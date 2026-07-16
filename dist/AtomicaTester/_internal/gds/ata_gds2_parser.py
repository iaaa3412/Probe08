
from __future__ import annotations

import argparse
import json
import os

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Atomica Test Automation Phase 1 GDSII parser/exporter")
    parser.add_argument("gds_file", help="Input .gds or .gdsii file")
    parser.add_argument("--out", default="gds_results", help="Output folder")
    parser.add_argument("--top-cell", default=None, help="Selected top/device cell name")
    parser.add_argument("--pad-layer", type=int, default=None, help="GDS layer used for probe pads")
    parser.add_argument("--pad-datatype", type=int, default=0, help="GDS datatype used for probe pads")
    parser.add_argument("--min-pad-size", type=float, default=20.0, help="Minimum pad bbox dimension in um")
    parser.add_argument("--max-pad-size", type=float, default=500.0, help="Maximum pad bbox dimension in um")
    parser.add_argument("--no-flatten", action="store_true", help="Do not flatten selected cell for pad extraction")
    parser.add_argument("--wafer-diameter-mm", type=float, default=200.0)
    parser.add_argument("--edge-exclusion-mm", type=float, default=3.0)
    parser.add_argument("--die-pitch-x-um", type=float, default=None)
    parser.add_argument("--die-pitch-y-um", type=float, default=None)
    parser.add_argument("--ignore-gds-references", action="store_true", help="Generate circular wafer grid even if references exist")
    parser.add_argument("--alignment-mark-names", default=default_alignment_mark_names(), help="Comma-separated GDS cell/text names/patterns used for alignment marks")
    parser.add_argument("--metadata-json", default=None, help="Optional ATA layout metadata sidecar JSON file")
    args = parser.parse_args()

    lib = read_gds_library(args.gds_file)
    if args.metadata_json:
        with open(args.metadata_json, "r", encoding="utf-8") as f:
            layout_metadata = json.load(f)
        metadata_path = os.path.abspath(args.metadata_json)
    else:
        layout_metadata, metadata_path = discover_layout_metadata(args.gds_file)
    data = collect_records(
        lib,
        selected_cell_name=args.top_cell,
        pad_layer=args.pad_layer,
        pad_datatype=args.pad_datatype,
        min_pad_size_um=args.min_pad_size,
        max_pad_size_um=args.max_pad_size,
        flatten_selected_for_pads=not args.no_flatten,
        alignment_mark_names=args.alignment_mark_names,
        layout_metadata=layout_metadata,
        metadata_path=metadata_path,
    )
    pitch_x, pitch_y = default_die_pitch_from_summary(data)
    wafer_map = generate_wafer_map(
        selected_cell_bbox=data.get("summary", {}).get("selected_cell_bbox"),
        selected_cell_references=selected_cell_references(data),
        wafer_diameter_mm=args.wafer_diameter_mm,
        edge_exclusion_mm=args.edge_exclusion_mm,
        die_pitch_x_um=args.die_pitch_x_um or pitch_x,
        die_pitch_y_um=args.die_pitch_y_um or pitch_y,
        use_references_if_available=not args.ignore_gds_references,
    )
    files = export_ata_files(data, args.out, wafer_map, source_file=os.path.abspath(args.gds_file))

    print("ATA GDSII export complete:")
    for name, path in files.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
