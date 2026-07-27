"""Unwedge the prober after an unread acknowledgement blocked the bus.

SM15M111100000 turns on MC/MF acknowledgement for every subsequent command. If
those acks are not collected the prober stops accepting writes entirely - which
is where it is now.

Escalates gently, least invasive first:
  1. serial poll (no write at all - just asks the interface chip)
  2. long reads to pull anything queued
  3. viClear / Selected Device Clear, which resets the instrument's GPIB I/O
     state. That is an interface-level reset - it does not move the machine or
     change its configuration.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.gpib_base import open_resource  # noqa: E402

inst, _ = open_resource("GPIB0::29::INSTR")
inst.write_termination = ""
inst.read_termination = None

print("1. serial poll (no write):")
try:
    print(f"   STB = 0x{inst.read_stb():02X}")
except Exception as e:
    print(f"   failed: {type(e).__name__}")

print("\n2. draining queued replies (long timeout):")
inst.timeout = 2000
drained = 0
for _ in range(10):
    try:
        data = inst.read_raw()
    except Exception:
        break
    drained += 1
    print(f"   <- {data!r}")
print(f"   drained {drained}")

print("\n3. can it accept a write now?")
inst.timeout = 1500
try:
    inst.write("?S")
    print(f"   yes -> {inst.read_raw()!r}")
    inst.close()
    sys.exit(0)
except Exception as e:
    print(f"   still refusing: {type(e).__name__}")

print("\n4. device clear (interface reset, machine state untouched):")
try:
    inst.clear()
    print("   viClear ok")
except Exception as e:
    print(f"   viClear failed: {e}")

print("\n5. retry after clear:")
try:
    inst.write("?S")
    print(f"   recovered -> {inst.read_raw()!r}")
except Exception as e:
    print(f"   STILL REFUSING: {e}")
    print("   -> the prober likely needs ON LINE toggled at the panel")

inst.close()
