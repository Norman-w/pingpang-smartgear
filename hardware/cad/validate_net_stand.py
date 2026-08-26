#!/usr/bin/env python3
"""Validate the current integrated net-stand OpenSCAD parameter source."""

from __future__ import annotations

import re
import math
import struct
import subprocess
import tempfile
from pathlib import Path

from validate_scad import find_openscad, stl_bounds, stl_x_center


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_stand.scad"
PARTS = (
    "assembly",
    "left_stand",
    "right_stand",
    "post",
    "post_segment",
    "lower_stand_segment",
    "post_joint_sleeve",
    "post_joint_key",
    "table_clamp",
    "table_clamp_section",
    "table_clamp_body",
    "clamp_top_pad",
    "clamp_pressure_pad",
    "clamp_screw",
    "clamp_body_nut",
    "clamp_knob",
    "clamp_knob_nut",
    "net",
    "net_rail",
    "net_rail_segment",
    "net_rail_splice",
    "net_rail_saddle",
    "optical_rail",
    "optical_strip",
    "optical_module_carrier",
    "m6_sensor_rail",
    "m6_sensor_test_coupon",
    "m6_sensor_array",
    "m6_detector_fit_probe",
    "m6_detector_fit_body",
    "m6_detector_body",
    "m6_detector_shell_front",
    "m6_detector_shell_rear",
    "m6_detector_bottom_cover",
    "m6_detector_mount",
    "m6_ballhead",
    "m6_gimbal",
    "stg120_outer_carrier",
    "stg120_center_bridge",
    "stg120_preview",
    "sensor_mount",
    "sensor_mount_body",
    "pvdf_film",
    "sensor_clamp_lip",
    "reference_carriage",
    "reference_carriage_body",
    "reference_pin",
    "calibration_gauge",
)
# These PARTs deliberately combine multiple overlapping visual envelopes. They
# are rendered as PNG evidence or used for assembly/fit inspection, not handed
# to a slicer as one printable STL.  Only standalone print parts are checked
# for closed edge topology below.
PREVIEW_ONLY_PARTS = {
    "assembly",
    "left_stand",
    "right_stand",
    "post",
    "table_clamp_section",
    "table_clamp",
    "net",
    "net_rail",
    "optical_strip",
    "m6_sensor_rail",
    "m6_sensor_array",
    "m6_detector_fit_probe",
    "m6_detector_fit_body",
    "m6_detector_mount",
    "m6_ballhead",
    "m6_gimbal",
    "stg120_preview",
    "sensor_mount",
    "reference_carriage",
}
NO_DRILL_TABLE_THICKNESSES = (18, 25, 30)


def run_openscad(openscad: str, output: Path, *definitions: str) -> subprocess.CompletedProcess[str]:
    command = [openscad, "-o", str(output)]
    for definition in definitions:
        command.extend(["-D", definition])
    command.append(str(SOURCE))
    return subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _stl_triangles(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    """Read binary or ASCII STL triangles using only the standard library."""

    data = path.read_bytes()
    if len(data) >= 84:
        triangle_count = struct.unpack_from("<I", data, 80)[0]
        expected_size = 84 + triangle_count * 50
        if expected_size == len(data):
            triangles = []
            for index in range(triangle_count):
                base = 84 + index * 50 + 12
                triangles.append(
                    tuple(
                        struct.unpack_from("<fff", data, base + vertex * 12)
                        for vertex in range(3)
                    )
                )
            return triangles

    vertices = [
        (float(match.group(1)), float(match.group(2)), float(match.group(3)))
        for match in re.finditer(
            r"\bvertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)",
            data.decode("utf-8", errors="replace"),
            re.IGNORECASE,
        )
    ]
    if len(vertices) == 0 or len(vertices) % 3 != 0:
        raise RuntimeError(f"cannot parse STL triangles from {path}")
    return [
        (vertices[index], vertices[index + 1], vertices[index + 2])
        for index in range(0, len(vertices), 3)
    ]


def _stl_topology(path: Path, tolerance: float = 1e-6) -> tuple[bool, str]:
    """Return a compact closed-edge report for a generated STL."""

    edge_counts: dict[tuple[tuple[int, int, int], tuple[int, int, int]], int] = {}
    edge_orientation: dict[tuple[tuple[int, int, int], tuple[int, int, int]], int] = {}
    degenerate = 0
    triangles = _stl_triangles(path)

    def vertex_key(point: tuple[float, float, float]) -> tuple[int, int, int]:
        return tuple(int(round(value / tolerance)) for value in point)

    for triangle in triangles:
        keys = tuple(vertex_key(point) for point in triangle)
        if len(set(keys)) < 3:
            degenerate += 1
        for start, end in ((keys[0], keys[1]), (keys[1], keys[2]), (keys[2], keys[0])):
            edge = tuple(sorted((start, end)))
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
            edge_orientation[edge] = edge_orientation.get(edge, 0) + (
                1 if (start, end) == edge else -1
            )

    boundary = sum(count == 1 for count in edge_counts.values())
    non_manifold = sum(count > 2 for count in edge_counts.values())
    inconsistent = sum(
        count == 2 and edge_orientation[edge] != 0
        for edge, count in edge_counts.items()
    )
    ok = bool(triangles) and not (degenerate or boundary or non_manifold or inconsistent)
    volume_mm3 = _stl_volume_from_triangles(triangles)
    details = (
        f"triangles={len(triangles)}, degenerate={degenerate}, boundary={boundary}, "
        f"non_manifold={non_manifold}, inconsistent_orientation={inconsistent}, "
        f"volume_mm3={volume_mm3:.3f}"
    )
    return ok, details


def _stl_volume_from_triangles(
    triangles: list[tuple[tuple[float, float, float], ...]]
) -> float:
    """Return the absolute closed-mesh volume using a local reference point.

    Translating every triangle by the first vertex avoids loss of precision for
    the detector parts, whose global x coordinates are around 770 mm.  The
    topology check remains the authority for closure; this value catches an
    empty/zero-volume export and records the requested volume evidence.
    """

    if not triangles:
        return 0.0
    reference = triangles[0][0]
    total = 0.0
    for triangle in triangles:
        vectors = [
            tuple(point[axis] - reference[axis] for axis in range(3))
            for point in triangle
        ]
        first, second, third = vectors
        cross = (
            second[1] * third[2] - second[2] * third[1],
            second[2] * third[0] - second[0] * third[2],
            second[0] * third[1] - second[1] * third[0],
        )
        total += (
            first[0] * cross[0]
            + first[1] * cross[1]
            + first[2] * cross[2]
        ) / 6.0
    return abs(total)


def _stl_volume(path: Path) -> float:
    """Return the absolute STL volume in cubic millimetres."""

    return _stl_volume_from_triangles(_stl_triangles(path))


def _stl_mirror_signature(
    path: Path, *, reflect_x: bool, tolerance: float = 1e-5
) -> set[tuple[int, int, int]]:
    """Return an orientation-independent unique-vertex signature for mirrors."""

    signature: set[tuple[int, int, int]] = set()

    def vertex_key(point: tuple[float, float, float]) -> tuple[int, int, int]:
        x, y, z = point
        if reflect_x:
            x = -x
        return (
            int(round(x / tolerance)),
            int(round(y / tolerance)),
            int(round(z / tolerance)),
        )

    for triangle in _stl_triangles(path):
        # STL export order and winding are not semantic. Compare the complete
        # unique vertex set and triangle count instead of triangle grouping:
        # OpenSCAD is allowed to choose the other diagonal when triangulating
        # a mirrored planar quad, while the generated solid remains identical.
        for point in triangle:
            signature.add(vertex_key(point))
    return signature


def require_stl(
    result: subprocess.CompletedProcess[str],
    output: Path,
    label: str,
    *,
    require_closed: bool = True,
) -> None:
    if result.returncode != 0:
        raise RuntimeError(f"OpenSCAD rejected {label}:\n{result.stdout}")
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"OpenSCAD produced no STL for {label}")
    if require_closed:
        closed, details = _stl_topology(output)
        if not closed:
            raise RuntimeError(f"OpenSCAD produced a non-closed STL for {label}: {details}")
        volume_mm3 = _stl_volume(output)
        if volume_mm3 <= 1e-6:
            raise RuntimeError(
                f"OpenSCAD produced a zero-volume STL for {label}: "
                f"volume_mm3={volume_mm3:.6f}"
            )


def validate_no_drill_thickness(
    openscad: str,
    output_dir: Path,
    table_thickness: int,
    top_pad_t: float,
    knob_nut_stack_depth: float,
) -> None:
    """Compile the under-table pressure path for a first-pass thickness matrix."""

    definitions = (f"table_thickness={table_thickness}",)
    body = output_dir / f"table-clamp-body-{table_thickness}.stl"
    top_pad = output_dir / f"top-pad-{table_thickness}.stl"
    pad = output_dir / f"pressure-pad-{table_thickness}.stl"
    screw = output_dir / f"clamp-screw-{table_thickness}.stl"
    body_nut = output_dir / f"clamp-body-nut-{table_thickness}.stl"
    knob = output_dir / f"clamp-knob-{table_thickness}.stl"
    knob_nut = output_dir / f"clamp-knob-nut-{table_thickness}.stl"
    require_stl(
        run_openscad(openscad, body, 'PART="table_clamp_body"', *definitions),
        body,
        f"table clamp body table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, top_pad, 'PART="clamp_top_pad"', *definitions),
        top_pad,
        f"upper protective pad table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, pad, 'PART="clamp_pressure_pad"', *definitions),
        pad,
        f"pressure pad table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, screw, 'PART="clamp_screw"', *definitions),
        screw,
        f"clamp screw table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, body_nut, 'PART="clamp_body_nut"', *definitions),
        body_nut,
        f"fixed M8 nut table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, knob, 'PART="clamp_knob"', *definitions),
        knob,
        f"clamp knob table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, knob_nut, 'PART="clamp_knob_nut"', *definitions),
        knob_nut,
        f"captured knob M8 nut table_thickness={table_thickness}",
    )
    top_pad_bounds = stl_bounds(top_pad)
    pad_bounds = stl_bounds(pad)
    screw_bounds = stl_bounds(screw)
    body_nut_bounds = stl_bounds(body_nut)
    knob_bounds = stl_bounds(knob)
    knob_nut_bounds = stl_bounds(knob_nut)
    tabletop_bottom = -float(table_thickness)
    if not (
        top_pad_bounds[4] >= -0.01
        and top_pad_bounds[5] <= top_pad_t + 0.01
        and pad_bounds[5] < tabletop_bottom
        and screw_bounds[5] < tabletop_bottom
        and screw_bounds[5] <= pad_bounds[4] + 0.01
        and body_nut_bounds[5] < tabletop_bottom
        and knob_bounds[5] < tabletop_bottom
        and knob_nut_bounds[5] < tabletop_bottom
        and knob_nut_bounds[4] >= knob_bounds[4] - 0.01
        and knob_nut_bounds[5] <= knob_bounds[5] + 0.01
        and knob_nut_bounds[5] - knob_nut_bounds[4]
        >= knob_nut_stack_depth - 0.01
    ):
        raise RuntimeError(
            "no-drill under-table path reaches the tabletop for "
            f"table_thickness={table_thickness}: top_pad={top_pad_bounds}, pad={pad_bounds}, "
            f"screw={screw_bounds}, "
            f"body_nut={body_nut_bounds}, knob={knob_bounds}, knob_nut={knob_nut_bounds}"
        )


