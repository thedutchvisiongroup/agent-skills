---
name: using-subagents
description: Coordinates approval-gated implementation with bounded workers, evidence reports and independent reviews. Use for delegated features, refactors, fixes and multi-part work. In TDVG OpenCode, implementer owns tests/source through Red-Green-Refactor; every phase/batch requires code and post-implementation TDD review, separate advance-approved test exceptions and risk-triggered security review. Preserves discovery, plan/storage approval, evidence reuse, resumed fixes, disjoint parallel work and bounded advisory nesting. Dedicated coordinators never implement project files themselves.
---

# Using Subagents

## The Iron Law

```
IN ORCHESTRATOR MODE YOU DELEGATE, STEER, AND VERIFY. YOU NEVER WRITE CODE.
NO DISPATCH WITHOUT A WORK PLAN THE USER HAS EXPLICITLY APPROVED.
NO IMPLEMENTATION IS DONE WITHOUT INDEPENDENT REVIEW.
ONE IMPLEMENTER OWNS TESTS AND SOURCE; TDD REVIEW FOLLOWS IMPLEMENTATION.
EVERY PHASE/BATCH HAS CODE AND TEST REVIEW, UNLESS TEST REVIEW WAS EXPLICITLY EXEMPTED IN ADVANCE.
```

An orchestrator that writes code is not an orchestrator — it is an author with extra steps. And a sub-agent dispatched without a contract is not a worker — it is a guess with a budget.

**You MUST complete each phase before proceeding to the next.**

## Overview

Sub-agent orchestration means: the main agent decomposes a task, dispatches bounded pieces to fresh sub-agents, and integrates their verified results. Done well, this buys clean context, focused expertise, and safe parallelism. Done badly, it buys duplicated work, conflicting decisions, and a multiplied token bill.

**Core principles:**

1. **The orchestrator owns every decision.** Sub-agents execute bounded tasks; they NEVER make architectural choices, NEVER talk to the user directly, and NEVER see the whole plan. Actions carry implicit decisions — so every decision that matters must be explicit in the delegation contract.
2. **Fresh context is the feature.** A sub-agent's value is its clean context window. Feed it a bounded brief, NEVER the conversation history.
3. **Delegation has a real cost.** Every dispatch writes a fresh system prompt and burns tokens. The Delegation Gate (Phase 1) exists to make sure the task is worth it.
4. **Cohesive feedback:** one worker owns Red–Green–Refactor; independent specialists review completed phases/batches, not separate Red/Green stages.
5. **Reuse evidence, not verdicts:** share applicable tooling, research and checks when scope/revision/versions/environment match; reviewers still analyze independently.

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

- **Trivial edits by an implementation-capable primary** may be direct. Dedicated coordinators group them in lightweight approved implementer batches; route (a) never widens their role.
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

**(a) Direct work within your role** — advice/investigation or small work an implementation-capable primary may execute directly. Dedicated coordinators never gain project-edit authority; implementation requires (b), batching coupled work, or a user-approved switch to a direct implementation role.

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
4. **Handle gaps:** require `implementer` for execution and `code-reviewer`/`tdd-expert` for mandatory seats. Missing agents are BLOCKED, never a silent general fallback. Other harnesses need explicitly approved equivalent role-capable workers. Coordinators recommend missing agents, never create their definitions themselves.
5. **Consider model routing**: cheap/fast models for mechanical work, strong models for planning and review — record the choices in the work plan.

Read `references/subagent-discovery.md` for the matching matrix and fallback rules.

```
STOP. Is your inventory live?
- [ ] Yes, I listed the actually-available sub-agents in THIS environment
- [ ] Yes, I read their descriptions before matching
- [ ] Yes, each required execution/review seat has a real role-capable agent, no silent fallback
If any box is unchecked: GO BACK and discover.
```

### Phase 3: Work Plan (ALWAYS) — Requires Explicit User Approval

NO DISPATCH WITHOUT AN APPROVED WORK PLAN. Build the plan per `references/work-plan.md`:

