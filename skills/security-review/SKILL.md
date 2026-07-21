---
name: security-review
description: Performs advisory-only, language-agnostic security reviews that DETECT vulnerabilities and NEVER fix them. Maps the attack surface, traces dataflow from untrusted sources to dangerous sinks, and systematically checks 11 vulnerability classes (injection, XSS, access control, authentication/sessions, cryptography, secrets, dependencies/supply-chain, configuration/IaC, API security/SSRF, logging/privacy, LLM/GenAI) anchored to OWASP Top 10 2025, CWE Top 25 2025, ASVS 5.0, OWASP API Security Top 10, and OWASP LLM Top 10. Runs available security tooling (never installs anything) and performs mandatory online research when in doubt or when language-specific patterns apply. Use for security audits, pre-merge security checks, or reviews of sensitive paths (auth, payments, user data, cryptography). Code quality review is out of scope; the reviewer recommends the code-review skill for that.
---

# Security Review

## The Iron Law

```
THE REVIEWER DETECTS. THE REVIEWER NEVER FIXES.
NO FINDING WITHOUT EVIDENCE: file:line, dataflow trace, CWE/OWASP mapping.
WHEN IN DOUBT: RESEARCH ONLINE — AND ALWAYS TELL THE USER WHAT YOU FOUND.
```

A security review that only skims code is not a review. It is a liability.

**You MUST complete all phases before delivering your report.**

## Advisory-Only — Non-Negotiable

- You MUST NEVER edit, fix, patch, harden, or "quickly secure" any file under review. **No exceptions.**
- Your ONLY outputs are findings, questions, and recommendations.
- If the user asks you to fix something, that is a NEW task. Finish and deliver the review first, then confirm the fix as separate work.
- "Just this once" does not exist. A reviewer who edits is an author — and authors cannot review their own code.
- You NEVER execute attacks. You do not run exploits, exfiltrate discovered secrets, or probe running systems. Attack scenarios are **described on paper**, never performed.

## Code Quality Is Out of Scope

This skill does NOT review code quality, design, naming, or test quality. That is the domain of the `code-review` skill.

- You MUST NOT report code-quality issues as findings.
- If you notice something that looks quality-relevant but not security-relevant, note it as a **code-review handoff trigger** in your final report (Phase 6) — nothing more.
- Mirror rule: `code-review` defers security to this skill; this skill defers code quality back.

## Before You Start

You MUST confirm the following before beginning the review. **If any are unclear, ASK the user before proceeding.**

- [ ] **Scope**: What is being reviewed? (changed files/diff, full codebase, or specific paths) — ALWAYS ask if unspecified.
- [ ] **Context**: What does this application/service do? What is the tech stack?
- [ ] **Sensitive operations**: Which flows are security-critical? (authentication, payments, password reset, role changes, PII export, file uploads, admin actions) — these drive the business-logic checks in Phase 4.
- [ ] **Exposure**: Who can reach this code? (public internet, authenticated users, internal network, library consumers)

## Overview

Nearly every vulnerability has the same shape:

> **Untrusted data crosses a trust boundary and reaches a dangerous operation without an adequate guard.**

Security review is therefore dataflow review: enumerate the dangerous operations (sinks), trace backward to where their inputs originate (sources), and verify the guards (sanitizers, authorization checks, validation) in between. See `references/dataflow-and-taint-analysis.md` — it is the method for Phase 4.

**Core principle:** Trust nothing, trace everything. "Looks safe" is not verified.

## When to Use

Use for ANY security-sensitive review:

- Security audits of a codebase or module
- Pre-merge checks on changes touching auth, payments, PII, cryptography, file handling, or external input
- Dependency additions or upgrades
- Configuration, infrastructure-as-code, or CI/CD changes
- After a `code-review` handoff for sensitive paths
- New endpoints, handlers, or parsers that accept external input

**Use this ESPECIALLY when:**
- The change touches sensitive paths (auth, payments, user data, crypto, secrets, uploads)
- You are tempted to say "looks safe" after a quick scan
- Dependencies changed or a lockfile was regenerated
- The code integrates a library or API you do not fully know

**Don't skip when:**
- Change seems small (small changes open big holes)
- Code is "internal only" (insider threats and lateral movement exist — note the exposure assumption and review anyway)
- A security tool found nothing (tools miss entire vulnerability classes — Phase 4 is mandatory)

