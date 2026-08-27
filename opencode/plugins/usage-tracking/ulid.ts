/**
 * ULID generation + per-project directory resolution for the usage-tracking
 * plugin.
 *
 * Supports the V11 output layout: instead of deriving a subdirectory from
 * project.id/worktree basenames, every project identity (absolute worktree
 * path, else absolute directory path) gets a stable ULID subdirectory under
 * the configured output root. The mapping is persisted in a registry
 * `<outputRoot>/projects.json` (ULID → {identity, directory, createdAt}).
 *
 * Fail-open (ADR-05): an unreadable/corrupted registry starts fresh (silent);
 * a registry write failure still returns the new ULID after logging exactly
 * once. Registry keys are validated as ULIDs on read (security review F1): a
 * key that is not a canonical 26-char Crockford-base32 ULID is treated as
 * absent, so a hostile/hand-edited key never becomes a path segment. This
 * module is pure and testable — no OpenCode imports; the only I/O
 * is `node:fs/promises`.
 */

import { mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, isAbsolute, join, resolve } from "node:path";

const CROCKFORD_ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
// 48-bit timestamp → 10 base32 chars; 80-bit randomness → 16 base32 chars.
const TIME_LENGTH = 10;
const RANDOM_LENGTH = 16;
const REGISTRY_FILENAME = "projects.json";

// Registry keys are ULIDs and become path segments: on read, any key that is
// not a canonical 26-char Crockford-base32 ULID (this alphabet, minus I L O U)
// is treated as absent — a hand-crafted key like "../escape" or "__proto__"
// is never returned as a directory name and never rewritten (security
// review F1).
const ULID_KEY_RE = /^[0-9A-HJKMNP-TV-Z]{26}$/;

/** Receives one message per registry write failure; must never throw. */
export type ProjectRegistryLogger = (message: string) => void;

/** Resolved-config slice this module consumes: only the absolute `output` root. */
export type ProjectDirectoryConfig = {
  output: string;
};

/** Plugin init input slice (unvalidated `unknown` fields from OpenCode). */
export type ProjectDirectoryInput = {
  worktree?: unknown;
  directory?: unknown;
  project?: unknown;
};

/** One registry entry: `directory` differs from `identity` when a worktree is present. */
export type ProjectRegistryEntry = {
  identity: string;
  directory: string;
  createdAt: string;
};

