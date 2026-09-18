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
# Match export_net_stand_printables.py so the documented default command reads
# the current 37-part manifest instead of the historical 33-part directory.
EXPORT_ROOT = HERE / "exports" / "desktop-clamp-one-side-x1c-v0.4-top-load"
SOURCE_MANIFEST = EXPORT_ROOT / "manifest.json"
DEFAULT_OUTPUT = EXPORT_ROOT / "print-platter-256"
TRIANGLE = struct.Struct("<12fH")
# The taller one-piece post is the only part that needs a reduced nominal bed
# edge margin after the verified diagonal pose is applied.  Its transformed
# envelope is about 252.5 mm on a 256 mm bed, leaving roughly 1.75 mm per side.
# All other parts retain the normal 5 mm margin.
PART_EDGE_MARGINS_MM: dict[str, float] = {
    "post_clamp_carrier": 1.5,
}

Matrix3 = tuple[tuple[float, float, float], ...]
Bounds3 = tuple[tuple[float, float, float], tuple[float, float, float]]


@dataclass(frozen=True)
class Orientation:
    """A rigid print orientation, including optional 3D tilt."""

    label: str
    euler_deg: tuple[float, float, float]
    matrix: Matrix3
    rotated_bounds: Bounds3

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
    orientation: Orientation
    x: float
    y: float
    rotated_bounds: Bounds3


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


def matrix_multiply(left: Matrix3, right: Matrix3) -> Matrix3:
    return tuple(
        tuple(sum(left[row][index] * right[index][column] for index in range(3))
              for column in range(3))
        for row in range(3)
    )


