#!/usr/bin/env python3
"""Validate ADR files against OKF frontmatter + MADR 4.0 body structure.

OKF v0.2 provenance: the frontmatter requires a `generated` block ({by, at}).
`by` must follow the actor convention (<harness>/<model-id>, harness opencode or
claude-code | human:<id> | process:<id>); `at` must be an ISO 8601 datetime with explicit UTC offset.
A legacy `timestamp` field triggers a WARN migration nudge only, never an error.

Deliberate divergence vs validate_okf.py (ADR layer is intentionally stricter):
this validator rejects quoted ISO 8601 `at` shapes that the generic OKF
validator accepts (space-separated datetimes, lowercase 't'/'z', no-seconds,
hour-only offsets) and only inspects list-form `verified` entries (bare-mapping
`verified` is skipped). ADRs should use the full YYYY-MM-DDTHH:MM:SS±HH:MM form.

Usage:
    python3 validate_adr.py <path-to-adr-file>
    python3 validate_adr.py <directory>  # validates all ADR .md files in directory
                                         # (reserved files index.md/log.md are skipped)

Exit codes:
    0 = all validations passed
    1 = one or more validations failed
    2 = usage error
"""

import sys
import re
import os
import glob
import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

VALID_STATUSES = {"proposed", "rejected", "accepted", "deprecated", "superseded"}

RESERVED_FILENAMES = {"index.md", "log.md"}

REQUIRED_FRONTMATTER_FIELDS = ["title", "description", "tags", "deciders", "status", "generated"]

REQUIRED_SECTIONS = [
    "Context and Problem Statement",
    "Considered Options",
    "Decision Outcome",
]

FILENAME_PATTERN = re.compile(r"^\d{4}-[a-z0-9]+(-[a-z0-9]+)*\.md$")

# Actor convention (house): <harness>/<model-id> (harness opencode or claude-code)
# | human:<id> | process:<id>
ACTOR_PATTERN = re.compile(r"^((?:opencode|claude-code)/[A-Za-z0-9._-]+|human:[A-Za-z0-9@._-]+|process:[A-Za-z0-9._-]+)$")

# ISO 8601 datetime with explicit UTC offset, e.g. 2026-07-21T10:00:00Z or 2026-07-21T10:00:00+02:00
GENERATED_AT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(Z|[+-]\d{2}:?\d{2})$")

LEGACY_TIMESTAMP_WARN = (
    "Frontmatter has legacy 'timestamp' field (retired in OKF v0.2); "
    "migrate to 'generated: {by, at}'."
)

# Legacy MADR 2.x metadata lines that must NOT appear in the body
LEGACY_METADATA_PATTERNS = [
    (re.compile(r"^-\s*Status:", re.MULTILINE | re.IGNORECASE), "- Status:"),
    (re.compile(r"^-\s*Deciders:", re.MULTILINE | re.IGNORECASE), "- Deciders:"),
    (re.compile(r"^-\s*Date:", re.MULTILINE | re.IGNORECASE), "- Date:"),
]


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