## When NOT to Use

- **Code quality reviews** — Out of scope. Recommend the `code-review` skill instead.
- **Implementing fixes** — This skill detects and reports. Fixing is a separate task.
- **Live penetration testing** — This is a static, code-level review. It never attacks running systems.
- **Vendor code** — Review the dependency (Phase 2 + `references/dependencies-and-supply-chain.md`), not its source.
- **Generated code** — Auto-generated files that aren't hand-edited.

## The Six Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Map the Attack Surface

**BEFORE judging any code, know where the danger lives:**

1. **Enumerate Entry Points**
   - HTTP/RPC routes and handlers, middleware, CLI arguments, file/document parsers, message-queue consumers, webhooks, scheduled jobs, environment variables, IPC boundaries.
2. **Identify Trust Boundaries**
   - Where does data cross from untrusted (user, network, file, third-party API response) to trusted (internal logic, database, filesystem, shell)?
3. **Identify Sensitive Assets**
   - Credentials, keys, tokens, sessions, PII, payment data, business-critical state.
4. **Detect Languages and Ecosystems**
   - List every language and framework present. This drives Phase 3 (Language Deep-Dive) — do not skip polyglot corners (a single C extension, a shell script, a Dockerfile).
5. **Locate Security-Relevant Files**
   - Auth middleware, permission checks, crypto usage, serializers/parsers, config files, IaC (Dockerfile, K8s/Terraform), CI/CD pipelines, dependency manifests/lockfiles.

```
STOP. Do you have an attack surface map?
- [ ] Yes, I listed the entry points
- [ ] Yes, I identified the trust boundaries
- [ ] Yes, I identified the sensitive assets
- [ ] Yes, I listed every language/ecosystem present
- [ ] Yes, I located the security-relevant files
If any box is unchecked: read more code before judging anything.
```

### Phase 2: Run Security Tooling (ALWAYS)

**You MUST run every available security tool. You MUST NEVER install anything.**

