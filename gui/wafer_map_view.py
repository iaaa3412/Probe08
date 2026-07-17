import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import csv
import math
import os

from recipe_panel import recipes_to_rows, rows_to_recipes, STEP_FIELDS

CARD_CSV_FIELDS = ["kind", "recipe", "pin", "pad", "net", "seq"] + list(STEP_FIELDS)


def _bind_zoom_only(canvas):
    canvas.configure(scrollregion=(-20000, -20000, 20000, 20000))

    def _zoom(cx, cy, factor):
        canvas.scale("all", cx, cy, factor, factor)
        bb = canvas.bbox("all")
        if bb:
            pad = 500
            canvas.configure(scrollregion=(
                min(bb[0] - pad, -20000), min(bb[1] - pad, -20000),
                max(bb[2] + pad,  20000), max(bb[3] + pad,  20000),
            ))

    canvas.bind("<MouseWheel>", lambda e: _zoom(e.x, e.y, 1.15 if e.delta > 0 else 1 / 1.15))
    canvas.bind("<Button-4>",   lambda e: _zoom(e.x, e.y, 1.15))
    canvas.bind("<Button-5>",   lambda e: _zoom(e.x, e.y, 1 / 1.15))


def _pz_bind(canvas, on_reset):
    canvas.bind("<ButtonPress-1>",   lambda e: canvas.scan_mark(e.x, e.y))
    canvas.bind("<B1-Motion>",       lambda e: canvas.scan_dragto(e.x, e.y, gain=1))
    canvas.bind("<Double-Button-1>", lambda _: on_reset())
    _bind_zoom_only(canvas)


ATA_KEY_FILES = {
    "ata_wafer_map.csv":           ("Die map & coordinates (GDS-derived)", "shared"),
    "ata_wafer_map_accretech.csv": ("Die map & coordinates (real prober extraction)", "accretech"),
    "ata_wafer_map_pma.csv":       ("Die/shot map (PMA workbook extraction)", "shared"),
    "ata_wafer_map_merged.csv":    ("Accretech + PMA merged map (multi-die-per-shot)", "accretech"),
    "ata_metadata.csv":         ("Wafer / lot metadata", "shared"),
    "ata_sites.csv":            ("Probe sites", "shared"),
    "ata_pad_layout.csv":       ("Pad geometry", "shared"),
    "reference_pad_layout.csv": ("Hand-drawn pad layout sketch (Pad to Probe -> Custom; not used by recipes/wiring)", "shared"),
    "ata_alignment_marks.csv":  ("Alignment marks", "shared"),
    "alignment_marks.csv":      ("Alignment marks (alt)", "shared"),
    "ata_devices.csv":          ("Device definitions", "shared"),
    "ata_die_markers.csv":      ("Die-level markers", "shared"),
    "ata_test_structures.csv":  ("Test structures", "shared"),
    "ata_test_plan":            ("Test plan", "shared"),
    "ata_validation_report.csv":("Validation report", "shared"),
    "ata_export_formats.json":  ("Results tab SQL/CSV export format definitions", "accretech"),
    "ata_export_formats_electroglas.json": ("Results tab SQL/CSV export format definitions", "electroglas"),
}

WAFER_MAP_SOURCES = {
    "GDS":       "ata_wafer_map.csv",
    "Accretech": "ata_wafer_map_accretech.csv",
}


