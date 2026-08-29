// Red test suite (v12, dispatch 2026-08-27) for the usage-tracking plugin's
// deterministic project-directory naming. Specification sources: v12 dispatch
// (approved deterministic-hash scheme, replacing ULID + projects.json registry).
//
// Contract under test — "./projectdir" (NEW pure module: no fs, no OpenCode
// imports, no randomness):
//   projectDirectoryName(input: {
//     worktree?: unknown;   // non-empty string → resolved absolute path
//     directory?: unknown;  // fallback when worktree is absent, non-string, or the filesystem root
//     remote?: unknown;     // git remote URL (see remoteKey below)
//     hostname?: unknown;   // non-empty string → used verbatim, else "unknown"
//   }): string | null
//
// Formula (pinned exactly by the dispatch; root-worktree rule added v1.3):
//   identity  = resolve(worktree) when worktree is a non-empty string whose
//               resolution is not the filesystem root "/" (OpenCode's
//               placeholder for non-git projects — counts as absent),
//               else resolve(directory) when directory is a non-empty string
//               (a genuine "/" included),
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

describe("projectDirectoryName() — filesystem-root worktree (non-git projects, v1.3)", () => {
  // OpenCode passes worktree = "/" when started outside a git repository.
  // Taking that placeholder as the project identity made every non-git
  // project on a machine share ONE output directory (the live bug:
  // sha256("<hostname>\n/") held 13 sessions from 3 project directories).
  // A filesystem-root worktree therefore counts as ABSENT — identity falls
  // back to the directory — while a genuine directory of "/" stays valid.

  it("treats a \"/\" worktree as absent: the directory becomes the identity", () => {
    const viaRootWorktree = projectDirectoryName({ worktree: "/", directory: "/home/x/proj", hostname: "dev1" });
    expect(viaRootWorktree).not.toBeNull();
    // Hashes over the directory path, not the placeholder "/".
    expect(viaRootWorktree).toBe(projectDirectoryName({ directory: "/home/x/proj", hostname: "dev1" }));
    // And it does not collapse into the genuine-root identity.
    expect(viaRootWorktree).not.toBe(projectDirectoryName({ directory: "/", hostname: "dev1" }));
  });

  it("returns null for a \"/\" worktree without a directory (fail-open upstream), even with remote and hostname", () => {
    expect(projectDirectoryName({ worktree: "/" })).toBeNull();
    expect(projectDirectoryName({ worktree: "/", remote: "https://github.com/a/b.git", hostname: "dev1" })).toBeNull();
  });

  it("keeps a \"/\" directory as a valid identity (OpenCode genuinely started in /)", () => {
    const rootDirectory = projectDirectoryName({ worktree: "/", directory: "/", hostname: "dev1" });
    expect(rootDirectory).not.toBeNull();
    expect(rootDirectory).toBe(projectDirectoryName({ directory: "/", hostname: "dev1" }));
  });

  it("leaves normal worktrees in place: only \"/\" counts as absent", () => {
    const a = projectDirectoryName({ worktree: "/wt/x", directory: "/dir/x", hostname: "dev1" });
    expect(a).not.toBeNull();
    // A non-root worktree still wins over the directory (unchanged rule).
    expect(a).toBe(projectDirectoryName({ worktree: "/wt/x", directory: "/other", hostname: "dev1" }));
    expect(a).not.toBe(projectDirectoryName({ directory: "/dir/x", hostname: "dev1" }));
  });

  it("keeps the remote override and hostname salt unchanged for a \"/\" worktree", () => {
    // Same remote key as the frozen known vector below: the override must
    // still win, unaffected by the root-worktree rule.
    expect(
      projectDirectoryName({ worktree: "/", directory: "/home/x/proj", remote: "https://github.com/a/b.git", hostname: "dev1" }),
    ).toBe("9d899ec6af2600a07a69a4eb");
  });

  // Digests computed OUTSIDE this suite (printf | sha256sum; the third vector
  // reproduces the live bug evidence — the old shared non-git directory
  // 23be191393b51993adc296ed = sha256("remote-dev-server\n/")[:24] — which is
  // reachable now only via a genuine root directory).
  it("known vector: hostname 'dev1' + \"/\" worktree + directory '/home/x/proj' → sha256('dev1\\n/home/x/proj') first 24 hex chars", () => {
    expect(projectDirectoryName({ worktree: "/", directory: "/home/x/proj", hostname: "dev1" })).toBe("ddbf0aa94c437a3fc5e768d0");
  });

  it("known vector: hostname 'dev1' + \"/\" worktree + directory '/' → sha256('dev1\\n/') first 24 hex chars (genuine root stays valid)", () => {
    expect(projectDirectoryName({ worktree: "/", directory: "/", hostname: "dev1" })).toBe("f88226973f1cbf53eaf2c720");
  });

  it("known vector: the historical non-git collision hash is now reachable only via a genuine root directory", () => {
    expect(projectDirectoryName({ directory: "/", hostname: "remote-dev-server" })).toBe("23be191393b51993adc296ed");
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