def check_status_and_supersede(status_value, superseded_by, filepath, result):
    """Shared status/superseded_by checks for both YAML and fallback paths."""
    if status_value is None:
        result.error("Frontmatter missing required 'status' field.")
        return
    if status_value not in VALID_STATUSES:
        result.error(
            f"Invalid status '{status_value}'. "
            f"Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )
        return
    if status_value == "superseded":
        if not superseded_by:
            result.error("Status is 'superseded' but frontmatter lacks 'superseded_by: <path>'.")
        else:
            target = os.path.normpath(os.path.join(os.path.dirname(filepath), superseded_by))
            if not os.path.exists(target):
                result.warn(f"superseded_by target not found on disk: {superseded_by}")


def check_actor_format(by_value, field_label, result):
    """Warn when an actor value does not follow the house actor convention."""
    if not ACTOR_PATTERN.match(str(by_value).strip()):
        result.warn(
            f"Frontmatter '{field_label}' does not follow the actor convention "
            f"<harness>/<model-id> (opencode or claude-code) | human:<id> | process:<id>, got '{by_value}'."
        )


def check_generated_at(at_value, result):
    """Validate generated.at is an ISO 8601 datetime with explicit UTC offset.

    PyYAML parses ISO 8601 timestamps into datetime objects; such values are
    valid by construction, but an offset-less (naive) datetime is rejected.
    A date-only value (no time) or a non-ISO string is rejected as well.
    """
    if isinstance(at_value, datetime.datetime):
        if at_value.tzinfo is None:
            result.error(
                f"Frontmatter 'generated.at' must include an explicit UTC offset "
                f"(e.g., 2026-07-21T10:00:00+02:00), got offset-less '{at_value}'."
            )
        return
    if isinstance(at_value, datetime.date):
        result.error(
            f"Frontmatter 'generated.at' must include a time component with "
            f"explicit UTC offset (e.g., 2026-07-21T10:00:00+02:00), got date-only '{at_value}'."
        )
        return
    at_raw = str(at_value).strip()
    if not GENERATED_AT_PATTERN.match(at_raw):
        result.error(
            f"Frontmatter 'generated.at' must be an ISO 8601 datetime with "
            f"explicit UTC offset (e.g., 2026-07-21T10:00:00+02:00), got '{at_raw}'."
        )


def check_generated(generated_value, result):
    """Validate the OKF v0.2 provenance block 'generated' (required: by + at)."""
    if not isinstance(generated_value, dict):
        result.error(
            "Frontmatter 'generated' must be a mapping with 'by' and 'at' "
            f"(OKF v0.2 provenance), got {type(generated_value).__name__} '{generated_value}'."
        )
        return

    by_value = generated_value.get("by")
    if by_value is None or str(by_value).strip() == "":
        result.error("Frontmatter 'generated' must include a non-empty 'by' actor.")
    else:
        check_actor_format(by_value, "generated.by", result)

    at_value = generated_value.get("at")
    if at_value is None or (isinstance(at_value, str) and at_value.strip() == ""):
        result.error("Frontmatter 'generated' must include an 'at' ISO 8601 datetime.")
    else:
        check_generated_at(at_value, result)


def validate_frontmatter(yaml_str, filepath, result):
    """Validate OKF frontmatter + ADR extension fields. Returns (title, body_title_ok) info."""
    if yaml_str is None:
        result.error("Missing YAML frontmatter. File must start with '---' block.")
        return None

    if yaml is None:
        result.warn("PyYAML not installed; using basic string checks. Install with: pip install pyyaml")
        if not re.search(r"^type:\s*ADR\s*$", yaml_str, re.MULTILINE):
            if re.search(r"^type:", yaml_str, re.MULTILINE):
                result.error("Frontmatter 'type' must be 'ADR'.")
            else:
                result.error("Frontmatter missing required 'type' field.")
        for field in ["title", "description", "tags", "deciders", "generated"]:
            if not re.search(rf"^{field}:", yaml_str, re.MULTILINE):
                result.error(f"Frontmatter missing required '{field}' field.")
        if re.search(r"^timestamp:", yaml_str, re.MULTILINE):
            result.warn(LEGACY_TIMESTAMP_WARN)
        gen_match = re.search(r"^generated:\s*(\S.*)?$", yaml_str, re.MULTILINE)
        if gen_match:
            gen_inline = gen_match.group(1) or ""
            by_match = re.search(r"\bby:\s*[\"']?([^\s\",}{]+)", gen_inline) or re.search(
                r"^\s+by:\s*(\S+)", yaml_str, re.MULTILINE
            )
            at_match = re.search(r"\bat:\s*[\"']?([^\s\",}{]+)", gen_inline) or re.search(
                r"^\s+at:\s*(\S+)", yaml_str, re.MULTILINE
            )
            if not by_match:
                result.error("Frontmatter 'generated' must include a non-empty 'by' actor.")
            else:
                check_actor_format(by_match.group(1).strip('"\''), "generated.by", result)
            if not at_match:
                result.error("Frontmatter 'generated' must include an 'at' ISO 8601 datetime.")
            else:
                check_generated_at(at_match.group(1).strip('"\''), result)
        status_match = re.search(r"^status:\s*(\S+)", yaml_str, re.MULTILINE)
        supersede_match = re.search(r"^superseded_by:\s*(\S+)", yaml_str, re.MULTILINE)
        check_status_and_supersede(
            status_match.group(1).strip('"\'') if status_match else None,
            supersede_match.group(1).strip('"\'') if supersede_match else None,
            filepath,
            result,
        )
        title_match = re.search(r"^title:\s*(.+)$", yaml_str, re.MULTILINE)
        return title_match.group(1).strip().strip('"\'') if title_match else None

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
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in fm:
            result.error(f"Frontmatter missing required '{field}' field.")

    # List-typed fields
    for field in ("tags", "deciders"):
        if field in fm and not (isinstance(fm[field], list) and len(fm[field]) > 0):
            result.error(f"Frontmatter '{field}' must be a non-empty YAML list.")

    # OKF v0.2 provenance block (replaces the legacy timestamp field)
    if "generated" in fm:
        check_generated(fm["generated"], result)

    # Legacy timestamp: retired in OKF v0.2 → migration nudge only
    if "timestamp" in fm:
        result.warn(LEGACY_TIMESTAMP_WARN)

    # Optional OKF v0.2 trust layer: warn on bad actor format in verified entries
    verified = fm.get("verified")
    if isinstance(verified, list):
        for entry in verified:
            if isinstance(entry, dict) and entry.get("by"):
                check_actor_format(entry["by"], "verified[].by", result)

    # Status + superseded_by
    status_value = str(fm["status"]).strip().lower() if "status" in fm else None
    check_status_and_supersede(status_value, fm.get("superseded_by"), filepath, result)

    title = fm.get("title")
    return str(title).strip() if title is not None else None


def validate_filename(filepath, result):
    """Validate NNNN-kebab-case-title.md naming convention."""
    filename = os.path.basename(filepath)
    if not FILENAME_PATTERN.match(filename):
        result.error(
            f"Filename '{filename}' does not match NNNN-kebab-case-title.md convention. "
            f"Example: 0001-use-postgresql.md"
        )


def validate_body_sections(body, fm_title, result):
    """Validate required MADR 4.0 body sections and title/H1 consistency."""
    if not body:
        result.error("ADR body is empty.")
        return

    # Check H1 title
    h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if not h1_match:
        result.error("Missing H1 title heading.")
    elif fm_title is not None and h1_match.group(1).strip() != fm_title:
        result.error(
            f"Frontmatter 'title' ('{fm_title}') does not match H1 heading "
            f"('{h1_match.group(1).strip()}')."
        )

    # Check required H2 sections
    for section in REQUIRED_SECTIONS:
        pattern = rf"^##\s+{re.escape(section)}(?:\s|$)"
        if not re.search(pattern, body, re.MULTILINE):
            result.error(f"Missing required section: '## {section}'")

    # Guard: no legacy MADR 2.x metadata duplicated in the body
    for pattern, label in LEGACY_METADATA_PATTERNS:
        if pattern.search(body):
            result.error(
                f"Body contains legacy metadata line '{label}'. "
                f"Status, deciders and date live in the YAML frontmatter only (MADR 4.0)."
            )


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

    # 2. Parse and validate frontmatter (returns title for H1 cross-check)
    yaml_str, body = parse_frontmatter(content)
    fm_title = validate_frontmatter(yaml_str, filepath, result)

    # 3. Validate body sections + title/H1 match + legacy metadata guard
    validate_body_sections(body, fm_title, result)

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
        if os.path.basename(target) in RESERVED_FILENAMES:
            print(f"[SKIP] {target} is a reserved filename (not an ADR).")
            sys.exit(0)
        files = [target]
    elif os.path.isdir(target):
        files = sorted(
            f for f in glob.glob(os.path.join(target, "*.md"))
            if os.path.basename(f) not in RESERVED_FILENAMES
        )
        if not files:
            print(f"No ADR .md files found in {target} (reserved files index.md/log.md are skipped)")
            sys.exit(2)
    else:
        print(f"Error: {target} is not a file or directory")
        sys.exit(2)

    results = [validate_adr_file(filepath) for filepath in files]
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
