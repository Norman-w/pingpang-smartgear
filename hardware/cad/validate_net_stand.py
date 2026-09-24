#!/usr/bin/env python3
"""Validate the current integrated net-stand OpenSCAD parameter source."""

from __future__ import annotations

import re
import math
import struct
import subprocess
import tempfile
from pathlib import Path

from build_print_platter import dimensions, rotation_matrix_xyz, transform_bounds
from validate_scad import find_openscad, stl_bounds, stl_x_center


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_stand.scad"
PARTS = (
    "assembly",
    "left_stand",
    "right_stand",
    "post",
    "post_segment",
    "post_clamp_carrier",
    "post_clamp_carrier_lower",
    "post_clamp_carrier_upper",
    "clamp_body_segment",
    "clamp_body_half_user",
    "clamp_body_half_opponent",
    "post_clamp_slide_exploded",
    "post_clamp_slide_interface_exploded",
    "clamp_slide_post_foot_detent_detail",
    "post_joint_exploded",
    "clamp_slide_exploded",
    "clamp_slide_fit_probe",
    "clamp_slide_fit_section",
    "table_clamp",
    "table_clamp_section",
    "table_clamp_body",
    "clamp_electronics_ui_panel",
    "clamp_electronics_ui_panel_mount",
    "clamp_electronics_emitter_preview",
    "clamp_electronics_system_preview",
    "clamp_electronics_full_cutaway",
    "clamp_electronics_exploded",
    "clamp_electronics_emitter_exploded",
    "clamp_electronics_system_exploded",
    "table_clamp_electronics_preview",
    "table_clamp_electronics_cutaway_preview",
    "clamp_top_pad",
    "clamp_pressure_pad",
    "clamp_pressure_pad_guard",
    "clamp_screw",
    "clamp_printed_screw",
    "clamp_body_nut",
    "clamp_knob",
    "clamp_knob_nut",
    "net",
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
    "m6_detector_wiring_reference",
    "m6_detector_bottom_gasket",
    "m6_detector_cable_gland",
    "net_clamp_fit_probe",
    "net_clamp_fit_section",
    "net_clamp_rod",
    "m6_detector_net_connector",
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
    "post_clamp_slide_exploded",
    "post_clamp_slide_interface_exploded",
    "clamp_slide_post_foot_detent_detail",
    "post_joint_exploded",
    "clamp_slide_exploded",
    "clamp_slide_fit_probe",
    "clamp_slide_fit_section",
    "table_clamp_section",
    "table_clamp",
    "net",
    "optical_strip",
    "m6_sensor_rail",
    "m6_sensor_array",
    "m6_detector_fit_probe",
    "m6_detector_fit_body",
    "m6_detector_mount",
    "m6_detector_net_connector",
    "net_clamp_fit_probe",
    "net_clamp_fit_section",
    "m6_ballhead",
    "m6_gimbal",
    "stg120_preview",
    "sensor_mount",
    "reference_carriage",
    "table_clamp_electronics_preview",
    "table_clamp_electronics_cutaway_preview",
    "clamp_electronics_ui_panel",
    "clamp_electronics_emitter_preview",
    "clamp_electronics_system_preview",
    "clamp_electronics_full_cutaway",
    "clamp_electronics_exploded",
    "clamp_electronics_emitter_exploded",
    "clamp_electronics_system_exploded",
    "m6_detector_wiring_reference",
}
# The formal gray C body is printable, but its SKP-pocket subtraction includes
# Minkowski-expanded tools. OpenSCAD may tessellate the reflected CSG with a
# different diagonal/facet split; center/bounds are still checked while strict
# vertex-set equality remains for direct primitive print parts.
MIRROR_TRIANGULATION_RELAXED_PARTS = PREVIEW_ONLY_PARTS | {
    "clamp_body_segment",
    "clamp_body_half_user",
    "clamp_body_half_opponent",
}
NO_DRILL_TABLE_THICKNESSES = (12, 18, 25, 30, 40)


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


def _stl_component_count(path: Path, tolerance: float = 1e-6) -> int:
    """Return the number of edge-connected solids in an STL mesh."""

    triangles = _stl_triangles(path)
    if not triangles:
        return 0

    def vertex_key(point: tuple[float, float, float]) -> tuple[int, int, int]:
        return tuple(int(round(value / tolerance)) for value in point)

    edge_to_triangles: dict[
        tuple[tuple[int, int, int], tuple[int, int, int]], list[int]
    ] = {}
    for index, triangle in enumerate(triangles):
        keys = tuple(vertex_key(point) for point in triangle)
        for start, end in (
            (keys[0], keys[1]),
            (keys[1], keys[2]),
            (keys[2], keys[0]),
        ):
            edge = tuple(sorted((start, end)))
            edge_to_triangles.setdefault(edge, []).append(index)

    adjacency: list[set[int]] = [set() for _ in triangles]
    for connected in edge_to_triangles.values():
        for index in connected:
            adjacency[index].update(
                other for other in connected if other != index
            )

    unseen = set(range(len(triangles)))
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            index = stack.pop()
            for other in adjacency[index]:
                if other in unseen:
                    unseen.remove(other)
                    stack.append(other)
    return components


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


def validate_electronics_interference_probes(
    openscad: str, output_dir: Path
) -> None:
    """Require the electronics collision PARTs to stay geometrically empty.

    OpenSCAD omits an STL and exits with code 1 for an empty intersection. That
    is the intended pass state here; a non-empty STL means a board, canonical
    component solid, or structural shell has positive-volume penetration.
    """

    collision_parts = (
        "clamp_electronics_interference_check",
        "clamp_electronics_emitter_interference_check",
        "clamp_electronics_ui_internal_interference_check",
        "clamp_electronics_ui_proxy_board_collision",
        "clamp_electronics_board_end_bracket_main_board_collision",
        "clamp_electronics_emitter_clip_board_collision",
        "clamp_split_boss_main_board_collision",
    )
    for part in collision_parts:
        output = output_dir / f"{part}.stl"
        result = run_openscad(openscad, output, f'PART="{part}"')
        if "Current top level object is empty" not in result.stdout:
            raise RuntimeError(
                f"electronics collision probe {part} is not empty:\n{result.stdout}"
            )
        if output.is_file() and output.stat().st_size > 0:
            volume_mm3 = _stl_volume(output)
            if volume_mm3 > 0.01:
                raise RuntimeError(
                    f"electronics collision probe {part} has positive-volume overlap: "
                    f"volume_mm3={volume_mm3:.3f}"
                )

    layout_output = output_dir / "clamp_electronics_ui_proxy_layout_check.stl"
    layout_result = run_openscad(
        openscad,
        layout_output,
        'PART="clamp_electronics_ui_proxy_layout_check"',
    )
    if "UI_PROXY_LAYOUT_OK" not in layout_result.stdout:
        raise RuntimeError(
            "UI component layout did not satisfy the faceplate clearance contract:\n"
            f"{layout_result.stdout}"
        )

    alignment_output = output_dir / "clamp_electronics_ui_component_alignment_check.stl"
    alignment_result = run_openscad(
        openscad,
        alignment_output,
        'PART="clamp_electronics_ui_component_alignment_check"',
    )
    if "UI_COMPONENT_ALIGNMENT_OK" not in alignment_result.stdout:
        raise RuntimeError(
            "SCAD electronics component alignment contract failed:\n"
            f"{alignment_result.stdout}"
        )


def validate_post_clamp_slide_path(
    openscad: str, output_dir: Path, parameters: dict[str, float]
) -> None:
    """Prove the coplanar seat and the later x-only service clear-out path.

    The current upright starts exactly on the fixed C-clamp's z=16 mm upper
    support plane.  The two printable solids may share that boundary face, but
    they must not have a positive-volume intersection at the seated datum or
    at any sampled x-only slide position.
    """

    offsets = (0, 0.5, 1, 1.5, 2, 4, 8, 41, 82)
    for side in (1, -1):
        for offset in offsets:
            output = output_dir / f"post-clamp-collision-side-{side}-{offset:g}.stl"
            result = run_openscad(
                openscad,
                output,
                'PART="post_clamp_fit_collision_probe_at_offset"',
                f"SIDE={side}",
                f"fit_probe_offset_x={offset}",
            )
            empty_probe = "Current top level object is empty" in result.stdout
            if result.returncode != 0 and not empty_probe:
                raise RuntimeError(
                    f"OpenSCAD rejected the post/clamp path probe SIDE={side} "
                    f"offset={offset:g}:\n{result.stdout}"
                )
            # OpenSCAD may omit a completely empty STL.  A coplanar seat has
            # zero volume; any positive-volume result is an unintended
            # penetration into the fixed C-clamp.
            volume_mm3 = 0.0
            if output.is_file() and output.stat().st_size > 0:
                volume_mm3 = _stl_volume(output)
            if volume_mm3 > 0.01:
                raise RuntimeError(
                    "post/clamp carrier has positive-volume penetration; the seat must be coplanar: "
                    f"SIDE={side}, offset={offset:g}, volume_mm3={volume_mm3:.3f}"
                )
    if not (
        parameters["clamp_slide_entry_open_x"]
        > parameters["clamp_fixed_body_max_x"]
        and parameters["clamp_slide_entry_open_x"]
        >= parameters["clamp_fixed_body_max_x"]
        + parameters["clamp_slide_clearance"]
    ):
        raise RuntimeError(
            "female slideway entry is not open through the fixed body's x+ face: "
            f"entry={parameters['clamp_slide_entry_open_x']}, "
            f"body_max={parameters['clamp_fixed_body_max_x']}"
        )


