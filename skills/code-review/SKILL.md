---
name: code-review
description: Performs advisory-only, language-agnostic code reviews. Runs linters, formatters, and tests, then analyzes logic, design (DRY, SOLID, YAGNI), complexity, naming, dead code, performance, and documentation. Use when reviewing pull requests, validating code changes, or performing pre-merge quality checks. The reviewer NEVER modifies code — it only reports findings. Test-suite quality (flakiness, test smells, assertion strength, coverage gaps, mutation mindset) is out of scope; the reviewer hands test-quality off to the test-driven-development skill. Security review is out of scope; the reviewer asks the user whether a separate security-review agent should be started.
---

# Comprehensive Code Review

## The Iron Law

```
NO REVIEW IS COMPLETE WITHOUT RUNNING: LINTERS, FORMATTERS, AND TESTS
THE REVIEWER ADVISES. THE REVIEWER NEVER EDITS CODE.
TEST-SUITE QUALITY IS OUT OF SCOPE. ALWAYS HAND IT OFF TO test-driven-development.
SECURITY IS OUT OF SCOPE. ALWAYS ASK ABOUT A SEPARATE SECURITY REVIEW.
```

A code review that only reads code is not a review. It is a glance.

**You MUST execute all verification steps before providing your review.**

## Advisory-Only — Non-Negotiable

- You MUST NEVER edit, fix, refactor, reformat, or "quickly correct" any file under review. **No exceptions.**
- Your ONLY outputs are findings, questions, and recommendations.
- If the user asks you to fix something, that is a NEW task. Finish and deliver the review first, then confirm the fix as separate work.
- "Just this once" does not exist. A reviewer who edits is an author — and authors cannot review their own code.

## Security Is Out of Scope

This skill does NOT perform security review. A dedicated security review is a separate discipline.

- You MUST ask the user in the clarification step whether a separate security-review agent should be started.
- You MUST NOT check for vulnerabilities, injection, auth flaws, or secrets yourself. If you notice something that looks security-relevant, you note it as a handoff trigger — nothing more.
- See Phase 1 for sensitive-path detection, and Phase 6 for the handoff recommendation.

## Test-Suite Quality Is Out of Scope

This skill does NOT review test quality (flakiness, test smells, assertion strength, coverage gaps, mutation mindset). That is the domain of the `test-driven-development` skill.

- You MUST run the test suite (Phase 2) to confirm the suite passes — but you do NOT assess test quality yourself.
- You MUST ask the user in the clarification step whether a separate `test-driven-development` agent should be started for a test-quality review.
- If you notice something that looks test-quality-relevant (flaky tests, skipped tests, over-mocking, weak assertions, coverage gaps), note it as a **test-quality handoff trigger** in your final report (Phase 6) — nothing more.
- The coverage thresholds and gap analysis that previously lived in this skill have moved to `test-driven-development`; this skill no longer carries coverage config or coverage-gap questions.

## Before You Start

You MUST confirm the following before beginning review:

- [ ] **Scope**: What files/changes are being reviewed?
- [ ] **Context**: What is the purpose of this change? (feature, fix, refactor)
- [ ] **Commands**: How do you run lints, formatters, and tests in this project? (You will also detect this yourself in Phase 2 — ask if detection fails.)
- [ ] **Security review**: Ask: "Security is out of scope for this review. Do you want me to start a separate security-review agent in parallel?" — ALWAYS ask this.
- [ ] **Test-quality review**: Ask: "Test-suite quality (flakiness, smells, assertion strength, coverage gaps) is out of scope for this review. Do you want me to start a separate `test-driven-development` agent to review the tests?" — ALWAYS ask this. (Coverage thresholds are now owned by `test-driven-development`.)

**If any are unclear, ASK the user before proceeding.**

## Overview

Code review is not just reading a diff. It is systematic verification that code:

1. **Works** — tests pass, logic is correct
2. **Conforms** — lints clean, formatting verified, style consistent
3. **Is complete** — edge cases handled (test-suite quality itself is handed off to `test-driven-development`)
4. **Is maintainable** — DRY, SOLID where relevant, no dead code, documented, no needless complexity

