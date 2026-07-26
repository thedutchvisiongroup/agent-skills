# Harness Notes

The skill's core is harness-agnostic; this file maps its concepts to concrete mechanisms in known harnesses. **These notes drift**: harnesses change between versions. Verify against the live harness (docs, `--help`, config schema) before relying on any mechanism listed here.

## Contents

- Concept-to-mechanism map
- OpenCode
- Claude Code
- Generic fallback guidance

## Concept-to-mechanism map

| Skill concept | What to look for in your harness |
|---------------|----------------------------------|
| Dispatch | A task/agent tool that starts a sub-agent with a fresh context and returns its final message |
| Discovery | The delegation tool's agent listing; agent definition directories (user- and project-level); a CLI list command |
| Status contract | Prompt-level: you define it in the delegation prompt (harnesses rarely enforce it) |
| Report files | Plain files in the run directory — works everywhere |
| Resuming | A task/session id accepted by the delegation tool to continue an existing sub-agent session |
| Nesting limit | A depth config (e.g. `subagent_depth`) or a hard product limit |
| Question-tool control | Per-agent permission to deny interactive question tools |
| Model routing | Per-agent or per-dispatch model selection; sub-agent model environment variables |
| Parallel dispatch | Multiple delegation tool calls in one message |
| Worktree isolation | An isolation option giving the sub-agent its own working copy |

## OpenCode

- **Agents & modes**: agents are `primary`, `subagent`, or `all`. Primary agents are the ones you talk to; subagents are invoked via the Task tool or `@`-mention. `mode: all` agents can play both roles.
- **Dispatch**: the `task` tool with `subagent_type`, `prompt`, `description`. The sub-agent runs in a NEW session (fresh context) with `parentID` pointing at yours.
- **Result return**: the sub-agent's final message returns to you — it is NOT shown to the user. Summarize results yourself (Phase 6).
- **Resuming**: pass the `task_id` from a previous dispatch to continue that sub-agent session with its prior context — use this for fix loops.
- **Discovery**: agents live in markdown files (`~/.config/opencode/agents/`, project `.opencode/agents/`) and JSON config; the Task tool description lists invokable subagents; `opencode agent list` shows them. Agents with `hidden: true` don't appear in `@`-menus but remain Task-invokable.
- **Nesting**: `subagent_depth` config (introduced in OpenCode 1.18.2 — older versions reject the key at startup; check `opencode debug config`). Default 1: primary → subagent only. Depth 2 (the skill's advisory handoff) requires setting it to ≥ 2. At depth 1 a nested Task call errors — the depth-1 agent should fall back to handoff notes (see `references/nesting-policy.md`).
- **Question tool**: a sub-agent's `question` call goes to the END USER via the TUI (event `question.asked`) — bypassing you. The skill's no-interactive-questions rule therefore matters doubly here. It can be denied per agent: `"permission": { "question": "deny" }`.
- **Task permission**: `permission.task` with glob patterns controls which subagents an agent may invoke (`"*": "deny"`, `"orchestrator-*": "allow"`); denied agents vanish from the Task tool description. Last matching rule wins.
- **Model routing**: unset models inherit — primary uses the global model, subagents inherit the invoking primary's model. Set `model` per agent definition to route.
- **Todos**: the todo tool is disabled for subagents by default — don't rely on sub-agent-side todo tracking; your ledger is the tracker.
- **Background subagents**: experimental (`OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`) — out of scope for this skill's synchronous wave model.

## Claude Code

- **Agents**: defined in `.claude/agents/` (project) and `~/.claude/agents/` (user) as markdown with YAML frontmatter (`name`, `description`, `tools`, `model`, `maxTurns`, ...). The `description` drives auto-delegation.
- **Dispatch**: the `Task`/`Agent` tool; the sub-agent runs in its own context window and returns a final summary. Multiple Task calls in one message run concurrently.
- **Question tool**: `AskUserQuestion` is UNAVAILABLE to sub-agents (it requires main-thread state; background sub-agents auto-deny permission-prompting calls). Sub-agents literally cannot ask — the status contract is the only escalation channel. Do not waste prompt bytes inviting questions.
- **Nesting**: since v2.1.172 sub-agents may nest up to 5 levels. Mechanics that matter:
  - A sub-agent nests only when `Agent` is in its `tools` list; **omit `Agent` from leaf agents** so they physically cannot nest.
  - `Agent(name1, name2)` allowlists are IGNORED inside sub-agent definitions (they only bind when the agent runs as the main thread via `claude --agent`). Real restriction: `permissions.deny: ["Agent(name)"]` in `settings.json`.
  - Each nested level pays a fresh system-prompt write (+30–60%); tier models per level (`CLAUDE_CODE_SUBAGENT_MODEL` as the default for un-set agents).
  - This skill's policy (depth ≤ 2, advisory only) applies REGARDLESS of the 5-level product maximum.
- **Model routing**: `model` frontmatter field (`opus`/`sonnet`/`haiku`/`inherit`); `inherit` uses the main conversation's model — usually too expensive for leaves.
- **Isolation**: `isolation: worktree` frontmatter gives the sub-agent its own git worktree — the write fan-out escape hatch (see `references/parallel-execution.md`).
- **maxTurns**: cap turns per sub-agent (leaves ~8, mid-tier ~12) as a loop-circuit-breaker.

## Generic fallback guidance

Working in a different harness? Find these four things and the skill works:

1. **How do I dispatch a fresh-context sub-agent?** (the delegation tool)
2. **What sub-agents exist here?** (listing/directory — Phase 2)
3. **Can a sub-agent ask the user, and can I deny that?** (the question-tool policy)
4. **Is nesting possible, and what limits it?** (the depth policy)

If any answer is "unknown": assume the most restrictive case (no nesting, questions possible → forbid them in the contract) and proceed. The skill's defaults are safe under restrictive assumptions.
