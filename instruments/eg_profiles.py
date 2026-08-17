"""Per-bench instrument profiles for the Electroglas probers.

The EG benches are not built alike - different instruments, different GPIB
addresses, and the same secondary address holding a different relay card from
one bench to the next. GUI System/eg_probers.yaml records each bench; this
module selects between them.

HOW IT PLUGS IN. The drivers all resolve their address through
instruments.yaml, so switching profile writes the active bench's addresses into
that file's *_eg entries. Nothing downstream has to know profiles exist, and
instruments.yaml stays an honest picture of what the GUI is currently pointed
at. The profile file remains the source of truth; instruments.yaml is derived.
Both files live in GUI System/, next to app_settings.json - real per-machine
setup, not program source.
"""

import yaml

from instruments.gpib_base import get_machine_config_path

_PROFILES_FILE = "eg_probers.yaml"

# Every EG instrument key a profile may define. A key absent from a profile is
# treated as not fitted on that bench rather than an error - benches differ, and
# that is the whole point.
EG_KEYS = ("prober_eg", "smu_eg", "dmm_eg", "dmm_vxi_eg",
           "relay1_eg", "relay2_eg", "relay3_eg", "power_supply_eg")


def _path() -> str:
    return get_machine_config_path(_PROFILES_FILE)


