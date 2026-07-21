#!/usr/bin/env python3
"""Validate OKF documents against the Open Knowledge Format specification
plus house conventions.

Every finding is labelled:
    [SPEC]  — violates OKF v0.1 conformance (always fix)
    [HOUSE] — violates a house convention (fix unless the user waives it)

Usage:
    python3 validate_okf.py <path-to-file>
    python3 validate_okf.py <directory>  # validates all .md files in directory

Exit codes:
    0 = all validations passed
    1 = one or more validations failed
    2 = usage error
"""

import sys
import re
import os
import glob

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


class ValidationResult:
    def __init__(self, filepath):
        self.filepath = filepath
        self.findings = []  # list of (level, label, message)

    def error(self, msg, label="SPEC"):
        self.findings.append(("ERROR", label, msg))

    def warn(self, msg, label="SPEC"):
        self.findings.append(("WARN", label, msg))

    @property
    def errors(self):
        return [f for f in self.findings if f[0] == "ERROR"]

    @property
    def warnings(self):
        return [f for f in self.findings if f[0] == "WARN"]

    @property
    def passed(self):
        return len(self.errors) == 0


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
        except yaml.YAMLError:
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
            "'---' block closed by '---' on its own line."
        )
        return None

    if yaml is None:
        result.warn(
            "PyYAML not installed; using basic string checks. Install with: pip install pyyaml",
            label="HOUSE",
        )
        # Manual string-based checks
        if not re.search(r"^type:", yaml_str, re.MULTILINE):
            result.error("Frontmatter missing required 'type' field.")
        for field in ("title", "description", "tags", "timestamp"):
            if not re.search(rf"^{field}:", yaml_str, re.MULTILINE):
                result.warn(f"Frontmatter missing recommended '{field}' field.")
        return None

    try:
        fm = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        result.error(f"Invalid YAML in frontmatter: {e}")
        return None

    if not isinstance(fm, dict):
        result.error("Frontmatter must be a YAML mapping (key-value pairs).")
        return None

    # Required: type field
    if "type" not in fm:
        result.error("Frontmatter missing required 'type' field.")
    elif not fm["type"] or not str(fm["type"]).strip():
        result.error("Frontmatter 'type' field must not be empty.")

    # Recommended fields (spec §4.1)
    for field in ("title", "description", "tags", "timestamp"):
        if field not in fm:
            result.warn(f"Frontmatter missing recommended '{field}' field.")

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
        )


def validate_body(body, result, is_reserved):
    """Validate the markdown body."""
    if not body:
        result.error("Document body is empty.", label="HOUSE")
        return

    # For index.md: check for section headings (spec §6 structure)
    if is_reserved and os.path.basename(result.filepath) == "index.md":
        if not re.search(r"^#\s+.+", body, re.MULTILINE):
            result.warn(
                "index.md has no section headings. Consider organizing content under headings."
            )
        return

    # For log.md: date headings are required by spec §7 ("MUST use ISO 8601")
    if is_reserved and os.path.basename(result.filepath) == "log.md":
        if not re.search(r"^##\s+\d{4}-\d{2}-\d{2}", body, re.MULTILINE):
            result.error(
                "log.md has no date entries. Expected headings like '## 2026-07-20' (spec §7)."
            )
        return

    # For concept documents: H1 heading is a house convention
    h1_match = re.search(r"^#\s+.+", body, re.MULTILINE)
    if not h1_match:
        result.warn(
            "No H1 title heading found. Consider adding a top-level heading.",
            label="HOUSE",
        )


def validate_encoding(filepath, result):
    """Validate UTF-8 encoding."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
    except UnicodeDecodeError:
        result.error("File is not valid UTF-8 encoded.")


def validate_okf_file(filepath):
    """Run all validations on a single OKF file."""
    result = ValidationResult(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        result.error(f"File not found: {filepath}")
        return result
    except Exception as e:
        result.error(f"Error reading file: {e}")
        return result

    if not content.strip():
        result.error("File is empty.")
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
        # bundle-root index.md (spec §11), the only legal index frontmatter.
        if yaml_str is not None:
            filename = os.path.basename(filepath)
            keys = reserved_frontmatter_keys(yaml_str)
            if not (filename == "index.md" and keys is not None and keys <= {"okf_version"}):
                result.warn(
                    "Reserved file has frontmatter. Only an 'okf_version' key in the "
                    "bundle-root index.md is permitted (spec §11)."
                )
    else:
        # Concept documents must have frontmatter
        validate_frontmatter(yaml_str, result)

    # 5. Validate body
    validate_body(body, result, reserved)

    return result


def print_result(result):
    """Print validation result for a single file."""
    status = "PASS" if result.passed else "FAIL"
    print(f"\n[{status}] {result.filepath}")

    for level, label, message in result.findings:
        print(f"  {level} [{label}]: {message}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    target = sys.argv[1]

    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = sorted(glob.glob(os.path.join(target, "**", "*.md"), recursive=True))
        if not files:
            print(f"No .md files found in {target}")
            sys.exit(2)
    else:
        print(f"Error: {target} is not a file or directory")
        sys.exit(2)

    results = [validate_okf_file(filepath) for filepath in files]
    for result in results:
        print_result(result)

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
