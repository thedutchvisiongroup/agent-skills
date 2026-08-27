# Usage Tracking Plugin — Implementation Tasks

Implements [FTD-opencode-usage-tracking-v1.0](ftd-v1.0.md) (project scenario).
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

- [x] Verify plugin tuple-options form works for **local plugin paths** on live OpenCode ≥ 1.18.x (OQ-1, R-02): load `["./plugins/usage-tracking/index.ts", { … }]` and log the received options object
- [x] Probe exact payloads of `session.created`, `session.updated`, `session.idle`, `session.deleted` (fields: sessionID, info, timestamps) (OQ-2, R-03)
- [x] Probe `message.part.updated` payloads for part types `step-finish`, `step-start`, and tool parts — record exact field names (`tokens`, `cost`, `cache`, `time`, agent, modelID, providerID)
- [x] Identify which event carries the auto-generated session title (rename/update) and its exact payload (OQ-2)
- [x] Verify where model variant/reasoning metadata is exposed: event fields vs. SDK model/session lookup (OQ-3)
- [x] Verify how child sessions surface: `parentID` in session info, and the timing of `session.created` for children spawned by the task tool
- [x] Confirm `scripts/link.py` can sync `opencode/plugins/usage-tracking/*` and `opencode/command/usage-status.md` as item keys; extend the script if directory sync is missing
- [x] Record all findings in this file (append a "Spike findings" section) and update the FTD if any finding contradicts the design

### DoD — Group 0
- [x] Field map documented for every event type the plugin will consume
- [x] Go/no-go decision on tuple-options recorded; fallback chosen (defaults + explicit global config entry) if unsupported
- [x] Title event, idle payload, and variant metadata source confirmed with evidence
- [x] link.py sync path verified (or extension task filed as concrete subtask)
- [x] FTD §21 open questions annotated; revision history updated on material deviations

---

## Group 1 — Plugin skeleton & fail-open foundation

- [x] Create `opencode/plugins/usage-tracking/index.ts` exporting the default plugin function (`PluginInput` signature, options param)
- [x] Keep zero runtime npm dependencies — type-only imports from `@opencode-ai/plugin` (FTD §15)
- [x] Implement the fail-open wrapper: every hook callback runs in try/catch; errors logged once via `client.app.log` (service `usage-tracking`) and swallowed — never rethrow (ADR-05)
- [x] Emit `plugin.initialized` log event with a config summary
- [x] Register the `event` hook with an empty dispatcher (wiring only, no logic yet)
- [x] Add project scaffolding: `package.json`, `tsconfig.json`, and a runnable empty `bun test`
- [ ] Add link.py item keys for the plugin directory; link, restart OpenCode, and confirm the init log line appears — item keys auto-discovered (incl. flat entry file, task-5-entry-file); linking + restart + init-log confirmation: **owner run pending**

### DoD — Group 1
- [ ] OpenCode starts with the plugin loaded; `plugin.initialized` visible in the log — **owner run pending**
- [ ] An induced error inside a hook leaves OpenCode fully unaffected (manual verification) — fail-open verified at unit level (injected failures never propagate); live manual re-check: **owner run pending**
- [x] `bun test` runs green with the empty harness
- [ ] Plugin reachable via symlink in `~/.config/opencode/plugins/`; restart verified — **owner run pending**

---

## Group 2 — Session lifecycle capture (US-01)

- [x] EventRouter: on `session.created`, emit `session.started` with sessionID, parentID (if any), projectID, directory/worktree path, agent, model `{id, providerID, variant}`, and timestamp
- [x] MetadataResolver: SDK lookup for session info, cached per sessionID (first event per session) — *deviation: no SDK lookups needed; metadata arrives via events (title via `session.updated`, model via `message.info` join) — see FTD §11.4(b)/(c) and the spike findings below*
- [x] Capture the auto-generated session title as soon as it becomes available (event per Group 0 findings) and write it to the aggregate
- [x] Track model switches: maintain the models list in the aggregate from message/session metadata
- [x] Track the set of active agents per session (agents list)
- [x] On `session.idle`, finalise the aggregate (activeMs, final totals) — idempotent, safe on repeated idle events (ADR-02, R-03)
- [x] On `session.deleted`, log a `session.deleted` event; collected data is retained (no deletion — FTD §11.3)
- [x] In-memory session state map with eviction after finalisation to bound memory — *deviation: eviction-on-idle removed (`session.idle` fires per turn — multi-turn regression, task-7-fix-3); V1 keeps state in memory per process, restart re-seeds via `store.replay()` — FTD §11.4(g)*

