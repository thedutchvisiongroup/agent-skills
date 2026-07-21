# Test Suite Quality Review

Read this during Phase 3 (Test Suite Review). Passing tests prove nothing about test quality. Tests are code too — they don't test themselves, and a green suite of bad tests is false confidence.

## Contents

- The Core Question
- Flaky Tests
- Test Smells Catalog
- Assertion Quality
- DRY vs Readability in Tests
- Review Checklist

## The Core Question

**Would this test FAIL if the production code were broken?**

Apply the mutation mindset: mentally mutate the code under test — flip a condition, delete a line, change a boundary — and ask whether any test would catch it. A test that cannot fail is decoration, not verification.

**Signs a test can't fail:**

- No assertions at all, or assertions only on constants
- Asserts merely that no exception was thrown
- Mocks are configured to return exactly what the code under test produces (circular)
- Assertions verify mocked data, not behavior
- Assertions are unconditional tautologies (`assertTrue(true)` equivalents)

When you find these, flag them as `issue`: the test inflates coverage while verifying nothing.

## Flaky Tests

A flaky test passes and fails intermittently under identical conditions, with no code changes. Flaky tests destroy trust in the entire suite — teams learn to ignore failures, and real regressions hide in the noise.

### Common causes (review signals)

| Cause | Signals to look for |
|-------|---------------------|
| Time dependence | Fixed `sleep()` calls, wall-clock reads (`now()`, `Date()`), timezone/locale assumptions |
| Randomness | Unseeded random values, generated UUIDs influencing assertions |
| Order dependence | Tests mutating shared state, relying on execution order, database not reset between tests |
| External resources | Real network calls, real services, filesystem assumptions, environment variables |
| Concurrency | Missing `await`, fire-and-forget async, races between test and code |
| Resource leaks | Ports, files, connections, or subscriptions not cleaned up between tests |

### Detection during review

1. **Re-run the suite** when failures look intermittent. Consistent pass/fail → deterministic. Alternating results with no code change → flaky. Report it.
2. **Compare sequential vs. parallel execution** if the runner supports it. Failures appearing only in one mode signal shared state or order dependence.
3. **Search test files** for sleeps, fixed delays, unseeded randomness, and wall-clock usage.
4. **Check retry configuration.** Heavy reliance on retries masks flakiness instead of fixing it. If the suite only passes with retries, that is a finding, not a solution.

### What to report

- Suspect tests, with evidence (file:line, the mechanism you suspect)
- Retry configuration that masks instability
- **Skipped/ignored tests**: why are they skipped, for how long, and who owns re-enabling them? A skip without an owner and a reason is silent rot.

## Test Smells Catalog

### 1. Assertion Roulette
A test with multiple undocumented assertions — when it fails, you can't tell which behavior broke.

```javascript
// SMELL: which of these is the point of the test?
expect(user.name).toBe('Ada');
expect(user.age).toBe(36);
expect(user.roles).toContain('admin');
expect(user.isActive).toBe(true);
```

Fix to recommend: one behavior per test, or assertion messages that name the behavior.

### 2. Mystery Guest
The test depends on data it doesn't create or show — an external file, a shared fixture, a seeded database row.

```python
# SMELL: where does user 42 come from? why 3 orders?
def test_user_has_three_orders():
    user = repo.find(42)
    assert len(user.orders) == 3
```

The reader can't understand the test from the test. Recommend: create the data inside the test.

### 3. Eager Test
One test exercises many different behaviors of the production unit. Failure points everywhere and nowhere.

### 4. Conditional Test Logic
`if`/`for` inside a test means the test itself has untested paths — and may silently skip its assertions.

```python
# SMELL: if items is empty, this test asserts NOTHING and passes
for item in items:
    assert item.is_valid()
```

### 5. Magic Numbers
Numeric literals in assertions with no explained meaning (`assert total == 18` — why 18?). Recommend named constants or visible construction.

### 6. Over-Mocking
Mocking every collaborator — the test verifies the mocks, not the behavior, and shatters on every refactor.

```python
# SMELL: proves nothing — everything is a mock
@patch('service.db')
@patch('service.cache')
@patch('service.mailer')
def test_create_user(mock_mailer, mock_cache, mock_db):
    create_user({"name": "test"})
```

### 7. Testing Implementation Details
Calling private methods via reflection, or asserting that internal helper X was called. The test breaks when internals change, even if behavior is unchanged. Test through the public API; assert on outcomes.

### 8. Sleepy Test
Fixed `sleep()` used as synchronization. Slow when it works, flaky when the machine is loaded. Recommend awaiting conditions/events instead of time.

### 9. Ignored/Skipped Tests
Disabled tests rot silently. Every skip needs a reason, an owner, and ideally a ticket — or deletion.

### 10. Empty/Trivial Tests
Placeholder tests asserting nothing — coverage theater. Flag as `issue`.

### 11. Redundant Assertions
The same assertion repeated, or equality via `toString()` comparison (sensitive equality) that breaks on formatting changes without behavior changes.

### 12. General Fixture
Heavy shared setup that most tests only partially use — slows the suite and couples every test to data it doesn't need.

## Assertion Quality

- **One behavior per test.** Multiple assertions are fine when they verify a single behavior.
- **Names describe behavior**: `rejects_negative_amounts` — not `test_transfer_1`.
- **Arrange–Act–Assert is visible.** If you can't point to each part, the test is probably doing too much.
- **Assert on outcomes and state**, not on internal interactions — unless the interaction IS the contract (e.g. "sends exactly one email").
- **Assertions are specific**: `toBe(3)`, not `toBeTruthy()`. `raises(ValidationError, match="page_size")`, not `raises(Exception)`.

## DRY vs Readability in Tests

**Clarity beats DRY in tests.** Each test should tell its own short story; a reader should understand it without jumping to shared helpers.

- Some setup duplication between tests is fine and often good.
- Extract shared setup (builders, factories, `beforeEach`) only when it genuinely repeats AND the extraction keeps each test readable.
- Over-abstracted tests — deep base-class hierarchies, setup defined files away from the test — hide intent and create mystery guests.
- See `design-principles.md` for the general DRY nuance; tests are the main exception to aggressive de-duplication.

## Review Checklist

- [ ] Every reviewed test would FAIL if the code it covers were broken (mutation mindset applied)
- [ ] No tests that assert nothing, or only assert mocks
- [ ] No flakiness signals: sleeps, wall-clock, unseeded randomness, order dependence, shared state
- [ ] Retries aren't masking instability
- [ ] Skipped tests have a reason and an owner — or a recommendation to delete
- [ ] One behavior per test, named for that behavior
- [ ] Assertions are specific and on outcomes, not implementation details
- [ ] Mocking is proportionate (seams, not total replacement)
- [ ] Setup is visible; duplication in tests is intentional, not lazy
- [ ] Coverage gaps handled per `coverage-strategies.md`
