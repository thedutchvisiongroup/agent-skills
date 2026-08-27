// Red test suite (Task 4) for the usage-tracking plugin's session aggregation.
// Specification sources: task dispatch (2026-08-26 + follow-ups), FTD
// docs/specs/opencode-usage-tracking/ftd-v1.0.md §11.2 (aggregate schema) and
// AC 7.3 (rollup semantics), spike findings (child rollup via parentID,
// event-ID deduplication for multi-instance safety), plan.md Task 4.
//
// Contract under test — `SessionAggregator` from "./aggregate":
//   new SessionAggregator()
//   apply(record, sourceEventID?): void
//       — consumes mapped records (see mapping.test.ts); the optional second
//         argument is the source event envelope id. A record delivered under an
//         already-seen source event id is ignored (event-ID deduplication, the
//         multi-instance safety guarantee from the spike decision).
//   finalize(): Record<sessionID, SessionAggregate>
//
// SessionAggregate fields pinned by these tests (FTD §11.2, AC 7.3):
//   tokens      — summed step.finished tokens with flat cache fields
//                 { input, output, reasoning, cacheRead, cacheWrite }. For a
//                 parent session this INCLUDES the rolled-up totals of all
//                 descendant sessions (own steps + child totals, recursively);
//                 a child's own record keeps its own totals only.
//   cost        — same rollup rule as tokens (own steps + child totals).
//   models      — distinct models as objects carrying at least `id`
//                 (FTD §11.2: [{ id, provider, variant }]).
//   toolCounts  — Record<toolName, count> of tool.executed records.
//   children    — on a parent, separately complete per-child records (own
//                 totals only), per FTD AC 7.3 / §11.2.
//   depth       — 0 for a root session, +1 per parentID chain link.
//
// Record fixtures are deliberately untyped (`any`): the sibling modules do not
// exist yet and these red tests define their runtime contract.
import { describe, it, expect } from "bun:test";
import { SessionAggregator } from "./aggregate";
import { mapEvent } from "./mapping";

const TOKENS_P = { input: 50, output: 20, reasoning: 5, cache: { read: 200, write: 10 } };
const TOKENS_A = { input: 100, output: 40, reasoning: 10, cache: { read: 500, write: 60 } };
const TOKENS_B = { input: 25, output: 15, reasoning: 5, cache: { read: 50, write: 6 } };

function sessionStarted(sessionID: string, parentID: string | null): any {
  return {
    type: "session.started",
    sessionID,
    parentID,
    projectID: "proj_1",
    directory: "/home/user/project",
    agent: "build",
    model: { providerID: "anthropic" },
    ts: 1,
  };
}

function stepFinished(sessionID: string, modelID: string, tokens: unknown, partID: string): any {
  return {
    type: "step.finished",
    sessionID,
    messageID: `msg_${partID}`,
    partID,
    agent: "build",
    modelID,
    providerID: "anthropic",
    tokens,
    // Dyadic value so summed costs stay float-exact under toBe().
    cost: 0.25,
    ts: 2,
  };
}

function toolExecuted(sessionID: string, tool: string): any {
  return { type: "tool.executed", sessionID, tool, ok: true };
}

