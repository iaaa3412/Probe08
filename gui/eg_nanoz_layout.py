"""Electroglas main section for NanoZ mode (see gui/nanoz_mode.py).

Built as its OWN lightweight container rather than a MainLayout variant -
MainLayout's Electroglas tabs (Recipe/Run/Probe Card/PMA Process) assume
self.recipe_panel/self.pin_wiring exist unconditionally in several places
(instrument_panel.py load_ata_folder, _exec2_run_steps_once, etc.), which
none of NanoZ's own workflow needs or produces. Reusing MainLayout would
mean either dragging all of that in unused or auditing/patching a very
large, tightly-coupled file to make those attributes optional throughout -
more risk than benefit for what is otherwise two self-contained tabs.

This mirrors the Accretech NanoZPanel's own relationship to its MainLayout
(gui/nanoz_panel.py only ever reads main_layout.export_path_var) - light,
read-through coupling to the REAL Electroglas MainLayout instance
(controller._by_system["electroglas"]["ui"], always built regardless of
which mode is displayed - see app.py) for the one thing that actually
needs to stay in sync across modes: which ATA folder is active.
"""

import os
import tkinter as tk
from tkinter import ttk

from eg_nanoz_recipe_panel import EgNanozRecipePanel
from eg_nanoz_run_panel import EgNanozRunPanel


class EgNanozMainLayout(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)
        self._build_sidebar(paned)
        self._build_notebook(paned)

    def _eg_ui(self):
        """The real Electroglas MainLayout - always built at startup (see
        app.py __init__) regardless of which mode/system is displayed -
        used purely as the shared ATA-folder/instrument-connect state
        holder, the same way NanoZPanel reads Accretech's MainLayout."""
        return self.controller._by_system["electroglas"]["ui"]

    def get_ata_folder(self):
        return self._eg_ui()._ata_folder

    def log(self, msg):
        self.controller.log(msg)

    # -- sidebar --------------------------------------------------------

    def _build_sidebar(self, paned):
        sidebar = ttk.Frame(paned, width=230, relief="sunken", padding=5)
        paned.add(sidebar, weight=0)
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="NanoZ — Electroglas", font=("Arial", 11, "bold")
                 ).pack(anchor="w", pady=(0, 4))
        self._ata_lbl = ttk.Label(sidebar, text="No ATA folder", foreground="gray",
                                  wraplength=210, justify="left")
        self._ata_lbl.pack(anchor="w", pady=(0, 8))

        ttk.Label(sidebar, text="Prober connection is shared with the normal "
                                "Electroglas Debug > Instruments tab.",
                  foreground="#6b7280", font=("Segoe UI", 8), wraplength=210,
                  justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Button(sidebar, text="↻ Refresh Connections",
                  command=self.controller.init_hardware_eg).pack(fill="x")

        log_frame = ttk.LabelFrame(sidebar, text="Log")
        log_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.log_text = tk.Text(log_frame, bg="#1e1e1e", fg="lime",
                                font=("Consolas", 8), wrap="word",
                                state="disabled", width=24)
        sb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

    def append_log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # -- notebook ---------------------------------------------------------

    def _build_notebook(self, paned):
        nb = ttk.Notebook(paned)
        paned.add(nb, weight=1)

        recipe_tab = ttk.Frame(nb)
        nb.add(recipe_tab, text="Nanoz Recipe")
        recipe_tab.rowconfigure(0, weight=1)
        recipe_tab.columnconfigure(0, weight=1)
        self.recipe_panel = EgNanozRecipePanel(
            recipe_tab, controller=self.controller,
            get_ata_folder=self.get_ata_folder, log_fn=self._log_both)
        self.recipe_panel.grid(row=0, column=0, sticky="nsew")

        run_tab = ttk.Frame(nb)
        nb.add(run_tab, text="Nanoz Run")
        run_tab.rowconfigure(0, weight=1)
        run_tab.columnconfigure(0, weight=1)
        self.run_panel = EgNanozRunPanel(
            run_tab, controller=self.controller,
            recipe_panel=self.recipe_panel, log_fn=self._log_both)
        self.run_panel.grid(row=0, column=0, sticky="nsew")

        self.refresh_ata_folder()

    def _log_both(self, msg):
        self.controller.log(msg)
        self.append_log(msg)

    @property
    def _running(self):
        """Mirrors NanoZPanel._running for app.py's run-in-progress check -
        see nanoz_mode.NanozModeLayout.nanoz_panel."""
        return getattr(self.run_panel, "_running", False)

    def refresh_ata_folder(self):
        folder = self.get_ata_folder()
        if folder:
            self._ata_lbl.config(text=os.path.basename(folder), foreground="#1d4ed8")
        else:
            self._ata_lbl.config(text="No ATA folder", foreground="gray")
        self.recipe_panel.on_ata_folder_loaded()
        self.run_panel.refresh_anchor_choices()
        self.run_panel.refresh_table()

    def on_ata_folder_loaded(self, folder_path):
        """Called by app.py's notify_nanoz_ata_folder_loaded when either
        system's ATA folder changes - only actually relevant when it's
        Electroglas's, since get_ata_folder() always reads that system's
        MainLayout regardless of which folder loaded here."""
        self.refresh_ata_folder()
