"""Relay switchbox test panel for the Electroglas bench.

The three GPIB addresses at primary 9 are three cards inside ONE E1300A
mainframe, not three boxes. Only one card is wired to the probe card on
probe03, and two of the three report the same card type (E1364A), so which
address is the wired one has to be established rather than assumed - that is
what the Identify and Continuity Walk sections are for.

See instruments/hp_switchbox.py for the wiring model and
references/probe03mapping for the raw transcription it came from.
"""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from instruments.hp_switchbox import (
    CHANNELS, COAX_OF_CHANNEL, DIE_SETS, GROUND_TERMINAL_CHANNEL, NODE_LABELS,
    NODE_OF_CHANNEL, POLARITY_OF_CHANNEL, conflicts_with, describe_channel,
    die_of_channel,
)

# The wired card is relay2. Established by elimination: with all three fitted
# the backplane reported LADDRs 80, 112 and 120; pulling the BOTTOM E1364-66201
# removed 112, so the top (wired) E1364A is LADDR 80 = secondary address 10.
_BOXES = [("relay2", "★ E1364A  9::10  (LADDR 80) — WIRED"),
          ("relay3", "E1364A  9::14  (LADDR 112) — spare"),
          ("relay1", "E1343A  9::15  (LADDR 120) — mux, spare")]

_DEFAULT_BOX = "relay2"

_BANNER = (
    "All channels OPEN is the safe state: on probe03 an open channel sits on its "
    "NC contact, which is tied to the grounded NC bus, so every probe coax is "
    "grounded rather than floating. Never close two channels on the same side (HI "
    "or LO) — that shorts two probe pins together. The E1364A's relays LATCH, so "
    "the card powers up in whatever state it was left in: hit ALL OPEN before "
    "trusting the state, which is what Read all does automatically on first use."
)


