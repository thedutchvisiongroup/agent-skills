#!/usr/bin/env python3
"""Validate ADR files against OKF frontmatter + MADR body structure.

Usage:
    python3 validate_adr.py <path-to-adr-file>
    python3 validate_adr.py <directory>  # validates all .md files in directory

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

VALID_STATUSES = {"proposed", "accepted", "deprecated", "superseded"}

REQUIRED_SECTIONS = [
    "Context and Problem Statement",
    "Decision Drivers",
    "Considered Options",
    "Decision Outcome",
    "Pros and Cons of the Options",
    "Links",
]

REQUIRED_H3_SECTIONS = [
    "Positive Consequences",
    "Negative Consequences",
]

FILENAME_PATTERN = re.compile(r"^\d{4}-[a-z0-9]+(-[a-z0-9]+)*\.md$")


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


def validate_frontmatter(yaml_str, result):
    """Validate OKF frontmatter requirements."""
    if yaml_str is None:
        result.error("Missing YAML frontmatter. File must start with '---' block.")
        return None

    if yaml is None:
        result.warn("PyYAML not installed; using basic string checks. Install with: pip install pyyaml")
        # Manual string-based checks for frontmatter fields
        if not re.search(r"^type:\s*ADR\s*$", yaml_str, re.MULTILINE):
            if re.search(r"^type:", yaml_str, re.MULTILINE):
                result.error("Frontmatter 'type' must be 'ADR'.")
            else:
                result.error("Frontmatter missing required 'type' field.")
        if not re.search(r"^title:", yaml_str, re.MULTILINE):
            result.error("Frontmatter missing required 'title' field.")
        if not re.search(r"^description:", yaml_str, re.MULTILINE):
            result.error("Frontmatter missing required 'description' field.")
        if not re.search(r"^tags:", yaml_str, re.MULTILINE):
            result.error("Frontmatter missing required 'tags' field.")
        if not re.search(r"^timestamp:", yaml_str, re.MULTILINE):
            result.error("Frontmatter missing required 'timestamp' field.")
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
    elif fm["type"] != "ADR":
        result.error(f"Frontmatter 'type' must be 'ADR', got '{fm['type']}'.")

    # Required fields
    if "title" not in fm:
        result.error("Frontmatter missing required 'title' field.")
    if "description" not in fm:
        result.error("Frontmatter missing required 'description' field.")
    if "tags" not in fm:
        result.error("Frontmatter missing required 'tags' field.")
    if "timestamp" not in fm:
        result.error("Frontmatter missing required 'timestamp' field.")

    return fm


def validate_filename(filepath, result):
    """Validate NNNN-kebab-case-title.md naming convention."""
    filename = os.path.basename(filepath)
    if not FILENAME_PATTERN.match(filename):
        result.error(
            f"Filename '{filename}' does not match NNNN-kebab-case-title.md convention. "
            f"Example: 0001-use-postgresql.md"
        )


def validate_body_sections(body, result):
    """Validate required MADR body sections exist."""
    if not body:
        result.error("ADR body is empty.")
        return

    # Check H1 title
    h1_match = re.search(r"^#\s+.+", body, re.MULTILINE)
    if not h1_match:
        result.error("Missing H1 title heading.")

    # Check required H2 sections
    for section in REQUIRED_SECTIONS:
        pattern = rf"^##\s+{re.escape(section)}(?:\s|$)"
        if not re.search(pattern, body, re.MULTILINE):
            result.error(f"Missing required section: '## {section}'")

    # Check required H3 sections (under Decision Outcome)
    for section in REQUIRED_H3_SECTIONS:
        pattern = rf"^###\s+{re.escape(section)}(?:\s|$)"
        if not re.search(pattern, body, re.MULTILINE):
            result.error(f"Missing required section: '### {section}'")


def validate_status(body, result):
    """Validate the Status field has a valid value."""
    status_match = re.search(
        r"^-\s*Status:\s*(.+)$", body, re.MULTILINE | re.IGNORECASE
    )
    if not status_match:
        result.error("Missing 'Status' field in body (e.g., '- Status: proposed').")
        return

    status_raw = status_match.group(1).strip().lower()

    # Handle "superseded by [ADR-NNNN](link)"
    if status_raw.startswith("superseded"):
        return  # Valid

    # Check against known statuses (extract first word)
    status_value = status_raw.split("|")[0].strip().rstrip(".")
    if status_value not in VALID_STATUSES:
        result.error(
            f"Invalid status '{status_value}'. "
            f"Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )


def validate_metadata_fields(body, result):
    """Validate Deciders and Date fields exist."""
    if not re.search(r"^-\s*Deciders:", body, re.MULTILINE | re.IGNORECASE):
        result.error("Missing required 'Deciders' field in body.")

    if not re.search(r"^-\s*Date:", body, re.MULTILINE | re.IGNORECASE):
        result.error("Missing required 'Date' field in body.")


def validate_adr_file(filepath):
    """Run all validations on a single ADR file."""
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

    # 1. Filename convention
    validate_filename(filepath, result)

    # 2. Parse and validate frontmatter
    yaml_str, body = parse_frontmatter(content)
    validate_frontmatter(yaml_str, result)

    # 3. Validate body sections
    validate_body_sections(body, result)

    # 4. Validate status
    validate_status(body, result)

    # 5. Validate metadata fields
    validate_metadata_fields(body, result)

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
        files = sorted(glob.glob(os.path.join(target, "*.md")))
        if not files:
            print(f"No .md files found in {target}")
            sys.exit(2)
    else:
        print(f"Error: {target} is not a file or directory")
        sys.exit(2)

    all_passed = True
    for filepath in files:
        result = validate_adr_file(filepath)
        print_result(result)
        if not result.passed:
            all_passed = False

    total = len(files)
    passed = sum(1 for f in files if validate_adr_file(f).passed)
    failed = total - passed

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()