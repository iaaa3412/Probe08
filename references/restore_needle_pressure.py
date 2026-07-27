"""Restore this machine's own overtravel and clearance before touchdown.

SP5Z overtravel is the pressure applied PAST sensed contact - the edge sensor
finds the surface, then Z continues by this much. LaMP's 3.70 mils is 2.5x this
machine's own 1.50, and applies to LaMP's probe card, not the one now fitted.

Deliberately targeted: it does NOT touch SP7Z (up limit, now 400 mils) or SP9Z
(align height, 350 mils), both of which were set on purpose for this setup. The
general 'send_lamp_init.py restore' would overwrite them.

Configuration only - nothing moves. Acks collected (SM15 is in effect).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.electroglas_2001x import Electroglas2001X  # noqa: E402

ROWS = [
    ("Z overtravel", "1.50 mils - needle pressure past contact "
                     "(was LaMP's 3.70)", "SP5Z15"),
    ("Z clearance",  "10.00 mils (was LaMP's 15.00)", "SP6Z100"),
]

drv = Electroglas2001X()
if not drv.inst:
    sys.exit("could not open the prober - is the GUI holding the session?")

drv.clear_interface()

print(f"before : {drv.decode_status(drv.get_prober_status())}")
print(f"?P {drv.get_xy_position()}   ?Z {drv.query('?Z')}   "
      f"?T {drv.query('?T')}   error: {drv.decode_error(drv.get_error_code())}\n")

try:
    drv.send_settings(ROWS, log=lambda line: print(f"  {line}"))
except Exception as e:
    print(f"\n  *** ABORTED: {e}")
    drv.clear_interface()

print(f"\nafter  : {drv.decode_status(drv.get_prober_status())}")
print(f"?P {drv.get_xy_position()}   ?Z {drv.query('?Z')}   "
      f"error: {drv.decode_error(drv.get_error_code())}")
print("\nConfirm on SET PRMTR:  06 Z OVERTRAVEL = 1.50   07 Z CLEARANCE = 10.00")
print("Unchanged on purpose:  08 Z UP LIMIT = 400.00   10 Z ALIGN = 350.00")
drv.close()
