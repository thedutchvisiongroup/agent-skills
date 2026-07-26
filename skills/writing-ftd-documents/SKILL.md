---
name: writing-ftd-documents
description: Drafts, reviews, and restructures right-sized Functional Technical Design (FTD) documents using a ceiling model — a small mandatory core plus only justified additions. Use when writing or reviewing an FTD, FSD, TSD, functioneel/technisch ontwerp (FO/TO), SDD, or system design document — feature, project, or enterprise. Enforces scope clarification before drafting; adds OKF metadata via the writing-okf skill so documents serve humans and agents; splits enterprise designs into indexed multi-file bundles; optional self-contained HTML output; privacy- and security-by-design always present.
---

# Writing FTD Documents

Author, review, and restructure Functional Technical Design (FTD) documents that are **concrete without being overkill**. The default output is **Markdown** (OKF-frontmatter + Mermaid diagrams + numbered headings + TOC). An extended **self-contained HTML** mode produces one portable file for human presentation. Both modes are always offered; the user always chooses.

This skill supports two top-level workflows:
- **Draft** (Phase 0 → 1 → 2 → 3 → 4): create a new FTD from scratch.
- **Review & Restructure** (Phase R): audit, improve, or restructure an existing FTD, legacy design document, or loose feature description. See [references/review-workflow.md](references/review-workflow.md).

## The Ceiling Principle (core design rule)

**Every section must earn its place.** Research and practice agree: documents that try to be complete stop being read and stop being maintained. This skill therefore uses a **ceiling model**, not a floor model:

1. **The core is always mandatory** — a small set of sections every FTD needs, regardless of scenario:
   - Document control (with OKF frontmatter)
   - Scope & objectives (in/out + success criteria)
   - User stories (INVEST-checked)
   - Acceptance criteria (bullets or EARS)
   - Definition of Done (always; DoR is recommended)
   - Privacy-by-design statement (always — even if "no personal data", with justification)
   - Security-by-design statement (always — even if minimal exposure, with justification)
2. **Everything else is default-included per scenario, but omittable with a one-line justification.** See the toggle table in [references/scenario-identification.md](references/scenario-identification.md). If you cannot write one sentence on why a section is needed for THIS design, drop it.
3. **Omissions are recorded, never silent.** Every dropped recommended section gets one line in the document's **"Omitted sections & open questions"** section (NL: "Weggelaten secties & open punten"). Doubts and open points go there too — do not resolve doubt by padding.
4. **When in doubt, leave it out — and note the doubt.** This supersedes any "when in doubt, keep it" instinct. An open question in the omissions section is more valuable than a speculative section.
5. **Size budgets are enforced as warnings.** See the budget table below. Bigger is not better; a budget breach triggers a trim-or-split review, not failure.

| Scenario | Size budget | Form |
|----------|------------|------|
| feature | ≤ ~150 lines | single file |
| project | ≤ ~400 lines | single file |
| enterprise | ≤ ~800 lines per file | **multi-file bundle** (see Phase 2) |

## Iron Law

**You MUST complete the clarification gate before drafting or restructuring any FTD. NO EXCEPTIONS.**

Premature drafting produces designs that miss scope, omit stakeholders, under-specify non-functional requirements, or skip privacy/security implications. An FTD written on insufficient scope is worse than no FTD — it creates false confidence.

```
STOP. Before drafting or restructuring any FTD:
- [ ] I identified the workflow (Draft or Review/Restructure) — see below
- [ ] I identified the scenario (feature / project / enterprise) — Phase 0
- [ ] I completed the intake conversation until scope is fully clear — Phase 1
- [ ] For project/enterprise: I produced a Scope Summary and got explicit sign-off
- [ ] I asked the five mandatory output questions (split, language, mode, AC format, filename)
- [ ] The user answered the mandatory scope questions
If any box is unchecked: GO BACK. Do not draft.
```

### Hard refusal

If the user refuses to answer mandatory scope questions after being asked clearly, **you MUST refuse to draft the FTD**. Explain why scope clarity is non-negotiable and offer to resume when they can provide it. Never produce an FTD on insufficient scope. Producing a wrong-but-complete document is failure, not professionalism.

