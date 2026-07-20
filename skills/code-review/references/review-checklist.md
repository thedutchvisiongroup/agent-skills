# Code Review Checklist

## Pre-Review Setup

### 1. Understand Context

- [ ] Read PR description / change summary
- [ ] Understand the problem being solved
- [ ] Check for related issues or PRs
- [ ] Identify the type of change (feature, fix, refactor)

### 2. Identify Scope

- [ ] How many files changed?
- [ ] Which files are critical?
- [ ] Which files are supporting (tests, config)?
- [ ] What's the estimated review time?

## Phase 1: Static Analysis (ALWAYS)

### Linting

- [ ] Run project linter
- [ ] Check for lint errors
- [ ] Check for lint warnings
- [ ] Verify all issues are reported

### Type Checking

- [ ] Run type checker (if available)
- [ ] Check for type errors
- [ ] Verify type annotations are correct

### Formatting

- [ ] Run formatter check (if available)
- [ ] Check for formatting violations
- [ ] Verify consistent style

### Results

```
Lint:      [ ] PASS  [ ] FAIL (___ errors, ___ warnings)
Types:     [ ] PASS  [ ] FAIL (___ errors)
Format:    [ ] PASS  [ ] FAIL (___ violations)
```

## Phase 2: Tests (ALWAYS)

### Test Execution

- [ ] Run full test suite
- [ ] Check for test failures
- [ ] Check for skipped tests
- [ ] Verify test results

### Test Quality

- [ ] Tests cover happy path
- [ ] Tests cover error paths
- [ ] Tests cover edge cases
- [ ] Tests are readable
- [ ] Tests are maintainable

### Results

```
Tests:     [ ] PASS  [ ] FAIL (___ passed, ___ failed, ___ skipped)
```

## Phase 3: Coverage (ALWAYS)

### Coverage Analysis

- [ ] Run coverage tool
- [ ] Check coverage of changed files
- [ ] Identify coverage gaps
- [ ] Prioritize gaps

### Coverage Questions

For each gap:
- [ ] Is this gap intentional?
- [ ] Should tests be added?
- [ ] Is this covered elsewhere?

### Results

```
Coverage:  [ ] PASS (>= ___%)  [ ] FAIL (___%)

Gaps identified:
- File: ___, Lines: ___ — [ ] Intentional  [ ] Needs tests  [ ] Covered elsewhere
- File: ___, Lines: ___ — [ ] Intentional  [ ] Needs tests  [ ] Covered elsewhere
```

## Phase 4: Code Logic

### Correctness

- [ ] Logic is correct
- [ ] No off-by-one errors
- [ ] No null/undefined issues
- [ ] No boolean logic errors

### Edge Cases

- [ ] Empty input handled
- [ ] Boundary values handled
- [ ] Large inputs handled
- [ ] Invalid input handled

### Error Handling

- [ ] Errors caught appropriately
- [ ] Error messages helpful
- [ ] Errors propagated correctly
- [ ] Cleanup on error

### Performance

- [ ] No O(n²) loops where O(n) possible
- [ ] No N+1 query patterns
- [ ] Missing indexes identified
- [ ] Unnecessary allocations avoided

### Security

- [ ] Input validated
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] Auth checks present
- [ ] No hardcoded secrets
- [ ] Sensitive data protected

### Architecture

- [ ] Follows existing patterns
- [ ] Responsibilities separated
- [ ] Right layer for logic
- [ ] No unnecessary coupling

## Phase 5: Code Quality

### Readability

- [ ] Code is self-documenting
- [ ] Names are descriptive
- [ ] Comments explain WHY, not WHAT
- [ ] No magic numbers/strings

### Maintainability

- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Functions are small and focused
- [ ] Classes have single responsibility
- [ ] Easy to modify

### Consistency

- [ ] Follows project style guide
- [ ] Consistent naming conventions
- [ ] Consistent patterns
- [ ] Consistent error handling

## Phase 6: Documentation

### Code Comments

- [ ] Complex logic explained
- [ ] Non-obvious decisions documented
- [ ] Public APIs documented
- [ ] TODOs tracked

### External Documentation

- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] Changelog updated (if needed)
- [ ] Migration guide (if needed)

## Phase 7: Final Review

### Summary

```
Change: [description]
Files: [count] changed

Automated Checks:
- Lint:    [PASS/FAIL]
- Types:   [PASS/FAIL]
- Tests:   [PASS/FAIL]
- Coverage: [PASS/FAIL] (___%)

Issues Found:
- Critical: [count]
- Warnings: [count]
- Suggestions: [count]

Coverage Gaps:
- [count] gaps identified, [count] questions for user

Recommendation:
[ ] APPROVE
[ ] REQUEST CHANGES
[ ] COMMENT
```

### Issue Categories

**Critical (MUST fix):**
- [ ] Logic errors
- [ ] Security vulnerabilities
- [ ] Test failures
- [ ] Missing critical tests

**Warnings (SHOULD fix):**
- [ ] Code quality issues
- [ ] Missing edge case tests
- [ ] Performance concerns
- [ ] Style inconsistencies

**Suggestions (Consider):**
- [ ] Minor improvements
- [ ] Alternative approaches
- [ ] Documentation gaps
- [ ] Refactoring opportunities

## Post-Review

### Documentation

- [ ] Review findings documented
- [ ] Questions for user listed
- [ ] Next steps defined

### Follow-up

- [ ] Critical issues addressed
- [ ] Warnings addressed
- [ ] Coverage gaps discussed
- [ ] User questions answered

## Quick Reference

| Check | Tool | Command |
|-------|------|---------|
| Lint | Varies | `npm run lint`, `ruff check .`, `cargo clippy` |
| Types | Varies | `npm run typecheck`, `mypy .`, `cargo check` |
| Format | Varies | `npm run format:check`, `ruff format --check .` |
| Tests | Varies | `npm test`, `pytest`, `cargo test` |
| Coverage | Varies | `npm run test:coverage`, `pytest --cov` |
| Security | Varies | `npm audit`, `pip audit`, `cargo audit` |

## Review Etiquette

### DO

- Be specific about issues
- Provide examples of fixes
- Acknowledge good work
- Ask questions, don't assume
- Focus on code, not author

### DON'T

- Nitpick style (let linter handle it)
- Block on opinions without evidence
- Review when tired or rushed
- Skip phases because "it looks fine"
- Assume tests pass without running