def load() -> dict:
    # A missing eg_probers.yaml (fresh machine, GUI System declined at
    # startup) means "no benches recorded yet" - the same as app_settings's
    # load_settings(), not a reason to crash every panel that asks for the
    # active bench during construction.
    try:
        with open(_path(), "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except (OSError, ValueError):
        return {}


def _save(data: dict) -> None:
    with open(_path(), "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, default_flow_style=False, sort_keys=False,
                       allow_unicode=True, width=100)


def profile_names() -> list:
    return sorted((load().get("probers") or {}).keys())


def active_name() -> str:
    data = load()
    name = data.get("active")
    names = sorted((data.get("probers") or {}).keys())
    if name in names:
        return name
    return names[0] if names else ""


def get(name: str = None) -> dict:
    data = load()
    name = name or active_name()
    if not name:
        # No bench recorded at all yet (fresh/declined GUI System folder) -
        # that is a legitimate "nothing to show" for every read-only
        # accessor built on top of get(), not an error. A KeyError is only
        # for a caller asking about a SPECIFIC bench that doesn't exist.
        return {}
    profile = (data.get("probers") or {}).get(name)
    if profile is None:
        raise KeyError(f"no Electroglas profile named {name!r} "
                       f"(known: {sorted((data.get('probers') or {}))})")
    return profile


def label(name: str = None) -> str:
    name = name or active_name()
    try:
        return get(name).get("label") or name
    except KeyError:
        return name


def instruments(name: str = None) -> dict:
    return get(name).get("instruments") or {}


def is_fitted(key: str, name: str = None) -> bool:
    entry = instruments(name).get(key)
    return bool(entry and entry.get("fitted", True))


def fitted_keys(name: str = None) -> list:
    """Keys actually on this bench, in EG_KEYS order."""
    inst = instruments(name)
    return [k for k in EG_KEYS if k in inst and inst[k].get("fitted", True)]


def roster(name: str = None) -> list:
    """(display name, key, id_queries, fitted, write_probe) per instrument.

    The shape gui/instruments_eg_panel.py wants for its address table. Every
    key the profile defines is listed, fitted or not - a known absence should be
    visible and individually pingable, not hidden.
    """
    inst = instruments(name)
    out = []
    for key in EG_KEYS:
        entry = inst.get(key)
        if not entry:
            continue
        out.append((entry.get("name", key),
                    key,
                    tuple(entry.get("id_queries") or ()),
                    bool(entry.get("fitted", True)),
                    entry.get("write_probe")))
    return out


def apply_to_instruments_yaml(name: str = None) -> list:
    """Point instruments.yaml at this profile's addresses.

    Returns the keys that changed. Only *_eg keys are touched, so the Accretech
    half of the file is left exactly as it was.
    """
    name = name or active_name()
    inst = instruments(name)
    yaml_path = get_machine_config_path("instruments.yaml")
    with open(yaml_path, "r", encoding="utf-8") as fh:
        live = yaml.safe_load(fh) or {}
    live.setdefault("instruments", {})

    changed = []
    for key in EG_KEYS:
        entry = inst.get(key)
        if not entry:
            continue
        want = {"name": entry.get("name", key),
                "protocol": "GPIB",
                "address": entry["address"],
                "timeout_ms": int(entry.get("timeout_ms", 3000))}
        if live["instruments"].get(key) != want:
            live["instruments"][key] = want
            changed.append(key)

    if changed:
        with open(yaml_path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(live, fh, default_flow_style=False, sort_keys=False)
    return changed


def add_profile(new_name: str, based_on: str = None) -> None:
    """Create a new bench profile, starting as a full copy of `based_on`
    (or the active one) - the Setup tab's "+ Add Prober". Copies every
    field, including notes/scanned/id_queries, so the new bench starts as
    a real duplicate rather than an empty shell; the label is reset to
    the new name since the old one describes the SOURCE bench.
    """
    import copy
    new_name = (new_name or "").strip()
    if not new_name:
        raise ValueError("prober name cannot be blank")
    data = load()
    probers = data.setdefault("probers", {})
    if new_name in probers:
        raise ValueError(f"a profile named {new_name!r} already exists")
    source = based_on or active_name()
    if source not in probers:
        raise KeyError(f"no Electroglas profile named {source!r}")
    probers[new_name] = copy.deepcopy(probers[source])
    probers[new_name]["label"] = new_name
    _save(data)


def set_instrument(bench: str, key: str, *, name: str = None,
                   address: str = None, timeout_ms: int = None,
                   fitted: bool = None) -> None:
    """Add or update one instrument entry on `bench` - the Setup tab's
    per-instrument editor. Only the given (non-None) fields change; on an
    EXISTING entry, notes/scanned/id_queries/write_probe are left exactly
    as they were - Setup does not expose or touch those. A brand new
    entry gets id_queries=[] (no probe-specific ID query known yet).
    """
    if key not in EG_KEYS:
        raise ValueError(f"{key!r} is not a known instrument key "
                         f"(expected one of {EG_KEYS})")
    data = load()
    probers = data.get("probers") or {}
    if bench not in probers:
        raise KeyError(f"no Electroglas profile named {bench!r}")
    inst = probers[bench].setdefault("instruments", {})
    entry = inst.setdefault(key, {"id_queries": []})
    if name is not None:
        entry["name"] = name
    if address is not None:
        entry["address"] = address
    if timeout_ms is not None:
        entry["timeout_ms"] = int(timeout_ms)
    if fitted is not None:
        entry["fitted"] = bool(fitted)
    _save(data)


def remove_instrument(bench: str, key: str) -> None:
    """Drop one instrument entry from `bench` entirely - not just marking
    it unfitted, actually removing the row, for "this bench never had
    one of these" rather than "has one but it's not connected"."""
    data = load()
    probers = data.get("probers") or {}
    if bench not in probers:
        raise KeyError(f"no Electroglas profile named {bench!r}")
    (probers[bench].get("instruments") or {}).pop(key, None)
    _save(data)


def set_active(name: str) -> list:
    """Make `name` the active bench and push its addresses into instruments.yaml."""
    data = load()
    if name not in (data.get("probers") or {}):
        raise KeyError(f"no Electroglas profile named {name!r}")
    data["active"] = name
    _save(data)
    return apply_to_instruments_yaml(name)


def summary(name: str = None) -> str:
    """One-line-per-instrument description, for logging a switch."""
    name = name or active_name()
    lines = [f"{name}: {label(name)}"]
    for display, key, _queries, fitted, _probe in roster(name):
        addr = instruments(name)[key]["address"]
        lines.append(f"   {'ok ' if fitted else '-- '} {display:<34} {addr}")
    return "\n".join(lines)
