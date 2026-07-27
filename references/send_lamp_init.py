"""Send LaMP's prober configuration, or restore what was there before it.

    python references/send_lamp_init.py lamp      <- apply LaMP's settings
    python references/send_lamp_init.py restore   <- put the previous ones back

Configuration only: every command is SP/SM/SO/SX/WM. Nothing moves the chuck,
stage or handler. The Z values DO differ from what this machine was set to, so
'restore' exists and PRE_LAMP_SETTINGS records the originals - there is no GPIB
query that reads SP parameters back.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import (  # noqa: E402
    LAMP_INIT_SEQUENCE, PRE_LAMP_SETTINGS, Electroglas2001X,
)

mode = (sys.argv[1].lower() if len(sys.argv) > 1 else "lamp")
if mode not in ("lamp", "restore"):
    sys.exit("use 'lamp' or 'restore'")

drv = Electroglas2001X()
if not drv.inst:
    sys.exit("could not open the prober")

status = drv.get_prober_status()
print(f"status : {status}  = {drv.decode_status(status)}")
print(f"?P     : {drv.get_xy_position()}     ?Z: {drv.query('?Z')}")
err = drv.get_error_code()
print(f"error  : {drv.decode_error(err)}\n")

rows = LAMP_INIT_SEQUENCE if mode == "lamp" else PRE_LAMP_SETTINGS
label = "LAMP_INIT_SEQUENCE" if mode == "lamp" else "PRE_LAMP_SETTINGS"
print(f"=== sending {label} ({len(rows)} commands) ===")

# Every command acknowledges once SM15M111100000 is in effect, and an
# uncollected acknowledgement wedges the prober - so send_settings() reads each
# one. clear_interface() first, in case anything is still pending from before.
drv.clear_interface()
try:
    drv.send_settings(rows, log=lambda line: print(f"  {line}"))
except Exception as e:
    print(f"\n  *** ABORTED: {e}")
    print("  running clear_interface() to leave the link usable")
    drv.clear_interface()

time.sleep(0.3)
print("\n--- after ---")
print(f"status : {drv.decode_status(drv.get_prober_status())}")
print(f"?P     : {drv.get_xy_position()}     ?Z: {drv.query('?Z')}")
print(f"error  : {drv.decode_error(drv.get_error_code())}")
print(f"options: {drv.query('?O')}")
print("\nCheck the prober's SET PRMTR page to confirm the values took.")
drv.close()
