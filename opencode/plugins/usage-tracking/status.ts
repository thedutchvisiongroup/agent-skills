/**
 * Write-health tracking for the usage-tracking plugin.
 *
 * Side-channel to the main pipeline (config → mapping → aggregate → store,
 * wired by `index.ts`): counts writes and errors so the `usage_status` tool
 * can report plugin health. Purely in-memory per plugin instance — never
 * persisted.
 */

import type { SessionAggregate, SessionAggregator, SessionTokens } from "./aggregate";

/**
 * Health snapshot returned by the `usage_status` tool (JSON-stringified).
 * `currentSession` is the AC 7.3 rollup totals for the requesting session,
 * or null when the session is unknown to the aggregator.
 */
export type StatusSnapshot = {
  outputPath: string;
  sessionsWritten: number;
  eventsWritten: number;
  lastWriteTs: number | null;
  errorCount: number;
  currentSession: { tokens: SessionTokens; cost: number } | null;
};

/** Counters plus a live read-through to the shared `SessionAggregator`. */
export class StatusTracker {
  private readonly outputPath: string;
  private readonly aggregator: SessionAggregator;
  private readonly writtenSessionIDs = new Set<string>();
  private eventsWrittenCount = 0;
  private errorCountValue = 0;
  private lastWriteTsValue: number | null = null;

  /**
   * @param outputPath - The project-scoped store root (for diagnostics).
   * @param aggregator - The live aggregator; `snapshot` reads current
   *     session totals from it.
   */
  constructor(outputPath: string, aggregator: SessionAggregator) {
    this.outputPath = outputPath;
    this.aggregator = aggregator;
  }

  /** Counts one persisted event append and stamps the last-write time (wall clock). */
  recordEventWritten(): void {
    this.eventsWrittenCount += 1;
    this.lastWriteTsValue = Date.now();
  }

  // Distinct-id counting: re-upserting the same session (another step, idle
  // flush) must not grow the counter.
  recordSessionWritten(sessionID: string): void {
    if (typeof sessionID !== "string" || sessionID.length === 0) return;
    this.writtenSessionIDs.add(sessionID);
    this.lastWriteTsValue = Date.now();
  }

  /** Counts one store/queue error (any fail-open path funnels through here). */
  recordError(): void {
    this.errorCountValue += 1;
  }

  /**
   * Builds the health snapshot for the `usage_status` tool.
   *
   * @param currentSessionID - Session id of the tool-invoking context, when
   *     known; drives `currentSession` (live rollup totals).
   * @returns The counters plus the current session's tokens/cost, or null
   *     for `currentSession` when the id is absent/unknown or finalize fails.
   */
  snapshot(currentSessionID?: string | null): StatusSnapshot {
    return {
      outputPath: this.outputPath,
      sessionsWritten: this.writtenSessionIDs.size,
      eventsWritten: this.eventsWrittenCount,
      lastWriteTs: this.lastWriteTsValue,
      errorCount: this.errorCountValue,
      currentSession: this.currentSessionTotals(currentSessionID),
    };
  }

  // Read-through: finalize() is pure, so calling it per status request is
  // safe; any throw degrades to null (fail-open, ADR-05).
  private currentSessionTotals(currentSessionID?: string | null): StatusSnapshot["currentSession"] {
    if (typeof currentSessionID !== "string" || currentSessionID.length === 0) return null;
    try {
      const aggregates: Record<string, SessionAggregate> = this.aggregator.finalize();
      const aggregate = aggregates[currentSessionID];
      if (aggregate === undefined) return null;
      return { tokens: { ...aggregate.tokens }, cost: aggregate.cost };
    } catch {
      return null;
    }
  }
}
