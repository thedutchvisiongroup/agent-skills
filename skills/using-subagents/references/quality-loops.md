# Quality Loops

Phase 5 of the skill. **Self-review never replaces independent review.** Every implementation gets reviewed by a sub-agent that is NOT its implementer. This file defines the loop, the triggers, and the limits.

## Contents

- The mandatory loop
- Independent code review (always)
- Security review (conditional trigger)
- Reviewer rules
- The fix loop and its limit
- The final whole-change review
- Evidence rules

## The mandatory loop

```
implement → independent code review → (fix → re-review)× ≤ 3 → approved
                                                        ↘ 3rd failure → escalate to user
```

Per task or per batch of tasks — whichever the approved work plan says. What you may NEVER do: mark implementation work "done" with only the implementer's self-review behind it. Self-review is blind to its own assumptions; that is precisely the failure it cannot catch.

## Independent code review (always)

- **Always, for every implementation** — no exceptions for "small" or "simple" changes. Small changes break production too.
- **Independent**: a different sub-agent from the implementer, with fresh context and no stake in the outcome. The implementer reviewing its own work is not review.
- **Prefer a dedicated review agent** discovered in Phase 2 (it carries a real review method). Fallback: `templates/reviewer.md` on a general-purpose sub-agent.
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

When triggered:

1. Dispatch a **security-specialist reviewer** when one exists (Phase 2 discovery). This can be an approved advisory handoff from the code reviewer (see `references/nesting-policy.md`) when the plan says so — or a direct dispatch by you.
2. When NO specialist exists: do NOT let a general reviewer guess at security. Record the need explicitly: handoff notes with suspect file:line locations, surfaced in your Phase 6 summary to the user.

## Reviewer rules

For every review dispatch:

- **Never tell a reviewer what not to flag.** Limited reviews are blind reviews.
- **Never pre-rate findings** ("it's probably minor"). Severity is the reviewer's call.
- **Never edit the verdict** — you integrate it, you don't negotiate with it.
- **Reviewer is advisory-only**: it reports; it never fixes. Fixes go to the implementer (resumed when possible — see `references/subagent-prompts.md`).

## The fix loop and its limit

`CHANGES_REQUESTED` → resume/dispatch the implementer with the findings → it fixes, re-runs tests, appends a fix report → re-review.

**Max 3 fix iterations per task.** A third failure means the problem is not the code — it's the plan: wrong decomposition, wrong approach, or wrong task size. STOP and escalate to the user with the history. Never start iteration 4 hoping for a different result.

**Never carry open Critical/Important findings into dependent work.** Downstream tasks build on upstream code; broken foundations compound.

## The final whole-change review

Per-task reviews miss cross-task failure: interface drift between tasks, logic duplicated by two implementers, conventions applied inconsistently. In Phase 6, one reviewer passes over the COMPLETE change set (full diff). For small runs (route b, single task) the per-task review and the whole-change review may be the same review — say so in the plan.

## Evidence rules

- The implementer's report carries the test evidence: commands run, real output. Reviewers may re-run when in doubt — they are not required to trust, but they are required to assess the evidence.
- The fix loop's evidence is appended to the same report file: what changed, which tests cover it, command, output.
- Your Phase 6 summary to the user lists: review verdicts per task, the security-review outcome or handoff, the final whole-change verdict, and where all evidence lives.
