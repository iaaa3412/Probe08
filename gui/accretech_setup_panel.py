"""Setup tab (Accretech) - add/edit prober benches, their instrument
addresses, and (new) which MODEL occupies a given slot, without hand-editing
GUI System/accretech_probers.yaml.

Same shape as gui/eg_setup_panel.py on purpose - Accretech used to be one
hardcoded bench with no per-instrument model choice at all (see
instruments/accretech_profiles.py's own module docstring for why MODEL is
the one real difference from the Electroglas version: eg profiles only vary
which keys are fitted, never what class a key resolves to). Editing a
bench's addresses/models here only pushes into instruments.yaml (the file
the actual drivers open) for the bench that is currently ACTIVE - an
already-open session keeps its old handle regardless, same "restart/Refresh
Connections to take effect live" caveat the old single-bench version of this
panel already carried.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from instruments import accretech_profiles

_KEY_LABELS = {
    "prober": "Prober", "smu": "SMU", "dmm": "DMM",
    "switch_matrix": "Switch Matrix", "wave_gen": "Wave Gen",
}


class AccretechSetupPanel(ttk.Frame):
    def __init__(self, parent, controller, main_layout=None):
        super().__init__(parent)
        self.controller = controller
        self._main_layout = main_layout
        self._bench_var = tk.StringVar(value="")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_bench_bar()
        self._build_table()
        self._refresh_benches()

    def _log(self, msg: str):
        try:
            self.controller.log(msg)
        except Exception:
            pass

    # -- bench bar ----------------------------------------------------------

    def _build_bench_bar(self):
        bar = ttk.Frame(self, padding=6)
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(bar, text="Prober bench:").pack(side="left")
        self._bench_cb = ttk.Combobox(bar, textvariable=self._bench_var,
                                      state="readonly", width=16)
        self._bench_cb.pack(side="left", padx=(4, 8))
        self._bench_cb.bind("<<ComboboxSelected>>", lambda _e: self._on_bench_picked())
        ttk.Button(bar, text="＋ Add Prober…", command=self._add_prober).pack(
            side="left", padx=2)
        self._active_lbl = tk.StringVar(value="")
        ttk.Label(bar, textvariable=self._active_lbl, foreground="#16a34a",
                 font=("Segoe UI", 8, "italic")).pack(side="left", padx=(10, 0))

    def _refresh_benches(self):
        names = accretech_profiles.profile_names()
        self._bench_cb.config(values=names)
        if self._bench_var.get() not in names:
            self._bench_var.set(accretech_profiles.active_name()
                                or (names[0] if names else ""))
        self._update_active_label()
        self._refresh_table()

    def _update_active_label(self):
        active = accretech_profiles.active_name()
        if self._bench_var.get() == active:
            self._active_lbl.set(f"● currently active ({active})")
        else:
            self._active_lbl.set(f"active bench is {active!r} - "
                                 "switch to it from the toolbar to test changes live")

    def _on_bench_picked(self):
        self._update_active_label()
        self._refresh_table()

    def _add_prober(self):
        source = self._bench_var.get()
        if not source:
            messagebox.showerror("No Bench", "No existing prober to copy from.")
            return
        name = simpledialog.askstring(
            "Add Prober",
            f"New prober name (starts as a copy of {source!r} - "
            "every instrument, address, and model comes along, ready to edit):",
            parent=self)
        if not name:
            return
        try:
            accretech_profiles.add_profile(name.strip(), based_on=source)
        except (ValueError, KeyError) as exc:
            messagebox.showerror("Add Prober Failed", str(exc))
            return
        self._log(f"[SETUP] Added Accretech prober {name!r} (copy of {source!r})")
        self._bench_var.set(name.strip())
        self._refresh_benches()

    # -- instrument table -----------------------------------------------------

    def _build_table(self):
        frame = ttk.Frame(self, padding=(6, 0, 6, 6))
        frame.grid(row=1, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        cols = ("key", "model", "name", "address", "timeout")
        self._tree = ttk.Treeview(frame, columns=cols, show="headings",
                                  selectmode="browse")
        heads = [("key", "Slot", 100), ("model", "Model", 150),
                 ("name", "Instrument", 180), ("address", "GPIB Address", 200),
                 ("timeout", "Timeout (ms)", 90)]
        for cid, text, width in heads:
            self._tree.heading(cid, text=text)
            self._tree.column(cid, width=width,
                              anchor="center" if cid == "timeout" else "w")
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
                             "address/model change to take effect on an open session.",
                 foreground="#6b7280", font=("Segoe UI", 8)).pack(
                 side="left", padx=(10, 0))

    def _refresh_table(self):
        self._tree.delete(*self._tree.get_children())
        bench = self._bench_var.get()
        if not bench:
            return
        try:
            inst = accretech_profiles.instruments(bench)
        except KeyError:
            return
        for key in accretech_profiles.ACCR_KEYS:
            entry = inst.get(key)
            if not entry:
                continue
            self._tree.insert("", "end", iid=key, values=(
                _KEY_LABELS.get(key, key),
                entry.get("model", accretech_profiles.DEFAULT_MODEL.get(key, "")),
                entry.get("name", key), entry.get("address", ""),
                entry.get("timeout_ms", 3000)))

    def _selected_key(self):
        sel = self._tree.selection()
        return sel[0] if sel else None

    def _edit_selected(self):
        bench = self._bench_var.get()
        key = self._selected_key()
        if not bench or not key:
            return
        entry = accretech_profiles.instruments(bench).get(key, {})
        dlg = _InstrumentDialog(
            self, title=f"Edit {_KEY_LABELS.get(key, key)} on {bench!r}", key=key,
            initial=(entry.get("model", accretech_profiles.DEFAULT_MODEL.get(key, "")),
                    entry.get("name", key), entry.get("address", ""),
                    entry.get("timeout_ms", 3000)))
        self.wait_window(dlg)
        if dlg.result is None:
            return
        model, name, address, timeout_ms = dlg.result
        try:
            accretech_profiles.set_instrument(
                bench, key, name=name, address=address,
                timeout_ms=timeout_ms, model=model)
        except (ValueError, KeyError) as exc:
            messagebox.showerror("Edit Failed", str(exc))
            return
        self._log(f"[SETUP] {bench}: updated {_KEY_LABELS.get(key, key)} "
                  f"({model}, {name!r} @ {address})")
        self._after_edit(bench)

    def _after_edit(self, bench: str):
        self._refresh_table()
        # Only the ACTIVE bench's addresses feed the real drivers - editing a
        # bench that is not currently selected in the toolbar just saves to
        # the YAML for next time it IS selected.
        if bench == accretech_profiles.active_name():
            try:
                accretech_profiles.apply_to_instruments_yaml(bench)
            except Exception as exc:
                self._log(f"[SETUP] Could not push {bench!r} into "
                          f"instruments.yaml: {exc}")


class _InstrumentDialog(tk.Toplevel):
    """Edit form for one instrument slot - model, name, GPIB address,
    timeout. `key` fixes which slot this is (Accretech's five are always
    present on every bench, unlike Electroglas's add/remove-a-slot model),
    so only the model dropdown's own choices vary by key."""

    def __init__(self, parent, title: str, key: str, initial: tuple):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.result = None

        body = ttk.Frame(self, padding=10)
        body.pack(fill="both", expand=True)
        model0, name0, addr0, timeout0 = initial

        row = 0
        ttk.Label(body, text="Model:").grid(row=row, column=0, sticky="e", pady=3)
        self._model_var = tk.StringVar(value=model0)
        choices = accretech_profiles.MODEL_CHOICES.get(key, (model0,))
        model_cb = ttk.Combobox(body, textvariable=self._model_var,
                                state="readonly" if len(choices) > 1 else "disabled",
                                values=choices, width=29)
        model_cb.grid(row=row, column=1, sticky="w", padx=6, pady=3)

        row += 1
        ttk.Label(body, text="Name:").grid(row=row, column=0, sticky="e", pady=3)
        self._name_var = tk.StringVar(value=name0)
        ttk.Entry(body, textvariable=self._name_var, width=32).grid(
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
        self.result = (self._model_var.get(), name, address, timeout_ms)
        self.destroy()
