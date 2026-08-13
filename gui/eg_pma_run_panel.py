"""Drive a .PMA recipe on the Electroglas as relative die steps.

HOW THE MACHINE DIVIDES THE WORK. The prober stores no wafer map. The operator
aligns and lands the chuck on a known die; from there the PC holds the map and
walks the recipe. So this panel needs one thing from the operator that it cannot
work out for itself - WHERE THE CHUCK IS RIGHT NOW - and everything after that
is arithmetic.

THE FRAME IS NOW PINNED DOWN (operator, from the original LaMP exe):

  1. the operator aligns and lands the chuck on the ALIGN SITE, near the middle
     of the wafer, and tells the prober that point is its 0,0;
  2. the exe then moves to the TOP-LEFT of the wafer grid and calls THAT 0,0
     internally - the prober never agrees, and does not need to;
  3. everything after is worked out from that top-left origin.

So XMoveFirstFromAlignSite/Y... is the align site -> MAP ORIGIN vector, NOT
align site -> first touchdown as previously recorded here. Confirmed on three
recipes: negating it lands on the wafer's extent centre (exactly for GIAL5,
within the half-pitch grid parity for the other two), while the first touchdown
is nowhere near the origin in any of them. Hence:

    prober_um = (XMoveFirstFromAlignSite + map_x,
                 YMoveFirstFromAlignSite + map_y)      [prober 0,0 = align site]

WHY THIS PANEL STILL STEPS RELATIVELY. The original exe drove absolute MICRON
moves (MA) off that transform and never used die moves at all. Relative MD
steps are what has been verified on this bench, so they stay the default; the
micron path is the more faithful one and removes the die-size trap below, but
it has not yet been run against hardware.

MD STEPS BY THE PROBER'S OWN DIE SIZE, not by anything in the recipe. For a LaMP
electrical recipe that must be the QUAD pitch (7042 x 3284 um for HP LaMP),
twice the physical die, because each touchdown covers a 2x2 shot. Set it wrong
and every step lands between quads. This panel checks the recipe's die size
against a value you confirm, and refuses to run until you have.

Verified on the bench: MD +1/-1 on both axes tracked ?P exactly, 0.5-0.8 s per
move, and returned to the start position exactly. Recipe +X/+Y match MD +1 (+X
right, +Y up).
"""

import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from electroglas_pma import (parse_pma_file, load_touchdowns, align_site_info,
                             format_quad, expand_touchdowns_to_dies, die_grid_index,
                             measurement_plan, workbook_touchdowns, QUAD_ORDER,
                             shot_geometry, slot_names)

# Where LaMP kept its recipes, then the repo's own copies.
_RECIPE_DIRS = (r"C:\_local\data\debug\LaMPElectrical",
                os.path.join(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))), "pma"))

_POS_RE = re.compile(r"X(-?\d+)Y(-?\d+)")

MOTION_DIE = "die"      # MD - relative die indices, the prober does the pitch
MOTION_UM = "um"        # MM - relative microns, the PC does the pitch

# Largest single micron hop before it gets split. A whole-wafer row flyback is
# legitimately ~130 mm, so this is not a "no move is this big" guard like the
# die-step cap - it just keeps any one command bounded.
_MAX_UM_HOP = 150000


