// Entry-file test (Task 5 loading-route fix, 2026-08-27).
//
// Contract under test — the flat entry file "../usage-tracking.ts":
// OpenCode plugin auto-discovery scans only files DIRECTLY inside the plugins
// dir (glob "{plugin,plugins}/*.{ts,js}"), so the subdirectory layout alone is
// NOT discoverable. The repo entry opencode/plugins/usage-tracking.ts (linked
// flat into ~/.config/opencode/plugins/usage-tracking.ts) must re-export the
// plugin's default export unchanged. The plugin default export is a function
// (Plugin = (input, options?) => Promise<Hooks>); anything else (undefined,
// module namespace, object) would silently break the loading route.
import { describe, it, expect } from "bun:test";
import entry from "../usage-tracking.ts";

describe("usage-tracking flat entry file (loading route)", () => {
  it("re-exports the plugin default export as a function", () => {
    expect(typeof entry).toBe("function");
  });
});
