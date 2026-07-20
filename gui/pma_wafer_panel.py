from __future__ import annotations

import bisect
import csv
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

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
    _MPL = True
except ImportError:
    _MPL = False



_MAIN_MENU_PARAMS_FIRST_ROW1 = 35
_MAIN_MENU_PARAMS_LAST_ROW1 = 300


def _cell_value(sheet, row0: int, col0: int):
    if row0 < 0 or row0 >= sheet.nrows or col0 >= sheet.row_len(row0):
        return ""
    return sheet.cell_value(row0, col0)


def _fmt_float(v: float) -> str:
    if float(v).is_integer():
        return str(int(v))
    return f"{v:.10f}".rstrip("0").rstrip(".")


def _cell_text(sheet, row0: int, col0: int) -> str:
    v = _cell_value(sheet, row0, col0)
    if v == "" or v is None:
        return ""
    if isinstance(v, float):
        return _fmt_float(v)
    return str(v).strip()


def _positive_float(s: str) -> Optional[float]:
    try:
        v = float(s)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def _grid_pitch(headers: List[float]) -> Optional[float]:
    for i in range(1, len(headers)):
        d = abs(headers[i] - headers[i - 1])
        if d > 0:
            return d
    return None


def _resolve_named_cell(book, name: str):
    objs = book.name_map.get(name.lower())
    if not objs:
        return None
    try:
        ref = objs[0].result.value[0]
        return ref.rowxlo, ref.colxlo
    except Exception:
        return None


def _named_text(book, name: str, default: str = "") -> str:
    hit = _resolve_named_cell(book, name)
    if not hit:
        return default
    row0, col0 = hit
    try:
        sheet = book.sheet_by_name("MainMenu")
    except Exception:
        return default
    return _cell_text(sheet, row0, col0) or default


def _find_label_right(sheet, label: str) -> str:
    label_l = label.strip().lower()
    for row0 in range(sheet.nrows):
        for col0 in range(sheet.row_len(row0) - 1):
            if _cell_text(sheet, row0, col0).strip().lower() == label_l:
                return _cell_text(sheet, row0, col0 + 1)
    return ""


def read_main_menu_info(book) -> Dict[str, Any]:
    sheet = book.sheet_by_name("MainMenu")

    params: Dict[str, str] = {}
    for row1 in range(_MAIN_MENU_PARAMS_FIRST_ROW1, _MAIN_MENU_PARAMS_LAST_ROW1 + 1):
        row0 = row1 - 1
        name = _cell_text(sheet, row0, 1)
        if not name:
            break
        value = _cell_text(sheet, row0, 2)
        params[name.replace(" ", "")] = value

    return {
        "recipe_name": _named_text(book, "RecipeName"),
        "die_size_x": _named_text(book, "DieSizeX"),
        "die_size_y": _named_text(book, "DieSizeY"),
        "x_move_first": _named_text(book, "XMoveFirstFromAlignSite"),
        "y_move_first": _named_text(book, "YMoveFirstFromAlignSite"),
        "align_die": _find_label_right(sheet, "align die"),
        "params": params,
    }


def _pad7(n: int) -> str:
    return str(n).zfill(7)


def _is_near_white(rgb, threshold: int = 245) -> bool:
    return all(c >= threshold for c in rgb)


def _is_cell_excluded(book, sheet, row0: int, col0: int) -> bool:
    xfx = sheet.cell_xf_index(row0, col0)
    bg = book.xf_list[xfx].background
    if bg.fill_pattern == 0:
        return False
    rgb = book.colour_map.get(bg.pattern_colour_index)
    if rgb is not None and _is_near_white(rgb):
        return False
    return True


def read_moves_grid(book, sheet_name: str = "MajorMoves") -> Dict[str, Any]:
    sheet = book.sheet_by_name(sheet_name)

    last_y_row0 = 1
    while _cell_text(sheet, last_y_row0, 0):
        last_y_row0 += 1
    last_x_col0 = 1
    while _cell_text(sheet, 0, last_x_col0):
        last_x_col0 += 1

    x_headers = [float(_cell_value(sheet, 0, c) or 0) for c in range(1, last_x_col0)]
    y_headers = [float(_cell_value(sheet, r, 0) or 0) for r in range(1, last_y_row0)]

    shots: List[Dict[str, Any]] = []
    auto_id = 1
    for ri, row0 in enumerate(range(1, last_y_row0)):
        for ci, col0 in enumerate(range(1, last_x_col0)):
            excluded = _is_cell_excluded(book, sheet, row0, col0)
            shot: Dict[str, Any] = {
                "row": ri, "col": ci,
                "x_um": x_headers[ci], "y_um": y_headers[ri],
                "included": not excluded,
                "raw_text": "", "dies": [],
            }
            if not excluded:
                text = _cell_text(sheet, row0, col0)
                shot["raw_text"] = text
                if text:
                    shot["dies"] = [t.strip() for t in text.split("/")]
                else:
                    shot["dies"] = [_pad7(auto_id)]
                    auto_id += 1
            shots.append(shot)

    return {
        "x_headers": x_headers, "y_headers": y_headers,
        "rows": len(y_headers), "cols": len(x_headers),
        "shots": shots,
    }