def rotation_matrix_xyz(rx_deg: float, ry_deg: float, rz_deg: float) -> Matrix3:
    """Return Rz * Ry * Rx, matching the documented platter Euler order."""
    rx = math.radians(rx_deg)
    ry = math.radians(ry_deg)
    rz = math.radians(rz_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    rotate_x: Matrix3 = ((1.0, 0.0, 0.0), (0.0, cx, -sx), (0.0, sx, cx))
    rotate_y: Matrix3 = ((cy, 0.0, sy), (0.0, 1.0, 0.0), (-sy, 0.0, cy))
    rotate_z: Matrix3 = ((cz, -sz, 0.0), (sz, cz, 0.0), (0.0, 0.0, 1.0))
    return matrix_multiply(rotate_z, matrix_multiply(rotate_y, rotate_x))


def rotate_point(point: tuple[float, float, float], matrix: Matrix3) -> tuple[float, float, float]:
    return tuple(sum(matrix[row][axis] * point[axis] for axis in range(3)) for row in range(3))


def transform_bounds(bounds: Bounds3, matrix: Matrix3) -> Bounds3:
    lo, hi = bounds
    points = [
        rotate_point((x, y, z), matrix)
        for x in (lo[0], hi[0])
        for y in (lo[1], hi[1])
        for z in (lo[2], hi[2])
    ]
    return (
        tuple(min(point[axis] for point in points) for axis in range(3)),
        tuple(max(point[axis] for point in points) for axis in range(3)),
    )


def rotate_bounds(
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
    angle: int,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    return transform_bounds(bounds, rotation_matrix_xyz(0, 0, angle))


def transform_triangles(
    triangles: Iterable[tuple[float, ...]],
    matrix: Matrix3,
    shift: tuple[float, float, float],
) -> tuple[tuple[float, ...], ...]:
    transformed: list[tuple[float, ...]] = []
    for values in triangles:
        moved = list(values)
        normal = rotate_point((values[0], values[1], values[2]), matrix)
        moved[0:3] = [normal[0], normal[1], normal[2]]
        for start in (3, 6, 9):
            x, y, z = rotate_point(
                (values[start], values[start + 1], values[start + 2]), matrix
            )
            moved[start:start + 3] = [
                x + shift[0],
                y + shift[1],
                z + shift[2],
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


def edge_margin_for_part(part: str | None, default: float) -> float:
    return PART_EDGE_MARGINS_MM.get(str(part or ""), default)


def fit_orientations(
    mesh: BinaryStl,
    bed_width: float,
    bed_depth: float,
    bed_height: float,
    margin: float,
    part: str | None = None,
) -> list[Orientation]:
    usable_width = bed_width - 2 * margin
    usable_depth = bed_depth - 2 * margin
    candidates: list[Orientation] = []
    rotations = [
        ("z0", (0.0, 0.0, 0.0)),
        ("z90", (0.0, 0.0, 90.0)),
    ]
    if part == "post_clamp_carrier":
        # The complete installed part is intentionally kept whole.  Although
        # the active post is taller than the 256 mm build height, the complete
        # carrier stays one piece and uses this rigid 3D tilt.  The post has a
        # part-specific 1.5 mm nominal edge margin; supports remain a slicer
        # decision and the source mesh is never cut or scaled.
        rotations = [("diagonal-rx0-ry51-rz45", (0.0, 51.0, 45.0))]
    for label, euler_deg in rotations:
        matrix = rotation_matrix_xyz(*euler_deg)
        rotated = transform_bounds(mesh.bounds, matrix)
        size = dimensions(rotated)
        if size[0] <= usable_width + 1e-6 and size[1] <= usable_depth + 1e-6 and size[2] <= bed_height + 1e-6:
            candidates.append(Orientation(label, euler_deg, matrix, rotated))
    return candidates


def part_sort_key(item: dict[str, object], mesh: BinaryStl):
    size = dimensions(mesh.bounds)
    return (-max(size[0], size[1]), -(size[0] * size[1]), str(item["file"]))


def material_group_for(item: dict[str, object]) -> str:
    """Resolve the material group, with a safe fallback for older manifests."""
    explicit = str(item.get("material_group") or "").strip()
    if explicit:
        return explicit
    material = str(item.get("material") or "PETG")
    normalized = material.upper()
    if "TPU" in normalized or "硅胶" in material:
        return "TPU/柔性"
    return "PETG"


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

    grouped_parts: dict[str, list[dict[str, object]]] = {}
    for item in parts:
        grouped_parts.setdefault(material_group_for(item), []).append(item)
    material_groups = sorted(
        grouped_parts,
        key=lambda group: (group != "PETG", group),
    )
    plates: list[list[Placement]] = []
    rows: list[list[dict[str, float]]] = []
    unplaced: list[dict[str, object]] = []

    def start_plate(material_group: str) -> None:
        plates.append([])
        rows.append([])

    for current_material_group in material_groups:
        ordered = sorted(
            grouped_parts[current_material_group],
            key=lambda item: part_sort_key(item, meshes[str(item["file"])]),
        )
        start_plate(current_material_group)

        for item in ordered:
            filename = str(item["file"])
            mesh = meshes[filename]
            part = str(item.get("part") or "")
            item_margin = edge_margin_for_part(part, margin)
            candidates = fit_orientations(
                mesh,
                bed_width,
                bed_depth,
                bed_height,
                item_margin,
                part=part,
            )
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
                    "material_group": current_material_group,
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
                best: tuple[tuple[float, ...], Orientation, float, float] | None = None
                row = current_rows[-1] if current_rows else None
                if row is not None:
                    for orientation_index, orientation in enumerate(candidates):
                        rotated_size = dimensions(orientation.rotated_bounds)
                        x = max(row["x"], item_margin)
                        y = max(row["y"], item_margin)
                        if x + rotated_size[0] > bed_width - item_margin + 1e-6:
                            continue
                        if y + rotated_size[1] > bed_depth - item_margin + 1e-6:
                            continue
                        score = (
                            max(row["height"], rotated_size[1]),
                            orientation_index,
                            rotated_size[0],
                            x,
                            y,
                        )
                        if best is None or score < best[0]:
                            best = (score, orientation, x, y)

                if best is None:
                    row_y = (
                        item_margin
                        if row is None
                        else max(item_margin, row["y"] + row["height"] + gap)
                    )
                    for orientation_index, orientation in enumerate(candidates):
                        rotated_size = dimensions(orientation.rotated_bounds)
                        x = item_margin
                        y = row_y
                        if y + rotated_size[1] > bed_depth - item_margin + 1e-6:
                            continue
                        score = (rotated_size[1], orientation_index, rotated_size[0], x, y)
                        if best is None or score < best[0]:
                            best = (score, orientation, x, y)
                    if best is not None:
                        _, orientation, x, y = best
                        rotated_size = dimensions(orientation.rotated_bounds)
                        current_rows.append({"x": x + rotated_size[0] + gap, "y": y, "height": rotated_size[1]})
                    else:
                        start_plate(current_material_group)
                        continue
                else:
                    _, orientation, x, y = best
                    rotated_size = dimensions(orientation.rotated_bounds)
                    row["x"] = x + rotated_size[0] + gap
                    row["height"] = max(row["height"], rotated_size[1])

                # Keep the unshifted, rotated source bounds here.  The final bed
                # bounds are derived from x/y; using final_bounds as the transform
                # origin would leave the source CAD's absolute coordinates in the
                # combined STL.
                plates[-1].append(
                    Placement(item, mesh, orientation, x, y, orientation.rotated_bounds)
                )
                placed = True

        # A material group containing only oversized parts should not leave an
        # empty STL plate in the output package.
        if plates and not plates[-1]:
            plates.pop()
            rows.pop()

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
                placement.orientation.matrix,
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
                "material_group": material_group_for(item),
                "orientation": item.get("orientation"),
                "notes": item.get("notes"),
                "side": item.get("side"),
                "side_value": item.get("side_value"),
                "index": item.get("index"),
                "plate_id": plate_id,
                "status": "placed",
                "orientation_label": placement.orientation.label,
                "rotation_euler_deg": list(placement.orientation.euler_deg),
                "rotation_matrix": [list(row) for row in placement.orientation.matrix],
                "rotation_z_deg": (
                    placement.orientation.euler_deg[2]
                    if placement.orientation.euler_deg[0] == 0
                    and placement.orientation.euler_deg[1] == 0
                    else None
                ),
                "x_mm": placement.x,
                "y_mm": placement.y,
                "source_path": os.path.relpath(placement.mesh.path, output_dir).replace(os.sep, "/"),
                "source_sha256": sha256_file(placement.mesh.path),
                "source_size_mm": list(dimensions(placement.mesh.bounds)),
                "edge_margin_mm": edge_margin_for_part(
                    str(item.get("part") or ""), margin
                ),
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
            "label": f"{material_group_for(plate[0].source)} 拼盘 {index:02d}",
            "material_group": material_group_for(plate[0].source),
            "file": output_path.name,
            "path": output_path.name,
            "description": f"{material_group_for(plate[0].source)} 独立零件刚体排版；不同材料不混盘，导入切片器后仍需确认支撑、壁数和首层。",
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
                "name_zh": item.get("name_zh"),
                "name_en": item.get("name_en"),
                "component_kind": item.get("component_kind", "打印件"),
                "printable": item.get("printable", True),
                "material": item.get("material"),
                "material_group": material_group_for(item),
                "status": "missing",
            },
        )))
    return {
        "schema_version": "0.1",
        "design": "desktop-clamp-one-side-x1c-v0.4-top-load",
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
            "algorithm": "deterministic shelf packing from actual STL bounds with tested rigid 3D tilt candidates",
            "rigid_transforms_only": True,
            "three_dimensional_rotation": True,
            "scaling": False,
            "remeshing": False,
            "boolean_union": False,
            "separate_material_groups": True,
            "part_edge_margins_mm": dict(PART_EDGE_MARGINS_MM),
            "material_groups": sorted(
                {material_group_for(item) for item in source_manifest.get("parts", [])},
                key=lambda group: (group != "PETG", group),
            ),
        },
        "plates": plate_entries,
        "oversized": oversized_entries,
        "parts": parts,
        "notes": [
            "拼盘 STL 由多个互相独立的封闭零件组成，不是装配件，也不改变源零件尺寸。",
            "整根固定网柱与绿色整体底座是一件；绿色底座从 x+ 侧推入固定 C 夹的让位腔，中央 4 mm 钢珠定位，两枚 M4 对孔锁紧。黄绿一体件从底座 z=-4 mm 延伸至 z=260.5 mm；网布/卡夹的功能通道仍只到 z=168.5 mm。X1C 采用已验证的 rx=0°、ry=51°、rz=45° 三轴斜放，不裁切、不缩放，导入切片器后仍需配置支撑并确认设备实际可用范围。",
            "STL 不保存切片参数；导入切片器时仍需确认 1:1 单位、支撑、壁数、填充和首层。",
            "不同材料组严格分盘：TPU/柔性件不会与 PETG 零件进入同一张拼盘；混合材料标注的试样按柔性材料盘处理。",
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
        raise SystemExit(f"找不到打印件 manifest: {source_manifest_path}；请先运行当前打印件导出脚本")
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
