/**
 * Configuration resolution for the usage-tracking plugin.
 *
 * First stage of the pipeline (config → mapping → aggregate → store, wired by
 * `index.ts`): turns the raw plugin options delivered by OpenCode into a
 * validated `ResolvedConfig` with absolute paths, collecting warnings for
 * every deviation instead of failing (fail-open, ADR-05).
 */

import { homedir } from "node:os";
import { isAbsolute, join, resolve } from "node:path";
import type { PluginOptions } from "@opencode-ai/plugin";

const DEFAULT_OUTPUT_ROOT = "~/.local/share/opencode-usage/";
const KNOWN_OPTION_KEYS = ["output", "excludeAgents"];

/** Receives one warning message per invalid/unknown option; must never throw. */
export type ConfigWarningLogger = (message: string) => void;

/**
 * Fully validated plugin configuration.
 *
 * - `output`: absolute output root (project-scoped subdirectory is appended
 *   later by `index.ts`)
 * - `excludeAgents`: agent names to exclude (accepted, V1 keeps it unenforced)
 * - `warnings`: every warning emitted during resolution, in order
 */
export type ResolvedConfig = {
  output: string;
  excludeAgents: string[];
  warnings: string[];
};

/** Expands a leading `~`/`~/` to the user's home directory; other values pass through. */
function expandHomeDirectory(value: string): string {
  if (value === "~") return homedir();
  if (value.startsWith("~/")) return join(homedir(), value.slice(2));
  return value;
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function toStringArray(value: unknown): string[] | null {
  // All-or-nothing validation: any non-string item rejects the whole array
  // (the caller then warns and keeps the empty default).
  if (!Array.isArray(value)) return null;
  const items: string[] = [];
  for (const item of value) {
    if (typeof item !== "string") return null;
    items.push(item);
  }
  return items;
}

/**
 * Resolves the plugin's delivered options into a validated configuration.
 *
 * Every problem (missing/invalid `output`, non-string-array `excludeAgents`,
 * unknown keys) degrades to the default with a warning — resolution never
 * throws, keeping the plugin loadable under any input (fail-open, ADR-05).
 *
 * @param options - Raw options as delivered by OpenCode (arbitrary shape;
 *   known keys: `output` string, `excludeAgents` string[])
 * @param logger - Optional sink for warnings; each warning is also collected
 *   in `ResolvedConfig.warnings`. Logger throws are swallowed.
 * @returns The resolved config: `output` is home-expanded and absolute
 *   (relative roots are pinned against the host cwd at resolution time),
 *   `excludeAgents` defaults to `[]`.
 */
export function resolveConfig(
  options?: PluginOptions | null,
  logger?: ConfigWarningLogger,
): ResolvedConfig {
  const warnings: string[] = [];

  const warn = (message: string): void => {
    warnings.push(message);
    try {
      logger?.(message);
    } catch {}
  };

  let output = expandHomeDirectory(DEFAULT_OUTPUT_ROOT);
  let excludeAgents: string[] = [];

  const delivered = isPlainObject(options) ? options : null;
  if (delivered !== null) {
    for (const key of Object.keys(delivered)) {
      const value = delivered[key];
      if (key === "output") {
        if (typeof value !== "string" || value.trim() === "") {
          warn(
            `usage-tracking: option "output" must be a non-empty string, falling back to ${DEFAULT_OUTPUT_ROOT}`,
          );
          continue;
        }
        output = expandHomeDirectory(value);
      } else if (key === "excludeAgents") {
        const agents = toStringArray(value);
        if (agents === null) {
          warn('usage-tracking: option "excludeAgents" must be an array of strings, ignoring it');
          continue;
        }
        excludeAgents = agents;
      } else {
        warn(
          `usage-tracking: unknown option "${key}" ignored (known options: ${KNOWN_OPTION_KEYS.join(", ")})`,
        );
      }
    }
  }

  return { output: resolveRelative(output), excludeAgents, warnings };
}

// A relative output root is host-cwd-dependent; pin it at resolution time so
// every consumer (status, store) shares one absolute path.
function resolveRelative(output: string): string {
  return isAbsolute(output) ? output : resolve(output);
}
