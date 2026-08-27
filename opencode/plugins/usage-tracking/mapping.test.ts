// Red test suite (Task 4) for the usage-tracking plugin's event → record mapping.
// Specification sources: task dispatch (2026-08-26 + follow-up), FTD
// docs/specs/opencode-usage-tracking/ftd-v1.0.md §11.1 (event-stream record
// schemas), verified event field map (spike-findings-and-decision.md), SDK
// types @opencode-ai/sdk 1.18.21.
//
// Contract under test — `mapEvent(event)` from "./mapping" takes an OpenCode
// event envelope `{ id, type, properties }` and returns a metadata-only record
// (discriminated by `type`, FTD §11.1) or nullish when the event yields no
// record:
//   session.created            → { type: "session.started", sessionID, parentID,
//                                  projectID, directory, agent, model, ts }
//   message.part.updated
//     part.type "step-finish"  → { type: "step.finished", sessionID, messageID
//                                  (from part.messageID), partID, agent?,
//                                  modelID?, providerID?, tokens { input, output,
//                                  reasoning, cache { read, write } }, cost, ts }
//   message.part.updated
//     part.type "tool"         → { type: "tool.executed", sessionID, tool, ok }
//                                  state.status "completed" → ok: true;
//                                  state.status "error" → ok: false and
//                                  status: "error"; pending/running → no record
//   session.idle               → { type: "session.idle", sessionID }
//   session.deleted            → { type: "session.deleted", sessionID } (log-only)
//
// Privacy invariant: no produced record may contain the keys "text", "prompt",
// "output" or "delta" at any depth. The single exception is the numeric token
// counter `tokens.output`. Event fixtures deliberately carry sensitive-looking
// tool state content (input/output/error/title/metadata) so leakage is detected.
//
// Fixtures are deliberately untyped (`any`): the sibling modules do not exist
// yet and these red tests define their runtime contract.
import { describe, it, expect } from "bun:test";
import { mapEvent } from "./mapping";

const FORBIDDEN_KEYS: string[] = ["text", "prompt", "output", "delta"];

/**
 * Recursively collects forbidden key paths. `tokens.output` (a number) is the
 * only permitted "output" key; every other occurrence is a privacy violation.
 */
function findForbiddenKeys(value: unknown, path: readonly string[] = []): string[] {
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => findForbiddenKeys(item, [...path, String(index)]));
  }
  if (value !== null && typeof value === "object") {
    const violations: string[] = [];
    for (const [key, child] of Object.entries(value)) {
      const childPath = [...path, key];
      const isTokenOutputCount =
        key === "output" && path[path.length - 1] === "tokens" && typeof child === "number";
      if (FORBIDDEN_KEYS.includes(key) && !isTokenOutputCount) {
        violations.push(childPath.join("."));
      }
      violations.push(...findForbiddenKeys(child, childPath));
    }
    return violations;
  }
  return [];
}

function expectPrivacyClean(record: unknown): void {
  expect(findForbiddenKeys(record)).toEqual([]);
}

const sessionCreatedEvent: any = {
  id: "evt-session-created-1",
  type: "session.created",
  properties: {
    sessionID: "sess_1",
    info: {
      id: "sess_1",
      slug: "sess-1",
      parentID: "sess_parent",
      projectID: "proj_1",
      directory: "/home/user/project",
      title: "Session title",
      agent: "build",
      model: { id: "claude-sonnet-4-5", providerID: "anthropic" },
      version: "1",
      time: { created: 1724670000, updated: 1724670001 },
    },
  },
};

const stepFinishEvent: any = {
  id: "evt-step-finish-1",
  type: "message.part.updated",
  properties: {
    sessionID: "sess_1",
    time: 1724670099,
    part: {
      id: "part_sf_1",
      sessionID: "sess_1",
      messageID: "msg_1",
      type: "step-finish",
      reason: "stop",
      cost: 0.0123,
      tokens: { input: 1200, output: 340, reasoning: 50, cache: { read: 8000, write: 900 } },
      // Part-level correlation candidates (spike: record when present).
      agent: "build",
      modelID: "claude-sonnet-4-5",
      providerID: "anthropic",
    },
  },
};

