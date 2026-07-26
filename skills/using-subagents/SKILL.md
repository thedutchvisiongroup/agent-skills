---
name: using-subagents
description: Orchestrates sub-agents for multi-step coding work. Starts with a mandatory Delegation Gate that decides between doing it directly, dispatching one sub-agent, or full orchestrator mode — in which the main agent NEVER writes code and only delegates, steers, and verifies. Enforces live sub-agent discovery, a work plan that requires explicit user approval (including the storage location) before any dispatch, delegation-contract prompts with a mandatory status contract (DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT) plus report files, quality loops with independent code review after every implementation (max 3 fix iterations, then escalate; security review only for security-relevant work), parallel writing only for provably disjoint scopes, and recursion limited to depth 2 for approved advisory handoffs only. Use for feature implementation, large refactors, multi-part bug hunts, or any task big enough to delegate. Not for trivial edits or tightly coupled work the main agent should do directly.
---

# Using Subagents

## The Iron Law

```
IN ORCHESTRATOR MODE YOU DELEGATE, STEER, AND VERIFY. YOU NEVER WRITE CODE.
NO DISPATCH WITHOUT A WORK PLAN THE USER HAS EXPLICITLY APPROVED.
NO IMPLEMENTATION IS DONE WITHOUT INDEPENDENT REVIEW.
```

An orchestrator that writes code is not an orchestrator — it is an author with extra steps. And a sub-agent dispatched without a contract is not a worker — it is a guess with a budget.

**You MUST complete each phase before proceeding to the next.**

## Overview

Sub-agent orchestration means: the main agent decomposes a task, dispatches bounded pieces to fresh sub-agents, and integrates their verified results. Done well, this buys clean context, focused expertise, and safe parallelism. Done badly, it buys duplicated work, conflicting decisions, and a multiplied token bill.

**Core principles:**

1. **The orchestrator owns every decision.** Sub-agents execute bounded tasks; they NEVER make architectural choices, NEVER talk to the user directly, and NEVER see the whole plan. Actions carry implicit decisions — so every decision that matters must be explicit in the delegation contract.
2. **Fresh context is the feature.** A sub-agent's value is its clean context window. Feed it a bounded brief, NEVER the conversation history.
3. **Delegation has a real cost.** Every dispatch writes a fresh system prompt and burns tokens. The Delegation Gate (Phase 1) exists to make sure the task is worth it.

## When to Use

Use when a task is big enough to delegate:

- Feature implementation spanning multiple files or modules
- Large refactors with separable workstreams
- Multi-part bug hunts with independent root causes
- Breadth-first exploration of an unfamiliar codebase
- Work whose verbose intermediate output would flood the main context

**Use this ESPECIALLY when:**

- The task decomposes into clearly independent parts
- You would otherwise lose the thread in a long session
- Independent review of the work matters (it always does — see Phase 5)

## When NOT to Use

- **Trivial or mechanical edits** — a typo fix, a rename, a config tweak: do it directly (Phase 1 decides)
- **Tightly coupled changes** — every file depends on every other file; delegation only adds telephone
- **High-stakes exploratory work** — architecture decisions, ambiguous requirements: these need continuous user dialogue, not dispatch
- **Sequential dependency chains** — step B cannot start without step A's output: one sub-agent or direct work, never fan-out

## Before You Start

You MUST confirm the following with the user (before or during Phase 1–3):

- [ ] **Scope & success criteria**: what does "done" look like, measurably?
- [ ] **Context**: what triggered this work? (feature, bug, refactor)
- [ ] **Constraints**: forbidden areas, time/token budget, agents or models to prefer or avoid?

**If any are unclear, ASK the user before proceeding.** The work plan (Phase 3) separately confirms the storage location and requires explicit approval.

## The Six Phases

### Phase 1: Delegation Gate (ALWAYS)

Decide the route BEFORE any work:

**(a) Do it yourself** — the task is trivial, tightly coupled to the conversation, or needs continuous user judgement. Execute directly. This skill ends here.

