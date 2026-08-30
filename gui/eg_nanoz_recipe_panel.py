"""Wafer plan import + Global Pass/Fail Limits + per-touchdown measurement,
for the Electroglas NanoZ Recipe tab - mirrors gui/nanoz_panel.py's own
Recipe tab (minus the manual excluded-boards shot editor/named-recipe
persistence - see run_cycle_and_collect's own docstring for why that's
computed live instead here).

Board I/O itself (discovery/connect/console) lives on
gui/eg_nanoz_setup_panel.py's EgNanozSetupPanel, passed in here as
`setup_panel` - this panel only reads its .boards/.identities/.queue,
it does not own a second copy of any of them.
"""

import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import instruments.nanoz_board as nzb


class EgNanozRecipePanel(ttk.Frame):
    def __init__(self, parent, controller, setup_panel, get_ata_folder, log_fn):
        super().__init__(parent)
        self.controller = controller
        self._setup = setup_panel
        self._get_ata_folder = get_ata_folder
        self._log = log_fn

        self._wafer_plan: "nzb.WaferPlan | None" = None
        self._wafer_plan_path: "str | None" = None

        self._pf_metric_var = tk.StringVar(value="Current")
        self._pf_limit_vars = {
            s: (tk.StringVar(value=""), tk.StringVar(value=""))
            for s in (1, 2, 3, 4)
        }

        # Every die measured this session, most recent last - read by
        # gui/eg_nanoz_results_panel.py. Not persisted beyond the CSV
        # export run_cycle_and_collect already writes per die.
        self.results_history: list[dict] = []

        self.columnconfigure(0, weight=1)
        self._build_wafer_plan_row()
        self._build_limits_row()

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
        self._reload_wafer_plan()

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

    # -- per-touchdown measurement ----------------------------------------

    def run_cycle_and_collect(self, die_col: int, start_row: int, timeout_s: float = 15.0):
        """Runs the whole 1x20 touchdown window whose TOP die is
        (start_row, die_col) in the wafer plan's own row/col space - the
        touchdown's reference point, per the wafer plan's own convention.

        Board/chip -> physical slot exclusions are computed fresh from the
        wafer plan and the Setup tab's CURRENT board slot assignments every
        time this runs (nzb.touchdown_slot_exclusions), rather than from a
        separately maintained/saved shot list - the wafer plan plus live
        slot assignments are already the complete picture for any given
        touchdown, so there is nothing a saved shot could add except a
        second copy to keep in sync.

        Returns (ok: bool, slot_verdicts: dict[int, bool], log_lines: list[str]).
        A slot with no product die under it (off-wafer/reference) is left
        out of slot_verdicts entirely, same as a shot's NA corners in the
        Electroglas PMA run - not measured, not counted.
        """
        plan = self._wafer_plan
        if plan is None:
            return False, {}, ["[NANOZ] No wafer plan loaded - cannot run a cycle."]
        boards, identities, q = self._setup.boards, self._setup.identities, self._setup.queue
        end_row = start_row + plan.probe_height - 1
        exclusions = nzb.touchdown_slot_exclusions(die_col, start_row, end_row, plan)

        slot_to_board_chip = {}
        for sn, ident in identities.items():
            if sn not in boards:
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
            boards[sn].set_active_die(die_map_per_board[sn])

        # Drain anything stale before triggering, so this cycle's results
        # can't be misread as leftovers from a previous one.
        try:
            while True:
                q.get_nowait()
        except Exception:
            pass

        for sn in active_boards:
            boards[sn].run_cycle(0)

        wanted = {(sn, chip) for slot, (sn, chip) in slot_to_board_chip.items()
                 if sn in active_boards and exclusions.get(slot) is None}
        got: dict = {}
        deadline = time.time() + timeout_s
        while got.keys() < wanted and time.time() < deadline:
            try:
                item = q.get(timeout=0.2)
            except Exception:
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
            row_data = {
                "die_id": die_id, "row": row, "col": die_col, "slot": slot,
                "board_sn": sn, "chip": chip, "pass": passed,
                **{k: v for k, v in pkt.items()
                   if k.startswith(("adc_", "dac_", "heater"))},
            }
            csv_rows.append(row_data)
            self.results_history.append(row_data)

        folder = self._get_ata_folder()
        if folder and csv_rows:
            path = os.path.join(folder, "ata_nanoz_electroglas_results.csv")
            for row in csv_rows:
                nzb.append_csv_row(path, row)

        ok = all(slot_verdicts.values()) if slot_verdicts else True
        return ok, slot_verdicts, logs
