# Test Smells

Read this during Modes B/C (review / improve). Passing tests prove nothing about quality. A green suite of bad tests is false confidence. Each smell below is a symptom of a design or implementation problem in the test code.

## The Core Question

**Would this test FAIL if the production code were broken?** Apply the mutation mindset (see `assertion-quality.md`): mentally mutate the code — flip a condition, delete a line, change a boundary — and ask whether any test catches it. A test that cannot fail is decoration.

## Smells Catalog

### 1. Assertion Roulette
A test with many undocumented assertions — when it fails, you can't tell which behavior broke.
```
// SMELL: which of these is the point?
expect(user.name).toBe('Ada');
expect(user.age).toBe(36);
expect(user.roles).toContain('admin');
expect(user.isActive).toBe(true);
```
**Fix:** one behavior per test, or assertion messages/descriptions that name the behavior.

### 2. Mystery Guest
The test depends on data it doesn't create or show — an external file, a shared fixture, a seeded DB row.
```
# SMELL: where does user 42 come from? why 3 orders?
def test_user_has_three_orders():
    user = repo.find(42)
    assert len(user.orders) == 3
```
**Fix:** create the data inside the test (builders/factories). The reader must understand the test from the test.

### 3. Eager Test
One test exercises many behaviors. Failure points everywhere and nowhere.
**Fix:** split into focused tests, one behavior each.

### 4. Conditional Test Logic
`if`/`for`/`while` inside a test means the test has untested paths and may silently skip its assertions.
```
# SMELL: if items is empty, this test asserts NOTHING and passes
for item in items:
    assert item.is_valid()
```
**Fix:** parameterized tests (one row per case); remove branches from tests. Tests should be linear.

### 5. Magic Numbers
Numeric literals in assertions with no explained meaning (`assert total == 18` — why 18?).
**Fix:** named constants, or construct the expected value visibly (`2 * 9`).

### 6. Over-Mocking
Mocking every collaborator — the test verifies the mocks, not the behavior, and shatters on every refactor.
```
# SMELL: proves nothing — everything is a mock
@patch('service.db'); @patch('service.cache'); @patch('service.mailer')
def test_create_user(mock_mailer, mock_cache, mock_db):
    create_user({"name": "test"})
```
**Fix:** sociable tests with real collaborators; double only volatile seams. See `test-doubles.md`.

### 7. Testing Implementation Details
Calling private methods via reflection, or asserting that internal helper X was called. Breaks when internals change even if behavior is identical.
**Fix:** test through the public API; assert on outcomes, not internal interactions.

### 8. Sleepy Test
Fixed `sleep()` used as synchronization — slow when it works, flaky under load.
**Fix:** await a condition/event/poll; use fake clocks; assert on readiness, not elapsed time. See `flaky-tests.md`.

### 9. Ignored / Skipped Tests
Disabled tests rot silently. Every skip needs a reason, an owner, and ideally a ticket — or deletion.
**Fix (Mode C):** re-enable with a fix, or delete. A skip without owner/reason is silent rot — report it (Mode B).

### 10. Empty / Trivial Tests
Placeholder tests asserting nothing — coverage theater.
**Fix:** flag as `issue`. Delete or implement a real assertion.

### 11. Redundant Assertions
The same assertion repeated, or equality via `toString()` comparison (sensitive equality) that breaks on formatting changes with no behavior change.
**Fix:** one assertion per behavior; compare on semantic equality, not serialization.

### 12. General Fixture
Heavy shared setup that most tests only partially use — slows the suite and couples every test to data it doesn't need.
**Fix:** extract only genuinely shared setup; prefer per-test builders. See `test-patterns.md` (Object Mother / Builder).

### 13. Algorithm Duplication
Duplicating the production algorithm in the test (white-box). The test is coupled to implementation and verifies "the code does what it does".
**Fix:** assert on outcomes with known expected values, not by re-implementing the logic.

### 14. 1:1 Test-to-Function Mapping
Insisting one unit test per function, testing no more than one function. Real behavior often spans functions.
**Fix:** test behavior through the public API; let coverage fall where it may.

### 15. Test-After Bias (for Mode A)
Tests written after the code pass immediately — they verify the cases you remembered, not the ones you'd have discovered test-first.
**Fix:** test-first where feasible; characterize for legacy code.

## Flakiness Smells (see `flaky-tests.md`)

These overlap with flakiness causes — flag them in Mode B, fix them in Mode C:
- Fixed `sleep`, wall-clock reads (`now()`, `Date()`), timezone assumptions
- Unseeded randomness, generated UUIDs influencing assertions
- Order dependence, shared mutable state, DB not reset
- Real network/HTTP calls, filesystem path assumptions
- Missing `await`, fire-and-forget async, races
- Heavy reliance on retries (masks flakiness)

## Review Checklist (Mode B)

- [ ] Every reviewed test would FAIL if the code it covers were broken (mutation mindset)
- [ ] No tests that assert nothing, or only assert mocks
- [ ] No flakiness signals (sleeps, wall-clock, unseeded randomness, order dependence)
- [ ] Skipped tests have a reason + owner — or a recommendation to delete
- [ ] One behavior per test, named for that behavior
- [ ] Assertions specific and on outcomes, not implementation details
- [ ] Mocking proportionate (seams only)
- [ ] Setup visible; duplication intentional, not lazy

## Improve Checklist (Mode C)

- [ ] Removed conditional logic from tests (parameterized instead)
- [ ] Strengthened weak assertions (specific values, mutation-killing)
- [ ] Reduced over-mocking (sociable where possible)
- [ ] Eliminated sleeps / wall-clock (fake clock, awaited conditions)
- [ ] Re-enabled or deleted skipped tests
- [ ] Tests still green after changes; coverage not regressed

## See Also
- `assertion-quality.md` — the mutation mindset and strong assertions.
- `flaky-tests.md` — root causes and fixes for the flakiness smells above.
- `test-doubles.md` — over-mocking and seams.
