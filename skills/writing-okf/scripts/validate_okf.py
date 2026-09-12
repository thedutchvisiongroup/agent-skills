#!/usr/bin/env python3
"""Validate OKF documents against the Open Knowledge Format specification
plus house conventions.

Every finding is labelled:
    [SPEC]  — violates OKF conformance, v0.1 or v0.2 (always fix)
    [HOUSE] — violates a house convention (fix unless the user waives it)

Usage:
    python3 validate_okf.py <path-to-file>
    python3 validate_okf.py <directory>   # validates all .md files and every
                                          # directory recursively — one run
                                          # covers a deeply nested bundle
    python3 validate_okf.py --json <path> # machine-readable output for agents

Directory-level house checks (see ../references/house-rules.md):
    - index.md / log.md links stay at their OWN directory level: concept
      files (file.md) and direct subdirectories (subdir/) only
    - index.md lists every concept file and every direct subdirectory
    - every index entry points at an existing target (no dead entries)
    - a directory with concept files carries index.md (ERROR) and log.md (WARN)
    - reserved files must not start with a YAML-looking line (frontmatter
      without --- delimiters)

v0.2 provenance/trust/freshness/lifecycle checks (concept documents, spec §5):
    - legacy 'timestamp' field still present → WARN legacy-timestamp
    - 'generated' present without 'by' → ERROR generated-by (spec §5.2)
    - generated.at / verified[].at / stale_after not valid ISO 8601 →
      ERROR iso-datetime; valid but without explicit UTC offset → WARN
    - generated.by / verified[].by not matching the actor convention
      (opencode/<name>, human:<id>, process:<name>) → WARN actor-format
    - 'status' outside draft/stable/deprecated → WARN status-vocabulary
    - sources entry without 'resource' → ERROR sources-resource (spec §5.1)
    - body footnote [^id] without matching sources[].id → WARN footnote-source
    - index.md declaring okf_version other than "0.2" while the bundle uses
      v0.2 families → WARN version-mismatch (directory mode only)

Recommended concept frontmatter fields are title/description/tags — the v0.1
'timestamp' field is retired in v0.2 (legacy-timestamp warns on remnants).
Concepts with type: ADR use the ADR-domain status vocabulary (proposed,
accepted, rejected, superseded, deprecated) and are exempt from
status-vocabulary; every other v0.2 check still applies to ADRs.

Exit codes:
    0 = all validations passed (warnings allowed)
    1 = one or more validations failed
    2 = usage error
"""

import datetime
import glob
import json
import os
import re
import sys
import urllib.parse

try:
    import yaml
except ImportError:
    yaml = None

RESERVED_FILES = {"index.md", "log.md"}

# House rule: concept filenames use lowercase-kebab-case (not part of the OKF spec).
FILENAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$")

# Frontmatter delimiters must appear on their own line (spec §4). Matching the
# closing delimiter at line start prevents '---' inside quoted YAML values from
# terminating the block early.
FRONTMATTER_PATTERN = re.compile(
    r"\A---[ \t]*\r?\n(.*?)^---[ \t]*$", re.DOTALL | re.MULTILINE
)

# Inline markdown links and images: [text](target "title") / ![alt](target)
INLINE_LINK_PATTERN = re.compile(
    r"!?\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)"
)

# Reference-style link definitions: [label]: target
REF_DEF_PATTERN = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?([^>\s]+)>?", re.MULTILINE)

# Targets with a URI scheme (https:, mailto:, ...) are external, not bundle paths
EXTERNAL_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:")

# First body line that looks like 'key: value' without --- delimiters
PSEUDO_FRONTMATTER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*\s*:\s*\S")

# v0.2 actor convention for 'by' fields (house rule): opencode/<name>,
# human:<id>, process:<name>
ACTOR_PATTERN = re.compile(
    r"^(opencode/[A-Za-z0-9._-]+|human:[A-Za-z0-9@._-]+|process:[A-Za-z0-9._-]+)$"
)

