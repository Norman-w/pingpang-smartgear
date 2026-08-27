#!/usr/bin/env python3
"""Keep the dependency-free intent preview aligned with the SCAD source."""

from __future__ import annotations

import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCAD = HERE / "net_stand.scad"
PREVIEW = HERE / "preview.py"
PREVIEW_INDEX = HERE / "preview" / "index.html"
PREVIEW_APP = HERE / "preview" / "app.js"

# These are the direct, first-article geometry values that the lightweight
# preview must mirror. Derived coordinates are intentionally checked by the
# OpenSCAD validator; this test prevents the two visual entry points from
# silently diverging on the design boundary itself.
PARAMETER_MAP = {
    "TABLE_WIDTH": "table_width",
    "TABLE_THICKNESS": "table_thickness",
    "NET_POST_OUTBOARD_EXTENSION": "net_post_outboard_extension",
    "POST_OFFSET": "post_offset",
    "POST_WIDTH": "post_body_width",
    "CLAMP_OUTER_EXTENSION": "clamp_outer_extension",
    "CLAMP_REACH_INBOARD": "clamp_reach_inboard",
    "CLAMP_PAD_T": "clamp_pad_t",
    "CLAMP_CLEARANCE": "clamp_clearance",
    "CLAMP_SCREW_INSET": "clamp_screw_inset",
    "CLAMP_KNOB_D": "clamp_knob_d",
    "CLAMP_KNOB_H": "clamp_knob_h",
    "CLAMP_SCREW_TO_KNOB_TOP_BASE": "clamp_screw_to_knob_top_base",
    "CLAMP_SCREW_EXTRA_LENGTH_Z": "clamp_screw_extra_length_z",
    "CLAMP_NUT_AF": "clamp_nut_af",
    "CLAMP_NUT_H": "clamp_nut_h",
    "CLAMP_NUT_CLEARANCE": "clamp_nut_clearance",
    "CLAMP_KNOB_NUT_GAP": "clamp_knob_nut_gap",
    "CLAMP_LOWER_ARM_CLEARANCE": "clamp_lower_arm_clearance",
    "CLAMP_REINFORCEMENT_INBOARD_OFFSET_X": "clamp_reinforcement_inboard_offset_x",
    "CLAMP_REINFORCEMENT_NEAR_TABLE_THICKNESS_Z": "clamp_reinforcement_near_table_thickness_z",
    "CLAMP_REINFORCEMENT_DEPTH_Y": "clamp_reinforcement_depth_y",
    "CLAMP_SOLID_BRIDGE_CLEARANCE_X": "clamp_solid_bridge_clearance_x",
    "CLAMP_PRESSURE_PAD_WIDTH": "clamp_pressure_pad_width",
    "CLAMP_PRESSURE_PAD_T": "clamp_pressure_pad_t",
    "M6_SENSOR_HEAD_LENGTH_X": "m6_sensor_head_length_x",
    "M6_SENSOR_HEAD_WIDTH_Y": "m6_sensor_head_width_y",
    "M6_SENSOR_HEAD_HEIGHT_Z": "m6_sensor_head_height_z",
    "M6_SENSOR_HEAD_HEX_AF": "m6_sensor_head_hex_af",
    "M6_SENSOR_CENTER_PITCH": "m6_sensor_center_pitch",
    "M6_SENSOR_BODY_LENGTH": "m6_sensor_body_length",
    "M6_SENSOR_MOUNT_STEM_LENGTH": "m6_sensor_mount_stem_length",
    "M6_RAIL_T": "m6_rail_t",
    "M6_RAIL_WIDTH_Y": "m6_rail_width_y",
    "M6_RAIL_TAB_T": "m6_rail_tab_t",
    "M6_RAIL_TAB_WIDTH_Y": "m6_rail_tab_width_y",
    "M6_SENSOR_LANE_OFFSET_Y": "m6_sensor_lane_offset_y",
    "M6_YAW_STAGE_T": "m6_yaw_stage_t",
    "M6_YAW_STAGE_RADIUS": "m6_yaw_stage_radius",
    "M6_YAW_SLOT_RADIUS": "m6_yaw_slot_radius",
    "M6_PITCH_YOKE_T": "m6_pitch_yoke_t",
    "M6_PITCH_YOKE_WIDTH_Y": "m6_pitch_yoke_width_y",
    "M6_PITCH_FRAME_T": "m6_pitch_frame_t",
    "M6_PITCH_FRAME_OUTER_WIDTH_Y": "m6_pitch_frame_outer_width_y",
    "M6_PITCH_FRAME_WINDOW_WIDTH_Y": "m6_pitch_frame_window_width_y",
    "M6_PITCH_FRAME_OUTER_HEIGHT_Z": "m6_pitch_frame_outer_height_z",
    "M6_PITCH_FRAME_WINDOW_HEIGHT_Z": "m6_pitch_frame_window_height_z",
    "M6_ROLL_PLATE_D": "m6_roll_plate_d",
    "M6_ROLL_PIVOT_D": "m6_roll_pivot_d",
    "M6_SENSOR_ROLL_DEG": "m6_sensor_roll_deg",
    "M6_DETECTOR_BODY_DEPTH_Y": "m6_detector_body_depth_y",
    "M6_DETECTOR_BODY_CENTER_Y": "m6_detector_body_center_y",
    "M6_DETECTOR_BODY_LENGTH_X": "m6_detector_body_length_x",
    "M6_DETECTOR_BODY_MARGIN_Z": "m6_detector_body_margin_z",
    "M6_DETECTOR_BODY_FRONT_MARGIN_X": "m6_detector_body_front_margin_x",
    "M6_DETECTOR_SHELL_WALL": "m6_detector_shell_wall",
    "M6_DETECTOR_SHELL_CLEARANCE": "m6_detector_shell_clearance",
    "M6_DETECTOR_SHELL_BOTTOM_LIP_Z": "m6_detector_shell_bottom_lip_z",
    "M6_DETECTOR_SHELL_TOP_LIP_Z": "m6_detector_shell_top_lip_z",
    "M6_DETECTOR_SHELL_SPLIT_OVERLAP_X": "m6_detector_shell_split_overlap_x",
    "M6_DETECTOR_SHELL_CORNER_RADIUS": "m6_detector_shell_corner_radius",
    "M6_DETECTOR_FRONT_CAP_LENGTH_X": "m6_detector_front_cap_length_x",
    "M6_DETECTOR_FRONT_CAP_REDUCTION": "m6_detector_front_cap_reduction",
    "M6_DETECTOR_BODY_GROOVE_WIDTH_X": "m6_detector_body_groove_width_x",
    "M6_DETECTOR_BODY_GROOVE_DEPTH_Y": "m6_detector_body_groove_depth_y",
    "M6_DETECTOR_BODY_GROOVE_MARGIN_Z": "m6_detector_body_groove_margin_z",
    "M6_DETECTOR_SHELL_TONGUE_DEPTH_Y": "m6_detector_shell_tongue_depth_y",
    "M6_DETECTOR_SHELL_TONGUE_CLEARANCE": "m6_detector_shell_tongue_clearance",
    "M6_DETECTOR_OPTICAL_BORE_D": "m6_detector_optical_bore_d",
    "M6_DETECTOR_THREAD_CLEARANCE_D": "m6_detector_thread_clearance_d",
    "M6_DETECTOR_HEX_POCKET_DEPTH_X": "m6_detector_hex_pocket_depth_x",
    "M6_DETECTOR_HEX_POCKET_FLOOR": "m6_detector_hex_pocket_floor",
    "M6_DETECTOR_SHELL_SCREW_PILOT_D": "m6_detector_shell_screw_pilot_d",
    "M6_DETECTOR_SHELL_SCREW_HEAD_D": "m6_detector_shell_screw_head_d",
    "M6_DETECTOR_SHELL_SCREW_HEAD_DEPTH": "m6_detector_shell_screw_head_depth",
    "M6_DETECTOR_SHELL_SCREW_MARGIN_Z": "m6_detector_shell_screw_margin_z",
    "M6_DETECTOR_BOTTOM_COVER_T": "m6_detector_bottom_cover_t",
    "M6_BOTTOM_COVER_SCREW_DEPTH": "m6_bottom_cover_screw_depth",
    "M6_DETECTOR_BOTTOM_COVER_SCREW_D": "m6_detector_bottom_cover_screw_d",
    "M6_DETECTOR_BOTTOM_COVER_SCREW_HEAD_D": "m6_detector_bottom_cover_screw_head_d",
    "M6_DETECTOR_BOTTOM_COVER_SCREW_HEAD_DEPTH": "m6_detector_bottom_cover_screw_head_depth",
    "M6_DETECTOR_BOTTOM_COVER_SCREW_INSET_X": "m6_detector_bottom_cover_screw_inset_x",
    "M6_DETECTOR_CABLE_EXIT_D": "m6_detector_cable_exit_d",
    "M6_DETECTOR_CABLE_EXIT_SLEEVE_CLEARANCE": "m6_detector_cable_exit_sleeve_clearance",
    "M6_DETECTOR_SHELL_SUPPORT_BOSS_LENGTH_X": "m6_detector_shell_support_boss_length_x",
    "M6_DETECTOR_SHELL_SUPPORT_BOSS_OVERLAP_X": "m6_detector_shell_support_boss_overlap_x",
    "M6_DETECTOR_SHELL_SUPPORT_BOSS_DEPTH_Y": "m6_detector_shell_support_boss_depth_y",
    "M6_DETECTOR_SHELL_SUPPORT_BOSS_HEIGHT_Z": "m6_detector_shell_support_boss_height_z",
    "M6_DETECTOR_SHELL_SUPPORT_BOSS_RADIUS": "m6_detector_shell_support_boss_radius",
    "M6_DETECTOR_SHELL_SUPPORT_HOLE_D": "m6_detector_shell_support_hole_d",
    "M6_DETECTOR_SHELL_SUPPORT_HOLE_DEPTH_X": "m6_detector_shell_support_hole_depth_x",
    "M6_DETECTOR_SHELL_SUPPORT_STUD_ENGAGEMENT_X": "m6_detector_shell_support_stud_engagement_x",
    "M6_DETECTOR_DETECTOR_BALLHEAD_GAP_X": "m6_detector_detector_ballhead_gap_x",
    "M6_DETECTOR_SENSOR_HEAD_Y_OFFSET": "m6_detector_sensor_head_y_offset",
    "M6_DETECTOR_DIRECT_MOUNT_ARM_WIDTH_Y": "m6_detector_direct_mount_arm_width_y",
    "M6_DETECTOR_DIRECT_MOUNT_ARM_T_Z": "m6_detector_direct_mount_arm_t_z",
    "M6_DETECTOR_DIRECT_MOUNT_WEB_WIDTH_Y": "m6_detector_direct_mount_web_width_y",
    "M6_DETECTOR_DIRECT_MOUNT_WEB_T_X": "m6_detector_direct_mount_web_t_x",
    "M6_DETECTOR_DIRECT_MOUNT_POST_OVERLAP_X": "m6_detector_direct_mount_post_overlap_x",
    "M6_DETECTOR_DIRECT_MOUNT_SOCKET_OUTER_D": "m6_detector_direct_mount_socket_outer_d",
    "M6_DETECTOR_DIRECT_MOUNT_SOCKET_TAP_D": "m6_detector_direct_mount_socket_tap_d",
    "M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_CLEARANCE_Z": "m6_detector_direct_mount_socket_bottom_clearance_z",
    "M6_DETECTOR_DIRECT_MOUNT_SOCKET_TOP_CLEARANCE_Z": "m6_detector_direct_mount_socket_top_clearance_z",
}

