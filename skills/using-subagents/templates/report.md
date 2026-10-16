# Sub-agent Report Template

Sub-agents write their full report to the report-file path given in their delegation prompt, using this structure. The orchestrator points each dispatch at its own report file inside the approved run directory (see `references/work-plan.md` — the storage location is confirmed with the user before execution).

Delete sections the delegation prompt marks optional; do not invent new top-level sections.

---

# Report: [TASK NAME]

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- **Date:** [date]
- **Sub-agent:** [agent type/name used]

## Summary

[2–4 sentences: what was done and the outcome]

## Work performed

[What was implemented / investigated / reviewed — per requirement or per question from the task brief]

## Files changed

[path — what changed, one line each. Explorers: "none (read-only)"]

## Test evidence

[Revision/commit or content fingerprint, scope, tool/dependency versions and environment. Real RED/GREEN commands/output, refactor/fix checks and relevant full final checks. Distinguish executed/reused evidence with references. Record separate new-test/test-review exceptions and alternatives; justify test-contract corrections against requirements. Reviewers assess applicability independently and report probes/unverified claims.]

## Self-review findings

[Issues the sub-agent found and fixed during its own self-review, or "none"]

## Findings (reviewers only)

[file:line, what, why it matters, severity (Critical | Important | Minor), recommendation — grouped by severity]

## Concerns

[Anything the orchestrator should know: doubts, risks, deviations from the brief, surprises in the codebase]

## Handoff notes

[Out-of-scope observations worth another pass, one line each — e.g. "possible security issue at src/auth/login.ts:44". No analysis here — the orchestrator routes these.]
