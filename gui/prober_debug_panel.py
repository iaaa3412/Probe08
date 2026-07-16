"""Prober Debug Panel — Accretech UF200/190 verification tool.

All commands sourced from UF200/190 GP-IB Commands Manual (FT02000-R003-E0).

Safe commands in this panel (read-only, no chuck motion):
  B   Get prober ID            Q   Die coordinates (probing-only)
  E   Short error code         R   Absolute position, 0.1 µm (probing-only)
  e   Full error message       V   Lot number
  ms  Prober status code       X   Wafer number
  H   Multi-site info          b   Wafer ID
  q   Start die coordinates    c   Pass/Fail counts
  O   On-wafer info (probing)  w   Wafer status (cassette)
  Y   Gross die count          x   Cassette status
                               y   Yield data

Z STATE IS NOT QUERYABLE on the prober — there is no "is the chuck up?"
request. The only Z information is the completion STB of each motion
command (67 = finished chuck UP, 65/66/68/70/90 = finished chuck DOWN),
so the driver tracks it (drv.z_is_up) and this panel displays the tracked
value. After an alarm, stop (K), or unconfirmed raw motion command the
state shows "unknown" until the next confirmed Z/D/motion reply.

Motion / action (confirmation required):
  A   XY travel BY a distance in µm (chuck height restored after)
  S   XY travel by DIE INDEXES, relative (SY±nnnnX±nnnn; whole dies, not µm)
  J   Next die, or ABSOLUTE die map position (JYyyyXxxx, −99…511)
  G   Position start die (resets counters)
  Z   Z UP  ⚠ CONTACT — chuck rises to probing height + overdrive:
              the wafer TOUCHES the probe card needles
  D   Z DOWN — chuck drops, wafer SEPARATES from the needles (safe direction)
  I   Set index / pitch (only while waiting for lot process start)
  K   Stop

IMPORTANT — the CHUCK moves in Z, not the probe card. "Up" = contact.
Commands A, C, D, F, G, J, M, P, S, W, Z, jp, js, z are only valid while
probing is active (start die positioned → last die tested); at other times
they cause a "GP-IB Command Execution Condition Error".

STB codes are USER-CONFIGURABLE on the prober via STB Code Settings menu.
The driver's _wait_for_stb values are the manual's factory defaults, which
may differ if this installation's config was customized.
"""
from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from instruments.accretech_uf200r import STB_DESCRIPTIONS

# Commands only valid while probing is active — warn if sent while idle.
# (A/C/F/G/J/M/P/S/W/jp/js/z are *2 in the command list; the D and Z
# flowcharts (§4.4, §4.36) also reject when probing is not going on.)
# Case-sensitive: 'z' (set contact height) ≠ 'Z' (Z UP).
_PROBING_ONLY = {"A", "C", "D", "F", "G", "J", "M", "P", "S", "W", "Z",
                 "jp", "js", "z"}
# Commands that cause physical motion (or marking) — require confirmation
_MOTION_CMDS  = {"A", "C", "D", "G", "J", "K", "L", "L1", "L8", "L9",
                 "M", "N", "N1", "N2", "N9", "S", "U", "U0", "U9",
                 "W", "WB", "Z", "Z+", "Z-", "jc", "j2", "jm", "jp", "js"}
# Commands answered with data (command echo + string) — sent as query;
# everything else only responds via STB / serial poll.
_QUERY_CMDS   = {"B", "E", "H", "O", "Q", "R", "V", "X", "Y",
                 "b", "c", "d", "e", "f", "i", "o", "q", "r", "w", "x", "y",
                 "ms", "kc", "kh", "ku", "nd", "ni", "np", "fp", "du"}
# Two-character mnemonics (checked before falling back to the first char)
_TWO_CHAR = {"ms", "kc", "ku", "kd", "kh", "jc", "j2", "ji", "jm", "jp",
             "js", "jv", "jw", "n6", "nc", "nd", "ni", "np", "du", "dd",
             "em", "es", "fp", "al", "le", "st", "vZ", "vE", "U0", "U9",
             "L1", "L8", "L9", "N1", "N2", "N9", "WB", "VR", "Z+", "Z-"}


def _mnemonic(raw: str) -> str:
    """Extract the (case-sensitive) command mnemonic from a raw string."""
    if raw[:2] in _TWO_CHAR:
        return raw[:2]
    return raw[:1]


class ProberDebugPanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._polling  = False
        self._poll_job = None

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_main()
        self._update_z_display()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _drv(self, silent: bool = False):
        drv = self.controller.drivers.get("prober")
        ok  = drv is not None and drv.inst is not None
        if not ok and not silent:
            self._set_stb("Not connected", "red")
        return drv if ok else None

    def _log(self, msg: str):
        self.controller.log(msg)

    def _set_stb(self, text: str, color: str = "black"):
        self._stb_lbl.config(text=text, foreground=color)

    def _show_response(self, cmd: str, resp: str):
        self._resp_var.set(f"[{cmd}]  {resp}")

    def _run_bg(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    def _safe_query(self, drv, method_name: str, cmd_label: str):
        try:
            self._log(f"[PROBER] >> {cmd_label}")
            result = getattr(drv, method_name)()
            self.after(0, lambda r=result: self._show_response(cmd_label, str(r)))
        except Exception as e:
            self._log(f"[PROBER] ERROR ({cmd_label}): {e}")
            self.after(0, lambda: self._resp_var.set(f"Error: {e}"))

    # ── Top bar ──────────────────────────────────────────────────────────────

    def _build_topbar(self):
        bar = ttk.Frame(self, padding=(6, 4))
        bar.grid(row=0, column=0, sticky="ew")

        self._stb_lbl = ttk.Label(bar, text="STB: —",
                                   font=("Consolas", 10, "bold"),
                                   foreground="gray", width=60, anchor="w")
        self._stb_lbl.pack(side="left")

        self._poll_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Auto-poll STB (1 s)",
                        variable=self._poll_var,
                        command=self._toggle_poll).pack(side="right", padx=8)
        ttk.Button(bar, text="Read STB",
                   command=self._cmd_read_stb).pack(side="right", padx=2)

    # ── Main area ─────────────────────────────────────────────────────────────

    def _build_main(self):
        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)

        self._build_left(pane)
        self._build_right(pane)

    # ── Left pane ─────────────────────────────────────────────────────────────

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

        def _left_wheel(e):
            sc.yview_scroll(-1 if e.delta > 0 else 1, "units")
        sc.bind("<MouseWheel>", _left_wheel)
        left.bind("<MouseWheel>", _left_wheel)

        def _btn(parent, label, fn, tip=""):
            f = ttk.Frame(parent)
            f.pack(fill="x", pady=1)
            ttk.Button(f, text=label, width=26, command=fn).pack(side="left")
            if tip:
                ttk.Label(f, text=tip, foreground="gray",
                          font=("Arial", 8)).pack(side="left", padx=6)

        # ── System Identity ───────────────────────────────────────────────
        idf = ttk.LabelFrame(left, text="System Identity & Status", padding=6)
        idf.pack(fill="x", padx=4, pady=(4, 6))

        _btn(idf, "B  — Get Prober ID",     self._cmd_get_id,      "User-defined label + firmware ver")
        _btn(idf, "ms — Prober Status Code", self._cmd_get_status,  "Current operating mode")
        _btn(idf, "H  — Multi-site Info",    self._cmd_get_multisite,"Multi-site location number")

        # ── Position ──────────────────────────────────────────────────────
        pf = ttk.LabelFrame(left, text="Chuck Position  (read-only)", padding=6)
        pf.pack(fill="x", padx=4, pady=(0, 6))

        _btn(pf, "Q  — Die Coordinates",       self._cmd_xy_position, "Current die X,Y (−99…511; probing-only)")
        _btn(pf, "R  — Absolute Position",     self._cmd_xy_absolute, "In probing area, 0.1 µm units (probing-only)")
        _btn(pf, "q  — Start Die Coordinates", self._cmd_start_die,   "First die XY of current wafer")

        # ── XY Motion ────────────────────────────────────────────────────
        xf = ttk.LabelFrame(left, text="XY Motion", padding=6)
        xf.pack(fill="x", padx=4, pady=(0, 6))

        ttk.Label(xf,
                  text="A — travel BY a distance from the current position (1 µm steps,\n"
                       "±999999). Sent as AY±nnnnnnX±nnnnnn. X+ = leftward, Y+ = backward.\n"
                       "Chuck height is RESTORED after the move — re-contacts if it was up.\n"
                       "Probing-only.",
                  foreground="gray", font=("Arial", 8), justify="left").pack(anchor="w", pady=(0, 4))

        xy_row = ttk.Frame(xf)
        xy_row.pack(fill="x", pady=2)
        ttk.Label(xy_row, text="dX:", width=4).pack(side="left")
        self._move_x_var = tk.StringVar(value="0")
        ttk.Entry(xy_row, textvariable=self._move_x_var, width=9).pack(side="left", padx=2)
        ttk.Label(xy_row, text="µm   dY:", width=8).pack(side="left")
        self._move_y_var = tk.StringVar(value="0")
        ttk.Entry(xy_row, textvariable=self._move_y_var, width=9).pack(side="left", padx=2)
        ttk.Label(xy_row, text="µm").pack(side="left")

        ttk.Button(xf, text="▶  Travel by Distance  (A)", command=self._cmd_move_xy).pack(fill="x", pady=(6, 4))

        ttk.Separator(xf, orient="horizontal").pack(fill="x", pady=6)

        ttk.Label(xf,
                  text="S — RELATIVE travel by DIE INDEXES (whole dies, not µm; ±9999).\n"
                       "Sent as SY±nnnnX±nnnn. Chuck height restored after. Probing-only.",
                  foreground="gray", font=("Arial", 8), justify="left").pack(anchor="w", pady=(0, 4))

        s_row = ttk.Frame(xf)
        s_row.pack(fill="x", pady=2)
        ttk.Label(s_row, text="dX:", width=4).pack(side="left")
        self._step_x_var = tk.StringVar(value="0")
        ttk.Entry(s_row, textvariable=self._step_x_var, width=9).pack(side="left", padx=2)
        ttk.Label(s_row, text="dies  dY:", width=9).pack(side="left")
        self._step_y_var = tk.StringVar(value="0")
        ttk.Entry(s_row, textvariable=self._step_y_var, width=9).pack(side="left", padx=2)
        ttk.Label(s_row, text="dies").pack(side="left")

        ttk.Button(xf, text="▶  Step by Dies  (S)", command=self._cmd_step_dies).pack(fill="x", pady=(6, 4))

        ttk.Separator(xf, orient="horizontal").pack(fill="x", pady=6)

        ttk.Label(xf,
                  text="J — position a target die at ABSOLUTE die map coordinates\n"
                       "(−99…511). Sent as JYyyyXxxx (3 chars each). Chuck height\n"
                       "restored after. Probing-only.",
                  foreground="gray", font=("Arial", 8), justify="left").pack(anchor="w", pady=(0, 4))

        j_row = ttk.Frame(xf)
        j_row.pack(fill="x", pady=2)
        ttk.Label(j_row, text="X:", width=4).pack(side="left")
        self._die_x_var = tk.StringVar(value="0")
        ttk.Entry(j_row, textvariable=self._die_x_var, width=9).pack(side="left", padx=2)
        ttk.Label(j_row, text="die   Y:", width=8).pack(side="left")
        self._die_y_var = tk.StringVar(value="0")
        ttk.Entry(j_row, textvariable=self._die_y_var, width=9).pack(side="left", padx=2)
        ttk.Label(j_row, text="die").pack(side="left")

        ttk.Button(xf, text="▶  Go To Die  (J)", command=self._cmd_go_to_die).pack(fill="x", pady=(6, 4))

        ttk.Separator(xf, orient="horizontal").pack(fill="x", pady=6)

        ttk.Label(xf,
                  text="I — set die pitch / index size (1 µm steps, sent as IYyyyyyXxxxxx).\n"
                       "Only accepted while waiting for lot process start; wafer and\n"
                       "probe-pad alignment must be redone afterwards.",
                  foreground="gray", font=("Arial", 8), justify="left").pack(anchor="w", pady=(0, 4))

        pitch_row = ttk.Frame(xf)
        pitch_row.pack(fill="x", pady=2)
        ttk.Label(pitch_row, text="X:", width=4).pack(side="left")
        self._pitch_x_var = tk.StringVar(value="1000")
        ttk.Entry(pitch_row, textvariable=self._pitch_x_var, width=9).pack(side="left", padx=2)
        ttk.Label(pitch_row, text="µm   Y:", width=8).pack(side="left")
        self._pitch_y_var = tk.StringVar(value="1000")
        ttk.Entry(pitch_row, textvariable=self._pitch_y_var, width=9).pack(side="left", padx=2)
        ttk.Label(pitch_row, text="µm").pack(side="left")

        ttk.Button(xf, text="Set Index / Pitch  (I)", command=self._cmd_set_index).pack(fill="x", pady=(6, 0))

        # ── Errors ────────────────────────────────────────────────────────
        ef = ttk.LabelFrame(left, text="Errors  (use when STB=76)", padding=6)
        ef.pack(fill="x", padx=4, pady=(0, 6))

        _btn(ef, "E  — Short Error Code",   self._cmd_error_code, "Brief code")
        _btn(ef, "e  — Full Error Message", self._cmd_error_msg,  "Human-readable description")
        _btn(ef, "🔕 Buzzer Clear (E + es)", self._cmd_buzzer_clear,
             "Read error code, then clear alarm / silence buzzer (STB 119)")

        # ── Motion Commands ───────────────────────────────────────────────
        sf = ttk.LabelFrame(left, text="Motion Commands", padding=6)
        sf.pack(fill="x", padx=4, pady=(0, 4))

        ttk.Label(sf,
                  text="The CHUCK moves in Z, not the probe card:\n"
                       "Z (Z Up) = chuck rises to probing height + overdrive\n"
                       "    → wafer TOUCHES the probe card  ⚠\n"
                       "D (Z Down) = chuck drops → wafer separates (safe direction).\n"
                       "Z, D, Next Die: all probing-only.",
                  foreground="gray", font=("Arial", 8), justify="left").pack(anchor="w", pady=(0, 4))

        r1 = ttk.Frame(sf); r1.pack(fill="x", pady=1)
        ttk.Button(r1, text="⬆  Contact — Z Up  (Z)  ⚠",
                   command=self._cmd_z_up).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(r1, text="⬇  Separate — Z Down  (D)",
                   command=self._cmd_z_down).pack(side="left", expand=True, fill="x", padx=(2, 0))

        r2 = ttk.Frame(sf); r2.pack(fill="x", pady=1)
        ttk.Button(r2, text="▶▶  Next Die  (J)",
                   command=self._cmd_next_die).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(r2, text="⏹  Emergency Stop  (K)",
                   command=self._cmd_stop).pack(side="left", expand=True, fill="x", padx=(2, 0))

        r3 = ttk.Frame(sf); r3.pack(fill="x", pady=1)
        ttk.Button(r3, text="⏏  Unload Wafer  (U)",
                   command=self._cmd_unload).pack(side="left", expand=True, fill="x")

    # ── Right pane ────────────────────────────────────────────────────────────

    def _build_right(self, pane):
        right = ttk.Frame(pane, padding=4)
        pane.add(right, weight=1)
        right.rowconfigure(4, weight=1)
        right.columnconfigure(0, weight=1)

        # ── Z & Die Status ────────────────────────────────────────────────
        # Z state is NOT queryable on the prober — this shows the state the
        # driver tracked from Z/D/motion completion STBs.
        zf = ttk.LabelFrame(right, text="Z Status (tracked from replies) & Die", padding=6)
        zf.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        zf.columnconfigure(1, weight=1)

        z_top = ttk.Frame(zf)
        z_top.pack(fill="x")
        self._z_dot = tk.Label(z_top, text="  ", bg="#94a3b8", width=2,
                               relief="flat", font=("Consolas", 10))
        self._z_dot.pack(side="left", padx=(0, 6))
        self._z_text_var = tk.StringVar(value="Z unknown — no Z/D/motion reply seen yet")
        ttk.Label(z_top, textvariable=self._z_text_var,
                  font=("Consolas", 9, "bold"), anchor="w").pack(
                  side="left", fill="x", expand=True)
        ttk.Button(z_top, text="↻ Refresh Die Info",
                   command=self._check_z_die).pack(side="right")

        self._die_info_var = tk.StringVar(value="Die: —")
        ttk.Label(zf, textvariable=self._die_info_var,
                  font=("Consolas", 8), foreground="#374151").pack(
                  anchor="w", pady=(3, 0))

        self._xy_var = tk.StringVar(value="XY: —")
        ttk.Label(zf, textvariable=self._xy_var,
                  font=("Consolas", 8), foreground="#374151").pack(anchor="w")

        # ── Lot / Wafer info ──────────────────────────────────────────────
        lf = ttk.LabelFrame(right, text="Lot & Wafer Info", padding=6)
        lf.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        grid = ttk.Frame(lf); grid.pack(fill="x")
        READ_CMDS = [
            ("V  — Lot Number",       self._cmd_lot_number,    "Current lot ID"),
            ("X  — Wafer Number",     self._cmd_wafer_number,  "Wafer index in lot"),
            ("b  — Wafer ID",         self._cmd_wafer_id,      "Barcode / cassette label"),
            ("Y  — Gross Die Count",  self._cmd_gross,         "Total die count on wafer"),
            ("c  — Pass/Fail Counts", self._cmd_pf_counts,     "Running pass & fail totals"),
            ("y  — Yield Data",       self._cmd_yield,         "Yield for current lot"),
            ("w  — Wafer Status",     self._cmd_wafer_status,  "Each slot: processed/pending"),
            ("x  — Cassette Status",  self._cmd_cassette,      "Wafer presence per slot"),
            ("O  — On-Wafer Info",    self._cmd_on_wafer,      "Current die (probing only)"),
        ]
        for ri, (label, fn, tip) in enumerate(READ_CMDS):
            r, c = divmod(ri, 2)
            btn = ttk.Button(grid, text=label, width=22, command=fn)
            btn.grid(row=r, column=c*2, padx=(2, 0), pady=2, sticky="ew")
            ttk.Label(grid, text=tip, foreground="gray",
                      font=("Arial", 8), anchor="w").grid(
                      row=r, column=c*2+1, padx=(2, 8), sticky="w")
            grid.columnconfigure(c*2, weight=1)

        # ── Last Response ─────────────────────────────────────────────────
        rf = ttk.LabelFrame(right, text="Last Response", padding=6)
        rf.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self._resp_var = tk.StringVar(value="—")
        ttk.Label(rf, textvariable=self._resp_var,
                  font=("Consolas", 9), foreground="#0077cc",
                  wraplength=380, justify="left").pack(anchor="w")

        # ── Raw GPIB Terminal ─────────────────────────────────────────────
        tf = ttk.LabelFrame(right, text="Raw GPIB Terminal", padding=6)
        tf.grid(row=3, column=0, sticky="ew", pady=(0, 6))

        term = ttk.Frame(tf)
        term.pack(fill="x")

        self._cmd_var = tk.StringVar()
        entry = ttk.Entry(term, textvariable=self._cmd_var, font=("Consolas", 10), width=20)
        entry.pack(side="left", padx=(0, 4))
        entry.bind("<Return>", lambda _e: self._send_raw())
        ttk.Label(term, text="STB:", foreground="gray").pack(side="left")
        self._expect_stb = tk.StringVar(value="")
        ttk.Entry(term, textvariable=self._expect_stb, width=4).pack(side="left", padx=(2, 6))
        ttk.Button(term, text="Send", command=self._send_raw).pack(side="left", padx=2)
        ttk.Label(term, text="⚠ motion cmds ask confirm",
                  foreground="orange", font=("Arial", 8)).pack(side="left", padx=8)

        # ── STB Reference ─────────────────────────────────────────────────
        stb_outer = ttk.LabelFrame(right,
                                   text="STB Code Reference  (factory defaults — may differ if customized)",
                                   padding=4)
        stb_outer.grid(row=4, column=0, sticky="nsew")
        stb_outer.rowconfigure(0, weight=1)
        stb_outer.columnconfigure(0, weight=1)

        stb_canvas = tk.Canvas(stb_outer, highlightthickness=0, bg="#f5f5f5")
        stb_sb = ttk.Scrollbar(stb_outer, orient="vertical", command=stb_canvas.yview)
        stb_canvas.configure(yscrollcommand=stb_sb.set)
        stb_canvas.grid(row=0, column=0, sticky="nsew")
        stb_sb.grid(row=0, column=1, sticky="ns")

        stb_inner = ttk.Frame(stb_canvas)
        _win = stb_canvas.create_window((0, 0), window=stb_inner, anchor="nw")

        _ERROR   = {76}
        _WARNING = {74, 84, 87, 99, 104, 111, 115, 117, 121}
        _OK      = {64, 65, 66, 67, 68, 69, 70, 71, 75, 77, 78, 79, 80,
                    81, 82, 85, 86, 88, 89, 90, 91, 92, 93, 94, 98,
                    100, 101, 103, 105, 107, 108, 109, 110, 113, 114,
                    116, 118, 119, 120, 122, 123}

        for stb, desc in sorted(STB_DESCRIPTIONS.items()):
            row = ttk.Frame(stb_inner)
            row.pack(fill="x", pady=0)
            color = ("red"    if stb in _ERROR
                     else "orange" if stb in _WARNING
                     else "#228822")
            ttk.Label(row, text=f"{stb:3d} (0x{stb:02X})", width=10,
                      font=("Consolas", 8), foreground=color, anchor="w").pack(side="left", padx=(2, 0))
            ttk.Label(row, text=desc, font=("Arial", 8),
                      foreground=color, anchor="w").pack(side="left", padx=2)

        stb_inner.bind("<Configure>",
                       lambda e: stb_canvas.configure(scrollregion=stb_canvas.bbox("all")))
        stb_canvas.bind("<Configure>",
                        lambda e: (stb_canvas.configure(scrollregion=stb_canvas.bbox("all")),
                                   stb_canvas.itemconfig(_win, width=e.width)))
        stb_canvas.bind_all("<MouseWheel>",
                            lambda e: stb_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ── Read-only command handlers ────────────────────────────────────────────

    def _cmd_read_stb(self):
        # Refresh the tracked-Z display too — motion handlers and the
        # auto-poll all funnel through here after commands complete.
        self._update_z_display()
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                stb, desc = drv.read_stb_decoded()
                binary = f"{stb:08b}b"
                color  = ("red" if stb == 76 else
                           "orange" if stb in {74, 84, 87, 99} else "#22bb55")
                msg = f"STB {stb}  (0x{stb:02X}  {binary})   {desc}"
                self._log(f"[PROBER] {msg}")
                self.after(0, lambda: self._set_stb(msg, color))
            except Exception as e:
                self._log(f"[PROBER] STB error: {e}")
                self.after(0, lambda: self._set_stb(f"STB error: {e}", "red"))
        self._run_bg(_run)

    def _make_reader(self, method: str, label: str):
        def handler():
            def _run():
                drv = self._drv()
                if drv:
                    self._safe_query(drv, method, label)
            self._run_bg(_run)
        return handler

    _cmd_get_id       = property(lambda self: self._make_reader("get_prober_id",       "B"))
    _cmd_get_status   = property(lambda self: self._make_reader("get_prober_status",   "ms"))
    _cmd_get_multisite= property(lambda self: self._make_reader("get_multisite_info",  "H"))
    _cmd_xy_position  = property(lambda self: self._make_reader("get_xy_position",     "Q"))
    _cmd_xy_absolute  = property(lambda self: self._make_reader("get_xy_absolute",     "R"))
    _cmd_start_die    = property(lambda self: self._make_reader("get_start_die_coords","q"))
    _cmd_error_code   = property(lambda self: self._make_reader("get_error_code",      "E"))
    _cmd_error_msg    = property(lambda self: self._make_reader("get_error_message",   "e"))
    _cmd_lot_number   = property(lambda self: self._make_reader("get_lot_number",      "V"))
    _cmd_wafer_number = property(lambda self: self._make_reader("get_wafer_number",    "X"))
    _cmd_wafer_id     = property(lambda self: self._make_reader("get_wafer_id",        "b"))
    _cmd_gross        = property(lambda self: self._make_reader("get_gross_value",     "Y"))
    _cmd_pf_counts    = property(lambda self: self._make_reader("get_pass_fail_counts","c"))
    _cmd_yield        = property(lambda self: self._make_reader("get_yield_data",      "y"))
    _cmd_wafer_status = property(lambda self: self._make_reader("get_wafer_status",    "w"))
    _cmd_cassette     = property(lambda self: self._make_reader("get_cassette_status", "x"))
    _cmd_on_wafer     = property(lambda self: self._make_reader("get_on_wafer_info",   "O"))

    # ── Z & Die status ────────────────────────────────────────────────────────

    def _update_z_display(self):
        """Show the driver's tracked Z state. Must run on the UI thread.

        There is no 'is the chuck up?' request on the prober — the driver
        tracks Z from the completion STB of each Z/D/motion command.
        """
        drv = self._drv(silent=True)
        z = getattr(drv, "z_is_up", None) if drv else None
        if drv is None:
            self._z_dot.config(bg="#94a3b8")
            self._z_text_var.set("Z — prober not connected")
        elif z is True:
            self._z_dot.config(bg="#dc2626")
            self._z_text_var.set("Z UP — wafer IN CONTACT with probe card ⚠")
        elif z is False:
            self._z_dot.config(bg="#22c55e")
            self._z_text_var.set("Z DOWN — wafer separated (safe)")
        else:
            self._z_dot.config(bg="#94a3b8")
            self._z_text_var.set("Z unknown — send D (Separate) to establish a known state")

    def _check_z_die(self):
        self._update_z_display()
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                info = drv.get_on_wafer_info()
                self.after(0, lambda v=info: self._die_info_var.set(
                    f"Die: {v}" if v else "Die: (not in probing)"))
            except Exception:
                self.after(0, lambda: self._die_info_var.set("Die: —"))
            try:
                xy = drv.get_xy_position()
                self.after(0, lambda v=xy: self._xy_var.set(
                    f"XY: {v}" if v else "XY: —"))
            except Exception:
                self.after(0, lambda: self._xy_var.set("XY: —"))
        self._run_bg(_run)

    # ── XY motion handlers ────────────────────────────────────────────────────

    def _cmd_move_xy(self):
        try:
            dx = int(round(float(self._move_x_var.get())))
            dy = int(round(float(self._move_y_var.get())))
        except ValueError:
            messagebox.showerror("Invalid Input", "dX and dY must be numeric values in µm.")
            return
        if not (-999999 <= dx <= 999999 and -999999 <= dy <= 999999):
            messagebox.showerror("Invalid Input", "A: travel distance must be within ±999999 µm.")
            return
        if not messagebox.askyesno(
            "Travel by Distance (A)",
            f"Send  AY{dy:+07d}X{dx:+07d}  ?\n\n"
            f"Chuck travels BY dX={dx} µm, dY={dy} µm from the current position\n"
            "(X+ = leftward, Y+ = backward).\n\n"
            "⚠ Chuck height is RESTORED after the move — if the wafer was in\n"
            "contact with the probe card, it RE-CONTACTS at the new position.\n"
            "Only valid during active probing."
        ):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log(f"[PROBER] >> AY{dy:+07d}X{dx:+07d}  (travel by distance)")
                stb = drv.move_xy_absolute(dx, dy)
                height = "UP (in contact)" if stb == 67 else "DOWN"
                self._log(f"[PROBER] Travel complete — dX={dx} dY={dy} µm, chuck {height}")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Travel error: {e}")
        self._run_bg(_run)

    def _cmd_step_dies(self):
        try:
            dx = int(self._step_x_var.get())
            dy = int(self._step_y_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "dX and dY must be whole numbers of dies.")
            return
        if not (-9999 <= dx <= 9999 and -9999 <= dy <= 9999):
            messagebox.showerror("Invalid Input", "S: travel must be within ±9999 die indexes.")
            return
        if not messagebox.askyesno(
            "Step by Dies (S)",
            f"Send  SY{dy:+05d}X{dx:+05d}  ?\n\n"
            f"Chuck travels BY {dx} die(s) in X and {dy} die(s) in Y\n"
            "(directions per the prober's Set-up Sequence Settings).\n\n"
            "⚠ Chuck height is RESTORED after the move — if the wafer was in\n"
            "contact with the probe card, it RE-CONTACTS at the new position.\n"
            "Only valid during active probing."
        ):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log(f"[PROBER] >> SY{dy:+05d}X{dx:+05d}  (travel by die indexes)")
                stb = drv.move_xy_relative(dx, dy)
                height = "UP (in contact)" if stb == 67 else "DOWN"
                self._log(f"[PROBER] Step complete — dX={dx} dY={dy} dies, chuck {height}")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Step error: {e}")
        self._run_bg(_run)

    def _cmd_go_to_die(self):
        try:
            x = int(self._die_x_var.get())
            y = int(self._die_y_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Die X and Y must be whole numbers.")
            return
        if not (-99 <= x <= 511 and -99 <= y <= 511):
            messagebox.showerror("Invalid Input", "J: die coordinates must be within −99…511.")
            return
        if not messagebox.askyesno(
            "Go To Die (J)",
            f"Send  JY{y:03d}X{x:03d}  ?\n\n"
            f"Positions the die at ABSOLUTE map coordinates X={x}, Y={y}.\n\n"
            "⚠ Chuck height is RESTORED after the move — if the wafer was in\n"
            "contact with the probe card, it RE-CONTACTS at the new die.\n"
            "Only valid during active probing."
        ):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log(f"[PROBER] >> JY{y:03d}X{x:03d}  (position target die)")
                stb = drv.move_to_die_xy(x, y)
                if stb == 81:
                    self._log(f"[PROBER] At die X={x} Y={y} — wafer end die (STB=81)")
                else:
                    height = "UP (in contact)" if stb == 67 else "DOWN"
                    self._log(f"[PROBER] At die X={x} Y={y} — chuck {height}")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Go to die error: {e}")
        self._run_bg(_run)

    def _cmd_set_index(self):
        try:
            px = int(round(float(self._pitch_x_var.get())))
            py = int(round(float(self._pitch_y_var.get())))
        except ValueError:
            messagebox.showerror("Invalid Input", "Pitch X and Y must be numeric values in µm.")
            return
        if not (0 <= px <= 99999 and 0 <= py <= 99999):
            messagebox.showerror("Invalid Input", "I: index sizes must be 0–99999 µm.")
            return
        if not messagebox.askyesno(
            "Set Index / Pitch (I)",
            f"Send  IY{py:05d}X{px:05d}  ?\n\n"
            "Only accepted while the prober is waiting for lot process start.\n"
            "Wafer alignment and probe-pad alignment must be redone afterwards."
        ):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log(f"[PROBER] >> IY{py:05d}X{px:05d}  (index size setting)")
                drv.set_index_size(px, py)
                self._log(f"[PROBER] Index set — X={px} µm  Y={py} µm  (STB=77). "
                          "Re-run wafer + probe-pad alignment.")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Set index error: {e}")
        self._run_bg(_run)

    # ── Motion handlers ───────────────────────────────────────────────────────

    def _cmd_z_up(self):
        if not messagebox.askyesno(
            "Contact — Z Up (Z)",
            "Send Z (Z UP)?\n\n"
            "⚠ CONTACT: the CHUCK RISES to Probing Height INCLUDING OVERDRIVE —\n"
            "the wafer TOUCHES the probe card needles.\n\n"
            "Confirm the wafer and needles are aligned and contact is intended.\n"
            "Only valid during active probing (command error while idle)."
        ):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log("[PROBER] >> Z  (Z Up — chuck rises, wafer CONTACTS probe card)")
                drv.z_up()
                self._log("[PROBER] Z Up complete — wafer in contact (STB=67)")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Z Up error: {e}")
        self._run_bg(_run)

    def _cmd_z_down(self):
        if not messagebox.askyesno(
            "Separate — Z Down (D)",
            "Send D (Z DOWN)?\n\n"
            "The chuck DROPS away from the probe card — the wafer SEPARATES\n"
            "from the needles. This is the safe direction.\n\n"
            "Only valid during active probing (command error while idle)."
        ):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log("[PROBER] >> D  (Z Down — chuck drops, wafer separates)")
                drv.z_down()
                self._log("[PROBER] Z Down complete — wafer separated (STB=68)")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Z Down error: {e}")
        self._run_bg(_run)

    def _cmd_next_die(self):
        if not messagebox.askyesno(
            "Next Die (J)",
            "Send J (Position Next Die)?\n\n"
            "Chuck goes DOWN, steps to the next testing die, then RETURNS to\n"
            "its previous height — if the wafer was in contact before, it\n"
            "RE-CONTACTS at the new die. Send D (Separate) first if contact\n"
            "after the step is not wanted.\n\n"
            "Only valid during active probing.\n"
            "STB: 66 = done chuck down, 67 = done chuck up, 81 = wafer end."
        ):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log("[PROBER] >> J  (Next Die)")
                stb = drv.next_die()
                if stb == 81:
                    self._log("[PROBER] Wafer end (STB=81) — no more dice to test")
                elif stb == 90:
                    self._log("[PROBER] Probing stop (STB=90) — <STOP> pushed; "
                              "press START on the prober to continue")
                else:
                    height = "UP (in contact)" if stb == 67 else "DOWN"
                    self._log(f"[PROBER] Stepped to next die — chuck {height}")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Next die error: {e}")
        self._run_bg(_run)

    def _cmd_unload(self):
        if not messagebox.askyesno(
            "Unload Wafer (U)",
            "Send U (Unload Wafer)?\n\n"
            "Releases the current wafer from the chuck back to the cassette.\n"
            "This ends probing on this wafer — confirm testing is actually done.\n\n"
            "STB=71 confirms unloading done."
        ):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log("[PROBER] >> U  (Unload Wafer)")
                stb = drv.unload_wafer()
                self._log(f"[PROBER] Wafer unloaded (STB={stb})")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Unload error: {e}")
        self._run_bg(_run)

    def _cmd_buzzer_clear(self):
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log("[PROBER] >> E + es  (Buzzer Clear — read error, clear alarm)")
                code = drv.buzzer_clear()
                msg = f"error code: {code}" if code else "no pending error code"
                self._log(f"[PROBER] Buzzer Clear done — {msg}")
                self.after(0, lambda m=msg: self._show_response("E+es", m))
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Buzzer Clear error: {e}")
        self._run_bg(_run)

    def _cmd_stop(self):
        if not messagebox.askyesno("Emergency Stop",
                                   "Send K (Stop)?\n\nHalts current prober operation.\n"
                                   "Does NOT unload wafer. Resume with START button on prober."):
            return
        def _run():
            drv = self._drv()
            if not drv:
                return
            try:
                self._log("[PROBER] >> K  (Emergency Stop)")
                drv.emergency_stop()
                self._log("[PROBER] Stop confirmed (STB=85)")
                self.after(0, self._cmd_read_stb)
            except Exception as e:
                self._log(f"[PROBER] Stop error: {e}")
        self._run_bg(_run)

    # ── Raw terminal ──────────────────────────────────────────────────────────

    def _send_raw(self):
        raw = self._cmd_var.get().strip()
        if not raw:
            return

        # Mnemonics are case-sensitive on this prober ('Z' Z-UP ≠ 'z' set
        # contact height, 'E' error code ≠ 'e' error message) — never upper().
        mn = _mnemonic(raw)

        if mn in _MOTION_CMDS:
            motion_names = {
                "A": "XY travel BY a distance (µm)",
                "C": "Marking",                "M": "Marking",
                "D": "Z Down — chuck drops, wafer SEPARATES from probe card",
                "G": "Position start die (resets PASS/FAIL counters)",
                "J": "Position next / target die",
                "S": "XY travel by die indexes",
                "K": "Stop prober operation",
                "L": "Load/align wafer",       "U": "Unload wafer",
                "N": "Alignment retry",        "W": "Needle cleaning",
                "Z": "Z Up — chuck rises, wafer CONTACTS probe card ⚠",
                "Z+": "Chuck height fine adjust (up)",
                "Z-": "Chuck height fine adjust (down)",
                "jc": "Needle cleaning",       "j2": "Load specified wafer",
            }
            label = motion_names.get(mn, mn)
            if not messagebox.askyesno("Motion Command",
                                       f"'{raw}' → {label}\n\nThis causes physical prober motion.\n"
                                       "Send anyway?"):
                return

        if mn in _PROBING_ONLY:
            messagebox.showwarning("Probing-Only Command",
                                   f"'{mn}' is only valid during active probing.\n"
                                   "Sending it while idle will cause a GP-IB Execution Condition Error.")

        def _run(cmd=raw, mnemonic=mn):
            drv = self._drv()
            if not drv:
                return
            try:
                self._log(f"[PROBER] >> {cmd!r}")
                expect_str = self._expect_stb.get().strip()

                # Only data-request commands answer as Talker; querying an
                # action command would time out AND still execute it — so
                # route by mnemonic instead of trying query first.
                if mnemonic in _QUERY_CMDS:
                    resp = drv.inst.query(cmd)
                    self._log(f"[PROBER] << {resp!r}")
                    self.after(0, lambda r=resp: self._resp_var.set(f"[{cmd}] {r}"))
                    return

                drv.inst.write(cmd)
                if expect_str and expect_str.isdigit():
                    tgt = int(expect_str)
                    start = time.time()
                    while time.time() - start < 15:
                        stb = drv.inst.read_stb()
                        if stb == tgt:
                            self._log(f"[PROBER] STB={stb} received ✓")
                            # Completion STBs carry the only Z information the
                            # prober gives — keep the tracked state current.
                            if stb == 67:
                                drv.z_is_up = True
                            elif stb in (65, 66, 68, 70, 90):
                                drv.z_is_up = False
                            self.after(0, lambda s=stb: self._resp_var.set(f"STB={s} ✓"))
                            self.after(0, self._cmd_read_stb)
                            return
                        if stb == 76:
                            self._log("[PROBER] ⚠  ALARM — STB=76")
                            drv.z_is_up = None
                            self.after(0, lambda: self._set_stb("⚠ ALARM STB=76", "red"))
                            self.after(0, self._update_z_display)
                            return
                        time.sleep(0.05)
                    self._log("[PROBER] Timeout waiting for STB")
                    if mnemonic in _MOTION_CMDS:
                        drv.z_is_up = None
                        self.after(0, self._update_z_display)
                else:
                    self._log("[PROBER] Write sent (no STB wait)")
                    if mnemonic in _MOTION_CMDS:
                        # Motion sent without confirming completion — the chuck
                        # height can no longer be trusted until the next reply.
                        drv.z_is_up = None
                        self.after(0, self._update_z_display)
                    self.after(0, lambda: self._resp_var.set("Write sent — no response expected"))
            except Exception as e:
                self._log(f"[PROBER] ERROR: {e}")
                self.after(0, lambda: self._resp_var.set(f"Error: {e}"))
        self._run_bg(_run)

    # ── Auto-poll ─────────────────────────────────────────────────────────────

    def _toggle_poll(self):
        if self._poll_var.get():
            self._polling = True
            self._poll_tick()
        else:
            self._polling = False
            if self._poll_job:
                self.after_cancel(self._poll_job)
                self._poll_job = None

    def _poll_tick(self):
        if not self._polling:
            return
        self._cmd_read_stb()
        self._poll_job = self.after(1000, self._poll_tick)
