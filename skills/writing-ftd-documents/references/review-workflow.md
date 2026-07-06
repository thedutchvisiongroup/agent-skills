# Review & Restructure Workflow

## Contents
- When to use this workflow
- Mode A: Audit (gap report on existing document)
- Mode B: Restructure (legacy doc → FTD-conform document)
- Mode C: Feature-structuring (loose feature description → FTD-feature format)
- Clarification gate (all modes)
- Cross-references

This reference supports the **Phase R** workflow in SKILL.md. It is loaded when the user asks to review, audit, improve, or restructure an existing FTD, design document, or feature description — instead of drafting a new one from scratch.

## When to use this workflow

Use Phase R when ANY of:
- The user provides an existing FTD/FSD/TSD/SDD and asks to "review", "audit", "check", or "improve" it.
- The user provides a legacy design document (Word, Confluence, wiki, markdown) and asks to restructure it into FTD format.
- The user provides a loose feature description (Jira ticket, OneNote, email, Confluence page) and asks to structure it into FTD-feature format.
- The user asks "is this FTD complete?" or "what's missing in this design?".

Do NOT use Phase R when:
- The user wants a brand-new FTD from scratch — use the standard Phase 0 → 1 → 2 → 3 → 4 flow.
- The user wants only a single diagram — produce it directly.
- The user asks how to *use* an existing system — that is documentation, not design review.

## Clarification gate (all modes)

Before any work, ask the user:

1. **Which mode?** — Audit (report only), Restructure (rewrite to FTD), or Feature-structuring (single feature to FTD-feature format).
2. **Source document** — file path, paste, or URL of the existing document.
3. **Target scenario** (for Restructure and Feature-structuring) — feature / project / enterprise, per [scenario-identification.md](scenario-identification.md).
4. **Output language** — English or Dutch (inherit from source if unclear, but confirm).
5. **Output mode** — Markdown only, HTML only, or both.
6. **Acceptance criteria format** — bullets or EARS (see [acceptance-criteria.md](acceptance-criteria.md)). Required for Restructure and Feature-structuring.
7. **Filename and storage location** — for Restructure and Feature-structuring output.

For Audit mode, only questions 1-2 are mandatory; the rest are optional.

## Mode A: Audit (gap report)

Goal: assess an existing document against the FTD standard and produce a prioritised gap report. **No changes are made to the source document.**

### Steps

1. **Read the source document** in full.
2. **Run `python scripts/validate.py <source> --scenario <feature|project|enterprise> --audit`** to get the automated gap report. If the scenario is unknown, run with `--scenario project` as default and note the assumption.
3. **Manual review** against the toggle matrix in [scenario-identification.md](scenario-identification.md):
   - For each mandatory (M) section: present / missing / incomplete / boilerplate.
   - For each optional (O) section: present / missing (acceptable).
   - For each enterprise-only (E) section (enterprise scenario): present / missing.
4. **Quality checks**:
   - User stories: are they in "As a…/I want…/So that…" format? Do they pass INVEST?
   - Acceptance criteria: single testable statements? Boundary values and error paths covered?
   - NFRs: every NFR has Subject / Attribute / Metric / Threshold / Verification?
   - Privacy-by-design: present and populated (not boilerplate)? Data inventory complete?
   - Security-by-design: present and populated? ASVS level stated? Threat model where required?
   - Traceability matrix: no orphan requirements, no orphan tests?
   - DoR/DoD: explicit and complete?
   - Diagrams: Mermaid renders? C4 levels appropriate for scenario?
   - Benefit hypothesis (project/enterprise): present and measurable?
   - Glossary (project/enterprise): present?
   - Crosscutting Concepts (enterprise): present?
5. **Produce the gap report** in this format:

