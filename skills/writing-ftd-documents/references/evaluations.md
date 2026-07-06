# Evaluations

## Contents
- How to use these scenarios
- Scenario 1: small feature
- Scenario 2: full project
- Scenario 3: enterprise (compliance-heavy)
- Scenario 4: feature-level with EARS and section flexibility
- Scenario 5: audit of an existing FTD
- Scenario 6: restructure a legacy design document
- Cross-scenario checks

## How to use these scenarios

These six scenarios test the skill against representative inputs. Run the skill from a fresh context with each scenario's input and check the expected behaviors. A failure on any expected behavior indicates a skill gap to fix.

The FIRST expected behavior in every drafting scenario is correct workflow and scenario identification — the skill must identify whether the user wants to draft or review/restructure, then classify the input as feature, project, or enterprise before any intake questions.

## Scenario 1: small feature

**Input (simulated user message):**
> "I need an FTD for a new 'export to CSV' button on the orders page. It's just one button, calls an existing service, and downloads the visible orders. Small change."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft** (no existing document provided), identifies as **feature** (one story, one component, one team, low risk)
- Phase 1: asks the five mandatory output questions (split, language, mode, AC format, filename) — does NOT require a Scope Summary sign-off
- Phase 1: still probes key details (which columns, max row count, permissions, what happens on empty result)
- Phase 2: uses the condensed template (drops executive summary, stakeholders/RACI, risk register, observability)
- Phase 2: agent MAY drop optional sections (C4 Context, NFRs, traceability) for this trivial feature, but DoD, PbD, SbD, scope, user stories, acceptance criteria, and approvals stay mandatory
- Phase 2: still includes privacy-by-design (likely "no personal data beyond existing — justification required") and security-by-design (auth on the export endpoint)
- Phase 2: includes DoR/DoD (DoD always mandatory), traceability matrix if retained, NFRs if retained (measurable: e.g. "export of 10k rows completes < 5s")
- Phase 3: runs `validate.py --scenario feature` and passes

**Failure signals:**
- Skipped Phase 0 workflow identification (draft vs review)
- Skipped Phase 0 scenario identification and went straight to drafting
- Did not ask the AC format question (question 4)
- Skipped privacy/security sections ("it's just a button")
- Used the full project template (over-engineered)
- Required a sign-off gate (not applicable for feature)
- Dropped DoD because "it's just one feature"

## Scenario 2: full project

**Input (simulated user message):**
> "We're building a new invoice approval workflow. Three teams involved: finance, IT, and an external supplier who builds the mobile app. Replaces the current email-based process. Goes live Q1 next year."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft**, identifies as **project** (multiple stories, cross-team, external supplier, moderate risk, multi-quarter)
- Phase 1: runs the full intake (scope, functional, technical, output) — keeps probing until each dimension is clear
- Phase 1: asks the five mandatory output questions; proposes combined FTD (single supplier boundary not multiple) but lets user decide
- Phase 1: produces a Scope Summary and **requires explicit sign-off** before drafting
- Phase 1: hard refusal if the user refuses to answer scope questions
- Phase 2: uses the full template (executive summary, stakeholders/RACI, risk register, observability, arc42 design decisions, glossary, benefit hypothesis)
- Phase 2: benefit hypothesis present and measurable (business outcome + user outcome + validation method + baseline + target)
- Phase 2: C4 L1+L2 mandatory, L3 optional
- Phase 2: privacy-by-design includes data inventory (approvers, invoices may contain supplier data) and DPIA decision
- Phase 2: security-by-design includes auth (MFA for approvers), audit logging, ASVS level
- Phase 2: traceability matrix, DoR/DoD (DoD always mandatory), measurable NFRs all present
- Phase 3: runs `validate.py --scenario project` and passes

**Failure signals:**
- Skipped the Scope Summary sign-off gate
- Did not probe whether the external supplier affects the FSD/TSD split decision
- Used the feature template (under-scoped)
- Missing benefit hypothesis (mandatory for project)
- Missing glossary (mandatory for project)
- NFRs not measurable ("should be fast")

