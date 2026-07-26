# Task Decomposition

How to split work into sub-agent-sized pieces. Read in Phase 3, together with `references/parallel-execution.md`. The goal: tasks that are **independent enough to isolate** and **big enough to be worth a system prompt**.

## Contents

- The core trade-off
- The four couplings
- The independence checklist
- Cohesion: keep coupled work together
- Granularity: not too small, not too big
- Dependency chains
- Effort scaling recap
- Worked example
- Anti-patterns

## The core trade-off

Every cross-agent boundary costs context transfer: the second agent cannot see what the first one saw, so everything that matters must be written down and handed over. This is the **communication-to-computation trade-off**:

- Finer splits → more parallelism, but more handoff cost and more room for interface mismatch.
- Coarser splits → less handoff cost, but less parallelism and bigger single contexts.

Empirically (repository-level coding research): naive per-file parallelism can be BOTH slower AND worse than sequential work, while dependency-aware partitioning beats both. Split along dependency lines, never along arbitrary lines.

## The four couplings

Two tasks are coupled when they share any of these:

1. **File coupling** — they touch the same files. → Same agent, or strict sequencing.
2. **Domain coupling** — they touch the same conceptual area (e.g. both change pricing logic), even in different files. → Same agent preferred.
3. **State coupling** — one task's output is the other's input (migrations, generated code, shared interfaces). → Sequential, with a file handoff.
4. **Decision coupling** — both need the same judgement call (naming scheme, API shape). → Decide FIRST in the plan; never let two agents make the same decision independently (they will make it differently).

## The independence checklist

A task pair is parallel-safe ONLY when you can answer yes to all:

- [ ] Provably disjoint file scopes (or isolated worktrees)
- [ ] No shared mutable state (database, env, running services)
- [ ] Neither needs the other's output to start or to finish
- [ ] No shared pending decision
- [ ] Integration afterwards is mechanical (no merge judgement needed)

Any "no" → sequential, or re-split along cleaner lines. When in doubt: sequential. Parallelism is an optimization; correctness is the requirement.

## Cohesion: keep coupled work together

Strongly coupled files belong to the SAME agent. Group by cohesion:

- A feature and its tests: one agent.
- An interface and all its implementations: one agent.
- A migration and the model changes requiring it: one agent.

Watch for **hub files** (project-wide utilities, base classes, top-level entry points): everything depends on them. Put hub-file changes in their own task, scheduled BEFORE the tasks that depend on them.

## Granularity: not too small, not too big

**Too small** — the leaf's output would be under ~500 tokens, or the orchestrator could produce it with two tool calls. Don't dispatch; fold it into a sibling task or do it directly (that may be route a).

**Too big** — the task needs multiple judgement calls, spans coupled domains, or its brief can't fit on one page. Split it; an over-big task recreates the original problem inside one sub-agent.

**Sweet spot** — one bounded outcome, specifiable on one page, verifiable with objective acceptance criteria, producing a compressed report.

## Dependency chains

Chain-shaped work (B needs A's output) is sequential — either one sub-agent doing both, or sequential dispatches with a file handoff (A writes interface/results to a file; B reads it). Never parallelize a chain and hope the timing works out.

Mixed shapes are normal: three independent feature tasks (parallel) that all follow one shared-setup task (sequential first). Draw the dependency graph in the work plan — boxes and arrows, not vibes.

## Effort scaling recap

| Task size | Agents |
|-----------|--------|
| Simple, fact-sized | 0–1 |
| Moderate, comparison-sized | 1–3 |
| Complex, multi-part | 4+ with clearly divided responsibilities |

Over-delegation is the most common failure. Every agent must earn its system prompt.

## Worked example

"Add OAuth login (Google + GitHub) with tests":

- **Task 0 (sequential first):** shared auth config + provider interface. Hub work — everything depends on it.
- **Task 1:** Google provider adapter + tests. Files: `providers/google/*`. Parallel-safe with Task 2.
- **Task 2:** GitHub provider adapter + tests. Files: `providers/github/*`. Parallel-safe with Task 1.
- **Task 3 (sequential last):** login UI wiring — depends on both adapters' real interfaces.
- Reviews per task; final whole-change review in Phase 6.

Note the shape: hub first, disjoint leaves parallel, integration last. That shape is the default for feature work.

## Anti-patterns

- **Per-file splitting** — "agent per file" ignores coupling; produces interface mismatch.
- **Splitting a judgement call** — two agents deciding the same convention differently (the Flappy Bird failure: valid parts, invalid whole).
- **Micro-leaves** — dispatching one-function tasks; pure overhead.
- **Mega-tasks** — "implement the whole feature" as one dispatch; the sub-agent drowns and the orchestrator learns nothing until the end.
