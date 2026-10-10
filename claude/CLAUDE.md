# TDVG Global Instructions

These rules apply to every project. Project instructions (`AGENTS.md`,
`CLAUDE.md`, project docs) take precedence where they conflict.

## Mandatory: simple code skill

Before any technical work (code, tests, scripts, configuration, dependencies,
technical design or recommendations), invoke the `writing-simple-code` skill
via the Skill tool and follow it. Not needed for purely non-technical work.

## Mandatory: Ask before you assume

- When scope, requirements, constraints or success criteria are unclear, or
  doubt arises mid-task, stop and ask before acting. Bundle concrete questions
  via `AskUserQuestion` and keep asking in multiple rounds until no doubt
  remains. Asking too much is always better than guessing even one thing.
- Never make a material decision (architecture, product behaviour, scope,
  guarantees) on an assumption.

## Minimize your own cost, always

- Delegate only when it pays off (see "Choose a route"). Never duplicate a
  dispatch or redo delegated work.
- Read narrowly: search (Grep/Glob) before reading, read only the relevant
  parts of large files, read a skill's references only when the skill or the
  current phase requires it, and never dump tool output.
- Keep output concise: no preamble or recaps. Put detailed results in report
  files and give short summaries in chat.
- Reuse evidence: do not rerun full test suites or research while revision,
  scope and environment are unchanged. Run focused checks when in doubt.

## Choose a route: do it yourself or delegate

Be critical about what you can do yourself and when subagents pay off. For
every non-trivial task, propose one route and wait for the user's choice
(trivial questions, reads and one-line fixes need no proposal):

1. **Direct**: small, tightly coupled, interactive or judgement-heavy work.
   Do it yourself in the main conversation.
2. **Implementer**: one bounded implementation task that benefits from a fresh
   context. Brief the `implementer` subagent with a complete contract.
3. **Orchestration**: multi-part features or refactors. Load the
   `using-subagents` skill and follow it.

TDVG subagents: `implementer` (tests and source through Red-Green-Refactor)
and the advisory reviewers `code-reviewer`, `tdd-expert` and
`security-reviewer`. After delegated implementation, schedule independent
review by `code-reviewer` and `tdd-expert`, plus `security-reviewer` for auth,
payments, PII, crypto/secrets, uploads/external input, dependencies or
security-relevant configuration. Subagents cannot ask the user; you own all
user contact.

## Working style

- Lead with the result, then only relevant details. Reference code as
  `path:line`.
- For non-trivial work, show a short plan and get approval before executing.
- When choosing, name the alternatives briefly with a recommendation.
- Chat in the user's language (usually Dutch). Write code, comments, commits,
  branch names and technical docs in English unless the project prescribes
  otherwise.

## Tooling: Devbox and Just

Most TDVG projects provide their toolchain through Devbox and their tasks
through Just.

- If `devbox.json` exists, run tools through it: `devbox run -- <command>`.
  direnv does not activate in your shell, so Devbox tools (including `just`)
  are not on PATH. Never fall back to system-installed versions.
- Start with `devbox run -- just --list` and use existing recipes (test, lint,
  format, build, `docker-*`) instead of ad-hoc commands. Without a justfile,
  use Devbox `scripts`, then the package manager's scripts.
- Never install anything globally (`npm -g`, `pip`, `apt`, `brew`, ...). New
  tooling goes into `devbox.json` or the project's dependencies, only after
  approval.
- Run Docker only through project recipes and only when the task needs it.
  Ask before destructive Docker actions (removing volumes, prune).

## Quality and verification

- Follow existing project conventions, structure and helpers. Use the
  project's formatter and linter. No unrequested refactors outside scope.
- Features and bug fixes you implement yourself follow
  `test-driven-development` (Red-Green-Refactor) unless the user grants an
  exception.
- For bugs, failing tests or unexpected behaviour, use `systematic-debugging`:
  root cause before fix.
- Before reporting work as done, run the relevant test, lint, format and
  typecheck recipes. Report honestly what was not run or failed.

## Research and documentation

- For libraries, frameworks, APIs and tools, consult current documentation
  (look at available MCPs for official docs) instead of memory. Derive versions
  from lockfiles and manifests. Name your sources and state uncertainty.
- Use `writing-okf` for knowledge docs, `writing-adrs` for architecture
  decisions, `writing-ftd-documents` for functional/technical designs and
  `keeping-a-changelog` for changelogs and release notes.

## Git and commits

- On the default branch, propose a branch `<type>/<short-slug>` before making
  changes. Branch names are always in lowercase. The types must match the types 
  of the Conventional Commit standard. 
- Never commit on your own: when work is done, propose a commit message and
  ask whether to commit.
- Never push, force-push, open or merge PRs, or delete branches without an
  explicit request. Use `gh`; PR titles follow Conventional Commits.
- Conventional Commits in English: `type(scope): subject`, imperative,
  lowercase, at most 72 characters, no period. The body explains why.
- The scope follows the path or module hierarchy, joined by ` > `, as deep as
  needed for precision: `feat(app > services > exports): add CSV writer`,
  `refactor(packages > app > ts): ...`. A short scope is fine when
  unambiguous; omit it for repository-wide changes.
- Unfinished work gets `WIP, ` after the scope:
  `feat(app > services > exports): WIP, add CSV writer`.
- One logical change per commit. Mark breaking changes with `!` and a
  `BREAKING CHANGE:` footer.
- Never skip hooks (`--no-verify`); fix the cause of a failing hook.

## Safety

- Ask before irreversible actions: deleting files or directories, resetting
  or rolling back databases, deleting data, `git reset --hard`, rewriting
  history.
- Never touch production or staging servers, databases or deployments unless
  explicitly asked for that specific action.

## Secrets

- Never put secrets (API keys, tokens, credentials) in repositories or prompts.
- Never read, print or commit `.env.keys`. Use encrypted env files only through
  `dotenvx`; never decrypt values into output or logs.
- If you find a plaintext secret in code or history, report it immediately. Do
  not rotate it or rewrite history yourself.
