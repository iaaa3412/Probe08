import csv
import os


WAFER_FIELDS = (
    "CountMovesMajor", "DeviceIDMajor", "MovesMajor",
    "CountMovesMinor", "DeviceIDMinor", "MovesMinor",
    "DieSizeX", "DieSizeY",
    "XMoveFirstFromAlignSite", "YMoveFirstFromAlignSite",
    "PreAlignMessage", "PostAlignMessage", "PictureFile",
)

ELECTRICAL_FIELDS = (
    "Voltage", "Delay1", "Delay2", "Delay3", "Iterations",
    "MeterDelay", "Averages", "NPLC", "MeterCurrentLimit", "MeterRange",
)

# A SECOND, SEPARATE measurement style, used by the recipes that drive an
# external DMM instead of the SMU. "ExternalDMM2Function" is not a made-up
# name - its values are the HP 3458A's own function commands (OHM = 2-wire
# ohms, OHMF = 4-wire), and ExternalDMM2Range values seen in real recipes
# (1000, 1000000) are exact members of the 3458A's ohms range list. So this
# group means: put the 3458A in this function on this range and read it.
#
# The two styles are mutually exclusive in every recipe seen so far - a file
# has ELECTRICAL_FIELDS (SMU, sourced volts, measured current) or
# EXTERNAL_DMM_FIELDS (3458A, resistance), never both.
EXTERNAL_DMM_FIELDS = (
    "ExternalDMM2Function", "ExternalDMM2Range", "ExternalDMM2NPLC",
    "ShortWait",
)

MISC_FIELDS = ("IsPicture",)

ALL_FIELDS = WAFER_FIELDS + ELECTRICAL_FIELDS + EXTERNAL_DMM_FIELDS + MISC_FIELDS

# 3458A function -> how many probe pins the measurement needs.
DMM_FUNCTION_WIRES = {"OHM": 2, "OHMF": 4}

_CSV_FIELDS = ("seq", "major_index", "minor_index", "device_id", "x", "y")


def parse_pma_file(path: str) -> dict:
    fields = {}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(("#", ";", "[")) or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            if key:
                fields[key] = val.strip()
    return fields


def _resolve_local(pma_path: str, ref_value: str) -> str:
    base = ref_value.replace("\\", "/").rsplit("/", 1)[-1]
    return os.path.join(os.path.dirname(os.path.abspath(pma_path)), base)


def _device_id_path(pma_path: str, fields: dict, key: str) -> str:
    ref = fields.get(key, "")
    return _resolve_local(pma_path, ref) if ref else ""


def _moves_path(pma_path: str, fields: dict, key: str, axis: str) -> str:
    ref = fields.get(key, "")
    if not ref:
        return ""
    return f"{_resolve_local(pma_path, ref)}{axis}.PMV"


def sibling_file_paths(pma_path: str, fields: dict) -> list:
    paths = []
    for key, axis in (("MovesMajor", "X"), ("MovesMajor", "Y"),
                      ("MovesMinor", "X"), ("MovesMinor", "Y")):
        p = _moves_path(pma_path, fields, key, axis)
        if p:
            paths.append(p)
    for key in ("DeviceIDMajor", "DeviceIDMinor"):
        p = _device_id_path(pma_path, fields, key)
        if p:
            paths.append(p)
    return paths


