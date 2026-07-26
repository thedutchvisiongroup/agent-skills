# Test Strategies

Read this when advising on test-suite shape or when a suite is unbalanced. A test strategy is about **where to invest** test effort for maximum confidence per dollar.

## The Core Trade-off

| Test type | Speed | Confidence per test | Maintenance cost | Debug difficulty |
|-----------|-------|----------------------|-------------------|------------------|
| Unit (isolated) | ms | Low–medium | Low | Low |
| Integration | sec | High | Medium | Medium |
| End-to-end (E2E) | min | Very high (real flow) | High (brittle) | High |

A famous rule of thumb: a bug costs ~$1 in a unit test, ~$10 in integration, ~$100 in E2E, ~$1000+ in production. The strategy models below allocate effort to keep bugs cheap.

## The Test Pyramid (Mike Cohn)

Many fast unit tests at the base, fewer integration in the middle, fewest E2E at the top. Fits **backend services, monoliths, API-heavy apps** where isolated business logic dominates.

```
   E2E
  -----
 Integration
-----------
   Unit
-------------
```

- Base: many unit tests — fast, isolated, exhaustive on logic.
- Middle: integration tests — component composition, DB, real services.
- Top: a few E2E tests — critical user journeys end-to-end.

## The Testing Trophy (Kent C. Dodds)

For **frontend / component-driven JS-TS apps**. Flips the proportions and adds a static-analysis base:

```
       E2E
    ---------
   Integration  (largest layer)
  ---------------
     Unit
  -----------------
 Static analysis   (lint, types)
```

Rationale: for components, "unit" vs "integration" is blurry, and mocking a component away often removes the behavior you care about. Integration tests give the best confidence-per-dollar here. The trophy's **default recommendation** is "when in doubt, write an integration test" — the inverse of the pyramid's default.

## Other Models

- **Testing Honeycomb (Spotify)** — for microservices: heavy integration middle, thinner unit and E2E. Most complexity lives in service-to-service interaction, not within a single service.
- **Testing Diamond** — roughly equal unit and integration, thin E2E. A middle ground.
- Choose by architecture, not by fashion. Pull the last 20 production incidents and tag each by which test type *could* have caught it — let the data inform the shape.

## Sociable vs Solitary Units (Martin Fowler)

- **Solitary** unit test: every collaborator is a double. Fast, isolated — but tests the wiring, and shatters on refactor.
- **Sociable** unit test: uses real collaborators, doubles only at volatile boundaries (DB, network, clock). More realistic, less brittle.
- Default lean **sociable**; reserve solitary for units with many volatile dependencies. Over-mocking (solitary-everything) is a leading smell — see `test-doubles.md` and `test-smells.md`.

## Anti-Patterns

### Ice Cream Cone (inverted pyramid)
Top-heavy: many manual/E2E tests, thin integration, almost no unit. Symptoms: slow suite, fragile E2E, 10x cost for 10x worse quality. Causes: over-correction for buggy software by "testing what we can see" (UI). Reverse by pushing coverage down into unit/integration.

### Hourglass
Many E2E + many unit, too few integration. Result: E2E failures that integration tests would have caught faster and cheaper. Add the missing middle.

## How to Choose (advisory)

1. Identify the architecture type (backend service / frontend / microservices / library).
2. Pick the matching model (pyramid / trophy / honeycomb). Propose this in the Phase 3 gate.
3. Apply **sociable-by-default** with doubles only at volatile seams.
4. Keep E2E to critical user journeys (checkout, auth, signup). A 5-min E2E suite of 1000 tests = 83 hours; the same coverage as 50ms unit tests = 50s.
5. Separate fast unit from slow integration/E2E in the runner config so devs run fast tests constantly.

## Coverage Targets by Tier (propose, then confirm)

| Code tier | Branch coverage target | Mutation testing |
|-----------|------------------------|------------------|
| Core business logic / financial rules | 90–95% | Yes (nightly / pre-merge on changes) |
| API endpoints / services | 80–90% | Optional |
| Standard features | 60–80% | No |
| Cosmetic / disposable / prototypes | 30% or none | No |

These are **defaults to propose**, not impose — always confirm with the user in Phase 3. See `coverage-and-mutation.md` for coverage types and mutation testing.

## When Strategy Is Out of Scope

Strategy advice is advisory only. You never edit production code or CI config to enforce a strategy — you recommend, the user decides.
