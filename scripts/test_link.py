"""Tests for scripts/link.py (stdlib unittest; temp dirs only, never the real home).

Run:
    PYTHONDONTWRITEBYTECODE=1 uv run python -m unittest discover -s scripts -p 'test_*.py' -v
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rich.console import Console

SCRIPT = Path(__file__).resolve().with_name("link.py")
_spec = importlib.util.spec_from_file_location("link_under_test", SCRIPT)
link = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = link  # dataclasses resolve annotations via sys.modules
_spec.loader.exec_module(link)


class LinkTestCase(unittest.TestCase):
    """Points every HOME/repo-derived module constant at a temp dir."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        self.home = self.tmp / "home"
        self.repo.mkdir()
        self.home.mkdir()
        self.managed = self.tmp / "etc-opencode"
        oc_target = self.home / ".config" / "opencode"
        cl_target = self.home / ".claude"
        overrides = {
            "REPO_ROOT": self.repo,
            "HOME": self.home,
            "STATE_FILE": self.repo / "scripts" / ".link-state.json",
            "OPENCODE_SOURCE_DIR": self.repo / "opencode",
            "OPENCODE_TARGET_DIR": oc_target,
            "MANAGED_TARGET_DIR": self.managed,
            "CONFIG_FILE_MAP": {
                "tdvg-standards.json": oc_target / "config.json",
                "tdvg-required.json": self.managed / "opencode.jsonc",
            },
            "CLAUDE_SOURCE_DIR": self.repo / "claude",
            "CLAUDE_TARGET_DIR": cl_target,
            "MERGE_FILE_MAP": {
                "tdvg-settings.json": cl_target / "settings.json",
                "tdvg-mcp.json": self.home / ".claude.json",
            },
            "console": Console(file=io.StringIO(), width=200),
        }
        for name, value in overrides.items():
            patcher = mock.patch.object(link, name, value, create=True)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write(self, rel: str, text: str = "x") -> Path:
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def write_json(self, path: Path, data) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
        return path

    def read_json(self, path: Path):
        return json.loads(path.read_text())

    def output(self) -> str:
        return link.console.file.getvalue()


class DiscoveryTests(LinkTestCase):
    def test_claude_files_map_one_to_one_into_claude_dir(self):
        self.write("claude/CLAUDE.md")
        self.write("claude/agents/implementer.md")
        items = {i.key: i for i in link.discover_claude_items()}
        self.assertEqual(set(items), {"claude/CLAUDE.md", "claude/agents/implementer.md"})
        agent = items["claude/agents/implementer.md"]
        self.assertEqual(agent.target, self.home / ".claude" / "agents" / "implementer.md")
        self.assertEqual(agent.kind, "symlink")
        self.assertEqual(agent.label, "claude/agents/implementer.md")

    def test_claude_discovery_skips_repo_only_files(self):
        self.write("claude/hooks/guard.py")
        for skipped in (
            "claude/hooks/test_guard.py",
            "claude/hooks/guard_test.py",
            "claude/hooks/guard.test.ts",
            "claude/hooks/__pycache__/guard.cpython-314.pyc",
            "claude/hooks/stray.pyc",
        ):
            self.write(skipped)
        keys = [i.key for i in link.discover_claude_items()]
        self.assertEqual(keys, ["claude/hooks/guard.py"])

    def test_claude_configs_are_merge_items_with_fixed_targets(self):
        self.write("claude/configs/tdvg-settings.json", "{}")
        self.write("claude/configs/tdvg-mcp.json", "{}")
        self.write("claude/configs/unmapped.json", "{}")
        items = {i.key: i for i in link.discover_claude_items()}
        self.assertEqual(
            set(items),
            {"claude/configs/tdvg-settings.json", "claude/configs/tdvg-mcp.json"},
        )
        settings = items["claude/configs/tdvg-settings.json"]
        self.assertEqual(settings.kind, "merge")
        self.assertEqual(settings.target, self.home / ".claude" / "settings.json")
        self.assertEqual(
            items["claude/configs/tdvg-mcp.json"].target, self.home / ".claude.json"
        )

    def test_claude_discovery_without_source_dir_is_empty(self):
        self.assertEqual(link.discover_claude_items(), [])

    def test_opencode_discovery_is_unchanged(self):
        self.write("opencode/agents/a.md")
        self.write("opencode/plugins/p/x.ts")
        self.write("opencode/plugins/p/x.test.ts")
        self.write("opencode/configs/tdvg-standards.json", "{}")
        items = {i.key: i for i in link.discover_opencode_items()}
        self.assertEqual(
            set(items),
            {
                "opencode/agents/a.md",
                "opencode/plugins/p/x.ts",
                "opencode/configs/tdvg-standards.json",
            },
        )
        oc = self.home / ".config" / "opencode"
        self.assertEqual(items["opencode/agents/a.md"].target, oc / "agents" / "a.md")
        cfg = items["opencode/configs/tdvg-standards.json"]
        self.assertEqual(cfg.target, oc / "config.json")
        self.assertEqual(cfg.kind, "symlink")
        self.assertFalse(cfg.managed)

    def test_opencode_required_config_stays_managed(self):
        self.write("opencode/configs/tdvg-required.json", "{}")
        (item,) = link.discover_opencode_items()
        self.assertTrue(item.managed)


