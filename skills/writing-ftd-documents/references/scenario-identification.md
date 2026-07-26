# Scenario Identification & Toggle Table

## Contents
- Decision criteria
- The ceiling model: core / recommended / enterprise-required
- Toggle table
- Size budgets
- The omissions convention
- Conflict resolution
- Scenario-conditional rules

## Decision criteria

### feature
Use when ALL of:
- One user story, or a tightly-coupled handful (≤5) sharing one component
- One component or service touched
- One team owns the change end-to-end
- Low risk: no regulatory exposure, no data migration, no supplier boundary
- Estimated effort ≤ 2 sprints

### project
Use when ANY of:
- Multiple stories or epics spanning components
- Cross-team or single external supplier involved
- Moderate risk: data migration, performance impact, or minor regulatory exposure
- Estimated effort > 2 sprints

### enterprise
Use when ANY of:
- Org-wide impact or multiple business units
- Regulatory exposure: AVG/DPIA triggers, NEN 7510 (healthcare), BIO (government), ISO 27001 certified scope
- Multiple external suppliers or procurement constraints
- High cost (>€250k) or high reputational risk
- AI component classified as high-risk under EU AI Act

## The ceiling model: core / recommended / enterprise-required

Every section falls in exactly one of three classes:

| Class | Meaning | If missing |
|-------|---------|------------|
| **Core (C)** | Mandatory in every scenario. | ERROR — the FTD is incomplete. |
| **Recommended (R)** | Default-included for the scenario. MAY be omitted when the omission is justified (one line) in "Omitted sections & open questions". | WARNING unless justified. |
| **Enterprise-required (E)** | Mandatory for enterprise only — choosing enterprise means opting into compliance rigour. | ERROR for enterprise; n/a otherwise. |

The ceiling model inverts the old floor model: you do not start from "everything is mandatory unless dropped" but from the core, and every additional section must earn its place. **If you cannot write one sentence on why a section is needed for THIS design, omit it and record the omission.**

## Toggle table

| Section | feature | project | enterprise |
|---------|---------|---------|------------|
| Document control (incl. OKF frontmatter) | C | C | C |
| Table of contents | C | C | C (index.md) |
| Scope & objectives (in/out, success criteria) | C | C | C |
| User stories (INVEST-checked) | C | C | C |
| Acceptance criteria (bullets or EARS + marker) | C | C | C |
| Definition of Done | C | C | C |
| Privacy-by-design statement | C | C | C |
| Security-by-design statement | C | C | C |
| Omitted sections & open questions | R | R | R |
| Definition of Ready | R | R | R |
| Approvals (feature: one-line "Akkoord") | R | R | R |
| Executive summary | — | R | R |
| Stakeholders & RACI | — | R | R |
| Business context & goals | — | R | R |
| Benefit hypothesis (measurable) | — | R | R |
| Traceability matrix | R | R | R |
| Architecture (C4 L1/L2, ADR-style decisions) | R | R | R |
| Architecture (C4 L3 component) | — | R | R |
| Sequence diagrams (key flows) | R | R | R |
| Data model (ERD) | R | R | R |
| API & integration | R | R | R |
| Non-functional requirements (measurable) | R | R | E |
| Risk register | — | R | R |
| Deployment & rollback | R | R | R |
| Observability & logging | — | R | R |
| Migration & runbook | — | R | R |
| Glossary | — | R | R |
| Crosscutting Concepts | — | R | R |
| DPIA decision + reference | — | R | E |
| Threat model (STRIDE + LINDDUN) | — | R | E |
| Compliance evidence (BIO/NEN 7510/ISO 27001/AI Act) | — | — | E |
| SBOM reference | — | — | E |
| Accessibility audit (WCAG 2.1 AA) | — | R | R |

Legend: **C** = core (always mandatory), **R** = recommended (include or justify omission), **E** = enterprise-required, **—** = not expected (may still be included when it earns its place).

## Size budgets

The budget is a WARNING threshold, not a failure — exceeding it triggers a conscious trim-or-split review with the user.

| Scenario | Budget | Form | Rationale |
|----------|--------|------|-----------|
| feature | ≤ ~150 lines | single file | A feature doc that needs more is usually an under-scoped project |
| project | ≤ ~400 lines | single file | Roughly the ~10-page ceiling practitioners recommend for complex designs |
| enterprise | ≤ ~800 lines **per file** | multi-file bundle with OKF index | Humans review per part; agents load only the relevant slice |

When a project document keeps growing past its budget, prefer **splitting by concern** over trimming substance: move e.g. the threat model or the migration runbook into a sibling file referenced from the main FTD. An FTD may always decompose into a bundle when size demands it — the bundle form is mandatory only for enterprise.

## The omissions convention

Every FTD contains (when anything is omitted or open) a section:

```markdown
## Omitted sections & open questions
(NL: ## Weggelaten secties & open punten)

- Architecture — omitted: no new components; change reuses the existing export service.
- NFRs — omitted: no performance/security impact; inherits system-level NFRs (see [ref]).
- Open question: max export size unknown — PO to confirm by [date].
```

Rules:
- One line per omitted recommended section: **what + why**.
- Open doubts go here too — never resolve doubt by padding a section.
- The validator reads this section and treats justified omissions as satisfied.

## Conflict resolution

If the user's stated scenario conflicts with the criteria (e.g. they say "feature" but the work touches regulated data or multiple teams):

1. Surface the conflict explicitly: "You said feature, but I see [evidence] which puts this in the project/enterprise tier."
2. Propose the higher tier with justification.
3. If the user insists on the lower tier, accept their decision BUT record the deviation in the FTD's revision history as "scope downgrade — risk accepted by [user]".
4. Never silently upgrade or downgrade.

## Scenario-conditional rules

- **feature**: no sign-off gate in Phase 1. Single file, ≤ ~150 lines. Core + only what earns its place. Approvals collapse to one line. DoR optional (the intake gate largely covers it). PbD/SbD always present, concise.
- **project**: sign-off gate (Scope Summary) mandatory. Single file, ≤ ~400 lines. Recommended defaults included or justified-away. Benefit hypothesis and glossary strongly expected — omit only with a good reason.
- **enterprise**: sign-off gate mandatory. **Multi-file bundle** with OKF `index.md` (+ `log.md`), ≤ ~800 lines per file. Enterprise-required sections are non-negotiable: DPIA decision, threat model, compliance evidence, SBOM, measurable NFRs. Which compliance frameworks apply (NEN 7510 / BIO / ISO 27001 / AI Act) is documented inside Compliance evidence — not every framework heading is mandatory.
