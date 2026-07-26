# Sub-agent Discovery

Phase 2 of the skill. The rule: **NEVER dispatch to an assumed agent.** Agents differ between harnesses, projects, and machines. Inventory first, match second, dispatch third.

## Contents

- Live inventory
- Reading descriptions
- Capability matching
- Gap handling and fallbacks
- Model routing
- What you never do

## Live inventory

Inventory the agents that ACTUALLY exist in the current environment, using the harness's live mechanism — never your memory of another project:

- **Task/delegation tool listing** — most harnesses inject the available sub-agents (with descriptions) into the delegation tool's description. Read it.
- **Agent directories** — agent definition files on disk (user-level and project-level). See `references/harness-notes.md` for the conventional locations per harness.
- **CLI listing** — some harnesses offer a list command (e.g. `opencode agent list`).

Record the inventory in the work plan: which agents exist, which you selected, which you deliberately did NOT select.

## Reading descriptions

An agent's description is its capability contract. Extract from each:

1. **What it does** — the verb: implements, reviews, explores, debugs, plans.
2. **When to use it** — its trigger conditions; match them to your task.
3. **Its constraints** — permissions (e.g. edit-denied reviewers), mode (subagent-only?), anything its prompt forbids.
4. **Its collaboration rules** — some agents hand off to other agents; that interacts with `references/nesting-policy.md`.

Descriptions are one-sided advertisements: an agent claiming "does everything" is a generalist. Prefer narrow descriptions — they signal a specialist.

## Capability matching

Match each planned task to exactly one agent (or template fallback):

| Task type | Prefer | Avoid |
|-----------|--------|-------|
| Implementation | A build/implementer agent, else `templates/implementer.md` on a general-purpose agent | Review agents (edit-denied) |
| Independent review | A dedicated review agent (code-reviewer, security-reviewer) | The implementer itself; generic agents without a review method |
| Read-only exploration | An explore/scout agent, else `templates/explorer.md` | Anything with write permissions it doesn't need |
| Specialist review (security, perf) | The matching specialist agent — and only when the plan calls for it | General reviewers guessing outside their discipline |

One agent per task. Two agents on the same task at the same time = duplicated cost and possible conflict.

## Gap handling and fallbacks

When no existing agent fits a task:

1. **Fallback to a template**: dispatch a general-purpose sub-agent with the matching template from `templates/` — the template supplies the contract the agent definition would have.
2. **Recommend, never create**: if the missing specialist would have recurring value (e.g. a tdd-expert), RECOMMEND the user create it after the run. In orchestrator mode you NEVER write agent definitions yourself — that is writing config, and config is code.
3. **Re-scope the task**: sometimes the gap means the task is shaped wrong — a "security review" task with no security specialist becomes a code review plus an explicit security handoff note.

## Model routing

When the harness lets you choose a model per dispatch (see `references/harness-notes.md`):

- **Strong models** for planning, review, debugging, anything with judgement.
- **Cheap/fast models** for mechanical, well-specified work (formatting passes, simple explorers, log summarizing).
- **Never default everything to the strongest model** — cost compounds per dispatch; the leaf rarely needs the crown.
- Record routing choices in the work plan so the user sees the cost/quality trade-off they approved.

## What you never do

- Never dispatch to an agent you haven't verified exists HERE.
- Never rely on an agent list from a different project, machine, or session.
- Never dispatch two specialists to second-guess each other on the same input without the plan saying so (that is a tournament — it belongs in the approved plan, not in improvisation).
- Never create, edit, or "improve" agent definitions in orchestrator mode.
