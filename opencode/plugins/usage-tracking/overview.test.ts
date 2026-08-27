// Red test suite (v11, dispatch 2026-08-27) for the usage-tracking plugin's
// project-level overview.json + device info. Specification source: v11
// dispatch (three approved changes).
//
// Contract under test — `writeOverview` from "./overview" (new module):
//   writeOverview(projectDir, aggregates, deviceInfo, gitInfo): Promise<void>
//       — writes <projectDir>/overview.json with the EXACT shape:
//         { generatedAt, sessions, modelsUsed: [{id, provider, variant}],
//           tokens: {input, output, reasoning, cacheRead, cacheWrite}, cost,
//           toolCounts, activeMs, directory,
//           git: {branch, tag, lastCommit: {hash, subject, author, date} | null} | null,
//           device: {name, os, osVersion, opencodeVersion}, projectDirectory }
//         `aggregates` is a finalize()-shaped Record<sessionID, SessionAggregate>.
//         Regenerating overwrites the file atomically (a second write fully
//         replaces the first; no temp leftovers).
//
// Spec decisions recorded in reports/v11-red-tests.md:
// - `sessions` = the number of session aggregates (matches the sessions/*.json
//   files 1:1); the summed metrics (tokens/cost/toolCounts/activeMs) cover
//   ROOT sessions only — a child's own totals are already inside its parent's
//   AC 7.3 rollup, so summing children too would double-count. A session
//   whose parentID is absent from the aggregates (orphan) counts as a root so
//   its totals are never lost.
// - `directory` = the sessions' working directory; `projectDirectory` = the
//   projectDir argument (where overview.json is written).
// - `generatedAt` presence is asserted, its type (ISO string vs epoch) is
//   deliberately left to the implementation.
// - Null gitInfo is tolerated (git: null); a gitInfo with null tag/lastCommit
//   passes through verbatim.
import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { mkdtempSync, readFileSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { writeOverview } from "./overview";

const DEVICE_INFO = {
  name: "thim-desktop",
  os: "linux",
  osVersion: "6.8.0",
  opencodeVersion: "1.18.21",
};

const GIT_INFO = {
  branch: "main",
  tag: "v1.2.3",
  lastCommit: {
    hash: "abc123def4567890",
    subject: "fix: activeMs pairing",
    author: "Thim",
    date: "2026-08-27T10:00:00Z",
  },
};

/** Minimal finalize()-shaped session aggregate literal (loose `any`: the
 * overview consumes the persisted aggregate shape, not the class). */
function sessionAggregate(overrides: Record<string, any>): any {
  return {
    sessionID: "sess_1",
    parentID: null,
    project: "proj_1",
    directory: "/wt/x",
    depth: 0,
    title: null,
    agents: ["build"],
    models: [],
    tokens: { input: 0, output: 0, reasoning: 0, cacheRead: 0, cacheWrite: 0 },
    cost: 0,
    activeMs: 0,
    toolCounts: {},
    children: [],
    time: { created: null, updated: null, idle: null },
    ...overrides,
  };
}

let projectDir: string;

beforeEach(() => {
  projectDir = mkdtempSync(join(tmpdir(), "usage-tracking-overview-"));
});

afterEach(() => {
  rmSync(projectDir, { recursive: true, force: true });
});

/** Reads and parses <projectDir>/overview.json. */
function readOverview(): any {
  return JSON.parse(readFileSync(join(projectDir, "overview.json"), "utf8"));
}

describe("writeOverview()", () => {
  it("writes <dir>/overview.json with the exact shape, summing root-session totals and unioning models", async () => {
    const aggregates = {
      sess_1: sessionAggregate({
        sessionID: "sess_1",
        models: [{ id: "model-a", provider: "anthropic", variant: null }],
        tokens: { input: 100, output: 40, reasoning: 10, cacheRead: 500, cacheWrite: 60 },
        cost: 0.25,
        activeMs: 2000,
        toolCounts: { read: 2, bash: 1 },
      }),
      sess_2: sessionAggregate({
        sessionID: "sess_2",
        models: [
          { id: "model-a", provider: "anthropic", variant: null },
          { id: "model-b", provider: "openai", variant: "pro" },
        ],
        tokens: { input: 25, output: 15, reasoning: 5, cacheRead: 50, cacheWrite: 6 },
        cost: 0.5,
        activeMs: 1000,
        toolCounts: { read: 1 },
      }),
    };

    await writeOverview(projectDir, aggregates, DEVICE_INFO, GIT_INFO);

    const overview = readOverview();
    // EXACT shape: exactly these keys, nothing more.
    expect(Object.keys(overview).sort()).toEqual(
      [
        "activeMs",
        "cost",
        "device",
        "directory",
        "generatedAt",
        "git",
        "modelsUsed",
        "projectDirectory",
        "sessions",
        "tokens",
        "toolCounts",
      ].sort(),
    );

    // sessions = number of session aggregates.
    expect(overview.sessions).toBe(2);
    // Union of models across sessions, deduplicated by id.
    const modelsUsed = [...overview.modelsUsed].sort((a: any, b: any) =>
      a.id.localeCompare(b.id),
    );
    expect(modelsUsed).toEqual([
      { id: "model-a", provider: "anthropic", variant: null },
      { id: "model-b", provider: "openai", variant: "pro" },
    ]);
    // Summed across sessions.
    expect(overview.tokens).toEqual({
      input: 125,
      output: 55,
      reasoning: 15,
      cacheRead: 550,
      cacheWrite: 66,
    });
    expect(overview.cost).toBe(0.75);
    expect(overview.toolCounts).toEqual({ read: 3, bash: 1 });
    expect(overview.activeMs).toBe(3000);
    // directory = the sessions' working directory; projectDirectory = the
    // directory writeOverview writes into.
    expect(overview.directory).toBe("/wt/x");
    expect(overview.projectDirectory).toBe(projectDir);
    expect(overview.git).toEqual(GIT_INFO);
    expect(overview.device).toEqual(DEVICE_INFO);
    // generatedAt is present (type intentionally loose — see header).
    expect(overview.generatedAt).toBeTruthy();
  });

  it("tolerates null gitInfo (git: null)", async () => {
    await writeOverview(projectDir, { sess_1: sessionAggregate({}) }, DEVICE_INFO, null);

    expect(readOverview().git).toBe(null);
  });

  it("passes a gitInfo with null tag and null lastCommit through verbatim", async () => {
    const gitInfo = { branch: "main", tag: null, lastCommit: null };
    await writeOverview(projectDir, { sess_1: sessionAggregate({}) }, DEVICE_INFO, gitInfo);

    expect(readOverview().git).toEqual({ branch: "main", tag: null, lastCommit: null });
  });

  it("sums only root sessions: a child's own totals are already inside the parent's rollup (no double count)", async () => {
    const aggregates = {
      parent: sessionAggregate({
        sessionID: "parent",
        // AC 7.3 rollup: the parent's totals already include the child.
        tokens: { input: 175, output: 75, reasoning: 20, cacheRead: 750, cacheWrite: 76 },
        cost: 0.75,
        activeMs: 5000,
        toolCounts: { read: 3 },
        models: [{ id: "model-a", provider: "anthropic", variant: null }],
      }),
      child: sessionAggregate({
        sessionID: "child",
        parentID: "parent",
        tokens: { input: 100, output: 40, reasoning: 10, cacheRead: 500, cacheWrite: 60 },
        cost: 0.5,
        activeMs: 3000,
        toolCounts: { read: 2 },
        models: [{ id: "model-a", provider: "anthropic", variant: null }],
      }),
      orphan: sessionAggregate({
        sessionID: "orphan",
        parentID: "ghost", // absent parent → root; its totals must not be lost
        tokens: { input: 25, output: 15, reasoning: 5, cacheRead: 50, cacheWrite: 6 },
        cost: 0.25,
        activeMs: 1000,
        toolCounts: { bash: 1 },
        models: [{ id: "model-b", provider: "openai", variant: null }],
      }),
    };

    await writeOverview(projectDir, aggregates, DEVICE_INFO, null);

    const overview = readOverview();
    // parent (rolled-up) + orphan; the child is never summed on its own.
    expect(overview.tokens.input).toBe(200);
    expect(overview.cost).toBe(1);
    expect(overview.activeMs).toBe(6000);
    expect(overview.toolCounts).toEqual({ read: 3, bash: 1 });
    // sessions counts every aggregate (matches the sessions/*.json files).
    expect(overview.sessions).toBe(3);
  });

  it("regenerates atomically: a second write fully replaces the first, leaving no temp files", async () => {
    const first = {
      sess_1: sessionAggregate({
        cost: 0.75,
        tokens: { input: 100, output: 0, reasoning: 0, cacheRead: 0, cacheWrite: 0 },
      }),
    };
    const second = {
      sess_1: sessionAggregate({
        cost: 0.5,
        tokens: { input: 40, output: 0, reasoning: 0, cacheRead: 0, cacheWrite: 0 },
      }),
    };

    await writeOverview(projectDir, first, DEVICE_INFO, null);
    await writeOverview(projectDir, second, DEVICE_INFO, null);

    const overview = readOverview();
    // Fully replaced, never merged or appended.
    expect(overview.cost).toBe(0.5);
    expect(overview.tokens.input).toBe(40);
    // Atomicity proxy: only overview.json lives in the project directory —
    // no leftover temp files from the overwrite.
    expect(readdirSync(projectDir)).toEqual(["overview.json"]);
  });
});
