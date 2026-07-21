#!/usr/bin/env python3
"""Link AI agent skills and OpenCode config from this repo into global directories.

Usage:
    uv run scripts/link.py status
    uv run scripts/link.py link
    uv run scripts/link.py unlink
    uv run scripts/link.py list

Two kinds of things are synced:

1. **Skills** — individual skill folders from `<repo>/skills/<name>/` are
   symlinked into the global skills directory of each selected agent harness.
2. **OpenCode items** — files from `<repo>/opencode/` are symlinked per file
   into `~/.config/opencode/` (e.g. `agents/code-reviewer.md`). The reserved
   subfolder `<repo>/opencode/configs/` is NOT copied 1:1; each file in it has
   a fixed target mapping (see CONFIG_FILE_MAP), including the managed layer
   in `/etc/opencode/` (requires root).

The script is idempotent: existing correct symlinks are kept, broken symlinks
are repaired, and real files/dirs trigger an interactive prompt before being
replaced.
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

HOME = Path.home()
AGENTS_GLOBAL = HOME / ".agents" / "skills"

# OpenCode sync: <repo>/opencode/** → ~/.config/opencode/** (per file).
# The reserved subfolder opencode/configs/ is NOT copied 1:1; see CONFIG_FILE_MAP.
OPENCODE_SOURCE_DIR = REPO_ROOT / "opencode"
OPENCODE_RESERVED_DIR = "configs"
OPENCODE_TARGET_DIR = HOME / ".config" / "opencode"
MANAGED_TARGET_DIR = Path("/etc") / "opencode"

# Fixed targets for the reserved opencode/configs/ files.
# OpenCode loads and merges (later wins):
#   ~/.config/opencode/config.json  → opencode.json → opencode.jsonc  (global)
#   /etc/opencode/opencode.json(c)                                   (managed)
CONFIG_FILE_MAP: dict[str, Path] = {
    "tdvg-standards.json": OPENCODE_TARGET_DIR / "config.json",
    "tdvg-required.json": MANAGED_TARGET_DIR / "opencode.jsonc",
}


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


@dataclass(frozen=True)
class SyncItem:
    """A single repo file synced to a fixed target via symlink."""

    key: str  # repo-relative posix path, e.g. "opencode/agents/code-reviewer.md"
    label: str  # short human label for the UI
    source: Path  # absolute path inside the repo
    target: Path  # absolute symlink target path
    managed: bool = False  # True when the target requires root (e.g. /etc/...)


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
# Discovery
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


def _item_target_for_key(key: str) -> Optional[Path]:
    """Reconstruct the symlink target for an item key, even if the repo file
    no longer exists (needed for unlinking stale state)."""
    prefix = "opencode/"
    if not key.startswith(prefix):
        return None
    rel = key[len(prefix):]
    parts = rel.split("/")
    if parts[0] == OPENCODE_RESERVED_DIR:
        return CONFIG_FILE_MAP.get(parts[-1])
    return OPENCODE_TARGET_DIR.joinpath(*parts)


def discover_opencode_items() -> list[SyncItem]:
    """Return all OpenCode sync items available in <repo>/opencode/.

    Every file under opencode/ maps 1:1 (per file) into ~/.config/opencode/,
    EXCEPT the reserved configs/ subfolder, whose files map via CONFIG_FILE_MAP
    (tdvg-standards.json → ~/.config/opencode/config.json, tdvg-required.json →
    /etc/opencode/opencode.jsonc).
    """
    items: list[SyncItem] = []
    if not OPENCODE_SOURCE_DIR.is_dir():
        return items

    # 1:1 content (everything except the reserved configs/ dir).
    for path in sorted(OPENCODE_SOURCE_DIR.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(OPENCODE_SOURCE_DIR)
        if rel.parts[0] == OPENCODE_RESERVED_DIR:
            continue
        items.append(
            SyncItem(
                key=path.relative_to(REPO_ROOT).as_posix(),
                label=f"opencode/{rel.as_posix()}",
                source=path.resolve(),
                target=OPENCODE_TARGET_DIR.joinpath(*rel.parts),
            )
        )

    # Reserved configs with fixed targets.
    configs_dir = OPENCODE_SOURCE_DIR / OPENCODE_RESERVED_DIR
    if configs_dir.is_dir():
        for name, target in CONFIG_FILE_MAP.items():
            src = configs_dir / name
            if not src.is_file():
                continue
            items.append(
                SyncItem(
                    key=src.relative_to(REPO_ROOT).as_posix(),
                    label=f"opencode/{OPENCODE_RESERVED_DIR}/{name}",
                    source=src.resolve(),
                    target=target,
                    managed=target.is_relative_to(MANAGED_TARGET_DIR),
                )
            )
    return items


# --------------------------------------------------------------------------- #
# Path / conflict helpers
# --------------------------------------------------------------------------- #


def classify_target(path: Path, expected_source: Path) -> str:
    """Classify what currently sits at a target path.

    Returns one of:
      - "missing"        nothing there
      - "symlink_ok"     symlink pointing at the expected repo source
      - "symlink_other"  symlink pointing somewhere else
      - "symlink_broken"  symlink that resolves to nothing
      - "real_dir"       real directory (not a symlink)
      - "real_file"      real file (not a symlink)
    """
    if not path.exists() and not path.is_symlink():
        return "missing"
    if path.is_symlink():
        target = path.resolve()
        if not target.exists():
            return "symlink_broken"
        if target == expected_source.resolve():
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


def create_symlink(source: Path, target: Path) -> Path:
    """Create a symlink <target> -> <source>, replacing any existing link."""
    ensure_parent_dir(target)
    if target.is_symlink() or target.exists():
        target.unlink()
    target.symlink_to(source)
    return target


def remove_symlink(target: Path) -> bool:
    """Remove a symlink at target. Returns True if removed."""
    if target.is_symlink():
        target.unlink()
        return True
    return False


def is_root() -> bool:
    """True when running with root privileges (needed for managed targets)."""
    geteuid = getattr(os, "geteuid", None)
    return geteuid is not None and geteuid() == 0


# --------------------------------------------------------------------------- #
# State persistence
# --------------------------------------------------------------------------- #

STATE_VERSION = 2


def load_state() -> dict:
    """Load persisted link state.

    v2: {"version": 2, "linked": [[skill, harness], ...],
         "linked_items": [item_key, ...]}
    v1 files ({"version": 1, "linked": [...]}) are migrated transparently.
    """
    import json

    fresh = {"version": STATE_VERSION, "linked": [], "linked_items": []}
    if not STATE_FILE.exists():
        return fresh
    try:
        data = json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return fresh
    version = data.get("version", 1)
    if version == 1:
        data = {"version": STATE_VERSION, "linked": data.get("linked", [])}
    elif version != STATE_VERSION:
        return fresh
    data.setdefault("linked", [])
    data.setdefault("linked_items", [])
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


def state_record_item(state: dict, item_key: str) -> None:
    if item_key not in state["linked_items"]:
        state["linked_items"].append(item_key)


def state_forget_item(state: dict, item_key: str) -> None:
    while item_key in state["linked_items"]:
        state["linked_items"].remove(item_key)


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

STATUS_MARKS = {
    "missing": "[dim]·[/dim]",
    "symlink_ok": "[green]✓[/green]",
    "symlink_other": "[yellow]↗[/yellow]",
    "symlink_broken": "[red]✗[/red]",
    "real_dir": "[red]D[/red]",
    "real_file": "[red]F[/red]",
}

STATUS_LEGEND = (
    "[green]✓[/green]=linked  [dim]·[/dim]=missing  "
    "[yellow]↗[/yellow]=symlink→other  [red]✗[/red]=broken  "
    "[red]D[/red]=real dir  [red]F[/red]=real file  [blue]*[/blue]=tracked"
)


def _shorten_home(path: Path) -> str:
    try:
        return "~/" + str(path.relative_to(HOME))
    except ValueError:
        return str(path)


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
            cls = classify_target(target, SKILLS_SOURCE_DIR / skill)
            mark = STATUS_MARKS[cls]
            tracked = (skill, key) in linked_pairs
            tag = "[blue]*[/blue]" if tracked else " "
            row.append(f"{mark} {tag}")
        table.add_row(*row)
    console.print(table)


def render_items_status(items: list[SyncItem]) -> None:
    """Print a table of every OpenCode sync item and its current state."""
    table = Table(title="OpenCode sync status", show_lines=False)
    table.add_column("Item", style="bold")
    table.add_column("Target")
    table.add_column("Managed")
    table.add_column("Status")

    state = load_state()
    tracked_keys = set(state["linked_items"])

    for item in items:
        cls = classify_target(item.target, item.source)
        mark = STATUS_MARKS[cls]
        tag = "[blue]*[/blue]" if item.key in tracked_keys else " "
        managed = "[magenta]root[/magenta]" if item.managed else "[dim]·[/dim]"
        table.add_row(item.label, _shorten_home(item.target), managed, f"{mark} {tag}")
    console.print(table)
    console.print(STATUS_LEGEND)


# --------------------------------------------------------------------------- #
# Interactive prompts
# --------------------------------------------------------------------------- #


def prompt_skills(skills: list[str]) -> list[str]:
    """Step: choose which skills to link."""
    choices = []
    for skill in skills:
        choices.append(Choice(title=skill, value=skill, checked=True))
    selected = questionary.checkbox(
        "Select skills to link:",
        choices=choices,
    ).ask()
    if selected is None:
        return []
    return selected


def prompt_items(items: list[SyncItem]) -> list[SyncItem]:
    """Step: choose which OpenCode items to link."""
    choices = []
    for item in items:
        suffix = "  [managed → /etc, needs root]" if item.managed else ""
        choices.append(
            Choice(title=f"{item.label} → {_shorten_home(item.target)}{suffix}",
                   value=item.key, checked=True)
        )
    selected = questionary.checkbox(
        "Select OpenCode items to link:",
        choices=choices,
    ).ask()
    if selected is None:
        return []
    chosen = set(selected)
    return [item for item in items if item.key in chosen]


def prompt_harnesses(
    harnesses: dict[str, Harness],
    detected: set[str],
) -> list[str]:
    """Step: choose which harnesses to link into."""
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


def prompt_conflict(label: str, target: Path, cls: str) -> str:
    """Ask what to do with an existing real file/dir at the target.

    Returns one of: "backup", "overwrite", "skip".
    """
    kind = {"real_dir": "real directory", "real_file": "real file"}[cls]
    return questionary.select(
        f"Conflict for [bold]{label}[/bold] in {target.parent}: "
        f"a {kind} already exists. What now?",
        choices=[
            Choice("Backup then replace (recommended)", value="backup"),
            Choice("Overwrite (delete without backup)", value="overwrite"),
            Choice("Skip this one", value="skip"),
        ],
    ).ask()


# --------------------------------------------------------------------------- #
# Commands: link / unlink / list / status
# --------------------------------------------------------------------------- #


def cmd_link(
    skills_arg: Optional[list[str]],
    harness_arg: Optional[list[str]],
    opencode_arg: Optional[list[str]],
    skip_skills: bool,
    skip_opencode: bool,
) -> int:
    harnesses = _harnesses()
    skills = discover_repo_skills()
    items = discover_opencode_items()
    if not skills and not items:
        console.print(
            "[red]Nothing found to link[/red] — no skills in "
            + str(SKILLS_SOURCE_DIR)
            + " and no OpenCode items in "
            + str(OPENCODE_SOURCE_DIR)
        )
        return 1

    # --- Step 1: skills ---
    chosen_skills: list[str] = []
    if skip_skills:
        console.print("[dim]↷ skipping skills (--skip-skills)[/dim]")
    elif skills_arg:
        unknown = set(skills_arg) - set(skills)
        if unknown:
            console.print(f"[red]Unknown skills:[/red] {', '.join(unknown)}")
            return 1
        chosen_skills = skills_arg
    elif skills:
        chosen_skills = prompt_skills(skills)

    # --- Step 2: OpenCode items ---
    chosen_items: list[SyncItem] = []
    if skip_opencode:
        console.print("[dim]↷ skipping OpenCode items (--skip-opencode)[/dim]")
    elif opencode_arg:
        known = {item.key for item in items}
        unknown = set(opencode_arg) - known
        if unknown:
            console.print(
                f"[red]Unknown OpenCode items:[/red] {', '.join(sorted(unknown))}"
            )
            return 1
        chosen_items = [item for item in items if item.key in set(opencode_arg)]
    elif items:
        chosen_items = prompt_items(items)

    if not chosen_skills and not chosen_items:
        console.print("[yellow]Nothing selected. Aborting.[/yellow]")
        return 0

    # --- Step 3: harnesses (only relevant for skills) ---
    chosen_harness_keys: list[str] = []
    if chosen_skills:
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

    def link_one(label: str, source: Path, target: Path) -> str:
        """Link a single (source → target) pair, handling conflicts.

        Returns one of: "ok" | "created" | "backup" | "skip" | "error".
        """
        cls = classify_target(target, source)
        if cls == "symlink_ok":
            return "ok"
        outcome = "created"
        if cls in ("real_dir", "real_file"):
            action = prompt_conflict(label, target, cls)
            if action == "skip":
                return "skip"
            if action == "backup":
                backup = make_backup(target)
                console.print(f"[blue]⟲ backup → {backup.name}[/blue]")
                outcome = "backup"
            # overwrite: fall through and replace
        try:
            create_symlink(source, target)
        except OSError as exc:
            console.print(f"[red]✗ {label}: {exc}[/red]")
            return "error"
        return outcome

    def report(outcome: str, label: str) -> bool:
        """Update counters and print the result. Returns True if link is in place."""
        nonlocal created, skipped, backed_up, already_ok
        if outcome == "ok":
            already_ok += 1
            console.print(f"[green]✓[/green] {label} (already linked)")
            return True
        if outcome == "skip":
            skipped += 1
            console.print(f"[dim]↷ skip {label}[/dim]")
            return False
        if outcome == "error":
            return False
        if outcome == "backup":
            backed_up += 1
        created += 1
        console.print(f"[green]✓ link {label}[/green]")
        return True

    # --- Link skills ---
    for skill in chosen_skills:
        for key in chosen_harness_keys:
            harness = harnesses[key]
            outcome = link_one(
                skill,
                (SKILLS_SOURCE_DIR / skill).resolve(),
                expected_target(skill, harness),
            )
            if report(outcome, f"{skill} → {key}"):
                state_record(state, skill, key)

    # --- Link OpenCode items ---
    for item in chosen_items:
        if item.managed and not is_root():
            skipped += 1
            console.print(
                f"[yellow]↷ skip {item.label}: managed target {item.target} "
                f"requires root. Re-run as root to link it.[/yellow]"
            )
            continue
        outcome = link_one(item.label, item.source, item.target)
        if report(outcome, item.label):
            state_record_item(state, item.key)

    save_state(state)
    console.print(
        f"\n[bold]Done.[/bold] created={created} already_ok={already_ok} "
        f"backed_up={backed_up} skipped={skipped}"
    )
    return 0


def cmd_unlink(
    skills_arg: Optional[list[str]],
    harness_arg: Optional[list[str]],
    opencode_arg: Optional[list[str]],
) -> int:
    harnesses = _harnesses()
    state = load_state()
    linked = list(state["linked"])
    linked_items = list(state["linked_items"])

    if not linked and not linked_items:
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
    if opencode_arg:
        linked_items = [k for k in linked_items if k in set(opencode_arg)]

    if not linked and not linked_items:
        console.print("[yellow]No matching tracked links to unlink.[/yellow]")
        return 0

    removed = 0
    for skill, key in linked:
        harness = harnesses.get(key)
        if not harness:
            continue
        target = expected_target(skill, harness)
        cls = classify_target(target, SKILLS_SOURCE_DIR / skill)
        if cls in ("symlink_ok", "symlink_broken", "symlink_other"):
            target.unlink()
            removed += 1
            console.print(f"[green]✓ unlinked {skill} from {key}[/green]")
        else:
            console.print(f"[dim]↷ {skill} in {key} is {cls}, leaving as-is[/dim]")
        state_forget(state, skill, key)

    for item_key in linked_items:
        target = _item_target_for_key(item_key)
        if target is None:
            console.print(f"[dim]↷ {item_key}: unknown item, dropping from state[/dim]")
            state_forget_item(state, item_key)
            continue
        if target.is_symlink():
            target.unlink()
            removed += 1
            console.print(f"[green]✓ unlinked {item_key}[/green]")
        else:
            console.print(f"[dim]↷ {item_key} is not a symlink, leaving as-is[/dim]")
        state_forget_item(state, item_key)

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

    items = discover_opencode_items()
    console.print(f"\n[bold]OpenCode items in repo ({len(items)}):[/bold]")
    for item in items:
        managed = "  [magenta]managed → /etc, needs root[/magenta]" if item.managed else ""
        console.print(f"  - {item.label} → {_shorten_home(item.target)}{managed}")
    return 0


def cmd_status() -> int:
    harnesses = _harnesses()
    skills = discover_repo_skills()
    items = discover_opencode_items()
    if not skills and not items:
        console.print(
            "[red]Nothing found[/red] — no skills in "
            + str(SKILLS_SOURCE_DIR)
            + " and no OpenCode items in "
            + str(OPENCODE_SOURCE_DIR)
        )
        return 1
    if skills:
        render_status(skills, harnesses)
    if items:
        render_items_status(items)
    elif skills:
        console.print(STATUS_LEGEND)
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
        description="Symlink AI skills and OpenCode config from this repo "
        "into global directories.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show current link status tables.")
    p_status.set_defaults(func=lambda a: cmd_status())

    p_list = sub.add_parser("list", help="List supported harnesses, skills and items.")
    p_list.set_defaults(func=lambda a: cmd_list())

    p_link = sub.add_parser("link", help="Create symlinks for skills and OpenCode items.")
    p_link.add_argument(
        "--skills",
        help="Comma-separated skill names (default: interactive prompt).",
    )
    p_link.add_argument(
        "--harnesses",
        help="Comma-separated harness keys (default: interactive prompt).",
    )
    p_link.add_argument(
        "--opencode",
        help="Comma-separated OpenCode item keys (default: interactive prompt).",
    )
    p_link.add_argument(
        "--skip-skills",
        action="store_true",
        help="Do not link any skills (OpenCode items only).",
    )
    p_link.add_argument(
        "--skip-opencode",
        action="store_true",
        help="Do not link any OpenCode items (skills only).",
    )
    p_link.set_defaults(
        func=lambda a: cmd_link(
            _parse_csv(a.skills),
            _parse_csv(a.harnesses),
            _parse_csv(a.opencode),
            a.skip_skills,
            a.skip_opencode,
        )
    )

    p_unlink = sub.add_parser("unlink", help="Remove tracked symlinks.")
    p_unlink.add_argument(
        "--skills",
        help="Comma-separated skill names to unlink.",
    )
    p_unlink.add_argument(
        "--harnesses",
        help="Comma-separated harness keys to unlink from.",
    )
    p_unlink.add_argument(
        "--opencode",
        help="Comma-separated OpenCode item keys to unlink.",
    )
    p_unlink.set_defaults(
        func=lambda a: cmd_unlink(
            _parse_csv(a.skills), _parse_csv(a.harnesses), _parse_csv(a.opencode)
        )
    )

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
