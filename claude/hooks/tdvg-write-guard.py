#!/usr/bin/env python3
"""PreToolUse write guard for the TDVG advisory Claude Code subagents.

Usage (from a subagent's `hooks` frontmatter):
    python3 "$HOME/.claude/hooks/tdvg-write-guard.py" <profile>

Profiles:
    reviewer    may only write Markdown files inside a `.agents/runs/` directory.
    tdd-expert  reviewer paths plus test files and test directories.

The hook reads the PreToolUse JSON from stdin. Allowed writes exit 0 silently;
blocked writes print one reason to stderr and exit 2. Anything unparseable or
unknown fails closed. Tools other than Write/Edit/MultiEdit/NotebookEdit are ignored.
"""

import fnmatch
import json
import os
import sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
TEST_DIRS = {"test", "tests", "__tests__", "__specs__", "spec", "specs"}
TEST_FILES = [
    "*.test.*", "*.spec.*", "test_*.py", "*_test.py", "*_test.go", "*_test.rs",
    *(f"*{suffix}.{ext}" for suffix in ("Test", "Tests") for ext in ("java", "kt", "cs", "php")),
]
PROFILES = {"reviewer", "tdd-expert"}


def is_run_report(parts):
    """Markdown file below a `.agents/runs` directory."""
    return parts[-1].endswith(".md") and any(
        parts[i : i + 2] == [".agents", "runs"] for i in range(len(parts) - 2)
    )


def is_test_path(parts):
    return bool(TEST_DIRS.intersection(parts[:-1])) or any(
        fnmatch.fnmatchcase(parts[-1], pattern) for pattern in TEST_FILES
    )


def block(reason):
    print(f"tdvg-write-guard: {reason}", file=sys.stderr)
    return 2


def main(argv):
    profile = argv[1] if len(argv) == 2 else None
    if profile not in PROFILES:
        return block(f"unknown or missing profile {profile!r}; expected one of {sorted(PROFILES)}")

    try:
        data = json.load(sys.stdin)
        tool = data["tool_name"]
        tool_input = data.get("tool_input") or {}
        cwd = data.get("cwd")
    except (ValueError, KeyError, AttributeError, TypeError):
        return block("unreadable hook input")

    if tool not in WRITE_TOOLS:
        return 0

    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(path, str) or not path:
        return block(f"{tool} without a target path")
    if not os.path.isabs(path):
        if not isinstance(cwd, str) or not os.path.isabs(cwd):
            return block(f"cannot resolve relative path {path!r} without cwd")
        path = os.path.join(cwd, path)

    resolved = os.path.realpath(path)
    parts = resolved.split(os.sep)
    if is_run_report(parts) or (profile == "tdd-expert" and is_test_path(parts)):
        return 0
    allowed = "Markdown in .agents/runs/" + (" or test files" if profile == "tdd-expert" else "")
    return block(f"{profile} may only write {allowed}; blocked {resolved}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
