# Assertion Quality

Read this during Modes A/B/C. The assertion is the heart of the test. A test with a weak assertion is coverage theater — it runs the code but verifies nothing.

## The Mutation Mindset (the core test)

**Would this test FAIL if the production code were broken?**

Apply it before writing (Mode A) and during review (Mode B): mentally mutate the code under test —
- flip a condition (`>` → `>=`, `&&` → `||`)
- delete a line
- change a boundary (`<` → `<=`)
- swap a return value
- invert an error check

and ask: **does any test fail?** If not, the test does not cover that behavior. A "surviving mutant" is a real gap. Mutation-testing tools automate this (see `coverage-and-mutation.md`); the manual mindset is always available.

## Signs a Test Can't Fail (flag as `issue`)

- No assertions at all, or assertions only on constants
- Asserts merely that no exception was thrown
- Mocks configured to return exactly what the code produces (circular)
- Assertions verify mocked data, not behavior
- Tautologies (`assertTrue(true)`, `expect(true).toBe(true)`)

## One Behavior per Test

- One test, one behavior. "and" in the test name? Split it.
- Multiple assertions are fine **when they verify a single behavior** (e.g. "returns a valid user" might assert `id`, `name`, `email` — one behavior).
- If two assertions can fail independently for different reasons, that's two behaviors → two tests.

## Specific, Not Loose

| Weak | Strong |
|------|--------|
| `toBeTruthy()` / `assert x` | `toBe(3)`, `assert x == 3` |
| `raises(Exception)` | `raises(ValidationError, match="page_size")` |
| `toContain(something)` when one-of-many | `toHaveLength(1)` + `toBe(theItem)` |
| `expect(result).toBeDefined()` | `expect(result.id).toBe(42)` |
| Identity values (`f(5, 1)` → `5`) | Non-identity values (`f(5, 3)` → `15`) |

Identity values (`1` is the multiplicative identity) let arithmetic mutations survive — mutants change `*` to `/` and the test still passes. Choose inputs where the expected output is sensitive to the operation.

## Assert on Outcomes, Not Implementation

- Assert on **return values, observable state, and real side effects** — not on which internal helper was called.
- Exception: assert on an interaction **when the interaction IS the contract** ("sends exactly one email", "retries exactly 3 times") — use a mock/spy there (see `test-doubles.md`).
- Don't assert on calls to internal helpers; the test should survive an internal refactor that preserves behavior.

## Structure: Arrange-Act-Assert / Given-When-Then

Two names, one shape (Meszaros's Four-Phase Test):

| Phase | AAA (Wake) | GWT (North/BDD) | Meszaros |
|-------|------------|-----------------|----------|
| Precondition | Arrange | Given | Setup |
| Exercise | Act | When | Exercise |
| Verify | Assert | Then | Verify |
| Cleanup | (auto) | (auto) | Teardown |

- Keep **Arrange small and visible**. Big hidden setup = mystery guest.
- **One Act** per test. Multiple acts = eager test.
- Specific **Verify**. Then stop.

## Naming

Names describe behavior, not implementation:
- ✅ `rejects_negative_amounts`, `returns_zero_for_empty_list`, `retries_three_times_on_transient_error`
- ❌ `test_transfer_1`, `testCalculator`, `test_process`

Conventions vary by stack — match the suite (`MethodName_StateUnderTest_ExpectedBehavior`, BDD `should ...`, `it ...`, snake_case). Detect the convention in Phase 1; validate in Phase 3.

## AAA Edge Cases

- **Expected-exception tests**: assert the **type AND message** (`raises(ValidationError, match="page_size")`), not just "something threw" — otherwise any throw passes the test, including the wrong one.
- **Async tests**: `await` the act; assert after completion. Asserting on a pending promise is a no-op.
- **No-return side effects**: assert on observable state (DB row, captured email, emitted event) — not on "no exception".

## Assertion Roulette Prevention

- One behavior per test (above) is the main fix.
- If multiple assertions are needed, use named/described assertions where the framework supports it (`expect(x, 'the total').toBe(3)`, `assert x == 3, "total"`), so failures point at the behavior.

## DRY vs Readability in Tests

**Clarity beats DRY in tests.** Each test tells its own short story; a reader understands it without jumping to shared helpers.
- Some setup duplication is fine and often good.
- Extract shared setup (builders, factories, `beforeEach`) only when it genuinely repeats AND keeps each test readable.
- Over-abstracted tests — deep base-class hierarchies, setup defined files away — hide intent and create mystery guests.

## Checklist

- [ ] Every test would FAIL if the covered code were broken (mutation mindset applied)
- [ ] No tests that assert nothing, constants, or only mocks
- [ ] One behavior per test; named for that behavior
- [ ] Assertions specific (no `toBeTruthy`, no identity values for arithmetic)
- [ ] Expected-exception tests assert type AND message
- [ ] Assert on outcomes, not implementation (unless the interaction is the contract)
- [ ] AAA/GWT visible; one Act per test
- [ ] Setup visible; duplication intentional

## See Also
- `test-smells.md` — assertion roulette, eager test, redundant assertions.
- `coverage-and-mutation.md` — mutation testing tools that automate the mutation mindset.
- `test-doubles.md` — when asserting on an interaction (the contract) is correct.