BROWSER_PARAMETER_MAP = {
    "mountRaiseZ": "M6_DETECTOR_MOUNT_RAISE_Z",
    "netPassageWidthY": "NET_PASSAGE_WIDTH_Y",
    "sensorPitch": "M6_SENSOR_CENTER_PITCH",
    "sensorRollDeg": "M6_SENSOR_ROLL_DEG",
    "bodyCenterY": "M6_DETECTOR_BODY_CENTER_Y",
    "bodyDepthY": "M6_DETECTOR_BODY_DEPTH_Y",
    "headHexAF": "M6_SENSOR_HEAD_HEX_AF",
    "hexPocketDepthX": "M6_DETECTOR_HEX_POCKET_DEPTH_X",
    "cableExitD": "M6_DETECTOR_CABLE_EXIT_D",
    "shellSupportBossLengthX": "M6_DETECTOR_SHELL_SUPPORT_BOSS_LENGTH_X",
    "shellSupportBossOverlapX": "M6_DETECTOR_SHELL_SUPPORT_BOSS_OVERLAP_X",
    "shellSupportBossDepthY": "M6_DETECTOR_SHELL_SUPPORT_BOSS_DEPTH_Y",
    "shellSupportBossHeightZ": "M6_DETECTOR_SHELL_SUPPORT_BOSS_HEIGHT_Z",
    "shellSupportBossRadius": "M6_DETECTOR_SHELL_SUPPORT_BOSS_RADIUS",
    "shellSupportHoleD": "M6_DETECTOR_SHELL_SUPPORT_HOLE_D",
    "shellSupportHoleDepthX": "M6_DETECTOR_SHELL_SUPPORT_HOLE_DEPTH_X",
    "shellSupportStudEngagementX": "M6_DETECTOR_SHELL_SUPPORT_STUD_ENGAGEMENT_X",
    "ballheadBallD": "M6_BALLHEAD_BALL_D",
    "ballheadHousingD": "M6_BALLHEAD_HOUSING_D",
    "ballheadHousingLength": "M6_BALLHEAD_HOUSING_LENGTH_X",
    "ballheadBaseD": "M6_BALLHEAD_BASE_D",
    "ballheadBaseT": "M6_BALLHEAD_BASE_T",
    "ballheadSensorStudD": "M6_BALLHEAD_SENSOR_STUD_D",
    "ballheadNetStudD": "M6_BALLHEAD_NET_STUD_D",
    "ballheadTiltDeg": "M6_BALLHEAD_TILT_RANGE_DEG",
    "ballheadRotationDeg": "M6_BALLHEAD_ROTATION_RANGE_DEG",
    "directMountArmWidthY": "M6_DETECTOR_DIRECT_MOUNT_ARM_WIDTH_Y",
    "directMountArmThicknessZ": "M6_DETECTOR_DIRECT_MOUNT_ARM_T_Z",
    "directMountWebWidthY": "M6_DETECTOR_DIRECT_MOUNT_WEB_WIDTH_Y",
    "directMountWebThicknessX": "M6_DETECTOR_DIRECT_MOUNT_WEB_T_X",
    "directMountPostOverlapX": "M6_DETECTOR_DIRECT_MOUNT_POST_OVERLAP_X",
    "directMountSocketOuterD": "M6_DETECTOR_DIRECT_MOUNT_SOCKET_OUTER_D",
    "directMountSocketTapD": "M6_DETECTOR_DIRECT_MOUNT_SOCKET_TAP_D",
}


