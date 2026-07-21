#!/usr/bin/env python3
"""extract_dependencies.py — normalize dependency manifests/lockfiles.

Detects common manifests and lockfiles across ecosystems and emits a uniform
package list: ecosystem / name / version. The security-review skill feeds this
list into online advisory lookups (OSV / NVD / GitHub Advisory) — known-CVE
status exists only online, never guess it.

Lockfile versions are preferred over manifest ranges (locked = what actually
ships). Manifest-only entries keep their declared range and are marked
"declared" so the reviewer knows the resolved version may differ.

Stdlib only (tomllib used when available). Read-only.

Usage:
    python3 extract_dependencies.py [PATH] [--json]

Exit codes: 0 = ok (even when zero manifests found), 2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    tomllib = None

# OSV-aligned ecosystem names
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "vendor",
    "dist", "build", "target", ".terraform", ".next", ".gradle",
}

Deps = list[dict]  # {"ecosystem", "name", "version", "source", "kind"}


# ---------------------------------------------------------------------------
# Parsers — one per file type. Each takes (path) and returns Deps.
# ---------------------------------------------------------------------------

def _load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def parse_package_json(path: str) -> Deps:
    data = _load_json(path)
    if not isinstance(data, dict):
        return []
    deps: Deps = []
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        for name, rng in (data.get(section) or {}).items():
            if isinstance(rng, str):
                deps.append({"ecosystem": "npm", "name": name,
                             "version": rng, "source": path, "kind": "declared"})
    return deps


def parse_package_lock(path: str) -> Deps:
    data = _load_json(path)
    if not isinstance(data, dict):
        return []
    deps: Deps = []
    packages = data.get("packages")
    if isinstance(packages, dict):  # lockfileVersion 2/3
        for key, meta in packages.items():
            if not key or not isinstance(meta, dict):
                continue
            name = key.split("node_modules/")[-1]
            version = meta.get("version")
            if name and version:
                deps.append({"ecosystem": "npm", "name": name,
                             "version": version, "source": path, "kind": "locked"})
    else:  # lockfileVersion 1
        for name, meta in (data.get("dependencies") or {}).items():
            if isinstance(meta, dict) and meta.get("version"):
                deps.append({"ecosystem": "npm", "name": name,
                             "version": meta["version"], "source": path,
                             "kind": "locked"})
    return deps


YARN_LOCK_RE = re.compile(r'^"?(@?[^@\s"][^@\s"]*)@[^"]*"?:\s*$')
YARN_VER_RE = re.compile(r'^\s+version\s+"?([^"\s]+)"?')


def parse_yarn_lock(path: str) -> Deps:
    deps: Deps = []
    current: str | None = None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = YARN_LOCK_RE.match(line)
                if m and not line.startswith(" "):
                    current = m.group(1)
                    continue
                v = YARN_VER_RE.match(line)
                if v and current:
                    deps.append({"ecosystem": "npm", "name": current,
                                 "version": v.group(1), "source": path,
                                 "kind": "locked"})
                    current = None
    except OSError:
        pass
    return deps


PNPM_RE = re.compile(r"^\s{2,}/(@?[^/\s]+(?:/[^/\s]+)?)@([0-9][^\s:'(]*)")


def parse_pnpm_lock(path: str) -> Deps:
    deps: Deps = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = PNPM_RE.match(line)
                if m:
                    deps.append({"ecosystem": "npm", "name": m.group(1),
                                 "version": m.group(2), "source": path,
                                 "kind": "locked"})
    except OSError:
        pass
    return deps


REQ_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+(?:\[[^\]]*\])?)\s*==\s*([^\s;#]+)")
REQ_RANGE_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+(?:\[[^\]]*\])?)\s*(~=|>=|<=|>|<)\s*([^\s;#]+)")


def parse_requirements_txt(path: str) -> Deps:
    deps: Deps = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith(("#", "-", "git+", "http")):
                    continue
                m = REQ_RE.match(line)
                if m:
                    deps.append({"ecosystem": "PyPI",
                                 "name": re.sub(r"\[.*\]", "", m.group(1)),
                                 "version": m.group(2), "source": path,
                                 "kind": "locked"})
                    continue
                m = REQ_RANGE_RE.match(line)
                if m:
                    deps.append({"ecosystem": "PyPI",
                                 "name": re.sub(r"\[.*\]", "", m.group(1)),
                                 "version": m.group(2) + m.group(3),
                                 "source": path, "kind": "declared"})
    except OSError:
        pass
    return deps


def parse_pyproject_toml(path: str) -> Deps:
    if tomllib is None:
        return []
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return []
    deps: Deps = []
    pep508 = re.compile(r"^\s*([A-Za-z0-9_.\-]+)(?:\[.*\])?\s*(.*)$")
    for raw in (data.get("project", {}).get("dependencies") or []):
        m = pep508.match(str(raw))
        if m:
            deps.append({"ecosystem": "PyPI", "name": m.group(1),
                         "version": (m.group(2) or "unspecified").strip(),
                         "source": path, "kind": "declared"})
    poetry = data.get("tool", {}).get("poetry", {})
    for section in ("dependencies", "dev-dependencies"):
        for name, spec in (poetry.get(section) or {}).items():
            if name.lower() == "python":
                continue
            version = spec if isinstance(spec, str) else \
                (spec.get("version", "unspecified") if isinstance(spec, dict)
                 else "unspecified")
            deps.append({"ecosystem": "PyPI", "name": name,
                         "version": version, "source": path, "kind": "declared"})
    return deps


def parse_pipfile_lock(path: str) -> Deps:
    data = _load_json(path)
    if not isinstance(data, dict):
        return []
    deps: Deps = []
    for section in ("default", "develop"):
        for name, meta in (data.get(section) or {}).items():
            if isinstance(meta, dict) and meta.get("version"):
                deps.append({"ecosystem": "PyPI", "name": name,
                             "version": str(meta["version"]).lstrip("="),
                             "source": path, "kind": "locked"})
    return deps


def parse_go_mod(path: str) -> Deps:
    deps: Deps = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            in_block = False
            for line in fh:
                stripped = line.strip()
                if stripped.startswith("require ("):
                    in_block = True
                    continue
                if in_block and stripped == ")":
                    in_block = False
                    continue
                if stripped.startswith("require ") and not in_block:
                    stripped = stripped[len("require "):]
                if (in_block or line.startswith("require ")) and stripped:
                    parts = stripped.split()
                    if len(parts) >= 2 and re.match(r"^v\d", parts[1]):
                        deps.append({"ecosystem": "Go", "name": parts[0],
                                     "version": parts[1], "source": path,
                                     "kind": "locked"})
    except OSError:
        pass
    return deps


def parse_cargo_toml(path: str) -> Deps:
    if tomllib is None:
        return []
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return []
    deps: Deps = []
    for section in ("dependencies", "dev-dependencies", "build-dependencies"):
        for name, spec in (data.get(section) or {}).items():
            version = spec if isinstance(spec, str) else \
                (spec.get("version", "unspecified") if isinstance(spec, dict)
                 else "unspecified")
            deps.append({"ecosystem": "crates.io", "name": name,
                         "version": version, "source": path, "kind": "declared"})
    return deps


def parse_cargo_lock(path: str) -> Deps:
    if tomllib is None:
        return []
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return []
    return [{"ecosystem": "crates.io", "name": p.get("name", "?"),
             "version": p.get("version", "?"), "source": path, "kind": "locked"}
            for p in data.get("package", []) if isinstance(p, dict)]


def parse_composer_json(path: str) -> Deps:
    data = _load_json(path)
    if not isinstance(data, dict):
        return []
    deps: Deps = []
    for section in ("require", "require-dev"):
        for name, rng in (data.get(section) or {}).items():
            if "/" in str(name) and not str(name).startswith(("php", "ext-")):
                deps.append({"ecosystem": "Packagist", "name": name,
                             "version": str(rng), "source": path,
                             "kind": "declared"})
    return deps


def parse_composer_lock(path: str) -> Deps:
    data = _load_json(path)
    if not isinstance(data, dict):
        return []
    deps: Deps = []
    for section in ("packages", "packages-dev"):
        for pkg in (data.get(section) or []):
            if isinstance(pkg, dict) and pkg.get("name") and pkg.get("version"):
                deps.append({"ecosystem": "Packagist", "name": pkg["name"],
                             "version": pkg["version"], "source": path,
                             "kind": "locked"})
    return deps


GEMFILE_LOCK_SECTION = re.compile(r"^\s{4}([A-Za-z0-9_.\-]+)\s\(([^)]+)\)")


def parse_gemfile_lock(path: str) -> Deps:
    deps: Deps = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = GEMFILE_LOCK_SECTION.match(line)
                if m:
                    deps.append({"ecosystem": "RubyGems", "name": m.group(1),
                                 "version": m.group(2), "source": path,
                                 "kind": "locked"})
    except OSError:
        pass
    return deps


def parse_pom_xml(path: str) -> Deps:
    import xml.etree.ElementTree as ET  # stdlib, local import keeps top clean
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return []
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    deps: Deps = []
    for dep in root.iter(ns + "dependency"):
        g = dep.findtext(ns + "groupId")
        a = dep.findtext(ns + "artifactId")
        v = dep.findtext(ns + "version")
        if g and a:
            deps.append({"ecosystem": "Maven", "name": f"{g}:{a}",
                         "version": (v or "unspecified").strip(),
                         "source": path, "kind": "declared"})
    return deps


GRADLE_RE = re.compile(
    r"(?:implementation|api|compileOnly|runtimeOnly|testImplementation|classpath)"
    r"\s*\(?\s*['\"]([^:'\"]+):([^:'\"]+):([^'\"]+)['\"]")


def parse_gradle(path: str) -> Deps:
    deps: Deps = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = GRADLE_RE.search(line)
                if m:
                    deps.append({"ecosystem": "Maven",
                                 "name": f"{m.group(1)}:{m.group(2)}",
                                 "version": m.group(3), "source": path,
                                 "kind": "declared"})
    except OSError:
        pass
    return deps


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

FILE_PARSERS = {
    "package.json": parse_package_json,
    "package-lock.json": parse_package_lock,
    "yarn.lock": parse_yarn_lock,
    "pnpm-lock.yaml": parse_pnpm_lock,
    "pyproject.toml": parse_pyproject_toml,
    "Pipfile.lock": parse_pipfile_lock,
    "go.mod": parse_go_mod,
    "Cargo.toml": parse_cargo_toml,
    "Cargo.lock": parse_cargo_lock,
    "composer.json": parse_composer_json,
    "composer.lock": parse_composer_lock,
    "Gemfile.lock": parse_gemfile_lock,
    "pom.xml": parse_pom_xml,
    "build.gradle": parse_gradle,
    "build.gradle.kts": parse_gradle,
}


def discover(root: str) -> tuple[Deps, list[str]]:
    deps: Deps = []
    notes: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            parser = FILE_PARSERS.get(name)
            if parser:
                deps.extend(parser(path))
            elif name.startswith("requirements") and name.endswith(".txt"):
                deps.extend(parse_requirements_txt(path))
    # De-duplicate locked entries (same ecosystem+name+version)
    seen: set[tuple] = set()
    unique: Deps = []
    for d in deps:
        key = (d["ecosystem"], d["name"], d["version"], d["kind"])
        if key not in seen:
            seen.add(key)
            unique.append(d)
    if not unique:
        notes.append("No manifests/lockfiles found. If this project has "
                     "dependencies in another format, extract them manually "
                     "and check them against OSV — do not skip advisory lookup.")
    ecosystems = sorted({d["ecosystem"] for d in unique})
    locked = sum(1 for d in unique if d["kind"] == "locked")
    declared = len(unique) - locked
    notes.append(f"Ecosystems: {', '.join(ecosystems) or 'none'}")
    notes.append(f"Packages: {len(unique)} ({locked} locked, {declared} declared ranges)")
    if declared and not locked:
        notes.append("WARNING: no lockfile found — resolved versions may "
                     "differ from declared ranges. Note the reproducibility/"
                     "integrity gap in the report (see dependencies reference).")
    return unique, notes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize dependency manifests/lockfiles to a package list.")
    parser.add_argument("path", nargs="?", default=".", help="Project root (default: .)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"error: not a directory: {args.path}", file=sys.stderr)
        return 2

    deps, notes = discover(args.path)
    if args.json:
        print(json.dumps({"root": os.path.abspath(args.path),
                          "count": len(deps), "notes": notes,
                          "packages": deps}, indent=2))
    else:
        print(f"extract_dependencies.py — {os.path.abspath(args.path)}")
        for note in notes:
            print(f"  {note}")
        if deps:
            print("\nPackages (feed this list to OSV / NVD / GitHub Advisory "
                  "lookup — MANDATORY, Phase 5):\n")
            for d in sorted(deps, key=lambda x: (x["ecosystem"], x["name"])):
                print(f"  {d['ecosystem']:<10} {d['name']:<40} "
                      f"{d['version']:<20} [{d['kind']}]")
            print("\nREMINDER: known-CVE status exists only online. Check "
                  "each entry; never assert safety from this list alone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
