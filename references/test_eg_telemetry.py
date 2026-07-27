"""Exercise the telemetry read the GUI's 'Refresh Telemetry' button uses.

SAFETY: read-only. Only '?' queries. The init sequence is NOT sent here - that
is configuration, and is deliberately left behind a confirm in the GUI.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import LAMP_INIT_SEQUENCE, Electroglas2001X  # noqa: E402

drv = Electroglas2001X()
if not drv.inst:
    sys.exit("could not open the prober")

print("=== read_telemetry() ===")
for key, value in drv.read_telemetry().items():
    print(f"  {key:<20} {value!r}")

print(f"\n=== LAMP_INIT_SEQUENCE: {len(LAMP_INIT_SEQUENCE)} commands (not sent) ===")
for what, value, command in LAMP_INIT_SEQUENCE:
    print(f"  {command:<16} {what}" + (f" ({value})" if value else ""))

drv.close()