SETTINGS = {
    "$schema": "https://example.invalid/schema.json",
    "permissions": {"ask": ["Bash(rm *)"], "deny": ["Read(**/.env)", "Agent(claude)"]},
}
MCP = {"mcpServers": {"context7": {"type": "http", "url": "https://mcp.example/mcp"}}}


def decide(answer):
    """A conflict resolver that always answers `answer` and records the calls."""
    calls = []

    def resolve(path, existing, tdvg):
        calls.append((path, existing, tdvg))
        return answer

    resolve.calls = calls
    return resolve


class MergeJsonTests(unittest.TestCase):
    def test_absent_keys_are_set_leaf_by_leaf_without_schema(self):
        existing = {}
        records = link.merge_json(existing, SETTINGS, decide("keep"))
        self.assertEqual(
            existing,
            {"permissions": {"ask": ["Bash(rm *)"], "deny": ["Read(**/.env)", "Agent(claude)"]}},
        )
        self.assertEqual(
            records[0], {"path": ["permissions", "ask"], "op": "append", "value": "Bash(rm *)"}
        )
        self.assertEqual(len(records), 3)

    def test_absent_scalar_is_recorded_as_set_without_previous(self):
        existing = {}
        (record,) = link.merge_json(existing, {"a": {"b": 1}}, decide("keep"))
        self.assertEqual(
            record, {"path": ["a", "b"], "op": "set", "value": 1, "had_previous": False}
        )

    def test_arrays_are_unioned_in_order(self):
        existing = {"permissions": {"ask": ["mine", "Bash(rm *)"]}}
        records = link.merge_json(existing, SETTINGS, decide("keep"))
        self.assertEqual(existing["permissions"]["ask"], ["mine", "Bash(rm *)"])
        self.assertEqual(existing["permissions"]["deny"], ["Read(**/.env)", "Agent(claude)"])
        self.assertNotIn(["permissions", "ask"], [r["path"] for r in records])

    def test_equal_content_is_a_noop(self):
        existing = {"permissions": dict(SETTINGS["permissions"])}
        resolve = decide("overwrite")
        self.assertEqual(link.merge_json(existing, SETTINGS, resolve), [])
        self.assertEqual(resolve.calls, [])

    def test_foreign_keys_are_untouched(self):
        existing = {"hooks": {"Stop": [1]}, "permissions": {"allow": ["x"]}}
        link.merge_json(existing, SETTINGS, decide("keep"))
        self.assertEqual(existing["hooks"], {"Stop": [1]})
        self.assertEqual(existing["permissions"]["allow"], ["x"])

    def test_scalar_conflict_keep_leaves_value_and_records_nothing(self):
        existing = {"a": 1}
        resolve = decide("keep")
        self.assertEqual(link.merge_json(existing, {"a": 2}, resolve), [])
        self.assertEqual(existing, {"a": 1})
        self.assertEqual(resolve.calls, [(["a"], 1, 2)])

    def test_scalar_conflict_overwrite_records_previous(self):
        existing = {"a": 1}
        (record,) = link.merge_json(existing, {"a": 2}, decide("overwrite"))
        self.assertEqual(existing, {"a": 2})
        self.assertEqual(
            record,
            {"path": ["a"], "op": "set", "value": 2, "had_previous": True, "previous": 1},
        )

    def test_type_mismatch_is_a_conflict(self):
        for existing_value, tdvg_value in (("s", ["x"]), (["x"], "s"), ({"k": 1}, 5)):
            existing = {"a": existing_value}
            resolve = decide("keep")
            link.merge_json(existing, {"a": tdvg_value}, resolve)
            self.assertEqual(len(resolve.calls), 1, (existing_value, tdvg_value))

    def test_skip_aborts_the_whole_merge(self):
        with self.assertRaises(link.MergeSkipped):
            link.merge_json({"a": 1}, {"a": 2}, decide("skip"))


