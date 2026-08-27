// Red test suite (Task 4) for the usage-tracking plugin entry point.
// Specification sources: task dispatch (2026-08-26), spike findings
// (fail-open, multi-instance safety), @opencode-ai/plugin 1.18.21 types
// (Plugin = (input, options?) => Promise<Hooks>, Hooks.event).
//
// Contract under test — the default export of "./index":
//   plugin(input, options) resolves to a Hooks object exposing `event`.
//   event({ event }) must ALWAYS resolve (fail-open): a malformed envelope or
//   failing internals (store, mapping, aggregation) must never reject and break
//   the host OpenCode instance.
//
// The fake input is deliberately minimal — only the surfaces the plugin may
// touch at initialization/event time (client.app.log for warnings). It is
// untyped (`any`) because the sibling modules do not exist yet; these red tests
// define their runtime contract.
import { describe, it, expect } from "bun:test";
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { hostname, tmpdir } from "node:os";
import { basename, dirname, join } from "node:path";
import plugin from "./index";

const fakeInput: any = {
  client: { app: { log: async () => {} } },
  project: {},
  directory: "/tmp",
  worktree: "/tmp",
};

describe("usage-tracking plugin (default export)", () => {
  // Test hygiene (review finding, 2026-08-27): every init below passes an
  // explicit tmpdir `output`. A default-config init would write a real
  // registry entry to ~/.local/share/opencode-usage/projects.json (identity
  // "/tmp") — tests must never touch the real default root. These two tests
  // exercise the default fallback of every OTHER option field, not the
  // default output root.
  it("resolves to hooks exposing an event() function", async () => {
    const out = mkdtempSync(join(tmpdir(), "usage-tracking-default-export-"));
    try {
      const hooks = await plugin(fakeInput, { output: out });

      expect(hooks).toBeDefined();
      expect(typeof hooks.event).toBe("function");
      await hooks.dispose?.();
    } finally {
      rmSync(out, { recursive: true, force: true });
    }
  });

  it("event() resolves even when internals fail (fail-open)", async () => {
    const out = mkdtempSync(join(tmpdir(), "usage-tracking-fail-open-"));
    try {
      const hooks = await plugin(fakeInput, { output: out });

      let rejected = false;
      try {
        // Malformed envelope on purpose: no event id, empty properties. Internals
        // may fail or skip; the hook itself must never reject.
        await hooks.event({ event: { type: "session.idle", properties: {} } });
      } catch {
        rejected = true;
      }
      expect(rejected).toBe(false);
      await hooks.dispose?.();
    } finally {
      rmSync(out, { recursive: true, force: true });
    }
  });
});

// ---------------------------------------------------------------------------
// Task 6 addition — review finding (code + security review, 2026-08-26):
// message.info and step.started are INTERNAL records — they feed the live
// aggregator but must never be persisted to events.jsonl (the event stream is
// the rebuild source; internal records are derivable and not part of the
// persisted contract). This test is the guard for that filter: it is vacuously
// green while mapping ignores message.updated/step-start parts, and turns red
// the moment mapping emits those records unless the write path filters them.
// ---------------------------------------------------------------------------

/** Recursively locates the single events.jsonl under the plugin output root. */
function findEventsFile(root: string): string | null {
  for (const entry of readdirSync(root, { recursive: true })) {
    const name = String(entry);
    if (name.endsWith("events.jsonl")) {
      const path = join(root, name);
      if (existsSync(path)) return path;
    }
  }
  return null;
}

