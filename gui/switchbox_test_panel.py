import tkinter as tk
from tkinter import ttk


class SwitchboxTestPanel(ttk.Frame):
    _BOXES = [("relay1", "HP Switchbox 1"), ("relay2", "HP Switchbox 2"),
             ("relay3", "HP Switchbox 3")]

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._channel_vars = {}

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        for i, (key, label) in enumerate(self._BOXES):
            self._build_box(key, label, column=i)

    def _log(self, msg: str):
        self.controller.log(msg)

    def _drv(self, key: str):
        drv = self.controller.drivers.get(key)
        return drv if (drv and drv.inst) else None

    def _build_box(self, key: str, label: str, column: int):
        lf = ttk.LabelFrame(self, text=label, padding=8)
        lf.grid(row=0, column=column, sticky="new", padx=8, pady=8)

        status_var = tk.StringVar(value="—")
        ttk.Label(lf, textvariable=status_var, foreground="gray",
                 wraplength=180, justify="left").pack(anchor="w")

        ch_row = ttk.Frame(lf)
        ch_row.pack(fill="x", pady=(6, 2))
        ttk.Label(ch_row, text="Relay #:").pack(side="left")
        ch_var = tk.StringVar(value="1")
        self._channel_vars[key] = ch_var
        ttk.Entry(ch_row, textvariable=ch_var, width=6).pack(side="left", padx=4)

        btn_row = ttk.Frame(lf)
        btn_row.pack(fill="x", pady=(4, 2))
        ttk.Button(btn_row, text="Close", command=lambda k=key: self._close(k)).pack(
            side="left")
        ttk.Button(btn_row, text="Open", command=lambda k=key: self._open(k)).pack(
            side="left", padx=(4, 0))
        ttk.Button(btn_row, text="Open All",
                  command=lambda k=key: self._open_all(k)).pack(side="left", padx=(4, 0))

        ttk.Button(lf, text="↻ Read ID",
                  command=lambda k=key, v=status_var: self._read_id(k, v)).pack(
            anchor="w", pady=(6, 0))

    def _close(self, key: str):
        drv = self._drv(key)
        if not drv:
            self._log(f"[{key.upper()}] Not connected")
            return
        ch = self._channel_vars[key].get().strip()
        try:
            drv.close_channel(ch)
            self._log(f"[{key.upper()}] Closed relay {ch}")
        except Exception as e:
            self._log(f"[{key.upper()}] Close error: {e}")

    def _open(self, key: str):
        drv = self._drv(key)
        if not drv:
            self._log(f"[{key.upper()}] Not connected")
            return
        ch = self._channel_vars[key].get().strip()
        try:
            drv.open_channel(ch)
            self._log(f"[{key.upper()}] Opened relay {ch}")
        except Exception as e:
            self._log(f"[{key.upper()}] Open error: {e}")

    def _open_all(self, key: str):
        drv = self._drv(key)
        if not drv:
            self._log(f"[{key.upper()}] Not connected")
            return
        try:
            drv.open_all()
            self._log(f"[{key.upper()}] All relays opened")
        except Exception as e:
            self._log(f"[{key.upper()}] Open All error: {e}")

    def _read_id(self, key: str, status_var: tk.StringVar):
        drv = self._drv(key)
        if not drv:
            status_var.set("not connected")
            return
        try:
            resp = drv.get_id()
            status_var.set(resp or "(no response)")
            self._log(f"[{key.upper()}] ID: {resp}")
        except Exception as e:
            status_var.set(f"error: {e}")
            self._log(f"[{key.upper()}] ID error: {e}")
