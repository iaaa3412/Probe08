"""Results table for the Electroglas NanoZ Results tab - shows every die
measured this session (gui/eg_nanoz_recipe_panel.py's results_history,
appended to by run_cycle_and_collect) plus pass/fail counts. CSV export
already happens automatically per die in run_cycle_and_collect
(ata_nanoz_electroglas_results.csv in the active ATA folder); this tab
is a live view of that same data, not a second export path.
"""

import os
import tkinter as tk
from tkinter import ttk


class EgNanozResultsPanel(ttk.Frame):
    def __init__(self, parent, recipe_panel, get_ata_folder):
        super().__init__(parent)
        self._recipe = recipe_panel
        self._get_ata_folder = get_ata_folder
        self._last_len = 0

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        self._summary_var = tk.StringVar(value="0 measured — 0 pass, 0 fail")
        ttk.Label(bar, textvariable=self._summary_var, font=("Segoe UI", 10, "bold")
                 ).pack(side="left")
        self._csv_path_var = tk.StringVar(value="")
        ttk.Label(bar, textvariable=self._csv_path_var, foreground="#6b7280",
                 font=("Segoe UI", 8)).pack(side="right")

        cols = ("die_id", "row", "col", "slot", "board", "chip", "pass")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        for col, head, width in (("die_id", "Die", 100), ("row", "row", 50),
                                 ("col", "col", 50), ("slot", "slot", 50),
                                 ("board", "Board S/N", 130), ("chip", "chip", 40),
                                 ("pass", "Result", 80)):
            self._tree.heading(col, text=head)
            self._tree.column(col, width=width, anchor="w")
        self._tree.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        sb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        sb.grid(row=1, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.tag_configure("fail", foreground="#dc2626")

        self.after(500, self._refresh_loop)

    def _refresh_loop(self):
        self._refresh()
        self.after(1000, self._refresh_loop)

    def _refresh(self):
        history = self._recipe.results_history
        if len(history) != self._last_len:
            for row in history[self._last_len:]:
                self._tree.insert("", "end", values=(
                    row.get("die_id", ""), row.get("row", ""), row.get("col", ""),
                    row.get("slot", ""), row.get("board_sn", ""), row.get("chip", ""),
                    "PASS" if row.get("pass") else "FAIL"),
                    tags=() if row.get("pass") else ("fail",))
            self._last_len = len(history)
            n_pass = sum(1 for r in history if r.get("pass"))
            n_fail = len(history) - n_pass
            self._summary_var.set(f"{len(history)} measured — {n_pass} pass, {n_fail} fail")
            folder = self._get_ata_folder()
            if folder:
                self._csv_path_var.set(
                    os.path.join(folder, "ata_nanoz_electroglas_results.csv"))
