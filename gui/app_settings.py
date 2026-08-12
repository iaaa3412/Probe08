import json
import os
import sys

# When frozen by PyInstaller, __file__-relative paths land inside the
# bundle's extracted _internal/ folder (onedir) or a temp dir (onefile) -
# both are wrong for a persistent, user-writable settings file, since
# onefile's temp dir is wiped on every exit and onedir's _internal/ can
# require admin rights if installed under Program Files. sys.executable's
# directory (where AtomicaTester.exe itself sits) is the stable, normally
# user-writable location in both frozen cases; only fall back to this
# module's own directory when running from source (not frozen).
if getattr(sys, "frozen", False):
    _SETTINGS_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    _SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS_PATH = os.path.join(_SETTINGS_DIR, "app_settings.json")


def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_settings(data: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_default_ata_folder(system: str) -> "str | None":
    return load_settings().get("default_ata_folder", {}).get(system)


def set_default_ata_folder(system: str, folder: str) -> None:
    data = load_settings()
    data.setdefault("default_ata_folder", {})[system] = folder
    save_settings(data)


# The prober the GUI should come up on. Stored as (system, bench) together
# rather than just a bench name, because the system is what decides which
# whole UI is shown and a bench name alone would need a lookup to resolve -
# one that would break the moment a bench is renamed or removed.
def get_default_prober() -> "tuple[str, str] | tuple[None, None]":
    entry = load_settings().get("default_prober") or {}
    system, bench = entry.get("system"), entry.get("bench")
    return (system, bench) if system else (None, None)


def set_default_prober(system: str, bench: str) -> None:
    data = load_settings()
    data["default_prober"] = {"system": system, "bench": bench}
    save_settings(data)


def clear_default_prober() -> None:
    data = load_settings()
    data.pop("default_prober", None)
    save_settings(data)


# Per-channel assignments for the Electroglas relay cards. The GUI only knows
# what the CURRENT project wired (hp_switchbox.BENCH_WIRING covers probe02's
# CH00-03 and probe03's eight); every other channel on all three cards is
# physically there and unused. Recording what a channel is for, per bench,
# keeps that knowledge with the machine instead of in someone's memory - and a
# future project can claim spare channels without re-deriving which are free.
#
# Keyed bench -> "driver_key/NN" -> label, so a channel's meaning survives a
# card being swapped between secondary addresses.

def get_channel_assignments(bench: str) -> dict:
    data = load_settings().get("channel_assignments", {})
    return dict(data.get(str(bench), {}))


def set_channel_assignments(bench: str, assignments: dict) -> None:
    data = load_settings()
    store = data.setdefault("channel_assignments", {})
    # Drop blanks rather than storing empty strings: "no assignment" and
    # "assigned to nothing" should not be two different states in the file.
    store[str(bench)] = {k: v.strip() for k, v in assignments.items()
                         if (v or "").strip()}
    save_settings(data)


def set_channel_assignment(bench: str, key: str, label: str) -> None:
    current = get_channel_assignments(bench)
    if (label or "").strip():
        current[key] = label.strip()
    else:
        current.pop(key, None)
    set_channel_assignments(bench, current)