# v0.2 lifecycle vocabulary for 'status'
STATUS_VOCABULARY = ("draft", "stable", "deprecated")

# v0.2 frontmatter families that mark a file as speaking v0.2
V02_FAMILY_KEYS = {"generated", "verified", "status", "stale_after", "sources"}

# ISO 8601 shapes for timestamp-family values (generated.at, verified[].at,
# stale_after): full datetime with explicit UTC offset (hour-only offsets
# like +02 count), datetime without offset, or a bare date (the bare/
# offset-less shapes only warn — house).
ISO_DATETIME_UTC_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(?:[Zz]|[+-]\d{2}(?::?\d{2})?)$"
)
ISO_DATETIME_NAIVE_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?$"
)
ISO_DATE_ONLY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Footnote uses in body text ([^id], but not [^id]: definitions)
FOOTNOTE_USE_PATTERN = re.compile(r"\[\^([^\]\s]+)\](?!\s*:)")


class ValidationResult:
    def __init__(self, path, kind="file"):
        self.path = path
        self.kind = kind  # "file" or "directory"
        self.findings = []  # list of dicts: level, label, message, check, line

    def _add(self, level, msg, label, check, line):
        self.findings.append(
            {
                "level": level,
                "label": label,
                "message": msg,
                "check": check,
                "line": line,
            }
        )

    def error(self, msg, label="SPEC", check=None, line=None):
        self._add("ERROR", msg, label, check, line)

    def warn(self, msg, label="SPEC", check=None, line=None):
        self._add("WARN", msg, label, check, line)

    @property
    def errors(self):
        return [f for f in self.findings if f["level"] == "ERROR"]

    @property
    def warnings(self):
        return [f for f in self.findings if f["level"] == "WARN"]

    @property
    def passed(self):
        return len(self.errors) == 0

    def to_dict(self):
        return {
            "kind": self.kind,
            "path": self.path,
            "passed": self.passed,
            "findings": self.findings,
        }


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content.

    Returns (yaml_str, body), or (None, content) when no valid delimited
    block is present. The closing '---' must be on its own line.
    """
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return None, content
    yaml_str = match.group(1).strip()
    body = content[match.end():].strip()
    return yaml_str, body


def is_reserved_file(filepath):
    """Check if the file is a reserved OKF file (index.md or log.md)."""
    filename = os.path.basename(filepath)
    return filename in RESERVED_FILES


def reserved_frontmatter_keys(yaml_str):
    """Return the set of top-level frontmatter keys, or None if undetermined."""
    if yaml is not None:
        try:
            fm = yaml.safe_load(yaml_str)
        except (yaml.YAMLError, ValueError):
            # PyYAML raises a raw ValueError for invalid unquoted date
            # literals — treat like any other YAML error (undetermined).
            return None
        return set(fm.keys()) if isinstance(fm, dict) else None
    # Fallback without PyYAML: collect top-level 'key:' names.
    keys = set()
    for line in yaml_str.splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", line)
        if match:
            keys.add(match.group(1))
    return keys or None


def validate_frontmatter(yaml_str, result):
    """Validate OKF frontmatter requirements."""
    if yaml_str is None:
        result.error(
            "Missing or unterminated YAML frontmatter. File must start with a "
            "'---' block closed by '---' on its own line.",
            check="frontmatter",
        )
        return None

    if yaml is None:
        result.warn(
            "PyYAML not installed; using basic string checks. Install with: pip install pyyaml",
            label="HOUSE",
            check="frontmatter",
        )
        # Manual string-based checks
        if not re.search(r"^type:", yaml_str, re.MULTILINE):
            result.error(
                "Frontmatter missing required 'type' field.", check="frontmatter"
            )
        # 'timestamp' retired in v0.2 — legacy-timestamp nudges migration.
        for field in ("title", "description", "tags"):
            if not re.search(rf"^{field}:", yaml_str, re.MULTILINE):
                result.warn(
                    f"Frontmatter missing recommended '{field}' field.",
                    check="frontmatter",
                )
        return None

    try:
        fm = yaml.safe_load(yaml_str)
    except (yaml.YAMLError, ValueError) as e:
        # PyYAML raises a raw ValueError (not YAMLError) for invalid unquoted
        # date literals like 2026-13-45 — surface it as a normal finding.
        result.error(f"Invalid YAML in frontmatter: {e}", check="frontmatter")
        return None

    if not isinstance(fm, dict):
        result.error(
            "Frontmatter must be a YAML mapping (key-value pairs).", check="frontmatter"
        )
        return None

    # Required: type field
    if "type" not in fm:
        result.error(
            "Frontmatter missing required 'type' field.", check="frontmatter"
        )
    elif not fm["type"] or not str(fm["type"]).strip():
        result.error(
            "Frontmatter 'type' field must not be empty.", check="frontmatter"
        )

    # Recommended fields (spec §4.1) — 'timestamp' retired in v0.2;
    # the legacy-timestamp check nudges migration instead.
    for field in ("title", "description", "tags"):
        if field not in fm:
            result.warn(
                f"Frontmatter missing recommended '{field}' field.",
                check="frontmatter",
            )

    return fm


def validate_filename(filepath, result):
    """Validate file naming convention (house rule, not part of the OKF spec)."""
    filename = os.path.basename(filepath)

    # Reserved files are exempt from naming convention
    if filename in RESERVED_FILES:
        return

    if not FILENAME_PATTERN.match(filename):
        result.error(
            f"Filename '{filename}' does not match lowercase-kebab-case.md convention. "
            f"Example: my-concept.md",
            label="HOUSE",
            check="filename",
        )


def validate_body(body, result, is_reserved):
    """Validate the markdown body."""
    if not body:
        result.error("Document body is empty.", label="HOUSE", check="body")
        return

    # For index.md: check for section headings (spec §8 structure)
    if is_reserved and os.path.basename(result.path) == "index.md":
        if not re.search(r"^#\s+.+", body, re.MULTILINE):
            result.warn(
                "index.md has no section headings. Consider organizing content under headings.",
                check="index-structure",
            )
        return

    # For log.md: date headings are required by spec §9 ("MUST use ISO 8601")
    if is_reserved and os.path.basename(result.path) == "log.md":
        if not re.search(r"^##\s+\d{4}-\d{2}-\d{2}", body, re.MULTILINE):
            result.error(
                "log.md has no date entries. Expected headings like '## 2026-07-20' (spec §9).",
                check="log-structure",
            )
        return

    # For concept documents: H1 heading is a house convention
    h1_match = re.search(r"^#\s+.+", body, re.MULTILINE)
    if not h1_match:
        result.warn(
            "No H1 title heading found. Consider adding a top-level heading.",
            label="HOUSE",
            check="body",
        )


def validate_encoding(filepath, result):
    """Validate UTF-8 encoding."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
    except UnicodeDecodeError:
        result.error("File is not valid UTF-8 encoded.", check="encoding")


