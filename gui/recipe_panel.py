"""Recipe Panel — test recipe parameters + measurement steps.

A recipe = global parameters (prober sequence, die geometry, alignment,
measurement defaults) + an ordered list of MEASUREMENT STEPS. Each step
applies one action to a set of pins:

    type=resistance  — 2-wire Ω between HI and LO; always measure
    type=voltage     — mode=measure (read V) or mode=apply (force V)
    type=current     — mode=measure (read I) or mode=apply (force I)
    type=wave        — WGEN output on the HI pin (level = amplitude Vpp,
                       shape = SIN/SQU/RAMP/PULS/DC, freq = Hz); LO pin
                       lands on the SMU A LO/GND bus as the return
    type=delay       — wait; level = time in ms (no pins, no switching)
    type=open        — open the closures of a previous step (target = step
                       name or number) and reset that instrument's output if
                       it was driving (SMU apply / wave); target=all opens
                       every channel and resets all outputs
    type=passfail    — no switching; checks the reading from a prior
                       MEASUREMENT step (resistance, voltage/measure, or
                       current/measure — target = its step name/number, or
                       blank for the most recent one) against min/max
                       (either may be blank for a one-sided/unbounded
                       check). Drives the wafer map's die color (green =
                       pass, red = fail) and the Run tab's Pass/Fail
                       statistics for the current die.

Averaging (measurement steps only — resistance, voltage/measure,
current/measure): avg_count = number of readings to take (default 1,
i.e. off); avg_delay = wait between each reading in ms (default 0). The
Run tab takes avg_count readings back-to-back with avg_delay between
them, logs each one, and records/passfail-checks only their MEAN — never
the individual readings.

instrument — WHICH instrument performs the step, mirroring the Instruments
tab's DMM / SMU / Wave Gen cards (picked explicitly, not just inferred):
    resistance, voltage        → DMM or SMU
    current                    → SMU (apply always sources from the SMU —
                                  only it can force current); SMU or DMM
                                  when measuring
    wave                       → WGEN (fixed)
SMU steps also pick a channel: A → rows A/B, B → rows C/D. Wave steps pick
WGEN CH1 (row G) or CH2 (row H).

limit = output-protection value, meaning depends on what's being sourced
(shown next to the field):
    SMU sourcing voltage (voltage/apply)         → current compliance (A)
    SMU sourcing current (current/apply)         → voltage compliance (V)
    SMU biasing while measuring (current/measure)→ current compliance (A)
    WGEN (wave)                                  → output voltage clamp (V)
Sent via set_current_limit()/set_voltage_limit()/set_voltage_limit_ch()
before the output turns on. The two CURRENT-compliance cases (voltage/
apply and current/measure-while-biasing — anywhere an SMU output turns on
with Limit acting as a current, not voltage, clamp) default to 0.000001 A
(1 µA) whenever left blank, rather than the output going out uncompliant
— see _DEFAULT_SMU_CURRENT_LIMIT / _limit_is_current_compliance. The
voltage-compliance case (current/apply) and the WGEN clamp have no such
default; blank there really means "don't set one."

HI/LO pins are picked from Pad Layout ▸ Probe Card Wiring (one pin each,
stored as "<pin>:<pad>" so the pin number stays visible, e.g. "1:P1").
From the step + wiring, the panel computes the 707B switch-matrix closures —
AT MOST TWO per step: one instrument row onto the HI pin, one onto the LO
pin (rows: A=SMU A HI, B=SMU A LO, E=DMM LO, F=DMM HI; pins 1–12 → slot 2
columns, 13–24 → slot 4), chosen by the step's Instrument (+ channel). The
closures are STORED on the step (conn=…) when it is added and can be edited
per step if the auto-routing isn't what the fixture needs. The closure
report shows under the steps table and is mirrored on the Switch Debug tab.

The Recipe tab shows the steps. A recipe has no separate "parameters" any
more (no Prober Sequence / Die Geometry / Alignment / Measurement Defaults
form) — it is just a name + an ordered list of steps.

ONE PROBE CARD = ONE .csv FILE, holding BOTH that card's pin wiring AND
ALL of its recipes (see ProbeCardWiringFrame in wafer_map_view.py, Pad to
Probe tab — ATA folder/probe_cards/<Card>.csv). ProbeCardWiringFrame owns
the physical file; this module only knows how to turn a
{name: {"steps": [...]}} dict into/from the file's STEP rows
(kind=STEP, scoped by a "recipe" column) via recipes_to_rows() /
rows_to_recipes() — PIN rows are wafer_map_view's concern and pass straight
through untouched.

RecipePanel never reads/writes that file directly. MainLayout pushes the
active probe card's recipes in via load_recipes(card, recipes) whenever the
active card changes (ATA load, picker switch, ＋New/🗑 Delete/✎ Rename), and
RecipePanel pushes edits back out via the injected save_recipes(card,
recipes) callable — which is ProbeCardWiringFrame.save_recipes(), a single
rewrite of that one card's file (pins + all its recipes together). A
recipe belongs to exactly one probe card; there is no folder-wide or
ATA-root fallback, and Save/＋New/🗑 Delete/📂 Load .ini all operate on the
currently active card only (an error is shown if none is selected).

📂 Load .ini… still accepts the old flat single-recipe .ini format (see
parse_recipe_file/write_recipe_file below) as a convenient way to import a
hand-authored recipe — it's registered into the active card's in-memory
recipe set and saved on next persist, same as ＋New.
"""
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from pma_wafer_panel import (read_main_menu_info as _pma_read_main_menu_info,
                             read_moves_grid as _pma_read_moves_grid)
from engineering_units import parse_engineering, format_engineering_compact
try:
    import xlrd as _pma_xlrd
except ImportError:
    _pma_xlrd = None


_STEP_TYPES    = ("resistance", "voltage", "current", "wave", "passfail", "delay", "open",
                  "picture")
_STEP_MODES    = ("measure", "apply")
_INSTRUMENTS   = ("DMM", "SMU", "WGEN")
_SMU_CHANNELS  = ("A", "B")
_WGEN_CHANNELS = ("CH1", "CH2")
_WAVE_SHAPES   = ("SIN", "SQU", "RAMP", "PULS", "DC")
_STEP_FIELDS   = ("name", "type", "mode", "instrument", "chan", "target", "hi", "lo",
                  "level", "limit", "shape", "freq", "conn", "min", "max",
                  "avg_count", "avg_delay")

# Public alias — wafer_map_view.py (ProbeCardWiringFrame) needs this to build
# the combined probe-card CSV's column list; see recipes_to_rows/rows_to_recipes.
STEP_FIELDS = _STEP_FIELDS


def _normalize_numeric_field(text: str) -> str:
    """Leave a plain (no-prefix) numeric string byte-for-byte unchanged —
    matches float()'s behavior and every pre-existing recipe exactly, so
    a step nobody touched keeps reading "2500", not "2500.0". Only
    reformat when a unit prefix was actually used ("5m"), since a
    prefixed value has no way to survive verbatim and still be
    consumable by the run engine's bare float() calls
    (_exec2_run_steps_once). Raises ValueError on anything unparsable,
    same as plain float() always did."""
    try:
        float(text)
        return text
    except ValueError:
        pass
    return repr(parse_engineering(text))


def _is_measurement_step(step: dict) -> bool:
    """True for steps that produce a stored reading (record_result()) — the
    only valid targets for a passfail step's threshold check."""
    t = step.get("type")
    if t == "resistance":
        return True
    if t in ("voltage", "current"):
        return step.get("mode") == "measure"
    return False


def _instrument_options(step_type: str, mode: str) -> tuple:
    """Instruments allowed to perform this step — mirrors the Instruments
    tab's DMM / SMU / Wave Gen cards. resistance can use either meter;
    voltage/measure and current/measure can read from either; apply (either
    voltage or current) must source from the SMU — the DMM has no sourcing
    capability in this app, only measurement. wave is WGEN-only."""
    if step_type == "resistance":
        return ("DMM", "SMU")
    if step_type in ("voltage", "current"):
        return ("SMU",) if mode == "apply" else ("SMU", "DMM")
    if step_type == "wave":
        return ("WGEN",)
    return ()


def _default_instrument(step_type: str, mode: str) -> str:
    """Instrument a step gets when none is picked / the stored one is no
    longer valid for its type+mode — preserves the pre-Instrument-field
    defaults (resistance & voltage/measure → DMM, everything else → SMU)."""
    if step_type == "wave":
        return "WGEN"
    if step_type == "resistance":
        return "DMM"
    if step_type == "voltage":
        return "SMU" if mode == "apply" else "DMM"
    if step_type == "current":
        return "SMU"
    return ""


def _limit_applicable(step_type: str, mode: str, instrument: str) -> bool:
    """True when Limit (a current OR voltage compliance, depending on what's
    being sourced) is meaningful for this step."""
    if step_type == "wave":
        return True
    if instrument != "SMU":
        return False
    return step_type == "current" or (step_type == "voltage" and mode == "apply")


# Safety default: any step that turns an SMU output ON with Limit acting as
# a CURRENT compliance (as opposed to a voltage compliance/clamp) gets this
# value automatically when the user leaves Limit blank, rather than the SMU
# output going out uncompliant. See _limit_is_current_compliance.
_DEFAULT_SMU_CURRENT_LIMIT = "0.000001"


def _limit_is_current_compliance(step_type: str, mode: str, instrument: str) -> bool:
    """True for the two cases where Limit is a CURRENT value (amps): forcing
    voltage (voltage/apply — limits how much current the SMU will source to
    hit that voltage) and measuring current while biasing a voltage
    (current/measure via SMU — limits the bias's current draw). Forcing
    current (current/apply) uses a VOLTAGE compliance instead — not this."""
    if not _limit_applicable(step_type, mode, instrument):
        return False
    if step_type == "voltage":
        return True
    return step_type == "current" and mode != "apply"


def _limit_hint(step_type: str, mode: str, instrument: str) -> str:
    if step_type == "wave":
        return "V (output clamp, ±) · m/µ/n/k ok"
    if not _limit_applicable(step_type, mode, instrument):
        return "— (n/a)"
    if step_type == "voltage":                       # apply, SMU sources V
        return "A (current compliance) · m/µ/n/k ok"
    if step_type == "current" and mode == "apply":    # SMU sources I
        return "V (voltage compliance) · m/µ/n/k ok"
    return "A (current compliance, if biasing) · m/µ/n/k ok"   # current/measure


def _level_hint(step_type: str, mode: str) -> str:
    if step_type == "delay":
        return "ms (wait time)"
    if step_type == "resistance":
        return "— (2-wire Ω)"
    if step_type == "wave":
        return "Vpp (WGEN amplitude) · m/µ/n/k ok"
    if step_type == "open":
        return "— (no level)"
    if step_type == "picture":
        return "— (not yet implemented)"
    if step_type == "voltage":
        return "V (forced) · m/µ/n/k ok" if mode == "apply" else "— (reads V)"
    if step_type == "current":
        return "A (forced) · m/µ/n/k ok" if mode == "apply" else "V (bias while reading I) · m/µ/n/k ok"
    if step_type == "passfail":
        return "— (see Min/Max)"
    return ""


def _passfail_hint() -> str:
    return ("value must be Min ≤ x ≤ Max (leave either blank for one-sided / "
           "unbounded) · m/µ/n/k ok")


