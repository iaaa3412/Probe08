import json
import os

# Lives next to the project's data folders (LAMPATA, NautATA, ...) rather
# than next to the exe/script - this machine info (default ATA folder,
# default prober, channel assignments) belongs to the project on this PC,
# not to whichever copy of the GUI happens to be running it.
_SETTINGS_DIR = "C:/automationproject/GUI System"

SETTINGS_PATH = os.path.join(_SETTINGS_DIR, "app_settings.json")


def load_settings() -> dict:
    # If "GUI System" hasn't been created yet, there is nothing to load -
    # start blank rather than creating it just to read from it.
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_settings(data: dict) -> None:
    # Saving is an explicit user action (e.g. "Set as Default"), so it's
    # fine to create the folder here even though loading never does.
    os.makedirs(_SETTINGS_DIR, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def machine_config_status() -> dict:
    """Which pieces of this machine's setup exist on disk yet - the startup
    check's source of truth for whether to prompt, and for which files
    specifically to create. Imported lazily to dodge an import cycle
    (instruments.gpib_base has no reason to import this gui/ module)."""
    from instruments import gpib_base
    import switch_topology
    return {
        "folder": os.path.isdir(_SETTINGS_DIR),
        "app_settings.json": os.path.isfile(SETTINGS_PATH),
        "instruments.yaml": os.path.isfile(
            gpib_base.get_machine_config_path("instruments.yaml")),
        "eg_probers.yaml": os.path.isfile(
            gpib_base.get_machine_config_path("eg_probers.yaml")),
        "switch_topology.yaml": os.path.isfile(switch_topology.TOPOLOGY_PATH),
    }


def create_basic_machine_config() -> list:
    """Create whichever of this machine's setup files are missing, each
    with a blank/no-defaults starter shape - never guesses a real address,
    just the key structure the Setup tab expects to edit. Leaves anything
    that already exists untouched. Returns the filenames actually created."""
    from instruments import gpib_base
    import switch_topology
    os.makedirs(_SETTINGS_DIR, exist_ok=True)
    created = []
    if not os.path.isfile(SETTINGS_PATH):
        save_settings({})
        created.append("app_settings.json")
    if gpib_base.create_default_instruments_yaml():
        created.append("instruments.yaml")
    if gpib_base.create_default_eg_probers_yaml():
        created.append("eg_probers.yaml")
    if switch_topology.ensure_default_file():
        created.append("switch_topology.yaml")
    return created


# One default ATA folder for the whole project - not per system. Only one
# prober is ever actually running against real data at a time, and having
# Accretech/Electroglas remember different defaults was extra state nobody
# asked for.
def get_default_ata_folder() -> "str | None":
    return load_settings().get("default_ata_folder")


def set_default_ata_folder(folder: str) -> None:
    data = load_settings()
    data["default_ata_folder"] = folder
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
