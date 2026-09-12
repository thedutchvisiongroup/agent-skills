# Worked Examples

One fictional project ("InboxFlow", a reporting/export CLI) shown three times: the
internal `CHANGELOG.md`, the user-facing `RELEASE_NOTES.md` in English, and the same
notes in Dutch. The annotations explain what changed between the layers and why.

## Contents

- The internal CHANGELOG.md
- The user-facing RELEASE_NOTES.md (English)
- The user-facing RELEASE_NOTES.md (Dutch)
- Per-type rewrite map
- Good vs. bad: curated entry vs. commit dump

## The internal CHANGELOG.md

````markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Digest emails now show the recipient's timezone instead of UTC.

## [2.1.0] - 2026-03-14

The export pipeline release: large reports stream instead of failing, and exports
can be paused.

### Added

- Streaming export pipeline for reports of any size.
  - Reports over 100 MB no longer need to fit in memory.
  - Progress is reported per page instead of per report.
- Pause and resume for running exports (`export --pause`, `export --resume`).

### Changed

- **Breaking:** removed the `--legacy-sync` flag, deprecated in 2.0.0. Use
  `--sync` with the v2 sync driver.

### Fixed

- Exports larger than 100 MB no longer fail with an out-of-memory error.

## [2.0.0] - 2026-01-05

### Added

- `--sync` flag using the v2 sync driver, replacing the legacy sync mechanism.

### Deprecated

- `--legacy-sync` — removal planned for 3.0.0; migrate to `--sync`.

### Security

- CVE-2026-31840: cross-host redirects no longer forward the `Authorization`
  header, preventing credential leaks to untrusted destinations.

## [1.3.2] - 2025-12-02

### Fixed

- Gzip-encoded responses are decompressed correctly instead of returned as raw
  bytes.

## [1.3.1] - 2025-11-30 [YANKED]

This release was yanked: the gzip fix corrupted responses larger than 64 KB.
Use 1.3.2 instead.

### Fixed

- Gzip-encoded responses are decompressed instead of returned as raw bytes.

## [1.3.0] - 2025-11-18

### Added

- Support for `gzip` and `deflate` response compression.

[Unreleased]: https://github.com/acme/inboxflow/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/acme/inboxflow/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/acme/inboxflow/compare/v1.3.2...v2.0.0
[1.3.2]: https://github.com/acme/inboxflow/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/acme/inboxflow/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/acme/inboxflow/releases/tag/v1.3.0
````

What to notice:

- English only, `[Unreleased]` first, newest release next, ISO dates everywhere.
- The `2.1.0` summary is one sentence — optional, only because the release has a theme.
- The large pipeline change is **one bullet with sub-bullets**, not a paragraph.
- The removal in `2.1.0` completes the deprecation announced in `2.0.0`.
- `1.3.1` stays listed as `[YANKED]` with a "use X instead" line; `1.3.2` follows it.
- Every version heading resolves to a compare link at the bottom.
- No dependency bumps, refactors, or tooling noise — they were judged not notable.

## The user-facing RELEASE_NOTES.md (English)

````markdown
# Release Notes

All user-facing changes per release, derived from CHANGELOG.md.

## [2.1.0] - 2026-03-14

Large reports no longer fail on export — and you can pause a running export.

### Added

- You can now pause a running export and resume it later.

### Changed

- **Breaking:** the old `--legacy-sync` option is gone. Run exports with
  `--sync` instead.

### Fixed

- Exporting a report larger than 100 MB no longer fails.

## [2.0.0] - 2026-01-05

### Added

- New `--sync` option — a faster, more reliable way to sync your reports.

### Deprecated

- The `--legacy-sync` option will stop working in 3.0.0. Switch to `--sync`.

### Security

- Fixed a security issue where login credentials could leak to other servers
  during a redirect (CVE-2026-31840). Update as soon as possible.

## [1.3.2] - 2025-12-02

### Fixed

- Large compressed downloads no longer arrive corrupted.

## [1.3.1] - 2025-11-30 [YANKED]

This version was pulled back — it corrupted large compressed downloads.
Use 1.3.2 instead.

## [1.3.0] - 2025-11-18

### Added

- Downloads are now compressed, making them noticeably faster.
````

What changed from the internal changelog:

- **Subset**: the streaming-pipeline rewrite (internal `Added`) became the release
  intro; its sub-bullets collapsed into the `Fixed` outcome users feel. The
  progress-per-page detail was dropped.
