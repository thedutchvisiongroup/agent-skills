# Online Research Protocol

Read this in Phases 3 and 5. This protocol governs WHEN you must research online, HOW to do it credibly, and HOW to report it back. It exists because your training data has a cutoff and vulnerability knowledge decays: versions, advisories, deprecated APIs, and language-specific patterns change after it.

## Contents

- The Rule
- Mandatory Research Triggers
- Source Hierarchy
- How to Research (per situation)
- Verification Standard
- The Report-Back Rule (MANDATORY)
- What Research Can NOT Establish
- Anti-Patterns

## The Rule

```
WHEN IN DOUBT: RESEARCH ONLINE.
A guess reported as a fact is worse than no report.
You MUST ALWAYS tell the user what you researched and what you found.
```

Doubt is not weakness. Reporting doubt-as-fact is.

## Mandatory Research Triggers

Any ONE of these forces online research — no exceptions:

| # | Trigger | Why |
|---|---------|-----|
| 1 | You encounter an API, library, framework feature, or language construct you do not fully recognize | You cannot judge what you cannot name |
| 2 | A finding depends on version-specific behavior (default configs, deprecated algorithms, parser quirks) | Defaults and deprecations change per release |
| 3 | A candidate finding has Low/Medium confidence AND potentially High/Critical impact | Cheap research beats a missed critical |
| 4 | Dependency versions need advisory status (ALWAYS — every review) | Known-CVE status exists only online (OSV/NVD/GitHub Advisory) |
| 5 | Phase 3 Language Deep-Dive: language-specific vulnerability patterns for each detected language | Patterns evolve faster than training data |
| 6 | You are about to write "probably safe", "should be fine", "unlikely exploitable", or "by default this is secure" | Those phrases mark unverified assumptions |
| 7 | The code handles cryptography and you need to confirm an algorithm/mode/library is still considered sound | Cryptographic guidance changes (e.g., new attacks, deprecations) |

## Source Hierarchy

Prefer sources in this order. Cross-check at least two when the finding is Critical/High.

1. **Primary authoritative** — vendor/maintainer security advisories, official documentation for the EXACT version in the code, the project's own changelog/security policy
2. **Canonical databases** — OSV (osv.dev), NVD (nvd.nist.gov), GitHub Advisory Database, CISA KEV (actively exploited), MITRE CWE for weakness definitions
3. **Standards bodies** — OWASP (Top 10, ASVS, Cheat Sheet Series), IETF RFCs, NIST publications
4. **Reputable secondary** — established security researchers' write-ups, well-known security blogs — use to understand exploit mechanics, not as sole evidence

**Distrust:** your own memory of version numbers and CVE IDs (hallucination risk), SEO content farms, undated articles, and anything you cannot tie back to a version.

## How to Research (per situation)

| Situation | Query strategy |
|-----------|----------------|
| Unknown API/construct | `"<library> <function/construct>" security` + official docs for the used version; look for "deprecated", "insecure", "unsafe" notes |
| Version-specific default | `"<framework> <version> default <setting>"` → official changelog/docs of THAT version |
| Dependency advisory | Query OSV by `ecosystem + package + version` (the `extract_dependencies.py` output is built for this); cross-check NVD/GitHub Advisory for Critical/High |
| Language pattern (Phase 3) | `"<language> common vulnerabilities <current year>"`, `"<language> <construct> vulnerability"`, OWASP Cheat Sheets for the language/feature |
| Exploitability judgment | `"<weakness class> exploit <technology>"` — understand mechanics to grade severity, never to execute |
| Crypto soundness | `"<algorithm/mode> deprecated insecure"`, NIST/OWASP cryptographic storage guidance, library-specific known-issues |

**Version discipline:** always anchor to the version actually in the code/lockfile. "Vulnerable in < 2.3.1" means nothing until you know the project runs 2.3.0.

## Verification Standard

A research outcome may upgrade a candidate to a finding only when:

- [ ] The source is authoritative for the claim (vendor/advisory database/standard)
- [ ] The claim applies to the version/configuration actually present in the reviewed code
- [ ] You can state the mechanism in one sentence (what makes it exploitable)

Otherwise the item goes to **"Could NOT verify"** with what you tried — not into findings.

## The Report-Back Rule (MANDATORY)

For EVERY research action, report to the user — inline during work and as the "Online Research Log" in the final report:

```
Researched: <question>
Sources:    <what you consulted>
Outcome:    <what you found>
Effect:     <confirmed / upgraded / downgraded / dropped — and why>
```

- You MUST also report research that found NOTHING applicable ("researched X — no applicable pattern found"). Silence is not allowed: the user cannot distinguish "checked and clean" from "never checked".
- You MUST report it when research reveals something NEW the user didn't ask about (e.g., the discovered API has a known CVE unrelated to your original question). Newly found risk is always reported.

## What Research Can NOT Establish

Research cannot prove runtime exploitability (WAFs, deployment config, network position), business impact, or the absence of unknown (0-day) vulnerabilities. Say so in "Could NOT verify" — explicit limits make the rest of the report credible.

## Anti-Patterns

| Anti-pattern | Correct behavior |
|--------------|------------------|
| Trusting your memory of a CVE/version | Look it up. Every time. |
| Researching only to confirm your suspicion (confirmation bias) | Also search for why it might be SAFE (fixed versions, mitigations) |
| One SEO blog as sole evidence | Cross-check Critical/High claims against advisory databases or vendor sources |
| "No results" interpreted as "no risk" | Absence of evidence ≠ evidence of absence. Note the limit |
| Silent research (not telling the user) | Report-back rule — MANDATORY, including negative results |
| Reading about exploit mechanics, then trying them | You NEVER execute attacks. Describe, don't perform |
