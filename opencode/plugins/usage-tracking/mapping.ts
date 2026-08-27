/**
 * Event-to-record mapping for the usage-tracking plugin.
 *
 * Second stage of the pipeline (config → mapping → aggregate → store, wired by
 * `index.ts`): normalizes OpenCode's live event-bus envelopes into flat
 * `UsageRecord` shapes. All field extraction is defensive — every field is
 * nullable and a malformed event yields `null` instead of throwing
 * (fail-open, ADR-05). Records are metadata-only (ADR-06): ids, names,
 * token counts, costs, timestamps, title — never message content, prompts,
 * or tool outputs.
 */

/**
 * OpenCode event-bus envelope as the live runtime delivers it: `{id, type,
 * properties}`. The SDK's static Event type lacks `id`, so every field is
 * `unknown` and validated at read time.
 */
export type UsageEventEnvelope = {
  id?: unknown;
  type?: unknown;
  properties?: unknown;
};

/** Model attribution extracted from `session.started` (all fields nullable). */
export type ModelInfo = {
  id: string | null;
  providerID: string | null;
  variant: string | null;
};

/** Token counts as reported by a `step-finish` part; missing counters default to 0. */
export type TokenCounts = {
  input: number;
  output: number;
  reasoning: number;
  cache: { read: number; write: number };
};

/** Persisted record for `session.created`: session identity, parent, project, agent, model, title. */
export type SessionStartedRecord = {
  type: "session.started";
  eventID: string | null;
  sessionID: string | null;
  parentID: string | null;
  projectID: string | null;
  directory: string | null;
  agent: string | null;
  model: ModelInfo | null;
  title: string | null;
  ts: number | null;
};

/** Persisted record for `session.updated`: latest known session title (the only free-text field, ADR-06). */
export type SessionTitleRecord = {
  type: "session.title";
  eventID: string | null;
  sessionID: string | null;
  title: string | null;
  ts: number | null;
};

/**
 * Internal (non-persisted) record for `message.updated`: per-message model,
 * provider, and agent attribution. Feeds the live aggregator only.
 */
export type MessageInfoRecord = {
  type: "message.info";
  eventID: string | null;
  sessionID: string | null;
  messageID: string | null;
  modelID: string | null;
  providerID: string | null;
  agent: string | null;
  ts: number | null;
};

/** Internal (non-persisted) record for a `step-start` part: opens the active-time window for a step. */
export type StepStartedRecord = {
  type: "step.started";
  eventID: string | null;
  sessionID: string | null;
  messageID: string | null;
  partID: string | null;
  ts: number | null;
};

/** Persisted record for a `step-finish` part: tokens, cost, and model/agent attribution for one step. */
export type StepFinishedRecord = {
  type: "step.finished";
  eventID: string | null;
  sessionID: string | null;
  messageID: string | null;
  partID: string | null;
  agent: string | null;
  modelID: string | null;
  providerID: string | null;
  tokens: TokenCounts;
  cost: number;
  ts: number | null;
};

/** Persisted record for a terminal `tool` part state (completed or error). */
export type ToolExecutedRecord = {
  type: "tool.executed";
  eventID: string | null;
  sessionID: string | null;
  tool: string | null;
  partID: string | null;
  ok: boolean;
  status?: "error";
};

/** Persisted marker that a session went idle (turn finished); no payload beyond ids. */
export type SessionIdleRecord = {
  type: "session.idle";
  eventID: string | null;
  sessionID: string | null;
};

/**
 * Persisted marker that a session was deleted; the store's write path uses it
 * to stop updating that session's aggregate.
 */
export type SessionDeletedRecord = {
  type: "session.deleted";
  eventID: string | null;
  sessionID: string | null;
};

/**
 * Union of all normalized record types produced by `mapEvent`. Records with a
 * `type` in `INTERNAL_RECORD_TYPES` feed the live aggregator but are never
 * persisted; all others are the persisted event stream (ADR-02 layer 1).
 */
export type UsageRecord =
  | SessionStartedRecord
  | SessionTitleRecord
  | MessageInfoRecord
  | StepStartedRecord
  | StepFinishedRecord
  | ToolExecutedRecord
  | SessionIdleRecord
  | SessionDeletedRecord;

