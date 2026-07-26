#!/usr/bin/env python3
"""
validate.py — FTD Markdown validator (ceiling model).

Philosophy: the FTD skill uses a CEILING model. Every FTD contains a small
mandatory CORE. Scenario-default sections are recommended, but may be omitted
when the omission is justified in the document's "Omitted sections & open
questions" section. The validator therefore reports at three levels:

  ERROR    — core section missing, enterprise-required section missing,
             or a present section is broken (NFRs not measurable, placeholders,
             PbD/SbD without substance). Exit code 1.
  WARNING  — recommended section missing WITHOUT a recorded justification,
             or the size budget is exceeded. Exit code stays 0.
  INFO     — advisory notes (audit-mode categorisation).

The validator is ADVISORY. If a check appears to be wrong for a legitimate
document, report it to the user — do not pad or contort the document to
satisfy a check.

Usage:
    python validate.py <ftd-file.md> --scenario <feature|project|enterprise>
    python validate.py <ftd-file.md> --scenario <scenario> --audit
    python validate.py <ftd-file.md> --scenario <scenario> --max-lines 200

Dependencies: Python 3 standard library only. No pip install required.
"""

import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Section model
# ---------------------------------------------------------------------------
# Each section is a list of accepted aliases (EN + NL). A heading matches when
# any alias matches. Short aliases (<=4 chars) are matched with word
# boundaries to avoid false hits (e.g. "api" inside "Rapid", "bio" inside
# "biografie").

# Core: mandatory in EVERY scenario. Missing core = ERROR.
CORE_SECTIONS = [
    ["document control", "documentbeheer"],
    ["scope"],
    ["user stories", "user story"],
    ["acceptance criteria", "acceptatiecriteria"],
    ["definition of done", "definitie van klaar"],  # DoD is ALWAYS mandatory
    ["privacy-by-design", "privacy by design"],
    ["security-by-design", "security by design"],
]

# Recommended: default-included per scenario, but MAY be omitted when the
# omission is justified in the "Omitted sections & open questions" section.
# Missing + unjustified = WARNING (not an error). Ceiling model.
RECOMMENDED_SECTIONS = {
    "feature": [
        ["definition of ready", "definitie van gereed"],
        ["architecture", "architectuur"],
        ["traceability matrix", "traceerbaarheid"],
        ["approvals", "goedkeuring", "sign-off", "akkoord"],
    ],
    "project": [
        ["executive summary", "managementsamenvatting"],
        ["stakeholders", "raci", "belanghebbenden"],
        ["business context", "bedrijfscontext", "organisatiecontext"],
        ["benefit hypothesis", "batenhypothese", "waardehypothese"],
        ["traceability matrix", "traceerbaarheid"],
        ["definition of ready", "definitie van gereed"],
        ["architecture", "architectuur"],
        ["data model", "datamodel"],
        ["api", "integration", "integratie"],
        ["non-functional requirements", "non-functionele requirements", "nfr"],
        ["risk register", "risicoregister", "risico"],
        ["deployment", "rollback", "uitrol", "terugval"],
        ["glossary", "woordenlijst", "begrippenlijst"],
        ["approvals", "goedkeuring", "sign-off"],
    ],
    "enterprise": [
        ["executive summary", "managementsamenvatting"],
        ["stakeholders", "raci", "belanghebbenden"],
        ["business context", "bedrijfscontext", "organisatiecontext"],
        ["benefit hypothesis", "batenhypothese", "waardehypothese"],
        ["traceability matrix", "traceerbaarheid"],
        ["definition of ready", "definitie van gereed"],
        ["architecture", "architectuur"],
        ["data model", "datamodel"],
        ["api", "integration", "integratie"],
        ["risk register", "risicoregister", "risico"],
        ["deployment", "rollback", "uitrol", "terugval"],
        ["observability", "monitoring"],
        ["migration", "migratie", "runbook"],
        ["glossary", "woordenlijst", "begrippenlijst"],
        ["crosscutting concepts", "cross-cutting concepts", "crosscutting"],
        ["approvals", "goedkeuring", "sign-off"],
    ],
}

