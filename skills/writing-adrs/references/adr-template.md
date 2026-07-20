# ADR Template Reference

## Complete Template

This is the full ADR template combining OKF frontmatter with the MADR body structure.

```markdown
---
type: ADR
title: "<short imperative title>"
description: "<one-line summary of the decision>"
tags: [<domain>, <technology>, <component>]
deciders: [<person>, <person>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---

# <short title of solved problem and solution>

- Status: proposed | accepted | deprecated | superseded by [ADR-NNNN](link)
- Deciders: <list everyone involved in the decision>
- Date: <YYYY-MM-DD>

Technical Story: <description | ticket/issue URL>

## Context and Problem Statement

[Describe the context and problem statement, e.g., in free form using two to three
sentences. You may want to articulate the problem in form of a question.]

## Decision Drivers

- [driver 1, e.g., a force, facing concern, ...]
- [driver 2, e.g., a force, facing concern, ...]
- [driver 3, ...]
- ...

## Considered Options

- [option 1]
- [option 2]
- [option 3]
- ...

## Decision Outcome

Chosen option: "[option 1]", because [justification. e.g., only option, which meets
k.o. criterion decision driver | which resolves force force | ... | comes out best
(see below)].

### Positive Consequences

- [e.g., improvement of quality attribute satisfaction, follow-up decisions required, ...]
- ...

### Negative Consequences

- [e.g., compromising quality attribute, follow-up decisions required, ...]
- ...

## Pros and Cons of the Options

### [option 1]

[example | description | pointer to more information | ...]

- Good, because [argument a]
- Good, because [argument b]
- Bad, because [argument c]
- ...

### [option 2]

[example | description | pointer to more information | ...]

- Good, because [argument a]
- Good, because [argument b]
- Bad, because [argument c]
- ...

### [option 3]

[example | description | pointer to more information | ...]

- Good, because [argument a]
- Good, because [argument b]
- Bad, because [argument c]
- ...

## Links

- [Link type] [Link to ADR or resource]
- ...
```

## Example: Minimal Valid ADR

```markdown
---
type: ADR
title: "Use PostgreSQL for primary database"
description: "Select PostgreSQL as the primary relational database for the application."
tags: [database, postgresql, infrastructure]
deciders: [Alice (Tech Lead), Bob (DBA)]
timestamp: 2026-07-20T10:00:00Z
---

# Use PostgreSQL for primary database

- Status: proposed
- Deciders: Alice (Tech Lead), Bob (DBA)
- Date: 2026-07-20

Technical Story: We need a reliable relational database for our new application.

## Context and Problem Statement

We are starting a new application that requires a relational database for structured
data with ACID guarantees. Which database should we use?

## Decision Drivers

- Must support ACID transactions
- Team familiarity and expertise
- Cost (prefer open-source)
- Performance at expected scale

## Considered Options

- PostgreSQL
- MySQL
- SQLite

## Decision Outcome

Chosen option: "PostgreSQL", because it best meets our requirements for ACID compliance,
has strong team expertise, and is open-source with excellent community support.

### Positive Consequences

- Strong ACID compliance and data integrity
- Rich feature set (JSON support, full-text search)
- Large community and ecosystem

### Negative Consequences

- Requires dedicated database server (unlike SQLite)
- Team needs to learn PostgreSQL-specific features

## Pros and Cons of the Options

### PostgreSQL

Full-featured open-source relational database.

- Good, because excellent ACID compliance
- Good, because JSON and full-text search built-in
- Good, because team has production experience
- Bad, because requires dedicated server

### MySQL

Popular open-source relational database.

- Good, because widely used and well-documented
- Bad, because historically weaker ACID guarantees (pre-InnoDB)
- Bad, because less feature-rich than PostgreSQL

### SQLite

Embedded relational database.

- Good, because zero configuration required
- Good, because excellent for development/testing
- Bad, because not suitable for concurrent write workloads
- Bad, because no network access

## Links

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [ADR-0001: Database Selection Criteria](0001-database-selection-criteria.md)
```