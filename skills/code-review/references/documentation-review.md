# Documentation Review

Read this during Phase 5 (Design and Maintainability). Code tells you *how*; documentation must supply what code cannot: *why*, *when*, and *how to use*.

## Contents

- The Two Kinds of Documentation
- Comments: WHY, Not WHAT
- API Documentation
- External Documentation Sync
- Stale Documentation
- Review Checklist

## The Two Kinds of Documentation

1. **Comments** — for maintainers, inside the code. Explain reasoning the code can't express.
2. **Unit/API documentation** (docstrings, JSDoc, Javadoc, etc.) — for users of the code. Describe purpose, usage, and behavior.

Both are in scope for review. Absence where needed is a finding; noise where unneeded is also a finding.

## Comments: WHY, Not WHAT

**Good comments explain:**

- *Why* this code exists (business rule, constraint, requirement)
- *Why* this approach was chosen over the obvious one
- Workarounds for external bugs/limitations — with a link or ticket reference
- Warnings about pitfalls for the next maintainer

```python
# GOOD: explains reasoning
# Cap retries to prevent infinite loops when the network flaps
max_retries = min(requested_retries, 5)

# BAD: narrates the code
# Add 5 to x
x = x + 5
```

**Bad comments to flag:**

- Narration of what the code plainly does
- Commented-out code → flag as dead code (see `dead-code.md`)
- Changelog comments (`# changed 2023-04-01`) — version control does this
- Apology/compensation comments on unclear code — recommend making the code clearer instead of commenting it

**The rename-before-comment rule:** if a block needs a WHAT comment, first ask whether renaming or extracting a well-named function would make the comment unnecessary. Self-documenting code beats documented code (see `naming-and-readability.md`).

**Legitimate WHAT comments:** regular expressions, complex algorithms, bit manipulation, non-obvious math — here, explaining the mechanism IS valuable.

**Pre-existing comments:** check whether this change invalidates any of them. A TODO this change resolves should be removed. A comment warning against exactly this change deserves a `question`.

## API Documentation

Public API units (modules, exported functions/classes, endpoints) should document:

- [ ] **Purpose** — one line: what it's for
- [ ] **Parameters** — types, constraints, units, defaults
- [ ] **Returns** — shape and semantics, including edge-case behavior
- [ ] **Errors** — which exceptions/error values, and when they occur
- [ ] **Side effects** — I/O, mutation, external calls
- [ ] **Example** — when usage isn't obvious from the signature

Internal helpers: use judgment. Document when the behavior is non-obvious; skip when the name and signature say it all. Missing docs on a *public* API = `issue (non-blocking)` at minimum. Missing docs on a trivial internal = not a finding.

## External Documentation Sync

When a change alters how users build, test, configure, run, or interact with the system, check:

- [ ] README updated
- [ ] API reference docs updated (or regenerated, if generated)
- [ ] Changelog entry (if the project keeps one)
- [ ] Migration/upgrade notes for breaking changes
- [ ] Configuration examples updated
- [ ] Deleted or deprecated code → corresponding docs deleted or updated

Missing documentation for user-facing behavior changes is a finding. When unsure whether the project's conventions require it, ask the user — norms differ per project.

## Stale Documentation

Stale documentation is worse than no documentation — it actively misleads.

- **Comments contradicting the code** → flag as `issue`
- **Docs referencing removed/renamed symbols** → flag
- **Generated docs not regenerated** after an API change → flag
- **TODO/FIXME hygiene** — every TODO should have an owner or ticket and still be relevant. Orphan TODOs (no owner, no date, forgotten context) → `nitpick` or `suggestion` to track or delete

## Review Checklist

- [ ] Public APIs documented: purpose, params, returns, errors, side effects
- [ ] Comments explain WHY; no WHAT-narration that a rename would fix
- [ ] No commented-out code or changelog comments (cross-report as dead code)
- [ ] Behavior changes synced to README / API docs / changelog / migration notes
- [ ] Deleted code's documentation deleted too
- [ ] Pre-existing comments checked for invalidation by this change
- [ ] TODOs have owners/tickets; stale ones flagged
- [ ] Findings reported only — no documentation written into the reviewed code
