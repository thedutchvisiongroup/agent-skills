---
name: writing-skills
description: Guide for creating, improving, and reviewing AI agent skills. Use when writing new skills, editing existing skills, reviewing skill quality, or learning how to structure skill content effectively.
---

# Writing Skills

## Iron Law

**You MUST ask clarifying questions before writing or editing any skill.**

Ambiguous requirements lead to wasted effort and incorrect skills. Before you touch a single line, complete the Clarification Phase below. See [references/clarifying-questions.md](references/clarifying-questions.md) for the full framework — this is the most important reference in this skill.

## Process: Four Phases

### Phase 1: Clarify (REQUIRED — DO NOT SKIP)

Before writing anything, you MUST:

1. **Read the full request** carefully
2. **Identify your assumptions** — list at least TWO
3. **Ask clarifying questions** — at minimum:
   - What is the skill's **scope**? (What's in, what's out?)
   - What **constraints** exist? (Compatibility, style, framework preferences?)
   - What does **success** look like? (Acceptance criteria)
4. **Summarize your plan** in 2-3 sentences
5. **Wait for confirmation** before proceeding

```
STOP. Have you asked clarifying questions?
- [ ] Yes, I identified my assumptions
- [ ] Yes, I asked at least one scope/constraint/preference question
- [ ] Yes, I got confirmation before proceeding
If any box is unchecked: GO BACK. Do not proceed.
```

> **Why this matters:** Agents have a strong bias toward premature execution — jumping to implementation before gathering sufficient information. This phase exists to counter that bias. See [references/cognitive-biases.md](references/cognitive-biases.md) for details.

### Phase 2: Structure

Design the skill's architecture before writing content.

**Every skill requires:**
- `SKILL.md` with YAML frontmatter (`name` + `description`)
- Clear, scannable instructions in the body

**Key decisions:**
1. **Scope** — One skill, one responsibility. If it does two unrelated things, split it.
2. **Content budget** — Keep SKILL.md under 500 lines. Move details to reference files.
3. **Degrees of freedom** — How much latitude does the agent get?
   - **Low freedom**: Fragile operations, exact sequences (e.g., database migrations)
   - **High freedom**: Context-dependent tasks, multiple valid approaches (e.g., code review)

**Directory structure:**
```
skill-name/
├── SKILL.md              # Core instructions (<500 lines)
├── references/           # Deep-dive materials (loaded as needed)
│   ├── guide.md
│   └── examples.md
└── scripts/              # Utility scripts (executed, not loaded)
    └── validate.py
```

For progressive disclosure patterns, see [references/progressive-disclosure.md](references/progressive-disclosure.md).

### Phase 3: Write

Write the skill content following these principles:

**Conciseness** — The agent is already capable. Only add context it doesn't have. Challenge every paragraph: does this justify its token cost? See [references/anthropic-best-practices.md](references/anthropic-best-practices.md).

**Persuasion** — Use commitment language, authority cues, and bright-line rules to ensure compliance on critical steps. "MUST" beats "should". "ALWAYS" beats "try to". See [references/persuasion-principles.md](references/persuasion-principles.md).

**Bias resistance** — Design for cognitive biases the agent will exhibit:
- Add "When NOT to use" sections (counters confirmation bias)
- Provide multiple examples, not just the happy path (counters anchoring)
- Include verification checkpoints (counters premature closure)
- See [references/cognitive-biases.md](references/cognitive-biases.md)

**Description quality** — The `description` field is critical: it's the only thing loaded at startup. Include WHAT the skill does AND WHEN to use it. Write in third person.

**Clarification gates** — Build clarification triggers INTO the skill you're writing:
```markdown
## Before You Start
You MUST ask at least one clarifying question before beginning.
Confirm scope, constraints, and success criteria with the user.
```

### Phase 4: Validate

Test the skill before declaring it done.

1. **Self-review checklist:**
   - [ ] Description includes what AND when
   - [ ] SKILL.md body is under 500 lines
   - [ ] Instructions are specific, not vague
   - [ ] Examples cover common case + edge case + "when NOT to"
   - [ ] Clarification phase is built into the skill
   - [ ] No vendor-specific references (implementation-agnostic)
   - [ ] Consistent terminology throughout
   - [ ] File references are one level deep from SKILL.md

2. **Real-world test:** Use the skill on a representative task. Does the agent:
   - Find the right information?
   - Follow the critical rules?
   - Ask clarifying questions when it should?

3. **Iterate:** Fix what doesn't work. Re-test. Repeat.

## Red Flags — Signs Your Skill Needs Work

| Signal | Problem | Fix |
|--------|---------|-----|
| Agent skips verification steps | Rules aren't strong enough | Use MUST/ALWAYS + checklists |
| Agent makes wrong assumptions | No clarification phase | Add Phase 1 gate |
| Agent loads too much context | Poor progressive disclosure | Split into reference files |
| Skill works on one model but not another | Over/under-specified | Adjust degrees of freedom |
| Agent ignores edge cases | Only happy-path examples | Add "When NOT to" sections |
| Description doesn't trigger skill | Vague description | Add specific trigger terms |

## Quick Reference: References

| Reference | When to Read |
|-----------|-------------|
| [clarifying-questions.md](references/clarifying-questions.md) | **ALWAYS** — the most important reference |
| [anthropic-best-practices.md](references/anthropic-best-practices.md) | For authoring patterns, structure, and progressive disclosure |
| [skills-overview.md](references/skills-overview.md) | For understanding how skills work architecturally |
| [persuasion-principles.md](references/persuasion-principles.md) | For making critical instructions stick |
| [cognitive-biases.md](references/cognitive-biases.md) | For designing bias-resistant skills |
| [progressive-disclosure.md](references/progressive-disclosure.md) | For structuring large skills efficiently |
