import tkinter as tk
from tkinter import ttk
import os
import threading
import time

from wafer_map_view import (WaferMapPanel, PadLayoutPanel, ProbeCardWiringFrame,
                            ATA_KEY_FILES, WAFER_MAP_SOURCES, _pz_bind)
from execution_panel import ExecutionDashboard
from gds_parser_panel import GdsParserPanel
from switch_debug_panel import SwitchDebugPanel
from switch_settings_panel import SwitchSettingsPanel
from switchbox_test_panel import SwitchboxTestPanel
from instruments_eg_panel import InstrumentsEgPanel
from probe_routing_panel import scrollable_routing
from prober_debug_panel import ProberDebugPanel
from accr_wafer_panel import AccrWaferPanel
from cassette_panel import CassettePanel
from recipe_panel import RecipePanel
from pma_wafer_panel import (PmaWaferPanel, pma_shots_to_grid, merge_with_accretech,
                             centroid_offset)
from nanoz_panel import NanoZPanel
import export_formats as xfmt
from engineering_units import parse_engineering, format_engineering


def _parse_q_response(raw: str):
    import re
    raw = (raw or "").strip()
    m = re.search(r'Y\s*([+-]?\d+)\s*X\s*([+-]?\d+)', raw)
    if m:
        return float(m.group(2)), float(m.group(1))
    parts = re.findall(r'[+-]?\d+\.?\d*', raw)
    if len(parts) >= 2:
        return float(parts[1]), float(parts[0])
    raise ValueError(f"Cannot parse Q response: {raw!r}")


def _compute_alignment_transform(expected, measured):
    import math
    cx_e = sum(p[0] for p in expected) / len(expected)
    cy_e = sum(p[1] for p in expected) / len(expected)
    cx_m = sum(p[0] for p in measured) / len(measured)
    cy_m = sum(p[1] for p in measured) / len(measured)
    dx = cx_m - cx_e
    dy = cy_m - cy_e

    vex = expected[1][0] - expected[0][0]
    vey = expected[1][1] - expected[0][1]
    vmx = measured[1][0] - measured[0][0]
    vmy = measured[1][1] - measured[0][1]
    cross = vex * vmy - vey * vmx
    dot   = vex * vmx + vey * vmy
    theta_deg = math.degrees(math.atan2(cross, dot))

    return dx, dy, theta_deg


class AlignmentPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Alignment Marks")
        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        self._last_marks = None
        self.canvas.create_text(100, 100, text="NO SIGNAL", fill="red")
        _pz_bind(self.canvas, self._reset_view)

    def _reset_view(self):
        if self._last_marks:
            self._draw_marks(self._last_marks)
        else:
            self.canvas.delete("all")
            self._draw_grid()
            self.canvas.create_text(100, 100, text="NO SIGNAL", fill="red")

    def load_from_ata(self, folder_path):
        import csv
        marks = []
        for fname in ("ata_alignment_marks.csv", "alignment_marks.csv"):
            fpath = os.path.join(folder_path, fname)
            if os.path.exists(fpath):
                with open(fpath, newline="", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        marks.append({k.lower().strip(): v.strip() for k, v in row.items()})
                break

        if marks:
            self._last_marks = marks
            self._draw_marks(marks)
        else:
            self._last_marks = None
            self.canvas.delete("all")
            self._draw_grid()
            self.canvas.create_text(
                100, 80, text="No alignment marks\nfound in folder.", fill="orange", justify="center"
            )
        return marks

    def _draw_grid(self):
        self.update_idletasks()
        W = self.canvas.winfo_width() or 300
        H = self.canvas.winfo_height() or 300
        for i in range(0, W, 40):
            self.canvas.create_line(i, 0, i, H, fill="#1a1a1a")
        for i in range(0, H, 40):
            self.canvas.create_line(0, i, W, i, fill="#1a1a1a")

    def _draw_marks(self, marks):
        self.canvas.delete("all")
        self._draw_grid()
        self.update_idletasks()
        W = self.canvas.winfo_width() or 300
        H = self.canvas.winfo_height() or 300

        sample = marks[0]
        x_key = next((k for k in ("x_mm", "x_um", "x", "pos_x", "stage_x") if k in sample), None)
        y_key = next((k for k in ("y_mm", "y_um", "y", "pos_y", "stage_y") if k in sample), None)
        n_key = next((k for k in ("name", "mark_id", "mark", "id", "label") if k in sample), None)

        if not (x_key and y_key):
            for i, pos in enumerate([(W*0.3, H*0.3), (W*0.7, H*0.7)]):
                self._draw_crosshair(pos[0], pos[1], f"M{i+1}", "lime")
            return

        coords = []
        for m in marks:
            try:
                coords.append((float(m[x_key]), float(m[y_key]), m.get(n_key, "") if n_key else ""))
            except (ValueError, KeyError):
                continue

        if not coords:
            return

        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        margin = 60
        x_span = (max(xs) - min(xs)) or 1
        y_span = (max(ys) - min(ys)) or 1
        scale  = min((W - 2*margin) / x_span, (H - 2*margin) / y_span)
        x0 = (W - x_span*scale) / 2 - min(xs)*scale
        y0 = (H - y_span*scale) / 2 - min(ys)*scale

        palette = ["lime", "cyan", "yellow", "orange", "#ff80ff"]
        for i, (x, y, name) in enumerate(coords):
            self._draw_crosshair(x0 + x*scale, y0 + y*scale, name or f"M{i+1}", palette[i % len(palette)])

        self.config(text=f"Alignment Marks — {len(coords)} marks")

    def _draw_crosshair(self, cx, cy, label, color="lime"):
        arm = 20
        self.canvas.create_line(cx - arm, cy, cx + arm, cy, fill=color, width=1)
        self.canvas.create_line(cx, cy - arm, cx, cy + arm, fill=color, width=1)
        self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=color, outline="")
        self.canvas.create_text(cx + arm + 4, cy, text=label, fill=color, anchor="w", font=("Arial", 8))

    def lock_alignment(self):
        self.canvas.delete("all")
        self._draw_grid()
        self.update_idletasks()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 50:
            w, h = 200, 200
        self.canvas.create_line(w/2 - 35, h/2, w/2 + 35, h/2, fill="lime", width=2)
        self.canvas.create_line(w/2, h/2 - 35, w/2, h/2 + 35, fill="lime", width=2)
        self.canvas.create_oval(w/2 - 4, h/2 - 4, w/2 + 4, h/2 + 4, fill="lime", outline="")
        self.canvas.create_text(w/2, h/2 + 50, text="✓  LOCKED", fill="lime", font=("Arial", 10, "bold"))

    def highlight_mark(self, index: int):
        marks = self._last_marks
        if not marks or index >= len(marks):
            return
        sample = marks[0]
        x_key = next((k for k in ("x_mm", "x_um", "x", "pos_x", "stage_x") if k in sample), None)
        y_key = next((k for k in ("y_mm", "y_um", "y", "pos_y", "stage_y") if k in sample), None)
        n_key = next((k for k in ("name", "mark_id", "mark", "id", "label") if k in sample), None)
        if not (x_key and y_key):
            return
        coords = []
        for m in marks:
            try:
                coords.append((float(m[x_key]), float(m[y_key]),
                               m.get(n_key, "") if n_key else ""))
            except (ValueError, KeyError):
                continue
        if index >= len(coords):
            return
        self._draw_marks(marks)
        self.update_idletasks()
        W = self.canvas.winfo_width() or 300
        H = self.canvas.winfo_height() or 300
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        margin = 60
        x_span = (max(xs) - min(xs)) or 1
        y_span = (max(ys) - min(ys)) or 1
        scale  = min((W - 2*margin) / x_span, (H - 2*margin) / y_span)
        x0 = (W - x_span*scale) / 2 - min(xs)*scale
        y0 = (H - y_span*scale) / 2 - min(ys)*scale
        x, y, name = coords[index]
        cx = x0 + x*scale
        cy = y0 + y*scale
        self.canvas.create_oval(cx-22, cy-22, cx+22, cy+22,
                                outline="white", width=2, dash=(4, 2))
        self._draw_crosshair(cx, cy, f"▶ {name or f'M{index+1}'}", "white")
        self.update_idletasks()

    def show_alignment_result(self, dx, dy, theta_deg):
        self.update_idletasks()
        W = self.canvas.winfo_width() or 300
        H = self.canvas.winfo_height() or 300
        self.canvas.create_rectangle(
            W//2 - 155, H - 55, W//2 + 155, H - 8,
            fill="#0f172a", outline="#22c55e",
        )
        self.canvas.create_text(
            W//2, H - 32,
            text=f"ΔX = {dx:+.2f} µm    ΔY = {dy:+.2f} µm    θ = {theta_deg:+.4f}°",
            fill="#22c55e", font=("Consolas", 9),
        )


