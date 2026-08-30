"""Alternate whole-window GUI mode for NanoZ (Nautilus 1x20-shot) work.

Historically NanoZPanel lived as a third top-level tab inside MainLayout,
sitting next to Main/Debug on the Accretech side only. That worked while it
was purely an Accretech feature under active development, but Nautilus
needs to run against Electroglas eventually too, and NanoZ's own workflow
(one shared position window, its own wafer map/recipe handling) doesn't
actually fit as "one more tab" once it has to exist for both systems - it
wants to BE the main window, not share one with the normal Run/Recipe/
Results tab set.

So this module is a second top-level widget AtomicaDashboard can swap into
its _main_pane (see app.py's cmd_set_gui_mode), the same way it already
swaps one MainLayout for another when the operator toggles Accretech <->
Electroglas (cmd_set_active_system). NanozModeLayout itself is system-aware
internally: it shows Accretech's NanoZPanel or an Electroglas placeholder
(no EG NanoZ workflow exists yet) depending on controller.active_system,
and swaps between them in place when the system toggle is used while in
NanoZ mode, without the outer widget object itself changing.

NanoZPanel is built against the ALREADY-EXISTING MainLayout instance for
whichever system it is showing (controller._by_system[system]["ui"]) -
those instances are always constructed at startup regardless of which mode
is displayed (see app.py __init__), so NanoZPanel keeps reading/writing the
same ATA folder state, drivers, etc. it always has; only the container it
is packed into is new.
"""

import tkinter as tk
from tkinter import ttk

from nanoz_panel import NanoZPanel


class NanozModeLayout(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_header()

        self._body = ttk.Frame(self)
        self._body.grid(row=1, column=0, sticky="nsew")
        self._body.columnconfigure(0, weight=1)
        self._body.rowconfigure(0, weight=1)

        # system -> the holder Frame built for it (built lazily, kept
        # around so switching systems back and forth doesn't rebuild the
        # NanoZPanel and lose its board connections/state).
        self._holders = {}
        self._current_system = None
        self.refresh_for_system()

    def _build_header(self):
        bar = tk.Frame(self, bg="#374558", height=36)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        tk.Label(bar, text="NanoZ Mode", bg="#374558", fg="#f0a020",
                 font=("Arial", 11, "bold")).pack(side="left", padx=(10, 4))
        tk.Label(bar, text="— alternate main window, Nautilus 1x20 shots",
                 bg="#374558", fg="#9ca3af", font=("Arial", 9)).pack(side="left")
        tk.Button(bar, text="⬅ Switch to Normal", bd=1, relief="flat",
                  font=("Arial", 9, "bold"), padx=10, pady=2,
                  command=lambda: self.controller.cmd_set_gui_mode("normal")
                  ).pack(side="right", padx=10, pady=6)

    def refresh_for_system(self):
        """Show whichever system is currently active, building its holder
        the first time it's needed. Called on first display and again
        whenever the operator toggles Accretech/Electroglas while already
        in NanoZ mode (see app.py cmd_set_active_system)."""
        system = self.controller.active_system
        holder = self._holders.get(system)
        if holder is None:
            holder = self._build_holder(system)
            self._holders[system] = holder
        if self._current_system is not None and self._current_system != system:
            self._holders[self._current_system].grid_remove()
        holder.grid(row=0, column=0, sticky="nsew")
        self._current_system = system

    def _build_holder(self, system):
        holder = ttk.Frame(self._body)
        holder.columnconfigure(0, weight=1)
        holder.rowconfigure(0, weight=1)
        if system == "accretech":
            main_layout = self.controller._by_system["accretech"]["ui"]
            panel = NanoZPanel(holder, controller=self.controller, main_layout=main_layout)
            panel.grid(row=0, column=0, sticky="nsew")
            holder.nanoz_panel = panel
        else:
            holder.nanoz_panel = None
            msg = ttk.Frame(holder)
            msg.grid(row=0, column=0)
            ttk.Label(
                msg, text="NanoZ for Electroglas isn't built yet.",
                font=("Segoe UI", 12, "bold"), foreground="#374558"
            ).pack(pady=(40, 6))
            ttk.Label(
                msg, justify="center", foreground="#6b7280", wraplength=420,
                text=("This is the placeholder main section for the "
                      "Electroglas side of NanoZ mode - once an Electroglas "
                      "Nautilus workflow exists, it replaces this label the "
                      "same way NanoZPanel does for Accretech.")
            ).pack()
        return holder

    @property
    def nanoz_panel(self):
        """Whichever system's NanoZPanel is currently displayed, or None on
        the Electroglas side (no panel exists yet) - mirrors the attribute
        MainLayout.nanoz_panel used to expose, for the same external
        callers (see app.py's run-in-progress check)."""
        holder = self._holders.get(self._current_system)
        return getattr(holder, "nanoz_panel", None) if holder is not None else None

    def on_ata_folder_loaded(self, folder_path):
        """Forwarded from MainLayout.load_ata_folder (via app.py) so a
        folder reload still reaches whichever NanoZPanel exists, even
        though it is no longer a child of the MainLayout that loaded it.

        Mirrors what MainLayout used to do directly when NanoZPanel was one
        of its own tabs: clear whatever overlay/picks belonged to the
        previous folder before loading the new one's own saved map."""
        panel = self.nanoz_panel
        if panel is None:
            return
        try:
            if hasattr(panel, "_clear_overlay"):
                panel._clear_overlay()
                panel.wafer_map.clear_picks()
                panel._on_sites_changed([])
            panel.on_ata_folder_loaded(folder_path)
        except Exception:
            pass