def _read_numbers(path: str) -> list:
    if not path or not os.path.isfile(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(float(line))
            except ValueError:
                pass
    return out


def _read_strings(path: str) -> list:
    if not path or not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return [line.strip() for line in fh if line.strip()]


def split_quad_devices(device_id: str) -> list:
    """Split a slash-joined device ID into the dies of one touchdown.

    LaMP-era recipes probe a 2x2 quad per touchdown - 4 dies contacted at once
    through 8 probe-card pins - and record all four in a single .PMS line:

        93-01/83-71/93-02/83-72
        NA/86-14/NA/NA
        TARGET/41-71/TARGET/41-72

    'NA' marks a position with no die; 'TARGET' marks an alignment target
    rather than a device. Recipes that probe one die per touchdown have no
    slashes and come back as a single-element list.
    """
    parts = [p.strip() for p in str(device_id).split("/")]
    return parts if len(parts) > 1 else [str(device_id).strip()]


# Where each slash-separated die physically sits inside a 2x2 touchdown.
# Confirmed on a real LaMP align site, 54-00/44-70/54-01/44-71:
#
#           <- x ->                 index 0  54-00   top left
#     +---------+---------+         index 1  44-70   bottom left
#   ^ |  54-00  |  54-01  |         index 2  54-01   top right
#   y |  [0] TL |  [2] TR |         index 3  44-71   bottom right
#     +---------+---------+
#     |  44-70  |  44-71  |    i.e. COLUMN-major: down the left column
#     |  [1] BL |  [3] BR |    first, then down the right. NOT reading
#     +---------+---------+    order, which would give 54-00/54-01/...
#
# "top"/"left" here are MAP terms: the map frame runs +x right and +y DOWN
# from the top-left origin, so TL is the low-y pair. On the stage itself +y is
# up (MD +1 y moves up) - the two frames disagree on y, and map_to_prober_um()
# is the only place that crosses between them.
QUAD_ORDER = ("TL", "BL", "TR", "BR")
QUAD_LABELS = {"TL": "top left", "TR": "top right",
               "BL": "bottom left", "BR": "bottom right"}
# (col, row) with col 0 = left, row 0 = top.
QUAD_GRID = {"TL": (0, 0), "TR": (1, 0), "BL": (0, 1), "BR": (1, 1)}


def quad_positions(device_id: str) -> list:
    """Pair each die of a touchdown with its physical corner.

    Returns [{"index", "pos", "label", "device", "col", "row", "present"}, ...]
    in the recipe's own slash order. Any touchdown that is not four-up is
    returned with pos=None - a single-die recipe has no corners to assign,
    and guessing would be worse than saying nothing.
    """
    dies = split_quad_devices(device_id)
    out = []
    for i, die in enumerate(dies):
        pos = QUAD_ORDER[i] if len(dies) == len(QUAD_ORDER) else None
        col, row = QUAD_GRID[pos] if pos else (None, None)
        out.append({
            "index": i, "pos": pos, "label": QUAD_LABELS.get(pos, ""),
            "device": die, "col": col, "row": row,
            "present": die.strip().upper() not in ("NA", "TARGET", ""),
        })
    return out


def quad_die_offsets(die_size_x: float, die_size_y: float) -> dict:
    """Micron offset from a touchdown's own coordinate to each die's corner.

    DieSizeX/Y in a .PMA is the quad PITCH - twice the physical die - so the
    four dies tile it in half-pitch steps. The touchdown coordinate is the
    quad's top-left corner in MAP terms (+x right, +y down from the top-left
    origin), which is how the wafer map has always drawn the shot rectangle,
    so the offsets are all zero-or-positive.

    This is the map frame, NOT the prober frame - on the stage +y is up. Only
    map_to_prober_um() crosses between the two.
    """
    hx, hy = float(die_size_x) / 2.0, float(die_size_y) / 2.0
    return {pos: (col * hx, row * hy) for pos, (col, row) in QUAD_GRID.items()}


def format_quad(device_id: str) -> str:
    """One-line 'TL:54-00  TR:54-01  BL:44-70  BR:44-71' for the UI.

    Reordered into reading order so it matches what you see down a scope,
    rather than the recipe's column-major storage order.
    """
    entries = quad_positions(device_id)
    if len(entries) == 1:
        return entries[0]["device"]
    if not entries or entries[0]["pos"] is None:
        return "   ".join(f"{e['index'] + 1}:{e['device']}" for e in entries)
    by_pos = {e["pos"]: e["device"] for e in entries}
    return "   ".join(f"{p}:{by_pos[p]}" for p in ("TL", "TR", "BL", "BR"))


def load_touchdowns(pma_path: str, fields: dict) -> list:
    """Read a .PMA plus its move/device sibling files into touchdown records.

    UNITS ARE MICRONS. Verified against a real recipe: DieSizeX=7042 with a
    measured die of 3.521mm means the .PMA's "die size" is the 2x2 QUAD pitch,
    twice the physical die, and every move coordinate in the .PMV files is an
    exact integer multiple of it.

    Coordinates are absolute from the TOP-LEFT of the wafer grid, which the
    original LaMP exe treated as its own 0,0. They are NOT measured from the
    align site, and XMoveFirstFromAlignSite/Y... is the align site -> that
    top-left origin, not align site -> first touchdown. See align_site_info().

    The prober itself stores none of this - the PC holds the map and drives the
    stage to each coordinate in turn (MA, absolute move in microns).
    """
    major_x = _read_numbers(_moves_path(pma_path, fields, "MovesMajor", "X"))
    major_y = _read_numbers(_moves_path(pma_path, fields, "MovesMajor", "Y"))
    major_id = _read_strings(_device_id_path(pma_path, fields, "DeviceIDMajor"))
    minor_x = _read_numbers(_moves_path(pma_path, fields, "MovesMinor", "X"))
    minor_y = _read_numbers(_moves_path(pma_path, fields, "MovesMinor", "Y"))
    minor_id = _read_strings(_device_id_path(pma_path, fields, "DeviceIDMinor"))

    n_major = min(len(major_x), len(major_y))
    n_minor = min(len(minor_x), len(minor_y)) if minor_x and minor_y else 1

    touchdowns = []
    seq = 1
    for i in range(n_major):
        device_id_major = major_id[i] if i < len(major_id) else str(i + 1)
        for j in range(n_minor):
            mx = minor_x[j] if j < len(minor_x) else 0.0
            my = minor_y[j] if j < len(minor_y) else 0.0
            device_id = device_id_major
            if n_minor > 1:
                mid = minor_id[j] if j < len(minor_id) else str(j + 1)
                device_id = f"{device_id_major}.{mid}"
            touchdowns.append({
                "seq": seq,
                "major_index": i + 1,
                "minor_index": j + 1,
                "device_id": device_id,
                "device_id_major": device_id_major,
                # One entry per die in the touchdown - 4 for a LaMP 2x2 quad,
                # 1 for a single-die recipe. Keeps the raw string intact above
                # rather than replacing it, so existing callers are unaffected.
                "devices": split_quad_devices(device_id),
                "x": major_x[i] + mx,
                "y": major_y[i] + my,
                "major_x": major_x[i],
                "major_y": major_y[i],
            })
            seq += 1
    return touchdowns


def fmt_num(v) -> str:
    return str(int(v)) if float(v).is_integer() else str(v)


def align_site_info(fields: dict, touchdowns: list, align_die: str = "") -> dict:
    """Where the align site is, from the two independent sources.

    The .PMA states it only indirectly: XMoveFirstFromAlignSite/Y... are the
    offset FROM the align site TO THE MAP ORIGIN (the top-left of the grid,
    which the original exe called 0,0), so negating them puts the align site
    in the same frame the touchdowns use, and dividing by the quad pitch gives
    its quad coordinates. Sanity check: that lands on the wafer's extent centre,
    which is where an operator aligns. The recipe-generator workbook, when one is
    loaded,
    NAMES the die instead ("Align Die" on its first sheet) - that is stated
    rather than derived, so it wins when the two disagree.

    Returns keys: quad, offset_um, die_ids, named_touchdown, quad_touchdown,
    touchdown (the preferred one), source, agree.
    """
    info = {"quad": None, "offset_um": None, "die_ids": [],
            "named_touchdown": None, "quad_touchdown": None,
            "touchdown": None, "source": "", "agree": None}

    try:
        dx = float(fields["DieSizeX"])
        dy = float(fields["DieSizeY"])
        ox = float(fields["XMoveFirstFromAlignSite"])
        oy = float(fields["YMoveFirstFromAlignSite"])
    except (KeyError, TypeError, ValueError):
        dx = dy = ox = oy = None
    if dx and dy and ox is not None and oy is not None:
        info["offset_um"] = (ox, oy)
        info["quad"] = (-ox / dx, -oy / dy)
        want = (round(info["quad"][0]), round(info["quad"][1]))
        for t in touchdowns:
            if (round(t["x"] / dx), round(t["y"] / dy)) == want:
                info["quad_touchdown"] = t
                break

    info["die_ids"] = [p.strip() for p in (align_die or "").split("/") if p.strip()]
    if info["die_ids"]:
        wanted = {d.upper() for d in info["die_ids"]}
        for t in touchdowns:
            ids = {d.strip().upper() for d in t.get("devices") or [t["device_id"]]}
            if wanted & ids:
                info["named_touchdown"] = t
                break

    if info["named_touchdown"] is not None:
        info["touchdown"] = info["named_touchdown"]
        info["source"] = "recipe generator (Align Die)"
    elif info["quad_touchdown"] is not None:
        info["touchdown"] = info["quad_touchdown"]
        info["source"] = "PMA (XMoveFirstFromAlignSite)"
    elif info["quad"] is not None:
        info["source"] = "PMA (XMoveFirstFromAlignSite)"

    if info["named_touchdown"] is not None and info["quad_touchdown"] is not None:
        info["agree"] = info["named_touchdown"]["seq"] == info["quad_touchdown"]["seq"]
    return info


def measurement_plan(fields: dict) -> dict:
    """What this recipe actually measures, and with what.

    Returns keys: style ("dmm" | "smu" | "none"), summary, wires, and the
    raw settings. "none" is a real answer, not a failure - the 21PCM recipe
    carries no measurement fields at all and only steps the wafer.
    """
    fn = (fields.get("ExternalDMM2Function") or "").strip().upper()
    if fn:
        rng = fields.get("ExternalDMM2Range", "")
        nplc = fields.get("ExternalDMM2NPLC", "")
        wires = DMM_FUNCTION_WIRES.get(fn)
        try:
            current = _ohms_source_current(float(rng))
        except (TypeError, ValueError):
            current = None
        return {
            "style": "dmm", "function": fn, "range": rng, "nplc": nplc,
            "short_wait": fields.get("ShortWait", ""),
            "wires": wires,
            "source_current": current,
            "summary": (
                f"HP 3458A {fn} ({wires}-wire resistance) on the {rng} ohm "
                f"range, NPLC {nplc}"
                + (f", sources {_fmt_current(current)}" if current else "")),
        }
    if fields.get("Voltage"):
        return {
            "style": "smu", "wires": 2,
            "voltage": fields.get("Voltage"),
            "range": fields.get("MeterRange", ""),
            "compliance": fields.get("MeterCurrentLimit", ""),
            "nplc": fields.get("NPLC", ""),
            "summary": (
                f"SMU sources {fields.get('Voltage')} V and measures current; "
                f"range {fields.get('MeterRange', '?')}, compliance "
                f"{fields.get('MeterCurrentLimit', '?')}, NPLC "
                f"{fields.get('NPLC', '?')}"),
        }
    return {"style": "none", "wires": None,
            "summary": "No measurement fields - this recipe only steps the wafer."}


# Mirrors instruments/hp3458a.py OHMS_TEST_CURRENT; duplicated rather than
# imported so the recipe layer stays free of driver imports.
_OHMS_SOURCE_CURRENT = {
    10: 10e-3, 100: 1e-3, 1e3: 1e-3, 10e3: 100e-6, 100e3: 50e-6,
    1e6: 5e-6, 10e6: 500e-9, 100e6: 500e-9, 1e9: 500e-9,
}


def _ohms_source_current(range_ohms: float):
    for r in sorted(_OHMS_SOURCE_CURRENT):
        if range_ohms <= r * 1.001:
            return _OHMS_SOURCE_CURRENT[r]
    return None


def _fmt_current(amps: float) -> str:
    for scale, unit in ((1.0, "A"), (1e-3, "mA"), (1e-6, "uA"), (1e-9, "nA")):
        if abs(amps) >= scale:
            return f"{amps / scale:g} {unit}"
    return f"{amps:g} A"


def map_to_prober_um(fields: dict, map_x: float, map_y: float) -> tuple:
    """Recipe map microns -> prober microns, with the prober zeroed on the align site.

    This is what the original LaMP exe did: the operator zeros the prober on the
    align site, the exe shifts to the top-left of the grid and works from there,
    and every touchdown is reached with an absolute MICRON move (MA) rather than
    a die move. Absolute micron moves do not care what die size the prober has
    configured, which is the whole trap that MD stepping carries.
    """
    return (float(fields["XMoveFirstFromAlignSite"]) + float(map_x),
            float(fields["YMoveFirstFromAlignSite"]) + float(map_y))


def touchdown_prober_um(fields: dict, touchdown: dict) -> tuple:
    return map_to_prober_um(fields, touchdown["x"], touchdown["y"])


# row/col are the authoritative cell keys, row 0 = TOP of the wafer.
#
# x_um/y_um are RENDER coordinates, not recipe coordinates: WaferMapPanel maps
# larger y to higher on screen, while the recipe frame runs +y DOWN from the
# top-left origin. Emitting y_um = -map_y is what makes the Run tab map agree
# with the PMA Wafer tab instead of being upside down. map_x/map_y keep the
# recipe's own microns so the file is still traceable back to the .PMV.
_DIE_CSV_FIELDS = ("row", "col", "seq", "quad_pos", "device_id",
                   "x_um", "y_um", "map_x", "map_y",
                   "shot_x", "shot_y", "enabled")


def die_grid_index(dies: list) -> tuple:
    """(x -> col, y -> row) for a die list, row 0 at the TOP.

    Rows come from map y ascending because the recipe frame runs +y down, so
    the smallest y is the top of the wafer. eg_pma_run_panel._build_rc_index
    must agree with this exactly or the run would colour the wrong squares.
    """
    xs = sorted({round(d["x"]) for d in dies})
    ys = sorted({round(d["y"]) for d in dies})
    return ({x: i for i, x in enumerate(xs)},
            {y: i for i, y in enumerate(ys)})


def expand_touchdowns_to_dies(touchdowns: list, die_size_x, die_size_y) -> list:
    """One record per DIE, not per touchdown.

    A touchdown coordinate is the corner of the 2x2 quad the same way
    _draw_map has always treated it - the map frame runs +x right and +y down
    from the top-left origin, so that corner is the TOP-LEFT die, and the
    other three sit one half-pitch out. That makes QUAD_GRID's (col, row) the
    multiplier directly.

    Quads that are not four-up (single-die recipes) come back as one record
    with quad_pos "" at the touchdown coordinate, so callers do not have to
    special-case them.
    """
    dx, dy = float(die_size_x), float(die_size_y)
    half_x, half_y = dx / 2.0, dy / 2.0
    out = []
    for t in touchdowns:
        entries = quad_positions(t["device_id"])
        for ent in entries:
            if ent["pos"] is None:
                ox = oy = 0.0
            else:
                col, row = QUAD_GRID[ent["pos"]]
                ox, oy = col * half_x, row * half_y
            out.append({
                "seq": t["seq"],
                "quad_pos": ent["pos"] or "",
                "device_id": ent["device"],
                "x": t["x"] + ox,
                "y": t["y"] + oy,
                "shot_x": t["x"],
                "shot_y": t["y"],
                # "enabled" is the column name WaferMapPanel already filters on, so an
                # NA quad position is dropped from the map without extra plumbing.
                "enabled": 1 if ent["present"] else 0,
            })
    return out


def save_wafer_map_csv(folder: str, touchdowns: list, fields: dict = None) -> str:
    """Write the Run tab's Electroglas map.

    With `fields` (so the quad pitch is known) this writes one row per DIE, so
    the map shows every die with its own ID rather than one square per 2x2
    shot. Without it, the older per-touchdown form is written - kept so any
    caller that has not got the .PMA header to hand still works.
    """
    path = os.path.join(folder, "ata_wafer_map_electroglas.csv")
    if fields:
        dies = expand_touchdowns_to_dies(touchdowns, fields["DieSizeX"],
                                         fields["DieSizeY"])
        x_to_col, y_to_row = die_grid_index(dies)
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=_DIE_CSV_FIELDS)
            wr.writeheader()
            for d in dies:
                wr.writerow({
                    "row": y_to_row[round(d["y"])],
                    "col": x_to_col[round(d["x"])],
                    "seq": d["seq"], "quad_pos": d["quad_pos"],
                    "device_id": d["device_id"],
                    "x_um": fmt_num(d["x"]), "y_um": fmt_num(-d["y"]),
                    "map_x": fmt_num(d["x"]), "map_y": fmt_num(d["y"]),
                    "shot_x": fmt_num(d["shot_x"]),
                    "shot_y": fmt_num(d["shot_y"]),
                    "enabled": d["enabled"],
                })
        return path
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        wr.writeheader()
        for t in touchdowns:
            row = {k: t[k] for k in _CSV_FIELDS}
            row["x"] = fmt_num(row["x"])
            row["y"] = fmt_num(row["y"])
            wr.writerow(row)
    return path