/** A tool part event whose state carries sensitive content, in a given status. */
function toolPartEvent(status: "pending" | "running" | "completed" | "error"): any {
  const part: any = {
    id: "part_tool_1",
    sessionID: "sess_1",
    messageID: "msg_1",
    type: "tool",
    callID: "call_1",
    tool: "read",
  };
  part.state =
    status === "completed"
      ? {
          status: "completed",
          input: { filePath: "/tmp/secret-input.txt" },
          output: "SECRET TOOL OUTPUT",
          title: "Read /tmp/secret-input.txt",
          metadata: { lines: 42 },
          time: { start: 1724670300, end: 1724670305 },
        }
      : status === "error"
        ? {
            status: "error",
            input: { filePath: "/tmp/secret-input.txt" },
            error: "SECRET ERROR DETAIL",
            time: { start: 1724670300, end: 1724670302 },
          }
        : {
            status,
            input: { filePath: "/tmp/secret-input.txt" },
            raw: "SECRET PENDING PAYLOAD",
          };
  return {
    id: `evt-tool-${status}`,
    type: "message.part.updated",
    properties: { sessionID: "sess_1", time: 1724670301, part },
  };
}

describe("mapEvent()", () => {
  it("maps session.created to a session.started record", () => {
    const record = mapEvent(sessionCreatedEvent);

    expect(record).not.toBeNull();
    expect(record.type).toBe("session.started");
    expect(record.sessionID).toBe("sess_1");
    expect(record.parentID).toBe("sess_parent");
    expect(record.projectID).toBe("proj_1");
    expect(record.directory).toBe("/home/user/project");
    expect(record.agent).toBe("build");
    expect(record.model).toBeInstanceOf(Object);
    expect(record.model.providerID).toBe("anthropic");
    expect(typeof record.ts).toBe("number");
    expectPrivacyClean(record);
  });

  it("maps a step-finish part to a step.finished record with correlation ids, tokens and cost", () => {
    const record = mapEvent(stepFinishEvent);

    expect(record).not.toBeNull();
    expect(record.type).toBe("step.finished");
    expect(record.sessionID).toBe("sess_1");
    // messageID must come from part.messageID, not from the envelope.
    expect(record.messageID).toBe("msg_1");
    expect(record.partID).toBe("part_sf_1");
    expect(record.agent).toBe("build");
    expect(record.modelID).toBe("claude-sonnet-4-5");
    expect(record.providerID).toBe("anthropic");
    expect(record.tokens).toEqual({
      input: 1200,
      output: 340,
      reasoning: 50,
      cache: { read: 8000, write: 900 },
    });
    expect(record.cost).toBe(0.0123);
    expect(record.ts).toBe(1724670099);
    expectPrivacyClean(record);
  });

  it("still maps a step-finish part that carries no agent/model candidates (tolerant parsing)", () => {
    const event: any = {
      id: "evt-step-finish-2",
      type: "message.part.updated",
      properties: {
        sessionID: "sess_1",
        time: 1724670200,
        part: {
          id: "part_sf_2",
          sessionID: "sess_1",
          messageID: "msg_2",
          type: "step-finish",
          reason: "stop",
          cost: 0.5,
          tokens: { input: 1, output: 2, reasoning: 3, cache: { read: 4, write: 5 } },
        },
      },
    };
    const record = mapEvent(event);

    expect(record).not.toBeNull();
    expect(record.type).toBe("step.finished");
    expect(record.sessionID).toBe("sess_1");
    expect(record.messageID).toBe("msg_2");
    expect(record.partID).toBe("part_sf_2");
    expect(record.tokens.input).toBe(1);
    expect(record.cost).toBe(0.5);
    // Absent candidates stay nullish (spike OQ-3: record when present, null otherwise).
    expect(record.agent ?? null).toBeNull();
    expect(record.modelID ?? null).toBeNull();
    expect(record.providerID ?? null).toBeNull();
    expectPrivacyClean(record);
  });

  it("emits no tool.executed record while the tool part is pending or running", () => {
    expect(mapEvent(toolPartEvent("pending")) ?? null).toBeNull();
    expect(mapEvent(toolPartEvent("running")) ?? null).toBeNull();
  });

  it("maps a completed tool part to a tool.executed record without tool content", () => {
    const record = mapEvent(toolPartEvent("completed"));

    expect(record).not.toBeNull();
    expect(record.type).toBe("tool.executed");
    expect(record.sessionID).toBe("sess_1");
    expect(record.tool).toBe("read");
    expect(record.ok).toBe(true);
    expectPrivacyClean(record);
  });

  it("maps an errored tool part to a tool.executed record with ok=false and status error", () => {
    const record = mapEvent(toolPartEvent("error"));

    expect(record).not.toBeNull();
    expect(record.type).toBe("tool.executed");
    expect(record.sessionID).toBe("sess_1");
    expect(record.tool).toBe("read");
    expect(record.ok).toBe(false);
    expect(record.status).toBe("error");
    expectPrivacyClean(record);
  });

  it("maps session.idle to a session.idle record", () => {
    const record = mapEvent({
      id: "evt-idle-1",
      type: "session.idle",
      properties: { sessionID: "sess_1" },
    } as any);

    expect(record).not.toBeNull();
    expect(record.type).toBe("session.idle");
    expect(record.sessionID).toBe("sess_1");
    expectPrivacyClean(record);
  });

  it("maps session.deleted to a session.deleted record (log-only)", () => {
    const record = mapEvent({
      id: "evt-session-deleted-1",
      type: "session.deleted",
      properties: {
        sessionID: "sess_1",
        info: { id: "sess_1", time: { created: 1724670000, updated: 1724670500 } },
      },
    } as any);

    expect(record).not.toBeNull();
    expect(record.type).toBe("session.deleted");
    expect(record.sessionID).toBe("sess_1");
    expectPrivacyClean(record);
  });
});

