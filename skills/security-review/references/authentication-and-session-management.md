# Authentication and Session Management

Read this during Phase 4, class 4. Authentication Failures are A07 on the OWASP Top 10 (2025); CSRF is CWE-352 — #3 on the CWE Top 25 (2025). Anchors: ASVS V6 (Authentication), V7 (Session Management), V9 (Self-contained Tokens), V10 (OAuth/OIDC).

## Contents

- What It Is
- Password Storage and Handling
- Login and Account-Recovery Flows
- Session Management
- Tokens (JWT and friends)
- OAuth / OIDC
- CSRF
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

Authentication answers "who are you?" — and breaks through weak credential storage, brute-force/oracle-enabling flows, session lifecycle failures, and token misuse. Authorization (the neighboring class) is covered in `access-control-and-authorization.md`.

**Universal detection shape:**

```
credential/token SOURCE → verification or session-establishment logic (sink)
      with weak storage, weak comparison, missing binding, or missing lifecycle controls
```

## Password Storage and Handling

Detection patterns:

1. **Wrong hash function** — fast/general-purpose hashes for passwords (MD5, SHA-1, SHA-2 family) instead of password-specific KDFs (argon2id, bcrypt, scrypt, PBKDF2 with adequate work factor). Research current recommended work factors (Phase 5) — they drift upward.
2. **Reversible storage** — encrypted (not hashed) passwords, plaintext columns, passwords in backups/logs.
3. **Salt/pepper mistakes** — no salt, static/global salt, salt stored wrong, home-grown "hash+secret string" schemes.
4. **Comparison oracles** — non-constant-time comparison of secrets/tokens where timing is attacker-observable (mostly tokens; lower severity for hashed passwords).
5. **Passwords in transit inside the app** — passwords logged, put in URLs/query strings, emailed, stored in client storage.

## Login and Account-Recovery Flows

1. **User enumeration** — different responses/timing for "no such user" vs "wrong password" on login, registration, and reset flows.
2. **Missing brute-force defenses** — no rate limiting, lockout, or throttling on login/reset/OTP endpoints (see also `api-security-and-ssrf.md` resource consumption).
3. **Reset-token weaknesses** — predictable tokens (low entropy, sequential, derived from user data), no expiry, reusable, not bound to the account, delivered over a user-controllable host (host-header poisoning in reset links).
4. **MFA weaknesses** — MFA verification skippable via direct navigation, OTP without attempt limits, recovery codes unprotected, MFA "remember device" without binding.
5. **Registration/invite** — self-assigned roles at registration, invite links without expiry.

## Session Management

1. **Session id quality** — ids from weak randomness, sequential, or user-supplied.
2. **Fixation** — session id NOT rotated at login/privilege change. This is a classic; check the login path explicitly.
3. **Cookie flags** — session cookies missing `HttpOnly`, `Secure`, `SameSite`; overly broad `Domain`/`Path`.
4. **Lifecycle** — no absolute/idle timeout, no server-side invalidation at logout/password change (stateful), logout only client-side.
5. **Concurrent-session & device handling** for sensitive apps — note gaps as observations.

## Tokens (JWT and friends)

Detection patterns — these recur across ecosystems:

1. **Signature verification disabled or optional** — parsing claims without verifying; `alg=none` acceptance; verification behind a debug flag.
2. **Algorithm confusion** — accepting both RS256 (asymmetric) and HS256 (symmetric) so the public key works as an HMAC secret; `alg` taken from the token header without an allow-list.
3. **Claim validation missing** — no `exp`/`nbf`/`iat` checks, `aud`/`iss` not validated, excessive lifetimes.
4. **Secrets** — weak/hardcoded signing secrets (cross-reference `secrets-and-credentials.md`), keys in client-reachable code.
5. **Sensitive data in payload** — tokens are usually only base64-encoded, not encrypted: PII/passwords/roles-that-shouldn't-be-client-visible in claims.
6. **Revocation gaps** — stateless tokens with no revocation strategy for logout/compromise; note as design observation.
7. **Key management** — kid/jku/x5u header injection paths (attacker-controlled key URLs), missing key pinning/rotation.

## OAuth / OIDC

1. **State parameter** missing/not validated → login CSRF.
2. **Nonce** missing in OIDC implicit/hybrid flows.
3. **Redirect URI validation** — open/wildcard/prefix matching of redirect URIs → code/token leakage.
4. **Token handling** — tokens in browser storage vs secure cookies, tokens leaked in URLs, missing `aud` checks at the resource server, access tokens accepted where id tokens are required.
5. **PKCE** missing for public clients.

These are configuration-heavy and version-dependent — when the implementation is unfamiliar, research the library's secure-usage docs (Phase 5).

## CSRF

State-changing requests forged cross-site (CWE-352, Top 25 #3):

1. **Cookie-based auth + state-changing GET** — GET must never mutate state.
2. **Missing CSRF tokens** on state-changing form/AJAX endpoints that rely on ambient authority (cookies, basic auth, client certs).
3. **Token weaknesses** — tokens not bound to session, not verified server-side, predictable, or "verified" by mere presence.
4. **SameSite reliance** — `SameSite=Lax/Strict` helps but is not universal (older clients, subdomains, GET top-level navigations); note as defense-in-depth, not sole control.
5. **CORS interplay** — permissive CORS (`Access-Control-Allow-Origin: *` with credentials, reflecting origin) re-enables cross-origin abuse; cross-reference `configuration-and-infrastructure.md`.

## False-Positive Guidance

Do NOT report when:

- A vetted framework/library handles auth end-to-end and is used per its secure defaults (verify the defaults for the VERSION — research).
- `SameSite` + framework CSRF middleware verifiably covers the state-changing endpoints (trace middleware registration).
- Token verification uses an algorithm allow-list and validates exp/aud/iss — check the actual call, not the wrapper's name.
- Password hashing uses a password KDF with a defensible work factor for the algorithm's current guidance.

## Mandatory Online Research Triggers

- Current recommended KDF and work factors (they change; verify at OWASP Password Storage Cheat Sheet / vendor guidance).
- The JWT/OAuth library's defaults for the detected version (algorithm acceptance, claim validation defaults).
- Known advisories for the detected auth/session/OAuth libraries (protocol trigger #4).
- Session/cookie default flags for the framework+version in use.

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| Weak password hashing | CWE-916/759/760 | A07:2025 |
| Plaintext/reversible credential storage | CWE-256/257/522 | A07:2025 / A04:2025 |
| User enumeration | CWE-203/204 | A07:2025 |
| Session fixation | CWE-384 | A07:2025 |
| Missing cookie flags | CWE-1004/614 | A02:2025 / A07:2025 |
| JWT verification/algorithm flaws | CWE-347/345 | A07:2025 / API2:2023 |
| CSRF | CWE-352 (Top 25 #3, 2025) | A01:2025-adjacent / ASVS V3 |
| Missing rate limiting on auth flows | CWE-307/770 | A07:2025 / API4:2023 |
| ASVS | V6 (Authentication), V7 (Session Management), V9 (Self-contained Tokens), V10 (OAuth and OIDC) | — |