- **Rewritten, not copied**: "Streaming export pipeline for reports of any size"
  became "Large reports no longer fail on export".
- **"You" is allowed**: "You can now pause a running export".
- **Breaking change kept**, phrased as the action the user must take.
- **Security translated to impact**: no internal terminology, CVE kept, urgency added.
- **Same version labels and dates** as the changelog — parity is what the validator
  checks. No `[Unreleased]` section: the timezone fix stays invisible until released.

## The user-facing RELEASE_NOTES.md (Dutch)

````markdown
# Release Notes

Alle gebruikersgerichte wijzigingen per release, afgeleid van CHANGELOG.md.

## [2.1.0] - 2026-03-14

Grote rapporten mislukken niet langer bij het exporteren — en je kunt een lopende
export pauzeren.

### Nieuw

- Je kunt een lopende export nu pauzeren en later hervatten.

### Gewijzigd

- **Belangrijk:** de oude `--legacy-sync` optie is verdwenen. Gebruik `--sync`.

### Gefixt

- Het exporteren van rapporten groter dan 100 MB mislukt niet langer.

## [2.0.0] - 2026-01-05

### Nieuw

- Nieuwe `--sync` optie — een snellere en betrouwbaardere manier om je rapporten
  te synchroniseren.

### Verouderd

- De `--legacy-sync` optie werkt niet meer vanaf versie 3.0.0. Schakel over op
  `--sync`.

### Beveiliging

- Beveiligingsprobleem opgelost waarbij inloggegevens konden lekken naar andere
  servers tijdens een redirect (CVE-2026-31840). Update zo snel mogelijk.
````

What changed from the English notes:

- Dutch type headings: `Nieuw, Gewijzigd, Verouderd, Verwijderd, Gefixt, Beveiliging`.
- The `**Breaking:**` lead-in is localized consistently (`**Belangrijk:**`) — pick one
  per file and keep it.
- Version labels and dates stay ISO and identical to the changelog — never localized.
- Older releases (1.3.x) omitted here for brevity — validating this file against the
  full changelog then reports a "release [1.3.2] has no release notes yet" warning per
  omitted version. In a real file every released version with user-facing impact
  keeps an entry.

## Per-type rewrite map

| Type | Internal (EN) | Release notes (EN) | Release notes (NL) |
|------|---------------|--------------------|--------------------|
| Added | "Streaming export pipeline (`ExportService`, see #482)." | "Large reports now export without failing." | "Grote rapporten exporteren nu zonder te mislukken." |
| Changed | "**Breaking:** `parse()` returns `Result` instead of raising." | "**Breaking:** errors from `parse()` now need handling — see the migration guide." | "**Belangrijk:** fouten uit `parse()` moeten nu afgehandeld worden — zie de migratiehandleiding." |
| Deprecated | "`--legacy-sync` — removal planned for 3.0.0." | "The `--legacy-sync` option will stop working in 3.0.0." | "De `--legacy-sync` optie werkt niet meer vanaf versie 3.0.0." |
| Removed | "Dropped support for Node 14 (EOL 2023-04)." | "Node 14 is no longer supported — upgrade to Node 18+." | "Node 14 wordt niet langer ondersteund — upgrade naar Node 18+." |
| Fixed | "Fix OOM in `ExportService::build()` on >100 MB payloads." | "Exporting reports larger than 100 MB no longer fails." | "Het exporteren van rapporten groter dan 100 MB mislukt niet langer." |
| Security | "CVE-2026-31840: `Authorization` no longer forwarded on cross-host redirects." | "Fixed a credential leak during redirects (CVE-2026-31840). Update now." | "Lek van inloggegevens bij redirects opgelost (CVE-2026-31840). Update nu." |

## Good vs. bad: curated entry vs. commit dump

Bad — a commit dump (what NOT to write in either file):

```markdown
## [2.1.0] - 2026-03-14

- 3f2a1c9 fix: stuff
- a91bb02 wip export thing
- Merge branch 'feature/pipeline' into main
- 7c0d551 refactor ExportService
- chore: bump deps
```

Good — the same work as curated changelog entries:

```markdown
## [2.1.0] - 2026-03-14

### Added

- Streaming export pipeline for reports of any size.
  - Reports over 100 MB no longer need to fit in memory.

### Fixed

- Exports larger than 100 MB no longer fail with an out-of-memory error.
```

Five commits produced two entries: the merge, the WIP, the refactor, and the
dependency bump were not notable — the user-visible effect of the rest was.
