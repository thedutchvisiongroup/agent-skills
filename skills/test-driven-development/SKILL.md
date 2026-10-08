---
name: test-driven-development
description: "Shared test-driven development and test-quality methodology. Use when implementing features or fixes with Red-Green-Refactor, writing or improving tests, reviewing assertions, flakiness and coverage, or choosing a test strategy. An implementation-capable agent owns tests and production code in one vertical feedback loop; a delegated test specialist reviews independently after implementation. Respects the calling agent's role and permissions, protects tests, verifies Red and Green, and reuses applicable execution/documentation evidence."
---

# Test-Driven Development

## The Iron Law

```
WRITE A MEANINGFUL FAILING TEST BEFORE IMPLEMENTING NEW BEHAVIOR.
ONE IMPLEMENTER OWNS RED → GREEN → REFACTOR; DO NOT SPLIT THE FEEDBACK LOOP.
APPROVED BEHAVIOR IS THE AUTHORITY; A GENERATED TEST CAN BE WRONG.
THE CALLING ROLE AND PERMISSIONS DETERMINE WHAT YOU MAY CHANGE.
NO TEST WITHOUT FIRST UNDERSTANDING THE CODE UNDER TEST.
NO FINDING WITHOUT EVIDENCE: file:line, the smell, the trace.
VERIFY LANGUAGE-SPECIFIC CLAIMS AGAINST CURRENT SOURCES AND PROJECT VERSIONS.
```

A test written without understanding the behavior under test is decoration, not verification. A review that only skims tests is not a review.

**You MUST complete all phases before delivering your work.**

## Role Boundary — Non-Negotiable

This skill supplies a method, not extra authority. Establish your role before choosing a mode:

| Calling role | Permitted work |
| --- | --- |
| Implementation-capable agent | Mode A: tests, minimal production implementation and local refactoring within the approved task. Mode C: scoped test improvements and necessary, authorized source changes. |
| Delegated test specialist | Mode B only: independently assess tests and verification, report findings, never modify tests or production code. Fixes return to the coordinator's implementer. |
| Directly invoked test specialist | Modes A/B/C as requested, but edits are test files only. If Green or a source seam needs production changes, report the need to the user/implementer; never write it yourself. |

- Production/source files include application code, configs, build scripts and generated code. A tests-only agent's permissions never lift its production-code ban.
- Mode B is always advisory-only, including when an implementation-capable agent uses it.
- An approved, contract-named Markdown report is allowed within its approved run directory; it does not authorize other artifacts or executable helpers for a reviewer.
- Reviewers and test specialists NEVER install tools. An implementer may change/install project dependencies only when explicitly included in the approved task and allowed by project permissions. New tooling or expanded scope goes to the coordinator/user first.
- Missing context or a material tradeoff goes to the coordinator as `NEEDS_CONTEXT` in delegated work; direct work asks the user.

## Protect the Test Contract

- Derive expected outcomes from approved requirements, independent examples or trusted reference behavior, not from whatever the implementation returns.
- Never delete/skip a failing test, relax an assertion, broaden a mock, or regenerate a snapshot merely to produce Green.
- A genuinely incorrect test may be corrected: document the specification-based reason and changed expectation, preserve intended coverage, and submit the change to independent review.
- Characterization tests legitimately pass on existing behavior. New behavior/bug-reproduction tests must show expected Red; a setup error is not behavioral failure proof.

## Out of Scope

- **Code-quality review** of production code (DRY, SOLID, naming, complexity). Recommend the `code-review` skill.
- **Security review.** Recommend the `security-review` skill. Note security-looking smells only as a handoff trigger.
- **Unrelated production changes**, and any production changes by a tests-only specialist or reviewer.
- **Running exploits or live attacks.** Never.
- **Generated/vendor code.** Do not test it directly; test the integration seam at most.

## Before You Start — The Clarification Gate (MANDATORY)

