"""Cassette Panel — cassette-level wafer load/unload workflow testing.

This is a TESTING tool for the cassette-automation command sequence, kept
deliberately separate from the Run tab's Full Die / Test Die die-walk
engine (which uses the G/Z/D/J commands and their own, DIFFERENT STB
meanings — see instruments/accretech_uf200r.py's cassette-workflow
section for why the two are never mixed). It exercises exactly the
commands and lets the operator validate them against real hardware
before this workflow is wired into production test flow. Real per-die
measurement (SMU/DMM) is NOT implemented here yet — each die just logs a
placeholder "measured" row (timestamp/lot/wafer/die) to the results table
and, optionally, a CSV — swap in real instrument calls where noted once
this is ready to become the production path.

The end-to-end workflow (operator + prober + this GUI):

  1. Operator setup (outside this GUI): loads the cassette and presses
     NEW CST on the prober's touchscreen per EOI §8.4.1-8.4.10. The
     prober pulls Wafer #1, aligns it, and drives the chuck up so the
     needles touch Die #1.
  2. Handover: the instant the needles touch Die #1, the prober
     broadcasts STB=65. Enter Lot ID + starting Wafer #, click "Go" —
     this GUI polls for STB=65, and once seen, locks its controls and
     starts the wafer loop.
  3. Wafer loop (repeats for every die): run the (placeholder)
     measurement, send J (Next Die), poll ignoring STB=100 (Moving)
     until STB=66 (Next Die Arrived) — log and repeat.
  4. Cassette swap: J eventually returns STB=67 (End of Wafer Map,
     chuck didn't move) instead of 66. This GUI sends U (Unload and
     Load Next Wafer); the prober racks the finished wafer, pulls the
     next one, aligns it, and touches Die #1 — another STB=65 — and the
     GUI drops back into the wafer loop for the new wafer.
  5. Lot end: after the last wafer's U, the prober empties the cassette
     and goes idle (STB=0, "DONE !!" on the touchscreen) instead of
     sending 65. This GUI detects that (or simply times out waiting for
     65), closes out the CSV, and reports "Lot Complete." The operator
     then removes the finished cassette per EOI §8.4.14-8.4.19.
"""
from __future__ import annotations

