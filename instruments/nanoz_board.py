from __future__ import annotations

import csv
import datetime as dt
import json
import re
import struct
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import serial
from serial.tools import list_ports

BAUD = 921600
READ_TIMEOUT_S = 0.05

VER_RE = re.compile(r"SW:(V[^\s]+).*?S/N:\s*([0-9A-Fa-f]+-[0-9A-Fa-f]+)", re.S)
WHOAMI_RE = re.compile(r"Iam\s+([0-9A-Fa-f]+)", re.I)
ENV_HEADER_RE = re.compile(rb"#env(\d)!\s+(\d+)\s+([0-9A-Fa-f]+)\s+(\d+)\s+(\d+)\s*$", re.I)
SPL_HEADER_RE = re.compile(rb"#spl!\s+(\d+)\s+([0-9A-Fa-f]+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", re.I)
SEQ_HEADER_RE = re.compile(rb"#seq!\s+(-?\d+)\s+(-?\d+)\s*$", re.I)
EEP_HEADER_RE = re.compile(rb"#eep!\s+(\d+)\s+([0-9A-Fa-f]+)\s+(\d+)\s*$", re.I)


class NanoZError(RuntimeError):
    pass


@dataclass
class PortMeta:
    device: str
    description: str
    hwid: str
    serial_number: str
    vid_pid: str
    location: str


@dataclass
class BoardIdentity:
    port: str
    serial_number: str
    firmware: str
    signature: str
    raw_ver: str
    raw_whoami: str
    usb_id: str
    slot0: Optional[int] = None  # physical probe-head slot (1..N) wired to chip 0
    slot1: Optional[int] = None  # physical probe-head slot (1..N) wired to chip 1

    def chip_slots(self) -> dict:
        return {"0": self.slot0, "1": self.slot1}


def now_stamp() -> str:
    return dt.datetime.now().isoformat(timespec="milliseconds")


def list_serial_ports() -> list[PortMeta]:
    out: list[PortMeta] = []
    for p in sorted(list_ports.comports(), key=lambda x: x.device):
        vid_pid = ""
        if p.vid is not None and p.pid is not None:
            vid_pid = f"{p.vid:04X}:{p.pid:04X}"
        out.append(
            PortMeta(
                device=p.device,
                description=p.description or "",
                hwid=p.hwid or "",
                serial_number=p.serial_number or "",
                vid_pid=vid_pid,
                location=p.location or "",
            )
        )
    return out


def open_serial(port: str) -> serial.Serial:
    ser = serial.Serial(
        port=port,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=READ_TIMEOUT_S,
        write_timeout=1.0,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
    )
    time.sleep(0.2)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser


def send_ascii(ser: serial.Serial, cmd: str) -> None:
    if not cmd.endswith("\r"):
        cmd += "\r"
    ser.write(cmd.encode("ascii"))
    ser.flush()


def read_text_for(ser: serial.Serial, seconds: float) -> str:
    deadline = time.time() + seconds
    data = bytearray()
    while time.time() < deadline:
        chunk = ser.read(4096)
        if chunk:
            data.extend(chunk)
        else:
            time.sleep(0.01)
    return data.decode(errors="replace").strip()


def identify_on_port(port: str) -> Optional[BoardIdentity]:
    ser = open_serial(port)
    try:
        send_ascii(ser, "ver")
        raw_ver = read_text_for(ser, 0.75)
        send_ascii(ser, "whoami")
        raw_whoami = read_text_for(ser, 0.50)
    except Exception:
        return None
    finally:
        ser.close()

    m = VER_RE.search(raw_ver)
    if not m:
        return None

    firmware, sn = m.group(1), m.group(2).upper()
    wm = WHOAMI_RE.search(raw_whoami)
    signature = wm.group(1) if wm else ""

    usb_id = ""
    for p in list_serial_ports():
        if p.device.upper() == port.upper():
            usb_id = p.serial_number or f"VIDPID={p.vid_pid};LOC={p.location};PORT={p.device}"
            break

    return BoardIdentity(
        port=port,
        serial_number=sn,
        firmware=firmware,
        signature=signature,
        raw_ver=raw_ver,
        raw_whoami=raw_whoami,
        usb_id=usb_id,
    )


