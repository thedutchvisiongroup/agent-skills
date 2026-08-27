// Red test suite (v12, dispatch 2026-08-27) for the usage-tracking plugin's
// deterministic project-directory naming. Specification sources: v12 dispatch
// (approved deterministic-hash scheme, replacing ULID + projects.json registry).
//
// Contract under test — "./projectdir" (NEW pure module: no fs, no OpenCode
// imports, no randomness):
//   projectDirectoryName(input: {
//     worktree?: unknown;   // non-empty string → resolved absolute path
//     directory?: unknown;  // fallback when worktree is absent/non-string
//     remote?: unknown;     // git remote URL (see remoteKey below)
//     hostname?: unknown;   // non-empty string → used verbatim, else "unknown"
//   }): string | null
//
// Formula (pinned exactly by the dispatch):
//   identity  = resolve(worktree) when worktree is a non-empty string,
//               else resolve(directory) when directory is a non-empty string,
//               else null → the function returns null (regardless of remote).
//   remoteKey = remote trimmed with ONE trailing ".git" removed, when that
//               leaves a non-empty string; else identity.
//   hashInput = (hostname non-empty string ? hostname : "unknown") + "\n" + remoteKey
//   name      = sha256(hashInput) hex digest, first 24 lowercase chars.
//
// The three known-vector tests hard-code digests computed OUTSIDE this suite
// (printf | sha256sum, cross-checked with Python hashlib) so the formula is
// frozen: any deviation — different separator, different hostname fallback,
// different truncation length, uppercase hex — turns them red.
import { describe, it, expect } from "bun:test";
import { resolve } from "node:path";
import { projectDirectoryName } from "./projectdir";

const HEX24_RE = /^[0-9a-f]{24}$/;

describe("projectDirectoryName() — determinism and format", () => {
  it("returns the identical name for repeated calls with the same inputs (pure, no randomness)", () => {
    const first = projectDirectoryName({
      worktree: "/wt/x",
      directory: "/dir/x",
      remote: "https://github.com/a/b.git",
      hostname: "dev1",
    });
    // A fresh object literal with the same values: the name must depend on the
    // input VALUES, never on call order, caches, or object identity.
    const second = projectDirectoryName({
      worktree: "/wt/x",
      directory: "/dir/x",
      remote: "https://github.com/a/b.git",
      hostname: "dev1",
    });
    expect(first).not.toBeNull();
    expect(second).toBe(first);
  });

  it("returns 24 lowercase hex chars for remote-based, path-based, and unknown-hostname names", () => {
    const names = [
      projectDirectoryName({ worktree: "/wt/x", remote: "https://github.com/a/b.git", hostname: "dev1" }),
      projectDirectoryName({ worktree: "/wt/x", hostname: "dev1" }),
      projectDirectoryName({ worktree: "/wt/x" }),
    ];
    for (const name of names) {
      expect(name).not.toBeNull();
      expect(name).toMatch(HEX24_RE);
    }
  });
});

describe("projectDirectoryName() — hostname", () => {
  it("produces different names for different hostnames (same path and remote)", () => {
    const shared = { worktree: "/wt/x", directory: "/dir/x", remote: "https://github.com/a/b.git" };
    const a = projectDirectoryName({ ...shared, hostname: "host-a" });
    const b = projectDirectoryName({ ...shared, hostname: "host-b" });
    expect(a).not.toBeNull();
    expect(b).not.toBe(a);
  });

  it("treats an empty hostname string as \"unknown\": empty calls equal the omitted-hostname call and differ from a named host", () => {
    const shared = { worktree: "/wt/x", remote: "https://github.com/a/b.git" };
    const empty = projectDirectoryName({ ...shared, hostname: "" });
    const explicitUndefined = projectDirectoryName({ ...shared, hostname: undefined });
    const omitted = projectDirectoryName({ ...shared });
    const named = projectDirectoryName({ ...shared, hostname: "dev1" });
    expect(explicitUndefined).toBe(empty);
    expect(empty).toBe(omitted);
    expect(empty).not.toBe(named);
  });
});

