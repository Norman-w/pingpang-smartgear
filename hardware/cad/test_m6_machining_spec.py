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
        or "固定网柱从黄灰交界 z=16 mm 一体延伸到 z=372.5 mm"
        not in shell["top_entry"]
        or "底端不进入 C 形座" not in shell["top_entry"]
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
        or boss["gusset_min_global_mm"] != [866.8, -30.4, 266.5]
        or boss["gusset_max_global_mm"] != [870.2, 30.4, 278.5]
        or boss["gusset_x_overlap_mm"] != 0.2
        or boss["gusset_root_width_y_mm"] != 5
        or boss["gusset_wall_width_y_mm"] != 2.4
        or boss["gusset_height_z_mm"] != 12
        or boss["gusset_root_y_start_positive_mm"] != 4
        or boss["gusset_wall_y_start_positive_mm"] != 28
        or boss["hole_axis"] != "x- from the rear x+ face toward the optical side"
    ):
        raise AssertionError("centered rear-face boss contract changed")

    support = spec["support_contract"]
    if (
        support["type"] != "purchased 13 mm ballhead/gimbal"
        or support["posture"]
        != "vertical purchased ballhead on the M6 rear-cover boss; its downward M8 interface is a standalone optical-support envelope and is not connected to the fixed full-height post"
        or support["boss_hole_axis"]
        != "x- from the rear cover boss toward the optical side"
        or support["boss_hole_d_mm"] != 7
        or support["boss_hole_depth_x_mm"] != 14
        or support["boss_hole_entry_x_global_mm"] != 881
        or support["ballhead_stud_engagement_x_mm"] != 12
        or support["ballhead_center_x_global_mm"] != 901
        or support["ballhead_center_y_global_mm"] != 0
        or support["ballhead_center_z_global_mm"] != 272.5
        or support["mount_raise_z_mm"] != 20
        or "球头下端 M8 外牙接口朝 z-" not in support["net_interface"]
        or "不进入固定网柱" not in support["net_interface"]
        or "固定网柱从 z=16 mm 一体延伸到 z=372.5 mm" not in support["net_interface"]
        or "无旧版横向承托臂" not in support["load_path"]
        or "无旧版独立连接器" not in support["load_path"]
    ):
        raise AssertionError("rear-cover boss/purchased ballhead interface contract changed")

    direct_mount = support["direct_mount"]
    if (
        direct_mount["enabled"] is not False
        or direct_mount["material"] != "disabled; independent optical support pending"
        or direct_mount["interface_orientation"]
        != "standalone vertical M8 envelope; not connected to the fixed net post; no active top arm"
        or direct_mount["assembly_x_offset_mm"] != 84.6
        or direct_mount["assembled_ballhead_center_x_global_mm"] != 901
        or direct_mount["assembled_optical_axis_x_global_mm"] != 839.85
        or direct_mount["socket_center_x_global_mm"] != 901
        or direct_mount["arm_min_x_global_mm"] != 901
        or direct_mount["arm_max_x_global_mm"] != 901
        or direct_mount["arm_width_y_mm"] != 0
        or direct_mount["arm_thickness_z_mm"] != 0
        or direct_mount["web_min_x_global_mm"] != 887
        or direct_mount["web_max_x_global_mm"] != 887
        or direct_mount["web_width_y_mm"] != 0
        or direct_mount["web_thickness_x_mm"] != 0
        or direct_mount["web_min_z_global_mm"] != 372.5
        or direct_mount["web_max_z_global_mm"] != 372.5
        or direct_mount["socket_bottom_z_global_mm"] != 221.5
        or direct_mount["socket_top_z_global_mm"] != 251.5
        or direct_mount["socket_height_z_mm"] != 30
        or direct_mount["socket_outer_d_mm"] != 24
        or direct_mount["socket_tap_d_mm"] != 6.8
        or direct_mount["socket_clearance_d_mm"] != 8.6
        or direct_mount["socket_base_overlap_z_mm"] != 0
        or direct_mount["nut_loading_clearance_z_mm"] != 0
        or direct_mount["captured_nut_pocket_af_mm"] != 0
        or direct_mount["captured_nut_pocket_depth_z_mm"] != 0
        or direct_mount["captured_nut_pocket_bottom_z_global_mm"] != 221.5
        or direct_mount["captured_nut_pocket_center_z_global_mm"] != 221.5
        or direct_mount["nut_loading_depth_z_mm"] != 0
        or direct_mount["ballhead_interface_bottom_z_global_mm"] != 223.5
        or direct_mount["lower_post_top_z_global_mm"] != 372.5
        or direct_mount["assembly_z_raise_mm"] != 20
        or direct_mount["print_status"]
        != "not integrated into post_clamp_carrier; fixed net post has no M8 optical hole; independent M6 support is pending and no direct-mount STL is released"
    ):
        raise AssertionError("direct ballhead-to-same-material-PETG-upper-post contract changed")

    net_retention = spec["net_retention_contract"]
    if net_retention != {
        "fixture_bottom_z_global_mm": 16,
        "post_top_z_global_mm": 372.5,
        "net_top_z_global_mm": 168.5,
        "channel_opening": "右侧外侧 x+、左侧镜像后外侧 x-；俯视保留 U 形承力截面，外侧开口允许整高卡夹滑入",
        "channel_depth_x_mm": 25,
        "clip_receiver_depth_x_mm": 25,
        "channel_back_wall_t_x_mm": 3,
        "channel_width_y_mm": 8,
        "net_passage_width_y_mm": 3,
        "net_passage_clearance_each_side_y_mm": 0.9,
        "net_passage_x_span_mm": [881.8, 920.2],
        "net_passage_z_span_mm": [16, 168.5],
        "channel_z_span_mm": [16, 168.5],
        "passive_keeper": {
            "enabled": True,
            "role": "立柱一体内嵌止挡，仅防止卡夹向外拔出，不承担网布/绳张力主路径",
            "z_span_mm": [88, 96],
            "x_span_mm": [894.7, 895.7],
            "y_span_mm": [2.4, 4.4],
            "clip_relief_x_span_mm": [893, 897.4],
            "clip_relief_y_span_mm": [2.25, 3.45],
            "clip_one_way_latch": {
                "type": "卡夹正侧 jaw 一体弹性扣舌；斜面允许装入，闭合肩只阻止向外拔出",
                "x_span_mm": [893.4, 894.4],
                "y_span_mm": [2.05, 3.05],
                "z_span_mm": [88.4, 95.6],
                "installed_clearance_to_keeper_x_mm": 0.3,
            },
        },
        "printed_part": "net_clamp_clip",
        "material": "PETG",
        "assembly": "网布先沿 x 穿过立柱主体 y 向 3 mm 过道，端部止在立柱外表面；整高 U 形卡夹沿 x 从桌外侧滑入，两片 jaw 夹住网布；网布张力和绳的拉力把卡夹压在承托面上，立柱内嵌单一被动止挡只防向外拔出，无穿钉，按开夹爪即可解锁",
    }:
        raise AssertionError("printed U-slot net-retention contract changed")

    ballhead = spec["ballhead_contract"]
    if (
        ballhead["selected_variant"] != "13mm球【M8外牙】（当前模型默认）"
        or ballhead["sensor_stud_d_mm"] != 6.35
        or ballhead["net_stud_d_mm"] != 8
        or ballhead["sensor_stud_role"]
        != "商品固定上端 1/4-20 外牙；沿 x 接入后盖隐藏的 1/4-20 捕获螺母"
        or ballhead["net_stud_role"]
        != "当前选定下端 M8 外牙；z- 仅作独立光学支撑接口包络，当前不进入固定网柱"
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

    print("M6_MACHINING_SPEC_TEST_OK (rectangular PETG body, full-height fixed post with independent M6 support pending, 10 rolled L-sensor channels at 20 mm pitch)")


if __name__ == "__main__":
    main()
