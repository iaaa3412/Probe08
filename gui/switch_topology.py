import os
import string
import yaml

import workdir

# Real per-machine setup - how this bench's switch matrix is actually wired -
# lives outside the repo next to app_settings.json/instruments.yaml, not
# under instruments/. See gui/app_settings.py's module docstring.
#
# This describes a bench's physical wiring, not a per-PC preference, so
# unlike app_settings.py's defaults it stays ONE shared file - it just now
# lives inside whichever working directory is active (workdir.gui_system_
# dir()), since "GUI System" moved to a shared network folder. TOPOLOGY_PATH
# stays available as a plain attribute (switch_settings_panel.py and
# app_settings.py read it directly) via module __getattr__ below, so it
# always reflects the CURRENT working directory instead of being frozen at
# whatever it was when this module first imported.
#
# BENCH-SCOPED as of the probe08new (Keithley 2400) bring-up: probe08 has
# its SMU's real second channel (rows C/D) and a wave gen (rows G/H) wired;
# probe08new's 2400 has neither (2400 is single-channel, and this bench has
# no wave gen fitted at all - see instruments/accretech_profiles.py). One
# global file/cache meant editing the wiring for whichever bench happened
# to be active at the time silently applied to BOTH benches the moment
# either one was reloaded - "save settings acting weird when switching
# between the two probers" was exactly that: there was never a per-bench
# file to switch between. Each bench now gets its own {slots, row_roles}
# block under one "benches:" file, the same shape accretech_probers.yaml
# already uses for instrument profiles.


def _config_dir() -> str:
    return workdir.gui_system_dir()


def _topology_path() -> str:
    return os.path.join(_config_dir(), "switch_topology.yaml")


def __getattr__(name):
    if name == "TOPOLOGY_PATH":
        return _topology_path()
    if name == "_CONFIG_DIR":
        return _config_dir()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

ROW_LETTERS_POOL = list(string.ascii_uppercase)
MIN_ROW_COUNT = 1
MAX_ROW_COUNT = len(ROW_LETTERS_POOL)
INSTRUMENTS = ("SMU", "DMM", "WGEN", "")
SMU_CHANNELS = ("A", "B")
WGEN_CHANNELS = ("CH1", "CH2")
# SHI/SLO are the 4-wire SENSE legs, used only by "ohmf" recipe steps. A rig
# without them wired simply leaves no row assigned those roles; the recipe
# validator then says so rather than silently routing three wires.
POLARITIES = ("HI", "LO", "SHI", "SLO")

DEFAULT_TOPOLOGY = {
    "slots": [
        {"slot": "2", "cols": 12, "rows": ["A", "B", "C", "D", "E", "F", "G", "H"]},
        {"slot": "4", "cols": 12, "rows": ["A", "B", "C", "D", "E", "F", "G", "H"]},
    ],
    "row_roles": {
        "A": {"instrument": "SMU",  "channel": "A",   "polarity": "HI"},
        "B": {"instrument": "SMU",  "channel": "A",   "polarity": "LO"},
        "C": {"instrument": "SMU",  "channel": "B",   "polarity": "HI"},
        "D": {"instrument": "SMU",  "channel": "B",   "polarity": "LO"},
        "E": {"instrument": "DMM",  "channel": "",    "polarity": "LO"},
        "F": {"instrument": "DMM",  "channel": "",    "polarity": "HI"},
        "G": {"instrument": "WGEN", "channel": "CH1", "polarity": "HI"},
        "H": {"instrument": "WGEN", "channel": "CH2", "polarity": "HI"},
    },
}

# The bench this file already assumed for its whole existence pre-dating
# per-bench profiles - what an old flat (no "benches:" key) file migrates
# its one topology into, and the seed a brand-new file starts from.
_LEGACY_BENCH = "probe08"

_cache = None


def _default_copy() -> dict:
    return {"slots": [dict(s) for s in DEFAULT_TOPOLOGY["slots"]],
            "row_roles": {k: dict(v) for k, v in DEFAULT_TOPOLOGY["row_roles"].items()}}


def _active_bench() -> str:
    """Which bench a bench-less call means - the accretech_probers.yaml
    active bench, same one the toolbar/Setup tab picker shows. Lazily
    imported: instruments/accretech_profiles.py has no reason to import
    this gui/ module, so importing it back here at module load time would
    be the wrong direction - this mirrors every other lazy cross-import in
    this codebase (see wafer_map_view._valid_pins)."""
    try:
        from instruments import accretech_profiles
        return accretech_profiles.active_name() or _LEGACY_BENCH
    except Exception:
        return _LEGACY_BENCH


def _migrate(data: dict) -> dict:
    if "benches" in data:
        return data
    if data.get("slots") and data.get("row_roles"):
        return {"benches": {_LEGACY_BENCH: {"slots": data["slots"],
                                            "row_roles": data["row_roles"]}}}
    return {"benches": {}}


def _load_all(force: bool = False) -> dict:
    global _cache
    if _cache is not None and not force:
        return _cache
    path = _topology_path()
    data = {}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, ValueError):
            data = {}
    _cache = _migrate(data)
    return _cache


