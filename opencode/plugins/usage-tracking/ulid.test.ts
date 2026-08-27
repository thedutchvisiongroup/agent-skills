// Red test suite (v11, dispatch 2026-08-27) for the usage-tracking plugin's
// ULID project directories + registry. Specification sources: v11 dispatch
// (three approved changes), ULID specification (ulid/spec: 26 chars, Crockford
// base32 "0123456789ABCDEFGHJKMNPQRSTVWXYZ", 48-bit timestamp + 80-bit
// randomness, monotonic within the same millisecond).
//
// Contract under test — "./ulid" (new module; the registry may internally
// live elsewhere as long as these exports resolve from "./ulid"):
//   generateULID(): string
//       — 26 characters over the Crockford base32 alphabet; two ids generated
//         in order compare <= (monotonic ULID: within one millisecond the
//         random component increments, so later ids sort after earlier ones);
//         same-millisecond generation stays unique.
//   resolveProjectDirectory(config, input, logger?): Promise<string>
//       — resolves the per-project subdirectory name (a ULID) under
//         config.output, maintaining the registry <outputRoot>/projects.json
//         that maps ULID → {identity, directory, createdAt}.
//         identity = absolute worktree path if present, else absolute
//         directory path (project.id is NOT part of the identity — the old
//         project.id-first projectSubdirectory candidates are gone).
//         First init for an identity creates the entry and returns its ULID;
//         a repeated init of the same identity returns the SAME ULID without
//         adding an entry; a different identity gets a different ULID.
//         A corrupted/unreadable registry yields a fresh ULID without
//         throwing; a registry write failure fails open (a ULID is still
//         returned and the logger is called exactly once).
//
// Spec decisions recorded in reports/v11-red-tests.md: the optional third
// parameter is the error logger (house convention, cf. resolveConfig /
// EventStore) — the dispatch's suggested `fs?` seam is NOT required by these
// tests, which use the real filesystem via tmpdir (cf. store.test.ts).
import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { resolveConfig } from "./config";
import { generateULID, resolveProjectDirectory } from "./ulid";

const CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
const ULID_RE = new RegExp(`^[${CROCKFORD_BASE32}]{26}$`);

let root: string;
let config: { output: string };

beforeEach(() => {
  root = mkdtempSync(join(tmpdir(), "usage-tracking-ulid-"));
  config = resolveConfig({ output: root });
});

afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});

/** Reads and parses the registry at <outputRoot>/projects.json. */
function readRegistry(): Record<string, any> {
  return JSON.parse(readFileSync(join(root, "projects.json"), "utf8"));
}

describe("generateULID()", () => {
  it("produces 26-character ids over the Crockford base32 alphabet", () => {
    for (let i = 0; i < 50; i++) {
      const ulid = generateULID();
      expect(ulid).toHaveLength(26);
      expect(ulid).toMatch(ULID_RE);
    }
  });

  it("is monotonic: ids generated in order compare <= and same-ms generation stays unique", () => {
    const first = generateULID();
    const second = generateULID();
    expect(first <= second).toBe(true);

    // A tight loop keeps (most) generations inside one millisecond: every id
    // must stay unique AND non-decreasing (ULID-spec monotonicity — the
    // random component increments within the same millisecond).
    const batch: string[] = [];
    for (let i = 0; i < 200; i++) {
      batch.push(generateULID());
    }
    expect(new Set(batch).size).toBe(batch.length);
    for (let i = 1; i < batch.length; i++) {
      expect(batch[i - 1] <= batch[i]).toBe(true);
    }
  });
});

describe("resolveProjectDirectory() — registry semantics", () => {
  it("creates <outputRoot>/projects.json on first init and returns the new ULID as the subdirectory name", async () => {
    const subdirectory = await resolveProjectDirectory(config, {
      worktree: "/wt/x",
      directory: "/dir/x",
    });

    expect(subdirectory).toMatch(ULID_RE);
    const registry = readRegistry();
    expect(Object.keys(registry)).toHaveLength(1);
    const entry = registry[subdirectory];
    expect(entry).toBeDefined();
    // identity prefers the absolute worktree path; directory is the
    // project's directory path; createdAt is present.
    expect(entry.identity).toBe("/wt/x");
    expect(entry.directory).toBe("/dir/x");
    expect(entry.createdAt).toBeTruthy();
  });

  it("returns the SAME ULID for a repeated init of the same identity (no new entry)", async () => {
    const first = await resolveProjectDirectory(config, {
      worktree: "/wt/x",
      directory: "/dir/x",
    });
    const second = await resolveProjectDirectory(config, {
      worktree: "/wt/x",
      directory: "/dir/x",
    });

    expect(second).toBe(first);
    expect(Object.keys(readRegistry())).toHaveLength(1);
  });

  it("returns a different ULID for a different identity", async () => {
    const a = await resolveProjectDirectory(config, { worktree: "/wt/x", directory: "/dir/x" });
    const b = await resolveProjectDirectory(config, { worktree: "/wt/y", directory: "/dir/y" });

    expect(b).not.toBe(a);
    expect(b).toMatch(ULID_RE);
    expect(Object.keys(readRegistry())).toHaveLength(2);
  });

  it("derives identity from the worktree when present, else from the directory", async () => {
    const withWorktree = await resolveProjectDirectory(config, {
      worktree: "/wt/x",
      directory: "/dir/x",
    });
    const withoutWorktree = await resolveProjectDirectory(config, { directory: "/dir/x" });

    // "/wt/x" and "/dir/x" are distinct identities → distinct ULIDs.
    expect(withoutWorktree).not.toBe(withWorktree);
    const registry = readRegistry();
    expect(registry[withWorktree].identity).toBe("/wt/x");
    expect(registry[withoutWorktree].identity).toBe("/dir/x");
  });

  it("ignores project.id when deriving the identity (old project.id-first candidates are gone)", async () => {
    const a = await resolveProjectDirectory(config, {
      worktree: "/wt/x",
      directory: "/dir/x",
      project: { id: "proj_a" },
    });
    const b = await resolveProjectDirectory(config, {
      worktree: "/wt/x",
      directory: "/dir/x",
      project: { id: "proj_b" },
    });

    expect(b).toBe(a);
    expect(Object.keys(readRegistry())).toHaveLength(1);
  });

  it("generates a new ULID without throwing when the registry is corrupted/unreadable", async () => {
    writeFileSync(join(root, "projects.json"), "{not-json");

    let threw = false;
    let subdirectory: string | null = null;
    try {
      subdirectory = await resolveProjectDirectory(config, {
        worktree: "/wt/x",
        directory: "/dir/x",
      });
    } catch {
      threw = true;
    }
    expect(threw).toBe(false);
    expect(subdirectory).toMatch(ULID_RE);
  });

  it("fails open on a registry write failure: still returns a ULID and logs exactly once", async () => {
    // A directory at the registry path blocks both reading and writing it
    // (EISDIR) — the house pattern for unwritable-path tests (cf.
    // store.test.ts's blocker file).
    mkdirSync(join(root, "projects.json"));
    const messages: string[] = [];

    const subdirectory = await resolveProjectDirectory(
      config,
      { worktree: "/wt/x", directory: "/dir/x" },
      (message) => messages.push(message),
    );

    expect(subdirectory).toMatch(ULID_RE);
    // "Logs once": the unreadable registry is tolerated silently (fresh
    // ULID) and the write failure is reported exactly once — no flooding.
    expect(messages).toHaveLength(1);
  });
});