**(b) One sub-agent** — one bounded task that benefits from a fresh context (or would flood yours). You become the orchestrator for that single dispatch; Phases 2–6 apply in lightweight form.

**(c) Orchestrator mode** — the task decomposes into multiple sub-tasks. You become a strict orchestrator: you NEVER write code, edit files, or run mutating commands for the delegated scope. You delegate, steer, verify, integrate.

Read `references/delegation-gate.md` for the full decision criteria, the cost check, effort scaling, and worked examples.

```
STOP. Did you pass the gate?
- [ ] Yes, I chose route (a), (b), or (c) deliberately, with reasons
- [ ] Yes, I checked the task is worth the delegation overhead (routes b/c)
- [ ] Yes, I accept that routes (b)/(c) forbid me to write code for the delegated scope
If any box is unchecked: GO BACK to the gate criteria.
```

### Phase 2: Sub-agent Discovery (ALWAYS when delegating)

NEVER dispatch to an assumed agent. Inventory what actually exists in THIS environment:

1. **List available sub-agents** via the harness's live mechanism (task-tool listing, agent directories — see `references/harness-notes.md`). Never rely on memory: agents differ between projects and machines.
2. **Read each agent's description** — it is the capability contract: what it does, when to use it, what it may not do.
3. **Match tasks to agents**: specialist over generalist. A dedicated review agent beats a generic prompt every time.
4. **Handle gaps**: no fitting agent → dispatch a general-purpose sub-agent with the matching template from `templates/`. If a missing specialist would have recurring value, RECOMMEND the user create it — NEVER create agents yourself (that is writing config: forbidden in orchestrator mode).
5. **Consider model routing**: cheap/fast models for mechanical work, strong models for planning and review — record the choices in the work plan.

Read `references/subagent-discovery.md` for the matching matrix and fallback rules.

```
STOP. Is your inventory live?
- [ ] Yes, I listed the actually-available sub-agents in THIS environment
- [ ] Yes, I read their descriptions before matching
- [ ] Yes, every planned dispatch has a real agent or a template fallback
If any box is unchecked: GO BACK and discover.
```

### Phase 3: Work Plan (ALWAYS) — Requires Explicit User Approval

NO DISPATCH WITHOUT AN APPROVED WORK PLAN. Build the plan per `references/work-plan.md`:

1. **Goal & success criteria** (from Before You Start)
2. **Decomposition** — tasks with an independence analysis (see `references/task-decomposition.md`): which may run in parallel (provably disjoint scope — see `references/parallel-execution.md`), which must be sequential
3. **Agent assignment** per task (from Phase 2), including model routing
4. **Quality loops** per task (Phase 5 minimums: independent code review ALWAYS; security review only for security-relevant work)
5. **Nesting**, if any — only advisory handoffs, total depth ≤ 2, and only because the plan says so (see `references/nesting-policy.md`)
6. **Integration & final verification** steps (Phase 6)
7. **Abort criteria** — when to stop and re-plan
8. **Storage location** — propose where the plan file and report files live (default: `.agents/runs/<date>-<task>/`). ALWAYS ask the user to confirm or override this location.

Present the plan AND the storage location. **WAIT for explicit user approval.** Approval means the user said yes in so many words. Silence, implied consent, or your own enthusiasm are not approval.

Did the approved plan change mid-run (new tasks, different agents, added nesting)? STOP and re-approve the delta with the user.

```
STOP. Is the plan approved?
- [ ] Yes, the plan follows the template (goal, decomposition, agents, loops, integration, abort criteria)
- [ ] Yes, the storage location is explicitly confirmed
- [ ] Yes, the user said yes — explicitly
If any box is unchecked: DO NOT DISPATCH.
```

### Phase 4: Execution — Dispatch and Steer

Per task, dispatch with a full delegation contract (use `templates/`; see `references/subagent-prompts.md`):

- **Objective** — one bounded task
- **Context** — scene-setting for THIS task only (see `references/context-engineering.md`)
- **Boundaries** — what NOT to touch; no interactive ask-the-user tools; no dispatching sub-agents (unless approved nesting)
- **Acceptance criteria** — measurable
- **Output contract** — report file + a <15-line status message (`DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT`)

