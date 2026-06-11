# Prompt Review Checklist

Use when auditing or refactoring an existing prompt. Score each item; fix red flags before shipping.

## 1. Structure

- [ ] Clear sections with consistent XML tags (or clean Markdown headings)
- [ ] Instructions, context, examples, and variable input are visually/semantically separated
- [ ] Untrusted input is fenced and explicitly labeled as data

## 2. System / user split

- [ ] Stable behavior (role, tools, guardrails, examples) is in the system prompt
- [ ] Dynamic content (task, context, params) is in the user prompt
- [ ] No leakage of per-request data into the stable prefix (caching-friendly)

## 3. Clarity & altitude

- [ ] Role is concrete and task-relevant
- [ ] Instructions are specific, action-oriented, and at the right altitude (not brittle, not vague)
- [ ] Tells the model what TO do, not only what to avoid
- [ ] Minimal but complete — no filler that doesn't change behavior

## 4. Techniques

- [ ] Few-shot examples are present where output shape matters (3–5, diverse, tagged)
- [ ] Reasoning approach fits the task (CoT for multi-step, ReAct for tools)
- [ ] Output format is explicit and, if structured, anchored by a literal example

## 5. Tools

- [ ] Each tool has a precise description and when-to-use / when-not-to-use
- [ ] Tools are least-privilege (no over-broad capabilities)
- [ ] No "ALWAYS call tool X" over-triggering
- [ ] Failure handling for tools is specified

## 6. Reliability & safety

- [ ] Grounding / anti-hallucination instruction present ("don't speculate", quote sources, or RAG-only)
- [ ] Uncertainty is permitted ("say I don't know")
- [ ] Refusal-on-conflict / injection defense present
- [ ] High-stakes actions gated by a non-LLM check
- [ ] Output validated against a contract with a fallback

## 7. Positioning

- [ ] Long data high, query low
- [ ] Critical constraints restated at the end

## Common red flags → fix

| Red flag | Fix |
|----------|-----|
| Everything crammed in the user prompt | Move stable behavior to system prompt |
| "Be thorough" / "always query everything" | Replace with specific stop conditions |
| Untrusted input mixed with instructions | Fence and label as data |
| One happy-path example only | Add diverse + edge-case examples |
| `run_arbitrary_sql`-style tool | Replace with narrow, least-privilege tools |
| Output format only described, never shown | Add a literal example of the exact shape |
| Vague hand-waving | Raise specificity to the right altitude |