describe("SessionAggregator", () => {
  it("sums tokens and collects every model of a session's step.finished records", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p1"));
    aggregator.apply(stepFinished("sess_1", "model-b", TOKENS_B, "p2"));

    const aggregate = aggregator.finalize()["sess_1"];

    expect(aggregate.tokens).toEqual({
      input: 125,
      output: 55,
      reasoning: 15,
      cacheRead: 550,
      cacheWrite: 66,
    });
    const modelIDs = aggregate.models.map((model: any) => model.id);
    expect(modelIDs).toHaveLength(2);
    expect(modelIDs).toContain("model-a");
    expect(modelIDs).toContain("model-b");
  });

  it("counts a tool once when its part is observed repeatedly (pending → completed)", () => {
    const aggregator = new SessionAggregator();
    const toolPartEvent = (status: string): any => ({
      id: `evt-tool-${status}`,
      type: "message.part.updated",
      properties: {
        sessionID: "sess_1",
        time: 3,
        part: {
          id: "part_tool_1",
          sessionID: "sess_1",
          messageID: "msg_1",
          type: "tool",
          callID: "call_1",
          tool: "read",
          state: {
            status,
            ...(status === "completed" ? { time: { start: 1, end: 2 } } : {}),
          },
        },
      },
    });

    // The same tool part first arrives as pending, later as completed; only the
    // completed observation may produce a tool.executed record.
    for (const event of [toolPartEvent("pending"), toolPartEvent("completed")]) {
      const record = mapEvent(event);
      if (record != null) {
        aggregator.apply(record);
      }
    }

    const aggregate = aggregator.finalize()["sess_1"];
    expect(aggregate.toolCounts).toEqual({ read: 1 });
  });

  it("counts a twice-delivered record with the same source event id only once (multi-instance safety)", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p1"), "evt-step-1");
    aggregator.apply(toolExecuted("sess_1", "read"), "evt-tool-1");
    const before = aggregator.finalize();

    // The same source events delivered again (overlapping plugin instances or
    // source re-delivery) must be ignored entirely.
    aggregator.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p1"), "evt-step-1");
    aggregator.apply(toolExecuted("sess_1", "read"), "evt-tool-1");

    const after = aggregator.finalize();
    expect(after).toEqual(before);

    const aggregate = after["sess_1"];
    // Tokens counted once, not doubled.
    expect(aggregate.tokens.input).toBe(100);
    // Tool counted once.
    expect(aggregate.toolCounts).toEqual({ read: 1 });
    // Models list has no duplicate entries.
    expect(aggregate.models.map((model: any) => model.id)).toEqual(["model-a"]);
  });

  it("counts records delivered under different source event ids", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p1"), "evt-step-1");
    aggregator.apply(stepFinished("sess_1", "model-b", TOKENS_B, "p2"), "evt-step-2");

    const aggregate = aggregator.finalize()["sess_1"];
    expect(aggregate.tokens.input).toBe(125);
    const modelIDs = aggregate.models.map((model: any) => model.id);
    expect(modelIDs).toHaveLength(2);
    expect(modelIDs).toContain("model-a");
    expect(modelIDs).toContain("model-b");

    // Oracle: distinct source event ids behave exactly like id-less application.
    const oracle = new SessionAggregator();
    oracle.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p1"));
    oracle.apply(stepFinished("sess_1", "model-b", TOKENS_B, "p2"));
    expect(aggregator.finalize()).toEqual(oracle.finalize());
  });

  it("rolls child totals into the parent's tokens and cost via parentID and tracks depth by chain", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(sessionStarted("parent", null));
    aggregator.apply(sessionStarted("child", "parent"));
    aggregator.apply(sessionStarted("grandchild", "child"));
    aggregator.apply(stepFinished("parent", "model-p", TOKENS_P, "p0"));
    aggregator.apply(stepFinished("child", "model-a", TOKENS_A, "p1"));
    aggregator.apply(stepFinished("grandchild", "model-b", TOKENS_B, "p2"));

    const aggregates = aggregator.finalize();
    const parent = aggregates["parent"];
    const child = aggregates["child"];
    const grandchild = aggregates["grandchild"];

    // The parent's tokens and cost are its own steps plus the rolled-up totals
    // of all descendant sessions (FTD AC 7.3): 50 + 100 + 25 input, 3 × 0.25 cost.
    expect(parent.tokens).toEqual({
      input: 175,
      output: 75,
      reasoning: 20,
      cacheRead: 750,
      cacheWrite: 76,
    });
    expect(parent.cost).toBe(0.75);

    // A child's own record keeps its own totals only.
    expect(child.tokens.input).toBe(100);
    expect(child.cost).toBe(0.25);
    expect(grandchild.tokens.input).toBe(25);

    // Children remain separately complete records in the parent's children
    // list, with their own (non-rolled-up) totals.
    const childEntry = parent.children.find((entry: any) => entry.sessionID === "child");
    expect(childEntry).toBeDefined();
    expect(childEntry.tokens.input).toBe(100);

    // Depth follows the parentID chain: root 0, child 1, grandchild 2.
    expect(parent.depth).toBe(0);
    expect(child.depth).toBe(1);
    expect(grandchild.depth).toBe(2);
  });

  it("is idempotent: finalize() returns the same aggregates on repeated calls", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p1"));

    const first = aggregator.finalize();
    const second = aggregator.finalize();

    expect(second).toEqual(first);
    // Repeated finalization must not double-count.
    expect(second["sess_1"].tokens.input).toBe(100);
  });
});