describe("usage-tracking plugin — review findings (task 6)", () => {
  it("does not persist internal records (message.info, step.started) to events.jsonl", async () => {
    const out = mkdtempSync(join(tmpdir(), "usage-tracking-internal-"));
    try {
      const hooks = await plugin({ ...fakeInput }, { output: out });

      // One persisted record type (session.started) and two internal ones.
      await hooks.event({
        event: {
          id: "evt-internal-1",
          type: "session.created",
          properties: {
            sessionID: "sess_int_1",
            info: { id: "sess_int_1", time: { created: 1 } },
          },
        },
      });
      await hooks.event({
        event: {
          id: "evt-internal-2",
          type: "message.updated",
          properties: {
            sessionID: "sess_int_1",
            info: {
              id: "msg_1",
              sessionID: "sess_int_1",
              agent: "build",
              modelID: "model-a",
              providerID: "anthropic",
              time: { created: 2 },
            },
          },
        },
      });
      await hooks.event({
        event: {
          id: "evt-internal-3",
          type: "message.part.updated",
          properties: {
            sessionID: "sess_int_1",
            time: 3,
            part: {
              id: "part_int_1",
              sessionID: "sess_int_1",
              messageID: "msg_1",
              type: "step-start",
            },
          },
        },
      });
      await hooks.dispose?.();

      const eventsFile = findEventsFile(out);
      expect(eventsFile).not.toBeNull();
      const types = readFileSync(eventsFile!, "utf8")
        .split("\n")
        .filter((line) => line.trim() !== "")
        .map((line) => JSON.parse(line).type);

      expect(types).toContain("session.started");
      expect(types).not.toContain("message.info");
      expect(types).not.toContain("step.started");
    } finally {
      rmSync(out, { recursive: true, force: true });
    }
  });
});

// ---------------------------------------------------------------------------
// v12 addition — dispatch 2026-08-27: deterministic-hash project directories
// (replaces ULID + projects.json registry). The project subdirectory is
// projectDirectoryName({worktree, directory, remote, hostname}): hostname from
// os.hostname() (fail-open "unknown"), remote probed ONCE at init via
// `git -C <worktree||directory> remote get-url origin` through input.$ (trimmed,
// fail-open null). Wiring pins:
//   - events land under the EXACT projectDirectoryName() value for the init
//     inputs (remote probed through the fake $ shell below);
//   - NO projects.json exists anywhere under the output root (registry gone);
//   - two inits with SEPARATE output roots produce the SAME subdirectory —
//     impossible with random ULIDs unless a registry bridges them, which is
//     exactly what v12 removes.
// "./projectdir" is imported DYNAMICALLY inside the wiring test so this file's
// other (green) tests keep running while the module is missing: a static
// import would fail the whole file at module resolution and mask the
// old-behavior red reason the dispatch asks to verify. After Green, the
// import may be hoisted to the top of the file (behavior-neutral).
// ---------------------------------------------------------------------------

const REMOTE_URL = "https://github.com/usage-tracking/wiring.git";

/**
 * Fake host shell (input.$): answers any `git … remote get-url origin` probe
 * with REMOTE_URL via .text() (the house convention for shell probes, cf.
 * collectGitInfo); every other command fails so the remaining fail-open probes
 * (opencode --version, git branch/tag/log) degrade to null.
 */
const fakeShell: any = (strings: TemplateStringsArray, ...values: unknown[]) => {
  let command = "";
  for (let i = 0; i < strings.length; i++) {
    command += strings[i];
    if (i < values.length) command += String(values[i]);
  }
  return {
    text: async () => {
      if (command.includes("remote get-url origin")) return REMOTE_URL;
      throw new Error(`fake shell: unstubbed command: ${command}`);
    },
  };
};

const wiredInput: any = {
  client: { app: { log: async () => {} } },
  project: {},
  directory: "/tmp",
  worktree: "/tmp",
  $: fakeShell,
};

/** Recursively locates any projects.json under the output root (must stay absent in v12). */
function findProjectsJson(root: string): string | null {
  for (const entry of readdirSync(root, { recursive: true })) {
    const name = String(entry);
    if (name.endsWith("projects.json")) {
      const path = join(root, name);
      if (existsSync(path)) return path;
    }
  }
  return null;
}

