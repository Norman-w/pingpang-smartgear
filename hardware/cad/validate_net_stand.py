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
    "post_joint_sleeve",
    "post_joint_key",
    "table_clamp",
    "table_clamp_section",
    "table_clamp_body",
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
    details = (
        f"triangles={len(triangles)}, degenerate={degenerate}, boundary={boundary}, "
        f"non_manifold={non_manifold}, inconsistent_orientation={inconsistent}"
    )
    return ok, details


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


def validate_no_drill_thickness(
    openscad: str, output_dir: Path, table_thickness: int
) -> None:
    """Compile the under-table pressure path for a first-pass thickness matrix."""

    definitions = (f"table_thickness={table_thickness}",)
    body = output_dir / f"table-clamp-body-{table_thickness}.stl"
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
    pad_bounds = stl_bounds(pad)
    screw_bounds = stl_bounds(screw)
    body_nut_bounds = stl_bounds(body_nut)
    knob_bounds = stl_bounds(knob)
    knob_nut_bounds = stl_bounds(knob_nut)
    tabletop_bottom = -float(table_thickness)
    if not (
        pad_bounds[5] < tabletop_bottom
        and screw_bounds[5] < tabletop_bottom
        and screw_bounds[5] <= pad_bounds[4] + 0.01
        and body_nut_bounds[5] < tabletop_bottom
        and knob_bounds[5] < tabletop_bottom
        and knob_nut_bounds[5] < tabletop_bottom
        and knob_nut_bounds[4] >= knob_bounds[4] - 0.01
        and knob_nut_bounds[5] <= knob_bounds[5] + 0.01
    ):
        raise RuntimeError(
            "no-drill under-table path reaches the tabletop for "
            f"table_thickness={table_thickness}: pad={pad_bounds}, screw={screw_bounds}, "
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
        "net_height",
        "net_rail_height",
        "net_rail_depth",
        "beam_count",
        "beam_first_height",
        "beam_last_height",
        "beam_pitch",
        "post_center_x",
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
        "clamp_screw_x",
        "clamp_screw_d",
        "clamp_threaded_boss_d",
        "clamp_threaded_boss_h",
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
        "clamp_body_nut_z",
        "clamp_knob_top_z",
        "clamp_knob_bottom_z",
        "clamp_knob_nut_z",
        "clamp_lower_arm_bottom_z",
        "clamp_lower_arm_top_z",
        "clamp_pressure_pad_top_z",
        "clamp_pressure_pad_bottom_z",
        "optical_locating_hole_d",
        "optical_rail_width",
        "optical_module_depth",
        "optical_module_width",
        "optical_module_height",
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
        "reference_pin_d",
    }
    missing = required - parameters.keys()
    if missing:
        raise RuntimeError(f"parameter probe did not emit: {sorted(missing)}\n{result.stdout}")
    if parameters["beam_count"] != 10 or parameters["beam_last_height"] != 100:
        raise RuntimeError(f"unexpected optical grid parameters: {parameters}")
    if not (parameters["post_center_x"] > parameters["table_width"] / 2):
        raise RuntimeError(f"post is not outside table edge: {parameters}")
    if not (
        parameters["post_segment_count"] == 2
        and 100 < parameters["post_segment_length"] < 180
        and parameters["post_joint_gap"] == 2
    ):
        raise RuntimeError(f"unexpected printable post segmentation: {parameters}")
    table_edge = parameters["table_width"] / 2
    if not (
        parameters["clamp_pad_x"] < table_edge < parameters["clamp_pad_outer_x"]
        and parameters["clamp_pad_x"] < parameters["clamp_screw_x"] < table_edge
    ):
        raise RuntimeError(f"clamp does not bridge edge with an under-table screw: {parameters}")
    if not (
        parameters["clamp_screw_top_z"] < -parameters["table_thickness"]
        and parameters["clamp_pressure_pad_top_z"] < -parameters["table_thickness"]
        and parameters["clamp_screw_top_z"] <= parameters["clamp_pressure_pad_bottom_z"]
        and parameters["clamp_screw_bottom_z"] < parameters["clamp_knob_top_z"]
        and parameters["clamp_knob_bottom_z"] < parameters["clamp_knob_top_z"]
        and parameters["clamp_pressure_pad_bottom_z"] <
        parameters["clamp_pressure_pad_top_z"]
        and parameters["clamp_lower_arm_top_z"] <
        parameters["clamp_pressure_pad_bottom_z"]
    ):
        raise RuntimeError(f"clamp pressure path is not below tabletop: {parameters}")
    if not (
        parameters["clamp_nut_af"] > parameters["clamp_screw_d"]
        and parameters["clamp_nut_pocket_af"] > parameters["clamp_nut_af"]
        and parameters["clamp_nut_pocket_af"] / math.cos(math.radians(30)) + 2
        < parameters["clamp_threaded_boss_d"]
        and parameters["clamp_nut_pocket_depth"] >= parameters["clamp_nut_h"]
        and parameters["clamp_nut_pocket_depth"] < parameters["clamp_threaded_boss_h"]
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
    if not (0 < parameters["reference_pin_d"] < parameters["optical_locating_hole_d"]):
        raise RuntimeError(f"reference pin cannot fit the locating hole: {parameters}")
    if not (
        parameters["sensor_film_length"] > parameters["sensor_clamp_tab_width"] > 0
        and parameters["sensor_film_depth"] > 0
    ):
        raise RuntimeError(f"invalid removable PVDF film clamp dimensions: {parameters}")
    return parameters


def main() -> None:
    openscad = find_openscad()
    with tempfile.TemporaryDirectory(prefix="pingpang-smartgear-net-stand-") as directory:
        output_dir = Path(directory)
        parameters = probe_parameters(openscad, output_dir)

        for part in PARTS:
            output = output_dir / f"{part}.stl"
            require_stl(
                run_openscad(openscad, output, f'PART="{part}"'),
                output,
                f"PART={part}",
                require_closed=part not in PREVIEW_ONLY_PARTS,
            )

        mirrored_paths: dict[str, Path] = {}
        for part in (
            "post",
            "post_segment",
            "post_joint_sleeve",
            "post_joint_key",
            "table_clamp",
            "table_clamp_section",
            "table_clamp_body",
            "clamp_pressure_pad",
            "clamp_screw",
            "clamp_body_nut",
            "clamp_knob",
            "clamp_knob_nut",
            "net_rail_saddle",
            "optical_rail",
            "optical_strip",
            "optical_module_carrier",
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
        pressure_pad_bounds = stl_bounds(output_dir / "clamp_pressure_pad.stl")
        screw_bounds = stl_bounds(output_dir / "clamp_screw.stl")
        body_nut_bounds = stl_bounds(output_dir / "clamp_body_nut.stl")
        knob_bounds = stl_bounds(output_dir / "clamp_knob.stl")
        knob_nut_bounds = stl_bounds(output_dir / "clamp_knob_nut.stl")
        sensor_bounds = stl_bounds(output_dir / "sensor_mount.stl")
        film_bounds = stl_bounds(output_dir / "pvdf_film.stl")
        film_lip_bounds = stl_bounds(output_dir / "sensor_clamp_lip.stl")
        reference_bounds = stl_bounds(output_dir / "reference_carriage.stl")
        saddle_bounds = stl_bounds(output_dir / "net_rail_saddle.stl")
        optical_rail_bounds = stl_bounds(output_dir / "optical_rail.stl")
        carrier_bounds = stl_bounds(output_dir / "optical_module_carrier.stl")
        assembly_bounds = stl_bounds(output_dir / "assembly.stl")
        post_bounds = stl_bounds(output_dir / "post.stl")
        post_segment_bounds = stl_bounds(output_dir / "post_segment.stl")
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
        if not (
            clamp_body_bounds[0] < parameters["table_width"] / 2 < clamp_body_bounds[1]
            and clamp_body_bounds[1] > parameters["clamp_pad_outer_x"] - 0.01
        ):
            raise RuntimeError(f"fixed clamp body does not bridge the table edge: {clamp_body_bounds}")
        if not (
            clamp_section_bounds[0] < parameters["table_width"] / 2 < clamp_section_bounds[1]
            and clamp_section_bounds[1] > parameters["clamp_pad_outer_x"] - 0.01
            and clamp_section_bounds[2] < 0 < clamp_section_bounds[3]
            and clamp_section_bounds[4] <= parameters["clamp_knob_bottom_z"] + 0.01
            and clamp_section_bounds[5] > 0
            and clamp_section_bounds[3] - clamp_section_bounds[2] <= 8.01
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
            and post_segment_bounds[5] - post_segment_bounds[4] < 180
            and post_segment_bounds[1] - post_segment_bounds[0] > parameters["post_body_width"]
            and post_segment_bounds[3] - post_segment_bounds[2] > parameters["post_body_depth"]
        ):
            raise RuntimeError(
                f"post assembly/segment bounds or lower reinforcement are not printable: post={post_bounds}, "
                f"segment={post_segment_bounds}"
            )

        for table_thickness in NO_DRILL_TABLE_THICKNESSES:
            validate_no_drill_thickness(openscad, output_dir, table_thickness)

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
        f"optical +{parameters['beam_first_height']:g}..+{parameters['beam_last_height']:g} mm, "
        f"{int(parameters['beam_count'])} channels, no-drill table thickness "
        f"{','.join(str(value) for value in NO_DRILL_TABLE_THICKNESSES)} mm)"
    )


if __name__ == "__main__":
    main()
