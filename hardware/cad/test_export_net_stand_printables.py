#!/usr/bin/env python3
"""Regression-test the net-stand printable export matrix and manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from export_net_stand_printables import (
    DEFAULT_OUTPUT,
    EXPORT_SPECS,
    SOURCE,
    material_group_for,
)


EXPECTED_COUNTS = {
    "post_clamp_carrier": 2,
    "clamp_body_half_user": 2,
    "clamp_body_half_opponent": 2,
    "clamp_electronics_ui_bezel": 2,
    "clamp_electronics_ui_retaining_frame": 2,
    "m6_detector_body": 2,
    "m6_detector_shell_front": 2,
    "m6_detector_shell_rear": 2,
    "m6_detector_bottom_cover": 2,
    "m6_detector_bottom_gasket": 2,
    "m6_detector_cable_gland": 2,
    "net_clamp_clip": 2,
    "clamp_pressure_pad": 2,
    "clamp_pressure_pad_guard": 2,
    "clamp_printed_screw": 2,
    "clamp_body_nut": 2,
    "clamp_knob": 2,
    "clamp_knob_nut": 2,
    "sensor_mount_body": 2,
    "sensor_clamp_lip": 2,
    "calibration_gauge": 1,
}

PREVIEW_ONLY_PARTS = {
    "assembly",
    "left_stand",
    "right_stand",
    "post",
    "clamp_slide_fit_section",
    "table_clamp",
    "net_rail",
    "optical_strip",
    "m6_sensor_rail",
    "m6_sensor_array",
    "m6_gimbal",
    "stg120_preview",
    "sensor_mount",
    "reference_carriage",
}

REMOVED_ACTIVE_PARTS = {
    "net_rail_segment",
    "net_rail_splice",
    "net_rail_saddle",
    "m6_detector_net_connector",
    "post_joint_sleeve",
    "post_joint_key",
    "lower_stand_segment",
    "upper_stand_segment",
    "net_clamp_rod",
    "clamp_body_segment",
}


def validate_export_specs() -> None:
    if len(EXPORT_SPECS) != 41:
        raise AssertionError(f"expected 41 printable exports, got {len(EXPORT_SPECS)}")
    filenames = [spec.filename for spec in EXPORT_SPECS]
    if len(set(filenames)) != len(filenames):
        raise AssertionError("printable export filenames must be unique")
    counts = Counter(spec.part for spec in EXPORT_SPECS)
    if counts != Counter(EXPECTED_COUNTS):
        raise AssertionError(f"printable PART matrix changed: {counts}")
    post_specs = [spec for spec in EXPORT_SPECS if spec.part == "post_clamp_carrier"]
    if len(post_specs) != 2 or any(
        "整根" not in spec.notes
        or "绿色 SKP 整体底座" not in spec.notes
        or "Ø4 mm" not in spec.notes
        or "Ø6×2 mm" not in spec.notes
        or "z=168.5 mm" not in spec.notes
        or "z=260.5 mm" not in spec.notes
        or "没有 T 槽、公轨" not in spec.notes
        or "配套 C 方案夹体" not in spec.notes
        for spec in post_specs
    ):
        raise AssertionError("整根立柱 + SKP C 方案整体底座必须明确推入让位腔、孔位和定位结构")
    removed = sorted(REMOVED_ACTIVE_PARTS & set(counts))
    if removed:
        raise AssertionError(f"legacy/整件 C 夹零件 re-entered print matrix: {removed}")
    split_parts = {
        "clamp_body_half_user",
        "clamp_body_half_opponent",
    }
    if set(counts) & {"clamp_body_segment"}:
        raise AssertionError("完整 C 形夹体不能重新进入正式打印矩阵")
    for part in split_parts:
        split_specs = [spec for spec in EXPORT_SPECS if spec.part == part]
        if len(split_specs) != 2 or any(
            "y=0" not in spec.notes
            or "9 个" not in spec.notes
            or "M5" not in spec.notes
            or "0.20 mm" not in spec.notes
            for spec in split_specs
        ):
            raise AssertionError(f"{part} 必须明确 y=0 分型、9 处 M5 连接位与分型间隙")

    ui_parts = {
        "clamp_electronics_ui_bezel": [spec for spec in EXPORT_SPECS if spec.part == "clamp_electronics_ui_bezel"],
        "clamp_electronics_ui_retaining_frame": [spec for spec in EXPORT_SPECS if spec.part == "clamp_electronics_ui_retaining_frame"],
    }
    if any(len(items) != 2 for items in ui_parts.values()):
        raise AssertionError("UI 填平板和八孔搭接框必须各导出左右两件")
    if any(
        "不打孔" not in spec.notes or "外表面与 C 夹壁齐平" not in spec.notes
        for spec in ui_parts["clamp_electronics_ui_bezel"]
    ):
        raise AssertionError("UI 外侧填平板必须没有可见螺钉孔")
    if any(
        "8 个通孔为 Ø2.3 mm" not in spec.notes or "1.6 mm" not in spec.notes or "2 mm 蘑菇头自攻钉" not in spec.notes
        for spec in ui_parts["clamp_electronics_ui_retaining_frame"]
    ):
        raise AssertionError("UI 八孔搭接框必须记录 2 mm 自攻钉和 C 夹内壁 1.6 mm 盲导孔")

    for spec in EXPORT_SPECS:
        if spec.part in PREVIEW_ONLY_PARTS:
            raise AssertionError(f"preview PART entered printable export: {spec.part}")
        if not spec.filename.endswith(".stl"):
            raise AssertionError(f"non-STL export filename: {spec.filename}")
        if not spec.definitions or spec.definitions[0] != f'PART="{spec.part}"':
            raise AssertionError(f"PART definition mismatch: {spec}")
        if spec.side is None:
            if spec.side_value is not None:
                raise AssertionError(f"side value without side label: {spec}")
        elif spec.side not in {"left", "right"} or spec.side_value not in {-1, 1}:
            raise AssertionError(f"invalid mirror metadata: {spec}")

def _manifest_entries(path: Path) -> dict[str, dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "0.1":
        raise AssertionError("unexpected print manifest schema version")
    if data.get("source") != "hardware/cad/net_stand.scad":
        raise AssertionError(f"manifest source changed: {data.get('source')}")
    if data.get("source_sha256") != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
        raise AssertionError("manifest source hash does not match net_stand.scad")
    if data.get("units") != "mm" or "免打孔" not in data.get("install_model", ""):
        raise AssertionError("manifest lost units or no-drill install boundary")
    components = data.get("assembly_components")
    if not isinstance(components, list) or not components:
        raise AssertionError("manifest 缺少装配物料清单")
    rod = next((item for item in components if item.get("id") == "printed-coarse-thread-rods"), None)
    if (
        not isinstance(rod, dict)
        or rod.get("scad_part") != "clamp_printed_screw"
        or rod.get("printable") is not True
        or "4 mm 螺距" not in str(rod.get("notes"))
        or "牙根宽约 2 mm" not in str(rod.get("notes"))
        or "凹槽宽约 2 mm" not in str(rod.get("notes"))
        or "0.4 mm 锥尖" not in str(rod.get("notes"))
        or "M8×1.25" not in str(rod.get("notes"))
    ):
        raise AssertionError("粗牙 PETG 螺杆必须作为可打印件进入中文物料清单")
    body_nut = next((item for item in components if item.get("id") == "printed-coarse-body-nuts"), None)
    drive_nuts = next((item for item in components if item.get("id") == "printed-coarse-drive-nuts"), None)
    if (
        not isinstance(body_nut, dict)
        or body_nut.get("scad_part") != "clamp_body_nut"
        or body_nut.get("printable") is not True
        or not isinstance(drive_nuts, dict)
        or drive_nuts.get("scad_part") != "clamp_knob_nut"
        or drive_nuts.get("printable") is not True
    ):
        raise AssertionError("粗牙 PETG 固定螺母和旋钮对锁螺母必须进入中文物料清单")
    net_clip = next((item for item in components if item.get("id") == "net-clamp-clips"), None)
    if (
        not isinstance(net_clip, dict)
        or net_clip.get("scad_part") != "net_clamp_clip"
        or net_clip.get("printable") is not True
        or "1.8" not in str(net_clip.get("notes"))
        or "张力" not in str(net_clip.get("notes"))
        or "止挡" not in str(net_clip.get("notes"))
        or "M3" in str(net_clip.get("notes"))
    ):
        raise AssertionError("全高 U 形卡网夹必须作为 PETG 可打印件出现在物料清单")
    if any(
        isinstance(item, dict) and item.get("id") == "net-clip-m3-hardware"
        for item in components
    ):
        raise AssertionError("无穿钉卡网夹不应再列出 M3 防滑脱硬件")
    c_scheme_components = {
        item.get("id")
        for item in components
        if isinstance(item, dict)
    } & {
        "c-scheme-retaining-fasteners",
        "c-scheme-detent-hardware",
    }
    if c_scheme_components != {
        "c-scheme-retaining-fasteners",
        "c-scheme-detent-hardware",
    }:
        raise AssertionError(
            "C 方案必须在 manifest 中列出连接螺钉和钢珠弹簧定位件: "
            f"{sorted(c_scheme_components)}"
        )

    entries = data.get("parts")
    if not isinstance(entries, list):
        raise AssertionError("manifest parts must be a list")
    result: dict[str, dict[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("file"), str):
            raise AssertionError("manifest contains a malformed part entry")
        filename = entry["file"]
        if filename in result:
            raise AssertionError(f"manifest contains duplicate file: {filename}")
        result[filename] = entry
    return result


def validate_manifest(path: Path) -> None:
    if not path.is_file():
        raise AssertionError(f"manifest not found: {path}")
    entries = _manifest_entries(path)
    expected_by_file = {spec.filename: spec for spec in EXPORT_SPECS}
    if set(entries) != set(expected_by_file):
        raise AssertionError(
            "manifest file set differs from export matrix: "
            f"missing={sorted(set(expected_by_file) - set(entries))}, "
            f"extra={sorted(set(entries) - set(expected_by_file))}"
        )

    for filename, spec in expected_by_file.items():
        entry = entries[filename]
        if entry.get("part") != spec.part:
            raise AssertionError(f"manifest PART mismatch for {filename}")
        if not isinstance(entry.get("name_zh"), str) or not entry["name_zh"]:
            raise AssertionError(f"manifest 缺少中文名称: {filename}")
        if entry.get("printable") is not True:
            raise AssertionError(f"打印清单条目必须标记 printable=true: {filename}")
        expected_material_group = material_group_for(spec.material)
        if entry.get("material_group") != expected_material_group:
            raise AssertionError(
                f"材料组不符合分盘策略: {filename} -> {entry.get('material_group')}"
            )
        if entry.get("definitions") != list(spec.definitions):
            raise AssertionError(f"manifest definitions mismatch for {filename}")
        if entry.get("units") != "mm":
            raise AssertionError(f"manifest units mismatch for {filename}")
        topology = entry.get("topology")
        if not isinstance(topology, dict) or topology.get("watertight_by_edge_topology") is not True:
            raise AssertionError(f"manifest topology is not watertight for {filename}")
        if not isinstance(entry.get("volume_mm3"), (int, float)) or entry["volume_mm3"] <= 0:
            raise AssertionError(f"manifest volume is not positive for {filename}")
        bounds = entry.get("bounds")
        if not isinstance(bounds, dict) or not all(
            isinstance(bounds.get(key), list) and len(bounds[key]) == 3
            for key in ("min", "max", "size")
        ):
            raise AssertionError(f"manifest bounds malformed for {filename}")
        if not (path.parent / filename).is_file():
            raise AssertionError(f"manifest STL missing for {filename}")

    actual_stl = {item.name for item in path.parent.glob("*.stl")}
    expected_stl = set(expected_by_file)
    extra_stl = sorted(actual_stl - expected_stl)
    if extra_stl:
        raise AssertionError(
            "print directory contains STL files outside manifest: "
            + ", ".join(extra_stl)
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT / "manifest.json",
        help="optional generated manifest to validate when present",
    )
    args = parser.parse_args()
    validate_export_specs()
    if args.manifest.is_file():
        validate_manifest(args.manifest)
        print(f"EXPORT_MATRIX_OK (41 specs, manifest={args.manifest})")
    else:
        print("EXPORT_MATRIX_OK (41 specs, manifest not present)")


if __name__ == "__main__":
    main()
