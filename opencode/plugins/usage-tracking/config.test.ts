// Red test suite (Task 4) for the usage-tracking plugin's config resolution.
// Specification sources: task dispatch (2026-08-26), spike findings
// (.agents/runs/2026-08-26-opencode-usage-tracking/reports/spike-findings-and-decision.md).
//
// Contract under test — `resolveConfig(options?)` from "./config" returns:
//   { output: string, excludeAgents: string[], warnings: string[] }
// - Default output root is the expansion of "~/.local/share/opencode-usage/".
// - Tuple-delivered plugin options override the output root ("output" key).
// - Unknown option keys and an invalid "output" type each produce exactly one
//   warning; an invalid type falls back to the default root.
import { describe, it, expect } from "bun:test";
import { homedir } from "node:os";
import { isAbsolute, join } from "node:path";
import { resolveConfig } from "./config";

/** The default output root with any trailing slash normalized away. */
function defaultOutputRoot(): string {
  return join(homedir(), ".local/share/opencode-usage");
}

describe("resolveConfig()", () => {
  it("returns the expanded default output root and an empty excludeAgents list when called without options", () => {
    const config = resolveConfig();

    expect(typeof config.output).toBe("string");
    // "~" must be expanded to the real home directory, never kept literal.
    expect(config.output.includes("~")).toBe(false);
    expect(config.output.startsWith(homedir())).toBe(true);
    expect(config.output.replace(/\/+$/, "")).toBe(defaultOutputRoot());
    expect(Array.isArray(config.excludeAgents)).toBe(true);
    expect(config.excludeAgents).toHaveLength(0);
    expect(config.warnings).toHaveLength(0);
  });

  it("lets tuple options override the output root without warnings", () => {
    const config = resolveConfig({ output: "/tmp/usage-tracking-override" });

    expect(config.output).toBe("/tmp/usage-tracking-override");
    expect(config.warnings).toHaveLength(0);
  });

  it("warns exactly once for an unknown option", () => {
    const config = resolveConfig({ completelyUnknownOption: true });

    expect(config.warnings).toHaveLength(1);
  });

  it("falls back to the default output root and warns exactly once when output has an invalid type", () => {
    const config = resolveConfig({ output: 42 });

    expect(config.output.replace(/\/+$/, "")).toBe(defaultOutputRoot());
    expect(config.warnings).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// Task 6 additions — review findings (code + security review, 2026-08-26):
// the excludeAgents validation branches (previously uncovered by tests) and
// relative output path resolution.
// ---------------------------------------------------------------------------

describe("resolveConfig() — review findings (task 6)", () => {
  it("keeps the default excludeAgents and warns exactly once when excludeAgents is not an array", () => {
    const config = resolveConfig({ excludeAgents: 42 });

    expect(config.excludeAgents).toEqual([]);
    expect(config.warnings).toHaveLength(1);
    expect(config.warnings[0]).toContain("excludeAgents");
  });

  it("keeps the default excludeAgents and warns exactly once when excludeAgents mixes non-strings", () => {
    const config = resolveConfig({ excludeAgents: ["plan", 7] });

    expect(config.excludeAgents).toEqual([]);
    expect(config.warnings).toHaveLength(1);
    expect(config.warnings[0]).toContain("excludeAgents");
  });

  it("accepts a valid excludeAgents array without warnings", () => {
    const config = resolveConfig({ excludeAgents: ["plan", "explore"] });

    expect(config.excludeAgents).toEqual(["plan", "explore"]);
    expect(config.warnings).toHaveLength(0);
  });

  it("resolves a relative output path to an absolute path against the process cwd", () => {
    const config = resolveConfig({ output: "usage-tracking-relative" });

    expect(config.output).toBe(join(process.cwd(), "usage-tracking-relative"));
    expect(isAbsolute(config.output)).toBe(true);
  });
});
