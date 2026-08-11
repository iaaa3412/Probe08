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
