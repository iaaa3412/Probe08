"""NanoZ EK-IV evaluation board driver — serial (pyserial), not GPIB/VISA.

Protocol logic (port scanning, board identification via ver/whoami, and the
#spl!/#env! binary packet formats) is ported from the reference CLI tool
gds/nanoz_ekiv_run_collect.py, which was written against real hardware and
already documents/handles the on-wire format correctly — this module keeps
that parsing byte-for-byte identical and just restructures it for a GUI:
persistent per-board reader threads that continuously push parsed packets
onto a shared queue.Queue() (see NanoZBoard), instead of one CLI process
collecting a single fixed-duration run for one board.

Multiple boards (up to 6 in the intended setup) each own an independent
COM port at 921600 baud.
"""
from __future__ import annotations

import csv
import datetime as dt
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
#  <cs> is printed in hex by real EK-IV firmware (e.g. "1BA8") even though
#  every other field in the header is decimal -- confirmed against a live
#  board log (COM3: "#env3! 132 1BA8 41794 0"), which the reference
#  script's all-decimal (\d+) regex could not match at all. Every other
#  header field stays \d+ (decimal), matching real captures.
ENV_HEADER_RE = re.compile(rb"#env(\d)!\s+(\d+)\s+([0-9A-Fa-f]+)\s+(\d+)\s+(\d+)\s*$", re.I)
SPL_HEADER_RE = re.compile(rb"#spl!\s+(\d+)\s+([0-9A-Fa-f]+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", re.I)


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


def xor_checksum(data: bytes) -> int:
    cs = 0
    for b in data:
        cs ^= b
    return cs


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
    """Probe `port` with ver/whoami; None if nothing NanoZ-shaped answers."""
    try:
        with open_serial(port) as ser:
            send_ascii(ser, "ver")
            raw_ver = read_text_for(ser, 0.75)
            send_ascii(ser, "whoami")
            raw_whoami = read_text_for(ser, 0.50)
    except Exception:
        return None

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
    """Probe candidate ports (default: every COM port currently on the
    system) and return every one that answers like a NanoZ EK-IV board.
    `log`, if given, is called with a short progress string after each
    port is probed — meant for live GUI feedback during a scan that may
    take a few seconds (each candidate port gets ~1.25s to respond)."""
    candidates = ports if ports is not None else [p.device for p in list_serial_ports()]
    found: list[BoardIdentity] = []
    for port in candidates:
        if log:
            log(f"Probing {port}...")
        ident = identify_on_port(port)
        if ident:
            found.append(ident)
            if log:
                log(f"  -> NanoZ board found: S/N {ident.serial_number}  FW {ident.firmware}")
        elif log:
            log(f"  -> no response")
    return found


def read_line_bytes(ser: serial.Serial, buffer: bytearray, timeout_s: float = 2.0) -> Optional[bytes]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        for sep in (b"\n", b"\r"):
            idx = buffer.find(sep)
            if idx >= 0:
                line = bytes(buffer[:idx]).strip()
                del buffer[: idx + 1]
                if line:
                    return line
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
    # sample_t is 48 bytes in the protocol document.
    # uint32 ppms, uint8 chipID, uint8 sensorMask, uint16 reserved,
    # int16 DAC_Voltage[4], float ADC_Current[4], heater_t heater[2] = 4 floats.
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
    # env_typ is 132 bytes for EK-IV based on the documented C struct.
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


class NanoZBoard:
    """One connected board: owns its serial port and a persistent
    background reader thread that continuously parses #spl!/#env! packets
    and pushes them onto a shared queue.Queue() — Tkinter widgets can only
    be touched from the main thread, so the GUI drains this queue on a
    self.after() poll instead (see gui/nanoz_panel.py's _nanoz_check_queue).

    `die_provider`, if given, is called (with no arguments) at the moment
    each packet is parsed and should return the (row, col) of whichever
    die the prober currently has under test — every packet dict gets
    tagged with it (die_row/die_col), same intent as the reference
    script's "append the current Die X and Die Y coordinates" step.
    """

    def __init__(self, identity: BoardIdentity, out_queue,
                die_provider: Optional[Callable[[], tuple]] = None,
                env_interval_s: float = 1.0):
        self.identity = identity
        self.port = identity.port
        self.out_queue = out_queue
        self._die_provider = die_provider or (lambda: (None, None))
        self.env_interval_s = env_interval_s
        self.selected = True
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

    def connect(self):
        if self.ser is None:
            self.ser = open_serial(self.port)

    def start(self):
        """Open the port (if needed), make sure the board isn't already
        mid-cycle from an earlier session, then start the persistent
        reader thread.

        An active cycle keeps streaming unsolicited #spl!/#env! binary
        blocks on its own schedule. If the reader thread starts reading
        before it's synchronized to a clean header boundary, a stray
        \\r/\\n byte that happens to occur inside that binary data gets
        misread by read_line_bytes as a text line terminator — the bytes
        around it then get decoded as "text" and show up as illegible
        garbage in the log. Sending pause first stops any in-progress
        cycle so the board goes quiet before we start listening; the
        buffer reset afterward drops whatever partial/unsynced bytes
        arrived in that window (harmless — at most a "Cycle completed"
        or "no cycle running" status line) so the reader thread's first
        read starts from a clean boundary."""
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

    def run_cycle(self, cycle: int):
        """'run <cycle>' — trigger the heaters for this die's touchdown."""
        if self.ser:
            send_ascii(self.ser, f"run {cycle}")

    def pause(self):
        """'pause' — halt the heaters (end of a touchdown, or teardown)."""
        if self.ser:
            send_ascii(self.ser, "pause")

    def send_raw(self, cmd: str):
        """Send an arbitrary ASCII command from the protocol reference
        (ver, whoami, #env?, calib!, calib ?, cleep, or a manual run/pause
        for isolated testing outside a full lot — see the NanoZ Protocol
        doc under references/). Any reply arrives asynchronously through
        the normal reader thread/queue as a "text" packet, same as every
        other status line (see _reader_loop) — there is no separate
        synchronous read here, since the reader thread already owns the
        port and a second concurrent read would race it."""
        if self.ser:
            send_ascii(self.ser, cmd)

    def stop(self):
        """Stop the reader thread and close the port."""
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

    # ── Background reader thread ────────────────────────────────────────

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
            if not line.startswith(b"#"):
                text = line.decode(errors="replace")
                self.out_queue.put({
                    "kind": "text", "board_sn": self.identity.serial_number,
                    "port": self.port, "text": text, "host_timestamp": now_stamp(),
                })
                continue
            sm = SPL_HEADER_RE.match(line)
            if sm:
                self._handle_spl(sm)
                continue
            em = ENV_HEADER_RE.match(line)
            if em:
                self._handle_env(em)
                continue
            self.out_queue.put({
                "kind": "unrecognized", "board_sn": self.identity.serial_number,
                "port": self.port, "raw": line, "host_timestamp": now_stamp(),
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
        cs_ok = xor_checksum(data) == expected_cs
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
            "checksum_expected": expected_cs, "checksum_ok": cs_ok,
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
        cs_ok = xor_checksum(data) == expected_cs
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
            "len": length, "checksum_expected": expected_cs, "checksum_ok": cs_ok,
            **parsed,
        })