def iter_links(content):
    """Yield (raw_target, line_number) for every markdown link in content.

    Covers inline links, images, and reference-style link definitions —
    including links inside tables (ADR-style tabular indexes).
    """
    seen = []
    for pattern in (INLINE_LINK_PATTERN, REF_DEF_PATTERN):
        for m in pattern.finditer(content):
            line = content.count("\n", 0, m.start()) + 1
            seen.append((m.group(1), line))
    return seen


def classify_link(raw):
    """Classify a raw markdown link target for the same-level rule.

    Returns (kind, value):
        ("skip", None)          external URL, mailto, or pure anchor — exempt
        ("absolute", target)    bundle-absolute path, forbidden in index/log
        ("escape", target)      climbs out of the directory (..), forbidden
        ("nested", target)      reaches into a subdirectory, forbidden
        ("same-level", segment) a single same-level segment (file or directory)
    """
    target = raw.strip()
    if not target:
        return "skip", None
    if EXTERNAL_PATTERN.match(target):
        return "skip", None
    target = target.split("#", 1)[0].strip()
    if not target:
        return "skip", None
    target = urllib.parse.unquote(target)
    if target.startswith("/"):
        return "absolute", target
    parts = [p for p in target.split("/") if p and p != "."]
    if any(p == ".." for p in parts):
        return "escape", target
    if not parts:
        return "skip", None
    if len(parts) > 1:
        return "nested", target
    return "same-level", parts[0]


