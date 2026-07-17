from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

ATA_EXPORT_FORMATS_FILENAME = "ata_export_formats.json"

SQL_SOURCE_FIELDS = {
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
    "instrument":  "Instrument that took the reading (SMU/DMM)",
    "connection":  "Switch-matrix channel(s) closed for this reading",
    "timestamp":   "Reading timestamp",
    "test_serial": "Computed test serial — see compute_test_serial",
    "iteration":   "Always 1 (one row per die's final averaged reading)",
}

CSV_SOURCE_FIELDS = {
    "lot_id":         "Lot ID entered on the Results tab",
    "wafer_id":       "Wafer ID entered on the Results tab",
    "chip_id":        "Row+Column die label (e.g. 02I)",
    "row_num":        "Die row number",
    "column_letter":  "Die column letter",
    "connection":     "All switch-matrix channels used for this die, merged",
    "current":        "Forced/measured current for this die",
    "voltage":        "SMU voltage readback for this die",
    "resistance":     "Resistance reading for this die",
    "voltage_dmm":    "Independent DMM voltage reading for this die",
    "compliance":     "Compliance-limit flag (currently always FALSE)",
    "time_stamp":     "Timestamp of the die's first reading",
    "test_serial":    "Computed test serial — see compute_test_serial",
}

SOURCE_FIELDS_BY_TYPE = {"sql": SQL_SOURCE_FIELDS, "csv": CSV_SOURCE_FIELDS}

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
        {"field": "Voltage_DMM", "source": "voltage_dmm", "multiply": -1},
        {"field": "Compliance",  "source": "compliance"},
        {"field": "Time_Stamp",  "source": "time_stamp"},
    ],
}


def compute_test_serial(lot_id: str, wafer_id: str) -> int:
    digits = "".join(ch for ch in f"{lot_id}{wafer_id}" if ch.isdigit())
    return int(digits) if digits else 0


def sql_num(value, default: float = 0.0) -> str:
    try:
        f = float(value)
    except (TypeError, ValueError):
        f = default
    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    s = f"{f:.15f}".rstrip("0")
    return s if not s.endswith(".") else s + "0"


def sql_string(value) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _formats_filename(system: str) -> str:
    if system == "accretech":
        return ATA_EXPORT_FORMATS_FILENAME
    base, ext = os.path.splitext(ATA_EXPORT_FORMATS_FILENAME)
    return f"{base}_{system}{ext}"


def load_formats(folder: str, system: str = "accretech") -> List[Dict[str, Any]]:
    path = os.path.join(folder, _formats_filename(system))
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
    save_formats(folder, seeded, system)
    return seeded


def save_formats(folder: str, formats: List[Dict[str, Any]], system: str = "accretech"):
    path = os.path.join(folder, _formats_filename(system))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"formats": formats}, f, indent=2)


def add_format(folder: str, fmt: Dict[str, Any], system: str = "accretech") -> List[Dict[str, Any]]:
    formats = [f for f in load_formats(folder, system) if f["name"] != fmt["name"]]
    formats.append(fmt)
    save_formats(folder, formats, system)
    return formats


def find_format(folder: str, name: str, system: str = "accretech") -> Optional[Dict[str, Any]]:
    return next((f for f in load_formats(folder, system) if f["name"] == name), None)


def resolve_source(source: str, row: Dict[str, Any], context: Dict[str, Any]):
    if source == "test_serial":
        return context.get("test_serial", 0)
    if source == "iteration":
        return 1
    if source in context:
        return context[source]
    return row.get(source, "")


def resolve_column_value(col: Dict[str, Any], row: Dict[str, Any], context: Dict[str, Any]):
    if "constant" in col and col["constant"] not in (None, ""):
        return col["constant"]
    raw = resolve_source(col.get("source", ""), row, context)
    mult = col.get("multiply")
    if mult not in (None, "", 1, 1.0) and raw not in (None, ""):
        try:
            return f"{float(raw) * float(mult):.6g}"
        except (TypeError, ValueError):
            return raw
    return raw


def detect_reading_kinds(results_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    seen = set()
    out = []
    for r in results_data:
        t, mode, instrument = r.get("type") or "", r.get("mode") or "", r.get("instrument") or ""
        key = (t, mode, instrument)
        if key == ("", "", "") or key in seen:
            continue
        seen.add(key)
        bits = [b for b in (t, mode, instrument) if b]
        out.append({"label": " / ".join(bits) if bits else "(reading)",
                    "type": t, "mode": mode, "instrument": instrument})
    return out


def rows_for_format(fmt: Dict[str, Any],
                    results_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if fmt.get("requires_die_id", True):
        return [r for r in results_data if r.get("die_id")]
    return list(results_data)


def build_insert_statements(fmt: Dict[str, Any], results_data: List[Dict[str, Any]],
                            lot_id: str, wafer_id: str) -> List[str]:
    rows = rows_for_format(fmt, results_data)
    context = {"test_serial": compute_test_serial(lot_id, wafer_id)}
    cols = fmt["columns"]
    field_list = ", ".join(c["field"] for c in cols)
    out = []
    for r in rows:
        vals = []
        for c in cols:
            raw = resolve_column_value(c, r, context)
            vals.append(sql_string(raw) if c.get("quote") else sql_num(raw))
        out.append(f"INSERT INTO {fmt['table']} ({field_list}) VALUES ({','.join(vals)})")
    return out



_DIE_RC_RE = re.compile(r"R(\d+)C(\d+)")


def _parse_die_rc(die_label: str):
    m = _DIE_RC_RE.search(die_label or "")
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def _col_letter(col: int) -> str:
    n = col + 1
    letters = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def _combined_connection(rows: List[Dict[str, Any]]) -> str:
    seen: List[str] = []
    for r in rows:
        for ch in (r.get("connection") or "").split("_"):
            if ch and ch not in seen:
                seen.append(ch)
    seen.sort(key=lambda ch: ch[1] if len(ch) > 1 else ch)
    return "_".join(seen)


def group_results_by_die(results_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        connection = _combined_connection(rows)

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
            "compliance": "FALSE",
            "time_stamp": rows[0].get("timestamp", "") if rows else "",
        })
    return out


def build_csv_rows(fmt: Dict[str, Any], results_data: List[Dict[str, Any]],
                   lot_id: str, wafer_id: str) -> List[Dict[str, Any]]:
    context = {"lot_id": lot_id, "wafer_id": wafer_id,
              "test_serial": compute_test_serial(lot_id, wafer_id)}
    out = []
    for g in group_results_by_die(results_data):
        if not g["current"] and not g["resistance"]:
            continue
        out.append({c["field"]: resolve_column_value(c, g, context) for c in fmt["columns"]})
    return out


def has_data_for_format(fmt: Dict[str, Any], results_data: List[Dict[str, Any]]) -> bool:
    if fmt.get("type") == "csv":
        return any(g["current"] or g["resistance"]
                  for g in group_results_by_die(results_data))
    return bool(rows_for_format(fmt, results_data))