def parse_position(reply) -> tuple:
    """'X30Y38' -> (30, 38), or None."""
    m = _POS_RE.match(str(reply or ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def chunk_step(dx: int, dy: int, cap: int) -> list:
    """Split one die step into hops of at most `cap` on each axis.

    The driver refuses a single MD larger than max_die_step - a guard against
    driving off the platen, added after a run of unchecked steps put the chuck
    238 mm past the edge with every one of them acknowledged. Recipe row
    flybacks are routinely bigger than the cap, so they get split here.
    """
    hops = []
    while dx or dy:
        hop_x = max(-cap, min(cap, dx))
        hop_y = max(-cap, min(cap, dy))
        hops.append((hop_x, hop_y))
        dx -= hop_x
        dy -= hop_y
    return hops


class EgPmaRunPanel(ttk.Frame):
    def __init__(self, parent, controller, main_layout=None):
        super().__init__(parent)
        self.controller = controller
        self._main_layout = main_layout

        self._recipe_path = None
        self._fields = {}
        self._touchdowns = []
        self._die_um = (0.0, 0.0)
        self._index = None          # index of the touchdown the chuck is on
        self._anchored = False
        self._size_confirmed = False
        self._running = False
        self._abort = False
        self._rc = {}               # touchdown seq -> one representative (row, col)
        self._cells = {}            # touchdown seq -> every map cell it covers
        self._results = {}          # touchdown seq -> "PASS" / "FAIL"
        self._die_results = {}      # (seq, quad_pos) -> "PASS" / "FAIL"
        self._slot_rc = {}          # seq -> {quad_pos: (row, col)}
        self._last_seq = None       # which square currently holds CURRENT

        self._selected = None
        self._seq_at_rc = {}        # (row, col) -> touchdown seq, for map clicks
        self._die_at_rc = {}        # (row, col) -> that die's record, for naming it
        self._sel_rc = None         # the exact cell clicked, so we can name the corner
        self._shot_window_items = []   # canvas ids for the 2x2 "you are here" box
        self._sel_window_items = []    # canvas ids for the selected touchdown's box
        # Microns asked for but not yet delivered, because MM only moves in
        # whole 2.5 um counts. Carried into the next move - see _move_um.
        self._um_residual = [0.0, 0.0]

        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        self._build_recipe_row()
        self._build_info()
        self._build_anchor()
        self._build_controls()
        self._build_selection()
        self._build_table()

    # -- plumbing -----------------------------------------------------------

    def _log(self, msg: str):
        self.controller.log(msg)

    def _prober(self):
        drv = self.controller.drivers.get("prober")
        return drv if (drv and drv.inst) else None

    def _ui(self, fn):
        try:
            self.after(0, fn)
        except (RuntimeError, tk.TclError):
            pass

    # -- layout -------------------------------------------------------------

    def _build_recipe_row(self):
        row = ttk.Frame(self)
        row.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        row.columnconfigure(1, weight=1)
        ttk.Label(row, text="Recipe:").grid(row=0, column=0, sticky="w")
        self._recipe_var = tk.StringVar(value="(none loaded)")
        ttk.Label(row, textvariable=self._recipe_var, foreground="#0077cc",
                  font=("Consolas", 9)).grid(row=0, column=1, sticky="w", padx=6)
        # Nothing here loads a recipe. The PMA Process tab parses recipes and
        # owns the source folder, and its LOAD ALL is the single entry point -
        # it builds the recipe, adopts it here, and attaches the touchdown
        # list in one go. A second way in from this side let the Run tab and
        # the Recipe tab end up on different PMAs with nothing to say so.
        # adopt_from_process() still runs by itself at startup.

    def _build_info(self):
        lf = ttk.LabelFrame(self, text="Recipe", padding=6)
        lf.grid(row=1, column=0, sticky="ew", padx=6, pady=2)
        self._info_var = tk.StringVar(value="Load a .PMA to begin.")
        ttk.Label(lf, textvariable=self._info_var, font=("Consolas", 8),
                  justify="left").pack(anchor="w")

    def _build_anchor(self):
        lf = ttk.LabelFrame(self, text="Where is the chuck now?", padding=6)
        lf.grid(row=2, column=0, sticky="ew", padx=6, pady=2)
        lf.columnconfigure(1, weight=1)

        ttk.Label(lf, font=("Arial", 8), foreground="#888", justify="left",
                  wraplength=430, text=(
                      "Align, then land the chuck on a die you can name. Nothing moves "
                      "until you set this — the prober holds no map, so this is the only "
                      "thing tying the recipe to the wafer.")
                  ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))

        ttk.Label(lf, text="Chuck is on:").grid(row=1, column=0, sticky="w")
        self._anchor_var = tk.StringVar()
        # Editable, not readonly: a whole-wafer recipe has thousands of sites
        # and scrolling to one is hopeless, so typing filters the list. A die
        # ID can also just be typed straight in - see _set_anchor.
        self._anchor_cb = ttk.Combobox(lf, textvariable=self._anchor_var, width=44)
        self._anchor_cb.grid(row=1, column=1, sticky="ew", padx=6)
        self._anchor_cb.bind("<KeyRelease>", self._on_anchor_typed)
        ttk.Button(lf, text="Set", command=self._set_anchor).grid(row=1, column=2)

        self._anchor_state_var = tk.StringVar(value="not set")
        ttk.Label(lf, textvariable=self._anchor_state_var, font=("Consolas", 8),
                  foreground="#b45309").grid(row=2, column=0, columnspan=3,
                                             sticky="w", pady=(4, 0))

    def _build_controls(self):
        lf = ttk.LabelFrame(self, text="Run", padding=6)
        lf.grid(row=3, column=0, sticky="ew", padx=6, pady=2)

        btns = ttk.Frame(lf)
        btns.pack(fill="x")
        self._back_btn = ttk.Button(btns, text="⏮ Back", command=self._step_back)
        self._back_btn.pack(side="left")
        self._step_btn = ttk.Button(btns, text="⏭ Next", command=self._step_once)
        self._step_btn.pack(side="left", padx=(4, 0))
        self._run_btn = ttk.Button(btns, text="▶ Run", command=self._run_all)
        self._run_btn.pack(side="left", padx=(6, 0))
        self._stop_btn = ttk.Button(btns, text="⏹ Stop", command=self._stop)
        self._stop_btn.pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="↻ Sync ?P", command=self._sync_position).pack(
            side="left", padx=(6, 0))
        ttk.Button(btns, text="🗺 Sync Run map", command=self._sync_run_map).pack(
            side="left", padx=(6, 0))

        mode = ttk.Frame(lf)
        mode.pack(fill="x", pady=(6, 0))
        ttk.Label(mode, text="Move by:").pack(side="left")
        self._motion_var = tk.StringVar(value=MOTION_DIE)
        ttk.Radiobutton(mode, text="die steps (MD)", value=MOTION_DIE,
                        variable=self._motion_var,
                        command=self._on_motion_mode).pack(side="left", padx=(6, 0))
        # MM is a fine positional move, but its count is NOT one micron - a
        # 7042 command travelled 17605 um, a scale of 2.5. The driver now
        # converts microns to MM counts via MM_UNIT_UM, whose value is still
        # unconfirmed between 0.1 mil and 2.5 um; see electroglas_2001x.
        self._um_radio = ttk.Radiobutton(
            mode, text="microns (MM) — scale UNCONFIRMED",
            value=MOTION_UM, variable=self._motion_var,
            command=self._on_motion_mode)
        self._um_radio.pack(side="left", padx=(8, 0))
        self._motion_note = ttk.Label(lf, font=("Arial", 8), foreground="#888",
                                      justify="left", wraplength=430, text="")
        self._motion_note.pack(anchor="w")
        self._on_motion_mode()

        self._status_var = tk.StringVar(value="idle")
        ttk.Label(lf, textvariable=self._status_var, font=("Consolas", 9)
                  ).pack(anchor="w", pady=(6, 0))
        self._pos_var = tk.StringVar(value="—")
        ttk.Label(lf, textvariable=self._pos_var, font=("Consolas", 9),
                  foreground="#0077cc").pack(anchor="w")
        self._shot_window_var = tk.StringVar(value="Shot window: chuck not set")
        ttk.Label(lf, textvariable=self._shot_window_var, font=("Consolas", 8),
                  foreground="#2563eb", wraplength=430, justify="left").pack(
                  anchor="w", pady=(2, 0))

    def _build_selection(self):
        lf = ttk.LabelFrame(self, text="Selected die", padding=6)
        lf.grid(row=4, column=0, sticky="ew", padx=6, pady=2)
        ttk.Label(lf, font=("Arial", 8), foreground="#888", justify="left",
                  wraplength=430, text=("Click a square on the Run tab's wafer map, or a "
                                        "row in the table below.")).pack(anchor="w")
        self._sel_var = tk.StringVar(value="no die selected")
        ttk.Label(lf, textvariable=self._sel_var, font=("Consolas", 8),
                  justify="left").pack(anchor="w", pady=(4, 4))
        self._goto_btn = ttk.Button(lf, text="➤ Move to selected",
                                    command=self._goto_selected)
        self._goto_btn.pack(anchor="w")
        self._goto_btn.state(["disabled"])

    def _build_table(self):
        lf = ttk.LabelFrame(self, text="Touchdowns", padding=4)
        lf.grid(row=5, column=0, sticky="nsew", padx=6, pady=(2, 6))
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        cols = ("seq", "quad", "step", "devices")
        self._tree = ttk.Treeview(lf, columns=cols, show="headings", height=10)
        for col, head, width, stretch in (("seq", "#", 46, False),
                                          ("quad", "quad x,y", 74, False),
                                          ("step", "MD", 64, False),
                                          ("devices", "devices", 260, True)):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=width, anchor="w", stretch=stretch)
        self._tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, orient="vertical", command=self._tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.tag_configure("here", background="#fde68a")
        self._tree.tag_configure("done", foreground="#9ca3af")
        self._tree.bind("<<TreeviewSelect>>", self._on_table_click)

    # -- recipe -------------------------------------------------------------

    def adopt_from_process(self, quiet: bool = True) -> bool:
        """Pull the PMA Process tab's recipe. Returns True if one was taken.

        `quiet` suppresses the "nothing loaded" dialogs so this can run at
        startup, where an empty PMA Process tab is normal rather than an
        error worth interrupting anyone about.
        """
        proc = getattr(self._main_layout, "pma_process", None)
        if proc is None:
            if not quiet:
                messagebox.showinfo("PMA", "The PMA Process tab is not available.")
            return False
        path = getattr(proc, "_pma_path", None)
        fields = getattr(proc, "_fields", None)
        touchdowns = getattr(proc, "_touchdowns", None)
        if not (path and fields and touchdowns):
            if not quiet:
                messagebox.showinfo(
                    "PMA", "No recipe is loaded in the PMA Process tab yet.")
            return False
        self._adopt(path, fields, touchdowns)
        return True

    def _use_loaded_pma(self):
        """Button handler - same as adopt_from_process, but it says so when
        there is nothing to take."""
        self.adopt_from_process(quiet=False)

    def _align_die_from_wafer_tab(self):
        """The align die named by the recipe-generator workbook, if one is loaded.

        Better than inferring it from XMoveFirstFromAlignSite, because it is
        stated rather than derived - so it is preferred when present.
        """
        data = self.wafer_definition_data()
        if isinstance(data, dict) and data.get("align_die"):
            return str(data["align_die"])
        return None

    def _load_recipe(self):
        initial = next((d for d in _RECIPE_DIRS if os.path.isdir(d)), None)
        path = filedialog.askopenfilename(
            title="Load a .PMA recipe", initialdir=initial,
            filetypes=[("PMA recipe", "*.PMA"), ("All files", "*.*")])
        if not path:
            return
        try:
            fields = parse_pma_file(path)
            touchdowns = load_touchdowns(path, fields)
            die = (float(fields["DieSizeX"]), float(fields["DieSizeY"]))
        except Exception as e:
            messagebox.showerror("Recipe", f"Could not load:\n{e}")
            return
        if not touchdowns:
            messagebox.showerror("Recipe", "No touchdowns found — are the .PMV "
                                           "and .PMS siblings next to the .PMA?")
            return
        self._adopt(path, fields, touchdowns)

    def _adopt(self, path: str, fields: dict, touchdowns: list):
        self._recipe_path = path
        self._fields = fields
        self._touchdowns = touchdowns
        self._die_um = (float(fields["DieSizeX"]), float(fields["DieSizeY"]))
        # The chuck can be parked on - and driven to - ANY die on the wafer,
        # not only the ones this recipe probes. So the position list becomes
        # the whole wafer whenever a workbook is loaded, and the .PMA stops
        # being that list: it is now an ORDER over it, applied by
        # _enabled_indices. Keyed on quad coordinates rather than seq, because
        # the workbook and the .PMA number their shots independently.
        self._pma_order_keys = [self._quad(t) for t in touchdowns]
        self._touchdowns = self._map_source_touchdowns()
        self._index = None
        self._anchored = False
        self._size_confirmed = False
        self._rc = {}
        self._cells = {}
        self._results = {}
        self._die_results = {}
        self._last_seq = None
        self._build_rc_index()
        self._recipe_var.set(os.path.basename(path))
        self._fill_info()
        self._fill_anchor_choices()
        self._fill_table()
        self._anchor_state_var.set("not set — pick where the chuck is, then Set")
        self._log(f"[PMA] Loaded {os.path.basename(path)}: {len(touchdowns)} touchdowns, "
                  f"die {self._die_um[0]:.0f} x {self._die_um[1]:.0f} um")

    def forget_recipe(self):
        """Drop the adopted recipe - called when the ATA folder changes.

        Everything here is wafer-specific: the touchdowns, the anchor list, the
        row/col index the map is painted through, and where the chuck is
        believed to be. Carrying any of it across to a different wafer means
        the Run tab and the map disagree about what a square is, which is worse
        than an empty Run tab.
        """
        self._recipe_path = ""
        self._fields = {}
        self._touchdowns = []
        self._pma_order_keys = []
        self._index = None
        self._anchored = False
        self._size_confirmed = False
        self._rc = {}
        self._cells = {}
        self._slot_rc = {}
        self._results = {}
        self._die_results = {}
        self._last_seq = None
        self._anchor_choices = []
        try:
            self._recipe_var.set("(none)")
            self._anchor_cb.config(values=[])
            self._anchor_var.set("")
            self._anchor_state_var.set("not set — load a recipe for this wafer")
            self._info_var.set("No recipe loaded.")
            self._tree.delete(*self._tree.get_children())
            self._clear_selection_window()
            self.update_shot_window()
        except Exception:
            pass
        self._log("[PMA] Run tab cleared — the ATA folder changed, so the "
                  "previous wafer's touchdowns no longer apply.")

    def _fill_info(self):
        f, dx, dy = self._fields, *self._die_um
        n = len(self._touchdowns)
        align = self._align_quad()
        lines = [
            f"die size (quad pitch)  {dx:.0f} x {dy:.0f} um   "
            f"= {dx / 1000:.3f} x {dy / 1000:.3f} mm",
            f"touchdowns this run    {len(self._enabled_indices())}",
        ]
        if len(self._enabled_indices()) != n:
            lines.append(f"wafer positions        {n}  (the chuck can be set "
                         "to, or moved to, any of them)")
        if align:
            lines.append(f"align site             quad ({align[0]:.0f},{align[1]:.0f})")
        n_minor = int(f.get("CountMovesMinor") or 1)
        lines.append(
            f"structure              {f.get('CountMovesMajor', '?')} major"
            + (f" x {n_minor} minor sub-sites per touchdown" if n_minor > 1
               else " moves, ONE die per touchdown (no minor moves)"))
        plan = measurement_plan(f)
        lines.append(f"measurement            {plan['summary']}")
        if plan["wires"]:
            lines.append(f"probe pins needed      {plan['wires']}")
        self._info_var.set("\n".join(lines))

    def _align_info(self):
        """Shared with the PMA Process tab, so the two tabs cannot disagree."""
        return align_site_info(self._fields, self._touchdowns,
                               self._align_die_from_wafer_tab() or "")

    def _align_quad(self):
        """Quad coords of the align site, from the ...FromAlignSite fields."""
        return self._align_info()["quad"]

    def _quad(self, t) -> tuple:
        return (round(t["x"] / self._die_um[0]), round(t["y"] / self._die_um[1]))

    def _align_index(self):
        """Index of the touchdown sitting on the align site, if there is one."""
        td = self._align_info()["quad_touchdown"]
        if td is None:
            return None
        return next((i for i, t in enumerate(self._touchdowns)
                     if t["seq"] == td["seq"]), None)

    def _fill_anchor_choices(self):
        choices = []
        info = self._align_info()
        named = self._align_die_from_wafer_tab()
        if named and info["named_touchdown"] is not None:
            hit = info["named_touchdown"]
            choices.append(f"align die ({named}) — #{hit['seq']} {hit['device_id']}")
        ai = self._align_index()
        if ai is not None:
            t = self._touchdowns[ai]
            label = f"align site — #{t['seq']} {t['device_id']}"
            if label not in choices and not any(f"#{t['seq']} " in c for c in choices):
                choices.append(label)
        # Every site, not the first 40 - the chuck can legitimately be parked
        # anywhere on the wafer, and a truncated list silently made most of
        # them unpickable.
        for t in self._touchdowns:
            choices.append(f"#{t['seq']} {t['device_id']}")
        self._anchor_choices = choices
        self._anchor_cb.config(values=choices)
        self._anchor_var.set(choices[0] if choices else "")

    _ANCHOR_MAX_LISTED = 300

    def _on_anchor_typed(self, event=None):
        """Narrow the dropdown to what the operator has typed.

        Navigation keys are ignored so arrowing through the list does not
        re-filter out from under them.
        """
        if event is not None and event.keysym in (
                "Up", "Down", "Left", "Right", "Return", "Escape", "Tab"):
            return
        text = self._anchor_var.get().strip().lower()
        if not text:
            matches = self._anchor_choices
        else:
            matches = [c for c in self._anchor_choices if text in c.lower()]
        self._anchor_cb.config(values=matches[:self._ANCHOR_MAX_LISTED])

    def _fill_table(self):
        # The run's touchdowns, in run order - not every wafer position.
        # _touchdowns is now the whole wafer, but this table is the recipe's
        # touchdown list and listing 634 rows would bury it. The iid stays the
        # index into _touchdowns so selection still resolves to a position.
        self._tree.delete(*self._tree.get_children())
        prev = None
        for i in self._enabled_indices():
            t = self._touchdowns[i]
            qx, qy = self._quad(t)
            step = "start" if prev is None else \
                f"{qx - prev[0]:+d},{qy - prev[1]:+d}"
            self._tree.insert("", "end", iid=str(i),
                              values=(t["seq"], f"{qx},{qy}", step, t["device_id"]))
            prev = (qx, qy)

    # -- anchoring ----------------------------------------------------------

    def _resolve_anchor(self, choice: str):
        """Index of the touchdown the operator named, or None (with a reason).

        Accepts a picked list entry ("#123 54-00"), a bare sequence ("#123"),
        or a die ID typed straight in ("54-00") - including one die of a quad,
        since that is what is legible under the scope.
        """
        text = (choice or "").strip()
        if not text:
            messagebox.showwarning("Anchor", "Pick or type where the chuck is first.")
            return None

        m = re.search(r"#(\d+)", text)
        if m:
            seq = int(m.group(1))
            idx = next((i for i, t in enumerate(self._touchdowns)
                        if t["seq"] == seq), None)
            if idx is None:
                messagebox.showwarning("Anchor", f"No touchdown #{seq} in this recipe.")
            return idx

        want = text.upper()
        exact = [i for i, t in enumerate(self._touchdowns)
                 if want in {d.strip().upper()
                             for d in (t.get("devices") or [t["device_id"]])}
                 or want == t["device_id"].strip().upper()]
        if len(exact) == 1:
            return exact[0]
        if len(exact) > 1:
            seqs = ", ".join(f"#{self._touchdowns[i]['seq']}" for i in exact[:6])
            messagebox.showwarning(
                "Anchor", f"'{text}' appears at {len(exact)} touchdowns ({seqs}"
                          f"{'…' if len(exact) > 6 else ''}).\n\n"
                          "Pick the one you want from the list instead.")
            return None
        messagebox.showwarning(
            "Anchor", f"No touchdown matches '{text}'.\n\n"
                      "Type a die ID, or pick an entry from the list.")
        return None

    def _set_anchor(self):
        if not self._touchdowns:
            return
        choice = self._anchor_var.get()
        idx = self._resolve_anchor(choice)
        if idx is None:
            return

        dx, dy = self._die_um
        # Only MD depends on the prober's own pitch, so only MD needs this
        # asked. In micron mode the question is meaningless and asking it
        # would train people to click through it.
        if not self._size_confirmed and self._motion_var.get() == MOTION_DIE:
            if not messagebox.askokcancel(
                    "Confirm die size",
                    f"This recipe steps by {dx:.0f} x {dy:.0f} um "
                    f"({dx / 1000:.3f} x {dy / 1000:.3f} mm).\n\n"
                    "MD moves by the PROBER'S configured die size, not this one. "
                    "They must match, or every step lands between quads.\n\n"
                    "Is the prober's SET PRMTR die size set to this?\n\n"
                    "(Switching 'Move by' to microns avoids this entirely.)"):
                return
            self._size_confirmed = True

        self._index = idx
        self._anchored = True
        self._um_residual = [0.0, 0.0]
        t = self._touchdowns[idx]
        qx, qy = self._quad(t)
        self._anchor_state_var.set(f"anchored at #{t['seq']} quad ({qx},{qy}) — "
                                   f"{t['device_id']}")
        self._mark_current()
        self._refresh_position()
        self._log(f"[PMA] Anchored at #{t['seq']} {t['device_id']} quad ({qx},{qy})")

    def _mark_current(self):
        for iid in self._tree.get_children():
            i = int(iid)
            tags = ()
            if self._index is not None:
                if i == self._index:
                    tags = ("here",)
                elif i < self._index:
                    tags = ("done",)
            self._tree.item(iid, tags=tags)
        if self._index is not None:
            self._tree.see(str(self._index))

    def _refresh_position(self):
        if self._index is None:
            self._pos_var.set("—")
            self._mark_on_wafer_map(None)
            return
        t = self._touchdowns[self._index]
        qx, qy = self._quad(t)
        self._pos_var.set(f"#{t['seq']}/{len(self._touchdowns)}  quad ({qx},{qy})  "
                          f"{t['device_id']}")
        self._mark_on_wafer_map(t)
        self._highlight(self._index)

    # -- the Run tab's own wafer map ----------------------------------------
    #
    # WaferMapPanel keys its dies by (row, col), and when a CSV carries x/y but
    # no row/col it derives them by sorting the unique coordinates and indexing
    # them. The same derivation is reproduced here from the touchdown list, so
    # the run can colour the right square without the map having to hand back
    # any mapping. Statuses come from WaferMapPanel.update_die:
    # UNTESTED / CURRENT / CONTACT / TESTING / PASS / FAIL / SKIP / CONTACT_FAIL.

    # The wafer is defined by the recipe-generator .xls, or by an imported CSV
    # of die IDs - never by the .PMA, which only names the subset to visit.
    #
    # Deliberately NOT wafer.workbook_data. That attribute is not the workbook:
    # PmaWaferPanel._refresh_view assigns it whichever source the Wafer Map tab
    # is currently DISPLAYING, so with the view set to "PMA" it holds the
    # touchdown list. Reading it here redrew the whole wafer as just the
    # touchdowns and took every row/col index with it.
    _WAFER_SOURCE_ATTRS = ("_xls_shot_data", "_csv_shot_data")

    def shot_layout(self) -> tuple:
        """(rows, cols) of the die block one touchdown covers.

        Taken from the loaded wafer definition, which carries it, so a 1x5
        strip does not get expanded as though it were the 2x2 LaMP quad. Falls
        back to shot_geometry's inference from the widest device-ID list.
        """
        data = self.wafer_definition_data() or {}
        widest = max(
            (len(str(t.get("device_id", "")).split("/"))
             for t in (self._touchdowns or [])), default=1)
        return shot_geometry(widest, int(data.get("shot_rows") or 0),
                             int(data.get("shot_cols") or 0))

    def wafer_definition_data(self):
        """The loaded source that defines the whole wafer, or None."""
        wafer = getattr(self._main_layout, "pma_wafer", None)
        if wafer is None:
            return None
        for attr in self._WAFER_SOURCE_ATTRS:
            data = getattr(wafer, attr, None)
            if isinstance(data, dict) and data.get("shots"):
                return data
        return None

    def _map_source_touchdowns(self) -> list:
        """Every shot the MAP shows - the workbook's, not this recipe's.

        The recipe generator .xls is the wafer; the .PMA is the subset this
        recipe visits. Deriving the grid from self._touchdowns made a
        15-touchdown gauge recipe index a 15-shot grid, so its dies landed on
        cells 0..7 of a wafer that has hundreds - the map drew only the
        touchdowns, and every row/col was wrong for the real map.
        """
        data = self.wafer_definition_data()
        if data:
            try:
                shots = workbook_touchdowns(data)
                if shots:
                    return shots
            except Exception as e:
                self._log(f"[PMA] Could not read the wafer map from the recipe "
                          f"generator workbook ({type(e).__name__}: {e}) — "
                          "falling back to the PMA's touchdowns.")
        return self._touchdowns

    def _build_rc_index(self):
        """seq -> the map cells that touchdown covers.

        The map carries one cell per DIE, so a 2x2 shot owns four of them and
        a single-die recipe owns one. The row/col derivation has to match
        WaferMapPanel._parse_die_list exactly - sorted unique x/y, densely
        indexed - because that is what decides the cell keys it draws under,
        and it has to be derived from the SAME die set the map was written
        from or every key is off.
        """
        rows, cols = self.shot_layout()
        map_dies = expand_touchdowns_to_dies(self._map_source_touchdowns(),
                                             *self._die_um, rows=rows, cols=cols)
        x_to_col, y_to_row = die_grid_index(map_dies)
        dies = expand_touchdowns_to_dies(self._touchdowns, *self._die_um,
                                         rows=rows, cols=cols)

        self._cells = {}
        self._rc = {}
        self._seq_at_rc = {}
        self._die_at_rc = {}
        self._anchor_rc = {}
        # seq -> {quad_pos: rc}. Every die of the shot, NA corners included, so
        # slot N always lines up with fldSwitch N even where a corner is empty.
        # This is what lets a result be filed against the die it was actually
        # taken on rather than against the shot's anchor cell.
        self._slot_rc = {}
        missing = 0
        for d in dies:
            try:
                rc = (y_to_row[round(d["y"])], x_to_col[round(d["x"])])
            except KeyError:
                # A touchdown at coordinates the workbook has no shot for -
                # the two files are for different wafers. Skip it rather than
                # invent a cell, and say how many.
                missing += 1
                continue
            self._cells.setdefault(d["seq"], []).append(rc)
            self._slot_rc.setdefault(d["seq"], {})[d["quad_pos"]] = rc
            # Only real dies get a reverse mapping - clicking an NA corner
            # should not select the shot, since nothing is probed there.
            if d["enabled"]:
                self._seq_at_rc[rc] = d["seq"]
                self._die_at_rc[rc] = d
                # One cell stands for the whole touchdown wherever a shot has
                # to be named by a single square. It must be an ENABLED die's
                # cell, because that is the only kind _seq_at_rc maps back -
                # a shot like NA/NA/NA/81-10 has just one, and it is not the
                # top-left corner.
                self._anchor_rc.setdefault(d["seq"], rc)
        if missing:
            self._log(f"[PMA] ⚠ {missing} of {len(dies)} recipe dies are not on "
                      "the recipe generator's wafer map — the .PMA and the .xls "
                      "look like they are for different wafers.")
        # Kept for anything that still wants a single representative cell.
        self._rc = {seq: cells[0] for seq, cells in self._cells.items()}

    def _run_map(self):
        return getattr(self._main_layout, "_exec2_wafer_map", None)

    def _results_map(self):
        return getattr(self._main_layout, "_results_wafer_map", None)

    def _paint(self, seq, status: str, also_results: bool = False):
        """Colour one touchdown on the Run tab map. Best effort.

        also_results mirrors it onto the Results tab's map, which the
        Accretech flow does for verdicts only - that map is about outcomes,
        so the transient PROBING highlight does not belong on it.
        """
        self._paint_cells(self._cells.get(seq), status, also_results)

    def _paint_cells(self, cells, status: str, also_results: bool = False):
        """Colour specific map squares - one die's, or a whole touchdown's."""
        if not cells:
            return
        maps = [self._run_map()]
        if also_results:
            maps.append(self._results_map())
        for wmap in maps:
            if wmap is None:
                continue
            for rc in cells:
                try:
                    if rc in wmap.dies:
                        wmap.update_die(rc[0], rc[1], status)
                except Exception:
                    pass

    # -- 2x2 position window ------------------------------------------------
    #
    # Modelled on NanoZ's 1x20 window (nanoz_panel._update_position_window):
    # one outline over the block the head covers rather than per-cell
    # decoration, positions taken from the map's own canvas coords so it
    # follows pan/zoom, and extrapolated from the die pitch when a corner of
    # the block has no die drawn (an NA position, or the wafer edge).

    def _clear_shot_window(self):
        self._clear_items(self._shot_window_items)
        self._shot_window_items = []

    def _clear_selection_window(self):
        self._clear_items(self._sel_window_items)
        self._sel_window_items = []

    def _clear_items(self, items):
        wmap = self._run_map()
        for item in items:
            try:
                wmap.canvas.delete(item)
            except Exception:
                pass

    def _cell_pitch(self, wmap):
        """Canvas (dx, dy) between horizontally and vertically adjacent cells."""
        px = py = None
        for (r, c) in wmap.dies:
            if px is None and (r, c + 1) in wmap.dies:
                a = wmap.canvas.coords(wmap.dies[(r, c)])
                b = wmap.canvas.coords(wmap.dies[(r, c + 1)])
                if a and b:
                    px = b[0] - a[0]
            if py is None and (r + 1, c) in wmap.dies:
                a = wmap.canvas.coords(wmap.dies[(r, c)])
                b = wmap.canvas.coords(wmap.dies[(r + 1, c)])
                if a and b:
                    py = b[1] - a[1]
            if px is not None and py is not None:
                break
        return px, py

    def _cell_box(self, wmap, rc, pitch):
        """Canvas box for a cell, extrapolated from a neighbour if not drawn."""
        item = wmap.dies.get(rc)
        if item is not None:
            coords = wmap.canvas.coords(item)
            if len(coords) >= 4:
                return coords
        px, py = pitch
        if px is None or py is None:
            return None
        # Nearest drawn cell, then step over by whole pitches.
        best = None
        for (r, c), it in wmap.dies.items():
            d = abs(r - rc[0]) + abs(c - rc[1])
            if best is None or d < best[0]:
                best = (d, (r, c), it)
        if best is None:
            return None
        _d, (br, bc), it = best
        base = wmap.canvas.coords(it)
        if len(base) < 4:
            return None
        ox, oy = (rc[1] - bc) * px, (rc[0] - br) * py
        return [base[0] + ox, base[1] + oy, base[2] + ox, base[3] + oy]

    def _block_box(self, wmap, cells):
        """Bounding canvas box of a set of cells, or None if none are placeable."""
        pitch = self._cell_pitch(wmap)
        boxes = [b for b in (self._cell_box(wmap, rc, pitch) for rc in cells) if b]
        if not boxes:
            return None
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes))

    def update_shot_window(self):
        """Redraw both canvas overlays this panel owns.

        The Run tab's redraw/zoom hook calls this one name, so the selected
        touchdown's outline rides along with the "you are here" box rather
        than needing its own hook - a zoom scales items in place instead of
        rebuilding, so anything not redrawn here is left behind at the wrong
        size.
        """
        self._draw_shot_window()
        self.update_selection_window()

    def update_selection_window(self):
        """Outline the touchdown the selected die belongs to.

        Deliberately a different colour and dash from the chuck's box: the two
        coincide only when the selection is where the prober already is, and
        the operator needs to see at a glance which is which.
        """
        self._clear_selection_window()
        wmap = self._run_map()
        idx = self._selected
        # The index can outlive the recipe it pointed into (reload, re-sync),
        # so range-check it here rather than trusting every caller to clear it.
        if wmap is None or not self._cells or idx is None \
                or not (0 <= idx < len(self._touchdowns)):
            return
        seq = self._touchdowns[idx]["seq"]
        cells = self._cells.get(seq) or []
        box = self._block_box(wmap, cells) if cells else None
        if not box:
            return
        rect = wmap.canvas.create_rectangle(*box, outline="#d97706", width=2,
                                            dash=(4, 3))
        wmap.canvas.tag_raise(rect)
        self._sel_window_items.append(rect)
        # The one die that was actually clicked gets a tighter ring inside the
        # touchdown box, so "which corner am I on" is answerable too.
        if self._sel_rc is not None:
            cell = self._cell_box(wmap, self._sel_rc, self._cell_pitch(wmap))
            if cell:
                inner = wmap.canvas.create_rectangle(*cell, outline="#d97706",
                                                     width=2)
                wmap.canvas.tag_raise(inner)
                self._sel_window_items.append(inner)

    def _draw_shot_window(self):
        """Outline the 2x2 (or 1x1) block the chuck is currently on."""
        self._clear_shot_window()
        wmap = self._run_map()
        if wmap is None or self._index is None or not self._cells:
            self._shot_window_var.set("Shot window: chuck not set")
            return
        seq = self._touchdowns[self._index]["seq"]
        cells = self._cells.get(seq) or []
        if not cells:
            self._shot_window_var.set("Shot window: not on the map")
            return
        box = self._block_box(wmap, cells)
        if not box:
            self._shot_window_var.set("Shot window: off the drawn map")
            return
        rect = wmap.canvas.create_rectangle(*box, outline="#2563eb", width=3)
        wmap.canvas.tag_raise(rect)
        self._shot_window_items.append(rect)

        t = self._touchdowns[self._index]
        drawn = sum(1 for rc in cells if rc in wmap.dies)
        self._shot_window_var.set(
            f"Shot window #{t['seq']} {len(cells)}-up "
            f"({drawn} die{'' if drawn == 1 else 's'} on the map):  "
            f"{format_quad(t['device_id'], *self.shot_layout())}")

    def mark_die_result(self, seq, quad_pos: str, passed: bool):
        """Record and paint ONE die's verdict.

        A shot carries four dies and they pass or fail independently, so the
        square that goes green or red is the die's own - not all four corners
        painted with the shot's combined verdict, which is what a per-touchdown
        mark_result() did. Counted per die too: three probed shots is twelve
        die results, not three.
        """
        rc = (self._slot_rc.get(seq) or {}).get(quad_pos)
        if rc is None:
            return
        key = (seq, quad_pos)
        was = self._die_results.get(key)
        self._die_results[key] = "PASS" if passed else "FAIL"
        self._paint_cells([rc], self._die_results[key], also_results=True)
        self._tally(was, self._die_results[key])

    def mark_result(self, seq, passed: bool):
        """Record and paint a whole touchdown's verdict.

        Retained for the case where nothing reported per-die verdicts - the
        shot's four squares then share one colour, which is better than none.
        """
        was = self._results.get(seq)
        self._results[seq] = "PASS" if passed else "FAIL"
        self._paint(seq, self._results[seq], also_results=True)
        self._tally(was, self._results[seq])

    def _tally(self, was: str, now: str):
        """Move one result between the PASS/FAIL columns.

        Counted once per thing measured. Re-probing the same die (Back, then
        forward again) must not inflate the totals, and a changed verdict has
        to move the count from one column to the other rather than add to both.
        """
        if was == now:
            return
        layout = self._main_layout
        add_pass = getattr(layout, "_exec2_add_pass", None)
        add_fail = getattr(layout, "_exec2_add_fail", None)
        if not (add_pass and add_fail):
            return
        try:
            if was in ("PASS", "FAIL"):
                var = (layout._exec2_pass_var if was == "PASS"
                       else layout._exec2_fail_var)
                var.set(max(0, var.get() - 1))
            (add_pass if now == "PASS" else add_fail)()
        except Exception as e:
            self._log(f"[PMA] Could not update pass/fail counts — "
                      f"{type(e).__name__}: {e}")

    def reset_results(self):
        """Drop recorded verdicts and repaint - pairs with Reset Counts."""
        for seq in list(self._results):
            self._paint(seq, "UNTESTED", also_results=True)
        self._results.clear()
        for (seq, quad), _v in list(self._die_results.items()):
            rc = (self._slot_rc.get(seq) or {}).get(quad)
            if rc is not None:
                self._paint_cells([rc], "UNTESTED", also_results=True)
        self._die_results.clear()
        if self._index is not None:
            self._last_seq = None
            self._highlight(self._index)

    def _restore_colours(self, seq):
        """Repaint a shot with whatever verdicts it actually has.

        Per die when there are per-die verdicts, otherwise the shot's own,
        otherwise untested. Reading only the per-SHOT _results here is what
        erased the run: verdicts now land in _die_results, so _results.get()
        returned "UNTESTED" and every die the run had just coloured went grey
        again the moment the chuck moved on. Only the Run map was affected,
        because this repaint does not mirror to the Results tab - which is why
        the colours survived there and vanished here.
        """
        slots = self._slot_rc.get(seq) or {}
        per_die = {quad: self._die_results.get((seq, quad)) for quad in slots}
        if any(per_die.values()):
            for quad, rc in slots.items():
                self._paint_cells([rc], per_die.get(quad) or "UNTESTED")
            return
        self._paint(seq, self._results.get(seq, "UNTESTED"))

    def _highlight(self, index):
        """Orange-ish CURRENT on the new shot; the one we left keeps its result
        colour if it has one, otherwise goes back to untested."""
        if self._last_seq is not None and self._last_seq != (
                self._touchdowns[index]["seq"] if index is not None else None):
            self._restore_colours(self._last_seq)
        if index is None:
            self._last_seq = None
            self.update_shot_window()
            return
        seq = self._touchdowns[index]["seq"]
        self._paint(seq, "PROBING")
        self._last_seq = seq
        self.update_shot_window()

    def _sync_run_map(self):
        """Point the Run tab's map at this recipe so highlighting has squares.

        Writes the Electroglas wafer-map CSV into the ATA folder only with
        permission - it is the operator's data folder, and an existing file may
        have come from a different recipe.
        """
        layout = self._main_layout
        wmap = self._run_map()
        if wmap is None or layout is None:
            messagebox.showinfo("Run map", "The Run tab's wafer map is not available.")
            return
        if not self._touchdowns:
            messagebox.showinfo("Run map", "Load a recipe first.")
            return
        folder = getattr(layout, "_exec2_map_folder", None) or \
            getattr(layout, "_ata_folder", None)
        if not folder or not os.path.isdir(folder):
            messagebox.showinfo("Run map", "Load an ATA folder on the Run tab first.")
            return

        csv_path = os.path.join(folder, "ata_wafer_map_electroglas.csv")
        existing = 0
        if os.path.isfile(csv_path):
            with open(csv_path, encoding="utf-8-sig") as fh:
                existing = max(0, sum(1 for _ in fh) - 1)
        # The map is per-DIE now, so a 2x2 recipe writes four rows per
        # touchdown. A file written by the older per-shot code has a quarter
        # of the rows and would draw a quarter of the wafer, so the mismatch
        # check compares against the die count and offers to rewrite.
        want = len(expand_touchdowns_to_dies(self._touchdowns, *self._die_um,
                                             *self.shot_layout()))
        if existing != want:
            if not messagebox.askokcancel(
                    "Run map",
                    f"{os.path.basename(csv_path)} has {existing} rows but this "
                    f"recipe has {want} dies across "
                    f"{len(self._touchdowns)} touchdowns.\n\n"
                    "Rewrite it from the loaded recipe?"):
                return
            from electroglas_pma import save_wafer_map_csv
            save_wafer_map_csv(folder, self._touchdowns, self._fields)
            self._log(f"[PMA] Wrote {csv_path} — {want} dies")

        try:
            layout._exec2_map_folder = folder
            layout._exec2_map_source_var.set("Electroglas")
            layout._exec2_draw_wafer_map()
        except Exception as e:
            self._log(f"[PMA] Could not redraw the Run map: {type(e).__name__}: {e}")
            return
        self._build_rc_index()
        self._last_seq = None
        try:
            wmap.set_click_handler(self._on_map_click)
        except AttributeError:
            self._log("[PMA] This wafer map build has no click handler — "
                      "select dies from the table instead")
        if self._index is not None:
            self._highlight(self._index)
        self._log(f"[PMA] Run map synced — {len(self._rc)} shots, click a die to select it")

    def _mark_on_wafer_map(self, touchdown):
        """Ring the current shot on the PMA Wafer tab's map.

        The map is drawn in the same micron frame as the touchdown coordinates,
        so this is a direct hand-off. Best effort - the map is a convenience for
        matching against the scope, and a run must not fail because it is not
        loaded or matplotlib is missing.
        """
        wafer = getattr(self._main_layout, "pma_wafer", None)
        if wafer is None:
            return
        try:
            if touchdown is None:
                wafer.clear_current_shot()
            else:
                label = "/".join(d for d in touchdown["devices"]
                                 if d.strip().upper() != "NA") or touchdown["device_id"]
                wafer.mark_current_shot(touchdown["x"], touchdown["y"],
                                        f"#{touchdown['seq']}  {label}")
        except Exception as e:
            self._log(f"[PMA] wafer map marker skipped — {type(e).__name__}: {e}")

    def _sync_position(self):
        drv = self._prober()
        if not drv:
            self._log("[PMA] Prober not connected")
            return

        def _work():
            drv.recover()
            pos = drv.get_xy_position()
            status = drv.decode_status(drv.get_prober_status())
            self._ui(lambda: (self._status_var.set(f"?P={pos}  {status}"),
                              self._log(f"[PMA] ?P={pos}  {status}")))

        threading.Thread(target=_work, daemon=True).start()

    # -- running ------------------------------------------------------------

    def _guard(self) -> bool:
        if not self._anchored or self._index is None:
            messagebox.showwarning("Run", "Set where the chuck is first.")
            return False
        if not self._prober():
            self._log("[PMA] Prober not connected")
            return False
        if self._running:
            self._log("[PMA] Already running")
            return False
        return True

    # -- which touchdowns this run actually probes ---------------------------
    #
    # The .PMA's move list is the default, not the last word. A recipe may
    # carry its own touchdown list - saved from this tab's map selection - and
    # when it does it OVERRIDES the PMA: the operator picked a subset on
    # purpose. Without this the override was visible on the map and ignored by
    # the run, which is the worst of both.

    def _probe_seqs(self):
        """Touchdown seqs the loaded recipe restricts the run to, or None."""
        panel = getattr(self._main_layout, "recipe_panel", None)
        get_sites = getattr(panel, "get_sites", None)
        if not get_sites:
            return None
        try:
            sites = list(get_sites())
        except Exception:
            return None
        if not sites:
            return None
        seqs = {self._seq_at_rc[rc] for rc in sites if rc in self._seq_at_rc}
        return seqs or None

    def _pma_order(self):
        """Indices of the .PMA's touchdowns, in the order it visits them.

        _touchdowns is the whole wafer in map order, so probing it in index
        order would abandon the route the .PMA lays out. This maps the .PMA's
        sequence onto the position list by quad coordinate.
        """
        index_of = {self._quad(t): i for i, t in enumerate(self._touchdowns)}
        return [index_of[k] for k in getattr(self, "_pma_order_keys", [])
                if k in index_of]

    def _enabled_indices(self):
        """Positions this run probes, in the order it probes them."""
        order = self._pma_order() or list(range(len(self._touchdowns)))
        seqs = self._probe_seqs()
        if seqs is None:
            # No touchdown list on the recipe: fall back to the .PMA's own
            # list, NOT to every position - widening _touchdowns to the wafer
            # must not turn a 15-shot recipe into a 634-shot run.
            return order
        chosen = [i for i in order if self._touchdowns[i]["seq"] in seqs]
        # A die the operator picked that the .PMA never mentions still gets
        # probed - it is on the recipe's list, which overrides the .PMA.
        seen = set(chosen)
        chosen.extend(i for i, t in enumerate(self._touchdowns)
                      if t["seq"] in seqs and i not in seen)
        return chosen

    def _next_enabled_index(self, after):
        """The position after `after` in RUN order, not in index order."""
        order = self._enabled_indices()
        if not order:
            return None
        if after is None:
            return order[0]
        try:
            pos = order.index(after)
        except ValueError:
            # Anchored somewhere off the run list - start at its beginning.
            return order[0]
        return order[pos + 1] if pos + 1 < len(order) else None

    def _step_once(self):
        if self._guard():
            self._start(1)

    def _run_all(self):
        if not self._guard():
            return
        enabled = self._enabled_indices()
        # Position in RUN order, not index order - the run follows the .PMA's
        # route over a wafer-wide position list, so "ahead" is not "> index".
        try:
            ahead = enabled[enabled.index(self._index) + 1:]
        except ValueError:
            ahead = enabled
        remaining = len(ahead)
        if remaining <= 0:
            self._log("[PMA] Already at the last touchdown of this run")
            return
        total = len(self._touchdowns)
        subset = (f"\n\nThe loaded recipe restricts this run to {len(enabled)} "
                  f"of the PMA's {total} touchdown(s); the rest are skipped."
                  if len(enabled) != total else "")
        if not messagebox.askokcancel(
                "Run", f"Probe {remaining} more touchdown(s)?{subset}\n\n"
                       "THIS MEASURES. The wafer contacts the probe card and "
                       "the recipe runs on all four dies of each shot.\n\n"
                       "Z is verified against ?S before each measurement — if "
                       "the chuck is not in contact the run stops rather than "
                       "measuring open air. The chuck is separated at the end."):
            return
        self._start(remaining)

    def _stop(self):
        self._abort = True
        self._status_var.set("stopping after the current move…")

    def _publish_total_dies(self) -> int:
        """Tell the stats panel how many DIES this run measures.

        _exec2_total_dies was never set on Electroglas, so "untested" was
        computed as 0 - tested and went negative. It also has to be dies rather
        than touchdowns: three probed shots is twelve die results, and NA
        corners are not dies at all.
        """
        total = 0
        for i in self._enabled_indices():
            devs = self._touchdowns[i].get("devices") or []
            total += sum(1 for d in devs
                         if (d or "").strip().upper() not in ("", "NA"))
        try:
            self._main_layout._exec2_total_dies = total
            self._main_layout._exec2_push_stats()
        except Exception as e:
            self._log(f"[PMA] Could not publish the die total — "
                      f"{type(e).__name__}: {e}")
        return total

    def _start(self, count: int):
        self._running = True
        self._abort = False
        self._publish_total_dies()
        drv = self._prober()
        cap = getattr(drv, "max_die_step", 5)

        def _work():
            done = 0
            try:
                for _ in range(count):
                    if self._abort:
                        break
                    if not self._move_next(drv, cap):
                        break
                    if not self._measure_here(drv):
                        break
                    done += 1
            except Exception as e:
                err = f"{type(e).__name__}: {str(e).splitlines()[0][:80]}"
                self._ui(lambda: self._log(f"[PMA] run aborted — {err}"))
            finally:
                # Separate before leaving the chuck unattended. The prober
                # handles Z around its own moves, but nothing moves after the
                # last touchdown, so without this the needles stay in contact.
                if drv is not None:
                    try:
                        drv.z_down()
                        self._ui(lambda: self._log("[PMA] Chuck separated (Z down)."))
                    except Exception as e:
                        self._ui(lambda: self._log(
                            f"[PMA] ⚠ Could not separate the chuck — "
                            f"{type(e).__name__}: {e}  Check Z before moving."))
                # Cleared here, not in the Tk callback: if the window is gone the
                # callback never runs and the panel would be dead for good.
                self._running = False
            self._ui(lambda: (self._status_var.set(
                f"{'stopped' if self._abort else 'done'} — {done} touchdown(s)"),
                self._mark_current(), self._refresh_position()))

        threading.Thread(target=_work, daemon=True).start()

    def _ensure_contact(self, drv) -> bool:
        """Confirm the chuck really is UP before anything is measured.

        With a clearance set, the prober drops Z, moves, and raises it again by
        itself, so a run normally arrives already in contact - the same
        behaviour the joystick shows. Convenient, but never assumed here. If Z
        is silently down (no clearance, or Z TRAVEL MODE back on auto profile,
        which turns ZU into a no-op) every die measures open air and PASSES.
        A false pass is the one failure worth stopping a run for.
        """
        if drv is None:
            return True
        try:
            status = (drv.get_prober_status() or "").upper()
        except Exception as e:
            self._ui(lambda: self._log(
                f"[PMA] Could not read the Z state ({type(e).__name__}: {e}) — "
                "stopping rather than measuring blind."))
            return False
        if "ZU" in status:
            return True
        # Not in contact. Ask for it once - z_up() verifies against ?S and
        # raises if it did not land, so a no-op cannot pass silently.
        try:
            drv.z_up()
            return True
        except Exception as e:
            self._ui(lambda: self._log(
                f"[PMA] Chuck is not in contact ({status or 'no status'}) and ZU "
                f"failed — {e}  Run stopped; nothing was measured."))
            return False

    def _measure_here(self, drv) -> bool:
        """Measure the touchdown the chuck is on. False stops the run.

        One call covers the whole shot: the recipe repeats its block per die
        with the relay channel and probe-card pins set on each, so all four
        dies of the quad are measured before the chuck moves on.
        """
        layout = self._main_layout
        run_steps = getattr(layout, "_exec2_run_steps_once", None)
        if run_steps is None:
            self._ui(lambda: self._log(
                "[PMA] No measurement engine on this layout — run stopped."))
            return False
        if not self._ensure_contact(drv):
            return False
        t = self._touchdowns[self._index]
        seq, dev = t["seq"], t["device_id"]
        rc = self._anchor_rc.get(seq)
        if rc is not None:
            layout._exec2_current_rc = rc
        # device_id is already the slash-joined quad ("NA/92-74/NA/93-70"),
        # which is exactly what LaMP's fldDieID holds. Without this the export
        # took the die ID of whichever single cell anchored the shot.
        layout._exec2_die_id_override = dev
        # Per-slot die ID and map cell, indexed by QUAD_ORDER so slot N is
        # fldSwitch N. The recipe's step names carry "(Die N)", so this is what
        # turns a result into "this reading belongs to die 83-71, at that
        # square" instead of four readings all filed under the shot's corner.
        slots = self._slot_rc.get(seq, {})
        layout._exec2_die_ids_by_slot = list(t.get("devices") or [])
        order = slot_names(*self.shot_layout())
        layout._exec2_die_rc_by_slot = [slots.get(q) for q in order]
        self._ui(lambda: layout._exec2_die_var.set(f"Die: {dev}"))
        try:
            ok = bool(run_steps())
        except Exception as e:
            self._ui(lambda: self._log(
                f"[PMA] Measurement error at #{seq} {dev} — "
                f"{type(e).__name__}: {e}"))
            return False
        # Per-die verdicts when the recipe produced them, so each die's own
        # square goes green or red and the totals count dies rather than shots.
        slot_verdicts = dict(getattr(layout, "_exec2_slot_verdicts", None) or {})
        if slot_verdicts:
            ids = t.get("devices") or []

            def _mark():
                for slot, passed in sorted(slot_verdicts.items()):
                    order = slot_names(*self.shot_layout())
                    quad = order[slot - 1] if 1 <= slot <= len(order) else None
                    if quad is None:
                        continue
                    die = ids[slot - 1] if slot - 1 < len(ids) else ""
                    # An NA corner is not a die. It is still measured and
                    # logged - LaMP measured all four switches too, and those
                    # readings are how a shorted corner shows up - but it must
                    # not be painted or counted, or empty positions appear as
                    # failed dies and the tally exceeds the die total.
                    if (die or "").strip().upper() in ("", "NA"):
                        self._log(f"[PMA] #{seq} {quad} (no die): "
                                  f"{'in spec' if passed else 'OUT OF SPEC'} "
                                  "— not counted")
                        continue
                    self.mark_die_result(seq, quad, passed)
                    self._log(f"[PMA] #{seq} {quad} {die}: "
                              f"{'PASS' if passed else 'FAIL'}")
            self._ui(_mark)
        else:
            self._ui(lambda: (self.mark_result(seq, ok),
                              self._log(f"[PMA] #{seq} {dev}: "
                                        f"{'PASS' if ok else 'FAIL'}")))
        return True

    @staticmethod
    def _read_position(drv):
        """?P, surviving one link stall. None if it still cannot be read.

        The 2001X intermittently stops answering mid-run - a query times out and
        the link stays wedged until it is drained or cleared. That is a link
        fault, not a motion fault: the moves either side of it land correctly.
        Letting it propagate would abort a 634-touchdown run over a hiccup, so
        one recover() is attempted. If the position still cannot be read the run
        does stop, because continuing without being able to verify where the
        chuck is means probing dies nobody has confirmed.
        """
        try:
            return parse_position(drv.get_xy_position())
        except Exception:
            pass
        try:
            drv.recover()
            return parse_position(drv.get_xy_position())
        except Exception:
            return None

    def _move_next(self, drv, cap: int) -> bool:
        nxt = self._next_enabled_index(self._index)
        if nxt is None:
            self._ui(lambda: self._log(
                "[PMA] No further touchdowns in this recipe's list."))
            return False
        # Skipped touchdowns are still MOVED THROUGH by _move_to_index, which
        # steps die by die - this only decides where to stop and probe.
        return self._move_to_index(drv, cap, nxt)

    def _move_to_index(self, drv, cap: int, target: int) -> bool:
        """Move to any touchdown, forward or back. Returns False to stop.

        Direction is just the sign of the delta - the recipe order is a
        convenience, not a constraint, so stepping back or jumping to a die
        picked off the wafer map all go through here.
        """
        if not 0 <= target < len(self._touchdowns):
            return False
        i = self._index
        cur, nxt = self._touchdowns[i], self._touchdowns[target]
        cx, cy = self._quad(cur)
        nx, ny = self._quad(nxt)
        dx, dy = nx - cx, ny - cy
        if (dx, dy) == (0, 0):
            self._index = target
            self._ui(lambda: (self._mark_current(), self._refresh_position()))
            return True

        if self._motion_var.get() == MOTION_UM:
            return self._move_um(drv, cur, nxt, target, (nx, ny))

        before = self._read_position(drv)
        self._ui(lambda: self._status_var.set(
            f"#{nxt['seq']}  MD {dx:+d},{dy:+d}  {nxt['device_id']}"))

        for hop_x, hop_y in chunk_step(dx, dy, cap):
            if self._abort:
                return False
            try:
                drv.move_relative_die(hop_x, hop_y)
            except Exception as e:
                msg = f"{type(e).__name__}: {str(e).splitlines()[0][:70]}"
                self._ui(lambda: self._log(
                    f"[PMA] #{nxt['seq']} MD {hop_x:+d},{hop_y:+d} FAILED — {msg}"))
                return False

        after = self._read_position(drv)
        # The prober counts dies in its own frame, but the DELTA must match what
        # was commanded. If it does not, the map and the machine have diverged
        # and continuing would probe the wrong dies.
        if before is None or after is None:
            self._ui(lambda: self._log(
                f"[PMA] STOPPED at #{nxt['seq']}: could not read ?P to confirm the "
                "move, even after a recover(). The move itself may well have "
                "landed — re-anchor once the link is back rather than assuming."))
            return False
        got = (after[0] - before[0], after[1] - before[1])
        if got != (dx, dy):
            self._ui(lambda: self._log(
                f"[PMA] STOPPED at #{nxt['seq']}: commanded ({dx:+d},{dy:+d}) "
                f"but ?P moved ({got[0]:+d},{got[1]:+d}) — "
                f"{before} -> {after}. Map and machine have diverged."))
            return False

        self._index = target
        self._ui(lambda: (self._mark_current(), self._refresh_position()))
        self._ui(lambda: self._log(
            f"[PMA] #{nxt['seq']} MD {dx:+d},{dy:+d} -> quad ({nx},{ny})  "
            f"{nxt['device_id']}"))
        return True

    def _move_um(self, drv, cur, nxt, target, quad) -> bool:
        """Relative MICRON move (MM), the way the original LaMP exe worked.

        The recipe's own coordinates are microns, so the delta between two
        touchdowns is the move, with no die-size arithmetic.

        That does NOT make it assumption-free. MM's count is 2.5 um, measured
        rather than documented, and why it is 2.5 is unknown - if it comes
        from a prober configuration setting then this mode swaps a dependency
        on the die size for a dependency on that, which is no better and is
        harder to notice. MD stays the default until the 2.5 is explained.

        Signs are deliberately the SAME as the MD path (delta straight from
        the recipe, no flip), because MD deltas are themselves recipe deltas
        divided by the pitch and that path is bench-verified.

        Verification is necessarily weaker. ?P counts DIES, in the prober's
        own pitch, so it can only confirm a micron move when that pitch
        happens to match the recipe - which is exactly the assumption this
        mode exists to avoid. So a ?P mismatch is reported and not treated as
        divergence; the driver's own MC/MF acknowledgement check is what
        catches a refused move.
        """
        # Carry the sub-count remainder. A quad step is 7042 um and a count is
        # 2.5 um, so 2816.8 counts - and rounding the SAME way every step makes
        # the error accumulate linearly, ~317 um over a 634-touchdown recipe.
        # Adding back what was not delivered last time keeps the total error
        # bounded by half a count instead of growing without limit.
        want_x = (nxt["x"] - cur["x"]) + self._um_residual[0]
        want_y = (nxt["y"] - cur["y"]) + self._um_residual[1]
        dx_um = int(round(want_x))
        dy_um = int(round(want_y))
        before = self._read_position(drv)
        self._ui(lambda: self._status_var.set(
            f"#{nxt['seq']}  MM {dx_um:+d},{dy_um:+d} um  {nxt['device_id']}"))

        for hop_x, hop_y in chunk_step(dx_um, dy_um, _MAX_UM_HOP):
            if self._abort:
                return False
            try:
                drv.move_relative_um(hop_x, hop_y)
            except Exception as e:
                msg = f"{type(e).__name__}: {str(e).splitlines()[0][:70]}"
                self._ui(lambda: self._log(
                    f"[PMA] #{nxt['seq']} MM {hop_x:+d},{hop_y:+d} um FAILED — {msg}"))
                return False

        after = self._read_position(drv)
        note = ""
        if before is not None and after is not None:
            got = (after[0] - before[0], after[1] - before[1])
            dxq, dyq = quad[0] - self._quad(cur)[0], quad[1] - self._quad(cur)[1]
            if got != (dxq, dyq):
                note = (f"   [?P moved ({got[0]:+d},{got[1]:+d}) dies, recipe step "
                        f"is ({dxq:+d},{dyq:+d}) — the prober's die size differs "
                        f"from the recipe's, which does not affect a micron move]")

        # What the prober was actually able to deliver, to the nearest count.
        unit = float(getattr(drv, "MM_UNIT_UM", 1.0)) or 1.0
        self._um_residual = [want_x - round(dx_um / unit) * unit,
                             want_y - round(dy_um / unit) * unit]

        self._index = target
        self._ui(lambda: (self._mark_current(), self._refresh_position()))
        self._ui(lambda: self._log(
            f"[PMA] #{nxt['seq']} MM {dx_um:+d},{dy_um:+d} um -> quad "
            f"({quad[0]},{quad[1]})  {nxt['device_id']}{note}"))
        return True

    def _on_motion_mode(self):
        um = self._motion_var.get() == MOTION_UM
        self._motion_note.config(text=(
            "Microns, converted to MM counts by the driver. The count size is "
            "NOT 1 um — measured 2.5 um/count, most likely 0.1 mil (2.54). "
            "Those two differ by 1.6%, so confirm over a long move before "
            "trusting this on a wafer that matters."
            if um else
            "Relative die-index moves (MD). The PROBER applies the pitch, so "
            "its SET PRMTR die size must match this recipe or every touchdown "
            "lands between sites. ?P fully verifies each move, and the step is "
            "bounds-checked."))

    # -- selection: pick a die on the map or in the table --------------------

    def _on_map_click(self, row: int, col: int):
        """A die was clicked on the Run tab's wafer map."""
        seq = self._seq_at_rc.get((row, col))
        if seq is None:
            self._select(None)
            return
        idx = next((i for i, t in enumerate(self._touchdowns) if t["seq"] == seq), None)
        self._select(idx, clicked_rc=(row, col))
        if idx is not None:
            self._tree.selection_set(str(idx))
            self._tree.see(str(idx))

    def _on_table_click(self, _event=None):
        sel = self._tree.selection()
        self._select(int(sel[0]) if sel else None)

    def _select(self, index, clicked_rc=None):
        self._selected = index
        self._sel_rc = clicked_rc
        if index is None:
            self._sel_var.set("no die selected")
            self._goto_btn.state(["disabled"])
            self.update_selection_window()
            return
        t = self._touchdowns[index]
        qx, qy = self._quad(t)
        dies = [d for d in t["devices"] if d.strip().upper() != "NA"]
        na = len(t["devices"]) - len(dies)
        detail = format_quad(t["device_id"], *self.shot_layout())
        # Name the die that was actually clicked, not just the touchdown: on a
        # per-die map the two are different questions.
        die = self._die_at_rc.get(clicked_rc) if clicked_rc else None
        picked = ""
        if die:
            corner = die.get("quad_pos") or "single"
            picked = (f"  clicked {die.get('device_id') or '?'} "
                      f"({corner}) — touchdown #{t['seq']}\n")
        self._sel_var.set(
            f"{picked}"
            f"#{t['seq']}  quad ({qx},{qy})   {len(dies)} die"
            f"{'' if len(dies) == 1 else 's'}"
            f"{f', {na} empty' if na else ''}\n"
            f"  {detail}\n"
            f"  x={t['x']:.0f} um  y={t['y']:.0f} um")
        self.update_selection_window()
        here = "" if self._index is None else \
            f"  ({index - self._index:+d} from here)"
        self._goto_btn.config(text=f"➤ Move to #{t['seq']}{here}")
        self._goto_btn.state(["!disabled"])

    def _goto_selected(self):
        if self._selected is None:
            return
        if not self._guard():
            return
        target = self._selected
        t = self._touchdowns[target]
        cur = self._touchdowns[self._index]
        cx, cy = self._quad(cur)
        nx, ny = self._quad(t)
        if not messagebox.askokcancel(
                "Move", f"Move from #{cur['seq']} to #{t['seq']}?\n\n"
                        f"MD {nx - cx:+d},{ny - cy:+d} die steps\n"
                        f"{t['device_id']}"):
            return
        drv = self._prober()
        cap = getattr(drv, "max_die_step", 5)
        self._running = True
        self._abort = False

        def _work():
            try:
                ok = self._move_to_index(drv, cap, target)
            except Exception as e:
                err = f"{type(e).__name__}: {str(e).splitlines()[0][:80]}"
                self._ui(lambda: self._log(f"[PMA] move failed — {err}"))
                ok = False
            finally:
                self._running = False
            self._ui(lambda: self._status_var.set("moved" if ok else "move stopped"))

        threading.Thread(target=_work, daemon=True).start()

    def _step_back(self):
        if not self._guard():
            return
        if self._index <= 0:
            self._log("[PMA] Already at the first touchdown")
            return
        target = self._index - 1
        drv = self._prober()
        cap = getattr(drv, "max_die_step", 5)
        self._running = True
        self._abort = False

        def _work():
            try:
                self._move_to_index(drv, cap, target)
            except Exception as e:
                err = f"{type(e).__name__}: {str(e).splitlines()[0][:80]}"
                self._ui(lambda: self._log(f"[PMA] back failed — {err}"))
            finally:
                self._running = False
            self._ui(lambda: self._status_var.set("idle"))

        threading.Thread(target=_work, daemon=True).start()
