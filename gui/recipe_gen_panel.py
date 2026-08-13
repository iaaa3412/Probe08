from __future__ import annotations

import bisect
import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Any, Dict, List, Optional

import electroglas_pma as egpma
from pma_process_panel import PMA_SOURCE_SUBDIR
from pma_wafer_panel import read_main_menu_info, read_moves_grid, real_die_ids

try:
    import xlrd
    _XLRD = True
    _XLRD_ERR = ""
except ImportError as _e:
    _XLRD = False
    _XLRD_ERR = f"{type(_e).__name__}: {_e}"

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


_COLOR_BLANK = "#93c5fd"
_COLOR_HAS_ID = "#22c55e"
_COLOR_EXCLUDED = "#ef4444"
_COLOR_SELECTED = "#f59e0b"



def _to_float(text: str, default: float = 0.0) -> float:
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _grid_from_moves(moves_grid: Dict[str, Any]) -> Dict[str, Any]:
    """Converts a pma_wafer_panel.read_moves_grid() result (real MajorMoves
    sheet geometry, one shot per xls cell) into a Recipe Gen major grid.
    A shot's raw cell text is kept verbatim as the cell's device_id -- for
    a quad-grouped recipe (e.g. LaMP's "NA/B4-00/NA/B4-01") that means the
    whole joined string becomes one device id, exactly as CreateAllFiles'
    WriteMovesFile would write it (it prints the cell's text as-is, it
    never unpacks it), not one id per real die.
    """
    cells = {(s["row"], s["col"]): {"device_id": s["raw_text"], "excluded": not s["included"]}
            for s in moves_grid["shots"]}
    return {"x_headers": list(moves_grid["x_headers"]),
           "y_headers": list(moves_grid["y_headers"]), "cells": cells}


def _minor_rows_from_moves(moves_grid: Dict[str, Any]) -> List[Dict[str, str]]:
    """Converts a MinorMoves read_moves_grid() result into Recipe Gen's flat
    minor-sites row list -- one row per INCLUDED cell, using its column/row
    header values as the site's dx/dy offset and its own text as the id
    suffix (blank if the cell has none, auto-numbered at generate time)."""
    rows = [{"dx": egpma.fmt_num(s["x_um"]), "dy": egpma.fmt_num(s["y_um"]),
            "suffix": s["raw_text"]}
           for s in moves_grid["shots"] if s["included"]]
    return rows or [{"dx": "0", "dy": "0", "suffix": ""}]