def validate_reserved_links(filepath, content, result):
    """House rule: every link in an index.md/log.md stays at its own
    directory level and points at an existing target."""
    filename = os.path.basename(filepath)
    is_index = filename == "index.md"
    check = "index-scope" if is_index else "log-scope"
    dirpath = os.path.dirname(filepath) or "."

    for raw, line in iter_links(content):
        kind, value = classify_link(raw)
        if kind == "skip":
            continue
        if kind == "absolute":
            result.error(
                f"line {line}: bundle-absolute link '{raw}' — {filename} must use "
                f"same-level relative links ('file.md' or 'subdir/'). "
                f"Bundle-absolute links belong in concept documents, not in index/log files.",
                label="HOUSE",
                check=check,
                line=line,
            )
        elif kind == "escape":
            result.error(
                f"line {line}: link '{raw}' climbs out of the directory — "
                f"{filename} may only link targets in its own directory.",
                label="HOUSE",
                check=check,
                line=line,
            )
        elif kind == "nested":
            first_segment = value.split("/")[0]
            result.error(
                f"line {line}: nested link '{raw}' — {filename} may only link "
                f"same-level files and direct subdirectories. List the subdirectory "
                f"itself ('{first_segment}/') and put the entry in that "
                f"subdirectory's own index.md/log.md.",
                label="HOUSE",
                check=check,
                line=line,
            )
        else:
            # Same-level target: must exist in this directory. A dead index
            # entry is always wrong; a dead log entry may be legitimate
            # history (renamed or removed files), so it only warns.
            if not os.path.exists(os.path.join(dirpath, value)):
                if is_index:
                    result.error(
                        f"line {line}: dead entry — target '{raw}' does not exist "
                        f"in this directory.",
                        label="HOUSE",
                        check="index-scope",
                        line=line,
                    )
                else:
                    result.warn(
                        f"line {line}: target '{raw}' does not exist in this "
                        f"directory (acceptable in log.md when it refers to "
                        f"renamed or removed history).",
                        label="HOUSE",
                        check="log-scope",
                        line=line,
                    )


def validate_index_completeness(filepath, content, result):
    """House rule: index.md lists every concept file and every direct
    subdirectory of its own directory (bidirectional completeness)."""
    dirpath = os.path.dirname(filepath) or "."

    listed = set()
    for raw, _line in iter_links(content):
        kind, value = classify_link(raw)
        if kind == "same-level":
            listed.add(value)

    try:
        entries = sorted(os.listdir(dirpath))
    except OSError as e:
        result.error(f"Cannot read directory '{dirpath}': {e}", check="index-completeness")
        return

    concept_files = [
        e
        for e in entries
        if e.endswith(".md") and e not in RESERVED_FILES and not e.startswith(".")
    ]
    subdirs = [
        e
        for e in entries
        if os.path.isdir(os.path.join(dirpath, e)) and not e.startswith(".")
    ]

    for f in concept_files:
        if f not in listed:
            result.error(
                f"concept file '{f}' is not listed in index.md — every concept "
                f"file in the directory must have an entry.",
                label="HOUSE",
                check="index-completeness",
            )
    for d in subdirs:
        if d not in listed:
            result.error(
                f"subdirectory '{d}/' is not listed in index.md — every direct "
                f"subdirectory must have an entry (link it as '{d}/').",
                label="HOUSE",
                check="index-completeness",
            )


