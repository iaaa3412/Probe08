"""Diagnose the Electroglas 2001X's GPIB link. Re-run this after changing any
GPIB/host setting on the prober itself to see whether it starts responding.

    python references/probe_2001x.py

SAFETY: read-only. The only string ever written is '?S', a query. No motion,
handler or SP/MO/MD/MA command is sent - in this command set bare letters
(Z, U, L, J, I, D, M) are motion and wafer-handler commands, so nothing here
goes near them.

What it establishes, in order of increasing involvement from the prober:
  1. serial poll      - answered by the GPIB interface chip on its own
  2. accepts a command - requires the prober's software to service the bus
  3. answers a query   - requires it to understand the command

A known-good instrument on the same adapter is tested alongside, so a failure
can be attributed to the prober rather than to the cable, adapter or VISA.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.gpib_base import open_resource  # noqa: E402

PROBER = "GPIB0::29::INSTR"
CONTROL = "GPIB0::9::15::INSTR"      # HP switchbox: same bus, same adapter


def stage_1_and_2(address, label):
    inst, via = open_resource(address)
    inst.timeout = 800
    inst.write_termination = ""
    inst.read_termination = None
    print(f"\n{label}  ({address}, via {via})")
    try:
        print("  1. resource opens        : yes")
        try:
            stb = inst.read_stb()
            print(f"  2. serial poll           : STB = 0x{stb:02X}")
        except Exception as e:
            print(f"  2. serial poll           : FAILED ({type(e).__name__})")
            return False
        try:
            n = inst.write("?S")
            print(f"  3. accepts a command     : yes, {n} bytes taken")
        except Exception as e:
            print(f"  3. accepts a command     : NO — {e}")
            return False
        try:
            print(f"  4. answers the query     : {inst.read_raw()!r}")
        except Exception:
            print("  4. answers the query     : silent (took the command, sent nothing back)")
        return True
    finally:
        inst.close()


print("=== control vs prober ===")
stage_1_and_2(CONTROL, "HP switchbox (known good)")
prober_talks = stage_1_and_2(PROBER, "Electroglas 2001X")

if not prober_talks:
    print("\n  The prober's GPIB interface chip is alive - it answers listener")
    print("  detection and serial polls without any help from the prober's")
    print("  software. Refusing every command byte means nothing behind that")
    print("  chip is servicing the bus. Check on the prober itself:")
    print("    - is host / remote GPIB control enabled in its configuration?")
    print("    - is it sitting in a local, manual or setup screen?")
    print("    - is its own GPIB address set to 29, as a device (not controller)?")
    print("    - is its control software running, rather than at a boot/error screen?")
    sys.exit(0)

print("\n=== prober responds — sweeping '?A'..'?Z' for supported queries ===")
inst, _ = open_resource(PROBER)
inst.timeout = 400
inst.write_termination = ""
inst.read_termination = None
try:
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        try:
            inst.write(f"?{letter}")
            reply = inst.read_raw()
        except Exception:
            continue
        if reply:
            print(f"  ?{letter} -> {reply!r}")
        time.sleep(0.05)
finally:
    inst.close()
