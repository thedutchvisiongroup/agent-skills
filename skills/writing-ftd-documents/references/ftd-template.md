# FTD Master Template (with scenario toggles)

## Contents
- How to use this template
- Table of contents
- Section 1: Document control
- Section 2: Executive summary
- Section 3: Scope & objectives
- Section 4: Stakeholders & RACI
- Section 5: Business context & goals
- Section 6: User stories
- Section 7: Acceptance criteria
- Section 8: Traceability matrix
- Section 9: Definition of Ready / Definition of Done
- Section 10: Architecture (C4 + arc42)
- Section 11: Data model
- Section 12: API & integration
- Section 13: Non-functional requirements
- Section 14: Privacy-by-design
- Section 15: Security-by-design
- Section 16: Risk register
- Section 17: Deployment & rollback
- Section 18: Observability & logging
- Section 19: Compliance evidence (enterprise)
- Section 20: Migration & runbook
- Section 21: Approvals & sign-off
- Author checklist

## How to use this template

Copy this template into the draft. Apply the toggle matrix from [scenario-identification.md](scenario-identification.md): keep mandatory (M) and enterprise-only (E) sections, drop or condense optional (O) sections as appropriate. Replace every `[PLACEHOLDER]` with concrete content. Numbered headings are mandatory (1, 1.1, 1.1.1). A table of contents at the top is mandatory.

The template below uses English placeholders. If the user chose Dutch as the output language, translate the section titles and placeholder text to Dutch at draft time. Keep technical terms (API, NFR, RACI, DPIA, STRIDE, etc.) in English regardless of output language.

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
21. Approvals & sign-off
```

(Adjust the list to the sections actually present per scenario.)

---

## 1. Document control

```markdown
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

## 2. Executive summary

*(project, enterprise — mandatory; feature — drop)*

```markdown
## 2. Executive summary

[One paragraph: which problem, which solution at a high level, which scope,
key decisions and risks. Intended for decision-makers who will not read the
full document.]
```

## 3. Scope & objectives

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

## 4. Stakeholders & RACI

*(project, enterprise — mandatory; feature — replace with "Impacted teams")*

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

## 5. Business context & goals

*(project, enterprise — mandatory; feature — optional)*

```markdown
## 5. Business context & goals

### 5.1 Business context
[How does this fit into the wider organisation and strategy?]

### 5.2 Business goals
- [Measurable business goal, e.g. "Conversion +10% within 6 months"]
- [Cost saving or risk reduction]

### 5.3 Constraints
- [Budget, time, tech stack, compliance, organisational]
```

## 6. User stories

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

## 7. Acceptance criteria

```markdown
## 7. Acceptance criteria

Acceptance criteria are bullets — one single, testable statement per bullet.
No Gherkin.

### 7.1 US-01: [title]
- [Testable statement, e.g. "The system rejects CSV files larger than 10 MB
  with HTTP 413 and an error message stating the size limit."]
- [Testable statement]
- [Testable statement]

### 7.2 US-02: [title]
- [Testable statement]
```

See [acceptance-criteria.md](acceptance-criteria.md) for the format and examples.

## 8. Traceability matrix

```markdown
## 8. Traceability matrix

Every requirement is mapped to a design component and a test. No orphan
requirements without design, no design without a requirement.

| ID | Requirement (user story) | Design component | API / DB artefact | Test case | Status |
|----|--------------------------|------------------|--------------------|-----------|--------|
| US-01 | [title] | [component] | [endpoint/table] | TC-01 | Open |
| US-02 | [title] | [component] | [endpoint/table] | TC-02 | Open |
```

## 9. Definition of Ready / Definition of Done

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

## 10. Architecture

