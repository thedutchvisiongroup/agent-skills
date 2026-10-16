# House Rules — Conventions ON TOP of the OKF Spec

These are house conventions for OKF bundles maintained with this skill. They are
**stricter than the OKF v0.2 specification** (see [okf-spec.md](okf-spec.md)).
A document can be spec-conformant yet still violate a house rule — the validator
labels every finding accordingly: `[SPEC]` (format conformance) or `[HOUSE]`
(house convention).

## Contents

- File naming
- Body expectations
- Frontmatter field policy
- Provenance, trust, and lifecycle (OKF v0.2)
- Type vocabulary policy
- Bundle location policy
- Scaffolding maintenance (index.md / log.md)
- Index and log scoping (same-level rule)
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
- `title`, `description`, `tags` are expected on every concept.
  Validator: **WARN [SPEC]** when missing (spec labels them "Recommended").
- `resource` is only expected when the concept describes a tangible asset;
  absent for abstract concepts (metrics, playbooks, processes) — never warned on.
- `generated` and `status` are REQUIRED at house level on every concept this
  skill writes — see Provenance, Trust, and Lifecycle below.
- `verified`, `stale_after`, and `sources` are optional: add them when they are
  true, never fabricate them.

## Provenance, Trust, and Lifecycle (OKF v0.2)

House adopts the OKF v0.2 provenance, trust, freshness, and lifecycle families
(see [okf-spec.md](okf-spec.md), spec §5 and §7). Attested Computation (spec
§10) is NOT adopted.

- `generated: { by, at }` is REQUIRED at house level on every concept — it
  replaces the v0.1 `timestamp`. A legacy `timestamp` (with or without
  `generated`) triggers the validator's WARN nudge to migrate.
- `status` is REQUIRED at house level, one of `draft | stable | deprecated`
  (spec: absent `status` means `stable`).
- `verified` and `stale_after` are optional and NEVER fabricated: record
  verification events and staleness instants only when they actually exist.
- `sources` replaces the v0.1 body `# Citations` list. Every entry carries a
  REQUIRED `resource`; `id` is REQUIRED when body footnotes cite the entry.
  Per-claim attribution uses markdown footnotes keyed to `sources[].id`:

  ```markdown
  The pipeline runs hourly.[^pipeline-docs]

  [^pipeline-docs]: Pipeline documentation
  ```

House-required is an AUTHORING requirement: the validator checks the shapes of
`generated` and `status` when they are present (see Validator Policy below) but
does not flag their absence — the skill's Phase 5 manual checklist is the
authoring-time enforcement.

Actor convention for `generated.by` and `verified[].by`:

| Actor | Format | Example |
|-------|--------|---------|
| Agent | `<harness>/<model-id>` | `opencode/glm-5.3-flash`, `claude-code/claude-sonnet-5-5` |
| Human | `human:<id>` | `human:thim` |
| Process | `process:<id>` | `process:finance-nightly` |

**ADR status exception:** concepts with `type: ADR` use the MADR 4.0 lifecycle
vocabulary (`proposed | rejected | accepted | deprecated | superseded`) in
`status` instead of the OKF three-value set. Rationale: the ADR lifecycle
carries decision-specific meaning (a rejected ADR is a considered-and-declined
record; a superseded ADR points at its successor via `superseded_by`) that
collapsing into `draft | stable | deprecated` would destroy. The vocabularies
map monotonically — proposed ≈ `draft`, accepted ≈ `stable`,
rejected/deprecated/superseded ≈ `deprecated`. This exception is mechanically
enforced: the validator EXEMPTS `type: ADR` concepts from the
`status-vocabulary` check entirely (no WARN fires on ADR statuses; every other
v0.2 check still applies to ADRs). ADR status correctness itself is enforced by
the writing-adrs skill's `validate_adr.py` — `validate_okf.py` deliberately
provides no typo safety-net for ADR `status` values.

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

- Scaffolding is STANDARD: every directory that holds concept documents carries
  its own `index.md` and `log.md`. When adding or modifying a concept in a
  directory that lacks them, CREATE them there — do not route the entry through
  a parent directory's scaffolding.
