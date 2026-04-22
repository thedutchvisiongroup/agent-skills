# Time-Boxing Investigation

## Overview

Debugging without a time limit leads to tunnel vision. You keep digging deeper into one hypothesis while the answer might be obvious from a different angle. Time-boxing forces periodic reassessment.

**Core principle:** Set investigation checkpoints. If you haven't made progress after a defined effort, change your approach — don't keep digging the same hole.

## When to Use

- Investigation has been going on for multiple rounds without progress
- You've tried 2+ fixes and none worked
- The same clue keeps leading to dead ends
- You're adding more and more logging without getting closer

## The Escalation Ladder

### Checkpoint 1: After 2 Failed Hypotheses

**Reassess your understanding:**
- Re-read the original error message from scratch
- List what you KNOW vs what you ASSUME
- Ask: "Am I looking in the right place?"
- Consider: Is this a different bug than I think?

### Checkpoint 2: After 3 Failed Fixes

**Question the approach:**
- Stop fixing and return to Phase 1 (Root Cause Investigation)
- Try a completely different investigation angle
- Read the code path from the entry point, not from the error
- Ask the user for more context about when/how the bug occurs

### Checkpoint 3: After Exhausting Local Investigation

**Escalate to the user:**

```
"I've investigated [specific areas] and tested [specific hypotheses].
Here's what I've confirmed:
- [fact 1]
- [fact 2]

I haven't been able to isolate the root cause. I recommend:
- [option A: specific next investigation step]
- [option B: alternative approach]
- [option C: involve someone with domain knowledge]

Which direction would you like to go?"
```

## What to Include When Escalating

ALWAYS provide:
1. **What you investigated** — Specific files, functions, code paths
2. **What you tested** — Hypotheses and their results
3. **What you ruled out** — Areas confirmed NOT to be the cause
4. **What you suspect** — Your best remaining hypothesis with evidence level
5. **Recommended next steps** — Concrete options, not vague suggestions

## Anti-Patterns

| Anti-Pattern | Better Approach |
|-------------|-----------------|
| "I'll keep trying" (after 3+ failures) | Escalate with findings |
| "Let me try one more thing" | State what that thing is and WHY, then try |
| Silently continuing without update | Share progress: "I've ruled out X, now investigating Y" |
| Escalating with no information | Always include what you tried and what you learned |
| Giving up without options | Provide 2-3 concrete next steps for the user to choose |

## Key Insight

**Escalation is not failure.** Providing a structured summary of what you investigated, what you ruled out, and what remains is valuable work. The next person (or your next attempt) starts from a much stronger position.
