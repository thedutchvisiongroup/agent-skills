---
name: writing-adrs
description: Creates, validates, and manages Architecture Decision Records (ADRs) using the MADR 4.0 template with OKF-compliant YAML frontmatter. Use when the user needs to document an architectural decision, create a new ADR, review or supersede existing ADRs, validate ADR structure, or establish an ADR directory in a project. Covers discovery of existing ADR locations, ADR lifecycle management (proposed/rejected/accepted/deprecated/superseded), per-directory numbering rules, and conformance with Open Knowledge Format (OKF) frontmatter requirements.
---

# Writing Architecture Decision Records (ADRs)

Every ADR combines **OKF frontmatter** (metadata, machine-readable) with a **MADR 4.0 body** (the decision narrative). All metadata lives in the frontmatter — never duplicate it in the body.

## Process

### Phase 1: Discover ADR Location (REQUIRED)

Determine WHERE ADRs live by inferring context, not by asking.

1. **Search for existing ADRs** using these patterns:
   - `**/adr/**/*.md`, `**/adrs/**/*.md`, `**/decisions/**/*.md`
   - `**/docs/adr/**/*.md`, `**/docs/architecture/**/*.md`
   - Files matching `NNNN-*.md` in any directory

2. **If ADRs exist:**
   - Use that directory
   - Determine the next sequence number from existing files (highest `NNNN` + 1)
   - Proceed to Phase 2

3. **If no ADRs found — infer the logical location:**
   - Look at what part of the codebase the decision affects (the context)
   - If working in `src/database/`, place ADRs in `src/database/adr/`
   - If working in `services/auth/`, place ADRs in `services/auth/adr/`
   - If the decision is project-wide, use `docs/adr/` or `adr/` at the repo root
   - Create the directory and an `index.md` with this table header:

     ```markdown
     # ADR Index

     | ADR | Title | Status |
     |-----|-------|--------|
     ```
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
| `timestamp` | Current time (ISO 8601) | No — generate it |
| **Deciders** | — | **ALWAYS ASK** |
| **Status** | — | **ALWAYS ASK** |

**When to ask the user:**

- The user requested a change without explaining why → ask for the rationale
- Multiple valid interpretations of the decision exist → ask to disambiguate
- The "considered options" are not evident from context → ask what alternatives were evaluated
- **Always ask: who are the deciders?**
- **Always ask: what is the status?** (proposed / rejected / accepted / deprecated / superseded)

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

Every ADR has two parts: OKF frontmatter and MADR 4.0 body. For the fully annotated template and worked examples (minimal, rejected, supersede pair), read [references/adr-template.md](references/adr-template.md).

#### OKF Frontmatter (REQUIRED)

```yaml
---
type: ADR
title: "<short imperative title>"
description: "<one-line summary>"
tags: [<relevant>, <tags>]
deciders: [<person>, <person>]
status: <proposed | rejected | accepted | deprecated | superseded>
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

- `type` MUST be `ADR`
- `title` MUST match the markdown H1 heading exactly
- `description` MUST be a single sentence
- `tags` MUST be a YAML list of relevant tags
- `deciders` MUST be a YAML list of people involved in the decision
- `status` MUST be one of the lifecycle values (see Status Lifecycle)
- `timestamp` MUST be ISO 8601 of last meaningful change — bump it on every meaningful edit
- When `status: superseded`, `superseded_by: <relative path to the superseding ADR>` is REQUIRED
- Optional MADR fields: `consulted: [<person>]` (two-way input) and `informed: [<person>]` (one-way updates) MAY be added

#### MADR 4.0 Body

Sections marked REQUIRED must always be present; optional sections may be removed when they add no value. Use the full annotated template in [references/adr-template.md](references/adr-template.md).

```markdown
# <short title, representative of solved problem and found solution>   ← MUST equal frontmatter title

## Context and Problem Statement          (REQUIRED)

## Decision Drivers                       (optional)

## Considered Options                     (REQUIRED)

## Decision Outcome                       (REQUIRED)

### Consequences                          (optional — "Good/Bad/Neutral, because …")

### Confirmation                          (optional — how compliance will be verified)

## Pros and Cons of the Options           (optional — per option: "Good/Bad/Neutral, because …")

## More Information                       (optional — evidence, team agreement, "Supersedes …", links)
```

**Metadata discipline (MADR 4.0 style):** status, deciders and date live ONLY in the frontmatter. Do NOT add a `- Status:` / `- Deciders:` / `- Date:` block or a `Technical Story:` line to the body. Ticket/issue links go in `## More Information` or the Context section.