class MergeItemTests(LinkTestCase):
    def make_item(self, name="tdvg-settings.json", data=SETTINGS):
        src = self.write_json(self.repo / "claude" / "configs" / name, data)
        return next(i for i in link.discover_claude_items() if i.source == src.resolve())

    def fresh_state(self):
        return {"version": 3, "linked": [], "linked_items": [], "merged": {}}

    def backups(self, target: Path):
        return sorted(target.parent.glob(f"{target.name}.bak-*"))

    def test_missing_target_is_created_with_parents_and_state(self):
        item = self.make_item()
        state = self.fresh_state()
        self.assertEqual(link.merge_item(item, state), "created")
        self.assertEqual(self.read_json(item.target)["permissions"]["ask"], ["Bash(rm *)"])
        self.assertTrue(item.target.read_text().endswith("\n"))
        self.assertEqual(len(state["merged"][item.key]), 3)
        self.assertEqual(self.backups(item.target), [])

    def test_new_claude_json_gets_mode_0600(self):
        item = self.make_item("tdvg-mcp.json", MCP)
        link.merge_item(item, self.fresh_state())
        self.assertEqual(os.stat(item.target).st_mode & 0o777, 0o600)

    def test_existing_file_keeps_foreign_keys_mode_and_gets_backup(self):
        item = self.make_item()
        original = {"hooks": {"Stop": ["keep me"]}, "permissions": {"ask": ["mine"]}}
        self.write_json(item.target, original)
        os.chmod(item.target, 0o600)
        self.assertEqual(link.merge_item(item, self.fresh_state()), "created")
        merged = self.read_json(item.target)
        self.assertEqual(merged["hooks"], {"Stop": ["keep me"]})
        self.assertEqual(merged["permissions"]["ask"], ["mine", "Bash(rm *)"])
        self.assertEqual(os.stat(item.target).st_mode & 0o777, 0o600)
        (backup,) = self.backups(item.target)
        self.assertEqual(self.read_json(backup), original)
        self.assertEqual(
            [p.name for p in item.target.parent.iterdir() if p.name.endswith(".tmp")], []
        )

    def test_symlinked_target_is_written_through_and_stays_a_symlink(self):
        item = self.make_item()
        real = self.write_json(self.tmp / "dotfiles" / "settings.json", {"x": 1})
        item.target.parent.mkdir(parents=True)
        item.target.symlink_to(real)
        link.merge_item(item, self.fresh_state())
        self.assertTrue(item.target.is_symlink())
        self.assertEqual(self.read_json(real)["x"], 1)
        self.assertIn("permissions", self.read_json(real))

    def test_invalid_json_target_is_refused_and_untouched(self):
        item = self.make_item()
        item.target.parent.mkdir(parents=True)
        item.target.write_text("{ not json")
        state = self.fresh_state()
        self.assertEqual(link.merge_item(item, state), "error")
        self.assertEqual(item.target.read_text(), "{ not json")
        self.assertEqual(self.backups(item.target), [])
        self.assertEqual(state["merged"], {})

    def test_non_object_target_is_refused(self):
        item = self.make_item()
        self.write_json(item.target, [1, 2])
        self.assertEqual(link.merge_item(item, self.fresh_state()), "error")
        self.assertEqual(self.read_json(item.target), [1, 2])

    def test_second_run_is_a_noop_without_new_backup_or_records(self):
        item = self.make_item()
        state = self.fresh_state()
        link.merge_item(item, state)
        before = item.target.read_text()
        self.assertEqual(link.merge_item(item, state), "ok")
        self.assertEqual(item.target.read_text(), before)
        self.assertEqual(self.backups(item.target), [])
        self.assertEqual(len(state["merged"][item.key]), 3)

    def test_conflict_keep_writes_the_rest_and_keeps_existing(self):
        item = self.make_item("tdvg-mcp.json", MCP)
        self.write_json(item.target, {"mcpServers": {"context7": {"type": "sse"}}})
        with mock.patch.object(link, "prompt_merge_conflict", return_value="keep"):
            link.merge_item(item, self.fresh_state())
        server = self.read_json(item.target)["mcpServers"]["context7"]
        self.assertEqual(server, {"type": "sse", "url": "https://mcp.example/mcp"})

    def test_conflict_overwrite_replaces_value(self):
        item = self.make_item("tdvg-mcp.json", MCP)
        self.write_json(item.target, {"mcpServers": {"context7": {"type": "sse"}}})
        with mock.patch.object(link, "prompt_merge_conflict", return_value="overwrite"):
            link.merge_item(item, self.fresh_state())
        self.assertEqual(self.read_json(item.target)["mcpServers"]["context7"]["type"], "http")

    def test_conflict_skip_leaves_file_untouched(self):
        item = self.make_item("tdvg-mcp.json", MCP)
        self.write_json(item.target, {"mcpServers": {"context7": {"type": "sse"}}})
        before = item.target.read_text()
        state = self.fresh_state()
        with mock.patch.object(link, "prompt_merge_conflict", return_value="skip"):
            self.assertEqual(link.merge_item(item, state), "skip")
        self.assertEqual(item.target.read_text(), before)
        self.assertEqual(self.backups(item.target), [])
        self.assertEqual(state["merged"], {})

    def test_cancelled_conflict_prompt_counts_as_skip(self):
        item = self.make_item("tdvg-mcp.json", MCP)
        self.write_json(item.target, {"mcpServers": {"context7": {"type": "sse"}}})
        with mock.patch.object(link, "prompt_merge_conflict", return_value=None):
            self.assertEqual(link.merge_item(item, self.fresh_state()), "skip")