def direct_assignments(path: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    pattern = re.compile(
        r"^\s*([A-Za-z_]\w*)\s*=\s*([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            values[match.group(1)] = float(match.group(2))
    return values


def main() -> None:
    scad_values = direct_assignments(SCAD)
    preview_values = direct_assignments(PREVIEW)
    missing_scad = sorted(set(PARAMETER_MAP.values()) - set(scad_values))
    missing_preview = sorted(set(PARAMETER_MAP) - set(preview_values))
    if missing_scad or missing_preview:
        raise AssertionError(
            f"preview parameter coverage missing: scad={missing_scad}, "
            f"preview={missing_preview}"
        )

    mismatches = []
    for preview_name, scad_name in PARAMETER_MAP.items():
        if preview_values[preview_name] != scad_values[scad_name]:
            mismatches.append(
                f"{preview_name}={preview_values[preview_name]} "
                f"!= {scad_name}={scad_values[scad_name]}"
            )
    if mismatches:
        raise AssertionError("preview/SCAD parameter mismatch: " + "; ".join(mismatches))

    # The browser preview retains a few historical STG branches for old
    # manifests, but its visible current entry point must describe the M6
    # optical array.  This prevents a stale label from silently advertising
    # the superseded purchase/geometry path.
    index_text = PREVIEW_INDEX.read_text(encoding="utf-8")
    app_text = PREVIEW_APP.read_text(encoding="utf-8")
    browser_mismatches = []
    for browser_name, preview_name in BROWSER_PARAMETER_MAP.items():
        match = re.search(
            rf"\b{re.escape(browser_name)}:\s*([-+]?\d+(?:\.\d*)?)",
            app_text,
        )
        if match is None:
            browser_mismatches.append(f"{browser_name}=missing")
            continue
        actual = float(match.group(1))
        expected = preview_values[preview_name]
        if actual != expected:
            browser_mismatches.append(
                f"{browser_name}={actual} != {preview_name}={expected}"
            )
    if browser_mismatches:
        raise AssertionError(
            "browser preview/current M6 geometry mismatch: "
            + "; ".join(browser_mismatches)
        )
    required_current_copy = (
        "M6 直角十路光电阵列",
        "显示网布、M6 光电器件、PVDF 和标准件",
        "按步骤检查网架、M6 阵列和擦网传感器",
        "M6 45° L 型主体、x 向分体壳与竖直球头",
        "球头 z- 接口直接落在浅黄色下段最高水平面的一体 M8 承座",
        "取消横向黄色承托臂",
        "不再显示深黄色上段和深灰色独立连接器",
    )
    missing_copy = [text for text in required_current_copy if text not in index_text + app_text]
    if missing_copy:
        raise AssertionError(f"browser preview current M6 copy missing: {missing_copy}")
    stale_visible_copy = (
        "STG-120ML 两段光栅怎么装",
        "显示网布、STG 光纤头、传感器和标准件",
        "按步骤检查网架、STG-120ML 和擦网传感器",
        "STG-120ML 光纤头、两段检测窗口和已确认的标准件",
    )
    stale_hits = [text for text in stale_visible_copy if text in index_text + app_text]
    if stale_hits:
        raise AssertionError(f"browser preview still exposes stale current copy: {stale_hits}")

    print(f"PREVIEW_CONSISTENCY_OK ({len(PARAMETER_MAP)} direct parameters + current M6 copy)")


if __name__ == "__main__":
    main()
