# Clarifying Questions for Skill Design

## Overview

The single most impactful thing an AI agent can do before executing a task is **ask clarifying questions**. Ambiguous requirements lead to wasted effort, incorrect implementations, and frustrated users. Yet agents consistently skip this step, defaulting to assumptions instead of inquiry.

**Core principle:** When in doubt, ASK. When not in doubt, verify your assumptions anyway.

**Research foundation:** Deng et al. (2023) demonstrated that current LLMs have a strong tendency to not ask clarifying questions, even when requests are ambiguous. Kobalczyk et al. (2025) showed that Bayesian-optimal question selection can maximize information gain from minimal clarifying interactions.

## The Psychology: Why Agents Skip Questions

AI agents exhibit the same cognitive shortcuts as humans when facing ambiguous tasks:

### Premature Execution Bias

**What it is:** The tendency to start working immediately rather than gathering sufficient information first.

**Why it happens:**
- Training data rewards action over inquiry
- Agents optimize for perceived helpfulness (doing something > asking something)
- Users often expect immediate output, creating implicit pressure

**Impact on skills:** If a skill doesn't explicitly require clarification, agents will assume and proceed.

### Confirmation Bias

**What it is:** The tendency to interpret ambiguous requirements in a way that confirms the agent's initial understanding.

**Why it happens:**
- First interpretation anchors all subsequent reasoning
- Agents rarely generate alternative interpretations
- Asking "did I understand correctly?" feels like admitting uncertainty

**Impact on skills:** Agents fill in gaps with plausible-sounding assumptions rather than identifying what they don't know.

### Anchoring Effect

**What it is:** Over-reliance on the first piece of information encountered.

**Why it happens:**
- Initial context frames the entire task
- Early details receive disproportionate weight
- Later contradictions are rationalized away

**Impact on skills:** The first example or requirement in a skill dominates behavior, even when later sections provide nuance.

### The Completion Drive

**What it is:** Strong bias toward producing a complete output rather than an accurate partial one.

**Why it happens:**
- Incomplete responses feel like failures
- Training rewards complete, coherent outputs
- "I need more information" feels less valuable than "Here's my answer"

**Impact on skills:** Agents would rather deliver a wrong-but-complete result than pause and ask.

## When to Ask Clarifying Questions

**Always ask when:**
- Requirements are ambiguous or underspecified
- Multiple valid interpretations exist
- Implicit assumptions could change the approach significantly
- The task scope is unclear (what's in, what's out?)
- Constraints haven't been stated (performance, compatibility, style)
- The cost of getting it wrong is high

**Don't ask when:**
- The answer is already in the provided context
- The question is trivially obvious
- You've already asked about the same thing
- The task is well-specified with clear acceptance criteria

## Question Taxonomy

Use these categories to systematically identify what you don't know:

### 1. Scope Questions

Clarify boundaries of the task.

```markdown
- "Which files/components are in scope for this change?"
- "Should this apply to existing data, or only new entries?"
- "Are there related systems that need updating too?"
```

### 2. Constraint Questions

Surface hidden requirements.

```markdown
- "Are there performance requirements I should consider?"
- "Does this need to be backwards-compatible?"
- "Are there coding style or framework preferences?"
```

### 3. Preference Questions

Resolve ambiguity when multiple valid approaches exist.

```markdown
- "Do you prefer approach A (faster, less flexible) or B (slower, more extensible)?"
- "Should error handling be strict (fail fast) or lenient (best effort)?"
- "Is conciseness or readability more important here?"
```

### 4. Validation Questions

Confirm your understanding before proceeding.

```markdown
- "Let me confirm: you want X to do Y when Z happens. Correct?"
- "My understanding is [summary]. Is there anything I'm missing?"
- "Before I start: the main goal is [X], and [Y] is out of scope. Right?"
```

### 5. Priority Questions

Understand what matters most when tradeoffs exist.

```markdown
- "If I can only achieve two of these three goals, which matters most?"
- "Should I optimize for speed of delivery or thoroughness?"
- "Is the MVP version acceptable, or do you need the full solution?"
```

## The Socratic Pattern for Skills

When designing skills, build in a clarification phase using this pattern:

### 1. Define

Establish what you know from the provided context.

### 2. Clarify

Identify gaps, ambiguities, and implicit assumptions. Ask targeted questions.

### 3. Challenge

Question your own interpretation. Generate at least one alternative reading of the requirements.

### 4. Validate

Summarize your understanding and get explicit confirmation before proceeding.

### 5. Execute

Only now begin the actual work.

**Example in a skill:**
```markdown
## Before Starting

1. Read the full request carefully
2. Identify at least ONE assumption you're making
3. Ask the user to confirm or correct that assumption
4. Summarize your plan in 2-3 sentences
5. Wait for approval before implementing
```

## Anti-Patterns

### Asking too many questions at once

```markdown
- Bad: 10 questions in a wall of text (user overwhelmed, skips half)
- Good: 2-3 most critical questions, grouped logically
```

### Asking overly broad questions

```markdown
- Bad: "What do you want?"
- Good: "Should the output be in JSON or CSV format?"
```

### Asking when the answer is in context

```markdown
- Bad: "What language should I use?" (when the file is clearly Python)
- Good: Read context first, ask only about genuinely missing information
```

### Asking instead of proposing

```markdown
- Bad: "How should I structure this?"
- Good: "I'd structure this as X. Does that align with your expectations?"
```

## Designing Skills That Encourage Clarification

When writing skills, explicitly build in clarification triggers:

**Use commitment language** (see [persuasion-principles.md](./persuasion-principles.md)):
```markdown
## Before You Start
You MUST ask at least one clarifying question before beginning implementation.
```

**Provide question templates:**
```markdown
## Required Clarifications
Before proceeding, confirm:
- [ ] Scope: What files/components are affected?
- [ ] Constraints: Are there compatibility requirements?
- [ ] Priority: What's the most important outcome?
```

**Make it a gate, not a suggestion:**
```markdown
## Phase 1: Understand (REQUIRED)
Do NOT skip to implementation. Complete this phase first.
1. Read the full request
2. List your assumptions
3. Ask clarifying questions
4. Get confirmation

## Phase 2: Implement
Only after Phase 1 is complete.
```

## Quick Reference

| Signal | Action |
|--------|--------|
| Ambiguous requirement | Ask a scope or preference question |
| Multiple valid approaches | Ask a preference question with your recommendation |
| Hidden assumptions | Ask a validation question |
| Unclear priority | Ask a priority question |
| Well-specified task | Proceed (but state your assumptions briefly) |
| High-stakes change | Always validate before executing |

## Research Citations

**Deng, Y. et al. (2023).** Prompting and Evaluating Large Language Models for Proactive Dialogues. Findings of EMNLP.
- LLMs have strong tendency to not ask clarifying questions
- Prompting techniques can trigger clarification behavior

**Kobalczyk, K. et al. (2025).** Active Task Disambiguation with LLMs. University of Oxford.
- Bayesian Experimental Design for optimal question selection
- Maximizing information gain from minimal clarifying interactions

**Zhang, Y. et al. (2024).** Ask-before-Plan: Proactive Language Agents for Real-World Planning.
- Agents that ask before executing outperform those that assume
- Proactive clarification reduces error rates significantly

**Tversky, A. & Kahneman, D. (1974).** Judgment Under Uncertainty: Heuristics and Biases. Science.
- Foundation for understanding anchoring, availability, and confirmation biases
- Directly applicable to how AI agents process ambiguous instructions
