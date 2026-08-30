"""Simple live chart of recent SPL sensor current/voltage readings, for the
Electroglas NanoZ Charts tab. A deliberately smaller version of
gui/nanoz_panel.py's own Charts tab - one scrolling window of the last N
samples per connected board/chip rather than that tab's full pan/zoom/
history-browsing system. Subscribes to gui/eg_nanoz_setup_panel.py's
packet stream (EgNanozSetupPanel.subscribe) rather than owning any board
I/O itself.
"""

import collections
import tkinter as tk
from tkinter import ttk

try:
    import matplotlib
    try:
        matplotlib.use("TkAgg")
    except Exception:
        pass
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    _MPL = True
except ImportError:
    _MPL = False

_HISTORY_LEN = 200


class EgNanozChartsPanel(ttk.Frame):
    def __init__(self, parent, setup_panel):
        super().__init__(parent)
        self._setup = setup_panel

        self._history: dict[tuple, dict] = {}  # (sn, chip) -> {field: deque}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        ttk.Label(bar, text="Metric:").pack(side="left")
        self._metric_var = tk.StringVar(value="Current (mA)")
        ttk.Combobox(bar, textvariable=self._metric_var, state="readonly", width=14,
                    values=("Current (mA)", "Voltage (mV)")).pack(side="left", padx=(4, 0))

        if _MPL:
            self._fig = Figure(figsize=(8, 5), dpi=100)
            self._ax = self._fig.add_subplot(111)
            self._canvas = FigureCanvasTkAgg(self._fig, master=self)
            self._canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
            self._draw_empty()
        else:
            ttk.Label(self, text="matplotlib not installed - install it to view charts.",
                     foreground="red").grid(row=1, column=0, sticky="nw", padx=10, pady=10)

        setup_panel.subscribe(self._on_packet)
        if _MPL:
            self.after(500, self._redraw_loop)

    def _draw_empty(self):
        self._ax.clear()
        self._ax.set_title("no data yet", fontsize=9)
        self._canvas.draw_idle()

    def _on_packet(self, item: dict):
        if item.get("kind") != "spl":
            return
        key = (item.get("board_sn"), str(item.get("header_chip")))
        hist = self._history.setdefault(key, {f"s{n}": collections.deque(maxlen=_HISTORY_LEN)
                                               for n in (1, 2, 3, 4)})
        for n in (1, 2, 3, 4):
            field = f"adc_current_ma_s{n}" if self._metric_var.get().startswith("Current") \
                else f"dac_mv_s{n}"
            val = item.get(field)
            if val is not None:
                hist[f"s{n}"].append(val)

    def _redraw_loop(self):
        self._redraw()
        self.after(1000, self._redraw_loop)

    def _redraw(self):
        if not self._history:
            return
        self._ax.clear()
        unit = "mA" if self._metric_var.get().startswith("Current") else "mV"
        for (sn, chip), hist in self._history.items():
            for n in (1, 2, 3, 4):
                data = list(hist[f"s{n}"])
                if data:
                    self._ax.plot(data, label=f"{sn[-6:]} chip{chip} S{n}", linewidth=1)
        self._ax.set_title(f"Sensor readings ({unit}) - last {_HISTORY_LEN} samples", fontsize=9)
        if self._ax.get_legend_handles_labels()[0]:
            self._ax.legend(fontsize=6, ncol=2)
        self._canvas.draw_idle()
