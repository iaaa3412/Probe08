from __future__ import annotations

import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Any, Dict, List, Optional, Tuple

from electroglas_pma import fmt_num
from pma_wafer_panel import ATA_CSV_MAP_FILENAME

try:
    import matplotlib
    try:
        matplotlib.use("TkAgg")
    except Exception:
        pass
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    _MPL = True
except ImportError:
    _MPL = False


_COLOR_BLANK = "#93c5fd"     # present, no die ID yet
_COLOR_HAS_ID = "#22c55e"    # present, has a die ID
_COLOR_SKIP = "#ef4444"      # marked skip
_COLOR_ALIGN = "#f5c518"     # marked alignment
_COLOR_ABSENT = "#e2e8f0"    # not present (blank slot in the shot / no shot here)
_COLOR_SELECTED = "#f59e0b"


def _to_float(text, default: float = 0.0) -> float:
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _to_int(text, default: int = 0) -> int:
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return default


def present_slots(cells: Dict[tuple, dict], rows: int, cols: int) -> Dict[tuple, int]:
    """(row, col) -> 1-based slot number, column-major over PRESENT cells only.

    Column-major so a slot list still reads top-to-bottom-then-left-to-right,
    the same convention electroglas_pma's quad/slot helpers already use - a
    saved die-pin map keeps meaning what it meant if the shot shape changes
    without changing which physical position is slot 1.
    """
    out = {}
    n = 0
    for c in range(cols):
        for r in range(rows):
            if cells.get((r, c), {}).get("present"):
                n += 1
                out[(r, c)] = n
    return out


def sniff_csv_kind(rows: List[List[str]]) -> Optional[str]:
    """Which of the three tabs a plain CSV grid describes, from its shape
    alone - no file extension or naming convention to rely on.

    - A header row naming pin_hi/pin_lo -> Shot (the only format with pins).
    - Every non-blank cell is 0/1/X -> Shot Map (pure presence grid).
    - Anything else with real content -> Die Map (die IDs / SKIP / ALIGN).
    - All blank -> None, so the caller falls back to whatever tab is open.
    """
    if not rows:
        return None
    header = [(c or "").strip().lower() for c in rows[0]]
    if "pin_hi" in header and "pin_lo" in header:
        return "shot"
    all_cells = [(c or "").strip() for r in rows for c in r if (c or "").strip()]
    if all_cells and all(c.upper() in ("0", "1", "X") for c in all_cells):
        return "shotmap"
    if any((c or "").strip() for r in rows for c in r):
        return "die"
    return None


def _resize_cells(cells: Dict[tuple, dict], new_rows: int, new_cols: int,
                  default: dict) -> Dict[tuple, dict]:
    """New cell dict of the given size, keeping whatever still fits."""
    out = {}
    for r in range(new_rows):
        for c in range(new_cols):
            out[(r, c)] = dict(cells.get((r, c), default))
    return out


