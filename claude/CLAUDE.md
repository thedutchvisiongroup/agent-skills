# TDVG Global Instructions

## Mandatory: simple code skill

Before any technical work (code, tests, scripts, configuration, dependencies,
technical design or recommendations), invoke the `writing-simple-code` skill
via the Skill tool and follow it. Not needed for purely non-technical work.

## Minimize your own cost, always

- Delegate only when it pays off: do small or tightly coupled tasks directly.
  Use subagents only for bounded work that would flood your context or needs
  independent review. Never duplicate a dispatch or redo delegated work.
- Read narrowly: search (Grep/Glob) before reading, read only the relevant
  parts of large files, read a skill's references only when the skill or the
  current phase requires it, and never dump tool output.
- Keep output concise: no preamble or recaps. Put detailed results in report
  files and give short summaries in chat.
- Reuse evidence: do not rerun full test suites or research while revision,
  scope and environment are unchanged. Run focused checks when in doubt.

## Secrets

Never put secrets (API keys, tokens, credentials) in repositories or prompts.

## TDVG subagents

Available subagents: `implementer` (tests and source through Red-Green-Refactor),
and the advisory reviewers `code-reviewer`, `tdd-expert` and `security-reviewer`.