## Scope of this skill

**In scope:** FTDs for software applications, data products, integration/migration projects, infrastructure and platform engineering, business-process automation. Functional and technical design combined or split.

**Out of scope:** Pure business cases, project plans, RFP/tender responses, marketing briefs. If the user asks for these, decline and point to the right artifact.

## Degrees of freedom

- **Low freedom** (mandatory, non-negotiable): the Iron Law, Phase 0 workflow and scenario identification, the five mandatory output questions, the ceiling-model core (incl. DoD, PbD, SbD always), the omissions convention, measurable NFRs whenever an NFR section is present, the OKF mandate (writing-okf invocation + frontmatter on every artifact), Markdown-first when both modes are requested.
- **High freedom** (adapt to context): which recommended sections to include (with justification), section ordering, depth per section, diagram choice, narrative tone, naming of artifacts, and the enterprise bundle's file mapping.

## Phase 0: Workflow & Scenario Identification (REQUIRED — FIRST STEP)

Before any intake questions, identify **which workflow** and **which scenario** applies. These two decisions drive every downstream toggle.

### Step 1: Workflow identification

Determine whether the user wants to **draft a new FTD** (Phase 1 → 4) or **review/restructure an existing document** (Phase R). The user provides or references an existing document — a Jira ticket, Confluence page, Word doc, legacy FTD — and asks to "review", "audit", "improve", "restructure", or "structure" it. If so, go to [Phase R](#phase-r-review--restructure) and read [references/review-workflow.md](references/review-workflow.md). Otherwise, continue with the draft workflow below.

### Step 2: Scenario identification

This single decision drives the size budget, the recommended-section defaults, and the enterprise-required sections.

| Scenario | When it applies | Sign-off gate | Budget | Form |
|----------|-----------------|---------------|--------|------|
| **feature** | One user story or a tightly-coupled handful; one component touched; low risk; one team | No | ≤ ~150 lines | single file |
| **project** | Multiple stories/epics; cross-component; multiple teams or external supplier; moderate risk | Yes (Scope Summary) | ≤ ~400 lines | single file |
| **enterprise** | Org-wide impact; regulatory exposure (AVG/NEN 7510/BIO/ISO 27001); multiple suppliers; high risk or high cost | Yes (Scope Summary) | ≤ ~800 lines/file | **bundle** |

**How to decide:** ask the user one framing question first — "Is this a small feature, a full project, or an enterprise-grade project?" — and verify their answer against the criteria above. If their answer conflicts with the criteria (e.g. they say "feature" but it touches multiple teams and regulated data), surface the conflict and propose the higher tier.

See [references/scenario-identification.md](references/scenario-identification.md) for the full core/recommended/required toggle table.

## Phase 1: Intake (REQUIRED — CLARIFICATION GATE)

The intake is a **free conversation**. Other skills may have already gathered context (research, codebase analysis, prior FTDs) — use that as input, do not re-ask what is already answered. Internally track four dimensions and keep probing until each is fully clear:

1. **Scope** — what is in, what is out, what is the boundary, what is the success criterion
2. **Functional** — who are the users/personas, what must the system do, what are the user stories, what is the business value
3. **Technical** — what is the existing architecture, what changes, what are the constraints (perf, security, compliance, budget, time), what integrations
4. **Output** — see the five mandatory questions below

Keep probing. Do not accept vague answers. If the user says "it should be fast", ask "what does fast mean — p95 latency target under which load?". If they say "secure", ask "against which threats, complying with which framework?".

### Five mandatory output questions

You MUST always ask these, regardless of scenario:

1. **FSD/TSD split vs combined FTD** — Should we produce two separate documents (functional + technical) or one combined FTD? You SHOULD propose a default based on scenario (see [references/split-decision.md](references/split-decision.md)): combined for feature, propose split for enterprise with multiple suppliers. **The user always decides.** (Note: an FSD/TSD split is by audience/approval flow; the enterprise multi-file bundle is by size. They are orthogonal and can combine.)
2. **Output language** — English (default: "As a…/I want…/So that…") or Dutch ("Als…/wil ik…/zodat…")?
3. **Output mode** — Markdown only, HTML only, or both? If both, Markdown is drafted first, then HTML is generated from it.
4. **Acceptance criteria format** — Simple bullet lists (default) or EARS notation? See [references/acceptance-criteria.md](references/acceptance-criteria.md). EARS is recommended for enterprise and regulated contexts where unambiguous requirement sentences are required. **The user always decides.**
5. **Filename and storage location** — Confirm filename convention (suggested: `FTD-[project]-[feature]-vX.Y.{md,html}`, or the bundle directory `FTD-[project]/` for enterprise) and where to save.

### Sign-off gate (project and enterprise only)

For project and enterprise scenarios, before exiting Phase 1 you MUST produce a **Scope Summary** — a concise recap of:
- Scenario and chosen size budget / form
- In-scope / out-of-scope
- Key user stories (titles only)
- Stakeholders and RACI owners
- Output decisions (split, language, mode, AC format, filename)
- Open assumptions (if any) marked explicitly

Present the Scope Summary to the user and require explicit approval before drafting. Do not begin Phase 2 without it.

For feature scenarios, no sign-off gate — proceed to drafting once scope is clear.

See [references/intake-questions.md](references/intake-questions.md) for the full question bank per dimension.

## Phase 2: Draft

Apply the master template with the ceiling-model toggles for the scenario. See [references/ftd-template.md](references/ftd-template.md).

**Non-negotiable in every draft, all scenarios:**

- **The ceiling-model core is complete** (see The Ceiling Principle). PbD and SbD statements are substantive but concise — a correct three-sentence "no personal data, because…" statement beats a padded page.
- **Recommended sections earn their place** — include the scenario defaults that matter for THIS design; record every omission with a one-line reason in "Omitted sections & open questions".
- **OKF frontmatter on every artifact.** You MUST invoke the `writing-okf` skill for the metadata layer: follow its conventions for `type` (reuse bundle types, or propose `FTD`), frontmatter fields, and — for bundles — `index.md`/`log.md` scaffolding. The frontmatter sits above the human-facing document control table; it does not replace it.
- **NFRs are measurable whenever present** — Subject / Attribute / Metric / Threshold / Verification per ISO/IEC 25010. See [references/nfr-taxonomy.md](references/nfr-taxonomy.md). An FTD without an NFR section is acceptable when justified; an NFR section without thresholds is never acceptable.
- **User stories in "As a…/I want…/So that…" (or Dutch equivalent) format, checked against INVEST.**
- **Acceptance criteria** as bullet lists (default) or EARS notation (per Phase 1 question 4), marked with an `<!-- ac-format: bullets|ears -->` comment. See [references/acceptance-criteria.md](references/acceptance-criteria.md).
- **Benefit hypothesis for project/enterprise** (default-included): "We believe [business outcome] will be achieved if [users] achieve [user outcome] with [feature]" — measurable target + validation method.
- **C4 diagrams via Mermaid** as the default architecture notation when an architecture section is included. See [references/mermaid-snippets.md](references/mermaid-snippets.md).
- **Numbered headings** (1, 1.1, 1.1.1) and **table of contents** at the top.

**Scenario-specific additions:**

- **feature:** core + only what earns its place. Approvals collapse to one line ("Akkoord: [PO], [date]"). DoR optional (the intake gate largely covers it).
- **project:** recommended defaults (executive summary, stakeholders/RACI, benefit hypothesis, traceability, architecture, NFRs, risk notes, deployment, glossary) — each included or justified-away.
- **enterprise:** all project defaults plus the enterprise-required set — DPIA decision, threat model (STRIDE + LINDDUN), compliance evidence (BIO/NEN 7510/ISO 27001/AI Act as applicable), SBOM reference, measurable NFRs. **Enterprise FTDs are produced as a multi-file bundle** so humans can review per part and agents can load only the relevant slice:

```
FTD-[project]/
├── index.md            # OKF index: 1-2 sentence summary + link per file (for humans AND agents)
├── log.md              # OKF change log (per writing-okf conventions)
├── 01-scope.md         # doc control, executive summary, scope, stakeholders, business context
├── 02-requirements.md  # user stories, acceptance criteria, traceability, DoR/DoD
├── 03-architecture.md  # C4, design decisions (ADR-style), data model, API & integration
├── 04-quality.md       # NFRs, privacy-by-design, security-by-design, threat model
├── 05-compliance.md    # DPIA, compliance evidence, SBOM, accessibility audit
└── 06-delivery.md      # risk register, deployment & rollback, observability, migration & runbook
```

The file mapping is a default — adapt it (high freedom), but keep: one OKF index, global section numbering across files, and one `ftd`-type frontmatter block per file. Validate every file with `scripts/validate.py` (size budget applies per file).

## Phase 3: Validate

### Self-review checklist

Before marking the draft complete, verify:

- [ ] All core sections present and substantive (not boilerplate)
- [ ] Every recommended section either present or justified in "Omitted sections & open questions"
- [ ] Enterprise-required sections present (enterprise scenario)
- [ ] Every user story passes INVEST
- [ ] Every acceptance criterion is a single testable bullet or valid EARS statement; `ac-format` marker present
- [ ] NFR section (if present) fully measurable: Metric + Threshold + Verification
- [ ] PbD/SbD sections substantive but concise — no padding
- [ ] Mermaid diagrams render
- [ ] DoD explicit (always); benefit hypothesis measurable (project/enterprise)
- [ ] OKF frontmatter present and valid; bundle has index.md (enterprise)
- [ ] Size budget respected, or breach consciously justified to the user

### Automated validation

Run `python scripts/validate.py <ftd-file.md> --scenario <feature|project|enterprise>` to check the core, enterprise-required sections, NFR measurability, PbD/SbD substance, placeholders, and the size budget. For bundles, run it per file.

**The validator is advisory, not absolute.** Fix every ERROR you agree with; resolve WARNINGs by including the section or recording a justified omission. If a check appears wrong for a legitimate document, report it to the user — never pad or contort the document to satisfy a check.

Also run the OKF validator (per the writing-okf skill) on every artifact: `python3 <writing-okf-dir>/scripts/validate_okf.py <path>`.

### HTML generation (if HTML or both mode)

Generate the HTML from the Markdown using [references/html-scaffold.md](references/html-scaffold.md) as the scaffold. Requirements:

- **One self-contained `.html` file.** Inline CSS, inline JS (Mermaid via CDN with a fallback `<div>` containing the raw diagram code if CDN fails).
- Sticky TOC, tabs per major section, collapsible subsections, carousel for wireframes/diagrams, light/dark toggle (respects OS `prefers-color-scheme` by default with manual toggle), print stylesheet.
- **Wireframes as CSS-box mockups** (gray boxes with labels), not SVG.
- The HTML is for humans; the Markdown is for humans AND agents (via OKF metadata). When producing both, always draft Markdown first, then generate HTML from it.

## Phase 4: Deliver

Save the file(s) at the location and with the filename confirmed in Phase 1. Present the deliverable path(s) to the user. Offer to iterate on specific sections.

**Lifecycle guidance:** an FTD is a decision record. Keep it trimmed and accurate (a small fresh document beats a large stale one). Update via the revision history (and bundle `log.md`) for material changes; when the design fundamentally changes, write a new version that supersedes the old one instead of endlessly patching. Do not let the FTD fossilize into a half-correct specification of the code — the code is the most detailed spec.

## Phase R: Review & Restructure

When the user provides an existing document (FTD, legacy design doc, feature description) and asks to review, audit, improve, or restructure it, use **Phase R** instead of the draft workflow (Phase 1 → 4). Phase R has three modes:

- **Mode A: Audit** — produce a prioritised gap report against the FTD standard. No changes to the source document.
- **Mode B: Restructure** — rewrite a legacy design document into FTD-conform format (bundle for enterprise).
- **Mode C: Feature-structuring** — structure a loose feature description (Jira ticket, Confluence page, OneNote) into FTD-feature format.

The full workflow, clarification gate, and per-mode steps are in [references/review-workflow.md](references/review-workflow.md). Key rules:

- **Clarification gate is still mandatory** — confirm mode, target scenario, output language, output mode, AC format, and filename before any work.
- **Audit mode is report-only** — never modify the source document in Audit mode.
- **Restructure mode preserves the source's revision history** — the restructured doc is a continuation, not a replacement.
- **Feature-structuring always includes the core** — DoD, PbD, and SbD are never optional.
- **Validate the output** — run `python scripts/validate.py <file> --scenario <scenario>` (or `--audit` for Audit mode) and resolve every error (fix or consciously report).

## When NOT to use this skill

- The user wants a **business case** or **project plan** — decline.
- The user wants a **tender/RFP response** — decline.
- The user wants a **quick technical spec for one endpoint** with no broader scope — use a lighter artifact, not an FTD.
- The user wants **only architecture diagrams** with no functional content — produce diagrams directly, not an FTD.
- The user is asking how to *use* an existing system — that is documentation, not design.

## Common anti-patterns to refuse

- "Just write something based on what we discussed" without going through Phase 1 — refuse, run the gate.
- "Skip the privacy section, we don't have personal data" — refuse; the section must be present and explicitly justify the claim. (It may be three sentences long — concise is fine, absent is not.)
- "Make the NFRs flexible, we'll figure out numbers later" — refuse; NFRs without thresholds are not NFRs. (Justified omission of the whole NFR section IS allowed — record it.)
- "Generate the HTML directly without Markdown" — refuse; Markdown-first is mandatory so the agent-facing artifact exists.
- "Skip the acceptance-criteria-format question, just use bullets" — refuse; the AC format is a mandatory output question (Phase 1, question 4) and must be confirmed with the user.
- "Audit the FTD and fix the issues silently" — refuse; Audit mode is report-only. Offer Restructure mode if the user wants fixes applied.
- "Pad the privacy/security sections until the validator passes" — refuse; the validator checks substance, not volume. Concise sections are a virtue.
- "Keep every template section because a section might be useful someday" — refuse; justify each recommended section or record the omission. Completeness is not a goal.
- "Drop recommended sections silently" — refuse; record every omission with a one-line reason in "Omitted sections & open questions".
- "Produce a 23-section single-file enterprise FTD" — refuse; enterprise designs ship as an indexed multi-file bundle.
- "Skip the OKF frontmatter / skip invoking writing-okf" — refuse; the metadata layer is what makes the document agent-consumable.

## Reference index

| Reference | When to read |
|-----------|--------------|
| [references/scenario-identification.md](references/scenario-identification.md) | Phase 0 — always: core/recommended/required toggles, budgets, omissions convention |
| [references/intake-questions.md](references/intake-questions.md) | Phase 1 — to drive the intake conversation |
| [references/ftd-template.md](references/ftd-template.md) | Phase 2 — the core template + optional section library |
| [references/acceptance-criteria.md](references/acceptance-criteria.md) | Phase 2 — bullets vs EARS format, INVEST, examples |
| [references/mermaid-snippets.md](references/mermaid-snippets.md) | Phase 2 — C4, sequence, ERD, BPMN snippets |
| [references/nfr-taxonomy.md](references/nfr-taxonomy.md) | Phase 2 — ISO 25010 + ISO 29148 + measurable format |
| [references/privacy-by-design.md](references/privacy-by-design.md) | Phase 2 — always; 7 Cavoukian principles → FTD fields |
| [references/security-by-design.md](references/security-by-design.md) | Phase 2 — always; SbD controls, STRIDE+LINDDUN |
| [references/split-decision.md](references/split-decision.md) | Phase 1 — FSD/TSD vs combined FTD decision tree |
| [references/html-scaffold.md](references/html-scaffold.md) | Phase 3 — when HTML output is requested |
| [references/review-workflow.md](references/review-workflow.md) | Phase R — audit, restructure, or feature-structuring |
| [references/evaluations.md](references/evaluations.md) | When testing the skill against the scenarios |
