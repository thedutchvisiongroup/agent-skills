#!/usr/bin/env python3
"""scan_secrets.py — deterministic secrets scanner for security-review.

Language-agnostic working-tree scan with three detectors:
  1. Provider formats      (AWS, Stripe, GitHub, Slack, Google, OpenAI, ...)
  2. Private key material  (-----BEGIN ... PRIVATE KEY-----)
  3. Keyword + high-entropy assignment (password/secret/token/api_key ... = "...")

Stdlib only. Read-only: scans files, never modifies anything.

Usage:
    python3 scan_secrets.py [PATH] [--allowlist FILE] [--json]

Exit codes: 0 = no candidates found, 1 = candidates found, 2 = usage error.
Findings are printed with REDACTED values — never full secrets.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    "vendor", "dist", "build", ".next", ".nuxt", "target", ".idea", ".vscode",
    ".terraform", "coverage", ".cache",
}

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svgz", ".pdf",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".jar", ".war",
    ".so", ".dll", ".dylib", ".exe", ".bin", ".class", ".pyc", ".o",
    ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4", ".mov",
    ".min.js", ".min.css", ".map",
}

MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MiB — skip large files (generated/data)

# Provider formats: (name, regex, confidence)
PROVIDER_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "high"),
    ("AWS secret key (context-dependent)", re.compile(r"(?i)aws.{0,20}secret.{0,10}['\"=:\s]+[A-Za-z0-9/+=]{40}\b"), "medium"),
    ("Stripe secret key", re.compile(r"\b[sr]k_(live|test)_[0-9A-Za-z]{16,}\b"), "high"),
    ("GitHub token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{22,})\b"), "high"),
    ("GitLab token", re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}\b"), "high"),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"), "high"),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"), "high"),
    ("OpenAI-style API key", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{20,}\b"), "high"),
    ("SendGrid API key", re.compile(r"\bSG\.[A-Za-z0-9_\-]{16,}\.[A-Za-z0-9_\-]{16,}\b"), "high"),
    ("Twilio API key", re.compile(r"\bSK[0-9a-f]{32}\b"), "medium"),
    ("npm token", re.compile(r"\bnpm_[A-Za-z0-9]{30,}\b"), "high"),
    ("PyPI token", re.compile(r"\bpypi-[A-Za-z0-9_\-]{30,}\b"), "high"),
    ("JWT-shaped string", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}\b"), "medium"),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY(?: BLOCK)?-----"), "high"),
    ("Credentials in URL", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@[^\s'\"]+", re.IGNORECASE), "high"),
    ("Generic bearer/auth header literal", re.compile(r"(?i)(authorization|x-api-key)\s*[:=]\s*['\"]?(bearer\s+)?[A-Za-z0-9._\-]{20,}['\"]?"), "medium"),
]

# Keyword + entropy detector
KEYWORD_RE = re.compile(
    r"""(?ix)
    \b(pass(?:word)?|passwd|pwd|secret|secret_?key|api_?key|apikey|api_?secret|
       access_?key|access_?secret|app_?secret|consumer_?secret|jwt_?secret|
       session_?secret|token|auth_?token|access_?token|refresh_?token|
       id_?token|client_?secret|private_?key|signing_?key|encryption_?key|
       master_?key|db_?pass(?:word)?|database_?url|connection_?string|
       smtp_?pass(?:word)?)\b
    \s*[:=]\s*
    ['"]([^'"\s]{12,})['"]
    """
)

# Placeholders that are NOT secrets. Two tiers:
# - HINTS: substring match for structural placeholders ("your-...", "xxx...")
# - EXACT: whole-value match for literal placeholder values ("password", "admin")
# NOTE: never put "admin"/"password"/"secret" in HINTS — a real credential
# containing such a substring (e.g. a URL with user "admin") would be
# silently dropped. Recall beats precision here: the reviewer verifies.
PLACEHOLDER_HINTS = (
    "changeme", "change-me", "your-", "your_", "xxx", "example", "sample",
    "dummy", "placeholder", "todo", "fixme", "fake", "notasecret",
    "not-a-secret", "insert-", "replace", "redacted", "localhost",
    "127.0.0.1",
)

PLACEHOLDER_EXACT = {
    "password", "passw0rd", "secret", "admin", "changeme", "change-me",
    "test", "none", "null", "undefined", "12345678", "00000000",
}

ENTROPY_THRESHOLD = 4.5
ENTROPY_MIN_LENGTH = 20


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    freq: dict[str, int] = {}
    for ch in value:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def redact(value: str) -> str:
    """Never print a full secret. First 4 + last 2 at most."""
    value = value.strip()
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}…{value[-2:]} (len={len(value)})"


def looks_like_placeholder(value: str) -> bool:
    low = value.lower().strip()
    if low in PLACEHOLDER_EXACT:
        return True
    return any(hint in low for hint in PLACEHOLDER_HINTS)


def load_allowlist(path: str | None) -> list[str]:
    if not path:
        default = os.path.join(os.getcwd(), ".security-review-allowlist")
        path = default if os.path.isfile(default) else None
    if not path:
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh
                    if line.strip() and not line.startswith("#")]
    except OSError:
        return []


def is_allowed(text: str, allowlist: list[str]) -> bool:
    return any(entry and entry in text for entry in allowlist)


def iter_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for name in filenames:
            path = os.path.join(dirpath, name)
            lower = name.lower()
            if any(lower.endswith(ext) for ext in SKIP_EXTENSIONS):
                continue
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def read_lines(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def scan_file(path: str, allowlist: list[str]) -> list[dict]:
    findings: list[dict] = []
    for lineno, line in enumerate(read_lines(path), start=1):
        if not line.strip() or is_allowed(line, allowlist):
            continue

        # 1. Provider formats
        for name, pattern, confidence in PROVIDER_PATTERNS:
            for match in pattern.finditer(line):
                value = match.group(0)
                if looks_like_placeholder(value):
                    continue
                findings.append({
                    "file": path, "line": lineno, "type": name,
                    "confidence": confidence, "match": redact(value),
                })

        # 2. Keyword + entropy
        kw = KEYWORD_RE.search(line)
        if kw:
            value = kw.group(2)
            if (len(value) >= ENTROPY_MIN_LENGTH
                    and shannon_entropy(value) >= ENTROPY_THRESHOLD
                    and not looks_like_placeholder(value)):
                findings.append({
                    "file": path, "line": lineno,
                    "type": f"high-entropy assignment to '{kw.group(1)}'",
                    "confidence": "medium", "match": redact(value),
                })
    # de-duplicate (file, line, type)
    seen: set[tuple] = set()
    unique: list[dict] = []
    for f in findings:
        key = (f["file"], f["line"], f["type"])
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic secrets scanner (read-only).")
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan (default: .)")
    parser.add_argument("--allowlist", help="Allowlist file: lines are substrings to ignore")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"error: not a directory: {args.path}", file=sys.stderr)
        return 2

    allowlist = load_allowlist(args.allowlist)
    findings: list[dict] = []
    for path in iter_files(args.path):
        findings.extend(scan_file(path, allowlist))

    findings.sort(key=lambda f: (f["file"], f["line"]))

    if args.json:
        print(json.dumps({"scanned": os.path.abspath(args.path),
                          "count": len(findings),
                          "findings": findings}, indent=2))
    else:
        print(f"scan_secrets.py — scanned {os.path.abspath(args.path)}")
        if not findings:
            print("No secret candidates found.")
            print("NOTE: this scans the working tree only. Scan git history "
                  "with gitleaks/trufflehog if available.")
            return 0
        print(f"{len(findings)} candidate(s) — VERIFY each manually "
              f"(false positives exist; values are redacted):\n")
        for f in findings:
            print(f"  {f['file']}:{f['line']}")
            print(f"    type:       {f['type']}")
            print(f"    confidence: {f['confidence']}")
            print(f"    match:      {f['match']}")
        print("\nREMINDER: a committed secret is a leaked secret. Report, "
              "recommend rotation. NEVER print or use the full value.")
        print("NOTE: working tree only — scan git history with gitleaks/"
              "trufflehog if available.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