class MainLayout(ttk.Frame):
    def __init__(self, parent, controller, instrument_names=None, init_hardware_fn=None,
                 system: str = "accretech"):
        super().__init__(parent)
        self.controller = controller
        self._system = system
        self._instrument_names = instrument_names or [
            "UF200R Prober", "SMU (2636B)", "DMM (34461A)", "SW_MATRIX", "Wave Gen (33512B)"]
        self._init_hardware_fn = init_hardware_fn or controller.init_hardware
        self.export_path_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Downloads'))
        self.working_dir_var = tk.StringVar(value="C:/automationproject")
        self.lot_id = tk.StringVar()
        self.wafer_id_var = tk.StringVar()
        self.status_labels = {}
        self._ata_folder = None
        self._pad_custom_loaded = False
        self._smu_output_lf: dict = {}
        self._wg_output_lf: dict = {}
        self._smu_level_vars: dict = {}
        self._smu_cont_active: dict = {}
        self._dmm_cont_active: bool = False
        self._dmm_cont_thread = None
        self._dmm_status_var: tk.StringVar | None = None
        self._inst_status_vars: dict = {}
        self._build_layout()

    def _build_layout(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)

        self._build_sidebar(paned)
        self._build_notebook(paned)

    def _build_sidebar(self, paned):
        sidebar = ttk.Frame(paned, width=280, relief="sunken", padding=5)
        paned.add(sidebar, weight=0)
        sidebar.pack_propagate(False)

        self.status_label = ttk.Label(
            sidebar, text="INITIALIZING", foreground="orange",
            font=("Arial", 11, "bold")
        )
        self.status_label.pack(anchor="w", pady=(0, 4))

        self.prober_status_label = ttk.Label(
            sidebar, text="Prober: —", foreground="orange",
            font=("Arial", 9)
        )
        self.prober_status_label.pack(anchor="w", pady=(0, 10))

        inst_frame = ttk.LabelFrame(sidebar, text="Instruments")
        inst_frame.pack(fill="x", pady=4)
        for inst in self._instrument_names:
            lbl = ttk.Label(inst_frame, text=f"⏳ {inst}", foreground="orange")
            lbl.pack(anchor="w", padx=4, pady=2)
            self.status_labels[inst] = lbl
        ttk.Button(
            inst_frame, text="↻ Refresh Connections",
            command=self._init_hardware_fn
        ).pack(pady=(8, 4), padx=4, fill="x")

        self.lbl_progress = ttk.Label(sidebar, text="No wafer loaded")
        self.sidebar_canvas = tk.Canvas(
            sidebar, width=110, height=110, bg="#f0f0f0", highlightthickness=0
        )
        self.lbl_stats_text = ttk.Label(
            sidebar, text="Pass: 0  |  Fail: 0\nUntested: 0", justify="center"
        )

        log_frame = ttk.LabelFrame(sidebar, text="Execution Log")
        log_frame.pack(fill="both", expand=True, pady=4)
        self.log_text = tk.Text(
            log_frame, bg="#1e1e1e", fg="lime", font=("Consolas", 8),
            wrap="word", state="disabled", width=24
        )
        log_sb = ttk.Scrollbar(log_frame, orient="vertical",
                               command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_sb.set)
        log_sb.pack(side="right", fill="y", pady=2)
        self.log_text.pack(fill="both", expand=True, padx=(2, 0), pady=2)

    @staticmethod
    def _enable_tab_drag(nb: ttk.Notebook):
        state = {}

        def on_press(event):
            try:
                state["src"] = nb.index(f"@{event.x},{event.y}")
            except tk.TclError:
                state["src"] = None

        def on_motion(event):
            if state.get("src") is None:
                return
            try:
                dst = nb.index(f"@{event.x},{event.y}")
            except tk.TclError:
                return
            if dst != state["src"]:
                nb.insert(dst, nb.tabs()[state["src"]])
                state["src"] = dst

        nb.bind("<ButtonPress-1>", on_press, add=True)
        nb.bind("<B1-Motion>",     on_motion, add=True)

    def _build_notebook(self, paned):
        top_nb = ttk.Notebook(paned)
        paned.add(top_nb, weight=1)

        main_frame = ttk.Frame(top_nb)
        top_nb.add(main_frame, text="  Main  ")
        main_nb = ttk.Notebook(main_frame)
        main_nb.pack(fill="both", expand=True)
        self._enable_tab_drag(main_nb)

        self._tab_wafer_map(main_nb)
        self._tab_recipe(main_nb)
        self._tab_execution2(main_nb)
        self._tab_results(main_nb)
        self._tab_gds_parser(main_nb)
        self._tab_pad_layout(main_nb)
        if self._system == "accretech":
            self._tab_accr_wafer(main_nb)
        self._tab_pma_wafer(main_nb)

        debug_frame = ttk.Frame(top_nb)
        top_nb.add(debug_frame, text="  Debug  ")
        debug_nb = ttk.Notebook(debug_frame)
        debug_nb.pack(fill="both", expand=True)
        self._enable_tab_drag(debug_nb)

        if self._system == "accretech":
            self._tab_instruments(debug_nb)
            self._tab_probe_routing(debug_nb)
        else:
            self._tab_instruments_eg(debug_nb)
        self._tab_switch_settings(debug_nb)
        self._tab_prober_debug(debug_nb)
        self._tab_cassette(debug_nb)

        self._build_exec_panel()
        self._build_alignment_panel()

        if self._system == "accretech":
            nanoz_frame = ttk.Frame(top_nb)
            top_nb.add(nanoz_frame, text="  NanoZ  ")
            self.nanoz_panel = NanoZPanel(nanoz_frame, controller=self.controller, main_layout=self)
            self.nanoz_panel.pack(fill="both", expand=True)

    def _tab_instruments(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Instruments")
        tab.rowconfigure(2, weight=1)
        tab.columnconfigure(0, weight=1)

        rst = tk.Frame(tab, bg="#7f1d1d")
        rst.grid(row=0, column=0, sticky="ew")
        tk.Button(
            rst,
            text="⚠  Global Reset — All Outputs OFF + Open All Switches",
            bg="#dc2626", fg="white",
            activebackground="#b91c1c", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
            command=self._global_reset,
        ).pack(side="left", padx=8, pady=4)
        tk.Button(
            rst,
            text="↻ Query Status",
            bg="#1e3a5f", fg="white",
            activebackground="#1e40af", activeforeground="white",
            font=("Segoe UI", 9), relief="flat", bd=0,
            command=lambda: threading.Thread(
                target=self._query_all_status, daemon=True).start(),
        ).pack(side="left", padx=4, pady=4)

        sbar = tk.Frame(tab, bg="#0f172a")
        sbar.grid(row=1, column=0, sticky="ew")
        for key, lbl in [("smua", "SMU A"), ("smub", "SMU B"),
                          ("wg1", "WG CH1"), ("wg2", "WG CH2"),
                          ("dmm", "DMM"), ("prober", "Prober")]:
            v = tk.StringVar(value=f"{lbl}: ?")
            self._inst_status_vars[key] = v
            tk.Label(sbar, textvariable=v,
                     bg="#0f172a", fg="#94a3b8",
                     font=("Consolas", 8), padx=10, pady=2).pack(side="left")

        pane = ttk.PanedWindow(tab, orient="horizontal")
        pane.grid(row=2, column=0, sticky="nsew")

        dmm_pane = ttk.Frame(pane)
        pane.add(dmm_pane, weight=1)

        smu_pane = ttk.Frame(pane)
        pane.add(smu_pane, weight=3)

        wg_pane = ttk.Frame(pane)
        pane.add(wg_pane, weight=1)

        self._build_dmm_card(dmm_pane)
        self._build_smu_card(smu_pane)
        self._build_wavegen_card(wg_pane)

    def _build_dmm_card(self, parent):
        card = ttk.LabelFrame(parent, text="Keysight 34461A  (DMM)")
        card.pack(fill="both", expand=True, padx=6, pady=6)

        ttk.Label(
            card, text="Addr: USB0::0x2A8D::0x1301::MY57216618::INSTR",
            foreground="gray", font=("Consolas", 8)
        ).pack(anchor="w", padx=6, pady=(4, 0))

        self._dmm_status_var = tk.StringVar(value="○ IDLE")
        ttk.Label(card, textvariable=self._dmm_status_var,
                  font=("Consolas", 8, "bold"), foreground="#6b7280",
                  ).pack(anchor="w", padx=6, pady=(0, 2))

        reading_var = tk.StringVar(value="──")
        ttk.Label(
            card, textvariable=reading_var,
            font=("Consolas", 18, "bold"), foreground="#0077cc"
        ).pack(pady=10)

        def measure(mode):
            drv = self.controller.drivers.get("dmm")
            if not drv or not drv.inst:
                reading_var.set("NOT CONNECTED")
                self.controller.log(f"[DMM] {mode}: not connected")
                return
            try:
                if mode == "VDC":
                    val = drv.measure_voltage_dc();  reading_var.set(format_engineering(val, "V"))
                elif mode == "IDC":
                    val = drv.measure_current_dc();  reading_var.set(format_engineering(val, "A"))
                elif mode == "R2W":
                    val = drv.measure_resistance(2); reading_var.set(format_engineering(val, "Ω"))
                elif mode == "R4W":
                    val = drv.measure_resistance(4); reading_var.set(format_engineering(val, "Ω"))
                self.controller.log(f"[DMM] {mode}: {reading_var.get()}")
            except Exception as e:
                reading_var.set("ERROR"); self.controller.log(f"[DMM] {mode} error: {e}")

        btn_row = ttk.Frame(card)
        btn_row.pack(fill="x", padx=6, pady=2)
        for lbl, mode in [("VDC", "VDC"), ("IDC", "IDC"), ("Ω 2W", "R2W"), ("Ω 4W", "R4W")]:
            ttk.Button(btn_row, text=f"Meas {lbl}", command=lambda m=mode: measure(m)).pack(side="left", padx=2, pady=2)

        all_lf = ttk.LabelFrame(card, text="All Readings", padding=(6, 4))
        all_lf.pack(fill="x", padx=6, pady=(2, 0))
        all_lf.columnconfigure(1, weight=1)
        all_lf.columnconfigure(3, weight=1)

        _all_vars: dict[str, tk.StringVar] = {}
        _all_items = [("VDC:", "VDC", "V"), ("IDC:", "IDC", "A"), ("R 2W:", "R2W", "Ω"), ("R 4W:", "R4W", "Ω")]
        for i, (lbl, key, _) in enumerate(_all_items):
            r, c = divmod(i, 2)
            ttk.Label(all_lf, text=lbl, width=5, anchor="e").grid(row=r, column=c*2,   sticky="e",  padx=(4, 2), pady=2)
            v = tk.StringVar(value="——")
            ttk.Label(all_lf, textvariable=v,
                      font=("Consolas", 9, "bold"), foreground="#0077cc",
                      anchor="w").grid(row=r, column=c*2+1, sticky="ew", padx=(0, 8), pady=2)
            _all_vars[key] = v

        def _meas_all_dmm():
            drv = self.controller.drivers.get("dmm")
            if not drv or not drv.inst:
                self.controller.log("[DMM] Meas All: not connected")
                return
            pairs = [
                ("VDC", drv.measure_voltage_dc,           lambda x: format_engineering(x, "V")),
                ("IDC", drv.measure_current_dc,           lambda x: format_engineering(x, "A")),
                ("R2W", lambda: drv.measure_resistance(2), lambda x: format_engineering(x, "Ω")),
                ("R4W", lambda: drv.measure_resistance(4), lambda x: format_engineering(x, "Ω")),
            ]
            for key, fn, fmt in pairs:
                try:
                    _all_vars[key].set(fmt(fn()))
                except Exception as e:
                    _all_vars[key].set("ERROR")
                    self.controller.log(f"[DMM] Meas All {key} error: {e}")
            self.controller.log(
                f"[DMM] All: VDC={_all_vars['VDC'].get()}  IDC={_all_vars['IDC'].get()}  "
                f"R2W={_all_vars['R2W'].get()}  R4W={_all_vars['R4W'].get()}"
            )

        ttk.Button(card, text="Meas All  (V · I · R2W · R4W)",
                   command=_meas_all_dmm).pack(fill="x", padx=6, pady=(4, 0))

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=6, pady=6)

        cfg_lf = ttk.LabelFrame(card, text="Configuration", padding=(8, 4))
        cfg_lf.pack(fill="x", padx=6, pady=(0, 4))

        dmm_func_var  = tk.StringVar(value="VDC")
        dmm_range_var = tk.StringVar(value="AUTO")
        dmm_nplc_var  = tk.StringVar(value="1")

        cfg_row1 = ttk.Frame(cfg_lf)
        cfg_row1.pack(fill="x", pady=2)
        ttk.Label(cfg_row1, text="Function:", width=9, anchor="e").pack(side="left")
        ttk.Combobox(cfg_row1, textvariable=dmm_func_var,
                     values=["VDC", "IDC", "R2W", "R4W"],
                     width=6, state="readonly").pack(side="left", padx=(4, 0))

        cfg_row2 = ttk.Frame(cfg_lf)
        cfg_row2.pack(fill="x", pady=2)
        ttk.Label(cfg_row2, text="Range:", width=9, anchor="e").pack(side="left")
        ttk.Entry(cfg_row2, textvariable=dmm_range_var, width=10).pack(side="left", padx=(4, 6))
        ttk.Label(cfg_row2, text="NPLC:", width=6, anchor="e").pack(side="left")
        ttk.Entry(cfg_row2, textvariable=dmm_nplc_var, width=5).pack(side="left", padx=(4, 0))

        def _dmm_configure():
            drv = self.controller.drivers.get("dmm")
            if not drv or not drv.inst:
                self.controller.log("[DMM] Configure: not connected")
                return
            try:
                func  = dmm_func_var.get()
                rng   = dmm_range_var.get().strip()
                nplc  = float(dmm_nplc_var.get())
                drv.set_nplc(nplc)
                func_map = {
                    "VDC": ("VOLT:DC", "VOLT:DC:RANG"),
                    "IDC": ("CURR:DC", "CURR:DC:RANG"),
                    "R2W": ("RES",     "RES:RANG"),
                    "R4W": ("FRES",    "FRES:RANG"),
                }
                func_cmd, rang_cmd = func_map.get(func, ("VOLT:DC", "VOLT:DC:RANG"))
                drv.write(f"CONF:{func_cmd}")
                if rng.upper() != "AUTO":
                    try:
                        drv.write(f"{rang_cmd} {parse_engineering(rng)}")
                    except ValueError:
                        pass
                self.controller.log(f"[DMM] Configured: func={func}, range={rng}, NPLC={nplc}")
            except Exception as e:
                self.controller.log(f"[DMM] Configure error: {e}")

        ttk.Button(cfg_lf, text="Apply Configuration",
                   command=_dmm_configure).pack(fill="x", pady=(4, 2))

        cont_lf = ttk.LabelFrame(card, text="Continuous Read", padding=(6, 4))
        cont_lf.pack(fill="x", padx=6, pady=(4, 0))

        cont_r = ttk.Frame(cont_lf)
        cont_r.pack(fill="x", pady=2)
        ttk.Label(cont_r, text="Interval:", width=9, anchor="e").pack(side="left")
        _dmm_cont_iv = tk.StringVar(value="500")
        ttk.Entry(cont_r, textvariable=_dmm_cont_iv, width=6).pack(side="left", padx=2)
        ttk.Label(cont_r, text="ms", foreground="gray").pack(side="left")
        _dmm_cont_btn = ttk.Button(cont_r, text="▶ Continuous")
        _dmm_cont_btn.pack(side="right", padx=(4, 0))

        def _toggle_cont_dmm():
            if self._dmm_cont_active:
                self._dmm_cont_active = False
                _dmm_cont_btn.config(text="▶ Continuous")
                self._dmm_status_var.set("○ IDLE")
                self.controller.log("[DMM] Continuous read stopped")
            else:
                self._dmm_cont_active = True
                _dmm_cont_btn.config(text="■ Stop")
                self.controller.log("[DMM] Continuous read started")
                def _loop():
                    while self._dmm_cont_active:
                        try:
                            ms = max(100, int(_dmm_cont_iv.get()))
                        except ValueError:
                            ms = 500
                        drv = self.controller.drivers.get("dmm")
                        if drv and drv.inst:
                            try:
                                func_now = dmm_func_var.get()
                                if func_now == "VDC":
                                    val = drv.measure_voltage_dc()
                                    reading_var.set(format_engineering(val, "V"))
                                    self._dmm_status_var.set(f"● CONT  {format_engineering(val, 'V')}")
                                elif func_now == "IDC":
                                    val = drv.measure_current_dc()
                                    reading_var.set(format_engineering(val, "A"))
                                    self._dmm_status_var.set(f"● CONT  {format_engineering(val, 'A')}")
                                elif func_now in ("R2W", "R4W"):
                                    mode = 4 if func_now == "R4W" else 2
                                    val = drv.measure_resistance(mode)
                                    reading_var.set(format_engineering(val, "Ω"))
                                    self._dmm_status_var.set(f"● CONT  {format_engineering(val, 'Ω')}")
                            except Exception as e:
                                self._dmm_status_var.set(f"● ERR: {e}")
                        time.sleep(ms / 1000)
                self._dmm_cont_thread = threading.Thread(target=_loop, daemon=True)
                self._dmm_cont_thread.start()

        _dmm_cont_btn.config(command=_toggle_cont_dmm)

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=6, pady=6)
        self._scpi_row(card, "dmm")

    def _build_smu_card(self, parent):
        card = ttk.LabelFrame(parent, text="Keithley 2636B  (SMU)")
        card.pack(fill="both", expand=True, padx=6, pady=6)
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Addr: GPIB0::10::INSTR",
                  foreground="gray", font=("Consolas", 8)).pack(
                  anchor="w", padx=8, pady=(4, 6))

        ch_frame = ttk.Frame(card)
        ch_frame.pack(fill="both", expand=True, padx=6)
        ch_frame.columnconfigure(0, weight=1)
        ch_frame.columnconfigure(1, weight=1)

        self._smu_last = {
            "smua": {"I": None, "V": None, "R": None},
            "smub": {"I": None, "V": None, "R": None},
        }

        for idx, ch in enumerate(("smua", "smub")):
            self._build_smu_channel(ch_frame, ch, col=idx)

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=6, pady=6)

        comp_lf = ttk.LabelFrame(card, text="Compliance Thresholds", padding=(8, 6))
        comp_lf.pack(fill="x", padx=6, pady=(0, 4))

        thresh_row = ttk.Frame(comp_lf)
        thresh_row.pack(fill="x", pady=(0, 6))

        self._smu_thr = {}
        for label, key, default, unit in [
            ("I max",  "I_max", "1e-6",  "A"),
            ("V min",  "V_min", "0.9",   "V"),
            ("V max",  "V_max", "3.6",   "V"),
            ("R min",  "R_min", "1e4",   "Ω"),
        ]:
            f = ttk.Frame(thresh_row)
            f.pack(side="left", padx=(0, 12))
            ttk.Label(f, text=f"{label}:").pack(side="left")
            var = tk.StringVar(value=default)
            ttk.Entry(f, textvariable=var, width=8).pack(side="left", padx=2)
            ttk.Label(f, text=unit, foreground="gray").pack(side="left")
            self._smu_thr[key] = var

        btn_row = ttk.Frame(comp_lf)
        btn_row.pack(fill="x")
        self._smu_comp_result = tk.StringVar(value="—")

        for label, ch_arg in [("Check smua", "smua"),
                               ("Check smub", "smub"),
                               ("Check Both", "both")]:
            ttk.Button(btn_row, text=f"✓  {label}",
                       command=lambda c=ch_arg: self._smu_check_compliance(c)).pack(
                       side="left", padx=2)

        self._smu_comp_lbl = ttk.Label(btn_row, textvariable=self._smu_comp_result,
                                       font=("Consolas", 11, "bold"),
                                       foreground="#374151")
        self._smu_comp_lbl.pack(side="left", padx=12)

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=6, pady=6)
        self._scpi_row(card, "smu")

    def _build_smu_channel(self, parent, ch: str, col: int):
        lf = ttk.LabelFrame(parent, text=f"{ch.upper()}  ○ OFF", padding=(8, 6))
        lf.grid(row=0, column=col, sticky="nsew",
                padx=(0 if col == 0 else 6, 0), pady=0)
        lf.columnconfigure(1, weight=1)
        self._smu_output_lf[ch] = lf

        src_row = ttk.Frame(lf)
        src_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        ttk.Label(src_row, text="Source:").pack(side="left")
        src_var = tk.StringVar(value="Voltage")
        src_cb  = ttk.Combobox(src_row, textvariable=src_var,
                                values=["Voltage", "Current"],
                                width=8, state="readonly")
        src_cb.pack(side="left", padx=(4, 0))

        level_row = ttk.Frame(lf)
        level_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Label(level_row, text="Level:", width=9, anchor="e").pack(side="left")
        level_var = tk.StringVar(value="0.0")
        self._smu_level_vars[ch] = level_var
        ttk.Entry(level_row, textvariable=level_var, width=7).pack(side="left", padx=2)
        level_unit = ttk.Label(level_row, text="V", foreground="gray")
        level_unit.pack(side="left")

        comp_row = ttk.Frame(lf)
        comp_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)
        comp_lbl = ttk.Label(comp_row, text="I Limit:", width=9, anchor="e")
        comp_lbl.pack(side="left")
        comp_var = tk.StringVar(value="100e-6")
        ttk.Entry(comp_row, textvariable=comp_var, width=7).pack(side="left", padx=2)
        comp_unit = ttk.Label(comp_row, text="A", foreground="gray")
        comp_unit.pack(side="left")

        def _on_src(*_):
            if src_var.get() == "Voltage":
                level_unit.config(text="V")
                comp_lbl.config(text="I Limit:")
                comp_unit.config(text="A")
            else:
                level_unit.config(text="A")
                comp_lbl.config(text="V Limit:")
                comp_unit.config(text="V")
        src_var.trace_add("write", _on_src)

        nplc_row = ttk.Frame(lf)
        nplc_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Label(nplc_row, text="NPLC:", width=9, anchor="e").pack(side="left")
        nplc_var = tk.StringVar(value="1")
        ttk.Entry(nplc_row, textvariable=nplc_var, width=7).pack(side="left", padx=2)
        ttk.Label(nplc_row, text="PLC", foreground="gray").pack(side="left")

        out_row = ttk.Frame(lf)
        out_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 2))
        ttk.Button(out_row, text="Set & On",
                   command=lambda: _smu_set_on()).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(out_row, text="Output Off",
                   command=lambda: _smu_off()).pack(side="left", expand=True, fill="x", padx=(2, 0))

        ttk.Separator(lf, orient="horizontal").grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=6)

        reading_vars = {}
        for r_idx, (meas, key) in enumerate([
            ("I",  "I"),
            ("V",  "V"),
            ("R", "R"),
        ]):
            ttk.Label(lf, text=meas + ":", anchor="e", width=6).grid(
                row=6 + r_idx, column=0, sticky="e", pady=2)
            var = tk.StringVar(value="——")
            ttk.Label(lf, textvariable=var,
                      font=("Consolas", 10, "bold"),
                      foreground="#cc5500", anchor="w").grid(
                      row=6 + r_idx, column=1, sticky="ew", padx=(4, 0))
            reading_vars[key] = var

        meas_row = ttk.Frame(lf)
        meas_row.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(4, 1))
        ttk.Button(meas_row, text="Meas I",
                   command=lambda: _measure("I")).pack(side="left", expand=True, fill="x", padx=(0, 1))
        ttk.Button(meas_row, text="Meas V",
                   command=lambda: _measure("V")).pack(side="left", expand=True, fill="x", padx=1)
        ttk.Button(meas_row, text="Meas R",
                   command=lambda: _measure("R")).pack(side="left", expand=True, fill="x", padx=(1, 0))

        def _meas_all():
            _measure("I"); _measure("V"); _measure("R")
        ttk.Button(lf, text="Meas All  (I · V · R)",
                   command=_meas_all).grid(
                   row=10, column=0, columnspan=2, sticky="ew", pady=(1, 0))

        cont_row = ttk.Frame(lf)
        cont_row.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        _cont_iv = tk.StringVar(value="500")
        ttk.Label(cont_row, text="Interval:", width=9, anchor="e").pack(side="left")
        ttk.Entry(cont_row, textvariable=_cont_iv, width=5).pack(side="left", padx=2)
        ttk.Label(cont_row, text="ms", foreground="gray").pack(side="left")
        _cont_btn = ttk.Button(cont_row, text="▶ Cont.")
        _cont_btn.pack(side="right", padx=(4, 0))

        def _drv():
            drv = self.controller.drivers.get("smu")
            if not drv or not drv.inst:
                self.controller.log(f"[SMU] {ch}: not connected")
                return None
            return drv

        def _smu_set_on():
            drv = _drv()
            if not drv:
                return
            try:
                src  = src_var.get()
                lvl  = parse_engineering(level_var.get())
                comp = parse_engineering(comp_var.get())
                nplc = float(nplc_var.get())
                if src == "Voltage":
                    drv.set_voltage(ch, lvl)
                    drv.set_current_limit(ch, comp)
                else:
                    drv.set_current(ch, lvl)
                    drv.set_voltage_limit(ch, comp)
                try:
                    drv.set_nplc(ch, nplc)
                except Exception:
                    pass
                drv.turn_output_on(ch)
                self.controller.log(f"[SMU] {ch} ON — {src}={lvl}, comp={comp}, NPLC={nplc}")
                lf.config(text=f"{ch.upper()}  ● ON")
            except Exception as e:
                self.controller.log(f"[SMU] {ch} set_on error: {e}")

        def _smu_off():
            drv = _drv()
            if not drv:
                return
            try:
                drv.turn_output_off(ch)
                self.controller.log(f"[SMU] {ch} output OFF")
                lf.config(text=f"{ch.upper()}  ○ OFF")
            except Exception as e:
                self.controller.log(f"[SMU] {ch} off error: {e}")

        def _measure(what: str):
            drv = _drv()
            if not drv:
                return
            try:
                if what == "I":
                    val = drv.measure_current(ch)
                    reading_vars["I"].set(format_engineering(val, "A"))
                    self._smu_last[ch]["I"] = val
                    self.controller.log(f"[SMU] {ch} I = {format_engineering(val, 'A')}")
                elif what == "V":
                    val = drv.measure_voltage(ch)
                    reading_vars["V"].set(format_engineering(val, "V"))
                    self._smu_last[ch]["V"] = val
                    self.controller.log(f"[SMU] {ch} V = {format_engineering(val, 'V')}")
                elif what == "R":
                    val = drv.measure_resistance(ch)
                    reading_vars["R"].set(format_engineering(val, "Ω"))
                    self._smu_last[ch]["R"] = val
                    self.controller.log(f"[SMU] {ch} R = {format_engineering(val, 'Ω')}")
            except Exception as e:
                reading_vars[what].set("ERROR")
                self.controller.log(f"[SMU] {ch} meas_{what} error: {e}")

        self._smu_cont_active[ch] = False

        def _toggle_cont():
            if self._smu_cont_active.get(ch, False):
                self._smu_cont_active[ch] = False
                _cont_btn.config(text="▶ Cont.")
                self.controller.log(f"[SMU] {ch} continuous stopped")
            else:
                self._smu_cont_active[ch] = True
                _cont_btn.config(text="■ Stop")
                self.controller.log(f"[SMU] {ch} continuous started")
                def _loop():
                    while self._smu_cont_active.get(ch, False):
                        try:
                            ms = max(100, int(_cont_iv.get()))
                        except ValueError:
                            ms = 500
                        _meas_all()
                        time.sleep(ms / 1000)
                threading.Thread(target=_loop, daemon=True).start()
        _cont_btn.config(command=_toggle_cont)

    def _smu_check_compliance(self, which: str):
        channels = ["smua", "smub"] if which == "both" else [which]
        try:
            i_max = parse_engineering(self._smu_thr["I_max"].get())
            v_min = parse_engineering(self._smu_thr["V_min"].get())
            v_max = parse_engineering(self._smu_thr["V_max"].get())
            r_min = parse_engineering(self._smu_thr["R_min"].get())
        except ValueError:
            self._smu_comp_result.set("Bad thresholds")
            self._smu_comp_lbl.config(foreground="#dc2626")
            return

        all_pass = True
        lines = []
        for ch in channels:
            last = self._smu_last.get(ch, {})
            I = last.get("I")
            V = last.get("V")
            R = last.get("R")
            fails = []
            if I is None:
                fails.append("I not measured")
            elif abs(I) > i_max:
                fails.append(f"I={format_engineering(abs(I), 'A')} > {format_engineering(i_max, 'A')}")
            if V is None:
                fails.append("V not measured")
            elif not (v_min <= V <= v_max):
                fails.append(f"V={format_engineering(V, 'V')} not in "
                            f"[{format_engineering(v_min, 'V')}, {format_engineering(v_max, 'V')}]")
            if R is None:
                fails.append("R not measured")
            elif R < r_min:
                fails.append(f"R={format_engineering(R, 'Ω')} < {format_engineering(r_min, 'Ω')}")

            if fails:
                all_pass = False
                lines.append(f"{ch} FAIL: {'; '.join(fails)}")
                self.controller.log(f"[SMU] Compliance {ch}: FAIL — {'; '.join(fails)}")
            else:
                lines.append(f"{ch} PASS")
                self.controller.log(f"[SMU] Compliance {ch}: PASS")

        result_text = "  |  ".join(lines)
        self._smu_comp_result.set(result_text)
        self._smu_comp_lbl.config(foreground="#16a34a" if all_pass else "#dc2626")

    def _global_reset(self):
        log = self.controller.log

        for ch in list(self._smu_cont_active):
            self._smu_cont_active[ch] = False

        self._dmm_cont_active = False
        if self._dmm_status_var:
            self._dmm_status_var.set("○ IDLE")

        drv_smu = self.controller.drivers.get("smu")
        if drv_smu and drv_smu.inst:
            for ch in ("smua", "smub"):
                try:
                    drv_smu.turn_output_off(ch)
                    drv_smu.set_voltage(ch, 0)
                    log(f"[RESET] SMU {ch} OFF, level → 0 V")
                except Exception as e:
                    log(f"[RESET] SMU {ch} error: {e}")
                lv = self._smu_level_vars.get(ch)
                if lv:
                    lv.set("0.0")
                lf = self._smu_output_lf.get(ch)
                if lf:
                    try:
                        lf.config(text=f"{ch.upper()}  ○ OFF")
                    except Exception:
                        pass
                sv = self._inst_status_vars.get(ch)
                if sv:
                    sv.set(f"{ch.upper()}: ○ OFF  0 V")

        drv_wg = self.controller.drivers.get("wave_gen")
        if drv_wg and drv_wg.inst:
            for ch_num in (1, 2):
                try:
                    drv_wg.turn_output_off_ch(ch_num)
                    log(f"[RESET] WaveGen CH{ch_num} OFF")
                except Exception as e:
                    log(f"[RESET] WaveGen CH{ch_num} error: {e}")
                lf = self._wg_output_lf.get(ch_num)
                if lf:
                    try:
                        lf.config(text=f"CH {ch_num}  ○ OFF")
                    except Exception:
                        pass
                sv = self._inst_status_vars.get(f"wg{ch_num}")
                if sv:
                    sv.set(f"WG CH{ch_num}: ○ OFF")

        drv_sw = self.controller.drivers.get("switch")
        if drv_sw and drv_sw.inst:
            try:
                drv_sw.open_all()
                log("[RESET] Switch matrix: all channels open")
            except Exception as e:
                log(f"[RESET] Switch open_all error: {e}")

        log("[RESET] Global reset complete")

    def _query_all_status(self):
        def _sv(key, text):
            v = self._inst_status_vars.get(key)
            if v:
                v.set(text)

        drv_smu = self.controller.drivers.get("smu")
        if drv_smu and drv_smu.inst:
            for ch in ("smua", "smub"):
                key = ch
                try:
                    raw = drv_smu.query(f"print({ch}.source.output)")
                    is_on = str(raw).strip().startswith("1")
                    lf = self._smu_output_lf.get(ch)
                    if is_on:
                        lf and lf.config(text=f"{ch.upper()}  ● ON")
                        _sv(key, f"{ch.upper()}: ● ON")
                    else:
                        lf and lf.config(text=f"{ch.upper()}  ○ OFF")
                        _sv(key, f"{ch.upper()}: ○ OFF")
                except Exception as e:
                    _sv(key, f"{ch.upper()}: ERR")
                    self.controller.log(f"[QUERY] SMU {ch}: {e}")
        else:
            for ch in ("smua", "smub"):
                _sv(ch, f"{ch.upper()}: —")

        drv_wg = self.controller.drivers.get("wave_gen")
        if drv_wg and drv_wg.inst:
            for ch_num in (1, 2):
                key = f"wg{ch_num}"
                try:
                    raw = drv_wg.query(f"OUTPut{ch_num}?")
                    is_on = str(raw).strip() in ("1", "ON")
                    lf = self._wg_output_lf.get(ch_num)
                    if is_on:
                        lf and lf.config(text=f"CH {ch_num}  ● ON")
                        _sv(key, f"WG CH{ch_num}: ● ON")
                    else:
                        lf and lf.config(text=f"CH {ch_num}  ○ OFF")
                        _sv(key, f"WG CH{ch_num}: ○ OFF")
                except Exception as e:
                    _sv(key, f"WG CH{ch_num}: ERR")
                    self.controller.log(f"[QUERY] WaveGen CH{ch_num}: {e}")
        else:
            for ch_num in (1, 2):
                _sv(f"wg{ch_num}", f"WG CH{ch_num}: —")

        drv_dmm = self.controller.drivers.get("dmm")
        if drv_dmm and drv_dmm.inst:
            try:
                raw = drv_dmm.query(":FUNC?").strip().strip('"')
                _sv("dmm", f"DMM: {raw}")
            except Exception as e:
                _sv("dmm", "DMM: ERR")
                self.controller.log(f"[QUERY] DMM: {e}")
        else:
            _sv("dmm", "DMM: —")

        drv_prb = self.controller.drivers.get("prober")
        if drv_prb and drv_prb.inst:
            try:
                stb, desc = drv_prb.read_stb_decoded()
                Z_UP   = {67, 65, 75}
                Z_DOWN = {66, 68, 70}
                if stb in Z_UP:
                    z_str = "Z UP (contact)"
                elif stb in Z_DOWN:
                    z_str = "Z DOWN"
                else:
                    z_str = f"STB={stb}"
                _sv("prober", f"Prober: {z_str}")
            except Exception as e:
                _sv("prober", "Prober: ERR")
                self.controller.log(f"[QUERY] Prober: {e}")
        else:
            _sv("prober", "Prober: —")

    def _build_wavegen_card(self, parent):
        card = ttk.LabelFrame(parent, text="Keysight 33512B  (Wave Gen)")
        card.pack(fill="both", expand=True, padx=6, pady=6)

        ttk.Label(
            card, text="Addr: GPIB0::12::INSTR",
            foreground="gray", font=("Consolas", 8)
        ).pack(anchor="w", padx=6, pady=(4, 0))

        ch_frame = ttk.Frame(card)
        ch_frame.pack(fill="x", padx=6, pady=(4, 0))
        ch_frame.columnconfigure(0, weight=1)
        ch_frame.columnconfigure(1, weight=1)

        for idx, ch_num in enumerate((1, 2)):
            self._build_wavegen_channel(ch_frame, ch_num, col=idx)

        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=6, pady=8)
        self._scpi_row(card, "wave_gen")

    def _build_wavegen_channel(self, parent, ch: int, col: int):
        lf = ttk.LabelFrame(parent, text=f"CH {ch}  ○ OFF", padding=(8, 6))
        lf.grid(row=0, column=col, sticky="nsew",
                padx=(0 if col == 0 else 6, 0), pady=0)
        self._wg_output_lf[ch] = lf

        shape_var  = tk.StringVar(value="SIN")
        freq_var   = tk.StringVar(value="1000")
        amp_var    = tk.StringVar(value="1.0")
        offset_var = tk.StringVar(value="0.0")

        sh_row = ttk.Frame(lf)
        sh_row.pack(fill="x", pady=(4, 3))
        ttk.Label(sh_row, text="Shape:", width=8, anchor="e").pack(side="left")
        ttk.Combobox(sh_row, textvariable=shape_var,
                     values=["SIN", "SQU", "RAMP", "PULS", "NOIS", "DC"],
                     width=7, state="readonly").pack(side="left", padx=4)

        for lbl, var, unit in [("Freq:", freq_var, "Hz"),
                                ("Amp:", amp_var, "Vpp"),
                                ("Offset:", offset_var, "V")]:
            f = ttk.Frame(lf)
            f.pack(fill="x", pady=2)
            ttk.Label(f, text=lbl, width=8, anchor="e").pack(side="left")
            ttk.Entry(f, textvariable=var, width=9).pack(side="left", padx=4)
            ttk.Label(f, text=unit).pack(side="left")

        def _drv():
            drv = self.controller.drivers.get("wave_gen")
            if not drv or not drv.inst:
                self.controller.log(f"[WAVEGEN] CH{ch}: not connected")
                return None
            return drv

        def _apply():
            drv = _drv()
            if not drv:
                return
            try:
                freq = parse_engineering(freq_var.get())
                amp = parse_engineering(amp_var.get())
                offset = parse_engineering(offset_var.get())
                drv.set_waveform_ch(ch, shape_var.get(), freq, amp, offset)
                self.controller.log(
                    f"[WAVEGEN] CH{ch} {shape_var.get()} {format_engineering(freq, 'Hz')}  "
                    f"{format_engineering(amp, 'Vpp')}  offset={format_engineering(offset, 'V')}"
                )
            except Exception as e:
                self.controller.log(f"[WAVEGEN] CH{ch} apply error: {e}")

        def _on():
            drv = _drv()
            if not drv:
                return
            try:
                drv.turn_output_on_ch(ch)
                self.controller.log(f"[WAVEGEN] CH{ch} ON")
                lf.config(text=f"CH {ch}  ● ON")
            except Exception as e:
                self.controller.log(f"[WAVEGEN] CH{ch} on error: {e}")

        def _off():
            drv = _drv()
            if not drv:
                return
            try:
                drv.turn_output_off_ch(ch)
                self.controller.log(f"[WAVEGEN] CH{ch} OFF")
                lf.config(text=f"CH {ch}  ○ OFF")
            except Exception as e:
                self.controller.log(f"[WAVEGEN] CH{ch} off error: {e}")

        ttk.Button(lf, text="Apply", command=_apply).pack(fill="x", pady=(8, 2))
        out_row = ttk.Frame(lf)
        out_row.pack(fill="x", pady=2)
        ttk.Button(out_row, text="Output ON",  command=_on).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(out_row, text="Output OFF", command=_off).pack(side="left", expand=True, fill="x", padx=(2, 0))

    def _scpi_row(self, parent, driver_key):
        cmd_var  = tk.StringVar()
        resp_var = tk.StringVar(value="")

        row = ttk.Frame(parent)
        row.pack(fill="x", padx=6, pady=2)
        ttk.Label(row, text="SCPI:").pack(side="left")
        ttk.Entry(row, textvariable=cmd_var, width=22).pack(side="left", padx=4, fill="x", expand=True)

        def send():
            cmd = cmd_var.get().strip()
            if not cmd:
                return
            drv = self.controller.drivers.get(driver_key)
            if not drv or not drv.inst:
                resp_var.set("NOT CONNECTED"); return
            try:
                if cmd.strip().endswith("?"):
                    resp = drv.query(cmd); resp_var.set(resp or "")
                else:
                    drv.write(cmd); resp_var.set("OK")
                self.controller.log(f"[{driver_key.upper()}] {cmd}  →  {resp_var.get()}")
            except Exception as e:
                resp_var.set(f"ERR: {e}")

        ttk.Button(row, text="Send", command=send).pack(side="left")

        resp_row = ttk.Frame(parent)
        resp_row.pack(fill="x", padx=6, pady=(0, 8))
        ttk.Label(resp_row, text="Resp:").pack(side="left")
        ttk.Label(resp_row, textvariable=resp_var, foreground="#0055aa",
                  font=("Consolas", 9)).pack(side="left", padx=4)

    def _wafer_map_source_choices(self) -> list:
        return [k for k in WAFER_MAP_SOURCES if k == "GDS" or k.lower() == self._system]

    def _tab_wafer_map(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="ATA Folder")
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        ctrl = ttk.Frame(tab)
        ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))

        ttk.Button(ctrl, text="📁 Load ATA Folder…",
                  command=self.controller.cmd_import_map).pack(side="left", padx=(0, 10))
        self._ata_path_lbl = ttk.Label(ctrl, text="No folder selected", foreground="gray")
        self._ata_path_lbl.pack(side="left", padx=10)

        ttk.Label(ctrl, text="Map source:").pack(side="right", padx=(4, 2))
        self._map_source_var = tk.StringVar(value="GDS")
        map_source_cb = ttk.Combobox(ctrl, textvariable=self._map_source_var,
                                     values=self._wafer_map_source_choices(), state="readonly",
                                     width=10)
        map_source_cb.pack(side="right")
        map_source_cb.bind("<<ComboboxSelected>>", lambda _e: self._reload_wafer_map_source())

        split = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        split.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 6))

        list_frame = ttk.LabelFrame(split, text="ATA Files", width=240)
        split.add(list_frame, weight=0)
        list_frame.pack_propagate(False)

        cols = ("status", "file", "description")
        self._ata_tree = ttk.Treeview(
            list_frame, columns=cols, show="headings", height=20, selectmode="browse"
        )
        self._ata_tree.heading("status",      text="")
        self._ata_tree.heading("file",        text="File")
        self._ata_tree.heading("description", text="Contents")
        self._ata_tree.column("status",      width=24,  stretch=False, anchor="center")
        self._ata_tree.column("file",        width=170, stretch=False)
        self._ata_tree.column("description", width=160)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._ata_tree.yview)
        self._ata_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._ata_tree.pack(fill="both", expand=True)

        self._ata_tree.tag_configure("found",   foreground="#006400")
        self._ata_tree.tag_configure("missing", foreground="#999999")
        self._ata_tree.tag_configure("other",   foreground="#333333")

        self.wafer_map = WaferMapPanel(split)
        split.add(self.wafer_map, weight=1)

    def load_ata_folder(self, folder_path):
        self._ata_folder = folder_path
        self._ata_path_lbl.config(text=folder_path, foreground="black")
        self._pad_custom_loaded = False

        self.pin_wiring.load_from_ata(folder_path)

        all_files = {f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))}

        for item in self._ata_tree.get_children():
            self._ata_tree.delete(item)

        self._ata_tree.insert("", "end", values=("", "── Key ATA Files ──", ""), tags=("other",))
        for fname, (desc, owner) in ATA_KEY_FILES.items():
            if owner not in ("shared", self._system):
                continue
            if fname in all_files:
                self._ata_tree.insert("", "end", values=("✔", fname, desc), tags=("found",))
            else:
                self._ata_tree.insert("", "end", values=("–", fname, desc), tags=("missing",))

        active_card = self.pin_wiring.get_active_card()
        card_names = sorted(self.pin_wiring.get_card_names())
        if card_names:
            self._ata_tree.insert("", "end",
                                  values=("", "── Probe Cards ──", ""), tags=("other",))
            for name in card_names:
                n_recipes = self.pin_wiring.get_recipe_count(name)
                mark = "  (active)" if name == active_card else ""
                self._ata_tree.insert(
                    "", "end",
                    values=("✔", name + mark, f"{n_recipes} recipe(s)"),
                    tags=("found",))
        else:
            self._ata_tree.insert(
                "", "end",
                values=("–", "probe_cards/", "No probe cards yet — create one on Pad to Probe"),
                tags=("missing",))

        others = sorted(f for f in all_files if f not in ATA_KEY_FILES)
        if others:
            self._ata_tree.insert("", "end", values=("", "── Other Files ──", ""), tags=("other",))
            for fname in others:
                self._ata_tree.insert("", "end", values=("", fname, ""), tags=("other",))

        n_dies = self.wafer_map.load_from_ata(
            folder_path, filename=WAFER_MAP_SOURCES[self._map_source_var.get()])

        self.load_pad_layout(folder_path)
        self._on_pad_source_change()
        self.load_alignment_marks(folder_path)

        accr_wafer = getattr(self, "accr_wafer", None)
        if accr_wafer is not None:
            accr_wafer.load_from_ata(folder_path)
        self.pma_wafer.load_from_ata(folder_path)
        self._exec2_map_folder = folder_path
        self._exec2_map_source_var.set("Accretech" if self._system == "accretech" else "GDS")
        self._exec2_draw_wafer_map(quiet_if_missing=True)
        self._refresh_export_formats()

        nanoz = getattr(self, "nanoz_panel", None)
        if nanoz is not None:
            try:
                nanoz.on_ata_folder_loaded(folder_path)
            except Exception:
                pass

        return n_dies

    def _reload_wafer_map_source(self):
        if not self._ata_folder:
            return
        filename = WAFER_MAP_SOURCES[self._map_source_var.get()]
        n = self.wafer_map.load_from_ata(self._ata_folder, filename=filename)
        self.controller.log(f"[WAFER MAP] Loaded {n} dies from {filename}")

    def _build_alignment_panel(self):
        tab = ttk.Frame(self)
        tab.rowconfigure(1, weight=1)
        tab.rowconfigure(2, weight=0)
        tab.columnconfigure(0, weight=1)

        ctrl = ttk.Frame(tab)
        ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        self._align_path_lbl = ttk.Label(ctrl, text="No folder selected", foreground="gray")
        self._align_path_lbl.pack(side="left", padx=10)
        ttk.Button(
            ctrl, text="✓  Lock Alignment",
            command=self.controller.cmd_align
        ).pack(side="right", padx=4)
        ttk.Button(
            ctrl, text="🔄  Run Handshake",
            command=self._run_alignment_handshake
        ).pack(side="right", padx=4)

        split = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        split.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 4))

        list_frame = ttk.LabelFrame(split, text="Marks", width=240)
        split.add(list_frame, weight=0)
        list_frame.pack_propagate(False)

        cols = ("mark", "x", "y", "type")
        self._align_tree = ttk.Treeview(
            list_frame, columns=cols, show="headings", height=20, selectmode="browse"
        )
        self._align_tree.heading("mark", text="Mark")
        self._align_tree.heading("x",    text="X (mm)")
        self._align_tree.heading("y",    text="Y (mm)")
        self._align_tree.heading("type", text="Type")
        self._align_tree.column("mark", width=80)
        self._align_tree.column("x",    width=65, anchor="e")
        self._align_tree.column("y",    width=65, anchor="e")
        self._align_tree.column("type", width=80)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._align_tree.yview)
        self._align_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._align_tree.pack(fill="both", expand=True)

        self.align_panel = AlignmentPanel(split)
        split.add(self.align_panel, weight=1)

        result_bar = ttk.LabelFrame(tab, text="Computed Alignment Transform")
        result_bar.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 6))
        for col_idx in range(4):
            result_bar.columnconfigure(col_idx, weight=1)
        self._align_dx_lbl = ttk.Label(result_bar, text="ΔX:  —", font=("Consolas", 10))
        self._align_dy_lbl = ttk.Label(result_bar, text="ΔY:  —", font=("Consolas", 10))
        self._align_th_lbl = ttk.Label(result_bar, text="θ:   —", font=("Consolas", 10))
        self._align_st_lbl = ttk.Label(result_bar, text="Status: waiting for handshake",
                                       foreground="gray", font=("Consolas", 9))
        self._align_dx_lbl.grid(row=0, column=0, padx=14, pady=6, sticky="w")
        self._align_dy_lbl.grid(row=0, column=1, padx=14, pady=6, sticky="w")
        self._align_th_lbl.grid(row=0, column=2, padx=14, pady=6, sticky="w")
        self._align_st_lbl.grid(row=0, column=3, padx=14, pady=6, sticky="w")

    def load_alignment_marks(self, folder_path):
        self._align_path_lbl.config(text=folder_path, foreground="black")
        marks = self.align_panel.load_from_ata(folder_path)

        for item in self._align_tree.get_children():
            self._align_tree.delete(item)

        if not marks:
            return marks

        sample = marks[0]
        n_key = next((k for k in ("name", "mark_id", "mark", "id", "label") if k in sample), None)
        x_key = next((k for k in ("x_mm", "x_um", "x", "pos_x") if k in sample), None)
        y_key = next((k for k in ("y_mm", "y_um", "y", "pos_y") if k in sample), None)
        t_key = next((k for k in ("type", "mark_type", "kind") if k in sample), None)

        for m in marks:
            self._align_tree.insert("", "end", values=(
                m.get(n_key, "") if n_key else "",
                m.get(x_key, "") if x_key else "",
                m.get(y_key, "") if y_key else "",
                m.get(t_key, "") if t_key else "",
            ))
        return marks

    def _run_alignment_handshake(self):
        import random

        marks = self.align_panel._last_marks
        if not marks:
            self.controller.log("[ALIGN] No alignment marks loaded.")
            self._align_st_lbl.config(text="Status: no marks loaded", foreground="red")
            return
        if len(marks) < 2:
            self.controller.log("[ALIGN] Need at least 2 marks for a full transform.")
            self._align_st_lbl.config(text="Status: need ≥ 2 marks", foreground="red")
            return

        prober = self.controller.drivers.get("prober")

        sample = marks[0]
        n_key = next((k for k in ("mark_name", "name", "mark_id", "mark", "id", "label") if k in sample), None)
        x_key = next((k for k in ("x_um", "x_mm", "x", "pos_x", "stage_x") if k in sample), None)
        y_key = next((k for k in ("y_um", "y_mm", "y", "pos_y", "stage_y") if k in sample), None)

        if not (x_key and y_key):
            self.controller.log("[ALIGN] Cannot identify X/Y columns in alignment marks.")
            self._align_st_lbl.config(text="Status: bad mark format", foreground="red")
            return

        expected = []
        measured = []

        self._align_st_lbl.config(text="Status: running…", foreground="#2563eb")
        self.update_idletasks()

        for i, mark in enumerate(marks[:2]):
            try:
                ex = float(mark.get(x_key, 0))
                ey = float(mark.get(y_key, 0))
            except (ValueError, TypeError):
                self.controller.log(f"[ALIGN] Mark {i+1}: invalid coordinates — skipping.")
                continue
            name = (mark.get(n_key, "") if n_key else "") or f"Mark {i+1}"
            expected.append((ex, ey))

            self.align_panel.highlight_mark(i)

            if prober:
                try:
                    self.controller.log(f"[ALIGN] A {ex:.1f} {ey:.1f} → driving to {name}")
                    prober.move_xy_absolute(ex, ey)
                except Exception as e:
                    self.controller.log(f"[ALIGN] Prober move error: {e}")
                    self._align_st_lbl.config(text=f"Status: prober error — mark {i+1}", foreground="red")
                    return
            else:
                self.controller.log(f"[ALIGN] (sim) A {ex:.1f} {ey:.1f} → {name}")

            self._show_jog_popup(i + 1, name, ex, ey, prober is not None)

            if prober:
                try:
                    raw = prober.get_xy_position()
                    mx, my = _parse_q_response(raw)
                    self.controller.log(f"[ALIGN] Q → mark {i+1} actual X={mx:.1f}  Y={my:.1f} µm")
                except Exception as e:
                    self.controller.log(f"[ALIGN] Q read error: {e}")
                    self._align_st_lbl.config(text=f"Status: Q error — mark {i+1}", foreground="red")
                    return
            else:
                mx = ex + random.uniform(-5.0, 5.0)
                my = ey + random.uniform(-5.0, 5.0)
                self.controller.log(f"[ALIGN] (sim) Q → mark {i+1} actual X={mx:.1f}  Y={my:.1f} µm")

            measured.append((mx, my))

        if len(expected) < 2 or len(measured) < 2:
            self._align_st_lbl.config(text="Status: insufficient data", foreground="red")
            return

        dx, dy, theta_deg = _compute_alignment_transform(expected, measured)
        self.controller.log(
            f"[ALIGN] Result: ΔX={dx:+.2f} µm  ΔY={dy:+.2f} µm  θ={theta_deg:+.4f}°"
        )

        self._align_dx_lbl.config(text=f"ΔX:  {dx:+.2f} µm")
        self._align_dy_lbl.config(text=f"ΔY:  {dy:+.2f} µm")
        self._align_th_lbl.config(text=f"θ:   {theta_deg:+.4f}°")
        self._align_st_lbl.config(text="Status: ✓ complete", foreground="green")

        if hasattr(self, "exec_panel"):
            self.exec_panel.alignment.update({
                "offset_x_um": dx,
                "offset_y_um": dy,
                "theta_deg":   theta_deg,
                "confidence":  99.0,
            })

        self.align_panel.show_alignment_result(dx, dy, theta_deg)

    def _show_jog_popup(self, mark_num, mark_name, ex, ey, real_prober):
        dlg = tk.Toplevel(self)
        dlg.title(f"Alignment — Mark {mark_num}")
        dlg.resizable(False, False)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        tk.Label(
            dlg, text=f"Prober moved to  {mark_name}",
            font=("Segoe UI", 12, "bold"),
        ).pack(pady=(18, 4), padx=28)
        tk.Label(
            dlg, text=f"Expected:   X = {ex:.1f} µm,   Y = {ey:.1f} µm",
            font=("Consolas", 9), foreground="#555555",
        ).pack(padx=28, pady=(0, 12))

        body = (
            "Use the prober joystick / arrow keys to centre\n"
            "the alignment mark under the microscope.\n\n"
            "Click  OK  when the mark is centred."
            if real_prober else
            "[ SIMULATION — no prober connected ]\n\n"
            "In production: jog the chuck to centre the mark.\n"
            "Click  OK  to continue with a simulated position."
        )
        tk.Label(dlg, text=body, font=("Segoe UI", 10), justify="center").pack(padx=28, pady=4)

        ttk.Button(dlg, text="  OK  ", command=dlg.destroy, width=14).pack(pady=(14, 20))

        dlg.update_idletasks()
        pw = self.winfo_toplevel()
        x = pw.winfo_x() + (pw.winfo_width()  - dlg.winfo_width())  // 2
        y = pw.winfo_y() + (pw.winfo_height() - dlg.winfo_height()) // 2
        dlg.geometry(f"+{x}+{y}")
        dlg.wait_window()

    def _tab_pad_layout(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Pad to Probe")
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        ctrl = ttk.Frame(tab)
        ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        self._pad_path_lbl = ttk.Label(ctrl, text="No folder selected", foreground="gray")
        self._pad_path_lbl.pack(side="left", padx=10)
        ttk.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(ctrl, text="Layout:").pack(side="left")
        self._pad_source_var = tk.StringVar(value="Custom")
        pad_source_cb = ttk.Combobox(ctrl, textvariable=self._pad_source_var,
                                     values=["ATA", "Custom"], state="readonly", width=8)
        pad_source_cb.pack(side="left", padx=(4, 8))
        pad_source_cb.bind("<<ComboboxSelected>>", lambda _e: self._on_pad_source_change())
        self._btn_pad_clear = ttk.Button(ctrl, text="🗑 Clear", state="disabled",
                                         command=self._clear_custom_pads)
        self._btn_pad_clear.pack(side="left", padx=2)
        self._btn_pad_save = ttk.Button(ctrl, text="💾 Save Custom", state="disabled",
                                        command=self._save_custom_pads)
        self._btn_pad_save.pack(side="left", padx=2)
        self._btn_pad_add_die = ttk.Button(ctrl, text="▭ Add Die", state="disabled",
                                           command=self._add_custom_die)
        self._btn_pad_add_die.pack(side="left", padx=2)
        ttk.Label(ctrl, text="Custom Sketch",
                 foreground="#6b7280", wraplength=420, justify="left").pack(side="left", padx=(10, 0))

        split = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        split.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 6))

        left_col = ttk.PanedWindow(split, orient=tk.VERTICAL, width=310)
        split.add(left_col, weight=0)

        list_frame = ttk.LabelFrame(left_col, text="Pads")
        left_col.add(list_frame, weight=1)

        cols = ("pad", "net", "x", "y")
        self._pad_tree = ttk.Treeview(
            list_frame, columns=cols, show="headings", height=10, selectmode="browse"
        )
        self._pad_tree.heading("pad", text="Pad")
        self._pad_tree.heading("net", text="Net")
        self._pad_tree.heading("x",   text="X (µm)")
        self._pad_tree.heading("y",   text="Y (µm)")
        self._pad_tree.column("pad", width=80)
        self._pad_tree.column("net", width=95)
        self._pad_tree.column("x",   width=65, anchor="e")
        self._pad_tree.column("y",   width=65, anchor="e")

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._pad_tree.yview)
        self._pad_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._pad_tree.pack(fill="both", expand=True)

        self.pin_wiring = ProbeCardWiringFrame(
            left_col,
            get_folder=lambda: self._ata_folder,
            log_fn=self.controller.log,
            on_card_change=self._on_probe_card_change,
            on_pins_change=lambda: self.pad_panel.refresh_pins(),
            system=self._system,
        )
        left_col.add(self.pin_wiring, weight=1)

        self.pad_panel = PadLayoutPanel(split, on_custom_change=self._refresh_pad_tree_from_custom,
                                        get_pins=self.pin_wiring.get_wiring)
        split.add(self.pad_panel, weight=1)

        self._on_pad_source_change()

    def _on_pad_source_change(self):
        source = self._pad_source_var.get()
        if source == "Custom":
            if not self._pad_custom_loaded and self._ata_folder:
                self.pad_panel.load_custom(self._ata_folder)
                self._pad_custom_loaded = True
            self.pad_panel.set_source("custom")
            self._btn_pad_clear.config(state="normal")
            self._btn_pad_save.config(state="normal")
            self._btn_pad_add_die.config(state="normal")
            self._refresh_pad_tree_from_custom()
        else:
            self.pad_panel.set_source("ata")
            self._btn_pad_clear.config(state="disabled")
            self._btn_pad_save.config(state="disabled")
            self._btn_pad_add_die.config(state="disabled")
            self._populate_pad_tree_from_ata(self.pad_panel._last_pads or [])

    def _refresh_pad_tree_from_custom(self):
        for item in self._pad_tree.get_children():
            self._pad_tree.delete(item)
        for pad in self.pad_panel._custom_pads:
            self._pad_tree.insert("", "end", values=(pad["name"], "", pad["x"], pad["y"]))

    def _populate_pad_tree_from_ata(self, pads: list):
        for item in self._pad_tree.get_children():
            self._pad_tree.delete(item)
        if not pads:
            return 0
        sample = pads[0]
        n_key   = next((k for k in ("pad_name", "name", "label", "pad") if k in sample), None)
        net_key = next((k for k in ("net_name", "net", "signal") if k in sample), None)
        x_key   = next((k for k in ("x_um", "x_mm", "x", "center_x") if k in sample), None)
        y_key   = next((k for k in ("y_um", "y_mm", "y", "center_y") if k in sample), None)
        for p in pads:
            self._pad_tree.insert("", "end", values=(
                p.get(n_key, "")   if n_key   else "",
                p.get(net_key, "") if net_key else "",
                p.get(x_key, "")  if x_key   else "",
                p.get(y_key, "")  if y_key   else "",
            ))
        return len(pads)

    def _clear_custom_pads(self):
        from tkinter import messagebox
        if not messagebox.askyesno("Clear Custom Layout",
                                   "Delete every pad and die in the hand-drawn custom layout?"):
            return
        self.pad_panel.clear_custom()

    def _add_custom_die(self):
        self.pad_panel.add_die()

    def _save_custom_pads(self):
        if not self._ata_folder:
            from tkinter import messagebox
            messagebox.showerror("No ATA Folder", "Load an ATA folder from the toolbar first.")
            return
        path = self.pad_panel.save_custom(self._ata_folder)
        self._pad_custom_loaded = True
        self.controller.log(f"[PAD] Custom layout saved to {path}")

    def _on_probe_card_change(self, card_name: str):
        if not hasattr(self, "recipe_panel"):
            return
        self.recipe_panel.load_recipes(card_name, self.pin_wiring.get_recipes())
        self.recipe_panel.refresh_connections()
        if getattr(self, "_exec2_steps", None):
            self._exec2_steps = []
            self._exec2_steps_tree.delete(*self._exec2_steps_tree.get_children())
            self._exec2_steps_var.set("No recipe loaded")
            self._exec2_recipe_var.set("")
            self.controller.log(
                "[RUN] Probe card changed — cleared the loaded recipe "
                "(⟳ Load Recipe again for the new card).")
        if hasattr(self.controller, "check_system_ready"):
            self.controller.check_system_ready()

    def load_pad_layout(self, folder_path):
        self._pad_path_lbl.config(text=folder_path, foreground="black")
        pads = self.pad_panel.load_from_ata(folder_path)
        return self._populate_pad_tree_from_ata(pads)

    def _tab_gds_parser(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="GDS Parser")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.gds_panel = GdsParserPanel(tab, controller=self.controller)
        self.gds_panel.grid(row=0, column=0, sticky="nsew")

    def _tab_recipe(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Recipe")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.recipe_panel = RecipePanel(
            tab, controller=self.controller, system=self._system,
            get_pins=lambda: (self.pin_wiring.get_pin_choices()
                              if hasattr(self, "pin_wiring") else []),
            get_wiring=lambda: (self.pin_wiring.get_wiring()
                                if hasattr(self, "pin_wiring") else []),
            get_active_card=lambda: (self.pin_wiring.get_active_card()
                                     if hasattr(self, "pin_wiring") else ""),
            save_recipes=lambda card, recipes: (
                self.pin_wiring.save_recipes(card, recipes)
                if hasattr(self, "pin_wiring") else False))
        self.recipe_panel.grid(row=0, column=0, sticky="nsew")

    def _tab_switch_settings(self, nb):
        tab = ttk.Frame(nb)
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        if self._system == "accretech":
            nb.add(tab, text="Switch Settings")
            self.switch_settings = SwitchSettingsPanel(tab, controller=self.controller)
            self.switch_settings.grid(row=0, column=0, sticky="nsew")
        else:
            nb.add(tab, text="Switch Debug")
            self.switch_debug = SwitchboxTestPanel(tab, controller=self.controller)
            self.switch_debug.grid(row=0, column=0, sticky="nsew")

    def _tab_instruments_eg(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Instruments")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.instruments_eg = InstrumentsEgPanel(tab, controller=self.controller)
        self.instruments_eg.grid(row=0, column=0, sticky="nsew")

    def _tab_probe_routing(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Probe Routing")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        holder, self.probe_routing = scrollable_routing(tab, self.controller)
        holder.grid(row=0, column=0, sticky="nsew")

    def _tab_prober_debug(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Prober Debug")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.prober_debug = ProberDebugPanel(tab, controller=self.controller)
        self.prober_debug.grid(row=0, column=0, sticky="nsew")

    def _tab_cassette(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Cassette")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.cassette_panel = CassettePanel(tab, controller=self.controller)
        self.cassette_panel.grid(row=0, column=0, sticky="nsew")

    def _tab_accr_wafer(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Accr Wafer")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.accr_wafer = AccrWaferPanel(tab, controller=self.controller,
                                         get_folder=lambda: self._ata_folder)
        self.accr_wafer.grid(row=0, column=0, sticky="nsew")

    def _tab_pma_wafer(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="PMA")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.pma_wafer = PmaWaferPanel(tab, controller=self.controller,
                                       get_folder=lambda: self._ata_folder)
        self.pma_wafer.grid(row=0, column=0, sticky="nsew")

    def _build_exec_panel(self):
        tab = ttk.Frame(self)
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.exec_panel = ExecutionDashboard(
            tab,
            log_fn=self.controller.log,
            on_stats_change=self.controller.on_exec_stats_change,
        )
        self.exec_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _tab_execution2(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="▶  Run")
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        self._exec2_running  = False
        self._exec2_aborted  = False
        self._exec2_run_mode = None
        self._exec2_die_num  = 0
        self._exec2_total_dies = 0
        self._exec2_steps    = []
        self._exec2_current_rc = None
        self._exec2_pma_row_offset = 0
        self._exec2_pma_col_offset = 0
        self._exec2_pma_offset_confirmed = False
        self._exec2_current_pma_shot = None

        ctrl = tk.Frame(tab, bg="#f1f5f9", relief="solid", bd=1)
        ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))

        tk.Label(ctrl, text="Recipe:", bg="#f1f5f9").pack(side="left", padx=(10, 2), pady=6)
        self._exec2_recipe_var = tk.StringVar()
        self._exec2_recipe_cb = ttk.Combobox(
            ctrl, textvariable=self._exec2_recipe_var, width=20, state="readonly",
            postcommand=lambda: self._exec2_recipe_cb.config(
                values=self.recipe_panel.get_recipe_names()))
        self._exec2_recipe_cb.pack(side="left", pady=6)
        ttk.Button(ctrl, text="⟳ Load Recipe",
                   command=self._exec2_load_recipe).pack(side="left", padx=4, pady=5)

        ttk.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)

        self._exec2_full_btn = ttk.Button(
            ctrl, text="▶  Full Die", command=self._exec2_start_full_die)
        self._exec2_full_btn.pack(side="left", padx=4, pady=5)
        self._exec2_test_btn = ttk.Button(
            ctrl, text="▶  Test Die", command=self._exec2_start_test_die)
        self._exec2_test_btn.pack(side="left", padx=2, pady=5)
        self._exec2_test_pma_btn = ttk.Button(
            ctrl, text="▶  Test PMA", command=self._exec2_start_test_pma)
        self._exec2_test_pma_btn.pack(side="left", padx=2, pady=5)

        ttk.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)
        ttk.Button(ctrl, text="Touchdown/Measure",
                   command=self._exec2_touchdown_measure).pack(side="left", padx=2, pady=5)


        for label, cmd in [
            ("⬆  Z Up",       self._exec2_manual_z_up),
            ("⬇  Z Down",     self._exec2_manual_z_down),
            ("⏮  First Die (G)", self._exec2_manual_go_to_start),
            ("▶▶  Next Die",   self._exec2_manual_next_die),
            ("📍  XY",         self._exec2_get_xy),
            ("⏏  Unload (U)",  self._exec2_manual_unload),
            ("⏹  Stop Run",       self._exec2_abort),
        ]:
            ttk.Button(ctrl, text=label, command=cmd).pack(side="left", padx=3, pady=5)

        self._exec2_state_lbl = tk.Label(
            ctrl, text="IDLE", bg="#f1f5f9", fg="#6b7280",
            font=("Segoe UI", 11, "bold"))
        self._exec2_state_lbl.pack(side="right", padx=12)

        body = ttk.PanedWindow(tab, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 6))

        left_col = ttk.Frame(body)
        body.add(left_col, weight=1)
        left_col.rowconfigure(0, weight=0)
        left_col.rowconfigure(1, weight=1)
        left_col.columnconfigure(0, weight=1)

        pos_lf = ttk.LabelFrame(left_col, text="Chuck Position", padding=10)
        pos_lf.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        pos_lf.columnconfigure(0, weight=1)

        self._exec2_xy_var = tk.StringVar(value="X: —\nY: —")
        ttk.Label(pos_lf, textvariable=self._exec2_xy_var,
                  font=("Consolas", 16, "bold"), foreground="#0077cc",
                  justify="center").pack(expand=True)

        ttk.Separator(pos_lf, orient="horizontal").pack(fill="x", pady=8)

        self._exec2_die_var = tk.StringVar(value="Die: —")
        ttk.Label(pos_lf, textvariable=self._exec2_die_var,
                  font=("Consolas", 10), foreground="#374151",
                  justify="center").pack()

        self._exec2_step_var = tk.StringVar(value="Step: —")
        ttk.Label(pos_lf, textvariable=self._exec2_step_var,
                  font=("Consolas", 10), foreground="#6b7280",
                  justify="center").pack(pady=(2, 8))

        ttk.Button(pos_lf, text="↻  Refresh XY",
                   command=self._exec2_get_xy).pack(fill="x")
        ttk.Button(pos_lf, text="Reset Counts",
                   command=self._exec2_reset_counts).pack(fill="x", pady=(4, 0))

        steps_lf = ttk.LabelFrame(left_col, text="Recipe Steps", padding=(6, 4))
        steps_lf.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        steps_lf.rowconfigure(1, weight=1)
        steps_lf.columnconfigure(0, weight=1)

        self._exec2_steps_var = tk.StringVar(value="No recipe loaded")
        ttk.Label(steps_lf, textvariable=self._exec2_steps_var,
                  font=("Consolas", 8), foreground="#6b7280").grid(
                  row=0, column=0, sticky="w", pady=(0, 2))

        cols = ("n", "name", "type", "conn")
        self._exec2_steps_tree = ttk.Treeview(
            steps_lf, columns=cols, show="headings", height=5, selectmode="browse")
        for cid, text, width in (("n", "#", 24), ("name", "Name", 78),
                                 ("type", "Type", 68), ("conn", "Conn", 100)):
            self._exec2_steps_tree.heading(cid, text=text)
            self._exec2_steps_tree.column(cid, width=width,
                                          anchor="center" if cid == "n" else "w")
        self._exec2_steps_tree.grid(row=1, column=0, sticky="nsew")
        ssb = ttk.Scrollbar(steps_lf, orient="vertical",
                            command=self._exec2_steps_tree.yview)
        ssb.grid(row=1, column=1, sticky="ns")
        self._exec2_steps_tree.configure(yscrollcommand=ssb.set)

        map_lf = ttk.LabelFrame(body, text="Wafer Map")
        body.add(map_lf, weight=2)
        map_lf.rowconfigure(1, weight=1)
        map_lf.columnconfigure(0, weight=1)

        map_bar = ttk.Frame(map_lf)
        map_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        ttk.Button(map_bar, text="📂 Load Wafer Map",
                   command=self._exec2_load_wafer_map).pack(side="left")
        self._exec2_map_folder = None
        self._exec2_map_source_var = tk.StringVar(value="GDS")
        exec2_source_cb = ttk.Combobox(map_bar, textvariable=self._exec2_map_source_var,
                                       values=self._wafer_map_source_choices(), state="readonly",
                                       width=10)
        exec2_source_cb.pack(side="left", padx=(8, 0))
        exec2_source_cb.bind("<<ComboboxSelected>>",
                             lambda _e: self._exec2_reload_wafer_map_source())
        self._exec2_map_path_var = tk.StringVar(value="No wafer map loaded")
        ttk.Label(map_bar, textvariable=self._exec2_map_path_var,
                  foreground="#6b7280", font=("Segoe UI", 8)).pack(
                  side="left", padx=8)

        ttk.Separator(map_bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(map_bar, text="🎲 Randomize 5",
                   command=self._exec2_randomize_sites).pack(side="left")
        self._exec2_sites_var = tk.StringVar(value="Test sites: 0 picked (click dies to add/remove)")
        ttk.Label(map_bar, textvariable=self._exec2_sites_var,
                  foreground="#6b7280", font=("Segoe UI", 8)).pack(
                  side="left", padx=8)

        ttk.Separator(map_bar, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(map_bar, text="🔀 Compare/Merge PMA…",
                   command=self._exec2_open_pma_compare_dialog).pack(side="left")

        self._exec2_wafer_map = WaferMapPanel(map_lf)
        self._exec2_wafer_map.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self._exec2_wafer_map.enable_picking(on_change=self._exec2_on_sites_changed)

        stat_lf = ttk.LabelFrame(body, text="Pass / Fail", padding=10)
        body.add(stat_lf, weight=1)
        stat_lf.columnconfigure(0, weight=1)

        self._exec2_pass_var = tk.IntVar(value=0)
        self._exec2_fail_var = tk.IntVar(value=0)

        for var, label, color in [
            (self._exec2_pass_var, "PASS", "#00a800"),
            (self._exec2_fail_var, "FAIL", "#dc2626"),
        ]:
            row_f = ttk.Frame(stat_lf)
            row_f.pack(fill="x", pady=4)
            ttk.Label(row_f, text=label, width=6,
                      font=("Segoe UI", 10, "bold"),
                      foreground=color).pack(side="left")
            ttk.Label(row_f, textvariable=var,
                      font=("Consolas", 24, "bold"),
                      foreground=color).pack(side="left", padx=8)

        ttk.Separator(stat_lf, orient="horizontal").pack(fill="x", pady=8)

        self._exec2_pct_var = tk.StringVar(value="Yield:  —")
        ttk.Label(stat_lf, textvariable=self._exec2_pct_var,
                  font=("Consolas", 13, "bold"), foreground="#374151").pack()


    def _exec2_log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.controller.log(f"{ts}  {msg}")

    def _exec2_load_wafer_map(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory(
            title="Select ATA Output Folder (Wafer Map)",
            initialdir=self._ata_folder or os.getcwd())
        if not folder:
            return
        self._exec2_map_folder = folder
        self._exec2_draw_wafer_map()

    def _exec2_reload_wafer_map_source(self):
        if self._exec2_map_folder:
            self._exec2_draw_wafer_map()

    def _exec2_draw_wafer_map(self, quiet_if_missing: bool = False):
        folder = self._exec2_map_folder
        filename = WAFER_MAP_SOURCES[self._exec2_map_source_var.get()]
        n = self._exec2_wafer_map.load_from_ata(folder, filename=filename)
        self._exec2_wafer_map.clear_picks()
        name = os.path.basename(folder)
        self._exec2_map_path_var.set(
            f"{name}  ({n} dies)" if n else f"{name} — {filename} not found")
        if n or not quiet_if_missing:
            self._exec2_log(f"[RUN] Wafer map loaded from '{name}/{filename}' — {n} dies")

    def _exec2_set_state(self, text: str, color: str):
        self._exec2_state_lbl.config(text=text, fg=color)

    def _exec2_abort(self):
        self._exec2_running = False
        self._exec2_aborted = True
        self.after(0, lambda: self._exec2_full_btn.config(state="normal"))
        self.after(0, lambda: self._exec2_test_btn.config(state="normal"))
        self.after(0, lambda: self.recipe_panel.set_locked(False))
        self.after(0, lambda: self._exec2_wafer_map.enable_picking(
            on_change=self._exec2_on_sites_changed))
        self.after(0, lambda: self._exec2_set_state("ABORTED", "#dc2626"))
        self._exec2_log("[RUN] Aborted.")
        prober = self.controller.drivers.get("prober")
        if prober and prober.inst:
            def _stop_and_clear():
                try:
                    prober.emergency_stop()
                except Exception as e:
                    self._exec2_log(f"[RUN] Emergency stop error: {e}")
                try:
                    prober.send_es()
                    self._exec2_log("[RUN] es sent (buzzer clear)")
                except Exception as e:
                    self._exec2_log(f"[RUN] es error: {e}")
            threading.Thread(target=_stop_and_clear, daemon=True).start()

    def _exec2_finish_run(self, msg: str, color: str):
        self._exec2_running  = False
        self._exec2_run_mode = None
        self.after(0, lambda: self._exec2_full_btn.config(state="normal"))
        self.after(0, lambda: self._exec2_test_btn.config(state="normal"))
        self.after(0, lambda: self.recipe_panel.set_locked(False))
        self.after(0, lambda: self._exec2_step_var.set("Step: —"))
        self.after(0, lambda: self._exec2_wafer_map.enable_picking(
            on_change=self._exec2_on_sites_changed))
        if not self._exec2_aborted:
            self.after(0, lambda: self._exec2_set_state(msg, color))

    def _exec2_ensure_separated(self, prober, stb: int, sim: bool):
        if sim or stb != 67:
            return
        self._exec2_log("[RUN] ⚠ finished chuck UP (STB=67 — contact) >> D  (Separate)")
        prober.z_down()

    def _exec2_zup_measure_zdown(self, sim: bool, prober, die_label: str) -> bool:
        self.after(0, lambda: self._exec2_step_var.set("Step: Contact"))
        try:
            self._exec2_log("[RUN] >> Z  (Contact — chuck rises, wafer CONTACTS probe card)")
            if not sim:
                stb = prober.z_up()
                if stb == 67:
                    self._exec2_log("[RUN] << STB=67  (Z Up confirmed — CONTACT)")
                else:
                    self._exec2_log(f"[RUN] ⚠ Z Up returned STB={stb} (expected 67)")
        except Exception as e:
            self._exec2_log(f"[RUN] Touchdown error: {e} — measuring anyway")

        self.after(0, lambda: self._exec2_step_var.set("Step: Testing"))
        ok = self._exec2_run_steps_once()
        self.after(0, lambda p=ok, dl=die_label: self._exec2_log(
            f"[RESULT] {'PASS' if p else 'FAIL'}  {dl}"))

        z_down_confirmed = True
        try:
            self._exec2_log("[RUN] >> D  (Separate — chuck drops before any XY move)")
            if not sim:
                stb = prober.z_down()
                if stb == 68:
                    self._exec2_log("[RUN] << STB=68  (Z Down confirmed — separated)")
                else:
                    self._exec2_log(f"[RUN] ⚠ Z Down returned STB={stb} (expected 68) "
                                    "— separation NOT confirmed")
                    z_down_confirmed = False
        except Exception as e:
            self._exec2_log(f"[RUN] Separate error: {e} — separation NOT confirmed")
            z_down_confirmed = False

        if not sim and not z_down_confirmed:
            self._exec2_log("[RUN] ⚠ Aborting — refusing to move the chuck again "
                            "without a confirmed Z Down")
            self._exec2_abort()
        elif not sim:
            self._exec2_maybe_read_state()
        return ok

    def _exec2_update_die_color(self, row: int, col: int, ok: bool):
        try:
            if (row, col) in self._exec2_wafer_map.dies:
                self._exec2_wafer_map.update_die(row, col, "PASS" if ok else "FAIL")
        except Exception:
            pass


    def _exec2_switch_panels(self):
        panels = []
        probe_routing = getattr(self, "probe_routing", None)
        if probe_routing is not None:
            panels.append(probe_routing)
        switch_debug = getattr(self, "switch_debug", None)
        if switch_debug is not None and hasattr(switch_debug, "mark_closed"):
            panels.append(switch_debug)
        bottom = getattr(self.controller, "bottom_routing", None)
        if bottom is not None:
            panels.append(bottom)
        return panels

    def _exec2_mark_closed(self, channels):
        for ch in channels:
            for p in self._exec2_switch_panels():
                self.after(0, lambda p=p, ch=ch: p.mark_closed(ch))

    def _exec2_mark_open(self, channels):
        for ch in channels:
            for p in self._exec2_switch_panels():
                self.after(0, lambda p=p, ch=ch: p.mark_open(ch))

    def _exec2_mark_all_open(self):
        for p in self._exec2_switch_panels():
            self.after(0, p.mark_all_open)

    def _exec2_maybe_read_state(self):
        if self._exec2_die_num % 5:
            return
        for p in self._exec2_switch_panels():
            self.after(0, p.read_state)


    def _exec2_can_start(self) -> bool:
        ok = True
        if not self._exec2_steps:
            self._exec2_log("[RUN] Cannot start — no recipe loaded "
                            "(pick one and ⟳ Load Recipe first).")
            ok = False
        if (self._exec2_map_source_var.get() != "Accretech"
                or not self._exec2_wafer_map._last_dies):
            self._exec2_log("[RUN] Cannot start — no Accretech wafer map loaded "
                            "(📂 Load Wafer Map, set source to 'Accretech'; extract "
                            "one on the Accr Wafer tab first if you haven't).")
            ok = False
        required_instruments = ("prober", "smu", "dmm", "switch", "wave_gen")
        missing_instruments = [k for k in required_instruments if k not in self.controller.drivers]
        if missing_instruments:
            self._exec2_log("[RUN] Cannot start — instrument(s) not connected: "
                            f"{', '.join(missing_instruments)} (Global Reset / "
                            "check cabling, then retry — see the Instruments tab).")
            ok = False
        return ok

    def _exec2_start_full_die(self):
        if self._exec2_running:
            self._exec2_log("[RUN] A run is already active — stop it first.")
            return
        if not self._exec2_can_start():
            return
        self._exec2_reset_counts(total_dies=len(self._exec2_wafer_map._last_dies or []))
        self._exec2_running  = True
        self._exec2_aborted  = False
        self._exec2_run_mode = "full"
        self._exec2_full_btn.config(state="disabled")
        self._exec2_test_btn.config(state="disabled")
        self.recipe_panel.set_locked(True)
        self._exec2_wafer_map.enable_picking(0)
        self.after(0, lambda: self._exec2_set_state("RUNNING (Full Die)", "#2563eb"))
        self._exec2_log("[RUN] ▶ Full Die — walking the entire wafer (G/J), "
                        "measuring the loaded recipe at every die.")
        threading.Thread(target=self._exec2_full_die_thread, daemon=True).start()

    def _exec2_full_die_thread(self):
        prober = self.controller.drivers.get("prober")
        sim = not (prober and prober.inst)
        self._exec2_current_pma_shot = None
        try:
            self._exec2_log("[RUN] >> D  (Separate)")
            if sim:
                time.sleep(0.15)
            else:
                prober.z_down()

            self._exec2_log("[RUN] >> G  (Position start die)")
            if sim:
                stb = 70
                time.sleep(0.2)
            else:
                stb = prober.move_to_start_die()
            self._exec2_log(f"[RUN] << STB={stb}")
            self._exec2_ensure_separated(prober, stb, sim)

            sim_dies_remaining = 12
            while self._exec2_running and not self._exec2_aborted:
                if sim:
                    x, y = float(self._exec2_die_num % 5), float(self._exec2_die_num // 5)
                else:
                    raw = prober.get_xy_position()
                    x, y = _parse_q_response(raw)
                self._exec2_die_num += 1
                die_label = f"Die #{self._exec2_die_num}  (X{x:.0f} Y{y:.0f})"
                self.after(0, lambda d=die_label: self._exec2_die_var.set(f"Die: {d}"))
                self.after(0, lambda x=x, y=y:
                           self._exec2_xy_var.set(f"X: {x:.0f} die\nY: {y:.0f} die"))
                self._exec2_highlight_current(int(y), int(x))
                self._exec2_log(f"[RUN] << Q  die X={x:.0f} Y={y:.0f}")

                ok = self._exec2_zup_measure_zdown(sim, prober, die_label)
                self._exec2_update_die_color(int(y), int(x), ok)
                self.after(0, self._exec2_add_pass if ok else self._exec2_add_fail)

                if not self._exec2_running or self._exec2_aborted:
                    break

                self._exec2_log("[RUN] >> J  (Next die)")
                if sim:
                    time.sleep(0.15)
                    sim_dies_remaining -= 1
                    stb = 81 if sim_dies_remaining <= 0 else 66
                else:
                    stb = prober.next_die()
                if stb == 81:
                    self._exec2_log("[RUN] << STB=81  (wafer end)")
                    break
                if stb == 90:
                    self._exec2_log("[RUN] << STB=90  (probing stop — <STOP> pushed)")
                    break
                self._exec2_log(f"[RUN] << STB={stb}")
                self._exec2_ensure_separated(prober, stb, sim)
        except Exception as e:
            self._exec2_log(f"[RUN] ERROR: {e}")
        finally:
            self._exec2_finish_run("DONE (Full Die)", "#16a34a")


    def _exec2_on_sites_changed(self, picks):
        self._exec2_sites_var.set(
            f"Test sites: {len(picks)} picked (click dies to add/remove)")

    def _exec2_randomize_sites(self):
        dies = self._exec2_wafer_map._last_dies
        if not dies:
            self._exec2_log("[RUN] No wafer map loaded — load one before picking test sites.")
            return
        import random
        pool = [(d["row"], d["col"]) for d in dies]
        picks = random.sample(pool, min(5, len(pool)))
        self._exec2_wafer_map.set_picked(picks)
        self._exec2_on_sites_changed(picks)
        self._exec2_log("[RUN] Randomized test sites: "
                        + ", ".join(f"R{r}C{c}" for r, c in picks))


    def _exec2_pma_accretech_rc(self):
        accr_wafer = getattr(self, "accr_wafer", None)
        if accr_wafer is None:
            return set()
        return {(y, x) for (x, y, _raw) in accr_wafer._dies}

    def _exec2_compute_pma_merge(self, row_offset: int = 0, col_offset: int = 0):
        data = self.pma_wafer.workbook_data
        if not data:
            self._exec2_log("[RUN] Test PMA / Compare: no PMA workbook loaded — "
                            "open one on the PMA tab first.")
            return None, None, None
        accretech_rc = self._exec2_pma_accretech_rc()
        if not accretech_rc:
            self._exec2_log("[RUN] Test PMA / Compare: no Accretech wafer map loaded — "
                            "extract one on the Accr Wafer tab (or load an ATA folder "
                            "that already has ata_wafer_map_accretech.csv).")
            return None, None, None
        pma_grid = pma_shots_to_grid(data)
        merged = merge_with_accretech(pma_grid, accretech_rc, row_offset, col_offset)
        return merged, pma_grid, accretech_rc

    def _exec2_pma_starting_offset(self, pma_grid, accretech_rc):
        if self._exec2_pma_offset_confirmed:
            return self._exec2_pma_row_offset, self._exec2_pma_col_offset
        return centroid_offset(pma_grid, accretech_rc)

    def _exec2_save_pma_merge_to_ata(self, merged):
        from tkinter import messagebox
        import csv
        if not merged:
            messagebox.showinfo("No Data", "No merged dies to save — check the "
                                "Compare/Merge counts (row/col offset may be off).")
            return
        folder = self._ata_folder
        if not folder:
            messagebox.showerror(
                "No ATA Folder",
                "No ATA folder is loaded — use 📁 Load ATA Folder on the top "
                "toolbar first.")
            return
        path = os.path.join(folder, "ata_wafer_map_merged.csv")
        if os.path.exists(path) and not messagebox.askyesno(
            "Overwrite Merged Map",
            f"{path}\nalready exists — overwrite it with the current "
            f"{len(merged)} merged die(s)?"
        ):
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["row", "col", "x_die", "y_die", "die_ids"])
            for d in merged:
                wr.writerow([d["row"], d["col"], d["col"], d["row"],
                            "/".join(d["die_ids"])])
        self._exec2_log(f"[RUN] Saved {len(merged)} merged die(s) → {path}")

    def _exec2_open_pma_compare_dialog(self):
        data = self.pma_wafer.workbook_data
        if not data:
            self._exec2_log("[RUN] Test PMA / Compare: no PMA workbook loaded — "
                            "open one on the PMA tab first.")
            return
        accretech_rc = self._exec2_pma_accretech_rc()
        if not accretech_rc:
            self._exec2_log("[RUN] Test PMA / Compare: no Accretech wafer map loaded — "
                            "extract one on the Accr Wafer tab (or load an ATA folder "
                            "that already has ata_wafer_map_accretech.csv).")
            return
        pma_grid = pma_shots_to_grid(data)
        start_row, start_col = self._exec2_pma_starting_offset(pma_grid, accretech_rc)

        dlg = tk.Toplevel(self)
        dlg.title("Compare / Merge PMA Wafer Map")
        dlg.transient(self.winfo_toplevel())
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)

        summary_var = tk.StringVar()
        ttk.Label(frm, textvariable=summary_var, font=("Consolas", 9),
                 justify="left").grid(row=0, column=0, columnspan=4, sticky="w",
                                      pady=(0, 8))
        ttk.Label(frm, text="Overlaid by matching the two maps' centers (see "
                 "🎯 Center Overlay) — a PMA die counts as \"merged\" when its "
                 "(row, col), shifted by the offset below, lands on a die the "
                 "Accretech prober actually walked. Nudge the offset by hand if "
                 "dies land on the wrong physical die.",
                 font=("Segoe UI", 8), foreground="#6b7280", wraplength=340,
                 justify="left").grid(row=1, column=0, columnspan=4, sticky="w",
                                      pady=(0, 10))

        ttk.Label(frm, text="Row offset:").grid(row=2, column=0, sticky="e")
        row_var = tk.IntVar(value=start_row)
        ttk.Spinbox(frm, from_=-50, to=50, width=6, textvariable=row_var).grid(
            row=2, column=1, sticky="w", padx=(4, 16))
        ttk.Label(frm, text="Col offset:").grid(row=2, column=2, sticky="e")
        col_var = tk.IntVar(value=start_col)
        ttk.Spinbox(frm, from_=-50, to=50, width=6, textvariable=col_var).grid(
            row=2, column=3, sticky="w", padx=(4, 0))

        state = {"merged": []}

        def recompute(*_a):
            try:
                ro, co = row_var.get(), col_var.get()
            except tk.TclError:
                return
            state["merged"] = merge_with_accretech(pma_grid, accretech_rc, ro, co)
            summary_var.set(
                f"Accretech dies walked:      {len(accretech_rc)}\n"
                f"PMA dies (with a real ID):  {len(pma_grid)}\n"
                f"Merged (on both maps):      {len(state['merged'])}"
            )

        row_var.trace_add("write", recompute)
        col_var.trace_add("write", recompute)
        recompute()

        def center_overlay():
            ro, co = centroid_offset(pma_grid, accretech_rc)
            row_var.set(ro)
            col_var.set(co)

        def use_offsets():
            self._exec2_pma_row_offset = row_var.get()
            self._exec2_pma_col_offset = col_var.get()
            self._exec2_pma_offset_confirmed = True

        def highlight():
            use_offsets()
            picks = [(d["row"], d["col"]) for d in state["merged"]]
            self._exec2_wafer_map.set_picked(picks)
            self._exec2_on_sites_changed(picks)
            self._exec2_log(f"[RUN] Highlighted {len(picks)} merged PMA/Accretech "
                            "die(s) on the map.")

        def save_ata():
            use_offsets()
            self._exec2_save_pma_merge_to_ata(state["merged"])

        def use_for_test():
            use_offsets()
            picks = [(d["row"], d["col"]) for d in state["merged"]]
            self._exec2_wafer_map.set_picked(picks)
            self._exec2_on_sites_changed(picks)
            dlg.destroy()
            self._exec2_start_test_die()

        ttk.Button(frm, text="🎯 Center Overlay", command=center_overlay).grid(
            row=2, column=4, sticky="w", padx=(10, 0))

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=5, sticky="ew", pady=(12, 0))
        ttk.Button(btns, text="🖌 Highlight on Map", command=highlight).pack(side="left")
        ttk.Button(btns, text="💾 Save Merged to ATA", command=save_ata).pack(
            side="left", padx=6)
        ttk.Button(btns, text="▶ Use for Test PMA", command=use_for_test).pack(side="left")
        ttk.Button(btns, text="Close", command=lambda: (use_offsets(), dlg.destroy())).pack(
            side="right")

        dlg.update_idletasks()
        dlg.grab_set()

    def _exec2_start_test_pma(self):
        if self._exec2_running:
            self._exec2_log("[RUN] A run is already active — stop it first.")
            return
        data = self.pma_wafer.workbook_data
        if not data:
            self._exec2_log("[RUN] Test PMA: no PMA workbook loaded — "
                            "open one on the PMA tab first.")
            return
        accretech_rc = self._exec2_pma_accretech_rc()
        if not accretech_rc:
            self._exec2_log("[RUN] Test PMA: no Accretech wafer map loaded — "
                            "extract one on the Accr Wafer tab (or load an ATA folder "
                            "that already has ata_wafer_map_accretech.csv).")
            return
        pma_grid = pma_shots_to_grid(data)
        row_off, col_off = self._exec2_pma_starting_offset(pma_grid, accretech_rc)
        merged = merge_with_accretech(pma_grid, accretech_rc, row_off, col_off)
        if not merged:
            self._exec2_log(
                "[RUN] Test PMA: no PMA dies land on the Accretech-walked map at "
                f"offset row{row_off:+d}/col{col_off:+d} — open 🔀 Compare/Merge PMA "
                "to check/nudge the alignment.")
            return
        self._exec2_pma_row_offset = row_off
        self._exec2_pma_col_offset = col_off
        self._exec2_pma_offset_confirmed = True
        picks = [(d["row"], d["col"]) for d in merged]
        die_shots_by_rc = {(d["row"], d["col"]): d for d in merged}
        self._exec2_wafer_map.set_picked(picks)
        self._exec2_on_sites_changed(picks)
        self._exec2_log(
            f"[RUN] ▶ Test PMA — {len(picks)} merged die(s) "
            f"(offset row{row_off:+d}/col{col_off:+d})")
        self._exec2_start_test_die(die_shots_by_rc=die_shots_by_rc)

    def _exec2_start_test_die(self, die_shots_by_rc=None):
        if self._exec2_running:
            self._exec2_log("[RUN] A run is already active — stop it first.")
            return
        if not self._exec2_can_start():
            return
        sites = self._exec2_wafer_map.get_picked()
        if not sites:
            self._exec2_randomize_sites()
            sites = self._exec2_wafer_map.get_picked()
        if not sites:
            self._exec2_log("[RUN] No dies available to pick test sites from.")
            return
        self._exec2_reset_counts(total_dies=len(sites))
        self._exec2_running  = True
        self._exec2_aborted  = False
        self._exec2_run_mode = "test"
        self._exec2_full_btn.config(state="disabled")
        self._exec2_test_btn.config(state="disabled")
        self.recipe_panel.set_locked(True)
        self._exec2_wafer_map.enable_picking(0)
        self.after(0, lambda: self._exec2_set_state("RUNNING (Test Die)", "#2563eb"))
        self._exec2_log(f"[RUN] ▶ Test Die — {len(sites)} site(s): "
                        + ", ".join(f"R{r}C{c}" for r, c in sites))
        threading.Thread(target=self._exec2_test_die_thread,
                         args=(sites, die_shots_by_rc), daemon=True).start()

    def _exec2_test_die_thread(self, sites, die_shots_by_rc=None):
        prober = self.controller.drivers.get("prober")
        sim = not (prober and prober.inst)
        die_shots_by_rc = die_shots_by_rc or {}
        try:
            self._exec2_log("[RUN] >> D  (Separate)")
            if sim:
                time.sleep(0.15)
            else:
                prober.z_down()

            row, col = sites[0]
            self._exec2_log(f"[RUN] >> J  (Position die X={col} Y={row})")
            if sim:
                stb = 66
                time.sleep(0.2)
            else:
                stb = prober.move_to_die_xy(col, row)
            if stb == 81:
                self._exec2_log("[RUN] << STB=81  (wafer end)")
                return
            if stb == 90:
                self._exec2_log("[RUN] << STB=90  (probing stop — <STOP> pushed)")
                return
            self._exec2_log(f"[RUN] << STB={stb}")
            self._exec2_ensure_separated(prober, stb, sim)

            idx = 0
            while self._exec2_running and not self._exec2_aborted and idx < len(sites):
                row, col = sites[idx]
                die_label = f"R{row}C{col}  (X{col} Y{row})"
                self.after(0, lambda d=die_label: self._exec2_die_var.set(f"Die: {d}"))
                self.after(0, lambda x=col, y=row:
                           self._exec2_xy_var.set(f"X: {x} die\nY: {y} die"))
                self._exec2_highlight_current(row, col)
                self._exec2_die_num += 1

                self._exec2_current_pma_shot = die_shots_by_rc.get((row, col))

                ok = self._exec2_zup_measure_zdown(sim, prober, die_label)
                self._exec2_update_die_color(row, col, ok)
                self.after(0, self._exec2_add_pass if ok else self._exec2_add_fail)

                idx += 1
                if not self._exec2_running or self._exec2_aborted or idx >= len(sites):
                    break

                row, col = sites[idx]
                self._exec2_log(f"[RUN] >> J  (Position die X={col} Y={row})")
                if sim:
                    time.sleep(0.15)
                    stb = 66
                else:
                    stb = prober.move_to_die_xy(col, row)
                if stb == 81:
                    self._exec2_log("[RUN] << STB=81  (wafer end)")
                    break
                if stb == 90:
                    self._exec2_log("[RUN] << STB=90  (probing stop — <STOP> pushed)")
                    break
                self._exec2_log(f"[RUN] << STB={stb}")
                self._exec2_ensure_separated(prober, stb, sim)
        except Exception as e:
            self._exec2_log(f"[RUN] ERROR: {e}")
        finally:
            self._exec2_finish_run("DONE (Test Die)", "#16a34a")


    def _exec2_load_recipe(self):
        name = self._exec2_recipe_var.get()
        if not name:
            self._exec2_log("[RUN] Pick a recipe first — the dropdown lists the "
                            "Recipe tab's recipes.")
            return
        if not self.recipe_panel.select_recipe(name):
            self._exec2_log(f"[RUN] Recipe '{name}' not found — reload the ATA folder.")
            return
        self._exec2_steps = self.recipe_panel.get_steps()

        self._exec2_steps_tree.delete(*self._exec2_steps_tree.get_children())
        for i, s in enumerate(self._exec2_steps, 1):
            self._exec2_steps_tree.insert("", "end", values=(
                i, s.get("name", ""), s.get("type", ""), s.get("conn", "")))
        self._exec2_steps_var.set(f"{name} — {len(self._exec2_steps)} step(s)")

        self._exec2_log(f"[RUN] Loaded recipe '{name}' with "
                        f"{len(self._exec2_steps)} step(s):")
        for i, s in enumerate(self._exec2_steps, 1):
            extra = (f" target={s['target']}" if s.get("target")
                     else f" {s.get('hi', '')}→{s.get('lo', '')}")
            self._exec2_log(f"[RUN]   {i}. {s.get('name')} [{s.get('type')}"
                            f"{('/' + s['mode']) if s.get('mode') else ''}]"
                            f"{extra}  conn={s.get('conn') or '—'}")
        issues = self.recipe_panel.validate_recipe()
        for msg in issues:
            self._exec2_log(f"[RUN] {msg}")
        if issues:
            self._exec2_log(f"[RUN] ⚠ {len(issues)} validation issue(s) — "
                            "review before 🦶 Touchdown/Measure")
        if hasattr(self.controller, "check_system_ready"):
            self.controller.check_system_ready()


    def _exec2_find_loaded_step(self, ref: str):
        ref = (ref or "").strip()
        if ref.isdigit():
            i = int(ref) - 1
            return self._exec2_steps[i] if 0 <= i < len(self._exec2_steps) else None
        for s in self._exec2_steps:
            if s.get("name", "").strip().lower() == ref.lower():
                return s
        return None

    def _exec2_reset_output(self, ref, smu, wgen, sim: bool):
        if ref is None:
            return ""
        if ref.get("type") == "wave":
            wch = 2 if ref.get("chan") == "CH2" else 1
            if not sim and wgen and wgen.inst:
                wgen.turn_output_off_ch(wch)
            return f"reset WGEN CH{wch}"
        if ref.get("mode") == "apply":
            smu_ch = "smub" if ref.get("chan") == "B" else "smua"
            if not sim and smu and smu.inst:
                smu.turn_output_off(smu_ch)
            return f"reset SMU {ref.get('chan') or 'A'}"
        return ""

    def _exec2_touchdown_measure(self):
        if self._exec2_running:
            self._exec2_log("[MEASURE] A run is active — stop it first.")
            return
        if not self._exec2_steps:
            self._exec2_log("[MEASURE] No recipe loaded — pick one and ⟳ Load Recipe first.")
            return
        threading.Thread(target=self._exec2_touchdown_then_measure, daemon=True).start()

    def _exec2_touchdown_then_measure(self):
        prober = self.controller.drivers.get("prober")
        if prober and prober.inst:
            try:
                self._exec2_log("[MEASURE] >> Z  (Touchdown — chuck rises, "
                                "wafer CONTACTS probe card)")
                prober.z_up()
                self._exec2_log("[MEASURE] Touchdown complete — wafer in contact")
            except Exception as e:
                self._exec2_log(f"[MEASURE] Touchdown error: {e} — measuring anyway")
        else:
            self._exec2_log("[MEASURE] Prober not connected — skipping touchdown, "
                            "measuring at current state")
        self._exec2_run_steps_once()

    def _exec2_avg_spec(self, step: dict) -> tuple:
        try:
            count = max(1, int(step.get("avg_count") or 1))
        except ValueError:
            count = 1
        try:
            delay = max(0.0, float(step.get("avg_delay") or 0))
        except ValueError:
            delay = 0.0
        return count, delay

    def _exec2_take_average(self, read_one, avg_count: int, avg_delay_ms: float, unit: str) -> float:
        readings = []
        for k in range(avg_count):
            readings.append(read_one())
            if avg_count > 1:
                self._exec2_log(f"[MEASURE]      reading {k + 1}/{avg_count} = "
                                f"{readings[-1]:.6g} {unit}")
                if k < avg_count - 1 and avg_delay_ms > 0:
                    time.sleep(avg_delay_ms / 1000.0)
        return sum(readings) / len(readings)

    def _exec2_run_steps_once(self) -> bool:
        import random
        import re
        switch = self.controller.drivers.get("switch")
        smu    = self.controller.drivers.get("smu")
        dmm    = self.controller.drivers.get("dmm")
        wgen   = self.controller.drivers.get("wave_gen")
        sim = not (switch and switch.inst)

        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        recipe_name = self.recipe_panel.get_active_recipe() if hasattr(self, "recipe_panel") else ""
        die_label = (self._exec2_die_var.get().replace("Die: ", "")
                    if self._exec2_die_num else
                    self._exec2_xy_var.get().replace("\n", " "))

        pma_shot = getattr(self, "_exec2_current_pma_shot", None)
        pma_die_id = (pma_shot or {}).get("raw_text") or ""
        last_set_voltage_by_ch = {}

        overall_ok = True
        last_reading = None
        readings_by_name = {}

        self._exec2_log(f"[MEASURE] One iteration — {len(self._exec2_steps)} step(s)"
                        + ("  [SIM — no switch matrix connected]" if sim else ""))
        _die_slot_re = re.compile(r"\(Die (\d+)\)\s*$")
        for i, s in enumerate(self._exec2_steps, 1):
            t    = s.get("type")
            name = s.get("name") or f"step {i}"
            lvl  = s.get("level") or ""
            conn = (s.get("conn") or "").replace(" ", "")
            chans = [c for c in conn.split(",") if c and c.lower() != "all"]
            conn_str = "_".join(chans)
            try:
                if t == "delay":
                    ms = float(lvl or 0)
                    self._exec2_log(f"[MEASURE] {i}. {name}: wait {ms:.0f} ms")
                    time.sleep(ms / 1000.0)
                    continue

                if t == "picture":
                    self._exec2_log(f"[MEASURE] {i}. {name}: take picture "
                                    "(not yet implemented — skipped)")
                    continue

                if t == "open":
                    if conn.lower() == "all" or (s.get("target") or "").strip().lower() == "all":
                        self._exec2_log(f"[MEASURE] {i}. {name}: open ALL channels + reset all outputs")
                        if not sim:
                            switch.open_all()
                            if smu and smu.inst:
                                smu.turn_output_off("smua")
                                smu.turn_output_off("smub")
                            if wgen and wgen.inst:
                                wgen.turn_output_off_ch(1)
                                wgen.turn_output_off_ch(2)
                        self._exec2_mark_all_open()
                        continue
                    ref = self._exec2_find_loaded_step(s.get("target", ""))
                    note = self._exec2_reset_output(ref, smu, wgen, sim)
                    self._exec2_log(f"[MEASURE] {i}. {name}: open {conn or '—'}"
                                    + (f"  ({note})" if note else ""))
                    if not sim:
                        for ch in chans:
                            switch.open_crosspoint(ch[:2], ch[2:])
                    self._exec2_mark_open(chans)
                    continue

                if t == "passfail":
                    tgt = (s.get("target") or "").strip()
                    if tgt:
                        found = readings_by_name.get(tgt)
                        ref_name = tgt
                    else:
                        found = (last_reading[1], last_reading[2]) if last_reading else None
                        ref_name = last_reading[0] if last_reading else "(none)"
                    if found is None:
                        self._exec2_log(f"[MEASURE] {i}. {name}: ERROR no reading found "
                                        f"for '{ref_name}' — FAIL")
                        overall_ok = False
                        continue
                    value, unit = found
                    mn, mx = s.get("min") or "", s.get("max") or ""
                    verdict = ((not mn or value >= float(mn)) and
                              (not mx or value <= float(mx)))
                    overall_ok = overall_ok and verdict
                    spec = f"[{mn or '-inf'}, {mx or '+inf'}]"
                    self._exec2_log(f"[MEASURE] {i}. {name}: "
                                    f"{'PASS' if verdict else 'FAIL'}  "
                                    f"{ref_name} = {value:.6g} {unit}  spec {spec}")
                    continue

                mode       = s.get("mode") or ""
                instrument = s.get("instrument") or ""
                label = f"{i}. {name} [{t}{('/' + mode) if mode else ''} " \
                        f"via {instrument}]"
                self._exec2_log(f"[MEASURE] {label}: close {conn or '—'}")
                if not sim:
                    for ch in chans:
                        switch.close_channel(ch)
                self._exec2_mark_closed(chans)
                smu_ch = "smub" if s.get("chan") == "B" else "smua"
                wch    = 2 if s.get("chan") == "CH2" else 1

                limit = s.get("limit") or ""
                avg_count, avg_delay = self._exec2_avg_spec(s)
                avg_txt = f"  [avg of {avg_count}, {avg_delay:.0f} ms apart]" if avg_count > 1 else ""

                if t == "resistance":
                    if instrument == "SMU":
                        read_one = ((lambda: abs(random.gauss(50, 15)))
                                   if sim or not (smu and smu.inst)
                                   else (lambda: smu.measure_resistance(smu_ch)))
                    else:
                        read_one = ((lambda: abs(random.gauss(50, 15)))
                                   if sim or not (dmm and dmm.inst)
                                   else (lambda: dmm.measure_resistance()))
                    r = self._exec2_take_average(read_one, avg_count, avg_delay, "Ω")
                    self._exec2_log(f"[MEASURE]    R = {r:.4g} Ω  (via {instrument}){avg_txt}")
                    self.record_result(timestamp=ts, recipe=recipe_name, die=die_label,
                                       step=name, type=t, mode=mode, value=f"{r:.6g}",
                                       unit="ohm", connection=conn_str, instrument=instrument)
                    last_reading = (name, r, "ohm")
                    readings_by_name[name] = (r, "ohm")
                elif t == "voltage" and mode == "measure":
                    if instrument == "SMU":
                        read_one = ((lambda: random.gauss(3.3, 0.1))
                                   if sim or not (smu and smu.inst)
                                   else (lambda: smu.measure_voltage(smu_ch)))
                    else:
                        read_one = ((lambda: random.gauss(3.3, 0.1))
                                   if sim or not (dmm and dmm.inst)
                                   else (lambda: dmm.measure_voltage_dc()))
                    v = self._exec2_take_average(read_one, avg_count, avg_delay, "V")
                    self._exec2_log(f"[MEASURE]    V = {v:.4g} V  (via {instrument}){avg_txt}")
                    self.record_result(timestamp=ts, recipe=recipe_name, die=die_label,
                                       step=name, type=t, mode=mode, value=f"{v:.6g}",
                                       unit="V", connection=conn_str, instrument=instrument)
                    last_reading = (name, v, "V")
                    readings_by_name[name] = (v, "V")
                elif t == "voltage":
                    if not sim and smu and smu.inst:
                        smu.set_voltage(smu_ch, float(lvl or 0))
                        if limit:
                            smu.set_current_limit(smu_ch, float(limit))
                        smu.turn_output_on(smu_ch)
                    last_set_voltage_by_ch[smu_ch] = float(lvl or 0)
                    lim_txt = f", current limit {limit} A" if limit else ""
                    self._exec2_log(f"[MEASURE]    forcing {lvl or 0} V on SMU "
                                    f"{s.get('chan') or 'A'}{lim_txt} "
                                    "(output ON until an open step)")
                elif t == "current" and mode == "apply":
                    actual_current = None
                    actual_voltage = None
                    if not sim and smu and smu.inst:
                        smu.set_current(smu_ch, float(lvl or 0))
                        if limit:
                            smu.set_voltage_limit(smu_ch, float(limit))
                        smu.turn_output_on(smu_ch)
                        try:
                            actual_current = smu.measure_current(smu_ch)
                        except Exception:
                            actual_current = None
                        try:
                            actual_voltage = smu.measure_voltage(smu_ch)
                        except Exception:
                            actual_voltage = None
                    if actual_current is None:
                        actual_current = abs(random.gauss(
                            float(lvl or 0), abs(float(lvl or 0)) * 0.0005 + 1e-12))
                    lim_txt = f", voltage limit {limit} V" if limit else ""
                    readback_txt = (f"  readback I={actual_current:.6g} A"
                                    + (f", V={actual_voltage:.6g} V"
                                       if actual_voltage is not None else ""))
                    self._exec2_log(f"[MEASURE]    forcing {lvl or 0} A on SMU "
                                    f"{s.get('chan') or 'A'}{lim_txt} "
                                    "(output ON until an open step)" + readback_txt)
                    self.record_result(timestamp=ts, recipe=recipe_name, die=die_label,
                                       step=name, type=t, mode=mode, value=f"{actual_current:.6g}",
                                       unit="A", voltage=actual_voltage,
                                       connection=conn_str, instrument=instrument)
                    last_reading = (name, actual_current, "A")
                    readings_by_name[name] = (actual_current, "A")
                elif t == "current":
                    set_voltage = None
                    actual_voltage = None
                    if instrument == "SMU":
                        if not sim and smu and smu.inst:
                            if lvl:
                                smu.set_voltage(smu_ch, float(lvl))
                                if limit:
                                    smu.set_current_limit(smu_ch, float(limit))
                                smu.turn_output_on(smu_ch)
                                last_set_voltage_by_ch[smu_ch] = float(lvl)
                            read_one = lambda: smu.measure_current(smu_ch)
                        else:
                            read_one = lambda: abs(random.gauss(4e-7, 2e-7))
                        bias_txt = f"  (bias {lvl} V via SMU)" if lvl else "  (via SMU)"
                        set_voltage = last_set_voltage_by_ch.get(smu_ch)
                    else:
                        read_one = ((lambda: abs(random.gauss(4e-7, 2e-7)))
                                   if sim or not (dmm and dmm.inst)
                                   else (lambda: dmm.measure_current_dc()))
                        bias_txt = "  (via DMM)"
                    i_a = self._exec2_take_average(read_one, avg_count, avg_delay, "A")
                    if instrument == "SMU" and not sim and smu and smu.inst:
                        try:
                            actual_voltage = smu.measure_voltage(smu_ch)
                        except Exception:
                            actual_voltage = None
                    self._exec2_log(f"[MEASURE]    I = {i_a:.4g} A{bias_txt}{avg_txt}")
                    die_slot_m = _die_slot_re.search(name)
                    if actual_voltage is None:
                        actual_voltage = set_voltage
                    self.record_result(
                        timestamp=ts, recipe=recipe_name, die=die_label,
                        step=name, type=t, mode=mode, value=f"{i_a:.6g}", unit="A",
                        die_id=pma_die_id or None,
                        switch=int(die_slot_m.group(1)) if die_slot_m else None,
                        set_voltage=set_voltage, voltage=actual_voltage,
                        connection=conn_str, instrument=instrument)
                    last_reading = (name, i_a, "A")
                    readings_by_name[name] = (i_a, "A")
                elif t == "wave":
                    shape = s.get("shape") or "SIN"
                    freq = float(s.get("freq") or 1000)
                    if not sim and wgen and wgen.inst:
                        wgen.set_waveform_ch(wch, shape, freq, float(lvl or 1.0))
                        if limit:
                            wgen.set_voltage_limit_ch(wch, float(limit))
                        wgen.turn_output_on_ch(wch)
                    lim_txt = f", clamp ±{limit} V" if limit else ""
                    self._exec2_log(f"[MEASURE]    WGEN CH{wch} ON — {shape} "
                                    f"{lvl or 1.0} Vpp @ {freq:.4g} Hz{lim_txt} "
                                    "(until an open step)")
            except Exception as e:
                self._exec2_log(f"[MEASURE] {i}. {name}: ERROR {e} — iteration aborted")
                return False
        self._exec2_log(f"[MEASURE] Iteration complete — "
                        f"{'PASS' if overall_ok else 'FAIL'}")
        return overall_ok


    def record_result(self, timestamp, recipe, die, step, type, mode, value, unit,
                      die_id=None, switch=None, set_voltage=None, voltage=None,
                      connection=None, instrument=None):
        row = {"timestamp": timestamp, "recipe": recipe, "die": die, "step": step,
               "type": type, "mode": mode, "value": value, "unit": unit,
               "die_id": die_id or "", "switch": switch if switch is not None else "",
               "set_voltage": set_voltage if set_voltage is not None else "",
               "voltage": voltage if voltage is not None else "",
               "connection": connection or "", "instrument": instrument or ""}
        self.controller.results_data.append(row)
        if hasattr(self, "_results_tree"):
            def _ui():
                self._results_tree.insert("", "end", values=(
                    row["timestamp"], row["recipe"], row["die"], row["step"],
                    row["type"], row["value"], row["unit"]))
                kids = self._results_tree.get_children()
                if kids:
                    self._results_tree.see(kids[-1])
            self.after(0, _ui)

    def clear_results(self):
        self.controller.results_data.clear()
        if hasattr(self, "_results_tree"):
            self._results_tree.delete(*self._results_tree.get_children())


    def _exec2_manual_z_up(self):
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log("[EXEC2] Z Up: prober not connected.")
            return
        def _run():
            try:
                self.after(0, lambda: self._exec2_log("[EXEC2] >> Z  (Contact)"))
                prober.z_up()
                self.after(0, lambda: self._exec2_log("[EXEC2] Z Up complete."))
            except Exception as e:
                self.after(0, lambda e=e: self._exec2_log(f"[EXEC2] Z Up error: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _exec2_manual_z_down(self):
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log("[EXEC2] Z Down: prober not connected.")
            return
        def _run():
            try:
                self.after(0, lambda: self._exec2_log("[EXEC2] >> D  (Separate)"))
                prober.z_down()
                self.after(0, lambda: self._exec2_log("[EXEC2] Z Down complete."))
            except Exception as e:
                self.after(0, lambda e=e: self._exec2_log(f"[EXEC2] Z Down error: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _exec2_manual_go_to_start(self):
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log("[EXEC2] First Die: prober not connected.")
            return
        threading.Thread(target=self._exec2_go_to_start_thread, args=(prober,),
                         daemon=True).start()

    def _exec2_go_to_start_thread(self, prober):
        try:
            self._exec2_log("[EXEC2] >> G  (Position start die)")
            stb = prober.move_to_start_die()
            self._exec2_log(f"[EXEC2] << STB={stb}  (start die positioned, chuck "
                            f"{'UP — CONTACT' if stb == 67 else 'DOWN'})")
            self._exec2_get_xy()
        except Exception as e:
            self._exec2_log(f"[EXEC2] First Die error: {e}")

    def _exec2_manual_unload(self):
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log("[EXEC2] Unload: prober not connected.")
            return
        threading.Thread(target=self._exec2_unload_thread, args=(prober,),
                         daemon=True).start()

    def _exec2_unload_thread(self, prober):
        try:
            self._exec2_log("[EXEC2] >> U  (Unload wafer)")
            stb = prober.unload_wafer()
            self._exec2_log(f"[EXEC2] << STB={stb}  (wafer unloaded)")
        except Exception as e:
            self._exec2_log(f"[EXEC2] Unload error: {e}")

    def _exec2_manual_next_die(self):
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log("[EXEC2] Next Die: prober not connected.")
            return
        def _run():
            try:
                self.after(0, lambda: self._exec2_log("[EXEC2] >> J  (Next Die)"))
                prober.next_die()
                self.after(0, lambda: self._exec2_log("[EXEC2] Stepped to next die."))
                self.after(0, self._exec2_get_xy)
            except Exception as e:
                self.after(0, lambda e=e: self._exec2_log(f"[EXEC2] Next Die error: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _exec2_get_xy(self):
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_xy_var.set("X: —\nY: —")
            self._exec2_log("[EXEC2] XY: prober not connected.")
            return
        def _run():
            try:
                raw = prober.get_xy_position()
                x, y = _parse_q_response(raw)
                self.after(0, lambda: self._exec2_xy_var.set(f"X: {x:.0f} die\nY: {y:.0f} die"))
                self.after(0, lambda: self._exec2_log(f"[EXEC2] Q → die X={x:.0f}  Y={y:.0f}"))
                self.after(0, lambda: self._exec2_highlight_current(int(y), int(x)))
            except Exception as e:
                self.after(0, lambda e=e: self._exec2_log(f"[EXEC2] XY error: {e}"))
                self.after(0, lambda: self._exec2_xy_var.set("X: ERROR\nY: ERROR"))
        threading.Thread(target=_run, daemon=True).start()

    def _exec2_highlight_current(self, row: int, col: int):
        wm = self._exec2_wafer_map
        prev = self._exec2_current_rc
        if prev is not None and prev != (row, col) and prev in wm.dies:
            try:
                if wm.canvas.itemcget(wm.dies[prev], "fill") == "#dbeafe":
                    wm.update_die(prev[0], prev[1], "UNTESTED")
            except Exception:
                pass
        self._exec2_current_rc = (row, col)
        if (row, col) in wm.dies:
            wm.update_die(row, col, "CURRENT")

    def _exec2_add_pass(self):
        self._exec2_pass_var.set(self._exec2_pass_var.get() + 1)
        self._exec2_update_yield()
        self._exec2_push_stats()

    def _exec2_add_fail(self):
        self._exec2_fail_var.set(self._exec2_fail_var.get() + 1)
        self._exec2_update_yield()
        self._exec2_push_stats()

    def _exec2_reset_counts(self, total_dies=None):
        self._exec2_pass_var.set(0)
        self._exec2_fail_var.set(0)
        self._exec2_die_num = 0
        if total_dies is not None:
            self._exec2_total_dies = total_dies
        self._exec2_pct_var.set("Yield:  —")
        self._exec2_die_var.set("Die: —")
        self._exec2_step_var.set("Step: —")
        self._exec2_push_stats()

    def _exec2_push_stats(self):
        if not hasattr(self.controller, "on_exec_stats_change"):
            return
        p = self._exec2_pass_var.get()
        f = self._exec2_fail_var.get()
        self.controller.on_exec_stats_change(p + f, p, f, self._exec2_total_dies)

    def _exec2_update_yield(self):
        p = self._exec2_pass_var.get()
        f = self._exec2_fail_var.get()
        total = p + f
        pct = (p / total * 100) if total else 0.0
        self._exec2_pct_var.set(f"Yield:  {pct:.1f}%  ({p}/{total})")


    def _tab_results(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Results")

        wd_frame = ttk.LabelFrame(tab, text="Working Directory")
        wd_frame.pack(fill="x", padx=15, pady=(15, 0))
        ttk.Label(
            wd_frame,
            text="Will list all subfolders here "
                 "whose name ends with \"ata\" (case-insensitive)."
        ).pack(anchor="w", padx=10, pady=(8, 4))
        wd_row = ttk.Frame(wd_frame)
        wd_row.pack(fill="x", padx=10, pady=(4, 12))
        ttk.Label(wd_row, text="Working Directory:").pack(side="left")
        ttk.Entry(wd_row, textvariable=self.working_dir_var, width=40).pack(
            side="left", padx=6)
        ttk.Button(
            wd_row, text="Browse...", command=self.controller.cmd_browse_working_dir
        ).pack(side="left", padx=4)

        export_frame = ttk.LabelFrame(tab, text="Data Export")
        export_frame.pack(fill="x", padx=15, pady=15)

        ttk.Label(
            export_frame,
            text="Output filename:  <Lot ID>_<Wafer ID>_results.csv  "
                 "(Wafer ID omitted if blank)"
        ).pack(anchor="w", padx=10, pady=(8, 4))

        file_row = ttk.Frame(export_frame)
        file_row.pack(fill="x", padx=10, pady=4)
        ttk.Label(file_row, text="Lot ID:").pack(side="left")
        ttk.Entry(file_row, textvariable=self.lot_id, width=22).pack(side="left", padx=6)
        ttk.Label(file_row, text="Wafer ID:").pack(side="left", padx=(12, 0))
        ttk.Entry(file_row, textvariable=self.wafer_id_var, width=22).pack(side="left", padx=6)

        path_row = ttk.Frame(export_frame)
        path_row.pack(fill="x", padx=10, pady=(4, 12))
        ttk.Label(path_row, text="Export Path:").pack(side="left")
        ttk.Entry(path_row, textvariable=self.export_path_var, width=40).pack(side="left", padx=6)
        ttk.Button(
            path_row, text="Browse...", command=self.controller.cmd_browse_export
        ).pack(side="left", padx=4)
        ttk.Button(
            path_row, text="Save to CSV", command=self.controller.cmd_save_csv
        ).pack(side="left", padx=10)

        sql_row = ttk.Frame(export_frame)
        sql_row.pack(fill="x", padx=10, pady=(0, 12))
        ttk.Label(sql_row, text="Export Format:").pack(side="left")
        self.export_format_var = tk.StringVar()
        self._export_format_cb = ttk.Combobox(
            sql_row, textvariable=self.export_format_var, state="readonly", width=42)
        self._export_format_cb.pack(side="left", padx=6)
        ttk.Button(
            sql_row, text="💾 Export", command=self.controller.cmd_export_sql
        ).pack(side="left", padx=(4, 10))
        ttk.Button(
            sql_row, text="➕ New Format…", command=lambda: self._open_new_format_dialog()
        ).pack(side="left")
        ttk.Button(
            sql_row, text="✏ Edit Selected…", command=self._open_edit_format_dialog
        ).pack(side="left", padx=(6, 0))
        self._export_formats: list = []

        results_lf = ttk.LabelFrame(tab, text="Measurement Results")
        results_lf.pack(fill="both", expand=True, padx=15, pady=(0, 8))
        results_lf.rowconfigure(0, weight=1)
        results_lf.columnconfigure(0, weight=1)

        cols = ("timestamp", "recipe", "die", "step", "type", "value", "unit")
        self._results_tree = ttk.Treeview(
            results_lf, columns=cols, show="headings", height=8, selectmode="browse")
        heads = [("timestamp", "Time", 135), ("recipe", "Recipe", 110),
                 ("die", "Die", 90), ("step", "Step", 110), ("type", "Type", 75),
                 ("value", "Value", 90), ("unit", "Unit", 45)]
        for cid, text, width in heads:
            self._results_tree.heading(cid, text=text)
            self._results_tree.column(cid, width=width,
                                      anchor="center" if cid in ("type", "unit") else "w")
        self._results_tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        rsb = ttk.Scrollbar(results_lf, orient="vertical",
                            command=self._results_tree.yview)
        rsb.grid(row=0, column=1, sticky="ns", pady=6)
        self._results_tree.configure(yscrollcommand=rsb.set)

        ttk.Button(results_lf, text="Clear Results", command=self.clear_results).grid(
            row=1, column=0, columnspan=2, sticky="e", padx=6, pady=(0, 6))

        stats_frame = ttk.LabelFrame(tab, text="Run Statistics")
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.results_canvas = tk.Canvas(
            stats_frame, width=300, height=300, bg="#f0f0f0", highlightthickness=0
        )
        self.results_canvas.pack(pady=15)
        self.lbl_results_large = ttk.Label(
            stats_frame,
            text="Pass: 0   |   Fail: 0   |   Untested: 0",
            font=("Arial", 14, "bold")
        )
        self.lbl_results_large.pack(pady=8)


    def _refresh_export_formats(self, select_name: str = None):
        if not self._ata_folder:
            self._export_formats = []
            self._export_format_cb.config(values=[])
            self.export_format_var.set("")
            return
        self._export_formats = xfmt.load_formats(self._ata_folder, system=self._system)
        names = [f["name"] for f in self._export_formats]
        self._export_format_cb.config(values=names)
        if select_name in names:
            self.export_format_var.set(select_name)
        elif self.export_format_var.get() not in names:
            self.export_format_var.set(names[0] if names else "")

    def get_selected_export_format(self):
        name = self.export_format_var.get()
        return next((f for f in self._export_formats if f["name"] == name), None)

    def _open_edit_format_dialog(self):
        from tkinter import messagebox
        fmt = self.get_selected_export_format()
        if not fmt:
            messagebox.showerror("No Format Selected",
                                 "Pick a format from the Export Format dropdown first.")
            return
        self._open_new_format_dialog(existing_fmt=fmt)

    def _open_new_format_dialog(self, existing_fmt=None):
        from tkinter import messagebox
        if not self._ata_folder:
            messagebox.showerror(
                "No ATA Folder",
                "Load an ATA folder first — export formats are saved there "
                "(ata_export_formats.json).")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Edit Export Format" if existing_fmt else "New Export Format")
        dlg.transient(self.winfo_toplevel())
        dlg.resizable(True, True)

        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Format Name:").grid(row=0, column=0, sticky="e", pady=2)
        name_var = tk.StringVar(value=(existing_fmt or {}).get("name", ""))
        ttk.Entry(frm, textvariable=name_var, width=46).grid(
            row=0, column=1, columnspan=3, sticky="w", pady=2)

        ttk.Label(frm, text="Table Name:").grid(row=1, column=0, sticky="e", pady=2)
        table_var = tk.StringVar(value=(existing_fmt or {}).get("table", ""))
        ttk.Entry(frm, textvariable=table_var, width=46).grid(
            row=1, column=1, columnspan=3, sticky="w", pady=2)

        ttk.Label(frm, text="Format Type:").grid(row=2, column=0, sticky="e", pady=2)
        type_var = tk.StringVar(value=(existing_fmt or {}).get("type", "sql"))
        type_row = ttk.Frame(frm)
        type_row.grid(row=2, column=1, columnspan=3, sticky="w", pady=2)
        ttk.Radiobutton(type_row, text="SQL INSERT (one row per reading)",
                       variable=type_var, value="sql",
                       command=lambda: _on_type_change()).pack(side="left")
        ttk.Radiobutton(type_row, text="CSV (one row per die, merged)",
                       variable=type_var, value="csv",
                       command=lambda: _on_type_change()).pack(side="left", padx=(12, 0))

        only_pma_var = tk.BooleanVar(value=(existing_fmt or {}).get("requires_die_id", True))
        only_pma_chk = ttk.Checkbutton(
            frm, text="Only include Test PMA readings (has a die ID)",
            variable=only_pma_var)
        only_pma_chk.grid(row=3, column=0, columnspan=4, sticky="w", pady=(4, 8))

        detect_hint = tk.StringVar()
        ttk.Label(frm, text="Available fields (double-click, or select + Add):").grid(
            row=4, column=0, columnspan=4, sticky="w")
        ttk.Label(frm, textvariable=detect_hint, foreground="#6b7280",
                 font=("Segoe UI", 8), wraplength=460, justify="left").grid(
            row=5, column=0, columnspan=4, sticky="w")
        avail_row = ttk.Frame(frm)
        avail_row.grid(row=6, column=0, columnspan=4, sticky="nsew", pady=(2, 6))
        avail_list = tk.Listbox(avail_row, height=6, width=58, exportselection=False)
        avail_list.pack(side="left", fill="both", expand=True)
        ttk.Button(avail_row, text="Add Selected →",
                  command=lambda: _add_from_available()).pack(side="left", padx=(6, 0), anchor="n")
        avail_sources: list = []

        ttk.Label(frm, text="Columns (in output order):").grid(
            row=7, column=0, columnspan=4, sticky="w")
        cols_tree = ttk.Treeview(
            frm, columns=("field", "source", "quote", "transform"),
            show="headings", height=7)
        for cid, text, width in [("field", "Field Name", 130), ("source", "Source", 130),
                                 ("quote", "Quote", 55), ("transform", "Transform", 110)]:
            cols_tree.heading(cid, text=text)
            cols_tree.column(cid, width=width, anchor="w" if cid == "field" else "center")
        cols_tree.grid(row=8, column=0, columnspan=4, sticky="nsew", pady=(2, 6))

        order_row = ttk.Frame(frm)
        order_row.grid(row=9, column=0, columnspan=4, sticky="w")
        ttk.Button(order_row, text="▲ Move Up", command=lambda: move_col(-1)).pack(side="left")
        ttk.Button(order_row, text="▼ Move Down", command=lambda: move_col(1)).pack(
            side="left", padx=(6, 0))
        ttk.Button(order_row, text="Remove Selected", command=lambda: remove_col()).pack(
            side="left", padx=(6, 0))
        ttk.Button(order_row, text="Edit Selected", command=lambda: _edit_selected()).pack(
            side="left", padx=(6, 0))

        add_row = ttk.Frame(frm)
        add_row.grid(row=10, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        ttk.Label(add_row, text="Field:").pack(side="left")
        field_var = tk.StringVar()
        ttk.Entry(add_row, textvariable=field_var, width=14).pack(side="left", padx=(2, 8))
        ttk.Label(add_row, text="Source:").pack(side="left")
        source_var = tk.StringVar()
        source_cb = ttk.Combobox(add_row, textvariable=source_var, state="readonly", width=14)
        source_cb.pack(side="left", padx=(2, 8))
        quote_var = tk.BooleanVar(value=False)
        quote_chk = ttk.Checkbutton(add_row, text="Quote", variable=quote_var)
        quote_chk.pack(side="left")

        add_row2 = ttk.Frame(frm)
        add_row2.grid(row=11, column=0, columnspan=4, sticky="ew", pady=(4, 0))
        ttk.Label(add_row2, text="Multiply by:").pack(side="left")
        multiply_var = tk.StringVar()
        ttk.Entry(add_row2, textvariable=multiply_var, width=8).pack(side="left", padx=(2, 12))
        ttk.Label(add_row2, text="Or always use constant:").pack(side="left")
        constant_var = tk.StringVar()
        ttk.Entry(add_row2, textvariable=constant_var, width=14).pack(side="left", padx=(2, 8))
        ttk.Button(add_row2, text="+ Add Column", command=lambda: add_col()).pack(
            side="left", padx=(8, 0))

        _NICE = {"dmm": "DMM", "id": "ID", "num": "Num"}

        def _default_field_name(source):
            return "_".join(_NICE.get(p, p.capitalize()) for p in source.split("_"))

        def _fields_for_type():
            return xfmt.SOURCE_FIELDS_BY_TYPE.get(type_var.get(), {})

        def _populate_available():
            avail_list.delete(0, "end")
            avail_sources.clear()
            fields = _fields_for_type()
            source_cb.config(values=list(fields))
            if source_var.get() not in fields:
                source_var.set(next(iter(fields), ""))
            results = self.controller.results_data
            if type_var.get() == "csv":
                populated = {"lot_id", "wafer_id", "test_serial"}
                for g in xfmt.group_results_by_die(results):
                    for k, v in g.items():
                        if v not in (None, ""):
                            populated.add(k)
                for source, desc in fields.items():
                    mark = "✓" if source in populated else " "
                    avail_list.insert("end", f"[{mark}] {source}  —  {desc}")
                    avail_sources.append(source)
                detect_hint.set("✓ = this field has data in the current Results tab right now.")
            else:
                kinds = xfmt.detect_reading_kinds(results)
                for source, desc in fields.items():
                    avail_list.insert("end", f"{source}  —  {desc}")
                    avail_sources.append(source)
                if kinds:
                    detect_hint.set(
                        "Reading kinds detected in current Results: " +
                        ", ".join(k["label"] for k in kinds) +
                        ".  Each SQL row is ONE reading — to merge several reading "
                        "kinds into one row per die, use a CSV format instead.")
                else:
                    detect_hint.set(
                        "No results captured yet — run a recipe first, or pick "
                        "sources manually below.")

        def _on_type_change():
            if type_var.get() == "csv":
                only_pma_chk.grid_remove()
                quote_chk.pack_forget()
            else:
                only_pma_chk.grid(row=3, column=0, columnspan=4, sticky="w", pady=(4, 8))
                quote_chk.pack(side="left")
            _populate_available()

        def _add_from_available(_evt=None):
            sel = avail_list.curselection()
            if not sel:
                return
            source = avail_sources[sel[0]]
            field_var.set(_default_field_name(source))
            source_var.set(source)
            add_col()
        avail_list.bind("<Double-Button-1>", _add_from_available)

        def _parse_transform(txt):
            txt = (txt or "").strip()
            if txt.startswith("="):
                return {"constant": txt[1:].strip()}
            if txt[:1] in ("×", "x", "X"):
                try:
                    return {"multiply": float(txt[1:].strip())}
                except ValueError:
                    return {}
            return {}

        def add_col():
            field = field_var.get().strip()
            source = source_var.get().strip()
            constant = constant_var.get().strip()
            mult = multiply_var.get().strip()
            if not field or (not source and not constant):
                return
            transform_txt = f"={constant}" if constant else (f"×{mult}" if mult else "")
            cols_tree.insert("", "end", values=(
                field, source, "yes" if quote_var.get() else "no", transform_txt))
            field_var.set("")
            multiply_var.set("")
            constant_var.set("")

        def remove_col():
            sel = cols_tree.selection()
            if sel:
                cols_tree.delete(sel[0])

        def move_col(delta):
            sel = cols_tree.selection()
            if not sel:
                return
            iid = sel[0]
            idx = cols_tree.index(iid)
            cols_tree.move(iid, "", idx + delta)

        def _edit_selected(_evt=None):
            sel = cols_tree.selection()
            if not sel:
                return
            iid = sel[0]
            f, src, q, tr = cols_tree.item(iid, "values")
            field_var.set(f)
            if src in _fields_for_type():
                source_var.set(src)
            quote_var.set(q == "yes")
            parsed = _parse_transform(tr)
            multiply_var.set(str(parsed["multiply"]) if "multiply" in parsed else "")
            constant_var.set(parsed.get("constant", ""))
            cols_tree.delete(iid)
        cols_tree.bind("<Double-Button-1>", _edit_selected)

        if existing_fmt:
            for c in existing_fmt.get("columns", []):
                tr = ""
                if c.get("constant") not in (None, ""):
                    tr = f"={c['constant']}"
                elif c.get("multiply") not in (None, "", 1, 1.0):
                    tr = f"×{c['multiply']}"
                cols_tree.insert("", "end", values=(
                    c.get("field", ""), c.get("source", ""),
                    "yes" if c.get("quote") else "no", tr))

        def save():
            name = name_var.get().strip()
            table = table_var.get().strip()
            if not name or not table:
                messagebox.showerror("Incomplete", "Format Name and Table Name are required.")
                return
            columns = []
            for iid in cols_tree.get_children():
                f, src, q, tr = cols_tree.item(iid, "values")
                col = {"field": f, "source": src, "quote": q == "yes"}
                col.update(_parse_transform(tr))
                columns.append(col)
            if not columns:
                messagebox.showerror("Incomplete", "Add at least one column.")
                return
            fmt = {"name": name, "table": table, "type": type_var.get(),
                  "requires_die_id": only_pma_var.get(), "columns": columns}
            xfmt.add_format(self._ata_folder, fmt, system=self._system)
            self._refresh_export_formats(select_name=name)
            self.controller.log(f"[RESULTS] Saved export format '{name}' ({table}, "
                                f"{type_var.get()}) to ATA folder.")
            dlg.destroy()

        btns = ttk.Frame(frm)
        btns.grid(row=12, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        ttk.Button(btns, text="Save Format", command=save).pack(side="left")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right")

        _on_type_change()
        dlg.update_idletasks()
        dlg.grab_set()

    def draw_donut(self, canvas, size, passed, failed, untested):
        canvas.delete("all")
        cx, cy = size / 2, size / 2
        r_outer, r_inner = size * 0.45, size * 0.25
        total = passed + failed + untested or 1
        start = 90
        for count, color in [(passed, "#00d200"), (failed, "red"), (untested, "#d0d0d0")]:
            if count > 0:
                extent = (count / total) * 360
                canvas.create_arc(
                    cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                    start=start, extent=-extent, fill=color, outline=""
                )
                start -= extent
        canvas.create_oval(
            cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner,
            fill="#f0f0f0", outline=""
        )
        pct = int(((passed + failed) / total) * 100) if total > 1 else 0
        font_size = 11 if size < 150 else 24
        canvas.create_text(cx, cy, text=f"{pct}%", font=("Arial", font_size, "bold"), fill="#333333")