#### File Naming & Numbering

- Use: `NNNN-kebab-case-title.md` (e.g., `0001-use-postgresql-for-primary-database.md`)
- `NNNN` = zero-padded sequence number, unique **per ADR directory**
- Numbers are sequential, monotonic, and **NEVER reused** — not even after deprecation or superseding
- Because numbers repeat across directories, cross-references between ADRs MUST use path + number: `[ADR-0001](../auth/adr/0001-ldap-for-authentication.md)`

#### Update the Index (REQUIRED)

After writing the ADR file:

1. Add a row to the directory's `index.md`: `| [NNNN](NNNN-kebab-case-title.md) | <title> | <status> |`
2. If the directory has a `log.md`, add a dated entry there too
3. When superseding, also update the OLD ADR's row status

### Phase 4: Validate

After writing, run the validation script:

```bash
python3 <skill-dir>/scripts/validate_adr.py <path-to-adr-file>
python3 <skill-dir>/scripts/validate_adr.py <adr-directory>  # validates all ADRs; index.md/log.md are skipped
```

Fix any errors reported by the script. A valid ADR MUST pass all checks.

## Superseding an ADR

1. Create the new ADR with the next sequence number. In its `## More Information` section, link back: `Supersedes [ADR-NNNN](<path-to-old-adr>)`.
2. In the OLD ADR's frontmatter: set `status: superseded`, add `superseded_by: <relative path to the new ADR>`, and bump `timestamp`.
3. Update both rows in `index.md`.
4. NEVER delete the old ADR and NEVER reuse its number — the history is the point.

## When NOT to Use This Skill

- For decisions that are trivial, reversible, and single-developer — use a code comment instead
- For decisions already covered by existing standards or policies
- For temporary workarounds or experiments that won't ship to production

## Status Lifecycle

| Status | Meaning | When to use |
|--------|---------|-------------|
| `proposed` | Under discussion | Default for new ADRs |
| `rejected` | Proposal was considered and explicitly declined | Keep as record of the considered-and-rejected decision |
| `accepted` | Approved and in effect | After stakeholder agreement |
| `deprecated` | No longer relevant | Replaced by newer thinking, no superseding ADR |
| `superseded` | Replaced by another ADR | Requires `superseded_by` in frontmatter + link back in the new ADR |

## Conformance

An ADR is conformant if:

1. The file contains valid YAML frontmatter delimited by `---`
2. The frontmatter contains `type: ADR`, `title`, `description`, `tags`, `deciders`, `status`, and `timestamp`
3. The frontmatter `title` matches the H1 heading
4. The required MADR 4.0 body sections are present: `## Context and Problem Statement`, `## Considered Options`, `## Decision Outcome`
5. `status` is one of the valid lifecycle values; `status: superseded` implies a `superseded_by` path
6. The body contains no duplicated metadata block (`- Status:` / `- Deciders:` / `- Date:`)
7. The file follows the `NNNN-kebab-case-title.md` naming convention
8. The directory's `index.md` lists the ADR

For how these requirements map onto the OKF specification (and which are ADR-specific extensions), see [references/okf-conformance.md](references/okf-conformance.md).

## References

| Reference | When to read |
|-----------|--------------|
| [references/adr-template.md](references/adr-template.md) | Full annotated MADR 4.0 + OKF template; worked examples: minimal, rejected, supersede pair |
| [references/okf-conformance.md](references/okf-conformance.md) | OKF spec mapping: which fields OKF requires vs. which this skill adds as ADR extensions |

The skill's own architectural decisions live in [adr/](adr/index.md) — dogfooding this exact format.

## Quick Reference

| Task | Action |
|------|--------|
| Find existing ADRs | Search `**/adr/**/*.md`, `**/decisions/**/*.md` |
| Determine next number | Highest `NNNN` in that directory + 1; never reuse numbers |
| Infer location | Place ADRs near the code they affect |
| Gather context | Read git diffs, session summaries, surrounding code |
| Write an ADR | OKF frontmatter + MADR 4.0 body; see [references/adr-template.md](references/adr-template.md) |
| Link between ADRs | Use path + number: `[ADR-0001](../other/adr/0001-title.md)` |
| Validate an ADR | Run `validate_adr.py` on the file or directory |
| Supersede an ADR | See "Superseding an ADR" — update both ADRs + index |
