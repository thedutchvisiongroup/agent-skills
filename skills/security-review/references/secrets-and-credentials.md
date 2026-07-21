# Secrets and Credentials

Read this during Phases 2 and 4, class 6. Hard-coded credentials are CWE-798; secret leakage underpins supply-chain and cloud breaches. Anchor: ASVS V13 (Configuration — secret management). This class is unusually deterministic: run `scripts/scan_secrets.py` (Phase 2) and verify manually — do not eyeball for secrets, agents are bad at judging entropy by sight.

## Contents

- What It Is
- Where Secrets Hide
- Pattern Categories
- Entropy and Confidence
- Git History
- False-Positive Guidance
- Handling Discovered Secrets (STRICT)
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

A secret in code is any committed artifact that grants access: API keys, tokens, passwords, private keys, connection strings with credentials, signing secrets, encryption keys. **A committed secret is a leaked secret** — regardless of intent ("just for dev"), regardless of whether the repo is "private".

## Where Secrets Hide

Check ALL of these, not just source files:

| Location | Notes |
|----------|-------|
| Source code | literals assigned to credential-looking names; credentials embedded in URLs (`user:pass@host` form) |
| Config files | `.env`, `.env.*`, `*.ini/cfg/conf/yaml/json/toml/properties`, settings modules |
| IaC | Dockerfiles (`ENV`, `ARG`), compose files, Terraform variables/`*.tfvars`, K8s manifests (secrets in plaintext, not just base64), CI/CD variables hardcoded in pipeline files |
| Tests & fixtures | seeded credentials, recorded API responses/cassettes, mock tokens that are real |
| Docs & comments | README examples with live keys, comment blocks, Postman collections |
| Client-side bundles | mobile/desktop/web artifacts containing server keys |
| Git history | deleted secrets are still secrets — see below |
| Certificates/keys | `*.pem`, `*.key`, `*.p12`, `*.jks`, private-key blocks pasted into strings |

## Pattern Categories

`scan_secrets.py` implements three deterministic detectors; know what they mean:

1. **Provider formats** — recognizable key shapes (cloud access keys, payment provider keys, SCM tokens, chat/ops tokens, JWT-shaped strings, etc.). High confidence by format.
2. **Private key material** — `-----BEGIN ... PRIVATE KEY-----` blocks anywhere. Critical on sight.
3. **Keyword + high-entropy assignment** — names like `password`, `secret`, `token`, `api_key`, `client_secret`, `passwd`, `pwd`, `credential` assigned a long high-entropy literal. Medium confidence: needs your verification.

## Entropy and Confidence

- Provider-format match + plausible length = **High/Confirmed** candidate.
- Keyword + entropy = verify manually: is it a real credential, a hash, an id, a test vector, a UUID?
- **Judge by function, not by appearance**: trace whether the value is USED as a credential (sent as auth, used to sign/encrypt, opens a connection). Usage as a credential confirms; unused-looking still gets reported (Medium) because committed secrets are liabilities even when dormant.

## Git History

Secrets removed from the working tree persist in history.

- If `gitleaks`/`trufflehog` is available, run it (it covers history).
- If not: check suspicious deletions with `git log -p`/`git log -S <pattern>` for known secret shapes, and ALWAYS include in the report: "git history was/was not scanned — benefit of gitleaks: deterministic history scan" (Phase 2 missing-tool rule).
- Any secret found in history is **Confirmed** — rotation advice is part of the finding.

## False-Positive Guidance

Do NOT report as High when:

- The value is a documented public identifier (public API keys designed to be embedded, publishable keys) — verify the provider's model online if unsure (Phase 5).
- The value is an obvious placeholder (`changeme`, `your-key-here`, `xxx`, example.com-style) — but flag committed `.env` files anyway as a process finding (they attract real secrets later).
- The value is a hash/checksum/id used as data, verified by tracing its use.
- Test fixtures use syntactically-valid-but-revoked/sample credentials — still report as Low/Medium (they teach bad patterns and sometimes are real).

## Handling Discovered Secrets (STRICT)

- **Never print the full secret** in chat or in the report. Redact: show at most the first 4 and last 2 characters (e.g., `AKIA...19`), or state "value redacted".
- **Never use the secret** to "verify it works" — that is executing an attack. Validation happens via provider tooling owned by the user, not by you.
- Report: location (`file:line`), secret type, confidence, and the required actions (rotate/revoke immediately, remove from history, move to a secret manager). Rotation urgency is HIGHER than code cleanliness — say so.

## Mandatory Online Research Triggers

- Unfamiliar token/key format: identify the provider/type before classifying (protocol trigger #1).
- Whether a key type is designed to be public vs secret (publishable vs secret keys differ per provider).
- Git-history scanning tooling availability/approach for the detected VCS setup.

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| Hard-coded credentials | CWE-798 | A07:2025 / ASVS V13 |
| Private key in repo | CWE-321/798 | A04:2025 / ASVS V13 |
| Sensitive data in config/IaC | CWE-798/256 | A02:2025 Security Misconfiguration |
| Credentials in URL/logs/comments | CWE-532/598 | A09:2025 |
| Secret in git history | CWE-798 + rotation requirement | A07:2025 |
| ASVS | V13 (Configuration — secret management) | — |
