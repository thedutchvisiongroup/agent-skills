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
  like `title`, `description`, `tags`, and `timestamp` are *recommended* by
  OKF, not required.
- **This skill tightens the recommendation into a requirement** and adds
  ADR-specific extension fields. OKF explicitly permits this: producers MAY
  include additional keys, and consumers MUST tolerate unknown keys (§4.1
  Extensions, §9 Conformance).

### Frontmatter (OKF §4.1 + ADR extensions)

```yaml
---
type: ADR                    # REQUIRED by OKF
title: "<display name>"      # recommended by OKF → REQUIRED by this skill
description: "<one-liner>"   # recommended by OKF → REQUIRED by this skill
tags: [<tag>, <tag>]         # recommended by OKF → REQUIRED by this skill
timestamp: <ISO 8601>        # recommended by OKF → REQUIRED by this skill
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
- MADR 4.0's optional `date` field is intentionally omitted: OKF's `timestamp`
  already records the last meaningful change, and two date fields invite drift.

### Body (OKF §4.2)

OKF requires no specific body sections; it recommends structural markdown over
freeform prose. This skill requires the MADR 4.0 core sections
(`## Context and Problem Statement`, `## Considered Options`,
`## Decision Outcome`) and allows the remaining MADR 4.0 sections as optional.

OKF's conventional `# Citations` heading (§8) maps naturally onto MADR 4.0's
`## More Information` section; use either when citing external sources.

### Cross-linking (OKF §5)

ADRs link with standard markdown links. Because ADR numbers are only unique
within their directory, links between ADRs MUST include the path, not just the
number:

- **Relative:** `[ADR-0004](./0004-use-postgresql.md)` — within one directory
- **Bundle-relative:** `[auth ADR-0001](/services/auth/adr/0001-ldap.md)` — across directories

Per OKF §5.3, consumers MUST tolerate broken links; the validator only warns
about a missing `superseded_by` target, never errors.

## Conformance Checklist

An ADR is conformant when ALL of these hold:

- [ ] Parseable YAML frontmatter block delimited by `---` (OKF §9.1)
- [ ] `type: ADR` present (OKF §9.2)
- [ ] `title`, `description`, `tags`, `timestamp` present (skill-tightened OKF recommendations)
- [ ] `deciders` and `status` present (skill extensions)
- [ ] Frontmatter `title` matches the H1 heading
- [ ] Required MADR 4.0 sections present; no duplicated metadata block in the body
- [ ] `status: superseded` implies `superseded_by`
- [ ] Filename matches `NNNN-kebab-case-title.md`
- [ ] UTF-8 encoded, valid markdown

Consumers MUST NOT reject an ADR because of (OKF §9):

- Unknown additional frontmatter keys
- Broken cross-links
- Missing optional MADR sections or citations

## Differences from Generic OKF

| Aspect | Generic OKF | This ADR Skill |
|--------|-------------|----------------|
| Required frontmatter | Only `type` | `type` + `title`, `description`, `tags`, `timestamp` (tightened) + `deciders`, `status` (extensions) |
| `type` value | Any descriptive string | MUST be `ADR` |
| Body sections | None required | MADR 4.0 core required, rest optional |
| Status | Not specified | Frontmatter `status`: proposed / rejected / accepted / deprecated / superseded |
| File naming | Any `.md` except reserved | `NNNN-kebab-case-title.md` |
| Reserved files | `index.md`, `log.md` | Same; validator skips them in directory mode |
| `index.md` | Optional, frontmatter-free listing | Required per ADR directory; table with ADR / Title / Status |