You MUST NOT begin mode work until the gate is passed. The gate is **detect-then-validate**: gather everything you can yourself, then ALWAYS validate your findings and ask for everything you could NOT find.

**Detect (before asking):** inspect relevant manifests, CI/config, behavior and tests. Applicable coordinator detection evidence may be reused after checking scope and versions (Phases 1–2).

**Validate + ask:** confirm each element below. Explicitly user-confirmed answers in an approved delegation contract satisfy matching items; approval alone does not answer omitted items. Do not re-ask confirmed answers. Missing answers/mismatches go to the coordinator; direct work validates with the user.

- [ ] **What is tested + scope** — Which code/feature/module must be covered, and what is explicitly OUT of scope?
- [ ] **Role + mode** — (A) test-first implementation/test writing, (B) independent review, (C) improvement; confirm the role's edit boundary. Delegated test specialists use B.
- [ ] **Tech-stack, framework & conventions** — Language(s), test framework(s)/runner(s), assertion style, naming convention, existing test structure, coverage tool + config. Detect these; validate them.
- [ ] **Behavior / specification & edge cases** — What is the expected behavior of the code under test, including edge cases and error paths? (Without this you cannot write meaningful tests.) If a spec is missing, ask or read the behavior from the code + existing tests and confirm.
- [ ] **Coverage goals & strategy** — Is there a coverage threshold or test-strategy target (pyramid/trophy/honeycomb)? If not, propose layered defaults (see `references/coverage-and-mutation.md`) and confirm.

```
STOP. Has the gate passed?
- [ ] Yes, I detected stack/framework/conventions/coverage-config myself
- [ ] Yes, I validated every element with the user or matching user-confirmed delegation answers
- [ ] Yes, I asked for everything I could not detect
- [ ] Yes, I know the mode(s) and their order
If any box is unchecked: ASK. Do not start mode work.
```

## The Three Modes

| Mode | What you do | Primary references |
|------|-------------|--------------------|
| **A — Test-first implementation / test writing** | Red → Green → Refactor in one implementer. A direct tests-only specialist stops at its production boundary. Characterization tests for existing behavior. | `tdd-fundamentals.md`, `test-patterns.md`, `test-doubles.md`, `assertion-quality.md` |
| **B — Review existing tests** | Assess flakiness, test smells, assertion quality, coverage gaps, mutation mindset. Report findings with evidence; do not edit. | `test-smells.md`, `flaky-tests.md`, `assertion-quality.md`, `coverage-and-mutation.md` |
| **C — Improve existing tests** | Fix root causes and strengthen tests within the caller's role: implementer may change necessary approved source seams; direct specialists edit tests only; delegated specialists remain in B. | `flaky-tests.md`, `assertion-quality.md`, `test-doubles.md`, `test-smells.md` |

In every mode understand the behavior and validate applicable language-specific evidence. Review mode judges tests and Red/Green claims independently.

## Evidence-Oriented Reuse

Do not reconstruct identical baselines, tooling inventories or research per agent. Reuse only when evidence identifies the code revision (commit or content fingerprint), scope, commands/results, tool/dependency versions and environment. For documentation, check source date/version and applicability. Attribute reused evidence; a bare “tests pass” is insufficient.

- Every reviewer still reasons independently about changed behavior and tests; evidence reuse never means accepting the author's verdict.
- Run/research again when code, configuration, dependencies or environment changed, evidence is missing/stale, or a concrete doubt is unanswered.
- Use focused tests during the local cycle and fix rounds. Run relevant full checks at batch completion and after integration changes; do not repeat an unchanged full run solely for another review seat.
- Use existing coverage/mutation tooling where relevant; report absent/inapplicable tools and unverified claims. Exceptions to new tests and to test review are separate, explicit, advance-approved plan decisions with reason and alternative verification. Never infer an exception from task size.

## The Six Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Understand the Code Under Test (MANDATORY)

