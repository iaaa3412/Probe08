"""NanoZ board management + per-touchdown measurement for the Electroglas
NanoZ main section (see gui/nanoz_mode.py, gui/eg_nanoz_layout.py).

Scope of this first version - deliberately narrower than the Accretech
NanoZPanel (gui/nanoz_panel.py), which also has charts, cassette
automation, named-recipe persistence with a manual excluded-boards editor,
and NanoZ_EK/EEPROM tooling. None of that is reproduced here yet; this
covers the load-bearing path only: connect boards, import a wafer plan,
set Global Pass/Fail Limits, and run one 1x20 touchdown window's cycle on
demand (called by gui/eg_nanoz_run_panel.py once per touchdown). Shot
exclusions (which boards/chips have no real die under them for a given
touchdown) are computed live from the current board slot assignments and
wafer plan every time a touchdown runs, via instruments/nanoz_board.py's
touchdown_slot_exclusions() - there is no separate "recipe" of saved
shots to keep in sync with the boards the way NanoZPanel's Recipe tab has,
since the wafer plan + live slot assignments are already the complete
picture for a given touchdown.
"""

import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import instruments.nanoz_board as nzb


class EgNanozRecipePanel(ttk.Frame):
    def __init__(self, parent, controller, get_ata_folder, log_fn):
        super().__init__(parent)
        self.controller = controller
        self._get_ata_folder = get_ata_folder
        self._log = log_fn

        self._identities: dict[str, nzb.BoardIdentity] = {}   # serial_number -> identity
        self._boards: dict[str, nzb.NanoZBoard] = {}          # serial_number -> live board
        self._queue: "queue.Queue" = queue.Queue()

        self._wafer_plan: "nzb.WaferPlan | None" = None
        self._wafer_plan_path: "str | None" = None

        self._pf_metric_var = tk.StringVar(value="Current")
        self._pf_limit_vars = {
            s: (tk.StringVar(value=""), tk.StringVar(value=""))
            for s in (1, 2, 3, 4)
        }

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._build_wafer_plan_row()
        self._build_limits_row()
        self._build_boards_row()

        self.after(200, self._drain_queue_loop)

    # -- wafer plan -----------------------------------------------------

    def _build_wafer_plan_row(self):
        lf = ttk.LabelFrame(self, text="Wafer Plan (.xlsx)", padding=6)
        lf.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        lf.columnconfigure(0, weight=1)
        self._plan_lbl = ttk.Label(lf, text="No wafer plan loaded.", foreground="gray")
        self._plan_lbl.grid(row=0, column=0, sticky="w")
        ttk.Button(lf, text="Import .xlsx...", command=self._import_wafer_plan
                  ).grid(row=0, column=1, padx=(6, 0))
        ttk.Button(lf, text="Reload from folder", command=self._reload_wafer_plan
                  ).grid(row=0, column=2, padx=(6, 0))

    def get_wafer_plan(self):
        return self._wafer_plan

    def _import_wafer_plan(self):
        folder = self._get_ata_folder()
        if not folder:
            messagebox.showwarning("Wafer Plan", "Load/select an ATA folder first.")
            return
        path = filedialog.askopenfilename(
            title="Import NanoZ wafer plan", filetypes=[("Excel workbook", "*.xlsx")])
        if not path:
            return
        try:
            dest = nzb.import_wafer_plan_into_folder(folder, path)
            plan = nzb.load_wafer_plan(dest)
        except Exception as e:
            messagebox.showerror("Wafer Plan", f"Could not import:\n{e}")
            return
        self._wafer_plan, self._wafer_plan_path = plan, dest
        self._refresh_plan_label()
        self._log(f"[NANOZ] Wafer plan imported: {len(plan.dies)} die(s), "
                  f"{len(plan.touchdowns)} touchdown(s).")

    def _reload_wafer_plan(self):
        folder = self._get_ata_folder()
        if not folder:
            return
        path = nzb.wafer_plan_path_in_folder(folder)
        if not os.path.isfile(path):
            self._log("[NANOZ] No wafer plan file in this ATA folder yet - use Import.")
            return
        try:
            self._wafer_plan = nzb.load_wafer_plan(path)
            self._wafer_plan_path = path
        except Exception as e:
            messagebox.showerror("Wafer Plan", f"Could not load:\n{e}")
            return
        self._refresh_plan_label()
        self._log(f"[NANOZ] Wafer plan reloaded: {len(self._wafer_plan.dies)} die(s), "
                  f"{len(self._wafer_plan.touchdowns)} touchdown(s).")

    def _refresh_plan_label(self):
        plan = self._wafer_plan
        if plan is None:
            self._plan_lbl.config(text="No wafer plan loaded.", foreground="gray")
            return
        self._plan_lbl.config(
            text=f"{os.path.basename(self._wafer_plan_path or '')} — "
                 f"{len(plan.dies)} dies, {len(plan.touchdowns)} touchdowns, "
                 f"probe height {plan.probe_height}",
            foreground="black")

    def on_ata_folder_loaded(self):
        """Called when the Electroglas NanoZ layout's ATA folder changes -
        picks up whatever wafer plan/known boards already live there."""
        self._reload_wafer_plan()
        self._load_known_boards()

    # -- global pass/fail limits -----------------------------------------

    def _build_limits_row(self):
        lf = ttk.LabelFrame(self, text="Global Pass/Fail Limits", padding=6)
        lf.grid(row=1, column=0, sticky="ew", padx=6, pady=2)
        ttk.Label(lf, text="Metric:").grid(row=0, column=0, sticky="w")
        ttk.OptionMenu(lf, self._pf_metric_var, self._pf_metric_var.get(),
                      "Current", "Voltage").grid(row=0, column=1, sticky="w", padx=(4, 12))
        ttk.Label(lf, text="(applied to every sensor S1-S4 reading; blank = not checked)",
                  foreground="#6b7280", font=("Segoe UI", 8)).grid(
                  row=0, column=2, sticky="w")
        for i, s in enumerate((1, 2, 3, 4), start=1):
            lo, hi = self._pf_limit_vars[s]
            ttk.Label(lf, text=f"S{s} min").grid(row=i, column=0, sticky="w")
            ttk.Entry(lf, textvariable=lo, width=10).grid(row=i, column=1, sticky="w")
            ttk.Label(lf, text="max").grid(row=i, column=1, sticky="e", padx=(0, 60))
            ttk.Entry(lf, textvariable=hi, width=10).grid(row=i, column=2, sticky="w")

    def _evaluate_limits(self, spl: dict) -> bool:
        metric = self._pf_metric_var.get()
        key_fmt = "adc_current_ma_s{}" if metric == "Current" else "dac_mv_s{}"
        for s in (1, 2, 3, 4):
            lo_s, hi_s = (v.get().strip() for v in self._pf_limit_vars[s])
            if not lo_s and not hi_s:
                continue
            val = spl.get(key_fmt.format(s))
            if val is None:
                return False
            try:
                if lo_s and val < float(lo_s):
                    return False
                if hi_s and val > float(hi_s):
                    return False
            except ValueError:
                continue
        return True

    # -- boards -----------------------------------------------------------

    def _build_boards_row(self):
        lf = ttk.LabelFrame(self, text="NanoZ Boards", padding=6)
        lf.grid(row=2, column=0, sticky="nsew", padx=6, pady=(2, 6))
        lf.rowconfigure(1, weight=1)
        lf.columnconfigure(0, weight=1)

        bar = ttk.Frame(lf)
        bar.grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Button(bar, text="Discover Boards", command=self._discover_boards).pack(side="left")
        ttk.Button(bar, text="Connect All", command=self._connect_all).pack(
            side="left", padx=(6, 0))
        ttk.Button(bar, text="Disconnect All", command=self._disconnect_all).pack(
            side="left", padx=(6, 0))
        ttk.Button(bar, text="Edit Slots...", command=self._edit_selected_slots).pack(
            side="left", padx=(6, 0))

        cols = ("sn", "port", "fw", "slot0", "slot1", "state")
        self._tree = ttk.Treeview(lf, columns=cols, show="headings", height=8)
        for col, head, width in (("sn", "Serial", 140), ("port", "Port", 70),
                                 ("fw", "Firmware", 90), ("slot0", "Chip0 slot", 80),
                                 ("slot1", "Chip1 slot", 80), ("state", "State", 90)):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=width, anchor="w")
        self._tree.grid(row=1, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, orient="vertical", command=self._tree.yview)
        sb.grid(row=1, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=sb.set)

        self._load_known_boards()

    def _load_known_boards(self):
        folder = self._get_ata_folder()
        if not folder:
            return
        for ident in nzb.load_known_boards(folder):
            if ident.serial_number:
                self._identities.setdefault(ident.serial_number, ident)
        self._refresh_tree()

    def _save_known_boards(self):
        folder = self._get_ata_folder()
        if folder:
            nzb.save_known_boards(folder, list(self._identities.values()))

    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        for sn, ident in sorted(self._identities.items()):
            board = self._boards.get(sn)
            state = board.state if board is not None else "not_connected"
            self._tree.insert("", "end", iid=sn, values=(
                sn, ident.port or ident.last_port or "", ident.firmware,
                ident.slot0 if ident.slot0 is not None else "",
                ident.slot1 if ident.slot1 is not None else "", state))

    def _discover_boards(self):
        def _work():
            found = nzb.discover_boards(log=lambda m: self.after(0, lambda: self._log(f"[NANOZ] {m}")))
            for ident in found:
                if ident.serial_number:
                    self._identities[ident.serial_number] = ident
            self.after(0, self._refresh_tree)
            self.after(0, self._save_known_boards)
        threading.Thread(target=_work, daemon=True).start()

    def _connect_all(self):
        for sn, ident in list(self._identities.items()):
            if sn in self._boards:
                continue
            port = ident.port or ident.last_port
            if not port:
                self._log(f"[NANOZ] {sn}: no known port - run Discover Boards first.")
                continue
            ident.port = port
            board = nzb.NanoZBoard(ident, self._queue, env_interval_s=1.0)
            try:
                board.start()
            except Exception as e:
                self._log(f"[NANOZ] {sn}: connect failed - {e}")
                continue
            self._boards[sn] = board
        self._refresh_tree()

    def _disconnect_all(self):
        for sn, board in list(self._boards.items()):
            try:
                board.stop()
            except Exception:
                pass
        self._boards.clear()
        self._refresh_tree()

    def _edit_selected_slots(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Edit Slots", "Select a board row first.")
            return
        sn = sel[0]
        ident = self._identities.get(sn)
        if ident is None:
            return
        dlg = tk.Toplevel(self)
        dlg.title(f"Slots for {sn}")
        dlg.transient(self)
        dlg.grab_set()
        v0 = tk.StringVar(value=str(ident.slot0) if ident.slot0 is not None else "")
        v1 = tk.StringVar(value=str(ident.slot1) if ident.slot1 is not None else "")
        frm = ttk.Frame(dlg, padding=10)
        frm.pack()
        ttk.Label(frm, text="Chip 0 (right) physical slot (1-20):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=v0, width=6).grid(row=0, column=1)
        ttk.Label(frm, text="Chip 1 (left) physical slot (1-20):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=v1, width=6).grid(row=1, column=1)

        def _save():
            def _parse(v):
                v = v.strip()
                return int(v) if v else None
            try:
                ident.slot0, ident.slot1 = _parse(v0.get()), _parse(v1.get())
            except ValueError:
                messagebox.showerror("Edit Slots", "Slots must be whole numbers.")
                return
            self._save_known_boards()
            self._refresh_tree()
            dlg.destroy()
        ttk.Button(frm, text="Save", command=_save).grid(row=2, column=0, columnspan=2, pady=(8, 0))

    def _drain_queue_loop(self):
        try:
            while True:
                item = self._queue.get_nowait()
                self._handle_packet(item)
        except queue.Empty:
            pass
        self.after(200, self._drain_queue_loop)

    def _handle_packet(self, item: dict):
        kind = item.get("kind")
        if kind == "text":
            self._log(f"[NANOZ {item.get('board_sn')}] {item.get('text')}")
        elif kind == "unrecognized":
            self._log(f"[NANOZ {item.get('board_sn')}] ? {item.get('raw')}")
        # "spl"/"env" packets are consumed directly by run_cycle_and_collect
        # via its own short-lived queue drain below, not here - this loop
        # only surfaces board log/error text between cycles.

    # -- per-touchdown measurement ----------------------------------------

    def get_connected_ports_and_slots(self):
        ports = list(self._boards.keys())
        slots_by_port = {sn: self._identities[sn].chip_slots() for sn in ports}
        return ports, slots_by_port

    def run_cycle_and_collect(self, die_col: int, start_row: int, timeout_s: float = 15.0):
        """Runs the whole 1x20 touchdown window whose TOP die is
        (start_row, die_col) in the wafer plan's own row/col space - the
        touchdown's reference point, per the wafer plan's own convention.

        Returns (ok: bool, slot_verdicts: dict[int, bool], log_lines: list[str]).
        A slot with no product die under it (off-wafer/reference) is left
        out of slot_verdicts entirely, same as a shot's NA corners in the
        Electroglas PMA run - not measured, not counted.
        """
        plan = self._wafer_plan
        if plan is None:
            return False, {}, ["[NANOZ] No wafer plan loaded - cannot run a cycle."]
        end_row = start_row + plan.probe_height - 1
        exclusions = nzb.touchdown_slot_exclusions(die_col, start_row, end_row, plan)

        slot_to_board_chip = {}
        for sn, ident in self._identities.items():
            if sn not in self._boards:
                continue
            for chip, slot in ident.chip_slots().items():
                if slot is not None:
                    slot_to_board_chip[slot] = (sn, chip)

        active_boards = set()
        die_map_per_board: dict[str, dict] = {}
        for slot in range(1, plan.probe_height + 1):
            bc = slot_to_board_chip.get(slot)
            if bc is None:
                continue
            sn, chip = bc
            row = start_row + slot - 1
            d = plan.dies.get((row, die_col))
            die_id = d["serial"] if d else ""
            die_map_per_board.setdefault(sn, {})[chip] = (row, die_col, die_id)
            if exclusions.get(slot) is None:
                active_boards.add(sn)

        if not active_boards:
            return True, {}, [f"[NANOZ] Touchdown (col {die_col}, top row {start_row}): "
                              "no connected board has a product die here - skipped."]

        for sn in active_boards:
            top = plan.dies.get((start_row, die_col))
            die_map_per_board[sn][None] = (start_row, die_col, top["serial"] if top else "")
            self._boards[sn].set_active_die(die_map_per_board[sn])

        # Drain anything stale before triggering, so this cycle's results
        # can't be misread as leftovers from a previous one.
        try:
            while True:
                self._queue.get_nowait()
        except queue.Empty:
            pass

        for sn in active_boards:
            self._boards[sn].run_cycle(0)

        wanted = {(sn, chip) for slot, (sn, chip) in slot_to_board_chip.items()
                 if sn in active_boards and exclusions.get(slot) is None}
        got: dict = {}
        import time as _time
        deadline = _time.time() + timeout_s
        while got.keys() < wanted and _time.time() < deadline:
            try:
                item = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            if item.get("kind") == "spl":
                key = (item.get("board_sn"), str(item.get("header_chip")))
                if key in wanted:
                    got[key] = item

        logs = []
        slot_verdicts = {}
        csv_rows = []
        for slot in range(1, plan.probe_height + 1):
            if exclusions.get(slot) is not None:
                continue
            bc = slot_to_board_chip.get(slot)
            row = start_row + slot - 1
            d = plan.dies.get((row, die_col))
            die_id = d["serial"] if d else ""
            if bc is None:
                slot_verdicts[slot] = False
                logs.append(f"[NANOZ] slot {slot} (die {die_id or '?'}): "
                           "FAIL - no board wired to this slot")
                continue
            sn, chip = bc
            pkt = got.get((sn, chip))
            if pkt is None:
                slot_verdicts[slot] = False
                logs.append(f"[NANOZ] slot {slot} (die {die_id or '?'}, {sn} chip{chip}): "
                           f"FAIL - no reading within {timeout_s:.0f}s")
                continue
            passed = self._evaluate_limits(pkt)
            slot_verdicts[slot] = passed
            logs.append(f"[NANOZ] slot {slot} (die {die_id or '?'}, {sn} chip{chip}): "
                       f"{'PASS' if passed else 'FAIL'}")
            csv_rows.append({
                "die_id": die_id, "row": row, "col": die_col, "slot": slot,
                "board_sn": sn, "chip": chip, "pass": passed,
                **{k: v for k, v in pkt.items()
                   if k.startswith(("adc_", "dac_", "heater"))},
            })

        folder = self._get_ata_folder()
        if folder and csv_rows:
            path = os.path.join(folder, "ata_nanoz_electroglas_results.csv")
            for row in csv_rows:
                nzb.append_csv_row(path, row)

        ok = all(slot_verdicts.values()) if slot_verdicts else True
        return ok, slot_verdicts, logs
