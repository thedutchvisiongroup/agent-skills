// Red test suite (Task 4) for the usage-tracking plugin's persistent event store.
// Specification sources: task dispatch (2026-08-26 + follow-ups), FTD
// docs/specs/opencode-usage-tracking/ftd-v1.0.md §11.1/§11.2 and AC 7.3, spike
// findings (idempotent JSONL appends, aggregate upserts keyed by sessionID,
// event-ID deduplication, fail-open).
//
// Contract under test — `EventStore` from "./store":
//   new EventStore(rootDirectory: string)
//   append(record): Promise<void> | void   — appends one JSON line per record to
//                                            <root>/events.jsonl; every persisted
//                                            record carries the source `eventID`
//                                            (the event envelope id)
//   upsertAggregate(sessionID, aggregate)  — writes <root>/sessions/<sessionID>.json,
//                                            latest upsert wins
//   rebuild(): Promise<Record<sessionID, SessionAggregate>> | Record<...>
//                                          — reconstructs aggregates by replaying
//                                            events.jsonl through the aggregator
//                                            semantics (including the AC 7.3
//                                            rollup), deduplicating repeated
//                                            event ids (multi-instance safety)
//
// Fail-open: a store whose root is an invalid path must never throw, neither on
// construction nor on append — tracking must never break the host plugin.
//
// Record fixtures are deliberately untyped (`any`): the sibling modules do not
// exist yet and these red tests define their runtime contract.
import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { existsSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { EventStore } from "./store";
import { SessionAggregator } from "./aggregate";

let root: string;

beforeEach(() => {
  root = mkdtempSync(join(tmpdir(), "usage-tracking-store-"));
});

afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});

function sessionStartedRecord(sessionID: string, parentID: string | null, eventID: string): any {
  return {
    type: "session.started",
    eventID,
    sessionID,
    parentID,
    projectID: "proj_1",
    directory: "/tmp",
    agent: "build",
    model: { providerID: "anthropic" },
    ts: 1,
  };
}

function stepFinishedRecord(sessionID: string, partID: string, modelID: string, eventID: string): any {
  return {
    type: "step.finished",
    eventID,
    sessionID,
    messageID: `msg_${partID}`,
    partID,
    agent: "build",
    modelID,
    providerID: "anthropic",
    tokens: { input: 10, output: 5, reasoning: 1, cache: { read: 2, write: 3 } },
    cost: 0.1,
    ts: 2,
  };
}

function toolExecutedRecord(sessionID: string, eventID: string): any {
  return { type: "tool.executed", eventID, sessionID, tool: "read", ok: true };
}

