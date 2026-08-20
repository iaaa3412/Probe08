import json
import os
import platform

# Named presets for the project root that holds the ATA folders and "GUI
# System" - a plain custom path still works via the working-directory
# Browse button, these are just the two locations anyone actually switches
# between.
PRESETS = {
    "automationproject": "C:/automationproject",
    "proberautomation": r"\\prober\M\ETL\proberautomation",
}

# This file's own directory is fixed regardless of which working directory
# is chosen - it lives next to the app itself, not inside "GUI System".
# "GUI System" now lives INSIDE whichever working directory is picked (see
# gui_system_dir() below), so "which working directory to default to on
# this PC" can't be stored there without a chicken-and-egg problem on the
# very first read on a fresh machine.
_PREF_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "working_dir_pref.json"))

# TEMPORARY: pinned to automationproject for now - proberautomation is
# still being populated/updated on the user's end, so nothing should touch
# it yet. Once the user confirms the move to proberautomation is complete,
# flip this to PRESETS["proberautomation"] (that was the state as of the
# request to switch defaults - see conversation history). Overrides any
# saved preference in the meantime; get_default_working_dir() already falls
# back to the saved preference / the automationproject preset on its own
# without this line at all.
_FORCE_TEMPORARY_DEFAULT = PRESETS["automationproject"]


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
    return saved_default_working_dir() or PRESETS["automationproject"]


def set_default_working_dir(path: str) -> None:
    data = _load_pref()
    data["working_dir"] = path
    try:
        with open(_PREF_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


_current = None


def get_current_working_dir() -> str:
    global _current
    if _current is None:
        _current = get_default_working_dir()
    return _current


def set_current_working_dir(path: str) -> None:
    global _current
    _current = path


def gui_system_dir() -> str:
    """The "GUI System" folder for whichever working directory is active
    right now - moves with it, since it lives on a shared network location
    alongside the ATA folders rather than at one fixed local path."""
    return os.path.join(get_current_working_dir(), "GUI System")
