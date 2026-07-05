#!/usr/bin/env python3
"""
validate.py — FTD Markdown validator.

Validates that an FTD Markdown file contains the mandatory sections for the
given scenario (feature / project / enterprise), that NFRs are measurable,
and that privacy-by-design and security-by-design sections are present and
populated (not boilerplate).

Usage:
    python validate.py <ftd-file.md> --scenario <feature|project|enterprise>

Dependencies: Python 3 standard library only. No pip install required.
"""

import argparse
import re
import sys
from pathlib import Path


# Each mandatory section is a list of accepted aliases (EN + NL).
# A heading matches if ANY alias is found as a substring (case-insensitive).
SCENARIO_SECTIONS = {
    "feature": [
        ["document control", "documentbeheer"],
        ["scope"],
        ["user stories"],
        ["acceptance criteria", "acceptatiecriteria"],
        ["traceability matrix"],
        ["definition of ready"],
        ["architecture", "architectuur"],
        ["non-functional requirements", "non-functionele requirements"],
        ["privacy-by-design"],
        ["security-by-design"],
        ["approvals", "goedkeuring", "sign-off"],
    ],
    "project": [
        ["document control", "documentbeheer"],
        ["executive summary"],
        ["scope"],
        ["stakeholders"],
        ["business context"],
        ["user stories"],
        ["acceptance criteria", "acceptatiecriteria"],
        ["traceability matrix"],
        ["definition of ready"],
        ["architecture", "architectuur"],
        ["data model", "datamodel"],
        ["api"],
        ["non-functional requirements", "non-functionele requirements"],
        ["privacy-by-design"],
        ["security-by-design"],
        ["risk register", "risico"],
        ["deployment"],
        ["approvals", "goedkeuring", "sign-off"],
    ],
    "enterprise": [
        ["document control", "documentbeheer"],
        ["executive summary"],
        ["scope"],
        ["stakeholders"],
        ["business context"],
        ["user stories"],
        ["acceptance criteria", "acceptatiecriteria"],
        ["traceability matrix"],
        ["definition of ready"],
        ["architecture", "architectuur"],
        ["data model", "datamodel"],
        ["api"],
        ["non-functional requirements", "non-functionele requirements"],
        ["privacy-by-design"],
        ["security-by-design"],
        ["risk register", "risico"],
        ["deployment"],
        ["observability"],
        ["compliance evidence"],
        ["migration", "migratie"],
        ["approvals", "goedkeuring", "sign-off"],
    ],
}

ENTERPRISE_ONLY = {
    "enterprise": [
        "dpia",
        "threat model",
        "nen 7510",
        "bio",
        "iso 27001",
        "sbom",
        "wcag",
        "ai act",
    ],
}

PLACEHOLDER_RE = re.compile(r"\[PLACEHOLDER\]|\[veld\]|\[naam\]|\[link/ID\]|\[reden\]")
NFR_TABLE_RE = re.compile(
    r"\|.*?(subject|attribute|metric|threshold|verification).*?\|",
    re.IGNORECASE,
)


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        sys.exit(f"ERROR: file not found: {path}")
    return p.read_text(encoding="utf-8")


def normalize(text: str) -> str:
    return text.lower()


def find_headings(content: str) -> list[str]:
    """Return list of heading texts (## and ### level)."""
    headings = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("##") or stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                headings.append(normalize(heading))
    return headings


def check_sections(content: str, headings: list[str], scenario: str) -> list[str]:
    """Check that all mandatory sections are present as headings.
    Each section is a list of aliases (EN + NL); match if any alias is found."""
    errors = []
    required = SCENARIO_SECTIONS.get(scenario, [])
    joined = "\n".join(headings)
    for aliases in required:
        if not any(alias in joined for alias in aliases):
            label = aliases[0]
            errors.append(
                f"MISSING SECTION: '{label}' is mandatory for scenario "
                f"'{scenario}' but was not found in headings."
            )
    return errors


def check_enterprise_only(content: str, headings: list[str], scenario: str) -> list[str]:
    """For enterprise scenario, check that enterprise-only sections are present."""
    errors = []
    if scenario != "enterprise":
        return errors
    required = ENTERPRISE_ONLY.get("enterprise", [])
    joined = "\n".join(headings)
    full_text = normalize(content)
    for section in required:
        if section not in joined and section not in full_text:
            errors.append(
                f"MISSING ENTERPRISE SECTION: '{section}' is mandatory for "
                f"enterprise scenario but was not found."
            )
    return errors


def check_placeholders(content: str) -> list[str]:
    """Check for unfilled placeholders."""
    errors = []
    matches = PLACEHOLDER_RE.findall(content)
    if matches:
        errors.append(
            f"UNFILLED PLACEHOLDERS: found {len(matches)} placeholder(s) still "
            f"present in the document. Replace all [PLACEHOLDER]/[veld]/[naam] "
            f"with concrete content."
        )
    return errors


def check_nfrs_measurable(content: str) -> list[str]:
    """Check that NFR section contains measurable criteria (table with threshold)."""
    errors = []
    nfr_section = (
        extract_section(content, "non-functional requirements")
        or extract_section(content, "non-functionele requirements")
    )
    if not nfr_section:
        return errors
    if not re.search(r"threshold|drempelwaarde|<|≤|≥|ms|%|sec|min|u|s\b", nfr_section, re.IGNORECASE):
        errors.append(
            "NFR NOT MEASURABLE: the non-functional requirements section does "
            "not contain measurable thresholds. Every NFR must have a Metric + "
            "Threshold + Verification."
        )
    return errors