Steering rules (deep rules in `references/orchestrator-control.md`):

1. **Track progress in a ledger** (it survives context compaction): task → agent → status → report path.
2. **Parallel**: dispatch multiple sub-agents in ONE message only when the plan marked them parallel-safe. Read-only work (explorers) is always parallel-safe. Writing is parallel-safe ONLY for provably disjoint scopes. Never re-dispatch a task the ledger marks complete.
3. **Never duplicate delegated work.** While a sub-agent runs, do other non-overlapping orchestrator work or wait — do not "also have a look yourself".
4. **Handle statuses:**
   - `DONE` → verify the report exists, continue
   - `DONE_WITH_CONCERNS` → read the concerns; accept them or attach them to the Phase 5 review
   - `NEEDS_CONTEXT` → answer from your own context when you can; otherwise BUNDLE the question(s) to the user in one go — NEVER relay piecemeal
   - `BLOCKED` → re-plan: more context, smaller scope, stronger model, or take it back to the user
5. **Cost awareness**: if dispatches keep failing or looping, STOP and reconsider the decomposition — do not keep spending.

### Phase 5: Quality Loops (ALWAYS after implementation)

Self-review NEVER replaces independent review.

1. **Independent code review — ALWAYS.** After every implementation task (or batch, per the approved plan), dispatch a reviewer that is NOT the implementer (see `references/quality-loops.md`). Never tell a reviewer what not to flag. Never pre-rate findings.
2. **Security review — ONLY when security-relevant.** Trigger when the change touches sensitive paths: authentication/authorization, payments, personal data, cryptography, secrets, file uploads, external input handling, permission checks. Dispatch a security-specialist reviewer when one exists; otherwise record the handoff need explicitly in your final summary.
3. **Fix loop**: `CHANGES_REQUESTED` → dispatch the fix (resume the implementer with the findings when the harness supports it), then re-review. **Max 3 fix iterations per task.** Third failure → STOP and escalate to the user: the plan, the approach, or the task size is wrong.
4. **Never carry open Critical/Important findings** into the next dependent task.

```
STOP. Is quality gated?
- [ ] Yes, every implementation got independent review
- [ ] Yes, security-relevant changes got (or explicitly scheduled) security review
- [ ] Yes, no task exceeded 3 fix iterations without user escalation
- [ ] Yes, no open Critical/Important findings are being carried forward
If any box is unchecked: GO BACK.
```

### Phase 6: Integration & Final Verification

Sub-agent results are NOT visible to the user — you are their messenger.

1. **Conflict check** (after parallel work): verify no two sub-agents touched the same files; reconcile before continuing (see `references/parallel-execution.md`).
2. **Full verification**: run the whole test suite (and lint/type/format checks) over the integrated result — not per task, but over everything together.
3. **Final whole-change review**: one reviewer over the complete change set catches what per-task reviews miss (interface drift, duplicated logic across tasks).
4. **Summarize to the user**: what was built, by which agents, review outcomes, test results, concerns, and where the plan + reports are stored. Close the ledger.

## Red Flags — STOP and Follow Process

If you catch yourself thinking:

- "I'll just make this tiny edit myself" (in orchestrator mode) — you NEVER write code
- "The plan is obvious, the user will approve anyway" — NO dispatch without explicit approval
- "These two tasks share one file but should be fine in parallel" — disjoint or sequential
- "The implementer tested it, review is overkill" — independent review is mandatory
- "The sub-agent can ask the user if unclear" — questions return via status; you own user contact
- "Let me spawn a sub-orchestrator to manage sub-agents" — depth ≤ 2, advisory handoffs only, and only if approved
- "I'll paste the full report into context" — reports live in files; summaries return
- "One more fix iteration" (after 3) — escalate to the user
- "This two-line task deserves its own agent" — the gate exists for a reason
- "I remember which agents exist here" — discovery is live, always

**ALL of these mean: STOP. Return to the relevant phase.**

