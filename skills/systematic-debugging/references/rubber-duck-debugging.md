# Rubber Duck Debugging

## Overview

Explaining a problem out loud — even to an inanimate object — forces you to articulate assumptions you haven't examined. For AI agents, this means explaining the problem step-by-step to the user instead of silently reasoning and jumping to a fix.

**Core principle:** When stuck, EXPLAIN the problem to the user before attempting to solve it. The act of articulation reveals hidden assumptions and logic gaps.

## When to Use

- You've been investigating for multiple steps without progress
- The bug doesn't match your mental model of the code
- You're confused about what the code SHOULD do vs what it DOES
- Multiple hypotheses seem equally plausible
- You're about to guess instead of understand

## The Technique

### Step 1: State the Expected Behavior

```
"This function should take an order with a 15% discount coupon
and return a subtotal of 85.00 for a 100.00 order."
```

Be specific. Use concrete values, not abstractions.

### Step 2: State the Actual Behavior

```
"Instead, it returns 0.15 — which looks like the discount percentage
itself rather than the discounted total."
```

### Step 3: Walk Through the Code Path

Explain each step the code takes:

```
"The function receives the order object.
It calls calculateSubtotal() which returns 100.00 — correct.
It then calls applyDiscount(100.00, 15).
Inside applyDiscount, it does: subtotal * (discount / 100).
That gives 100 * 0.15 = 15.0.
But then it returns the discount AMOUNT, not subtotal - discount.
That's the bug — it returns the discount, not the discounted price."
```

### Step 4: Identify the Gap

The gap between expected and actual behavior is now visible:
- **Expected:** Return `subtotal - discountAmount`
- **Actual:** Returns `discountAmount`

## For AI Agents Specifically

As an AI agent, you MUST externalize your reasoning to the user when stuck:

**Do this:**
```
"Let me walk through what I understand:
1. The request hits /api/orders/:id
2. The controller calls OrderService.getById(id)
3. The service queries the database...
4. Wait — I see the service is using a raw query instead of the
   repository method. The repository applies soft-delete filtering,
   but the raw query doesn't. That could return deleted orders."
```

**Don't do this:**
```
"I think the issue might be related to the query. Let me try
adding a WHERE clause."
```

The first version shows understanding. The second is a guess.

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Explaining too abstractly | "Something is wrong with the data flow" reveals nothing. Use specific values. |
| Skipping to the fix | The point is understanding, not fixing. Fix comes AFTER understanding. |
| Only explaining what you already know | Focus on the parts you DON'T understand. That's where the bug lives. |
| Silently reasoning | The user can't help if they can't see your reasoning. Externalize it. |

## Quick Checklist

Before proposing a fix, can you answer ALL of these?

- [ ] What SHOULD this code do? (specific input → expected output)
- [ ] What DOES it actually do? (specific input → actual output)
- [ ] WHERE exactly does the behavior diverge?
- [ ] WHY does it diverge there?

If any box is unchecked, you don't understand the bug yet. Keep explaining.