def discover_boards(ports: Optional[list[str]] = None,
                    log: Optional[Callable[[str], None]] = None) -> list[BoardIdentity]:
    candidates = ports if ports is not None else [p.device for p in list_serial_ports()]
    found: list[BoardIdentity] = []
    for port in candidates:
        if log:
            log(f"Probing {port}...")
        try:
            ident = identify_on_port(port)
        except Exception as e:
            if log:
                log(f"  -> could not open ({e}) - in use by another program?")
            continue
        if ident:
            found.append(ident)
            if log:
                log(f"  -> NanoZ board found: S/N {ident.serial_number}  FW {ident.firmware}")
        elif log:
            log(f"  -> no response (not a NanoZ board, or powered off)")
    return found


def read_line_bytes(ser: serial.Serial, buffer: bytearray, timeout_s: float = 2.0) -> Optional[bytes]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        idx = buffer.find(b"\n")
        if idx >= 0:
            line = bytes(buffer[:idx]).strip(b"\r\n ")
            del buffer[: idx + 1]
            if line:
                return line
            continue
        chunk = ser.read(4096)
        if chunk:
            buffer.extend(chunk)
        else:
            time.sleep(0.005)
    return None


def read_exact_from_buffer(ser: serial.Serial, buffer: bytearray, n: int, timeout_s: float = 2.0) -> bytes:
    deadline = time.time() + timeout_s
    while len(buffer) < n and time.time() < deadline:
        chunk = ser.read(n - len(buffer))
        if chunk:
            buffer.extend(chunk)
        else:
            time.sleep(0.005)
    if len(buffer) < n:
        raise NanoZError(f"Timed out waiting for binary block: needed {n}, got {len(buffer)}")
    data = bytes(buffer[:n])
    del buffer[:n]
    return data


def parse_spl_data(data: bytes) -> dict:
    if len(data) < 48:
        raise NanoZError(f"SPL data block too short: {len(data)} bytes")
    vals = struct.unpack_from("<IBBH4h4f4f", data, 0)
    ppms, chip_id, sensor_mask, reserved = vals[:4]
    dac = vals[4:8]
    adc = vals[8:12]
    heaters = vals[12:16]
    return {
        "ppms": ppms,
        "chip_id": chip_id,
        "sensor_mask": sensor_mask,
        "reserved": reserved,
        "dac_mv_s1": dac[0],
        "dac_mv_s2": dac[1],
        "dac_mv_s3": dac[2],
        "dac_mv_s4": dac[3],
        "adc_current_ma_s1": adc[0],
        "adc_current_ma_s2": adc[1],
        "adc_current_ma_s3": adc[2],
        "adc_current_ma_s4": adc[3],
        "heater1_voltage_mv": heaters[0],
        "heater1_current_ma": heaters[1],
        "heater2_voltage_mv": heaters[2],
        "heater2_current_ma": heaters[3],
    }


def parse_env_data(data: bytes) -> dict:
    if len(data) < 132:
        raise NanoZError(f"ENV data block too short: {len(data)} bytes")
    off = 0
    pps, samples_nb, adc_mask = struct.unpack_from("<IHH", data, off)
    off += 8
    adc_samples = struct.unpack_from("<8H", data, off)
    off += 16
    adc_voltage = struct.unpack_from("<8f", data, off)
    off += 32
    adc_current = struct.unpack_from("<8f", data, off)
    off += 32
    htr_voltage = struct.unpack_from("<4f", data, off)
    off += 16
    adc_mid, mcu_temp = struct.unpack_from("<ff", data, off)
    off += 8
    humidity_x100, tempH_x100, pressure_x10, tempP_x100, pending, align = struct.unpack_from("<6h", data, off)
    off += 12
    age = struct.unpack_from("<2I", data, off)

    return {
        "pps": pps,
        "adc_samples_nb": samples_nb,
        "adc_mask": adc_mask,
        "adc_mid_value": adc_mid,
        "mcu_temperature_c": mcu_temp,
        "humidity_percent": humidity_x100 / 100.0,
        "temp_h_c": tempH_x100 / 100.0,
        "pressure_hpa_minus_1013": pressure_x10 / 10.0,
        "temp_p_c": tempP_x100 / 100.0,
        "pending": pending,
        "align": align,
        "age_chip1_s": age[0],
        "age_chip2_s": age[1],
        "adc_samples_4x2": ";".join(str(x) for x in adc_samples),
        "adc_voltage_4x2": ";".join(f"{x:.6g}" for x in adc_voltage),
        "adc_current_4x2": ";".join(f"{x:.6g}" for x in adc_current),
        "htr_voltage_2x2": ";".join(f"{x:.6g}" for x in htr_voltage),
    }