// ---------------------------------------------------------------------------
// Task 6 additions — review findings (code + security review, 2026-08-26).
// New record contracts pinned per the task-6 dispatch; event field shapes per
// the spike's verified field map (session.updated → info.title, message.updated
// → info.{id,agent,modelID|model.{modelID,providerID}}, message.part.updated
// part.type "step-start"). All records carry the source `eventID` like every
// other record family member; `ts` sources are pinned per type below.
// ---------------------------------------------------------------------------

const sessionUpdatedEvent: any = {
  id: "evt-session-updated-1",
  type: "session.updated",
  properties: {
    sessionID: "sess_1",
    info: {
      id: "sess_1",
      title: "Refactor the mapping layer",
      time: { created: 1724670000, updated: 1724670100 },
    },
  },
};

const messageUpdatedFlatModelEvent: any = {
  id: "evt-message-updated-1",
  type: "message.updated",
  properties: {
    sessionID: "sess_1",
    info: {
      id: "msg_1",
      sessionID: "sess_1",
      parentID: null,
      agent: "build",
      // Flat model fields (assistant messages, per spike).
      modelID: "claude-sonnet-4-5",
      providerID: "anthropic",
      cost: 0.02,
      tokens: { input: 10, output: 5, reasoning: 0, cache: { read: 0, write: 0 } },
      time: { created: 1724670050, completed: 1724670090 },
    },
  },
};

const messageUpdatedNestedModelEvent: any = {
  id: "evt-message-updated-2",
  type: "message.updated",
  properties: {
    sessionID: "sess_1",
    info: {
      id: "msg_0",
      sessionID: "sess_1",
      agent: "build",
      // Nested model fields (user messages, per spike).
      model: { modelID: "gpt-5", providerID: "openai" },
      time: { created: 1724670040 },
    },
  },
};

const stepStartPartEvent: any = {
  id: "evt-step-start-1",
  type: "message.part.updated",
  properties: {
    sessionID: "sess_1",
    time: 1724670080,
    part: { id: "part_ss_1", sessionID: "sess_1", messageID: "msg_1", type: "step-start" },
  },
};

