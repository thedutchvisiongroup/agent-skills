# FTD Master Template (ceiling model)

## Contents
- How to use this template
- Table of contents
- Core sections (always mandatory): 1, 3, 6, 7, 9 (DoD), 14, 15, 24
- Recommended sections (include or justify omission): 2, 4, 5, 8, 9 (DoR), 10-13, 16-18, 20-23
- Enterprise-required sections: 19 (+ DPIA, threat model, SBOM, NFRs)
- Author checklist

## How to use this template

This template uses the **ceiling model**: start from the core, add only what earns its place.

1. **Always include the core** — sections marked **(C)**. They are mandatory in every scenario.
2. **For each recommended section (R)**: include it when it earns its place for THIS design, or omit it and record a one-line justification in §24 "Omitted sections & open questions". If you cannot write that one sentence of why, the section does not belong in the document.
3. **Enterprise-required sections (E)** are mandatory for the enterprise scenario only.
4. Replace every `[placeholder]` with concrete content. Numbered headings are mandatory (1, 1.1, 1.1.1). A table of contents at the top is mandatory. Respect the scenario size budget (feature ≤ ~150 lines, project ≤ ~400 lines, enterprise = bundle ≤ ~800 lines per file) — see [scenario-identification.md](scenario-identification.md).
5. Concise beats complete. A correct three-sentence privacy statement beats a padded page.

The template below uses English placeholders. If the user chose Dutch as the output language, translate the section titles and placeholder text to Dutch at draft time. Keep technical terms (API, NFR, RACI, DPIA, STRIDE, DoR, DoD, etc.) in English regardless of output language (Dutch aliases are tolerated by the validator, but consistency aids grep-ability).

**Enterprise bundle mapping:** for the enterprise scenario, split this template across files per the default mapping in SKILL.md Phase 2 (01-scope, 02-requirements, 03-architecture, 04-quality, 05-compliance, 06-delivery), each file with its own OKF frontmatter, plus an OKF `index.md`. Section numbering stays global across files.

---

## Table of contents

```markdown
## Table of contents

1. Document control
2. Executive summary
3. Scope & objectives
4. Stakeholders & RACI
5. Business context & goals
6. User stories
7. Acceptance criteria
8. Traceability matrix
9. Definition of Ready / Definition of Done
10. Architecture
11. Data model
12. API & integration
13. Non-functional requirements
14. Privacy-by-design
15. Security-by-design
16. Risk register
17. Deployment & rollback
18. Observability & logging
19. Compliance evidence
20. Migration & runbook
21. Glossary
22. Crosscutting Concepts
23. Approvals & sign-off
24. Omitted sections & open questions
```

(Adjust the list to the sections actually present — keep core sections, keep included recommended sections, drop omitted ones. §24 stays whenever anything is omitted or open.)

---

## 1. Document control **(C — core, all scenarios)**

Every FTD artifact starts with an OKF frontmatter block (for agents) above the human-facing title and document control table (for humans). Invoke the `writing-okf` skill and follow its conventions for the `type` value and fields.

```markdown
---
type: FTD
title: "[Project/Feature name] — Functional Technical Design"
description: "[One-sentence summary of the design and its scope]"
tags: [ftd, scenario-feature|project|enterprise, <domain>, <compliance-tags-if-any>]
timestamp: [YYYY-MM-DDTHH:MM:SS]
---

# [Project/Feature name] — Functional Technical Design

| Field | Value |
|-------|-------|
| Document ID | FTD-[project]-[feature]-vX.Y |
| Scenario | feature / project / enterprise |
| Author | [name] |
| Date | [YYYY-MM-DD] |
| Status | Draft / Review / Approved |
| Classification | Public / Internal / Confidential |

## Revision history

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1 | YYYY-MM-DD | [name] | Initial draft |
```

## 2. Executive summary **(R — recommended for project/enterprise; omit with justification; not expected for feature)**

```markdown
## 2. Executive summary

[One paragraph: which problem, which solution at a high level, which scope,
key decisions and risks. Intended for decision-makers who will not read the
full document.]
```

