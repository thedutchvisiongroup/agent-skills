# Configuration and Infrastructure

Read this during Phase 4, class 8. Security Misconfiguration is A02 on the OWASP Top 10 (2025). Anchor: ASVS V13 (Configuration). Covers application config, web/security headers, CORS, infrastructure-as-code (Docker, Kubernetes, Terraform), and CI/CD pipelines.

## Contents

- What It Is
- Application Configuration
- CORS
- Security Headers and Transport
- Docker / Containers
- Kubernetes / Orchestration
- Terraform / Cloud IaC
- CI/CD Pipelines
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

Misconfiguration is insecure-by-default or insecure-by-omission: the code may be flawless while the deployment envelope is wide open. Review config FILES and infrastructure definitions with the same source→sink discipline: the "sink" is the deployed attack surface.

## Application Configuration

Detection patterns:

1. **Debug/development modes enabled** — debug flags, verbose error pages, stack traces to clients, hot-reload/dev servers, debug endpoints (cross-reference `logging-privacy-and-error-handling.md`).
2. **Default credentials/accounts** — seeded admin/admin-style accounts, unchanged framework defaults, example configs deployed verbatim.
3. **Permissive environment handling** — prod falling back to dev defaults when env vars are missing; secrets defaulted in code (`os.getenv("KEY", "hardcoded-default")`).
4. **Directory listing / exposed static paths** — web roots exposing `.git`, backups, `.env`, uploads, internal docs.
5. **Overly broad permissions** — world-readable/writable paths, permissive umask, config files readable by app users.
6. **Feature flags** — security controls behind flags defaulting to off/disabled in prod config.

## CORS

1. `Access-Control-Allow-Origin: *` combined with credentials.
2. **Reflecting arbitrary `Origin`** into `Access-Control-Allow-Origin` (echo without allow-list) — functionally equivalent to `*` with credentials.
3. Allow-lists with weak matching (substring/regex errors: `evil-trusted.com`, `trusted.com.evil.io`).
4. `Access-Control-Allow-Origin: null` patterns (sandbox/null-origin abuse).
5. Overly broad allowed methods/headers + long preflight caching.

## Security Headers and Transport

Check responses/middleware config for (missing = hardening finding, usually Low/Medium):

- `Content-Security-Policy` (see `xss-and-output-encoding.md` for what makes a CSP weak)
- `Strict-Transport-Security` (on HTTPS sites; includeSubDomains for full coverage)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options` / CSP `frame-ancestors` (clickjacking)
- `Referrer-Policy`, `Permissions-Policy`
- Cookies: `Secure`, `HttpOnly`, `SameSite` (cross-reference authentication reference)
- TLS config: minimum protocol 1.2+, no weak cipher suites, HSTS where applicable

## Docker / Containers

1. **Running as root** — no `USER` directive, or `USER root`; `--privileged`, `privileged: true` in compose.
2. **Unpinned images** — `FROM image:latest` or no tag; pin by digest. Note for Phase 5: image CVE lookup (trivy/OSV) is online work.
3. **Secrets in image** — `ENV`/`ARG` with secrets, copied `.env`/keys, secrets in build history (multi-stage fixes this — check what lands in the FINAL stage).
4. **`ADD` from remote URLs** (unverifiable fetch), `ADD` of archives (auto-extract surprises) — prefer pinned `COPY` + verified fetch.
5. **Dangerous mounts/sockets** — docker socket mounted, host paths mounted rw, `--network host` without need.
6. **Attack surface** — unnecessary packages/shells/tools in the final image, exposed ports beyond need, healthcheck endpoints leaking info.

## Kubernetes / Orchestration

1. `privileged: true`, `allowPrivilegeEscalation: true` (or unset), `runAsUser: 0` / missing `runAsNonRoot`.
2. `hostNetwork`, `hostPID`, `hostIPC`, `hostPath` mounts (especially of `/`, `/var/run/docker.sock`).
3. Missing `readOnlyRootFilesystem`, missing resource `limits` (resource consumption, CWE-770).
4. Capabilities: `SYS_ADMIN`, `NET_ADMIN`, `ALL` added; missing `drop: ["ALL"]`.
5. Overly broad RBAC — `cluster-admin` bindings, wildcard verbs/resources, automounted service-account tokens where unneeded.
6. Secrets as env vars/plaintext manifests instead of a secret store; missing NetworkPolicies.

## Terraform / Cloud IaC

1. **Public exposure** — security groups/firewalls open to `0.0.0.0/0` on sensitive ports (SSH, RDP, databases, internal services); public object-storage buckets; public database snapshots.
2. **Encryption off** — unencrypted storage volumes/databases/buckets; missing TLS-only policies.
3. **IAM** — wildcard actions/resources (`*:*`), admin policies attached broadly, access keys instead of roles.
4. **Logging off** — disabled audit/access logging (cross-reference logging reference).
5. **State files** — terraform state committed to the repo (contains secrets).

## CI/CD Pipelines

1. **Script injection** — untrusted context (PR titles, branch names, commit messages, issue bodies) interpolated into `run:` steps (workflow-pwn class).
2. **Untrusted-code + secrets** — workflows running PR/fork code while exposing secrets or write tokens (`pull_request_target` misuse is the canonical example).
3. **Unpinned actions/images** — third-party actions by mutable tag instead of commit SHA.
4. **Over-privileged tokens** — default `GITHUB_TOKEN`-equivalents with write-all; long-lived deploy keys in repo secrets.
5. **Artifacts/deploy integrity** — unsigned artifacts, deploy steps without environment protection/approvals.
6. **Secrets echoed** — printing env vars, debug dumps in logs (masking is not guaranteed — note it).

## False-Positive Guidance

Do NOT report when:

- The insecure value is provably confined to local-dev config files that are not deployed (verify separation; committed prod-aimed config is never "dev-only").
- The framework version's defaults are secure and nothing overrides them (VERIFY defaults online — version-specific).
- A compensating control exists (WAF, gateway) AND you can verify its coverage from available config; otherwise → "Could NOT verify", not dismissal.
- `0.0.0.0` binding for a container service is normal for the platform AND exposure is handled by documented network policy you can see.

## Mandatory Online Research Triggers

- Framework default configs (debug, headers, CORS, session flags) for the detected version.
- Base-image CVE status for containers (trivy/OSV online lookup).
- Cloud service default posture (bucket public-by-default?, logging on?) — changes over time.
- CI/CD platform features: token default permissions, `pull_request_target` semantics — verify current docs.

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| Debug mode / verbose errors in prod | CWE-489/215 | A02:2025 |
| Default credentials | CWE-1392/798 | A02:2025 / A07:2025 |
| Permissive CORS | CWE-942/346 | A02:2025 / API8:2023 |
| Missing security headers | CWE-693/1021 | A02:2025 |
| Root/privileged containers, host mounts | CWE-732/250 | A02:2025 |
| Public cloud exposure, open SGs | CWE-284/668 | A02:2025 / A01:2025 |
| CI script injection, unpinned actions | CWE-94/829/494 | A08:2025 / A03:2025 |
| Missing resource limits | CWE-770 (Top 25 #25, 2025) | API4:2023 |
| ASVS | V13 (Configuration) | — |
