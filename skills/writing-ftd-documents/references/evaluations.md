# Evaluations

## Contents
- How to use these scenarios
- Scenario 1: small feature
- Scenario 2: full project
- Scenario 3: enterprise (compliance-heavy)
- Scenario 4: feature-level with EARS and section flexibility
- Scenario 5: audit of an existing FTD
- Scenario 6: restructure a legacy design document
- Scenario 7: ceiling-model discipline (no bloat, justified omissions)
- Cross-scenario checks

## How to use these scenarios

These seven scenarios test the skill against representative inputs. Run the skill from a fresh context with each scenario's input and check the expected behaviors. A failure on any expected behavior indicates a skill gap to fix.

The FIRST expected behavior in every drafting scenario is correct workflow and scenario identification — the skill must identify whether the user wants to draft or review/restructure, then classify the input as feature, project, or enterprise before any intake questions.

Remember the ceiling model while evaluating: the goal is never a complete template, the goal is a complete *core* plus justified additions. Over-production is as much a failure as under-production.

## Scenario 1: small feature

**Input (simulated user message):**
> "I need an FTD for a new 'export to CSV' button on the orders page. It's just one button, calls an existing service, and downloads the visible orders. Small change."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft** (no existing document provided), identifies as **feature** (one story, one component, one team, low risk)
- Phase 1: asks the five mandatory output questions (split, language, mode, AC format, filename) — does NOT require a Scope Summary sign-off
- Phase 1: still probes key details (which columns, max row count, permissions, what happens on empty result)
- Phase 2: produces the **core** (document control with OKF frontmatter, TOC, scope, user stories, acceptance criteria + `ac-format` marker, DoD, PbD, SbD) — concise, within the ~150-line feature budget
- Phase 2: includes only recommended sections that earn their place (e.g. one-line approvals); every omitted recommended section (architecture, traceability matrix, NFRs) has a one-line justification in "Omitted sections & open questions"
- Phase 2: privacy-by-design present and concise (e.g. "no new personal data beyond existing — because…"); security-by-design present (auth on the export endpoint)
- Phase 3: runs `validate.py --scenario feature` — passes with zero or only justified-omission notes; does NOT pad sections to satisfy the validator
- Phase 3: invokes `writing-okf` and runs the OKF validator

**Failure signals:**
- Skipped Phase 0 workflow identification (draft vs review)
- Skipped Phase 0 scenario identification and went straight to drafting
- Did not ask the AC format question (question 4)
- Skipped privacy/security sections ("it's just a button")
- Used the full project template (over-engineered) — the most common regression
- Produced sections without justification and no "Omitted sections & open questions"
- Padded PbD/SbD with boilerplate to look "complete"
- Dropped DoD because "it's just one feature"
- Missing OKF frontmatter, or writing-okf never invoked

## Scenario 2: full project

**Input (simulated user message):**
> "We're building a new invoice approval workflow. Three teams involved: finance, IT, and an external supplier who builds the mobile app. Replaces the current email-based process. Goes live Q1 next year."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft**, identifies as **project** (multiple stories, cross-team, external supplier, moderate risk, multi-quarter)
- Phase 1: runs the full intake (scope, functional, technical, output) — keeps probing until each dimension is clear
- Phase 1: asks the five mandatory output questions; proposes combined FTD (single supplier boundary not multiple) but lets user decide
- Phase 1: produces a Scope Summary and **requires explicit sign-off** before drafting
- Phase 1: hard refusal if the user refuses to answer scope questions
- Phase 2: core complete; recommended defaults included **because they earn their place here** (executive summary, stakeholders/RACI, benefit hypothesis, traceability, architecture C4 L1+L2, measurable NFRs, risk register, deployment, glossary) — or justified-away in "Omitted sections & open questions"
- Phase 2: benefit hypothesis measurable (business outcome + user outcome + validation method + baseline + target)
- Phase 2: privacy-by-design includes data inventory (approvers, invoices may contain supplier data) and DPIA decision
- Phase 2: security-by-design includes auth (MFA for approvers), audit logging, ASVS level
- Phase 2: OKF frontmatter present; document stays within the ~400-line project budget
- Phase 3: runs `validate.py --scenario project` — errors fixed, warnings resolved via inclusion or recorded justification

**Failure signals:**
- Skipped the Scope Summary sign-off gate
- Did not probe whether the external supplier affects the FSD/TSD split decision
- Used the feature core only (under-scoped)
- Included sections mechanically without any earning-their-place reasoning — or omitted recommended sections silently
- Benefit hypothesis missing without a recorded justification
- NFRs not measurable ("should be fast")
- Document blows past the ~400-line budget without a trim/split discussion

## Scenario 3: enterprise (compliance-heavy)

