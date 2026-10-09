# Concept Document Templates

These templates are starting points, not mandatory structures. `type` values are
not registered anywhere: pick descriptive, self-explanatory values, reuse `type`
values already present in the bundle, and adapt the sections to the concept at hand.

All templates use the OKF v0.2 provenance and lifecycle families: `generated`
(with the house actor convention) and `status` are house-required, and claims
are backed by `sources` frontmatter entries via `[^id]` footnotes. The Generic
Concept template shows `status: draft` (it is a fill-in scaffold, work in
progress until completed); the others show `status: stable`.

## Generic Concept

```markdown
---
type: <Concept Type>
title: "<Display Name>"
description: "<One-line summary>"
tags: [<domain>, <technology>]
generated: { by: <harness>/<model-id>, at: <ISO 8601> }
status: draft
sources:
  - id: primary-source
    resource: <Source URL or reference>
    title: "<Source title>"
---

# <Display Name>

<Overview paragraph explaining what this concept is.>[^primary-source]

## Details

<Structured description of the concept. Use tables, lists, or code blocks as appropriate.>

## Relationships

- Related to [other concept](/path/to/other.md) — <description of relationship>
- Part of [parent concept](/path/to/parent.md)

[^primary-source]: <Source title>
```

## Data Asset (Table/Dataset)

```markdown
---
type: Table
title: "<Table Name>"
description: "<One-line summary of what each row represents>"
resource: <URI of the asset, e.g. a database or catalog URL>
tags: [<domain>, <data>]
generated: { by: <harness>/<model-id>, at: <ISO 8601> }
status: stable
sources:
  - id: source-docs
    resource: https://example.com/docs
    title: "Source documentation"
---

# <Table Name>

<Overview of the table's purpose and contents.>[^source-docs]

# Schema

| Column        | Type      | Description                  |
|---------------|-----------|------------------------------|
| `id`          | STRING    | Unique identifier.           |
| `created_at`  | TIMESTAMP | When the record was created. |
| `value`       | DECIMAL   | The measured value.          |

# Joins

- Joined with [other table](/tables/other.md) on `id`.

[^source-docs]: Source documentation
```

## API Endpoint

```markdown
---
type: API Endpoint
title: "<Endpoint Name>"
description: "<One-line summary>"
resource: https://api.example.com/v1/<path>
tags: [<service>, <api>]
generated: { by: <harness>/<model-id>, at: <ISO 8601> }
status: stable
sources:
  - id: api-docs
    resource: https://api.example.com/docs
    title: "API Documentation"
---

# <Endpoint Name>

<Overview of what this endpoint does.>[^api-docs]

## Request

### Method

`GET` / `POST` / `PUT` / `DELETE`

### Path Parameters

| Parameter | Type   | Description            |
|-----------|--------|------------------------|
| `id`      | string | The resource identifier|

### Query Parameters

| Parameter | Type    | Default | Description        |
|-----------|---------|---------|-------------------|
| `limit`   | integer | 10      | Max results to return|

### Request Body

```json
{
  "field": "value"
}
```

## Response

### Success (200)

```json
{
  "id": "123",
  "name": "Example"
}
```

### Errors

| Code | Description           |
|------|-----------------------|
| 404  | Resource not found    |
| 500  | Internal server error |

[^api-docs]: API Documentation
```

## Playbook / Runbook

```markdown
---
type: Playbook
title: "<Playbook Name>"
description: "<One-line summary of when this playbook applies>"
tags: [<team>, <incident>]
generated: { by: <harness>/<model-id>, at: <ISO 8601> }
status: stable
sources:
  - id: source-docs
    resource: <Source or documentation link>
    title: "<Source title>"
---

# <Playbook Name>

<Overview of when to use this playbook.>[^source-docs]

# Trigger

<Describe the condition or alert that triggers this playbook.>

# Steps

1. <First step — what to do>
2. <Second step — what to do>
3. <Third step — what to do>

# Escalation

<When and how to escalate.>

# Related

- [Monitoring dashboard](https://example.com/dash)
- [Related playbook](/playbooks/related.md)

[^source-docs]: <Source title>
```

## Service / Component

```markdown
---
type: Service
title: "<Service Name>"
description: "<One-line summary of what this service does>"
tags: [<team>, <domain>]
generated: { by: <harness>/<model-id>, at: <ISO 8601> }
status: stable
sources:
  - id: service-docs
    resource: https://wiki.example.com/service
    title: "Service documentation"
---

# <Service Name>

<Overview of the service's purpose and responsibilities.>[^service-docs]

## Architecture

<Describe the service's architecture, dependencies, and deployment.>

## APIs

- [Endpoint 1](/apis/service/endpoint1.md) — <description>
- [Endpoint 2](/apis/service/endpoint2.md) — <description>

## Data

- [Table 1](/tables/service/table1.md) — <description>

## Configuration

| Variable        | Description              | Default  |
|-----------------|--------------------------|----------|
| `SERVICE_PORT`  | Port to listen on        | 8080     |
| `LOG_LEVEL`     | Logging verbosity        | info     |

## Runbooks

- [Incident response](/playbooks/service-incident.md)

[^service-docs]: Service documentation
```
