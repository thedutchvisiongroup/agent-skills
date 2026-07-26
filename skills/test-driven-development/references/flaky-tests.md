# Flaky Tests

Read this during Modes B/C whenever flakiness is suspected. A flaky test passes and fails intermittently under identical conditions, with no code change. Flaky tests destroy trust in the entire suite — teams learn to ignore failures, and real regressions hide in the noise.

## The Iron Rule of Flakiness

**Retries mask flakiness; they never fix it.** A suite that only passes with retries is a finding, not a solution. Fix the root cause.

## Common Causes (review signals)

| Cause | Signals to look for |
|-------|---------------------|
| **Time dependence** | Fixed `sleep()` calls, wall-clock reads (`now()`, `Date()`, `datetime.now`, `Instant.now`), timezone/locale assumptions, expiry assertions |
| **Randomness** | Unseeded random values, generated UUIDs/collisions influencing assertions, `rand()` without a seed |
| **Order dependence** | Tests mutating shared state, relying on execution order, DB/data not reset between tests, static/class-level mutable state |
| **External resources** | Real network/HTTP calls, real services, filesystem path assumptions, environment variables, containerized deps not isolated |
| **Concurrency** | Missing `await`, fire-and-forget async, races between test and code, channels/queues not drained |
| **Resource leaks** | Ports, files, connections, subscriptions, temp dirs not cleaned up between tests |
| **Time-of-test** | Assertions on "within 100ms"; assumptions about CI-runner speed vs laptop |

## Detection (Mode B)

1. **Re-run the suite** when failures look intermittent. Consistent pass/fail → deterministic. Alternating results with no code change → flaky. Report it.
2. **Compare sequential vs parallel execution** if the runner supports it. Failures appearing only in one mode signal shared state or order dependence.
3. **Run the isolated suspect test N times** (e.g. `--repeat-until-fail 20`, `pytest-repeat`, `flaky` plugin, jest `--testNamePattern` in a loop). A flaky test will surface.
4. **Search test files** for the signals above: `sleep`, `now`, `Date`, `random`, `uuid`, network clients, env reads, shared static state.
5. **Check retry/quarantine config.** A `@flaky` decorator, `pytest.mark.flaky(reruns=N)`, jest `retryTimes`, or skipped-with-`@Ignore` — these are treatments, not cures. Report the underlying test.
6. **CI history** — platforms track pass/fail rates over time; a test that flips is a candidate.

## What to Report (Mode B)

- Suspect tests with evidence: `file:line`, the mechanism you suspect, the re-run/parallel result.
- Retry/quarantine config that masks instability.
- Skipped/ignored tests: why skipped, how long, who owns re-enabling. A skip without owner + reason is silent rot.

## Root-Cause Fixes (Mode C — edit test files only)

### Time dependence
- **Inject a clock** (`freezegun`/`time-machine` Python, `TimeProvider` .NET 8+, `vi.useFakeTimers`/`jest.useFakeTimers`, `FakeAsyncClock`); never read wall-clock in the unit.
- Replace `sleep(N)` with awaiting a **condition**: poll a predicate, await an event/promise, assert readiness instead of elapsed time.
- For expiry tests, advance the injected clock instead of waiting.

### Randomness
- **Seed** the generator in test setup (fixed seed) so runs are reproducible. Expose the seed on failure.
- Inject a deterministic random source (a fake) the unit accepts via dependency.
- If the test must use real randomness, assert on properties (distribution bounds), not exact sequences — or use property-based testing (see `test-patterns.md`).

### Order dependence
- Each test creates and destroys its own state. Reset DBs/slices per test (transaction rollback, per-test schema, ephemeral container).
- No static/class-level mutable state across tests.
- Run the suite in random order (`pytest-randomly`, jest `--randomize`, .NET `[Collection]` behavior) — order-dependent tests surface immediately.

### External resources
- Double volatile external deps at the seam (HTTP: `responses`/`msw`/`nock`/`WireMock`; DB: in-memory fake or test container; filesystem: temp dirs). See `test-doubles.md`.
- If a real resource is required, isolate it (container per run/class, transaction per test) and never let tests share mutable state in it.
- Network: never make real outbound HTTP in unit tests; integration tests use a controlled fake or contract test.

### Concurrency
- `await` all async operations; assert the async work **completed** before asserting on its effects.
- Drain queues/channels; let background jobs finish (await, poll, or await a "settled" state).
- Avoid fire-and-forget in tests; capture the task and await it.

### Resource leaks
- Use framework fixtures/teardown to close connections, files, servers, subscriptions, temp dirs.
- Verify with a clean second run — leaks surface as "port already in use" or "file exists".

## Quarantine Policy (Mode C)

If a test **cannot** be made deterministic immediately, quarantine it deliberately:
- Mark it skipped with a **reason** and an **owner** and a **ticket**.
- Quarantined tests run separately (or not at all) so they don't poison the main suite.
- Track the count — a rising quarantine list is a quality signal to leadership.

Never quarantine silently. Never delete a test for being flaky unless you can prove the behavior is covered elsewhere.

## Retry Policy (the last resort, reported honestly)

Retries are acceptable **only** for genuinely non-deterministic external systems AND only with:
- A documented reason the test cannot be made deterministic.
- A bounded retry count and a quarantine plan to fix it.
- Explicit team awareness that retries hide bugs.

Default to **no retries**. A suite that needs retries is a finding.

## Checklist

- [ ] Re-ran the suite; identified flaky tests with evidence
- [ ] Searched for sleep / wall-clock / unseeded random / order / external / async signals
- [ ] Checked retry/quarantine config — reported masking
- [ ] (Mode C) Fixed root causes: injected clock, seeded random, isolated state, awaited conditions, doubled seams
- [ ] (Mode C) Tests deterministic under repeat + random-order runs
- [ ] (Mode C) Skipped tests have reason + owner + ticket, or are deleted

## See Also
- `test-smells.md` — sleepy test and shared state as smells.
- `test-doubles.md` — doubling volatile seams to remove external flakiness.
- `assertion-quality.md` — assert on readiness/properties, not elapsed time.
