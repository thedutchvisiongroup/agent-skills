# Post-Fix Documentation

## Overview

Fixing a bug without documenting the lesson means the same class of bug will recur. Spending 30 seconds recording what you learned saves hours of future debugging.

**Core principle:** Every bug fix is a learning opportunity. Capture the root cause, the fix, and the pattern to watch for.

## When to Use

- After ANY non-trivial bug fix (skip for obvious typos)
- When the root cause was surprising or non-obvious
- When the bug took multiple attempts to fix
- When the bug could easily recur in similar code

## The Three-Line Pattern

After fixing a bug, add a brief note. This can be a code comment, a commit message, or a message to the user:

```
ROOT CAUSE: [What actually caused the bug]
FIX: [What was changed and why]
WATCH FOR: [What to check in similar code]
```

### Example (commit message)

```
fix: correct discount calculation returning percentage instead of amount

ROOT CAUSE: applyDiscount() returned `subtotal * (discount / 100)` which
is the discount amount, but callers expected the discounted price.

FIX: Changed return to `subtotal - (subtotal * (discount / 100))`.

WATCH FOR: Other calculation functions that may confuse "the delta" with
"the result after applying the delta".
```

### Example (code comment)

```typescript
// FIX(2025-01): Previously returned discount amount instead of discounted price.
// The discount parameter is a percentage (e.g., 15 for 15%), not a multiplier.
const applyDiscount = (subtotal: number, discountPercent: number): number => {
  return subtotal - (subtotal * (discountPercent / 100));
};
```

### Example (PHP DocBlock)

```php
/**
 * Apply percentage discount to subtotal.
 *
 * Note: $discountPercent is a whole number (e.g., 15 for 15%), not a decimal.
 * A previous bug returned the discount amount instead of the discounted price.
 */
public function applyDiscount(float $subtotal, float $discountPercent): float
{
    return $subtotal - ($subtotal * ($discountPercent / 100));
}
```

## When to Add Regression Tests

ALWAYS add a regression test when:
- The bug was in business logic (calculations, state transitions, permissions)
- The bug was caused by an edge case that wasn't covered
- The bug could be reintroduced by refactoring

A regression test is the strongest form of documentation — it actively prevents the bug from returning.

```typescript
describe('applyDiscount - regression', () => {
  it('should return discounted price, not discount amount', () => {
    // Regression: previously returned 15.0 instead of 85.0
    expect(applyDiscount(100, 15)).toBe(85.0);
  });
});
```

## What NOT to Document

- Typos and obvious syntax errors
- Dependency version bumps that just work
- Build tool configuration that's environment-specific
- Anything that would be noise rather than signal

## Quick Checklist

After fixing a non-trivial bug:

- [ ] Root cause is documented (commit message, comment, or shared with user)
- [ ] Regression test exists for business logic bugs
- [ ] "Watch for" pattern identified for similar code
- [ ] User informed of what was wrong and what to look for in future