```markdown
# Audit report — [document name]

| Field | Value |
|-------|-------|
| Source document | [path/name] |
| Detected scenario | feature / project / enterprise |
| Audit date | YYYY-MM-DD |
| Auditor | [name/agent] |

## Summary

- Total sections expected: [N]
- Present: [N]
- Missing (mandatory): [N]
- Incomplete / boilerplate: [N]
- Overall verdict: PASS / NEEDS IMPROVEMENT / FAIL

## Findings by priority

### Critical (mandatory section missing or non-functional)
| # | Section | Issue | Recommendation |
|---|---------|-------|----------------|
| 1 | Privacy-by-design | Section absent | Add section; document data inventory and DPIA decision |
| 2 | NFRs | "Should be fast" — not measurable | Rewrite as Subject/Attribute/Metric/Threshold/Verification |

### Important (mandatory section present but incomplete)
| # | Section | Issue | Recommendation |
|---|---------|-------|----------------|
| 3 | Traceability matrix | 2 user stories without test case IDs | Add TC-XX for US-03 and US-04 |

### Nice-to-have (optional section or polish)
| # | Section | Issue | Recommendation |
|---|---------|-------|----------------|
| 4 | Sequence diagrams | Only happy-path shown | Add error-case sequence for the payment flow |

## Next steps

1. Address all Critical findings.
2. Address Important findings.
3. Consider Nice-to-have findings.
4. Re-run `python scripts/validate.py <file> --scenario <scenario>` to verify.
```

6. **Present the report** to the user. Do not modify the source document. Offer to enter Restructure mode if the user wants the gaps fixed.

### Anti-patterns in Audit mode

- Silently fixing issues — Audit is report-only. The user decides what to fix.
- Running the validator and stopping — the manual quality checks (INVEST, boilerplate detection, diagram render) are non-automatable and mandatory.
- Skipping the manual review because the validator passed — the validator checks presence, not quality.

## Mode B: Restructure (legacy doc → FTD-conform document)

Goal: take an existing design document (legacy FTD, SDD, Word doc, Confluence page, wiki) and produce a new FTD-conform document that passes validation.

### Steps

1. **Read the source document** in full. Identify what kind of document it is and what scenario it maps to.
2. **Run the clarification gate** (above) — confirm mode, scenario, output language, output mode, AC format, filename.
3. **Extract content per dimension**:
   - **Scope**: what does the source say is in/out? What's the boundary? What's the success criterion?
   - **Functional**: who are the personas? What user stories are implicit or explicit? What business rules? What edge cases?
   - **Technical**: what architecture is described? What integrations? What NFRs (often implicit — extract and make measurable)? What data model?
   - **Output**: confirmed in the gate.
4. **Identify gaps** — what is present in the source vs. what the FTD template requires:
   - Missing sections (e.g. no privacy-by-design, no traceability matrix)
   - Incomplete sections (e.g. NFRs stated as "fast" without thresholds)
   - Implicit content (e.g. user stories embedded in prose that need to be extracted to INVEST format)
5. **Run the Phase 1 intake** (from SKILL.md) **only for the gaps**. Do not re-ask what the source already answers clearly. Probe only what is missing or ambiguous.
6. **Draft the new FTD** using [ftd-template.md](ftd-template.md) with toggles for the confirmed scenario. Map extracted content into the template. Fill gaps with answers from the intake.
7. **Revision history**: add an entry "Restructured from [source document name/version] by [agent] on [date]" as the first revision. Preserve the original author and date where known.
8. **Validate**: run `python scripts/validate.py <new-file> --scenario <scenario>` and fix every error.
9. **Deliver**: save at the confirmed location and filename. Present to the user.

### Anti-patterns in Restructure mode

- Re-asking questions the source document already answers — extract first, probe only gaps.
- Silently inventing content for gaps — every gap must be flagged back to the user in the intake.
- Discarding the source's revision history — preserve it; the restructured doc is a continuation, not a replacement.
- Skipping the clarification gate because "the source has the info" — the gate confirms output decisions (split, language, mode, AC format, filename) which the source does not dictate.

