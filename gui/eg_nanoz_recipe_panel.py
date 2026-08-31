"""Shot list + Global Pass/Fail Limits + per-touchdown measurement, for the
Electroglas NanoZ Recipe tab - mirrors gui/nanoz_panel.py's own Recipe tab
shape (shot treeview with Add/Duplicate/Remove/Reorder/board-toggle,
named recipe save/load/delete, Pass/Fail Limits).

WAFER DATA SOURCE: the same Wafer Builder die map the normal side's
Wafer Builder tab uses - NOT a separately-imported .xlsx wafer plan.
Accretech's NanoZPanel overlays the Wafer Builder map onto its own
internal (prober-native) wafer map; Electroglas has no internal map of
its own (no onboard wafer map, per electroglas_2001x.py), so here the
Wafer Builder map IS the only wafer data, taken directly - see
_wafer_plan_from_wafer_builder, which reads main_layout.recipe_gen the
same way nanoz_panel.NanoZPanel._wafer_builder_dies already does for
Accretech, then groups each column's dies into probe-height-tall
touchdown windows top-down (nzb.build_shots_from_windows) - the
touchdown's reference point is always the TOP die of the column, per
the physical probe card's own convention.

Board I/O itself (discovery/connect/console) lives on
gui/eg_nanoz_setup_panel.py's EgNanozSetupPanel, passed in here as
`setup_panel` - this panel only reads its .boards/.identities/.queue.
"""

import time
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

import instruments.nanoz_board as nzb

DEFAULT_PROBE_HEIGHT = 20


def _wafer_plan_from_wafer_builder(main_layout, probe_height=DEFAULT_PROBE_HEIGHT):
    """Live wafer plan built from the Wafer Builder tab's Die Map, in the
    same shape instruments/nanoz_board.WaferPlan already provides for an
    imported .xlsx - so touchdown_slot_exclusions/build_shots_from_windows
    work unchanged regardless of which source produced it."""
    gen = getattr(main_layout, "recipe_gen", None)
    if gen is None:
        return None
    try:
        dpx, dpy = gen._die_pitch()
    except Exception:
        return None
    if not dpx or not dpy:
        return None
    dies, serial_to_rc = {}, {}
    for d in gen._die_positions():
        if d.get("status") != "normal" or not d.get("die_id"):
            continue
        row, col = round(d["y"] / dpy), round(d["x"] / dpx)
        serial = str(d["die_id"])
        dies[(row, col)] = {"serial": serial, "status": "product"}
        serial_to_rc[serial.upper()] = (row, col)
    if not dies:
        return None
    by_col: dict = {}
    for (row, col) in dies:
        by_col.setdefault(col, []).append(row)
    touchdowns = []
    for col, rows in sorted(by_col.items()):
        rows.sort()
        start = rows[0]
        while start <= rows[-1]:
            touchdowns.append((start, col))
            start += probe_height
    return nzb.WaferPlan(dies=dies, serial_to_rc=serial_to_rc,
                         touchdowns=touchdowns, probe_height=probe_height)