- When adding or modifying a concept: update the directory's `index.md`
  (add or refresh the entry, using the concept's `description`) and `log.md`
  (newest first, date headings as `## YYYY-MM-DD`).
- When creating a new bundle: a root `index.md` is REQUIRED; `log.md` is
  strongly recommended. Declare `okf_version: "0.2"` in the root `index.md`
  frontmatter when versioning matters (the only legal index frontmatter —
  spec §12).
- The spec makes both files optional; this policy makes them standard wherever
  concepts live, so every level of a deep bundle is self-describing.

## Index and Log Scoping (same-level rule)

An `index.md` or `log.md` references ONLY its own directory level. The problem
this prevents: top-level indexes accumulating entries for deeply nested files,
which defeats progressive disclosure and goes stale immediately — each
directory's scaffolding must carry its own content.

- Allowed link targets in `index.md`/`log.md`: same-directory concept files
  (`file.md`) and direct subdirectories (`subdir/`). External links
  (`https://…`, `mailto:…`) and pure anchors are exempt.
- FORBIDDEN in `index.md`/`log.md`: nested paths (`subdir/file.md`), paths
  that climb out (`../file.md`), and bundle-absolute paths (`/path/file.md`) —
  use the relative form instead. (Bundle-absolute links remain the recommended
  form for cross-linking in CONCEPT documents; the restriction applies to
  index/log files only.)
- Bidirectional completeness for `index.md`: every concept file in the
  directory MUST be listed, every direct subdirectory MUST be listed (as
  `subdir/`), and every entry MUST point at an existing target — no dead
  entries. Hidden entries (dotfiles/dot-directories) are exempt.
- `log.md` completeness is NOT checked — a log records changes, not an
  inventory. Dead links in `log.md` only WARN: history may legitimately
  reference since-renamed or removed files.

## Validator Policy

| Check | Level | Label |
|-------|-------|-------|
| File not valid UTF-8 | ERROR | `[SPEC]` |
| Missing/unparseable YAML frontmatter | ERROR | `[SPEC]` |
| Missing or empty `type` | ERROR | `[SPEC]` |
| `log.md` without `## YYYY-MM-DD` date headings | ERROR | `[SPEC]` (spec §9: "MUST") |
| Missing `title` / `description` / `tags` | WARN | `[SPEC]` |
| `timestamp` present (with or without `generated`) | WARN | `[HOUSE]` |
| `generated` present without `by` | ERROR | `[SPEC]` (spec §5.2) |
| `generated.at`/`verified[].at`/`stale_after` not valid ISO 8601 | ERROR | `[SPEC]` |
| ISO 8601 datetime without explicit UTC offset | WARN | `[HOUSE]` |
| `by`-fields not matching actor convention | WARN | `[HOUSE]` |
| Unknown `status` value | WARN | `[HOUSE]` |
| `sources` entry without `resource` | ERROR | `[SPEC]` (spec §5.1) |
| Footnote `[^id]` without matching `sources[].id` | WARN | `[HOUSE]` |
| Root index `okf_version: "0.1"` while bundle uses v0.2 families | WARN | `[HOUSE]` |
| Frontmatter in reserved files (other than root `index.md` with only `okf_version`) | WARN | `[SPEC]` |
| `index.md` without section headings | WARN | `[SPEC]` (spec §8 structure) |
| Filename not lowercase-kebab-case | ERROR | `[HOUSE]` |
| Empty body | ERROR | `[HOUSE]` |
| No H1 heading in body | WARN | `[HOUSE]` |
| `index.md`/`log.md` link crosses the directory level (nested, escaping, or bundle-absolute) | ERROR | `[HOUSE]` |
| `index.md` entry points at a non-existing target (dead entry) | ERROR | `[HOUSE]` |
| `log.md` link points at a non-existing target (may be legitimate history) | WARN | `[HOUSE]` |
| `index.md` does not list every concept file / every direct subdirectory | ERROR | `[HOUSE]` |
| Directory with concept files lacks `index.md` | ERROR | `[HOUSE]` |
| Directory with concept files lacks `log.md` | WARN | `[HOUSE]` |
| Reserved file starts with a YAML-looking line (frontmatter without `---` delimiters) | WARN | `[HOUSE]` |

The validator runs recursively in directory mode: one invocation over the
bundle root validates every `.md` file AND applies the directory checks to
every directory holding `.md` content — no per-directory runs needed. Output
carries line numbers and check names; `--json` produces machine-readable
output for agents.

A document is done when it passes all ERROR checks and the author has
consciously accepted or fixed every WARN.
