from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk


class CassettePanel(ttk.Frame):
    """Drives a real cassette load end-to-end: one physical wafer per
    cassette slot, each tagged with its own Lot ID/Wafer ID. The operator
    loads the cassette, presses NEW CST on the prober, loads/starts the
    FIRST wafer normally (ATA folder + ▶ Full Die, or ▶ Test Selected),
    then presses ▶ Arm here - from then on this panel watches for that run
    to finish, auto-exports it (reusing the ATA Folder tab's own Export
    Directory/Format), checks yield against the threshold (pausing if
    it's too low instead of silently continuing to burn wafers on a bad
    recipe/setup), and if it's fine sends U (unload/load next wafer) and
    auto-starts the next slot's run in that SAME mode the first wafer
    used (see _run_mode) - repeating until the list is exhausted or the
    cassette reports no next wafer."""

    def __init__(self, parent, controller, ui):
        super().__init__(parent)
        self.controller = controller
        self.ui = ui
        self._wafers: list[str] = []  # [wafer_id, ...] in slot order; lot_id is shared
        self._slot_idx = 0
        self._armed = False
        # "full" or "test" - which run mode to repeat on every later slot,
        # set from the first wafer's actual run (see _on_wafer_finished).
        # Defaults to "full" so arming before that first run has even
        # finished once still falls back to the old Full Die behavior.
        self._run_mode = "full"

        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_wafer_list()
        self._build_export()
        self._build_manual()
        self._build_progress()

    # ------------------------------------------------------------------ UI

    def _build_topbar(self):
        bar = ttk.Frame(self, padding=(6, 4))
        bar.grid(row=0, column=0, sticky="ew")

        self._go_btn = ttk.Button(bar, text="▶  Cassette Automation",
                                  command=self._arm)
        self._go_btn.pack(side="left", padx=4)
        self._stop_btn = ttk.Button(bar, text="⏹  Stop Automation", state="disabled",
                                    command=lambda: self._disarm("Stopped by user."))
        self._stop_btn.pack(side="left", padx=4)
        ttk.Button(bar, text="🔄 Reset to Slot #1",
                  command=self._reset_slot).pack(side="left", padx=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Label(bar, text="Pass yield ≥").pack(side="left")
        self._yield_var = tk.StringVar(value="95")
        ttk.Entry(bar, textvariable=self._yield_var, width=5).pack(side="left", padx=(2, 0))
        ttk.Label(bar, text="% to auto-continue, else pause").pack(side="left", padx=(2, 0))

        self._state_var = tk.StringVar(value="IDLE")
        self._state_lbl = ttk.Label(bar, textvariable=self._state_var,
                                    font=("Consolas", 11, "bold"), foreground="#6b7280")
        self._state_lbl.pack(side="right", padx=8)

    def _build_wafer_list(self):
        lf = ttk.LabelFrame(
            self, text="Cassette Slots — one Wafer ID per physical wafer, in slot order "
                       "(slot #1 is whatever the operator already manually loaded/started). "
                       "Lot ID below applies to every wafer in the cassette.",
            padding=6)
        lf.grid(row=1, column=0, sticky="ew", padx=6, pady=(4, 2))
        lf.columnconfigure(0, weight=1)

        btns = ttk.Frame(lf)
        btns.grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Button(btns, text="＋ Add Slot", command=self._add_slot).pack(side="left", padx=2)
        ttk.Button(btns, text="✎ Edit", command=self._edit_slot).pack(side="left", padx=2)
        ttk.Button(btns, text="🗑 Remove", command=self._remove_slot).pack(side="left", padx=2)
        ttk.Button(btns, text="▲", width=3, command=lambda: self._move_slot(-1)).pack(
            side="left", padx=(10, 2))
        ttk.Button(btns, text="▼", width=3, command=lambda: self._move_slot(1)).pack(
            side="left", padx=2)
        ttk.Button(btns, text="🗑 Clear All", command=self._clear_slots).pack(side="left", padx=(10, 2))

        ttk.Separator(btns, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Label(btns, text="Lot ID (all wafers):").pack(side="left")
        self._lot_id_var = tk.StringVar()
        ttk.Entry(btns, textvariable=self._lot_id_var, width=20).pack(
            side="left", padx=(4, 0))

        cols = ("slot", "lot", "wafer")
        self._slot_tree = ttk.Treeview(lf, columns=cols, show="headings", height=5,
                                       selectmode="browse")
        heads = [("slot", "Slot #", 60), ("lot", "Lot ID", 160), ("wafer", "Wafer ID", 160)]
        for cid, text, width in heads:
            self._slot_tree.heading(cid, text=text)
            self._slot_tree.column(cid, width=width, anchor="center" if cid == "slot" else "w")
        self._slot_tree.grid(row=1, column=0, sticky="ew")
        self._slot_tree.bind("<Double-1>", lambda _e: self._edit_slot())

    def _build_export(self):
        ef = ttk.LabelFrame(self, text="Auto-Export (after every wafer, using the ATA Folder "
                                       "tab's own Export Directory/Format)", padding=6)
        ef.grid(row=2, column=0, sticky="ew", padx=6, pady=(2, 2))

        self._auto_export_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ef, text="Auto-export after each wafer",
                       variable=self._auto_export_var).pack(side="left", padx=(0, 16))

        ttk.Label(ef, text="Export Directory:").pack(side="left")
        ttk.Entry(ef, textvariable=self.ui.export_path_var, width=32).pack(
            side="left", padx=6)
        ttk.Button(ef, text="Browse...", command=self._browse_export_dir).pack(side="left")

        ttk.Label(ef, text="Format:").pack(side="left", padx=(16, 2))
        self._export_format_cb = ttk.Combobox(
            ef, textvariable=self.ui.export_format_var, state="readonly", width=32)
        self._export_format_cb.pack(side="left", padx=(0, 4))
        self._export_format_cb.bind("<<ComboboxSelected>>", lambda _e: None)
        ttk.Button(ef, text="↻", width=3, command=self._refresh_export_formats).pack(side="left")

    def _build_manual(self):
        mf = ttk.LabelFrame(
            self, text="Manual Command Test (exercise each cassette-workflow "
                       "command on its own, without running full automation)",
            padding=6)
        mf.grid(row=3, column=0, sticky="ew", padx=6, pady=(2, 2))

        ttk.Button(mf, text="Read STB",
                   command=self._manual_read_stb).pack(side="left", padx=2)
        ttk.Button(mf, text="Get Wafer Status (w)",
                   command=self._manual_wafer_status).pack(side="left", padx=2)
        ttk.Button(mf, text="Get Cassette Status (x)",
                   command=self._manual_cassette_status).pack(side="left", padx=2)
        ttk.Button(mf, text="Wait for Wafer Ready (STB=65)",
                   command=self._manual_wait_ready).pack(side="left", padx=2)
        ttk.Button(mf, text="Send J (Next Die)",
                   command=self._manual_next_die).pack(side="left", padx=2)
        ttk.Button(mf, text="Send U (Unload Only)",
                   command=self._manual_unload_only).pack(side="left", padx=2)
        ttk.Button(mf, text="Send L (Unload / Load Next Wafer)",
                   command=self._manual_unload_next).pack(side="left", padx=2)

    def _build_progress(self):
        pf = ttk.LabelFrame(self, text="Cassette Automation Log", padding=6)
        pf.grid(row=4, column=0, sticky="nsew", padx=6, pady=(2, 6))
        pf.rowconfigure(0, weight=1)
        pf.columnconfigure(0, weight=1)

        cols = ("timestamp", "slot", "lot", "event")
        self._tree = ttk.Treeview(pf, columns=cols, show="headings",
                                  height=10, selectmode="browse")
        heads = [("timestamp", "Time", 150), ("slot", "Slot", 50),
                 ("lot", "Lot ID", 120), ("event", "Event", 400)]
        for cid, text, width in heads:
            self._tree.heading(cid, text=text)
            self._tree.column(cid, width=width,
                              anchor="center" if cid == "slot" else "w")
        self._tree.grid(row=0, column=0, sticky="nsew")
        tsb = ttk.Scrollbar(pf, orient="vertical", command=self._tree.yview)
        tsb.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=tsb.set)

    # ------------------------------------------------------------- helpers

    def _log(self, msg: str):
        self.controller.log(msg)

    def _set_state(self, text: str, color: str = "#6b7280"):
        self._state_var.set(text)
        self._state_lbl.config(foreground=color)

    def _set_locked(self, locked: bool):
        self._go_btn.config(state="disabled" if locked else "normal")
        self._stop_btn.config(state="normal" if locked else "disabled")

    def _drv(self):
        drv = self.controller.drivers.get("prober")
        return drv if (drv and drv.inst) else None

    def _browse_export_dir(self):
        selected = filedialog.askdirectory(
            initialdir=self.ui.export_path_var.get(), title="Select Export Directory")
        if selected:
            self.ui.export_path_var.set(selected)

    def _refresh_export_formats(self):
        names = [f["name"] for f in getattr(self.ui, "_export_formats", [])]
        self._export_format_cb.config(values=names)
        if names and self.ui.export_format_var.get() not in names:
            self.ui.export_format_var.set(names[0])

    def _record(self, slot_num, lot_id: str, event: str):
        row = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
              "slot": slot_num, "lot": lot_id, "event": event}
        def _ui():
            self._tree.insert("", "end", values=(row["timestamp"], row["slot"],
                                                  row["lot"], row["event"]))
            children = self._tree.get_children()
            if children:
                self._tree.see(children[-1])
        self.after(0, _ui)

    def _log_event(self, slot_num, lot_id: str, event: str):
        self._log(f"[CASSETTE] Slot {slot_num}: {event}" if slot_num else f"[CASSETTE] {event}")
        self._record(slot_num, lot_id, event)

    def _yield_threshold(self) -> float:
        try:
            return float(self._yield_var.get())
        except ValueError:
            return 95.0

    # ------------------------------------------------------------ slot list

    def _lot_id(self) -> str:
        return self._lot_id_var.get().strip()

    def _redraw_slots(self):
        self._slot_tree.delete(*self._slot_tree.get_children())
        lot_id = self._lot_id()
        for i, wafer_id in enumerate(self._wafers):
            marker = " (current)" if self._armed and i == self._slot_idx else ""
            self._slot_tree.insert("", "end", iid=str(i), values=(
                f"{i + 1}{marker}", lot_id, wafer_id))

    def _add_slot(self):
        wafer_id = simpledialog.askstring("Add Slot", "Wafer ID:", parent=self)
        if wafer_id is None:
            return
        wafer_id = wafer_id.strip()
        if not wafer_id:
            messagebox.showerror("Wafer ID Required", "Wafer ID can't be blank.")
            return
        self._wafers.append(wafer_id)
        self._redraw_slots()

    def _selected_slot_index(self):
        sel = self._slot_tree.selection()
        return int(sel[0]) if sel else None

    def _edit_slot(self):
        idx = self._selected_slot_index()
        if idx is None:
            return
        wafer_id = simpledialog.askstring(
            "Edit Slot", "Wafer ID:", initialvalue=self._wafers[idx], parent=self)
        if wafer_id is None:
            return
        wafer_id = wafer_id.strip()
        if not wafer_id:
            messagebox.showerror("Wafer ID Required", "Wafer ID can't be blank.")
            return
        self._wafers[idx] = wafer_id
        self._redraw_slots()

    def _remove_slot(self):
        idx = self._selected_slot_index()
        if idx is None:
            return
        del self._wafers[idx]
        if self._slot_idx > idx:
            self._slot_idx -= 1
        self._redraw_slots()

    def _move_slot(self, direction: int):
        idx = self._selected_slot_index()
        if idx is None:
            return
        new_idx = idx + direction
        if not (0 <= new_idx < len(self._wafers)):
            return
        self._wafers[idx], self._wafers[new_idx] = self._wafers[new_idx], self._wafers[idx]
        self._redraw_slots()
        self._slot_tree.selection_set(str(new_idx))

    def _clear_slots(self):
        if self._armed:
            messagebox.showerror("Automation Armed", "Stop automation before clearing the list.")
            return
        if self._wafers and not messagebox.askyesno(
            "Clear All", f"Remove all {len(self._wafers)} slot(s)?"):
            return
        self._wafers = []
        self._slot_idx = 0
        self._redraw_slots()

    def _reset_slot(self):
        if self._armed:
            messagebox.showerror("Automation Armed", "Stop automation before resetting.")
            return
        self._slot_idx = 0
        self._redraw_slots()
        self._log_event(1, "", "Reset — next Arm will start tracking from slot #1.")

    # --------------------------------------------------- manual command test

    def _manual_wait_ready(self):
        drv = self._drv()
        if not drv:
            self._log("[CASSETTE] Wait for Wafer Ready: prober not connected.")
            return
        def _run():
            self._log("[CASSETTE] Polling for STB=65 (wafer ready)...")
            stb = drv.cassette_wait_for_wafer_ready(timeout_s=30)
            if stb == 65:
                self._log("[CASSETTE] << STB=65 — wafer ready, Die #1 in contact.")
            else:
                self._log("[CASSETTE] Timed out waiting for STB=65.")
        threading.Thread(target=_run, daemon=True).start()

    def _manual_next_die(self):
        drv = self._drv()
        if not drv:
            self._log("[CASSETTE] Send J: prober not connected.")
            return
        def _run():
            self._log("[CASSETTE] >> J  (Next Die)")
            stb = drv.cassette_next_die(timeout_s=60)
            if stb == 66:
                self._log("[CASSETTE] << STB=66  (next die arrived)")
            elif stb == 67:
                self._log("[CASSETTE] << STB=67  (end of wafer map)")
            else:
                self._log("[CASSETTE] Timed out waiting for STB=66/67.")
        threading.Thread(target=_run, daemon=True).start()

    def _manual_wafer_status(self):
        drv = self._drv()
        if not drv:
            self._log("[CASSETTE] Get Wafer Status: prober not connected.")
            return
        def _run():
            raw = drv.get_wafer_status()
            self._log(f"[CASSETTE] << w (wafer status): {raw!r}")
            self._log("[CASSETTE]    Per the manual (4.81 w): cassette ID "
                      "(0=no cassette/1=ready/2=testing/3=finished/"
                      "4=rejected) then 25 per-slot wafer codes (0=no wafer/"
                      "1=not done/2=finished/3=under way), for cassette 1 "
                      "then cassette 2 - raw string shown as-is, exact field "
                      "widths not parsed here.")
        threading.Thread(target=_run, daemon=True).start()

    def _manual_cassette_status(self):
        drv = self._drv()
        if not drv:
            self._log("[CASSETTE] Get Cassette Status: prober not connected.")
            return
        def _run():
            raw = drv.get_cassette_status()
            self._log(f"[CASSETTE] << x (cassette status): {raw!r}")
            self._log("[CASSETTE]    Per the manual (4.82 x): cassette IDs, "
                      "then the count of not-yet-tested wafers remaining in "
                      "the current cassette, then the slot number of the "
                      "wafer currently on the chuck - raw string shown as-is, "
                      "exact field widths not parsed here.")
        threading.Thread(target=_run, daemon=True).start()

    def _manual_unload_only(self):
        drv = self._drv()
        if not drv:
            self._log("[CASSETTE] Send U: prober not connected.")
            return
        def _run():
            self._log("[CASSETTE] >> U  (Unload only)")
            stb = drv.unload_wafer()
            if stb == 71:
                self._log("[CASSETTE] << STB=71  (wafer unloaded - prober now "
                          "waits for the next load command, it will NOT "
                          "auto-advance to the next wafer on its own)")
            else:
                self._log(f"[CASSETTE] << STB={stb}  (unexpected - see Read STB)")
        threading.Thread(target=_run, daemon=True).start()

    def _manual_unload_next(self):
        drv = self._drv()
        if not drv:
            self._log("[CASSETTE] Send L: prober not connected.")
            return
        def _run():
            self._log("[CASSETTE] >> L  (Unload / Load Next Wafer)")
            stb = drv.cassette_unload_and_load_next(timeout_s=120)
            if stb == 70:
                self._log("[CASSETTE] << STB=70  (next wafer loaded, start die positioned, chuck DOWN)")
            else:
                self._log("[CASSETTE] No next wafer — cassette empty / idle / timed out.")
        threading.Thread(target=_run, daemon=True).start()

    def _manual_read_stb(self):
        drv = self._drv()
        if not drv:
            self._log("[CASSETTE] Read STB: prober not connected.")
            return
        def _run():
            stb, desc = drv.read_stb_decoded()
            self._log(f"[CASSETTE] STB={stb}  {desc}")
        threading.Thread(target=_run, daemon=True).start()

    # ------------------------------------------------------------- automation

    def _arm(self):
        if not self._wafers:
            messagebox.showerror("No Slots", "Add at least one cassette slot "
                                 "(Wafer ID) first.")
            return
        if not self._lot_id():
            messagebox.showerror("Lot ID Required", "Enter the Lot ID for this "
                                 "cassette first.")
            return
        if self._slot_idx >= len(self._wafers):
            messagebox.showerror("Nothing Left", "Every slot in the list is already "
                                 "done — 🔄 Reset to Slot #1 to run it again.")
            return
        if self._auto_export_var.get() and not self.ui.get_selected_export_format():
            messagebox.showerror("No Export Format", "Pick an export format above, or "
                                 "turn off auto-export.")
            return
        if getattr(self.ui, "_exec2_on_run_finished", None) not in (None, self._on_wafer_finished):
            messagebox.showerror("Already Hooked", "Another automation is already watching "
                                 "for the run to finish.")
            return

        self._armed = True
        self.ui._exec2_on_run_finished = self._on_wafer_finished
        self._set_locked(True)
        self._set_state("ARMED — waiting for the current/next run to finish", "#2563eb")
        self._redraw_slots()
        self._log_event(
            self._slot_idx + 1, self._lot_id(),
            "Armed — if this wafer's run isn't already going, start it normally "
            "(▶ Full Die or ▶ Test Selected on the Run tab) and this panel will "
            "take over from there, repeating whichever one you used for every "
            "later slot.")

    def _disarm(self, reason: str = ""):
        self._armed = False
        if getattr(self.ui, "_exec2_on_run_finished", None) is self._on_wafer_finished:
            self.ui._exec2_on_run_finished = None
        self._set_locked(False)
        self._redraw_slots()
        if reason:
            self._log_event(self._slot_idx + 1, "", reason)

    def _on_wafer_finished(self, pass_n: int, fail_n: int, total_n: int, aborted: bool,
                           run_mode: str = "full"):
        if not self._armed:
            return
        # Whatever mode the FIRST wafer's run was actually started in
        # (Full Die from the Run tab, or Test Selected) - every later slot
        # repeats that exact same mode, not always Full Die. run_mode is
        # None on an aborted run (nothing finished to read a mode from);
        # keep whatever was last recorded rather than overwrite it with
        # nothing.
        if run_mode:
            self._run_mode = run_mode
        lot_id, wafer_id = self._lot_id(), self._wafers[self._slot_idx]

        if aborted:
            self._log_event(self._slot_idx + 1, lot_id,
                            "Run was aborted — cassette automation stopped.")
            self._disarm()
            self._set_state("STOPPED (run aborted)", "#dc2626")
            return

        tested = pass_n + fail_n
        pct = (pass_n / tested * 100) if tested else 0.0
        self._log_event(self._slot_idx + 1, lot_id,
                        f"Run finished — {pass_n}/{tested} pass ({pct:.1f}%), "
                        f"{total_n} die(s) on the wafer map.")

        if self._auto_export_var.get():
            self._export_current(lot_id, wafer_id)

        threshold = self._yield_threshold()
        if tested and pct < threshold:
            self._log_event(self._slot_idx + 1, lot_id,
                            f"Yield {pct:.1f}% is below the {threshold:g}% threshold — "
                            f"PAUSING cassette automation (wafer left loaded).")
            self._disarm()
            self._set_state(f"PAUSED — yield {pct:.1f}% < {threshold:g}%", "#f97316")
            return

        self._slot_idx += 1
        if self._slot_idx >= len(self._wafers):
            self._log_event(self._slot_idx, lot_id,
                            "All slots in the list are complete — cassette automation finished.")
            self._disarm()
            self._set_state("CASSETTE COMPLETE", "#16a34a")
            return

        self._set_state("SWAPPING CASSETTE", "#f97316")
        self._redraw_slots()
        threading.Thread(target=self._advance_thread, daemon=True).start()

    def _export_current(self, lot_id: str, wafer_id: str):
        self.ui.lot_id.set(lot_id)
        self.ui.wafer_id_var.set(wafer_id)
        try:
            self.controller.cmd_export_sql()
        except Exception as e:
            self._log_event(self._slot_idx + 1, lot_id, f"Auto-export error: {e}")

    def _advance_thread(self):
        drv = self._drv()
        try:
            if drv is None:
                self._log("[CASSETTE] (simulated — no prober connected) "
                          ">> L  (Unload / Load Next Wafer)")
                time.sleep(0.2)
                next_ready = True
            else:
                self._log("[CASSETTE] >> L  (Unload / Load Next Wafer)")
                next_ready = drv.cassette_unload_and_load_next(timeout_s=180) == 70
        except Exception as e:
            self._log(f"[CASSETTE] Unload/load-next error: {e}")
            next_ready = False

        if not next_ready:
            self.after(0, lambda: self._log_event(
                self._slot_idx + 1, "", "No next wafer (cassette empty/idle/error) — "
                "cassette automation stopped."))
            self.after(0, self._disarm)
            self.after(0, lambda: self._set_state(
                "STOPPED (no next wafer)", "#dc2626"))
            return

        wafer_id = self._wafers[self._slot_idx]
        lot_id = self._lot_id()
        self.after(0, lambda: self.ui.lot_id.set(lot_id))
        self.after(0, lambda: self.ui.wafer_id_var.set(wafer_id))
        self.after(0, lambda: self._log_event(
            self._slot_idx + 1, lot_id,
            "Next wafer ready (STB=70) — auto-starting its run."))
        self.after(0, self._start_next_run)

    def _start_next_run(self):
        if not self._armed:
            return
        # Repeat whatever mode the first wafer was actually started in -
        # Test Selected reuses the wafer map's current picks (untouched
        # across slots, since the same ATA folder/recipe stays loaded for
        # the whole cassette), so each wafer gets the same subset of dies.
        starter = (self.ui._exec2_start_test_die if self._run_mode == "test"
                  else self.ui._exec2_start_full_die)
        try:
            starter()
        except Exception as e:
            self._log_event(self._slot_idx + 1, "", f"Could not auto-start the next run: {e}")
            self._disarm()
            self._set_state("STOPPED (auto-start failed)", "#dc2626")
