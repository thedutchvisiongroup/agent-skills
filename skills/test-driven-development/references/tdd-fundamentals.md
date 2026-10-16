# TDD Fundamentals

Read this during Mode A. An implementer owns Red–Green–Refactor. A direct tests-only specialist stops at its production boundary; delegated specialists review afterward, never execute separate Red/Green stages.

## The Three Laws of TDD (Uncle Bob)

1. You MUST write a failing test BEFORE you write any production code.
2. You MUST NOT write more of a test than is sufficient to fail (or fail to compile).
3. You MUST NOT write more production code than is sufficient to make the currently failing test pass.

These form the **nano-cycle** (second-by-second). The **micro-cycle** is Red → Green → Refactor (minute-by-minute, once per complete test).

## Red-Green-Refactor (one implementation worker)

Use vertical slices: one behavior, its test, minimal implementation and verification, then the next behavior. Outline future cases in a test list, not a bulk test implementation.

### RED — Write one failing test
- Write ONE minimal test for ONE behavior. A clear name that describes behavior, not "test1".
- Use real code. Avoid mocks unless the dependency is a genuine seam (see `test-doubles.md`).
- The test expresses approved behavior; it is an executable specification claim, not authority to invent requirements.

### Verify RED (MANDATORY — never skip)
Run the test and confirm:
- It fails for the missing behavior or an explicitly specified public API, including a corresponding compilation failure. A bad fixture/import path, typo or missing test dependency is invalid setup, not Red.
- The **failure message** is what you expect.
- It fails because the **feature is missing**, not because of a typo or wrong import.

Investigate new-behavior/reproduction tests that pass immediately. Characterization intentionally preserves existing behavior and need not be Red. Capture expected failure commands/output before new implementation.

### GREEN — Implement the current behavior
Write minimal production code for approved behavior, then run focused tests and regressions. Never weaken tests to pass. Justify incorrect expectations against the specification and submit corrections to independent review.

### REFACTOR — Improve local structure while Green
Clarify names and test/source structure inside role/task scope; rerun covering tests and avoid unrelated cleanup. Verify the relevant full suite at batch completion; reuse applicable unchanged-revision evidence.

### Tests-only role boundary
A direct specialist delivers verified Red and reports required production behavior/seams to the user/implementer, never implements them. This role boundary does not impose agent swaps on the normal implementation cycle.

## Test-List First (Martin Fowler)

Before the first RED, write a list of test cases. Sequence them to drive quickly to the salient design points. Add to the list as new cases occur during the cycle. Picking the right next test is a skill — start with the simplest case that teaches you something, then triangulate.

## Triangulation

When you have only one test, the simplest passing implementation is often a constant (`return 3`). **Triangulate**: write a second test with different inputs that forces a general implementation. Only then generalize. Triangulation is how Chicago/classical TDD drives out general algorithms from specifics.

## Minimal Code (the Green principle)

Implement current approved behavior simply and completely, without speculative features/options/abstractions. Minimal never means hardcoding observed examples while ignoring the contract; triangulate and exercise boundaries.

## Good vs Bad Tests (language-neutral shape)

| Quality | Good | Bad |
|---------|------|-----|
| **Minimal** | One behavior. "and" in the name? Split it. | `validates email and domain and whitespace` |
| **Clear** | Name describes behavior | `test1`, `test_process` |
| **Honest** | Asserts on real outcomes | Asserts on mock data |
| **Deterministic** | No wall-clock, no unseeded random, no real network | Sleeps, `Date.now()`, real HTTP |

## Exceptions (approve before execution)

- Throwaway prototypes — characterize instead.
- Generated code — test the seam, not the generated output.
- Pure configuration files — usually not unit-tested; integration-test the effect.

Record reason, scope and alternative checks in the approved plan. New-test and independent test-review exceptions are separate decisions, each explicitly approved.

## Exceptions Are Not Loopholes

"Skip TDD just this once" is rationalization. If you find yourself thinking it, stop and return to RED. The discipline is the value.

## See Also

- `test-patterns.md` — schools (Chicago vs London), characterization tests, property-based testing.
- `assertion-quality.md` — assertion strength, naming, AAA/Given-When-Then.
- `test-doubles.md` — when a mock is unavoidable (a genuine seam).
