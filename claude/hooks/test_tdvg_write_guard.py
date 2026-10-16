"""Tests for tdvg-write-guard.py; the hook is run as a subprocess, as Claude Code does."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).with_name("tdvg-write-guard.py")
CWD = "/work/project"


def run_hook(profile, stdin_text, args=None):
    argv = [sys.executable, str(HOOK)] + ([profile] if args is None else args)
    return subprocess.run(argv, input=stdin_text, capture_output=True, text=True)


def event(path, tool="Write", key="file_path", cwd=CWD):
    return json.dumps({"tool_name": tool, "tool_input": {key: path}, "cwd": cwd})


class GuardTestCase(unittest.TestCase):
    def assertAllowed(self, profile, path, **kwargs):
        result = run_hook(profile, event(path, **kwargs))
        self.assertEqual((result.returncode, result.stderr), (0, ""), path)

    def assertBlocked(self, profile, path, **kwargs):
        result = run_hook(profile, event(path, **kwargs))
        self.assertEqual(result.returncode, 2, path)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1, path)
        self.assertTrue(result.stderr.startswith("tdvg-write-guard:"), result.stderr)


class ReviewerProfile(GuardTestCase):
    def test_allows_markdown_in_runs_dir(self):
        self.assertAllowed("reviewer", "/work/project/.agents/runs/2026-10-09-x/reports/r.md")

    def test_blocks_source_file(self):
        self.assertBlocked("reviewer", "/work/project/src/app.py")

    def test_blocks_non_markdown_in_runs_dir(self):
        self.assertBlocked("reviewer", "/work/project/.agents/runs/x/run.sh")

    def test_blocks_markdown_outside_runs_dir(self):
        self.assertBlocked("reviewer", "/work/project/docs/README.md")

    def test_blocks_test_file(self):
        self.assertBlocked("reviewer", "/work/project/tests/test_app.py")

    def test_blocks_traversal_out_of_runs_dir(self):
        self.assertBlocked("reviewer", "/work/project/.agents/runs/../../src/x.md")

    def test_blocks_runs_dir_lookalike(self):
        self.assertBlocked("reviewer", "/work/project/.agents/runs-old/x.md")

    def test_relative_path_resolved_against_cwd(self):
        self.assertAllowed("reviewer", ".agents/runs/x/r.md")
        self.assertBlocked("reviewer", "src/x.md")

    def test_relative_traversal_blocked(self):
        self.assertBlocked("reviewer", ".agents/runs/../../src/x.md")

    def test_notebook_path_is_checked(self):
        self.assertAllowed("reviewer", ".agents/runs/x/n.md", tool="NotebookEdit", key="notebook_path")
        self.assertBlocked("reviewer", "analysis.ipynb", tool="NotebookEdit", key="notebook_path")

    def test_edit_and_multiedit_are_checked(self):
        for tool in ("Edit", "MultiEdit"):
            self.assertBlocked("reviewer", "/work/project/src/app.py", tool=tool)
            self.assertAllowed("reviewer", ".agents/runs/x/r.md", tool=tool)


class TddExpertProfile(GuardTestCase):
    ALLOWED = [
        ".agents/runs/x/r.md",
        "test/foo.txt",
        "pkg/tests/data.json",
        "web/__tests__/a.js",
        "web/__specs__/a.js",
        "spec/a.rb",
        "a/specs/b.rb",
        "src/app.test.ts",
        "src/app.spec.js",
        "pkg/test_app.py",
        "pkg/app_test.py",
        "pkg/app_test.go",
        "pkg/app_test.rs",
        "src/FooTest.java",
        "src/FooTests.java",
        "src/FooTest.kt",
        "src/FooTests.kt",
        "src/FooTest.cs",
        "src/FooTests.cs",
        "src/FooTest.php",
        "src/FooTests.php",
    ]
    BLOCKED = [
        "src/app.py",
        "src/contest/app.py",
        "src/latest.py",
        "src/testing.py",
        "src/Foo.java",
        "src/FooTest.rb",
        "docs/README.md",
        ".agents/runs/x/run.sh",
    ]

    def test_allows_runs_markdown_and_test_paths(self):
        for path in self.ALLOWED:
            with self.subTest(path=path):
                self.assertAllowed("tdd-expert", path)

    def test_blocks_production_paths(self):
        for path in self.BLOCKED:
            with self.subTest(path=path):
                self.assertBlocked("tdd-expert", path)

    def test_blocks_traversal_from_test_dir(self):
        self.assertBlocked("tdd-expert", "tests/../src/app.py")

    def test_reviewer_does_not_get_test_paths(self):
        self.assertBlocked("reviewer", "src/app.test.ts")


class FailClosed(GuardTestCase):
    def test_unknown_tools_are_ignored(self):
        for tool in ("Read", "Bash", "Grep"):
            self.assertAllowed("reviewer", "/work/project/src/app.py", tool=tool)

    def test_unparseable_input_blocks(self):
        for text in ("", "not json", "[]", "null"):
            with self.subTest(text=text):
                self.assertEqual(run_hook("reviewer", text).returncode, 2)

    def test_missing_path_blocks(self):
        text = json.dumps({"tool_name": "Write", "tool_input": {}, "cwd": CWD})
        self.assertEqual(run_hook("reviewer", text).returncode, 2)

    def test_missing_tool_input_blocks(self):
        text = json.dumps({"tool_name": "Write", "cwd": CWD})
        self.assertEqual(run_hook("reviewer", text).returncode, 2)

    def test_relative_path_without_cwd_blocks(self):
        text = json.dumps({"tool_name": "Write", "tool_input": {"file_path": ".agents/runs/r.md"}})
        self.assertEqual(run_hook("reviewer", text).returncode, 2)

    def test_unknown_profile_blocks(self):
        result = run_hook("admin", event(".agents/runs/x/r.md"))
        self.assertEqual(result.returncode, 2)

    def test_missing_profile_blocks(self):
        self.assertEqual(run_hook(None, event(".agents/runs/x/r.md"), args=[]).returncode, 2)


if __name__ == "__main__":
    unittest.main()