## Scenario 3: enterprise (compliance-heavy)

**Input (simulated user message):**
> "We're building a patient triage assistant for a Dutch hospital network. Uses an LLM to suggest priority levels based on symptoms. Must comply with NEN 7510. Goes to 5 hospitals. Patient data is involved."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft**, identifies as **enterprise** (org-wide, NEN 7510, patient data, multiple hospitals, AI component)
- Phase 1: full intake; probes AI Act classification (high-risk AI likely), DPIA triggers (special category health data → mandatory DPIA)
- Phase 1: asks the five mandatory output questions; proposes **SPLIT** (FSD + TSD) due to compliance traceability and multiple stakeholders — user decides
- Phase 1: Scope Summary mandatory with explicit sign-off
- Phase 2: full template + all enterprise-only (E) sections:
  - DPIA decision and reference
  - Threat model (STRIDE + LINDDUN)
  - Compliance evidence (NEN 7510 mapping, EU AI Act high-risk obligations)
  - SBOM reference
  - WCAG 2.1 AA accessibility audit
  - Migration & runbook
  - Glossary (mandatory)
  - Crosscutting Concepts (mandatory)
  - Benefit hypothesis (mandatory and measurable)
- Phase 2: privacy-by-design includes data inventory with special categories, DPIA, DSR flow, retention, pseudonymisation
- Phase 2: security-by-design includes ASVS L3, full threat model, audit logging, incident response
- Phase 2: C4 L1+L2+L3 (component level mandatory for enterprise)
- Phase 3: runs `validate.py --scenario enterprise` and passes; checks that all E sections are present

**Failure signals:**
- Did not identify the workflow as draft vs review/restructure
- Did not flag the AI Act classification
- Skipped DPIA despite health data (special category)
- Did not propose a split for compliance traceability
- Missing NEN 7510 mapping
- Missing glossary or Crosscutting Concepts (both mandatory for enterprise)
- Missing benefit hypothesis (mandatory for enterprise)
- Used project-level template instead of enterprise (missing E sections)
- Threat model missing or only STRIDE (LINDDUN also required for privacy threats)

## Scenario 4: feature-level with EARS and section flexibility

**Input (simulated user message):**
> "I need an FTD for adding rate limiting to our public API. It's one endpoint group (/api/v1/*), one team, no new data. But it does have a performance impact and we want formal requirements because it's going to be audited. Use EARS notation. Output in Dutch."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft**, identifies as **feature** (one story cluster, one team, low risk, one component)
- Phase 1: asks the five mandatory output questions — user already answered AC format (EARS) and language (Dutch), agent confirms and asks the remaining three (split, mode, filename)
- Phase 1: probes performance impact (target RPS, burst behaviour, 429 vs 503 response), security impact (does rate limit leak user identity?)
- Phase 2: agent JUDGES that this feature has performance impact → keeps NFRs (measurable) even though feature allows dropping them; keeps C4 Context (security boundary change); keeps traceability matrix
- Phase 2: DoD stays mandatory; PbD/SbD stay mandatory (rate limiting may leak user identity via timing)
- Phase 2: acceptance criteria written in **EARS notation** (event-driven: "When a client exceeds the rate limit, the system shall return HTTP 429 with a Retry-After header"), Dutch language
- Phase 2: benefit hypothesis optional but agent includes it because the user mentioned audit (measurable outcome helps audit)
- Phase 3: runs `validate.py --scenario feature` and passes; validator recognises EARS format
- Phase 3: HTML output in Dutch (if both modes requested)

**Failure signals:**
- Used bullets instead of EARS despite user's explicit choice
- Dropped NFRs because "feature allows it" — the agent should keep them because there IS performance impact
- Skipped PbD/SbD ("no new data" is not the same as "no privacy implications")
- Did not confirm the AC format choice even though user stated it (must still ask the mandatory question)
- Mixed EARS and bullets in the same document

## Scenario 5: audit of an existing FTD