def validate_no_drill_thickness(
    openscad: str,
    output_dir: Path,
    table_thickness: int,
    top_pad_t: float,
    pressure_pad_socket_depth: float,
    knob_nut_stack_depth: float,
    body_nut_z: float,
    body_nut_top_z: float,
    pressure_pad_t: float,
    retainer_h: float,
    retainer_top_clearance_z: float,
    retainer_outer_d: float,
) -> None:
    """Compile the under-table pressure path for a first-pass thickness matrix."""

    definitions = (f"table_thickness={table_thickness}",)
    body = output_dir / f"table-clamp-body-{table_thickness}.stl"
    top_pad = output_dir / f"top-pad-{table_thickness}.stl"
    pad = output_dir / f"pressure-pad-{table_thickness}.stl"
    guard = output_dir / f"pressure-pad-guard-{table_thickness}.stl"
    screw = output_dir / f"clamp-screw-{table_thickness}.stl"
    printed_screw = output_dir / f"clamp-printed-screw-{table_thickness}.stl"
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
        run_openscad(openscad, guard, 'PART="clamp_pressure_pad_guard"', *definitions),
        guard,
        f"pressure pad back guard table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, screw, 'PART="clamp_screw"', *definitions),
        screw,
        f"clamp screw table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, printed_screw, 'PART="clamp_printed_screw"', *definitions),
        printed_screw,
        f"coarse printed clamp screw table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, body_nut, 'PART="clamp_body_nut"', *definitions),
        body_nut,
        f"fixed coarse PETG nut table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, knob, 'PART="clamp_knob"', *definitions),
        knob,
        f"clamp knob table_thickness={table_thickness}",
    )
    require_stl(
        run_openscad(openscad, knob_nut, 'PART="clamp_knob_nut"', *definitions),
        knob_nut,
        f"captured coarse PETG nuts table_thickness={table_thickness}",
    )
    top_pad_bounds = stl_bounds(top_pad)
    pad_bounds = stl_bounds(pad)
    guard_bounds = stl_bounds(guard)
    screw_bounds = stl_bounds(screw)
    printed_screw_bounds = stl_bounds(printed_screw)
    body_nut_bounds = stl_bounds(body_nut)
    knob_bounds = stl_bounds(knob)
    knob_nut_bounds = stl_bounds(knob_nut)
    tabletop_bottom = -float(table_thickness)
    pad_body_bottom_z = pad_bounds[5] - pressure_pad_t
    retainer_top_z = pad_body_bottom_z - retainer_top_clearance_z
    retainer_bottom_z = retainer_top_z - retainer_h
    guard_components = _stl_component_count(guard)
    if guard_components != 1:
        raise RuntimeError(
            "pressure pad retainer is not one connected printed part: "
            f"components={guard_components}"
        )
    if not (
        top_pad_bounds[4] >= -0.01
        and top_pad_bounds[5] <= top_pad_t + 0.01
        and pad_bounds[5] < tabletop_bottom
        and screw_bounds[5] < tabletop_bottom
        and screw_bounds[5] <= pad_body_bottom_z + pressure_pad_socket_depth + 0.01
        and printed_screw_bounds[5] < tabletop_bottom
        and printed_screw_bounds[5] <= pad_body_bottom_z + pressure_pad_socket_depth + 0.01
        and guard_bounds[2] < guard_bounds[3]
        and guard_bounds[4] < pad_body_bottom_z
        and abs(guard_bounds[4] - retainer_bottom_z) < 0.01
        and abs(guard_bounds[5] - retainer_top_z) < 0.01
        and abs(
            (guard_bounds[1] - guard_bounds[0]) - retainer_outer_d
        ) < 0.02
        and body_nut_bounds[5] < tabletop_bottom
        and body_nut_bounds[4] >= body_nut_z - 0.01
        and body_nut_bounds[5] <= body_nut_top_z + 0.01
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
        "net_fixture_bottom_z",
        "net_height",
        "net_top_rail_required",
        "net_panel_top_z",
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
        "clamp_slide_interface_enabled",
        "post_bottom",
        "post_interface_transition_height_z",
        "post_interface_transition_extra_x",
        "post_interface_transition_extra_y",
        "post_c_clamp_overlap_depth_z",
        "post_interface_transition_bottom_width_x",
        "post_interface_transition_bottom_depth_y",
        "post_lower_overlap_solid_height_z",
        "post_interface_transition_start_z",
        "post_interface_transition_top_z",
        "post_interface_transition_outer_max_x",
        "net_post_top_z",
        "post_segment_count",
        "post_segment_length",
        "post_joint_gap",
        "preview_fit_display_gap",
        "post_joint_above_net_clearance_z",
        "active_post_top_z",
        "active_post_total_height",
        "active_post_segment_length",
        "active_post_joint_z",
        "post_split_z",
        "post_lower_segment_z",
        "post_lower_segment_height",
        "post_upper_segment_z",
        "post_upper_segment_height",
        "m4_joint_bolt_clearance_d",
        "m4_joint_bolt_length",
        "m4_joint_bolt_z_offset",
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
        "sensor_length",
        "sensor_depth",
        "sensor_height",
        "sensor_post_clearance_x",
        "sensor_film_y",
        "sensor_film_height",
        "sensor_film_length",
        "sensor_film_depth",
        "sensor_clamp_tab_width",
        "clamp_reach_inboard",
        "clamp_tongue_extra_length_x",
        "clamp_tongue_reach_inboard",
        "clamp_pad_x",
        "clamp_split_plane_y",
        "clamp_split_seam_gap_y",
        "clamp_split_boss_d",
        "clamp_split_boss_depth_y",
        "clamp_split_lower_boss_d",
        "clamp_split_lower_boss_board_clearance_z",
        "clamp_split_lower_boss_drop_z",
        "clamp_split_lower_right_x",
        "clamp_split_lower_right_z",
        "clamp_split_lower_left_x",
        "clamp_split_lower_left_z",
        "clamp_split_boss_min_cavity_overlap_x",
        "clamp_split_fastener_d",
        "clamp_split_fastener_head_d",
        "clamp_split_fastener_head_depth_y",
        "clamp_split_fastener_label_size",
        "clamp_split_fastener_label_height",
        "clamp_split_fastener_label_offset_x",
        "clamp_split_fastener_label_pocket_depth_y",
        "clamp_split_fastener_label_floor_overlap_y",
        "clamp_split_nut_af",
        "clamp_split_nut_depth_y",
        "clamp_split_nut_clearance",
        "clamp_electronics_cavity_floor_t",
        "clamp_electronics_cavity_top_z",
        "clamp_electronics_assembly_z_shift",
        "clamp_electronics_cavity_y_half",
        "clamp_electronics_board_bottom_z",
        "clamp_electronics_board_width_y",
        "clamp_electronics_main_board_y_shift",
        "clamp_electronics_main_board_wall_clearance_y",
        "clamp_electronics_board_bracket_clearance_xy",
        "clamp_electronics_board_bracket_clearance_z",
        "clamp_electronics_board_bracket_lower_lip_below_z",
        "clamp_electronics_board_bracket_lower_lip_t_z",
        "clamp_electronics_board_bracket_upper_lip_gap_z",
        "clamp_electronics_board_bracket_upper_lip_t_z",
        "clamp_electronics_board_bracket_root_overlap_x",
        "clamp_electronics_board_bracket_wall_overlap_x",
        "clamp_electronics_board_bracket_edge_overlap_x",
        "clamp_electronics_board_bracket_y_overrun",
        "clamp_electronics_board_support_floor_clearance_z",
        "clamp_electronics_emitter_clip_top_clearance_z",
        "clamp_electronics_ui_side_board_plane_y",
        "clamp_electronics_ui_side_board_z_min",
        "clamp_electronics_ui_side_panel_inward_shift_y",
        "clamp_electronics_ui_side_window_border",
        "clamp_electronics_ui_insert_panel_border",
        "clamp_electronics_ui_insert_panel_t",
        "clamp_electronics_ui_panel_outer_local_z",
        "clamp_electronics_ui_panel_inner_local_z",
        "clamp_electronics_ui_panel_mount_outer_border",
        "clamp_electronics_ui_panel_mount_inner_border",
        "clamp_electronics_ui_panel_mount_window_clearance",
        "clamp_electronics_ui_panel_mount_t",
        "clamp_electronics_ui_panel_mount_hole_d",
        "clamp_electronics_ui_panel_mount_min_edge_land",
        "clamp_electronics_ui_wall_pilot_d",
        "clamp_electronics_ui_wall_pilot_floor_t",
        "clamp_electronics_ui_panel_mount_boss_d",
        "clamp_electronics_ui_panel_mount_screw_nominal_d",
        "clamp_electronics_ui_panel_mount_boss_height",
        "clamp_electronics_faceplate_t",
        "clamp_reinforcement_start_x",
        "clamp_reinforcement_end_x",
        "clamp_pad_outer_x",
        "clamp_outer_wall_x",
        "clamp_horizontal_part_outboard_limit",
        "clamp_outboard_extension_actual",
        "clamp_screw_inset",
        "clamp_lower_arm_x",
        "clamp_screw_x",
        "clamp_screw_d",
        "clamp_screw_pitch",
        "clamp_screw_bore_d",
        "clamp_printed_thread_major_d",
        "clamp_printed_thread_core_d",
        "clamp_printed_thread_pitch",
        "clamp_printed_thread_band_tangent_width",
        "clamp_printed_thread_clearance_r",
        "clamp_printed_thread_nut_af",
        "clamp_printed_thread_body_nut_h",
        "clamp_printed_thread_drive_nut_h",
        "clamp_table_thickness_min",
        "clamp_table_thickness_max",
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
        "clamp_screw_to_knob_top_base",
        "clamp_screw_extra_length_z",
        "clamp_screw_to_knob_top",
        "clamp_nut_af",
        "clamp_nut_h",
        "clamp_nut_clearance",
        "clamp_nut_pocket_af",
        "clamp_nut_pocket_depth",
        "clamp_knob_nut_gap",
        "clamp_knob_nut_h",
        "clamp_knob_nut_stack_depth",
        "clamp_knob_nut_pocket_depth",
        "clamp_body_nut_z",
        "clamp_body_nut_top_z",
        "clamp_body_nut_pocket_z",
        "clamp_body_nut_load_from_top",
        "clamp_knob_d",
        "clamp_knob_grip_root_d",
        "clamp_knob_grip_tooth_count",
        "clamp_knob_grip_tooth_d",
        "clamp_knob_grip_tooth_pitch_r",
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
        "clamp_pressure_pad_d",
        "clamp_pressure_pad_width",
        "clamp_pressure_pad_depth",
        "clamp_pressure_pad_t",
        "clamp_pressure_pad_screw_socket_d",
        "clamp_pressure_pad_screw_socket_depth",
        "clamp_pressure_pad_screw_socket_mouth_d",
        "clamp_pressure_pad_screw_socket_chamfer_h",
        "clamp_pressure_pad_ball_clearance_r",
        "clamp_pressure_pad_ball_clearance_z",
        "clamp_pressure_pad_socket_housing_root_d",
        "clamp_pressure_pad_socket_housing_major_d",
        "clamp_pressure_pad_socket_housing_bottom_offset_z",
        "clamp_pressure_pad_socket_housing_h",
        "clamp_pressure_pad_socket_cavity_depth_z",
        "clamp_pressure_pad_socket_thread_pitch",
        "clamp_pressure_pad_socket_thread_clearance_r",
        "clamp_pressure_pad_socket_thread_start_offset_z",
        "clamp_pressure_pad_socket_thread_length_z",
        "clamp_pressure_pad_retainer_outer_d",
        "clamp_pressure_pad_retainer_h",
        "clamp_pressure_pad_retainer_top_clearance_z",
        "clamp_pressure_pad_retainer_thread_start_offset_z",
        "clamp_pressure_pad_retainer_thread_length_z",
        "clamp_pressure_pad_retainer_thread_tangent_width",
        "clamp_pressure_pad_retainer_transition_h",
        "clamp_pressure_pad_retainer_transition_outer_d",
        "clamp_pressure_pad_retainer_thread_root_clear_d",
        "clamp_pressure_pad_retainer_thread_major_clear_d",
        "clamp_pressure_pad_retainer_lip_inner_d",
        "clamp_pressure_pad_retainer_lip_inner_top_d",
        "clamp_pressure_pad_retainer_lip_outer_d",
        "clamp_pressure_pad_retainer_lip_h",
        "clamp_pressure_pad_retainer_top_z",
        "clamp_pressure_pad_retainer_bottom_z",
        "clamp_pressure_pad_retainer_lip_bottom_z",
        "clamp_pressure_pad_retainer_lip_top_z",
        "clamp_pressure_pad_guard_outer_d",
        "clamp_pressure_pad_guard_inner_d",
        "clamp_pressure_pad_guard_t",
        "clamp_pressure_pad_guard_post_d",
        "clamp_pressure_pad_guard_post_h",
        "clamp_pressure_pad_guard_post_radius",
        "clamp_printed_screw_shaft_d",
        "clamp_printed_screw_thread_root_d",
        "clamp_printed_screw_head_d",
        "clamp_printed_screw_head_h",
        "clamp_printed_screw_head_flat_h",
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
        "m6_ballhead_body_depth_y",
        "m6_ballhead_body_corner_radius",
        "m6_ballhead_ball_socket_d",
        "m6_ballhead_side_plate_d",
        "m6_ballhead_side_plate_t_x",
        "m6_ballhead_lock_knob_d",
        "m6_ballhead_lock_knob_t_y",
        "m6_ballhead_lock_knob_ridge_count",
        "m6_ballhead_base_d",
        "m6_ballhead_base_t",
        "m6_ballhead_sensor_stud_d",
        "m6_ballhead_sensor_stud_length",
        "m6_ballhead_sensor_thread_core_d",
        "m6_ballhead_sensor_thread_pitch",
        "m6_ballhead_net_stud_d",
        "m6_ballhead_net_stud_length",
        "m6_ballhead_net_thread_core_d",
        "m6_ballhead_net_thread_pitch",
        "m6_ballhead_top_nut_af",
        "m6_ballhead_top_nut_h",
        "m6_ballhead_bottom_nut_af",
        "m6_ballhead_bottom_nut_h",
        "m6_ballhead_nut_clearance",
        "m6_ballhead_top_nut_pocket_af",
        "m6_ballhead_top_nut_pocket_depth",
        "m6_ballhead_bottom_nut_pocket_af",
        "m6_ballhead_bottom_nut_pocket_depth",
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
        "m6_detector_shell_split_clearance_x",
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
        "m6_detector_shell_support_gusset_x_overlap",
        "m6_detector_shell_support_gusset_root_width_y",
        "m6_detector_shell_support_gusset_wall_width_y",
        "m6_detector_shell_support_gusset_height_z",
        "m6_detector_shell_support_hole_d",
        "m6_detector_shell_support_hole_depth_x",
        "m6_detector_shell_support_stud_engagement_x",
        "m6_detector_shell_support_nut_pocket_center_x",
        "m6_detector_detector_ballhead_gap_x",
        "m6_detector_sensor_head_y_offset",
        "m6_detector_net_connector_arm_width_y",
        "m6_detector_net_connector_arm_t_z",
        "m6_detector_net_connector_leg_width_y",
        "m6_detector_net_connector_leg_t_x",
        "m6_detector_net_connector_post_overlap_x",
        "m6_detector_net_connector_socket_outer_d",
        "m6_detector_net_connector_socket_clearance_d",
        "m6_detector_net_connector_socket_overlap_z",
        "m6_detector_net_connector_post_bolt_d",
        "m6_detector_net_connector_post_bolt_y",
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
        "m6_detector_shell_support_gusset_min_x",
        "m6_detector_shell_support_gusset_max_x",
        "m6_detector_shell_support_gusset_root_y_start_positive",
        "m6_detector_shell_support_gusset_wall_y_start_positive",
        "m6_detector_shell_support_gusset_bottom_z",
        "m6_detector_shell_support_gusset_top_z",
        "m6_detector_shell_support_hole_entry_x",
        "m6_detector_shell_support_hole_center_x",
        "m6_detector_ballhead_center_x",
        "m6_detector_mount_x_offset",
        "m6_detector_mount_raise_z",
        "m6_detector_assembly_ballhead_center_x",
        "m6_detector_assembly_optical_axis_x",
        "m6_detector_ballhead_center_y",
        "m6_detector_ballhead_center_z",
        "m6_detector_ballhead_base_center_z",
        "m6_detector_ballhead_net_stud_center_z",
        "m6_detector_ballhead_sensor_stud_center_x",
        "m6_detector_ballhead_net_interface_bottom_z",
        "m6_detector_assembly_ballhead_center_z",
        "m6_detector_assembly_ballhead_base_center_z",
        "m6_detector_assembly_ballhead_net_stud_center_z",
        "m6_detector_assembly_ballhead_net_interface_bottom_z",
        "m6_detector_net_connector_interface_height_z",
        "m6_detector_net_connector_socket_bottom_z",
        "m6_detector_net_connector_socket_top_z",
        "m6_detector_net_connector_socket_height_z",
        "m6_detector_net_connector_socket_center_z",
        "m6_detector_net_connector_arm_min_x",
        "m6_detector_net_connector_post_inner_face_x",
        "m6_detector_net_connector_arm_max_x",
        "m6_detector_net_connector_arm_bottom_z",
        "m6_detector_net_connector_arm_top_z",
        "m6_detector_net_connector_leg_min_x",
        "m6_detector_net_connector_leg_max_x",
        "m6_detector_net_connector_leg_bottom_z",
        "m6_detector_net_connector_leg_top_z",
        "m6_detector_net_connector_leg_height_z",
        "m6_detector_net_connector_mount_height_z",
        "m6_detector_direct_mount_socket_bottom_z",
        "m6_detector_direct_mount_socket_top_z",
        "m6_detector_direct_mount_socket_height_z",
        "m6_detector_direct_mount_socket_center_z",
        "m6_detector_direct_mount_socket_clearance_d",
        "m6_detector_direct_mount_socket_tap_d",
        "m6_detector_direct_mount_enabled",
        "m6_detector_direct_mount_socket_base_overlap_z",
        "m6_detector_direct_mount_socket_bottom_clearance_z",
        "m6_detector_direct_mount_socket_top_clearance_z",
        "m6_detector_direct_mount_thread_tap_d",
        "m6_detector_direct_mount_thread_depth_z",
        "m6_detector_direct_mount_thread_bottom_z",
        "m6_detector_direct_mount_thread_top_z",
        "m6_detector_direct_mount_thread_depth_extra_z",
        "m6_detector_direct_mount_socket_center_x",
        "m6_detector_direct_mount_nut_loading_clearance_z",
        "m6_detector_direct_mount_nut_pocket_center_z",
        "m6_detector_direct_mount_nut_pocket_bottom_z",
        "m6_detector_direct_mount_nut_loading_depth_z",
        "m6_detector_direct_mount_arm_min_x",
        "m6_detector_direct_mount_arm_max_x",
        "m6_detector_direct_mount_arm_width_y",
        "m6_detector_direct_mount_arm_t_z",
        "m6_detector_direct_mount_post_inner_face_x",
        "m6_detector_direct_mount_arm_bottom_z",
        "m6_detector_direct_mount_arm_top_z",
        "m6_detector_direct_mount_lower_post_top_z",
        "m6_detector_direct_mount_web_width_y",
        "m6_detector_direct_mount_web_t_x",
        "net_fixture_bottom_z",
        "net_panel_bottom_z",
        "net_clamp_rod_d",
        "net_clamp_rod_clearance",
        "net_clamp_rod_bore_d",
        "net_clamp_rod_length",
        "net_clamp_rod_axis_x",
        "net_clamp_rod_axis_y",
        "net_clamp_rod_reference_d",
        "net_clamp_channel_depth_x",
        "net_clamp_channel_back_wall_t_x",
        "net_clamp_channel_side_clearance",
        "net_clamp_channel_back_clearance",
        "net_clamp_channel_width_y",
        "net_clamp_channel_bottom_z",
        "net_clamp_channel_top_z",
        "net_clamp_channel_void_min_x",
        "net_clamp_channel_void_max_x",
        "net_clamp_rod_bore_bottom_z",
        "net_clamp_rod_bore_top_z",
        "net_clamp_rod_sleeve_outer_d",
        "net_clamp_rod_sleeve_clearance",
        "net_clamp_rod_sleeve_passage_clearance_y",
        "net_clamp_rod_print_fn",
        "post_split_from_top_z",
        "post_split_z",
        "post_lower_segment_height",
        "post_upper_segment_height",
        "post_split_key_height_z",
        "post_split_key_x_base_width",
        "post_split_key_x_neck_width",
        "post_split_key_y_depth",
        "post_split_key_clearance",
        "post_split_screw_clearance_d",
        "post_split_pilot_d",
        "post_split_pilot_depth_z",
        "post_split_screw_length",
        "net_sheet_t",
        "net_passage_width_y",
        "net_passage_side_clearance_y",
        "net_passage_body_extension_x",
        "net_passage_min_x",
        "net_passage_max_x",
        "net_passage_bottom_z",
        "net_passage_top_z",
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
        "clamp_pad_t",
        "clamp_outboard_extension_min",
        "clamp_reinforcement_inboard_offset_x",
        "clamp_reinforcement_near_table_thickness_z",
        "clamp_reinforcement_depth_y",
        "clamp_solid_bridge_clearance_x",
        "clamp_solid_bridge_start_x",
        "clamp_solid_bridge_top_z",
        "clamp_reinforcement_start_x",
        "clamp_reinforcement_end_x",
        "clamp_reinforcement_top_z",
        "clamp_reinforcement_near_table_bottom_z",
        "clamp_reinforcement_outer_thickness_z",
        "clamp_reinforcement_outer_bottom_z",
        "clamp_lower_arm_t",
        "post_joint_rail_height_z",
        "post_joint_rail_z0",
        "post_joint_rail_root_overlap_z",
        "post_joint_rail_x_base_width",
        "post_joint_rail_x_neck_width",
        "post_joint_rail_y_depth",
        "post_joint_rail_clearance",
        "post_joint_lock_z",
        "clamp_slide_split_x",
        "clamp_slide_shoe_deepening_x",
        "clamp_slide_length_x",
        "clamp_slide_tongue_attach_x",
        "clamp_slide_tongue_min_x",
        "clamp_slide_receiver_length_x",
        "clamp_slide_rail_y_outer",
        "clamp_slide_rail_y_depth",
        "clamp_slide_rail_head_width_y",
        "clamp_slide_rail_neck_width_y",
        "clamp_slide_rail_head_height_z",
        "clamp_slide_rail_neck_height_z",
        "clamp_slide_shoe_drop_z",
        "clamp_slide_rail_floor_z",
        "clamp_slide_rail_base_width_z",
        "clamp_slide_rail_neck_width_z",
        "clamp_slide_rail_height_z",
        "clamp_slide_rail_center_z",
        "clamp_slide_clearance",
        "clamp_slide_receiver_floor_z",
        "clamp_slide_receiver_top_z",
        "clamp_slide_receiver_neck_height_z",
        "clamp_slide_seat_z",
        "clamp_slide_post_seat_clearance_x",
        "clamp_slide_post_seat_end_x",
        "clamp_fixed_body_max_x",
        "clamp_slide_entry_open_x",
        "clamp_slide_post_foot_root_width_y",
        "clamp_slide_post_foot_ankle_inboard_extension_x",
        "clamp_slide_post_foot_root_min_x",
        "clamp_slide_post_foot_root_max_x",
        "clamp_slide_post_foot_bridge_min_x",
        "clamp_slide_post_foot_bridge_max_x",
        "clamp_slide_post_foot_cross_tie_length_x",
        "clamp_slide_post_foot_cross_tie_top_z",
        "clamp_slide_post_foot_cross_tie_height_z",
        "clamp_slide_post_foot_cross_tie_bottom_z",
        "clamp_slide_post_foot_cross_tie_bottom_half_y",
        "clamp_slide_post_foot_cross_tie_top_half_y",
        "clamp_slide_post_foot_cross_tie_bridge_half_y",
        "clamp_slide_post_foot_bottom_z",
        "clamp_slide_post_foot_top_z",
        "clamp_slide_post_foot_transition_section_count",
        "clamp_slide_post_foot_transition_slice_z",
        "clamp_slide_post_foot_transition_start_z",
        "clamp_slide_post_foot_transition_side_start_z",
        "clamp_slide_post_foot_transition_end_z",
        "clamp_slide_post_foot_post_fusion_inset",
        "clamp_slide_post_foot_side_top_inner_y",
        "clamp_slide_post_foot_side_top_outer_y",
        "clamp_slide_post_foot_side_outer_y",
        "clamp_slide_post_foot_ankle_height_z",
        "clamp_slide_post_foot_slope_top_min_x",
        "clamp_slide_post_foot_slope_top_max_x",
        "clamp_slide_post_foot_shoe_buried_overlap_z",
        "clamp_slide_post_foot_shoe_overlap_z",
        "clamp_slide_post_foot_root_overlap_z",
        "clamp_slide_lock_x",
        "clamp_slide_lock_bore_d",
        "clamp_slide_lock_bolt_d",
        "clamp_slide_lock_bolt_length",
        "clamp_slide_lock_nut_af",
        "clamp_slide_lock_nut_h",
        "clamp_slide_detent_x",
        "clamp_slide_detent_y_count",
        "clamp_slide_detent_y_center",
        "clamp_slide_detent_ball_d",
        "clamp_slide_detent_ball_offset_z",
        "clamp_slide_detent_ball_center_z",
        "clamp_slide_detent_bore_d",
        "clamp_slide_detent_bore_top_z",
        "clamp_slide_detent_dimple_d",
        "clamp_slide_detent_dimple_depth_z",
        "clamp_slide_detent_female_roof_z",
        "clamp_slide_detent_spring_d",
        "clamp_slide_detent_spring_h",
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
        and parameters["post_joint_gap"] == 0
        and math.isclose(
            parameters["post_bottom"],
            parameters["clamp_slide_seat_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["net_post_top_z"],
            parameters["post_top"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["post_segment_length"],
            parameters["post_split_from_top_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["net_post_top_z"] > parameters["net_panel_top_z"]
        and 0 < parameters["preview_fit_display_gap"] <= 0.2
        and math.isclose(
            parameters["active_post_top_z"],
            parameters["net_post_top_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["active_post_total_height"],
            parameters["net_post_top_z"] - parameters["post_bottom"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["active_post_segment_length"],
            parameters["post_lower_segment_height"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["post_lower_segment_z"],
            parameters["post_bottom"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["post_lower_segment_height"],
            parameters["post_split_z"] - parameters["post_bottom"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["post_upper_segment_height"],
            parameters["post_split_from_top_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["post_split_z"],
            parameters["active_post_top_z"] - parameters["post_split_from_top_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["post_upper_segment_z"], parameters["post_split_z"],
            rel_tol=0, abs_tol=1e-4,
        )
        and math.isclose(
            parameters["active_post_joint_z"], parameters["post_split_z"],
            rel_tol=0, abs_tol=1e-4,
        )
        and math.isclose(parameters["post_split_screw_clearance_d"], 3.4, abs_tol=1e-4)
        and math.isclose(parameters["post_split_pilot_d"], 2.4, abs_tol=1e-4)
        and math.isclose(parameters["post_split_pilot_depth_z"], 10, abs_tol=1e-4)
        and math.isclose(parameters["post_split_screw_length"], 40, abs_tol=1e-4)
    ):
        raise RuntimeError(f"unexpected split printable post parameters: {parameters}")
    if parameters["clamp_slide_interface_enabled"] and not (
        parameters["clamp_slide_shoe_deepening_x"] >= 8
        and parameters["clamp_slide_shoe_drop_z"] >= 9
        and parameters["clamp_slide_receiver_length_x"]
        == 73 + parameters["clamp_slide_shoe_deepening_x"]
        and parameters["clamp_slide_length_x"]
        == 71 + parameters["clamp_slide_shoe_deepening_x"]
        and parameters["clamp_slide_tongue_min_x"]
        + parameters["clamp_slide_receiver_length_x"]
        == parameters["clamp_fixed_body_max_x"]
        and parameters["clamp_slide_tongue_min_x"]
        + parameters["clamp_slide_length_x"]
        <= parameters["clamp_slide_post_foot_root_max_x"]
        and parameters["clamp_slide_post_foot_root_max_x"]
        - (
            parameters["clamp_slide_tongue_min_x"]
            + parameters["clamp_slide_length_x"]
        )
        <= 0.75
        and parameters["clamp_slide_receiver_length_x"] >= 60
        and parameters["clamp_slide_tongue_attach_x"] >= 35.5
        and math.isclose(
            parameters["clamp_slide_tongue_attach_x"],
            parameters["clamp_slide_post_foot_root_max_x"]
            - parameters["clamp_slide_split_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_tongue_min_x"] < parameters["clamp_slide_split_x"]
        and parameters["clamp_slide_split_x"]
        < parameters["clamp_slide_tongue_min_x"]
        + parameters["clamp_slide_length_x"]
        and parameters["clamp_slide_rail_y_outer"] > 0
        and parameters["clamp_slide_rail_y_depth"] >= 16
        and parameters["clamp_slide_rail_head_width_y"]
        > parameters["clamp_slide_rail_neck_width_y"]
        > 0
        and parameters["clamp_slide_rail_head_width_y"] >= 16
        and parameters["clamp_slide_rail_neck_width_y"] >= 10
        and parameters["clamp_slide_rail_head_height_z"] >= 6.5
        and parameters["clamp_slide_rail_neck_height_z"] >= 5.5
        and math.isclose(
            parameters["clamp_slide_rail_height_z"],
            parameters["clamp_slide_rail_head_height_z"]
            + parameters["clamp_slide_rail_neck_height_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["clamp_slide_rail_floor_z"],
            parameters["clamp_slide_rail_center_z"]
            - parameters["clamp_slide_rail_height_z"] / 2,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_rail_base_width_z"]
        > parameters["clamp_slide_rail_neck_width_z"]
        > 0
        and parameters["clamp_slide_rail_height_z"] >= 12
        and parameters["clamp_slide_clearance"] > 0
        and parameters["clamp_slide_receiver_floor_z"]
        < parameters["clamp_slide_rail_floor_z"]
        and parameters["clamp_slide_receiver_top_z"]
        > parameters["clamp_slide_rail_floor_z"]
        + parameters["clamp_slide_rail_height_z"]
        and parameters["clamp_slide_receiver_neck_height_z"] > 0
        and math.isclose(
            parameters["clamp_slide_receiver_top_z"],
            parameters["clamp_slide_receiver_floor_z"]
            + parameters["clamp_slide_rail_head_height_z"]
            + parameters["clamp_slide_clearance"]
            + parameters["clamp_slide_receiver_neck_height_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_rail_y_outer"]
        + parameters["clamp_slide_rail_head_width_y"] / 2
        + parameters["clamp_slide_clearance"]
        < parameters["clamp_pad_depth"] / 2
        and parameters["clamp_slide_rail_y_outer"]
        - parameters["clamp_slide_post_foot_root_width_y"] / 2
        - parameters["clamp_slide_clearance"]
        > parameters["net_passage_width_y"] / 2
        and parameters["clamp_slide_rail_y_outer"]
        + parameters["clamp_slide_post_foot_root_width_y"] / 2
        + parameters["clamp_slide_clearance"]
        < parameters["clamp_pad_depth"] / 2
        and math.isclose(
            parameters["clamp_slide_post_foot_side_top_inner_y"],
            parameters["net_passage_width_y"] / 2
            - parameters["clamp_slide_post_foot_post_fusion_inset"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["clamp_slide_post_foot_side_top_outer_y"],
            parameters["post_body_depth"] / 2
            - parameters["clamp_slide_post_foot_post_fusion_inset"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_side_top_inner_y"]
        < parameters["clamp_slide_post_foot_side_top_outer_y"]
        and parameters["clamp_slide_post_foot_side_top_outer_y"]
        < parameters["clamp_slide_rail_y_outer"]
        + parameters["clamp_slide_post_foot_root_width_y"] / 2
        and parameters["clamp_slide_post_foot_transition_section_count"] >= 6
        and parameters["clamp_slide_post_foot_transition_slice_z"] > 0
        and math.isclose(
            parameters["clamp_slide_post_foot_transition_start_z"],
            parameters["clamp_slide_post_foot_bottom_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_transition_start_z"]
        < parameters["clamp_slide_post_foot_top_z"]
        and math.isclose(
            parameters["clamp_slide_post_foot_transition_side_start_z"],
            parameters["clamp_slide_rail_floor_z"]
            + parameters["clamp_slide_rail_height_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_transition_side_start_z"]
        < parameters["clamp_slide_post_foot_transition_end_z"]
        and math.isclose(
            parameters["clamp_slide_post_foot_transition_end_z"],
            parameters["post_bottom"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_root_max_x"]
        - parameters["clamp_slide_post_foot_root_min_x"]
        >= parameters["post_body_width"] / 2
        and parameters["clamp_slide_post_foot_root_min_x"]
        >= parameters["clamp_slide_tongue_min_x"]
        and parameters["clamp_slide_post_foot_ankle_inboard_extension_x"]
        >= 8
        and math.isclose(
            parameters["clamp_slide_split_x"]
            - parameters["clamp_slide_post_foot_root_min_x"],
            parameters["clamp_slide_post_foot_ankle_inboard_extension_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_bridge_min_x"]
        >= parameters["clamp_slide_post_foot_root_min_x"]
        and parameters["clamp_slide_post_foot_bridge_max_x"]
        <= parameters["clamp_slide_post_foot_root_max_x"]
        and parameters["clamp_slide_post_foot_root_max_x"]
        - parameters["clamp_slide_post_foot_bridge_max_x"]
        >= parameters["clamp_slide_clearance"]
        and parameters["clamp_slide_post_foot_bridge_max_x"]
        > parameters["clamp_slide_post_foot_bridge_min_x"]
        and parameters["clamp_slide_post_foot_cross_tie_length_x"] >= 10
        and parameters["clamp_slide_post_foot_cross_tie_height_z"]
        > 3
        and math.isclose(
            parameters["clamp_slide_post_foot_cross_tie_top_z"],
            parameters["net_passage_bottom_z"]
            - parameters["clamp_slide_clearance"]
            - 0.1,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_cross_tie_top_z"]
        < parameters["net_passage_bottom_z"]
        and parameters["clamp_slide_post_foot_cross_tie_bottom_z"]
        < parameters["clamp_slide_post_foot_cross_tie_top_z"]
        and parameters["clamp_slide_post_foot_cross_tie_bottom_half_y"]
        > parameters["clamp_slide_post_foot_cross_tie_top_half_y"]
        > 0
        and parameters["clamp_slide_post_foot_cross_tie_bottom_half_y"]
        < parameters["clamp_slide_rail_y_outer"]
        - parameters["clamp_slide_rail_head_width_y"] / 2
        and parameters["clamp_slide_post_foot_cross_tie_bridge_half_y"]
        > parameters["clamp_slide_post_foot_cross_tie_bottom_half_y"]
        and parameters["clamp_slide_post_foot_cross_tie_bridge_half_y"]
        < parameters["clamp_slide_rail_y_outer"]
        - parameters["clamp_slide_rail_head_width_y"] / 2
        + parameters["clamp_slide_post_foot_root_width_y"]
        / 2
        and parameters["clamp_slide_post_foot_shoe_buried_overlap_z"] > 0
        and math.isclose(
            parameters["clamp_slide_rail_floor_z"]
            + parameters["clamp_slide_rail_height_z"]
            - parameters["clamp_slide_post_foot_bottom_z"],
            parameters["clamp_slide_rail_height_z"]
            + parameters["clamp_slide_post_foot_shoe_buried_overlap_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["clamp_slide_post_foot_bridge_max_x"]
            - parameters["clamp_slide_post_foot_bridge_min_x"],
            parameters["clamp_slide_post_foot_cross_tie_length_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_top_z"]
        > parameters["clamp_slide_rail_floor_z"]
        + parameters["clamp_slide_rail_height_z"]
        and parameters["clamp_slide_post_foot_root_max_x"]
        < parameters["clamp_fixed_body_max_x"]
        and parameters["clamp_fixed_body_max_x"]
        - parameters["clamp_slide_post_foot_root_max_x"]
        >= 1.2
        and math.isclose(
            parameters["clamp_slide_seat_z"],
            parameters["clamp_solid_bridge_top_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_seat_clearance_x"] > 0
        and parameters["clamp_slide_post_seat_end_x"]
        >= post_outer_face
        and parameters["clamp_slide_post_seat_end_x"]
        == parameters["clamp_fixed_body_max_x"]
        and math.isclose(
            parameters["post_bottom"],
            parameters["clamp_slide_seat_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_seat_z"]
        > parameters["clamp_slide_rail_floor_z"]
        + parameters["clamp_slide_rail_height_z"]
        and parameters["clamp_slide_post_foot_ankle_height_z"] >= 20
        and math.isclose(
            parameters["clamp_slide_post_foot_ankle_height_z"],
            parameters["post_bottom"]
            - parameters["clamp_slide_post_foot_bottom_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_root_overlap_z"] >= 0.2
        and math.isclose(
            parameters["clamp_slide_post_foot_top_z"]
            - parameters["post_bottom"],
            parameters["clamp_slide_post_foot_root_overlap_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_top_z"]
        > parameters["post_bottom"]
        and parameters["clamp_slide_post_foot_bottom_z"]
        < parameters["clamp_slide_rail_floor_z"]
        + parameters["clamp_slide_rail_height_z"]
        and parameters["clamp_slide_post_foot_shoe_overlap_z"] >= 10
        and math.isclose(
            parameters["clamp_slide_rail_floor_z"]
            + parameters["clamp_slide_rail_height_z"]
            - parameters["clamp_slide_post_foot_bottom_z"],
            parameters["clamp_slide_post_foot_shoe_overlap_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_lock_x"] > parameters["clamp_slide_tongue_min_x"]
        and parameters["clamp_slide_lock_x"] < parameters["clamp_slide_split_x"]
        and parameters["clamp_slide_lock_bore_d"]
        > parameters["clamp_slide_lock_bolt_d"]
        and parameters["clamp_slide_lock_bolt_length"] >= 20
        and parameters["clamp_slide_lock_nut_af"]
        > parameters["clamp_slide_lock_bolt_d"]
        and parameters["clamp_slide_lock_nut_h"] > 0
        and parameters["clamp_slide_detent_y_count"] == 1
        and parameters["clamp_slide_detent_y_center"] == 0
        and parameters["clamp_slide_detent_x"]
        > parameters["clamp_slide_lock_x"]
        and parameters["clamp_slide_detent_x"]
        >= parameters["clamp_slide_post_foot_bridge_min_x"]
        and parameters["clamp_slide_detent_x"]
        <= parameters["clamp_slide_post_foot_bridge_max_x"]
        and parameters["clamp_slide_detent_x"]
        - parameters["clamp_slide_post_foot_bridge_min_x"]
        >= parameters["clamp_slide_detent_dimple_d"] / 2
        and parameters["clamp_slide_post_foot_bridge_max_x"]
        - parameters["clamp_slide_detent_x"]
        >= parameters["clamp_slide_detent_dimple_d"] / 2
        and parameters["clamp_slide_detent_x"]
        > parameters["post_interface_transition_outer_max_x"]
        and parameters["clamp_slide_detent_x"]
        < parameters["clamp_fixed_body_max_x"]
        and parameters["clamp_slide_detent_x"]
        >= parameters["clamp_slide_post_foot_bridge_min_x"]
        + parameters["clamp_slide_detent_bore_d"] / 2
        and parameters["clamp_slide_detent_x"]
        <= parameters["clamp_slide_post_foot_bridge_max_x"]
        - parameters["clamp_slide_detent_bore_d"] / 2
        and parameters["clamp_slide_post_foot_bridge_max_x"]
        - parameters["clamp_slide_post_foot_bridge_min_x"]
        >= parameters["clamp_slide_detent_bore_d"]
        and parameters["clamp_slide_detent_bore_d"]
        > parameters["clamp_slide_detent_ball_d"]
        and parameters["clamp_slide_detent_dimple_d"]
        >= parameters["clamp_slide_detent_ball_d"]
        and parameters["clamp_slide_detent_dimple_depth_z"] > 0
        and parameters["clamp_slide_detent_spring_d"]
        < parameters["clamp_slide_detent_ball_d"]
        and parameters["clamp_slide_detent_spring_h"] > 0
        and parameters["clamp_slide_detent_female_roof_z"]
        > parameters["clamp_slide_rail_center_z"]
        and parameters["clamp_slide_detent_bore_top_z"]
        > parameters["clamp_slide_seat_z"]
        and math.isclose(
            parameters["clamp_slide_detent_ball_center_z"]
            - parameters["clamp_slide_post_foot_cross_tie_bottom_z"],
            parameters["clamp_slide_detent_ball_offset_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_cross_tie_bottom_z"]
        >= parameters["clamp_slide_rail_floor_z"]
        and parameters["clamp_slide_post_foot_cross_tie_bottom_z"]
        - parameters["clamp_slide_rail_floor_z"]
        >= 0.2
        and parameters["clamp_slide_post_foot_cross_tie_bottom_z"]
        + parameters["clamp_slide_detent_dimple_depth_z"]
        >= parameters["clamp_slide_detent_ball_center_z"]
        + parameters["clamp_slide_detent_ball_d"] / 2
        and parameters["clamp_slide_detent_bore_top_z"]
        - parameters["clamp_slide_detent_ball_center_z"]
        >= parameters["clamp_slide_detent_ball_d"] / 2
        and math.isclose(
            parameters["post_interface_transition_height_z"],
            0,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["post_interface_transition_outer_max_x"],
            parameters["post_center_x"] + parameters["post_body_width"] / 2,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["net_clamp_rod_axis_x"]
        - parameters["net_clamp_rod_bore_d"] / 2
        > post_inner_face
        and parameters["net_clamp_rod_axis_x"]
        + parameters["net_clamp_rod_bore_d"] / 2
        < post_outer_face
    ):
        raise RuntimeError(
            f"clamp body broad interlocking slideway and anti-slide dimensions are inconsistent: {parameters}"
        )
    if not (
        math.isclose(
            parameters["clamp_slide_post_foot_slope_top_min_x"],
            post_inner_face
            + parameters["clamp_slide_post_foot_post_fusion_inset"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["clamp_slide_post_foot_slope_top_max_x"],
            post_outer_face
            - parameters["clamp_slide_post_foot_post_fusion_inset"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["clamp_slide_post_foot_slope_top_min_x"]
        < parameters["clamp_slide_post_foot_slope_top_max_x"]
        and parameters["clamp_slide_entry_open_x"]
        >= parameters["clamp_fixed_body_max_x"]
        + parameters["clamp_slide_clearance"]
    ):
        raise RuntimeError(
            "sloped post-foot transition or open x+ entry datum is inconsistent: "
            f"{parameters}"
        )
    if not (
        parameters["clamp_tongue_extra_length_x"] > 0
        and parameters["clamp_tongue_reach_inboard"]
        == parameters["clamp_reach_inboard"]
        + parameters["clamp_tongue_extra_length_x"]
        and parameters["clamp_tongue_reach_inboard"]
        > parameters["clamp_reach_inboard"]
        and parameters["clamp_lower_arm_x"] == parameters["clamp_pad_x"]
        and abs(
            parameters["clamp_screw_x"]
            - (parameters["clamp_pad_x"] + table_edge) / 2
        )
        < 0.01
        and abs(
            parameters["clamp_screw_inset"]
            - parameters["clamp_tongue_reach_inboard"] / 2
        )
        < 0.01
        and parameters["clamp_pad_x"] < table_edge < parameters["clamp_pad_outer_x"]
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
        and math.isclose(
            parameters["post_interface_transition_outer_max_x"],
            parameters["clamp_fixed_body_max_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
    ):
        raise RuntimeError(
            "clamp does not bridge edge with an under-table screw or the gray body "
            "does not align to the seated post's outboard face: "
            f"{parameters}"
        )
    if not (
        parameters["clamp_reinforcement_inboard_offset_x"] > 0
        and parameters["clamp_reinforcement_near_table_thickness_z"] == 40
        and parameters["clamp_reinforcement_depth_y"] == parameters["clamp_pad_depth"]
        and parameters["clamp_solid_bridge_clearance_x"] > 0
        and parameters["clamp_solid_bridge_start_x"]
        == table_edge + parameters["clamp_solid_bridge_clearance_x"]
        and parameters["clamp_solid_bridge_start_x"] > table_edge
        and parameters["clamp_solid_bridge_start_x"]
        < parameters["clamp_reinforcement_end_x"]
        and parameters["clamp_solid_bridge_top_z"]
        == parameters["clamp_top_pad_t"] + parameters["clamp_pad_t"]
        and parameters["clamp_solid_bridge_top_z"]
        > parameters["clamp_reinforcement_top_z"]
        and parameters["clamp_reinforcement_start_x"] < table_edge
        and parameters["clamp_reinforcement_start_x"]
        > parameters["clamp_pressure_pad_x"]
        + parameters["clamp_pressure_pad_width"]
        / 2
        and parameters["clamp_reinforcement_end_x"]
        > parameters["clamp_reinforcement_start_x"]
        and parameters["clamp_reinforcement_end_x"]
        > parameters["clamp_outer_wall_x"]
        and parameters["clamp_reinforcement_top_z"]
        == parameters["clamp_lower_arm_top_z"]
        and parameters["clamp_reinforcement_near_table_bottom_z"]
        == parameters["clamp_reinforcement_top_z"]
        - parameters["clamp_reinforcement_near_table_thickness_z"]
        and parameters["clamp_reinforcement_outer_thickness_z"]
        == parameters["clamp_lower_arm_t"]
        and parameters["clamp_reinforcement_outer_bottom_z"]
        == parameters["clamp_reinforcement_top_z"]
        - parameters["clamp_reinforcement_outer_thickness_z"]
        and parameters["clamp_reinforcement_near_table_bottom_z"]
        < parameters["clamp_reinforcement_outer_bottom_z"]
        < parameters["clamp_reinforcement_top_z"]
    ):
        raise RuntimeError(
            f"solid tapered under-clamp reinforcement geometry is inconsistent: {parameters}"
        )
    if not (
        parameters["clamp_screw_to_knob_top_base"] == 32
        and parameters["clamp_screw_extra_length_z"] == 12
        and parameters["clamp_tongue_extra_length_x"] == 20
        and parameters["clamp_tongue_reach_inboard"] == 82
        and parameters["clamp_screw_inset"] == 41
        and parameters["clamp_lower_arm_x"] == parameters["clamp_pad_x"]
        and abs(
            parameters["clamp_screw_x"]
            - (parameters["clamp_pad_x"] + parameters["table_width"] / 2) / 2
        ) < 0.01
        and parameters["clamp_screw_to_knob_top"]
        == parameters["clamp_screw_to_knob_top_base"]
        + parameters["clamp_screw_extra_length_z"]
        and
        parameters["clamp_screw_d"] == 8
        and parameters["clamp_screw_pitch"] == 1.25
        and parameters["clamp_screw_bore_d"]
        > parameters["clamp_printed_thread_major_d"]
        and parameters["clamp_printed_thread_major_d"]
        > parameters["clamp_printed_thread_core_d"] > 0
        and parameters["clamp_printed_thread_pitch"] >= 3.5
        and 0 < parameters["clamp_printed_thread_clearance_r"] <= 0.4
        and parameters["clamp_printed_thread_major_d"]
        == parameters["clamp_printed_screw_shaft_d"]
        and parameters["clamp_printed_thread_core_d"]
        == parameters["clamp_printed_screw_thread_root_d"]
        and parameters["clamp_printed_thread_body_nut_h"]
        > 2 * parameters["clamp_printed_thread_pitch"]
        and parameters["clamp_printed_thread_drive_nut_h"]
        >= parameters["clamp_printed_thread_pitch"]
        and parameters["clamp_table_thickness_min"]
        <= parameters["table_thickness"]
        <= parameters["clamp_table_thickness_max"]
        and parameters["clamp_table_thickness_max"] == 40
        and
        parameters["clamp_screw_top_z"] < -parameters["table_thickness"]
        and parameters["clamp_pressure_pad_top_z"] < -parameters["table_thickness"]
        and parameters["clamp_screw_top_z"] > parameters["clamp_pressure_pad_bottom_z"]
        and parameters["clamp_screw_top_z"]
        <= parameters["clamp_pressure_pad_bottom_z"]
        + parameters["clamp_pressure_pad_screw_socket_depth"] + 0.01
        and parameters["clamp_screw_bottom_z"] < parameters["clamp_knob_top_z"]
        and parameters["clamp_screw_bottom_z"] > parameters["clamp_knob_bottom_z"]
        and parameters["clamp_knob_bottom_z"] < parameters["clamp_knob_top_z"]
        and parameters["clamp_pressure_pad_bottom_z"] <
        parameters["clamp_pressure_pad_top_z"]
        and parameters["clamp_lower_arm_top_z"] <
        parameters["clamp_pressure_pad_bottom_z"]
        and parameters["clamp_pad_t"] == 14
        and parameters["clamp_lower_arm_t"] == parameters["clamp_pad_t"]
        and abs(
            parameters["clamp_screw_top_z"]
            - (
                parameters["clamp_pressure_pad_bottom_z"]
                + parameters["clamp_pressure_pad_screw_socket_depth"]
                - parameters["clamp_pressure_pad_ball_clearance_z"]
            )
        ) < 0.01
        and parameters["clamp_pressure_pad_d"]
        == parameters["clamp_pressure_pad_width"]
        and parameters["clamp_pressure_pad_d"]
        == parameters["clamp_pressure_pad_depth"]
        and parameters["clamp_pressure_pad_d"] == 50
        and parameters["clamp_pressure_pad_t"]
        > parameters["clamp_pressure_pad_screw_socket_depth"]
        and parameters["clamp_pressure_pad_screw_socket_d"]
        >= parameters["clamp_printed_screw_head_d"] - 0.01
        and parameters["clamp_pressure_pad_screw_socket_d"]
        < parameters["clamp_pressure_pad_d"]
        and parameters["clamp_pressure_pad_screw_socket_mouth_d"]
        > parameters["clamp_screw_d"]
        and parameters["clamp_pressure_pad_screw_socket_mouth_d"]
        > parameters["clamp_printed_thread_core_d"]
        and parameters["clamp_pressure_pad_screw_socket_mouth_d"]
        < parameters["clamp_pressure_pad_screw_socket_d"]
        and 0 < parameters["clamp_pressure_pad_screw_socket_chamfer_h"]
        < parameters["clamp_pressure_pad_screw_socket_depth"]
        and parameters["clamp_pressure_pad_guard_outer_d"]
        > parameters["clamp_pressure_pad_guard_inner_d"]
        and parameters["clamp_pressure_pad_guard_inner_d"]
        > parameters["clamp_printed_screw_shaft_d"]
        and abs(
            parameters["clamp_pressure_pad_screw_socket_d"]
            - (
                parameters["clamp_printed_screw_head_d"]
                + 2 * parameters["clamp_pressure_pad_ball_clearance_r"]
            )
        )
        < 0.01
        and parameters["clamp_pressure_pad_socket_housing_major_d"]
        > parameters["clamp_pressure_pad_socket_housing_root_d"]
        > parameters["clamp_pressure_pad_screw_socket_d"]
        and parameters["clamp_pressure_pad_socket_housing_h"]
        >= parameters["clamp_pressure_pad_socket_cavity_depth_z"]
        and parameters["clamp_pressure_pad_socket_thread_length_z"]
        >= parameters["clamp_pressure_pad_socket_thread_pitch"]
        and parameters["clamp_pressure_pad_retainer_outer_d"]
        > parameters["clamp_pressure_pad_retainer_thread_major_clear_d"] + 5
        and parameters["clamp_pressure_pad_retainer_h"]
            > parameters["clamp_pressure_pad_retainer_lip_h"]
        and parameters["clamp_pressure_pad_retainer_h"]
            > parameters["clamp_pressure_pad_retainer_transition_h"]
        and parameters["clamp_pressure_pad_retainer_thread_start_offset_z"]
            > parameters["clamp_pressure_pad_retainer_transition_h"]
        and parameters["clamp_pressure_pad_retainer_thread_length_z"]
            >= parameters["clamp_pressure_pad_socket_thread_pitch"]
        and parameters["clamp_pressure_pad_retainer_thread_tangent_width"]
            > parameters["clamp_printed_thread_band_tangent_width"]
        and abs(
            parameters["clamp_pressure_pad_retainer_bottom_z"]
            + parameters["clamp_pressure_pad_retainer_thread_start_offset_z"]
            - (
                parameters["clamp_pressure_pad_bottom_z"]
                - parameters["clamp_pressure_pad_socket_housing_bottom_offset_z"]
                + parameters["clamp_pressure_pad_socket_thread_start_offset_z"]
            )
        ) < 0.01
        and parameters["clamp_pressure_pad_retainer_transition_outer_d"]
            > parameters["clamp_pressure_pad_retainer_thread_root_clear_d"]
        and parameters["clamp_pressure_pad_retainer_bottom_z"]
            + parameters["clamp_pressure_pad_retainer_transition_h"]
            < parameters["clamp_pressure_pad_bottom_z"]
            - parameters["clamp_pressure_pad_socket_housing_bottom_offset_z"]
            - 0.1
        and parameters["clamp_pressure_pad_retainer_thread_root_clear_d"]
        > parameters["clamp_pressure_pad_socket_housing_root_d"]
        and parameters["clamp_pressure_pad_retainer_thread_major_clear_d"]
        > parameters["clamp_pressure_pad_socket_housing_major_d"]
        and parameters["clamp_pressure_pad_retainer_lip_inner_d"]
        > parameters["clamp_printed_screw_shaft_d"]
        and parameters["clamp_pressure_pad_retainer_lip_inner_d"]
        < parameters["clamp_printed_screw_head_d"]
        and parameters["clamp_pressure_pad_retainer_lip_inner_top_d"]
        > parameters["clamp_pressure_pad_retainer_lip_inner_d"]
        and parameters["clamp_pressure_pad_retainer_lip_inner_top_d"]
        < parameters["clamp_pressure_pad_retainer_lip_outer_d"]
        and parameters["clamp_pressure_pad_retainer_lip_outer_d"]
        < parameters["clamp_pressure_pad_screw_socket_d"]
        and parameters["clamp_pressure_pad_retainer_bottom_z"]
        < parameters["clamp_pressure_pad_retainer_lip_bottom_z"]
        < parameters["clamp_pressure_pad_retainer_lip_top_z"]
        and parameters["clamp_pressure_pad_retainer_lip_top_z"]
            <= parameters["clamp_screw_top_z"]
            - parameters["clamp_printed_screw_head_h"]
            - 0.19
        < parameters["clamp_pressure_pad_retainer_top_z"]
        < parameters["clamp_pressure_pad_bottom_z"]
    ):
        raise RuntimeError(f"coarse printed clamp pressure path is inconsistent: {parameters}")
    if not (
        parameters["clamp_nut_af"] > parameters["clamp_screw_d"]
        and parameters["clamp_nut_af"]
        == parameters["clamp_printed_thread_nut_af"]
        and parameters["clamp_nut_h"]
        == parameters["clamp_printed_thread_body_nut_h"]
        and parameters["clamp_nut_pocket_af"] > parameters["clamp_nut_af"]
        and parameters["clamp_nut_pocket_af"] / math.cos(math.radians(30)) + 2
        < parameters["clamp_threaded_boss_d"]
        and parameters["clamp_nut_pocket_depth"] >= parameters["clamp_nut_h"]
        and parameters["clamp_nut_pocket_depth"] < parameters["clamp_threaded_boss_h"]
        and parameters["clamp_body_nut_load_from_top"] == 1
        and parameters["clamp_body_nut_pocket_z"]
        >= parameters["clamp_lower_arm_bottom_z"] - 0.01
        and parameters["clamp_body_nut_pocket_z"]
        + parameters["clamp_nut_pocket_depth"]
        <= parameters["clamp_lower_arm_top_z"] + 0.01
        and parameters["clamp_body_nut_top_z"]
        <= parameters["clamp_lower_arm_top_z"] + 0.01
        and parameters["clamp_knob_nut_gap"] >= 0
        and parameters["clamp_knob_nut_stack_depth"]
        == 2 * parameters["clamp_knob_nut_h"] + parameters["clamp_knob_nut_gap"]
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
        raise RuntimeError(f"coarse printed nut capture dimensions are inconsistent: {parameters}")
    if not (
        parameters["clamp_knob_grip_root_d"] > parameters["clamp_screw_d"] + 0.8
        and parameters["clamp_knob_grip_root_d"] < parameters["clamp_knob_d"]
        and parameters["clamp_knob_grip_tooth_count"] >= 12
        and parameters["clamp_knob_grip_tooth_d"] > 0
        and parameters["clamp_knob_grip_tooth_pitch_r"]
        > parameters["clamp_knob_grip_root_d"] / 2
        and parameters["clamp_knob_grip_tooth_pitch_r"]
        - parameters["clamp_knob_grip_tooth_d"] / 2
        < parameters["clamp_knob_grip_root_d"] / 2
        and abs(
            parameters["clamp_knob_grip_tooth_pitch_r"]
            + parameters["clamp_knob_grip_tooth_d"] / 2
            - parameters["clamp_knob_d"] / 2
        )
        < 0.01
    ):
        raise RuntimeError(
            f"rounded anti-slip hand knob geometry is inconsistent: {parameters}"
        )
    if parameters["net_span"] <= parameters["table_width"]:
        raise RuntimeError(f"net span does not bridge the table: {parameters}")
    if not (
        parameters["net_top_rail_required"] == 0
        and math.isclose(
            parameters["net_panel_top_z"],
            parameters["net_fixture_bottom_z"] + parameters["net_height"],
            rel_tol=0,
            abs_tol=1e-4,
        )
    ):
        raise RuntimeError(f"active net still depends on a top rail: {parameters}")
    if not (
        parameters["net_rail_segment_count"] == 3
        and parameters["net_rail_segment_length"] > 500
        and parameters["net_rail_splice_overlap"] == 20
        and parameters["net_rail_splice_plate_length"] == 60
        and parameters["net_rail_splice_hole_d"] > 0
    ):
        raise RuntimeError(f"legacy rail diagnostic parameters are inconsistent: {parameters}")
    if not (
        parameters["net_rail_saddle_width"] > parameters["net_rail_saddle_overlap"] > 0
        and parameters["net_rail_saddle_depth"] > parameters["net_rail_depth"]
        and parameters["net_rail_saddle_height"] > 0
    ):
        raise RuntimeError(f"legacy rail-saddle diagnostic parameters are inconsistent: {parameters}")
    if not (
        parameters["sensor_x"] > parameters["sensor_length"] / 2
        and parameters["sensor_x"] + parameters["sensor_length"] / 2
        < post_inner_face
        and math.isclose(
            post_inner_face
            - (parameters["sensor_x"] + parameters["sensor_length"] / 2),
            parameters["sensor_post_clearance_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["sensor_post_clearance_x"] >= 10
        and parameters["sensor_depth"] > 0
        and parameters["sensor_height"] > 0
        and parameters["sensor_film_y"] < -parameters["net_sheet_t"] / 2
    ):
        raise RuntimeError(f"PVDF sensor mounts are not near the net ends or clear of the posts: {parameters}")
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
        and parameters["m6_ballhead_body_depth_y"] > 0
        and 0 < parameters["m6_ballhead_body_corner_radius"] < min(
            parameters["m6_ballhead_housing_d"],
            parameters["m6_ballhead_body_depth_y"],
        ) / 2
        and parameters["m6_ballhead_ball_socket_d"]
        > parameters["m6_ballhead_ball_d"]
        and parameters["m6_ballhead_side_plate_d"]
        > parameters["m6_ballhead_ball_d"]
        and parameters["m6_ballhead_side_plate_t_x"] > 0
        and parameters["m6_ballhead_lock_knob_d"] > 0
        and parameters["m6_ballhead_lock_knob_t_y"] > 0
        and parameters["m6_ballhead_lock_knob_ridge_count"] >= 12
        and parameters["m6_ballhead_base_d"] > parameters["m6_ballhead_ball_d"]
        and parameters["m6_ballhead_base_t"] > 0
        and parameters["m6_ballhead_sensor_stud_d"]
        > parameters["m6_ballhead_sensor_thread_core_d"] > 0
        and parameters["m6_ballhead_sensor_thread_pitch"] > 0
        and parameters["m6_ballhead_net_stud_d"] > 0
        and parameters["m6_ballhead_net_stud_d"]
        > parameters["m6_ballhead_net_thread_core_d"] > 0
        and parameters["m6_ballhead_net_thread_pitch"] > 0
        and parameters["m6_ballhead_net_stud_length"] > 0
        and parameters["m6_ballhead_top_nut_pocket_af"]
        > parameters["m6_ballhead_top_nut_af"]
        and parameters["m6_ballhead_top_nut_pocket_depth"]
        >= parameters["m6_ballhead_top_nut_h"]
        and parameters["m6_ballhead_top_nut_pocket_af"] / math.cos(math.radians(30))
        < parameters["m6_detector_shell_support_boss_depth_y"]
        and parameters["m6_ballhead_bottom_nut_pocket_af"]
        > parameters["m6_ballhead_bottom_nut_af"]
        and parameters["m6_ballhead_bottom_nut_pocket_depth"]
        >= parameters["m6_ballhead_bottom_nut_h"]
        and parameters["m6_ballhead_bottom_nut_pocket_af"]
        / math.cos(math.radians(30))
        < parameters["m6_detector_direct_mount_socket_outer_d"]
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
        > parameters["post_interface_transition_top_z"]
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
        if start < 0 and "(" in name:
            # Parameterized modules may evolve from a no-argument contract to
            # a configurable preview/material contract.  Locate the module by
            # its stable function name while keeping the body-boundary check.
            marker = f"module {name.split('(', 1)[0]}"
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
    rear_footprint_module = module_text("m6_detector_rear_rounded_footprint_positive()")
    bottom_cover_module = module_text("m6_detector_bottom_cover_positive()")
    wiring_module = module_text("m6_detector_cable_routing_reference_positive()")
    bottom_gasket_module = module_text("m6_detector_bottom_gasket_positive()")
    direct_mount_module = module_text("m6_detector_direct_mount_positive()")
    table_clamp_body_module = module_text("table_clamp_body_positive()")
    cavity_module = module_text("clamp_electronics_cavity_negative()")
    table_clamp_raw_module = module_text("table_clamp_raw_positive()")
    clamp_body_segment_module = module_text("clamp_body_segment_positive()")
    clamp_carrier_module = module_text("table_clamp_carrier_positive()")
    clamp_tongue_module = module_text("clamp_slide_tongues_positive()")
    clamp_tongue_raw_module = module_text("clamp_slide_tongues_raw_positive(tongue_color = \"darkorange\")")
    clamp_foot_module = module_text("clamp_slide_post_foot_positive()")
    knob_module = module_text("clamp_knob_positive()")
    post_module = module_text("post_positive()")
    post_segment_module = module_text("post_segment_positive(index = 0)")
    # The lower half owns the real doorway/keeper cuts; the assembly wrapper
    # only unions lower and upper halves and therefore cannot prove those
    # features by itself.
    post_body_module = module_text("post_body_lower_positive()")
    transition_module = module_text("post_interface_transition_positive()")
    post_carrier_module = module_text("post_clamp_carrier_positive()")
    net_panel_module = module_text("net_panel()")
    mount_module = module_text("m6_detector_mount_positive()")
    assembly_module = module_text("m6_detector_assembly_positive()")
    exploded_module = module_text("m6_detector_exploded_positive()")
    exploded_assembly_module = module_text("m6_detector_exploded_assembly_positive()")
    gimbal_module = module_text("m6_gimbal_positive()")
    stand_module = module_text("stand(side = 1)")
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
        or "polygon(points = concat(" not in rear_footprint_module
        or "rear_min_x = m6_detector_shell_rear_min_x;" not in rear_footprint_module
        or "rear_max_x - radius" not in rear_footprint_module
        or "offset(r = m6_detector_shell_corner_radius)" in rear_footprint_module
        or "m6_detector_shell_support_boss_positive();" not in rear_outer_module
        or "m6_detector_shell_support_hole_positive();" not in rear_shell_module
        or "m6_detector_shell_support_gussets_positive();" not in rear_shell_module
        or "m6_detector_body_tail_clearance_positive" in rear_shell_module
        or "m6_rounded_rect_prism_x(" not in rear_boss_module
        or "m6_cylinder_x(" not in rear_hole_module
        or "m6_hex_prism_x(" not in rear_hole_module
        or "m6_detector_front_optical_holes_positive();" not in front_shell_module
        or "m6_detector_shell_footprint_positive();" not in bottom_cover_module
        or "m6_detector_cable_gland_positive();" not in bottom_cover_module
        or "m6_detector_cable_trunk_positive();" not in wiring_module
        or "m6_detector_cable_branch_positive(index);" not in wiring_module
        or "offset(delta = m6_detector_shell_gasket_clearance" not in bottom_gasket_module
        or "m6_detector_shell_tongue_positive(-1, y_side);" not in front_shell_module
        or "m6_detector_shell_tongue_positive(1, y_side);" not in rear_shell_module
        or not re.search(
            r"m6_countersink_x\(\s*"
            r"m6_detector_shell_min_x,\s*1,",
            front_shell_module,
        )
        or not re.search(
            r"m6_countersink_x\(\s*"
            r"m6_detector_shell_max_x,\s*-1,",
            rear_shell_module,
        )
        or not re.search(
            r"m6_cylinder_z\(\s*m6_detector_cable_exit_d,",
            bottom_cover_module,
        )
        or "Compatibility hook retained" not in direct_mount_module
        or "post_body_positive();" not in post_module
        or "net_passage_negative_positive();" not in post_body_module
        or "net_clamp_rod_recess_negative_positive();" not in post_body_module
        or "post_continuous_envelope_lower_positive();" not in post_body_module
        or "post_clamp_carrier_lower_positive();" not in post_carrier_module
        or "post_clamp_carrier_upper_positive();" not in post_carrier_module
        or "net_panel_top_z" not in net_panel_module
        or "net_rail_saddle_positive();" in stand_module
        or "net_rail();" in source_text[source_text.find('if (PART == "assembly")'):source_text.find('} else if (PART == "left_stand")')]
        or "table_clamp_raw_positive();" not in table_clamp_body_module
        or "clamp_electronics_cavity_negative();" not in table_clamp_body_module
        or "if (clamp_slide_interface_enabled)" not in table_clamp_body_module
        or "net_passage_negative_positive();" in table_clamp_body_module
        or "clamp_electronics_main_board_end_bracket_capture_positive();" not in table_clamp_body_module
        or "clamp_electronics_main_board_pocket_negative();" not in cavity_module
        or "clamp_electronics_emitter_edge_clips_positive();" not in table_clamp_body_module
        or "clamp_electronics_battery_rails_positive();" not in table_clamp_body_module
        or "clamp_solid_tapered_reinforcement_positive();" not in table_clamp_raw_module
        or "clamp_solid_outboard_bridge_positive();" not in table_clamp_raw_module
        or "table_clamp_body_positive();" not in clamp_body_segment_module
        or "post_skp_leg_foot_c_fit_tool_positive();" not in clamp_body_segment_module
        or "post_skp_c_detent_bore_negative_positive();" not in clamp_body_segment_module
        or "post_skp_c_clamp_fastener_holes_negative_positive();" not in clamp_body_segment_module
        or "post_skp_leg_foot_c_fit_tool_positive();" not in clamp_body_segment_module
        or "table_clamp_raw_positive();" in clamp_carrier_module
        or "clamp_slide_tongues_positive" in clamp_carrier_module
        or "net_passage_negative_positive();" in clamp_carrier_module
        or "interlocking_slide_prism_x(" not in clamp_tongue_raw_module
        or "clamp_slide_rail_head_width_y" not in clamp_tongue_raw_module
        or "clamp_slide_rail_neck_width_y" not in clamp_tongue_raw_module
        or "clamp_slide_lock_bores_negative_positive();" not in clamp_tongue_module
        or "clamp_slide_detent_bores_negative_positive();" in clamp_tongue_module
        or "post_interface_transition_positive();" not in clamp_foot_module
        or "post_interface_transition_positive();" in post_body_module
        or "hull()" in transition_module
        or "clamp_knob_grip_positive(" not in knob_module
        or "m6_detector_mount_raise_z" not in assembly_module
        or "m6_detector_mount_raise_z" not in exploded_assembly_module
        or "net_clamp_rod_positive();" not in stand_module
        or "net_clamp_lock_hardware_positive();" in source_text
        or "net_clamp_clip_lock" in source_text
        or "cube([" in direct_mount_module
        or "m6_detector_mount_x_offset" not in assembly_module
        or "m6_detector_mount_x_offset" not in exploded_assembly_module
        or "m6_detector_assembly_positive();" not in gimbal_module
        or "m6_detector_net_connector_positive();" in mount_module
        or "m6_detector_net_connector_positive();" in exploded_module
        or "intersection(" in exploded_module
        or "m6_mount_adapter_positive();" in mount_module
        or "m6_post_mount_hardware_positive();" in mount_module
        or "m6_mount_adapter_positive();" in exploded_module
        or "m6_post_mount_hardware_positive();" in exploded_module
    ):
        raise RuntimeError(
            "active M6/mechanical path diverged: rectangular body, installed sensor "
            "voids, rear-cover boss/hole and split upright/carrier path must be used"
        )

    cover_install_order = [
        mount_module.find("m6_detector_shell_front_positive();"),
        mount_module.find("m6_detector_shell_rear_positive();"),
        mount_module.find("m6_detector_bottom_cover_positive();"),
    ]
    if any(position < 0 for position in cover_install_order) or cover_install_order != sorted(cover_install_order):
        raise RuntimeError(
            "front/rear/bottom cover assembly order must be front from z+, rear from z+, bottom from z-"
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
        and parameters["m6_detector_front_cap_length_x"] > 0
        and math.isclose(
            parameters["m6_detector_shell_front_max_x"],
            parameters["m6_detector_shell_split_x"]
            - parameters["m6_detector_shell_split_clearance_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_shell_rear_min_x"],
            parameters["m6_detector_shell_split_x"]
            + parameters["m6_detector_shell_split_clearance_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_shell_front_max_x"]
        < parameters["m6_detector_shell_rear_min_x"]
        and parameters["m6_detector_shell_split_overlap_x"] == 0
        and parameters["m6_detector_shell_split_clearance_x"] > 0
        and parameters["m6_detector_front_cap_length_x"]
        > parameters["m6_detector_shell_split_clearance_x"]
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
        and parameters["m6_detector_shell_support_nut_pocket_center_x"]
        - parameters["m6_ballhead_top_nut_pocket_depth"] / 2
        >= parameters["m6_detector_shell_support_boss_min_x"]
        and parameters["m6_detector_shell_support_nut_pocket_center_x"]
        + parameters["m6_ballhead_top_nut_pocket_depth"] / 2
        <= parameters["m6_detector_shell_support_boss_max_x"]
        and parameters["m6_ballhead_top_nut_pocket_af"]
        / math.cos(math.radians(30))
        < parameters["m6_detector_shell_support_boss_depth_y"]
        and parameters["m6_detector_shell_support_gusset_min_x"]
        < parameters["m6_detector_shell_support_boss_min_x"]
        and parameters["m6_detector_shell_support_gusset_max_x"]
        > parameters["m6_detector_shell_max_x"]
        and math.isclose(
            parameters["m6_detector_shell_support_gusset_root_y_start_positive"],
            parameters["m6_detector_shell_support_boss_max_y"]
            - parameters["m6_detector_shell_support_gusset_root_width_y"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_shell_support_gusset_wall_y_start_positive"],
            parameters["m6_detector_shell_max_y"]
            - parameters["m6_detector_shell_support_gusset_wall_width_y"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_shell_support_gusset_root_y_start_positive"]
        > parameters["m6_detector_shell_support_boss_center_y"]
        + parameters["m6_detector_shell_support_hole_d"] / 2
        and parameters["m6_detector_shell_support_boss_min_y"]
        + parameters["m6_detector_shell_support_gusset_root_width_y"]
        < parameters["m6_detector_shell_support_boss_center_y"]
        - parameters["m6_detector_shell_support_hole_d"] / 2
        and parameters["m6_detector_shell_support_gusset_wall_y_start_positive"]
        + parameters["m6_detector_shell_support_gusset_wall_width_y"]
        <= parameters["m6_detector_shell_max_y"] + 1e-4
        and parameters["m6_detector_shell_min_y"]
        + parameters["m6_detector_shell_support_gusset_wall_width_y"]
        <= parameters["m6_detector_shell_support_gusset_wall_y_start_positive"]
        and parameters["m6_detector_shell_support_gusset_bottom_z"]
        >= parameters["m6_detector_shell_bottom_z"]
        and parameters["m6_detector_shell_support_gusset_top_z"]
        <= parameters["m6_detector_shell_top_z"]
        and math.isclose(
            parameters["m6_detector_shell_support_gusset_height_z"],
            parameters["m6_detector_shell_support_gusset_top_z"]
            - parameters["m6_detector_shell_support_gusset_bottom_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
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

    # The net remains one net height, but the fixed-net post continues to the
    # full post_top datum.  The M6 optical group keeps its standalone geometry
    # datums; its former direct blind-M8 connection must not be treated as an
    # installed load path until an independent support is designed.
    if not parameters["m6_detector_direct_mount_enabled"]:
        if not (
            math.isclose(
                parameters["m6_detector_direct_mount_lower_post_top_z"],
                parameters["net_post_top_z"],
                rel_tol=0,
                abs_tol=1e-4,
            )
            and math.isclose(
                parameters["net_post_top_z"],
                parameters["post_top"],
                rel_tol=0,
                abs_tol=1e-4,
            )
            and parameters["net_post_top_z"] > parameters["net_panel_top_z"]
            and math.isclose(
                parameters["active_post_top_z"],
                parameters["net_post_top_z"],
                rel_tol=0,
                abs_tol=1e-4,
            )
            and math.isclose(
                parameters["active_post_total_height"],
                parameters["net_post_top_z"] - parameters["post_bottom"],
                rel_tol=0,
                abs_tol=1e-4,
            )
        ):
            raise RuntimeError(
                "tall fixed-net post must reach post_top and stay separate from the M6 direct mount: "
                f"{parameters}"
            )
        return

    if not (
        math.isclose(
            parameters["m6_detector_assembly_ballhead_net_interface_bottom_z"],
            parameters["m6_detector_assembly_ballhead_net_stud_center_z"]
            - parameters["m6_ballhead_net_stud_length"] / 2,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_socket_bottom_z"],
            parameters["m6_detector_direct_mount_socket_top_z"]
            - parameters["m6_detector_direct_mount_socket_height_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_socket_top_z"],
            parameters["m6_detector_assembly_ballhead_base_center_z"]
            - parameters["m6_ballhead_base_t"] / 2
            + parameters["m6_detector_direct_mount_socket_top_clearance_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_socket_height_z"],
            parameters["m6_detector_direct_mount_thread_depth_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_socket_center_z"],
            (
                parameters["m6_detector_direct_mount_socket_bottom_z"]
                + parameters["m6_detector_direct_mount_socket_top_z"]
            )
            / 2,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_direct_mount_socket_bottom_z"]
        < parameters["m6_detector_direct_mount_socket_top_z"]
        and math.isclose(
            parameters["m6_detector_direct_mount_thread_top_z"],
            parameters["m6_detector_assembly_ballhead_base_center_z"]
            - parameters["m6_ballhead_base_t"] / 2,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_thread_bottom_z"],
            parameters["m6_detector_direct_mount_thread_top_z"]
            - parameters["m6_detector_direct_mount_thread_depth_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_thread_depth_z"],
            parameters["m6_ballhead_net_stud_length"]
            + parameters["m6_detector_direct_mount_thread_depth_extra_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_direct_mount_thread_depth_z"]
        >= parameters["m6_ballhead_net_stud_length"] + 1
        and math.isclose(
            parameters["m6_detector_direct_mount_thread_tap_d"],
            parameters["m6_detector_direct_mount_socket_tap_d"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_direct_mount_thread_tap_d"]
        > parameters["m6_ballhead_net_thread_core_d"]
        and parameters["m6_detector_direct_mount_thread_tap_d"]
        < parameters["m6_ballhead_net_stud_d"]
        and parameters["m6_detector_direct_mount_socket_base_overlap_z"] == 0
        and parameters["m6_detector_direct_mount_socket_bottom_clearance_z"] == 0
        and parameters["m6_detector_direct_mount_socket_top_clearance_z"] == 0
        and parameters["m6_detector_direct_mount_nut_loading_clearance_z"] == 0
        and parameters["m6_detector_direct_mount_nut_loading_depth_z"] == 0
        and math.isclose(
            parameters["m6_detector_direct_mount_nut_pocket_bottom_z"],
            parameters["m6_detector_direct_mount_thread_bottom_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_nut_pocket_center_z"],
            parameters["m6_detector_direct_mount_thread_bottom_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_socket_center_x"],
            parameters["post_center_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_assembly_ballhead_center_x"],
            parameters["post_center_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_mount_x_offset"] > 0
        and parameters["m6_detector_assembly_optical_axis_x"]
        > parameters["table_width"] / 2
        and parameters["m6_detector_assembly_optical_axis_x"]
        < parameters["net_span"] / 2
        and math.isclose(
            parameters["m6_detector_direct_mount_arm_min_x"],
            parameters["post_center_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_arm_max_x"],
            parameters["post_center_x"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_direct_mount_arm_width_y"] == 0
        and parameters["m6_detector_direct_mount_arm_t_z"] == 0
        and math.isclose(
            parameters["m6_detector_direct_mount_post_inner_face_x"],
            parameters["post_center_x"] - parameters["post_body_width"] / 2,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(
            parameters["m6_detector_direct_mount_lower_post_top_z"],
            parameters["m6_detector_direct_mount_thread_bottom_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_direct_mount_lower_post_top_z"]
        > parameters["post_bottom"]
        and parameters["m6_detector_direct_mount_lower_post_top_z"]
        - parameters["post_bottom"]
        < 270
        and parameters["m6_detector_direct_mount_web_width_y"] == 0
        and parameters["m6_detector_direct_mount_web_t_x"] == 0
        and math.isclose(
            parameters["m6_detector_direct_mount_arm_top_z"],
            parameters["m6_detector_direct_mount_arm_bottom_z"],
            rel_tol=0,
            abs_tol=1e-4,
        )
        and parameters["m6_detector_direct_mount_arm_bottom_z"]
        >= parameters["net_height"]
    ):
        raise RuntimeError(
            f"direct ballhead-to-same-material-PETG lower-stand interface is inconsistent: {parameters}"
        )


def validate_split_fastener_label_contract(parameters: dict[str, float]) -> None:
    """Keep the nine split-joint identification digits printable and hidden."""

    source_text = SOURCE.read_text(encoding="utf-8")
    required_fragments = (
        "module clamp_split_fastener_label_recess_negative_positive(y_side)",
        "module clamp_split_fastener_labels_positive(y_side)",
        "text(str(index + 1)",
        "clamp_split_fastener_label_recess_negative_positive(y_side);",
        "clamp_split_fastener_labels_positive(y_side);",
        "label_rotation = y_side < 0 ? [-90, 0, 0] : [90, 0, 0];",
    )
    if any(fragment not in source_text for fragment in required_fragments):
        raise RuntimeError(
            "split-joint label source is incomplete: numbered positive digits must be "
            "defined and called after the hidden split-face recess"
        )

    label_size = parameters["clamp_split_fastener_label_size"]
    label_height = parameters["clamp_split_fastener_label_height"]
    label_offset = parameters["clamp_split_fastener_label_offset_x"]
    recess_depth = parameters["clamp_split_fastener_label_pocket_depth_y"]
    floor_overlap = parameters["clamp_split_fastener_label_floor_overlap_y"]
    head_d = parameters["clamp_split_fastener_head_d"]
    nut_radius = (
        parameters["clamp_split_nut_af"]
        + 2 * parameters["clamp_split_nut_clearance"]
    ) / (2 * math.cos(math.radians(30)))
    seam_half_gap = parameters["clamp_split_seam_gap_y"] / 2
    user_floor_y = -seam_half_gap - recess_depth
    opponent_floor_y = seam_half_gap + recess_depth
    user_digit_top_y = user_floor_y - floor_overlap + label_height
    opponent_digit_top_y = opponent_floor_y + floor_overlap - label_height
    if not (
        2.0 <= label_size <= 5.0
        and 0.30 <= label_height <= 0.80
        and 0.50 <= recess_depth <= 1.20
        and 0.0 <= floor_overlap <= 0.10
        and label_offset - label_size / 2
        >= max(head_d, 2 * nut_radius) / 2 + 0.2
        and user_digit_top_y <= -seam_half_gap - 0.20
        and opponent_digit_top_y >= seam_half_gap + 0.20
    ):
        raise RuntimeError(
            "split-joint labels must be raised, pocket-floor mounted, and clear of "
            f"the M5 head/nut envelope: size={label_size}, height={label_height}, "
            f"offset={label_offset}, recess_depth={recess_depth}, "
            f"user_floor_y={user_floor_y}, opponent_floor_y={opponent_floor_y}, "
            f"user_digit_top_y={user_digit_top_y}, opponent_digit_top_y={opponent_digit_top_y}"
        )


def validate_net_retention_contract(parameters: dict[str, float]) -> None:
    """Validate the historical side-open cylindrical rod recess contract."""

    source_text = SOURCE.read_text(encoding="utf-8")
    required_fragments = (
        "module net_passage_negative_positive()",
        "module net_clamp_rod_recess_negative_positive()",
        "module net_clamp_rod_positive()",
        "module net_clamp_net_sleeve_preview_positive()",
        "module net_clamp_rod_printable_positive()",
        "module net_clamp_fit_probe_positive()",
        "module net_clamp_fit_section_positive()",
        "module post_split_male_keys_positive()",
        "module post_split_female_pockets_negative_positive()",
        "module post_split_upper_clearance_holes_negative_positive()",
        "module post_split_lower_pilots_negative_positive()",
        "net_passage_negative_positive();",
        "net_clamp_rod_recess_negative_positive();",
        "net_clamp_rod_positive();",
        "net_clamp_net_sleeve_preview_positive();",
        "post_split_male_keys_positive();",
        "post_split_upper_clearance_holes_negative_positive();",
        "post_split_lower_pilots_negative_positive();",
    )
    if any(fragment not in source_text for fragment in required_fragments):
        raise RuntimeError(
            "net retention source is incomplete: the thin cloth passage, side-open cylindrical rod recess, "
            "printable rod, sleeve preview, fit probe and split-post calls must all remain present"
        )
    retired = (
        "net_clamp_channel_negative_positive",
        "net_clamp_clip_positive",
        "net_clamp_clip_printable_positive",
        "net_clamp_keeper_positive",
        "net_clamp_keeper_relief_negative_positive",
        "net_clamp_keeper_latch_positive",
        "net_clamp_clip_lock",
        "net_clamp_lock_hardware_positive",
    )
    leaked = [name for name in retired if name in source_text]
    if leaked:
        raise RuntimeError(f"retired rectangular U-clip/keeper path remains in source: {leaked}")

    rod_d = parameters["net_clamp_rod_d"]
    rod_clearance = parameters["net_clamp_rod_clearance"]
    axis_x = parameters["net_clamp_rod_axis_x"]
    sleeve_d = parameters["net_clamp_rod_sleeve_outer_d"]
    channel_min_x = parameters["net_clamp_channel_void_min_x"]
    channel_max_x = parameters["net_clamp_channel_void_max_x"]
    channel_width_y = parameters["net_clamp_channel_width_y"]
    channel_bottom = parameters["net_clamp_channel_bottom_z"]
    channel_top = parameters["net_clamp_channel_top_z"]
    fixture_bottom_z = parameters["net_fixture_bottom_z"]
    fixture_top_z = parameters["net_panel_top_z"]
    if not (
        8 <= rod_d <= 10
        and rod_clearance >= 0.4
        and math.isclose(
            parameters["net_clamp_rod_bore_d"],
            rod_d + 2 * rod_clearance,
            rel_tol=0,
            abs_tol=1e-4,
        )
        and math.isclose(parameters["net_clamp_rod_length"], parameters["net_height"], rel_tol=0, abs_tol=1e-4)
        and math.isclose(channel_bottom, fixture_bottom_z, rel_tol=0, abs_tol=1e-4)
        and math.isclose(channel_top, fixture_top_z, rel_tol=0, abs_tol=1e-4)
        and math.isclose(parameters["net_clamp_rod_axis_y"], 0, rel_tol=0, abs_tol=1e-4)
        and channel_min_x < axis_x < channel_max_x
        and axis_x - sleeve_d / 2 >= channel_min_x - 0.01
        and axis_x + sleeve_d / 2 <= channel_max_x + 0.01
        and sleeve_d > rod_d
        and parameters["net_clamp_rod_sleeve_clearance"] > 0
        and parameters["net_clamp_rod_print_fn"] >= 32
        and channel_width_y >= sleeve_d + 2 * parameters["net_clamp_channel_side_clearance"]
        and math.isclose(parameters["net_passage_width_y"], 3, rel_tol=0, abs_tol=1e-4)
        and parameters["net_passage_width_y"] > parameters["net_sheet_t"]
        and parameters["net_passage_side_clearance_y"] > 0
        and parameters["net_passage_min_x"] < parameters["post_center_x"] - parameters["post_body_width"] / 2
        and parameters["net_passage_max_x"] > parameters["post_center_x"] + parameters["post_body_width"] / 2
        and math.isclose(parameters["net_passage_bottom_z"], fixture_bottom_z, rel_tol=0, abs_tol=1e-4)
        and math.isclose(parameters["net_passage_top_z"], fixture_top_z, rel_tol=0, abs_tol=1e-4)
        and parameters["net_passage_top_z"] <= parameters["post_split_z"]
    ):
        raise RuntimeError(
            "cylindrical net rod, side-open recess, sleeve envelope, or thin cloth passage is inconsistent: "
            f"rod={rod_d}, axis=({axis_x}, {parameters['net_clamp_rod_axis_y']}), "
            f"channel_x=({channel_min_x}, {channel_max_x}), channel_y={channel_width_y}, "
            f"passage_y={parameters['net_passage_width_y']}"
        )


def main() -> None:
    openscad = find_openscad()
    with tempfile.TemporaryDirectory(prefix="pingpang-smartgear-net-stand-") as directory:
        output_dir = Path(directory)
        parameters = probe_parameters(openscad, output_dir)
        validate_split_fastener_label_contract(parameters)
        validate_current_m6_contract(parameters)
        validate_net_retention_contract(parameters)
        validate_post_clamp_slide_path(openscad, output_dir, parameters)

        for part in PARTS:
            output = output_dir / f"{part}.stl"
            require_stl(
                run_openscad(openscad, output, f'PART="{part}"'),
                output,
                f"PART={part}",
                require_closed=part not in PREVIEW_ONLY_PARTS,
            )

        validate_electronics_interference_probes(openscad, output_dir)

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
            "post_clamp_carrier",
            "post_clamp_carrier_lower",
            "post_clamp_carrier_upper",
            "post_joint_exploded",
            "clamp_slide_exploded",
            "clamp_slide_fit_probe",
            "clamp_slide_fit_section",
            "clamp_body_segment",
            "clamp_body_half_user",
            "clamp_body_half_opponent",
            "net_clamp_fit_probe",
            "net_clamp_fit_section",
            "table_clamp",
            "table_clamp_section",
            "table_clamp_body",
            "clamp_electronics_ui_panel",
            "clamp_electronics_ui_panel_mount",
            "clamp_electronics_emitter_preview",
            "clamp_electronics_full_cutaway",
            "clamp_electronics_exploded",
            "clamp_electronics_emitter_exploded",
            "clamp_top_pad",
            "clamp_pressure_pad",
            "clamp_pressure_pad_guard",
            "clamp_screw",
            "clamp_printed_screw",
            "clamp_body_nut",
            "clamp_knob",
            "clamp_knob_nut",
            "optical_rail",
            "optical_strip",
            "optical_module_carrier",
            "m6_detector_body",
            "m6_detector_shell_front",
            "m6_detector_shell_rear",
            "m6_detector_bottom_cover",
            "m6_detector_cable_gland",
            "m6_detector_wiring_reference",
            "m6_detector_bottom_gasket",
            "m6_detector_net_connector",
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
            # These are composite review envelopes, not printable solids. Their
            # Minkowski/intersection triangulation can legitimately choose a
            # different diagonal or facet tessellation after x reflection even
            # though the bounds and visual assembly are mirrored. Standalone
            # print parts keep the strict vertex-set equality below.
            if part in MIRROR_TRIANGULATION_RELAXED_PARTS:
                continue
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
        clamp_body_bounds = stl_bounds(output_dir / "table_clamp_body.stl")
        clamp_section_bounds = stl_bounds(output_dir / "table_clamp_section.stl")
        top_pad_bounds = stl_bounds(output_dir / "clamp_top_pad.stl")
        pressure_pad_bounds = stl_bounds(output_dir / "clamp_pressure_pad.stl")
        pressure_pad_guard_bounds = stl_bounds(
            output_dir / "clamp_pressure_pad_guard.stl"
        )
        screw_bounds = stl_bounds(output_dir / "clamp_screw.stl")
        printed_screw_bounds = stl_bounds(
            output_dir / "clamp_printed_screw.stl"
        )
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
        optical_rail_bounds = stl_bounds(output_dir / "optical_rail.stl")
        carrier_bounds = stl_bounds(output_dir / "optical_module_carrier.stl")
        stg_outer_bounds = stl_bounds(output_dir / "stg120_outer_carrier.stl")
        stg_center_bounds = stl_bounds(output_dir / "stg120_center_bridge.stl")
        stg_preview_bounds = stl_bounds(output_dir / "stg120_preview.stl")
        coupon_bounds = stl_bounds(output_dir / "m6_sensor_test_coupon.stl")
        assembly_bounds = stl_bounds(output_dir / "assembly.stl")
        post_bounds = stl_bounds(output_dir / "post.stl")
        post_segment_bounds = stl_bounds(output_dir / "post_segment.stl")
        post_clamp_carrier_lower_bounds = stl_bounds(
            output_dir / "post_clamp_carrier_lower.stl"
        )
        post_clamp_carrier_upper_bounds = stl_bounds(
            output_dir / "post_clamp_carrier_upper.stl"
        )
        clamp_body_segment_bounds = stl_bounds(output_dir / "clamp_body_segment.stl")
        clamp_body_half_user_bounds = stl_bounds(
            output_dir / "clamp_body_half_user.stl"
        )
        clamp_body_half_opponent_bounds = stl_bounds(
            output_dir / "clamp_body_half_opponent.stl"
        )
        net_clamp_rod_bounds = stl_bounds(output_dir / "net_clamp_rod.stl")
        if net_bounds[0] >= 0 or net_bounds[1] <= 0:
            raise RuntimeError(f"net is not centered across the table: {net_bounds}")
        cavity_x_min = parameters["clamp_electronics_cavity_x_min"]
        cavity_x_max = parameters["clamp_electronics_cavity_x_max"]
        cavity_y_half = parameters["clamp_electronics_cavity_y_half"]
        cavity_length = parameters["clamp_electronics_cavity_length_x"]
        board_length = parameters["clamp_electronics_board_length_x"]
        board_width = parameters["clamp_electronics_board_width_y"]
        if not (
            cavity_length > board_length
            and board_width / 2 < cavity_y_half
        ):
            raise RuntimeError(
                "electronics cavity does not leave a board envelope: "
                f"cavity=({cavity_x_min}, {cavity_x_max}, +/-{cavity_y_half}), "
                f"board=({board_length} x {board_width})"
            )
        end_margin_x = (
            parameters["clamp_electronics_cavity_length_x"]
            - parameters["clamp_electronics_board_length_x"]
        ) / 2
        if not (
            parameters["clamp_electronics_board_bracket_clearance_xy"] >= 0.2
            and parameters["clamp_electronics_board_bracket_clearance_z"] >= 0.15
            and parameters["clamp_electronics_board_bracket_lower_lip_below_z"] >= 0.6
            and parameters["clamp_electronics_board_bracket_lower_lip_below_z"]
            - parameters["clamp_electronics_board_bracket_lower_lip_t_z"]
            >= parameters["clamp_electronics_board_bracket_clearance_z"]
            and parameters["clamp_electronics_board_bracket_upper_lip_gap_z"] >= 0.2
            and parameters["clamp_electronics_board_bracket_upper_lip_t_z"] >= 0.8
            and parameters["clamp_electronics_board_bracket_root_overlap_x"] >= 3.0
            and parameters["clamp_electronics_board_bracket_root_overlap_x"]
            < end_margin_x
            and parameters["clamp_electronics_board_bracket_wall_overlap_x"] > 0
            and 0.3
            <= parameters["clamp_electronics_board_bracket_edge_overlap_x"]
            < end_margin_x
            and parameters["clamp_electronics_board_bracket_y_overrun"] >= 0
            and parameters["clamp_electronics_board_width_y"] / 2
            + parameters["clamp_electronics_board_bracket_y_overrun"]
            < cavity_y_half
        ):
            raise RuntimeError(
                "PCB end brackets must leave printable board clearance and a rooted two-lip capture: "
                f"clearance_xy={parameters['clamp_electronics_board_bracket_clearance_xy']}, "
                f"clearance_z={parameters['clamp_electronics_board_bracket_clearance_z']}, "
                f"wall_overlap={parameters['clamp_electronics_board_bracket_wall_overlap_x']}"
            )
        if not (
            0 <= parameters["clamp_electronics_emitter_clip_top_clearance_z"]
            <= 0.8
        ):
            raise RuntimeError(
                "emitter PCB clips must end at or below the board underside: "
                f"clearance={parameters['clamp_electronics_emitter_clip_top_clearance_z']}"
            )
        board_y_min = (
            parameters["clamp_electronics_main_board_y_shift"]
            - parameters["clamp_electronics_board_width_y"]
        )
        board_y_max = parameters["clamp_electronics_main_board_y_shift"]
        wall_clearance_y = parameters[
            "clamp_electronics_main_board_wall_clearance_y"
        ]
        if not (
            wall_clearance_y > 0
            and board_y_min >= -cavity_y_half + wall_clearance_y - 0.01
            and board_y_max <= cavity_y_half - wall_clearance_y + 0.01
        ):
            raise RuntimeError(
                "main PCB must be centered inside the electronics cavity: "
                f"board_y=({board_y_min}, {board_y_max}), cavity=+/-{cavity_y_half}, "
                f"wall_clearance={wall_clearance_y}"
            )
        ui_plane_y = parameters["clamp_electronics_ui_side_board_plane_y"]
        ui_shift_y = parameters["clamp_electronics_ui_side_panel_inward_shift_y"]
        ui_window_border = parameters["clamp_electronics_ui_side_window_border"]
        ui_panel_border = parameters["clamp_electronics_ui_insert_panel_border"]
        ui_panel_lower_z = (
            parameters["clamp_electronics_ui_side_board_z_min"]
            - ui_panel_border
        )
        ui_panel_inner_local_z = parameters["clamp_electronics_ui_panel_inner_local_z"]
        ui_panel_outer_local_z = parameters["clamp_electronics_ui_panel_outer_local_z"]
        ui_wall_outer_y = parameters["clamp_reinforcement_depth_y"] / 2
        ui_panel_inner_y = ui_plane_y + ui_panel_inner_local_z
        ui_panel_outer_y = ui_plane_y + ui_panel_outer_local_z
        ui_frame_outer_border = parameters["clamp_electronics_ui_panel_mount_outer_border"]
        ui_frame_inner_border = parameters["clamp_electronics_ui_panel_mount_inner_border"]
        ui_frame_window_clearance = parameters[
            "clamp_electronics_ui_panel_mount_window_clearance"
        ]
        ui_frame_t = parameters["clamp_electronics_ui_panel_mount_t"]
        ui_frame_integrated_overlap = parameters[
            "clamp_electronics_ui_integrated_capture_overlap_z"
        ]
        ui_frame_hole_d = parameters["clamp_electronics_ui_panel_mount_hole_d"]
        ui_frame_min_edge_land = parameters[
            "clamp_electronics_ui_panel_mount_min_edge_land"
        ]
        ui_wall_pilot_d = parameters["clamp_electronics_ui_wall_pilot_d"]
        ui_wall_pilot_floor_t = parameters[
            "clamp_electronics_ui_wall_pilot_floor_t"
        ]
        # Compatibility values must stay zero so no stale positive boss can
        # enter the printable body through an older module name.
        ui_boss_d = parameters["clamp_electronics_ui_panel_mount_boss_d"]
        ui_screw_d = parameters["clamp_electronics_ui_panel_mount_screw_nominal_d"]
        ui_boss_h = parameters["clamp_electronics_ui_panel_mount_boss_height"]
        ui_frame_hole_centers = (
            (10.0, -4.6), (48.0, -4.6),
            (10.0, 32.6), (48.0, 32.6),
            (-4.6, 8.0), (-4.6, 20.0),
            (62.6, 8.0), (62.6, 20.0),
        )
        ui_frame_edge_lands = [
            min(
                x - (-ui_frame_outer_border) - ui_frame_hole_d / 2,
                (parameters["clamp_electronics_ui_board_length_x"] + ui_frame_outer_border)
                - x - ui_frame_hole_d / 2,
                y - (-ui_frame_outer_border) - ui_frame_hole_d / 2,
                (parameters["clamp_electronics_ui_board_width_y"] + ui_frame_outer_border)
                - y - ui_frame_hole_d / 2,
            )
            for x, y in ui_frame_hole_centers
        ]
        # The released UI panel mount is stepped: its broad mounting flange
        # sits on the cavity side of the solid wall, and only the narrower
        # capture bridge enters the y+ window. The bridge intentionally
        # overlaps the panel perimeter so both pieces are one connected print.
        ui_frame_mount_front_y = cavity_y_half
        ui_frame_mount_back_y = ui_frame_mount_front_y - ui_frame_t
        ui_frame_capture_back_y = ui_frame_mount_front_y
        ui_frame_capture_front_y = ui_panel_inner_y + ui_frame_integrated_overlap
        if not (
            ui_shift_y > 0
            and ui_plane_y < cavity_y_half
            and ui_plane_y > board_y_max
            and ui_frame_mount_back_y > board_y_max + 0.1
            and ui_frame_mount_front_y <= cavity_y_half + 0.01
            and ui_frame_capture_back_y >= cavity_y_half - 0.01
            and ui_frame_capture_front_y > ui_frame_capture_back_y + 2.0
            and ui_frame_integrated_overlap > 0
            and ui_frame_capture_front_y > ui_panel_inner_y
            and ui_panel_border <= ui_window_border - 0.4
            and ui_frame_outer_border > ui_window_border
            and ui_frame_window_clearance >= 0.2
            and ui_window_border - ui_frame_window_clearance > ui_panel_border
            and ui_frame_inner_border < ui_panel_border
            and ui_frame_outer_border - ui_window_border >= 2.0
            and ui_frame_t >= 2.0
            and ui_frame_min_edge_land >= 1.0
            and min(ui_frame_edge_lands) >= ui_frame_min_edge_land - 0.01
            and ui_wall_pilot_floor_t >= 0.5
            and abs(ui_screw_d - 2.0) <= 0.01
            and 1.5 <= ui_wall_pilot_d < ui_screw_d
            and ui_frame_hole_d > ui_screw_d
            and abs(ui_boss_d) <= 0.01
            and abs(ui_boss_h) <= 0.01
            and ui_wall_outer_y - ui_wall_pilot_floor_t - ui_frame_mount_front_y > 2.0
            and abs(ui_panel_outer_y - ui_wall_outer_y) <= 0.05
        ):
            raise RuntimeError(
                "UI integrated panel mount must fit from the cavity, finish flush, fuse the capture ring into the panel perimeter, and keep the 2 mm screw in a direct 1.6 mm wall pilot: "
                f"plane_y={ui_plane_y}, panel_inner_y={ui_panel_inner_y}, panel_outer_y={ui_panel_outer_y}, "
                f"mount_frame=({ui_frame_mount_back_y}, {ui_frame_mount_front_y}), "
                f"capture_frame=({ui_frame_capture_back_y}, {ui_frame_capture_front_y}), "
                f"integrated_overlap={ui_frame_integrated_overlap}, "
                f"frame_t={ui_frame_t}, edge_land={min(ui_frame_edge_lands)}, "
                f"wall_pilot={ui_wall_pilot_d}, screw={ui_screw_d}, bosses=({ui_boss_d}, {ui_boss_h})"
            )
        if abs(net_bounds[5] - parameters["net_panel_top_z"]) > 0.01:
            raise RuntimeError(f"net panel top does not meet the direct cloth-top datum: {net_bounds}")
        inner_face = parameters["post_center_x"] - parameters["post_body_width"] / 2
        outer_face = parameters["post_center_x"] + parameters["post_body_width"] / 2
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
        half_depth = parameters["clamp_pad_depth"] / 2
        seam_half_gap = parameters["clamp_split_seam_gap_y"] / 2
        if not (
            clamp_body_half_user_bounds[2]
            <= -half_depth + 0.01
            and clamp_body_half_user_bounds[3]
            <= -seam_half_gap + 0.01
            and clamp_body_half_opponent_bounds[2]
            >= seam_half_gap - 0.01
            and clamp_body_half_opponent_bounds[3]
            >= half_depth - 0.01
            and clamp_body_half_user_bounds[0]
            < parameters["clamp_pad_outer_x"]
            and clamp_body_half_opponent_bounds[1]
            > parameters["clamp_pad_outer_x"] - 0.01
            and clamp_body_half_user_bounds[5]
            > clamp_body_half_user_bounds[4]
            and clamp_body_half_opponent_bounds[5]
            > clamp_body_half_opponent_bounds[4]
        ):
            raise RuntimeError(
                "split C-clamp halves do not leave the declared y=0 seam or full structural envelope: "
                f"user={clamp_body_half_user_bounds}, opponent={clamp_body_half_opponent_bounds}"
            )
        if not (
            0 < parameters["clamp_split_boss_min_cavity_overlap_x"]
            <= parameters["clamp_split_boss_d"]
            and parameters["clamp_split_boss_min_cavity_overlap_x"]
            >= parameters["clamp_split_boss_d"] / 2 - 0.01
        ):
            raise RuntimeError(
                "split C-clamp boss filter allows a shallow cavity-edge graze: "
                f"min_overlap={parameters['clamp_split_boss_min_cavity_overlap_x']}, "
                f"boss_d={parameters['clamp_split_boss_d']}"
            )
        def reinforcement_bottom_at(x: float) -> float:
            start = parameters["clamp_reinforcement_start_x"]
            end = parameters["clamp_reinforcement_end_x"]
            near = parameters["clamp_reinforcement_near_table_bottom_z"]
            outer = parameters["clamp_reinforcement_outer_bottom_z"]
            return near + (x - start) / (end - start) * (outer - near)

        def cavity_overlap_at(x: float, diameter: float) -> float:
            return min(
                x + diameter / 2,
                cavity_x_max,
            ) - max(
                x - diameter / 2,
                cavity_x_min,
            )

        lower_boss_d = parameters["clamp_split_lower_boss_d"]
        lower_boss_clearance_z = parameters[
            "clamp_split_lower_boss_board_clearance_z"
        ]
        expected_lower_boss_z = (
            parameters["clamp_electronics_board_bottom_z"]
            - lower_boss_clearance_z
            - lower_boss_d / 2
            - parameters["clamp_split_lower_boss_drop_z"]
        )
        for label, x_key, z_key in (
            ("right", "clamp_split_lower_right_x", "clamp_split_lower_right_z"),
            ("left", "clamp_split_lower_left_x", "clamp_split_lower_left_z"),
        ):
            x = parameters[x_key]
            z = parameters[z_key]
            cavity_floor = reinforcement_bottom_at(x) + parameters[
                "clamp_electronics_cavity_floor_t"
            ]
            if not (
                lower_boss_d > parameters["clamp_split_fastener_head_d"]
                and lower_boss_d < parameters["clamp_split_boss_d"]
                and lower_boss_clearance_z >= 0.5
                and 0 <= parameters["clamp_split_lower_boss_drop_z"] <= 10
                and math.isclose(z, expected_lower_boss_z, abs_tol=0.01)
                and z + lower_boss_d / 2 < ui_panel_lower_z - 0.5
                and cavity_overlap_at(x, lower_boss_d)
                >= parameters["clamp_split_boss_min_cavity_overlap_x"]
                and z - lower_boss_d / 2
                < parameters["clamp_electronics_cavity_top_z"]
                and z + lower_boss_d / 2 > cavity_floor
                and z - lower_boss_d / 2
                > reinforcement_bottom_at(x) + 0.5
                and x - lower_boss_d / 2
                > parameters["clamp_reinforcement_start_x"] + 0.5
                and x + lower_boss_d / 2
                < parameters["clamp_reinforcement_end_x"] - 0.5
                and z + lower_boss_d / 2
                <= parameters["clamp_electronics_board_bottom_z"]
                - lower_boss_clearance_z + 0.01
            ):
                raise RuntimeError(
                    f"lower {label} split boss must clear the main PCB and remain inside the tapered wall: "
                    f"x={x}, z={z}, d={lower_boss_d}, board_bottom="
                    f"{parameters['clamp_electronics_board_bottom_z']}, "
                    f"drop_z={parameters['clamp_split_lower_boss_drop_z']}, "
                    f"ui_panel_lower_z={ui_panel_lower_z}, "
                    f"reinforcement_bottom={reinforcement_bottom_at(x):.3f}"
                )
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
            and screw_bounds[5]
            <= pressure_pad_bounds[5]
            - parameters["clamp_pressure_pad_t"]
            + parameters["clamp_pressure_pad_screw_socket_depth"]
            + 0.01
            and abs(pressure_pad_bounds[5] - parameters["clamp_pressure_pad_top_z"]) < 0.01
            and abs(
                pressure_pad_bounds[0]
                - (
                    parameters["clamp_screw_x"]
                    - parameters["clamp_pressure_pad_d"] / 2
                )
            )
            < 0.01
            and abs(
                pressure_pad_bounds[1]
                - (
                    parameters["clamp_screw_x"]
                    + parameters["clamp_pressure_pad_d"] / 2
                )
            )
            < 0.01
            and abs(
                pressure_pad_bounds[2]
                + parameters["clamp_pressure_pad_d"] / 2
            )
            < 0.01
            and abs(
                pressure_pad_bounds[3]
                - parameters["clamp_pressure_pad_d"] / 2
            )
            < 0.01
            and abs(screw_bounds[5] - parameters["clamp_screw_top_z"]) < 0.01
            and pressure_pad_guard_bounds[2] < pressure_pad_guard_bounds[3]
            and pressure_pad_guard_bounds[4]
            < pressure_pad_bounds[5] - parameters["clamp_pressure_pad_t"]
            and abs(
                pressure_pad_guard_bounds[0]
                - (
                    parameters["clamp_screw_x"]
                    - parameters["clamp_pressure_pad_retainer_outer_d"] / 2
                )
            )
            < 0.01
            and abs(
                pressure_pad_guard_bounds[1]
                - (
                    parameters["clamp_screw_x"]
                    + parameters["clamp_pressure_pad_retainer_outer_d"] / 2
                )
            )
            < 0.01
            and abs(
                pressure_pad_guard_bounds[4]
                - parameters["clamp_pressure_pad_retainer_bottom_z"]
            )
            < 0.01
            and abs(
                pressure_pad_guard_bounds[5]
                - parameters["clamp_pressure_pad_retainer_top_z"]
            )
            < 0.01
            and printed_screw_bounds[5] < -parameters["table_thickness"]
            and printed_screw_bounds[5]
            <= pressure_pad_bounds[5]
            - parameters["clamp_pressure_pad_t"]
            + parameters["clamp_pressure_pad_screw_socket_depth"]
            + 0.01
            and abs(knob_bounds[4] - parameters["clamp_knob_bottom_z"]) < 0.01
            and abs(knob_bounds[5] - parameters["clamp_knob_top_z"]) < 0.01
            and screw_bounds[4] < knob_bounds[5]
            and knob_nut_bounds[4] >= knob_bounds[4] - 0.01
            and knob_nut_bounds[5] <= knob_bounds[5] + 0.01
            and body_nut_bounds[4] >= parameters["clamp_body_nut_z"] - 0.01
            and body_nut_bounds[5] <= parameters["clamp_body_nut_top_z"] + 0.01
            and body_nut_bounds[5] <= parameters["clamp_lower_arm_top_z"] + 0.01
        ):
            raise RuntimeError(
                "pressure pad, coarse printed screw tip or nut capture breaks the no-drill clamp path: "
                f"pad={pressure_pad_bounds}, screw={screw_bounds}, "
                f"body_nut={body_nut_bounds}, knob={knob_bounds}, knob_nut={knob_nut_bounds}"
            )
        if not (
            sensor_bounds[0] > parameters["sensor_x"] - parameters["sensor_length"] / 2 - 0.01
            and sensor_bounds[1] < parameters["sensor_x"] + parameters["sensor_length"] / 2 + 0.01
            and sensor_bounds[2] < -parameters["net_sheet_t"] / 2
            and sensor_bounds[3] > parameters["net_sheet_t"] / 2
            and sensor_bounds[4] < parameters["net_panel_top_z"]
            and sensor_bounds[5] >= parameters["net_panel_top_z"] - 0.01
            and sensor_bounds[1] <= inner_face - parameters["sensor_post_clearance_x"] + 0.01
        ):
            raise RuntimeError(f"PVDF mount does not straddle the net top edge or clear the post: {sensor_bounds}")
        if not (
            abs(film_bounds[2] - parameters["sensor_film_y"]) < 0.01
            and abs(
                film_bounds[4]
                - (parameters["net_panel_top_z"] - parameters["sensor_film_height"])
            ) < 0.01
            and film_bounds[2] < film_bounds[3]
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
            and abs(post_bounds[5] - parameters["net_post_top_z"]) < 0.01
            and abs(post_segment_bounds[4] - parameters["post_bottom"]) < 0.01
            and post_segment_bounds[5] >= parameters["post_split_z"] - 0.01
            and post_segment_bounds[5] < parameters["net_post_top_z"]
            and post_segment_bounds[1] - post_segment_bounds[0] >= parameters["post_body_width"]
            and post_segment_bounds[3] - post_segment_bounds[2] >= parameters["post_body_depth"]
            and abs(
                post_clamp_carrier_upper_bounds[4] - parameters["post_split_z"]
            ) < 0.01
            and abs(
                post_clamp_carrier_upper_bounds[5] - parameters["net_post_top_z"]
            ) < 0.01
            and post_clamp_carrier_upper_bounds[1] - post_clamp_carrier_upper_bounds[0]
            >= parameters["post_body_width"]
            and post_clamp_carrier_upper_bounds[3] - post_clamp_carrier_upper_bounds[2]
            >= parameters["post_body_depth"]
        ):
            raise RuntimeError(
                "split upright bounds are inconsistent: "
                f"assembly={post_bounds}, lower={post_segment_bounds}, "
                f"upper={post_clamp_carrier_upper_bounds}"
            )
        diagonal_post_bounds = transform_bounds(
            (
                (post_clamp_carrier_lower_bounds[0], post_clamp_carrier_lower_bounds[2], post_clamp_carrier_lower_bounds[4]),
                (post_clamp_carrier_lower_bounds[1], post_clamp_carrier_lower_bounds[3], post_clamp_carrier_lower_bounds[5]),
            ),
            rotation_matrix_xyz(0, 51, 45),
        )
        diagonal_post_size = dimensions(diagonal_post_bounds)
        if not (
            post_clamp_carrier_lower_bounds[0]
            <= inner_face
            - parameters["post_interface_transition_extra_x"]
            + 0.01
            and post_clamp_carrier_lower_bounds[1]
            >= outer_face
            + parameters["post_interface_transition_extra_x"]
            - 0.01
            and post_clamp_carrier_lower_bounds[3] - post_clamp_carrier_lower_bounds[2]
            >= parameters["post_body_depth"]
            + 2 * parameters["post_interface_transition_extra_y"]
            - 0.01
            and post_clamp_carrier_lower_bounds[4]
            >= parameters["post_skp_leg_foot_bottom_z"] - 0.01
            and post_clamp_carrier_lower_bounds[5]
            >= parameters["post_split_z"] - 0.01
            and max(diagonal_post_size) <= 253.0 + 1e-3
        ):
            raise RuntimeError(
                "lower split post/carrier cannot use the tested 256 mm diagonal print pose: "
                f"carrier={post_clamp_carrier_lower_bounds}, diagonal_size={diagonal_post_size}"
            )
        rod_sizes = (
            net_clamp_rod_bounds[1] - net_clamp_rod_bounds[0],
            net_clamp_rod_bounds[3] - net_clamp_rod_bounds[2],
            net_clamp_rod_bounds[5] - net_clamp_rod_bounds[4],
        )
        if not (
            max(rod_sizes) > parameters["net_clamp_rod_length"] - 0.01
            and max(rod_sizes) < parameters["net_clamp_rod_length"] + 0.01
            and min(rod_sizes) > parameters["net_clamp_rod_d"] - 0.01
            and min(rod_sizes) < parameters["net_clamp_rod_d"] + 0.01
            and sorted(rod_sizes)[1] > parameters["net_clamp_rod_d"] - 0.01
            and sorted(rod_sizes)[1] < parameters["net_clamp_rod_d"] + 0.01
        ):
            raise RuntimeError(
                "printed net rod bounds do not match one cylindrical Ø10 x 152.5 mm part: "
                f"rod={net_clamp_rod_bounds}"
            )
        if not (
            clamp_body_segment_bounds[0]
            <= parameters["clamp_pad_x"] + 0.01
            and clamp_body_segment_bounds[1]
            >= parameters["clamp_fixed_body_max_x"] - 0.01
            and clamp_body_segment_bounds[1]
            <= parameters["clamp_fixed_body_max_x"] + 0.01
            and clamp_body_segment_bounds[3] - clamp_body_segment_bounds[2]
            >= parameters["clamp_pad_depth"] - 0.01
            and clamp_body_segment_bounds[5]
            >= parameters["clamp_solid_bridge_top_z"] - 0.01
            ):
            raise RuntimeError(
                "fixed gray clamp body does not own the full C-frame outboard face or span the clamp depth: "
                f"body={clamp_body_segment_bounds}"
            )
        socket_x = parameters["m6_detector_direct_mount_socket_center_x"]
        socket_radius = parameters["m6_detector_direct_mount_socket_outer_d"] / 2
        if parameters["m6_detector_direct_mount_enabled"] and not (
            post_bounds[0] <= socket_x - socket_radius + 0.01
            and post_bounds[1] >= socket_x + socket_radius - 0.01
            and post_bounds[2] <= -socket_radius + 0.01
            and post_bounds[3] >= socket_radius - 0.01
            and post_bounds[5]
            >= parameters["m6_detector_direct_mount_socket_top_z"] - 0.01
        ):
            raise RuntimeError(
                "split post assembly does not contain the direct ballhead support: "
                f"post={post_bounds}"
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
                parameters["clamp_pressure_pad_screw_socket_depth"],
                parameters["clamp_knob_nut_stack_depth"],
                # The lower arm follows the tabletop underside, so the
                # top-loaded nut datum shifts by the same thickness delta.
                parameters["clamp_body_nut_z"]
                - (table_thickness - parameters["table_thickness"]),
                parameters["clamp_body_nut_top_z"]
                - (table_thickness - parameters["table_thickness"]),
                parameters["clamp_pressure_pad_t"],
                parameters["clamp_pressure_pad_retainer_h"],
                parameters["clamp_pressure_pad_retainer_top_clearance_z"],
                parameters["clamp_pressure_pad_retainer_outer_d"],
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