**BEFORE writing or judging any test, build a mental model of the behavior under test.**

Read `references/understanding-code-under-test.md` NOW. Then:

1. **Read the public API** — the functions/classes/modules to be tested. What does each do? What are inputs, outputs, side effects, errors?
2. **Trace behavior, not implementation** — understand WHAT it does, not just HOW. Note invariants and contracts.
3. **Identify seams and dependencies** — external services, I/O, time, randomness, config. These drive test-double decisions later.
4. **Read existing tests** — conventions, fixtures, helpers, naming, assertion style. Match the suite's style.
5. **Detect sensitive/complex areas** — error paths, boundaries, concurrency, external input (these need the most attention).
6. **Locate test config & coverage config** — `pyproject.toml`, `jest.config.*`, `Cargo.toml`, `go.mod`, CI workflows, `.coveragerc`, `coverage/`.

```
STOP. Do you understand the code under test?
- [ ] Yes, I read the public API and traced behavior
- [ ] Yes, I listed seams/dependencies (test-double candidates)
- [ ] Yes, I read existing tests and noted conventions
- [ ] Yes, I located test & coverage config
If any box is unchecked: read more before writing or judging tests.
```

### Phase 2: Detect Tooling, Establish Baseline & Language Deep-Dive (MANDATORY)

**Establish applicable tooling, baseline and language-specific evidence. Reuse qualified evidence; honor role-bound dependency/installation permissions.**

1. **Detect tooling** from config + CI (`.github/workflows`, `.gitlab-ci.yml`, pre-commit). CI reveals the authoritative commands.

   | Stack | Typical |
   |-------|---------|
   | Python | `pytest`, `coverage`/`pytest-cov`, `hypothesis`, `mutmut` |
   | JS/TS | `jest`/`vitest`, `cypress`/`playwright`, `nyc`/`c8`, `stryker` |
   | .NET | `xunit`/`nunit`, `coverlet`, `Stryker.NET` |
   | Java | `JUnit`/`TestNG`, `JaCoCo`, `PITest`, `jqwik` |
   | Go | `go test`, `-coverprofile`, `testify` |
   | Rust | `cargo test`, `tarpaulin`/`llvm-cov`, `proptest`, `cargo-mutants` |

2. **Establish a baseline when a suite exists** — execute the relevant suite/coverage or assess recorded baseline evidence under Evidence-Oriented Reuse. Before/after comparisons refer to the correct revisions. Investigate flakiness with focused repeats; one Green is not determinism proof.

3. **Language-specific validation.** For each language in scope follow `references/online-research-protocol.md`. Validate relevant framework/version claims using current authoritative sources or applicable documented research. Investigate unresolved questions online; report newly collected versus reused sources.

4. **Missing tools: report + benefit.** Record missing/inapplicable runner, coverage, mutation or flakiness tooling and its benefit. Respect role-bound installation authority; reviewers never install.

```
STOP. Did you handle tooling and language research?
- [ ] Yes, I detected the test runner + coverage tool from config/CI
- [ ] Yes, I established a revision-bound baseline or reported its absence/applicable exceptions
- [ ] Yes, I validated relevant language-specific claims against current, applicable sources
- [ ] Yes, I reported tooling gaps and respected role-bound installation authority
If any box is unchecked: GO BACK and complete it.
```

### Phase 3: Clarification Gate — Validate With the User (MANDATORY)

Run the Before-You-Start gate using Phases 1–2 evidence. Check every element against confirmed answers; ask only for missing/mismatching context. **Do not proceed to Phase 4 until the gate is passed.**

> Detection is not approval. Confirmed requirements and role permissions remain authoritative.

### Phase 4: Mode-Specific Work

Load the references for your mode(s). One behavior per test; one concern per finding; one fix per improvement.

**Mode A — Test-first implementation / test writing:**