def validate_pseudo_frontmatter(body, result, filename):
    """House rule: a reserved file whose first line looks like 'key: value'
    almost certainly lost its --- delimiters (caught a real bug once)."""
    if not body:
        return
    first_line = body.splitlines()[0].strip()
    if PSEUDO_FRONTMATTER_PATTERN.match(first_line):
        result.warn(
            f"first line '{first_line}' looks like frontmatter without '---' "
            f"delimiters — {filename} may only carry frontmatter as a bundle-root "
            f"index.md with a single 'okf_version' key, properly delimited.",
            label="HOUSE",
            check="pseudo-frontmatter",
        )


def frontmatter_key_line(content, key):
    """Return the 1-based file line of a top-level frontmatter key, or None.

    Only column-0 occurrences inside the delimited block match, so nested
    keys never shadow the top-level one.
    """
    fm_match = FRONTMATTER_PATTERN.match(content)
    if not fm_match:
        return None
    match = re.search(
        rf"^{re.escape(key)}\s*:", content[: fm_match.end()], re.MULTILINE
    )
    if not match:
        return None
    return content.count("\n", 0, match.start()) + 1


def iso_datetime_level(value):
    """Classify a timestamp-family value for the iso-datetime checks.

    Returns "ok" (datetime with explicit UTC offset), "naive" (valid ISO 8601
    but a bare date or missing UTC offset), or "invalid" (not ISO 8601).
    PyYAML parses unquoted timestamps into datetime objects, so both typed
    values and strings are classified.
    """
    if isinstance(value, datetime.datetime):
        return "ok" if value.tzinfo is not None else "naive"
    if isinstance(value, datetime.date):
        return "naive"
    if not isinstance(value, str):
        return "invalid"
    text = value.strip()
    if ISO_DATETIME_UTC_PATTERN.match(text):
        normalized = re.sub(r"[Zz]$", "+00:00", text)
        normalized = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", normalized)
        # Hour-only offsets (+02) normalize to +02:00, matching how PyYAML
        # treats the unquoted form (quoted/unquoted must get one verdict).
        normalized = re.sub(r"([+-]\d{2})$", r"\1:00", normalized)
        try:
            datetime.datetime.fromisoformat(normalized.replace("t", "T", 1))
        except ValueError:
            return "invalid"
        return "ok"
    if ISO_DATETIME_NAIVE_PATTERN.match(text) or ISO_DATE_ONLY_PATTERN.match(text):
        try:
            datetime.datetime.fromisoformat(text.replace("t", "T", 1))
        except ValueError:
            return "invalid"
        return "naive"
    return "invalid"


def validate_iso_field(field, value, result, line=None):
    """iso-datetime: timestamp-family values must be valid ISO 8601; a valid
    datetime without explicit UTC offset only warns (house convention)."""
    level = iso_datetime_level(value)
    if level == "ok":
        return
    if level == "invalid":
        result.error(
            f"'{field}' value '{value}' is not a valid ISO 8601 datetime.",
            check="iso-datetime",
            line=line,
        )
    else:
        result.warn(
            f"'{field}' value '{value}' lacks an explicit UTC offset — use a "
            f"full ISO 8601 datetime like '2026-12-31T23:59:59+00:00' (or '...Z').",
            label="HOUSE",
            check="iso-datetime",
            line=line,
        )


def validate_actor_field(field, value, result, line=None):
    """actor-format (house): 'by' values follow the actor convention."""
    if isinstance(value, str) and ACTOR_PATTERN.match(value):
        return
    result.warn(
        f"'{field}' value '{value}' does not match the actor convention "
        f"'opencode/<name>', 'human:<id>', or 'process:<name>'.",
        label="HOUSE",
        check="actor-format",
        line=line,
    )


