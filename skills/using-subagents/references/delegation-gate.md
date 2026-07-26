# The Delegation Gate

The gate is Phase 1 of every run of this skill. It produces one deliberate decision: route (a), (b), or (c). The criteria below are **heuristics, not hard thresholds** — apply them with judgement, and state your reasons when you choose.

## Contents

- The three routes
- Route (a): do it yourself
- Route (b): one sub-agent
- Route (c): orchestrator mode
- The cost check
- Effort scaling
- Worked examples
- Anti-examples

## The three routes

| Route | Shape | Your role | Skill ends? |
|-------|-------|-----------|-------------|
| (a) Do it yourself | Direct execution in the main context | Author | Yes — immediately |
| (b) One sub-agent | A single bounded dispatch | Orchestrator of one | No — Phases 2–6 in lightweight form |
| (c) Orchestrator mode | Decomposition + multiple dispatches | Strict orchestrator | No — full flow |

Routes (b) and (c) share the Iron Law: once you delegate a scope, you NEVER write code inside it.

## Route (a) signals — do it yourself

Choose direct execution when ANY of these hold:

- **Trivially small**: a handful of lines, one file, one or two tool calls.
- **Tightly coupled to the conversation**: the "task" is really the next sentence of an ongoing discussion; a sub-agent would need the whole chat to understand it.
- **High-stakes judgement**: architecture decisions, ambiguous requirements, anything where you would need to ask the user mid-way. Delegation freezes judgement into a prompt — keep it warm.
- **Sequential dependency**: the output frames the very next step and you need it immediately.
- **Approval-gated edits**: changes the user wants to watch and steer interactively.
- **Learning mode**: the user wants to see and understand the change as it is made.

## Route (b) signals — one sub-agent

Choose a single dispatch when ALL of these hold:

- **One bounded task** with a clear definition of done — no decomposition needed.
- **Fresh context is the win**: verbose exploration, log analysis, reading many large files, a self-contained implementation. Its intermediate output would flood your context.
- **Well-specified**: you can write acceptance criteria without guessing.

Typical route-(b) work: "map how feature X works", "implement this isolated utility with tests", "review this diff".

## Route (c) signals — orchestrator mode

Choose full orchestration when ALL of these hold:

- **Decomposable**: two or more clearly bounded sub-tasks.
- **Independence available**: provably disjoint scopes (parallel potential, see `references/parallel-execution.md`), OR a long sequential chain you would rather steer than execute.
- **Exceeds comfortable single-context execution**: doing it all yourself would degrade quality late in the session.
- **Worth the overhead** — see the cost check.

## The cost check

Delegation multiplies token spend. Research systems report ~4× for single agents and up to ~15× for multi-agent runs versus plain chat; every dispatch writes a fresh system prompt and re-pays context.

Delegation pays when at least one of these is true:

1. **Context preservation** — the work's intermediate output would degrade your own reasoning in a long session.
2. **Specialization** — a dedicated agent (reviewer, security specialist) does this class of work measurably better.
3. **Wall-clock parallelism** — independent sub-tasks genuinely finish sooner concurrently (see `references/parallel-execution.md` — genuine means disjoint).

If none is true: route (a).

## Effort scaling

Scale the number of agents to the task — over-delegation is the most common orchestration failure:

| Task size | Shape | Agents |
|-----------|-------|--------|
| Simple, fact-sized | One lookup, one edit | 0 (route a) — or 1 sub-agent |
| Moderate, comparison-sized | A few bounded parts | 1–3 sub-agents |
| Complex, multi-part | Many independent parts | 4+ sub-agents with clearly divided responsibilities |

Never spawn an army for a simple query. Each additional agent must earn its system prompt.

## Worked examples

1. **"Fix the typo in the footer and update the year"** → route (a). Two edits, one file, zero ambiguity.
2. **"Find out why the payment webhook intermittently returns 500"** → route (b): one explorer over logs and code paths; verbose intermediate output stays out of your context. (Route (a) if you already suspect the exact spot.)
3. **"Add OAuth login (Google + GitHub) with tests"** → route (c): decomposes into config, provider adapters, UI, tests; review mandatory; the two providers are disjoint and parallel-safe.
4. **"These 4 test files fail for different reasons"** → route (c) with parallel implementers: independent root causes, disjoint files — the textbook parallel case.

## Anti-examples

- **"Refactor the state management"** with no further spec → first clarify with the user (route a-with-dialogue). Ambiguous, high-stakes work is not dispatchable until it is specified.
- **"Change the primary-key strategy across every model"** → tightly coupled; route (a) or one sub-agent at most. Parallel agents would produce conflicting migrations.
- **"Read file X and tell me the function name on line 40"** → never dispatch what two of your own tool calls answer. The leaf is too small.