## 3. Scope & objectives **(C — core, all scenarios)**

```markdown
## 3. Scope & objectives

### 3.1 Problem statement
[What is the problem or opportunity? What is the cost of doing nothing?]

### 3.2 In scope
- [Concrete: components, teams, data, processes]

### 3.3 Out of scope
- [Explicit: adjacent work that someone might assume is included]

### 3.4 Success criteria
- [Measurable: "p95 latency < 500ms at 1000 concurrent users"]
- [Measurable: "0 critical pentest findings before production"]
```

## 4. Stakeholders & RACI **(R — recommended for project/enterprise; for feature, fold impacted teams into §3 if worth noting)**

```markdown
## 4. Stakeholders & RACI

### 4.1 Stakeholders
| Name | Role | Interest |
|------|------|----------|
| [name] | Product Owner | [interest] |
| [name] | Architect | [interest] |
| [name] | DPO / Security Officer | [interest] |

### 4.2 RACI matrix
| Activity | Responsible | Accountable | Consulted | Informed |
|----------|-------------|-------------|-----------|----------|
| FTD authoring | [name] | [name] | [name] | [name] |
| Implementation | [name] | [name] | [name] | [name] |
| Approval | [name] | [name] | [name] | [name] |
```

## 5. Business context & goals **(R — recommended for project/enterprise; optional for feature)**

```markdown
## 5. Business context & goals

### 5.1 Business context
[How does this fit into the wider organisation and strategy?]

### 5.2 Business goals
- [Measurable business goal, e.g. "Conversion +10% within 6 months"]
- [Cost saving or risk reduction]

### 5.3 Benefit hypothesis
*(R — recommended for project/enterprise (strongly expected — omit only with good reason); optional for feature)*

We believe [business outcome] will be achieved if [these users] successfully
achieve [this user outcome] with [this feature/change].

- **Business outcome (measurable):** [e.g. "Reduce support tickets by 20% within Q1"]
- **User outcome:** [e.g. "Users complete self-service password reset without contacting support"]
- **Validation method:** [e.g. "Track support ticket category 'password reset' over 3 months"]
- **Baseline:** [current metric value]
- **Target:** [target metric value]

### 5.4 Constraints
- [Budget, time, tech stack, compliance, organisational]
```

## 6. User stories **(C — core, all scenarios)**

```markdown
## 6. User stories

All user stories are checked against INVEST (Independent, Negotiable, Valuable,
Estimable, Small, Testable). Format: "As a [role], I want [action], so that
[value]" (EN) or "Als [rol], wil ik [actie], zodat [waarde]" (NL).

### 6.1 [Epic / theme]

#### US-01: [title]
**As a** [role],
**I want** [action],
**so that** [value].

**INVEST check:**
- Independent: [yes/no — explanation]
- Negotiable: [yes/no]
- Valuable: [yes/no — to which business goal]
- Estimable: [yes/no]
- Small: [yes/no — fits in one sprint]
- Testable: [yes/no]

**Priority:** MoSCoW (Must / Should / Could / Won't)
**Story points:** [X]
```

## 7. Acceptance criteria **(C — core, all scenarios)**

```markdown
## 7. Acceptance criteria
<!-- ac-format: bullets|ears -->

Acceptance criteria are written in the format chosen in Phase 1 (question 4):
bullets (default) or EARS notation. Each criterion is a single, testable
statement. No Gherkin. Do not mix formats within one document. The
`ac-format` marker comment above is mandatory — it lets tooling and agents
detect the format; keep the chosen value.

### 7.1 US-01: [title]
- [Testable statement, e.g. "The system rejects CSV files larger than 10 MB
  with HTTP 413 and an error message stating the size limit."]
- [Testable statement]
- [Testable statement]

### 7.2 US-02: [title]
- [Testable statement]
```

See [acceptance-criteria.md](acceptance-criteria.md) for both formats (bullets
and EARS), INVEST, and examples.

## 8. Traceability matrix **(R — recommended for all scenarios; omit with justification for trivial features)**