def real_die_ids(shot: Dict[str, Any]) -> List[str]:
    return [d for d in shot["dies"] if d.strip().upper() != "NA"]


def parse_legacy_workbook(path: str) -> Dict[str, Any]:
    if not _XLRD:
        raise RuntimeError(f"xlrd is not installed ({_XLRD_ERR}) — run: pip install xlrd")
    book = xlrd.open_workbook(path, formatting_info=True)
    info = read_main_menu_info(book)
    grid = read_moves_grid(book, "MajorMoves")

    shots = grid["shots"]
    included = [s for s in shots if s["included"]]
    real_count = sum(len(real_die_ids(s)) for s in included)
    na_count = sum(len(s["dies"]) - len(real_die_ids(s)) for s in included)

    die_size_x = info["die_size_x"] if _positive_float(info["die_size_x"]) else ""
    die_size_y = info["die_size_y"] if _positive_float(info["die_size_y"]) else ""
    if not die_size_x:
        pitch = _grid_pitch(grid["x_headers"])
        if pitch:
            die_size_x = _fmt_float(pitch)
    if not die_size_y:
        pitch = _grid_pitch(grid["y_headers"])
        if pitch:
            die_size_y = _fmt_float(pitch)

    return {
        "path": path,
        **info,
        "die_size_x": die_size_x, "die_size_y": die_size_y,
        "x_headers": grid["x_headers"], "y_headers": grid["y_headers"],
        "rows": grid["rows"], "cols": grid["cols"],
        "shots": shots,
        "shot_count": len(shots),
        "included_shot_count": len(included),
        "excluded_shot_count": len(shots) - len(included),
        "real_die_count": real_count,
        "na_die_count": na_count,
    }


ATA_PMA_FILENAME = "ata_wafer_map_pma.csv"
_ATA_PMA_META_FIELDS = ("recipe_name", "die_size_x", "die_size_y",
                        "x_move_first", "y_move_first", "align_die")


def save_workbook_to_ata(data: Dict[str, Any], folder: str) -> str:
    path = os.path.join(folder, ATA_PMA_FILENAME)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([*_ATA_PMA_META_FIELDS, "row", "col", "x_um", "y_um",
                   "die1", "die2", "die3", "die4"])
        for s in data.get("shots", []):
            if not s["included"]:
                continue
            dies = (s["dies"] + ["", "", "", ""])[:4]
            w.writerow([data.get(k, "") for k in _ATA_PMA_META_FIELDS]
                      + [s["row"], s["col"], s["x_um"], s["y_um"], *dies])
    return path