# EEPROM "Configuration" layout — reverse-engineered live against a real
# EK-IV board and Nanoz_EK.exe (2026-08-04), NOT from any vendor
# documentation (neither reference PDF documents this). Nanoz_EK.exe embeds
# named constants (EEPROM_PARAMS_ADDR, EEPROM_CYCLES_PAGE, etc.) via its own
# Free Pascal RTTI/debug info, but those ADDR constants turned out to be
# red herrings — the real byte address of a section is PAGE * PAGE_SIZE, not
# the ADDR constant itself. Confirmed by diffing a real Sequence Duration
# edit (5s -> 2s) against a live rdeep and finding it land exactly at the
# predicted offset. Cycle-record layout confirmed against 2 real cycles
# (32 bytes apart, matching CYCLE_RECORD_SIZE). Sequence-record layout is
# only confirmed for Duration (offset +2) and Chip (offset +54) - only ONE
# real sequence has ever been observed, so the exact stride between
# consecutive sequence records, and the sub-order of the heater ramp
# fields, are NOT yet confirmed. Read-only so far - no wreep support, since
# writing to an unconfirmed offset could corrupt the board's stored config
# with no way to detect or undo it (see gui/nanoz_panel.py's NanoZ_EK tab).
EEPROM_PAGE_SIZE = 32
EEPROM_PARAMS_ADDR = 0
EEPROM_CYCLES_PAGE = 16
EEPROM_CYCLES_ADDR = EEPROM_CYCLES_PAGE * EEPROM_PAGE_SIZE       # 512
EEPROM_SEQUENCES_PAGE = 64
EEPROM_SEQUENCES_ADDR = EEPROM_SEQUENCES_PAGE * EEPROM_PAGE_SIZE  # 2048
EEPROM_CYCLE_RECORD_SIZE = 32
MAX_CYCLES_NB = 48
MAX_SEQUENCE_NB = 96


def parse_params_block(data: bytes) -> dict:
    """Decode the EEPROM_PARAMS_ADDR (0) region: device signature, cycle
    count, periodicity, the board's own CAL-1/CAL-2 calibration offsets
    (same values `calib ?` reports), and the two installed chips'
    identity/age records. Confirmed field-for-field against Nanoz_EK.exe's
    own display (Signature, CAL-1/CAL-2, and the "ID:"/"Age:" fields, whose
    "D{W}L{X}-{Y}-{Z}" format matches this decode's w/x/y/z exactly)."""
    if len(data) < 152:
        raise NanoZError(f"PARAMS block too short: {len(data)} bytes (need >= 152)")
    signature = struct.unpack_from("<H", data, 0)[0]
    cycles_configured = struct.unpack_from("<H", data, 4)[0]
    periodicity_ms = data[14]
    cal1, cal2 = struct.unpack_from("<ff", data, 20)

    def chip_record(off):
        w, x, y, z, age_s = struct.unpack_from("<5I", data, off)
        return {"w": w, "x": x, "y": y, "z": z, "age_s": age_s,
               "id": f"D{w}L{x}-{y}-{z}"}

    return {
        "signature": f"0x{signature:04X}",
        "cycles_configured": cycles_configured,
        "periodicity_ms": periodicity_ms,
        "cal1": cal1,
        "cal2": cal2,
        "chip1": chip_record(112),
        "chip2": chip_record(132),
    }


