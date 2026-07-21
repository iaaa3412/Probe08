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

ALL_FIELDS = WAFER_FIELDS + ELECTRICAL_FIELDS

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


def load_touchdowns(pma_path: str, fields: dict) -> list:
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
                "x": major_x[i] + mx,
                "y": major_y[i] + my,
                "major_x": major_x[i],
                "major_y": major_y[i],
            })
            seq += 1
    return touchdowns


def fmt_num(v) -> str:
    return str(int(v)) if float(v).is_integer() else str(v)


def save_wafer_map_csv(folder: str, touchdowns: list) -> str:
    path = os.path.join(folder, "ata_wafer_map_electroglas.csv")
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
                            "dies": [groups[idx]["device_id_major"]], "included": True}
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
    real_dies = sum(len(s["dies"]) for s in shots)
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
        "real_die_count": real_dies,
        "na_die_count": 0,
        "shots": shots,
        "x_headers": xs,
        "y_headers": ys,
    }
