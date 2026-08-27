// Red test suite (Task 6) for the usage-tracking plugin's status tracker and
// the aggregator's eviction surface. Specification sources: task-6 dispatch
// (code + security review findings 15–16, 2026-08-26).
//
// Contract under test:
//   StatusTracker.recordSessionWritten(sessionID) — `sessionsWritten` counts
//   DISTINCT session ids: re-upserting the same session must not grow the
//   counter (two upserts for one session = 1).
//   SessionAggregator.evict(sessionID) — after a session's aggregate has been
//   finalized and upserted, the aggregator can drop the session's internal
//   state; subsequent finalize() calls no longer report it. Evicting an
//   unknown id is a tolerated no-op.
//
// Both findings address the same review concern: unbounded in-memory growth in
// long-running hosts (the status counter must not over-report, and finalized
// sessions must be reclaimable).
import { describe, it, expect } from "bun:test";
import { StatusTracker } from "./status";
import { SessionAggregator } from "./aggregate";

describe("StatusTracker — review findings (task 6)", () => {
  it("sessionsWritten counts distinct session ids (two upserts of the same session count once)", () => {
    const tracker = new StatusTracker("/tmp/usage-tracking-status", new SessionAggregator());

    tracker.recordSessionWritten("sess_1");
    // The same session's aggregate is upserted again (e.g. another step).
    tracker.recordSessionWritten("sess_1");
    tracker.recordSessionWritten("sess_2");

    const snapshot = tracker.snapshot();
    expect(snapshot.sessionsWritten).toBe(2);
    expect(snapshot.outputPath).toBe("/tmp/usage-tracking-status");
  });
});

describe("SessionAggregator.evict() — review findings (task 6)", () => {
  it("removes a finalized session from subsequent finalize() output; unknown ids do not throw", () => {
    const aggregator = new SessionAggregator();
    aggregator.apply({
      type: "session.started",
      eventID: "evt-start-1",
      sessionID: "sess_evict",
      parentID: null,
      projectID: "proj_1",
      directory: "/tmp",
      agent: "build",
      model: null,
      ts: 1,
    });
    expect(Object.hasOwn(aggregator.finalize(), "sess_evict")).toBe(true);

    // Minimal eviction surface: after finalize + upsert the caller may drop
    // the session's in-memory state.
    expect(typeof (aggregator as any).evict).toBe("function");
    aggregator.evict("sess_evict");
    expect(Object.hasOwn(aggregator.finalize(), "sess_evict")).toBe(false);

    // Evicting a session that was never seen is a tolerated no-op.
    expect(() => aggregator.evict("never-existed")).not.toThrow();
  });
});