def _group_by_major(touchdowns: list) -> tuple:
    groups = {}
    order = []
    for t in touchdowns:
        idx = t["major_index"]
        if idx not in groups:
            groups[idx] = {"x": t["major_x"], "y": t["major_y"],
                           "device_id_major": t["device_id_major"],
                           "device_ids": [], "minor_x": [], "minor_y": []}
            order.append(idx)
        groups[idx]["device_ids"].append(t["device_id"])
        groups[idx]["minor_x"].append(t["x"] - t["major_x"])
        groups[idx]["minor_y"].append(t["y"] - t["major_y"])
    return groups, order


def _join_nums(values: list) -> str:
    return ",".join(fmt_num(v) for v in values)


MOVE_LIST_FIELDS = ("step", "command", "major_index", "device_ids",
                    "MovesMajorX", "MovesMajorY", "MovesMinorX", "MovesMinorY")


def build_move_list(touchdowns: list) -> list:
    groups, order = _group_by_major(touchdowns)
    move_list = []
    for step, idx in enumerate(order, start=1):
        g = groups[idx]
        move_list.append({
            "step": step,
            "command": "G" if step == 1 else "J",
            "major_index": idx,
            "device_ids": ",".join(g["device_ids"]),
            "MovesMajorX": g["x"],
            "MovesMajorY": g["y"],
            "MovesMinorX": _join_nums(g["minor_x"]),
            "MovesMinorY": _join_nums(g["minor_y"]),
        })
    return move_list


