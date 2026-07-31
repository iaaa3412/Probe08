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
    slot: Optional[int] = None


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
         "signature": i.signature, "usb_id": i.usb_id, "slot": i.slot}
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
            slot=row.get("slot"),
        )
        for row in rows
    ]


LEGACY_RECIPE_FILENAME = "ata_nanoz_recipe.json"
RECIPES_FILENAME = "ata_nanoz_recipes.json"

_RECIPE_SHOT_META_KEYS = ("die_column", "td_start_row", "td_end_row", "board_reasons")


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


def build_shots_from_wafer_plan(plan: "WaferPlan", ports: list, slot_by_port: dict) -> list[dict]:
    """One shot per touchdown, ordered by die column then touchdown index.
    A port is excluded from a shot unless it has an assigned slot that lands
    on a normal product die for that specific touchdown. Each shot also
    records "board_reasons" (port -> reason string, or None if it runs) so
    the decision can be explained/displayed later, independent of whatever
    the manual excluded_boards toggle grid does to it afterwards."""
    shots = []
    for die_col in sorted(plan.columns):
        col = plan.columns[die_col]
        for td_i, (start, end) in enumerate(col.touchdowns, start=1):
            exclusions = touchdown_slot_exclusions(die_col, start, end, plan)
            excluded_boards = set()
            board_reasons = {}
            for port in ports:
                slot = slot_by_port.get(port)
                if slot is None:
                    reason = "no slot assigned"
                else:
                    reason = exclusions.get(slot, "slot beyond probe head height")
                board_reasons[port] = reason
                if reason is not None:
                    excluded_boards.add(port)
            shots.append({
                "label": f"Col {die_col} · TD{td_i} (rows {start}-{end})",
                "excluded_boards": excluded_boards,
                "board_reasons": board_reasons,
                "die_column": die_col, "td_start_row": start, "td_end_row": end,
            })
    return shots


class NanoZBoard:

    def __init__(self, identity: BoardIdentity, out_queue,
                die_provider: Optional[Callable[[], tuple]] = None,
                env_interval_s: float = 1.0):
        self.identity = identity
        self.port = identity.port
        self.out_queue = out_queue
        self._die_provider = die_provider or (lambda: (None, None))
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
        row, col = self._die_provider()
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
        row, col = self._die_provider()
        self.env_count += 1
        self.out_queue.put({
            "kind": "env", "host_timestamp": now_stamp(),
            "board_sn": self.identity.serial_number, "port": self.port,
            "die_row": row, "die_col": col,
            "env_x": env_x, "header_time_ms": header_time, "header_bfr": header_bfr,
            "len": length, "checksum_expected": expected_cs,
            **parsed,
        })
