---
name: systematic-debugging
description: Diagnoses bugs, test failures, and unexpected behavior using structured root cause analysis. Use when encountering any technical issue, error, or broken test, before proposing fixes. Covers reproduction, bisection, hypothesis testing, and fix verification.
---

# Systematic Debugging

## Before You Start

You MUST ask at least one clarifying question before beginning investigation.

Confirm with the user:
- [ ] **Scope**: Which component/file/test is affected?
- [ ] **Context**: What changed recently? (deploy, dependency update, config change)
- [ ] **Reproduction**: Can the user trigger it reliably, or is it intermittent?

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Stakeholder wants it fixed NOW (systematic is faster than thrashing)

## When NOT to Use

- **Typos / obvious one-character mistakes** - If the fix is self-evident and trivially verifiable, just fix it
- **Known configuration drift** - If the issue is a documented environment setup step that was skipped, follow the setup docs
- **Already diagnosed by another tool** - If a linter, type checker, or CI already pinpoints the exact cause and line, apply the fix directly
- **Non-technical issues** - Process problems, communication gaps, or requirement ambiguity need discussion, not debugging

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible, gather more data — don't guess

   **Example (TypeScript):**
   ```typescript
   // Minimal reproduction script
   const result = calculateDiscount(order);
   console.assert(result === 15.0, `Expected 15.0, got ${result}`);
   ```

3. **Check Recent Changes**
   - What changed that could cause this?
   - `git diff`, recent commits, `git log --oneline -10`
   - New dependencies, config changes
   - Environmental differences (local vs CI, dev vs prod)

4. **Isolate the Failing Component**

   **WHEN bug location is unclear, use bisection:**

   See `references/bisection-debugging.md` for the full binary search technique.

   **Quick version:**
   - Divide the suspect area in half
   - Test each half to determine which contains the bug
   - Repeat until isolated
   - Use `git bisect` when the bug was introduced by a recent commit

5. **Gather Evidence in Multi-Component Systems**

   **WHEN system has multiple components (API → service → database, CI → build → deploy):**

   **BEFORE proposing fixes, add diagnostic instrumentation:**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **Example (Python - API pipeline):**
   ```python
   # Layer 1: Request handler
   print(f"=== Request received: method={request.method}, path={request.path}")
   print(f"=== Auth header: {'SET' if request.headers.get('Authorization') else 'UNSET'}")

   # Layer 2: Service layer
   print(f"=== Service input: user_id={user_id}, action={action}")
   result = service.process(user_id, action)
   print(f"=== Service output: status={result.status}, data={result.data}")

   # Layer 3: Database layer
   print(f"=== Query: {query}, params={params}")
   rows = db.execute(query, params)
   print(f"=== Query returned {len(rows)} rows")
   ```

   **This reveals:** Which layer fails (request ✓, service ✓, database ✗)

6. **Trace Data Flow**

   **WHEN error is deep in call stack:**

   See `references/root-cause-tracing.md` for the complete backward tracing technique.

   **Quick version:**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

7. **Explain the Problem (Rubber Duck)**

   **WHEN you're stuck or confused:**

   See `references/rubber-duck-debugging.md` for the full technique.

   **Quick version:** Explain the problem step-by-step to the user. Articulate what SHOULD happen vs what DOES happen. This often reveals the gap.

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim — read every line
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

   **Example (PHP):**
   ```php
   // Working endpoint
   $user = $this->userRepository->find($id);  // Uses repository
   
   // Broken endpoint
   $user = User::where('id', $id)->first();   // Bypasses repository cache
   // ^ Different data access pattern - could this be the cause?
   ```

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help
   - Research more

   See `references/agent-pitfalls.md` for common agent mistakes during this phase.

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing

   **Example (TypeScript):**
   ```typescript
   it('should apply percentage discount correctly', () => {
     const order = createOrder({ subtotal: 100, discountPercent: 15 });
     const result = calculateDiscount(order);
     expect(result).toBe(15.0); // Currently returns 0.15 (bug)
   });
   ```

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?

4. **If Fix Doesn't Work**
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - **If >= 3: STOP and question the architecture (step 5 below)**
   - DON'T attempt Fix #4 without architectural discussion

   See `references/time-boxing.md` for guidance on when to escalate.

5. **If 3+ Fixes Failed: Question Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   **Discuss with the user before attempting more fixes.**

   This is NOT a failed hypothesis — this is a wrong architecture.

6. **Document What You Learned**

   See `references/post-fix-documentation.md` for the full pattern.

   **Quick version:** After fixing, briefly note the root cause, the fix, and what to watch for in future.

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 4.5)

## User Signals You're Doing It Wrong

**Watch for these redirections:**
- "Is that not happening?" — You assumed without verifying
- "Will it show us...?" — You should have added evidence gathering
- "Stop guessing" — You're proposing fixes without understanding
- "Think harder" — Question fundamentals, not just symptoms
- "We're stuck?" (frustrated) — Your approach isn't working

**When you see these:** STOP. Return to Phase 1.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms != understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, isolate, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify, document | Bug resolved, tests pass |

## When Process Reveals "No Root Cause"

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

## Supporting Techniques

These techniques are part of systematic debugging and available in this directory:

- **`references/root-cause-tracing.md`** — Trace bugs backward through call stack to find original trigger
- **`references/defense-in-depth.md`** — Add validation at multiple layers after finding root cause
- **`references/bisection-debugging.md`** — Narrow down bug location using binary search and git bisect
- **`references/rubber-duck-debugging.md`** — Explain the problem step-by-step to reveal hidden assumptions
- **`references/agent-pitfalls.md`** — Common mistakes AI agents make during debugging
- **`references/time-boxing.md`** — When to stop investigating and escalate
- **`references/post-fix-documentation.md`** — Capture learnings to prevent recurring bugs