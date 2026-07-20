# OKF Conformance for ADRs

## What is OKF?

Open Knowledge Format (OKF) is a minimal, human- and agent-friendly format for
representing knowledge as markdown files with YAML frontmatter. It standardizes
the small set of structural conventions needed for self-describing knowledge
documents.

Source: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

## OKF Requirements Applied to ADRs

An ADR is an OKF **concept document**. It MUST satisfy these conformance rules:

### 1. Frontmatter (Section 4.1)

Every ADR file MUST start with a YAML frontmatter block delimited by `---`:

```yaml
---
type: ADR
title: "<display name>"
description: "<one-line summary>"
tags: [<tag>, <tag>]
deciders: [<person>, <person>]
timestamp: <ISO 8601 datetime>
---
```

**Required fields:**
- `type` — MUST be `ADR`. This is the OKF concept type that enables routing,
  filtering, and presentation by consumers.
- `title` — Human-readable display name. MUST match the H1 heading.
- `description` — Single sentence summarizing the ADR.
- `tags` — YAML list of short strings for categorization.
- `deciders` — YAML list of people involved in making the decision.
- `timestamp` — ISO 8601 datetime of last meaningful change.

**Extensions:** Additional keys MAY be included. Consumers MUST NOT reject
documents with unrecognized fields.

### 2. Body (Section 4.2)

The body is standard markdown after the frontmatter. OKF recommends structural
markdown (headings, lists, tables) over freeform prose.

The ADR body follows the MADR template with these conventional sections defined
by the skill (not by OKF itself).

### 3. Cross-linking (Section 5)

ADRs MAY link to other ADRs or external resources using standard markdown links:

- **Bundle-relative:** `[customers table](/tables/customers.md)` — recommended
- **Relative:** `[other ADR](./0002-other-decision.md)`

### 4. Citations (Section 8)

When an ADR makes claims from external sources, list them under `# Citations`:

```markdown
# Citations

[1] [BigQuery public dataset announcement](https://cloud.google.com/blog/...)
[2] [Internal data quality runbook](https://wiki.acme.internal/data/quality)
```

## OKF Conformance Checklist

An ADR is OKF-conformant if:

1. [x] The file starts with a parseable YAML frontmatter block (`---` delimited)
2. [x] The frontmatter contains `type: ADR`, `title`, `description`, `tags`, `deciders`, and `timestamp`
3. [x] The file is UTF-8 encoded
4. [x] The file is valid markdown
5. [x] All required MADR body sections are present
6. [x] The `Deciders` and `Date` fields are present in the body

Consumers MUST NOT reject an ADR because of:
- Unknown additional frontmatter keys
- Broken cross-links
- Missing citations

## Differences from Generic OKF

| Aspect | Generic OKF | ADR Skill |
|--------|-------------|----------|
| `type` field | Any descriptive string | MUST be `ADR` |
| Body sections | No required sections | MADR sections required |
| Status | Not specified | Must be one of: proposed, accepted, deprecated, superseded |
| File naming | Any `.md` except reserved | `NNNN-kebab-case-title.md` |
| Reserved files | `index.md`, `log.md` | Same, plus ADR-specific `index.md` |