1. Write a test list (Fowler): enumerate cases, sequence them, add more as they occur.
2. **RED** — write ONE minimal failing test for one behavior. Clear name (behavior, not "test1"). Real code, no mocks unless unavoidable.
3. **Verify RED (MANDATORY for new behavior)** — confirm the expected behavioral failure or absence of an explicitly specified public API (including a corresponding compilation failure). A typo, bad fixture/import path or missing test dependency is setup failure, not Red. Record why the failure demonstrates the missing requirement. Investigate immediate passes; characterization intentionally covers existing behavior.
4. **GREEN** — an implementation-capable agent writes the minimal production change for current approved behavior, then runs the focused test and relevant regressions. A direct tests-only specialist reports the production need and stops at its boundary instead.
5. **REFACTOR** — after Green, improve local test/source structure within role and scope; rerun covering tests. Repeat one behavior at a time, never bulk tests then bulk implementation.
6. For EXISTING code, write characterization/golden-master tests that lock in current behavior.

See `references/tdd-fundamentals.md`, `references/test-patterns.md`, `references/test-doubles.md`, `references/assertion-quality.md`.

**Mode B — Review existing tests:**

1. **Flakiness scan** — inspect sleeps, time/randomness, shared state, order, external resources and retry-masking. Assess applicable repeat-run evidence; repeat focused suspect tests or compare execution modes when needed to resolve a concrete risk, not automatically every full suite. See `references/flaky-tests.md`.
2. **Test smells** — walk the catalog. See `references/test-smells.md`.
3. **Assertion quality + mutation mindset** — would each test FAIL if the code it covers were broken? Mentally mutate: flip a condition, delete a line, change a boundary. See `references/assertion-quality.md`.
4. **Coverage gaps** — focus on changed/critical files; prioritize errors > branches > lines. See `references/coverage-and-mutation.md`.
5. **Evidence per finding**: `file:line`, the smell, why it matters, severity + confidence. Report; do not edit.

**Mode C — Improve existing tests:**

