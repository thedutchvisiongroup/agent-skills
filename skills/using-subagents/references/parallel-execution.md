# Parallel Execution

Read in Phases 3, 4 and 6. Parallelism is the most over-used and least verified optimization in multi-agent work. The rule of this skill: **read-only work is always parallel-safe; writing is parallel-safe ONLY for provably disjoint scopes.**

## Contents

- The two kinds of parallel work
- The disjointness test
- Fan-out discipline
- Dispatch mechanics
- Integration verification (mandatory)
- Failure modes

## The two kinds of parallel work

**Read-only fan-out (always safe).** Explorers, researchers, analyzers: they change nothing, so they cannot conflict. Run them concurrently whenever the questions are independent. This is where most of the real speed lives — breadth-first investigation compressed into small answers.

**Write fan-out (conditionally safe).** Two implementers writing concurrently is safe ONLY when the disjointness test passes in full. When it doesn't, parallel writing doesn't just risk conflicts — it manufactures them: conflicting implicit decisions, colliding edits, duplicated logic.

## The disjointness test

All five must be yes (mirrors the independence checklist in `references/task-decomposition.md`):

- [ ] Provably disjoint file scopes — different files, or isolated worktrees/branches per agent
- [ ] No shared mutable state — database, environment, running services, generated artifacts
- [ ] No output dependency — neither needs the other's result to start or finish
- [ ] No shared pending decision — all conventions/judgement calls settled in the plan beforehand
- [ ] Mechanical integration — combining results needs no judgement, only verification

Any "no" → sequential. "Probably disjoint" is not disjoint. When two tasks share even one file, they are sequential — or one task.

**Worktree escape hatch:** when the harness supports isolated working copies (e.g. git worktrees), write fan-out can tolerate overlapping INTENT — each agent works on its own copy and integration becomes an explicit, reviewed merge. Record this choice in the plan; isolation moves the risk to the merge, it doesn't delete it.

## Fan-out discipline

- **Cap the fan-out**: 3–5 concurrent sub-agents is the practical band for coding work. Beyond that, coordination cost eats the speed.
- **One message, one wave**: dispatch a parallel wave in a single message (multiple tool calls at once); then WAIT for the wave. Don't drip-feed parallel dispatches — you lose the ability to reason about what's in flight.
- **Waves, not streams**: structure parallel work in waves separated by verification (wave 1: explorers → verify findings; wave 2: implementers → verify; wave 3: reviewers). Each wave's results feed the next wave's contracts.

## Dispatch mechanics

Per wave, per sub-agent: a full delegation contract (see `references/subagent-prompts.md`) with one addition — the boundary section names the disjoint scope explicitly: *"You may touch ONLY: `providers/google/**`. Other agents are concurrently working in `providers/github/**`; their files are out of scope."*

Ledger each dispatch before moving on (task → agent → status → report path). If you can't write down what's in flight, you have too much in flight.

## Integration verification (mandatory)

After ANY parallel wave, before the next phase:

1. **Read every summary** — status + concerns, not just DONE-checkmarks.
2. **Conflict check** — verify no two agents touched the same files. If they did: STOP, reconcile now (this is orchestrator judgement — or user escalation), and re-verify.
3. **Run the full test suite** — per-task greens can hide cross-task breakage. The suite over the INTEGRATED result is the verdict.
4. **Spot check** — read a sample of actual diffs. Systematic errors (wrong convention applied consistently by all agents) only show up when you look.

Skipping integration verification turns Phase 6 into archaeology.

## Failure modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Over-parallelizing | Ten agents for a simple feature; token bill explodes | Group micro-tasks; cap fan-out; check the gate's effort scaling |
| Under-parallelizing | Four independent analyses run sequentially | Look for domain independence at plan time |
| Hidden coupling | Two agents "finished" but the merge is broken | The disjointness test failed upstream — re-split and re-run one of them |
| Conflicting decisions | Same convention, two versions (the Flappy Bird failure) | Decide conventions IN THE PLAN; never let parallel agents decide |
| No integration pass | Per-task green, whole-change red | Mandatory integration verification — every wave, every time |
| Drip-feed dispatching | Losing track of what's in flight | One message per wave; ledger everything |