class WaferMapPanel(ttk.LabelFrame):
    _PICK_COLOR = "#f59e0b"

    def __init__(self, parent):
        super().__init__(parent, text="Wafer Map")
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        self.dies = {}
        self._last_dies = None
        self.canvas.create_text(150, 100, text="Waiting for Wafer Map...", fill="gray")
        _pz_bind(self.canvas, self._reset_view)

        self._picked = set()
        self._picking_enabled = False
        self._pick_max = None
        self._on_pick_change = None
        self._press_xy = None
        self.canvas.bind("<ButtonPress-1>", self._on_pick_press, add="+")
        self.canvas.bind("<ButtonRelease-1>", self._on_pick_release, add="+")

    def enable_picking(self, max_picks=None, on_change=None):
        self._on_pick_change = on_change
        if max_picks == 0:
            self._picking_enabled = False
            self.clear_picks()
            return
        self._picking_enabled = True
        self._pick_max = max_picks

    def get_picked(self):
        return sorted(self._picked)

    def set_picked(self, rc_list):
        self._picked = set(rc_list)
        self._recolor_picks()

    def clear_picks(self):
        self._picked.clear()
        self._recolor_picks()

    def _recolor_picks(self):
        for rc, item in self.dies.items():
            try:
                self.canvas.itemconfig(
                    item, fill=(self._PICK_COLOR if rc in self._picked else "#7aaec8"))
            except tk.TclError:
                pass

    def _on_pick_press(self, e):
        self._press_xy = (e.x, e.y)

    def _on_pick_release(self, e):
        press = self._press_xy
        self._press_xy = None
        if not self._picking_enabled or press is None:
            return
        dx, dy = e.x - press[0], e.y - press[1]
        if dx * dx + dy * dy > 16:
            return
        hit = self.canvas.find_closest(e.x, e.y)
        if not hit:
            return
        rc = next((k for k, v in self.dies.items() if v == hit[0]), None)
        if rc is None:
            return
        if rc in self._picked:
            self._picked.discard(rc)
        elif self._pick_max is None or len(self._picked) < self._pick_max:
            self._picked.add(rc)
        else:
            return
        self._recolor_picks()
        if self._on_pick_change:
            self._on_pick_change(self.get_picked())

    def _reset_view(self):
        if self._last_dies is not None:
            self._draw_from_die_list(self._last_dies)
        else:
            self.draw_map()

    def draw_map(self):
        self.canvas.delete("all")
        self.dies.clear()
        self.update_idletasks()
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 50:
            width, height = 300, 300

        cx, cy = width / 2, height / 2
        radius = min(width, height) / 2.2
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="black", width=2)
        self.canvas.create_text(cx, cy - radius + 10, text="Notch", font=("Arial", 8))

        die_size, grid_size = 20, 12
        start_x = cx - (grid_size * die_size) / 2
        start_y = cy - (grid_size * die_size) / 2

        for row in range(grid_size):
            for col in range(grid_size):
                x1 = start_x + col * die_size
                y1 = start_y + row * die_size
                if (x1 - cx) ** 2 + (y1 - cy) ** 2 < (radius - 20) ** 2:
                    rect = self.canvas.create_rectangle(
                        x1, y1, x1 + die_size - 2, y1 + die_size - 2,
                        fill="#e0e0e0", outline="gray"
                    )
                    self.dies[(row, col)] = rect

    def load_from_ata(self, folder_path, filename="ata_wafer_map.csv"):
        map_file = os.path.join(folder_path, filename)
        if not os.path.exists(map_file):
            self.canvas.delete("all")
            self.dies.clear()
            self.canvas.create_text(
                150, 80, text=f"{filename} not found\nin selected folder.",
                fill="red", justify="center"
            )
            self.config(text="Wafer Map")
            return 0

        raw = []
        with open(map_file, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw.append({k.lower().strip(): v.strip() for k, v in row.items()})

        if not raw:
            return 0

        dies = self._parse_die_list(raw)
        self._last_dies = dies
        self._draw_from_die_list(dies)
        self.config(text=f"Wafer Map — {len(self.dies)} dies")
        return len(self.dies)

    def _parse_die_list(self, raw):
        sample = raw[0]
        row_key = next((k for k in ("row", "die_row", "y_index", "die_y_idx") if k in sample), None)
        col_key = next((k for k in ("col", "column", "die_col", "x_index", "die_x_idx") if k in sample), None)
        x_key   = next((k for k in ("x_um", "x_mm", "x", "die_x", "center_x", "origin_x") if k in sample), None)
        y_key   = next((k for k in ("y_um", "y_mm", "y", "die_y", "center_y", "origin_y") if k in sample), None)
        en_key  = next((k for k in ("enabled", "active", "include", "in_spec", "test_enabled") if k in sample), None)

        dies = []
        for r in raw:
            if en_key:
                val = r[en_key].lower()
                if val in ("0", "false", "no", "n", "skip"):
                    continue

            x_um = y_um = row = col = None
            if x_key and y_key:
                try:
                    x_um = float(r[x_key])
                    y_um = float(r[y_key])
                except (ValueError, KeyError):
                    pass
            if row_key and col_key:
                try:
                    rv, cv = r[row_key].strip(), r[col_key].strip()
                    if rv and cv:
                        row = int(float(rv))
                        col = int(float(cv))
                except (ValueError, KeyError):
                    pass
            if x_um is None and row is None:
                continue
            dies.append({"x_um": x_um, "y_um": y_um, "row": row, "col": col})

        if dies and dies[0]["row"] is None:
            xs = sorted(set(round(d["x_um"]) for d in dies))
            ys = sorted(set(round(d["y_um"]) for d in dies))
            x_to_col = {x: i for i, x in enumerate(xs)}
            y_to_row = {y: i for i, y in enumerate(ys)}
            for d in dies:
                d["row"] = y_to_row[round(d["y_um"])]
                d["col"] = x_to_col[round(d["x_um"])]

        if dies and dies[0]["x_um"] is None:
            for d in dies:
                d["x_um"] = float(d["col"])
                d["y_um"] = -float(d["row"])

        return [d for d in dies if d["row"] is not None and d["x_um"] is not None]

    def _draw_from_die_list(self, dies):
        self.canvas.delete("all")
        self.dies.clear()

        if not dies:
            self.canvas.create_text(150, 100, text="No dies found in wafer map.", fill="red")
            return

        self.update_idletasks()
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W < 50:
            W, H = 400, 400

        xs = [d["x_um"] for d in dies]
        ys = [d["y_um"] for d in dies]

        cx_d = (max(xs) + min(xs)) / 2.0
        cy_d = (max(ys) + min(ys)) / 2.0

        def _min_pitch(vals):
            uniq = sorted(set(round(v) for v in vals))
            gaps = [abs(uniq[i+1] - uniq[i]) for i in range(len(uniq) - 1)
                    if uniq[i+1] != uniq[i]]
            return min(gaps) if gaps else (max(vals) - min(vals)) or 1.0

        pitch_x = _min_pitch(xs)
        pitch_y = _min_pitch(ys)

        max_dist = max(math.hypot(x - cx_d, y - cy_d) for x, y in zip(xs, ys))
        wafer_r_d = max_dist + max(pitch_x, pitch_y) * 0.7

        margin = 28
        scale = min((W - 2 * margin) / (2 * wafer_r_d),
                    (H - 2 * margin) / (2 * wafer_r_d))

        def to_cx(xd): return W / 2 + (xd - cx_d) * scale
        def to_cy(yd): return H / 2 - (yd - cy_d) * scale

        ccx, ccy = W / 2, H / 2
        cr = wafer_r_d * scale

        self.canvas.create_oval(
            ccx - cr, ccy - cr, ccx + cr, ccy + cr,
            fill="#f5f5f0", outline="#333", width=2
        )

        ee = cr * 0.95
        self.canvas.create_oval(
            ccx - ee, ccy - ee, ccx + ee, ccy + ee,
            outline="#aaa", width=1, dash=(4, 4)
        )

        ns = max(5, cr * 0.04)
        ny = ccy + cr
        self.canvas.create_arc(
            ccx - ns, ny - ns, ccx + ns, ny + ns,
            start=0, extent=180, fill="#333", outline=""
        )

        arm = max(5, cr * 0.03)
        self.canvas.create_line(ccx - arm, ccy, ccx + arm, ccy, fill="#ccc", dash=(2, 2))
        self.canvas.create_line(ccx, ccy - arm, ccx, ccy + arm, fill="#ccc", dash=(2, 2))

        dw = max(2, min(pitch_x * scale * 0.85, 26))
        dh = max(2, min(pitch_y * scale * 0.85, 26))
        ol = "#4a7090" if dw > 5 else ""
        for d in dies:
            cx_ = to_cx(d["x_um"])
            cy_ = to_cy(d["y_um"])
            rect = self.canvas.create_rectangle(
                cx_ - dw / 2, cy_ - dh / 2,
                cx_ + dw / 2, cy_ + dh / 2,
                fill="#7aaec8", outline=ol
            )
            self.dies[(d["row"], d["col"])] = rect
        self._recolor_picks()

    def update_die(self, row, col, status):
        colors = {
            "UNTESTED":     "#7aaec8",
            "CURRENT":      "#dbeafe",
            "CONTACT":      "#ede9fe",
            "TESTING":      "#dbeafe",
            "PASS":         "#00d200",
            "FAIL":         "#e53935",
            "SKIP":         "#fbbc04",
            "CONTACT_FAIL": "#fb923c",
        }
        if (row, col) in self.dies:
            self.canvas.itemconfig(self.dies[(row, col)], fill=colors.get(status, "#9ca3af"))


def _safe_card_filename(name: str) -> str:
    return "".join(c for c in name.strip() if c.isalnum() or c in " _-").strip() or "card"


class ProbeCardWiringFrame(ttk.LabelFrame):

    def __init__(self, parent, get_folder=None, log_fn=None, on_card_change=None,
                 on_pins_change=None, system: str = "accretech"):
        self._system = system
        super().__init__(parent, text=self._title())
        self._get_folder = get_folder or (lambda: None)
        self._log = log_fn or (lambda _msg: None)
        self._on_card_change = on_card_change or (lambda _name: None)
        self._on_pins_change = on_pins_change or (lambda: None)

        self._cards: dict = {}
        self._current: str = ""
        self._card_recipes: dict = {}
        self._card_src: dict = {}
        self._ata_card_names: set = set()
        self._ata_probe_cards_dir: str = ""
        self._rows: list = []

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_card_bar()

        cols = ("pin", "pad", "net")
        self._tree = ttk.Treeview(self, columns=cols, show="headings",
                                  height=7, selectmode="browse")
        for cid, text, width, anch in (("pin", "Pin", 45, "center"),
                                       ("pad", "Pad", 80, "w"),
                                       ("net", "Net", 90, "w")):
            self._tree.heading(cid, text=text)
            self._tree.column(cid, width=width, anchor=anch)
        self._tree.grid(row=1, column=0, sticky="nsew", padx=(4, 0), pady=(2, 0))
        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        vsb.grid(row=1, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.bind("<<TreeviewSelect>>", lambda _e: self._row_to_editor())

        ed = ttk.Frame(self)
        ed.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 0))
        self._pin_var = tk.StringVar()
        self._pad_var = tk.StringVar()
        self._net_var = tk.StringVar()
        ttk.Label(ed, text="Pin").pack(side="left")
        ttk.Entry(ed, textvariable=self._pin_var, width=4).pack(side="left", padx=(1, 4))
        ttk.Label(ed, text="Pad").pack(side="left")
        ttk.Entry(ed, textvariable=self._pad_var, width=7).pack(side="left", padx=(1, 4))
        ttk.Label(ed, text="Net").pack(side="left")
        ttk.Entry(ed, textvariable=self._net_var, width=8).pack(side="left", padx=(1, 4))

        btns = ttk.Frame(self)
        btns.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 4))
        ttk.Button(btns, text="＋ Add / Update", command=self._add_update).pack(
            side="left", padx=(0, 2))
        ttk.Button(btns, text="🗑 Remove", command=self._remove).pack(side="left", padx=2)
        ttk.Button(btns, text="💾 Save All", command=self._save).pack(side="right")
        ttk.Button(btns, text="📂 Load .csv…", command=self._load_clicked).pack(
            side="right", padx=(0, 2))


    def _title(self) -> str:
        return f"Probe Card Wiring ({self._system.capitalize()})"

    def _build_card_bar(self):
        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 0))
        ttk.Label(bar, text="Probe Card:").pack(side="left")
        self._picker_var = tk.StringVar()
        self._picker = ttk.Combobox(bar, textvariable=self._picker_var,
                                    state="readonly", width=14)
        self._picker.pack(side="left", padx=(2, 4))
        self._picker.bind("<<ComboboxSelected>>", lambda _e: self._switch_card())
        ttk.Button(bar, text="＋New", width=6, command=self._new_card).pack(side="left", padx=1)
        ttk.Button(bar, text="✎ Rename", width=9, command=self._rename_card).pack(
            side="left", padx=1)
        ttk.Button(bar, text="🗑 Delete", width=8, command=self._delete_card).pack(
            side="left", padx=1)

    def get_active_card(self) -> str:
        return self._current

    def get_card_names(self) -> list:
        return list(self._cards.keys())

    def _refresh_card_picker(self):
        names = list(self._cards.keys())
        self._picker.config(values=names)
        self._picker_var.set(self._current)
        self.config(text=f"{self._title()} — '{self._current}'"
                    if self._current else f"{self._title()} — no card")

    def _switch_card(self):
        name = self._picker_var.get()
        if name == self._current or name not in self._cards:
            return
        self._current = name
        self._rows = self._cards[name]
        self._refresh()
        self._refresh_card_picker()
        self._log(f"[WIRING] Active probe card: {name}")
        self._on_card_change(name)

    def _new_card(self):
        folder = self._get_folder()
        if not folder:
            messagebox.showerror(
                "No ATA Folder",
                "Load an ATA folder first — new probe cards are created as\n"
                ".csv files inside its probe_cards\\ subfolder.")
            return
        name = simpledialog.askstring("New Probe Card", "Probe card name (= file name):",
                                      parent=self)
        if not name:
            return
        name = _safe_card_filename(name)
        if not name:
            messagebox.showerror("Invalid Name", "Use letters, digits, space, - or _.")
            return
        if name in self._cards:
            messagebox.showerror("Duplicate", f"Probe card '{name}' already exists.")
            return
        cards_dir = os.path.join(folder, "probe_cards")
        path = os.path.join(cards_dir, f"{name}.csv")
        if os.path.exists(path):
            messagebox.showerror("File Exists", f"{path}\nalready exists.")
            return
        try:
            os.makedirs(cards_dir, exist_ok=True)
            self._write_card_file(path, [], {})
        except OSError as exc:
            messagebox.showerror("Create Failed", str(exc))
            return
        self._cards[name] = []
        self._card_recipes[name] = {}
        self._card_src[name] = path
        self._ata_card_names.add(name)
        self._ata_probe_cards_dir = cards_dir
        self._current = name
        self._rows = self._cards[name]
        self._refresh()
        self._refresh_card_picker()
        self._log(f"[WIRING] Created probe card '{name}' → {path}")
        self._on_card_change(name)

    def _rename_card(self):
        if not self._current:
            messagebox.showerror("No Probe Card", "No probe card is active.")
            return
        old_name = self._current
        new_name = simpledialog.askstring(
            "Rename Probe Card", "New name:",
            initialvalue=old_name, parent=self)
        if not new_name:
            return
        new_name = _safe_card_filename(new_name)
        if not new_name or new_name == old_name:
            return
        if new_name in self._cards:
            messagebox.showerror("Duplicate", f"Probe card '{new_name}' already exists.")
            return

        old_path = self._card_src.get(old_name)
        folder = self._get_folder()
        cards_dir = self._ata_probe_cards_dir or \
            (os.path.join(folder, "probe_cards") if folder else "")
        new_path = os.path.join(cards_dir, f"{new_name}.csv") if cards_dir else None

        self._cards[new_name] = self._cards.pop(old_name)
        self._card_recipes[new_name] = self._card_recipes.pop(old_name, {})
        self._card_src.pop(old_name, None)
        if old_name in self._ata_card_names:
            self._ata_card_names.discard(old_name)
            self._ata_card_names.add(new_name)

        if new_path:
            try:
                os.makedirs(cards_dir, exist_ok=True)
                recipes_for_main = (self._card_recipes[new_name]
                                    if self._system == "accretech"
                                    else self._read_main_file_recipes(old_path))
                self._write_card_file(new_path, self._cards[new_name], recipes_for_main)
                self._card_src[new_name] = new_path
                if self._system != "accretech":
                    self._write_side_recipes(new_path, self._card_recipes[new_name])
                    if old_path:
                        old_side = self._recipe_side_path(old_path)
                        if os.path.isfile(old_side) and os.path.normcase(old_side) != \
                                os.path.normcase(self._recipe_side_path(new_path)):
                            os.remove(old_side)
                if old_path and os.path.exists(old_path) and \
                        os.path.normcase(old_path) != os.path.normcase(new_path):
                    os.remove(old_path)
                self._log(f"[WIRING] Renamed probe card '{old_name}' → '{new_name}'")
            except OSError as exc:
                self._log(f"[WIRING] Rename failed: {exc}")

        self._current = new_name
        self._rows = self._cards[new_name]
        self._refresh()
        self._refresh_card_picker()
        self._on_card_change(new_name)

    def _delete_card(self):
        if not self._current:
            return
        if len(self._cards) <= 1 and not messagebox.askyesno(
                "Delete Probe Card",
                f"Delete probe card '{self._current}'? This removes the "
                "last probe card — no recipes will be selectable until a "
                "new one is created."):
            return
        elif len(self._cards) > 1 and not messagebox.askyesno(
                "Delete Probe Card", f"Delete probe card '{self._current}'?"):
            return
        name = self._current
        path = self._card_src.get(name, "")
        del self._cards[name]
        self._card_recipes.pop(name, None)
        self._card_src.pop(name, None)
        self._ata_card_names.discard(name)
        if path:
            try:
                os.remove(path)
                self._log(f"[WIRING] Deleted {path}")
            except OSError as exc:
                self._log(f"[WIRING] File delete error: {exc}")
            base = path[:-4] if path.lower().endswith(".csv") else path
            card_dir = os.path.dirname(path)
            if os.path.isdir(card_dir):
                prefix = os.path.basename(base) + ".recipes."
                for fname in os.listdir(card_dir):
                    if fname.lower().startswith(prefix.lower()) and fname.lower().endswith(".csv"):
                        try:
                            os.remove(os.path.join(card_dir, fname))
                        except OSError:
                            pass
        self._current = next(iter(self._cards), "")
        self._rows = self._cards.get(self._current, [])
        self._refresh()
        self._refresh_card_picker()
        self._on_card_change(self._current)


    def _row_to_editor(self):
        sel = self._tree.selection()
        if not sel:
            return
        idx = self._tree.index(sel[0])
        if 0 <= idx < len(self._rows):
            r = self._rows[idx]
            self._pin_var.set(r["pin"])
            self._pad_var.set(r["pad"])
            self._net_var.set(r["net"])

    def _add_update(self):
        if not self._current:
            messagebox.showerror("No Probe Card", "Create a probe card first (＋New).")
            return
        pin = self._pin_var.get().strip()
        if not pin:
            return
        row = {"pin": pin,
               "pad": self._pad_var.get().strip(),
               "net": self._net_var.get().strip()}
        for i, r in enumerate(self._rows):
            if r["pin"] == pin:
                self._rows[i] = row
                break
        else:
            self._rows.append(row)
        self._rows.sort(key=lambda r: (len(r["pin"]), r["pin"]))
        self._refresh()

    def _remove(self):
        sel = self._tree.selection()
        if not sel:
            return
        idx = self._tree.index(sel[0])
        if 0 <= idx < len(self._rows):
            del self._rows[idx]
            self._refresh()

    def _refresh(self):
        self._tree.delete(*self._tree.get_children())
        for r in self._rows:
            self._tree.insert("", "end", values=(r["pin"], r["pad"], r["net"]))
        self._on_pins_change()


    def _load_clicked(self):
        path = filedialog.askopenfilename(
            title="Load Probe Card .csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        rows = self._read_csv(path)
        if rows is None:
            return
        name = _safe_card_filename(os.path.splitext(os.path.basename(path))[0])
        unique, n = name, 2
        while unique in self._cards:
            unique = f"{name} ({n})"
            n += 1
        self._cards[unique] = rows
        self._card_recipes[unique] = {}
        self._card_src[unique] = path
        self._current = unique
        self._rows = self._cards[unique]
        self._refresh()
        self._refresh_card_picker()
        self._log(f"[WIRING] Loaded '{unique}' ({len(rows)} pin(s)) from {path}")
        self._on_card_change(unique)

    def _read_csv(self, path: str):
        rows = []
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                for raw in csv.DictReader(f):
                    row = {k.lower().strip(): (v or "").strip()
                           for k, v in raw.items() if k}
                    pin = next((row[k] for k in
                                ("pin", "probe_pin", "card_pin", "channel", "pin_no")
                                if row.get(k)), "")
                    if not pin:
                        continue
                    rows.append({
                        "pin": pin,
                        "pad": next((row[k] for k in
                                     ("pad", "pad_name", "name", "label")
                                     if row.get(k)), ""),
                        "net": next((row[k] for k in
                                     ("net", "net_name", "signal")
                                     if row.get(k)), ""),
                    })
        except OSError as exc:
            self._log(f"[WIRING] Error reading {os.path.basename(path)}: {exc}")
            return None
        return rows

    def _read_card_file(self, path: str):
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                rows = [{k.lower().strip(): (v or "").strip()
                         for k, v in raw.items() if k}
                        for raw in csv.DictReader(f)]
        except OSError as exc:
            self._log(f"[WIRING] Error reading {os.path.basename(path)}: {exc}")
            return None, None
        pins = []
        for row in rows:
            if (row.get("kind") or "PIN").upper() != "PIN":
                continue
            pin = row.get("pin", "")
            if not pin:
                continue
            pins.append({"pin": pin, "pad": row.get("pad", ""), "net": row.get("net", "")})
        recipes = rows_to_recipes(rows)
        return pins, recipes

    def _write_card_file(self, path: str, pins: list, recipes: dict):
        rows = [{"kind": "PIN", "pin": r["pin"], "pad": r["pad"], "net": r["net"]}
                for r in pins]
        rows.extend(recipes_to_rows(recipes))
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=CARD_CSV_FIELDS, restval="")
            wr.writeheader()
            wr.writerows(rows)

    def _recipe_side_path(self, main_path: str) -> str:
        base = main_path[:-4] if main_path.lower().endswith(".csv") else main_path
        return f"{base}.recipes.{self._system}.csv"

    def _read_main_file_recipes(self, path: str) -> dict:
        if not path or not os.path.isfile(path):
            return {}
        _, recipes = self._read_card_file(path)
        return recipes or {}

    def _read_side_recipes(self, main_path: str) -> dict:
        side = self._recipe_side_path(main_path)
        if not os.path.isfile(side):
            return {}
        _, recipes = self._read_card_file(side)
        return recipes or {}

    def _write_side_recipes(self, main_path: str, recipes: dict):
        self._write_card_file(self._recipe_side_path(main_path), [], recipes)

    def load_from_ata(self, folder: str) -> int:
        cards_dir = os.path.join(folder, "probe_cards")
        self._ata_probe_cards_dir = cards_dir
        found, found_src, found_recipes = {}, {}, {}
        if os.path.isdir(cards_dir):
            for fname in sorted(os.listdir(cards_dir)):
                if not fname.lower().endswith(".csv"):
                    continue
                if ".recipes." in fname.lower():
                    continue
                path = os.path.join(cards_dir, fname)
                if not os.path.isfile(path):
                    continue
                pins, main_recipes = self._read_card_file(path)
                if pins is None:
                    continue
                name = os.path.splitext(fname)[0]
                found[name] = pins
                found_src[name] = path
                found_recipes[name] = (main_recipes if self._system == "accretech"
                                       else self._read_side_recipes(path))

        stale = [name for name in self._ata_card_names if name not in found]
        for name in stale:
            self._cards.pop(name, None)
            self._card_src.pop(name, None)
            self._card_recipes.pop(name, None)
        self._ata_card_names = set(found)

        self._cards.update(found)
        self._card_src.update(found_src)
        self._card_recipes.update(found_recipes)

        if self._current not in self._cards:
            self._current = next(iter(self._cards), "")
        self._rows = self._cards.get(self._current, [])
        self._refresh()
        self._refresh_card_picker()

        msg = f"[WIRING] {len(found)} probe card(s) from {cards_dir}: {', '.join(found)}" \
              if found else f"[WIRING] No probe cards found in {cards_dir}"
        if stale:
            msg += f" — removed {len(stale)} no longer on disk: {', '.join(stale)}"
        self._log(msg)
        self._on_card_change(self._current)
        return len(found)

    def _save(self):
        folder = self._get_folder()
        if not folder:
            self._log("[WIRING] No ATA folder loaded — load one first.")
            return
        if not self._cards:
            return
        target_dir = self._ata_probe_cards_dir or os.path.join(folder, "probe_cards")
        try:
            os.makedirs(target_dir, exist_ok=True)
        except OSError as exc:
            self._log(f"[WIRING] Could not create probe_cards\\ subfolder: {exc}")
            return
        saved = []
        for name, rows in self._cards.items():
            path = self._card_src.get(name) or os.path.join(
                target_dir, f"{_safe_card_filename(name)}.csv")
            self._card_src[name] = path
            try:
                recipes_for_main = (self._card_recipes.get(name, {})
                                    if self._system == "accretech"
                                    else self._read_main_file_recipes(path))
                self._write_card_file(path, rows, recipes_for_main)
                saved.append(path)
            except OSError as exc:
                self._log(f"[WIRING] Save error for '{name}': {exc}")
        self._log(f"[WIRING] Saved {len(saved)} probe card(s) (wiring + recipes), "
                  "one file each")


    def get_recipes(self) -> dict:
        return {name: {"steps": [dict(s) for s in rec.get("steps", [])]}
                for name, rec in self._card_recipes.get(self._current, {}).items()}

    def get_recipe_count(self, card: str) -> int:
        return len(self._card_recipes.get(card, {}))

    def save_recipes(self, card: str, recipes: dict) -> bool:
        if card not in self._cards:
            return False
        self._card_recipes[card] = {
            name: {"steps": [dict(s) for s in rec.get("steps", [])]}
            for name, rec in recipes.items()}
        path = self._card_src.get(card)
        if not path:
            folder = self._get_folder()
            if not folder:
                return False
            cards_dir = self._ata_probe_cards_dir or os.path.join(folder, "probe_cards")
            path = os.path.join(cards_dir, f"{_safe_card_filename(card)}.csv")
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if self._system == "accretech":
                self._write_card_file(path, self._cards.get(card, []), self._card_recipes[card])
            else:
                if not os.path.isfile(path):
                    self._write_card_file(path, self._cards.get(card, []), {})
                self._write_side_recipes(path, self._card_recipes[card])
        except OSError as exc:
            self._log(f"[WIRING] Save error for probe card '{card}' recipes: {exc}")
            return False
        self._card_src[card] = path
        return True


    def get_wiring(self) -> list:
        return [dict(r) for r in self._rows]

    def get_pin_choices(self) -> list:
        choices = []
        for r in self._rows:
            value = f"{r['pin']}:{r['pad']}" if r["pad"] else r["pin"]
            label = f"pin {r['pin']}"
            if r["pad"]:
                label += f" — {r['pad']}"
            if r["net"]:
                label += f" ({r['net']})"
            choices.append((value, label))
        return choices


