"""Read-only state check. Is error 28 persistent or was it a stale latch?

?E is read-and-clear, so a single read cannot tell the difference. Reading it
repeatedly can: a condition that is still true re-latches, a stale one does not.
Nothing here moves the prober.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import Electroglas2001X  # noqa: E402

drv = Electroglas2001X()
if not drv.inst:
    sys.exit("could not open the prober")

print("?E read four times (read-and-clear):")
for i in range(4):
    raw = drv.get_error_code()
    print(f"  {i + 1}: {raw!r:8} = {drv.decode_error(raw)}")

print()
for label, cmd in (("?S status  ", "?S"), ("?P position", "?P"),
                   ("?Z z-axis  ", "?Z"), ("?C cassette", "?C")):
    print(f"{label} -> {drv.query(cmd)!r}")

print(f"\ndecoded: {drv.decode_status(drv.get_prober_status())}")
drv.close()
