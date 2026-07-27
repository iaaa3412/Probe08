"""Find what makes the prober stop acknowledging.

Acknowledgements arrive reliably and then stop. Three candidate triggers, all
consistent with the observed log:
  A  a rejected move (MF) leaves the protocol in a different state
  B  reaching an axis limit exactly (Z2000 = the Z DOWN LIMIT)
  C  clear_interface() itself disables acknowledgement, in which case the
     recovery is what breaks everything after the first timeout

Each is provoked separately, with a run of known-good moves after it, so the
one that actually kills acks is identifiable rather than inferred.

RUN WITH THE GUI CLOSED - a second VISA session on the same address is its own
source of interference and would invalidate the result.

Read-only apart from small Z moves well inside the limits, plus one deliberate
MD that the prober is expected to refuse.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import Electroglas2001X  # noqa: E402

Z_FLOOR = 2000      # Z DOWN LIMIT, 0.1-mil units
SAFE = 2300         # comfortably off both limits

drv = Electroglas2001X()
if not drv.inst:
    sys.exit("could not open the prober - is the GUI holding the session?")


def z():
    return drv.query("?Z")


def step(label, fn):
    """Run one action, timing it, reporting ack or loss."""
    started = time.monotonic()
    try:
        result = fn()
        ok = True
    except Exception as e:
        result, ok = f"{type(e).__name__}: {str(e).splitlines()[0][:70]}", False
    secs = time.monotonic() - started
    flag = "ok  " if ok else "LOST"
    print(f"  {flag} {label:<26} {secs:5.1f}s  {result}")
    return ok


def run_of_good_moves(tag, count=3):
    """Known-good ZR moves. How many still acknowledge?"""
    good = 0
    for i in range(count):
        direction = 100 if i % 2 == 0 else -100
        if step(f"{tag} ZR{direction:+d}", lambda d=direction: drv.move_z_relative(d)):
            good += 1
    print(f"    -> {good}/{count} acknowledged\n")
    return good


print(f"start: ?Z={z()}  ?P={drv.get_xy_position()}  "
      f"{drv.decode_status(drv.get_prober_status())}\n")

print("get Z to a safe mid position first:")
step("ZM to safe", lambda: drv.move_z_absolute(SAFE))
print()

print("BASELINE - do acks work at all right now?")
baseline = run_of_good_moves("base")

print("TRIGGER A - a refused move (MD -1 in X, expected MF):")
step("MD -1 X (expect MF)", lambda: drv.move_relative_die(-1, 0))
after_mf = run_of_good_moves("post-MF")

print("TRIGGER B - land exactly on the Z DOWN LIMIT:")
step("ZM to floor", lambda: drv.move_z_absolute(Z_FLOOR))
after_floor = run_of_good_moves("post-floor")

print("re-centre Z:")
step("ZM to safe", lambda: drv.move_z_absolute(SAFE))
print()

print("TRIGGER C - does clear_interface() itself stop acknowledgements?")
step("clear_interface", lambda: (drv.clear_interface(), "cleared")[1])
after_clear = run_of_good_moves("post-clear")

print("=" * 62)
print(f"  baseline        {baseline}/3")
print(f"  after MF        {after_mf}/3")
print(f"  after Z floor   {after_floor}/3")
print(f"  after clear     {after_clear}/3")
print("\nWhichever run collapses is the trigger. If none do, the cause is")
print("something the GUI does that this script does not.")
print(f"\nfinal ?Z={z()}  error={drv.decode_error(drv.get_error_code())}")
drv.close()
