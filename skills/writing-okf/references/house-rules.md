# House Rules — Conventions ON TOP of the OKF Spec

These are house conventions for OKF bundles maintained with this skill. They are
**stricter than the OKF v0.1 specification** (see [okf-spec.md](okf-spec.md)).
A document can be spec-conformant yet still violate a house rule — the validator
labels every finding accordingly: `[SPEC]` (format conformance) or `[HOUSE]`
(house convention).

## Contents

- File naming
- Body expectations
- Frontmatter field policy
- Type vocabulary policy
- Bundle location policy
- Scaffolding maintenance (index.md / log.md)
- Validator policy

## File Naming

- Concept documents MUST use lowercase-kebab-case: `concept-name.md`
  (pattern: `^[a-z0-9]+(-[a-z0-9]+)*\.md$`).
- Reserved filenames `index.md` and `log.md` are exempt.
- The spec itself imposes no naming convention; this rule exists so bundles stay
  predictable to browse and diff. Validator: **ERROR [HOUSE]**.

## Body Expectations

- The body MUST NOT be empty — a concept without content carries no knowledge.
  Validator: **ERROR [HOUSE]**.
- The body SHOULD start with an H1 heading naming the concept.
  Validator: **WARN [HOUSE]**.
- The spec requires nothing of the body beyond markdown; structural markdown
  (headings, lists, tables, code blocks) remains the expectation.

## Frontmatter Field Policy

- `type` is REQUIRED by the spec. Validator: **ERROR [SPEC]**.
- `title`, `description`, `tags`, `timestamp` are expected on every concept.
  Validator: **WARN [SPEC]** when missing (spec labels them "Recommended").
- `resource` is only expected when the concept describes a tangible asset;
  absent for abstract concepts (metrics, playbooks, processes) — never warned on.

## Type Vocabulary Policy

- `type` values are free: there is no registry and no hard validation on
  unknown values. Programmers choose a fitting type per concept.
- Reuse `type` values already present in the bundle for consistency — consumers
  use `type` for routing, filtering, and presentation.
- When the user does not specify a `type`, the agent MUST propose one (reuse an
  existing bundle type when one fits, otherwise a new descriptive value) and
  confirm when ambiguous.
- There is deliberately **no validator block** on unknown types. This may be
  revisited if type sprawl becomes a problem.

## Bundle Location Policy

- The agent may investigate the codebase to locate a bundle, but MUST NEVER
  default to a standard location. When the location is not clear from context,
  the agent MUST ALWAYS ask the user.
- Rationale: a bundle created in the wrong place is worse than no bundle —
  it fragments knowledge and misleads consumers.

## Scaffolding Maintenance (index.md / log.md)

- When adding or modifying a concept: update the (sub)directory's `index.md`
  and `log.md` **when they are present**. Newest log entries first, date
  headings as `## YYYY-MM-DD`.
- When creating a new bundle: a root `index.md` is REQUIRED; `log.md` is
  optional. Declare `okf_version: "0.1"` in the root `index.md` frontmatter
  when versioning matters (the only legal index frontmatter — spec §11).
- Do NOT introduce index/log files into existing bundles that chose not to
  use them; respect the bundle's existing conventions.
- The spec makes both files optional; this policy keeps them trustworthy
  where they exist.

## Validator Policy

| Check | Level | Label |
|-------|-------|-------|
| Missing/unparseable YAML frontmatter | ERROR | `[SPEC]` |
| Missing or empty `type` | ERROR | `[SPEC]` |
| `log.md` without `## YYYY-MM-DD` date headings | ERROR | `[SPEC]` (spec §7: "MUST") |
| Missing `title` / `description` / `tags` / `timestamp` | WARN | `[SPEC]` |
| Frontmatter in reserved files (other than root `index.md` with only `okf_version`) | WARN | `[SPEC]` |
| Filename not lowercase-kebab-case | ERROR | `[HOUSE]` |
| Empty body | ERROR | `[HOUSE]` |
| No H1 heading in body | WARN | `[HOUSE]` |
| `index.md` without section headings | WARN | `[SPEC]` (spec §6 structure) |

A document is done when it passes all ERROR checks and the author has
consciously accepted or fixed every WARN.
