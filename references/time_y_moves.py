"""Time a run of Y-only die moves, one at a time, and look at the spread.

XY moves are the ones that intermittently stall - pure Z moves measured a flat
0.3-0.4s, twelve for twelve. Every XY move first drives Z to the down limit,
and with Z TRAVEL MODE = auto profile (SM5E2) it very likely profiles
afterwards, hunting for a wafer surface that is not there. If that is the
cause, the slow moves should be XY-specific and irregular, with Z steps
interleaved here staying fast throughout.

Walks +Y up, then back down to where it started. Strictly one command at a
time, so nothing here can be blamed on concurrency.

RUN WITH THE GUI CLOSED. No wafer, no probe card.
"""
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import Electroglas2001X  # noqa: E402

STEPS = 8

drv = Electroglas2001X()
if not drv.inst:
    sys.exit("could not open the prober - is the GUI holding the session?")

start_pos = drv.get_xy_position()
print(f"start: ?P={start_pos}  ?Z={drv.query('?Z')}  "
      f"{drv.decode_status(drv.get_prober_status())}\n")

xy_times, z_times = [], []


def timed(label, fn, bucket):
    t0 = time.monotonic()
    try:
        result = fn()
        ok = True
    except Exception as e:
        result, ok = f"{type(e).__name__}: {str(e).splitlines()[0][:60]}", False
    secs = time.monotonic() - t0
    bucket.append(secs)
    mark = "" if secs < 3 else ("  <-- SLOW" if secs < 25 else "  <-- STALLED")
    print(f"  {'ok  ' if ok else 'FAIL'} {label:<16} {secs:6.1f}s  "
          f"?P={drv.get_xy_position():<8} ?Z={drv.query('?Z'):<7}{mark}")
    return ok


# The Z control moves need Z inside its limits. It parks at Z0, below the down
# limit, and a relative move from there targets somewhere still outside and is
# refused - which is what made all four controls fail last run.
low, high = drv.z_limits
z_now = drv._parse_z(drv.query("?Z"))
if z_now is None or not low <= z_now <= high:
    print(f"Z is at {z_now}, outside its limits [{low}..{high}] — "
          f"moving into range so the Z controls are meaningful:")
    timed("  ZM into range", lambda: drv.move_z_absolute(low + 300), z_times)
    z_times.clear()
    print()

print(f"=== {STEPS} x  MD +0,+1   (Y up, one die each) ===")
climbed = 0
for i in range(STEPS):
    if not timed(f"{i + 1}. MD 0,+1", lambda: drv.move_relative_die(0, 1), xy_times):
        break
    climbed += 1
    if i % 3 == 2:      # a Z move between XY moves, as a control
        timed("   (Z control)", lambda: drv.move_z_relative(100), z_times)
        timed("   (Z control)", lambda: drv.move_z_relative(-100), z_times)

print(f"\n=== returning {climbed} steps in -Y ===")
for i in range(climbed):
    if not timed(f"{i + 1}. MD 0,-1", lambda: drv.move_relative_die(0, -1), xy_times):
        break

print("\n" + "=" * 60)
if xy_times:
    print(f"XY moves ({len(xy_times)}):  min {min(xy_times):5.1f}s   "
          f"median {statistics.median(xy_times):5.1f}s   max {max(xy_times):6.1f}s")
if z_times:
    print(f"Z  moves ({len(z_times)}):  min {min(z_times):5.1f}s   "
          f"median {statistics.median(z_times):5.1f}s   max {max(z_times):6.1f}s")
print(f"\nend: ?P={drv.get_xy_position()} (started {start_pos})  "
      f"?Z={drv.query('?Z')}")
print(f"error: {drv.decode_error(drv.get_error_code())}")
drv.close()
