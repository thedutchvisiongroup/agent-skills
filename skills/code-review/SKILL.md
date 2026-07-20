---
name: code-review
description: Performs comprehensive code reviews including linting, testing, logic analysis, and test coverage checks. Use when reviewing pull requests, validating code changes, or performing pre-merge quality checks. Covers static analysis, test execution, coverage gaps, security patterns, and architectural consistency. Always asks clarifying questions when issues are found.
---

# Comprehensive Code Review

## The Iron Law

```
NO REVIEW IS COMPLETE WITHOUT RUNNING: LINT, TESTS, AND LOGIC CHECKS
```

A code review that only reads code is not a review. It is a glance.

**You MUST execute all verification steps before providing your review.**

## Before You Start

You MUST confirm the following before beginning review:

- [ ] **Scope**: What files/changes are being reviewed?
- [ ] **Context**: What is the purpose of this change? (feature, fix, refactor)
- [ ] **Test commands**: How do you run tests and lints in this project?
- [ ] **Coverage expectations**: Is there a coverage threshold or config?

**If any are unclear, ASK the user before proceeding.**

## Overview

Code review is not just reading diff. It is systematic verification that code:

1. **Works** — tests pass, logic is correct
2. **Conforms** — lints clean, style consistent
3. **Is complete** — edge cases handled, tests exist, coverage adequate
4. **Is safe** — no security issues, no data leaks, no regressions

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

```
STOP. Do you understand the change?
- [ ] Yes, I know what this change does
- [ ] Yes, I know why it was made
- [ ] Yes, I know which files are critical
- [ ] Yes, I know what tests exist
If any box is unchecked: read more context before reviewing code.
```

### Phase 2: Run Static Analysis (ALWAYS)

**You MUST run linters and static analysis. NO EXCEPTIONS.**

1. **Discover Available Tools**

   Check for configuration files:
   - `package.json` → `npm run lint`, `npm run typecheck`
   - `pyproject.toml` → `ruff`, `mypy`, `pylint`
   - `Makefile` → `make lint`, `make check`
   - `.eslintrc*` → `eslint`
   - `Cargo.toml` → `cargo clippy`
   - `go.mod` → `golangci-lint`

2. **Run Linting**

   ```bash
   # Detect and run project linter
   # Examples:
   npm run lint
   ruff check .
   cargo clippy
   golangci-lint run
   ```

3. **Run Type Checking**

   ```bash
   # If available:
   npm run typecheck
   mypy .
   cargo check
   ```

4. **Run Formatting Check**

   ```bash
   # If available:
   npm run format:check
   ruff format --check .
   cargo fmt --check
   ```

5. **Report ALL Issues**

   - List every lint error/warning
   - List every type error
   - List every formatting violation
   - Do NOT fix silently — report to user

```
STOP. Did you run all static analysis?
- [ ] Yes, I ran the linter
- [ ] Yes, I ran the type checker (if available)
- [ ] Yes, I ran the formatter check (if available)
- [ ] Yes, I reported all issues
If any box is unchecked: GO BACK and run them.
```

### Phase 3: Run Tests (ALWAYS)

**You MUST run the test suite. NO EXCEPTIONS.**

1. **Discover Test Framework**

   Check for configuration files:
   - `package.json` → `npm test`, `npm run test`
   - `pyproject.toml` → `pytest`
   - `Makefile` → `make test`
   - `Cargo.toml` → `cargo test`
   - `go.mod` → `go test ./...`

2. **Run Full Test Suite**

   ```bash
   # Detect and run project tests
   # Examples:
   npm test
   pytest
   cargo test
   go test ./...
   ```

3. **Analyze Results**

   - How many tests passed/failed?
   - Are there skipped tests? Why?
   - Are there new test failures?
   - Are flaky tests masking real failures?

4. **If Tests Fail**

   **STOP REVIEW. Tests must pass before code review continues.**

   - Report which tests failed
   - Provide the failure messages
   - Ask: "Should I fix these, or are they known failures?"

5. **Check for Missing Tests**

   - New functions without tests?
   - New branches without test coverage?
   - Edge cases not tested?
   - Error paths not tested?

```
STOP. Did you run the tests?
- [ ] Yes, I ran the full test suite
- [ ] Yes, I know which tests passed/failed
- [ ] Yes, I identified missing test coverage
If any box is unchecked: GO BACK and run them.
```

### Phase 4: Logic and Correctness Review

**Now that automated checks pass, review the actual code logic:**

1. **Read Every Changed Line**

   - Don't skim diffs
   - Understand each change in context
   - Check surrounding code for consistency

2. **Check for Logic Errors**

   See `references/logic-patterns.md` for common patterns.

   - **Off-by-one errors** — Loop bounds, array indices, range checks
   - **Null/undefined handling** — Missing null checks, optional chaining
   - **Boolean logic** — De Morgan's law violations, inverted conditions
   - **Race conditions** — Shared mutable state, async ordering
   - **Resource leaks** — Unclosed files, connections, streams
   - **Error swallowing** — Empty catch blocks, ignored errors

3. **Check Edge Cases**

   - Empty input (null, undefined, empty array, empty string)
   - Boundary values (0, 1, -1, MAX_INT, MIN_INT)
   - Large inputs (performance, memory)
   - Concurrent access (if applicable)
   - Invalid input (wrong types, malformed data)

4. **Check Error Handling**

   - Are errors caught appropriately?
   - Are error messages helpful?
   - Are errors propagated correctly?
   - Is cleanup performed on error?

5. **Check Security Patterns**

   See `references/security-patterns.md` for details.

   - **Input validation** — All user input validated?
   - **SQL injection** — Parameterized queries used?
   - **XSS** — Output properly escaped?
   - **Auth checks** — Permissions verified?
   - **Secrets** — No hardcoded credentials?
   - **Sensitive data** — Properly masked in logs?

