# Bisection Debugging

## Overview

When the bug location is unclear — it could be anywhere in a large codebase or commit history — linear searching wastes time. Binary search cuts the problem space in half with each step.

**Core principle:** Don't search linearly. Divide and conquer to isolate the bug in O(log n) steps.

## When to Use

- Bug exists somewhere in a large file or module
- A feature worked before but broke at some point
- You can't tell which of many recent changes caused the issue
- Multiple components could be at fault

## Code Bisection

Narrow down the bug location within code by systematically halving the suspect area.

### The Process

1. **Identify the suspect area** — The function, module, or pipeline where the bug manifests
2. **Divide in half** — Comment out, disable, or bypass the second half
3. **Test** — Does the bug still occur?
   - **Yes** → Bug is in the first half. Divide that half again.
   - **No** → Bug is in the second half. Restore first half, divide second half.
4. **Repeat** until isolated to a small section

### Example (TypeScript)

```typescript
// Suspect: processOrder() produces wrong total
// Step 1: Bypass second half
const processOrder = (order: Order): number => {
  const subtotal = calculateSubtotal(order.items);
  const discounted = applyDiscounts(subtotal, order.coupons);
  
  // BISECT: Return here to test first half
  // return discounted;
  
  const taxed = applyTax(discounted, order.region);
  const total = addShipping(taxed, order.shippingMethod);
  return total;
};

// If returning early gives correct value → bug is in applyTax or addShipping
// If returning early gives wrong value → bug is in calculateSubtotal or applyDiscounts
```

### Example (Python)

```python
# Suspect: data pipeline produces wrong output
def process_pipeline(raw_data):
    cleaned = clean_data(raw_data)
    transformed = transform_data(cleaned)
    
    # BISECT: Check intermediate state
    print(f"DEBUG after transform: {transformed[:3]}")
    # If correct here → bug is in aggregate or format
    # If wrong here → bug is in clean or transform
    
    aggregated = aggregate_data(transformed)
    formatted = format_output(aggregated)
    return formatted
```

## Git Bisect

Find the exact commit that introduced a bug. Git automates the binary search across commit history.

### Manual Git Bisect

```bash
# Start bisect session
git bisect start

# Mark current commit as bad (has the bug)
git bisect bad

# Mark a known good commit (before the bug existed)
git bisect good abc123

# Git checks out a commit in the middle — test it
# Then tell git the result:
git bisect good    # if this commit works
git bisect bad     # if this commit has the bug

# Repeat until git identifies the first bad commit
# When done:
git bisect reset
```

### Automated Git Bisect

```bash
# Provide a test script — git runs it automatically
git bisect start HEAD abc123
git bisect run npm test
# or
git bisect run python -m pytest tests/test_discount.py
# or
git bisect run php artisan test --filter=DiscountTest

# Git automatically finds the first failing commit
```

### Tips

- **Small, atomic commits make bisect powerful** — If each commit does one thing, the bad commit immediately reveals the cause
- **Large commits require further bisection** — Bisect the changes within that commit using code bisection
- **Flaky tests ruin bisect** — Ensure your test is deterministic before running bisect
- **Stash or commit first** — `git bisect` checks out different commits, so save your work

## When NOT to Use

- **The error message already tells you the location** — Read the error first
- **Only one recent change** — Just review that change directly
- **Non-deterministic bugs** — Bisect requires consistent reproduction; use logging instead
