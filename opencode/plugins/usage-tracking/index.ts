/**
 * Plugin wiring for usage-tracking (OpenCode plugin entry).
 *
 * Composes the pipeline stages: `config` (resolve options) → `mapping`
 * (normalize bus events) → `aggregate` (session state + AC 7.3 rollup) →
 * `store` (ADR-02 JSONL + aggregates), and exposes the `usage_status` tool
 * backed by `status`.
 *
 * Core invariants:
 * - Fail-open (ADR-05): no error from any stage ever reaches the host — the
 *   event hook, write queue, and tool all swallow and log.
 * - Metadata-only (ADR-06): only the normalized records from `mapEvent` are
 *   processed; no message content, prompts, or tool outputs.
 * - Event-ID dedup: the live envelope id (fallback: record `eventID`) keeps
 *   re-delivered events from double-counting.
 * - Sequential writes: all store mutations run on one queue in arrival
 *   order; restart seeding is queued first so replayed state lands before
 *   any live event.
 */

import { basename, join } from "node:path";
import type { Plugin, PluginOptions, tool } from "@opencode-ai/plugin";
import { SessionAggregator } from "./aggregate";
import { resolveConfig } from "./config";
import { mapEvent, isInternalRecord, type UsageEventEnvelope } from "./mapping";
import { EventStore } from "./store";
import { StatusTracker } from "./status";

// The `tool` helper from "@opencode-ai/plugin" is an identity function over its
// input; per FTD §15 the plugin keeps zero runtime npm dependencies, so only
// its TYPE is imported and the definition below is typed through it.
type ToolDefinition = ReturnType<typeof tool>;

const SERVICE = "usage-tracking";
const DEFAULT_PROJECT_SEGMENT = "default";

type AppLogLevel = "debug" | "info" | "warn" | "error";

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readNonEmptyString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function errorClassKey(error: unknown): string {
  if (isPlainObject(error)) {
    const code = error.code;
    if (typeof code === "string" && code.length > 0) return code;
  }
  if (error instanceof Error) return error.name.length > 0 ? error.name : "Error";
  return typeof error;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function sanitizeSegment(value: string): string {
  // Filesystem-safe project segment: collapse invalid chars to "-", strip
  // runs and edges, cap at 64 chars, then re-strip (the cap can expose new
  // edge dashes). "." and ".." are rejected outright.
  const cleaned = value
    .replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 64)
    .replace(/^-+|-+$/g, "");
  if (cleaned === "" || cleaned === "." || cleaned === "..") return "";
  return cleaned;
}

/**
 * Derives the per-project subdirectory under the configured output root.
 *
 * Preference order: project.id → worktree → directory → project.name; any
 * path-like candidate is reduced to its basename, then sanitized. Falls back
 * to "default" when nothing yields a safe segment.
 *
 * @param input - The plugin's init input (project/worktree/directory fields
 *   are unvalidated `unknown` from OpenCode).
 */
function projectSubdirectory(input: {
  project?: { id?: unknown; name?: unknown };
  worktree?: unknown;
  directory?: unknown;
}): string {
  const candidates: Array<string | null> = [
    readNonEmptyString(input?.project?.id),
    readNonEmptyString(input?.worktree),
    readNonEmptyString(input?.directory),
    readNonEmptyString(input?.project?.name),
  ];
  for (const candidate of candidates) {
    if (candidate === null) continue;
    const base =
      candidate.includes("/") || candidate.includes("\\") ? basename(candidate) : candidate;
    const segment = sanitizeSegment(base);
    if (segment !== "") return segment;
  }
  return DEFAULT_PROJECT_SEGMENT;
}

