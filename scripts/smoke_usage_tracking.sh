#!/usr/bin/env bash
# Owner-run smoke test for the usage-tracking plugin
# (FTD-opencode-usage-tracking-v1.0 §7.6 AC / TC-06, §3.4, §17).
#
# Modes:
#   scripts/smoke_usage_tracking.sh --check
#       Static validation, fully offline: bash -n on this script, plugin and
#       command files exist, bun test green, tsc clean. No provider request,
#       no live OpenCode run.
#
#   scripts/smoke_usage_tracking.sh --run --model PROVIDER/MODEL
#       Live smoke test (owner-executed). Verifies the plugin deploy surface
#       (aborting with link instructions otherwise — this script never links
#       anything itself): the auto-discovery entry symlink ~/.config/opencode/
#       plugins/usage-tracking.ts (OpenCode's plugin glob scans only files
#       DIRECTLY in the plugins dir, so this entry is what actually loads the
#       plugin) plus the per-file directory ~/.config/opencode/plugins/
#       usage-tracking/, then runs ONE fixed parent->one-subagent no-file
#       workload through
#       `opencode run --model ... --format json` in a mktemp workspace with
#       OpenCode stdout/stderr suppressed, and finally asserts metadata-only
#       against the plugin output root (~/.local/share/opencode-usage/):
#         A. the project subdir exists
#         B. events.jsonl exists and every line parses as JSON
#         C. at least one sessions/<id>.json has title != null,
#            tokens.input > 0, and cost > 0
#         D. a child session aggregate exists with parentID set
#         E. the parent's children list contains that child
#         F. toolCounts present with task >= 1
#         G. the models list is non-empty
#         H. overview.json exists, parses as JSON, and carries exactly the
#            11 expected top-level keys
#       Exits non-zero listing every failed assertion; exits 0 printing a
#       summary of the found artifacts.
#
# Metadata safety: never prints file contents — only paths, counts, and
# booleans. Best run while no other OpenCode sessions are active.
set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

readonly PLUGIN_SOURCE_DIR="${REPO_ROOT}/opencode/plugins/usage-tracking"
readonly PLUGIN_ENTRY_SOURCE_FILE="${REPO_ROOT}/opencode/plugins/usage-tracking.ts"
readonly COMMAND_SOURCE_FILE="${REPO_ROOT}/opencode/command/usage-status.md"
readonly PLUGIN_PRODUCTION_FILES=(aggregate.ts config.ts index.ts mapping.ts status.ts store.ts)

readonly OPENCODE_PLUGINS_DIR="${HOME}/.config/opencode/plugins"
readonly LINKED_PLUGIN_DIR="${OPENCODE_PLUGINS_DIR}/usage-tracking"
readonly LINKED_PLUGIN_ENTRY_FILE="${OPENCODE_PLUGINS_DIR}/usage-tracking.ts"
readonly USAGE_OUTPUT_ROOT="${HOME}/.local/share/opencode-usage"

# link.py item keys for this feature's deploy surface (FTD §17). The flat
# entry opencode/plugins/usage-tracking.ts comes first: it is the piece
# OpenCode auto-discovery actually loads (glob "{plugin,plugins}/*.{ts,js}"
# does not descend into subdirectories). The directory key
# opencode/plugins/usage-tracking/ expands to the plugin's discovered
# production files (repo-only *.test.ts files are never linked).
readonly PLUGIN_ITEM_KEYS="opencode/plugins/usage-tracking.ts,opencode/plugins/usage-tracking/,opencode/command/usage-status.md"

# Fixed workload: one parent session, exactly one subagent dispatch, no
# file access.
readonly WORKLOAD_PROMPT="Use the task tool exactly once to launch one subagent. Tell the subagent not to read, write, or change any files and to reply exactly: child-smoke-complete. After it returns, reply exactly: smoke-complete."

MODE=""
MODEL=""

