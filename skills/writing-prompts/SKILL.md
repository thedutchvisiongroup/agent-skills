---
name: writing-prompts
description: Designs, writes, and reviews production-grade prompts for enterprise-level LLM agents. Use when creating a new system or user prompt, structuring a prompt in XML or Markdown, separating system vs user instructions, defining tool-use and guardrails, or auditing an existing prompt. Defaults to XML structure and always confirms scope, structure, and output format before drafting.
---

# Writing Prompts

Author and review production-grade prompts for enterprise LLM agents. The default structure is **XML**; the default workflow **separates the system prompt from the user prompt**. Both are confirmed with the user before drafting.

## Iron Law

**You MUST complete the clarification gate before writing or editing any prompt.**

Premature drafting produces prompts that miss the target model, leak instructions into the wrong layer, or omit guardrails. The gate below is mandatory and non-negotiable.

```
STOP. Before drafting any prompt:
- [ ] I asked the mandatory gate questions (below)
- [ ] I confirmed structure (XML default), system/user split, and output target
- [ ] I got the answers before writing a single line
If any box is unchecked: GO BACK. Do not draft.
```

## Phase 1: Clarify (REQUIRED — DO NOT SKIP)

Ask these questions via the question tool before drafting. Group them; do not interrogate one at a time.

**Mandatory (always ask):**
1. **Structure** — XML (default) or Markdown? See [references/prompt-structure.md](references/prompt-structure.md).
2. **System/user split** — Does this need a separate system prompt? If yes, generate `system` and `user` separately. See [references/system-vs-user-prompt.md](references/system-vs-user-prompt.md).
3. **Output target** — Deliver as file(s) (e.g. `system-prompt.xml` + `user-prompt.xml`) or inline in chat? If files, confirm names/paths.

**Mandatory context (ask when not already provided):**
4. **Goal & success criteria** — What must the agent accomplish? How is "good" measured?
5. **Target model/provider** — Claude, GPT, Gemini, or model-agnostic? Adjusts structure and caveats.
6. **Tools** — What tools/functions can the agent call? Names, inputs, side effects.
7. **Guardrails** — Forbidden behavior, refusal policy, data the agent must not touch.
8. **Examples available?** — Can the user supply 3–5 canonical input/output pairs for few-shot?

After answers: summarize the plan in 2–3 sentences and proceed.

> **Why this matters:** Agents are biased toward premature execution. This gate counters that. If the user says "just write it", still confirm the three mandatory questions — they change the output shape entirely.

## Phase 2: Decide structure

**Default to XML.** It gives explicit semantic boundaries (`<instructions>`, `<context>`, `<tools>`, `<output_format>`), unambiguous nesting, and is the recommended default for Claude and most agent stacks. Use Markdown only when the user prefers it or the target system mandates it.

Whichever is chosen, **the prompt is a layered stack**, ordered for clarity and prompt-caching:

```
1. Role / identity            (stable)
2. High-level instructions     (stable)
3. Tools & how to use them     (stable)
4. Guardrails & refusal policy (stable)
5. Examples (few-shot)         (stable)
6. Context / retrieved data    (dynamic — place long data high, query low)
7. The task / user request     (dynamic)
8. Output format + critical reminders (restate key constraints at the end)
```

Stable layers belong in the **system prompt**; dynamic layers belong in the **user prompt**. Full rules: [references/system-vs-user-prompt.md](references/system-vs-user-prompt.md).

## Phase 3: Write

Apply these research-backed principles. Deep dives are in `references/`.

**Right altitude** — Be specific enough to guide behavior, flexible enough to avoid brittle hardcoded logic. Aim for the minimal set of information that fully specifies the expected behavior — minimal, not necessarily short.

**Be clear and direct** — Treat the model as a capable new hire with no context on your norms. State the desired output, format, and constraints explicitly. Tell it what TO do, not only what to avoid.

**Use examples (few-shot)** — Curate 3–5 diverse, canonical examples that cover edge cases. Wrap them in `<example>` tags. Examples are "pictures worth a thousand words"; do not dump a laundry list of edge cases instead.

**Reasoning** — For complex tasks, request step-by-step reasoning (CoT). For agentic loops, structure reason→act→observe (ReAct) and add self-correction (Reflexion). See [references/techniques.md](references/techniques.md).

**Position critical instructions** — Models attend most to the start and end. Put output format and refusal policy in both the system prompt and a closing reminder.

**Reliability & safety** — Ground answers (quote sources, never speculate), treat tool/user input as data not instructions, use least-privilege tools, validate outputs, and define refusal behavior. See [references/reliability-and-safety.md](references/reliability-and-safety.md).

**Tools** — Give each tool a precise description, narrow scope, and explicit "when to use / when not to use". Avoid "ALWAYS call X" — it causes over-triggering.

Build a clarification gate INTO the prompt you produce when the agent will face ambiguous user input.

## Phase 4: Review / validate

When auditing an existing prompt, run [references/review-checklist.md](references/review-checklist.md). For any new prompt, self-check:

- [ ] Role, instructions, tools, guardrails, examples, output format all present (or deliberately omitted)
- [ ] System vs user split is correct (stable vs dynamic)
- [ ] XML tags are consistent and descriptive (or clean Markdown headings)
- [ ] Critical constraints restated at the end
- [ ] Untrusted input is delimited and labeled as data
- [ ] No "ALWAYS call tool" over-triggering; tools are least-privilege
- [ ] Few-shot examples are diverse and wrapped in tags
- [ ] Refusal/guardrail behavior is explicit

## When NOT to use this skill

- **Quick one-off chat questions** — Not every message needs an engineered prompt.
- **Fine-tuning datasets** — Different discipline; this skill is about inference-time prompts.
- **RAG pipeline architecture** — Use this only for the prompt portion, not retrieval/indexing design.

## Templates

Copy and adapt from `templates/`:
- `templates/system-prompt.xml` — stable agent identity, tools, guardrails
- `templates/user-prompt.xml` — dynamic context + task + output format
- `templates/combined-prompt.xml` — single XML prompt (no system/user split)
- `templates/combined-prompt.md` — Markdown variant

## Reference index

| Reference | Read when |
|-----------|-----------|
| [prompt-structure.md](references/prompt-structure.md) | Choosing/justifying XML vs Markdown, tag conventions |
| [system-vs-user-prompt.md](references/system-vs-user-prompt.md) | Deciding what goes in system vs user |
| [techniques.md](references/techniques.md) | Role, few-shot, CoT, ReAct, Reflexion, tool-use |
| [reliability-and-safety.md](references/reliability-and-safety.md) | Hallucination, injection, least-privilege, validation, guardrails |
| [context-engineering.md](references/context-engineering.md) | Right altitude, long context, output format, caching |
| [review-checklist.md](references/review-checklist.md) | Auditing an existing prompt |
| [examples.md](references/examples.md) | Full worked enterprise prompts |