// The SDK's static Event type has no `id`, but the live envelope carries one
// (verified spike); read it defensively.
function envelopeEventID(envelope: unknown): string | null {
  if (!isPlainObject(envelope)) return null;
  return readNonEmptyString(envelope.id);
}

  /**
   * The plugin factory. Runs once per OpenCode initialization.
   *
   * @param input - Plugin init input from OpenCode: `client` (SDK app
   *   client), `project`/`worktree`/`directory` (used for output scoping).
   * @param options - User-supplied plugin options; resolved by `resolveConfig`.
   * @returns Hooks: `event` (bus ingestion), `tool.usage_status`, and
   *   `dispose` (drains the write queue).
   */
  const plugin: Plugin = async (input, options) => {
  const client = input?.client;

  const appLog = async (level: AppLogLevel, message: string): Promise<void> => {
    try {
      await client?.app?.log?.({ body: { service: SERVICE, level, message } });
    } catch {}
  };

  // Error reporting with two dedup layers: the first error of any kind also
  // emits a one-time "plugin.degraded" marker, and each distinct error class
  // (code or Error.name) is logged at most once. Logging failures are
  // swallowed (fail-open, ADR-05).
  const loggedErrorClasses = new Set<string>();
  let degradedReported = false;

  const reportErrorClass = (key: string, message: string): void => {
    if (!degradedReported) {
      degradedReported = true;
      void appLog("error", `plugin.degraded (cause: ${message})`);
    }
    if (loggedErrorClasses.has(key)) return;
    loggedErrorClasses.add(key);
    void appLog("error", message);
  };

  const reportError = (error: unknown, context: string): void => {
    reportErrorClass(
      errorClassKey(error),
      `${context} failed (${errorMessage(error)}); swallowed (fail-open)`,
    );
  };

  const config = resolveConfig(options, (message) => {
    void appLog("warn", message);
  });

  const aggregator = new SessionAggregator();
  const outputPath = join(config.output, projectSubdirectory(input));
  const tracker = new StatusTracker(outputPath, aggregator);
  const store = new EventStore(outputPath, (message) => {
    tracker.recordError();
    reportErrorClass(`store:${message}`, message);
  });

  // Simple sequential async queue: every record's apply/append/upsert runs in
  // arrival order, never rejects, and flushes promptly (no batching).
  let writeQueue: Promise<void> = Promise.resolve();

  const enqueueWrite = (work: () => Promise<void>): void => {
    writeQueue = writeQueue.then(async () => {
      try {
        await work();
      } catch (error) {
        tracker.recordError();
        reportErrorClass(
          errorClassKey(error),
          `queued write failed (${errorMessage(error)}); swallowed (fail-open)`,
        );
      }
    });
  };

  // Restart seeding (first in the queue, so it lands before any live event):
  // replay this project's persisted records through the aggregator so a
  // restart mid-session resumes from the FULL prior totals — the next upsert
  // then persists prior + new data instead of regressing the aggregate.
  // Internal records (message.info, step.started) were never persisted, so
  // replay covers persisted types only; the aggregator tolerates the missing
  // step.started pairing (unmatched finishes contribute 0 activeMs).
  enqueueWrite(async () => {
    for (const record of await store.replay()) {
      aggregator.apply(record);
    }
  });

  /**
   * Processes one normalized record on the write queue.
   *
   * Order matters: aggregate first (so the snapshot below includes this
   * event), then persist the event (unless internal), then upsert the
   * session's finalized aggregate. `session.deleted` stops aggregate updates
   * for that session; `session.idle` additionally logs the finalized totals.
   *
   * @param record - Normalized record from `mapEvent`.
   * @param sourceEventID - Live envelope id (primary dedup key), or null.
   * @param sessionID - The record's session id (guaranteed non-empty).
   */
  const processRecord = async (
    record: Record<string, unknown>,
    sourceEventID: string | null,
    sessionID: string,
  ): Promise<void> => {
    aggregator.apply(record, sourceEventID);
    // Internal records (message.info, step.started) feed the live aggregator
    // but are derivable from the persisted stream — never append them.
    if (!isInternalRecord(record)) {
      await store.append(record);
      tracker.recordEventWritten();
    }
    const recordType = typeof record.type === "string" ? record.type : null;
    if (recordType === "session.deleted") return;
    const aggregate = aggregator.finalize()[sessionID];
    if (aggregate === undefined) return;
    await store.upsertAggregate(sessionID, aggregate);
    tracker.recordSessionWritten(sessionID);
    if (recordType === "session.idle") {
      void appLog(
        "info",
        `session.finalized (sessionID: ${sessionID}, tokens: ${JSON.stringify(aggregate.tokens)}, cost: ${aggregate.cost})`,
      );
      // Idle finalizes the turn's totals and persists them, but the session
      // itself lives on: session.idle fires after EVERY turn (busy→idle per
      // turn), so the in-memory state must be retained — evicting here would
      // make turn 2+ rebuild from zero and overwrite sessions/<id>.json with
      // partial totals, dropping child tokens from the parent rollup. V1
      // accepts unbounded in-memory retention per FTD (restart re-seeds).
    }
  };

  /**
   * Event-bus hook: the single ingestion point for all OpenCode events.
   *
   * Maps, dedups by session identity, and enqueues processing; mapping or
   * enqueue failures are counted and logged (fail-open, ADR-05) — never
   * rethrown to the host.
   *
   * @param hookInput - OpenCode event hook input: `{event}` is the live bus
   *   envelope (`{id, type, properties}`; see `UsageEventEnvelope`).
   */
  const handleEvent = async (hookInput: {
    event?: UsageEventEnvelope | null | undefined;
  }): Promise<void> => {
    try {
      const envelope = hookInput?.event;
      const record = mapEvent(envelope);
      if (!isPlainObject(record)) return;
      const sessionID = readNonEmptyString(record.sessionID);
      if (sessionID === null) return;
      const sourceEventID = envelopeEventID(envelope);
      enqueueWrite(() => processRecord(record, sourceEventID, sessionID));
    } catch (error) {
      tracker.recordError();
      reportError(error, "event hook");
    }
  };

  // Read-only health probe: returns the tracker snapshot (write counters +
  // current session rollup) as pretty JSON; failures return an error object
  // instead of throwing (fail-open, ADR-05).
  const usageStatusTool: ToolDefinition = {
    description:
      "Show usage-tracking write health: output path, sessions and events written, last write timestamp, error count, and the current session's running token and cost totals. Read-only, takes no arguments.",
    args: {},
    execute: async (_args, context) => {
      try {
        const sessionID = readNonEmptyString(context?.sessionID);
        return JSON.stringify(tracker.snapshot(sessionID), null, 2);
      } catch (error) {
        tracker.recordError();
        reportError(error, "usage_status tool");
        return JSON.stringify({ error: "usage_status failed", detail: errorMessage(error) }, null, 2);
      }
    },
  };

  void appLog("info", `plugin.initialized (output: ${outputPath})`);

  return {
    event: handleEvent,
    tool: { usage_status: usageStatusTool },
    dispose: async () => {
      try {
        await writeQueue;
      } catch {}
    },
  };
};

export default plugin;