def check_pbd_populated(content: str) -> list[str]:
    """Check that privacy-by-design section is present and not boilerplate."""
    errors = []
    pbd = extract_section(content, "privacy-by-design")
    if not pbd:
        errors.append(
            "MISSING PRIVACY-BY-DESIGN: section not found. Privacy-by-design is "
            "ALWAYS mandatory, even if no personal data is processed."
        )
        return errors
    if len(pbd) < 200:
        errors.append(
            "PRIVACY-BY-DESIGN TOO SHORT: section is under 200 characters — "
            "likely boilerplate. Document data inventory, DPIA decision, and "
            "applicable Cavoukian principles."
        )
    if "persoonsgegevens" not in pbd and "personal data" not in pbd.lower():
        errors.append(
            "PRIVACY-BY-DESIGN INCOMPLETE: section does not address whether "
            "personal data is processed. State explicitly: ja/nee with justification."
        )
    return errors


def check_sbd_populated(content: str) -> list[str]:
    """Check that security-by-design section is present and not boilerplate."""
    errors = []
    sbd = extract_section(content, "security-by-design")
    if not sbd:
        errors.append(
            "MISSING SECURITY-BY-DESIGN: section not found. Security-by-design "
            "is ALWAYS mandatory."
        )
        return errors
    if len(sbd) < 200:
        errors.append(
            "SECURITY-BY-DESIGN TOO SHORT: section is under 200 characters — "
            "likely boilerplate. Document authentication, authorization, "
            "encryption, audit logging, and ASVS level."
        )
    if "authenticatie" not in sbd.lower() and "authentication" not in sbd.lower():
        errors.append(
            "SECURITY-BY-DESIGN INCOMPLETE: section does not address authentication."
        )
    return errors


def check_traceability(content: str) -> list[str]:
    """Check that traceability matrix is present and populated."""
    errors = []
    tm = extract_section(content, "traceability matrix")
    if not tm:
        errors.append(
            "MISSING TRACEABILITY MATRIX: section not found. Required in all scenarios."
        )
        return errors
    if "US-" not in tm and "TC-" not in tm:
        errors.append(
            "TRACEABILITY MATRIX EMPTY: no user story IDs (US-) or test case IDs "
            "(TC-) found. Every requirement must map to a design component and test."
        )
    return errors


def check_dor_dod(content: str) -> list[str]:
    """Check that DoR and DoD are present."""
    errors = []
    text = normalize(content)
    if "definition of ready" not in text and "dor" not in text.split():
        errors.append("MISSING DEFINITION OF READY: DoR is always mandatory.")
    if "definition of done" not in text and "dod" not in text.split():
        errors.append("MISSING DEFINITION OF DONE: DoD is always mandatory.")
    return errors


def check_toc(content: str) -> list[str]:
    """Check that a table of contents is present."""
    errors = []
    text = normalize(content)
    if "inhoudsopgave" not in text and "table of contents" not in text and "inhoud" not in text:
        errors.append("MISSING TABLE OF CONTENTS: a TOC is mandatory at the top.")
    return errors


def check_mermaid(content: str) -> list[str]:
    """Check that Mermaid diagrams are present."""
    errors = []
    if "```mermaid" not in content:
        errors.append(
            "NO MERMAID DIAGRAMS: at least one Mermaid diagram (C4 Context) is "
            "mandatory in all scenarios."
        )
    return errors


def extract_section(content: str, heading_text: str) -> str:
    """Extract the body of a section given a (partial) heading text.
    Includes sub-headings (### and deeper) as part of the section body."""
    lines = content.splitlines()
    in_section = False
    section_level = 0
    body = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = normalize(stripped.lstrip("#").strip())
            if not in_section and heading_text in heading:
                in_section = True
                section_level = level
                continue
            elif in_section and level <= section_level:
                break
            # else: sub-heading (level > section_level) — fall through to add it
        if in_section:
            body.append(line)
    return "\n".join(body)


def validate(path: str, scenario: str) -> int:
    content = read_file(path)
    headings = find_headings(content)
    errors: list[str] = []

    errors.extend(check_toc(content))
    errors.extend(check_sections(content, headings, scenario))
    errors.extend(check_enterprise_only(content, headings, scenario))
    errors.extend(check_placeholders(content))
    errors.extend(check_nfrs_measurable(content))
    errors.extend(check_pbd_populated(content))
    errors.extend(check_sbd_populated(content))
    errors.extend(check_traceability(content))
    errors.extend(check_dor_dod(content))
    errors.extend(check_mermaid(content))

    print(f"Validating: {path}")
    print(f"Scenario:   {scenario}")
    print(f"Headings:   {len(headings)} found")
    print("-" * 60)

    if not errors:
        print("PASS — all mandatory checks passed.")
        return 0

    print(f"FAIL — {len(errors)} issue(s) found:\n")
    for i, e in enumerate(errors, 1):
        print(f"  {i}. {e}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an FTD Markdown file against the mandatory sections for a scenario."
    )
    parser.add_argument("file", help="Path to the FTD Markdown file")
    parser.add_argument(
        "--scenario",
        choices=["feature", "project", "enterprise"],
        required=True,
        help="Scenario tier to validate against",
    )
    args = parser.parse_args()
    return validate(args.file, args.scenario)


if __name__ == "__main__":
    sys.exit(main())
