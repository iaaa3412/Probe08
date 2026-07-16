import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import csv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from instrument_panel import MainLayout
from probe_routing_panel import scrollable_routing
from instruments.accretech_uf200r import AccretechUF200R
from instruments.dmm import Keysight34461A
from instruments.smu import Keithley2636B
from instruments.switch import Keithley707B
from instruments.wave_gen import Keysight33512B
import export_formats as xfmt


class AtomicaDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Accretech Tester")
        self.geometry("1400x800")
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.simulation_running = False
        self.test_queue = []
        self.results_data = []
        self.total_dies = 0
        self.dies_tested = 0
        self.dies_passed = 0
        self.dies_failed = 0
        self.drivers = {}
        self._sys_ready_prev = None
        self._prober_ready = None
        self._prober_stb = None
        self._build_brand_header()
        self.create_toolbar()
        self._main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self._main_pane.grid(row=2, column=0, sticky="nsew")
        self.instrument_panel = MainLayout(parent=self._main_pane, controller=self)
        self._main_pane.add(self.instrument_panel, weight=1)
        self.ui = self.instrument_panel
        self._build_bottom_routing()
        self.after(500, self.init_hardware)
        self.update_statistics_visuals()
        self.check_system_ready()
        self.after(2000, self._system_ready_loop)
        self.after(1500, self._poll_prober_ready)

    def _system_ready_loop(self):
        self.check_system_ready()
        self.after(2000, self._system_ready_loop)

    def _poll_prober_ready(self):
        prober = self.drivers.get("prober")
        if not (prober and prober.inst) or self._any_run_in_progress():
            self.after(3000, self._poll_prober_ready)
            return

        def _run():
            try:
                stb, _desc = prober.read_stb_decoded()
                if stb == 76 and prober.confirm_and_clear_alarm():
                    self.log("[SYSTEM] Alarm detected while idle : "
                            "buzzer auto-cleared (es sent).")
            except Exception:
                stb = None
            self.after(0, lambda: self._set_prober_ready(stb))

        import threading
        threading.Thread(target=_run, daemon=True).start()
        self.after(3000, self._poll_prober_ready)

    def _any_run_in_progress(self) -> bool:
        ui = self.ui
        if getattr(ui, "_exec2_running", False):
            return True
        cassette = getattr(ui, "cassette_panel", None)
        if cassette is not None and getattr(cassette, "_running", False):
            return True
        accr = getattr(ui, "accr_wafer", None)
        if accr is not None and getattr(accr, "_running", False):
            return True
        nanoz = getattr(ui, "nanoz_panel", None)
        if nanoz is not None and getattr(nanoz, "_running", False):
            return True
        return False

    def _set_prober_ready(self, stb):
        self._prober_stb = stb
        self._prober_ready = (stb == 65) if stb is not None else None
        self.check_system_ready()

    def _build_brand_header(self):
        hdr = tk.Frame(self, bg="#374558", height=48)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        logo_path = os.path.join(os.path.dirname(__file__), "logo2.jpg")
        if os.path.exists(logo_path):
            try:
                from PIL import Image, ImageTk
                pil_img = Image.open(logo_path)
                target_h = 36
                scale = target_h / pil_img.height
                pil_img = pil_img.resize((max(1, int(pil_img.width * scale)), target_h))
                img = ImageTk.PhotoImage(pil_img)
                lbl_img = tk.Label(hdr, image=img, bg="#0E0E0F")
                lbl_img.image = img
                lbl_img.pack(side="left", padx=(10, 6), pady=4)
            except Exception:
                pass
        tk.Label(hdr, text="Test",
                 bg="#374558", fg="white",
                 font=("Arial", 13, "bold")).pack(side="left", padx=4)
        tk.Label(hdr, text="Probe08 Automation",
                 bg="#374558", fg="#f0a020",
                 font=("Arial", 13)).pack(side="left", padx=4)

    def _build_bottom_routing(self):
        lf = ttk.LabelFrame(self._main_pane, text="Switch Routing")
        self._bottom_routing_frame = lf
        self._routing_visible = True
        self._main_pane.add(lf, weight=0)
        holder, self.bottom_routing = scrollable_routing(lf, self)
        holder.pack(fill="both", expand=True)

    def cmd_toggle_routing(self):
        if self._routing_visible:
            self._main_pane.forget(self._bottom_routing_frame)
            self._routing_toggle_btn.config(text="▸ Show Switch")
        else:
            self._main_pane.add(self._bottom_routing_frame, weight=0)
            self._routing_toggle_btn.config(text="▾ Hide Switch")
        self._routing_visible = not self._routing_visible

    def cmd_fit_windows(self):
        self.update_idletasks()
        self._fit_all_panes(self)
        self.log("[UI] Fit Windows: resized all panes to the current window size.")

    def _fit_all_panes(self, widget):
        for child in widget.winfo_children():
            if isinstance(child, ttk.PanedWindow):
                self._fit_one_pane(child)
                child.update_idletasks()
            self._fit_all_panes(child)

    @staticmethod
    def _fit_one_pane(pane, min_px=40):
        panes = pane.panes()
        if len(panes) < 2:
            return
        horizontal = str(pane.cget("orient")) == "horizontal"
        total = pane.winfo_width() if horizontal else pane.winfo_height()
        if total < min_px * len(panes):
            return
        reqs = []
        for p in panes:
            w = pane.nametowidget(p)
            reqs.append(max(w.winfo_reqwidth() if horizontal else w.winfo_reqheight(), 1))
        remainder = total - min_px * len(panes)
        req_sum = sum(reqs)
        sizes = [min_px + int(remainder * r / req_sum) for r in reqs]
        sizes[-1] += total - sum(sizes)
        pos = 0
        for i in range(len(panes) - 1):
            pos += sizes[i]
            try:
                pane.sashpos(i, pos)
            except tk.TclError:
                pass

    def log(self, message):
        txt = getattr(getattr(self, "ui", None), "log_text", None)
        if txt is None:
            print(message)
            return
        txt.configure(state="normal")
        txt.insert(tk.END, message + "\n")
        txt.see(tk.END)
        txt.configure(state="disabled")

    def init_hardware(self):
        self.log("[SYSTEM] Pinging hardware connections...")

        for lbl in self.ui.status_labels.values():
            lbl.config(foreground="orange")

        self.update_idletasks()

        connections = [
            ("UF200R Prober",    "prober",   AccretechUF200R()),
            ("SMU (2636B)",      "smu",      Keithley2636B()),
            ("DMM (34461A)",     "dmm",      Keysight34461A()),
            ("SW_MATRIX",        "switch",   Keithley707B()),
            ("Wave Gen (33512B)","wave_gen", Keysight33512B()),
        ]

        for name, key, driver in connections:
            try:
                if name == "UF200R Prober":
                    response = driver.get_prober_id()
                else:
                    response = driver.query("*IDN?")
                if response:
                    self.drivers[key] = driver
                    self.ui.status_labels[name].config(text=f"✅ {name}", foreground="green")
                    self.log(f"[SYSTEM] Connected: {name}")
                else:
                    raise Exception("No response")
            except Exception as e:
                self.ui.status_labels[name].config(text=f"❌ {name}", foreground="red")
                self.log(f"[ERROR] {name}: {e}")

        self.check_system_ready()

    def check_system_ready(self):
        missing = []
        exec2_wm = getattr(self.ui, "_exec2_wafer_map", None)
        if not (exec2_wm and exec2_wm._last_dies):
            missing.append("Accretech wafer map")
        pin_wiring = getattr(self.ui, "pin_wiring", None)
        if not (pin_wiring and pin_wiring.get_active_card() and pin_wiring.get_wiring()):
            missing.append("probe card pinout")
        if not getattr(self.ui, "_exec2_steps", None):
            missing.append("measurement recipe")
        required_instruments = ("prober", "smu", "dmm", "switch", "wave_gen")
        if not all(k in self.drivers for k in required_instruments):
            missing.append("instruments")

        ready = not missing
        if ready:
            self.ui.status_label.config(text="SYSTEM READY", foreground="green")
        else:
            self.ui.status_label.config(text=f"PENDING: {', '.join(missing)}", foreground="red")

        if ready != self._sys_ready_prev:
            if ready:
                self.ui.exec_panel.log("[SYSTEM] All criteria met. System is READY for a run.")
            elif self._sys_ready_prev is not None:
                self.ui.exec_panel.log(f"[SYSTEM] No longer ready — missing: {', '.join(missing)}")
            self._sys_ready_prev = ready

        self._update_prober_status_label()

    def _update_prober_status_label(self):
        lbl = getattr(self.ui, "prober_status_label", None)
        if lbl is None:
            return
        if "prober" not in self.drivers:
            text = "Prober: not connected"
        elif self._prober_ready is True:
            text = f"Prober: ready to probe (STB={self._prober_stb})"
        elif self._prober_ready is False:
            text = f"Prober: not ready (STB={self._prober_stb})"
        else:
            text = "Prober: status unknown (waiting on STB read)"
        lbl.config(text=text, foreground="orange")

    def create_toolbar(self):
        toolbar = ttk.Frame(self, relief="raised", padding=2)
        toolbar.grid(row=1, column=0, sticky="ew")
        style = ttk.Style()
        style.configure("Abort.TButton", foreground="red", font=("Arial", 9, "bold"))
        ttk.Button(toolbar, text="⏹ Abort", style="Abort.TButton", command=self.cmd_abort).pack(side="left", padx=6, pady=2)

        ttk.Label(toolbar, text="ATA Folder:").pack(side="left", padx=(6, 2), pady=2)
        self._ata_picker_var = tk.StringVar()
        self._ata_picker = ttk.Combobox(
            toolbar, textvariable=self._ata_picker_var, state="readonly",
            width=24, postcommand=self._refresh_ata_picker)
        self._ata_picker.pack(side="left", padx=(0, 4), pady=2)
        self._ata_picker.bind("<<ComboboxSelected>>",
                              lambda _e: self._on_ata_picker_selected())

        ttk.Button(toolbar, text="↻ Refresh", command=self.cmd_refresh_ata).pack(side="left", padx=2, pady=2)
        self._ata_lbl = ttk.Label(toolbar, text="No ATA loaded", foreground="gray",
                                  font=("Segoe UI", 9))
        self._ata_lbl.pack(side="left", padx=(2, 8), pady=2)
        ttk.Button(toolbar, text="🔕 Buzzer Clear", command=self.cmd_buzzer_clear).pack(side="left", padx=4, pady=2)
        self._routing_toggle_btn = ttk.Button(
            toolbar, text="▾ Hide Routing", command=self.cmd_toggle_routing)
        self._routing_toggle_btn.pack(side="right", padx=6, pady=2)
        ttk.Button(toolbar, text="⛶ Fit Windows", command=self.cmd_fit_windows).pack(
            side="right", padx=2, pady=2)
        self.after(200, self._refresh_ata_picker)

    def _find_ata_folders(self):
        working_dir = self.ui.working_dir_var.get() if hasattr(self, "ui") else ""
        if not working_dir or not os.path.isdir(working_dir):
            return []
        found = []
        try:
            for name in os.listdir(working_dir):
                full = os.path.join(working_dir, name)
                if os.path.isdir(full) and name.lower().endswith("ata"):
                    found.append((os.path.getmtime(full), name))
        except OSError:
            return []
        found.sort(key=lambda t: t[0], reverse=True)
        return [name for _mtime, name in found]

    def _refresh_ata_picker(self):
        self._ata_picker.configure(values=self._find_ata_folders())

    def _on_ata_picker_selected(self):
        name = self._ata_picker_var.get()
        if not name:
            return
        folder = os.path.join(self.ui.working_dir_var.get(), name)
        self._do_load_ata_folder(folder)

    def update_statistics_visuals(self):
        untested = self.total_dies - self.dies_tested
        self.ui.lbl_stats_text.config(text=f"Pass: {self.dies_passed}  |  Fail: {self.dies_failed}\nUntested: {untested}")
        self.ui.lbl_progress.config(text=f"Progress: {self.dies_tested} / {self.total_dies} tested")
        self.ui.lbl_results_large.config(text=f"Total Passed: {self.dies_passed}     |     Total Failed: {self.dies_failed}     |     Untested: {untested}")
        self.ui.draw_donut(self.ui.sidebar_canvas, 120, self.dies_passed, self.dies_failed, untested)
        self.ui.draw_donut(self.ui.results_canvas, 300, self.dies_passed, self.dies_failed, untested)

    def on_exec_stats_change(self, tested, passed, failed, total):
        self.dies_tested  = tested
        self.dies_passed  = passed
        self.dies_failed  = failed
        self.total_dies   = total
        self.update_statistics_visuals()

    def _do_load_ata_folder(self, folder):
        n_dies = self.ui.load_ata_folder(folder)
        self.total_dies = n_dies
        self.dies_tested = self.dies_passed = self.dies_failed = 0
        self.ui.clear_results()
        self.update_statistics_visuals()
        folder_name = os.path.basename(folder)
        self._ata_lbl.config(text=f"ATA: {folder_name}  ({n_dies} dies)",
                             foreground="#1d4ed8")
        self.ui.exec_panel.log(f"[SYSTEM] ATA folder '{folder_name}' loaded — {n_dies} dies found.")
        self.ui.exec_panel.set_wafer_map(self.ui.wafer_map, wafer_id=folder_name)
        self.ui.wafer_id_var.set(folder_name)
        self.check_system_ready()

    def cmd_import_map(self):
        initial = self.ui.working_dir_var.get() if hasattr(self, "ui") else None
        folder = filedialog.askdirectory(
            title="Select ATA Output Folder",
            initialdir=initial if initial and os.path.isdir(initial) else None)
        if not folder:
            return
        self._do_load_ata_folder(folder)

    def cmd_refresh_ata(self):
        folder = self.ui._ata_folder
        if not folder:
            self.log("[SYSTEM] No ATA folder loaded — pick one from the "
                     "toolbar's ATA Folder dropdown, or use 📁 Load ATA "
                     "Folder on the ATA Folder tab.")
            return
        if not os.path.isdir(folder):
            self.log(f"[SYSTEM] ATA folder no longer exists: {folder}")
            return
        self.log(f"[SYSTEM] Refreshing from ATA folder: {folder}")
        self._do_load_ata_folder(folder)

    def cmd_load_pads(self):
        folder = self.ui._ata_folder or filedialog.askdirectory(title="Select ATA Output Folder")
        if not folder:
            return
        n_pads = self.ui.load_pad_layout(folder)
        self.ui.exec_panel.load_recipe()
        self.ui.exec_panel.lbl_route.config(text="P1 (VDD)  -> SMU_HI\nP2 (GND)  -> SMU_LO\nP6 (OUT)  -> DMM_HI")
        folder_name = os.path.basename(folder)
        self.ui.exec_panel.log(f"[SYSTEM] Pad layout loaded from '{folder_name}' — {n_pads} pads.")

    def cmd_load_alignment(self):
        folder = self.ui._ata_folder or filedialog.askdirectory(title="Select ATA Output Folder")
        if not folder:
            return
        self.ui.load_alignment_marks(folder)
        folder_name = os.path.basename(folder)
        self.ui.exec_panel.log(f"[SYSTEM] Alignment marks loaded from '{folder_name}'.")

    def cmd_browse_export(self):
        selected_dir = filedialog.askdirectory(initialdir=self.ui.export_path_var.get(), title="Select Export Directory")
        if selected_dir:
            self.ui.export_path_var.set(selected_dir)

    def cmd_browse_working_dir(self):
        selected_dir = filedialog.askdirectory(
            initialdir=self.ui.working_dir_var.get(), title="Select Working Directory")
        if selected_dir:
            self.ui.working_dir_var.set(selected_dir)

    def cmd_save_csv(self):
        export_dir = self.ui.export_path_var.get()
        current_lot = self.ui.lot_id.get()
        if not os.path.exists(export_dir):
            self.ui.exec_panel.log("[ERROR] The selected export directory does not exist.")
            return
        if not current_lot:
            self.ui.exec_panel.log("[ERROR] Please enter a valid Lot ID.")
            return
        if not self.results_data:
            self.ui.exec_panel.log("[ERROR] No measurement results yet — nothing to save.")
            return
        wafer_id = self.ui.wafer_id_var.get().strip()
        name_parts = [current_lot] + ([wafer_id] if wafer_id else []) + ["results"]
        filepath = os.path.join(export_dir, "_".join(name_parts) + ".csv")
        fieldnames = ["timestamp", "recipe", "die", "step", "type", "mode", "value", "unit"]
        try:
            with open(filepath, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(self.results_data)

            self.ui.exec_panel.log(
                f"[SYSTEM] Success! {len(self.results_data)} result(s) saved to -> {filepath}")
        except Exception as e:
            self.ui.exec_panel.log(f"[ERROR] Failed to save CSV file: {e}")

    def cmd_export_sql(self):
        export_dir = self.ui.export_path_var.get()
        current_lot = self.ui.lot_id.get()
        if not os.path.exists(export_dir):
            self.ui.exec_panel.log("[ERROR] The selected export directory does not exist.")
            return
        if not current_lot:
            self.ui.exec_panel.log("[ERROR] Please enter a valid Lot ID.")
            return
        fmt = self.ui.get_selected_export_format()
        if not fmt:
            self.ui.exec_panel.log("[ERROR] No export format selected — pick one, or "
                                   "➕ New Format… to define one first.")
            return
        wafer_id = self.ui.wafer_id_var.get().strip()
        fmt_type = fmt.get("type", "sql")
        if not xfmt.has_data_for_format(fmt, self.results_data):
            if fmt_type == "csv":
                reason = "at least one current or resistance reading from a die touchdown"
            else:
                reason = ("readings recorded during a ▶ Test PMA run (they carry the "
                         "shot's device-ID string; Full Die/Test Die readings don't)"
                         if fmt.get("requires_die_id", True) else "measurement results")
            self.ui.exec_panel.log(
                f"[ERROR] No matching results yet for '{fmt['name']}' — this format needs "
                f"{reason}.")
            return
        ext = "csv" if fmt_type == "csv" else "sql"
        name_parts = [current_lot] + ([wafer_id] if wafer_id else []) + [
            fmt["table"].lower() or "export"]
        filepath = os.path.join(export_dir, "_".join(name_parts) + f".{ext}")

        try:
            if fmt_type == "csv":
                rows = xfmt.build_csv_rows(fmt, self.results_data, current_lot, wafer_id)
                fieldnames = [c["field"] for c in fmt["columns"]]
                with open(filepath, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                self.ui.exec_panel.log(
                    f"[SYSTEM] Success! {len(rows)} '{fmt['name']}' row(s) saved to -> {filepath}")
            else:
                statements = xfmt.build_insert_statements(fmt, self.results_data, current_lot, wafer_id)
                with open(filepath, "w", newline="") as f:
                    f.write("\n".join(statements) + "\n")
                self.ui.exec_panel.log(
                    f"[SYSTEM] Success! {len(statements)} '{fmt['name']}' row(s) saved to -> {filepath}")
        except Exception as e:
            self.ui.exec_panel.log(f"[ERROR] Failed to save {ext.upper()} file: {e}")

    def cmd_align(self):
        self.ui.align_panel.lock_alignment()
        self.ui.exec_panel.log("[ALIGN] Alignment locked by operator.")

    def cmd_buzzer_clear(self):
        drv = self.drivers.get("prober")
        if not (drv and drv.inst):
            self.log("[BUZZER] Prober not connected.")
            return
        import threading
        def _run():
            try:
                self.log("[BUZZER] >> E + es  (read error code, clear alarm)")
                code = drv.buzzer_clear()
                self.log(f"[BUZZER] Cleared — error code: {code or '(none pending)'}")
            except Exception as e:
                self.log(f"[BUZZER] Error: {e}")
        threading.Thread(target=_run, daemon=True).start()

    def cmd_abort(self):
        self.ui.exec_panel.abort()
        drv = self.drivers.get("prober")
        if drv and drv.inst:
            import threading
            def _send_k():
                try:
                    drv.write("K")
                    self.log("[ABORT] K sent to prober (emergency stop)")
                except Exception as e:
                    self.log(f"[ABORT] K error: {e}")
                try:
                    drv.send_es()
                    self.log("[ABORT] es sent (buzzer clear)")
                except Exception as e:
                    self.log(f"[ABORT] es error: {e}")
            threading.Thread(target=_send_k, daemon=True).start()

if __name__ == "__main__":
    app = AtomicaDashboard()
    app.mainloop()