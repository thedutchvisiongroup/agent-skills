# Review Feedback Format

Read this during Phase 6 (Synthesize Review). How you report findings determines whether they get acted on. Unlabeled, ambiguous feedback creates friction; labeled, actionable feedback creates progress.

## Contents

- Conventional Comments
- Anatomy of a Good Finding
- Severity-to-Verdict Mapping
- Report Template
- Tone Guidelines
- The Reviewer's Boundaries
- Format Checklist

## Conventional Comments

Prefix every finding with a **label** and a **decoration**:

```
label (decoration): comment
```

The label communicates the *type* of feedback; the decoration communicates whether *action is required*.

### Labels

| Label | Meaning | Blocking? |
|-------|---------|-----------|
| `issue` | A problem with the change — user-facing or internal. Always pair with a concrete recommendation. | Blocking by default |
| `suggestion` | A proposed improvement. Be explicit about what and why. | Non-blocking by default |
| `nitpick` | Trivial, preference-based request. | Never blocking |
| `question` | You need the author's intent before you can judge. | Blocks until answered |
| `todo` | Small, trivial, but necessary change. | Blocking by default |
| `praise` | Highlights something done well. Include at least one sincere praise per review. Never false praise. | — |
| `thought` | Context or an idea worth considering. No action needed. | Never blocking |

### Decorations

- `(blocking)` — must be resolved before merge
- `(non-blocking)` — the author's call

**Rules:**
- `nitpick`, `thought`, and `praise` are NEVER blocking.
- `issue` is blocking unless explicitly marked `(non-blocking)`.
- Every blocking finding MUST include its rationale ("because…") — an unexplained blocking finding is a veto, not a review.

## Anatomy of a Good Finding

1. **Label + decoration**
2. **Location** — `file:line`
3. **What** — the observation
4. **Why** — the impact, because…
5. **Recommendation** — the concrete action

**Bad:**
> This is wrong.

**Good:**
> `issue (blocking):` `src/orders/pricing.py:87` — `total` is compared with `==` to a float literal. Because floating-point arithmetic is inexact, this comparison can fail for legitimate values (e.g. `0.1 + 0.2 != 0.3`). Compare with a tolerance, or use a decimal type for money.

## Severity-to-Verdict Mapping

| Findings present | Verdict (advisory) |
|------------------|--------------------|
| Any `issue (blocking)` or `todo (blocking)` | **REQUEST CHANGES** |
| Only non-blocking findings | **APPROVE** (with comments) |
| Open `question`s and nothing blocking | **COMMENT** — await answers |
| No findings | **APPROVE** |

The verdict is always **advisory** — the user makes the final call.

## Report Template

```markdown
## Code Review: <one-line summary of the change>

**Verdict: APPROVE / COMMENT / REQUEST CHANGES** (advisory)

### Automated Checks
| Check | Result |
|-------|--------|
| Lint | ✓ PASS / ✗ FAIL (n errors, n warnings) / — not available |
| Types | ✓ PASS / ✗ FAIL / — not available |
| Format | ✓ PASS / ✗ FAIL / — not available |
| Tests | ✓ PASS (n/n) / ✗ FAIL (n failed) |
| Coverage | n% (n gaps identified) |

### Blocking Findings
1. `issue (blocking):` file:line — what. Why. Recommendation.

### Non-Blocking Findings
- `suggestion:` file:line — …
- `nitpick:` file:line — …

### Questions for the Author
- `question:` file:line — …

### Test Suite Findings
- Flakiness signals, test smells, assertion quality observations
- Coverage gaps + the user's answers / recommendations

### Security Handoff
- User's answer to the security-review question
- Sensitive paths detected (if any) + recommendation for a separate security-review agent

### Praise
- `praise:` …
```

## Tone Guidelines

- **Specific over general** — "rename `d` to `days_since_epoch`", not "names could be better"
- **Rationale over commands** — every finding says *because*
- **Questions over assertions** when uncertain — "I found no references to `X` — still needed?" beats "X is dead code"
- **Address the code, never the author** — "this function", not "you wrote"
- **No nitpick storms** — more than ~3 style nits of the same kind → ONE comment recommending a formatter/linter rule instead of repeating the nit
- **Praise sincerely** — good patterns, clean abstractions, thorough tests. Never manufacture praise; false praise is damaging.

## The Reviewer's Boundaries (restated)

- You deliver findings; the user decides. You NEVER edit code, push fixes, or apply your own suggestions.
- A finding with a code suggestion is still just a finding — the suggested code illustrates the recommendation; it is not applied.
- If the user asks you to fix something: that is a separate task, after the review is delivered.

## Format Checklist

- [ ] Every finding has a label, decoration, location, what, why, and recommendation
- [ ] Every blocking finding has an explicit rationale
- [ ] Findings are ordered: blocking → non-blocking → questions → praise
- [ ] Automated check results table is complete (including "not available" entries)
- [ ] Coverage gaps include the user's answers
- [ ] Security handoff section is present (answer + sensitive-path recommendation if triggered)
- [ ] At least one sincere praise — or none, if genuinely nothing merits it
- [ ] Verdict matches the severity mapping
- [ ] Nothing in the codebase was modified
