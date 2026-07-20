---
name: writing-okf
description: Creates, validates, and manages Open Knowledge Format (OKF) documents — markdown files with YAML frontmatter that represent structured knowledge about data, systems, and processes. Use when the user needs to document system components, data assets, APIs, metrics, playbooks, or any knowledge that should be machine-readable and agent-friendly. Covers bundle structure, cross-linking, index files, and conformance with the OKF specification.
---

# Writing Open Knowledge Format (OKF) Documents

## Process

### Phase 1: Discover Bundle Location (REQUIRED)

Determine WHERE the OKF bundle lives or should be created.

1. **Search for existing OKF bundles** by looking for:
   - `index.md` files that contain directory listings
   - Markdown files with YAML frontmatter containing a `type` field
   - Directories named `knowledge/`, `docs/`, `catalog/`, or `bundle/`

2. **If a bundle exists:**
   - Use that directory structure
   - Follow the existing organization pattern
   - Proceed to Phase 2

3. **If no bundle found — infer the logical location:**
   - Look at what the knowledge documents (data, system, process)
   - If documenting a service's internals, place in `services/<name>/docs/`
   - If documenting project-wide knowledge, use `docs/knowledge/` or `knowledge/`
   - If documenting data assets, use `docs/data/` or `catalog/`
   - Create the directory and an `index.md`
   - Proceed to Phase 2

### Phase 2: Gather Context (REQUIRED)

Gather context from available sources BEFORE drafting.

**Gather from these sources first:**

1. **Code context** — Read the code, configs, and schemas being documented
2. **Git history** — Check recent commits for context on changes
3. **Existing OKF documents** — Check for related concepts already documented
4. **Session summaries** — Check for relevant session context

**Then assess what you know vs. what's missing:**

| Field | Source | Ask? |
|-------|--------|------|
| `type` | Inferred from what's being documented | Only if ambiguous |
| `title` | From the asset/concept name | No |
| `description` | From code/comments/context | Only if unclear |
| `tags` | From domain/technology context | No |
| `timestamp` | Current time or last meaningful change | No |
| Body content | Code, schemas, configs, documentation | Only if rationale is missing |

**When to ask the user:**

- Multiple valid interpretations of what to document exist → ask to disambiguate
- The purpose of the document is unclear → ask for clarification
- Technical details are not evident from code → ask for specifics

```
STOP. Before drafting, verify:
- [ ] I know what concept/asset this document describes
- [ ] I gathered context from code and existing docs
- [ ] I know the appropriate `type` value
- [ ] I have enough information to write the body (or I asked)
If any box is unchecked: gather the missing information first.
```

### Phase 3: Write the OKF Document

Every OKF document has two parts: YAML frontmatter and markdown body.

#### YAML Frontmatter (REQUIRED)

```yaml
---
type: <Concept Type>
title: "<display name>"
description: "<one-line summary>"
tags: [<tag>, <tag>, ...]
timestamp: <ISO 8601 datetime>
---
```

**Required field:**
- `type` — A short string identifying the kind of concept. Examples:
  - `BigQuery Table`, `BigQuery Dataset`
  - `API Endpoint`, `Service`
  - `Metric`, `Playbook`, `Reference`
  - `ADR` (for architecture decision records)
  - Any descriptive string — consumers MUST tolerate unknown types

**Recommended fields:**
- `title` — Human-readable display name
- `description` — Single sentence summarizing the concept
- `tags` — YAML list of short strings for categorization
- `timestamp` — ISO 8601 datetime of last meaningful change
- `resource` — URI that uniquely identifies the underlying asset (if applicable)

**Extensions:** Additional keys MAY be included. Consumers MUST preserve unknown keys.

#### Markdown Body (REQUIRED)

The body is standard markdown. Use structural markdown — headings, lists, tables, fenced code blocks — over freeform prose.

**Conventional section headings** (use when applicable):

| Heading | Purpose |
|---------|---------|
| `# Schema` | Structured description of columns/fields |
| `# Examples` | Concrete usage examples, often as fenced code blocks |
| `# Citations` | External sources backing claims in the body |

The body SHOULD include:
- A top-level heading (`#`) describing the concept
- Sections that explain the concept's structure, usage, and relationships
- Cross-links to related concepts where relevant

#### Cross-linking

Link to other concepts using standard markdown links:

- **Bundle-relative (recommended):** `[customers table](/tables/customers.md)`
- **Relative:** `[other concept](./other.md)`

A link asserts a relationship. The specific kind is conveyed by surrounding prose.

#### File Naming

- Use lowercase with hyphens: `concept-name.md`
- Exception: reserved filenames `index.md` and `log.md`

### Phase 4: Validate

After writing, run the validation script:

```bash
python3 <skill-dir>/scripts/validate_okf.py <path-to-file>
```

Fix any errors reported by the script. A valid OKF document MUST pass all checks.

## Reserved Files

| Filename | Purpose |
|----------|---------|
| `index.md` | Directory listing for progressive disclosure |
| `log.md` | Chronological history of updates |

These filenames MUST NOT be used for concept documents.

### Index Files

An `index.md` enumerates a directory's contents. Contains no frontmatter. Uses sections with headings:

```markdown
# Section / Group Heading

* [Title 1](relative-url-1) - short description of item 1
* [Title 2](relative-url-2) - short description of item 2
```

### Log Files

A `log.md` records change history. Format: flat list of date-grouped entries, newest first:

```markdown
# Directory Update Log

## 2026-07-20
* **Creation**: Established the [Service Overview](service-overview.md).

## 2026-07-15
* **Initialization**: Created foundational directory structure.
```

Date headings MUST use ISO 8601 `YYYY-MM-DD` form.

## Bundle Structure

A bundle is a directory tree of markdown files:

```
bundle/
├── index.md                      # Directory listing
├── log.md                        # Update history (optional)
├── <concept>.md                  # Concept at bundle root
└── <subdirectory>/               # Subdirectories organize concepts
    ├── index.md
    ├── <concept>.md
    └── <subdirectory>/
        └── …
```

## Conformance

An OKF document is conformant if:
1. The file contains valid YAML frontmatter delimited by `---`
2. The frontmatter contains a non-empty `type` field
3. The file is UTF-8 encoded
4. The file is valid markdown

Consumers MUST NOT reject a document because of:
- Missing optional frontmatter fields
- Unknown `type` values
- Unknown additional frontmatter keys
- Broken cross-links
- Missing `index.md` files

## When NOT to Use This Skill

- For trivial notes or comments — use code comments instead
- For documentation that belongs in a different format (e.g., API specs in OpenAPI)
- For temporary or throwaway documentation

## Quick Reference

| Task | Action |
|------|--------|
| Find existing bundles | Search for `index.md` files with directory listings |
| Create a concept | Write markdown with YAML frontmatter containing `type` |
| Link to other concepts | Use bundle-relative paths: `[name](/path/to/file.md)` |
| Create directory listing | Add `index.md` with bullet list of contents |
| Log changes | Add `log.md` with date-grouped entries |
| Validate | Run `validate_okf.py` on the file |

Base directory for this skill: /home/abej/proj/agent-skills/skills/writing-okf
Relative paths in this skill (e.g., scripts/, references/) are relative to this base directory.