describe("mapEvent() — review findings (task 6)", () => {
  it("maps session.updated to a persisted session.title record (metadata-only: title is the only free-text field)", () => {
    const record = mapEvent(sessionUpdatedEvent);

    expect(record).not.toBeNull();
    expect(record.type).toBe("session.title");
    expect(record.eventID).toBe("evt-session-updated-1");
    expect(record.sessionID).toBe("sess_1");
    expect(record.title).toBe("Refactor the mapping layer");
    // ts pinned to info.time.updated (the session's own update timestamp).
    expect(record.ts).toBe(1724670100);
    // Metadata-only: exactly these keys — no other free-text field may ride along.
    expect(Object.keys(record).sort()).toEqual(["eventID", "sessionID", "title", "ts", "type"]);
    expectPrivacyClean(record);
  });

  it("carries info.title on the session.started record when present", () => {
    const record = mapEvent(sessionCreatedEvent);

    expect(record).not.toBeNull();
    expect(record.title).toBe("Session title");
    expectPrivacyClean(record);
  });

  it("leaves the session.started title nullish when info.title is absent", () => {
    const event: any = {
      id: "evt-session-created-no-title",
      type: "session.created",
      properties: {
        sessionID: "sess_2",
        info: { id: "sess_2", time: { created: 1724670000 } },
      },
    };
    const record = mapEvent(event);

    expect(record).not.toBeNull();
    expect(record.title ?? null).toBeNull();
  });

  it("maps message.updated to an internal message.info record (model from flat fields)", () => {
    const record = mapEvent(messageUpdatedFlatModelEvent);

    expect(record).not.toBeNull();
    expect(record.type).toBe("message.info");
    expect(record.eventID).toBe("evt-message-updated-1");
    expect(record.sessionID).toBe("sess_1");
    expect(record.messageID).toBe("msg_1");
    expect(record.modelID).toBe("claude-sonnet-4-5");
    expect(record.providerID).toBe("anthropic");
    expect(record.agent).toBe("build");
    // ts pinned to info.time.created.
    expect(record.ts).toBe(1724670050);
    // Internal record shape: the message's tokens/cost must NOT ride along.
    expect(Object.keys(record).sort()).toEqual([
      "agent",
      "eventID",
      "messageID",
      "modelID",
      "providerID",
      "sessionID",
      "ts",
      "type",
    ]);
    expectPrivacyClean(record);
  });

  it("maps message.updated to a message.info record reading the model from nested fields", () => {
    const record = mapEvent(messageUpdatedNestedModelEvent);

    expect(record).not.toBeNull();
    expect(record.type).toBe("message.info");
    expect(record.eventID).toBe("evt-message-updated-2");
    expect(record.sessionID).toBe("sess_1");
    expect(record.messageID).toBe("msg_0");
    expect(record.modelID).toBe("gpt-5");
    expect(record.providerID).toBe("openai");
    expect(record.agent).toBe("build");
    expect(record.ts).toBe(1724670040);
    expectPrivacyClean(record);
  });

  it("maps a step-start part to an internal step.started record", () => {
    const record = mapEvent(stepStartPartEvent);

    expect(record).not.toBeNull();
    expect(record.type).toBe("step.started");
    expect(record.eventID).toBe("evt-step-start-1");
    expect(record.sessionID).toBe("sess_1");
    expect(record.messageID).toBe("msg_1");
    expect(record.partID).toBe("part_ss_1");
    // ts pinned to properties.time (same source as step-finish parts).
    expect(record.ts).toBe(1724670080);
    expect(Object.keys(record).sort()).toEqual([
      "eventID",
      "messageID",
      "partID",
      "sessionID",
      "ts",
      "type",
    ]);
    expectPrivacyClean(record);
  });

  it("carries partID on tool.executed records (completed and error)", () => {
    const completed = mapEvent(toolPartEvent("completed"));
    expect(completed).not.toBeNull();
    expect(completed.partID).toBe("part_tool_1");

    const errored = mapEvent(toolPartEvent("error"));
    expect(errored).not.toBeNull();
    expect(errored.partID).toBe("part_tool_1");
  });
});