1. **Goal & success criteria** (from Before You Start)
2. **Decomposition:** phases/batches with Definitions of Done, cohesive tests + source tasks, and an independence analysis
3. **Agent assignment** per task (from Phase 2), including model routing
4. **Quality loops:** code + post-implementation TDD review per phase/batch; risk-triggered security review. New-test and test-review exceptions each need explicit advance approval, reason and alternative checks; one never implies the other.
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
- **Role/verification policy:** tests + source ownership, advisory-only reviewers, confirmed gate answers, evidence identity, approved exceptions and scheduled seats
- **Output contract** — report file + a <15-line status message (`DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT`)

Steering rules (deep rules in `references/orchestrator-control.md`):

1. **Track progress in a ledger** (it survives context compaction): task → agent → status → report path.
2. **Parallel:** approved waves in one message; read-only analysis needs stable inputs/independent questions, probes no shared mutable state, writes disjoint scope. Never re-dispatch completed work.
3. **Never duplicate delegated work.** While a sub-agent runs, do other non-overlapping orchestrator work or wait — do not "also have a look yourself".
4. **Handle statuses:**
   - `DONE` → verify evidence/report and schedule mandatory reviews; execution completion is not phase acceptance
   - `DONE_WITH_CONCERNS` → read the concerns; accept them or attach them to the Phase 5 review
   - `NEEDS_CONTEXT` → answer from your own context when you can; otherwise BUNDLE the question(s) to the user in one go — NEVER relay piecemeal
   - `BLOCKED` → re-plan: more context, smaller scope, stronger model, or take it back to the user
5. **Cost awareness**: if dispatches keep failing or looping, STOP and reconsider the decomposition — do not keep spending.

### Phase 5: Quality Loops (ALWAYS after implementation)

Self-review NEVER replaces independent review.

1. **Code review — ALWAYS per phase/batch.** An independent reviewer, scope per approved plan; never suppress or pre-rate findings.
2. **TDD review — ALWAYS after implementation per phase/batch**, unless explicitly exempted in advance. Advisory B assesses assertions, requirements/edges, Red/Green proof, determinism/coverage and test-contract changes; never authors fixes.
3. **Security review when relevant:** auth/permissions, payments, PII, crypto/secrets, uploads/external input, dependencies/lockfiles or security-relevant config/IaC. Missing required specialists block acceptance; a handoff note is not a passing verdict.
4. **Fix loop:** consolidate findings, resume implementer, verify amended evidence and obtain affected re-reviews. Changes invalidating another seat require its recheck. Three unsuccessful iterations maximum, then escalate.
5. **Acceptance:** all required verdicts present and no Critical/Important or equivalent blocking High findings before dependent work. Parallel reviews need stable inputs/non-conflicting probes; no duplicated scheduled seats.

```
STOP. Is quality gated?
- [ ] Yes, every implementation got independent review
- [ ] Yes, each phase/batch got post-implementation TDD review or its explicit advance exception
- [ ] Yes, required security review is completed before acceptance
- [ ] Yes, no task exceeded 3 fix iterations without user escalation
- [ ] Yes, no open Critical/Important findings are being carried forward
If any box is unchecked: GO BACK.
```

### Phase 6: Integration & Final Verification

Sub-agent results are NOT visible to the user — you are their messenger.

1. **Conflict check** (after parallel work): verify no two sub-agents touched the same files; reconcile before continuing (see `references/parallel-execution.md`).
2. **Full verification:** obtain relevant full checks over the integrated revision, delegating execution when coordinator permissions require. Reuse identical batch-final evidence only when revision/config/environment match; report gaps/inapplicable checks and exceptions.
3. **Final whole-change review**: one reviewer over the complete change set catches what per-task reviews miss (interface drift, duplicated logic across tasks).
4. **Summarize:** implementation, code/test/security verdicts, executed/reused evidence, exceptions and report paths. A single-batch review may also be whole-change review; avoid identical duplicate seats. Close the ledger.

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
| **5. Quality** | Code + post-implementation TDD reviews, security triggers, fixes ≤ 3 | Required verdicts; explicit exceptions; no blockers |
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
