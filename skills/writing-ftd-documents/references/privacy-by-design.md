# Privacy-by-Design

## Contents
- Foundational principles (Cavoukian, 7)
- Data inventory template
- DPIA triggers and decision
- Data subject rights flow
- Retention & deletion
- Mapping to compliance frameworks
- Anti-patterns
- FTD section template (copy-paste)

This reference operationalises Article 25 GDPR (Data Protection by Design and by Default) into concrete FTD fields. It is ALWAYS applied — even when no personal data is obviously involved, the FTD must explicitly state and justify that position.

## Foundational principles (Cavoukian, 7)

For each principle: what it means, what to document in the FTD, and the acceptance criterion.

### 1. Proactive not reactive (risk-based)

- **Means:** privacy risks are anticipated and mitigated before they materialise, not after.
- **Document in FTD:** risk register excerpt; DPIA decision (Y/N + reference); threat model output (LINDDUN).
- **Acceptance:** DPIA completed where triggered; mitigations tracked to closure or accepted residual risk.

### 2. Privacy as default

- **Means:** the system collects and retains the minimum by default; the user does not have to act to protect their privacy.
- **Document in FTD:** default data collection settings per flow; opt-in vs opt-out design; cookie/consent management.
- **Acceptance:** defaults collect only fields marked REQUIRED; UI shows privacy-friendly defaults; automated tests verify opt-out state.

### 3. Privacy embedded into design (data minimisation, purpose limitation)

- **Means:** privacy is part of the core design, not bolted on.
- **Document in FTD:** data inventory table (field, category, purpose, lawful basis, retention).
- **Acceptance:** every field has a documented purpose and lawful basis; DB schema contains no PII columns without justification.

### 4. End-to-end security (pseudonymisation, retention, breach linkage)

- **Means:** privacy protections cover the full data lifecycle, not just storage.
- **Document in FTD:** pseudonymisation approach; retention schedule; breach detection and notification linkage.
- **Acceptance:** pseudonymisation technique documented; retention job exists and tested; breach runbook linked.

### 5. Full functionality (positive-sum)

- **Means:** privacy does not require disabling legitimate functionality — both can coexist.
- **Document in FTD:** trade-offs log and accepted residuals.
- **Acceptance:** explicit justification for any trade-off; stakeholder sign-off recorded.

### 6. Visibility & transparency

- **Means:** processing is visible to the data subject and accountable to regulators.
- **Document in FTD:** user notices; logging of processing activities; data subject request (DSR) handling flows.
- **Acceptance:** privacy notice published; DSR flow documented with SLA (default 30 days); auditable logs retained per schedule.

### 7. Respect for user privacy (user controls)

- **Means:** the user can exercise their rights: access, rectification, erasure, portability, restriction, objection.
- **Document in FTD:** DSR endpoints; data export format; erasure verification method.
- **Acceptance:** automated export for portability; erasure job with verification audit record.

## Data inventory template

Every FTD that processes personal data must include this table.

| Field | Category | Special category? | Purpose | Lawful basis | DPIA trigger? | Retention | Pseudonymised? |
|-------|----------|-------------------|---------|--------------|---------------|-----------|-----------------|
| email | contact | no | account recovery | contract | no | 2 years after last login | no |
| IP address | technical | no | security, fraud | legitimate interest | no | 30 days | no |
| health_score | special (Art. 9) | yes | triage | explicit consent | YES | 1 year | yes (pseudonymised) |

**Lawful basis values:** consent, contract, legal obligation, vital interests, public task, legitimate interest.

**Special categories (Art. 9):** racial/ethnic origin, political opinions, religious/philosophical beliefs, trade union membership, genetic data, biometric data (for identification), health data, sex life/sexual orientation. These require a stricter lawful basis (typically explicit consent) and almost always trigger a DPIA.

## DPIA triggers and decision

A Data Protection Impact Assessment is REQUIRED when any of these apply (per Autoriteit Persoonsgegevens guidance):

- Large-scale automated decision-making with legal or similarly significant effects
- Processing of special categories of data (Art. 9) on a large scale
- Systematic monitoring of publicly accessible areas on a large scale
- Large-scale processing of location data or tracking
- Use of novel technologies (e.g. AI/ML for profiling)
- Data combinations that significantly increase the risk to data subjects
- Processing involving vulnerable individuals (children, patients, employees)

### DPIA decision field in the FTD

```
DPIA required? yes/no
Reason: [concrete assessment against the triggers above]
DPIA reference: [link/ID — if "yes"]
Outcomes: [summary of mitigating measures]
DPO sign-off: [name, date]
```