class PadLayoutPanel(ttk.LabelFrame):
    CUSTOM_FILENAME = "reference_pad_layout.csv"

    _PAD_W, _PAD_H = 32, 20
    _PIN_LENGTH = _PAD_W * 2

    def __init__(self, parent, on_custom_change=None, get_pins=None):
        super().__init__(parent, text="Pad Layout")
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        self._last_pads = None
        self.canvas.create_text(100, 100, text="Awaiting Layout...", fill="gray")
        _pz_bind(self.canvas, self._reset_view)

        self._source = "ata"
        self._on_custom_change = on_custom_change
        self._get_pins = get_pins
        self._custom_pads = []
        self._pad_items = {}
        self._custom_dies = []
        self._die_items = {}
        self._drag_index = None
        self._die_drag_index = None
        self._die_drag_pad_indices = []
        self._die_resize_index = None
        self._drag_press_xy = None
        self._pan_press_xy = None
        self._pin_offsets = {}
        self._pin_items = {}
        self._pin_tips = {}
        self._pins_by_pad = {}
        self._pin_drag_key = None

    def _reset_view(self):
        if self._last_pads is not None:
            self._draw_from_pads(self._last_pads)
        else:
            self.draw_pads()

    def set_source(self, source: str):
        self._source = source
        if source == "custom":
            self.canvas.bind("<ButtonPress-1>", self._on_edit_press)
            self.canvas.bind("<B1-Motion>", self._on_edit_motion)
            self.canvas.bind("<ButtonRelease-1>", self._on_edit_release)
            self.canvas.bind("<Double-Button-1>", self._on_edit_double_click)
            self.canvas.bind("<Button-3>", self._on_edit_right_click)
            _bind_zoom_only(self.canvas)
            self._draw_custom()
        else:
            _pz_bind(self.canvas, self._reset_view)
            self.canvas.bind("<Button-3>", lambda _e: None)
            self._reset_view()

    def load_custom(self, folder_path):
        path = os.path.join(folder_path, self.CUSTOM_FILENAME)
        self._custom_pads = []
        self._custom_dies = []
        self._pin_offsets = {}
        if os.path.exists(path):
            with open(path, newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    kind = (row.get("kind") or "pad").strip().lower()
                    try:
                        if kind == "die":
                            self._custom_dies.append({
                                "name": row.get("pad_name", ""),
                                "x1": float(row["x1"]), "y1": float(row["y1"]),
                                "x2": float(row["x2"]), "y2": float(row["y2"]),
                            })
                        elif kind == "pin":
                            self._pin_offsets[row.get("pad_name", "")] = \
                                (float(row["x"]), float(row["y"]))
                        else:
                            self._custom_pads.append({
                                "name": row.get("pad_name", ""),
                                "x": float(row["x"]), "y": float(row["y"]),
                            })
                    except (KeyError, ValueError):
                        continue
        if self._source == "custom":
            self._draw_custom()
        self._notify_change()
        return len(self._custom_pads)

    def save_custom(self, folder_path):
        os.makedirs(folder_path, exist_ok=True)
        path = os.path.join(folder_path, self.CUSTOM_FILENAME)
        fields = ["kind", "pad_name", "x", "y", "x1", "y1", "x2", "y2"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for pad in self._custom_pads:
                writer.writerow({"kind": "pad", "pad_name": pad["name"],
                                 "x": pad["x"], "y": pad["y"]})
            for die in self._custom_dies:
                writer.writerow({"kind": "die", "pad_name": die["name"],
                                 "x1": die["x1"], "y1": die["y1"],
                                 "x2": die["x2"], "y2": die["y2"]})
            for key, (dx, dy) in self._pin_offsets.items():
                writer.writerow({"kind": "pin", "pad_name": key, "x": dx, "y": dy})
        return path

    def clear_custom(self):
        self._custom_pads = []
        self._custom_dies = []
        self._pin_offsets = {}
        if self._source == "custom":
            self._draw_custom()
        self._notify_change()

    def add_die(self, name=None):
        if name is None:
            name = simpledialog.askstring(
                "New Die", "Die label:", initialvalue=f"Die{len(self._custom_dies) + 1}",
                parent=self)
            if not name:
                return
        self.canvas.update_idletasks()
        w, h = max(self.canvas.winfo_width(), 300), max(self.canvas.winfo_height(), 300)
        cx = self.canvas.canvasx(w / 2)
        cy = self.canvas.canvasy(h / 2)
        dw, dh = 160, 110
        self._custom_dies.append({
            "name": name, "x1": cx - dw / 2, "y1": cy - dh / 2,
            "x2": cx + dw / 2, "y2": cy + dh / 2,
        })
        self._draw_custom()
        self._notify_change()

    def _draw_custom(self):
        self.canvas.delete("all")
        self._die_items = {}
        self._pad_items = {}
        self._pin_items = {}
        self._pin_tips = {}
        self._pins_by_pad = {}

        for idx, die in enumerate(self._custom_dies):
            x1, y1, x2, y2 = die["x1"], die["y1"], die["x2"], die["y2"]
            rect_id = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline="#4444cc", width=2, dash=(5, 3))
            text_id = self.canvas.create_text(
                x1 + 4, y1 + 10, text=die["name"], anchor="w",
                font=("Arial", 8, "bold"), fill="#4444cc")
            handle_id = self.canvas.create_rectangle(
                x2 - 4, y2 - 4, x2 + 4, y2 + 4, fill="#4444cc", outline="")
            self._die_items[idx] = (rect_id, text_id, handle_id)

        half_w, half_h = self._PAD_W / 2, self._PAD_H / 2
        for idx, pad in enumerate(self._custom_pads):
            x, y = pad["x"], pad["y"]
            rect_id = self.canvas.create_rectangle(
                x - half_w, y - half_h, x + half_w, y + half_h,
                fill="gold", outline="#888", width=1)
            text_id = self.canvas.create_text(x, y, text=pad["name"], font=("Arial", 7), fill="#333")
            self._pad_items[idx] = (rect_id, text_id)

        self._draw_pins()

        if not self._custom_pads and not self._custom_dies:
            self.canvas.create_text(
                150, 80, text="Custom layout — click anywhere to add a pad, or "
                             "▭ Add Die to draw a containing rectangle.\n"
                             "Drag to move, double-click to rename, "
                             "right-click to delete.",
                fill="gray", justify="center")
        n_dies = len(self._custom_dies)
        die_txt = f", {n_dies} die(s)" if n_dies else ""
        self.config(text=f"Pad Layout (custom) — {len(self._custom_pads)} pad(s){die_txt}")

    _PIN_MIN_LEN = 12.0

    def _clamp_pin_tail(self, cx, cy, tip_x, tip_y):
        dx, dy = cx - tip_x, cy - tip_y
        length = math.hypot(dx, dy)
        if length < self._PIN_MIN_LEN:
            if length == 0:
                return tip_x, tip_y - self._PIN_MIN_LEN
            scale = self._PIN_MIN_LEN / length
            return tip_x + dx * scale, tip_y + dy * scale
        return cx, cy

    def _draw_pins(self):
        if not self._get_pins:
            return
        try:
            pins = self._get_pins()
        except Exception:
            return
        if not pins:
            return
        pad_by_name = {p["name"]: p for p in self._custom_pads}
        for pin in pins:
            pin_num = pin.get("pin", "")
            pad_name = (pin.get("pad") or "").strip()
            pad = pad_by_name.get(pad_name)
            if pad is None:
                continue
            key = f"{pin_num}:{pad_name}"
            tip_x, tip_y = pad["x"], pad["y"]
            dx, dy = self._pin_offsets.get(key, (0.0, -self._PIN_LENGTH))
            tail_x, tail_y = tip_x + dx, tip_y + dy
            line_id = self.canvas.create_line(
                tail_x, tail_y, tip_x, tip_y,
                fill="black", width=2, arrow=tk.LAST, arrowshape=(8, 10, 3))
            text_id = self.canvas.create_text(
                tail_x, tail_y - 7, text=pin_num,
                font=("Arial", 7, "bold"), fill="black")
            handle_id = self.canvas.create_oval(
                tail_x - 4, tail_y - 4, tail_x + 4, tail_y + 4,
                fill="white", outline="black")
            self._pin_items[key] = (line_id, text_id, handle_id)
            self._pin_tips[key] = (tip_x, tip_y)
            self._pins_by_pad.setdefault(pad_name, []).append(key)

    def refresh_pins(self):
        if self._source == "custom":
            self._draw_custom()

    def _hit_test_pad(self, cx, cy):
        for idx, (rect_id, _text_id) in self._pad_items.items():
            x1, y1, x2, y2 = self.canvas.coords(rect_id)
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return idx
        return None

    def _hit_test_die_handle(self, cx, cy, radius=8):
        for idx, (_rect_id, _text_id, handle_id) in self._die_items.items():
            hx1, hy1, hx2, hy2 = self.canvas.coords(handle_id)
            if hx1 - radius <= cx <= hx2 + radius and hy1 - radius <= cy <= hy2 + radius:
                return idx
        return None

    def _hit_test_pin_handle(self, cx, cy, radius=8):
        for key, (_line_id, _text_id, handle_id) in self._pin_items.items():
            hx1, hy1, hx2, hy2 = self.canvas.coords(handle_id)
            if hx1 - radius <= cx <= hx2 + radius and hy1 - radius <= cy <= hy2 + radius:
                return key
        return None

    def _hit_test_die(self, cx, cy):
        for idx, (rect_id, _text_id, _handle_id) in self._die_items.items():
            x1, y1, x2, y2 = self.canvas.coords(rect_id)
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return idx
        return None

    def _notify_change(self):
        if self._on_custom_change:
            self._on_custom_change()

    def _move_pad_pins(self, pad_name, dx, dy):
        for key in self._pins_by_pad.get(pad_name, []):
            line_id, text_id, handle_id = self._pin_items[key]
            self.canvas.move(line_id, dx, dy)
            self.canvas.move(text_id, dx, dy)
            self.canvas.move(handle_id, dx, dy)

    def _sync_pad_pin_tips(self, pad):
        for key in self._pins_by_pad.get(pad["name"], []):
            self._pin_tips[key] = (pad["x"], pad["y"])

    def _on_edit_press(self, e):
        cx, cy = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
        self._drag_index = None
        self._die_drag_index = None
        self._die_drag_pad_indices = []
        self._die_resize_index = None
        self._pin_drag_key = None
        self._pan_press_xy = None

        pad_idx = self._hit_test_pad(cx, cy)
        if pad_idx is not None:
            self._drag_index = pad_idx
            self._drag_press_xy = (cx, cy)
            return

        pin_key = self._hit_test_pin_handle(cx, cy)
        if pin_key is not None:
            self._pin_drag_key = pin_key
            return

        handle_idx = self._hit_test_die_handle(cx, cy)
        if handle_idx is not None:
            self._die_resize_index = handle_idx
            self._drag_press_xy = (cx, cy)
            return

        die_idx = self._hit_test_die(cx, cy)
        if die_idx is not None:
            self._die_drag_index = die_idx
            self._drag_press_xy = (cx, cy)
            die = self._custom_dies[die_idx]
            x1, y1, x2, y2 = die["x1"], die["y1"], die["x2"], die["y2"]
            self._die_drag_pad_indices = [
                i for i, p in enumerate(self._custom_pads)
                if x1 <= p["x"] <= x2 and y1 <= p["y"] <= y2
            ]
            return

        self._pan_press_xy = (e.x, e.y)
        self.canvas.scan_mark(e.x, e.y)

    def _on_edit_motion(self, e):
        cx, cy = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
        if self._drag_index is not None:
            px, py = self._drag_press_xy
            dx, dy = cx - px, cy - py
            rect_id, text_id = self._pad_items[self._drag_index]
            self.canvas.move(rect_id, dx, dy)
            self.canvas.move(text_id, dx, dy)
            self._move_pad_pins(self._custom_pads[self._drag_index]["name"], dx, dy)
            self._drag_press_xy = (cx, cy)
        elif self._pin_drag_key is not None:
            key = self._pin_drag_key
            line_id, text_id, handle_id = self._pin_items[key]
            tip_x, tip_y = self._pin_tips[key]
            tail_x, tail_y = self._clamp_pin_tail(cx, cy, tip_x, tip_y)
            self.canvas.coords(line_id, tail_x, tail_y, tip_x, tip_y)
            self.canvas.coords(text_id, tail_x, tail_y - 7)
            self.canvas.coords(handle_id, tail_x - 4, tail_y - 4, tail_x + 4, tail_y + 4)
        elif self._die_resize_index is not None:
            rect_id, _text_id, handle_id = self._die_items[self._die_resize_index]
            x1, y1, _x2, _y2 = self.canvas.coords(rect_id)
            x2, y2 = max(cx, x1 + 20), max(cy, y1 + 20)
            self.canvas.coords(rect_id, x1, y1, x2, y2)
            self.canvas.coords(handle_id, x2 - 4, y2 - 4, x2 + 4, y2 + 4)
        elif self._die_drag_index is not None:
            px, py = self._drag_press_xy
            dx, dy = cx - px, cy - py
            rect_id, text_id, handle_id = self._die_items[self._die_drag_index]
            self.canvas.move(rect_id, dx, dy)
            self.canvas.move(text_id, dx, dy)
            self.canvas.move(handle_id, dx, dy)
            for pad_idx in self._die_drag_pad_indices:
                pad_rect_id, pad_text_id = self._pad_items[pad_idx]
                self.canvas.move(pad_rect_id, dx, dy)
                self.canvas.move(pad_text_id, dx, dy)
                self._move_pad_pins(self._custom_pads[pad_idx]["name"], dx, dy)
            self._drag_press_xy = (cx, cy)
        elif self._pan_press_xy is not None:
            self.canvas.scan_dragto(e.x, e.y, gain=1)

    def _on_edit_release(self, e):
        if self._drag_index is not None:
            idx = self._drag_index
            rect_id, _text_id = self._pad_items[idx]
            x1, y1, x2, y2 = self.canvas.coords(rect_id)
            self._custom_pads[idx]["x"] = (x1 + x2) / 2
            self._custom_pads[idx]["y"] = (y1 + y2) / 2
            self._sync_pad_pin_tips(self._custom_pads[idx])
            self._drag_index = None
            self._drag_press_xy = None
            self._notify_change()
            return
        if self._pin_drag_key is not None:
            key = self._pin_drag_key
            line_id, _text_id, _handle_id = self._pin_items[key]
            tail_x, tail_y, tip_x, tip_y = self.canvas.coords(line_id)
            self._pin_offsets[key] = (tail_x - tip_x, tail_y - tip_y)
            self._pin_drag_key = None
            self._notify_change()
            return
        if self._die_resize_index is not None:
            idx = self._die_resize_index
            rect_id, _text_id, _handle_id = self._die_items[idx]
            x1, y1, x2, y2 = self.canvas.coords(rect_id)
            die = self._custom_dies[idx]
            die["x1"], die["y1"], die["x2"], die["y2"] = x1, y1, x2, y2
            self._die_resize_index = None
            self._drag_press_xy = None
            self._notify_change()
            return
        if self._die_drag_index is not None:
            idx = self._die_drag_index
            rect_id, _text_id, _handle_id = self._die_items[idx]
            x1, y1, x2, y2 = self.canvas.coords(rect_id)
            die = self._custom_dies[idx]
            die["x1"], die["y1"], die["x2"], die["y2"] = x1, y1, x2, y2
            for pad_idx in self._die_drag_pad_indices:
                pad_rect_id, _pad_text_id = self._pad_items[pad_idx]
                px1, py1, px2, py2 = self.canvas.coords(pad_rect_id)
                pad = self._custom_pads[pad_idx]
                pad["x"], pad["y"] = (px1 + px2) / 2, (py1 + py2) / 2
                self._sync_pad_pin_tips(pad)
            self._die_drag_index = None
            self._die_drag_pad_indices = []
            self._drag_press_xy = None
            self._notify_change()
            return
        if self._pan_press_xy is not None:
            press = self._pan_press_xy
            self._pan_press_xy = None
            dx, dy = e.x - press[0], e.y - press[1]
            if dx * dx + dy * dy > 16:
                return
            cx, cy = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
            self._add_pad_at(cx, cy)

    def _on_edit_double_click(self, e):
        cx, cy = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
        idx = self._hit_test_pad(cx, cy)
        if idx is not None:
            name = simpledialog.askstring(
                "Rename Pad", "Pad label:", initialvalue=self._custom_pads[idx]["name"],
                parent=self)
            if name:
                self._custom_pads[idx]["name"] = name
                _, text_id = self._pad_items[idx]
                self.canvas.itemconfig(text_id, text=name)
                self._notify_change()
            return
        didx = self._hit_test_die(cx, cy)
        if didx is not None:
            name = simpledialog.askstring(
                "Rename Die", "Die label:", initialvalue=self._custom_dies[didx]["name"],
                parent=self)
            if name:
                self._custom_dies[didx]["name"] = name
                _, text_id, _handle_id = self._die_items[didx]
                self.canvas.itemconfig(text_id, text=name)
                self._notify_change()

    def _on_edit_right_click(self, e):
        cx, cy = self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)
        idx = self._hit_test_pad(cx, cy)
        if idx is not None:
            name = self._custom_pads[idx]["name"]
            if messagebox.askyesno("Delete Pad", f"Delete pad '{name}'?", parent=self):
                del self._custom_pads[idx]
                self._draw_custom()
                self._notify_change()
            return
        didx = self._hit_test_die(cx, cy)
        if didx is not None:
            name = self._custom_dies[didx]["name"]
            if messagebox.askyesno("Delete Die", f"Delete die '{name}'? "
                                   "(pads inside are kept, just ungrouped)", parent=self):
                del self._custom_dies[didx]
                self._draw_custom()
                self._notify_change()

    def _add_pad_at(self, cx, cy, name=None):
        if name is None:
            name = simpledialog.askstring(
                "New Pad", "Pad label:", initialvalue=f"P{len(self._custom_pads) + 1}",
                parent=self)
            if not name:
                return
        self._custom_pads.append({"name": name, "x": cx, "y": cy})
        self._draw_custom()
        self._notify_change()

    def load_from_ata(self, folder_path):
        for fname in ("ata_pad_layout.csv", "pads.csv"):
            fpath = os.path.join(folder_path, fname)
            if os.path.exists(fpath):
                break
        else:
            self.canvas.delete("all")
            self.canvas.create_text(
                150, 80, text="ata_pad_layout.csv not found.", fill="red", justify="center"
            )
            return []

        pads = []
        with open(fpath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pads.append({k.lower().strip(): v.strip() for k, v in row.items()})

        if pads:
            self._last_pads = pads
            self._draw_from_pads(pads)
        return pads

    def _draw_from_pads(self, pads):
        self.canvas.delete("all")
        self.update_idletasks()
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W < 50:
            W, H = 340, 340

        sample = pads[0]
        x_key = next((k for k in ("x_um", "x_mm", "x", "center_x", "pad_x", "cx") if k in sample), None)
        y_key = next((k for k in ("y_um", "y_mm", "y", "center_y", "pad_y", "cy") if k in sample), None)
        n_key = next((k for k in ("pad_name", "name", "label", "net_name", "net", "pad") if k in sample), None)
        w_key = next((k for k in ("width_um", "w_um", "width", "bbox_width_um") if k in sample), None)
        h_key = next((k for k in ("height_um", "h_um", "height", "bbox_height_um") if k in sample), None)

        if not (x_key and y_key):
            self.draw_pads()
            return

        pdata = []
        for p in pads:
            try:
                x = float(p[x_key])
                y = float(p[y_key])
                name = p.get(n_key, "") if n_key else ""
                pw_d = float(p[w_key]) if w_key and p.get(w_key, "").strip() else None
                ph_d = float(p[h_key]) if h_key and p.get(h_key, "").strip() else None
                pdata.append((x, y, name, pw_d, ph_d))
            except (ValueError, KeyError):
                continue

        if not pdata:
            self.draw_pads()
            return

        xs = [p[0] for p in pdata]
        ys = [p[1] for p in pdata]
        margin = 52
        x_span = (max(xs) - min(xs)) or 1.0
        y_span = (max(ys) - min(ys)) or 1.0
        scale  = min((W - 2 * margin) / x_span, (H - 2 * margin) / y_span)

        def to_cx(xd): return margin + (xd - min(xs)) * scale
        def to_cy(yd): return (H - margin) - (yd - min(ys)) * scale

        auto_pw = max(8, min(22, scale * 20))
        auto_ph = max(5, auto_pw * 0.6)

        dm = max(auto_pw, auto_ph) * 1.8
        bx1, by1 = to_cx(min(xs)) - dm, to_cy(max(ys)) - dm
        bx2, by2 = to_cx(max(xs)) + dm, to_cy(min(ys)) + dm
        self.canvas.create_rectangle(bx1, by1, bx2, by2,
                                     outline="#999", width=1, dash=(6, 4))
        self.canvas.create_text((bx1 + bx2) / 2, by1 - 9,
                                 text="Device Boundary", fill="#aaa", font=("Arial", 7))

        self.canvas.create_text(W / 2, H - 8, text="X (µm)", fill="#888", font=("Arial", 7))
        self.canvas.create_text(10, H / 2, text="Y\n(µm)", fill="#888", font=("Arial", 7))

        for x, y, name, pw_d, ph_d in pdata:
            cx_ = to_cx(x)
            cy_ = to_cy(y)
            if pw_d and ph_d:
                half_w = max(4, min(pw_d * scale / 2, 32))
                half_h = max(3, min(ph_d * scale / 2, 22))
            else:
                half_w, half_h = auto_pw / 2, auto_ph / 2
            self.canvas.create_rectangle(
                cx_ - half_w, cy_ - half_h, cx_ + half_w, cy_ + half_h,
                fill="gold", outline="#888", width=1
            )
            if name:
                self.canvas.create_text(cx_, cy_ - half_h - 6,
                                        text=name, font=("Arial", 7), fill="#333")

        self.config(text=f"Pad Layout — {len(pdata)} pads")

    def draw_pads(self):
        self.canvas.delete("all")
        self.update_idletasks()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 50:
            w, h = 200, 200

        self.canvas.create_rectangle(
            w * 0.25, h * 0.25, w * 0.75, h * 0.75, fill="#f0f0f0", outline="black", width=2
        )
        self.canvas.create_text(w / 2, h / 2, text="MEMS ACCEL\nDEVICE", justify="center", font=("Arial", 9, "bold"))

        pads = [
            (w * 0.35, h * 0.25 - 10, "P1"), (w * 0.5, h * 0.25 - 10, "P2"), (w * 0.65, h * 0.25 - 10, "P3"),
            (w * 0.35, h * 0.75 + 10, "P6"), (w * 0.5, h * 0.75 + 10, "P5"), (w * 0.65, h * 0.75 + 10, "P4"),
        ]
        for px, py, name in pads:
            self.canvas.create_rectangle(px - 15, py - 5, px + 15, py + 5, fill="gold", outline="black")
            self.canvas.create_text(
                px, py - 18 if py < h / 2 else py + 18,
                text=name, font=("Arial", 8, "bold")
            )
