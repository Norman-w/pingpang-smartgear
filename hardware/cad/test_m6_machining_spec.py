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
    if parts["m6_machining_support"]["blank_mm"] != [101.7, 18, 60]:
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
    if (
        shell["outer_envelope_mm"] != [24.8, 60.8, 222]
        or shell["split_axis"] != "x"
        or shell["split_x_global_mm"] != 766
        or shell["front_max_x_global_mm"] != 766.3
        or shell["rear_min_x_global_mm"] != 765.7
        or shell["top_entry"]
        != "前盖位于 x- 光学端并做正球弧、后盖位于 x+ 线缆端并做圆角矩形；后盖 y- 外侧带 M8 金属桥接 boss；主体位于两盖中间，前后盖均从主体 z+ 套入；底盖从 z- 贴合，最终尺寸待真实器件首样复核"
    ):
        raise AssertionError("split-cover contract changed")
    grooves = shell["shared_edge_grooves"]
    if grooves != {
        "width_x_mm": 4,
        "depth_y_mm": 1.2,
        "margin_z_mm": 5,
        "tongue_clearance_mm": 0.25,
        "ownership": "前盖占 x- 半、后盖占 x+ 半；两盖共享 y± 两条连续竖槽",
    }:
        raise AssertionError("shared edge-groove contract changed")

    support = spec["support_contract"]
    if (
        support["thread_nominal_d_mm"] != 8
        or support["metal_insert_d_mm"] != 12
        or support["metal_insert_length_x_mm"] != 16
        or support["printed_boss_clearance_d_mm"] != 8.6
        or "后盖 boss -> 90°金属支撑水平臂" not in support["load_path"]
    ):
        raise AssertionError("M8 metal bridge contract changed")

    ballhead = spec["ballhead_contract"]
    if (
        ballhead["selected_variant"] != "13mm球【M8外牙】（当前模型默认）"
        or ballhead["sensor_stud_d_mm"] != 8
        or ballhead["net_stud_d_mm"] != 8
    ):
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
