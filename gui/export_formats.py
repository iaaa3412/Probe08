"""Results tab data export — format DEFINITIONS (table/column list + where
each column's value comes from) are data, not code, so the LaMP SQL layout
is just one example rather than the only option. Definitions are persisted
per-project as ATA_EXPORT_FORMATS_FILENAME in the ATA folder (see
load_formats/save_formats/add_format) and picked from a dropdown on the
Results tab (see instrument_panel.py's _tab_results).

Two format "type"s are supported:

  - "sql" (default, e.g. LAMP_FORMAT) — one INSERT INTO statement per
    eligible results_data row (see rows_for_format/build_insert_statements).
    This is what the ➕ New Format… dialog builds.

  - "csv" (e.g. MADX_FORMAT) — one CSV row per die touchdown, built by
    grouping all the readings recorded during that touchdown (current,
    voltage, resistance, ...) back into a single row (see
    group_results_by_die/build_csv_rows). Not (yet) buildable from the ➕
    New Format… dialog — ship additional ones as code, the same way
    MADX_FORMAT is shipped alongside LAMP_FORMAT.

A "sql"-type format definition is a plain dict:
    {
        "name": "LaMP Electrical (tblLampElectricalMeasurements)",
        "table": "tblLampElectricalMeasurements",
        "requires_die_id": True,   # only rows from a Test PMA run are eligible
        "columns": [
            {"field": "fldTestSerial", "source": "test_serial", "quote": False},
            {"field": "fldDieID",      "source": "die_id",      "quote": True},
            ...
        ],
    }

`source` picks a value per output row — either straight off a
results_data row dict (see instrument_panel.py's record_result: die_id,
switch, set_voltage, voltage, value, unit, recipe, die, step, type, mode,
timestamp, connection, instrument) or a computed extra (test_serial,
iteration) — see SOURCE_FIELDS/resolve_source.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

ATA_EXPORT_FORMATS_FILENAME = "ata_export_formats.json"

# Sources a column can be mapped to when defining a new format — the
# well-known fields on a results_data row, plus a couple of computed
# extras that only make sense for a PMA-linked export.
SOURCE_FIELDS = {
    "die_id":      "Shot device-ID string (e.g. 94-60/94-50/94-61/94-51) — Test PMA only",
    "switch":      "Which of the shot's co-touched dies (1-4) — Test PMA only",
    "set_voltage": "Commanded/set bias voltage",
    "voltage":     "Actual measured voltage (SMU readback, falls back to set_voltage)",
    "value":       "The measurement reading itself (current, resistance, etc.)",
    "unit":        "Unit of the reading (A, V, ohm)",
    "recipe":      "Active recipe name",
    "die":         "Die label shown on the Run tab (Accretech XY/die number)",
    "step":        "Recipe step name",
    "type":        "Step type (current, voltage, resistance)",
    "mode":        "Step mode (apply/measure)",
    "timestamp":   "Reading timestamp",
    "test_serial": "Computed test serial — see compute_test_serial",
    "iteration":   "Always 1 (one row per die's final averaged reading)",
}

# Shipped as the default/example format — seeded into a fresh ATA folder's
# format file so there's always at least one usable format to pick.
LAMP_FORMAT: Dict[str, Any] = {
    "name": "LaMP Electrical (tblLampElectricalMeasurements)",
    "table": "tblLampElectricalMeasurements",
    "type": "sql",
    "requires_die_id": True,
    "columns": [
        {"field": "fldTestSerial", "source": "test_serial", "quote": False},
        {"field": "fldDieID",      "source": "die_id",      "quote": True},
        {"field": "fldSwitch",     "source": "switch",      "quote": False},
        {"field": "fldIteration",  "source": "iteration",   "quote": False},
        {"field": "fldSetVoltage", "source": "set_voltage", "quote": False},
        {"field": "fldVoltage",    "source": "voltage",     "quote": False},
        {"field": "fldCurrent",    "source": "value",       "quote": False},
    ],
}

# A second shipped example — a plain CSV (not SQL) layout, matching a
# legacy MAD-X-lot resistance-test export:
#   LotID,WaferID,ChipID,Row,Column,Connection,Voltage,Current,Resistance,
#   Voltage_DMM,Compliance,Time_Stamp
# One row per die touchdown rather than one row per reading — see
# group_results_by_die/build_csv_rows.
MADX_FORMAT: Dict[str, Any] = {
    "name": "MAD-X Resistance CSV (LotID/WaferID/ChipID...)",
    "table": "madx_resistance",
    "type": "csv",
    "requires_die_id": False,
    "columns": [
        {"field": "LotID",       "source": "lot_id"},
        {"field": "WaferID",     "source": "wafer_id"},
        {"field": "ChipID",      "source": "chip_id"},
        {"field": "Row",         "source": "row_num"},
        {"field": "Column",      "source": "column_letter"},
        {"field": "Connection",  "source": "connection"},
        {"field": "Voltage",     "source": "voltage"},
        {"field": "Current",     "source": "current"},
        {"field": "Resistance",  "source": "resistance"},
        {"field": "Voltage_DMM", "source": "voltage_dmm"},
        {"field": "Compliance",  "source": "compliance"},
        {"field": "Time_Stamp",  "source": "time_stamp"},
    ],
}


def compute_test_serial(lot_id: str, wafer_id: str) -> int:
    """No original schema was available to confirm the real numbering
    scheme, so for now this is Lot ID + Wafer ID's digits concatenated
    into one number (same identifiers the CSV export's filename already
    uses), constant across the whole export rather than incrementing per
    row."""
    digits = "".join(ch for ch in f"{lot_id}{wafer_id}" if ch.isdigit())
    return int(digits) if digits else 0


def sql_num(value, default: float = 0.0) -> str:
    """A value formatted as a bare SQL numeric literal: whole numbers with
    no decimal point (10, not 10.0 — matches the legacy example),
    fractional values in full decimal notation up to 15 places with
    trailing zeros trimmed (never scientific notation — SQL literal
    parsing doesn't want "1.57e-09")."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        f = default
    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    s = f"{f:.15f}".rstrip("0")
    return s if not s.endswith(".") else s + "0"


def sql_string(value) -> str:
    """A value formatted as a quoted SQL string literal, embedded single
    quotes doubled (the standard SQL escape)."""
    return "'" + str(value).replace("'", "''") + "'"


def load_formats(folder: str) -> List[Dict[str, Any]]:
    """Read ATA_EXPORT_FORMATS_FILENAME from folder, seeding it with the
    built-in LaMP + MAD-X formats if it doesn't exist yet (or is
    empty/corrupt) so a fresh ATA folder always has usable formats. Never
    returns an empty list; never raises."""
    path = os.path.join(folder, ATA_EXPORT_FORMATS_FILENAME)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            formats = data.get("formats") or []
            if formats:
                return formats
        except (OSError, ValueError):
            pass
    seeded = [LAMP_FORMAT, MADX_FORMAT]
    save_formats(folder, seeded)
    return seeded


def save_formats(folder: str, formats: List[Dict[str, Any]]):
    path = os.path.join(folder, ATA_EXPORT_FORMATS_FILENAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"formats": formats}, f, indent=2)


