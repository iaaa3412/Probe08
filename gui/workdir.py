import json
import os
import platform
import sys

# Named presets for the project root that holds the ATA folders and "GUI
# System" - a plain custom path still works via the working-directory
# Browse button, these are just the two locations anyone actually switches
# between.
PRESETS = {
    "automationproject": "C:/automationproject",
    "proberautomation": r"\\prober\M\ETL\proberautomation",
}

# Where the running app itself lives - the exe's OWN folder once this is
# built to one, or this checkout's root (this file's grandparent - same
# place main.py sits) during plain-python development. Defined here,
# before _PREF_PATH, specifically so _PREF_PATH can be anchored to it -
# see that constant's own comment for why this distinction matters.
#
# sys.frozen/sys.executable are what PyInstaller (and friends) set before
# ever running the bundled entry point, so this is correct as a plain
# constant computed once at import time - no call has to happen "too
# early" relative to the bundle's own startup.
def _exe_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# This file's own directory is fixed regardless of which working directory
# is chosen - it lives next to the app itself, not inside "GUI System".
# "GUI System" now lives INSIDE whichever working directory is picked (see
# gui_system_dir() below), so "which working directory to default to on
# this PC" can't be stored there without a chicken-and-egg problem on the
# very first read on a fresh machine.
#
# Anchored to _exe_dir(), NOT a bare __file__-relative path - under
# PyInstaller's --onefile mode, __file__ for a bundled module resolves
# inside a fresh temp extraction directory (sys._MEIPASS) that gets wiped
# when the process exits, so a bare __file__-relative path here would
# silently lose every "Set Default" the moment the app closed and always
# fall back to PRESETS["proberautomation"] on the next launch. Anchoring
# to the exe's own real, persistent folder (or the checkout root in dev
# mode) is what makes "just the exe, self-creating this one file next to
# itself on first Set Default" a valid deployment - no installer, no
# per-user/per-machine OS config directory needed.
_PREF_PATH = os.path.join(_exe_dir(), "working_dir_pref.json")

# No forced override - proberautomation is confirmed ready, so
# get_default_working_dir() just uses whatever was last saved via Set
# Default (falling back to the proberautomation preset - the real shared
# location - if nothing has been saved yet on this PC).
_FORCE_TEMPORARY_DEFAULT = None


def computer_name() -> str:
    """This PC's own identity, for scoping per-machine settings (default ATA
    folder, default prober) now that GUI System is a shared network folder
    multiple computers can open at once - see app_settings.py."""
    return os.environ.get("COMPUTERNAME") or platform.node() or "UNKNOWN-PC"


def _load_pref() -> dict:
    try:
        with open(_PREF_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def saved_default_working_dir() -> "str | None":
    """Whatever was last explicitly set via Set Default, ignoring the
    temporary override above - exists so the UI can show the two separately
    (what's saved vs. what's actually active right now)."""
    return _load_pref().get("working_dir")


def get_default_working_dir() -> str:
    if _FORCE_TEMPORARY_DEFAULT:
        return _FORCE_TEMPORARY_DEFAULT
    return saved_default_working_dir() or PRESETS["proberautomation"]


def set_default_working_dir(path: str) -> None:
    data = _load_pref()
    data["working_dir"] = path
    try:
        with open(_PREF_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def _looks_like_project_root(path: str) -> bool:
    """Does `path` actually hold this app's own project layout (a "GUI
    System" folder, or at least one *ata folder) - not just any reachable
    directory. The exe's own install folder is normally just the exe/code
    itself with neither (confirmed: labviewtest has no GUI System/ATA
    folders of its own, only its parent does) - checking mere existence
    would stop the fallback search there and never reach the parent that
    actually holds the data."""
    if not path or not os.path.isdir(path):
        return False
    try:
        names = os.listdir(path)
    except OSError:
        return False
    if "GUI System" in names:
        return True
    return any(n.lower().endswith("ata") and os.path.isdir(os.path.join(path, n))
              for n in names)


def _fallback_candidates() -> list:
    """Where to look for the real working directory if the configured one
    (preset or saved pref) isn't reachable right now - the exe's own
    folder, then that folder's parent. Matches the intended real
    deployment: the GUI lives locally as an exe, and the project data
    (GUI System + ATA folders) sits either right beside it or one level
    up, so a dead/disconnected network share for the *configured* location
    doesn't have to mean a dead app - it can still find a local copy."""
    base = _exe_dir()
    return [base, os.path.dirname(base)]


_current = None


def get_current_working_dir() -> str:
    global _current
    if _current is None:
        _current = get_default_working_dir()
    # The configured directory itself only needs to be REACHABLE, not
    # complete - one that exists but has no GUI System/ATA folders yet is
    # a legitimate first-run state (see app._check_machine_config_folder's
    # own create-it prompt) and must NOT be silently swapped out from
    # under that flow just because nothing has been scaffolded there yet.
    if os.path.isdir(_current):
        return _current
    # Only a directory that flat-out cannot be reached (network share
    # down, wrong/renamed path) falls back - here, both fallback
    # candidates DO need the completeness check (not just reachability),
    # since the exe's own folder always "exists" trivially and would
    # otherwise win by default even when it's just code with no project
    # data in it, leaving the parent (which actually has it) never tried.
    # Re-checked live on every call, so a share coming back online is
    # picked up again without restarting the app.
    for candidate in _fallback_candidates():
        if _looks_like_project_root(candidate):
            return candidate
    return _current


def set_current_working_dir(path: str) -> None:
    global _current
    _current = path


def gui_system_dir() -> str:
    """The "GUI System" folder for whichever working directory is active
    right now - moves with it, since it lives on a shared network location
    alongside the ATA folders rather than at one fixed local path."""
    return os.path.join(get_current_working_dir(), "GUI System")
