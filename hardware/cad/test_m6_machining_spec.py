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
        or sensors["body_global_min_mm"] != [845.85, -28, 144.5]
        or sensors["body_envelope_mm"] != [10, 56, 216]
        or sensors["body_envelope_global_min_mm"] != [845.85, -28, 144.5]
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
        or sensors["lane_layout"] != "单列竖直安装，所有光学中心 y=0；主体为 x=10 mm 厚、y=56 mm 宽并居中 y=0；原始通道高度为 +10、+30…+190 mm，安装总成上抬 20 mm 后为 +30、+50…+210 mm，不采用旧的左右交错双列"
        or sensors["cable_pocketed_in_body"] is not False
        or sensors["sensor_optical_bore_d_mm"] != 3
        or sensors["optical_aperture_location"] != "M6 中空外丝筒的末端中心孔；灰色六角处不再画独立黑色光学面"
        or sensors["sensor_nut_count_per_channel"] != 1
        or sensors["sensor_nut_position"] != "主体平滑的另一侧表面；不嵌入主体；不使用打印固定螺丝"
        or sensors["thread_visible_after_body_mm"] != 6
        or sensors["installed_height_schedule_mm"] != list(range(30, 211, 20))
        or sensors["mount_raise_z_mm"] != 20
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
        or shell["split_x_global_mm"] != 850.6
        or shell["top_view_profile"]
        != "z+ 俯视：x- 光学端为正圆弧，x+ 线缆端仅后部圆角、x- 接驳边为直角；中间仅为前后盖分型边界，不建连线"
        or shell["front_cap_length_x_mm"] != 18
        or shell["rear_corner_radius_mm"] != 4
        or shell["front_max_x_global_mm"] != 850.4
        or shell["rear_min_x_global_mm"] != 850.8
        or shell["parting_clearance_x_mm"] != 0.4
        or shell["top_entry"]
        != "前盖位于 x- 光学端并做正球弧、后盖位于 x+ 线缆端且只在自身后部做圆角，和前盖接驳的 x- 边保持直角；后盖 x+ 背面中央（y=0、z 中心）适当增厚形成 M8 支撑 boss，主体位于两盖中间，前后盖均从主体 z+ 套入；底盖从 z- 贴合，左侧发射端按 x 镜像；球头 z- 接口直接拧入浅黄色直立下段顶面的一体 M8 承座，球头与立柱中心同轴，检测器/球头总成沿 x 移到立柱中心，取消横向黄色承托臂，当前装配取消深黄色上段和深灰色独立连接器，最终尺寸待真实器件首样复核"
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
        boss["min_global_mm"] != [867, -9, 254.5]
        or boss["max_global_mm"] != [881, 9, 290.5]
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
        != "vertical; its downward interface screws directly into the integrated light-yellow straight lower post at the post centre"
        or support["boss_hole_axis"]
        != "x- from the rear cover boss toward the optical side"
        or support["boss_hole_d_mm"] != 8.6
        or support["boss_hole_depth_x_mm"] != 14
        or support["boss_hole_entry_x_global_mm"] != 881
        or support["ballhead_stud_engagement_x_mm"] != 12
        or support["ballhead_center_x_global_mm"] != 901
        or support["ballhead_center_y_global_mm"] != 0
        or support["ballhead_center_z_global_mm"] != 272.5
        or support["mount_raise_z_mm"] != 20
        or "球头 M8 竖直接口朝 z-" not in support["net_interface"]
        or "直接拧入浅黄色直立下段顶面的一体 M8 承座" not in support["net_interface"]
        or "球头与立柱中心同轴" not in support["net_interface"]
        or "无横向黄色承托臂" not in support["load_path"]
        or "无深灰色独立连接器" not in support["load_path"]
    ):
        raise AssertionError("rear-cover boss/purchased ballhead interface contract changed")

    direct_mount = support["direct_mount"]
    if (
        direct_mount["material"] != "integrated light-yellow PETG lower stand"
        or direct_mount["interface_orientation"]
        != "vertical M8 tap axis coaxial with the straight lower post; no horizontal top arm"
        or direct_mount["assembly_x_offset_mm"] != 84.6
        or direct_mount["assembled_ballhead_center_x_global_mm"] != 901
        or direct_mount["assembled_optical_axis_x_global_mm"] != 847.6
        or direct_mount["socket_center_x_global_mm"] != 901
        or direct_mount["arm_min_x_global_mm"] != 901
        or direct_mount["arm_max_x_global_mm"] != 901
        or direct_mount["arm_width_y_mm"] != 0
        or direct_mount["arm_thickness_z_mm"] != 0
        or direct_mount["web_min_x_global_mm"] != 887
        or direct_mount["web_max_x_global_mm"] != 887
        or direct_mount["web_width_y_mm"] != 0
        or direct_mount["web_thickness_x_mm"] != 0
        or direct_mount["web_min_z_global_mm"] != 223.5
        or direct_mount["web_max_z_global_mm"] != 223.5
        or direct_mount["socket_bottom_z_global_mm"] != 223.3
        or direct_mount["socket_top_z_global_mm"] != 252
        or direct_mount["socket_height_z_mm"] != 28.7
        or direct_mount["socket_outer_d_mm"] != 18
        or direct_mount["socket_tap_d_mm"] != 6.8
        or direct_mount["ballhead_interface_bottom_z_global_mm"] != 223.5
        or direct_mount["lower_post_top_z_global_mm"] != 223.5
        or direct_mount["assembly_z_raise_mm"] != 20
        or direct_mount["print_status"]
        != "integrated into lower_stand_segment; vertical post-centred socket only; no horizontal arm or separate connector STL"
    ):
        raise AssertionError("direct ballhead-to-light-yellow lower-stand contract changed")

    net_retention = spec["net_retention_contract"]
    if net_retention != {
        "post_top_z_global_mm": 223.5,
        "channel_opening": "右侧外侧 x+、左侧镜像后外侧 x-；俯视保留 U 形承力截面",
        "channel_depth_x_mm": 28,
        "cylinder_insertion_depth_x_mm": 28,
        "channel_back_wall_t_x_mm": 3,
        "channel_width_y_mm": 15.2,
        "net_passage_width_y_mm": 3,
        "net_passage_clearance_each_side_y_mm": 0.9,
        "net_passage_x_span_mm": [881.8, 920.2],
        "net_passage_z_span_mm": [0, 152.5],
        "channel_z_span_mm": [0, 152.5],
        "interference_cylinder_d_mm": 14,
        "printed_cylinder_d_mm": 12,
        "diameter_reduction_mm": 2,
        "printed_part": "net_clamp_rod",
        "material": "PETG",
        "assembly": "网布先沿 x 穿过立柱主体 y 向 3 mm 过道，再从外侧塞入 U 槽；独立打印圆柱沿 x 推入并卡住；不使用采购圆柱",
    }:
        raise AssertionError("printed U-slot net-retention contract changed")

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

    print("M6_MACHINING_SPEC_TEST_OK (rectangular PETG body, direct light-yellow lower-stand ballhead mount, 10 rolled L-sensor channels at 20 mm pitch)")


if __name__ == "__main__":
    main()
