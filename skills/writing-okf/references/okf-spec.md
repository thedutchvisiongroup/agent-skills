# OKF Specification Summary

## What is OKF?

Open Knowledge Format (OKF) is a minimal, human- and agent-friendly format for
representing knowledge as markdown files with YAML frontmatter. It standardizes
the small set of structural conventions needed for self-describing knowledge
documents, and makes provenance, trust, freshness, and lifecycle first-class.

**Source:** https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

**Version:** 0.2

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
| **Concept ID** | Path of the file within the bundle, with `.md` removed (e.g. `tables/users`) |
| **Frontmatter** | YAML metadata block delimited by `---` on its own line |
| **Body** | Everything after the frontmatter |
| **Link** | Standard markdown link from one concept to another |
| **Source** | A material a concept derives from, external or internal to the bundle, recorded in the `sources` frontmatter family |
| **Provenance** | The set of sources a concept derives from |
| **Credibility signal** | An objective, per-source fact (`author`, `usage_count`, `last_modified`) used to infer trust; OKF records the signals, not a verdict |
| **Actor** | String identifying who or what performed an action: `<producer>/<version>` for agents/tools, `human:<id>` for people, `process:<id>` for automated processes |
| **Trust tier** | Level derived from a concept's `verified` field: **unverified**, **machine-confirmed**, or **human-reviewed** |
| **stale_after** | Absolute ISO 8601 instant; a concept is stale when `now >= stale_after` |
| **Citation** (v0.1 legacy) | Link to an external source backing a claim — superseded by `sources` (§13.1) |

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

A bundle MAY be distributed as:

- A git repository (recommended — provides history, attribution, diffs)
- A tarball or zip archive of the directory
- A subdirectory within a larger repository

## Reserved Filenames

| Filename | Purpose | Rules |
|----------|---------|-------|
| `index.md` | Directory listing | No frontmatter — EXCEPT an optional `okf_version` key in the bundle-ROOT `index.md` (see Versioning). Sections with bullet lists. |
| `log.md` | Update history | No frontmatter. Date-grouped entries, newest first. |

## Concept Document Structure

### Frontmatter

```yaml
---
type: <Type name>                            # REQUIRED — the only always-required key
title: <Optional display name>               # Recommended
description: <Optional one-line summary>     # Recommended
resource: <Optional canonical URI>           # If applicable
tags: [<tag>, <tag>, ...]                    # Recommended
generated: { by: <actor>, at: <ISO 8601 datetime> }       # Provenance/trust (§5.2)
verified: [{ by: <actor>, at: <ISO 8601 datetime> }]      # Trust (§5.2)
status: <draft | stable | deprecated>        # Lifecycle (§5.4); absent = stable
stale_after: <ISO 8601 datetime>             # Freshness (§5.5)
sources:                                     # Provenance (§5.1)
  - id: <stable-key>                         # Optional; REQUIRED when footnotes cite it
    resource: <URI, path, or scope>          # REQUIRED within each entry
    title: <human-readable label>            # Optional
    author: <actor>                          # Credibility signal (optional)
    usage_count: <count>                     # Credibility signal (optional)
    last_modified: <ISO 8601 datetime>       # Credibility signal (optional)
usage_window: { from: <ISO 8601>, to: <ISO 8601> }       # Optional sibling of sources
---
```

**Required:** `type` — still the ONLY always-required key; a concept carrying
just `type` is fully conformant.

**Recommended (in priority order):**
- `title` — Human-readable display name
- `description` — Single sentence summary
- `resource` — URI for the underlying asset (absent for abstract concepts)
- `tags` — YAML list for categorization
- `generated` — How the current content was produced; `by` REQUIRED within it (§5.2)
- `verified` — List of `{ by, at }` verification events; derives the trust tier (§5.2–§5.3)
- `status` — Lifecycle value: `draft`, `stable` (default), or `deprecated` (§5.4)
- `stale_after` — Absolute instant on/after which the content is stale (§5.5)
- `sources` — Provenance: materials the concept derives from; per-entry `resource`
  REQUIRED, optional `id`/`title`/`author`/`usage_count`/`last_modified`, and the
  `usage_window` sibling framing `usage_count` (§5.1)

**v0.1 legacy:** `timestamp` and the body `# Citations` list are superseded
(v0.2 §13.1) — by `generated.at` and `sources` respectively. Consumers MAY fall
back to them when consuming v0.1 documents.

**Extensions:** Additional keys MAY be included. Consumers SHOULD preserve unknown
keys when round-tripping and SHOULD NOT reject documents with unrecognized fields.

### Body

Standard markdown. SHOULD favor structural markdown (headings, lists, tables, code blocks)
over freeform prose. There are no required body sections.

Conventional headings:

| Heading | Purpose |
|---------|---------|
| `# Schema` | Structured description of fields/columns |
| `# Examples` | Concrete usage examples |
| `# Computation` | Sanctioned computation of an Attested Computation concept (§10) |

Per-claim attribution to external sources uses markdown footnotes keyed to
`sources[].id` rather than a body citations list (§5.1). The v0.1 `# Citations`
body list is legacy — superseded by the `sources` frontmatter family.

## Provenance, Trust, and Lifecycle (§5)

All families are optional at spec level. Their absence carries meaning: an
unverified concept is distinguishable from a verified one, but is never
rejected. Every timestamp-valued key is an ISO 8601 datetime with an explicit
UTC offset, for example `2026-06-30T14:00:00Z`.

### Provenance: `sources` (§5.1)

`sources` records the materials a concept derives from. Each entry carries:

- `resource` — REQUIRED within an entry. An absolute URL, a bundle-relative
  path, a path into a `references/` subdirectory, or a scope descriptor a
  consumer cannot follow (e.g. `all queries in project X`).
