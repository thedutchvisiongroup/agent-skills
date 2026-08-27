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
import { tmpdir } from "node:os";
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
// v11 addition — dispatch 2026-08-27: ULID project directories + registry.
// The plugin's output root must carry <outputRoot>/projects.json (mapping
// ULID → {identity, directory, createdAt}) and write events.jsonl inside the
// ULID subdirectory registered for the init input's identity (absolute
// worktree path if present, else absolute directory path). This pins the
// wiring that replaces the old project.id-first projectSubdirectory
// candidates — no pre-existing test pinned those candidates (verified by
// grep: findEventsFile is recursion-agnostic), so this is the new guard.
// ---------------------------------------------------------------------------

const ULID_CHARS = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
const ULID_RE = new RegExp(`^[${ULID_CHARS}]{26}$`);

describe("usage-tracking plugin — ULID project directories (v11)", () => {
  it("registers the project in projects.json and writes events under its ULID subdirectory", async () => {
    const out = mkdtempSync(join(tmpdir(), "usage-tracking-ulid-wiring-"));
    try {
      const hooks = await plugin({ ...fakeInput }, { output: out });
      await hooks.event({
        event: {
          id: "evt-ulid-wiring-1",
          type: "session.idle",
          properties: { sessionID: "sess_ulid_1" },
        },
      });
      await hooks.dispose?.();

      // The registry exists at the output root.
      const registryPath = join(out, "projects.json");
      expect(existsSync(registryPath)).toBe(true);
      const registry = JSON.parse(readFileSync(registryPath, "utf8"));

      // events.jsonl lives inside a ULID-named subdirectory…
      const eventsFile = findEventsFile(out);
      expect(eventsFile).not.toBeNull();
      const subdirectory = basename(dirname(eventsFile!));
      expect(subdirectory).toMatch(ULID_RE);
      // …that is a key of the registry, registered under the init input's
      // worktree identity.
      expect(Object.hasOwn(registry, subdirectory)).toBe(true);
      expect(registry[subdirectory].identity).toBe("/tmp");
    } finally {
      rmSync(out, { recursive: true, force: true });
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
    // Four call sites today (two default-export tests, task 6, v11 wiring);
    // the floor keeps the scan from rotting into a vacuous pass.
    expect(callLines.length).toBeGreaterThanOrEqual(4);
    for (const line of callLines) {
      expect(line).toContain("output:");
    }
  });
});