// Null-prototype record: hostile keys like "__proto__" in a hand-crafted
// registry land as own properties instead of hitting Object.prototype's
// setter (prototype-pollution guard, cf. aggregate.ts's safeRecord).
function safeRecord<T>(): Record<string, T> {
  return Object.create(null);
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readNonEmptyString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

/** Expands a leading `~`/`~/` and pins the result to an absolute path. */
function absolutePath(value: string): string {
  if (value === "~") return homedir();
  const expanded = value.startsWith("~/") ? join(homedir(), value.slice(2)) : value;
  return isAbsolute(expanded) ? expanded : resolve(expanded);
}

// ---------------------------------------------------------------------------
// Monotonic ULID generation
// ---------------------------------------------------------------------------

// Generator state (module-level): the last emitted timestamp plus its random
// component. Within one millisecond the random component increments (ULID-spec
// monotonicity, so same-ms ids stay unique AND non-decreasing); a new
// millisecond draws fresh randomness. A backwards-moving clock is clamped to
// the last timestamp so ordering never regresses.
let lastTime = Number.NaN;
let lastRandom: number[] = [];

/** Encodes a non-negative integer timestamp as 10 Crockford base32 chars (zero-padded). */
function encodeTime(time: number): string {
  let out = "";
  let rest = time;
  for (let i = 0; i < TIME_LENGTH; i++) {
    out = CROCKFORD_ENCODING[rest % 32] + out;
    rest = Math.floor(rest / 32);
  }
  return out;
}

/** Draws 16 uniform base32 digits (80 bits of randomness). */
function randomDigits(): number[] {
  const digits = new Array<number>(RANDOM_LENGTH);
  const bytes = new Uint8Array(RANDOM_LENGTH);
  if (typeof globalThis.crypto?.getRandomValues === "function") {
    globalThis.crypto.getRandomValues(bytes);
    // 256 % 32 === 0, so byte % 32 stays uniform.
    for (let i = 0; i < RANDOM_LENGTH; i++) digits[i] = bytes[i] % 32;
  } else {
    for (let i = 0; i < RANDOM_LENGTH; i++) digits[i] = Math.floor(Math.random() * 32);
  }
  return digits;
}

/** Increments a base32 digit string (MSB first); null on 80-bit overflow. */
function incrementDigits(digits: number[]): number[] | null {
  const next = [...digits];
  for (let i = next.length - 1; i >= 0; i--) {
    if (next[i] < 31) {
      next[i] += 1;
      return next;
    }
    next[i] = 0;
  }
  return null;
}

/**
 * Generates a monotonic ULID: 26 chars over the Crockford base32 alphabet,
 * 48-bit millisecond timestamp + 80-bit randomness.
 *
 * Two ids generated in order compare `<=` (lexicographic order matches
 * numeric order for this alphabet): the timestamp dominates across
 * milliseconds, and within one millisecond the random component increments.
 *
 * @returns A 26-character ULID string.
 */
export function generateULID(): string {
  const now = Date.now();
  let time = now;
  let random: number[] | null = null;
  if (now <= lastTime) {
    // Same millisecond (or a backwards clock): increment the previous
    // random component. On the (astronomically unlikely) 80-bit overflow,
    // advance one millisecond and draw fresh randomness.
    time = lastTime;
    random = incrementDigits(lastRandom);
    if (random === null) {
      time = lastTime + 1;
      random = randomDigits();
    }
  } else {
    random = randomDigits();
  }
  lastTime = time;
  lastRandom = random;
  let out = encodeTime(time);
  for (let i = 0; i < RANDOM_LENGTH; i++) {
    out += CROCKFORD_ENCODING[random[i]];
  }
  return out;
}

// ---------------------------------------------------------------------------
// Registry-backed project directory resolution
// ---------------------------------------------------------------------------

/**
 * Parses registry content; anything unreadable/corrupted yields a fresh
 * (empty) registry, and entries with a non-ULID key are skipped (treated as
 * absent — F1).
 */
function parseRegistry(content: string): Record<string, ProjectRegistryEntry> {
  const registry = safeRecord<ProjectRegistryEntry>();
  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch {
    return registry;
  }
  if (!isPlainObject(parsed)) return registry;
  for (const key of Object.keys(parsed)) {
    // Key validation before any use: a non-ULID key is skipped (absent),
    // never resolved into a directory (F1). All keys we write ourselves are
    // generateULID() output, so this only ever filters foreign entries.
    if (!ULID_KEY_RE.test(key)) continue;
    const entry = parsed[key];
    if (!isPlainObject(entry)) continue;
    const identity = readNonEmptyString(entry.identity);
    const directory = readNonEmptyString(entry.directory);
    if (identity === null || directory === null) continue;
    registry[key] = {
      identity,
      directory,
      createdAt: readNonEmptyString(entry.createdAt) ?? new Date().toISOString(),
    };
  }
  return registry;
}

/** Reads the registry; missing/unreadable files yield a fresh registry (silent, fail-open). */
async function readRegistry(file: string): Promise<Record<string, ProjectRegistryEntry>> {
  try {
    return parseRegistry(await readFile(file, "utf8"));
  } catch {
    return safeRecord<ProjectRegistryEntry>();
  }
}

/** Returns the ULID key of the first entry matching `identity`, or null. */
function findULIDByIdentity(
  registry: Record<string, ProjectRegistryEntry>,
  identity: string,
): string | null {
  for (const key of Object.keys(registry)) {
    if (registry[key].identity === identity) return key;
  }
  return null;
}

/**
 * Writes the registry ATOMICALLY: a temp file in the same directory, then
 * rename over the target — readers never observe a torn file.
 */
async function writeRegistry(
  file: string,
  registry: Record<string, ProjectRegistryEntry>,
): Promise<void> {
  const directory = dirname(file);
  await mkdir(directory, { recursive: true });
  const temp = join(directory, `.${REGISTRY_FILENAME}.${generateULID()}.tmp`);
  try {
    await writeFile(temp, `${JSON.stringify(registry, null, 2)}\n`, "utf8");
    await rename(temp, file);
  } catch (error) {
    try {
      await rm(temp, { force: true });
    } catch {}
    throw error;
  }
}

/**
 * Resolves the per-project subdirectory name (a ULID) under `config.output`.
 *
 * Identity = absolute worktree path when present, else absolute directory
 * path (`~` expanded, relative paths pinned against the host cwd);
 * `project.id` is deliberately NOT part of the identity. The registry
 * `<outputRoot>/projects.json` maps ULID → {identity, directory, createdAt}:
 * a known identity returns its existing ULID untouched; a new identity gets a
 * fresh ULID and an atomically persisted registry entry.
 *
 * Fail-open (ADR-05): a corrupted/unreadable registry starts fresh (silent);
 * a registry write failure still returns the new ULID after logging exactly
 * once via the injected logger.
 *
 * @param config - Resolved config (`.output` is the registry's parent root).
 * @param input - Plugin init input (`worktree`/`directory` are unvalidated).
 * @param logger - Optional error sink; invoked exactly once per failed write.
 * @returns The ULID subdirectory name for the input's identity.
 */
export async function resolveProjectDirectory(
  config: ProjectDirectoryConfig | null | undefined,
  input: ProjectDirectoryInput | null | undefined,
  logger?: ProjectRegistryLogger,
): Promise<string> {
  const log = (message: string): void => {
    try {
      logger?.(message);
    } catch {}
  };

  const outputRoot = isPlainObject(config) ? readNonEmptyString(config.output) : null;
  if (outputRoot === null) {
    log("usage-tracking: no output root available for the project registry; using an unpersisted ULID (fail-open)");
    return generateULID();
  }

  const fields = isPlainObject(input) ? input : {};
  const worktree = readNonEmptyString(fields.worktree);
  const directory = readNonEmptyString(fields.directory);
  // Identity prefers the worktree; the recorded `directory` prefers the
  // actual directory, falling back to the worktree when absent.
  const identity = absolutePath(worktree ?? directory ?? ".");
  const projectDirectory = absolutePath(directory ?? worktree ?? ".");

  const registryFile = join(outputRoot, REGISTRY_FILENAME);
  const registry = await readRegistry(registryFile);
  const existing = findULIDByIdentity(registry, identity);
  if (existing !== null) return existing;

  const ulid = generateULID();
  registry[ulid] = {
    identity,
    directory: projectDirectory,
    createdAt: new Date().toISOString(),
  };
  try {
    await writeRegistry(registryFile, registry);
  } catch (error) {
    log(
      `usage-tracking: writing ${registryFile} failed (${errorMessage(error)}); continuing with directory ${ulid} (fail-open)`,
    );
  }
  return ulid;
}
