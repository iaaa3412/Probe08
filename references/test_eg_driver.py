"""Does the Electroglas2001X driver itself talk to the prober correctly?

The probe scripts set write_termination="" (EOI only) explicitly. The driver
does not, so it inherits pyvisa's default - worth checking before trusting it.

SAFETY: read-only, '?'-prefixed queries only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import Electroglas2001X  # noqa: E402

drv = Electroglas2001X()
print(f"inst           : {drv.inst}")
print(f"write_term     : {drv.inst.write_termination!r}")
print(f"read_term      : {drv.inst.read_termination!r}")
print(f"is_present     : {drv.is_present()}")
print(f"get_id         : {drv.get_id()!r}")

print("\n--- driver query() calls ---")
for label, cmd in (("status  (?S)", "?S"), ("position(?P)", "?P"),
                   ("error   (?E)", "?E"), ("counts  (?Y)", "?Y")):
    try:
        print(f"  {label} -> {drv.query(cmd)!r}")
    except Exception as e:
        print(f"  {label} -> FAILED {type(e).__name__}: {e}")

print("\n--- driver helper methods ---")
for name in ("get_prober_status", "get_xy_position", "get_error_code",
             "get_die_counts", "get_cassette_status", "get_wafer_info"):
    try:
        print(f"  {name}() -> {getattr(drv, name)()!r}")
    except Exception as e:
        print(f"  {name}() -> FAILED {type(e).__name__}: {e}")

drv.close()
