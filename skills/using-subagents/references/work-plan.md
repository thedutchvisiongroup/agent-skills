# The Work Plan

Phase 3 of the skill. **NO DISPATCH WITHOUT A WORK PLAN THE USER HAS EXPLICITLY APPROVED.** This file contains the plan template, the approval protocol, and the storage-location gate.

## Contents

- Why a plan, always
- The plan template
- The storage-location gate
- The approval protocol
- Lightweight plans (route b)
- Mid-run changes and re-approval

## Why a plan, always

The plan is the only artifact that forces the orchestrator to think before spending. It makes the decomposition reviewable by the one person who can catch a wrong split cheaply: the user. Research on multi-agent systems is unambiguous — vague delegation causes duplicated work, gaps, and conflicting decisions. The plan is where vagueness dies.

Even for a single dispatch (route b) you write a plan — a short one. The discipline scales, never disappears.

## The plan template

Write the plan to the confirmed storage location (see below) using this structure:

```markdown
# Work Plan: [TASK NAME]
- **Date:** [date]
- **Route:** (b) one sub-agent | (c) orchestrator mode
- **Storage:** [this directory — plan file + report files]

## Goal & success criteria
[What "done" looks like, measurably — from the Before-You-Start answers]

## Available agents (from Phase 2 discovery)
[agent — one-line capability note. Include deliberate non-choices.]

## Tasks
### Task 1: [name]
- **Agent:** [discovered agent | template fallback on general-purpose]
- **Model:** [routing choice, if the harness supports it]
- **Scope/files:** [what it may touch — the disjointness claim]
- **Depends on:** [nothing | Task N]
- **Parallel-safe with:** [Task M — because scopes are disjoint] 
- **Acceptance criteria:** [measurable]
- **Quality loop:** code review (always) [+ security review — because: sensitive path X]
[### Task 2: ...]

## Nesting (if any)
[Only approved advisory handoffs, depth ≤ 2 — see references/nesting-policy.md.
 Otherwise: "None — all dispatching is done by the orchestrator."]

## Integration & final verification
[Conflict check, full test suite, final whole-change review — Phase 6]

## Abort criteria
[When to stop and re-plan: e.g. "3rd fix iteration on any task", "BLOCKED twice on the same task", "scope grows beyond N files"]

## Ledger
[task — agent — status — report path. Updated throughout Phase 4.]
```

## The storage-location gate

**ALWAYS ask the user where the plan and reports live.** This is not bureaucracy: unfindable reports are unreviewable work, and scattered artifacts defeat the file-handoff pattern (see `references/context-engineering.md`).

- Propose a default: `.agents/runs/<date>-<task-slug>/` inside the project (report files, plan, ledger in one place).
- The user confirms or overrides. Their answer goes in the plan header.
- One directory per run. Never spread reports across the repo.

## The approval protocol

1. Present the plan AND the storage location together — compactly, in chat.
2. **WAIT for explicit approval.** Approval = the user said yes in so many words ("oké", "go", "approved"). Silence, absence of objection, or your own confidence are NOT approval.
3. Approval covers: the decomposition, the agent assignment, the parallel/sequential choices, the quality loops, any nesting, and the storage location.
4. Only then: Phase 4.

If the user adjusts the plan, incorporate and re-present briefly — the amended plan needs its own yes.

## Lightweight plans (route b)

For a single dispatch, the plan collapses to:

- Goal & acceptance criteria
- The one agent (or template) + model choice
- Quality loop (what review applies)
- Storage location
- Abort criterion (usually: "BLOCKED → come back to the user")

Same rule: explicit approval before dispatch. For genuinely small dispatches the user may wave you through quickly — but THEY wave, you don't skip.

## Mid-run changes and re-approval

The approved plan is a contract with the user. STOP and re-approve the delta when:

- A new task appears (scope growth)
- An agent assignment changes materially
- Sequential work wants to become parallel (or the reverse)
- Nesting is added
- An abort criterion fires

Re-approval is cheap: show the delta, get a yes, update the plan file, continue.
