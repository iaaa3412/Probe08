import os
import yaml

_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "instruments")
TOPOLOGY_PATH = os.path.join(_CONFIG_DIR, "switch_topology.yaml")

ROW_LETTERS = list("ABCDEFGH")
INSTRUMENTS = ("SMU", "DMM", "WGEN", "")
SMU_CHANNELS = ("A", "B")
WGEN_CHANNELS = ("CH1", "CH2")
POLARITIES = ("HI", "LO")

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

_cache = None


def _default_copy() -> dict:
    return {"slots": [dict(s) for s in DEFAULT_TOPOLOGY["slots"]],
            "row_roles": {k: dict(v) for k, v in DEFAULT_TOPOLOGY["row_roles"].items()}}


def load_topology(force: bool = False) -> dict:
    global _cache
    if _cache is not None and not force:
        return _cache
    if os.path.exists(TOPOLOGY_PATH):
        try:
            with open(TOPOLOGY_PATH, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and data.get("slots") and data.get("row_roles"):
                _cache = data
                return _cache
        except (OSError, ValueError):
            pass
    _cache = _default_copy()
    return _cache


def save_topology(data: dict):
    global _cache
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(TOPOLOGY_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
    _cache = data


def reset_topology() -> dict:
    data = _default_copy()
    save_topology(data)
    return data


def slots() -> list:
    return load_topology()["slots"]


def row_roles() -> dict:
    return load_topology()["row_roles"]


def role_label(role: dict) -> str:
    instrument = (role or {}).get("instrument", "")
    channel = (role or {}).get("channel", "")
    polarity = (role or {}).get("polarity", "")
    if not instrument:
        return "(unused)"
    if instrument == "WGEN":
        return f"WGEN {channel}".strip()
    label = " ".join(b for b in (instrument, channel, polarity) if b)
    if instrument == "SMU" and polarity == "LO":
        label += "/GND"
    return label


def total_pins() -> int:
    return sum(spec.get("cols", 0) for spec in slots())


def slot_and_col_for_pin(pin_no: int):
    remaining = pin_no
    for spec in slots():
        cols = spec.get("cols", 0)
        if remaining <= cols:
            return spec["slot"], remaining
        remaining -= cols
    return None, None


def pin_channel(pin_no: int, row: str) -> str:
    slot, col = slot_and_col_for_pin(pin_no)
    if slot is None:
        return ""
    return f"{slot}{row}{col:02d}"


def rows_for(step_type: str, chan: str, instrument: str):
    roles = row_roles()

    def _match(want_instrument, want_channel=None, want_polarity=None):
        out = []
        for letter in ROW_LETTERS:
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
