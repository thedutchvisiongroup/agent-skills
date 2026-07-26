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

Most tools default to line/statement; **branch coverage is what actually matters**. Switch the project's report to branch if available.

## Reading a Report

```
Name                  Stmts   Miss  Cover   Branch  Missing
src/auth/login.py        45     12    73%      60%   45-50, 67, 89
```
Focus on: **Missing** lines, **Branch** column (often lower than line), and changed/critical files first.

## Identifying Gaps (priority order)

1. **New/modified functions without tests** — MUST add tests (Mode A).
2. **Error-handling paths** — frequently untested; high bug density.
3. **Branches (else, fall-through)** — the gap between line and branch coverage.
4. **Boundary/edge cases** — empty, zero, negative, MAX/MIN, pagination.
5. **Async/concurrent paths** — failure, timeout, partial failure.

## The 100% Myth

100% line coverage can be achieved with **zero assertions** — call every line, assert nothing. The suite is green, the report is perfect, and it catches no bug. This is why coverage alone is a weak positive signal.

**Don't chase 100%.** Some code is genuinely untestable (third-party wrappers, framework glue); mark it excluded (`# pragma: no cover`, `/* istanbul ignore */`, `#[allow(...)]`) with a reason, rather than writing tests that exist only to hit lines.

## Mutation Testing (the stronger signal)

Mutation testing answers "would my tests catch a bug?" by **injecting faults** and checking whether any test fails:
1. **Mutate** — change `>` to `>=`, swap `&&`/`||`, delete a line, change a constant.
2. **Run tests.**
3. **Evaluate** — tests fail → mutant **killed** (good). Tests pass → mutant **survived** (weak test gap).

**Mutation score** = Killed Mutants / (Total Mutants − Equivalent Mutants).
Equivalent mutants change code in a way that produces identical behavior (e.g. `i++` → `i += 1`) — no test can kill them; tools exclude them automatically.

### Score interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 90–100% | Excellent — assertions tightly check behavior | Maintain; guard with a CI threshold |
| 75–89% | Good — minor gaps | Kill survivors opportunistically |
| 60–74% | Mediocre — many weak assertions | Schedule a hardening sprint |
| <60% | Poor — coverage largely cosmetic | Treat as untested; prioritize critical paths |

Do **not** chase 100% mutation score — equivalent mutants make some survivors unavoidable. The goal is a high score on **meaningful** mutants.

## Mutation Tools (research the current state — do NOT install)

| Language | Tool |
|----------|------|
| Java | **PITest** (mature, widely used) |
| JS/TS | **Stryker** (StrykerJS), **mutode** |
| .NET | **Stryker.NET** |
| Python | **mutmut**, **Cosmic Ray** |
| Rust | **cargo-mutants** |
| Swift | **Muter** |
| Go | **go-mutesting** (less mature) |

Mutation testing is **slow** (10–100x coverage) and **needs a stable suite first** (flaky tests break mutation runs). Run it nightly or on changed files only, not on every save. Never install a mutation tool — report it missing-with-benefit and let the user add it.

## Layered Coverage Targets (propose, then confirm in Phase 3)

| Code tier | Branch coverage target | Mutation testing |
|-----------|------------------------|------------------|
| Core business logic / financial rules | 90–95% | Yes (nightly / pre-merge on changes) |
| API endpoints / services | 80–90% | Optional |
| Standard features | 60–80% | No |
| Cosmetic / disposable / prototypes | 30% or none | No |

These are **defaults to propose**, not impose. Confirm with the user in the Phase 3 gate. Enforcing thresholds (e.g. `--cov-fail-under=80`, jest `coverageThreshold`) is the project's call, not yours — you never edit config to enforce.

## Coverage Anti-Patterns (report in Mode B)

- **Testing for coverage, not behavior** — tests that call code to hit lines, with no meaningful assertions.
- **Over-mocking for coverage** — mock everything so the test "covers" the unit; assertions are on mocks.
- **Ignoring the report** — running coverage but never reading `term-missing` / the missing-lines column.
- **Flat thresholds** — a blanket "80%" that over-invests in glue and under-invests in core logic. Tier instead.
- **Chasing the number** — adding tests that exist only to move the percentage, with no defect-catching value.

## Checklist

- [ ] Ran coverage tool (project's own) and read the report (missing lines + branch column)
- [ ] Identified gaps in changed/critical files, prioritized (errors > branches > lines)
- [ ] Asked the user about each significant gap (or confirmed via the Phase 3 goals)
- [ ] Recommended concrete tests for accepted gaps (Mode A) — did NOT write production code
- [ ] (If a mutation tool is available and code is critical) ran it; reported surviving mutants as weak-assertion findings
- [ ] Confirmed coverage meets the agreed tiered goals — or reported gaps
- [ ] Did NOT install anything; reported missing tools with their benefit

## See Also
- `assertion-quality.md` — the manual mutation mindset.
- `test-smells.md` — coverage theater as a smell.
- `test-strategies.md` — tiered targets by code importance.