// Internal record types feed the live aggregator but are derivable from the
// persisted event stream, so the write path must filter them from persistence.
/** Record types that live in memory only: `message.info` and `step.started`. */
export const INTERNAL_RECORD_TYPES: ReadonlySet<string> = new Set([
  "message.info",
  "step.started",
]);

function asRecord(value: unknown): Record<string, unknown> | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  return value as Record<string, unknown>;
}

/**
 * Tests whether a value is an internal (non-persisted) record: a plain object
 * whose `type` is in `INTERNAL_RECORD_TYPES`.
 *
 * @param record - Any value; non-records and persisted record types return false.
 */
export function isInternalRecord(record: unknown): boolean {
  const fields = asRecord(record);
  return fields !== null && typeof fields.type === "string" && INTERNAL_RECORD_TYPES.has(fields.type);
}

function asString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

/**
 * Maps one OpenCode event-bus envelope to a normalized `UsageRecord`.
 *
 * Dispatches on `envelope.type` (`session.created`, `session.updated`,
 * `message.updated`, `message.part.updated`, `session.idle`,
 * `session.deleted`); everything else is not consumed. The whole mapping is
 * wrapped in try/catch — any unexpected shape yields `null`, never a throw
 * (fail-open, ADR-05).
 *
 * @param event - The live envelope `{id, type, properties}` (see
 *   `UsageEventEnvelope`); `properties` carries the payload (`info`, `part`,
 *   `sessionID`, `time`).
 * @returns The normalized record, or `null` when the event is not consumed
 *   (unknown type, unparseable payload, or a mapped record that lacks its
 *   session identity).
 */
export function mapEvent(event: UsageEventEnvelope | null | undefined): any {
  try {
    const envelope = asRecord(event);
    if (envelope === null) return null;
    const properties = asRecord(envelope.properties);
    const eventType = typeof envelope.type === "string" ? envelope.type : null;

    if (eventType === "session.created") {
      return mapSessionCreated(envelope, properties);
    }
    if (eventType === "session.updated") {
      return mapSessionUpdated(envelope, properties);
    }
    if (eventType === "message.updated") {
      return mapMessageUpdated(envelope, properties);
    }
    if (eventType === "message.part.updated") {
      return mapMessagePartUpdated(envelope, properties);
    }
    if (eventType === "session.idle" || eventType === "session.deleted") {
      const sessionID =
        asString(properties?.sessionID) ?? asString(asRecord(properties?.info)?.id);
      if (eventType === "session.idle") {
        return { type: "session.idle", eventID: asString(envelope.id), sessionID };
      }
      return { type: "session.deleted", eventID: asString(envelope.id), sessionID };
    }
    return null;
  } catch {
    return null;
  }
}

/** Maps `session.created`: identity from `properties.info`, model from `info.model` (falling back to `info.modelID`/`info.variant`). */
function mapSessionCreated(
  envelope: Record<string, unknown>,
  properties: Record<string, unknown> | null,
): SessionStartedRecord {
  const info = asRecord(properties?.info);
  const modelSource = asRecord(info?.model);
  return {
    type: "session.started",
    eventID: asString(envelope.id),
    sessionID: asString(properties?.sessionID) ?? asString(info?.id),
    parentID: asString(info?.parentID),
    projectID: asString(info?.projectID),
    directory: asString(info?.directory),
    agent: asString(info?.agent),
    model:
      modelSource === null
        ? null
        : {
            id: asString(modelSource.id) ?? asString(info?.modelID),
            providerID: asString(modelSource.providerID),
            variant: asString(modelSource.variant) ?? asString(info?.variant),
          },
    title: asString(info?.title),
    ts: asNumber(asRecord(info?.time)?.created),
  };
}

/** Maps `session.updated` to a title record; returns null when no sessionID is derivable. */
function mapSessionUpdated(
  envelope: Record<string, unknown>,
  properties: Record<string, unknown> | null,
): SessionTitleRecord | null {
  const info = asRecord(properties?.info);
  const sessionID = asString(properties?.sessionID) ?? asString(info?.id);
  if (sessionID === null) return null;
  return {
    type: "session.title",
    eventID: asString(envelope.id),
    sessionID,
    title: asString(info?.title),
    ts: asNumber(asRecord(info?.time)?.updated),
  };
}

