"""Accr Wafer — dry-run wafer map extraction from the Accretech UF200/190.

Steps the prober through every valid die and records the coordinates,
reconstructing the wafer map. Command sequence per manual FT02000-R003-E0
(§3.4 Example 1, adapted for a dry run — same command semantics as the
Prober Debug tab descriptions):

  1. D — separate (chuck DOWN) so the needles never touch during the dry
         run. STB 68. Optional but ON by default: G and J restore the chuck
         to its PRIOR height after every travel, so a chuck left UP would
         re-contact the probe card at every die.
  2. G — position the start die (STB 70 = done chuck DOWN / 67 = done chuck
         UP, i.e. in CONTACT). Also resets the prober's PASS/FAIL counters.
  3. Q — read current die coordinates (response QYyyyXxxx, Y first, die
         units −99…511; clips at −99).
  4. J — position the next testing die (STB 66 = moved chuck DOWN,
         67 = moved chuck UP/contact, 81 = wafer end (no move),
         90 = <STOP> pushed on prober, 76 = alarm).
  5. Repeat 3–4 until STB 81. The die is recorded BEFORE each J, so the
         last die (whose J answers 81 without moving) is not lost.

Contact guard: when "Send D first" is on, any G/J that finishes chuck UP
(STB 67 — wafer touching the probe card) is followed immediately by D.

Requires active probing (wafer loaded & aligned, start die positioned) —
G/J/Q are rejected or indefinite otherwise. Runs a simulated wafer when no
prober is connected (phase-1 offline mode).
"""
from __future__ import annotations

import csv
import math
import os
import re
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def _parse_q(raw: str):
    """Parse a Q response (QYyyyXxxx, Y first) into (x_die, y_die) ints."""
    raw = (raw or "").strip()
    m = re.search(r'Y\s*([+-]?\d+)\s*X\s*([+-]?\d+)', raw)
    if m:
        return int(m.group(2)), int(m.group(1))
    parts = re.findall(r'[+-]?\d+', raw)
    if len(parts) >= 2:
        return int(parts[1]), int(parts[0])  # Y comes first on the wire
    raise ValueError(f"Cannot parse Q response: {raw!r}")


