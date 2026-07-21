# Naming and Readability Review

Read this during Phase 5 (Design and Maintainability). Names are the primary documentation of code. A misleading name is worse than no name — it actively costs every future reader time.

## Contents

- Naming Heuristics
- Magic Numbers and Strings
- Misleading Names
- Readability Signals
- When NOT to Flag
- Review Checklist

## Naming Heuristics

**Reveal intent.** The name should answer: why does this exist, what does it do, how is it used — without needing a comment.

**Length is proportional to scope.**
- `i` is fine in a 3-line loop; unacceptable as a module-level variable
- The wider the scope, the more precise the name must be

**Grammatical conventions:**
- Functions/methods = **verbs**: `calculate_total`, `send_email`
- Classes/types = **nouns**: `Invoice`, `UserRepository`
- Booleans = **predicates**: `is_active`, `has_permission`, `can_retry`, `should_cache`

**Abbreviations:** domain-standard ones are fine (`id`, `url`, `db`, `config`); invented ones are not (`usr`, `mgr`, `calc`, `tmp`). If you have to think about what an abbreviation means, it fails.

**Pronounceable and searchable.** You can't discuss `xqyrt` in a meeting, and you can't grep for it reliably either.

**Avoid noise words** — `data`, `info`, `manager`, `handler`, `util`, `stuff`, `thing` — unless the codebase has a precise convention for them. `UserInfo` vs `User` vs `UserData`: three names, zero information.

**No type encoding** where the type system speaks for itself: `strName`, `arrItems`, `intCount` add noise, not signal.

**One term per concept.** `fetch`, `get`, `retrieve` — pick one and apply it consistently across the change. Use symmetric pairs: `begin`/`end`, `add`/`remove`, `open`/`close`.

**Encode units where applicable:** `timeout_ms`, `max_retries`, `price_cents`, `delay_seconds` — not `timeout` (milliseconds? seconds?).

## Magic Numbers and Strings

- Unexplained literals → named constants: `MAX_RETRIES = 5  # balances reliability vs. latency`
- The constant's name should convey meaning; a short comment can justify the value (no "voodoo constants")
- **Exceptions:** `0`, `1`, `-1` in obvious contexts; domain-well-known values (`100` for percents)
- Repeated string literals with semantic meaning → constants or enums, so typos become compile errors instead of silent bugs

## Misleading Names (worse than bad names)

Flag these as `issue`, not `nitpick`:

- **Names that lie:** `get_user` that also writes to the database; `cached_result` that isn't cached; `user_list` that holds a dict
- **Near-identical names for different things:** `userList` vs `usersList` vs `userListing` in the same scope
- **Names outliving their behavior:** the implementation changed after refactors, the name didn't — verify names against what the code actually does now

## Readability Signals

- **The 30–60 second test:** can a competent but unfamiliar engineer grasp each changed file's intent within a minute? If you (the reviewer) can't, future maintainers can't either — that is a finding about the code, not about you.
- **Visible happy path:** early returns, one indentation level for the main flow, error handling pushed to the edges
- **Scannable structure:** short blocks, blank lines between logical steps, related statements grouped
- **Comments that restate code** → recommend renaming/extracting instead (see `documentation-review.md`)
- **Formatting:** delegate to the formatter. NEVER nitpick what the project's formatter/linter owns — verify it ran (Phase 2), and move on.
- **Idiom consistency:** judge readability against the codebase's language idioms. Don't flag Pythonic code for not reading like Java.

## When NOT to Flag

- **Domain jargon unfamiliar to you** — ask a `question` first; flagging domain vocabulary as "unclear" wastes everyone's time
- **Established codebase conventions** that deviate from your personal preference — consistency beats preference
- **Generated code** — excluded from review
- **Names matching a ubiquitous industry pattern** (`dto`, `ctx`, `req`, `res`) when the codebase uses them consistently

## Review Checklist

- [ ] Every new/changed identifier reveals intent without a comment
- [ ] Name length matches scope width
- [ ] Verbs for functions, nouns for types, predicates for booleans
- [ ] No invented abbreviations, no noise words, no type encoding
- [ ] One term per concept; symmetric pairs used consistently
- [ ] Units encoded in quantity names
- [ ] Magic numbers/strings extracted to justified, named constants
- [ ] No misleading names (verified against actual behavior)
- [ ] Files pass the 30–60 second comprehension test
- [ ] Zero formatting nitpicks (formatter's job) — style flagged only when inconsistent with the codebase
