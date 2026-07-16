import tkinter as tk
from tkinter import ttk
import random
import time
import math


class ATADemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATA - Atomica Test Application Demo")
        self.root.geometry("1450x850")
        self.root.minsize(1200, 700)

        self.running = False
        self.in_contact = False
        self.aborted = False

        self.rows = 18
        self.cols = 24
        self.current_index = 0
        self.dies = []
        self.die_rects = {}

        self.wafer_id = "WAFER_NAUTILUS_001"
        self.recipe = "NAUTILUS_EKIV_SENSOR_TEST"
        self.current_die = None

        self.alignment = {
            "offset_x_um": 0.0,
            "offset_y_um": 0.0,
            "theta_deg": 0.0,
            "confidence": 0.0,
        }

        self.stats = {
            "tested": 0,
            "pass": 0,
            "fail": 0,
            "skip": 0,
            "untested": 0,
        }

        self.nanoz_connected = True
        self.nanoz_cycle = 3
        self.nanoz_frames = 0
        self.nanoz_checksum_errors = 0

        self.create_fake_wafer()
        self.build_ui()
        self.bind_keys()
        self.update_current_die()
        self.refresh_all()

        self.log("System ready.")
        self.log("Keyboard demo controls: Space=start/pause, N=next die, T=touchdown, R=run test, A=align, E=NanoZ frame, Esc=abort.")

    def create_fake_wafer(self):
        cx = (self.cols - 1) / 2
        cy = (self.rows - 1) / 2
        rx = self.cols / 2.05
        ry = self.rows / 2.05

        for r in range(self.rows):
            for c in range(self.cols):
                nx = (c - cx) / rx
                ny = (r - cy) / ry

                if nx * nx + ny * ny <= 1.0:
                    die_id = f"R{r+1:02d}C{c+1:02d}"

                    status = "UNTESTED"
                    if random.random() < 0.04:
                        status = "SKIP"

                    self.dies.append({
                        "die_id": die_id,
                        "row": r + 1,
                        "col": c + 1,
                        "x_mm": round((c - cx) * 2.5, 3),
                        "y_mm": round((cy - r) * 2.5, 3),
                        "status": status,
                        "leakage_na": None,
                        "sensor_current_ma": None,
                        "heater_current_ma": None,
                        "bin": status,
                    })

        self.stats["skip"] = sum(1 for d in self.dies if d["status"] == "SKIP")
        self.stats["untested"] = len(self.dies) - self.stats["skip"]

    def build_ui(self):
        self.root.configure(bg="#f4f6f8")

        self.build_top_bar()
        self.build_main_layout()
        self.build_status_bar()

    def build_top_bar(self):
        top = tk.Frame(self.root, bg="#ffffff", height=58, bd=1, relief="solid")
        top.pack(side="top", fill="x")

        title = tk.Label(
            top,
            text="ATA - Atomica Test Application Demo",
            bg="#ffffff",
            fg="#1f2937",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(side="left", padx=18)

        buttons = [
            ("A  Align", self.run_alignment),
            ("T  Touchdown", self.toggle_touchdown),
            ("R  Run Test", self.run_test),
            ("N  Next Die", self.next_die),
            ("E  NanoZ Frame", self.simulate_nanoz_frame),
            ("Esc  Abort", self.abort),
        ]

        for text, cmd in buttons:
            b = ttk.Button(top, text=text, command=cmd)
            b.pack(side="left", padx=5, pady=10)

        self.run_button = ttk.Button(top, text="Space  Start / Pause", command=self.toggle_running)
        self.run_button.pack(side="right", padx=18, pady=10)

    def build_main_layout(self):
        main = tk.Frame(self.root, bg="#f4f6f8")
        main.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.left_panel = tk.Frame(main, bg="#ffffff", bd=1, relief="solid")
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.center_panel = tk.Frame(main, bg="#ffffff", bd=1, relief="solid")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=8)

        self.right_panel = tk.Frame(main, bg="#ffffff", bd=1, relief="solid", width=380)
        self.right_panel.pack(side="right", fill="both", padx=(8, 0))
        self.right_panel.pack_propagate(False)

        self.build_wafer_map_panel()
        self.build_execution_panel()
        self.build_right_panel()

    def build_wafer_map_panel(self):
        header = tk.Frame(self.left_panel, bg="#ffffff")
        header.pack(fill="x", padx=12, pady=(10, 0))

        tk.Label(
            header,
            text="Wafer Map",
            bg="#ffffff",
            fg="#111827",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        self.wafer_info = tk.Label(
            header,
            text="",
            bg="#ffffff",
            fg="#4b5563",
            font=("Segoe UI", 9)
        )
        self.wafer_info.pack(side="right")

        self.canvas = tk.Canvas(self.left_panel, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=12)

        legend = tk.Frame(self.left_panel, bg="#ffffff")
        legend.pack(fill="x", padx=12, pady=(0, 12))

        for label, color in [
            ("Pass", "#35a853"),
            ("Fail", "#e53935"),
            ("Skip", "#fbbc04"),
            ("Untested", "#e5e7eb"),
            ("Current", "#2563eb"),
            ("Contact", "#7c3aed"),
        ]:
            item = tk.Frame(legend, bg="#ffffff")
            item.pack(side="left", padx=8)
            tk.Label(item, text="■", fg=color, bg="#ffffff", font=("Segoe UI", 11, "bold")).pack(side="left")
            tk.Label(item, text=label, bg="#ffffff", fg="#374151", font=("Segoe UI", 9)).pack(side="left")

        self.canvas.bind("<Configure>", lambda e: self.draw_wafer_map())

    def build_execution_panel(self):
        top = tk.Frame(self.center_panel, bg="#ffffff")
        top.pack(fill="x", padx=12, pady=(10, 0))

        tk.Label(
            top,
            text="Execution + Test Sequence",
            bg="#ffffff",
            fg="#111827",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        self.state_label = tk.Label(
            top,
            text="IDLE",
            bg="#ffffff",
            fg="#2563eb",
            font=("Segoe UI", 11, "bold")
        )
        self.state_label.pack(side="right")

        self.sequence = ttk.Treeview(
            self.center_panel,
            columns=("step", "description", "status"),
            show="headings",
            height=9
        )
        self.sequence.heading("step", text="Step")
        self.sequence.heading("description", text="Description")
        self.sequence.heading("status", text="Status")
        self.sequence.column("step", width=120, anchor="w")
        self.sequence.column("description", width=330, anchor="w")
        self.sequence.column("status", width=110, anchor="center")
        self.sequence.pack(fill="x", padx=12, pady=12)

        steps = [
            ("ALIGN_WAFER", "Find alignment marks and calculate transform", "Ready"),
            ("MOVE_TO_DIE", "Move UF200R stage to target die", "Ready"),
            ("TOUCHDOWN", "Lower probes onto pad set", "Ready"),
            ("CONTACT_CHECK", "Verify safe contact state", "Ready"),
            ("NANOZ_RUN", "Start NanoZ EK-IV cycle over USB", "Ready"),
            ("NANOZ_SAMPLE", "Collect sensor/heater data frames", "Ready"),
            ("BIN_DIE", "Evaluate results and assign bin", "Ready"),
            ("SEPARATE", "Lift probes before XY move", "Ready"),
        ]

        for step in steps:
            self.sequence.insert("", "end", values=step)

        log_header = tk.Frame(self.center_panel, bg="#ffffff")
        log_header.pack(fill="x", padx=12)

        tk.Label(
            log_header,
            text="Execution Log",
            bg="#ffffff",
            fg="#111827",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        ttk.Button(log_header, text="Clear", command=self.clear_log).pack(side="right")

        log_frame = tk.Frame(self.center_panel, bg="#ffffff")
        log_frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.log_box = tk.Text(
            log_frame,
            height=14,
            bg="#0f172a",
            fg="#dbeafe",
            insertbackground="#ffffff",
            font=("Consolas", 10),
            wrap="word"
        )
        self.log_box.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        sb.pack(side="right", fill="y")
        self.log_box.configure(yscrollcommand=sb.set)

    def build_right_panel(self):
        self.die_frame = self.make_card(self.right_panel, "Current Die")
        self.die_text = tk.Text(self.die_frame, height=9, bg="#ffffff", fg="#111827", font=("Consolas", 10), bd=0)
        self.die_text.pack(fill="x", padx=10, pady=8)

        self.nanoz_frame = self.make_card(self.right_panel, "NanoZ EK-IV USB DAQ")
        self.nanoz_text = tk.Text(self.nanoz_frame, height=11, bg="#ffffff", fg="#111827", font=("Consolas", 10), bd=0)
        self.nanoz_text.pack(fill="x", padx=10, pady=8)

        self.inst_frame = self.make_card(self.right_panel, "Instrument Status")
        self.inst_text = tk.Text(self.inst_frame, height=8, bg="#ffffff", fg="#111827", font=("Consolas", 10), bd=0)
        self.inst_text.pack(fill="x", padx=10, pady=8)

        self.stats_frame = self.make_card(self.right_panel, "Run Statistics")
        self.stats_text = tk.Text(self.stats_frame, height=9, bg="#ffffff", fg="#111827", font=("Consolas", 10), bd=0)
        self.stats_text.pack(fill="x", padx=10, pady=8)

    def make_card(self, parent, title):
        frame = tk.Frame(parent, bg="#ffffff", bd=1, relief="groove")
        frame.pack(fill="x", padx=10, pady=8)

        tk.Label(
            frame,
            text=title,
            bg="#f9fafb",
            fg="#111827",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padx=8,
            pady=5
        ).pack(fill="x")

        return frame

    def build_status_bar(self):
        self.status = tk.Frame(self.root, bg="#ffffff", height=34, bd=1, relief="solid")
        self.status.pack(side="bottom", fill="x")

        self.status_left = tk.Label(
            self.status,
            text="System Ready",
            bg="#ffffff",
            fg="#15803d",
            font=("Segoe UI", 10, "bold")
        )
        self.status_left.pack(side="left", padx=12)

        self.status_center = tk.Label(
            self.status,
            text="UF200R: Connected | GPIB: Online | NanoZ EK-IV: COM7 Connected",
            bg="#ffffff",
            fg="#374151",
            font=("Segoe UI", 10)
        )
        self.status_center.pack(side="left", padx=30)

        self.progress_label = tk.Label(
            self.status,
            text="",
            bg="#ffffff",
            fg="#374151",
            font=("Segoe UI", 10)
        )
        self.progress_label.pack(side="right", padx=12)

    def bind_keys(self):
        self.root.bind("<space>", lambda e: self.toggle_running())
        self.root.bind("n", lambda e: self.next_die())
        self.root.bind("N", lambda e: self.next_die())
        self.root.bind("t", lambda e: self.toggle_touchdown())
        self.root.bind("T", lambda e: self.toggle_touchdown())
        self.root.bind("r", lambda e: self.run_test())
        self.root.bind("R", lambda e: self.run_test())
        self.root.bind("a", lambda e: self.run_alignment())
        self.root.bind("A", lambda e: self.run_alignment())
        self.root.bind("e", lambda e: self.simulate_nanoz_frame())
        self.root.bind("E", lambda e: self.simulate_nanoz_frame())
        self.root.bind("f", lambda e: self.force_fail())
        self.root.bind("F", lambda e: self.force_fail())
        self.root.bind("p", lambda e: self.force_pass())
        self.root.bind("P", lambda e: self.force_pass())
        self.root.bind("<Escape>", lambda e: self.abort())

    def update_current_die(self):
        valid = [d for d in self.dies if d["status"] != "SKIP"]
        if not valid:
            self.current_die = None
            return

        self.current_index = max(0, min(self.current_index, len(valid) - 1))
        self.current_die = valid[self.current_index]

    def draw_wafer_map(self):
        self.canvas.delete("all")
        self.die_rects.clear()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w < 100 or h < 100:
            return

        margin = 35
        cell_w = (w - 2 * margin) / self.cols
        cell_h = (h - 2 * margin) / self.rows
        cell = min(cell_w, cell_h)

        grid_w = cell * self.cols
        grid_h = cell * self.rows
        x0 = (w - grid_w) / 2
        y0 = (h - grid_h) / 2

        radius = min(grid_w, grid_h) / 2 + cell * 0.8
        cx = w / 2
        cy = h / 2

        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline="#374151",
            width=2,
            fill="#f8fafc"
        )

        for d in self.dies:
            r = d["row"] - 1
            c = d["col"] - 1
            x1 = x0 + c * cell
            y1 = y0 + r * cell
            x2 = x1 + cell * 0.85
            y2 = y1 + cell * 0.85

            color = self.color_for_status(d["status"])

            outline = "#9ca3af"
            width = 1

            if self.current_die and d["die_id"] == self.current_die["die_id"]:
                outline = "#2563eb"
                width = 3
                color = "#dbeafe"

                if self.in_contact:
                    outline = "#7c3aed"
                    width = 4

            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=outline,
                width=width
            )
            self.die_rects[d["die_id"]] = rect

        if self.current_die:
            label = f"Current: {self.current_die['die_id']}"
            self.canvas.create_text(
                12,
                18,
                text=label,
                anchor="w",
                fill="#111827",
                font=("Segoe UI", 11, "bold")
            )

    def color_for_status(self, status):
        return {
            "PASS": "#35a853",
            "FAIL": "#e53935",
            "SKIP": "#fbbc04",
            "UNTESTED": "#e5e7eb",
            "CONTACT_FAIL": "#fb923c",
        }.get(status, "#e5e7eb")

    def refresh_all(self):
        self.refresh_text_panels()
        self.draw_wafer_map()
        self.refresh_status_bar()

    def refresh_text_panels(self):
        d = self.current_die

        self.die_text.config(state="normal")
        self.die_text.delete("1.0", "end")

        if d:
            contact = "YES" if self.in_contact else "NO"
            self.die_text.insert("end", f"Die ID:       {d['die_id']}\n")
            self.die_text.insert("end", f"Row / Col:    R{d['row']:02d} / C{d['col']:02d}\n")
            self.die_text.insert("end", f"Stage X:      {d['x_mm']: .3f} mm\n")
            self.die_text.insert("end", f"Stage Y:      {d['y_mm']: .3f} mm\n")
            self.die_text.insert("end", f"Status:       {d['status']}\n")
            self.die_text.insert("end", f"Contact:      {contact}\n")
            self.die_text.insert("end", f"Leakage:      {self.safe_value(d['leakage_na'], 'nA')}\n")
            self.die_text.insert("end", f"NanoZ I:      {self.safe_value(d['sensor_current_ma'], 'mA')}\n")
            self.die_text.insert("end", f"Heater I:     {self.safe_value(d['heater_current_ma'], 'mA')}\n")

        self.die_text.config(state="disabled")

        self.nanoz_text.config(state="normal")
        self.nanoz_text.delete("1.0", "end")
        self.nanoz_text.insert("end", f"Connection:   {'Connected' if self.nanoz_connected else 'Disconnected'}\n")
        self.nanoz_text.insert("end", "Port:         COM7 / FTDI USB Serial\n")
        self.nanoz_text.insert("end", "Identity:     Iam 5164\n")
        self.nanoz_text.insert("end", "Firmware:     NANOZ EK gen IV SW:V1.12.153\n")
        self.nanoz_text.insert("end", f"Cycle:        {self.nanoz_cycle}\n")
        self.nanoz_text.insert("end", f"Frames:       {self.nanoz_frames}\n")
        self.nanoz_text.insert("end", f"Checksum Err: {self.nanoz_checksum_errors}\n")
        self.nanoz_text.insert("end", "Sensor Mask:  0x0F\n")
        self.nanoz_text.insert("end", "Channels:     4 sensors + 2 heaters\n")
        self.nanoz_text.insert("end", "Command Set:  ver, whoami, run, pause, #env?\n")
        self.nanoz_text.config(state="disabled")

        self.inst_text.config(state="normal")
        self.inst_text.delete("1.0", "end")
        self.inst_text.insert("end", "UF200R Prober:      GPIB0::10  OK\n")
        self.inst_text.insert("end", "Keithley 2636B SMU: GPIB0::05  OK\n")
        self.inst_text.insert("end", "Keysight 34461A:    GPIB0::22  OK\n")
        self.inst_text.insert("end", "Keithley 707B:      GPIB0::15  OK\n")
        self.inst_text.insert("end", "Keysight 33500B:    GPIB0::18  OK\n")
        self.inst_text.insert("end", "NanoZ EK-IV:        COM7       OK\n")
        self.inst_text.config(state="disabled")

        total = len(self.dies)
        tested = self.stats["tested"]
        yield_pct = 0 if tested == 0 else 100 * self.stats["pass"] / tested

        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("end", f"Wafer ID:     {self.wafer_id}\n")
        self.stats_text.insert("end", f"Recipe:       {self.recipe}\n")
        self.stats_text.insert("end", f"Total Dies:   {total}\n")
        self.stats_text.insert("end", f"Tested:       {self.stats['tested']}\n")
        self.stats_text.insert("end", f"Pass:         {self.stats['pass']}\n")
        self.stats_text.insert("end", f"Fail:         {self.stats['fail']}\n")
        self.stats_text.insert("end", f"Skip:         {self.stats['skip']}\n")
        self.stats_text.insert("end", f"Yield:        {yield_pct:.1f}%\n")
        self.stats_text.insert("end", f"Alignment:    θ={self.alignment['theta_deg']:.4f}°\n")
        self.stats_text.config(state="disabled")

    def safe_value(self, value, units):
        if value is None:
            return "--"
        return f"{value:.4f} {units}"

    def refresh_status_bar(self):
        state = "RUNNING" if self.running else "IDLE"
        if self.aborted:
            state = "ABORTED"
        elif self.in_contact:
            state = "CONTACT"

        self.state_label.config(text=state)

        if self.aborted:
            self.status_left.config(text="Aborted", fg="#dc2626")
        elif self.running:
            self.status_left.config(text="Running", fg="#2563eb")
        elif self.in_contact:
            self.status_left.config(text="In Contact", fg="#7c3aed")
        else:
            self.status_left.config(text="System Ready", fg="#15803d")

        total = len([d for d in self.dies if d["status"] != "SKIP"])
        self.progress_label.config(
            text=f"{self.stats['tested']} / {total} tested"
        )

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"{timestamp}   {message}\n")
        self.log_box.see("end")

    def clear_log(self):
        self.log_box.delete("1.0", "end")

    def toggle_running(self):
        self.running = not self.running
        self.aborted = False

        if self.running:
            self.log("Run started.")
            self.auto_step()
        else:
            self.log("Run paused.")

        self.refresh_all()

    def auto_step(self):
        if not self.running or self.aborted:
            return

        if not self.current_die:
            self.log("No current die available.")
            self.running = False
            self.refresh_all()
            return

        if not self.in_contact:
            self.toggle_touchdown()
            self.root.after(900, self.auto_step)
            return

        self.run_test(auto=True)
        self.root.after(900, self.auto_next_after_test)

    def auto_next_after_test(self):
        if not self.running or self.aborted:
            return

        if self.in_contact:
            self.toggle_touchdown()

        self.next_die()

        if self.stats["tested"] >= len([d for d in self.dies if d["status"] != "SKIP"]):
            self.running = False
            self.log("Full wafer demo complete.")
            self.refresh_all()
            return

        self.root.after(700, self.auto_step)

    def run_alignment(self):
        self.alignment["offset_x_um"] = random.uniform(-3.0, 3.0)
        self.alignment["offset_y_um"] = random.uniform(-3.0, 3.0)
        self.alignment["theta_deg"] = random.uniform(-0.025, 0.025)
        self.alignment["confidence"] = random.uniform(98.2, 99.9)

        self.log(
            f"Alignment complete: "
            f"dX={self.alignment['offset_x_um']:.2f} µm, "
            f"dY={self.alignment['offset_y_um']:.2f} µm, "
            f"θ={self.alignment['theta_deg']:.4f}°, "
            f"confidence={self.alignment['confidence']:.2f}%."
        )
        self.refresh_all()

    def toggle_touchdown(self):
        if not self.current_die:
            return

        if self.in_contact:
            self.in_contact = False
            self.log(f"Probes separated from {self.current_die['die_id']}. XY motion enabled.")
        else:
            self.in_contact = True
            self.log(f"Touchdown on {self.current_die['die_id']}. XY motion locked.")

        self.refresh_all()

    def run_test(self, auto=False):
        if not self.current_die:
            return

        if not self.in_contact:
            self.log("Cannot run test: probes are not in contact. Press T to touchdown first.")
            return

        d = self.current_die

        self.log(f"Running test recipe {self.recipe} on {d['die_id']}.")

        leakage = abs(random.gauss(0.45, 0.25))
        sensor_current = abs(random.gauss(0.120, 0.018))
        heater_current = abs(random.gauss(4.8, 0.5))

        d["leakage_na"] = leakage
        d["sensor_current_ma"] = sensor_current
        d["heater_current_ma"] = heater_current

        self.simulate_nanoz_frame(log_header=False)

        passed = (
            leakage < 1.0 and
            0.060 <= sensor_current <= 0.180 and
            3.5 <= heater_current <= 6.5
        )

        if random.random() < 0.07:
            passed = False

        old_status = d["status"]
        d["status"] = "PASS" if passed else "FAIL"
        d["bin"] = d["status"]

        if old_status not in ("PASS", "FAIL", "CONTACT_FAIL"):
            self.stats["tested"] += 1
            self.stats["untested"] = max(0, self.stats["untested"] - 1)

        if passed:
            self.stats["pass"] += 1
            self.log(
                f"PASS {d['die_id']}: leakage={leakage:.3f} nA, "
                f"NanoZ current={sensor_current:.4f} mA, heater={heater_current:.3f} mA."
            )
        else:
            self.stats["fail"] += 1
            self.log(
                f"FAIL {d['die_id']}: leakage={leakage:.3f} nA, "
                f"NanoZ current={sensor_current:.4f} mA, heater={heater_current:.3f} mA."
            )

        self.refresh_all()

    def simulate_nanoz_frame(self, log_header=True):
        self.nanoz_frames += 1

        if random.random() < 0.015:
            self.nanoz_checksum_errors += 1
            self.log("NanoZ EK-IV checksum warning: frame discarded.")
        else:
            chip = random.choice([0, 1])
            currents = [abs(random.gauss(0.120, 0.018)) for _ in range(4)]
            if log_header:
                self.log(
                    f"NanoZ #spl! frame received: chip={chip}, "
                    f"mask=0x0F, I=[{currents[0]:.4f}, {currents[1]:.4f}, "
                    f"{currents[2]:.4f}, {currents[3]:.4f}] mA."
                )

        self.refresh_all()

    def next_die(self):
        if self.in_contact:
            self.log("Blocked: cannot move to next die while probes are in contact. Press T to separate first.")
            return

        valid = [d for d in self.dies if d["status"] != "SKIP"]

        if not valid:
            return

        start = self.current_index

        for i in range(1, len(valid) + 1):
            candidate_index = (start + i) % len(valid)
            candidate = valid[candidate_index]

            if candidate["status"] == "UNTESTED":
                self.current_index = candidate_index
                self.current_die = candidate
                self.log(f"Moved to die {candidate['die_id']} at X={candidate['x_mm']:.3f} mm, Y={candidate['y_mm']:.3f} mm.")
                self.refresh_all()
                return

        self.current_index = (self.current_index + 1) % len(valid)
        self.current_die = valid[self.current_index]
        self.log(f"No untested dies left. Moved to {self.current_die['die_id']}.")
        self.refresh_all()

    def force_fail(self):
        if not self.current_die:
            return
        old = self.current_die["status"]
        self.current_die["status"] = "FAIL"
        self.current_die["bin"] = "FAIL"

        if old not in ("PASS", "FAIL", "CONTACT_FAIL"):
            self.stats["tested"] += 1
            self.stats["fail"] += 1
        self.log(f"Manual bin override: {self.current_die['die_id']} -> FAIL.")
        self.refresh_all()

    def force_pass(self):
        if not self.current_die:
            return
        old = self.current_die["status"]
        self.current_die["status"] = "PASS"
        self.current_die["bin"] = "PASS"

        if old not in ("PASS", "FAIL", "CONTACT_FAIL"):
            self.stats["tested"] += 1
            self.stats["pass"] += 1
        self.log(f"Manual bin override: {self.current_die['die_id']} -> PASS.")
        self.refresh_all()

    def abort(self):
        self.running = False
        self.in_contact = False
        self.aborted = True
        self.log("ABORT pressed. Probes separated. Run stopped. System moved to safe state.")
        self.refresh_all()


if __name__ == "__main__":
    root = tk.Tk()
    app = ATADemoApp(root)
    root.mainloop()