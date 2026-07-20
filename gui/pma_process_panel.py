import os
import tkinter as tk
from tkinter import ttk, filedialog

import electroglas_pma as egpma

PMA_SOURCE_SUBDIR = "pma_source"


class PmaProcessPanel(ttk.Frame):
    def __init__(self, parent, controller, main_layout):
        super().__init__(parent)
        self.controller = controller
        self._main_layout = main_layout
        self._pma_path = ""
        self._fields = {}
        self._touchdowns = []
        self._pma_choices = []
        self._xls_choices = []

        self.operator_var = tk.StringVar()
        self.process_step_var = tk.StringVar()
        self.recipe_name_var = tk.StringVar()
        self.prober_name_var = tk.StringVar(value="Electroglas 2001CXE")
        self.wafer_size_var = tk.StringVar()
        self._production_die_var = tk.StringVar(value="—")
        self.test_die_var = tk.StringVar(value="—")
        self._pma_picker_var = tk.StringVar()
        self._xls_picker_var = tk.StringVar()

        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_source_picker()
        self._build_run_setup()
        self._build_wafer_info()
        self._build_body()

    def _log(self, msg: str):
        self.controller.log(msg)

    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        ttk.Button(bar, text="📥  Load PMA File…", command=self._load_pma).pack(side="left")
        ttk.Button(bar, text="📥  Open Recipe Generator (.xls)…",
                  command=self._open_recipe_generator).pack(side="left", padx=(6, 0))
        ttk.Button(bar, text="🧪  Create Recipe from PMA",
                  command=self._create_recipe_from_pma).pack(side="left", padx=(6, 0))
        self._path_lbl = ttk.Label(bar, text="No PMA file loaded", foreground="gray")
        self._path_lbl.pack(side="left", padx=10)

    def _build_source_picker(self):
        bar = ttk.LabelFrame(
            self, text=f"ATA Folder Source ({PMA_SOURCE_SUBDIR}\\)", padding=6)
        bar.grid(row=1, column=0, sticky="ew", padx=6, pady=(2, 4))

        ttk.Label(bar, text="PMA:").pack(side="left")
        self._pma_picker = ttk.Combobox(
            bar, textvariable=self._pma_picker_var, state="readonly", width=28)
        self._pma_picker.pack(side="left", padx=(4, 12))
        self._pma_picker.bind("<<ComboboxSelected>>", self._on_pma_picked)

        ttk.Label(bar, text="Recipe Generator:").pack(side="left")
        self._xls_picker = ttk.Combobox(
            bar, textvariable=self._xls_picker_var, state="readonly", width=28)
        self._xls_picker.pack(side="left", padx=(4, 12))
        self._xls_picker.bind("<<ComboboxSelected>>", self._on_xls_picked)

        ttk.Button(bar, text="🔄  Rescan", command=self.scan_ata_folder).pack(side="left")

    def _build_run_setup(self):
        lf = ttk.LabelFrame(self, text="Run Setup", padding=8)
        lf.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 4))
        for i in range(6):
            lf.columnconfigure(i, weight=1)

        fields = (
            ("Lot ID:", self._main_layout.lot_id),
            ("Wafer ID:", self._main_layout.wafer_id_var),
            ("Operator:", self.operator_var),
            ("Process Step:", self.process_step_var),
            ("Recipe Name:", self.recipe_name_var),
            ("Prober Name:", self.prober_name_var),
        )
        for col, (label, var) in enumerate(fields):
            ttk.Label(lf, text=label).grid(row=0, column=col, sticky="w", padx=(0, 6))
            ttk.Entry(lf, textvariable=var, width=16).grid(
                row=1, column=col, sticky="ew", padx=(0, 6))

    def _build_wafer_info(self):
        lf = ttk.LabelFrame(self, text="Wafer Info", padding=8)
        lf.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 4))

        ttk.Label(lf, text="Wafer Size:").pack(side="left")
        ttk.Entry(lf, textvariable=self.wafer_size_var, width=10).pack(
            side="left", padx=(4, 16))

        ttk.Label(lf, text="Production Die #:").pack(side="left")
        ttk.Label(lf, textvariable=self._production_die_var,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(4, 16))

        ttk.Label(lf, text="Test Die #:").pack(side="left")
        ttk.Entry(lf, textvariable=self.test_die_var, width=8).pack(
            side="left", padx=(4, 0))

        ttk.Label(lf, text="(full wafer map now shown on the PMA Wafer tab)",
                 foreground="gray").pack(side="left", padx=(16, 0))

    def _build_body(self):
        split = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        split.grid(row=4, column=0, sticky="nsew", padx=6, pady=(0, 6))

        fields_lf = ttk.LabelFrame(split, text="Parsed PMA Fields", width=320)
        split.add(fields_lf, weight=0)
        fields_lf.pack_propagate(False)
        cols = ("field", "value")
        self._fields_tree = ttk.Treeview(
            fields_lf, columns=cols, show="headings", height=16, selectmode="browse")
        self._fields_tree.heading("field", text="Field")
        self._fields_tree.heading("value", text="Value")
        self._fields_tree.column("field", width=170)
        self._fields_tree.column("value", width=140)
        vsb1 = ttk.Scrollbar(fields_lf, orient="vertical", command=self._fields_tree.yview)
        self._fields_tree.configure(yscrollcommand=vsb1.set)
        vsb1.pack(side="right", fill="y")
        self._fields_tree.pack(fill="both", expand=True, padx=(4, 0), pady=4)

        move_lf = ttk.LabelFrame(split, text="Move List (G / J sequence)")
        split.add(move_lf, weight=1)
        cols2 = ("step", "command", "device_ids", "major_x", "major_y",
                "minor_x", "minor_y")
        self._move_tree = ttk.Treeview(
            move_lf, columns=cols2, show="headings", height=16, selectmode="browse")
        for cid, text, w in (("step", "#", 40), ("command", "Cmd", 40),
                             ("device_ids", "Device ID(s)", 110),
                             ("major_x", "MovesMajorX", 85), ("major_y", "MovesMajorY", 85),
                             ("minor_x", "MovesMinorX", 85), ("minor_y", "MovesMinorY", 85)):
            self._move_tree.heading(cid, text=text)
            self._move_tree.column(cid, width=w, anchor="center" if cid in
                                   ("step", "command") else "w")
        vsb2 = ttk.Scrollbar(move_lf, orient="vertical", command=self._move_tree.yview)
        self._move_tree.configure(yscrollcommand=vsb2.set)
        vsb2.pack(side="right", fill="y")
        self._move_tree.pack(fill="both", expand=True, padx=(4, 0), pady=4)

        self._summary_var = tk.StringVar(value="Load a .PMA file to begin.")
        ttk.Label(self, textvariable=self._summary_var, foreground="#374151").grid(
            row=5, column=0, sticky="w", padx=8, pady=(0, 6))

    def _pma_source_dir(self) -> str:
        folder = getattr(self._main_layout, "_ata_folder", "")
        return os.path.join(folder, PMA_SOURCE_SUBDIR) if folder else ""

    def scan_ata_folder(self):
        src_dir = self._pma_source_dir()
        pma_files, xls_files = [], []
        if src_dir and os.path.isdir(src_dir):
            for fname in sorted(os.listdir(src_dir)):
                path = os.path.join(src_dir, fname)
                if not os.path.isfile(path):
                    continue
                low = fname.lower()
                if low.endswith(".pma"):
                    pma_files.append(path)
                elif low.endswith(".xls"):
                    xls_files.append(path)

        self._pma_choices = pma_files
        self._pma_picker.config(values=[os.path.basename(p) for p in pma_files])
        if len(pma_files) == 1:
            self._pma_picker_var.set(os.path.basename(pma_files[0]))
            self.load_path(pma_files[0])
        else:
            self._pma_picker_var.set("")
            if len(pma_files) > 1:
                self._log(f"[PMA] {len(pma_files)} .PMA file(s) found in "
                          f"{PMA_SOURCE_SUBDIR}\\ — pick one from the PMA dropdown.")

        self._xls_choices = xls_files
        self._xls_picker.config(values=[os.path.basename(p) for p in xls_files])
        if len(xls_files) == 1:
            self._xls_picker_var.set(os.path.basename(xls_files[0]))
            self._load_recipe_generator_path(xls_files[0])
        else:
            self._xls_picker_var.set("")
            if len(xls_files) > 1:
                self._log(f"[PMA] {len(xls_files)} recipe-generator .xls file(s) found "
                          f"in {PMA_SOURCE_SUBDIR}\\ — pick one from the Recipe "
                          "Generator dropdown.")

    def _on_pma_picked(self, _evt=None):
        name = self._pma_picker_var.get()
        path = next((p for p in self._pma_choices if os.path.basename(p) == name), None)
        if path:
            self.load_path(path)

    def _on_xls_picked(self, _evt=None):
        name = self._xls_picker_var.get()
        path = next((p for p in self._xls_choices if os.path.basename(p) == name), None)
        if path:
            self._load_recipe_generator_path(path)

    def _load_pma(self):
        path = filedialog.askopenfilename(
            title="Load PMA File",
            filetypes=[("PMA recipe files", "*.PMA *.pma"), ("All files", "*.*")])
        if not path:
            return
        self.load_path(path)

    def _open_recipe_generator(self):
        pma_wafer = getattr(self._main_layout, "pma_wafer", None)
        if pma_wafer is None:
            self._log("[PMA] PMA Wafer tab is not available.")
            return
        pma_wafer.open_workbook_dialog()

    def _load_recipe_generator_path(self, path: str):
        pma_wafer = getattr(self._main_layout, "pma_wafer", None)
        if pma_wafer is None:
            self._log("[PMA] PMA Wafer tab is not available.")
            return
        pma_wafer.load_workbook_path(path)

    def _create_recipe_from_pma(self):
        if not self._pma_path:
            self._log("[PMA] Load a .PMA file first.")
            return
        recipe_panel = getattr(self._main_layout, "recipe_panel", None)
        if recipe_panel is None or not hasattr(recipe_panel, "import_legacy_from_path"):
            self._log("[PMA] Recipe tab is not available.")
            return
        if recipe_panel.import_legacy_from_path(self._pma_path):
            self.recipe_name_var.set(recipe_panel.get_active_recipe())

    def load_path(self, path: str):
        try:
            fields = egpma.parse_pma_file(path)
        except OSError as exc:
            self._log(f"[PMA] Error reading {path}: {exc}")
            return
        self._pma_path = path
        self._fields = fields
        self._path_lbl.config(text=path, foreground="black")

        self._fields_tree.delete(*self._fields_tree.get_children())
        for key in egpma.ALL_FIELDS:
            if key in fields:
                self._fields_tree.insert("", "end", values=(key, fields[key]))
        others = sorted(k for k in fields if k not in egpma.ALL_FIELDS)
        for key in others:
            self._fields_tree.insert("", "end", values=(key, fields[key]))

        touchdowns = egpma.load_touchdowns(path, fields)
        self._touchdowns = touchdowns

        self._production_die_var.set(str(len(touchdowns)))
        self.test_die_var.set(str(len(touchdowns)))

        pma_wafer = getattr(self._main_layout, "pma_wafer", None)
        if pma_wafer is not None and touchdowns:
            shot_data = egpma.to_shot_data(path, fields, touchdowns)
            pma_wafer.show_touchdowns(shot_data)

        move_list = egpma.build_move_list(touchdowns)
        self._move_list = move_list
        self._move_tree.delete(*self._move_tree.get_children())
        for m in move_list:
            self._move_tree.insert("", "end", values=(
                m["step"], m["command"], m["device_ids"],
                egpma.fmt_num(m["MovesMajorX"]), egpma.fmt_num(m["MovesMajorY"]),
                m["MovesMinorX"], m["MovesMinorY"]))

        ata_folder = getattr(self._main_layout, "_ata_folder", "")
        saved_note = ""
        if ata_folder and touchdowns:
            try:
                csv_path = egpma.save_wafer_map_csv(ata_folder, touchdowns)
                saved_note = f" — wafer map saved to {os.path.basename(csv_path)}"
            except OSError as exc:
                self._log(f"[PMA] Could not save wafer map CSV: {exc}")
        elif touchdowns:
            saved_note = " — load an ATA folder to persist the wafer map"

        recipe_panel = getattr(self._main_layout, "recipe_panel", None)
        recipe_note = ""
        if recipe_panel is not None:
            expected_name = os.path.splitext(os.path.basename(path))[0]
            if expected_name in recipe_panel.get_recipe_names():
                if recipe_panel.select_recipe(expected_name):
                    self.recipe_name_var.set(expected_name)
                    recipe_note = f" — loaded existing recipe '{expected_name}'"
            else:
                self.recipe_name_var.set("")
                recipe_note = (" — no matching recipe yet "
                               "(use 🧪 Create Recipe from PMA)")

        pin_wiring = getattr(self._main_layout, "pin_wiring", None)
        active_card = pin_wiring.get_active_card() if pin_wiring is not None else ""
        move_note = ""
        if pin_wiring is not None and active_card and move_list:
            if pin_wiring.save_move_list(active_card, move_list):
                move_note = f" — move list saved under probe card '{active_card}'"
            else:
                move_note = " — could not save the move list to the probe card"
        elif move_list:
            move_note = " — select/create a probe card first to save the move list"

        self._summary_var.set(
            f"{len(touchdowns)} touchdown(s), {len(move_list)} move(s) parsed from "
            f"{os.path.basename(path)}{saved_note}{recipe_note}{move_note} — "
            "see PMA Wafer tab for the map")
        self._log(f"[PMA] Loaded {path}: {len(touchdowns)} touchdown(s), "
                  f"{len(move_list)} move(s){saved_note}{recipe_note}{move_note}")
