import threading
import tkinter as tk
from tkinter import messagebox, ttk

_NONE = "none"
_INT1 = "int1"
_INT2 = "int2"
_FLOAT2 = "float2"

_ZERO_ARG_MOTION = [
    ("Z Up (ZU)", "z_up",
     "Send ZU?\n\n⚠ CONTACT: the chuck rises to probing height — the wafer "
     "TOUCHES the probe card needles."),
    ("Z Down (ZD)", "z_down",
     "Send ZD?\n\nThe chuck drops — the wafer separates from the probe "
     "card. This is the safe direction."),
    ("Move to First Die (MF)", "move_to_start_die",
     "Send MF?\n\nPositions the first die of the current wafer map."),
    ("Move to Home (HO)", "move_to_home",
     "Send HO?\n\nReturns the chuck to its mechanical home position."),
]

_ONE_ARG_MOTION = [
    ("Z Absolute (ZM)", "move_z_absolute", "Z"),
    ("Z Relative (ZR)", "move_z_relative", "dZ"),
    ("Theta Relative (MT)", "move_theta_relative", "dθ"),
]

_TWO_ARG_MOTION = [
    ("Move Relative — M units (MM, default step)", "move_relative_m", "dX", "dY"),
    ("Move Absolute — M units (MA)", "move_absolute_m", "X", "Y"),
    ("Move Absolute — Die (MO)", "move_absolute_die", "Die X", "Die Y"),
    ("Move Relative — Die (MD)", "move_relative_die", "dDie X", "dDie Y"),
    ("Move Micro (FM)", "move_micro", "dX", "dY"),
]

_SETUP_COMMANDS = [
    ("Die Size (SP1, raw units)", "set_die_size", _INT2, ("X", "Y")),
    ("Die Size — mm  (×1000 → SP1)", "set_die_size_mm", _FLOAT2, ("X mm", "Y mm")),
    ("Die Size — mil  (×10 → SP1)", "set_die_size_mil", _FLOAT2, ("X mil", "Y mil")),
    ("Die Size — precise mm (SP29)", "set_die_size_precise_mm", _FLOAT2, ("X mm", "Y mm")),
    ("Reference Die Coordinate (SP2)", "set_reference_die_coordinate", _INT2, ("X", "Y")),
    ("Set First Die (FD)", "set_first_die", _NONE, ()),
    ("Wafer Diameter (SP4D)", "set_wafer_diameter", _INT1, ("Diameter",)),
    ("Starting Wafer Number (SM16N)", "set_starting_wafer_number", _INT1, ("Number",)),
    ("Current Cassette (SM70C)", "set_current_cassette", _INT1, ("Cassette",)),
    ("Flat Orientation (SM3F)", "set_flat_orientation", _INT1, ("Orientation",)),
    ("Coordinate Quadrant (SM11Q)", "set_coordinate_quadrant", _INT1, ("Quadrant",)),
    ("Probe Quadrant (SM2Q)", "set_probe_quadrant", _INT1, ("Quadrant",)),
    ("Units (SM1U)", "set_units", _INT1, ("Unit code",)),
]

_LIMIT_COMMANDS = [
    ("Z Autoalign Height (SP9Z)", "set_z_autoalign_height", _INT1, ("Z",)),
    ("Z Clearance (SP6Z)", "set_z_clearance", _INT1, ("Z",)),
    ("Z Down Limit (SP8Z)", "set_z_down_limit", _INT1, ("Z",)),
    ("Z Up Limit (SP7Z)", "set_z_up_limit", _INT1, ("Z",)),
    ("Z Overtravel (SP5Z)", "set_z_overtravel", _INT1, ("Z",)),
    ("Z Undertravel (SP10Z)", "set_z_undertravel", _INT1, ("Z",)),
    ("Zprofile Height (PH)", "set_zprofile_height", _NONE, ()),
]

_COUNTER_COMMANDS = [
    ("Reprobe Count (SP14R)", "set_reprobe_count", _INT1, ("Count",)),
    ("Touchdown Counter (SP19C)", "set_touchdown_counter", _INT1, ("Count",)),
    ("Yield to Pass Wafer (SP33Y)", "set_yield_to_pass_wafer", _INT1, ("Yield %",)),
    ("Count Pulse Width (SM32P)", "set_count_pulse_width", _INT1, ("Width",)),
    ("Probe Clean Count (SM12C)", "set_probe_clean_count", _INT2, ("Count", "W")),
    ("Profiler Retry Count (SM42R)", "set_profiler_retry_count", _INT1, ("Retries",)),
]

_MISC_COMMANDS = [
    ("Wafer X Expansion (SX4C)", "set_wafer_x_expansion", _INT1, ("Coefficient",)),
    ("Wafer Y Expansion (SX5C)", "set_wafer_y_expansion", _INT1, ("Coefficient",)),
    ("Sync Date/Time to Now (TI)", "set_date_time", _NONE, ()),
]

