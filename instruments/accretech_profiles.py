"""Per-bench instrument profiles for the Accretech probers.

Mirrors instruments/eg_profiles.py's shape (GUI System/accretech_probers.yaml
records each bench; this module selects between them) - Accretech has always
had exactly one bench (probe08) with five fixed instrument keys hardcoded
into gui/app.py's init_hardware(), which is what made "Add Prober" and
swapping an instrument's MODEL (e.g. the SMU: Keithley 2636B vs Keithley
2400) impossible before this file existed. Same plug-in shape as EG: the
drivers resolve their address through instruments.yaml, so switching bench
(or editing an instrument on the active one) writes into that file's plain
top-level entries - nothing downstream has to know profiles exist.

MODEL is the one thing EG profiles do not need and this one does - EG only
varies which KEYS are fitted, never what class a given key resolves to
(smu_eg is always a 2400). Accretech's "smu" key can be either a
Keithley2636B or a Keithley2400, so each instrument entry also carries a
"model" field, and gui/app.py's own _ACCRETECH_MODELS registry (driver
classes live there, not here, same separation eg_profiles.py keeps from
gui/app.py's _EG_DRIVERS) decides which class that model name means.
"""

import yaml

from instruments.gpib_base import get_machine_config_path

_PROFILES_FILE = "accretech_probers.yaml"

# Every Accretech instrument slot - fixed, unlike EG_KEYS's per-bench
# fitted/unfitted set, since every bench built so far has had exactly these
# five. A key absent from a profile still means "not fitted" like EG, this
# just hasn't come up yet.
ACCR_KEYS = ("prober", "smu", "dmm", "switch_matrix", "wave_gen")

_KEY_LABELS = {
    "prober": "Prober", "smu": "SMU", "dmm": "DMM",
    "switch_matrix": "Switch Matrix", "wave_gen": "Wave Gen",
}

# Model names valid per slot, for the Setup tab's dropdown - just strings
# here, no driver imports (gui/app.py's _ACCRETECH_MODELS resolves a name to
# an actual class). Every non-SMU slot lists its one real driver so the
# dropdown is consistent everywhere without inventing fake alternatives.
MODEL_CHOICES = {
    "prober": ("AccretechUF200R",),
    "smu": ("Keithley2636B", "Keithley2400"),
    "dmm": ("Keysight34461A",),
    "switch_matrix": ("Keithley707B",),
    "wave_gen": ("Keysight33512B",),
}

DEFAULT_MODEL = {
    "prober": "AccretechUF200R",
    "smu": "Keithley2636B",
    "dmm": "Keysight34461A",
    "switch_matrix": "Keithley707B",
    "wave_gen": "Keysight33512B",
}


def _path() -> str:
    return get_machine_config_path(_PROFILES_FILE)