```markdown
## 8. Traceability matrix

Every requirement is mapped to a design component and a test. No orphan
requirements without design, no design without a requirement.

| ID | Requirement (user story) | Design component | API / DB artefact | Test case | Status |
|----|--------------------------|------------------|--------------------|-----------|--------|
| US-01 | [title] | [component] | [endpoint/table] | TC-01 | Open |
| US-02 | [title] | [component] | [endpoint/table] | TC-02 | Open |
```

## 9. Definition of Ready / Definition of Done **(DoD: C — core, ALWAYS mandatory. DoR: R — recommended; optional for feature, where the intake gate largely covers it)**

```markdown
## 9. Definition of Ready / Definition of Done

### 9.1 Definition of Ready (DoR)
A user story is ready for implementation when:
- [ ] User story written in "As a…/I want…/so that…" format
- [ ] Acceptance criteria written as bullets
- [ ] INVEST check completed
- [ ] Dependencies identified and documented
- [ ] Performance implication assessed (NFRs relevant?)
- [ ] Security implication assessed (PbD/SbD section relevant?)
- [ ] Data implication assessed (AVG/DPIA trigger?)

### 9.2 Definition of Done (DoD)
A user story is done when:
- [ ] Implementation complete and merged
- [ ] Automated tests green (unit + integration)
- [ ] Acceptance criteria met and demonstrated
- [ ] Documentation updated (FTD, OpenAPI, runbook)
- [ ] Migration tested (if applicable)
- [ ] Privacy and security review performed
- [ ] Deployed to a production-like environment
- [ ] Sign-off by Product Owner and Architect
```

## 10. Architecture **(R — recommended for all scenarios; omit with justification for trivial features with no architecture impact)**

```markdown
## 10. Architecture

Architecture notation: C4 model (Context, Container, Component) via Mermaid.
At project and enterprise level, supplemented with arc42 sections: design
decisions (ADR-style) and quality scenarios. See [mermaid-snippets.md](mermaid-snippets.md).

### 10.1 C4 Context (Level 1)
[Mermaid C4 Context diagram — system in relation to users and external systems]

### 10.2 C4 Container (Level 2)
*(R — recommended for project/enterprise; optional for feature)*
[Mermaid C4 Container diagram — containers (apps, services, datastores) and their relationships]

### 10.3 C4 Component (Level 3) — per container
*(R — recommended for enterprise; optional for project)*
[Mermaid C4 Component diagram per relevant container]

### 10.4 Sequence diagrams — key flows
*(R — recommended for project/enterprise; optional for feature)*
[Mermaid sequence diagrams for the key use cases]

### 10.5 Design decisions (arc42)
*(R — recommended for project/enterprise)*
Architecture decisions in ADR style (Architecture Decision Records):

#### ADR-01: [Decision title]
- **Context:** [Why a decision is needed]
- **Decision:** [What was decided]
- **Status:** Proposed / Accepted / Superseded
- **Consequences:** [Positive and negative]
- **Alternatives considered:** [Which other options and why rejected]

### 10.6 Quality scenarios (arc42)
*(R — recommended for project/enterprise)*
Concrete scenarios the design must be tested against:
- **Performance scenario:** "100 concurrent users do X, p95 latency < Y ms"
- **Availability scenario:** "On failure of component Z the system degrades to [behaviour]"
- **Security scenario:** "An anonymous attacker attempts [attack]; expected behaviour [response]"
```

## 11. Data model **(R — recommended for project/enterprise; optional for feature)**

```markdown
## 11. Data model

*(R — recommended for project/enterprise; optional for feature)*

### 11.1 Conceptual model (ERD)
[Mermaid ER diagram with entities, relationships, cardinality]

### 11.2 Entities
| Entity | Description | PII? | Source | Retention |
|--------|-------------|------|--------|-----------|
| [name] | [description] | yes/no | [system] | [period] |

### 11.3 Migration from existing model
*(if applicable)*
[What changes, how it is migrated, what is the cutover strategy]
```

## 12. API & integration **(R — recommended for all scenarios with API surface; omit with justification)**

