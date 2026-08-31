"""Electroglas NanoZ Run tab - walks the Recipe tab's computed shot list
(gui/eg_nanoz_recipe_panel.py's self._shots, one 1x20 touchdown window per
shot) using the Electroglas prober's own relative die-stepping (goto_die),
then triggers a NanoZ board cycle at each stop via
EgNanozRecipePanel.run_cycle_and_collect.

LAYOUT mirrors the normal Electroglas Run tab (instrument_panel.py's
_tab_execution2) as closely as this tab's own content allows: a top
control bar (bg #f1f5f9, Run/Pause/Stop + a state label on the right),
then a horizontal 25:20:55 split - [pitch/anchor/shot list] |
[Chuck Position: live ?P + Back/Next] | [Wafer Map] - same three-pane
shape and sash ratio as the normal tab's [EgPmaRunPanel] | [Chuck
Position + Recipe Steps] | [Wafer Map] split, just with NanoZ's own
content (die pitch/shot list instead of PMA touchdowns, no Recipe Steps
box since there is no SMU/DMM step list here).

Datum handling mirrors gui/eg_pma_run_panel.py's "Set Initial" anchor: the
prober's own die-grid zero moves every time the operator re-aligns (see
instruments/electroglas_2001x.py's module docstring), so this never trusts
it as fixed. Instead the operator points at a die whose (row, col) is
known from the wafer data (the same Wafer Builder map the normal
Electroglas side uses - see eg_nanoz_recipe_panel.py), the chuck is
physically sitting on it, and "Chuck Is Set" reads the REAL ?P and stores
the offset between that and the wafer grid's own coordinate for that die -
every later move is computed from that grid plus this one offset.

Touchdown reference point: each shot's (td_start_row, die_column) is the
TOP die of that 1x20 column, per the physical probe card's own convention
(confirmed by the person who built this feature - the touchdown's
reference is always the top slot, not the centre or bottom).

AXIS MAPPING IS NOT HARDWARE-VERIFIED. This treats the wafer plan's
column as the prober's X and row as the prober's Y (goto_die(x=col,
y=row) once offset). That is a reasonable reading of "column" but has
not been checked against a real Electroglas + Nautilus card the way
electroglas_2001x.py's own MD direction notes were - verify against ?P
on the actual bench before trusting a real run, the same caution that
module's own docstring applies everywhere else about this prober.
"""

import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

from wafer_map_view import WaferMapPanel


def _read_position(drv):
    """?P, surviving one link stall - same pattern as
    eg_pma_run_panel.EgPmaRunPanel._read_position."""
    try:
        return drv.get_die_position()
    except Exception:
        pass
    try:
        drv.recover()
        return drv.get_die_position()
    except Exception:
        return None