class EgNanozRecipePanel(ttk.Frame):
    def __init__(self, parent, controller, setup_panel, get_ata_folder, log_fn):
        super().__init__(parent)
        self.controller = controller
        self._setup = setup_panel
        self._get_ata_folder = get_ata_folder
        self._log = log_fn

        self._wafer_plan: "nzb.WaferPlan | None" = None
        self._shots: list = []
        self._current_recipe_name: "str | None" = None
        # Set by set_run_panel() once gui/eg_nanoz_layout.py has built both
        # tabs - see that method's docstring.
        self._run_panel = None

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
        self.rowconfigure(3, weight=1)
        self._build_wafer_row()
        self._build_recipe_name_row()
        self._build_shot_bar()
        self._build_shot_tree()
        self._build_limits_row()

    def _eg_ui(self):
        return self.controller._by_system["electroglas"]["ui"]

    # -- wafer data (Wafer Builder, live) --------------------------------

    def _build_wafer_row(self):
        lf = ttk.LabelFrame(self, text="Wafer Data — same map as the Wafer Builder tab", padding=6)
        lf.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        self._plan_lbl = ttk.Label(lf, text="No die map yet.", foreground="gray")
        self._plan_lbl.pack(side="left")
        ttk.Label(lf, text="Probe height:").pack(side="left", padx=(12, 2))
        self._probe_height_var = tk.StringVar(value=str(DEFAULT_PROBE_HEIGHT))
        ttk.Entry(lf, textvariable=self._probe_height_var, width=4).pack(side="left")
        ttk.Button(lf, text="↻ Refresh from Wafer Builder", command=self._refresh_wafer_plan
                  ).pack(side="left", padx=(10, 0))

    def get_wafer_plan(self):
        return self._wafer_plan

    def _refresh_wafer_plan(self):
        try:
            probe_height = int(self._probe_height_var.get())
        except ValueError:
            probe_height = DEFAULT_PROBE_HEIGHT
        plan = _wafer_plan_from_wafer_builder(self._eg_ui(), probe_height)
        if plan is None:
            self._plan_lbl.config(
                text="No Wafer Builder die map yet - set die IDs on the normal "
                     "Electroglas side's Wafer Builder tab first.", foreground="#b45309")
            return
        self._wafer_plan = plan
        self._plan_lbl.config(
            text=f"{len(plan.dies)} dies, {len(plan.touchdowns)} touchdowns "
                 f"(probe height {plan.probe_height})", foreground="black")
        self._log(f"[NANOZ] Wafer data refreshed from Wafer Builder: "
                  f"{len(plan.dies)} die(s), {len(plan.touchdowns)} touchdown(s).")
        if self._run_panel is not None:
            self._run_panel.refresh_wafer_map()

    def on_ata_folder_loaded(self):
        self._refresh_wafer_plan()
        self._refresh_recipe_name_cb()

    # -- named recipe (shot list) -----------------------------------------

    def _build_recipe_name_row(self):
        row = ttk.Frame(self)
        row.grid(row=1, column=0, sticky="ew", padx=6, pady=2)
        ttk.Label(row, text="Recipe:").pack(side="left")
        self._recipe_name_var = tk.StringVar(value="")
        self._recipe_name_cb = ttk.Combobox(row, textvariable=self._recipe_name_var,
                                            state="readonly", width=24)
        self._recipe_name_cb.pack(side="left", padx=(4, 4))
        self._recipe_name_cb.bind("<<ComboboxSelected>>", lambda _e: self._load_named_recipe())
        ttk.Button(row, text="💾 Save As...", command=self._save_recipe_as).pack(side="left", padx=2)
        ttk.Button(row, text="🗑 Delete", command=self._delete_named_recipe).pack(side="left", padx=2)
        self._recipe_active_lbl = ttk.Label(row, text="(no recipe saved yet)", foreground="#6b7280")
        self._recipe_active_lbl.pack(side="left", padx=(12, 0))

    def _refresh_recipe_name_cb(self):
        folder = self._get_ata_folder()
        names = nzb.list_recipe_names(folder) if folder else []
        self._recipe_name_cb.config(values=names)
        self._recipe_name_var.set(self._current_recipe_name or "")
        text = (f"active: {self._current_recipe_name}" if self._current_recipe_name
               else "(unsaved - Save As... to keep this recipe)")
        self._recipe_active_lbl.config(text=text)

    def _save_recipe_as(self):
        folder = self._get_ata_folder()
        if not folder:
            messagebox.showerror("No ATA Folder", "Load an ATA folder first.")
            return
        if not self._shots:
            messagebox.showinfo("No Shots", "Compute or add shots before saving a recipe.")
            return
        name = simpledialog.askstring("Save Recipe", "Recipe name:",
                                      initialvalue=self._current_recipe_name or "", parent=self)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if name in nzb.list_recipe_names(folder) and not messagebox.askyesno(
                "Overwrite Recipe", f"A recipe named '{name}' already exists - overwrite it?"):
            return
        nzb.save_named_recipe(folder, name, self._shots)
        self._current_recipe_name = name
        self._refresh_recipe_name_cb()
        self._log(f"[NANOZ] Recipe saved as '{name}' - {len(self._shots)} shot(s).")

    def _load_named_recipe(self, name=None):
        folder = self._get_ata_folder()
        if not folder:
            return
        name = name or self._recipe_name_var.get()
        if not name:
            return
        self._shots = nzb.load_named_recipe(folder, name)
        self._current_recipe_name = name
        nzb.set_active_recipe(folder, name)
        self._redraw_shot_tree()
        self._refresh_recipe_name_cb()
        self._log(f"[NANOZ] Recipe '{name}' loaded - {len(self._shots)} shot(s).")

    def _delete_named_recipe(self):
        folder = self._get_ata_folder()
        name = self._recipe_name_var.get()
        if not folder or not name:
            return
        if not messagebox.askyesno("Delete Recipe", f"Delete recipe '{name}'?"):
            return
        nzb.delete_named_recipe(folder, name)
        if self._current_recipe_name == name:
            self._current_recipe_name = None
        self._refresh_recipe_name_cb()

    # -- shot list ----------------------------------------------------------

    def get_shots(self):
        return self._shots

    def set_run_panel(self, run_panel):
        """Wired by gui/eg_nanoz_layout.py once both tabs exist - this is
        the ONLY thing this panel reads off the Run tab (its pickable
        WaferMapPanel), and only ever through get_picked(), which returns
        a fresh sorted list - never a reference into that map's own
        internal state, let alone the real Wafer Builder map underneath
        it. See _shots_from_map_selection and this module's docstring."""
        self._run_panel = run_panel

    def _build_shot_bar(self):
        bar = ttk.Frame(self)
        bar.grid(row=2, column=0, sticky="ew", padx=6, pady=2)
        ttk.Button(bar, text="⬅ Take From Map Selection", command=self._shots_from_map_selection
                  ).pack(side="left")
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(bar, text="＋ Add", command=self._add_shot).pack(side="left")
        ttk.Button(bar, text="⎘ Duplicate", command=self._duplicate_shot).pack(side="left", padx=4)
        ttk.Button(bar, text="🗑 Remove", command=self._remove_shots).pack(side="left", padx=4)
        ttk.Button(bar, text="▲", width=3, command=lambda: self._move_shot(-1)).pack(
            side="left", padx=(10, 2))
        ttk.Button(bar, text="▼", width=3, command=lambda: self._move_shot(1)).pack(side="left")
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(bar, text="Enable All Boards",
                  command=lambda: self._set_selected_boards(True)).pack(side="left", padx=4)
        ttk.Button(bar, text="Disable All Boards",
                  command=lambda: self._set_selected_boards(False)).pack(side="left", padx=4)

    def _build_shot_tree(self):
        frame = ttk.Frame(self)
        frame.grid(row=3, column=0, sticky="nsew", padx=6, pady=(2, 6))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self._tree = ttk.Treeview(frame, columns=("seq",), show="headings",
                                  selectmode="extended", height=10)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.bind("<Button-1>", self._on_tree_click)
        self._tree.bind("<Double-1>", self._on_tree_double_click)
        self._redraw_shot_tree()

    def _ports(self):
        return sorted(self._setup.boards.keys())

    def _board_label(self, sn):
        ident = self._setup.identities.get(sn)
        if ident and (ident.slot0 or ident.slot1):
            return f"{sn} · slots {ident.slot0 or '—'}/{ident.slot1 or '—'}"
        return sn

    def _redraw_shot_tree(self):
        self._rebuild_shot_columns_only()
        self._tree.delete(*self._tree.get_children())
        ports = self._ports()
        for i, shot in enumerate(self._shots, 1):
            excluded = shot.get("excluded_boards", set())
            active_n = sum(1 for p in ports if p not in excluded)
            vals = [str(i), shot.get("label") or f"Shot {i}", f"{active_n}/{len(ports)}"]
            vals += ["·" if p in excluded else "✓" for p in ports]
            self._tree.insert("", "end", values=vals)

    def _rebuild_shot_columns_only(self):
        ports = self._ports()
        cols = ("seq", "label", "active") + tuple(ports)
        if tuple(self._tree["columns"]) != cols:
            self._tree.configure(columns=cols)
            heads = [("seq", "#", 36), ("label", "Label", 220), ("active", "Active", 70)]
            heads += [(p, self._board_label(p), 110) for p in ports]
            for cid, text, width in heads:
                self._tree.heading(cid, text=text)
                self._tree.column(cid, width=width, anchor="w" if cid == "label" else "center")

    def _shots_from_map_selection(self):
        """The only way a wafer selection becomes this recipe's touchdown
        list - mirrors recipe_panel.RecipePanel._sites_from_map ("Take
        from map selection") on the normal side exactly: read picks off
        the Run tab's map, snapshot them into plain shot dicts, replace
        self._shots. Never touches the wafer plan or the real Wafer
        Builder map - get_picked() already returns a fresh copy (see
        wafer_map_view.WaferMapPanel.get_picked), and the Run tab's map
        itself is a separate WaferMapPanel instance populated by copying
        rows out of the wafer plan (see EgNanozRunPanel.refresh_wafer_map),
        never a shared reference to gui/recipe_gen_panel.py's live object.
        """
        if self._wafer_plan is None:
            self._refresh_wafer_plan()
        plan = self._wafer_plan
        if plan is None:
            messagebox.showerror("No Wafer Data", "Refresh from Wafer Builder first.")
            return
        if self._run_panel is None:
            messagebox.showerror("No Run Tab", "Run tab not available.")
            return
        picks = self._run_panel.wafer_map.get_picked()
        if not picks:
            messagebox.showinfo("No Selection", "Click the top die of each touchdown "
                                                "you want on the Run tab's map first.")
            return
        ports = self._ports()
        slots_by_port = {sn: self._setup.identities[sn].chip_slots() for sn in ports}
        self._shots = nzb.build_shots_from_windows(plan, picks, ports, slots_by_port)
        self._redraw_shot_tree()
        self._log(f"[NANOZ] Took {len(self._shots)} shot(s) from the map selection.")

    def _selected_indices(self):
        return sorted(self._tree.index(iid) for iid in self._tree.selection())

    def _add_shot(self):
        self._shots.append({"label": "", "excluded_boards": set()})
        self._redraw_shot_tree()

    def _duplicate_shot(self):
        idxs = self._selected_indices()
        if not idxs:
            return
        idx = idxs[0]
        clone = dict(self._shots[idx])
        clone["excluded_boards"] = set(clone.get("excluded_boards", set()))
        self._shots.insert(idx + 1, clone)
        self._redraw_shot_tree()

    def _remove_shots(self):
        for i in reversed(self._selected_indices()):
            del self._shots[i]
        self._redraw_shot_tree()

    def _move_shot(self, delta):
        idxs = self._selected_indices()
        if not idxs:
            return
        idx = idxs[0]
        new_idx = idx + delta
        if not (0 <= new_idx < len(self._shots)):
            return
        self._shots[idx], self._shots[new_idx] = self._shots[new_idx], self._shots[idx]
        self._redraw_shot_tree()

    def _set_selected_boards(self, included):
        idxs = self._selected_indices()
        if not idxs:
            return
        ports = self._ports()
        for i in idxs:
            self._shots[i]["excluded_boards"] = set() if included else set(ports)
        self._redraw_shot_tree()

    def _rename_shot(self, idx):
        if not (0 <= idx < len(self._shots)):
            return
        new = simpledialog.askstring("Rename Shot", "Label for this shot:",
                                     initialvalue=self._shots[idx].get("label", ""), parent=self)
        if new is None:
            return
        self._shots[idx]["label"] = new.strip()
        self._redraw_shot_tree()

    def _on_tree_click(self, event):
        if self._tree.identify_region(event.x, event.y) != "cell":
            return
        row_iid = self._tree.identify_row(event.y)
        col_id = self._tree.identify_column(event.x)
        if not row_iid or not col_id:
            return
        cols = self._tree["columns"]
        col_idx = int(col_id[1:]) - 1
        if not (0 <= col_idx < len(cols)):
            return
        port = cols[col_idx]
        if port not in self._ports():
            return
        idx = self._tree.index(row_iid)
        excluded = self._shots[idx].setdefault("excluded_boards", set())
        if port in excluded:
            excluded.discard(port)
        else:
            excluded.add(port)
        self._redraw_shot_tree()

    def _on_tree_double_click(self, event):
        if self._tree.identify_region(event.x, event.y) != "cell":
            return
        row_iid = self._tree.identify_row(event.y)
        col_id = self._tree.identify_column(event.x)
        if not row_iid or not col_id:
            return
        cols = self._tree["columns"]
        col_idx = int(col_id[1:]) - 1
        if 0 <= col_idx < len(cols) and cols[col_idx] == "label":
            self._rename_shot(self._tree.index(row_iid))

    # -- global pass/fail limits -----------------------------------------

    def _build_limits_row(self):
        lf = ttk.LabelFrame(self, text="Global Pass/Fail Limits", padding=6)
        lf.grid(row=4, column=0, sticky="ew", padx=6, pady=2)
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

    def run_cycle_and_collect(self, shot_index: int, timeout_s: float = 15.0):
        """Runs one shot's whole 1x20 touchdown window - shot_index into
        self._shots (see _compute_shots), whose excluded_boards is the
        (possibly manually overridden) source of truth for which board/chip
        actually fires, rather than recomputing exclusions from the wafer
        plan on every run - a shot's manual toggle (Recipe tab, click a
        board cell) has to stick.

        Returns (ok: bool, slot_verdicts: dict[int, bool], log_lines: list[str]).
        A slot with no product die under it (off-wafer/reference) is left
        out of slot_verdicts entirely, same as a shot's NA corners in the
        Electroglas PMA run - not measured, not counted.
        """
        if not (0 <= shot_index < len(self._shots)):
            return False, {}, ["[NANOZ] No shot at that index."]
        shot = self._shots[shot_index]
        return self._run_cycle_core(shot["die_column"], shot["td_start_row"],
                                    shot.get("excluded_boards", set()), timeout_s)

    def run_cycle_at(self, die_col: int, start_row: int, timeout_s: float = 15.0):
        """Ad-hoc single-touchdown measurement at an explicit wafer-grid
        position, NOT tied to a saved shot - used by the Run tab's manual
        "Measure" button (mirrors the normal Electroglas Run tab's own
        Measure, instrument_panel._exec2_touchdown_measure, which also
        measures wherever the chuck currently is rather than requiring a
        selected recipe row). Only the wafer plan's own computed
        exclusions apply here - there is no shot-level manual override to
        honor since this isn't a saved shot."""
        return self._run_cycle_core(die_col, start_row, set(), timeout_s)

    def _run_cycle_core(self, die_col: int, start_row: int, excluded_boards: set,
                        timeout_s: float = 15.0):
        plan = self._wafer_plan
        if plan is None:
            return False, {}, ["[NANOZ] No wafer data/shot to run."]
        end_row = start_row + plan.probe_height - 1
        exclusions = nzb.touchdown_slot_exclusions(die_col, start_row, end_row, plan)

        boards, identities, q = self._setup.boards, self._setup.identities, self._setup.queue
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
            if exclusions.get(slot) is None and sn not in excluded_boards:
                active_boards.add(sn)

        if not active_boards:
            return True, {}, [f"[NANOZ] Shot at (col {die_col}, top row {start_row}): "
                              "no active board has a product die here - skipped."]

        for sn in active_boards:
            top = plan.dies.get((start_row, die_col))
            die_map_per_board[sn][None] = (start_row, die_col, top["serial"] if top else "")
            boards[sn].set_active_die(die_map_per_board[sn])

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
            if bc is None or bc[0] in excluded_boards:
                continue  # manually disabled for this shot - not measured, not counted
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
            import os
            path = os.path.join(folder, "ata_nanoz_electroglas_results.csv")
            for row in csv_rows:
                nzb.append_csv_row(path, row)

        ok = all(slot_verdicts.values()) if slot_verdicts else True
        return ok, slot_verdicts, logs