class RecipeGenPanel(ttk.Frame):
    """Wafer Builder (Electroglas): three independent pages that together
    describe a wafer with no .PMA/.xls needed at all.

    Shot - what one touchdown covers: a rows x cols block where each slot is
    either present (assign it a HI/LO pin pair) or blank (nothing there -
    e.g. a corner of an otherwise-2x2 shot). Shot Map - how many touchdowns
    the wafer has and how they're arranged: a plain presence grid, one square
    per touchdown. Die Map - the wafer at die resolution (Shot x Shot Map
    expanded), where every real die gets an ID, and any die can be marked
    skip or alignment instead.

    A CSV can be imported on any tab; _import_csv sniffs its shape to route
    it, falling back to whichever tab is currently open if the shape alone
    doesn't say.
    """

    def __init__(self, parent, controller, main_layout):
        super().__init__(parent)
        self.controller = controller
        self._main_layout = main_layout

        self.recipe_name_var = tk.StringVar(value="NewRecipe")

        # -- Shot --
        self._shot_rows_var = tk.StringVar(value="2")
        self._shot_cols_var = tk.StringVar(value="2")
        self._die_pitch_x_var = tk.StringVar(value="1000")
        self._die_pitch_y_var = tk.StringVar(value="1000")
        self._shot_pitch_x_var = tk.StringVar(value="")
        self._shot_pitch_y_var = tk.StringVar(value="")
        self._shot_cells: Dict[tuple, dict] = {
            (r, c): {"present": True} for r in range(2) for c in range(2)}
        self._shot_pins: Dict[int, tuple] = {}
        self._shot_selected: Optional[tuple] = None
        self._shot_card_var = tk.StringVar(value="No probe card selected")
        self._shot_status_var = tk.StringVar(value="")

        # -- Shot Map --
        self._shotmap_rows_var = tk.StringVar(value="4")
        self._shotmap_cols_var = tk.StringVar(value="4")
        self._shotmap_cells: Dict[tuple, bool] = {
            (r, c): True for r in range(4) for c in range(4)}
        self._shotmap_status_var = tk.StringVar(value="")

        # -- Die Map --
        # (shot_r, shot_c, slot_r, slot_c) -> {"die_id": str, "status":
        # "normal"/"skip"/"align"}. Keyed by position, not by a flat index,
        # so it survives Shot/Shot Map edits that don't touch that slot.
        self._die_status: Dict[tuple, dict] = {}
        self._diemap_mode_var = tk.StringVar(value="id")
        self._diemap_status_var = tk.StringVar(value="")
        self._die_editor: Optional[tk.Entry] = None
        self._die_editor_key: Optional[tuple] = None
        self._die_boxes: List[dict] = []
        self._selected_die_patch = None

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_toolbar()
        self._sub_nb = ttk.Notebook(self)
        self._sub_nb.grid(row=1, column=0, sticky="nsew")

        shot_tab = ttk.Frame(self._sub_nb)
        self._sub_nb.add(shot_tab, text="Shot")
        self._build_shot_tab(shot_tab)

        shotmap_tab = ttk.Frame(self._sub_nb)
        self._sub_nb.add(shotmap_tab, text="Shot Map")
        self._build_shotmap_tab(shotmap_tab)

        diemap_tab = ttk.Frame(self._sub_nb)
        self._sub_nb.add(diemap_tab, text="Die Map")
        self._build_diemap_tab(diemap_tab)

        # Die Map is computed from Shot x Shot Map, but nothing about editing
        # either of those pages touched Die Map's cached _die_boxes/canvas -
        # so switching to Die Map after resizing Shot, or after just toggling
        # a Shot Map square, showed (and let you click into) stale die
        # positions from before the edit. Redrawing on every arrival at Die
        # Map, rather than chasing down every individual mutation call site,
        # guarantees it is always freshly recomputed from current Shot/Shot
        # Map state by the time it is visible or clickable.
        self._sub_nb.bind("<<NotebookTabChanged>>", self._on_subtab_changed)

        # Keeps PmaWaferPanel (Overlay dialog / Run tab centroid-match) alive
        # without a visible tab - Wafer Builder no longer round-trips through
        # it, but other code still reads self.pma_wafer defensively.
        self._hidden_pma_wafer_parent = ttk.Frame(self)

        self.after(300, self._load_die_pins)

    def _log(self, msg: str):
        try:
            self.controller.log(msg)
        except Exception:
            pass

    def _wiring_panel(self):
        return getattr(self._main_layout, "pin_wiring", None)

    # ------------------------------------------------------------------
    def _build_toolbar(self):
        bar = ttk.Frame(self, padding=6)
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(bar, text="Recipe Name:").pack(side="left")
        ttk.Entry(bar, textvariable=self.recipe_name_var, width=22).pack(
            side="left", padx=(4, 12))
        ttk.Button(bar, text="📥 Import CSV…", command=self._import_csv).pack(
            side="left", padx=(0, 6))

    # ==================================================================
    # SHOT — what one touchdown covers
    # ==================================================================
    _CELL = 78
    _GAP = 6

    def _build_shot_tab(self, tab):
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        top = ttk.Frame(tab, padding=6)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Label(top, text="Shot size:").pack(side="left")
        ttk.Entry(top, textvariable=self._shot_rows_var, width=3).pack(side="left")
        ttk.Label(top, text="x").pack(side="left", padx=1)
        ttk.Entry(top, textvariable=self._shot_cols_var, width=3).pack(side="left")
        ttk.Button(top, text="Apply", width=7, command=self._shot_apply_size).pack(
            side="left", padx=(4, 16))
        ttk.Label(top, text="Die pitch X/Y (µm):").pack(side="left")
        ttk.Entry(top, textvariable=self._die_pitch_x_var, width=8).pack(
            side="left", padx=(4, 2))
        ttk.Entry(top, textvariable=self._die_pitch_y_var, width=8).pack(
            side="left", padx=(2, 16))
        ttk.Label(top, text="Shot pitch X/Y (µm, blank = touching):").pack(side="left")
        ttk.Entry(top, textvariable=self._shot_pitch_x_var, width=8).pack(
            side="left", padx=(4, 2))
        ttk.Entry(top, textvariable=self._shot_pitch_y_var, width=8).pack(
            side="left", padx=(2, 4))
        ttk.Button(top, text="Apply", width=7, command=self._draw_shot).pack(
            side="left", padx=(4, 0))

        body = ttk.Frame(tab)
        body.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self._shot_canvas = tk.Canvas(body, background="#f8fafc",
                                      highlightthickness=1,
                                      highlightbackground="#cbd5e1")
        self._shot_canvas.grid(row=0, column=0, sticky="nsew")
        self._shot_canvas.bind("<Button-1>", self._on_shot_click)
        self._shot_canvas.bind("<Button-3>", self._on_shot_right_click)
        self._shot_canvas.bind("<Configure>", lambda _e: self._draw_shot())

        side = ttk.Frame(body, padding=(8, 0, 0, 0))
        side.grid(row=0, column=1, sticky="ns")
        ttk.Label(side, textvariable=self._shot_card_var,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Label(side, text="Click a blank square to add a die there; click "
                            "a die to set its pins. Right-click removes a "
                            "die (makes it blank).", foreground="#6b7280",
                 wraplength=220, justify="left").pack(anchor="w", pady=(2, 6))
        ttk.Button(side, text="💾 Save pins to probe card",
                  command=self._save_die_pins).pack(anchor="w")
        ttk.Button(side, text="↻ Reload from probe card",
                  command=self._load_die_pins).pack(anchor="w", pady=(4, 0))
        ttk.Label(side, textvariable=self._shot_status_var, foreground="#374151",
                 wraplength=220, justify="left").pack(anchor="w", pady=(6, 0))

        self._draw_shot()

    def _shot_dims(self) -> tuple:
        return (max(1, _to_int(self._shot_rows_var.get(), 1)),
               max(1, _to_int(self._shot_cols_var.get(), 1)))

    def _shot_apply_size(self):
        rows, cols = self._shot_dims()
        self._shot_cells = _resize_cells(self._shot_cells, rows, cols,
                                         {"present": True})
        self._draw_shot()

    def _shot_cell_rects(self) -> Dict[tuple, tuple]:
        rows, cols = self._shot_dims()
        w = int(self._shot_canvas.winfo_width() or 1)
        h = int(self._shot_canvas.winfo_height() or 1)
        cell = min(self._CELL,
                  max(28, (w - 20 - self._GAP * cols) // max(1, cols)),
                  max(28, (h - 20 - self._GAP * rows) // max(1, rows)))
        span_w = cols * cell + (cols - 1) * self._GAP
        span_h = rows * cell + (rows - 1) * self._GAP
        x0 = max(8, (w - span_w) // 2)
        y0 = max(8, (h - span_h) // 2)
        out = {}
        for r in range(rows):
            for c in range(cols):
                left = x0 + c * (cell + self._GAP)
                top = y0 + r * (cell + self._GAP)
                out[(r, c)] = (left, top, left + cell, top + cell)
        return out

    def _draw_shot(self):
        cv = getattr(self, "_shot_canvas", None)
        if cv is None:
            return
        cv.delete("all")
        rows, cols = self._shot_dims()
        slots = present_slots(self._shot_cells, rows, cols)
        for (r, c), (x0, y0, x1, y1) in self._shot_cell_rects().items():
            present = self._shot_cells.get((r, c), {}).get("present")
            slot = slots.get((r, c))
            pins = self._shot_pins.get(slot) if slot else None
            if not present:
                fill, outline = _COLOR_ABSENT, "#94a3b8"
            elif pins:
                fill, outline = "#bbf7d0", "#15803d"
            else:
                fill, outline = _COLOR_BLANK, "#1d4ed8"
            width = 1.5
            if (r, c) == self._shot_selected:
                outline, width = "#b45309", 3
            cv.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline,
                               width=width)
            if present:
                cv.create_text((x0 + x1) / 2, y0 + 13,
                              text=f"die {slot}", font=("Segoe UI", 8, "bold"),
                              fill="#0f172a")
                cv.create_text((x0 + x1) / 2, (y0 + y1) / 2 + 6,
                              text=(f"HI {pins[0]}\nLO {pins[1]}" if pins
                                    else "click to\nset pins"),
                              font=("Consolas", 8),
                              fill="#14532d" if pins else "#64748b",
                              justify="center")
        n_dies = len(slots)
        n_set = sum(1 for s in slots.values() if s in self._shot_pins)
        self._shot_status_var.set(f"{n_dies} die(s) in this shot, {n_set} wired.")

    def _on_shot_click(self, event):
        for (r, c), (x0, y0, x1, y1) in self._shot_cell_rects().items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self._shot_selected = (r, c)
                if not self._shot_cells.get((r, c), {}).get("present"):
                    self._shot_cells[(r, c)] = {"present": True}
                    self._draw_shot()
                    return
                self._draw_shot()
                self._assign_pins_dialog(r, c)
                return

    def _on_shot_right_click(self, event):
        for (r, c), (x0, y0, x1, y1) in self._shot_cell_rects().items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self._shot_cells[(r, c)] = {"present": False}
                if self._shot_selected == (r, c):
                    self._shot_selected = None
                self._draw_shot()
                return

    def _assign_pins_dialog(self, row: int, col: int):
        rows, cols = self._shot_dims()
        slots = present_slots(self._shot_cells, rows, cols)
        slot = slots.get((row, col))
        if slot is None:
            return
        wiring = self._wiring_panel()
        choices = wiring.get_pin_choices() if wiring else []
        if not choices:
            messagebox.showinfo(
                "No Pins", "The active probe card has no pins listed. Add "
                "them on the Probe Card tab first.")
            return
        by_pin = {v.split(":")[0]: lab for v, lab in choices}
        labels = list(by_pin.values())
        pin_of_label = {lab: pin for pin, lab in by_pin.items()}
        cur = self._shot_pins.get(slot, ("", ""))

        dlg = tk.Toplevel(self)
        dlg.title(f"Die {slot} — pins")
        dlg.transient(self.winfo_toplevel())
        dlg.resizable(False, False)
        dlg.grab_set()
        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=f"Die {slot} (row {row}, col {col})",
                 font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        vars_ = {}
        for i, (key, text) in enumerate((("hi", "HI (source):"),
                                        ("lo", "LO (return):"))):
            ttk.Label(frm, text=text).grid(row=i + 1, column=0, sticky="e", pady=3)
            v = tk.StringVar(value=by_pin.get(cur[i], ""))
            ttk.Combobox(frm, textvariable=v, values=labels, width=32,
                        state="readonly").grid(row=i + 1, column=1, sticky="w",
                                               padx=(6, 0), pady=3)
            vars_[key] = v

        def on_ok():
            hi = pin_of_label.get(vars_["hi"].get(), "")
            lo = pin_of_label.get(vars_["lo"].get(), "")
            if hi and lo and hi == lo:
                messagebox.showerror("Same Pin", "HI and LO cannot be the "
                                     "same pin.", parent=dlg)
                return
            if hi and lo:
                self._shot_pins[slot] = (hi, lo)
            else:
                self._shot_pins.pop(slot, None)
            dlg.destroy()
            self._draw_shot()

        def on_clear():
            vars_["hi"].set("")
            vars_["lo"].set("")

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btns, text="OK", command=on_ok).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear", command=on_clear).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="left", padx=4)
        dlg.update_idletasks()
        pw = self.winfo_toplevel()
        dlg.geometry(f"+{pw.winfo_x() + (pw.winfo_width() - dlg.winfo_width()) // 2}"
                    f"+{pw.winfo_y() + (pw.winfo_height() - dlg.winfo_height()) // 2}")
        dlg.wait_window()

    def _load_die_pins(self):
        wiring = self._wiring_panel()
        card = wiring.get_active_card() if wiring else ""
        self._shot_card_var.set(f"Probe card: {card}" if card
                                else "No probe card selected")
        self._shot_pins = dict(wiring.get_die_pins()) if wiring else {}
        self._draw_shot()

    def _save_die_pins(self):
        wiring = self._wiring_panel()
        card = wiring.get_active_card() if wiring else ""
        if not card:
            messagebox.showerror("No Probe Card",
                                 "Select a probe card on the Probe Card tab "
                                 "first — the die-to-pin map is stored with "
                                 "the card, not with the wafer.")
            return
        rows, cols = self._shot_dims()
        slots = present_slots(self._shot_cells, rows, cols)
        missing = [s for s in slots.values() if s not in self._shot_pins]
        if missing and not messagebox.askokcancel(
                "Incomplete Map",
                f"Die {', '.join(str(m) for m in missing)} have no pins "
                "yet.\n\nA recipe can only wire the dies that do. Save "
                "anyway?"):
            return
        if wiring.set_die_pins(card, self._shot_pins):
            self._shot_status_var.set(f"Saved {len(self._shot_pins)} die(s) "
                                      f"to '{card}'.")
        else:
            messagebox.showerror("Save Failed",
                                 f"Could not write the die-pin map to '{card}'.")

    def _die_pitch(self) -> tuple:
        return (_to_float(self._die_pitch_x_var.get(), 1.0) or 1.0,
               _to_float(self._die_pitch_y_var.get(), 1.0) or 1.0)

    def _shot_pitch(self) -> tuple:
        rows, cols = self._shot_dims()
        dx, dy = self._die_pitch()
        spx = _to_float(self._shot_pitch_x_var.get(), 0.0) or cols * dx
        spy = _to_float(self._shot_pitch_y_var.get(), 0.0) or rows * dy
        return spx, spy

    # ==================================================================
    # SHOT MAP — how many touchdowns, and their arrangement
    # ==================================================================
    def _build_shotmap_tab(self, tab):
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        top = ttk.Frame(tab, padding=6)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Label(top, text="Wafer size:").pack(side="left")
        ttk.Entry(top, textvariable=self._shotmap_rows_var, width=4).pack(side="left")
        ttk.Label(top, text="x").pack(side="left", padx=1)
        ttk.Entry(top, textvariable=self._shotmap_cols_var, width=4).pack(side="left")
        ttk.Label(top, text="touchdowns").pack(side="left", padx=(2, 8))
        ttk.Button(top, text="Apply", width=7, command=self._shotmap_apply_size).pack(
            side="left", padx=(0, 16))
        ttk.Button(top, text="☑ Fill All",
                  command=lambda: self._shotmap_set_all(True)).pack(side="left")
        ttk.Button(top, text="☐ Clear All",
                  command=lambda: self._shotmap_set_all(False)).pack(
            side="left", padx=(6, 0))
        ttk.Label(top, textvariable=self._shotmap_status_var,
                 foreground="#374151").pack(side="left", padx=12)
        ttk.Label(tab, text="Click a square to toggle whether a touchdown "
                           "lands there.", foreground="#6b7280").grid(
            row=1, column=0, sticky="w", padx=6)

        body = ttk.Frame(tab)
        body.grid(row=2, column=0, sticky="nsew", padx=6, pady=6)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)

        self._shotmap_canvas = tk.Canvas(body, background="#f8fafc",
                                         highlightthickness=1,
                                         highlightbackground="#cbd5e1")
        self._shotmap_canvas.grid(row=0, column=0, sticky="nsew")
        self._shotmap_canvas.bind("<Button-1>", self._on_shotmap_click)
        self._shotmap_canvas.bind("<Configure>", lambda _e: self._draw_shotmap())

        self._draw_shotmap()

    def _shotmap_dims(self) -> tuple:
        return (max(1, _to_int(self._shotmap_rows_var.get(), 1)),
               max(1, _to_int(self._shotmap_cols_var.get(), 1)))

    def _shotmap_apply_size(self):
        rows, cols = self._shotmap_dims()
        cells = {}
        for r in range(rows):
            for c in range(cols):
                cells[(r, c)] = self._shotmap_cells.get((r, c), True)
        self._shotmap_cells = cells
        self._draw_shotmap()

    def _shotmap_set_all(self, present: bool):
        for k in self._shotmap_cells:
            self._shotmap_cells[k] = present
        self._draw_shotmap()

    _SM_CELL = 26
    _SM_GAP = 3

    def _shotmap_cell_rects(self) -> Dict[tuple, tuple]:
        rows, cols = self._shotmap_dims()
        w = int(self._shotmap_canvas.winfo_width() or 1)
        h = int(self._shotmap_canvas.winfo_height() or 1)
        cell = min(self._SM_CELL,
                  max(6, (w - 20 - self._SM_GAP * cols) // max(1, cols)),
                  max(6, (h - 20 - self._SM_GAP * rows) // max(1, rows)))
        span_w = cols * cell + (cols - 1) * self._SM_GAP
        span_h = rows * cell + (rows - 1) * self._SM_GAP
        x0 = max(8, (w - span_w) // 2)
        y0 = max(8, (h - span_h) // 2)
        out = {}
        for r in range(rows):
            for c in range(cols):
                left = x0 + c * (cell + self._SM_GAP)
                top = y0 + r * (cell + self._SM_GAP)
                out[(r, c)] = (left, top, left + cell, top + cell)
        return out

    def _draw_shotmap(self):
        cv = getattr(self, "_shotmap_canvas", None)
        if cv is None:
            return
        cv.delete("all")
        n = 0
        for (r, c), (x0, y0, x1, y1) in self._shotmap_cell_rects().items():
            present = self._shotmap_cells.get((r, c), False)
            if present:
                n += 1
            fill = "#60a5fa" if present else "#f1f5f9"
            outline = "#1d4ed8" if present else "#cbd5e1"
            cv.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline)
        self._shotmap_status_var.set(f"{n} touchdown(s) on the wafer.")

    def _on_shotmap_click(self, event):
        for (r, c), (x0, y0, x1, y1) in self._shotmap_cell_rects().items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self._shotmap_cells[(r, c)] = not self._shotmap_cells.get((r, c), False)
                self._draw_shotmap()
                return

    # ==================================================================
    # DIE MAP — the whole wafer, at die resolution
    # ==================================================================
    def _build_diemap_tab(self, tab):
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        top = ttk.Frame(tab, padding=6)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Label(top, text="Click mode:").pack(side="left")
        for value, text in (("id", "✏ Set Die ID"), ("skip", "⛔ Mark Skip"),
                           ("align", "🎯 Mark Alignment")):
            ttk.Radiobutton(top, text=text, value=value,
                           variable=self._diemap_mode_var).pack(side="left", padx=(6, 0))
        ttk.Label(top, text="(right-click clears a die back to normal)",
                 foreground="#6b7280").pack(side="left", padx=(10, 0))
        ttk.Button(top, text="🔄 Refresh from Shot / Shot Map",
                  command=self._redraw_diemap).pack(side="left", padx=(16, 0))
        ttk.Button(top, text="🗺 Save Wafer Map",
                  command=self._save_wafer_map).pack(side="left", padx=(6, 0))
        ttk.Label(top, textvariable=self._diemap_status_var,
                 foreground="#374151").pack(side="left", padx=10)

        legend = ttk.Frame(tab)
        legend.grid(row=1, column=0, sticky="ew", padx=6)
        for color, text in [(_COLOR_HAS_ID, "has ID"), (_COLOR_BLANK, "blank"),
                           (_COLOR_SKIP, "skip"), (_COLOR_ALIGN, "alignment")]:
            sw = tk.Canvas(legend, width=12, height=12, highlightthickness=0)
            sw.create_rectangle(0, 0, 12, 12, fill=color, outline="")
            sw.pack(side="left", padx=(0, 3))
            ttk.Label(legend, text=text).pack(side="left", padx=(0, 10))

        body = ttk.Frame(tab)
        body.grid(row=2, column=0, sticky="nsew", padx=6, pady=(4, 6))
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)

        if _MPL:
            self.fig = Figure(figsize=(6, 6), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=body)
            toolbar = NavigationToolbar2Tk(self.canvas, body, pack_toolbar=False)
            toolbar.grid(row=1, column=0, sticky="ew")
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            self.canvas.mpl_connect("button_press_event", self._on_diemap_click)
            self.canvas.mpl_connect("scroll_event", self._on_diemap_scroll_zoom)
        else:
            ttk.Label(body, text="matplotlib not installed — install it to "
                                "view/edit the die map.", foreground="red").grid(
                row=0, column=0, sticky="w", padx=10, pady=10)

        self._redraw_diemap()

    def _die_positions(self) -> List[dict]:
        """Every die the current Shot x Shot Map produces, in wafer microns,
        each carrying its own status (defaulting to normal/blank)."""
        shot_rows, shot_cols = self._shot_dims()
        dpx, dpy = self._die_pitch()
        spx, spy = self._shot_pitch()
        out = []
        for (sr, sc), present in self._shotmap_cells.items():
            if not present:
                continue
            ox, oy = sc * spx, sr * spy
            for (slr, slc), cell in self._shot_cells.items():
                if not cell.get("present"):
                    continue
                key = (sr, sc, slr, slc)
                info = self._die_status.get(key, {})
                out.append({
                    "key": key, "x": ox + slc * dpx, "y": oy + slr * dpy,
                    "w": dpx, "h": dpy, "shot_r": sr, "shot_c": sc,
                    "slot_r": slr, "slot_c": slc,
                    "die_id": info.get("die_id", ""),
                    "status": info.get("status", "normal"),
                })
        return out

    def _die_color(self, box: dict) -> str:
        status = box["status"]
        if status == "skip":
            return _COLOR_SKIP
        if status == "align":
            return _COLOR_ALIGN
        return _COLOR_HAS_ID if box["die_id"] else _COLOR_BLANK

    def _redraw_diemap(self):
        # Guards construction-order calls too, not just missing matplotlib -
        # Shot/Shot Map's own initial _draw_shot()/_draw_shotmap() run during
        # __init__ before _build_diemap_tab has created self.ax/self.canvas.
        if not _MPL or not hasattr(self, "ax"):
            return
        self._close_die_editor(commit=True)
        self.ax.clear()
        self._selected_die_patch = None
        self._die_boxes = self._die_positions()
        if self._die_boxes:
            patches = [Rectangle((b["x"], b["y"]), b["w"], b["h"])
                      for b in self._die_boxes]
            coll = PatchCollection(patches, edgecolor="#0f172a", linewidths=0.3)
            coll.set_facecolor([self._die_color(b) for b in self._die_boxes])
            self.ax.add_collection(coll)
            xs = [b["x"] for b in self._die_boxes]
            ys = [b["y"] for b in self._die_boxes]
            dpx, dpy = self._die_pitch()
            self.ax.set_xlim(min(xs) - dpx, max(xs) + 2 * dpx)
            self.ax.set_ylim(min(ys) - dpy, max(ys) + 2 * dpy)
        self.ax.invert_yaxis()
        n_id = sum(1 for b in self._die_boxes if b["die_id"] and b["status"] == "normal")
        n_skip = sum(1 for b in self._die_boxes if b["status"] == "skip")
        n_align = sum(1 for b in self._die_boxes if b["status"] == "align")
        self.ax.set_title(f"{self.recipe_name_var.get()} — {len(self._die_boxes)} die(s), "
                          f"{n_id} with ID, {n_skip} skip, {n_align} alignment")
        self.ax.set_aspect("equal")
        self.ax.set_axis_off()
        self.canvas.draw_idle()
        self._diemap_status_var.set(f"{len(self._die_boxes)} die(s) on the wafer.")

    def _on_diemap_scroll_zoom(self, event):
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        self._close_die_editor(commit=True)
        factor = 0.85 if event.button == "up" else (1 / 0.85)
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        xd, yd = event.xdata, event.ydata
        self.ax.set_xlim(xd - (xd - xlim[0]) * factor, xd + (xlim[1] - xd) * factor)
        self.ax.set_ylim(yd - (yd - ylim[0]) * factor, yd + (ylim[1] - yd) * factor)
        self.canvas.draw_idle()

    def _hit_die(self, xdata, ydata) -> Optional[dict]:
        # event.xdata/ydata are already in DATA space, not screen pixels, so
        # this keeps working correctly at any zoom level - matplotlib does
        # the pixel<->data conversion itself before this handler ever runs.
        for b in self._die_boxes:
            if b["x"] <= xdata < b["x"] + b["w"] and b["y"] <= ydata < b["y"] + b["h"]:
                return b
        return None

    def _on_diemap_click(self, event):
        if event.xdata is None or event.ydata is None:
            return
        die = self._hit_die(event.xdata, event.ydata)
        if die is None:
            return
        if event.button == 3:
            self._close_die_editor(commit=True)
            self._die_status[die["key"]] = {"die_id": die["die_id"], "status": "normal"}
            self._redraw_diemap()
            return
        mode = self._diemap_mode_var.get()
        if mode == "id":
            self._select_die(die)
            self._open_die_editor(die)
        else:
            self._close_die_editor(commit=True)
            cur = self._die_status.get(die["key"], {"die_id": die["die_id"],
                                                     "status": "normal"})
            cur["status"] = "normal" if cur.get("status") == mode else mode
            self._die_status[die["key"]] = cur
            self._redraw_diemap()

    def _select_die(self, box: dict):
        if self._selected_die_patch is not None:
            try:
                self._selected_die_patch.remove()
            except Exception:
                pass
        hl = Rectangle((box["x"], box["y"]), box["w"], box["h"], fill=False,
                      edgecolor=_COLOR_SELECTED, linewidth=2.2, zorder=7)
        self.ax.add_patch(hl)
        self._selected_die_patch = hl
        self.canvas.draw_idle()

    def _open_die_editor(self, box: dict):
        self._close_die_editor(commit=True)
        (px0, py0), (px1, py1) = self.ax.transData.transform(
            [(box["x"], box["y"]), (box["x"] + box["w"], box["y"] + box["h"])])
        canvas_h = self.fig.bbox.height
        left, right = sorted((px0, px1))
        top, bottom = sorted((canvas_h - py0, canvas_h - py1))

        entry = tk.Entry(self.canvas.get_tk_widget(), borderwidth=1,
                         relief="solid", font=("Segoe UI", 9))
        entry.insert(0, box["die_id"])
        entry.select_range(0, "end")
        entry.place(x=left, y=top, width=max(right - left, 30),
                   height=max(bottom - top, 16))
        entry.focus_set()
        entry.bind("<Return>", lambda _e: self._close_die_editor(commit=True))
        entry.bind("<Escape>", lambda _e: self._close_die_editor(commit=False))
        entry.bind("<FocusOut>", lambda _e: self._close_die_editor(commit=True))
        self._die_editor = entry
        self._die_editor_key = box["key"]

    def _close_die_editor(self, commit: bool):
        entry, key = self._die_editor, self._die_editor_key
        if entry is None:
            return
        self._die_editor = None
        self._die_editor_key = None
        if commit and key is not None:
            text = entry.get().strip()
            cur = self._die_status.get(key, {"die_id": "", "status": "normal"})
            cur["die_id"] = text
            self._die_status[key] = cur
        try:
            entry.destroy()
        except Exception:
            pass
        if commit:
            self._redraw_diemap()

    # ------------------------------------------------------------------
    def _save_wafer_map(self):
        """Write the Run tab's Electroglas wafer map directly from the Die
        Map, one row per real die - no touchdown-text encoding involved,
        since this tab already knows each die's exact position and status."""
        self._close_die_editor(commit=True)
        folder = getattr(self._main_layout, "_exec2_map_folder", None) or \
            getattr(self._main_layout, "_ata_folder", None)
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("No ATA Folder", "Load an ATA folder first.")
            return
        dies = self._die_positions()
        if not dies:
            messagebox.showerror("Empty Map", "No touchdowns/dies to save — "
                                 "set up Shot and Shot Map first.")
            return
        n_id = sum(1 for d in dies if d["status"] == "normal" and d["die_id"])
        n_skip = sum(1 for d in dies if d["status"] == "skip")
        if not messagebox.askokcancel(
                "Save Wafer Map",
                f"Write {len(dies)} die(s) ({n_id} with an ID, {n_skip} skip) "
                f"to ata_wafer_map_electroglas.csv in\n{folder}?\n\n"
                "This replaces the Run tab's Electroglas wafer map."):
            return

        shot_rows, shot_cols = self._shot_dims()
        # A stable per-touchdown sequence number, row-major over the shot map
        # - only used as a label (the "seq" column), not for geometry.
        shot_order = {(sr, sc): i + 1 for i, (sr, sc) in
                     enumerate(sorted(k for k, v in self._shotmap_cells.items() if v))}
        path = os.path.join(folder, "ata_wafer_map_electroglas.csv")
        fields = ("row", "col", "seq", "quad_pos", "device_id",
                 "x_um", "y_um", "map_x", "map_y", "shot_x", "shot_y", "enabled")
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                wr = csv.DictWriter(f, fieldnames=fields)
                wr.writeheader()
                for d in dies:
                    device_id = d["die_id"] or ("ALIGN" if d["status"] == "align" else "")
                    ox, oy = d["shot_c"] * self._shot_pitch()[0], d["shot_r"] * self._shot_pitch()[1]
                    wr.writerow({
                        "row": d["shot_r"] * shot_rows + d["slot_r"],
                        "col": d["shot_c"] * shot_cols + d["slot_c"],
                        "seq": shot_order.get((d["shot_r"], d["shot_c"]), 0),
                        "quad_pos": f"R{d['slot_r']}C{d['slot_c']}",
                        "device_id": device_id,
                        "x_um": fmt_num(d["x"]), "y_um": fmt_num(-d["y"]),
                        "map_x": fmt_num(d["x"]), "map_y": fmt_num(d["y"]),
                        "shot_x": fmt_num(ox), "shot_y": fmt_num(oy),
                        "enabled": 0 if d["status"] == "skip" else 1,
                    })
        except OSError as exc:
            messagebox.showerror("Write Failed", str(exc))
            return
        self._diemap_status_var.set(f"Wrote {len(dies)} die(s) to the Run tab's wafer map.")
        self._log(f"[WAFER MAP] Wrote {path} — {len(dies)} die(s), {n_id} with an "
                 f"ID, {n_skip} skip.")
        self._sync_views(folder)

    def _sync_views(self, folder: str):
        layout = self._main_layout
        try:
            layout._exec2_map_folder = folder
            layout._exec2_map_source_var.set("Electroglas")
            layout._exec2_draw_wafer_map()
        except Exception as exc:
            self._log(f"[WAFER MAP] Map written, but the Run tab did not "
                     f"redraw: {type(exc).__name__}: {exc}")
        proc = getattr(layout, "pma_process", None)
        if proc is not None:
            try:
                proc.refresh_align_site()
            except Exception:
                pass
        self._push_to_pma_wafer(folder)

    def _plain_csv_rows(self) -> List[List[str]]:
        """This wafer as the 'plain CSV wafer map' shape PmaWaferPanel
        already understands: one cell per touchdown, holding that shot's
        dies slash-joined in Shot's own column-major slot order (skip/align
        dies written as the literal SKIP/ALIGN, matching the Die Map CSV
        import convention) - because Shot only ever includes PRESENT slots,
        every joined entry is a real die; there is no blank-corner case to
        represent here."""
        shot_rows, shot_cols = self._shot_dims()
        ordered = sorted(present_slots(self._shot_cells, shot_rows, shot_cols).items(),
                         key=lambda kv: kv[1])
        present_shots = [rc for rc, v in self._shotmap_cells.items() if v]
        max_sr = max((r for r, _ in present_shots), default=-1)
        max_sc = max((c for _, c in present_shots), default=-1)
        rows = []
        for sr in range(max_sr + 1):
            row = []
            for sc in range(max_sc + 1):
                if not self._shotmap_cells.get((sr, sc)):
                    row.append("")
                    continue
                texts = []
                for (slr, slc), _slot_no in ordered:
                    info = self._die_status.get((sr, sc, slr, slc), {})
                    status = info.get("status", "normal")
                    if status == "skip":
                        texts.append("SKIP")
                    elif status == "align":
                        texts.append("ALIGN")
                    else:
                        texts.append(info.get("die_id") or "UNNAMED")
                row.append("/".join(texts))
            rows.append(row)
        return rows

    def _push_to_pma_wafer(self, folder: str):
        """Feeds PmaWaferPanel's in-memory CSV source from this page's own
        state, best-effort. Nothing here reads ata_wafer_map_electroglas.csv
        (the file _save_wafer_map just wrote) - PmaWaferPanel is legacy
        machinery of its own, read directly by EgPmaRunPanel (the .PMA
        recipe-stepping pane's own embedded map, its shot-window sizing, and
        its per-die row/col lookup for multi-die shots) via
        self.pma_wafer._csv_shot_data/_xls_shot_data. With the old Wafer
        View tab (and its Import .xls/Load CSV buttons) gone, that data
        would otherwise never get populated again once this tab replaces
        it - silently blanking EgPmaRunPanel's own map/shot-window for
        anyone still driving a run from a loaded .PMA recipe."""
        wafer = getattr(self._main_layout, "pma_wafer", None)
        if wafer is None:
            return
        rows = self._plain_csv_rows()
        if not any(c for r in rows for c in r):
            return
        shot_rows, shot_cols = self._shot_dims()
        try:
            wafer._shot_rows_var.set(str(shot_rows))
            wafer._shot_cols_var.set(str(shot_cols))
            path = os.path.join(folder, ATA_CSV_MAP_FILENAME)
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            wafer.load_csv_path(path)
        except Exception as exc:
            self._log(f"[WAFER MAP] Could not sync the legacy .PMA-recipe "
                     f"wafer view: {type(exc).__name__}: {exc}")

    # ==================================================================
    # CSV IMPORT — one button, all three tabs
    # ==================================================================
    def _current_tab_kind(self) -> str:
        idx = self._sub_nb.index(self._sub_nb.select())
        return ("shot", "shotmap", "die")[idx] if 0 <= idx < 3 else "die"

    def _on_subtab_changed(self, _event=None):
        if self._current_tab_kind() == "die":
            self._redraw_diemap()

    def _import_csv(self):
        path = filedialog.askopenfilename(
            title="Import CSV (Shot / Shot Map / Die Map)",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8-sig") as fh:
                rows = [r for r in csv.reader(fh)]
        except OSError as exc:
            messagebox.showerror("Import Failed", f"Could not read {path}:\n{exc}")
            return
        while rows and not any((c or "").strip() for c in rows[0]):
            rows.pop(0)
        while rows and not any((c or "").strip() for c in rows[-1]):
            rows.pop()
        if not rows:
            messagebox.showerror("Empty File", f"{os.path.basename(path)} has "
                                 "no data in it.")
            return

        kind = sniff_csv_kind(rows) or self._current_tab_kind()
        name = os.path.basename(path)
        if kind == "shot":
            self._import_shot_csv(rows, name)
        elif kind == "shotmap":
            self._import_shotmap_csv(rows, name)
        else:
            self._import_diemap_csv(rows, name)

    def _import_shot_csv(self, rows: List[List[str]], name: str):
        header = [(c or "").strip().lower() for c in rows[0]]
        try:
            idx = {h: header.index(h) for h in ("row", "col", "present",
                                                "pin_hi", "pin_lo")}
        except ValueError:
            messagebox.showerror("Import Failed",
                                 "Shot CSV needs row,col,present,pin_hi,pin_lo columns.")
            return
        cells: Dict[tuple, dict] = {}
        pins_by_rc: Dict[tuple, tuple] = {}
        max_r = max_c = 0
        for r in rows[1:]:
            if len(r) <= max(idx.values()):
                continue
            rr, cc = _to_int(r[idx["row"]]), _to_int(r[idx["col"]])
            present = (r[idx["present"]] or "").strip() not in ("", "0")
            max_r, max_c = max(max_r, rr), max(max_c, cc)
            cells[(rr, cc)] = {"present": present}
            hi, lo = (r[idx["pin_hi"]] or "").strip(), (r[idx["pin_lo"]] or "").strip()
            if present and hi and lo:
                pins_by_rc[(rr, cc)] = (hi, lo)
        rows_n, cols_n = max_r + 1, max_c + 1
        cells = _resize_cells(cells, rows_n, cols_n, {"present": False})
        slots = present_slots(cells, rows_n, cols_n)
        pins = {slots[rc]: pair for rc, pair in pins_by_rc.items() if rc in slots}

        self._shot_rows_var.set(str(rows_n))
        self._shot_cols_var.set(str(cols_n))
        self._shot_cells = cells
        self._shot_pins = pins
        self._draw_shot()
        self._log(f"[WAFER BUILDER] Imported Shot from '{name}': {rows_n}x{cols_n}, "
                 f"{len(slots)} die(s), {len(pins)} wired.")
        self._sub_nb.select(0)

    def _import_shotmap_csv(self, rows: List[List[str]], name: str):
        cols_n = max(len(r) for r in rows)
        rows_n = len(rows)
        cells = {}
        n = 0
        for r, row in enumerate(rows):
            for c in range(cols_n):
                text = (row[c].strip() if c < len(row) else "")
                present = text.upper() in ("1", "X")
                cells[(r, c)] = present
                n += present
        self._shotmap_rows_var.set(str(rows_n))
        self._shotmap_cols_var.set(str(cols_n))
        self._shotmap_cells = cells
        self._draw_shotmap()
        self._log(f"[WAFER BUILDER] Imported Shot Map from '{name}': "
                 f"{rows_n}x{cols_n}, {n} touchdown(s).")
        self._sub_nb.select(1)

    def _import_diemap_csv(self, rows: List[List[str]], name: str):
        shot_rows, shot_cols = self._shot_dims()
        max_row = len(rows) - 1
        max_col = max(len(r) for r in rows) - 1
        need_shot_r = max_row // shot_rows + 1
        need_shot_c = max_col // shot_cols + 1
        cells = {}
        for r in range(need_shot_r):
            for c in range(need_shot_c):
                cells[(r, c)] = self._shotmap_cells.get((r, c), False)
        n = 0
        for r, row in enumerate(rows):
            for c in range(len(row)):
                text = (row[c] or "").strip()
                if not text:
                    continue
                sr, sc = r // shot_rows, c // shot_cols
                slr, slc = r % shot_rows, c % shot_cols
                cells[(sr, sc)] = True
                status = "normal"
                die_id = text
                if text.upper() == "SKIP":
                    status, die_id = "skip", ""
                elif text.upper() == "ALIGN":
                    status, die_id = "align", ""
                self._die_status[(sr, sc, slr, slc)] = {"die_id": die_id,
                                                        "status": status}
                n += 1
        self._shotmap_rows_var.set(str(need_shot_r))
        self._shotmap_cols_var.set(str(need_shot_c))
        self._shotmap_cells = cells
        self._draw_shotmap()
        self._redraw_diemap()
        self._log(f"[WAFER BUILDER] Imported Die Map from '{name}': {n} die(s) "
                 f"placed on a {shot_rows}x{shot_cols} shot grid.")
        self._sub_nb.select(2)
