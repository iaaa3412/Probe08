import tkinter as tk
from tkinter import ttk, messagebox

import switch_topology as topo


class SwitchSettingsPanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._slots: list = [dict(s) for s in topo.slots()]
        self._roles: dict = {k: dict(v) for k, v in topo.row_roles().items()}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_header()
        self._build_slots_section()
        self._build_roles_section()
        self._build_footer()

    def _log(self, msg: str):
        self.controller.log(msg)

    def _build_header(self):
        hdr = ttk.Frame(self, padding=(10, 10, 10, 4))
        hdr.grid(row=0, column=0, sticky="ew")
        ttk.Label(hdr, text="Switch Matrix Settings",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(hdr, foreground="gray", font=("Segoe UI", 8), wraplength=780, justify="left",
                 text="Defines how the switch matrix is physically wired: which slots hold "
                      "cards (and how many probe-card pins/columns each one covers), and "
                      "which instrument each row letter (A-H) connects to. Recipes resolve "
                      "their HI/LO channel codes from this — saving changes here takes "
                      "effect immediately for any step computed afterward."
                 ).pack(anchor="w", pady=(2, 0))

    def _build_slots_section(self):
        lf = ttk.LabelFrame(self, text="Slots / Cards", padding=8)
        lf.grid(row=1, column=0, sticky="ew", padx=10, pady=(4, 4))
        lf.columnconfigure(0, weight=1)

        self._slots_tree = ttk.Treeview(
            lf, columns=("slot", "cols", "rows"), show="headings", height=4)
        for cid, text, width in [("slot", "Slot", 80), ("cols", "Columns (pins)", 120),
                                 ("rows", "Rows used", 320)]:
            self._slots_tree.heading(cid, text=text)
            self._slots_tree.column(cid, width=width, anchor="center" if cid != "rows" else "w")
        self._slots_tree.grid(row=0, column=0, sticky="ew")
        self._slots_tree.bind("<<TreeviewSelect>>", lambda _e: self._load_selected_slot())

        add_row = ttk.Frame(lf)
        add_row.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        ttk.Label(add_row, text="Slot ID:").pack(side="left")
        self._slot_id_var = tk.StringVar()
        ttk.Entry(add_row, textvariable=self._slot_id_var, width=6).pack(
            side="left", padx=(2, 10))
        ttk.Label(add_row, text="Columns:").pack(side="left")
        self._slot_cols_var = tk.StringVar(value="12")
        ttk.Entry(add_row, textvariable=self._slot_cols_var, width=6).pack(
            side="left", padx=(2, 10))

        rows_row = ttk.Frame(lf)
        rows_row.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        ttk.Label(rows_row, text="Rows on this card:").pack(side="left")
        self._slot_row_vars = {letter: tk.BooleanVar() for letter in topo.ROW_LETTERS}
        for letter in topo.ROW_LETTERS:
            ttk.Checkbutton(rows_row, text=letter,
                            variable=self._slot_row_vars[letter]).pack(side="left", padx=2)

        btn_row = ttk.Frame(lf)
        btn_row.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(btn_row, text="+ Add / Update Slot",
                  command=self._add_or_update_slot).pack(side="left")
        ttk.Button(btn_row, text="Remove Selected Slot",
                  command=self._remove_slot).pack(side="left", padx=(6, 0))

        self._refresh_slots_tree()

    def _refresh_slots_tree(self):
        self._slots_tree.delete(*self._slots_tree.get_children())
        for spec in self._slots:
            self._slots_tree.insert("", "end", iid=spec["slot"], values=(
                spec["slot"], spec.get("cols", 0), ",".join(spec.get("rows", []))))

    def _load_selected_slot(self):
        sel = self._slots_tree.selection()
        if not sel:
            return
        spec = next((s for s in self._slots if s["slot"] == sel[0]), None)
        if not spec:
            return
        self._slot_id_var.set(spec["slot"])
        self._slot_cols_var.set(str(spec.get("cols", 12)))
        active_rows = set(spec.get("rows", []))
        for letter, var in self._slot_row_vars.items():
            var.set(letter in active_rows)

    def _add_or_update_slot(self):
        slot_id = self._slot_id_var.get().strip()
        if not slot_id:
            messagebox.showerror("Missing Slot ID", "Enter a slot ID (e.g. 1, 2, 3...).")
            return
        try:
            cols = int(self._slot_cols_var.get().strip())
            if cols <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Columns", "Columns must be a positive integer.")
            return
        rows = [letter for letter in topo.ROW_LETTERS if self._slot_row_vars[letter].get()]
        if not rows:
            messagebox.showerror("No Rows Selected", "Pick at least one row for this slot.")
            return
        existing = next((s for s in self._slots if s["slot"] == slot_id), None)
        if existing:
            existing["cols"] = cols
            existing["rows"] = rows
        else:
            self._slots.append({"slot": slot_id, "cols": cols, "rows": rows})
        self._refresh_slots_tree()
        self._log(f"[SETTINGS] Slot '{slot_id}' set: {cols} columns, rows {','.join(rows)} "
                  "(not saved yet — click Save Settings)")

    def _remove_slot(self):
        sel = self._slots_tree.selection()
        if not sel:
            return
        slot_id = sel[0]
        self._slots = [s for s in self._slots if s["slot"] != slot_id]
        self._refresh_slots_tree()
        self._log(f"[SETTINGS] Slot '{slot_id}' removed (not saved yet — click Save Settings)")

    def _build_roles_section(self):
        lf = ttk.LabelFrame(self, text="Row Wiring (which instrument each row connects to)",
                            padding=8)
        lf.grid(row=2, column=0, sticky="nsew", padx=10, pady=(4, 4))
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)

        self._roles_tree = ttk.Treeview(
            lf, columns=("row", "instrument", "channel", "polarity", "label"),
            show="headings", height=8)
        for cid, text, width in [("row", "Row", 50), ("instrument", "Instrument", 90),
                                 ("channel", "Channel", 80), ("polarity", "Polarity", 80),
                                 ("label", "Label", 160)]:
            self._roles_tree.heading(cid, text=text)
            self._roles_tree.column(cid, width=width, anchor="center")
        self._roles_tree.grid(row=0, column=0, sticky="nsew")
        self._roles_tree.bind("<<TreeviewSelect>>", lambda _e: self._load_selected_role())

        edit_row = ttk.Frame(lf)
        edit_row.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        ttk.Label(edit_row, text="Row:").pack(side="left")
        self._role_row_var = tk.StringVar(value="A")
        ttk.Combobox(edit_row, textvariable=self._role_row_var, values=topo.ROW_LETTERS,
                    width=4, state="readonly").pack(side="left", padx=(2, 10))

        ttk.Label(edit_row, text="Instrument:").pack(side="left")
        self._role_instrument_var = tk.StringVar()
        inst_cb = ttk.Combobox(edit_row, textvariable=self._role_instrument_var,
                               values=["", "SMU", "DMM", "WGEN"], width=8, state="readonly")
        inst_cb.pack(side="left", padx=(2, 10))
        inst_cb.bind("<<ComboboxSelected>>", lambda _e: self._sync_role_channel_choices())

        ttk.Label(edit_row, text="Channel:").pack(side="left")
        self._role_channel_var = tk.StringVar()
        self._role_channel_cb = ttk.Combobox(edit_row, textvariable=self._role_channel_var,
                                             values=[], width=6, state="readonly")
        self._role_channel_cb.pack(side="left", padx=(2, 10))

        ttk.Label(edit_row, text="Polarity:").pack(side="left")
        self._role_polarity_var = tk.StringVar()
        self._role_polarity_cb = ttk.Combobox(edit_row, textvariable=self._role_polarity_var,
                                              values=list(topo.POLARITIES), width=6,
                                              state="readonly")
        self._role_polarity_cb.pack(side="left", padx=(2, 10))

        ttk.Button(edit_row, text="Apply to Row", command=self._apply_role).pack(
            side="left", padx=(8, 0))

        self._refresh_roles_tree()

    def _sync_role_channel_choices(self):
        instrument = self._role_instrument_var.get()
        if instrument == "SMU":
            self._role_channel_cb.config(values=list(topo.SMU_CHANNELS), state="readonly")
        elif instrument == "WGEN":
            self._role_channel_cb.config(values=list(topo.WGEN_CHANNELS), state="readonly")
        else:
            self._role_channel_var.set("")
            self._role_channel_cb.config(values=[], state="disabled")
        if instrument == "WGEN":
            self._role_polarity_var.set("HI")
            self._role_polarity_cb.config(state="disabled")
        else:
            self._role_polarity_cb.config(state="readonly")

    def _refresh_roles_tree(self):
        self._roles_tree.delete(*self._roles_tree.get_children())
        for letter in topo.ROW_LETTERS:
            role = self._roles.get(letter, {})
            self._roles_tree.insert("", "end", iid=letter, values=(
                letter, role.get("instrument", ""), role.get("channel", ""),
                role.get("polarity", ""), topo.role_label(role)))

    def _load_selected_role(self):
        sel = self._roles_tree.selection()
        if not sel:
            return
        letter = sel[0]
        role = self._roles.get(letter, {})
        self._role_row_var.set(letter)
        self._role_instrument_var.set(role.get("instrument", ""))
        self._sync_role_channel_choices()
        self._role_channel_var.set(role.get("channel", ""))
        self._role_polarity_var.set(role.get("polarity", ""))

    def _apply_role(self):
        letter = self._role_row_var.get()
        instrument = self._role_instrument_var.get()
        channel = self._role_channel_var.get() if instrument in ("SMU", "WGEN") else ""
        polarity = "HI" if instrument == "WGEN" else self._role_polarity_var.get()
        if instrument and not polarity:
            messagebox.showerror("Missing Polarity", "Pick HI or LO for this row.")
            return
        self._roles[letter] = {"instrument": instrument, "channel": channel,
                               "polarity": polarity}
        self._refresh_roles_tree()
        self._log(f"[SETTINGS] Row {letter} set to "
                  f"{topo.role_label(self._roles[letter])} (not saved yet — click Save Settings)")

    def _build_footer(self):
        bar = ttk.Frame(self, padding=(10, 4, 10, 10))
        bar.grid(row=3, column=0, sticky="ew")
        ttk.Button(bar, text="💾 Save Settings", command=self._save).pack(side="left")
        ttk.Button(bar, text="↺ Reset to Defaults", command=self._reset).pack(
            side="left", padx=(6, 0))
        self._status_var = tk.StringVar(value="")
        ttk.Label(bar, textvariable=self._status_var, foreground="#6b7280",
                 font=("Segoe UI", 8)).pack(side="left", padx=(10, 0))

    def _save(self):
        data = {"slots": [dict(s) for s in self._slots],
               "row_roles": {k: dict(v) for k, v in self._roles.items()}}
        topo.save_topology(data)
        self._status_var.set(f"Saved to {topo.TOPOLOGY_PATH}")
        self._log("[SETTINGS] Switch topology saved — recipe channel resolution "
                  "updates immediately.")

    def _reset(self):
        if not messagebox.askyesno(
                "Reset to Defaults",
                "Discard all changes and restore the default 2-slot Keithley 707B layout?"):
            return
        data = topo.reset_topology()
        self._slots = [dict(s) for s in data["slots"]]
        self._roles = {k: dict(v) for k, v in data["row_roles"].items()}
        self._refresh_slots_tree()
        self._refresh_roles_tree()
        self._status_var.set("Reset to defaults and saved.")
        self._log("[SETTINGS] Switch topology reset to defaults.")