# Enterprise-required: choosing the enterprise scenario means opting into
# compliance rigour. Missing = ERROR. Note: we deliberately do NOT require
# per-framework headings (NEN 7510 / BIO / ISO 27001 / AI Act) — which
# frameworks apply is documented inside "Compliance evidence".
ENTERPRISE_REQUIRED = [
    ["dpia"],
    ["threat model", "dreigingsmodel", "stride"],
    ["compliance evidence", "compliance"],
    ["sbom"],
    ["non-functional requirements", "non-functionele requirements", "nfr"],
]

# Omissions convention: a section where dropped recommended sections are
# justified, and open doubts are recorded.
OMISSION_ALIASES = [
    "omitted sections",
    "omissions",
    "weggelaten secties",
    "open questions",
    "open punten",
]

# Size budgets (ceiling model). Exceeding = WARNING with trim/split advice.
SIZE_BUDGET_LINES = {
    "feature": 150,
    "project": 400,
    "enterprise": 800,  # per file when split into a bundle
}

# ---------------------------------------------------------------------------
# Content checks
# ---------------------------------------------------------------------------

# Placeholders: [word]-style gaps. We strip YAML frontmatter, fenced code
# blocks and inline code first (Mermaid diagrams and OKF frontmatter contain
# legitimate brackets). Markdown links [text](url), reference links [t][r]
# and task-list markers [ ]/[x] are excluded.
PLACEHOLDER_RE = re.compile(
    r"\[(?![ xX\-]?\])([a-z][a-z0-9/ .,'_-]{1,50}?)\](?![(\[:])",
    re.IGNORECASE,
)

# NFR measurability: requires a comparison operator with a number, a number
# with a real unit, or a 99.x availability figure. Deliberately does NOT
# match bare letters or the Dutch word "u" (you).
NFR_MEASURABLE_RE = re.compile(
    r"(?:<|>|≤|≥|<=|>=)\s*\d"
    r"|\b\d+(?:[.,]\d+)?\s*(?:%|ms|s|sec|seconden|min(?:uten)?|uren?|hours?|"
    r"rps|req/s|requests?|gebruikers|users|concurrent(?:e)?|mb|gb|tb)\b"
    r"|\b99[.,]\d",
    re.IGNORECASE,
)

# Privacy-by-design substance signals (beyond the bare personal-data mention).
PBD_SIGNALS = [
    "lawful basis", "grondslag", "retention", "bewaartermijn", "bewaarperiode",
    "dpia", "data inventory", "gegevensinventaris", "data-inventaris",
    "minimisation", "minimalisatie", "pseudonym", "anonimis",
    "data subject", "betrokkene", "verwerker", "no personal data",
    "geen persoonsgegevens",
]
PBD_JUSTIFICATION_MARKERS = [
    "because", "omdat", "daarom", "therefore", "reden", "justif", "aangezien",
]

# Security-by-design substance signals.
SBD_SIGNALS = [
    "authentication", "authenticatie", "authorization", "authorisation",
    "autorisatie", "authorisatie", "encrypt", "tls", "audit log", "auditlog",
    "asvs", "mfa", "threat", "dreiging", "least privilege", "secrets",
    "access control", "toegangscontrole", "oidc", "oauth",
]

# Minimum sane length for PbD/SbD — a tripwire against one-liners, not a
# volume incentive. Concise but complete sections pass.
MIN_SUBSTANCE_CHARS = 80