class SwitchboxTestPanel(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._busy = False
        self._walk_index = 0
        self._walk_order = [c for c in CHANNELS if c in COAX_OF_CHANNEL]

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_banner()
        self._build_card_section()
        self._build_routing_section()
        self._build_channel_table()
        self._build_walk_section()

    # -- plumbing -----------------------------------------------------------

    def _log(self, msg: str):
        self.controller.log(msg)

    def _drv(self, key=None):
        key = key or self._box_var.get()
        drv = self.controller.drivers.get(key)
        return drv if (drv and drv.inst) else None

    def _run_bg(self, label: str, fn):
        """Run `fn` off the UI thread, one at a time, with the buttons locked.

        `fn` must not touch Tk. It returns a callable that is run back on the
        main thread with the result, or None.
        """
        if self._busy:
            self._log(f"[RELAY] Busy — {label} ignored")
            return
        self._busy = True
        self._set_busy_label(label)

        def _work():
            done = None
            try:
                done = fn()
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                self._ui(lambda: self._log(f"[RELAY] {label} failed — {err}"))
            finally:
                # Released here, not in the Tk callback: if the window is gone
                # the callback never runs, and a lock that only ever releases on
                # the UI thread would leave every button dead.
                self._busy = False
                self._ui(self._clear_busy)
            if callable(done):
                self._ui(done)

        threading.Thread(target=_work, daemon=True).start()

    def _ui(self, fn):
        """Hand `fn` to the Tk thread, dropping it if the widget is gone."""
        try:
            self.after(0, fn)
        except (RuntimeError, tk.TclError):
            pass

    def _set_busy_label(self, label: str):
        self._status_var.set(f"… {label}")

    def _clear_busy(self):
        self._busy = False
        self._status_var.set("idle")

    # -- sections -----------------------------------------------------------

    def _build_banner(self):
        bar = tk.Label(self, text=_BANNER, bg="#3a2f1a", fg="#f0d090",
                       font=("Arial", 8), justify="left", wraplength=900,
                       anchor="w", padx=8, pady=5)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))

    def _build_card_section(self):
        lf = ttk.LabelFrame(self, text="Which card is wired?", padding=8)
        lf.grid(row=1, column=0, sticky="new", padx=8, pady=4)

        self._box_var = tk.StringVar(value=_DEFAULT_BOX)
        for key, label in _BOXES:
            ttk.Radiobutton(lf, text=label, value=key,
                            variable=self._box_var,
                            command=self._on_box_changed).pack(anchor="w")

        btn = ttk.Frame(lf)
        btn.pack(fill="x", pady=(6, 2))
        ttk.Button(btn, text="Identify cards", command=self._identify).pack(side="left")
        ttk.Button(btn, text="Check assumptions",
                   command=self._check_assumptions).pack(side="left", padx=(6, 0))

        self._ident_txt = tk.Text(lf, height=7, width=46, font=("Consolas", 8),
                                  wrap="none")
        self._ident_txt.pack(fill="both", expand=True, pady=(6, 0))
        self._ident_txt.insert("1.0",
                               "Identify reads *IDN? and SYST:CTYP? on all three\n"
                               "addresses. Read-only — nothing switches.\n\n"
                               "9::10 (LADDR 80) is the wired card, established by\n"
                               "elimination: pulling the bottom E1364-66201 removed\n"
                               "LADDR 112 from the backplane, so the top one is 80.\n"
                               "Logical addresses are set by switches on the cards,\n"
                               "so this holds when the spares are refitted.")
        self._ident_txt.config(state="disabled")

    def _build_routing_section(self):
        lf = ttk.LabelFrame(self, text="Die select — 2×2 shot", padding=8)
        lf.grid(row=1, column=1, sticky="new", padx=8, pady=4)

        ttk.Label(lf, justify="left", font=("Consolas", 8), text=(
            "die 1   CH00 coax3  HI  Input HI     CH01 coax4  LO  Input LO\n"
            "die 2   CH02 coax5  HI  Input HI     CH03 coax6  LO  Input LO\n"
            "die 3   CH08 coax7  HI  Current HI   CH09 coax8  LO  Current LO\n"
            "die 4   CH10 coax9  HI  Current HI   CH11 coax10 LO  Current LO\n\n"
            "Force current, read voltage, expect a high reading (isolation).\n"
            "One HI and one LO closed at a time — everything else grounded.")
                  ).pack(anchor="w")

        tk.Label(lf, justify="left", font=("Arial", 8), bg="#3a2f1a", fg="#f0d090",
                 wraplength=380, padx=6, pady=4, anchor="w", text=(
                     "VERIFY FIRST: two pins per die means Input HI must be commoned "
                     "with Current HI, and Input LO with Current LO — otherwise dies 1–2 "
                     "can only be sensed and dies 3–4 only driven. probe03mapping records "
                     "no such strap. Meter between those adapter terminals before "
                     "trusting any reading.")).pack(fill="x", pady=(6, 0))

        btn = ttk.Frame(lf)
        btn.pack(fill="x", pady=(8, 2))
        ttk.Button(btn, text="■ ALL OPEN (safe)",
                   command=self._all_open).pack(side="left")
        for die in sorted(DIE_SETS):
            ttk.Button(btn, text=f"Die {die}", width=6,
                       command=lambda d=die: self._route(d)).pack(side="left", padx=(4, 0))

        meas = ttk.Frame(lf)
        meas.pack(fill="x", pady=(8, 2))
        ttk.Label(meas, text="E1326B:").pack(side="left")
        ttk.Button(meas, text="Ω 4-wire",
                   command=lambda: self._measure("fres")).pack(side="left", padx=(4, 0))
        ttk.Button(meas, text="DCV",
                   command=lambda: self._measure("dcv")).pack(side="left", padx=(4, 0))
        self._reading_var = tk.StringVar(value="—")
        ttk.Label(meas, textvariable=self._reading_var,
                  font=("Consolas", 10)).pack(side="left", padx=(10, 0))

        self._status_var = tk.StringVar(value="idle")
        ttk.Label(lf, textvariable=self._status_var,
                  font=("Consolas", 8), foreground="gray").pack(anchor="w", pady=(6, 0))

    def _build_channel_table(self):
        lf = ttk.LabelFrame(self, text="Channels (00–15)", padding=8)
        lf.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=4)
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        cols = ("ch", "coax", "closed", "open", "state")
        self._tree = ttk.Treeview(lf, columns=cols, show="headings", height=9)
        for col, head, width in (("ch", "Ch", 44), ("coax", "Coax", 52),
                                 ("closed", "Closed → connects to", 190),
                                 ("open", "Open → connects to", 150),
                                 ("state", "Reads back", 100)):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=width, anchor="w", stretch=(col == "closed"))
        self._tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, orient="vertical", command=self._tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=sb.set)

        for ch in CHANNELS:
            node = NODE_OF_CHANNEL.get(ch)
            if ch == GROUND_TERMINAL_CHANNEL:
                closed, opened, coax = "(NC = ground bus entry)", "—", "—"
            elif node is None:
                closed, opened, coax = "not wired", "not wired", "—"
            else:
                closed = (f"{NODE_LABELS[node]}  ·  die {die_of_channel(ch)} "
                          f"{POLARITY_OF_CHANNEL[ch]}")
                opened = "ground (NC bus)"
                coax = str(COAX_OF_CHANNEL[ch])
            self._tree.insert("", "end", iid=str(ch),
                              values=(f"{ch:02d}", coax, closed, opened, "?"))

        btn = ttk.Frame(lf)
        btn.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Button(btn, text="Read all", command=self._read_all).pack(side="left")
        ttk.Button(btn, text="Close selected",
                   command=self._close_selected).pack(side="left", padx=(6, 0))
        ttk.Button(btn, text="Open selected",
                   command=self._open_selected).pack(side="left", padx=(6, 0))
        ttk.Button(btn, text="Close ONLY selected",
                   command=self._close_only_selected).pack(side="left", padx=(6, 0))

    def _build_walk_section(self):
        lf = ttk.LabelFrame(self, text="Continuity walk — identify the wired card "
                                       "and confirm each coax", padding=8)
        lf.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 8))
        lf.columnconfigure(1, weight=1)

        ttk.Label(lf, justify="left", font=("Arial", 8), foreground="#888", text=(
            "Nothing powered, coax free of the probe card. Step to a channel, then meter "
            "from that coax to the E1326B adapter terminal named below — it should read "
            "short when the channel is closed and short to ground when it is open. If "
            "neither happens, this is not the wired card: pick another address above."
        )).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        ttk.Label(lf, text="Channel:").grid(row=1, column=0, sticky="w")
        self._walk_var = tk.StringVar(value=f"{self._walk_order[0]:02d}")
        combo = ttk.Combobox(lf, textvariable=self._walk_var, width=6, state="readonly",
                             values=[f"{c:02d}" for c in self._walk_order])
        combo.grid(row=1, column=1, sticky="w", padx=4)
        combo.bind("<<ComboboxSelected>>", lambda _e: self._show_walk_expectation())

        row = ttk.Frame(lf)
        row.grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 2))
        ttk.Button(row, text="Close only this", command=self._walk_close).pack(side="left")
        ttk.Button(row, text="Next ▸", command=self._walk_next).pack(side="left", padx=(6, 0))
        ttk.Button(row, text="■ All open", command=self._all_open).pack(side="left", padx=(6, 0))

        self._walk_expect_var = tk.StringVar()
        ttk.Label(lf, textvariable=self._walk_expect_var, font=("Consolas", 9),
                  foreground="#4a8fd0").grid(row=3, column=0, columnspan=3,
                                             sticky="w", pady=(4, 4))

        rec = ttk.Frame(lf)
        rec.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(2, 2))
        ttk.Label(rec, text="Measured:").pack(side="left")
        self._walk_note_var = tk.StringVar()
        ttk.Entry(rec, textvariable=self._walk_note_var, width=46).pack(side="left", padx=4)
        ttk.Button(rec, text="↧ from E1326B",
                   command=lambda: self._measure("fres", into_note=True)).pack(side="left")
        ttk.Button(rec, text="Record", command=self._walk_record).pack(
            side="left", padx=(6, 0))
        ttk.Button(rec, text="Save findings…", command=self._walk_save).pack(
            side="left", padx=(6, 0))

        self._walk_txt = tk.Text(lf, height=6, font=("Consolas", 8), wrap="none")
        self._walk_txt.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(4, 0))

        self._show_walk_expectation()

    # -- actions ------------------------------------------------------------

    def _on_box_changed(self):
        for ch in CHANNELS:
            self._tree.set(str(ch), "state", "?")
        self._log(f"[RELAY] Target switchbox set to {self._box_var.get()}")

    def _identify(self):
        keys = [key for key, _ in _BOXES]

        def _work():
            lines = []
            for key in keys:
                drv = self._drv(key)
                if not drv:
                    lines.append(f"{key:<8} not connected")
                    continue
                try:
                    ident = drv.get_id() or "(no ID)"
                except Exception as e:
                    lines.append(f"{key:<8} ID error: {type(e).__name__}")
                    continue
                lines.append(f"{key:<8} {ident}")
                try:
                    for slot, card in drv.cards():
                        lines.append(f"{'':<8}   slot {slot}: {card}")
                except Exception as e:
                    lines.append(f"{'':<8}   card query failed: {type(e).__name__}")
            text = "\n".join(lines)
            return lambda: self._fill_identify(text)

        self._run_bg("identify", _work)

    def _fill_identify(self, text: str):
        self._ident_txt.config(state="normal")
        self._ident_txt.delete("1.0", "end")
        self._ident_txt.insert("1.0", text)
        self._ident_txt.config(state="disabled")
        for line in text.splitlines():
            self._log(f"[RELAY] {line}")

    def _check_assumptions(self):
        drv = self._drv()
        key = self._box_var.get()
        if not drv:
            self._log(f"[RELAY] {key} not connected")
            return

        def _work():
            problems = drv.verify_wiring_assumptions()
            if not problems:
                return lambda: self._log(
                    f"[RELAY] {key}: card type and channel numbering match "
                    "probe03mapping (E1364A, channels 00–15 accepted)")
            return lambda: [self._log(f"[RELAY] {key}: {p}") for p in problems]

        self._run_bg("check assumptions", _work)

    def _read_all(self):
        drv = self._drv()
        if not drv:
            self._log(f"[RELAY] {self._box_var.get()} not connected")
            return

        def _work():
            states = drv.channel_states()
            return lambda: self._apply_states(states)

        self._run_bg("read all", _work)

    def _apply_states(self, states: dict):
        closed = []
        for ch, is_closed in states.items():
            self._tree.set(str(ch), "state", "CLOSED" if is_closed else "open")
            if is_closed:
                closed.append(ch)
        if closed:
            self._log("[RELAY] closed: " + ", ".join(f"CH{c:02d}" for c in closed))
        else:
            self._log("[RELAY] all channels open (all coax grounded)")

    def _selected_channel(self):
        sel = self._tree.selection()
        if not sel:
            self._log("[RELAY] Select a channel row first")
            return None
        return int(sel[0])

    def _close_selected(self):
        ch = self._selected_channel()
        if ch is None:
            return
        drv = self._drv()
        if not drv:
            self._log(f"[RELAY] {self._box_var.get()} not connected")
            return

        def _work():
            clash = conflicts_with(ch, drv.closed_channels())
            if clash:
                other = clash[0]
                raise ValueError(
                    f"CH{ch:02d} and CH{other:02d} are both "
                    f"{POLARITY_OF_CHANNEL[ch]} side — that would short coax "
                    f"{COAX_OF_CHANNEL[ch]} to coax {COAX_OF_CHANNEL[other]}. "
                    "Use 'Close ONLY selected'.")
            drv.close_channel(ch)
            ok = drv.read_channel(ch)
            return lambda: self._after_switch(ch, ok, "closed")

        self._run_bg(f"close CH{ch:02d}", _work)

    def _open_selected(self):
        ch = self._selected_channel()
        if ch is None:
            return
        drv = self._drv()
        if not drv:
            self._log(f"[RELAY] {self._box_var.get()} not connected")
            return

        def _work():
            drv.open_channel(ch)
            ok = drv.read_channel(ch)
            return lambda: self._after_switch(ch, ok, "opened")

        self._run_bg(f"open CH{ch:02d}", _work)

    def _close_only_selected(self):
        ch = self._selected_channel()
        if ch is None:
            return
        self._close_only(ch)

    def _close_only(self, ch: int):
        drv = self._drv()
        if not drv:
            self._log(f"[RELAY] {self._box_var.get()} not connected")
            return

        def _work():
            ok = drv.close_only(ch)
            return lambda: self._after_switch(ch, ok, "closed (all others open)")

        self._run_bg(f"close only CH{ch:02d}", _work)

    def _after_switch(self, ch: int, ok: bool, what: str):
        self._tree.set(str(ch), "state", "CLOSED" if ok else "open")
        self._log(f"[RELAY] CH{ch:02d} {what} — reads back "
                  f"{'CLOSED' if ok else 'open'} · {describe_channel(ch)}")
        self._read_all()

    def _all_open(self):
        drv = self._drv()
        if not drv:
            self._log(f"[RELAY] {self._box_var.get()} not connected")
            return

        def _work():
            drv.open_all()
            states = drv.channel_states()
            return lambda: (self._apply_states(states),
                            self._log("[RELAY] *RST — all channels open, "
                                      "every coax on the grounded NC bus"))

        self._run_bg("all open", _work)

    def _route(self, die: int):
        drv = self._drv()
        if not drv:
            self._log(f"[RELAY] {self._box_var.get()} not connected")
            return
        channels = DIE_SETS[die]
        if not messagebox.askokcancel(
                f"Select die {die}",
                "Close CH" + ", CH".join(f"{c:02d}" for c in channels) +
                "\n(coax " + ", ".join(str(COAX_OF_CHANNEL[c]) for c in channels) +
                ")\n\nThe other three dies are opened, i.e. grounded.\n\nProceed?"):
            return

        def _work():
            result = drv.route_die(die)
            states = drv.channel_states()
            return lambda: (self._apply_states(states),
                            self._log(f"[RELAY] die {die} selected — " + ", ".join(
                                f"CH{c:02d}={'ok' if v else 'FAILED'}"
                                for c, v in result.items())))

        self._run_bg(f"select die {die}", _work)

    # -- measurement --------------------------------------------------------

    def _measure(self, kind: str, into_note: bool = False):
        """Read the E1326B, the meter the relay NO side is actually wired to.

        Resistance is always 4-wire: a stand-alone E1326B has no 2-wire mode,
        and this wiring feeds its sense and source pairs separately anyway.
        """
        drv = self.controller.drivers.get("dmm_vxi")
        if not (drv and drv.inst):
            self._log("[RELAY] E1326B not connected — it has no GPIB address "
                      "yet; run references/find_vxi_instruments.py")
            return

        def _work():
            if kind == "fres":
                value, unit = drv.measure_resistance_4w(), "Ω"
            else:
                value, unit = drv.measure_voltage_dc(), "V"
            text = f"{value:.6g} {unit}"
            return lambda: self._show_reading(text, into_note)

        self._run_bg(f"measure {kind}", _work)

    def _show_reading(self, text: str, into_note: bool):
        self._reading_var.set(text)
        if into_note:
            self._walk_note_var.set(text)
        self._log(f"[RELAY] E1326B reads {text}")

    # -- continuity walk ----------------------------------------------------

    def _show_walk_expectation(self):
        ch = int(self._walk_var.get())
        self._walk_expect_var.set(describe_channel(ch))

    def _walk_close(self):
        self._show_walk_expectation()
        self._close_only(int(self._walk_var.get()))

    def _walk_next(self):
        current = int(self._walk_var.get())
        try:
            idx = self._walk_order.index(current)
        except ValueError:
            idx = -1
        nxt = self._walk_order[(idx + 1) % len(self._walk_order)]
        self._walk_var.set(f"{nxt:02d}")
        self._show_walk_expectation()
        self._close_only(nxt)

    def _walk_record(self):
        ch = int(self._walk_var.get())
        note = self._walk_note_var.get().strip() or "(no note)"
        line = (f"{self._box_var.get():<8} CH{ch:02d}  coax "
                f"{COAX_OF_CHANNEL.get(ch, '—'):<3} expected "
                f"{NODE_LABELS.get(NODE_OF_CHANNEL.get(ch), '—'):<24} measured: {note}\n")
        self._walk_txt.insert("end", line)
        self._walk_txt.see("end")
        self._walk_note_var.set("")
        self._log(f"[RELAY] recorded — {line.strip()}")

    def _walk_save(self):
        text = self._walk_txt.get("1.0", "end").strip()
        if not text:
            self._log("[RELAY] Nothing recorded yet")
            return
        path = filedialog.asksaveasfilename(
            title="Save continuity findings", defaultextension=".txt",
            initialfile="relay_continuity.txt",
            filetypes=[("Text", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        header = ("Relay continuity walk — probe03\n"
                  "expected column is from references/probe03mapping via "
                  "instruments/hp_switchbox.py\n\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write(header + text + "\n")
        self._log(f"[RELAY] Findings saved to {path}")