def _avg_hint() -> str:
    return "take N readings (delay between each), record their mean — Count=1 is off"


def _avg_display(step: dict) -> str:
    """Compact "3×100ms" summary for the steps table; blank when averaging
    is off (Count ≤ 1) or not applicable to this step."""
    try:
        n = int(step.get("avg_count") or 1)
    except ValueError:
        n = 1
    if n <= 1:
        return ""
    return f"{n}×{step.get('avg_delay') or 0}ms"


# ── 707B switch-matrix routing ────────────────────────────────────────────────
# Physical wiring (see probe_routing_panel): matrix rows A–H carry the
# instrument buses, probe-card pins 1–12 land on slot 2 columns 1–12 and
# pins 13–24 on slot 4 columns 1–12. Channel strings are e.g. "2A06".
_ROW_LABELS = {"A": "SMU A HI", "B": "SMU A LO/GND", "C": "SMU B HI",
               "D": "SMU B LO/GND", "E": "DMM LO", "F": "DMM HI",
               "G": "WGEN CH1", "H": "WGEN CH2"}


def _rows_for(step_type: str, chan: str, instrument: str):
    """(rows for the HI pin, rows for the LO pin) — one row each, so a step
    closes at most two crosspoints. Routed by the step's chosen Instrument:
    DMM → F/E, SMU chan A → A/B, SMU chan B → C/D. Wave steps drive the HI
    pin from WGEN CH1 (row G) or CH2 (row H) with the LO pin landing on row B
    (the SMU A LO/GND bus) as the return.
    """
    if step_type == "wave":
        return (("H",) if chan == "CH2" else ("G",)), ("B",)
    if instrument == "DMM":
        return ("F",), ("E",)
    if instrument == "SMU":
        return (("C",), ("D",)) if chan == "B" else (("A",), ("B",))
    return (), ()


def _pin_channel(pin_no: int, row: str) -> str:
    """707B channel string for probe pin × instrument row, e.g. pin 14 row F → '4F02'."""
    slot, col = ("2", pin_no) if pin_no <= 12 else ("4", pin_no - 12)
    return f"{slot}{row}{col:02d}"


def _serialize_step(step: dict) -> str:
    return " | ".join(f"{k}={step.get(k, '')}" for k in _STEP_FIELDS)


def _normalize_step(step: dict) -> dict:
    """Clear or force the fields that don't apply to the step's type, and
    pick a valid Instrument for the type+mode (falls back to
    _default_instrument when missing/invalid — e.g. an older recipe file
    saved before the Instrument field existed)."""
    t = step["type"]
    if t == "delay":
        step["mode"] = step["chan"] = step["target"] = step["instrument"] = ""
        step["hi"] = step["lo"] = step["conn"] = ""
        step["limit"] = step["shape"] = step["freq"] = ""
        step["min"] = step["max"] = ""
        step["avg_count"] = step["avg_delay"] = ""
        return step
    if t == "open":
        step["mode"] = step["chan"] = step["instrument"] = ""
        step["hi"] = step["lo"] = step["level"] = ""
        step["limit"] = step["shape"] = step["freq"] = ""
        step["min"] = step["max"] = ""
        step["avg_count"] = step["avg_delay"] = ""
        return step
    if t == "passfail":
        step["mode"] = step["chan"] = step["instrument"] = ""
        step["hi"] = step["lo"] = step["conn"] = ""
        step["level"] = step["limit"] = step["shape"] = step["freq"] = ""
        step["avg_count"] = step["avg_delay"] = ""
        return step
    if t == "picture":
        # Placeholder step type — no fields, no switching, no execution
        # behavior yet (see the Run tab's exec loop). Reserved for a future
        # camera-capture integration.
        step["mode"] = step["chan"] = step["target"] = step["instrument"] = ""
        step["hi"] = step["lo"] = step["conn"] = step["level"] = ""
        step["limit"] = step["shape"] = step["freq"] = ""
        step["min"] = step["max"] = ""
        step["avg_count"] = step["avg_delay"] = ""
        return step

    step["target"] = ""
    step["min"] = step["max"] = ""
    if t == "resistance":
        step["mode"] = "measure"
    elif t == "wave":
        step["mode"] = "apply"
    elif step["mode"] not in _STEP_MODES:
        step["mode"] = "measure"

    options = _instrument_options(t, step["mode"])
    if step["instrument"] not in options:
        step["instrument"] = _default_instrument(t, step["mode"])
    instrument = step["instrument"]

    if t == "wave":
        if step["shape"] not in _WAVE_SHAPES:
            step["shape"] = "SIN"
        if not step["freq"]:
            step["freq"] = "1000"
        if step["chan"] not in _WGEN_CHANNELS:
            step["chan"] = "CH1"
    else:
        step["shape"] = step["freq"] = ""
        if instrument == "SMU":
            if step["chan"] not in _SMU_CHANNELS:
                step["chan"] = "A"
        else:
            step["chan"] = ""

    if not _limit_applicable(t, step["mode"], instrument):
        step["limit"] = ""
    elif (_limit_is_current_compliance(t, step["mode"], instrument)
          and not (step.get("limit") or "").strip()):
        step["limit"] = _DEFAULT_SMU_CURRENT_LIMIT

    if _is_measurement_step(step):
        if not (step.get("avg_count") or "").strip():
            step["avg_count"] = "1"
        if not (step.get("avg_delay") or "").strip():
            step["avg_delay"] = "0"
    else:
        step["avg_count"] = step["avg_delay"] = ""
    return step


def _parse_step(text: str) -> dict:
    step = {k: "" for k in _STEP_FIELDS}
    for part in text.split("|"):
        key, _, val = part.partition("=")
        key = key.strip().lower()
        if key in step:
            step[key] = val.strip()
    if step["type"] not in _STEP_TYPES:
        step["type"] = "resistance"
    return _normalize_step(step)


def _safe_filename(name: str) -> str:
    """Sanitize a recipe name into a filesystem-safe file stem."""
    return "".join(c for c in name.strip() if c.isalnum() or c in " _-").strip() or "recipe"


def parse_recipe_file(path: str) -> dict:
    """Parse a recipe .ini — ALWAYS exactly one recipe, named after the file
    (stem, no extension). Any [Section] or non-Step key=value lines from an
    older file (back when recipes carried a parameter form) are ignored —
    only StepN= lines are read.

    Returns {stem: {"steps": [...]}}.
    """
    name = os.path.splitext(os.path.basename(path))[0]
    step_items = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(("#", ";", "[")):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip()
                if key.lower().startswith("step") and key[4:].isdigit():
                    step_items.append((int(key[4:]), val))
    steps = [_parse_step(val) for _n, val in sorted(step_items)]
    return {name: {"steps": steps}}