## User Signals You're Doing It Wrong

**Watch for these redirections:**

- "Why did you edit that file yourself?" — you broke the Iron Law
- "Did I approve that plan?" — you dispatched without approval
- "Why am I getting questions from three different agents?" — sub-agents must escalate via status, not ask
- "Where is the report?" — the status contract was not enforced
- "Why did two agents change the same file?" — the disjointness check failed
- "Where is the review?" — you skipped Phase 5

**When you see these:** STOP. Return to the relevant phase.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Sub-agents make everything faster" | Delegation costs tokens and coordination. Small tasks are faster done directly. |
| "More agents = more parallelism = better" | Parallelism pays only with disjoint scopes; otherwise it buys conflicts. |
| "The sub-agent knows the project conventions" | It starts cold. Unwritten context is unshared context — put it in the contract. |
| "Self-review found nothing" | Self-review is blind to its own assumptions. Independent review is mandatory. |
| "Approval slows things down" | A wrong plan executed autonomously is slower — and pricier. |
| "The sub-agent said DONE" | Verify the report and the review verdict. Trust, but verify. |
| "Asking where to store files is bureaucracy" | Unfindable reports are unreviewable work. |
| "Nested orchestration handles complexity" | It compounds error and cost. Depth ≤ 2, advisory handoffs only. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Gate** | Route: self / one sub-agent / orchestrator | Deliberate choice; delegation is worth the overhead |
| **2. Discovery** | Live inventory, matching, fallbacks, model routing | Every dispatch mapped to a real agent or template |
| **3. Work Plan** | Decompose, assign, loops, abort criteria, storage | Explicit user approval, incl. storage location |
| **4. Execution** | Contracts, ledger, status handling, parallel rules | All tasks DONE-with-reports or escalated |
| **5. Quality** | Independent review, security trigger, fix loops ≤ 3 | All approved; no open Critical/Important findings |
| **6. Integration** | Conflict check, full suite, final review, summary | Verified whole; user informed; ledger closed |

## Reference Index

Load these files as needed during the matching phase:

| Reference | Read during | Contents |
|-----------|-------------|----------|
| `references/delegation-gate.md` | Phase 1 | Route criteria, cost check, effort scaling, worked examples |
| `references/subagent-discovery.md` | Phase 2 | Live inventory, capability matching, fallbacks, model routing |
| `references/work-plan.md` | Phase 3 | Plan template, approval protocol, storage-location gate |
| `references/task-decomposition.md` | Phase 3 | Independence analysis, cohesion, granularity, effort scaling |
| `references/subagent-prompts.md` | Phase 4 | Delegation contract anatomy, status contract, template usage |
| `references/parallel-execution.md` | Phases 3–4, 6 | Disjointness criteria, fan-out limits, integration verification |
| `references/context-engineering.md` | Phases 3–4 | What to include/exclude, file handoffs, summaries-not-dumps |
| `references/orchestrator-control.md` | Phase 4 | Ledger, status handling, escalation, abort, cost control |
| `references/quality-loops.md` | Phase 5 | Review loop, security trigger, fix-loop limits, reviewer rules |
| `references/nesting-policy.md` | Phases 3–4 | Depth ≤ 2, advisory handoffs only, forbidden patterns |
| `references/failure-modes.md` | All phases | Anti-pattern catalog with symptoms and fixes |
| `references/harness-notes.md` | Phases 2–4 | OpenCode / Claude Code mechanics, per-harness mapping |

## Templates

Copy and fill when dispatching (see `references/subagent-prompts.md`):

| Template | Use for |
|----------|---------|
| `templates/implementer.md` | Implementation sub-agents (writes code; status contract) |
| `templates/reviewer.md` | Independent review sub-agents (advisory-only; verdict contract) |
| `templates/explorer.md` | Read-only exploration sub-agents (safe parallel fan-out) |
| `templates/report.md` | The report-file structure sub-agents write their details into |

Base directory for this skill: the directory containing this SKILL.md.
Relative paths in this skill (e.g., references/, templates/) are relative to this base directory.
