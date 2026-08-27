/**
 * In-memory session aggregation for the usage-tracking plugin.
 *
 * Third stage of the pipeline (config → mapping → aggregate → store, wired by
 * `index.ts`): folds the record stream from `mapping.ts` into per-session
 * state and derives the aggregate snapshot persisted by `store.ts`.
 *
 * Key invariants:
 * - Idempotent input via event-ID dedup (`apply` drops re-delivered events).
 * - `finalize()` is a pure function of the current state: parent totals are
 *   the AC 7.3 rollup (own tokens/cost + entire subtree), while `children`
 *   carry their own (non-rolled-up) totals.
 * - State is grow-only in V1: `evict` exists as a memory-hygiene surface but
 *   is intentionally not wired (see the eviction note on `evict`).
 */

import type { UsageRecord } from "./mapping";

/** Cumulative token counters for one session (cache split into read/write). */
export type SessionTokens = {
  input: number;
  output: number;
  reasoning: number;
  cacheRead: number;
  cacheWrite: number;
};

/** One distinct model used in a session, keyed by model id. */
export type SessionModel = {
  id: string;
  provider: string | null;
  variant: string | null;
};

/**
 * Device attribution stamped on every serialized aggregate (V11): exactly
 * `{name, opencodeVersion}` — os/osVersion are overview-level only.
 */
export type DeviceInfo = {
  name: string;
  opencodeVersion: string;
};

/**
 * Serializable per-session aggregate produced by `finalize` — the exact shape
 * persisted as `sessions/<id>.json` (ADR-02 layer 2). `tokens`/`cost` carry
 * the AC 7.3 rollup on roots (parent totals include the subtree); each
 * `children[i]` holds that child's own (non-rolled-up) totals.
 */
export type SessionAggregate = {
  sessionID: string;
  parentID: string | null;
  project: string | null;
  directory: string | null;
  device: DeviceInfo | null;
  depth: number;
  title: string | null;
  agents: string[];
  models: SessionModel[];
  tokens: SessionTokens;
  cost: number;
  activeMs: number;
  toolCounts: Record<string, number>;
  children: any[];
  time: { created: number | null; updated: number | null; idle: number | null };
};

/** Subtree totals (own + all descendants) used by the AC 7.3 rollup in `finalize`. */
type SessionTotals = { tokens: SessionTokens; cost: number };

/**
 * Mutable per-session accumulator. Deliberately loose (`Record<string, unknown>`
 * in `apply`) so a restart replay of the persisted stream rehydrates it even
 * without the internal record types.
 */
type SessionState = {
  sessionID: string;
  parentID: string | null;
  project: string | null;
  directory: string | null;
  title: string | null;
  agents: Set<string>;
  models: Map<string, SessionModel>;
  tokens: SessionTokens;
  cost: number;
  activeMs: number;
  toolCounts: Map<string, number>;
  created: number | null;
  updated: number | null;
  idleTs: number | null;
};

function asFields(value: unknown): Record<string, unknown> | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  return value as Record<string, unknown>;
}

