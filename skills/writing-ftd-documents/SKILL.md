---
name: writing-ftd-documents
description: Drafts enterprise-level Functional Technical Design (FTD) documents for software, data, integration, and infrastructure projects. Use when the user needs to write an FTD, FSD, TSD, functioneel ontwerp (FO), technisch ontwerp (TO), software design document (SDD), or system design document — for a small feature, a full project, or an enterprise-grade project. Enforces intensive scope clarification before drafting, supports Markdown (Mermaid + numbered headings + TOC) and self-contained HTML output (inline CSS/JS, tabs, carrousel, wireframes), and embeds privacy-by-design and security-by-design by default. Also use when the user asks to split a design into separate functional and technical documents.
---

# Writing FTD Documents

Author and review enterprise-level Functional Technical Design (FTD) documents. The default output is **Markdown** with Mermaid diagrams, numbered headings, and a table of contents. An extended **self-contained HTML** mode produces one portable file (inline CSS/JS) for human presentation. Both modes are always offered; the user always chooses.

## Iron Law

**You MUST complete the clarification gate before drafting any FTD. NO EXCEPTIONS.**

Premature drafting produces designs that miss scope, omit stakeholders, under-specify non-functional requirements, or skip privacy/security implications. An FTD written on insufficient scope is worse than no FTD — it creates false confidence.

```
STOP. Before drafting any FTD:
- [ ] I identified the scenario (feature / project / enterprise) — Phase 0
- [ ] I completed the intake conversation until scope is fully clear — Phase 1
- [ ] For project/enterprise: I produced a Scope Summary and got explicit sign-off
- [ ] I asked the four mandatory output questions (split, language, mode, filename)
- [ ] The user answered the mandatory scope questions
If any box is unchecked: GO BACK. Do not draft.
```

### Hard refusal

If the user refuses to answer mandatory scope questions after being asked clearly, **you MUST refuse to draft the FTD**. Explain why scope clarity is non-negotiable and offer to resume when they can provide it. Never produce an FTD on insufficient scope. Producing a wrong-but-complete document is failure, not professionalism.

## Scope of this skill

**In scope:** FTDs for software applications, data products, integration/migration projects, infrastructure and platform engineering, business-process automation. Functional and technical design combined or split.

**Out of scope:** Pure business cases, project plans, RFP/tender responses, marketing briefs. If the user asks for these, decline and point to the right artifact.

## Degrees of freedom

- **Low freedom** (mandatory, non-negotiable): the Iron Law, Phase 0 scenario identification, the four mandatory output questions, privacy-by-design and security-by-design inclusion, traceability matrix, DoR/DoD, measurable NFRs.
- **High freedom** (adapt to context): section ordering within the template, depth per section, diagram choice, narrative tone, naming of artifacts.

## Phase 0: Scenario Identification (REQUIRED — FIRST STEP)

Before any intake questions, identify which of three scenarios applies. This single decision drives every downstream toggle.

| Scenario | When it applies | Sign-off gate | Template |
|----------|-----------------|---------------|----------|
| **feature** | One user story or a tightly-coupled handful; one component touched; low risk; one team | No | Condensed |
| **project** | Multiple stories/epics; cross-component; multiple teams or external supplier; moderate risk | Yes (Scope Summary) | Full |
| **enterprise** | Org-wide impact; regulatory exposure (AVG/NEN 7510/BIO/ISO 27001); multiple suppliers; high risk or high cost | Yes (Scope Summary) | Full + compliance evidence |

**How to decide:** ask the user one framing question first — "Is this a small feature, a full project, or an enterprise-grade project?" — and verify their answer against the criteria above. If their answer conflicts with the criteria (e.g. they say "feature" but it touches multiple teams and regulated data), surface the conflict and propose the higher tier.

See [references/scenario-identification.md](references/scenario-identification.md) for the full toggle matrix that controls which sections are mandatory per scenario.

## Phase 1: Intake (REQUIRED — CLARIFICATION GATE)