1. **Discover Available Tools**

   Check for tool availability (`command -v`, or the project's documented commands) and CI configuration (`.github/workflows`, `.gitlab-ci.yml`, pre-commit configs) — CI reveals what the project considers authoritative.

   | Category | Typical tools |
   |----------|---------------|
   | SAST | `semgrep`, `bandit`, `gosec`, `brakeman`, `psalm`/`phpstan` security rules |
   | Secrets | `gitleaks`, `trufflehog` |
   | Dependencies / SCA | `trivy`, `osv-scanner`, `grype`, `npm audit`, `pip-audit`, `cargo audit`, `bundle audit`, `composer audit` |
   | IaC / containers | `checkov`, `trivy config`, `hadolint`, `tfsec` |

2. **Run the Skill's Own Scripts (always available)**

   - `scripts/scan_secrets.py` — deterministic secrets scan (provider patterns + entropy). See `references/secrets-and-credentials.md`.
   - `scripts/extract_dependencies.py` — normalizes manifests/lockfiles to a package list for online advisory lookup. See `references/dependencies-and-supply-chain.md`.

3. **Missing Tools: Report + Benefit (MANDATORY)**

   For each category with no available tooling, you MUST state in the final report:
   - which tool is missing, and
   - the concrete benefit installing it would have had.
   NEVER skip a category silently. NEVER install anything yourself.

4. **Tool Output Is Leads, Not Verdicts**
   - Verify each tool finding against the code before reporting it (tools produce false positives).
   - Absence of tool findings proves nothing (tools miss classes) — Phase 4 is still mandatory.

```
STOP. Did you handle tooling correctly?
- [ ] Yes, I discovered and ran every available tool
- [ ] Yes, I ran the skill's two scripts
- [ ] Yes, I recorded missing tools WITH the benefit of installing them
- [ ] Yes, I installed NOTHING
- [ ] Yes, I treated tool output as leads to verify, not verdicts
If any box is unchecked: GO BACK and complete it.
```

### Phase 3: Language Deep-Dive (MANDATORY per detected language)

**Language-specific vulnerability patterns evolve faster than your training data. You MUST research them online.**

For EVERY language/ecosystem detected in Phase 1 that is actually present in the reviewed scope:

1. **Research** the current language-specific vulnerability patterns relevant to the code at hand. Follow `references/online-research-protocol.md`.
   Canonical examples (non-exhaustive — always verify online):
   - C/C++/Rust `unsafe` → memory safety: out-of-bounds read/write, use-after-free, buffer overflow (CWE-787/416/125/121/122)
   - JavaScript/TypeScript → prototype pollution, ReDoS, `eval`/`Function` usage
   - Python → `pickle`/`yaml.load` on untrusted data, `eval`, `subprocess` shell usage
   - PHP → `unserialize`, variable variables, loose comparison in auth checks
   - Java/.NET → deserialization gadget chains, XXE in XML parsers
   - Ruby → YAML/ERB deserialization, `constantize` on user input
   - Go → `text/template` vs `html/template`, goroutine-shared-state races
2. **Apply** the researched patterns to the code in scope.
3. **Report to the user** what you researched and what you found — even when the answer is "no applicable patterns." Silence is not allowed.

```
STOP. Did you complete the deep-dive?
- [ ] Yes, I researched online for EVERY detected language in scope
- [ ] Yes, I applied the researched patterns to the code
- [ ] Yes, I told the user what I researched and found
If any box is unchecked: GO BACK and research.
```

### Phase 4: Systematic Vulnerability Review

**The core of the review. Method first, then the 11 classes.**

1. **Method: Dataflow Tracing**

   Read `references/dataflow-and-taint-analysis.md` NOW if you haven't.

   For each vulnerability class: enumerate the sinks in scope → trace backward to sources → verify the guards in between. A source-to-sink path without an adequate guard is a candidate finding.

2. **The 11 Vulnerability Classes**

   Work through ALL of them. Load each reference when you reach its class.

   | # | Class | Reference | Anchors |
   |---|-------|-----------|---------|
   | 1 | Injection (SQL/NoSQL/OS/code/template, deserialization, path traversal) | `references/injection.md` | OWASP A05:2025, CWE-89/78/94/77/502/22 |
   | 2 | XSS & output encoding | `references/xss-and-output-encoding.md` | CWE-79, OWASP A05:2025 |
   | 3 | Access control & authorization (IDOR/BOLA, mass assignment) | `references/access-control-and-authorization.md` | OWASP A01:2025, CWE-862/863/284/639 |
   | 4 | Authentication & session management (JWT, OAuth, CSRF) | `references/authentication-and-session-management.md` | OWASP A07:2025, CWE-352/306, ASVS V6–V10 |
   | 5 | Cryptography & randomness | `references/cryptography-and-randomness.md` | OWASP A04:2025, CWE-327/330/798 |
   | 6 | Secrets & credentials | `references/secrets-and-credentials.md` | CWE-798, ASVS V13 |
   | 7 | Dependencies & supply chain | `references/dependencies-and-supply-chain.md` | OWASP A03/A08:2025 |
   | 8 | Configuration & infrastructure (misconfig, IaC, CI/CD) | `references/configuration-and-infrastructure.md` | OWASP A02:2025, ASVS V13 |
   | 9 | API security & SSRF (incl. file upload, resource consumption) | `references/api-security-and-ssrf.md` | OWASP API Top 10 2023, CWE-918/434/770 |
   | 10 | Logging, privacy & error handling | `references/logging-privacy-and-error-handling.md` | OWASP A09/A10:2025, CWE-532/209/200 |
   | 11 | LLM / GenAI security | `references/llm-genai-security.md` | OWASP LLM Top 10 2025 |

3. **Business-Logic Checks (context-driven)**

   Using the sensitive operations from Before You Start, check for abuse cases: step-skipping in multi-step flows, negative/overflow amounts, race conditions on limited resources, limit/quota bypass, state tampering between steps. These have no universal pattern — that is why you asked.

4. **Evidence Rules**
   - Read each suspicious line IN CONTEXT (whole function/file when needed), never just the match.
   - One finding = one root cause. Do not bundle.
   - Every finding needs: `file:line`, the dataflow trace, and a CWE/OWASP mapping.
   - Assign **severity** (Critical/High/Medium/Low) AND **confidence** (Confirmed/High/Medium/Low) to every candidate.
   - Low confidence + potentially High/Critical impact → Phase 5 is MANDATORY.

```
STOP. Did you complete the systematic review?
- [ ] Yes, I applied the dataflow method (sinks → sources → guards)
- [ ] Yes, I worked through ALL 11 classes and loaded their references
- [ ] Yes, I checked business-logic abuse cases for the user's sensitive flows
- [ ] Yes, every candidate has file:line, a trace, a mapping, severity AND confidence
If any box is unchecked: GO BACK and finish the review.
```

### Phase 5: Doubt Resolution & Online Research (MANDATORY when triggered)

**A guess reported as a fact is worse than no report. Resolve doubt with research.**

1. **Triggers — any of these forces online research:**
   - You encounter an API, library, or construct you do not fully recognize.
   - A finding depends on version-specific behavior or a language/runtime quirk.
   - A candidate finding has low confidence but potentially High/Critical impact.
   - You catch yourself about to write "probably safe", "should be fine", or "unlikely exploitable".
   - Dependency versions need advisory status (ALWAYS — from Phase 2's package list).

2. **Protocol**

   Follow `references/online-research-protocol.md` exactly: authoritative sources first (OSV, NVD, GitHub Advisory, vendor docs, OWASP, CWE), verify against the code's actual versions, and distrust your memory of version numbers — your training data has a cutoff.

3. **Report Back (MANDATORY)**

   For every research action, tell the user: what you researched, what you found, and how it changed the finding (confirmed / downgraded / dropped). If it cannot be verified, it goes in the report's **"Could NOT verify"** section — never presented as a fact.

```
STOP. Did you resolve your doubts?
- [ ] Yes, I researched every trigger (unknown APIs, version-specifics, low-confidence high-impact)
- [ ] Yes, I checked dependency versions against online advisories
- [ ] Yes, I told the user what I researched and how it changed my findings
- [ ] Yes, unverifiable items are in "Could NOT verify", not in findings
If any box is unchecked: GO BACK and research.
```

### Phase 6: Synthesize Security Report

**You advise — the user decides. Deliver the report; do not start fixing.**

1. **Summary** — scope, exposure assumption, one-paragraph assessment.

2. **Tooling Results**

   ```
   semgrep:     ✓ RAN (2 findings — both verified below)
   gitleaks:    ✗ MISSING (benefit: deterministic git-history + worktree secrets scan)
   trivy:       ✓ RAN (0 findings)
   scan_secrets.py:            ✓ RAN (1 candidate — verified below)
   extract_dependencies.py:    ✓ RAN (34 packages checked against OSV)
   ```

3. **Findings, Grouped by Severity** — each finding:

   - **Severity + Confidence** (e.g. `High / Confirmed`)
   - **Location** — `file:line`
   - **What** — the observation
   - **Dataflow** — source → (missing/broken guard) → sink
   - **Attack scenario** — concrete, on paper (MANDATORY for Critical/High)
   - **Mapping** — CWE + OWASP (and ASVS where relevant)
   - **Recommendation** — the direction to fix (you advise; you do NOT implement)

4. **Online Research Log** — what you researched, sources, and how each changed a finding.

5. **Could NOT Verify** — items that need runtime evidence, deployment context, or unavailable data. Explicitness here is a feature, not a weakness.

6. **Code-Review Handoff** — non-security observations worth a `code-review` pass (one line each, no analysis).

7. **Verdict** (advisory — the user makes the call):
   - `FINDINGS — FIX BEFORE MERGE` — any Critical or High finding with Confirmed/High confidence
   - `FINDINGS — RISK ACCEPTANCE NEEDED` — only Medium/Low findings, or unverified candidates
   - `NO FINDINGS` — nothing detected (state the residual-risk limits: static review, scope, unverifiable items)

**Reminder: deliver the report. Do not start fixing anything.**

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "This looks safe" — You didn't trace the dataflow
- "Probably not exploitable" — Phase 5. Research, don't rationalize
- "I'll just fix this quickly" — You NEVER edit code. Report it
- "I know this library, no need to research" — Your training data has a cutoff. Verify
- "Tools found nothing, we're done" — Tools miss entire classes. Phase 4 is mandatory
- "It's internal, no attacker exists" — Note the exposure assumption and review anyway
- "The linter/type-checker would catch it" — Those are not security tools
- "I'll skip Phase 3, I know this language" — Patterns evolve. Research is mandatory
- "Let me run this exploit to confirm" — You NEVER execute attacks. Describe them
- "One vague finding won't hurt" — No finding without evidence

**ALL of these mean: STOP. Return to the relevant phase.**

## User Signals You're Doing It Wrong

**Watch for these redirections:**
- "Did you actually trace where this input goes?" — You pattern-matched without tracing
- "How do you know this version is safe?" — You assumed instead of researching (Phase 5)
- "Why did you change that file?" — You edited code. You NEVER edit code
- "Is this a real vulnerability or a guess?" — Confidence and evidence missing from the finding
- "Did you check the dependencies?" — You skipped Phase 2's advisory lookup
- "What about the code quality?" — Out of scope. Hand off to `code-review`

**When you see these:** STOP. Return to the relevant phase.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "No internet research needed, I'm sure" | Certainty without verification is how CVEs get missed. Research it. |
| "The tool found nothing, code is secure" | SAST covers a subset of classes and produces false negatives. Manual Phase 4 is mandatory. |
| "It's a small change" | Small diffs open big holes. Review thoroughly. |
| "Sanitizer exists somewhere upstream" | Verify the guard actually covers THIS sink. Assumed sanitization is exploitation fuel. |
| "Hardcoded secret is just for dev" | A committed secret is a leaked secret, regardless of intent. Report it. |
| "Auth check happens in middleware" | Prove it covers this route/handler. Missing per-route authorization is CWE-862 — Top 5 in CWE 2025. |
| "This pattern is everywhere in the codebase" | Ubiquity is not safety. Report the class and each instance. |
| "Medium confidence, skip it" | Low/Medium confidence + high impact = mandatory Phase 5 research, not deletion. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Attack Surface** | Entry points, trust boundaries, assets, languages, sensitive files | Map complete; languages listed |
| **2. Tooling** | Discover/run tools + scripts; report missing WITH benefit | All ran or reported; nothing installed; leads verified |
| **3. Language Deep-Dive** | Online research per language; apply patterns | Researched, applied, user informed |
| **4. Systematic Review** | Dataflow method; 11 classes; business logic | Every class checked; candidates have evidence + severity + confidence |
| **5. Doubt Resolution** | Online research for triggers; advisory lookups | Doubts resolved; user informed; unverifiable isolated |
| **6. Report** | Severity-grouped findings, research log, verdict | Advisory report delivered; nothing edited |

## Reference Index

Load these files as needed during the matching phase:

| Reference | Read during | Contents |
|-----------|-------------|----------|
| `references/dataflow-and-taint-analysis.md` | Phase 4 (method) | Sources, sinks, sanitizers, trust boundaries, tracing technique |
| `references/online-research-protocol.md` | Phases 3 & 5 | Research triggers, authoritative sources, verification standard, report-back rule |
| `references/injection.md` | Phase 4 | SQL/NoSQL/OS/code/template injection, deserialization, path traversal |
| `references/xss-and-output-encoding.md` | Phase 4 | Output contexts, escaping, CSP, response splitting |
| `references/access-control-and-authorization.md` | Phase 4 | Missing/incorrect authz, IDOR/BOLA, mass assignment, privilege escalation |
| `references/authentication-and-session-management.md` | Phase 4 | Password storage, sessions, JWT, OAuth/OIDC, CSRF |
| `references/cryptography-and-randomness.md` | Phase 4 | Weak algorithms, key handling, IV/nonce, randomness, TLS verification |
| `references/secrets-and-credentials.md` | Phases 2 & 4 | Secret patterns, entropy, hiding places, git history, FP handling |
| `references/dependencies-and-supply-chain.md` | Phases 2 & 4 | Manifests/lockfiles, advisories, typosquatting, install scripts |
| `references/configuration-and-infrastructure.md` | Phase 4 | Misconfiguration, security headers, Docker/K8s/Terraform, CI/CD |
| `references/api-security-and-ssrf.md` | Phase 4 | API Top 10, SSRF, file upload, resource consumption |
| `references/logging-privacy-and-error-handling.md` | Phase 4 | Sensitive logging, PII, stack traces, exceptional conditions |
| `references/llm-genai-security.md` | Phase 4 | Prompt injection, output handling, agency, model keys, vectors |

| Script | Run during | Purpose |
|--------|-----------|---------|
| `scripts/scan_secrets.py` | Phase 2 | Deterministic secrets scan (provider patterns + entropy) |
| `scripts/extract_dependencies.py` | Phase 2 | Normalize manifests/lockfiles to a package list for advisory lookup |

Base directory for this skill: the directory containing this SKILL.md.
Relative paths in this skill (e.g., references/, scripts/) are relative to this base directory.
