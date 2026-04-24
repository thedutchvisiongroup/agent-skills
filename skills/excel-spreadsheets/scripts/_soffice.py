"""
Shared helpers for running LibreOffice headless on Linux, macOS, and Windows.
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path

_SYSTEM = platform.system()

MACRO_DIR = {
    "Darwin": "~/Library/Application Support/LibreOffice/4/user/basic/Standard",
    "Linux": "~/.config/libreoffice/4/user/basic/Standard",
    "Windows": "~/AppData/Roaming/LibreOffice/4/user/basic/Standard",
}

_WINDOWS_SEARCH_PATHS = [
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "LibreOffice" / "program" / "soffice.exe",
    Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "LibreOffice" / "program" / "soffice.exe",
]


def _find_soffice() -> str:
    """Return the path to the soffice binary, searching known locations on Windows."""
    if _SYSTEM == "Windows":
        for candidate in _WINDOWS_SEARCH_PATHS:
            if candidate.exists():
                return str(candidate)
    # Fall back to PATH lookup (works on Linux/macOS, and Windows if added to PATH)
    found = shutil.which("soffice")
    if found:
        return found
    return "soffice"


def soffice_env() -> dict[str, str]:
    """Return environment variables for headless LibreOffice execution."""
    env = os.environ.copy()
    if _SYSTEM != "Windows":
        env["SAL_USE_VCLPLUGIN"] = "svp"
    return env


def macro_dir() -> Path:
    """Return the LibreOffice user macro directory for the current platform."""
    return Path(MACRO_DIR.get(_SYSTEM, MACRO_DIR["Linux"])).expanduser()


def run_soffice(args: list[str], timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    """Run soffice with the given arguments, using Python-native timeout on all platforms."""
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
        # Mimic the returncode 124 that the old gtimeout/timeout produced
        return subprocess.CompletedProcess(cmd, returncode=124, stdout="", stderr="Timeout expired")