1. Start from the Mode B review (you must know what's wrong before improving).
2. Fix flakiness at the root (inject a clock, seed randomness, isolate state, await conditions instead of sleeping). NEVER mask with retries.
3. Strengthen assertions (specific values, one behavior per test, assert on outcomes not implementation).
4. Reduce over-mocking (replace mocks with fakes/real collaborators where the seam allows; test through the public API).
5. Refactor TEST code for clarity (extract builders/factories, remove general fixtures, name for behavior). Keep tests green.
6. Respect the role: direct specialists edit tests only; implementers may make necessary authorized source changes with regression protection. Delegated specialists remain in B and return findings for the implementer.

```
STOP. Did you complete the mode work?
- [ ] Mode A: new behavior showed expected Red and verified Green in one implementation worker (or an explicit tests-only boundary)
- [ ] Mode B: every finding has file:line + smell + severity + confidence; nothing edited
- [ ] Mode C: role/scope respected; root cause addressed; tests still Green
- [ ] Every mode: one behavior per test; assertions specific and on outcomes
If any box is unchecked: GO BACK and finish.
```

### Phase 5: Verify (MANDATORY)

**Verify current results using execution evidence, never assumptions.** Apply Evidence-Oriented Reuse; changed code/tests require covering checks for the new revision.

- **Mode A:** capture Red, focused Green and covering checks after refactoring; verify the relevant full suite at batch completion. Direct tests-only work may remain Red with an explicit production handoff.
- **Mode B:** assess applicable suite/coverage evidence; run focused probes/repeats for concrete doubts. Report unverified claims and observed flakiness.
- **Mode C:** compare applicable before evidence with covering execution after the changed revision; verify root-cause improvement, regressions and relevant coverage.
- Assess available/applicable coverage against revision-bound baseline and agreed goals; report missing evidence rather than inventing a score.
- If mutation tooling is available and code is critical, consider focused checks. Reviewers never install; adding tooling is a separately approved implementer task.
- Investigate determinism risks. Quarantine is an explicitly approved test-contract change with reason and owner, never a shortcut to Green; in B report the need.

```
STOP. Did you verify?
- [ ] Yes, applicable execution evidence covers the current revision; changes were checked
- [ ] Yes, coverage was assessed against goals or its absence reported
- [ ] Yes, determinism risks were investigated; one passing run was not treated as proof
- [ ] Yes, role-specific source/test/report boundaries were respected
If any box is unchecked: GO BACK and verify.
```

### Phase 6: Synthesize & Deliver

**Deliver implementation/test work or advisory review appropriate to your role.** The coordinator still obtains independent code and test-quality review after implementation.

1. **Summary** — scope, mode(s), baseline → after, one-paragraph assessment.
2. **Tooling & baseline results** (executed / reused with revision/source / missing or inapplicable; authorized dependency work if any).
3. **Mode A deliverable:**
   - New test files created (list).
   - The test list (cases written + cases still pending).
   - Red/Green commands, output, failure reason and revision identity; refactoring and covering checks.
   - Test-contract corrections and specification-based justification.
   - Production handoff only for a tests-only caller; distinguish intentional Red from completed Green.
4. **Mode B deliverable (findings, by severity):** each finding — severity + confidence, `file:line`, the smell, why it matters, the recommendation (you advise; you do not implement).
5. **Mode C deliverable:** test files changed (list), per change: what was wrong → what you changed → why it's better. Before/after suite + coverage.
6. **Online research log** — what you researched per language, sources, how it changed your work.
7. **Coverage gaps** — with the user's answers; remaining gaps and recommended tests.
8. **Out-of-scope handoffs** — code-quality (`code-review`) / security (`security-review`) / production-code work, one line each.
9. **Verdict:**
    - `IMPLEMENTED — VERIFIED GREEN` (implementation role; independent reviews still required)
    - `TESTS DELIVERED — PRODUCTION CODE NEEDED` (direct tests-only role with pending Green)
   - `FINDINGS — FIX BEFORE MERGE` (any Critical/High flakiness or no-assertion tests)
   - `FINDINGS — RISK ACCEPTANCE NEEDED` (Medium/Low or unverified)
   - `NO FINDINGS` / `TESTS IMPROVED — ALL GREEN`

For delegation, write the named report and return the short status/verdict. Review findings never authorize fixes to reviewed files.

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "I'll fix production code despite my review/tests-only role" — Report the need; role limits bind.
- "The test passes, so it's a good test" — Green tests can be flaky, shallow, over-mocked. Review them.
- "I'll write the test after the code" — Tests written after are biased by the code. Test-first (Mode A) or characterize existing behavior.
- "A new-behavior test passes immediately — good enough" — Investigate and demonstrate expected Red. Characterization is different.
- "100% coverage means well-tested" — Coverage is a negative indicator only. Check assertions (mutation mindset).
- "I remember the framework default" — Verify project versions and applicable current sources.
- "I'll mock everything for isolation" — Over-mocking tests the mocks, not the behavior. See `test-doubles.md`.
- "Tools found nothing, tests are fine" — Tools miss classes. Manual Phase 4 review is mandatory.
- "It's just a flaky test, I'll add a retry" — Retries mask flakiness; fix the root. See `flaky-tests.md`.
- "I'll rewrite the expectation to match my code" — Requirements are authoritative; justify and review genuine test corrections.

**ALL of these mean: STOP. Return to the relevant phase.**

## User Signals You're Doing It Wrong

**Watch for these redirections:**
- "Did you actually read the code under test?" — You skipped Phase 1.
- "Why did a reviewer change that file?" — Review is advisory-only; fixes belong to the implementer.
- "Did you watch the test fail?" — You skipped Verify RED (Mode A).
- "Is this a real finding or a guess?" — Evidence missing (`file:line`, the smell).
- "Did you check coverage?" — You skipped Phase 5.
- "How do you know this framework idiom is current?" — You skipped the online deep-dive (Phase 2).
- "What about the code/security quality?" — Out of scope. Hand off to `code-review`/`security-review`.

**When you see these:** STOP. Return to the relevant phase.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Test-after is just as good" | Tests-after are biased by the code; you verify the cases you remembered, not the ones you'd have discovered. Test-first forces failure-proof. |
| "Tests pass, so they're good" | Green tests can be flaky, shallow, over-mocked, or assert on mocks. Review quality. |
| "100% coverage = well-tested" | Coverage is a negative indicator only; it says nothing about assertion strength. Use the mutation mindset. |
| "I remember the framework defaults" | Validate using current version-applicable sources; investigate unresolved claims. |
| "Mock everything for isolation" | Over-mocking tests the mocks, not behavior; shatters on refactor. Use doubles at seams only. |
| "A role boundary is inconvenient" | A method never broadens the caller's authority. |
| "Another agent already tested it" | Assess revision-bound evidence independently; rerun if insufficient or doubtful. |
| "Retries will handle the flakiness" | Retries mask flakiness; fix the root cause. |
| "Too simple to test" | Exceptions require advance approval, reason and alternative verification. |
| "The CI will catch it" | Tests should catch issues before CI. That's the point of this skill. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Understand** | Read API, trace behavior, find seams, read existing tests, locate config | Mental model complete; conventions noted |
| **2. Tooling + Language** | Establish applicable tooling/baseline/source evidence; report gaps | Revision/version relevance checked; installation role respected |
| **3. Gate** | Validate the five elements with the user; ask what's missing | Gate passed; mode(s) confirmed |
| **4. Mode work** | A: Red–Green–Refactor / B: independent findings / C: scoped improvement | Protected tests; role-aware changes |
| **5. Verify** | Assess execution/coverage evidence; investigate doubts | Current revisions covered; limits reported |
| **6. Synthesize** | Deliver implementation/tests or findings; evidence; verdict | Role respected; independent acceptance separate |

## Reference Index

Load these files as needed during the matching phase:

| Reference | Read during | Contents |
|-----------|-------------|----------|
| `references/understanding-code-under-test.md` | Phase 1 | Building the mental model: public API, behavior tracing, seams, existing tests, config |
| `references/online-research-protocol.md` | Phase 2 | Language-specific research triggers, authoritative sources, version verification, report-back |
| `references/tdd-fundamentals.md` | Mode A | Red-Green-Refactor, Three Laws, watch-it-fail, vertical slices and role boundaries |
| `references/test-patterns.md` | Mode A | Chicago vs London, outside-in vs inside-out, triangulation, characterization/golden master, parameterized, property-based & fuzzing, BDD/Gherkin, fixtures |
| `references/test-doubles.md` | Modes A/C | Meszaros taxonomy (dummy/fake/stub/spy/mock), mocks-vs-stubs, over-mocking smell, seams at boundaries |
| `references/assertion-quality.md` | Modes A/B/C | One behavior per test, specific assertions, AAA/Given-When-Then, naming, mutation mindset, weak-assertion patterns |
| `references/test-smells.md` | Modes B/C | Full catalog: assertion roulette, mystery guest, eager test, conditional logic, over-mocking, implementation testing, sleepy, ignored, general fixture |
| `references/flaky-tests.md` | Modes B/C | Causes, detection (re-run, sequential vs parallel, retry-masking), quarantine, root-cause fixes |
| `references/coverage-and-mutation.md` | Modes B/C, Phase 5 | Coverage types, 100% myth, layered thresholds, gap analysis, mutation testing tools & score |
| `references/test-strategies.md` | Strategy advice | Pyramid, trophy, honeycomb, diamond, sociable vs solitary, ice-cream cone & hourglass anti-patterns |

Base directory for this skill: the directory containing this SKILL.md.
Relative paths in this skill (e.g. references/, scripts/) are relative to this base directory.