def save_move_list_csv(path: str, move_list: list) -> str:
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=MOVE_LIST_FIELDS)
        wr.writeheader()
        for m in move_list:
            row = {k: m[k] for k in MOVE_LIST_FIELDS}
            row["MovesMajorX"] = fmt_num(row["MovesMajorX"])
            row["MovesMajorY"] = fmt_num(row["MovesMajorY"])
            wr.writerow(row)
    return path


def load_move_list_csv(path: str) -> list:
    if not path or not os.path.isfile(path):
        return []
    move_list = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                move_list.append({
                    "step": int(row.get("step") or 0),
                    "command": row.get("command", ""),
                    "major_index": int(row.get("major_index") or 0),
                    "device_ids": row.get("device_ids", ""),
                    "MovesMajorX": float(row.get("MovesMajorX") or 0),
                    "MovesMajorY": float(row.get("MovesMajorY") or 0),
                    "MovesMinorX": row.get("MovesMinorX", ""),
                    "MovesMinorY": row.get("MovesMinorY", ""),
                })
            except (TypeError, ValueError):
                continue
    return move_list


def _pitch_index(values: list) -> dict:
    uniq = sorted(set(values))
    if len(uniq) < 2:
        return {v: 0 for v in uniq}
    pitch = min(uniq[i + 1] - uniq[i] for i in range(len(uniq) - 1))
    if pitch <= 0:
        return {v: i for i, v in enumerate(uniq)}
    base = uniq[0]
    return {v: round((v - base) / pitch) for v in uniq}


