# Prompting Techniques

Research-backed techniques. Pick by task; do not stack all of them blindly.

## Role prompting

Assign a concrete, task-relevant role in the system prompt. Improves relevance, tone, and domain focus.

- Keep it concise and realistic; overly elaborate personas add noise.
- State the role first, then pair with clear task instructions.
- Example: `You are a skeptical venture capitalist. Review the pitch and list 3 pros and 3 cons.`

## Few-shot (multishot)

Provide examples of input → output. One of the most reliable ways to steer format, tone, and structure.

- Use **3–5** examples for best results.
- Make them **relevant** (mirror the real use case), **diverse** (cover edge cases), and **structured** (wrap in `<example>` tags; group in `<examples>`).
- Curate canonical examples; do NOT dump every edge case as a rule list.
- Label distribution and format matter — keep outputs in the exact target shape.

## Chain-of-Thought (CoT)

Ask the model to reason step by step before answering. Helps arithmetic, logic, and multi-step tasks.

- Zero-shot CoT: add "Let's think step by step."
- Few-shot CoT: include examples that show the reasoning steps.
- For user-facing output, separate reasoning from the final answer (e.g. reasoning in `<scratchpad>`, result in `<answer>`), or rely on the model's native thinking mode and only surface the answer.

## ReAct (Reason + Act)

Interleave reasoning traces with tool actions: **Thought → Action → Observation → … → Finish.** The backbone of tool-using agents; reduces fact hallucination by grounding actions in real observations.

```
Thought: I need the customer's current plan before recommending an upgrade.
Action: get_subscription(customer_id="123")
Observation: { "plan": "Pro", "seats": 12 }
Thought: They are on Pro with 12 seats; Enterprise unlocks SSO they asked about.
Action: Finish("Recommend Enterprise: it adds SSO and unlimited seats.")
```

Specify the loop format explicitly and tell the agent when to stop.

## Reflexion / self-correction

After an attempt (or a failed action), have the agent critique its own output against the goal and retry. Useful for code, planning, and tasks with verifiable success criteria.

- Give it a concrete check ("verify the result satisfies all constraints; if not, revise once").
- Bound the retries to avoid loops.

## Tool / function-calling design

The tool description is part of the prompt and strongly shapes behavior.

- Precise name + description of what it does and returns.
- Explicit **when to use / when NOT to use**.
- **Narrow scope (least privilege):** prefer `get_user_by_id` over `run_arbitrary_sql`.
- Avoid "ALWAYS call tool X" — it causes over-triggering on every turn. Describe the condition instead.
- State what to do when a tool fails or returns unexpected data.

## Meta / format-first prompting

For complex outputs, describe the structure and logic of the answer (the "shape") rather than relying only on examples. Combine with one example that anchors the literal format.

## Choosing techniques

```
Needs domain framing?            -> role
Output shape must be exact?      -> few-shot (3–5) + explicit output_format
Multi-step reasoning?            -> CoT
Uses tools / external state?     -> ReAct
Verifiable goal, want retries?   -> Reflexion
```
