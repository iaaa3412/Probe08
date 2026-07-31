"""Inventory the E1300A mainframe: what is on the backplane vs what GPIB can reach.

Those are two different lists, and the gap between them is the interesting part.

The mainframe's system instrument (secondary address 0) answers

    VXI:CONF:NUMB?      how many devices are on the VXI backplane
    VXI:CONF:DLAD?      their logical addresses

That is authoritative - it is the mainframe reporting its own backplane. A
module only becomes reachable over GPIB if the command module also publishes it
as an instrument, at

    secondary address = logical address / 8

A module whose logical address is not a free multiple of 8, or that the command
module has no driver for, is left UNASSIGNED: powered, seated, listed by
DLAD?, but with no GPIB address at all. VISA will not even open the address -
it returns VI_ERROR_RSRC_NFOUND rather than opening and timing out.

READ-ONLY: VXI:CONF queries, a serial poll, *IDN?, and SYST:CTYP? on anything
that says SWITCHBOX. Nothing closes a relay, changes a setting or triggers a
measurement.

RUN WITH THE GUI CLOSED so it is not fighting for the sessions.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.gpib_base import open_resource  # noqa: E402

PRIMARY = 9
POLL_TIMEOUT_MS = 300
QUERY_TIMEOUT_MS = 900


def ask_backplane():
    """[logical addresses] straight from the mainframe, or None."""
    try:
        inst, _ = open_resource(f"GPIB0::{PRIMARY}::0::INSTR")
    except Exception as e:
        print(f"cannot reach the system instrument: {e}")
        return None
    try:
        inst.timeout = QUERY_TIMEOUT_MS
        print(f"system instrument: {(inst.query('*IDN?') or '').strip()}")
        count = (inst.query("VXI:CONF:NUMB?") or "").strip()
        raw = (inst.query("VXI:CONF:DLAD?") or "").strip()
        print(f"VXI:CONF:NUMB? -> {count}   VXI:CONF:DLAD? -> {raw}\n")
        return [int(part) for part in raw.split(",") if part.strip()]
    except Exception as e:
        print(f"backplane query failed: {type(e).__name__}: {e}")
        return None
    finally:
        try:
            inst.close()
        except Exception:
            pass


def identify(sa):
    """(identity, [cards]) for a secondary address, or None if unreachable."""
    address = f"GPIB0::{PRIMARY}::{sa}::INSTR"
    try:
        inst, _ = open_resource(address)
    except Exception:
        return None                      # VISA has no such resource
    try:
        inst.timeout = POLL_TIMEOUT_MS
        try:
            inst.read_stb()
        except Exception:
            return None
        inst.timeout = QUERY_TIMEOUT_MS
        try:
            identity = (inst.query("*IDN?") or "").strip()
        except Exception:
            identity = "(no answer to *IDN?)"
        cards = []
        if "SWITCHBOX" in identity.upper():
            for slot in range(1, 5):
                try:
                    card = (inst.query(f"SYST:CTYP? {slot}") or "").strip()
                except Exception:
                    break
                if card and not card.upper().startswith("NONE"):
                    cards.append((slot, card))
        return identity, cards
    finally:
        try:
            inst.close()
        except Exception:
            pass


laddrs = ask_backplane()
if laddrs is None:
    print("Falling back to a blind sweep of every secondary address.")
    laddrs = [sa * 8 for sa in range(31)]

print(f"{'LADDR':>5}  {'SA':>3}  {'address':<22} identity")
print("-" * 82)

unassigned = []
for laddr in sorted(laddrs):
    sa = laddr // 8
    address = f"GPIB0::{PRIMARY}::{sa}::INSTR"
    if laddr % 8:
        unassigned.append((laddr, "logical address is not a multiple of 8"))
        print(f"{laddr:>5}  {'—':>3}  {'—':<22} UNASSIGNED (not a multiple of 8)")
        continue
    result = identify(sa)
    if result is None:
        unassigned.append((laddr, "no GPIB instrument published for it"))
        print(f"{laddr:>5}  {sa:>3}  {address:<22} UNASSIGNED — on the backplane, "
              "not reachable over GPIB")
        continue
    identity, cards = result
    print(f"{laddr:>5}  {sa:>3}  {address:<22} {identity}")
    for slot, card in cards:
        print(f"{'':>5}  {'':>3}  {'':<22}   slot {slot}: {card}")

print("-" * 82)

if not unassigned:
    print("Every device on the backplane is reachable over GPIB.")
    sys.exit(0)

print(f"\n{len(unassigned)} device(s) on the backplane with no GPIB address:")
for laddr, why in unassigned:
    print(f"  LADDR {laddr}  —  {why}")

print("\nOn this bench the expected culprit is an E1326B multimeter. The relay")
print("wiring lands on one, so nothing can be measured until it is assigned.")
print("Fix, in order:")
print("  1. E1300A front panel — it lists the configured instruments and will")
print("     say what it made of the module.")
print("  2. The logical address switch on the module. Factory is 24 (secondary")
print("     address 03). Two multimeters cannot both be 24 — move one to any")
print("     free multiple of 8; 80, 112 and 120 are taken by the switchboxes.")
print("  3. Power-cycle the mainframe. Logical addresses are read at boot.")
print("\nThen set dmm_vxi_eg in instruments/instruments.yaml to the new address.")