class RevertMergeTests(unittest.TestCase):
    def merged(self, original, tdvg, answer="overwrite"):
        data = json.loads(json.dumps(original))
        return data, link.merge_json(data, tdvg, decide(answer))

    def test_revert_restores_the_original_exactly(self):
        original = {"hooks": {"Stop": [1]}, "permissions": {"ask": ["mine"]}}
        data, records = self.merged(original, SETTINGS)
        self.assertNotEqual(data, original)
        self.assertEqual(link.revert_merge(data, records), [])
        self.assertEqual(data, original)

    def test_revert_prunes_containers_that_became_empty(self):
        data, records = self.merged({}, {**SETTINGS, **MCP})
        link.revert_merge(data, records)
        self.assertEqual(data, {})

    def test_revert_keeps_non_empty_containers(self):
        data, records = self.merged({"mcpServers": {"mine": {"type": "stdio"}}}, MCP)
        link.revert_merge(data, records)
        self.assertEqual(data, {"mcpServers": {"mine": {"type": "stdio"}}})

    def test_revert_restores_overwritten_previous_value(self):
        data, records = self.merged({"a": {"b": 1}}, {"a": {"b": 2}})
        self.assertEqual(data["a"]["b"], 2)
        link.revert_merge(data, records)
        self.assertEqual(data, {"a": {"b": 1}})

    def test_revert_leaves_value_the_user_changed_and_warns(self):
        data, records = self.merged({}, {"a": 1})
        data["a"] = 99
        warnings = link.revert_merge(data, records)
        self.assertEqual(data, {"a": 99})
        self.assertEqual(len(warnings), 1)
        self.assertIn("a", warnings[0])

    def test_revert_ignores_entries_already_removed(self):
        data, records = self.merged({}, SETTINGS)
        data["permissions"]["ask"].remove("Bash(rm *)")
        self.assertEqual(link.revert_merge(data, records), [])
        self.assertNotIn("permissions", data)

    def test_revert_keeps_user_entries_added_to_a_list_we_created(self):
        data, records = self.merged({}, SETTINGS)
        data["permissions"]["deny"].append("mine")
        link.revert_merge(data, records)
        self.assertEqual(data, {"permissions": {"deny": ["mine"]}})


