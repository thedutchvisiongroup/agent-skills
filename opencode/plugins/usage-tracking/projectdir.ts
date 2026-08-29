/**
 * Deterministic project-directory naming for the usage-tracking plugin.
 *
 * V12 output layout: the per-project subdirectory under the configured output
 * root is a pure hash of the project's identity, replacing the V11 ULID +
 * `projects.json` registry (state that could not bridge separate output
 * roots). Formula (FTD §11.4 formula note, v12 dispatch — pinned exactly):
 *
 *   identity  = resolve(worktree) for a non-empty-string worktree whose
 *               resolution is not the filesystem root ("/" — OpenCode's
 *               placeholder for non-git projects; treated as absent, v1.3),
 *               else resolve(directory) for a non-empty-string directory
 *               (a genuine "/" included),
 *               else null → the result is null (regardless of remote).
 *   remoteKey = remote trimmed with ONE trailing ".git" removed, when that
 *               leaves a non-empty string; else identity.
 *   hashInput = (hostname non-empty string ? hostname : "unknown") + "\n"
 *               + remoteKey
 *   name      = sha256(hashInput) hex digest, first 24 lowercase chars.
 *
 * A present remote key makes the name location-independent (a moved clone
 * keeps its directory); the hostname salt keeps multi-device merges
 * collision-free. The formula is frozen by externally computed known vectors
 * (see `projectdir.test.ts`).
 *
 * Pure and testable — no fs, no OpenCode imports, no randomness; only
 * `node:crypto` (sha256) and `node:path` (resolve). Never throws: any
 * unexpected internal failure yields null (fail-open, ADR-05).
 */

import { createHash } from "node:crypto";
import { resolve } from "node:path";

/** Hash-input fields: unvalidated init values plus the probed origin remote. */
export type ProjectDirectoryNameInput = {
  worktree?: unknown;
  directory?: unknown;
  remote?: unknown;
  hostname?: unknown;
};

const UNKNOWN_HOSTNAME = "unknown";
const REMOTE_SUFFIX = ".git";
const NAME_LENGTH = 24;
// The filesystem root as a worktree is OpenCode's "not in a git repository"
// placeholder, not a project path (resolved once for platform correctness).
const FILESYSTEM_ROOT = resolve("/");

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** A non-empty string value; anything else (including "") is "absent". */
function readNonEmptyString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

/** resolve()d absolute path for a non-empty string; anything else → null. */
function absoluteIdentity(value: unknown): string | null {
  const raw = readNonEmptyString(value);
  return raw === null ? null : resolve(raw);
}

/**
 * Worktree path identity; a filesystem-root resolution ("/") counts as
 * ABSENT. OpenCode passes worktree = "/" for non-git projects (v1.3 bug
 * fix): without this rule every non-git project on a machine shared one
 * output directory. A genuine directory of "/" remains a valid identity.
 */
function worktreeIdentity(value: unknown): string | null {
  const identity = absoluteIdentity(value);
  return identity === FILESYSTEM_ROOT ? null : identity;
}

/**
 * Trimmed remote with exactly ONE trailing ".git" removed; non-string input
 * or a result stripping to empty yields null (the caller falls back to the
 * path identity).
 */
function remoteKey(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  const stripped = trimmed.endsWith(REMOTE_SUFFIX)
    ? trimmed.slice(0, trimmed.length - REMOTE_SUFFIX.length)
    : trimmed;
  return stripped.length > 0 ? stripped : null;
}

/**
 * Computes the deterministic per-project subdirectory name (V12).
 *
 * Identity prefers the worktree over the directory (both `resolve()`d;
 * empty strings and a filesystem-root worktree count as absent — the latter
 * is OpenCode's non-git placeholder, v1.3); a null identity yields null —
 * even with a remote and hostname present. The remote key (trimmed, ONE
 * trailing ".git" off) overrides the identity in the hash input, so the same
 * clone keeps its name across checkouts and machines-with-different-paths;
 * the hostname (used VERBATIM when a non-empty string, else the literal
 * "unknown") salts the hash so concurrent devices never collide.
 *
 * Pure: same input values → same name, independent of call order or caches;
 * never throws (unexpected failures yield null, fail-open ADR-05).
 *
 * @param input - Hash-input fields: `worktree`/`directory` (path identity),
 *   `remote` (probed `git remote get-url origin`, fail-open null), and
 *   `hostname` (e.g. `os.hostname()`).
 * @returns 24 lowercase hex chars, or null when no path identity exists.
 */
export function projectDirectoryName(input: ProjectDirectoryNameInput): string | null {
  try {
    const fields = isPlainObject(input) ? input : {};
    const identity = worktreeIdentity(fields.worktree) ?? absoluteIdentity(fields.directory);
    if (identity === null) return null;
    const key = remoteKey(fields.remote) ?? identity;
    const hostname = readNonEmptyString(fields.hostname) ?? UNKNOWN_HOSTNAME;
    const hashInput = `${hostname}\n${key}`;
    return createHash("sha256").update(hashInput).digest("hex").slice(0, NAME_LENGTH);
  } catch {
    return null;
  }
}