def validate_footnote_sources(fm, content, result):
    """House rule: footnote references used in the body must resolve to a
    sources[] entry by id. No sources at all → legacy v0.1 style, skip."""
    sources = fm.get("sources")
    if not isinstance(sources, list):
        return
    fm_match = FRONTMATTER_PATTERN.match(content)
    body_start = fm_match.end() if fm_match else 0
    used = {}
    for match in FOOTNOTE_USE_PATTERN.finditer(content):
        if match.start() < body_start:
            continue
        footnote_id = match.group(1)
        used.setdefault(footnote_id, content.count("\n", 0, match.start()) + 1)
    if not used:
        return
    source_ids = {
        entry.get("id")
        for entry in sources
        if isinstance(entry, dict) and entry.get("id")
    }
    for footnote_id, line in sorted(used.items(), key=lambda item: item[1]):
        if footnote_id not in source_ids:
            result.warn(
                f"line {line}: footnote '[^{footnote_id}]' has no matching "
                f"sources[] entry with id '{footnote_id}'.",
                label="HOUSE",
                check="footnote-source",
                line=line,
            )


def validate_version_mismatch(filepath, yaml_str, content, result):
    """House rule (directory mode only): when any .md file in the subtree
    below an index.md uses v0.2 frontmatter families, that index must declare
    okf_version "0.2"."""
    if yaml is None:
        return
    try:
        index_fm = yaml.safe_load(yaml_str)
    except (yaml.YAMLError, ValueError):
        # PyYAML raises a raw ValueError for invalid unquoted date literals.
        return
    if not isinstance(index_fm, dict) or "okf_version" not in index_fm:
        return
    declared = str(index_fm["okf_version"]).strip().strip("\"'")
    if declared == "0.2":
        return

    dirpath = os.path.dirname(filepath) or "."
    family_files = []
    for md_path in sorted(
        glob.glob(os.path.join(dirpath, "**", "*.md"), recursive=True)
    ):
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                other_content = f.read()
        except (OSError, ValueError):
            # UnicodeDecodeError (⊂ ValueError) on non-UTF-8 files: skip here —
            # validate_okf_file already reports them as io/encoding ERRORs.
            continue
        other_yaml, _body = parse_frontmatter(other_content)
        if other_yaml is None:
            continue
        keys = reserved_frontmatter_keys(other_yaml)
        if not keys:
            continue
        families = sorted(keys & V02_FAMILY_KEYS)
        if families:
            relpath = os.path.relpath(md_path, dirpath)
            family_files.append((relpath, families))

    if not family_files:
        return

    all_families = sorted(
        {family for _path, families in family_files for family in families}
    )
    listed = ", ".join(
        f"{path} ({', '.join(families)})" for path, families in family_files
    )
    result.warn(
        f"index declares okf_version '{declared}' but the bundle uses v0.2 "
        f"frontmatter families ({', '.join(all_families)}) in {listed} — "
        f"declare okf_version: \"0.2\" or keep the files on v0.1.",
        label="HOUSE",
        check="version-mismatch",
        line=frontmatter_key_line(content, "okf_version"),
    )