class UnlinkMergeTests(LinkTestCase):
    def setUp(self):
        super().setUp()
        self.mcp_src = self.write_json(self.repo / "claude/configs/tdvg-mcp.json", MCP)
        self.write_json(self.repo / "claude/configs/tdvg-settings.json", SETTINGS)
        self.items = {i.key: i for i in link.discover_claude_items()}
        self.item = self.items["claude/configs/tdvg-mcp.json"]

    def link_merge(self, original=None):
        if original is not None:
            self.write_json(self.item.target, original)
        state = link.load_state()
        self.assertEqual(link.merge_item(self.item, state), "created")
        link.save_state(state)

    def unlink(self, *keys):
        return link.cmd_unlink(None, None, None, list(keys) or None)

    def test_unlink_reverts_exactly_and_forgets_state(self):
        original = {"numStartups": 3, "mcpServers": {"mine": {"type": "stdio"}}}
        self.link_merge(original)
        self.assertEqual(self.unlink(), 0)
        self.assertEqual(self.read_json(self.item.target), original)
        self.assertEqual(link.load_state()["merged"], {})

    def test_unlink_removes_file_content_we_created_but_keeps_the_file(self):
        self.link_merge()
        self.unlink()
        self.assertEqual(self.read_json(self.item.target), {})

    def test_unlink_restores_previous_value_after_overwrite(self):
        original = {"mcpServers": {"context7": {"type": "sse"}}}
        self.write_json(self.item.target, original)
        state = link.load_state()
        with mock.patch.object(link, "prompt_merge_conflict", return_value="overwrite"):
            link.merge_item(self.item, state)
        link.save_state(state)
        self.assertEqual(self.read_json(self.item.target)["mcpServers"]["context7"]["type"], "http")
        self.unlink()
        self.assertEqual(self.read_json(self.item.target), original)

    def test_unlink_leaves_values_changed_since_and_warns(self):
        self.link_merge()
        data = self.read_json(self.item.target)
        data["mcpServers"]["context7"]["url"] = "https://mine.example"
        self.write_json(self.item.target, data)
        self.unlink()
        after = self.read_json(self.item.target)
        self.assertEqual(after, {"mcpServers": {"context7": {"url": "https://mine.example"}}})
        self.assertIn("mcpServers.context7.url", self.output())

    def test_unlink_writes_a_backup_before_changing(self):
        self.link_merge({"numStartups": 1})
        self.unlink()
        self.assertEqual(len(list(self.item.target.parent.glob(".claude.json.bak-*"))), 2)

    def test_unlink_invalid_json_keeps_state_and_file(self):
        self.link_merge()
        self.item.target.write_text("{ broken")
        self.unlink()
        self.assertEqual(self.item.target.read_text(), "{ broken")
        self.assertIn(self.item.key, link.load_state()["merged"])

    def test_unlink_missing_target_drops_state(self):
        self.link_merge()
        self.item.target.unlink()
        self.unlink()
        self.assertEqual(link.load_state()["merged"], {})
        self.assertFalse(self.item.target.exists())

    def test_claude_arg_selects_only_that_merge_item(self):
        settings = self.items["claude/configs/tdvg-settings.json"]
        state = link.load_state()
        link.merge_item(self.item, state)
        link.merge_item(settings, state)
        link.save_state(state)
        self.unlink("claude/configs/tdvg-mcp.json")
        self.assertEqual(list(link.load_state()["merged"]), [settings.key])

    def test_unknown_claude_key_is_an_error(self):
        self.link_merge()
        self.assertEqual(self.unlink("claude/nope.md"), 1)

    def test_unlink_removes_tracked_claude_symlinks(self):
        src = self.write("claude/agents/implementer.md")
        target = self.home / ".claude" / "agents" / "implementer.md"
        target.parent.mkdir(parents=True)
        target.symlink_to(src)
        state = link.load_state()
        link.state_record_item(state, "claude/agents/implementer.md")
        link.save_state(state)
        self.unlink("claude/agents/implementer.md")
        self.assertFalse(target.is_symlink())

    def test_opencode_arg_does_not_drop_tracked_claude_items(self):
        state = link.load_state()
        link.state_record_item(state, "claude/CLAUDE.md")
        link.state_record_item(state, "opencode/agents/a.md")
        link.save_state(state)
        self.write("opencode/agents/a.md")
        link.cmd_unlink(None, None, ["opencode/agents/a.md"])
        self.assertEqual(link.load_state()["linked_items"], ["claude/CLAUDE.md"])


