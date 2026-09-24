#!/usr/bin/env python3
"""Validate the current M6 first-article/CNC handoff contract."""

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
    if set(parts) != {"m6_machining_detector_body"}:
        raise AssertionError("current PETG/CNC part schedule changed")
    body = parts["m6_machining_detector_body"]
    if body["per_side"] != 1 or body["total"] != 2 or body["preview_is_printable"] is not True:
        raise AssertionError("current detector body quantity changed")
    if body["blank_mm"] != [10, 56, 216]:
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
        or sensors["cable_pocketed_in_body"] is not False
        or sensors["sensor_optical_bore_d_mm"] != 3
        or sensors["sensor_nut_count_per_channel"] != 1
        or sensors["thread_visible_after_body_mm"] != 6
        or sensors["installed_height_schedule_mm"] != list(range(39, 220, 20))
        or sensors["mount_raise_z_mm"] != 29
    ):
        raise AssertionError("45-degree L-sensor contract changed")
    if sensors["channel_schedule"][0]["sensor_center_z_local_to_body_mm"] != 18:
        raise AssertionError("lowest channel local height changed")
    if sensors["channel_schedule"][-1]["sensor_center_z_local_to_body_mm"] != 198:
        raise AssertionError("highest channel local height changed")

    shell = spec["shell_contract"]
    if (
        shell["outer_envelope_mm"] != [37.4, 60.8, 222]
        or shell["split_axis"] != "x"
        or shell["split_x_global_mm"] != 850.6
        or shell["front_cap_length_x_mm"] != 18
        or shell["rear_corner_radius_mm"] != 4
        or shell["parting_clearance_x_mm"] != 0.4
        or "下段从黄灰交界 z=16 mm 延伸到分型面 z=230.5 mm" not in shell["top_entry"]
        or "上段延伸到 z=260.5 mm" not in shell["top_entry"]
        or "四枚 M3×40" not in shell["top_entry"]
    ):
        raise AssertionError("split-cover contract changed")
    if shell["support_boss"]["min_global_mm"] != [867, -9, 263.5]:
        raise AssertionError("rear-cover boss lower datum changed")
    if shell["support_boss"]["max_global_mm"] != [881, 9, 299.5]:
        raise AssertionError("rear-cover boss upper datum changed")

    support = spec["support_contract"]
    if (
        support["type"] != "purchased 13 mm ballhead/gimbal"
        or "split fixed net post" not in support["posture"]
        or support["ballhead_center_z_global_mm"] != 281.5
        or support["mount_raise_z_mm"] != 29
        or "下段 z=16…230.5 mm、上段 z=230.5…260.5 mm" not in support["net_interface"]
        or "四枚 M3×40" not in support["net_interface"]
    ):
        raise AssertionError("rear-cover boss/purchased ballhead interface contract changed")

    direct_mount = support["direct_mount"]
    if (
        direct_mount["enabled"] is not True
        or direct_mount["lower_post_top_z_global_mm"] != 230.5
        or direct_mount["socket_bottom_z_global_mm"] != 230.5
        or direct_mount["socket_top_z_global_mm"] != 260.5
        or direct_mount["ballhead_interface_bottom_z_global_mm"] != 232.5
        or direct_mount["assembly_z_raise_mm"] != 29
        or direct_mount["print_status"]
        != "not integrated into post_clamp_carrier; fixed net post has no M8 optical hole; independent M6 support is pending and no direct-mount STL is released"
    ):
        raise AssertionError("direct ballhead-to-same-material-PETG-upper-post contract changed")

    net_retention = spec["net_retention_contract"]
    keeper = net_retention["passive_keeper"]
    if (
        net_retention["fixture_bottom_z_global_mm"] != 16
        or net_retention["post_top_z_global_mm"] != 260.5
        or net_retention["net_top_z_global_mm"] != 168.5
        or net_retention["printed_part"] != "net_clamp_rod"
        or net_retention["channel_width_y_mm"] != 15.2
        or net_retention["rod_d_mm"] != 10
        or net_retention["rod_axis_x_mm"] != 897.6
        or net_retention["rod_axis_y_mm"] != 0
        or net_retention["rod_sleeve_outer_d_mm"] != 12
        or net_retention["channel_void_x_span_mm"] != [890, 915.2]
        or keeper["enabled"] is not False
        or keeper["z_span_mm"] != []
        or keeper["x_span_mm"] != []
        or keeper["y_span_mm"] != []
        or "Ø10 mm 圆柱插杆" not in net_retention["assembly"]
        or "侧开接收腔" not in net_retention["assembly"]
        or "立柱上段与下段的四枚 M3×40 连接不属于网端插杆" not in net_retention["assembly"]
    ):
        raise AssertionError("printed cylindrical net-retention contract changed")

    ballhead = spec["ballhead_contract"]
    if (
        ballhead["selected_variant"] != "13mm球【M8外牙】（当前模型默认）"
        or ballhead["sensor_stud_d_mm"] != 6.35
        or ballhead["net_stud_d_mm"] != 8
        or ballhead["net_stud_role"]
        != "当前选定下端 M8 外牙；z- 仅作独立光学支撑接口包络，当前不进入固定网柱"
    ):
        raise AssertionError("ballhead default variant changed")

    print("M6_MACHINING_SPEC_TEST_OK (rectangular PETG body, split fixed post, independent M6 support pending, 10 rolled L-sensor channels at 20 mm pitch)")


if __name__ == "__main__":
    main()