def parse_cycle_record(data: bytes) -> "dict | None":
    """Decode one EEPROM_CYCLE_RECORD_SIZE-byte (32) cycle record. Returns
    None if it's erased/unused (all 0xFF). wire_index is 0-based - Nanoz_EK's
    UI "Cycle 1"/"Cycle 2" are wire index 0/1 (same off-by-one as `run <nn>`,
    confirmed against the manual's error text for an out-of-range index)."""
    if len(data) < EEPROM_CYCLE_RECORD_SIZE:
        raise NanoZError(f"Cycle record too short: {len(data)} bytes")
    if all(b == 0xFF for b in data[:EEPROM_CYCLE_RECORD_SIZE]):
        return None
    wire_index, num_sequences = struct.unpack_from("<HH", data, 0)
    seq_refs = []
    off = 4
    for _ in range(min(num_sequences, (EEPROM_CYCLE_RECORD_SIZE - 4) // 4)):
        seq_refs.append(struct.unpack_from("<I", data, off)[0])
        off += 4
    return {"wire_index": wire_index, "num_sequences": num_sequences,
           "sequence_refs": seq_refs}


def parse_sequence_records(data: bytes) -> list:
    """Best-effort scan of the EEPROM_SEQUENCES_ADDR region for sequence
    records, each terminated by a 0xFFFF marker. Only Duration (int16 at
    record offset +2) and Chip (int16 at +54) are confirmed; every other
    field in a record is returned as raw bytes (hex) rather than guessed,
    since the exact sub-order of the heater ramp fields and the true record
    stride are not yet confirmed against real hardware (only 1 real
    sequence has ever been observed)."""
    records = []
    start = 0
    n = len(data)
    while start < n:
        if data[start] == 0xFF and (start + 1 >= n or data[start + 1] == 0xFF):
            break  # ran into erased/unused space - no more records
        term = data.find(b"\xff\xff", start)
        if term == -1:
            end = n
        else:
            end = term + 2
        record = data[start:end]
        if len(record) >= 4:
            wire_index = struct.unpack_from("<H", record, 0)[0]
            duration_s = struct.unpack_from("<h", record, 2)[0]
            chip = (struct.unpack_from("<h", record, 54)[0]
                   if len(record) >= 56 else None)
            records.append({
                "wire_index": wire_index,
                "duration_s": duration_s,
                "chip": chip,
                "raw_hex": record.hex(),
            })
        start = end
    return records


def append_csv_row(path, row: dict) -> None:
    path = Path(path)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


BOARDS_MEMORY_FILENAME = "ata_nanoz_boards.json"


def save_known_boards(folder, identities: list) -> None:
    path = Path(folder) / BOARDS_MEMORY_FILENAME
    rows = [
        {"port": i.port, "serial_number": i.serial_number, "firmware": i.firmware,
         "signature": i.signature, "usb_id": i.usb_id, "slot0": i.slot0, "slot1": i.slot1}
        for i in identities
    ]
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def load_known_boards(folder) -> list[BoardIdentity]:
    path = Path(folder) / BOARDS_MEMORY_FILENAME
    if not path.is_file():
        return []
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [
        BoardIdentity(
            port=row.get("port", ""), serial_number=row.get("serial_number", ""),
            firmware=row.get("firmware", ""), signature=row.get("signature", ""),
            raw_ver="", raw_whoami="", usb_id=row.get("usb_id", ""),
            # Legacy single-slot files (pre-two-chip-per-board) had "slot" -> migrate to slot0.
            slot0=row.get("slot0", row.get("slot")),
            slot1=row.get("slot1"),
        )
        for row in rows
    ]


LEGACY_RECIPE_FILENAME = "ata_nanoz_recipe.json"
RECIPES_FILENAME = "ata_nanoz_recipes.json"

_RECIPE_SHOT_META_KEYS = ("die_column", "td_start_row", "td_end_row", "board_reasons",
                          "chip_reasons")


def _shots_to_rows(shots: list) -> list:
    rows = []
    for s in shots:
        row = {"label": s.get("label", ""), "excluded_boards": sorted(s.get("excluded_boards", ()))}
        for k in _RECIPE_SHOT_META_KEYS:
            if k in s:
                row[k] = s[k]
        rows.append(row)
    return rows


def _rows_to_shots(rows: list) -> list[dict]:
    shots = []
    for s in rows:
        if not isinstance(s, dict):
            continue
        shot = {"label": s.get("label", ""), "excluded_boards": set(s.get("excluded_boards", ()))}
        for k in _RECIPE_SHOT_META_KEYS:
            if k in s:
                shot[k] = s[k]
        shots.append(shot)
    return shots


def _load_recipes_file(folder) -> dict:
    path = Path(folder) / RECIPES_FILENAME
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data.get("recipes"), dict):
                data.setdefault("active", None)
                return data
        except (OSError, ValueError):
            pass
    return {"active": None, "recipes": {}}


def _write_recipes_file(folder, data: dict) -> None:
    path = Path(folder) / RECIPES_FILENAME
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_recipe_names(folder) -> list[str]:
    return sorted(_load_recipes_file(folder)["recipes"].keys())


def get_active_recipe_name(folder):
    return _load_recipes_file(folder).get("active")


def save_named_recipe(folder, name: str, shots: list, wafer_plan_path: str | None = None) -> None:
    data = _load_recipes_file(folder)
    data["recipes"][name] = _shots_to_rows(shots)
    data["active"] = name
    if wafer_plan_path:
        data.setdefault("wafer_plan_paths", {})[name] = wafer_plan_path
    _write_recipes_file(folder, data)


def load_named_recipe(folder, name: str) -> list[dict]:
    rows = _load_recipes_file(folder)["recipes"].get(name)
    return _rows_to_shots(rows) if rows is not None else []


def get_recipe_wafer_plan_path(folder, name: str) -> str | None:
    """The source .xlsx path a named recipe's shots were generated from, if any
    was recorded — lets the GUI auto-reload the wafer map alongside the recipe."""
    return _load_recipes_file(folder).get("wafer_plan_paths", {}).get(name)


def set_active_recipe(folder, name: str) -> None:
    data = _load_recipes_file(folder)
    if name in data["recipes"]:
        data["active"] = name
        _write_recipes_file(folder, data)


def delete_named_recipe(folder, name: str) -> None:
    data = _load_recipes_file(folder)
    data["recipes"].pop(name, None)
    data.get("wafer_plan_paths", {}).pop(name, None)
    if data.get("active") == name:
        data["active"] = None
    _write_recipes_file(folder, data)


def load_active_recipe(folder):
    """Returns (name, shots, wafer_plan_path) for the last-saved/loaded recipe,
    or (None, [], None)."""
    data = _load_recipes_file(folder)
    name = data.get("active")
    if not name or name not in data["recipes"]:
        return None, [], None
    wafer_plan_path = data.get("wafer_plan_paths", {}).get(name)
    return name, _rows_to_shots(data["recipes"][name]), wafer_plan_path


def migrate_legacy_recipe(folder):
    """One-time migration of the old single-recipe file (pre-naming) into the
    named scheme, under the name 'Imported'. Returns the name if it migrated
    something, else None. No-op if any named recipe already exists."""
    legacy_path = Path(folder) / LEGACY_RECIPE_FILENAME
    if not legacy_path.is_file() or _load_recipes_file(folder)["recipes"]:
        return None
    try:
        legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    shots = _rows_to_shots(legacy.get("shots", []))
    if not shots:
        return None
    save_named_recipe(folder, "Imported", shots)
    return "Imported"


# ── Wafer-plan (.xlsx) import ───────────────────────────────────────────────
# Parses a Nautilus-style wafer-plan workbook ("Shot Map" / "Probe Plan" /
# "Reference Dies" sheets) into the geometry needed to auto-generate the
# NanoZ recipe: which of the probe head's slots (1..probe_height, top to
# bottom) land on a real product die, a reference/monitor die, or off the
# wafer entirely, for every touchdown of every die column.

try:
    import openpyxl
    _OPENPYXL_AVAILABLE = True
except ImportError:
    _OPENPYXL_AVAILABLE = False

# Fixed local-position pattern (row, col within a 5x5 shot, 1-based) that is
# a reference/monitor die on every reference shot in a Nautilus wafer plan -
# see the workbook's own "Reference Dies" sheet for the source description.
REFERENCE_LOCAL_POSITIONS = frozenset({
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
    (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
    (3, 1),
    (4, 1), (4, 2),
})


@dataclass
class WaferPlanColumn:
    die_column: int
    top_valid_row: int
    bottom_valid_row: int
    touchdowns: list  # list[tuple[int, int]] of (start_row, end_row), 1-based inclusive


@dataclass
class WaferPlan:
    probe_height: int
    dies_per_shot: int
    columns: dict  # die_column -> WaferPlanColumn
    reference_shots: set  # {(shot_row, shot_col), ...}


def load_wafer_plan(path) -> WaferPlan:
    if not _OPENPYXL_AVAILABLE:
        raise NanoZError("openpyxl is required to import a wafer plan .xlsx (pip install openpyxl)")

    wb = openpyxl.load_workbook(path, data_only=True)
    for name in ("Shot Map", "Probe Plan", "Reference Dies"):
        if name not in wb.sheetnames:
            raise NanoZError(f"'{name}' sheet not found — not a recognized wafer-plan workbook.")

    shot_ws = wb["Shot Map"]
    shots_across = shot_ws.cell(row=1, column=2).value
    if not isinstance(shots_across, int) or shots_across <= 0:
        raise NanoZError("Shot Map!B1 ('Shots across') is missing or not a number.")

    pp_ws = wb["Probe Plan"]
    probe_height = pp_ws.cell(row=2, column=2).value
    if not isinstance(probe_height, int) or probe_height <= 0:
        raise NanoZError("Probe Plan!B2 ('Probe height (dies)') is missing or not a number.")

    columns: dict[int, WaferPlanColumn] = {}
    max_die_col = 0
    for row in pp_ws.iter_rows(min_row=5, values_only=True):
        die_col = row[0] if row else None
        if not isinstance(die_col, int):
            continue
        top_valid, bottom_valid = row[2], row[3]
        touchdowns = []
        for i in range(6, len(row) - 1, 2):
            start, end = row[i], row[i + 1]
            if start is None or end is None:
                break
            touchdowns.append((int(start), int(end)))
        if not touchdowns:
            continue
        columns[die_col] = WaferPlanColumn(die_col, int(top_valid), int(bottom_valid), touchdowns)
        max_die_col = max(max_die_col, die_col)

    if not columns:
        raise NanoZError("Probe Plan: no die-column rows found.")

    dies_per_shot = round(max_die_col / shots_across)
    if dies_per_shot <= 0:
        raise NanoZError("Could not determine dies-per-shot from Shot Map / Probe Plan.")
    if dies_per_shot != 5:
        raise NanoZError(
            f"This wafer plan uses {dies_per_shot}x{dies_per_shot}-die shots, but the "
            f"reference-die local-position pattern is only known for 5x5 shots — "
            f"refusing to guess which dies within a reference shot to skip.")

    ref_ws = wb["Reference Dies"]
    reference_shots = set()
    header_row = None
    for i, row in enumerate(ref_ws.iter_rows(values_only=True), start=1):
        if row and row[0] == "Serial (top-left die)":
            header_row = i
            break
    if header_row is None:
        raise NanoZError("Reference Dies: could not find the data header row.")
    for row in ref_ws.iter_rows(min_row=header_row + 1, values_only=True):
        if not row or len(row) < 5:
            continue
        _serial, _die_row, _die_col, shot_row, shot_col = row[:5]
        if isinstance(shot_row, int) and isinstance(shot_col, int):
            reference_shots.add((shot_row, shot_col))

    return WaferPlan(probe_height=probe_height, dies_per_shot=dies_per_shot,
                     columns=columns, reference_shots=reference_shots)


def classify_die(plan: "WaferPlan", row: int, col: int) -> str:
    """Returns 'product', 'reference', or 'off_wafer' for a given (row, col)."""
    col_info = plan.columns.get(col)
    if col_info is None or row < col_info.top_valid_row or row > col_info.bottom_valid_row:
        return "off_wafer"
    shot_row = (row - 1) // plan.dies_per_shot + 1
    shot_col = (col - 1) // plan.dies_per_shot + 1
    if (shot_row, shot_col) in plan.reference_shots:
        local_row = (row - 1) % plan.dies_per_shot + 1
        local_col = (col - 1) % plan.dies_per_shot + 1
        if (local_row, local_col) in REFERENCE_LOCAL_POSITIONS:
            return "reference"
    return "product"


def touchdown_slot_exclusions(die_col: int, start_row: int, end_row: int, plan: "WaferPlan") -> dict:
    """Slot (1..probe_height, top to bottom of this touchdown) -> exclusion reason,
    or None if that slot lands on a normal product die that should be run."""
    result = {}
    for slot in range(1, plan.probe_height + 1):
        physical_row = start_row + slot - 1
        if physical_row > end_row:
            result[slot] = "past touchdown end"
            continue
        status = classify_die(plan, physical_row, die_col)
        result[slot] = {"off_wafer": "off wafer", "reference": "reference die",
                        "product": None}[status]
    return result


def wafer_plan_die_grid(plan: "WaferPlan") -> list[dict]:
    """Every on-wafer die (product or reference) as {row, col, status, serial}."""
    if not plan.columns:
        return []
    max_row = max(c.bottom_valid_row for c in plan.columns.values())
    dies = []
    for col in sorted(plan.columns):
        for row in range(1, max_row + 1):
            status = classify_die(plan, row, col)
            if status != "off_wafer":
                dies.append({"row": row, "col": col, "status": status,
                            "serial": die_serial(row, col)})
    return dies


# Letters/numbers scheme for the Nautilus wafer plan's LL### die serials
# (see the workbook's own "Serial Reference" sheet) - verified against two
# real entries from "Reference Dies" (row=11,col=51 -> AL056; row=51,col=51
# -> CE056).
_SERIAL_LETTERS = "ABCDEFGHJKLMNPRSTUVWXYZ"  # 23 letters, I/O/Q excluded
_SERIAL_VALID_NUMS = [n for n in range(1, 117) if n % 10 != 0]  # 105 values, 1..116


def die_serial(row: int, col: int) -> str:
    r_idx = row - 1
    first, second = divmod(r_idx, len(_SERIAL_LETTERS))
    letters = _SERIAL_LETTERS[first % len(_SERIAL_LETTERS)] + _SERIAL_LETTERS[second]
    num = (_SERIAL_VALID_NUMS[col - 1] if 1 <= col <= len(_SERIAL_VALID_NUMS) else col)
    return f"{letters}{num:03d}"


def wafer_plan_stats(plan: "WaferPlan") -> dict:
    counts = {"product": 0, "reference": 0, "off_wafer": 0}
    for die_col, col in plan.columns.items():
        for start, end in col.touchdowns:
            for reason in touchdown_slot_exclusions(die_col, start, end, plan).values():
                if reason is None:
                    counts["product"] += 1
                elif reason == "reference die":
                    counts["reference"] += 1
                else:
                    counts["off_wafer"] += 1
    return counts


def build_shots_from_wafer_plan(plan: "WaferPlan", ports: list, slots_by_port: dict) -> list[dict]:
    """One shot per touchdown, ordered by die column then touchdown index.

    Each NanoZ board has two independent chips (0 and 1), each wired to its
    own physical probe-head slot — `slots_by_port[port]` is a {"0": slot_or_None,
    "1": slot_or_None} dict (see BoardIdentity.chip_slots()). A `run <nn>`
    always actuates both chips together (confirmed in the vendor manual, no
    per-chip run command exists), so a board is only excluded from a shot if
    BOTH of its chips land off a normal product die for that touchdown —
    if at least one chip has a real die there, the board still needs to run.
    "chip_reasons" (port -> {"0": reason_or_None, "1": reason_or_None}) records
    the per-chip detail for display/filtering; "board_reasons" (port -> reason
    string, or None if it runs) is the board-level summary, independent of
    whatever the manual excluded_boards toggle grid does to it afterwards."""
    shots = []
    for die_col in sorted(plan.columns):
        col = plan.columns[die_col]
        for td_i, (start, end) in enumerate(col.touchdowns, start=1):
            exclusions = touchdown_slot_exclusions(die_col, start, end, plan)
            excluded_boards = set()
            board_reasons = {}
            chip_reasons = {}
            for port in ports:
                chip_slots = slots_by_port.get(port) or {}
                per_chip = {}
                for chip in ("0", "1"):
                    slot = chip_slots.get(chip)
                    if slot is None:
                        per_chip[chip] = "no slot assigned"
                    else:
                        per_chip[chip] = exclusions.get(slot, "slot beyond probe head height")
                chip_reasons[port] = per_chip
                if all(r is not None for r in per_chip.values()):
                    excluded_boards.add(port)
                    board_reasons[port] = "; ".join(
                        f"chip{c}: {r}" for c, r in per_chip.items())
                else:
                    board_reasons[port] = None
            shots.append({
                "label": f"Col {die_col} · TD{td_i} (rows {start}-{end})",
                "excluded_boards": excluded_boards,
                "board_reasons": board_reasons,
                "chip_reasons": chip_reasons,
                "die_column": die_col, "td_start_row": start, "td_end_row": end,
            })
    return shots


class NanoZBoard:

    def __init__(self, identity: BoardIdentity, out_queue,
                die_provider: Optional[Callable[[Optional[str]], tuple]] = None,
                env_interval_s: float = 1.0):
        self.identity = identity
        self.port = identity.port
        self.out_queue = out_queue
        # die_provider(chip) -> (row, col); chip is "0"/"1" for a per-chip SPL
        # reading, or None for a board-wide ENV reading.
        self._die_provider = die_provider or (lambda chip: (None, None))
        self.env_interval_s = env_interval_s
        self.ser: Optional[serial.Serial] = None
        self._buffer = bytearray()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self.spl_count = 0
        self.env_count = 0
        self.last_error = ""

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def state(self) -> str:
        if self._running and self.last_error:
            return "error"
        if self._running:
            return "connected"
        return "not_connected"

    def connect(self):
        if self.ser is None:
            self.ser = open_serial(self.port)

    def start(self):
        self.last_error = ""
        self.connect()
        try:
            send_ascii(self.ser, "pause")
            time.sleep(0.2)
            self.ser.reset_input_buffer()
        except Exception:
            pass
        self._running = True
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def reconnect(self):
        self.stop()
        self.start()

    def run_cycle(self, cycle: int):
        if self.ser:
            send_ascii(self.ser, f"run {cycle}")

    def pause(self):
        if self.ser:
            send_ascii(self.ser, "pause")

    def request_eeprom(self, addr: int, length: int):
        """Read-only: request a raw non-volatile-memory block (rdeep). The
        response arrives asynchronously as a "kind": "eep" item on
        out_queue, decoded by _handle_eep. Does not actuate anything on the
        board - safe to call at any time, including mid-cycle."""
        if self.ser:
            send_ascii(self.ser, f"rdeep {addr} {length}")

    def send_raw(self, cmd: str):
        if self.ser:
            send_ascii(self.ser, cmd)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None


    def _reader_loop(self):
        next_env = time.time() + self.env_interval_s if self.env_interval_s > 0 else float("inf")
        while self._running:
            try:
                if self.env_interval_s > 0 and time.time() >= next_env:
                    send_ascii(self.ser, "#env?")
                    next_env = time.time() + self.env_interval_s
                line = read_line_bytes(self.ser, self._buffer, timeout_s=0.2)
            except Exception as e:
                self.last_error = str(e)
                time.sleep(0.2)
                continue
            if line is None:
                continue
            self.last_error = ""
            if not line.startswith(b"#") or line.startswith(b"##"):
                self._emit_text(line)
                continue
            sm = SPL_HEADER_RE.match(line)
            if sm:
                self._handle_spl(sm)
                continue
            em = ENV_HEADER_RE.match(line)
            if em:
                self._handle_env(em)
                continue
            eepm = EEP_HEADER_RE.match(line)
            if eepm:
                self._handle_eep(eepm)
                continue
            if SEQ_HEADER_RE.match(line):
                self._emit_text(line)
                continue
            self.out_queue.put({
                "kind": "unrecognized", "board_sn": self.identity.serial_number,
                "port": self.port, "raw": line, "host_timestamp": now_stamp(),
            })

    def _emit_text(self, line: bytes):
        self.out_queue.put({
            "kind": "text", "board_sn": self.identity.serial_number,
            "port": self.port, "text": line.decode(errors="replace"),
            "host_timestamp": now_stamp(),
        })

    def _handle_spl(self, m):
        length_s, cs_s, chip_s, time_s, bfr_s = m.groups()
        length, header_chip, header_time, header_bfr = (
            int(length_s), int(chip_s), int(time_s), int(bfr_s))
        expected_cs = int(cs_s, 16)
        try:
            data = read_exact_from_buffer(self.ser, self._buffer, length, timeout_s=2.0)
        except NanoZError as e:
            self.last_error = str(e)
            return
        try:
            parsed = parse_spl_data(data)
        except Exception as e:
            parsed = {"parse_error": str(e)}
        row, col = self._die_provider(str(header_chip))
        self.spl_count += 1
        self.out_queue.put({
            "kind": "spl", "host_timestamp": now_stamp(),
            "board_sn": self.identity.serial_number, "port": self.port,
            "die_row": row, "die_col": col,
            "header_chip": header_chip, "header_time_ms": header_time,
            "header_bfr": header_bfr, "len": length,
            "checksum_expected": expected_cs,
            **parsed,
        })

    def _handle_env(self, m):
        x_s, length_s, cs_s, time_s, bfr_s = m.groups()
        env_x, length, header_time, header_bfr = (
            int(x_s), int(length_s), int(time_s), int(bfr_s))
        expected_cs = int(cs_s, 16)
        try:
            data = read_exact_from_buffer(self.ser, self._buffer, length, timeout_s=2.0)
        except NanoZError as e:
            self.last_error = str(e)
            return
        try:
            parsed = parse_env_data(data)
        except Exception as e:
            parsed = {"parse_error": str(e)}
        row, col = self._die_provider(None)
        self.env_count += 1
        self.out_queue.put({
            "kind": "env", "host_timestamp": now_stamp(),
            "board_sn": self.identity.serial_number, "port": self.port,
            "die_row": row, "die_col": col,
            "env_x": env_x, "header_time_ms": header_time, "header_bfr": header_bfr,
            "len": length, "checksum_expected": expected_cs,
            **parsed,
        })

    def _handle_eep(self, m):
        length_s, cs_s, addr_s = m.groups()
        length, addr = int(length_s), int(addr_s)
        expected_cs = int(cs_s, 16)
        try:
            data = read_exact_from_buffer(self.ser, self._buffer, length, timeout_s=2.0)
        except NanoZError as e:
            self.last_error = str(e)
            return
        actual_cs = 0
        for b in data:
            actual_cs ^= b
        self.out_queue.put({
            "kind": "eep", "host_timestamp": now_stamp(),
            "board_sn": self.identity.serial_number, "port": self.port,
            "addr": addr, "len": length,
            "checksum_expected": expected_cs, "checksum_actual": actual_cs,
            "checksum_ok": actual_cs == expected_cs,
            "data_hex": data.hex(),
        })