def load() -> dict:
    # A missing accretech_probers.yaml (fresh machine, GUI System declined,
    # or simply never created before this file existed) means "no benches
    # recorded yet" - not a reason to crash every panel that asks for the
    # active bench during construction. ensure_default_file() is what turns
    # this into a real probe08 entry, called once at startup.
    try:
        with open(_path(), "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except (OSError, ValueError):
        return {}


def _save(data: dict) -> None:
    with open(_path(), "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, default_flow_style=False, sort_keys=False,
                       allow_unicode=True, width=100)


def ensure_default_file() -> bool:
    """First-run scaffold - one "probe08" bench, seeded from whatever is
    CURRENTLY in instruments.yaml's flat Accretech keys if that file
    already has real addresses saved (an existing installation upgrading
    to this file), so probe08 keeps working exactly as it did before this
    module existed - same addresses, same models (2636B/UF200R/etc, i.e.
    DEFAULT_MODEL), same timeouts. Returns False if accretech_probers.yaml
    already existed (left untouched)."""
    path = _path()
    if __import__("os").path.exists(path):
        return False
    instruments = {}
    try:
        with open(get_machine_config_path("instruments.yaml"), "r", encoding="utf-8") as fh:
            live = (yaml.safe_load(fh) or {}).get("instruments") or {}
    except (OSError, ValueError):
        live = {}
    for key in ACCR_KEYS:
        existing = live.get(key) or {}
        instruments[key] = {
            "name": existing.get("name", _KEY_LABELS.get(key, key)),
            "address": existing.get("address", ""),
            "timeout_ms": int(existing.get("timeout_ms", 3000)),
            "model": DEFAULT_MODEL[key],
        }
    data = {"active": "probe08",
           "probers": {"probe08": {"label": "probe08", "instruments": instruments}}}
    _save(data)
    return True


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
        return {}
    profile = (data.get("probers") or {}).get(name)
    if profile is None:
        raise KeyError(f"no Accretech profile named {name!r} "
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


def model_of(key: str, name: str = None) -> str:
    entry = instruments(name).get(key) or {}
    return entry.get("model") or DEFAULT_MODEL.get(key, "")


def apply_to_instruments_yaml(name: str = None) -> list:
    """Point instruments.yaml's flat Accretech keys at this bench's
    addresses. Returns the keys that changed. Only ACCR_KEYS are touched,
    so the Electroglas half of the file (including smu_eg - Accretech's own
    2400 model uses a Keithley2400 pointed at THIS profile's own "smu" key
    instead, see gui/app.py, precisely so the two never collide here)."""
    name = name or active_name()
    inst = instruments(name)
    yaml_path = get_machine_config_path("instruments.yaml")
    with open(yaml_path, "r", encoding="utf-8") as fh:
        live = yaml.safe_load(fh) or {}
    live.setdefault("instruments", {})

    changed = []
    for key in ACCR_KEYS:
        entry = inst.get(key)
        if not entry:
            continue
        want = {"name": entry.get("name", key),
                "protocol": "GPIB",
                "address": entry.get("address", ""),
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
    (or the active one) - the Setup tab's "+ Add Prober", now real."""
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
        raise KeyError(f"no Accretech profile named {source!r}")
    probers[new_name] = copy.deepcopy(probers[source])
    probers[new_name]["label"] = new_name
    _save(data)


def set_instrument(bench: str, key: str, *, name: str = None,
                   address: str = None, timeout_ms: int = None,
                   model: str = None) -> None:
    """Add or update one instrument entry on `bench` - the Setup tab's
    per-instrument editor. Only the given (non-None) fields change."""
    if key not in ACCR_KEYS:
        raise ValueError(f"{key!r} is not a known instrument key "
                         f"(expected one of {ACCR_KEYS})")
    if model is not None and model not in MODEL_CHOICES.get(key, ()):
        raise ValueError(f"{model!r} is not a valid model for {key!r} "
                         f"(expected one of {MODEL_CHOICES.get(key, ())})")
    data = load()
    probers = data.get("probers") or {}
    if bench not in probers:
        raise KeyError(f"no Accretech profile named {bench!r}")
    inst = probers[bench].setdefault("instruments", {})
    entry = inst.setdefault(key, {"model": DEFAULT_MODEL.get(key, "")})
    if name is not None:
        entry["name"] = name
    if address is not None:
        entry["address"] = address
    if timeout_ms is not None:
        entry["timeout_ms"] = int(timeout_ms)
    if model is not None:
        entry["model"] = model
    _save(data)


def set_active(name: str) -> list:
    """Make `name` the active bench and push its addresses into instruments.yaml."""
    data = load()
    if name not in (data.get("probers") or {}):
        raise KeyError(f"no Accretech profile named {name!r}")
    data["active"] = name
    _save(data)
    return apply_to_instruments_yaml(name)


def summary(name: str = None) -> str:
    """One-line-per-instrument description, for logging a switch."""
    name = name or active_name()
    lines = [f"{name}: {label(name)}"]
    inst = instruments(name)
    for key in ACCR_KEYS:
        entry = inst.get(key)
        if not entry:
            continue
        lines.append(f"   {_KEY_LABELS.get(key, key):<14} "
                     f"{entry.get('model', ''):<16} {entry.get('address', '')}")
    return "\n".join(lines)
