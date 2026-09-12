#!/usr/bin/env python3
"""Validate and manage Keep a Changelog 2.0.0 files.

Two artifacts share one format:
  CHANGELOG.md      the internal, complete record (English only, always present)
  RELEASE_NOTES.md  user-facing release notes (English or Dutch, optional;
                    released versions only, never an Unreleased section)

Subcommands:
  validate <CHANGELOG.md> [RELEASE_NOTES.md]
      Errors report format violations; warnings report best practices.
      With RELEASE_NOTES.md: structural checks plus parity with CHANGELOG.md.
  extract <file> (<version> | --unreleased) [--output FILE]
      Print one release section verbatim, heading included.
  release <CHANGELOG.md> <version> [--date YYYY-MM-DD]
      Cut [Unreleased] into a dated version: rename the heading, insert a
      fresh empty [Unreleased] at the top, and update the link reference
      definitions. Refuses to run on a changelog with validation errors.
  list <file>
      Table of versions with dates and entry counts per change type.

Exit codes:
  0  success (warnings allowed)
  1  validation errors, or the operation could not complete
  2  usage error (bad arguments, unreadable file)

Standard library only; Python 3.9+.
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

EN_TYPES = ("Added", "Changed", "Deprecated", "Removed", "Fixed", "Security")
NL_TYPES = ("Nieuw", "Gewijzigd", "Verouderd", "Verwijderd", "Gefixt", "Beveiliging")
NL_TO_EN = {
    "Nieuw": "Added",
    "Gewijzigd": "Changed",
    "Verouderd": "Deprecated",
    "Verwijderd": "Removed",
    "Gefixt": "Fixed",
    "Beveiliging": "Security",
}

# A sub-bullet is indented by at least this many spaces (or a tab).
SUB_BULLET_INDENT = 2

H1_RE = re.compile(r"^# (.+?)\s*$")
H2_RE = re.compile(r"^## (.+?)\s*$")
H3_RE = re.compile(r"^### (.+?)\s*$")
HEADING_ANY_RE = re.compile(r"^#{1,6} ")
VERSION_HEADING_RE = re.compile(
    r"^## \[(?P<label>[^\]]+)\]"
    r"(?: - (?P<date>\d{4}-\d{2}-\d{2}))?"
    r"(?: \[(?P<yanked>YANKED)\])?"
    r"\s*$"
)
LINK_DEF_RE = re.compile(r"^\[(?P<label>[^\]]+)\]:\s*(?P<url>\S+)\s*$")
BULLET_RE = re.compile(r"^(?P<indent>\s*)[-*] (?P<text>.*)$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
PINNED_KAC_RE = re.compile(r"keepachangelog\.com/en/\d+\.\d+\.\d+/")
KAC_RE = re.compile(r"keepachangelog\.com")
VERSIONING_RE = re.compile(r"semver\.org|calver\.org|versioning", re.IGNORECASE)
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_LABEL_RE = re.compile(r"^[\w.+-]+$")
# Compare URL like https://github.com/org/repo/compare/v1.0.0...HEAD
COMPARE_RE = re.compile(r"^(?P<base>.*/compare/)(?P<a>v?[\w.+-]+?)\.\.\.(?P<b>v?[\w.+-]+)$")
TAG_RE = re.compile(r"^(?P<base>.*/)releases/tag/(?P<tag>v?[\w.+-]+)$")

TODAY = datetime.date.today()


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

class Release:
    """One `## [label] [- date] [[YANKED]]` section."""

    def __init__(self, label, date, yanked, line):
        self.label = label
        self.date = date
        self.yanked = yanked
        self.line = line  # 1-based line number of the heading
        self.events = []  # tuples (kind, line, level, payload) in document order

    @property
    def is_unreleased(self):
        return self.label is not None and self.label.lower() == "unreleased"

    def bullets(self):
        """All bullet events, top-level and sub-bullets alike."""
        return [e for e in self.events if e[0] == "bullet"]

    def summary_lines(self):
        """Prose directly under the version heading (before the first H3)."""
        out = []
        for kind, _line, _level, payload in self.events:
            if kind == "type":
                break
            if kind == "prose":
                out.append(payload)
        return out


class Doc:
    """Parsed changelog / release notes file."""

    def __init__(self, path):
        self.path = path
        self.filename = Path(path).name
        self.h1 = None
        self.h1_line = 0
        self.releases = []
        self.invalid_h2 = []  # (1-based line, raw heading text)
        self.link_defs = {}   # label -> (url, 1-based line)
        self.preamble = []    # (line, text) between H1 and the first release heading
        self.raw_text = ""
        self.crlf = False

    def released_versions(self):
        return [r for r in self.releases if not r.is_unreleased]

    def find(self, label):
        """Exact-label lookup; for 'unreleased' any casing matches."""
        if label.lower() == "unreleased":
            return next((r for r in self.releases if r.is_unreleased), None)
        for r in self.releases:
            if r.label == label:
                return r
        return None


def detect_kind(path):
    """RELEASE_NOTES* files are user-facing notes; everything else is a changelog."""
    name = Path(path).name.upper()
    return "notes" if name.startswith("RELEASE_NOTES") else "changelog"


def read_text(path):
    """Read a UTF-8 file (BOM-tolerant, newline-preserving) or exit 2."""
    try:
        # newline="" keeps \r\n intact so the file's newline style survives a
        # read-modify-write cycle; utf-8-sig strips a leading BOM if present.
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            return f.read()
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(2)


def parse_markdown(path):
    """Lenient line-based parser. Structural problems are collected, not raised."""
    text = read_text(path)
    doc = Doc(path)
    doc.raw_text = text
    doc.crlf = "\r\n" in text

    # Split on "\n" only (splitlines() would also break on \x0b, \u2028, ...),
    # then drop a trailing "\r" so CRLF files parse like LF files.
    lines = [l.rstrip("\r") for l in text.split("\n")]

    in_fence = False
    current_release = None
    seen_h1 = False

    for i, line in enumerate(lines, start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue

        if in_fence:
            if current_release is not None:
                current_release.events.append(("content", i, 0, line.strip()))
            elif seen_h1 and line.strip():
                doc.preamble.append((i, line.strip()))
            continue

        # Link reference definitions belong to no release section.
        lm = LINK_DEF_RE.match(line)
        if lm:
            doc.link_defs[lm.group("label")] = (lm.group("url"), i)
            current_release = None
            continue

        m = H1_RE.match(line)
        if m and not seen_h1:
            doc.h1 = m.group(1)
            doc.h1_line = i
            seen_h1 = True
            continue

        if line.startswith("## "):
            vm = VERSION_HEADING_RE.match(line)
            if vm:
                current_release = Release(
                    vm.group("label"),
                    vm.group("date"),
                    bool(vm.group("yanked")),
                    i,
                )
                doc.releases.append(current_release)
            else:
                doc.invalid_h2.append((i, line))
                # Contain the invalid section's content so it does not pollute
                # the preamble; validation reports the heading error itself.
                current_release = Release(None, None, False, i)
            continue

        if current_release is None:
            if seen_h1 and line.strip():
                doc.preamble.append((i, line.strip()))
            continue

        if line.startswith("### "):
            hm = H3_RE.match(line)
            current_release.events.append(("type", i, 0, hm.group(1) if hm else ""))
            continue

        if HEADING_ANY_RE.match(line):
            current_release.events.append(("deepheading", i, 0, line))
            continue

        if not line.strip():
            continue

        bm = BULLET_RE.match(line)
        if bm:
            indent = bm.group("indent")
            level = 0 if len(indent.replace("\t", "  ")) < SUB_BULLET_INDENT else 1
            current_release.events.append(("bullet", i, level, bm.group("text")))
            continue

        # An indented non-bullet line continues the previous bullet (entries
        # wrap over multiple lines). Indented prose with no bullet above it
        # stays prose so the non-bullet warning still fires.
        if line[:1] in (" ", "\t") and current_release.events and \
                current_release.events[-1][0] in ("bullet", "continuation"):
            current_release.events.append(("continuation", i, 0, line.strip()))
            continue

        current_release.events.append(("prose", i, 0, line.strip()))

    return doc


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def valid_iso_date(date_str):
    if not ISO_DATE_RE.match(date_str or ""):
        return False
    try:
        datetime.date.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def version_key(label):
    """Sort key for version labels; SemVer-aware (pre-releases sort first)."""
    core = label.partition("+")[0]          # build metadata never affects order
    core, _, pre = core.partition("-")     # pre-release sorts before release
    key = []
    for part in re.split(r"[.]", core):
        key.append((0, int(part), "") if part.isdigit() else (1, 0, part))
    if pre:
        key.append((0, -1, pre))
    else:
        key.append((0, 0, ""))
    return tuple(key)


def match_compare(url):
    """Match a compare URL; exactly one '...' separator is allowed."""
    if url.count("...") != 1:
        return None
    return COMPARE_RE.match(url)


def type_sections(release):
    """Group release events into type sections.

    Returns (sections, outside_bullets) where each section is
    {"name", "line", "bullets": [(line, level)], "prose": [(line, text)]}
    and outside_bullets are bullets found before any type heading.
    """
    sections = []
    current = None
    outside_bullets = []
    for kind, line, level, payload in release.events:
        if kind == "type":
            current = {"name": payload, "line": line, "bullets": [], "prose": []}
            sections.append(current)
        elif kind == "bullet":
            if current is None:
                outside_bullets.append((line, level))
            else:
                current["bullets"].append((line, level))
        elif kind == "prose":
            if current is not None:
                current["prose"].append((line, payload))
    return sections, outside_bullets


def check_common_structure(doc, issues, allowed_types, is_notes):
    """Structural checks shared by changelog and release notes files."""
    fname = doc.filename

    if doc.h1 is None:
        issues.append(("error", 0, f"{fname}: missing H1 heading ('# Changelog' expected)"))
    elif doc.h1 != "Changelog" and not is_notes:
        issues.append(("warning", doc.h1_line, f"{fname}: H1 is '{doc.h1}' — use '# Changelog'"))

    for line, raw in doc.invalid_h2:
        issues.append((
            "error", line,
            f"{fname}: invalid version heading '{raw}' — "
            f"expected '## [x.y.z] - YYYY-MM-DD' or '## [Unreleased]'",
        ))

    seen_labels = {}
    for rel in doc.releases:
        if rel.is_unreleased and rel.date:
            issues.append(("error", rel.line, f"{fname}: [Unreleased] must not carry a date"))
        if not rel.is_unreleased and not rel.date:
            issues.append((
                "error", rel.line,
                f"{fname}: version [{rel.label}] has no release date — "
                f"expected '## [{rel.label}] - YYYY-MM-DD'",
            ))
        if rel.date and not valid_iso_date(rel.date):
            issues.append((
                "error", rel.line,
                f"{fname}: invalid date '{rel.date}' — use ISO 8601 (YYYY-MM-DD)",
            ))
        if rel.label.lower() in seen_labels:
            issues.append((
                "error", rel.line,
                f"{fname}: duplicate version [{rel.label}] — "
                f"first defined at line {seen_labels[rel.label.lower()]}",
            ))
        else:
            seen_labels[rel.label.lower()] = rel.line
        if rel.date and valid_iso_date(rel.date) and datetime.date.fromisoformat(rel.date) > TODAY:
            issues.append((
                "warning", rel.line,
                f"{fname}: release date {rel.date} of [{rel.label}] is in the future",
            ))

        if is_notes and rel.is_unreleased:
            issues.append((
                "error", rel.line,
                f"{fname}: [Unreleased] is not allowed here — "
                f"RELEASE_NOTES.md lists released versions only",
            ))

        sections, outside = type_sections(rel)
        for line, _level in outside:
            issues.append((
                "error", line,
                f"{fname}: entry outside a type section — "
                f"move it under an '### Added/Changed/...' heading",
            ))
        for kind, line, _level, payload in rel.events:
            if kind == "deepheading":
                issues.append((
                    "warning", line,
                    f"{fname}: unexpected heading level '{payload}' — the format uses ## and ### only",
                ))

        total_bullets = len(rel.bullets())
        has_summary = bool(rel.summary_lines())
        for sec in sections:
            if sec["name"] not in allowed_types:
                if is_notes:
                    issues.append((
                        "error", sec["line"],
                        f"{fname}: unknown change type '### {sec['name']}' — use an English type "
                        f"({', '.join(EN_TYPES)}) or a Dutch type ({', '.join(NL_TYPES)})",
                    ))
                elif sec["name"] in NL_TYPES:
                    issues.append((
                        "error", sec["line"],
                        f"{fname}: Dutch type '### {sec['name']}' — CHANGELOG.md entries must be "
                        f"English (use '### {NL_TO_EN[sec['name']]}')",
                    ))
                else:
                    issues.append((
                        "error", sec["line"],
                        f"{fname}: unknown change type '### {sec['name']}' — use one of: "
                        f"{', '.join(EN_TYPES)}",
                    ))
            if not sec["bullets"]:
                advice = ("keep the fresh [Unreleased] section clean"
                          if rel.is_unreleased else "remove sections without entries")
                issues.append(("warning" if rel.is_unreleased else "error", sec["line"],
                               f"{fname}: empty section '### {sec['name']}' — {advice}"))
            for line, _text in sec["prose"]:
                issues.append((
                    "warning", line,
                    f"{fname}: content under '### {sec['name']}' is not a bullet entry",
                ))

        if not rel.is_unreleased and total_bullets == 0 and not has_summary:
            # A version with no entries at all. A one-sentence summary makes
            # this legitimate (reconstructed history, minimal releases);
            # summary-only versions pass without warnings.
            if is_notes:
                issues.append((
                    "warning", rel.line,
                    f"{fname}: empty release [{rel.label}] — write the user-facing notes "
                    f"or remove the section",
                ))
            else:
                issues.append((
                    "warning", rel.line,
                    f"{fname}: release [{rel.label}] has no entries — add the notable changes "
                    f"or a one-sentence summary",
                ))

    if any(r.is_unreleased for r in doc.releases) and not doc.releases[0].is_unreleased:
        unrel = next(r for r in doc.releases if r.is_unreleased)
        issues.append(("warning", unrel.line, f"{fname}: [Unreleased] should be the first section"))

    released = doc.released_versions()
    for prev, nxt in zip(released, released[1:]):
        if version_key(prev.label) < version_key(nxt.label):
            issues.append((
                "warning", nxt.line,
                f"{fname}: [{nxt.label}] should be listed before [{prev.label}] — newest release first",
            ))

    return seen_labels


def detect_notes_language(doc):
    """Returns ('en' | 'nl' | 'mixed' | None, [type names used])."""
    names = []
    for rel in doc.releases:
        for kind, _line, _level, payload in rel.events:
            if kind == "type":
                names.append(payload)
    en = {n for n in names if n in EN_TYPES}
    nl = {n for n in names if n in NL_TYPES}
    if en and nl:
        return "mixed", sorted(en | nl)
    if en:
        return "en", sorted(en)
    if nl:
        return "nl", sorted(nl)
    return None, []


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_changelog(doc):
    issues = []
    fname = doc.filename

    seen_labels = check_common_structure(doc, issues, EN_TYPES, is_notes=False)

    # Preamble best practices (warnings)
    preamble_text = "\n".join(t for _l, t in doc.preamble)
    if "all notable changes" not in preamble_text.lower():
        issues.append((
            "warning", 0,
            f"{fname}: missing standard preamble sentence ('All notable changes ...')",
        ))
    if not KAC_RE.search(preamble_text):
        issues.append((
            "warning", 0,
            f"{fname}: preamble does not mention Keep a Changelog — pin the version, "
            f"e.g. https://keepachangelog.com/en/2.0.0/",
        ))
    elif not PINNED_KAC_RE.search(preamble_text):
        issues.append((
            "warning", 0,
            f"{fname}: pin the Keep a Changelog link to a specific version "
            f"(e.g. https://keepachangelog.com/en/2.0.0/)",
        ))
    if not VERSIONING_RE.search(preamble_text):
        issues.append((
            "warning", 0,
            f"{fname}: preamble does not state the versioning scheme (e.g. Semantic Versioning)",
        ))

    # Link reference definitions (warnings)
    link_labels_lower = {k.lower() for k in doc.link_defs}
    for rel in doc.releases:
        if seen_labels.get(rel.label.lower()) != rel.line:
            continue  # later occurrence of a duplicate label; report once
        if rel.label.lower() not in link_labels_lower:
            issues.append((
                "warning", rel.line,
                f"{fname}: missing link reference definition for [{rel.label}] — "
                f"add '[{rel.label}]: <compare url>' at the bottom of the file",
            ))
    for label, (_url, line) in doc.link_defs.items():
        if label.lower() not in seen_labels:
            issues.append((
                "warning", line,
                f"{fname}: link definition [{label}] matches no version in the file",
            ))

    return issues


def validate_notes(doc, changelog_doc=None):
    issues = []
    fname = doc.filename

    check_common_structure(doc, issues, EN_TYPES + NL_TYPES, is_notes=True)

    # One language per file (warning on mixing)
    language, used = detect_notes_language(doc)
    if language == "mixed":
        issues.append((
            "warning", 0,
            f"{fname}: mixed languages ({', '.join(used)}) — keep one language per file",
        ))

    if changelog_doc is None:
        issues.append((
            "warning", 0,
            f"{fname}: parity with CHANGELOG.md not checked — "
            f"pass the changelog as the first argument",
        ))
        return issues

    # Parity with CHANGELOG.md
    ch_versions = {r.label: r for r in changelog_doc.released_versions()}
    notes_versions = {r.label: r for r in doc.released_versions()}
    for label, rel in notes_versions.items():
        if label not in ch_versions:
            issues.append((
                "error", rel.line,
                f"{fname}: version [{label}] is not in {changelog_doc.filename}",
            ))
        elif ch_versions[label].date != rel.date:
            issues.append((
                "error", rel.line,
                f"{fname}: date mismatch for [{label}] — "
                f"{changelog_doc.filename} says {ch_versions[label].date}",
            ))
    for label, rel in ch_versions.items():
        if label not in notes_versions:
            # Located in the changelog (that is where the missing entry pairs).
            issues.append((
                "warning", rel.line,
                f"{changelog_doc.filename}: release [{label}] has no release notes yet",
            ))

    return issues


def report(issues, label):
    """Print issues as '<file>:<line>: <level>: <message>'; return the error count."""
    errors = [i for i in issues if i[0] == "error"]
    warnings = [i for i in issues if i[0] == "warning"]
    for level, line, message in issues:
        fname, sep, body = message.partition(":")
        if not sep:
            fname, body = label, message
        loc = f"{fname}:{line}" if line else fname
        print(f"{loc}: {level}: {body.strip()}")
    plural_e = "s" if len(errors) != 1 else ""
    plural_w = "s" if len(warnings) != 1 else ""
    print(f"{label}: {len(errors)} error{plural_e}, {len(warnings)} warning{plural_w}")
    return len(errors)


def cmd_validate(args):
    first_doc = parse_markdown(args.changelog)
    if detect_kind(args.changelog) == "notes":
        if args.notes:
            print("error: RELEASE_NOTES.md as the first argument expects no second file",
                  file=sys.stderr)
            sys.exit(2)
        all_errors = report(validate_notes(first_doc), first_doc.filename)
        sys.exit(1 if all_errors else 0)

    if args.notes and detect_kind(args.notes) != "notes":
        print("error: the second argument must be a RELEASE_NOTES*.md file", file=sys.stderr)
        sys.exit(2)

    all_errors = report(validate_changelog(first_doc), first_doc.filename)
    if args.notes:
        notes_doc = parse_markdown(args.notes)
        all_errors += report(validate_notes(notes_doc, first_doc), notes_doc.filename)

    sys.exit(1 if all_errors else 0)


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------

def cmd_extract(args):
    if bool(args.version) == bool(args.unreleased):
        print("error: give exactly one of <version> or --unreleased", file=sys.stderr)
        sys.exit(2)

    doc = parse_markdown(args.file)
    label = "Unreleased" if args.unreleased else args.version
    rel = doc.find(label)
    if rel is None:
        available = [r.label for r in doc.releases] or ["(none)"]
        print(
            f"error: [{label}] not found in {doc.filename}. Available: {', '.join(available)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Raw lines so the output is verbatim (CRLF content included).
    lines = doc.raw_text.split("\n")

    # The section ends at the next H2 heading, the first link definition, or
    # EOF — ignoring anything inside fenced code blocks.
    end = len(lines)
    fence = False
    for i in range(rel.line, len(lines)):  # 0-based index i == 1-based line i+1
        line = lines[i]
        if FENCE_RE.match(line):
            fence = not fence
            continue
        if fence:
            continue
        if H2_RE.match(line) or LINK_DEF_RE.match(line):
            end = i
            break
    while end > rel.line and not lines[end - 1].strip():
        end -= 1

    section = "\n".join(lines[rel.line - 1:end]) + "\n"
    if args.output:
        Path(args.output).write_text(section, encoding="utf-8")
        print(f"Extracted [{label}] to {args.output}")
    else:
        sys.stdout.write(section)


# ---------------------------------------------------------------------------
# Release (cut Unreleased into a dated version)
# ---------------------------------------------------------------------------

def derive_url_token(doc, version):
    """How this project writes versions in URLs (with or without a 'v' prefix)."""
    for url, _line in doc.link_defs.values():
        m = match_compare(url)
        if m:
            return "v" + version if m.group("a").startswith("v") else version
        m = TAG_RE.match(url)
        if m:
            return "v" + version if m.group("tag").startswith("v") else version
    return version


def write_atomic(path, content):
    """Write via a temp file + rename so a crash never truncates the target."""
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def cmd_release(args):
    if detect_kind(args.changelog) == "notes":
        print("error: release operates on CHANGELOG.md, not on release notes", file=sys.stderr)
        sys.exit(2)
    if args.version.lower() == "unreleased":
        print("error: the new version cannot be 'Unreleased'", file=sys.stderr)
        sys.exit(1)
    if not VERSION_LABEL_RE.match(args.version):
        print(f"error: invalid version label '{args.version}'", file=sys.stderr)
        sys.exit(2)
    if not valid_iso_date(args.date):
        print(f"error: invalid date '{args.date}' — use ISO 8601 (YYYY-MM-DD)", file=sys.stderr)
        sys.exit(2)

    doc = parse_markdown(args.changelog)
    issues = validate_changelog(doc)
    if any(i[0] == "error" for i in issues):
        report(issues, doc.filename)
        print("error: fix the validation errors before cutting a release", file=sys.stderr)
        sys.exit(1)

    unreleased = next((r for r in doc.releases if r.is_unreleased), None)
    if unreleased is None:
        print(f"error: no [Unreleased] section in {doc.filename} — nothing to cut", file=sys.stderr)
        sys.exit(1)
    if doc.find(args.version) is not None:
        print(f"error: version [{args.version}] already exists in {doc.filename}", file=sys.stderr)
        sys.exit(1)
    if not unreleased.bullets():
        print("error: [Unreleased] is empty — nothing to release", file=sys.stderr)
        sys.exit(1)

    # --- Derive the new link definitions -------------------------------
    token = derive_url_token(doc, args.version)
    unreleased_url = None
    version_url = None
    unrel_def = doc.link_defs.get("Unreleased")
    if unrel_def and match_compare(unrel_def[0]):
        # [Unreleased]: <base><prev-version>...HEAD
        m = match_compare(unrel_def[0])
        version_url = f"{m.group('base')}{m.group('a')}...{token}"
        unreleased_url = f"{m.group('base')}{token}...HEAD"
    else:
        # Derive from the newest released version's definition.
        latest_url, latest_line = None, None
        for rel in doc.released_versions():
            if rel.label in doc.link_defs:
                latest_url, latest_line = doc.link_defs[rel.label]
        if latest_url and match_compare(latest_url):
            m = match_compare(latest_url)
            unreleased_url = f"{m.group('base')}{token}...HEAD"
            version_url = f"{m.group('base')}{m.group('b')}...{token}"
        elif latest_url and TAG_RE.match(latest_url):
            m = TAG_RE.match(latest_url)
            unreleased_url = f"{m.group('base')}compare/{token}...HEAD"
            version_url = f"{m.group('base')}compare/{m.group('tag')}...{token}"
        elif unrel_def or latest_url:
            print(
                "warning: could not derive new link definitions from the existing URL "
                f"pattern — add compare links for [{args.version}] and [Unreleased] manually",
                file=sys.stderr,
            )
        else:
            print(
                "warning: no link reference definitions found — add compare links for "
                f"[{args.version}] and [Unreleased] manually",
                file=sys.stderr,
            )

    # --- Line surgery ----------------------------------------------------
    # All indices are 0-based and refer to the ORIGINAL file. Apply the edit
    # furthest down first so indices above it stay valid, whichever side of
    # the [Unreleased] heading the definitions live on.
    lines = [l.rstrip("\r") for l in doc.raw_text.split("\n")]
    idx = unreleased.line - 1

    def_edits = []  # (action, 0-based index, content)
    if unreleased_url and version_url:
        if unrel_def:
            def_line = unrel_def[1] - 1
            def_edits = [("replace", def_line, f"[Unreleased]: {unreleased_url}"),
                         ("insert", def_line + 1, f"[{args.version}]: {version_url}")]
        else:
            # No [Unreleased] definition existed; insert the pair above the
            # newest released version's definition.
            anchor = None
            for rel in doc.released_versions():
                if rel.label in doc.link_defs:
                    anchor = doc.link_defs[rel.label][1] - 1
            if anchor is None:
                anchor = len(lines)  # append at the end (no defs exist)
                if lines and lines[-1].strip() == "":
                    anchor -= 1
            def_edits = [("insert", anchor, f"[Unreleased]: {unreleased_url}"),
                         ("insert", anchor + 1, f"[{args.version}]: {version_url}")]

    # Heading edits: rename (no size change) + insert a fresh [Unreleased].
    if def_edits and min(e[1] for e in def_edits) > idx:
        # Definitions sit below the heading: apply def edits first.
        for action, pos, content in def_edits:
            if action == "replace":
                lines[pos] = content
            else:
                lines.insert(pos, content)
        lines[idx] = f"## [{args.version}] - {args.date}"
        lines.insert(idx, "")
        lines.insert(idx, "## [Unreleased]")
    else:
        lines[idx] = f"## [{args.version}] - {args.date}"
        lines.insert(idx, "")
        lines.insert(idx, "## [Unreleased]")
        for action, pos, content in def_edits:
            if action == "replace":
                lines[pos] = content
            else:
                lines.insert(pos, content)

    content = "\n".join(lines)
    if not content.endswith("\n"):
        content += "\n"
    if doc.crlf:
        content = content.replace("\n", "\r\n")
    write_atomic(args.changelog, content)

    print(f"Cut [{args.version}] - {args.date} in {doc.filename}:")
    print(f"  - renamed [Unreleased] heading (was line {unreleased.line})")
    print("  - inserted a fresh empty [Unreleased] section at the top")
    if def_edits:
        print("  - updated the link reference definitions")

    # Post-cut sanity check: the mutated file must still validate.
    fresh_doc = parse_markdown(args.changelog)
    fresh_issues = validate_changelog(fresh_doc)
    if any(i[0] == "error" for i in fresh_issues):
        report(fresh_issues, fresh_doc.filename)
        print("error: the cut introduced validation errors — please review the file",
              file=sys.stderr)
        sys.exit(1)

    # Release notes reminder (parity with existing RELEASE_NOTES*.md files).
    notes_files = sorted(Path(args.changelog).parent.glob("RELEASE_NOTES*.md"))
    if notes_files:
        for notes_file in notes_files:
            notes_doc = parse_markdown(notes_file)
            if notes_doc.find(args.version) is None:
                print(f"reminder: {notes_file.name} has no entry for [{args.version}] yet")
    else:
        print("note: no RELEASE_NOTES*.md found next to the changelog (it is optional)")


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def cmd_list(args):
    doc = parse_markdown(args.file)
    if not doc.releases:
        print(f"No release sections found in {doc.filename}.")
        return

    rows = []
    for rel in doc.releases:
        counts = {}
        sections, _outside = type_sections(rel)
        for sec in sections:
            top = sum(1 for _l, level in sec["bullets"] if level == 0)
            if top:
                counts[sec["name"]] = top
        detail = ", ".join(f"{name} {n}" for name, n in counts.items()) or "no entries"
        yanked = " [YANKED]" if rel.yanked else ""
        rows.append((rel.label + yanked, rel.date or "-", detail))

    w_version = max(len(r[0]) for r in rows)
    w_date = max(len(r[1]) for r in rows)
    print(f"{'VERSION':<{w_version}}  {'DATE':<{w_date}}  ENTRIES")
    for label, date, detail in rows:
        print(f"{label:<{w_version}}  {date:<{w_date}}  {detail}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def today_str():
    return TODAY.isoformat()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="changelog.py",
        description="Validate and manage Keep a Changelog 2.0.0 files.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="validate CHANGELOG.md (and optional RELEASE_NOTES.md)")
    p.add_argument("changelog", help="path to CHANGELOG.md")
    p.add_argument("notes", nargs="?", default=None, help="optional path to RELEASE_NOTES.md")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("extract", help="print one release section verbatim")
    p.add_argument("file", help="path to CHANGELOG.md or RELEASE_NOTES.md")
    p.add_argument("version", nargs="?", default=None, help="version label, e.g. 1.2.3")
    p.add_argument("-u", "--unreleased", action="store_true",
                   help="extract the [Unreleased] section")
    p.add_argument("-o", "--output", default=None,
                   help="write the section to this file instead of stdout")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("release", help="cut [Unreleased] into a dated version")
    p.add_argument("changelog", help="path to CHANGELOG.md")
    p.add_argument("version", help="new version label, e.g. 1.2.3")
    p.add_argument("--date", default=today_str(), help="release date, ISO 8601 (default: today)")
    p.set_defaults(func=cmd_release)

    p = sub.add_parser("list", help="list versions with dates and entry counts")
    p.add_argument("file", help="path to CHANGELOG.md or RELEASE_NOTES.md")
    p.set_defaults(func=cmd_list)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
