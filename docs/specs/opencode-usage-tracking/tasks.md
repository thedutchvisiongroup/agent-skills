# Usage Tracking Plugin — Implementation Tasks

Implements [FTD-opencode-usage-tracking-v1.0](docs/specs/FTD-opencode-usage-tracking-v1.0.md) (project scenario).
Groups are ordered implementation batches; each maps to FTD user stories (US-01..06) and ends with its own Definition of Done.
Work top-to-bottom within a group; groups 0–1 first, 8 last. Keep this file checked off as work progresses.

| Group | Scope | Maps to |
|-------|-------|---------|
| 0 | Spike: event & config verification | OQ-1/2/3, R-02/R-03 |
| 1 | Plugin skeleton & fail-open foundation | ADR-05, NFR-04 |
| 2 | Session lifecycle capture | US-01, AC 7.1 |
| 3 | Step, token & tool tracking | US-01/02, AC 7.1/7.2 |
| 4 | Storage layer & configuration | US-04, AC 7.4, ADR-02/03 |
| 5 | Recursive subagent tracking | US-03, AC 7.3 |
| 6 | Status command | US-05, AC 7.5 |
| 7 | Verification: tests & smoke | US-06, AC 7.6, NFR-01..06 |
| 8 | Deployment, docs & closure | FTD §9.2, §17 |

---

## Group 0 — Spike: event & config verification

Resolves the FTD open questions before building on unverified assumptions. Uses a temporary debug plugin (throwaway, never merged).

- [ ] Verify plugin tuple-options form works for **local plugin paths** on live OpenCode ≥ 1.18.x (OQ-1, R-02): load `["./plugins/usage-tracking/index.ts", { … }]` and log the received options object
- [ ] Probe exact payloads of `session.created`, `session.updated`, `session.idle`, `session.deleted` (fields: sessionID, info, timestamps) (OQ-2, R-03)
- [ ] Probe `message.part.updated` payloads for part types `step-finish`, `step-start`, and tool parts — record exact field names (`tokens`, `cost`, `cache`, `time`, agent, modelID, providerID)
- [ ] Identify which event carries the auto-generated session title (rename/update) and its exact payload (OQ-2)
- [ ] Verify where model variant/reasoning metadata is exposed: event fields vs. SDK model/session lookup (OQ-3)
- [ ] Verify how child sessions surface: `parentID` in session info, and the timing of `session.created` for children spawned by the task tool
- [ ] Confirm `scripts/link.py` can sync `opencode/plugins/usage-tracking/*` and `opencode/command/usage-status.md` as item keys; extend the script if directory sync is missing
- [ ] Record all findings in this file (append a "Spike findings" section) and update the FTD if any finding contradicts the design

### DoD — Group 0
- [ ] Field map documented for every event type the plugin will consume
- [ ] Go/no-go decision on tuple-options recorded; fallback chosen (defaults + explicit global config entry) if unsupported
- [ ] Title event, idle payload, and variant metadata source confirmed with evidence
- [ ] link.py sync path verified (or extension task filed as concrete subtask)
- [ ] FTD §21 open questions annotated; revision history updated on material deviations

---

## Group 1 — Plugin skeleton & fail-open foundation

- [ ] Create `opencode/plugins/usage-tracking/index.ts` exporting the default plugin function (`PluginInput` signature, options param)
- [ ] Keep zero runtime npm dependencies — type-only imports from `@opencode-ai/plugin` (FTD §15)
- [ ] Implement the fail-open wrapper: every hook callback runs in try/catch; errors logged once via `client.app.log` (service `usage-tracking`) and swallowed — never rethrow (ADR-05)
- [ ] Emit `plugin.initialized` log event with a config summary
- [ ] Register the `event` hook with an empty dispatcher (wiring only, no logic yet)
- [ ] Add project scaffolding: `package.json`, `tsconfig.json`, and a runnable empty `bun test`
- [ ] Add link.py item keys for the plugin directory; link, restart OpenCode, and confirm the init log line appears

### DoD — Group 1
- [ ] OpenCode starts with the plugin loaded; `plugin.initialized` visible in the log
- [ ] An induced error inside a hook leaves OpenCode fully unaffected (manual verification)
- [ ] `bun test` runs green with the empty harness
- [ ] Plugin reachable via symlink in `~/.config/opencode/plugins/`; restart verified

