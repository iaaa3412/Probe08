import threading
import time
import tkinter as tk
from tkinter import ttk


class InstrumentsEgPanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._dmm_cont = False

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self._build_smu()
        self._build_dmm()
        self._build_ps()

    def _log(self, msg: str):
        self.controller.log(msg)

    def _drv(self, key: str):
        drv = self.controller.drivers.get(key)
        return drv if (drv and drv.inst) else None

    def _build_smu(self):
        lf = ttk.LabelFrame(self, text="SMU — Keithley 2400", padding=8)
        lf.grid(row=0, column=0, sticky="new", padx=8, pady=8)

        row = ttk.Frame(lf)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text="Source:").pack(side="left")
        self._smu_src_var = tk.StringVar(value="Voltage")
        ttk.Combobox(row, textvariable=self._smu_src_var, values=["Voltage", "Current"],
                    width=9, state="readonly").pack(side="left", padx=4)
        ttk.Label(row, text="Level:").pack(side="left", padx=(8, 0))
        self._smu_level_var = tk.StringVar(value="0")
        ttk.Entry(row, textvariable=self._smu_level_var, width=10).pack(side="left", padx=4)
        ttk.Label(row, text="Limit:").pack(side="left", padx=(8, 0))
        self._smu_limit_var = tk.StringVar(value="0.01")
        ttk.Entry(row, textvariable=self._smu_limit_var, width=10).pack(side="left", padx=4)

        btn_row = ttk.Frame(lf)
        btn_row.pack(fill="x", pady=(6, 2))
        ttk.Button(btn_row, text="Output ON", command=self._smu_output_on).pack(side="left")
        ttk.Button(btn_row, text="Output OFF", command=self._smu_output_off).pack(
            side="left", padx=(6, 0))
        ttk.Button(btn_row, text="Measure", command=self._smu_measure).pack(
            side="left", padx=(6, 0))

        self._smu_reading_var = tk.StringVar(value="V: —    I: —    R: —")
        ttk.Label(lf, textvariable=self._smu_reading_var, font=("Consolas", 9)).pack(
            anchor="w", pady=(6, 0))

    def _smu_output_on(self):
        drv = self._drv("smu")
        if not drv:
            self._log("[SMU] Not connected")
            return
        try:
            level = float(self._smu_level_var.get())
            limit = float(self._smu_limit_var.get())
            if self._smu_src_var.get() == "Voltage":
                drv.set_voltage("", level)
                drv.set_current_limit("", limit)
            else:
                drv.set_current("", level)
                drv.set_voltage_limit("", limit)
            drv.turn_output_on("")
            self._log(f"[SMU] Output ON — {self._smu_src_var.get()}={level}, limit={limit}")
        except Exception as e:
            self._log(f"[SMU] Error: {e}")

    def _smu_output_off(self):
        drv = self._drv("smu")
        if not drv:
            self._log("[SMU] Not connected")
            return
        try:
            drv.turn_output_off("")
            self._log("[SMU] Output OFF")
        except Exception as e:
            self._log(f"[SMU] Error: {e}")

    def _smu_measure(self):
        drv = self._drv("smu")
        if not drv:
            self._log("[SMU] Not connected")
            return

        def _run():
            try:
                v = drv.measure_voltage("")
                i = drv.measure_current("")
                r = drv.measure_resistance("")
                self.after(0, lambda: self._smu_reading_var.set(
                    f"V: {v:.6g} V    I: {i:.6g} A    R: {r:.6g} Ω"))
                self._log(f"[SMU] V={v:.6g} V  I={i:.6g} A  R={r:.6g} Ω")
            except Exception as e:
                self._log(f"[SMU] Measure error: {e}")
        threading.Thread(target=_run, daemon=True).start()

    def _build_dmm(self):
        lf = ttk.LabelFrame(self, text="DMM — HP 3458A", padding=8)
        lf.grid(row=0, column=1, sticky="new", padx=8, pady=8)

        btn_row = ttk.Frame(lf)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Measure DCV",
                  command=lambda: self._dmm_measure("v")).pack(side="left")
        ttk.Button(btn_row, text="Measure DCI",
                  command=lambda: self._dmm_measure("i")).pack(side="left", padx=(6, 0))
        self._dmm_cont_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(btn_row, text="Continuous", variable=self._dmm_cont_var,
                       command=self._toggle_dmm_cont).pack(side="left", padx=(10, 0))

        self._dmm_reading_var = tk.StringVar(value="—")
        ttk.Label(lf, textvariable=self._dmm_reading_var, font=("Consolas", 9)).pack(
            anchor="w", pady=(6, 0))

    def _dmm_measure(self, kind: str):
        drv = self._drv("dmm")
        if not drv:
            self._log("[DMM] Not connected")
            return
        try:
            if kind == "v":
                val = drv.measure_voltage_dc()
                self._dmm_reading_var.set(f"{val:.6g} V")
            else:
                val = drv.measure_current_dc()
                self._dmm_reading_var.set(f"{val:.6g} A")
            self._log(f"[DMM] {kind.upper()} = {val:.6g}")
        except Exception as e:
            self._log(f"[DMM] Error: {e}")

    def _toggle_dmm_cont(self):
        self._dmm_cont = self._dmm_cont_var.get()
        if self._dmm_cont:
            threading.Thread(target=self._dmm_cont_thread, daemon=True).start()

    def _dmm_cont_thread(self):
        while self._dmm_cont:
            drv = self._drv("dmm")
            if drv:
                try:
                    val = drv.measure_voltage_dc()
                    self.after(0, lambda v=val: self._dmm_reading_var.set(f"{v:.6g} V"))
                except Exception:
                    pass
            time.sleep(0.5)

    def _build_ps(self):
        lf = ttk.LabelFrame(self, text="Power Supply — Agilent 6634B", padding=8)
        lf.grid(row=1, column=0, columnspan=2, sticky="new", padx=8, pady=(0, 8))

        row = ttk.Frame(lf)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text="Voltage:").pack(side="left")
        self._ps_v_var = tk.StringVar(value="0")
        ttk.Entry(row, textvariable=self._ps_v_var, width=10).pack(side="left", padx=4)
        ttk.Label(row, text="Current Limit:").pack(side="left", padx=(8, 0))
        self._ps_i_var = tk.StringVar(value="0.1")
        ttk.Entry(row, textvariable=self._ps_i_var, width=10).pack(side="left", padx=4)

        btn_row = ttk.Frame(lf)
        btn_row.pack(fill="x", pady=(6, 2))
        ttk.Button(btn_row, text="Output ON", command=self._ps_output_on).pack(side="left")
        ttk.Button(btn_row, text="Output OFF", command=self._ps_output_off).pack(
            side="left", padx=(6, 0))
        ttk.Button(btn_row, text="Measure", command=self._ps_measure).pack(
            side="left", padx=(6, 0))

        self._ps_reading_var = tk.StringVar(value="V: —    I: —")
        ttk.Label(lf, textvariable=self._ps_reading_var, font=("Consolas", 9)).pack(
            anchor="w", pady=(6, 0))

    def _ps_output_on(self):
        drv = self._drv("power_supply")
        if not drv:
            self._log("[PS] Not connected")
            return
        try:
            drv.set_voltage(float(self._ps_v_var.get()))
            drv.set_current_limit(float(self._ps_i_var.get()))
            drv.turn_output_on()
            self._log(f"[PS] Output ON — V={self._ps_v_var.get()}, "
                     f"I limit={self._ps_i_var.get()}")
        except Exception as e:
            self._log(f"[PS] Error: {e}")

    def _ps_output_off(self):
        drv = self._drv("power_supply")
        if not drv:
            self._log("[PS] Not connected")
            return
        try:
            drv.turn_output_off()
            self._log("[PS] Output OFF")
        except Exception as e:
            self._log(f"[PS] Error: {e}")

    def _ps_measure(self):
        drv = self._drv("power_supply")
        if not drv:
            self._log("[PS] Not connected")
            return
        try:
            v = drv.measure_voltage()
            i = drv.measure_current()
            self._ps_reading_var.set(f"V: {v:.6g} V    I: {i:.6g} A")
            self._log(f"[PS] V={v:.6g} V  I={i:.6g} A")
        except Exception as e:
            self._log(f"[PS] Error: {e}")
