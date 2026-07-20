---
name: writing-adrs
description: Creates, validates, and manages Architecture Decision Records (ADRs) using the MADR template with OKF-compliant YAML frontmatter. Use when the user needs to document an architectural decision, create a new ADR, review existing ADRs, validate ADR structure, or establish an ADR directory in a project. Covers discovery of existing ADR locations, ADR lifecycle management (proposed/accepted/deprecated/superseded), and ensures conformance with Open Knowledge Format (OKF) frontmatter requirements.
---

# Writing Architecture Decision Records (ADRs)

## Iron Law

**You MUST ask clarifying questions before writing any ADR.**

## Process

### Phase 1: Discover ADR Location (REQUIRED)

Before writing anything, determine WHERE ADRs live in this project.

1. **Search for existing ADRs** using these patterns:
   - `**/adr/**/*.md`, `**/adrs/**/*.md`, `**/decisions/**/*.md`
   - `**/docs/adr/**/*.md`, `**/docs/architecture/**/*.md`
   - Files matching `NNNN-*.md` in any directory

2. **If ADRs exist:**
   - Confirm the directory with the user
   - Determine the next sequence number from existing files
   - Proceed to Phase 2

3. **If no ADRs found:**
   - ASK the user where to create the ADR directory
   - Suggest common locations: `docs/adr/`, `adr/`, `decisions/`
   - Create the directory and an `index.md` after user confirms
   - Proceed to Phase 2

```
STOP. Have you checked for existing ADRs?
- [ ] Yes, I searched for existing ADR files
- [ ] Yes, I confirmed the directory with the user (or asked where to create it)
- [ ] Yes, I know the next sequence number
If any box is unchecked: GO BACK.
```

### Phase 2: Clarify the Decision (REQUIRED)

Before drafting, gather the decision context. Ask the user:

1. **What is the decision?** — One sentence describing the architectural choice
2. **What is the context?** — Why does this decision need to be made now?
3. **What options exist?** — At minimum, 2 alternatives (including "do nothing")
4. **Who are the deciders?** — Who was involved in making this decision?
5. **What is the status?** — `proposed` (default), or another valid status?

```
STOP. Have you clarified the decision?
- [ ] Yes, I know what decision is being made
- [ ] Yes, I know the context and problem
- [ ] Yes, I know at least 2 options
- [ ] Yes, I know the deciders
If any box is unchecked: GO BACK.
```

### Phase 3: Write the ADR

Use this exact structure. Every ADR has two parts: OKF frontmatter and MADR body.

#### OKF Frontmatter (REQUIRED)

```yaml
---
type: ADR
title: "<short imperative title>"
description: "<one-line summary>"
tags: [<relevant>, <tags>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

- `type` MUST be `ADR`
- `title` MUST match the markdown H1 heading
- `description` MUST be a single sentence
- `tags` MUST be a YAML list of relevant tags
- `timestamp` MUST be ISO 8601 of last meaningful change

#### MADR Body (REQUIRED sections)

```markdown
# <short title of solved problem and solution>

- Status: <proposed | accepted | deprecated | superseded by [ADR-NNNN](link)>
- Deciders: <list everyone involved>
- Date: <YYYY-MM-DD>

Technical Story: <description | ticket/issue URL>

## Context and Problem Statement

<2-3 sentences describing context and problem. May be phrased as a question.>

## Decision Drivers

- <driver 1, e.g., a force, facing concern>
- <driver 2>
- ...

## Considered Options

- <option 1>
- <option 2>
- ...

## Decision Outcome

Chosen option: "<option>", because <justification>.

### Positive Consequences

- <e.g., improvement of quality attribute>

### Negative Consequences

- <e.g., compromising quality attribute, follow-up decisions required>

## Pros and Cons of the Options

### <option 1>

<description>

- Good, because <argument>
- Bad, because <argument>

### <option 2>

<description>

- Good, because <argument>
- Bad, because <argument>

## Links

- <Link type> <Link to ADR or resource>
```

#### File Naming

Use: `NNNN-kebab-case-title.md`

- `NNNN` = zero-padded sequence number (e.g., `0001`, `0002`)
- Title uses lowercase with hyphens (e.g., `use-postgresql-for-primary-database.md`)

### Phase 4: Validate

After writing, run the validation script:

```bash
python3 <skill-dir>/scripts/validate_adr.py <path-to-adr-file>
```

Fix any errors reported by the script. A valid ADR MUST pass all checks.

## When NOT to Use This Skill

- For decisions that are trivial, reversible, and single-developer — use a code comment instead
- For decisions already covered by existing standards or policies
- For temporary workarounds or experiments that won't ship to production

## Status Lifecycle

| Status | Meaning | When to use |
|--------|---------|-------------|
| `proposed` | Under discussion | Default for new ADRs |
| `accepted` | Approved and in effect | After stakeholder agreement |
| `deprecated` | No longer relevant | Replaced by newer thinking, no superseding ADR |
| `superseded` | Replaced by another ADR | Link to the superseding ADR |

## Conformance

An ADR is conformant if:
1. The file contains valid YAML frontmatter delimited by `---`
2. The frontmatter contains `type: ADR`, `title`, `description`, `tags`, and `timestamp`
3. All required body sections are present (see Phase 3)
4. The status is one of the valid values
5. The `Deciders` and `Date` fields are present in the body
6. The file follows the `NNNN-kebab-case-title.md` naming convention

## Quick Reference

| Task | Action |
|------|--------|
| Find existing ADRs | Search `**/adr/**/*.md`, `**/decisions/**/*.md` |
| Determine next number | Find highest `NNNN` prefix, increment by 1 |
| Validate an ADR | Run `validate_adr.py` on the file |
| Supersede an ADR | Create new ADR, update old ADR status to `superseded by [ADR-NNNN]` |