# OKF Conformance for ADRs

## What is OKF?

Open Knowledge Format (OKF) is a minimal, human- and agent-friendly format for
representing knowledge as markdown files with YAML frontmatter. It standardizes
the small set of structural conventions needed for self-describing knowledge
documents.

Source: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

## How ADRs Map onto OKF

An ADR is an OKF **concept document** with `type: ADR`. Important nuance:

- **OKF itself (§4.1) requires only one frontmatter field: `type`.** Fields
  like `title`, `description`, and `tags` are *recommended* by OKF, and OKF
  v0.2 defines the provenance block `generated` (`by` + `at`, §5.2).
- **This skill tightens the recommendations into requirements** and adds
  ADR-specific extension fields. OKF explicitly permits this: producers MAY
  include additional keys, and consumers MUST tolerate unknown keys (§4.1
  Extensions, §11 Conformance).

### Frontmatter (OKF §4.1 + ADR extensions)

```yaml
---
type: ADR                    # REQUIRED by OKF
title: "<display name>"      # recommended by OKF → REQUIRED by this skill
description: "<one-liner>"   # recommended by OKF → REQUIRED by this skill
tags: [<tag>, <tag>]         # recommended by OKF → REQUIRED by this skill
generated:                   # OKF v0.2 provenance (§5.2) → REQUIRED by this skill
  by: <actor>                #   actor convention: <harness>/<model-id> | human:<id> | process:<id>
  at: <ISO 8601 with UTC offset>
deciders: [<person>]         # ADR extension (OKF-unknown key) → REQUIRED by this skill
status: <lifecycle value>    # ADR extension (OKF-unknown key) → REQUIRED by this skill
superseded_by: <path>        # ADR extension → REQUIRED when status is superseded
---
```

Notes on the extension fields:

- `deciders` plays the role MADR 4.0 calls `decision-makers`. This skill uses
  the shorter `deciders` for consistency with OKF's terse naming style.
- MADR 4.0's optional `consulted` and `informed` MAY be added as further
  extension keys.
- MADR 4.0's optional `date` field is intentionally omitted: OKF v0.2's
  `generated.at` already records the last meaningful change, and two date
  fields invite drift.
- OKF v0.2's optional freshness/trust fields (`verified`, `stale_after`) MAY
  be added when truthfully known — NEVER fabricate them. `verified` is a list
  of `{ by, at }` entries; the supersede flow suggests appending one when the
  new ADR was human-confirmed.

### Body (OKF §4.2)

OKF requires no specific body sections; it recommends structural markdown over
freeform prose. This skill requires the MADR 4.0 core sections
(`## Context and Problem Statement`, `## Considered Options`,
`## Decision Outcome`) and allows the remaining MADR 4.0 sections as optional.

OKF v0.2 replaces the legacy conventional `# Citations` heading with
structured `sources` frontmatter (§5.1): one entry per source, each with
`resource` REQUIRED, plus `id` REQUIRED once the body cites it via a `[^id]`
footnote (per-claim attribution). In ADRs, evidence and links primarily live
in MADR 4.0's `## More Information` section; when a claim needs per-source
attribution, add the source to `sources` and reference it with a `[^id]`
footnote. Prefer `sources` over a legacy `# Citations` heading.

### Cross-linking (OKF §6)

ADRs link with standard markdown links. Because ADR numbers are only unique
within their directory, links between ADRs MUST include the path, not just the
number:

- **Relative:** `[ADR-0004](./0004-use-postgresql.md)` — within one directory
- **Bundle-relative:** `[auth ADR-0001](/services/auth/adr/0001-ldap.md)` — across directories

Per OKF §6.1, consumers MUST tolerate broken links; the validator only warns
about a missing `superseded_by` target, never errors.

## Conformance Checklist

An ADR is conformant when ALL of these hold:

- [ ] Parseable YAML frontmatter block delimited by `---` (OKF §11.1)
- [ ] `type: ADR` present (OKF §11.2)
- [ ] `title`, `description`, `tags` present; `generated` present with `by` + `at` (skill-tightened OKF v0.2 requirements)
- [ ] `deciders` and `status` present (skill extensions)
- [ ] When external sources are cited: `sources` entries carry `resource` (and `id` when cited via `[^id]` footnotes) — the legacy `# Citations` heading is retired
- [ ] Frontmatter `title` matches the H1 heading
- [ ] Required MADR 4.0 sections present; no duplicated metadata block in the body
- [ ] `status: superseded` implies `superseded_by`
- [ ] Filename matches `NNNN-kebab-case-title.md`
- [ ] UTF-8 encoded, valid markdown

Consumers MUST NOT reject an ADR because of (OKF §11):

- Unknown additional frontmatter keys
- Broken cross-links
- Missing optional MADR sections or citations

## Differences from Generic OKF

| Aspect | Generic OKF | This ADR Skill |
|--------|-------------|----------------|
| Required frontmatter | Only `type` | `type` + `title`, `description`, `tags`, `generated` (tightened OKF v0.2) + `deciders`, `status` (extensions) |
| `type` value | Any descriptive string | MUST be `ADR` |
| Body sections | None required | MADR 4.0 core required, rest optional |
| Provenance | v0.2 `generated {by, at}` (§5.2); actors `<harness>/<model-id>`, `human:<id>`, `process:<id>`; `verified`/`stale_after` optional, never fabricated | Same actor convention; `generated` tightened to REQUIRED |
| Citations | v0.2 `sources` frontmatter (§5.1): `resource` required per entry; footnote `[^id]` for per-claim attribution | Same `sources` convention; evidence links live in MADR's `## More Information` |
| Status | v0.2 `status`: draft / stable / deprecated (absent = stable) | **House exception:** ADR lifecycle `status`: proposed / rejected / accepted / deprecated / superseded — OKF `status` vocabulary intentionally NOT applied (see Status Lifecycle in SKILL.md) |
| File naming | Any `.md` except reserved | `NNNN-kebab-case-title.md` |
| Reserved files | `index.md`, `log.md` | Same; validator skips them in directory mode |
| `index.md` | Optional, frontmatter-free listing (except root-index `okf_version`, spec §12) | Required per ADR directory; table with ADR / Title / Status |
