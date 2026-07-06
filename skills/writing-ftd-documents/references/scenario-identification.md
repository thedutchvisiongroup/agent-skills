# Scenario Identification & Toggle Matrix

## Contents
- Decision criteria
- Toggle matrix (which sections are mandatory per scenario)
- Feature flexibility († and ‡ rules)
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

## Toggle matrix

Legend: **M** = mandatory, **O** = optional (recommended), **—** = not required, **E** = enterprise-only mandatory.

| Section | feature | project | enterprise |
|---------|---------|---------|------------|
| Title / version / revision history | M | M | M |
| Executive summary | — | M | M |
| Scope & objectives (in/out, success criteria) | M | M | M |
| Stakeholders & RACI | — | M | M |
| Business context & goals | O | M | M |
| Benefit hypothesis | O | M | M |
| User stories (INVEST-checked) | M | M | M |
| Acceptance criteria (bullets or EARS) | M | M | M |
| Traceability matrix | O† | M | M |
| Definition of Ready / Definition of Done | M‡ | M | M |
| Architecture — C4 Context (L1) | O† | M | M |
| Architecture — C4 Container (L2) | O | M | M |
| Architecture — C4 Component (L3) | — | O | M |
| Sequence diagrams (key flows) | O | M | M |
| Data model (ERD) | O | M | M |
| API summary (inline + OpenAPI ref) | O | M | M |
| Integration & data flows | — | O | M |
| NFRs (ISO 25010, measurable) | O† | M | M |
| Privacy-by-design section | M | M | M |
| Security-by-design section | M | M | M |
| Risk register | — | M | M |
| Deployment & rollback plan | O | M | M |
| Observability & logging plan | — | O | M |
| DPIA decision (Y/N + reference) | O | O | E |
| Threat model (STRIDE + LINDDUN) | — | O | E |
| Compliance evidence (BIO/NEN 7510/ISO 27001) | — | — | E |
| SBOM reference | — | — | E |
| Accessibility audit (WCAG 2.1 AA) | — | O | M |
| Migration & runbook | — | O | M |
| Backwards compatibility notes | O | M | M |
| Glossary | O | M | M |
| Crosscutting Concepts | O | O | M |
| Approvals & sign-off | M | M | M |

**† Feature flexibility:** in the `feature` scenario, the agent MAY drop or condense optional sections marked with † (traceability matrix, C4 Context, NFRs) for trivial single-story features with no performance, security, or data impact — based on the agent's judgement of the feature's complexity. When in doubt, keep the section.

**‡ DoD is ALWAYS mandatory,** regardless of feature size or complexity. DoR follows the same rule. PbD and SbD are also always mandatory and never optional.

## Conflict resolution

If the user's stated scenario conflicts with the criteria (e.g. they say "feature" but the work touches regulated data or multiple teams):

1. Surface the conflict explicitly: "You said feature, but I see [evidence] which puts this in the project/enterprise tier."
2. Propose the higher tier with justification.
3. If the user insists on the lower tier, accept their decision BUT record the deviation in the FTD's revision history as "scope downgrade — risk accepted by [user]".
4. Never silently upgrade or downgrade.

## Scenario-conditional rules

- **feature**: no sign-off gate in Phase 1. Condensed template. Risk register replaced with "impacted teams" note. The agent MAY drop optional sections († in toggle matrix) for trivial single-story features with no performance, security, or data impact. **DoD, DoR, PbD, SbD, scope, user stories, acceptance criteria, and approvals are always mandatory and never dropped.** Benefit hypothesis optional but recommended if the feature has a measurable outcome.
- **project**: sign-off gate (Scope Summary) mandatory. Full template. arc42 design decisions section added. Glossary mandatory. Benefit hypothesis mandatory and measurable.
- **enterprise**: sign-off gate mandatory. Full template + all enterprise-only (E) sections. DPIA, threat model, and compliance evidence are non-negotiable. Glossary and Crosscutting Concepts mandatory. Benefit hypothesis mandatory and measurable.
