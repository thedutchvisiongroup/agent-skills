# Error Handling Review

Read this during Phase 4 (Logic and Correctness). Poor error handling is the most common source of production incidents — and the least likely to be caught by a green test suite.

## Contents

- Error Swallowing
- Resource Leaks
- Error Propagation
- Retries and Timeouts
- Error Message Quality
- When NOT to Flag
- Review Checklist

## Error Swallowing

**Empty catch blocks:**
```javascript
// WRONG: Error silently ignored
try {
  await riskyOperation();
} catch (e) {
  // Silently swallowed
}

// WRONG: Only logging, not handling
try {
  await riskyOperation();
} catch (e) {
  console.log(e);  // What happens next? State may be inconsistent.
}

// CORRECT: Handle or rethrow with context
try {
  await riskyOperation();
} catch (e) {
  logger.error('Operation failed', { error: e });
  throw new AppError('Operation failed', { cause: e });
}
```

**Ignored promise rejections / unawaited futures:**
```javascript
// WRONG: Unhandled rejection
fetchData();  // No .catch(), no await

// CORRECT: Handle or await
await fetchData();
// Or:
fetchData().catch(handleError);
```

**Catching too broadly:**
```python
# WRONG: Swallows everything, including bugs and interrupts
try:
    process(order)
except Exception:
    pass

# CORRECT: Catch the specific, expected failures
try:
    process(order)
except (ValidationError, TransientStoreError) as e:
    mark_failed(order, reason=str(e))
```

**Review question for every catch block:** what state is the system in after this handler runs, and who knows the failure happened?

## Resource Leaks

**Unclosed resources:**
```python
# WRONG: File not closed on error
def read_file(path):
    f = open(path)
    data = f.read()
    return data  # File never closed if error occurs

# CORRECT: Use context manager
def read_file(path):
    with open(path) as f:
        return f.read()
```

**Connection leaks:**
```javascript
// WRONG: Connection not released on error
async function query(sql) {
  const conn = await pool.getConnection();
  const result = await conn.execute(sql);
  conn.release();
  return result;
}

// CORRECT: Always release
async function query(sql) {
  const conn = await pool.getConnection();
  try {
    return await conn.execute(sql);
  } finally {
    conn.release();
  }
}
```

**Also check for:** open streams, subscriptions and event listeners never removed, timers/intervals never cleared, temp files never deleted, locks never released.

## Error Propagation

**Catch at the right layer:**
- Handle an error only where you can do something meaningful about it (retry, fall back, compensate, or translate it for the caller).
- Otherwise let it propagate. A catch that only rethrows unchanged is noise.

**Preserve cause and context when wrapping:**
```python
# WRONG: Original error lost
except DbError:
    raise OrderError("could not save order")

# CORRECT: Chain the cause, add context
except DbError as e:
    raise OrderError(f"could not save order {order.id}") from e
```

**Don't leak abstractions across layers:**
- A database exception escaping through your API layer couples callers to the storage implementation.
- Translate at module boundaries: storage error → domain error → HTTP/CLI response.

**Match the codebase's error idiom:**
- Exceptions vs. result types vs. sentinel returns — follow the existing convention. Introducing a second idiom in one change is a consistency finding.

**Never use exceptions for normal control flow** — exceptions are for exceptional paths; expected outcomes (e.g. "user not found" in a lookup-by-design) deserve ordinary return values or explicit result types.

## Retries and Timeouts

**Missing timeouts:**
- Every network, IPC, or external-service call needs an explicit timeout. Default timeouts are often infinite.
- A call without a timeout turns a slow dependency into a hung system.

**Unbounded or naive retries:**
```python
# WRONG: Infinite, immediate retries — hammers the failing dependency
while True:
    try:
        return call_api()
    except ApiError:
        pass

# CORRECT: Bounded retries with backoff and jitter
for attempt in range(MAX_RETRIES):
    try:
        return call_api()
    except TransientApiError:
        sleep(backoff_with_jitter(attempt))
raise ApiUnavailableError("api still failing after retries")
```

**Retry only what's retryable:**
- Transient errors (timeouts, 502/503, connection resets) may be retried.
- Permanent errors (validation, auth failures, 4xx) must not be retried.
- Retried operations must be idempotent, or retries must use idempotency keys — otherwise retries duplicate side effects (double charges, duplicate records).

**Partial failure and cleanup:**
- Multi-step operations that fail midway must roll back or compensate (transactions, sagas, explicit cleanup).
- Ask: "if step 3 of 5 fails, what state is left behind?"

## Error Message Quality

**Actionable and contextual:**
```python
# WRONG: No context
raise ValueError("invalid input")

# CORRECT: What failed, which value, what's expected
raise ValueError(f"invalid 'page_size' {page_size!r}: expected int between 1 and 100")
```

**For logs:**
- Include identifiers (order id, user id, correlation id) that make the failure traceable.
- Prefer structured logging (key-value fields) over interpolated strings.
- User-facing messages should be clear and safe to show; internal details (stack traces, query text, file paths) belong in logs, not in responses.

## When NOT to Flag

- **Documented best-effort paths** — e.g. cache writes or analytics calls deliberately ignored on failure, with a comment saying so. Flag missing intent, not the pattern itself.
- **Framework-managed resources** — connections/sessions managed by the framework's lifecycle don't need manual cleanup.
- **Top-level handlers** — a single catch-all at the process boundary (logging + graceful exit) is correct design, not swallowing.

## Review Checklist

- [ ] Every catch block handles, translates, or rethrows — never silently swallows
- [ ] No overly broad catches hiding bugs
- [ ] All resources released on every path (success AND error)
- [ ] Errors propagate to a layer that can act on them
- [ ] Wrapped errors preserve cause and add context
- [ ] Error idiom consistent with the codebase
- [ ] All external calls have timeouts
- [ ] Retries are bounded, backoffed, jittered, and only on retryable, idempotent operations
- [ ] Partial failures leave no inconsistent state
- [ ] Error messages are actionable and traceable
