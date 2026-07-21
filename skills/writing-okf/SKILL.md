---
name: writing-okf
description: Creates, validates, and manages Open Knowledge Format (OKF) documents — markdown files with YAML frontmatter that represent structured knowledge about data, systems, and processes. Use when the user needs to document system components, data assets, APIs, metrics, playbooks, or any knowledge that should be machine-readable and agent-friendly. Covers bundle structure, cross-linking, index files, and conformance with the OKF specification.
---

# Writing Open Knowledge Format (OKF) Documents

## Reference Files

Load these when needed:

- **[references/okf-spec.md](references/okf-spec.md)** — Summary of the OKF v0.1 specification (the format rules)
- **[references/house-rules.md](references/house-rules.md)** — House conventions ON TOP of the spec (naming, type vocabulary, validator policy)
- **[references/concept-templates.md](references/concept-templates.md)** — Ready-to-use document templates per concept type

## Process

### Phase 1: Locate the Bundle (REQUIRED)

Determine WHERE the OKF bundle lives.

1. **Search for existing OKF bundles** by looking for:
   - `index.md` files that contain directory listings
   - Markdown files with YAML frontmatter containing a `type` field
   - Directories named `knowledge/`, `docs/`, `catalog/`, or `bundle/`

2. **Decide:**
   - **Exactly one unambiguous bundle location found** → use it, follow the existing organization pattern, proceed to Phase 2.
   - **No bundle found, or multiple candidate locations** → STOP. Ask the user where the bundle lives or should be created.

```
RULE: You may investigate the codebase yourself, but you MUST NEVER
default to a standard location for a bundle. When the location is not
clear from the context, you MUST ALWAYS ask the user.
```

### Phase 2: Gather Context + Clarify (REQUIRED)

Gather context from available sources BEFORE drafting:

1. **Code context** — Read the code, configs, and schemas being documented
2. **Git history** — Check recent commits for context on changes
3. **Existing OKF documents** — Check for related concepts already documented; reuse their `type` values for consistency
4. **Session summaries** — Check for relevant session context

**Clarification gate (hybrid):**

- **New bundle, or ambiguous request** → You MUST ask at least one clarifying question and confirm your plan in 2-3 sentences before drafting.
- **Clear task within an existing bundle** → Proceed, but state your assumptions briefly.

**When to ask the user:**

- Multiple valid interpretations of what to document exist → ask to disambiguate
- The purpose of the document is unclear → ask for clarification
- Technical details are not evident from code → ask for specifics

**Type proposal rule:** If the user did not specify a `type`, you MUST propose one yourself — reuse an existing `type` from the bundle when one fits, otherwise propose a new descriptive value. Confirm with the user when ambiguous.

```
STOP. Before drafting, verify:
- [ ] I know what concept/asset this document describes
- [ ] I gathered context from code and existing docs
- [ ] I know the appropriate `type` value (or proposed one)
- [ ] I have enough information to write the body (or I asked)
- [ ] Clarification gate satisfied (question asked, or assumptions stated)
If any box is unchecked: gather the missing information first.
```

### Phase 3: Write the OKF Document

Every OKF document has two parts: YAML frontmatter and markdown body. See [references/concept-templates.md](references/concept-templates.md) for complete per-type templates.

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
  - `Service`, `API Endpoint`
  - `Dataset`, `Table`
  - `Metric`, `Playbook`, `Reference`
  - `ADR` (for architecture decision records)
  - Any descriptive string — consumers MUST tolerate unknown types

**Recommended fields:**
- `title` — Human-readable display name
- `description` — Single sentence summarizing the concept
- `resource` — URI that uniquely identifies the underlying asset (only when applicable)
- `tags` — YAML list of short strings for categorization
- `timestamp` — ISO 8601 datetime of last meaningful change

**Extensions:** Additional keys MAY be included. Consumers SHOULD preserve unknown keys when round-tripping.

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

#### File Naming (house rule)

- Use lowercase with hyphens: `concept-name.md`
- Exception: reserved filenames `index.md` and `log.md`
- This is a house convention, not part of the OKF spec — see [references/house-rules.md](references/house-rules.md)

### Phase 4: Update Bundle Scaffolding

When adding or modifying a concept:

- **`index.md` present in the (sub)directory** → You MUST update it: add or refresh the entry, using the `description` from the concept's frontmatter.
- **`log.md` present in the (sub)directory** → You MUST add a date-grouped entry (newest first, `## YYYY-MM-DD`).
- **Creating a NEW bundle** → A root `index.md` is REQUIRED; `log.md` is optional. Consider declaring `okf_version: "0.1"` in the root `index.md` frontmatter — the ONLY place frontmatter is permitted in an `index.md` (spec §11).
- **Existing bundle without index/log files** → Do NOT create them; respect the bundle's existing conventions.

### Phase 5: Validate

After writing, run the validation script:

```bash
python3 <skill-dir>/scripts/validate_okf.py <path-to-file-or-directory>
```

- `[SPEC]` findings are OKF conformance violations — ALWAYS fix them.
- `[HOUSE]` findings are house conventions — fix them unless the user explicitly waives them.

After the script passes, verify manually:

```
- [ ] Cross-links point to the intended concepts
- [ ] index.md / log.md updated (when present — see Phase 4)
- [ ] `type` value consistent with sibling documents
- [ ] No [SPEC] errors remain
```

## Reserved Files

| Filename | Purpose |
|----------|---------|
| `index.md` | Directory listing for progressive disclosure |
| `log.md` | Chronological history of updates |

These filenames MUST NOT be used for concept documents.

### Index Files

An `index.md` enumerates a directory's contents. Contains no frontmatter — EXCEPT an optional `okf_version: "0.1"` declaration in the bundle-ROOT `index.md` (spec §11). Uses sections with headings:

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

An OKF document is conformant with the spec if:
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

House rules (file naming, non-empty body, scaffolding maintenance) are stricter than the spec — see [references/house-rules.md](references/house-rules.md).

## When NOT to Use This Skill

- For trivial notes or comments — use code comments instead
- For documentation that belongs in a different format (e.g., API specs in OpenAPI)
- For temporary or throwaway documentation

## Quick Reference

| Task | Action |
|------|--------|
| Find existing bundles | Search for `index.md` files with directory listings |
| Bundle location unclear | ALWAYS ask the user — never pick a default |
| Create a concept | Write markdown with YAML frontmatter containing `type` |
| Choose a `type` | Reuse sibling types, or propose a descriptive new one |
| See per-type templates | Read [references/concept-templates.md](references/concept-templates.md) |
| Check the format rules | Read [references/okf-spec.md](references/okf-spec.md) |
| Check house conventions | Read [references/house-rules.md](references/house-rules.md) |
| Link to other concepts | Use bundle-relative paths: `[name](/path/to/file.md)` |
| Add/update a concept | Also update `index.md` and `log.md` when present |
| Log changes | Add `log.md` entries with `## YYYY-MM-DD` headings |
| Validate | Run `validate_okf.py`; fix `[SPEC]` always, `[HOUSE]` unless waived |

Base directory for this skill: /root/htdocs/projects-tdvg/agent-skills/skills/writing-okf
Relative paths in this skill (e.g., scripts/, references/) are relative to this base directory.
