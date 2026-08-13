import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, simpledialog, messagebox
import os
import csv
import sys
import datetime as dt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from instrument_panel import MainLayout
from probe_routing_panel import scrollable_routing
from instruments.accretech_uf200r import AccretechUF200R
from instruments.dmm import Keysight34461A
from instruments.smu import Keithley2636B
from instruments.switch import Keithley707B
from instruments.wave_gen import Keysight33512B
from instruments.electroglas_2001x import Electroglas2001X
from instruments.keithley2400 import Keithley2400
from instruments.hp3458a import HP3458A
from instruments.hp6634b import Agilent6634B
from instruments.hp_switchbox import HPSwitchbox
from instruments.hp_e1326b import HPE1326B
from instruments import eg_profiles
import export_formats as xfmt
import app_settings

ACCRETECH_INSTRUMENT_NAMES = ["UF200R Prober", "SMU (2636B)", "DMM (34461A)",
                              "SW_MATRIX", "Wave Gen (33512B)"]
# Every display name _EG_DRIVERS can produce, in the order eg_profiles.EG_KEYS
# connects them, so the sidebar reads top-to-bottom as the sweep progresses.
# A name missing from here has no status label, and the connect loop cannot
# report on it - keep the two in step.
ELECTROGLAS_INSTRUMENT_NAMES = ["Electroglas 2001X", "Keithley 2400", "HP 3458A",
                                "HP E1326B (VXI)", "HP Switchbox 1", "HP Switchbox 2",
                                "HP Switchbox 3", "Agilent 6634B"]

# Accretech is one machine for now. Electroglas benches come from
# instruments/eg_probers.yaml instead, because they genuinely differ.
ACCRETECH_BENCHES = ("probe08",)

ACCRETECH_REQUIRED_DRIVERS = ("prober", "smu", "dmm", "switch", "wave_gen")
# No "smu"/"power_supply" for the same reason - requiring them would hold the
# Electroglas tab at PENDING forever.
ELECTROGLAS_REQUIRED_DRIVERS = ("prober", "dmm", "relay1", "relay2", "relay3")


class AtomicaDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Electrical Prober")
        self.geometry("1400x800")
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.simulation_running = False
        self.test_queue = []
        self.active_system = "accretech"
        self._by_system = {
            "accretech":   {"drivers": {}, "results": [], "ui": None,
                            "total": 0, "tested": 0, "passed": 0, "failed": 0},
            "electroglas": {"drivers": {}, "results": [], "ui": None,
                            "total": 0, "tested": 0, "passed": 0, "failed": 0},
        }
        # False until the startup sweep has run, so a bench selected during
        # construction does not connect twice.
        self._startup_done = False
        # Which systems have had a connect sweep run at least once - a
        # system is only pinged when it is actually selected (at startup,
        # or the first time the operator switches to it), never both, so
        # switching to Accretech does not also probe an Electroglas rig
        # that may not even be powered on, and vice versa.
        self._connected_systems = set()
        self._sys_ready_prev = None
        self._prober_ready = None
        self._prober_stb = None
        self.working_dir_var = tk.StringVar(value="C:/automationproject")
        self._build_brand_header()
        self.create_toolbar()
        self._main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self._main_pane.grid(row=2, column=0, sticky="nsew")

        self.instrument_panel = MainLayout(
            parent=self._main_pane, controller=self,
            instrument_names=ACCRETECH_INSTRUMENT_NAMES,
            init_hardware_fn=self.init_hardware, system="accretech")
        self._by_system["accretech"]["ui"] = self.instrument_panel
        self._main_pane.add(self.instrument_panel, weight=1)

        self.instrument_panel_eg = MainLayout(
            parent=self._main_pane, controller=self,
            instrument_names=ELECTROGLAS_INSTRUMENT_NAMES,
            init_hardware_fn=self.init_hardware_eg, system="electroglas")
        self._by_system["electroglas"]["ui"] = self.instrument_panel_eg

        self._build_bottom_routing()
        self._autoload_default_ata_folders()
        # After the folders, so switching system finds its folder already
        # loaded; before init_hardware, so the first connect sweep runs
        # against the bench that was actually chosen.
        self._apply_default_prober()
        # Only the active system (Accretech unless a default prober says
        # otherwise, applied just above) sweeps at startup - pinging the
        # other rig's instruments when nobody selected it just produces
        # "not connected" log noise for hardware that may not even be
        # powered on. The other system connects itself the first time the
        # operator actually switches to it - see cmd_set_active_system.
        self.after(500, self._startup_sweep)
        self.update_statistics_visuals()
        self.check_system_ready()
        self.after(2000, self._system_ready_loop)
        self.after(1500, self._poll_prober_ready)

    def _autoload_default_ata_folders(self):
        """Each system (Accretech/Electroglas) can have its own default ATA
        folder, set via the ⭐ Set as Default button on the ATA Folder tab —
        load them both now so switching system doesn't need a manual load."""
        for system in ("accretech", "electroglas"):
            folder = app_settings.get_default_ata_folder(system)
            if not (folder and os.path.isdir(folder)):
                continue
            ui = self._by_system[system]["ui"]
            n_dies = ui.load_ata_folder(folder)
            self._by_system[system]["total"] = n_dies
            self._by_system[system]["tested"] = 0
            self._by_system[system]["passed"] = 0
            self._by_system[system]["failed"] = 0
            self._by_system[system]["results"].clear()
            folder_name = os.path.basename(folder)
            if system == self.active_system:
                self._ata_lbl.config(text=f"ATA: {folder_name}  ({n_dies} dies)",
                                     foreground="#1d4ed8")
                self._refresh_ata_picker()
                self._ata_picker_var.set(self._ata_display_name(folder_name))
                ui.exec_panel.set_wafer_map(ui.wafer_map, wafer_id=folder_name)
                ui.wafer_id_var.set(folder_name)
            ui.exec_panel.log(
                f"[SYSTEM] Default ATA folder '{folder_name}' auto-loaded — "
                f"{n_dies} dies found.")

    @property
    def drivers(self):
        return self._by_system[self.active_system]["drivers"]

    @property
    def results_data(self):
        return self._by_system[self.active_system]["results"]

    @property
    def ui(self):
        return self._by_system[self.active_system]["ui"]

    @property
    def total_dies(self):
        return self._by_system[self.active_system]["total"]

    @total_dies.setter
    def total_dies(self, value):
        self._by_system[self.active_system]["total"] = value

    @property
    def dies_tested(self):
        return self._by_system[self.active_system]["tested"]

    @dies_tested.setter
    def dies_tested(self, value):
        self._by_system[self.active_system]["tested"] = value

    @property
    def dies_passed(self):
        return self._by_system[self.active_system]["passed"]

    @dies_passed.setter
    def dies_passed(self, value):
        self._by_system[self.active_system]["passed"] = value

    @property
    def dies_failed(self):
        return self._by_system[self.active_system]["failed"]

    @dies_failed.setter
    def dies_failed(self, value):
        self._by_system[self.active_system]["failed"] = value

    def cmd_set_active_system(self, system):
        if system == self.active_system or system not in self._by_system:
            return
        old_ui = self.ui
        carry_over_folder = old_ui._ata_folder
        self.active_system = system
        self.title("Electrical Prober")
        self._main_pane.forget(old_ui)
        if self._main_pane.panes():
            self._main_pane.insert(0, self.ui, weight=1)
        else:
            self._main_pane.add(self.ui, weight=1)
        self._style_system_toggle()
        default_folder = app_settings.get_default_ata_folder(system)
        if default_folder and os.path.isdir(default_folder):
            if self.ui._ata_folder != default_folder:
                self._do_load_ata_folder(default_folder)
        elif carry_over_folder and self.ui._ata_folder != carry_over_folder:
            self._do_load_ata_folder(carry_over_folder)
        # _do_load_ata_folder (above) already syncs the label/picker when it
        # runs - but if this system's folder was already correctly loaded
        # (e.g. pre-loaded at startup), neither branch above fires, so do it
        # unconditionally here too.
        if self.ui._ata_folder:
            folder_name = os.path.basename(self.ui._ata_folder)
            self._ata_lbl.config(text=f"ATA: {folder_name}", foreground="#1d4ed8")
            self._refresh_ata_picker()
            self._ata_picker_var.set(self._ata_display_name(folder_name))
        else:
            self._ata_lbl.config(text="No ATA loaded", foreground="gray")
            self._ata_picker_var.set("")
        # The prober list is per-system, so it has to follow the toggle.
        self._refresh_bench_picker()
        self._refresh_routing_button()
        self.update_statistics_visuals()
        self.check_system_ready()
        self.log(f"[SYSTEM] Switched active system to {system.capitalize()} "
                 f"— prober {self._active_bench()}.")
        # First time this system is actually selected, connect its own
        # instruments - not before, and never the other system's. Deferred
        # so the tab swap above finishes redrawing first.
        if system not in self._connected_systems:
            fn = self.init_hardware_eg if system == "electroglas" else self.init_hardware
            self.after(100, fn)

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
        tk.Label(hdr, text="Electrical Prober",
                 bg="#374558", fg="#f0a020",
                 font=("Arial", 13)).pack(side="left", padx=4)

        toggle_frame = tk.Frame(hdr, bg="#374558")
        toggle_frame.pack(side="right", padx=12, pady=10)
        self._system_buttons = {}
        self._system_buttons["accretech"] = tk.Button(
            toggle_frame, text="Accretech", bd=1, relief="flat",
            font=("Arial", 9, "bold"), padx=10, pady=3,
            command=lambda: self.cmd_set_active_system("accretech"))
        self._system_buttons["accretech"].pack(side="left")
        self._system_buttons["electroglas"] = tk.Button(
            toggle_frame, text="Electroglas", bd=1, relief="flat",
            font=("Arial", 9, "bold"), padx=10, pady=3,
            command=lambda: self.cmd_set_active_system("electroglas"))
        self._system_buttons["electroglas"].pack(side="left")
        self._style_system_toggle()

    def _style_system_toggle(self):
        for system, btn in self._system_buttons.items():
            active = system == self.active_system
            btn.config(
                bg="#f0a020" if active else "#4b5768",
                fg="#1f2937" if active else "#d1d5db",
                activebackground="#f0a020" if active else "#5a6779",
                relief="sunken" if active else "flat")

    def _build_bottom_routing(self):
        lf = ttk.LabelFrame(self._main_pane, text="Switch Routing")
        self._bottom_routing_frame = lf
        self._routing_visible = False
        holder, self.bottom_routing = scrollable_routing(lf, self)
        holder.pack(fill="both", expand=True)

    def accretech_benches(self) -> list:
        return list(ACCRETECH_BENCHES)

    def electroglas_benches(self) -> list:
        try:
            return eg_profiles.profile_names()
        except Exception:
            return []

    def apply_prober(self, system: str, bench: str):
        """Switch the whole GUI to a prober: system first, then bench.

        Order matters - cmd_set_eg_profile reconnects instruments and pokes
        the Electroglas UI, so the Electroglas side has to be the active one
        before it runs.
        """
        if system not in self._by_system:
            self.log(f"[SYSTEM] Unknown system {system!r}")
            return
        if system != self.active_system:
            self.cmd_set_active_system(system)
        if system == "electroglas" and bench:
            try:
                if bench != eg_profiles.active_name():
                    self.cmd_set_eg_profile(bench)
            except Exception as e:
                self.log(f"[SYSTEM] Could not select {bench!r}: {e}")
        self._refresh_bench_picker()

    def _apply_default_prober(self):
        """Startup only. Silent when nothing is set - Accretech stays the
        fallback, which is what the app did before this setting existed."""
        system, bench = app_settings.get_default_prober()
        if not system:
            return
        self.log(f"[SYSTEM] Default prober: {system} / {bench}")
        self.apply_prober(system, bench)

    def _refresh_routing_button(self):
        """Switch Routing is an Accretech-only view, so hide its toggle on the
        Electroglas side rather than leaving a button that opens a pane with
        nothing relevant in it. Collapses the pane first if it is open,
        otherwise it would be stranded with no way to close it."""
        btn = getattr(self, "_routing_toggle_btn", None)
        if btn is None:
            return
        if self.active_system == "electroglas":
            if getattr(self, "_routing_visible", False):
                self.cmd_toggle_routing()
            btn.pack_forget()
        else:
            btn.pack(side="right", padx=6, pady=2)

    def cmd_toggle_routing(self):
        if self._routing_visible:
            self._main_pane.forget(self._bottom_routing_frame)
            self._routing_toggle_btn.config(text="▸ Show Routing")
        else:
            self._main_pane.add(self._bottom_routing_frame, weight=0)
            self._routing_toggle_btn.config(text="▾ Hide Routing")
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

    def _set_status(self, ui, name, mark, colour):
        """Update one roster row, tolerating a name with no label.

        The status labels are built from a fixed name list while the sweep
        works off the bench profile, so the two can drift. A KeyError here used
        to escape the connect loop's own except clause - which repeats the
        lookup - and abort the whole sweep, leaving every instrument after the
        missing one stuck on its previous result. A drifted name is a bug worth
        logging, but never one worth losing the rest of the bench over.
        """
        lbl = ui.status_labels.get(name)
        if lbl is None:
            self.log(f"[SYSTEM] {name} has no status row — add it to the "
                     f"instrument name list for this system")
            return
        lbl.config(text=f"{mark} {name}", foreground=colour)

    def _connect_instruments(self, ui, drivers, connections):
        ui.set_visible_instruments([name for name, _key, _drv in connections])
        # Reset the text, not just the colour. Leaving the previous sweep's
        # tick or cross showing meant an orange row was ambiguous - it could be
        # "not pinged yet" or a stale result from another bench entirely.
        for inst_name, lbl in ui.status_labels.items():
            lbl.config(text=f"⏳ {inst_name}", foreground="orange")
        self.update_idletasks()
        for name, key, driver in connections:
            try:
                response = driver.get_id() if hasattr(driver, "get_id") else driver.query("*IDN?")
                if response:
                    drivers[key] = driver
                    self._set_status(ui, name, "✅", "green")
                    self.log(f"[SYSTEM] Connected: {name}")
                else:
                    raise Exception("No response")
            except Exception as e:
                self._set_status(ui, name, "❌", "red")
                self.log(f"[ERROR] {name}: {e}")

    def _connect_instruments_eg(self, ui, drivers, connections):
        """Electroglas connect. Takes driver *factories*, not instances.

        Separate from _connect_instruments so the Accretech path keeps its
        existing behaviour untouched. Two things differ here:

        - Each driver is built inside the try. The 2400 sends *RST from its
          __init__, which raises when it is switched off, and with the whole
          list built up front that single failure aborted the sequence before
          any status label was updated - the tab just sat on "Pinging...".
        - Presence is settled by a serial poll before any ID query. It answers
          in milliseconds, where an absent instrument otherwise costs a full
          ID-query timeout; this loop runs on the UI thread, so that froze the
          window for ~30s whenever something on the bench was powered off.
        """
        # Only what this bench actually carries. Unfitted instruments used to
        # sit here as permanently grey "(not fitted)" rows; they are now simply
        # absent, and the Instruments tab still reports the full roster.
        ui.set_visible_instruments([name for name, _key, _factory in connections])
        # Reset the text, not just the colour. Leaving the previous sweep's
        # tick or cross showing meant an orange row was ambiguous - it could be
        # "not pinged yet" or a stale result from another bench entirely.
        for inst_name, lbl in ui.status_labels.items():
            lbl.config(text=f"⏳ {inst_name}", foreground="orange")
        self.update_idletasks()
        for name, key, build_driver in connections:
            try:
                driver = build_driver()
                if not driver.is_present():
                    raise Exception("no answer to serial poll — powered off or not on the bus?")
                response = driver.get_id()
                if response:
                    drivers[key] = driver
                    self._set_status(ui, name, "✅", "green")
                    self.log(f"[SYSTEM] Connected: {name}")
                else:
                    raise Exception("No response")
            except Exception as e:
                self._set_status(ui, name, "❌", "red")
                self.log(f"[ERROR] {name}: {e}")
            # Each row settles as it is pinged rather than all at the end, so a
            # slow instrument reads as "still going" instead of "hung".
            self.update_idletasks()

    def _startup_sweep(self):
        """Connect whichever system is active (Accretech, unless a default
        prober picked Electroglas above) - not both. See cmd_set_active_system
        for how the other one connects on demand, the first time it is
        actually selected.

        Skips the system if it is already in _connected_systems - a default
        prober set at startup switches the active system via
        cmd_set_active_system before this runs, which already scheduled its
        own connect; sweeping again here would just ping the bus twice."""
        try:
            if self.active_system in self._connected_systems:
                pass
            elif self.active_system == "electroglas":
                self.init_hardware_eg()
            else:
                self.init_hardware()
        finally:
            self._startup_done = True

    def init_hardware(self):
        self._connected_systems.add("accretech")
        self.log("[SYSTEM] Pinging Accretech hardware connections...")
        connections = [
            ("UF200R Prober",    "prober",   AccretechUF200R()),
            ("SMU (2636B)",      "smu",      Keithley2636B()),
            ("DMM (34461A)",     "dmm",      Keysight34461A()),
            ("SW_MATRIX",        "switch",   Keithley707B()),
            ("Wave Gen (33512B)","wave_gen", Keysight33512B()),
        ]
        acc_ui = self._by_system["accretech"]["ui"]
        try:
            acc_ui.set_bench_label(ACCRETECH_BENCHES[0])
        except Exception:
            pass
        self._connect_instruments(acc_ui,
                                  self._by_system["accretech"]["drivers"], connections)
        self.check_system_ready()

    # Driver per profile key. Which of these actually get connected depends on
    # the active bench profile - see instruments/eg_probers.yaml. A key marked
    # not-fitted there is skipped rather than reported as a failure, because the
    # benches genuinely differ: probe02 has a Keithley 2400 and a working VXI
    # multimeter, probe03 has neither.
    _EG_DRIVERS = {
        "prober_eg":     ("Electroglas 2001X",  "prober",  Electroglas2001X),
        # Keithley2400.__init__ takes no config key - it hardcodes 'smu_eg'.
        # Passing one raised TypeError inside the connect loop, so the SMU went
        # red on a bench where it answers perfectly well.
        "smu_eg":        ("Keithley 2400",      "smu",     Keithley2400),
        "dmm_eg":        ("HP 3458A",           "dmm",     HP3458A),
        "dmm_vxi_eg":    ("HP E1326B (VXI)",    "dmm_vxi", lambda: HPE1326B("dmm_vxi_eg")),
        "relay1_eg":     ("HP Switchbox 1",     "relay1",  lambda: HPSwitchbox("relay1_eg")),
        "relay2_eg":     ("HP Switchbox 2",     "relay2",  lambda: HPSwitchbox("relay2_eg")),
        "relay3_eg":     ("HP Switchbox 3",     "relay3",  lambda: HPSwitchbox("relay3_eg")),
        "power_supply_eg": ("Agilent 6634B", "power_supply", Agilent6634B),
    }

    def init_hardware_eg(self):
        self._connected_systems.add("electroglas")
        profile = eg_profiles.active_name()
        self.log(f"[SYSTEM] Pinging Electroglas hardware — {eg_profiles.label(profile)}")
        # instruments.yaml is derived from the profile, so make sure it matches
        # the active bench before any driver reads an address out of it.
        try:
            eg_profiles.apply_to_instruments_yaml(profile)
        except Exception as e:
            self.log(f"[SYSTEM] Could not apply profile {profile!r}: {e}")

        eg_ui = self._by_system["electroglas"]["ui"]
        try:
            eg_ui.set_bench_label(profile)
        except Exception:
            pass

        connections = []
        for key in eg_profiles.fitted_keys(profile):
            entry = self._EG_DRIVERS.get(key)
            if entry is None:
                self.log(f"[SYSTEM] {key} is in the profile but has no driver — skipped")
                continue
            display, drv_key, factory = entry
            connections.append((display, drv_key, factory))

        self._connect_instruments_eg(self._by_system["electroglas"]["ui"],
                                     self._by_system["electroglas"]["drivers"],
                                     connections)
        self.check_system_ready()

    def cmd_set_eg_profile(self, name: str):
        """Switch the Electroglas bench and reconnect against it."""
        try:
            changed = eg_profiles.set_active(name)
        except Exception as e:
            self.log(f"[SYSTEM] Could not switch to {name!r}: {e}")
            return
        # Old sessions point at the previous bench's addresses; drop them rather
        # than leave stale handles that would talk to the wrong instrument.
        drivers = self._by_system["electroglas"]["drivers"]
        for drv in list(drivers.values()):
            try:
                drv.close()
            except Exception:
                pass
        drivers.clear()
        self.log(f"[SYSTEM] Electroglas bench -> {eg_profiles.label(name)}"
                 + (f" ({len(changed)} address(es) updated)" if changed else ""))
        self.log(eg_profiles.summary(name))
        # The Recipe tab only offers instruments the bench actually has, so it
        # has to be told the bench changed.
        panel = getattr(self._by_system["electroglas"]["ui"], "recipe_panel", None)
        refresh = getattr(panel, "refresh_bench_instruments", None)
        if refresh:
            try:
                refresh()
            except Exception as e:
                self.log(f"[SYSTEM] Recipe tab instrument refresh failed: {e}")
        # During startup the scheduled sweep has not run yet and will pick this
        # bench up, so connecting here as well would just sweep the bus twice.
        if self._startup_done:
            self.init_hardware_eg()
 
    def check_system_ready(self):
        missing = []
        exec2_wm = getattr(self.ui, "_exec2_wafer_map", None)
        if not (exec2_wm and exec2_wm._last_dies):
            missing.append("wafer map")
        if not getattr(self.ui, "_exec2_steps", None):
            missing.append("recipe")
        required_instruments = (ACCRETECH_REQUIRED_DRIVERS if self.active_system == "accretech"
                                else ELECTROGLAS_REQUIRED_DRIVERS)
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
        ttk.Button(toolbar, text="🔕 Buzzer Clear", command=self.cmd_buzzer_clear).pack(side="left", padx=(0, 6), pady=2)

        ttk.Label(toolbar, text="ATA Folder:").pack(side="left", padx=(6, 2), pady=2)
        self._ata_picker_var = tk.StringVar()
        self._ata_picker_label_to_name: dict[str, str] = {}
        self._ata_picker = ttk.Combobox(
            toolbar, textvariable=self._ata_picker_var, state="readonly",
            width=24, postcommand=self._refresh_ata_picker)
        self._ata_picker.pack(side="left", padx=(0, 4), pady=2)
        self._ata_picker.bind("<<ComboboxSelected>>",
                              lambda _e: self._on_ata_picker_selected())

        # Moved to the Internal tab's own toolbar, next to Load/New ATA
        # Folder.
        # Not packed - the "ATA Folder:" picker above already names the
        # loaded folder, so this text was a second copy of the same
        # information. Left instantiated (just not shown) rather than
        # removed outright, so nothing has to change everywhere else in
        # this file that updates it via .config().
        self._ata_lbl = ttk.Label(toolbar, text="No ATA loaded", foreground="gray",
                                  font=("Segoe UI", 9))

        # Which physical prober the active system is pointed at. The Electroglas
        # benches carry different instruments at different addresses, so this
        # decides what gets connected - see instruments/eg_probers.yaml.
        # Accretech has only probe08 for now, so its list is a single entry and
        # the control is inert rather than hidden, to keep the toolbar stable.
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y",
                                                       padx=4, pady=3)
        ttk.Label(toolbar, text="Prober:").pack(side="left", padx=(2, 2), pady=2)
        self._bench_picker_var = tk.StringVar()
        self._bench_picker = ttk.Combobox(
            toolbar, textvariable=self._bench_picker_var, state="readonly",
            width=10, postcommand=self._refresh_bench_picker)
        self._bench_picker.pack(side="left", padx=(0, 4), pady=2)
        self._bench_picker.bind("<<ComboboxSelected>>",
                                lambda _e: self._on_bench_picker_selected())
        self._bench_lbl = ttk.Label(toolbar, text="", foreground="gray",
                                    font=("Segoe UI", 9))
        self._bench_lbl.pack(side="left", padx=(2, 8), pady=2)
        self._refresh_bench_picker()
        self._routing_toggle_btn = ttk.Button(
            toolbar, text="▸ Show Routing", command=self.cmd_toggle_routing)
        self._refresh_routing_button()
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

    @staticmethod
    def _ata_display_name(name: str) -> str:
        """Toolbar picker shows the trailing "ata" (case-insensitive)
        stripped, e.g. "NautATA" -> "Naut" - display only, the real folder
        name is still what's stored/opened everywhere else."""
        if name and name.lower().endswith("ata"):
            return name[:-3] or name
        return name

    def _refresh_ata_picker(self):
        names = self._find_ata_folders()
        self._ata_picker_label_to_name = {self._ata_display_name(n): n for n in names}
        self._ata_picker.configure(values=list(self._ata_picker_label_to_name.keys()))

    # -- prober bench picker ------------------------------------------------
    #
    # Only Electroglas has real profiles today. Accretech is a single machine,
    # so its "list" is one entry - the control still shows which prober you are
    # on, which is the point, and it grows the day a second Accretech appears.

    def _bench_names(self) -> list:
        if self.active_system == "electroglas":
            try:
                return eg_profiles.profile_names()
            except Exception as e:
                self.log(f"[SYSTEM] Could not read prober profiles: {e}")
                return []
        return list(ACCRETECH_BENCHES)

    def _active_bench(self) -> str:
        if self.active_system == "electroglas":
            try:
                return eg_profiles.active_name()
            except Exception:
                return ""
        return ACCRETECH_BENCHES[0]

    def _refresh_bench_picker(self):
        names = self._bench_names()
        self._bench_picker.configure(values=names)
        active = self._active_bench()
        if self._bench_picker_var.get() != active:
            self._bench_picker_var.set(active)
        if self.active_system == "electroglas" and active:
            try:
                fitted = eg_profiles.fitted_keys(active)
                self._bench_lbl.config(text=f"{len(fitted)} instruments",
                                       foreground="#1d4ed8")
            except Exception:
                self._bench_lbl.config(text="", foreground="gray")
        else:
            self._bench_lbl.config(text="", foreground="gray")
        # A single-entry list is not a choice; make that visible rather than
        # letting someone click at it expecting something to happen.
        self._bench_picker.configure(
            state="readonly" if len(names) > 1 else "disabled")

    def _on_bench_picker_selected(self):
        name = self._bench_picker_var.get()
        if self.active_system != "electroglas":
            return
        if name == eg_profiles.active_name():
            return
        self.cmd_set_eg_profile(name)
        self._refresh_bench_picker()
        # Keep the Instruments tab's own copy of this selector in step.
        panel = getattr(self._by_system["electroglas"]["ui"], "instruments_eg", None)
        for method in ("_refresh_bench_label", "_rebuild_addresses"):
            fn = getattr(panel, method, None)
            if fn:
                try:
                    fn()
                except Exception:
                    pass
        if panel is not None and hasattr(panel, "_bench_var"):
            panel._bench_var.set(name)

    def _on_ata_picker_selected(self):
        label = self._ata_picker_var.get()
        if not label:
            return
        name = self._ata_picker_label_to_name.get(label, label)
        folder = os.path.join(self.ui.working_dir_var.get(), name)
        self._do_load_ata_folder(folder)

    def update_statistics_visuals(self):
        untested = self.total_dies - self.dies_tested
        self.ui.lbl_stats_text.config(text=f"Pass: {self.dies_passed}  |  Fail: {self.dies_failed}\nUntested: {untested}")
        self.ui.lbl_progress.config(text=f"Progress: {self.dies_tested} / {self.total_dies} tested")
        self.ui.lbl_results_large.config(text=f"Total Passed: {self.dies_passed}     |     Total Failed: {self.dies_failed}     |     Untested: {untested}")
        self.ui.draw_donut(self.ui.sidebar_canvas, 120, self.dies_passed, self.dies_failed, untested)
        if hasattr(self.ui, "results_canvas"):
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
        self._refresh_ata_picker()
        self._ata_picker_var.set(self._ata_display_name(folder_name))
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

    def cmd_new_ata_folder(self):
        working_dir = self.ui.working_dir_var.get()
        if not working_dir:
            messagebox.showerror("No Working Directory",
                                 "Set a Working Directory first.")
            return
        if not os.path.isdir(working_dir):
            try:
                os.makedirs(working_dir, exist_ok=True)
            except OSError as exc:
                messagebox.showerror("Working Directory",
                                     f"Could not create working directory:\n{exc}")
                return
        name = simpledialog.askstring("New ATA Folder", "Folder name:", parent=self)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if not name.lower().endswith("ata"):
            name = f"{name}ATA"
        folder = os.path.join(working_dir, name)
        if os.path.exists(folder):
            messagebox.showerror("Already Exists", f"{folder}\nalready exists.")
            return
        try:
            os.makedirs(folder)
        except OSError as exc:
            messagebox.showerror("Could Not Create Folder", str(exc))
            return
        self.log(f"[SYSTEM] Created new ATA folder: {folder}")
        self._refresh_ata_picker()
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
        # Export formats (unlike "Save as CSV", which dumps the whole
        # session's history) only ever cover the most recently started run —
        # re-running shouldn't silently pile old runs' rows into a new export.
        last_run_results = self.ui.get_last_run_results()
        if not xfmt.has_data_for_format(fmt, last_run_results):
            if fmt_type == "csv":
                reason = "at least one current or resistance reading from a die touchdown"
            else:
                reason = ("readings that carry a device-ID string — the wafer map "
                         "needs an ID column, or set the IDs with Overlay…"
                         if fmt.get("requires_die_id", True) else "measurement results")
            self.ui.exec_panel.log(
                f"[ERROR] No matching results yet from the last run for '{fmt['name']}' — "
                f"this format needs {reason}.")
            return
        ext = "csv" if fmt_type == "csv" else "sql"
        name_parts = [current_lot] + ([wafer_id] if wafer_id else []) + [
            fmt["table"] or "export"]
        if fmt.get("append_date"):
            name_parts.append(dt.date.today().strftime("%Y%m%d"))
        filepath = os.path.join(export_dir, "_".join(name_parts) + f".{ext}")

        try:
            if fmt_type == "csv":
                rows = xfmt.build_csv_rows(fmt, last_run_results, current_lot, wafer_id)
                fieldnames = [c["field"] for c in fmt["columns"]]
                # Explicit utf-8: without it Python uses the Windows locale
                # encoding (cp1252 here), which wrote an em-dash as a lone
                # 0x97 byte - not valid UTF-8, so the export would not reopen.
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                self.ui.exec_panel.log(
                    f"[SYSTEM] Success! {len(rows)} '{fmt['name']}' row(s) saved to -> {filepath}")
            else:
                statements = xfmt.build_insert_statements(fmt, last_run_results, current_lot, wafer_id)
                # Explicit utf-8: without it Python uses the Windows locale
                # encoding (cp1252 here), which wrote an em-dash as a lone
                # 0x97 byte - not valid UTF-8, so the export would not reopen.
                with open(filepath, "w", newline="", encoding="utf-8") as f:
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
        if drv and drv.inst and self.active_system != "accretech":
            self.log(f"[ABORT] {self.active_system.capitalize()} prober stop command "
                    "not yet implemented — verify chuck/output state manually.")
        if drv and drv.inst and self.active_system == "accretech":
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

_SINGLE_INSTANCE_MUTEX_NAME = "Global\\AtomicaTesterSingleInstanceMutex"
_ERROR_ALREADY_EXISTS = 183
_SW_RESTORE = 9
_APP_WINDOW_TITLES = ("Electrical Prober",)


def _find_other_instance_window() -> int:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum_proc(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        if buf.value in _APP_WINDOW_TITLES:
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(enum_proc, 0)
    return found[0] if found else 0


def _ensure_single_instance() -> bool:
    if sys.platform != "win32":
        return True
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW(None, False, _SINGLE_INSTANCE_MUTEX_NAME)
    if kernel32.GetLastError() != _ERROR_ALREADY_EXISTS:
        return True
    hwnd = _find_other_instance_window()
    if hwnd:
        user32 = ctypes.windll.user32
        user32.ShowWindow(hwnd, _SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
    return False


if __name__ == "__main__":
    if _ensure_single_instance():
        app = AtomicaDashboard()
        app.mainloop()