def load_workbook_from_ata(folder: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(folder, ATA_PMA_FILENAME)
    if not os.path.exists(path):
        return None
    shots = []
    meta = {k: "" for k in _ATA_PMA_META_FIELDS}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            for k in _ATA_PMA_META_FIELDS:
                if row.get(k):
                    meta[k] = row[k]
            try:
                r, c = int(row["row"]), int(row["col"])
                x_um, y_um = float(row["x_um"]), float(row["y_um"])
            except (KeyError, ValueError):
                continue
            dies = [row.get(f"die{i}", "") for i in range(1, 5)]
            dies = [d for d in dies if d != ""]
            shots.append({"row": r, "col": c, "x_um": x_um, "y_um": y_um,
                          "included": True, "raw_text": "/".join(dies), "dies": dies})
    if not shots:
        return None
    real_count = sum(len(real_die_ids(s)) for s in shots)
    na_count = sum(len(s["dies"]) - len(real_die_ids(s)) for s in shots)
    x_headers = sorted({s["x_um"] for s in shots})
    y_headers = sorted({s["y_um"] for s in shots})
    return {
        "path": path,
        **meta,
        "x_headers": x_headers, "y_headers": y_headers,
        "rows": len({s["row"] for s in shots}), "cols": len({s["col"] for s in shots}),
        "shots": shots,
        "shot_count": len(shots),
        "included_shot_count": len(shots),
        "excluded_shot_count": 0,
        "real_die_count": real_count,
        "na_die_count": na_count,
    }



def pma_shots_to_grid(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        die_x = float(data.get("die_size_x") or 0)
        die_y = float(data.get("die_size_y") or 0)
        move_x = float(data.get("x_move_first") or 0)
        move_y = float(data.get("y_move_first") or 0)
    except (TypeError, ValueError):
        return []
    if not die_x or not die_y:
        return []

    out = []
    for s in data.get("shots", []):
        if not s.get("included"):
            continue
        dies = real_die_ids(s)
        if not dies:
            continue
        align_x = move_x + s["x_um"]
        align_y = move_y + s["y_um"]
        out.append({"row": round(align_y / die_y), "col": round(align_x / die_x),
                    "die_ids": dies, "raw_text": s.get("raw_text", "")})
    return out


def merge_with_accretech(pma_grid: List[Dict[str, Any]], accretech_rc,
                         row_offset: int = 0, col_offset: int = 0) -> List[Dict[str, Any]]:
    accretech_rc = set(accretech_rc)
    merged: Dict[tuple, Dict[str, Any]] = {}
    for p in pma_grid:
        rc = (p["row"] + row_offset, p["col"] + col_offset)
        if rc not in accretech_rc:
            continue
        entry = merged.setdefault(rc, {"row": rc[0], "col": rc[1], "die_ids": [],
                                       "raw_text": ""})
        entry["die_ids"].extend(p["die_ids"])
        entry["raw_text"] = p["raw_text"]
    return sorted(merged.values(), key=lambda d: (d["row"], d["col"]))


def align_die_ids(data: Dict[str, Any]) -> List[str]:
    raw = (data.get("align_die") or "").strip()
    if not raw:
        return []
    return [t.strip() for t in raw.split("/") if t.strip()]


def find_align_shots(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    ids = set(align_die_ids(data))
    if not ids:
        return []
    return [s for s in data.get("shots", [])
           if s.get("included") and ids & set(s.get("dies", []))]


def centroid_offset(pma_grid: List[Dict[str, Any]], accretech_rc) -> tuple:
    accretech_rc = list(accretech_rc)
    if not pma_grid or not accretech_rc:
        return 0, 0
    pma_row_c = sum(p["row"] for p in pma_grid) / len(pma_grid)
    pma_col_c = sum(p["col"] for p in pma_grid) / len(pma_grid)
    acc_row_c = sum(rc[0] for rc in accretech_rc) / len(accretech_rc)
    acc_col_c = sum(rc[1] for rc in accretech_rc) / len(accretech_rc)
    return round(acc_row_c - pma_row_c), round(acc_col_c - pma_col_c)



_COLOR_EXCLUDED = "#374151"
_COLOR_FULL     = "#16a34a"
_COLOR_PARTIAL  = "#d97706"
_COLOR_EMPTY    = "#dc2626"
_COLOR_SELECTED = "#38bdf8"


class PmaWaferPanel(ttk.Frame):
    def __init__(self, parent, controller, get_folder=None):
        super().__init__(parent)
        self.controller = controller
        self._get_folder = get_folder or (lambda: None)
        self.workbook_data: Optional[Dict[str, Any]] = None
        self._loaded_ata_folder: Optional[str] = None
        self.path_var = tk.StringVar(value="No workbook loaded.")
        self.summary_var = tk.StringVar(value="")
        self.selected_var = tk.StringVar(value="Click a shot on the map to see its dies.")
        self._selected_patch = None

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self._build_controls()
        self._build_body()

    def _log(self, msg: str):
        try:
            self.controller.log(msg)
        except Exception:
            pass


    def _build_controls(self):
        ctl = ttk.Frame(self, padding=6)
        ctl.grid(row=0, column=0, sticky="ew")
        ttk.Button(ctl, text="💾 Save to ATA Folder",
                   command=self._save_to_ata).pack(side="left", padx=(6, 0))
        ttk.Label(ctl, textvariable=self.path_var, foreground="gray").pack(
            side="left", padx=10)

        if not _XLRD:
            ttk.Label(
                self,
                text=("xlrd is not installed — run:\n"
                      "    .venv\\Scripts\\pip install xlrd\n\n"
                      f"({_XLRD_ERR})"),
                font=("Consolas", 10), justify="left", foreground="red",
            ).grid(row=1, column=0, pady=40, padx=20, sticky="w")
            self.rowconfigure(1, weight=0)

    def _build_body(self):
        if not _XLRD:
            return
        body = ttk.PanedWindow(self, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew")

        left = ttk.Frame(body)
        body.add(left, weight=3)
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        if _MPL:
            self.fig = Figure(figsize=(7, 6), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=left)
            toolbar = NavigationToolbar2Tk(self.canvas, left, pack_toolbar=False)
            toolbar.grid(row=1, column=0, sticky="ew")
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            self.canvas.mpl_connect("button_press_event", self._on_map_click)
            self._draw_empty()
        else:
            ttk.Label(left, text="matplotlib not installed — install it to view "
                                 "the wafer/shot map.", foreground="red").grid(
                row=0, column=0, sticky="w", padx=10, pady=10)

        right = ttk.Frame(body, padding=6)
        body.add(right, weight=2)
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, textvariable=self.summary_var, justify="left",
                  font=("Consolas", 9)).grid(row=0, column=0, sticky="w")

        legend = ttk.Frame(right)
        legend.grid(row=1, column=0, sticky="w", pady=(8, 4))
        self._legend_labels: Dict[str, ttk.Label] = {}
        for key, color, text in [
            ("full", _COLOR_FULL, "full"),
            ("partial", _COLOR_PARTIAL, "partial"),
            ("empty", _COLOR_EMPTY, "none"),
            ("excluded", _COLOR_EXCLUDED, "excluded"),
        ]:
            sw = tk.Canvas(legend, width=12, height=12, highlightthickness=0)
            sw.create_rectangle(0, 0, 12, 12, fill=color, outline="")
            sw.pack(side="left", padx=(0, 3))
            lbl = ttk.Label(legend, text=text)
            lbl.pack(side="left", padx=(0, 10))
            self._legend_labels[key] = lbl

        ttk.Label(right, text="Selected shot:", font=("Segoe UI", 9, "bold")).grid(
            row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(right, textvariable=self.selected_var, justify="left",
                  wraplength=280).grid(row=3, column=0, sticky="nw", pady=(2, 8))

        tf = ttk.Frame(right)
        tf.grid(row=4, column=0, sticky="nsew")
        right.rowconfigure(4, weight=2)
        cols = ("row", "col", "x_um", "y_um", "dies")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", height=12)
        heads = [("row", "Row", 40), ("col", "Col", 40), ("x_um", "X (µm)", 70),
                 ("y_um", "Y (µm)", 70), ("dies", "Dies", 160)]
        for cid, text, width in heads:
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=width, anchor="w")
        ysb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        ttk.Button(right, text="Export Shots to CSV…", command=self._export_csv).grid(
            row=5, column=0, sticky="w", pady=(6, 0))


    def open_workbook_dialog(self):
        path = filedialog.askopenfilename(
            title="Open Recipe Generator (.xls)",
            filetypes=[("Excel 97-2003 Workbook", "*.xls"), ("All files", "*.*")],
        )
        if not path:
            return
        self.load_workbook_path(path)

    def load_workbook_path(self, path: str):
        self.path_var.set(f"Loading {os.path.basename(path)} …")
        self._log(f"[PMA] Opening legacy recipe workbook {path}")
        threading.Thread(target=self._load_worker, args=(path,), daemon=True).start()

    def _load_worker(self, path: str):
        try:
            data = parse_legacy_workbook(path)
            self._loaded_ata_folder = None
            self.after(0, lambda: self._after_load(data))
        except Exception as exc:
            self.after(0, lambda e=exc: self._load_failed(e))

    def _load_failed(self, exc: Exception):
        self.path_var.set("Load failed.")
        messagebox.showerror("Could not load workbook", str(exc))
        self._log(f"[PMA] Load failed: {exc}")

    def _save_to_ata(self):
        if not self.workbook_data:
            messagebox.showinfo("No Data", "Open a legacy recipe workbook first.")
            return
        folder = self._get_folder()
        if not folder:
            messagebox.showerror(
                "No ATA Folder",
                "No ATA folder is loaded — use 📁 Load ATA Folder on the\n"
                "top toolbar first, then Save to ATA Folder here.")
            return
        path = os.path.join(folder, ATA_PMA_FILENAME)
        if os.path.exists(path) and not messagebox.askyesno(
            "Overwrite Wafer Map",
            f"{path}\nalready exists — overwrite it with the currently "
            f"loaded workbook's {self.workbook_data['included_shot_count']} shot(s)?"
        ):
            return
        save_workbook_to_ata(self.workbook_data, folder)
        self._loaded_ata_folder = folder
        self._log(f"[PMA] Saved {self.workbook_data['included_shot_count']} shot(s) → {path}")

    def load_from_ata(self, folder: str):
        if not folder:
            return
        data = load_workbook_from_ata(folder)
        if data is None:
            return
        self._loaded_ata_folder = folder
        self._after_load(data)
        self._log(f"[PMA] Restored '{data['recipe_name']}' from {ATA_PMA_FILENAME}")

    def show_touchdowns(self, data: Dict[str, Any]):
        self.path_var.set(f"{data['path']}  (from PMA Process)")
        align_line = self._align_summary_line(data)
        self.summary_var.set(
            f"Recipe: {data['recipe_name'] or '(unnamed)'}\n"
            f"Die size: {data['die_size_x']} x {data['die_size_y']} um\n"
            f"Align offset: ({data['x_move_first']}, {data['y_move_first']}) um\n"
            f"{align_line}"
            f"Grid: {data['rows']} rows x {data['cols']} cols\n"
            f"Shots on map: {data['included_shot_count']}\n"
            f"Real dies: {data['real_die_count']}"
        )
        self._populate_tree(data)
        self._update_legend(data)
        if _MPL:
            self._draw_map(data)
        self._log(
            f"[PMA] Wafer map merged from PMA Process: {data['included_shot_count']} "
            f"shot(s), {data['real_die_count']} die(s) on the map."
        )

    def _align_summary_line(self, data: Dict[str, Any]) -> str:
        ids = align_die_ids(data)
        if not ids:
            return ""
        return f"Align die: {'/'.join(ids)}  (marked ★ on map)\n"

    def _after_load(self, data: Dict[str, Any]):
        self.workbook_data = data
        self.path_var.set(data["path"])
        align_line = self._align_summary_line(data)
        self.summary_var.set(
            f"Recipe: {data['recipe_name'] or '(unnamed)'}\n"
            f"Die size: {data['die_size_x']} x {data['die_size_y']} um\n"
            f"Align offset: ({data['x_move_first']}, {data['y_move_first']}) um\n"
            f"{align_line}"
            f"Grid: {data['rows']} rows x {data['cols']} cols\n"
            f"Shots on map: {data['included_shot_count']} "
            f"(excluded: {data['excluded_shot_count']})\n"
            f"Real dies: {data['real_die_count']}  (NA slots skipped: {data['na_die_count']})"
        )
        self._populate_tree(data)
        self._update_legend(data)
        if _MPL:
            self._draw_map(data)
        self._log(
            f"[PMA] Loaded '{data['recipe_name']}': {data['included_shot_count']} shots, "
            f"{data['real_die_count']} real dies on the map."
        )

    def _update_legend(self, data: Dict[str, Any]):
        width = max((len(s["dies"]) for s in data["shots"] if s["included"]), default=0)
        n = width or 1
        self._legend_labels["full"].config(text=f"{n}/{n} dies (full)")

    def _populate_tree(self, data: Dict[str, Any]):
        self.tree.delete(*self.tree.get_children())
        for s in data["shots"]:
            if not s["included"]:
                continue
            iid = f"{s['row']}:{s['col']}"
            self.tree.insert("", tk.END, iid=iid, values=(
                s["row"], s["col"], f"{s['x_um']:.0f}", f"{s['y_um']:.0f}",
                "/".join(s["dies"]),
            ))


    def _draw_empty(self):
        self.ax.clear()
        self.ax.set_title("Wafer Map")
        self.ax.set_xlabel("X (µm)")
        self.ax.set_ylabel("Y (µm)")
        self.canvas.draw_idle()

    def _shot_color(self, shot: Dict[str, Any]) -> str:
        if not shot["included"]:
            return _COLOR_EXCLUDED
        n_real = len(real_die_ids(shot))
        if n_real == len(shot["dies"]) and n_real > 0:
            return _COLOR_FULL
        if n_real == 0:
            return _COLOR_EMPTY
        return _COLOR_PARTIAL

    def _draw_map(self, data: Dict[str, Any]):
        self.ax.clear()
        dx = float(data["die_size_x"] or 1) or 1.0
        dy = float(data["die_size_y"] or 1) or 1.0
        self._patches_by_rc: Dict[tuple, Rectangle] = {}
        for s in data["shots"]:
            rect = Rectangle((s["x_um"], s["y_um"]), dx, dy,
                              facecolor=self._shot_color(s),
                              edgecolor="#0f172a", linewidth=0.3)
            self.ax.add_patch(rect)
            self._patches_by_rc[(s["row"], s["col"])] = rect
        for s in find_align_shots(data):
            cx, cy = s["x_um"] + dx / 2, s["y_um"] + dy / 2
            self.ax.plot(cx, cy, marker="*", markersize=14, color="#facc15",
                        markeredgecolor="#78350f", markeredgewidth=1.0, zorder=5)
        x_headers, y_headers = data["x_headers"], data["y_headers"]
        if x_headers and y_headers:
            self.ax.set_xlim(min(x_headers) - dx, max(x_headers) + 2 * dx)
            self.ax.set_ylim(min(y_headers) - dy, max(y_headers) + 2 * dy)
        self.ax.invert_yaxis()
        self.ax.set_title(f"{data['recipe_name']} — {data['included_shot_count']} shots, "
                          f"{data['real_die_count']} dies")
        self.ax.set_xlabel("X (µm)")
        self.ax.set_ylabel("Y (µm)")
        self.ax.set_aspect("equal")
        self.canvas.draw_idle()

    def _on_map_click(self, event):
        if not self.workbook_data or event.xdata is None or event.ydata is None:
            return
        x_headers = self.workbook_data["x_headers"]
        y_headers = self.workbook_data["y_headers"]
        col = bisect.bisect_right(x_headers, event.xdata) - 1
        row = bisect.bisect_right(y_headers, event.ydata) - 1
        if not (0 <= row < len(y_headers) and 0 <= col < len(x_headers)):
            return
        shot = next((s for s in self.workbook_data["shots"]
                    if s["row"] == row and s["col"] == col), None)
        if shot:
            self._select_shot(shot)

    def _on_tree_select(self, _event=None):
        sel = self.tree.selection()
        if not sel or not self.workbook_data:
            return
        row, col = (int(x) for x in sel[0].split(":"))
        shot = next((s for s in self.workbook_data["shots"]
                    if s["row"] == row and s["col"] == col), None)
        if shot:
            self._select_shot(shot, from_tree=True)

    def _select_shot(self, shot: Dict[str, Any], from_tree: bool = False):
        if _MPL and self._selected_patch is not None:
            self._selected_patch.set_edgecolor("#0f172a")
            self._selected_patch.set_linewidth(0.3)
        if _MPL:
            patch = self._patches_by_rc.get((shot["row"], shot["col"]))
            if patch is not None:
                patch.set_edgecolor(_COLOR_SELECTED)
                patch.set_linewidth(2.0)
                self._selected_patch = patch
                self.canvas.draw_idle()
        if shot["included"]:
            align_ids = set(align_die_ids(self.workbook_data or {}))
            is_align = bool(align_ids & set(shot["dies"]))
            tag = "  ★ ALIGN DIE" if is_align else ""
            lines = [f"Row {shot['row']}, Col {shot['col']}  —  "
                    f"X={shot['x_um']:.0f} µm, Y={shot['y_um']:.0f} µm{tag}", ""]
            for i, d in enumerate(shot["dies"]):
                mark = "NA (skipped)" if d.strip().upper() == "NA" else d
                lines.append(f"  Die {i + 1}: {mark}")
        else:
            lines = [f"Row {shot['row']}, Col {shot['col']}  —  excluded (not on map)"]
        self.selected_var.set("\n".join(lines))
        if not from_tree:
            iid = f"{shot['row']}:{shot['col']}"
            if self.tree.exists(iid):
                self.tree.selection_set(iid)
                self.tree.see(iid)


    def _export_csv(self):
        if not self.workbook_data:
            messagebox.showinfo("No data", "Load a legacy recipe workbook first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Shots CSV", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["row", "col", "x_um", "y_um", "included",
                       "die1", "die2", "die3", "die4"])
            for s in self.workbook_data["shots"]:
                dies = (s["dies"] + ["", "", "", ""])[:4]
                w.writerow([s["row"], s["col"], s["x_um"], s["y_um"],
                           s["included"], *dies])
        self._log(f"[PMA] Exported shots to {path}")
        messagebox.showinfo("Exported", f"Shots exported to:\n{path}")
