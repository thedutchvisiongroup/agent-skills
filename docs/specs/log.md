# Directory Update Log

## 2026-08-29
* **v1.3 bug fix**: [OpenCode Usage Tracking FTD](opencode-usage-tracking/ftd-v1.0.md) revision 1.3 — non-git projects no longer share one output directory (filesystem-root worktree treated as absent; project identity falls back to the directory). Bun suite 85/85 green with the frozen formula vectors untouched; data migration of the old shared directory is a separate pending task.

## 2026-08-27
* **Implementation milestone**: [OpenCode Usage Tracking FTD](opencode-usage-tracking/ftd-v1.0.md) v1.0 implemented (status → Implemented; revision 1.0). Code and security reviews approved; Bun suite 49/49 green; tasks.md checked off with spike findings recorded. Live smoke run, deploy verification and owner sign-off pending (FTD §17, §20).
* **v1.1 improvements**: [OpenCode Usage Tracking FTD](opencode-usage-tracking/ftd-v1.0.md) revision 1.1 — ULID project dirs, overview.json, activeMs fix, device/git info. Bun suite 69/69 green; registry reads hardened (ULID key validation); smoke script asserts the overview shape (H).
* **v1.2 improvements**: [OpenCode Usage Tracking FTD](opencode-usage-tracking/ftd-v1.0.md) revision 1.2 — deterministic hash project directories replace ULID + projects.json. Bun suite 77/77 green; project names are a pure function of (device, project) — no registry, no persisted state.

## 2026-08-20
* **Creation**: Established the [OpenCode Usage Tracking FTD](opencode-usage-tracking/ftd-v1.0.md) (v0.1 draft, project scenario).

## 2026-08-19
* **Creation**: Established the specs bundle with the [OpenCode Model Router FTD](opencode-model-router/ftd-v1.0.md) (v0.1 draft, project scenario).
