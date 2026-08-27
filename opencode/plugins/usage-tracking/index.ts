/**
 * Plugin wiring for usage-tracking (OpenCode plugin entry).
 *
 * Composes the pipeline stages: `config` (resolve options) → `projectdir`
 * (deterministic per-project directory) → `mapping` (normalize bus events) →
 * `aggregate` (session state + AC 7.3 rollup) → `store` (ADR-02 JSONL +
 * aggregates) + `overview` (project-level snapshot), and exposes the
 * `usage_status` tool backed by `status`.
 *
 * Core invariants:
 * - Fail-open (ADR-05): no error from any stage ever reaches the host — the
 *   event hook, write queue, tool, and every init-time probe (device info,
 *   git info, origin remote) swallow and log.
 * - Metadata-only (ADR-06): only the normalized records from `mapEvent` are
 *   processed; no message content, prompts, or tool outputs.
 * - Event-ID dedup: the live envelope id (fallback: record `eventID`) keeps
 *   re-delivered events from double-counting.
 * - Sequential writes: all store mutations run on one queue in arrival
 *   order; restart seeding is queued first so replayed state lands before
 *   any live event.
 */

import { readFile } from "node:fs/promises";
import { hostname, release } from "node:os";
import { join } from "node:path";
import type { Plugin, PluginInput, PluginOptions, tool } from "@opencode-ai/plugin";
import { SessionAggregator, type DeviceInfo } from "./aggregate";
import { resolveConfig } from "./config";
import { mapEvent, isInternalRecord, type UsageEventEnvelope } from "./mapping";
import { writeOverview, type OverviewDeviceInfo, type OverviewGitInfo } from "./overview";
import { projectDirectoryName } from "./projectdir";
import { EventStore } from "./store";
import { StatusTracker } from "./status";

// The `tool` helper from "@opencode-ai/plugin" is an identity function over its
// input; per FTD §15 the plugin keeps zero runtime npm dependencies, so only
// its TYPE is imported and the definition below is typed through it.
type ToolDefinition = ReturnType<typeof tool>;

const SERVICE = "usage-tracking";
const OS_RELEASE_FILE = "/etc/os-release";

type AppLogLevel = "debug" | "info" | "warn" | "error";

// The host-provided Bun shell (PluginInput["$"]); absent in stripped-down
// inputs (tests, offline harnesses), so every shell probe fails open to null.
type PluginShell = PluginInput["$"];

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

// The SDK's static Event type has no `id`, but the live envelope carries one
// (verified spike); read it defensively.
function envelopeEventID(envelope: unknown): string | null {
  if (!isPlainObject(envelope)) return null;
  return readNonEmptyString(envelope.id);
}

