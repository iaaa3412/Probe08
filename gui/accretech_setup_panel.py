"""Setup tab (Accretech) - edit the fixed instrument set's addresses/
timeouts/protocol without hand-editing instruments/instruments.yaml.

DIFFERENT SHAPE FROM ELECTROGLAS ON PURPOSE. Electroglas has real per-bench
profiles (instruments/eg_profiles.py, instruments/eg_probers.yaml) because
probe02 and probe03 are genuinely different benches with different
instruments at different addresses. Accretech has no such thing today - one
bench (probe08), five instrument keys hardcoded into
AtomicaDashboard.init_hardware()'s own connections list (see gui/app.py) and
read from flat top-level keys in instruments.yaml, not a per-bench profile.

So this tab can genuinely EDIT those five keys' address/protocol/timeout,
but "add a prober" has nothing to plug into yet - it would need
init_hardware() itself to loop over a bench-selectable connections list the
way Electroglas already does, which is a real architecture change, not a
button here. The Add Prober button says so rather than pretending to work.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

import yaml

from instruments.gpib_base import get_resource_path

_YAML_PATH = "instruments/instruments.yaml"

# The five keys AtomicaDashboard.init_hardware() actually connects, in the
# order it connects them - see gui/app.py's ACCRETECH_REQUIRED_DRIVERS.
_ACCRETECH_KEYS = ("prober", "smu", "dmm", "switch_matrix", "wave_gen")
_KEY_LABELS = {
    "prober": "Prober", "smu": "SMU", "dmm": "DMM",
    "switch_matrix": "Switch Matrix", "wave_gen": "Wave Gen",
}


def _load_yaml() -> dict:
    path = get_resource_path(_YAML_PATH)
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _save_yaml(data: dict) -> None:
    path = get_resource_path(_YAML_PATH)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, default_flow_style=False, sort_keys=False)


class AccretechSetupPanel(ttk.Frame):
    def __init__(self, parent, controller, main_layout=None):
        super().__init__(parent)
        self.controller = controller
        self._main_layout = main_layout

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        bar = ttk.Frame(self, padding=6)
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(bar, text="Prober bench: probe08 (the only one Accretech "
                            "connects today)",
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Button(bar, text="＋ Add Prober…", command=self._add_prober_info).pack(
            side="left", padx=(12, 0))

        frame = ttk.Frame(self, padding=(6, 0, 6, 6))
        frame.grid(row=1, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        cols = ("key", "name", "protocol", "address", "timeout")
        self._tree = ttk.Treeview(frame, columns=cols, show="headings",
                                  selectmode="browse")
        heads = [("key", "Slot", 100), ("name", "Instrument", 200),
                 ("protocol", "Protocol", 90), ("address", "Address", 220),
                 ("timeout", "Timeout (ms)", 90)]
        for cid, text, width in heads:
            self._tree.heading(cid, text=text)
            self._tree.column(cid, width=width,
                              anchor="center" if cid in ("protocol", "timeout") else "w")
        self._tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.bind("<Double-Button-1>", lambda _e: self._edit_selected())

        btns = ttk.Frame(frame)
        btns.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(btns, text="✎ Edit Selected…", command=self._edit_selected).pack(
            side="left")
        ttk.Label(btns, text="Restart the app (or Refresh Connections) for an "
                             "address change to take effect on an open session.",
                 foreground="#6b7280", font=("Segoe UI", 8)).pack(
                 side="left", padx=(10, 0))

        self._refresh_table()

    def _log(self, msg: str):
        try:
            self.controller.log(msg)
        except Exception:
            pass

    def _add_prober_info(self):
        messagebox.showinfo(
            "Not Wired Up Yet",
            "Accretech connects one fixed bench (probe08) - its five "
            "instrument keys are hardcoded into AtomicaDashboard."
            "init_hardware()'s own connect list, not read from a "
            "per-bench profile the way Electroglas's probe02/probe03 "
            "are.\n\nAdding a second real Accretech prober needs that "
            "connect list to become bench-selectable first - not "
            "something this button can do safely on its own.")

    def _refresh_table(self):
        self._tree.delete(*self._tree.get_children())
        try:
            data = _load_yaml()
        except (OSError, yaml.YAMLError) as exc:
            self._log(f"[SETUP] Could not read instruments.yaml: {exc}")
            return
        inst = data.get("instruments") or {}
        for key in _ACCRETECH_KEYS:
            entry = inst.get(key)
            if not entry:
                continue
            self._tree.insert("", "end", iid=key, values=(
                _KEY_LABELS.get(key, key), entry.get("name", key),
                entry.get("protocol", "GPIB"), entry.get("address", ""),
                entry.get("timeout_ms", 3000)))

    def _selected_key(self):
        sel = self._tree.selection()
        return sel[0] if sel else None

    def _edit_selected(self):
        key = self._selected_key()
        if not key:
            return
        try:
            data = _load_yaml()
        except (OSError, yaml.YAMLError) as exc:
            messagebox.showerror("Read Failed", str(exc))
            return
        entry = (data.get("instruments") or {}).get(key, {})
        dlg = _InstrumentDialog(
            self, title=f"Edit {_KEY_LABELS.get(key, key)}",
            initial=(entry.get("name", key), entry.get("protocol", "GPIB"),
                    entry.get("address", ""), entry.get("timeout_ms", 3000)))
        self.wait_window(dlg)
        if dlg.result is None:
            return
        name, protocol, address, timeout_ms = dlg.result
        data.setdefault("instruments", {}).setdefault(key, {})
        data["instruments"][key].update({
            "name": name, "protocol": protocol, "address": address,
            "timeout_ms": timeout_ms,
        })
        try:
            _save_yaml(data)
        except OSError as exc:
            messagebox.showerror("Save Failed", str(exc))
            return
        self._log(f"[SETUP] probe08: updated {_KEY_LABELS.get(key, key)} "
                  f"({name!r} @ {address})")
        self._refresh_table()


class _InstrumentDialog(tk.Toplevel):
    def __init__(self, parent, title: str, initial: tuple):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.result = None

        body = ttk.Frame(self, padding=10)
        body.pack(fill="both", expand=True)
        name0, protocol0, addr0, timeout0 = initial

        row = 0
        ttk.Label(body, text="Name:").grid(row=row, column=0, sticky="e", pady=3)
        self._name_var = tk.StringVar(value=name0)
        ttk.Entry(body, textvariable=self._name_var, width=32).grid(
            row=row, column=1, sticky="w", padx=6, pady=3)

        row += 1
        ttk.Label(body, text="Protocol:").grid(row=row, column=0, sticky="e", pady=3)
        self._protocol_var = tk.StringVar(value=protocol0)
        ttk.Combobox(body, textvariable=self._protocol_var, state="readonly",
                    values=("GPIB", "USB_TMC"), width=12).grid(
                    row=row, column=1, sticky="w", padx=6, pady=3)

        row += 1
        ttk.Label(body, text="Address:").grid(row=row, column=0, sticky="e", pady=3)
        self._addr_var = tk.StringVar(value=addr0)
        ttk.Entry(body, textvariable=self._addr_var, width=32).grid(
            row=row, column=1, sticky="w", padx=6, pady=3)

        row += 1
        ttk.Label(body, text="Timeout (ms):").grid(row=row, column=0, sticky="e", pady=3)
        self._timeout_var = tk.StringVar(value=str(timeout0))
        ttk.Entry(body, textvariable=self._timeout_var, width=10).grid(
            row=row, column=1, sticky="w", padx=6, pady=3)

        row += 1
        btns = ttk.Frame(body)
        btns.grid(row=row, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=4)
        ttk.Button(btns, text="OK", command=self._on_ok).pack(side="left")

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _on_ok(self):
        name = self._name_var.get().strip()
        address = self._addr_var.get().strip()
        if not name or not address:
            messagebox.showerror("Missing Info", "Name and address are required.",
                                 parent=self)
            return
        try:
            timeout_ms = int(self._timeout_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Timeout", "Timeout (ms) must be a whole number.",
                                 parent=self)
            return
        self.result = (name, self._protocol_var.get(), address, timeout_ms)
        self.destroy()