/** Maps `message.updated` to an internal `message.info` record; model fields come from `info` or nested `info.model`. */
function mapMessageUpdated(
  envelope: Record<string, unknown>,
  properties: Record<string, unknown> | null,
): MessageInfoRecord | null {
  const info = asRecord(properties?.info);
  if (info === null) return null;
  const nestedModel = asRecord(info.model);
  return {
    type: "message.info",
    eventID: asString(envelope.id),
    sessionID: asString(properties?.sessionID) ?? asString(info.sessionID),
    messageID: asString(info.id),
    modelID: asString(info.modelID) ?? asString(nestedModel?.modelID),
    providerID: asString(info.providerID) ?? asString(nestedModel?.providerID),
    agent: asString(info.agent),
    ts: asNumber(asRecord(info.time)?.created),
  };
}

/** Dispatches `message.part.updated` on the part type: `step-finish`, `step-start`, `tool`, else null. */
function mapMessagePartUpdated(
  envelope: Record<string, unknown>,
  properties: Record<string, unknown> | null,
): UsageRecord | null {
  const part = asRecord(properties?.part);
  if (part === null) return null;
  const sessionID = asString(properties?.sessionID) ?? asString(part.sessionID);
  if (part.type === "step-finish") {
    return mapStepFinish(envelope, properties, part, sessionID);
  }
  if (part.type === "step-start") {
    return mapStepStart(envelope, properties, part, sessionID);
  }
  if (part.type === "tool") {
    return mapToolPart(envelope, part, sessionID);
  }
  return null;
}

/** Maps a `step-start` part to an internal `step.started` record (active-time window open). */
function mapStepStart(
  envelope: Record<string, unknown>,
  properties: Record<string, unknown> | null,
  part: Record<string, unknown>,
  sessionID: string | null,
): StepStartedRecord {
  return {
    type: "step.started",
    eventID: asString(envelope.id),
    sessionID,
    messageID: asString(part.messageID),
    partID: asString(part.id),
    ts: asNumber(properties?.time),
  };
}

/** Maps a `step-finish` part: tokens/cost default to 0 when absent, closing the active-time window. */
function mapStepFinish(
  envelope: Record<string, unknown>,
  properties: Record<string, unknown> | null,
  part: Record<string, unknown>,
  sessionID: string | null,
): StepFinishedRecord {
  const tokens = asRecord(part.tokens);
  const cache = asRecord(tokens?.cache);
  return {
    type: "step.finished",
    eventID: asString(envelope.id),
    sessionID,
    messageID: asString(part.messageID),
    partID: asString(part.id),
    agent: asString(part.agent),
    modelID: asString(part.modelID),
    providerID: asString(part.providerID),
    tokens: {
      input: asNumber(tokens?.input) ?? 0,
      output: asNumber(tokens?.output) ?? 0,
      reasoning: asNumber(tokens?.reasoning) ?? 0,
      cache: {
        read: asNumber(cache?.read) ?? 0,
        write: asNumber(cache?.write) ?? 0,
      },
    },
    cost: asNumber(part.cost) ?? 0,
    ts: asNumber(properties?.time),
  };
}

/** Maps a `tool` part in a terminal state (`state.status` completed/error); non-terminal states return null. */
function mapToolPart(
  envelope: Record<string, unknown>,
  part: Record<string, unknown>,
  sessionID: string | null,
): ToolExecutedRecord | null {
  const status = asString(asRecord(part.state)?.status);
  if (status === "completed") {
    return {
      type: "tool.executed",
      eventID: asString(envelope.id),
      sessionID,
      tool: asString(part.tool),
      partID: asString(part.id),
      ok: true,
    };
  }
  if (status === "error") {
    return {
      type: "tool.executed",
      eventID: asString(envelope.id),
      sessionID,
      tool: asString(part.tool),
      partID: asString(part.id),
      ok: false,
      status: "error",
    };
  }
  return null;
}