---

## Group 2 — Session lifecycle capture (US-01)

- [ ] EventRouter: on `session.created`, emit `session.started` with sessionID, parentID (if any), projectID, directory/worktree path, agent, model `{id, providerID, variant}`, and timestamp
- [ ] MetadataResolver: SDK lookup for session info, cached per sessionID (first event per session)
- [ ] Capture the auto-generated session title as soon as it becomes available (event per Group 0 findings) and write it to the aggregate
- [ ] Track model switches: maintain the models list in the aggregate from message/session metadata
- [ ] Track the set of active agents per session (agents list)
- [ ] On `session.idle`, finalise the aggregate (activeMs, final totals) — idempotent, safe on repeated idle events (ADR-02, R-03)
- [ ] On `session.deleted`, log a `session.deleted` event; collected data is retained (no deletion — FTD §11.3)
- [ ] In-memory session state map with eviction after finalisation to bound memory

### DoD — Group 2 (AC 7.1)
- [ ] `session.started` written on `session.created` with all AC 7.1 fields present
- [ ] Title lands in the aggregate once generated
- [ ] A model switch mid-session results in all used models in the aggregate's model list
- [ ] `session.idle` finalises the aggregate idempotently
- [ ] No message text, prompt content, or tool output is ever written to storage (verified by inspection of all written files)

---

## Group 3 — Step, token & tool tracking (US-01/02)

- [ ] Handle `message.part.updated` with part type `step-finish`: emit `step.finished` within 1 s with sessionID, messageID, partID, agent, modelID, providerID, `tokens {input, output, reasoning, cache.read, cache.write}`, cost, stepMs
- [ ] Measure step duration from `step-start` part timestamps; accumulate into active agent time (activeMs)
- [ ] Handle tool parts/events: emit `tool.executed` (sessionID, tool name, ok flag)
- [ ] SessionAggregator: per-session token totals, cost total, and toolCounts per tool name
- [ ] De-duplicate streamed part updates: count each step/tool part exactly once (parts update incrementally — use final state only)
- [ ] Asynchronous write queue so event processing never blocks the host (NFR-01)

### DoD — Group 3 (AC 7.1/7.2, NFR-03)
- [ ] Every step-finish produces exactly one `step.finished` event with the full breakdown including cache read/write and reasoning tokens
- [ ] toolCounts present in the aggregate per tool name
- [ ] activeMs accumulates step durations only — no user idle time
- [ ] Events persisted within 1 s of emission (NFR-03)

---

## Group 4 — Storage layer & configuration (US-04)

- [ ] ConfigResolver: parse tuple-options (output root, `excludeAgents`, toggles) with safe defaults; unknown or invalid options are ignored with exactly one warning (AC 7.4)
- [ ] Default output root `~/.local/share/opencode-usage/` with a per-project subdirectory derived from projectID/path
- [ ] EventStore: append-only JSONL writer per project (`events.jsonl`), `mkdir -p` on first write
- [ ] Aggregate store: upsert `sessions/<sessionID>.json` on every state change
- [ ] Aggregate rebuild function: reconstruct any aggregate from the JSONL stream (ADR-02 recovery path)
- [ ] Guarantee no file is written inside any git worktree unless `output` is explicitly configured to a worktree path (AC 7.4)
- [ ] Log a warning when a session's storage footprint exceeds 100 KB (NFR-06 visibility)
- [ ] Handle write errors (disk full, read-only path): single `write.error` log event, degrade without crash (ADR-05, R-05)

### DoD — Group 4 (AC 7.4)
- [ ] With no options configured, data lands under the default central root in a per-project directory
- [ ] A project-level `opencode.json` plugin entry overrides the global entry's options (verified on live instance)
- [ ] Unknown option → exactly one warning; OpenCode continues normally
- [ ] A corrupted aggregate file is deleted and correctly rebuilt from `events.jsonl`
- [ ] Induced write failure leaves OpenCode unaffected (fail-open verified)

---

## Group 5 — Recursive subagent tracking (US-03)