**Input (simulated user message):**
> "Here's our current FTD for the customer portal redesign. Can you review it and tell me what's missing or could be better? [attaches FTD-CustomerPortal-v2.1.md]"

**Expected behaviors:**
- Phase 0: identifies workflow as **review/restructure**, mode **A: Audit** (user said "review" and "tell me what's missing")
- Phase R clarification gate: asks only mandatory questions for audit mode (mode + source document); does NOT ask split/language/mode/filename (audit is report-only)
- Reads the source document in full
- Runs `python scripts/validate.py <source> --scenario <detected> --audit` to get the automated gap report
- Detects scenario from the document content (likely project based on the described scope)
- Performs manual review against the toggle matrix: per mandatory section — present / missing / incomplete / boilerplate
- Checks quality: INVEST on user stories, NFR measurability, PbD/SbD populated (not boilerplate), traceability orphans, diagram rendering, benefit hypothesis (project), glossary (project)
- Produces a **gap report** in the format from [review-workflow.md](review-workflow.md) Mode A: summary, findings by priority (Critical / Important / Nice-to-have), next steps
- Does NOT modify the source document
- Offers to enter Restructure mode (Mode B) if the user wants the gaps fixed

**Failure signals:**
- Silently fixed issues in the source document (audit is report-only)
- Ran only the validator and stopped — manual quality checks are mandatory
- Skipped the clarification gate (mode confirmation is still required)
- Did not offer Restructure mode as a follow-up
- Report lacks prioritisation (Critical / Important / Nice-to-have)

## Scenario 6: restructure a legacy design document

**Input (simulated user message):**
> "We have an old Confluence page that describes our payment module design — it's a mix of user stories, some architecture sketches, and a bunch of prose. Can you turn it into a proper FTD? [pastes content or provides URL]"

**Expected behaviors:**
- Phase 0: identifies workflow as **review/restructure**, mode **B: Restructure** (user said "turn it into a proper FTD")
- Phase R clarification gate: asks all mandatory questions (mode confirmed, scenario, output language, output mode, AC format, filename)
- Reads the source content in full
- Identifies that the source is a legacy design doc, not an FTD — maps to scenario (likely project based on payment module scope)
- Extracts content per dimension: scope (in/out), functional (user stories embedded in prose), technical (architecture sketches, integrations), output (from gate)
- Identifies gaps: missing PbD/SbD, NFRs stated as "fast" without thresholds, no traceability matrix, no DoR/DoD, no benefit hypothesis, no glossary
- Runs Phase 1 intake ONLY for the gaps — does not re-ask what the source already answers (e.g. user stories are in the prose, just need formalising)
- Drafts the new FTD using the full template with project toggles, mapping extracted content and filling gaps from the intake
- Revision history: first entry "Restructured from [Confluence page name, date] by [agent] on [date]"
- Validates: runs `validate.py --scenario project` and fixes every error
- Delivers at the confirmed filename/location

**Failure signals:**
- Re-asked questions the source already answered (extract first, probe only gaps)
- Silently invented content for gaps without probing the user
- Discarded the source's existing content (user stories, architecture) instead of mapping it
- Skipped the clarification gate because "the source has the info" (gate confirms output decisions the source does not dictate)
- Missing "restructured from" entry in revision history
- Did not run the validator before delivery

## Cross-scenario checks

Regardless of scenario, the skill must always:
- Identify the workflow (draft or review/restructure) before anything else
- For draft: run Phase 0 scenario identification before Phase 1
- Ask the five mandatory output questions (including AC format)
- Include privacy-by-design and security-by-design sections (never skip, even if "no personal data")
- Include DoD explicitly (always mandatory, regardless of scenario or feature size)
- Make NFRs measurable (Subject/Attribute/Metric/Threshold/Verification)
- Refuse to draft if mandatory scope questions go unanswered
- Draft Markdown first if both MD+HTML requested
- For audit mode: never modify the source document; produce a report only
- For restructure mode: preserve the source's revision history as the first entry
- For feature-structuring: DoD always mandatory, even for a single feature
- Respect the user's AC format choice (bullets or EARS) consistently throughout the document