class RecipeGenPanel(ttk.Frame):
    def __init__(self, parent, controller, main_layout):
        super().__init__(parent)
        self.controller = controller
        self._main_layout = main_layout

        self.recipe_name_var = tk.StringVar(value="NewRecipe")
        self._die_size_x_var = tk.StringVar()
        self._die_size_y_var = tk.StringVar()
        # Mirrors the Wafer View page's shot layout, so the two sub-tabs can
        # never disagree about how many dies a touchdown covers.
        self._shot_rows_var = tk.StringVar(value="0")
        self._shot_cols_var = tk.StringVar(value="0")
        self._status_var = tk.StringVar(value="Build a grid to begin.")
        self._selected_var = tk.StringVar(value="Click a die on the map to edit it.")

        self._major: Dict[str, Any] = egpma.new_grid(1, 1, 0, 0, 1, 1)
        self._minor_rows: List[Dict[str, str]] = [{"dx": "0", "dy": "0", "suffix": ""}]
        self._selected_rc: Optional[tuple] = None
        self._selected_patch = None
        self._cell_editor: Optional[tk.Entry] = None
        self._cell_editor_rc: Optional[tuple] = None
        self._dielist_editor: Optional[tk.Entry] = None
        self._dielist_editor_iid: Optional[str] = None
        # Which wafer this page is currently showing. adopt_from_wafer_view is
        # called on every Wafer View refresh, so without this it would throw
        # away hand edits (grid, minor sites, a typed pick list) every time
        # that page redrew for an unrelated reason.
        self._adopted_sig: Optional[tuple] = None
        # Shot map: slot number -> (HI pin, LO pin). Mirrors the active probe
        # card's DIEPIN table; unsaved until "Save pins to probe card".
        self._shot_pins: Dict[int, tuple] = {}
        self._shot_selected: Optional[int] = None
        self._shot_card_var = tk.StringVar(value="No probe card selected")
        self._shot_pins_var = tk.StringVar(value="")

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_main_fields()
        self._build_body()
        self.after(300, self._load_die_pins)

    def _log(self, msg: str):
        try:
            self.controller.log(msg)
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _build_toolbar(self):
        bar = ttk.Frame(self, padding=6)
        bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(bar, text="Recipe Name:").pack(side="left")
        ttk.Entry(bar, textvariable=self.recipe_name_var, width=22).pack(
            side="left", padx=(4, 12))
        ttk.Button(bar, text="🧱 Build Major Grid…", command=self._build_grid_dialog).pack(
            side="left", padx=(0, 6))
        ttk.Button(bar, text="📥 Import .xls…",
                  command=self._import_xls_template).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="📥 Import die-ID CSV…",
                  command=self._import_csv_template).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="🗺 Save Wafer Map", command=self._save_wafer_map).pack(
            side="left", padx=(0, 6))
        ttk.Label(bar, textvariable=self._status_var, foreground="#374151").pack(
            side="left", padx=10)

    def _build_main_fields(self):
        """Wafer geometry only.

        This used to carry the .PMA's whole Main Menu header - Voltage,
        Delay1/2/3, Iterations, MeterDelay, Averages, NPLC, MeterCurrentLimit,
        MeterRange, and the align-site move vector. Those describe a
        MEASUREMENT and a move sequence, not a wafer, and they belong to the
        recipe; having them here meant the same numbers existed in two places
        with nothing keeping them equal. The die pitch stays because it is
        geometry: without it a grid of IDs says where dies sit relative to
        each other but not how far apart.
        """
        lf = ttk.LabelFrame(self, text="Wafer Geometry", padding=8)
        lf.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 4))
        ttk.Label(lf, text="Die pitch X (um):").pack(side="left")
        ttk.Entry(lf, textvariable=self._die_size_x_var, width=12).pack(
            side="left", padx=(4, 12))
        ttk.Label(lf, text="Die pitch Y (um):").pack(side="left")
        ttk.Entry(lf, textvariable=self._die_size_y_var, width=12).pack(
            side="left", padx=(4, 12))
        ttk.Label(lf, text="Shot layout:").pack(side="left")
        ttk.Entry(lf, textvariable=self._shot_rows_var, width=3).pack(side="left")
        ttk.Label(lf, text="x").pack(side="left", padx=1)
        ttk.Entry(lf, textvariable=self._shot_cols_var, width=3).pack(side="left")
        ttk.Label(lf, text="dies per touchdown", foreground="#6b7280",
                  font=("Arial", 8)).pack(side="left", padx=(3, 4))
        ttk.Button(lf, text="Apply", width=7,
                   command=self._apply_shot_layout).pack(side="left", padx=(0, 10))
        ttk.Label(lf, text="Pitch is the SHOT pitch — the step between "
                           "touchdowns, not one die.",
                  foreground="#6b7280", font=("Arial", 8)).pack(side="left")

    def _build_body(self):
        split = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        split.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))

        # Two maps, because there are two things to describe and they are not
        # the same shape: what one touchdown covers (a handful of dies, each
        # reached by its own pins) and where those touchdowns land on the
        # wafer. Stacked rather than side by side so the wafer keeps its width.
        maps = ttk.PanedWindow(split, orient=tk.VERTICAL)
        split.add(maps, weight=3)

        self._build_shot_map(maps)

        left = ttk.Frame(maps)
        maps.add(left, weight=4)
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        if _MPL:
            self.fig = Figure(figsize=(6, 6), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=left)
            toolbar = NavigationToolbar2Tk(self.canvas, left, pack_toolbar=False)
            toolbar.grid(row=1, column=0, sticky="ew")
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            self.canvas.mpl_connect("button_press_event", self._on_grid_click)
            self.canvas.mpl_connect("scroll_event", self._on_scroll_zoom)
        else:
            ttk.Label(left, text="matplotlib not installed — install it to edit "
                                 "the recipe grid.", foreground="red").grid(
                row=0, column=0, sticky="w", padx=10, pady=10)

        wafer_btns = ttk.Frame(left)
        wafer_btns.grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Label(wafer_btns, text="Wafer — one cell per touchdown:",
                  font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        ttk.Button(wafer_btns, text="＋ Row", width=8,
                   command=lambda: self._grow_grid(rows=1)).pack(side="left")
        ttk.Button(wafer_btns, text="＋ Col", width=8,
                   command=lambda: self._grow_grid(cols=1)).pack(side="left", padx=(4, 0))
        ttk.Label(wafer_btns, text="then click a cell and type its die IDs "
                                   "(slash-separated, NA for an empty slot)",
                  foreground="#6b7280", font=("Arial", 8)).pack(side="left", padx=(8, 0))

        right = ttk.Frame(split, padding=6)
        split.add(right, weight=2)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        legend = ttk.Frame(right)
        legend.grid(row=0, column=0, sticky="w", pady=(0, 6))
        for color, text in [(_COLOR_BLANK, "included (auto ID)"),
                            (_COLOR_HAS_ID, "included (custom ID)"),
                            (_COLOR_EXCLUDED, "excluded")]:
            sw = tk.Canvas(legend, width=12, height=12, highlightthickness=0)
            sw.create_rectangle(0, 0, 12, 12, fill=color, outline="")
            sw.pack(side="left", padx=(0, 3))
            ttk.Label(legend, text=text).pack(side="left", padx=(0, 10))

        right_split = ttk.PanedWindow(right, orient=tk.VERTICAL)
        right_split.grid(row=1, column=0, sticky="nsew")

        sel_lf = ttk.LabelFrame(right_split, text="Selected die", padding=6)
        right_split.add(sel_lf, weight=0)
        sel_lf.columnconfigure(0, weight=1)
        ttk.Label(sel_lf, textvariable=self._selected_var, justify="left",
                 wraplength=260).grid(row=0, column=0, sticky="w")
        ttk.Label(sel_lf, text="Click a cell to select + edit it in place "
                 "(type, then Enter/Tab to move to the next cell, Esc to "
                 "cancel). Right-click toggles excluded.",
                 foreground="#6b7280", wraplength=260,
                 justify="left").grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Button(sel_lf, text="Toggle Exclude", command=self._toggle_exclude).grid(
            row=2, column=0, sticky="w", pady=(6, 0))

        die_lf = ttk.LabelFrame(right_split, text="Die List", padding=6)
        right_split.add(die_lf, weight=2)
        die_lf.rowconfigure(0, weight=1)
        die_lf.columnconfigure(0, weight=1)
        self._dielist_tree = ttk.Treeview(
            die_lf, columns=("id", "shot"), show="headings", height=8,
            selectmode="extended")
        self._dielist_tree.heading("id", text="Device ID")
        self._dielist_tree.column("id", width=150)
        self._dielist_tree.heading("shot", text="Shot")
        self._dielist_tree.column("shot", width=70, anchor="center")
        self._dielist_tree.grid(row=0, column=0, sticky="nsew")
        dsb = ttk.Scrollbar(die_lf, orient="vertical", command=self._dielist_tree.yview)
        self._dielist_tree.configure(yscrollcommand=dsb.set)
        dsb.grid(row=0, column=1, sticky="ns")
        self._dielist_tree.bind("<Double-1>", self._on_dielist_double_click)
        ttk.Label(die_lf, text="Every die on the loaded wafer; greyed rows are "
                 "not probed by this recipe. Double-click a row (or ＋ Add) to "
                 "type a device ID; Enter commits and adds the next row. The "
                 "pick buttons act on the selected rows, or on the whole list "
                 "when nothing is selected.",
                 foreground="#6b7280", wraplength=260,
                 justify="left").grid(row=1, column=0, columnspan=2, sticky="w",
                                     pady=(4, 0))
        row_btns = ttk.Frame(die_lf)
        row_btns.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Button(row_btns, text="＋ Add", command=self._add_dielist_row).pack(side="left")
        ttk.Button(row_btns, text="🗑 Remove",
                  command=self._remove_dielist_row).pack(side="left", padx=(6, 0))
        pick_btns = ttk.Frame(die_lf)
        pick_btns.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Button(pick_btns, text="🎯 Test These Devices",
                  command=self._test_these_devices).pack(side="left")
        ttk.Button(pick_btns, text="↺ Un-pick These Devices",
                  command=self._unpick_these_devices).pack(side="left", padx=(6, 0))
        bulk_btns = ttk.Frame(die_lf)
        bulk_btns.grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Button(bulk_btns, text="☒ Exclude All",
                  command=lambda: self._set_all_excluded(True)).pack(side="left")
        ttk.Button(bulk_btns, text="☐ Include All",
                  command=lambda: self._set_all_excluded(False)).pack(
            side="left", padx=(6, 0))

        minor_lf = ttk.LabelFrame(right_split, text="Minor Sites (sub-die touchdowns)",
                                  padding=6)
        right_split.add(minor_lf, weight=1)
        minor_lf.rowconfigure(0, weight=1)
        minor_lf.columnconfigure(0, weight=1)
        cols = ("dx", "dy", "suffix")
        self._minor_tree = ttk.Treeview(
            minor_lf, columns=cols, show="headings", height=4, selectmode="browse")
        for cid, text, w in (("dx", "ΔX", 70), ("dy", "ΔY", 70), ("suffix", "ID suffix", 90)):
            self._minor_tree.heading(cid, text=text)
            self._minor_tree.column(cid, width=w, anchor="center")
        self._minor_tree.grid(row=0, column=0, sticky="nsew")
        self._refresh_minor_tree()
        minor_btns = ttk.Frame(minor_lf)
        minor_btns.grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Button(minor_btns, text="＋ Add Site", command=self._add_minor_site).pack(
            side="left")
        ttk.Button(minor_btns, text="🗑 Remove Selected",
                  command=self._remove_minor_site).pack(side="left", padx=(6, 0))

        self._redraw_grid()
        self._draw_shot_map()

    # ------------------------------------------------------------------
    # THE SHOT MAP
    #
    # A touchdown lands several dies at once and each one is reached by its
    # own pair of pins. That mapping used to be typed into a probe-card CSV by
    # hand, or guessed from pad labels like "BRU" - a convention that holds on
    # exactly one card. Here it is drawn: say the shot is 2x3, get six squares,
    # and put pins on each. Pins, not pad names, because the pin is the
    # physical contact that reaches the relay and still means something on the
    # next card and the next product.
    # ------------------------------------------------------------------
    _SHOT_CELL = 78
    _SHOT_GAP = 6

    def _build_shot_map(self, parent):
        lf = ttk.LabelFrame(parent, text="Shot — what one touchdown covers",
                            padding=6)
        parent.add(lf, weight=1)
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        self._shot_canvas = tk.Canvas(lf, height=self._SHOT_CELL * 2 + 24,
                                      background="#f8fafc", highlightthickness=1,
                                      highlightbackground="#cbd5e1")
        self._shot_canvas.grid(row=0, column=0, sticky="nsew")
        self._shot_canvas.bind("<Button-1>", self._on_shot_click)
        self._shot_canvas.bind("<Configure>", lambda _e: self._draw_shot_map())

        side = ttk.Frame(lf)
        side.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        ttk.Label(side, textvariable=self._shot_card_var,
                  font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Label(side, text="Click a die to set the two pins that land on "
                             "it. HI is the sourced pin, LO the return.",
                  foreground="#6b7280", wraplength=200,
                  justify="left").pack(anchor="w", pady=(2, 6))
        ttk.Button(side, text="💾 Save pins to probe card",
                   command=self._save_die_pins).pack(anchor="w")
        ttk.Button(side, text="↻ Reload from probe card",
                   command=self._load_die_pins).pack(anchor="w", pady=(4, 0))
        ttk.Label(side, textvariable=self._shot_pins_var, foreground="#374151",
                  wraplength=200, justify="left").pack(anchor="w", pady=(6, 0))

    def _wiring_panel(self):
        return getattr(self._main_layout, "pin_wiring", None)

    def _shot_slots(self) -> tuple:
        """(rows, cols) the shot map is drawing, always at least 1x1."""
        rows = int(_to_float(self._shot_rows_var.get(), 0))
        cols = int(_to_float(self._shot_cols_var.get(), 0))
        if rows > 0 and cols > 0:
            return rows, cols
        return egpma.shot_geometry(self._dies_per_shot())

    def _dies_per_shot(self) -> int:
        n = 0
        for cell in self._major["cells"].values():
            text = (cell.get("device_id") or "").strip()
            if text and not cell.get("excluded"):
                n = max(n, len(text.split("/")))
        return n or 1

    def _apply_shot_layout(self):
        rows, cols = self._shot_slots()
        wafer = getattr(self._main_layout, "pma_wafer", None)
        data = getattr(wafer, "workbook_data", None) if wafer else None
        widest = max((len(s.get("dies") or []) for s in (data or {}).get("shots", [])),
                     default=0)
        regrouped = False
        if widest and rows * cols < widest:
            # Shrinking the shot is not a relabel - those dies still exist and
            # still have to come down in SOME touchdown. Re-shotting regroups
            # them; changing the layout alone would quietly drop the overflow.
            if rows != 1:
                messagebox.showerror(
                    "Shot Too Small",
                    f"This wafer has touchdowns of up to {widest} dies, which "
                    f"does not fit a {rows}x{cols} shot.\n\nRegrouping is only "
                    "defined for single-row shots — set the rows to 1 first, "
                    "or widen the shot.")
                return
            if not messagebox.askokcancel(
                    "Regroup the wafer?",
                    f"Touchdowns on this wafer cover up to {widest} dies; a "
                    f"{rows}x{cols} shot holds {rows * cols}.\n\nRegroup the "
                    f"same dies into {rows * cols}-die touchdowns? The dies "
                    "and their IDs do not change — only which of them come "
                    "down together, and so how many touchdowns there are."):
                return
            try:
                wafer._reshot_to(rows * cols)
                regrouped = True
            except Exception as exc:
                messagebox.showerror("Regroup Failed",
                                     f"{type(exc).__name__}: {exc}")
                return
        self._shot_rows_var.set(str(rows))
        self._shot_cols_var.set(str(cols))
        self._draw_shot_map()
        # A regroup has already set the layout and redrawn. Delegating on top
        # of it would re-stamp the ORIGINAL source too - the .xls still holds
        # 5-die touchdowns - and that check fails, so it reported an error for
        # a regroup that had just succeeded.
        applied = regrouped
        if not regrouped and wafer is not None and hasattr(wafer, "_apply_shot_layout"):
            try:
                wafer._shot_rows_var.set(str(rows))
                wafer._shot_cols_var.set(str(cols))
                wafer._apply_shot_layout()
                applied = True
            except Exception as exc:
                self._log(f"[SHOT] Wafer View did not take the layout: "
                          f"{type(exc).__name__}: {exc}")
        self._status_var.set(f"Shot is {rows} x {cols} = {rows * cols} dies "
                             "per touchdown."
                             + ("" if applied else "  (Wafer View not loaded)"))
        self._log(f"[SHOT] Shot layout set to {rows}x{cols} "
                  f"({rows * cols} dies per touchdown).")

    def _load_die_pins(self):
        wiring = self._wiring_panel()
        card = wiring.get_active_card() if wiring else ""
        self._shot_card_var.set(f"Probe card: {card}" if card
                                else "No probe card selected")
        self._shot_pins = dict(wiring.get_die_pins()) if wiring else {}
        self._draw_shot_map()

    def _save_die_pins(self):
        wiring = self._wiring_panel()
        card = wiring.get_active_card() if wiring else ""
        if not card:
            messagebox.showerror("No Probe Card",
                                 "Select a probe card on the Probe Card tab "
                                 "first — the die-to-pin map is stored with "
                                 "the card, not with the wafer.")
            return
        rows, cols = self._shot_slots()
        missing = [s for s in range(1, rows * cols + 1) if s not in self._shot_pins]
        if missing and not messagebox.askokcancel(
                "Incomplete Map",
                f"Die {', '.join(str(m) for m in missing)} have no pins yet.\n\n"
                "A recipe can only wire the dies that do. Save anyway?"):
            return
        if wiring.set_die_pins(card, self._shot_pins):
            self._shot_pins_var.set(f"Saved {len(self._shot_pins)} die(s) to "
                                    f"'{card}'.")
        else:
            messagebox.showerror("Save Failed",
                                 f"Could not write the die-pin map to '{card}'.")

    def _shot_cell_rects(self) -> Dict[int, tuple]:
        """slot number -> (x0, y0, x1, y1) on the canvas.

        Slot numbering follows electroglas_pma's column-major slot order, the
        same order a device ID lists its dies in and the same order the DIEPIN
        rows are stored in, so what is drawn here is what a recipe wires.
        """
        rows, cols = self._shot_slots()
        w = int(self._shot_canvas.winfo_width() or 1)
        h = int(self._shot_canvas.winfo_height() or 1)
        cell = min(self._SHOT_CELL,
                   max(28, (w - 20 - self._SHOT_GAP * cols) // max(1, cols)),
                   max(28, (h - 20 - self._SHOT_GAP * rows) // max(1, rows)))
        span_w = cols * cell + (cols - 1) * self._SHOT_GAP
        span_h = rows * cell + (rows - 1) * self._SHOT_GAP
        x0 = max(8, (w - span_w) // 2)
        y0 = max(8, (h - span_h) // 2)
        out = {}
        for i in range(rows * cols):
            r, c = i % rows, i // rows          # column-major, as above
            left = x0 + c * (cell + self._SHOT_GAP)
            top = y0 + r * (cell + self._SHOT_GAP)
            out[i + 1] = (left, top, left + cell, top + cell)
        return out

    def _draw_shot_map(self):
        cv = getattr(self, "_shot_canvas", None)
        if cv is None:
            return
        cv.delete("all")
        rows, cols = self._shot_slots()
        rects = self._shot_cell_rects()
        names = egpma.slot_names(rows, cols)
        for slot, (x0, y0, x1, y1) in rects.items():
            pins = self._shot_pins.get(slot)
            fill = "#bbf7d0" if pins else "#e2e8f0"
            outline = "#15803d" if pins else "#94a3b8"
            if slot == self._shot_selected:
                outline, width = "#b45309", 3
            else:
                width = 1.5
            cv.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline,
                                width=width)
            pos = names[slot - 1] if slot - 1 < len(names) else ""
            cv.create_text((x0 + x1) / 2, y0 + 13,
                           text=f"die {slot}" + (f"  ({pos})" if pos else ""),
                           font=("Segoe UI", 8, "bold"), fill="#0f172a")
            cv.create_text((x0 + x1) / 2, (y0 + y1) / 2 + 6,
                           text=(f"HI {pins[0]}\nLO {pins[1]}" if pins
                                 else "click to\nset pins"),
                           font=("Consolas", 8),
                           fill="#14532d" if pins else "#64748b",
                           justify="center")
        n_set = sum(1 for s in rects if s in self._shot_pins)
        self._shot_pins_var.set(f"{n_set} of {len(rects)} dies wired.")

    def _on_shot_click(self, event):
        for slot, (x0, y0, x1, y1) in self._shot_cell_rects().items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self._shot_selected = slot
                self._draw_shot_map()
                self._assign_pins_dialog(slot)
                return

    def _assign_pins_dialog(self, slot: int):
        wiring = self._wiring_panel()
        choices = wiring.get_pin_choices() if wiring else []
        if not choices:
            messagebox.showinfo(
                "No Pins", "The active probe card has no pins listed. Add them "
                "on the Probe Card tab first — this map points at pins, so "
                "there is nothing to point at yet.")
            return
        # value is "PIN:pad" or "PIN"; the stored map keeps the bare pin,
        # because that is what the relay wiring is looked up by.
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
        rows, cols = self._shot_slots()
        ttk.Label(frm, text=f"Die {slot} of {rows * cols} "
                            f"({egpma.slot_label(egpma.slot_names(rows, cols)[slot - 1], rows, cols)})",
                  font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=2,
                                                     sticky="w", pady=(0, 8))
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
                messagebox.showerror("Same Pin",
                                     "HI and LO cannot be the same pin — that "
                                     "is a short across the source.", parent=dlg)
                return
            if hi and lo:
                self._shot_pins[slot] = (hi, lo)
            else:
                self._shot_pins.pop(slot, None)
            dlg.destroy()
            self._draw_shot_map()
            self._log(f"[SHOT] Die {slot} = HI {hi or '—'} / LO {lo or '—'} "
                      "(not saved to the card yet).")

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

    def _grow_grid(self, rows: int = 0, cols: int = 0):
        """Add empty touchdown positions to the wafer without rebuilding it."""
        self._close_cell_editor(commit=True)
        xh = list(self._major["x_headers"])
        yh = list(self._major["y_headers"])
        pitch_x = _to_float(self._die_size_x_var.get()) or \
            (xh[1] - xh[0] if len(xh) > 1 else 1000.0)
        pitch_y = _to_float(self._die_size_y_var.get()) or \
            (yh[1] - yh[0] if len(yh) > 1 else 1000.0)
        for _ in range(max(0, cols)):
            xh.append((xh[-1] if xh else 0.0) + pitch_x)
        for _ in range(max(0, rows)):
            yh.append((yh[-1] if yh else 0.0) + pitch_y)
        cells = self._major["cells"]
        for r in range(len(yh)):
            for c in range(len(xh)):
                # New positions start EXCLUDED: an empty cell is off the wafer
                # until someone names a die there, which is what keeps a map
                # wafer-shaped instead of a filled rectangle.
                cells.setdefault((r, c), {"device_id": "", "excluded": True})
        self._major = {"x_headers": xh, "y_headers": yh, "cells": cells}
        self._redraw_grid()
        self._status_var.set(f"Wafer grid is now {len(yh)} rows x {len(xh)} "
                             "cols. Click a new cell and type its die IDs.")

    # ------------------------------------------------------------------
    def _build_grid_dialog(self):
        self._close_cell_editor(commit=False)
        dlg = tk.Toplevel(self)
        dlg.title("Build Major Grid")
        dlg.transient(self.winfo_toplevel())
        dlg.resizable(False, False)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)

        specs = [
            ("Rows:", "rows", "8"),
            ("Cols:", "cols", "8"),
            ("X start (µm):", "x_start", self._die_size_x_var.get() or "0"),
            ("Y start (µm):", "y_start", self._die_size_y_var.get() or "0"),
            ("Pitch X (µm):", "pitch_x", self._die_size_x_var.get() or "1000"),
            ("Pitch Y (µm):", "pitch_y", self._die_size_y_var.get() or "1000"),
        ]
        vars_ = {}
        for row, (label, key, default) in enumerate(specs):
            ttk.Label(frm, text=label).grid(row=row, column=0, sticky="e", pady=2)
            v = tk.StringVar(value=default)
            ttk.Entry(frm, textvariable=v, width=14).grid(
                row=row, column=1, sticky="w", padx=(6, 0), pady=2)
            vars_[key] = v

        result = {}

        def on_ok():
            try:
                rows = int(vars_["rows"].get())
                cols = int(vars_["cols"].get())
                x_start = float(vars_["x_start"].get())
                y_start = float(vars_["y_start"].get())
                pitch_x = float(vars_["pitch_x"].get())
                pitch_y = float(vars_["pitch_y"].get())
            except ValueError:
                messagebox.showerror("Invalid Input", "All fields must be numbers "
                                     "(rows/cols must be whole numbers).", parent=dlg)
                return
            if rows < 1 or cols < 1:
                messagebox.showerror("Invalid Input", "Rows and columns must be "
                                     "at least 1.", parent=dlg)
                return
            result.update(rows=rows, cols=cols, x_start=x_start, y_start=y_start,
                         pitch_x=pitch_x, pitch_y=pitch_y)
            dlg.destroy()

        btns = ttk.Frame(frm)
        btns.grid(row=len(specs), column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btns, text="Build", command=on_ok).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="left", padx=4)

        dlg.update_idletasks()
        pw = self.winfo_toplevel()
        x = pw.winfo_x() + (pw.winfo_width() - dlg.winfo_width()) // 2
        y = pw.winfo_y() + (pw.winfo_height() - dlg.winfo_height()) // 2
        dlg.geometry(f"+{x}+{y}")
        dlg.wait_window()

        if not result or not self._confirm_discard_edits():
            return
        self._major = egpma.new_grid(result["rows"], result["cols"], result["x_start"],
                                     result["y_start"], result["pitch_x"], result["pitch_y"])
        if not self._die_size_x_var.get():
            self._die_size_x_var.set(egpma.fmt_num(result["pitch_x"]))
        if not self._die_size_y_var.get():
            self._die_size_y_var.set(egpma.fmt_num(result["pitch_y"]))
        self._selected_rc = None
        self._status_var.set(f"Grid built: {result['rows']} x {result['cols']} dies.")
        self._redraw_grid()

    def _confirm_discard_edits(self) -> bool:
        has_edits = any(c.get("device_id") or c.get("excluded")
                       for c in self._major["cells"].values())
        if not has_edits:
            return True
        return messagebox.askyesno(
            "Replace Grid",
            "This will discard the current grid's device IDs and exclusions. Continue?")

    # -- plain die-ID CSV ---------------------------------------------------
    #
    # The simple way in, and the one that does not need a legacy workbook: a
    # CSV laid out like the wafer. One cell per SHOT, holding that shot's
    # device ID - or the slash-joined IDs of the dies it co-touches, exactly
    # as the workbook writes them. Blank cells are off-wafer. Nothing else:
    # no headers, no coordinates. The pitch comes from the Die Size fields,
    # which is the one thing a bare grid cannot tell us.

    def _import_csv_template(self):
        self._close_cell_editor(commit=False)
        path = filedialog.askopenfilename(
            title="Import a die-ID CSV (laid out like the wafer)",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8-sig") as fh:
                rows = [r for r in csv.reader(fh)]
        except OSError as exc:
            messagebox.showerror("Import Failed", f"Could not read {path}:\n{exc}")
            return
        # Trim fully blank leading/trailing rows so a file with padding still
        # lands with the wafer at the origin.
        while rows and not any((c or "").strip() for c in rows[0]):
            rows.pop(0)
        while rows and not any((c or "").strip() for c in rows[-1]):
            rows.pop()
        if not rows:
            messagebox.showerror("Empty File",
                                 f"{os.path.basename(path)} has no die IDs in it.")
            return

        pitch_x = _to_float(self._die_size_x_var.get())
        pitch_y = _to_float(self._die_size_y_var.get())
        if not pitch_x or not pitch_y:
            messagebox.showerror(
                "Die Size Needed",
                "Set Die Size X and Y (in microns) before importing a die-ID "
                "CSV.\n\nA bare grid of IDs says where dies are relative to "
                "each other but not how far apart they are, and the pitch is "
                "what every move on the Run tab is computed from.")
            return
        if not self._confirm_discard_edits():
            return

        cols = max(len(r) for r in rows)
        grid = egpma.new_grid(len(rows), cols, 0.0, 0.0, pitch_x, pitch_y)
        n = 0
        for r, row in enumerate(rows):
            for c in range(cols):
                text = (row[c].strip() if c < len(row) else "")
                cell = grid["cells"][(r, c)]
                cell["device_id"] = text
                # A blank cell is off the wafer, not an unnamed die - that is
                # what makes the grid wafer-shaped.
                cell["excluded"] = not text
                if text:
                    n += 1

        self._major = grid
        self._selected_rc = None
        self._redraw_grid()
        self._status_var.set(f"Imported {n} shot(s) from "
                             f"{os.path.basename(path)} ({cols}x{len(rows)} grid).")
        self._log(f"[WAFER MAP] Imported '{os.path.basename(path)}' — {cols}x"
                  f"{len(rows)} grid, {n} shot(s) with a device ID, pitch "
                  f"{pitch_x:g} x {pitch_y:g} um. Blank cells are treated as "
                  "off-wafer.")

    def _save_wafer_map(self):
        """Write the Run tab's wafer map straight from this grid.

        The point of this tab: a map without going through .PMA/.PMS/.PMV at
        all. Writes the same ata_wafer_map_electroglas.csv the PMA Process
        path produces, so the Run tab, the die-ID overlay and the exports all
        read it the same way and cannot tell where it came from.
        """
        self._close_cell_editor(commit=True)
        pitch_x = _to_float(self._die_size_x_var.get())
        pitch_y = _to_float(self._die_size_y_var.get())
        if not pitch_x or not pitch_y:
            messagebox.showerror("Die Size Needed",
                                 "Set Die Size X and Y (in microns) first.")
            return
        folder = getattr(self._main_layout, "_exec2_map_folder", None) or \
            getattr(self._main_layout, "_ata_folder", None)
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("No ATA Folder", "Load an ATA folder first.")
            return

        shots = []
        for (r, c), cell in sorted(self._major["cells"].items()):
            text = (cell.get("device_id") or "").strip()
            if not text or cell.get("excluded"):
                continue
            shots.append({"seq": len(shots) + 1, "device_id": text,
                          "devices": [t.strip() for t in text.split("/")],
                          "x": self._major["x_headers"][c],
                          "y": self._major["y_headers"][r]})
        if not shots:
            messagebox.showerror("Empty Map",
                                 "No included cell has a device ID, so there is "
                                 "no wafer map to write.")
            return
        n_dies = len(egpma.expand_touchdowns_to_dies(shots, pitch_x, pitch_y))
        if not messagebox.askokcancel(
                "Save Wafer Map",
                f"Write {len(shots)} shot(s) / {n_dies} die(s) to\n"
                f"ata_wafer_map_electroglas.csv in\n{folder}?\n\n"
                "This replaces the Run tab's Electroglas wafer map."):
            return
        try:
            path = egpma.save_wafer_map_csv(
                folder, shots, {"DieSizeX": pitch_x, "DieSizeY": pitch_y})
        except OSError as exc:
            messagebox.showerror("Write Failed", str(exc))
            return
        self._status_var.set(f"Wrote {len(shots)} shot(s) / {n_dies} die(s) "
                             "to the Run tab's wafer map.")
        self._log(f"[WAFER MAP] Wrote {path} — {len(shots)} shot(s), {n_dies} die(s).")
        self._sync_views(folder)

    def adopt_from_wafer_view(self):
        """Load whatever the Wafer View page is showing into Build / Edit.

        The two pages describe the same wafer, and they used to hold entirely
        separate state: opening a CSV populated the map beside this one while
        this grid stayed at its 1x1 default, so the fields were blank for a
        wafer that was plainly loaded. Editing then started from nothing.
        """
        wafer = getattr(self._main_layout, "pma_wafer", None)
        data = getattr(wafer, "workbook_data", None) if wafer else None
        if not data or not data.get("shots"):
            # Cleared, not the same wafer: forget it, so reloading the very
            # same wafer afterwards is seen as a change and adopted again.
            self._adopted_sig = None
            return False

        try:
            rows, cols = wafer.shot_layout()
        except Exception:
            rows, cols = 0, 0
        sig = (data.get("path"), data.get("recipe_name"), len(data["shots"]),
               data.get("real_die_count"), data.get("die_size_x"),
               data.get("die_size_y"), rows, cols)
        if sig == self._adopted_sig:
            # Same wafer we already hold. Re-importing would silently discard
            # whatever the user has typed into the grid since.
            return True
        self._adopted_sig = sig

        x_headers, y_headers, rc_of = self._headers_from_shots(data)
        cells = {}
        for s in data["shots"]:
            cells[rc_of(s)] = {
                "device_id": s.get("raw_text") or "/".join(s.get("dies") or []),
                "excluded": not s.get("included", True),
            }
        # Any grid position the wafer does not mention is off-wafer, not a
        # hole in the middle of a table - fill it so the editor shows a
        # rectangle rather than raising on a missing key.
        for r in range(len(y_headers)):
            for c in range(len(x_headers)):
                cells.setdefault((r, c), {"device_id": "", "excluded": True})
        self._major = {"x_headers": x_headers, "y_headers": y_headers,
                       "cells": cells}

        self._selected_rc = None
        self._close_cell_editor(commit=False)
        self._die_size_x_var.set(str(data.get("die_size_x") or ""))
        self._die_size_y_var.set(str(data.get("die_size_y") or ""))
        self._shot_rows_var.set(str(rows))
        self._shot_cols_var.set(str(cols))
        name = data.get("recipe_name")
        if name:
            self.recipe_name_var.set(name)
        # A new wafer means the previous wafer's sub-die touchdowns describe
        # nothing; leaving them would carry one folder's minor sites into the
        # next folder's recipe.
        self._minor_rows = [{"dx": "0", "dy": "0", "suffix": ""}]

        n_shots = len(data["shots"])
        n_dies = self._populate_dielist(data)
        self._status_var.set(
            f"{n_shots} touchdown(s), {rows}x{cols} dies per shot, "
            f"{n_dies} die(s), pitch {data.get('die_size_x')} x "
            f"{data.get('die_size_y')} um — loaded from the Wafer View page.")
        # No try/except around the redraw: this used to call a _redraw() that
        # does not exist, and the swallowed AttributeError left the page
        # showing its 1x1 startup grid for a wafer it had fully loaded.
        self._redraw_grid()
        self._refresh_minor_tree()
        # The shot map has to follow too: it draws rows x cols squares, and a
        # new wafer can change both.
        self._load_die_pins()
        return True

    @staticmethod
    def _headers_from_shots(data: Dict[str, Any]):
        """Grid axes derived from the shot COORDINATES, plus a shot -> (r, c).

        Not from data["row"]/["col"]: the .xls MajorMoves reader numbers rows
        from 1 and columns from 0, so indexing y_headers by a shot's own row
        walked off the end of the list and the whole adopt died on an
        IndexError - which is what left this page showing its 1x1 startup
        grid. Micron positions carry no such convention.
        """
        shots = data["shots"]
        xs = sorted({float(s["x_um"]) for s in shots})
        ys = sorted({float(s["y_um"]) for s in shots})

        def axis(vals, pitch):
            # A uniform pitch keeps positions no shot occupies - an empty
            # column down one side of the wafer - as real grid slots rather
            # than closing the gap and shearing the map.
            pitch = float(pitch or 0)
            if pitch <= 0 or len(vals) < 2:
                return vals
            span = vals[-1] - vals[0]
            n = int(round(span / pitch)) + 1
            if not 0 < n <= 4 * len(vals) + 8:
                return vals
            return [vals[0] + i * pitch for i in range(n)]

        x_headers = axis(xs, data.get("die_size_x"))
        y_headers = axis(ys, data.get("die_size_y"))
        x_index = {round(v, 3): i for i, v in enumerate(x_headers)}
        y_index = {round(v, 3): i for i, v in enumerate(y_headers)}

        def rc_of(shot):
            return (y_index.get(round(float(shot["y_um"]), 3), 0),
                    x_index.get(round(float(shot["x_um"]), 3), 0))

        return x_headers, y_headers, rc_of

    def _populate_dielist(self, data: Dict[str, Any]) -> int:
        """Fill the Die List with every real die on the adopted wafer.

        One row per die, not per touchdown: a shot on this wafer covers
        several dies, and the die is the thing that gets a result. NA slots
        are pad-only positions, so they are left out.

        Every die, not just the probed ones. "included" means "this recipe
        probes it" - the LaMP gauge probes 15 of 634 shots - and listing only
        those meant the one control for choosing what to test could not offer
        the 2376 dies you might want to add. Unprobed dies are greyed instead.
        """
        self._close_dielist_editor(commit=False)
        self._dielist_tree.delete(*self._dielist_tree.get_children())
        self._dielist_tree.tag_configure("unprobed", foreground="#94a3b8")
        _, _, rc_of = self._headers_from_shots(data)
        n = 0
        for shot in data["shots"]:
            dies = real_die_ids(shot)
            if not dies:
                continue
            # The grid's own row/col, so a die's "Shot" reads the same here as
            # the cell readout does when you click it on the map.
            r, c = rc_of(shot)
            where = f"r{r} c{c}"
            tags = () if shot.get("included", True) else ("unprobed",)
            for die in dies:
                self._dielist_tree.insert("", "end", values=(die, where),
                                          tags=tags)
                n += 1
        return n

    def _sync_views(self, folder: str):
        """Push a freshly written map to everything that draws one.

        Three views show this wafer - the Run tab's map, the Wafer View page
        beside this one, and the PMA Process tab's align-site readout - and
        they read it from the file rather than from each other. Writing the
        file without refreshing them leaves the others showing the previous
        wafer, which is exactly how a stale 60-die map survived a LOAD ALL.
        """
        layout = self._main_layout
        try:
            layout._exec2_map_folder = folder
            layout._exec2_map_source_var.set("Electroglas")
            layout._exec2_draw_wafer_map()
        except Exception as exc:
            self._log(f"[WAFER MAP] Map written, but the Run tab did not redraw: "
                      f"{type(exc).__name__}: {exc}")
        wafer = getattr(layout, "pma_wafer", None)
        if wafer is not None:
            # _refresh_view, NOT load_from_ata: the latter calls reset_view,
            # which nulls workbook_data - and workbook_data is what the Run
            # tab derives the whole wafer map from. Reloading here would drop
            # the map back to the recipe's touchdowns, which is the exact bug
            # this tab exists to stop.
            try:
                wafer._refresh_view()
            except Exception as exc:
                self._log(f"[WAFER MAP] Wafer View did not refresh: "
                          f"{type(exc).__name__}: {exc}")
        proc = getattr(layout, "pma_process", None)
        if proc is not None:
            try:
                proc.refresh_align_site()
            except Exception:
                pass

    def _import_xls_template(self):
        self._close_cell_editor(commit=False)
        if not _XLRD:
            messagebox.showerror("xlrd Not Installed",
                                 f"xlrd is not installed ({_XLRD_ERR}) — run:\n"
                                 "    .venv\\Scripts\\pip install xlrd")
            return
        path = filedialog.askopenfilename(
            title="Import Recipe Generator (.xls) as Template",
            filetypes=[("Excel 97-2003 Workbook", "*.xls"), ("All files", "*.*")])
        if not path:
            return
        try:
            book = xlrd.open_workbook(path, formatting_info=True)
            info = read_main_menu_info(book)
            major_grid = read_moves_grid(book, "MajorMoves")
            try:
                minor_grid = read_moves_grid(book, "MinorMoves")
            except Exception:
                minor_grid = None
        except Exception as exc:
            messagebox.showerror("Import Failed", f"Could not read {path}:\n{exc}")
            return

        if not self._confirm_discard_edits():
            return

        self.recipe_name_var.set(info.get("recipe_name") or self.recipe_name_var.get())
        if info.get("die_size_x"):
            self._die_size_x_var.set(info["die_size_x"])
        if info.get("die_size_y"):
            self._die_size_y_var.set(info["die_size_y"])

        self._major = _grid_from_moves(major_grid)
        self._minor_rows = _minor_rows_from_moves(minor_grid) if minor_grid else \
            [{"dx": "0", "dy": "0", "suffix": ""}]
        self._refresh_minor_tree()
        self._selected_rc = None
        self._redraw_grid()

        n_included = sum(1 for c in self._major["cells"].values() if not c.get("excluded"))
        self._status_var.set(f"Imported template from {os.path.basename(path)}: "
                             f"{n_included} included dies.")
        self._log(f"[RECIPE GEN] Imported '{os.path.basename(path)}' as a template — "
                  f"{major_grid['cols']}x{major_grid['rows']} grid, {n_included} "
                  "included dies, main-menu fields and die list layout copied from "
                  "the xls's CURRENT MajorMoves/MinorMoves sheets (generating now "
                  "reflects what's in the sheets today, which may differ from an "
                  "existing separately-shipped .PMA of the same name).")

    # ------------------------------------------------------------------
    def _cell_color(self, cell: Dict[str, Any]) -> str:
        if cell.get("excluded"):
            return _COLOR_EXCLUDED
        if (cell.get("device_id") or "").strip():
            return _COLOR_HAS_ID
        return _COLOR_BLANK

    def _redraw_grid(self):
        if not _MPL:
            return
        self.ax.clear()
        self._selected_patch = None
        x_headers = self._major["x_headers"]
        y_headers = self._major["y_headers"]
        cells = self._major["cells"]
        dx = x_headers[1] - x_headers[0] if len(x_headers) > 1 else 1.0
        dy = y_headers[1] - y_headers[0] if len(y_headers) > 1 else 1.0
        dx = dx or 1.0
        dy = dy or 1.0

        patches, colors = [], []
        for (row, col), cell in cells.items():
            patches.append(Rectangle((x_headers[col], y_headers[row]), dx, dy))
            colors.append(self._cell_color(cell))
        if patches:
            coll = PatchCollection(patches, edgecolor="#0f172a", linewidths=0.4)
            coll.set_facecolor(colors)
            self.ax.add_collection(coll)

        if x_headers and y_headers:
            self.ax.set_xlim(min(x_headers) - dx, max(x_headers) + 2 * dx)
            self.ax.set_ylim(min(y_headers) - dy, max(y_headers) + 2 * dy)
        self.ax.invert_yaxis()
        self.ax.set_title(f"{self.recipe_name_var.get()} — "
                          f"{len(cells)} dies, {sum(1 for c in cells.values() if not c.get('excluded'))} included")
        self.ax.set_xlabel("X (µm)")
        self.ax.set_ylabel("Y (µm)")
        self.ax.set_aspect("equal")

        if self._selected_rc in cells:
            row, col = self._selected_rc
            hl = Rectangle((x_headers[col], y_headers[row]), dx, dy, fill=False,
                          edgecolor=_COLOR_SELECTED, linewidth=2.2, zorder=7)
            self.ax.add_patch(hl)
            self._selected_patch = hl

        self.canvas.draw_idle()

    def _on_scroll_zoom(self, event):
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        self._close_cell_editor(commit=True)
        factor = 0.85 if event.button == "up" else (1 / 0.85)
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        xd, yd = event.xdata, event.ydata
        self.ax.set_xlim(xd - (xd - xlim[0]) * factor, xd + (xlim[1] - xd) * factor)
        self.ax.set_ylim(yd - (yd - ylim[0]) * factor, yd + (ylim[1] - yd) * factor)
        self.canvas.draw_idle()

    def _on_grid_click(self, event):
        if event.xdata is None or event.ydata is None:
            return
        x_headers = self._major["x_headers"]
        y_headers = self._major["y_headers"]
        if not x_headers or not y_headers:
            return
        col = bisect.bisect_right(x_headers, event.xdata) - 1
        row = bisect.bisect_right(y_headers, event.ydata) - 1
        if (row, col) not in self._major["cells"]:
            return
        if event.button == 3:
            self._close_cell_editor(commit=True)
            self._select_cell(row, col)
            self._toggle_exclude()
        else:
            self._select_cell(row, col)
            self._open_cell_editor(row, col)

    def _select_cell(self, row: int, col: int):
        self._selected_rc = (row, col)
        cell = self._major["cells"][(row, col)]
        x = self._major["x_headers"][col]
        y = self._major["y_headers"][row]
        state = "EXCLUDED" if cell.get("excluded") else "included"
        self._selected_var.set(
            f"Row {row}, Col {col}  (X={egpma.fmt_num(x)}, Y={egpma.fmt_num(y)})\n"
            f"Status: {state}")
        self._redraw_grid()

    def _cell_size(self) -> tuple:
        x_headers = self._major["x_headers"]
        y_headers = self._major["y_headers"]
        dx = x_headers[1] - x_headers[0] if len(x_headers) > 1 else 1.0
        dy = y_headers[1] - y_headers[0] if len(y_headers) > 1 else 1.0
        return dx or 1.0, dy or 1.0

    def _open_cell_editor(self, row: int, col: int):
        self._close_cell_editor(commit=True)
        x = self._major["x_headers"][col]
        y = self._major["y_headers"][row]
        dx, dy = self._cell_size()
        (px0, py0), (px1, py1) = self.ax.transData.transform([(x, y), (x + dx, y + dy)])
        canvas_h = self.fig.bbox.height
        left, right = sorted((px0, px1))
        top, bottom = sorted((canvas_h - py0, canvas_h - py1))

        entry = tk.Entry(self.canvas.get_tk_widget(), borderwidth=1,
                         relief="solid", font=("Segoe UI", 9))
        entry.insert(0, self._major["cells"][(row, col)].get("device_id", ""))
        entry.select_range(0, "end")
        entry.place(x=left, y=top, width=max(right - left, 30),
                   height=max(bottom - top, 16))
        entry.focus_set()
        entry.bind("<Return>", lambda _e: self._commit_cell_editor("down"))
        entry.bind("<Shift-Return>", lambda _e: self._commit_cell_editor("up"))
        entry.bind("<Tab>", lambda _e: (self._commit_cell_editor("right"), "break")[1])
        entry.bind("<Shift-Tab>", lambda _e: (self._commit_cell_editor("left"), "break")[1])
        entry.bind("<Escape>", lambda _e: self._close_cell_editor(commit=False))
        entry.bind("<FocusOut>", lambda _e: self._close_cell_editor(commit=True))
        self._cell_editor = entry
        self._cell_editor_rc = (row, col)

    def _close_cell_editor(self, commit: bool):
        entry, rc = self._cell_editor, self._cell_editor_rc
        if entry is None:
            return
        self._cell_editor = None
        self._cell_editor_rc = None
        if commit and rc in self._major["cells"]:
            self._major["cells"][rc]["device_id"] = entry.get().strip()
        try:
            entry.destroy()
        except Exception:
            pass
        if commit:
            self._redraw_grid()

    _MOVE_DELTAS = {"down": (1, 0), "up": (-1, 0), "right": (0, 1), "left": (0, -1)}

    def _commit_cell_editor(self, move: Optional[str] = None):
        if self._cell_editor_rc is None:
            return
        row, col = self._cell_editor_rc
        self._close_cell_editor(commit=True)
        if move not in self._MOVE_DELTAS:
            return
        rows = len(self._major["y_headers"])
        cols = len(self._major["x_headers"])
        dr, dc = self._MOVE_DELTAS[move]
        nrow, ncol = row + dr, col + dc
        if 0 <= nrow < rows and 0 <= ncol < cols:
            self._select_cell(nrow, ncol)
            self._open_cell_editor(nrow, ncol)

    def _toggle_exclude(self):
        if self._cell_editor_rc == self._selected_rc:
            self._close_cell_editor(commit=True)
        if self._selected_rc is None:
            return
        cell = self._major["cells"][self._selected_rc]
        cell["excluded"] = not cell.get("excluded")
        self._select_cell(*self._selected_rc)

    def _set_all_excluded(self, excluded: bool):
        self._close_cell_editor(commit=False)
        for cell in self._major["cells"].values():
            cell["excluded"] = excluded
        self._redraw_grid()
        if self._selected_rc is not None:
            self._select_cell(*self._selected_rc)

    # ------------------------------------------------------------------
    def _dielist_ids(self) -> List[str]:
        """The IDs the pick buttons act on.

        A selection wins when there is one - the list now holds the whole
        wafer, so 'act on every row' would mean 'include everything', which
        is not a pick. With nothing selected it still means the whole list,
        which is what a hand-typed list of a few IDs wants.
        """
        iids = self._dielist_tree.selection() or self._dielist_tree.get_children()
        ids = []
        for iid in iids:
            value = self._dielist_tree.item(iid, "values")[0]
            if str(value).strip():
                ids.append(str(value).strip())
        return ids

    def _add_dielist_row(self):
        self._close_dielist_editor(commit=True)
        iid = self._dielist_tree.insert("", "end", values=("", ""))
        self._open_dielist_editor(iid)

    def _remove_dielist_row(self):
        sel = self._dielist_tree.selection()
        if not sel:
            return
        self._close_dielist_editor(commit=False)
        self._dielist_tree.delete(*sel)

    def _on_dielist_double_click(self, event):
        row_id = self._dielist_tree.identify_row(event.y)
        if row_id:
            self._open_dielist_editor(row_id)

    def _open_dielist_editor(self, iid: str):
        self._close_dielist_editor(commit=True)
        self._dielist_tree.see(iid)
        self._dielist_tree.update_idletasks()
        bbox = self._dielist_tree.bbox(iid, "id")
        if not bbox:
            return
        x, y, w, h = bbox
        value = self._dielist_tree.item(iid, "values")[0]
        entry = tk.Entry(self._dielist_tree, borderwidth=1, relief="solid",
                         font=("Segoe UI", 9))
        entry.insert(0, value)
        entry.select_range(0, "end")
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()
        entry.bind("<Return>", lambda _e: self._commit_dielist_editor(move_next=True))
        entry.bind("<Escape>", lambda _e: self._close_dielist_editor(commit=False))
        entry.bind("<FocusOut>", lambda _e: self._close_dielist_editor(commit=True))
        self._dielist_editor = entry
        self._dielist_editor_iid = iid

    def _close_dielist_editor(self, commit: bool):
        entry, iid = self._dielist_editor, self._dielist_editor_iid
        if entry is None:
            return
        self._dielist_editor = None
        self._dielist_editor_iid = None
        if commit and self._dielist_tree.exists(iid):
            where = (list(self._dielist_tree.item(iid, "values")) + ["", ""])[1]
            self._dielist_tree.item(iid, values=(entry.get().strip(), where))
        try:
            entry.destroy()
        except Exception:
            pass

    def _commit_dielist_editor(self, move_next: bool):
        iid = self._dielist_editor_iid
        self._close_dielist_editor(commit=True)
        if not move_next or iid is None:
            return
        children = self._dielist_tree.get_children()
        idx = children.index(iid) if iid in children else -1
        if 0 <= idx < len(children) - 1:
            self._open_dielist_editor(children[idx + 1])
        else:
            self._add_dielist_row()

    @staticmethod
    def _cell_matches(cell: Dict[str, Any], ids_lower: List[str]) -> bool:
        """Does this touchdown contain any of the wanted dies?

        Whole-die equality first: the list now holds real IDs, and a plain
        substring test makes 'B2' pick up B21..B29. Substring stays as the
        fallback so a hand-typed partial like 'B4-' still works as a filter.
        """
        text = (cell.get("device_id") or "").strip().lower()
        if not text:
            return False
        dies = {d.strip() for d in text.split("/") if d.strip()}
        return bool(dies & set(ids_lower)) or any(i in text for i in ids_lower)

    def _pick_scope(self) -> str:
        return ("the selected" if self._dielist_tree.selection()
                else "every listed")

    def _test_these_devices(self):
        self._close_dielist_editor(commit=True)
        scope = self._pick_scope()
        ids = self._dielist_ids()
        if not ids:
            self._log("[RECIPE GEN] Die list is empty — nothing to test.")
            return
        ids_lower = [i.lower() for i in ids]
        matched = 0
        for cell in self._major["cells"].values():
            hit = self._cell_matches(cell, ids_lower)
            cell["excluded"] = not hit
            matched += hit
        self._redraw_grid()
        self._log(f"[RECIPE GEN] Test These Devices ({scope} die): excluded "
                  f"every touchdown, then re-included the {matched} holding "
                  f"{', '.join(ids[:8])}"
                  f"{f' (+{len(ids) - 8} more)' if len(ids) > 8 else ''}. A "
                  "touchdown covers a whole shot, so its other dies come with it.")

    def _unpick_these_devices(self):
        self._close_dielist_editor(commit=True)
        scope = self._pick_scope()
        ids = self._dielist_ids()
        if not ids:
            self._log("[RECIPE GEN] Die list is empty — nothing to un-pick.")
            return
        ids_lower = [i.lower() for i in ids]
        matched = 0
        for cell in self._major["cells"].values():
            if self._cell_matches(cell, ids_lower):
                cell["excluded"] = True
                matched += 1
        self._redraw_grid()
        self._log(f"[RECIPE GEN] Un-pick These Devices ({scope} die): excluded "
                  f"{matched} touchdown(s) matching {', '.join(ids[:8])}"
                  f"{f' (+{len(ids) - 8} more)' if len(ids) > 8 else ''}.")

    # ------------------------------------------------------------------
    def _refresh_minor_tree(self):
        self._minor_tree.delete(*self._minor_tree.get_children())
        for i, row in enumerate(self._minor_rows):
            self._minor_tree.insert("", "end", iid=str(i),
                                    values=(row["dx"], row["dy"], row["suffix"]))

    def _add_minor_site(self):
        n = len(self._minor_rows)
        self._minor_rows.append({"dx": "0", "dy": "0", "suffix": chr(ord('A') + n) if n < 26 else str(n)})
        self._refresh_minor_tree()

    def _remove_minor_site(self):
        sel = self._minor_tree.selection()
        if not sel or len(self._minor_rows) <= 1:
            return
        idx = int(sel[0])
        del self._minor_rows[idx]
        self._refresh_minor_tree()

    # ------------------------------------------------------------------
    def _pma_source_dir(self) -> str:
        folder = getattr(self._main_layout, "_ata_folder", "")
        return os.path.join(folder, PMA_SOURCE_SUBDIR) if folder else ""