```markdown
## 12. API & integration

### 12.1 API overview
Endpoints summarised; full spec in external OpenAPI file (reference below).

| Endpoint | Method | Auth | Summary | OpenAPI ref |
|----------|--------|------|---------|-------------|
| /path | GET/POST | [type] | [what it does] | [link/ref] |

**OpenAPI specification:** [link to openapi.yaml or reference]

### 12.2 Integrations
*(R — recommended for project/enterprise; feature — if applicable)*
| System | Protocol | Direction | Frequency | Error handling |
|--------|----------|-----------|-----------|-----------------|
| [name] | REST/Kafka/SFTP | in/out/bi | [realtime/batch] | [behaviour on error] |

### 12.3 Data flows
[Mermaid data flow diagram or sequence diagram for critical integrations]
```

## 13. Non-functional requirements **(R — recommended for all scenarios; E — enterprise-required. When present, always measurable; when omitted, record the justification — e.g. "inherits system-level NFRs")**

```markdown
## 13. Non-functional requirements

Taxonomy: ISO/IEC 25010 (8 quality characteristics). Every NFR is measurable:
Subject / Attribute / Metric / Threshold / Verification. See [nfr-taxonomy.md](nfr-taxonomy.md).

### 13.1 Performance efficiency
| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-01 | /orders endpoint | response time | p95 latency | < 500 ms | load test with 1000 concurrent users |

### 13.2 Reliability
| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-02 | [service] | availability | uptime | 99.9% per month | monitoring dashboard |

### 13.3 Security
[See also §15 Security-by-design]

### 13.4 Maintainability
| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-03 | codebase | test coverage | % | >= 80% | CI pipeline |

### 13.5 Portability / Compatibility
[If applicable]

### 13.6 Usability & Accessibility
| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-04 | UI | accessibility | WCAG level | 2.1 AA | accessibility audit |

(Complete per ISO 25010: Functional suitability, Performance, Compatibility, Usability,
Reliability, Security, Maintainability, Portability.)
```

## 14. Privacy-by-design **(C — core, ALWAYS present — even if no personal data: then explicitly justify that position. Concise is fine; absent is not.)**

```markdown
## 14. Privacy-by-design

ALWAYS present, even if no personal data appears to be involved — then explicitly
justify that position. See [privacy-by-design.md](privacy-by-design.md) for the 7
Cavoukian principles and field set.

### 14.1 Processing of personal data
Are personal data processed? yes/no. If yes:

### 14.2 Data inventory
| Field | Category | Special category? | Purpose | Lawful basis | DPIA required? | Retention |
|-------|----------|-------------------|---------|--------------|-----------------|-----------|
| [field] | [personal data/...] | yes/no | [purpose] | [lawful basis] | yes/no | [period] |

### 14.3 DPIA
- DPIA required? yes/no — [reason]
- DPIA reference: [link/ID]
- Outcomes: [summary of mitigating measures]

### 14.4 Privacy principles applied
- **Data minimisation:** [how]
- **Purpose limitation:** [how]
- **Pseudonymisation/anonymisation:** [how, or n/a with reason]
- **Privacy-friendly defaults:** [how, e.g. analytics default off]
- **Data subject rights:** [access/rectification/erasure/portability — flow]

### 14.5 Retention & deletion
- Retention policy: [reference or table]
- Deletion process: [automated job, periodicity, verification]
```

## 15. Security-by-design **(C — core, ALWAYS present — even if minimal exposure: then explicitly justify. Concise is fine; absent is not.)**