6. **Check Performance**

   - O(n²) loops that could be O(n)?
   - N+1 query patterns?
   - Missing indexes?
   - Unnecessary allocations?
   - Missing caching where appropriate?

7. **Check Architectural Consistency**

   - Does this follow existing patterns?
   - Does this introduce new patterns without justification?
   - Is this the right layer for this logic?
   - Are responsibilities properly separated?

### Phase 5: Test Coverage Analysis (ALWAYS)

**You MUST check test coverage. NO EXCEPTIONS.**

1. **Discover Coverage Tools**

   Check for configuration:
   - `package.json` → `npm run test:coverage`, `jest --coverage`
   - `pyproject.toml` → `pytest --cov`
   - `Makefile` → `make coverage`
   - `Cargo.toml` → `cargo tarpaulin`

2. **Run Coverage Analysis**

   ```bash
   # Detect and run coverage
   # Examples:
   npm run test:coverage
   pytest --cov=src --cov-report=term-missing
   cargo tarpaulin
   ```

3. **Analyze Coverage Gaps**

   - Which changed files have LOW coverage?
   - Which new functions are NOT covered?
   - Which branches are NOT tested?
   - Which error paths are NOT covered?

4. **Report Coverage Findings**

   List every coverage gap found:

   ```
   File: src/auth/login.py
   - Line 45-50: Login validation not tested
   - Line 67: Error path for invalid credentials not tested
   - Line 89: Token refresh logic has no tests

   File: src/utils/parser.py
   - Line 23: Empty input handling not tested
   - Line 34-38: Malformed input error path not tested
   ```

5. **Ask About Coverage Gaps**

   **For each coverage gap, ASK the user:**

   - "Is this gap intentional?"
   - "Should I add tests for this?"
   - "Is this covered by integration tests elsewhere?"

```
STOP. Did you check test coverage?
- [ ] Yes, I ran the coverage tool
- [ ] Yes, I identified all coverage gaps
- [ ] Yes, I asked the user about each gap
If any box is unchecked: GO BACK and run coverage.
```

### Phase 6: Synthesize Review

**After completing all phases, provide a comprehensive review:**

1. **Summary**

   Brief overview of the change and your assessment.

2. **Automated Check Results**

   ```
   Lint:      ✓ PASS (0 errors, 0 warnings)
   Types:     ✓ PASS (0 errors)
   Tests:     ✓ PASS (42/42 passed)
   Coverage:  ⚠ 78% (3 gaps identified)
   ```

3. **Critical Issues** (MUST fix before merge)

   - Issue 1: [description] — [file:line]
   - Issue 2: [description] — [file:line]

4. **Warnings** (SHOULD fix, but not blocking)

   - Warning 1: [description] — [file:line]
   - Warning 2: [description] — [file:line]

5. **Suggestions** (Consider, optional)

   - Suggestion 1: [description]
   - Suggestion 2: [description]

6. **Coverage Gaps** (with user questions)

   - Gap 1: [description] — [file:line] — "Is this intentional?"
   - Gap 2: [description] — [file:line] — "Should I add tests?"

7. **Positive Observations**

   - What was done well?
   - Good patterns followed?
   - Clean abstractions?

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "LGTM, looks fine" — You didn't run checks
- "Tests probably pass" — You didn't verify
- "I don't need to run lint" — You're skipping Phase 2
- "Coverage is fine, I trust the author" — You didn't check
- "This is too simple to break" — Simple changes break things
- "The CI will catch it" — Review should catch issues before CI
- "I'll just read the diff" — Reading is not reviewing
- "I don't understand but it looks right" — Ask questions

**ALL of these mean: STOP. Return to Phase 1.**

## User Signals You're Doing It Wrong

**Watch for these redirections:**
- "Did you actually run the tests?" — You assumed without running
- "What about the lint errors?" — You skipped Phase 2
- "Is that all the coverage?" — You didn't check thoroughly
- "What about edge case X?" — You missed Phase 4.3
- "That's not what the change does" — You didn't understand Phase 1

**When you see these:** STOP. Return to the relevant phase.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Tests are slow, skip them" | Slow tests are better than broken code. Run them. |
| "Lint is noisy, ignore warnings" | Warnings exist for a reason. Report them all. |
| "Coverage doesn't matter for this" | All code matters. Check coverage. |
| "Author said tests pass" | Verify independently. Trust but verify. |
| "It's a small change" | Small changes cause big outages. Review thoroughly. |
| "I'll just check the critical parts" | Non-critical parts hide bugs too. Check everything. |
| "This pattern is fine, I've seen it before" | Past patterns can be wrong. Evaluate objectively. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Understand** | Read description, identify files, check context | Know what and why |
| **2. Static Analysis** | Run lint, typecheck, format check | All clean or issues reported |
| **3. Tests** | Run full test suite, check for failures | All pass or failures reported |
| **4. Logic** | Review each line, check edges, security, performance | No logic errors found |
| **5. Coverage** | Run coverage, identify gaps, ask user | All gaps identified and discussed |
| **6. Synthesize** | Compile findings, categorize issues | Comprehensive review delivered |

## Supporting Techniques

These techniques are available in this directory:

- **`references/logic-patterns.md`** — Common logic error patterns to watch for
- **`references/security-patterns.md`** — Security review checklist
- **`references/coverage-strategies.md`** — How to identify and address coverage gaps
- **`references/review-checklist.md`** — Complete checklist for thorough reviews

Base directory for this skill: /home/abej/proj/agent-skills/skills/code-review
Relative paths in this skill (e.g., references/) are relative to this base directory.
