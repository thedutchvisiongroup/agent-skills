---
name: keeping-a-changelog
description: Maintains Keep a Changelog 2.0.0-compliant changelogs and user-facing release notes. Creates and updates CHANGELOG.md (the internal, always-present, English-only record), cuts releases, writes the optional RELEASE_NOTES.md (user-facing, English or Dutch), validates both files programmatically, and migrates existing changelogs to the format. Use when the user mentions a changelog or release notes, asks to document changes (git changes or named changes) in CHANGELOG.md, cuts or prepares a release, or wants CHANGELOG.md or RELEASE_NOTES.md validated.
---

# Keeping a Changelog

Two artifacts share one format:

| Artifact | Audience | Presence | Language |
|----------|----------|----------|----------|
| `CHANGELOG.md` | Developers, contributors — the complete record | **Always** | **English only** |
| `RELEASE_NOTES.md` | End users — curated, per-release announcements | **Optional**, per project | English **or** Dutch (one language per file) |

The changelog is the source; release notes are drawn from it — extracted as a draft basis,
then **hand-written (AI-assisted), never auto-assembled**. Machines draft, humans curate:
an agent may draft entries from git changes, but curation (what is notable, how it reads) is
always a deliberate writing step, never a mechanical transformation.

## The Format

Every `CHANGELOG.md` follows Keep a Changelog 2.0.0 exactly:

````markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- One entry per bullet, written for humans.

## [1.0.0] - 2026-01-31

Optional one or two sentence release summary.

### Fixed

- Corrected the date parsing for leap years.

[Unreleased]: https://github.com/org/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
````

`RELEASE_NOTES.md` mirrors this skeleton (H1 + `## [x.y.z] - date` sections, same
version labels and dates), but contains **released versions only — never an
[Unreleased] section** — and only the entries that matter to users, in user language.

### The six change types

| Type | Use for |
|------|---------|
| `Added` | New features |
| `Changed` | Changes in existing functionality |
| `Deprecated` | Soon-to-be removed features (announce before you remove) |
| `Removed` | Now removed features |
| `Fixed` | Bug fixes — the old behavior was wrong |
| `Security` | Vulnerability fixes — lead with the CVE when one exists |

Deciding between `Fixed`, `Changed`, and `Security`: ask whether the old behavior was a
bug. Bug → `Fixed`. Intentional behavior now different → `Changed`. Vulnerability →
`Security`. Dependencies, refactors, and housekeeping are **not** types — describe their
user-facing effect under the right type, or leave them out.

### Entry rules (bright lines)

- Every entry is **one bullet, maximum 2-3 sentences**.
- A change too large for one bullet: keep the one-bullet summary and add **sub-bullets** for detail.
- `CHANGELOG.md` is **always English**, without exception.
- Breaking changes carry a `**Breaking:**` lead-in, under `Changed` or `Removed`.
- Name the part of the project an entry touches (component, command, endpoint).
- Dates are ISO 8601 (`YYYY-MM-DD`), newest release first, `[Unreleased]` at the top.
- Version and issue links are reference-style definitions at the bottom of the file.
- Yanked releases stay listed: `## [0.0.5] - 2014-12-13 [YANKED]`.

## Process

### Phase 1: Determine the state (REQUIRED)

1. Find `CHANGELOG.md` at the repository root. If it is missing, set one up (see
   "Setting up a changelog" below).
2. Look for `RELEASE_NOTES.md` next to it (any `RELEASE_NOTES*.md` variant counts).
   This file is **optional**:
   - If present → the project keeps user-facing notes; detect its language from the
     type headings used (`Added/Fixed/...` = English, `Nieuw/Gefixt/...` = Dutch).
   - If absent → ASK the user whether this project should keep user-facing release
     notes, unless the project has already established the answer.
   - A request for notes in a **different language** than the existing file means a
     separate variant file (e.g. `RELEASE_NOTES.nl.md`) — ASK the user which
     variant to write instead of mixing languages.
3. When writing the first release notes ever, ASK which language the file should be in.
4. Run the validator to learn the current state:

```bash
python3 <skill-dir>/scripts/changelog.py validate CHANGELOG.md [RELEASE_NOTES.md]
```

### Phase 2: Turn changes into entries (REQUIRED)

Input: git changes (diff/log) or changes named by the user.

1. **Draft** from the raw material: read the diff or git log, and group multi-commit
   work into single changes. NEVER paste a git log into the changelog.
2. **Curate**: decide what is notable. Trivial changes are left out deliberately.
3. **Write** each entry per the entry rules above and place it under `[Unreleased]`
   in its type section. Write from the reader's perspective, not the commit's.

```
STOP. Before finishing this phase, verify:
- [ ] every entry is one bullet, max 2-3 sentences (sub-bullets for larger changes)
- [ ] every entry is in the right type section (bug → Fixed, intentional → Changed)
- [ ] breaking changes carry **Breaking:**; every deprecation is listed
- [ ] CHANGELOG.md stayed English
- [ ] the validator reports 0 errors
If any box is unchecked: fix it before proceeding.
```

### Phase 3: Cut a release

