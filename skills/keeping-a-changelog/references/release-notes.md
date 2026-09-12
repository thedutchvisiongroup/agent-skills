# Writing User-Facing Release Notes (RELEASE_NOTES.md)

`RELEASE_NOTES.md` is the user-facing counterpart of `CHANGELOG.md`: a curated,
per-release announcement written for people who **use** the software, not the people
who build it. It is derived from the internal changelog but never auto-assembled —
extraction provides the draft basis; the writing is deliberate work.

## Contents

- Purpose and relationship to the changelog
- When a project keeps release notes
- Structure
- Language policy (English / Dutch)
- Curation: what makes the cut
- Rewriting rules
- Yanked releases and breaking changes
- Workflow
- Do / Don't

## Purpose and relationship to the changelog

| | `CHANGELOG.md` | `RELEASE_NOTES.md` |
|---|---|---|
| Role | The complete, ongoing record | An announcement per release |
| Audience | Developers, contributors, operators | End users, customers, admins |
| Content | Every notable change, technical | A curated subset, benefit-first |
| Voice | Precise, plain | Plain **and** user-oriented ("you can now…") |
| Sections | `[Unreleased]` + every version | Released versions only |
| Language | English only | English or Dutch (one per file) |

The changelog is the source; the release notes are drawn from it. Never maintain the
two independently, and never let a host's generated release page become a second
source of truth — channels like GitHub Releases publish **from** this file.

## When a project keeps release notes

`RELEASE_NOTES.md` is optional; `CHANGELOG.md` is not. A project keeps release notes
when it has an audience that reads them: end users of an application, customers of a
SaaS product, site admins updating a plugin. A library consumed only by developers
who read the changelog may skip it. When absent and the need is unclear, ask the user
once, then stay consistent for the project.

## Structure

```markdown
# Release Notes

All user-facing changes per release, derived from CHANGELOG.md.

## [2.1.0] - 2026-03-14

Exports of large reports no longer fail — and you can follow their progress live.

### Added

- You can now pause and resume a running export.

### Fixed

- Reports larger than 100 MB no longer fail with an out-of-memory error.
```

- H1 `# Release Notes`, then a one-sentence preamble.
- Every release gets `## [x.y.z] - YYYY-MM-DD` with **exactly the same version label
  and date as `CHANGELOG.md`** — the validator enforces this parity.
- **No `[Unreleased]` section** — users only see what has shipped.
- The six type sections are available, but a release uses **only the groups it
  needs** — often just two or three.
- A one or two sentence release intro is welcome when there is a theme worth stating.
- Entries follow the same bright line as the changelog: one bullet, 2-3 sentences
  max, sub-bullets for anything larger.

## Language policy (English / Dutch)

- **One language per file**, for headings, entries, and intro alike.
- **English types**: `Added, Changed, Deprecated, Removed, Fixed, Security`.
- **Dutch types**: `Nieuw, Gewijzigd, Verouderd, Verwijderd, Gefixt, Beveiliging`.
- Dates and version labels are always ISO (`YYYY-MM-DD`, `[2.1.0]`) in both languages.

When writing new release notes for a file that already exists: **detect the language
from the type headings already used and match it.** When writing the first entry ever:
**ask the user** which language the file should be in. When the user asks for notes in
a language different from the existing file, do not mix — propose a separate variant
file (e.g. `RELEASE_NOTES.nl.md` next to `RELEASE_NOTES.md`) and ask which one to
maintain. The validator accepts any `RELEASE_NOTES*.md` and warns when EN and NL
headings are mixed within one file.

## Curation: what makes the cut

Start from the extracted internal section, then keep only what changes something for
a user:

- **Keep**: new capabilities, visible improvements, fixes users can feel, anything
  that changes their workflow, all breaking changes and removals.
- **Drop**: internal refactors, dependency bumps (unless visible), tooling-only
  changes, entries whose subject is invisible to users.
- A release with nothing user-facing can honestly say "Minor fixes and improvements
  under the hood" — do not invent excitement.

Aim for a strict subset: if the internal changelog lists eight entries, two to four
typically survive into the notes.

## Rewriting rules

An internal entry and its user-facing counterpart describe the same change for
different readers. Rewrite, do not copy:

| Internal (CHANGELOG.md) | User-facing (RELEASE_NOTES.md) |
|---|---|
| "Refactored `ExportService::build()` to stream rows via a generator (fixes OOM on >100 MB)" | "Reports larger than 100 MB no longer fail — exports now stream instead of loading everything into memory." |
| "Bumped guzzle/guzzle to ^7.9" | *(dropped — invisible to users)* |
| "**Breaking:** removed the `--legacy-sync` flag; use `--sync` with the new driver" | "Gewijzigd — **Breaking:** de oude `--legacy-sync` optie is verwijderd. Gebruik `--sync` met de nieuwe driver." |

Rules of thumb:

1. **Outcome first**: lead with what the user can do now, or what stops failing — not
   with the component or technique.
2. **No jargon**: no commit hashes, PR numbers, class names, or internal identifiers
   unless users see them too (a setting, a CLI flag, an error message).
3. **"You" is allowed and encouraged** in user-facing notes; the internal changelog
   stays impersonal.
4. **One bullet per outcome** — if one internal entry produces two user-visible
   effects, it may become two user-facing bullets.

## Yanked releases and breaking changes

- Breaking changes, removals, and deprecations are the **last things you may drop**
  from user-facing notes — users must know what will break before they upgrade. Keep
  the `**Breaking:**` lead-in (or `**Belangrijk:**` in Dutch files, if it reads more
  naturally — but stay consistent within the file).
- Yanked releases are listed in the notes with a short "use [x.y.z+1] instead" line.
- Upgrade **steps** do not belong in the notes; link to the documentation. The notes
  say what changed and where to read more.

## Workflow

1. Extract the internal section as the draft basis:

   ```bash
   python3 <skill-dir>/scripts/changelog.py extract CHANGELOG.md <version> -o /tmp/release-draft.md
   ```

2. Curate: strike everything invisible to users.
3. Rewrite each surviving entry in the file's language, outcome-first.
4. Add the `## [version] - date` heading with the same label and date as the
   changelog, plus a one-sentence intro when there is a theme.
5. Validate structure and parity, fix errors, repeat:

   ```bash
   python3 <skill-dir>/scripts/changelog.py validate CHANGELOG.md RELEASE_NOTES.md
   ```

Worked examples (English and Dutch) live in [examples.md](examples.md).

## Do / Don't

| Do | Don't |
|----|-------|
| Detect the file's language from existing headings; ask on the first entry ever | Mix English and Dutch headings in one file |
| Keep version labels and dates identical to `CHANGELOG.md` | Re-date, renumber, or paraphrase version headings |
| Lead with the user outcome | Lead with the class, ticket, or technique |
| Keep every breaking change and removal | Drop breaking changes to "keep it friendly" |
| Write "Minor fixes and improvements" when nothing visible shipped | Pad notes with invisible technical changes |
| Link to docs for upgrade steps | Inline long migration procedures |