usage() {
  cat <<'EOF'
Usage:
  scripts/smoke_usage_tracking.sh --check
  scripts/smoke_usage_tracking.sh --run --model PROVIDER/MODEL

--check runs static validation only (bash -n, plugin files exist, bun test
green, tsc clean). It is fully offline: no provider request and no live
OpenCode run.

--run performs the live smoke test (owner-executed): it verifies the plugin
deploy surface (aborting with link instructions otherwise — it never links
anything itself) — the auto-discovery entry ~/.config/opencode/plugins/
usage-tracking.ts (OpenCode's plugin glob scans only files DIRECTLY in the
plugins dir, so this entry is what actually loads the plugin) plus the
per-file directory ~/.config/opencode/plugins/usage-tracking/ — then runs
ONE fixed parent->one-subagent no-file workload through `opencode run --model ...
--format json` in a temporary workspace with OpenCode output suppressed, then
asserts metadata-only against the plugin output root
(~/.local/share/opencode-usage/): project subdir, events.jsonl JSON validity,
session aggregate completeness, child/parent linkage, task tool counts, model
list, and overview.json's exact 11-key shape. Exits non-zero listing every
failed assertion. Only paths, counts, and booleans are ever printed.
EOF
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --check)
      [[ -z "${MODE}" ]] || fail "specify exactly one of --check or --run"
      MODE="check"
      ;;
    --run)
      [[ -z "${MODE}" ]] || fail "specify exactly one of --check or --run"
      MODE="run"
      ;;
    --model)
      shift
      (($#)) || fail "--model requires PROVIDER/MODEL"
      MODEL="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
  shift
done

# Fail fast, before any request or filesystem action.
[[ -n "${MODE}" ]] || { usage >&2; fail "specify exactly one of --check or --run"; }
[[ -z "${MODEL}" || "${MODE}" == "run" ]] || fail "--model is only valid with --run"
[[ "${MODE}" != "run" || -n "${MODEL}" ]] || fail "--run requires --model PROVIDER/MODEL"
[[ -z "${MODEL}" || "${MODEL}" == */* ]] || fail "--model must be PROVIDER/MODEL"

print_owner_reminders() {
  printf '\nVerification reminder (FTD §17): run /usage-status in an OpenCode session to\n'
  printf 'confirm write health (output path, session/event counters, last write timestamp,\n'
  printf 'error count). Restart OpenCode first if it was running before the plugin was\n'
  printf '(re)linked — plugins load at startup.\n'
  printf '\nRollback (FTD §17):\n'
  printf '  uv run scripts/link.py unlink --opencode=%s\n' "${PLUGIN_ITEM_KEYS}"
  printf '  then restart OpenCode. Collected data is disposable and derived — no migration\n'
  printf '  is needed. (If *.test.ts plugin items were linked too, append their keys, or run\n'
  printf '  plain "uv run scripts/link.py unlink" to remove every tracked link.)\n'
}

run_check_mode() {
  local failures=()
  local file output

  printf '== usage-tracking smoke --check (static, offline) ==\n'

  # 1. Static syntax check of this script (bash -n semantics).
  if bash -n "${BASH_SOURCE[0]}" 2>/dev/null; then
    printf 'PASS: bash -n syntax check\n'
  else
    failures+=("bash -n syntax check failed")
  fi

  # 2. Plugin production files and command file exist in the repo.
  for file in "${PLUGIN_PRODUCTION_FILES[@]}"; do
    if [[ -f "${PLUGIN_SOURCE_DIR}/${file}" ]]; then
      printf 'PASS: plugin file exists: opencode/plugins/usage-tracking/%s\n' "${file}"
    else
      failures+=("plugin file missing: opencode/plugins/usage-tracking/${file}")
    fi
  done
  if [[ -f "${COMMAND_SOURCE_FILE}" ]]; then
    printf 'PASS: command file exists: opencode/command/usage-status.md\n'
  else
    failures+=("command file missing: opencode/command/usage-status.md")
  fi

  # 3. bun test green (bun may live in devbox rather than on PATH).
  local bun_cmd=()
  if command -v bun >/dev/null 2>&1; then
    bun_cmd=(bun)
  elif command -v devbox >/dev/null 2>&1; then
    bun_cmd=(devbox run -- bun)
  else
    failures+=("bun is not available (needed for 'bun test'); run inside devbox or install bun")
  fi
  if ((${#bun_cmd[@]})); then
    output="$(mktemp)"
    if (cd -- "${REPO_ROOT}" && "${bun_cmd[@]}" test) >"${output}" 2>&1; then
      printf 'PASS: bun test\n'
      grep -E '^[[:space:]]*[0-9]+ (pass|fail|skip|error)|^Ran [0-9]+ tests' "${output}" || true
    else
      failures+=("bun test failed")
      printf -- '--- bun test output (stderr) ---\n' >&2
      cat -- "${output}" >&2
    fi
    rm -f -- "${output}"
  fi

  # 4. tsc clean.
  local tsc_bin="${REPO_ROOT}/node_modules/.bin/tsc"
  if [[ -x "${tsc_bin}" ]]; then
    output="$(mktemp)"
    if (cd -- "${REPO_ROOT}" && "${tsc_bin}" -p tsconfig.json) >"${output}" 2>&1; then
      printf 'PASS: tsc -p tsconfig.json (no errors)\n'
    else
      failures+=("tsc -p tsconfig.json reported errors")
      printf -- '--- tsc output (stderr) ---\n' >&2
      cat -- "${output}" >&2
    fi
    rm -f -- "${output}"
  else
    failures+=("tsc not found at node_modules/.bin/tsc (run: bun install)")
  fi

  if ((${#failures[@]})); then
    printf '\n--check FAILED (%d):\n' "${#failures[@]}"
    printf '  - %s\n' "${failures[@]}"
    exit 1
  fi

  printf '\n--check passed: all static checks green (no provider request was made).\n'
  printf 'Live mode (owner-executed, provider-backed):\n'
  printf '  %s --run --model PROVIDER/MODEL\n' "${SCRIPT_DIR}/smoke_usage_tracking.sh"
}

verify_plugin_linked() {
  local file linked expected actual
  local missing=()

  # Assertion A / plugin-discoverability check, part 1 — the flat entry
  # symlink (loading-route fix, 2026-08-27): OpenCode's plugin auto-discovery
  # scans only files DIRECTLY inside the plugins dir (glob
  # "{plugin,plugins}/*.{ts,js}"), so without this entry the per-file
  # directory below is NOT discoverable and the plugin never loads.
  expected="$(readlink -f -- "${PLUGIN_ENTRY_SOURCE_FILE}" 2>/dev/null || true)"
  actual="$(readlink -f -- "${LINKED_PLUGIN_ENTRY_FILE}" 2>/dev/null || true)"
  if [[ -n "${actual}" && "${actual}" == "${expected}" ]]; then
    printf 'PASS: plugin entry linked (auto-discoverable): %s\n' "${LINKED_PLUGIN_ENTRY_FILE}"
  else
    missing+=("usage-tracking.ts (flat entry directly in ${OPENCODE_PLUGINS_DIR} — required for auto-discovery)")
  fi

  # Assertion A / plugin-discoverability check, part 2 — the existing
  # per-file directory check (unchanged).
  if [[ -d "${LINKED_PLUGIN_DIR}" ]]; then
    for file in "${PLUGIN_PRODUCTION_FILES[@]}"; do
      linked="${LINKED_PLUGIN_DIR}/${file}"
      expected="$(readlink -f -- "${PLUGIN_SOURCE_DIR}/${file}" 2>/dev/null || true)"
      actual="$(readlink -f -- "${linked}" 2>/dev/null || true)"
      if [[ -n "${actual}" && "${actual}" == "${expected}" ]]; then
        printf 'PASS: plugin linked: %s/%s\n' "${LINKED_PLUGIN_DIR}" "${file}"
      else
        missing+=("${file}")
      fi
    done
  else
    missing+=("${PLUGIN_PRODUCTION_FILES[@]}")
  fi

  if ((${#missing[@]})); then
    {
      printf 'ERROR: the usage-tracking plugin deploy surface is incomplete under %s\n' "${OPENCODE_PLUGINS_DIR}"
      printf '  missing or not resolving to the repo source: %s\n' "${missing[*]}"
      printf '  (the flat entry usage-tracking.ts is what OpenCode auto-discovery loads;\n'
      printf '   the usage-tracking/ directory alone is NOT discoverable)\n'
      printf 'Link it first (this script never creates or modifies links itself):\n'
      printf '  uv run scripts/link.py link --skip-skills --opencode=%s\n' "${PLUGIN_ITEM_KEYS}"
      printf 'or interactively: uv run scripts/link.py link\n'
      printf 'Then restart any running OpenCode (plugins load at startup) and re-run this script.\n'
    } >&2
    exit 1
  fi
}

run_live_mode() {
  [[ -x "$(command -v opencode)" ]] || fail "opencode is not available on PATH"
  [[ -x "$(command -v python3)" ]] || fail "python3 is not available on PATH"

  printf '== usage-tracking smoke --run (live) ==\n'
  printf 'model: %s\n' "${MODEL}"

  verify_plugin_linked

  TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/usage-tracking-smoke.XXXXXX")"
  cleanup() { rm -rf -- "${TMP_ROOT}"; }
  trap cleanup EXIT
  WORKSPACE="${TMP_ROOT}/workspace"
  mkdir -p -- "${WORKSPACE}"

  # Deliberately NO opencode.json in the workspace: the loading route under
  # test is global auto-discovery with default options (spike decision,
  # ADR-03), so the plugin must write to its default output root.
  SNAPSHOT_FILE="${TMP_ROOT}/pre-run-subdirs.txt"
  : >"${SNAPSHOT_FILE}"
  if [[ -d "${USAGE_OUTPUT_ROOT}" ]]; then
    find "${USAGE_OUTPUT_ROOT}" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' \
      | LC_ALL=C sort >"${SNAPSHOT_FILE}" || true
  fi
  RUN_START_EPOCH="$(date +%s)"
  WORKSPACE_CANONICAL="$(cd -- "${WORKSPACE}" && pwd -P)"

  printf 'Running one fixed parent->one-subagent no-file workload (OpenCode output suppressed)...\n'
  if ! (
    cd -- "${WORKSPACE}"
    opencode run --model "${MODEL}" --format json "${WORKLOAD_PROMPT}" >/dev/null 2>&1
  ); then
    fail "OpenCode live run failed; no CLI output was captured"
  fi

  VALIDATOR_STATUS=0
  python3 - "${USAGE_OUTPUT_ROOT}" "${SNAPSHOT_FILE}" "${RUN_START_EPOCH}" \
    "${WORKSPACE}" "${WORKSPACE_CANONICAL}" <<'PY' || VALIDATOR_STATUS=$?
import json
import os
import sys
from pathlib import Path

output_root = Path(sys.argv[1])
snapshot_file = Path(sys.argv[2])
run_start_epoch = int(sys.argv[3])
workspace_paths = {sys.argv[4], sys.argv[5]}

failures = []
passes = 0


def record_pass(message):
    global passes
    passes += 1
    print(f"PASS: {message}")


def record_fail(message):
    failures.append(message)
    print(f"FAIL: {message}")


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def positive(value):
    return is_number(value) and value > 0


def read_records(events_file):
    """Return (records, invalid_line_numbers) for a JSONL file, or (None, [])."""
    if not events_file.is_file():
        return None, []
    try:
        text = events_file.read_text()
    except OSError:
        return None, []
    records = []
    invalid = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            invalid.append(number)
    return records, invalid


# --- Locate the project subdirectory for this run's workspace ----------------
#
# Layer 1 (precise): a project dir whose events.jsonl contains a
# session.started record with directory == this run's workspace.
# Layer 2 (fallback): subdirs new since the pre-run snapshot, plus pre-existing
# subdirs whose events.jsonl was written during this run, disambiguated by the
# workload signature (a session.started with parentID set). Still needed under
# the v1.1 ULID layout: a repeat run of the same workspace reuses its
# registry-mapped ULID directory (so it is not new), and concurrent OpenCode
# sessions may write sibling ULID directories during the run. The layered
# detection is name-agnostic — it never assumes anything about a directory's
# name (ULID or otherwise).

all_subdirs = []
if output_root.is_dir():
    all_subdirs = sorted(entry.name for entry in output_root.iterdir() if entry.is_dir())


def project_candidates():
    matched = []
    for name in all_subdirs:
        events_file = output_root / name / "events.jsonl"
        records, _ = read_records(events_file)
        if records is None:
            continue
        for record in records:
            if (
                isinstance(record, dict)
                and record.get("type") == "session.started"
                and record.get("directory") in workspace_paths
            ):
                matched.append(output_root / name)
                break
    return matched


candidates = project_candidates()
if not candidates:
    before = set()
    if snapshot_file.is_file():
        before = {
            line.strip()
            for line in snapshot_file.read_text().splitlines()
            if line.strip()
        }
    timed = []
    for name in all_subdirs:
        events_file = output_root / name / "events.jsonl"
        if name not in before:
            timed.append(output_root / name)
        elif events_file.is_file() and os.path.getmtime(events_file) >= run_start_epoch:
            timed.append(output_root / name)
    if len(timed) > 1:
        signed = [
            d
            for d in timed
            if any(
                isinstance(r, dict)
                and r.get("type") == "session.started"
                and isinstance(r.get("parentID"), str)
                and r["parentID"]
                for r in (read_records(d / "events.jsonl")[0] or [])
            )
        ]
        candidates = signed if len(signed) == 1 else []
    else:
        candidates = timed

project_dir = None
if len(candidates) == 1:
    project_dir = candidates[0]
elif len(candidates) > 1:
    record_fail(
        "project subdir is ambiguous between %d candidates: %s"
        % (len(candidates), ", ".join(d.name for d in candidates))
    )

if project_dir is None:
    if not failures:
        record_fail(
            "no project subdir for this run's workspace was found under the "
            "output root (plugin did not load or did not write)"
        )
    print()
    print("DIAGNOSTIC (no usage data written for this run):")
    print(f"  output root: {output_root}")
    print("  - The plugin symlinks were verified before the run, but nothing was")
    print("    written for this workspace.")
    print("  - Confirm the plugin actually loaded: OpenCode plugin auto-discovery")
    print('    scans only files DIRECTLY inside ~/.config/opencode/plugins/ (glob')
    print('    "{plugin,plugins}/*.{ts,js}"); files inside subdirectories such as')
    print("    usage-tracking/ are NOT discovered (OpenCode 1.18.21/1.18.23).")
    print("  - Check write health with /usage-status in an OpenCode session and look")
    print('    for "usage-tracking" service entries in the OpenCode logs.')
    print()
    print(f"RESULT: FAILED — {len(failures)} assertion(s):")
    for message in failures:
        print(f"  - {message}")
    sys.exit(1)

record_pass(f"project subdir exists: {project_dir}")

# --- Assertion B: events.jsonl exists and every line parses as JSON ----------

events_file = project_dir / "events.jsonl"
event_records, invalid_event_lines = read_records(events_file)
if event_records is None:
    record_fail(f"events.jsonl missing or unreadable: {events_file}")
elif invalid_event_lines:
    record_fail(
        "events.jsonl contains invalid JSON on line(s): %s"
        % ", ".join(str(n) for n in invalid_event_lines[:10])
    )
else:
    record_pass(f"events.jsonl: {len(event_records)} record(s), every line valid JSON")

# --- Load session aggregates --------------------------------------------------

sessions_dir = project_dir / "sessions"
session_files = sorted(sessions_dir.glob("*.json")) if sessions_dir.is_dir() else []
aggregates = []
invalid_session_files = []
for session_file in session_files:
    try:
        data = json.loads(session_file.read_text())
    except (OSError, json.JSONDecodeError):
        invalid_session_files.append(session_file.name)
        continue
    if isinstance(data, dict):
        aggregates.append(data)
    else:
        invalid_session_files.append(session_file.name)

if invalid_session_files:
    record_fail(
        "session aggregate file(s) not valid JSON: %s"
        % ", ".join(invalid_session_files[:10])
    )
if not session_files:
    record_fail(f"no session aggregate files under {sessions_dir}")

# --- Assertion C: a session aggregate with title, input tokens, and cost -----

complete_sessions = [
    a
    for a in aggregates
    if isinstance(a.get("title"), str)
    and a["title"]
    and isinstance(a.get("tokens"), dict)
    and positive(a["tokens"].get("input"))
    and positive(a.get("cost"))
]
if complete_sessions:
    record_pass(
        "session aggregate with title != null, tokens.input > 0, cost > 0: %d found"
        % len(complete_sessions)
    )
else:
    record_fail(
        "no session aggregate with title != null AND tokens.input > 0 AND cost > 0"
    )

# --- Assertion D: a child session aggregate with parentID set ----------------

child_aggregates = [
    a for a in aggregates if isinstance(a.get("parentID"), str) and a["parentID"]
]
if child_aggregates:
    record_pass(
        "child session aggregate with parentID set: %d found"
        % len(child_aggregates)
    )
else:
    record_fail("no child session aggregate with parentID set")

# --- Assertion E: the parent's children list contains the child --------------

by_session_id = {
    a["sessionID"]: a
    for a in aggregates
    if isinstance(a.get("sessionID"), str) and a["sessionID"]
}
linked_pairs = []
for child in child_aggregates:
    parent = by_session_id.get(child["parentID"])
    if parent is None:
        continue
    children_list = parent.get("children")
    if not isinstance(children_list, list):
        continue
    if any(
        isinstance(entry, dict) and entry.get("sessionID") == child["sessionID"]
        for entry in children_list
    ):
        linked_pairs.append((parent, child))
if linked_pairs:
    record_pass(
        "parent children list contains the child session: %d link(s)"
        % len(linked_pairs)
    )
else:
    record_fail("no parent aggregate whose children list contains a child session")

# --- Assertion F: toolCounts present with task >= 1 ---------------------------

task_counts = [
    a["toolCounts"]["task"]
    for a in aggregates
    if isinstance(a.get("toolCounts"), dict)
    and is_number(a["toolCounts"].get("task"))
]
if any(count >= 1 for count in task_counts):
    record_pass(
        "toolCounts present with task >= 1 (max task count: %d)" % max(task_counts)
    )
else:
    record_fail("no session aggregate with toolCounts task >= 1")

# --- Assertion G: models list non-empty ---------------------------------------

with_models = [a for a in aggregates if isinstance(a.get("models"), list) and a["models"]]
if with_models:
    record_pass("models list non-empty: %d session(s)" % len(with_models))
else:
    record_fail("no session aggregate with a non-empty models list")

# --- Assertion H: overview.json with the exact 11-key shape -------------------

overview_file = project_dir / "overview.json"
try:
    overview = json.loads(overview_file.read_text())
except (OSError, json.JSONDecodeError):
    overview = None
    record_fail(f"overview.json missing, unreadable, or invalid JSON: {overview_file}")
if isinstance(overview, dict):
    expected_overview_keys = {
        "generatedAt",
        "sessions",
        "modelsUsed",
        "tokens",
        "cost",
        "toolCounts",
        "activeMs",
        "directory",
        "git",
        "device",
        "projectDirectory",
    }
    actual_overview_keys = set(overview.keys())
    if actual_overview_keys == expected_overview_keys:
        record_pass("overview.json: exactly the 11 expected top-level keys")
    else:
        record_fail(
            "overview.json top-level keys mismatch — missing: %s; unexpected: %s"
            % (
                ", ".join(sorted(expected_overview_keys - actual_overview_keys)) or "none",
                ", ".join(sorted(actual_overview_keys - expected_overview_keys)) or "none",
            )
        )
elif overview is not None:
    record_fail("overview.json is valid JSON but not an object")

# --- Summary (paths and counts only) ------------------------------------------

print()
print("SUMMARY (paths and counts only):")
print(f"  output root:  {output_root}")
print(f"  project dir:  {project_dir}")
print(f"  events:       {events_file} ({len(event_records or [])} record(s))")
print(f"  sessions dir: {sessions_dir} ({len(session_files)} file(s))")
print(f"  overview:     {overview_file}")
print(f"  assertions:   {passes} passed, {len(failures)} failed")

if failures:
    print()
    print(f"RESULT: FAILED — {len(failures)} assertion(s):")
    for message in failures:
        print(f"  - {message}")
    sys.exit(1)

print()
print("RESULT: PASSED — all assertions green.")
sys.exit(0)
PY

  print_owner_reminders
  exit "${VALIDATOR_STATUS}"
}

case "${MODE}" in
  check) run_check_mode ;;
  run) run_live_mode ;;
  *) fail "internal error: unknown mode ${MODE}" ;;
esac