**Core principle:** ALWAYS verify, never assume. "Looks correct" is not verified.

## When to Use

Use for ANY code change review:
- Pull request reviews
- Pre-merge validation
- Post-merge audit
- Refactoring validation
- Dependency updates
- Configuration changes

**Use this ESPECIALLY when:**
- The change is large or touches multiple files
- The change affects critical paths (auth, payments, data)
- The change modifies test files
- The change introduces new dependencies
- You're tempted to say "LGTM" after a quick scan

**Don't skip when:**
- Change seems simple (simple changes break things too)
- It's a "quick fix" (quick fixes cause most outages)
- Tests are "probably fine" (verify, don't guess)
- The author is experienced (everyone makes mistakes)

## When NOT to Use

- **Test-suite quality reviews** — Out of scope. Recommend the `test-driven-development` skill instead (flakiness, test smells, assertion strength, coverage gaps, mutation testing).
- **Security audits** — Out of scope. Recommend a dedicated security-review agent instead.
- **Trivial formatting-only changes** — If only whitespace/formatting changed with no logic impact
- **Generated code** — Auto-generated files that aren't hand-edited
- **Vendor code** — Third-party libraries (review the dependency, not the code)
- **Documentation-only changes** — Unless code examples in docs need verification

## The Six Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Understand the Change

**BEFORE reviewing code, understand what you're reviewing:**

1. **Read the Description**
   - What is this change supposed to do?
   - What problem does it solve?
   - What is the expected behavior?

2. **Identify Changed Files**
   - How many files changed?
   - What types of changes? (new files, modifications, deletions)
   - Which files are critical vs. supporting?

3. **Check for Related Changes**
   - Are there related PRs or issues?
   - Does this depend on other changes?
   - Are there follow-up changes needed?

4. **Understand the Test Strategy**
   - What tests were added/modified?
   - What is NOT tested?
   - Are there integration tests?

5. **Detect Sensitive Paths** (security handoff trigger)
   - Scan the changed files for: authentication, authorization, payments, personal data, cryptography, secrets, file uploads, external input handling, permission checks.
   - If found: note them. You will NOT review them for security — but you MUST include a security-review recommendation in your final report (Phase 6).

```
STOP. Do you understand the change?
- [ ] Yes, I know what this change does
- [ ] Yes, I know why it was made
- [ ] Yes, I know which files are critical
- [ ] Yes, I know what tests exist
- [ ] Yes, I noted any sensitive paths (for handoff only)
If any box is unchecked: read more context before reviewing code.
```

### Phase 2: Run Automated Checks (ALWAYS)

**You MUST run linters, formatters, type checkers, and tests. NO EXCEPTIONS.**

1. **Discover Available Tools**

   Detect the project's tooling from configuration files. Also check CI configuration (e.g. `.github/workflows`, `.gitlab-ci.yml`) — it reveals the exact commands the project considers authoritative.

   | Config file | Typical commands |
   |-------------|------------------|
   | `package.json` | `npm run lint`, `npm run typecheck`, `npm run format:check`, `npm test` |
   | `pyproject.toml` | the project's lint/type/format/test commands |
   | `Makefile` | `make lint`, `make check`, `make test` |
   | `Cargo.toml` | `cargo clippy`, `cargo fmt --check`, `cargo test` |
   | `go.mod` | the project's lint command, `go test ./...` |

2. **Run Everything You Found**
   - Linting
   - Type checking (if available)
   - Formatting check (if available) — run the formatter in CHECK mode only. NEVER apply formatting.
   - Full test suite

3. **If Tooling Is Missing: Detect → Report → Ask**

   - If a category (lint, format, types, or tests) has no detectable tooling, you MUST:
     1. Report it explicitly in your review as "not available"
     2. Ask the user how (or whether) it should be run
   - NEVER skip a category silently.

4. **Report ALL Issues**
   - List every lint error/warning
   - List every type error
   - List every formatting violation
   - Do NOT fix anything — report to the user

5. **If Tests Fail**

   **STOP REVIEW. Tests must pass before code review continues.**

   - Report which tests failed, with failure messages
   - Ask: "Are these known failures, or caused by this change?"
   - Do NOT fix the tests. Do NOT continue reviewing on a red suite without explicit user confirmation.

```
STOP. Did you run all automated checks?
- [ ] Yes, I ran the linter
- [ ] Yes, I ran the type checker (or reported it missing + asked)
- [ ] Yes, I ran the formatter check (or reported it missing + asked)
- [ ] Yes, I ran the full test suite
- [ ] Yes, I reported all issues — and fixed NOTHING
If any box is unchecked: GO BACK and complete them.
```

### Phase 3: Test Suite — Hand Off Quality Assessment

**You run the suite (Phase 2) to confirm it passes. You do NOT assess test quality.**

Test quality — flakiness, test smells, assertion strength, coverage gaps, mutation mindset — is the domain of the `test-driven-development` skill. This skill no longer carries the test-quality catalog, coverage-strategies reference, or coverage-gap questions.

1. **Run the suite** (already done in Phase 2) and report pass/fail counts including skipped/ignored tests.
2. **Flag obvious signals for handoff** (do NOT analyze them): tests marked skipped/ignored without a visible reason, sleeps/wall-clock in tests, unseeded randomness, large skipped count, or a coverage number significantly below what the project configures. List these as one-line handoff triggers — no smell analysis, no coverage-gap questions.
3. **Hand off to `test-driven-development`**: if the user accepted the test-quality review in the Before-You-Start gate, or if Phase 2 flagged obvious signals, invoke the `test-driven-development` agent (via the `task` tool / `tdd-expert` subagent) to perform the test-quality review. Include its outcome in your final report.
4. **If the handoff is not possible or not requested**: include a "Test-quality handoff" section in your final report (Phase 6) listing the flagged signals and recommending the `test-driven-development` agent — no analysis of your own.

```
STOP. Did you handle test quality correctly?
- [ ] Yes, I ran the suite and reported pass/fail + skipped counts
- [ ] Yes, I flagged obvious signals as one-line handoff triggers (no analysis)
- [ ] Yes, I handed off to `test-driven-development` (or recommended it) if triggered
- [ ] Yes, I did NOT perform test-smell/coverage-gap analysis myself
If any box is unchecked: GO BACK. Do not analyze test quality.
```

### Phase 4: Logic and Correctness Review

**Now that automated checks pass, review the actual code logic:**

1. **Read Every Changed Line**
   - Don't skim diffs
   - Understand each change in context — read the whole file when needed, not just the diff hunk
   - Check surrounding code for consistency

2. **Check for Logic Errors**

   See `references/logic-patterns.md` for common patterns.

   - Off-by-one errors, null/undefined handling, boolean logic
   - Race conditions and async ordering
   - Type coercion, boundary issues, floating point

3. **Check Error Handling**

   See `references/error-handling.md` for the full catalog.

   - Error swallowing, resource leaks
   - Propagation and cleanup on error
   - Retries, timeouts, error message quality

4. **Check Edge Cases**
   - Empty input (null, undefined, empty array, empty string)
   - Boundary values (0, 1, -1, MAX, MIN)
   - Large inputs (performance, memory)
   - Concurrent access (if applicable)
   - Invalid input (wrong types, malformed data)

```
STOP. Did you verify correctness?
- [ ] Yes, I read every changed line in context
- [ ] Yes, I checked logic patterns and error handling
- [ ] Yes, I traced the edge cases
If any box is unchecked: GO BACK and verify.
```

### Phase 5: Design and Maintainability Review

**Correct code can still be bad code. Review design with the same rigor as logic.**

1. **DRY and Duplication**

   See `references/design-principles.md`.

   - Is knowledge duplicated (same rule in multiple places)?
   - Nuance: is this harmful duplication, or acceptable look-alike code? The wrong abstraction is costlier than duplication.
   - Are implementations as MINIMAL as the requirement allows?

2. **SOLID (where relevant)**

   See `references/design-principles.md` for per-principle heuristics.

   - Applies to OO-style code. Use judgment for functional/procedural code — do not force OO principles where they don't fit.

3. **YAGNI / Over-Engineering**

   - Speculative generality, unused parameters "for the future", abstractions with a single implementation
   - Solve the problem that exists NOW, not the imagined future one

4. **Complexity**

   See `references/complexity-metrics.md`.

   - Function length, nesting depth, parameter count, cyclomatic/cognitive complexity signals
   - Flag what "can't be understood quickly by code readers"

5. **Naming and Readability**

   See `references/naming-and-readability.md`.

   - Intention-revealing names, magic numbers, misleading names
   - Self-documenting code over comments

6. **Dead Code**

   See `references/dead-code.md`.

   - Unused functions, methods, classes, files, exports, parameters
   - Zombie dependencies, commented-out code, unreachable branches
   - REPORT candidates with evidence. NEVER delete anything.

7. **Performance**

   See `references/performance-review.md`.

   - N+1 patterns, hidden O(n²), repeated I/O in loops, unbounded result sets
   - Flag only clear algorithmic issues — require evidence for anything subtler

8. **Documentation**

   See `references/documentation-review.md`.

   - Public APIs documented (purpose, params, returns, errors)
   - Comments explain WHY, not WHAT
   - README/changelog/migration docs updated when behavior changes

9. **Architectural Consistency**
   - Does this follow existing patterns?
   - Is this the right layer for this logic?
   - Does it introduce new patterns without justification?

```
STOP. Did you review design and maintainability?
- [ ] Yes, I checked DRY, SOLID (where relevant), and YAGNI
- [ ] Yes, I checked complexity, naming, and readability
- [ ] Yes, I searched for dead code and reported candidates
- [ ] Yes, I checked documentation completeness
- [ ] Yes, I checked performance for clear algorithmic issues
If any box is unchecked: GO BACK and complete the review.
```

### Phase 6: Synthesize Review

**After completing all phases, provide a comprehensive review. You advise — the user decides.**

See `references/feedback-format.md` for the full format, labels, and tone guidelines.

1. **Summary** — Brief overview of the change and your assessment.

2. **Automated Check Results**

   ```
   Lint:      ✓ PASS (0 errors, 0 warnings)
   Types:     ✓ PASS (0 errors)
   Format:    ✓ PASS
   Tests:     ✓ PASS (42/42 passed, 0 skipped)
   Coverage:  reported by test-driven-development agent (out of scope here)
   ```

3. **Findings, Labeled** — Every finding gets a Conventional Comments label:

   - `issue (blocking):` — MUST fix before merge
   - `issue (non-blocking):` / `suggestion:` — SHOULD fix or consider
   - `nitpick:` — trivial, preference-based, non-blocking by nature
   - `question:` — you need the author's intent before judging
   - `praise:` — what was done well (include at least one sincere praise)

   Each finding includes: file:line, what, why it matters, and a concrete recommendation.

4. **Test-Quality Handoff**
   - Restate the answer to the Before-You-Start test-quality question.
   - If obvious signals were flagged in Phase 3 (skipped tests, sleeps, low coverage), you MUST explicitly recommend: "The test suite shows [signals]. I did not review test quality. I recommend starting a separate `test-driven-development` agent."
   - If the `test-driven-development` agent was invoked, summarize its outcome here.

5. **Security Handoff**
   - Restate the answer to the Before-You-Start security question.
   - If sensitive paths were detected in Phase 1, you MUST explicitly recommend: "This change touches [auth/payments/user data/...]. I did not review security. I recommend starting a separate security-review agent."

6. **Verdict** (advisory — the user makes the call):
   - `APPROVE` — no blocking findings
   - `COMMENT` — questions or discussion pending
   - `REQUEST CHANGES` — blocking findings present

**Reminder: deliver the review. Do not start fixing anything.**

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "LGTM, looks fine" — You didn't run checks
- "Tests probably pass" — You didn't verify
- "I don't need to run lint" — You're skipping Phase 2
- "These tests look flaky, let me analyze them" — Out of scope. Hand off to `test-driven-development`.
- "Coverage looks low, let me check the gaps" — Out of scope. Hand off to `test-driven-development`.
- "I'll just fix this typo myself" — You NEVER edit code. Report it.
- "The user will appreciate me fixing it" — They asked for a review, not an edit
- "This dead code might be needed later" — Version control keeps history. Report it.
- "Let me quickly check security too" — Out of scope. Recommend a security-review agent.
- "The CI will catch it" — Review should catch issues before CI
- "I'll just read the diff" — Reading is not reviewing

**ALL of these mean: STOP. Return to the relevant phase.**

## User Signals You're Doing It Wrong

**Watch for these redirections:**
- "Did you actually run the tests?" — You assumed without running
- "Why did you change that file?" — You edited code. You NEVER edit code.
- "Did you review the test suite quality?" — Out of scope. Hand off to `test-driven-development`.
- "What about edge case X?" — You missed Phase 4
- "Is any of this code still used?" — You missed dead code in Phase 5
- "I asked about security?" — You reviewed security yourself, or forgot the handoff question
- "What about the test quality / coverage?" — Out of scope. Recommend the `test-driven-development` agent.

**When you see these:** STOP. Return to the relevant phase.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Tests are slow, skip them" | Slow tests are better than broken code. Run them. |
| "Lint is noisy, ignore warnings" | Warnings exist for a reason. Report them all. |
| "Test quality is part of code review" | No — it's a separate discipline. Hand off to `test-driven-development`. |
| "Coverage doesn't matter for this" | Coverage is owned by `test-driven-development`; don't analyze it here. |
| "Tests pass, so they must be good" | Green tests can still be flaky, shallow, or over-mocked. Hand off to `test-driven-development`. |
| "Author said tests pass" | Verify independently. Trust but verify. |
| "It's a small change" | Small changes cause big outages. Review thoroughly. |
| "I'll just fix it quickly" | You advise, you never edit. Report the finding instead. |
| "Duplication is always bad" | The wrong abstraction is costlier. Evaluate objectively. |
| "This pattern is fine, I've seen it before" | Past patterns can be wrong. Evaluate objectively. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Understand** | Read description, identify files, detect sensitive paths | Know what and why; handoff triggers noted |
| **2. Automated Checks** | Run lint, types, format check, tests | All clean or issues reported; nothing fixed |
| **3. Test Handoff** | Run suite, flag obvious signals, hand off quality to `test-driven-development` | Suite confirmed; quality handed off, not self-reviewed |
| **4. Logic** | Every line, logic patterns, error handling, edges | No correctness errors found |
| **5. Design** | DRY, SOLID, YAGNI, complexity, naming, dead code, performance, docs | Maintainability verified |
| **6. Synthesize** | Labeled findings, verdict, test-quality + security handoff | Advisory review delivered; nothing edited |

## Reference Index

Load these files as needed during the matching phase:

| Reference | Read during | Contents |
|-----------|-------------|----------|
| `references/logic-patterns.md` | Phase 4 | Off-by-one, null, boolean, race, coercion, boundaries |
| `references/error-handling.md` | Phase 4 | Swallowing, leaks, propagation, retries, messages |
| `references/design-principles.md` | Phase 5 | DRY nuance, SOLID heuristics, YAGNI, over-engineering |
| `references/complexity-metrics.md` | Phase 5 | Complexity signals, thresholds, remedies |
| `references/naming-and-readability.md` | Phase 5 | Naming heuristics, magic numbers, self-documenting code |
| `references/dead-code.md` | Phase 5 | Unused code, zombie dependencies, safe-removal advice |
| `references/performance-review.md` | Phase 5 | N+1, O(n²), I/O patterns, when to demand benchmarks |
| `references/documentation-review.md` | Phase 5 | Comments, docstrings, README/changelog sync |
| `references/feedback-format.md` | Phase 6 | Conventional Comments, report template, tone |
| `references/review-checklist.md` | All phases | Master checklist for the full review |

> Test-suite quality (flakiness, test smells, assertion strength, coverage gaps, mutation testing) is owned by the `test-driven-development` skill. Do not load test-quality references here — hand off instead.

Base directory for this skill: /root/htdocs/projects-tdvg/agent-skills/skills/code-review
Relative paths in this skill (e.g., references/) are relative to this base directory.