def write_recipe_file(path: str, recipe: dict):
    """Write ONE recipe {"steps": [...]} as a flat .ini (StepN= lines only).
    The recipe's name is the file name — no [section] header is written."""
    lines = [f"# ATA recipe — {os.path.splitext(os.path.basename(path))[0]}", ""]
    steps = recipe.get("steps", [])
    for i, step in enumerate(steps, 1):
        lines.append(f"Step{i}={_serialize_step(step)}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ── Legacy .pma/.PMS import (📥 Import Legacy Recipe) ─────────────────────
# The OLD LabVIEW-era recipe format was a flat key=value file mixing prober
# sequence / die geometry / alignment (CountMovesMajor, DeviceIDMajor,
# MovesMajor, CountMovesMinor, DeviceIDMinor, MovesMinor, DieSizeX, DieSizeY,
# XMoveFirstFromAlignSite, YMoveFirstFromAlignSite, PreAlignMessage,
# PostAlignMessage, PictureFile — none of that is used by this app, same as
# the params form removed earlier) with measurement defaults this app CAN
# still act on. _PMA_MAPPED_KEYS translate directly onto step fields;
# _PMA_UNMAPPED_KEYS are extracted (surfaced in the import log) but have no
# equivalent field — set them directly on the instrument if still needed.
_PMA_MAPPED_KEYS   = {"Voltage", "MeterCurrentLimit", "Averages", "MeterDelay",
                      "Delay1", "Delay2", "Delay3"}
_PMA_UNMAPPED_KEYS = {"NPLC", "MeterRange", "Iterations"}
_PMA_USEFUL_KEYS   = _PMA_MAPPED_KEYS | _PMA_UNMAPPED_KEYS


def parse_pma_params(path: str) -> dict:
    """Read a legacy flat key=value recipe file and return ONLY the
    recognized measurement-relevant keys (_PMA_USEFUL_KEYS), as strings.
    Everything else (moves, die size, alignment messages, picture file,
    unrecognized keys) is silently ignored."""
    useful = {}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(("#", ";", "[")) or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if key in _PMA_USEFUL_KEYS and val:
                useful[key] = val
    return useful


def _pma_blank_step() -> dict:
    return {k: "" for k in _STEP_FIELDS}


def _pma_num(params: dict, key: str, default: str = "0") -> str:
    """The raw string value for `key` if it's a valid number, else default
    — preserves the file's own formatting rather than reformatting floats."""
    val = (params.get(key) or "").strip()
    if not val:
        return default
    try:
        float(val)
    except ValueError:
        return default
    return val


def pma_params_to_steps(params: dict) -> list:
    """Best-effort translation of a legacy file's measurement defaults into
    an executable IDDQ-style step sequence, with the file's three delays
    placed BETWEEN steps rather than all bunched up front:

        Delay1 (settle)  ->  apply (force Voltage)  ->  Delay2 (settle)
        ->  measure current (Averages/MeterDelay -> avg_count/avg_delay)
        ->  passfail against MeterCurrentLimit  ->  open (release)
        ->  Delay3 (settle)

    apply and measure are separate steps (not fused into one) so Delay2
    can sit between them, matching the file's own Delay1/Delay2/Delay3
    ordering. Each of Delay1/2/3 defaults to 100ms whenever the source
    file doesn't mention it at all (no bare/unguarded gap between steps);
    an explicit 0 in the file still means "no delay there" and is left
    out. HI/LO pins can't be inferred from the file — left blank for the
    user to fill in on BOTH the apply and measure steps, same as any
    freshly hand-created step."""
    steps = []

    d1 = _pma_num(params, "Delay1", "100")
    if float(d1) > 0:
        steps.append(_normalize_step({**_pma_blank_step(), "type": "delay",
                                      "name": "Settle before bias (Delay1)",
                                      "level": d1}))

    voltage = (params.get("Voltage") or "").strip()
    limit   = (params.get("MeterCurrentLimit") or "").strip()
    apply_name = "Bias Voltage"
    steps.append(_normalize_step({
        **_pma_blank_step(), "type": "voltage", "mode": "apply",
        "instrument": "SMU", "chan": "A", "name": apply_name,
        "level": voltage, "limit": limit,
    }))

    d2 = _pma_num(params, "Delay2", "100")
    if float(d2) > 0:
        steps.append(_normalize_step({**_pma_blank_step(), "type": "delay",
                                      "name": "Settle between bias and measure (Delay2)",
                                      "level": d2}))

    avg_count = _pma_num(params, "Averages", "1")
    meter_delay_s = (params.get("MeterDelay") or "").strip()
    avg_delay_ms = "0"
    if meter_delay_s:
        try:
            ms = float(meter_delay_s) * 1000
            avg_delay_ms = str(int(ms)) if ms.is_integer() else str(ms)
        except ValueError:
            pass

    meas_name = "Leakage Measurement"
    steps.append(_normalize_step({
        **_pma_blank_step(), "type": "current", "mode": "measure",
        "instrument": "SMU", "chan": "A", "name": meas_name,
        "avg_count": avg_count, "avg_delay": avg_delay_ms,
    }))

    if limit:
        steps.append(_normalize_step({
            **_pma_blank_step(), "type": "passfail", "name": "Leakage Check",
            "target": meas_name, "max": limit}))

    steps.append(_normalize_step({
        **_pma_blank_step(), "type": "open", "name": "Release", "target": apply_name}))

    d3 = _pma_num(params, "Delay3", "100")
    if float(d3) > 0:
        steps.append(_normalize_step({**_pma_blank_step(), "type": "delay",
                                      "name": "Settle after release (Delay3)",
                                      "level": d3}))
    return steps


def repeat_steps_per_die(steps: list, dies_per_shot: int) -> list:
    """A probe card that co-touches multiple dies in one shot (see the PMA
    tab's wafer/shot map — a MajorMoves cell like "13-12/NA/13-13/13-03"
    covers up to 4 dies per touchdown) needs the SAME measurement sequence
    run once per die, each routed to a different die's pins via the switch
    matrix. dies_per_shot <= 1 returns `steps` unchanged; otherwise the
    whole sequence is duplicated dies_per_shot times, with each repetition's
    step names suffixed " (Die N)" (and any `target` reference to another
    step's name in the same repetition renamed to match) so the user can
    tell the copies apart and assign each one's HI/LO pins separately."""
    if dies_per_shot <= 1:
        return steps
    names_in_block = {s["name"] for s in steps if s.get("name")}
    out = []
    for i in range(1, dies_per_shot + 1):
        suffix = f" (Die {i})"
        for s in steps:
            s2 = dict(s)
            if s2.get("name"):
                s2["name"] = s2["name"] + suffix
            if s2.get("target") in names_in_block:
                s2["target"] = s2["target"] + suffix
            out.append(s2)
    return out


def recipes_to_rows(recipes: dict) -> list:
    """Flatten {name: {"steps": [...]}} into CSV row-dicts for a probe
    card's combined .csv: one kind=RECIPE existence-marker row per recipe
    (so an empty, just-created recipe still survives a save/reload round
    trip — it would otherwise leave zero rows and vanish) plus kind=STEP
    rows for its steps (scoped by the "recipe" column, ordered by "seq").
    PIN rows are not this module's concern — ProbeCardWiringFrame adds
    those separately."""
    rows = []
    for name, rec in recipes.items():
        rows.append({"kind": "RECIPE", "recipe": name})
        for i, step in enumerate(rec.get("steps", []), 1):
            row = {"kind": "STEP", "recipe": name, "seq": str(i)}
            for k in _STEP_FIELDS:
                row[k] = step.get(k, "")
            rows.append(row)
    return rows


def rows_to_recipes(rows: list) -> dict:
    """Inverse of recipes_to_rows — group RECIPE/STEP rows (as read from a
    probe card's combined .csv) back into {name: {"steps": [...]}}, in the
    order recipe names first appear, steps ordered by their "seq" column
    (falling back to file order if seq is missing/non-numeric). Non-RECIPE/
    STEP rows (e.g. PIN rows) are ignored — callers should pre-filter, but
    it's harmless either way since only those two kinds are read here."""
    recipes: dict = {}
    step_rows: dict = {}
    for row in rows:
        kind = (row.get("kind") or "").strip().upper()
        if kind not in ("RECIPE", "STEP"):
            continue
        name = (row.get("recipe") or "").strip()
        if not name:
            continue
        recipes.setdefault(name, {"steps": []})
        if kind == "RECIPE":
            continue
        try:
            seq = int(row.get("seq") or 0)
        except ValueError:
            seq = 0
        step = {k: row.get(k, "") for k in _STEP_FIELDS}
        if step.get("type") not in _STEP_TYPES:
            step["type"] = "resistance"
        step_rows.setdefault(name, []).append((seq, step))
    for name, items in step_rows.items():
        items.sort(key=lambda t: t[0])
        recipes[name]["steps"] = [_normalize_step(s) for _seq, s in items]
    return recipes


class RecipePanel(ttk.Frame):
    def __init__(self, parent, controller, get_pins=None, get_wiring=None,
                 get_active_card=None, save_recipes=None):
        super().__init__(parent)
        self.controller = controller
        # Callable returning [(value, label), …] of available probe-card pins
        # (Pad Layout ▸ Probe Card Wiring) for the step pin pickers.
        self._get_pins = get_pins or (lambda: [])
        # Callable returning the full wiring rows [{pin, pad, net}] of the
        # ACTIVE probe card — used to resolve step pins → matrix columns
        # for switch computation.
        self._get_wiring = get_wiring or (lambda: [])
        # Callable returning the ACTIVE probe card's name ("" = none) —
        # ProbeCardWiringFrame.get_active_card. Shown in the toolbar so the
        # tab always says which card's recipes it's looking under.
        self._get_active_card = get_active_card or (lambda: "")
        # Callable(card, recipes_dict) -> bool that persists this panel's
        # ENTIRE recipe set for `card` — ProbeCardWiringFrame.save_recipes(),
        # a single rewrite of that card's one .csv (pins + all its recipes).
        self._save_recipes = save_recipes or (lambda _card, _recipes: False)
        # Closure-report viewer (registered by the Switch Debug tab)
        self._conn_viewer = None
        self._conn_report = "— no steps —"

        # Multi-recipe store for the ACTIVE probe card: name → {"steps": [...]}.
        # The startup placeholder exists so the UI isn't empty before any
        # ATA folder / probe card is loaded.
        self._recipes: dict = {"(unsaved)": {"steps": []}}
        self._current: str = "(unsaved)"
        # Name of the probe card these recipes belong to ("" = none active
        # yet — set by load_recipes(), called whenever the active card
        # changes: ATA load, picker switch, ＋New/🗑 Delete/✎ Rename).
        self._active_card: str = ""

        # Active recipe's steps (list of dicts, mirrored in the treeview)
        self._steps: list[dict] = self._recipes[self._current]["steps"]

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_body()
        self._refresh_picker()
        self._update_connections()
        self._update_validity_label()

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self):
        bar = tk.Frame(self, bg="#e2e8f0", relief="flat", bd=1)
        bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 0))

        tk.Label(bar, text="Recipe:", bg="#e2e8f0",
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(8, 2), pady=4)
        self._picker_var = tk.StringVar(value=self._current)
        self._picker = ttk.Combobox(bar, textvariable=self._picker_var,
                                    state="readonly", width=26)
        self._picker.pack(side="left", padx=(0, 8), pady=4)
        self._picker.bind("<<ComboboxSelected>>", lambda _e: self._switch_recipe())

        # Cached validate_recipe() verdict for whichever recipe is active —
        # see validate_all_recipes/_update_validity_label. Green/red so a
        # recipe's readiness is visible at a glance, including right after
        # switching to it (no need to hit ✓ Validate by hand every time).
        self._validity_lbl = tk.Label(bar, text="", bg="#e2e8f0",
                                      font=("Segoe UI", 9, "bold"))
        self._validity_lbl.pack(side="left", padx=(0, 8), pady=4)

        self._btn_new = ttk.Button(bar, text="＋ New", width=7,
                                   command=self._new_recipe)
        self._btn_new.pack(side="left", padx=2, pady=4)
        self._btn_delete = ttk.Button(bar, text="🗑 Delete", width=9,
                                      command=self._delete_recipe)
        self._btn_delete.pack(side="left", padx=2, pady=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=6, pady=4)

        self._btn_load_ini = ttk.Button(bar, text="📂  Load .ini…", command=self._load)
        self._btn_load_ini.pack(side="left", padx=2, pady=4)
        self._btn_import_legacy = ttk.Button(bar, text="📥  Import Legacy (.pma)…",
                                             command=self._import_legacy)
        self._btn_import_legacy.pack(side="left", padx=2, pady=4)
        self._btn_import_workbook = ttk.Button(
            bar, text="📥  Import Legacy Workbook (.xls)…",
            command=self._import_legacy_workbook)
        self._btn_import_workbook.pack(side="left", padx=2, pady=4)
        self._btn_save = ttk.Button(bar, text="💾  Save", command=self._save)
        self._btn_save.pack(side="left", padx=2, pady=4)

        # Shown while a run is in progress — see set_locked().
        self._locked_lbl = tk.Label(bar, text="", bg="#e2e8f0", fg="#b45309",
                                    font=("Segoe UI", 8, "italic"))
        self._locked_lbl.pack(side="left", padx=(4, 8))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=6, pady=4)

        # Always-visible "which probe card am I editing" indicator.
        self._card_lbl = tk.Label(bar, text="Probe Card: (none)",
                                  bg="#e2e8f0", fg="#1e3a5f",
                                  font=("Segoe UI", 9, "bold"), anchor="w")
        self._card_lbl.pack(side="left", padx=(4, 8))

        self._file_lbl = tk.Label(bar, text="No probe card selected",
                                  bg="#e2e8f0", fg="#6b7280",
                                  font=("Segoe UI", 8), anchor="w")
        self._file_lbl.pack(side="left", padx=8)

    # ── Body: measurement steps ────────────────────────────────────────────

    def _build_body(self):
        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self._build_steps(body)

    # ── Measurement steps ─────────────────────────────────────────────────────

    def _build_steps(self, parent):
        sf = ttk.LabelFrame(parent, text="Measurement Steps (per shot)",
                            padding=6)
        sf.grid(row=0, column=0, sticky="nsew")
        sf.rowconfigure(1, weight=1)
        sf.columnconfigure(0, weight=1)

        ttk.Label(sf,
                  text="Don't edit",
                  foreground="gray", font=("Arial", 8), justify="left", wraplength=760).grid(
                  row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        cols = ("n", "name", "type", "instrument", "mode", "chan", "target",
                "hi", "lo", "level", "limit", "avg", "min", "max", "shape", "freq", "conn")
        self._step_tree = ttk.Treeview(sf, columns=cols, show="headings",
                                       height=5, selectmode="browse")
        heads = [("n", "#", 28), ("name", "Name", 90), ("type", "Type", 75),
                 ("instrument", "Instr", 50), ("mode", "Mode", 55), ("chan", "Chan", 40),
                 ("target", "Target", 62),
                 ("hi", "HI pin", 55), ("lo", "LO pin", 55),
                 ("level", "Level", 52), ("limit", "Limit", 50),
                 ("avg", "Avg", 68),
                 ("min", "Min", 46), ("max", "Max", 46),
                 ("shape", "Shape", 48), ("freq", "Freq(Hz)", 58),
                 ("conn", "Switch conn", 110)]
        for cid, text, width in heads:
            self._step_tree.heading(cid, text=text)
            self._step_tree.column(
                cid, width=width,
                anchor="center" if cid in ("n", "type", "instrument", "mode", "chan",
                                           "shape") else "w")
        self._step_tree.grid(row=1, column=0, sticky="nsew")
        ssb = ttk.Scrollbar(sf, orient="vertical", command=self._step_tree.yview)
        ssb.grid(row=1, column=1, sticky="ns")
        self._step_tree.configure(yscrollcommand=ssb.set)
        self._step_tree.bind("<<TreeviewSelect>>", lambda _e: self._step_to_editor())

        # Editor (four rows)
        ed1 = ttk.Frame(sf)
        ed1.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ed2 = ttk.Frame(sf)
        ed2.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        ed3 = ttk.Frame(sf)
        ed3.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        ed4 = ttk.Frame(sf)
        ed4.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(2, 0))

        self._ed_vars = {k: tk.StringVar() for k in _STEP_FIELDS}
        self._ed_vars["type"].set("resistance")
        self._ed_vars["mode"].set("measure")

        def _lbl(parent, text):
            ttk.Label(parent, text=text).pack(side="left", padx=(6, 1))

        # Row 1: identity + instrument selection
        _lbl(ed1, "Name:")
        ttk.Entry(ed1, textvariable=self._ed_vars["name"], width=12).pack(side="left")
        _lbl(ed1, "Type:")
        type_cb = ttk.Combobox(ed1, textvariable=self._ed_vars["type"],
                               values=_STEP_TYPES, state="readonly", width=10)
        type_cb.pack(side="left")
        type_cb.bind("<<ComboboxSelected>>", lambda _e: self._on_type_change())
        _lbl(ed1, "Mode:")
        self._mode_cb = ttk.Combobox(ed1, textvariable=self._ed_vars["mode"],
                                     values=_STEP_MODES, state="readonly", width=8)
        self._mode_cb.pack(side="left")
        self._mode_cb.bind("<<ComboboxSelected>>", lambda _e: self._on_type_change())
        _lbl(ed1, "Instr:")
        self._instr_cb = ttk.Combobox(ed1, textvariable=self._ed_vars["instrument"],
                                      values=_INSTRUMENTS, state="readonly", width=6)
        self._instr_cb.pack(side="left")
        self._instr_cb.bind("<<ComboboxSelected>>", lambda _e: self._on_type_change())
        _lbl(ed1, "Chan:")
        self._chan_cb = ttk.Combobox(ed1, textvariable=self._ed_vars["chan"],
                                     values=_SMU_CHANNELS, state="readonly", width=5)
        self._chan_cb.pack(side="left")
        _lbl(ed1, "Target:")
        self._target_cb = ttk.Combobox(ed1, textvariable=self._ed_vars["target"],
                                       values=("all",), width=13,
                                       postcommand=self._refresh_target_values)
        self._target_cb.pack(side="left")

        # Row 2: pins + level + stored closures. HI/LO are plain dropdowns
        # listing the probe card wiring pins (typing is still allowed).
        _lbl(ed2, "HI:")
        self._hi_cb = ttk.Combobox(ed2, textvariable=self._ed_vars["hi"], width=10,
                                   postcommand=lambda: self._refresh_pin_values(self._hi_cb))
        self._hi_cb.pack(side="left")
        _lbl(ed2, "LO:")
        self._lo_cb = ttk.Combobox(ed2, textvariable=self._ed_vars["lo"], width=10,
                                   postcommand=lambda: self._refresh_pin_values(self._lo_cb))
        self._lo_cb.pack(side="left")
        self._pin_widgets = [self._hi_cb, self._lo_cb]
        _lbl(ed2, "Level:")
        self._level_ent = ttk.Entry(ed2, textvariable=self._ed_vars["level"], width=8)
        self._level_ent.pack(side="left")
        self._level_hint = ttk.Label(ed2, text=_level_hint("resistance", "measure"),
                                     foreground="gray", font=("Arial", 8))
        self._level_hint.pack(side="left", padx=(2, 6))
        _lbl(ed2, "Conn:")
        conn_ent = ttk.Entry(ed2, textvariable=self._ed_vars["conn"], width=16)
        conn_ent.pack(side="left")
        conn_btn = ttk.Button(ed2, text="⚙", width=3, command=self._conn_from_editor)
        conn_btn.pack(side="left")
        self._conn_widgets = [conn_ent, conn_btn]

        # Row 3: output-protection limit (unit depends on instrument/type/mode
        # — see _limit_hint) + wave shape/freq
        _lbl(ed3, "Limit:")
        self._limit_ent = ttk.Entry(ed3, textvariable=self._ed_vars["limit"], width=9)
        self._limit_ent.pack(side="left")
        self._limit_hint_lbl = ttk.Label(ed3, text=_limit_hint("resistance", "measure", "DMM"),
                                         foreground="gray", font=("Arial", 8))
        self._limit_hint_lbl.pack(side="left", padx=(2, 10))
        _lbl(ed3, "Shape:")
        self._shape_cb = ttk.Combobox(ed3, textvariable=self._ed_vars["shape"],
                                      values=_WAVE_SHAPES, state="readonly", width=6)
        self._shape_cb.pack(side="left")
        _lbl(ed3, "Freq (Hz, k/M ok):")
        self._freq_ent = ttk.Entry(ed3, textvariable=self._ed_vars["freq"], width=9)
        self._freq_ent.pack(side="left")

        # Row 4: passfail spec — Target (row 1) + Min/Max bound the measurement
        # named by Target (or, if blank, the most recent measurement step)
        _lbl(ed4, "Min:")
        self._pf_min_ent = ttk.Entry(ed4, textvariable=self._ed_vars["min"], width=9)
        self._pf_min_ent.pack(side="left")
        _lbl(ed4, "Max:")
        self._pf_max_ent = ttk.Entry(ed4, textvariable=self._ed_vars["max"], width=9)
        self._pf_max_ent.pack(side="left")
        self._pf_hint_lbl = ttk.Label(ed4, text=_passfail_hint(),
                                      foreground="gray", font=("Arial", 8))
        self._pf_hint_lbl.pack(side="left", padx=(2, 6))

        # Row 5: averaging — measurement steps only (resistance, voltage/
        # measure, current/measure). Count=1 (default) is effectively off.
        ed5 = ttk.Frame(sf)
        ed5.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        _lbl(ed5, "Avg Count:")
        self._avg_count_ent = ttk.Entry(ed5, textvariable=self._ed_vars["avg_count"], width=5)
        self._avg_count_ent.pack(side="left")
        _lbl(ed5, "Avg Delay (ms):")
        self._avg_delay_ent = ttk.Entry(ed5, textvariable=self._ed_vars["avg_delay"], width=7)
        self._avg_delay_ent.pack(side="left")
        self._avg_hint_lbl = ttk.Label(ed5, text=_avg_hint(),
                                       foreground="gray", font=("Arial", 8))
        self._avg_hint_lbl.pack(side="left", padx=(6, 6))

        self._on_type_change()

        btns = ttk.Frame(sf)
        btns.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        self._btn_add_step = ttk.Button(btns, text="＋ Add Step", command=self._step_add)
        self._btn_add_step.pack(side="left", padx=2)
        self._btn_update_step = ttk.Button(btns, text="✎ Update Selected",
                                           command=self._step_update)
        self._btn_update_step.pack(side="left", padx=2)
        self._btn_remove_step = ttk.Button(btns, text="🗑 Remove", command=self._step_remove)
        self._btn_remove_step.pack(side="left", padx=2)
        self._btn_move_up = ttk.Button(btns, text="▲", width=3,
                                       command=lambda: self._step_move(-1))
        self._btn_move_up.pack(side="left", padx=(10, 2))
        self._btn_move_down = ttk.Button(btns, text="▼", width=3,
                                         command=lambda: self._step_move(+1))
        self._btn_move_down.pack(side="left", padx=2)
        # ✓ Validate is read-only (inspects, never mutates) so it stays
        # enabled even while a run is in progress — see set_locked().
        ttk.Button(btns, text="✓ Validate",
                   command=self._validate_clicked).pack(side="left", padx=(10, 2))
        self._btn_recompute = ttk.Button(btns, text="↻ Recompute connections",
                                         command=self._recompute_all)
        self._btn_recompute.pack(side="right", padx=2)

        # ── Computed switch connections ───────────────────────────────────
        cf = ttk.LabelFrame(
            sf, text="Switch Connections (stored per step; max 2 closes)", padding=4)
        cf.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        cf.columnconfigure(0, weight=1)
        ttk.Label(cf,
                  text="707B rows: A=SMU A HI  B=SMU A LO  E=DMM LO  F=DMM HI   •   "
                       "pins 1–12 → slot 2, 13–24 → slot 4 (e.g. pin 14 → 4_02)",
                  foreground="gray", font=("Arial", 8)).grid(row=0, column=0, sticky="w")
        self._conn_text = tk.Text(cf, height=4, font=("Consolas", 8),
                                  state="disabled", bg="#f8fafc", wrap="none")
        self._conn_text.grid(row=1, column=0, sticky="ew")
        csb = ttk.Scrollbar(cf, orient="vertical", command=self._conn_text.yview)
        csb.grid(row=1, column=1, sticky="ns")
        self._conn_text.configure(yscrollcommand=csb.set)

    def _update_level_hint(self):
        t = self._ed_vars["type"].get()
        mode = self._ed_vars["mode"].get()
        instrument = self._ed_vars["instrument"].get()
        self._level_hint.config(text=_level_hint(t, mode))
        self._limit_hint_lbl.config(text=_limit_hint(t, mode, instrument))

    def _refresh_pin_values(self, cb):
        """Fill a HI/LO dropdown from the probe card wiring just before it
        opens, so it always reflects the current wiring (values are the
        stored pin:name tokens)."""
        tokens = []
        for r in self._get_wiring():
            pin = (r.get("pin") or "").strip()
            pad = (r.get("pad") or "").strip()
            if pin:
                tokens.append(f"{pin}:{pad}" if pad else pin)
        if not tokens:
            tokens = [v for v, _label in self._get_pins()]
        cb.config(values=tokens)

    def _refresh_target_values(self):
        """Target options depend on what's being edited:
        open  → 'all' or any previous switching step (resistance/voltage/
                current/wave) — what to open/reset.
        passfail → any previous MEASUREMENT step (resistance, voltage/
                current in measure mode) — what reading to check."""
        if self._ed_vars["type"].get() == "passfail":
            names = [s.get("name", "") for s in self._steps
                     if _is_measurement_step(s) and s.get("name")]
        else:
            names = ["all"] + [s.get("name", "") for s in self._steps
                               if s.get("type") not in ("delay", "open", "passfail", "picture")
                               and s.get("name")]
        self._target_cb.config(values=names)

    def _on_type_change(self):
        """Enable/disable + repopulate fields to match Type, Mode, and
        Instrument (any of the three can trigger this — see their binds)."""
        t = self._ed_vars["type"].get()

        def _set(widgets, state):
            for w in widgets:
                w.config(state=state)

        _set(self._pin_widgets + self._conn_widgets + [self._level_ent], "normal")
        self._target_cb.config(state="disabled")
        self._limit_ent.config(state="disabled")
        self._shape_cb.config(state="disabled")
        self._freq_ent.config(state="disabled")
        self._instr_cb.config(state="disabled")
        self._chan_cb.config(state="disabled")
        self._pf_min_ent.config(state="disabled")
        self._pf_max_ent.config(state="disabled")
        self._avg_count_ent.config(state="disabled")
        self._avg_delay_ent.config(state="disabled")

        if t == "delay":
            self._ed_vars["mode"].set("")
            self._ed_vars["chan"].set("")
            self._ed_vars["instrument"].set("")
            self._mode_cb.config(state="disabled")
            _set(self._pin_widgets + self._conn_widgets, "disabled")
            self._update_level_hint()
            return
        if t == "picture":
            self._ed_vars["mode"].set("")
            self._ed_vars["chan"].set("")
            self._ed_vars["instrument"].set("")
            self._mode_cb.config(state="disabled")
            _set(self._pin_widgets + self._conn_widgets + [self._level_ent], "disabled")
            self._update_level_hint()
            return
        if t == "open":
            self._ed_vars["mode"].set("")
            self._ed_vars["chan"].set("")
            self._ed_vars["instrument"].set("")
            self._mode_cb.config(state="disabled")
            self._target_cb.config(state="normal")
            self._refresh_target_values()
            _set(self._pin_widgets + [self._level_ent], "disabled")
            self._update_level_hint()
            return
        if t == "passfail":
            self._ed_vars["mode"].set("")
            self._ed_vars["chan"].set("")
            self._ed_vars["instrument"].set("")
            self._mode_cb.config(state="disabled")
            self._target_cb.config(state="normal")
            self._refresh_target_values()
            _set(self._pin_widgets + self._conn_widgets + [self._level_ent], "disabled")
            self._pf_min_ent.config(state="normal")
            self._pf_max_ent.config(state="normal")
            self._update_level_hint()
            return

        if t == "resistance":
            self._ed_vars["mode"].set("measure")
            self._mode_cb.config(state="disabled")
        elif t == "wave":
            self._ed_vars["mode"].set("apply")
            self._mode_cb.config(state="disabled")
        else:  # voltage / current
            if self._ed_vars["mode"].get() not in _STEP_MODES:
                self._ed_vars["mode"].set("measure")
            self._mode_cb.config(state="readonly")
        mode = self._ed_vars["mode"].get()

        # Instrument — options depend on type+mode (mirrors the Instruments tab)
        options = _instrument_options(t, mode)
        if t == "wave":
            self._ed_vars["instrument"].set("WGEN")   # fixed, shown but locked
        else:
            self._instr_cb.config(state="readonly", values=options)
            if self._ed_vars["instrument"].get() not in options:
                self._ed_vars["instrument"].set(_default_instrument(t, mode))
        instrument = self._ed_vars["instrument"].get()

        # Channel — SMU (A/B) or WGEN (CH1/CH2); none for DMM
        if t == "wave":
            self._chan_cb.config(state="readonly", values=_WGEN_CHANNELS)
            if self._ed_vars["chan"].get() not in _WGEN_CHANNELS:
                self._ed_vars["chan"].set("CH1")
            self._shape_cb.config(state="readonly")
            if self._ed_vars["shape"].get() not in _WAVE_SHAPES:
                self._ed_vars["shape"].set("SIN")
            self._freq_ent.config(state="normal")
            if not self._ed_vars["freq"].get():
                self._ed_vars["freq"].set("1000")
        elif instrument == "SMU":
            self._chan_cb.config(state="readonly", values=_SMU_CHANNELS)
            if self._ed_vars["chan"].get() not in _SMU_CHANNELS:
                self._ed_vars["chan"].set("A")
        else:
            self._ed_vars["chan"].set("")

        if _limit_applicable(t, mode, instrument):
            self._limit_ent.config(state="normal")
            if (_limit_is_current_compliance(t, mode, instrument)
                    and not self._ed_vars["limit"].get()):
                self._ed_vars["limit"].set(_DEFAULT_SMU_CURRENT_LIMIT)

        if _is_measurement_step({"type": t, "mode": mode}):
            self._avg_count_ent.config(state="normal")
            self._avg_delay_ent.config(state="normal")
            if not self._ed_vars["avg_count"].get():
                self._ed_vars["avg_count"].set("1")
            if not self._ed_vars["avg_delay"].get():
                self._ed_vars["avg_delay"].set("0")

        self._update_level_hint()

    def _conn_from_editor(self):
        """⚙ — fill the Conn field with closures computed from the editor."""
        step = self._editor_step()
        _channels, _detail, unresolved = self.step_connections(step)
        self._ed_vars["conn"].set(self._computed_conn_string(step))
        if unresolved:
            messagebox.showwarning(
                "Unresolved",
                "Not found in wiring / steps: " + ", ".join(unresolved))

    # ── Switch-connection computation ─────────────────────────────────────────

    def _resolve_pin(self, token: str):
        """Resolve a step pin token to the probe-card PIN NUMBER.

        The pin number alone determines the matrix column to close:
        pins 1–12 → slot 2 columns 1–12, pins 13–24 → slot 4 columns 1–12.
        Accepts "<pin>:<pad>" (picker format) or a bare pin number — the
        leading number wins directly; a bare pad name is looked up in the
        wiring table to find its pin number. Returns int or None."""
        token = token.strip()
        if not token:
            return None
        head = token.split(":", 1)[0].strip()
        if head.isdigit():
            return int(head)                      # pin number is authoritative
        for r in self._get_wiring():              # pad name → its pin number
            if token.lower() == (r.get("pad") or "").strip().lower():
                pin = (r.get("pin") or "").strip()
                return int(pin) if pin.isdigit() else None
        return None

    def _step_index(self, ref: str):
        """Index of a step referenced by name (case-insensitive) or 1-based
        number; None when not found."""
        ref = ref.strip()
        if not ref:
            return None
        if ref.isdigit():
            i = int(ref) - 1
            return i if 0 <= i < len(self._steps) else None
        for j, s in enumerate(self._steps):
            if s.get("name", "").strip().lower() == ref.lower():
                return j
        return None

    def _find_step(self, ref: str):
        """Find a step by name (case-insensitive) or 1-based step number."""
        idx = self._step_index(ref)
        return self._steps[idx] if idx is not None else None

    def _computed_conn_string(self, step: dict) -> str:
        """Auto-computed value for the step's stored conn field."""
        if step.get("type") == "open" \
                and (step.get("target") or "").strip().lower() == "all":
            return "all"
        return ",".join(self.step_connections(step)[0])

    def step_connections(self, step: dict):
        """Compute the 707B closures for a step.

        Returns (channels: list[str], detail: list[str], unresolved: list[str]).
        For open steps the channels are the ones to OPEN — taken from the
        target step's STORED closures; target=all means open every channel
        (empty list + note) and reset all instrument outputs.
        """
        t = step.get("type")
        if t == "delay":
            return [], ["no switching — wait"], []
        if t == "picture":
            return [], ["no switching — take picture (not yet implemented)"], []
        if t == "passfail":
            tgt = (step.get("target") or "").strip()
            return [], [f"no switching — checks '{tgt}' against Min/Max" if tgt
                        else "no switching — checks the previous measurement"], []
        if t == "open":
            tgt = (step.get("target") or "").strip()
            if tgt.lower() == "all":
                return [], ["open ALL channels (channel.open('allslots')) "
                            "+ reset all instrument outputs"], []
            ref = self._find_step(tgt)
            if ref is None or ref.get("type") in ("delay", "open", "passfail", "picture"):
                return [], [], [tgt or "(no target)"]
            channels = [c for c in (ref.get("conn") or "").replace(" ", "").split(",")
                        if c]
            detail = [f"open closures of step '{ref.get('name')}'"]
            if ref.get("type") == "wave":
                detail.append(f"reset WGEN {ref.get('chan') or 'CH1'} output")
            elif ref.get("mode") == "apply":
                detail.append(f"reset SMU {ref.get('chan') or 'A'} output")
            return channels, detail, []

        rows_hi, rows_lo = _rows_for(t, step.get("chan") or "",
                                     step.get("instrument") or "")
        channels, detail, unresolved = [], [], []
        for field, rows in (("hi", rows_hi), ("lo", rows_lo)):
            for token in (p for p in step.get(field, "").split(",") if p.strip()):
                pin = self._resolve_pin(token)
                if pin is None or not (1 <= pin <= 24):
                    unresolved.append(token.strip())
                    continue
                slot, col = ("2", pin) if pin <= 12 else ("4", pin - 12)
                for row in rows:
                    ch = _pin_channel(pin, row)
                    channels.append(ch)
                    detail.append(
                        f"{ch} = {_ROW_LABELS[row]} × pin {pin} (slot {slot} col {col:02d})")
        return channels, detail, unresolved

    def _update_connections(self):
        """Rebuild the per-step closure report (STORED closures; steps whose
        stored value was hand-edited away from the wiring-computed routing
        are flagged) and push it to the registered viewer (Switch Debug tab)."""
        lines = []
        for i, step in enumerate(self._steps, 1):
            _channels, detail, unresolved = self.step_connections(step)
            computed = self._computed_conn_string(step)
            stored   = (step.get("conn") or "").replace(" ", "")
            tag = step.get("mode") or step.get("chan") or ""
            label = f"{i}. {step.get('name') or '(unnamed)'} " \
                    f"[{step.get('type')}{('/' + tag) if tag else ''}]"
            if step.get("type") == "delay":
                lines.append(f"{label}  wait {step.get('level') or '?'} ms — no switching")
                continue
            if step.get("type") == "passfail":
                tgt = step.get("target") or "(most recent measurement)"
                mn, mx = step.get("min") or "—", step.get("max") or "—"
                lines.append(f"{label}  check '{tgt}' in [{mn}, {mx}] — no switching")
                continue
            verb = "open" if step.get("type") == "open" else "close"
            body = f"{verb} {stored}" if stored else "no closures stored"
            if stored != computed:
                body += f"   ✎ edited (auto: {computed or '—'})"
            elif detail:
                body += f"   ({'; '.join(detail)})"
            if unresolved:
                body += f"   ⚠ unresolved: {', '.join(unresolved)}"
            lines.append(f"{label}  {body}")
        self._conn_report = "\n".join(lines) if lines else "— no steps —"
        self._conn_text.config(state="normal")
        self._conn_text.delete("1.0", "end")
        self._conn_text.insert("1.0", self._conn_report)
        self._conn_text.config(state="disabled")
        if self._conn_viewer:
            try:
                self._conn_viewer(f"[{self._current}]\n{self._conn_report}")
            except Exception:
                pass

    def set_connections_viewer(self, fn):
        """Register a callable(text) that mirrors the per-step closure
        report (shown on the Switch Debug tab too). Pushes the current one."""
        self._conn_viewer = fn
        self._update_connections()

    # ── Recipe validation ─────────────────────────────────────────────────────

    _CHAN_RE = re.compile(r"^[24][A-H](0[1-9]|1[0-2])$")

    def validate_recipe(self) -> list:
        """Sanity-check the active recipe's steps.

        Returns a list of "ERROR …"/"WARN …" strings (empty = recipe OK):
          - HI and LO must differ; pins must resolve via the wiring (1–24)
          - switching steps need stored closures with valid 707B channels
          - apply/wave/delay steps need a numeric Level
          - open targets must exist and come BEFORE the open step
          - WARN if an apply/wave output is never opened/reset afterwards
          - WARN when persisting closures put two instrument rows on one pin
          - WARN when closures are still closed at the end of the recipe
        """
        issues = []
        closed = {}        # channel → closing step label (closures persist)
        outputs_on = {}    # step index → step (apply/wave output still on)
        wiring_pins = {(r.get("pin") or "").strip()
                       for r in self._get_wiring() if (r.get("pin") or "").strip()}
        for i, s in enumerate(self._steps, 1):
            t    = s.get("type")
            name = s.get("name") or f"step {i}"
            tag  = f"{i}. {name}"
            if t == "delay":
                try:
                    float(s.get("level") or "")
                except ValueError:
                    issues.append(f"ERROR {tag}: delay time (Level) is not a number")
                continue

            if t == "picture":
                continue   # placeholder — no fields to validate yet

            if t == "passfail":
                tgt = (s.get("target") or "").strip()
                if tgt:
                    idx = self._step_index(tgt)
                    if idx is None:
                        issues.append(f"ERROR {tag}: target '{tgt}' not found")
                    elif idx >= i - 1:
                        issues.append(f"ERROR {tag}: target '{tgt}' comes at/after this "
                                      "passfail step — the measurement must come first")
                    elif not _is_measurement_step(self._steps[idx]):
                        issues.append(f"ERROR {tag}: target '{tgt}' is a "
                                      f"{self._steps[idx].get('type')} step "
                                      "(not a measurement — nothing to check)")
                elif not any(_is_measurement_step(s2) for s2 in self._steps[:i - 1]):
                    issues.append(f"ERROR {tag}: no target set and no measurement "
                                  "step precedes this passfail step")
                mn, mx = (s.get("min") or "").strip(), (s.get("max") or "").strip()
                if not mn and not mx:
                    issues.append(f"ERROR {tag}: set at least one of Min/Max")
                for label, val in (("Min", mn), ("Max", mx)):
                    if val:
                        try:
                            float(val)
                        except ValueError:
                            issues.append(f"ERROR {tag}: {label} is not a number")
                if mn and mx:
                    try:
                        if float(mn) > float(mx):
                            issues.append(f"ERROR {tag}: Min is greater than Max")
                    except ValueError:
                        pass
                continue

            if t == "open":
                tgt = (s.get("target") or "").strip()
                if tgt.lower() == "all":
                    closed.clear()
                    outputs_on.clear()
                    continue
                idx = self._step_index(tgt)
                if idx is None:
                    issues.append(f"ERROR {tag}: target '{tgt}' not found")
                elif idx >= i - 1:
                    issues.append(f"ERROR {tag}: target '{tgt}' comes at/after this "
                                  "open step — open must follow the step it opens")
                elif self._steps[idx].get("type") in ("delay", "open", "passfail", "picture"):
                    issues.append(f"ERROR {tag}: target '{tgt}' is a "
                                  f"{self._steps[idx].get('type')} step (nothing to open)")
                else:
                    outputs_on.pop(idx, None)
                    for ch in (self._steps[idx].get("conn") or "").replace(" ", "").split(","):
                        closed.pop(ch, None)
                continue

            # Switching steps (resistance / voltage / current / wave)
            mode = s.get("mode") or ""
            instrument = s.get("instrument") or ""
            valid_instruments = _instrument_options(t, mode)
            if instrument not in valid_instruments:
                issues.append(f"ERROR {tag}: instrument '{instrument or '(none)'}' is "
                              f"not valid for {t}{'/' + mode if mode else ''} "
                              f"(expected {' or '.join(valid_instruments)})")

            hi, lo = s.get("hi", "").strip(), s.get("lo", "").strip()
            if hi and lo and hi == lo:
                issues.append(f"ERROR {tag}: HI and LO are the same pin ({hi})")
            _ch, _det, unresolved = self.step_connections(s)
            if unresolved:
                issues.append(f"ERROR {tag}: pins not resolvable / out of range: "
                              + ", ".join(unresolved))
            for token in (hi, lo):
                pin = self._resolve_pin(token) if token else None
                if pin is not None and wiring_pins and str(pin) not in wiring_pins:
                    issues.append(f"WARN {tag}: pin {pin} ('{token}') is not defined "
                                  "in the probe card wiring")
            if t == "wave" or mode == "apply":
                try:
                    float(s.get("level") or "")
                except ValueError:
                    issues.append(f"ERROR {tag}: "
                                  f"{'amplitude' if t == 'wave' else 'source level'}"
                                  " (Level) is not a number")
                outputs_on[i - 1] = s

            if t == "wave":
                try:
                    float(s.get("freq") or "")
                except ValueError:
                    issues.append(f"ERROR {tag}: frequency (Freq) is not a number")
                if s.get("shape") not in _WAVE_SHAPES:
                    issues.append(f"ERROR {tag}: waveform shape "
                                  f"'{s.get('shape')}' is invalid")

            limit = s.get("limit") or ""
            if limit:
                try:
                    float(limit)
                except ValueError:
                    issues.append(f"ERROR {tag}: limit value is not a number")
                if not _limit_applicable(t, mode, instrument):
                    issues.append(f"WARN {tag}: limit set but not applicable to this "
                                  "step (needs SMU sourcing, or wave) — it will be ignored")

            if _is_measurement_step(s):
                try:
                    if int(s.get("avg_count") or 1) < 1:
                        issues.append(f"ERROR {tag}: Avg Count must be a whole number ≥ 1")
                except ValueError:
                    issues.append(f"ERROR {tag}: Avg Count is not a whole number")
                try:
                    if float(s.get("avg_delay") or 0) < 0:
                        issues.append(f"ERROR {tag}: Avg Delay must be a number ≥ 0")
                except ValueError:
                    issues.append(f"ERROR {tag}: Avg Delay is not a number")

            conn = (s.get("conn") or "").replace(" ", "")
            if not conn:
                issues.append(f"ERROR {tag}: no switch closures stored")
                continue
            bad = [c for c in conn.split(",") if not self._CHAN_RE.match(c)]
            if bad:
                issues.append(f"ERROR {tag}: invalid channel(s): {', '.join(bad)}")
                continue
            # Two SOURCE/HI rows on one pin = instruments shorted at the pin.
            # Shared LO/GND returns (rows B/D/E) on one pin are normal.
            _HI_ROWS = set("ACFGH")
            for ch in conn.split(","):
                pin_key = (ch[0], ch[2:])       # (slot, column) = one probe pin
                for other, other_tag in closed.items():
                    if ((other[0], other[2:]) == pin_key and other[1] != ch[1]
                            and ch[1] in _HI_ROWS and other[1] in _HI_ROWS):
                        issues.append(
                            f"WARN {tag}: {ch} puts a second instrument HI row on "
                            f"the same pin as {other} (closed by {other_tag}) — "
                            "intended bias, or missing open step?")
                closed[ch] = tag

        for idx in sorted(outputs_on):
            s = outputs_on[idx]
            what = ("WGEN " + (s.get("chan") or "CH1")) if s.get("type") == "wave" \
                   else f"SMU {s.get('chan') or 'A'}"
            issues.append(f"WARN {idx + 1}. {s.get('name') or 'step'}: {what} output "
                          "is never opened/reset — add an open step")
        if closed:
            issues.append(f"WARN: {len(closed)} closure(s) still closed at the end "
                          "— consider finishing with an open (target=all) step")
        return issues

    def _validate_clicked(self):
        issues = self.validate_recipe()
        if not self._steps:
            messagebox.showinfo("Validate Recipe", "No steps to check.")
            return
        for msg in issues:
            self.controller.log(f"[RECIPE] {msg}")
        self._store_validity(self._current, issues)
        if not issues:
            self.controller.log(f"[RECIPE] '{self._current}' validated — "
                                f"{len(self._steps)} step(s) OK")
            messagebox.showinfo("Recipe OK",
                                f"'{self._current}' — {len(self._steps)} step(s), "
                                "no issues found.")
        else:
            shown = "\n".join(issues[:15])
            if len(issues) > 15:
                shown += f"\n… and {len(issues) - 15} more (see log)"
            messagebox.showwarning(
                "Recipe Issues",
                f"'{self._current}' — {len(issues)} issue(s):\n\n{shown}")

    # ── Per-recipe validity status — green/red, cached across recipe
    # switches so the picker always reflects each recipe's last-known
    # readiness without forcing a re-validate ─────────────────────────────

    def _store_validity(self, name: str, issues: list):
        """Cache whether `name` is ready to use (no ERROR-level issues —
        WARNs alone don't block a run) and refresh the indicator if it's
        the one currently shown."""
        rec = self._recipes.get(name)
        if rec is None:
            return
        rec["valid"] = bool(rec.get("steps")) and not any(
            m.startswith("ERROR") for m in issues)
        if name == self._current:
            self._update_validity_label()

    def validate_all_recipes(self) -> dict:
        """Run validate_recipe() against every recipe for the active probe
        card (not just the one open in the editor) and cache each one's
        pass/fail — called on 💾 Save and whenever a new recipe set is
        loaded (see load_recipes), so switching recipes shows an
        up-to-date status immediately instead of "not validated" until the
        user happens to click ✓ Validate on that one specifically."""
        saved_steps = self._steps
        results = {}
        try:
            for name, rec in self._recipes.items():
                self._steps = rec.get("steps", [])
                issues = self.validate_recipe()
                self._store_validity(name, issues)
                results[name] = rec.get("valid", False)
        finally:
            self._steps = saved_steps
        return results

    def _update_validity_label(self):
        rec = self._recipes.get(self._current, {})
        valid = rec.get("valid")
        if valid is True:
            self._validity_lbl.config(text="✓ Valid", fg="#15803d")
        elif valid is False:
            self._validity_lbl.config(text="✗ Invalid", fg="#dc2626")
        else:
            self._validity_lbl.config(text="— Not validated", fg="#6b7280")

    # ── Lock while a run is in progress ─────────────────────────────────────
    #
    # A run (Full Die/Test Die/Test PMA) executes its own frozen snapshot of
    # steps (see instrument_panel.py's _exec2_load_recipe -> get_steps(), a
    # copy) so editing here can't corrupt an in-flight run's data — but
    # letting the operator add/save/switch/delete recipes while a run is
    # actually executing on the prober is still confusing and error-prone
    # (e.g. "why didn't my edit take effect", or accidentally overwriting a
    # different recipe mid-run). MainLayout calls this whenever
    # self._exec2_running flips.
    _LOCKABLE_BUTTONS = (
        "_btn_new", "_btn_delete", "_btn_load_ini", "_btn_import_legacy",
        "_btn_import_workbook", "_btn_save", "_btn_add_step",
        "_btn_update_step", "_btn_remove_step", "_btn_move_up",
        "_btn_move_down", "_btn_recompute",
    )

    def set_locked(self, locked: bool):
        state = "disabled" if locked else "normal"
        for attr in self._LOCKABLE_BUTTONS:
            getattr(self, attr).config(state=state)
        self._picker.config(state="disabled" if locked else "readonly")
        self._locked_lbl.config(
            text="🔒 Locked while a run is in progress" if locked else "")

    def _recompute_all(self):
        """↻ — overwrite every step's stored closures with computed values."""
        if not self._steps:
            return
        if not messagebox.askyesno(
                "Recompute Connections",
                "Overwrite the stored switch connections on ALL steps with\n"
                "values computed from the probe card wiring?\n"
                "Hand-edited connections will be replaced."):
            return
        # Two passes: open steps copy their target's stored closures, so the
        # normal steps must be recomputed first.
        for step in self._steps:
            if step.get("type") not in ("delay", "open", "passfail", "picture"):
                step["conn"] = self._computed_conn_string(step)
        for step in self._steps:
            if step.get("type") == "open":
                step["conn"] = self._computed_conn_string(step)
        self._refresh_steps()

    def _editor_step(self) -> dict:
        step = {k: self._ed_vars[k].get().strip() for k in _STEP_FIELDS}
        if step["type"] not in _STEP_TYPES:
            step["type"] = "resistance"
        return _normalize_step(step)

    # Fields that hold a plain base-unit float once _finalize_step has
    # normalized them (see below) -- re-displayed with an auto-picked
    # engineering prefix ("1.000u" instead of "0.000001") rather than
    # the raw stored string. Old recipes saved before prefix support
    # existed already store plain floats here too, so they get the
    # nicer display for free the next time a step is opened.
    _PREFIXABLE_FIELDS = ("level", "limit", "freq", "min", "max")

    def _step_to_editor(self):
        sel = self._step_tree.selection()
        if not sel:
            return
        idx = self._step_tree.index(sel[0])
        if 0 <= idx < len(self._steps):
            stored = self._steps[idx]
            for k in _STEP_FIELDS:
                raw = stored.get(k, "")
                if k in self._PREFIXABLE_FIELDS and raw:
                    try:
                        self._ed_vars[k].set(format_engineering_compact(float(raw)))
                        continue
                    except ValueError:
                        pass   # not actually numeric -- fall through and show it raw
                self._ed_vars[k].set(raw)
            self._on_type_change()

    def _finalize_step(self, step: dict) -> bool:
        """Validate and auto-fill a step from the editor. Returns False on error."""
        if step["type"] == "delay":
            try:
                step["level"] = _normalize_numeric_field(step["level"])
            except ValueError:
                messagebox.showerror("Invalid Step", "Delay steps need a time in ms (Level).")
                return False
            return True
        if step["type"] == "picture":
            return True   # placeholder — no fields to validate yet
        if step["type"] == "open":
            tgt = step["target"].strip()
            if tgt.lower() != "all":
                ref = self._find_step(tgt)
                if ref is None or ref.get("type") in ("delay", "open", "passfail", "picture"):
                    messagebox.showerror(
                        "Invalid Step",
                        "Open steps need a Target: a previous measurement/wave\n"
                        "step (by name or number), or 'all'.")
                    return False
            if not step["conn"]:
                step["conn"] = self._computed_conn_string(step)
            return True
        if step["type"] == "passfail":
            tgt = step["target"].strip()
            if tgt:
                ref = self._find_step(tgt)
                if ref is None or not _is_measurement_step(ref):
                    messagebox.showerror(
                        "Invalid Step",
                        "Passfail Target must be a previous resistance / voltage"
                        "(measure) / current(measure) step, or blank to use the "
                        "most recent measurement.")
                    return False
            elif not any(_is_measurement_step(s) for s in self._steps):
                messagebox.showerror(
                    "Invalid Step",
                    "No measurement step exists yet for this passfail step to check.")
                return False
            if not (step["min"] or step["max"]):
                messagebox.showerror("Invalid Step", "Set at least one of Min/Max.")
                return False
            for label, key in (("Min", "min"), ("Max", "max")):
                if step[key]:
                    try:
                        step[key] = _normalize_numeric_field(step[key])
                    except ValueError:
                        messagebox.showerror("Invalid Step", f"{label} must be a number.")
                        return False
            return True
        if not (step["hi"] or step["lo"]):
            messagebox.showerror("Invalid Step", "Specify at least one HI or LO pin.")
            return False
        if _is_measurement_step(step):
            try:
                if int(step["avg_count"]) < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Step", "Avg Count must be a whole number ≥ 1.")
                return False
            try:
                if float(step["avg_delay"]) < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Step", "Avg Delay must be a number ≥ 0.")
                return False
        # Normalize Level/Limit/Freq to a plain base-unit float string (a
        # user-typed "5m"/"2u"/"1k" is accepted here and everywhere else
        # keeps working against a plain float, exactly as before prefix
        # support existed — the run engine's _exec2_run_steps_once and
        # every CSV/export path never sees a suffix).
        for label, key in (("Level", "level"), ("Limit", "limit"), ("Freq", "freq")):
            if step[key]:
                try:
                    step[key] = _normalize_numeric_field(step[key])
                except ValueError:
                    messagebox.showerror(
                        "Invalid Step",
                        f"{label} must be a number (optionally with a unit "
                        "prefix like m/µ/n/k, e.g. \"5m\" or \"2u\").")
                    return False
        # Store the computed switch closures with the step (leave the field
        # alone if the user typed/edited their own routing; clear it to
        # regenerate from the wiring).
        if not step["conn"]:
            step["conn"] = self._computed_conn_string(step)
        return True

    def _step_add(self):
        step = self._editor_step()
        if not step["name"]:
            step["name"] = f"Step {len(self._steps) + 1}"
        if not self._finalize_step(step):
            return
        self._steps.append(step)
        self._refresh_steps()

    def _step_update(self):
        sel = self._step_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a step to update.")
            return
        idx = self._step_tree.index(sel[0])
        if 0 <= idx < len(self._steps):
            step = self._editor_step()
            if not self._finalize_step(step):
                return
            self._steps[idx] = step
            self._refresh_steps(select=idx)

    def _step_remove(self):
        sel = self._step_tree.selection()
        if not sel:
            return
        idx = self._step_tree.index(sel[0])
        if 0 <= idx < len(self._steps):
            del self._steps[idx]
            self._refresh_steps()

    def _step_move(self, delta: int):
        sel = self._step_tree.selection()
        if not sel:
            return
        idx = self._step_tree.index(sel[0])
        new = idx + delta
        if 0 <= idx < len(self._steps) and 0 <= new < len(self._steps):
            self._steps[idx], self._steps[new] = self._steps[new], self._steps[idx]
            self._refresh_steps(select=new)

    def _refresh_steps(self, select: int = -1):
        self._step_tree.delete(*self._step_tree.get_children())
        for i, step in enumerate(self._steps, 1):
            self._step_tree.insert("", "end", values=(
                i, step.get("name", ""), step.get("type", ""),
                step.get("instrument", ""), step.get("mode", ""),
                step.get("chan", ""), step.get("target", ""),
                step.get("hi", ""), step.get("lo", ""),
                step.get("level", ""), step.get("limit", ""),
                _avg_display(step),
                step.get("min", ""), step.get("max", ""),
                step.get("shape", ""), step.get("freq", ""), step.get("conn", "")))
        kids = self._step_tree.get_children()
        if 0 <= select < len(kids):
            self._step_tree.selection_set(kids[select])
        self._refresh_target_values()
        self._update_connections()

    # ── Recipe switching / management ─────────────────────────────────────────

    def _store_form(self):
        """Write the active recipe's steps back into the recipe store."""
        rec = self._recipes.get(self._current)
        if rec is None:
            return
        rec["steps"] = self._steps

    def _load_form(self, name: str):
        """Populate the steps table from recipe `name`."""
        rec = self._recipes[name]
        self._current = name
        self._picker_var.set(name)
        self._steps = rec.setdefault("steps", [])
        self._refresh_steps()
        self._update_validity_label()

    def _switch_recipe(self):
        name = self._picker_var.get()
        if name == self._current or name not in self._recipes:
            return
        self._store_form()
        self._load_form(name)
        self.controller.log(f"[RECIPE] Active recipe: {name}")

    def _refresh_picker(self):
        names = list(self._recipes.keys())
        self._picker.config(values=names)
        if self._current not in names and names:
            self._load_form(names[0])
        else:
            self._picker_var.set(self._current)

    def _new_recipe(self):
        """＋ New — add a recipe (copy of the current one) to the active
        probe card's recipe set and persist it immediately."""
        card = self._get_active_card()
        if not card:
            messagebox.showerror(
                "No Probe Card",
                "Select or create a probe card first — on the Pad to Probe "
                "tab. Recipes belong to exactly one probe card and are "
                "stored inside its .csv file.")
            return
        name = simpledialog.askstring("New Recipe", "Recipe name:",
                                      parent=self)
        if not name:
            return
        name = _safe_filename(name)
        if not name:
            messagebox.showerror("Invalid Name", "Use letters, digits, space, - or _.")
            return
        if name in self._recipes:
            messagebox.showerror("Duplicate", f"Recipe '{name}' already exists.")
            return
        self._store_form()
        # New recipe starts as a copy of the current one
        cur = self._recipes[self._current]
        rec = {"steps": [dict(s) for s in cur["steps"]]}
        self._recipes[name] = rec
        # Drop the untouched startup placeholder once a real recipe exists
        if ("(unsaved)" in self._recipes and "(unsaved)" != name
                and len(self._recipes) > 1
                and not self._recipes["(unsaved)"]["steps"]):
            del self._recipes["(unsaved)"]
        self._load_form(name)
        self._refresh_picker()
        if self._save_recipes(card, self._recipes):
            self.controller.log(f"[RECIPE] Created '{name}' in probe card '{card}' "
                                f"(copy of previous recipe)")
        else:
            self.controller.log(f"[RECIPE] Created '{name}' — save to probe card "
                                f"'{card}' failed")

    def _delete_recipe(self):
        """🗑 Delete — removes the recipe from the active probe card's
        recipe set and persists immediately."""
        if len(self._recipes) <= 1:
            messagebox.showinfo("Cannot Delete", "At least one recipe must remain.")
            return
        name = self._current
        if not messagebox.askyesno("Delete Recipe", f"Delete recipe '{name}'?"):
            return

        del self._recipes[name]
        self._current = next(iter(self._recipes))
        self._load_form(self._current)
        self._refresh_picker()

        card = self._get_active_card()
        if card and self._save_recipes(card, self._recipes):
            self.controller.log(f"[RECIPE] Deleted '{name}' from probe card '{card}'")
        elif card:
            self.controller.log(f"[RECIPE] Deleted '{name}' — save to probe card "
                                f"'{card}' failed")
        else:
            self.controller.log(f"[RECIPE] Deleted '{name}' (in-memory only — "
                                "no probe card active)")

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _load(self):
        """📂 Load .ini… — import a hand-authored single-recipe .ini file
        into the active probe card's recipe set (like ＋New, persisted
        immediately)."""
        card = self._get_active_card()
        if not card:
            messagebox.showerror(
                "No Probe Card",
                "Select or create a probe card first — on the Pad to Probe "
                "tab. A loaded recipe is registered under the active card.")
            return
        path = filedialog.askopenfilename(
            title="Load Recipe .ini",
            filetypes=[("Recipe / INI files", "*.ini *.txt *.cfg *.pms"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            found = parse_recipe_file(path)
        except Exception as exc:
            self.controller.log(f"[RECIPE] Load error: {exc}")
            return
        (name, rec), = found.items()
        orig_name, n = name, 2
        while name in self._recipes:
            name = f"{orig_name} ({n})"
            n += 1
        self._store_form()
        self._recipes[name] = rec
        # Drop the untouched startup placeholder when a real recipe arrives
        if ("(unsaved)" in self._recipes and "(unsaved)" != name
                and len(self._recipes) > 1
                and not self._recipes["(unsaved)"]["steps"]):
            del self._recipes["(unsaved)"]
        self._load_form(name)
        self._refresh_picker()
        if self._save_recipes(card, self._recipes):
            self._file_lbl.config(text=f"Imported '{name}' from {path}", fg="#374151")
            self.controller.log(
                f"[RECIPE] Imported '{name}' from {path} into probe card '{card}'")
        else:
            self.controller.log(
                f"[RECIPE] Imported '{name}' from {path} — save to probe card "
                f"'{card}' failed")

    def _import_legacy(self):
        """📥 Import Legacy (.pma)… — best-effort translate an old flat
        key=value prober recipe file's measurement defaults (Voltage,
        delays, averaging, current limit) into a new executable step
        sequence on the active probe card. Prober-sequence/die-geometry/
        alignment keys (moves, die size, align messages, picture file)
        are ignored outright — this app has no use for them. HI/LO pins
        can't be inferred from the file; fill them in on the generated
        measurement step before running."""
        card = self._get_active_card()
        if not card:
            messagebox.showerror(
                "No Probe Card",
                "Select or create a probe card first — on the Pad to Probe "
                "tab. An imported recipe is registered under the active card.")
            return
        path = filedialog.askopenfilename(
            title="Import Legacy Recipe (.pma / .PMS)",
            filetypes=[("Legacy recipe files", "*.pma *.PMS *.ini *.txt *.cfg"),
                      ("All files", "*.*")],
        )
        if not path:
            return
        try:
            useful = parse_pma_params(path)
        except Exception as exc:
            self.controller.log(f"[RECIPE] Legacy import error: {exc}")
            return
        if not useful:
            messagebox.showwarning(
                "Nothing to Import",
                "No recognized measurement parameters (Voltage, delays, "
                "averaging, current limit) were found in that file.")
            return
        steps = pma_params_to_steps(useful)

        name = os.path.splitext(os.path.basename(path))[0]
        orig_name, n = name, 2
        while name in self._recipes:
            name = f"{orig_name} ({n})"
            n += 1
        self._store_form()
        self._recipes[name] = {"steps": steps}
        if ("(unsaved)" in self._recipes and "(unsaved)" != name
                and len(self._recipes) > 1
                and not self._recipes["(unsaved)"]["steps"]):
            del self._recipes["(unsaved)"]
        self._load_form(name)
        self._refresh_picker()

        mapped = ", ".join(f"{k}={useful[k]}" for k in _PMA_MAPPED_KEYS if k in useful)
        unmapped = ", ".join(f"{k}={useful[k]}" for k in _PMA_UNMAPPED_KEYS if k in useful)
        msg = (f"[RECIPE] Imported legacy recipe '{name}' from {path} — "
              f"{len(steps)} step(s) generated from: {mapped or '(nothing recognized)'}")
        if unmapped:
            msg += f" — no step field for: {unmapped} (set on the instrument directly if needed)"
        self.controller.log(msg)
        if self._save_recipes(card, self._recipes):
            self._file_lbl.config(text=f"Imported legacy recipe '{name}'", fg="#374151")
            self.controller.log(f"[RECIPE] Saved '{name}' to probe card '{card}'")
        else:
            self.controller.log(
                f"[RECIPE] Imported '{name}' — save to probe card '{card}' failed")

        messagebox.showinfo(
            "Legacy Recipe Imported",
            f"Created recipe '{name}' with {len(steps)} step(s) from the legacy "
            "file's measurement defaults.\n\n"
            "HI/LO pins could not be inferred from the file — set them on the "
            "measurement step, then ✓ Validate before running.")

    def _import_legacy_workbook(self):
        """📥 Import Legacy Workbook (.xls)… — same translation as Import
        Legacy (.pma), but reads the measurement defaults straight from the
        MainMenu tab of the original "IMT Prober Recipe Generation" .xls
        workbook (the tool that used to hand-generate .PMA files) instead
        of requiring an already-exported .pma file. Useful when only the
        workbook is on hand, or the .PMA was never actually generated. See
        pma_wafer_panel.py for the wafer/shot map half of this same
        workbook (PMA tab)."""
        if _pma_xlrd is None:
            messagebox.showerror(
                "xlrd Not Installed",
                "Reading legacy .xls workbooks needs the xlrd package.\n\n"
                "Run:  .venv\\Scripts\\pip install xlrd")
            return
        card = self._get_active_card()
        if not card:
            messagebox.showerror(
                "No Probe Card",
                "Select or create a probe card first — on the Pad to Probe "
                "tab. An imported recipe is registered under the active card.")
            return
        path = filedialog.askopenfilename(
            title="Import Legacy Recipe Workbook (.xls)",
            filetypes=[("Excel 97-2003 Workbook", "*.xls"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            book = _pma_xlrd.open_workbook(path, formatting_info=True)
            info = _pma_read_main_menu_info(book)
            useful = info["params"]
        except Exception as exc:
            self.controller.log(f"[RECIPE] Legacy workbook import error: {exc}")
            messagebox.showerror("Import Failed", f"Could not read that workbook:\n{exc}")
            return
        if not useful:
            messagebox.showwarning(
                "Nothing to Import",
                "No Name/Value measurement fields (Voltage, delays, "
                "averaging, current limit) were found on that workbook's "
                "MainMenu tab.")
            return
        steps = pma_params_to_steps(useful)

        # A shot that co-touches multiple dies (see the PMA tab's wafer/shot
        # map) needs this same sequence run once per die, each later routed
        # to a different die's pins via the switch matrix.
        dies_per_shot = 1
        try:
            grid = _pma_read_moves_grid(book, "MajorMoves")
            widths = [len(s["dies"]) for s in grid["shots"] if s["included"]]
            if widths:
                dies_per_shot = max(widths)
        except Exception as exc:
            self.controller.log(f"[RECIPE] Could not read MajorMoves for dies-per-shot "
                                f"(defaulting to 1): {exc}")
        steps = repeat_steps_per_die(steps, dies_per_shot)

        name = info["recipe_name"] or os.path.splitext(os.path.basename(path))[0]
        orig_name, n = name, 2
        while name in self._recipes:
            name = f"{orig_name} ({n})"
            n += 1
        self._store_form()
        self._recipes[name] = {"steps": steps}
        if ("(unsaved)" in self._recipes and "(unsaved)" != name
                and len(self._recipes) > 1
                and not self._recipes["(unsaved)"]["steps"]):
            del self._recipes["(unsaved)"]
        self._load_form(name)
        self._refresh_picker()

        mapped = ", ".join(f"{k}={useful[k]}" for k in _PMA_MAPPED_KEYS if k in useful)
        unmapped = ", ".join(f"{k}={useful[k]}" for k in _PMA_UNMAPPED_KEYS if k in useful)
        msg = (f"[RECIPE] Imported legacy recipe '{name}' from workbook {path} — "
              f"{len(steps)} step(s) generated from: {mapped or '(nothing recognized)'}")
        if dies_per_shot > 1:
            msg += f" — repeated {dies_per_shot}x (this probe card's shots co-touch {dies_per_shot} dies)"
        if unmapped:
            msg += f" — no step field for: {unmapped} (set on the instrument directly if needed)"
        self.controller.log(msg)
        if self._save_recipes(card, self._recipes):
            self._file_lbl.config(text=f"Imported legacy recipe '{name}'", fg="#374151")
            self.controller.log(f"[RECIPE] Saved '{name}' to probe card '{card}'")
        else:
            self.controller.log(
                f"[RECIPE] Imported '{name}' — save to probe card '{card}' failed")

        repeat_note = (
            f"This probe card's shots co-touch {dies_per_shot} dies, so the "
            f"sequence was repeated {dies_per_shot}x (\"(Die 1)\", \"(Die 2)\", "
            "...) — assign each repetition's HI/LO pins separately.\n\n"
            if dies_per_shot > 1 else "")
        messagebox.showinfo(
            "Legacy Recipe Imported",
            f"Created recipe '{name}' with {len(steps)} step(s) from the "
            "workbook's MainMenu measurement defaults.\n\n"
            f"{repeat_note}"
            "HI/LO pins could not be inferred from the file — set them on the "
            "measurement step, then ✓ Validate before running.")

    def _save(self):
        """💾 Save — persist every recipe currently shown (the whole active
        probe card's recipe set, one combined write to its .csv file)."""
        if not self._recipes:
            return
        self._store_form()
        self.validate_all_recipes()
        card = self._get_active_card()
        if not card:
            messagebox.showerror(
                "No Probe Card",
                "Select or create a probe card first — recipes are stored "
                "inside its .csv file.")
            return
        if self._save_recipes(card, self._recipes):
            self._file_lbl.config(
                text=f"Saved {len(self._recipes)} recipe(s) to probe card '{card}'",
                fg="#374151")
            self.controller.log(
                f"[RECIPE] Saved {len(self._recipes)} recipe(s) to probe card '{card}'")
        else:
            self.controller.log(f"[RECIPE] Save failed for probe card '{card}'")

    # ── ATA integration ───────────────────────────────────────────────────────

    def load_recipes(self, card: str, recipes: dict):
        """Replace the panel's recipe set with `recipes` (name -> {"steps":
        [...]})  scoped to probe card `card` (""=no card active). Called by
        MainLayout whenever the active probe card changes (ATA load, picker
        switch, ＋New/🗑 Delete/✎ Rename) — a real replace, not a merge, since
        a recipe belongs to exactly the currently active card. Any unsaved
        edits to the recipe that was active before the switch are dropped —
        they were never persisted (same as before this file layout change:
        switching cards without saving already discarded in-flight edits)."""
        self._active_card = card
        if recipes:
            self._recipes = {name: {"steps": [dict(s) for s in rec.get("steps", [])]}
                              for name, rec in recipes.items()}
            self._current = next(iter(self._recipes))
        else:
            self._recipes = {"(unsaved)": {"steps": []}}
            self._current = "(unsaved)"
        self.validate_all_recipes()
        self._load_form(self._current)
        self._refresh_picker()

        self._card_lbl.config(text=f"Probe Card: {card}" if card else "Probe Card: (none)")
        if card:
            self._file_lbl.config(
                text=f"{len(recipes)} recipe(s) — probe card '{card}'", fg="#374151")
            self.controller.log(
                f"[RECIPE] Probe card '{card}': {len(recipes)} recipe(s)"
                + (f": {', '.join(recipes)}" if recipes else ""))
        else:
            self._file_lbl.config(text="No probe card selected", fg="#6b7280")
            self.controller.log("[RECIPE] No probe card active — no recipes to show.")

    # ── Public accessors ──────────────────────────────────────────────────────

    def get_active_card(self) -> str:
        return self._active_card

    def get_steps(self) -> list:
        """Return the active recipe's measurement steps (list of dicts with
        keys: name, type, mode, chan, target, hi, lo, level, conn — conn is
        the stored 707B closure list, e.g. "2A01,2B02"; for open steps it is
        the channels to open, or "all")."""
        return [dict(s) for s in self._steps]

    def refresh_connections(self):
        """Recompute the displayed switch closures (call after the probe-card
        wiring changes)."""
        self._update_connections()

    def get_recipe_names(self) -> list:
        return list(self._recipes.keys())

    def get_active_recipe(self) -> str:
        return self._current

    def select_recipe(self, name: str) -> bool:
        """Programmatically switch the active recipe. Returns True on success."""
        if name not in self._recipes:
            return False
        self._store_form()
        self._load_form(name)
        self._refresh_picker()
        return True