def _write_all(data: dict):
    global _cache
    _cache = data
    os.makedirs(_config_dir(), exist_ok=True)
    with open(_topology_path(), "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def bench_names() -> list:
    return sorted(_load_all().get("benches", {}).keys())


def load_topology(bench: str = None, force: bool = False) -> dict:
    """This bench's {slots, row_roles} - the active bench if none is given.
    A bench with nothing saved yet (a brand-new prober added on the Setup
    tab) starts from the same full default layout probe08 always has -
    safe until the operator narrows it down to what's actually wired, the
    same way probe08new needs to be narrowed to just A/B/E/F now that its
    2400 has no second channel or wave gen."""
    all_data = _load_all(force=force)
    bench = bench or _active_bench()
    benches = all_data.setdefault("benches", {})
    if bench not in benches:
        benches[bench] = _default_copy()
    return benches[bench]


def save_topology(data: dict, bench: str = None):
    bench = bench or _active_bench()
    all_data = _load_all()
    all_data.setdefault("benches", {})[bench] = data
    _write_all(all_data)


def reset_topology(bench: str = None) -> dict:
    bench = bench or _active_bench()
    data = _default_copy()
    save_topology(data, bench)
    return data


def ensure_default_file() -> bool:
    """First-run scaffold - write the built-in default topology for
    probe08 if this machine has no switch_topology.yaml yet. Returns False
    if the file already existed (left untouched). Other benches are seeded
    on first read (see load_topology) rather than here, since a machine's
    set of Accretech benches can grow after this file already exists."""
    if os.path.exists(_topology_path()):
        return False
    _write_all({"benches": {_LEGACY_BENCH: _default_copy()}})
    return True


def slots(bench: str = None) -> list:
    return load_topology(bench)["slots"]


def row_roles(bench: str = None) -> dict:
    return load_topology(bench)["row_roles"]


def row_letters(bench: str = None) -> list:
    return sorted(row_roles(bench).keys())


def role_label(role: dict) -> str:
    instrument = (role or {}).get("instrument", "")
    channel = (role or {}).get("channel", "")
    polarity = (role or {}).get("polarity", "")
    if not instrument:
        return "(unused)"
    if instrument == "WGEN":
        return f"WGEN {channel}".strip()
    shown = {"SHI": "SENSE HI", "SLO": "SENSE LO"}.get(polarity, polarity)
    label = " ".join(b for b in (instrument, channel, shown) if b)
    if instrument == "SMU" and polarity == "LO":
        label += "/GND"
    return label


def total_pins(bench: str = None) -> int:
    return sum(spec.get("cols", 0) for spec in slots(bench))


def pin_numbers(bench: str = None) -> list:
    """Every valid probe-card pin number on this bench, as strings ("1".."24"
    by default) - always re-derived from the live topology (slots x cols),
    so widening Switch Settings later widens this too with no separate list
    to keep in sync."""
    return [str(n) for n in range(1, total_pins(bench) + 1)]


def slot_and_col_for_pin(pin_no: int, bench: str = None):
    remaining = pin_no
    for spec in slots(bench):
        cols = spec.get("cols", 0)
        if remaining <= cols:
            return spec["slot"], remaining
        remaining -= cols
    return None, None


def pin_channel(pin_no: int, row: str, bench: str = None) -> str:
    slot, col = slot_and_col_for_pin(pin_no, bench)
    if slot is None:
        return ""
    return f"{slot}{row}{col:02d}"


def rows_for(step_type: str, chan: str, instrument: str, bench: str = None):
    roles = row_roles(bench)

    def _match(want_instrument, want_channel=None, want_polarity=None):
        out = []
        for letter in sorted(roles):
            role = roles.get(letter)
            if not role or role.get("instrument") != want_instrument:
                continue
            if want_channel is not None and role.get("channel") != want_channel:
                continue
            if want_polarity is not None and role.get("polarity") != want_polarity:
                continue
            out.append(letter)
        return tuple(out)

    if step_type == "wave":
        return _match("WGEN", chan or "CH1"), _match("SMU", "A", "LO")
    if instrument == "DMM":
        return _match("DMM", want_polarity="HI"), _match("DMM", want_polarity="LO")
    if instrument == "SMU":
        want_chan = chan or "A"
        return _match("SMU", want_chan, "HI"), _match("SMU", want_chan, "LO")
    return (), ()


def rows_for_fields(step_type: str, chan: str, instrument: str, bench: str = None) -> dict:
    """Switch rows per pin field, so 4-wire steps can carry their sense legs.

    rows_for() is kept as-is for the 2-wire callers; this returns the same
    HI/LO plus his/los when the step is 4-wire. An empty tuple for a sense
    field means no row is assigned that role in this rig's topology.
    """
    rows_hi, rows_lo = rows_for(step_type, chan, instrument, bench)
    fields = {"hi": rows_hi, "lo": rows_lo}
    if step_type == "ohmf":
        roles = row_roles(bench)

        def _sense(polarity):
            return tuple(letter for letter in sorted(roles)
                         if (roles.get(letter) or {}).get("instrument") == "DMM"
                         and (roles.get(letter) or {}).get("polarity") == polarity)

        fields["his"] = _sense("SHI")
        fields["los"] = _sense("SLO")
    return fields