class ClassifyMergeTests(LinkTestCase):
    def setUp(self):
        super().setUp()
        self.write_json(self.repo / "claude/configs/tdvg-settings.json", SETTINGS)
        (self.item,) = link.discover_claude_items()

    def test_missing_target_is_none(self):
        self.assertEqual(link.classify_merge(self.item), "merge_none")

    def test_fully_merged_is_ok(self):
        link.merge_item(self.item, link.load_state())
        self.assertEqual(link.classify_merge(self.item), "merge_ok")

    def test_foreign_content_only_is_none(self):
        self.write_json(self.item.target, {"hooks": {}})
        self.assertEqual(link.classify_merge(self.item), "merge_none")

    def test_some_entries_present_is_partial(self):
        self.write_json(self.item.target, {"permissions": {"ask": ["Bash(rm *)"]}})
        self.assertEqual(link.classify_merge(self.item), "merge_partial")

    def test_conflicting_value_next_to_present_entries_is_partial(self):
        self.write_json(self.item.target, {"permissions": {"ask": "oops", "deny": ["Agent(claude)"]}})
        self.assertEqual(link.classify_merge(self.item), "merge_partial")

    def test_invalid_json_is_flagged(self):
        self.item.target.parent.mkdir(parents=True)
        self.item.target.write_text("{ broken")
        self.assertEqual(link.classify_merge(self.item), "merge_invalid")