import csv
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class CassettePanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._running = False
        self._abort = False
        self._results: list = []   # placeholder per-die log rows (dicts)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_manual()
        self._build_progress()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_topbar(self):
        bar = ttk.Frame(self, padding=(6, 4))
        bar.grid(row=0, column=0, sticky="ew")

        ttk.Label(bar, text="Lot ID:").pack(side="left")
        self._lot_var = tk.StringVar()
        self._lot_entry = ttk.Entry(bar, textvariable=self._lot_var, width=14)
        self._lot_entry.pack(side="left", padx=(2, 10))

        ttk.Label(bar, text="Starting Wafer #:").pack(side="left")
        self._wafer_var = tk.StringVar(value="1")
        self._wafer_entry = ttk.Entry(bar, textvariable=self._wafer_var, width=5)
        self._wafer_entry.pack(side="left", padx=(2, 10))

        self._go_btn = ttk.Button(bar, text="▶  Go (Start Lot)", command=self._start_lot)
        self._go_btn.pack(side="left", padx=4)
        self._stop_btn = ttk.Button(bar, text="⏹  Stop", state="disabled",
                                    command=self._request_stop)
        self._stop_btn.pack(side="left", padx=4)

        self._state_var = tk.StringVar(value="IDLE")
        self._state_lbl = ttk.Label(bar, textvariable=self._state_var,
                                    font=("Consolas", 11, "bold"), foreground="#6b7280")
        self._state_lbl.pack(side="right", padx=8)

    def _build_manual(self):
        mf = ttk.LabelFrame(
            self, text="Manual Command Test (exercise each cassette-workflow "
                       "command on its own, without running a full lot)",
            padding=6)
        mf.grid(row=1, column=0, sticky="ew", padx=6, pady=(4, 2))

        ttk.Button(mf, text="Wait for Wafer Ready (STB=65)",
                   command=self._manual_wait_ready).pack(side="left", padx=2)
        ttk.Button(mf, text="Send J (Next Die)",
                   command=self._manual_next_die).pack(side="left", padx=2)
        ttk.Button(mf, text="Send U (Unload / Load Next Wafer)",
                   command=self._manual_unload_next).pack(side="left", padx=2)
        ttk.Button(mf, text="Read STB",
                   command=self._manual_read_stb).pack(side="left", padx=2)

    def _build_progress(self):
        pf = ttk.LabelFrame(self, text="Lot Progress", padding=6)
        pf.grid(row=2, column=0, sticky="nsew", padx=6, pady=(2, 6))
        pf.rowconfigure(2, weight=1)
        pf.columnconfigure(0, weight=1)

        counters = ttk.Frame(pf)
        counters.grid(row=0, column=0, sticky="ew")
        self._wafer_count_var = tk.StringVar(value="Wafer: —")
        self._die_count_var = tk.StringVar(value="Die: —")
        ttk.Label(counters, textvariable=self._wafer_count_var,
                  font=("Consolas", 10, "bold")).pack(side="left", padx=(0, 16))
        ttk.Label(counters, textvariable=self._die_count_var,
                  font=("Consolas", 10, "bold")).pack(side="left")

        csv_row = ttk.Frame(pf)
        csv_row.grid(row=1, column=0, sticky="ew", pady=(6, 4))
        ttk.Label(csv_row, text="Export CSV:").pack(side="left")
        self._csv_var = tk.StringVar()
        ttk.Entry(csv_row, textvariable=self._csv_var, width=40).pack(
            side="left", padx=6)
        ttk.Button(csv_row, text="Browse...", command=self._browse_csv).pack(side="left")
        ttk.Label(csv_row, text="(blank = don't save)", foreground="gray",
                  font=("Arial", 8)).pack(side="left", padx=6)

        cols = ("timestamp", "wafer", "die", "event")
        self._tree = ttk.Treeview(pf, columns=cols, show="headings",
                                  height=10, selectmode="browse")
        heads = [("timestamp", "Time", 150), ("wafer", "Wafer", 60),
                 ("die", "Die", 60), ("event", "Event", 260)]
        for cid, text, width in heads:
            self._tree.heading(cid, text=text)
            self._tree.column(cid, width=width,
                              anchor="center" if cid in ("wafer", "die") else "w")
        self._tree.grid(row=2, column=0, sticky="nsew")
        tsb = ttk.Scrollbar(pf, orient="vertical", command=self._tree.yview)
        tsb.grid(row=2, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=tsb.set)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _log(self, msg: str):
        self.controller.log(msg)

    def _set_state(self, text: str, color: str = "#6b7280"):
        self._state_var.set(text)
        self._state_lbl.config(foreground=color)

    def _set_locked(self, locked: bool):
        state = "disabled" if locked else "normal"
        self._lot_entry.config(state=state)
        self._wafer_entry.config(state=state)
        self._go_btn.config(state=state)
        self._stop_btn.config(state="normal" if locked else "disabled")

    def _browse_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export Cassette Run CSV", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            self._csv_var.set(path)

    def _drv(self):
        drv = self.controller.drivers.get("prober")
        return drv if (drv and drv.inst) else None

    # ── Manual single-command tests ─────────────────────────────────────────

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

    def _manual_unload_next(self):
        drv = self._drv()
        if not drv:
            self._log("[CASSETTE] Send U: prober not connected.")
            return
        def _run():
            self._log("[CASSETTE] >> U  (Unload / Load Next Wafer)")
            stb = drv.cassette_unload_and_load_next(timeout_s=120)
            if stb == 65:
                self._log("[CASSETTE] << STB=65  (next wafer ready, Die #1 in contact)")
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

    # ── Full lot run ─────────────────────────────────────────────────────────

    def _start_lot(self):
        if self._running:
            return
        lot_id = self._lot_var.get().strip()
        if not lot_id:
            messagebox.showerror("Lot ID Required", "Enter a Lot ID before starting.")
            return
        try:
            wafer_num = int(self._wafer_var.get())
            if wafer_num <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Wafer #",
                                 "Starting Wafer # must be a positive whole number.")
            return

        sim = self._drv() is None
        if not messagebox.askyesno(
            "Start Lot",
            f"Start cassette-automated testing for Lot '{lot_id}'?\n\n"
            "This assumes the operator has already loaded the cassette and\n"
            "pressed NEW CST on the prober's touchscreen (EOI 8.4.1-8.4.10).\n\n"
            + ("Prober not connected — this will run SIMULATED."
               if sim else
               "The GUI locks its controls while waiting for/testing each "
               "wafer, until the lot completes or Stop is pressed.")
        ):
            return

        self._results = []
        self._tree.delete(*self._tree.get_children())
        self._running = True
        self._abort = False
        self._set_locked(True)
        self._set_state("WAITING FOR WAFER", "#f59e0b")
        threading.Thread(target=self._lot_thread, args=(lot_id, wafer_num, sim),
                         daemon=True).start()

    def _request_stop(self):
        self._abort = True
        self._log("[CASSETTE] Stop requested.")

    def _lot_thread(self, lot_id: str, wafer_num: int, sim: bool):
        drv = self._drv()
        try:
            while not self._abort:
                self._log(f"[CASSETTE] Waiting for STB=65 (Wafer #{wafer_num} ready)...")
                if sim:
                    time.sleep(0.2)
                    ready = wafer_num <= 3   # bounded simulated lot (3 wafers)
                else:
                    ready = drv.cassette_wait_for_wafer_ready(timeout_s=60) == 65
                if not ready:
                    self._log("[CASSETTE] No STB=65 — treating as idle / lot complete.")
                    break

                self._log(f"[CASSETTE] << STB=65 — Wafer #{wafer_num} ready, "
                          "Die #1 in contact.")
                self._set_state(f"TESTING WAFER #{wafer_num}", "#2563eb")
                self.after(0, lambda w=wafer_num: self._wafer_count_var.set(f"Wafer: {w}"))

                die_num = 1
                while not self._abort:
                    self.after(0, lambda d=die_num: self._die_count_var.set(f"Die: {d}"))
                    # Placeholder measurement — swap in real recipe/SMU/DMM
                    # execution here once this workflow goes into production.
                    self._log(f"[CASSETTE] Die #{die_num}: running measurements "
                             "(placeholder)...")
                    self._record(wafer_num, die_num, "measured (placeholder)")

                    if sim:
                        time.sleep(0.05)
                        stb = 67 if die_num >= 5 else 66   # bounded simulated wafer
                    else:
                        self._log("[CASSETTE] >> J  (Next Die)")
                        stb = drv.cassette_next_die(timeout_s=60)

                    if stb == 66:
                        self._log(f"[CASSETTE] << STB=66 — Die #{die_num + 1} arrived.")
                        die_num += 1
                        continue
                    if stb == 67:
                        self._log("[CASSETTE] << STB=67 — end of wafer map.")
                        self._record(wafer_num, die_num, "end of wafer map (STB=67)")
                        break
                    self._log(f"[CASSETTE] Unexpected result ({stb}) waiting for "
                             "STB=66/67 — stopping this wafer.")
                    self._record(wafer_num, die_num, f"unexpected STB={stb} — stopped")
                    break

                if self._abort:
                    break

                self._set_state("SWAPPING CASSETTE", "#f97316")
                self._log("[CASSETTE] >> U  (Unload / Load Next Wafer)")
                if sim:
                    time.sleep(0.1)
                    next_ready = wafer_num < 3   # bounded simulated lot
                else:
                    next_ready = drv.cassette_unload_and_load_next(timeout_s=180) == 65
                if next_ready:
                    wafer_num += 1
                    continue
                self._log("[CASSETTE] No next wafer (cassette empty / idle) — "
                         "Lot Complete.")
                break
        except Exception as e:
            self._log(f"[CASSETTE] ERROR: {e}")
        finally:
            self._finish(lot_id)

    def _record(self, wafer_num: int, die_num: int, event: str):
        row = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
              "wafer": wafer_num, "die": die_num, "event": event}
        self._results.append(row)
        def _ui():
            self._tree.insert("", "end", values=(row["timestamp"], row["wafer"],
                                                  row["die"], row["event"]))
            self._tree.see(self._tree.get_children()[-1])
        self.after(0, _ui)

    def _finish(self, lot_id: str):
        self._running = False
        aborted = self._abort
        saved = self._maybe_save_csv(lot_id)
        msg = "ABORTED" if aborted else "LOT COMPLETE"
        self._log(f"[CASSETTE] {msg}"
                  + (f" — saved {saved}" if saved else ""))
        self.after(0, lambda: self._set_state(msg, "#dc2626" if aborted else "#16a34a"))
        self.after(0, lambda: self._set_locked(False))

    def _maybe_save_csv(self, lot_id: str):
        path = self._csv_var.get().strip()
        if not path or not self._results:
            return None
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", newline="", encoding="utf-8") as f:
                wr = csv.DictWriter(f, fieldnames=["timestamp", "wafer", "die", "event"])
                wr.writeheader()
                wr.writerows(self._results)
            return path
        except OSError as exc:
            self._log(f"[CASSETTE] CSV save error: {exc}")
            return None
