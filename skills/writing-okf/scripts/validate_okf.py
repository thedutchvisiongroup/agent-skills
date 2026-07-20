#!/usr/bin/env python3
"""Validate OKF documents against the Open Knowledge Format specification.

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
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

RESERVED_FILES = {"index.md", "log.md"}

FILENAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$")


class ValidationResult:
    def __init__(self, filepath):
        self.filepath = filepath
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    @property
    def passed(self):
        return len(self.errors) == 0


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None, content

    end = content.find("---", 3)
    if end == -1:
        return None, content

    yaml_str = content[3:end].strip()
    body = content[end + 3:].strip()
    return yaml_str, body


def is_reserved_file(filepath):
    """Check if the file is a reserved OKF file (index.md or log.md)."""
    filename = os.path.basename(filepath)
    return filename in RESERVED_FILES


def validate_frontmatter(yaml_str, result):
    """Validate OKF frontmatter requirements."""
    if yaml_str is None:
        result.error("Missing YAML frontmatter. File must start with '---' block.")
        return None

    if yaml is None:
        result.warn("PyYAML not installed; using basic string checks. Install with: pip install pyyaml")
        # Manual string-based checks
        if not re.search(r"^type:", yaml_str, re.MULTILINE):
            result.error("Frontmatter missing required 'type' field.")
        if not re.search(r"^title:", yaml_str, re.MULTILINE):
            result.warn("Frontmatter missing recommended 'title' field.")
        if not re.search(r"^description:", yaml_str, re.MULTILINE):
            result.warn("Frontmatter missing recommended 'description' field.")
        if not re.search(r"^tags:", yaml_str, re.MULTILINE):
            result.warn("Frontmatter missing recommended 'tags' field.")
        if not re.search(r"^timestamp:", yaml_str, re.MULTILINE):
            result.warn("Frontmatter missing recommended 'timestamp' field.")
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

    # Recommended fields (warnings)
    if "title" not in fm:
        result.warn("Frontmatter missing recommended 'title' field.")
    if "description" not in fm:
        result.warn("Frontmatter missing recommended 'description' field.")
    if "tags" not in fm:
        result.warn("Frontmatter missing recommended 'tags' field.")
    if "timestamp" not in fm:
        result.warn("Frontmatter missing recommended 'timestamp' field.")

    return fm


def validate_filename(filepath, result):
    """Validate file naming convention."""
    filename = os.path.basename(filepath)

    # Reserved files are exempt from naming convention
    if filename in RESERVED_FILES:
        return

    if not FILENAME_PATTERN.match(filename):
        result.error(
            f"Filename '{filename}' does not match lowercase-kebab-case.md convention. "
            f"Example: my-concept.md"
        )


def validate_body(body, result, is_reserved):
    """Validate the markdown body."""
    if not body:
        result.error("Document body is empty.")
        return

    # For index.md: check for section headings
    if is_reserved and os.path.basename(result.filepath) == "index.md":
        # Index files should have at least one heading
        if not re.search(r"^#\s+.+", body, re.MULTILINE):
            result.warn("index.md has no section headings. Consider organizing content under headings.")
        return

    # For log.md: check for date entries
    if is_reserved and os.path.basename(result.filepath) == "log.md":
        if not re.search(r"^##\s+\d{4}-\d{2}-\d{2}", body, re.MULTILINE):
            result.warn("log.md has no date entries. Expected headings like '## 2026-07-20'.")
        return

    # For concept documents: check for H1 heading
    h1_match = re.search(r"^#\s+.+", body, re.MULTILINE)
    if not h1_match:
        result.warn("No H1 title heading found. Consider adding a top-level heading.")


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

    # 2. Filename convention
    validate_filename(filepath, result)

    # 3. Check if reserved file
    reserved = is_reserved_file(filepath)

    # 4. Parse and validate frontmatter
    yaml_str, body = parse_frontmatter(content)

    # Reserved files (index.md, log.md) have no frontmatter
    if reserved:
        if yaml_str is not None:
            result.warn(f"Reserved file has frontmatter. {os.path.basename(filepath)} files typically have no frontmatter.")
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

    for error in result.errors:
        print(f"  ERROR: {error}")

    for warning in result.warnings:
        print(f"  WARN:  {warning}")


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

    all_passed = True
    for filepath in files:
        result = validate_okf_file(filepath)
        print_result(result)
        if not result.passed:
            all_passed = False

    total = len(files)
    passed = sum(1 for f in files if validate_okf_file(f).passed)
    failed = total - passed

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
