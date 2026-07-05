# Evaluations

## Contents
- How to use these scenarios
- Scenario 1: small feature
- Scenario 2: full project
- Scenario 3: enterprise (compliance-heavy)

## How to use these scenarios

These three scenarios test the skill against representative inputs. Run the skill from a fresh context with each scenario's input and check the expected behaviors. A failure on any expected behavior indicates a skill gap to fix.

The FIRST expected behavior in every scenario is correct scenario identification — the skill must classify the input as feature, project, or enterprise before any intake questions.

## Scenario 1: small feature

**Input (simulated user message):**
> "I need an FTD for a new 'export to CSV' button on the orders page. It's just one button, calls an existing service, and downloads the visible orders. Small change."

**Expected behaviors:**
- Phase 0: identifies as **feature** (one story, one component, one team, low risk)
- Phase 1: asks the four mandatory output questions (split, language, mode, filename) — does NOT require a Scope Summary sign-off
- Phase 1: still probes key details (which columns, max row count, permissions, what happens on empty result)
- Phase 2: uses the condensed template (drops executive summary, stakeholders/RACI, risk register, observability)
- Phase 2: still includes privacy-by-design (likely "no personal data beyond existing — justification required") and security-by-design (auth on the export endpoint)
- Phase 2: includes traceability matrix, DoR/DoD, NFRs (measurable: e.g. "export of 10k rows completes < 5s")
- Phase 3: runs `validate.py --scenario feature` and passes

**Failure signals:**
- Skipped Phase 0 and went straight to drafting
- Skipped privacy/security sections ("it's just a button")
- Used the full project template (over-engineered)
- Required a sign-off gate (not applicable for feature)

## Scenario 2: full project

**Input (simulated user message):**
> "We're building a new invoice approval workflow. Three teams involved: finance, IT, and an external supplier who builds the mobile app. Replaces the current email-based process. Goes live Q1 next year."

**Expected behaviors:**
- Phase 0: identifies as **project** (multiple stories, cross-team, external supplier, moderate risk, multi-quarter)
- Phase 1: runs the full intake (scope, functional, technical, output) — keeps probing until each dimension is clear
- Phase 1: asks the four mandatory output questions; proposes combined FTD (single supplier boundary not multiple) but lets user decide
- Phase 1: produces a Scope Summary and **requires explicit sign-off** before drafting
- Phase 1: hard refusal if the user refuses to answer scope questions
- Phase 2: uses the full template (executive summary, stakeholders/RACI, risk register, observability, arc42 design decisions)
- Phase 2: C4 L1+L2 mandatory, L3 optional
- Phase 2: privacy-by-design includes data inventory (approvers, invoices may contain supplier data) and DPIA decision
- Phase 2: security-by-design includes auth (MFA for approvers), audit logging, ASVS level
- Phase 2: traceability matrix, DoR/DoD, measurable NFRs all present
- Phase 3: runs `validate.py --scenario project` and passes

**Failure signals:**
- Skipped the Scope Summary sign-off gate
- Did not probe whether the external supplier affects the FSD/TSD split decision
- Used the feature template (under-scoped)
- NFRs not measurable ("should be fast")

## Scenario 3: enterprise (compliance-heavy)

**Input (simulated user message):**
> "We're building a patient triage assistant for a Dutch hospital network. Uses an LLM to suggest priority levels based on symptoms. Must comply with NEN 7510. Goes to 5 hospitals. Patient data is involved."

**Expected behaviors:**
- Phase 0: identifies as **enterprise** (org-wide, NEN 7510, patient data, multiple hospitals, AI component)
- Phase 1: full intake; probes AI Act classification (high-risk AI likely), DPIA triggers (special category health data → mandatory DPIA)
- Phase 1: proposes **SPLIT** (FSD + TDD) due to compliance traceability and multiple stakeholders — user decides
- Phase 1: Scope Summary mandatory with explicit sign-off
- Phase 2: full template + all enterprise-only (E) sections:
  - DPIA decision and reference
  - Threat model (STRIDE + LINDDUN)
  - Compliance evidence (NEN 7510 mapping, EU AI Act high-risk obligations)
  - SBOM reference
  - WCAG 2.1 AA accessibility audit
  - Migration & runbook
- Phase 2: privacy-by-design includes data inventory with special categories, DPIA, DSR flow, retention, pseudonymisation
- Phase 2: security-by-design includes ASVS L3, full threat model, audit logging, incident response
- Phase 2: C4 L1+L2+L3 (component level mandatory for enterprise)
- Phase 3: runs `validate.py --scenario enterprise` and passes; checks that all E sections are present

**Failure signals:**
- Did not flag the AI Act classification
- Skipped DPIA despite health data (special category)
- Did not propose a split for compliance traceability
- Missing NEN 7510 mapping
- Used project-level template instead of enterprise (missing E sections)
- Threat model missing or only STRIDE (LINDDUN also required for privacy threats)

## Cross-scenario checks

Regardless of scenario, the skill must always:
- Run Phase 0 before Phase 1
- Ask the four mandatory output questions
- Include privacy-by-design and security-by-design sections (never skip, even if "no personal data")
- Include traceability matrix
- Include DoR/DoD explicitly
- Make NFRs measurable (Subject/Attribute/Metric/Threshold/Verification)
- Refuse to draft if mandatory scope questions go unanswered
- Draft Markdown first if both MD+HTML requested