# EARS patterns for validation when EARS mode is detected.
EARS_PATTERNS = [
    re.compile(r"\bthe\s+\S+\s+shall\s+", re.IGNORECASE),  # Ubiquitous (EN)
    re.compile(r"\bwhile\s+.*?,?\s*the\s+\S+\s+shall\s+", re.IGNORECASE),
    re.compile(r"\bwhen\s+.*?,?\s*the\s+\S+\s+shall\s+", re.IGNORECASE),
    re.compile(r"\bwhere\s+.*?,?\s*the\s+\S+\s+shall\s+", re.IGNORECASE),
    re.compile(r"\bif\s+.*?,?\s*then\s+the\s+\S+\s+shall\s+", re.IGNORECASE),
    # Dutch EARS: "zal" as normative verb (per acceptance-criteria.md)
    re.compile(r"\bde\s+\S+\s+zal\s+", re.IGNORECASE),
    re.compile(r"\bhet\s+\S+\s+zal\s+", re.IGNORECASE),
    re.compile(r"\b(?:als|wanneer|terwijl|waar)\b.*?\bzal\s+", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        sys.exit(f"ERROR: file not found: {path}")
    return p.read_text(encoding="utf-8")


def normalize(text: str) -> str:
    return text.lower()


def strip_frontmatter(content: str) -> str:
    return re.sub(r"\A---\n.*?\n---\n", "", content, flags=re.DOTALL)


def strip_code(content: str) -> str:
    """Remove fenced code blocks and inline code (they contain legitimate
    brackets and keywords that confuse placeholder/content checks)."""
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    content = re.sub(r"`[^`\n]*`", "", content)
    return content


def find_headings(content: str) -> list[str]:
    """Return normalized heading texts (all levels)."""
    headings = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                headings.append(normalize(heading))
    return headings


def alias_matches(text: str, aliases: list[str]) -> bool:
    """Match aliases against text. Short aliases (<=4 chars) use word
    boundaries; longer aliases use substring matching."""
    for alias in aliases:
        if len(alias) <= 4:
            if re.search(r"\b" + re.escape(alias) + r"\b", text):
                return True
        elif alias in text:
            return True
    return False


def section_present(headings: list[str], aliases: list[str]) -> bool:
    joined = "\n".join(headings)
    return alias_matches(joined, aliases)


def extract_section(content: str, aliases) -> str:
    """Extract the body of a section given alias(es). Includes sub-headings."""
    if isinstance(aliases, str):
        aliases = [aliases]
    lines = content.splitlines()
    in_section = False
    section_level = 0
    body = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = normalize(stripped.lstrip("#").strip())
            if not in_section and alias_matches(heading, aliases):
                in_section = True
                section_level = level
                continue
            elif in_section and level <= section_level:
                break
        if in_section:
            body.append(line)
    return "\n".join(body)


def label(aliases: list[str]) -> str:
    return aliases[0]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_core(content: str, headings: list[str], audit: bool) -> list[str]:
    """Core sections are mandatory in every scenario. Missing = ERROR."""
    errors = []
    for aliases in CORE_SECTIONS:
        if not section_present(headings, aliases):
            errors.append(
                f"MISSING CORE SECTION: '{label(aliases)}' is mandatory in every "
                f"scenario (ceiling-model core) but was not found in headings."
            )
    return errors


def check_enterprise_required(headings: list[str], scenario: str, audit: bool) -> list[str]:
    """Enterprise-required sections. Missing = ERROR (enterprise = opting
    into compliance rigour)."""
    errors = []
    if scenario != "enterprise":
        return errors
    for aliases in ENTERPRISE_REQUIRED:
        if not section_present(headings, aliases):
            errors.append(
                f"MISSING ENTERPRISE-REQUIRED SECTION: '{label(aliases)}' is "
                f"mandatory for the enterprise scenario but was not found in headings."
            )
    return errors


def check_recommended(content: str, headings: list[str], scenario: str, audit: bool) -> tuple[list[str], list[str]]:
    """Recommended sections may be omitted WITH a recorded justification in
    the 'Omitted sections & open questions' section. Missing + unjustified =
    WARNING. Returns (warnings, infos)."""
    warnings: list[str] = []
    infos: list[str] = []
    omissions_text = normalize(
        extract_section(content, OMISSION_ALIASES) or ""
    )
    for aliases in RECOMMENDED_SECTIONS.get(scenario, []):
        if section_present(headings, aliases):
            continue
        if omissions_text and alias_matches(omissions_text, aliases):
            infos.append(
                f"omitted (justified): '{label(aliases)}' — justification recorded."
            )
            continue
        warnings.append(
            f"RECOMMENDED SECTION MISSING WITHOUT JUSTIFICATION: '{label(aliases)}' "
            f"is default-included for scenario '{scenario}'. Either include it, or "
            f"record the omission (with reason) in 'Omitted sections & open questions'."
        )
    return warnings, infos


def check_size_budget(content: str, scenario: str, max_lines: int | None) -> list[str]:
    """Ceiling model: warn when the document exceeds its size budget."""
    warnings = []
    budget = max_lines if max_lines is not None else SIZE_BUDGET_LINES.get(scenario)
    if budget is None:
        return warnings
    lines = len(content.splitlines())
    if lines > budget:
        warnings.append(
            f"SIZE BUDGET EXCEEDED: {lines} lines > {budget}-line budget for "
            f"scenario '{scenario}'. Ceiling model: trim sections that do not earn "
            f"their place, or split (enterprise -> multi-file bundle). "
            f"Override with --max-lines if this size is justified."
        )
    return warnings


def check_placeholders(content: str, audit: bool) -> list[str]:
    """Unfilled [placeholder] markers, ignoring frontmatter and code."""
    errors = []
    scannable = strip_code(strip_frontmatter(content))
    matches = PLACEHOLDER_RE.findall(scannable)
    # Filter out harmless one-letter anchors and pure numbers
    matches = [m for m in matches if len(m.strip()) > 1]
    if matches:
        sample = ", ".join(f"[{m}]" for m in matches[:5])
        errors.append(
            f"UNFILLED PLACEHOLDERS: found {len(matches)} placeholder(s), e.g. "
            f"{sample}. Replace all [placeholder] markers with concrete content."
        )
    return errors


def check_nfrs_measurable(content: str, scenario: str, audit: bool) -> list[str]:
    """An NFR section that is PRESENT must be measurable. (Absence is handled
    by core/recommended/enterprise logic — a missing NFR section is never an
    error here.)"""
    errors = []
    nfr_section = extract_section(
        content,
        ["non-functional requirements", "non-functionele requirements"],
    )
    if not nfr_section:
        return errors
    if not NFR_MEASURABLE_RE.search(nfr_section):
        errors.append(
            "NFR NOT MEASURABLE: the non-functional requirements section contains "
            "no measurable thresholds (no comparison + number, no number + unit). "
            "Every NFR must have a Metric + Threshold + Verification. "
            "'Should be fast' is not an NFR."
        )
    return errors


def check_pbd_populated(content: str, audit: bool) -> list[str]:
    """Privacy-by-design: always mandatory. Content-based check, not a volume
    floor — concise but complete sections pass."""
    errors = []
    pbd = extract_section(content, ["privacy-by-design", "privacy by design"])
    if not pbd:
        return errors  # absence is already a core error
    body = strip_code(normalize(pbd))
    if "persoonsgegevens" not in body and "personal data" not in body:
        errors.append(
            "PRIVACY-BY-DESIGN INCOMPLETE: the section does not state whether "
            "personal data is processed. State explicitly: yes/no WITH justification."
        )
    if len(body.strip()) < MIN_SUBSTANCE_CHARS:
        errors.append(
            "PRIVACY-BY-DESIGN TOO THIN: the section is a one-liner. State "
            "whether personal data is processed and justify the answer."
        )
    elif not any(s in body for s in PBD_SIGNALS) and not any(
        m in body for m in PBD_JUSTIFICATION_MARKERS
    ):
        errors.append(
            "PRIVACY-BY-DESIGN WITHOUT SUBSTANCE: no data handling signals "
            "(lawful basis / retention / DPIA / minimisation / no-personal-data "
            "statement) and no justification markers found."
        )
    return errors


def check_sbd_populated(content: str, audit: bool) -> list[str]:
    """Security-by-design: always mandatory. Content-based check."""
    errors = []
    sbd = extract_section(content, ["security-by-design", "security by design"])
    if not sbd:
        return errors  # absence is already a core error
    body = strip_code(normalize(sbd))
    if len(body.strip()) < MIN_SUBSTANCE_CHARS:
        errors.append(
            "SECURITY-BY-DESIGN TOO THIN: the section is a one-liner. Document "
            "at minimum authentication/authorization or justify minimal exposure."
        )
    elif not any(s in body for s in SBD_SIGNALS):
        errors.append(
            "SECURITY-BY-DESIGN WITHOUT SUBSTANCE: no security signals found "
            "(authentication / authorization / encryption / audit logging / ASVS). "
            "Even a minimal-exposure statement should name what is reused."
        )
    return errors


def check_traceability(content: str, scenario: str, audit: bool) -> list[str]:
    """If a traceability matrix is present, it must be populated."""
    errors = []
    tm = extract_section(content, ["traceability matrix", "traceerbaarheid"])
    if not tm:
        return errors  # absence handled by recommended logic
    if "US-" not in tm and "TC-" not in tm:
        errors.append(
            "TRACEABILITY MATRIX EMPTY: no user story IDs (US-) or test case IDs "
            "(TC-) found. Every requirement must map to a design component and test."
        )
    return errors


def check_toc(content: str, audit: bool) -> list[str]:
    """TOC present (heading-level) and accurate."""
    errors = []
    warnings = []
    headings = find_headings(content)
    toc_aliases = ["table of contents", "inhoudsopgave"]
    if not any(alias_matches(h, toc_aliases) for h in headings):
        errors.append("MISSING TABLE OF CONTENTS: a TOC heading is mandatory at the top.")
        return errors

    toc_section = extract_section(content, toc_aliases)
    if not toc_section:
        return errors

    toc_items = re.findall(r"^\s*\d+\.\s+(.+)$", toc_section, re.MULTILINE)
    if not toc_items:
        toc_items = re.findall(r"^\s*\d+\s+(.+)$", toc_section, re.MULTILINE)
    if not toc_items:
        return errors

    heading_texts = [
        h for h in headings
        if not alias_matches(h, toc_aliases)
    ]
    toc_items_norm = [normalize(item.strip()) for item in toc_items]
    mismatches = [
        item for item in toc_items_norm
        if not any(item in ht or ht in item for ht in heading_texts)
    ]
    if mismatches:
        warnings.append(
            f"TOC INACCURATE: {len(mismatches)} TOC item(s) do not match any "
            f"heading: {', '.join(mismatches[:5])}"
            f"{'...' if len(mismatches) > 5 else ''}"
        )
    return errors + warnings


def check_diagrams(content: str, headings: list[str], audit: bool) -> list[str]:
    """If an architecture section exists, it should contain at least one
    Mermaid diagram. Absence of the architecture section itself is handled by
    recommended/core logic."""
    warnings = []
    has_arch = section_present(headings, ["architecture", "architectuur"])
    if has_arch and "```mermaid" not in content:
        warnings.append(
            "ARCHITECTURE WITHOUT DIAGRAMS: an architecture section is present "
            "but contains no Mermaid diagram (C4 Context is the default notation)."
        )
    return warnings


def check_ears_format(content: str, audit: bool) -> list[str]:
    """When EARS mode is detected, acceptance criteria must match EARS
    patterns (EN 'shall' or NL 'zal')."""
    errors = []
    ac_section = extract_section(
        content, ["acceptance criteria", "acceptatiecriteria"]
    )
    if not ac_section:
        return errors

    ears_indicated = (
        "ears" in normalize(ac_section[:200])
        or "<!-- ac-format: ears -->" in normalize(content)
        or "acceptance criteria format: ears" in normalize(content)
    )
    if not ears_indicated:
        return errors

    criteria_lines = [
        line.strip().lstrip("-").strip()
        for line in ac_section.splitlines()
        if line.strip().startswith("-") and line.strip().lstrip("-").strip()
    ]
    if not criteria_lines:
        return errors

    non_ears_lines = []
    for line in criteria_lines:
        if not any(pattern.search(line) for pattern in EARS_PATTERNS):
            if not line.startswith("#") and not line.startswith("**") and len(line) > 10:
                non_ears_lines.append(line)

    if non_ears_lines:
        errors.append(
            f"EARS FORMAT VIOLATION: {len(non_ears_lines)} acceptance "
            f"criterion/criteria do not match EARS patterns (Ubiquitous/State-driven/"
            f"Event-driven/Optional/Unwanted; EN 'shall' or NL 'zal'). "
            f"First: '{non_ears_lines[0][:80]}...'"
        )
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate(path: str, scenario: str, audit: bool = False, max_lines: int | None = None) -> int:
    content = read_file(path)
    headings = find_headings(content)
    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []

    errors.extend(check_core(content, headings, audit))
    errors.extend(check_enterprise_required(headings, scenario, audit))
    rec_warnings, rec_infos = check_recommended(content, headings, scenario, audit)
    warnings.extend(rec_warnings)
    infos.extend(rec_infos)
    warnings.extend(check_size_budget(content, scenario, max_lines))
    errors.extend(check_placeholders(content, audit))
    errors.extend(check_nfrs_measurable(content, scenario, audit))
    errors.extend(check_pbd_populated(content, audit))
    errors.extend(check_sbd_populated(content, audit))
    errors.extend(check_traceability(content, scenario, audit))
    toc_issues = check_toc(content, audit)
    errors.extend([e for e in toc_issues if e.startswith("MISSING")])
    warnings.extend([e for e in toc_issues if e.startswith("TOC")])
    warnings.extend(check_diagrams(content, headings, audit))
    errors.extend(check_ears_format(content, audit))

    if audit:
        print("=== AUDIT REPORT ===")
        print(f"Source: {path}")
        print(f"Scenario: {scenario}")
        print(f"Headings found: {len(headings)}")
        print(f"Size: {len(content.splitlines())} lines "
              f"(budget: {max_lines or SIZE_BUDGET_LINES.get(scenario)})")
        print("-" * 60)
        print()
        print("### Summary")
        print(f"- Critical findings (errors): {len(errors)}")
        print(f"- Important findings (warnings): {len(warnings)}")
        print(f"- Justified omissions: {len(infos)}")
        overall = (
            "PASS" if not errors and not warnings
            else "NEEDS IMPROVEMENT" if not errors
            else "FAIL"
        )
        print(f"- Overall verdict: {overall}")
        print()

        if errors:
            print("### Critical (core/enterprise-required missing, or broken content)")
            for i, e in enumerate(errors, 1):
                print(f"  {i}. {e}")
            print()
        if warnings:
            print("### Important (unjustified omissions, budget, polish)")
            for i, w in enumerate(warnings, 1):
                print(f"  {i}. {w}")
            print()
        if infos:
            print("### Justified omissions (recorded in 'Omitted sections')")
            for i, info in enumerate(infos, 1):
                print(f"  {i}. {info}")
            print()

        print("### Next steps")
        print("1. Address all Critical findings.")
        print("2. Address Important findings — include the section or record a justified omission.")
        print("3. Re-run: python scripts/validate.py", path, "--scenario", scenario)
        return 2 if errors else 0

    # Non-audit mode
    print(f"Validating: {path}")
    print(f"Scenario:   {scenario} (ceiling model: core enforced, recommended justified-or-warned)")
    print(f"Headings:   {len(headings)} found | Size: {len(content.splitlines())} lines "
          f"(budget: {max_lines or SIZE_BUDGET_LINES.get(scenario)})")
    print("-" * 60)

    for i, e in enumerate(errors, 1):
        print(f"  ERROR {i}. {e}")
    for i, w in enumerate(warnings, 1):
        print(f"  WARNING {i}. {w}")
    for info in infos:
        print(f"  info: {info}")

    if not errors and not warnings:
        print("PASS — core complete, all recommended sections present or justified.")
        return 0
    if not errors:
        print(f"\nPASS WITH WARNINGS — {len(warnings)} warning(s). "
              f"Fix or justify via 'Omitted sections & open questions'.")
        return 0
    print(f"\nFAIL — {len(errors)} error(s), {len(warnings)} warning(s).")
    print("Note: the validator is advisory. If a check appears wrong for a "
          "legitimate document, report it to the user instead of padding the document.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an FTD Markdown file against the ceiling-model "
                    "core and scenario recommendations."
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
        help="Produce a gap report (critical/important/justified) instead of "
             "pass/fail. For reviewing existing documents.",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=None,
        help="Override the scenario size budget (ceiling-model warning).",
    )
    args = parser.parse_args()
    return validate(args.file, args.scenario, args.audit, args.max_lines)


if __name__ == "__main__":
    sys.exit(main())