## Mode C: Feature-structuring (loose feature description → FTD-feature format)

Goal: take a loose feature description (Jira ticket, Confluence page, OneNote, email, product brief) and structure it into the FTD-feature format from [ftd-template.md](ftd-template.md), producing a self-contained piece that can either stand alone or slot into a larger FTD.

### Steps

1. **Read the source feature description** in full.
2. **Run the clarification gate** (above) — confirm mode (feature-structuring), target scenario (almost always `feature`, but confirm — could be `project` if the "feature" turns out to be multi-team), output language, output mode, AC format, filename.
3. **Identify the scenario** per [scenario-identification.md](scenario-identification.md). If the "feature" touches multiple teams, regulated data, or external suppliers, propose a higher tier — do not silently downscale.
4. **Extract and structure** into the condensed FTD-feature template:
   - **Document control** — derive a feature ID and title from the source.
   - **Scope & objectives** — extract or infer the problem statement, in/out scope, success criteria.
   - **User stories** — rewrite the source's feature description into "As a…/I want…/So that…" (or Dutch equivalent) and check against INVEST. Split if the source describes multiple stories.
   - **Acceptance criteria** — in the format chosen in the gate (bullets or EARS). Convert vague statements ("it should work") into testable criteria. Include edge cases (empty, oversized, malformed, unauthorised, concurrent).
   - **Benefit hypothesis** (project/enterprise: mandatory; feature: optional) — if the source contains an expected outcome, formalise it: "We believe [business outcome] will be achieved if [users] achieve [user outcome] with [feature]." Add a measurable target and validation method.
   - **Traceability matrix** — map each user story to a design component and test case ID. If the design component is not yet known, mark as TBD.
   - **DoR / DoD** — populate from the standard template in [ftd-template.md](ftd-template.md) §9. DoD is ALWAYS mandatory, even for a single feature.
   - **NFRs** — if the feature has performance, security, or accessibility impact, extract NFRs in Subject/Attribute/Metric/Threshold/Verification format. If not, state "no feature-specific NFRs; inherits system-level NFRs" with a reference.
   - **Privacy-by-design** — ALWAYS present. If the feature does not touch personal data, state that explicitly with justification. If it does, complete the data inventory.
   - **Security-by-design** — ALWAYS present. Document authentication, authorisation, and any feature-specific security controls. If minimal, state that explicitly.
   - **Approvals & sign-off** — populate with the feature owner and relevant approvers.
5. **Validate**: run `python scripts/validate.py <new-file> --scenario feature` and fix every error.
6. **Deliver**: save at the confirmed location and filename. Present to the user. Offer to merge into a parent FTD if one exists.

### Anti-patterns in Feature-structuring mode

- Treating a Jira ticket as already complete — most tickets lack NFRs, PbD/SbD, and edge cases. The value of this mode is filling those gaps.
- Skipping DoD because "it's just one feature" — DoD is always mandatory.
- Inventing acceptance criteria not supported by the source — probe the user for missing criteria; do not fabricate.
- Forcing the full project template on a genuine single-feature input — use the condensed feature template and let the agent drop optional sections per scenario-identification rules (DoD stays mandatory).

## Cross-references

- [scenario-identification.md](scenario-identification.md) — for toggle matrix and scenario conflict resolution
- [ftd-template.md](ftd-template.md) — for the master template and section structure
- [acceptance-criteria.md](acceptance-criteria.md) — for bullets vs EARS format
- [intake-questions.md](intake-questions.md) — for probing during gap-filling in Restructure mode
- [nfr-taxonomy.md](nfr-taxonomy.md) — for making implicit NFRs measurable
- [privacy-by-design.md](privacy-by-design.md) and [security-by-design.md](security-by-design.md) — for the always-mandatory PbD/SbD sections
- `scripts/validate.py --audit` — for the automated gap report in Audit mode
