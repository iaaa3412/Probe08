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

# The five slots every Accretech bench has ALWAYS had - fixed, unlike
# EG_KEYS's per-bench fitted/unfitted set. These can never be removed
# (see remove_instrument), only marked fitted=False (e.g. a disconnected
# wave gen a bench genuinely doesn't have wired), and Setup's own table
# always shows all five whether fitted or not. A bench can ALSO carry
# extra, custom-keyed slots beyond these five - see add_instrument/
# all_keys - for equipment this project has no driver class for yet.
ACCR_KEYS = ("prober", "smu", "dmm", "switch_matrix", "wave_gen")

_KEY_LABELS = {
    "prober": "Prober", "smu": "SMU", "dmm": "DMM",
    "switch_matrix": "Switch Matrix", "wave_gen": "Wave Gen",
}

# Stands in for a real driver class on a custom-added slot (see
# add_instrument) - gui/app.py's _ACCRETECH_MODELS/init_hardware() build a
# bare GPIBInstrument for this instead of a real subclass, which still
# opens the address and answers a plain *IDN?/serial-poll presence check
# (see _connect_instruments's driver.query("*IDN?") fallback) - enough to
# name it and see it go green/red in the sidebar without writing a driver.
# Someone can write a real one later and switch this slot's model to it
# the same way an SMU gets swapped between 2636B/2400.
GENERIC_MODEL = "Generic (no driver yet)"

# Model names valid per slot, for the Setup tab's dropdown - just strings
# here, no driver imports (gui/app.py's _ACCRETECH_MODELS resolves a name to
# an actual class). Every non-SMU CORE slot lists its one real driver so the
# dropdown is consistent everywhere without inventing fake alternatives. A
# custom slot (key not listed here at all) always gets just (GENERIC_MODEL,)
# - see model_choices_for().
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


def model_choices_for(key: str) -> tuple:
    """Model choices for the Setup tab's dropdown. A core slot (key
    already in MODEL_CHOICES) is unchanged - its own fixed short list.
    A custom slot (Setup tab's "+ Add Instrument") gets GENERIC_MODEL
    (no driver required - see GENERIC_MODEL's own comment) PLUS every
    model already coded for some OTHER slot, so equipment this project
    already has a working driver for (e.g. a spare 707B) can be added
    without waiting on new driver code, alongside the option to add
    something genuinely undefined."""
    if key in MODEL_CHOICES:
        return MODEL_CHOICES[key]
    seen = [GENERIC_MODEL]
    for models in MODEL_CHOICES.values():
        for m in models:
            if m not in seen:
                seen.append(m)
    return tuple(seen)


def _slugify_key(display_name: str) -> str:
    slug = "".join(c.lower() if c.isalnum() else "_" for c in display_name.strip())
    slug = "_".join(p for p in slug.split("_") if p)
    return slug or "instrument"


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
    return entry.get("model") or DEFAULT_MODEL.get(key, GENERIC_MODEL)


def is_fitted(key: str, name: str = None) -> bool:
    entry = instruments(name).get(key)
    return bool(entry and entry.get("fitted", True))


def all_keys(name: str = None) -> list:
    """Every slot this bench actually has - the five ACCR_KEYS (always,
    fitted or not) plus whatever custom slots were added (see
    add_instrument), custom ones sorted after the fixed five. This is
    what the Setup tab's table and init_hardware()/apply_to_instruments_
    yaml/summary all iterate, instead of the fixed ACCR_KEYS alone."""
    inst = instruments(name)
    custom = sorted(k for k in inst if k not in ACCR_KEYS)
    return list(ACCR_KEYS) + custom


def fitted_keys(name: str = None) -> list:
    """Keys actually connected on this bench, in all_keys() order - what
    init_hardware() should build a driver/attempt a ping for. Mirrors
    eg_profiles.fitted_keys(); unlike EG, a CORE key is never actually
    ABSENT here (all five always exist in the profile - see ACCR_KEYS's
    own comment) so for those this is purely the fitted=True subset, not
    a presence check too - a custom key, by contrast, IS presence-checked
    (it either exists on this bench or it doesn't)."""
    inst = instruments(name)
    return [k for k in all_keys(name) if k in inst and inst[k].get("fitted", True)]