def to_shot_data(pma_path: str, fields: dict, touchdowns: list) -> dict:
    groups, order = _group_by_major(touchdowns)
    shots_by_major = {idx: {"x_um": groups[idx]["x"], "y_um": groups[idx]["y"],
                            "dies": split_quad_devices(groups[idx]["device_id_major"]),
                            "included": True}
                      for idx in order}

    xs = sorted(set(shots_by_major[idx]["x_um"] for idx in order))
    ys = sorted(set(shots_by_major[idx]["y_um"] for idx in order))
    x_to_col = _pitch_index(xs)
    y_to_row = _pitch_index(ys)

    shots = []
    for idx in order:
        s = shots_by_major[idx]
        s["row"] = y_to_row[s["y_um"]]
        s["col"] = x_to_col[s["x_um"]]
        shots.append(s)

    rows = (max(y_to_row.values()) + 1) if y_to_row else 0
    cols = (max(x_to_col.values()) + 1) if x_to_col else 0

    name = os.path.splitext(os.path.basename(pma_path))[0]
    total_dies = sum(len(s["dies"]) for s in shots)
    na_dies = sum(1 for s in shots for d in s["dies"] if d.strip().upper() == "NA")
    return {
        "path": pma_path,
        "recipe_name": name,
        "die_size_x": fields.get("DieSizeX", ""),
        "die_size_y": fields.get("DieSizeY", ""),
        "x_move_first": fields.get("XMoveFirstFromAlignSite", ""),
        "y_move_first": fields.get("YMoveFirstFromAlignSite", ""),
        "rows": rows,
        "cols": cols,
        "included_shot_count": len(shots),
        "excluded_shot_count": 0,
        "real_die_count": total_dies - na_dies,
        "na_die_count": na_dies,
        "shots": shots,
        "x_headers": xs,
        "y_headers": ys,
    }


