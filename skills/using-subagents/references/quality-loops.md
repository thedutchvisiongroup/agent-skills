# Quality Loops

Each phase/batch needs independent code and post-implementation TDD review, plus risk-triggered security review. Self-review never replaces acceptance. Only a separately explicit advance-approved test-review exception removes the TDD seat.

## Contents

- The mandatory loop
- Independent TDD review (after implementation)
- Independent code review (always)
- Security review (conditional trigger)
- Reviewer rules
- The fix loop and its limit
- The final whole-change review
- Evidence rules

## The mandatory loop

```
implementer (tests + source, Red–Green–Refactor)
 → code + TDD review [+ security]
 → (resume implementer → affected re-reviews)× ≤ 3 → accepted batch
    ↘ third unsuccessful fix round → escalate to user
```

Plan phase/batch Definitions of Done; additional per-task reviews are optional approved granularity. Worker DONE means execution complete, not phase acceptance. All required verdicts and resolved blockers precede dependent work.

## Independent TDD review (after implementation)

- Dispatch `tdd-expert` in advisory B after each phase/batch, never as separate Red/Green workers.
- Inputs: original approved behavior, source/test changes, revision-bound Red/Green/final proof, research/tooling evidence and exceptions.
- Assess assertion strength, independent expectations, boundaries/errors, over-mocking, determinism/coverage and test-contract changes; Green alone is insufficient.
- Reviewer never edits tests/source. Fixes return to implementer; direct specialist authoring is separate.
- New-test and TDD-review exceptions each require advance approval, reason and alternative checks. No new tests does not exempt review of regression coverage/verification strategy.
- Missing required reviewer blocks acceptance; task size/absent tooling never silently exempts it.

## Independent code review (always)

- **Always, for every implementation** — no exceptions for "small" or "simple" changes. Small changes break production too.
- **Independent**: a different sub-agent from the implementer, with fresh context and no stake in the outcome. The implementer reviewing its own work is not review.
- Use live `code-reviewer`; elsewhere only explicitly approved equivalents, never silent disabled-general fallback.
- **Input**: the diff file + the implementer's report (with its test evidence) + the task brief with acceptance criteria. Never "review the repo" — review the change.
- **Verdict contract**: `APPROVED` | `CHANGES_REQUESTED` | `NEEDS_CONTEXT`, with findings labeled Critical / Important / Minor.

## Security review (conditional trigger)

Security review is NOT part of every loop. Trigger it when the change touches **sensitive paths**:

- authentication / authorization, session handling
- payments, financial flows
- personal data (PII), privacy-sensitive export
- cryptography, randomness, secrets handling
- file uploads, parsers of external input
- permission checks, role changes, admin actions
- dependencies/lockfiles and security-relevant config/IaC

When triggered:

1. Dispatch a **security-specialist reviewer** when one exists (Phase 2 discovery). This can be an approved advisory handoff from the code reviewer (see `references/nesting-policy.md`) when the plan says so — or a direct dispatch by you.
2. Missing required specialist blocks acceptance; resolve availability or ask the user to amend the plan. A handoff note is not approval.

Parallel code/TDD/security reviews require frozen inputs, separate reports and non-conflicting probes. Contracts name scheduled seats; new signals go to coordinator instead of duplicate nested reviews.

## Reviewer rules

For every review dispatch:

- **Never tell a reviewer what not to flag.** Limited reviews are blind reviews.
- **Never pre-rate findings** ("it's probably minor"). Severity is the reviewer's call.
- **Never edit the verdict** — you integrate it, you don't negotiate with it.
- **Reviewer is advisory-only**: it reports; it never fixes. Fixes go to the implementer (resumed when possible — see `references/subagent-prompts.md`).

## The fix loop and its limit

Consolidate findings → resume implementer → amended-revision checks → append evidence → affected re-reviews. Changes invalidating an approved seat need its recheck; retain only untouched, still applicable verdicts with scope/revision evidence.

**Max 3 fix iterations per task.** A third failure means the problem is not the code — it's the plan: wrong decomposition, wrong approach, or wrong task size. STOP and escalate to the user with the history. Never start iteration 4 hoping for a different result.

**Never carry open Critical/Important findings into dependent work.** Downstream tasks build on upstream code; broken foundations compound.

## The final whole-change review

Per-task reviews miss cross-task failure: interface drift between tasks, logic duplicated by two implementers, conventions applied inconsistently. In Phase 6, one reviewer passes over the COMPLETE change set (full diff). For small runs (route b, single task) the per-task review and the whole-change review may be the same review — say so in the plan.

## Evidence rules

- Reports identify revision/fingerprint, scope, commands/output, versions/environment. Reviewers check applicability and analyze independently; gaps/staleness/doubt require focused checks/research, not automatically repeated full suites.
- The fix loop's evidence is appended to the same report file: what changed, which tests cover it, command, output.
- Phase 6 lists code/test/security verdicts, exceptions, integration outcome, executed/reused evidence and locations.
