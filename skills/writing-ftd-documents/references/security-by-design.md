# Security-by-Design

## Contents
- Foundational principles (Saltzer & Schroeder)
- Control classes (what to document in the FTD)
- ASVS levels
- Threat modeling (STRIDE + LINDDUN)
- Threat model template
- Mapping to compliance frameworks
- Anti-patterns
- FTD section template (copy-paste)

This reference is ALWAYS applied — every FTD has a security-by-design section, even if only to document that the system handles no sensitive data and the threat surface is minimal.

## Foundational principles (Saltzer & Schroeder)

| Principle | In the FTD |
|-----------|------------|
| Economy of mechanism | Keep design simple; avoid unnecessary complexity in security controls |
| Fail-secure defaults | On error, deny access; do not default to open |
| Complete mediation | Every access is checked, not just the first |
| Open design | Security does not depend on obscurity; algorithms and designs are public |
| Separation of privilege | Require multiple conditions/roles for sensitive operations |
| Least privilege | A role has the minimum permissions needed |
| Least common mechanism | Avoid shared channels that leak across users |
| Psychological acceptability | Security is usable; if it is hard, users will bypass it |

## Control classes

For each class: what to document, minimal acceptable controls, implementation options.

### Authentication & session management

- **Document:** auth method (OAuth2/OIDC/SAML/local), MFA requirement per role, session timeout, revocation flow
- **Minimal controls:** MFA for privileged accounts; session timeout ≤ 8h idle; revocation on password change
- **Options:** OAuth2/OIDC for SSO; device binding for mobile; WebAuthn for passwordless

### Authorization model

- **Document:** model (RBAC/ABAC/claims), decision points, policy store
- **Minimal controls:** enforcement in service layer (not just UI); unit tests per access rule; periodic policy review
- **Options:** RBAC for simple scopes; ABAC for complex attribute-based policies; OAuth2 scopes for API

### Secrets & key management

- **Document:** KMS/HSM usage, key rotation policy, secret storage
- **Minimal controls:** no secrets in repo; CI integrates secret scanning; rotation evidence
- **Options:** managed cloud KMS; dedicated HSM (BIO/ISO 27001 contexts); HashiCorp Vault

### Encryption in transit & at rest

- **Document:** organisational crypto policy reference; TLS version; algorithm for at-rest
- **Minimal controls:** TLS 1.2+ for all external traffic; AES-256 at rest; automated scanner results
- **Options:** mTLS for service-to-service; envelope encryption for sensitive fields

### Dependency & third-party management

- **Document:** SBOM (Software Bill of Materials); SCA cadence; gate policy
- **Minimal controls:** SCA results in CI; no critical CVEs in production; mitigation tickets for high CVEs
- **Options:** Syft/Trivy for SBOM; Dependabot/Renovate for updates

### CI/CD security gates

- **Document:** gate list (SAST/DAST/SCA/secret scan); runtime protections (WAF/EDR); monitoring dashboards
- **Minimal controls:** pipeline logs; SAST on every PR; DAST on staging
- **Options:** GitHub Advanced Security; SonarQube; OWASP ZAP; Snyk

### Audit logging & incident response

- **Document:** logging schema; retention; access control to logs; SIEM linkage; IR contacts; runbook attachment
- **Minimal controls:** log integrity checks; incident playbooks; alerting SLA
- **Options:** Splunk/Elastic for SIEM; PagerDuty for alerting; pre-built IR runbooks

### Input validation & output encoding

- **Document:** validation strategy (allowlist over blocklist); output encoding per context (HTML, JS, SQL)
- **Minimal controls:** framework-level validation; parameterised queries; contextual output encoding
- **Options:** JSON Schema for API input; CSP headers for XSS prevention

## ASVS levels

OWASP Application Security Verification Standard (ASVS) defines three verification levels. Choose the target in the FTD.

| Level | When | Examples |
|-------|------|----------|
| **ASVS Level 1** | Low-risk apps; no sensitive data; opportunistic | Marketing site, internal tool |
| **ASVS Level 2** | Apps handling personal data or business-critical functions; standard enterprise default | Most enterprise apps |
| **ASVS Level 3** | High-risk apps; critical infrastructure; large-scale financial or health data | Payment systems, healthcare, government |

Document the chosen level and the verification method (audit, penetration test, automated check).

## Threat modeling (STRIDE + LINDDUN)