- [ ] Treat child sessions (parentID set) identically to top-level sessions, at any nesting depth
- [ ] Compute nesting depth by walking the parentID chain
- [ ] Parent aggregate: children list with sessionID, agent, depth, and usage totals per child
- [ ] Roll child usage up into the parent's totals (child records also remain standalone)
- [ ] Handle arrival ordering: a child's `session.created` can arrive mid-parent-session; attach when seen
- [ ] Optional `excludeAgents` option: filter internal agents (title/compaction) out of the roll-up when configured (R-04)

### DoD — Group 5 (AC 7.3)
- [ ] Child sessions tracked with the same event set as top-level sessions at any depth (verified with a nested dispatch)
- [ ] Parent aggregate lists all children with agent, depth, and totals
- [ ] Parent totals include subagent usage; each child record is also complete on its own
- [ ] A subagent dispatch during the smoke test produces a child aggregate

---

## Group 6 — Status command (US-05)

- [ ] Track plugin counters in state: sessions/events written, error count, last write timestamp
- [ ] Register the `usage_status` custom tool returning: configured output path, tracked session/event counts, last write timestamp, error count, and the current session's running totals (tokens + cost)
- [ ] Create `opencode/command/usage-status.md` that invokes the `usage_status` tool and returns its output verbatim

### DoD — Group 6 (AC 7.5)
- [ ] `/usage-status` returns all listed fields
- [ ] The command file returns the tool output verbatim (no added text)
- [ ] Running totals update live within the same session

---

## Group 7 — Verification: tests & smoke (US-06)

- [ ] Bun unit tests: event mapping for every consumed event type (fixtures from Group 0 field map)
- [ ] Bun unit tests: aggregation logic — totals, toolCounts, activeMs, model list, dedup, idempotent finalisation
- [ ] Bun unit tests: ConfigResolver — defaults, project override, unknown/invalid options warning
- [ ] Bun unit tests: error isolation — injected failures never propagate (fail-open)
- [ ] Reach ≥ 80% line coverage on router/aggregator/config (NFR-05, `bun test --coverage`)
- [ ] Performance benchmark: ≤ 5 ms p95 synchronous processing per event excluding disk write (NFR-01)
- [ ] Smoke script `scripts/smoke_usage_tracking.sh`: start headless OpenCode, run a scripted session including a subagent dispatch, assert plugin loaded, aggregate produced, all files valid JSON/JSONL; exit non-zero on any failure
- [ ] Smoke script asserts NFR-02 (no host failures) and checks sample session footprint ≤ 100 KB (NFR-06)

### DoD — Group 7 (AC 7.6, NFR-01..06)
- [ ] `bun test` green with ≥ 80% coverage on the core modules
- [ ] Smoke script exits 0 on the live workstation, including the subagent dispatch path
- [ ] All six NFRs verified using their stated verification method
- [ ] Acceptance criteria 7.1–7.6 demonstrated and checked off in the FTD traceability matrix

---

## Group 8 — Deployment, docs & closure

- [ ] Finalize link.py item keys: `opencode/plugins/usage-tracking/*` and `opencode/command/usage-status.md`
- [ ] Update AGENTS.md / README.md if the repo structure changed (repo rule)
- [ ] Deploy: `uv run scripts/link.py link` → restart OpenCode → smoke script (exit 0) → verify via `/usage-status` (FTD §17)
- [ ] Update the FTD: revision history, traceability matrix statuses, and §21 open-question resolutions
- [ ] Add a `docs/specs/log.md` entry for the implementation milestone
- [ ] Record owner sign-off in FTD §20
- [ ] Park V2 backlog explicitly out of scope: OpenRouter pricing enrichment incl. OQ-4 decision (ADR-04)

### DoD — Group 8 (FTD §9.2)
- [ ] Deployed and verified healthy on the workstation after restart (`/usage-status` responds)
- [ ] Fail-open path re-verified post-deploy (induced write failure)
- [ ] FTD and log.md updated; all open questions resolved or explicitly parked
- [ ] Owner sign-off recorded; every group above is fully checked off

---

## Spike findings (append after Group 0)

<!-- Document verified event payloads, tuple-options behaviour, and link.py results here. -->
