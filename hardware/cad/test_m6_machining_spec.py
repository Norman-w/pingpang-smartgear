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
    expected_parts = {"m6_machining_detector_body"}
    if set(parts) != expected_parts or any(
        entry["per_side"] != 1
        or entry["total"] != 2
        or entry["preview_is_printable"] is not True
        for entry in parts.values()
    ):
        raise AssertionError("current PETG/CNC part schedule changed")
    if parts["m6_machining_detector_body"]["blank_mm"] != [10, 56, 216]:
        raise AssertionError("rectangular PETG body envelope changed")

    sensors = spec["sensor_contract"]
    if (
        sensors["count_per_detector"] != 10
        or sensors["channel_pitch_mm"] != 20
        or sensors["height_schedule_mm"] != list(range(10, 191, 20))
        or sensors["body_blank_mm"] != [10, 56, 216]
        or sensors["body_global_min_mm"] != [761.25, -28, 144.5]
        or sensors["body_envelope_mm"] != [10, 56, 216]
        or sensors["body_envelope_global_min_mm"] != [761.25, -28, 144.5]
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
        or sensors["hex_pocket_af_mm"] != 8
        or sensors["hex_pocket_depth_local_axis_mm"] != 2.1
        or sensors["insertion_axis"] != "right x+ / left x- outward entry; outer gray hex captured by shallow pocket; hollow threaded optical barrel and one nut pass toward the smooth opposite body face"
        or sensors["lane_layout"] != "单列竖直安装，所有光学中心 y=0；主体为 x=10 mm 厚、y=56 mm 宽并居中 y=0；十路中心高度为 +10、+30…+190 mm，不采用旧的左右交错双列"
        or sensors["cable_pocketed_in_body"] is not False
        or sensors["sensor_optical_bore_d_mm"] != 3
        or sensors["optical_aperture_location"] != "M6 中空外丝筒的末端中心孔；灰色六角处不再画独立黑色光学面"
        or sensors["sensor_nut_count_per_channel"] != 1
        or sensors["sensor_nut_position"] != "主体平滑的另一侧表面；不嵌入主体；不使用打印固定螺丝"
        or sensors["thread_visible_after_body_mm"] != 6
    ):
        raise AssertionError("45-degree L-sensor contract changed")
    schedule = sensors["channel_schedule"]
    if schedule[0]["sensor_center_z_local_to_body_mm"] != 18:
        raise AssertionError("lowest channel local height changed")
    if schedule[-1]["sensor_center_z_local_to_body_mm"] != 198:
        raise AssertionError("highest channel local height changed")

    shell = spec["shell_contract"]
    if (
        shell["outer_envelope_mm"] != [37.4, 60.8, 222]
        or shell["split_axis"] != "x"
        or shell["split_x_global_mm"] != 766
        or shell["top_view_profile"]
        != "z+ 俯视：x- 光学端为正圆弧，x+ 线缆端为圆角矩形；中间仅为前后盖分型边界，不建连线"
        or shell["front_cap_length_x_mm"] != 18
        or shell["rear_corner_radius_mm"] != 4
        or shell["front_max_x_global_mm"] != 765.8
        or shell["rear_min_x_global_mm"] != 766.2
        or shell["parting_clearance_x_mm"] != 0.4
        or shell["top_entry"]
        != "前盖位于 x- 光学端并做正球弧、后盖位于 x+ 线缆端并做圆角矩形；后盖 x+ 背面中央（y=0、z 中心）适当增厚形成 M8 支撑 boss，主体位于两盖中间，前后盖均从主体 z+ 套入；底盖从 z- 贴合，左侧发射端按 x 镜像；球头 z- 接口由采购金属 90°连接器从最低端承接，连接器沿 x 直接连接网架立柱，不经过中间转接板，最终尺寸待真实器件首样复核"
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
    boss = shell["support_boss"]
    if (
        boss["min_global_mm"] != [782.4, -9, 234.5]
        or boss["max_global_mm"] != [796.4, 9, 270.5]
        or boss["length_x_mm"] != 14
        or boss["root_overlap_x_mm"] != 3
        or boss["depth_y_mm"] != 18
        or boss["height_z_mm"] != 36
        or boss["center_y_global_mm"] != 0
        or boss["hole_axis"] != "x- from the rear x+ face toward the optical side"
    ):
        raise AssertionError("centered rear-face boss contract changed")

    support = spec["support_contract"]
    if (
        support["type"] != "purchased 13 mm ballhead/gimbal"
        or support["posture"]
        != "vertical; its downward interface is carried by a separate purchased metal 90-degree connector"
        or support["boss_hole_axis"]
        != "x- from the rear cover boss toward the optical side"
        or support["boss_hole_d_mm"] != 8.6
        or support["boss_hole_depth_x_mm"] != 14
        or support["boss_hole_entry_x_global_mm"] != 796.4
        or support["ballhead_stud_engagement_x_mm"] != 12
        or support["ballhead_center_x_global_mm"] != 816.4
        or support["ballhead_center_y_global_mm"] != 0
        or support["ballhead_center_z_global_mm"] != 252.5
        or "球头 M8 竖直接口朝 z-" not in support["net_interface"]
        or "采购金属 90°连接器" not in support["load_path"]
    ):
        raise AssertionError("rear-cover boss/purchased ballhead interface contract changed")

    connector = support["net_connector"]
    if (
        connector["material"] != "purchased metal (not printed)"
        or connector["arm_min_x_global_mm"] != 809.4
        or connector["arm_max_x_global_mm"] != 889
        or connector["arm_width_y_mm"] != 24
        or connector["arm_thickness_z_mm"] != 10
        or connector["leg_min_x_global_mm"] != 881
        or connector["leg_max_x_global_mm"] != 889
        or connector["leg_width_y_mm"] != 32
        or connector["leg_thickness_x_mm"] != 8
        or connector["arm_bottom_z_global_mm"] != 203.5
        or connector["arm_top_z_global_mm"] != 213.5
        or connector["leg_bottom_z_global_mm"] != 203.5
        or connector["leg_top_z_global_mm"] != 262.5
        or connector["socket_bottom_z_global_mm"] != 203.3
        or connector["socket_top_z_global_mm"] != 231.7
        or connector["socket_outer_d_mm"] != 14
        or connector["socket_clearance_d_mm"] != 8.6
        or connector["ballhead_interface_bottom_z_global_mm"] != 203.5
        or connector["mount_height_from_interface_bottom_mm"] != 49
        or connector["post_bolt_pattern_y_mm"] != [-10, 10]
        or connector["post_bolt_d_mm"] != 6.5
        or connector["print_status"] != "preview-only purchased metal part; exclude from PETG STL"
    ):
        raise AssertionError("downward ballhead metal connector contract changed")

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

    print("M6_MACHINING_SPEC_TEST_OK (rectangular PETG body, downward ballhead connector, 10 rolled L-sensor channels at 20 mm pitch)")


if __name__ == "__main__":
    main()
