# API Security and SSRF

Read this during Phase 4, class 9. Anchored to the OWASP API Security Top 10 (2023). SSRF is CWE-918 (#22 on the CWE Top 25, 2025); unrestricted upload CWE-434 (#12); unthrottled allocation CWE-770 (#25). This reference covers API-specific shapes — the underlying authn/authz mechanics live in their own references.

## Contents

- What It Is
- API Surface Review (inventory first)
- BOLA and Property-Level Patterns (pointer)
- Broken Authentication Patterns (API shape)
- Unrestricted Resource Consumption
- SSRF
- File Upload and Download
- Unsafe Consumption of Third-Party APIs
- GraphQL-Specific
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

APIs expose object graphs and business functions directly. The recurring failure: the API trusts client-supplied object references, properties, volumes, and URLs far more than a UI ever would. Review each endpoint as: **input → authorization → operation → response shape**.

## API Surface Review (inventory first)

Before judging endpoints, enumerate them (Improper Inventory Management, API9:2023):

- All routes/handlers, including: versioned leftovers (`/v1/`, `/api/old/`), debug/health/metrics/actuator endpoints, internal-only endpoints on public listeners, staging hosts referenced in code, undocumented-but-registered routes.
- **Orphaned/legacy endpoints** found in code but not in docs/config → report (they skip newer controls).
- Check that sensitive endpoints (admin, export, internal) are not reachable on the public surface (deployment-dependent → "Could NOT verify" if unknowable from code).

## BOLA and Property-Level Patterns (pointer)

- **BOLA/IDOR (API1:2023)** and **Broken Function Level Authorization (API5:2023)**: mechanics in `access-control-and-authorization.md`. API shape to check here: object ids in PATH/body on EVERY endpoint — enumerate them all.
- **Broken Object Property Level Authorization (API3:2023)**: responses that serialize the WHOLE object when the client needs three fields (excessive data exposure — PII/internal fields leaking); mass assignment on write. Check serializers/DTOs per endpoint, not globally.

## Broken Authentication Patterns (API shape)

- API keys/tokens accepted in URLs (logged by proxies), in client storage, or without expiry/rotation.
- Endpoints mixing auth schemes where one is weaker (basic auth fallback on a token API).
- Missing binding between token and audience/scope (a token for service A accepted by service B).
- Mechanics in `authentication-and-session-management.md`.

## Unrestricted Resource Consumption (API4:2023)

Detection patterns:

1. **No rate limiting** on: auth endpoints (login/reset/OTP — brute force), expensive operations (search, export, report generation), and the API globally.
2. **Unbounded pagination** — client-controlled `limit`/`per_page` without a maximum.
3. **Unbounded input sizes** — no body-size limits, no string/array length caps, unbounded file sizes.
4. **Expensive operations without guards** — regex on user input (ReDoS shapes), N+1-exposed queries via include/expand parameters, unbounded date ranges, fan-out operations (notifications to N recipients).
5. **No timeouts** on outbound calls (threads hang → exhaustion).

## SSRF (API7:2023)

Server-Side Request Forgery: user-influenced data controls WHERE the server connects.

**Detection shape:**

```
user-controlled URL/host/ip/webhook/callback SOURCE → server-side HTTP client / fetch / redirect-follow (sink)
      without allow-list validation of scheme+host+resolved-IP
```

1. **Sinks**: server HTTP clients, URL fetchers, image/file fetch-by-URL, webhooks/callback URLs, PDF/screenshot renderers, "import from URL", OAuth/OIDC discovery URLs, URL preview/unfurl features, XML external entities (XXE is SSRF's cousin — see injection reference).
2. **Guard that works**: parse the URL → allow-list scheme (`https`) AND host → resolve DNS and reject private/reserved ranges (RFC1918, loopback, link-local, cloud metadata `169.254.169.254`) → re-validate after redirects (or disable redirects).
3. **Bypass shapes to check**: redirects to internal targets, DNS rebinding (TOCTOU between check and connect), alternate IP notations (decimal/hex/octal), IPv6 loopback, URL parser inconsistencies between validator and fetcher, userinfo tricks (`https://allowed@evil/`).
4. **Blind SSRF still matters**: no response needed — internal port scanning and metadata theft work blind.

## File Upload and Download

Unrestricted upload is CWE-434 (Top 25 #12):

1. **Type checks** — extension-only or client-supplied `Content-Type` trusted; **guard**: server-side magic-byte/content sniffing + extension allow-list.
2. **Storage location** — uploads inside the web root / executable paths → stored code execution; check where files land and how they're served (direct execution vs attachment/download).
3. **Names and paths** — user-controlled filenames (path traversal on write — see injection reference), missing randomization (overwrites, squatting).
4. **Content risks** — SVG/HTML served same-origin (stored XSS via upload), archives extracted without entry validation (zip slip, zip bombs), image parsers on hostile input (research parser CVEs — Phase 5).
5. **Size/quantity limits** — absent → resource consumption (above).
6. **Downloads** — user-controlled file paths/ids for download endpoints (traversal + IDOR combined).

## Unsafe Consumption of Third-Party APIs (API10:2023)

The mirror image: data FROM external APIs is untrusted.

1. Responses from third parties used without validation/encoding (injection/XSS second-order — data flows INTO your sinks).
2. No integrity/schema validation on webhooks (missing signature verification).
3. TLS verification disabled for outbound calls (see cryptography reference).
4. Sensitive data sent to third parties beyond need (privacy — see logging reference).
5. No timeouts/retries-with-backoff/circuit-breaking on outbound calls (resilience → resource consumption).

## GraphQL-Specific

1. **Introspection enabled in production** — full schema disclosure (Low/Medium; aids attackers).
2. **Query depth/complexity unlimited** — nested-query DoS.
3. **Batching abuse** — many operations in one request (brute force amplification, e.g., OTP guessing).
4. **Field-level authorization missing** — resolver-level checks absent on sensitive fields (BOLA at field granularity).
5. **Persisted queries / suggestions** leaking schema info.

## False-Positive Guidance

Do NOT report when:

- The SSRF guard verifiably does parse→allow-list→DNS-resolve→range-reject, including redirect handling.
- Rate limiting is verifiably enforced at a gateway/edge you can see in config; if claimed-but-invisible → "Could NOT verify".
- Upload validation does content sniffing + allow-list + safe storage path.
- Pagination/limits are enforced by the framework with a hard maximum (verify the default for the version — research).

## Mandatory Online Research Triggers

- Framework default limits (body size, pagination, rate limiting) for the detected version.
- Parser CVEs for file/image/archive libraries in use (Phase 5 + advisory lookup).
- Cloud metadata endpoint specifics if SSRF + cloud deployment is detected.
- GraphQL library defaults (introspection, depth limiting) per version.

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| BOLA / IDOR | CWE-639/862 | API1:2023 / A01:2025 |
| Excessive data exposure | CWE-200/213 | API3:2023 |
| Missing rate limiting / unbounded input | CWE-770/307/400 | API4:2023 |
| SSRF | CWE-918 (Top 25 #22, 2025) | API7:2023 |
| Unrestricted upload | CWE-434 (#12) | A05:2025 / API8:2023-adjacent |
| Inventory gaps (legacy/debug endpoints) | CWE-1059/489 | API9:2023 / A02:2025 |
| Unvalidated third-party data | CWE-20/345 | API10:2023 |
| ASVS | V4 (API and Web Service), V5 (File Handling) | — |