def add_format(folder: str, fmt: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Append a new format definition (replacing any existing one with the
    same name) and persist. Returns the updated list."""
    formats = [f for f in load_formats(folder) if f["name"] != fmt["name"]]
    formats.append(fmt)
    save_formats(folder, formats)
    return formats


def find_format(folder: str, name: str) -> Optional[Dict[str, Any]]:
    return next((f for f in load_formats(folder) if f["name"] == name), None)


def resolve_source(source: str, row: Dict[str, Any], context: Dict[str, Any]):
    if source == "test_serial":
        return context.get("test_serial", 0)
    if source == "iteration":
        return 1
    return row.get(source, "")


def rows_for_format(fmt: Dict[str, Any],
                    results_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if fmt.get("requires_die_id", True):
        return [r for r in results_data if r.get("die_id")]
    return list(results_data)


def build_insert_statements(fmt: Dict[str, Any], results_data: List[Dict[str, Any]],
                            lot_id: str, wafer_id: str) -> List[str]:
    """One "INSERT INTO <table> (...) VALUES (...)" line per eligible row
    in results_data (see rows_for_format), per the given format
    definition's column list."""
    rows = rows_for_format(fmt, results_data)
    context = {"test_serial": compute_test_serial(lot_id, wafer_id)}
    cols = fmt["columns"]
    field_list = ", ".join(c["field"] for c in cols)
    out = []
    for r in rows:
        vals = []
        for c in cols:
            raw = resolve_source(c["source"], r, context)
            vals.append(sql_string(raw) if c.get("quote") else sql_num(raw))
        out.append(f"INSERT INTO {fmt['table']} ({field_list}) VALUES ({','.join(vals)})")
    return out


# ── "csv"-type formats — one row per die touchdown ─────────────────────────
#
# A results_data row is one reading (one record_result() call); a single
# die touchdown runs several steps and so produces several readings (a
# current, maybe a resistance, maybe a DMM voltage...) all sharing the same
# `die` label. A "csv"-type format wants one output row per touchdown, so
# these readings need to be grouped back together first.

_DIE_RC_RE = re.compile(r"R(\d+)C(\d+)")


def _parse_die_rc(die_label: str):
    """"R{row}C{col}  (X.. Y..)" (the die_label the Run tab uses for every
    Accretech-sourced touchdown — see instrument_panel.py) -> (row, col)
    ints, or (None, None) if it doesn't match (e.g. a GDS-sourced label)."""
    m = _DIE_RC_RE.search(die_label or "")
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def _col_letter(col: int) -> str:
    """0-based column index -> spreadsheet-style letter (0->A, 8->I,
    25->Z, 26->AA), matching the legacy MAD-X ChipID scheme."""
    n = col + 1
    letters = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def group_results_by_die(results_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group flat results_data rows into one entry per die touchdown (all
    readings sharing the same `die` label), in first-seen order. Returns a
    context dict per touchdown with the fields a "csv"-type format's
    columns can reference (see MADX_FORMAT): die, chip_id, row_num,
    column_letter, connection, current, voltage, resistance, voltage_dmm,
    compliance, time_stamp."""
    order: List[str] = []
    rows_by_die: Dict[str, List[Dict[str, Any]]] = {}
    for r in results_data:
        die = r.get("die") or ""
        if die not in rows_by_die:
            rows_by_die[die] = []
            order.append(die)
        rows_by_die[die].append(r)

    out = []
    for die in order:
        rows = rows_by_die[die]
        row_num, col_num = _parse_die_rc(die)
        current_row = next((r for r in rows if r.get("type") == "current"), None)
        smu_voltage_row = next(
            (r for r in rows if r.get("type") == "voltage" and r.get("mode") == "measure"
             and r.get("instrument") == "SMU"), None)
        dmm_voltage_row = next(
            (r for r in rows if r.get("type") == "voltage" and r.get("mode") == "measure"
             and r.get("instrument") == "DMM"), None)
        resistance_row = next((r for r in rows if r.get("type") == "resistance"), None)
        connection = next((r.get("connection") for r in rows if r.get("connection")), "")

        current_val = current_row.get("value") if current_row else ""
        if current_row and current_row.get("voltage") not in (None, ""):
            voltage_val = current_row.get("voltage")
        elif smu_voltage_row:
            voltage_val = smu_voltage_row.get("value")
        else:
            voltage_val = ""

        if resistance_row:
            resistance_val = resistance_row.get("value")
        else:
            try:
                resistance_val = float(voltage_val) / float(current_val)
            except (TypeError, ValueError, ZeroDivisionError):
                resistance_val = ""

        out.append({
            "die": die,
            "chip_id": (f"{row_num:02d}{_col_letter(col_num)}"
                       if row_num is not None and col_num is not None else die),
            "row_num": f"{row_num:02d}" if row_num is not None else "",
            "column_letter": _col_letter(col_num) if col_num is not None else "",
            "connection": connection,
            "current": current_val,
            "voltage": voltage_val,
            "resistance": resistance_val,
            "voltage_dmm": dmm_voltage_row.get("value") if dmm_voltage_row else "",
            "compliance": "FALSE",   # not measured/tracked yet — always False for now
            "time_stamp": rows[0].get("timestamp", "") if rows else "",
        })
    return out


def build_csv_rows(fmt: Dict[str, Any], results_data: List[Dict[str, Any]],
                   lot_id: str, wafer_id: str) -> List[Dict[str, Any]]:
    """One dict per die touchdown that actually measured something (see
    group_results_by_die), keyed by the format's field names — ready for
    csv.DictWriter."""
    context = {"lot_id": lot_id, "wafer_id": wafer_id}
    out = []
    for g in group_results_by_die(results_data):
        if not g["current"] and not g["resistance"]:
            continue
        out.append({c["field"]: context.get(c["source"], g.get(c["source"], ""))
                   for c in fmt["columns"]})
    return out


def has_data_for_format(fmt: Dict[str, Any], results_data: List[Dict[str, Any]]) -> bool:
    """Whether an export of this format would produce at least one row —
    used to give a clear "nothing to export yet" error instead of writing
    an empty file."""
    if fmt.get("type") == "csv":
        return any(g["current"] or g["resistance"]
                  for g in group_results_by_die(results_data))
    return bool(rows_for_format(fmt, results_data))
