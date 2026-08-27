/**
 * Project-level overview generation for the usage-tracking plugin.
 *
 * Companion to `store.ts`: while the store persists per-session aggregates
 * (`sessions/<id>.json`) and the append-only event stream, this module derives
 * the single project-level `<projectDir>/overview.json` snapshot (V11) —
 * summed root-session totals, the union of models used, and the device/git
 * attribution collected by `index.ts` at init/refresh time.
 *
 * Key invariants:
 * - Exact shape: exactly the 11 dispatch keys, nothing more.
 * - Root-only sums: a child's own totals are already inside its parent's
 *   AC 7.3 rollup, so summing children too would double-count. A session
 *   whose parentID is absent from the aggregates (orphan) counts as a root
 *   so its totals are never lost. `sessions` and the `modelsUsed` union
 *   cover ALL aggregates (a set union cannot double-count).
 * - Atomic regeneration: every call fully replaces the previous file via
 *   temp-file + rename, leaving no temp leftovers.
 * - Fail-open (ADR-05): any failure (including an invalid projectDir) is
 *   reported once to the optional logger and swallowed — never thrown.
 *
 * Pure and testable — no OpenCode imports; the only I/O is `node:fs/promises`
 * plus `generateULID` for temp-file names.
 */

import { mkdir, rename, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { generateULID } from "./ulid";
import type { SessionModel, SessionTokens } from "./aggregate";

const OVERVIEW_FILENAME = "overview.json";

/** Receives one message per failed overview write; must never throw. */
export type OverviewLogger = (message: string) => void;

/** Overview-level device attribution (os fields are overview-only, V11). */
export type OverviewDeviceInfo = {
  name: string | null;
  os: string | null;
  osVersion: string | null;
  opencodeVersion: string | null;
};

/** Head commit of the project's git worktree, as reported by `git log -1`. */
export type OverviewCommitInfo = {
  hash: string;
  subject: string;
  author: string;
  date: string;
};

/** Git attribution of the project directory; individual fields fail open to null. */
export type OverviewGitInfo = {
  branch: string;
  tag: string | null;
  lastCommit: OverviewCommitInfo | null;
};

/** The exact shape persisted as `<projectDir>/overview.json`. */
export type ProjectOverview = {
  generatedAt: string;
  sessions: number;
  modelsUsed: SessionModel[];
  tokens: SessionTokens;
  cost: number;
  toolCounts: Record<string, number>;
  activeMs: number;
  directory: string | null;
  git: OverviewGitInfo | null;
  device: OverviewDeviceInfo | null;
  projectDirectory: string;
};

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function readCounter(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function errorMessage(error: unknown): string {
  const code =
    isPlainObject(error) && typeof error.code === "string" ? error.code : null;
  const message = error instanceof Error ? error.message : String(error);
  return code === null ? message : `${code}: ${message}`;
}

// Null-prototype record: hostile keys like "__proto__" in aggregate
// toolCounts land as own properties instead of hitting Object.prototype's
// setter (prototype-pollution guard, cf. aggregate.ts / ulid.ts).
function safeRecord<T>(): Record<string, T> {
  return Object.create(null);
}

/** Accepts any plain object; anything else (incl. null) → null. */
function normalizeDeviceInfo(value: unknown): OverviewDeviceInfo | null {
  if (!isPlainObject(value)) return null;
  return {
    name: readString(value.name),
    os: readString(value.os),
    osVersion: readString(value.osVersion),
    opencodeVersion: readString(value.opencodeVersion),
  };
}

/**
 * Accepts a `{branch, tag, lastCommit}` with a non-empty branch; a missing
 * branch (or a non-object) → null. `tag`/`lastCommit` pass through as null;
 * `lastCommit` requires a non-empty hash and date (subject/author degrade to
 * empty strings) so a truncated parse never reports a broken commit.
 */
function normalizeGitInfo(value: unknown): OverviewGitInfo | null {
  if (!isPlainObject(value)) return null;
  const branch = readString(value.branch);
  if (branch === null) return null;
  let lastCommit: OverviewCommitInfo | null = null;
  if (isPlainObject(value.lastCommit)) {
    const hash = readString(value.lastCommit.hash);
    const date = readString(value.lastCommit.date);
    if (hash !== null && date !== null) {
      lastCommit = {
        hash,
        subject: readString(value.lastCommit.subject) ?? "",
        author: readString(value.lastCommit.author) ?? "",
        date,
      };
    }
  }
  return { branch, tag: readString(value.tag), lastCommit };
}

/**
 * Writes `<projectDir>/overview.json` — the project-level usage snapshot.
 *
 * Regeneration is a full atomic replacement: a temp file in the same
 * directory is renamed over the target, so readers never observe a torn
 * file and repeated calls never merge or append. Root sessions (no parent,
 * or a parentID absent from the aggregates) contribute the summed
 * tokens/cost/toolCounts/activeMs; every aggregate contributes to `sessions`
 * and the `modelsUsed` union (deduplicated by model id, first occurrence
 * wins). `directory` is the sessions' working directory (first non-null);
 * `projectDirectory` is the directory this file is written into.
 *
 * Fail-open (ADR-05): any error is reported once to the optional logger and
 * swallowed — this function never throws.
 *
 * @param projectDirPath - Project-scoped output directory (the ULID
 *   subdirectory resolved by `resolveProjectDirectory`).
 * @param aggregates - Finalize()-shaped map of sessionID → session aggregate
 *   (in-memory or replayed); non-object entries are skipped.
 * @param deviceInfo - Overview-level device block, or null.
 * @param gitInfo - Git attribution of the project directory, or null.
 * @param logger - Optional error sink; invoked at most once per call.
 */
export async function writeOverview(
  projectDirPath: string,
  aggregates: Record<string, unknown> | null | undefined,
  deviceInfo: OverviewDeviceInfo | Record<string, unknown> | null | undefined,
  gitInfo: OverviewGitInfo | Record<string, unknown> | null | undefined,
  logger?: OverviewLogger,
): Promise<void> {
  try {
    if (typeof projectDirPath !== "string" || projectDirPath.length === 0) {
      throw new Error("projectDirPath must be a non-empty string");
    }

    // Index the valid aggregate entries once: sessions/models/directory cover
    // ALL of them, the summed metrics only the roots. Keys are session ids
    // (finalize()-shaped Record<sessionID, …>).
    const entries: Array<Record<string, unknown>> = [];
    const knownIDs = new Set<string>();
    if (isPlainObject(aggregates)) {
      for (const key of Object.keys(aggregates)) {
        const fields = aggregates[key];
        if (!isPlainObject(fields)) continue;
        entries.push(fields);
        knownIDs.add(key);
      }
    }

    let sessions = 0;
    const tokens: SessionTokens = {
      input: 0,
      output: 0,
      reasoning: 0,
      cacheRead: 0,
      cacheWrite: 0,
    };
    let cost = 0;
    let activeMs = 0;
    const toolCounts = safeRecord<number>();
    const modelsUsed: SessionModel[] = [];
    const seenModelIDs = new Set<string>();
    let directory: string | null = null;

    for (const fields of entries) {
      sessions += 1;
      if (directory === null) directory = readString(fields.directory);
      if (Array.isArray(fields.models)) {
        for (const model of fields.models) {
          if (!isPlainObject(model)) continue;
          const id = readString(model.id);
          if (id === null || seenModelIDs.has(id)) continue;
          seenModelIDs.add(id);
          modelsUsed.push({
            id,
            provider: readString(model.provider),
            variant: readString(model.variant),
          });
        }
      }
      // Root-only sums: a live parent link means this session's own totals
      // are already inside the parent's AC 7.3 rollup. Orphans (parentID
      // absent from the aggregates) count as roots.
      const parentID = readString(fields.parentID);
      if (parentID !== null && knownIDs.has(parentID)) continue;
      const tokenFields = isPlainObject(fields.tokens) ? fields.tokens : {};
      tokens.input += readCounter(tokenFields.input);
      tokens.output += readCounter(tokenFields.output);
      tokens.reasoning += readCounter(tokenFields.reasoning);
      tokens.cacheRead += readCounter(tokenFields.cacheRead);
      tokens.cacheWrite += readCounter(tokenFields.cacheWrite);
      cost += readCounter(fields.cost);
      activeMs += readCounter(fields.activeMs);
      if (isPlainObject(fields.toolCounts)) {
        for (const tool of Object.keys(fields.toolCounts)) {
          toolCounts[tool] = (toolCounts[tool] ?? 0) + readCounter(fields.toolCounts[tool]);
        }
      }
    }

    const overview: ProjectOverview = {
      generatedAt: new Date().toISOString(),
      sessions,
      modelsUsed,
      tokens,
      cost,
      toolCounts,
      activeMs,
      directory,
      git: normalizeGitInfo(gitInfo),
      device: normalizeDeviceInfo(deviceInfo),
      projectDirectory: projectDirPath,
    };

    await mkdir(projectDirPath, { recursive: true });
    const target = join(projectDirPath, OVERVIEW_FILENAME);
    const temp = join(projectDirPath, `.${OVERVIEW_FILENAME}.${generateULID()}.tmp`);
    try {
      await writeFile(temp, `${JSON.stringify(overview, null, 2)}\n`, "utf8");
      await rename(temp, target);
    } catch (error) {
      try {
        await rm(temp, { force: true });
      } catch {}
      throw error;
    }
  } catch (error) {
    try {
      logger?.(
        `usage-tracking: writing overview.json failed (${errorMessage(error)}); overview skipped (fail-open)`,
      );
    } catch {}
  }
}
