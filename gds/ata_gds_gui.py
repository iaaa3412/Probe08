"""
ATA GDSII GUI Parser
--------------------
Desktop GUI for Phase 1 of the Atomica Test Automation project.

Features:
- Open a GDS/GDSII file from the File menu or button.
- Select the top/device cell from a dropdown.
- Display parsed cells, layers, labels, references, and pad candidates.
- Plot a first-pass device layout preview.
- Plot a first-pass wafer map preview.
- Export ATA-ready CSV/JSON files.
"""

from __future__ import annotations

import json
import os
import threading
import traceback
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional, Sequence

import matplotlib

try:
    matplotlib.use("TkAgg")
except ImportError:
    # A normal Windows desktop Python install can use TkAgg.
    # This fallback only helps automated/headless syntax checks.
    pass
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle

from ata_gds_core import (
    collect_records,
    default_alignment_mark_names,
    default_die_pitch_from_summary,
    discover_layout_metadata,
    export_ata_files,
    generate_wafer_map,
    read_gds_library,
    selected_cell_references,
)


class AtaGdsGui(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Atomica Test Automation GDS2 Parsing Application")
        self.geometry("1400x900")
        self.minsize(1100, 700)

        self.gds_path: Optional[str] = None
        self.library: Any = None
        self.data: Dict[str, Any] = {}
        self.wafer_map: List[Dict[str, Any]] = []
        self.layout_metadata: Dict[str, Any] = {}
        self.layout_metadata_path: str = ""
        self.max_table_rows = 5000
        self.logo_image: Optional[tk.PhotoImage] = None

        self._build_vars()
        self._build_menu()
        self._build_layout()
        self._set_status("Open a GDS/GDSII file to begin.")

    def _build_vars(self) -> None:
        self.top_cell_var = tk.StringVar()
        self.pad_layer_var = tk.StringVar(value="")
        self.pad_datatype_var = tk.StringVar(value="0")
        self.min_pad_size_var = tk.StringVar(value="20")
        self.max_pad_size_var = tk.StringVar(value="500")
        self.flatten_pads_var = tk.BooleanVar(value=True)
        self.wafer_diameter_var = tk.StringVar(value="200")
        self.edge_exclusion_var = tk.StringVar(value="3")
        self.die_pitch_x_var = tk.StringVar(value="")
        self.die_pitch_y_var = tk.StringVar(value="")
        self.use_refs_var = tk.BooleanVar(value=True)
        self.alignment_mark_names_var = tk.StringVar(value=default_alignment_mark_names())
        self.metadata_status_var = tk.StringVar(value="No layout metadata JSON loaded")
        self.status_var = tk.StringVar()

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Open GDS/GDSII File...", command=self.open_gds_file)
        file_menu.add_command(label="Load Layout Metadata JSON...", command=self.load_metadata_file)
        file_menu.add_command(label="Generate ATA Files...", command=self.export_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

    def _build_layout(self) -> None:
        outer = ttk.Frame(self, padding=8)
        outer.pack(fill=tk.BOTH, expand=True)

        self._build_brand_header(outer)

        controls = ttk.LabelFrame(outer, text="GDS Import, ATA Convention Detection, Alignment Mark Detection and ATA Export Settings", padding=8)
        controls.pack(fill=tk.X, side=tk.TOP)

        row1 = ttk.Frame(controls)
        row1.pack(fill=tk.X, pady=2)
        ttk.Button(row1, text="Open GDS File", command=self.open_gds_file).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(row1, text="Load Metadata JSON", command=self.load_metadata_file).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(row1, text="Selected cell:").pack(side=tk.LEFT)
        self.top_cell_combo = ttk.Combobox(row1, textvariable=self.top_cell_var, width=42, state="readonly")
        self.top_cell_combo.pack(side=tk.LEFT, padx=4)
        self.top_cell_combo.bind("<<ComboboxSelected>>", lambda event: self.reparse_current_file())
        ttk.Button(row1, text="Parse / Refresh", command=self.reparse_current_file).pack(side=tk.LEFT, padx=8)
        ttk.Button(row1, text="Generate ATA Files", command=self.export_files).pack(side=tk.LEFT, padx=8)

        row2 = ttk.Frame(controls)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Pad layer:").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.pad_layer_var, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Label(row2, text="Pad datatype:").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.pad_datatype_var, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Label(row2, text="Min pad size um:").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.min_pad_size_var, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Label(row2, text="Max pad size um:").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.max_pad_size_var, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(row2, text="Flatten selected cell for pad extraction", variable=self.flatten_pads_var).pack(side=tk.LEFT, padx=10)

        row3 = ttk.Frame(controls)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Wafer diameter mm:").pack(side=tk.LEFT)
        ttk.Entry(row3, textvariable=self.wafer_diameter_var, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Label(row3, text="Edge exclusion mm:").pack(side=tk.LEFT)
        ttk.Entry(row3, textvariable=self.edge_exclusion_var, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Label(row3, text="Die pitch X um:").pack(side=tk.LEFT)
        ttk.Entry(row3, textvariable=self.die_pitch_x_var, width=10).pack(side=tk.LEFT, padx=4)
        ttk.Label(row3, text="Die pitch Y um:").pack(side=tk.LEFT)
        ttk.Entry(row3, textvariable=self.die_pitch_y_var, width=10).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(row3, text="Use GDS references as device locations when available", variable=self.use_refs_var).pack(side=tk.LEFT, padx=10)
        ttk.Button(row3, text="Update Wafer Map", command=self.update_wafer_map_and_plots).pack(side=tk.LEFT, padx=8)

        row4 = ttk.Frame(controls)
        row4.pack(fill=tk.X, pady=2)
        ttk.Label(row4, text="Alignment mark cell/text names:").pack(side=tk.LEFT)
        ttk.Entry(row4, textvariable=self.alignment_mark_names_var, width=44).pack(side=tk.LEFT, padx=4)
        ttk.Label(row4, text="Example: ATA_ALIGN_*, KS_LYR4, KS_Neg_LYR2").pack(side=tk.LEFT, padx=8)

        row5 = ttk.Frame(controls)
        row5.pack(fill=tk.X, pady=2)
        ttk.Label(row5, text="Layout metadata:").pack(side=tk.LEFT)
        ttk.Label(row5, textvariable=self.metadata_status_var).pack(side=tk.LEFT, padx=4)

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(8, 4))

        self.summary_text = self._make_text_tab("Summary")
        self.cells_tree = self._make_tree_tab("Cells")
        self.layers_tree = self._make_tree_tab("Layers")
        self.references_tree = self._make_tree_tab("References")
        self.labels_tree = self._make_tree_tab("Labels")
        self.polygons_tree = self._make_tree_tab("Polygons")
        self.pads_tree = self._make_tree_tab("Pads")
        self.alignment_tree = self._make_tree_tab("Alignment Marks")
        self.ata_alignment_tree = self._make_tree_tab("ATA Alignment Marks")
        self.ata_metadata_tree = self._make_tree_tab("ATA Metadata")
        self.ata_validation_tree = self._make_tree_tab("ATA QA Report")
        self.ata_devices_tree = self._make_tree_tab("ATA Devices/Tests")
        self.ata_channel_tree = self._make_tree_tab("ATA Channel Map")
        self.layout_metadata_tree = self._make_tree_tab("Layout Metadata")
        self.pad_layout_tree = self._make_tree_tab("ATA Pad Layout")
        self.wafer_tree = self._make_tree_tab("ATA Wafer Map")
        self.device_fig, self.device_ax, self.device_canvas = self._make_plot_tab("Device Layout Preview")
        self.wafer_fig, self.wafer_ax, self.wafer_canvas = self._make_plot_tab("Wafer Map Preview")
        self.log_text = self._make_text_tab("Export Log")

        status = ttk.Label(outer, textvariable=self.status_var, anchor=tk.W)
        status.pack(fill=tk.X, side=tk.BOTTOM)

    def _build_brand_header(self, parent: ttk.Frame) -> None:
        header = tk.Frame(parent, bg="black", padx=10, pady=6)
        header.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "atomica_logo.png")
        try:
            self.logo_image = tk.PhotoImage(file=logo_path)
            tk.Label(header, image=self.logo_image, bg="black").pack(side=tk.LEFT, padx=(0, 18))
        except Exception:
            self.logo_image = None
            tk.Label(header, text="ATOMICA", bg="black", fg="#ff9700", font=("Segoe UI", 22, "bold")).pack(side=tk.LEFT, padx=(0, 18))

        title_frame = tk.Frame(header, bg="black")
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            title_frame,
            text="Atomica Test Automation",
            bg="black",
            fg="white",
            font=("Segoe UI", 18, "bold"),
            anchor="w",
        ).pack(fill=tk.X)
        tk.Label(
            title_frame,
            text="GDS2 Parsing Application",
            bg="black",
            fg="#ff9700",
            font=("Segoe UI", 13),
            anchor="w",
        ).pack(fill=tk.X)

    def _make_text_tab(self, title: str) -> tk.Text:
        frame = ttk.Frame(self.notebook)
        text = tk.Text(frame, wrap=tk.WORD, height=10)
        yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=yscroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.notebook.add(frame, text=title)
        return text

    def _make_tree_tab(self, title: str) -> ttk.Treeview:
        frame = ttk.Frame(self.notebook)
        tree = ttk.Treeview(frame, show="headings")
        yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        xscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.notebook.add(frame, text=title)
        return tree

    def _make_plot_tab(self, title: str):
        frame = ttk.Frame(self.notebook)
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        toolbar = NavigationToolbar2Tk(canvas, frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.notebook.add(frame, text=title)
        return fig, ax, canvas

    def open_gds_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Open GDS/GDSII File",
            filetypes=[
                ("GDSII files", "*.gds *.gdsii"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        self.gds_path = path
        self._set_status(f"Loading {os.path.basename(path)} ...")
        self._run_threaded(self._load_library_worker)

    def _run_threaded(self, worker) -> None:
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _load_library_worker(self) -> None:
        try:
            assert self.gds_path is not None
            lib = read_gds_library(self.gds_path)
            self.library = lib
            metadata, metadata_path = discover_layout_metadata(self.gds_path)
            # First parse to get top-cell list and apply any sidecar metadata.
            data = collect_records(
                lib,
                alignment_mark_names=self.alignment_mark_names_var.get(),
                layout_metadata=metadata,
                metadata_path=metadata_path,
            )
            self.after(0, lambda: self._after_library_loaded(data, metadata, metadata_path))
        except Exception as exc:
            tb = traceback.format_exc()
            self.after(0, lambda err=exc, trace=tb: self._show_error("Could not load GDSII file", err, trace))

    def _after_library_loaded(self, data: Dict[str, Any], metadata: Dict[str, Any], metadata_path: str) -> None:
        self.layout_metadata = metadata or {}
        self.layout_metadata_path = metadata_path or ""
        self._apply_metadata_to_gui()
        top_names = data.get("top_cell_names", [])
        self.top_cell_combo.configure(values=top_names)
        if top_names:
            self.top_cell_var.set(data.get("selected_cell_name", top_names[0]))
        self._set_status("GDS file loaded. Parsing selected cell...")
        self.reparse_current_file()

    def reparse_current_file(self) -> None:
        if self.library is None:
            messagebox.showinfo("No GDS file", "Open a GDS/GDSII file first.")
            return
        self._set_status("Parsing GDS data...")
        self._run_threaded(self._parse_worker)

    def _parse_worker(self) -> None:
        try:
            data = collect_records(
                self.library,
                selected_cell_name=self.top_cell_var.get() or None,
                pad_layer=self._optional_int(self.pad_layer_var.get()),
                pad_datatype=self._optional_int(self.pad_datatype_var.get()),
                min_pad_size_um=self._float_or_default(self.min_pad_size_var.get(), 0.0),
                max_pad_size_um=self._float_or_default(self.max_pad_size_var.get(), 1e12),
                flatten_selected_for_pads=self.flatten_pads_var.get(),
                alignment_mark_names=self.alignment_mark_names_var.get(),
                layout_metadata=self.layout_metadata,
                metadata_path=self.layout_metadata_path,
            )
            self.after(0, lambda: self._after_parse(data))
        except Exception as exc:
            tb = traceback.format_exc()
            self.after(0, lambda err=exc, trace=tb: self._show_error("Could not parse GDSII file", err, trace))

    def _after_parse(self, data: Dict[str, Any]) -> None:
        self.data = data
        # If die pitch entries are blank, fill from selected cell bounding box.
        pitch_x, pitch_y = default_die_pitch_from_summary(data)
        if not self.die_pitch_x_var.get().strip() and pitch_x > 0:
            self.die_pitch_x_var.set(f"{pitch_x:.3f}")
        if not self.die_pitch_y_var.get().strip() and pitch_y > 0:
            self.die_pitch_y_var.set(f"{pitch_y:.3f}")
        self.update_wafer_map_and_plots()
        self._populate_all_views()
        summary = data.get("summary", {})
        self._set_status(
            f"Parsed {summary.get('cell_count', 0)} cells, {summary.get('layer_count', 0)} layers, "
            f"{summary.get('pad_count', 0)} pad candidates."
        )

    def update_wafer_map_and_plots(self) -> None:
        if not self.data:
            return
        summary = self.data.get("summary", {})
        refs = selected_cell_references(self.data)
        self.wafer_map = generate_wafer_map(
            selected_cell_bbox=summary.get("selected_cell_bbox"),
            selected_cell_references=refs,
            wafer_diameter_mm=self._float_or_default(self.wafer_diameter_var.get(), 200.0),
            edge_exclusion_mm=self._float_or_default(self.edge_exclusion_var.get(), 3.0),
            die_pitch_x_um=self._float_or_default(self.die_pitch_x_var.get(), 0.0),
            die_pitch_y_um=self._float_or_default(self.die_pitch_y_var.get(), 0.0),
            use_references_if_available=self.use_refs_var.get(),
        )
        self._load_tree(self.wafer_tree, self.wafer_map)
        self._plot_device_layout()
        self._plot_wafer_map()
        self._set_status(f"Wafer map updated with {len(self.wafer_map)} device locations.")

    def _populate_all_views(self) -> None:
        if not self.data:
            return
        self._populate_summary()
        self._load_tree(self.cells_tree, self.data.get("cells", []))
        self._load_tree(self.layers_tree, self.data.get("layers", []))
        self._load_tree(self.references_tree, self.data.get("references", []))
        self._load_tree(self.labels_tree, self.data.get("labels", []))
        self._load_tree(self.polygons_tree, self.data.get("polygons", []))
        self._load_tree(self.pads_tree, self.data.get("pads", []))
        self._load_tree(self.alignment_tree, self.data.get("alignment_marks", []))
        self._load_tree(self.ata_alignment_tree, self.data.get("ata_alignment_marks", []))
        self._load_tree(self.ata_metadata_tree, self.data.get("ata_metadata", []))
        self._load_tree(self.ata_validation_tree, self.data.get("ata_validation_report", []))
        device_test_records = list(self.data.get("ata_devices", [])) + list(self.data.get("ata_test_structures", []))
        self._load_tree(self.ata_devices_tree, device_test_records)
        self._load_tree(self.ata_channel_tree, self.data.get("ata_channel_map", []))
        self._load_tree(self.layout_metadata_tree, self.data.get("layout_metadata", []))
        self._load_tree(self.pad_layout_tree, self.data.get("ata_pad_layout", []))
        self._load_tree(self.wafer_tree, self.wafer_map)

    def _populate_summary(self) -> None:
        self.summary_text.delete("1.0", tk.END)
        summary = self.data.get("summary", {})
        source = self.gds_path or ""
        lines = [
            "ATA Phase 1 GDSII Parse Summary",
            "================================",
            "",
            f"Source file: {source}",
            f"Parsed at: {datetime.now().isoformat(timespec='seconds')}",
            f"Selected cell: {self.data.get('selected_cell_name', '')}",
            f"GDS unit: {summary.get('unit', '')}",
            f"GDS precision: {summary.get('precision', '')}",
            "",
            f"Cells: {summary.get('cell_count', 0)}",
            f"Top cells: {', '.join(summary.get('top_cells', []))}",
            f"Layers: {summary.get('layer_count', 0)}",
            f"Polygons: {summary.get('polygon_count', 0)}",
            f"Labels: {summary.get('label_count', 0)}",
            f"References: {summary.get('reference_count', 0)}",
            f"Pad candidates: {summary.get('pad_count', 0)}",
            f"Alignment marks found: {summary.get('alignment_mark_count', 0)}",
            f"Alignment mark search names: {', '.join(summary.get('alignment_mark_search_names', []))}",
            f"ATA metadata records: {summary.get('ata_metadata_count', 0)}",
            f"ATA device labels: {summary.get('ata_device_count', 0)}",
            f"ATA test structure labels: {summary.get('ata_test_structure_count', 0)}",
            f"Layout metadata JSON loaded: {summary.get('layout_metadata_loaded', False)}",
            f"Layout metadata path: {summary.get('layout_metadata_path', '')}",
            f"Wafer map device locations: {len(self.wafer_map)}",
            "",
            "Important:",
            "- GDSII usually gives die/device layout geometry, not a complete production wafer test plan.",
            "- Verify that the coordinates are in microns before using them with the prober.",
            "- If the layout follows the ATA manual, ATA_* labels/cells are detected automatically.",
            "- Enter the actual pad layer/datatype for useful pad extraction, or provide these in the sidecar metadata JSON.",
            "- Review the ATA QA Report tab before sending files into the next ATA phase.",
            "- The exported ATA files are Phase 1 layout inputs; instrument/channel mapping still needs to be assigned.",
        ]
        self.summary_text.insert(tk.END, "\n".join(lines))

    def _load_tree(self, tree: ttk.Treeview, records: Sequence[Dict[str, Any]]) -> None:
        tree.delete(*tree.get_children())
        tree["columns"] = []
        if not records:
            tree["columns"] = ["message"]
            tree.heading("message", text="message")
            tree.column("message", width=500, anchor=tk.W)
            tree.insert("", tk.END, values=["No records to display."])
            return

        columns: List[str] = []
        for rec in records[: min(len(records), self.max_table_rows)]:
            for key in rec.keys():
                if key not in columns:
                    columns.append(key)
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=max(90, min(220, len(col) * 10)), anchor=tk.W)
        for rec in records[: self.max_table_rows]:
            tree.insert("", tk.END, values=[self._format_cell_value(rec.get(col, "")) for col in columns])
        if len(records) > self.max_table_rows:
            tree.insert("", tk.END, values=[f"Only showing first {self.max_table_rows} of {len(records)} rows"] + [""] * (len(columns) - 1))

    def _plot_device_layout(self) -> None:
        self.device_ax.clear()
        if not self.data:
            self.device_ax.set_title("No GDS data loaded")
            self.device_canvas.draw_idle()
            return

        selected = self.data.get("selected_cell_name", "")
        polygons = [p for p in self.data.get("polygons", []) if p.get("cell") == selected]
        refs = [r for r in self.data.get("references", []) if r.get("parent_cell") == selected]
        pads = self.data.get("pads", [])
        alignment_marks = self.data.get("alignment_marks", [])

        # Draw direct polygons by bounding box. This keeps preview fast for large files.
        drawn = 0
        for poly in polygons[:10000]:
            try:
                x = float(poly.get("bbox_min_x_um", 0))
                y = float(poly.get("bbox_min_y_um", 0))
                w = float(poly.get("bbox_width_um", 0))
                h = float(poly.get("bbox_height_um", 0))
                if w == 0 or h == 0:
                    continue
                self.device_ax.add_patch(Rectangle((x, y), w, h, fill=False, linewidth=0.4, alpha=0.5))
                drawn += 1
            except Exception:
                continue

        # Draw references as larger dashed boxes if the selected cell is mostly hierarchical.
        for ref in refs[:2000]:
            try:
                x = float(ref.get("bbox_min_x_um", ref.get("origin_x_um", 0)))
                y = float(ref.get("bbox_min_y_um", ref.get("origin_y_um", 0)))
                w = float(ref.get("bbox_width_um", 0))
                h = float(ref.get("bbox_height_um", 0))
                if w == 0 or h == 0:
                    self.device_ax.plot(float(ref.get("origin_x_um", 0)), float(ref.get("origin_y_um", 0)), marker=".")
                else:
                    self.device_ax.add_patch(Rectangle((x, y), w, h, fill=False, linestyle="--", linewidth=0.8))
            except Exception:
                continue

        for pad in pads[:2000]:
            try:
                x = float(pad.get("bbox_min_x_um", 0))
                y = float(pad.get("bbox_min_y_um", 0))
                w = float(pad.get("bbox_width_um", 0))
                h = float(pad.get("bbox_height_um", 0))
                self.device_ax.add_patch(Rectangle((x, y), w, h, fill=False, linewidth=1.2))
                self.device_ax.text(float(pad.get("x_um", x)), float(pad.get("y_um", y)), str(pad.get("pad_name", "")), fontsize=6)
            except Exception:
                continue

        for mark in alignment_marks[:200]:
            try:
                x = float(mark.get("x_um", 0))
                y = float(mark.get("y_um", 0))
                self.device_ax.plot(x, y, marker="x", markersize=10)
                self.device_ax.text(x, y, str(mark.get("mark_name", "ALIGN")), fontsize=8)
            except Exception:
                continue

        # Draw key ATA convention anchors.
        for rec in self.data.get("ata_metadata", [])[:500]:
            if rec.get("record_class") in {"die_origin", "wafer_origin", "reticle_origin", "device", "test_structure", "probe_site", "nanoz_channel"}:
                try:
                    x = float(rec.get("x_um", 0))
                    y = float(rec.get("y_um", 0))
                    self.device_ax.plot(x, y, marker="+")
                    self.device_ax.text(x, y, str(rec.get("name", "ATA")), fontsize=6)
                except Exception:
                    continue

        self.device_ax.set_title(f"Device Layout Preview: {selected}")
        self.device_ax.set_xlabel("X (GDS user units, usually um)")
        self.device_ax.set_ylabel("Y (GDS user units, usually um)")
        self.device_ax.axis("equal")
        self.device_ax.autoscale_view()
        self.device_fig.tight_layout()
        self.device_canvas.draw_idle()

    def _plot_wafer_map(self) -> None:
        self.wafer_ax.clear()
        if not self.wafer_map:
            self.wafer_ax.set_title("No wafer map generated")
            self.wafer_canvas.draw_idle()
            return

        xs = []
        ys = []
        for row in self.wafer_map:
            try:
                xs.append(float(row.get("x_um", 0)))
                ys.append(float(row.get("y_um", 0)))
            except Exception:
                pass
        if xs and ys:
            self.wafer_ax.scatter(xs, ys, s=8)

        wafer_radius_um = self._float_or_default(self.wafer_diameter_var.get(), 200.0) * 1000.0 / 2.0
        edge_radius_um = max(0.0, wafer_radius_um - self._float_or_default(self.edge_exclusion_var.get(), 3.0) * 1000.0)
        self.wafer_ax.add_patch(Circle((0, 0), wafer_radius_um, fill=False, linewidth=1.0))
        self.wafer_ax.add_patch(Circle((0, 0), edge_radius_um, fill=False, linestyle="--", linewidth=0.8))
        self.wafer_ax.set_title(f"ATA Wafer Map Preview: {len(self.wafer_map)} locations")
        self.wafer_ax.set_xlabel("Wafer X um")
        self.wafer_ax.set_ylabel("Wafer Y um")
        self.wafer_ax.axis("equal")
        self.wafer_ax.autoscale_view()
        self.wafer_fig.tight_layout()
        self.wafer_canvas.draw_idle()

    def export_files(self) -> None:
        if not self.data:
            messagebox.showinfo("No parsed data", "Open and parse a GDS/GDSII file first.")
            return
        base_name = "ata_gds_export"
        if self.gds_path:
            base_name = os.path.splitext(os.path.basename(self.gds_path))[0] + "_ata_export"
        initial_dir = os.path.dirname(self.gds_path) if self.gds_path else os.getcwd()
        target = filedialog.askdirectory(title="Choose Export Folder", initialdir=initial_dir)
        if not target:
            return
        output_dir = os.path.join(target, base_name)
        try:
            files = export_ata_files(self.data, output_dir, self.wafer_map, source_file=self.gds_path or "")
            self._append_log("Generated ATA files:\n" + "\n".join(f"- {k}: {v}" for k, v in files.items()) + "\n")
            self._set_status(f"ATA files generated in {output_dir}")
            messagebox.showinfo("ATA files generated", f"Files generated in:\n\n{output_dir}")
        except Exception as exc:
            self._show_error("Could not export ATA files", exc, traceback.format_exc())


    def load_metadata_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Open ATA Layout Metadata JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.layout_metadata = json.load(f)
            self.layout_metadata_path = path
            self._apply_metadata_to_gui(force=True)
            self._append_log(f"Loaded layout metadata JSON: {path}\n")
            self.reparse_current_file()
        except Exception as exc:
            self._show_error("Could not load layout metadata JSON", exc, traceback.format_exc())

    def _apply_metadata_to_gui(self, force: bool = False) -> None:
        metadata = self.layout_metadata or {}
        if self.layout_metadata_path:
            self.metadata_status_var.set(self.layout_metadata_path)
        else:
            self.metadata_status_var.set("No layout metadata JSON loaded")
        if not metadata:
            return

        def set_if_available(var: tk.StringVar, *keys: str) -> None:
            value = self._metadata_value(metadata, *keys)
            if value is not None and (force or not var.get().strip()):
                var.set(str(value))

        set_if_available(self.wafer_diameter_var, "wafer_diameter_mm")
        set_if_available(self.edge_exclusion_var, "edge_exclusion_mm")
        set_if_available(self.die_pitch_x_var, "die_pitch_x_um")
        set_if_available(self.die_pitch_y_var, "die_pitch_y_um")
        set_if_available(self.pad_layer_var, "pad_layer", "probe_pad_layer")
        set_if_available(self.pad_datatype_var, "pad_datatype", "probe_pad_datatype")

        align_names = self._metadata_value(metadata, "alignment_mark_names", "alignment_marks")
        if align_names is not None and (force or self.alignment_mark_names_var.get().strip() == default_alignment_mark_names()):
            if isinstance(align_names, list):
                self.alignment_mark_names_var.set(", ".join(str(v) for v in align_names))
            else:
                self.alignment_mark_names_var.set(str(align_names))

    @staticmethod
    def _metadata_value(metadata: Dict[str, Any], *keys: str) -> Any:
        if not metadata:
            return None
        for key in keys:
            if key in metadata:
                return metadata[key]
        for section in ("wafer", "die", "layers", "probe", "ata", "layout"):
            sub = metadata.get(section)
            if isinstance(sub, dict):
                for key in keys:
                    if key in sub:
                        return sub[key]
        return None

    def show_about(self) -> None:
        messagebox.showinfo(
            "About Atomica Test Automation GDS2 Parsing Application",
            "Atomica Test Automation GDS2 Parsing Application\n\n"
            "This Phase 1 utility extracts layout data, ATA_* convention records, pad candidates, alignment mark positions and sidecar metadata from GDSII files. It generates first-pass ATA CSV/JSON inputs and a QA report.\n\n"
            "It is intended for layout import and planning, not final prober control.",
        )

    def _append_log(self, text: str) -> None:
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.update_idletasks()

    def _show_error(self, title: str, exc: Exception, traceback_text: str = "") -> None:
        self._set_status(f"ERROR: {exc}")
        self._append_log(f"{title}: {exc}\n{traceback_text}\n")
        messagebox.showerror(title, f"{exc}\n\nSee the Export Log tab for details.")

    @staticmethod
    def _optional_int(value: str) -> Optional[int]:
        value = value.strip()
        if value == "":
            return None
        return int(value)

    @staticmethod
    def _float_or_default(value: str, default: float) -> float:
        try:
            if value is None or str(value).strip() == "":
                return default
            return float(value)
        except Exception:
            return default

    @staticmethod
    def _format_cell_value(value: Any) -> str:
        if isinstance(value, float):
            return f"{value:.6g}"
        return str(value)


def main() -> None:
    app = AtaGdsGui()
    app.mainloop()


if __name__ == "__main__":
    main()