class AccrWaferPanel(ttk.Frame):
    def __init__(self, parent, controller, get_folder=None):
        super().__init__(parent)
        self.controller = controller
        # Callable returning the currently loaded ATA folder (or "" / None),
        # used by "Save to ATA" to write ata_wafer_map_accretech.csv there.
        self._get_folder = get_folder or (lambda: None)
        self._running = False
        self._abort   = False
        self._dies    = []   # list of (x_die, y_die, raw_q) in visit order
        # Folder whose saved ata_wafer_map_accretech.csv self._dies currently
        # reflects — None means _dies is either empty or a live/unsaved
        # extraction, which auto-loading must never clear out from under
        # the user just because a different folder was opened.
        self._loaded_ata_folder = None

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_main()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_topbar(self):
        bar = ttk.Frame(self, padding=(6, 4))
        bar.grid(row=0, column=0, sticky="ew")

        self._start_btn = ttk.Button(bar, text="▶  Extract Wafer Map",
                                     command=self._start_extraction)
        self._start_btn.pack(side="left", padx=(0, 4))
        self._abort_btn = ttk.Button(bar, text="⏹  Abort", state="disabled",
                                     command=self._request_abort)
        self._abort_btn.pack(side="left", padx=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)

        self._separate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar, text="Send D (Separate) first",
                        variable=self._separate_var).pack(side="left", padx=4)

        ttk.Label(bar, text="Max dies:").pack(side="left", padx=(12, 2))
        self._max_var = tk.StringVar(value="10000")
        ttk.Entry(bar, textvariable=self._max_var, width=7).pack(side="left")

        self._status_var = tk.StringVar(value="Idle")
        self._status_lbl = ttk.Label(bar, textvariable=self._status_var,
                                     font=("Consolas", 10, "bold"),
                                     foreground="#6b7280")
        self._status_lbl.pack(side="right", padx=8)

    def _build_main(self):
        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)

        # ── Left: collected dies ──────────────────────────────────────────
        lf = ttk.LabelFrame(pane, text="Collected Dies", padding=6)
        pane.add(lf, weight=1)
        lf.rowconfigure(1, weight=1)
        lf.columnconfigure(0, weight=1)

        self._count_var = tk.StringVar(value="0 dies")
        ttk.Label(lf, textvariable=self._count_var,
                  font=("Consolas", 10, "bold"),
                  foreground="#0077cc").grid(row=0, column=0, sticky="w", pady=(0, 4))

        self._list = tk.Text(lf, width=24, font=("Consolas", 9),
                             state="disabled", bg="#f8fafc")
        self._list.grid(row=1, column=0, sticky="nsew")
        lsb = ttk.Scrollbar(lf, orient="vertical", command=self._list.yview)
        lsb.grid(row=1, column=1, sticky="ns")
        self._list.configure(yscrollcommand=lsb.set)

        btns = ttk.Frame(lf)
        btns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(btns, text="Save CSV…", command=self._save_csv).pack(
            side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(btns, text="Copy", command=self._copy_clipboard).pack(
            side="left", expand=True, fill="x", padx=2)
        ttk.Button(btns, text="Clear", command=self._clear).pack(
            side="left", expand=True, fill="x", padx=(2, 0))

        ttk.Button(lf, text="💾 Save to ATA Folder",
                   command=self._save_to_ata).grid(
                   row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        # ── Right: wafer map canvas ───────────────────────────────────────
        rf = ttk.LabelFrame(pane, text="Reconstructed Wafer Map", padding=4)
        pane.add(rf, weight=3)
        rf.rowconfigure(0, weight=1)
        rf.columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(rf, bg="#0f172a", highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._canvas.bind("<Configure>", lambda _e: self._redraw())

    # ── Start / abort ─────────────────────────────────────────────────────────

    def _start_extraction(self):
        if self._running:
            return
        try:
            max_dies = int(self._max_var.get())
            if max_dies <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Max dies must be a positive whole number.")
            return

        drv = self.controller.drivers.get("prober")
        sim = not (drv and drv.inst)

        if sim:
            if not messagebox.askyesno(
                "Extract Wafer Map (simulation)",
                "Prober not connected — run a SIMULATED map extraction?"
            ):
                return
        elif not messagebox.askyesno(
            "Extract Wafer Map",
            "Start dry-run map extraction?\n\n"
            "The prober will drive to the start die (G) and then step through\n"
            "EVERY testing die (J), reading coordinates (Q) at each one.\n\n"
            "⚠ Physical chuck motion across the whole wafer.\n"
            "Requires active probing (wafer loaded & aligned, lot started).\n"
            + ("D (Separate) is sent first so the needles never contact."
               if self._separate_var.get() else
               "⚠ 'Send D first' is OFF — if the chuck is UP the wafer\n"
               "RE-CONTACTS the probe card at every die!")
        ):
            return

        self._clear()
        self._running = True
        self._abort   = False
        self._start_btn.config(state="disabled")
        self._abort_btn.config(state="normal")
        self._set_status("Running…", "#2563eb")
        threading.Thread(
            target=self._worker,
            args=(sim, self._separate_var.get(), max_dies),
            daemon=True,
        ).start()

    def _request_abort(self):
        if self._running:
            self._abort = True
            self._set_status("Aborting after current step…", "#f97316")
            self._log("[ACCR MAP] Abort requested — stopping after current step")
            drv = self.controller.drivers.get("prober")
            if drv and drv.inst:
                def _clear():
                    try:
                        drv.send_es()
                        self._log("[ACCR MAP] es sent (buzzer clear)")
                    except Exception as e:
                        self._log(f"[ACCR MAP] es error: {e}")
                threading.Thread(target=_clear, daemon=True).start()

    # ── Extraction workers ────────────────────────────────────────────────────

    def _worker(self, sim: bool, send_separate: bool, max_dies: int):
        try:
            if sim:
                self._worker_sim(max_dies)
            else:
                self._worker_hw(send_separate, max_dies)
        finally:
            self._running = False
            self.after(0, lambda: (self._start_btn.config(state="normal"),
                                   self._abort_btn.config(state="disabled")))

    def _ensure_separated(self, drv, stb: int, cmd: str) -> None:
        """Contact guard: G/J restore the chuck's PRIOR height, so a travel
        can finish chuck UP (STB=67 — wafer in CONTACT with the probe card).
        During a dry run that must not persist — send D to separate again."""
        if stb == 67:
            self._log(f"[ACCR MAP] ⚠ {cmd} finished chuck UP (STB=67 — contact!) "
                      ">> D  (Separate)")
            drv.z_down()
            self._log("[ACCR MAP] << STB=68  (chuck down — separated)")

    def _worker_hw(self, send_separate: bool, max_dies: int):
        drv = self.controller.drivers.get("prober")
        if not (drv and drv.inst):
            self._finish("Prober not connected", error=True)
            return
        try:
            # 1. D — separate first so G/J's height restoration keeps the
            #    chuck DOWN for the whole dry run (no needle contact).
            if send_separate:
                self._log("[ACCR MAP] >> D  (Z Down — chuck drops, wafer separates)")
                drv.z_down()
                self._log("[ACCR MAP] << STB=68  (Z Down done)")

            # 2. G — position the start die (resets PASS/FAIL counters)
            self._log("[ACCR MAP] >> G  (Position start die)")
            stb = drv.move_to_start_die()
            self._log(f"[ACCR MAP] << STB={stb}  (start die positioned, chuck "
                      f"{'UP — CONTACT' if stb == 67 else 'DOWN'})")
            if send_separate:
                self._ensure_separated(drv, stb, "G")

            while True:
                if self._abort:
                    self._finish(f"Aborted — {len(self._dies)} dies collected")
                    return
                if len(self._dies) >= max_dies:
                    self._finish(f"Stopped at max-dies cap ({max_dies})", error=True)
                    return

                # 3. Q — record the die we are on (BEFORE stepping, so the
                #    last die is kept when J answers 81 without moving)
                self._log("[ACCR MAP] >> Q  (die coordinates)")
                raw = drv.get_xy_position()
                x, y = _parse_q(raw)
                self._log(f"[ACCR MAP] << {raw!r}  → die X={x} Y={y}")
                self._add_die(x, y, raw)

                # 4. J — position the next testing die
                self._log("[ACCR MAP] >> J  (position next testing die)")
                stb = drv.next_die()
                if stb == 81:
                    self._log("[ACCR MAP] << STB=81  (wafer end — no more testing dies)")
                    self._finish(f"Complete — {len(self._dies)} dies")
                    return
                if stb == 90:
                    self._log("[ACCR MAP] << STB=90  (probing stop — <STOP> pushed)")
                    self._finish(f"<STOP> pushed on prober (STB=90) — "
                                 f"{len(self._dies)} dies collected", error=True)
                    return
                self._log(f"[ACCR MAP] << STB={stb}  (moved, chuck "
                          f"{'UP — CONTACT' if stb == 67 else 'DOWN'})")
                if send_separate:
                    self._ensure_separated(drv, stb, "J")

        except Exception as e:
            # driver raises on STB=76 (alarm), STB=74, and timeouts
            self._log(f"[ACCR MAP] ERROR: {e}")
            self._finish(f"Error after {len(self._dies)} dies — see log", error=True)

    def _worker_sim(self, max_dies: int):
        """Offline mode: serpentine walk over a circular wafer footprint."""
        self._log("[ACCR MAP] (sim) Extracting simulated wafer map…")
        radius = 12
        for row, y in enumerate(range(-radius, radius + 1)):
            xs = [x for x in range(-radius, radius + 1)
                  if math.hypot(x, y) <= radius + 0.4]
            if row % 2:
                xs.reverse()
            for x in xs:
                if self._abort:
                    self._finish(f"Aborted — {len(self._dies)} dies collected")
                    return
                if len(self._dies) >= max_dies:
                    self._finish(f"Stopped at max-dies cap ({max_dies})", error=True)
                    return
                self._add_die(x, y, f"QY{y:03d}X{x:03d}")
                time.sleep(0.02)
        self._finish(f"Complete (sim) — {len(self._dies)} dies")

    # ── Result handling (worker thread → UI) ──────────────────────────────────

    def _add_die(self, x: int, y: int, raw: str):
        self._dies.append((x, y, raw))
        n = len(self._dies)
        def _ui():
            self._count_var.set(f"{n} dies")
            self._list.config(state="normal")
            self._list.insert("end", f"{n:4d}  X{x:+04d} Y{y:+04d}\n")
            self._list.see("end")
            self._list.config(state="disabled")
            self._redraw()
        self.after(0, _ui)

    def _finish(self, msg: str, error: bool = False):
        self._log(f"[ACCR MAP] {msg}")
        self.after(0, lambda: self._set_status(msg, "#dc2626" if error else "#16a34a"))

    def _log(self, msg: str):
        self.controller.log(msg)

    def _set_status(self, text: str, color: str = "#6b7280"):
        self._status_var.set(text)
        self._status_lbl.config(foreground=color)

    # ── Wafer map canvas ──────────────────────────────────────────────────────

    def _redraw(self):
        cv = self._canvas
        cv.delete("all")
        if not self._dies:
            cv.create_text(cv.winfo_width() // 2, cv.winfo_height() // 2,
                           text="No map data — run an extraction",
                           fill="#475569", font=("Segoe UI", 11))
            return

        xs = [d[0] for d in self._dies]
        ys = [d[1] for d in self._dies]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        nx, ny = xmax - xmin + 1, ymax - ymin + 1

        w = max(cv.winfo_width(), 50)
        h = max(cv.winfo_height(), 50)
        pad = 24
        cell = max(2, min((w - 2 * pad) / nx, (h - 2 * pad) / ny))
        ox = (w - cell * nx) / 2
        oy = (h - cell * ny) / 2

        last = len(self._dies) - 1
        for i, (x, y, _raw) in enumerate(self._dies):
            # +Y is backward on the prober (far side of the wafer from the
            # operator) → draw +Y toward screen bottom, so the map matches
            # what's seen looking down at the chuck (G's start die lands
            # bottom-left, not top-left).
            cx = ox + (x - xmin) * cell
            cy = oy + (y - ymin) * cell
            color = ("#2563eb" if i == 0            # start die
                     else "#f97316" if i == last    # most recent die
                     else "#22c55e")
            cv.create_rectangle(cx + 1, cy + 1, cx + cell - 1, cy + cell - 1,
                                fill=color, outline="")

        cv.create_text(pad, h - 10, anchor="w", fill="#94a3b8", font=("Consolas", 8),
                       text=f"X {xmin}…{xmax}   Y {ymin}…{ymax}   {len(self._dies)} dies"
                            f"   ■ start  ■ latest")

    # ── Export / clear ────────────────────────────────────────────────────────

    def _save_csv(self):
        if not self._dies:
            messagebox.showinfo("No Data", "No dies collected yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="accretech_wafer_map.csv",
            title="Save wafer map",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["order", "x_die", "y_die", "raw_q"])
            for i, (x, y, raw) in enumerate(self._dies, 1):
                wr.writerow([i, x, y, raw])
        self._log(f"[ACCR MAP] Saved {len(self._dies)} dies → {path}")

    def _save_to_ata(self):
        """💾 Save to ATA Folder — write ata_wafer_map_accretech.csv into the
        loaded ATA folder, in the row/col schema WaferMapPanel.load_from_ata
        reads (row=Y die, col=X die — the Accretech die-grid indices
        themselves, no µm coordinates). Deliberately a DIFFERENT filename
        than the GDS parser's ata_wafer_map.csv so the two never collide —
        pick "Accretech" as the map source on the Wafer Map / Run tabs to
        load this one back instead of the GDS-derived map."""
        if not self._dies:
            messagebox.showinfo("No Data", "No dies collected yet.")
            return
        folder = self._get_folder()
        if not folder:
            messagebox.showerror(
                "No ATA Folder",
                "No ATA folder is loaded — use 📁 Load ATA Folder on the\n"
                "top toolbar first, then Save to ATA Folder here.")
            return
        path = os.path.join(folder, "ata_wafer_map_accretech.csv")
        if os.path.exists(path) and not messagebox.askyesno(
            "Overwrite Wafer Map",
            f"{path}\nalready exists — overwrite it with the "
            f"{len(self._dies)} die(s) extracted here?"
        ):
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["row", "col", "x_die", "y_die", "raw_q"])
            for x, y, raw in self._dies:
                wr.writerow([y, x, x, y, raw])
        self._loaded_ata_folder = folder
        self._log(f"[ACCR MAP] Saved {len(self._dies)} dies → {path}")
        self._log("[ACCR MAP] Pick 'Accretech' as the map source on the "
                  "Wafer Map / Run tabs to reload from this file.")

    def load_from_ata(self, folder: str) -> int:
        """Opportunistically restore a previous extraction: read
        ata_wafer_map_accretech.csv from folder (written by 💾 Save to ATA
        Folder) and populate the collected-dies list + preview canvas.
        Silent no-op (returns 0) if the file doesn't exist yet or an
        extraction is currently running — this is called automatically
        whenever an ATA folder is (re)loaded, not on explicit user action.

        If nothing is found here but the currently-shown dies were
        themselves loaded from a DIFFERENT folder's file, they're cleared
        (stale — belong to a folder that's no longer open); a live/unsaved
        extraction (never loaded from a file) is left alone either way."""
        if self._running or not folder:
            return 0
        path = os.path.join(folder, "ata_wafer_map_accretech.csv")
        if not os.path.exists(path):
            if self._loaded_ata_folder is not None:
                self._clear()
            return 0
        dies = []
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    try:
                        x = int(float(row.get("x_die", "")))
                        y = int(float(row.get("y_die", "")))
                    except (TypeError, ValueError):
                        continue
                    dies.append((x, y, row.get("raw_q", "")))
        except OSError as exc:
            self._log(f"[ACCR MAP] Could not read {path}: {exc}")
            return 0

        self._dies = dies
        self._loaded_ata_folder = folder
        self._count_var.set(f"{len(dies)} dies")
        self._list.config(state="normal")
        self._list.delete("1.0", "end")
        for i, (x, y, _raw) in enumerate(dies, 1):
            self._list.insert("end", f"{i:4d}  X{x:+04d} Y{y:+04d}\n")
        self._list.config(state="disabled")
        self._redraw()
        if dies:
            self._set_status(f"Loaded {len(dies)} dies from ATA folder", "#16a34a")
            self._log(f"[ACCR MAP] Auto-loaded {len(dies)} dies from {path}")
        return len(dies)

    def _copy_clipboard(self):
        if not self._dies:
            return
        text = "\n".join(f"{x},{y}" for x, y, _ in self._dies)
        self.clipboard_clear()
        self.clipboard_append(text)
        self._log(f"[ACCR MAP] Copied {len(self._dies)} dies to clipboard (x,y per line)")

    def _clear(self):
        self._dies = []
        self._loaded_ata_folder = None
        self._count_var.set("0 dies")
        self._list.config(state="normal")
        self._list.delete("1.0", "end")
        self._list.config(state="disabled")
        self._redraw()
        if not self._running:
            self._set_status("Idle")
