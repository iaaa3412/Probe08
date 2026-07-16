import time
import os
import sys
from instruments.gpib_base import GPIBInstrument

class Keithley707B(GPIBInstrument):
    def __init__(self):
        super().__init__('switch_matrix')

    def open_all(self):
        self.write("channel.open('allslots')")

    def close_channel(self, channel: str):
        """Close a single channel by its full identifier, e.g. '1A3'."""
        self.write(f"channel.close('{channel}')")

    def close_crosspoint(self, row, column):
        crosspoint = f"{row}{column}"
        self.write(f"channel.close('{crosspoint}')")

    def open_crosspoint(self, row, column):
        crosspoint = f"{row}{column}"
        self.write(f"channel.open('{crosspoint}')")

    def read_crosspoint(self, crosspoint: str) -> bool:
        """Returns True if crosspoint is closed. crosspoint e.g. '1A3'."""
        resp = self.query(f"print(channel.getstate('{crosspoint}'))")
        return str(resp).strip() == "1" if resp else False

    def query_state(self, channel_list: str) -> str:
        """Query channel.getstate for an explicit channel list.

        Pass a comma-separated list built from the configured card, e.g.
        '1A1,1A2,...,1D8'. The 707B returns one character per channel in the
        same order: '0'=open, '1'=closed. This is more reliable than
        'allslots' which spans all mainframe slots in a firmware-defined order.
        """
        resp = self.query(f"print(channel.getstate('{channel_list}'))")
        return str(resp).strip() if resp else ""

    def query_mainframe_idn(self) -> str:
        """Return the mainframe model, serial, and firmware revision."""
        parts = []
        for tsp in ("localnode.model", "localnode.serialno", "localnode.revision"):
            val = self.query(f"print({tsp})")
            parts.append(str(val).strip() if val else "?")
        return "  |  ".join(parts)   # e.g. "707B  |  1234567  |  1.5.0a"

    def query_slot_info(self, slot: int) -> dict:
        """Return card info for one mainframe slot (1-4).

        The 707B TSP slot[N].idn returns two values (string + table object).
        When passed to print() they are tab-separated, e.g.:
            "7072, 8*12 Semiconductor Channels: \ttable: a096bb90"
        slot[N].startchannel / endchannel are also table objects — not strings —
        so we do NOT query them. Instead we parse the dimensions directly from
        the IDN string where they appear as "8*12" or "8x12".

        Returns a dict:
            model      — card model, e.g. '7072'
            idn        — full first-line IDN text (no table part)
            start_ch   — constructed first channel, e.g. '2A1'
            end_ch     — constructed last channel,  e.g. '2H12'
            rows       — int number of row buses  (0 if slot empty)
            cols       — int number of column buses (0 if slot empty)
        """
        import re

        idn_raw = self.query(f"print(slot[{slot}].idn)")
        idn_full = str(idn_raw).strip() if idn_raw else ""

        # Tab separates the model string from the TSP table object — keep only the first part
        idn_str = idn_full.split("\t")[0].strip()

        # Detect empty slot (nil, blank, or explicit "empty" text)
        _EMPTY = {"nil", "empty slot", "no card", "empty", "none", ""}
        if not idn_str or idn_str.lower() in _EMPTY:
            return {"model": "Empty", "idn": "", "start_ch": "", "end_ch": "",
                    "rows": 0, "cols": 0}

        # Model = first token before the comma  e.g. "7072"
        model = idn_str.split(",")[0].strip()

        # Dimensions embedded in IDN as "<rows>*<cols>" or "<rows>x<cols>"
        dim = re.search(r'(\d+)\s*[x*×]\s*(\d+)', idn_str)
        rows = int(dim.group(1)) if dim else 0
        cols = int(dim.group(2)) if dim else 0

        # Construct readable channel range from slot/rows/cols
        row_letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        start_ch = f"{slot}A1" if rows and cols else ""
        end_ch   = f"{slot}{row_letters[rows - 1]}{cols}" if rows and cols else ""

        return {"model": model, "idn": idn_str, "start_ch": start_ch, "end_ch": end_ch,
                "rows": rows, "cols": cols}

    def query_all_slots(self) -> dict:
        """Return query_slot_info for all four mainframe slots."""
        return {s: self.query_slot_info(s) for s in range(1, 5)}