# Context Engineering

Prompt engineering is one part of context engineering: curating the full set of information the agent sees. Keep context **informative yet tight**.

## Right altitude

The Goldilocks zone between two failure modes:

- **Too low (brittle):** hardcoding complex, exact logic to force precise behavior. Fragile, high-maintenance.
- **Too high (vague):** high-level hand-waving that assumes shared context the model doesn't have.
- **Right altitude:** specific enough to guide behavior, flexible enough to give the model strong heuristics.

Aim for the **minimal set of information that fully specifies the expected behavior**. Minimal does not mean short — give enough up front to ensure adherence, then trim. Start with a minimal prompt on the best available model, observe failure modes, and add targeted instructions/examples to fix them.

## Long-context placement

- Put long documents and data **near the top** of the (user) prompt, above the query, instructions, and examples.
- Put the **actual question at the end**. On complex multi-document inputs this can improve quality meaningfully.
- Wrap each document with metadata: `<document index="1"><source>…</source><document_content>…</document_content></document>`.
- For long-document tasks, ask the model to extract relevant quotes first, then answer.

## Position effects

Models attend most to the **start and end** of the prompt; the middle gets less attention. Therefore:

- Lead with role + core instructions.
- Close with the output contract and the single most important constraint, restated.

## Output format control

- Tell the model what to do, not only what not to do ("write flowing prose paragraphs" beats "don't use markdown").
- Use a named tag for the answer (`<answer>…</answer>`) to make parsing reliable.
- Anchor structured output with a literal example of the exact shape.
- Match prompt style to desired output style — formatting leaks from prompt to response.

## Prompt-caching layout

Order layers stable → dynamic so providers can cache the stable prefix:

```
[stable]  role, instructions, tools, guardrails, examples
[dynamic] retrieved context, the task, request params
```

Keep the stable prefix byte-stable across requests (no per-request timestamps inside it) to maximize cache hits and reduce latency/cost.

## Sub-agents & context hygiene

For complex workflows, split work across specialized sub-agents (e.g. one for retrieval, one for drafting) instead of one mega-prompt. This keeps each context clean and improves accuracy. Don't put large manuals inline — store them and instruct the agent to retrieve on demand.