function readString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function readCounter(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function readTimestamp(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function zeroTokens(): SessionTokens {
  return { input: 0, output: 0, reasoning: 0, cacheRead: 0, cacheWrite: 0 };
}

// Null-prototype record: hostile keys like "__proto__" land as own properties
// instead of hitting Object.prototype's setter (prototype-pollution guard).
// Used for every keyed output that later becomes JSON in stored files.
function safeRecord<T>(): Record<string, T> {
  return Object.create(null);
}

function serializeToolCounts(counts: Map<string, number>): Record<string, number> {
  const result = safeRecord<number>();
  for (const [tool, count] of counts) {
    result[tool] = count;
  }
  return result;
}

/** Accepts only a `{name, opencodeVersion}` with both fields non-empty; anything else → null. */
function normalizeDeviceInfo(value: unknown): DeviceInfo | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const fields = value as Record<string, unknown>;
  const name = readString(fields.name);
  const opencodeVersion = readString(fields.opencodeVersion);
  if (name === null || opencodeVersion === null) return null;
  return { name, opencodeVersion };
}

/**
 * Folds usage records into per-session state and derives aggregates.
 *
 * State lives entirely in memory; persistence is the store's job. All
 * registries (`seenEventIDs`, `seenToolParts`, `stepStartQueues`) are
 * grow-only by design so a re-delivered event can never be double-counted.
 */
export class SessionAggregator {
  private sessions = new Map<string, SessionState>();
  // Dedup registries must stay grow-only: once an event/tool part has been
  // counted, a re-delivery (restart replay, bus redelivery) must stay a
  // no-op even if the owning session's state was evicted and re-created.
  private seenEventIDs = new Set<string>();
  private seenToolParts = new Set<string>();
  // FIFO queues of unconsumed step.started timestamps, keyed by
  // (sessionID, messageID): a start pushes onto its message's queue; a
  // finish consumes the OLDEST unconsumed start of the same message. Live
  // step-start and step-finish are DIFFERENT parts (different partIDs), so
  // partID-based pairing never matches — the message is the stable join key.
  private stepStartQueues = new Map<string, number[]>();
  private readonly device: DeviceInfo | null;

  /**
   * @param device - Optional device attribution (`{name, opencodeVersion}`)
   *   stamped on every serialized aggregate; absent/invalid → `null`
   *   (fail-open). Single injection point, backward compatible.
   */
  constructor(device?: DeviceInfo | null) {
    this.device = normalizeDeviceInfo(device);
  }

  /**
   * Applies one record to the session state.
   *
   * Event-ID dedup: the optional `sourceEventID` (live bus envelope id)
   * takes precedence over the record's own `eventID`; records without either
   * are applied unconditionally (no dedup key available).
   *
   * @param record - A `UsageRecord` from `mapEvent`, or the loose shape of a
   *   persisted record during restart replay. Unknown types are no-ops.
   * @param sourceEventID - Live envelope id supplied by the caller.
   */
  apply(
    record: UsageRecord | Record<string, unknown> | null | undefined,
    sourceEventID?: string | null,
  ): void {
    const fields = asFields(record);
    if (fields === null) return;
    const eventType = typeof fields.type === "string" ? fields.type : null;
    if (eventType === null) return;

    const dedupKey = readString(sourceEventID) ?? readString(fields.eventID);
    if (dedupKey !== null) {
      if (this.seenEventIDs.has(dedupKey)) return;
      this.seenEventIDs.add(dedupKey);
    }

    if (eventType === "session.started") {
      this.applySessionStarted(fields);
    } else if (eventType === "session.title") {
      this.applySessionTitle(fields);
    } else if (eventType === "message.info") {
      this.applyMessageInfo(fields);
    } else if (eventType === "step.started") {
      this.applyStepStarted(fields);
    } else if (eventType === "step.finished") {
      this.applyStepFinished(fields);
    } else if (eventType === "tool.executed") {
      this.applyToolExecuted(fields);
    } else if (eventType === "session.idle") {
      this.applySessionIdle(fields);
    }
  }

  // Memory-hygiene surface: after a session's aggregate has been finalized and
  // upserted, the caller may drop its in-memory state. Unknown ids (and ids
  // already evicted) are tolerated no-ops. Dedup registries (seenEventIDs,
  // seenToolParts) are deliberately kept so a re-delivered event cannot be
  // double-counted into a re-created session.
  //
  // NOTE: not wired in V1 — index.ts never calls this. session.idle fires
  // after every turn, not session end, so evicting there would make later
  // turns rebuild from zero and overwrite the persisted aggregate with
  // partial totals; V1 accepts unbounded in-memory retention by design.
  evict(sessionID: string): void {
    if (typeof sessionID !== "string" || sessionID.length === 0) return;
    this.sessions.delete(sessionID);
    const stepPrefix = `${sessionID}\u0000`;
    for (const key of this.stepStartQueues.keys()) {
      if (key.startsWith(stepPrefix)) this.stepStartQueues.delete(key);
    }
  }

  /**
   * Derives the aggregate snapshot of every known session.
   *
   * Pure and idempotent: state is never mutated, so calling it again (every
   * written event, every `usage_status` call) yields the same result. Cycles
   * are tolerated — a session in a parent cycle contributes zero subtree
   * totals and is skipped in child serialization.
   *
   * @returns Null-prototype map of sessionID → `SessionAggregate`. Root
   *   sessions (no parent, or an absent parent) carry the AC 7.3 rollup
   *   (own + subtree tokens/cost); nested children carry their own totals
   *   only, so no double counting when walking `children`.
   */
  finalize(): Record<string, SessionAggregate> {
    const childrenOf = this.buildChildrenIndex();
    const totalsCache = new Map<string, SessionTotals>();

    // Memoized post-order subtree totals; the `visiting` set guards against
    // parent cycles (a cycle member contributes zero, not infinity).
    const subtreeTotals = (sessionID: string, visiting: Set<string>): SessionTotals => {
      const cached = totalsCache.get(sessionID);
      if (cached !== undefined) return cached;
      const state = this.sessions.get(sessionID);
      if (state === undefined || visiting.has(sessionID)) {
        return { tokens: zeroTokens(), cost: 0 };
      }
      visiting.add(sessionID);
      const tokens: SessionTokens = { ...state.tokens };
      let cost = state.cost;
      for (const childID of childrenOf.get(sessionID) ?? []) {
        const childTotals = subtreeTotals(childID, visiting);
        tokens.input += childTotals.tokens.input;
        tokens.output += childTotals.tokens.output;
        tokens.reasoning += childTotals.tokens.reasoning;
        tokens.cacheRead += childTotals.tokens.cacheRead;
        tokens.cacheWrite += childTotals.tokens.cacheWrite;
        cost += childTotals.cost;
      }
      visiting.delete(sessionID);
      const totals: SessionTotals = { tokens, cost };
      totalsCache.set(sessionID, totals);
      return totals;
    };

    // Depth = number of live ancestor links; stops at cycles, missing parents,
    // and self-parents.
    const depthOf = (state: SessionState): number => {
      let depth = 0;
      let current: SessionState | undefined = state;
      const visited = new Set<string>([state.sessionID]);
      while (current !== undefined && current.parentID !== null) {
        const parentID = current.parentID;
        if (visited.has(parentID)) break;
        depth += 1;
        visited.add(parentID);
        if (!this.sessions.has(parentID)) break;
        current = this.sessions.get(parentID);
      }
      return depth;
    };

    // `rolledUp` is true only for roots: they get subtree totals, nested
    // children get own totals. `path` prevents infinite recursion in cycles.
    const serialize = (state: SessionState, rolledUp: boolean, path: ReadonlySet<string>): SessionAggregate => {
      const totals = rolledUp
        ? subtreeTotals(state.sessionID, new Set<string>())
        : { tokens: state.tokens, cost: state.cost };
      const pathWithSelf = new Set(path);
      pathWithSelf.add(state.sessionID);
      const children: SessionAggregate[] = [];      for (const childID of childrenOf.get(state.sessionID) ?? []) {
        if (pathWithSelf.has(childID)) continue;
        const child = this.sessions.get(childID);
        if (child !== undefined) children.push(serialize(child, false, pathWithSelf));
      }
      return {
        sessionID: state.sessionID,
        parentID: state.parentID,
        project: state.project,
        directory: state.directory,
        device: this.device === null ? null : { name: this.device.name, opencodeVersion: this.device.opencodeVersion },
        depth: depthOf(state),
        title: state.title,
        agents: [...state.agents],
        models: [...state.models.values()],
        tokens: { ...totals.tokens },
        cost: totals.cost,
        activeMs: state.activeMs,
        toolCounts: serializeToolCounts(state.toolCounts),
        children,
        time: { created: state.created, updated: state.updated, idle: state.idleTs },
      };
    };

    const aggregates = safeRecord<SessionAggregate>();
    for (const state of this.sessions.values()) {
      const rolledUp = state.parentID === null || !this.sessions.has(state.parentID);
      aggregates[state.sessionID] = serialize(state, rolledUp, new Set<string>());
    }
    return aggregates;
  }

  /** Indexes live sessions by parentID; self-parents and dead parents are skipped. */
  private buildChildrenIndex(): Map<string, string[]> {
    const childrenOf = new Map<string, string[]>();
    for (const state of this.sessions.values()) {
      const parentID = state.parentID;
      if (parentID === null || parentID === state.sessionID) continue;
      if (!this.sessions.has(parentID)) continue;
      const siblings = childrenOf.get(parentID);
      if (siblings === undefined) {
        childrenOf.set(parentID, [state.sessionID]);
      } else if (!siblings.includes(state.sessionID)) {
        siblings.push(state.sessionID);
      }
    }
    return childrenOf;
  }

  /** Creates (or returns) the state slot for a session; called lazily so records can arrive in any order. */
  private ensureSession(sessionID: string): SessionState {
    let state = this.sessions.get(sessionID);
    if (state === undefined) {
      state = {
        sessionID,
        parentID: null,
        project: null,
        directory: null,
        title: null,
        agents: new Set<string>(),
        models: new Map<string, SessionModel>(),
        tokens: zeroTokens(),
        cost: 0,
        activeMs: 0,
        toolCounts: new Map<string, number>(),
        created: null,
        updated: null,
        idleTs: null,
      };
      this.sessions.set(sessionID, state);
    }
    return state;
  }

  // Steps pair by (sessionID, messageID): live start and finish parts carry
  // different partIDs, so the message is the only stable join key. The \u0000
  // separator keeps ids from colliding across namespaces.
  private stepQueueKey(sessionID: string, messageID: string): string {
    return `${sessionID}\u0000${messageID}`;
  }

  /** session.started: sets identity/parent/project/directory, first agent, model, title, and created ts. */
  private applySessionStarted(fields: Record<string, unknown>): void {
    const sessionID = readString(fields.sessionID);
    if (sessionID === null) return;
    const state = this.ensureSession(sessionID);
    state.parentID = readString(fields.parentID);
    state.project = readString(fields.projectID);
    state.directory = readString(fields.directory);
    const agent = readString(fields.agent);
    if (agent !== null) state.agents.add(agent);
    const title = readString(fields.title);
    if (title !== null) state.title = title;
    const model = asFields(fields.model);
    const modelID = model === null ? null : readString(model.id);
    if (modelID !== null && !state.models.has(modelID)) {
      state.models.set(modelID, {
        id: modelID,
        provider: model === null ? null : readString(model.providerID),
        variant: model === null ? null : readString(model.variant),
      });
    }
    const ts = readTimestamp(fields.ts);
    if (ts !== null) {
      state.created = ts;
      if (state.updated === null || ts > state.updated) state.updated = ts;
    }
  }

  /** session.title: last non-empty title wins (see inline note). */
  private applySessionTitle(fields: Record<string, unknown>): void {
    const sessionID = readString(fields.sessionID);
    if (sessionID === null) return;
    const state = this.ensureSession(sessionID);
    const title = readString(fields.title);
    // Non-empty later-wins; an empty title never clears a previous one.
    if (title !== null) state.title = title;
  }

  /** message.info (internal): contributes agent/model attribution only. */
  private applyMessageInfo(fields: Record<string, unknown>): void {
    const sessionID = readString(fields.sessionID);
    if (sessionID === null) return;
    const state = this.ensureSession(sessionID);
    const agent = readString(fields.agent);
    if (agent !== null) state.agents.add(agent);
    const modelID = readString(fields.modelID);
    if (modelID !== null && !state.models.has(modelID)) {
      state.models.set(modelID, {
        id: modelID,
        provider: readString(fields.providerID),
        variant: null,
      });
    }
  }

  /** step.started (internal): pushes the step's start ts onto its message's FIFO queue for activeMs pairing. */
  private applyStepStarted(fields: Record<string, unknown>): void {
    const sessionID = readString(fields.sessionID);
    if (sessionID === null) return;
    const messageID = readString(fields.messageID);
    if (messageID === null) return;
    const ts = readTimestamp(fields.ts);
    if (ts === null) return;
    const key = this.stepQueueKey(sessionID, messageID);
    const queue = this.stepStartQueues.get(key);
    if (queue === undefined) {
      this.stepStartQueues.set(key, [ts]);
    } else {
      queue.push(ts);
    }
  }

  /** step.finished: adds tokens/cost, closes the OLDEST open step of its message (FIFO activeMs pairing), and records agent/model. */
  private applyStepFinished(fields: Record<string, unknown>): void {
    const sessionID = readString(fields.sessionID);
    if (sessionID === null) return;
    const state = this.ensureSession(sessionID);
    const tokens = asFields(fields.tokens);
    const cache = tokens === null ? null : asFields(tokens.cache);
    state.tokens.input += readCounter(tokens?.input);
    state.tokens.output += readCounter(tokens?.output);
    state.tokens.reasoning += readCounter(tokens?.reasoning);
    state.tokens.cacheRead += readCounter(cache?.read);
    state.tokens.cacheWrite += readCounter(cache?.write);
    state.cost += readCounter(fields.cost);
    const ts = readTimestamp(fields.ts);
    const messageID = readString(fields.messageID);
    if (messageID !== null) {
      // A finish without an unconsumed start of its message contributes 0
      // activeMs (tokens/cost above still count); an exhausted queue behaves
      // the same as no queue at all.
      const queue = this.stepStartQueues.get(this.stepQueueKey(sessionID, messageID));
      const startTs = queue?.shift();
      if (startTs !== undefined && ts !== null) {
        const stepMs = ts - startTs;
        if (stepMs > 0) state.activeMs += stepMs;
      }
    }
    const agent = readString(fields.agent);
    if (agent !== null) state.agents.add(agent);
    const modelID = readString(fields.modelID);
    if (modelID !== null && !state.models.has(modelID)) {
      state.models.set(modelID, {
        id: modelID,
        provider: readString(fields.providerID),
        variant: readString(fields.variant),
      });
    }
    if (ts !== null && (state.updated === null || ts > state.updated)) state.updated = ts;
  }

  /** tool.executed: counts the tool, deduped by (sessionID, partID) so a re-delivered part counts once. */
  private applyToolExecuted(fields: Record<string, unknown>): void {
    const sessionID = readString(fields.sessionID);
    if (sessionID === null) return;
    const tool = readString(fields.tool);
    if (tool === null) return;
    const partID = readString(fields.partID);
    if (partID !== null) {
      const partKey = `${sessionID}\u0000${partID}`;
      if (this.seenToolParts.has(partKey)) return;
      this.seenToolParts.add(partKey);
    }
    const state = this.ensureSession(sessionID);
    state.toolCounts.set(tool, (state.toolCounts.get(tool) ?? 0) + 1);
  }

  /** session.idle: pins idleTs to the last known updated ts (not "now") so the marker stays event-sourced. */
  private applySessionIdle(fields: Record<string, unknown>): void {
    const sessionID = readString(fields.sessionID);
    if (sessionID === null) return;
    const state = this.ensureSession(sessionID);
    state.idleTs = state.updated;
  }
}
