"""Walk the stage back to X0Y0 one die at a time.

A single large MD move was refused with MF even though the same distance was
covered fine in single-die steps, which left the stage parked away from the
origin. Single steps are known-good, so step back with those and verify ?P
after each one.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import Electroglas2001X  # noqa: E402

TARGET = (0, 0)
MAX_STEPS = 60

drv = Electroglas2001X()
if not drv.inst:
    sys.exit("could not open the prober")


def parse(pos):
    try:
        return (int(pos.split("X", 1)[1].split("Y", 1)[0]),
                int(pos.split("Y", 1)[1]))
    except (IndexError, ValueError):
        return None


pos = drv.get_xy_position()
print(f"status : {drv.decode_status(drv.get_prober_status())}")
print(f"at     : {pos}  -> walking back to X0Y0\n")

for _ in range(MAX_STEPS):
    here = parse(pos)
    if here is None:
        sys.exit(f"cannot parse position {pos!r} - stopping")
    if here == TARGET:
        break
    dx = -1 if here[0] > TARGET[0] else (1 if here[0] < TARGET[0] else 0)
    dy = -1 if here[1] > TARGET[1] else (1 if here[1] < TARGET[1] else 0)
    try:
        drv.move_relative_die(dx, dy)
    except RuntimeError as e:
        print(f"  refused at {pos}: {e}")
        break
    pos = drv.get_xy_position()
    print(f"  step ({dx:+d},{dy:+d}) -> {pos}")

print(f"\nfinal ?P: {pos}")
print("AT ORIGIN" if parse(pos) == TARGET else "*** NOT at origin ***")
print(f"status  : {drv.decode_status(drv.get_prober_status())}")
print(f"error   : {drv.decode_error(drv.get_error_code())}")
drv.close()
