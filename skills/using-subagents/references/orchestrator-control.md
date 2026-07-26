# Orchestrator Control

Phase 4 steering rules: how to stay in control of running work without doing the work. Read together with `references/subagent-prompts.md` (contracts) and `references/failure-modes.md` (what happens when you don't).

## Contents

- The ledger
- Status handling
- Answering NEEDS_CONTEXT
- Handling BLOCKED
- Never duplicate delegated work
- Abort criteria and re-planning
- Cost awareness

## The ledger

A durable progress ledger — inside the plan file — is your external memory. It survives context compaction and prevents double-dispatch:

```
| Task | Agent | Status | Report |
|------|-------|--------|--------|
| 1. Auth config | implementer (general) | DONE | .agents/runs/…/task-1-report.md |
| 2. Google adapter | implementer (general) | IN FLIGHT | — |
| 3. GitHub adapter | implementer (general) | IN FLIGHT | — |
| Review T1 | code-reviewer | APPROVED | .agents/runs/…/task-1-review.md |
```

Rules:

- Update on every dispatch and every return. One line per event.
- **Never re-dispatch a task the ledger marks complete.** If the ledger says DONE but the report file is missing, the task is NOT done — investigate, don't re-run blindly.
- The ledger is the last thing you update before any compaction-risk moment.

## Status handling

| Status | Meaning | Your action |
|--------|---------|-------------|
| `DONE` | Complete, criteria met | Verify report exists; spot-check at integration; continue |
| `DONE_WITH_CONCERNS` | Complete, with doubts | READ the concerns. Accept and note them, or attach them to the Phase 5 review brief |
| `NEEDS_CONTEXT` | Missing info | Answer from your context, or bundle to the user (see below) |
| `BLOCKED` | Cannot complete | Re-plan (see below). Never just re-send the same prompt |

A status is a claim, not a fact. At integration time, claims are checked against diffs and test runs.

## Answering NEEDS_CONTEXT

1. **Answer it yourself when you can** — you hold the plan, the user's constraints, and the conversation. Redispatch (or resume) with the answer added to the contract.
2. **Bundle to the user when you can't** — collect the question(s), add your own if the blocker reveals plan ambiguity, and ask ONCE. Never relay questions piecemeal: three sub-agents asking separately is exactly the multi-interruption failure this skill forbids.
3. **Record the answer** in the plan file — it is a decision, and decisions belong in the plan.

## Handling BLOCKED

BLOCKED is information, not failure. The sub-agent told you the task as specified doesn't work. Options, in order:

1. **More context** — the brief missed something; resume with it.
2. **Smaller scope** — split the task at the blocker; dispatch the unblocked half.
3. **Stronger model** — the task outclasses the routed model; re-dispatch with more capability (note the cost).
4. **Back to the user** — the task needs a human decision, new information, or a plan change. Escalate with the BLOCKED specifics.

Never dispatch the identical prompt hoping for a different outcome — that is the definition of a loop.

## Never duplicate delegated work

While a sub-agent runs, you do NOT "also take a look", "prepare the fix", or "draft the same thing just in case". Duplication wastes tokens and, worse, creates two competing versions of the same work.

Legitimate orchestrator work while waiting: update the ledger, prepare the NEXT wave's contracts (against planned dependencies, not against running tasks), read completed report files, or simply wait.

## Abort criteria and re-planning

The approved plan contains abort criteria. Fire them honestly:

- Fix iteration 3 failed on any task → STOP, escalate to the user (see `references/quality-loops.md`).
- Same task BLOCKED twice → the decomposition is wrong; re-plan with the user.
- Scope grows beyond the plan → re-approve the delta (see `references/work-plan.md`).
- Parallel wave produces conflicts → reconcile before any new dispatch.

Aborting is not failing. Burning another wave on a broken plan is failing.

## Cost awareness

You are spending the user's tokens with every dispatch:

- Check the gate's effort scaling before adding agents mid-run.
- Prefer resuming over fresh dispatches for fix loops.
- Model routing: don't pay strong-model prices for mechanical leaves.
- When loops appear (repeated failures, NEEDS_CONTEXT ping-pong), STOP spending and re-think — loops are decomposition problems, not prompt problems.
- If the user set a budget in Before-You-Start, track against it and say so when you approach it.
