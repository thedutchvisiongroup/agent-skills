# TDD Fundamentals

Read this during Mode A (write new tests). This skill drives Red-Green-Refactor on the **test side only** — it never writes production code.

## The Three Laws of TDD (Uncle Bob)

1. You MUST write a failing test BEFORE you write any production code.
2. You MUST NOT write more of a test than is sufficient to fail (or fail to compile).
3. You MUST NOT write more production code than is sufficient to make the currently failing test pass.

These form the **nano-cycle** (second-by-second). The **micro-cycle** is Red → Green → Refactor (minute-by-minute, once per complete test).

## Red-Green-Refactor (with the handoff)

Because this skill never writes production code, the cycle is adapted:

### RED — Write one failing test
- Write ONE minimal test for ONE behavior. A clear name that describes behavior, not "test1".
- Use real code. Avoid mocks unless the dependency is a genuine seam (see `test-doubles.md`).
- The test IS the specification — it expresses the desired behavior.

### Verify RED (MANDATORY — never skip)
Run the test and confirm:
- It **fails** (not errors — errors mean a setup/compile problem, fix and re-run).
- The **failure message** is what you expect.
- It fails because the **feature is missing**, not because of a typo or wrong import.

A test that passes immediately tests existing behavior (or nothing). Fix the test. A test you didn't watch fail proves nothing — you don't know it can catch the bug.

### HANDOFF (NOT Green — you never write production code)
The failing test is the specification. Report to the user/another agent: "production code is now needed to make this test pass — it must [behavior the test expresses]." Do NOT write the production code. When the user/another agent supplies it, proceed to Verify Green (Phase 5).

### GREEN-verify (when production code is supplied by the user/another agent)
Run the test. Confirm it passes AND the rest of the suite still passes. If it fails, the production code is wrong — report back. Do not fix production code.

### REFACTOR (tests only)
After green, refactor the **test code** for clarity: remove duplication, improve names, extract helpers. Keep tests green. **Do not refactor production code** — that is out of scope; report production refactor opportunities as a handoff note.

## Test-List First (Martin Fowler)

Before the first RED, write a list of test cases. Sequence them to drive quickly to the salient design points. Add to the list as new cases occur during the cycle. Picking the right next test is a skill — start with the simplest case that teaches you something, then triangulate.

## Triangulation

When you have only one test, the simplest passing implementation is often a constant (`return 3`). **Triangulate**: write a second test with different inputs that forces a general implementation. Only then generalize. Triangulation is how Chicago/classical TDD drives out general algorithms from specifics.

## Minimal Code (the Green principle, for the handoff)

When you hand off, the production-code implementer should write the **simplest** code that passes the current test — no anticipated features, no options object "for the future", no premature abstraction. Over-engineering breaks TDD's feedback. If the implementer adds behavior no test demands, that is a finding worth reporting.

## Good vs Bad Tests (language-neutral shape)

| Quality | Good | Bad |
|---------|------|-----|
| **Minimal** | One behavior. "and" in the name? Split it. | `validates email and domain and whitespace` |
| **Clear** | Name describes behavior | `test1`, `test_process` |
| **Honest** | Asserts on real outcomes | Asserts on mock data |
| **Deterministic** | No wall-clock, no unseeded random, no real network | Sleeps, `Date.now()`, real HTTP |

## When NOT to do test-first (ask the user)

- Throwaway prototypes — characterize instead.
- Generated code — test the seam, not the generated output.
- Pure configuration files — usually not unit-tested; integration-test the effect.

## Exceptions Are Not Loopholes

"Skip TDD just this once" is rationalization. If you find yourself thinking it, stop and return to RED. The discipline is the value.

## See Also

- `test-patterns.md` — schools (Chicago vs London), characterization tests, property-based testing.
- `assertion-quality.md` — assertion strength, naming, AAA/Given-When-Then.
- `test-doubles.md` — when a mock is unavoidable (a genuine seam).
