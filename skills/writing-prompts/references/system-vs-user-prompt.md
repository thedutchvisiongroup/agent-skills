# System vs User Prompt

The split is the difference between **how/why the agent behaves** (system) and **what to do right now** (user).

## What goes in the SYSTEM prompt (stable)

Sent once, reused for the whole session. Put everything that does not change per request:

- **Role / identity** — "You are an enterprise contract-analysis agent."
- **High-level instructions & operating principles** — goals, priorities, tone.
- **Tool definitions & usage policy** — when to use each tool, when not to.
- **Guardrails & refusal policy** — forbidden actions, data boundaries, how to handle conflicting instructions.
- **Output contract** — required format, schema, length norms.
- **Canonical few-shot examples** — diverse, representative behavior.

System instructions are intended to **take precedence** over conflicting user-message instructions. This is what makes a persona and its guardrails controllable and injection-resistant.

## What goes in the USER prompt (dynamic)

Changes every turn. Put what is specific to this request:

- **The task / question** — the actual thing to do now.
- **Per-request context / retrieved data** — documents, records, RAG results.
- **Request-specific parameters** — this customer's id, this date range.
- **A closing restatement** of the most critical output constraint.

## Layout rules

- **Long data high, query low.** Place large documents near the top of the user prompt and the actual question at the end. Queries at the end can improve quality on long, multi-document inputs.
- **Restate critical constraints at both ends.** Output format and refusal policy belong in the system prompt AND a closing reminder in the user prompt — models attend most to start and end.
- **Stable-prefix first for caching.** Keep the stable layers (system, tools, examples) constant so providers can cache them; vary only the dynamic tail.

## Provider notes (model-agnostic + Claude accent)

- **Claude** — strong adherence to system role; XML structure recommended; system prompt sets behavior, user message carries the task. Claude weights user messages heavily, so keep the user prompt clean and unambiguous.
- **GPT / Gemini** — same three-role model (`system`, `user`, `assistant`). Behavior is broadly similar; differences are minor compared to getting the split right.

## When a separate system prompt is NOT needed

- Single-shot tasks with no reusable behavior (a one-off transformation).
- Platforms that expose only one prompt field.

In those cases, produce one combined prompt but keep the same internal ordering (role → instructions → tools → guardrails → examples → context → task → output format).

## Gate behavior

Always ask whether a separate system prompt is required. If yes, deliver `system` and `user` as distinct outputs and state explicitly what was placed where and why.
