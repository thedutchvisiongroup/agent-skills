# Code Review Master Checklist

The complete checklist for a thorough review, mirroring the six phases of `SKILL.md`. Copy it, track it, and do not skip items — a checklist without tracking is decoration.

**Reminder: you advise, you never edit. Security is out of scope — see the handoff items below.**

## Contents

- Pre-Review Setup
- Phase 1: Understand the Change
- Phase 2: Automated Checks
- Phase 3: Test Suite Review
- Phase 4: Logic and Correctness
- Phase 5: Design and Maintainability
- Phase 6: Report and Verdict
- Post-Review
- Review Etiquette

## Pre-Review Setup

- [ ] Read the change description; understand the problem being solved
- [ ] Identify change type: feature / fix / refactor / dependency / config
- [ ] Count changed files; identify critical vs. supporting files
- [ ] Confirm how to run lint, types, format check, and tests in this project
- [ ] Confirm coverage expectations (threshold or config)
- [ ] **Ask the security question:** "Security is out of scope for this review. Do you want me to start a separate security-review agent in parallel?"

## Phase 1: Understand the Change

- [ ] Know what the change does and why
- [ ] Know what is NOT tested
- [ ] Sensitive paths noted (auth, payments, personal data, crypto, secrets, uploads, external input) — for handoff only, never for security review

## Phase 2: Automated Checks (ALWAYS)

- [ ] Tooling detected (config files + CI configuration)
- [ ] Linter run — all errors/warnings reported
- [ ] Type checker run (or: reported missing + user asked)
- [ ] Format check run (or: reported missing + user asked)
- [ ] Full test suite run
- [ ] Missing tooling: reported AND asked — nothing skipped silently
- [ ] Failing tests: review STOPPED, failures reported, user consulted
- [ ] **Nothing fixed, formatted, or edited**

```
Lint:    [ ] PASS  [ ] FAIL (___ errors, ___ warnings)  [ ] not available
Types:   [ ] PASS  [ ] FAIL (___ errors)                [ ] not available
Format:  [ ] PASS  [ ] FAIL (___ violations)            [ ] not available
Tests:   [ ] PASS  [ ] FAIL (___ passed, ___ failed, ___ skipped)
```

## Phase 3: Test Suite Review (ALWAYS when a suite exists)

See `test-quality.md` and `coverage-strategies.md`.

- [ ] Flakiness signals checked (sleeps, wall-clock, randomness, order dependence, shared state)
- [ ] Retry config isn't masking instability
- [ ] Skipped tests have reasons and owners
- [ ] Test smells checked (assertion roulette, mystery guest, eager test, over-mocking, implementation-detail testing)
- [ ] Core question applied: would each test FAIL if the code were broken?
- [ ] One behavior per test; assertions specific and on outcomes
- [ ] Coverage run; gaps in changed files identified and prioritized
- [ ] User asked about each significant coverage gap

```
Tests quality: [ ] reviewed   Flakiness: [ ] none found / [ ] suspects reported
Coverage:      ___% (___ gaps identified, ___ questions asked)
```

## Phase 4: Logic and Correctness

See `logic-patterns.md` and `error-handling.md`.

- [ ] Every changed line read in context (whole file where needed)
- [ ] Off-by-one, null handling, boolean logic, race conditions, coercion, boundaries, floats
- [ ] Edge cases: empty, boundary, large, invalid, concurrent inputs
- [ ] No error swallowing; resources released on all paths
- [ ] Propagation, retries, timeouts, partial-failure cleanup reviewed
- [ ] Error messages actionable and traceable

## Phase 5: Design and Maintainability

See `design-principles.md`, `complexity-metrics.md`, `naming-and-readability.md`, `dead-code.md`, `performance-review.md`, `documentation-review.md`.

- [ ] Knowledge duplication flagged; look-alike code left alone (wrong-abstraction nuance applied)
- [ ] Implementations minimal for the stated requirement
- [ ] SOLID checked where the paradigm fits — not forced
- [ ] No speculative generality (YAGNI): every option/hook/abstraction has a current consumer
- [ ] Complexity signals examined; acceptable complexity verified against tests + docs
- [ ] Names reveal intent; no misleading names; magic numbers extracted
- [ ] Dead-code candidates reported with evidence + confidence level (CERTAIN / LIKELY / NEEDS CONFIRMATION)
- [ ] Clear performance patterns flagged (N+1, O(n²), unbounded results); evidence demanded for the rest
- [ ] Public APIs documented; comments explain WHY; external docs synced with behavior changes
- [ ] Architectural consistency: existing patterns followed, right layer for the logic

## Phase 6: Report and Verdict

See `feedback-format.md`.

- [ ] Every finding labeled (issue/suggestion/nitpick/question/todo/praise/thought) + decoration (blocking/non-blocking)
- [ ] Every finding has location, what, why (because…), and recommendation
- [ ] Automated check results table complete (including "not available")
- [ ] Coverage gaps include the user's answers
- [ ] Security handoff section present: user's answer + sensitive-path recommendation if triggered
- [ ] At least one sincere praise (never manufactured)
- [ ] Verdict matches severity mapping: blocking → REQUEST CHANGES; questions → COMMENT; else APPROVE
- [ ] **The codebase is untouched — review delivered as advice only**

## Post-Review

- [ ] All user questions answered or recorded as open
- [ ] Accepted coverage-gap recommendations recorded for follow-up
- [ ] Security-review agent started if the user requested it
- [ ] Any fix work confirmed as a SEPARATE task — never silently merged into the review

## Review Etiquette

**DO:** be specific · give rationale · acknowledge good work · ask questions instead of assuming · focus on code, never the author

**DON'T:** nitpick formatting (the formatter owns it) · block on opinion without evidence · skip phases because "it looks fine" · assume tests pass without running · review security (out of scope) · edit the code under review
