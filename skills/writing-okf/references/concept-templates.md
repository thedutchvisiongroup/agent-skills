# Concept Document Templates

## Generic Concept

```markdown
---
type: <Concept Type>
title: "<Display Name>"
description: "<One-line summary>"
tags: [<domain>, <technology>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---

# <Display Name>

<Overview paragraph explaining what this concept is.>

## Details

<Structured description of the concept. Use tables, lists, or code blocks as appropriate.>

## Relationships

- Related to [other concept](/path/to/other.md) — <description of relationship>
- Part of [parent concept](/path/to/parent.md)

# Citations

[1] <Source URL or reference>
```

## Data Asset (Table/Dataset)

```markdown
---
type: BigQuery Table
title: "<Table Name>"
description: "<One-line summary of what each row represents>"
resource: https://console.cloud.google.com/bigquery?p=<project>&d=<dataset>&t=<table>
tags: [<domain>, <data>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---

# <Table Name>

<Overview of the table's purpose and contents.>

# Schema

| Column        | Type      | Description                  |
|---------------|-----------|------------------------------|
| `id`          | STRING    | Unique identifier.           |
| `created_at`  | TIMESTAMP | When the record was created. |
| `value`       | NUMERIC   | The measured value.          |

# Joins

- Joined with [other table](/tables/other.md) on `id`.

# Citations

[1] [Source documentation](https://example.com/docs)
```

## API Endpoint

```markdown
---
type: API Endpoint
title: "<Endpoint Name>"
description: "<One-line summary>"
resource: https://api.example.com/v1/<path>
tags: [<service>, <api>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---

# <Endpoint Name>

<Overview of what this endpoint does.>

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

# Citations

[1] [API Documentation](https://api.example.com/docs)
```

## Playbook / Runbook

```markdown
---
type: Playbook
title: "<Playbook Name>"
description: "<One-line summary of when this playbook applies>"
tags: [<team>, <incident>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---

# <Playbook Name>

<Overview of when to use this playbook.>

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

# Citations

[1] <Source or documentation link>
```

## Service / Component

```markdown
---
type: Service
title: "<Service Name>"
description: "<One-line summary of what this service does>"
tags: [<team>, <domain>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---

# <Service Name>

<Overview of the service's purpose and responsibilities.>

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

# Citations

[1] [Service documentation](https://wiki.example.com/service)
```