# ---------------------------------------------------------------------------
# Recipe GENERATION (the reverse of the parsing above) -- mirrors the
# "IMT Recipe Generation" VBA macro suite (basProbeRecipe.CreateAllFiles /
# WriteMovesFile / Padto7Digits) embedded in the real recipe-generator .xls
# files, which is normally run from inside Excel. A grid here is:
#   {"x_headers": [float, ...], "y_headers": [float, ...],
#    "cells": {(row, col): {"device_id": str, "excluded": bool}}}
# with row 0 / col 0 at (y_headers[0], x_headers[0]), matching MajorMoves'/
# MinorMoves' own row-1/column-A header convention.
# ---------------------------------------------------------------------------

_STRUCTURAL_FIELDS = ("DieSizeX", "DieSizeY",
                      "XMoveFirstFromAlignSite", "YMoveFirstFromAlignSite")


def _pad7_gen(n: int) -> str:
    return str(n).zfill(7)


def serpentine_order(y_count: int, x_count: int, cells: dict) -> list:
    """(row, col) visiting order for a grid scan, skipping excluded cells.

    Replicates WriteMovesFile's row-major "boustrophedon" scan exactly:
    the column direction only flips after a row that actually had at
    least one non-excluded cell -- an all-excluded row leaves the next
    row's direction unchanged, just like the VBA's HaveWritten-gated
    IsRightward toggle.
    """
    order = []
    is_rightward = True
    have_written = False
    for row in range(y_count):
        if have_written:
            is_rightward = not is_rightward
        have_written = False
        cols = range(x_count) if is_rightward else range(x_count - 1, -1, -1)
        for col in cols:
            cell = cells.get((row, col))
            if cell is None or cell.get("excluded"):
                continue
            order.append((row, col))
            have_written = True
    return order


