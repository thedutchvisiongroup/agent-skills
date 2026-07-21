# Dependencies and Supply Chain

Read this during Phases 2 and 4, class 7. Software Supply Chain Failures are A03 on the OWASP Top 10 (2025); integrity failures are A08. This class CANNOT be completed from code alone: known-vulnerability status exists only online. The flow is: `extract_dependencies.py` → package list → online advisory lookup (OSV/NVD/GitHub Advisory) per `online-research-protocol.md` trigger #4.

## Contents

- What It Is
- The Review Flow
- Manifest and Lockfile Review
- Known-Vulnerability Lookup (MANDATORY)
- Typosquatting and Malicious Packages
- Install-Time and Build-Time Risks
- Version Pinning and Integrity
- False-Positive Guidance
- Mandatory Online Research Triggers
- CWE/OWASP Mapping

## What It Is

Supply-chain risk enters through code you did not write: vulnerable versions, malicious packages, compromised build steps, unverifiable artifacts. You review the **selection, pinning, and verification** of dependencies — not the dependencies' source code.

## The Review Flow

1. Run `scripts/extract_dependencies.py` (Phase 2) → normalized `ecosystem / package / version` list.
2. Note ecosystems it could NOT parse (they go in "Could NOT verify").
3. Review manifests/lockfiles manually (below).
4. Look up advisories online for the extracted versions — MANDATORY, every review. Prioritize: direct dependencies, security-relevant packages (auth, crypto, parsers, network), anything pinned to old majors.
5. Report each vulnerable package: `package@version`, advisory id + link, severity, and the fixed version (from the advisory). Do not invent version numbers — quote the advisory.

## Manifest and Lockfile Review

1. **Lockfile presence** — libraries may skip them; deployable apps SHOULD have them. Missing lockfile = reproducibility/integrity gap (Medium).
2. **Manifest/lockfile mismatch** — ranges in the manifest that drifted from locked versions; lockfile entries not in the manifest (possible tampering or stale state).
3. **Version ranges that float** — `*`, `latest`, unbounded ranges (`>=`), branch/tag references (`main`, `master`) instead of releases.
4. **Sources** — dependencies from URLs, gists, local paths, forks, or private registries without documented provenance; git dependencies pinned by branch not commit.
5. **Abandoned signals** — very old versions, packages unchanged for years (research whether it's stable-vs-abandoned before claiming risk).

## Known-Vulnerability Lookup (MANDATORY)

Per `online-research-protocol.md`:

- Query **OSV** by ecosystem+name+version (it aggregates GitHub Advisory, NVD, and ecosystem DBs). Cross-check Critical/High against NVD/GitHub Advisory.
- Note **CISA KEV** membership (actively exploited → upgrade urgency Critical).
- Verify the vulnerable RANGE covers the locked version — advisory ranges, not vibes.
- If online lookup is impossible (no network): state it explicitly, list the packages that NEED checking, and mark the whole class "Could NOT verify". Never present unchecked versions as safe.

## Typosquatting and Malicious Packages

Signals (each → research the package online before judging):

- Name near-identical to a popular package (character swaps, added hyphens/prefixes/suffixes).
- Low download/maintenance profile for a package doing something sensitive (crypto, auth, network).
- Single maintainer, very recent creation, version jumps inconsistent with age.
- Obfuscated code, unexpected install scripts, network calls at install time (see below).
- Dependency-confusion shape: internal-sounding names that also exist on the PUBLIC registry (private names must be reserved/scoped).

## Install-Time and Build-Time Risks

1. **Install scripts** — pre/post-install hooks in manifests execute arbitrary code at install; flag unexpected ones.
2. **CI/CD integration** — dependencies fetched unpinned in pipelines; pipeline steps that execute dependency-controlled code with secrets in scope (cross-reference `configuration-and-infrastructure.md`).
3. **Vendored/bundled code** — copied libraries in-tree without version provenance (they never get advisories — flag for SBOM/inventory).
4. **Generated artifacts committed** — minified/bundled files whose inputs are unverifiable.

## Version Pinning and Integrity

- Lockfiles SHOULD include integrity hashes (most ecosystems do); absence → note.
- Containers: base images pinned by digest, not `latest` (cross-reference `configuration-and-infrastructure.md`).
- CI actions/plugins pinned by commit SHA, not mutable tags.

## False-Positive Guidance

Do NOT report when:

- The locked version is outside the advisory's vulnerable range (VERIFY the range — quote it).
- The package is dev-only AND the advisory's vector is runtime-only — downgrade with rationale, don't drop.
- A vulnerability affects an unused code path — report as lower severity ONLY if non-reachability is demonstrable from code; otherwise report normally.
- "Old" ≠ "vulnerable" — age without an advisory is an observation, not a finding.

## Mandatory Online Research Triggers

- Every extracted dependency version (protocol trigger #4 — no exceptions).
- Any typosquat/malicious-package signal (registry metadata, creation date, maintainer).
- Whether a suspicious package is abandoned vs stable.
- Vulnerable-code-path reachability claims (advisory details describe affected functions).

## CWE/OWASP Mapping

| Pattern | CWE | OWASP |
|---------|-----|-------|
| Known-vulnerable dependency | CWE-1395 (via advisory) | A03:2025 Software Supply Chain Failures |
| Missing lockfile / floating versions | CWE-1104 | A03/A08:2025 |
| Unpinned external artifacts | CWE-494/1357 | A08:2025 Software or Data Integrity Failures |
| Typosquat / malicious package risk | CWE-1357/506 | A03:2025 |
| Install scripts / build-time execution | CWE-829/494 | A03:2025 |
| ASVS | V15 (Secure Coding and Architecture — SBOM/dependency management) | — |
