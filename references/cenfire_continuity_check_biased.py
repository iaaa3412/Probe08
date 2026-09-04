"""
Cenfire probe-card continuity check - SMU BIASED version.

Same idea as cenfire_continuity_check.py, but instead of the DMM's small
built-in test current, the SMU forces the real production current
(10 mA, 7V compliance - matching the Cenfire recipe) across each pair
and resistance is computed from the SMU's own combined V/I read. Useful
for comparing against the DMM-only (near-zero current) sweep to see if
contact resistance changes under real load.

Assumes the chuck is ALREADY UP (pins in contact) - this script does not
touch the prober at all.

Usage:
    python cenfire_continuity_check_biased.py
"""
import sys, os, time, itertools

ROOT = r"c:\automationproject\Probe08"
for p in (ROOT, os.path.join(ROOT, "gui")):
    if p not in sys.path:
        sys.path.insert(0, p)

from instruments.keithley2400 import Keithley2400
from instruments.keithley_707b import Keithley707B

# --- tune these ---
FORCE_CURRENT = 0.01   # 10 mA, matches the Cenfire recipe
VOLTAGE_LIMIT = 7.0    # matches the Cenfire recipe
OPEN_CURRENT_A = 1e-4  # if measured current stays under this, SMU hit compliance -> open
SAME_PAD_MAX_OHM = 20  # same-pad pairs should read a real short, well under this
SETTLE_S = 0.4         # settle time after closing crosspoints + turning output on

# pairs that land on the same physical pad - these SHOULD read a near-short.
# everything else should NOT be anywhere near this low (real per-die values
# vary die to die, roughly 0.5-5 ohm on some, 100-500 ohm on others).
SAME_PAD_PAIRS = {frozenset((12, 13)), frozenset((1, 24)), frozenset((11, 2))}

PINS = {
    1:  ("2", "01", "J1",  "Sense-"),
    2:  ("2", "02", "J3",  ""),
    11: ("2", "11", "J21", "Force+"),
    12: ("2", "12", "J23", "Sense+"),
    13: ("4", "01", "J25", ""),
    23: ("4", "11", "J45", "Force-"),
    24: ("4", "12", "J47", ""),
}


def tag(p):
    slot, col, j, label = PINS[p]
    return f"pin{p}({j}{'/' + label if label else ''})"


def main():
    print("=== Connecting (SMU + switch only) ===")
    smu = Keithley2400(config_key="smu")
    switch = Keithley707B(config_key="switch_matrix")

    smu.write(":OUTP OFF")
    switch.write('channel.open("allslots")')
    time.sleep(0.3)

    smu.set_current("smua", FORCE_CURRENT)
    smu.set_voltage_limit("smua", VOLTAGE_LIMIT)

    pin_ids = list(PINS.keys())
    pairs = list(itertools.combinations(pin_ids, 2))
    print(f"Sweeping {len(pairs)} pin pairs with SMU forcing {FORCE_CURRENT*1000:.1f} mA\n")

    opens, bad, ok = [], [], []

    try:
        for a, b in pairs:
            slot_a, col_a, _, _ = PINS[a]
            slot_b, col_b, _, _ = PINS[b]
            same_pad = frozenset((a, b)) in SAME_PAD_PAIRS

            # row A = SMU HI, row B = SMU LO
            switch.close_crosspoint(f"{slot_a}A", col_a)
            switch.close_crosspoint(f"{slot_b}B", col_b)
            smu.turn_output_on("smua")
            time.sleep(SETTLE_S)

            i_val, v_val = smu.measure_current_and_voltage("smua")

            smu.turn_output_off("smua")
            switch.open_crosspoint(f"{slot_a}A", col_a)
            switch.open_crosspoint(f"{slot_b}B", col_b)
            time.sleep(0.15)

            is_open = abs(i_val) < OPEN_CURRENT_A
            r = (v_val / i_val) if not is_open else float("nan")

            label = f"{tag(a):22s} <-> {tag(b):22s}"
            pad_note = "  [same pad - expect short]" if same_pad else ""

            if same_pad:
                if is_open or r > SAME_PAD_MAX_OHM:
                    shown = "OPEN" if is_open else f"{r:.4g} ohm"
                    print(f"  {label}  {shown:>10}   <-- NOT SHORTED (expected short){pad_note}   [I={i_val:.4e}A V={v_val:.4f}V]")
                    bad.append((a, b, r, "expected short but isn't"))
                else:
                    print(f"  {label}  {r:10.4g} ohm   ok (shorted as expected){pad_note}")
                    ok.append((a, b, r))
            else:
                if is_open:
                    print(f"  {label}  OPEN   [I={i_val:.4e}A V={v_val:.4f}V]")
                    opens.append((a, b))
                elif r <= SAME_PAD_MAX_OHM:
                    print(f"  {label}  {r:10.4g} ohm   <-- SUSPICIOUSLY LOW (same-pad-level short on a pair that shouldn't be)")
                    bad.append((a, b, r, "unexpectedly shorted"))
                else:
                    print(f"  {label}  {r:10.4g} ohm   ok   [I={i_val:.4e}A V={v_val:.4f}V]")
                    ok.append((a, b, r))
    finally:
        smu.turn_output_off("smua")
        switch.write('channel.open("allslots")')

    print("\n=== Summary ===")
    print(f"OK ({len(ok)}):")
    for a, b, r in ok:
        print(f"  pin{a} <-> pin{b}: {r:.4g} ohm")

    print(f"\nUNEXPECTED ({len(bad)}):")
    for a, b, r, why in bad:
        print(f"  pin{a} <-> pin{b}: {r:.4g} ohm  ({why})")

    print(f"\nOPEN / not connected ({len(opens)}):")
    for a, b in opens:
        print(f"  pin{a} <-> pin{b}")


if __name__ == "__main__":
    main()