class CliTests(LinkTestCase):
    def setUp(self):
        super().setUp()
        self.agent_src = self.write("claude/agents/implementer.md")
        self.write_json(self.repo / "claude/configs/tdvg-settings.json", SETTINGS)
        self.write_json(self.repo / "claude/configs/tdvg-mcp.json", MCP)
        self.agent_key = "claude/agents/implementer.md"
        self.settings_key = "claude/configs/tdvg-settings.json"
        self.mcp_key = "claude/configs/tdvg-mcp.json"

    def link_claude(self, claude_arg=None, skip_claude=False):
        return link.cmd_link(None, None, None, True, True, claude_arg, skip_claude)

    def test_link_with_claude_arg_links_symlinks_and_merges(self):
        rc = self.link_claude([self.agent_key, self.settings_key])
        self.assertEqual(rc, 0)
        target = self.home / ".claude" / "agents" / "implementer.md"
        self.assertEqual(target.resolve(), self.agent_src.resolve())
        self.assertIn("permissions", self.read_json(self.home / ".claude" / "settings.json"))
        state = link.load_state()
        self.assertEqual(state["linked_items"], [self.agent_key])
        self.assertEqual(list(state["merged"]), [self.settings_key])
        self.assertFalse((self.home / ".claude.json").exists())

    def test_unknown_claude_key_fails_without_changes(self):
        self.assertEqual(self.link_claude([self.agent_key, "claude/nope.md"]), 1)
        self.assertFalse((self.home / ".claude").exists())

    def test_skip_claude_touches_nothing(self):
        self.assertEqual(self.link_claude(skip_claude=True), 0)
        self.assertFalse((self.home / ".claude").exists())

    def test_interactive_selection_prompts_claude_items(self):
        with mock.patch.object(link, "prompt_items") as prompt:
            prompt.return_value = [
                i for i in link.discover_claude_items() if i.key == self.agent_key
            ]
            self.link_claude()
        shown = {i.key for i in prompt.call_args.args[0]}
        self.assertEqual(shown, {self.agent_key, self.settings_key, self.mcp_key})
        self.assertTrue((self.home / ".claude" / "agents" / "implementer.md").is_symlink())
        self.assertFalse((self.home / ".claude" / "settings.json").exists())

    def test_claude_json_needs_confirmation_when_selected_interactively(self):
        chosen = [i for i in link.discover_claude_items() if i.key == self.mcp_key]
        with mock.patch.object(link, "prompt_items", return_value=chosen), \
                mock.patch.object(link, "confirm_claude_json", return_value=False) as confirm:
            self.link_claude()
        confirm.assert_called_once()
        self.assertFalse((self.home / ".claude.json").exists())
        self.assertIn("Close all Claude Code", self.output())

    def test_claude_json_is_merged_after_confirmation(self):
        chosen = [i for i in link.discover_claude_items() if i.key == self.mcp_key]
        with mock.patch.object(link, "prompt_items", return_value=chosen), \
                mock.patch.object(link, "confirm_claude_json", return_value=True):
            self.link_claude()
        self.assertIn("context7", self.read_json(self.home / ".claude.json")["mcpServers"])

    def test_claude_json_with_explicit_arg_warns_but_does_not_prompt(self):
        with mock.patch.object(link, "confirm_claude_json") as confirm:
            self.link_claude([self.mcp_key])
        confirm.assert_not_called()
        self.assertIn("Close all Claude Code", self.output())
        self.assertTrue((self.home / ".claude.json").exists())

    def test_status_renders_claude_table_with_kinds_and_marks(self):
        self.link_claude([self.settings_key])
        self.write_json(self.home / ".claude.json", {"mcpServers": {"context7": {"type": "http"}}})
        link.console.file.seek(0)
        link.console.file.truncate()
        self.assertEqual(link.cmd_status(), 0)
        rows = {
            key: next(line for line in self.output().splitlines() if key in line)
            for key in ("implementer.md", "tdvg-settings.json", "tdvg-mcp.json")
        }
        self.assertIn("Claude sync status", self.output())
        self.assertRegex(rows["implementer.md"], r"symlink\s+│\s+·")
        self.assertRegex(rows["tdvg-settings.json"], r"merge\s+│\s+✓ \*")
        self.assertRegex(rows["tdvg-mcp.json"], r"merge\s+│\s+~")  # url missing

    def test_list_shows_claude_items(self):
        self.assertEqual(link.cmd_list(), 0)
        out = self.output()
        self.assertIn("Claude items in repo (3)", out)
        self.assertIn(self.agent_key, out)

    def test_parser_accepts_claude_flags(self):
        parser = link.build_parser()
        args = parser.parse_args(["link", "--claude=a,b", "--skip-claude"])
        self.assertEqual((args.claude, args.skip_claude), ("a,b", True))
        self.assertEqual(parser.parse_args(["unlink", "--claude=a"]).claude, "a")


class StateTests(LinkTestCase):
    def write_state(self, data):
        self.write_json(link.STATE_FILE, data)

    def test_fresh_state_is_v3_with_merged(self):
        self.assertEqual(
            link.load_state(),
            {"version": 3, "linked": [], "linked_items": [], "merged": {}},
        )

    def test_v2_state_migrates_transparently(self):
        self.write_state({"version": 2, "linked": [["s", "agents"]], "linked_items": ["opencode/a.md"]})
        state = link.load_state()
        self.assertEqual(state["version"], 3)
        self.assertEqual(state["linked"], [["s", "agents"]])
        self.assertEqual(state["linked_items"], ["opencode/a.md"])
        self.assertEqual(state["merged"], {})

    def test_v1_state_migrates_transparently(self):
        self.write_state({"version": 1, "linked": [["s", "agents"]]})
        state = link.load_state()
        self.assertEqual(state["version"], 3)
        self.assertEqual(state["linked"], [["s", "agents"]])
        self.assertEqual(state["linked_items"], [])
        self.assertEqual(state["merged"], {})

    def test_v3_state_round_trips(self):
        state = link.load_state()
        link.state_record_merge(state, "claude/configs/x.json", {"path": ["a"], "op": "set"})
        link.save_state(state)
        self.assertEqual(link.load_state()["merged"]["claude/configs/x.json"], [{"path": ["a"], "op": "set"}])

    def test_unknown_future_version_is_ignored(self):
        self.write_state({"version": 99, "linked": [["s", "agents"]]})
        self.assertEqual(link.load_state()["linked"], [])


if __name__ == "__main__":
    unittest.main()