```markdown
## 15. Security-by-design

ALWAYS present. See [security-by-design.md](security-by-design.md) for controls,
ASVS, STRIDE+LINDDUN threat modeling.

### 15.1 Authentication & session management
- Method: [OAuth2/OIDC/...]
- MFA required for: [roles/scope]
- Session policy: [timeout, revocation]

### 15.2 Authorization model
- Model: [RBAC/ABAC/claims]
- Decision points: [where rights are enforced]
- Test strategy: [unit tests per access rule]

### 15.3 Encryption
- In transit: [TLS policy reference]
- At rest: [algorithm, key management (KMS/HSM)]

### 15.4 Secrets & key management
- Storage: [KMS/HSM/vault]
- Rotation: [policy reference + cadence]

### 15.5 Dependency management
- SBOM: [reference]
- SCA: [tool, cadence]
- Gate: [no critical CVEs before production]

### 15.6 CI/CD security gates
- SAST: [tool]
- DAST: [tool]
- Secret scanning: [tool]

### 15.7 Audit logging
- Events: [what is logged]
- Retention: [period]
- Access control: [who may read logs]
- SIEM integration: [yes/no + reference]

### 15.8 Threat model
*(E — enterprise-required; R — recommended for project)*
- Methods: STRIDE (security) + LINDDUN (privacy)
- Asset -> Threat -> Existing controls -> Residual risk -> Mitigation owner
[See security-by-design.md for template]

### 15.9 ASVS level
Target ASVS level: [L1/L2/L3] — [reason]
```

## 16. Risk register **(R — recommended for project/enterprise; not expected for feature)**

```markdown
## 16. Risk register

*(R — recommended for project/enterprise)*

| ID | Risk | Likelihood | Impact | Score | Mitigation | Owner | Status |
|----|------|------------|--------|-------|------------|-------|--------|
| R-01 | [risk description] | L/M/H | L/M/H | [score] | [measure] | [name] | Open/Closed |
```

## 17. Deployment & rollback **(R — recommended for all scenarios with deployable artefacts)**

```markdown
## 17. Deployment & rollback

### 17.1 Deployment strategy
- Environments: [dev/test/acc/prod]
- Strategy: [blue-green/canary/rolling]
- Release gates: [tests, approvals]

### 17.2 Rollback plan
- Trigger: [when to roll back]
- Procedure: [steps]
- RTO: [recovery time objective]
- Data implication: [what happens to data on rollback]
```

## 18. Observability & logging **(R — recommended for project/enterprise)**

```markdown
## 18. Observability & logging

*(R — recommended for project/enterprise)*

### 18.1 Metrics
| Metric | Threshold | Alert | Dashboard |
|--------|-----------|-------|-----------|
| [metric] | [threshold] | [yes/no + channel] | [link] |

### 18.2 Logging
- Application logs: [level, format, destination]
- Access logs: [retention, destination]
- Audit logs: [see §15.7]

### 18.3 Tracing
[Distributed tracing, sampling rate, tool]

### 18.4 Runbook references
[Links to runbooks for critical operations]
```

## 19. Compliance evidence **(E — enterprise-required)**

```markdown
## 19. Compliance evidence

*(E — enterprise-required. Document which frameworks apply — not every framework section is mandatory.)*

### 19.1 GDPR / AVG
- DPIA: [reference or "not required — reason"]
- Record of processing: [reference]
- Officers: DPO = [name]

### 19.2 NEN 7510 (healthcare — if applicable)
- Scope: [which systems]
- Controls: [reference to control matrix]

### 19.3 BIO (government — if applicable)
- Baseline: BIO2
- Deviations: [list or "none"]

### 19.4 ISO 27001 (if applicable)
- Scope: [which systems]
- Statement of Applicability: [reference]

### 19.5 EU AI Act (if AI component)
- Classification: [none/limited/high/prohibited]
- For high-risk: technical documentation, risk management, human oversight, logging
```

## 20. Migration & runbook **(R — recommended for project/enterprise)**

```markdown
## 20. Migration & runbook

*(R — recommended for project/enterprise)*

### 20.1 Migration plan
- Data to migrate: [volume, source, target]
- Cutover strategy: [big bang / phased]
- Reversibility: [yes/no — how]

### 20.2 Runbook
[Links to or inline runbooks for: deployment, rollback, incident response, data restore]
```

## 21. Glossary **(R — recommended for project/enterprise (strongly expected); optional for feature)**

*(R — recommended for project/enterprise)*

```markdown
## 21. Glossary

A glossary of domain and technical terms used in this FTD, so all stakeholders
share a common vocabulary ("ubiquitous language"). Include abbreviations,
domain-specific terms, and any terms that could be ambiguous in this context.

| Term / abbreviation | Definition |
|---------------------|------------|
| [term] | [definition] |
| [abbreviation] | [full form + definition] |
```

