# Migrating an Existing Changelog

For projects that already have a changelog (or changelog-like file) that does not
conform to the format: wrong heading style, undated versions, commit dumps, mixed
section names. The goal is a `CHANGELOG.md` that passes the validator without losing
real history.

## Contents

- Audit first
- Strategy A: record from now on (default)
- Strategy B: reconstruct history
- Mapping legacy categories to the six types
- Migration steps
- Rules

## Audit first

1. Run the validator to see the gap:

   ```bash
   python3 <skill-dir>/scripts/changelog.py validate CHANGELOG.md
   ```

2. Inventory what exists: which versions are listed, do they have dates, what
   section names are used, how much of it is commit noise?
3. Check the git tags — real release dates live there (`git tag -l`,
   `git log -1 --format=%ad <tag>`), not in commit dates.

## Strategy A: record from now on (default)

Keep the old file untouched and start the new format **from the current version**:

1. Rename the old file to its archive name (e.g. `CHANGELOG.old.md` or
   `docs/changelog-archive.md`) or keep its content below the new content —
   whichever keeps it findable.
2. Write a fresh `CHANGELOG.md` (skeleton from [kac-format.md](kac-format.md))
   with an empty `[Unreleased]`.
3. Record notable changes from now on, properly.

This is the default because it is honest, cheap, and impossible to get wrong: no
history is fabricated, and the migration takes minutes. Reconstructing the past is
optional and can happen later (Strategy B can be applied retroactively).

## Strategy B: reconstruct history

Worth doing when the audience needs the full record: public libraries whose consumers
upgrade across many versions, or projects whose old changelog is half-usable already.

1. List the released versions from git tags (not from memory).
2. For each version, collect what was notable **at that time**:
   - usable entries from the old file (rewrite per the entry rules, one bullet each);
   - for versions with nothing usable: `git log <prev-tag>..<tag>`, grouped into
     changes — drafts only, then curate.
3. Use the tag dates as release dates.
4. Versions with no recoverable notable changes still get their heading with the
   date, plus a one-sentence summary — `No notable changes were recorded for this
   version.` — so the file stays valid; never invent entries to fill a version.

Do not mix strategies per version without saying so: pick one, apply it, and if the
file switches (e.g. reconstructed up to 1.0, recorded properly after), that is fine —
the format does not care, readers do not either.

## Mapping legacy categories to the six types

| Legacy heading | Maps to | Notes |
|----------------|---------|-------|
| Features, New, Enhancements | `Added` | |
| Improvements, Performance | `Changed` | Only if user-visible; otherwise drop |
| Bugfixes, Bug Fixes, Resolved | `Fixed` | |
| Deprecated (any spelling) | `Deprecated` | Add "removed in version X" if known |
| Deleted, Dropped | `Removed` | Add `**Breaking:**` where upgrades break |
| Security, Vulnerabilities | `Security` | Lead with the CVE if known |
| Dependencies, Maintenance, Chores, Internal | — | Drop unless the effect is user-visible |
| Known issues | — | Not a change; move to the issue tracker |
| Breaking changes (own section) | `Changed` / `Removed` | Merge into their type with `**Breaking:**` |

## Migration steps

1. Audit (above) and choose the strategy — when in doubt, ask the user which they
   want; reconstructing history is a real time investment.
2. Produce the new `CHANGELOG.md`: preamble pinned to
   [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/), the project's
   versioning scheme, the versions in scope, newest first.
3. Rewrite entries: one bullet each, 2-3 sentences max, English, grouped under the
   six types; add `**Breaking:**` and deprecation notes where the history shows them.
4. Add link reference definitions for every version (compare URLs from the tags).
5. Validate and fix until clean:

   ```bash
   python3 <skill-dir>/scripts/changelog.py validate CHANGELOG.md
   ```

6. If the project keeps `RELEASE_NOTES.md`, migrate it the same way: same versions,
   same dates, user-facing language, one language per file.

## Rules

- **Never delete history.** Unmigrated old content stays archived and linked from
  (or below) the new file.
- **Never fabricate entries.** A version with nothing notable gets a heading and
  nothing else.
- **Dates come from actual releases** (tags), not from commit or edit dates.
- **Yanked releases stay listed**, marked `[YANKED]`, even in migration.
- The result must pass the validator — that is the definition of "migrated".
