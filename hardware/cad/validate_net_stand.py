#!/usr/bin/env python3
"""Validate the current integrated net-stand OpenSCAD parameter source."""

from __future__ import annotations

import re
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
    "table_clamp_body",
    "clamp_pressure_pad",
    "clamp_screw",
    "clamp_knob",
    "net",
    "net_rail",
    "net_rail_segment",
    "net_rail_splice",
    "net_rail_saddle",
    "optical_rail",
    "optical_strip",
    "optical_module_carrier",
    "sensor_mount",
    "pvdf_film",
    "sensor_clamp_lip",
    "reference_carriage",
    "reference_pin",
    "calibration_gauge",
)
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


def require_stl(result: subprocess.CompletedProcess[str], output: Path, label: str) -> None:
    if result.returncode != 0:
        raise RuntimeError(f"OpenSCAD rejected {label}:\n{result.stdout}")
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"OpenSCAD produced no STL for {label}")


def validate_no_drill_thickness(
    openscad: str, output_dir: Path, table_thickness: int
) -> None:
    """Compile the under-table pressure path for a first-pass thickness matrix."""

    definitions = (f"table_thickness={table_thickness}",)
    body = output_dir / f"table-clamp-body-{table_thickness}.stl"
    pad = output_dir / f"pressure-pad-{table_thickness}.stl"
    screw = output_dir / f"clamp-screw-{table_thickness}.stl"
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
    pad_bounds = stl_bounds(pad)
    screw_bounds = stl_bounds(screw)
    tabletop_bottom = -float(table_thickness)
    if not (pad_bounds[5] < tabletop_bottom and screw_bounds[5] < tabletop_bottom):
        raise RuntimeError(
            "no-drill under-table path reaches the tabletop for "
            f"table_thickness={table_thickness}: pad={pad_bounds}, screw={screw_bounds}"
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
        "clamp_screw_top_z",
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
        and parameters["clamp_pressure_pad_bottom_z"] <
        parameters["clamp_pressure_pad_top_z"]
        and parameters["clamp_lower_arm_top_z"] <
        parameters["clamp_pressure_pad_bottom_z"]
    ):
        raise RuntimeError(f"clamp pressure path is not below tabletop: {parameters}")
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
            )

        mirrored_paths: dict[str, Path] = {}
        for part in (
            "post",
            "post_segment",
            "post_joint_sleeve",
            "post_joint_key",
            "table_clamp",
            "table_clamp_body",
            "clamp_pressure_pad",
            "clamp_screw",
            "clamp_knob",
            "net_rail_saddle",
            "optical_rail",
            "optical_strip",
            "optical_module_carrier",
            "sensor_mount",
            "pvdf_film",
            "sensor_clamp_lip",
            "reference_carriage",
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

        net_bounds = stl_bounds(output_dir / "net.stl")
        rail_bounds = stl_bounds(output_dir / "net_rail.stl")
        rail_segment_bounds = stl_bounds(output_dir / "net_rail_segment.stl")
        clamp_body_bounds = stl_bounds(output_dir / "table_clamp_body.stl")
        pressure_pad_bounds = stl_bounds(output_dir / "clamp_pressure_pad.stl")
        screw_bounds = stl_bounds(output_dir / "clamp_screw.stl")
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
            pressure_pad_bounds[5] < -parameters["table_thickness"]
            and screw_bounds[5] < -parameters["table_thickness"]
            and abs(pressure_pad_bounds[5] - parameters["clamp_pressure_pad_top_z"]) < 0.01
            and abs(screw_bounds[5] - parameters["clamp_screw_top_z"]) < 0.01
        ):
            raise RuntimeError(
                "pressure pad or screw reaches the tabletop; no-drill clearance is broken: "
                f"pad={pressure_pad_bounds}, screw={screw_bounds}"
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
