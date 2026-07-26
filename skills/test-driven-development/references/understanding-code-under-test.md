# Understanding the Code Under Test

Read this during Phase 1 (MANDATORY). You cannot write or judge a test without a mental model of the behavior under test. **Trace behavior, not implementation.**

## The Goal

By the end of Phase 1 you should be able to answer, for each unit under test:
- What does it **do** (inputs, outputs, side effects, errors)?
- What are its **invariants and contracts**?
- What does it **depend on** (seams where you may need test doubles)?
- What is **already tested**, and how (conventions, fixtures, helpers)?
- What is **complex or sensitive** (error paths, boundaries, concurrency, external input)?

## Steps

### 1. Read the Public API
Start with the public surface — exported functions, public methods, route handlers, CLI commands. This is what tests should exercise. Testing private internals couples tests to implementation (a smell — see `test-smells.md`).

### 2. Trace Behavior, Not Implementation
Understand WHAT the code does before HOW. Note:
- **Return values and post-conditions** (state-based verification targets).
- **Interactions with collaborators** (behavior-verification targets — only when the interaction IS the contract, e.g. "sends exactly one email").
- **Error conditions** — what raises/returns on bad input, missing resource, timeout.
- **Invariants** — properties that must always hold (these become property-based tests; see `test-patterns.md`).

### 3. Identify Seams and Dependencies
List every external concern: databases, HTTP APIs, filesystem, clock, randomness, env vars, message queues, other services. Each is a candidate for a test double (see `test-doubles.md`). Distinguish:
- **Volatile/external** (real DB, real network, real clock) → prime candidates for doubles.
- **Stable/value** (domain objects, pure logic) → use real instances; do not mock.

Over-mocking stable collaborators is a leading cause of brittle tests.

### 4. Read Existing Tests and Note Conventions
Match the suite's style or you will fight it. Record:
- **Framework & runner** (pytest, jest, JUnit, go test, …) and version.
- **Assertion style** (expect, assert, require, should, …).
- **Naming convention** (`MethodName_StateUnderTest_ExpectedBehavior`, BDD `should ...`, `it ...`, snake_case, …).
- **Structure** — Arrange-Act-Assert vs Given-When-Then, describe/it nesting, fixtures location.
- **Shared setup** — `beforeEach`/`setUp`, factories, builders, Object Mother, fixtures files.
- **What is already covered** — avoid duplication; identify gaps.

### 5. Detect Sensitive and Complex Areas
These need the most test attention and are where bugs live:
- **Error handling** — try/except, error returns, fallbacks (frequently untested).
- **Boundaries** — off-by-one, empty, zero, negative, MAX/MIN, pagination edges.
- **Concurrency** — async ordering, shared mutable state, races, timeouts.
- **External input** — parsing, validation, deserialization (also a security surface — hand off).
- **Branching logic** — switch/if-else chains with uncovered branches (see `coverage-and-mutation.md`).

### 6. Locate Test and Coverage Configuration
Find and read:
- Test config: `pyproject.toml` (`[tool.pytest]`), `jest.config.*`, `phpunit.xml`, `Cargo.toml`, `go.mod`, `pom.xml`/`build.gradle`.
- Coverage config: `.coveragerc`, `pyproject.toml` coverage, `jest` `coverageThreshold`, JaCoCo config, `.gitlab-ci`/`.github/workflows` coverage gates.
- Existing coverage reports if generated.

Config tells you the project's authoritative commands and thresholds — use them in Phase 2.

## Detect-Then-Validate

You detect all of the above yourself in Phase 1–2. In Phase 3 you **validate** each finding with the user and ask for what you could not detect. Detection does not replace validation — the user's confirmation is the authority.

## Output of Phase 1

A short mental model (or notes) covering the six questions above, plus a candidate test list for Mode A, or a focus list for Modes B/C (which units/paths to prioritize). This drives the rest of the work.