```bash
python3 <skill-dir>/scripts/changelog.py release CHANGELOG.md <version> [--date YYYY-MM-DD]
```

The command refuses to run on a changelog with validation errors or an empty
`[Unreleased]` section, renames `[Unreleased]` into the dated version, inserts a fresh
`[Unreleased]` at the top, updates the link reference definitions, and reminds you about
missing release notes. The date defaults to today. Pick the version number per the
project's stated scheme (default: Semantic Versioning — major for breaking changes,
minor for features, patch for fixes). The script only edits the file — create and push
the matching git tag yourself (`git tag v<x.y.z>`); the compare links point at tags.

### Phase 4: Write the release notes (only when the project keeps RELEASE_NOTES.md)

1. Extract the release section as the draft basis:

```bash
python3 <skill-dir>/scripts/changelog.py extract CHANGELOG.md <version> --output /tmp/release-draft.md
```

2. Hand-write the user-facing entry from that basis: a curated subset of the internal
   entries, rewritten in non-technical, outcome-first language, under the same
   `## [version] - date` heading. Breaking changes and removals always stay visible.
   Follow the language policy from Phase 1 (one language per file; Dutch files use
   `Nieuw/Gewijzigd/Verouderd/Verwijderd/Gefixt/Beveiliging`).
3. Validate:

```bash
python3 <skill-dir>/scripts/changelog.py validate CHANGELOG.md RELEASE_NOTES.md
```

Full writing guide with rewrite rules and good/bad examples:
[references/release-notes.md](references/release-notes.md).

### Phase 5: Validate (ALWAYS the last step)

Run the validator over both files, fix every error, and repeat until it reports 0
errors. Warnings are best-practice advice — preamble and link-definition warnings are
compliance-relevant and MUST be fixed in any file this session created or edited; for
pre-existing files, fix them when the cause is clear, and mention any warnings you
leave in place.

## Setting up a changelog

When a project has no `CHANGELOG.md`:

1. Create it with the skeleton above (preamble pinned to the format version, the
   project's versioning scheme, an empty `[Unreleased]`, compare links once tags exist).
2. Start recording notable changes **now** — do not fabricate history. Reconstructing
   past releases is a deliberate, optional exercise; see
   [references/migration.md](references/migration.md).
3. `RELEASE_NOTES.md` is only created when the user wants user-facing notes (Phase 1).

## Migrating an existing changelog

For a changelog that does not conform (wrong headings, wrong dates, commit dumps),
follow [references/migration.md](references/migration.md): audit, choose the
"record from now on" or the "reconstruct history" strategy, map legacy categories to
the six types, then validate.

## When NOT to Use This Skill

- One-off scripts, docs-only repositories, or projects without versioned releases —
  no changelog is needed.
- Git commit messages (Conventional Commits) — related, but a commit message is not a
  changelog entry; do not copy one into the other.
- Hosted release pages (GitHub Releases) — publish from `RELEASE_NOTES.md`, but the
  files in the repository remain the canonical record; do not maintain the host's copy
  as a second source of truth.

## Script Reference

`<skill-dir>/scripts/changelog.py` — Python 3, standard library only.

| Command | Purpose | Exit codes |
|---------|---------|------------|
| `validate CHANGELOG.md [RELEASE_NOTES.md]` | Format compliance (errors) + best practices (warnings) + notes parity | 0 ok, 1 errors, 2 usage |
| `extract <file> <version> \| --unreleased [-o FILE]` | Print one release section verbatim (draft basis) | 0 ok, 1 not found, 2 usage |
| `release CHANGELOG.md <version> [--date ...]` | Cut `[Unreleased]` into a dated version | 0 ok, 1 refused, 2 usage |
| `list <file>` | Versions, dates, entry counts per type | 0 ok, 2 usage |

An unreadable or missing file always exits 2.

## References

| Reference | When to read |
|-----------|--------------|
| [references/kac-format.md](references/kac-format.md) | The full annotated format spec, entry-writing rules, curation philosophy, and the git-to-entry drafting workflow |
| [references/release-notes.md](references/release-notes.md) | Writing user-facing RELEASE_NOTES.md: curation, outcome-first rewriting, the EN/NL language policy |
| [references/examples.md](references/examples.md) | Worked examples: internal entries → user-facing English → user-facing Dutch, plus good/bad rewrites |
| [references/migration.md](references/migration.md) | Migrating an existing non-conforming changelog to the format |

## Quick Reference

| Task | Action |
|------|--------|
| Add entries for changes | Phase 2: draft from git/named changes → curate → one bullet per entry under `[Unreleased]` |
| Cut a release | `changelog.py release CHANGELOG.md <version>` (date defaults to today) |
| Write release notes | Extract section → rewrite user-facing → validate parity |
| Check a changelog | `changelog.py validate CHANGELOG.md [RELEASE_NOTES.md]` |
| See what is unreleased | `changelog.py extract CHANGELOG.md --unreleased` |
| Overview of versions | `changelog.py list CHANGELOG.md` |
| New project | Skeleton + empty `[Unreleased]`; RELEASE_NOTES.md only if wanted |
| Legacy changelog | Follow [references/migration.md](references/migration.md) |