def probe_parameters(openscad: str, output_dir: Path) -> dict[str, float]:
    output = output_dir / "parameter-probe.stl"
    result = run_openscad(openscad, output, 'PART="parameter_probe"')
    require_stl(result, output, "PART=parameter_probe")
    parameters: dict[str, float] = {}
    for key, value in re.findall(r"NETSTAND_PARAM\s+(\w+)=([-+0-9.eE]+)", result.stdout):
        parameters[key] = float(value)
    required = {
        "table_width",
        "table_thickness",
        "net_post_outboard_extension",
        "net_height",
        "net_rail_height",
        "net_rail_depth",
        "beam_count",
        "beam_first_height",
        "beam_last_height",
        "beam_pitch",
        "post_center_x",
        "post_offset",
        "post_body_width",
        "post_body_depth",
        "post_bottom",
        "post_segment_count",
        "post_segment_length",
        "post_joint_gap",
        "net_span",
        "net_rail_segment_count",
        "net_rail_segment_length",
        "net_rail_splice_overlap",
        "net_rail_splice_plate_length",
        "net_rail_splice_hole_d",
        "net_rail_saddle_overlap",
        "net_rail_saddle_width",
        "net_rail_saddle_depth",
        "net_rail_saddle_height",
        "post_top",
        "sensor_x",
        "sensor_film_length",
        "sensor_film_depth",
        "sensor_clamp_tab_width",
        "clamp_pad_x",
        "clamp_pad_outer_x",
        "clamp_outer_wall_x",
        "clamp_horizontal_part_outboard_limit",
        "clamp_outboard_extension_actual",
        "clamp_screw_x",
        "clamp_screw_d",
        "clamp_screw_pitch",
        "clamp_threaded_boss_d",
        "clamp_threaded_boss_h",
        "clamp_top_pad_x",
        "clamp_top_pad_width",
        "clamp_top_pad_depth",
        "clamp_top_pad_t",
        "clamp_screw_top_z",
        "clamp_screw_bottom_z",
        "clamp_screw_length",
        "clamp_screw_tip_radius",
        "clamp_screw_to_knob_top",
        "clamp_nut_af",
        "clamp_nut_h",
        "clamp_nut_clearance",
        "clamp_nut_pocket_af",
        "clamp_nut_pocket_depth",
        "clamp_knob_nut_gap",
        "clamp_knob_nut_stack_depth",
        "clamp_knob_nut_pocket_depth",
        "clamp_body_nut_z",
        "clamp_knob_h",
        "clamp_knob_top_z",
        "clamp_knob_bottom_z",
        "clamp_knob_nut_z",
        "clamp_knob_drive_nut_z",
        "clamp_knob_lock_nut_z",
        "clamp_knob_nut_bottom_z",
        "clamp_knob_nut_top_z",
        "clamp_lower_arm_bottom_z",
        "clamp_lower_arm_top_z",
        "clamp_pressure_pad_top_z",
        "clamp_pressure_pad_bottom_z",
        "clamp_pressure_pad_x",
        "clamp_pressure_pad_width",
        "optical_locating_hole_d",
        "optical_rail_width",
        "optical_module_depth",
        "optical_module_width",
        "optical_module_height",
        "optical_rail_depth",
        "optical_beam_edge_overlap",
        "optical_beam_axis_x",
        "optical_rail_x",
        "optical_carrier_clearance",
        "optical_carrier_wall",
        "optical_carrier_z_wall",
        "optical_carrier_back_depth",
        "optical_carrier_front_depth",
        "optical_carrier_width",
        "optical_carrier_height",
        "optical_carrier_slot_d",
        "optical_carrier_slot_length",
        "optical_module_index",
        "m6_sensor_count",
        "m6_sensor_center_pitch",
        "m6_sensor_first_height",
        "m6_sensor_thread_d",
        "m6_sensor_thread_pitch",
        "m6_sensor_head_length_x",
        "m6_sensor_head_width_y",
        "m6_sensor_head_height_z",
        "m6_sensor_body_d",
        "m6_sensor_body_length",
        "m6_sensor_mount_x_offset",
        "m6_sensor_mount_stem_length",
        "m6_sensor_cable_guard_length",
        "m6_sensor_cable_preview_length",
        "m6_sensor_cable_d",
        "m6_sensor_thread_start_x",
        "m6_sensor_thread_end_x",
        "m6_sensor_overall_end_x",
        "m6_sensor_head_center_x",
        "m6_sensor_cable_exit_x",
        "m6_sensor_mount_plane_offset_z",
        "m6_sensor_lock_nut_af",
        "m6_sensor_guard_outer_d",
        "m6_sensor_guard_h",
        "m6_sensor_test_coupon_backbone_h",
        "m6_sensor_test_coupon_clearance_d",
        "m6_sensor_test_coupon_guard_overlap",
        "m6_sensor_nut_pocket_clearance",
        "m6_sensor_lane_offset_y",
        "m6_adjacent_channel_center_distance_yz",
        "m6_adjacent_guard_gap_y",
        "m6_adjacent_guard_gap_z",
        "m6_rail_t",
        "m6_sensor_body_clearance_d",
        "m6_rail_width_y",
        "m6_rail_tab_t",
        "m6_rail_tab_width_y",
        "m6_rail_mount_clearance_d",
        "m6_rail_mount_tap_d",
        "m6_rail_mount_tap_depth",
        "m6_rail_mount_hole_y",
        "m6_rail_mount_z_offset",
        "m6_rail_mount_bolt_length",
        "m6_rail_length_z",
        "m6_array_bottom_z",
        "m6_array_top_z",
        "m6_array_center_z",
        "m6_detector_backplate_t",
        "m6_detector_backplate_width_y",
        "m6_detector_backplate_height_z",
        "m6_detector_backplate_lock_hole_y",
        "m6_detector_backplate_mount_clearance_d",
        "m6_detector_backplate_anti_rotation_d",
        "m6_ballhead_ball_d",
        "m6_ballhead_housing_d",
        "m6_ballhead_housing_length_x",
        "m6_ballhead_base_d",
        "m6_ballhead_base_t",
        "m6_ballhead_sensor_stud_d",
        "m6_ballhead_sensor_stud_length",
        "m6_ballhead_net_stud_d",
        "m6_ballhead_net_stud_length",
        "m6_ballhead_tilt_range_deg",
        "m6_ballhead_rotation_range_deg",
        "m6_ballhead_mount_clearance_d",
        "m6_detector_backplate_x",
        "m6_ballhead_center_x",
        "m6_ballhead_axis_z",
        "m6_ballhead_net_stud_center_x",
        "m6_mount_plate_t",
        "m6_mount_slot_length",
        "m6_post_mount_clearance_d",
        "m6_post_mount_hole_y",
        "m6_post_mount_bolt_length",
        "m6_post_mount_hole_z",
        "m6_yaw_stage_t",
        "m6_yaw_stage_radius",
        "m6_yaw_slot_radius",
        "m6_yaw_stage_z",
        "m6_yaw_carrier_bottom_z",
        "m6_yaw_carrier_height",
        "m6_yaw_plate_t",
        "m6_pitch_yoke_t",
        "m6_pitch_yoke_width_y",
        "m6_pitch_yoke_length_x",
        "m6_pitch_yoke_foot_t",
        "m6_pitch_frame_t",
        "m6_pitch_frame_outer_width_y",
        "m6_pitch_frame_window_width_y",
        "m6_pitch_frame_outer_height_z",
        "m6_pitch_frame_window_height_z",
        "m6_pitch_frame_spine_width_y",
        "m6_pitch_frame_hub_d",
        "m6_pitch_pivot_offset_z",
        "m6_pitch_pivot_x",
        "m6_pitch_pivot_z",
        "m6_roll_pivot_z",
        "m6_pitch_slot_length",
        "m6_roll_plate_t",
        "m6_roll_plate_d",
        "m6_roll_slot_length",
        "m6_pivot_d",
        "m6_roll_pivot_d",
        "m6_pitch_lock_tap_d",
        "m6_pitch_lock_tap_depth",
        "m6_roll_lock_tap_d",
        "m6_roll_lock_tap_depth",
        "m6_roll_pivot_bolt_length",
        "m6_stage_bolt_d",
        "m6_fine_adjuster_d",
        "m6_fine_adjuster_length",
        "m6_yaw_adjuster_block_width_x",
        "m6_yaw_adjuster_block_depth_y",
        "m6_yaw_adjuster_block_height_z",
        "m6_yaw_adjuster_foot_inset_y",
        "m6_yaw_adjuster_tap_d",
        "m6_yaw_adjuster_tap_depth",
        "m6_yaw_adjuster_tip_overtravel_y",
        "m6_sensor_lock_nut_h",
        "m6_sensor_roll_deg",
        "m6_detector_body_depth_y",
        "m6_detector_body_center_y",
        "m6_detector_body_length_x",
        "m6_detector_body_margin_z",
        "m6_detector_body_front_margin_x",
        "m6_detector_fit_head_length_x",
        "m6_detector_fit_head_width_y",
        "m6_detector_fit_head_height_z",
        "m6_detector_fit_capture_depth_x",
        "m6_detector_fit_head_clearance_y",
        "m6_detector_fit_head_clearance_z",
        "m6_detector_fit_thread_length_x",
        "m6_detector_fit_thread_clearance_d",
        "m6_detector_fit_thread_tip_allowance_x",
        "m6_detector_fit_head_inner_x",
        "m6_detector_fit_head_center_x",
        "m6_detector_fit_thread_tip_x",
        "m6_detector_fit_thread_visible_length_x",
        "m6_detector_fit_body_depth_limit_x",
        "m6_detector_fit_nut_center_x",
        "m6_detector_sensor_install_offset_x",
        "m6_detector_sensor_nut_center_x",
        "m6_detector_thread_visible_length",
        "m6_detector_shell_wall",
        "m6_detector_shell_clearance",
        "m6_detector_shell_bottom_lip_z",
        "m6_detector_shell_top_lip_z",
        "m6_detector_shell_split_overlap_x",
        "m6_detector_shell_corner_radius",
        "m6_detector_front_cap_length_x",
        "m6_detector_front_cap_reduction",
        "m6_detector_body_groove_width_x",
        "m6_detector_body_groove_depth_y",
        "m6_detector_body_groove_margin_z",
        "m6_detector_shell_tongue_depth_y",
        "m6_detector_shell_tongue_clearance",
        "m6_detector_optical_bore_d",
        "m6_detector_thread_clearance_d",
        "m6_detector_hex_pocket_af",
        "m6_detector_hex_pocket_depth_y",
        "m6_detector_hex_pocket_floor",
        "m6_detector_shell_screw_pilot_d",
        "m6_detector_shell_screw_head_d",
        "m6_detector_shell_screw_head_depth",
        "m6_detector_shell_screw_margin_z",
        "m6_detector_bottom_cover_t",
        "m6_bottom_cover_screw_depth",
        "m6_detector_bottom_cover_screw_d",
        "m6_detector_bottom_cover_screw_head_d",
        "m6_detector_bottom_cover_screw_head_depth",
        "m6_detector_bottom_cover_screw_inset_x",
        "m6_detector_cable_exit_d",
        "m6_detector_cable_exit_sleeve_clearance",
        "m6_detector_cable_exit_x",
        "m6_detector_detector_thread_axis_x",
        "m6_detector_sensor_thread_center_y",
        "m6_detector_sensor_head_center_y",
        "m6_detector_shell_support_boss_length_x",
        "m6_detector_shell_support_boss_overlap_x",
        "m6_detector_shell_support_boss_depth_y",
        "m6_detector_shell_support_boss_height_z",
        "m6_detector_shell_support_boss_radius",
        "m6_detector_shell_support_hole_d",
        "m6_detector_shell_support_hole_depth_x",
        "m6_detector_shell_support_stud_engagement_x",
        "m6_detector_detector_ballhead_gap_x",
        "m6_detector_sensor_head_y_offset",
        "m6_detector_body_min_x",
        "m6_detector_body_max_x",
        "m6_detector_body_bottom_z",
        "m6_detector_body_top_z",
        "m6_detector_body_height_z",
        "m6_detector_body_center_z",
        "m6_detector_body_min_y",
        "m6_detector_body_max_y",
        "m6_detector_shell_min_x",
        "m6_detector_shell_max_x",
        "m6_detector_shell_min_y",
        "m6_detector_shell_max_y",
        "m6_detector_shell_width_y",
        "m6_detector_shell_bottom_z",
        "m6_detector_shell_top_z",
        "m6_detector_shell_height_z",
        "m6_detector_shell_split_x",
        "m6_detector_shell_front_max_x",
        "m6_detector_shell_rear_min_x",
        "m6_detector_shell_split_y",
        "m6_detector_shell_front_min_y",
        "m6_detector_shell_rear_max_y",
        "m6_detector_shell_inner_min_x",
        "m6_detector_shell_inner_max_x",
        "m6_detector_detector_thread_axis_x",
        "m6_detector_shell_support_boss_min_x",
        "m6_detector_shell_support_boss_max_x",
        "m6_detector_shell_support_boss_min_y",
        "m6_detector_shell_support_boss_max_y",
        "m6_detector_shell_support_boss_center_x",
        "m6_detector_shell_support_boss_center_y",
        "m6_detector_shell_support_boss_bottom_z",
        "m6_detector_shell_support_boss_top_z",
        "m6_detector_shell_support_boss_center_z",
        "m6_detector_shell_support_hole_entry_x",
        "m6_detector_shell_support_hole_center_x",
        "m6_detector_ballhead_center_x",
        "m6_detector_ballhead_center_y",
        "m6_detector_ballhead_center_z",
        "m6_detector_ballhead_sensor_stud_center_x",
        "stg120_head_length",
        "stg120_active_length",
        "stg120_head_width",
        "stg120_head_thickness",
        "stg120_beam_count",
        "stg120_beam_pitch",
        "stg120_detect_distance_max",
        "stg120_outer_face_x",
        "stg120_outer_frame_min_x",
        "stg120_outer_frame_max_x",
        "stg120_reference_height",
        "reference_pin_d",
        "reference_pin_bore_d",
        "reference_pin_length",
        "reference_carriage_depth",
        "clamp_pad_depth",
        "clamp_outboard_extension_min",
        "clamp_gusset_t_y",
        "clamp_gusset_start_inset",
        "clamp_gusset_start_x",
        "clamp_gusset_end_x",
        "clamp_gusset_top_z",
        "clamp_gusset_bottom_z",
    }
    missing = required - parameters.keys()
    if missing:
        raise RuntimeError(f"parameter probe did not emit: {sorted(missing)}\n{result.stdout}")
    if parameters["beam_count"] != 10 or parameters["beam_last_height"] != 100:
        raise RuntimeError(f"unexpected optical grid parameters: {parameters}")
    if not (parameters["post_center_x"] > parameters["table_width"] / 2):
        raise RuntimeError(f"post is not outside table edge: {parameters}")
    table_edge = parameters["table_width"] / 2
    post_inner_face = parameters["post_center_x"] - parameters["post_body_width"] / 2
    post_outer_face = parameters["post_center_x"] + parameters["post_body_width"] / 2
    if not (
        parameters["net_post_outboard_extension"] >= 130
        and abs(post_outer_face - table_edge - parameters["net_post_outboard_extension"]) < 0.01
        and abs(parameters["net_span"] - (
            parameters["table_width"]
            + 2 * parameters["net_post_outboard_extension"]
        )) < 0.01
    ):
        raise RuntimeError(f"net assembly outboard extension is inconsistent: {parameters}")
    if not (
        parameters["post_offset"] > 0
        and parameters["optical_beam_edge_overlap"] >= 0
        and parameters["optical_beam_axis_x"] >= table_edge
        and 2 * parameters["optical_beam_axis_x"] >= parameters["table_width"]
        and parameters["optical_rail_x"] >= table_edge
        and parameters["optical_rail_x"] + parameters["optical_rail_depth"]
        <= post_inner_face + 0.01
    ):
        raise RuntimeError(
            "optical axis/rail does not cover the full tabletop while staying outside the post body: "
            f"{parameters}"
        )
    if not (
        parameters["post_segment_count"] == 2
        and 100 < parameters["post_segment_length"] < 240
        and parameters["post_joint_gap"] == 2
    ):
        raise RuntimeError(f"unexpected printable post segmentation: {parameters}")
    if not (
        parameters["clamp_pad_x"] < table_edge < parameters["clamp_pad_outer_x"]
        and parameters["clamp_pad_x"] < parameters["clamp_screw_x"] < table_edge
        and abs(
            parameters["clamp_outboard_extension_actual"]
            - (parameters["clamp_pad_outer_x"] - table_edge)
        )
        < 0.01
        and parameters["clamp_outboard_extension_actual"]
        >= parameters["clamp_outboard_extension_min"]
        and parameters["clamp_outboard_extension_min"] >= 130
        and parameters["clamp_outboard_extension_actual"]
        <= parameters["clamp_horizontal_part_outboard_limit"] + 0.01
    ):
        raise RuntimeError(f"clamp does not bridge edge with an under-table screw: {parameters}")
    if not (
        parameters["clamp_gusset_t_y"] > 0
        and parameters["clamp_gusset_t_y"] < parameters["clamp_pad_depth"] / 2
        and parameters["clamp_gusset_start_x"] > parameters["clamp_pressure_pad_x"]
        + parameters["clamp_pressure_pad_width"]
        / 2
        and parameters["clamp_gusset_end_x"] > parameters["clamp_gusset_start_x"]
        and parameters["clamp_gusset_end_x"] > parameters["clamp_outer_wall_x"]
        and parameters["clamp_gusset_top_z"] < -parameters["table_thickness"]
        and parameters["clamp_gusset_top_z"] > parameters["clamp_lower_arm_top_z"]
        and parameters["clamp_gusset_bottom_z"]
        < parameters["clamp_lower_arm_bottom_z"]
    ):
        raise RuntimeError(f"under-clamp triangular gusset geometry is inconsistent: {parameters}")
    if not (
        parameters["clamp_screw_d"] == 8
        and parameters["clamp_screw_pitch"] == 1.25
        and
        parameters["clamp_screw_top_z"] < -parameters["table_thickness"]
        and parameters["clamp_pressure_pad_top_z"] < -parameters["table_thickness"]
        and parameters["clamp_screw_top_z"] <= parameters["clamp_pressure_pad_bottom_z"]
        and parameters["clamp_screw_bottom_z"] < parameters["clamp_knob_top_z"]
        and parameters["clamp_screw_bottom_z"] > parameters["clamp_knob_bottom_z"]
        and parameters["clamp_knob_bottom_z"] < parameters["clamp_knob_top_z"]
        and parameters["clamp_pressure_pad_bottom_z"] <
        parameters["clamp_pressure_pad_top_z"]
        and parameters["clamp_lower_arm_top_z"] <
        parameters["clamp_pressure_pad_bottom_z"]
    ):
        raise RuntimeError(f"M8x1.25 clamp pressure path is inconsistent: {parameters}")
    if not (
        parameters["clamp_nut_af"] > parameters["clamp_screw_d"]
        and parameters["clamp_nut_pocket_af"] > parameters["clamp_nut_af"]
        and parameters["clamp_nut_pocket_af"] / math.cos(math.radians(30)) + 2
        < parameters["clamp_threaded_boss_d"]
        and parameters["clamp_nut_pocket_depth"] >= parameters["clamp_nut_h"]
        and parameters["clamp_nut_pocket_depth"] < parameters["clamp_threaded_boss_h"]
        and parameters["clamp_knob_nut_gap"] >= 0
        and parameters["clamp_knob_nut_stack_depth"]
        == 2 * parameters["clamp_nut_h"] + parameters["clamp_knob_nut_gap"]
        and parameters["clamp_knob_nut_pocket_depth"]
        > parameters["clamp_knob_nut_stack_depth"]
        and parameters["clamp_knob_nut_pocket_depth"]
        < parameters["clamp_knob_h"]
        and parameters["clamp_knob_nut_bottom_z"] >= parameters["clamp_knob_bottom_z"]
        and parameters["clamp_knob_nut_top_z"] <= parameters["clamp_knob_top_z"]
        and parameters["clamp_knob_drive_nut_z"] > parameters["clamp_knob_lock_nut_z"]
        and parameters["clamp_screw_top_z"] > parameters["clamp_knob_nut_top_z"]
        and parameters["clamp_screw_bottom_z"] < parameters["clamp_knob_nut_bottom_z"]
    ):
        raise RuntimeError(f"M8 nut capture dimensions are inconsistent: {parameters}")
    if parameters["net_span"] <= parameters["table_width"]:
        raise RuntimeError(f"net span does not bridge the table: {parameters}")
    if not (
        parameters["net_rail_segment_count"] == 3
        and parameters["net_rail_segment_length"] > 500
        and parameters["net_rail_splice_overlap"] == 20
        and parameters["net_rail_splice_plate_length"] == 60
        and parameters["net_rail_splice_hole_d"] > 0
    ):
        raise RuntimeError(f"unexpected printable rail segmentation: {parameters}")
    if not (
        parameters["net_rail_saddle_width"] > parameters["net_rail_saddle_overlap"] > 0
        and parameters["net_rail_saddle_depth"] > parameters["net_rail_depth"]
        and parameters["net_rail_saddle_height"] > 0
    ):
        raise RuntimeError(f"unexpected rail saddle geometry: {parameters}")
    if not (0 < parameters["optical_locating_hole_d"] < parameters["optical_rail_width"]):
        raise RuntimeError(f"invalid optical locating hole diameter: {parameters}")
    if not (
        parameters["optical_carrier_front_depth"] > parameters["optical_module_depth"]
        and parameters["optical_carrier_width"] > parameters["optical_module_width"]
        and parameters["optical_carrier_height"] > parameters["optical_module_height"]
        and parameters["optical_carrier_height"] < parameters["beam_pitch"]
        and parameters["optical_carrier_slot_length"] > parameters["optical_carrier_slot_d"]
    ):
        raise RuntimeError(f"optical module carrier does not leave an adjustment envelope: {parameters}")
    if parameters["optical_module_index"] != 0:
        raise RuntimeError(f"parameter probe must use the default optical module index: {parameters}")
    if not (
        parameters["m6_sensor_count"] == 10
        and parameters["m6_sensor_center_pitch"] == 2 * parameters["beam_pitch"]
        and parameters["m6_sensor_first_height"] == parameters["beam_first_height"]
        and parameters["m6_sensor_first_height"]
        + (parameters["m6_sensor_count"] - 1) * parameters["m6_sensor_center_pitch"]
        > parameters["m6_sensor_first_height"]
        and parameters["m6_sensor_thread_d"] == 6
        and parameters["m6_sensor_thread_pitch"] == 0.75
        and parameters["m6_sensor_head_width_y"] >= parameters["m6_sensor_thread_d"]
        and parameters["m6_sensor_head_height_z"] > 0
        and parameters["m6_sensor_body_d"] >= parameters["m6_sensor_thread_d"]
        and parameters["m6_sensor_body_length"] > 5
        and parameters["m6_sensor_mount_stem_length"] > 5
    ):
        raise RuntimeError(f"M6 sensor envelope/grid parameters are inconsistent: {parameters}")
    if not (
        parameters["m6_rail_t"] > 0
        and parameters["m6_rail_width_y"] > parameters["m6_sensor_head_width_y"] + 2
        and parameters["m6_rail_tab_t"] >= 5
        and parameters["m6_rail_tab_width_y"] > parameters["m6_sensor_thread_d"] + 2
        and 2 * parameters["m6_sensor_lane_offset_y"] > parameters["m6_sensor_head_width_y"]
        and 2 * parameters["m6_sensor_lane_offset_y"] > parameters["m6_rail_tab_width_y"]
        and parameters["m6_sensor_body_clearance_d"] > parameters["m6_sensor_body_d"]
        and parameters["m6_sensor_body_clearance_d"] / 2
        < parameters["m6_rail_width_y"] / 2 - parameters["m6_sensor_lane_offset_y"]
        and parameters["m6_adjacent_channel_center_distance_yz"]
        > parameters["m6_sensor_guard_outer_d"]
        + 2 * parameters["m6_sensor_nut_pocket_clearance"]
        and parameters["m6_adjacent_guard_gap_y"]
        > 2 * parameters["m6_sensor_nut_pocket_clearance"]
        and parameters["m6_adjacent_guard_gap_z"]
        > 2 * parameters["m6_sensor_nut_pocket_clearance"]
        and parameters["m6_rail_mount_clearance_d"]
        > parameters["m6_rail_mount_tap_d"]
        and parameters["m6_rail_mount_tap_depth"]
        <= parameters["m6_rail_t"] - 2
        and parameters["m6_rail_mount_hole_y"]
        + parameters["m6_rail_mount_clearance_d"] / 2
        < parameters["m6_rail_width_y"] / 2
        and parameters["m6_rail_mount_z_offset"]
        + parameters["m6_rail_mount_clearance_d"] / 2
        < parameters["m6_rail_length_z"] / 2
        and math.hypot(
            parameters["m6_rail_mount_hole_y"]
            - parameters["m6_sensor_lane_offset_y"],
            (parameters["m6_sensor_count"] - 1)
            * parameters["m6_sensor_center_pitch"]
            / 2
            - parameters["m6_rail_mount_z_offset"],
        )
        > (
            parameters["m6_rail_mount_clearance_d"]
            + parameters["m6_sensor_body_clearance_d"]
        )
        / 2
        and parameters["m6_rail_length_z"] > 0
        and parameters["m6_array_bottom_z"] < parameters["m6_array_top_z"]
        and parameters["m6_sensor_axis_x"] >= table_edge
        and parameters["m6_sensor_rail_x"] > parameters["m6_sensor_axis_x"]
        and parameters["m6_sensor_rail_x"] + parameters["m6_rail_t"] <= post_inner_face + 0.01
    ):
        raise RuntimeError(f"M6 single vertical sensor-bar envelope/clearance is inconsistent: {parameters}")
    if not (
        parameters["m6_detector_backplate_t"] >= 6
        and parameters["m6_detector_backplate_width_y"] > parameters["m6_rail_width_y"]
        and parameters["m6_detector_backplate_height_z"] > parameters["m6_rail_length_z"]
        and parameters["m6_detector_backplate_x"] >= parameters["m6_sensor_rail_x"]
        and parameters["m6_detector_backplate_x"]
        <= parameters["m6_sensor_rail_x"] + parameters["m6_rail_t"]
        and parameters["m6_detector_backplate_mount_clearance_d"]
        > parameters["m6_ballhead_sensor_stud_d"]
        and parameters["m6_detector_backplate_anti_rotation_d"] > 0
        and parameters["m6_detector_backplate_lock_hole_y"]
        + parameters["m6_detector_backplate_anti_rotation_d"] / 2
        < parameters["m6_detector_backplate_width_y"] / 2
        and parameters["m6_ballhead_ball_d"] == 13
        and parameters["m6_ballhead_housing_d"] > parameters["m6_ballhead_ball_d"]
        and parameters["m6_ballhead_housing_length_x"]
        > parameters["m6_ballhead_sensor_stud_length"]
        and parameters["m6_ballhead_base_d"] > parameters["m6_ballhead_ball_d"]
        and parameters["m6_ballhead_base_t"] > 0
        and parameters["m6_ballhead_net_stud_d"] > 0
        and parameters["m6_ballhead_net_stud_length"] > 0
        and parameters["m6_ballhead_tilt_range_deg"] == 90
        and parameters["m6_ballhead_rotation_range_deg"] == 360
        and math.isclose(
            parameters["m6_ballhead_axis_z"],
            parameters["m6_array_center_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_ballhead_center_x"]
        > parameters["m6_detector_backplate_x"]
        + parameters["m6_detector_backplate_t"]
        and parameters["m6_ballhead_net_stud_center_x"]
        - parameters["m6_ballhead_net_stud_length"] / 2
        >= parameters["m6_ballhead_center_x"]
        + parameters["m6_ballhead_housing_length_x"] / 2
        - 1e-4
    ):
        raise RuntimeError(
            f"13 mm commercial ball-head interface is inconsistent: {parameters}"
        )
    expected_adjacent_distance = math.hypot(
        2 * parameters["m6_sensor_lane_offset_y"],
        parameters["m6_sensor_center_pitch"],
    )
    expected_guard_gap_y = (
        2 * parameters["m6_sensor_lane_offset_y"]
        - parameters["m6_sensor_guard_outer_d"]
    )
    expected_guard_gap_z = (
        parameters["m6_sensor_center_pitch"]
        - parameters["m6_sensor_guard_h"]
    )
    if not (
        math.isclose(
            parameters["m6_adjacent_channel_center_distance_yz"],
            expected_adjacent_distance,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_adjacent_guard_gap_y"],
            expected_guard_gap_y,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_adjacent_guard_gap_z"],
            expected_guard_gap_z,
            rel_tol=0,
            abs_tol=1e-4,
        )
    ):
        raise RuntimeError(
            "M6 adjacent guard clearance probe does not match the staggered grid: "
            f"{parameters}"
        )
    if not (
        math.isclose(
            parameters["m6_post_mount_hole_z"],
            parameters["m6_array_center_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_post_mount_clearance_d"] >= parameters["m6_stage_bolt_d"]
        and parameters["m6_post_mount_hole_y"]
        + parameters["m6_post_mount_clearance_d"] / 2
        < parameters["post_body_depth"] / 2
        and parameters["m6_post_mount_hole_y"]
        > parameters["m6_post_mount_clearance_d"] / 2
        and parameters["m6_post_mount_hole_z"]
        > parameters["post_bottom"]
        + parameters["post_segment_length"]
        + parameters["post_joint_gap"]
        and parameters["m6_post_mount_hole_z"] < parameters["post_top"]
        and parameters["m6_post_mount_bolt_length"]
        >= parameters["m6_mount_plate_t"]
        + parameters["post_body_width"]
        + 8
    ):
        raise RuntimeError(
            f"M6 adapter-to-upright through-bolt interface is inconsistent: {parameters}"
        )
    if not (
        parameters["m6_mount_plate_t"] >= 4
        and parameters["m6_mount_plate_width_y"] > parameters["m6_rail_width_y"]
        and parameters["m6_mount_plate_height_z"] > parameters["m6_rail_length_z"]
        and parameters["m6_yaw_stage_radius"]
        > parameters["m6_yaw_slot_radius"] + parameters["m6_stage_bolt_d"]
        and parameters["m6_yaw_slot_radius"] > parameters["m6_stage_bolt_d"]
        and parameters["m6_yaw_stage_t"] >= parameters["m6_yaw_plate_t"]
        and parameters["m6_yaw_stage_z"] < parameters["m6_array_bottom_z"]
        and parameters["m6_yaw_stage_z"]
        >= parameters["m6_array_center_z"] - parameters["m6_mount_plate_height_z"] / 2
        and parameters["m6_yaw_carrier_bottom_z"] < parameters["m6_array_center_z"]
        and parameters["m6_yaw_carrier_bottom_z"] + parameters["m6_yaw_carrier_height"]
        > parameters["m6_array_top_z"]
        and parameters["m6_pitch_yoke_width_y"] >= parameters["m6_mount_plate_width_y"]
        and parameters["m6_pitch_frame_t"] >= 4
        and parameters["m6_pitch_frame_outer_width_y"] > parameters["m6_pitch_frame_window_width_y"]
        and parameters["m6_pitch_frame_outer_height_z"] > parameters["m6_pitch_frame_window_height_z"]
        and parameters["m6_pitch_frame_window_width_y"] > parameters["m6_roll_plate_d"] + 6
        and parameters["m6_pitch_frame_window_height_z"] > parameters["m6_roll_plate_d"] + 6
        and parameters["m6_pitch_frame_spine_width_y"] > parameters["m6_roll_pivot_d"]
        and parameters["m6_pitch_frame_hub_d"] > parameters["m6_roll_pivot_d"]
        and parameters["m6_pitch_yoke_width_y"] > parameters["m6_pitch_frame_outer_width_y"] + 2
        and parameters["m6_pitch_pivot_z"] > parameters["m6_array_center_z"] - parameters["m6_pitch_frame_outer_height_z"] / 2
        and parameters["m6_pitch_pivot_z"] < parameters["m6_array_center_z"] + parameters["m6_pitch_frame_outer_height_z"] / 2
        and parameters["m6_roll_plate_d"] > parameters["m6_pivot_d"]
        and math.hypot(
            parameters["m6_rail_mount_hole_y"],
            parameters["m6_rail_mount_z_offset"],
        )
        + parameters["m6_rail_mount_clearance_d"] / 2
        < parameters["m6_roll_plate_d"] / 2
        and parameters["m6_pivot_d"] > parameters["m6_sensor_thread_d"]
        and parameters["m6_roll_pivot_d"] > parameters["m6_sensor_thread_d"]
        and math.hypot(
            parameters["m6_sensor_lane_offset_y"],
            parameters["m6_sensor_center_pitch"] / 2,
        )
        > (
            parameters["m6_sensor_body_clearance_d"]
            + parameters["m6_roll_pivot_d"]
        ) / 2
        and parameters["m6_stage_bolt_d"] > parameters["m6_fine_adjuster_d"]
        and parameters["m6_yaw_adjuster_block_width_x"] > parameters["m6_fine_adjuster_d"]
        and parameters["m6_yaw_adjuster_block_depth_y"] > 0
        and parameters["m6_yaw_adjuster_block_height_z"] > 2 * parameters["m6_yaw_stage_t"]
        and parameters["m6_yaw_adjuster_foot_inset_y"] > 0
        and parameters["m6_yaw_adjuster_tap_d"] < parameters["m6_fine_adjuster_d"]
        and parameters["m6_yaw_adjuster_tap_depth"] >= parameters["m6_yaw_adjuster_block_depth_y"]
        and 0 < parameters["m6_yaw_adjuster_tip_overtravel_y"] < parameters["m6_yaw_stage_t"] / 2
    ):
        raise RuntimeError(f"M6 three-axis gimbal parameters are inconsistent: {parameters}")
    if not (
        parameters["stg120_head_length"] == 130
        and parameters["stg120_active_length"] == 120
        and parameters["stg120_head_width"] == 19
        and parameters["stg120_head_thickness"] == 6
        and parameters["stg120_beam_count"] == 32
        and abs(parameters["stg120_beam_pitch"] - 3.87) < 0.001
        and parameters["stg120_detect_distance_max"] == 1000
        and parameters["stg120_outer_face_x"] >= table_edge
        and parameters["stg120_outer_frame_min_x"] < parameters["stg120_outer_face_x"]
        and parameters["stg120_outer_frame_max_x"] > parameters["stg120_outer_face_x"]
        and abs(parameters["stg120_reference_height"] - 13 * parameters["stg120_beam_pitch"]) < 0.001
    ):
        raise RuntimeError(f"STG-120ML geometry parameters are inconsistent: {parameters}")
    if not (
        0 < parameters["reference_pin_d"]
        < parameters["reference_pin_bore_d"]
        < parameters["optical_locating_hole_d"]
        and parameters["reference_pin_length"]
        > parameters["optical_rail_width"] + parameters["reference_carriage_depth"]
    ):
        raise RuntimeError(
            f"reference pin/bore cannot span the locating hole with print clearance: {parameters}"
        )
    if not (
        parameters["sensor_film_length"] > parameters["sensor_clamp_tab_width"] > 0
        and parameters["sensor_film_depth"] > 0
    ):
        raise RuntimeError(f"invalid removable PVDF film clamp dimensions: {parameters}")
    return parameters


def validate_current_m6_contract(parameters: dict[str, float]) -> None:
    """Validate the active 45-degree L-sensor body rather than the legacy rail."""

    source_text = SOURCE.read_text(encoding="utf-8")

    def module_text(name: str) -> str:
        marker = f"module {name}"
        start = source_text.find(marker)
        if start < 0:
            raise RuntimeError(f"current M6 source module is missing: {name}")
        next_module = source_text.find("\nmodule ", start + len(marker))
        return source_text[start:] if next_module < 0 else source_text[start:next_module]

    body_module = module_text("m6_detector_body_positive()")
    body_envelope_module = module_text("m6_detector_body_envelope_positive()")
    fit_body_module = module_text("m6_detector_fit_body_positive()")
    sensor_array_module = module_text("m6_detector_sensor_array_positive()")
    fit_sensor_module = module_text("m6_detector_fit_sensor_positive(index)")
    front_outer_module = module_text("m6_detector_front_outer_positive()")
    rear_outer_module = module_text("m6_detector_shell_rear_outer_positive()")
    rear_boss_module = module_text("m6_detector_shell_support_boss_positive()")
    rear_hole_module = module_text("m6_detector_shell_support_hole_positive()")
    front_shell_module = module_text("m6_detector_shell_front_positive(alpha = m6_detector_shell_alpha)")
    rear_shell_module = module_text("m6_detector_shell_rear_positive(alpha = m6_detector_shell_alpha)")
    bottom_cover_module = module_text("m6_detector_bottom_cover_positive()")
    mount_module = module_text("m6_detector_mount_positive()")
    exploded_module = module_text("m6_detector_exploded_positive()")
    if (
        "m6_detector_body_envelope_positive();" not in body_module
        or "cube([m6_detector_body_length_x" not in body_envelope_module
        or "m6_detector_body_t_tail_positive" in body_envelope_module
        or "m6_detector_body_tail_thread_void_positive" in body_module
        or "m6_detector_body_envelope_positive();" not in fit_body_module
        or "m6_detector_body_tail_thread_void_positive" in fit_body_module
        or "m6_detector_sensor_fit_voids_positive();" not in body_module
        or "m6_detector_sensor_fit_voids_positive();" not in fit_body_module
        or "m6_detector_sensor_installed_positive(index);" not in sensor_array_module
        or "m6_detector_sensor_installed_positive(index);" not in fit_sensor_module
        or "m6_sensor_head_width_y + 1.6" in body_module
        or "m6_detector_front_arc_footprint_positive();" not in front_outer_module
        or "m6_detector_rear_rounded_footprint_positive();" not in rear_outer_module
        or "m6_detector_shell_support_boss_positive();" not in rear_outer_module
        or "m6_detector_shell_support_hole_positive();" not in rear_shell_module
        or "m6_detector_body_tail_clearance_positive" in rear_shell_module
        or "m6_rounded_rect_prism_x(" not in rear_boss_module
        or "m6_cylinder_x(" not in rear_hole_module
        or "m6_detector_front_optical_holes_positive();" not in front_shell_module
        or "m6_detector_shell_footprint_positive();" not in bottom_cover_module
        or "m6_mount_adapter_positive();" in mount_module
        or "m6_post_mount_hardware_positive();" in mount_module
        or "m6_mount_adapter_positive();" in exploded_module
        or "m6_post_mount_hardware_positive();" in exploded_module
    ):
        raise RuntimeError(
            "active M6 body/fit path diverged: rectangular body, installed sensor "
            "voids, rear-cover boss/hole and z+ split-cover footprints must be used"
        )

    count = int(parameters["m6_sensor_count"])
    pitch = parameters["m6_sensor_center_pitch"]
    body_depth_limit = (
        parameters["m6_detector_fit_thread_length_x"]
        + parameters["m6_detector_fit_capture_depth_x"]
        - parameters["m6_sensor_lock_nut_h"]
        - parameters["m6_detector_fit_thread_tip_allowance_x"]
    )
    expected_body_bottom = (
        parameters["net_height"]
        + parameters["m6_sensor_first_height"]
        - parameters["m6_detector_body_margin_z"]
    )
    expected_body_top = (
        parameters["net_height"]
        + parameters["m6_sensor_first_height"]
        + (count - 1) * pitch
        + parameters["m6_detector_body_margin_z"]
    )
    expected_body_height = expected_body_top - expected_body_bottom
    expected_shell_width = (
        parameters["m6_detector_body_depth_y"]
        + 2 * parameters["m6_detector_shell_wall"]
    )
    expected_shell_split = (
        parameters["m6_sensor_axis_x"] + parameters["m6_sensor_head_length_x"] / 2
    )
    expected_shell_min = (
        expected_shell_split - parameters["m6_detector_front_cap_length_x"]
    )
    expected_shell_height = (
        expected_body_height
        + parameters["m6_detector_shell_bottom_lip_z"]
        + parameters["m6_detector_shell_top_lip_z"]
    )
    expected_body_min_y = (
        parameters["m6_detector_body_center_y"]
        - parameters["m6_detector_body_depth_y"] / 2
    )
    expected_body_max_y = (
        parameters["m6_detector_body_center_y"]
        + parameters["m6_detector_body_depth_y"] / 2
    )
    roll_rad = math.radians(parameters["m6_sensor_roll_deg"])
    # OpenSCAD's R_x(-45) maps the local z- cable branch to y-/z-.  This is
    # the physical tail-relief direction requested for the L sensor.
    rolled_stem_y = math.sin(roll_rad)
    rolled_stem_z = -math.cos(roll_rad)
    if not (
        count == 10
        and pitch == 20
        and math.isclose(
            parameters["m6_sensor_roll_deg"], -45, rel_tol=0, abs_tol=1e-4
        )
        and math.isclose(
            parameters["m6_detector_body_center_y"], 0.0, rel_tol=0, abs_tol=1e-4
        )
        and rolled_stem_y < 0
        and rolled_stem_z < 0
        and math.isclose(
            parameters["m6_sensor_head_length_x"]
            + parameters["m6_sensor_mount_stem_length"],
            20.0,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_sensor_thread_start_x"],
            parameters["m6_sensor_axis_x"] + parameters["m6_sensor_head_length_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_sensor_thread_end_x"],
            parameters["m6_sensor_overall_end_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_sensor_cable_guard_length"] > 0
        and parameters["m6_sensor_cable_preview_length"] > 0
        and parameters["m6_sensor_cable_d"] > 0
        and math.isclose(
            parameters["m6_sensor_cable_exit_x"],
            parameters["m6_sensor_axis_x"] + parameters["m6_sensor_head_length_x"] / 2,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_body_min_x"]
        < parameters["m6_sensor_axis_x"]
        < parameters["m6_detector_body_max_x"]
        and parameters["m6_detector_body_max_x"]
        < parameters["m6_sensor_thread_start_x"]
        + parameters["m6_sensor_lock_nut_h"]
        and math.isclose(
            parameters["m6_detector_body_min_y"],
            expected_body_min_y,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_body_max_y"],
            expected_body_max_y,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_body_min_y"]
        < parameters["m6_detector_sensor_head_center_y"]
        < parameters["m6_detector_body_max_y"]
        and parameters["m6_detector_body_length_x"] <= body_depth_limit
        and math.isclose(
            parameters["m6_detector_body_length_x"], body_depth_limit,
            rel_tol=0, abs_tol=1e-4
        )
        and parameters["m6_detector_body_depth_y"] > parameters["m6_sensor_head_width_y"] + 2
        and math.isclose(
            parameters["m6_detector_body_bottom_z"],
            expected_body_bottom,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_body_top_z"],
            expected_body_top,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_body_height_z"],
            expected_body_height,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_optical_bore_d"]
        > parameters["m6_sensor_thread_d"]
        and parameters["m6_detector_optical_bore_d"] < pitch
        and parameters["m6_detector_thread_clearance_d"]
        > parameters["m6_sensor_thread_d"]
        and math.isclose(
            parameters["m6_detector_hex_pocket_af"],
            parameters["m6_sensor_head_hex_af"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_hex_pocket_af"]
        < parameters["m6_sensor_lock_nut_af"]
        and 0 < parameters["m6_detector_hex_pocket_depth_y"]
        < parameters["m6_detector_body_length_x"]
        and math.isclose(
            parameters["m6_detector_hex_pocket_depth_y"],
            parameters["m6_detector_fit_capture_depth_x"] + 0.1,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_hex_pocket_floor"] > 0
        and parameters["m6_detector_hex_pocket_floor"]
        < parameters["m6_detector_hex_pocket_depth_y"]
    ):
        raise RuntimeError(f"current 45-degree L-sensor body contract is inconsistent: {parameters}")

    fit_visible = parameters["m6_detector_fit_thread_visible_length_x"]
    if not (
        parameters["m6_detector_fit_head_length_x"]
        > parameters["m6_detector_fit_capture_depth_x"] > 0
        and parameters["m6_detector_fit_head_width_y"] > 0
        and parameters["m6_detector_fit_head_height_z"] > 0
        and parameters["m6_detector_fit_head_clearance_y"] >= 0
        and parameters["m6_detector_fit_head_clearance_z"] >= 0
        and parameters["m6_detector_fit_thread_length_x"] > 0
        and parameters["m6_detector_fit_thread_clearance_d"]
        > parameters["m6_sensor_thread_d"]
        and fit_visible
        >= parameters["m6_sensor_lock_nut_h"]
        + parameters["m6_detector_fit_thread_tip_allowance_x"]
        - 0.01
        and math.isclose(
            parameters["m6_detector_fit_thread_tip_x"],
            parameters["m6_detector_fit_head_inner_x"]
            - parameters["m6_detector_fit_thread_length_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            fit_visible,
            parameters["m6_detector_body_min_x"]
            - parameters["m6_detector_fit_thread_tip_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_sensor_install_offset_x"],
            parameters["m6_detector_fit_head_center_x"]
            - parameters["m6_sensor_head_center_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_cable_exit_x"],
            parameters["m6_sensor_cable_exit_x"]
            + parameters["m6_detector_sensor_install_offset_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_shell_min_x"]
        < parameters["m6_detector_cable_exit_x"]
        < parameters["m6_detector_shell_max_x"]
    ):
        raise RuntimeError(f"minimal M6 fit-probe contract is inconsistent: {parameters}")

    if not (
        math.isclose(
            parameters["m6_detector_shell_width_y"],
            expected_shell_width,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_shell_height_z"],
            expected_shell_height,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_shell_front_max_x"]
        > parameters["m6_detector_shell_min_x"]
        and parameters["m6_detector_shell_rear_min_x"]
        < parameters["m6_detector_shell_max_x"]
        and parameters["m6_detector_shell_min_x"]
        < parameters["m6_detector_shell_split_x"]
        < parameters["m6_detector_shell_max_x"]
        and math.isclose(
            parameters["m6_detector_shell_split_x"],
            expected_shell_split,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_shell_min_x"],
            expected_shell_min,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_front_cap_length_x"]
        > parameters["m6_detector_shell_split_overlap_x"]
        and parameters["m6_detector_shell_front_max_x"]
        > parameters["m6_detector_shell_split_x"]
        and parameters["m6_detector_shell_rear_min_x"]
        < parameters["m6_detector_shell_split_x"]
        and parameters["m6_detector_shell_front_max_x"]
        > parameters["m6_detector_shell_rear_min_x"]
        and parameters["m6_detector_shell_split_overlap_x"] > 0
        and math.isclose(
            parameters["m6_detector_shell_front_min_y"],
            parameters["m6_detector_shell_min_y"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_shell_rear_max_y"],
            parameters["m6_detector_shell_max_y"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_body_groove_width_x"] / 2
        > 2 * parameters["m6_detector_shell_tongue_clearance"]
        and parameters["m6_detector_body_groove_depth_y"]
        > 2 * parameters["m6_detector_shell_tongue_clearance"]
        and parameters["m6_detector_body_groove_margin_z"] > 0
        and parameters["m6_detector_shell_tongue_depth_y"]
        > parameters["m6_detector_shell_tongue_clearance"]
        and parameters["m6_detector_shell_inner_min_x"]
        < parameters["m6_sensor_axis_x"]
        and parameters["m6_detector_shell_inner_min_x"]
        < parameters["m6_detector_fit_thread_tip_x"]
        and parameters["m6_detector_shell_min_x"]
        + parameters["m6_detector_shell_wall"]
        < parameters["m6_detector_fit_thread_tip_x"]
        and parameters["m6_detector_shell_wall"]
        < parameters["m6_detector_shell_front_max_x"]
        - parameters["m6_detector_shell_min_x"]
        and parameters["m6_detector_shell_inner_max_x"]
        > parameters["m6_sensor_overall_end_x"]
        and parameters["m6_detector_shell_corner_radius"]
        < min(
            parameters["m6_detector_shell_max_x"]
            - parameters["m6_detector_shell_rear_min_x"],
            parameters["m6_detector_shell_width_y"],
        )
        / 2
        and parameters["m6_detector_shell_clearance"] > 0
        and parameters["m6_detector_shell_wall"]
        > parameters["m6_detector_shell_clearance"]
        and parameters["m6_detector_bottom_cover_t"] > 0
        and parameters["m6_detector_cable_exit_d"]
        < parameters["m6_detector_shell_width_y"]
        and parameters["m6_detector_cable_exit_x"]
        - parameters["m6_detector_cable_exit_d"] / 2
        > parameters["m6_detector_shell_min_x"]
        and parameters["m6_detector_cable_exit_x"]
        + parameters["m6_detector_cable_exit_d"] / 2
        < parameters["m6_detector_shell_max_x"]
    ):
        raise RuntimeError(f"current M6 split shell/bottom cover contract is inconsistent: {parameters}")

    if not (
        parameters["m6_detector_shell_support_boss_min_x"]
        < parameters["m6_detector_shell_max_x"]
        < parameters["m6_detector_shell_support_boss_max_x"]
        and math.isclose(
            parameters["m6_detector_shell_support_boss_overlap_x"],
            parameters["m6_detector_shell_max_x"]
            - parameters["m6_detector_shell_support_boss_min_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_shell_support_boss_min_x"]
        >= parameters["m6_detector_shell_rear_min_x"]
        and parameters["m6_detector_shell_support_boss_min_y"]
        >= parameters["m6_detector_shell_min_y"]
        and parameters["m6_detector_shell_support_boss_max_y"]
        <= parameters["m6_detector_shell_max_y"]
        and parameters["m6_detector_shell_support_boss_min_y"]
        < parameters["m6_detector_body_center_y"]
        < parameters["m6_detector_shell_support_boss_max_y"]
        and math.isclose(
            parameters["m6_detector_shell_support_boss_center_y"],
            parameters["m6_detector_body_center_y"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_shell_support_boss_top_z"]
        > parameters["m6_detector_shell_support_boss_bottom_z"]
        and parameters["m6_detector_shell_support_boss_bottom_z"]
        < parameters["m6_detector_body_center_z"]
        < parameters["m6_detector_shell_support_boss_top_z"]
        and parameters["m6_detector_shell_support_boss_length_x"]
        == parameters["m6_detector_shell_support_boss_max_x"]
        - parameters["m6_detector_shell_support_boss_min_x"]
        and parameters["m6_detector_shell_support_boss_height_z"]
        == parameters["m6_detector_shell_support_boss_top_z"]
        - parameters["m6_detector_shell_support_boss_bottom_z"]
        and parameters["m6_detector_shell_support_boss_radius"] > 0
        and parameters["m6_detector_shell_support_hole_d"]
        > parameters["m6_ballhead_sensor_stud_d"]
        and parameters["m6_detector_shell_support_hole_depth_x"]
        <= parameters["m6_detector_shell_support_boss_length_x"]
        and parameters["m6_detector_shell_support_hole_entry_x"]
        == parameters["m6_detector_shell_support_boss_max_x"]
        and (
            parameters["m6_detector_ballhead_sensor_stud_center_x"]
            - parameters["m6_ballhead_sensor_stud_length"] / 2
            < parameters["m6_detector_shell_support_hole_entry_x"]
        )
        and (
            parameters["m6_detector_ballhead_sensor_stud_center_x"]
            + parameters["m6_ballhead_sensor_stud_length"] / 2
            > parameters["m6_detector_shell_support_hole_entry_x"]
            - parameters["m6_detector_shell_support_stud_engagement_x"]
        )
    ):
        raise RuntimeError(f"current M6 rear-cover boss and purchased ballhead interface is inconsistent: {parameters}")

    if not (
        math.isclose(
            parameters["m6_detector_ballhead_center_z"],
            parameters["m6_detector_body_center_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_ballhead_center_x"]
        > parameters["m6_detector_shell_support_hole_entry_x"]
        and math.isclose(
            parameters["m6_detector_ballhead_center_y"],
            parameters["m6_detector_shell_support_boss_center_y"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_ballhead_center_y"],
            parameters["m6_detector_body_center_y"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_ballhead_center_z"],
            parameters["m6_detector_body_center_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_ballhead_sensor_stud_center_x"],
            parameters["m6_detector_shell_support_hole_entry_x"]
            + parameters["m6_ballhead_sensor_stud_length"] / 2
            - parameters["m6_detector_shell_support_stud_engagement_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_ballhead_base_center_z"]
        < parameters["m6_detector_ballhead_center_z"]
        and parameters["m6_detector_ballhead_net_stud_center_z"]
        < parameters["m6_detector_ballhead_base_center_z"]
        and parameters["m6_ballhead_rotation_range_deg"] == 360
        and parameters["m6_ballhead_tilt_range_deg"] == 90
    ):
        raise RuntimeError(f"vertical commercial ballhead interface is inconsistent: {parameters}")


def main() -> None:
    openscad = find_openscad()
    with tempfile.TemporaryDirectory(prefix="pingpang-smartgear-net-stand-") as directory:
        output_dir = Path(directory)
        parameters = probe_parameters(openscad, output_dir)
        validate_current_m6_contract(parameters)

        for part in PARTS:
            output = output_dir / f"{part}.stl"
            require_stl(
                run_openscad(openscad, output, f'PART="{part}"'),
                output,
                f"PART={part}",
                require_closed=part not in PREVIEW_ONLY_PARTS,
            )

        # Compile both signs of each independent axis boundary on both
        # mirrored sides.  The nominal PART matrix proves that the assembly
        # renders; these states prove that yaw/pitch/roll can each reach the
        # advertised +/-4 degree adjustment envelope rather than only one
        # convenient combined pose.
        trim_states = (
            ("yaw-negative", ("m6_yaw_angle=-4",)),
            ("yaw-positive", ("m6_yaw_angle=4",)),
            ("pitch-negative", ("m6_pitch_angle=-4",)),
            ("pitch-positive", ("m6_pitch_angle=4",)),
            ("roll-negative", ("m6_roll_angle=-4",)),
            ("roll-positive", ("m6_roll_angle=4",)),
            (
                "combined-nonzero",
                ("m6_yaw_angle=3", "m6_pitch_angle=-2", "m6_roll_angle=2"),
            ),
        )
        for side in (1, -1):
            for label, trim_definitions in trim_states:
                trim_output = output_dir / f"m6-gimbal-trim-{label}-side-{side}.stl"
                require_stl(
                    run_openscad(
                        openscad,
                        trim_output,
                        'PART="m6_gimbal"',
                        *trim_definitions,
                        f"SIDE={side}",
                    ),
                    trim_output,
                    f"PART=m6_gimbal trim {label} SIDE={side}",
                    require_closed=False,
                )
        invalid_trim_states = (
            ("yaw", "m6_yaw_angle=4.1"),
            ("pitch", "m6_pitch_angle=-4.1"),
            ("roll", "m6_roll_angle=4.1"),
        )
        for label, definition in invalid_trim_states:
            invalid_trim = run_openscad(
                openscad,
                output_dir / f"invalid-m6-gimbal-{label}-trim.stl",
                'PART="m6_gimbal"',
                definition,
            )
            if invalid_trim.returncode == 0:
                raise RuntimeError(
                    f"OpenSCAD accepted a {label} trim outside the configured range"
                )

        mirrored_paths: dict[str, Path] = {}
        for part in (
            "post",
            "post_segment",
            "post_joint_sleeve",
            "post_joint_key",
            "lower_stand_segment",
            "table_clamp",
            "table_clamp_section",
            "table_clamp_body",
            "clamp_top_pad",
            "clamp_pressure_pad",
            "clamp_screw",
            "clamp_body_nut",
            "clamp_knob",
            "clamp_knob_nut",
            "net_rail_saddle",
            "optical_rail",
            "optical_strip",
            "optical_module_carrier",
            "m6_detector_body",
            "m6_detector_shell_front",
            "m6_detector_shell_rear",
            "m6_detector_bottom_cover",
            "m6_detector_mount",
            "stg120_outer_carrier",
            "sensor_mount",
            "sensor_mount_body",
            "pvdf_film",
            "sensor_clamp_lip",
            "reference_carriage",
            "reference_carriage_body",
            "reference_pin",
        ):
            mirrored = output_dir / f"{part}-mirror.stl"
            require_stl(
                run_openscad(
                    openscad,
                    mirrored,
                    f'PART="{part}"',
                    "SIDE=-1",
                ),
                mirrored,
                f"PART={part} SIDE=-1",
                require_closed=part not in PREVIEW_ONLY_PARTS,
            )
            mirrored_paths[part] = mirrored

        left_center = stl_x_center(output_dir / "left_stand.stl")
        right_center = stl_x_center(output_dir / "right_stand.stl")
        if not (left_center < 0 < right_center):
            raise RuntimeError(
                f"integrated stand sides are not separated: left={left_center}, right={right_center}"
            )
        for part, mirrored in mirrored_paths.items():
            default_center = stl_x_center(output_dir / f"{part}.stl")
            mirror_center = stl_x_center(mirrored)
            if not (default_center > 0 and mirror_center < 0):
                raise RuntimeError(f"{part} SIDE=-1 did not produce opposite geometry")
            default_signature = _stl_mirror_signature(
                output_dir / f"{part}.stl", reflect_x=False
            )
            mirror_signature = _stl_mirror_signature(mirrored, reflect_x=True)
            if (
                default_signature != mirror_signature
                or len(_stl_triangles(output_dir / f"{part}.stl"))
                != len(_stl_triangles(mirrored))
            ):
                raise RuntimeError(
                    f"{part} SIDE=-1 is not a vertex-set X mirror"
                )

        net_bounds = stl_bounds(output_dir / "net.stl")
        rail_bounds = stl_bounds(output_dir / "net_rail.stl")
        rail_segment_bounds = stl_bounds(output_dir / "net_rail_segment.stl")
        clamp_body_bounds = stl_bounds(output_dir / "table_clamp_body.stl")
        clamp_section_bounds = stl_bounds(output_dir / "table_clamp_section.stl")
        top_pad_bounds = stl_bounds(output_dir / "clamp_top_pad.stl")
        pressure_pad_bounds = stl_bounds(output_dir / "clamp_pressure_pad.stl")
        screw_bounds = stl_bounds(output_dir / "clamp_screw.stl")
        body_nut_bounds = stl_bounds(output_dir / "clamp_body_nut.stl")
        knob_bounds = stl_bounds(output_dir / "clamp_knob.stl")
        knob_nut_bounds = stl_bounds(output_dir / "clamp_knob_nut.stl")
        sensor_bounds = stl_bounds(output_dir / "sensor_mount.stl")
        film_bounds = stl_bounds(output_dir / "pvdf_film.stl")
        film_lip_bounds = stl_bounds(output_dir / "sensor_clamp_lip.stl")
        # Use the body-only envelope for pin span checks; the combined preview
        # intentionally contains the pin itself and would hide an absent bore.
        reference_bounds = stl_bounds(output_dir / "reference_carriage_body.stl")
        reference_pin_bounds = stl_bounds(output_dir / "reference_pin.stl")
        saddle_bounds = stl_bounds(output_dir / "net_rail_saddle.stl")
        optical_rail_bounds = stl_bounds(output_dir / "optical_rail.stl")
        carrier_bounds = stl_bounds(output_dir / "optical_module_carrier.stl")
        stg_outer_bounds = stl_bounds(output_dir / "stg120_outer_carrier.stl")
        stg_center_bounds = stl_bounds(output_dir / "stg120_center_bridge.stl")
        stg_preview_bounds = stl_bounds(output_dir / "stg120_preview.stl")
        coupon_bounds = stl_bounds(output_dir / "m6_sensor_test_coupon.stl")
        assembly_bounds = stl_bounds(output_dir / "assembly.stl")
        post_bounds = stl_bounds(output_dir / "post.stl")
        post_segment_bounds = stl_bounds(output_dir / "post_segment.stl")
        lower_stand_bounds = stl_bounds(output_dir / "lower_stand_segment.stl")
        if net_bounds[0] >= 0 or net_bounds[1] <= 0:
            raise RuntimeError(f"net is not centered across the table: {net_bounds}")
        if rail_bounds[0] >= 0 or rail_bounds[1] <= 0:
            raise RuntimeError(f"net rail is not centered across the table: {rail_bounds}")
        if abs(net_bounds[5] - (parameters["net_height"] - parameters["net_rail_height"])) > 0.01:
            raise RuntimeError(f"net panel top does not meet the net rail datum: {net_bounds}")
        if abs(rail_bounds[5] - parameters["net_height"]) > 0.01:
            raise RuntimeError(f"net rail top does not match net height: {rail_bounds}")
        if not (
            abs(rail_bounds[0] + parameters["net_span"] / 2) < 0.01
            and abs(rail_bounds[1] - parameters["net_span"] / 2) < 0.01
            and rail_segment_bounds[1] - rail_segment_bounds[0]
            > 500
        ):
            raise RuntimeError(
                f"segmented net rail does not cover the full span: rail={rail_bounds}, "
                f"segment={rail_segment_bounds}"
            )
        inner_face = parameters["post_center_x"] - parameters["post_body_width"] / 2
        if not (
            saddle_bounds[0] < inner_face < saddle_bounds[1]
            and saddle_bounds[3] - saddle_bounds[2] > parameters["net_rail_depth"]
            and abs(saddle_bounds[5] - parameters["net_height"]) < 0.01
        ):
            raise RuntimeError(f"rail saddle does not support/stop the net rail: {saddle_bounds}")
        carrier_center_z = (carrier_bounds[4] + carrier_bounds[5]) / 2
        if not (
            carrier_bounds[1] - carrier_bounds[0] > parameters["optical_module_depth"]
            and carrier_bounds[3] - carrier_bounds[2] > parameters["optical_module_width"]
            and carrier_bounds[5] - carrier_bounds[4] > parameters["optical_module_height"]
            and abs(carrier_center_z - (parameters["net_height"] + parameters["beam_first_height"])) < 0.01
        ):
            raise RuntimeError(f"optical module carrier envelope is not centered on channel 0: {carrier_bounds}")
        if not (
            stg_outer_bounds[0] >= parameters["stg120_outer_frame_min_x"] - 0.01
            and stg_outer_bounds[1] <= parameters["stg120_outer_frame_max_x"] + 0.01
            and stg_outer_bounds[1] > parameters["table_width"] / 2
            and stg_outer_bounds[3] - stg_outer_bounds[2] >= parameters["stg120_head_width"]
            and stg_outer_bounds[5] - stg_outer_bounds[4] >= parameters["stg120_head_length"]
        ):
            raise RuntimeError(f"STG-120ML outer carrier does not retain the head envelope: {stg_outer_bounds}")
        if not (
            stg_center_bounds[1] - stg_center_bounds[0] >= 20
            and stg_center_bounds[3] - stg_center_bounds[2] > parameters["stg120_head_width"]
            and stg_center_bounds[5] - stg_center_bounds[4] >= parameters["stg120_head_length"]
            and stg_center_bounds[0] < 0 < stg_center_bounds[1]
            and stg_preview_bounds[0] < -parameters["table_width"] / 2
            and stg_preview_bounds[1] > parameters["table_width"] / 2
        ):
            raise RuntimeError(
                f"STG-120ML central bridge or two-segment preview is inconsistent: "
                f"center={stg_center_bounds}, preview={stg_preview_bounds}"
            )
        if not (
            optical_rail_bounds[3] - optical_rail_bounds[2] <= parameters["optical_rail_width"] + 0.01
            and optical_rail_bounds[4] < parameters["net_height"]
            and optical_rail_bounds[5] > parameters["net_height"] + parameters["beam_last_height"]
        ):
            raise RuntimeError(f"printable optical rail envelope is not a standalone guide: {optical_rail_bounds}")
        expected_reference_z = parameters["net_height"] + 50
        if not (
            reference_bounds[4] < expected_reference_z < reference_bounds[5]
        ):
            raise RuntimeError(f"reference carriage is not at the selected detent: {reference_bounds}")
        reference_pin_axis_x = (
            parameters["optical_rail_x"] + parameters["optical_rail_depth"] / 2
        )
        if not (
            abs((reference_pin_bounds[0] + reference_pin_bounds[1]) / 2 - reference_pin_axis_x)
            < 0.01
            and abs((reference_pin_bounds[4] + reference_pin_bounds[5]) / 2 - expected_reference_z)
            < 0.01
            and reference_pin_bounds[2] < reference_bounds[2]
            and reference_pin_bounds[3] > reference_bounds[3]
            and reference_pin_bounds[2] < -parameters["optical_rail_width"] / 2
            and reference_pin_bounds[3] > parameters["optical_rail_width"] / 2
        ):
            raise RuntimeError(
                "reference pin does not span the carriage and optical rail on the selected detent: "
                f"carriage={reference_bounds}, pin={reference_pin_bounds}"
            )
        if not (
            clamp_body_bounds[0] < parameters["table_width"] / 2 < clamp_body_bounds[1]
            and clamp_body_bounds[1] > parameters["clamp_pad_outer_x"] - 0.01
        ):
            raise RuntimeError(f"fixed clamp body does not bridge the table edge: {clamp_body_bounds}")
        if not (
            abs(top_pad_bounds[0] - parameters["clamp_top_pad_x"]) < 0.01
            and abs(
                top_pad_bounds[1]
                - (parameters["clamp_top_pad_x"] + parameters["clamp_top_pad_width"])
            )
            < 0.01
            and abs(
                top_pad_bounds[3]
                - top_pad_bounds[2]
                - parameters["clamp_top_pad_depth"]
            )
            < 0.01
            and top_pad_bounds[4] >= -0.01
            and top_pad_bounds[5] <= parameters["clamp_top_pad_t"] + 0.01
        ):
            raise RuntimeError(f"upper protective pad envelope is inconsistent: {top_pad_bounds}")
        if not (
            clamp_section_bounds[0] < parameters["table_width"] / 2 < clamp_section_bounds[1]
            and clamp_section_bounds[1] > parameters["clamp_pad_outer_x"] - 0.01
            and clamp_section_bounds[2] < 0 < clamp_section_bounds[3]
            and clamp_section_bounds[4] <= parameters["clamp_knob_bottom_z"] + 0.01
            and clamp_section_bounds[5] > 0
            and clamp_section_bounds[3] - clamp_section_bounds[2]
            <= parameters["clamp_pad_depth"] + 0.01
        ):
            raise RuntimeError(
                "table clamp section does not expose the complete no-drill path: "
                f"section={clamp_section_bounds}"
            )
        if not (
            pressure_pad_bounds[5] < -parameters["table_thickness"]
            and screw_bounds[5] < -parameters["table_thickness"]
            and screw_bounds[5] <= pressure_pad_bounds[4] + 0.01
            and abs(pressure_pad_bounds[5] - parameters["clamp_pressure_pad_top_z"]) < 0.01
            and abs(screw_bounds[5] - parameters["clamp_screw_top_z"]) < 0.01
            and abs(knob_bounds[4] - parameters["clamp_knob_bottom_z"]) < 0.01
            and abs(knob_bounds[5] - parameters["clamp_knob_top_z"]) < 0.01
            and screw_bounds[4] < knob_bounds[5]
            and knob_nut_bounds[4] >= knob_bounds[4] - 0.01
            and knob_nut_bounds[5] <= knob_bounds[5] + 0.01
            and body_nut_bounds[4] >= parameters["clamp_lower_arm_bottom_z"] - 0.01
            and body_nut_bounds[5] <= parameters["clamp_lower_arm_bottom_z"] +
            parameters["clamp_nut_pocket_depth"] + 0.01
        ):
            raise RuntimeError(
                "pressure pad, M8 tip or nut capture breaks the no-drill clamp path: "
                f"pad={pressure_pad_bounds}, screw={screw_bounds}, "
                f"body_nut={body_nut_bounds}, knob={knob_bounds}, knob_nut={knob_nut_bounds}"
            )
        if not (
            sensor_bounds[2] < -parameters["net_rail_depth"] / 2
            and abs(sensor_bounds[3] + parameters["net_rail_depth"] / 2) < 0.01
        ):
            raise RuntimeError(f"PVDF mount does not reach the net rail front face: {sensor_bounds}")
        if not (
            film_bounds[2] < film_bounds[3]
            and film_lip_bounds[2] < film_bounds[2]
            and film_lip_bounds[3] > film_bounds[3]
        ):
            raise RuntimeError(
                f"removable PVDF film is not captured by the clamp lips: "
                f"film={film_bounds}, lips={film_lip_bounds}"
            )
        if assembly_bounds[2] >= 0 or assembly_bounds[3] <= 0:
            raise RuntimeError(f"assembly does not include the table-depth axis: {assembly_bounds}")
        if assembly_bounds[5] <= parameters["net_height"] + parameters["beam_last_height"]:
            raise RuntimeError(f"uprights do not clear the optical window: {assembly_bounds}")
        if not (
            abs(post_bounds[4] - parameters["post_bottom"]) < 0.01
            and post_bounds[5] > parameters["net_height"] + parameters["beam_last_height"]
            and post_segment_bounds[5] - post_segment_bounds[4] < 240
            and post_segment_bounds[1] - post_segment_bounds[0] > parameters["post_body_width"]
            and post_segment_bounds[3] - post_segment_bounds[2] > parameters["post_body_depth"]
        ):
            raise RuntimeError(
                f"post assembly/segment bounds or lower reinforcement are not printable: post={post_bounds}, "
                f"segment={post_segment_bounds}"
            )
        if not (
            lower_stand_bounds[0] <= parameters["clamp_pad_x"] + 0.01
            and lower_stand_bounds[1] >= parameters["clamp_pad_outer_x"] - 0.01
            and lower_stand_bounds[3] - lower_stand_bounds[2]
            >= parameters["clamp_pad_depth"] - 0.01
            and lower_stand_bounds[4] <= parameters["clamp_lower_arm_bottom_z"] + 0.01
            and lower_stand_bounds[5] >= post_segment_bounds[5] - 0.01
        ):
            raise RuntimeError(
                "integrated lower stand segment does not contain both the post and C clamp: "
                f"lower={lower_stand_bounds}, post_segment={post_segment_bounds}"
            )
        if not (
            coupon_bounds[0] < 0 < coupon_bounds[1]
            and coupon_bounds[3] - coupon_bounds[2]
            >= parameters["m6_rail_width_y"] - 0.01
            and coupon_bounds[4] >= -0.01
            and coupon_bounds[5] - coupon_bounds[4]
            >= parameters["m6_sensor_test_coupon_backbone_h"] - 0.01
            and coupon_bounds[1] - coupon_bounds[0]
            > parameters["m6_sensor_guard_outer_d"]
        ):
            raise RuntimeError(
                "M6 single-sensor fit coupon does not contain the backbone, tab and guard envelope: "
                f"coupon={coupon_bounds}"
            )

        for table_thickness in NO_DRILL_TABLE_THICKNESSES:
            validate_no_drill_thickness(
                openscad,
                output_dir,
                table_thickness,
                parameters["clamp_top_pad_t"],
                parameters["clamp_knob_nut_stack_depth"],
            )

        invalid_grid = run_openscad(
            openscad,
            output_dir / "invalid-grid.stl",
            'PART="assembly"',
            "beam_count=9",
        )
        if invalid_grid.returncode == 0:
            raise RuntimeError("OpenSCAD accepted beam_count=9")

        invalid_reference = run_openscad(
            openscad,
            output_dir / "invalid-reference.stl",
            'PART="assembly"',
            "reference_height=55",
        )
        if invalid_reference.returncode == 0:
            raise RuntimeError("OpenSCAD accepted a reference line outside the 10 mm grid")

        invalid_reference_bore = run_openscad(
            openscad,
            output_dir / "invalid-reference-bore.stl",
            'PART="reference_carriage_body"',
            "reference_pin_bore_d=3",
        )
        if invalid_reference_bore.returncode == 0:
            raise RuntimeError("OpenSCAD accepted a reference pin bore without print clearance")

        for height in range(10, 101, 10):
            detent = output_dir / f"reference-{height}.stl"
            require_stl(
                run_openscad(
                    openscad,
                    detent,
                    'PART="assembly"',
                    f"reference_height={height}",
                ),
                detent,
                f"reference_height={height}",
                require_closed=False,
            )

        for index in range(10):
            carrier = output_dir / f"optical-carrier-{index}.stl"
            require_stl(
                run_openscad(
                    openscad,
                    carrier,
                    'PART="optical_module_carrier"',
                    f"optical_module_index={index}",
                ),
                carrier,
                f"optical_module_index={index}",
            )
        invalid_carrier = run_openscad(
            openscad,
            output_dir / "invalid-optical-carrier.stl",
            'PART="optical_module_carrier"',
            "optical_module_index=10",
        )
        if invalid_carrier.returncode == 0:
            raise RuntimeError("OpenSCAD accepted a non-existent optical module index")

        for index in range(3):
            segment = output_dir / f"net-rail-segment-{index}.stl"
            require_stl(
                run_openscad(
                    openscad,
                    segment,
                    'PART="net_rail_segment"',
                    f"rail_segment_index={index}",
                ),
                segment,
                f"net_rail_segment index={index}",
            )
        for index in range(2):
            splice = output_dir / f"net-rail-splice-{index}.stl"
            require_stl(
                run_openscad(
                    openscad,
                    splice,
                    'PART="net_rail_splice"',
                    f"rail_splice_index={index}",
                ),
                splice,
                f"net_rail_splice index={index}",
            )
        invalid_segment = run_openscad(
            openscad,
            output_dir / "invalid-rail-segment.stl",
            'PART="net_rail_segment"',
            "rail_segment_index=3",
        )
        if invalid_segment.returncode == 0:
            raise RuntimeError("OpenSCAD accepted a non-existent net rail segment")
        for index in range(2):
            segment = output_dir / f"post-segment-{index}.stl"
            require_stl(
                run_openscad(
                    openscad,
                    segment,
                    'PART="post_segment"',
                    f"post_segment_index={index}",
                ),
                segment,
                f"post_segment index={index}",
            )
        invalid_post_segment = run_openscad(
            openscad,
            output_dir / "invalid-post-segment.stl",
            'PART="post_segment"',
            "post_segment_index=2",
        )
        if invalid_post_segment.returncode == 0:
            raise RuntimeError("OpenSCAD accepted a non-existent post segment")
        invalid_splice = run_openscad(
            openscad,
            output_dir / "invalid-rail-splice.stl",
            'PART="net_rail_splice"',
            "rail_splice_index=2",
        )
        if invalid_splice.returncode == 0:
            raise RuntimeError("OpenSCAD accepted a non-existent net rail splice")

    print(
        "NET_STAND_OK "
        f"(table {parameters['table_width']:g} mm, net {parameters['net_height']:g} mm, "
        f"STG-120ML {int(parameters['stg120_beam_count'])}×{parameters['stg120_beam_pitch']:g} mm, "
        f"legacy optical +{parameters['beam_first_height']:g}..+{parameters['beam_last_height']:g} mm, "
        f"no-drill table thickness "
        f"{','.join(str(value) for value in NO_DRILL_TABLE_THICKNESSES)} mm)"
    )


if __name__ == "__main__":
    main()
