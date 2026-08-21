import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import filedialog, messagebox
import os
import re
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
from eg_setup_panel import EgSetupPanel
from accretech_setup_panel import AccretechSetupPanel
from instrument_connection_panel import build_address_panel
from probe_routing_panel import scrollable_routing
from prober_debug_panel import ProberDebugPanel
from eg_prober_debug_panel import EgProberDebugPanel
from gpib_trace_panel import GpibTracePanel
from eg_pma_run_panel import EgPmaRunPanel
from accr_wafer_panel import AccrWaferPanel
from cassette_panel import CassettePanel
from recipe_panel import RecipePanel, load_default_recipe, compute_target_derived
from pma_wafer_panel import PmaWaferPanel, centroid_offset
from nanoz_panel import NanoZPanel
from pma_process_panel import PmaProcessPanel
from recipe_gen_panel import RecipeGenPanel, shot_die_rc, present_slots
import export_formats as xfmt
import mdb_export
import app_settings
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
        self._downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        default_export_dir = (r"\\prober\NewData\ETL\RAWDATA\PROBE08"
                              if self._system == "accretech" else self._downloads_dir)
        self.export_path_var = tk.StringVar(value=default_export_dir)
        self.working_dir_var = (getattr(controller, "working_dir_var", None)
                                or tk.StringVar(value="C:/automationproject"))
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
        sidebar = ttk.Frame(paned, width=230, relief="sunken", padding=5)
        paned.add(sidebar, weight=0)
        sidebar.pack_propagate(False)

        self.status_label = ttk.Label(
            sidebar, text="INITIALIZING", foreground="orange",
            font=("Arial", 11, "bold")
        )
        self.status_label.pack(anchor="w", pady=(0, 4))

        # Not packed - the separate "Prober: connected/not connected/ready/
        # not ready" line is gone; status_label above (PENDING/SYSTEM READY)
        # already covers whether the prober is usable. Left instantiated
        # (just not shown) so AtomicaDashboard._update_prober_status_label
        # doesn't need touching everywhere it's called from.
        self.prober_status_label = ttk.Label(
            sidebar, text="Prober: —", foreground="orange",
            font=("Arial", 9)
        )

        inst_frame = ttk.LabelFrame(sidebar, text="Instruments")
        inst_frame.pack(fill="x", pady=4)
        self._inst_frame = inst_frame
        for inst in self._instrument_names:
            lbl = ttk.Label(inst_frame, text=f"⏳ {inst}", foreground="orange")
            lbl.pack(anchor="w", padx=4, pady=2)
            self.status_labels[inst] = lbl
        self._refresh_conn_btn = ttk.Button(
            inst_frame, text="↻ Refresh Connections",
            command=self._init_hardware_fn)
        self._refresh_conn_btn.pack(pady=(8, 4), padx=4, fill="x")

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

    def set_visible_instruments(self, names):
        """Show only these in the sidebar roster, in the declared order.

        An instrument that is neither fitted nor pinged has no status to
        report, so listing it just adds a permanently grey row. The bench
        profile decides which those are, and it changes when the prober
        selector changes - hence re-applied on every connect sweep rather
        than fixed at build time.
        """
        missing = [n for n in (names or []) if n not in self.status_labels]
        if missing:
            # Not fatal, but the caller asked to show something with no row, so
            # it will silently never appear. Surfacing it beats hunting for a
            # bench instrument that is connected yet invisible.
            print(f"[MainLayout] no status row for: {', '.join(missing)}")
        wanted = set(names or [])
        for inst in self._instrument_names:
            lbl = self.status_labels.get(inst)
            if lbl is None:
                continue
            lbl.pack_forget()
            if inst in wanted:
                # before= keeps the Refresh button at the bottom; a bare
                # pack() would re-append the label underneath it.
                lbl.pack(anchor="w", padx=4, pady=2,
                         before=self._refresh_conn_btn)

    def set_bench_label(self, bench: str = ""):
        """Name the bench this roster is reporting on, in the frame's title.

        The Electroglas benches carry different instruments, so a roster with
        no bench on it is genuinely ambiguous - "Keithley 2400" missing could
        mean broken or simply not fitted here.
        """
        frame = getattr(self, "_inst_frame", None)
        if frame is None:
            return
        frame.config(text=f"Instruments — {bench}" if bench else "Instruments")

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

        # Run leads on both systems - it is what an operator opens the GUI to
        # do; the setup tabs behind it are visited far less often.
        self._tab_execution2(main_nb)
        if self._system == "accretech":
            # Cassette's export controls read self.export_format_var, which
            # _tab_results creates - built last so that already exists, then
            # both are moved to sit right after Run to match the intended
            # tab order (Run, Results, Cassette, Wafer Builder, Probe Card,
            # Recipe, Internal) without adding a second build-order
            # dependency.
            self._tab_pma_wafer(main_nb)
            self._tab_probe_card(main_nb)
            self._tab_recipe(main_nb)
            self._tab_wafer_map(main_nb)
            self._tab_results(main_nb)
            self._tab_cassette(main_nb)
            main_nb.insert(1, self.results_tab_frame)
            main_nb.insert(2, self.cassette_panel.master)
        else:
            # Electroglas has no cassette handling - order is Run, Results,
            # Recipe, Probe Card, PMA Process, Wafer Builder, Internal.
            self._tab_results(main_nb)
            self._tab_recipe(main_nb)
            self._tab_probe_card(main_nb)
            self._tab_pma_process(main_nb)
            self._tab_recipe_gen(main_nb)
            self._tab_wafer_map(main_nb)

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
        self._tab_setup(debug_nb)
        self._tab_gds_parser(debug_nb)
        self._tab_switch_settings(debug_nb)
        self._tab_prober_debug(debug_nb)
        self._tab_gpib_trace(debug_nb)

        self._build_exec_panel()
        self._build_alignment_panel()

        if self._system == "accretech":
            nanoz_frame = ttk.Frame(top_nb)
            top_nb.add(nanoz_frame, text="  NanoZ  ")
            self.nanoz_panel = NanoZPanel(nanoz_frame, controller=self.controller, main_layout=self)
            self.nanoz_panel.pack(fill="both", expand=True)
            self._nanoz_tab_frame = nanoz_frame
            top_nb.bind("<<NotebookTabChanged>>", self._on_top_tab_changed, add="+")

    def _on_top_tab_changed(self, event):
        nb = event.widget
        try:
            selected = nb.select()
        except Exception:
            return
        if selected != str(getattr(self, "_nanoz_tab_frame", None)):
            return
        # Clicking the NanoZ tab loads NAUTATA into the shared ATA folder,
        # exactly as if it had been picked from the toolbar's ATA Folder
        # dropdown — NanoZ doesn't track its own independent folder.
        if self._ata_folder and os.path.basename(self._ata_folder).lower() == "nautata":
            return
        working_dir = self.working_dir_var.get()
        if not working_dir or not os.path.isdir(working_dir):
            return
        match = next((n for n in os.listdir(working_dir)
                     if n.lower() == "nautata"
                     and os.path.isdir(os.path.join(working_dir, n))), None)
        if not match:
            self.controller.log(
                f"[SYSTEM] NanoZ tab: no NAUTATA folder found under '{working_dir}'.")
            return
        self.controller._do_load_ata_folder(os.path.join(working_dir, match))

    _ACCRETECH_INSTRUMENTS = [
        ("UF200R Prober", "prober"),
        ("Switch Matrix (Keithley 707B)", "switch_matrix"),
        ("SMU (Keithley 2636B)", "smu"),
        ("DMM (Keysight 34461A)", "dmm"),
        ("Wave Gen (Keysight 33512B)", "wave_gen"),
    ]

    def _build_addresses_accretech(self, parent, row: int):
        panel = build_address_panel(
            parent, self._ACCRETECH_INSTRUMENTS, self.controller.log, self._init_hardware_fn)
        panel.grid(row=row, column=0, sticky="ew", padx=8, pady=(6, 0))

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

        # Ping/address section - a diagnostic, not the first thing an
        # operator needs - sits below the instrument control panels.
        self._build_addresses_accretech(tab, row=3)

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

    def _build_default_prober_row(self, tab):
        """Which prober the GUI comes up on, across BOTH systems.

        Deliberately not per-system: the point is to decide whether the app
        starts on Accretech or Electroglas at all, so one list spans both and
        picking an entry sets the system as well as the bench.
        """
        lf = ttk.LabelFrame(tab, text="Default prober (used at startup)", padding=6)
        lf.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 4))

        ttk.Label(lf, text="Start the GUI on:").pack(side="left", padx=(0, 4))
        self._default_prober_var = tk.StringVar()
        self._default_prober_cb = ttk.Combobox(
            lf, textvariable=self._default_prober_var, state="readonly", width=32,
            postcommand=self._refresh_default_prober_choices)
        self._default_prober_cb.pack(side="left", padx=(0, 6))
        ttk.Button(lf, text="⭐ Set as Default",
                   command=self._set_default_prober).pack(side="left", padx=(0, 4))
        ttk.Button(lf, text="✖ Clear",
                   command=self._clear_default_prober).pack(side="left", padx=(0, 10))

        self._default_prober_lbl = ttk.Label(lf, text="", foreground="#374151",
                                             font=("Segoe UI", 8, "italic"))
        self._default_prober_lbl.pack(side="left")
        self._refresh_default_prober_choices()
        self._update_default_prober_label()

    def _prober_choices(self) -> list:
        """[(label, system, bench)] for every prober on both systems."""
        out = [(f"Accretech — {b}", "accretech", b)
               for b in self.controller.accretech_benches()]
        for b in self.controller.electroglas_benches():
            out.append((f"Electroglas — {b}", "electroglas", b))
        return out

    def _refresh_default_prober_choices(self):
        self._prober_choice_map = {lab: (s, b) for lab, s, b in self._prober_choices()}
        self._default_prober_cb.config(values=list(self._prober_choice_map))
        if not self._default_prober_var.get():
            system, bench = app_settings.get_default_prober()
            match = next((lab for lab, (s, b) in self._prober_choice_map.items()
                          if s == system and b == bench), "")
            self._default_prober_var.set(match)

    def _update_default_prober_label(self):
        system, bench = app_settings.get_default_prober()
        if not system:
            self._default_prober_lbl.config(
                text="no default — the GUI starts on Accretech", foreground="#6b7280")
        else:
            self._default_prober_lbl.config(
                text=f"default: {system} / {bench}", foreground="#166534")

    def _set_default_prober(self):
        from tkinter import messagebox
        label = self._default_prober_var.get()
        pick = getattr(self, "_prober_choice_map", {}).get(label)
        if not pick:
            messagebox.showinfo("Default prober", "Pick a prober from the list first.")
            return
        system, bench = pick
        app_settings.set_default_prober(system, bench)
        self._update_default_prober_label()
        self.controller.log(
            f"[SYSTEM] Default prober set to {system} / {bench} — the GUI will "
            f"start on {'Electroglas' if system == 'electroglas' else 'Accretech'}.")
        # Switch to it now too, so the setting is visibly what you just chose
        # rather than something that only takes effect next launch.
        self.controller.apply_prober(system, bench)

    def _clear_default_prober(self):
        app_settings.clear_default_prober()
        self._default_prober_var.set("")
        self._update_default_prober_label()
        self.controller.log("[SYSTEM] Default prober cleared.")

    def _tab_wafer_map(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Internal")
        tab.rowconfigure(2, weight=1)          # the file list / map split
        tab.columnconfigure(0, weight=1)

        ctrl = ttk.Frame(tab)
        ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))

        ttk.Button(ctrl, text="📁 Load ATA Folder…",
                  command=self.controller.cmd_import_map).pack(side="left", padx=(0, 10))
        ttk.Button(ctrl, text="＋ New ATA Folder…",
                  command=self.controller.cmd_new_ata_folder).pack(side="left", padx=(0, 10))
        ttk.Button(ctrl, text="⭐ Set as Default",
                  command=self._set_default_ata_folder).pack(side="left", padx=(0, 10))
        # Moved in from the top toolbar's "ATA Folder:" row.
        ttk.Button(ctrl, text="↻ Refresh",
                  command=self.controller.cmd_refresh_ata).pack(side="left", padx=(0, 10))

        ttk.Label(ctrl, text="Working Directory:").pack(side="left", padx=(0, 4))
        # Preset picker (automationproject / proberautomation) - the Entry
        # next to it still shows/accepts the full path either way (a preset
        # just fills it in), so a one-off custom path via Browse still works.
        import workdir as _workdir
        self._workdir_preset_var = tk.StringVar(value="")
        preset_box = ttk.Combobox(
            ctrl, textvariable=self._workdir_preset_var, state="readonly",
            width=16, values=list(_workdir.PRESETS.keys()))
        preset_box.pack(side="left", padx=(0, 4))
        preset_box.bind("<<ComboboxSelected>>",
                        lambda _e: self.controller.cmd_pick_working_dir_preset(
                            self._workdir_preset_var.get()))
        ttk.Entry(ctrl, textvariable=self.working_dir_var, width=26).pack(
            side="left", padx=(0, 4))
        ttk.Button(
            ctrl, text="Browse...", command=self.controller.cmd_browse_working_dir
        ).pack(side="left", padx=(0, 4))
        ttk.Button(
            ctrl, text="⭐ Set Default", command=self.controller.cmd_set_default_working_dir
        ).pack(side="left", padx=(0, 10))

        self._ata_path_lbl = ttk.Label(ctrl, text="No folder selected", foreground="gray")
        self._ata_path_lbl.pack(side="left", padx=10)

        self._default_ata_lbl = ttk.Label(ctrl, text="", foreground="#374151",
                                          font=("Segoe UI", 8, "italic"))
        self._default_ata_lbl.pack(side="left", padx=(0, 10))
        self._update_default_ata_label()

        self._build_default_prober_row(tab)

        # Same fix as the Run tab's _exec2_map_source_var: Electroglas has no
        # hardware-extracted map of its own - the legacy "Electroglas" source
        # (ata_wafer_map_electroglas.csv) is whatever the old PMA Process
        # extraction last wrote, often stale or a placeholder rectangle (see
        # MADDYATA). There is no picker for this var - it is set once here
        # and never touched again - so getting the default right matters.
        self._map_source_var = tk.StringVar(
            value="Accretech" if self._system == "accretech" else "Wafer Builder")

        split = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        split.grid(row=2, column=0, sticky="nsew", padx=6, pady=(2, 6))

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
        # Drop the recipe the Run tab adopted from the PREVIOUS folder. Its
        # touchdowns, anchor list and row/col index all belong to that wafer,
        # and nothing else clears them - so switching folder left the Run tab
        # offering the old wafer's dies over the new wafer's map, with the two
        # silently disagreeing about what a given square is.
        run = getattr(self, "eg_pma_run", None)
        reset = getattr(run, "forget_recipe", None)
        if callable(reset):
            try:
                reset()
            except Exception as exc:
                self._exec2_log(f"[RUN] Could not reset the Run tab for the new "
                                f"ATA folder: {type(exc).__name__}: {exc}")
        # NOT here yet - _exec2_autoload_default_recipe (moved below,
        # after the new wafer map is actually drawn) selects the recipe's
        # touchdowns via self._exec2_wafer_map.set_picked(), which needs
        # self._exec2_wafer_map.dies to already be this folder's dies. This
        # early in the method it is still the PREVIOUS folder's (or empty on
        # the very first load), so the picks it set matched nothing - and
        # either way clear_picks()/_on_sites_changed([]) below wiped them a
        # few lines later regardless. That is why the highlight sometimes
        # would not show up right after an autoload.

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
                values=("–", "probe_cards/", "No probe cards yet — create one on Probe Card"),
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
        pma_wafer = getattr(self, "pma_wafer", None)
        if pma_wafer is not None:
            pma_wafer.load_from_ata(folder_path)
        recipe_gen = getattr(self, "recipe_gen", None)
        if recipe_gen is not None:
            recipe_gen.autoload_map_for_folder(folder_path)
        self._exec2_map_folder = folder_path
        # Electroglas has no hardware-extracted map of its own anymore - the
        # Wafer Builder tab (synced above via autoload_map_for_folder) IS the
        # wafer there. Defaulting back to the legacy "Electroglas" source
        # here would silently reintroduce whatever ata_wafer_map_electroglas
        # .csv happens to still be sitting in the folder from the old PMA
        # Process extraction (often stale or a placeholder rectangle) even
        # though _sync_views already pointed the Run tab at "Wafer Builder"
        # the last time a map was actually published from that tab.
        self._exec2_map_source_var.set(
            "Accretech" if self._system == "accretech" else "Wafer Builder")
        # The drawn overlay (canvas items + die_ids) belongs to the PREVIOUS
        # folder's map and is stale the instant the map changes underneath
        # it - cleared here unconditionally. The alignment itself (row/col
        # offset + confirmed flag) is NOT touched by this: recipe_gen's
        # autoload_map_for_folder (above) already restored it from the new
        # folder's own saved Wafer Builder map, if that map ever had one
        # confirmed - see recipe_gen_panel._state_from_dict. It gets
        # re-drawn below, once the new folder's Accretech map is actually on
        # screen.
        self._exec2_clear_overlay()
        self._exec2_wafer_map.clear_picks()
        self._exec2_on_sites_changed([])
        nanoz_panel = getattr(self, "nanoz_panel", None)
        if nanoz_panel is not None and hasattr(nanoz_panel, "_clear_overlay"):
            nanoz_panel._clear_overlay()
            nanoz_panel.wafer_map.clear_picks()
            nanoz_panel._on_sites_changed([])
        self._exec2_draw_wafer_map(quiet_if_missing=True)
        self._exec2_reapply_overlay()
        self._refresh_export_formats()

        pma_process = getattr(self, "pma_process", None)
        if pma_process is not None:
            try:
                pma_process.scan_ata_folder()
            except Exception:
                pass

        # Now that the map actually holds this folder's dies (and the picks
        # from the previous folder are cleared), the default recipe's
        # touchdowns can be selected and will actually paint. This also has
        # to be AFTER pma_process.scan_ata_folder() above, not just after
        # the map draw: _exec2_apply_recipe_sites expands each selected site
        # into its WHOLE shot via eg_pma_run._seq_at_rc/_cells, and those are
        # only populated once eg_pma_run has adopted a recipe and built its
        # row/col index (_build_rc_index, via scan_ata_folder's own PMA
        # autoload -> adopt_from_process). Selecting sites before that index
        # exists does not fail loudly - _exec2_touchdown_cells falls back to
        # the raw (row, col) picks with no shot expansion - so only the
        # anchor die of each shot got selected, not the whole quad. A manual
        # reselect from the Recipe dropdown later worked fine because by then
        # the index was already built, which made this look intermittent.
        self._exec2_autoload_default_recipe(folder_path)

        nanoz = getattr(self, "nanoz_panel", None)
        if nanoz is not None:
            try:
                nanoz.on_ata_folder_loaded(folder_path)
            except Exception:
                pass

        self._update_default_ata_label()
        return n_dies

    def _set_default_ata_folder(self):
        from tkinter import messagebox
        if not self._ata_folder:
            messagebox.showerror("No ATA Folder", "Load an ATA folder first.")
            return
        app_settings.set_default_ata_folder(self._ata_folder)
        self._update_default_ata_label()
        self.controller.log(
            f"[SYSTEM] '{os.path.basename(self._ata_folder)}' set as the default "
            "ATA folder for the project — auto-loads on startup and when "
            "switching systems or probers.")

    def _update_default_ata_label(self):
        default_folder = app_settings.get_default_ata_folder()
        if default_folder:
            is_current = (default_folder == self._ata_folder)
            self._default_ata_lbl.config(
                text=("⭐ default: this folder" if is_current
                      else f"⭐ default: {os.path.basename(default_folder)}"))
        else:
            self._default_ata_lbl.config(text="")

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

    def _tab_probe_card(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Probe Card")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        split = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        split.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        self.pin_wiring = ProbeCardWiringFrame(
            split,
            get_folder=lambda: self._ata_folder,
            log_fn=self.controller.log,
            on_card_change=self._on_probe_card_change,
            on_pins_change=lambda: self.pad_panel.refresh_pins(),
            system=self._system,
            # Save All covers the hand-drawn Custom pad sketch too now, so
            # there is one save button for the whole tab instead of two.
            on_save_all=lambda: self._save_custom_pads(quiet=True),
        )
        split.add(self.pin_wiring, weight=1)

        right_col = ttk.PanedWindow(split, orient=tk.VERTICAL, width=340)
        split.add(right_col, weight=0)

        list_frame = ttk.LabelFrame(right_col, text="Pads")
        right_col.add(list_frame, weight=1)

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

        pad_container = ttk.Frame(right_col)
        right_col.add(pad_container, weight=1)
        pad_container.rowconfigure(0, weight=1)
        pad_container.columnconfigure(0, weight=1)

        self.pad_panel = PadLayoutPanel(pad_container, on_custom_change=self._refresh_pad_tree_from_custom,
                                        get_pins=self.pin_wiring.get_wiring,
                                        rename_pad=self.pin_wiring.rename_pad)
        self.pad_panel.grid(row=0, column=0, sticky="nsew")

        pad_ctrl = ttk.Frame(pad_container)
        pad_ctrl.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Label(pad_ctrl, text="Layout:").pack(side="left")
        self._pad_source_var = tk.StringVar(value="Custom")
        pad_source_cb = ttk.Combobox(pad_ctrl, textvariable=self._pad_source_var,
                                     values=["ATA", "Custom"], state="readonly", width=8)
        pad_source_cb.pack(side="left", padx=(4, 8))
        pad_source_cb.bind("<<ComboboxSelected>>", lambda _e: self._on_pad_source_change())
        self._btn_pad_clear = ttk.Button(pad_ctrl, text="🗑 Clear", state="disabled",
                                         command=self._clear_custom_pads)
        self._btn_pad_clear.pack(side="left", padx=2)
        self._btn_pad_add_die = ttk.Button(pad_ctrl, text="▭ Add Die", state="disabled",
                                           command=self._add_custom_die)
        self._btn_pad_add_die.pack(side="left", padx=2)
        ttk.Label(pad_ctrl, text="Custom Sketch — saved by 💾 Save All, top of tab",
                 foreground="#6b7280", wraplength=420, justify="left").pack(side="left", padx=(10, 0))

        self._on_pad_source_change()

    def _on_pad_source_change(self):
        source = self._pad_source_var.get()
        if source == "Custom":
            if not self._pad_custom_loaded and self._ata_folder:
                self.pad_panel.load_custom(self._ata_folder)
                self._pad_custom_loaded = True
            self.pad_panel.set_source("custom")
            self._btn_pad_clear.config(state="normal")
            self._btn_pad_add_die.config(state="normal")
            self._refresh_pad_tree_from_custom()
        else:
            self.pad_panel.set_source("ata")
            self._btn_pad_clear.config(state="disabled")
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

    def _save_custom_pads(self, quiet: bool = False):
        if not self._ata_folder:
            if not quiet:
                from tkinter import messagebox
                messagebox.showerror("No ATA Folder", "Load an ATA folder from the toolbar first.")
            return
        path = self.pad_panel.save_custom(self._ata_folder)
        self._pad_custom_loaded = True
        self.controller.log(f"[PAD] Custom layout saved to {path}")

    def _exec2_on_card_picked(self):
        name = self._exec2_card_var.get()
        if not hasattr(self, "pin_wiring"):
            return
        if name != self.pin_wiring.get_active_card():
            self.pin_wiring.switch_to_card(name)

    def _on_probe_card_change(self, card_name: str):
        if hasattr(self, "_exec2_card_var"):
            self._exec2_card_cb.config(values=[""] + sorted(self.pin_wiring.get_card_names()))
            self._exec2_card_var.set(card_name)
        # Nothing to tell Wafer Builder here any more: the Shot tab used to
        # hold the card's die-to-pin table and had to follow a card change,
        # but pins are picked per measurement step on the Recipe tab now, so
        # a shot is the same shot whichever card is loaded.
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
                "(pick it again from the Recipe dropdown for the new card).")
        if hasattr(self.controller, "check_system_ready"):
            self.controller.check_system_ready()

    def load_pad_layout(self, folder_path):
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
                if hasattr(self, "pin_wiring") else False),
            switch_card=lambda name: (self.pin_wiring.switch_to_card(name)
                                      if hasattr(self, "pin_wiring") else None),
            get_card_names=lambda: (self.pin_wiring.get_card_names_for_system()
                                    if hasattr(self, "pin_wiring") else []),
            get_ata_folder=lambda: self._ata_folder,
            get_die_pins=lambda: (self.pin_wiring.get_die_pins()
                                  if hasattr(self, "pin_wiring") else {}),
            on_save=self._exec2_load_recipe_by_name)
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
            nb.add(tab, text="Switch Settings")
            self.switch_debug = SwitchboxTestPanel(tab, controller=self.controller)
            self.switch_debug.grid(row=0, column=0, sticky="nsew")

    def _tab_instruments_eg(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Instruments")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.instruments_eg = InstrumentsEgPanel(tab, controller=self.controller)
        self.instruments_eg.grid(row=0, column=0, sticky="nsew")

    def _tab_setup(self, nb):
        """Add/edit prober benches and their instrument fitment - separate
        implementations per system (see eg_setup_panel.py/
        accretech_setup_panel.py's module docstrings for why: Electroglas
        already has real per-bench profiles to edit, Accretech has one
        fixed bench with no such infrastructure yet)."""
        tab = ttk.Frame(nb)
        nb.add(tab, text="Setup")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        if self._system == "accretech":
            self.setup_panel = AccretechSetupPanel(
                tab, controller=self.controller, main_layout=self)
        else:
            self.setup_panel = EgSetupPanel(
                tab, controller=self.controller, main_layout=self)
        self.setup_panel.grid(row=0, column=0, sticky="nsew")

    def _tab_probe_routing(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Switch Routing")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        holder, self.probe_routing = scrollable_routing(tab, self.controller)
        holder.grid(row=0, column=0, sticky="nsew")

    def _tab_prober_debug(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Prober Debug")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        if self._system == "accretech":
            self.prober_debug = ProberDebugPanel(tab, controller=self.controller)
        else:
            self.prober_debug = EgProberDebugPanel(tab, controller=self.controller)
        self.prober_debug.grid(row=0, column=0, sticky="nsew")

    def _tab_gpib_trace(self, nb):
        """Live view of every GPIB/USB command this app itself sends - see
        gpib_trace_panel.py/instruments/gpib_trace.py for what it can and
        can't see (LabVIEW's own traffic needs NI I/O Trace alongside it)."""
        tab = ttk.Frame(nb)
        nb.add(tab, text="GPIB Trace")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.gpib_trace_panel = GpibTracePanel(tab, controller=self.controller)
        self.gpib_trace_panel.grid(row=0, column=0, sticky="nsew")

    def _tab_cassette(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Cassette")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.cassette_panel = CassettePanel(tab, controller=self.controller, ui=self)
        self.cassette_panel.grid(row=0, column=0, sticky="nsew")

    def _tab_pma_wafer(self, nb):
        """Accretech's Wafer Builder - same RecipeGenPanel (Shot/Shot Map/
        Die Map) Electroglas uses, via _tab_recipe_gen, plus Accr Wafer
        (the hardware extraction) as its own first sub-tab rather than a
        separate top-level tab - it feeds the same wafer, so it lives where
        the rest of the wafer-building work does. Load PMA/Load Recipe Gen
        (.xls) autofill Shot/Shot Map/Die Map exactly like Import CSV does,
        just from an older file.

        PmaWaferPanel is still built - just not shown - and still assigned
        to self.pma_wafer: the Overlay dialog (available on Accretech's Run
        tab) reads self.pma_wafer.workbook_data/_pma_shot_data/etc
        defensively via getattr for its PMA/xls/csv comparison sources, so
        keeping the object alive avoids breaking that even though there is
        no more UI here to feed it from.
        """
        tab = ttk.Frame(nb)
        nb.add(tab, text="Wafer Builder")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        self.recipe_gen = RecipeGenPanel(tab, controller=self.controller,
                                         main_layout=self, system="accretech")
        self.recipe_gen.grid(row=0, column=0, sticky="nsew")

        accr_tab = ttk.Frame(self.recipe_gen._sub_nb)
        accr_tab.rowconfigure(0, weight=1)
        accr_tab.columnconfigure(0, weight=1)
        self.accr_wafer = AccrWaferPanel(accr_tab, controller=self.controller,
                                         get_folder=lambda: self._ata_folder)
        self.accr_wafer.grid(row=0, column=0, sticky="nsew")
        self.recipe_gen._sub_nb.insert(0, accr_tab, text="Accr Wafer")

        hidden = ttk.Frame(tab)
        self.pma_wafer = PmaWaferPanel(
            hidden, controller=self.controller, get_folder=lambda: self._ata_folder,
            main_layout=self)
        self.pma_wafer.grid(row=0, column=0, sticky="nsew")

    def _tab_pma_process(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="PMA Process")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        self.pma_process = PmaProcessPanel(tab, controller=self.controller, main_layout=self)
        self.pma_process.grid(row=0, column=0, sticky="nsew")

    def _tab_recipe_gen(self, nb):
        """The Wafer Builder tab on Electroglas - RecipeGenPanel owns three
        pages of its own (Shot / Shot Map / Die Map) that together replace
        the old Build/Edit + read-only Wafer View split entirely.

        PmaWaferPanel is still built - just not shown - and still assigned
        to self.pma_wafer: other code (the Overlay dialog,
        _exec2_overlay_source_data, centroid matching against an Accretech
        map) reads self.pma_wafer.workbook_data/_pma_shot_data/etc
        defensively via getattr, so keeping the object alive avoids breaking
        those paths even though there is no more .PMA/.xls-driven UI to feed
        it from this tab.
        """
        tab = ttk.Frame(nb)
        nb.add(tab, text="Wafer Builder")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        self.recipe_gen = RecipeGenPanel(tab, controller=self.controller,
                                         main_layout=self)
        self.recipe_gen.grid(row=0, column=0, sticky="nsew")

        hidden = ttk.Frame(tab)
        self.pma_wafer = PmaWaferPanel(
            hidden, controller=self.controller, get_folder=lambda: self._ata_folder,
            main_layout=self)
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
        # Set per touchdown by the Electroglas run so exports name the whole
        # shot; blank means fall back to the map/overlay per-cell die ID.
        self._exec2_die_id_override = ""
        self._exec2_total_dies = 0
        # Bumped on every start/abort. A run thread captures its own token and
        # re-checks it at every loop step/finish — if a new run (or an abort)
        # bumps the token out from under it, the stale thread stops touching
        # shared state/hardware instead of racing the new run and silently
        # "resuming" its own old loop.
        self._exec2_run_token = 0
        self._exec2_lot_thread: threading.Thread | None = None
        # Cassette automation hooks into this - set to a callable
        # fn(pass_n, fail_n, total_n, aborted) to be notified whenever a run
        # (Full Die today) finishes, instead of polling _exec2_running.
        self._exec2_on_run_finished = None
        # Index into controller.results_data where the most recently started
        # run began — export formats (unlike "Save as CSV") only export from
        # here onward, so re-running doesn't pile old runs' rows into a new
        # export.
        self._exec2_last_run_start_idx = 0
        self._exec2_steps    = []
        self._exec2_current_rc = None
        self._exec2_overlay_row_offset = 0
        self._exec2_overlay_col_offset = 0
        self._exec2_overlay_offset_confirmed = False
        self._exec2_overlay_items: list = []
        self._exec2_overlay_result_items: list = []
        self._exec2_overlay_die_ids: dict = {}
        # Accretech's equivalent of NanoZ's 1x20 window / Electroglas's 2x2
        # quad window - see _exec2_update_shot_window.
        self._exec2_shot_window_items: list = []
        # ➡ Move to Selected's own arm/target state - see
        # _exec2_move_selected_button. Deliberately separate from the
        # normal pick system (_exec2_wafer_map._picked/get_picked()).
        self._exec2_move_armed = False
        self._exec2_move_target_rc = None
        self._exec2_move_target_prev_fill = None
        self._exec2_move_prev_click_handler = None
        self._exec2_move_prev_picking_enabled = True

        ctrl = tk.Frame(tab, bg="#f1f5f9", relief="solid", bd=1)
        ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))

        tk.Label(ctrl, text="Recipe:", bg="#f1f5f9").pack(side="left", padx=(10, 2), pady=6)
        self._exec2_recipe_var = tk.StringVar()
        self._exec2_recipe_cb = ttk.Combobox(
            ctrl, textvariable=self._exec2_recipe_var, width=20, state="readonly",
            postcommand=lambda: self._exec2_recipe_cb.config(
                values=self.recipe_panel.get_recipe_names()))
        self._exec2_recipe_cb.pack(side="left", pady=6)
        self._exec2_recipe_cb.bind(
            "<<ComboboxSelected>>", lambda _e: self._exec2_load_recipe())

        tk.Label(ctrl, text="Probe Card:", bg="#f1f5f9").pack(side="left", padx=(10, 2), pady=6)
        self._exec2_card_var = tk.StringVar(value="")
        self._exec2_card_cb = ttk.Combobox(
            ctrl, textvariable=self._exec2_card_var, width=14, state="readonly")
        self._exec2_card_cb.pack(side="left", pady=6)
        self._exec2_card_cb.bind("<<ComboboxSelected>>",
                                 lambda _e: self._exec2_on_card_picked())

        ttk.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)

        self._exec2_full_btn = ttk.Button(
            ctrl, text="▶  Full Die", command=self._exec2_start_full_die)
        self._exec2_full_btn.pack(side="left", padx=4, pady=5)
        # Kept but not packed on either system - Test Selected replaces it as
        # the sole "test some dies" entry point, but _exec2_abort/
        # _exec2_finish_run/_exec2_start_test_die still toggle its state
        # alongside _exec2_full_btn regardless of which system this is, so
        # the attribute stays around either way.
        self._exec2_test_btn = ttk.Button(
            ctrl, text="▶  Test Die", command=self._exec2_start_test_die)
        self._exec2_test_selected_btn = ttk.Button(
            ctrl, text="▶  Test Selected", command=self._exec2_start_test_selected)
        self._exec2_test_selected_btn.pack(side="left", padx=2, pady=5)

        ttk.Separator(ctrl, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)

        # The real, full-story entry point - recipe steps, the recipe's own
        # saved touchdown list, Minor Moves (Accretech) and all - unlike
        # Full Die/Test Selected to its left, which stay the plain
        # single-die case only (see _exec2_start_run's docstring). To the
        # RIGHT of the separator, immediately next to Unload: it starts the
        # wafer, and sitting among Full Die/Test Selected/Unload (which
        # only ever touch one die) made it indistinguishable from them.
        #
        # Green border, default everything else. Drawn as a frame BEHIND
        # the button rather than a ttk style: Windows' native button themes
        # paint their own border and ignore a style's bordercolor entirely,
        # so the only way to get a coloured edge without switching the
        # whole app to 'clam' is to let a coloured frame show through
        # around it.
        run_border = tk.Frame(ctrl, background="#15803d")
        run_border.pack(side="left", padx=(2, 6), pady=5)
        ttk.Button(run_border, text="▶  Run",
                   command=(lambda: self.eg_pma_run._run_all())
                           if self._system == "electroglas"
                           else self._exec2_start_run).pack(padx=2, pady=2)

        for label, cmd in [
            ("⏏  Unload (U)",  self._exec2_manual_unload),
            # Pause is what ⏹ Stop Run used to do: finish what is in
            # progress and hold, keeping the position so Run resumes. Stop
            # is now a real stop - see _exec2_abort.
            ("⏸  Pause",       self._exec2_pause),
            ("⏹  Stop Run",       self._exec2_abort),
        ]:
            ttk.Button(ctrl, text=label, command=cmd).pack(side="left", padx=3, pady=5)

        self._exec2_state_lbl = tk.Label(
            ctrl, text="IDLE", bg="#f1f5f9", fg="#6b7280",
            font=("Segoe UI", 11, "bold"))
        self._exec2_state_lbl.pack(side="right", padx=12)

        body = ttk.PanedWindow(tab, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 6))

        # Electroglas drives a .PMA as relative die steps anchored on a die the
        # operator names, which has nothing in common with the Accretech flow
        # above - so it gets its own pane rather than being woven into it.
        if self._system == "electroglas":
            self.eg_pma_run = EgPmaRunPanel(body, controller=self.controller,
                                            main_layout=self)
            body.add(self.eg_pma_run, weight=1)

        left_col = ttk.Frame(body)
        body.add(left_col, weight=1)
        left_col.rowconfigure(0, weight=0)
        left_col.rowconfigure(1, weight=1)
        left_col.columnconfigure(0, weight=1)

        # Chuck Position and Pass/Fail share one row, side by side, rather
        # than each owning a whole section of their own (Accretech used to
        # give Pass/Fail an entire extra pane to the right of the wafer
        # map; Electroglas stacked it under Chuck Position instead) - same
        # total footprint, just laid out as two boxes across instead of
        # stacked or off in their own pane.
        pos_row = ttk.Frame(left_col)
        pos_row.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        pos_row.columnconfigure(0, weight=1)
        pos_row.columnconfigure(1, weight=1)
        pos_row.rowconfigure(0, weight=1)

        pos_lf = ttk.LabelFrame(pos_row, text="Chuck Position", padding=6)
        pos_lf.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        pos_lf.columnconfigure(0, weight=1)
        pos_lf.columnconfigure(1, weight=1)

        self._exec2_xy_var = tk.StringVar(value="X: —\nY: —")
        ttk.Label(pos_lf, textvariable=self._exec2_xy_var,
                  font=("Consolas", 13, "bold"), foreground="#0077cc",
                  justify="center").grid(row=0, column=0, columnspan=2, pady=(0, 2))

        self._exec2_die_var = tk.StringVar(value="Die: —")
        ttk.Label(pos_lf, textvariable=self._exec2_die_var,
                  font=("Consolas", 9), foreground="#374151",
                  justify="center").grid(row=1, column=0, columnspan=2)

        self._exec2_step_var = tk.StringVar(value="Step: —")
        ttk.Label(pos_lf, textvariable=self._exec2_step_var,
                  font=("Consolas", 9), foreground="#6b7280",
                  justify="center").grid(row=2, column=0, columnspan=2, pady=(0, 4))

        ttk.Separator(pos_lf, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=3)

        # 3x2 grid: Measure/First Die, Z Up/Z Down, Back/Next, then (Accretech
        # only) Move to Selected and ↻ Refresh XY. Reset Counts moved to the
        # Pass/Fail section, next to what it resets - not here anymore.
        ttk.Button(pos_lf, text="Measure",
                   command=self._exec2_touchdown_measure).grid(
                   row=4, column=0, sticky="ew", padx=(0, 1), pady=1)
        ttk.Button(pos_lf, text="⏮ First Die", command=self._exec2_manual_go_to_start).grid(
                   row=4, column=1, sticky="ew", padx=(1, 0), pady=1)
        ttk.Button(pos_lf, text="⬆ Z Up", command=self._exec2_manual_z_up).grid(
                   row=5, column=0, sticky="ew", padx=(0, 1), pady=1)
        ttk.Button(pos_lf, text="⬇ Z Down", command=self._exec2_manual_z_down).grid(
                   row=5, column=1, sticky="ew", padx=(1, 0), pady=1)
        if self._system == "electroglas":
            # ▶▶ Next Die (an Accretech-shaped "advance one die" action) is
            # replaced by EgPmaRunPanel's own ⏭ Next/⏮ Back - moved in from
            # that pane's former Run section, since single-die-step
            # advancing through the touchdown list IS what Back/Next mean
            # for a .PMA step-through.
            ttk.Button(pos_lf, text="⏮ Back",
                       command=lambda: self.eg_pma_run._step_back()).grid(
                       row=6, column=0, sticky="ew", padx=(0, 1), pady=1)
            ttk.Button(pos_lf, text="⏭ Next",
                       command=lambda: self.eg_pma_run._step_once()).grid(
                       row=6, column=1, sticky="ew", padx=(1, 0), pady=1)
        else:
            # Accretech has no native "previous die" GPIB command (only "J"
            # Next Die) - Back is a plain relative die-index step backward
            # instead (S command), the closest "die mode" equivalent to
            # Next's bare J. Neither touches the picked-sites list or shots
            # - see _exec2_manual_prev_die/_exec2_manual_next_die.
            ttk.Button(pos_lf, text="⏮ Back",
                       command=self._exec2_manual_prev_die).grid(
                       row=6, column=0, sticky="ew", padx=(0, 1), pady=1)
            ttk.Button(pos_lf, text="⏭ Next",
                       command=self._exec2_manual_next_die).grid(
                       row=6, column=1, sticky="ew", padx=(1, 0), pady=1)
            ttk.Button(pos_lf, text="⏮⏮ Previous Shot",
                       command=self._exec2_manual_prev_shot).grid(
                       row=7, column=0, sticky="ew", padx=(0, 1), pady=1)
            ttk.Button(pos_lf, text="⏭⏭ Next Shot",
                       command=self._exec2_manual_next_shot).grid(
                       row=7, column=1, sticky="ew", padx=(1, 0), pady=1)
            # Its own separate arm/target system - see
            # _exec2_move_selected_button's docstring - deliberately not
            # tied to the normal pick system (Test Selected's picks) at all.
            self._exec2_move_selected_btn = ttk.Button(
                pos_lf, text="➡ Move to Selected",
                command=self._exec2_move_selected_button)
            self._exec2_move_selected_btn.grid(
                row=8, column=0, columnspan=2, sticky="ew", pady=1)
            # Manual, fire-and-forget version of the same Q read
            # _exec2_refresh_xy_blocking runs automatically (and blocking)
            # right before Full Die/Test Die/Test Selected/Minor Moves'
            # first move - see that method.
            ttk.Button(pos_lf, text="↻ Refresh XY", command=self._exec2_get_xy).grid(
                row=9, column=0, columnspan=2, sticky="ew", pady=1)

        # Recipe Steps is the one that grows, so it takes the weighted row on
        # both systems - Chuck Position/Pass-Fail (row 0, above) is fixed
        # height.
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
        self._exec2_map_folder = None
        # Electroglas has no hardware-extracted map of its own (unlike
        # Accretech's own "Accretech" source) - Wafer Builder IS the wafer
        # there, published straight to the Run tab by _sync_views whenever
        # it changes (see recipe_gen_panel.py). The old "Electroglas"
        # source (ata_wafer_map_electroglas.csv) predates Wafer Builder
        # entirely and is retired.
        self._exec2_map_source_var = tk.StringVar(
            value="Accretech" if self._system == "accretech" else "Wafer Builder")
        self._exec2_map_path_var = tk.StringVar(value="No wafer map loaded")
        ttk.Label(map_bar, textvariable=self._exec2_map_path_var,
                  foreground="#6b7280", font=("Segoe UI", 8)).pack(
                  side="left", padx=8)

        self._exec2_sites_var = tk.StringVar(value="Test sites: 0 picked")
        ttk.Label(map_bar, textvariable=self._exec2_sites_var,
                  foreground="#6b7280", font=("Segoe UI", 8)).pack(
                  side="left", padx=8)

        ttk.Separator(map_bar, orient="vertical").pack(side="left", fill="y", padx=8)
        if self._system == "accretech":
            ttk.Button(map_bar, text="Overlay…",
                       command=self._exec2_open_overlay_dialog).pack(side="left")
        # Both systems: the selection is the loaded recipe's touchdown list, so
        # saving and reloading it belongs wherever dies are picked.
        ttk.Button(map_bar, text="💾 Save Selected Map",
                   command=self._exec2_save_selected_map).pack(side="left", padx=(6, 0))
        self._exec2_select_all_btn = ttk.Button(
            map_bar, text="☑ Select All", command=self._exec2_toggle_select_all)
        self._exec2_select_all_btn.pack(side="left", padx=(6, 0))

        self._exec2_wafer_map = WaferMapPanel(
            map_lf, show_title=False, show_axis_grid=(self._system == "accretech"))
        self._exec2_wafer_map.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self._exec2_wafer_map.enable_picking(on_change=self._exec2_on_sites_changed)
        self._exec2_wafer_map.on_redraw = self._exec2_redraw_overlay_on_run_map
        # Both halves are needed and they do different jobs: on_zoom REBUILDS
        # the labels (a zoom scales canvas items in place rather than
        # redrawing, so stale ones survive at the wrong size), while the
        # bindings decide whether they should be VISIBLE at this zoom level.
        # Keeping only the visibility half would leave wrongly-sized labels;
        # keeping only the rebuild would show them when too small to read.
        # Debounced (_exec2_debounced) rather than called directly - a fast
        # scroll or a middle-drag pan (which reuses this same on_zoom, see
        # wafer_map_view._bind_zoom_only) fires this many times a second,
        # and each call rebuilds every die-ID label - so a burst of events
        # now collapses into one rebuild shortly after the burst ends,
        # instead of rebuilding on every single one of them. What gets
        # redrawn, and when the data itself changes, is unchanged.
        self._exec2_wafer_map.on_zoom = self._exec2_debounced(
            "_exec2_zoom_debounce_id", self._exec2_redraw_overlay_on_run_map)
        # Bound with add="+" so the map's own pan/zoom/reset bindings (set up
        # inside WaferMapPanel.__init__) still run first.
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>", "<Double-Button-1>"):
            self._exec2_wafer_map.canvas.bind(
                seq, lambda _e: self._exec2_update_overlay_visibility(), add="+")

        stat_lf = ttk.LabelFrame(pos_row, text="Pass / Fail", padding=(8, 4))
        stat_lf.grid(row=0, column=1, sticky="nsew", padx=(3, 0))
        count_font = ("Consolas", 18, "bold")
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
            ttk.Label(row_f, textvariable=var, font=count_font,
                      foreground=color).pack(side="left", padx=8)

        ttk.Separator(stat_lf, orient="horizontal").pack(fill="x", pady=8)

        self._exec2_pct_var = tk.StringVar(value="Yield:  —")
        ttk.Label(stat_lf, textvariable=self._exec2_pct_var,
                  font=("Consolas", 13, "bold"), foreground="#374151").pack()

        ttk.Button(stat_lf, text="Reset Counts", command=self._exec2_reset_counts).pack(
            fill="x", pady=(8, 0))


    def _exec2_log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"{ts}  {msg}"
        try:
            self.controller.log(line)
        except (RuntimeError, tk.TclError):
            # Called from a run thread on every step, so a queued Tcl call
            # occasionally losing the "main thread is not in main loop"
            # race (same class of bug fixed in pma_wafer_panel.py's
            # workbook loader) must not take the run down with it - the
            # run continues; this one line just goes to stdout instead.
            print(line)

    def _exec2_minor_moves_active(self) -> bool:
        """Whether the CURRENTLY LOADED recipe wants shot-aware single-die
        stepping - see the Recipe tab's Minor Moves checkbox. Read fresh
        each time rather than cached, since it can change any time the
        operator picks a different recipe."""
        rp = getattr(self, "recipe_panel", None)
        return bool(rp and hasattr(rp, "is_minor_moves") and rp.is_minor_moves())

    def _exec2_draw_wafer_map(self, quiet_if_missing: bool = False):
        folder = self._exec2_map_folder
        # The Run tab map is always the real per-die Accretech/Wafer
        # Builder map, Minor Moves on or off - a shot is drawn as an
        # OUTLINE over that die map (see _exec2_update_shot_window), never
        # by swapping the map itself to one square per shot.
        filename = WAFER_MAP_SOURCES[self._exec2_map_source_var.get()]
        n = self._exec2_wafer_map.load_from_ata(folder, filename=filename)
        run_dbg = self._exec2_wafer_map.last_draw_debug or {}
        if run_dbg.get("warning"):
            self._exec2_log(f"[ERROR] Run wafer map: {run_dbg['warning']}")
        self._exec2_wafer_map.clear_picks()
        name = os.path.basename(folder)
        self._exec2_map_path_var.set(
            f"{name}  ({n} dies)" if n else f"{name} — {filename} not found")
        if n or not quiet_if_missing:
            self._exec2_log(f"[RUN] Wafer map loaded from '{name}/{filename}' — {n} dies")
        self._exec2_adopt_map_die_ids()
        # Both systems mirror the Run map onto the Results tab, so the
        # pass/fail map there is never a stale copy of a different wafer.
        self._sync_results_wafer_map()
        if self._system == "accretech":
            self._exec2_load_selected_map(quiet_if_missing=True)

    def _exec2_adopt_map_die_ids(self):
        """Use the die IDs the loaded map file carries as the overlay.

        The Electroglas map (ata_wafer_map_electroglas.csv) names every
        touchdown in a device_id column, so there is nothing to match up -
        unlike Accretech, where the Overlay dialog has to reconcile two
        different maps. Feeding them into the SAME _exec2_overlay_die_ids
        dict means the labels inherit everything that already works there:
        redrawn from WaferMapPanel.on_redraw after any rebuild, moved with
        the dies by canvas.scale on zoom, and written out by Save Selected
        Map, so an export can never disagree with what is on screen.
        """
        wm = self._exec2_wafer_map
        ids = {rc: text for rc, text in (wm.die_ids or {}).items() if text}
        if not ids:
            return
        # Never clobber an overlay the operator built by hand in the dialog.
        if self._exec2_overlay_die_ids and self._system == "accretech":
            return
        self._exec2_clear_overlay_labels(wm, self._exec2_overlay_items)
        self._exec2_overlay_die_ids = ids
        self._exec2_redraw_overlay_on_run_map()

    def _new_results_wafer_map(self):
        """(Re)create the Results tab's own WaferMapPanel from scratch, on
        a brand new Canvas.

        Reusing the SAME long-lived canvas for every redraw (the previous
        approach - a plain rwm._draw_from_die_list(dies) call) is what
        actually produced the broken layout every "die packed with no
        gaps, overlay labels off their square" report traced back to -
        the very first draw on a canvas was always the correct one, every
        later one on that same canvas was not, for a Tk-geometry reason
        that resisted every attempt to pin down and fix in place. A fresh
        widget makes every draw the "first, always-good" one instead of
        chasing what state a long-lived canvas accumulates - see the
        session's git history for the abandoned attempts.
        """
        old = getattr(self, "_results_wafer_map", None)
        wm = WaferMapPanel(self._results_map_frame)
        wm.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=(0, 8))
        wm.canvas.bind("<Button-1>", self._on_results_map_click, add="+")
        wm.on_redraw = self._exec2_redraw_overlay_on_results_map
        wm.on_zoom = self._exec2_debounced(
            "_exec2_results_zoom_debounce_id", self._exec2_redraw_overlay_on_results_map)
        self._results_wafer_map = wm
        if old is not None:
            try:
                old.destroy()
            except tk.TclError:
                pass
        return wm

    def _sync_results_wafer_map(self):
        rwm = getattr(self, "_results_wafer_map", None)
        if rwm is None:
            return
        dies = self._exec2_wafer_map._last_dies
        if dies:
            rwm = self._new_results_wafer_map()
            rwm._last_dies = dies
            rwm._draw_from_die_list(dies)  # triggers on_redraw -> overlay labels
            dbg = rwm.last_draw_debug or {}
            if dbg.get("warning"):
                self._exec2_log(f"[ERROR] Results wafer map: {dbg['warning']}")
        else:
            rwm.canvas.delete("all")
            rwm.dies.clear()
            rwm.canvas.create_text(150, 100, text="No wafer map loaded yet.", fill="gray")
            rwm._run_on_redraw()

    def _exec2_set_state(self, text: str, color: str):
        self._exec2_state_lbl.config(text=text, fg=color)

    def _exec2_open_all_channels(self):
        """Open every switch channel, whichever matrix this bench has.

        Called on a stop, so the bench is never left with a source still
        strapped to a pad after the operator has told it to stop.
        """
        switch = self.controller.drivers.get("switch")
        if switch is None or not getattr(switch, "inst", None):
            return
        try:
            if hasattr(switch, "open_all"):
                switch.open_all()
            elif hasattr(switch, "open_crosspoint"):
                switch.open_channel("allslots")
            else:
                switch.open_channel("allslots")
            self._exec2_log("[RUN] All switch channels opened.")
        except Exception as e:
            self._exec2_log(f"[RUN] ⚠ Could not open all channels: "
                            f"{type(e).__name__}: {e}")

    def _exec2_pause(self):
        """Stop after the work in progress, keeping the position.

        What ⏹ Stop Run used to do. Nothing is reset and the bench is left
        as it is, so ▶ Run picks up from the next touchdown.
        """
        eg_run = getattr(self, "eg_pma_run", None)
        if eg_run is not None and getattr(eg_run, "_running", False):
            try:
                eg_run._pause()
                self._exec2_log("[RUN] ⏸ Pause — stopping after this touchdown; "
                                "position kept, press ▶ Run to carry on.")
                return
            except Exception as e:
                self._exec2_log(f"[RUN] Could not pause the .PMA run: {e}")
        if not self._exec2_running:
            self._exec2_log("[RUN] Nothing is running to pause.")
            return
        # The Accretech-style loops check _exec2_running between dies, so
        # clearing it stops them the same graceful way - without the abort
        # flag, which is what triggers the emergency stop and the reset.
        self._exec2_running = False
        self._exec2_set_state("PAUSED", "#b45309")
        self._exec2_log("[RUN] ⏸ Paused after the current die — position kept.")

    def _exec2_abort(self):
        # One Stop Run button covers both run engines now - the normal Full
        # Die/Test Selected/Test Die loop below, AND (Electroglas only)
        # EgPmaRunPanel's own .PMA step-through, which used to need its own
        # separate ⏹ Stop button to halt.
        #
        # A real stop, not "wind down when convenient": the run thread bails
        # at the next step boundary rather than finishing the touchdown, the
        # switch is opened, the chuck is separated, and the position is
        # forgotten so ▶ Run starts the recipe over. ⏸ Pause is the gentle
        # one. What cannot be interrupted is a reading already in flight -
        # that is a single blocking GPIB call, and abandoning it mid-transfer
        # would leave the bus out of step for everything after it.
        eg_run = getattr(self, "eg_pma_run", None)
        eg_was_running = bool(getattr(eg_run, "_running", False))
        if eg_run is not None:
            try:
                eg_run._stop()
            except Exception as e:
                self._exec2_log(f"[RUN] Could not stop the .PMA step-through: {e}")
        self._exec2_running = False
        self._exec2_aborted = True
        # The .PMA run thread opens the channels and drops Z itself on the
        # way out (see EgPmaRunPanel._make_safe), so doing it here as well
        # would race it. Anything else, this is the only chance.
        if not eg_was_running:
            self._exec2_open_all_channels()
            prober_z = self.controller.drivers.get("prober")
            if prober_z is not None and getattr(prober_z, "inst", None):
                try:
                    prober_z.z_down()
                    self._exec2_log("[RUN] Chuck separated (Z down).")
                except Exception as e:
                    self._exec2_log(f"[RUN] ⚠ Could not separate the chuck: "
                                    f"{type(e).__name__}: {e}")
        self._exec2_run_token += 1
        self.after(0, lambda: self._exec2_full_btn.config(state="normal"))
        self.after(0, lambda: self._exec2_test_btn.config(state="normal"))
        self.after(0, lambda: self.recipe_panel.set_locked(False))
        self.after(0, lambda: self._exec2_wafer_map.enable_picking(
            on_change=self._exec2_on_sites_changed))
        self.after(0, lambda: self._exec2_set_state(
            "STOPPING…" if eg_was_running else "STOPPED", "#dc2626"))
        self._exec2_log("[RUN] ⏹ Stop — channels opened, chuck separated, "
                        "run position reset; ▶ Run will start from the beginning.")
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

    def _exec2_safe_after(self, fn):
        """self.after(0, fn), swallowing the rare "main thread is not in
        main loop" RuntimeError a queued Tcl call can raise when called
        from a run thread (same class of bug fixed in
        pma_wafer_panel.py's workbook loader). Used in _exec2_finish_run
        because that is the one cleanup path EVERY run thread's finally
        block depends on to unlock the UI - losing that race there left a
        run stuck showing RUNNING forever instead of just losing a log
        line, which is what happens everywhere else _exec2_log is used."""
        try:
            self.after(0, fn)
        except (RuntimeError, tk.TclError):
            pass

    def _exec2_finish_run(self, token: int, msg: str, color: str):
        if token != self._exec2_run_token:
            # Superseded by a newer run (or an abort) while this thread was
            # blocked on a hardware call — it's no longer "the" run, so don't
            # stomp on whatever state that newer run/abort has already set.
            return
        finished_mode = self._exec2_run_mode
        self._exec2_running  = False
        self._exec2_run_mode = None
        self._exec2_safe_after(lambda: self._exec2_full_btn.config(state="normal"))
        self._exec2_safe_after(lambda: self._exec2_test_btn.config(state="normal"))
        self._exec2_safe_after(lambda: self.recipe_panel.set_locked(False))
        self._exec2_safe_after(lambda: self._exec2_step_var.set("Step: —"))
        self._exec2_safe_after(lambda: self._exec2_wafer_map.enable_picking(
            on_change=self._exec2_on_sites_changed))
        if not self._exec2_aborted:
            self._exec2_safe_after(lambda: self._exec2_set_state(msg, color))
        if self._exec2_on_run_finished:
            # pass_var/fail_var are Tk vars - read them inside the deferred
            # call (main thread) rather than here (this thread), same
            # reasoning as _exec2_safe_after itself.
            total = self._exec2_total_dies
            aborted = self._exec2_aborted
            hook = self._exec2_on_run_finished
            def _call_hook():
                hook(self._exec2_pass_var.get(), self._exec2_fail_var.get(),
                    total, aborted, finished_mode)
            self._exec2_safe_after(_call_hook)

    def _exec2_ensure_separated(self, prober, stb: int, sim: bool):
        if sim or stb != 67:
            return
        self._exec2_log("[RUN] ⚠ finished chuck UP (STB=67 — contact) >> D  (Separate)")
        prober.z_down()

    def _exec2_zup_measure_zdown(self, sim: bool, prober, die_label: str,
                                 steps: list = None) -> bool:
        self._exec2_safe_after(lambda: self._exec2_step_var.set("Step: Contact"))
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

        self._exec2_safe_after(lambda: self._exec2_step_var.set("Step: Testing"))
        ok = self._exec2_run_steps_once(steps)
        self._exec2_safe_after(lambda p=ok, dl=die_label: self._exec2_log(
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
        status = "PASS" if ok else "FAIL"
        # The only persistent record of this verdict - the map widgets only
        # hold it as canvas item colour. cmd_save_csv reads this to write
        # per-die PASS/FAIL, and cmd_import_results_csv repaints from it.
        try:
            self.controller.die_status[(row, col)] = status
        except Exception:
            pass
        try:
            if (row, col) in self._exec2_wafer_map.dies:
                self._exec2_wafer_map.update_die(row, col, status)
        except Exception:
            pass
        rwm = getattr(self, "_results_wafer_map", None)
        if rwm is not None:
            try:
                if (row, col) in rwm.dies:
                    rwm.update_die(row, col, status)
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
        if self._exec2_lot_thread and self._exec2_lot_thread.is_alive():
            self._exec2_log("[RUN] Cannot start — the previous run is still finishing "
                            "its last hardware command (probably waiting on the prober). "
                            "Wait a moment and try again.")
            ok = False
        if not self._exec2_steps:
            self._exec2_log("[RUN] Cannot start — no recipe loaded "
                            "(pick one from the Recipe dropdown first).")
            ok = False
        if self._system == "accretech":
            if (self._exec2_map_source_var.get() not in ("Accretech", "Wafer Builder")
                    or not self._exec2_wafer_map._last_dies):
                self._exec2_log("[RUN] Cannot start — no wafer map loaded (load an "
                                "ATA folder with source set to 'Accretech' or 'Wafer "
                                "Builder'; extract one on the Wafer Builder tab's Accr "
                                "Wafer sub-tab, or build one there, if you haven't).")
                ok = False
        elif not self._exec2_wafer_map._last_dies:
            self._exec2_log("[RUN] Cannot start — no wafer map loaded "
                            "(load an ATA folder with source set to 'Electroglas').")
            ok = False
        required_instruments = (("prober", "smu", "dmm", "switch", "wave_gen")
                                if self._system == "accretech"
                                else ("prober", "smu", "relay1"))
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
        # Full Die/Test Selected are the plain "walk the dies, measure"
        # entry points - Minor Moves (multi-die shots, touchdown list, the
        # whole story) is ▶ Run's job now, not theirs. Refuse rather than
        # silently doing a native G/J walk that doesn't mean anything on a
        # wafer where a map square is a multi-die shot.
        if self._system == "accretech" and self._exec2_minor_moves_active():
            self._exec2_log("[RUN] Full Die: this recipe has Minor Moves on — "
                            "use ▶ Run instead (Full Die/Test Selected only "
                            "handle the plain, one-square-one-die case).")
            return
        self._exec2_start_full_die_walk("Full Die")

    def _exec2_start_full_die_walk(self, mode_label: str):
        """The actual native G/J whole-wafer walk - shared by Full Die and
        ▶ Run's own "no saved touchdowns, do the whole wafer" fallback."""
        self._exec2_reset_counts(total_dies=len(self._exec2_wafer_map._last_dies or []))
        self._exec2_running  = True
        self._exec2_aborted  = False
        self._exec2_run_mode = "full"
        self._exec2_run_token += 1
        my_token = self._exec2_run_token
        self._exec2_full_btn.config(state="disabled")
        self._exec2_test_btn.config(state="disabled")
        self.recipe_panel.set_locked(True)
        self._exec2_wafer_map.enable_picking(0)
        self.after(0, lambda: self._exec2_set_state(f"RUNNING ({mode_label})", "#2563eb"))
        self._exec2_log(f"[RUN] ▶ {mode_label} — walking the entire wafer (G/J), "
                        "measuring the loaded recipe at every die.")
        self._exec2_lot_thread = threading.Thread(
            target=self._exec2_full_die_thread, args=(my_token,), daemon=True)
        self._exec2_lot_thread.start()

    def _exec2_full_die_thread(self, my_token: int):
        prober = self.controller.drivers.get("prober")
        sim = not (prober and prober.inst)
        error_msg = None
        try:
            self._exec2_refresh_xy_blocking(prober, sim)
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
                # move_to_start_die() raises if the prober answers with a GPIB
                # error (STB=76) instead of 67/70 — e.g. it wasn't sitting on
                # the probing menu when G was sent. Caught below so the GUI
                # reflects the real outcome instead of claiming a clean finish.
                stb = prober.move_to_start_die()
            self._exec2_log(f"[RUN] << STB={stb}")
            self._exec2_ensure_separated(prober, stb, sim)

            sim_dies_remaining = 12
            while (self._exec2_running and not self._exec2_aborted
                   and self._exec2_run_token == my_token):
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

                if (not self._exec2_running or self._exec2_aborted
                        or self._exec2_run_token != my_token):
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
            error_msg = str(e)
            self._exec2_log(f"[RUN] ERROR: {e}")
        finally:
            if error_msg:
                self._exec2_finish_run(my_token, f"ERROR: {error_msg[:60]}", "#dc2626")
            else:
                self._exec2_finish_run(my_token, "FINISHED (Full Die)", "#16a34a")

    def _exec2_start_minor_moves(self, shots: list, mode_label: str):
        """Shared Full Die / Test Die startup for Minor Moves - `shots` are
        real absolute (row, col) die coordinates picked on the map, each
        naming a die that belongs to one shot (see goto_shot_die below for
        how the shot itself, and die #1's own cell within it, are found);
        from there only the die(s) the loaded recipe's steps reference by
        die # are visited.
        Same button/lock/state bookkeeping _exec2_start_full_die and
        _exec2_start_test_die already do for the native G/J path.

        Everything Tk-touching (recipe_gen's shot dims/cells, which read
        Tk StringVars) is resolved HERE, on the main thread, and handed to
        the worker as plain data - a background thread calling .get() on a
        Tk variable can raise "main thread is not in main loop" (the same
        class of bug fixed in pma_wafer_panel.py's workbook loader; see
        that file's load_workbook_path for the longer explanation).

        Origin: each (row, col) in `shots` is a real absolute die
        coordinate picked on the map (the map only ever shows real dies -
        see _exec2_draw_wafer_map) - but it may be ANY die belonging to
        the target shot (whichever square the picker/shot-window
        highlighted), not necessarily die #1's own cell. Same as Next
        Shot/Previous Shot (_exec2_go_to_shot/_exec2_current_shot_index):
        the Overlay dialog's confirmed row/col offset is what tells us
        WHICH shot a real coordinate falls in (floor-divide by the shot
        dimensions), then shot_die_rc() gives any die #'s cell within
        that shot to land on."""
        if not self._exec2_overlay_offset_confirmed:
            self._exec2_log("[RUN] Minor Moves: no confirmed Overlay alignment — "
                            "press Overlay… (next to the map path, above) and "
                            "🖌 Overlay on Map first, then start again.")
            return
        overlay_offset = (self._exec2_overlay_row_offset, self._exec2_overlay_col_offset)
        gen = getattr(self, "recipe_gen", None)
        if gen is None:
            self._exec2_log("[RUN] Minor Moves: the Wafer Builder tab is not available.")
            return
        shot_rows, shot_cols = gen._shot_dims()
        shot_cells = dict(gen._shot_cells)

        # A saved touchdown list carries one SITE row per DIE the recipe
        # references (e.g. Cenfire's "first"/"second" pair), not one per
        # SHOT - two dies of the same physical shot resolve to the same
        # (shot_row, shot_col) below, and visiting a shot once per row
        # measured it twice, then a third time, etc. Collapse to one
        # representative pick per shot, first-seen order, before the
        # run thread ever starts.
        row_off, col_off = self._exec2_overlay_row_offset, self._exec2_overlay_col_offset
        seen_shots = {}
        deduped = []
        for row, col in shots:
            key = ((row - row_off) // shot_rows, (col - col_off) // shot_cols)
            if key in seen_shots:
                continue
            seen_shots[key] = (row, col)
            deduped.append((row, col))
        if len(deduped) != len(shots):
            self._exec2_log(f"[RUN] Minor Moves: {len(shots)} touchdown(s) resolved to "
                            f"{len(deduped)} distinct shot(s) — collapsed duplicates "
                            "(a saved touchdown list carries one row per die, not per shot).")
        shots = deduped

        self._exec2_reset_counts(total_dies=len(shots))
        self._exec2_running  = True
        self._exec2_aborted  = False
        self._exec2_run_mode = "full" if mode_label == "Full Die" else "test"
        self._exec2_run_token += 1
        my_token = self._exec2_run_token
        self._exec2_full_btn.config(state="disabled")
        self._exec2_test_btn.config(state="disabled")
        self.recipe_panel.set_locked(True)
        self._exec2_wafer_map.enable_picking(0)
        self.after(0, lambda: self._exec2_set_state(
            f"RUNNING (Minor Moves — {mode_label})", "#2563eb"))
        self._exec2_log(f"[RUN] ▶ {mode_label} (Minor Moves) — {len(shots)} shot(s), "
                        "visiting only the die(s) the recipe references.")
        self._exec2_lot_thread = threading.Thread(
            target=self._exec2_minor_move_thread,
            args=(shots, my_token, overlay_offset, shot_rows, shot_cols, shot_cells),
            daemon=True)
        self._exec2_lot_thread.start()

    def _exec2_minor_move_thread(self, shots: list, my_token: int, overlay_offset: tuple,
                                 shot_rows: int, shot_cols: int, shot_cells: dict):
        """One touchdown per shot, exactly like the native G/J path - the
        difference is what happens AT that touchdown. A shot lands on die
        #1 automatically (same as any single-die touchdown lands on *a*
        die before anything runs), then the loaded recipe's steps run flat,
        top to bottom, once: a "move" step (see recipe_panel._STEP_TYPES)
        is what repositions to any OTHER die # within that same shot -
        nothing moves the chuck between dies on its own any more. Nothing
        moves it between SHOTS either, beyond that automatic die-#1
        landing on the next square.
        """
        prober = self.controller.drivers.get("prober")
        sim = not (prober and prober.inst)
        error_msg = None
        row_offset, col_offset = overlay_offset

        class _Stop(Exception):
            pass

        def shot_rc_for(pick_row, pick_col):
            """Which (shot_row, shot_col) a real absolute die coordinate
            falls in - same floor-division Next Shot/Previous Shot use
            (_exec2_go_to_shot/_exec2_current_shot_index)."""
            wb_row = pick_row - row_offset
            wb_col = pick_col - col_offset
            return wb_row // shot_rows, wb_col // shot_cols

        def publish_die_slots(shot_row, shot_col):
            """Tell _exec2_run_steps_once/_exec2_slot_identity where each
            die # in THIS shot really sits, and what its real die ID is -
            same publish-before-run pattern
            eg_pma_run_panel._advance_touchdown already uses for
            Electroglas quads, so every measurement is filed against the
            die it actually measured (matched by real XY position + the
            step's own Die # field) instead of the shot's landing square
            for all of them. Cleared after the shot in the caller."""
            present = present_slots(shot_cells, shot_rows, shot_cols)
            max_die = max(present.values()) if present else 1
            rcs, ids, shotpos = [], [], []
            wm = self._exec2_wafer_map
            for die_num in range(1, max_die + 1):
                rc = shot_die_rc(shot_cells, shot_rows, shot_cols, die_num)
                if rc is None:
                    rcs.append(None)
                    ids.append("")
                    shotpos.append(None)
                    continue
                r, c = rc
                real_row = shot_row * shot_rows + r + row_offset
                real_col = shot_col * shot_cols + c + col_offset
                rcs.append((real_row, real_col))
                ids.append(self._exec2_overlay_die_ids.get((real_row, real_col))
                          or wm.die_ids.get((real_row, real_col), ""))
                # (reticle row, reticle col, row WITHIN the shot, col WITHIN
                # the shot) - generic reticle/shot-position bookkeeping any
                # export format can read (see export_formats.py's
                # shot_row/shot_col/intra_row/intra_col source fields),
                # not tied to any one project's naming.
                shotpos.append((shot_row, shot_col, r, c))
            self._exec2_die_rc_by_slot = rcs
            self._exec2_die_ids_by_slot = ids
            self._exec2_die_shotpos_by_slot = shotpos

        def goto_shot_die(pick_row, pick_col, die_num):
            """Separate, jump to (shot, die #), contact. Used both for the
            automatic die-#1 landing and for every in-recipe "move" step -
            the chuck must never travel in X/Y while contacted.

            (pick_row, pick_col) is a real absolute die coordinate that
            belongs to the target shot - not necessarily die #1's own
            cell (it may be whatever square the picker/shot-window
            highlighted). shot_rc_for() finds WHICH shot that is, then
            shot_die_rc() gives any die #'s cell to land on within it."""
            shot_row, shot_col = shot_rc_for(pick_row, pick_col)
            rc = shot_die_rc(shot_cells, shot_rows, shot_cols, die_num)
            if rc is None:
                raise RuntimeError(f"die #{die_num} is not on shot "
                                   f"R{shot_row}C{shot_col}")
            r, c = rc
            die_x = shot_col * shot_cols + c + col_offset
            die_y = shot_row * shot_rows + r + row_offset
            die_label = (f"shot R{shot_row}C{shot_col} die #{die_num} "
                        f"(X{die_x:.0f} Y{die_y:.0f})")
            self._exec2_safe_after(lambda d=die_label: self._exec2_die_var.set(f"Die: {d}"))
            self._exec2_safe_after(
                lambda x=die_x, y=die_y:
                self._exec2_xy_var.set(f"X: {x:.0f} die\nY: {y:.0f} die"))
            self._exec2_die_num += 1

            self._exec2_log(f"[RUN] >> D  (Separate before move)")
            if sim:
                time.sleep(0.05)
            else:
                prober.z_down()

            self._exec2_log(f"[RUN] >> J  (Position die X={die_x:.0f} Y={die_y:.0f}, "
                            f"die #{die_num})")
            if sim:
                stb = 66
                time.sleep(0.1)
            else:
                stb = prober.move_to_die_xy(die_x, die_y)
            self._exec2_log(f"[RUN] << STB={stb}")
            if stb == 81:
                self._exec2_log("[RUN] << (wafer end)")
                self._exec2_running = False
                raise _Stop()
            if stb == 90:
                self._exec2_log("[RUN] << (probing stop — <STOP> pushed)")
                self._exec2_running = False
                raise _Stop()
            self._exec2_ensure_separated(prober, stb, sim)

            self._exec2_log("[RUN] >> Z  (Contact)")
            if not sim:
                stb = prober.z_up()
                if stb != 67:
                    self._exec2_log(f"[RUN] ⚠ Z Up returned STB={stb} (expected 67)")

        try:
            self._exec2_refresh_xy_blocking(prober, sim)
            for land_row, land_col in shots:
                if (not self._exec2_running or self._exec2_aborted
                        or self._exec2_run_token != my_token):
                    break
                self._exec2_safe_after(
                    lambda r=land_row, c=land_col: self._exec2_highlight_current(r, c))
                self._exec2_log(f"[RUN] Shot at picked R{land_row}C{land_col}: landing on die #1")
                try:
                    goto_shot_die(land_row, land_col, 1)
                except _Stop:
                    break

                shot_row, shot_col = shot_rc_for(land_row, land_col)
                publish_die_slots(shot_row, shot_col)
                self._exec2_move_fn = (
                    lambda die_num, lr=land_row, lc=land_col: goto_shot_die(lr, lc, die_num))
                try:
                    shot_ok = self._exec2_run_steps_once()
                finally:
                    self._exec2_move_fn = None
                    self._exec2_die_rc_by_slot = []
                    self._exec2_die_ids_by_slot = []
                    self._exec2_die_shotpos_by_slot = []

                self._exec2_log("[RUN] >> D  (Separate)")
                if not sim:
                    prober.z_down()

                # Each die in the shot passes or fails on its OWN square,
                # not the shot's landing square for all of them - a shot's
                # dies are independent devices. Falls back to the single
                # combined verdict on the landing square only when the
                # recipe never tagged a passfail step with a Die #.
                slot_verdicts = dict(getattr(self, "_exec2_slot_verdicts", None) or {})
                if slot_verdicts:
                    for die_num, passed in sorted(slot_verdicts.items()):
                        rc = shot_die_rc(shot_cells, shot_rows, shot_cols, die_num)
                        if rc is None:
                            continue
                        r, c = rc
                        real_row = shot_row * shot_rows + r + row_offset
                        real_col = shot_col * shot_cols + c + col_offset
                        self._exec2_safe_after(
                            self._exec2_add_pass if passed else self._exec2_add_fail)
                        self._exec2_update_die_color(real_row, real_col, passed)
                else:
                    self._exec2_safe_after(
                        self._exec2_add_pass if shot_ok else self._exec2_add_fail)
                    self._exec2_update_die_color(land_row, land_col, shot_ok)
        except Exception as e:
            error_msg = str(e)
            self._exec2_log(f"[RUN] ERROR: {e}")
        finally:
            self._exec2_move_fn = None
            if error_msg:
                self._exec2_finish_run(my_token, f"ERROR: {error_msg[:60]}", "#dc2626")
            else:
                self._exec2_finish_run(my_token, "FINISHED (Minor Moves)", "#16a34a")

    def _exec2_on_sites_changed(self, picks):
        self._exec2_sites_var.set(self._exec2_sites_label(picks))
        btn = getattr(self, "_exec2_select_all_btn", None)
        dies = self._exec2_wafer_map._last_dies
        if btn and dies:
            all_rc = {(d["row"], d["col"]) for d in dies}
            is_all = bool(all_rc) and set(picks) == all_rc
            btn.config(text="☐ Deselect All" if is_all else "☑ Select All")

    def _exec2_sites_label(self, picks) -> str:
        """Header over the map. One pick names what sits on that square.

        On Accretech a square is one prober die, which for a quad product is a
        whole touchdown carrying up to four devices, so naming them answers
        "what comes down with this". Same ID sources and priority the exports
        use, so the header can never disagree with the recorded die_id.
        Multi-pick falls back to the count: this is only legible for one.
        """
        n = len(picks)
        if n != 1:
            return f"Test sites: {n} picked"
        rc = tuple(picks[0])
        ids = ((self._exec2_overlay_die_ids or {}).get(rc, "")
               or self._exec2_wafer_map.die_ids.get(rc, ""))
        where = f"Test site: 1 picked — R{rc[0]}C{rc[1]}"
        if not ids:
            return f"{where} (no die ID on this square)"
        devices = [d for d in ids.split("/") if d.strip()]
        if len(devices) < 2:
            return f"{where}:  {ids}"
        return f"{where}, touchdown of {len(devices)} devices:  {ids}"

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

    def _exec2_toggle_select_all(self):
        dies = self._exec2_wafer_map._last_dies
        if not dies:
            self._exec2_log("[RUN] No wafer map loaded — load one before selecting dies.")
            return
        all_rc = [(d["row"], d["col"]) for d in dies]
        already_all = set(self._exec2_wafer_map.get_picked()) == set(all_rc)
        if already_all:
            self._exec2_wafer_map.set_picked([])
            self._exec2_on_sites_changed([])
            self._exec2_log("[RUN] Deselected all dies.")
        else:
            self._exec2_wafer_map.set_picked(all_rc)
            self._exec2_on_sites_changed(all_rc)
            self._exec2_log(f"[RUN] Selected all {len(all_rc)} die(s) — "
                            "click any die to deselect it, or press again to deselect all.")

    _SELECTED_MAP_FILENAME = "ata_wafer_map_selected.csv"

    def _exec2_selected_map_path(self):
        return (os.path.join(self._ata_folder, self._SELECTED_MAP_FILENAME)
                if self._ata_folder else None)

    def _exec2_picks_as_touchdowns(self, picks) -> list:
        """Collapse picked map cells to one cell per PROBER TOUCHDOWN.

        On Accretech a square already is a touchdown, so this is a no-op. On
        Electroglas a square is a die and a 2x2 shot owns four of them - the
        chuck lands once and the recipe switches the mux through the dies
        under it, so clicking all four dies of a shot must still produce ONE
        touchdown, not four visits to the same place.
        """
        picks = [(int(r), int(c)) for r, c in picks]
        run = getattr(self, "eg_pma_run", None)
        seq_at_rc = getattr(run, "_seq_at_rc", None) or {}
        anchor_rc = getattr(run, "_anchor_rc", None) or {}
        if self._system != "electroglas" or not seq_at_rc:
            return picks
        out, seen = [], set()
        for rc in picks:
            seq = seq_at_rc.get(rc)
            if seq is None:
                # Not part of any touchdown this recipe knows - keep it as
                # itself rather than dropping the operator's selection.
                if rc not in seen:
                    seen.add(rc)
                    out.append(rc)
                continue
            if seq in seen:
                continue
            seen.add(seq)
            out.append(anchor_rc.get(seq, rc))
        return out

    def _exec2_touchdown_cells(self, picks) -> list:
        """The inverse: every cell belonging to the touchdowns in `picks`.

        Used for DISPLAY, so selecting a recipe lights up whole shots rather
        than one corner die of each.
        """
        picks = [(int(r), int(c)) for r, c in picks]
        run = getattr(self, "eg_pma_run", None)
        seq_at_rc = getattr(run, "_seq_at_rc", None) or {}
        cells = getattr(run, "_cells", None) or {}
        if self._system != "electroglas" or not seq_at_rc:
            return picks
        out, seen = [], set()
        for rc in picks:
            seq = seq_at_rc.get(rc)
            for cell in (cells.get(seq) or [rc]):
                if cell not in seen:
                    seen.add(cell)
                    out.append(cell)
        return out

    def _exec2_loaded_recipe_name(self) -> str:
        """The recipe the Run tab currently has loaded, if any."""
        if not getattr(self, "_exec2_steps", None):
            return ""
        try:
            return self.recipe_panel.get_active_recipe() or ""
        except Exception:
            return ""

    def _exec2_save_selected_map(self):
        """Save the picked dies as the loaded recipe's touchdown list.

        The selection is a property of the recipe, not of the ATA folder: one
        folder holds many recipes and they probe different dies. This and the
        Recipe tab's "Take from map selection" are the same operation from two
        places - whichever the operator reaches for, the list ends up in the
        same place and the other view shows it.

        With no recipe loaded there is nothing to attach it to, so it still
        falls back to the folder-level CSV rather than silently discarding the
        selection.
        """
        from tkinter import messagebox
        import csv
        picks = self._exec2_wafer_map.get_picked()
        if not picks:
            messagebox.showinfo("No Dies Selected",
                                "Click dies on the map to select them first.")
            return

        recipe = self._exec2_loaded_recipe_name()
        set_sites = getattr(self.recipe_panel, "set_sites", None)
        if recipe and set_sites:
            sites = []
            for rc in self._exec2_picks_as_touchdowns(picks):
                sites.append({
                    "die_id": (self._exec2_overlay_die_ids.get(rc)
                               or self._exec2_wafer_map.die_ids.get(rc, "")),
                    "row": rc[0], "col": rc[1]})
            if set_sites(recipe, sites):
                named = sum(1 for s in sites if s["die_id"])
                self._exec2_log(
                    f"[RUN] Saved {len(sites)} selected die(s) as the touchdown "
                    f"list of recipe '{recipe}' ({named} with a die ID) — "
                    "saved to the probe card, and shown on the Recipe tab.")
                return
            self._exec2_log(f"[RUN] Could not attach the selection to recipe "
                            f"'{recipe}' — falling back to the folder file.")

        if not self._ata_folder:
            messagebox.showerror(
                "Nowhere to save",
                "No recipe is loaded and no ATA folder is open.\n\n"
                "Pick a recipe from the Recipe dropdown to save the selection "
                "as its touchdown list, or open an ATA folder to save a "
                "folder-level selected map.")
            return
        self._exec2_log("[RUN] No recipe loaded — saving a folder-level selected "
                        "map instead. Load a recipe first to attach the "
                        "selection to it.")
        path = self._exec2_selected_map_path()
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["row", "col", "label"])
            for r, c in picks:
                wr.writerow([r, c, self._exec2_overlay_die_ids.get((r, c), "")])
        n_labeled = sum(1 for rc in picks if rc in self._exec2_overlay_die_ids)
        note = f" ({n_labeled} with overlay die ID)" if n_labeled else ""
        self._exec2_log(f"[RUN] Saved {len(picks)} selected die(s){note} → {path}")

    def _exec2_load_selected_map(self, quiet_if_missing: bool = False):
        # Only ever a recipe's own touchdown list - the standalone
        # "Load Selected Map" button is gone (picking a recipe from the
        # dropdown already does this, via _exec2_apply_recipe_sites/here),
        # and the old
        # folder-level CSV fallback used to load a stale selection even with
        # no recipe loaded at all. With no recipe loaded there is nothing to
        # select, so this is now a no-op rather than resurrecting whatever
        # was last saved to that file.
        recipe = self._exec2_loaded_recipe_name()
        if not recipe:
            return []
        get_records = getattr(self.recipe_panel, "get_site_records", None)
        sites = list(get_records()) if get_records else []
        if not sites:
            if not quiet_if_missing:
                self._exec2_log(
                    f"[RUN] Recipe '{recipe}' has no touchdown list yet — click "
                    "dies on the map, then 💾 Save Selected Map.")
            return []
        picks = [(s["row"], s["col"]) for s in sites]
        ids = {(s["row"], s["col"]): s["die_id"]
               for s in sites if s.get("die_id")}
        picks = [rc for rc in self._exec2_touchdown_cells(picks)
                 if rc in self._exec2_wafer_map.dies] or picks
        self._exec2_wafer_map.set_picked(picks)
        self._exec2_on_sites_changed(picks)
        if ids:
            self._exec2_clear_overlay()
            self._exec2_overlay_die_ids = ids
            self._exec2_redraw_overlay_on_run_map()
            self._exec2_redraw_overlay_on_results_map()
        self._exec2_log(f"[RUN] Loaded {len(picks)} touchdown(s) from "
                        f"recipe '{recipe}'.")
        return picks

    def _exec2_start_test_selected(self):
        if self._exec2_running:
            self._exec2_log("[RUN] A run is already active — stop it first.")
            return
        sites = self._exec2_wafer_map.get_picked()
        if not sites:
            sites = self._exec2_load_selected_map(quiet_if_missing=True)
        if not sites:
            self._exec2_log(
                "[RUN] Test Selected: no dies selected — click dies on the map, "
                "or pick a recipe from the Recipe dropdown to pull in its "
                "saved touchdown list.")
            return
        self._exec2_log(f"[RUN] ▶ Test Selected — {len(sites)} selected die(s): "
                        + ", ".join(f"R{r}C{c}" for r, c in sites))
        self._exec2_start_test_die()

    def _exec2_start_run(self):
        """The real, full-story entry point: the recipe's own saved
        touchdown list (Recipe tab's Touchdowns table - the same list ▶
        Save Selected Map/Take from map selection/Take die IDs build),
        Minor Moves if the recipe has it on, all of it - unlike Full Die/
        Test Selected, which are deliberately the plain single-die case
        only. No saved touchdowns and Minor Moves off falls back to the
        same native whole-wafer G/J walk Full Die does; no saved
        touchdowns and Minor Moves on falls back to landing on EVERY real
        die on the map and treating each as its own shot's die #1 - not
        actually one touchdown per real shot (the map carries no shot-
        boundary info of its own to enumerate those from). Save a proper
        touchdown list (one entry per shot) rather than relying on this
        fallback for a real run.
        """
        if self._exec2_running:
            self._exec2_log("[RUN] A run is already active — stop it first.")
            return
        if not self._exec2_can_start():
            return
        sites = self.recipe_panel.get_sites()
        if self._system == "accretech" and self._exec2_minor_moves_active():
            if not sites:
                sites = list(self._exec2_wafer_map.dies.keys())
            if not sites:
                self._exec2_log("[RUN] Run: Minor Moves is on but there is no "
                                "wafer map loaded — check the Run tab's map source.")
                return
            self._exec2_start_minor_moves(sites, "Run")
            return
        if sites:
            self._exec2_start_site_list(sites, "Run", "run")
            return
        if not (self._exec2_wafer_map._last_dies or []):
            self._exec2_log("[RUN] Run: no saved touchdowns on this recipe and "
                            "no wafer map loaded.")
            return
        self._exec2_log("[RUN] ▶ Run — no saved touchdowns on this recipe, "
                        "walking the whole wafer map instead.")
        self._exec2_start_full_die_walk("Run")

    def _exec2_wafer_builder_grid(self) -> list:
        """[{"row","col","die_ids","raw_text"}] from the Wafer Builder's Die
        Map, in die-pitch units - the same shape pma_shots_to_grid produces,
        so centroid_offset/merge_with_accretech work unchanged.

        This is the ONLY overlay source now. Accretech's Wafer Builder no
        longer keeps a PMA/Recipe Generator/CSV source loaded in memory the
        way the old three-map page did - it IS the wafer definition, so
        overlaying is always "the Wafer Builder map onto the Accretech map"
        rather than a choice of legacy sources.
        """
        gen = getattr(self, "recipe_gen", None)
        if gen is None:
            return []
        try:
            dpx, dpy = gen._die_pitch()
        except Exception:
            return []
        if not dpx or not dpy:
            return []
        out = []
        for d in gen._die_positions():
            if d["status"] != "normal" or not d["die_id"]:
                continue
            out.append({"row": round(d["y"] / dpy), "col": round(d["x"] / dpx),
                       "die_ids": [d["die_id"]], "raw_text": d["die_id"]})
        return out

    def _exec2_overlay_accretech_rc(self):
        return set(self._exec2_wafer_map.dies.keys())

    def _exec2_wafer_builder_footprint(self) -> set:
        """Every (row, col) Wafer Builder considers part of the wafer -
        present in a real shot, whether or not that die has been named yet
        - same row/col units as _exec2_wafer_builder_grid() (which only
        keeps the NAMED subset, for labeling). This is what bounds
        Overlay's SELECTION to Wafer Builder's actual footprint - a wafer
        with fewer real shots than the Accretech extraction has die
        positions should select fewer squares, not the whole Accretech map.
        Empty if Wafer Builder has no map/shots defined at all, which
        _exec2_overlay_all_accretech treats as "nothing to bound by" and
        falls back to selecting everything (unchanged from before)."""
        gen = getattr(self, "recipe_gen", None)
        if gen is None:
            return set()
        try:
            dpx, dpy = gen._die_pitch()
        except Exception:
            return set()
        if not dpx or not dpy:
            return set()
        out = set()
        for d in gen._die_positions():
            if d["status"] != "normal":
                continue
            out.add((round(d["y"] / dpy), round(d["x"] / dpx)))
        return out

    @staticmethod
    def _exec2_overlay_all_accretech(grid: list, accretech_rc, row_offset: int,
                                     col_offset: int, footprint: "set | None" = None) -> list:
        """One overlay entry per square the Accretech map actually has AND
        that falls within Wafer Builder's own footprint (see
        _exec2_wafer_builder_footprint) once the offset is applied - unlike
        merge_with_accretech (which drops any square the Wafer Builder grid
        has no real ID for), this covers every REAL shot Wafer Builder
        defines, labeling whichever of them also got a real ID. `footprint`
        empty/None (no Wafer Builder map loaded at all) falls back to
        selecting the whole Accretech map, same as before - there is
        nothing to bound by."""
        by_rc: dict = {}
        for p in grid:
            rc = (p["row"] + row_offset, p["col"] + col_offset)
            by_rc.setdefault(rc, []).extend(p["die_ids"])
        if footprint:
            selected = sorted(rc for rc in accretech_rc
                              if (rc[0] - row_offset, rc[1] - col_offset) in footprint)
        else:
            selected = sorted(accretech_rc)
        return [{"row": r, "col": c, "die_ids": by_rc.get((r, c), []), "raw_text": ""}
               for r, c in selected]

    _EXEC2_OVERLAY_MIN_DIE_PX = 22  # below this on-screen die width, overlay text is unreadable clutter

    def _exec2_update_overlay_visibility(self):
        if not self._exec2_overlay_items:
            return
        wm = self._exec2_wafer_map
        sample_rc = next(iter(self._exec2_overlay_die_ids), None)
        item = wm.dies.get(sample_rc) if sample_rc else None
        bbox = wm.canvas.bbox(item) if item is not None else None
        if not bbox:
            return
        width_px = bbox[2] - bbox[0]
        state = "normal" if width_px >= self._EXEC2_OVERLAY_MIN_DIE_PX else "hidden"
        for it in self._exec2_overlay_items:
            try:
                wm.canvas.itemconfigure(it, state=state)
            except tk.TclError:
                pass

    def _exec2_debounced(self, pending_attr: str, fn, delay_ms: int = 60):
        """Wrap fn so a burst of calls (a fast mouse-wheel scroll, or a
        middle-drag pan - both fire many events a second) collapses into
        one call ~delay_ms after the last one in the burst, rather than
        running fn on every single event. Used for the overlay label
        rebuild, which is what made zoom/pan noticeably laggy on a wafer
        map with many die-ID labels showing - this changes how OFTEN that
        rebuild runs, not what it does or when the underlying data changes.

        pending_attr names a per-caller instance attribute that holds the
        pending after() id, so two different debounced callbacks (e.g. the
        Run tab map and the Results tab map) do not cancel each other.
        """
        def _schedule():
            existing = getattr(self, pending_attr, None)
            if existing is not None:
                try:
                    self.after_cancel(existing)
                except Exception:
                    pass

            def _fire():
                setattr(self, pending_attr, None)
                fn()
            setattr(self, pending_attr, self.after(delay_ms, _fire))
        return _schedule

    def _exec2_redraw_overlay_on_run_map(self):
        # Explicitly clear first: a full redraw has already wiped the canvas,
        # but a ZOOM has not - it scales items in place - so without this the
        # old labels would survive alongside the new ones.
        self._exec2_clear_overlay_labels(self._exec2_wafer_map,
                                         self._exec2_overlay_items)
        if self._exec2_overlay_die_ids:
            self._exec2_overlay_items = self._exec2_draw_overlay_labels_on(
                self._exec2_wafer_map, self._exec2_overlay_die_ids)
        else:
            self._exec2_overlay_items = []
        self._exec2_update_overlay_visibility()
        # The PMA runner's "you are here" box is drawn on this same canvas and
        # is wiped by the same rebuild, so it re-draws off the one hook rather
        # than competing for on_redraw.
        redraw_window = getattr(getattr(self, "eg_pma_run", None),
                                "update_shot_window", None)
        if redraw_window:
            try:
                redraw_window()
            except Exception:
                pass
        if self._system == "accretech":
            self._exec2_update_shot_window()

    def _exec2_redraw_overlay_on_results_map(self):
        rwm = getattr(self, "_results_wafer_map", None)
        if rwm is None:
            return
        self._exec2_clear_overlay_labels(rwm, self._exec2_overlay_result_items)
        if not self._exec2_overlay_die_ids:
            self._exec2_overlay_result_items = []
            return
        self._exec2_overlay_result_items = self._exec2_draw_overlay_labels_on(
            rwm, self._exec2_overlay_die_ids)

    def _exec2_clear_overlay_labels(self, wm, items: list):
        for item in items:
            try:
                wm.canvas.delete(item)
            except tk.TclError:
                pass
        items.clear()

    def _exec2_clear_overlay(self):
        self._exec2_clear_overlay_labels(self._exec2_wafer_map, self._exec2_overlay_items)
        rwm = getattr(self, "_results_wafer_map", None)
        if rwm is not None:
            self._exec2_clear_overlay_labels(rwm, self._exec2_overlay_result_items)
        self._exec2_overlay_die_ids = {}

    def _exec2_persist_overlay_offset(self):
        """Writes the Overlay's current alignment into the active Wafer
        Builder map's saved JSON immediately, the moment it's confirmed (or
        cleared) - NOT deferred until some later save.

        Confirming Overlay is its own action; the Run tab's own 💾 Save
        Selected Map button (_exec2_save_selected_map) saves the loaded
        RECIPE's touchdown list, not the map file, and pressing it is not
        guaranteed to happen right after Overlay at all. Without this, the
        alignment only ever lived in the self._exec2_overlay_* instance
        attributes and was gone the moment the app closed - see
        recipe_gen_panel._state_to_dict/_state_from_dict for the fields this
        writes, and _exec2_reapply_overlay for the restore side.
        """
        gen = getattr(self, "recipe_gen", None)
        folder = getattr(self, "_exec2_map_folder", None) or getattr(self, "_ata_folder", None)
        if gen is None or not folder:
            return
        name_var = getattr(gen, "map_name_var", None)
        if name_var is None or not name_var.get().strip():
            return
        try:
            gen._autosave_named_map_quiet(folder)
        except Exception as e:
            self._exec2_log(f"[RUN] Could not save Overlay alignment: "
                            f"{type(e).__name__}: {e}")

    def _exec2_reapply_overlay(self):
        """Redraws the Overlay's saved alignment against whatever Accretech
        map/Wafer Builder grid this ATA folder just loaded.

        The row/col offset and confirmed flag are restored earlier, by
        recipe_gen_panel._state_from_dict (loaded together with the Wafer
        Builder map itself, since that offset is meaningless without knowing
        which map it was confirmed against) - this just re-draws from them,
        called from load_ata_folder AFTER the Accretech map is actually on
        screen (_exec2_overlay_accretech_rc needs self._exec2_wafer_map.dies
        populated, which is not true yet at state-restore time during a
        folder switch). A no-op if nothing was ever confirmed, or if the
        Accretech map turned out empty (e.g. Overlay was confirmed against a
        wafer map source that is no longer loaded).
        """
        if not self._exec2_overlay_offset_confirmed:
            return
        accretech_rc = self._exec2_overlay_accretech_rc()
        if not accretech_rc:
            return
        grid = self._exec2_wafer_builder_grid()
        footprint = self._exec2_wafer_builder_footprint()
        matched = self._exec2_overlay_all_accretech(
            grid, accretech_rc, self._exec2_overlay_row_offset,
            self._exec2_overlay_col_offset, footprint)
        self._exec2_draw_overlay(matched)
        self._exec2_log(
            f"[RUN] Overlay restored from the saved map ({len(matched)} die(s), "
            f"row {self._exec2_overlay_row_offset:+d}, col {self._exec2_overlay_col_offset:+d}).")

    _OVERLAY_FONT = ("Consolas", 7)

    def _exec2_overlay_font(self):
        # Cached: tkfont.Font is not free to build, and this runs per zoom step.
        if getattr(self, "_overlay_font_obj", None) is None:
            self._overlay_font_obj = tkfont.Font(family=self._OVERLAY_FONT[0],
                                                 size=self._OVERLAY_FONT[1])
        return self._overlay_font_obj

    def _exec2_labels_fit(self, wm, die_ids_by_rc: dict) -> bool:
        """Is a die currently drawn big enough to hold its ID?

        Zoomed out, a whole-wafer map draws dies a few pixels across and the
        IDs collapse into an unreadable smear, so they are not drawn at all
        until there is room. Measured with the real font rather than guessed,
        against the LONGEST label, so a quad ID like 'TARGET' does not
        overflow its neighbour.
        """
        box_w, box_h = wm.die_box_px()
        if box_w <= 0:
            return False
        longest = max(die_ids_by_rc.values(), key=len, default="")
        font = self._exec2_overlay_font()
        return (box_w >= font.measure(longest) + 3
                and box_h >= font.metrics("linespace"))

    def _exec2_draw_overlay_labels_on(self, wm, die_ids_by_rc: dict) -> list:
        if not self._exec2_labels_fit(wm, die_ids_by_rc):
            return []
        items = []
        for rc, label_text in die_ids_by_rc.items():
            item = wm.dies.get(rc)
            if item is None:
                continue
            coords = wm.canvas.coords(item)
            if len(coords) < 4:
                continue
            cx, cy = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
            items.append(wm.canvas.create_text(
                cx, cy, text=label_text, font=self._OVERLAY_FONT, fill="#1e293b"))
        return items

    def _exec2_draw_overlay(self, matched: list):
        self._exec2_clear_overlay()
        # Labels only for cells with a real ID - every cell in `matched`
        # still gets SELECTED below regardless, since Save Selected Map
        # acts on the selection, not on which squares happened to get a
        # label. See _exec2_overlay_all_accretech.
        self._exec2_overlay_die_ids = {(d["row"], d["col"]): "/".join(d["die_ids"])
                                       for d in matched if d["die_ids"]}
        self._exec2_overlay_items = self._exec2_draw_overlay_labels_on(
            self._exec2_wafer_map, self._exec2_overlay_die_ids)
        rwm = getattr(self, "_results_wafer_map", None)
        if rwm is not None:
            self._exec2_overlay_result_items = self._exec2_draw_overlay_labels_on(
                rwm, self._exec2_overlay_die_ids)
        picks = [(d["row"], d["col"]) for d in matched]
        self._exec2_wafer_map.set_picked(picks)
        self._exec2_on_sites_changed(picks)
        self._exec2_update_overlay_visibility()

    def _exec2_open_overlay_dialog(self):
        accretech_rc = self._exec2_overlay_accretech_rc()
        if not accretech_rc:
            self._exec2_log("[RUN] Overlay: no wafer map loaded on this Run tab yet — "
                            "load an ATA folder first.")
            return
        footprint = self._exec2_wafer_builder_footprint()

        dlg = tk.Toplevel(self)
        dlg.title("Overlay Wafer Map")
        dlg.transient(self.winfo_toplevel())
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)

        summary_var = tk.StringVar()
        ttk.Label(frm, textvariable=summary_var, font=("Consolas", 9),
                 justify="left").grid(row=1, column=0, columnspan=5, sticky="w",
                                      pady=(0, 4))
        # Wide enough for a real whole-wafer offset (Cenfire's is (-66,-83),
        # a 14,600-die extraction) - +-50 was a leftover from early, much
        # smaller test data and silently clamped any bigger wafer's real
        # alignment. Scaled to the actual loaded map's own row/col span
        # rather than a bigger fixed guess, so it's never too small again.
        rows_span = [rc[0] for rc in accretech_rc]
        cols_span = [rc[1] for rc in accretech_rc]
        row_limit = max(50, max(rows_span) - min(rows_span)) if rows_span else 50
        col_limit = max(50, max(cols_span) - min(cols_span)) if cols_span else 50
        ttk.Label(frm, text="Row offset:").grid(row=3, column=0, sticky="e")
        row_var = tk.IntVar(value=0)
        ttk.Spinbox(frm, from_=-row_limit, to=row_limit, width=6,
                   textvariable=row_var).grid(row=3, column=1, sticky="w", padx=(4, 16))
        ttk.Label(frm, text="Col offset:").grid(row=3, column=2, sticky="e")
        col_var = tk.IntVar(value=0)
        ttk.Spinbox(frm, from_=-col_limit, to=col_limit, width=6,
                   textvariable=col_var).grid(row=3, column=3, sticky="w", padx=(4, 0))

        state = {"grid": [], "matched": []}
        # What was actually on the map before this dialog opened - restored
        # if it's closed without pressing Overlay on Map or Clear Overlay,
        # so just previewing offsets while looking for the right one does
        # not leave an unconfirmed preview sitting on screen.
        prior_die_ids = dict(self._exec2_overlay_die_ids)
        prior_picks = list(self._exec2_wafer_map.get_picked())
        confirmed_this_session = {"value": False}

        # Debounced, not immediate: every spinbox keystroke/arrow-click
        # would otherwise redraw picks/labels on its own - fine for a
        # single click, but a held-down arrow or fast typing fires several
        # a second. Same pattern _exec2_redraw_overlay_on_run_map's caller
        # uses for zoom/pan bursts.
        schedule_live_draw = self._exec2_debounced(
            "_exec2_overlay_dialog_draw_pending",
            lambda: self._exec2_draw_overlay(state["matched"]))

        def recompute(*_a):
            grid = self._exec2_wafer_builder_grid()
            try:
                ro, co = row_var.get(), col_var.get()
            except tk.TclError:
                return
            state["grid"] = grid
            # Selection is bounded to Wafer Builder's own footprint (every
            # real shot it defines, named or not) once the offset is
            # applied - a real ID just earns that square a text label on
            # top. See _exec2_overlay_all_accretech's own docstring.
            state["matched"] = self._exec2_overlay_all_accretech(
                grid, accretech_rc, ro, co, footprint)
            n_with_id = sum(1 for m in state["matched"] if m["die_ids"])
            summary_var.set(
                f"Accretech dies on map:   {len(accretech_rc)}\n"
                f"Wafer Builder footprint: {len(footprint)}  "
                f"(named: {len(grid)})\n"
                f"Will select: {len(state['matched'])}"
                f"  ({n_with_id} labeled with a real ID)"
                + ("" if footprint else
                   "\n\nNo Wafer Builder map loaded - selecting the Accretech "
                   "map's own squares with no ID labels.")
            )
            schedule_live_draw()

        row_var.trace_add("write", recompute)
        col_var.trace_add("write", recompute)

        def center_overlay():
            grid = self._exec2_wafer_builder_grid()
            if not grid:
                recompute()
                return
            ro, co = centroid_offset(grid, accretech_rc)
            row_var.set(ro)
            col_var.set(co)

        center_overlay()

        def do_overlay():
            confirmed_this_session["value"] = True
            self._exec2_overlay_row_offset = row_var.get()
            self._exec2_overlay_col_offset = col_var.get()
            self._exec2_overlay_offset_confirmed = True
            self._exec2_draw_overlay(state["matched"])
            self._exec2_persist_overlay_offset()
            self._exec2_log(f"[RUN] Overlaid {len(state['matched'])} die(s) from the "
                            "Wafer Builder map onto the wafer map.")

        def do_clear():
            confirmed_this_session["value"] = True
            self._exec2_clear_overlay()
            self._exec2_wafer_map.clear_picks()
            self._exec2_on_sites_changed([])
            self._exec2_overlay_offset_confirmed = False
            self._exec2_persist_overlay_offset()
            self._exec2_log("[RUN] Overlay cleared.")

        def close_dialog():
            if not confirmed_this_session["value"]:
                self._exec2_clear_overlay()
                self._exec2_overlay_die_ids = prior_die_ids
                self._exec2_overlay_items = self._exec2_draw_overlay_labels_on(
                    self._exec2_wafer_map, prior_die_ids)
                rwm = getattr(self, "_results_wafer_map", None)
                if rwm is not None:
                    self._exec2_overlay_result_items = self._exec2_draw_overlay_labels_on(
                        rwm, prior_die_ids)
                self._exec2_wafer_map.set_picked(prior_picks)
                self._exec2_on_sites_changed(prior_picks)
                self._exec2_update_overlay_visibility()
            dlg.destroy()

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=5, sticky="ew", pady=(12, 0))
        ttk.Button(btns, text="🖌 Overlay on Map", command=do_overlay).pack(side="left")
        ttk.Button(btns, text="✕ Clear Overlay", command=do_clear).pack(
            side="left", padx=6)
        ttk.Button(btns, text="Close", command=close_dialog).pack(side="right")
        dlg.protocol("WM_DELETE_WINDOW", close_dialog)

        dlg.update_idletasks()
        dlg.grab_set()

    def _exec2_start_test_die(self):
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
        # Full Die/Test Selected are the plain "walk the dies, measure"
        # entry points - Minor Moves is ▶ Run's job now, not theirs. See
        # _exec2_start_full_die's matching refusal.
        if self._system == "accretech" and self._exec2_minor_moves_active():
            self._exec2_log("[RUN] Test Die: this recipe has Minor Moves on — "
                            "use ▶ Run instead (Full Die/Test Selected only "
                            "handle the plain, one-square-one-die case).")
            return
        self._exec2_start_site_list(sites, "Test Die", "test")

    def _exec2_start_site_list(self, sites: list, mode_label: str, run_mode: str):
        """Shared starter for a fixed list of (row, col) touchdowns - Test
        Die/Test Selected's picks, or ▶ Run's saved touchdown list."""
        self._exec2_reset_counts(total_dies=len(sites))
        self._exec2_running  = True
        self._exec2_aborted  = False
        self._exec2_run_mode = run_mode
        self._exec2_run_token += 1
        my_token = self._exec2_run_token
        self._exec2_full_btn.config(state="disabled")
        self._exec2_test_btn.config(state="disabled")
        self.recipe_panel.set_locked(True)
        self._exec2_wafer_map.enable_picking(0)
        self.after(0, lambda: self._exec2_set_state(f"RUNNING ({mode_label})", "#2563eb"))
        self._exec2_log(f"[RUN] ▶ {mode_label} — {len(sites)} site(s): "
                        + ", ".join(f"R{r}C{c}" for r, c in sites))
        self._exec2_lot_thread = threading.Thread(
            target=self._exec2_test_die_thread,
            args=(sites, my_token), daemon=True)
        self._exec2_lot_thread.start()

    def _exec2_test_die_thread(self, sites, my_token: int):
        prober = self.controller.drivers.get("prober")
        sim = not (prober and prober.inst)
        error_msg = None
        try:
            self._exec2_refresh_xy_blocking(prober, sim)
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
            while (self._exec2_running and not self._exec2_aborted
                   and self._exec2_run_token == my_token and idx < len(sites)):
                row, col = sites[idx]
                die_label = f"R{row}C{col}  (X{col} Y{row})"
                self.after(0, lambda d=die_label: self._exec2_die_var.set(f"Die: {d}"))
                self.after(0, lambda x=col, y=row:
                           self._exec2_xy_var.set(f"X: {x} die\nY: {y} die"))
                self._exec2_highlight_current(row, col)
                self._exec2_die_num += 1

                ok = self._exec2_zup_measure_zdown(sim, prober, die_label)
                self._exec2_update_die_color(row, col, ok)
                self.after(0, self._exec2_add_pass if ok else self._exec2_add_fail)

                idx += 1
                if (not self._exec2_running or self._exec2_aborted
                        or self._exec2_run_token != my_token or idx >= len(sites)):
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
            error_msg = str(e)
            self._exec2_log(f"[RUN] ERROR: {e}")
        finally:
            if error_msg:
                self._exec2_finish_run(my_token, f"ERROR: {error_msg[:60]}", "#dc2626")
            else:
                self._exec2_finish_run(my_token, "FINISHED (Test Die)", "#16a34a")


    def _exec2_autoload_default_recipe(self, folder_path):
        """If this ATA folder has a default recipe marked (Recipe tab's ⭐ Set
        as Default), switch to its probe card if needed and load it straight
        into the Run tab — same effect as manually picking it from the
        Recipe dropdown, just automatic on ATA folder open."""
        card, name = load_default_recipe(folder_path, system=self._system)
        if not card or not name:
            return
        if not hasattr(self, "recipe_panel") or not hasattr(self, "_exec2_recipe_var"):
            return
        if self.pin_wiring.get_active_card() != card:
            valid_cards = self.pin_wiring.get_card_names_for_system()
            if card not in valid_cards:
                self._exec2_log(f"[RUN] Default recipe '{name}' wants probe card "
                                f"'{card}', which doesn't exist or isn't wired for "
                                f"this bench — skipping autoload.")
                return
            self.pin_wiring.switch_to_card(card)
        if name not in self.recipe_panel.get_recipe_names():
            self._exec2_log(f"[RUN] Default recipe '{name}' not found on probe card "
                            f"'{card}' — skipping autoload.")
            return
        self._exec2_recipe_var.set(name)
        self._exec2_load_recipe()
        self._exec2_log(f"[RUN] Auto-loaded default recipe '{name}' (probe card '{card}').")

    def _exec2_apply_recipe_sites(self, name: str):
        """Select the recipe's touchdowns on the map, if it defines any.

        This is what makes the touchdown list the recipe's property rather
        than the ATA folder's: loading a recipe re-picks its own dies, so
        switching recipes can no longer inherit the previous one's selection.
        A recipe with no list leaves the map alone - the run then walks
        everything, which is the old behaviour.
        """
        get_sites = getattr(self.recipe_panel, "get_sites", None)
        sites = list(get_sites()) if get_sites else []
        if not sites:
            return
        known = self._exec2_wafer_map.dies
        on_map = [rc for rc in self._exec2_touchdown_cells(sites) if rc in known]
        self._exec2_wafer_map.set_picked(on_map)
        self._exec2_on_sites_changed(on_map)
        missing = len(sites) - len(on_map)
        self._exec2_log(
            f"[RUN] Recipe '{name}' defines {len(sites)} touchdown(s) — "
            f"selected {len(on_map)} on the map."
            + (f"  ⚠ {missing} are not on this wafer map; check that the loaded "
               "map matches the recipe." if missing else ""))
        # A Minor Moves recipe's own SITE table carries one row per DIE it
        # actually references (Cenfire's "first"/"second" pair), each with
        # its own real (row, col) AND its own real die_id - the loaded
        # wafer map file, by contrast, is shot-granularity (one label per
        # shot square, not per RuOx/Au sub-position), so publish_die_slots'
        # per-slot lookup missed the second die of every shot and silently
        # fell back to the shot-level id (the first die's). The recipe's
        # own site records are the authoritative source for exactly the
        # dies this recipe is about to measure - always adopt them here,
        # same as _exec2_load_selected_map does, rather than depending on
        # that function happening to run again after a recipe is picked
        # (it does not - it only fires on initial map draw, before a
        # recipe is normally loaded yet, or as a Test Selected fallback
        # that never triggers once cells are already highlighted).
        get_records = getattr(self.recipe_panel, "get_site_records", None)
        records = list(get_records()) if get_records else []
        ids = {(s["row"], s["col"]): s["die_id"] for s in records if s.get("die_id")}
        if ids:
            self._exec2_clear_overlay()
            self._exec2_overlay_die_ids = ids
            self._exec2_redraw_overlay_on_run_map()
            self._exec2_redraw_overlay_on_results_map()

    def _exec2_load_recipe_by_name(self, name: str):
        """Save button on the Recipe tab calls this too, so saving a recipe
        also loads it into the Run tab - redundant with picking it from the
        Run tab's own Recipe dropdown, on purpose."""
        if not name or not hasattr(self, "_exec2_recipe_var"):
            return
        self._exec2_recipe_var.set(name)
        self._exec2_load_recipe()

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
        self._exec2_apply_recipe_sites(name)

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
            self._exec2_log("[MEASURE] No recipe loaded — pick one from the "
                            "Recipe dropdown first.")
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

    def _exec2_nplc_spec(self, step: dict):
        try:
            nplc = float(step.get("nplc") or 1)
        except ValueError:
            return None
        return nplc if nplc != 1 else None

    def _exec2_measure_averaged(self, smu, smu_ch, read_one, avg_count: int,
                                avg_delay_ms: float, unit: str) -> float:
        """Average a reading, on the instrument itself where it can do it.

        The 2400 averages internally (sens:aver:coun N with tcon rep) and
        returns the mean from ONE :READ?. Averaging in software instead meant N
        separate :READ?s - and with sour:clear:auto on, that is N source cycles
        per die rather than one. Slower than the original LaMP executable, and
        audible: each cycle re-applies the bias to a discharged path, which can
        trip the compliance beeper.

        Falls back to the software loop for anything without set_averages (the
        DMM path), and if the instrument refuses, so a recipe's Averages value
        is always honoured one way or the other.
        """
        # averaged_reading_ok lets a driver advertise set_averages while saying
        # its averaged read is not trusted yet (the 3458A). Anything that does
        # not define it is treated as fine, which is the verified default.
        trusted = getattr(smu, "averaged_reading_ok", True)
        can_hw = (avg_count > 1 and smu is not None
                  and getattr(smu, "inst", None) is not None
                  and hasattr(smu, "set_averages") and trusted)
        if can_hw:
            try:
                smu.set_averages(smu_ch, avg_count)
                value = (smu.read_average() if hasattr(smu, "read_average")
                         else read_one())
                self._exec2_log(f"[MEASURE]      {avg_count} readings averaged "
                                f"inside the {type(smu).__name__} -> "
                                f"{value:.6g} {unit}")
                return value
            except Exception as e:
                self._exec2_log(f"[MEASURE]      instrument averaging failed "
                                f"({type(e).__name__}: {e}) — averaging in software")
        elif avg_count > 1 and not trusted:
            self._exec2_log(f"[MEASURE]      {type(smu).__name__} can average "
                            "internally but that path is unverified — averaging "
                            "in software")
        # Make sure the instrument is NOT also averaging, or the software loop
        # would average an already-averaged value.
        if smu is not None and hasattr(smu, "set_averages"):
            try:
                smu.set_averages(smu_ch, 1)
            except Exception:
                pass
        return self._exec2_take_average(read_one, avg_count, avg_delay_ms, unit)

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

    def _exec2_switch_driver(self):
        """The relay card a recipe's conn channels refer to on this system.

        Accretech has one matrix registered as "switch". Electroglas registers
        its three cards as relay1/relay2/relay3 and has no "switch" at all, so
        looking that key up returned None and every measurement step silently
        took the sim path - random.gauss() numbers recorded as if they were
        readings. relay1 is the wired card on both Electroglas benches
        (probe02's E1345A, probe03's E1364A), per hp_switchbox.BENCH_WIRING.
        """
        drivers = self.controller.drivers
        if self._system == "accretech":
            return drivers.get("switch")
        return drivers.get("relay1") or drivers.get("switch")

    def _exec2_apply_target(self, s, raw_value: float, raw_unit: str, readings_by_name: dict):
        """Combine a measure step's own raw reading with its Target step's
        already-recorded value into a derived quantity - e.g. force current
        on an earlier step, measure voltage here, get resistance out (see
        recipe_panel.compute_target_derived). No Target, an unresolved
        Target, or a unit pairing with no known calculation all fall back to
        the raw reading unchanged - a passfail after this step must always
        get a real value, never a silent None.

        Returns (value, unit, note) - note is a ready-to-append log
        fragment ("" when there was no Target to apply).
        """
        tgt = (s.get("target") or "").strip()
        if not tgt:
            return raw_value, raw_unit, ""
        applied = readings_by_name.get(tgt)
        if applied is None:
            return raw_value, raw_unit, (f"  (target '{tgt}' has no recorded value yet "
                                         "— using the raw reading)")
        derived = compute_target_derived(raw_value, raw_unit, applied[0], applied[1])
        if derived is None:
            return raw_value, raw_unit, (f"  (no known calculation for {raw_unit}+"
                                         f"{applied[1]} — using the raw reading)")
        dv, du = derived
        return dv, du, f"  -> R = {dv:.6g} Ω  (combined with '{tgt}')"

    def _exec2_run_steps_once(self, steps: list = None) -> bool:
        """Run the loaded recipe's steps once, top to bottom, against
        wherever the chuck currently sits.

        `steps` defaults to every loaded step (self._exec2_steps) - the
        normal case; callers with their own already-resolved subset (e.g.
        a per-die replay) can still pass one explicitly. Minor Moves runs
        the full flat list unchanged - a "move" step is what repositions
        the chuck to a different die within the current shot mid-list (see
        self._exec2_move_fn, set by _exec2_minor_move_thread /
        eg_pma_run_panel._minor_move_thread before this is called; a "move"
        step with no such context set just logs and is skipped).
        """
        if steps is None:
            steps = self._exec2_steps
        import random
        import re
        switch = self._exec2_switch_driver()
        smu    = self.controller.drivers.get("smu")
        dmm    = self.controller.drivers.get("dmm")
        wgen   = self.controller.drivers.get("wave_gen")
        sim = not (switch and switch.inst)

        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        recipe_name = self.recipe_panel.get_active_recipe() if hasattr(self, "recipe_panel") else ""
        # The override first: _exec2_die_num is an Accretech-only counter, so on
        # Electroglas it is always 0 and this fell through to the XY label -
        # which was unset, so every exported row read "X: — Y: —".
        die_label = (getattr(self, "_exec2_die_id_override", "")
                     or (self._exec2_die_var.get().replace("Die: ", "")
                         if self._exec2_die_num else
                         self._exec2_xy_var.get().replace("\n", " ")))

        cur_row, cur_col = self._exec2_current_rc or (None, None)
        # Two possible die-ID sources, in priority order:
        #   1. The Overlay dialog's manual die IDs (self._exec2_overlay_die_ids)
        #      — an explicit user action, so it wins if set.
        #   2. The currently-loaded wafer map's own ID column (e.g.
        #      Electroglas's "device_id"), captured by WaferMapPanel into
        #      .die_ids at load time — this is the map's real, authoritative
        #      ID and should be used automatically without any extra step.
        # Whichever wins, it's the same "die_id" every export format reads,
        # so the export always matches what the map/overlay actually shows.
        map_die_id = (self._exec2_wafer_map.die_ids.get((cur_row, cur_col), "")
                      if cur_row is not None else "")
        overlay_die_id = (self._exec2_overlay_die_ids.get((cur_row, cur_col), "")
                          if cur_row is not None else "")
        #   0. A shot-level override set by the Electroglas run, which knows the
        #      whole touchdown ("NA/92-74/NA/93-70") rather than the single die
        #      under one map cell. fldDieID names the SHOT in LaMP's schema -
        #      fldSwitch 1..4 is what picks the die within it - so exporting one
        #      corner's ID made the row claim the wrong device.
        die_id = (getattr(self, "_exec2_die_id_override", "")
                  or overlay_die_id or map_die_id)
        # Whichever probe card is loaded right now, generic to any system/
        # project - "pin_wiring" is each system's own ProbeCardWiringFrame
        # instance, built the same way on both.
        probe_card = (self.pin_wiring.get_active_card()
                     if hasattr(self, "pin_wiring") else "")

        def _shotpos_kwargs(shotpos):
            sr, sc, ir, ic = shotpos or (None, None, None, None)
            return {"shot_row": sr, "shot_col": sc,
                    "intra_row": ir, "intra_col": ic, "probe_card": probe_card}
        last_set_voltage_by_ch = {}

        overall_ok = True
        # die number (from the step's own Die # field) -> verdict. Read by
        # the Electroglas .PMA-stepping pane so each die's own square is
        # coloured.
        self._exec2_slot_verdicts = {}
        last_reading = None
        readings_by_name = {}

        self._exec2_log(f"[MEASURE] One iteration — {len(steps)} step(s)"
                        + ("  [SIM — no switch matrix connected]" if sim else ""))
        for i, s in enumerate(steps, 1):
            # Checked per STEP, not per touchdown: ⏹ Stop means stop, and a
            # shot's recipe is a dozen steps across four dies - finishing it
            # would keep sourcing into the wafer for seconds after the
            # button. The reading already in flight still completes (one
            # blocking GPIB call; abandoning it mid-transfer desyncs the bus
            # for everything after), but nothing new is started.
            if self._exec2_aborted:
                self._exec2_log(f"[MEASURE] ⏹ stopped before step {i} "
                                f"({s.get('name') or 'unnamed'}) — "
                                "remaining steps skipped.")
                self._exec2_mark_all_open()
                return False
            t    = s.get("type")
            name = s.get("name") or f"step {i}"
            lvl  = s.get("level") or ""
            conn = (s.get("conn") or "").replace(" ", "")
            # A step marked direct is cabled instrument-to-probe-card by
            # hand, so it closes nothing even if a stale conn string is still
            # sitting on it from before it was switched over.
            direct = s.get("route") == "direct"
            chans = ([] if direct else
                     [c for c in conn.split(",") if c and c.lower() != "all"])
            conn_str = "DIRECT" if direct else "_".join(chans)
            try:
                if t == "delay":
                    ms = float(lvl or 0)
                    self._exec2_log(f"[MEASURE] {i}. {name}: wait {ms:.0f} ms")
                    time.sleep(ms / 1000.0)
                    continue

                if t == "move":
                    try:
                        die_no = int(float(s.get("die") or "1"))
                    except (TypeError, ValueError):
                        die_no = 1
                    move_fn = getattr(self, "_exec2_move_fn", None)
                    if move_fn is None:
                        self._exec2_log(f"[MEASURE] {i}. {name}: move to die {die_no} "
                                        "— no Minor Moves context active (skipped)")
                        continue
                    self._exec2_log(f"[MEASURE] {i}. {name}: moving to die {die_no}...")
                    try:
                        move_fn(die_no)
                    except RuntimeError as e:
                        # STB=74 ("target die outside probing area") from
                        # move_to_die_xy - this die # exists in the shot
                        # template but has no real die at that position on
                        # THIS wafer (e.g. a shot at the wafer's edge whose
                        # second member falls off the real map). Not a run-
                        # ending error: skip the rest of THIS shot's steps
                        # (the die #1 measurement already taken still
                        # counts) and let the caller move on to the next
                        # shot, same as an aborted run would stop early.
                        self._exec2_log(f"[MEASURE] {i}. {name}: die {die_no} is off the "
                                        f"real wafer map ({e}) — skipping the rest of this "
                                        "shot, moving on to the next one.")
                        self._exec2_mark_all_open()
                        return False
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
                            # A 707B addresses a crosspoint (row, column); a
                            # switchbox card addresses a plain channel number.
                            if hasattr(switch, "open_crosspoint"):
                                switch.open_crosspoint(ch[:2], ch[2:])
                            else:
                                switch.open_channel(ch)
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
                    # Keep each die's verdict as well as the combined one. A
                    # shot's four dies pass or fail independently, so folding
                    # them into a single bool threw away three results.
                    try:
                        die_no = int(float(s.get("die") or "1"))
                    except (TypeError, ValueError):
                        die_no = 1
                    self._exec2_slot_verdicts[die_no] = verdict
                    spec = f"[{mn or '-inf'}, {mx or '+inf'}]"
                    self._exec2_log(f"[MEASURE] {i}. {name}: "
                                    f"{'PASS' if verdict else 'FAIL'}  "
                                    f"{ref_name} = {value:.6g} {unit}  spec {spec}")
                    continue

                mode       = s.get("mode") or ""
                instrument = s.get("instrument") or ""
                label = f"{i}. {name} [{t}{('/' + mode) if mode else ''} " \
                        f"via {instrument}]"
                self._exec2_log(f"[MEASURE] {label}: "
                                + ("direct wiring — no switchbox" if direct
                                   else f"close {conn or '—'}"))
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
                        if not sim and smu and smu.inst:
                            nplc = self._exec2_nplc_spec(s)
                            if nplc is not None:
                                smu.set_nplc(smu_ch, nplc)
                        read_one = ((lambda: abs(random.gauss(50, 15)))
                                   if sim or not (smu and smu.inst)
                                   else (lambda: smu.measure_resistance(smu_ch)))
                    else:
                        read_one = ((lambda: abs(random.gauss(50, 15)))
                                   if sim or not (dmm and dmm.inst)
                                   else (lambda: dmm.measure_resistance()))
                    r_raw = self._exec2_measure_averaged(
                        smu if instrument == "SMU" else dmm, smu_ch,
                        read_one, avg_count, avg_delay, "Ω")
                    r, r_unit, note = self._exec2_apply_target(s, r_raw, "ohm", readings_by_name)
                    self._exec2_log(f"[MEASURE]    R = {r_raw:.4g} Ω  (via {instrument})"
                                    f"{avg_txt}{note}")
                    slot_die, slot_row, slot_col, slot_sw, slot_shotpos = self._exec2_slot_identity(
                        s.get("die"), die_label, (cur_row, cur_col))
                    # slot_die is the die _this step_ actually measured (Minor
                    # Moves published it per-die) - the shot-level die_id
                    # computed once above is only the SHOT's own overlay/map
                    # ID (its anchor cell), so used verbatim it tagged every
                    # die in the shot with the first die's identity. Prefer
                    # the resolved per-slot one whenever a publication
                    # actually happened (slot_sw is not None); fall back to
                    # the shot-level id otherwise (non-Minor-Moves runs).
                    slot_die_id = slot_die if slot_sw is not None else (die_id or None)
                    self.record_result(timestamp=ts, recipe=recipe_name, die=slot_die,
                                       step=name, type=t, mode=mode, value=f"{r:.6g}",
                                       unit=r_unit, die_id=slot_die_id, switch=slot_sw,
                                       connection=conn_str, instrument=instrument,
                                       die_row=slot_row, die_col=slot_col,
                                       **_shotpos_kwargs(slot_shotpos))
                    last_reading = (name, r, r_unit)
                    readings_by_name[name] = (r, r_unit)
                elif t == "voltage" and mode == "measure":
                    if instrument == "SMU":
                        if not sim and smu and smu.inst:
                            nplc = self._exec2_nplc_spec(s)
                            if nplc is not None:
                                smu.set_nplc(smu_ch, nplc)
                        read_one = ((lambda: random.gauss(3.3, 0.1))
                                   if sim or not (smu and smu.inst)
                                   else (lambda: smu.measure_voltage(smu_ch)))
                    else:
                        read_one = ((lambda: random.gauss(3.3, 0.1))
                                   if sim or not (dmm and dmm.inst)
                                   else (lambda: dmm.measure_voltage_dc()))
                    v_raw = self._exec2_measure_averaged(
                        smu if instrument == "SMU" else dmm, smu_ch,
                        read_one, avg_count, avg_delay, "V")
                    v, v_unit, note = self._exec2_apply_target(s, v_raw, "V", readings_by_name)
                    self._exec2_log(f"[MEASURE]    V = {v_raw:.4g} V  (via {instrument})"
                                    f"{avg_txt}{note}")
                    slot_die, slot_row, slot_col, slot_sw, slot_shotpos = self._exec2_slot_identity(
                        s.get("die"), die_label, (cur_row, cur_col))
                    # See the resistance-step case above for why slot_die (not
                    # the shot-level die_id) is preferred here.
                    slot_die_id = slot_die if slot_sw is not None else (die_id or None)
                    self.record_result(timestamp=ts, recipe=recipe_name, die=slot_die,
                                       step=name, type=t, mode=mode, value=f"{v:.6g}",
                                       unit=v_unit, die_id=slot_die_id, switch=slot_sw,
                                       connection=conn_str, instrument=instrument,
                                       die_row=slot_row, die_col=slot_col,
                                       **_shotpos_kwargs(slot_shotpos))
                    last_reading = (name, v, v_unit)
                    readings_by_name[name] = (v, v_unit)
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
                    last_reading = (name, float(lvl or 0), "V")
                    readings_by_name[name] = (float(lvl or 0), "V")
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
                    slot_die, slot_row, slot_col, slot_sw, slot_shotpos = self._exec2_slot_identity(
                        s.get("die"), die_label, (cur_row, cur_col))
                    # See the resistance-step case above for why slot_die (not
                    # the shot-level die_id) is preferred here.
                    slot_die_id = slot_die if slot_sw is not None else (die_id or None)
                    self.record_result(timestamp=ts, recipe=recipe_name, die=slot_die,
                                       step=name, type=t, mode=mode, value=f"{actual_current:.6g}",
                                       unit="A", voltage=actual_voltage, die_id=slot_die_id,
                                       switch=slot_sw, connection=conn_str, instrument=instrument,
                                       die_row=slot_row, die_col=slot_col,
                                       **_shotpos_kwargs(slot_shotpos))
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
                            nplc = self._exec2_nplc_spec(s)
                            if nplc is not None:
                                smu.set_nplc(smu_ch, nplc)
                            # LaMP's MeterRange, carried from the .PMA. Pinned
                            # rather than autoranged, so a different PMA
                            # reconfigures the meter on LOAD ALL instead of
                            # inheriting whatever the last recipe left set.
                            mrange = (s.get("mrange") or "").strip()
                            if mrange and hasattr(smu, "set_current_range"):
                                try:
                                    smu.set_current_range(smu_ch, float(mrange))
                                except (TypeError, ValueError) as e:
                                    self._exec2_log(f"[MEASURE]    ignoring bad "
                                                    f"meter range {mrange!r}: {e}")
                            # sour:clear:auto on drops the output after every
                            # :READ?, so each of the averaged readings
                            # re-applies the bias to a discharged path. With no
                            # source delay the integration starts on the
                            # charging transient - a good die read ~90 nA where
                            # the original LaMP data shows sub-nanoamp. This is
                            # LaMP's MeterDelay, carried on the step as
                            # avg_delay (ms).
                            if avg_delay and hasattr(smu, "set_source_delay"):
                                smu.set_source_delay(avg_delay / 1000.0)
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
                    i_raw = self._exec2_measure_averaged(
                        smu if instrument == "SMU" else dmm, smu_ch,
                        read_one, avg_count, avg_delay, "A")
                    if instrument == "SMU" and not sim and smu and smu.inst:
                        try:
                            actual_voltage = smu.measure_voltage(smu_ch)
                        except Exception:
                            actual_voltage = None
                    i_a, i_unit, note = self._exec2_apply_target(s, i_raw, "A", readings_by_name)
                    self._exec2_log(f"[MEASURE]    I = {i_raw:.4g} A{bias_txt}{avg_txt}{note}")
                    if actual_voltage is None:
                        actual_voltage = set_voltage
                    slot_die, slot_row, slot_col, slot_sw, slot_shotpos = self._exec2_slot_identity(
                        s.get("die"), die_label, (cur_row, cur_col))
                    # See the resistance-step case above for why slot_die (not
                    # the shot-level die_id) is preferred here.
                    slot_die_id = slot_die if slot_sw is not None else (die_id or None)
                    self.record_result(
                        timestamp=ts, recipe=recipe_name, die=slot_die,
                        step=name, type=t, mode=mode, value=f"{i_a:.6g}", unit=i_unit,
                        die_id=slot_die_id,
                        switch=slot_sw,
                        die_row=slot_row, die_col=slot_col,
                        set_voltage=set_voltage, voltage=actual_voltage,
                        connection=conn_str, instrument=instrument,
                        **_shotpos_kwargs(slot_shotpos))
                    last_reading = (name, i_a, i_unit)
                    readings_by_name[name] = (i_a, i_unit)
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


    def _exec2_slot_identity(self, die_no, fallback_die, fallback_rc):
        """(die label, row, col, switch, shotpos) for a step's own Die #
        field. shotpos is (shot_row, shot_col, intra_row, intra_col) or
        None when nothing published one (non-Minor-Moves, or a system/
        recipe with no shot concept at all).

        Replaces the old "... (Die N)" name-suffix convention - a step now
        carries its die number directly (recipe_panel._STEP_FIELDS "die"),
        so this no longer depends on how the step happens to be named.

        The Electroglas run publishes the shot's die IDs and map cells in
        QUAD_ORDER before each touchdown, and Accretech Minor Moves
        publishes the shot's real per-die coordinates/reticle position
        (_exec2_minor_move_thread.publish_die_slots), before each
        touchdown, so a per-die step can be filed against the die it
        actually measured rather than against the shot's anchor cell.

        The test is whether that publication EXISTS, not whether die_no is
        greater than 1. Blank normalizes to "1", so "die 1" and "no die set"
        look identical here - short-circuiting on die_no <= 1 therefore filed
        die 1 of a quad under the whole shot's ID with a blank fldSwitch,
        while dies 2..4 got their own. One shot exported three individual
        dies and one shot-shaped row, and LaMP's fldSwitch 1..4 became
        0,2,3,4. With no publication (Accretech, or a single-die shot) there
        are no slots to file against and the shot-level fallback is right.
        """
        try:
            switch = int(float(die_no))
        except (TypeError, ValueError):
            switch = 1
        ids = getattr(self, "_exec2_die_ids_by_slot", None) or []
        rcs = getattr(self, "_exec2_die_rc_by_slot", None) or []
        shotpos_list = getattr(self, "_exec2_die_shotpos_by_slot", None) or []
        slot = switch - 1
        if switch < 1 or not (slot < len(ids) or slot < len(rcs)):
            return fallback_die, fallback_rc[0], fallback_rc[1], None, None
        die = ids[slot] if 0 <= slot < len(ids) and ids[slot] else fallback_die
        rc = rcs[slot] if 0 <= slot < len(rcs) and rcs[slot] else fallback_rc
        shotpos = shotpos_list[slot] if 0 <= slot < len(shotpos_list) else None
        return die, rc[0], rc[1], switch, shotpos

    def record_result(self, timestamp, recipe, die, step, type, mode, value, unit,
                      die_id=None, switch=None, set_voltage=None, voltage=None,
                      connection=None, instrument=None, die_row=None, die_col=None,
                      shot_row=None, shot_col=None, intra_row=None, intra_col=None,
                      probe_card=None):
        row = {"timestamp": timestamp, "recipe": recipe, "die": die, "step": step,
               "type": type, "mode": mode, "value": value, "unit": unit,
               "die_id": die_id or "", "switch": switch if switch is not None else "",
               "set_voltage": set_voltage if set_voltage is not None else "",
               "voltage": voltage if voltage is not None else "",
               "connection": connection or "", "instrument": instrument or "",
               "row": die_row, "col": die_col,
               # Blank on any run that never resolved a shot for this die
               # (non-Minor-Moves, or a system with no shot concept at
               # all) - see _exec2_slot_identity/_exec2_minor_move_thread.
               "shot_row": shot_row if shot_row is not None else "",
               "shot_col": shot_col if shot_col is not None else "",
               "intra_row": intra_row if intra_row is not None else "",
               "intra_col": intra_col if intra_col is not None else "",
               "probe_card": probe_card or ""}
        self.controller.results_data.append(row)
        if hasattr(self, "_results_tree"):
            def _ui():
                self._results_tree.insert("", "end", values=(
                    row["timestamp"], row["recipe"], row["die"], row["step"],
                    row["type"], row["value"], row["unit"]))
                kids = self._results_tree.get_children()
                if kids:
                    self._results_tree.see(kids[-1])
            self._exec2_safe_after(_ui)

    def clear_results(self):
        self.controller.results_data.clear()
        self._exec2_last_run_start_idx = 0
        if hasattr(self, "_results_tree"):
            self._results_tree.delete(*self._results_tree.get_children())

    def get_last_run_results(self) -> list:
        """Results from the most recently started run only (Full Die/Test
        Die/Test Selected) — what export formats other than plain
        "Save as CSV" should write, so re-running doesn't accumulate old
        runs' rows into a new export."""
        return self.controller.results_data[self._exec2_last_run_start_idx:]


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

    def _exec2_manual_prev_die(self):
        """Back: no native "previous die" GPIB command exists on this
        hardware (only "J" Next Die - see _exec2_manual_next_die), so this
        is the closest die-mode equivalent - a plain relative die-index
        step backward (S command, X-1), not a walk through any GUI-side
        site list. Bounded/verified the same way every other relative
        Accretech move in this file is (see move_xy_relative's own STB
        handling in instruments/accretech_uf200r.py)."""
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log("[EXEC2] Back: prober not connected.")
            return
        def _run():
            try:
                self.after(0, lambda: self._exec2_log("[EXEC2] >> S  (X-1, previous die)"))
                stb = prober.move_xy_relative(-1, 0)
                self.after(0, lambda: self._exec2_log(f"[EXEC2] << STB={stb}"))
                self.after(0, self._exec2_get_xy)
            except Exception as e:
                self.after(0, lambda e=e: self._exec2_log(f"[EXEC2] Back error: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _exec2_manual_next_die(self):
        """Next: plain native J - the prober's own "next die" per its
        internal wafer map. Nothing to do with shots, the picked-sites
        list, or Minor Moves - just the bare hardware command, same as
        Electroglas's Next (eg_pma_run_panel._step_once) is the bare .PMA
        step, not a shot-aware move."""
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log("[EXEC2] Next: prober not connected.")
            return
        def _run():
            try:
                self.after(0, lambda: self._exec2_log("[EXEC2] >> J  (next die)"))
                stb = prober.next_die()
                self.after(0, lambda: self._exec2_log(f"[EXEC2] << STB={stb}"))
                self.after(0, self._exec2_get_xy)
            except Exception as e:
                self.after(0, lambda e=e: self._exec2_log(f"[EXEC2] Next error: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _exec2_shot_step_setup(self, label: str):
        """Shared preflight for Next Shot/Previous Shot: the prober, Wafer
        Builder, confirmed Overlay alignment, shot size, and the sorted
        (row-major) shot list all need to exist before either can compute
        anything. Returns (prober, gen, shots, shot_rows, shot_cols,
        row_off, col_off) or None (already logged why) if not."""
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log(f"[EXEC2] {label}: prober not connected.")
            return None
        gen = getattr(self, "recipe_gen", None)
        if gen is None:
            self._exec2_log(f"[EXEC2] {label}: the Wafer Builder tab is not available.")
            return None
        if not self._exec2_overlay_offset_confirmed:
            self._exec2_log(f"[EXEC2] {label}: no confirmed Overlay alignment — "
                            "press Overlay… (above) and confirm it first.")
            return None
        try:
            shot_rows, shot_cols = gen._shot_dims()
        except Exception:
            self._exec2_log(f"[EXEC2] {label}: could not read the Wafer Builder shot size.")
            return None
        shots = sorted((sr, sc) for (sr, sc), present in gen._shotmap_cells.items() if present)
        if not shots:
            self._exec2_log(f"[EXEC2] {label}: no shots on the Wafer Builder Shot Map tab.")
            return None
        return (prober, gen, shots, shot_rows, shot_cols,
               self._exec2_overlay_row_offset, self._exec2_overlay_col_offset)

    def _exec2_go_to_shot(self, prober, gen, shot_row: int, shot_col: int,
                          shot_rows: int, shot_cols: int, row_off: int, col_off: int,
                          label: str):
        """Separate, jump to (shot_row, shot_col)'s die #1, same as Minor
        Moves' own landing (_exec2_minor_move_thread's goto_shot_die)."""
        r, c = shot_die_rc(dict(gen._shot_cells), shot_rows, shot_cols, 1) or (0, 0)
        die_x = shot_col * shot_cols + c + col_off
        die_y = shot_row * shot_rows + r + row_off
        def _run():
            try:
                self.after(0, lambda: self._exec2_log("[EXEC2] >> D  (Separate)"))
                prober.z_down()
                self.after(0, lambda: self._exec2_log(
                    f"[EXEC2] >> J  ({label} -> shot R{shot_row}C{shot_col}, "
                    f"die #1, X={die_x} Y={die_y})"))
                stb = prober.move_to_die_xy(die_x, die_y)
                self.after(0, lambda: self._exec2_log(f"[EXEC2] << STB={stb}"))
                self.after(0, self._exec2_get_xy)
                self.after(0, lambda: self._exec2_highlight_current(die_y, die_x))
            except Exception as e:
                self.after(0, lambda e=e: self._exec2_log(f"[EXEC2] {label} error: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _exec2_current_shot_index(self, shots: list, shot_rows: int, shot_cols: int,
                                  row_off: int, col_off: int) -> "int | None":
        """Index into `shots` of whichever shot the current real die
        position falls in, or None if unknown/not on the list."""
        if self._exec2_current_rc is None:
            return None
        wb_row = self._exec2_current_rc[0] - row_off
        wb_col = self._exec2_current_rc[1] - col_off
        cur_shot = (wb_row // shot_rows, wb_col // shot_cols)
        try:
            return shots.index(cur_shot)
        except ValueError:
            return None

    def _exec2_manual_next_shot(self):
        """Advance to die #1 of the NEXT shot (Wafer Builder Shot Map tab's
        shots, row-major order) - an absolute die-coordinate move, not a
        native command - Accretech has none that understands "shot"."""
        setup = self._exec2_shot_step_setup("Next Shot")
        if setup is None:
            return
        prober, gen, shots, shot_rows, shot_cols, row_off, col_off = setup
        cur_idx = self._exec2_current_shot_index(shots, shot_rows, shot_cols, row_off, col_off)
        idx = 0 if cur_idx is None else cur_idx + 1
        if idx >= len(shots):
            self._exec2_log("[EXEC2] Next Shot: already at the last shot.")
            return
        shot_row, shot_col = shots[idx]
        self._exec2_go_to_shot(prober, gen, shot_row, shot_col, shot_rows, shot_cols,
                               row_off, col_off, "Next Shot")

    def _exec2_manual_prev_shot(self):
        """Same as Next Shot, one shot back instead."""
        setup = self._exec2_shot_step_setup("Previous Shot")
        if setup is None:
            return
        prober, gen, shots, shot_rows, shot_cols, row_off, col_off = setup
        cur_idx = self._exec2_current_shot_index(shots, shot_rows, shot_cols, row_off, col_off)
        idx = (len(shots) - 1) if cur_idx is None else cur_idx - 1
        if idx < 0:
            self._exec2_log("[EXEC2] Previous Shot: already at the first shot.")
            return
        shot_row, shot_col = shots[idx]
        self._exec2_go_to_shot(prober, gen, shot_row, shot_col, shot_rows, shot_cols,
                               row_off, col_off, "Previous Shot")

    _EXEC2_MOVE_TARGET_COLOR = "#1e3a8a"  # dark blue - distinct from the pick color

    def _exec2_move_selected_button(self):
        """➡ Move to Selected is a self-contained arm/target toggle, NOT a
        reader of the normal pick system (_exec2_wafer_map.get_picked(),
        which Test Selected/Save Selected Map/Overlay all share and which
        this must never disturb):

          IDLE ("➡ Move to Selected") --click--> ARMED, no target
              ("✕ Cancel Move") --click a die--> ARMED, one target,
              highlighted dark blue ("➡ Move")

        While armed, clicking dies is intercepted via set_click_handler
        (see _exec2_move_target_click) instead of going through picking -
        picking itself is suspended (not cleared) for the duration, so any
        real Test Selected picks are exactly as they were once this is
        done. Clicking the target again deselects it (back to "Cancel
        Move"); clicking a different die just moves the highlight - only
        one target at a time. Pressing the button with a target executes
        the move and returns to idle; with no target, it cancels.
        """
        wm = self._exec2_wafer_map
        if not self._exec2_move_armed:
            self._exec2_move_armed = True
            self._exec2_move_target_rc = None
            self._exec2_move_prev_click_handler = wm._click_handler
            self._exec2_move_prev_picking_enabled = wm._picking_enabled
            wm._picking_enabled = False
            wm.set_click_handler(self._exec2_move_target_click)
            self._exec2_move_selected_btn.config(text="✕ Cancel Move")
            return
        target = self._exec2_move_target_rc
        self._exec2_disarm_move_selected()
        if target is None:
            self._exec2_log("[EXEC2] Move to Selected: cancelled.")
            return
        self._exec2_do_move_to(*target)

    def _exec2_move_target_click(self, row: int, col: int):
        if not self._exec2_move_armed:
            return
        wm = self._exec2_wafer_map
        rc = (row, col)
        if rc not in wm.dies:
            return
        if rc == self._exec2_move_target_rc:
            self._exec2_restore_move_target_color()
            self._exec2_move_target_rc = None
            self._exec2_move_selected_btn.config(text="✕ Cancel Move")
            return
        self._exec2_restore_move_target_color()
        item = wm.dies[rc]
        self._exec2_move_target_prev_fill = wm.canvas.itemcget(item, "fill")
        wm.canvas.itemconfig(item, fill=self._EXEC2_MOVE_TARGET_COLOR)
        self._exec2_move_target_rc = rc
        self._exec2_move_selected_btn.config(text="➡ Move")

    def _exec2_restore_move_target_color(self):
        wm = self._exec2_wafer_map
        rc = self._exec2_move_target_rc
        if rc is not None and rc in wm.dies and self._exec2_move_target_prev_fill is not None:
            try:
                wm.canvas.itemconfig(wm.dies[rc], fill=self._exec2_move_target_prev_fill)
            except tk.TclError:
                pass

    def _exec2_disarm_move_selected(self):
        self._exec2_restore_move_target_color()
        self._exec2_move_target_rc = None
        self._exec2_move_target_prev_fill = None
        wm = self._exec2_wafer_map
        wm.set_click_handler(self._exec2_move_prev_click_handler)
        wm._picking_enabled = self._exec2_move_prev_picking_enabled
        self._exec2_move_armed = False
        self._exec2_move_selected_btn.config(text="➡ Move to Selected")

    def _exec2_do_move_to(self, row: int, col: int):
        """Move straight to (row, col) - Z down first (never travel in X/Y
        while contacted), then the absolute die-coordinate move.
        Deliberately does NOT Z up afterward - this is a positioning aid
        (e.g. lining up before a manual Z Up/Measure), not a touchdown of
        its own."""
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self._exec2_log("[EXEC2] Move to Selected: prober not connected.")
            return
        def _run():
            try:
                self.after(0, lambda: self._exec2_log("[EXEC2] >> D  (Separate)"))
                prober.z_down()
                self.after(0, lambda: self._exec2_log(
                    f"[EXEC2] >> J  (X={col} Y={row})"))
                stb = prober.move_to_die_xy(col, row)
                self.after(0, lambda: self._exec2_log(f"[EXEC2] << STB={stb}"))
                self.after(0, self._exec2_get_xy)
                self.after(0, lambda: self._exec2_highlight_current(row, col))
            except Exception as e:
                self.after(0, lambda e=e: self._exec2_log(
                    f"[EXEC2] Move to Selected error: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _exec2_refresh_xy_blocking(self, prober, sim: bool):
        """The automatic, run-thread version of the ↻ Refresh XY button -
        called right before a run's first move (Full Die/Test Die/Test
        Selected/Minor Moves), so the displayed X/Y, the highlighted die,
        and self._exec2_current_rc are read fresh rather than left over
        from whatever happened before Start was pressed (a manual jog, the
        previous run's last die, ...). Runs ON the calling thread (already
        off the main thread by the time any of those call this) - blocking
        here is the point, unlike the ↻ Refresh XY button's own fire-and-
        forget _exec2_get_xy.
        """
        if sim:
            return
        try:
            raw = prober.get_xy_position()
            x, y = _parse_q_response(raw)
            self._exec2_safe_after(lambda: self._exec2_xy_var.set(f"X: {x:.0f} die\nY: {y:.0f} die"))
            self._exec2_safe_after(lambda: self._exec2_log(f"[RUN] Q → die X={x:.0f}  Y={y:.0f}"))
            self._exec2_safe_after(lambda: self._exec2_highlight_current(int(y), int(x)))
        except Exception as e:
            self._exec2_log(f"[RUN] Refresh XY before run failed: {e}")

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
        if self._system == "accretech":
            self._exec2_update_shot_window()

    def _exec2_clear_shot_window(self):
        wm = getattr(self, "_exec2_wafer_map", None)
        if wm is not None:
            for item in self._exec2_shot_window_items:
                try:
                    wm.canvas.delete(item)
                except Exception:
                    pass
        self._exec2_shot_window_items = []

    def _exec2_update_shot_window(self):
        """Outline, on the Run tab's wafer map, the block of REAL dies the
        current shot spans - the Accretech equivalent of NanoZ's 1x20
        window and Electroglas's 2x2 quad window (see
        eg_pma_run_panel._draw_shot_window) - now that a shot can be more
        than one physical die (Minor Moves), a single highlighted square no
        longer shows the whole touchdown's footprint.

        Skipped (and cleared) when: the wafer's shots are 1 die each
        (Cenfire-style multi-die shots are exactly the case this is FOR -
        nothing to outline beyond the die itself otherwise), the live XY
        position isn't known yet, or the Wafer Builder<->Accretech
        alignment (Overlay) was never confirmed - the block's real
        die-coordinates can't be computed without that offset. Draws
        against whatever's actually on screen, so a shot corner that's
        genuinely absent from the real Accretech extraction (wafer edge)
        just narrows the box instead of guessing.
        """
        self._exec2_clear_shot_window()
        wm = getattr(self, "_exec2_wafer_map", None)
        gen = getattr(self, "recipe_gen", None)
        if (wm is None or gen is None or self._exec2_current_rc is None
                or not self._exec2_overlay_offset_confirmed):
            return
        try:
            shot_rows, shot_cols = gen._shot_dims()
        except Exception:
            return
        if shot_rows <= 1 and shot_cols <= 1:
            return
        cur_row, cur_col = self._exec2_current_rc
        row_off = self._exec2_overlay_row_offset
        col_off = self._exec2_overlay_col_offset
        wb_row, wb_col = cur_row - row_off, cur_col - col_off
        shot_r0 = (wb_row // shot_rows) * shot_rows
        shot_c0 = (wb_col // shot_cols) * shot_cols
        cells = [(shot_r0 + r + row_off, shot_c0 + c + col_off)
                for r in range(shot_rows) for c in range(shot_cols)]
        boxes = [wm.canvas.coords(wm.dies[rc]) for rc in cells if rc in wm.dies]
        boxes = [b for b in boxes if len(b) >= 4]
        # Diagnostic (temporary) - if the box turns out misaligned with the
        # overlay's own die-ID labels, this line has everything needed to
        # tell whether it's the offset, the shot dims, or the current
        # position that's wrong. Deduped against the last logged inputs so
        # a zoom/pan burst (which also calls this) doesn't flood the log.
        diag_key = (cur_row, cur_col, row_off, col_off, shot_rows, shot_cols)
        if getattr(self, "_exec2_shot_window_last_diag", None) != diag_key:
            self._exec2_shot_window_last_diag = diag_key
            self._exec2_log(
                f"[SHOT WINDOW] die R{cur_row}C{cur_col} -> WB R{wb_row}C{wb_col} "
                f"-> shot block R{shot_r0}..{shot_r0 + shot_rows - 1}"
                f"C{shot_c0}..{shot_c0 + shot_cols - 1} (real, offset row{row_off:+d} "
                f"col{col_off:+d}) — {len(boxes)}/{len(cells)} cells on screen")
        if not boxes:
            return
        box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
              max(b[2] for b in boxes), max(b[3] for b in boxes))
        rect = wm.canvas.create_rectangle(*box, outline="#7c3aed", width=2, dash=(4, 3))
        wm.canvas.tag_raise(rect)
        self._exec2_shot_window_items = [rect]

    def _exec2_add_pass(self):
        self._exec2_pass_var.set(self._exec2_pass_var.get() + 1)
        self._exec2_update_yield()
        self._exec2_push_stats()

    def _exec2_add_fail(self):
        self._exec2_fail_var.set(self._exec2_fail_var.get() + 1)
        self._exec2_update_yield()
        self._exec2_push_stats()

    def _exec2_reset_counts(self, total_dies=None):
        self._exec2_last_run_start_idx = len(self.controller.results_data)
        self._exec2_pass_var.set(0)
        self._exec2_fail_var.set(0)
        # The PMA runner keeps its own verdict-per-touchdown record and paints
        # the map from it; zeroing the counters without clearing that would
        # leave green/red squares that nothing counts any more.
        reset = getattr(getattr(self, "eg_pma_run", None), "reset_results", None)
        if reset:
            try:
                reset()
            except Exception:
                pass
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
        page = ttk.Frame(nb)
        nb.add(page, text="Results")
        self.results_tab_frame = page
        page.rowconfigure(0, weight=1)
        page.columnconfigure(0, weight=1)

        # Vertical PanedWindow instead of a plain scroll wrapper - drag the
        # sashes between sections to give more room to whichever one you
        # need (wafer map, export controls, results table, ...).
        split = ttk.PanedWindow(page, orient="vertical")
        split.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # Both systems get the pass/fail wafer map at the top, above Data
        # Export. Electroglas used to get a donut of run statistics down at
        # the bottom instead, which said less than the map does and did not
        # let you click a die to read its measurements.
        wafer_pane = ttk.Frame(split)
        split.add(wafer_pane, weight=3)
        self._build_results_wafer_map(wafer_pane)

        export_frame = ttk.LabelFrame(split, text="Data Export")
        split.add(export_frame, weight=0)

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
        if self._system == "accretech":
            self._export_dir_choices = {
                "PROBE08 (network)": r"\\prober\NewData\ETL\RAWDATA\PROBE08",
                "Downloads": self._downloads_dir,
            }
            export_dir_var = tk.StringVar(value="PROBE08 (network)")
            export_dir_cb = ttk.Combobox(
                path_row, textvariable=export_dir_var, state="readonly",
                width=16, values=list(self._export_dir_choices.keys()))
            export_dir_cb.pack(side="left", padx=(4, 0))
            export_dir_cb.bind(
                "<<ComboboxSelected>>",
                lambda _e: self.export_path_var.set(
                    self._export_dir_choices[export_dir_var.get()]))
        ttk.Button(
            path_row, text="Save to CSV", command=self.controller.cmd_save_csv
        ).pack(side="left", padx=10)
        ttk.Button(
            path_row, text="📂 Import CSV",
            command=self.controller.cmd_import_results_csv
        ).pack(side="left", padx=(0, 4))

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
        ttk.Button(
            sql_row, text="⭐ Set Default", command=self._set_default_export_format
        ).pack(side="left", padx=(6, 0))
        ttk.Button(
            sql_row, text="🗑 Delete", command=self._delete_export_format
        ).pack(side="left", padx=(6, 0))
        # Push straight into an Access database instead of writing a .sql
        # file for someone to run later. Electroglas only for now: LaMP's
        # tblLampElectricalMeasurements is the database this exists for.
        if self._system == "electroglas":
            self._build_mdb_row(export_frame)

        self._export_formats: list = []
        self._export_default_lbl_var = tk.StringVar(value="")
        ttk.Label(export_frame, textvariable=self._export_default_lbl_var,
                 foreground="#6b7280", font=("Segoe UI", 8)).pack(
                 anchor="w", padx=10, pady=(0, 8))

        results_lf = ttk.LabelFrame(split, text="Measurement Results")
        split.add(results_lf, weight=2)
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

    # ------------------------------------------------------------------
    # ACCESS DATABASE PUSH
    #
    # An .mdb is a FILE, not a server - pushing writes rows into that file
    # and nothing else. Point this at the shared copy on the network and
    # everyone reading it sees the rows; point it at a local copy and the
    # rows go nowhere but that copy. See mdb_export's module docstring.
    # ------------------------------------------------------------------
    def _build_mdb_row(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(row, text="Access DB (.mdb):").pack(side="left")
        self.mdb_path_var = tk.StringVar(
            value=app_settings.load_settings().get("mdb_path", ""))
        ttk.Entry(row, textvariable=self.mdb_path_var, width=38).pack(
            side="left", padx=6)
        ttk.Button(row, text="Browse…", command=self._mdb_browse).pack(
            side="left", padx=2)
        ttk.Button(row, text="🔎 Check", command=self._mdb_check).pack(
            side="left", padx=(8, 2))
        ttk.Button(row, text="⬆ Push to DB", command=self._mdb_push).pack(
            side="left", padx=2)
        self._mdb_status_var = tk.StringVar(value="")
        ttk.Label(parent, textvariable=self._mdb_status_var, foreground="#6b7280",
                 font=("Segoe UI", 8), wraplength=620, justify="left").pack(
                 anchor="w", padx=10, pady=(0, 8))

    def _mdb_say(self, text: str):
        """Status line, or nothing on a system that never built the row.

        The push methods live on MainLayout for both systems but only
        Electroglas draws the controls, so on Accretech the status var does
        not exist. Nothing can reach them there through the UI - this just
        keeps that an inert fact rather than an AttributeError waiting for
        the first caller who does not know it.
        """
        var = getattr(self, "_mdb_status_var", None)
        if var is not None:
            var.set(text)

    def _mdb_browse(self):
        path = filedialog.askopenfilename(
            title="Select the Access database to push results into",
            filetypes=[("Access database", "*.mdb *.accdb"), ("All files", "*.*")])
        if not path:
            return
        self.mdb_path_var.set(path)
        # Remembered globally, not per ATA folder: it is one shared database
        # for the line, and re-picking it for every lot would be busywork.
        settings = app_settings.load_settings()
        settings["mdb_path"] = path
        app_settings.save_settings(settings)
        self._mdb_check()

    def _mdb_format(self):
        fmt = self.get_selected_export_format()
        if not fmt:
            self._mdb_say(
                "Pick an Export Format first — it says which table and columns "
                "to write.")
            return None
        if fmt.get("type") == "csv":
            self._mdb_say(
                f"'{fmt['name']}' is a CSV format — a database push needs a SQL "
                "format (one with a table and columns), such as the LaMP one.")
            return None
        return fmt

    def _mdb_check(self):
        fmt = self._mdb_format()
        if not fmt:
            return None
        info = mdb_export.preflight(getattr(self, "mdb_path_var", tk.StringVar()).get().strip(), fmt["table"])
        if not info["ok"]:
            self._mdb_say("✖  " + "  ".join(info["problems"]))
            self.controller.log("[MDB] Check failed — " + "; ".join(info["problems"]))
            return None
        missing = [c["field"] for c in fmt["columns"]
                   if c["field"].lower() not in {x.lower() for x in info["columns"]}]
        if missing:
            msg = (f"✖  '{fmt['table']}' exists but has no column(s): "
                  f"{', '.join(missing)} — the format and the table disagree.")
            self._mdb_say(msg)
            self.controller.log("[MDB] " + msg)
            return None
        n = info["row_count"]
        self._mdb_say(
            f"✔  {os.path.basename(getattr(self, "mdb_path_var", tk.StringVar()).get())} — table "
            f"'{fmt['table']}' found"
            + (f", {n} row(s) already in it" if n is not None else "")
            + f".  Driver: {info['driver']}.")
        return info

    def _mdb_push(self):
        fmt = self._mdb_format()
        if not fmt:
            return
        if not self._mdb_check():
            return
        lot = self.lot_id.get().strip()
        if not lot:
            self._mdb_say("✖  Enter a Lot ID first — it is what "
                                     "fldTestSerial is computed from.")
            return
        wafer = self.wafer_id_var.get().strip()
        # The last run only, matching what "💾 Export" writes - so the file
        # and the database always describe the same run.
        results = self.get_last_run_results()
        ata_folder = getattr(self, "_ata_folder", "") or ""
        fields, rows = mdb_export.build_rows(fmt, results, lot, wafer, ata_folder)
        if not rows:
            self._mdb_say(
                "✖  No rows from the last run match this format "
                "(it needs readings that carry a device ID).")
            return
        path = getattr(self, "mdb_path_var", tk.StringVar()).get().strip()
        if not messagebox.askokcancel(
                "Push to Database",
                f"Insert {len(rows)} row(s) into [{fmt['table']}]\nin "
                f"{path}?\n\nThis writes directly into that file. If it is the "
                "shared copy on the network, everyone reading it sees these "
                "rows straight away — there is no undo."):
            return
        res = mdb_export.push(path, fmt, results, lot, wafer, folder=ata_folder)
        if res["ok"]:
            msg = (f"✔  Pushed {res['inserted']} row(s) into "
                  f"[{res['table']}] — lot {lot}"
                  + (f", wafer {wafer}" if wafer else "") + ".")
            self._mdb_say(msg)
            self.controller.log("[MDB] " + msg)
        else:
            self._mdb_say("✖  " + res["error"])
            self.controller.log("[MDB] Push failed — " + res["error"])

    def _build_results_wafer_map(self, tab):
        map_frame = ttk.LabelFrame(tab, text="Wafer Map — Pass / Fail")
        map_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        map_frame.rowconfigure(1, weight=1)
        map_frame.columnconfigure(0, weight=2)
        map_frame.columnconfigure(1, weight=1)

        top_row = ttk.Frame(map_frame)
        top_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))
        self.lbl_results_large = ttk.Label(
            top_row, text="Total Passed: 0     |     Total Failed: 0     |     Untested: 0",
            font=("Arial", 11, "bold"))
        self.lbl_results_large.pack(side="left")
        zoom_bar = ttk.Frame(top_row)
        zoom_bar.pack(side="right")
        ttk.Button(zoom_bar, text="🔍+", width=3,
                  command=lambda: self._results_wafer_map.zoom_in()).pack(side="left")
        ttk.Button(zoom_bar, text="🔍-", width=3,
                  command=lambda: self._results_wafer_map.zoom_out()).pack(side="left", padx=(2, 0))
        ttk.Button(zoom_bar, text="Reset View",
                  command=lambda: self._results_wafer_map._reset_view()).pack(
                  side="left", padx=(6, 0))

        self._results_map_frame = map_frame
        self._new_results_wafer_map()

        detail_lf = ttk.LabelFrame(map_frame, text="Selected Die")
        detail_lf.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))
        detail_lf.rowconfigure(1, weight=1)
        detail_lf.columnconfigure(0, weight=1)

        self._results_die_var = tk.StringVar(
            value="Click a die on the map to see its measurements.")
        ttk.Label(detail_lf, textvariable=self._results_die_var, wraplength=220,
                 justify="left").grid(row=0, column=0, sticky="w", padx=6, pady=6)

        dcols = ("step", "type", "value", "unit")
        self._results_die_tree = ttk.Treeview(detail_lf, columns=dcols, show="headings", height=10)
        for cid, text, width in (("step", "Step", 90), ("type", "Type", 60),
                                 ("value", "Value", 70), ("unit", "Unit", 40)):
            self._results_die_tree.heading(cid, text=text)
            self._results_die_tree.column(cid, width=width, anchor="w" if cid == "step" else "center")
        self._results_die_tree.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        ddsb = ttk.Scrollbar(detail_lf, orient="vertical", command=self._results_die_tree.yview)
        ddsb.grid(row=1, column=1, sticky="ns")
        self._results_die_tree.configure(yscrollcommand=ddsb.set)

        self._results_selected_rc = None
        self._sync_results_wafer_map()

    def _on_results_map_click(self, event):
        wm = self._results_wafer_map
        cx, cy = wm.canvas.canvasx(event.x), wm.canvas.canvasy(event.y)
        rc = wm._hit_die(cx, cy)
        if rc is None:
            return
        self._results_show_die(rc)

    def _results_show_die(self, rc):
        wm = getattr(self, "_results_wafer_map", None)
        if wm is None:
            return
        prev = self._results_selected_rc
        if prev is not None and prev in wm.dies:
            try:
                wm.canvas.itemconfig(wm.dies[prev], width=1)
            except Exception:
                pass
        self._results_selected_rc = rc
        if rc in wm.dies:
            try:
                wm.canvas.itemconfig(wm.dies[rc], width=3)
            except Exception:
                pass
        row, col = rc
        matches = [r for r in self.controller.results_data
                  if r.get("row") == row and r.get("col") == col]
        die_id = (self._exec2_overlay_die_ids.get(rc, "")
                 or wm.die_ids.get(rc, ""))
        if not die_id:
            # The recorded per-die name, NOT die_id - die_id is the whole shot
            # ("B26/B27/NA/B29/B30"), so falling back to it labelled an empty
            # corner with every device in the touchdown.
            die_id = next((r.get("die") for r in matches if r.get("die")), "")
        die_desc = f"{die_id} (R{row}C{col})" if die_id else f"R{row}C{col}"
        self._results_die_var.set(
            f"Die {die_desc} — {len(matches)} reading(s)" if matches
            else f"Die {die_desc} — no measurements recorded yet.")
        for iid in self._results_die_tree.get_children():
            self._results_die_tree.delete(iid)
        for r in matches:
            self._results_die_tree.insert("", "end", values=(
                r.get("step"), r.get("type"), r.get("value"), r.get("unit")))


    def _refresh_export_formats(self, select_name: str = None):
        if not self._ata_folder:
            self._export_formats = []
            self._export_format_cb.config(values=[])
            self.export_format_var.set("")
            self._update_default_format_label(None)
            return
        self._export_formats = xfmt.load_formats(self._ata_folder, system=self._system)
        names = [f["name"] for f in self._export_formats]
        self._export_format_cb.config(values=names)
        default_name = xfmt.get_default_format_name(self._ata_folder, system=self._system)
        # This project's own remembered export directory, if it has one -
        # falls back to whatever export_path_var already held (the fixed
        # system-wide default, or wherever the operator last pointed it)
        # rather than clearing the field when a project has never set one.
        default_export_path = xfmt.get_default_export_path(self._ata_folder, system=self._system)
        if default_export_path:
            self.export_path_var.set(default_export_path)
        if select_name in names:
            self.export_format_var.set(select_name)
        elif self.export_format_var.get() not in names:
            self.export_format_var.set(default_name if default_name in names
                                       else (names[0] if names else ""))
        self._update_default_format_label(default_name)

    def _update_default_format_label(self, default_name):
        var = getattr(self, "_export_default_lbl_var", None)
        if var is None:
            return
        var.set(f"Default: {default_name}" if default_name else "No default format set.")

    def _set_default_export_format(self):
        from tkinter import messagebox
        if not self._ata_folder:
            messagebox.showerror("No ATA Folder", "Load an ATA folder first.")
            return
        fmt = self.get_selected_export_format()
        if not fmt:
            messagebox.showerror("No Format Selected",
                                 "Pick a format from the Export Format dropdown first.")
            return
        xfmt.set_default_format_name(self._ata_folder, fmt["name"], system=self._system)
        # Format and export directory are set as default together - the
        # two always travel together for a given project (a project's data
        # goes to its own place, in its own shape), so one button covers
        # both rather than needing two separate "set default" actions.
        xfmt.set_default_export_path(self._ata_folder, self.export_path_var.get(),
                                     system=self._system)
        self._update_default_format_label(fmt["name"])
        self.controller.log(f"[RESULTS] '{fmt['name']}' and export path "
                            f"'{self.export_path_var.get()}' set as default for this project.")

    def _delete_export_format(self):
        from tkinter import messagebox
        fmt = self.get_selected_export_format()
        if not fmt:
            messagebox.showerror("No Format Selected",
                                 "Pick a format from the Export Format dropdown first.")
            return
        if not messagebox.askyesno(
            "Delete Export Format",
            f"Delete export format '{fmt['name']}'? This cannot be undone."
        ):
            return
        xfmt.delete_format(self._ata_folder, fmt["name"], system=self._system)
        self.controller.log(f"[RESULTS] Deleted export format '{fmt['name']}'.")
        self._refresh_export_formats()

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
        append_date_var = tk.BooleanVar(value=(existing_fmt or {}).get("append_date", False))
        ttk.Checkbutton(type_row, text="📅 Append date to filename (_YYYYMMDD)",
                       variable=append_date_var).pack(side="left", padx=(20, 0))

        only_pma_var = tk.BooleanVar(value=(existing_fmt or {}).get("requires_die_id", True))
        only_pma_chk = ttk.Checkbutton(
            frm, text="Only include readings that have a die ID",
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
        # Not readonly: a "lookup" table's own column headers (e.g.
        # Cenfire's DIE_ID/ABS_ROW/COLUMN_RETICLE - see the "Lookup Table"
        # row below) are project-specific and cannot all be listed here,
        # so a source name can be typed directly as well as picked from
        # the documented list.
        source_cb = ttk.Combobox(add_row, textvariable=source_var, width=14)
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

        add_row3 = ttk.Frame(frm)
        add_row3.grid(row=12, column=0, columnspan=4, sticky="ew", pady=(4, 0))
        ttk.Label(add_row3, text="Or template (combine fields, "
                                 "e.g. {intra_col}-{intra_row}-{shot_col}-{shot_row}):"
                 ).pack(side="left")
        template_var = tk.StringVar()
        ttk.Entry(add_row3, textvariable=template_var, width=44).pack(
            side="left", padx=(4, 0))

        lookup_lf = ttk.LabelFrame(
            frm, text="Lookup Table (optional) — a project's own per-die "
                     "reference CSV, in the ATA folder, keyed by this app's "
                     "real (row, col)")
        lookup_lf.grid(row=13, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        _lu = (existing_fmt or {}).get("lookup") or {}
        lu_file_var = tk.StringVar(value=_lu.get("file", ""))
        lu_row_col_var = tk.StringVar(value=_lu.get("lookup_row_col", ""))
        lu_col_col_var = tk.StringVar(value=_lu.get("lookup_col_col", ""))
        lu_our_row_var = tk.StringVar(value=_lu.get("our_row_field", "abs_row"))
        lu_our_col_var = tk.StringVar(value=_lu.get("our_col_field", "abs_col"))
        lu_row1 = ttk.Frame(lookup_lf)
        lu_row1.pack(fill="x", padx=6, pady=(4, 2))
        ttk.Label(lu_row1, text="CSV filename:").pack(side="left")
        ttk.Entry(lu_row1, textvariable=lu_file_var, width=28).pack(
            side="left", padx=(2, 12))
        ttk.Label(lu_row1, text="Its row/col columns:").pack(side="left")
        ttk.Entry(lu_row1, textvariable=lu_row_col_var, width=14).pack(
            side="left", padx=(2, 4))
        ttk.Entry(lu_row1, textvariable=lu_col_col_var, width=14).pack(
            side="left", padx=(2, 0))
        lu_row2 = ttk.Frame(lookup_lf)
        lu_row2.pack(fill="x", padx=6, pady=(0, 4))
        ttk.Label(lu_row2, text="Matched against this format's own:").pack(side="left")
        ttk.Entry(lu_row2, textvariable=lu_our_row_var, width=14).pack(
            side="left", padx=(2, 4))
        ttk.Entry(lu_row2, textvariable=lu_our_col_var, width=14).pack(
            side="left", padx=(2, 0))
        ttk.Label(lookup_lf, text="Leave CSV filename blank for no lookup table. "
                                  "A column can then use any of that CSV's own "
                                  "headers as its Source above.",
                 foreground="#6b7280", font=("Segoe UI", 8), wraplength=520,
                 justify="left").pack(anchor="w", padx=6, pady=(0, 4))

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
            # A template's own braces are the marker - no prefix character
            # needed, since "={...}" would otherwise read as a literal
            # constant string containing braces instead.
            if "{" in txt and "}" in txt:
                return {"template": txt}
            return {}

        def add_col():
            field = field_var.get().strip()
            source = source_var.get().strip()
            constant = constant_var.get().strip()
            mult = multiply_var.get().strip()
            template = template_var.get().strip()
            if not field or not (source or constant or template):
                return
            transform_txt = (template if template else
                            (f"={constant}" if constant else
                             (f"×{mult}" if mult else "")))
            cols_tree.insert("", "end", values=(
                field, source, "yes" if quote_var.get() else "no", transform_txt))
            field_var.set("")
            multiply_var.set("")
            constant_var.set("")
            template_var.set("")

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
            # Not just the documented list - a "lookup" table's own column
            # (see the Source combobox note above) is a perfectly valid
            # source that would otherwise silently vanish on re-edit.
            source_var.set(src)
            quote_var.set(q == "yes")
            parsed = _parse_transform(tr)
            multiply_var.set(str(parsed["multiply"]) if "multiply" in parsed else "")
            constant_var.set(parsed.get("constant", ""))
            template_var.set(parsed.get("template", ""))
            cols_tree.delete(iid)
        cols_tree.bind("<Double-Button-1>", _edit_selected)

        if existing_fmt:
            for c in existing_fmt.get("columns", []):
                tr = ""
                if c.get("constant") not in (None, ""):
                    tr = f"={c['constant']}"
                elif c.get("template"):
                    tr = c["template"]
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
                  "requires_die_id": only_pma_var.get(), "append_date": append_date_var.get(),
                  "columns": columns}
            lu_file = lu_file_var.get().strip()
            if lu_file:
                fmt["lookup"] = {
                    "file": lu_file,
                    "lookup_row_col": lu_row_col_var.get().strip() or "row",
                    "lookup_col_col": lu_col_col_var.get().strip() or "col",
                    "our_row_field": lu_our_row_var.get().strip() or "abs_row",
                    "our_col_field": lu_our_col_var.get().strip() or "abs_col",
                }
            xfmt.add_format(self._ata_folder, fmt, system=self._system)
            self._refresh_export_formats(select_name=name)
            self.controller.log(f"[RESULTS] Saved export format '{name}' ({table}, "
                                f"{type_var.get()}) to ATA folder.")
            dlg.destroy()

        btns = ttk.Frame(frm)
        btns.grid(row=14, column=0, columnspan=4, sticky="ew", pady=(10, 0))
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