describe("projectDirectoryName() — remote key", () => {
  it("makes the path irrelevant when a remote is present (a moved repo keeps its name)", () => {
    const original = projectDirectoryName({
      worktree: "/old/location",
      directory: "/old",
      remote: "https://github.com/a/b.git",
      hostname: "dev1",
    });
    const moved = projectDirectoryName({
      worktree: "/new/location",
      directory: "/new",
      remote: "https://github.com/a/b.git",
      hostname: "dev1",
    });
    expect(original).not.toBeNull();
    expect(moved).toBe(original);
  });

  it("normalizes the remote: trims whitespace and removes exactly ONE trailing '.git'", () => {
    const base = { worktree: "/wt/x", hostname: "dev1" };
    const plain = projectDirectoryName({ ...base, remote: "https://x/y" });
    expect(plain).not.toBeNull();
    // ".git" suffix normalization: both remotes hash to the same key.
    expect(projectDirectoryName({ ...base, remote: "https://x/y.git" })).toBe(plain);
    // The remote is trimmed before hashing.
    expect(projectDirectoryName({ ...base, remote: "  https://x/y.git  " })).toBe(plain);
    // Exactly ONE trailing ".git" is removed: stripping ALL of them would make
    // this equal `plain`, which it must not be.
    expect(projectDirectoryName({ ...base, remote: "https://x/y.git.git" })).not.toBe(plain);
  });

  it("falls back to the path identity when the remote is absent, non-string, or strips to nothing", () => {
    const base = { worktree: "/wt/x", hostname: "dev1" };
    const identity = projectDirectoryName({ ...base });
    expect(identity).not.toBeNull();
    // Non-string remotes (the wiring's fail-open null among them) → identity.
    expect(projectDirectoryName({ ...base, remote: null })).toBe(identity);
    expect(projectDirectoryName({ ...base, remote: 123 })).toBe(identity);
    // Remotes that trim/strip to an empty string → identity.
    expect(projectDirectoryName({ ...base, remote: ".git" })).toBe(identity);
    expect(projectDirectoryName({ ...base, remote: "   " })).toBe(identity);
  });
});

describe("projectDirectoryName() — path identity (no remote)", () => {
  it("derives the name from the worktree when present (directory ignored); different worktrees differ", () => {
    const a = projectDirectoryName({ worktree: "/wt/x", directory: "/dir/a", hostname: "dev1" });
    expect(a).not.toBeNull();
    // The worktree wins: the directory may change freely.
    expect(a).toBe(projectDirectoryName({ worktree: "/wt/x", directory: "/dir/b", hostname: "dev1" }));
    expect(a).not.toBe(projectDirectoryName({ worktree: "/wt/y", directory: "/dir/a", hostname: "dev1" }));
    // Worktree preferred over directory when both are present.
    expect(a).not.toBe(projectDirectoryName({ directory: "/dir/a", hostname: "dev1" }));
  });

  it("falls back to the directory identity when no worktree is present", () => {
    const a = projectDirectoryName({ directory: "/dir/x", hostname: "dev1" });
    const b = projectDirectoryName({ directory: "/dir/y", hostname: "dev1" });
    expect(a).not.toBeNull();
    expect(b).not.toBe(a);
  });

  it("resolves paths before hashing: relative and absolute forms share a name, as do trailing-slash variants", () => {
    const absolute = projectDirectoryName({ worktree: "/wt/x", hostname: "dev1" });
    expect(absolute).not.toBeNull();
    expect(projectDirectoryName({ worktree: "/wt/x/", hostname: "dev1" })).toBe(absolute);
    const relative = projectDirectoryName({ worktree: "some/relative/wt", hostname: "dev1" });
    expect(relative).toBe(projectDirectoryName({ worktree: resolve("some/relative/wt"), hostname: "dev1" }));
  });
});

describe("projectDirectoryName() — null result", () => {
  it("returns null when worktree and directory are both absent, non-strings, or empty strings", () => {
    expect(projectDirectoryName({})).toBeNull();
    expect(projectDirectoryName({ worktree: null, directory: undefined })).toBeNull();
    expect(projectDirectoryName({ worktree: 42, directory: {} })).toBeNull();
    expect(projectDirectoryName({ worktree: "", directory: "" })).toBeNull();
  });

  it("returns null even with a remote and hostname when no path identity exists (identity null → null result)", () => {
    expect(projectDirectoryName({ remote: "https://github.com/a/b.git", hostname: "dev1" })).toBeNull();
  });
});

describe("projectDirectoryName() — known vectors (formula freeze)", () => {
  // Digests computed OUTSIDE this suite and hard-coded (printf | sha256sum,
  // cross-checked with Python hashlib):
  //   sha256("dev1\nhttps://github.com/a/b") → 9d899ec6af2600a07a69a4eb…
  //   sha256("dev1\n/wt/x")                  → 498d6f790e12229dc26ff0f1…
  //   sha256("unknown\n/wt/x")               → 68d4855f5368d7e1ba4fbb20…
  it("known vector: hostname 'dev1' + remote 'https://github.com/a/b.git' → sha256('dev1\\nhttps://github.com/a/b') first 24 hex chars", () => {
    expect(
      projectDirectoryName({
        worktree: "/any/path",
        directory: "/any",
        remote: "https://github.com/a/b.git",
        hostname: "dev1",
      }),
    ).toBe("9d899ec6af2600a07a69a4eb");
  });

  it("known vector: hostname 'dev1' + worktree '/wt/x' without a remote → sha256('dev1\\n/wt/x') first 24 hex chars", () => {
    expect(projectDirectoryName({ worktree: "/wt/x", hostname: "dev1" })).toBe("498d6f790e12229dc26ff0f1");
  });

  it("known vector: no hostname (→ 'unknown') + worktree '/wt/x' → sha256('unknown\\n/wt/x') first 24 hex chars", () => {
    expect(projectDirectoryName({ worktree: "/wt/x" })).toBe("68d4855f5368d7e1ba4fbb20");
  });
});
