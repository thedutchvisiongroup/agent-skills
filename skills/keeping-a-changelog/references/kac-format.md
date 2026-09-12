# Keep a Changelog 2.0.0 — Annotated Format Specification

The canonical source is https://keepachangelog.com/en/2.0.0/. This reference annotates
the spec with the concrete rules this skill enforces. The internal `CHANGELOG.md` follows
this specification 1:1 and is **always written in English**.

## Contents

- File and preamble
- Document skeleton
- Version headings
- The [Unreleased] section
- The six change types
- Entry writing rules
- Breaking changes
- Security entries
- The deprecation lifecycle
- Link reference definitions
- Curation: what is notable
- Drafting entries from git history
- Bad practices

## File and preamble

The file is named `CHANGELOG.md` (uppercase, repository root) and opens with a fixed
preamble that declares the conventions — telling readers **and tools** what to expect:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

- Pin the Keep a Changelog link to the format version you follow, so it stays accurate.
- Name the actual versioning scheme: Semantic Versioning, Calendar Versioning, or
  whatever the project uses. The versioning scheme defines what "breaking" means.
- Adopting a newer format version does not require rewriting history — the format core
  (six types, dates, `Unreleased`, `[YANKED]`) is stable.

## Document skeleton

```markdown
# Changelog
<preamble>

## [Unreleased]

### Added
- ...

## [2.1.0] - 2026-03-14

Optional 1-2 sentence release summary.

### Added
- ...
### Changed
- ...
### Fixed
- ...

## [2.0.0] - 2026-01-05

### Removed
- ...

<link reference definitions>
```

Structure rules:

- `#` H1 exactly once, at the top: `# Changelog`.
- Every version is an H2: `## [x.y.z] - YYYY-MM-DD`.
- Every change type is an H3 inside a version: `### Added`.
- Entries are bullets under their type. No other heading levels exist in the format.
- The latest release comes first; `[Unreleased]` sits above it.
- Omit type sections that have no entries — empty sections are noise.

## Version headings

```markdown
## [1.2.3] - 2026-03-14
## [1.2.2] - 2026-02-28 [YANKED]
## [Unreleased]
```

- The square brackets make the version a Markdown reference link, resolved once at the
  bottom of the file (see "Link reference definitions").
- The date is the **release date**, ISO 8601 `YYYY-MM-DD` — never regional formats.
- A version may open with a short summary (1-2 sentences) before the typed sections.
  Optional; use it when the release deserves an introduction, skip it otherwise.
- Yanked releases (pulled for a serious bug or security issue) **stay listed**, marked
  `[YANKED]` — the brackets make the tag easy to parse. Mention which version to use
  instead.
- Any versioning scheme is allowed (SemVer, CalVer, plain numbers); note the scheme in
  the preamble. Projects that release continuously with no version numbers keep dated
  entries under `[Unreleased]`.
- A changelog may be improved after a release (a forgotten entry, a missed breaking
  change). When you correct an already-released section, note the date of the
  correction so readers notice the update.

## The [Unreleased] section

Keep `[Unreleased]` at the top to collect notable changes as they land. It serves two
purposes: readers can see what to expect, and at release time its content simply becomes
the new version's section. At release time: rename the heading to
`## [x.y.z] - <date>`, insert a fresh empty `[Unreleased]` above it, update the link
definitions — this is exactly what `changelog.py release` does mechanically.

## The six change types

| Type | Use for | Reader's question it answers |
|------|---------|------------------------------|
| `Added` | New features | "What can I do now that I couldn't?" |
| `Changed` | Changes in existing functionality | "What behaves differently after upgrading?" |
| `Deprecated` | Soon-to-be removed features | "What should I stop relying on?" |
| `Removed` | Now removed features | "What disappeared?" |
| `Fixed` | Bug fixes | "What was wrong and is now right?" |
| `Security` | Vulnerability fixes | "What do I need to patch, urgently?" |

Choosing between the three that overlap:

- **Fixed vs. Changed**: ask whether the old behavior was a bug. Bug → `Fixed`.
  Intentional behavior now changed → `Changed`.
- **Security**: the change addresses a vulnerability. It might also fit `Fixed` or
  `Changed`, but its urgency and audience differ — that justifies its own type.

What is deliberately **not** a type:

- **Dependencies** are not a type. A dependency update can be harmless, a fix, or
  breaking — describe its effect under the right type, or leave it out.
- **Known issues** are discovered, not changed — note them on the affected version or
  in the issue tracker.
- `Performance`, `Improved`, `Internal`, `Housekeeping` — all map to `Changed` or are
  not notable enough to list. The six types do not grow; every changelog stays readable
  the same way and parseable by the same tools.