describe("EventStore", () => {
  it("append() writes one JSON line per record, carrying its source eventID, to events.jsonl", async () => {
    const store = new EventStore(root);
    await store.append(stepFinishedRecord("sess_1", "p1", "model-a", "evt-step-1"));
    await store.append(toolExecutedRecord("sess_1", "evt-tool-1"));

    const content = readFileSync(join(root, "events.jsonl"), "utf8");
    const lines = content.split("\n").filter((line) => line.trim() !== "");
    expect(lines).toHaveLength(2);

    const first = JSON.parse(lines[0]);
    const second = JSON.parse(lines[1]);
    expect(first.type).toBe("step.finished");
    expect(first.eventID).toBe("evt-step-1");
    expect(first.sessionID).toBe("sess_1");
    expect(first.tokens.input).toBe(10);
    expect(second.type).toBe("tool.executed");
    expect(second.eventID).toBe("evt-tool-1");
    expect(second.tool).toBe("read");
  });

  it("upsertAggregate() writes sessions/<id>.json and the latest upsert wins", async () => {
    const store = new EventStore(root);
    await store.upsertAggregate("sess_1", { sessionID: "sess_1", tokens: { input: 10 } });
    await store.upsertAggregate("sess_1", { sessionID: "sess_1", tokens: { input: 25 } });

    const path = join(root, "sessions", "sess_1.json");
    expect(existsSync(path)).toBe(true);
    const parsed = JSON.parse(readFileSync(path, "utf8"));
    expect(parsed.sessionID).toBe("sess_1");
    expect(parsed.tokens.input).toBe(25);
  });

  it("rebuild() reconstructs the rolled-up aggregates from events.jsonl, deduplicating a repeated event id", async () => {
    const records = [
      sessionStartedRecord("parent", null, "evt-start-parent"),
      sessionStartedRecord("child", "parent", "evt-start-child"),
      stepFinishedRecord("parent", "p1", "model-a", "evt-step-parent-1"),
      stepFinishedRecord("child", "p2", "model-b", "evt-step-child-1"),
      toolExecutedRecord("child", "evt-tool-child-1"),
    ];
    const store = new EventStore(root);
    for (const record of records) {
      await store.append(record);
    }
    // Overlapping plugin instances append the same source event again:
    await store.append(stepFinishedRecord("child", "p2", "model-b", "evt-step-child-1"));

    // A fresh store instance must reconstruct state purely from disk.
    const rebuilt = await new EventStore(root).rebuild();

    // Oracle: replaying the deduplicated stream through a fresh aggregator.
    const expected = new SessionAggregator();
    for (const record of records) {
      expected.apply(record);
    }
    expect(rebuilt).toEqual(expected.finalize());

    // Rollup (FTD AC 7.3): the parent's tokens include the child's totals
    // (own 10 + child 10), despite the duplicated event id in the stream.
    expect(rebuilt["parent"].tokens.input).toBe(20);
    // The child's own record keeps its own totals only, counted once.
    expect(rebuilt["child"].tokens.input).toBe(10);
    expect(rebuilt["child"].toolCounts).toEqual({ read: 1 });
  });

  it("does not throw on append when the store root is an invalid path (fail-open)", async () => {
    // A regular file blocks any path beneath it (ENOTDIR on every write).
    const blocker = join(root, "blocker");
    writeFileSync(blocker, "not a directory");

    let threw = false;
    try {
      const store = new EventStore(join(blocker, "usage"));
      await store.append(stepFinishedRecord("sess_1", "p1", "model-a", "evt-step-1"));
    } catch {
      threw = true;
    }
    expect(threw).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Task 6 additions — review findings (code + security review, 2026-08-26):
// replay() as the restart-seeding seam — reads events.jsonl and yields the
// parsed records in file order (the store root is already project-scoped, so
// no project argument is needed). Malformed lines are skipped, consistent
// with rebuild()'s fail-open tolerance.
// ---------------------------------------------------------------------------

describe("EventStore — review findings (task 6)", () => {
  it("replay() reads events.jsonl and yields the records in order, skipping malformed lines", async () => {
    const store = new EventStore(root);
    await store.append(sessionStartedRecord("sess_1", null, "evt-start-1"));
    await store.append(stepFinishedRecord("sess_1", "p1", "model-a", "evt-step-1"));
    await store.append(toolExecutedRecord("sess_1", "evt-tool-1"));
    // A corrupted line in the stream must not break restart seeding.
    writeFileSync(join(root, "events.jsonl"), "{not-json\n", { flag: "a" });

    expect(typeof (store as any).replay).toBe("function");
    const records: any[] = await store.replay();

    expect(Array.isArray(records)).toBe(true);
    expect(records.map((record) => record.type)).toEqual([
      "session.started",
      "step.finished",
      "tool.executed",
    ]);
    // Full-fidelity records, in file order.
    expect(records[0].sessionID).toBe("sess_1");
    expect(records[0].eventID).toBe("evt-start-1");
    expect(records[1].partID).toBe("p1");
    expect(records[1].tokens.input).toBe(10);
    expect(records[2].tool).toBe("read");
  });
});

// ---------------------------------------------------------------------------
// Task 7 addition — NFR-06 visibility: the store must log exactly one warning
// (via the injected logger, fail-open) when the output root's storage
// footprint (events.jsonl growth + aggregate files) exceeds the 100 KB budget
// (102400 bytes); subsequent writes stay silent. FTD §11 NFR-06, tasks.md
// "Log a warning when a session's storage footprint exceeds 100 KB".
// ---------------------------------------------------------------------------

describe("EventStore — NFR-06 storage-footprint warning (task 7)", () => {
  it("logs exactly one warning mentioning path and byte size once the footprint exceeds 100 KB", async () => {
    const warnings: string[] = [];
    const store = new EventStore(root, (message) => warnings.push(message));
    const eventsPath = join(root, "events.jsonl");
    const eventsSize = () => (existsSync(eventsPath) ? statSync(eventsPath).size : 0);

    // Realistic driver: normal tool.executed records with distinct eventIDs
    // until events.jsonl alone passes the 100 KB budget (102400 bytes).
    let i = 0;
    while (eventsSize() <= 102400) {
      await store.append(toolExecutedRecord("sess_1", `evt-tool-${i}`));
      i += 1;
      if (i > 5000) throw new Error("events.jsonl never crossed the 100 KB budget");
    }

    expect(warnings).toHaveLength(1);
    const warning = warnings[0];
    if (warning === undefined) throw new Error("footprint warning missing");
    // The warning mentions the output root and the measured byte size.
    expect(warning).toContain(root);
    const measuredBytes = Number(/(\d+) bytes/.exec(warning)?.[1]);
    expect(measuredBytes).toBeGreaterThan(102400);

    // Subsequent appends and aggregate upserts add no second warning.
    await store.append(toolExecutedRecord("sess_1", `evt-tool-${i}`));
    await store.upsertAggregate("sess_1", { sessionID: "sess_1", tokens: { input: 1 } });
    expect(warnings).toHaveLength(1);
  });
});
