#!/usr/bin/env python3
"""
validate.py — FTD Markdown validator.

Validates that an FTD Markdown file contains the mandatory sections for the
given scenario (feature / project / enterprise), that NFRs are measurable,
that privacy-by-design and security-by-design sections are present and
populated (not boilerplate), that the TOC is accurate, and that benefit
hypothesis is present for project/enterprise scenarios.

In --audit mode, produces a gap report (present / missing / incomplete per
section) instead of a pass/fail verdict — for reviewing existing documents.

Usage:
    python validate.py <ftd-file.md> --scenario <feature|project|enterprise>
    python validate.py <ftd-file.md> --scenario <feature|project|enterprise> --audit

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
        ["definition of ready"],
        ["definition of done"],
        ["architecture", "architectuur"],
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
        ["benefit hypothesis"],
        ["user stories"],
        ["acceptance criteria", "acceptatiecriteria"],
        ["traceability matrix"],
        ["definition of ready"],
        ["definition of done"],
        ["architecture", "architectuur"],
        ["data model", "datamodel"],
        ["api"],
        ["non-functional requirements", "non-functionele requirements"],
        ["privacy-by-design"],
        ["security-by-design"],
        ["risk register", "risico"],
        ["deployment"],
        ["glossary", "woordenlijst", "begrippenlijst"],
        ["approvals", "goedkeuring", "sign-off"],
    ],
    "enterprise": [
        ["document control", "documentbeheer"],
        ["executive summary"],
        ["scope"],
        ["stakeholders"],
        ["business context"],
        ["benefit hypothesis"],
        ["user stories"],
        ["acceptance criteria", "acceptatiecriteria"],
        ["traceability matrix"],
        ["definition of ready"],
        ["definition of done"],
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
        ["glossary", "woordenlijst", "begrippenlijst"],
        ["crosscutting concepts", "cross-cutting concepts"],
        ["approvals", "goedkeuring", "sign-off"],
    ],
}

# Enterprise-only sections — checked at heading level (not full-text substring).
ENTERPRISE_ONLY_HEADINGS = [
    ["dpia"],
    ["threat model", "dreigingsmodel"],
    ["nen 7510"],
    ["bio"],
    ["iso 27001"],
    ["sbom"],
    ["wcag"],
    ["ai act"],
]

PLACEHOLDER_RE = re.compile(r"\[PLACEHOLDER\]|\[veld\]|\[naam\]|\[link/ID\]|\[reden\]")
NFR_TABLE_RE = re.compile(
    r"\|.*?(subject|attribute|metric|threshold|verification).*?\|",
    re.IGNORECASE,
)

# EARS patterns for validation when EARS mode is detected.
EARS_PATTERNS = [
    re.compile(r"\bthe\s+\S+\s+shall\s+", re.IGNORECASE),  # Ubiquitous
    re.compile(r"\bwhile\s+.*?,?\s*the\s+\S+\s+shall\s+", re.IGNORECASE),  # State-driven
    re.compile(r"\bwhen\s+.*?,?\s*the\s+\S+\s+shall\s+", re.IGNORECASE),  # Event-driven
    re.compile(r"\bwhere\s+.*?,?\s*the\s+\S+\s+shall\s+", re.IGNORECASE),  # Optional feature
    re.compile(r"\bif\s+.*?,?\s*then\s+the\s+\S+\s+shall\s+", re.IGNORECASE),  # Unwanted
]


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


def find_heading_lines(content: str) -> list[tuple[int, str, str]]:
    """Return list of (line_number, level, heading_text) for all headings."""
    results = []
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped.lstrip("#").strip()
            if heading:
                results.append((i, level, normalize(heading)))
    return results


def check_sections(content: str, headings: list[str], scenario: str, audit: bool = False) -> list[str]:
    """Check that all mandatory sections are present as headings.
    Each section is a list of aliases (EN + NL); match if any alias is found."""
    errors = []
    required = SCENARIO_SECTIONS.get(scenario, [])
    joined = "\n".join(headings)
    for aliases in required:
        if not any(alias in joined for alias in aliases):
            label = aliases[0]
            if audit:
                errors.append(f"MISSING (mandatory): '{label}' not found in headings.")
            else:
                errors.append(
                    f"MISSING SECTION: '{label}' is mandatory for scenario "
                    f"'{scenario}' but was not found in headings."
                )
    return errors


def check_enterprise_only(content: str, headings: list[str], scenario: str, audit: bool = False) -> list[str]:
    """For enterprise scenario, check that enterprise-only sections are present at heading level."""
    errors = []
    if scenario != "enterprise":
        return errors
    joined = "\n".join(headings)
    for aliases in ENTERPRISE_ONLY_HEADINGS:
        # Check at heading level only (not full-text) to avoid false positives
        if not any(alias in joined for alias in aliases):
            label = aliases[0]
            if audit:
                errors.append(f"MISSING (enterprise-only): '{label}' not found in headings.")
            else:
                errors.append(
                    f"MISSING ENTERPRISE SECTION: '{label}' is mandatory for "
                    f"enterprise scenario but was not found as a heading."
                )
    return errors


def check_placeholders(content: str, audit: bool = False) -> list[str]:
    """Check for unfilled placeholders."""
    errors = []
    matches = PLACEHOLDER_RE.findall(content)
    if matches:
        label = "UNFILLED PLACEHOLDERS" if not audit else "INCOMPLETE (placeholders)"
        errors.append(
            f"{label}: found {len(matches)} placeholder(s) still "
            f"present in the document. Replace all [PLACEHOLDER]/[veld]/[naam] "
            f"with concrete content."
        )
    return errors


def check_nfrs_measurable(content: str, audit: bool = False) -> list[str]:
    """Check that NFR section contains measurable criteria (table with threshold)."""
    errors = []
    nfr_section = (
        extract_section(content, "non-functional requirements")
        or extract_section(content, "non-functionele requirements")
    )
    if not nfr_section:
        return errors
    if not re.search(r"threshold|drempelwaarde|<|≤|≥|ms|%|sec|min|u|s\b", nfr_section, re.IGNORECASE):
        label = "NFR NOT MEASURABLE" if not audit else "INCOMPLETE (NFRs not measurable)"
        errors.append(
            f"{label}: the non-functional requirements section does "
            f"not contain measurable thresholds. Every NFR must have a Metric + "
            f"Threshold + Verification."
        )
    return errors


def check_pbd_populated(content: str, audit: bool = False) -> list[str]:
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
        label = "PRIVACY-BY-DESIGN TOO SHORT" if not audit else "INCOMPLETE (PbD too short)"
        errors.append(
            f"{label}: section is under 200 characters — "
            "likely boilerplate. Document data inventory, DPIA decision, and "
            "applicable Cavoukian principles."
        )
    if "persoonsgegevens" not in pbd and "personal data" not in pbd.lower():
        label = "PRIVACY-BY-DESIGN INCOMPLETE" if not audit else "INCOMPLETE (PbD no data statement)"
        errors.append(
            f"{label}: section does not address whether "
            "personal data is processed. State explicitly: ja/nee with justification."
        )
    return errors


def check_sbd_populated(content: str, audit: bool = False) -> list[str]:
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
        label = "SECURITY-BY-DESIGN TOO SHORT" if not audit else "INCOMPLETE (SbD too short)"
        errors.append(
            f"{label}: section is under 200 characters — "
            "likely boilerplate. Document authentication, authorization, "
            "encryption, audit logging, and ASVS level."
        )
    if "authenticatie" not in sbd.lower() and "authentication" not in sbd.lower():
        label = "SECURITY-BY-DESIGN INCOMPLETE" if not audit else "INCOMPLETE (SbD no auth)"
        errors.append(
            f"{label}: section does not address authentication."
        )
    return errors


def check_traceability(content: str, scenario: str, audit: bool = False, section_errors: list[str] = None) -> list[str]:
    """Check that traceability matrix is present and populated.
    For feature scenario it is optional (may be dropped for trivial features) —
    only warn if absent, do not fail.
    Skips the 'missing' check if check_sections already reported it (avoids duplicates)."""
    errors = []
    tm = extract_section(content, "traceability matrix")
    if not tm:
        if scenario == "feature":
            # Optional for feature — note but do not fail
            if audit:
                errors.append("OPTIONAL (feature): traceability matrix not found. Recommended but may be dropped for trivial single-story features.")
            return errors
        # For project/enterprise: if check_sections already reported missing, don't duplicate
        if section_errors and any("traceability matrix" in e.lower() for e in section_errors):
            return errors
        errors.append(
            "MISSING TRACEABILITY MATRIX: section not found."
        )
        return errors
    if "US-" not in tm and "TC-" not in tm:
        label = "TRACEABILITY MATRIX EMPTY" if not audit else "INCOMPLETE (traceability empty)"
        errors.append(
            f"{label}: no user story IDs (US-) or test case IDs "
            "(TC-) found. Every requirement must map to a design component and test."
        )
    return errors


def check_dor_dod(content: str, audit: bool = False) -> list[str]:
    """Check that DoR and DoD are present. DoD is ALWAYS mandatory."""
    errors = []
    text = normalize(content)
    if "definition of ready" not in text and "dor" not in text.split():
        label = "MISSING DEFINITION OF READY" if not audit else "MISSING (DoR)"
        errors.append(f"{label}: DoR is always mandatory.")
    if "definition of done" not in text and "dod" not in text.split():
        label = "MISSING DEFINITION OF DONE" if not audit else "MISSING (DoD)"
        errors.append(f"{label}: DoD is ALWAYS mandatory, regardless of scenario.")
    return errors


def check_toc(content: str, audit: bool = False) -> list[str]:
    """Check that a table of contents is present AND accurate."""
    errors = []
    text = normalize(content)
    if "inhoudsopgave" not in text and "table of contents" not in text and "inhoud" not in text:
        errors.append("MISSING TABLE OF CONTENTS: a TOC is mandatory at the top.")
        return errors

    # TOC accuracy check: extract TOC items and compare against actual headings.
    toc_section = extract_section(content, "table of contents") or extract_section(content, "inhoudsopgave") or extract_section(content, "inhoud")
    if not toc_section:
        return errors  # TOC present but section extraction failed; skip accuracy check

    # Extract numbered TOC items (e.g. "1. Document control" or "1 Document control")
    toc_items = re.findall(r"^\s*\d+\.\s+(.+)$", toc_section, re.MULTILINE)
    if not toc_items:
        # Try without dot
        toc_items = re.findall(r"^\s*\d+\s+(.+)$", toc_section, re.MULTILINE)

    if not toc_items:
        if audit:
            errors.append("INCOMPLETE (TOC has no numbered items): TOC section found but no numbered entries detected.")
        return errors

    # Get actual top-level and second-level headings (excluding the TOC heading itself)
    actual_headings = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped.lstrip("#").strip()
            if heading and normalize(heading) not in ["table of contents", "inhoudsopgave", "inhoud"]:
                actual_headings.append((level, normalize(heading)))

    # Check that each TOC item matches an actual heading (by substring)
    toc_items_norm = [normalize(item.strip()) for item in toc_items]
    heading_texts = [h for _, h in actual_headings]

    mismatches = []
    for toc_item in toc_items_norm:
        # Check if the TOC item appears in any heading (allowing partial match)
        found = any(toc_item in ht or ht in toc_item for ht in heading_texts)
        if not found:
            mismatches.append(toc_item)

    if mismatches:
        label = "TOC INACCURATE" if not audit else "INCOMPLETE (TOC mismatch)"
        errors.append(
            f"{label}: {len(mismatches)} TOC item(s) do not match any heading: "
            f"{', '.join(mismatches[:5])}{'...' if len(mismatches) > 5 else ''}"
        )

    return errors


def check_mermaid(content: str, audit: bool = False) -> list[str]:
    """Check that Mermaid diagrams are present."""
    errors = []
    if "```mermaid" not in content:
        label = "NO MERMAID DIAGRAMS" if not audit else "MISSING (Mermaid)"
        errors.append(
            f"{label}: at least one Mermaid diagram (C4 Context) is "
            "mandatory in all scenarios."
        )
    return errors


def check_benefit_hypothesis(content: str, scenario: str, audit: bool = False) -> list[str]:
    """Check that benefit hypothesis is present for project/enterprise."""
    errors = []
    if scenario not in ("project", "enterprise"):
        return errors

    # Look for benefit hypothesis as a heading or in the business context section
    text = normalize(content)
    if "benefit hypothesis" not in text and "benefit-hypothesis" not in text:
        label = "MISSING BENEFIT HYPOTHESIS" if not audit else "MISSING (benefit hypothesis)"
        errors.append(
            f"{label}: benefit hypothesis is mandatory for scenario "
            f"'{scenario}'. It should state: 'We believe [business outcome] will be "
            f"achieved if [users] achieve [user outcome] with [feature]' — with a "
            f"measurable target and validation method."
        )
    return errors


def check_glossary(content: str, scenario: str, audit: bool = False) -> list[str]:
    """Check that glossary is present for project/enterprise."""
    errors = []
    if scenario not in ("project", "enterprise"):
        return errors

    headings = find_headings(content)
    joined = "\n".join(headings)
    if not any(alias in joined for alias in ["glossary", "woordenlijst", "begrippenlijst"]):
        label = "MISSING GLOSSARY" if not audit else "MISSING (glossary)"
        errors.append(
            f"{label}: glossary is mandatory for scenario '{scenario}'."
        )
    return errors


def check_crosscutting(content: str, scenario: str, audit: bool = False) -> list[str]:
    """Check that Crosscutting Concepts is present for enterprise."""
    errors = []
    if scenario != "enterprise":
        return errors

    headings = find_headings(content)
    joined = "\n".join(headings)
    if not any(alias in joined for alias in ["crosscutting concepts", "cross-cutting concepts"]):
        label = "MISSING CROSSCUTTING CONCEPTS" if not audit else "MISSING (crosscutting concepts)"
        errors.append(
            f"{label}: Crosscutting Concepts is mandatory for enterprise scenario."
        )
    return errors


def check_ears_format(content: str, audit: bool = False) -> list[str]:
    """If EARS mode is detected (via metadata or explicit marker), validate EARS patterns."""
    errors = []
    # Detect EARS mode: look for a marker comment or explicit "EARS" in the AC section heading
    ac_section = extract_section(content, "acceptance criteria") or extract_section(content, "acceptatiecriteria")
    if not ac_section:
        return errors

    # Check if EARS is indicated
    ears_indicated = (
        "ears" in normalize(ac_section[:200])  # heading area
        or "<!-- ac-format: ears -->" in normalize(content)
        or "acceptance criteria format: ears" in normalize(content)
    )

    if not ears_indicated:
        return errors  # bullets mode, no EARS check needed

    # Check that acceptance criteria contain EARS patterns
    # Look for lines that look like criteria (start with - or The/When/While/Where/If)
    criteria_lines = [
        line.strip().lstrip("-").strip()
        for line in ac_section.splitlines()
        if line.strip().startswith("-") and line.strip().lstrip("-").strip()
    ]

    if not criteria_lines:
        return errors

    non_ears_lines = []
    for line in criteria_lines:
        # Check if the line matches any EARS pattern
        matches_any = any(pattern.search(line) for pattern in EARS_PATTERNS)
        if not matches_any:
            # Allow non-criteria lines (like section headers, notes)
            if not line.startswith("#") and not line.startswith("**") and len(line) > 10:
                non_ears_lines.append(line)

    if non_ears_lines:
        label = "EARS FORMAT VIOLATION" if not audit else "INCOMPLETE (EARS violations)"
        errors.append(
            f"{label}: {len(non_ears_lines)} acceptance criterion/criteria do not "
            f"match EARS patterns (Ubiquitous/State-driven/Event-driven/Optional/"
            f"Unwanted). First: '{non_ears_lines[0][:80]}...'"
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


def validate(path: str, scenario: str, audit: bool = False) -> int:
    content = read_file(path)
    headings = find_headings(content)
    errors: list[str] = []

    errors.extend(check_toc(content, audit))
    section_errs = check_sections(content, headings, scenario, audit)
    errors.extend(section_errs)
    errors.extend(check_enterprise_only(content, headings, scenario, audit))
    errors.extend(check_placeholders(content, audit))
    errors.extend(check_nfrs_measurable(content, audit))
    errors.extend(check_pbd_populated(content, audit))
    errors.extend(check_sbd_populated(content, audit))
    errors.extend(check_traceability(content, scenario, audit, section_errs))
    errors.extend(check_dor_dod(content, audit))
    errors.extend(check_mermaid(content, audit))
    errors.extend(check_benefit_hypothesis(content, scenario, audit))
    errors.extend(check_glossary(content, scenario, audit))
    errors.extend(check_crosscutting(content, scenario, audit))
    errors.extend(check_ears_format(content, audit))

    if audit:
        print(f"=== AUDIT REPORT ===")
        print(f"Source: {path}")
        print(f"Scenario: {scenario}")
        print(f"Headings found: {len(headings)}")
        print("-" * 60)
        print()

        # Categorise findings
        critical = [e for e in errors if "MISSING" in e or "NOT MEASURABLE" in e]
        important = [e for e in errors if "INCOMPLETE" in e or "EMPTY" in e or "TOO SHORT" in e]
        nice_to_have = [e for e in errors if "INACCURATE" in e or "VIOLATION" in e]

        print("### Summary")
        print(f"- Critical findings: {len(critical)}")
        print(f"- Important findings: {len(important)}")
        print(f"- Nice-to-have findings: {len(nice_to_have)}")
        overall = "PASS" if not critical and not important else ("NEEDS IMPROVEMENT" if not critical else "FAIL")
        print(f"- Overall verdict: {overall}")
        print()

        if critical:
            print("### Critical (mandatory section missing or non-functional)")
            for i, e in enumerate(critical, 1):
                print(f"  {i}. {e}")
            print()

        if important:
            print("### Important (mandatory section present but incomplete)")
            for i, e in enumerate(important, 1):
                print(f"  {i}. {e}")
            print()

        if nice_to_have:
            print("### Nice-to-have (polish and accuracy)")
            for i, e in enumerate(nice_to_have, 1):
                print(f"  {i}. {e}")
            print()

        print("### Next steps")
        print("1. Address all Critical findings.")
        print("2. Address Important findings.")
        print("3. Consider Nice-to-have findings.")
        print(f"4. Re-run: python scripts/validate.py {path} --scenario {scenario}")
        return 0 if not critical else 2

    # Non-audit mode: pass/fail
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
    parser.add_argument(
        "--audit",
        action="store_true",
        default=False,
        help="Produce a gap report (present/missing/incomplete) instead of pass/fail. "
             "For reviewing existing documents.",
    )
    args = parser.parse_args()
    return validate(args.file, args.scenario, args.audit)


if __name__ == "__main__":
    sys.exit(main())
