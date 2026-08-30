"""NanoZ board discovery/connect + a raw command console, for the
Electroglas NanoZ Setup tab - mirrors gui/nanoz_panel.py's own Setup tab
(boards + console), minus the Connect Prober button (redundant here too -
Electroglas's prober connects via the normal Debug > Instruments tab).

Owns the live board objects (self._boards) and the shared packet queue
(self._queue) - gui/eg_nanoz_recipe_panel.py and gui/eg_nanoz_charts_panel.py
both read through this panel rather than keeping their own copies, so
there is exactly one live connection per board.
"""

import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

import instruments.nanoz_board as nzb


class EgNanozSetupPanel(ttk.Frame):
    _CHIP_LABELS = {"0": "1 (right)", "1": "2 (left)"}

    def __init__(self, parent, controller, get_ata_folder, log_fn):
        super().__init__(parent)
        self.controller = controller
        self._get_ata_folder = get_ata_folder
        self._log = log_fn

        self.identities: dict[str, nzb.BoardIdentity] = {}   # serial_number -> identity
        self.boards: dict[str, nzb.NanoZBoard] = {}          # serial_number -> live board
        self.queue: "queue.Queue" = queue.Queue()
        # Packet listeners (e.g. the Charts tab) - fn(packet_dict). Called
        # for every packet as it's drained, in addition to this panel's own
        # console handling - see subscribe().
        self._listeners = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_boards_row()
        self._build_console_row()

        self._load_known_boards()
        self.after(150, self._drain_queue_loop)

    def subscribe(self, fn):
        self._listeners.append(fn)

    # -- boards -----------------------------------------------------------

    def _build_boards_row(self):
        lf = ttk.LabelFrame(self, text="NanoZ Boards  (all connected boards are always live)",
                            padding=6)
        lf.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        lf.columnconfigure(0, weight=1)

        bar = ttk.Frame(lf)
        bar.pack(fill="x", pady=(0, 4))
        ttk.Button(bar, text="🔍 Discover Boards", command=self._discover_boards).pack(side="left")
        ttk.Button(bar, text="🔌 Connect All", command=self._connect_all).pack(
            side="left", padx=(6, 0))
        ttk.Button(bar, text="🔌 Disconnect All", command=self._disconnect_all).pack(
            side="left", padx=(6, 0))
        ttk.Button(bar, text="Edit Slots...", command=self._edit_selected_slots).pack(
            side="left", padx=(6, 0))

        cols = ("sn", "port", "fw", "slot0", "slot1", "state", "spl", "env")
        self._tree = ttk.Treeview(lf, columns=cols, show="headings", height=8)
        for col, head, width in (("sn", "Serial", 140), ("port", "Port", 70),
                                 ("fw", "Firmware", 90), ("slot0", "Chip0 slot", 80),
                                 ("slot1", "Chip1 slot", 80), ("state", "State", 90),
                                 ("spl", "SPL#", 50), ("env", "ENV#", 50)):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=width, anchor="w")
        self._tree.pack(fill="x")

    def _load_known_boards(self):
        folder = self._get_ata_folder()
        if not folder:
            return
        for ident in nzb.load_known_boards(folder):
            if ident.serial_number:
                self.identities.setdefault(ident.serial_number, ident)
        self._refresh_tree()

    def save_known_boards(self):
        folder = self._get_ata_folder()
        if folder:
            nzb.save_known_boards(folder, list(self.identities.values()))

    def on_ata_folder_loaded(self):
        self._load_known_boards()

    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        for sn, ident in sorted(self.identities.items()):
            board = self.boards.get(sn)
            state = board.state if board is not None else "not_connected"
            spl = board.spl_count if board is not None else ""
            env = board.env_count if board is not None else ""
            self._tree.insert("", "end", iid=sn, values=(
                sn, ident.port or ident.last_port or "", ident.firmware,
                ident.slot0 if ident.slot0 is not None else "",
                ident.slot1 if ident.slot1 is not None else "", state, spl, env))
        self._refresh_console_boards()

    def _discover_boards(self):
        def _work():
            found = nzb.discover_boards(log=lambda m: self.after(0, lambda: self._log(f"[NANOZ] {m}")))
            for ident in found:
                if ident.serial_number:
                    self.identities[ident.serial_number] = ident
            self.after(0, self._refresh_tree)
            self.after(0, self.save_known_boards)
        threading.Thread(target=_work, daemon=True).start()

    def _connect_all(self):
        for sn, ident in list(self.identities.items()):
            if sn in self.boards:
                continue
            port = ident.port or ident.last_port
            if not port:
                self._log(f"[NANOZ] {sn}: no known port - run Discover Boards first.")
                continue
            ident.port = port
            board = nzb.NanoZBoard(ident, self.queue, env_interval_s=1.0)
            try:
                board.start()
            except Exception as e:
                self._log(f"[NANOZ] {sn}: connect failed - {e}")
                continue
            self.boards[sn] = board
        self._refresh_tree()

    def _disconnect_all(self):
        for sn, board in list(self.boards.items()):
            try:
                board.stop()
            except Exception:
                pass
        self.boards.clear()
        self._refresh_tree()

    def _edit_selected_slots(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Edit Slots", "Select a board row first.")
            return
        sn = sel[0]
        ident = self.identities.get(sn)
        if ident is None:
            return
        dlg = tk.Toplevel(self)
        dlg.title(f"Slots for {sn}")
        dlg.transient(self)
        dlg.grab_set()
        v0 = tk.StringVar(value=str(ident.slot0) if ident.slot0 is not None else "")
        v1 = tk.StringVar(value=str(ident.slot1) if ident.slot1 is not None else "")
        frm = ttk.Frame(dlg, padding=10)
        frm.pack()
        ttk.Label(frm, text="Chip 0 (right) physical slot (1-20):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=v0, width=6).grid(row=0, column=1)
        ttk.Label(frm, text="Chip 1 (left) physical slot (1-20):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=v1, width=6).grid(row=1, column=1)

        def _save():
            def _parse(v):
                v = v.strip()
                return int(v) if v else None
            try:
                ident.slot0, ident.slot1 = _parse(v0.get()), _parse(v1.get())
            except ValueError:
                messagebox.showerror("Edit Slots", "Slots must be whole numbers.")
                return
            self.save_known_boards()
            self._refresh_tree()
            dlg.destroy()
        ttk.Button(frm, text="Save", command=_save).grid(row=2, column=0, columnspan=2, pady=(8, 0))

    # -- console ------------------------------------------------------------

    def _build_console_row(self):
        lf = ttk.LabelFrame(self, text="Board Console", padding=6)
        lf.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 6))
        lf.rowconfigure(2, weight=1)
        lf.columnconfigure(0, weight=1)

        pick = ttk.Frame(lf)
        pick.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(pick, text="Board:").pack(side="left")
        self._console_board_var = tk.StringVar(value="")
        self._console_board_cb = ttk.Combobox(pick, textvariable=self._console_board_var,
                                              state="readonly", width=18)
        self._console_board_cb.pack(side="left", padx=(4, 12))
        ttk.Label(pick, text="Chip:").pack(side="left")
        self._console_chip_var = tk.StringVar(value=self._CHIP_LABELS["0"])
        ttk.Combobox(pick, textvariable=self._console_chip_var, state="readonly", width=12,
                    values=list(self._CHIP_LABELS.values())).pack(side="left", padx=(4, 0))

        cmds = ttk.Frame(lf)
        cmds.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        for label, cmd in (("ver", "ver"), ("whoami", "whoami"), ("#env?", "#env?"),
                          ("calib ?", "calib ?"), ("pause", "pause")):
            ttk.Button(cmds, text=label, width=9,
                      command=lambda c=cmd: self._send(c)).pack(side="left", padx=2)
        ttk.Label(cmds, text="Cycle #:").pack(side="left", padx=(10, 2))
        self._cycle_var = tk.StringVar(value="0")
        ttk.Entry(cmds, textvariable=self._cycle_var, width=5).pack(side="left")
        ttk.Button(cmds, text="▶ run", command=self._run_cycle_console
                  ).pack(side="left", padx=(4, 10))
        ttk.Label(cmds, text="Raw:").pack(side="left")
        self._raw_var = tk.StringVar(value="")
        ttk.Entry(cmds, textvariable=self._raw_var, width=16).pack(side="left", padx=(4, 4))
        ttk.Button(cmds, text="Send", command=lambda: self._send(self._raw_var.get())
                  ).pack(side="left")

        self._console_text = tk.Text(lf, wrap="none", state="disabled", height=10,
                                     font=("Consolas", 9))
        self._console_text.grid(row=2, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, orient="vertical", command=self._console_text.yview)
        sb.grid(row=2, column=1, sticky="ns")
        self._console_text.configure(yscrollcommand=sb.set)

    def _refresh_console_boards(self):
        sns = sorted(self.identities.keys())
        self._console_board_cb.config(values=sns)
        if not self._console_board_var.get() and sns:
            self._console_board_var.set(sns[0])

    def _selected_board(self):
        return self.boards.get(self._console_board_var.get())

    def _send(self, cmd):
        board = self._selected_board()
        if not board or not board.ser:
            messagebox.showwarning("Console", "Select a connected board first.")
            return
        board.send_raw(cmd)
        self._console_log(f">> {cmd}")

    def _run_cycle_console(self):
        board = self._selected_board()
        if not board or not board.ser:
            messagebox.showwarning("Console", "Select a connected board first.")
            return
        try:
            cycle = int(self._cycle_var.get())
        except ValueError:
            messagebox.showerror("Console", "Cycle # must be a whole number.")
            return
        board.run_cycle(cycle)
        self._console_log(f">> run {cycle}")

    def _console_log(self, text):
        self._console_text.config(state="normal")
        self._console_text.insert("end", text + "\n")
        self._console_text.see("end")
        self._console_text.config(state="disabled")

    def _drain_queue_loop(self):
        try:
            while True:
                item = self.queue.get_nowait()
                self._handle_packet(item)
        except queue.Empty:
            pass
        self.after(150, self._drain_queue_loop)

    def _handle_packet(self, item: dict):
        for fn in self._listeners:
            try:
                fn(item)
            except Exception:
                pass
        kind = item.get("kind")
        sn = item.get("board_sn")
        if sn != self._console_board_var.get():
            if kind in ("spl", "env"):
                self._refresh_spl_env_counts()
            return
        if kind == "text":
            self._console_log(f"[{sn}] {item.get('text')}")
        elif kind == "unrecognized":
            self._console_log(f"[{sn}] ? {item.get('raw')}")
        elif kind == "spl":
            self._console_log(f"[{sn} chip{item.get('header_chip')}] SPL "
                             f"S1-4 mA: {item.get('adc_current_ma_s1'):.3f} "
                             f"{item.get('adc_current_ma_s2'):.3f} "
                             f"{item.get('adc_current_ma_s3'):.3f} "
                             f"{item.get('adc_current_ma_s4'):.3f}")
        elif kind == "env":
            self._console_log(f"[{sn}] ENV mcu_temp={item.get('mcu_temperature_c'):.1f}C "
                             f"humidity={item.get('humidity_percent'):.1f}%")
        self._refresh_spl_env_counts()

    def _refresh_spl_env_counts(self):
        for sn, board in self.boards.items():
            try:
                self._tree.set(sn, "spl", board.spl_count)
                self._tree.set(sn, "env", board.env_count)
            except tk.TclError:
                pass
