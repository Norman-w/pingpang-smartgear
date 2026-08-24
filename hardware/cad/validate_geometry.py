#!/usr/bin/env python3
"""Validate motion and geometry invariants from the OpenSCAD parameter source.

The script deliberately reads a parameter manifest emitted by OpenSCAD instead
of maintaining a second hand-copied parameter table in Python.
"""

from __future__ import annotations

import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_post_x_clamp.scad"
MARKER = "SMARTGEAR_PARAM "


def find_openscad() -> str:
    candidates = [
        os.environ.get("OPENSCAD", ""),
        shutil.which("openscad") or "",
        "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("OpenSCAD executable not found; set OPENSCAD to run CAD validation")


def read_parameters(openscad: str) -> dict[str, float]:
    with tempfile.TemporaryDirectory(prefix="pingpang-smartgear-geometry-") as directory:
        output = Path(directory) / "parameter-probe.stl"
        result = subprocess.run(
            [
                openscad,
                "-o",
                str(output),
                "-D",
                'PART="parameter_probe"',
                str(SOURCE),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    payload = next(
        (line.split(MARKER, 1)[1].rstrip('"') for line in result.stdout.splitlines() if MARKER in line),
        None,
    )
    if payload is None:
        raise RuntimeError("OpenSCAD parameter probe did not emit SMARTGEAR_PARAM")

    parameters: dict[str, float] = {}
    for item in payload.split(";"):
        name, separator, value = item.partition("=")
        if not separator:
            raise RuntimeError(f"malformed CAD parameter item: {item!r}")
        parameters[name] = float(value)
    return parameters


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def point(radius: float, angle_deg: float, sign: int, inner: bool) -> tuple[float, float]:
    angle = math.radians(angle_deg)
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    if inner:
        return (x, -sign * y)
    return (-x, sign * y)


def cross(first: tuple[float, float], second: tuple[float, float]) -> float:
    return first[0] * second[1] - first[1] * second[0]


def distance(first: tuple[float, float], second: tuple[float, float]) -> float:
    return math.hypot(second[0] - first[0], second[1] - first[1])


def validate(parameters: dict[str, float]) -> str:
    required = {
        "post_nominal_d",
        "jaw_clearance",
        "jaw_length",
        "jaw_mount_overlap",
        "v_angle",
        "arm_length_outer",
        "arm_length_inner",
        "arm_outer_y",
        "arm_inner_y",
        "clamp_angle_deg",
        "clamp_angle_min_deg",
        "clamp_angle_max_deg",
        "arm_width",
        "arm_height",
        "arm_layer_thickness",
        "arm_layer_gap",
        "arm_gusset_length",
        "arm_gusset_base",
        "pivot_d",
        "pivot_clearance",
        "roller_d",
        "roller_cap_tab_t",
        "roller_cap_tab_h",
        "screw_d",
        "screw_pitch",
        "screw_span",
        "bridge_h",
        "rod_len",
        "beam_count",
        "beam_first_height",
        "beam_pitch",
        "beam_last_height",
        "reference_height",
        "reference_line_d",
        "reference_line_clearance",
        "optical_module_depth",
        "optical_module_width",
        "optical_module_height",
        "optical_lens_d",
        "optical_lens_depth",
        "optical_bank_clearance",
        "reference_pin_length",
        "nut_capture_outer_d",
        "nut_capture_width",
        "nut_capture_pocket_d",
        "nut_capture_pocket_depth",
        "nut_bore_clearance",
        "guide_width",
    }
    require(required <= parameters.keys(), "CAD parameter manifest is incomplete")

    post_x = parameters["arm_length_inner"] + 5.0
    outer_radius = math.hypot(parameters["arm_length_outer"], parameters["arm_outer_y"])
    inner_radius = math.hypot(parameters["arm_length_inner"], parameters["arm_inner_y"])
    min_angle = parameters["clamp_angle_min_deg"]
    max_angle = parameters["clamp_angle_max_deg"]
    selected_angle = parameters["clamp_angle_deg"]

    require(parameters["v_angle"] == 90, "inner V jaw must remain 90 degrees")
    require(0 < parameters["jaw_mount_overlap"] < parameters["jaw_length"] / 2,
            "V jaw must overlap its arm endpoint without spanning the full jaw")
    require(parameters["pivot_d"] == 8, "pivot shaft must remain 8 mm")
    require(parameters["screw_d"] == 8, "adjustment screw must remain M8")
    require(math.isclose(parameters["screw_pitch"], 1.25, abs_tol=1e-6),
            "adjustment screw must remain M8 x 1.25")
    require(
        0 < parameters["roller_cap_tab_t"] < parameters["roller_d"]
        and parameters["roller_cap_tab_h"] > parameters["arm_layer_thickness"],
        "roller cap retention tabs must overlap the U-cheeks",
    )
    require(
        parameters["nut_capture_outer_d"] > parameters["nut_capture_pocket_d"]
        > parameters["screw_d"]
        and parameters["nut_capture_width"]
        > parameters["nut_capture_pocket_depth"]
        and parameters["nut_bore_clearance"] > 0,
        "M8 nut capture must leave a pocket wall and screw clearance",
    )
    require(0 < min_angle <= selected_angle <= max_angle < 30,
            "selected clamp angle must stay inside a stable motion range")
    require(parameters["pivot_d"] < parameters["pivot_d"] + 2 * parameters["pivot_clearance"] < parameters["arm_width"],
            "pivot bore clearance must fit inside the printed arm")
    require(
        math.isclose(
            2 * parameters["arm_layer_thickness"] + parameters["arm_layer_gap"],
            parameters["arm_height"],
            abs_tol=1e-6,
        ),
        "scissor arm layers must fit the 16 mm stack envelope",
    )
    require(
        parameters["arm_layer_thickness"] > 0
        and parameters["arm_layer_gap"] > 0,
        "scissor arm layers must have positive thickness and separation",
    )
    require(
        0 < parameters["arm_gusset_length"] < parameters["arm_length_inner"]
        and parameters["arm_gusset_base"] > parameters["arm_width"],
        "triangular arm gussets must widen the pivot transition within the inner span",
    )
    require(parameters["beam_count"] == 10, "height grid must contain 10 beams")
    expected_last = parameters["beam_first_height"] + (
        parameters["beam_count"] - 1
    ) * parameters["beam_pitch"]
    require(math.isclose(expected_last, parameters["beam_last_height"], abs_tol=1e-6),
            "beam height sequence is inconsistent")
    detent_index = (
        parameters["reference_height"] - parameters["beam_first_height"]
    ) / parameters["beam_pitch"]
    require(math.isclose(detent_index, round(detent_index), abs_tol=1e-6),
            "reference line must land on a beam detent")
    require(
        parameters["reference_line_d"] > 0
        and parameters["reference_line_clearance"] >= 0
        and parameters["reference_line_d"] + parameters["reference_line_clearance"]
        < parameters["bridge_h"],
        "reference line bore must fit inside the carriage body",
    )
    require(parameters["rod_len"] >= parameters["beam_last_height"],
            "extension rod is shorter than the optical grid")
    require(
        parameters["optical_module_depth"] > 0
        and parameters["optical_module_width"] > 0
        and parameters["optical_module_height"] > 0
        and parameters["optical_lens_d"] > 0
        and parameters["optical_lens_depth"] > 0,
        "optical module placeholder dimensions must be positive",
    )
    require(
        parameters["optical_module_height"] < parameters["beam_pitch"],
        "optical module placeholder must fit between beam heights",
    )
    reference_carriage_half_y = (parameters["guide_width"] + 6.0) / 2.0
    optical_bank_y = (
        parameters["guide_width"] / 2.0
        + parameters["optical_module_width"] / 2.0
        + parameters["optical_bank_clearance"]
    )
    require(parameters["optical_bank_clearance"] > 0,
            "optical bank must have a positive side clearance")
    require(
        optical_bank_y - parameters["optical_module_width"] / 2.0
        > reference_carriage_half_y,
        "optical bank envelope overlaps the reference carriage",
    )
    require(
        parameters["reference_pin_length"]
        > parameters["guide_width"] / 2.0 + reference_carriage_half_y,
        "reference pin must pass through the carriage and guide",
    )

    for angle in (min_angle, selected_angle, max_angle):
        upper_outer = point(outer_radius, angle, 1, inner=False)
        upper_inner = point(inner_radius, angle, 1, inner=True)
        lower_outer = point(outer_radius, angle, -1, inner=False)
        lower_inner = point(inner_radius, angle, -1, inner=True)
        require(abs(cross(upper_outer, upper_inner)) < 0.01,
                "upper arm endpoints are not collinear with the pivot")
        require(abs(cross(lower_outer, lower_inner)) < 0.01,
                "lower arm endpoints are not collinear with the pivot")
        require(
            distance(upper_inner, (post_x, 0.0)) + parameters["jaw_clearance"]
            < parameters["jaw_length"],
            f"upper V jaw cannot reach the post with clearance at {angle:g} degrees",
        )
        require(
            distance(lower_inner, (post_x, 0.0)) + parameters["jaw_clearance"]
            < parameters["jaw_length"],
            f"lower V jaw cannot reach the post with clearance at {angle:g} degrees",
        )

    max_outer_y = outer_radius * math.sin(math.radians(max_angle))
    require(parameters["screw_span"] / 2 >= max_outer_y + parameters["roller_d"] / 2,
            "M8 screw span does not cover the complete motion range")

    selected_outer_y = outer_radius * math.sin(math.radians(selected_angle))
    return (
        f"GEOMETRY_OK (angle {min_angle:g}..{max_angle:g} deg, "
        f"post Ø{parameters['post_nominal_d']:g}, "
        f"arm layers {parameters['arm_layer_thickness']:g}+"
        f"{parameters['arm_layer_gap']:g}+{parameters['arm_layer_thickness']:g} mm, "
        f"outer roller separation {2 * selected_outer_y:.2f} mm)"
    )


def main() -> None:
    result = validate(read_parameters(find_openscad()))
    print(result)


if __name__ == "__main__":
    main()
