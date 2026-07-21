# Dead Code Review

Read this during Phase 5 (Design and Maintainability). Dead code is code that costs maintenance, review time, and clarity — while delivering nothing. The reviewer's job: find candidates, present evidence, recommend removal. The reviewer NEVER deletes anything.

## Contents

- What Counts as Dead Code
- Why It Matters
- Detection Strategy
- False-Positive Caution
- Confidence Classification
- Safe-Removal Playbook (advice for the author)
- Review Checklist

## What Counts as Dead Code

- **Unused functions, methods, classes** — nothing calls them
- **Unused files/modules** — not reachable from any entry point
- **Unused exports** — exported, but no file imports them
- **Unused variables, parameters, fields** — declared, never read
- **Zombie dependencies** — present in the dependency manifest, never imported or used
- **Commented-out code** — always dead; version control is its archive
- **Unreachable branches** — code after `return`/`throw`, provably impossible conditions
- **Dead feature flags** — flags permanently on or off; the dead branch is dead code
- **Orphaned tests and docs** — testing or documenting code that no longer exists
- **Unused configuration keys** — nothing reads them

## Why It Matters

- **Confusion:** readers investigate the purpose of code that has none
- **Maintenance tax:** dead code still gets compiled, linted, refactored, and reviewed
- **False confidence:** the codebase appears to offer functionality it doesn't
- **Drag on change:** fear of touching dead code slows real work

## Detection Strategy

Work language-agnostically; use what the project already provides.

1. **Mine the Phase 2 output.** Lint warnings about unused variables, imports, or unreachable code ARE dead-code leads. Collect them instead of discarding them as noise.
2. **Reference search.** For each suspect symbol, search the entire codebase — source, tests, configs, templates, string-based references. Zero references → candidate.
3. **Entry-point reachability.** Trace from entry points (routes, CLI commands, main functions, public API exports). Files unreachable from every entry point are candidates.
4. **Manifest vs. imports.** Every dependency in the manifest should be imported/required somewhere, or used by build/tooling configuration. Otherwise it's a zombie dependency.
5. **Commented-out blocks.** Always candidates. No analysis needed.
6. **Feature flags.** A flag that is permanently on or off makes one branch dead.

## False-Positive Caution

Dead-code detection over-reports. Before flagging, consider dynamic usage:

- **Reflection / dynamic dispatch** — string-based lookups, dynamic imports, plugin loading
- **Framework magic** — dependency injection, decorators, registered handlers, lifecycle hooks, ORM models and DTOs populated by the framework
- **Public APIs / published libraries** — "unused" internally may mean "used by consumers"
- **Entry points wired in config** — cron jobs, event handlers, queue consumers, CLI registrations
- **Templates, i18n keys, config-driven references**

## Confidence Classification

Report every candidate with its confidence level:

| Confidence | Applies to | How to phrase |
|-----------|-----------|---------------|
| **CERTAIN** | Unused locals/params, unreachable branches, commented-out code | `issue (non-blocking):` — recommend removal |
| **LIKELY** | Unreferenced private functions/files after full-text search | `suggestion:` — present the search evidence |
| **NEEDS CONFIRMATION** | Exported/public symbols, framework-invoked code | `question:` — "I found no references to X — is it still needed?" |

## Safe-Removal Playbook (advice for the author)

When recommending removal, include this playbook:

1. Remove one category at a time (unused files first, then exports, then internals)
2. Run the full test suite and linter after each step
3. One logical deletion per commit — trivial to revert
4. Double-check dynamic references (config, reflection, DI wiring) before deleting
5. Trust version control, not comments — "keep it just in case" is what `git log` is for

## Review Checklist

- [ ] Phase 2 lint output mined for unused-code warnings
- [ ] Suspect symbols searched across source, tests, configs, templates
- [ ] Reachability from entry points verified for suspect files
- [ ] Dependency manifest compared against actual imports
- [ ] Commented-out code flagged
- [ ] Dead feature-flag branches identified
- [ ] Dynamic-usage false positives considered before flagging
- [ ] Every candidate reported with evidence AND confidence level
- [ ] Nothing deleted — findings only
