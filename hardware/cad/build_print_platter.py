#!/usr/bin/env python3
"""Build deterministic rigid-transform print plates for the net-stand parts.

The exporter in ``export_net_stand_printables.py`` creates one STL per printable
part.  This script only places those already-exported meshes on a configurable
print bed; it never scales, remeshes, welds, or booleans the source geometry.
Parts that cannot fit the selected bed are kept in the manifest as
``oversized`` instead of being silently clipped or rotated out of bounds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
EXPORT_ROOT = HERE / "exports" / "net-stand-v0.1"
SOURCE_MANIFEST = EXPORT_ROOT / "manifest.json"
DEFAULT_OUTPUT = EXPORT_ROOT / "print-platter-256"
TRIANGLE = struct.Struct("<12fH")

PRESETS: dict[str, dict[str, object]] = {
    "x1c-256": {
        "label": "256 × 256 × 256 mm（X1C 类）",
        "width_mm": 256.0,
        "depth_mm": 256.0,
        "height_mm": 256.0,
        "edge_margin_mm": 5.0,
    },
    "large-300": {
        "label": "300 × 300 × 300 mm",
        "width_mm": 300.0,
        "depth_mm": 300.0,
        "height_mm": 300.0,
        "edge_margin_mm": 5.0,
    },
    "large-400": {
        "label": "400 × 400 × 400 mm",
        "width_mm": 400.0,
        "depth_mm": 400.0,
        "height_mm": 400.0,
        "edge_margin_mm": 5.0,
    },
}


@dataclass(frozen=True)
class BinaryStl:
    path: Path
    triangles: tuple[tuple[float, ...], ...]
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]]


@dataclass(frozen=True)
class Placement:
    source: dict[str, object]
    mesh: BinaryStl
    rotation_z_deg: int
    x: float
    y: float
    rotated_bounds: tuple[tuple[float, float, float], tuple[float, float, float]]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bounds_of(triangles: Iterable[tuple[float, ...]]):
    mins = [float("inf")] * 3
    maxs = [float("-inf")] * 3
    found = False
    for values in triangles:
        found = True
        for start in (3, 6, 9):
            for axis in range(3):
                value = values[start + axis]
                mins[axis] = min(mins[axis], value)
                maxs[axis] = max(maxs[axis], value)
    if not found:
        raise ValueError("STL 不包含三角形")
    return (tuple(mins), tuple(maxs))


def load_binary_stl(path: Path) -> BinaryStl:
    data = path.read_bytes()
    if len(data) < 84:
        return load_ascii_stl(path, data)
    if data.lstrip().startswith(b"solid") and b"facet" in data[:512].lower():
        return load_ascii_stl(path, data)
    triangle_count = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + triangle_count * TRIANGLE.size
    if len(data) != expected:
        raise ValueError(f"无法解析 STL: {path} ({len(data)} != {expected})")
    triangles = tuple(
        TRIANGLE.unpack_from(data, 84 + index * TRIANGLE.size)
        for index in range(triangle_count)
    )
    return BinaryStl(path, triangles, bounds_of(triangles))


def load_ascii_stl(path: Path, data: bytes) -> BinaryStl:
    """Parse the simple ASCII STL emitted by the local OpenSCAD CLI."""
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ValueError(f"ASCII STL 编码无效: {path}") from error
    triangles: list[tuple[float, ...]] = []
    normal = (0.0, 0.0, 0.0)
    vertices: list[tuple[float, float, float]] = []
    for line in lines:
        fields = line.strip().split()
        if not fields:
            continue
        if fields[0].lower() == "facet" and len(fields) >= 5:
            normal = tuple(float(value) for value in fields[2:5])
        elif fields[0].lower() == "vertex" and len(fields) >= 4:
            vertices.append(tuple(float(value) for value in fields[1:4]))
            if len(vertices) == 3:
                triangles.append((*normal, *vertices[0], *vertices[1], *vertices[2], 0))
                vertices = []
    if vertices or not triangles:
        raise ValueError(f"ASCII STL 三角形结构不完整: {path}")
    result = tuple(triangles)
    return BinaryStl(path, result, bounds_of(result))


def rotate_xy(x: float, y: float, angle: int) -> tuple[float, float]:
    if angle == 0:
        return x, y
    if angle == 90:
        return -y, x
    raise ValueError(f"仅支持 0/90 度 Z 轴旋转，收到 {angle}")


def rotate_bounds(
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
    angle: int,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    lo, hi = bounds
    points = [
        rotate_xy(x, y, angle)
        for x in (lo[0], hi[0])
        for y in (lo[1], hi[1])
    ]
    return (
        (min(point[0] for point in points), min(point[1] for point in points), lo[2]),
        (max(point[0] for point in points), max(point[1] for point in points), hi[2]),
    )


def transform_triangles(
    triangles: Iterable[tuple[float, ...]],
    angle: int,
    shift: tuple[float, float, float],
) -> tuple[tuple[float, ...], ...]:
    transformed: list[tuple[float, ...]] = []
    for values in triangles:
        moved = list(values)
        normal_x, normal_y = rotate_xy(values[0], values[1], angle)
        moved[0:3] = [normal_x, normal_y, values[2]]
        for start in (3, 6, 9):
            x, y = rotate_xy(values[start], values[start + 1], angle)
            moved[start:start + 3] = [
                x + shift[0],
                y + shift[1],
                values[start + 2] + shift[2],
            ]
        transformed.append(tuple(moved))
    return tuple(transformed)


def write_binary_stl(path: Path, triangles: Iterable[tuple[float, ...]], label: str) -> None:
    all_triangles = tuple(triangles)
    header = label.encode("ascii", errors="replace")[:80]
    with path.open("wb") as handle:
        handle.write(header.ljust(80, b"\0"))
        handle.write(struct.pack("<I", len(all_triangles)))
        for triangle in all_triangles:
            handle.write(TRIANGLE.pack(*triangle))


def dimensions(bounds):
    return tuple(bounds[1][axis] - bounds[0][axis] for axis in range(3))


def fit_orientations(
    mesh: BinaryStl,
    bed_width: float,
    bed_depth: float,
    bed_height: float,
    margin: float,
) -> list[tuple[int, tuple[tuple[float, float, float], tuple[float, float, float]]]]:
    usable_width = bed_width - 2 * margin
    usable_depth = bed_depth - 2 * margin
    candidates = []
    for angle in (0, 90):
        rotated = rotate_bounds(mesh.bounds, angle)
        size = dimensions(rotated)
        if size[0] <= usable_width + 1e-6 and size[1] <= usable_depth + 1e-6 and size[2] <= bed_height + 1e-6:
            candidates.append((angle, rotated))
    return candidates


def part_sort_key(item: dict[str, object], mesh: BinaryStl):
    size = dimensions(mesh.bounds)
    return (-max(size[0], size[1]), -(size[0] * size[1]), str(item["file"]))


def pack_parts(
    parts: list[dict[str, object]],
    meshes: dict[str, BinaryStl],
    *,
    bed_width: float,
    bed_depth: float,
    bed_height: float,
    gap: float,
    margin: float,
) -> tuple[list[list[Placement]], list[dict[str, object]]]:
    if min(bed_width, bed_depth, bed_height, gap) <= 0:
        raise ValueError("打印床尺寸和间隔必须为正数")
    if bed_width <= 2 * margin or bed_depth <= 2 * margin:
        raise ValueError("打印床尺寸必须大于两倍边缘安全余量")

    ordered = sorted(parts, key=lambda item: part_sort_key(item, meshes[str(item["file"])]))
    plates: list[list[Placement]] = []
    rows: list[list[dict[str, float]]] = []
    unplaced: list[dict[str, object]] = []

    def start_plate() -> None:
        plates.append([])
        rows.append([])

    start_plate()

    for item in ordered:
        filename = str(item["file"])
        mesh = meshes[filename]
        candidates = fit_orientations(mesh, bed_width, bed_depth, bed_height, margin)
        if not candidates:
            oversized_entry = {
                "file": filename,
                "part": item.get("part"),
                "side": item.get("side"),
                "index": item.get("index"),
                "status": "oversized",
                "reason": "XY 或 Z 尺寸超过当前打印床（未缩放、未裁切）",
                "source_bounds": [list(value) for value in mesh.bounds],
                "source_size_mm": list(dimensions(mesh.bounds)),
            }
            for key in ("name_zh", "name_en", "component_kind", "printable", "material", "orientation", "notes"):
                if key in item:
                    oversized_entry[key] = item[key]
            unplaced.append(oversized_entry)
            continue

        placed = False
        while not placed:
            current_rows = rows[-1]
            # Keep a strict shelf frontier.  Back-filling an earlier row can
            # make a later row overlap when the earlier row grows taller, so
            # rows are never revisited after the frontier moves on.
            best: tuple[float, int, tuple[tuple[float, float, float], tuple[float, float, float]], float, float] | None = None
            row = current_rows[-1] if current_rows else None
            if row is not None:
                for angle, rotated in candidates:
                    rotated_size = dimensions(rotated)
                    x = row["x"]
                    y = row["y"]
                    if x + rotated_size[0] > bed_width - margin + 1e-6:
                        continue
                    if y + rotated_size[1] > bed_depth - margin + 1e-6:
                        continue
                    score = (max(row["height"], rotated_size[1]), angle, rotated_size[0], x, y)
                    if best is None or score < (best[0], best[1], dimensions(best[2])[0], best[3], best[4]):
                        best = (score[0], angle, rotated, x, y)

            if best is None:
                row_y = margin if row is None else row["y"] + row["height"] + gap
                for angle, rotated in candidates:
                    rotated_size = dimensions(rotated)
                    x = margin
                    y = row_y
                    if y + rotated_size[1] > bed_depth - margin + 1e-6:
                        continue
                    score = (rotated_size[1], angle, rotated_size[0], x, y)
                    if best is None or score < (best[0], best[1], dimensions(best[2])[0], best[3], best[4]):
                        best = (score[0], angle, rotated, x, y)
                if best is not None:
                    _, angle, rotated, x, y = best
                    rotated_size = dimensions(rotated)
                    current_rows.append({"x": x + rotated_size[0] + gap, "y": y, "height": rotated_size[1]})
                else:
                    start_plate()
                    continue
            else:
                _, angle, rotated, x, y = best
                rotated_size = dimensions(rotated)
                row["x"] = x + rotated_size[0] + gap
                row["height"] = max(row["height"], rotated_size[1])

            # Keep the unshifted, rotated source bounds here.  The final bed
            # bounds are derived from x/y; using final_bounds as the transform
            # origin would leave the source CAD's absolute coordinates in the
            # combined STL.
            plates[-1].append(Placement(item, mesh, angle, x, y, rotated))
            placed = True

    # Empty plates can only appear if every remaining part was oversized.
    if plates and not plates[-1]:
        plates.pop()
    return plates, unplaced


def build_manifest(
    source_manifest: dict[str, object],
    plates: list[list[Placement]],
    unplaced: list[dict[str, object]],
    *,
    output_dir: Path,
    bed_width: float,
    bed_depth: float,
    bed_height: float,
    gap: float,
    margin: float,
    preset: str,
    source_manifest_path: Path,
) -> dict[str, object]:
    plate_entries = []
    placement_by_file: dict[str, dict[str, object]] = {}
    for index, plate in enumerate(plates, start=1):
        plate_id = f"plate-{index:02d}"
        output_path = output_dir / f"{plate_id}.stl"
        triangles = []
        placement_entries = []
        for placement in plate:
            rotated_bounds = placement.rotated_bounds
            rotated_lo = rotated_bounds[0]
            shift = (
                placement.x - rotated_lo[0],
                placement.y - rotated_lo[1],
                -rotated_lo[2],
            )
            transformed = transform_triangles(
                placement.mesh.triangles,
                placement.rotation_z_deg,
                shift,
            )
            triangles.extend(transformed)
            item = placement.source
            filename = str(item["file"])
            rotated_size = dimensions(rotated_bounds)
            placed_bounds = (
                (placement.x, placement.y, 0.0),
                (
                    placement.x + rotated_size[0],
                    placement.y + rotated_size[1],
                    rotated_size[2],
                ),
            )
            entry = {
                "file": filename,
                "part": item.get("part"),
                "name_zh": item.get("name_zh", filename.replace(".stl", "")),
                "name_en": item.get("name_en", item.get("part")),
                "component_kind": item.get("component_kind", "打印件"),
                "printable": item.get("printable", True),
                "material": item.get("material"),
                "orientation": item.get("orientation"),
                "notes": item.get("notes"),
                "side": item.get("side"),
                "side_value": item.get("side_value"),
                "index": item.get("index"),
                "plate_id": plate_id,
                "status": "placed",
                "rotation_z_deg": placement.rotation_z_deg,
                "x_mm": placement.x,
                "y_mm": placement.y,
                "source_path": os.path.relpath(placement.mesh.path, output_dir).replace(os.sep, "/"),
                "source_sha256": sha256_file(placement.mesh.path),
                "source_size_mm": list(dimensions(placement.mesh.bounds)),
                "placed_bounds": [list(value) for value in placed_bounds],
                "label": filename.replace(".stl", ""),
            }
            placement_entries.append(entry)
            placement_by_file[filename] = entry
        write_binary_stl(
            output_path,
            triangles,
            f"SmartGear {plate_id}; rigid transforms; independent parts",
        )
        plate_entries.append({
            "id": plate_id,
            "label": f"拼盘 {index:02d}",
            "file": output_path.name,
            "path": output_path.name,
            "description": "独立零件刚体排版；导入切片器后仍需确认支撑、壁数和首层。",
            "part_count": len(placement_entries),
            "parts": placement_entries,
            "sha256": sha256_file(output_path),
        })

    oversized_entries = []
    for entry in unplaced:
        entry_with_path = dict(entry)
        entry_with_path["source_path"] = os.path.relpath(
            source_manifest_path.parent / str(entry["file"]), output_dir
        ).replace(os.sep, "/")
        oversized_entries.append(entry_with_path)

    parts = []
    for item in source_manifest.get("parts", []):
        filename = str(item["file"])
        parts.append(placement_by_file.get(filename, next(
            (entry for entry in oversized_entries if entry["file"] == filename),
            {
                "file": filename,
                "part": item.get("part"),
                "status": "missing",
            },
        )))
    return {
        "schema_version": "0.1",
        "design": "net-stand-v0.1",
        "generated_by": "hardware/cad/build_print_platter.py",
        "source_manifest": os.path.relpath(source_manifest_path, output_dir).replace(os.sep, "/"),
        "source_manifest_sha256": sha256_file(source_manifest_path),
        "units": "mm",
        "preset": preset,
        "print_bed": {
            "width_mm": bed_width,
            "depth_mm": bed_depth,
            "height_mm": bed_height,
            "edge_margin_mm": margin,
            "part_gap_mm": gap,
        },
        "install_model": source_manifest.get("install_model"),
        "assembly_components": source_manifest.get("assembly_components", []),
        "packing": {
            "algorithm": "deterministic shelf packing from actual STL bounds",
            "rigid_transforms_only": True,
            "scaling": False,
            "remeshing": False,
            "boolean_union": False,
        },
        "plates": plate_entries,
        "oversized": oversized_entries,
        "parts": parts,
        "notes": [
            "拼盘 STL 由多个互相独立的封闭零件组成，不是装配件，也不改变源零件尺寸。",
            "超出当前打印床的零件不会被裁切或缩放；网顶长件需要换大床、进一步拆分或改用铝型材。",
            "STL 不保存切片参数；导入切片器时仍需确认 1:1 单位、支撑、壁数、填充和首层。",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=SOURCE_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--preset", choices=tuple(PRESETS), default="x1c-256")
    parser.add_argument("--bed-width", type=float)
    parser.add_argument("--bed-depth", type=float)
    parser.add_argument("--bed-height", type=float)
    parser.add_argument("--gap", type=float, default=5.0)
    parser.add_argument("--edge-margin", type=float)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="仅清理当前输出目录中的 plate-*.stl 和 manifest.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_manifest_path = args.manifest.resolve()
    if not source_manifest_path.is_file():
        raise SystemExit(f"找不到打印件 manifest: {source_manifest_path}；请先导出 50 件 STL")
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if source_manifest.get("source") != "hardware/cad/net_stand.scad":
        raise SystemExit("输入 manifest 不是当前 net_stand.scad 打印清单")

    preset = PRESETS[args.preset]
    bed_width = float(args.bed_width or preset["width_mm"])
    bed_depth = float(args.bed_depth or preset["depth_mm"])
    bed_height = float(args.bed_height or preset["height_mm"])
    margin = float(args.edge_margin if args.edge_margin is not None else preset["edge_margin_mm"])
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.clean:
        for path in output_dir.glob("plate-*.stl"):
            path.unlink()
        manifest_path = output_dir / "manifest.json"
        if manifest_path.exists():
            manifest_path.unlink()

    parts = list(source_manifest.get("parts", []))
    meshes = {}
    for item in parts:
        source_path = source_manifest_path.parent / str(item["file"])
        if not source_path.is_file():
            raise SystemExit(f"打印件 STL 缺失: {source_path}")
        meshes[str(item["file"])] = load_binary_stl(source_path)

    plates, unplaced = pack_parts(
        parts,
        meshes,
        bed_width=bed_width,
        bed_depth=bed_depth,
        bed_height=bed_height,
        gap=args.gap,
        margin=margin,
    )
    manifest = build_manifest(
        source_manifest,
        plates,
        unplaced,
        output_dir=output_dir,
        bed_width=bed_width,
        bed_depth=bed_depth,
        bed_height=bed_height,
        gap=args.gap,
        margin=margin,
        preset=args.preset,
        source_manifest_path=source_manifest_path,
    )
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    placed_count = sum(len(plate) for plate in plates)
    print(
        f"PRINT_PLATTER_OK (preset={args.preset}, plates={len(plates)}, "
        f"placed={placed_count}, oversized={len(unplaced)}, manifest={manifest_path})"
    )
    for item in unplaced:
        print(
            f"OVERSIZED {item['file']}: "
            f"size={item['source_size_mm']} bed={bed_width:g}x{bed_depth:g}x{bed_height:g}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
