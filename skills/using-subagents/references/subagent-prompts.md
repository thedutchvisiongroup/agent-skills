# Sub-agent Prompts: The Delegation Contract

Phase 4 of the skill. A sub-agent starts with a **fresh context** — everything it knows about your task comes from your dispatch prompt. The quality of that prompt IS the quality of the delegation. This is the anatomy of a good one.

## Contents

- The delegation contract
- The status contract (mandatory)
- The no-interactive-questions rule
- Using the templates
- Resuming sub-agents for fix loops
- Prompt quality failure modes

## The delegation contract

Every dispatch prompt contains ALL of these layers (the templates in `templates/` implement them):

| Layer | Content | Why it's non-optional |
|-------|---------|----------------------|
| **Role** | What kind of sub-agent this is (implementer / reviewer / explorer) | Frames every decision it makes |
| **Objective** | ONE bounded task, one sentence | Vague objectives → duplicated work and gaps |
| **Brief / acceptance criteria** | The full requirements, or a path to a brief file + measurable acceptance criteria | "Close enough" is the default failure without them |
| **Context** | Scene-setting for THIS task: where it fits, dependencies, interfaces, conventions | The sub-agent starts cold; unwritten context is unshared context |
| **Boundaries** | What NOT to touch; no sub-agent dispatching; no interactive question tools; scope discipline | Actions carry implicit decisions — forbid the wrong ones explicitly |
| **Escalation rules** | When and how to report BLOCKED / NEEDS_CONTEXT | Bad work is worse than no work; make stopping safe |
| **Output contract** | Report file + <15-line status message | Keeps YOUR context clean and the evidence on disk |

Skip a layer and the sub-agent fills the hole with a guess. Guesses are where multi-agent systems go to die.

## The status contract (mandatory)

Every sub-agent returns a status message of **under 15 lines** plus a report file:

- **`DONE`** — work complete, acceptance criteria met, report written.
- **`DONE_WITH_CONCERNS`** — complete, but with doubts the orchestrator must read.
- **`BLOCKED`** — cannot complete; the message itself contains what is stuck, what was tried, what is needed.
- **`NEEDS_CONTEXT`** — information missing that only the orchestrator/user has; questions listed in the message.

The **report file** (structure: `templates/report.md`) carries the detail: work performed, files changed, test evidence (commands + real output), self-review findings, concerns, handoff notes. The status message carries the pointer.

Why a file: sub-agent output that flows only through the orchestrator's context degrades (the "game of telephone") and bloats it. Files preserve evidence exactly; summaries transport it. See `references/context-engineering.md`.

## The no-interactive-questions rule

Sub-agents NEVER use interactive ask-the-user tools. This is a hard line, for three reasons:

1. **Harness divergence** — in some harnesses a sub-agent's question goes straight to the end user (bypassing you, the orchestrator); in others the tool is unavailable or auto-denied to sub-agents (documented failure mode: agents looping on denied question calls, burning tokens, producing nothing). See `references/harness-notes.md`.
2. **Parallel safety** — a mid-run question blocks one branch while others run, or worse: three sub-agents interrupt the user simultaneously.
3. **Single point of contact** — the user approved ONE plan with ONE orchestrator. Questions are bundled BY you, not sprayed AT them.

Questions travel the status contract instead: `NEEDS_CONTEXT` (missing info) or `BLOCKED` (stuck). You answer from your own context when you can; otherwise you bundle questions to the user in one go. Front-load clarity: a good brief and the plan-approval gate make mid-run questions rare.

## Using the templates

| Template | Dispatch when |
|----------|---------------|
| `templates/implementer.md` | The sub-agent will write/modify code |
| `templates/reviewer.md` | The sub-agent reviews (advisory-only) — use the relevant parts when dispatching a dedicated review agent |
| `templates/explorer.md` | Read-only investigation |
| `templates/report.md` | Given to every sub-agent as the report structure |

Fill every `[PLACEHOLDER]`. Delete guidance blocks. Never send a template with placeholders left — a sub-agent that reads "[SCOPE]" reads it as permission to define its own scope.

When dispatching a **dedicated discovered agent** (e.g. a code-reviewer agent), you don't paste the whole template — its own system prompt already carries its method. You DO still supply: the objective, the scope (diff/report file paths), the acceptance criteria, and the output contract.

## Resuming sub-agents for fix loops

Some harnesses let you resume the same sub-agent session (e.g. via a task/session id — see `references/harness-notes.md`). Prefer resuming the IMPLEMENTER with the review findings: it already holds the task context, making fixes cheaper and more consistent than a cold fix agent. The fix report is appended to the same report file. Count every fix round toward the 3-iteration limit (see `references/quality-loops.md`).

## Prompt quality failure modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Vague objective | Two agents do the same work; a third area untouched | One bounded task per dispatch; check coverage in the plan |
| Missing scene-setting | Sub-agent reinvents conventions, clashes with the codebase | Context layer: where it fits, dependencies, patterns to follow |
| No boundaries | "While I'm here" refactors outside scope | Explicit NOT-list + scope discipline in the contract |
| Whole-plan paste | Sub-agent anchors on other tasks, pollutes decisions | Per-task brief only — never the whole plan |
| Output dump | 200-line file contents returned into your context | Output contract: report file + <15-line status |
| Silent uncertainty | Plausible-sounding wrong work reported as DONE | Escalation layer making DONE_WITH_CONCERNS/BLOCKED safe and expected |