The intake is a **free conversation**. Other skills may have already gathered context (research, codebase analysis, prior FTDs) — use that as input, do not re-ask what is already answered. Internally track four dimensions and keep probing until each is fully clear:

1. **Scope** — what is in, what is out, what is the boundary, what is the success criterion
2. **Functional** — who are the users/personas, what must the system do, what are the user stories, what is the business value
3. **Technical** — what is the existing architecture, what changes, what are the constraints (perf, security, compliance, budget, time), what integrations
4. **Output** — see the four mandatory questions below

Keep probing. Do not accept vague answers. If the user says "it should be fast", ask "what does fast mean — p95 latency target under which load?". If they say "secure", ask "against which threats, complying with which framework?".

### Four mandatory output questions

You MUST always ask these, regardless of scenario:

1. **FSD/TSD split vs combined FTD** — Should we produce two separate documents (functional + technical) or one combined FTD? You SHOULD propose a default based on scenario (see [references/split-decision.md](references/split-decision.md)): combined for feature, propose split for enterprise with multiple suppliers. **The user always decides.**
2. **Output language** — English (default: "As a…/I want…/So that…") or Dutch ("Als…/wil ik…/zodat…")?
3. **Output mode** — Markdown only, HTML only, or both? If both, Markdown is drafted first, then HTML is generated from it.
4. **Filename and storage location** — Confirm filename convention (suggested: `FTD-[project]-[feature]-vX.Y.{md,html}`) and where to save.

### Sign-off gate (project and enterprise only)

For project and enterprise scenarios, before exiting Phase 1 you MUST produce a **Scope Summary** — a concise recap of:
- Scenario and chosen template
- In-scope / out-of-scope
- Key user stories (titles only)
- Stakeholders and RACI owners
- Output decisions (split, language, mode, filename)
- Open assumptions (if any) marked explicitly

Present the Scope Summary to the user and require explicit approval before drafting. Do not begin Phase 2 without it.

For feature scenarios, no sign-off gate — proceed to drafting once scope is clear.

See [references/intake-questions.md](references/intake-questions.md) for the full question bank per dimension.

## Phase 2: Draft

Apply the master template with toggles based on the scenario. See [references/ftd-template.md](references/ftd-template.md).

**Non-negotiable in every draft, all scenarios:**

- **Privacy-by-design and security-by-design sections always present.** See [references/privacy-by-design.md](references/privacy-by-design.md) and [references/security-by-design.md](references/security-by-design.md). Even if no personal data is obviously involved, the section must explicitly state that and justify it.
- **Traceability matrix always present** — every requirement mapped to design component and test.
- **DoR and DoD always explicit.**
- **NFRs always measurable** — Subject / Attribute / Metric / Threshold / Verification per ISO/IEC 25010. See [references/nfr-taxonomy.md](references/nfr-taxonomy.md).
- **User stories in "As a…/I want…/So that…" (or Dutch equivalent) format, checked against INVEST.**
- **Acceptance criteria as bullet lists** (not Gherkin). Each criterion is a single, testable statement.
- **C4 diagrams via Mermaid** as the default architecture notation. For project/enterprise, add arc42 sections: design decisions (ADR-style), quality scenarios. See [references/mermaid-snippets.md](references/mermaid-snippets.md).
- **Numbered headings** (1, 1.1, 1.1.1) and **table of contents** at the top.

**Scenario-specific additions:**

- **feature:** condensed template; risk register and RACI optional (mention "impacted teams" only).
- **project:** full template; add risk register, RACI, arc42 design decisions, deployment & rollback plan.
- **enterprise:** full template plus DPIA reference, threat model (STRIDE + LINDDUN), compliance evidence mapping to BIO/NEN 7510/ISO 27001 as toggled, SBOM reference, accessibility audit (WCAG 2.1 AA).

## Phase 3: Validate

### Self-review checklist

Before marking the draft complete, verify:

