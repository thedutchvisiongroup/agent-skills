# Cognitive Biases in Skill Design

## Overview

AI agents are susceptible to the same cognitive biases that affect human reasoning. These biases manifest both when agents *use* skills and when you *design* skills. Understanding these biases helps you write skills that produce reliable, accurate behavior even under pressure.

**Research foundation:** Mohanani et al. (2018) classified cognitive biases in software engineering into eight families. Chattopadhyay et al. (2020) demonstrated anchoring bias in design decisions. Meincke et al. (2025) showed AI agents respond to the same influence patterns as humans.

## Key Biases and Counter-Strategies

### 1. Anchoring Bias

**What it is:** Over-reliance on the first piece of information encountered.

**How it manifests in agents:**
- First example in a skill dominates behavior
- Initial interpretation of a task resists correction
- Early context frames all subsequent decisions

**Counter-strategies for skill design:**
- Place the most important rule first (it will anchor strongest)
- Provide multiple examples showing different scenarios
- Explicitly state when the first interpretation might be wrong

```markdown
- Bad: One example that covers the common case only
- Good: 2-3 examples covering common case, edge case, and "when NOT to apply"
```

### 2. Confirmation Bias

**What it is:** Seeking information that confirms existing beliefs while ignoring contradictory evidence.

**How it manifests in agents:**
- Agent interprets ambiguous requirements to match its first guess
- Selectively reads parts of a skill that support its current approach
- Ignores "when NOT to use" sections

**Counter-strategies for skill design:**
- Include explicit "devil's advocate" sections
- Add "When NOT to use" with concrete examples
- Use red flags lists to trigger self-correction

```markdown
## When NOT to Use This Pattern
- When the data set is small (<100 records) — use direct iteration instead
- When real-time performance matters — this pattern adds latency
- When the source is already validated — double-validation wastes cycles
```

### 3. Premature Closure

**What it is:** Stopping information gathering too early and committing to a solution before the problem is fully understood.

**How it manifests in agents:**
- Jumping to implementation before reading the full skill
- Skipping verification steps in workflows
- Declaring "done" before checking all acceptance criteria

**Counter-strategies for skill design:**
- Add mandatory verification checkpoints
- Use "STOP and verify" gates before proceeding
- Require explicit completion checklists

```markdown
## Before Marking Complete
STOP. Verify ALL of the following:
- [ ] All acceptance criteria met
- [ ] Edge cases considered
- [ ] No assumptions left unverified
```

### 4. Availability Bias

**What it is:** Over-relying on the most recent or memorable solution, even when it's not the best fit.

**How it manifests in agents:**
- Defaulting to patterns from recent conversations
- Applying familiar frameworks to unfamiliar problems
- Recommending tools the agent has used recently over better alternatives

**Counter-strategies for skill design:**
- Document multiple valid approaches, not just the default
- Explicitly state when the "obvious" approach is wrong
- Include decision criteria for choosing between approaches

```markdown
## Choosing an Approach
| Situation | Use | Don't Use |
|-----------|-----|-----------|
| Small data (<1k rows) | Direct processing | Streaming pipeline |
| Large data (>100k rows) | Streaming pipeline | Loading all into memory |
| Real-time requirement | Event-driven | Batch processing |
```

### 5. Automation Bias

**What it is:** Users over-trusting automated/AI output without critical evaluation.

**How it manifests:**
- Users accept agent output without verification
- Agents present uncertain results with high confidence
- Skill outputs bypass human review

**Counter-strategies for skill design:**
- Build verification steps that involve the user
- Flag areas of uncertainty explicitly
- Include "human review required" checkpoints for high-stakes outputs

```markdown
## Output Verification
The following outputs REQUIRE human review before use:
- Any changes to production configuration
- Generated SQL that modifies data
- Security-related recommendations
```

### 6. Sunk Cost Fallacy

**What it is:** Continuing with an approach because of time already invested, even when switching would be better.

**How it manifests in agents:**
- Continuing a failing approach rather than starting over
- Adding complexity to fix symptoms instead of changing strategy
- Defending an implementation choice after discovering it's wrong

**Counter-strategies for skill design:**
- Include explicit "abort criteria" in workflows
- Normalize starting over as a valid outcome
- Add "if stuck after N attempts, change approach" rules

```markdown
## When to Abandon This Approach
If after 3 attempts the pattern doesn't work:
1. STOP trying to make it work
2. Document what you learned
3. Consider an alternative approach
4. Discuss with the user before continuing
```

## Combining Biases with Persuasion Principles

Cognitive biases and persuasion principles (see [persuasion-principles.md](./persuasion-principles.md)) work together:

| Bias to Counter | Persuasion Principle | Technique |
|-----------------|---------------------|-----------|
| Premature closure | **Commitment** | Require explicit "I have verified X" statements |
| Confirmation bias | **Authority** | "You MUST consider at least one alternative" |
| Anchoring | **Social proof** | "Every experienced developer considers multiple approaches" |
| Automation bias | **Scarcity** | "Review IMMEDIATELY before applying changes" |
| Sunk cost | **Authority** | "Starting over is NOT failure. It's professionalism." |

## Designing Bias-Resistant Skills

**General principles:**

1. **Make the right behavior easier than the wrong behavior** — if verification is easy, agents will do it
2. **Assume the bias will occur** — don't hope agents won't anchor; design for it
3. **Use multiple counter-measures** — combine bright-line rules with checklists and red flags
4. **Test for bias** — evaluate skills by looking for bias-driven failures, not just functional correctness

## Research Citations

**Tversky, A. & Kahneman, D. (1974).** Judgment Under Uncertainty: Heuristics and Biases. *Science*, 185(4157), 1124-1131.
- Foundation for anchoring, availability, and representativeness biases
- Directly applicable to AI agent reasoning patterns

**Mohanani, R. et al. (2018).** Cognitive Biases in Software Engineering: A Systematic Mapping Study. *IEEE Transactions on Software Engineering*, 46(12), 1318-1339.
- Classified biases into 8 families: interest, stability, action-oriented, pattern recognition, perception, memory, decision, social
- Identified confirmation bias and anchoring as most prevalent in SE

**Chattopadhyay, S. et al. (2020).** A Tale from the Trenches: Cognitive Biases and Software Development. *ICSE 2020*.
- Demonstrated anchoring bias in real-world design decisions
- Engineers who saw initial designs stuck with them despite better alternatives

**Meincke, L. et al. (2025).** Call Me A Jerk: Persuading AI to Comply with Objectionable Requests. University of Pennsylvania.
- Validated that AI agents respond to human persuasion patterns
- Authority and commitment techniques most effective for compliance
