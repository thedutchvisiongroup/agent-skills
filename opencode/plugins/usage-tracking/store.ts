/**
 * Filesystem persistence for the usage-tracking plugin.
 *
 * Fourth stage of the pipeline (config → mapping → aggregate → store, wired
 * by `index.ts`): implements ADR-02's two-layer output — an append-only
 * `events.jsonl` event stream plus derived per-session aggregate files in
 * `sessions/` — all under a project-scoped root.
 *
 * Fail-open (ADR-05): every method swallows filesystem errors after logging
 * them once per error class; a failing store never breaks the host. The
 * JSONL stream is the source of truth — a lost/corrupt aggregate is
 * recoverable via `rebuild()` (ADR-02).
 */

import { appendFile, mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { SessionAggregator, type SessionAggregate } from "./aggregate";
import type { UsageRecord } from "./mapping";

/** Receives one message per (deduplicated) store error; must never throw. */
export type StoreErrorLogger = (message: string) => void;

const EVENTS_FILENAME = "events.jsonl";
const SESSIONS_DIRNAME = "sessions";
// NFR-06 visibility: the per-session storage budget (events.jsonl growth +
// aggregate files) is 100 KB; crossing it logs one warning, never blocks.
const STORAGE_WARNING_BYTES = 102_400;

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Guards against path traversal: sessionIDs become filenames, so no separators/NUL and no `.`/`..`. */
function isSafeFilename(value: string): boolean {
  if (value.length === 0 || value === "." || value === "..") return false;
  return !value.includes("/") && !value.includes("\\") && !value.includes("\0");
}

function errorCode(error: unknown): string | null {
  if (typeof error === "object" && error !== null && "code" in error) {
    const code = (error as { code?: unknown }).code;
    if (typeof code === "string" && code.length > 0) return code;
  }
  return null;
}

function errorKeySuffix(error: unknown): string {
  return errorCode(error) ?? (error instanceof Error ? "error" : "unknown");
}

function errorMessage(error: unknown): string {
  const code = errorCode(error);
  const message = error instanceof Error ? error.message : String(error);
  return code === null ? message : `${code}: ${message}`;
}

/**
 * ADR-02 two-layer store: append-only JSONL events + derived aggregates.
 *
 * All writes funnel through `ensureDir` + try/catch; errors are reported once
 * per distinct error key (the caller's logger drives the plugin's degraded
 * marker), and ENOENT invalidates the directory cache so the next write
 * retries `mkdir`.
 */
export class EventStore {
  private readonly root: string;
  private readonly logger?: StoreErrorLogger;
  private readonly ensuredDirs = new Set<string>();
  private readonly reportedKeys = new Set<string>();
  private footprintWarned = false;

  /**
   * @param root - Absolute, project-scoped output root (config output +
   *     project subdirectory, built by `index.ts`).
   * @param logger - Optional error sink; invoked once per distinct error key.
   */
  constructor(root: string, logger?: StoreErrorLogger) {
    this.root = root;
    this.logger = logger;
  }

  /**
   * Appends one record as a JSON line to `events.jsonl` (ADR-02 layer 1).
   *
   * Side effects: recursive `mkdir` of the root on first write, an append to
   * the JSONL file, and a footprint check (NFR-06). On failure the record is
   * dropped and the error reported (fail-open, ADR-05).
   *
   * @param record - Persisted-type record from `mapEvent`; internal record
   *     types must be filtered by the caller (see `isInternalRecord`).
   *     Non-plain-object input is a silent no-op.
   */
  async append(record: UsageRecord | Record<string, unknown> | null | undefined): Promise<void> {
    if (!isPlainObject(record)) return;
    const file = join(this.root, EVENTS_FILENAME);
    try {
      const line = JSON.stringify(record);
      if (typeof line !== "string") return;
      if (!(await this.ensureDir(this.root))) return;
      await appendFile(file, `${line}\n`, "utf8");
      await this.checkFootprint();
    } catch (error) {
      this.report(
        `append:${errorKeySuffix(error)}`,
        `append to ${file} failed (${errorMessage(error)}); event dropped (fail-open)`,
      );
      // The root vanished after being ensured once (e.g. removed by the
      // user): invalidate the cache so the next write retries mkdir.
      if (errorCode(error) === "ENOENT") this.ensuredDirs.delete(this.root);
    }
  }

  /**
   * Upserts one session's aggregate to `sessions/<sessionID>.json`
   * (ADR-02 layer 2), pretty-printed with a trailing newline.
   *
   * Idempotent whole-file replacement: the aggregate always reflects the
   * session's full totals, so re-writing it after every event is safe.
   * Unsafe sessionIDs (separators, `.`/`..`) are rejected with one warning
   * (path-traversal guard). Side effects: mkdir of `sessions/`, the write,
   * and a footprint check (NFR-06). Failures skip the update (fail-open).
   *
   * @param sessionID - Session id used verbatim as the filename.
   * @param aggregate - `SessionAggregate` from `finalize()` (loose shape
   *     accepted for tests).
   */
  async upsertAggregate(
    sessionID: string,
    aggregate: SessionAggregate | Record<string, unknown>,
  ): Promise<void> {
    if (!isSafeFilename(sessionID)) {
      this.report(
        "upsert:unsafe-sessionID",
        `aggregate upsert rejected for unsafe sessionID ${JSON.stringify(sessionID)}; update skipped (fail-open)`,
      );
      return;
    }
    const file = join(this.root, SESSIONS_DIRNAME, `${sessionID}.json`);
    const dir = join(this.root, SESSIONS_DIRNAME);
    try {
      if (!(await this.ensureDir(dir))) return;
      await writeFile(file, `${JSON.stringify(aggregate, null, 2)}\n`, "utf8");
      await this.checkFootprint();
    } catch (error) {
      this.report(
        `upsert:${errorKeySuffix(error)}`,
        `aggregate upsert to ${file} failed (${errorMessage(error)}); update skipped (fail-open)`,
      );
      if (errorCode(error) === "ENOENT") this.ensuredDirs.delete(dir);
    }
  }

  /**
   * Rebuilds all aggregates from scratch by replaying `events.jsonl` through
   * a fresh `SessionAggregator` — the designed recovery path when derived
   * aggregate files are lost or corrupted (ADR-02).
   *
   * Malformed lines are skipped and reported once; a missing JSONL yields an
   * empty result. Never throws (fail-open, ADR-05): on read failure it
   * returns `{}` after logging.
   *
   * @returns Null-prototype map of sessionID → `SessionAggregate` (same shape
   *     as `finalize()`).
   */
  async rebuild(): Promise<Record<string, SessionAggregate>> {
    const file = join(this.root, EVENTS_FILENAME);
    try {
      let content: string;
      try {
        content = await readFile(file, "utf8");
      } catch (error) {
        if (errorCode(error) === "ENOENT") return {};
        throw error;
      }
      const aggregator = new SessionAggregator();
      let malformed = 0;
      for (const line of content.split("\n")) {
        if (line.trim() === "") continue;
        try {
          aggregator.apply(JSON.parse(line));
        } catch {
          malformed += 1;
        }
      }
      if (malformed > 0) {
        this.report(
          "rebuild:malformed",
          `rebuild of ${file} skipped ${malformed} malformed line(s)`,
        );
      }
      return aggregator.finalize();
    } catch (error) {
      this.report(
        `rebuild:${errorKeySuffix(error)}`,
        `rebuild of ${file} failed (${errorMessage(error)}); returning empty aggregates (fail-open)`,
      );
      return {};
    }
  }

  // Restart-seeding seam: yields the persisted records in file order so a
  // fresh plugin instance can rebuild its live aggregator state. The store
  // root is already project-scoped, so no project argument is needed.
  // Malformed lines are skipped (fail-open, consistent with rebuild()).
  /**
   * Reads back the persisted event stream for restart seeding.
   *
   * @returns Records in file (append) order — the same order they were
   *     applied live, so replaying them reproduces the aggregator state.
   *     Missing `events.jsonl` yields `[]`; malformed lines are skipped with
   *     one report; read failures yield `[]` (fail-open, ADR-05).
   */
  async replay(): Promise<Array<Record<string, unknown>>> {
    const file = join(this.root, EVENTS_FILENAME);
    try {
      let content: string;
      try {
        content = await readFile(file, "utf8");
      } catch (error) {
        if (errorCode(error) === "ENOENT") return [];
        throw error;
      }
      const records: Array<Record<string, unknown>> = [];
      let malformed = 0;
      for (const line of content.split("\n")) {
        if (line.trim() === "") continue;
        try {
          const parsed: unknown = JSON.parse(line);
          if (isPlainObject(parsed)) {
            records.push(parsed);
          } else {
            malformed += 1;
          }
        } catch {
          malformed += 1;
        }
      }
      if (malformed > 0) {
        this.report(
          "replay:malformed",
          `replay of ${file} skipped ${malformed} malformed line(s)`,
        );
      }
      return records;
    } catch (error) {
      this.report(
        `replay:${errorKeySuffix(error)}`,
        `replay of ${file} failed (${errorMessage(error)}); returning empty stream (fail-open)`,
      );
      return [];
    }
  }

  // NFR-06 visibility: measures the root's real on-disk footprint (stat, so
  // pre-existing data from earlier runs counts too) and warns once per store
  // instance when it exceeds the 100 KB budget. Never throws (fail-open):
  // measurement failures are silently skipped.
  private async checkFootprint(): Promise<void> {
    if (this.footprintWarned) return;
    try {
      let total = 0;
      try {
        total += (await stat(join(this.root, EVENTS_FILENAME))).size;
      } catch {
        // No events.jsonl (yet) — contributes zero.
      }
      try {
        const dir = join(this.root, SESSIONS_DIRNAME);
        for (const entry of await readdir(dir)) {
          try {
            total += (await stat(join(dir, entry))).size;
          } catch {}
        }
      } catch {
        // No sessions/ directory (yet) — contributes zero.
      }
      if (total > STORAGE_WARNING_BYTES) {
        this.footprintWarned = true;
        this.report(
          "footprint",
          `storage footprint of ${this.root} exceeds the 100 KB budget (${total} bytes > ${STORAGE_WARNING_BYTES} bytes, NFR-06); writes continue (fail-open)`,
        );
      }
    } catch {}
  }

  /** Memoized recursive mkdir; a successful ensure is cached for the store's lifetime. */
  private async ensureDir(dir: string): Promise<boolean> {
    if (this.ensuredDirs.has(dir)) return true;
    try {
      await mkdir(dir, { recursive: true });
      this.ensuredDirs.add(dir);
      return true;
    } catch (error) {
      this.report(
        `mkdir:${errorKeySuffix(error)}`,
        `mkdir ${dir} failed (${errorMessage(error)}); writes are skipped (fail-open)`,
      );
      return false;
    }
  }

  /** Logs a message once per distinct key (error class + operation), so repeated failures don't flood the log. */
  private report(key: string, message: string): void {
    if (this.reportedKeys.has(key)) return;
    this.reportedKeys.add(key);
    try {
      this.logger?.(`usage-tracking: ${message}`);
    } catch {}
  }
}
