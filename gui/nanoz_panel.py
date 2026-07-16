"""NanoZ tab — alternate measurement setup using up to 6 NanoZ EK-IV
evaluation boards over serial COM ports instead of the Keithley/Keysight
GPIB instruments the Main/Debug tabs drive. Board discovery + the SPL/ENV
streaming protocol live in instruments/nanoz_board.py (ported from the
reference CLI tool gds/nanoz_ekiv_run_collect.py); this module is the Tk
UI plus the die-to-die lot sequencing described in the integration
workflow (Phases 1-6): discover/connect boards, hand-shake with the
Accretech prober's cassette workflow (STB 65/66/67), trigger/halt the
heaters once per touchdown, and drain the boards' data queue into CSV +
a live wafer map.

This is a self-contained, additive tab — it shares the prober connection
(self.controller.drivers["prober"]) with the rest of the app so the same
physical GPIB session is reused rather than opened twice, but it does not
touch the Main/Debug tabs' own state, wafer map, recipe, or run logic.
The one exception is one-directional: instrument_panel.py's
load_ata_folder calls this panel's on_ata_folder_loaded(folder_path) so
its own wafer map (Run tab) auto-populates the same way every other
tab's map does — nothing here reaches back into Main/Debug.
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import os
import queue
import random
import re
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from wafer_map_view import WaferMapPanel
from instruments.accretech_uf200r import AccretechUF200R
import instruments.nanoz_board as nzb

# Charts tab — same defensive/optional matplotlib pattern as
# gui/pma_wafer_panel.py so a missing install degrades to a message
# instead of breaking the whole NanoZ tab.
try:
    import matplotlib
    try:
        matplotlib.use("TkAgg")
    except Exception:
        pass
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    _MPL = True
except ImportError:
    _MPL = False

# Accretech Q-command response parser, duplicated (not imported) from
# instrument_panel.py's module-level _parse_q_response to avoid a circular
# import (instrument_panel constructs this panel) — keep byte-identical
# behavior if that one ever changes: "QY<3>X<3>" die-map coords, Y before
# X on the wire, returns (x_die, y_die).
_Q_RESPONSE_RE = re.compile(r'Y\s*([+-]?\d+)\s*X\s*([+-]?\d+)')


def _parse_q_response(raw: str):
    raw = (raw or "").strip()
    m = _Q_RESPONSE_RE.search(raw)
    if m:
        return float(m.group(2)), float(m.group(1))
    parts = re.findall(r'[+-]?\d+\.?\d*', raw)
    if len(parts) >= 2:
        return float(parts[1]), float(parts[0])
    raise ValueError(f"Cannot parse Q response: {raw!r}")


class NanoZPanel(ttk.Frame):
    def __init__(self, parent, controller, main_layout):
        super().__init__(parent)
        self.controller = controller
        # Direct reference to the MainLayout instance (not routed through
        # controller.ui) so this works even before AtomicaDashboard has
        # finished wiring self.ui — see instrument_panel.py's _tab_nanoz.
        self._main_layout = main_layout

        self._boards: dict[str, nzb.NanoZBoard] = {}   # port -> NanoZBoard
        self._board_rows: dict[str, str] = {}           # port -> Treeview iid
        self._queue: "queue.Queue" = queue.Queue()

        self._running = False
        self._run_mode: str | None = None   # None | "full" | "test" — which run loop owns self._running
        self._lot_thread: threading.Thread | None = None
        self._current_rc = (None, None)   # (row, col) of the die under test
        self._touchdown_errors = 0
        self._touchdown_packets = 0
        self._spl_total = 0
        self._env_total = 0
        # Running per-lot tally — mirrors Main's "▶ Run" tab Pass/Fail
        # LabelFrame (instrument_panel.py _tab_execution2), reset at the
        # start of each lot; see _reset_counts/_mark_touchdown_result.
        self._pass_count = 0
        self._fail_count = 0
        self._spl_path: str | None = None
        self._env_path: str | None = None
        # Latest decoded packet per board (port -> dict), for the Board
        # Console tab's live "Latest Reading" display — see _handle_packet.
        self._latest_spl: dict[str, dict] = {}
        self._latest_env: dict[str, dict] = {}
        # Rolling per-board sample history (port -> deque[dict]), for the
        # Charts tab — bounded so a long-running lot can't grow this
        # unboundedly; see _handle_packet.
        self._spl_history: dict[str, "collections.deque"] = {}
        self._env_history: dict[str, "collections.deque"] = {}

        self._build_ui()
        self.after(50, self._check_queue)
        self.after(300, self._refresh_charts_loop)

    # ------------------------------------------------------------------
    # UI — a sub-notebook (Setup / Run / Board Console) over a shared log,
    # the same nested-tab pattern Main/Debug already use. Setup owns board
    # discovery/connection, the prober connection, and the wafer map;
    # Run is just the lot-parameters + start/stop + live status; Board
    # Console is for testing individual protocol commands against one
    # board without running a full lot (see references/ NanoZ Protocol +
    # EK-IV User Manual).
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Vertical sash between the sub-tabs and the shared log — drag to
        # resize instead of the old fixed 3:1 split.
        outer = ttk.PanedWindow(self, orient="vertical")
        outer.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self._outer_pane = outer

        sub_nb = ttk.Notebook(outer)
        self._sub_nb = sub_nb
        outer.add(sub_nb, weight=3)

        self._build_setup_tab(sub_nb)
        self._build_run_tab(sub_nb)
        self._build_console_tab(sub_nb)
        self._build_charts_tab(sub_nb)

        # ── Shared log — visible regardless of which sub-tab is active ───
        log_frame = ttk.LabelFrame(outer, text="NanoZ Log")
        outer.add(log_frame, weight=1)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, bg="#1e1e1e", fg="#7CFC00",
                                font=("Consolas", 9), wrap="word", state="disabled", height=8)
        log_sb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_sb.set)
        log_sb.grid(row=0, column=1, sticky="ns", pady=2)
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=(2, 0), pady=2)

    def _build_setup_tab(self, nb):
        """Board discovery/connection and the prober connection — one-time
        setup before running lots. The wafer map lives on the Run tab
        instead (auto-loaded whenever an ATA folder is picked from the
        toolbar, same fan-out every other tab's map already gets — see
        NanoZPanel.on_ata_folder_loaded / instrument_panel.load_ata_folder),
        next to the controls that actually drive it during a lot — same
        idea as Main's own "▶ Run" tab (instrument_panel.py
        _tab_execution2)."""
        tab = ttk.Frame(nb)
        nb.add(tab, text="Setup")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        # Vertical sash — drag to give the boards list more/less room.
        split = ttk.PanedWindow(tab, orient="vertical")
        split.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        boards_lf = ttk.LabelFrame(split, text="NanoZ Boards  (double-click a row to toggle Use)")
        split.add(boards_lf, weight=3)

        brow = ttk.Frame(boards_lf)
        brow.pack(fill="x", padx=6, pady=(6, 2))
        self._btn_discover = ttk.Button(brow, text="🔍 Discover Boards", command=self._discover_boards)
        self._btn_discover.pack(side="left", padx=(0, 4))
        self._btn_connect_boards = ttk.Button(brow, text="🔌 Connect Selected", command=self._connect_boards)
        self._btn_connect_boards.pack(side="left", padx=4)
        self._btn_disconnect_boards = ttk.Button(brow, text="🔌 Disconnect Boards",
                                                 command=self._disconnect_boards)
        self._btn_disconnect_boards.pack(side="left", padx=4)
        self._btn_refresh_status = ttk.Button(brow, text="🔄 Refresh Status",
                                              command=self._refresh_board_status)
        self._btn_refresh_status.pack(side="left", padx=4)
        ttk.Separator(brow, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(brow, text="ENV interval (s):").pack(side="left")
        self.env_interval_var = tk.StringVar(value="1.0")
        ttk.Entry(brow, textvariable=self.env_interval_var, width=6).pack(side="left", padx=(4, 0))

        cols = ("port", "sn", "fw", "sig", "use", "status", "spl", "env")
        self._board_tree = ttk.Treeview(boards_lf, columns=cols, show="headings", height=6)
        heads = [("port", "Port", 70), ("sn", "S/N", 100), ("fw", "Firmware", 80),
                 ("sig", "Signature", 70), ("use", "Use", 45), ("status", "Status", 100),
                 ("spl", "SPL#", 55), ("env", "ENV#", 55)]
        for cid, text, width in heads:
            self._board_tree.heading(cid, text=text)
            self._board_tree.column(cid, width=width, anchor="center" if cid != "sn" else "w")
        self._board_tree.pack(fill="x", padx=6, pady=6)
        self._board_tree.bind("<Double-1>", self._on_board_row_toggle)

        prober_lf = ttk.LabelFrame(split, text="Prober")
        split.add(prober_lf, weight=1)
        prow = ttk.Frame(prober_lf)
        prow.pack(fill="x", padx=6, pady=6)
        self._btn_connect_prober = ttk.Button(prow, text="🔌 Connect Prober", command=self._connect_prober)
        self._btn_connect_prober.pack(side="left", padx=(0, 8))
        self.prober_status_var = tk.StringVar(value="Prober: not connected")
        ttk.Label(prow, textvariable=self.prober_status_var, foreground="#6b7280").pack(side="left")

    def _build_run_tab(self, nb):
        """Lot parameters, start/stop, live status, the running pass/fail
        tally, and the wafer map — everything you watch or interact with
        WHILE a lot runs, assuming Setup has already been done. The
        wafer map auto-loads from whichever ATA folder is active (see
        on_ata_folder_loaded) with a manual reload button here as a
        fallback, same pattern Main's "▶ Run" tab uses for its own map."""
        tab = ttk.Frame(nb)
        nb.add(tab, text="Run")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        # Vertical sash — drag to trade space between the controls above
        # and the wafer map below.
        split = ttk.PanedWindow(tab, orient="vertical")
        split.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        controls = ttk.Frame(split)
        split.add(controls, weight=1)
        controls.columnconfigure(0, weight=1)

        # Every button on this tab lives in this one section, top to
        # bottom: lot parameters -> Full Die/Test Die/Stop Run -> manual
        # chuck controls -> wafer-map/counts utility buttons. Status-only
        # displays (Active Boards, Pass/Fail numbers, the map itself)
        # stay in their own sections below since they're not actions.
        #
        # "Full Die" is the intended NanoZ workflow: the cassette-
        # workflow wafer walk (STB 65/66/67 handshake, _lot_thread_body)
        # already does exactly what running a die looks like in
        # practice — the prober's cassette automation brings the chuck
        # into contact once per die (touchdown), _trigger_cycle_and_wait
        # then fires `run <cycle>` at every connected board in a tight
        # loop (near-simultaneous — one quick serial write per board,
        # so this scales to ~20 boards fine with no threading needed),
        # waits the shared touchdown duration, sends `pause` to every
        # board, and only THEN does cassette_next_die() — which is what
        # separates the chuck (lift off) before advancing. "Test Die" is
        # the same idea over a picked subset, using explicit Z/D/J
        # instead of the cassette handshake — see _test_die_thread_body.
        ctrl_lf = ttk.LabelFrame(controls, text="Controls")
        ctrl_lf.grid(row=0, column=0, sticky="ew")

        prow = ttk.Frame(ctrl_lf)
        prow.pack(fill="x", padx=6, pady=(6, 2))
        ttk.Label(prow, text="Cycle #:").pack(side="left")
        self.cycle_var = tk.StringVar(value="1")
        self._cycle_entry = ttk.Entry(prow, textvariable=self.cycle_var, width=6)
        self._cycle_entry.pack(side="left", padx=(4, 12))
        ttk.Label(prow, text="Touchdown duration (s):").pack(side="left")
        self.duration_var = tk.StringVar(value="10")
        self._duration_entry = ttk.Entry(prow, textvariable=self.duration_var, width=6)
        self._duration_entry.pack(side="left", padx=(4, 0))

        crow = ttk.Frame(ctrl_lf)
        crow.pack(fill="x", padx=6, pady=2)
        self.start_btn = ttk.Button(crow, text="▶ Full Die", command=self._start_lot)
        self.start_btn.pack(side="left", padx=(0, 4))
        self.test_btn = ttk.Button(crow, text="▶ Test Die", command=self._start_test_die)
        self.test_btn.pack(side="left", padx=4)
        self.stop_btn = ttk.Button(crow, text="⏹ Stop Run", command=self._stop_lot, state="disabled")
        self.stop_btn.pack(side="left", padx=4)
        self.state_var = tk.StringVar(value="IDLE")
        ttk.Label(crow, textvariable=self.state_var, font=("Segoe UI", 9, "bold"),
                 foreground="#6b7280").pack(side="left", padx=(12, 4))
        self.die_var = tk.StringVar(value="Die: —")
        ttk.Label(crow, textvariable=self.die_var).pack(side="left", padx=(12, 4))
        self.counts_var = tk.StringVar(value="SPL: 0   ENV: 0")
        ttk.Label(crow, textvariable=self.counts_var, foreground="#0077cc").pack(side="left", padx=(12, 0))

        ttk.Separator(ctrl_lf, orient="horizontal").pack(fill="x", padx=6, pady=4)

        # Manual chuck controls — the die-walk command family (G/Z/D/J),
        # a SEPARATE workflow from Full Die's cassette automation (J/U
        # mean something else there — see accretech_uf200r.py's own
        # "must never be mixed" note on the cassette_* methods). Same
        # idea as Main's "▶ Run" tab manual nav row (instrument_panel.py
        # _tab_execution2) — for spot-checking/homing without starting a
        # real run. Locked out while any NanoZ run is active (_set_locked)
        # so they can never collide with the lot thread on the same GPIB
        # session.
        mrow = ttk.Frame(ctrl_lf)
        mrow.pack(fill="x", padx=6, pady=2)
        self._btn_manual_zup = ttk.Button(mrow, text="⬆ Z Up", command=self._manual_z_up)
        self._btn_manual_zup.pack(side="left", padx=2)
        self._btn_manual_zdown = ttk.Button(mrow, text="⬇ Z Down", command=self._manual_z_down)
        self._btn_manual_zdown.pack(side="left", padx=2)
        self._btn_manual_first_die = ttk.Button(mrow, text="⏮ First Die (G)", command=self._manual_first_die)
        self._btn_manual_first_die.pack(side="left", padx=2)
        self._btn_manual_next_die = ttk.Button(mrow, text="▶▶ Next Die (J)", command=self._manual_next_die)
        self._btn_manual_next_die.pack(side="left", padx=2)
        self._btn_manual_xy = ttk.Button(mrow, text="XY", command=self._manual_xy)
        self._btn_manual_xy.pack(side="left", padx=2)
        self._btn_manual_unload = ttk.Button(mrow, text="⏏ Unload (U)", command=self._manual_unload)
        self._btn_manual_unload.pack(side="left", padx=2)
        self._btn_measure = ttk.Button(mrow, text="Measure", command=self._manual_measure)
        self._btn_measure.pack(side="left", padx=(12, 2))
        self.manual_xy_var = tk.StringVar(value="X: —  Y: —")
        ttk.Label(mrow, textvariable=self.manual_xy_var, foreground="#6b7280").pack(side="left", padx=(12, 0))

        ttk.Separator(ctrl_lf, orient="horizontal").pack(fill="x", padx=6, pady=4)

        # Bench-test the currently active (selected+connected) boards
        # directly — no prober/touchdown involved, just `run <cycle>` /
        # `pause` sent straight to every active board at once, using the
        # same Cycle # as Full Die/Test Die/Measure above. For sanity-
        # checking boards before or between real runs.
        trow = ttk.Frame(ctrl_lf)
        trow.pack(fill="x", padx=6, pady=2)
        self._btn_test_active = ttk.Button(trow, text="▶ Run Cycle (Active Boards)",
                                           command=self._test_active_boards)
        self._btn_test_active.pack(side="left", padx=(0, 4))
        self._btn_pause_active = ttk.Button(trow, text="⏸ Pause (Active Boards)",
                                            command=self._pause_active_boards)
        self._btn_pause_active.pack(side="left", padx=4)

        ttk.Separator(ctrl_lf, orient="horizontal").pack(fill="x", padx=6, pady=4)

        urow = ttk.Frame(ctrl_lf)
        urow.pack(fill="x", padx=6, pady=(2, 6))
        self._btn_reset_counts = ttk.Button(urow, text="Reset Counts", command=self._reset_counts)
        self._btn_reset_counts.pack(side="left")
        self._btn_load_map = ttk.Button(urow, text="📂 Load Accretech Map",
                                        command=self._load_wafer_map)
        self._btn_load_map.pack(side="left", padx=(8, 0))
        self._btn_randomize_sites = ttk.Button(urow, text="🎲 Randomize 5", command=self._randomize_sites)
        self._btn_randomize_sites.pack(side="left", padx=(8, 4))
        self.sites_var = tk.StringVar(value="Test sites: 0 picked (click dies to add/remove)")
        ttk.Label(urow, textvariable=self.sites_var, foreground="#6b7280").pack(side="left")

        status_lf = ttk.LabelFrame(controls, text="Active Boards")
        status_lf.grid(row=1, column=0, sticky="ew", pady=4)
        self.active_boards_var = tk.StringVar(
            value="No boards connected yet — see the Setup tab.")
        ttk.Label(status_lf, textvariable=self.active_boards_var, wraplength=520,
                 justify="left").pack(anchor="w", padx=6, pady=6)

        # Running pass/fail tally — same idea as Main's "▶ Run" tab Pass/
        # Fail LabelFrame (instrument_panel.py _tab_execution2), adapted
        # to NanoZ's per-touchdown result (see _mark_touchdown_result):
        # a touchdown counts PASS if it produced at least one SPL/ENV
        # packet with no checksum/parse errors, FAIL otherwise.
        stat_lf = ttk.LabelFrame(controls, text="Pass / Fail")
        stat_lf.grid(row=2, column=0, sticky="ew", pady=(0, 0))
        srow = ttk.Frame(stat_lf)
        srow.pack(fill="x", padx=6, pady=6)
        ttk.Label(srow, text="PASS:").pack(side="left")
        self.pass_var = tk.StringVar(value="0")
        ttk.Label(srow, textvariable=self.pass_var, font=("Consolas", 16, "bold"),
                 foreground="#16a34a").pack(side="left", padx=(4, 16))
        ttk.Label(srow, text="FAIL:").pack(side="left")
        self.fail_var = tk.StringVar(value="0")
        ttk.Label(srow, textvariable=self.fail_var, font=("Consolas", 16, "bold"),
                 foreground="#dc2626").pack(side="left", padx=(4, 16))
        self.yield_var = tk.StringVar(value="Yield: —")
        ttk.Label(srow, textvariable=self.yield_var, foreground="#6b7280").pack(side="left", padx=(4, 16))

        # Wafer map — auto-loads from the active ATA folder
        # (on_ata_folder_loaded); the Load/Randomize buttons that drive
        # it live in Controls above, this is the visualization only.
        # Click-to-pick site selection (for Test Die) is enabled here —
        # see _on_sites_changed/_randomize_sites.
        map_lf = ttk.LabelFrame(split, text="Wafer Map")
        split.add(map_lf, weight=2)
        map_lf.rowconfigure(0, weight=1)
        map_lf.columnconfigure(0, weight=1)
        self.wafer_map = WaferMapPanel(map_lf)
        self.wafer_map.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.wafer_map.enable_picking(on_change=self._on_sites_changed)

    def _build_console_tab(self, nb):
        """Manual per-command testing against one connected board, without
        running a whole lot — every command documented in references/'s
        NanoZ Protocol (ver, whoami, #env?, calib!, calib ?, cleep) plus a
        raw entry for anything else (manual run/pause on a single board).
        Replies arrive asynchronously through the shared log (see
        NanoZBoard.send_raw) — there's no separate synchronous read, since
        the board's reader thread already owns the port."""
        tab = ttk.Frame(nb)
        nb.add(tab, text="Board Console")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        # Vertical sash — drag to trade space between the command panel
        # above and Latest Reading below.
        split = ttk.PanedWindow(tab, orient="vertical")
        split.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        top = ttk.Frame(split)
        split.add(top, weight=1)
        top.columnconfigure(0, weight=1)

        pick = ttk.Frame(top)
        pick.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(pick, text="Board:").pack(side="left")
        self.console_board_var = tk.StringVar(value="")
        self._console_board_cb = ttk.Combobox(
            pick, textvariable=self.console_board_var, state="readonly", width=14)
        self._console_board_cb.pack(side="left", padx=(4, 12))
        self._console_board_cb.bind("<<ComboboxSelected>>",
                                    lambda _e: self._refresh_console_reading())

        cmds = ttk.LabelFrame(
            top, text="Commands")
        cmds.grid(row=1, column=0, sticky="ew")
        crow1 = ttk.Frame(cmds)
        crow1.pack(fill="x", padx=6, pady=(6, 2))
        ttk.Button(crow1, text="ver", width=10,
                  command=lambda: self._console_send("ver")).pack(side="left", padx=2)
        ttk.Button(crow1, text="whoami", width=10,
                  command=lambda: self._console_send("whoami")).pack(side="left", padx=2)
        ttk.Button(crow1, text="#env?", width=10,
                  command=lambda: self._console_send("#env?")).pack(side="left", padx=2)
        ttk.Button(crow1, text="calib ?", width=10,
                  command=lambda: self._console_send("calib ?")).pack(side="left", padx=2)
        ttk.Button(crow1, text="⚠ calib!", width=10,
                  command=self._console_calib_bang).pack(side="left", padx=2)
        ttk.Button(crow1, text="⚠ cleep", width=10,
                  command=self._console_cleep).pack(side="left", padx=2)

        crow2 = ttk.Frame(cmds)
        crow2.pack(fill="x", padx=6, pady=(2, 6))
        ttk.Label(crow2, text="Cycle #:").pack(side="left")
        self.console_cycle_var = tk.StringVar(value="1")
        ttk.Entry(crow2, textvariable=self.console_cycle_var, width=5).pack(side="left", padx=(4, 8))
        ttk.Button(crow2, text="▶ run", command=self._console_run).pack(side="left", padx=2)
        ttk.Button(crow2, text="⏸ pause",
                  command=lambda: self._console_send("pause")).pack(side="left", padx=2)
        ttk.Separator(crow2, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(crow2, text="Raw command:").pack(side="left")
        self.console_raw_var = tk.StringVar(value="")
        ttk.Entry(crow2, textvariable=self.console_raw_var, width=16).pack(side="left", padx=(4, 4))
        ttk.Button(crow2, text="Send", command=self._console_send_raw).pack(side="left", padx=2)

        reading_lf = ttk.LabelFrame(split, text="Latest Reading")
        split.add(reading_lf, weight=2)
        reading_lf.rowconfigure(0, weight=1)
        reading_lf.columnconfigure(0, weight=1)

        # Horizontal sash between the SPL and ENV panes.
        reading_split = ttk.PanedWindow(reading_lf, orient="horizontal")
        reading_split.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        spl_frame = ttk.Frame(reading_split)
        reading_split.add(spl_frame, weight=1)
        spl_frame.rowconfigure(1, weight=1)
        spl_frame.columnconfigure(0, weight=1)
        ttk.Label(spl_frame, text="SPL", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky="w")
        self.console_spl_text = tk.Text(spl_frame, wrap="none", state="disabled",
                                        height=14, font=("Consolas", 9))
        self.console_spl_text.grid(row=1, column=0, sticky="nsew")
        spl_sb = ttk.Scrollbar(spl_frame, orient="vertical", command=self.console_spl_text.yview)
        spl_sb.grid(row=1, column=1, sticky="ns")
        self.console_spl_text.configure(yscrollcommand=spl_sb.set)

        env_frame = ttk.Frame(reading_split)
        reading_split.add(env_frame, weight=1)
        env_frame.rowconfigure(1, weight=1)
        env_frame.columnconfigure(0, weight=1)
        ttk.Label(env_frame, text="ENV", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky="w")
        self.console_env_text = tk.Text(env_frame, wrap="none", state="disabled",
                                        height=14, font=("Consolas", 9))
        self.console_env_text.grid(row=1, column=0, sticky="nsew")
        env_sb = ttk.Scrollbar(env_frame, orient="vertical", command=self.console_env_text.yview)
        env_sb.grid(row=1, column=1, sticky="ns")
        self.console_env_text.configure(yscrollcommand=env_sb.set)

    def _build_charts_tab(self, nb):
        """Live plots fed from the same packets _handle_packet already
        parses — no separate polling of the boards. Heater voltage/sensor
        current come from SPL packets (only streamed while a cycle is
        actively running); temperature comes from ENV packets (streamed
        continuously from the periodic #env? poll, regardless of run
        state — see the "does htr_voltage mean it's on" discussion this
        tab exists to make visually obvious). Shares console_board_var
        with Board Console so picking a board in either tab keeps both
        in sync."""
        tab = ttk.Frame(nb)
        nb.add(tab, text="Charts")
        self._charts_tab = tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        pick = ttk.Frame(tab)
        pick.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        ttk.Label(pick, text="Board:").pack(side="left")
        self._chart_board_cb = ttk.Combobox(
            pick, textvariable=self.console_board_var, state="readonly", width=14)
        self._chart_board_cb.pack(side="left", padx=(4, 12))
        self._chart_board_cb.bind("<<ComboboxSelected>>", lambda _e: self._redraw_charts())
        ttk.Label(pick, text="active board",
                 foreground="#6b7280", wraplength=480, justify="left").pack(side="left")

        if _MPL:
            self._chart_fig = Figure(figsize=(8, 7), dpi=100)
            self._chart_ax_v = self._chart_fig.add_subplot(311)
            self._chart_ax_i = self._chart_fig.add_subplot(312, sharex=self._chart_ax_v)
            self._chart_ax_t = self._chart_fig.add_subplot(313, sharex=self._chart_ax_v)
            self._chart_fig.tight_layout(pad=2.2)
            self._chart_canvas = FigureCanvasTkAgg(self._chart_fig, master=tab)
            self._chart_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 0))
            # Standard matplotlib zoom-rectangle/pan/home toolbar — same
            # pattern as gui/pma_wafer_panel.py's wafer/shot map.
            toolbar = NavigationToolbar2Tk(self._chart_canvas, tab, pack_toolbar=False)
            toolbar.update()
            toolbar.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
            self._draw_empty_charts()
        else:
            ttk.Label(tab, text="matplotlib not installed — install it to view live charts.",
                     foreground="red").grid(row=1, column=0, sticky="nw", padx=10, pady=10)

    def _draw_empty_charts(self):
        for ax, title in ((self._chart_ax_v, "Heater Voltage (mV) — SPL"),
                          (self._chart_ax_i, "Sensor Current (mA) — SPL"),
                          (self._chart_ax_t, "Temperature (°C) — ENV")):
            ax.clear()
            ax.set_title(title, fontsize=9)
            ax.text(0.5, 0.5, "no data yet", ha="center", va="center",
                    transform=ax.transAxes, color="#999999")
        self._chart_canvas.draw_idle()

    def _charts_tab_visible(self):
        if not _MPL:
            return False
        try:
            return self._sub_nb.select() == str(self._charts_tab)
        except Exception:
            return False

    def _refresh_charts_loop(self):
        """Self-rescheduling — only actually redraws (matplotlib redraws
        are much heavier than a plain Tk widget update) while the Charts
        tab is the one currently visible."""
        if self._charts_tab_visible():
            self._redraw_charts()
        self.after(300, self._refresh_charts_loop)

    @staticmethod
    def _pkt_time(item: dict):
        """Parse a packet's host_timestamp (now_stamp() — ISO 8601 with
        milliseconds) back into a datetime, or None if missing/malformed."""
        ts = item.get("host_timestamp")
        if not ts:
            return None
        try:
            return dt.datetime.fromisoformat(ts)
        except ValueError:
            return None

    def _elapsed_seconds(self, hist: list, t0: "dt.datetime"):
        """hist's host_timestamps as seconds elapsed since t0 — a real
        wall-clock axis shared across SPL/ENV (which arrive at
        independent, unrelated rates) instead of a per-series sample
        index, so a run's actual timing lines up between subplots."""
        out = []
        for item in hist:
            t = self._pkt_time(item)
            out.append((t - t0).total_seconds() if t else float("nan"))
        return out

    def _break_gaps(self, xs: list, ys: list):
        """Insert a NaN break wherever consecutive samples are more than
        _CHART_GAP_THRESHOLD_S apart, so a real pause (e.g. SPL streaming
        stops between cycles while ENV keeps polling on its own timer)
        renders as a visible gap instead of a straight line drawn across
        dead time that was never actually sampled."""
        out_x, out_y = [], []
        prev = None
        for x, y in zip(xs, ys):
            if prev is not None and (x - prev) > self._CHART_GAP_THRESHOLD_S:
                out_x.append(float("nan"))
                out_y.append(float("nan"))
            out_x.append(x)
            out_y.append(y)
            prev = x
        return out_x, out_y

    def _plot_series(self, ax, xs: list, hist: list, field: str, label: str):
        ys = [r.get(field, 0) for r in hist]
        gx, gy = self._break_gaps(xs, ys)
        ax.plot(gx, gy, label=label)

    def _redraw_charts(self):
        if not _MPL:
            return
        port = self.console_board_var.get()
        spl_hist = list(self._spl_history.get(port, ()))
        env_hist = list(self._env_history.get(port, ()))

        self._chart_ax_v.clear()
        self._chart_ax_i.clear()
        self._chart_ax_t.clear()

        # One shared time-zero (earliest sample across BOTH histories) so
        # SPL and ENV land on the same wall-clock x-axis — required for
        # a gap in one to actually line up as a gap against the other's
        # continuously-arriving data, not just an independent index reset.
        candidates = [self._pkt_time(h[0]) for h in (spl_hist, env_hist) if h]
        candidates = [t for t in candidates if t is not None]
        t0 = min(candidates) if candidates else dt.datetime.now()

        if spl_hist:
            xs = self._elapsed_seconds(spl_hist, t0)
            self._plot_series(self._chart_ax_v, xs, spl_hist, "heater1_voltage_mv", "heater1")
            self._plot_series(self._chart_ax_v, xs, spl_hist, "heater2_voltage_mv", "heater2")
            self._chart_ax_v.legend(fontsize=7, loc="upper left")
            for s in (1, 2, 3, 4):
                self._plot_series(self._chart_ax_i, xs, spl_hist, f"adc_current_ma_s{s}", f"s{s}")
            self._chart_ax_i.legend(fontsize=7, loc="upper left", ncol=4)
        else:
            for ax in (self._chart_ax_v, self._chart_ax_i):
                ax.text(0.5, 0.5, "no SPL data yet (needs an active run)",
                        ha="center", va="center", transform=ax.transAxes, color="#999999")

        if env_hist:
            xs2 = self._elapsed_seconds(env_hist, t0)
            self._plot_series(self._chart_ax_t, xs2, env_hist, "temp_h_c", "temp_h_c")
            self._plot_series(self._chart_ax_t, xs2, env_hist, "mcu_temperature_c", "mcu_temp")
            self._chart_ax_t.legend(fontsize=7, loc="upper left")
        else:
            self._chart_ax_t.text(0.5, 0.5, "no ENV data yet", ha="center", va="center",
                                  transform=self._chart_ax_t.transAxes, color="#999999")

        self._chart_ax_v.set_title("Heater Voltage (mV) — SPL", fontsize=9)
        self._chart_ax_i.set_title("Sensor Current (mA) — SPL", fontsize=9)
        self._chart_ax_t.set_title("Temperature (°C) — ENV", fontsize=9)
        self._chart_ax_t.set_xlabel(f"time (s, board {port or '—'})")
        self._chart_canvas.draw_idle()

    # ── Lock Setup controls + Run's Cycle#/Duration while a lot is
    # running (the EK-IV vendor tool itself won't let you change its
    # configuration window while a cycle is running — same idea) ─────────
    _LOCKABLE_WIDGETS = ("_cycle_entry", "_duration_entry", "_btn_discover",
                        "_btn_connect_boards", "_btn_disconnect_boards",
                        "_btn_connect_prober", "_btn_load_map",
                        "_btn_manual_zup", "_btn_manual_zdown", "_btn_manual_first_die",
                        "_btn_manual_next_die", "_btn_manual_xy", "_btn_manual_unload",
                        "_btn_measure", "_btn_randomize_sites",
                        "_btn_test_active", "_btn_pause_active")

    # Charts tab rolling-history bound per board (samples, not seconds —
    # SPL/ENV arrive at different, data-dependent rates).
    _CHART_HISTORY_LEN = 300
    # SPL only streams while a cycle is actively running; ENV keeps
    # polling on its own timer (env_interval_s) regardless — so a real
    # pause between cycles shows up as a time gap in SPL's history while
    # ENV keeps going. A gap this large between consecutive SPL/ENV
    # samples is drawn as a break in the line rather than a straight
    # (misleading) interpolation across dead time — see _redraw_charts.
    _CHART_GAP_THRESHOLD_S = 3.0

    def _set_locked(self, locked: bool):
        state = "disabled" if locked else "normal"
        for attr in self._LOCKABLE_WIDGETS:
            getattr(self, attr).config(state=state)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def _log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"{ts}  {msg}"
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _log_main(self, msg: str):
        """Also echo phase-level transitions to the shared sidebar log so
        NanoZ activity is visible without switching tabs."""
        self._log(msg)
        if hasattr(self.controller, "log"):
            self.controller.log(f"[NANOZ] {msg}")

    # ------------------------------------------------------------------
    # Board discovery / connection
    # ------------------------------------------------------------------
    def _discover_boards(self):
        threading.Thread(target=self._discover_boards_thread, daemon=True).start()

    def _discover_boards_thread(self):
        """The actual scan — a plain, directly-callable method (spawned as
        a background thread by _discover_boards) so it can also be called
        synchronously from a test without going through a real OS thread."""
        self.after(0, lambda: self._log("Scanning COM ports for NanoZ boards..."))
        found = nzb.discover_boards(log=lambda m: self.after(0, lambda m=m: self._log(m)))
        self.after(0, lambda: self._on_discovered(found))

    def _on_discovered(self, found: list):
        try:
            env_interval_s = float(self.env_interval_var.get())
        except ValueError:
            env_interval_s = 1.0
        for ident in found:
            if ident.port in self._boards:
                continue
            board = nzb.NanoZBoard(ident, self._queue, die_provider=lambda: self._current_rc,
                                   env_interval_s=env_interval_s)
            self._boards[ident.port] = board
            iid = self._board_tree.insert("", "end", values=(
                ident.port, ident.serial_number, ident.firmware, ident.signature,
                "✓", "discovered", 0, 0))
            self._board_rows[ident.port] = iid
        self._log_main(f"Discovery complete — {len(found)} board(s) found, "
                       f"{len(self._boards)} total known.")
        self._refresh_console_boards()
        self._refresh_active_boards_label()

    def _on_board_row_toggle(self, _event):
        sel = self._board_tree.selection()
        if not sel:
            return
        iid = sel[0]
        port = self._board_tree.item(iid, "values")[0]
        board = self._boards.get(port)
        if not board:
            return
        board.selected = not board.selected
        vals = list(self._board_tree.item(iid, "values"))
        vals[4] = "✓" if board.selected else ""
        self._board_tree.item(iid, values=vals)
        self._refresh_active_boards_label()

    def _connect_boards(self):
        targets = [b for b in self._boards.values() if b.selected and not b.is_running]
        if not targets:
            self._log_main("Connect Selected: nothing to connect (discover boards first, "
                           "or everything selected is already connected).")
            return
        threading.Thread(target=self._connect_boards_thread, args=(targets,), daemon=True).start()

    def _connect_boards_thread(self, targets: list):
        for board in targets:
            try:
                board.start()
                self.after(0, lambda p=board.port: self._set_board_status(p, "connected"))
                self.after(0, lambda p=board.port: self._log(f"{p}: connected, reader running"))
            except Exception as e:
                self.after(0, lambda p=board.port, e=e: self._set_board_status(p, "ERROR"))
                self.after(0, lambda p=board.port, e=e: self._log(f"{p}: connect failed — {e}"))
        self.after(0, lambda: self._log_main(
            f"{sum(1 for b in targets if b.is_running)}/{len(targets)} board(s) connected."))
        self.after(0, self._refresh_active_boards_label)

    def _disconnect_boards(self):
        if self._running:
            messagebox.showerror("Lot Running", "Stop the lot before disconnecting boards.")
            return
        targets = [b for b in self._boards.values() if b.is_running]
        if not targets:
            self._log_main("Disconnect Boards: nothing connected.")
            return
        threading.Thread(target=self._disconnect_boards_thread, args=(targets,), daemon=True).start()

    def _disconnect_boards_thread(self, targets: list):
        """board.stop() joins each reader thread (up to ~2s) -- run off
        the main thread so disconnecting several boards can't freeze the
        GUI for several seconds."""
        for board in targets:
            board.stop()
            self.after(0, lambda p=board.port: self._set_board_status(p, "discovered"))
        self.after(0, lambda: self._log_main(
            f"{len(targets)} board(s) disconnected (ports closed)."))
        self.after(0, self._refresh_active_boards_label)

    def _set_board_status(self, port: str, status: str):
        iid = self._board_rows.get(port)
        if not iid:
            return
        vals = list(self._board_tree.item(iid, "values"))
        vals[5] = status
        self._board_tree.item(iid, values=vals)

    def _set_board_counts(self, port: str, spl: int, env: int):
        iid = self._board_rows.get(port)
        if not iid:
            return
        vals = list(self._board_tree.item(iid, "values"))
        vals[6], vals[7] = spl, env
        self._board_tree.item(iid, values=vals)

    def _refresh_board_status(self):
        """🔄 Refresh Status — re-derive every known board's Status column
        from its actual live state instead of the value last set at
        connect/disconnect time. A board's reader thread doesn't exit on
        a serial error (see NanoZBoard._reader_loop — it catches, records
        last_error, and keeps retrying), so a board that's been silently
        unplugged still shows "connected" forever unless something
        re-checks it — this does that check on demand."""
        connected = errored = idle = 0
        for port, board in self._boards.items():
            last_error = getattr(board, "last_error", "")
            if board.is_running and last_error:
                status = "ERROR"
                errored += 1
            elif board.is_running:
                status = "connected"
                connected += 1
            else:
                status = "discovered"
                idle += 1
            self._set_board_status(port, status)
            if status == "ERROR":
                self._log(f"{port}: last error — {last_error}")
        self._log_main(f"Refresh Status — {connected} connected, {errored} error(s), "
                       f"{idle} not connected ({len(self._boards)} known).")

    def _refresh_active_boards_label(self):
        """Run tab's read-only summary of which boards are actually
        selected+connected — kept in sync so Run doesn't need its own
        copy of the boards Treeview (that lives on Setup)."""
        active = [b for b in self._boards.values() if b.selected and b.is_running]
        if not active:
            self.active_boards_var.set("No boards connected yet — see the Setup tab.")
        else:
            self.active_boards_var.set(
                f"{len(active)} board(s) ready: " + ", ".join(b.port for b in active))

    # ------------------------------------------------------------------
    # Prober (shared with the rest of the app — same driver registry)
    # ------------------------------------------------------------------
    def _connect_prober(self):
        existing = self.controller.drivers.get("prober")
        if existing and existing.inst:
            self._log_main("Prober already connected (shared with the Instruments tab).")
            self._update_prober_status()
            return
        threading.Thread(target=self._connect_prober_thread, daemon=True).start()

    def _connect_prober_thread(self):
        self.after(0, lambda: self._log("Connecting to prober (GPIB)..."))
        drv = AccretechUF200R()
        def _finish():
            if drv.inst:
                self.controller.drivers["prober"] = drv
                self._log_main("Prober connected.")
            else:
                self._log_main("Prober connection FAILED — check GPIB address/cabling.")
            self._update_prober_status()
        self.after(0, _finish)

    def _update_prober_status(self):
        drv = self.controller.drivers.get("prober")
        if drv and drv.inst:
            self.prober_status_var.set("Prober: connected")
        else:
            self.prober_status_var.set("Prober: not connected")

    # ------------------------------------------------------------------
    # Wafer map (own instance, lives on the Run tab — does not touch
    # Main's or Debug's wafer maps).
    # ------------------------------------------------------------------
    def _load_wafer_map(self):
        """Manual reload button on the Run tab — mirrors
        on_ata_folder_loaded but reports an error if no folder is loaded
        yet, since this is a deliberate user action rather than an
        automatic fan-out."""
        folder = getattr(self._main_layout, "_ata_folder", None)
        if not folder:
            messagebox.showerror("No ATA Folder",
                                 "Load an ATA folder from the toolbar first.")
            return
        n = self.wafer_map.load_from_ata(folder, filename="ata_wafer_map_accretech.csv")
        self._log_main(f"Wafer map loaded from '{os.path.basename(folder)}' — {n} die(s).")

    def on_ata_folder_loaded(self, folder_path: str):
        """Called by MainLayout.load_ata_folder (instrument_panel.py)
        right after the user picks/refreshes an ATA folder from the
        toolbar — the same auto-population fan-out every other tab's
        wafer map already gets (Accr Wafer, PMA, Main's own "▶ Run" tab).
        Quiet on a missing CSV: WaferMapPanel.load_from_ata already just
        draws a "not found" message on its own canvas (no popup), which
        is the right behavior here too since the file may not exist yet
        if Accr Wafer hasn't been run for this folder."""
        n = self.wafer_map.load_from_ata(folder_path, filename="ata_wafer_map_accretech.csv")
        if n:
            self._log_main(f"Wafer map auto-loaded from "
                           f"'{os.path.basename(folder_path)}' — {n} die(s).")

    # ------------------------------------------------------------------
    # Board Console — manual per-command testing against one board, no
    # lot required. Every command here writes to the board directly; the
    # reply (if any) shows up asynchronously in the shared log as a plain
    # "text" packet, same as run/pause confirmations already do during a
    # lot (see NanoZBoard.send_raw / _reader_loop).
    # ------------------------------------------------------------------
    def _refresh_console_boards(self):
        ports = sorted(self._boards.keys())
        self._console_board_cb.config(values=ports)
        self._chart_board_cb.config(values=ports)
        if self.console_board_var.get() not in ports and ports:
            self.console_board_var.set(ports[0])
        self._refresh_console_reading()

    def _console_selected_board(self):
        return self._boards.get(self.console_board_var.get())

    def _console_send(self, cmd: str):
        board = self._console_selected_board()
        if not board or not board.is_running:
            messagebox.showerror("No Board Selected",
                                 "Pick a connected board first (Setup tab -> Connect Selected).")
            return
        board.send_raw(cmd)
        self._log(f"{board.port}: >> {cmd}")

    def _console_send_raw(self):
        cmd = self.console_raw_var.get().strip()
        if not cmd:
            return
        self._console_send(cmd)

    def _console_run(self):
        try:
            cycle = int(self.console_cycle_var.get())
        except ValueError:
            messagebox.showerror("Invalid Cycle", "Cycle # must be a whole number.")
            return
        self._console_send(f"run {cycle}")

    def _console_calib_bang(self):
        """'calib!' — EK-IV only, requires the 10K-resistor calibration
        kit mounted in place of the normal sensors (see the NanoZ
        Protocol reference) — confirm first since running it with real
        sensors attached produces meaningless calibration offsets."""
        if not messagebox.askyesno(
            "Run Calibration",
            "calib! runs the EK-IV's calibration routine and REQUIRES the "
            "10K-resistor calibration kit to be mounted in place of the "
            "normal sensors. Running it with real sensors attached will "
            "produce meaningless calibration offsets.\n\nContinue?"):
            return
        self._console_send("calib!")

    def _console_cleep(self):
        """'cleep' — erases every stored cycle/sequence on the board's
        non-volatile memory; confirm first since it can't be undone from
        here (the board needs to be reprogrammed with Nanoz_EK afterward)."""
        if not messagebox.askyesno(
            "Erase EEPROM",
            "cleep erases every stored cycle/sequence on this board's "
            "non-volatile memory. This cannot be undone from here — the "
            "board will need to be reprogrammed with Nanoz_EK before it "
            "can run a cycle again.\n\nContinue?"):
            return
        self._console_send("cleep")

    @staticmethod
    def _format_reading_lines(item: "dict | None"):
        if not item:
            return ["(none yet)"]
        return [f"{k}: {v}" for k, v in item.items() if k not in ("kind", "port")]

    def _refresh_console_reading(self):
        """SPL and ENV shown side by side (two separate Text widgets) —
        they arrive on independent, unrelated schedules (SPL only while
        a cycle runs; ENV on its own timer regardless — see the Charts
        tab), so interleaving them into one combined view made it hard
        to tell which packet's fields were which."""
        port = self.console_board_var.get()
        spl_lines = self._format_reading_lines(self._latest_spl.get(port))
        env_lines = self._format_reading_lines(self._latest_env.get(port))
        for widget, lines in ((self.console_spl_text, spl_lines),
                              (self.console_env_text, env_lines)):
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("1.0", "\n".join(lines))
            widget.configure(state="disabled")

    # ------------------------------------------------------------------
    # Output paths — new files only, written into the active ATA folder
    # when one is loaded (falls back to the Results tab's export path,
    # then the current working directory) — never overwrites an existing
    # ATA file (each lot gets its own timestamped pair).
    # ------------------------------------------------------------------
    def _new_csv_paths(self):
        folder = (getattr(self._main_layout, "_ata_folder", None)
                 or self._main_layout.export_path_var.get()
                 or os.getcwd())
        os.makedirs(folder, exist_ok=True)
        run_id = time.strftime("%Y%m%d_%H%M%S")
        return (os.path.join(folder, f"ata_nanoz_spl_{run_id}.csv"),
               os.path.join(folder, f"ata_nanoz_env_{run_id}.csv"))

    # ------------------------------------------------------------------
    # Phase 5 — drain the shared queue on the Tk main thread, write CSV,
    # update live counters/log/wafer map.
    # ------------------------------------------------------------------
    def _check_queue(self):
        drained = 0
        while drained < 500:   # bound per tick so a burst can't freeze the UI
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                break
            drained += 1
            self._handle_packet(item)
        if drained:
            self.counts_var.set(f"SPL: {self._spl_total}   ENV: {self._env_total}")
        self.after(50, self._check_queue)

    def _handle_packet(self, item: dict):
        kind = item.get("kind")
        port = item.get("port")
        board = self._boards.get(port)
        if kind == "spl":
            self._spl_total += 1
            self._touchdown_packets += 1
            if not item.get("checksum_ok", True) or "parse_error" in item:
                self._touchdown_errors += 1
            self._latest_spl[port] = item
            self._spl_history.setdefault(
                port, collections.deque(maxlen=self._CHART_HISTORY_LEN)).append(item)
            if self._spl_path:
                row = {k: v for k, v in item.items() if k != "kind"}
                try:
                    nzb.append_csv_row(self._spl_path, row)
                except OSError as e:
                    self._log(f"SPL CSV write error: {e}")
            if board:
                self._set_board_counts(port, board.spl_count, board.env_count)
            if port == self.console_board_var.get():
                self._refresh_console_reading()
        elif kind == "env":
            self._env_total += 1
            self._touchdown_packets += 1
            if not item.get("checksum_ok", True) or "parse_error" in item:
                self._touchdown_errors += 1
            self._latest_env[port] = item
            self._env_history.setdefault(
                port, collections.deque(maxlen=self._CHART_HISTORY_LEN)).append(item)
            if self._env_path:
                row = {k: v for k, v in item.items() if k != "kind"}
                try:
                    nzb.append_csv_row(self._env_path, row)
                except OSError as e:
                    self._log(f"ENV CSV write error: {e}")
            if board:
                self._set_board_counts(port, board.spl_count, board.env_count)
            if port == self.console_board_var.get():
                self._refresh_console_reading()
        elif kind == "text":
            self._log(f"{port}: {item.get('text', '')}")
        elif kind == "unrecognized":
            self._log(f"{port}: UNRECOGNIZED HEADER: {item.get('raw')!r}")

    # ------------------------------------------------------------------
    # Phase 2/3/4/6 — lot sequencing thread. Reuses the SAME prober
    # driver + cassette-workflow methods the Run tab uses (STB
    # handshakes are already implemented/tested there — see
    # instruments/accretech_uf200r.py's cassette_* methods); this thread
    # only adds the NanoZ-specific per-die run/pause + data logging.
    # ------------------------------------------------------------------
    def _start_lot(self):
        """▶ Full Die — the cassette-workflow wafer walk (STB 65/66/67
        handshake, see _lot_thread_body)."""
        if self._running:
            self._log_main("A run is already active.")
            return
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            messagebox.showerror("Prober Not Connected", "🔌 Connect Prober first.")
            return
        active = [b for b in self._boards.values() if b.selected and b.is_running]
        if not active:
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect Selected at least one NanoZ board first.")
            return
        try:
            cycle = int(self.cycle_var.get())
            duration_s = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Invalid Parameters", "Cycle # and duration must be numeric.")
            return

        self._spl_path, self._env_path = self._new_csv_paths()
        self._log_main(f"Starting Full Die — cycle {cycle}, {duration_s:g}s/touchdown, "
                       f"{len(active)} board(s): {', '.join(b.port for b in active)}")
        self._log(f"SPL CSV: {self._spl_path}")
        self._log(f"ENV CSV: {self._env_path}")

        self._reset_counts()
        self._running = True
        self._run_mode = "full"
        self.start_btn.config(state="disabled")
        self.test_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.state_var.set("RUNNING (Full Die)")
        self._set_locked(True)
        self._lot_thread = threading.Thread(
            target=self._lot_thread_body, args=(prober, active, cycle, duration_s), daemon=True)
        self._lot_thread.start()

    def _stop_lot(self):
        """⏹ Stop Run — pauses heaters on every board immediately, and
        clears self._running so whichever run loop is active (Full Die's
        _lot_thread_body or Test Die's _test_die_thread_body — both just
        watch self._running) stops at its next checkpoint (right after
        the current touchdown's timer, or after whichever prober wait
        it's currently blocked in returns — same responsiveness tradeoff
        as the existing Cassette tab's Stop button)."""
        if not self._running:
            return
        self._running = False
        self._log_main("Stop requested — pausing heaters now; the prober "
                       "handshake in progress will still finish or time out "
                       "before the run actually stops.")
        for board in self._boards.values():
            try:
                board.pause()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Manual chuck controls (Run tab) — the die-walk command family
    # (G/Z/D/J), a workflow SEPARATE from Full Die's cassette automation
    # (J/U mean something else there — accretech_uf200r.py's cassette_*
    # docstrings call these "must never be mixed"). Same intent as
    # Main's "▶ Run" tab manual nav row (instrument_panel.py
    # _tab_execution2's _exec2_manual_*): spot-check/home the prober
    # without starting a real run. _run_guard blocks all of them while
    # any NanoZ run is active, on top of _set_locked disabling the
    # buttons themselves — belt and suspenders against colliding with
    # the run thread on the same GPIB session.
    # ------------------------------------------------------------------
    def _run_guard(self, name: str) -> bool:
        if self._running:
            messagebox.showerror("Run Active", f"{name}: stop the current run first.")
            return True
        return False

    def _do_manual_call(self, name: str, fn, log_cmd: str, refresh_xy: bool = False):
        """Body shared by every one-shot manual chuck control — logs the
        outgoing command, calls fn(prober), logs the confirmed STB. Safe
        to call directly (tests) or from a spawned thread (real UI path,
        see the public _manual_* wrappers)."""
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self.after(0, lambda: self._log_main(f"{name}: prober not connected."))
            return
        try:
            self.after(0, lambda: self._log(log_cmd))
            stb = fn(prober)
            self.after(0, lambda stb=stb: self._log(f"<< STB={stb}  ({name} complete)"))
            if refresh_xy:
                self._manual_xy_thread()
        except Exception as e:
            self.after(0, lambda e=e: self._log_main(f"{name} error: {e}"))

    def _manual_z_up(self):
        if self._run_guard("Z Up"):
            return
        threading.Thread(target=self._manual_z_up_thread, daemon=True).start()

    def _manual_z_up_thread(self):
        self._do_manual_call("Z Up", lambda p: p.z_up(), ">> Z  (Contact)")

    def _manual_z_down(self):
        if self._run_guard("Z Down"):
            return
        threading.Thread(target=self._manual_z_down_thread, daemon=True).start()

    def _manual_z_down_thread(self):
        self._do_manual_call("Z Down", lambda p: p.z_down(), ">> D  (Separate)")

    def _manual_first_die(self):
        if self._run_guard("First Die"):
            return
        threading.Thread(target=self._manual_first_die_thread, daemon=True).start()

    def _manual_first_die_thread(self):
        self._do_manual_call("First Die", lambda p: p.move_to_start_die(),
                             ">> G  (Position start die)", refresh_xy=True)

    def _manual_next_die(self):
        if self._run_guard("Next Die"):
            return
        threading.Thread(target=self._manual_next_die_thread, daemon=True).start()

    def _manual_next_die_thread(self):
        self._do_manual_call("Next Die", lambda p: p.next_die(),
                             ">> J  (Next Die)", refresh_xy=True)

    def _manual_unload(self):
        if self._run_guard("Unload"):
            return
        threading.Thread(target=self._manual_unload_thread, daemon=True).start()

    def _manual_unload_thread(self):
        self._do_manual_call("Unload", lambda p: p.unload_wafer(), ">> U  (Unload wafer)")

    def _manual_xy(self):
        if self._run_guard("XY"):
            return
        threading.Thread(target=self._manual_xy_thread, daemon=True).start()

    def _manual_xy_thread(self):
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            self.after(0, lambda: self.manual_xy_var.set("X: —  Y: —"))
            self.after(0, lambda: self._log_main("XY: prober not connected."))
            return
        try:
            raw = prober.get_xy_position()
            x, y = _parse_q_response(raw)
            self.after(0, lambda: self.manual_xy_var.set(f"X: {x:.0f}  Y: {y:.0f}"))
            self.after(0, lambda: self._log(f"Q -> die X={x:.0f} Y={y:.0f}"))
            self.after(0, lambda: self.wafer_map.update_die(int(y), int(x), "CURRENT"))
        except Exception as e:
            self.after(0, lambda e=e: self._log_main(f"XY error: {e}"))
            self.after(0, lambda: self.manual_xy_var.set("X: ERROR  Y: ERROR"))

    def _manual_measure(self):
        """🦶 Measure — single touchdown at the CURRENT die: Z Up (if a
        prober is connected), trigger `run <cycle>` on every selected
        board, wait, `pause`. Deliberately does NOT Z Down afterward
        (matches Main's own simple Touchdown/Measure button) — use Z
        Down when ready to release contact. Reuses the same Cycle #/
        Touchdown duration fields as Full Die/Test Die."""
        if self._run_guard("Measure"):
            return
        active = [b for b in self._boards.values() if b.selected and b.is_running]
        if not active:
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect Selected at least one NanoZ board first.")
            return
        try:
            cycle = int(self.cycle_var.get())
            duration_s = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Invalid Parameters", "Cycle # and duration must be numeric.")
            return
        threading.Thread(target=self._manual_measure_thread, args=(active, cycle, duration_s),
                         daemon=True).start()

    def _manual_measure_thread(self, active: list, cycle: int, duration_s: float):
        prober = self.controller.drivers.get("prober")
        if prober and prober.inst:
            try:
                self.after(0, lambda: self._log(
                    ">> Z  (Touchdown — chuck rises, wafer CONTACTS probe card)"))
                stb = prober.z_up()
                self.after(0, lambda stb=stb: self._log(f"<< STB={stb}  (touchdown complete)"))
            except Exception as e:
                self.after(0, lambda e=e: self._log_main(
                    f"Measure: touchdown error: {e} — measuring anyway"))
        else:
            self.after(0, lambda: self._log_main(
                "Measure: prober not connected — measuring at current state."))

        self._trigger_cycle_and_wait(active, cycle, duration_s, "Measure")
        self.after(0, lambda: self._log(
            "Measure complete — chuck still in contact; use Z Down to release."))

    def _test_active_boards(self):
        """▶ Run Cycle (Active Boards) — bench-test every currently
        active (selected+connected) board directly: no prober, no
        touchdown, just `run <cycle>` sent straight to each board.
        Doesn't wait or auto-pause — use Pause (Active Boards) when
        done watching, or the Board Console for one board at a time."""
        if self._run_guard("Run Cycle"):
            return
        active = [b for b in self._boards.values() if b.selected and b.is_running]
        if not active:
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect Selected at least one NanoZ board first.")
            return
        try:
            cycle = int(self.cycle_var.get())
        except ValueError:
            messagebox.showerror("Invalid Cycle", "Cycle # must be a whole number.")
            return
        for board in active:
            board.run_cycle(cycle)
        self._log_main(f"Run Cycle {cycle} triggered on {len(active)} active board(s): "
                       + ", ".join(b.port for b in active))

    def _pause_active_boards(self):
        """⏸ Pause (Active Boards) — pause every currently active board.
        Locked out during a real run same as the other manual controls
        (see _run_guard): pausing here wouldn't actually stop a Full
        Die/Test Die run (the loop would just re-trigger on the next
        touchdown) — Stop Run is the correct control for that, so this
        stays a bench-test-only action to avoid the confusing illusion
        of having paused a run that's still going."""
        if self._run_guard("Pause"):
            return
        active = [b for b in self._boards.values() if b.selected and b.is_running]
        if not active:
            self._log_main("Pause (Active Boards): nothing connected.")
            return
        for board in active:
            board.pause()
        self._log_main(f"Paused {len(active)} active board(s): "
                       + ", ".join(b.port for b in active))

    # ------------------------------------------------------------------
    # Test Die (Run tab) — a picked-subset walk over the die-walk command
    # family (move_to_die_xy), for testing specific sites instead of the
    # whole wafer. Same overall shape/safety gates as Main's
    # _exec2_test_die_thread (contact guard, Z-Down-not-confirmed aborts
    # the run) — see accretech_uf200r.py's move_to_die_xy docstring for
    # the STB codes.
    # ------------------------------------------------------------------
    def _on_sites_changed(self, picks: list):
        self.sites_var.set(f"Test sites: {len(picks)} picked (click dies to add/remove)")

    def _randomize_sites(self):
        if self._run_guard("Randomize"):
            return
        dies = list(self.wafer_map.dies.keys())
        n = min(5, len(dies))
        picks = random.sample(dies, n) if n else []
        self.wafer_map.set_picked(picks)
        self._on_sites_changed(picks)

    def _ensure_separated(self, prober, stb: int):
        """Contact guard: move_to_die_xy restores the chuck's PRIOR
        height, so a travel can finish chuck UP (STB=67 — contact).
        Separate again immediately — contact should only happen
        deliberately, inside _zup_measure_zdown (matches Main's own
        _exec2_ensure_separated)."""
        if stb != 67:
            return
        self.after(0, lambda: self._log("finished chuck UP (STB=67 — contact) >> D  (Separate)"))
        prober.z_down()

    def _zup_measure_zdown(self, prober, boards: list, cycle: int, duration_s: float, label: str) -> bool:
        """Contact (Z UP) -> _trigger_cycle_and_wait -> separate (Z
        DOWN). Z Down is a safety gate here: if it's not confirmed
        (wrong STB, timeout, or a real error), self._running is cleared
        right here so the caller's loop can never follow with more
        chuck travel — matches Main's own _exec2_zup_measure_zdown."""
        try:
            self.after(0, lambda: self._log(f"{label}: >> Z  (Contact)"))
            stb = prober.z_up()
            if stb == 67:
                self.after(0, lambda: self._log(f"{label}: << STB=67 (contact confirmed)"))
            else:
                self.after(0, lambda stb=stb: self._log_main(
                    f"{label}: Z Up returned STB={stb} (expected 67)"))
        except Exception as e:
            self.after(0, lambda e=e: self._log_main(
                f"{label}: touchdown error: {e} — measuring anyway"))

        ok = self._trigger_cycle_and_wait(boards, cycle, duration_s, label)

        z_down_confirmed = True
        try:
            self.after(0, lambda: self._log(f"{label}: >> D  (Separate)"))
            stb = prober.z_down()
            if stb != 68:
                z_down_confirmed = False
                self.after(0, lambda stb=stb: self._log_main(
                    f"{label}: Z Down returned STB={stb} (expected 68) — separation NOT confirmed"))
        except Exception as e:
            z_down_confirmed = False
            self.after(0, lambda e=e: self._log_main(f"{label}: separate error: {e}"))
        if not z_down_confirmed:
            self._running = False
            self.after(0, lambda: self._log_main(
                "Z Down not confirmed — stopping (safety gate, same as Full Die)."))
        return ok

    def _start_test_die(self):
        if self._running:
            self._log_main("A run is already active.")
            return
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            messagebox.showerror("Prober Not Connected", "🔌 Connect Prober first.")
            return
        active = [b for b in self._boards.values() if b.selected and b.is_running]
        if not active:
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect Selected at least one NanoZ board first.")
            return
        sites = self.wafer_map.get_picked()
        if not sites:
            self._randomize_sites()
            sites = self.wafer_map.get_picked()
        if not sites:
            messagebox.showerror("No Dies", "No dies available to pick test sites from — "
                                 "load a wafer map first.")
            return
        try:
            cycle = int(self.cycle_var.get())
            duration_s = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Invalid Parameters", "Cycle # and duration must be numeric.")
            return

        self._spl_path, self._env_path = self._new_csv_paths()
        self._log_main(f"Starting Test Die — cycle {cycle}, {duration_s:g}s/touchdown, "
                       f"{len(sites)} site(s): " + ", ".join(f"R{r}C{c}" for r, c in sites))
        self._log(f"SPL CSV: {self._spl_path}")
        self._log(f"ENV CSV: {self._env_path}")

        self._reset_counts()
        self._running = True
        self._run_mode = "test"
        self.start_btn.config(state="disabled")
        self.test_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.state_var.set("RUNNING (Test Die)")
        self.wafer_map.enable_picking(0)
        self._set_locked(True)
        self._lot_thread = threading.Thread(
            target=self._test_die_thread_body, args=(prober, active, sites, cycle, duration_s),
            daemon=True)
        self._lot_thread.start()

    def _test_die_thread_body(self, prober, boards: list, sites: list, cycle: int, duration_s: float):
        """D (separate) -> position the first picked site -> loop[
        Z-up/measure/Z-down (_zup_measure_zdown), position next picked
        site ] until every site is tested or Stop Run clears
        self._running — the SAME shape as _run_wafer, substituting
        move_to_die_xy for the cassette workflow's next-die handshake
        since Test Die targets specific sites instead of stepping the
        prober's own raster."""
        try:
            self.after(0, lambda: self._log(">> D  (Separate)"))
            prober.z_down()

            row, col = sites[0]
            self.after(0, lambda: self._log(f">> J  (Position die X={col} Y={row})"))
            stb = prober.move_to_die_xy(col, row)
            if stb == 81:
                self.after(0, lambda: self._log_main("STB=81 — wafer end, stopping."))
                return
            if stb == 90:
                self.after(0, lambda: self._log_main(
                    "STB=90 — probing stop (<STOP> pushed), stopping."))
                return
            self.after(0, lambda stb=stb: self._log(f"<< STB={stb}"))
            self._ensure_separated(prober, stb)

            idx = 0
            while self._running and idx < len(sites):
                row, col = sites[idx]
                die_label = f"R{row}C{col}"
                self._current_rc = (row, col)
                self.after(0, lambda dl=die_label: self.die_var.set(f"Die: {dl}"))
                self.after(0, lambda r=row, c=col: self.wafer_map.update_die(r, c, "CURRENT"))

                ok = self._zup_measure_zdown(prober, boards, cycle, duration_s, die_label)
                if not self._running:
                    # the Z-Down safety gate inside _zup_measure_zdown
                    # already cleared self._running -- don't score/move further
                    break
                status = "PASS" if ok else "FAIL"
                if status == "PASS":
                    self._pass_count += 1
                else:
                    self._fail_count += 1
                self.after(0, self._update_pass_fail_display)
                self.after(0, lambda r=row, c=col, s=status: self.wafer_map.update_die(r, c, s))

                idx += 1
                if not self._running or idx >= len(sites):
                    break

                row, col = sites[idx]
                self.after(0, lambda r=row, c=col: self._log(f">> J  (Position die X={c} Y={r})"))
                stb = prober.move_to_die_xy(col, row)
                if stb == 81:
                    self.after(0, lambda: self._log_main("STB=81 — wafer end, stopping."))
                    break
                if stb == 90:
                    self.after(0, lambda: self._log_main(
                        "STB=90 — probing stop (<STOP> pushed), stopping."))
                    break
                self.after(0, lambda stb=stb: self._log(f"<< STB={stb}"))
                self._ensure_separated(prober, stb)
        except Exception as e:
            self.after(0, lambda e=e: self._log_main(f"ERROR: {e}"))
        finally:
            for board in boards:
                try:
                    board.pause()
                except Exception:
                    pass
            self._running = False
            self._run_mode = None
            self.after(0, lambda: self._finish_lot("TEST DIE COMPLETE"))

    # Timeouts match gui/cassette_panel.py's own established values for
    # these exact same driver calls (see its _lot_thread) — one bounded
    # call each, not a short-chunk retry loop: cassette_next_die/
    # cassette_unload_and_load_next send J/U themselves on every call, so
    # retrying them on a short timeout would resend the command while the
    # prior one might still be in flight. This does mean ⏹ Stop Run can
    # take up to the current call's timeout to actually land — the same
    # tradeoff the existing Cassette tab already makes.
    _WAFER_READY_TIMEOUT_S = 60.0
    _NEXT_DIE_TIMEOUT_S = 60.0
    _UNLOAD_LOAD_TIMEOUT_S = 180.0

    def _lot_thread_body(self, prober, boards: list, cycle: int, duration_s: float):
        """STB=0 (idle — cassette empty / no more wafers) is a normal,
        expected end state here, not an error — cassette_wait_for_wafer_ready/
        cassette_unload_and_load_next both collapse it (and a plain
        timeout) down to None rather than surfacing the raw code, so it's
        deliberately never logged by number, just as "idle / lot complete".
        A confirmed STB=76 alarm is the one code that DOES need explicit
        handling — see the except block below, which clears the buzzer."""
        try:
            while self._running:
                self.after(0, lambda: self.state_var.set("WAITING (STB=65)"))
                self.after(0, lambda: self._log_main("Waiting for STB=65 (wafer ready)..."))
                stb = prober.cassette_wait_for_wafer_ready(timeout_s=self._WAFER_READY_TIMEOUT_S)
                if stb != 65:
                    self.after(0, lambda: self._log_main(
                        "No STB=65 — treating as idle / lot complete."))
                    break
                self.after(0, lambda: self.state_var.set("RUNNING"))
                self.after(0, lambda: self._log_main("Wafer ready — needles on Die 1."))

                stb = self._run_wafer(prober, boards, cycle, duration_s)
                if not self._running or stb != 67:
                    break

                self.after(0, lambda: self.state_var.set("SWAPPING CASSETTE"))
                self.after(0, lambda: self._log_main(
                    "End of wafer map — unloading and loading next wafer..."))
                stb = prober.cassette_unload_and_load_next(timeout_s=self._UNLOAD_LOAD_TIMEOUT_S)
                if stb != 65:
                    self.after(0, lambda: self._log_main(
                        "No next wafer (cassette empty / idle) — Lot Complete."))
                    break
                # loop back — the next cassette_wait_for_wafer_ready call
                # will see the STB=65 unload_and_load_next just confirmed
        except Exception as e:
            self.after(0, lambda e=e: self._log_main(f"ERROR: {e}"))
            # A confirmed STB=76 alarm (see accretech_uf200r.py's
            # _wait_for_stb_any) raises rather than returning a value, so
            # it lands here instead of the normal stb-checks above — make
            # sure the buzzer actually gets cleared instead of leaving it
            # blaring on the operator (same "es" the rest of the app sends
            # for a confirmed alarm — see AtomicaDashboard._poll_prober_ready).
            if "STB=76" in str(e):
                try:
                    prober.send_es()
                    self.after(0, lambda: self._log_main(
                        "Alarm buzzer cleared (es sent)."))
                except Exception:
                    pass
        finally:
            for board in boards:
                try:
                    board.pause()
                except Exception:
                    pass
            self._running = False
            self._run_mode = None
            self.after(0, lambda: self._finish_lot("LOT COMPLETE"))

    def _finish_lot(self, msg: str = "LOT COMPLETE"):
        self.start_btn.config(state="normal")
        self.test_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.state_var.set(msg)
        self._set_locked(False)
        self.wafer_map.enable_picking(on_change=self._on_sites_changed)
        self._log_main(f"{msg} — heaters paused on all boards.")

    def _trigger_cycle_and_wait(self, boards: list, cycle: int, duration_s: float, label: str) -> bool:
        """Trigger `run <cycle>` on every board, wait duration_s (checking
        self._running so Stop Run can interrupt mid-touchdown), then
        `pause`. Returns True if at least one SPL/ENV packet arrived with
        no checksum/parse error. Shared by Full Die's per-die loop
        (_run_wafer), Test Die's per-site loop (_zup_measure_zdown), and
        the manual Measure button — the only difference between them is
        what (if anything) each does with the chuck before/after this."""
        self._touchdown_errors = 0
        self._touchdown_packets = 0
        for board in boards:
            board.run_cycle(cycle)
        self.after(0, lambda: self._log_main(
            f"{label} — triggered run {cycle} on {len(boards)} board(s)."))

        t0 = time.time()
        while self._running and time.time() - t0 < duration_s:
            time.sleep(0.05)

        for board in boards:
            board.pause()
        self.after(0, lambda: self._log(f"{label}: heaters paused."))
        return self._touchdown_packets > 0 and self._touchdown_errors == 0

    def _run_wafer(self, prober, boards: list, cycle: int, duration_s: float):
        """Phase 3 — die-to-die loop for the CURRENTLY loaded wafer.
        Returns 67 (end of wafer map, handled normally by the caller), or
        None if the run was stopped/aborted or the prober reported
        anything unexpected."""
        while self._running:
            self._update_current_die(prober)
            self._trigger_cycle_and_wait(boards, cycle, duration_s, f"Die {self._current_rc}")
            self._mark_touchdown_result()

            if not self._running:
                return None

            self.after(0, lambda: self._log(">> J  (Next Die)"))
            stb = prober.cassette_next_die(timeout_s=self._NEXT_DIE_TIMEOUT_S)
            if stb == 66:
                self.after(0, lambda: self._log("<< STB=66 — next die arrived."))
                continue
            if stb == 67:
                self.after(0, lambda: self._log("<< STB=67 — end of wafer map."))
                return 67
            self.after(0, lambda stb=stb: self._log_main(
                f"Unexpected result ({stb}) waiting for STB=66/67 — stopping."))
            self._running = False
            return None
        return None

    def _update_current_die(self, prober):
        """Refresh self._current_rc from the prober's own live position
        (Q command) and mark it CURRENT on the wafer map. The previous
        die's final color was already set by _mark_touchdown_result()
        right after its touchdown finished — do not touch it again here."""
        try:
            raw = prober.get_xy_position()
            x_die, y_die = _parse_q_response(raw)
            row, col = int(y_die), int(x_die)
        except Exception:
            row, col = self._current_rc
        self._current_rc = (row, col)
        self.after(0, lambda: self.die_var.set(f"Die: R{row}C{col}"))
        self.after(0, lambda: self.wafer_map.update_die(row, col, "CURRENT"))

    def _mark_touchdown_result(self):
        row, col = self._current_rc
        if row is None:
            return
        status = "PASS" if (self._touchdown_packets > 0 and self._touchdown_errors == 0) else "FAIL"
        if status == "PASS":
            self._pass_count += 1
        else:
            self._fail_count += 1
        self.after(0, self._update_pass_fail_display)
        self.after(0, lambda: self.wafer_map.update_die(row, col, status))

    def _reset_counts(self):
        """Zero the running pass/fail tally — called automatically at the
        start of each lot (matching Main's own "▶ Run" tab resetting its
        counters on Full Die/Test Die start), and available as a manual
        button on the Run tab too."""
        self._pass_count = 0
        self._fail_count = 0
        self._update_pass_fail_display()

    def _update_pass_fail_display(self):
        self.pass_var.set(str(self._pass_count))
        self.fail_var.set(str(self._fail_count))
        total = self._pass_count + self._fail_count
        if total:
            pct = 100.0 * self._pass_count / total
            self.yield_var.set(f"Yield: {pct:.1f}%  ({self._pass_count}/{total})")
        else:
            self.yield_var.set("Yield: —")