// ---------------------------------------------------------------------------
// Task 6 additions — review findings (code + security review, 2026-08-26).
// New aggregator contracts pinned per the task-6 dispatch: session.title
// records, message.info attribution via messageID join, session.started model
// baseline, project/directory on the serialized aggregate, step.started →
// step.finished stepMs computation, toolCounts partID dedup across event ids,
// and Map/null-prototype semantics for hostile "__proto__" ids.
// ---------------------------------------------------------------------------

describe("SessionAggregator — review findings (task 6)", () => {
  it("sets the aggregate title from session.title records: later wins, non-empty only", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(sessionStarted("sess_title", null));

    aggregator.apply({
      type: "session.title",
      eventID: "evt-title-1",
      sessionID: "sess_title",
      title: "First title",
      ts: 10,
    });
    expect(aggregator.finalize()["sess_title"].title).toBe("First title");

    // A later title supersedes an earlier one.
    aggregator.apply({
      type: "session.title",
      eventID: "evt-title-2",
      sessionID: "sess_title",
      title: "Second title",
      ts: 20,
    });
    expect(aggregator.finalize()["sess_title"].title).toBe("Second title");

    // An empty title must not clear a previously observed title.
    aggregator.apply({
      type: "session.title",
      eventID: "evt-title-3",
      sessionID: "sess_title",
      title: "",
      ts: 30,
    });
    expect(aggregator.finalize()["sess_title"].title).toBe("Second title");
  });

  it("attributes a step.finished's unknown model via its message.info (messageID join)", () => {
    const aggregator = new SessionAggregator();
    // A step whose model is unknown (no modelID on the part): its tokens count,
    // but the model stays unattributed…
    aggregator.apply({
      type: "step.finished",
      eventID: "evt-step-unattributed",
      sessionID: "sess_1",
      messageID: "msg_1",
      partID: "p1",
      agent: null,
      modelID: null,
      providerID: null,
      tokens: TOKENS_A,
      cost: 0.25,
      ts: 2,
    });
    expect(aggregator.finalize()["sess_1"].models).toEqual([]);

    // …until the message's info arrives; then the models list contains it and
    // the agent is attributed to the session.
    aggregator.apply({
      type: "message.info",
      eventID: "evt-message-info-1",
      sessionID: "sess_1",
      messageID: "msg_1",
      modelID: "model-x",
      providerID: "anthropic",
      agent: "plan",
      ts: 3,
    });
    const aggregate = aggregator.finalize()["sess_1"];
    const entry = aggregate.models.find((model: any) => model.id === "model-x");
    expect(entry).toEqual({ id: "model-x", provider: "anthropic", variant: null });
    expect(aggregate.agents).toContain("plan");
    // The step's tokens were counted all along.
    expect(aggregate.tokens.input).toBe(100);
  });

  it("lands the session.started model in the models list as baseline", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply({
      ...sessionStarted("sess_1", null),
      model: { id: "model-s", providerID: "anthropic", variant: null },
    });

    const aggregate = aggregator.finalize()["sess_1"];
    const entry = aggregate.models.find((model: any) => model.id === "model-s");
    expect(entry).toEqual({ id: "model-s", provider: "anthropic", variant: null });
  });

  it("stores project and directory on the serialized aggregate", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(sessionStarted("sess_1", null));

    const aggregate = aggregator.finalize()["sess_1"];
    expect(aggregate.project).toBe("proj_1");
    expect(aggregate.directory).toBe("/home/user/project");
  });

  it("computes stepMs from the step.started → step.finished ts difference and accumulates activeMs", () => {
    const aggregator = new SessionAggregator();
    const stepStartedAt = (partID: string, ts: number): any => ({
      type: "step.started",
      eventID: `evt-ss-${partID}`,
      sessionID: "sess_1",
      messageID: `msg_${partID}`,
      partID,
      ts,
    });
    const stepFinishedAt = (partID: string, ts: number): any => ({
      ...stepFinished("sess_1", "model-a", TOKENS_A, partID),
      eventID: `evt-sf-${partID}`,
      ts,
    });

    aggregator.apply(stepStartedAt("p1", 1000));
    // activeMs stays 0 until the step finishes: stepMs is computed on the
    // step.finished application, not on step.started.
    expect(aggregator.finalize()["sess_1"]?.activeMs ?? 0).toBe(0);
    aggregator.apply(stepFinishedAt("p1", 3000));
    expect(aggregator.finalize()["sess_1"].activeMs).toBe(2000);

    // A second step accumulates on top of the first.
    aggregator.apply(stepStartedAt("p2", 4000));
    aggregator.apply(stepFinishedAt("p2", 4500));
    expect(aggregator.finalize()["sess_1"].activeMs).toBe(2500);
  });

  it("contributes 0 activeMs to a step.finished that never saw its step.started", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p9"));

    expect(aggregator.finalize()["sess_1"].activeMs).toBe(0);
  });

  it("dedups toolCounts by partID across different source event ids", () => {
    const aggregator = new SessionAggregator();
    const toolPartCompleted = (envelopeID: string): any => ({
      id: envelopeID,
      type: "message.part.updated",
      properties: {
        sessionID: "sess_1",
        time: 3,
        part: {
          id: "part_tool_dedup",
          sessionID: "sess_1",
          messageID: "msg_1",
          type: "tool",
          callID: "call_1",
          tool: "read",
          state: { status: "completed" },
        },
      },
    });

    // The same tool part delivered under two different event ids (e.g. two
    // plugin instances mapping the same part observation) counts once.
    for (const envelopeID of ["evt-tool-dedup-a", "evt-tool-dedup-b"]) {
      const record = mapEvent(toolPartCompleted(envelopeID));
      if (record != null) {
        aggregator.apply(record, envelopeID);
      }
    }

    expect(aggregator.finalize()["sess_1"].toolCounts).toEqual({ read: 1 });
  });

  it("tracks a sessionID and tool name literally named __proto__ without polluting Object.prototype", () => {
    const protoKeysBefore = Object.getOwnPropertyNames(Object.prototype);
    const aggregator = new SessionAggregator();
    aggregator.apply({
      type: "session.started",
      eventID: "evt-proto-1",
      sessionID: "__proto__",
      parentID: null,
      projectID: "proj_1",
      directory: "/tmp",
      agent: "build",
      model: null,
      ts: 1,
    });
    aggregator.apply({
      type: "tool.executed",
      eventID: "evt-proto-2",
      sessionID: "__proto__",
      tool: "__proto__",
      ok: true,
    });

    const aggregates = aggregator.finalize();
    // No prototype pollution: Object.prototype gains nothing, fresh objects
    // stay clean.
    expect(Object.getOwnPropertyNames(Object.prototype)).toEqual(protoKeysBefore);
    expect(({} as any).sessionID).toBeUndefined();
    expect(({} as any).toolCounts).toBeUndefined();

    // The hostile-named session is still tracked (own property, not a
    // prototype hop).
    expect(Object.hasOwn(aggregates, "__proto__")).toBe(true);
    const aggregate = Object.getOwnPropertyDescriptor(aggregates, "__proto__")?.value;
    expect(aggregate).toBeDefined();
    // The hostile-named tool is still counted (own property on toolCounts).
    expect(Object.hasOwn(aggregate.toolCounts, "__proto__")).toBe(true);
    expect(Object.getOwnPropertyDescriptor(aggregate.toolCounts, "__proto__")?.value).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// v11 additions — dispatch 2026-08-27 (three approved changes), RED tests:
//
// (1) activeMs pairing fix: step-start and step-finish are DIFFERENT parts
//     (verified live: prt_03df0185… start vs prt_03df0221… finish, same
//     session + messageID), so pairing by partID never matches live data.
//     Pairing must key on (sessionID, messageID); multiple steps of one
//     message pair FIFO. A finish without a start still contributes 0
//     (already pinned by the task-6 suite above).
//
// (2) device block on serialized session aggregates: exactly
//     {name, opencodeVersion} when device info is provided to the
//     aggregator, null when absent (fail-open). Spec decision: device info
//     is injected via the SessionAggregator constructor (single injection
//     point, backward compatible); os/osVersion are overview-level only.
//     See reports/v11-red-tests.md for all recorded spec decisions.
// ---------------------------------------------------------------------------

describe("SessionAggregator — activeMs pairing fix (v11)", () => {
  it("pairs step.started → step.finished by messageID when the partIDs differ (live-data shape)", () => {
    const aggregator = new SessionAggregator();
    // The verified live shape: the step-start part and the step-finish part
    // are different parts (different partIDs) of the SAME message.
    aggregator.apply({
      type: "step.started",
      eventID: "evt-v11-ss-1",
      sessionID: "sess_1",
      messageID: "msg_1",
      partID: "prt_start_03df0185",
      ts: 1000,
    });
    aggregator.apply({
      type: "step.finished",
      eventID: "evt-v11-sf-1",
      sessionID: "sess_1",
      messageID: "msg_1",
      partID: "prt_finish_03df0221",
      agent: "build",
      modelID: "model-a",
      providerID: "anthropic",
      tokens: TOKENS_A,
      cost: 0.25,
      ts: 3000,
    });

    // T2 − T1 = 3000 − 1000, despite the mismatched partIDs.
    expect(aggregator.finalize()["sess_1"].activeMs).toBe(2000);
  });

  it("pairs multiple steps of one message FIFO: two starts, then two finishes, then an unpaired finish", () => {
    const aggregator = new SessionAggregator();
    const stepStarted = (partID: string, ts: number): any => ({
      type: "step.started",
      eventID: `evt-v11-ss-${partID}`,
      sessionID: "sess_1",
      messageID: "msg_1",
      partID,
      ts,
    });
    const stepFinished = (partID: string, ts: number): any => ({
      type: "step.finished",
      eventID: `evt-v11-sf-${partID}`,
      sessionID: "sess_1",
      messageID: "msg_1",
      partID,
      agent: "build",
      modelID: "model-a",
      providerID: "anthropic",
      tokens: TOKENS_A,
      cost: 0.25,
      ts,
    });

    // One message running two sequential steps; both starts are observed
    // before the finishes arrive (dispatch scenario).
    aggregator.apply(stepStarted("prt_s1", 1000));
    aggregator.apply(stepStarted("prt_s2", 2000));
    aggregator.apply(stepFinished("prt_f1", 2500));
    aggregator.apply(stepFinished("prt_f2", 4000));

    // FIFO: the first finish closes the first start (2500−1000), the second
    // closes the second (4000−2000).
    expect(aggregator.finalize()["sess_1"].activeMs).toBe(1500 + 2000);

    // A third finish finds no unconsumed start left: contributes 0.
    aggregator.apply(stepFinished("prt_f3", 5000));
    expect(aggregator.finalize()["sess_1"].activeMs).toBe(3500);
  });
});

describe("SessionAggregator — device block (v11)", () => {
  it("carries device {name, opencodeVersion} on serialized aggregates when device info is provided", () => {
    const aggregator = new SessionAggregator({ name: "thim-desktop", opencodeVersion: "1.18.21" });
    aggregator.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p1"));

    const aggregate = aggregator.finalize()["sess_1"];
    expect(aggregate.device).toEqual({ name: "thim-desktop", opencodeVersion: "1.18.21" });
  });

  it("serializes device as null when no device info was provided (fail-open)", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply(stepFinished("sess_1", "model-a", TOKENS_A, "p1"));

    expect(aggregator.finalize()["sess_1"].device).toBe(null);
  });
});
