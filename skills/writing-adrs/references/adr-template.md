# ADR Template Reference

## Contents

- [Complete Template](#complete-template) — fully annotated OKF + MADR 4.0 template
- [Example: Minimal Valid ADR](#example-minimal-valid-adr) — only the required sections
- [Example: Rejected ADR](#example-rejected-adr) — an explicitly declined proposal
- [Example: Supersede Pair](#example-supersede-pair) — old ADR + its replacement

## Complete Template

OKF frontmatter carries all metadata; the MADR 4.0 body carries the decision narrative. Optional elements are marked — remove them when they add no value, but keep the required ones.

```markdown
---
type: ADR
title: "<short imperative title>"
description: "<one-line summary of the decision>"
tags: [<domain>, <technology>, <component>]
deciders: [<person>, <person>]
status: proposed | rejected | accepted | deprecated | superseded
timestamp: <YYYY-MM-DDTHH:MM:SSZ>   # last meaningful change
# Required when status is superseded:
# superseded_by: <relative path to the superseding ADR>
# Optional MADR fields:
# consulted: [<subject-matter experts, two-way communication>]
# informed: [<people kept up-to-date, one-way communication>]
---

# <short title, representative of solved problem and found solution>

## Context and Problem Statement

[REQUIRED. Two to three sentences, or an illustrative story. You may articulate
the problem as a question and link to issue trackers or boards.]

## Decision Drivers

[Optional. Remove if none.]

- [driver 1, e.g., a force, facing concern]
- [driver 2]

## Considered Options

[REQUIRED.]

- [option 1]
- [option 2]
- [option 3]

## Decision Outcome

[REQUIRED.] Chosen option: "[option 1]", because [justification — only the
decisive factors, not a repeat of the full pros/cons below].

### Consequences

[Optional.]

- Good, because [positive consequence]
- Bad, because [negative consequence]
- Neutral, because [consequence that is neither clearly good nor bad]

### Confirmation

[Optional, but valuable: describe how implementation of/compliance with this
ADR will be confirmed — e.g., a design/code review, an ArchUnit test, a lint
rule, a checklist item in CI.]

## Pros and Cons of the Options

[Optional, but recommended for contested decisions.]

### [option 1]

[example | description | pointer to more information]

- Good, because [argument a]
- Bad, because [argument b]
- Neutral, because [argument c]

### [option 2]

- Good, because [argument a]
- Bad, because [argument b]

## More Information

[Optional. Additional evidence, team-agreement notes, when/how to realize or
revisit the decision, links to other ADRs and resources. When this ADR
supersedes another, state: Supersedes [ADR-NNNN](relative/path.md).]
```

## Example: Minimal Valid ADR

Only the required frontmatter fields and the three required body sections. This is the floor, not the target.

`0002-use-redis-for-session-cache.md`:

```markdown
---
type: ADR
title: "Use Redis for session cache"
description: "Select Redis as the session cache for the web application."
tags: [cache, redis, infrastructure]
deciders: [Alice (Tech Lead), Bob (Backend)]
status: accepted
timestamp: 2026-07-20T10:00:00Z
---

# Use Redis for session cache

## Context and Problem Statement

Our web application needs shared session storage across multiple instances.
Which store should hold session data?

## Considered Options

- Redis
- Memcached
- Database-backed sessions

## Decision Outcome

Chosen option: "Redis", because the team already operates it for queues and it
supports expiring keys natively.
```

## Example: Rejected ADR

Rejected ADRs are valuable history: they record that an option was seriously considered and declined, so future teams don't re-litigate it.

`0003-use-sqlite-for-primary-storage.md`:

```markdown
---
type: ADR
title: "Use SQLite for primary storage"
description: "Proposal to use SQLite as the primary application database."
tags: [database, sqlite, infrastructure]
deciders: [Alice (Tech Lead), Carol (Architect)]
status: rejected
timestamp: 2026-07-19T14:30:00Z
---

# Use SQLite for primary storage

## Context and Problem Statement

Our deployment footprint should stay small and self-contained. Could SQLite
serve as the primary database instead of running a separate server?

## Decision Drivers

- Minimal operational footprint
- Expected concurrent write load (~50 requests/s)
- Multi-instance deployment planned for Q4

## Considered Options

- SQLite
- PostgreSQL (incumbent)

## Decision Outcome

Chosen option: rejected the proposal, because SQLite cannot sustain concurrent
writes from multiple application instances, which the Q4 scale-out requires.

### Consequences

- Good, because the rejection and its rationale are recorded for the next time
  this idea resurfaces
- Bad, because we keep the operational cost of a database server
```

## Example: Supersede Pair

Superseding keeps both ADRs forever, linked in both directions.

Old ADR, `0001-use-mysql-for-primary-database.md`:

```markdown
---
type: ADR
title: "Use MySQL for primary database"
description: "Select MySQL as the primary relational database."
tags: [database, mysql, infrastructure]
deciders: [Alice (Tech Lead)]
status: superseded
superseded_by: ./0004-use-postgresql-for-primary-database.md
timestamp: 2026-07-21T09:00:00Z
---

# Use MySQL for primary database

## Context and Problem Statement

We need a relational database for the new application. (Superseded — see
[ADR-0004](0004-use-postgresql-for-primary-database.md) for the current
decision.)

## Considered Options

- MySQL
- PostgreSQL

## Decision Outcome

Chosen option: "MySQL", because of existing hosting contracts at the time.
```

New ADR, `0004-use-postgresql-for-primary-database.md`:

```markdown
---
type: ADR
title: "Use PostgreSQL for primary database"
description: "Replace MySQL with PostgreSQL as the primary relational database."
tags: [database, postgresql, infrastructure]
deciders: [Alice (Tech Lead), Bob (DBA)]
status: accepted
timestamp: 2026-07-21T09:00:00Z
---

# Use PostgreSQL for primary database

## Context and Problem Statement

The MySQL hosting contract ends this year and our JSON-heavy workloads need
better native support. Should we renew MySQL or migrate?

## Decision Drivers

- JSON query performance and indexing
- Team expertise across both engines
- Migration cost within the contract window

## Considered Options

- PostgreSQL
- MySQL (renew)

## Decision Outcome

Chosen option: "PostgreSQL", because its JSONB indexing meets the workload
requirements and the contract window makes migration cost acceptable.

### Consequences

- Good, because JSON queries no longer need application-side workarounds
- Good, because we standardize on one engine with the analytics team
- Bad, because a data migration and rollback plan are required

### Confirmation

Migration runbook reviewed by DBA; cutover checklist added to release
pipeline; first month monitored via replication lag and error-rate dashboards.

## Pros and Cons of the Options

### PostgreSQL

- Good, because JSONB indexing fits the workload
- Good, because strong ACID guarantees
- Bad, because team has less production experience with it

### MySQL (renew)

- Good, because zero migration effort
- Bad, because weak JSON support keeps workarounds alive
- Neutral, because hosting cost is comparable

## More Information

Supersedes [ADR-0001](0001-use-mysql-for-primary-database.md). Migration
runbook: see internal wiki. Decision to be revisited if migration slips past
Q4.
```