- [ ] All mandatory sections for the scenario present (per toggle matrix)
- [ ] Every user story passes INVEST
- [ ] Every acceptance criterion is a single testable bullet
- [ ] Traceability matrix complete (no orphan requirements, no orphan tests)
- [ ] NFRs all have Metric + Threshold + Verification
- [ ] Privacy-by-design section present and populated (not boilerplate)
- [ ] Security-by-design section present and populated (not boilerplate)
- [ ] C4 diagrams render in Mermaid
- [ ] DoR and DoD explicit
- [ ] For project/enterprise: risk register and RACI present
- [ ] For enterprise: DPIA decision documented, threat model attached, compliance toggles addressed

### Automated validation

Run `python scripts/validate.py <ftd-file.md> --scenario <feature|project|enterprise>` to check mandatory sections, NFR measurability, and PbD/SbD presence. Fix every error before delivery. The validator's word is final — do not override it.

### HTML generation (if HTML or both mode)

Generate the HTML from the Markdown using [references/html-scaffold.md](references/html-scaffold.md) as the scaffold. Requirements:

- **One self-contained `.html` file.** Inline CSS, inline JS (Mermaid via CDN with a fallback `<div>` containing the raw diagram code if CDN fails).
- Sticky TOC, tabs per major section, collapsible subsections, carrousel for wireframes/diagrams, light/dark toggle (respects OS `prefers-color-scheme` by default with manual toggle), print stylesheet.
- **Wireframes as CSS-box mockups** (gray boxes with labels), not SVG.
- The HTML is for humans; the Markdown is for agents. When producing both, always draft Markdown first, then generate HTML from it.

## Phase 4: Deliver

Save the file(s) at the location and with the filename confirmed in Phase 1. Present the deliverable path(s) to the user. Offer to iterate on specific sections.

## When NOT to use this skill

- The user wants a **business case** or **project plan** — decline.
- The user wants a **tender/RFP response** — decline.
- The user wants a **quick technical spec for one endpoint** with no broader scope — use a lighter artifact, not an FTD.
- The user wants **only architecture diagrams** with no functional content — produce diagrams directly, not an FTD.
- The user is asking how to *use* an existing system — that is documentation, not design.

## Common anti-patterns to refuse

- "Just write something based on what we discussed" without going through Phase 1 — refuse, run the gate.
- "Skip the privacy section, we don't have personal data" — refuse; the section must be present and explicitly justify the claim.
- "Make the NFRs flexible, we'll figure out numbers later" — refuse; NFRs without thresholds are not NFRs.
- "Generate the HTML directly without Markdown" — refuse; Markdown-first is mandatory so the agent-facing artifact exists.

## Reference index

| Reference | When to read |
|-----------|--------------|
| [references/scenario-identification.md](references/scenario-identification.md) | Phase 0 — always, to apply the toggle matrix |
| [references/intake-questions.md](references/intake-questions.md) | Phase 1 — to drive the intake conversation |
| [references/ftd-template.md](references/ftd-template.md) | Phase 2 — the master template with toggles |
| [references/acceptance-criteria.md](references/acceptance-criteria.md) | Phase 2 — bullet format, INVEST, examples |
| [references/mermaid-snippets.md](references/mermaid-snippets.md) | Phase 2 — C4, sequence, ERD, BPMN snippets |
| [references/nfr-taxonomy.md](references/nfr-taxonomy.md) | Phase 2 — ISO 25010 + measurable format |
| [references/privacy-by-design.md](references/privacy-by-design.md) | Phase 2 — always; 7 Cavoukian principles → FTD fields |
| [references/security-by-design.md](references/security-by-design.md) | Phase 2 — always; SbD controls, STRIDE+LINDDUN |
| [references/split-decision.md](references/split-decision.md) | Phase 1 — FSD/TSD vs combined FTD decision tree |
| [references/html-scaffold.md](references/html-scaffold.md) | Phase 3 — when HTML output is requested |
| [references/evaluations.md](references/evaluations.md) | When testing the skill against the three scenarios |