Use **STRIDE** for security threats and **LINDDUN** for privacy threats. For enterprise scenarios, both are mandatory. For project, optional but recommended. For feature, only when the change touches security boundaries.

### STRIDE (security)

| Category | Threat example | Mitigation |
|----------|----------------|------------|
| **S**poofing | Attacker impersonates a user | Strong auth, MFA |
| **T**ampering | Attacker modifies data in transit or at rest | Integrity checks, mTLS, signatures |
| **R**epudiation | User denies an action | Audit logs, non-repudiation |
| **I**nformation disclosure | Sensitive data leaked to unauthorised party | Encryption, access control |
| **D**enial of service | Service overwhelmed | Rate limiting, autoscaling |
| **E**levation of privilege | User gains unauthorised permissions | Least privilege, RBAC/ABAC |

### LINDDUN (privacy)

| Category | Threat example | Mitigation |
|----------|----------------|------------|
| **L**inkability | Two records can be linked to one person | Pseudonymisation, data minimisation |
| **I**dentifiability | Records identify a person without their name | Anonymisation, aggregation |
| **N**on-repudiation | Cannot deny processing of personal data | Audit logs, processing records |
| **D**etectability | Presence of a person is detectable | Mix networks, padding |
| **D**isclosure of information | Personal data exposed | Encryption, access control |
| **U**nawareness & unintervenability | User unaware of processing or cannot intervene | Transparency, DSR flow |
| **N**on-compliance | Processing violates legal basis | Lawful basis documentation |

## Threat model template

```markdown
### Threat model

**Scope:** [which component/flow]

#### STRIDE
| Asset | Threat (category) | Existing controls | Residual risk | Mitigation owner |
|-------|-------------------|-------------------|---------------|------------------|
| [asset] | [threat description] (Spoofing) | [controls] | L/M/H | [name] |

#### LINDDUN
| Asset | Privacy threat (category) | Existing controls | Residual risk | Mitigation owner |
|-------|----------------------------|-------------------|---------------|------------------|
| [asset] | [threat description] (Linkability) | [controls] | L/M/H | [name] |
```

## Mapping to compliance frameworks

| Control | OWASP ASVS / Top 10 | NEN 7510 | BIO | ISO 27001 |
|---------|----------------------|----------|-----|-----------|
| Authentication | ASVS V2 | §6.1 | U-03 | A.5.17-5.18 |
| Authorization | ASVS V4 | §6.2 | U-04 | A.5.15-5.18 |
| Encryption at rest | ASVS V6 | §6.6 | U-15 | A.8.24 |
| Encryption in transit | ASVS V9 | §6.6 | U-15 | A.8.24 |
| Logging & monitoring | ASVS V7 | §7.3 | U-21 | A.8.15-8.16 |
| Dependency scanning | Top 10 A06 | §6.7 | U-17 | A.5.20-5.21 |
| Input validation | Top 10 A03 | §6.5 | U-10 | A.8.28 |
| Secrets management | ASVS V6 | §6.4 | U-16 | A.5.17, A.8.25 |

## Anti-patterns

| Anti-pattern | Example | Fix |
|--------------|---------|-----|
| "We encrypt everything" | No specifics | Specify algorithm, key management, rotation, evidence |
| No ASVS level | "Secure by default" | Pick L1/L2/L3 and verify |
| No threat model | Generic "we considered threats" | Run STRIDE + LINDDUN; document the table |
| Auth only at UI | API trusts the UI to enforce | Enforce in service layer; test directly |
| Secrets in repo | Hardcoded API keys | Vault/KMS; secret scanning in CI |
| No log retention policy | "Logs are kept somewhere" | State retention, access control, integrity |
| Skipped for "internal" tool | Internal tools are trusted | Internal tools are also attack surface; document why controls are lighter |

## FTD section template (copy-paste)

```markdown
## 15. Security-by-design

### 15.1 Authentication & session management
- Method: [OAuth2/OIDC/...]
- MFA required for: [roles/scope]
- Session policy: [timeout, revocation]

### 15.2 Authorization model
- Model: [RBAC/ABAC/claims]
- Decision points: [where enforced]
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
[See STRIDE + LINDDUN template above]

### 15.9 ASVS level
Target ASVS level: [L1/L2/L3] — [reason]
Verification method: [audit / pentest / automated]
```