## 22. Crosscutting Concepts **(R — recommended for enterprise; optional for project/feature)**

*(R — recommended for enterprise; optional for project/feature)*

```markdown
## 22. Crosscutting Concepts

Cross-cutting concerns that apply across multiple building blocks and sections
of the design. Document each concept that is relevant; omit sections that do
not apply with a brief justification.

### 22.1 Security concepts
[Cross-references to §15 Security-by-design; domain models, security patterns and styles relevant across the system]

### 22.2 Persistence and data access
[ORM, repository pattern, caching strategy, transaction management — where used across multiple components]

### 22.3 Logging and observability
[Cross-reference to §18 Observability; logging schema, correlation IDs, tracing conventions used consistently]

### 22.4 Error and exception handling
[Consistent error model, error codes, HTTP status code conventions, retry policies]

### 22.5 Internationalisation (i18n) and localisation
[UI label strategy, date/number formatting, multi-language content handling]

### 22.6 Domain models and business rules
[Ubiquitous language, domain-driven design patterns, shared business rule engines]

### 22.7 Architecture and design patterns
[Patterns consistently applied across the system: e.g. CQRS, event sourcing, saga, hexagonal architecture]
```

## 23. Approvals & sign-off **(R — recommended for all scenarios; feature: one line, e.g. "Akkoord: [PO], [date]")**

```markdown
## 23. Approvals & sign-off

| Role | Name | Date | Signature (digital) |
|------|------|------|----------------------|
| Product Owner | [name] | YYYY-MM-DD | |
| Architect | [name] | YYYY-MM-DD | |
| Security Officer | [name] | YYYY-MM-DD | |
| DPO (if GDPR applies) | [name] | YYYY-MM-DD | |
| Project sponsor | [name] | YYYY-MM-DD | |
```

## 24. Omitted sections & open questions **(R — mandatory whenever any recommended section is omitted or any doubt is open; otherwise drop)**

```markdown
## 24. Omitted sections & open questions
(NL: ## Weggelaten secties & open punten)

Every recommended section that is not included in this FTD is listed here
with a one-line justification. Open doubts are recorded here as well — never
resolve doubt by padding a section.

- [Section name] — omitted: [one-line justification]
- NFRs — omitted: no performance/security impact; inherits system-level NFRs (see [ref]).
- Open question: [what is unknown, who will answer it, by when]
```

---

## Author checklist

Before delivering, verify the CEILING MODEL — completeness of the core, justification of the rest:

- [ ] All core (C) sections present: document control (incl. OKF frontmatter), TOC, scope & objectives, user stories, acceptance criteria (+ `ac-format` marker), DoD, privacy-by-design, security-by-design
- [ ] Core sections are substantive but concise — no padding
- [ ] Every recommended (R) section is either present (because it earns its place) or listed with a one-line justification in "Omitted sections & open questions"
- [ ] All enterprise-required (E) sections present (enterprise scenario): DPIA decision, threat model, compliance evidence, SBOM, measurable NFRs
- [ ] Enterprise output is a multi-file bundle with OKF `index.md` (or the deviation is consciously agreed with the user)
- [ ] No `[placeholder]` left unfilled
- [ ] User stories INVEST-checked
- [ ] Acceptance criteria in chosen format (bullets or EARS), testable, consistent, marked with `<!-- ac-format: ... -->`
- [ ] Traceability matrix (if present) complete
- [ ] NFR section (if present) fully measurable (Metric + Threshold + Verification)
- [ ] Mermaid diagrams render
- [ ] Size budget respected (feature ≤ ~150, project ≤ ~400, enterprise ≤ ~800 lines/file), or breach consciously justified to the user
- [ ] `python scripts/validate.py <file> --scenario <scenario>` — errors fixed; warnings resolved (include or justify); suspected validator bugs reported to the user, never worked around by padding
- [ ] OKF validator passed (per the writing-okf skill)