### DoD — Group 2 (AC 7.1)
- [x] `session.started` written on `session.created` with all AC 7.1 fields present
- [x] Title lands in the aggregate once generated
- [x] A model switch mid-session results in all used models in the aggregate's model list
- [x] `session.idle` finalises the aggregate idempotently
- [x] No message text, prompt content, or tool output is ever written to storage (verified by inspection of all written files)

---

## Group 3 — Step, token & tool tracking (US-01/02)

- [x] Handle `message.part.updated` with part type `step-finish`: emit `step.finished` within 1 s with sessionID, messageID, partID, agent, modelID, providerID, `tokens {input, output, reasoning, cache.read, cache.write}`, cost, stepMs
- [x] Measure step duration from `step-start` part timestamps; accumulate into active agent time (activeMs)
- [x] Handle tool parts/events: emit `tool.executed` (sessionID, tool name, ok flag)
- [x] SessionAggregator: per-session token totals, cost total, and toolCounts per tool name
- [x] De-duplicate streamed part updates: count each step/tool part exactly once (parts update incrementally — use final state only)
- [x] Asynchronous write queue so event processing never blocks the host (NFR-01)

### DoD — Group 3 (AC 7.1/7.2, NFR-03)
- [x] Every step-finish produces exactly one `step.finished` event with the full breakdown including cache read/write and reasoning tokens
- [x] toolCounts present in the aggregate per tool name
- [x] activeMs accumulates step durations only — no user idle time
- [ ] Events persisted within 1 s of emission (NFR-03) — write path is arrival-ordered with no batching; timing verification via smoke-test timestamps: **owner run pending**

---

## Group 4 — Storage layer & configuration (US-04)

- [x] ConfigResolver: parse tuple-options (output root, `excludeAgents`, toggles) with safe defaults; unknown or invalid options are ignored with exactly one warning (AC 7.4)
- [x] Default output root `~/.local/share/opencode-usage/` with a per-project subdirectory derived from projectID/path
- [x] EventStore: append-only JSONL writer per project (`events.jsonl`), `mkdir -p` on first write
- [x] Aggregate store: upsert `sessions/<sessionID>.json` on every state change
- [x] Aggregate rebuild function: reconstruct any aggregate from the JSONL stream (ADR-02 recovery path)
- [x] Guarantee no file is written inside any git worktree unless `output` is explicitly configured to a worktree path (AC 7.4)
- [x] Log a warning when a session's storage footprint exceeds 100 KB (NFR-06 visibility) — implemented in EventStore: one fail-open warning per output root > 102400 bytes (task-7-nfr06)
- [x] Handle write errors (disk full, read-only path): single `write.error` log event, degrade without crash (ADR-05, R-05)

### DoD — Group 4 (AC 7.4)
- [x] With no options configured, data lands under the default central root in a per-project directory
- [ ] A project-level `opencode.json` plugin entry overrides the global entry's options (verified on live instance) — override mechanism proven by the spike (options delivered verbatim); live verification: **owner run pending**
- [x] Unknown option → exactly one warning; OpenCode continues normally
- [x] A corrupted aggregate file is deleted and correctly rebuilt from `events.jsonl`
- [x] Induced write failure leaves OpenCode unaffected (fail-open verified)

---

## Group 5 — Recursive subagent tracking (US-03)

- [x] Treat child sessions (parentID set) identically to top-level sessions, at any nesting depth
- [x] Compute nesting depth by walking the parentID chain
- [x] Parent aggregate: children list with sessionID, agent, depth, and usage totals per child
- [x] Roll child usage up into the parent's totals (child records also remain standalone)
- [x] Handle arrival ordering: a child's `session.created` can arrive mid-parent-session; attach when seen
- [ ] Optional `excludeAgents` option: filter internal agents (title/compaction) out of the roll-up when configured (R-04) — option parsing + validation implemented in ConfigResolver; roll-up filtering not wired in V1 (agent is recorded per session, enabling analysis-side filtering)