### DPIA scoping checklist (when triggered)

- Processing description (what, why, how)
- Necessity & proportionality assessment
- Risks to rights and freedoms of data subjects
- Mitigation list
- Residual risk and acceptance
- DPO sign-off

**FTD linkage:** every DPIA outcome must produce explicit acceptance criteria in the FTD. Example: "Must implement pseudonymisation approach X" or "Do not deploy until mitigation Y is verified".

## Data subject rights flow

Document how each right is fulfilled:

| Right | Endpoint / process | SLA | Verification |
|-------|--------------------|-----|--------------|
| Access (Art. 15) | GET /account/export | 30 days | Audit log entry per request |
| Rectification (Art. 16) | PATCH /account | 30 days | Audit log + email notification |
| Erasure (Art. 17) | DELETE /account | 30 days | Erasure job + verification audit record |
| Portability (Art. 20) | GET /account/export?format=json | 30 days | JSON schema validation |
| Restriction (Art. 18) | POST /account/restrict | 30 days | Status flag check |
| Objection (Art. 21) | POST /account/object | 30 days | Processing halt verification |

## Retention & deletion

- **Retention schedule:** documented per data category (reference or inline table)
- **Deletion mechanism:** automated job with periodicity, manual fallback, and verification
- **Verification:** audit record confirming deletion, including backups (backups must honour retention within their own cycle)

## Mapping to compliance frameworks

| Principle / control | AVG / GDPR | NEN 7510 (healthcare) | BIO (government) | ISO 27001 |
|---------------------|------------|------------------------|------------------|-----------|
| Data inventory | Art. 30 | §4.3 | Baseline measure | A.5.12 |
| DPIA | Art. 35 | §6.4 | Topic in baseline | A.5.34 |
| Lawful basis | Art. 6, 9 | §4.4 | — | — |
| Retention | Art. 5(1)(e) | §4.5 | Baseline measure | A.5.34 |
| Data subject rights | Art. 15-22 | §6.5 | — | — |
| Pseudonymisation | Art. 25, 32 | §6.6 | Baseline measure | A.8.25 |
| Breach notification | Art. 33-34 | §7.3 | Incident management | A.5.24-5.28 |

## Anti-patterns

| Anti-pattern | Example | Fix |
|--------------|---------|-----|
| "We encrypt everything" | No specification of what, where, how, keys | Specify algorithm, KMS/HSM, rotation, test evidence |
| Boilerplate DPIA missing | "Privacy is taken into account" with no DPIA decision | State Y/N with reasoning; attach DPIA if Y |
| No measurable controls | "Privacy is respected" | Use the data inventory; map each field to purpose, basis, retention |
| No retention | Data kept indefinitely "just in case" | Document retention per category; automate deletion |
| No DSR flow | "Users can contact support" | Document endpoint/process with SLA |
| Hidden special categories | Health data stored without Art. 9 basis | Identify in inventory; apply explicit consent + DPIA |
| Silent AI profiling | ML model uses personal data without DPIA | Trigger DPIA; document lawful basis for profiling |

## FTD section template (copy-paste)

```markdown
## 14. Privacy-by-design

### 14.1 Processing of personal data
Are personal data processed? [yes/no]
If no, justification: [why not]

### 14.2 Data inventory
| Field | Category | Special category? | Purpose | Lawful basis | DPIA required? | Retention | Pseudonymised? |
|-------|----------|-------------------|---------|--------------|-----------------|-----------|-----------------|
| [field] | [category] | yes/no | [purpose] | [lawful basis] | yes/no | [period] | yes/no |

### 14.3 DPIA
- DPIA required? [yes/no — reason]
- DPIA reference: [link/ID]
- Outcomes: [mitigating measures]
- DPO sign-off: [name, date]

### 14.4 Privacy principles applied
- Data minimisation: [how]
- Purpose limitation: [how]
- Pseudonymisation/anonymisation: [how, or n/a with reason]
- Privacy-friendly defaults: [how]
- Data subject rights: [access/rectification/erasure/portability — flow per table in §DSR]

### 14.5 Retention & deletion
- Retention policy: [reference or table]
- Deletion process: [automated job, periodicity, verification]
- Backup strategy: [how backups are included in retention]

### 14.6 Privacy threat model (LINDDUN)
*(enterprise — mandatory)*
[Asset → privacy threat (linkability, identifiability, ...) → existing controls → residual risk → mitigation owner]
```