def apply_to_instruments_yaml(name: str = None) -> list:
    """Point instruments.yaml's flat Accretech keys at this bench's
    addresses. Returns the keys that changed. Only ACCR_KEYS are touched,
    so the Electroglas half of the file (including smu_eg - Accretech's own
    2400 model uses a Keithley2400 pointed at THIS profile's own "smu" key
    instead, see gui/app.py, precisely so the two never collide here).

    Pushes the address for an unfitted key too (same as eg_profiles) - it
    just never gets used, since init_hardware() skips building a driver
    for anything fitted_keys() leaves out. Keeping the address in
    instruments.yaml means re-fitting it later doesn't need the address
    retyped."""
    name = name or active_name()
    inst = instruments(name)
    yaml_path = get_machine_config_path("instruments.yaml")
    with open(yaml_path, "r", encoding="utf-8") as fh:
        live = yaml.safe_load(fh) or {}
    live.setdefault("instruments", {})

    changed = []
    for key in all_keys(name):
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
                   model: str = None, fitted: bool = None) -> None:
    """Update one EXISTING instrument entry on `bench` (core or custom) -
    the Setup tab's per-instrument editor. Only the given (non-None)
    fields change. Does not create a new slot - see add_instrument for
    that; this raises if `key` isn't already on this bench, same as
    eg_profiles.set_instrument only ever updating a present entry."""
    data = load()
    probers = data.get("probers") or {}
    if bench not in probers:
        raise KeyError(f"no Accretech profile named {bench!r}")
    inst = probers[bench].setdefault("instruments", {})
    if key not in inst:
        raise KeyError(f"{key!r} is not a slot on Accretech bench {bench!r} - "
                       "use add_instrument for a new one")
    if model is not None and model not in model_choices_for(key):
        raise ValueError(f"{model!r} is not a valid model for {key!r} "
                         f"(expected one of {model_choices_for(key)})")
    entry = inst[key]
    if name is not None:
        entry["name"] = name
    if address is not None:
        entry["address"] = address
    if timeout_ms is not None:
        entry["timeout_ms"] = int(timeout_ms)
    if model is not None:
        entry["model"] = model
    if fitted is not None:
        entry["fitted"] = bool(fitted)
    _save(data)


def add_instrument(bench: str, display_name: str, *, address: str = "",
                   timeout_ms: int = 3000, fitted: bool = True) -> str:
    """Add a brand new, custom-keyed instrument slot to `bench` - the
    Setup tab's "+ Add Instrument". No driver class is required: it gets
    GENERIC_MODEL, which gui/app.py's init_hardware() turns into a bare
    GPIBInstrument(key) - enough to name it, address it, and see it
    answer a plain *IDN?/serial-poll presence check without anyone having
    written a real driver for it yet (see GENERIC_MODEL's own comment).
    Returns the new slot's key (a slug derived from display_name, de-duped
    with a numeric suffix if it collides with an existing one)."""
    display_name = (display_name or "").strip()
    if not display_name:
        raise ValueError("instrument name cannot be blank")
    data = load()
    probers = data.get("probers") or {}
    if bench not in probers:
        raise KeyError(f"no Accretech profile named {bench!r}")
    inst = probers[bench].setdefault("instruments", {})
    base_key = _slugify_key(display_name)
    key = base_key
    n = 2
    while key in inst:
        key = f"{base_key}_{n}"
        n += 1
    inst[key] = {"name": display_name, "address": address,
                "timeout_ms": int(timeout_ms), "model": GENERIC_MODEL,
                "fitted": bool(fitted)}
    _save(data)
    return key


def remove_instrument(bench: str, key: str) -> None:
    """Drop a CUSTOM instrument slot from `bench` entirely - not
    available for the five core ACCR_KEYS, which always exist (mark them
    fitted=False via set_instrument instead - see ACCR_KEYS's own
    comment)."""
    if key in ACCR_KEYS:
        raise ValueError(f"{key!r} is a core Accretech slot and can't be "
                         "removed - mark it not fitted instead.")
    data = load()
    probers = data.get("probers") or {}
    if bench not in probers:
        raise KeyError(f"no Accretech profile named {bench!r}")
    (probers[bench].get("instruments") or {}).pop(key, None)
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
    for key in all_keys(name):
        entry = inst.get(key)
        if not entry:
            continue
        fitted_note = "" if entry.get("fitted", True) else "  (not fitted)"
        role = _KEY_LABELS.get(key) or entry.get("name") or key
        lines.append(f"   {role:<14} "
                     f"{entry.get('model', ''):<16} {entry.get('address', '')}{fitted_note}")
    return "\n".join(lines)
