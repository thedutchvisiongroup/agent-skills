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

[Commands run and their relevant output. When TDD was required: RED evidence (failing test before implementation) and GREEN evidence (passing after). Reviewers: assessment of the implementer's evidence plus any re-runs you performed. This section is the evidence — keep the real commands and outputs.]

## Self-review findings

[Issues the sub-agent found and fixed during its own self-review, or "none"]

## Findings (reviewers only)

[file:line, what, why it matters, severity (Critical | Important | Minor), recommendation — grouped by severity]

## Concerns

[Anything the orchestrator should know: doubts, risks, deviations from the brief, surprises in the codebase]

## Handoff notes

[Out-of-scope observations worth another pass, one line each — e.g. "possible security issue at src/auth/login.ts:44". No analysis here — the orchestrator routes these.]
