#!/usr/bin/env python3
"""Link AI agent skills from this repo into harness-specific global directories.

Usage:
    uv run scripts/link.py status
    uv run scripts/link.py link
    uv run scripts/link.py unlink
    uv run scripts/link.py list

The script symlinks individual skill folders from `<repo>/skills/<name>/` into
the global skills directory of each selected agent harness. It is idempotent:
existing correct symlinks are kept, broken symlinks are repaired, and real
files/dirs trigger an interactive prompt before being replaced.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import questionary
from questionary import Choice
from rich.console import Console
from rich.table import Table

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_SOURCE_DIR = REPO_ROOT / "skills"
STATE_FILE = REPO_ROOT / "scripts" / ".link-state.json"
BACKUP_SUFFIX = ".bak"


@dataclass(frozen=True)
class Harness:
    """A single agent harness and its global skills directory."""

    key: str
    name: str
    global_dir: Path
    # Whether this harness also reads the universal ~/.agents/skills/ path.
    reads_agents_dir: bool = False
    # Short note shown in the UI / used for path validation messaging.
    note: str = ""


HOME = Path.home()
AGENTS_GLOBAL = HOME / ".agents" / "skills"


def _harnesses() -> dict[str, Harness]:
    """Return the supported harnesses keyed by their short key.

    Paths are based on official docs (see research notes in the PR):
      - OpenCode:   ~/.config/opencode/skills/, ~/.claude/skills/, ~/.agents/skills/
      - Zed:        ~/.agents/skills/  (only global path)
      - Codex CLI:  ~/.agents/skills/  (USER) + /etc/codex/skills/ (ADMIN)
      - Copilot:    ~/.copilot/skills/, ~/.claude/skills/, ~/.agents/skills/
      - Cursor:     ~/.cursor/skills/  (+ reads ~/.agents/skills/)
      - Gemini CLI: ~/.gemini/skills/   (+ reads .agents alias)
      - Claude Code:~/.claude/skills/   (does NOT read ~/.agents)
      - Windsurf:   ~/.codeium/windsurf/skills/   (does NOT read ~/.agents)
      - Antigravity:~/.gemini/config/skills/      (does NOT read ~/.agents globally)
    """
    return {
        "agents": Harness(
            key="agents",
            name="Universal ~/.agents/skills (OpenCode, Zed, Codex, Copilot, Cursor, Gemini)",
            global_dir=AGENTS_GLOBAL,
            reads_agents_dir=True,
            note="Universal path read by 6 harnesses.",
        ),
        "claude": Harness(
            key="claude",
            name="Claude Code",
            global_dir=HOME / ".claude" / "skills",
            note="Does NOT read ~/.agents/skills; needs its own symlink.",
        ),
        "windsurf": Harness(
            key="windsurf",
            name="Windsurf (Cascade)",
            global_dir=HOME / ".codeium" / "windsurf" / "skills",
            note="Does NOT read ~/.agents/skills; needs its own symlink.",
        ),
        "antigravity": Harness(
            key="antigravity",
            name="Google Antigravity",
            global_dir=HOME / ".gemini" / "config" / "skills",
            note="Does NOT read ~/.agents globally; needs its own symlink.",
        ),
    }


# Order in which harnesses are presented in the UI.
HARNESS_ORDER = ["agents", "claude", "windsurf", "antigravity"]


# --------------------------------------------------------------------------- #
# Console
# --------------------------------------------------------------------------- #

console = Console()


# --------------------------------------------------------------------------- #
# Skill discovery
# --------------------------------------------------------------------------- #


def discover_repo_skills() -> list[str]:
    """Return the sorted list of skill names available in <repo>/skills/.

    A skill is a direct subdirectory containing a SKILL.md (any case, but the
    spec requires uppercase). We accept SKILL.md only.
    """
    if not SKILLS_SOURCE_DIR.is_dir():
        return []
    names: list[str] = []
    for entry in sorted(SKILLS_SOURCE_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if (entry / "SKILL.md").is_file():
            names.append(entry.name)
    return names


# --------------------------------------------------------------------------- #
# Path / conflict helpers
# --------------------------------------------------------------------------- #


def classify_target(path: Path) -> str:
    """Classify what currently sits at a target path.

    Returns one of:
      - "missing"        nothing there
      - "symlink_ok"     symlink pointing at the expected repo skill
      - "symlink_other"  symlink pointing somewhere else
      - "symlink_broken"  symlink that resolves to nothing
      - "real_dir"       real directory (not a symlink)
      - "real_file"      real file (not a symlink)
    """
    if not path.exists() and not path.is_symlink():
        return "missing"
    if path.is_symlink():
        target = path.resolve()
        expected = (SKILLS_SOURCE_DIR / path.name).resolve()
        if not target.exists():
            return "symlink_broken"
        if target == expected:
            return "symlink_ok"
        return "symlink_other"
    if path.is_dir():
        return "real_dir"
    return "real_file"


def expected_target(skill: str, harness: Harness) -> Path:
    """The absolute path where a skill symlink should live for a harness."""
    return harness.global_dir / skill


# --------------------------------------------------------------------------- #
# Symlink primitives
# --------------------------------------------------------------------------- #


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def make_backup(path: Path) -> Path:
    """Move an existing real file/dir aside to <path>.bak-<timestamp>."""
    import time

    ts = int(time.time())
    backup = path.with_name(f"{path.name}{BACKUP_SUFFIX}-{ts}")
    # Avoid clobbering an existing backup.
    i = 1
    while backup.exists():
        backup = path.with_name(f"{path.name}{BACKUP_SUFFIX}-{ts}-{i}")
        i += 1
    path.rename(backup)
    return backup


def create_symlink(skill: str, harness: Harness) -> Path:
    """Create a symlink <harness.global_dir>/<skill> -> repo/skills/<skill>."""
    target = expected_target(skill, harness)
    source = (SKILLS_SOURCE_DIR / skill).resolve()
    ensure_parent_dir(target)
    if target.is_symlink() or target.exists():
        target.unlink()
    target.symlink_to(source)
    return target


def remove_symlink(skill: str, harness: Harness) -> bool:
    """Remove a symlink for a skill in a harness dir. Returns True if removed."""
    target = expected_target(skill, harness)
    if target.is_symlink():
        target.unlink()
        return True
    return False


# --------------------------------------------------------------------------- #
# State persistence
# --------------------------------------------------------------------------- #

STATE_VERSION = 1


def load_state() -> dict:
    """Load persisted link state: which (skill, harness) pairs were linked."""
    import json

    if not STATE_FILE.exists():
        return {"version": STATE_VERSION, "linked": []}
    try:
        data = json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"version": STATE_VERSION, "linked": []}
    if data.get("version") != STATE_VERSION:
        return {"version": STATE_VERSION, "linked": []}
    data.setdefault("linked", [])
    return data


def save_state(state: dict) -> None:
    import json

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def state_record(state: dict, skill: str, harness_key: str) -> None:
    pair = [skill, harness_key]
    if pair not in state["linked"]:
        state["linked"].append(pair)


def state_forget(state: dict, skill: str, harness_key: str) -> None:
    pair = [skill, harness_key]
    while pair in state["linked"]:
        state["linked"].remove(pair)


# --------------------------------------------------------------------------- #
# Harness detection + validation
# --------------------------------------------------------------------------- #


def detect_harnesses() -> set[str]:
    """Auto-detect which harnesses appear installed on this machine.

    We look for the parent config dir that each tool creates on install
    (e.g. ~/.claude for Claude Code). Presence of the skills dir itself is
    not required — the script can create it.
    """
    detected: set[str] = set()
    markers: dict[str, Path] = {
        "agents": HOME / ".agents",
        "claude": HOME / ".claude",
        "windsurf": HOME / ".codeium",
        "antigravity": HOME / ".gemini",
    }
    for key, marker in markers.items():
        if marker.exists():
            detected.add(key)
    return detected


def validate_harness_path(harness: Harness) -> Optional[str]:
    """Return a warning string if the harness path looks unsupported.

    We currently validate the universal `agents` harness lightly (always OK,
    since creating ~/.agents/skills is fine) and otherwise just confirm the
    parent dir is writable.
    """
    parent = harness.global_dir.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return f"Cannot create {parent} (permission error?)."
    if not os.access(parent, os.W_OK):
        return f"{parent} is not writable."
    return None


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def render_status(skills: list[str], harnesses: dict[str, Harness]) -> None:
    """Print a table of every (skill, harness) cell and its current state."""
    table = Table(title="Skill link status", show_lines=False)
    table.add_column("Skill", style="bold")
    for key in HARNESS_ORDER:
        table.add_column(harnesses[key].name.split(" (")[0])

    state = load_state()
    linked_pairs = {tuple(p) for p in state["linked"]}

    for skill in skills:
        row = [skill]
        for key in HARNESS_ORDER:
            harness = harnesses[key]
            target = expected_target(skill, harness)
            cls = classify_target(target)
            mark = {
                "missing": "[dim]·[/dim]",
                "symlink_ok": "[green]✓[/green]",
                "symlink_other": "[yellow]↗[/yellow]",
                "symlink_broken": "[red]✗[/red]",
                "real_dir": "[red]D[/red]",
                "real_file": "[red]F[/red]",
            }[cls]
            tracked = (skill, key) in linked_pairs
            tag = "[blue]*[/blue]" if tracked else " "
            row.append(f"{mark} {tag}")
        table.add_row(*row)
    console.print(table)
    console.print(
        "[green]✓[/green]=linked  [dim]·[/dim]=missing  "
        "[yellow]↗[/yellow]=symlink→other  [red]✗[/red]=broken  "
        "[red]D[/red]=real dir  [red]F[/red]=real file  [blue]*[/blue]=tracked"
    )


# --------------------------------------------------------------------------- #
# Interactive prompts
# --------------------------------------------------------------------------- #


def prompt_skills(skills: list[str]) -> list[str]:
    """Step 1: choose which skills to link."""
    choices = []
    for skill in skills:
        target = (SKILLS_SOURCE_DIR / skill).resolve()
        choices.append(Choice(title=skill, value=skill, checked=True))
    selected = questionary.checkbox(
        "Select skills to link:",
        choices=choices,
    ).ask()
    if selected is None:
        return []
    return selected


def prompt_harnesses(
    harnesses: dict[str, Harness],
    detected: set[str],
) -> list[str]:
    """Step 2: choose which harnesses to link into."""
    choices = []
    for key in HARNESS_ORDER:
        h = harnesses[key]
        is_detected = key in detected
        title = f"{h.name}  [{'detected' if is_detected else 'not detected'}]"
        choices.append(
            Choice(
                title=title,
                value=key,
                checked=is_detected,
            )
        )
    selected = questionary.checkbox(
        "Select target harnesses:",
        choices=choices,
    ).ask()
    if selected is None:
        return []
    return selected


def prompt_conflict(skill: str, harness: Harness, cls: str) -> str:
    """Ask what to do with an existing real file/dir at the target.

    Returns one of: "backup", "overwrite", "skip".
    """
    target = expected_target(skill, harness)
    label = {"real_dir": "real directory", "real_file": "real file"}[cls]
    return questionary.select(
        f"Conflict for [bold]{skill}[/bold] in {target.parent}: "
        f"a {label} already exists. What now?",
        choices=[
            Choice("Backup then replace (recommended)", value="backup"),
            Choice("Overwrite (delete without backup)", value="overwrite"),
            Choice("Skip this one", value="skip"),
        ],
    ).ask()


# --------------------------------------------------------------------------- #
# Commands: link / unlink / list / status
# --------------------------------------------------------------------------- #


def cmd_link(skills_arg: Optional[list[str]], harness_arg: Optional[list[str]]) -> int:
    harnesses = _harnesses()
    skills = discover_repo_skills()
    if not skills:
        console.print("[red]No skills found in[/red] " + str(SKILLS_SOURCE_DIR))
        return 1

    # --- Step 1: skills ---
    if skills_arg:
        unknown = set(skills_arg) - set(skills)
        if unknown:
            console.print(f"[red]Unknown skills:[/red] {', '.join(unknown)}")
            return 1
        chosen_skills = skills_arg
    else:
        chosen_skills = prompt_skills(skills)
        if not chosen_skills:
            console.print("[yellow]No skills selected. Aborting.[/yellow]")
            return 0

    # --- Step 2: harnesses ---
    detected = detect_harnesses()
    if harness_arg:
        unknown = set(harness_arg) - set(harnesses)
        if unknown:
            console.print(f"[red]Unknown harnesses:[/red] {', '.join(unknown)}")
            return 1
        chosen_harness_keys = harness_arg
    else:
        chosen_harness_keys = prompt_harnesses(harnesses, detected)
        if not chosen_harness_keys:
            console.print("[yellow]No harnesses selected. Aborting.[/yellow]")
            return 0

    # Validate harness paths.
    for key in chosen_harness_keys:
        warn = validate_harness_path(harnesses[key])
        if warn:
            console.print(f"[yellow]Warning ({harnesses[key].name}): {warn}[/yellow]")

    state = load_state()
    created = 0
    skipped = 0
    backed_up = 0
    already_ok = 0

    for skill in chosen_skills:
        for key in chosen_harness_keys:
            harness = harnesses[key]
            target = expected_target(skill, harness)
            cls = classify_target(target)
            if cls == "symlink_ok":
                state_record(state, skill, key)
                already_ok += 1
                console.print(
                    f"[green]✓[/green] {skill} → {key} (already linked)"
                )
                continue
            if cls in ("real_dir", "real_file"):
                action = prompt_conflict(skill, harness, cls)
                if action == "skip":
                    skipped += 1
                    console.print(f"[dim]↷ skip {skill} → {key}[/dim]")
                    continue
                if action == "backup":
                    backup = make_backup(target)
                    backed_up += 1
                    console.print(
                        f"[blue]⟲ backup → {backup.name}[/blue]"
                    )
                # overwrite: just unlink below
            # cls is missing / symlink_broken / symlink_other / after backup
            try:
                create_symlink(skill, harness)
            except OSError as exc:
                console.print(f"[red]✗ {skill} → {key}: {exc}[/red]")
                continue
            state_record(state, skill, key)
            created += 1
            console.print(f"[green]✓ link {skill} → {key}[/green]")

    save_state(state)
    console.print(
        f"\n[bold]Done.[/bold] created={created} already_ok={already_ok} "
        f"backed_up={backed_up} skipped={skipped}"
    )
    return 0


def cmd_unlink(
    skills_arg: Optional[list[str]],
    harness_arg: Optional[list[str]],
) -> int:
    harnesses = _harnesses()
    state = load_state()
    linked = list(state["linked"])

    if not linked:
        console.print("[yellow]Nothing tracked as linked. Nothing to do.[/yellow]")
        return 0

    # Filter by args.
    if skills_arg or harness_arg:
        filtered = []
        for skill, key in linked:
            if skills_arg and skill not in skills_arg:
                continue
            if harness_arg and key not in harness_arg:
                continue
            filtered.append((skill, key))
        linked = filtered

    if not linked:
        console.print("[yellow]No matching tracked links to unlink.[/yellow]")
        return 0

    removed = 0
    for skill, key in linked:
        harness = harnesses.get(key)
        if not harness:
            continue
        target = expected_target(skill, harness)
        cls = classify_target(target)
        if cls in ("symlink_ok", "symlink_broken", "symlink_other"):
            target.unlink()
            removed += 1
            console.print(f"[green]✓ unlinked {skill} from {key}[/green]")
        else:
            console.print(
                f"[dim]↷ {skill} in {key} is {cls}, leaving as-is[/dim]"
            )
        state_forget(state, skill, key)

    save_state(state)
    console.print(f"\n[bold]Done.[/bold] removed={removed}")
    return 0


def cmd_list() -> int:
    harnesses = _harnesses()
    detected = detect_harnesses()
    table = Table(title="Supported harnesses")
    table.add_column("Key")
    table.add_column("Name")
    table.add_column("Global path")
    table.add_column("Detected")
    table.add_column("Reads ~/.agents")
    for key in HARNESS_ORDER:
        h = harnesses[key]
        table.add_row(
            key,
            h.name,
            str(h.global_dir),
            "[green]yes[/green]" if key in detected else "[dim]no[/dim]",
            "yes" if h.reads_agents_dir else "no",
        )
    console.print(table)

    skills = discover_repo_skills()
    console.print(f"\n[bold]Skills in repo ({len(skills)}):[/bold]")
    for s in skills:
        console.print(f"  - {s}")
    return 0


def cmd_status() -> int:
    harnesses = _harnesses()
    skills = discover_repo_skills()
    if not skills:
        console.print("[red]No skills found in[/red] " + str(SKILLS_SOURCE_DIR))
        return 1
    render_status(skills, harnesses)
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _parse_csv(value: Optional[str]) -> Optional[list[str]]:
    if value is None:
        return None
    parts = [v.strip() for v in value.split(",") if v.strip()]
    return parts or None


def build_parser():
    import argparse

    p = argparse.ArgumentParser(
        prog="link.py",
        description="Symlink AI skills from this repo into harness global dirs.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show current link status table.")
    p_status.set_defaults(func=lambda a: cmd_status())

    p_list = sub.add_parser("list", help="List supported harnesses and skills.")
    p_list.set_defaults(func=lambda a: cmd_list())

    p_link = sub.add_parser("link", help="Create skill symlinks.")
    p_link.add_argument(
        "--skills",
        help="Comma-separated skill names (default: interactive prompt).",
    )
    p_link.add_argument(
        "--harnesses",
        help="Comma-separated harness keys (default: interactive prompt).",
    )
    p_link.set_defaults(
        func=lambda a: cmd_link(_parse_csv(a.skills), _parse_csv(a.harnesses))
    )

    p_unlink = sub.add_parser("unlink", help="Remove tracked skill symlinks.")
    p_unlink.add_argument(
        "--skills",
        help="Comma-separated skill names to unlink.",
    )
    p_unlink.add_argument(
        "--harnesses",
        help="Comma-separated harness keys to unlink from.",
    )
    p_unlink.set_defaults(
        func=lambda a: cmd_unlink(_parse_csv(a.skills), _parse_csv(a.harnesses))
    )

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