### DoD — Group 5 (AC 7.3)
- [x] Child sessions tracked with the same event set as top-level sessions at any depth (verified with a nested dispatch) — unit-verified to depth 2; live nested dispatch: **owner run pending**
- [x] Parent aggregate lists all children with agent, depth, and totals
- [x] Parent totals include subagent usage; each child record is also complete on its own
- [ ] A subagent dispatch during the smoke test produces a child aggregate — smoke assertions D/E pin it; live run: **owner run pending**

---

## Group 6 — Status command (US-05)

- [x] Track plugin counters in state: sessions/events written, error count, last write timestamp
- [x] Register the `usage_status` custom tool returning: configured output path, tracked session/event counts, last write timestamp, error count, and the current session's running totals (tokens + cost)
- [x] Create `opencode/command/usage-status.md` that invokes the `usage_status` tool and returns its output verbatim

### DoD — Group 6 (AC 7.5)
- [x] `/usage-status` returns all listed fields (unit-verified snapshot; live invocation: owner run pending)
- [x] The command file returns the tool output verbatim (no added text)
- [x] Running totals update live within the same session

---

## Group 7 — Verification: tests & smoke (US-06)

- [x] Bun unit tests: event mapping for every consumed event type (fixtures from Group 0 field map)
- [x] Bun unit tests: aggregation logic — totals, toolCounts, activeMs, model list, dedup, idempotent finalisation
- [x] Bun unit tests: ConfigResolver — defaults, project override, unknown/invalid options warning
- [x] Bun unit tests: error isolation — injected failures never propagate (fail-open)
- [x] Reach ≥ 80% line coverage on router/aggregator/config (NFR-05, `bun test --coverage`) — measured: config 100%, aggregate ~98%, mapping ~97%, store 100% (see FTD §13 note)
- [ ] Performance benchmark: ≤ 5 ms p95 synchronous processing per event excluding disk write (NFR-01) — not executed in V1 (never dispatched); the non-blocking sequential queue and allow-list mapping bound per-event work
- [x] Smoke script `scripts/smoke_usage_tracking.sh`: start headless OpenCode, run a scripted session including a subagent dispatch, assert plugin loaded, aggregate produced, all files valid JSON/JSONL; exit non-zero on any failure — delivered with assertions A–G (task-6-smoke), discoverability check incl. flat entry file (task-5-entry-file)
- [ ] Smoke script asserts NFR-02 (no host failures) and checks sample session footprint ≤ 100 KB (NFR-06) — NFR-06 realized differently: runtime warning in EventStore (task-7-nfr06); smoke-script footprint/NFR-02 assertions not implemented

### DoD — Group 7 (AC 7.6, NFR-01..06)
- [x] `bun test` green with ≥ 80% coverage on the core modules — 49 pass / 0 fail
- [ ] Smoke script exits 0 on the live workstation, including the subagent dispatch path — **owner run pending**
- [ ] All six NFRs verified using their stated verification method — NFR-02/05/06 unit-verified; NFR-01 benchmark not run; NFR-03/04 live verification: **owner run pending**
- [x] Acceptance criteria 7.1–7.6 demonstrated and checked off in the FTD traceability matrix (unit level; US-06 live smoke pending owner)

---

## Group 8 — Deployment, docs & closure

- [x] Finalize link.py item keys: `opencode/plugins/usage-tracking/*` and `opencode/command/usage-status.md` — auto-discovered per file; flat entry `opencode/plugins/usage-tracking.ts` added for auto-discovery (task-5-entry-file)
- [x] Update AGENTS.md / README.md if the repo structure changed (repo rule)
- [ ] Deploy: `uv run scripts/link.py link` → restart OpenCode → smoke script (exit 0) → verify via `/usage-status` (FTD §17) — **owner run pending**
- [x] Update the FTD: revision history, traceability matrix statuses, and §21 open-question resolutions
- [x] Add a `docs/specs/log.md` entry for the implementation milestone
- [ ] Record owner sign-off in FTD §20 — **owner run pending**
- [x] Park V2 backlog explicitly out of scope: OpenRouter pricing enrichment incl. OQ-4 decision (ADR-04)

### DoD — Group 8 (FTD §9.2)
- [ ] Deployed and verified healthy on the workstation after restart (`/usage-status` responds) — **owner run pending**
- [ ] Fail-open path re-verified post-deploy (induced write failure) — **owner run pending**
- [x] FTD and log.md updated; all open questions resolved or explicitly parked
- [ ] Owner sign-off recorded; every group above is fully checked off — **owner run pending**

