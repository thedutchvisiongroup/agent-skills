# Access Control and Authorization

Read this during Phase 4, class 3. Broken Access Control is A01 on the OWASP Top 10 (2025) — the top application risk. Missing/Incorrect Authorization are CWE-862 (#4), CWE-863 (#17), CWE-284 (#19), CWE-639 (#24) on the 2025 Top 25. This is the class SAST tools miss most: it requires understanding who MAY do what, not just what the code does.

## Contents

- What It Is
- The Core Questions
- Detection Patterns
- IDOR / BOLA
- Mass Assignment (Object Property Level)
- Privilege Escalation Paths
- Function-Level Authorization
- Business-Flow Abuse
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

Authorization answers: **"Is THIS actor allowed to perform THIS action on THIS object?"** It breaks when any of the three checks (actor, action, object) is missing, client-controlled, or assumed.

**Universal detection shape:**

```
request SOURCE (user-controlled id/role/action) → resource lookup or privileged operation (sink)
      without a verified authorization decision for THIS actor+action+object
```

Authentication ("who are you") is the neighboring class — see `authentication-and-session-management.md`. Never confuse the two: authenticated ≠ authorized.

## The Core Questions

For every handler/route/operation in scope, answer:

1. **Is there an authentication requirement?** (missing entirely = CWE-306, Top 25 #21)
2. **Is there an authorization check at all?** (missing = CWE-862)
3. **Is the check correct?** (wrong role, wrong comparison, client-side-only = CWE-863)
4. **Does it cover THIS object?** (object-level = IDOR/BOLA)
5. **Does it cover THESE fields?** (property-level = mass assignment)
6. **Can it be bypassed?** (alternate path, parameter tampering, HTTP method switch, direct call)

## Detection Patterns

1. **User-controlled identifiers used directly in lookups** — request id/key → database fetch → return, with no ownership/tenancy check. Trace where the id came from.
2. **Roles/permissions read from the request** — role, isAdmin, or permission claims taken from request body/params/headers (not from the server-side session/token claims).
3. **Client-side-only enforcement** — hidden UI elements, disabled buttons, checks only in frontend code; the endpoint itself unguarded.
4. **Middleware gaps** — auth middleware registered per-route with exclusions/wildcards; new routes added OUTSIDE the protected group; HTTP-method fallthrough (GET guarded, POST not).
5. **Negated/fallthrough logic** — checks of the form `if not admin: pass` (missing deny), `return` forgotten after a failed check, exceptions swallowed so the operation continues.
6. **Default-allow configurations** — frameworks/routes that are public unless explicitly protected.
7. **Multi-tenancy leaks** — queries filtered by user input tenant id instead of the authenticated session's tenant; shared caches keyed without tenant.

## IDOR / BOLA

Insecure Direct Object Reference (Broken Object Level Authorization, API1:2023 — the #1 API risk):

- Sequential/guessable object ids + missing per-object check = enumeration. Note: random UUIDs reduce guessing but do NOT replace the authorization check (ids leak via logs, referers, sharing).
- **Verify the check compares the object's owner/tenant to the authenticated principal** — not to a user id supplied in the request (that IS the vulnerability, CWE-639).
- Batch/export/download endpoints and "helper" endpoints (preview, share, print) are classic spots where the check is forgotten.

## Mass Assignment (Object Property Level)

- Request body bound wholesale to a model/entity (bind-all, `Model(request)`, spread of request into update) lets clients set fields they shouldn't: `role`, `isAdmin`, `price`, `ownerId`.
- **Guard**: explicit allow-list of bindable/updatable fields per operation, or DTOs that contain only safe fields.
- Check both create AND update paths, and PATCH/PUT semantics. API3:2023 (Broken Object Property Level Authorization) covers this.

## Privilege Escalation Paths

- **Vertical**: user → admin. Check admin-only operations for enforced role gates; check "self-service" endpoints that accept role/permission changes.
- **Horizontal**: user A → user B's data/actions (IDOR family).
- **Password-reset / invite / impersonation flows**: tokens without expiry/binding, impersonation without audit+authorization, invite acceptance creating privileged roles.
- **Default/seed accounts and backdoor users** in code/fixtures.

## Function-Level Authorization

- Administrative/sensitive functions reachable without function-level checks (API5:2023): hidden endpoints, "internal" endpoints exposed on the same server, debug/actuator/actuator-style endpoints, GraphQL mutations unguarded while queries are guarded.
- Check route registration against the authorization configuration — enumerate, don't sample.

## Business-Flow Abuse

Driven by the Before-You-Start sensitive-operations answers. No universal pattern — check for:

- **Step skipping**: later steps of a multi-step flow callable directly (payment confirmed before payment; order placed skipping verification).
- **State tampering between steps**: price/quantity/recipient re-supplied at confirm-time and trusted.
- **Race conditions**: limited resources (coupons, stock, votes, transfers) claimed concurrently — check for atomic operations/transactions/locks; TOCTOU between check and use.
- **Limit/quota bypass**: limits enforced client-side or per-request only.
- **Negative/overflow values**: amounts, quantities, discounts below zero or beyond maxima.

## False-Positive Guidance

Do NOT report when:

- A verified, centralized authorization layer provably covers the operation (trace its registration — don't take it on faith).
- The object lookup is scoped by construction to the authenticated principal (e.g., query constrained by session-derived owner id) — verify the scoping key comes from the session, not the request.
- The endpoint is intentionally public AND returns only public data (state why it's safe in one line if it LOOKS sensitive).
- Field allow-lists/DTOs verifiably exclude sensitive properties.

When authorization is framework-magic you cannot resolve → Phase 5 research or "Could NOT verify". Never guess "probably covered".

## Mandatory Online Research Triggers

- The framework's authorization model and defaults (default-allow vs default-deny; middleware semantics) for its version.
- Whether the detected framework binds request data to models by default (mass-assignment surface differs per framework/version).
- Known authorization-bypass advisories for the detected framework/router version.

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| Missing authorization | CWE-862 (Top 25 #4, 2025) | A01:2025 |
| Incorrect authorization | CWE-863 (#17) | A01:2025 |
| Improper access control (general) | CWE-284 (#19) | A01:2025 |
| User-controlled key bypass (IDOR) | CWE-639 (#24) | A01:2025 / API1:2023 BOLA |
| Missing authentication for critical function | CWE-306 (#21) | A07:2025 / API2:2023 |
| Mass assignment | CWE-915 | API3:2023 |
| Function-level authz missing | CWE-285/862 | API5:2023 |
| Race condition (TOCTOU) | CWE-367 | A06:2025 Insecure Design |
| ASVS | V8 (Authorization), V2 (Validation and Business Logic) | — |
