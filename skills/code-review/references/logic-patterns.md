# Common Logic Error Patterns

Read this during Phase 4 (Logic and Correctness). For error swallowing, resource leaks, retries, and error propagation, see `error-handling.md`.

## Contents

- Off-by-One Errors
- Null/Undefined Handling
- Boolean Logic Errors
- Race Conditions
- Type Coercion Issues
- String/Array Boundary Issues
- Floating Point Issues
- Review Checklist

## Off-by-One Errors

**Loop bounds:**
```python
# WRONG: Skips last element
for i in range(len(arr) - 1):
    process(arr[i])

# CORRECT: Processes all elements
for i in range(len(arr)):
    process(arr[i])

# CORRECT: If you need pairs
for i in range(len(arr) - 1):
    process(arr[i], arr[i + 1])
```

**Array slicing:**
```javascript
// WRONG: Off by one
const lastThree = arr.slice(-3, -1);  // Misses last element

// CORRECT
const lastThree = arr.slice(-3);  // Gets last 3 elements
```

**Range checks:**
```python
# WRONG: Excludes boundary
if 0 < x < 100:  # Misses 0 and 100

# CORRECT: If boundaries are valid
if 0 <= x <= 100:
```

## Null/Undefined Handling

**Missing null checks:**
```javascript
// WRONG: Throws if user is null
const name = user.name.toUpperCase();

// CORRECT: Null-safe
const name = user?.name?.toUpperCase() ?? '';
```

**Optional chaining:**
```python
# WRONG: AttributeError if config is None
timeout = config.get('timeout', 30)

# CORRECT: Safe access
timeout = config.get('timeout', 30) if config else 30
```

**Null vs undefined:**
```javascript
// WRONG: Doesn't catch undefined
if (value === null) { ... }

// CORRECT: Catches both
if (value == null) { ... }
// Or explicit:
if (value === null || value === undefined) { ... }
```

## Boolean Logic Errors

**De Morgan's Law violations:**
```python
# WRONG: !(A && B) is NOT the same as !A && !B
if not (is_admin and is_active):  # This is: (not is_admin) or (not is_active)

# WRONG: Trying to negate both conditions
if not is_admin and not is_active:  # This is: !(A || B)

# CORRECT: If you want "not both"
if not (is_admin and is_active):
```

**Inverted conditions:**
```javascript
// WRONG: Logic is inverted
if (!isEmpty) {
  return;  // Returns when NOT empty
}
processEmpty();  // Processes when empty - probably wrong

// CORRECT: Clear intent
if (isEmpty) {
  processEmpty();
  return;
}
```

**Complex boolean expressions:**
```python
# WRONG: Hard to understand
if (a and b or c) and not (d or e): ...

# CORRECT: Break it down
is_valid = a and b or c
is_excluded = d or e
if is_valid and not is_excluded: ...
```

## Race Conditions

**Shared mutable state:**
```javascript
// WRONG: Race condition
let counter = 0;
async function increment() {
  const current = counter;  // Another call might change this
  await delay(10);
  counter = current + 1;    // Lost update
}

// CORRECT: Use atomic operations
let counter = 0;
async function increment() {
  counter += 1;  // Atomic
}
```

**Async ordering:**
```python
# WRONG: Race condition
async def process():
    result = await fetch_data()  # Takes time
    await save(result)           # Another call might overwrite

# CORRECT: Use locks or queues
import asyncio

lock = asyncio.Lock()

async def process():
    async with lock:
        result = await fetch_data()
        await save(result)
```

**Check-then-act:**
```python
# WRONG: TOCTOU race — file may vanish between check and use
if os.path.exists(path):
    data = open(path).read()

# CORRECT: Act and handle the error
try:
    data = open(path).read()
except FileNotFoundError:
    data = None
```

## Type Coercion Issues

**JavaScript type coercion:**
```javascript
// WRONG: String concatenation instead of addition
const total = "5" + 3;  // "53", not 8

// CORRECT: Explicit conversion
const total = Number("5") + 3;  // 8

// WRONG: Truthy/falsy issues
if ("0") { ... }  // Truthy! Non-empty string

// CORRECT: Explicit check
if (value !== "0") { ... }
```

**Python type issues:**
```python
# WRONG: Mutable default argument
def append_to(item, target=[]):
    target.append(item)
    return target  # Shared across calls!

# CORRECT: Use None sentinel
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

## String/Array Boundary Issues

**Empty string/array:**
```python
# WRONG: IndexError on empty list
first = items[0]

# CORRECT: Check first
first = items[0] if items else None

# WRONG: Slicing returns empty, not error
result = items[10:20]  # Might be empty
if result:  # This check works
    process(result)
```

**String encoding:**
```python
# WRONG: Assumes ASCII
length = len(string)  # Not byte length

# CORRECT: For byte length
byte_length = len(string.encode('utf-8'))
```

## Floating Point Issues

**Exact comparison:**
```python
# WRONG: Floating point precision
if total == 0.3:  # Might not be exact

# CORRECT: Use tolerance
if abs(total - 0.3) < 1e-9:

# CORRECT: Use Decimal for money
from decimal import Decimal
total = Decimal('0.3')
```

## Review Checklist

For each logic pattern, verify:

- [ ] Off-by-one: Loop bounds, slices, and ranges correct?
- [ ] Null: All nullable values handled?
- [ ] Boolean: Logic is correct and readable? De Morgan respected?
- [ ] Race: No shared mutable state or check-then-act issues?
- [ ] Types: No type coercion surprises? No mutable defaults?
- [ ] Boundaries: Empty inputs handled?
- [ ] Floats: No exact comparisons? Decimal for money?
- [ ] Errors: See `error-handling.md` — swallowing, leaks, propagation, retries
