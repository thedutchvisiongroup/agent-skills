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
import { join } from "node:path";
import plugin from "./index";

const fakeInput: any = {
  client: { app: { log: async () => {} } },
  project: {},
  directory: "/tmp",
  worktree: "/tmp",
};

describe("usage-tracking plugin (default export)", () => {
  it("resolves to hooks exposing an event() function", async () => {
    const hooks = await plugin(fakeInput, {});

    expect(hooks).toBeDefined();
    expect(typeof hooks.event).toBe("function");
  });

  it("event() resolves even when internals fail (fail-open)", async () => {
    const hooks = await plugin(fakeInput, {});

    let rejected = false;
    try {
      // Malformed envelope on purpose: no event id, empty properties. Internals
      // may fail or skip; the hook itself must never reject.
      await hooks.event({ event: { type: "session.idle", properties: {} } });
    } catch {
      rejected = true;
    }
    expect(rejected).toBe(false);
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
