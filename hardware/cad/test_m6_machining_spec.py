#!/usr/bin/env python3
"""Validate the current 45-degree L-sensor machining handoff."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from export_m6_machining_spec import SCHEMA_VERSION, SOURCE, build_spec
from validate_scad import find_openscad


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="m6-machining-test-") as directory:
        spec = build_spec(find_openscad(), Path(directory))

    if spec["schema_version"] != SCHEMA_VERSION:
        raise AssertionError("unexpected M6 machining spec schema")
    if spec["source_sha256"] != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
        raise AssertionError("machining spec source hash mismatch")

    parts = {entry["part"]: entry for entry in spec["part_schedule"]}
    expected_parts = {
        "m6_machining_detector_body",
        "m6_machining_support",
        "m6_machining_adapter",
    }
    if set(parts) != expected_parts or any(
        entry["per_side"] != 1
        or entry["total"] != 2
        or entry["preview_is_printable"] is not False
        for entry in parts.values()
    ):
        raise AssertionError("current aluminum part schedule changed")
    if parts["m6_machining_detector_body"]["blank_mm"] != [10, 56, 216]:
        raise AssertionError("detector body blank changed")
    if parts["m6_machining_support"]["blank_mm"] != [109.75, 18, 60]:
        raise AssertionError("90-degree support envelope changed")
    if parts["m6_machining_adapter"]["blank_mm"] != [6, 56, 228]:
        raise AssertionError("vertical adapter envelope changed")

    sensors = spec["sensor_contract"]
    if (
        sensors["count_per_detector"] != 10
        or sensors["channel_pitch_mm"] != 20
        or sensors["height_schedule_mm"] != list(range(10, 191, 20))
        or sensors["body_blank_mm"] != [10, 56, 216]
        or sensors["body_global_min_mm"] != [761.25, -28, 144.5]
        or sensors["body_center_y_global_mm"] != 0
        or sensors["sensor_roll_deg"] != -45
        or sensors["body_depth_limit_from_stem_and_one_nut_mm"] != 10
        or sensors["body_depth_margin_mm"] != 0
        or sensors["horizontal_thread_section_length_mm"] != 14
        or sensors["horizontal_overall_package_length_mm"] != 20
        or sensors["cable_branch_local_axis"] != "z-"
        or sensors["cable_branch_roll_deg_about_x"] != -45
        or sensors["cable_guard_length_mm"] != 10
        or sensors["cable_d_mm"] != 3
        or sensors["hex_pocket_af_mm"] != 10.7
        or sensors["hex_pocket_depth_local_axis_mm"] != 2.5
        or sensors["insertion_axis"] != "right x+ / left x- outward entry; outer gray hex captured by shallow pocket; hollow threaded optical barrel and one nut pass toward the smooth opposite body face"
        or sensors["lane_layout"] != "单列竖直安装，所有光学中心 y=0；主体为 x=10 mm 厚、y=56 mm 宽并居中 y=0；十路中心高度为 +10、+30…+190 mm，不采用旧的左右交错双列"
        or sensors["cable_pocketed_in_body"] is not False
        or sensors["sensor_optical_bore_d_mm"] != 3
        or sensors["optical_aperture_location"] != "M6 中空外丝筒的末端中心孔；灰色六角处不再画独立黑色光学面"
        or sensors["sensor_nut_count_per_channel"] != 1
        or sensors["sensor_nut_position"] != "主体平滑的另一侧表面；不嵌入主体；不使用打印固定螺丝"
        or sensors["thread_visible_after_body_mm"] != 12.25
    ):
        raise AssertionError("45-degree L-sensor contract changed")
    schedule = sensors["channel_schedule"]
    if schedule[0]["sensor_center_z_local_to_body_mm"] != 18:
        raise AssertionError("lowest channel local height changed")
    if schedule[-1]["sensor_center_z_local_to_body_mm"] != 198:
        raise AssertionError("highest channel local height changed")

    shell = spec["shell_contract"]
    if shell["outer_envelope_mm"] != [24.8, 60.8, 222]:
        raise AssertionError("front/rear shell envelope changed")
    if shell["split_axis"] != "y" or shell["split_y_global_mm"] != 0 or shell["front_min_y_global_mm"] != -0.3 or shell["rear_max_y_global_mm"] != 0.3 or shell["top_entry"] != "前盖 y+ 为球弧、后盖 y- 为圆角矩形并带桥接 boss；主体位于中间，从主体 z+ 套入；侧边竖槽、底盖和沉头孔为当前装配候选，最终尺寸待真实器件首样复核":
        raise AssertionError("split-cover contract changed")

    ballhead = spec["ballhead_contract"]
    if ballhead["selected_variant"] != "13mm球【M6外牙】（当前模型默认）":
        raise AssertionError("ballhead default variant changed")
    if ballhead["alternative_variants"] != [
        "13mm球【1/4内牙】",
        "13mm球【1/4外牙】",
        "13mm球【3/8外牙】",
        "13mm球【M6外牙】",
        "13mm球【M8外牙】",
        "13mm球【M10外牙】",
    ]:
        raise AssertionError("ballhead variant list changed")

    print("M6_MACHINING_SPEC_TEST_OK (body/support/adapter, 10 rolled L-sensor channels at 20 mm pitch)")


if __name__ == "__main__":
    main()
