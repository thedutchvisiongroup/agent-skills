# Complexity Review

Read this during Phase 5 (Design and Maintainability). Complexity thresholds are review SIGNALS, not laws — they tell you where to look, not what to verdict.

## Contents

- The Standard
- Signals and Heuristic Thresholds
- Cyclomatic vs. Cognitive Complexity
- Remedies to Recommend
- When Complexity Is Acceptable
- Review Checklist

## The Standard

"Too complex" usually means one of two things:

1. **Can't be understood quickly by code readers**
2. **Developers are likely to introduce bugs when they call or modify this code**

Judge against these, not against a number. The numbers below only tell you where to look closer.

## Signals and Heuristic Thresholds

| Signal | Heuristic | What to recommend |
|--------|-----------|-------------------|
| Function length | > ~40–60 lines | Extract well-named units |
| Nesting depth | > 3–4 levels | Guard clauses, early returns, extraction |
| Parameter count | > ~3–4 | Parameter object / options struct |
| Cyclomatic complexity | > ~10 per function | Split decision logic |
| Class size | Many unrelated fields + methods | SRP split (see `design-principles.md`) |
| Boolean/flag parameters | Any | The function does two things — split it |
| Long call chains ("train wrecks") | `a.b.c.d.e` | Tell-don't-ask; move behavior to the owner |
| Inheritance depth | > 2–3 levels | Prefer composition |
| Long lambdas/callbacks | > ~10 lines | Extract to a named function |

A function violating one signal is a look-closer. A function violating several is a finding.

## Cyclomatic vs. Cognitive Complexity

- **Cyclomatic complexity** counts independent paths through the code (decision points + 1). It is a *testability* proxy: N paths means at least N test cases for full path coverage. Cross-reference with coverage findings in Phase 3.
- **Cognitive complexity** measures how hard code is to *follow*: nesting adds weight, breaks in linear flow add weight, early returns reduce it. Deeply nested but simple logic can score low cyclomatic and high cognitive — and vice versa.

Both matter; cognitive complexity is usually the better predictor of review friction.

## Remedies to Recommend

- **Extract function** — give the block a name; the name is the documentation
- **Guard clauses / early returns** — flatten "arrow code" so the happy path reads top-to-bottom at one indentation level
- **Replace conditional with lookup/strategy/polymorphism** — where the codebase already uses that idiom (don't invent infrastructure; see YAGNI in `design-principles.md`)
- **Introduce explaining variable** — `is_retryable = status in (502, 503)` instead of an inline boolean puzzle
- **Parameter object** — collapse long parameter lists that travel together
- **Split multi-duty loops** — one loop, one job

## When Complexity Is Acceptable

Do NOT flag complexity when:

- **The problem is inherently branchy** — algorithms, parsers, state machines, protocol handling. Judge these by their tests and documentation instead: well-tested + well-documented essential complexity is fine.
- **The code is generated** — excluded from review anyway.
- **Extraction has a measured performance cost** on a proven hot path (see `performance-review.md` — measurement required, not speculation).
- **The complexity matches the problem's essential complexity** — simplification would just move it, not remove it.

The follow-up question for acceptable complexity: *is it covered by tests and explained by documentation?* If yes — leave it. If no — flag the missing tests/docs, not the complexity.

## Review Checklist

- [ ] Every long function checked against the signal table
- [ ] Nesting depth > 3 examined for guard-clause flattening
- [ ] Parameter lists > 4 examined for natural groupings
- [ ] High cyclomatic functions cross-checked with Phase 3 coverage (are all paths tested?)
- [ ] Boolean flag parameters flagged as split candidates
- [ ] Acceptable-complexity cases verified against tests + docs instead of flagged
- [ ] Remedies recommended follow codebase idioms — no framework-building
