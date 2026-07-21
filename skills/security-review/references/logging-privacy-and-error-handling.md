# Logging, Privacy and Error Handling

Read this during Phase 4, class 10. Security Logging and Alerting Failures are A09 on the OWASP Top 10 (2025); Mishandling of Exceptional Conditions is A10 — new in 2025. Sensitive-info exposure is CWE-200 (#20); log injection of sensitive data CWE-532; error info leaks CWE-209. Anchor: ASVS V16 (Security Logging and Error Handling), V14 (Data Protection).

## Contents

- What It Is
- Sensitive Data in Logs
- Error Handling and Information Disclosure
- Exceptional Conditions (A10)
- Missing Security Logging
- Privacy and Data Minimization
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

Two failure directions:

1. **Too much** — sensitive data written to logs, errors, and telemetry (disclosure).
2. **Too little** — security-relevant events NOT logged, so attacks are invisible (detection failure).

Both are findings. The first leaks to anyone with log access; the second blinds the defenders.

## Sensitive Data in Logs

Detection patterns:

1. **Direct sensitive logging** — passwords, tokens, session ids, API keys, full connection strings, private keys, credit-card/PAN, national ids, health data appearing in log statements (any level — DEBUG included; debug logs get shipped).
2. **Object dumping** — logging whole request/response/user objects that CONTAIN sensitive fields (the field list is the tell; check serializers/`toString` equivalents for redaction).
3. **Auth flows** — logging credentials or tokens at login/reset/refresh ("user X failed with password …" is a classic).
4. **Error paths** — exception handlers logging request bodies/headers on failure (bodies contain credentials).
5. **Third-party telemetry** — sensitive values sent to analytics/error trackers (crash reports with request context, session-replay capturing inputs, analytics events with PII).
6. **URLs and query strings logged** — tokens/PII in query params land in access logs (see also secrets reference).
7. **Log injection** — untrusted input logged raw (CRLF forging log entries, terminal escape injection in CLI logs).

**Judge by content, not by level:** `log.debug(password)` is the same finding as `log.info(password)`.

## Error Handling and Information Disclosure

1. **Stack traces / framework debug pages returned to clients** — paths, code, queries, config in responses (CWE-209).
2. **Verbose backend errors echoed** — SQL errors, parser messages, internal hostnames/IPs in API responses.
3. **Differential errors enabling oracles** — distinct messages/timing for "user not found" vs "wrong password" (see authentication reference), "invalid signature" vs "expired".
4. **Framework error handlers** — default error pages left enabled in prod config (see configuration reference); catch-all handlers that re-raise with internals attached.
5. **Health/status endpoints** disclosing versions, internals, dependency trees.

## Exceptional Conditions (A10:2025)

New in OWASP 2025 — how code behaves when things go wrong:

1. **Fail-open** — on error, access is GRANTED (`except: allow`, empty catch around auth checks, verification skipped on exception). **Critical pattern: hunt for catch blocks around security decisions.**
2. **Swallowed exceptions** — empty catch blocks, `catch: pass` on operations whose failure MUST be handled (payment, audit, authz).
3. **Inconsistent state on partial failure** — multi-step operations without rollback (charged but not recorded; created but not committed).
4. **Unchecked return values** on security-relevant calls (verification result ignored).
5. **Resource cleanup on error paths** — locks/sessions/files left open (availability + state corruption).

## Missing Security Logging

Check whether these events are logged (absence = finding, usually Medium):

- Authentication success/failure, MFA events, password changes/resets
- Authorization failures (access-denied decisions)
- Privilege/role changes, account creation/deletion
- Sensitive operations (export, payment, config change, API-key issuance)
- Input validation failures on security boundaries, suspicious patterns

**Quality of logs:** logged events need WHO (actor), WHAT, WHEN, and correlation ids — without leaking secrets. Logs must be integrity-protected destinations (append-only / shipped off-box) — if code writes security logs only to the same attackable box/db, note it.

## Privacy and Data Minimization

1. **PII over-collection/over-exposure** — API responses serializing full records (cross-reference API3:2023 excessive data exposure).
2. **PII at rest unprotected** — sensitive fields stored without encryption/masking where the architecture requires it.
3. **Retention/deletion absent** — no lifecycle for personal data, backups with live PII beyond policy, deleted-account data retained.
4. **Cross-border/third-party flows** — PII sent to third parties without a visible need.
5. **Client-side exposure** — sensitive data in URLs, localStorage, browser cache, screenshots (mobile).

Privacy findings from static code are necessarily partial — record assumptions in "Could NOT verify" (retention policies, DSR flows are often process, not code).

## False-Positive Guidance

Do NOT report when:

- A verified redaction/filter layer scrubs sensitive fields BEFORE logging (trace it — filter lists that omit fields are findings).
- Debug logging is provably gated to non-prod environments (verify the gating mechanism, not the comment).
- The framework's error handling is configured for generic client errors + internal detail logging (the correct split).
- Logged identifiers are pseudonymous tokens with no standalone value.

## Mandatory Online Research Triggers

- Framework default error pages/log formats for the detected version (what leaks by default).
- Error-tracker/telemetry SDK behavior: what context they attach automatically (request bodies? headers?).
- Whether a field type counts as regulated PII in the apparent jurisdiction context (ask the user if classification is unclear).

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| Sensitive data in logs | CWE-532/200 (#20, 2025) | A09:2025 |
| Error message info leaks | CWE-209/210 | A10:2025 / A02:2025 |
| Stack traces to client | CWE-209/215 | A10:2025 |
| Fail-open on exception | CWE-636/703 | A10:2025 / A01:2025 |
| Swallowed exceptions | CWE-390/1069 | A10:2025 |
| Missing security-event logging | CWE-778/223 | A09:2025 |
| Log injection (CRLF) | CWE-117/93 | A09:2025 |
| Excessive PII exposure | CWE-200/359 | A02:2025 / API3:2023 / ASVS V14 |
| ASVS | V16 (Security Logging and Error Handling), V14 (Data Protection) | — |
