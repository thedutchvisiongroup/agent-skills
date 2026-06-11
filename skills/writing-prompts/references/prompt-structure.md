# Prompt Structure: XML vs Markdown

## Default: XML

XML is the default for production agent prompts because it provides:

- **Explicit semantic boundaries** — `<instructions>`, `<context>`, `<input>`, `<output_format>` make intent unambiguous.
- **Unambiguous nesting** — natural hierarchy (`<documents>` → `<document index="1">` → `<document_content>`).
- **Separation of instructions from data** — wrapping untrusted input in a labeled tag reduces prompt-injection risk and "where do instructions end" guessing.
- **Steerable output** — asking for output inside a named tag (e.g. `<answer>`) is reliable to parse.

This matches Anthropic's recommendation to "structure prompts with XML tags" and to wrap examples in `<example>`/`<examples>` tags. It generalizes well to GPT and Gemini too.

### Why not just delimiters?

Plain delimiters (`###`, triple quotes) work for simple prompts and are fine for a single block of untrusted input. XML scales better once a prompt mixes instructions + context + examples + variables.

## When to use Markdown instead

- The user explicitly prefers Markdown.
- The target platform mandates Markdown system prompts (some agent builders do).
- The prompt is short and single-purpose (a role + one instruction + output format).

Markdown is readable and great for headings/bullets, but section boundaries are softer than XML tags. If you use Markdown, keep headings consistent (`##` for top-level sections) and still delimit untrusted input explicitly.

## Tag naming conventions (XML)

- Use **consistent, descriptive, lowercase_snake** names: `<role>`, `<instructions>`, `<tools>`, `<guardrails>`, `<context>`, `<task>`, `<output_format>`, `<examples>`, `<example>`.
- One concept per tag. Nest only when there is a real hierarchy.
- Match the tag you ask the model to fill (`<answer>`) to the tag you parse downstream.
- Reuse the same tag names across your prompt suite so the agent (and your code) learn one vocabulary.

## Format influences output

The formatting style of your prompt leaks into the model's output. Markdown-heavy prompts produce markdown-heavy answers. If you want flowing prose, reduce markdown in the prompt and say so explicitly. If you want structured output, structure the prompt the same way.

## Decision rule

```
Mixed instructions + context + examples + variables, or an agent?  -> XML
Single short instruction, or platform requires it?                 -> Markdown
Only one block of untrusted input to fence?                        -> delimiters are enough
```

Whatever the choice, confirm it in the clarification gate — never assume.