describe("usage-tracking plugin — deterministic project directories (v12)", () => {
  it("writes events under the exact projectDirectoryName() subdirectory for the init inputs", async () => {
    const out = mkdtempSync(join(tmpdir(), "usage-tracking-hash-wiring-"));
    try {
      const hooks = await plugin({ ...wiredInput }, { output: out });
      await hooks.event({
        event: {
          id: "evt-hash-wiring-1",
          type: "session.idle",
          properties: { sessionID: "sess_hash_1" },
        },
      });
      await hooks.dispose?.();

      const eventsFile = findEventsFile(out);
      expect(eventsFile).not.toBeNull();
      const subdirectory = basename(dirname(eventsFile!));
      // Old behavior (random ULID subdirectory) fails HERE first — the
      // old-behavior red the dispatch asks to verify — before the dynamic
      // import below ever runs.
      expect(subdirectory).toMatch(/^[0-9a-f]{24}$/);

      const { projectDirectoryName } = await import("./projectdir");
      const expected = projectDirectoryName({
        worktree: "/tmp",
        directory: "/tmp",
        remote: REMOTE_URL,
        hostname: hostname(),
      });
      expect(expected).not.toBeNull();
      expect(subdirectory).toBe(expected);
    } finally {
      rmSync(out, { recursive: true, force: true });
    }
  });

  it("creates no projects.json anywhere under the output root after init + events (registry removed)", async () => {
    const out = mkdtempSync(join(tmpdir(), "usage-tracking-no-registry-"));
    try {
      const hooks = await plugin({ ...wiredInput }, { output: out });
      await hooks.event({
        event: {
          id: "evt-no-registry-1",
          type: "session.idle",
          properties: { sessionID: "sess_noreg_1" },
        },
      });
      await hooks.dispose?.();

      // Sanity guard: the plugin actually initialized and wrote events, so the
      // absent registry cannot pass vacuously.
      expect(findEventsFile(out)).not.toBeNull();
      expect(findProjectsJson(out)).toBeNull();
    } finally {
      rmSync(out, { recursive: true, force: true });
    }
  });

  it("is deterministic: two inits with separate output roots produce the same project subdirectory", async () => {
    const outA = mkdtempSync(join(tmpdir(), "usage-tracking-det-a-"));
    const outB = mkdtempSync(join(tmpdir(), "usage-tracking-det-b-"));
    try {
      const hooksA = await plugin({ ...wiredInput }, { output: outA });
      await hooksA.event({
        event: { id: "evt-det-a-1", type: "session.idle", properties: { sessionID: "sess_det_1" } },
      });
      await hooksA.dispose?.();

      const hooksB = await plugin({ ...wiredInput }, { output: outB });
      await hooksB.event({
        event: { id: "evt-det-b-1", type: "session.idle", properties: { sessionID: "sess_det_1" } },
      });
      await hooksB.dispose?.();

      const eventsA = findEventsFile(outA);
      const eventsB = findEventsFile(outB);
      expect(eventsA).not.toBeNull();
      expect(eventsB).not.toBeNull();
      // Separate output roots: no shared registry can bridge the two names —
      // only a pure function of the inputs can make them equal.
      expect(basename(dirname(eventsB!))).toBe(basename(dirname(eventsA!)));
    } finally {
      rmSync(outA, { recursive: true, force: true });
      rmSync(outB, { recursive: true, force: true });
    }
  });
});

// ---------------------------------------------------------------------------
// v11 test hygiene — review finding (2026-08-27): the two default-export
// tests above used to init the plugin WITHOUT an `output` option, so the
// init-time project-registry write landed in the REAL default root
// (~/.local/share/opencode-usage/projects.json, identity "/tmp"). Tests must
// never touch the real root, so every plugin invocation in this file now
// passes an explicit tmpdir `output`. The guard below pins that rule: it
// fails the moment a call site without an `output:` option is added. Keep
// plugin invocations on a single line (call site and options together) so
// the line-based scan stays sound.
// ---------------------------------------------------------------------------

describe("usage-tracking plugin — test hygiene (v11)", () => {
  it("every plugin invocation in this file passes an explicit output (never the real default root)", () => {
    const source = readFileSync(join(import.meta.dir, "index.test.ts"), "utf8");
    // Assembled from parts so this guard's own source does not match itself.
    const callNeedle = "await plugin" + "(";
    const callLines = source.split("\n").filter((line) => line.includes(callNeedle));
    // Seven call sites today (two default-export tests, task 6, three v12
    // wiring tests — the determinism test inits twice); the floor keeps the
    // scan from rotting into a vacuous pass.
    expect(callLines.length).toBeGreaterThanOrEqual(4);
    for (const line of callLines) {
      expect(line).toContain("output:");
    }
  });
});
