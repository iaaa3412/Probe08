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
from tkinter import ttk, filedialog, messagebox, simpledialog

from wafer_map_view import WaferMapPanel
from instruments.accretech_uf200r import AccretechUF200R
from pma_wafer_panel import parse_plain_csv_wafer_map, merge_with_accretech, centroid_offset
import instruments.nanoz_board as nzb

try:
    import matplotlib
    try:
        matplotlib.use("TkAgg")
    except Exception:
        pass
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    _MPL = True
except ImportError:
    _MPL = False

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
        self._main_layout = main_layout

        self._boards: dict[str, nzb.NanoZBoard] = {}
        self._board_rows: dict[str, str] = {}
        self._board_label_to_port: dict[str, str] = {}
        self._queue: "queue.Queue" = queue.Queue()

        self._running = False
        self._run_mode: str | None = None
        self._lot_thread: threading.Thread | None = None
        self._current_rc = (None, None)
        self._current_touchdown = None  # (start_row, die_col) during a Recipe run only
        self._touchdown_errors = 0
        self._touchdown_packets = 0
        self._spl_total = 0
        self._env_total = 0
        self._pass_count = 0
        self._fail_count = 0
        self._spl_path: str | None = None
        self._env_path: str | None = None
        self._latest_spl: dict[tuple[str, str], dict] = {}
        self._latest_env: dict[str, dict] = {}
        self._latest_eep: dict[str, dict] = {}
        self._spl_history: dict[tuple[str, str], "collections.deque"] = {}
        self._env_history: dict[str, "collections.deque"] = {}
        self._cycle_start_time: "dt.datetime | None" = None
        self._mark_cycle_start()
        self._shots: list[dict] = []
        self._recipe_name_var = tk.StringVar(value="")
        self._current_recipe_name: str | None = None
        self._wafer_plan: "nzb.WaferPlan | None" = None
        self._wafer_plan_path: str | None = None
        self._nzmap_dies_by_rc: dict[tuple[int, int], dict] = {}
        self._nzmap_accr_dies_by_rc: dict[tuple[int, int], dict] = {}
        self._nzmap_source_var = tk.StringVar(value="probe_plan")
        self._show_nzmap_labels_var = tk.BooleanVar(value=True)
        self._nzmap_label_artists: list = []
        self._nzmap_view_debounce_id = None
        self._nzmap_current_labels: list = []
        self._nzmap_csv_data: dict | None = None
        self._nzmap_overlay_die_ids: dict[tuple[int, int], str] = {}
        self._nzmap_overlay_row_offset = 0
        self._nzmap_overlay_col_offset = 0

        self._build_ui()
        self.after(50, self._check_queue)
        self.after(300, self._refresh_charts_loop)
        self.after(500, self._refresh_results_loop)
        self.after(1000, self._auto_refresh_board_status)

    @property
    def _nanoz_ata_folder(self):
        """NanoZ shares the same ATA folder as the rest of the Accretech tab
        - selecting the NanoZ tab (see MainLayout._on_top_tab_changed) makes
        sure it's pointed at NAUTATA rather than tracking its own folder."""
        return getattr(self._main_layout, "_ata_folder", None)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        outer = ttk.PanedWindow(self, orient="vertical")
        outer.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self._outer_pane = outer

        sub_nb = ttk.Notebook(outer)
        self._sub_nb = sub_nb
        outer.add(sub_nb, weight=3)

        self._build_setup_tab(sub_nb)
        self._build_recipe_tab(sub_nb)
        self._build_wafer_map_tab(sub_nb)
        self._build_run_tab(sub_nb)
        self._build_console_tab(sub_nb)
        self._build_charts_tab(sub_nb)
        self._build_results_tab(sub_nb)
        self._build_nanoz_ek_tab(sub_nb)

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
        tab = ttk.Frame(nb)
        nb.add(tab, text="Setup")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        split = ttk.PanedWindow(tab, orient="vertical")
        split.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        boards_lf = ttk.LabelFrame(split, text="NanoZ Boards  (all connected boards are always live)")
        split.add(boards_lf, weight=3)

        brow = ttk.Frame(boards_lf)
        brow.pack(fill="x", padx=6, pady=(6, 2))
        self._btn_discover = ttk.Button(brow, text="🔍 Discover Boards", command=self._discover_boards)
        self._btn_discover.pack(side="left", padx=(0, 4))
        self._btn_connect_boards = ttk.Button(brow, text="🔌 Connect All", command=self._connect_boards)
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

        cols = ("port", "sn", "fw", "sig", "slot0", "slot1", "status", "spl", "env")
        self._board_tree = ttk.Treeview(boards_lf, columns=cols, show="headings", height=6)
        heads = [("port", "Port", 70), ("sn", "S/N", 100), ("fw", "Firmware", 80),
                 ("sig", "Signature", 70), ("slot0", "Slot (chip 0)", 90),
                 ("slot1", "Slot (chip 1)", 90), ("status", "Status", 280),
                 ("spl", "SPL#", 55), ("env", "ENV#", 55)]
        for cid, text, width in heads:
            self._board_tree.heading(cid, text=text)
            self._board_tree.column(cid, width=width, anchor="center" if cid != "sn" else "w")
        self._board_tree.pack(fill="x", padx=6, pady=6)
        ttk.Label(boards_lf,
                  text="Each of the 10 NanoZ boards has two independent chips (0 and 1), each "
                       "wired to its own die position on the probe head — double-click a "
                       "board's Slot (chip 0) / Slot (chip 1) cell to assign that chip's "
                       "physical position (1-20, top to bottom). This is what lets the Recipe "
                       "tab's wafer-plan import know which board+chip sits where.",
                  foreground="#6b7280", wraplength=760, justify="left").pack(
                  anchor="w", padx=6, pady=(0, 6))
        self._board_tree.bind("<Double-1>", self._on_board_tree_double_click)

        prober_lf = ttk.LabelFrame(split, text="Prober")
        split.add(prober_lf, weight=1)
        prow = ttk.Frame(prober_lf)
        prow.pack(fill="x", padx=6, pady=6)
        self._btn_connect_prober = ttk.Button(prow, text="🔌 Connect Prober", command=self._connect_prober)
        self._btn_connect_prober.pack(side="left", padx=(0, 8))
        self.prober_status_var = tk.StringVar(value="Prober: not connected")
        ttk.Label(prow, textvariable=self.prober_status_var, foreground="#6b7280").pack(side="left")

    def _build_recipe_tab(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Recipe")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(3, weight=1)

        ttk.Label(tab,
                  text="Each row is one prober shot (a single touchdown that contacts several "
                       "dies at once). Click a board's cell to include/exclude it from that "
                       "shot — included boards all run their cycle together when the shot "
                       "lands. Shot order is top → bottom.",
                  foreground="#6b7280", wraplength=760, justify="left").grid(
                  row=0, column=0, sticky="w", padx=8, pady=(8, 4))

        name_row = ttk.Frame(tab)
        name_row.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))
        ttk.Label(name_row, text="Recipe:").pack(side="left")
        self._recipe_name_cb = ttk.Combobox(
            name_row, textvariable=self._recipe_name_var, state="readonly", width=26)
        self._recipe_name_cb.pack(side="left", padx=(4, 4))
        self._recipe_name_cb.bind(
            "<<ComboboxSelected>>", lambda _e: self._load_named_recipe())
        ttk.Button(name_row, text="💾 Save As…", command=self._save_recipe_as).pack(
            side="left", padx=2)
        ttk.Button(name_row, text="📂 Load", command=lambda: self._load_named_recipe()).pack(
            side="left", padx=2)
        ttk.Button(name_row, text="🗑 Delete", command=self._delete_named_recipe).pack(
            side="left", padx=2)
        self._recipe_active_lbl = ttk.Label(name_row, text="(no recipe saved yet)",
                                            foreground="#6b7280")
        self._recipe_active_lbl.pack(side="left", padx=(12, 0))

        bar = ttk.Frame(tab)
        bar.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 4))
        self._btn_recipe_add = ttk.Button(bar, text="＋ Add Shot", command=self._add_shot)
        self._btn_recipe_add.pack(side="left", padx=(0, 4))
        self._btn_recipe_dup = ttk.Button(bar, text="⎘ Duplicate", command=self._duplicate_shot)
        self._btn_recipe_dup.pack(side="left", padx=4)
        self._btn_recipe_remove = ttk.Button(bar, text="\U0001f5d1 Remove", command=self._remove_shots)
        self._btn_recipe_remove.pack(side="left", padx=4)
        self._btn_recipe_up = ttk.Button(bar, text="▲", width=3,
                                         command=lambda: self._move_shot(-1))
        self._btn_recipe_up.pack(side="left", padx=(10, 2))
        self._btn_recipe_down = ttk.Button(bar, text="▼", width=3,
                                           command=lambda: self._move_shot(1))
        self._btn_recipe_down.pack(side="left", padx=2)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        self._btn_recipe_enable_all = ttk.Button(bar, text="Enable All Boards",
                                                 command=lambda: self._set_selected_boards(True))
        self._btn_recipe_enable_all.pack(side="left", padx=4)
        self._btn_recipe_disable_all = ttk.Button(bar, text="Disable All Boards",
                                                  command=lambda: self._set_selected_boards(False))
        self._btn_recipe_disable_all.pack(side="left", padx=4)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        self._btn_recipe_import_plan = ttk.Button(bar, text="📥 Import Wafer Plan (.xlsx)…",
                                                   command=self._import_wafer_plan)
        self._btn_recipe_import_plan.pack(side="left", padx=4)
        self._recipe_boards_lbl = ttk.Label(bar, text="", foreground="#6b7280")
        self._recipe_boards_lbl.pack(side="left", padx=(12, 0))

        tree_frame = ttk.Frame(tab)
        tree_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self._recipe_tree = ttk.Treeview(tree_frame, columns=("seq",), show="headings", height=16,
                                         selectmode="extended")
        self._recipe_tree.grid(row=0, column=0, sticky="nsew")
        rvsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._recipe_tree.yview)
        rvsb.grid(row=0, column=1, sticky="ns")
        rhsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self._recipe_tree.xview)
        rhsb.grid(row=1, column=0, sticky="ew")
        self._recipe_tree.configure(yscrollcommand=rvsb.set, xscrollcommand=rhsb.set)
        self._recipe_tree.bind("<Button-1>", self._on_recipe_click)
        self._recipe_tree.bind("<Double-1>", self._on_recipe_double_click)

        self._rebuild_recipe_columns()

    def _recipe_ports(self) -> list:
        return sorted(self._boards.keys())

    def _board_label(self, port: str) -> str:
        board = self._boards.get(port)
        ident = board.identity if board else None
        sn = ident.serial_number if ident and ident.serial_number else ""
        real_port = (ident.port if ident else "") or "not yet connected"
        label = f"SN {sn} ({real_port})" if sn else port
        if ident and (ident.slot0 or ident.slot1):
            s0 = ident.slot0 if ident.slot0 else "—"
            s1 = ident.slot1 if ident.slot1 else "—"
            label += f" · slots {s0}/{s1}"
        return label

    def _port_header(self, port: str) -> str:
        return self._board_label(port)

    def _rebuild_recipe_columns(self):
        ports = self._recipe_ports()
        cols = ("seq", "label", "active") + tuple(ports)
        self._recipe_tree.configure(columns=cols)
        heads = [("seq", "#", 36), ("label", "Label", 220), ("active", "Active", 60)]
        heads += [(p, self._port_header(p), 100) for p in ports]
        for cid, text, width in heads:
            self._recipe_tree.heading(cid, text=text)
            self._recipe_tree.column(cid, width=width, anchor="w" if cid == "label" else "center")
        self._recipe_boards_lbl.config(
            text=f"{len(ports)} board(s) known" if ports
            else "no boards known yet — discover/connect on the Setup tab first")
        self._redraw_recipe_tree()

    def _redraw_recipe_tree(self):
        for iid in self._recipe_tree.get_children():
            self._recipe_tree.delete(iid)
        ports = self._recipe_ports()
        for i, shot in enumerate(self._shots, 1):
            excluded = shot["excluded_boards"]
            active_n = sum(1 for p in ports if p not in excluded)
            vals = [str(i), shot["label"] or f"Shot {i}", f"{active_n}/{len(ports)}"]
            vals += ["·" if p in excluded else "✓" for p in ports]
            self._recipe_tree.insert("", "end", values=vals)

    def _selected_shot_indices(self) -> list:
        return sorted(self._recipe_tree.index(iid) for iid in self._recipe_tree.selection())

    def _selected_shot_index(self):
        idxs = self._selected_shot_indices()
        return idxs[0] if idxs else None

    def _persist_recipe(self):
        folder = self._nanoz_ata_folder
        if not folder or not self._current_recipe_name:
            return
        try:
            nzb.save_named_recipe(folder, self._current_recipe_name, self._shots,
                                  wafer_plan_path=self._wafer_plan_path)
        except OSError as e:
            self._log(f"Could not save NanoZ recipe: {e}")

    def _refresh_recipe_name_cb(self):
        folder = self._nanoz_ata_folder
        names = nzb.list_recipe_names(folder) if folder else []
        self._recipe_name_cb.config(values=names)
        self._run_recipe_name_cb.config(values=names)
        self._recipe_name_var.set(self._current_recipe_name or "")
        active_text = (f"active: {self._current_recipe_name}" if self._current_recipe_name
                      else "(unsaved — 💾 Save As… to keep this recipe)")
        self._recipe_active_lbl.config(text=active_text)
        self._run_recipe_active_lbl.config(text=active_text)

    def _save_recipe_as(self):
        folder = self._nanoz_ata_folder
        if not folder:
            messagebox.showerror("No ATA Folder",
                                 "Load an ATA folder from the toolbar first.")
            return
        if not self._shots:
            messagebox.showinfo("No Shots", "Add or import some shots before saving a recipe.")
            return
        name = simpledialog.askstring(
            "Save Recipe", "Recipe name:",
            initialvalue=self._current_recipe_name or "", parent=self)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if name in nzb.list_recipe_names(folder) and not messagebox.askyesno(
            "Overwrite Recipe", f"A recipe named '{name}' already exists — overwrite it?"):
            return
        nzb.save_named_recipe(folder, name, self._shots, wafer_plan_path=self._wafer_plan_path)
        self._current_recipe_name = name
        self._refresh_recipe_name_cb()
        self._log_main(f"Recipe saved as '{name}' — {len(self._shots)} shot(s). "
                       "Will auto-load next time this ATA folder is opened.")

    def _load_named_recipe(self, name: str | None = None):
        folder = self._nanoz_ata_folder
        if not folder:
            messagebox.showerror("No ATA Folder",
                                 "Load an ATA folder from the toolbar first.")
            return
        name = name or self._recipe_name_var.get()
        if not name:
            messagebox.showinfo("No Recipe Selected", "Pick a recipe from the dropdown first.")
            return
        self._shots = nzb.load_named_recipe(folder, name)
        self._current_recipe_name = name
        nzb.set_active_recipe(folder, name)
        self._redraw_recipe_tree()
        self._refresh_recipe_name_cb()
        self._log_main(f"Recipe '{name}' loaded — {len(self._shots)} shot(s).")
        self._autoload_wafer_plan_for_recipe(folder, name)

    def _autoload_wafer_plan_for_recipe(self, folder: str, name: str):
        """Reload the .xlsx wafer plan a recipe was generated from, if one was
        recorded and the file is still there — keeps the Wafer Map tab in sync
        with whichever recipe is active instead of requiring a manual re-import."""
        path = nzb.get_recipe_wafer_plan_path(folder, name)
        if not path:
            return
        if not os.path.isfile(path):
            self._log_main(f"Recipe '{name}' remembers wafer plan '{path}' but that "
                           "file is no longer there — Wafer Map tab left as-is.")
            return
        threading.Thread(target=self._autoload_wafer_plan_thread, args=(path,),
                         daemon=True).start()

    def _autoload_wafer_plan_thread(self, path: str):
        try:
            plan = nzb.load_wafer_plan(path)
        except Exception as e:
            self.after(0, lambda e=e: self._log_main(
                f"Could not auto-reload wafer plan '{path}': {e}"))
            return

        def _finish():
            self._wafer_plan = plan
            self._wafer_plan_path = path
            self._redraw_nanoz_wafer_map()
            self._log_main(f"Wafer map auto-loaded from '{os.path.basename(path)}' "
                           "alongside the recipe.")
        self.after(0, _finish)

    def _delete_named_recipe(self):
        folder = self._nanoz_ata_folder
        name = self._recipe_name_var.get()
        if not folder or not name:
            return
        if not messagebox.askyesno("Delete Recipe",
                                   f"Delete recipe '{name}'? This cannot be undone."):
            return
        nzb.delete_named_recipe(folder, name)
        if self._current_recipe_name == name:
            self._current_recipe_name = None
        self._refresh_recipe_name_cb()
        self._log_main(f"Recipe '{name}' deleted.")

    def _add_shot(self):
        self._shots.append({"label": "", "excluded_boards": set()})
        self._redraw_recipe_tree()
        self._persist_recipe()
        children = self._recipe_tree.get_children()
        if children:
            self._recipe_tree.selection_set(children[-1])
            self._recipe_tree.see(children[-1])

    def _duplicate_shot(self):
        idx = self._selected_shot_index()
        if idx is None:
            self._log_main("Duplicate Shot: select a shot first.")
            return
        src = self._shots[idx]
        clone = dict(src)
        clone["label"] = (src["label"] + " (copy)") if src["label"] else ""
        clone["excluded_boards"] = set(src["excluded_boards"])
        self._shots.insert(idx + 1, clone)
        self._redraw_recipe_tree()
        self._persist_recipe()
        children = self._recipe_tree.get_children()
        self._recipe_tree.selection_set(children[idx + 1])
        self._recipe_tree.see(children[idx + 1])

    def _remove_shots(self):
        idxs = self._selected_shot_indices()
        if not idxs:
            self._log_main("Remove Shot: select at least one shot first.")
            return
        for i in reversed(idxs):
            del self._shots[i]
        self._redraw_recipe_tree()
        self._persist_recipe()

    def _move_shot(self, delta: int):
        idx = self._selected_shot_index()
        if idx is None:
            return
        new_idx = idx + delta
        if not (0 <= new_idx < len(self._shots)):
            return
        self._shots[idx], self._shots[new_idx] = self._shots[new_idx], self._shots[idx]
        self._redraw_recipe_tree()
        self._persist_recipe()
        children = self._recipe_tree.get_children()
        self._recipe_tree.selection_set(children[new_idx])
        self._recipe_tree.see(children[new_idx])

    def _rename_shot(self, idx: int):
        if not (0 <= idx < len(self._shots)):
            return
        current = self._shots[idx]["label"]
        new = simpledialog.askstring("Rename Shot", "Label for this shot:",
                                     initialvalue=current, parent=self)
        if new is None:
            return
        self._shots[idx]["label"] = new.strip()
        self._redraw_recipe_tree()
        children = self._recipe_tree.get_children()
        if 0 <= idx < len(children):
            self._recipe_tree.selection_set(children[idx])
        self._persist_recipe()

    def _toggle_shot_board(self, idx: int, port: str):
        if not (0 <= idx < len(self._shots)):
            return
        excluded = self._shots[idx]["excluded_boards"]
        if port in excluded:
            excluded.discard(port)
        else:
            excluded.add(port)
        self._redraw_recipe_tree()
        children = self._recipe_tree.get_children()
        if 0 <= idx < len(children):
            self._recipe_tree.selection_set(children[idx])
        self._persist_recipe()

    def _set_selected_boards(self, included: bool):
        idxs = self._selected_shot_indices()
        if not idxs:
            self._log_main("Select at least one shot first.")
            return
        ports = self._recipe_ports()
        for i in idxs:
            self._shots[i]["excluded_boards"] = set() if included else set(ports)
        self._redraw_recipe_tree()
        children = self._recipe_tree.get_children()
        self._recipe_tree.selection_set([children[i] for i in idxs if 0 <= i < len(children)])
        self._persist_recipe()

    def _on_recipe_click(self, event):
        if self._recipe_tree.identify_region(event.x, event.y) != "cell":
            return
        row_iid = self._recipe_tree.identify_row(event.y)
        col_id = self._recipe_tree.identify_column(event.x)
        if not row_iid or not col_id:
            return
        cols = self._recipe_tree["columns"]
        col_idx = int(col_id[1:]) - 1
        if not (0 <= col_idx < len(cols)):
            return
        port = cols[col_idx]
        if port not in self._recipe_ports():
            return
        self._toggle_shot_board(self._recipe_tree.index(row_iid), port)

    def _on_recipe_double_click(self, event):
        if self._recipe_tree.identify_region(event.x, event.y) != "cell":
            return
        row_iid = self._recipe_tree.identify_row(event.y)
        col_id = self._recipe_tree.identify_column(event.x)
        if not row_iid or not col_id:
            return
        cols = self._recipe_tree["columns"]
        col_idx = int(col_id[1:]) - 1
        if not (0 <= col_idx < len(cols)) or cols[col_idx] != "label":
            return
        self._rename_shot(self._recipe_tree.index(row_iid))

    def _import_wafer_plan(self):
        path = filedialog.askopenfilename(
            title="Import Wafer Plan",
            filetypes=[("Excel workbook", "*.xlsx"), ("All files", "*.*")])
        if not path:
            return
        if self._shots and not messagebox.askyesno(
            "Replace Recipe",
            f"This will replace the current recipe ({len(self._shots)} shot(s)) with "
            "shots generated from the wafer plan. Continue?"):
            return
        threading.Thread(target=self._import_wafer_plan_thread, args=(path,), daemon=True).start()

    def _import_wafer_plan_thread(self, path: str):
        try:
            plan = nzb.load_wafer_plan(path)
        except Exception as e:
            self.after(0, lambda e=e: messagebox.showerror("Import Failed", str(e)))
            return
        ports = self._recipe_ports()
        slots_by_port = {p: self._boards[p].identity.chip_slots() for p in ports}
        unassigned = [p for p in ports
                     if not (slots_by_port[p].get("0") or slots_by_port[p].get("1"))]
        shots = nzb.build_shots_from_wafer_plan(plan, ports, slots_by_port)
        stats = nzb.wafer_plan_stats(plan)

        def _finish():
            self._shots = shots
            self._wafer_plan = plan
            self._wafer_plan_path = path
            self._redraw_recipe_tree()
            self._persist_recipe()
            self._redraw_nanoz_wafer_map()
            msg = (f"Wafer plan imported — {len(shots)} touchdown shot(s), "
                  f"probe head {plan.probe_height} dies tall, "
                  f"{plan.dies_per_shot}x{plan.dies_per_shot}-die shots. "
                  f"Physical positions across the whole plan: {stats['product']} product, "
                  f"{stats['reference']} reference (skipped), {stats['off_wafer']} off-wafer.")
            if unassigned:
                msg += (f" {len(unassigned)} known board(s) have no assigned slot and are "
                       f"excluded from every shot: {', '.join(unassigned)} "
                       f"— assign slots on the Setup tab and re-import.")
            self._log_main(msg)
        self.after(0, _finish)

    def _build_wafer_map_tab(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Wafer Map")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)

        ttk.Label(tab,
                  text="Probe Plan is the wafer geometry extracted from the imported "
                       ".xlsx (Recipe tab → Import Wafer Plan) — product dies are blue, "
                       "reference/monitor dies are dark red, and it carries computed die "
                       "serials. Accretech is the wafer map extracted on the Run tab — "
                       "the two are independent views of the same physical wafer, not "
                       "combined. Click a die to see its details.",
                  foreground="#6b7280", wraplength=760, justify="left").grid(
                  row=0, column=0, sticky="w", padx=8, pady=(8, 4))

        src_row = ttk.Frame(tab)
        src_row.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 4))
        ttk.Label(src_row, text="View:").pack(side="left", padx=(0, 4))
        ttk.Radiobutton(src_row, text="Probe Plan (.xlsx)", variable=self._nzmap_source_var,
                        value="probe_plan", command=self._redraw_nanoz_wafer_map).pack(side="left")
        ttk.Radiobutton(src_row, text="Accretech", variable=self._nzmap_source_var,
                        value="accretech", command=self._redraw_nanoz_wafer_map).pack(side="left")
        ttk.Checkbutton(src_row, text="🏷 Die Labels", variable=self._show_nzmap_labels_var,
                       command=self._update_visible_nzmap_labels).pack(side="left", padx=(12, 0))
        ttk.Button(src_row, text="🖌 Overlay CSV…",
                  command=self._nzmap_open_overlay_dialog).pack(side="left", padx=(12, 0))

        if _MPL:
            self._nzmap_fig = Figure(figsize=(8, 8), dpi=100)
            self._nzmap_ax = self._nzmap_fig.add_subplot(111)
            self._nzmap_ax.set_aspect("equal")
            self._nzmap_canvas = FigureCanvasTkAgg(self._nzmap_fig, master=tab)
            self._nzmap_canvas.get_tk_widget().grid(
                row=2, column=0, sticky="nsew", padx=8, pady=(0, 0))
            toolbar = NavigationToolbar2Tk(self._nzmap_canvas, tab, pack_toolbar=False)
            toolbar.update()
            toolbar.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 4))
            self._nzmap_canvas.mpl_connect("button_press_event", self._on_nzmap_click)
            self._nzmap_canvas.mpl_connect("scroll_event", self._on_nzmap_scroll_zoom)

            info_lf = ttk.LabelFrame(tab, text="Selected Die")
            info_lf.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 8))
            self._nzmap_die_var = tk.StringVar(value="Click a die to see its row/col/serial.")
            ttk.Label(info_lf, textvariable=self._nzmap_die_var,
                     font=("Consolas", 10)).pack(anchor="w", padx=6, pady=6)
            self._draw_empty_nzmap()
        else:
            ttk.Label(tab, text="matplotlib not installed — install it to view the wafer map.",
                     foreground="red").grid(row=2, column=0, sticky="nw", padx=10, pady=10)

    def _draw_empty_nzmap(self, message: str | None = None):
        if not _MPL:
            return
        self._nzmap_current_labels = []
        self._nzmap_label_artists = []
        self._nzmap_ax.clear()
        self._nzmap_ax.set_aspect("equal")
        self._nzmap_ax.text(
            0.5, 0.5, message or "No wafer plan imported yet — "
                                 "Recipe tab → Import Wafer Plan (.xlsx)",
            ha="center", va="center", transform=self._nzmap_ax.transAxes, color="#999999")
        self._nzmap_canvas.draw_idle()

    def _redraw_nanoz_wafer_map(self):
        if not _MPL:
            return
        self._nzmap_dies_by_rc = {}
        self._nzmap_accr_dies_by_rc = {}
        if self._nzmap_source_var.get() == "accretech":
            self._draw_accretech_nzmap()
        else:
            self._draw_probe_plan_nzmap()

    def _draw_probe_plan_nzmap(self):
        plan = self._wafer_plan
        if plan is None:
            self._draw_empty_nzmap()
            return
        dies = nzb.wafer_plan_die_grid(plan)
        self._nzmap_dies_by_rc = {(d["row"], d["col"]): d for d in dies}
        self._nzmap_ax.clear()
        self._nzmap_ax.set_aspect("equal")
        patches = [Rectangle((d["col"] - 0.5, -d["row"] - 0.5), 1, 1) for d in dies]
        colors = ["#8b0000" if d["status"] == "reference" else "#7aaec8" for d in dies]
        coll = PatchCollection(patches, edgecolor="#1e293b", linewidths=0.4)
        coll.set_facecolor(colors)
        self._nzmap_ax.add_collection(coll)
        max_col = max((d["col"] for d in dies), default=1)
        max_row = max((d["row"] for d in dies), default=1)
        self._nzmap_ax.set_xlim(0, max_col + 1)
        self._nzmap_ax.set_ylim(-(max_row + 1), 0)
        self._nzmap_ax.set_title(f"Probe Plan — {len(dies)} on-wafer die(s) — "
                                 "click a die to see its serial", fontsize=9)
        self._nzmap_current_labels = [
            {"x": d["col"], "y": -d["row"],
             "label": d["serial"], "color": "white" if d["status"] == "reference" else "black"}
            for d in dies
        ]
        self._connect_nzmap_view_callbacks()
        self._update_visible_nzmap_labels()
        self._nzmap_canvas.draw_idle()

    def _draw_accretech_nzmap(self):
        rcs = sorted(self.wafer_map.dies.keys())
        if not rcs:
            self._draw_empty_nzmap(
                "No Accretech wafer map yet — extract or auto-load one on the Run tab.")
            return
        self._nzmap_accr_dies_by_rc = {rc: {"row": rc[0], "col": rc[1]} for rc in rcs}
        self._nzmap_ax.clear()
        self._nzmap_ax.set_aspect("equal")
        patches = [Rectangle((c - 0.5, -r - 0.5), 1, 1) for r, c in rcs]
        coll = PatchCollection(patches, edgecolor="#1e293b", linewidths=0.4)
        coll.set_facecolor("#7aaec8")
        self._nzmap_ax.add_collection(coll)
        cols = [c for _r, c in rcs]
        rows = [r for r, _c in rcs]
        self._nzmap_ax.set_xlim(min(cols) - 1, max(cols) + 1)
        self._nzmap_ax.set_ylim(-(max(rows) + 1), -(min(rows) - 1))
        self._nzmap_ax.set_title(f"Accretech — {len(rcs)} die(s) — click a die to see "
                                 "its row/col", fontsize=9)
        self._nzmap_current_labels = [
            {"x": c, "y": -r,
             "label": self._nzmap_overlay_die_ids.get((r, c)) or f"R{r}C{c}",
             "color": "black"}
            for r, c in rcs
        ]
        self._connect_nzmap_view_callbacks()
        self._update_visible_nzmap_labels()
        self._nzmap_canvas.draw_idle()

    def _nzmap_open_overlay_dialog(self):
        accretech_rc = set(self.wafer_map.dies.keys())
        if not accretech_rc:
            self._log_main("Overlay: no Accretech wafer map loaded yet — "
                           "load an ATA folder first.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Overlay CSV Wafer Map onto Accretech")
        dlg.transient(self.winfo_toplevel())
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)

        path_var = tk.StringVar(
            value=self._nzmap_csv_data["path"] if self._nzmap_csv_data else "No CSV loaded.")
        ttk.Label(frm, textvariable=path_var, foreground="#6b7280",
                 wraplength=340, justify="left").grid(
                 row=0, column=0, columnspan=4, sticky="w")
        ttk.Button(frm, text="📂 Load CSV…", command=lambda: load_csv()).grid(
            row=0, column=4, sticky="e", padx=(8, 0))

        summary_var = tk.StringVar()
        ttk.Label(frm, textvariable=summary_var, font=("Consolas", 9),
                 justify="left").grid(row=1, column=0, columnspan=5, sticky="w", pady=(8, 4))
        ttk.Label(frm, text="Centered by matching the two maps' centers (🎯 Center Overlay) "
                 "— a CSV die counts as \"on the map\" when its (row, col), shifted by the "
                 "offset below, lands on a die the Accretech prober actually walked. Nudge "
                 "the offset if dies land on the wrong physical die, then Overlay on Map.",
                 font=("Segoe UI", 8), foreground="#6b7280", wraplength=340,
                 justify="left").grid(row=2, column=0, columnspan=5, sticky="w", pady=(0, 10))

        ttk.Label(frm, text="Row offset:").grid(row=3, column=0, sticky="e")
        row_var = tk.IntVar(value=self._nzmap_overlay_row_offset)
        ttk.Spinbox(frm, from_=-50, to=50, width=6, textvariable=row_var).grid(
            row=3, column=1, sticky="w", padx=(4, 16))
        ttk.Label(frm, text="Col offset:").grid(row=3, column=2, sticky="e")
        col_var = tk.IntVar(value=self._nzmap_overlay_col_offset)
        ttk.Spinbox(frm, from_=-50, to=50, width=6, textvariable=col_var).grid(
            row=3, column=3, sticky="w", padx=(4, 0))

        state = {"grid": []}

        def csv_grid():
            if not self._nzmap_csv_data:
                return []
            return [{"row": s["row"], "col": s["col"], "die_ids": s["dies"]}
                   for s in self._nzmap_csv_data["shots"]]

        def recompute(*_a):
            grid = csv_grid()
            state["grid"] = grid
            if not grid:
                summary_var.set("No CSV loaded — click 📂 Load CSV… first.")
                return
            try:
                ro, co = row_var.get(), col_var.get()
            except tk.TclError:
                return
            matched = merge_with_accretech(grid, accretech_rc, ro, co)
            state["matched"] = matched
            summary_var.set(
                f"Accretech dies on map:  {len(accretech_rc)}\n"
                f"CSV dies (real ID):     {len(grid)}\n"
                f"Overlaid (on both maps): {len(matched)}"
            )

        def center_overlay():
            grid = csv_grid()
            if not grid:
                recompute()
                return
            ro, co = centroid_offset(grid, accretech_rc)
            row_var.set(ro)
            col_var.set(co)

        def load_csv():
            path = filedialog.askopenfilename(
                title="Load CSV Wafer Map",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if not path:
                return
            try:
                self._nzmap_csv_data = parse_plain_csv_wafer_map(path)
            except OSError as exc:
                messagebox.showerror("Could not load CSV wafer map", str(exc))
                return
            path_var.set(f"{path}  ({self._nzmap_csv_data['die_count']} die(s))")
            center_overlay()

        row_var.trace_add("write", recompute)
        col_var.trace_add("write", recompute)
        recompute()

        def do_overlay():
            self._nzmap_overlay_row_offset = row_var.get()
            self._nzmap_overlay_col_offset = col_var.get()
            matched = state.get("matched", [])
            self._nzmap_overlay_die_ids = {(d["row"], d["col"]): "/".join(d["die_ids"])
                                           for d in matched}
            self._nzmap_source_var.set("accretech")
            self._redraw_nanoz_wafer_map()
            self._log_main(f"NanoZ Wafer Map: overlaid {len(matched)} CSV die(s) onto Accretech.")

        def do_clear():
            self._nzmap_overlay_die_ids = {}
            self._redraw_nanoz_wafer_map()
            self._log_main("NanoZ Wafer Map: overlay cleared.")

        ttk.Button(frm, text="🎯 Center Overlay", command=center_overlay).grid(
            row=3, column=4, sticky="w", padx=(10, 0))

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=5, sticky="ew", pady=(12, 0))
        ttk.Button(btns, text="🖌 Overlay on Map", command=do_overlay).pack(side="left")
        ttk.Button(btns, text="✕ Clear Overlay", command=do_clear).pack(side="left", padx=6)
        ttk.Button(btns, text="Close", command=dlg.destroy).pack(side="right")

    _NZMAP_MAX_VISIBLE_LABELS = 900

    def _connect_nzmap_view_callbacks(self):
        self._nzmap_ax.callbacks.connect("xlim_changed", self._on_nzmap_view_changed)
        self._nzmap_ax.callbacks.connect("ylim_changed", self._on_nzmap_view_changed)

    def _on_nzmap_view_changed(self, _ax=None):
        if self._nzmap_view_debounce_id is not None:
            try:
                self.after_cancel(self._nzmap_view_debounce_id)
            except Exception:
                pass
        self._nzmap_view_debounce_id = self.after(120, self._update_visible_nzmap_labels)

    def _clear_nzmap_labels(self):
        for t in self._nzmap_label_artists:
            try:
                t.remove()
            except Exception:
                pass
        self._nzmap_label_artists = []

    def _fit_nzmap_fontsize(self, box_w_px: float, box_h_px: float, text_len: int) -> float:
        text_len = max(text_len, 1)
        dpi = self._nzmap_fig.dpi
        by_width = box_w_px * 72.0 / dpi / (0.62 * text_len)
        by_height = box_h_px * 72.0 / dpi * 0.75
        return max(3.0, min(by_width, by_height, 24.0))

    def _update_visible_nzmap_labels(self):
        self._nzmap_view_debounce_id = None
        self._clear_nzmap_labels()
        if not (_MPL and self._show_nzmap_labels_var.get()):
            self._nzmap_canvas.draw_idle()
            return
        labels = self._nzmap_current_labels
        if not labels:
            return
        xlim = sorted(self._nzmap_ax.get_xlim())
        ylim = sorted(self._nzmap_ax.get_ylim())
        visible = [d for d in labels
                  if xlim[0] <= d["x"] <= xlim[1] and ylim[0] <= d["y"] <= ylim[1]]
        if not visible or len(visible) > self._NZMAP_MAX_VISIBLE_LABELS:
            self._nzmap_canvas.draw_idle()
            return
        bbox = self._nzmap_ax.get_window_extent()
        span_x = (xlim[1] - xlim[0]) or 1.0
        span_y = (ylim[1] - ylim[0]) or 1.0
        box_w_px = bbox.width / span_x
        box_h_px = bbox.height / span_y
        for d in visible:
            fs = self._fit_nzmap_fontsize(box_w_px, box_h_px, len(d["label"]))
            t = self._nzmap_ax.text(d["x"], d["y"], d["label"], fontsize=fs,
                                    ha="center", va="center", color=d["color"],
                                    zorder=6, clip_on=True)
            self._nzmap_label_artists.append(t)
        self._nzmap_canvas.draw_idle()

    def _on_nzmap_click(self, event):
        if event.xdata is None or event.ydata is None:
            return
        rc = (round(-event.ydata), round(event.xdata))
        if self._nzmap_source_var.get() == "accretech":
            d = self._nzmap_accr_dies_by_rc.get(rc)
            if d is None:
                return
            self._nzmap_die_var.set(f"Row {d['row']}, Col {d['col']}")
            return
        d = self._nzmap_dies_by_rc.get(rc)
        if d is None:
            return
        self._nzmap_die_var.set(
            f"Row {d['row']}, Col {d['col']} — serial {d['serial']}  ({d['status']})")

    def _on_nzmap_scroll_zoom(self, event):
        if event.inaxes != self._nzmap_ax or event.xdata is None or event.ydata is None:
            return
        factor = 0.85 if event.button == "up" else (1 / 0.85)
        xlim = self._nzmap_ax.get_xlim()
        ylim = self._nzmap_ax.get_ylim()
        xd, yd = event.xdata, event.ydata
        self._nzmap_ax.set_xlim(xd - (xd - xlim[0]) * factor, xd + (xlim[1] - xd) * factor)
        self._nzmap_ax.set_ylim(yd - (yd - ylim[0]) * factor, yd + (ylim[1] - yd) * factor)
        self._nzmap_canvas.draw_idle()

    def _build_run_tab(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Run")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        split = ttk.PanedWindow(tab, orient="vertical")
        split.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        controls = ttk.Frame(split)
        split.add(controls, weight=1)
        controls.columnconfigure(0, weight=1)

        ctrl_lf = ttk.LabelFrame(controls, text="Controls")
        ctrl_lf.grid(row=0, column=0, sticky="ew")

        rrow = ttk.Frame(ctrl_lf)
        rrow.pack(fill="x", padx=6, pady=(6, 2))
        ttk.Label(rrow, text="Recipe:").pack(side="left")
        self._run_recipe_name_cb = ttk.Combobox(
            rrow, textvariable=self._recipe_name_var, state="readonly", width=26)
        self._run_recipe_name_cb.pack(side="left", padx=(4, 4))
        self._run_recipe_name_cb.bind(
            "<<ComboboxSelected>>", lambda _e: self._load_named_recipe())
        ttk.Button(rrow, text="📂 Load", command=lambda: self._load_named_recipe()).pack(
            side="left", padx=2)
        self._run_recipe_active_lbl = ttk.Label(rrow, text="(no recipe saved yet)",
                                                foreground="#6b7280")
        self._run_recipe_active_lbl.pack(side="left", padx=(12, 0))

        prow = ttk.Frame(ctrl_lf)
        prow.pack(fill="x", padx=6, pady=(6, 2))
        ttk.Label(prow, text="Cycle #:").pack(side="left")
        self.cycle_var = tk.StringVar(value="0")
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
        self.recipe_btn = ttk.Button(crow, text="▶ Run Recipe", command=self._start_recipe_run)
        self.recipe_btn.pack(side="left", padx=4)
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

        shot_lf = ttk.LabelFrame(controls, text="Recipe — Current Shot")
        shot_lf.grid(row=2, column=0, sticky="ew", pady=4)
        self.recipe_shot_var = tk.StringVar(value="No recipe run active — see the Recipe tab.")
        ttk.Label(shot_lf, textvariable=self.recipe_shot_var, wraplength=520,
                 justify="left").pack(anchor="w", padx=6, pady=(6, 2))
        sd_cols = ("port", "slots", "decision", "reason")
        self._shot_decision_tree = ttk.Treeview(shot_lf, columns=sd_cols, show="headings", height=5)
        sd_heads = [("port", "Board", 80), ("slots", "Slots (chip0/chip1)", 110),
                   ("decision", "Decision", 80), ("reason", "Reason", 260)]
        for cid, text, width in sd_heads:
            self._shot_decision_tree.heading(cid, text=text)
            self._shot_decision_tree.column(cid, width=width, anchor="center" if cid != "reason" else "w")
        self._shot_decision_tree.pack(fill="x", padx=6, pady=(0, 6))

        stat_lf = ttk.LabelFrame(controls, text="Pass / Fail")
        stat_lf.grid(row=3, column=0, sticky="ew", pady=(0, 0))
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

        map_lf = ttk.LabelFrame(split, text="Wafer Map")
        split.add(map_lf, weight=2)
        map_lf.rowconfigure(0, weight=1)
        map_lf.columnconfigure(0, weight=1)
        self.wafer_map = WaferMapPanel(map_lf)
        self.wafer_map.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.wafer_map.enable_picking(on_change=self._on_sites_changed)

    def _build_console_tab(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Board Console")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        split = ttk.PanedWindow(tab, orient="vertical")
        split.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        top = ttk.Frame(split)
        split.add(top, weight=1)
        top.columnconfigure(0, weight=1)

        pick = ttk.Frame(top)
        pick.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(pick, text="Board:").pack(side="left")
        self.console_board_var = tk.StringVar(value="")
        self._console_board_label_var = tk.StringVar(value="")
        self._console_board_cb = ttk.Combobox(
            pick, textvariable=self._console_board_label_var, state="readonly", width=26)
        self._console_board_cb.pack(side="left", padx=(4, 12))
        self._console_board_cb.bind("<<ComboboxSelected>>", self._on_console_board_picked)
        ttk.Label(pick, text="Chip:").pack(side="left")
        self.console_chip_var = tk.StringVar(value="0")
        self._console_chip_cb = ttk.Combobox(
            pick, textvariable=self.console_chip_var, state="readonly", width=3,
            values=("0", "1"))
        self._console_chip_cb.pack(side="left", padx=(4, 2))
        self._console_chip_cb.bind("<<ComboboxSelected>>",
                                   lambda _e: self._refresh_console_reading())
        ttk.Label(pick, text="(0=right, 1=left, per board's NANOZ-logo-up orientation)",
                 foreground="#6b7280").pack(side="left", padx=(0, 12))

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
        self.console_cycle_var = tk.StringVar(value="0")
        ttk.Entry(crow2, textvariable=self.console_cycle_var, width=5).pack(side="left", padx=(4, 8))
        ttk.Button(crow2, text="▶ run", command=self._console_run).pack(side="left", padx=2)
        ttk.Button(crow2, text="⏸ pause",
                  command=lambda: self._console_send("pause")).pack(side="left", padx=2)
        ttk.Separator(crow2, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(crow2, text="Raw command:").pack(side="left")
        self.console_raw_var = tk.StringVar(value="")
        ttk.Entry(crow2, textvariable=self.console_raw_var, width=16).pack(side="left", padx=(4, 4))
        ttk.Button(crow2, text="Send", command=self._console_send_raw).pack(side="left", padx=2)

        crow3 = ttk.Frame(cmds)
        crow3.pack(fill="x", padx=6, pady=(0, 6))
        ttk.Label(crow3, text="Read EEPROM — addr:").pack(side="left")
        self.console_eep_addr_var = tk.StringVar(value="0")
        ttk.Entry(crow3, textvariable=self.console_eep_addr_var, width=8).pack(
            side="left", padx=(4, 8))
        ttk.Label(crow3, text="len:").pack(side="left")
        self.console_eep_len_var = tk.StringVar(value="64")
        ttk.Entry(crow3, textvariable=self.console_eep_len_var, width=6).pack(
            side="left", padx=(4, 8))
        ttk.Button(crow3, text="Read", command=self._console_read_eeprom).pack(side="left", padx=2)
        ttk.Label(crow3, text="Read-only — rdeep does not run or change anything on the "
                             "board. No known map of what cycle/sequence data lives at "
                             "which address yet.",
                 foreground="#6b7280", font=("Segoe UI", 8), wraplength=420,
                 justify="left").pack(side="left", padx=(10, 0))

        reading_lf = ttk.LabelFrame(split, text="Latest Reading")
        split.add(reading_lf, weight=2)
        reading_lf.rowconfigure(0, weight=1)
        reading_lf.columnconfigure(0, weight=1)

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

        eep_frame = ttk.Frame(reading_split)
        reading_split.add(eep_frame, weight=1)
        eep_frame.rowconfigure(1, weight=1)
        eep_frame.columnconfigure(0, weight=1)
        ttk.Label(eep_frame, text="EEPROM (hex)", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky="w")
        self.console_eep_text = tk.Text(eep_frame, wrap="word", state="disabled",
                                        height=14, font=("Consolas", 9))
        self.console_eep_text.grid(row=1, column=0, sticky="nsew")
        eep_sb = ttk.Scrollbar(eep_frame, orient="vertical", command=self.console_eep_text.yview)
        eep_sb.grid(row=1, column=1, sticky="ns")
        self.console_eep_text.configure(yscrollcommand=eep_sb.set)

    def _build_charts_tab(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Charts")
        self._charts_tab = tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)

        pick = ttk.Frame(tab)
        pick.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        ttk.Label(pick, text="Board:").pack(side="left")
        self._chart_board_cb = ttk.Combobox(
            pick, textvariable=self._console_board_label_var, state="readonly", width=26)
        self._chart_board_cb.pack(side="left", padx=(4, 12))
        self._chart_board_cb.bind(
            "<<ComboboxSelected>>",
            lambda _e: (self._on_console_board_picked(_e), self._redraw_charts()))
        ttk.Label(pick, text="Sensors:").pack(side="left", padx=(12, 0))
        self._chart_sensor_metric_var = tk.StringVar(value="Current")
        ttk.Combobox(pick, textvariable=self._chart_sensor_metric_var, state="readonly", width=10,
                    values=("Current", "Resistance")).pack(side="left", padx=(4, 12))
        self._chart_sensor_metric_var.trace_add(
            "write", lambda *_: self._redraw_charts(preserve_view=True))
        ttk.Label(pick, text="Heaters:").pack(side="left")
        self._chart_heater_metric_var = tk.StringVar(value="Voltage")
        ttk.Combobox(pick, textvariable=self._chart_heater_metric_var, state="readonly", width=10,
                    values=("Voltage", "Current", "Power", "Resistance")).pack(side="left", padx=(4, 12))
        self._chart_heater_metric_var.trace_add(
            "write", lambda *_: self._redraw_charts(preserve_view=True))
        self._chart_live_btn = ttk.Button(pick, text="▶ Jump to Live",
                                          command=self._chart_resume_live)
        self._chart_live_btn.pack(side="left", padx=(12, 0))

        channels_row = ttk.Frame(tab)
        channels_row.grid(row=1, column=0, sticky="w", padx=8, pady=(0, 4))
        ttk.Label(channels_row, text="Show chips:").pack(side="left")
        self._chart_chip_visible_vars = {}
        for chip, text in (("0", "Chip 0 (solid)"), ("1", "Chip 1 (dashed)")):
            var = tk.BooleanVar(value=True)
            self._chart_chip_visible_vars[chip] = var
            ttk.Checkbutton(channels_row, text=text, variable=var,
                            command=lambda: self._redraw_charts(preserve_view=True)).pack(
                            side="left", padx=(6, 0))
        ttk.Label(channels_row, text="   Show channels:").pack(side="left")
        self._chart_visible_vars = {}
        for key in ("s1", "s2", "s3", "s4", "h1", "h2"):
            var = tk.BooleanVar(value=True)
            self._chart_visible_vars[key] = var
            ttk.Checkbutton(channels_row, text=key.upper(), variable=var,
                            command=lambda: self._redraw_charts(preserve_view=True)).pack(
                            side="left", padx=(6, 0))

        if _MPL:
            self._chart_fig = Figure(figsize=(8, 7), dpi=100)
            self._chart_ax_v = self._chart_fig.add_subplot(311)
            self._chart_ax_i = self._chart_fig.add_subplot(312, sharex=self._chart_ax_v)
            self._chart_ax_t = self._chart_fig.add_subplot(313, sharex=self._chart_ax_v)
            self._chart_fig.tight_layout(pad=2.2)
            self._chart_canvas = FigureCanvasTkAgg(self._chart_fig, master=tab)
            self._chart_canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 0))
            toolbar = NavigationToolbar2Tk(self._chart_canvas, tab, pack_toolbar=False)
            toolbar.update()
            toolbar.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
            # Default view auto-scrolls to the last _CHART_WINDOW_S seconds.
            # Panning/zooming via the toolbar above (or scroll-back) drops
            # into "browsing history" mode and stops auto-scrolling until
            # ▶ Jump to Live is pressed - otherwise the 300ms redraw loop
            # would fight any manual pan attempt.
            self._chart_follow_live = True
            self._chart_programmatic_xlim = False
            self._chart_ax_v.callbacks.connect("xlim_changed", self._on_chart_xlim_changed)
            # xlim_changed alone isn't reliable for pausing mid-drag - some
            # backends only fire it once, on button release, so the 300ms
            # loop could still redraw (and snap the view back to live)
            # partway through a pan gesture. Pausing on the raw mouse-down
            # inside the chart canvas instead guarantees nothing resets the
            # view once the user has started interacting with it.
            self._chart_canvas.mpl_connect("button_press_event", self._on_chart_button_press)
            self._draw_empty_charts()
        else:
            ttk.Label(tab, text="matplotlib not installed — install it to view live charts.",
                     foreground="red").grid(row=2, column=0, sticky="nw", padx=10, pady=10)

    def _draw_empty_charts(self):
        for ax, title in ((self._chart_ax_v, "Heater Voltage (mV) — SPL"),
                          (self._chart_ax_i, "Sensor Current (mA) — SPL"),
                          (self._chart_ax_t, "Temperature (°C) — ENV")):
            ax.clear()
            ax.set_title(title, fontsize=9)
            ax.text(0.5, 0.5, "no data yet", ha="center", va="center",
                    transform=ax.transAxes, color="#999999")
        self._chart_canvas.draw_idle()

    def _build_results_tab(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Results")
        self._results_tab = tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)

        top = ttk.Frame(tab)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        ttk.Label(top, text="Latest current/voltage per board, chip, sensor (S1-S4) and heater "
                            "(H1-H2). Avg is over readings since the last Reset Counts / run "
                            "start. Every raw reading (not just this average) is logged to the "
                            "SPL CSV, tagged with the die it was taken on.",
                 foreground="#6b7280", wraplength=700, justify="left").pack(side="left")

        export_frame = ttk.LabelFrame(tab, text="Data Export")
        export_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        ttk.Label(
            export_frame,
            text="Output filename:  <Lot ID>_<Wafer ID>_nanoz_results.csv  "
                 "(Wafer ID omitted if blank)"
        ).pack(anchor="w", padx=10, pady=(8, 4))

        file_row = ttk.Frame(export_frame)
        file_row.pack(fill="x", padx=10, pady=4)
        ttk.Label(file_row, text="Lot ID:").pack(side="left")
        self._nz_lot_id_var = tk.StringVar(value="")
        ttk.Entry(file_row, textvariable=self._nz_lot_id_var, width=22).pack(side="left", padx=6)
        ttk.Label(file_row, text="Wafer ID:").pack(side="left", padx=(12, 0))
        self._nz_wafer_id_var = tk.StringVar(value="")
        ttk.Entry(file_row, textvariable=self._nz_wafer_id_var, width=22).pack(side="left", padx=6)

        path_row = ttk.Frame(export_frame)
        path_row.pack(fill="x", padx=10, pady=(4, 12))
        ttk.Label(path_row, text="Export Path:").pack(side="left")
        self._nz_export_path_var = tk.StringVar(value="")
        ttk.Entry(path_row, textvariable=self._nz_export_path_var, width=40).pack(side="left", padx=6)
        ttk.Button(path_row, text="Browse...", command=self._nz_browse_export_path).pack(
            side="left", padx=4)
        ttk.Button(path_row, text="Save to CSV", command=self._nz_save_results_csv).pack(
            side="left", padx=10)

        cols = ("port", "chip", "die", "channel", "v_now", "i_now", "v_avg", "i_avg", "n", "updated")
        self._results_tree = ttk.Treeview(tab, columns=cols, show="headings", height=16)
        heads = [("port", "Port", 70), ("chip", "Chip", 50), ("die", "Die (row,col)", 90),
                 ("channel", "Channel", 60),
                 ("v_now", "V now (mV)", 100), ("i_now", "I now (mA)", 100),
                 ("v_avg", "V avg (mV)", 100), ("i_avg", "I avg (mA)", 100),
                 ("n", "N", 50), ("updated", "Updated", 140)]
        for cid, text, width in heads:
            self._results_tree.heading(cid, text=text)
            self._results_tree.column(cid, width=width, anchor="center")
        self._results_tree.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def _nz_browse_export_path(self):
        path = filedialog.askdirectory(title="Choose Export Folder")
        if path:
            self._nz_export_path_var.set(path)

    def _nz_save_results_csv(self):
        folder = self._nz_export_path_var.get().strip() or self._nanoz_ata_folder
        if not folder:
            messagebox.showerror("No Export Path", "Choose an export path first.")
            return
        lot_id = self._nz_lot_id_var.get().strip()
        wafer_id = self._nz_wafer_id_var.get().strip()
        name_parts = [p for p in (lot_id, wafer_id) if p] or ["nanoz"]
        filename = "_".join(name_parts) + "_nanoz_results.csv"
        path = os.path.join(folder, filename)
        cols = ("port", "chip", "die", "channel", "v_now", "i_now", "v_avg", "i_avg", "n", "updated")
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for iid in self._results_tree.get_children():
                    writer.writerow(self._results_tree.item(iid, "values"))
        except OSError as e:
            messagebox.showerror("Save Failed", str(e))
            return
        self._log_main(f"NanoZ Results: saved {len(self._results_tree.get_children())} "
                       f"row(s) to {path}")

    def _results_tab_visible(self):
        try:
            return self._sub_nb.select() == str(self._results_tab)
        except Exception:
            return False

    def _refresh_results_loop(self):
        if self._results_tab_visible():
            self._redraw_results()
        self.after(500, self._refresh_results_loop)

    def _redraw_results(self):
        for iid in self._results_tree.get_children():
            self._results_tree.delete(iid)

        cutoff = self._cycle_start_time
        for port, chip in sorted(self._latest_spl.keys()):
            key = (port, chip)
            latest = self._latest_spl[key]
            hist = list(self._spl_history.get(key, ()))
            windowed = [h for h in hist if cutoff and (self._pkt_time(h) or cutoff) >= cutoff]
            if not windowed:
                windowed = hist
            updated = latest.get("host_timestamp", "")
            updated = updated.split("T")[-1] if "T" in updated else updated
            die_row, die_col = latest.get("die_row"), latest.get("die_col")
            die = f"{die_row},{die_col}" if die_row is not None and die_col is not None else "—"
            channels = ([(f"s{s}", f"dac_mv_s{s}", f"adc_current_ma_s{s}") for s in (1, 2, 3, 4)]
                       + [(f"h{h}", f"heater{h}_voltage_mv", f"heater{h}_current_ma")
                          for h in (1, 2)])
            for label, v_field, i_field in channels:
                v_now, i_now = latest.get(v_field), latest.get(i_field)
                v_vals = [h[v_field] for h in windowed if v_field in h]
                i_vals = [h[i_field] for h in windowed if i_field in h]
                v_avg = sum(v_vals) / len(v_vals) if v_vals else None
                i_avg = sum(i_vals) / len(i_vals) if i_vals else None
                self._results_tree.insert("", "end", values=(
                    port, chip, die, label,
                    f"{v_now:.2f}" if v_now is not None else "—",
                    f"{i_now:.5f}" if i_now is not None else "—",
                    f"{v_avg:.2f}" if v_avg is not None else "—",
                    f"{i_avg:.5f}" if i_avg is not None else "—",
                    len(windowed), updated,
                ))

    def _build_nanoz_ek_tab(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="NanoZ_EK")
        tab.columnconfigure(0, weight=1)

        ttk.Label(tab,
                  text="Replica of Nanoz_EK.exe's Configuration window (see references/250723_User "
                       "manual EK IV.pdf section IV.B-D), decoded from the board's EEPROM. Duration "
                       "is confirmed field-accurate against real hardware; other D.a/D.b fields are "
                       "high-confidence matches against a real sequence but not yet individually "
                       "isolated. \"Write Sequence to Device\" sends REAL writes for the D.a Sequence "
                       "settings + D.b Heater settings fields only (edit them, then click Write) - "
                       "Chip, Resolution, and everything in Cycle/Configuration are preserved exactly "
                       "as last read, never guessed at. Always read a sequence before editing/writing it.",
                  foreground="#6b7280", wraplength=1000, justify="left").grid(
                  row=0, column=0, sticky="w", padx=8, pady=(8, 4))

        pick = ttk.Frame(tab)
        pick.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        ttk.Label(pick, text="Board:").pack(side="left")
        self._ek_board_var = tk.StringVar(value="")
        self._ek_board_label_var = tk.StringVar(value="")
        self._ek_board_cb = ttk.Combobox(
            pick, textvariable=self._ek_board_label_var, state="readonly", width=26)
        self._ek_board_cb.pack(side="left", padx=(4, 12))
        self._ek_board_cb.bind("<<ComboboxSelected>>", self._on_ek_board_picked)
        self._btn_ek_read = ttk.Button(pick, text="🔄 Read Configuration",
                                       command=self._ek_read_configuration)
        self._btn_ek_read.pack(side="left")
        self._btn_ek_write = ttk.Button(pick, text="💾 Write Sequence to Device",
                                        command=self._ek_write_sequence, state="disabled")
        self._btn_ek_write.pack(side="left", padx=(6, 0))
        ttk.Label(pick, text="(writes D.a/D.b only — Chip/Resolution/Cycle/Configuration untouched; "
                             "read a sequence first)",
                  foreground="#9ca3af").pack(side="left", padx=(4, 0))
        self._ek_status_var = tk.StringVar(value="")
        ttk.Label(pick, textvariable=self._ek_status_var, foreground="#6b7280").pack(
                  side="left", padx=(10, 0))

        body = ttk.Frame(tab)
        body.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        tab.rowconfigure(2, weight=1)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        # --- B. Configuration -------------------------------------------------
        cfg_lf = ttk.LabelFrame(body, text="B — Configuration")
        cfg_lf.grid(row=0, column=0, sticky="new", padx=(0, 6), pady=(0, 6))
        self._ek_cycles_count_var = tk.StringVar(value="")
        self._ek_sequences_count_var = tk.StringVar(value="")
        self._ek_periodicity_var = tk.StringVar(value="")
        self._ek_signature_var = tk.StringVar(value="—")
        self._ek_chip1_var = tk.StringVar(value="—")
        self._ek_chip2_var = tk.StringVar(value="—")
        r = 0
        for label, var, editable in (
            ("Cycles:", self._ek_cycles_count_var, True),
            ("Sequences:", self._ek_sequences_count_var, True),
            ("Periodicity (ms):", self._ek_periodicity_var, True),
        ):
            ttk.Label(cfg_lf, text=label).grid(row=r, column=0, sticky="e", padx=4, pady=2)
            ttk.Entry(cfg_lf, textvariable=var, width=10).grid(row=r, column=1, sticky="w", padx=(0, 4))
            r += 1
        ttk.Label(cfg_lf, text="Signature:").grid(row=r, column=0, sticky="e", padx=4, pady=2)
        ttk.Label(cfg_lf, textvariable=self._ek_signature_var).grid(row=r, column=1, sticky="w")
        r += 1
        ttk.Label(cfg_lf, text="Chip 1 (ID / Age):").grid(row=r, column=0, sticky="e", padx=4, pady=2)
        ttk.Label(cfg_lf, textvariable=self._ek_chip1_var).grid(row=r, column=1, columnspan=3, sticky="w")
        r += 1
        ttk.Label(cfg_lf, text="Chip 2 (ID / Age):").grid(row=r, column=0, sticky="e", padx=4, pady=2)
        ttk.Label(cfg_lf, textvariable=self._ek_chip2_var).grid(row=r, column=1, columnspan=3, sticky="w")

        # --- C. Cycle -----------------------------------------------------
        cyc_lf = ttk.LabelFrame(body, text="C — Cycle")
        cyc_lf.grid(row=0, column=1, sticky="new", padx=(6, 0), pady=(0, 6))
        self._ek_cycle_index_var = tk.StringVar(value="1")
        self._ek_cycle_numseq_var = tk.StringVar(value="")
        self._ek_cycle_seqorder_var = tk.StringVar(value="")
        self._ek_cycle_loopback_var = tk.BooleanVar(value=False)
        ttk.Label(cyc_lf, text="Index:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self._ek_cycle_index_spin = ttk.Spinbox(
            cyc_lf, from_=1, to=nzb.MAX_CYCLES_NB, width=6, textvariable=self._ek_cycle_index_var,
            command=self._ek_on_cycle_index_changed)
        self._ek_cycle_index_spin.grid(row=0, column=1, sticky="w")
        self._ek_cycle_index_spin.bind("<Return>", self._ek_on_cycle_index_changed)
        self._ek_cycle_index_spin.bind("<FocusOut>", self._ek_on_cycle_index_changed)
        ttk.Label(cyc_lf, text="(cycle numbering starts at 1, per the manual)",
                 foreground="#9ca3af").grid(row=0, column=2, sticky="w", padx=(6, 0))
        ttk.Label(cyc_lf, text="Number of sequences:").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        ttk.Entry(cyc_lf, textvariable=self._ek_cycle_numseq_var, width=10).grid(row=1, column=1, sticky="w")
        ttk.Label(cyc_lf, text="Sequence order (comma-sep, UI index):").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        ttk.Entry(cyc_lf, textvariable=self._ek_cycle_seqorder_var, width=24).grid(
            row=2, column=1, columnspan=2, sticky="w")
        ttk.Checkbutton(cyc_lf, text="Loop back (not yet located in EEPROM — disabled)",
                        variable=self._ek_cycle_loopback_var, state="disabled").grid(
                        row=3, column=0, columnspan=3, sticky="w", padx=4, pady=(4, 2))

        # --- D.a Sequence settings -----------------------------------------
        seq_lf = ttk.LabelFrame(body, text="D.a — Sequence settings")
        seq_lf.grid(row=1, column=0, sticky="new", padx=(0, 6), pady=(0, 6))
        self._ek_seq_index_var = tk.StringVar(value="1")
        self._ek_seq_duration_var = tk.StringVar(value="")
        self._ek_seq_delay_var = tk.StringVar(value="")
        self._ek_seq_chip_var = tk.StringVar(value="1")
        self._ek_seq_sensor_var = tk.StringVar(value="")
        ttk.Label(seq_lf, text="Index:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self._ek_seq_index_spin = ttk.Spinbox(
            seq_lf, from_=1, to=nzb.MAX_SEQUENCE_NB, width=6, textvariable=self._ek_seq_index_var,
            command=self._ek_on_seq_index_changed)
        self._ek_seq_index_spin.grid(row=0, column=1, sticky="w")
        self._ek_seq_index_spin.bind("<Return>", self._ek_on_seq_index_changed)
        self._ek_seq_index_spin.bind("<FocusOut>", self._ek_on_seq_index_changed)
        ttk.Label(seq_lf, text="Duration (s):").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        ttk.Entry(seq_lf, textvariable=self._ek_seq_duration_var, width=10).grid(row=1, column=1, sticky="w")
        ttk.Label(seq_lf, text="(CONFIRMED offset)", foreground="#16a34a").grid(row=1, column=2, sticky="w", padx=(6, 0))
        ttk.Label(seq_lf, text="Delay (s):").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        ttk.Entry(seq_lf, textvariable=self._ek_seq_delay_var, width=10).grid(row=2, column=1, sticky="w")
        ttk.Label(seq_lf, text="Chip:").grid(row=3, column=0, sticky="e", padx=4, pady=2)
        ttk.Combobox(seq_lf, textvariable=self._ek_seq_chip_var, values=("1", "2"),
                    state="readonly", width=4).grid(row=3, column=1, sticky="w")
        ttk.Label(seq_lf, text="(offset ambiguous — see tab description)",
                 foreground="#9ca3af").grid(row=3, column=2, sticky="w", padx=(6, 0))
        ttk.Label(seq_lf, text="Sensors-NZG2 (mV, all sensors):").grid(row=4, column=0, sticky="e", padx=4, pady=2)
        ttk.Entry(seq_lf, textvariable=self._ek_seq_sensor_var, width=10).grid(row=4, column=1, sticky="w")

        # --- D.b Heater settings (Table 2) ----------------------------------
        heat_lf = ttk.LabelFrame(body, text="D.b — Heater settings  (Table 2: Heater control parameters)")
        heat_lf.grid(row=1, column=1, sticky="new", padx=(6, 0), pady=(0, 6))
        for c, text in enumerate(("Parameter", "Value", "Unit", "Min", "Max")):
            ttk.Label(heat_lf, text=text, font=("TkDefaultFont", 8, "bold")).grid(
                row=0, column=c, sticky="w", padx=4)
        self._ek_heater_vars = {}
        heater_rows = (
            ("heater1_low_mv", "1. Heater 1 — low state", "mV", "0", "2200"),
            ("heater1_high_mv", "1. Heater 1 — high state", "mV", "0", "2200"),
            ("heater2_low_mv", "2. Heater 2 — low state", "mV", "0", "2200"),
            ("heater2_high_mv", "2. Heater 2 — high state", "mV", "0", "2200"),
            ("ramp_up_ms", "3. Ramp up time", "ms", "0", "60000"),
            ("high_duration_ms", "4. High state duration", "ms", "0", "60000"),
            ("ramp_down_ms", "5. Ramp down time", "ms", "0", "60000"),
            ("low_duration_ms", "6. Low state duration", "ms", "0", "60000"),
            ("phase_shift_ms", "7. Phase shift Heater 1/2", "ms", "0", "60000"),
            ("resolution_ms", "8. Time resolution", "ms", "0", "10000"),
        )
        for i, (key, label, unit, lo, hi) in enumerate(heater_rows, start=1):
            var = tk.StringVar(value="")
            self._ek_heater_vars[key] = var
            ttk.Label(heat_lf, text=label).grid(row=i, column=0, sticky="w", padx=4, pady=1)
            ttk.Entry(heat_lf, textvariable=var, width=8).grid(row=i, column=1, padx=4)
            ttk.Label(heat_lf, text=unit).grid(row=i, column=2, sticky="w")
            ttk.Label(heat_lf, text=lo, foreground="#9ca3af").grid(row=i, column=3)
            ttk.Label(heat_lf, text=hi, foreground="#9ca3af").grid(row=i, column=4)
        ttk.Label(heat_lf, text="Rows 6/7 pairing and the Chip/Resolution offset ambiguity are "
                       "best-effort — see the tab description and project notes.",
                 foreground="#9ca3af", wraplength=380, justify="left").grid(
                 row=len(heater_rows) + 1, column=0, columnspan=5, sticky="w", padx=4, pady=(4, 2))

        raw_lf = ttk.LabelFrame(body, text="Raw sequence record (debug)")
        raw_lf.grid(row=2, column=0, columnspan=2, sticky="new")
        self._ek_seq_raw_var = tk.StringVar(value="(no data read yet)")
        ttk.Label(raw_lf, textvariable=self._ek_seq_raw_var, font=("Consolas", 8),
                 foreground="#6b7280").pack(anchor="w", padx=8, pady=4)

        self._ek_cycles_by_index = {}
        self._ek_sequences_by_index = {}
        self._ek_write_board = None

    def _ek_refresh_board_list(self):
        ports = sorted(self._boards.keys())
        labels = [self._board_label(p) for p in ports]
        self._ek_board_label_to_port = dict(zip(labels, ports))
        self._ek_board_cb.config(values=labels)
        if self._ek_board_var.get() not in ports and ports:
            self._ek_board_var.set(ports[0])
        current = self._ek_board_var.get()
        if current in self._boards:
            self._ek_board_label_var.set(self._board_label(current))

    def _on_ek_board_picked(self, _event=None):
        port = getattr(self, "_ek_board_label_to_port", {}).get(self._ek_board_label_var.get())
        if port:
            self._ek_board_var.set(port)

    def _ek_read_configuration(self):
        self._ek_refresh_board_list()
        port = self._ek_board_var.get()
        board = self._boards.get(port)
        if not board or board.state != "connected":
            messagebox.showerror("No Board Connected",
                                 "Pick a connected board first (Setup tab -> Connect All).")
            return
        self._ek_write_board = board
        self._btn_ek_read.config(state="disabled")
        self._btn_ek_write.config(state="disabled")
        self._ek_status_var.set("Reading...")
        threading.Thread(target=self._ek_read_thread, args=(board,), daemon=True).start()

    def _ek_request_eeprom_sync(self, board: "nzb.NanoZBoard", addr: int, length: int,
                                timeout_s: float = 3.0) -> "bytes | None":
        """Send one rdeep and block (in this worker thread) until the async
        reader thread delivers the matching #eep! response into
        self._latest_eep, polling since the response arrives via the same
        queue/_handle_packet path as every other packet - no separate,
        conflicting serial connection is opened. Clears any stale prior
        response for this port first, so a leftover response from an
        earlier addr/len that happens to match can't be mistaken for the
        new one."""
        self._latest_eep.pop(board.port, None)
        board.request_eeprom(addr, length)
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            item = self._latest_eep.get(board.port)
            if item and item.get("addr") == addr and item.get("len") == length:
                return bytes.fromhex(item.get("data_hex", ""))
            time.sleep(0.05)
        return None

    def _ek_read_thread(self, board: "nzb.NanoZBoard"):
        try:
            params_bytes = bytearray()
            for addr in (0, 64, 128):
                chunk = self._ek_request_eeprom_sync(board, addr, 64)
                if chunk is None:
                    self.after(0, lambda a=addr: self._ek_read_failed(f"PARAMS @ {a}"))
                    return
                params_bytes += chunk
                time.sleep(0.05)
            params = nzb.parse_params_block(bytes(params_bytes))

            cycles_nb = max(1, min(params["cycles_configured"], nzb.MAX_CYCLES_NB))
            cycles = []
            for i in range(cycles_nb):
                addr = nzb.EEPROM_CYCLES_ADDR + i * nzb.EEPROM_CYCLE_RECORD_SIZE
                chunk = self._ek_request_eeprom_sync(board, addr, nzb.EEPROM_CYCLE_RECORD_SIZE)
                if chunk is None:
                    self.after(0, lambda a=addr: self._ek_read_failed(f"CYCLES @ {a}"))
                    return
                rec = nzb.parse_cycle_record(chunk)
                if rec:
                    cycles.append(rec)
                time.sleep(0.05)

            seq_bytes = bytearray()
            for i in range(4):
                addr = nzb.EEPROM_SEQUENCES_ADDR + i * 64
                chunk = self._ek_request_eeprom_sync(board, addr, 64)
                if chunk is None:
                    self.after(0, lambda a=addr: self._ek_read_failed(f"SEQUENCES @ {a}"))
                    return
                seq_bytes += chunk
                time.sleep(0.05)
            sequences = nzb.parse_sequence_records(bytes(seq_bytes))

            self.after(0, lambda: self._ek_display_results(params, cycles, sequences))
        except Exception as e:
            self.after(0, lambda e=e: self._ek_read_failed(str(e)))

    def _ek_read_failed(self, where: str):
        self._btn_ek_read.config(state="normal")
        self._ek_status_var.set(f"Read failed/timed out at {where}.")
        self._log_main(f"NanoZ_EK: EEPROM read failed at {where}.")

    def _ek_display_results(self, params: dict, cycles: list, sequences: list):
        self._btn_ek_read.config(state="normal")
        self._ek_status_var.set(f"Read OK — {len(cycles)} cycle(s), {len(sequences)} sequence(s).")

        def age_str(seconds):
            h, rem = divmod(int(seconds), 3600)
            m, s = divmod(rem, 60)
            return f"{h:02d}:{m:02d}:{s:02d}"

        c1, c2 = params["chip1"], params["chip2"]
        self._ek_cycles_count_var.set(str(params["cycles_configured"]))
        self._ek_sequences_count_var.set(str(len(sequences)))
        self._ek_periodicity_var.set(str(params["periodicity_ms"]))
        self._ek_signature_var.set(params["signature"])
        self._ek_chip1_var.set(f"{c1['id']}  /  {age_str(c1['age_s'])}")
        self._ek_chip2_var.set(f"{c2['id']}  /  {age_str(c2['age_s'])}")

        self._ek_cycles_by_index = {c["wire_index"] + 1: c for c in cycles}
        self._ek_sequences_by_index = {s["wire_index"] + 1: s for s in sequences}

        cyc_max = max(self._ek_cycles_by_index.keys(), default=1)
        self._ek_cycle_index_spin.config(to=max(cyc_max, 1))
        first_cycle = min(self._ek_cycles_by_index.keys(), default=1)
        self._ek_cycle_index_var.set(str(first_cycle))
        self._ek_load_cycle(first_cycle)

        seq_max = max(self._ek_sequences_by_index.keys(), default=1)
        self._ek_seq_index_spin.config(to=max(seq_max, 1))
        first_seq = min(self._ek_sequences_by_index.keys(), default=1)
        self._ek_seq_index_var.set(str(first_seq))
        self._ek_load_sequence(first_seq)

    def _ek_on_cycle_index_changed(self, _event=None):
        try:
            idx = int(self._ek_cycle_index_var.get())
        except ValueError:
            return
        self._ek_load_cycle(idx)

    def _ek_load_cycle(self, idx: int):
        c = self._ek_cycles_by_index.get(idx)
        if not c:
            self._ek_cycle_numseq_var.set("—")
            self._ek_cycle_seqorder_var.set("—")
            return
        self._ek_cycle_numseq_var.set(str(c["num_sequences"]))
        self._ek_cycle_seqorder_var.set(
            ", ".join(str(r + 1) for r in c["sequence_refs"]) or "—")

    def _ek_on_seq_index_changed(self, _event=None):
        try:
            idx = int(self._ek_seq_index_var.get())
        except ValueError:
            return
        self._ek_load_sequence(idx)

    def _ek_load_sequence(self, idx: int):
        s = self._ek_sequences_by_index.get(idx)
        if not s:
            self._ek_seq_duration_var.set("—")
            self._ek_seq_delay_var.set("—")
            self._ek_seq_sensor_var.set("—")
            for var in self._ek_heater_vars.values():
                var.set("—")
            self._ek_seq_raw_var.set("(no sequence at this index)")
            self._btn_ek_write.config(state="disabled")
            return

        def fmt(v):
            return "—" if v is None else str(v)

        self._ek_seq_duration_var.set(fmt(s.get("duration_s")))
        self._ek_seq_delay_var.set(fmt(s.get("delay_s")))
        self._ek_seq_chip_var.set(fmt(s.get("chip")))
        self._ek_seq_sensor_var.set(fmt(s.get("sensor_mv")))
        for key, var in self._ek_heater_vars.items():
            var.set(fmt(s.get(key)))
        cc = s.get("chip_candidates")
        rc = s.get("resolution_candidates")
        self._ek_seq_raw_var.set(
            f"chip candidates: {cc}   resolution candidates: {rc}\n{s.get('raw_hex', '')}")
        self._btn_ek_write.config(
            state="normal" if self._ek_write_board is not None else "disabled")

    # (field_key, StringVar, label, min, max) for validation + the
    # confirmation dialog. Matches manual Table 2 / section D.a ranges.
    def _ek_d_field_specs(self):
        return [
            ("duration_s", self._ek_seq_duration_var, "Duration (s)", 0, 60000),
            ("delay_s", self._ek_seq_delay_var, "Delay (s)", 0, 60000),
            ("sensor_mv", self._ek_seq_sensor_var, "Sensors-NZG2 (mV)", -800, 800),
            ("ramp_up_ms", self._ek_heater_vars["ramp_up_ms"], "Ramp up time (ms)", 0, 60000),
            ("high_duration_ms", self._ek_heater_vars["high_duration_ms"], "High state duration (ms)", 0, 60000),
            ("ramp_down_ms", self._ek_heater_vars["ramp_down_ms"], "Ramp down time (ms)", 0, 60000),
            ("low_duration_ms", self._ek_heater_vars["low_duration_ms"], "Low state duration (ms)", 0, 60000),
            ("phase_shift_ms", self._ek_heater_vars["phase_shift_ms"], "Phase shift H1/H2 (ms)", 0, 60000),
            ("heater1_low_mv", self._ek_heater_vars["heater1_low_mv"], "Heater 1 low state (mV)", 0, 2200),
            ("heater2_low_mv", self._ek_heater_vars["heater2_low_mv"], "Heater 2 low state (mV)", 0, 2200),
            ("heater1_high_mv", self._ek_heater_vars["heater1_high_mv"], "Heater 1 high state (mV)", 0, 2200),
            ("heater2_high_mv", self._ek_heater_vars["heater2_high_mv"], "Heater 2 high state (mV)", 0, 2200),
        ]

    def _ek_write_sequence(self):
        try:
            idx = int(self._ek_seq_index_var.get())
        except ValueError:
            messagebox.showerror("Invalid Index", "Sequence index must be a number.")
            return
        s = self._ek_sequences_by_index.get(idx)
        board = self._ek_write_board
        if not s or board is None or board.state != "connected":
            messagebox.showerror("Not Ready", "Read this sequence from a connected board first.")
            return

        fields, errors, changes = {}, [], []
        for key, var, label, lo, hi in self._ek_d_field_specs():
            raw = var.get().strip()
            try:
                val = int(raw)
            except ValueError:
                errors.append(f"{label}: '{raw}' is not a whole number")
                continue
            if not (lo <= val <= hi):
                errors.append(f"{label}: {val} is outside the documented range [{lo}, {hi}]")
                continue
            fields[key] = val
            old = s.get(key)
            if old != val:
                changes.append(f"  {label}: {old} -> {val}")

        if errors:
            messagebox.showerror("Out of Range", "Fix these before writing:\n\n" + "\n".join(errors))
            return
        if not changes:
            messagebox.showinfo("Nothing Changed", "No D.a/D.b field differs from the last read - nothing to write.")
            return

        cc = s.get("chip_candidates")
        rc = s.get("resolution_candidates")
        proceed = messagebox.askyesno(
            "Confirm Write to Real Hardware",
            "This sends a real wreep write to the board's EEPROM. This is NOT simulated.\n\n"
            f"Sequence (UI index {idx}) changes:\n" + "\n".join(changes) + "\n\n"
            "Untouched (preserved exactly as last read): wire_index, sensor/heater padding "
            f"bytes, Chip (candidates {cc}, offset ambiguous), Resolution (candidates {rc}, "
            "offset ambiguous), and everything in the Cycle/Configuration sections.\n\n"
            "If the checksum this app computes doesn't match what the board expects, the "
            "board rejects the write outright (per the protocol doc) rather than corrupting "
            "anything - but there is no undo if the write DOES succeed with a wrong value.\n\n"
            "Proceed?",
            icon="warning")
        if not proceed:
            return

        self._btn_ek_write.config(state="disabled")
        self._ek_status_var.set("Writing...")
        threading.Thread(target=self._ek_write_thread, args=(board, s, fields, idx), daemon=True).start()

    def _ek_write_thread(self, board: "nzb.NanoZBoard", s: dict, fields: dict, idx: int):
        try:
            original = bytes.fromhex(s["raw_hex"])
            patched = nzb.encode_sequence_patch(original, fields)
            addr = nzb.EEPROM_SEQUENCES_ADDR + s["blob_offset"]
            board.write_eeprom(addr, bytes(patched))
            # No ack on success per the protocol doc - only an error line on
            # failure, which lands on the Console tab's log via the normal
            # text-packet path. Give it a moment, then read back to verify.
            time.sleep(1.0)
            length = s.get("record_len", len(patched))
            readback = self._ek_request_eeprom_sync(board, addr, length, timeout_s=3.0)
            ok = readback is not None and bytes(readback) == bytes(patched)
            self.after(0, lambda: self._ek_write_done(idx, ok, readback))
        except Exception as e:
            self.after(0, lambda e=e: self._ek_write_failed(str(e)))

    def _ek_write_done(self, idx: int, ok: bool, readback):
        self._btn_ek_write.config(state="normal")
        if ok:
            self._ek_status_var.set(f"Write OK — verified by readback (sequence UI index {idx}).")
            self._log_main(f"NanoZ_EK: wrote sequence {idx}, readback matches.")
        else:
            self._ek_status_var.set("Write sent, but readback did NOT match — check Console tab log for an error line, then re-read.")
            self._log_main(f"NanoZ_EK: wrote sequence {idx}, readback MISMATCH — "
                           f"got {readback.hex() if readback else None}. Re-read to confirm current state.")

    def _ek_write_failed(self, msg: str):
        self._btn_ek_write.config(state="normal")
        self._ek_status_var.set(f"Write failed: {msg}")
        self._log_main(f"NanoZ_EK: write failed — {msg}")

    def _charts_tab_visible(self):
        if not _MPL:
            return False
        try:
            return self._sub_nb.select() == str(self._charts_tab)
        except Exception:
            return False

    def _refresh_charts_loop(self):
        # Only auto-redraw while following live data. A manual pan/zoom (or
        # an in-progress drag) sets _chart_follow_live False; redrawing then
        # would clear+replot the axes out from under the user's drag every
        # 300ms, visually snapping the view back mid-gesture. Once paused,
        # nothing redraws until "Jump to Live" is pressed.
        if self._charts_tab_visible() and self._chart_follow_live:
            self._redraw_charts()
        self.after(300, self._refresh_charts_loop)

    @staticmethod
    def _pkt_time(item: dict):
        ts = item.get("host_timestamp")
        if not ts:
            return None
        try:
            return dt.datetime.fromisoformat(ts)
        except ValueError:
            return None

    def _elapsed_seconds(self, hist: list, t0: "dt.datetime"):
        out = []
        for item in hist:
            t = self._pkt_time(item)
            out.append((t - t0).total_seconds() if t else float("nan"))
        return out

    def _break_gaps(self, xs: list, ys: list):
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

    def _plot_series(self, ax, xs: list, hist: list, field: str, label: str, linestyle: str = "-"):
        ys = [r.get(field, 0) for r in hist]
        gx, gy = self._break_gaps(xs, ys)
        ax.plot(gx, gy, label=label, linestyle=linestyle)

    def _plot_computed(self, ax, xs: list, hist: list, value_fn, label: str, linestyle: str = "-"):
        ys = [value_fn(r) for r in hist]
        ys = [float("nan") if y is None else y for y in ys]
        gx, gy = self._break_gaps(xs, ys)
        ax.plot(gx, gy, label=label, linestyle=linestyle)

    # Graph settings (matches Nanoz_EK.exe's "Sensors"/"Heaters" dropdowns,
    # manual section V.A): Sensors = Current or Resistance; Heaters =
    # Voltage, Current, Power or Resistance. Resistance(Ohm) = V(mV)/I(mA)
    # (units cancel: mV/mA = V/A = Ohm). Power(mW) = V(mV)*I(mA)/1000.
    _SENSOR_METRIC_UNITS = {"Current": "mA", "Resistance": "Ω"}
    _HEATER_METRIC_UNITS = {"Voltage": "mV", "Current": "mA", "Power": "mW", "Resistance": "Ω"}

    def _sensor_metric_value(self, rec: dict, s: int):
        metric = self._chart_sensor_metric_var.get()
        if metric == "Resistance":
            v, i = rec.get(f"dac_mv_s{s}"), rec.get(f"adc_current_ma_s{s}")
            return v / i if (v is not None and i) else None
        return rec.get(f"adc_current_ma_s{s}")

    def _heater_metric_value(self, rec: dict, h: int):
        metric = self._chart_heater_metric_var.get()
        v, i = rec.get(f"heater{h}_voltage_mv"), rec.get(f"heater{h}_current_ma")
        if metric == "Voltage":
            return v
        if metric == "Current":
            return i
        if metric == "Power":
            return v * i / 1000 if (v is not None and i is not None) else None
        if metric == "Resistance":
            return v / i if (v is not None and i) else None
        return None

    def _on_chart_xlim_changed(self, _ax):
        if self._chart_programmatic_xlim:
            return
        # A real user pan/zoom (toolbar) moved the view - stop auto-scrolling
        # so _redraw_charts doesn't yank it back to the live edge every cycle.
        self._chart_follow_live = False

    def _on_chart_button_press(self, _event):
        # Fires on any mouse-down inside the chart canvas, including the
        # start of a toolbar pan/zoom drag - pausing here (rather than
        # waiting for xlim_changed) means the 300ms auto-redraw loop can't
        # sneak in a redraw mid-drag and snap the view back to live before
        # the drag itself has moved anything yet.
        self._chart_follow_live = False

    def _chart_resume_live(self):
        self._chart_follow_live = True
        self._redraw_charts()

    def _redraw_charts(self, preserve_view: bool = False):
        # preserve_view=True is for redraws triggered by a settings toggle
        # (channel/chip checkbox, metric dropdown) rather than by the live
        # data loop or the Jump to Live button - those should only ever
        # change which series are drawn, never yank the visible time
        # window back to the live edge, even while still in live-follow
        # mode (otherwise every checkbox click felt like an unwanted jump).
        if not _MPL:
            return
        port = self.console_board_var.get()
        hist_by_chip = {
            "0": list(self._spl_history.get((port, "0"), ())),
            "1": list(self._spl_history.get((port, "1"), ())),
        }
        env_hist = list(self._env_history.get(port, ()))

        prev_xlim = self._chart_ax_v.get_xlim()
        self._chart_ax_v.clear()
        self._chart_ax_i.clear()
        self._chart_ax_t.clear()

        candidates = [self._pkt_time(h[0]) for h in (*hist_by_chip.values(), env_hist) if h]
        candidates = [t for t in candidates if t is not None]
        t0 = min(candidates) if candidates else dt.datetime.now()
        t_max = 0.0
        visible = self._chart_visible_vars
        chip_visible = self._chart_chip_visible_vars

        any_spl = False
        for chip, hist, linestyle in (("0", hist_by_chip["0"], "-"), ("1", hist_by_chip["1"], "--")):
            if not hist or not chip_visible[chip].get():
                continue
            any_spl = True
            xs = self._elapsed_seconds(hist, t0)
            t_max = max(t_max, max(xs, default=0.0))
            for h in (1, 2):
                if visible[f"h{h}"].get():
                    self._plot_computed(self._chart_ax_v, xs, hist,
                                        lambda r, h=h: self._heater_metric_value(r, h),
                                        f"chip{chip}-h{h}", linestyle=linestyle)
            for s in (1, 2, 3, 4):
                if visible[f"s{s}"].get():
                    self._plot_computed(self._chart_ax_i, xs, hist,
                                        lambda r, s=s: self._sensor_metric_value(r, s),
                                        f"chip{chip}-s{s}", linestyle=linestyle)
        if any_spl:
            self._chart_ax_v.legend(fontsize=6, loc="upper left", ncol=2)
            self._chart_ax_i.legend(fontsize=6, loc="upper left", ncol=4)
        else:
            for ax in (self._chart_ax_v, self._chart_ax_i):
                ax.text(0.5, 0.5, "no SPL data yet (needs an active run)",
                        ha="center", va="center", transform=ax.transAxes, color="#999999")

        if env_hist:
            xs2 = self._elapsed_seconds(env_hist, t0)
            t_max = max(t_max, max(xs2, default=0.0))
            self._plot_series(self._chart_ax_t, xs2, env_hist, "temp_h_c", "temp_h_c")
            self._plot_series(self._chart_ax_t, xs2, env_hist, "mcu_temperature_c", "mcu_temp")
            self._chart_ax_t.legend(fontsize=7, loc="upper left")
        else:
            self._chart_ax_t.text(0.5, 0.5, "no ENV data yet", ha="center", va="center",
                                  transform=self._chart_ax_t.transAxes, color="#999999")

        h_metric = self._chart_heater_metric_var.get()
        s_metric = self._chart_sensor_metric_var.get()
        self._chart_ax_v.set_title(
            f"Heater {h_metric} ({self._HEATER_METRIC_UNITS[h_metric]}) — SPL (both chips)", fontsize=9)
        self._chart_ax_i.set_title(
            f"Sensor {s_metric} ({self._SENSOR_METRIC_UNITS[s_metric]}) — SPL (both chips)", fontsize=9)
        self._chart_ax_t.set_title("Temperature (°C) — ENV", fontsize=9)
        live_note = "" if self._chart_follow_live else "  [PAUSED — ▶ Jump to Live to resume auto-scroll]"
        self._chart_ax_t.set_xlabel(f"time (s, board {port or '—'}){live_note}")

        self._chart_programmatic_xlim = True
        try:
            if self._chart_follow_live and not preserve_view:
                self._chart_ax_v.set_xlim(max(0.0, t_max - self._CHART_WINDOW_S), max(t_max, self._CHART_WINDOW_S))
            else:
                self._chart_ax_v.set_xlim(prev_xlim)
        finally:
            self._chart_programmatic_xlim = False
        self._chart_canvas.draw_idle()

    _LOCKABLE_WIDGETS = ("_cycle_entry", "_duration_entry", "_btn_discover",
                        "_btn_connect_boards", "_btn_disconnect_boards",
                        "_btn_connect_prober", "_btn_load_map",
                        "_btn_manual_zup", "_btn_manual_zdown", "_btn_manual_first_die",
                        "_btn_manual_next_die", "_btn_manual_xy", "_btn_manual_unload",
                        "_btn_measure", "_btn_randomize_sites",
                        "_btn_test_active", "_btn_pause_active",
                        "_btn_recipe_add", "_btn_recipe_dup", "_btn_recipe_remove",
                        "_btn_recipe_up", "_btn_recipe_down",
                        "_btn_recipe_enable_all", "_btn_recipe_disable_all",
                        "_btn_recipe_import_plan")

    _CHART_HISTORY_LEN = 300
    _CHART_GAP_THRESHOLD_S = 3.0
    _CHART_WINDOW_S = 15.0

    def _set_locked(self, locked: bool):
        state = "disabled" if locked else "normal"
        for attr in self._LOCKABLE_WIDGETS:
            getattr(self, attr).config(state=state)

    def _log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"{ts}  {msg}"
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _log_main(self, msg: str):
        self._log(msg)
        if hasattr(self.controller, "log"):
            self.controller.log(f"[NANOZ] {msg}")

    def _discover_boards(self):
        threading.Thread(target=self._discover_boards_thread, daemon=True).start()

    def _discover_boards_thread(self):
        self.after(0, lambda: self._log("Scanning COM ports for NanoZ boards..."))
        found = nzb.discover_boards(log=lambda m: self.after(0, lambda m=m: self._log(m)))
        self.after(0, lambda: self._on_discovered(found))

    @staticmethod
    def _synthetic_board_key(serial_number: str) -> str:
        # Used for a "known" board that isn't currently reachable on any
        # live COM port (e.g. remembered from a previous session, not yet
        # plugged in this run) - self._boards still needs some dict key,
        # but it can't be a real port since there isn't one yet.
        return f"SN:{serial_number}"

    def _add_board(self, ident: "nzb.BoardIdentity"):
        # Match by serial number first, not port - Windows can (and does)
        # reassign a board to a different COM port across replugs/reboots,
        # so keying purely on port equality created a second, duplicate
        # entry (and a duplicate row in ata_nanoz_boards.json) for the same
        # physical board every time it came back on a different port.
        existing_key = None
        if ident.serial_number:
            for key, b in self._boards.items():
                if b.identity.serial_number == ident.serial_number:
                    existing_key = key
                    break
        new_key = ident.port or self._synthetic_board_key(ident.serial_number)

        if existing_key is not None:
            if existing_key == new_key:
                return None
            # Same physical board (by S/N), now reachable at a different
            # key (a real port replacing a placeholder, or a genuine port
            # change) - migrate the existing NanoZBoard object instead of
            # creating a duplicate. Slot assignments are kept from
            # whichever side already had them.
            board = self._boards.pop(existing_key)
            old_iid = self._board_rows.pop(existing_key, None)
            old_identity = board.identity
            board.identity = nzb.BoardIdentity(
                port=ident.port, serial_number=ident.serial_number,
                firmware=ident.firmware, signature=ident.signature,
                raw_ver=ident.raw_ver, raw_whoami=ident.raw_whoami, usb_id=ident.usb_id,
                slot0=old_identity.slot0 if old_identity.slot0 is not None else ident.slot0,
                slot1=old_identity.slot1 if old_identity.slot1 is not None else ident.slot1,
            )
            board.port = ident.port
            self._boards[new_key] = board
            if old_iid is not None:
                self._board_tree.item(old_iid, values=(
                    board.identity.port or "—", board.identity.serial_number,
                    board.identity.firmware, board.identity.signature,
                    board.identity.slot0 if board.identity.slot0 else "—",
                    board.identity.slot1 if board.identity.slot1 else "—",
                    self._board_status_text(board), 0, 0))
                self._board_rows[new_key] = old_iid
            return board

        if new_key in self._boards:
            return None
        try:
            env_interval_s = float(self.env_interval_var.get())
        except ValueError:
            env_interval_s = 1.0
        board = nzb.NanoZBoard(ident, self._queue, env_interval_s=env_interval_s)
        # die_provider reads board.port live (not a value captured at
        # creation time) so it keeps working correctly if this same board
        # object is later migrated to a different real port above.
        board._die_provider = lambda chip: self._die_provider(board.port, chip)
        self._boards[new_key] = board
        iid = self._board_tree.insert("", "end", values=(
            ident.port or "—", ident.serial_number, ident.firmware, ident.signature,
            ident.slot0 if ident.slot0 else "—",
            ident.slot1 if ident.slot1 else "—",
            self._board_status_text(board), 0, 0))
        self._board_rows[new_key] = iid
        return board

    def _persist_boards(self):
        folder = self._nanoz_ata_folder
        if not folder:
            return
        try:
            nzb.save_known_boards(folder, [b.identity for b in self._boards.values()])
        except OSError as e:
            self._log(f"Could not save NanoZ board memory: {e}")

    def _on_discovered(self, found: list):
        added = sum(1 for ident in found if self._add_board(ident))
        self._log_main(f"Discovery complete — {len(found)} board(s) found, "
                       f"{added} new, {len(self._boards)} total known.")
        self._refresh_console_boards()
        self._refresh_active_boards_label()
        self._rebuild_recipe_columns()
        self._persist_boards()

    def _connect_boards(self):
        targets = [b for b in self._boards.values() if b.state != "connected"]
        if not targets:
            self._log_main("Connect All: nothing to connect (discover boards first, "
                           "or everything known is already connected).")
            return
        threading.Thread(target=self._connect_boards_thread, args=(targets,), daemon=True).start()

    def _connect_boards_thread(self, targets: list):
        for board in targets:
            was_error = board.state == "error"
            try:
                board.reconnect() if was_error else board.start()
                verb = "reconnected" if was_error else "connected"
                self.after(0, lambda p=board.port, b=board: self._set_board_status(
                    p, self._board_status_text(b)))
                self.after(0, lambda p=board.port, v=verb: self._log(f"{p}: {v}, reader running"))
            except Exception as e:
                self.after(0, lambda p=board.port, e=e: self._set_board_status(
                    p, self._error_status_text(e)))
                self.after(0, lambda p=board.port, e=e: self._log(f"{p}: connect failed — {e}"))
        self.after(0, lambda: self._log_main(
            f"{sum(1 for b in targets if b.state == 'connected')}/{len(targets)} board(s) connected."))
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
        for board in targets:
            board.stop()
            self.after(0, lambda p=board.port, b=board: self._set_board_status(
                p, self._board_status_text(b)))
        self.after(0, lambda: self._log_main(
            f"{len(targets)} board(s) disconnected (ports closed)."))
        self.after(0, self._refresh_active_boards_label)

    def _set_board_status(self, port: str, status: str):
        iid = self._board_rows.get(port)
        if not iid:
            return
        vals = list(self._board_tree.item(iid, "values"))
        vals[6] = status
        self._board_tree.item(iid, values=vals)

    def _set_board_counts(self, port: str, spl: int, env: int):
        iid = self._board_rows.get(port)
        if not iid:
            return
        vals = list(self._board_tree.item(iid, "values"))
        vals[7], vals[8] = spl, env
        self._board_tree.item(iid, values=vals)

    def _on_board_tree_double_click(self, event):
        if self._board_tree.identify_region(event.x, event.y) != "cell":
            return
        row_iid = self._board_tree.identify_row(event.y)
        col_id = self._board_tree.identify_column(event.x)
        if not row_iid or not col_id:
            return
        cols = self._board_tree["columns"]
        col_idx = int(col_id[1:]) - 1
        if not (0 <= col_idx < len(cols)) or cols[col_idx] not in ("slot0", "slot1"):
            return
        chip = "0" if cols[col_idx] == "slot0" else "1"
        vals_idx = 4 if chip == "0" else 5
        # Look up by the internal dict key (via the iid), not the displayed
        # port text - a not-yet-discovered known board shows "—" in the
        # port column (its real port isn't known yet), which wouldn't
        # match any real self._boards key.
        key = next((k for k, v in self._board_rows.items() if v == row_iid), None)
        board = self._boards.get(key) if key is not None else None
        if not board:
            return
        label = board.identity.port or f"SN {board.identity.serial_number}"
        current = board.identity.slot0 if chip == "0" else board.identity.slot1
        new_slot = simpledialog.askinteger(
            "Assign Probe-Card Slot",
            f"Physical slot for {label}'s chip {chip} (1-20, top to bottom of the probe head):",
            initialvalue=current or 1, minvalue=1, maxvalue=99, parent=self)
        if new_slot is None:
            return
        if chip == "0":
            board.identity.slot0 = new_slot
        else:
            board.identity.slot1 = new_slot
        vals = list(self._board_tree.item(row_iid, "values"))
        vals[vals_idx] = str(new_slot)
        self._board_tree.item(row_iid, values=vals)
        self._persist_boards()
        self._rebuild_recipe_columns()
        self._refresh_console_boards()
        self._log_main(f"{label} chip {chip} assigned to probe-card slot {new_slot}.")

    @staticmethod
    def _error_status_text(err) -> str:
        return f"⚠ error: {err}"[:80]

    def _board_status_text(self, board: "nzb.NanoZBoard") -> str:
        state = board.state
        if state == "error":
            return self._error_status_text(board.last_error)
        if state == "connected":
            return "✅ connected"
        return "— not connected"

    def _refresh_board_status_quiet(self):
        for port, board in self._boards.items():
            self._set_board_status(port, self._board_status_text(board))

    def _auto_refresh_board_status(self):
        self._refresh_board_status_quiet()
        self.after(1000, self._auto_refresh_board_status)

    def _refresh_board_status(self):
        self._refresh_board_status_quiet()
        connected = sum(1 for b in self._boards.values() if b.state == "connected")
        errored = sum(1 for b in self._boards.values() if b.state == "error")
        idle = len(self._boards) - connected - errored
        self._log_main(f"Refresh Status — {connected} connected, {errored} error(s), "
                       f"{idle} not connected ({len(self._boards)} known).")

    def _refresh_active_boards_label(self):
        active = [b for b in self._boards.values() if b.state == "connected"]
        if not active:
            self.active_boards_var.set("No boards connected yet — see the Setup tab.")
        else:
            self.active_boards_var.set(
                f"{len(active)} board(s) ready: " + ", ".join(b.port for b in active))

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

    def _load_wafer_map(self):
        folder = self._nanoz_ata_folder
        if not folder:
            messagebox.showerror("No ATA Folder",
                                 "Load an ATA folder from the toolbar first.")
            return
        n = self.wafer_map.load_from_ata(folder, filename="ata_wafer_map_accretech.csv")
        self._log_main(f"Wafer map loaded from '{os.path.basename(folder)}' — {n} die(s).")

    def on_ata_folder_loaded(self, folder_path: str):
        n = self.wafer_map.load_from_ata(folder_path, filename="ata_wafer_map_accretech.csv")
        if n:
            self._log_main(f"Wafer map auto-loaded from "
                           f"'{os.path.basename(folder_path)}' — {n} die(s).")

        remembered = nzb.load_known_boards(folder_path)
        added = sum(1 for ident in remembered if self._add_board(ident))
        if added:
            self._log_main(f"Remembered {added} NanoZ board(s) from this ATA folder "
                           f"— Connect All once they're plugged in.")
            self._refresh_console_boards()
            self._refresh_active_boards_label()

        migrated = nzb.migrate_legacy_recipe(folder_path)
        if migrated:
            self._log_main(f"Migrated the old unnamed NanoZ recipe into '{migrated}'.")
        name, shots, wafer_plan_path = nzb.load_active_recipe(folder_path)
        self._shots = shots
        self._current_recipe_name = name
        self._wafer_plan_path = wafer_plan_path
        if shots:
            self._log_main(f"Recipe '{name}' auto-loaded from "
                           f"'{os.path.basename(folder_path)}' — {len(shots)} shot(s).")
        self._refresh_recipe_name_cb()
        self._rebuild_recipe_columns()
        if name:
            self._autoload_wafer_plan_for_recipe(folder_path, name)
        else:
            self._wafer_plan = None
            self._redraw_nanoz_wafer_map()

    def _refresh_console_boards(self):
        ports = sorted(self._boards.keys())
        labels = [self._board_label(p) for p in ports]
        self._board_label_to_port = dict(zip(labels, ports))
        self._console_board_cb.config(values=labels)
        self._chart_board_cb.config(values=labels)
        if self.console_board_var.get() not in ports and ports:
            self.console_board_var.set(ports[0])
        current = self.console_board_var.get()
        if current in self._boards:
            self._console_board_label_var.set(self._board_label(current))
        self._refresh_console_reading()
        if hasattr(self, "_ek_board_cb"):
            self._ek_refresh_board_list()

    def _on_console_board_picked(self, _event=None):
        port = self._board_label_to_port.get(self._console_board_label_var.get())
        if port:
            self.console_board_var.set(port)
        self._refresh_console_reading()

    def _console_selected_board(self):
        return self._boards.get(self.console_board_var.get())

    def _console_send(self, cmd: str):
        board = self._console_selected_board()
        if not board or not board.is_running:
            messagebox.showerror("No Board Selected",
                                 "Pick a connected board first (Setup tab -> Connect All).")
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
        if not messagebox.askyesno(
            "Run Calibration",
            "calib! runs the EK-IV's calibration routine and REQUIRES the "
            "10K-resistor calibration kit to be mounted in place of the "
            "normal sensors. Running it with real sensors attached will "
            "produce meaningless calibration offsets.\n\nContinue?"):
            return
        self._console_send("calib!")

    def _console_cleep(self):
        if not messagebox.askyesno(
            "Erase EEPROM",
            "cleep erases every stored cycle/sequence on this board's "
            "non-volatile memory. This cannot be undone from here — the "
            "board will need to be reprogrammed with Nanoz_EK before it "
            "can run a cycle again.\n\nContinue?"):
            return
        self._console_send("cleep")

    def _console_read_eeprom(self):
        board = self._console_selected_board()
        if not board or not board.is_running:
            messagebox.showerror("No Board Selected",
                                 "Pick a connected board first (Setup tab -> Connect All).")
            return
        try:
            addr = int(self.console_eep_addr_var.get())
            length = int(self.console_eep_len_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Address and length must be whole numbers.")
            return
        board.request_eeprom(addr, length)
        self._log(f"{board.port}: >> rdeep {addr} {length}")

    @staticmethod
    def _format_reading_lines(item: "dict | None"):
        if not item:
            return ["(none yet)"]
        return [f"{k}: {v}" for k, v in item.items() if k not in ("kind", "port")]

    @staticmethod
    def _format_eep_lines(item: "dict | None"):
        if not item:
            return ["(none yet)"]
        data_hex = item.get("data_hex", "")
        rows = [f"{k}: {v}" for k, v in item.items() if k not in ("kind", "port", "data_hex")]
        rows.append("")
        rows.append("data:")
        for i in range(0, len(data_hex), 32):
            offset = i // 2
            rows.append(f"  +{offset:04d}  {data_hex[i:i + 32]}")
        return rows

    def _refresh_console_reading(self):
        port = self.console_board_var.get()
        chip = self.console_chip_var.get()
        spl_lines = self._format_reading_lines(self._latest_spl.get((port, chip)))
        env_lines = self._format_reading_lines(self._latest_env.get(port))
        for widget, lines in ((self.console_spl_text, spl_lines),
                              (self.console_env_text, env_lines)):
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("1.0", "\n".join(lines))
            widget.configure(state="disabled")
        self._refresh_console_eep_display()

    def _refresh_console_eep_display(self):
        port = self.console_board_var.get()
        lines = self._format_eep_lines(self._latest_eep.get(port))
        self.console_eep_text.configure(state="normal")
        self.console_eep_text.delete("1.0", "end")
        self.console_eep_text.insert("1.0", "\n".join(lines))
        self.console_eep_text.configure(state="disabled")

    def _new_csv_paths(self):
        folder = (self._nanoz_ata_folder
                 or self._main_layout.export_path_var.get()
                 or os.getcwd())
        os.makedirs(folder, exist_ok=True)
        run_id = time.strftime("%Y%m%d_%H%M%S")
        return (os.path.join(folder, f"ata_nanoz_spl_{run_id}.csv"),
               os.path.join(folder, f"ata_nanoz_env_{run_id}.csv"))

    def _check_queue(self):
        drained = 0
        while drained < 500:
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
            chip = str(item.get("header_chip", ""))
            key = (port, chip)
            self._spl_total += 1
            self._touchdown_packets += 1
            if "parse_error" in item:
                self._touchdown_errors += 1
            self._latest_spl[key] = item
            self._spl_history.setdefault(
                key, collections.deque(maxlen=self._CHART_HISTORY_LEN)).append(item)
            if self._spl_path:
                row = {k: v for k, v in item.items() if k != "kind"}
                try:
                    nzb.append_csv_row(self._spl_path, row)
                except OSError as e:
                    self._log(f"SPL CSV write error: {e}")
            if board:
                self._set_board_counts(port, board.spl_count, board.env_count)
            if port == self.console_board_var.get() and chip == self.console_chip_var.get():
                self._refresh_console_reading()
        elif kind == "env":
            self._env_total += 1
            self._touchdown_packets += 1
            if "parse_error" in item:
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
        elif kind == "eep":
            self._latest_eep[port] = item
            status = "OK" if item.get("checksum_ok") else "CHECKSUM MISMATCH"
            self._log(f"{port}: EEPROM read addr={item['addr']} len={item['len']} ({status})")
            if port == self.console_board_var.get():
                self._refresh_console_eep_display()

    def _start_lot(self):
        if self._running:
            self._log_main("A run is already active.")
            return
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            messagebox.showerror("Prober Not Connected", "🔌 Connect Prober first.")
            return
        active = [b for b in self._boards.values() if b.state == "connected"]
        if not active:
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect All (Setup tab) — no NanoZ boards are connected.")
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
        self.recipe_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.state_var.set("RUNNING (Full Die)")
        self._set_locked(True)
        self._lot_thread = threading.Thread(
            target=self._lot_thread_body, args=(prober, active, cycle, duration_s), daemon=True)
        self._lot_thread.start()

    def _stop_lot(self):
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

    def _run_guard(self, name: str) -> bool:
        if self._running:
            messagebox.showerror("Run Active", f"{name}: stop the current run first.")
            return True
        return False

    def _do_manual_call(self, name: str, fn, log_cmd: str, refresh_xy: bool = False):
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
        if self._run_guard("Measure"):
            return
        active = [b for b in self._boards.values() if b.state == "connected"]
        if not active:
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect All (Setup tab) — no NanoZ boards are connected.")
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
        if self._run_guard("Run Cycle"):
            return
        active = [b for b in self._boards.values() if b.state == "connected"]
        if not active:
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect All (Setup tab) — no NanoZ boards are connected.")
            return
        try:
            cycle = int(self.cycle_var.get())
        except ValueError:
            messagebox.showerror("Invalid Cycle", "Cycle # must be a whole number.")
            return
        self._mark_cycle_start()
        for board in active:
            board.run_cycle(cycle)
        self._log_main(f"Run Cycle {cycle} triggered on {len(active)} active board(s): "
                       + ", ".join(b.port for b in active))

    def _pause_active_boards(self):
        if self._run_guard("Pause"):
            return
        active = [b for b in self._boards.values() if b.state == "connected"]
        if not active:
            self._log_main("Pause (Active Boards): nothing connected.")
            return
        for board in active:
            board.pause()
        self._log_main(f"Paused {len(active)} active board(s): "
                       + ", ".join(b.port for b in active))

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
        if stb != 67:
            return
        self.after(0, lambda: self._log("finished chuck UP (STB=67 — contact) >> D  (Separate)"))
        prober.z_down()

    def _zup_measure_zdown(self, prober, boards: list, cycle: int, duration_s: float, label: str) -> bool:
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
        active = [b for b in self._boards.values() if b.state == "connected"]
        if not active:
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect All (Setup tab) — no NanoZ boards are connected.")
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
        self.recipe_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.state_var.set("RUNNING (Test Die)")
        self.wafer_map.enable_picking(0)
        self._set_locked(True)
        self._lot_thread = threading.Thread(
            target=self._test_die_thread_body, args=(prober, active, sites, cycle, duration_s),
            daemon=True)
        self._lot_thread.start()

    def _test_die_thread_body(self, prober, boards: list, sites: list, cycle: int, duration_s: float):
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

    def _die_provider(self, port: str, chip: "str | None"):
        """(row, col) to tag a reading with. During a Recipe run, each board's
        two chips sit at different physical probe-head slots on the same
        touchdown — use that board's slot0/slot1 offset from the touchdown's
        top row so SPL readings get the die that chip actually contacted,
        not just the touchdown's anchor die. Falls back to the single
        manually-tracked _current_rc for Test Die / Full Die / manual modes,
        which probe one die at a time and have no per-chip slot concept."""
        anchor = self._current_touchdown
        if not anchor:
            return self._current_rc
        start_row, die_col = anchor
        board = self._boards.get(port)
        slot = None
        if board and chip in ("0", "1"):
            slot = board.identity.slot0 if chip == "0" else board.identity.slot1
        if slot:
            return (start_row + slot - 1, die_col)
        return (start_row, die_col)

    def _shot_active_boards(self, shot: dict) -> list:
        excluded = shot.get("excluded_boards", set())
        return [b for p, b in self._boards.items() if p not in excluded and b.state == "connected"]

    def _show_current_shot(self, idx: int, shot: dict):
        total = len(self._shots)
        self.recipe_shot_var.set(f"Shot {idx + 1}/{total}: {shot['label']}")
        for iid in self._shot_decision_tree.get_children():
            self._shot_decision_tree.delete(iid)
        excluded = shot.get("excluded_boards", set())
        reasons = shot.get("board_reasons") or {}
        chip_reasons = shot.get("chip_reasons") or {}
        for port in self._recipe_ports():
            board = self._boards.get(port)
            ident = board.identity if board else None
            s0 = ident.slot0 if ident and ident.slot0 else "—"
            s1 = ident.slot1 if ident and ident.slot1 else "—"
            slots = f"{s0}/{s1}"
            per_chip = chip_reasons.get(port)
            if port in excluded:
                decision = "SKIP"
                reason = reasons.get(port) or "excluded (manual)"
            elif not board or board.state != "connected":
                decision = "SKIP"
                reason = "not connected"
            else:
                decision = "RUN"
                if per_chip:
                    reason = "; ".join(
                        f"chip{c}: {r or 'product'}" for c, r in per_chip.items())
                else:
                    reason = "—"
            self._shot_decision_tree.insert("", "end", values=(port, slots, decision, reason))

    def _start_recipe_run(self):
        if self._running:
            self._log_main("A run is already active.")
            return
        if not self._shots:
            messagebox.showerror("No Recipe",
                                 "No recipe shots defined — import a wafer plan or add "
                                 "shots on the Recipe tab first.")
            return
        prober = self.controller.drivers.get("prober")
        if not prober or not prober.inst:
            messagebox.showerror("Prober Not Connected", "🔌 Connect Prober first.")
            return
        if not any(b.state == "connected" for b in self._boards.values()):
            messagebox.showerror("No Boards Connected",
                                 "🔌 Connect All (Setup tab) — no NanoZ boards are connected.")
            return
        try:
            cycle = int(self.cycle_var.get())
            duration_s = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Invalid Parameters", "Cycle # and duration must be numeric.")
            return

        self._spl_path, self._env_path = self._new_csv_paths()
        self._log_main(f"Starting Run Recipe — {len(self._shots)} shot(s), cycle {cycle}, "
                       f"{duration_s:g}s/touchdown.")
        self._log(f"SPL CSV: {self._spl_path}")
        self._log(f"ENV CSV: {self._env_path}")

        self._reset_counts()
        self._running = True
        self._run_mode = "recipe"
        self.start_btn.config(state="disabled")
        self.test_btn.config(state="disabled")
        self.recipe_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.state_var.set("RUNNING (Recipe)")
        self.wafer_map.enable_picking(0)
        self._set_locked(True)
        self._lot_thread = threading.Thread(
            target=self._recipe_thread_body, args=(prober, cycle, duration_s), daemon=True)
        self._lot_thread.start()

    def _recipe_thread_body(self, prober, cycle: int, duration_s: float):
        try:
            self.after(0, lambda: self._log(">> D  (Separate)"))
            prober.z_down()

            shots = self._shots
            idx = 0
            while self._running and idx < len(shots):
                shot = shots[idx]
                die_col = shot.get("die_column")
                row = shot.get("td_start_row")
                self.after(0, lambda i=idx, s=shot: self._show_current_shot(i, s))
                active_boards = self._shot_active_boards(shot)
                self.after(0, lambda i=idx, n=len(shots), s=shot, ab=active_boards: self._log_main(
                    f"Shot {i + 1}/{n}: {s['label']} — "
                    + (f"{len(ab)} board(s) active: " + ", ".join(b.port for b in ab)
                       if ab else "no boards active, skipping touchdown")))

                if die_col is None or row is None or not active_boards:
                    idx += 1
                    continue

                self._current_rc = (row, die_col)
                self._current_touchdown = (row, die_col)
                die_label = f"R{row}C{die_col}"
                self.after(0, lambda dl=die_label: self.die_var.set(f"Die: {dl}"))
                self.after(0, lambda r=row, c=die_col: self.wafer_map.update_die(r, c, "CURRENT"))

                self.after(0, lambda r=row, c=die_col: self._log(f">> J  (Position die X={c} Y={r})"))
                stb = prober.move_to_die_xy(die_col, row)
                if stb == 81:
                    self.after(0, lambda: self._log_main("STB=81 — wafer end, stopping."))
                    break
                if stb == 90:
                    self.after(0, lambda: self._log_main(
                        "STB=90 — probing stop (<STOP> pushed), stopping."))
                    break
                self.after(0, lambda stb=stb: self._log(f"<< STB={stb}"))
                self._ensure_separated(prober, stb)

                ok = self._zup_measure_zdown(prober, active_boards, cycle, duration_s, shot["label"])
                if not self._running:
                    break
                status = "PASS" if ok else "FAIL"
                if status == "PASS":
                    self._pass_count += 1
                else:
                    self._fail_count += 1
                self.after(0, self._update_pass_fail_display)
                self.after(0, lambda r=row, c=die_col, s=status: self.wafer_map.update_die(r, c, s))

                idx += 1
        except Exception as e:
            self.after(0, lambda e=e: self._log_main(f"ERROR: {e}"))
        finally:
            for board in self._boards.values():
                try:
                    board.pause()
                except Exception:
                    pass
            self._running = False
            self._run_mode = None
            self._current_touchdown = None
            self.after(0, lambda: self._finish_lot("RECIPE RUN COMPLETE"))

    _WAFER_READY_TIMEOUT_S = 60.0
    _NEXT_DIE_TIMEOUT_S = 60.0
    _UNLOAD_LOAD_TIMEOUT_S = 180.0

    def _lot_thread_body(self, prober, boards: list, cycle: int, duration_s: float):
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
        except Exception as e:
            self.after(0, lambda e=e: self._log_main(f"ERROR: {e}"))
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
        self.recipe_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.state_var.set(msg)
        self._set_locked(False)
        self.wafer_map.enable_picking(on_change=self._on_sites_changed)
        self._log_main(f"{msg} — heaters paused on all boards.")

    def _trigger_cycle_and_wait(self, boards: list, cycle: int, duration_s: float, label: str) -> bool:
        self._touchdown_errors = 0
        self._touchdown_packets = 0
        self._mark_cycle_start()
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

    def _mark_cycle_start(self):
        self._cycle_start_time = dt.datetime.now() - dt.timedelta(milliseconds=5)

    def _reset_counts(self):
        self._pass_count = 0
        self._fail_count = 0
        self._mark_cycle_start()
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
