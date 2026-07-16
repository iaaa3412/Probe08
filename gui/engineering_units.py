"""SI engineering-prefix parsing/formatting shared by every instrument
value field that sets or reads a voltage/current (Debug tab SMU/DMM/
WaveGen cards, Recipe step editor) — lets a user type "5m" for 5
millivolts/milliamps or "2u"/"2µ" for 2 microamps instead of always
entering/reading raw base-unit floats.

Every driver method (instruments/smu.py, dmm.py, wave_gen.py) takes and
returns plain floats in base SI units (V, A, Ohm, Hz, ...) with no
prefix handling of its own — parse_engineering/format_engineering are
the ONLY place prefix conversion happens; callers still pass/receive
base-unit floats to/from the instrument drivers.
"""
from __future__ import annotations

import re

# Parsing accepts both directions (sub- and super-unit) since it's the
# same generic mechanism either way; the primary ask is milli/micro/nano.
_PARSE_SUFFIXES = {
    "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6,  # µ (micro sign)
    "m": 1e-3, "k": 1e3, "K": 1e3, "M": 1e6,
}

# Largest-to-smallest so format_engineering picks the first (largest)
# prefix the magnitude still fits, avoiding awkward "0.001 m"-style
# near-misses.
_FORMAT_PREFIXES = [
    ("M", 1e6), ("k", 1e3), ("", 1.0),
    ("m", 1e-3), ("µ", 1e-6), ("n", 1e-9), ("p", 1e-12),
]

_NUM_RE = re.compile(r'^\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*([a-zA-Zµ]*)\s*$')


def parse_engineering(text: str) -> float:
    """"5m" -> 0.005, "2u"/"2µ" -> 2e-6, "10n" -> 1e-8, "1.5k" ->
    1500.0, "3.3" -> 3.3 (no suffix = base unit, same as plain float()
    today). A bare unit letter (e.g. a stray "V"/"A" the user typed
    alongside the value) is tolerated and ignored. Raises ValueError —
    same exception plain float() raises on bad input — on anything
    unparsable, so existing try/except ValueError call sites work
    unchanged."""
    m = _NUM_RE.match(text or "")
    if not m:
        raise ValueError(f"Not a number: {text!r}")
    value = float(m.group(1))
    suffix = m.group(2)
    if not suffix:
        return value
    prefix_char = suffix[0]
    if prefix_char in _PARSE_SUFFIXES:
        return value * _PARSE_SUFFIXES[prefix_char]
    # A lone unit letter with no recognized prefix (e.g. "3.3V") -- the
    # unit itself, not a prefix; treat as unscaled rather than rejecting
    # a perfectly good number just because the user typed the unit too.
    if prefix_char.lower() in ("v", "a", "w", "s", "h", "f", "o"):
        return value
    raise ValueError(f"Unrecognized unit prefix: {suffix!r}")


def _pick_prefix(value: float) -> tuple[str, float]:
    """(prefix_letter, scale) for the largest prefix `value` still fits
    under — shared by format_engineering and format_engineering_compact
    so the two can never disagree on which prefix to pick."""
    if value == 0:
        return "", 1.0
    av = abs(value)
    for prefix, scale in _FORMAT_PREFIXES:
        if av >= scale:
            return prefix, scale
    return _FORMAT_PREFIXES[-1]   # smaller than the smallest prefix (p) -- use p anyway


def format_engineering(value, unit: str, decimals: int = 3) -> str:
    """0.005 -> "5.000 mV" (unit="V"), 4.3e-7 -> "430.000 nA" (unit="A").
    None -> "--" (matches the existing "not yet measured" convention)."""
    if value is None:
        return "--"
    prefix, scale = _pick_prefix(value)
    return f"{value / scale:.{decimals}f} {prefix}{unit}"


def format_engineering_compact(value, decimals: int = 3) -> str:
    """Same prefix selection as format_engineering but no unit letter and
    no space — "5.000m" not "5.000 mV". For re-populating an editable
    Entry (Recipe step editor, see recipe_panel.py's _step_to_editor)
    where the unit is already shown separately by an adjacent hint
    label, so baking it into the editable text would be redundant and
    would force re-parsing a unit string just to tweak the number.
    Round-trips through parse_engineering (which ignores a bare/no
    trailing unit letter either way)."""
    if value is None or value == "":
        return ""
    value = float(value)
    prefix, scale = _pick_prefix(value)
    return f"{value / scale:.{decimals}f}{prefix}"