**Input (simulated user message):**
> "We're building a patient triage assistant for a Dutch hospital network. Uses an LLM to suggest priority levels based on symptoms. Must comply with NEN 7510. Goes to 5 hospitals. Patient data is involved."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft**, identifies as **enterprise** (org-wide, NEN 7510, patient data, multiple hospitals, AI component)
- Phase 1: full intake; probes AI Act classification (high-risk AI likely), DPIA triggers (special category health data → mandatory DPIA)
- Phase 1: asks the five mandatory output questions; proposes **SPLIT** (FSD + TSD) due to compliance traceability and multiple stakeholders — user decides
- Phase 1: Scope Summary mandatory with explicit sign-off
- Phase 2: produces a **multi-file bundle** (`FTD-[project]/`) with OKF `index.md` (+ `log.md`), each file with OKF frontmatter; global section numbering
- Phase 2: all enterprise-required (E) sections present:
  - DPIA decision and reference
  - Threat model (STRIDE + LINDDUN)
  - Compliance evidence (NEN 7510 mapping, EU AI Act high-risk obligations — only the frameworks that apply)
  - SBOM reference
  - Measurable NFRs
- Phase 2: privacy-by-design includes data inventory with special categories, DPIA, DSR flow, retention, pseudonymisation
- Phase 2: security-by-design includes ASVS L3, full threat model, audit logging, incident response
- Phase 2: C4 L1+L2 (+L3 where it earns its place)
- Phase 3: runs `validate.py --scenario enterprise` per bundle file; all errors fixed
- Phase 3: OKF validator passes on the bundle

**Failure signals:**
- Did not identify the workflow as draft vs review/restructure
- Did not flag the AI Act classification
- Skipped DPIA despite health data (special category)
- Did not propose a split for compliance traceability
- Missing NEN 7510 mapping in compliance evidence
- Produced a single 23-section mega-file instead of an indexed bundle
- Missing OKF `index.md`, or files without frontmatter
- Threat model missing or only STRIDE (LINDDUN also required for privacy threats)
- Demanding ALL framework headings (BIO for a hospital, NEN 7510 for a ministry) — only applicable frameworks are required

## Scenario 4: feature-level with EARS and section flexibility

**Input (simulated user message):**
> "I need an FTD for adding rate limiting to our public API. It's one endpoint group (/api/v1/*), one team, no new data. But it does have a performance impact and we want formal requirements because it's going to be audited. Use EARS notation. Output in Dutch."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft**, identifies as **feature** (one story cluster, one team, low risk, one component)
- Phase 1: asks the five mandatory output questions — user already answered AC format (EARS) and language (Dutch), agent confirms and asks the remaining three (split, mode, filename)
- Phase 1: probes performance impact (target RPS, burst behaviour, 429 vs 503 response), security impact (does rate limit leak user identity?)
- Phase 2: agent JUDGES that this feature has performance impact → includes measurable NFRs (they earn their place); keeps architecture (security boundary change) and traceability matrix; other recommended sections omitted with justification
- Phase 2: DoD stays mandatory; PbD/SbD stay mandatory (rate limiting may leak user identity via timing)
- Phase 2: acceptance criteria written in **EARS notation, Dutch** ("Wanneer een client de limiet overschrijdt, zal het systeem HTTP 429 teruggeven met een Retry-After-header") with the `<!-- ac-format: ears -->` marker
- Phase 2: benefit hypothesis included because the user mentioned audit (measurable outcome helps audit) — or omitted with a recorded reason
- Phase 3: runs `validate.py --scenario feature` and passes; validator recognises EARS via the marker

**Failure signals:**
- Used bullets instead of EARS despite user's explicit choice
- Dropped NFRs because "feature allows it" — the agent should keep them because there IS performance impact
- Skipped PbD/SbD ("no new data" is not the same as "no privacy implications")
- Did not confirm the AC format choice even though user stated it (must still ask the mandatory question)
- Mixed EARS and bullets in the same document
- Wrote Dutch EARS as English-keyword hybrids ("Wanneer …, the system shall …") instead of full Dutch with "zal"
- Missing the `ac-format` marker comment

## Scenario 5: audit of an existing FTD

**Input (simulated user message):**
> "Here's our current FTD for the customer portal redesign. Can you review it and tell me what's missing or could be better? [attaches FTD-CustomerPortal-v2.1.md]"

