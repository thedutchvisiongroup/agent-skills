# Test Patterns

Read this during Mode A (write new tests) when choosing a testing approach. Language-agnostic patterns — for language-specific idioms (framework syntax), research online per `online-research-protocol.md`.

## Two Schools of TDD

### Chicago / Detroit / Classical (Kent Beck)
- **State-based** verification — assert on return values and observable state.
- **Inside-out** (bottom-up): build from the leaf/domain objects up to the outside.
- **Minimal mocking** — use real collaborators; double only volatile seams.
- **Emergent design** — let the tests drive the design; triangulate from specifics.
- Strong for: core domain logic, pure functions, algorithms.

### London / Mockist (Freeman & Pryce)
- **Interaction-based** verification — assert on collaborations via mocks.
- **Outside-in** (top-down): start from the outermost behavior (UI/API), mock dependencies, then descend, replacing mocks with real implementations.
- **Interface discovery** — mocks reveal the collaborators you wish you had (responsibility-driven design, "Tell, Don't Ask").
- Strong for: service boundaries, integration points, when the design of interactions is the question.

### Hybrid (most effective in practice)
- London at **service boundaries and integration points** (where volatility lives).
- Chicago for **core domain logic** (where state matters and mocking hurts).
- Outside-in to discover interfaces, inside-out to fill in the domain.

## Inside-Out vs Outside-Out (orthogonal to classical/mockist)
- Inside-out / outside-in is about **applicative layers** (where you start).
- Classical / mockist is about **code dependencies** (how you isolate).
- You can mix: e.g., outside-in sequencing with classical (state-based) verification.

## Triangulation (classical)
With one test, the simplest passing implementation is often a constant (`return 3`). Write a second test with different data to force a general solution (`return a + b`). Only then generalize. Triangulation drives general algorithms from concrete examples — but do not overdo it; two tests usually suffice to justify generalization.

## Characterization Tests (for existing code)
When code has no tests or behavior is unclear, **characterize** current behavior:
1. Write a test that captures what the code *currently* does (warts and all).
2. Run it; if it fails, your assumption about behavior was wrong — fix the test, not the code.
3. These tests lock in behavior so you can refactor safely (production refactoring is still out of scope for this skill — you only provide the safety net).
Characterization tests are the entry point for legacy code without tests.

## Golden Master / Snapshot / Approval Tests
For complex output (large structures, formatted text, reports):
1. Capture current output as the "golden master".
2. Future runs compare against it; diffs flag unintended changes.
Use for: serializers, formatters, migrations, anything with large structured output. Beware: a golden master that nobody can read is a mystery guest (see `test-smells.md`) — keep masters small and reviewable.

## Parameterized / Table-Driven Tests
One test, many inputs — replaces loops-in-tests (a smell: a loop over an empty list asserts nothing).
- Python: `@pytest.mark.parametrize`
- JS/TS: `it.each` / `test.each`
- .NET: `[Theory]` + `[InlineData]`
- Go: table-driven `t.Run` subtests
One behavior, many examples. Name each row. Keep rows independent.

## Property-Based Testing & Fuzzing
Example-based tests check specific cases; **property-based** tests state an invariant and let a generator produce hundreds of inputs.
- State a **property** ("for any sorted list, `binary_search(x)` returns the index iff `x` is present").
- The library generates inputs, shrinks failures to minimal counterexamples.
- Tools: **Hypothesis** (Python), **QuickCheck** (Haskell, origin), **fast-check** (JS/TS), **FsCheck** (.NET), **jqwik** (Java), **proptest** (Rust).
- **Fuzzing** is the security-flavored cousin: random inputs looking for crashes/hangs; long-running, often in CI. Use for parsers, deserializers, security-sensitive code.

When to reach for it: pure functions, data structures, serializers, anything with a true invariant. Property testing can *replace* example-based tests; fuzzing *supplements* them.

## BDD / Given-When-Then
Behavior-Driven Development expresses scenarios in plain language:
```
Given a user with 100 shares
When they sell 20
Then they have 80 shares
```
- **Given-When-Then** (Dan North) maps 1:1 to **Arrange-Act-Assert** (Bill Wake) and the **Four-Phase Test** (Meszaros: Setup, Exercise, Verify, Teardown).
- Gherkin (Cucumber/Behave) makes scenarios executable and shared with non-devs.
- BDD is **complementary** to TDD: BDD for high-level behavior alignment with stakeholders; TDD for the units beneath. Use BDD when cross-functional alignment matters; TDD for code correctness.

## Fixtures: Object Mother & Test Data Builder
Shared setup grows into a "general fixture" smell. Two patterns keep it manageable:
- **Object Mother** — a factory of named, ready-made test objects (`Mother.userWithThreeOrders()`). Good for a small stable set.
- **Test Data Builder** — fluent, composable, overridable per test (`UserBuilder().withRole('admin').build()`). Good when each test needs a slightly different object.
Extract these only when duplication is real and the extraction keeps each test readable. Over-abstracted tests become mystery guests.

## Four-Phase Test (Meszaros)
1. **Setup** (Given) — establish preconditions.
2. **Exercise** (When) — invoke the unit under test.
3. **Verify** (Then) — assert expected outcomes/interactions.
4. **Teardown** — release resources (often auto via framework fixtures).

Keep Setup small and visible; one Exercise; specific Verify; reliable Teardown.

## Choosing a Pattern (quick guide)

| Situation | Pattern |
|-----------|---------|
| New feature, clear logic | Chicago classical, triangulate |
| New feature, design of interactions unclear | London outside-in |
| Legacy code, no tests | Characterization tests first |
| Large formatted output | Golden master / approval |
| Many input variants of one behavior | Parameterized / table-driven |
| Pure function with an invariant | Property-based testing |
| Parser/deserializer/security path | Add fuzzing |
| Cross-functional scenario alignment | BDD / Given-When-Then |

## See Also
- `tdd-fundamentals.md` — the Red-Green-Refactor cycle and the handoff.
- `test-doubles.md` — what to mock at the seams.
- `assertion-quality.md` — structuring the Verify phase.
