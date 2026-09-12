---
name: writing-okf
description: Creates, validates, and manages Open Knowledge Format (OKF) documents — markdown files with YAML frontmatter that represent structured knowledge about data, systems, and processes. Use when the user needs to document system components, data assets, APIs, metrics, playbooks, or any knowledge that should be machine-readable and agent-friendly. Covers bundle structure, cross-linking, same-level index.md/log.md files in every directory, and conformance with the OKF specification.
---

# Writing Open Knowledge Format (OKF) Documents

## Reference Files

Load these when needed:

- **[references/okf-spec.md](references/okf-spec.md)** — Summary of the OKF v0.2 specification (the format rules)
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
generated: { by: <actor>, at: <ISO 8601 datetime> }
status: <draft|stable|deprecated>
---
```

**Required field:**
- `type` — A short string identifying the kind of concept. Examples:
  - `Service`, `API Endpoint`
  - `Dataset`, `Table`
  - `Metric`, `Playbook`, `Reference`
  - `ADR` (for architecture decision records)
  - Any descriptive string — consumers MUST tolerate unknown types

**House-required fields** (REQUIRED at house level):
- `generated` — `{ by, at }` recording which actor produced the content and
  when; `by` uses the actor convention below
- `status` — `draft | stable | deprecated` (spec: absent `status` means `stable`)

**Recommended fields (spec):**
- `title` — Human-readable display name
- `description` — Single sentence summarizing the concept
- `resource` — URI that uniquely identifies the underlying asset (only when applicable)
- `tags` — YAML list of short strings for categorization

**Optional families (OKF v0.2):**
- `verified` — list of `{ by, at }` verification events; record only
  verifications that actually happened — never fabricate
- `stale_after` — ISO 8601 instant on/after which the content is
  stale; never fabricate
- `sources` — provenance entries backing the
  document's claims; `resource` REQUIRED per entry, `id` REQUIRED when
  footnotes cite the entry

**Actor convention** (for `generated.by` and `verified[].by`):

| Actor | Format | Example |
|-------|--------|---------|
| Agent | `opencode/<model-id>` | `opencode/glm-5.3-flash` |
| Human | `human:<id>` | `human:thim` |
| Process | `process:<id>` | `process:finance-nightly` |

**Per-claim attribution:** attribute a claim to a source with a markdown
footnote whose label is the `sources[].id`:

```markdown
The table is sharded daily.[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

**Extensions:** Additional keys MAY be included. Consumers SHOULD preserve unknown keys when round-tripping.

#### Markdown Body (REQUIRED)

The body is standard markdown. Use structural markdown — headings, lists, tables, fenced code blocks — over freeform prose.

**Conventional section headings** (use when applicable):

| Heading | Purpose |
|---------|---------|
| `# Schema` | Structured description of columns/fields |
| `# Examples` | Concrete usage examples, often as fenced code blocks |
| `# Computation` | Sanctioned computation of an Attested Computation concept (spec §10 — not adopted by this skill; per-claim provenance moved to `sources` frontmatter) |

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

Scaffolding is STANDARD: every directory that holds concept documents carries its own `index.md` and `log.md`. This is what keeps deep, nested bundles trustworthy at every level.

When adding or modifying a concept:

- **Directory has no `index.md`/`log.md`** → You MUST create them there, with the new concept as their first entry.
- **`index.md` present** → You MUST update it: add or refresh the entry, using the `description` from the concept's frontmatter.
- **`log.md` present** → You MUST add a date-grouped entry (newest first, `## YYYY-MM-DD`).
- **Creating a NEW bundle** → A root `index.md` is REQUIRED; `log.md` is strongly recommended. Consider declaring `okf_version: "0.2"` in the root `index.md` frontmatter — the ONLY place frontmatter is permitted in an `index.md` (spec §12).
- **Existing index/log with nested references** → You MUST migrate them: move the entry to the target directory's own `index.md`/`log.md` and replace the parent entry with a subdirectory entry (`subdir/`).

```
RULE: An index.md or log.md references ONLY its OWN directory level:
concept files ('file.md') and direct subdirectories ('subdir/'). NEVER
link a nested path ('subdir/file.md') from a parent index or log — the
subdirectory's own scaffolding is the place for that. A top-level index
that reaches into deep subdirectories defeats progressive disclosure
and goes stale immediately.
```

### Phase 5: Validate

After writing, run the validation script:

```bash
# Single file
python3 <skill-dir>/scripts/validate_okf.py <path-to-file>
# Whole bundle — recursive, one run covers every nested directory
python3 <skill-dir>/scripts/validate_okf.py <path-to-bundle>
# Machine-readable output for agents
python3 <skill-dir>/scripts/validate_okf.py --json <path-to-bundle>
```

Directory mode scans the entire tree recursively: every `.md` file is validated, and every directory holding `.md` content also gets the scaffolding checks (missing `index.md`/`log.md`). One run shows the complete error picture of a deeply nested bundle — never run it per directory.

- `[SPEC]` findings are OKF conformance violations — ALWAYS fix them.
- `[HOUSE]` findings are house conventions — fix them unless the user explicitly waives them.
- Findings carry line numbers and a check name (`index-scope`, `index-completeness`, `log-scope`, `scaffolding`, …) — jump straight to the offending link.

After the script passes, verify manually:

```
- [ ] Cross-links point to the intended concepts
- [ ] index.md / log.md updated in EVERY directory touched (see Phase 4)
- [ ] index.md/log.md entries are same-level only (no nested references)
- [ ] `type` value consistent with sibling documents
- [ ] `generated: { by, at }` and `status` present
- [ ] No [SPEC] errors remain
```

## Reserved Files

| Filename | Purpose |
|----------|---------|
| `index.md` | Directory listing for progressive disclosure |
| `log.md` | Chronological history of updates |

These filenames MUST NOT be used for concept documents.

### Index Files

An `index.md` enumerates a directory's contents — ONLY that directory's: every concept file and every direct subdirectory, nothing deeper. Contains no frontmatter — EXCEPT an optional `okf_version: "0.2"` declaration in the bundle-ROOT `index.md` (spec §12). Uses sections with headings:

```markdown
# Section / Group Heading

* [Title 1](file-1.md) - short description of item 1
* [Title 2](file-2.md) - short description of item 2
* [Subdirectory](subdir/) - short description of the subdirectory
```

**Same-level rules (house — validator enforces):**

- Every entry links SAME-LEVEL: a concept file (`file.md`) or a direct subdirectory (`subdir/`).
- Every concept file in the directory MUST have an entry; every direct subdirectory MUST have an entry. Non-`.md` files and external links (`https://…`) are exempt.
- Every entry MUST point at an existing target — no dead entries.
- Bundle-absolute links (`/path/to/file.md`) are FORBIDDEN in `index.md` — use the relative form. (Concept documents keep using bundle-relative links for cross-linking.)

```markdown
GOOD — top-level index of a bundle:
* [orders](orders.md) - one row per completed order
* [reference data](reference-data/) - lookup tables for joins

BAD — nested references belong in reference-data/index.md:
* [countries](reference-data/countries.md) - country codes
* [currencies](reference-data/currencies.md) - currency codes
```

### Log Files

A `log.md` records change history for its OWN directory. Same-level rule applies: entries reference only same-directory files and direct subdirectories. (Historical entries may point at since-renamed files — the validator only warns there.) Format: flat list of date-grouped entries, newest first:

```markdown
# Directory Update Log

## 2026-07-20
* **Creation**: Established the [Service Overview](service-overview.md).

## 2026-07-15
* **Initialization**: Created foundational directory structure.
```

Date headings MUST use ISO 8601 `YYYY-MM-DD` form.

## Bundle Structure

A bundle is a directory tree of markdown files. Scaffolding is per-directory: every directory holding concepts has its own `index.md` and `log.md`, and each index/log references only its own directory level:

```
bundle/
├── index.md                      # Lists bundle/ contents: root concepts + subdirs (as 'subdir/')
├── log.md                        # History of bundle/ itself
├── <concept>.md                  # Concept at bundle root
└── <subdirectory>/               # Subdirectories organize concepts
    ├── index.md                  # Lists THIS directory's concepts + subdirs
    ├── log.md                    # History of THIS directory
    ├── <concept>.md
    └── <subdirectory>/
        ├── index.md
        ├── log.md
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

House rules (file naming, non-empty body, standard scaffolding, same-level index/log scoping, provenance/trust/lifecycle frontmatter) are stricter than the spec — see [references/house-rules.md](references/house-rules.md).

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
| Record provenance | `generated: { by, at }` and `status` REQUIRED at house level — see [references/house-rules.md](references/house-rules.md) |
| Attribute a claim | `sources` entry plus a `[^id]` footnote keyed to `sources[].id` |
| Pick an actor | `opencode/<model-id>` (agents), `human:<id>` (people), `process:<id>` (processes) |
| See per-type templates | Read [references/concept-templates.md](references/concept-templates.md) |
| Check the format rules | Read [references/okf-spec.md](references/okf-spec.md) |
| Check house conventions | Read [references/house-rules.md](references/house-rules.md) |
| Link to other concepts | Use bundle-relative paths: `[name](/path/to/file.md)` |
| Add/update a concept | Update `index.md` and `log.md` — create them when the directory lacks them |
| Index/log entries | Same-level ONLY: `file.md` and `subdir/` — never nested paths |
| Nested reference found | Move the entry to that subdirectory's own `index.md`/`log.md`; list `subdir/` in the parent |
| Log changes | Add `log.md` entries with `## YYYY-MM-DD` headings |
| Validate | Run `validate_okf.py` on the bundle root (recursive); add `--json` for machine-readable output |

Base directory for this skill: /home/thim/htdocs/projects-tdvg/agent-skills/skills/writing-okf
Relative paths in this skill (e.g., scripts/, references/) are relative to this base directory.