**Expected behaviors:**
- Phase 0: identifies workflow as **review/restructure**, mode **A: Audit** (user said "review" and "tell me what's missing")
- Phase R clarification gate: asks only mandatory questions for audit mode (mode + source document); does NOT ask split/language/mode/filename (audit is report-only)
- Reads the source document in full
- Runs `python scripts/validate.py <source> --scenario <detected> --audit` to get the automated gap report
- Detects scenario from the document content (likely project based on the described scope)
- Performs manual review against the toggle table: per core section — present / missing / thin; per recommended section — present / justified omission (acceptable) / silent omission (finding)
- Checks quality: INVEST on user stories, NFR measurability (when present), PbD/SbD substantive, traceability orphans, diagram rendering, OKF frontmatter, size budget
- ALSO flags over-completeness: sections that do not earn their place (bloat is a finding too)
- Produces a **gap report** in the format from [review-workflow.md](review-workflow.md) Mode A: summary (core/recommended/required coverage, errors, warnings, justified omissions), findings by priority, next steps
- Does NOT modify the source document
- Offers to enter Restructure mode (Mode B) if the user wants the gaps fixed

**Failure signals:**
- Silently fixed issues in the source document (audit is report-only)
- Ran only the validator and stopped — manual quality checks are mandatory
- Skipped the clarification gate (mode confirmation is still required)
- Did not offer Restructure mode as a follow-up
- Report lacks prioritisation
- Reported justified omissions as defects (or failed to flag bloated sections)

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
- Drafts the new FTD using the template with the ceiling-model toggles, mapping extracted content and filling gaps from the intake — OKF frontmatter included, bundle form if enterprise
- Revision history: first entry "Restructured from [Confluence page name, date] by [agent] on [date]"
- Validates: runs `validate.py --scenario project` and fixes every error; resolves warnings via inclusion or recorded justification
- Delivers at the confirmed filename/location

**Failure signals:**
- Re-asked questions the source already answered (extract first, probe only gaps)
- Silently invented content for gaps without probing the user
- Discarded the source's existing content (user stories, architecture) instead of mapping it
- Skipped the clarification gate because "the source has the info" (gate confirms output decisions the source does not dictate)
- Missing "restructured from" entry in revision history
- Did not run the validator before delivery
- Kept every legacy section "because it was there" without checking it earns its place

## Scenario 7: ceiling-model discipline (no bloat, justified omissions)

**Input (simulated user message):**
> "Write an FTD for an internal reporting tool for our finance team. Two user stories, reuses our existing data warehouse and SSO, no personal data beyond employee names. It's maybe 3 sprints of work. Just give me what we need to start building."

**Expected behaviors:**
- Phase 0: identifies workflow as **draft**, identifies as **project** (multi-story, >2 sprints) — but LOW complexity
- Phase 1: asks the five mandatory output questions; Scope Summary sign-off (project scenario)
- Phase 2: produces core + only the recommended sections that earn their place. For example: architecture (one C4 Context), NFRs (one or two measurable rows), one-line approvals — and a populated "Omitted sections & open questions" listing e.g. risk register ("single team, no external dependencies"), observability ("reuses warehouse monitoring"), migration ("no migration"), glossary ("no domain-specific terms")
- Phase 2: document stays well within the ~400-line project budget — target ~150-250 lines
- Phase 3: validator passes; justified omissions shown as info, not warnings
- The agent can articulate WHY each included section earned its place

**Failure signals:**
- Produced a ~20-section document with boilerplate RACI, risk register, glossary etc. "because project scenario"
- Omitted recommended sections silently (no omissions section)
- Padded sections with filler text to look substantial
- Treated the validator's recommended-warnings as commands to add sections (the validator is advisory; justification is the alternative)

## Cross-scenario checks

Regardless of scenario, the skill must always:
- Identify the workflow (draft or review/restructure) before anything else
- For draft: run Phase 0 scenario identification before Phase 1
- Ask the five mandatory output questions (including AC format)
- Produce the ceiling-model core: document control (incl. OKF frontmatter), TOC, scope, user stories, acceptance criteria (+ marker), DoD, PbD, SbD
- Include privacy-by-design and security-by-design statements (never skip, even if "no personal data" — with justification; concise is fine)
- Include DoD explicitly (always mandatory, regardless of scenario or feature size)
- Make NFRs measurable whenever an NFR section is present (Subject/Attribute/Metric/Threshold/Verification)
- Record every omitted recommended section with a one-line reason in "Omitted sections & open questions"
- Invoke the `writing-okf` skill for the metadata layer; run the OKF validator
- Produce enterprise designs as an indexed multi-file bundle
- Respect the size budget, or consciously justify the breach to the user
- Refuse to draft if mandatory scope questions go unanswered
- Draft Markdown first if both MD+HTML requested
- Treat the validator as advisory: fix errors, resolve warnings, report suspected validator bugs instead of padding
- For audit mode: never modify the source document; produce a report only; flag bloat as well as gaps
- For restructure mode: preserve the source's revision history as the first entry
- For feature-structuring: DoD always mandatory, even for a single feature
- Respect the user's AC format choice (bullets or EARS) consistently throughout the document, with the `ac-format` marker
