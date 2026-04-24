"""
Shared helpers for running LibreOffice headless on Linux, macOS, and Windows.

This module provides cross-platform utilities for:
- Locating the ``soffice`` binary (auto-detects common install paths on Windows)
- Resolving the LibreOffice user macro directory
- Running LibreOffice in headless mode with a Python-native timeout

All path handling uses :mod:`pathlib` for cross-platform safety.
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path

_SYSTEM = platform.system()

"""Per-platform paths to the LibreOffice user macro directory (``Standard`` library).
Uses ``~`` which is expanded by :meth:`Path.expanduser` at runtime."""
MACRO_DIR = {
    "Darwin": "~/Library/Application Support/LibreOffice/4/user/basic/Standard",
    "Linux": "~/.config/libreoffice/4/user/basic/Standard",
    "Windows": "~/AppData/Roaming/LibreOffice/4/user/basic/Standard",
}

"""Well-known install locations for ``soffice.exe`` on Windows.
Checked in order by :func:`_find_soffice` when ``platform.system() == "Windows"``."""
_WINDOWS_SEARCH_PATHS = [
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "LibreOffice" / "program" / "soffice.exe",
    Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "LibreOffice" / "program" / "soffice.exe",
]


def _find_soffice() -> str:
    """Locate the ``soffice`` executable.

    Search order:
    1. Known Windows install paths (``Program Files``, ``Program Files (x86)``)
    2. System ``PATH`` via :func:`shutil.which` (works on all platforms)
    3. Falls back to bare ``"soffice"`` so :func:`subprocess.run` can raise
       a clear :class:`FileNotFoundError` if it really isn't installed.

    :returns: Absolute path to the binary, or ``"soffice"`` as a last resort.
    """
    if _SYSTEM == "Windows":
        for candidate in _WINDOWS_SEARCH_PATHS:
            if candidate.exists():
                return str(candidate)
    found = shutil.which("soffice")
    if found:
        return found
    return "soffice"


def soffice_env() -> dict[str, str]:
    """Build an environment dict for headless LibreOffice execution.

    On Linux / macOS the ``SAL_USE_VCLPLUGIN=svp`` variable is set to
    suppress the graphical back-end.  On Windows this variable is not
    needed and is omitted.

    :returns: A copy of :data:`os.environ` with platform-specific additions.
    """
    env = os.environ.copy()
    if _SYSTEM != "Windows":
        env["SAL_USE_VCLPLUGIN"] = "svp"
    return env


def macro_dir() -> Path:
    """Return the LibreOffice user macro directory for the current platform.

    Falls back to the Linux path on unknown platforms.

    :returns: Expanded :class:`Path` to the ``Standard`` macro library folder.
    """
    return Path(MACRO_DIR.get(_SYSTEM, MACRO_DIR["Linux"])).expanduser()


def run_soffice(args: list[str], timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    """Run ``soffice`` with the given CLI arguments.

    Uses Python-native :func:`subprocess.run` timeout on all platforms,
    replacing the old ``gtimeout`` / ``timeout`` wrapper approach.

    When a timeout fires, ``subprocess.run`` kills the child process
    automatically.  This function catches :class:`subprocess.TimeoutExpired`
    and returns a :class:`subprocess.CompletedProcess` with
    ``returncode=124`` (matching the convention used by GNU ``timeout``)
    so callers can handle timeouts uniformly.

    :param args: Arguments passed to ``soffice`` (e.g. ``["--headless", ...]``).
    :param timeout: Maximum seconds to wait.  ``None`` means wait forever.
    :returns: Completed process result.
    """
    soffice_bin = _find_soffice()
    cmd = [soffice_bin, *args]

    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=soffice_env(),
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, returncode=124, stdout="", stderr="Timeout expired")
