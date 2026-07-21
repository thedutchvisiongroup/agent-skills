# Performance Review

Read this during Phase 5 (Design and Maintainability). Performance review by reading code has narrow legitimate scope: flag *clear algorithmic problems*, demand *evidence* for everything else.

## Contents

- Review Stance
- Clear Patterns to Flag
- Concurrency-Adjacent Signals
- Evidence Rules
- When NOT to Flag
- Review Checklist

## Review Stance

- **Correctness first.** Never trade readable, correct code for speculative speed.
- **Flag the obvious, by reading.** N+1 queries and quadratic loops are visible without a profiler.
- **Demand evidence for the rest.** "This will be slow" without data-volume reasoning or measurement is not a review finding — it's a guess. Ask for benchmarks instead of asserting.
- **Reject premature optimization in both directions:** don't demand micro-optimizations without a measured need, and flag readability sacrifices made for unmeasured performance.

## Clear Patterns to Flag

**N+1 queries** — a database/API call inside a loop over results:
```python
# FLAG: one query per user
users = User.all()
for user in users:
    user.orders = Order.filter(user_id=user.id)  # N extra queries

# RECOMMEND: batch/prefetch
users = User.all().prefetch("orders")
```

**Hidden O(n²)** — linear search inside a loop:
```javascript
// FLAG: includes() inside a loop over the same data
const missing = candidates.filter(c => !existing.includes(c));

// RECOMMEND: constant-time lookup
const existingSet = new Set(existing);
const missing = candidates.filter(c => !existingSet.has(c));
```

**Repeated I/O in loops** — file, network, or database call per item when a batch operation exists.

**Unbounded result sets** — queries without pagination/limit feeding user-facing responses or memory.

**Unbounded growth** — caches or maps with no eviction, accumulators on long-lived objects, listeners that are added but never removed.

**Redundant recomputation** — loop-invariant values computed inside the loop; the same expensive call made repeatedly (recommend hoisting or memoization where appropriate).

**Sequential independent awaits:**
```javascript
// FLAG: independent calls serialized
const user = await fetchUser();
const orders = await fetchOrders();

// RECOMMEND: run concurrently when independent
const [user, orders] = await Promise.all([fetchUser(), fetchOrders()]);
```

**Blocking I/O on async hot paths** — synchronous file/network calls inside an event loop or request handler.

**String concatenation in tight loops** — language-dependent (immutable-string languages); recommend the idiomatic builder/join.

## Concurrency-Adjacent Signals

- Long critical sections; locks held across I/O calls (turns parallel work serial and invites contention)
- For the *correctness* side of concurrency (races, deadlocks), see `logic-patterns.md` — this file covers only the throughput impact.

## Evidence Rules

- **New hot path or algorithmic choice under real data volume** → ask for a benchmark or a complexity analysis. Missing evidence on a plausible hot path is a legitimate `question`.
- **Big-O reasoning is required** whenever input size can grow unboundedly ("how many items can this list hold in production?").
- **Database indexes:** if a new query filters/sorts on an unindexed column, raise it as a `question` with the query pattern as evidence. Do NOT demand speculative indexes — unused indexes tax every write.
- **Caching:** recommend caching only where the read pattern clearly dominates and invalidation is simple. Speculative caching imports invalidation complexity for nothing.

## When NOT to Flag

- **Micro-optimizations without profile evidence** — loop unrolling, bitwise tricks, allocation golf. Style-level perf nits are noise.
- **Cold paths** — startup code, admin scripts, one-off migrations with acceptable absolute runtimes
- **Readability sacrifices for unmeasured performance** — recommend AGAINST these; ask for the measurement
- **Speculative infrastructure** — connection pools, caches, queues for load that doesn't exist (cross-ref YAGNI in `design-principles.md`)

## Review Checklist

- [ ] No queries or external calls inside loops (N+1 check)
- [ ] No linear searches nested in loops (O(n²) check)
- [ ] Batch alternatives used where they exist
- [ ] Result sets bounded (pagination/limits)
- [ ] No unbounded growth (caches, accumulators, listeners)
- [ ] Loop invariants hoisted; expensive calls not repeated
- [ ] Independent awaits concurrent where safe
- [ ] No blocking I/O on async hot paths
- [ ] Benchmarks requested for plausible hot paths — asserted nowhere without evidence
- [ ] Zero premature-optimization demands; readability sacrifices questioned