/** Reads PRETTY_NAME from /etc/os-release; missing/unparsable → null (fail-open). */
async function readOsPrettyName(): Promise<string | null> {
  try {
    const content = await readFile(OS_RELEASE_FILE, "utf8");
    for (const line of content.split("\n")) {
      const separator = line.indexOf("=");
      if (separator === -1) continue;
      if (line.slice(0, separator).trim() !== "PRETTY_NAME") continue;
      let value = line.slice(separator + 1).trim();
      if (value.length >= 2 && value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1);
      }
      return value.length > 0 ? value : null;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * One-time `opencode --version` probe through the host shell; absent shell,
 * command failure, or empty output → null (fail-open).
 */
async function readOpencodeVersion(shell: PluginShell | null | undefined): Promise<string | null> {
  if (typeof shell !== "function") return null;
  try {
    const output = await shell`opencode --version`.text();
    const trimmed = typeof output === "string" ? output.trim() : "";
    return trimmed.length > 0 ? trimmed : null;
  } catch {
    return null;
  }
}

/**
 * Collects the git attribution of the project directory via the host shell:
 * branch (`rev-parse --abbrev-ref HEAD`), latest tag (`describe --tags
 * --abbrev=0`, null when untagged), and the head commit (`log -1` with a
 * \x1f-separated format). Any failure degrades to null pieces or a null
 * result — never a throw (fail-open, ADR-05).
 *
 * @param shell - Host Bun shell; absent → null.
 * @param input - Plugin init input; the probed directory is the worktree,
 *   falling back to the directory.
 */
async function collectGitInfo(
  shell: PluginShell | null | undefined,
  input: { worktree?: unknown; directory?: unknown } | null | undefined,
): Promise<OverviewGitInfo | null> {
  if (typeof shell !== "function") return null;
  const fields = isPlainObject(input) ? input : {};
  const dir = readNonEmptyString(fields.worktree) ?? readNonEmptyString(fields.directory);
  if (dir === null) return null;
  try {
    const branchOutput = await shell`git -C ${dir} rev-parse --abbrev-ref HEAD`.text();
    const branch = typeof branchOutput === "string" ? branchOutput.trim() : "";
    if (branch.length === 0) return null;
    let tag: string | null = null;
    try {
      const tagOutput = await shell`git -C ${dir} describe --tags --abbrev=0`.text();
      const trimmed = typeof tagOutput === "string" ? tagOutput.trim() : "";
      tag = trimmed.length > 0 ? trimmed : null;
    } catch {
      tag = null;
    }
    let lastCommit: OverviewGitInfo["lastCommit"] = null;
    try {
      const logOutput = await shell`git -C ${dir} log -1 --pretty=format:%H%x1f%s%x1f%an%x1f%aI`.text();
      const parts = typeof logOutput === "string" ? logOutput.split("\x1f") : [];
      if (parts.length === 4) {
        const [hash, subject, author, date] = parts.map((part) => part.trim());
        if (hash.length > 0 && date.length > 0) {
          lastCommit = { hash, subject, author, date };
        }
      }
    } catch {
      lastCommit = null;
    }
    return { branch, tag, lastCommit };
  } catch {
    return null;
  }
}

/**
 * One-time `git remote get-url origin` probe through the host shell, feeding
 * the project-directory hash: the trimmed URL on success; absent shell,
 * command failure, or empty output → null (fail-open), which makes the hash
 * fall back to the path identity inside `projectDirectoryName`.
 *
 * @param shell - Host Bun shell; absent → null.
 * @param input - Plugin init input; the probed directory is the worktree,
 *   falling back to the directory.
 */
async function readGitRemote(
  shell: PluginShell | null | undefined,
  input: { worktree?: unknown; directory?: unknown } | null | undefined,
): Promise<string | null> {
  if (typeof shell !== "function") return null;
  const fields = isPlainObject(input) ? input : {};
  const dir = readNonEmptyString(fields.worktree) ?? readNonEmptyString(fields.directory);
  if (dir === null) return null;
  try {
    const output = await shell`git -C ${dir} remote get-url origin`.text();
    const trimmed = typeof output === "string" ? output.trim() : "";
    return trimmed.length > 0 ? trimmed : null;
  } catch {
    return null;
  }
}

/**
 * The plugin factory. Runs once per OpenCode initialization.
 *
 * Init probes (all fail-open): device info (hostname, /etc/os-release
 * PRETTY_NAME, kernel release, one-time `opencode --version` via the host
 * shell), the origin remote (one-time, for the deterministic project
 * subdirectory), and the project's git attribution. The git info is
 * refreshed on every `session.idle` so the overview tracks branch switches;
 * the latest collected value is cached.
 *
 * @param input - Plugin init input from OpenCode: `client` (SDK app client),
 *   `project`/`worktree`/`directory` (used for output scoping and git
 *   probing), `$` (host Bun shell).
 * @param options - User-supplied plugin options; resolved by `resolveConfig`.
 * @returns Hooks: `event` (bus ingestion), `tool.usage_status`, and
 *   `dispose` (drains the write queue).
 */
const plugin: Plugin = async (input, options) => {
  const client = input?.client;
  const shell = input?.$;

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

  // Device info, once at init (V11): every field fails open. The full block
  // feeds overview.json; the aggregator's per-aggregate block is exactly
  // {name, opencodeVersion} and only when the version probe succeeded.
  const deviceName = hostname();
  const deviceOS = await readOsPrettyName();
  const deviceOSVersion = release();
  const deviceOpencodeVersion = await readOpencodeVersion(shell);
  const deviceInfo: OverviewDeviceInfo = {
    name: deviceName.length > 0 ? deviceName : null,
    os: deviceOS,
    osVersion: deviceOSVersion.length > 0 ? deviceOSVersion : null,
    opencodeVersion: deviceOpencodeVersion,
  };
  const aggregatorDevice: DeviceInfo | null =
    deviceInfo.name !== null && deviceOpencodeVersion !== null
      ? { name: deviceName, opencodeVersion: deviceOpencodeVersion }
      : null;

  const aggregator = new SessionAggregator(aggregatorDevice);

  // Per-project output subdirectory (V12): a deterministic hash — hostname
  // (os.hostname(); empty maps to "unknown" inside projectDirectoryName,
  // fail-open) salted with the origin remote (probed once at init; falls
  // back to the resolved path identity inside the hash). No registry: the
  // same project lands in the same subdirectory under any output root. A
  // null result (no usable path identity at all) fails open to "default".
  const originRemote = await readGitRemote(shell, input);
  const projectSubdir =
    projectDirectoryName({
      worktree: input?.worktree,
      directory: input?.directory,
      remote: originRemote,
      hostname: deviceName,
    }) ?? "default";
  const outputPath = join(config.output, projectSubdir);

  // Git attribution: probed at init and refreshed on every session.idle; the
  // latest collected value is cached for the next overview write.
  let gitInfo: OverviewGitInfo | null = await collectGitInfo(shell, input);

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
   * session's finalized aggregate, then regenerate the project overview from
   * the in-memory aggregates. `session.deleted` stops aggregate updates for
   * that session (append-only marker); `session.idle` additionally refreshes
   * the cached git info and logs the finalized totals.
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
    const aggregates = aggregator.finalize();
    const aggregate = aggregates[sessionID];
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
      // The idle boundary is also the git refresh point: the next overview
      // below picks up the (fail-open) refreshed attribution.
      gitInfo = await collectGitInfo(shell, input);
    }
    await writeOverview(outputPath, aggregates, deviceInfo, gitInfo, (message) => {
      tracker.recordError();
      reportErrorClass(`overview:${message}`, message);
    });
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