_MOTION_PREFIXES = ("ZU", "ZD", "ZM", "ZR", "MT", "MM", "MO", "MA", "MD",
                    "FM", "MF", "HO", "J", "U", "L", "I")


class EgProberDebugPanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_main()

    def _drv(self, silent: bool = False):
        drv = self.controller.drivers.get("prober")
        ok = drv is not None and drv.inst is not None
        if not ok and not silent:
            self._set_status("Not connected", "red")
        return drv if ok else None

    def _log(self, msg: str):
        self.controller.log(msg)

    def _set_status(self, text: str, color: str = "black"):
        self._status_lbl.config(text=text, foreground=color)

    def _show_response(self, label: str, resp: str):
        self._resp_var.set(f"[{label}]  {resp}")

    def _run_bg(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    def _build_topbar(self):
        bar = ttk.Frame(self, padding=(6, 4))
        bar.grid(row=0, column=0, sticky="ew")

        self._status_lbl = ttk.Label(bar, text="Status: —",
                                      font=("Consolas", 10, "bold"),
                                      foreground="gray", width=60, anchor="w")
        self._status_lbl.pack(side="left")
        ttk.Button(bar, text="Read Status (?S)",
                   command=self._cmd_read_status).pack(side="right", padx=2)

    def _build_main(self):
        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        self._build_left(pane)
        self._build_right(pane)

    def _build_left(self, pane):
        outer = ttk.Frame(pane)
        pane.add(outer, weight=1)
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)

        sc = tk.Canvas(outer, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=sc.yview)
        sc.configure(yscrollcommand=vsb.set)
        sc.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        left = tk.Frame(sc)
        win_id = sc.create_window((0, 0), window=left, anchor="nw")

        left.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
        sc.bind("<Configure>", lambda e: sc.itemconfig(win_id, width=e.width))

        def _wheel(e):
            sc.yview_scroll(-1 if e.delta > 0 else 1, "units")
        sc.bind("<MouseWheel>", _wheel)
        left.bind("<MouseWheel>", _wheel)

        mf = ttk.LabelFrame(left, text="Chuck / Die Motion", padding=6)
        mf.pack(fill="x", padx=4, pady=(4, 6))
        for label, method, confirm in _ZERO_ARG_MOTION:
            ttk.Button(mf, text=label,
                       command=lambda m=method, l=label, c=confirm:
                       self._send_motion(m, l, [], c)).pack(fill="x", pady=1)
        ttk.Separator(mf, orient="horizontal").pack(fill="x", pady=4)
        for label, method, f1 in _ONE_ARG_MOTION:
            self._motion_row(mf, label, method, (f1,))
        for label, method, f1, f2 in _TWO_ARG_MOTION:
            self._motion_row(mf, label, method, (f1, f2))

        self._setup_section(left, "Wafer / Die Setup", _SETUP_COMMANDS)
        self._setup_section(left, "Z Limits & Profile", _LIMIT_COMMANDS)
        self._setup_section(left, "Counters & Yield", _COUNTER_COMMANDS)
        self._setup_section(left, "Wafer Expansion & Time", _MISC_COMMANDS)

    def _motion_row(self, parent, label, method, field_labels):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, width=32, anchor="w").pack(side="left")
        vars_ = []
        for fl in field_labels:
            ttk.Label(row, text=f"{fl}:").pack(side="left")
            v = tk.StringVar(value="0")
            ttk.Entry(row, textvariable=v, width=7).pack(side="left", padx=(2, 6))
            vars_.append(v)
        mnemonic = label.rsplit("(", 1)[-1].rstrip(")")
        confirm = f"Send {mnemonic}?\n\nThis causes physical prober motion."
        ttk.Button(row, text="Send", width=6,
                   command=lambda m=method, l=label, vs=vars_, c=confirm:
                   self._send_motion(m, l, vs, c)).pack(side="left")

    def _setup_section(self, parent, title, specs):
        lf = ttk.LabelFrame(parent, text=title, padding=6)
        lf.pack(fill="x", padx=4, pady=(0, 6))
        for label, method, kind, field_labels in specs:
            row = ttk.Frame(lf)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=32, anchor="w").pack(side="left")
            vars_ = []
            for fl in field_labels:
                ttk.Label(row, text=f"{fl}:").pack(side="left")
                v = tk.StringVar(value="0")
                ttk.Entry(row, textvariable=v, width=8).pack(side="left", padx=(2, 6))
                vars_.append(v)
            ttk.Button(row, text="Send", width=6,
                       command=lambda m=method, l=label, k=kind, vs=vars_:
                       self._send_setup(m, l, k, vs)).pack(side="left")

    def _build_right(self, pane):
        right = ttk.Frame(pane, padding=4)
        pane.add(right, weight=1)
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        rf = ttk.LabelFrame(right, text="Last Response", padding=6)
        rf.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self._resp_var = tk.StringVar(value="—")
        ttk.Label(rf, textvariable=self._resp_var, font=("Consolas", 9),
                  foreground="#0077cc", wraplength=380, justify="left").pack(anchor="w")

        tf = ttk.LabelFrame(right, text="Raw GPIB Terminal", padding=6)
        tf.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        term = ttk.Frame(tf)
        term.pack(fill="x")
        self._cmd_var = tk.StringVar()
        entry = ttk.Entry(term, textvariable=self._cmd_var, font=("Consolas", 10), width=24)
        entry.pack(side="left", padx=(0, 4))
        entry.bind("<Return>", lambda _e: self._send_raw())
        ttk.Button(term, text="Send", command=self._send_raw).pack(side="left", padx=2)
        ttk.Label(tf,
                  text="Commands starting with '?' are sent as queries (e.g. "
                       "?S, ?X, ?Y); everything else is written as-is. Known "
                       "motion mnemonics ask for confirmation first.",
                  foreground="gray", font=("Arial", 8), justify="left",
                  wraplength=360).pack(anchor="w", pady=(4, 0))

        nf = ttk.LabelFrame(right, text="About Status Reporting", padding=6)
        nf.grid(row=2, column=0, sticky="new")
        ttk.Label(nf,
                  text="The Electroglas 2001CXE reports status as a string "
                       "via '?S' (e.g. 'idle', 'moving', 'error: ...') rather "
                       "than a numeric GP-IB status byte, so there is no STB "
                       "code table here — read the status line above after "
                       "sending a command.",
                  foreground="gray", font=("Arial", 8), justify="left",
                  wraplength=360).pack(anchor="w")

    def _cmd_read_status(self):
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                status = drv.get_prober_status()
                self._log(f"[PROBER] ?S -> {status}")
                color = "red" if "error" in (status or "").lower() else "#22bb55"
                self.after(0, lambda: self._set_status(f"Status: {status}", color))
            except Exception as e:
                self._log(f"[PROBER] Status error: {e}")
                self.after(0, lambda: self._set_status(f"Status error: {e}", "red"))
        self._run_bg(_run)

    def _send_motion(self, method, label, vars_, confirm_msg):
        try:
            args = [int(round(float(v.get()))) for v in vars_]
        except ValueError:
            messagebox.showerror("Invalid Input", f"{label}: enter numeric value(s).")
            return
        if not messagebox.askyesno("Confirm Motion", confirm_msg):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log(f"[PROBER] >> {label}  args={args}")
                result = getattr(drv, method)(*args)
                self._log(f"[PROBER] << {result}")
                self.after(0, lambda: self._show_response(label, str(result)))
                self.after(0, self._cmd_read_status)
            except Exception as e:
                self._log(f"[PROBER] ERROR ({label}): {e}")
                self.after(0, lambda: self._resp_var.set(f"Error: {e}"))
        self._run_bg(_run)

    def _send_setup(self, method, label, kind, vars_):
        try:
            if kind == _NONE:
                args = []
            elif kind == _INT1:
                args = [int(round(float(vars_[0].get())))]
            elif kind == _INT2:
                args = [int(round(float(vars_[0].get()))),
                        int(round(float(vars_[1].get())))]
            else:
                args = [float(vars_[0].get()), float(vars_[1].get())]
        except ValueError:
            messagebox.showerror("Invalid Input", f"{label}: enter numeric value(s).")
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log(f"[PROBER] >> {label}  args={args}")
                getattr(drv, method)(*args)
                self.after(0, lambda: self._show_response(label, "sent"))
            except Exception as e:
                self._log(f"[PROBER] ERROR ({label}): {e}")
                self.after(0, lambda: self._resp_var.set(f"Error: {e}"))
        self._run_bg(_run)

    def _send_raw(self):
        raw = self._cmd_var.get().strip()
        if not raw:
            return
        is_query = raw.startswith("?")
        is_motion = any(raw.upper().startswith(p) for p in _MOTION_PREFIXES)
        if is_motion:
            if not messagebox.askyesno("Motion Command",
                                       f"'{raw}' looks like a motion command.\n\n"
                                       "This may cause physical prober motion.\n"
                                       "Send anyway?"):
                return
        def _run(cmd=raw):
            drv = self._drv()
            if not drv:
                return
            try:
                self._log(f"[PROBER] >> {cmd!r}")
                if is_query:
                    resp = drv.inst.query(cmd)
                    self._log(f"[PROBER] << {resp!r}")
                    self.after(0, lambda: self._resp_var.set(f"[{cmd}] {resp}"))
                else:
                    drv.inst.write(cmd)
                    self.after(0, lambda: self._resp_var.set(
                        "Write sent — no response expected"))
                    if is_motion:
                        self.after(0, self._cmd_read_status)
            except Exception as e:
                self._log(f"[PROBER] ERROR: {e}")
                self.after(0, lambda: self._resp_var.set(f"Error: {e}"))
        self._run_bg(_run)
