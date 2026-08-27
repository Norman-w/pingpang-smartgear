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
    "lower_stand_segment": 2,
    "net_clamp_rod": 2,
    "clamp_pressure_pad": 2,
    "clamp_knob": 2,
    "net_rail_segment": 3,
    "net_rail_splice": 2,
    "net_rail_saddle": 2,
    "sensor_mount_body": 2,
    "sensor_clamp_lip": 2,
    "calibration_gauge": 1,
}

PREVIEW_ONLY_PARTS = {
    "assembly",
    "left_stand",
    "right_stand",
    "post",
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
    "post_segment",
    "post_joint_sleeve",
    "post_joint_key",
    "m6_detector_net_connector",
}


def validate_export_specs() -> None:
    if len(EXPORT_SPECS) != 20:
        raise AssertionError(f"expected 20 printable exports, got {len(EXPORT_SPECS)}")
    filenames = [spec.filename for spec in EXPORT_SPECS]
    if len(set(filenames)) != len(filenames):
        raise AssertionError("printable export filenames must be unique")
    counts = Counter(spec.part for spec in EXPORT_SPECS)
    if counts != Counter(EXPECTED_COUNTS):
        raise AssertionError(f"printable PART matrix changed: {counts}")
    removed = sorted(REMOVED_ACTIVE_PARTS & set(counts))
    if removed:
        raise AssertionError(f"removed upper/connector parts re-entered print matrix: {removed}")

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
    rod = next((item for item in components if item.get("id") == "m8-threaded-rod"), None)
    if not isinstance(rod, dict) or rod.get("name_zh") != "M8×1.25 金属螺杆" or rod.get("printable") is not False:
        raise AssertionError("M8 金属螺杆必须作为中文外购/非打印件出现在物料清单")
    net_rod = next((item for item in components if item.get("id") == "net-clamp-rods"), None)
    if (
        not isinstance(net_rod, dict)
        or net_rod.get("scad_part") != "net_clamp_rod"
        or net_rod.get("printable") is not True
        or "Ø12" not in str(net_rod.get("notes"))
    ):
        raise AssertionError("卡网圆柱必须作为 PETG 可打印件出现在物料清单")

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
        print(f"EXPORT_MATRIX_OK (20 specs, manifest={args.manifest})")
    else:
        print("EXPORT_MATRIX_OK (20 specs, manifest not present)")


if __name__ == "__main__":
    main()
