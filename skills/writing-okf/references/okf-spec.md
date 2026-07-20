# OKF Specification Summary

## What is OKF?

Open Knowledge Format (OKF) is a minimal, human- and agent-friendly format for
representing knowledge as markdown files with YAML frontmatter. It standardizes
the small set of structural conventions needed for self-describing knowledge
documents.

**Source:** https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

**Version:** 0.1 (Draft)

## Core Principles

- **Readable** by humans without tooling
- **Parseable** by agents without bespoke SDKs
- **Diffable** in version control
- **Portable** across tools, organizations, and time

## Terminology

| Term | Definition |
|------|------------|
| **Knowledge Bundle** | A self-contained, hierarchical collection of knowledge documents |
| **Concept** | A single unit of knowledge within a bundle. One markdown file. |
| **Concept ID** | Path of the file within the bundle, with `.md` removed |
| **Frontmatter** | YAML metadata block delimited by `---` |
| **Body** | Everything after the frontmatter |
| **Link** | Standard markdown link from one concept to another |
| **Citation** | Link to an external source that supports a claim |

## Bundle Structure

```
bundle/
├── index.md                      # Directory listing (optional)
├── log.md                        # Update history (optional)
├── <concept>.md                  # Concept at bundle root
└── <subdirectory>/
    ├── index.md
    ├── <concept>.md
    └── <subdirectory>/
        └── …
```

## Reserved Filenames

| Filename | Purpose | Rules |
|----------|---------|-------|
| `index.md` | Directory listing | No frontmatter. Sections with bullet lists. |
| `log.md` | Update history | No frontmatter. Date-grouped entries, newest first. |

## Concept Document Structure

### Frontmatter

```yaml
---
type: <Type name>                  # REQUIRED
title: <Optional display name>     # Recommended
description: <Optional summary>    # Recommended
resource: <Optional canonical URI> # If applicable
tags: [<tag>, <tag>, ...]          # Recommended
timestamp: <ISO 8601 datetime>     # Recommended
---
```

**Required:** `type` — A short string identifying the kind of concept.

**Recommended (in priority order):**
- `title` — Human-readable display name
- `description` — Single sentence summary
- `resource` — URI for the underlying asset
- `tags` — YAML list for categorization
- `timestamp` — ISO 8601 datetime of last change

**Extensions:** Additional keys MAY be included. Consumers MUST preserve unknown keys.

### Body

Standard markdown. SHOULD favor structural markdown (headings, lists, tables, code blocks)
over freeform prose.

Conventional headings:

| Heading | Purpose |
|---------|---------|
| `# Schema` | Structured description of fields/columns |
| `# Examples` | Concrete usage examples |
| `# Citations` | External sources backing claims |

## Cross-linking

### Bundle-relative (recommended)
```markdown
See the [customers table](/tables/customers.md) for the join key.
```

### Relative
```markdown
See the [neighboring concept](./other.md).
```

## Index Files

```markdown
# Section / Group Heading

* [Title 1](relative-url-1) - short description of item 1
* [Title 2](relative-url-2) - short description of item 2

# Another Section

* [Subdirectory](subdir/) - short description of the subdirectory
```

## Log Files

```markdown
# Directory Update Log

## 2026-07-20
* **Update**: Added new reference for [Concept Name](concept.md).
* **Creation**: Established the [Overview](overview.md).

## 2026-07-15
* **Initialization**: Created foundational directory structure.
```

## Conformance

A bundle is OKF-conformant if:
1. Every non-reserved `.md` file has parseable YAML frontmatter
2. Every frontmatter block has a non-empty `type` field
3. Reserved files follow their specified structure

## Permissive Consumption

Consumers MUST NOT reject a bundle because of:
- Missing optional frontmatter fields
- Unknown `type` values
- Unknown additional frontmatter keys
- Broken cross-links
- Missing `index.md` files
