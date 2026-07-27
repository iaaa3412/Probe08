"""Reproduce the GUI's conditions: a background status poller during jogs.

gui/app.py's _poll_prober_ready fires every 3 seconds on its own thread and
calls read_stb_decoded(), which for this driver is a ?S query. That is the one
thing the GUI does and the scripted runs never did - and scripted runs were
36/36 clean while the GUI intermittently lost an acknowledgement.

This runs the same poller alongside a run of MD moves. With the driver's I/O
lock in place every move should still acknowledge; without it, a move issued
while the poller holds the bus loses its MC and times out.

RUN WITH THE GUI CLOSED. No wafer, no probe card.
"""
import os
import statistics
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import Electroglas2001X  # noqa: E402

MOVES = 12
POLL_SECONDS = 3.0

drv = Electroglas2001X()
if not drv.inst:
    sys.exit("could not open the prober - is the GUI holding the session?")

stop = threading.Event()
polls = {"ok": 0, "fail": 0}


def poller():
    """Same cadence and call as gui/app.py's _poll_prober_ready."""
    while not stop.wait(POLL_SECONDS):
        try:
            drv.read_stb_decoded()
            polls["ok"] += 1
        except Exception:
            polls["fail"] += 1


print(f"start: ?P={drv.get_xy_position()}  ?Z={drv.query('?Z')}")
print(f"poller running every {POLL_SECONDS}s, {MOVES} MD moves alongside it\n")

thread = threading.Thread(target=poller, daemon=True)
thread.start()

times, failures = [], []
try:
    for i in range(MOVES):
        direction = 1 if i < MOVES // 2 else -1
        t0 = time.monotonic()
        try:
            ack = drv.move_relative_die(0, direction)
            note = f"ack={ack}"
        except Exception as e:
            note = f"FAILED {type(e).__name__}: {str(e).splitlines()[0][:55]}"
            failures.append(i + 1)
        secs = time.monotonic() - t0
        times.append(secs)
        print(f"  {i + 1:2}. MD 0,{direction:+d}  {secs:6.1f}s  "
              f"?P={drv.get_xy_position():<8} {note}")
finally:
    stop.set()
    thread.join(timeout=5)

print("\n" + "=" * 60)
print(f"moves      : {MOVES - len(failures)}/{MOVES} acknowledged")
print(f"timing     : min {min(times):.1f}s  median {statistics.median(times):.1f}s  "
      f"max {max(times):.1f}s")
print(f"poller     : {polls['ok']} ok, {polls['fail']} failed")
if failures:
    print(f"FAILED MOVES: {failures}  <-- the lock is not holding")
else:
    print("no lost acknowledgements - the lock holds under the GUI's own poller")
print(f"\nend: ?P={drv.get_xy_position()}  ?Z={drv.query('?Z')}  "
      f"error={drv.decode_error(drv.get_error_code())}")
drv.close()
