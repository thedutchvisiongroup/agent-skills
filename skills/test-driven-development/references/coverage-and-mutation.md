# Coverage and Mutation Testing

Read this during Modes B/C and Phase 5. Coverage measures **how much** code runs; mutation testing measures **whether tests would catch bugs**. Coverage is necessary but not sufficient; mutation testing is the stronger signal.

## The Core Truth

> "Coverage metrics are a good negative indicator but a bad positive one. Low coverage is a certain sign of trouble, but high coverage doesn't automatically mean your test suite is high quality." — Vladimir Khorikov

- **Low coverage** → untested code → bugs waiting to happen.
- **100% coverage** → every line ran; says **nothing** about whether assertions catch bugs. A test that calls code but asserts nothing still produces 100% coverage of those lines.
- Use coverage as a **gap-finder and trend**, not a target to chase.

## Coverage Types (from weakest to strongest)

| Type | Measures | Notes |
|------|----------|-------|
| **Line / statement** | Did each line execute? | Weakest; 100% line can be 50% branch |
| **Function** | Was each function called? | Coarse; misses internal branches |
| **Branch** | Did each branch (true/false of `if`/`case`/`&&`/`\|\|`) execute? | The practical default; what most teams should target |
| **Condition (MC/DC)** | Each boolean sub-expression evaluated both ways | Matters for critical/safety code; 4 cases for `a && b` |
| **Path** | Every possible path through a function | Combinatorial explosion (10 branches ≈ 1024 paths); a theoretical ideal, not an operational goal |

Assess branch coverage when available. Reviewers recommend reporting changes; implementers apply them only within explicitly approved scope.

## Reading a Report

```
Name                  Stmts   Miss  Cover   Branch  Missing
src/auth/login.py        45     12    73%      60%   45-50, 67, 89
```
Focus on: **Missing** lines, **Branch** column (often lower than line), and changed/critical files first.

## Identifying Gaps (priority order)

1. **New/modified behavior without meaningful tests** — report gaps in B; implementer adds tests in A unless an explicit advance exception applies.
2. **Error-handling paths** — frequently untested; high bug density.
3. **Branches (else, fall-through)** — the gap between line and branch coverage.
4. **Boundary/edge cases** — empty, zero, negative, MAX/MIN, pagination.
5. **Async/concurrent paths** — failure, timeout, partial failure.

## The 100% Myth

100% line coverage can be achieved with **zero assertions** — call every line, assert nothing. The suite is green, the report is perfect, and it catches no bug. This is why coverage alone is a weak positive signal.

Don't chase 100%. Integration seams may better cover framework glue/wrappers. Exclusions require a justified approved change, never conceal lost checks; reviewers recommend rather than edit.

## Mutation Testing (the stronger signal)

Mutation testing answers "would my tests catch a bug?" by **injecting faults** and checking whether any test fails:
1. **Mutate** — change `>` to `>=`, swap `&&`/`||`, delete a line, change a constant.
2. **Run tests.**
3. **Evaluate** — use the tool's documented states: detected valid faults provide evidence of sensitivity; a survivor is an investigation lead, not automatically a weak-test finding. Distinguish equivalent/invalid/error states.

Use the selected tool's documented score and state definitions. An equivalence-adjusted conceptual score is killed / (total − demonstrably equivalent), but tools do not automatically or definitively identify all equivalent mutants.
Equivalent mutants preserve observable behavior and cannot be killed by a behavior test. Investigate survivors: distinguish real non-equivalent faults from equivalence, exclusions, invalid mutants and tool errors. Justify exclusions and report uncertainty; a survivor alone is not proof of a weak assertion.

### Score interpretation

Use scores to prioritize investigation and compare like-for-like tool versions, operators, valid states and source/test scope. A score alone never proves weak assertions, cosmetic coverage, defect severity, or absence of bugs. Equivalent survivors, exclusions, invalid/error states and unrepresentative operators can materially affect interpretation.

Inspect survivors and establish the observable non-equivalent behavioral fault before recommending a test/source correction. Report the applicable denominator and uncertainty; any project threshold is an explicitly agreed monitoring goal, not a universal quality classification.

Do **not** chase 100% mutation score — equivalent mutants make some survivors unavoidable. The goal is a high score on **meaningful** mutants.

## Mutation Tools (verify applicability and installation authority)

| Language | Tool |
|----------|------|
| Java | **PITest** (mature, widely used) |
| JS/TS | **Stryker** (StrykerJS), **mutode** |
| .NET | **Stryker.NET** |
| Python | **mutmut**, **Cosmic Ray** |
| Rust | **cargo-mutants** |
| Swift | **Muter** |
| Go | **go-mutesting** (less mature) |

Mutation checks can be expensive and need stable tests. Prefer changed/critical scope or scheduled runs; assess applicable existing evidence first. Reviewers report missing tooling/benefit; installation is a separately approved implementation task.

## Layered Coverage Targets (propose, then confirm in Phase 3)

| Code tier | Branch coverage target | Mutation testing |
|-----------|------------------------|------------------|
| Core business logic / financial rules | 90–95% | Yes (nightly / pre-merge on changes) |
| API endpoints / services | 80–90% | Optional |
| Standard features | 60–80% | No |
| Cosmetic / disposable / prototypes | 30% or none | No |

Propose these defaults, never impose them. Confirm via user/gate or matching approved contract. Reviewers never edit config; implementer may enforce an explicitly approved threshold within scope.

## Coverage Anti-Patterns (report in Mode B)

- **Testing for coverage, not behavior** — tests that call code to hit lines, with no meaningful assertions.
- **Over-mocking for coverage** — mock everything so the test "covers" the unit; assertions are on mocks.
- **Ignoring the report** — running coverage but never reading `term-missing` / the missing-lines column.
- **Flat thresholds** — a blanket "80%" that over-invests in glue and under-invests in core logic. Tier instead.
- **Chasing the number** — adding tests that exist only to move the percentage, with no defect-catching value.

## Checklist

- [ ] Assessed applicable revision-bound coverage or executed the tool; reported absence/inapplicability
- [ ] Identified gaps in changed/critical files, prioritized (errors > branches > lines)
- [ ] Asked the user about each significant gap (or confirmed via the Phase 3 goals)
- [ ] Recommended tests for review gaps; changes respected the calling role
- [ ] Where relevant, assessed applicable mutation evidence or ran focused checks for unanswered doubts; investigated survivors and reported only established non-equivalent behavioral gaps
- [ ] Confirmed coverage meets the agreed tiered goals — or reported gaps
- [ ] Respected installation authority; reviewers installed nothing and reported gaps/benefit

## See Also
- `assertion-quality.md` — the manual mutation mindset.
- `test-smells.md` — coverage theater as a smell.
- `test-strategies.md` — tiered targets by code importance.
