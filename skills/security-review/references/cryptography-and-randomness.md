# Cryptography and Randomness

Read this during Phase 4, class 5. Cryptographic Failures are A04 on the OWASP Top 10 (2025). Anchor: ASVS V11 (Cryptography). Crypto review from code alone has limits — algorithm soundness and library defaults are version-dependent, so this class triggers Phase 5 research often. That is expected, not a failure.

## Contents

- What It Is
- Weak Algorithms and Modes
- Key Management
- IV / Nonce / Salt Handling
- Randomness
- Password Hashing (pointer)
- TLS / Transport Verification
- Home-Grown Crypto
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

Cryptographic failures occur when code uses weak primitives, misuses sound primitives, or manages keys badly — rendering protection ineffective while LOOKING protected. The danger is silent: broken crypto usually "works" functionally.

**Universal detection shape:**

```
sensitive data → cryptographic operation (sink)
      with weak algorithm/mode, bad key material, bad IV/nonce, or verification disabled
```

## Weak Algorithms and Modes

Detection patterns (names are recognizable across languages):

1. **Broken/legacy ciphers & hashes**: DES, 3DES, RC4, Blowfish, CAST, MD5, SHA-1 (for security purposes), RC2, IDEA. Flag on sight for security contexts.
2. **ECB mode** for block ciphers — leaks structure; flag on sight.
3. **Static/default parameters**: hardcoded IV, fixed salt, constant nonce.
4. **RSA misuse**: PKCS#1 v1.5 padding for encryption (Bleichenbacher family), textbook RSA, small keys (<2048).
5. **Encrypt-then-MAC violations**: unauthenticated encryption (no AEAD, no MAC), MAC-then-encrypt constructions, home-built authenticated modes. AEAD (e.g., GCM/ChaCha20-Poly1305-style) is the expected modern default — verify what the library call actually selects.
6. **Deprecated protocol versions**: SSLv3, TLS 1.0/1.1 negotiated/allowed; weak cipher suites configured explicitly.

**Note:** whether a specific library call maps to a weak primitive is often version-dependent — RESEARCH the library+version rather than assuming (Phase 5, protocol trigger #7).

## Key Management

1. **Hardcoded keys/seeds** in source, config, fixtures, or tests that ship (cross-reference `secrets-and-credentials.md`; CWE-798).
2. **Keys derived from passwords without a KDF**, or with a fast hash; low-entropy key material (short passphrases used directly as keys).
3. **Keys in the wrong place**: embedded in client-side code, in version control, in container images/layers, in logs/error messages.
4. **No rotation story** and no separation (same key for dev/staging/prod; same key for encryption and signing).
5. **Key length / parameter weakness** for the algorithm (research current minimums).

## IV / Nonce / Salt Handling

1. **Nonce reuse** in nonce-misuse-sensitive modes (GCM/CTR/stream ciphers): fixed IV, IV derived from a counter that can reset, random IVs too small for the volume. Catastrophic in GCM-family modes.
2. **IV required but not explicitly set** — relies on library default, which may be static or insecure across versions (research).
3. **Salt reuse** across users/purposes; missing salt for hashing; global pepper committed to the repo.
4. **Confusion of primitives**: IV used as key, salt as IV, etc.

## Randomness

1. **Non-cryptographic PRNG for security purposes**: predictable generators (time-seeded, default-seeded, math/random-style utilities) used for tokens, session ids, reset codes, OTPs, keys, nonces, UUID v4 substitutes.
   - The tell: security-relevant value ← randomness API that is NOT the platform's CSPRNG.
2. **Insufficient entropy space**: short numeric codes for high-value actions (4-digit reset codes without attempt limits), truncated tokens.
3. **Seeding from predictable inputs**: timestamps, process ids, usernames.

## Password Hashing (pointer)

Password storage belongs to `authentication-and-session-management.md` (KDF selection, work factors). Apply it here only when general-purpose hashing code is reused for credentials.

## TLS / Transport Verification

1. **Certificate verification disabled**: "verify=false"-style flags, trust-all managers, permissive hostname verifiers, `rejectUnauthorized: 0`-style settings. **Flag on sight — High severity.** Often hidden behind "temporary" comments; still a finding.
2. **Insecure endpoints hardcoded**: `http://` URLs for sensitive traffic, downgrade-tolerant configs, mixed content.
3. **Cleartext protocols** for sensitive data (ftp/telnet/ldap without TLS, internal mTLS absent where the architecture demands it — note as observation if undeterminable).
4. **Certificate pinning** claimed but bypassable, or disabled in "debug".

## Home-Grown Crypto

Custom encryption/hashing/obfuscation schemes, hand-rolled protocols, "proprietary encoding" presented as security, XOR-with-fixed-key obfuscation of secrets. **Report the class**: custom crypto is a design finding (A06/A04) even when you cannot break it on sight. Research breaks only if needed for severity grading — do not attempt cryptanalysis.

## False-Positive Guidance

Do NOT report when:

- A vetted high-level library (key-management or "safe defaults" crypto API) is used per current guidance — verify the version's defaults online.
- MD5/SHA-1 used for NON-security purposes (cache keys, checksums for integrity against non-adversarial corruption) — note context; do not flag as crypto failure (but flag if the same digest gates security decisions).
- Randomness is for non-security use (UI shuffle, sampling) — no finding.
- TLS termination is verifiably handled at a proxy AND the internal transport is documented as trusted — record the assumption in "Could NOT verify" if unproven.

## Mandatory Online Research Triggers

- The crypto library's default algorithm/mode/padding for the detected version (defaults shift).
- Current minimum key lengths, work factors, and recommended primitives (NIST/OWASP guidance).
- Known vulnerabilities of the detected crypto library version (protocol trigger #4).
- Any primitive, mode, or API you do not fully recognize (protocol trigger #1).

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| Weak/broken algorithm | CWE-327/328 | A04:2025 |
| ECB mode / missing authentication | CWE-353/327 | A04:2025 |
| Hardcoded cryptographic key | CWE-321/798 | A04:2025 / ASVS V13 |
| Insecure randomness | CWE-330/338 | A04:2025 |
| Nonce/IV reuse or missing | CWE-323/329 | A04:2025 |
| TLS verification disabled | CWE-295 | A02:2025 / A04:2025 |
| Cleartext transmission of sensitive data | CWE-319 | A04:2025 / ASVS V12 |
| Home-grown crypto | CWE-327 (design) | A04/A06:2025 |
| ASVS | V11 (Cryptography), V12 (Secure Communication) | — |