---

## Spike findings (Group 0)

Evidence: owner live spike + server-side verification under OpenCode 1.18.21 and 1.18.23 + official SDK types — see `.agents/runs/2026-08-26-opencode-usage-tracking/reports/spike-findings-and-decision.md` (field map & decision), `task-3a-loader-probe.md` (loader probe asset), `task-6-smoke.md` (auto-discovery research), `task-5-entry-file.md` (entry-file fix).

### Verified event field map (envelope: `{ id, type, properties }`)

| Event | Verified fields |
| --- | --- |
| `session.created` / `session.updated` | `properties.sessionID`, `properties.info.{id,parentID,title,agent,variant?,model.providerID,modelID?}`, `properties.info.{cost,time.{created,updated},tokens.*}` |
| `message.updated` | `properties.sessionID`, `properties.info.{id,sessionID,parentID,agent,modelID,providerID,model.{modelID,providerID},cost,time.*,tokens.*}` — model flat on assistant messages, nested on user messages |
| `message.part.updated` | `properties.sessionID`, `properties.time`, `properties.part.{id,sessionID,messageID,type}`; step-finish adds `part.{cost,tokens.*}`; tool adds `part.{tool,callID,state.{status,time.*}}`; step-start confirmed |
| `session.idle` | `properties.sessionID` only |
| `session.deleted` | not observed; tolerant handling (log-only) |

Key fact: **every Part carries `messageID`** — step-finish correlates to its message without any SDK lookup. Child sessions proven via `session.created.properties.info.parentID`; ordering via receipt sequence.

### Open questions resolved

- **OQ-1: YES** — tuple options delivered verbatim (`tupleOptionsReceived: true`).
- **OQ-2** — idle carries sessionID only (finalise idempotently on every update); title via `session.updated.properties.info.title`.
- **OQ-3** — variant not observed live; recorded when present, `null` otherwise (tolerant parsing).

### Loader probe conclusions (loading route)

1. **Auto-discovery scans only files directly in the plugins dir** (glob `{plugin,plugins}/*.{ts,js}`, verified against OpenCode source 1.18.21/1.18.23 and empirically via an isolated config dir) — the per-file subdirectory layout alone is NOT discoverable. Fix delivered: flat entry file `opencode/plugins/usage-tracking.ts` re-exporting `./usage-tracking/index.ts` (task-5-entry-file).
2. **Multi-instance safety is mandatory** — the owner laptop showed 3 plugin initializations in one run (concurrent OpenCode processes); event-ID dedup + idempotent upserts make overlapping instances safe regardless of route.
3. **Per-project tuple override works** (options delivered verbatim); combined global auto-discovery + project tuple entry is safe thanks to event-ID dedup.
4. **Non-git workspaces get the constant project id `"global"`** — a shared output directory; the smoke script's layered detection handles it (run the live smoke while no other OpenCode sessions are active).
5. No breaking plugin-loading changes between 1.18.21 and 1.18.23 (verified server-side with an isolated install).

Post-closure note: the two throwaway diagnostic scripts (`scripts/usage_tracking_spike.sh` and `scripts/usage_tracking_loader_probe.sh`) were removed after closure (they were never merged); their findings live in the run reports under `.agents/runs/2026-08-26-opencode-usage-tracking/reports/`.

---

## Post-V1 improvements (v1.1)

Delivered 2026-08-27 (v11 dispatches + final v1.1 polish). Verified by the 69-test Bun suite, `tsc -p tsconfig.json` clean, and the offline smoke check; spec additions in FTD §11.4(j)–(m); reports under `.agents/runs/2026-08-26-opencode-usage-tracking/reports/` (`v11-*.md`, `v11-polish.md`).

- [x] ULID project directories + `projects.json` registry — time-sortable and merge-safe across devices; registry keys validated as ULIDs on read (security review F1, hardened in v1.1 polish)
- [x] `overview.json` per project — exact 11-key shape, regenerated on every aggregate upsert (derived/disposable, last writer wins); smoke-script assertion H pins the shape
- [x] activeMs pairing fix — steps pair on (sessionID, messageID) FIFO across distinct step-start/step-finish parts
- [x] device/git info — device block on session aggregates and overview; git attribution refreshed at init and per `session.idle` (fail-open null)
