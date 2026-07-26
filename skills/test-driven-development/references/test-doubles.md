# Test Doubles

Read this during Modes A/C when a test depends on something volatile. Choosing the wrong double is a leading cause of brittle tests. **Research the language-specific mocking library online** — APIs differ and evolve (see `online-research-protocol.md`).

## The Meszaros Taxonomy

Gerard Meszaros (`xunitpatterns.com`) defines five kinds of test double. Martin Fowler's "Mocks Aren't Stubs" popularized them. Knowing the difference is non-negotiable.

| Double | Provides | Verifies | When to use |
|--------|----------|---------|-------------|
| **Dummy** | Nothing (filler) | Nothing | A parameter is required by the interface but the test ignores it |
| **Stub** | Canned answers to calls | Nothing (state) | The unit needs a value from a collaborator; you control that value |
| **Spy** | Canned answers + records calls | Post-hoc assertions on what was called | You need to inspect calls after the fact, not forbid them |
| **Mock** | Pre-programmed expectations | Interactions (fails on unexpected call) | The **interaction IS the contract** — e.g. "sends exactly one email" |
| **Fake** | A real (shortcut) implementation | Real behavior | A working-but-not-production implementation (in-memory DB, fake clock) |

## State vs Behavior Verification (the key distinction)

- **State verification** (stub/fake): set up inputs, exercise, assert on the **output/state** of the unit. The collaborator is just a source of values. Tests survive refactors of the collaborator's internals.
- **Behavior verification** (mock): pre-program expectations on **which calls happen**. The test asserts the interaction. Tests are coupled to *how* the unit uses the collaborator.

Fowler's point: **mocks aren't stubs**. A stub feeds the unit; a mock judges the unit's interactions. Most tests should use stubs/fakes (state); reserve mocks for cases where the interaction itself is the contract.

## When to Use Each

### Dummy
Only when a parameter is required by the signature but unused in the path under test. Do not use a dummy where a stub belongs — a dummy returns nothing and will NPE/None the test.

### Stub
The workhorse. The unit asks the collaborator for data; you return controlled data. The test then asserts on the unit's resulting state/output. The stub does **not** verify calls — it just answers.

### Spy
Like a stub but records calls so you can assert on them **after** the exercise. Less brittle than a mock because it doesn't fail on unexpected calls — you assert exactly what you care about.

### Mock
Pre-program the exact calls you expect. The mock fails if the calls don't match. Use **only** when the interaction is the contract:
- "sends exactly one email with subject X"
- "retries exactly 3 times"
- "persists the order before charging"
Otherwise prefer a stub/spy + state verification — it's more refactor-safe.

### Fake
A real, lightweight implementation: in-memory repository, fake clock, in-memory queue. Fakes give **real behavior** without the volatility. They are often the best choice for repository/service seams — they exercise behavior, not wiring, and survive refactors. The cost: you must keep the fake correct.

## The Seams Principle (where doubles belong)

Doubles belong at **volatility boundaries**, not everywhere:
- ✅ Database, HTTP APIs, filesystem, clock, randomness, message queues, external services.
- ❌ Stable domain objects, value objects, pure logic — use real instances.

Doubling stable collaborators is **over-mocking** (a smell): the test verifies the mocks, shatters on every refactor, and tells you nothing about real behavior. See `test-smells.md`.

## Sociable vs Solitary (relates to doubles)

- **Sociable** test: real collaborators, doubles only at volatile seams → fewer mocks, more realistic.
- **Solitary** test: every collaborator doubled → isolated, but coupled to internals.
Default **sociable**; reserve solitary for units with many volatile dependencies.

## Anti-Patterns

### Over-mocking
Mocking every collaborator (including internal helpers and value objects). The test mirrors the implementation and breaks on any refactor. It proves the mocks were called — not that the behavior works.

### Mocking to return what the code produces (circular)
The mock returns exactly the value the code under test would compute. The assertion is a tautology: it passes regardless of correctness. A test that cannot fail is decoration.

### Testing implementation details via mocks
Asserting that internal helper X was called, or that the code used method A not B. Breaks when internals change even if behavior is identical. Test through the public API; assert on outcomes.

### Mocking without understanding side effects
A mocked collaborator may hide real integration bugs. Before mocking a dependency, understand its side effects (ordering, errors, retries). If you don't, research it (see `online-research-protocol.md`).

## Language-Specific Notes (research online)

Mocking libraries and idioms differ and evolve. Always verify against the project's actual versions:
- **Python**: `unittest.mock` (Mock/MagicMock/patch/AsyncMock), `pytest-mock`, `freezegun`/`time-machine` for clocks, `responses`/`httpx_mock`/`pytest-vcr` for HTTP, `faker`.
- **JS/TS**: `vi.fn`/`vi.spyOn` (Vitest), `jest.fn`/`jest.spyOn`, `sinon`, `msw`, `nock`, `vitest` fake timers.
- **.NET**: `NSubstitute`, `Moq`, `FakeItEasy`, `TimeProvider` (.NET 8+) for clocks.
- **Java**: `Mockito`, `EasyMock`, `jMock` (the London-school origin), `WireMock` for HTTP.
- **Go**: table-driven with interfaces + hand-rolled fakes (Go idiom favors fakes over mocks), `gomock`, `testify/mock`, `http.HandlerFunc` for HTTP.
- **Rust**: hand-rolled trait impls as fakes (mocking is uncommon; traits are the seam), `mockall`, `faux`.

## Checklist for Choosing a Double

- [ ] Is the dependency **volatile** (DB/network/clock/random)? If no, use the real thing.
- [ ] Is the **interaction the contract** (exact calls matter)? If yes → mock. If no → stub/spy/fake.
- [ ] Need real behavior without volatility? → fake.
- [ ] Will this test **fail if the unit is wrong**, or only if the mocks are wrong? (Mutation mindset — see `assertion-quality.md`.)
- [ ] Did I research the current mocking-library API for this language/version?

## See Also
- `test-smells.md` — over-mocking and testing implementation details as smells.
- `assertion-quality.md` — state vs behavior assertions and the mutation mindset.
- `test-patterns.md` — Chicago (state) vs London (mock) schools.
