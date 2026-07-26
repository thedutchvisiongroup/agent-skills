# Failure Modes

The anti-pattern catalog: what goes wrong in sub-agent orchestration, how to recognize it, and how this skill prevents it. Skim it in every phase; consult it whenever something feels off.

## Contents

- Delegation failures
- Parallelism failures
- Context failures
- Quality-loop failures
- Control failures
- Cost failures

## Delegation failures

**Over-delegation.** Spawning agents for trivial work — the most common orchestration failure.
*Symptoms:* agents dispatched for two-line tasks; a plan with 9 tasks for a small feature.
*Prevention:* the Delegation Gate (Phase 1) and effort scaling (`references/delegation-gate.md`).

**Under-delegation.** Doing everything yourself in a marathon session until quality degrades.
*Symptoms:* your context is full of file dumps and test logs; late-session reasoning gets sloppy.
*Prevention:* route (b) exists for exactly this — offload the verbose middle.

**Vague delegation.** "Research X", "improve Y" as dispatch prompts.
*Symptoms:* two agents do the same work; a third area untouched; "close enough" results.
*Prevention:* the delegation contract (`references/subagent-prompts.md`) — bounded objective + acceptance criteria, every time.

**Whole-plan leakage.** Pasting the entire plan into every dispatch.
*Symptoms:* sub-agents anchor on other tasks, make decisions that belong to you, duplicate each other's scope.
*Prevention:* per-task briefs only (`references/context-engineering.md`).

## Parallelism failures

**Conflicting parallel decisions.** Two agents make the same judgement call differently (the Flappy Bird failure: valid parts, invalid whole).
*Prevention:* decisions are made IN THE PLAN; parallel agents only execute them (`references/task-decomposition.md` — decision coupling).

**Hidden coupling.** "Disjoint" tasks that shared a file, a convention, or a dependency.
*Symptoms:* merge conflicts, interface mismatch, per-task green / whole red.
*Prevention:* the disjointness test (`references/parallel-execution.md`) — "probably disjoint" is not disjoint.

**Over-parallelizing.** Fan-out of 10 for a simple feature.
*Prevention:* cap 3–5; waves, not streams.

## Context failures

**The telephone game.** Findings relayed orchestrator→agent→agent, degrading at each hop.
*Prevention:* file handoffs, never re-tellings (`references/context-engineering.md`).

**Output dumps.** Sub-agents returning 200-line file contents into your context.
*Prevention:* the status contract — <15 lines + report file.

**Cold-start assumptions.** Expecting the sub-agent to "know the conventions".
*Symptoms:* code that works but fits nothing; reinventions of existing utilities.
*Prevention:* scene-setting layer in every contract. Unwritten context is unshared context.

## Quality-loop failures

**Self-review acceptance.** Marking work done on the implementer's own say-so.
*Prevention:* independent review is mandatory (Phase 5). No exceptions for "small" work.

**Reviewer neutering.** Telling reviewers what not to flag, or pre-rating their findings.
*Prevention:* forbidden by rule (`references/quality-loops.md`).

**Infinite fix loops.** Iteration 5, 6, 7 on the same task.
*Prevention:* max 3, then escalate — the plan is wrong, not the code.

**Security guessing.** A general reviewer "checking security real quick".
*Prevention:* the conditional trigger + specialist-or-handoff rule (`references/quality-loops.md`).

## Control failures

**Question-tool stalls.** Sub-agents using interactive ask-the-user tools: the question bypasses you (some harnesses), is auto-denied (others — documented to cause token-burning loops), or interrupts the user from three branches at once.
*Prevention:* the no-interactive-questions rule; escalation via status contract (`references/subagent-prompts.md`).

**Runaway nesting.** Sub-agents spawning sub-agents spawning sub-agents.
*Symptoms:* bills multiplying without visible cause; work you never approved appearing in transcripts.
*Prevention:* depth ≤ 2, advisory handoffs only, plan approval required (`references/nesting-policy.md`).

**Ghost work.** Re-dispatching a completed task after context compaction.
*Prevention:* the ledger (`references/orchestrator-control.md`) — never re-dispatch what the ledger marks complete.

**Duplicated effort.** You "also take a look" while the sub-agent runs.
*Prevention:* delegated means delegated (`references/orchestrator-control.md`).

## Cost failures

**Token blowup.** Multi-agent runs can cost an order of magnitude more than direct work.
*Symptoms:* long sessions with many dispatches and little to show.
*Prevention:* the gate's cost check, model routing, resuming over fresh dispatches, abort criteria that actually fire (`references/orchestrator-control.md`).

**Opus-everywhere.** Strongest model for every leaf.
*Prevention:* model routing (`references/subagent-discovery.md`) — the leaf rarely needs the crown.