def write_major_moves(dest_dir: str, recipe_name: str, grid: dict) -> dict:
    """Writes <recipe_name>MovesMajorX.PMV / ...Y.PMV / DeviceIDMajor.PMS
    from a spatial wafer grid (see module docstring above).

    Device ids come from each cell's own text if present, else an
    auto-incrementing zero-padded 7-digit id (Padto7Digits) -- the
    counter only advances for auto-numbered cells, exactly like the VBA.
    """
    x_headers = grid["x_headers"]
    y_headers = grid["y_headers"]
    cells = grid["cells"]
    order = serpentine_order(len(y_headers), len(x_headers), cells)

    ids, xs, ys = [], [], []
    counter = 1
    for row, col in order:
        text = (cells[(row, col)].get("device_id") or "").strip()
        if text:
            ids.append(text)
        else:
            ids.append(_pad7_gen(counter))
            counter += 1
        xs.append(x_headers[col])
        ys.append(y_headers[row])

    x_path = os.path.join(dest_dir, f"{recipe_name}MovesMajorX.PMV")
    y_path = os.path.join(dest_dir, f"{recipe_name}MovesMajorY.PMV")
    id_path = os.path.join(dest_dir, f"{recipe_name}DeviceIDMajor.PMS")
    with open(x_path, "w", encoding="utf-8") as f:
        f.writelines(fmt_num(v) + "\n" for v in xs)
    with open(y_path, "w", encoding="utf-8") as f:
        f.writelines(fmt_num(v) + "\n" for v in ys)
    with open(id_path, "w", encoding="utf-8") as f:
        f.writelines(i + "\n" for i in ids)
    return {"count": len(order), "x_path": x_path, "y_path": y_path, "id_path": id_path}


