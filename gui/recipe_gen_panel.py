from __future__ import annotations

import bisect
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Any, Dict, List, Optional

import electroglas_pma as egpma
from pma_process_panel import PMA_SOURCE_SUBDIR
from pma_wafer_panel import read_main_menu_info, read_moves_grid

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

_FREE_FORM_SEED = (
    "Voltage", "Delay1", "Delay2", "Delay3", "Iterations",
    "MeterDelay", "Averages", "NPLC", "MeterCurrentLimit", "MeterRange",
    "PreAlignMessage", "PostAlignMessage", "PictureFile",
)


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
        self._x_move_var = tk.StringVar()
        self._y_move_var = tk.StringVar()
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

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_main_fields()
        self._build_body()

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
        ttk.Button(bar, text="📥 Import Recipe Generator (.xls) as Template…",
                  command=self._import_xls_template).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="💾 Create All Files", command=self._create_all_files).pack(
            side="left", padx=(0, 6))
        ttk.Label(bar, textvariable=self._status_var, foreground="#374151").pack(
            side="left", padx=10)

    def _build_main_fields(self):
        lf = ttk.LabelFrame(self, text="Main Menu Fields", padding=8)
        lf.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 4))
        for i in range(8):
            lf.columnconfigure(i, weight=1)

        fields = (
            ("Die Size X:", self._die_size_x_var),
            ("Die Size Y:", self._die_size_y_var),
            ("X Move First From Align Site:", self._x_move_var),
            ("Y Move First From Align Site:", self._y_move_var),
        )
        for col, (label, var) in enumerate(fields):
            ttk.Label(lf, text=label).grid(row=0, column=col, sticky="w", padx=(0, 4))
            ttk.Entry(lf, textvariable=var, width=12).grid(
                row=1, column=col, sticky="ew", padx=(0, 8))

        ff = ttk.Frame(lf)
        ff.grid(row=2, column=0, columnspan=8, sticky="ew", pady=(10, 0))
        ff.columnconfigure(0, weight=1)

        cols = ("name", "value")
        self._fields_tree = ttk.Treeview(
            ff, columns=cols, show="headings", height=6, selectmode="browse")
        self._fields_tree.heading("name", text="Field")
        self._fields_tree.heading("value", text="Value")
        self._fields_tree.column("name", width=180)
        self._fields_tree.column("value", width=200)
        self._fields_tree.grid(row=0, column=0, columnspan=4, sticky="ew")
        self._fields_tree.bind("<<TreeviewSelect>>", self._on_field_row_selected)
        for name in _FREE_FORM_SEED:
            self._fields_tree.insert("", "end", iid=name, values=(name, ""))

        ttk.Label(ff, text="Name:").grid(row=1, column=0, sticky="e", pady=(6, 0))
        self._field_name_var = tk.StringVar()
        ttk.Entry(ff, textvariable=self._field_name_var, width=22).grid(
            row=1, column=1, sticky="w", pady=(6, 0), padx=(4, 12))
        ttk.Label(ff, text="Value:").grid(row=1, column=2, sticky="e", pady=(6, 0))
        self._field_value_var = tk.StringVar()
        ttk.Entry(ff, textvariable=self._field_value_var, width=22).grid(
            row=1, column=3, sticky="w", pady=(6, 0), padx=(4, 0))
        btn_row = ttk.Frame(ff)
        btn_row.grid(row=2, column=0, columnspan=4, sticky="w", pady=(4, 0))
        ttk.Button(btn_row, text="Set", command=self._set_field_row).pack(side="left")
        ttk.Button(btn_row, text="Remove", command=self._remove_field_row).pack(
            side="left", padx=(4, 0))

    def _on_field_row_selected(self, _evt=None):
        sel = self._fields_tree.selection()
        if not sel:
            return
        name, value = self._fields_tree.item(sel[0], "values")
        self._field_name_var.set(name)
        self._field_value_var.set(value)

    def _set_field_row(self):
        name = self._field_name_var.get().strip()
        if not name:
            return
        value = self._field_value_var.get()
        if self._fields_tree.exists(name):
            self._fields_tree.item(name, values=(name, value))
        else:
            self._fields_tree.insert("", "end", iid=name, values=(name, value))

    def _remove_field_row(self):
        sel = self._fields_tree.selection()
        if not sel:
            return
        self._fields_tree.delete(*sel)
        self._field_name_var.set("")
        self._field_value_var.set("")

    def _free_form_fields(self) -> Dict[str, str]:
        out = {}
        for iid in self._fields_tree.get_children():
            name, value = self._fields_tree.item(iid, "values")
            if str(value).strip():
                out[name] = value
        return out

    # ------------------------------------------------------------------
    def _build_body(self):
        split = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        split.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))

        left = ttk.Frame(split)
        split.add(left, weight=3)
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
            die_lf, columns=("id",), show="headings", height=8, selectmode="browse")
        self._dielist_tree.heading("id", text="Device ID")
        self._dielist_tree.column("id", width=160)
        self._dielist_tree.grid(row=0, column=0, sticky="nsew")
        dsb = ttk.Scrollbar(die_lf, orient="vertical", command=self._dielist_tree.yview)
        self._dielist_tree.configure(yscrollcommand=dsb.set)
        dsb.grid(row=0, column=1, sticky="ns")
        self._dielist_tree.bind("<Double-1>", self._on_dielist_double_click)
        ttk.Label(die_lf, text="Double-click a row (or ＋ Add) to type a "
                 "device ID; Enter commits and adds the next row.",
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
        if info.get("x_move_first"):
            self._x_move_var.set(info["x_move_first"])
        if info.get("y_move_first"):
            self._y_move_var.set(info["y_move_first"])
        for name, value in info.get("params", {}).items():
            if self._fields_tree.exists(name):
                self._fields_tree.item(name, values=(name, value))
            else:
                self._fields_tree.insert("", "end", iid=name, values=(name, value))

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
        ids = []
        for iid in self._dielist_tree.get_children():
            (value,) = self._dielist_tree.item(iid, "values")
            if str(value).strip():
                ids.append(str(value).strip())
        return ids

    def _add_dielist_row(self):
        self._close_dielist_editor(commit=True)
        iid = self._dielist_tree.insert("", "end", values=("",))
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
        (value,) = self._dielist_tree.item(iid, "values")
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
            self._dielist_tree.item(iid, values=(entry.get().strip(),))
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

    def _test_these_devices(self):
        self._close_dielist_editor(commit=True)
        ids = self._dielist_ids()
        if not ids:
            self._log("[RECIPE GEN] Die list is empty — nothing to test.")
            return
        ids_lower = [i.lower() for i in ids]
        for cell in self._major["cells"].values():
            cell["excluded"] = True
        matched = 0
        for cell in self._major["cells"].values():
            text = (cell.get("device_id") or "").lower()
            if text and any(i in text for i in ids_lower):
                cell["excluded"] = False
                matched += 1
        self._redraw_grid()
        self._log(f"[RECIPE GEN] Test These Devices: excluded all dies, then "
                  f"re-included {matched} matching {', '.join(ids)}.")

    def _unpick_these_devices(self):
        self._close_dielist_editor(commit=True)
        ids = self._dielist_ids()
        if not ids:
            self._log("[RECIPE GEN] Die list is empty — nothing to un-pick.")
            return
        ids_lower = [i.lower() for i in ids]
        matched = 0
        for cell in self._major["cells"].values():
            text = (cell.get("device_id") or "").lower()
            if text and any(i in text for i in ids_lower):
                cell["excluded"] = True
                matched += 1
        self._redraw_grid()
        self._log(f"[RECIPE GEN] Un-pick These Devices: excluded {matched} "
                  f"die(s) matching {', '.join(ids)}.")

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

    def _create_all_files(self):
        self._close_cell_editor(commit=True)
        self._close_dielist_editor(commit=True)
        name = self.recipe_name_var.get().strip()
        if not name:
            messagebox.showerror("Missing Recipe Name", "Enter a recipe name first.")
            return
        safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
        if not safe_name:
            messagebox.showerror("Invalid Recipe Name",
                                 "Use letters, digits, space, - or _.")
            return
        dest_dir = self._pma_source_dir()
        if not dest_dir:
            messagebox.showerror("No ATA Folder",
                                 "Load an ATA folder first — recipe files are saved "
                                 f"into its {PMA_SOURCE_SUBDIR}\\ subfolder.")
            return
        if not any(not c.get("excluded") for c in self._major["cells"].values()):
            if not messagebox.askyesno(
                "No Included Dies",
                "Every die on the grid is currently excluded — the generated "
                "recipe would have zero touchdowns. Continue anyway?"
            ):
                return
        if not messagebox.askyesno(
            "Create All Files",
            f"Create all the recipe files for '{safe_name}'? Existing files "
            "with the same name will be overwritten. Are you sure?"
        ):
            return

        main_fields = {
            "DieSizeX": self._die_size_x_var.get().strip(),
            "DieSizeY": self._die_size_y_var.get().strip(),
            "XMoveFirstFromAlignSite": self._x_move_var.get().strip(),
            "YMoveFirstFromAlignSite": self._y_move_var.get().strip(),
        }
        main_fields.update(self._free_form_fields())

        minor_sites = [{"dx": _to_float(r["dx"]), "dy": _to_float(r["dy"]),
                       "suffix": r["suffix"].strip()} for r in self._minor_rows]

        try:
            pma_path = egpma.write_recipe_files(dest_dir, safe_name, main_fields,
                                               self._major, minor_sites)
        except OSError as exc:
            messagebox.showerror("Write Failed", str(exc))
            return

        n_major = sum(1 for c in self._major["cells"].values() if not c.get("excluded"))
        self._status_var.set(f"Created {os.path.basename(pma_path)} "
                             f"({n_major} dies x {len(minor_sites)} site(s))")
        self._log(f"[RECIPE GEN] Created all recipe files for '{safe_name}' in "
                  f"{PMA_SOURCE_SUBDIR}\\ — {n_major} die(s), {len(minor_sites)} "
                  "minor site(s) each.")

        pma_process = getattr(self._main_layout, "pma_process", None)
        if pma_process is not None:
            pma_process._refresh_pickers()
            pma_process._pma_picker_var.set(os.path.basename(pma_path))
            pma_process.load_path(pma_path)
