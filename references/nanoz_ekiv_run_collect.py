#!/usr/bin/env python3
"""
nanoz_ekiv_run_collect.py

Run a stored NanoZ EK-IV cycle on a specific board and collect SPL/ENV data to CSV.

This script DOES NOT write a .nnz configuration to the board. It assumes the test/cycle
has already been written to the EK-IV with the Nanoz_EK software, or was already stored
in the board's non-volatile memory.

Safe workflow:
  1) Use Nanoz_EK to Load from disk the supplied .nnz file.
  2) Press Write to Device for board 09.
  3) Close Nanoz_EK so Python can open the COM port.
  4) Run this script.

Examples:
  python nanoz_ekiv_run_collect.py --list
  python nanoz_ekiv_run_collect.py --port COM9 --identify
  python nanoz_ekiv_run_collect.py --sn 0002-0009 --cycle 1 --duration 60 --start

Requires:
  pip install pyserial
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import serial
from serial.tools import list_ports

BAUD = 921600
READ_TIMEOUT_S = 0.05
BOARD_09_SN = "0002-0009"

VER_RE = re.compile(r"SW:(V[^\s]+).*?S/N:\s*([0-9A-Fa-f]+-[0-9A-Fa-f]+)", re.S)
WHOAMI_RE = re.compile(r"Iam\s+([0-9A-Fa-f]+)", re.I)
ENV_HEADER_RE = re.compile(rb"#env(\d)!\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", re.I)
SPL_HEADER_RE = re.compile(rb"#spl!\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", re.I)


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


class NanoZError(RuntimeError):
    pass


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


def print_ports() -> None:
    print("\nDetected serial ports:")
    print("-" * 120)
    print(f"{'Port':10} {'USB Serial':18} {'VID:PID':10} {'Location':15} {'Description'}")
    print("-" * 120)
    for p in list_serial_ports():
        print(f"{p.device:10} {p.serial_number:18} {p.vid_pid:10} {p.location:15} {p.description}")
    print("-" * 120)


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


def find_port_by_sn(target_sn: str) -> BoardIdentity:
    target_sn = target_sn.upper()
    found: list[BoardIdentity] = []
    for p in list_serial_ports():
        ident = identify_on_port(p.device)
        if ident:
            found.append(ident)
            if ident.serial_number == target_sn:
                return ident

    print("\nScanned boards:")
    for b in found:
        print(f"  {b.port:10} {b.serial_number:12} FW={b.firmware} SIG={b.signature} USB={b.usb_id}")
    raise NanoZError(f"Could not find NanoZ board with S/N {target_sn}")


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


def parse_spl_data(data: bytes) -> dict[str, float | int]:
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


def parse_env_data(data: bytes) -> dict[str, float | int]:
    # env_typ is 132 bytes for EK-IV based on the documented C struct.
    # This parser handles at least the documented first 132 bytes.
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
        # Keep the arrays as compact string fields for CSV readability.
        "adc_samples_4x2": ";".join(str(x) for x in adc_samples),
        "adc_voltage_4x2": ";".join(f"{x:.6g}" for x in adc_voltage),
        "adc_current_4x2": ";".join(f"{x:.6g}" for x in adc_current),
        "htr_voltage_2x2": ";".join(f"{x:.6g}" for x in htr_voltage),
    }


def append_csv_row(path: Path, row: dict) -> None:
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def collect_run(
    port: str,
    sn: str,
    cycle: int,
    duration_s: float,
    outdir: Path,
    env_interval_s: float,
    pause_at_end: bool,
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    run_id = dt.datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{sn.replace('-', '')}"
    spl_csv = outdir / f"nanoz_SPL_{run_id}.csv"
    env_csv = outdir / f"nanoz_ENV_{run_id}.csv"
    raw_log = outdir / f"nanoz_RAW_{run_id}.bin"

    with open_serial(port) as ser, raw_log.open("wb") as raw:
        print(f"Starting board {sn} on {port}, cycle {cycle}, duration {duration_s:g} s")
        send_ascii(ser, f"run {cycle}")

        buffer = bytearray()
        start = time.time()
        next_env = start + env_interval_s if env_interval_s > 0 else float("inf")
        spl_count = 0
        env_count = 0

        try:
            while time.time() - start < duration_s:
                if time.time() >= next_env:
                    send_ascii(ser, "#env?")
                    next_env = time.time() + env_interval_s

                line = read_line_bytes(ser, buffer, timeout_s=0.2)
                if line is None:
                    continue

                raw.write(line + b"\n")

                # Text status line.
                if not line.startswith(b"#"):
                    text = line.decode(errors="replace")
                    print(f"TEXT: {text}")
                    if b"completed" in line.lower() or b"error" in line.lower():
                        # Do not always break on completed; some firmware says completed on pause.
                        pass
                    continue

                sm = SPL_HEADER_RE.match(line)
                if sm:
                    length = int(sm.group(1))
                    expected_cs = int(sm.group(2))
                    header_chip = int(sm.group(3))
                    header_time = int(sm.group(4))
                    header_bfr = int(sm.group(5))
                    data = read_exact_from_buffer(ser, buffer, length, timeout_s=2.0)
                    raw.write(data)
                    cs_ok = xor_checksum(data) == expected_cs
                    try:
                        parsed = parse_spl_data(data)
                    except Exception as e:
                        parsed = {"parse_error": str(e)}
                    row = {
                        "host_timestamp": now_stamp(),
                        "board_sn": sn,
                        "port": port,
                        "header_chip": header_chip,
                        "header_time_ms": header_time,
                        "header_bfr": header_bfr,
                        "len": length,
                        "checksum_expected": expected_cs,
                        "checksum_ok": cs_ok,
                        **parsed,
                    }
                    append_csv_row(spl_csv, row)
                    spl_count += 1
                    if spl_count % 10 == 1:
                        print(f"SPL #{spl_count}: chip={row.get('chip_id')} mask={row.get('sensor_mask')} I1={row.get('adc_current_ma_s1')}")
                    continue

                em = ENV_HEADER_RE.match(line)
                if em:
                    env_x = int(em.group(1))
                    length = int(em.group(2))
                    expected_cs = int(em.group(3))
                    header_time = int(em.group(4))
                    header_bfr = int(em.group(5))
                    data = read_exact_from_buffer(ser, buffer, length, timeout_s=2.0)
                    raw.write(data)
                    cs_ok = xor_checksum(data) == expected_cs
                    try:
                        parsed = parse_env_data(data)
                    except Exception as e:
                        parsed = {"parse_error": str(e)}
                    row = {
                        "host_timestamp": now_stamp(),
                        "board_sn": sn,
                        "port": port,
                        "env_x": env_x,
                        "header_time_ms": header_time,
                        "header_bfr": header_bfr,
                        "len": length,
                        "checksum_expected": expected_cs,
                        "checksum_ok": cs_ok,
                        **parsed,
                    }
                    append_csv_row(env_csv, row)
                    env_count += 1
                    print(f"ENV #{env_count}: T={row.get('temp_h_c')} C RH={row.get('humidity_percent')} %")
                    continue

                print(f"UNRECOGNIZED HEADER: {line!r}")

        finally:
            if pause_at_end:
                print("Stopping cycle with pause...")
                try:
                    send_ascii(ser, "pause")
                    time.sleep(0.2)
                    txt = read_text_for(ser, 0.5)
                    if txt:
                        print(txt)
                except Exception as e:
                    print(f"Pause command failed: {e}")

    print("\nDone.")
    print(f"  SPL CSV: {spl_csv}")
    print(f"  ENV CSV: {env_csv}")
    print(f"  RAW log: {raw_log}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Run and collect data from a NanoZ EK-IV board.")
    ap.add_argument("--list", action="store_true", help="List available COM ports.")
    ap.add_argument("--identify", action="store_true", help="Identify the selected port/board and exit.")
    ap.add_argument("--port", help="Explicit COM port, e.g. COM9.")
    ap.add_argument("--sn", default=BOARD_09_SN, help="Board S/N to find, default is board 09: 0002-0009.")
    ap.add_argument("--cycle", type=int, default=1, help="Stored cycle number to run.")
    ap.add_argument("--duration", type=float, default=60.0, help="Collection duration in seconds.")
    ap.add_argument("--env-interval", type=float, default=1.0, help="Seconds between #env? requests. Use 0 to disable.")
    ap.add_argument("--outdir", default="nanoz_data", help="Output folder for CSV/raw files.")
    ap.add_argument("--start", action="store_true", help="Actually send the run command. Without this, only identifies the board.")
    ap.add_argument("--no-pause", action="store_true", help="Do not send pause at the end.")
    args = ap.parse_args()

    if args.list:
        print_ports()
        return 0

    if args.port:
        ident = identify_on_port(args.port)
        if not ident:
            raise SystemExit(f"No NanoZ response found on {args.port}")
    else:
        ident = find_port_by_sn(args.sn)

    print("\nSelected NanoZ board:")
    print(f"  Port      : {ident.port}")
    print(f"  EK S/N    : {ident.serial_number}")
    print(f"  Firmware  : {ident.firmware}")
    print(f"  Signature : {ident.signature}")
    print(f"  USB ID    : {ident.usb_id}")

    if args.identify or not args.start:
        print("\nIdentify-only mode. Add --start to run the stored cycle and collect data.")
        return 0

    if ident.serial_number.upper() != args.sn.upper():
        print(f"WARNING: selected board S/N {ident.serial_number} does not match requested --sn {args.sn}")

    collect_run(
        port=ident.port,
        sn=ident.serial_number,
        cycle=args.cycle,
        duration_s=args.duration,
        outdir=Path(args.outdir),
        env_interval_s=args.env_interval,
        pause_at_end=not args.no_pause,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        raise SystemExit(130)
