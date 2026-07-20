---
name: writing-adrs
description: Creates, validates, and manages Architecture Decision Records (ADRs) using the MADR template with OKF-compliant YAML frontmatter. Use when the user needs to document an architectural decision, create a new ADR, review existing ADRs, validate ADR structure, or establish an ADR directory in a project. Covers discovery of existing ADR locations, ADR lifecycle management (proposed/accepted/deprecated/superseded), and ensures conformance with Open Knowledge Format (OKF) frontmatter requirements.
---

# Writing Architecture Decision Records (ADRs)

## Process

### Phase 1: Discover ADR Location (REQUIRED)

Determine WHERE ADRs live by inferring context, not by asking.

1. **Search for existing ADRs** using these patterns:
   - `**/adr/**/*.md`, `**/adrs/**/*.md`, `**/decisions/**/*.md`
   - `**/docs/adr/**/*.md`, `**/docs/architecture/**/*.md`
   - Files matching `NNNN-*.md` in any directory

2. **If ADRs exist:**
   - Use that directory
   - Determine the next sequence number from existing files
   - Proceed to Phase 2

3. **If no ADRs found — infer the logical location:**
   - Look at what part of the codebase the decision affects (the context)
   - If working in `src/database/`, place ADRs in `src/database/adr/`
   - If working in `services/auth/`, place ADRs in `services/auth/adr/`
   - If the decision is project-wide, use `docs/adr/` or `adr/` at the repo root
   - Create the directory and an `index.md`
   - Proceed to Phase 2

### Phase 2: Gather Decision Context (REQUIRED)

Gather context from available sources BEFORE drafting. Minimize questions.

**Gather from these sources first:**

1. **Git diffs** — Read recent commits and diffs to understand what changed and why
2. **Session summaries** — Check for any session summaries or compactions that explain the decision context
3. **Code context** — Read the surrounding code, comments, and related files
4. **Existing ADRs** — Check if any related decisions are already documented

**Then assess what you know vs. what's missing:**

| Field | Source | Ask? |
|-------|--------|------|
| Decision | Git diff / session context | Only if unclear |
| Context & Problem | Git diff / code / session | Only if rationale is missing |
| Decision Drivers | Inferred from code and context | Only if ambiguous |
| Considered Options | Git diff / session / code comments | Only if alternatives aren't evident |
| Decision Outcome | From the implemented change | No — read from code |
| Consequences | Inferred from the change | Only if impact is unclear |
| **Deciders** | — | **ALWAYS ASK** |
| **Status** | — | **ALWAYS ASK** |

**When to ask the user:**

- The user requested a change without explaining why → ask for the rationale
- Multiple valid interpretations of the decision exist → ask to disambiguate
- The "considered options" are not evident from context → ask what alternatives were evaluated
- **Always ask: who are the deciders?**
- **Always ask: what is the status?** (proposed / accepted / deprecated / superseded)

```
STOP. Before drafting, verify:
- [ ] I gathered context from git diffs and session history
- [ ] I know the decision and its rationale (or I asked)
- [ ] I know the deciders (ASKED the user)
- [ ] I know the status (ASKED the user)
- [ ] I have at least 2 options documented (or asked the user)
If any box is unchecked: gather the missing information first.
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
deciders: [<person>, <person>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

- `type` MUST be `ADR`
- `title` MUST match the markdown H1 heading
- `description` MUST be a single sentence
- `tags` MUST be a YAML list of relevant tags
- `deciders` MUST be a YAML list of people involved in the decision
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
2. The frontmatter contains `type: ADR`, `title`, `description`, `tags`, `deciders`, and `timestamp`
3. All required body sections are present (see Phase 3)
4. The status is one of the valid values
5. The `Deciders` and `Date` fields are present in the body
6. The file follows the `NNNN-kebab-case-title.md` naming convention

## Quick Reference

| Task | Action |
|------|--------|
| Find existing ADRs | Search `**/adr/**/*.md`, `**/decisions/**/*.md` |
| Determine next number | Find highest `NNNN` prefix, increment by 1 |
| Infer location | Place ADRs near the code they affect |
| Gather context | Read git diffs, session summaries, surrounding code |
| Validate an ADR | Run `validate_adr.py` on the file |
| Supersede an ADR | Create new ADR, update old ADR status to `superseded by [ADR-NNNN]` |