class EgNanozRunPanel(ttk.Frame):
    def __init__(self, parent, controller, recipe_panel, log_fn):
        super().__init__(parent)
        self.controller = controller
        self._recipe = recipe_panel
        self._log = log_fn

        self._origin_offset = None    # (dx, dy) real - plan, once anchored
        self._index = None
        self._running = False
        self._paused = False
        self._abort = False
        self._thread = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_ctrl_bar()
        self._build_body()

    def _drv(self):
        drv = self.controller.drivers.get("prober")
        return drv if (drv and drv.inst) else None

    # -- top control bar ----------------------------------------------------

    def _build_ctrl_bar(self):
        ctrl = tk.Frame(self, bg="#f1f5f9", relief="solid", bd=1)
        ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))

        run_border = tk.Frame(ctrl, background="#15803d")
        run_border.pack(side="left", padx=(6, 6), pady=5)
        ttk.Button(run_border, text="▶  Run All", command=self._start_run
                  ).pack(padx=2, pady=2)
        ttk.Button(ctrl, text="⏭  Run Selected Touchdown", command=self._run_selected
                  ).pack(side="left", padx=3, pady=5)
        ttk.Button(ctrl, text="⏸  Pause", command=self._pause).pack(
            side="left", padx=3, pady=5)
        ttk.Button(ctrl, text="⏹  Stop", command=self._stop).pack(
            side="left", padx=3, pady=5)

        self._status_var = tk.StringVar(value="IDLE")
        tk.Label(ctrl, textvariable=self._status_var, bg="#f1f5f9", fg="#6b7280",
                font=("Segoe UI", 11, "bold")).pack(side="right", padx=12)

    # -- body: 25:20:55 split, same technique as instrument_panel.py's
    # own _tab_execution2 (PanedWindow has no percentage-based initial
    # layout - sash positions are only real once the pane has a real
    # width, so this waits for the first <Configure> with a usable width
    # rather than fighting an after_idle measured too early).

    def _build_body(self):
        body = ttk.PanedWindow(self, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 6))

        pane1 = ttk.Frame(body)
        body.add(pane1, weight=25)
        pane1.columnconfigure(0, weight=1)
        pane1.rowconfigure(2, weight=1)
        self._build_pitch_row(pane1)
        self._build_anchor_row(pane1)
        self._build_shot_table(pane1)

        pane2 = ttk.Frame(body)
        body.add(pane2, weight=20)
        self._build_chuck_position(pane2)

        pane3 = ttk.LabelFrame(body, text="Wafer Map")
        body.add(pane3, weight=55)
        pane3.rowconfigure(1, weight=1)
        pane3.columnconfigure(0, weight=1)
        self._build_map(pane3)

        def _apply_initial_sashes():
            w = body.winfo_width()
            if w <= 1:
                return
            body.sashpos(0, int(w * 0.25))
            body.sashpos(1, int(w * 0.45))

        def _set_initial_sashes(_event=None):
            if body.winfo_width() <= 1:
                return
            body.unbind("<Configure>", sash_bind_id[0])
            body.after_idle(_apply_initial_sashes)

        sash_bind_id = [body.bind("<Configure>", _set_initial_sashes)]

    # -- pane 1a: pitch -------------------------------------------------

    def _build_pitch_row(self, parent):
        lf = ttk.LabelFrame(parent, text="Die Pitch", padding=6)
        lf.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        row1 = ttk.Frame(lf)
        row1.pack(fill="x")
        ttk.Label(row1, text="X (mm):").pack(side="left")
        self._pitch_x_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self._pitch_x_var, width=8).pack(side="left", padx=(2, 8))
        ttk.Label(row1, text="Y (mm):").pack(side="left")
        self._pitch_y_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self._pitch_y_var, width=8).pack(side="left", padx=(2, 0))
        row2 = ttk.Frame(lf)
        row2.pack(fill="x", pady=(4, 0))
        ttk.Button(row2, text="Set on Prober", command=self._set_pitch).pack(side="left")
        ttk.Button(row2, text="Verify", command=self._verify_pitch).pack(
            side="left", padx=(4, 0))
        self._pitch_status_var = tk.StringVar(value="not verified")
        ttk.Label(lf, textvariable=self._pitch_status_var, foreground="#b45309",
                 wraplength=220, justify="left").pack(anchor="w", pady=(4, 0))

    def _set_pitch(self):
        drv = self._drv()
        if not drv:
            messagebox.showwarning("Pitch", "Prober not connected.")
            return
        try:
            x_mm, y_mm = float(self._pitch_x_var.get()), float(self._pitch_y_var.get())
        except ValueError:
            messagebox.showerror("Pitch", "X/Y must be numbers (mm).")
            return
        try:
            drv.set_die_size_mm(x_mm, y_mm)
        except Exception as e:
            messagebox.showerror("Pitch", f"Could not set: {e}")
            return
        self._log(f"[NANOZ] Die pitch set on prober: {x_mm} x {y_mm} mm.")
        self._pitch_status_var.set("set - not yet re-verified")

    def _verify_pitch(self):
        drv = self._drv()
        if not drv:
            messagebox.showwarning("Pitch", "Prober not connected.")
            return
        try:
            x_mm, y_mm = float(self._pitch_x_var.get()), float(self._pitch_y_var.get())
        except ValueError:
            messagebox.showerror("Pitch", "Enter the expected X/Y (mm) first.")
            return

        def _work():
            try:
                size_x_um, size_y_um = drv.infer_die_size()
            except Exception as e:
                self.after(0, lambda: self._pitch_status_var.set(f"could not verify: {e}"))
                return
            got_x_mm, got_y_mm = size_x_um / 1000.0, size_y_um / 1000.0
            match = abs(got_x_mm - x_mm) < 0.001 and abs(got_y_mm - y_mm) < 0.001
            text = (f"prober reports {got_x_mm:.3f} x {got_y_mm:.3f} mm — "
                   f"{'MATCHES' if match else 'DOES NOT MATCH'} entered pitch")
            self.after(0, lambda: (
                self._pitch_status_var.set(text),
                self._log(f"[NANOZ] Pitch verify: {text}")))
        threading.Thread(target=_work, daemon=True).start()

    # -- pane 1b: anchor --------------------------------------------------

    def _build_anchor_row(self, parent):
        lf = ttk.LabelFrame(parent, text="Set Initial", padding=6)
        lf.grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Label(lf, text="Chuck is on die (serial):").pack(anchor="w")
        self._anchor_var = tk.StringVar()
        self._anchor_cb = ttk.Combobox(lf, textvariable=self._anchor_var, width=28)
        self._anchor_cb.pack(anchor="w", pady=(2, 4))
        ttk.Button(lf, text="Chuck Is Set", command=self._set_anchor).pack(anchor="w")
        self._anchor_state_var = tk.StringVar(value="not anchored")
        ttk.Label(lf, textvariable=self._anchor_state_var, foreground="#b45309",
                 wraplength=220, justify="left").pack(anchor="w", pady=(4, 0))

    def refresh_anchor_choices(self):
        plan = self._recipe.get_wafer_plan()
        serials = sorted(plan.serial_to_rc.keys()) if plan else []
        self._anchor_cb.config(values=serials)

    def _set_anchor(self):
        plan = self._recipe.get_wafer_plan()
        if plan is None:
            messagebox.showwarning("Anchor", "Load a wafer plan first.")
            return
        serial = self._anchor_var.get().strip().upper()
        rc = plan.serial_to_rc.get(serial)
        if rc is None:
            messagebox.showwarning("Anchor", f"'{serial}' is not on the wafer plan's Die Map.")
            return
        drv = self._drv()
        if not drv:
            messagebox.showwarning("Anchor", "Prober not connected - cannot read its "
                                             "real position to anchor against.")
            return

        def _work():
            real = _read_position(drv)
            self.after(0, lambda: self._finish_anchor(rc, real, serial))
        threading.Thread(target=_work, daemon=True).start()

    def _finish_anchor(self, rc, real, serial):
        if real is None:
            messagebox.showwarning("Anchor", "Could not read the prober's real "
                                             "position (?P) - try again.")
            return
        row, col = rc
        # Wafer plan grid: x = column, y = row - see module docstring for
        # why this axis pairing is a reasonable but UNVERIFIED reading.
        self._origin_offset = (real[0] - col, real[1] - row)
        self._anchored_touchdown_idx = self._nearest_touchdown_index(row, col)
        self._anchor_state_var.set(
            f"anchored at {serial} (row {row}, col {col}) — real X{real[0]}Y{real[1]} "
            f"— offset {self._origin_offset}")
        self._log(f"[NANOZ] Anchored: {serial} is real X{real[0]}Y{real[1]}, "
                 f"origin offset {self._origin_offset}.")

    def _nearest_touchdown_index(self, row, col):
        shots = self._recipe.get_shots()
        if not shots:
            return None
        # Not necessarily an exact touchdown top - just seeds self._index so
        # Next/Back have somewhere sane to start from; Run All always
        # targets an absolute wafer-grid coordinate, never a delta from
        # this guess, so a loose starting guess costs nothing.
        best = min(range(len(shots)),
                  key=lambda i: abs(shots[i]["td_start_row"] - row) + abs(shots[i]["die_column"] - col))
        return best

    # -- pane 1c: shot list ---------------------------------------------

    def _build_shot_table(self, parent):
        lf = ttk.LabelFrame(parent, text="Shots (Recipe tab)", padding=4)
        lf.grid(row=2, column=0, sticky="nsew", pady=(2, 0))
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)
        cols = ("idx", "label", "top_die", "row", "col", "status")
        self._tree = ttk.Treeview(lf, columns=cols, show="headings", height=10)
        for col, head, width in (("idx", "#", 30), ("label", "Label", 90),
                                 ("top_die", "Top die", 80),
                                 ("row", "row", 45), ("col", "col", 45),
                                 ("status", "Status", 140)):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=width, anchor="w")
        self._tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, orient="vertical", command=self._tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=sb.set)

    def refresh_table(self):
        self._tree.delete(*self._tree.get_children())
        plan = self._recipe.get_wafer_plan()
        shots = self._recipe.get_shots()
        if plan is None or not shots:
            return
        for i, shot in enumerate(shots):
            row, col = shot["td_start_row"], shot["die_column"]
            d = plan.dies.get((row, col))
            self._tree.insert("", "end", iid=str(i), values=(
                i, shot.get("label") or f"Shot {i+1}", d["serial"] if d else "?",
                row, col, "pending"))

    def _set_row_status(self, idx, text):
        try:
            self._tree.set(str(idx), "status", text)
        except tk.TclError:
            pass

    # -- pane 2: Chuck Position -------------------------------------------

    def _build_chuck_position(self, parent):
        lf = ttk.LabelFrame(parent, text="Chuck Position", padding=6)
        lf.pack(fill="both", expand=True)
        lf.columnconfigure(0, weight=1)
        lf.columnconfigure(1, weight=1)

        self._pos_var = tk.StringVar(value="X: —\nY: —")
        ttk.Label(lf, textvariable=self._pos_var, font=("Consolas", 13, "bold"),
                 foreground="#0077cc", justify="center").grid(
                 row=0, column=0, columnspan=2, pady=(0, 4))

        ttk.Separator(lf, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=3)

        ttk.Button(lf, text="↻ Sync ?P", command=self._sync_position).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=1)
        ttk.Button(lf, text="⏮ Back", command=self._step_back).grid(
            row=3, column=0, sticky="ew", padx=(0, 1), pady=1)
        ttk.Button(lf, text="⏭ Next", command=self._step_next).grid(
            row=3, column=1, sticky="ew", padx=(1, 0), pady=1)

    def _sync_position(self):
        drv = self._drv()
        if not drv:
            messagebox.showwarning("Sync", "Prober not connected.")
            return

        def _work():
            pos = _read_position(drv)
            text = f"X: {pos[0]}\nY: {pos[1]}" if pos else "X: —\nY: —"
            self.after(0, lambda: self._pos_var.set(text))
        threading.Thread(target=_work, daemon=True).start()

    def _step_back(self):
        if self._index is None or self._index <= 0:
            return
        self._run_indices([self._index - 1])

    def _step_next(self):
        shots = self._recipe.get_shots()
        if not shots:
            return
        nxt = 0 if self._index is None else self._index + 1
        if nxt >= len(shots):
            return
        self._run_indices([nxt])

    # -- pane 3: Wafer Map ----------------------------------------------

    def _build_map(self, parent):
        # Own WaferMapPanel instance, populated by copying rows out of the
        # wafer plan (load_die_list) - never touches gui/recipe_gen_panel.
        # py's live Wafer Builder object, so picking here cannot affect
        # that map, the same guarantee the normal Electroglas Run/Recipe
        # tabs already give (see eg_nanoz_recipe_panel.py's own module
        # docstring).
        bar = ttk.Frame(parent)
        bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        self._picked_var = tk.StringVar(value="Picked: 0")
        ttk.Label(bar, textvariable=self._picked_var, foreground="#6b7280",
                 font=("Segoe UI", 8)).pack(side="left")
        ttk.Label(bar, text="Click the TOP die of each 1x20 touchdown you want, "
                           "then use Recipe tab > Take From Map Selection.",
                 foreground="#6b7280", font=("Segoe UI", 8)).pack(side="left", padx=(10, 0))

        self.wafer_map = WaferMapPanel(parent, show_title=False)
        self.wafer_map.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.wafer_map.enable_picking(on_change=self._on_pick_change)

    def _on_pick_change(self):
        self._picked_var.set(f"Picked: {len(self.wafer_map.get_picked())}")

    def refresh_wafer_map(self):
        """Repopulate the pick map from the Recipe tab's current wafer
        plan - a plain copy (load_die_list), never a shared reference."""
        plan = self._recipe.get_wafer_plan()
        if plan is None:
            self.wafer_map.load_die_list([], label="dies")
            return
        dies = [{"row": row, "col": col, "x_um": float(col), "y_um": -float(row),
                "die_id": d["serial"]}
               for (row, col), d in plan.dies.items()]
        self.wafer_map.load_die_list(dies, label="dies")

    # -- run loop -----------------------------------------------------------

    def _run_selected(self):
        sel = self._tree.selection()
        if not sel:
            return
        self._run_indices([int(sel[0])])

    def _start_run(self):
        shots = self._recipe.get_shots()
        if not shots:
            messagebox.showwarning("Run", "Take shots from the map selection on the "
                                          "Recipe tab first.")
            return
        if self._origin_offset is None:
            messagebox.showwarning("Run", "Set the anchor (Chuck Is Set) first.")
            return
        self._run_indices(list(range(len(shots))))

    def _run_indices(self, indices):
        if self._running:
            self._log("[NANOZ] A run is already active.")
            return
        drv = self._drv()
        if not drv:
            messagebox.showwarning("Run", "Prober not connected.")
            return
        if self._origin_offset is None:
            messagebox.showwarning("Run", "Set the anchor (Chuck Is Set) first.")
            return
        self._running, self._abort, self._paused = True, False, False
        self._status_var.set("RUNNING")
        self._thread = threading.Thread(target=self._run_thread, args=(drv, indices), daemon=True)
        self._thread.start()

    def _run_thread(self, drv, indices):
        shots = self._recipe.get_shots()
        for idx in indices:
            while self._paused and not self._abort:
                time.sleep(0.2)
            if self._abort:
                break
            shot = shots[idx]
            row, col = shot["td_start_row"], shot["die_column"]
            ox, oy = self._origin_offset
            target_x, target_y = col + ox, row + oy
            self.after(0, lambda i=idx: self._set_row_status(i, "moving..."))
            try:
                drv.goto_die(target_x, target_y)
            except Exception as e:
                msg = f"MOVE FAILED: {type(e).__name__}: {e}"
                self.after(0, lambda i=idx, m=msg: (self._set_row_status(i, m), self._log(f"[NANOZ] {m}")))
                break
            self.after(0, lambda i=idx: self._set_row_status(i, "measuring..."))
            try:
                ok, verdicts, logs = self._recipe.run_cycle_and_collect(idx)
            except Exception as e:
                msg = f"MEASURE FAILED: {type(e).__name__}: {e}"
                self.after(0, lambda i=idx, m=msg: (self._set_row_status(i, m), self._log(f"[NANOZ] {m}")))
                break
            for line in logs:
                self.after(0, lambda l=line: self._log(l))
            n_pass = sum(1 for v in verdicts.values() if v)
            n_fail = len(verdicts) - n_pass
            status = "no dies here" if not verdicts else (
                f"PASS ({n_pass}/{len(verdicts)})" if ok else f"FAIL ({n_fail}/{len(verdicts)})")
            self.after(0, lambda i=idx, s=status: self._set_row_status(i, s))
            self._index = idx
        self._running = False
        self.after(0, lambda: self._status_var.set("IDLE"))

    def _pause(self):
        self._paused = not self._paused
        self._status_var.set("PAUSED" if self._paused else "RUNNING")

    def _stop(self):
        self._abort = True
        self._paused = False