## Entry writing rules

- **One entry = one bullet, maximum 2-3 sentences.** This is the bright line.
- **Larger changes get sub-bullets**, not longer sentences:

```markdown
- Reworked the export pipeline to stream large reports instead of building them in
  memory.
  - Reports over 100 MB no longer fail with an out-of-memory error.
  - Progress is now reported per page instead of per report.
```

- Write from the reader's perspective: what changed for them, and why. A changelog
  entry records a notable difference, often spanning several commits — it is not a
  reworded commit message.
- Name the part of the project the entry touches: the component, command, endpoint,
  or setting. "Added a retry option to the deploy command" beats "Added an option".
- Prefer plain prose over bare references: link issues and pull requests inline when
  it helps (`(#123)`), but keep the sentence meaningful without it.
- Past tense or present tense — pick one per file and stay consistent.
- English only, always, for `CHANGELOG.md`.

## Breaking changes

Breaking changes go under `Changed` or `Removed` — with a `**Breaking:**` lead-in so
they stand out while staying with their type:

```markdown
### Changed

- **Breaking:** `parse()` now returns a `Result` instead of raising — call sites must
  handle the error case explicitly.
```

- The version number already signals a break under SemVer, but the number is easy to
  miss — always add the marker to the entry itself.
- Say **what breaks**: which interface the project keeps stable (CLI, library API,
  protocol, file format, config schema) — state which one the versioning covers.
- A short upgrade note can live in the entry ("rename the `color` option to `theme`").
  When the steps are substantial, link to a migration guide instead of inlining the
  procedure — a how-to buries what changed.

## Security entries

When a CVE identifier exists, **lead with it** so readers and security tools can match
the entry to the advisory:

```markdown
### Security

- CVE-2026-31840: redirects to a different host no longer forward the `Authorization`
  header, preventing credential leaks to untrusted destinations.
```

Keep the entry focused; link to the full advisory for details.

## The deprecation lifecycle

Announce a deprecation before you act on it, so anyone upgrading meets the warning
before the removal:

1. Version N: the feature is listed under `Deprecated` — including the version that
   will remove it, so users can plan.
2. Version N+1 (or the announced major): the feature moves to `Removed`, with a
   `**Breaking:**` marker if its removal breaks workflows.

If you do nothing else in a changelog, list deprecations, removals, and breaking
changes. Upgrading should be painfully clear about what will break.

## Link reference definitions

Resolve every version heading once at the bottom of the file, pointing each version to
its comparison with the previous one:

```markdown
[Unreleased]: https://github.com/org/repo/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/org/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
```

- `[Unreleased]` compares the latest tag to `HEAD` — it always shows what has accrued
  since the last release.
- The oldest version links to its tag — there is nothing earlier to compare with.
- Issue/PR references may also be collected as reference-style definitions at the
  bottom, keeping the prose readable and every pointer in one place you control.
- Links break when a repository moves, and PR numbers belong to one host — prefer
  portable references (tags, commit hashes) for pointers that must survive a move.

## Curation: what is notable

Keeping a changelog is partly an act of restraint. A changelog records **notable**
changes; version control already records every change. Judgment about notability is
human — that judgment is the job.

Rough notability test: would a user, contributor, or operator reading only the version
heading and this entry understand something real changed for them? If an entry only
makes sense to the author of the commit, it is not ready.

## Drafting entries from git history

Machines draft; humans curate. A language model (this agent) can produce a draft from a
diff in seconds — that is the starting point, not the result. The brief for any draft:

1. Summarize notable, user-facing changes — do not paste a git log.
2. Group commits into changes: several commits often form one entry; some commits form
   none.
3. Sort each change into exactly one of the six types.
4. Explain the reason in the text — what it means for the reader.
5. Mark breaking changes with `**Breaking:**`; lead Security entries with their CVE.
6. Remove anything not worth reading.
7. Then re-read the result as if you were the user, and cut again.

Generated-from-commits changelogs (semantic-release, Changesets, git-cliff) are raw
material at best: a commit and a changelog entry are written for different people, and
one does not convert cleanly into the other.

## Bad practices

- **Commit log dumps**: merge commits, cryptic messages, internal noise — a raw git
  log is not a changelog.
- **Ignoring deprecations**: upgrading should never be a surprise.
- **Inconsistent recording**: a changelog that sometimes lists changes misleads more
  than none at all — readers treat it as the full picture.
- **Regional date formats**: `03/04/2026` is ambiguous; only `YYYY-MM-DD` is safe.
- **Empty sections**: headings with no entries are noise; remove them.
- **Hiding yanked releases**: list them, marked `[YANKED]`, with the version to use
  instead.
