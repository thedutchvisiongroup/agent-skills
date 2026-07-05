# NFR Taxonomy (ISO/IEC 25010)

## Contents
- The 8 quality characteristics
- Measurable NFR format
- Worked examples per characteristic
- Compliance overlays (AVG, WCAG, NEN 7510, BIO, ISO 27001)

## The 8 quality characteristics

ISO/IEC 25010 defines software quality across 8 characteristics. Every FTD must address each, even if only to state "not applicable because [reason]".

| # | Characteristic | What it covers |
|---|----------------|----------------|
| 1 | Functional suitability | Correctness, completeness, appropriateness of features |
| 2 | Performance efficiency | Response time, throughput, resource utilisation under load |
| 3 | Compatibility | Interoperability, co-existence with other systems |
| 4 | Usability | Learnability, operability, accessibility, user error protection |
| 5 | Reliability | Maturity, availability, fault tolerance, recoverability |
| 6 | Security | Confidentiality, integrity, non-repudiation, accountability, authenticity |
| 7 | Maintainability | Modularity, reusability, analysability, modifiability, testability |
| 8 | Portability | Adaptability, installability, replaceability |

## Measurable NFR format

Every NFR must be expressed as:

```
Subject  — the system or component the NFR applies to
Attribute — the quality characteristic being measured
Metric   — how it is measured
Threshold — the value that must be met
Verification — how compliance is demonstrated
```

**Template row:**

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-XX | [system/component] | [quality attribute] | [what is measured] | [target value] | [test/inspection method] |

**Rule:** if you cannot fill all five fields, the NFR is not yet ready. Do not write "should be fast" or "should be secure". Write "p95 latency of /orders endpoint < 500 ms under 1000 concurrent users, verified by load test".

## Worked examples per characteristic

### 1. Functional suitability

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-01 | Invoice import | Completeness | % of valid rows imported | 100% of rows passing schema validation | Integration test with reference dataset |

### 2. Performance efficiency

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-02 | /orders endpoint (GET) | Response time | p95 latency | < 500 ms | Load test: 1000 concurrent users, ramp 60s |
| NFR-03 | /orders endpoint (POST) | Throughput | requests/sec sustained | ≥ 50 rps | Load test: 1000 concurrent users over 10 min |
| NFR-04 | API service | Resource utilisation | CPU usage at peak | < 70% | Monitoring during load test |

### 3. Compatibility

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-05 | API | Interoperability | OpenAPI 3.1 compliance | 0 violations | Linter (Spectral) in CI |
| NFR-06 | Web app | Browser support | Supported browsers | Latest 2 versions of Chrome, Firefox, Safari, Edge | Manual + BrowserStack |

### 4. Usability & Accessibility

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-07 | Web app | Accessibility | WCAG conformance level | 2.1 AA | Automated (axe) + manual audit |
| NFR-08 | Core user flow | Task completion time | Time for new user to complete [flow] | < 2 minutes | Usability test with 5 participants |
| NFR-09 | UI | Responsiveness | Layout breakpoints | Functional at 320px, 768px, 1024px, 1440px | Visual regression test |

### 5. Reliability

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-10 | API service | Availability | Uptime per month | ≥ 99.9% (≤ 43m downtime) | Monitoring dashboard (uptime check every 30s) |
| NFR-11 | API service | Fault tolerance | Behaviour on DB failure | Returns 503 with retry-after, no crash | Chaos test: kill DB, observe API |
| NFR-12 | API service | Recoverability | RTO after crash | < 5 minutes | Failover test |

### 6. Security

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-13 | API | Authentication | MFA coverage | 100% of admin endpoints require MFA | Penetration test |
| NFR-14 | Datastore | Confidentiality at rest | Encryption | AES-256 via KMS | Config inspection |
| NFR-15 | API | Vulnerability density | Critical CVEs in production | 0 | SCA + DAST scan in CI |
| NFR-16 | Web app | ASVS conformance | ASVS level | L2 | ASVS checklist audit |

### 7. Maintainability

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-17 | Codebase | Test coverage | Line coverage | ≥ 80% | CI pipeline (coverage report) |
| NFR-18 | Codebase | Code quality | Linting violations | 0 errors, ≤ 5 warnings per file | Linter in CI |
| NFR-19 | API | Modifiability | Time to add a new endpoint | < 1 day for a senior developer | Spike exercise |

### 8. Portability

| ID | Subject | Attribute | Metric | Threshold | Verification |
|----|---------|-----------|--------|-----------|-------------|
| NFR-20 | API service | Deployability | Deployment time | < 10 minutes (build + deploy to staging) | CI pipeline metrics |
| NFR-21 | Database | Replaceability | Vendor lock-in | SQL standard compliance, no vendor-specific stored procedures | Code inspection |

## Compliance overlays

Apply these as toggles based on the scenario and intake answers.

### AVG / GDPR (always address, even if to state "not applicable")

- **Lawful basis** for each personal data field (consent, contract, legitimate interest, legal obligation)
- **Retention schedule** per data category
- **Data subject rights flow** (access, rectification, erasure, portability)
- **DPIA decision** documented (see [privacy-by-design.md](privacy-by-design.md))

### WCAG 2.1 AA (default for any user-facing UI)

- Level AA conformance
- Automated (axe-core) + manual audit
- Covers: perceivable, operable, understandable, robust

### NEN 7510 (healthcare — toggle)

When the system processes patient data or operates in a healthcare-certified scope:
- Map controls to NEN 7510 control set
- Reference the organisation's NEN 7510 certificate scope
- Include patient data flow diagram

### BIO (Dutch government — toggle)

When the system serves a Dutch government organisation:
- Apply BIO2 baseline
- Document deviations from the baseline
- Reference the organisation's BIO implementation

### ISO 27001 (toggle)

When the organisation is ISO 27001 certified and the system is in scope:
- Reference the Statement of Applicability
- Map NFRs to Annex A controls where relevant

### EU AI Act (toggle, when AI is involved)

- Classify the AI component: not AI / minimal risk / limited risk / high risk / prohibited
- For high-risk: technical documentation, risk management system, data governance, logging, human oversight, conformity assessment

## Anti-patterns

- "The system should be fast" — no metric, no threshold
- "The system should be secure" — no threats, no framework
- "99% uptime" — over which window? Maintenance windows excluded?
- "User-friendly" — not measurable
- "Scales well" — from what to what?
- Listing NFRs without verification — how will we know it is met?