- `id` — Optional stable key used to attribute individual claims; SHOULD be
  present when the body cites the source.
- `title` — Optional human-readable label.
- Optional **credibility signals**: `author` (authority, in actor convention),
  `usage_count` (adoption/liveness), `last_modified` (recency of the source
  itself — distinct from `generated.at`, which records when the concept was
  written). `usage_window` is written once as a sibling of `sources` and
  frames every `usage_count` with a `{ from, to }` datetime range.

Credibility is *inferred* from the signals — OKF never stores a credibility
score.

**Per-claim attribution:** attribute a specific claim with a markdown footnote
whose label is a `sources[].id`:

```markdown
The `events_` table is sharded daily as `events_YYYYMMDD`.[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

Labels are keyed, not positional (`sources[0]`): a stable `id` survives list
reordering, a positional index silently misattributes when the list changes.

### Trust: `generated` and `verified` (§5.2)

- `generated: { by, at }` records how the current content was produced.
  `generated.by` is REQUIRED within `generated` and uses the actor convention;
  `generated.at` is the ISO 8601 datetime of the content's last meaningful
  change (supersedes the v0.1 `timestamp`).
- `verified` records who or what confirmed the content: a list of
  `{ by, at }` verification events. A bare mapping is treated as a
  one-element list. Independent of `generated.at` — who *wrote* a concept need
  not be who *confirmed* it, and facts can be re-confirmed without
  regeneration.

### Trust tiers (§5.3)

Derived from `verified`, lowest to highest:

- No `verified` key ⇒ **unverified**
- `verified` by non-`human:` actors only ⇒ **machine-confirmed**
- `verified` by a `human:<id>` actor ⇒ **human-reviewed**

Trust tiers are advisory signals, not access control.

### Lifecycle: `status` (§5.4)

- `draft` — not yet reviewed; possibly incomplete
- `stable` — default; ready for consumption
- `deprecated` — kept for links and history; no longer current

Absent `status` ⇒ `stable`.

### Freshness: `stale_after` (§5.5)

Optional absolute instant (not a relative TTL): a concept is stale when
`now >= stale_after`. The absolute form keeps the staleness decision a plain
comparison with no reference to when the concept was read.

## Actor Convention (§7)

Fields recording an identity (`generated.by`, `verified[].by`) use one actor
convention:

| Actor | Format | Example |
|-------|--------|---------|
| Agent / tool | `<producer>/<version>` | `reference_agent/gemini-2.5-pro` |
| Human | `human:<id>` | `human:ahormati` |
| Process | `process:<id>` | `process:finance-nightly` |

Consumers that classify trust key off the `human:` prefix, so producers MUST
use it for hand-authored or human-confirmed content.

## Cross-linking

### Bundle-relative (recommended)
```markdown
See the [customers table](/tables/customers.md) for the join key.
```

### Relative
```markdown
See the [neighboring concept](./other.md).
```

A link asserts a relationship; the kind is conveyed by surrounding prose.
Consumers MUST tolerate broken links — the target may be not-yet-written knowledge.

## Index Files

```markdown
# Section / Group Heading

* [Title 1](relative-url-1) - short description of item 1
* [Title 2](relative-url-2) - short description of item 2

# Another Section

* [Subdirectory](subdir/) - short description of the subdirectory
```

Entries SHOULD include the `description` from the linked concept's frontmatter.

## Log Files

```markdown
# Directory Update Log

## 2026-07-20
* **Update**: Added new reference for [Concept Name](concept.md).
* **Creation**: Established the [Overview](overview.md).

## 2026-07-15
* **Initialization**: Created foundational directory structure.
```

Date headings MUST use ISO 8601 `YYYY-MM-DD` form. The leading bold word
(`**Update**`, `**Creation**`, `**Deprecation**`) is a convention, not a requirement.

## Attested Computation (§10) — not adopted by this skill

v0.2 adds the `Attested Computation` concept type: a concept carrying a
sanctioned way to *compute* a value (`runtime`, `parameters`, `computation`,
`executor`, `attester`, and the `# Computation` heading) so a consumer can
confirm the value was produced by running the sanctioned computation instead
of an agent's improvisation. **This skill does not adopt Attested
Computation** — adopting it is optional future work; nothing in the house
rules or templates uses it.

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

## Versioning (§12)

- Minor version bumps introduce backward-compatible additions; major bumps may break.
- Bundles MAY declare the targeted OKF version with `okf_version: "0.2"` in a
  bundle-ROOT `index.md` frontmatter block — the ONLY place frontmatter is
  permitted in an `index.md`.
- Consumers that do not understand the declared version SHOULD attempt
  best-effort consumption rather than refusing the bundle.

## Changes from v0.1 (§13)

v0.2 supersedes v0.1 — a minor version bump with two deliberate breaking
renames:

1. **`timestamp` is superseded by `generated.at`.** The last content change is
   now recorded as `generated: { by, at }` (§5.2). Consumers MAY fall back to
   a legacy `timestamp` when `generated` is absent.
2. **The body `# Citations` list is superseded by `sources`.** Provenance
   moves to frontmatter (§5.1). Consumers SHOULD read `sources` and MAY still
   parse a legacy `# Citations` body list for v0.1 documents.

Everything else is additive: the `sources` family with its credibility signals
(`author`, `usage_count`, `last_modified`) and the `usage_window` sibling;
`generated`/`verified`; `status`/`stale_after`; the actor convention (§7); the
`Attested Computation` type with its computation keys; and the `# Computation`
heading. Bundle structure, reserved filenames, the required `type`, the
recommended `title`/`description`/`resource`/`tags`, cross-linking, index and
log files, and permissive conformance carry forward unchanged.