```markdown
## 10. Architecture

Architecture notation: C4 model (Context, Container, Component) via Mermaid.
At project and enterprise level, supplemented with arc42 sections: design
decisions (ADR-style) and quality scenarios. See [mermaid-snippets.md](mermaid-snippets.md).

### 10.1 C4 Context (Level 1)
[Mermaid C4 Context diagram — system in relation to users and external systems]

### 10.2 C4 Container (Level 2)
*(project, enterprise — mandatory; feature — optional)*
[Mermaid C4 Container diagram — containers (apps, services, datastores) and their relationships]

### 10.3 C4 Component (Level 3) — per container
*(enterprise — mandatory; project — optional)*
[Mermaid C4 Component diagram per relevant container]

### 10.4 Sequence diagrams — key flows
*(project, enterprise — mandatory; feature — optional)*
[Mermaid sequence diagrams for the key use cases]

### 10.5 Design decisions (arc42)
*(project, enterprise — mandatory)*
Architecture decisions in ADR style (Architecture Decision Records):

#### ADR-01: [Decision title]
- **Context:** [Why a decision is needed]
- **Decision:** [What was decided]
- **Status:** Proposed / Accepted / Superseded
- **Consequences:** [Positive and negative]
- **Alternatives considered:** [Which other options and why rejected]

### 10.6 Quality scenarios (arc42)
*(project, enterprise — mandatory)*
Concrete scenarios the design must be tested against:
- **Performance scenario:** "100 concurrent users do X, p95 latency < Y ms"
- **Availability scenario:** "On failure of component Z the system degrades to [behaviour]"
- **Security scenario:** "An anonymous attacker attempts [attack]; expected behaviour [response]"
```

## 11. Data model

```markdown
## 11. Data model

*(project, enterprise — mandatory; feature — optional)*

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

## 12. API & integration

```markdown
## 12. API & integration

### 12.1 API overview
Endpoints summarised; full spec in external OpenAPI file (reference below).

| Endpoint | Method | Auth | Summary | OpenAPI ref |
|----------|--------|------|---------|-------------|
| /path | GET/POST | [type] | [what it does] | [link/ref] |

**OpenAPI specification:** [link to openapi.yaml or reference]

### 12.2 Integrations
*(project, enterprise — mandatory; feature — if applicable)*
| System | Protocol | Direction | Frequency | Error handling |
|--------|----------|-----------|-----------|-----------------|
| [name] | REST/Kafka/SFTP | in/out/bi | [realtime/batch] | [behaviour on error] |

### 12.3 Data flows
[Mermaid data flow diagram or sequence diagram for critical integrations]
```

## 13. Non-functional requirements

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

## 14. Privacy-by-design

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

## 15. Security-by-design

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
*(enterprise — mandatory; project — optional)*
- Methods: STRIDE (security) + LINDDUN (privacy)
- Asset -> Threat -> Existing controls -> Residual risk -> Mitigation owner
[See security-by-design.md for template]

### 15.9 ASVS level
Target ASVS level: [L1/L2/L3] — [reason]
```

## 16. Risk register

```markdown
## 16. Risk register

*(project, enterprise — mandatory; feature — only "impacted teams")*

| ID | Risk | Likelihood | Impact | Score | Mitigation | Owner | Status |
|----|------|------------|--------|-------|------------|-------|--------|
| R-01 | [risk description] | L/M/H | L/M/H | [score] | [measure] | [name] | Open/Closed |
```

## 17. Deployment & rollback

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

## 18. Observability & logging

```markdown
## 18. Observability & logging

*(enterprise — mandatory; project — optional)*

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

## 19. Compliance evidence

```markdown
## 19. Compliance evidence

*(enterprise — mandatory)*

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

## 20. Migration & runbook

```markdown
## 20. Migration & runbook

*(enterprise — mandatory; project — optional)*

### 20.1 Migration plan
- Data to migrate: [volume, source, target]
- Cutover strategy: [big bang / phased]
- Reversibility: [yes/no — how]

### 20.2 Runbook
[Links to or inline runbooks for: deployment, rollback, incident response, data restore]
```

## 21. Approvals & sign-off

```markdown
## 21. Approvals & sign-off

| Role | Name | Date | Signature (digital) |
|------|------|------|----------------------|
| Product Owner | [name] | YYYY-MM-DD | |
| Architect | [name] | YYYY-MM-DD | |
| Security Officer | [name] | YYYY-MM-DD | |
| DPO (if GDPR applies) | [name] | YYYY-MM-DD | |
| Project sponsor | [name] | YYYY-MM-DD | |
```

---

## Author checklist

Before delivering, verify:
- [ ] All M-sections for the scenario present
- [ ] All E-sections present (enterprise)
- [ ] No `[PLACEHOLDER]` left unfilled
- [ ] User stories INVEST-checked
- [ ] Acceptance criteria as bullets, testable
- [ ] Traceability matrix complete
- [ ] NFRs measurable (Metric + Threshold + Verification)
- [ ] Privacy-by-design populated (not boilerplate)
- [ ] Security-by-design populated (not boilerplate)
- [ ] Mermaid diagrams render
- [ ] Table of contents present and accurate
- [ ] Approvals table filled
- [ ] `python scripts/validate.py <file> --scenario <scenario>` passes
