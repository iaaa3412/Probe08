"""Read-only board EEPROM Configuration viewer, for the Electroglas NanoZ
NanoZ_EK tab. A deliberately smaller version of gui/nanoz_panel.py's own
NanoZ_EK tab: this reads and decodes the "B - Configuration" block only
(signature, cycle/sequence counts, periodicity, calibration offsets, both
chips' ID/age - see instruments/nanoz_board.parse_params_block) and skips
the Cycle/Sequence/Heater viewing and the EEPROM WRITE path entirely -
writing to EEPROM is explicitly flagged dangerous/unconfirmed in
nanoz_board.py itself (write_eeprom's own docstring), and porting that
safely is future work, not something to reproduce blind here.
"""

import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

import instruments.nanoz_board as nzb


class EgNanozEkPanel(ttk.Frame):
    def __init__(self, parent, setup_panel):
        super().__init__(parent)
        self._setup = setup_panel
        self._latest_eep: dict[str, dict] = {}   # port -> packet
        setup_panel.subscribe(self._on_packet)

        self.columnconfigure(0, weight=1)

        pick = ttk.Frame(self)
        pick.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        ttk.Label(pick, text="Board:").pack(side="left")
        self._board_var = tk.StringVar(value="")
        self._board_cb = ttk.Combobox(pick, textvariable=self._board_var,
                                      state="readonly", width=18)
        self._board_cb.pack(side="left", padx=(4, 12))
        ttk.Button(pick, text="🔄 Read Configuration", command=self._read_configuration
                  ).pack(side="left")
        self._status_var = tk.StringVar(value="")
        ttk.Label(pick, textvariable=self._status_var, foreground="#6b7280"
                 ).pack(side="left", padx=(10, 0))

        cfg_lf = ttk.LabelFrame(self, text="B — Configuration", padding=6)
        cfg_lf.grid(row=1, column=0, sticky="new", padx=6, pady=(0, 6))
        self._vars = {k: tk.StringVar(value="—") for k in
                      ("signature", "cycles_configured", "periodicity_ms",
                       "cal1", "cal2", "chip1", "chip2")}
        labels = (("signature", "Signature:"), ("cycles_configured", "Cycles configured:"),
                 ("periodicity_ms", "Periodicity (ms):"), ("cal1", "CAL-1:"),
                 ("cal2", "CAL-2:"), ("chip1", "Chip 1 (ID / Age):"),
                 ("chip2", "Chip 2 (ID / Age):"))
        for r, (key, label) in enumerate(labels):
            ttk.Label(cfg_lf, text=label).grid(row=r, column=0, sticky="e", padx=4, pady=2)
            ttk.Label(cfg_lf, textvariable=self._vars[key]).grid(row=r, column=1, sticky="w")

        self.refresh_boards()

    def refresh_boards(self):
        sns = sorted(self._setup.identities.keys())
        self._board_cb.config(values=sns)
        if not self._board_var.get() and sns:
            self._board_var.set(sns[0])

    def _on_packet(self, item):
        if item.get("kind") == "eep":
            self._latest_eep[item.get("port")] = item

    def _request_sync(self, board, addr, length, timeout_s=3.0):
        self._latest_eep.pop(board.port, None)
        board.request_eeprom(addr, length)
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            item = self._latest_eep.get(board.port)
            if item and item.get("addr") == addr and item.get("len") == length:
                return bytes.fromhex(item.get("data_hex", ""))
            time.sleep(0.05)
        return None

    def _read_configuration(self):
        self.refresh_boards()
        sn = self._board_var.get()
        board = self._setup.boards.get(sn)
        if not board or not board.ser:
            messagebox.showerror("NanoZ_EK", "Pick a connected board first (Setup tab).")
            return
        self._status_var.set("Reading...")

        def _work():
            try:
                blob = bytearray()
                for addr in (0, 64, 128):
                    chunk = self._request_sync(board, addr, 64)
                    if chunk is None:
                        self.after(0, lambda a=addr: self._status_var.set(
                            f"Timed out reading PARAMS @ {a}"))
                        return
                    blob += chunk
                params = nzb.parse_params_block(bytes(blob))
            except Exception as e:
                self.after(0, lambda: self._status_var.set(f"Failed: {e}"))
                return
            self.after(0, lambda: self._show(params))

        threading.Thread(target=_work, daemon=True).start()

    def _show(self, params):
        self._status_var.set("OK")
        self._vars["signature"].set(params["signature"])
        self._vars["cycles_configured"].set(str(params["cycles_configured"]))
        self._vars["periodicity_ms"].set(str(params["periodicity_ms"]))
        self._vars["cal1"].set(f"{params['cal1']:.4f}")
        self._vars["cal2"].set(f"{params['cal2']:.4f}")
        c1, c2 = params["chip1"], params["chip2"]
        self._vars["chip1"].set(f"{c1['id']}  (age {c1['age_s']}s)")
        self._vars["chip2"].set(f"{c2['id']}  (age {c2['age_s']}s)")