def validate_v02_families(fm, content, result):
    """Validate the v0.2 frontmatter families (provenance, trust, freshness,
    lifecycle — spec §5) plus body footnote linkage in a concept document."""
    # Legacy v0.1 timestamp surviving into a v0.2 world
    if "timestamp" in fm:
        result.warn(
            "frontmatter carries legacy 'timestamp' — v0.2 provenance uses "
            "'generated' (with 'by' and 'at'); migrate the value and remove "
            "'timestamp'.",
            label="HOUSE",
            check="legacy-timestamp",
            line=frontmatter_key_line(content, "timestamp"),
        )

    # Provenance: generated (spec §5.2)
    generated = fm.get("generated")
    generated_line = frontmatter_key_line(content, "generated")
    if "generated" in fm and not (
        isinstance(generated, dict) and generated.get("by")
    ):
        result.error(
            "'generated' present without 'by' — provenance must record the "
            "actor that produced the document (spec §5.2).",
            check="generated-by",
            line=generated_line,
        )
    if isinstance(generated, dict):
        if "at" in generated:
            validate_iso_field(
                "generated.at", generated["at"], result, line=generated_line
            )
        if generated.get("by"):
            validate_actor_field(
                "generated.by", generated["by"], result, line=generated_line
            )

    # Trust: verified (spec §5.2) — a bare mapping counts as one entry
    verified = fm.get("verified")
    verified_line = frontmatter_key_line(content, "verified")
    if isinstance(verified, dict):
        verified_entries = [("verified", verified)]
    elif isinstance(verified, list):
        verified_entries = [
            (f"verified[{index}]", entry) for index, entry in enumerate(verified)
        ]
    else:
        verified_entries = []
    for name, entry in verified_entries:
        if not isinstance(entry, dict):
            continue
        if "at" in entry:
            validate_iso_field(f"{name}.at", entry["at"], result, line=verified_line)
        if entry.get("by"):
            validate_actor_field(f"{name}.by", entry["by"], result, line=verified_line)

    # Freshness: stale_after
    if "stale_after" in fm:
        validate_iso_field(
            "stale_after",
            fm["stale_after"],
            result,
            line=frontmatter_key_line(content, "stale_after"),
        )

    # Lifecycle: status vocabulary. House exception: type: ADR concepts carry
    # the ADR-domain status vocabulary (proposed/accepted/rejected/superseded/
    # deprecated) and are exempt; all other v0.2 checks still apply to ADRs.
    if (
        "status" in fm
        and fm.get("type") != "ADR"
        and fm["status"] not in STATUS_VOCABULARY
    ):
        result.warn(
            f"'status' value '{fm['status']}' is not in the v0.2 lifecycle "
            f"vocabulary (draft, stable, deprecated).",
            label="HOUSE",
            check="status-vocabulary",
            line=frontmatter_key_line(content, "status"),
        )

    # Provenance links: sources (spec §5.1)
    sources = fm.get("sources")
    if isinstance(sources, list):
        sources_line = frontmatter_key_line(content, "sources")
        for index, entry in enumerate(sources):
            if not isinstance(entry, dict) or not entry.get("resource"):
                result.error(
                    f"sources[{index}] entry has no 'resource' — every source "
                    f"must point at a resource (spec §5.1).",
                    check="sources-resource",
                    line=sources_line,
                )

    # Footnote ↔ sources linkage
    validate_footnote_sources(fm, content, result)


