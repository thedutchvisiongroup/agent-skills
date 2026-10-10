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
- **Native explore reports:** its default permission profile is edit-denied. The mandatory report template requires a worker with explicit report-writing authority; otherwise use coordinator read-only investigation, not an unsupported explore dispatch or shell-write bypass. This does not broaden native explorer permissions.
- **TDVG policy:** managed config disables `general`; discovered `implementer` owns tests/source and fixes, denies task/question/todo and inherits the model. Code/TDD reviews follow per phase/batch; missing required seats block acceptance.
- **Prompt composition (1.18.34):** custom body replaces provider base prompt; environment/project/skill layers remain. Worker scope/tool/evidence/escalation rules must be in its prompt.
- **Background subagents**: experimental (`OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`) — out of scope for this skill's synchronous wave model.

## Claude Code

- **Agents**: markdown files with YAML frontmatter in `~/.claude/agents/` (user) and `.claude/agents/` (project; nearest wins). Plugin and managed agents also exist. Fields: `name`, `description` (drives auto-delegation), `tools` / `disallowedTools`, `model` (`sonnet`, `opus`, `haiku`, a full model id, or `inherit`), `effort`, `maxTurns`, `skills` (preloads the FULL skill content at startup), `hooks`, `permissionMode`, `isolation: worktree`, `memory`, `color`. There is no `temperature` field and no per-path edit permission.
- **No primary agents**: the main conversation is the coordinator. A session can run AS an agent via `claude --agent <name>` or the `agent` setting; its prompt then replaces the default system prompt, and `tools: Agent(a, b)` restricts which agent types it may spawn.
- **Dispatch**: the `Agent` tool with `subagent_type` and `prompt`. The sub-agent gets a fresh context: its own system prompt, the delegation message, CLAUDE.md, git status and preloaded skills; no conversation history. Its final message returns to you. Multiple `Agent` calls in one message run concurrently, and calls can run in the background.
- **Resuming**: `SendMessage` to the agent id or name continues it with its full history; use it for fix loops. Explore and Plan are one-shot and cannot be resumed.
- **Discovery**: the `Agent` tool description lists the available agent types; `/agents` manages them; definitions live in the directories above.
- **Question tool**: `AskUserQuestion` is removed from every sub-agent. The status contract is the only escalation channel, so do not invite questions in the prompt.
- **Nesting**: allowed by default up to 3 levels below main. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` sets the limit (`1` = off). Block nesting per agent by omitting `Agent` from `tools` or setting `disallowedTools: Agent`. Disable an agent type with `permissions.deny: ["Agent(name)"]`. The skill's depth policy (depth ≤ 2, advisory only) still applies.
- **Model routing**: precedence is the per-invocation `model` parameter, then frontmatter `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main model.
- **Path-scoped write limits**: use a `PreToolUse` hook in the agent's frontmatter. TDVG ships `~/.claude/hooks/tdvg-write-guard.py` with profiles `reviewer` and `tdd-expert`. Shell writes remain a prompt-level rule.
- **Isolation**: `isolation: worktree` gives the sub-agent its own git worktree — the write fan-out escape hatch (see `references/parallel-execution.md`).
- **maxTurns**: cap turns per sub-agent (leaves ~8, mid-tier ~12) as a loop-circuit-breaker.
- **TDVG policy**: `general-purpose` and `claude` built-ins are denied via TDVG settings. `implementer` (inherit model, no Agent tool) owns tests and source. `code-reviewer`, `security-reviewer` and `tdd-expert` run on sonnet. The coordinator role lives in the main conversation.

## Generic fallback guidance

Working in a different harness? Find these four things and the skill works:

1. **How do I dispatch a fresh-context sub-agent?** (the delegation tool)
2. **What sub-agents exist here?** (listing/directory — Phase 2)
3. **Can a sub-agent ask the user, and can I deny that?** (the question-tool policy)
4. **Is nesting possible, and what limits it?** (the depth policy)

If any answer is "unknown": assume the most restrictive case (no nesting, questions possible → forbid them in the contract) and proceed. The skill's defaults are safe under restrictive assumptions.
