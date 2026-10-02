#!/usr/bin/env python3
"""Build the template-based SCAD -> STL -> HTML assembly preview.

The formal OpenSCAD export remains the source of truth.  This adapter only
normalizes each exported STL into local coordinates and writes a manifest for
the reusable ``scad-assembly-web-preview`` engine.  Generated STL copies live
under ``preview/assembly/models`` and are intentionally ignored by git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Iterable, Sequence


CAD_ROOT = Path(__file__).resolve().parent
SOURCE_MANIFEST = CAD_ROOT / "exports" / "desktop-clamp-one-side-x1c-v0.7-split-c-scheme" / "manifest.json"
PREVIEW_ROOT = CAD_ROOT / "preview" / "assembly"
MODELS_ROOT = PREVIEW_ROOT / "models"
OUTPUT_MANIFEST = PREVIEW_ROOT / "manifest.json"


def _slug(value: object) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return result or "part"


def _vec_min(vertices: Sequence[tuple[float, float, float]]) -> tuple[float, float, float]:
    return tuple(min(vertex[index] for vertex in vertices) for index in range(3))


def _vec_max(vertices: Sequence[tuple[float, float, float]]) -> tuple[float, float, float]:
    return tuple(max(vertex[index] for vertex in vertices) for index in range(3))


def _cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _normal(triangle: Sequence[tuple[float, float, float]]) -> tuple[float, float, float]:
    a = tuple(triangle[1][i] - triangle[0][i] for i in range(3))
    b = tuple(triangle[2][i] - triangle[0][i] for i in range(3))
    n = _cross(a, b)
    length = math.sqrt(sum(value * value for value in n))
    return (0.0, 0.0, 0.0) if length == 0 else tuple(value / length for value in n)


def _read_ascii_stl(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    """Read the ASCII STL files emitted by the repository's OpenSCAD export."""

    vertices: list[tuple[float, float, float]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.strip().split()
        if len(fields) != 4 or fields[0].lower() != "vertex":
            continue
        try:
            vertices.append((float(fields[1]), float(fields[2]), float(fields[3])))
        except ValueError as error:
            raise ValueError(f"{path}: invalid STL vertex: {line!r}") from error
    if not vertices or len(vertices) % 3:
        raise ValueError(f"{path}: expected a non-empty ASCII STL with complete triangles")
    return [tuple(vertices[index : index + 3]) for index in range(0, len(vertices), 3)]


def _read_binary_stl(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    triangles = []
    for index in range(count):
        offset = 84 + index * 50
        triangles.append(tuple(
            struct.unpack_from("<3f", data, offset + 12 + vertex_index * 12)
            for vertex_index in range(3)
        ))
    return triangles


def _read_stl(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    data = path.read_bytes()
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if 84 + 50 * count == len(data):
            return _read_binary_stl(path)
    return _read_ascii_stl(path)


def _box_triangles(size: Sequence[float]) -> list[tuple[tuple[float, float, float], ...]]:
    """Return a watertight local-coordinate box for diagnostic context solids.

    These boxes are deliberately generated from SCAD assembly datums rather than
    pretending to be printable parts.  They let the reusable preview show the
    real table/net installation envelope without adding another source model.
    """

    sx, sy, sz = (float(value) for value in size)
    p = {
        "000": (0.0, 0.0, 0.0),
        "100": (sx, 0.0, 0.0),
        "110": (sx, sy, 0.0),
        "010": (0.0, sy, 0.0),
        "001": (0.0, 0.0, sz),
        "101": (sx, 0.0, sz),
        "111": (sx, sy, sz),
        "011": (0.0, sy, sz),
    }
    faces = [
        ("000", "100", "110", "010"),
        ("001", "011", "111", "101"),
        ("000", "001", "101", "100"),
        ("010", "110", "111", "011"),
        ("000", "010", "011", "001"),
        ("100", "101", "111", "110"),
    ]
    triangles: list[tuple[tuple[float, float, float], ...]] = []
    for a, b, c, d in faces:
        triangles.extend(((p[a], p[b], p[c]), (p[a], p[c], p[d])))
    return triangles


def _translate_triangles(
    triangles: Iterable[Sequence[tuple[float, float, float]]],
    offset: Sequence[float],
) -> list[tuple[tuple[float, float, float], ...]]:
    return [
        tuple(tuple(vertex[index] + float(offset[index]) for index in range(3)) for vertex in triangle)
        for triangle in triangles
    ]


def _cylinder_triangles(
    radius: float,
    height: float,
    *,
    axis: str = "z",
    origin: Sequence[float] = (0.0, 0.0, 0.0),
    segments: int = 32,
) -> list[tuple[tuple[float, float, float], ...]]:
    """Make a small faceted cylinder for a purchased-part envelope."""

    if axis not in {"x", "y", "z"}:
        raise ValueError(f"unsupported cylinder axis: {axis}")
    ox, oy, oz = (float(value) for value in origin)

    def point(distance: float, angle: float) -> tuple[float, float, float]:
        c, s = radius * math.cos(angle), radius * math.sin(angle)
        if axis == "x":
            return ox + distance, oy + c, oz + s
        if axis == "y":
            return ox + c, oy + distance, oz + s
        return ox + c, oy + s, oz + distance

    triangles: list[tuple[tuple[float, float, float], ...]] = []
    start_center = (ox, oy, oz)
    end_center = point(height, 0.0)
    for index in range(segments):
        a0 = 2 * math.pi * index / segments
        a1 = 2 * math.pi * (index + 1) / segments
        p0, p1 = point(0.0, a0), point(0.0, a1)
        q0, q1 = point(height, a0), point(height, a1)
        triangles.extend(((p0, p1, q1), (p0, q1, q0)))
        triangles.extend(((start_center, p1, p0), (end_center, q0, q1)))
    return triangles


def _sphere_triangles(
    radius: float,
    center: Sequence[float],
    *,
    segments: int = 24,
    rings: int = 12,
) -> list[tuple[tuple[float, float, float], ...]]:
    """Make a faceted sphere for the visible metal ball in the purchased head."""

    cx, cy, cz = (float(value) for value in center)

    def point(phi: float, theta: float) -> tuple[float, float, float]:
        return (
            cx + radius * math.sin(phi) * math.cos(theta),
            cy + radius * math.sin(phi) * math.sin(theta),
            cz + radius * math.cos(phi),
        )

    triangles: list[tuple[tuple[float, float, float], ...]] = []
    for ring in range(rings):
        phi0 = math.pi * ring / rings
        phi1 = math.pi * (ring + 1) / rings
        for segment in range(segments):
            theta0 = 2 * math.pi * segment / segments
            theta1 = 2 * math.pi * (segment + 1) / segments
            a, b = point(phi0, theta0), point(phi0, theta1)
            c, d = point(phi1, theta1), point(phi1, theta0)
            if ring == 0:
                triangles.append((a, c, d))
            elif ring == rings - 1:
                triangles.append((a, b, c))
            else:
                triangles.extend(((a, b, c), (a, c, d)))
    return triangles


def _purchased_ballhead_triangles() -> list[tuple[tuple[float, float, float], ...]]:
    """Approximate the purchased 13 mm ballhead and both threaded interfaces.

    This is a display envelope only.  It is intentionally tagged as a
    purchased part in the manifest and must not be mistaken for printable CAD.
    """

    # The local datum is the centre of the 13 mm ball.  The body is a 28 mm
    # long x-oriented housing; the selected M8 stud points z- and the fixed
    # 1/4-20 stud points x- into the rear-cover boss.  This is a transparent
    # envelope for an already purchased part, not a replacement thread model.
    triangles = _translate_triangles(_box_triangles((28.0, 24.0, 26.0)), (0.0, -12.0, -13.0))
    triangles += _sphere_triangles(6.5, (14.0, 0.0, 0.0))
    triangles += _cylinder_triangles(16.0, 8.0, origin=(14.0, 0.0, -17.0))
    triangles += _cylinder_triangles(4.0, 28.0, origin=(14.0, 0.0, -45.0))
    triangles += _cylinder_triangles(3.175, 16.0, axis="x", origin=(-16.0, 0.0, 0.0))
    triangles += _cylinder_triangles(9.0, 8.0, axis="y", origin=(14.0, -20.0, 0.0))
    return triangles


def _purchased_m6_sensor_array_triangles(
    count: int = 10,
    pitch: float = 20.0,
) -> list[tuple[tuple[float, float, float], ...]]:
    """Approximate one side's repeated purchased right-angle M6 sensors.

    One shared mesh is used for the ten identical devices on each side.  The
    mesh is an installation envelope only; the vendor SKU and cable exit still
    need to be checked against the delivered parts.
    """

    triangles: list[tuple[tuple[float, float, float], ...]] = []
    for index in range(count):
        offset_z = float(index) * pitch
        triangles += _translate_triangles(_box_triangles((6.0, 10.0, 8.0)), (0.0, -5.0, -4.0 + offset_z))
        triangles += _cylinder_triangles(3.0, 14.0, axis="x", origin=(6.0, 0.0, offset_z))
        triangles += _cylinder_triangles(2.0, 10.0, axis="z", origin=(3.0, 0.0, -14.0 + offset_z))
    return triangles


def _rotate_xyz(vertex: Sequence[float], rotation: Sequence[float]) -> tuple[float, float, float]:
    x, y, z = vertex
    rx, ry, rz = rotation
    cy, sy = math.cos(rx), math.sin(rx)
    y, z = y * cy - z * sy, y * sy + z * cy
    cx, sx = math.cos(ry), math.sin(ry)
    x, z = x * cx + z * sx, -x * sx + z * cx
    cz, sz = math.cos(rz), math.sin(rz)
    x, y = x * cz - y * sz, x * sz + y * cz
    return x, y, z


def _prepare_external_triangles(
    triangles: Iterable[Sequence[tuple[float, float, float]]],
    *,
    mirror_x: bool = False,
    mirror_y: bool = False,
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
) -> list[tuple[tuple[float, float, float], ...]]:
    raw = list(triangles)
    vertices = [vertex for triangle in raw for vertex in triangle]
    minimum = _vec_min(vertices)
    maximum = _vec_max(vertices)
    size = tuple(maximum[index] - minimum[index] for index in range(3))
    prepared = []
    for triangle in raw:
        result = []
        for vertex in triangle:
            point = tuple(vertex[index] - minimum[index] for index in range(3))
            if mirror_x:
                point = (size[0] - point[0], point[1], point[2])
            if mirror_y:
                point = (point[0], size[1] - point[1], point[2])
            result.append(_rotate_xyz(point, rotation))
        prepared.append(tuple(result))
    return prepared


def _local_stl_bytes(
    triangles: Iterable[Sequence[tuple[float, float, float]]],
) -> tuple[bytes, tuple[float, float, float], tuple[float, float, float]]:
    triangles = list(triangles)
    vertices = [vertex for triangle in triangles for vertex in triangle]
    minimum = _vec_min(vertices)
    maximum = _vec_max(vertices)
    header = b"Pingpang SmartGear template assembly local STL".ljust(80, b" ")
    payload = bytearray(header)
    payload.extend(struct.pack("<I", len(triangles)))
    for triangle in triangles:
        normal = _normal(triangle)
        payload.extend(struct.pack("<3f", *normal))
        for vertex in triangle:
            payload.extend(
                struct.pack(
                    "<3f",
                    vertex[0] - minimum[0],
                    vertex[1] - minimum[1],
                    vertex[2] - minimum[2],
                )
            )
        payload.extend(struct.pack("<H", 0))
    return bytes(payload), minimum, maximum


def _group_for(part: str) -> tuple[str, str, str]:
    if part == "context_tabletop":
        return "context", "外部环境（球台与网布）", "#64748b"
    if part == "context_net_fabric":
        return "context", "外部环境（球台与网布）", "#9bd9d1"
    if part == "context_net_height_reference":
        return "context", "外部环境（球台与网布）", "#8492a6"
    if part.startswith("purchased_"):
        return "purchased", "采购件（不打印）", "#d98b44"
    if part.startswith("electronics_"):
        return "electronics", "KiCad 线路板与板载器件", "#3aa4cf"
    if part.startswith("ui_"):
        return "ui-components", "UI 板外接实体件", "#78d9bc"
    if part in {"clamp_body_half_user", "clamp_body_half_opponent", "clamp_electronics_ui_panel_mount"}:
        return "c-clamp", "C 夹分型与 UI 面板", "#d8a24a"
    if part in {"post_clamp_carrier_lower", "post_clamp_carrier_upper"}:
        return "upright", "斜立柱与底座", "#66b6a4"
    if part == "net_clamp_rod":
        return "net", "球网与圆柱插杆", "#e7e7e7"
    if part.startswith("m6_detector_") or part in {"sensor_mount_body", "sensor_clamp_lip"}:
        return "m6", "M6 光电端结构", "#6aa9e8"
    if part in {
        "clamp_pressure_pad",
        "clamp_pressure_pad_guard",
        "clamp_printed_screw",
        "clamp_body_nut",
        "clamp_knob",
        "clamp_knob_nut",
    }:
        return "clamp-hardware", "桌下夹紧机构", "#d9a441"
    if part == "calibration_gauge":
        return "reference", "标定参考件", "#8492a6"
    return "other", "其他打印件", "#92b9f0"


def _side_label(value: object) -> str:
    if value == 1:
        return "右"
    if value == -1:
        return "左"
    return "共享"


def _installation_transform(
    entry: dict[str, object],
    minimum: tuple[float, float, float],
    right_m6_offset_x: float,
    m6_raise_z: float,
) -> tuple[list[float], list[float], list[float], list[float]]:
    """Return frame position/rotation, motion axis/range for one source part."""

    part = str(entry["part"])
    side = entry.get("side_value")
    position = list(minimum)
    rotation = [0.0, 0.0, 0.0]
    axis: list[float] = [0.0, 0.0, 0.0]
    motion_range = [0.0, 0.0]

    # The formal net rod is a print-oriented horizontal STL.  The installed
    # preview rotates it to the vertical Z datum used by the SCAD assembly.
    if part == "net_clamp_rod":
        side_value = 1 if side == 1 else -1
        rod_x = 912.8 * side_value
        position = [rod_x, -5.0, 16.0]
        rotation = [0.0, -math.pi / 2 if side_value > 0 else math.pi / 2, 0.0]
        axis = [1.0 if side_value > 0 else -1.0, 0.0, 0.0]
        motion_range = [0.0, 24.0]
    elif part == "clamp_body_half_user":
        axis, motion_range = [0.0, -1.0, 0.0], [0.0, 28.0]
    elif part == "clamp_body_half_opponent":
        axis, motion_range = [0.0, 1.0, 0.0], [0.0, 28.0]
    elif part == "clamp_electronics_ui_panel_mount":
        axis, motion_range = [0.0, 1.0, 0.0], [0.0, 24.0]
    elif part == "post_clamp_carrier_upper":
        axis, motion_range = [0.0, 0.0, 1.0], [0.0, 30.0]
    elif part == "m6_detector_shell_front":
        axis, motion_range = [1.0, 0.0, 0.0], [0.0, 18.0]
    elif part == "m6_detector_shell_rear":
        axis, motion_range = [-1.0, 0.0, 0.0], [0.0, 18.0]
    elif part in {"m6_detector_bottom_cover", "m6_detector_bottom_gasket"}:
        axis, motion_range = [0.0, 0.0, -1.0], [0.0, 12.0]
    elif part in {"clamp_pressure_pad", "clamp_pressure_pad_guard"}:
        axis, motion_range = [0.0, 0.0, -1.0], [0.0, 14.0]
    elif part in {"clamp_printed_screw", "clamp_body_nut", "clamp_knob", "clamp_knob_nut"}:
        axis, motion_range = [0.0, 0.0, -1.0], [0.0, 22.0]

    if part.startswith("m6_detector_"):
        side_value = 1 if side == 1 else -1
        position[0] += side_value * right_m6_offset_x
        position[2] += m6_raise_z
    return position, rotation, axis, motion_range


def _build_manifest(source: dict[str, object], source_path: Path) -> dict[str, object]:
    MODELS_ROOT.mkdir(parents=True, exist_ok=True)
    for old in MODELS_ROOT.glob("*.stl"):
        old.unlink()

    entries = list(source.get("parts", []))
    if not entries:
        raise ValueError("source print manifest has no parts")
    right_post = next((item for item in entries if item.get("part") == "post_clamp_carrier_lower" and item.get("side_value") == 1), None)
    right_rear = next((item for item in entries if item.get("part") == "m6_detector_shell_rear" and item.get("side_value") == 1), None)
    if not right_post or not right_rear:
        raise ValueError("source print manifest is missing right post or M6 rear cover")
    post_bounds = right_post["bounds"]
    rear_bounds = right_rear["bounds"]
    post_center_x = (float(post_bounds["min"][0]) + float(post_bounds["max"][0])) / 2
    rear_max_x = float(rear_bounds["max"][0])
    raw_ballhead_center_x = rear_max_x + (16.0 - 12.0) + 2.0 + 28.0 / 2
    right_m6_offset_x = post_center_x - raw_ballhead_center_x
    raw_shell_bottom_z = float(rear_bounds["min"][2])
    m6_raise_z = max(20.0, 168.5 + 2.0 - raw_shell_bottom_z)

    groups = [
        {"id": "context", "label": "外部环境（球台与网布）"},
        {"id": "purchased", "label": "采购件（不打印）"},
        {"id": "c-clamp", "label": "C 夹分型与 UI 面板"},
        {"id": "upright", "label": "斜立柱与底座"},
        {"id": "net", "label": "球网与圆柱插杆"},
        {"id": "m6", "label": "M6 光电端结构"},
        {"id": "electronics", "label": "KiCad 线路板与板载器件"},
        {"id": "ui-components", "label": "UI 板外接实体件"},
        {"id": "clamp-hardware", "label": "桌下夹紧机构"},
        {"id": "reference", "label": "标定参考件"},
        {"id": "other", "label": "其他打印件"},
    ]

    frames: list[dict[str, object]] = [{
        "id": "world",
        "label": "世界坐标（Z+向上）",
        "parentFrameId": None,
        "kind": "fixed",
        "localTransform": {"position": [0, 0, 0], "rotation": [0, 0, 0]},
    }]

    # Fixed mount frames make the physical dependency tree explicit.  Their
    # transforms intentionally stay at the world datum: the child frames keep
    # the measured SCAD/KiCad world positions, while moving a parent in the
    # template will still carry its complete mounted subtree with it.
    mount_frame_specs = [
        ("context-table", "球台台面（装配环境）", "world", "environment", "SCAD table_top datum"),
        ("context-net", "球网/网布（装配环境）", "world", "environment", "SCAD net datum"),
        ("context-reference", "球网高度参考线（诊断）", "context-net", "reference", "SCAD net_top datum"),
        ("mount-right-clamp", "右侧 C 夹总成", "world", "mount", "夹口夹持球台边缘"),
        ("mount-right-post", "右侧立柱总成（挂到 C 夹）", "mount-right-clamp", "mount", "底座安装面/分型面"),
        ("mount-right-ballhead", "右侧采购球头/连接接口", "mount-right-post", "purchased-interface", "M8×1.25 下端进入立柱上段；1/4-20 上端进入 M6 后盖 boss"),
        ("mount-right-m6", "右侧 M6 光电端（挂到采购球头）", "mount-right-ballhead", "mount", "后盖 boss 与球头 1/4-20 螺柱同轴"),
        ("mount-right-ui", "右侧 UI/电子腔（挂到 C 夹内壁）", "mount-right-clamp", "mount", "y+ 内壁 UI 安装面"),
        ("mount-left-clamp", "左侧 C 夹总成", "world", "mount", "夹口夹持球台边缘"),
        ("mount-left-post", "左侧立柱总成（挂到 C 夹）", "mount-left-clamp", "mount", "底座安装面/分型面"),
        ("mount-left-ballhead", "左侧采购球头/连接接口", "mount-left-post", "purchased-interface", "M8×1.25 下端进入立柱上段；1/4-20 上端进入 M6 后盖 boss"),
        ("mount-left-m6", "左侧 M6 光电端（挂到采购球头）", "mount-left-ballhead", "mount", "后盖 boss 与球头 1/4-20 螺柱同轴"),
        ("mount-left-ui", "左侧发射电子腔（挂到 C 夹）", "mount-left-clamp", "mount", "y+ 内壁电子安装面"),
    ]
    mount_relations: list[dict[str, object]] = []
    for frame_id, label, parent_id, node_type, interface in mount_frame_specs:
        frames.append({
            "id": frame_id,
            "label": label,
            "parentFrameId": parent_id,
            "kind": "fixed",
            "localTransform": {"position": [0, 0, 0], "rotation": [0, 0, 0]},
            "extensions": {"nodeType": node_type, "mountInterface": interface},
        })
        mount_relations.append({
            "childFrameId": frame_id,
            "parentFrameId": parent_id,
            "childLabel": label,
            "parentLabel": next(
                (item[1] for item in mount_frame_specs if item[0] == parent_id),
                "世界坐标（Z+向上）" if parent_id == "world" else parent_id,
            ),
            "interface": interface,
            "evidence": "SCAD/KiCad 装配定位关系；仅表示挂载依赖，不是受力/干涉验收。",
        })

    def parent_frame_for(entry: dict[str, object]) -> str:
        """Map each displayed object to its real mounted subsystem."""

        part = str(entry["part"])
        side = entry.get("side_value")
        side_name = "right" if side == 1 else "left" if side == -1 else None
        if part == "context_tabletop":
            return "context-table"
        if part == "context_net_fabric":
            return "context-net"
        if part == "context_net_height_reference":
            return "context-reference"
        if part == "calibration_gauge":
            return "context-table"
        if side_name is None:
            return "world"
        if part == "post_clamp_carrier_lower":
            return f"mount-{side_name}-clamp"
        if part == "post_clamp_carrier_upper":
            return f"mount-{side_name}-post"
        if part == "purchased_ballhead":
            return f"mount-{side_name}-ballhead"
        if part == "purchased_m6_sensor_array":
            return f"mount-{side_name}-m6"
        if part in {"m6_detector_body", "m6_detector_shell_front", "m6_detector_shell_rear",
                    "m6_detector_bottom_cover", "m6_detector_bottom_gasket",
                    "electronics_m6_receiver_carrier_right", "electronics_m6_receiver_carrier_left"}:
            return f"mount-{side_name}-m6"
        if part in {"sensor_mount_body", "sensor_clamp_lip", "net_clamp_rod"}:
            return f"mount-{side_name}-post"
        if part.startswith("electronics_") or part.startswith("ui_") or part == "clamp_electronics_ui_panel_mount":
            return f"mount-{side_name}-ui"
        return f"mount-{side_name}-clamp"

    parts: list[dict[str, object]] = []
    moving_frames: list[tuple[str, list[float], list[float]]] = []
    instances_by_part: dict[str, list[dict[str, object]]] = {}
    output_by_hash: dict[str, str] = {}
    used_ids: set[str] = set()
    focus_ids: dict[str, list[str]] = {}

    receiver_raw_origin = [780.0, -4.9, 212.5]
    receiver_installed_x = receiver_raw_origin[0] + right_m6_offset_x
    receiver_installed_z = receiver_raw_origin[2] + m6_raise_z
    raw_ballhead_center_z = (
        float(rear_bounds["min"][2]) + float(rear_bounds["max"][2])
    ) / 2
    installed_ballhead_center_z = raw_ballhead_center_z + m6_raise_z
    # These two values mirror the authoritative SCAD datums
    # (table_edge_x + optical_beam_edge_overlap and beam_first_height).  They
    # are used only to place the purchased display envelope against the same
    # M6 openings; the source SCAD remains the dimensional authority.
    installed_sensor_axis_x = 762.5 + 0.5 + right_m6_offset_x
    installed_sensor_first_z = 168.5 + 10.0 + m6_raise_z
    # These are the real KiCad-exported board/component solids already used by
    # the electronics maintenance page.  They are external display geometry,
    # not new SCAD parts and not printable replacements for the PCB source.
    context_entries: list[dict[str, object]] = [
        {
            "part": "context_tabletop",
            "name_zh": "球台台面（装配环境参考）",
            "file": "generated-context-tabletop.stl",
            "source_file": "../../net_stand.scad",
            "source_kind": "scad",
            "definitions": ["PART=assembly", "table_top datum"],
            "side_value": None,
            "generated_box": {"minimum": [-762.5, -250.0, -25.0], "size": [1525.0, 500.0, 25.0]},
            "color": "#64748b",
            "opacity": 0.24,
            "notes": "球台台面安装环境参考；来自 net_stand.scad 的 table_top datum，不是打印件。",
        },
        {
            "part": "context_net_fabric",
            "name_zh": "乒乓球网布（装配环境参考）",
            "file": "generated-context-net-fabric.stl",
            "source_file": "../../net_stand.scad",
            "source_kind": "scad",
            "definitions": ["PART=assembly", "net fabric datum"],
            "side_value": None,
            "generated_box": {"minimum": [-915.0, -0.6, 16.0], "size": [1830.0, 1.2, 152.5]},
            "color": "#9bd9d1",
            "opacity": 0.34,
            "explosion": [0.0, 0.0, 82.0],
            "notes": "网布/网套的装配环境占位；来自 net_stand.scad 的网高基准，不是打印件。",
        },
        {
            "part": "context_net_height_reference",
            "name_zh": "网顶高度参考线（诊断）",
            "file": "generated-context-net-height.stl",
            "source_file": "../../net_stand.scad",
            "source_kind": "scad",
            "definitions": ["PART=assembly", "net_top datum"],
            "side_value": None,
            "generated_box": {"minimum": [-915.0, -0.5, 202.0], "size": [1830.0, 1.0, 1.0]},
            "color": "#8492a6",
            "opacity": 0.55,
            "explosion": [0.0, -78.0, 48.0],
            "notes": "用于检查网顶高度的诊断线，不是实体零件。",
        },
    ]
    external_entries: list[dict[str, object]] = [
        {
            "part": "electronics_esp32_main",
            "name_zh": "ESP32-S3 主控板（KiCad）",
            "file": "esp32-control-v0.1.stl",
            "source_file": "../../../electronics/3d/v0.2/esp32-control-v0.1.stl",
            "source_kind": "external",
            "side_value": 1,
            "display_position": [792.9, -16.0, -36.4912],
            "motion_axis": [0.0, 0.0, 1.0],
            "motion_max": 24.0,
            "explosion": [0.0, 0.0, 24.0],
            "color": "#2f80ed",
            "notes": "KiCad 导出的板级模型，包含主控、板载器件和 UI 连接器；仅用于电子腔装配查看。",
        },
        {
            "part": "electronics_emitter_power",
            "name_zh": "发射端电源子板（KiCad）",
            "file": "emitter-power-v0.2.stl",
            "source_file": "../../../electronics/3d/v0.2/emitter-power-v0.2.stl",
            "source_kind": "external",
            "side_value": -1,
            "display_position": [-802.9, -16.0, -35.8912],
            "motion_axis": [0.0, 0.0, 1.0],
            "motion_max": 24.0,
            "explosion": [0.0, 0.0, 24.0],
            "mirror_x": True,
            "color": "#c94b63",
            "notes": "KiCad 导出的发射端电源子板；按现有电子腔镜像基准放置。",
        },
        {
            "part": "electronics_ui_panel",
            "name_zh": "UI 交互子板（KiCad）",
            "file": "ui-panel-v0.2.stl",
            "source_file": "../../../electronics/3d/v0.2/ui-panel-v0.2.stl",
            "source_kind": "external",
            "side_value": 1,
            "display_position": [806.9, 16.69, -12.0],
            "motion_axis": [0.0, 1.0, 0.0],
            "motion_max": 34.0,
            "explosion": [0.0, 34.0, 0.0],
            "mirror_y": True,
            "rotation": [-math.pi / 2, 0.0, 0.0],
            "color": "#48a0e8",
            "notes": "KiCad UI 板模型，含板载按键、LED 和唯一 Type-C 接口；按现有 y+ 面板方向预变换。",
        },
        {
            "part": "electronics_m6_receiver_carrier_right",
            "name_zh": "右侧 M6 十路接收子板（KiCad）",
            "file": "m6-receiver-carrier-v0.2.stl",
            "source_file": "../../../electronics/3d/v0.2/m6-receiver-carrier-v0.2.stl",
            "source_kind": "external",
            "side_value": 1,
            "display_position": [receiver_installed_x, receiver_raw_origin[1], receiver_installed_z],
            "motion_axis": [0.0, 1.0, 0.0],
            "motion_max": 42.0,
            "explosion": [0.0, 42.0, 0.0],
            "rotation": [0.0, -math.pi / 2, 0.0],
            "color": "#36a269",
            "notes": "KiCad M6 载板，随右侧 M6 壳体的 x/z 基准同步。",
        },
        {
            "part": "electronics_m6_receiver_carrier_left",
            "name_zh": "左侧 M6 十路接收子板（KiCad）",
            "file": "m6-receiver-carrier-v0.2.stl",
            "source_file": "../../../electronics/3d/v0.2/m6-receiver-carrier-v0.2.stl",
            "source_kind": "external",
            "side_value": -1,
            "display_position": [-receiver_installed_x, receiver_raw_origin[1], receiver_installed_z],
            "motion_axis": [0.0, 1.0, 0.0],
            "motion_max": 42.0,
            "explosion": [0.0, 42.0, 0.0],
            "mirror_x": True,
            "rotation": [0.0, -math.pi / 2, 0.0],
            "color": "#36a269",
            "notes": "KiCad M6 载板左侧镜像实例，保持与右侧板同一模型来源。",
        },
        {
            "part": "ui_physical_items",
            "name_zh": "屏幕与扬声器（SCAD 线束实体）",
            "file": "ui-physical-items-v0.2.stl",
            "source_file": "../../../electronics/3d/v0.2/ui-physical-items-v0.2.stl",
            "source_kind": "external",
            "side_value": 1,
            "display_position": [823.4, 25.8, -33.0],
            "motion_axis": [0.0, 1.0, 0.0],
            "motion_max": 34.0,
            "explosion": [0.0, 34.0, 0.0],
            "color": "#78d9bc",
            "notes": "只保留通过线束连接的屏幕和扬声器实体；PCB 按键、LED、Type-C 由 KiCad UI 板提供。",
        },
        {
            "part": "ui_led_light_pipes",
            "name_zh": "UI LED 导光柱（SCAD）",
            "file": "ui-led-light-pipes-v0.2.stl",
            "source_file": "../../../electronics/3d/v0.2/ui-led-light-pipes-v0.2.stl",
            "source_kind": "external",
            "side_value": 1,
            "display_position": [834.9, 25.4, -38.0],
            "motion_axis": [0.0, 1.0, 0.0],
            "motion_max": 34.0,
            "explosion": [0.0, 34.0, 0.0],
            "color": "#b8f6dc",
            "notes": "独立透明导光柱，作为 UI 板 LED 的装配参考。",
        },
    ]
    purchased_entries: list[dict[str, object]] = []
    for side_value, side_name in ((1, "右"), (-1, "左")):
        purchased_entries.append({
            "part": "purchased_ballhead",
            "name_zh": f"13 mm 采购球头/连接接口（{side_name}）",
            "file": "generated-purchased-ballhead.stl",
            "source_file": "../../net_stand.scad",
            "source_kind": "external",
            "definitions": [
                "PURCHASED m6_ballhead envelope",
                "M8x1.25 lower stud -> upright top",
                "1/4-20 upper stud -> M6 rear boss",
            ],
            "side_value": side_value,
            "generated_geometry": "purchased-ballhead",
            "display_position": [
                post_center_x - 30.0 if side_value == 1 else -post_center_x - 14.0,
                -20.0,
                installed_ballhead_center_z - 45.0,
            ],
            "mirror_x": side_value < 0,
            "motion_axis": [0.0, 0.0, 1.0],
            "motion_max": 18.0,
            "explosion": [side_value * 150.0, -28.0, 18.0],
            "color": "#d98b44",
            "notes": "外采 13 mm 球头只作为安装包络显示，不是打印件。下端选 M8×1.25 外牙沿 z- 进入立柱上段顶面攻丝孔；上端固定 1/4-20 外牙沿 x 进入 M6 后盖中央 boss，并由采购螺母锁紧。旧版 90° 独立连接器不属于当前方案。",
            "scope": "purchased",
            "procurement_status": "外购；螺纹有效长度和旋钮净空需按到货件复核",
            "assembly_role": "立柱与 M6 后盖之间的可调承力接口",
        })
        purchased_entries.append({
            "part": "purchased_m6_sensor_array",
            "name_zh": f"M6 直角光电件阵列包络（{side_name}，10 枚）",
            "file": "generated-purchased-m6-sensor-array.stl",
            "source_file": "../../net_stand.scad",
            "source_kind": "external",
            "definitions": [
                "PURCHASED m6_sensor_array envelope",
                "M6x0.75; 10 pcs; pitch 20 mm",
            ],
            "side_value": side_value,
            "generated_geometry": "purchased-m6-sensor-array",
            "display_position": [
                installed_sensor_axis_x if side_value == 1 else -installed_sensor_axis_x - 20.0,
                -5.0,
                installed_sensor_first_z - 14.0,
            ],
            "mirror_x": side_value < 0,
            "motion_axis": [side_value * 1.0, 0.0, 0.0],
            "motion_max": 14.0,
            "explosion": [side_value * 70.0, -24.0, 12.0],
            "color": "#b6b8bd",
            "notes": "外采 M6×0.75 直角发射/接收器的十枚重复包络；光学端沿光束轴进入主体，头部和安装杆由当前 M6 壳体的开孔包络承接。这里显示一份共享阵列网格，采购数量为左右各 10 枚；实际 SKU、尾线方向和锁紧螺母仍需实测。",
            "scope": "purchased",
            "procurement_status": "外购；左右各 10 枚，型号后缀和输出方式需核对",
            "assembly_role": "M6 外采光电头插入打印主体/壳体的安装包络",
        })
    all_entries = context_entries + purchased_entries + entries + external_entries

    for index, raw in enumerate(all_entries):
        entry = dict(raw)
        source_file = (
            CAD_ROOT.parent / "electronics" / "3d" / "v0.2" / str(entry["file"])
            if entry.get("source_kind") == "external"
            else source_path.parent / str(entry["file"])
        )
        generated_geometry = entry.get("generated_geometry")
        if generated_geometry == "purchased-ballhead":
            triangles = _purchased_ballhead_triangles()
        elif generated_geometry == "purchased-m6-sensor-array":
            triangles = _purchased_m6_sensor_array_triangles()
        elif entry.get("generated_box"):
            triangles = _box_triangles(entry["generated_box"]["size"])
        else:
            if not source_file.is_file():
                raise FileNotFoundError(f"missing source STL: {source_file}")
            triangles = _read_stl(source_file)
        if entry.get("source_kind") == "external":
            triangles = _prepare_external_triangles(
                triangles,
                mirror_x=bool(entry.get("mirror_x")),
                mirror_y=bool(entry.get("mirror_y")),
                rotation=entry.get("rotation", (0.0, 0.0, 0.0)),
            )
        local_bytes, minimum, maximum = _local_stl_bytes(triangles)
        digest = hashlib.sha256(local_bytes).hexdigest()
        model_file = output_by_hash.get(digest)
        if model_file is None:
            model_file = f"models/stl-{digest[:20]}.stl"
            (PREVIEW_ROOT / model_file).write_bytes(local_bytes)
            output_by_hash[digest] = model_file

        side = entry.get("side_value")
        base_id = _slug(f"{entry['part']}-{_side_label(side)}")
        part_id = base_id
        suffix = 2
        while part_id in used_ids:
            part_id = f"{base_id}-{suffix}"
            suffix += 1
        used_ids.add(part_id)
        instance_id = f"instance-{part_id}"
        frame_id = f"frame-{part_id}"
        group_id, group_label, color = _group_for(str(entry["part"]))
        position, rotation, axis, motion_range = _installation_transform(
            entry, minimum, right_m6_offset_x, m6_raise_z
        )
        if entry.get("generated_box"):
            position = list(entry["generated_box"]["minimum"])
            rotation = [0.0, 0.0, 0.0]
        if entry.get("source_kind") == "external":
            position = [
                float(entry["display_position"][index]) + minimum[index]
                for index in range(3)
            ]
            rotation = [0.0, 0.0, 0.0]
            axis = list(entry.get("motion_axis", [0.0, 1.0, 0.0]))
            motion_range = [0.0, float(entry.get("motion_max", 42.0))]
        kind = entry.get("role")
        if kind is None:
            if entry.get("scope") == "purchased":
                kind = "purchased"
            elif entry.get("source_kind") == "external" or entry.get("generated_box") or entry.get("part") == "calibration_gauge":
                kind = "diagnostic"
            else:
                kind = "printed"
        visible = bool(entry.get("visible", entry.get("part") != "calibration_gauge"))
        name = f"{entry.get('name_zh') or entry['part']} · {_side_label(side)}"
        selector = "; ".join(str(value) for value in entry.get("definitions", [])) or str(entry["part"])
        parent_frame_id = parent_frame_for(entry)
        frames.append({
            "id": frame_id,
            "label": name,
            "parentFrameId": parent_frame_id,
            "kind": "prismatic" if motion_range[1] else "fixed",
            "axis": axis if motion_range[1] else None,
            "range": motion_range if motion_range[1] else None,
            "defaultValue": 0 if motion_range[1] else None,
            "localTransform": {"position": position, "rotation": rotation},
        })
        frame = frames[-1]
        for key in ("axis", "range", "defaultValue"):
            if frame[key] is None:
                del frame[key]
        if motion_range[1]:
            moving_frames.append((frame_id, axis, motion_range))

        explosion = [0.0, 0.0, 0.0]
        if str(entry["part"]) == "clamp_body_half_user":
            explosion = [0, -22, 0]
        elif str(entry["part"]) == "clamp_body_half_opponent":
            explosion = [0, 22, 0]
        elif str(entry["part"]) == "clamp_electronics_ui_panel_mount":
            explosion = [0, 20, 0]
        elif str(entry["part"]) == "post_clamp_carrier_upper":
            explosion = [0, 0, 30]
        elif str(entry["part"]).startswith("m6_detector_shell_"):
            explosion = [22 if "front" in str(entry["part"]) else -22, 0, 0]
        elif str(entry["part"]) in {"m6_detector_bottom_cover", "m6_detector_bottom_gasket"}:
            explosion = [0, 0, -18]
        elif str(entry["part"]) == "net_clamp_rod":
            explosion = [25 if side == 1 else -25, 0, 0]
        elif str(entry["part"]) in {"clamp_pressure_pad", "clamp_pressure_pad_guard"}:
            explosion = [0, 0, -20]
        elif str(entry["part"]) in {"clamp_printed_screw", "clamp_body_nut", "clamp_knob", "clamp_knob_nut"}:
            explosion = [0, 0, -26]
        elif str(entry["part"]) in {"context_net_fabric", "context_net_height_reference"}:
            explosion = list(entry.get("explosion", [0.0, 0.0, 0.0]))
        if entry.get("source_kind") == "external":
            explosion = list(entry.get("explosion", [0.0, 0.0, 0.0]))
        if entry.get("generated_box"):
            explosion = list(entry.get("explosion", explosion))

        instance = {
            "id": instance_id,
            "name": name,
            "parentFrameId": frame_id,
            "localTransform": {"position": [0, 0, 0], "rotation": [0, 0, 0]},
            "explosion": explosion,
            "visible": visible,
        }
        part_record = {
            "id": part_id,
            "name": name,
            "source": {
                "kind": entry.get("source_kind", "scad"),
                "file": entry.get("source_file", "../../net_stand.scad"),
                "selector": selector,
            },
            "file": model_file,
            "geometrySpace": "local",
            "role": kind,
            "groupId": group_id,
            "color": entry.get("color", color),
            "opacity": float(entry.get("opacity", 0.35 if not visible else 1)),
            "instances": [instance],
            "extensions": {
                "sourcePart": entry["part"],
                "side": side,
                "sourceFile": entry["file"],
                "originalBounds": {"min": list(minimum), "max": list(maximum)},
                "notes": entry.get("notes") or entry.get("orientation") or "",
                "mountFrameId": parent_frame_id,
                "scope": entry.get(
                    "scope",
                    "project-print" if kind == "printed" else
                    "external-environment" if entry.get("generated_box") else
                    "external-reference",
                ),
            },
        }
        if entry.get("procurement_status"):
            part_record["extensions"]["procurementStatus"] = entry["procurement_status"]
        if entry.get("assembly_role"):
            part_record["extensions"]["assemblyRole"] = entry["assembly_role"]
        if generated_geometry:
            part_record["extensions"]["geometryStatus"] = "display envelope only; not printable CAD"
        parts.append(part_record)
        instances_by_part.setdefault(str(entry["part"]), []).append(instance)
        if entry["part"] in {"clamp_electronics_ui_panel_mount", "m6_detector_body", "post_clamp_carrier_upper", "net_clamp_rod", "context_tabletop", "context_net_fabric", "context_net_height_reference"} or entry["part"].startswith("purchased_"):
            focus_ids.setdefault(str(entry["part"]), []).append(instance_id)
            focus_ids.setdefault("purchased", []).append(instance_id)

    def values_for(stage: str) -> dict[str, float]:
        result: dict[str, float] = {}
        for frame_id, _axis, motion_range in moving_frames:
            result[frame_id] = {
                "assembled": motion_range[0],
                "service": motion_range[1] * 0.65,
                "exploded": motion_range[1],
            }[stage]
        return result

    source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source_rel = (Path("..", "..") / source_path.relative_to(CAD_ROOT)).as_posix()
    procurement_items = [
        {
            "id": item.get("id"),
            "name": item.get("name_zh") or item.get("name_en") or item.get("id"),
            "kind": item.get("kind"),
            "status": item.get("status"),
            "quantity": item.get("quantity"),
            "scadPart": item.get("scad_part"),
            "notes": item.get("notes", ""),
        }
        for item in source.get("assembly_components", [])
        if not item.get("printable", False)
    ]
    manifest: dict[str, object] = {
        "schemaVersion": 1,
        "title": "球网架通用装配预览 · 模板引擎",
        "ui": {"persistPanelState": True, "showSearch": True, "showGroups": True},
        "assembly": {
            "coordinateSystem": {
                "units": "mm",
                "handedness": "right",
                "up": "z",
                "description": "项目 SCAD 世界坐标；X 左右，Y 前后，Z 海拔/高度。",
            },
            "rootFrameId": "world",
            "frames": frames,
        },
        "groups": groups,
        "parts": parts,
        "stages": [
            {"id": "assembled", "label": "装配状态", "values": values_for("assembled")},
            {"id": "service", "label": "维护打开", "values": values_for("service")},
            {"id": "exploded", "label": "分解检查", "values": values_for("exploded")},
        ],
        "playback": {
            "sequence": ["assembled", "service", "exploded", "assembled"],
            "secondsPerTransition": 1.6,
            "loop": True,
        },
        "views": [
            {"id": "global", "label": "全局等轴", "direction": [1, 0.8, 0.65]},
            {"id": "table", "label": "球台安装关系", "direction": [1, 0.8, 0.45], "focusInstanceIds": focus_ids.get("context_tabletop", []) + focus_ids.get("context_net_fabric", []) + focus_ids.get("post_clamp_carrier_lower", [])},
            {"id": "front", "label": "前视（Y-）", "direction": [0, -1, 0]},
            {"id": "rear", "label": "后视（Y+）", "direction": [0, 1, 0]},
            {"id": "right", "label": "右视（X+）", "direction": [1, 0, 0]},
            {"id": "left", "label": "左视（X-）", "direction": [-1, 0, 0]},
            {"id": "top", "label": "俯视（Z+）", "direction": [0, 0, 1]},
            {"id": "ui", "label": "UI 面板与电子腔", "direction": [0, 1, 0], "focusInstanceIds": focus_ids.get("clamp_electronics_ui_panel_mount", [])},
            {"id": "m6", "label": "M6 光电端", "direction": [1, 0.35, 0.25], "focusInstanceIds": focus_ids.get("m6_detector_body", []) + focus_ids.get("purchased_ballhead", []) + focus_ids.get("purchased_m6_sensor_array", [])},
            {"id": "purchased", "label": "采购件与安装接口", "direction": [1, 0.55, 0.35], "focusInstanceIds": focus_ids.get("purchased", [])},
            {"id": "post", "label": "立柱分型", "direction": [1, 0.5, 0.4], "focusInstanceIds": focus_ids.get("post_clamp_carrier_upper", [])},
            {"id": "net", "label": "网杆入口", "direction": [1, 0.3, 0.25], "focusInstanceIds": focus_ids.get("net_clamp_rod", [])},
        ],
        "extensions": {
            "adapter": "hardware/cad/build_assembly_preview.py",
            "sourceManifest": source_rel,
            "sourceManifestSha256": source_sha,
            "sourceScad": "hardware/cad/net_stand.scad",
            "generatedGeometry": "local STL copies are derived from the formal export and are ignored by git",
            "motionStatus": "visual-service-stages; not a dynamics, load, or interference proof",
            "mountRelations": mount_relations,
            "treeSemantics": "frames describe installed parent-child dependencies; purchased parts stay in their real mount subtree; diagnostic context solids are not printable parts",
            "scopePolicy": {
                "project-print": "正式打印件，来源为当前打印 manifest",
                "purchased": "外采实体或外采实体包络，不进入打印盘",
                "external-environment": "球台/网布等项目外部安装环境，不是本工程零件",
                "external-reference": "KiCad/SCAD 外部参考实体；用于装配查看，不改变打印清单",
            },
            "procurementItems": procurement_items,
            "retiredExternalParts": [
                {
                    "id": "legacy-90-degree-m6-connector",
                    "name": "旧版 90°金属连接件/独立适配板",
                    "status": "retired",
                    "reason": "当前方案由 13 mm 采购球头的 M8 下端直接进入立柱、1/4-20 上端直接进入 M6 后盖 boss；旧件不再属于当前装配。",
                },
            ],
            "groupLegend": {group_id: label for group_id, label, _color in [
                _group_for(str(item["part"])) for item in all_entries
            ]},
        },
    }
    OUTPUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    global OUTPUT_MANIFEST
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-manifest", type=Path, default=SOURCE_MANIFEST)
    parser.add_argument("--output", type=Path, default=OUTPUT_MANIFEST)
    args = parser.parse_args()
    source_path = args.source_manifest.resolve()
    if not source_path.is_file():
        raise SystemExit(f"找不到正式打印件 manifest：{source_path}\n请先运行 python3 hardware/cad/export_net_stand_printables.py --clean")
    OUTPUT_MANIFEST = args.output.resolve()
    if OUTPUT_MANIFEST != PREVIEW_ROOT / "manifest.json":
        raise SystemExit("目前只支持输出到 hardware/cad/preview/assembly/manifest.json，以保持模板资源相对路径安全")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    manifest = _build_manifest(source, source_path)
    print(
        f"ASSEMBLY_PREVIEW_OK parts={len(manifest['parts'])} "
        f"frames={len(manifest['assembly']['frames'])} "
        f"models={len({part['file'] for part in manifest['parts']})} "
        f"manifest={OUTPUT_MANIFEST}"
    )


if __name__ == "__main__":
    main()