def validate_okf_file(filepath, bundle_mode=False):
    """Run all validations on a single OKF file.

    bundle_mode enables the directory-mode-only check (version-mismatch on
    index.md); single-file validation keeps it off.
    """
    result = ValidationResult(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        result.error(f"File not found: {filepath}", check="io")
        return result
    except Exception as e:
        result.error(f"Error reading file: {e}", check="io")
        return result

    if not content.strip():
        result.error("File is empty.", check="io")
        return result

    # 1. Encoding
    validate_encoding(filepath, result)

    # 2. Filename convention (house rule)
    validate_filename(filepath, result)

    # 3. Check if reserved file
    reserved = is_reserved_file(filepath)

    # 4. Parse and validate frontmatter
    yaml_str, body = parse_frontmatter(content)

    if reserved:
        # Reserved files have no frontmatter — EXCEPT an okf_version key in a
        # bundle-root index.md (spec §12), the only legal index frontmatter.
        if yaml_str is not None:
            filename = os.path.basename(filepath)
            keys = reserved_frontmatter_keys(yaml_str)
            if not (filename == "index.md" and keys is not None and keys <= {"okf_version"}):
                result.warn(
                    "Reserved file has frontmatter. Only an 'okf_version' key in the "
                    "bundle-root index.md is permitted (spec §12).",
                    check="reserved-frontmatter",
                )
            elif bundle_mode:
                # Legal index frontmatter: check the declared okf_version
                # against v0.2 family usage in the subtree (directory mode only).
                validate_version_mismatch(filepath, yaml_str, content, result)
        else:
            # No delimited frontmatter: flag a YAML-looking first line —
            # likely frontmatter that lost its --- delimiters.
            validate_pseudo_frontmatter(body, result, os.path.basename(filepath))
    else:
        # Concept documents must have frontmatter
        fm = validate_frontmatter(yaml_str, result)
        if fm is not None:
            validate_v02_families(fm, content, result)

    # 5. Validate body
    validate_body(body, result, reserved)

    # 6. Reserved-file link rules: same-level scope, dead entries,
    #    and (for index.md) bidirectional completeness.
    if reserved:
        validate_reserved_links(filepath, content, result)
        if os.path.basename(filepath) == "index.md":
            validate_index_completeness(filepath, content, result)

    return result


def validate_directory(dirpath):
    """Run directory-level house checks: a directory holding concept files
    must carry its own index.md (ERROR) and log.md (WARN)."""
    result = ValidationResult(dirpath, kind="directory")

    try:
        entries = [
            e for e in os.listdir(dirpath) if e.endswith(".md") and not e.startswith(".")
        ]
    except OSError as e:
        result.error(f"Cannot read directory '{dirpath}': {e}", check="scaffolding")
        return result

    concept_files = [e for e in entries if e not in RESERVED_FILES]
    if not concept_files:
        return result

    if "index.md" not in entries:
        result.error(
            f"directory has {len(concept_files)} concept file(s) "
            f"({', '.join(sorted(concept_files))}) but no index.md — scaffolding "
            f"is standard: every directory holding concepts carries its own index.md.",
            label="HOUSE",
            check="scaffolding",
        )
    if "log.md" not in entries:
        result.warn(
            f"directory has {len(concept_files)} concept file(s) but no log.md — "
            f"scaffolding is standard: every directory holding concepts carries "
            f"its own log.md.",
            label="HOUSE",
            check="scaffolding",
        )

    return result


def print_result(result):
    """Print validation result for a single file or directory."""
    status = "PASS" if result.passed else "FAIL"
    print(f"\n[{status}] {'directory: ' if result.kind == 'directory' else ''}{result.path}")

    for f in result.findings:
        print(f"  {f['level']} [{f['label']}]{' [' + f['check'] + ']' if f['check'] else ''}: {f['message']}")


def print_summary(file_results, dir_results):
    total_files = len(file_results)
    total_dirs = len(dir_results)
    errors = sum(len(r.errors) for r in file_results + dir_results)
    warnings = sum(len(r.warnings) for r in file_results + dir_results)
    failed = sum(1 for r in file_results + dir_results if not r.passed)

    print(f"\n{'='*50}")
    print(
        f"Summary: {total_files} file(s), {total_dirs} directories checked; "
        f"{failed} failed; {errors} error(s), {warnings} warning(s)"
    )


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]

    if not args:
        print(__doc__)
        sys.exit(2)

    target = args[0]

    if os.path.isfile(target):
        file_results = [validate_okf_file(target)]
        dir_results = []
    elif os.path.isdir(target):
        # One recursive run covers the whole (deeply nested) bundle: every
        # .md file is validated, and every directory holding .md content
        # gets the directory-level scaffolding checks.
        files = sorted(glob.glob(os.path.join(target, "**", "*.md"), recursive=True))
        if not files:
            print(f"No .md files found in {target}")
            sys.exit(2)
        file_results = [validate_okf_file(f, bundle_mode=True) for f in files]
        dirpaths = sorted({os.path.dirname(f) for f in files})
        dir_results = [validate_directory(d) for d in dirpaths]
    else:
        print(f"Error: {target} is not a file or directory")
        sys.exit(2)

    if as_json:
        payload = {
            "root": target,
            "files": [r.to_dict() for r in file_results],
            "directories": [r.to_dict() for r in dir_results],
            "summary": {
                "files_checked": len(file_results),
                "directories_checked": len(dir_results),
                "errors": sum(len(r.errors) for r in file_results + dir_results),
                "warnings": sum(len(r.warnings) for r in file_results + dir_results),
                "passed": all(r.passed for r in file_results + dir_results),
            },
        }
        print(json.dumps(payload, indent=2))
    else:
        for result in file_results + dir_results:
            print_result(result)
        print_summary(file_results, dir_results)

    failed = sum(1 for r in file_results + dir_results if not r.passed)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