def write_minor_sites(dest_dir: str, recipe_name: str, sites: list) -> dict:
    """Writes <recipe_name>MovesMinorX.PMV / ...Y.PMV / DeviceIDMinor.PMS
    from a flat list of per-die sub-touchdown sites (each a dict with
    "dx"/"dy" offsets and an optional "suffix" id) -- unlike Major, minor
    sites are just sub-positions within one die, not a second spatial
    wafer map, so no grid/serpentine scan applies: every listed site is
    written in list order, blank suffixes auto-numbered.
    """
    x_path = os.path.join(dest_dir, f"{recipe_name}MovesMinorX.PMV")
    y_path = os.path.join(dest_dir, f"{recipe_name}MovesMinorY.PMV")
    id_path = os.path.join(dest_dir, f"{recipe_name}DeviceIDMinor.PMS")
    ids = [(s.get("suffix") or "").strip() or _pad7_gen(i + 1)
          for i, s in enumerate(sites)]
    with open(x_path, "w", encoding="utf-8") as f:
        f.writelines(fmt_num(s["dx"]) + "\n" for s in sites)
    with open(y_path, "w", encoding="utf-8") as f:
        f.writelines(fmt_num(s["dy"]) + "\n" for s in sites)
    with open(id_path, "w", encoding="utf-8") as f:
        f.writelines(i + "\n" for i in ids)
    return {"count": len(sites), "x_path": x_path, "y_path": y_path, "id_path": id_path}


def write_recipe_files(dest_dir: str, recipe_name: str, main_fields: dict,
                       major: dict, minor_sites: list) -> str:
    """Writes the full 7-file recipe set (.PMA + 3 Major + 3 Minor) and
    returns the .PMA path. main_fields is an ordered name->value dict;
    DieSizeX/DieSizeY/XMoveFirstFromAlignSite/YMoveFirstFromAlignSite are
    written first (structural), then every other entry in insertion
    order -- mirroring MainMenu's rows 35-300 free-form field loop.
    """
    os.makedirs(dest_dir, exist_ok=True)
    maj = write_major_moves(dest_dir, recipe_name, major)
    minr = write_minor_sites(dest_dir, recipe_name, minor_sites)

    lines = [
        f"CountMovesMajor={maj['count']}",
        f"DeviceIDMajor={maj['id_path']}",
        f"MovesMajor={os.path.join(dest_dir, recipe_name + 'MovesMajor')}",
        f"CountMovesMinor={minr['count']}",
        f"DeviceIDMinor={minr['id_path']}",
        f"MovesMinor={os.path.join(dest_dir, recipe_name + 'MovesMinor')}",
    ]
    for key in _STRUCTURAL_FIELDS:
        value = str(main_fields.get(key, "")).strip()
        if value:
            lines.append(f"{key}={value}")
    for key, value in main_fields.items():
        if key in _STRUCTURAL_FIELDS:
            continue
        value = str(value).strip()
        if value:
            lines.append(f"{key}={value}")

    pma_path = os.path.join(dest_dir, f"{recipe_name}.PMA")
    with open(pma_path, "w", encoding="utf-8") as f:
        f.writelines(line + "\n" for line in lines)
    return pma_path


def new_grid(rows: int, cols: int, x_start: float, y_start: float,
            pitch_x: float, pitch_y: float) -> dict:
    """A fresh, fully-included, blank-device-id grid of the given shape."""
    x_headers = [x_start + i * pitch_x for i in range(cols)]
    y_headers = [y_start + i * pitch_y for i in range(rows)]
    cells = {(r, c): {"device_id": "", "excluded": False}
            for r in range(rows) for c in range(cols)}
    return {"x_headers": x_headers, "y_headers": y_headers, "cells": cells}
