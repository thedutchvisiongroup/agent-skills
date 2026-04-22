# Agent-Specific Debugging Pitfalls

## Overview

AI coding agents exhibit systematic biases during debugging that human developers don't. These pitfalls cause agents to propose wrong fixes, waste investigation time, or make bugs worse. Recognizing these patterns is the first step to avoiding them.

## Pitfall 1: Hallucinating Root Causes

**What happens:** The agent confidently identifies a root cause that doesn't exist — inventing plausible-sounding explanations based on pattern matching rather than evidence.

**Example:**
```
Agent: "The issue is that the Redis connection pool is exhausted because
       the connection timeout is set too low."
Reality: Redis isn't involved in this code path at all.
```

**Prevention:**
- ALWAYS verify your hypothesis against actual code before stating it
- Grep for the function/class/variable you're blaming — does it actually exist?
- Run the code path mentally or with logging before claiming causation
- If you can't point to a specific line number, you're guessing

## Pitfall 2: Overconfidence in First Hypothesis

**What happens:** The agent forms a hypothesis based on the first clue and stops investigating, even when evidence is insufficient.

**Example:**
```
Agent: "The test fails because the mock isn't returning the right value."
       *changes mock, still fails*
       "The mock format must be wrong."
       *changes format, still fails*
Reality: The function under test has a logic error that no mock change will fix.
```

**Prevention:**
- Generate at least TWO alternative hypotheses before committing to one
- Ask: "What else could explain these symptoms?"
- If your first fix doesn't work, seriously consider that your hypothesis is wrong — don't just tweak it

## Pitfall 3: Fixing Symptoms Without Verifying the Fix Path

**What happens:** The agent proposes a fix without verifying that the fix actually addresses the code path where the bug occurs.

**Example (PHP):**
```php
// Agent adds validation here:
public function store(Request $request) {
    $validated = $request->validate(['email' => 'required|email']);
    // ...
}

// But the bug is in the API endpoint, not the web endpoint:
// routes/api.php → ApiController@store (different controller entirely)
```

**Prevention:**
- Trace the EXACT code path that triggers the bug
- Verify your fix is in the right file, right class, right method
- Search for duplicate implementations — the bug might be in a copy you didn't find

## Pitfall 4: Assuming Code Works Without Running It

**What happens:** The agent reads code, decides it "looks correct," and moves on without actually executing or testing it.

**Example:**
```
Agent: "The sorting function looks correct, the issue must be elsewhere."
Reality: The comparison function has a subtle off-by-one error that only
         manifests with arrays longer than 10 elements.
```

**Prevention:**
- "Looks correct" is NOT evidence. Run it.
- Add logging at the suspect point and check the actual output
- Never say "this code is fine" without testing with the failing input

## Pitfall 5: Proposing Massive Refactors for Simple Bugs

**What happens:** The agent identifies a real issue but proposes an unnecessarily complex solution — rewriting modules, adding new abstractions, or restructuring code.

**Example:**
```
Bug: Missing null check causes crash
Agent: "We should introduce the Null Object pattern across the codebase,
       create a base handler class, and..."
Fix: Add `if (user === null) return;` — one line.
```

**Prevention:**
- ALWAYS ask: "What is the SMALLEST fix that addresses the root cause?"
- Match fix complexity to bug complexity
- Save refactoring suggestions for after the bug is fixed, as separate work

## Pitfall 6: Ignoring Environment Differences

**What happens:** The agent debugs assuming one environment but the bug only occurs in another.

**Common mismatches:**
- Local vs CI (different OS, different Node/PHP/Python version)
- Dev vs production (different config, different data volume)
- Fresh install vs existing install (missing migrations, cached state)

**Prevention:**
- Ask early: "Where does this bug occur? Local, CI, production?"
- Check environment-specific config before diving into code
- Compare versions: runtime, dependencies, OS

## Pitfall 7: Not Reading the Full Error

**What happens:** The agent reads the first line of an error message and stops, missing critical context in the full stack trace or error details.

**Example:**
```
Error: Cannot read properties of undefined (reading 'map')
Agent: "The array is undefined, let me add a null check."

Full error (which agent didn't read):
  at UserList.render (UserList.tsx:42)
  at processChild (react-dom.js:1234)
  caused by: fetchUsers returned { data: undefined } because API returned 401
```

**Prevention:**
- ALWAYS read the complete error output
- Read stack traces bottom-to-top to find the original trigger
- Look for "caused by", "Caused by", or nested exceptions

## Quick Self-Check

Before proposing any fix, verify:

- [ ] I can point to the EXACT line(s) causing the bug
- [ ] I have EVIDENCE (not just reasoning) for my hypothesis
- [ ] I verified my fix is in the correct code path
- [ ] My fix is proportional to the bug (not an over-engineered solution)
- [ ] I considered at least one alternative explanation
