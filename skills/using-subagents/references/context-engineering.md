# Context Engineering for Delegation

Read in Phases 3–4. A sub-agent's context is your most expensive resource and its only source of truth. What you put in determines what comes out — and what you leave in your OWN context determines how long you stay sharp.

## Contents

- Fresh context is the feature
- What to include
- What to exclude
- File handoffs beat pasted text
- Summaries, not dumps (the return path)
- The telephone game
- Context pollution and your own window

## Fresh context is the feature

Delegation's primary payoff is not parallelism — it's **context isolation**. The sub-agent's verbose middle (file reads, test runs, dead ends) never enters your window; only its compressed result returns. Two consequences:

1. **Cold start is real**: the sub-agent knows NOTHING of your conversation, the user's preferences, or the repo's unwritten conventions. Unwritten context is unshared context.
2. **Pollution cuts both ways**: pasting your whole history into the dispatch destroys the very isolation you dispatched for.

## What to include

Per dispatch, include exactly:

- **The brief**: full task text + acceptance criteria (or a path to the brief file).
- **Scene-setting**: where this task fits, dependencies on completed/planned tasks, interfaces to conform to, conventions to follow.
- **Relevant artifacts as PATHS**: diff files, report files from earlier tasks, interface definitions, key file:line pointers.
- **Constraints**: boundaries, forbidden areas, the no-interactive-questions rule, the output contract.

Test: could a capable new hire execute this task with ONLY this prompt plus repo access? If not, the context is incomplete.

## What to exclude

- **The whole plan** — other tasks anchor and pollute the sub-agent's decisions. Per-task briefs only.
- **Conversation history** — distill the relevant decisions into the context layer instead.
- **Whole files pasted inline** — point to paths; the sub-agent can read.
- **Other sub-agents' raw output** — summarize what this task needs from them, or hand over their report-file path.
- **Your reasoning process** — conclusions, not deliberations.

## File handoffs beat pasted text

For anything longer than a screenful, **hand over a path, not a paste**:

- Briefs live in files (one per task) inside the run directory.
- Diffs for review live in files (`git diff > run-dir/task-N.diff`).
- Reports live in files (`templates/report.md`).
- Inter-task dependencies flow through files (task A writes `interface.md`; task B reads it).

Files are exact, greppable, resumable, and survive context compaction. Pasted text is none of those. This is why the storage-location gate exists (see `references/work-plan.md`).

## Summaries, not dumps (the return path)

The return path mirrors the outbound path:

- **<15-line status message** into your context: status, commits, one-line test summary, concerns, report path.
- **Everything else** stays in the report file until YOU decide to read it.

Read report files selectively: concerns sections always; full reports when the status warrants (DONE_WITH_CONCERNS, BLOCKED, review verdicts) or at integration time. Never bulk-read every report the moment it lands — that re-imports the bloat you delegated away.

## The telephone game

Every hand-off through a middleman degrades: user → you → sub-agent → (report) → you → user. Two compressions are unavoidable (your dispatch, their summary). Don't add more:

- Never relay sub-agent output through a second sub-agent when a file handoff works.
- Never summarize a summary when the user asks for results — read the report file.
- When a sub-agent's finding matters to another sub-agent, hand over the FILE, not your retelling.

## Context pollution and your own window

Guard your own context like it pays your salary:

- Ledger entries are one line per task — not logs.
- Bundle user questions; don't drip-feed.
- At integration time, read diffs over reports (the diff is the truth; the report is the claim).
- If your context still fills despite delegation: compact by writing current plan-state + ledger to the plan file first, so nothing is lost.
