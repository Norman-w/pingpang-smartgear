#!/usr/bin/env python3
"""Validate the current integrated net-stand OpenSCAD parameter source."""

from __future__ import annotations

import os
import re
import shutil
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
    "table_clamp",
    "net",
    "net_rail",
    "optical_strip",
    "sensor_mount",
    "calibration_gauge",
)


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


def probe_parameters(openscad: str, output_dir: Path) -> dict[str, float]:
    output = output_dir / "parameter-probe.stl"
    result = run_openscad(openscad, output, 'PART="parameter_probe"')
    require_stl(result, output, "PART=parameter_probe")
    parameters: dict[str, float] = {}
    for key, value in re.findall(r"NETSTAND_PARAM\s+(\w+)=([-+0-9.eE]+)", result.stdout):
        parameters[key] = float(value)
    required = {
        "table_width",
        "net_height",
        "beam_count",
        "beam_first_height",
        "beam_last_height",
        "beam_pitch",
        "post_center_x",
        "net_span",
        "post_top",
        "sensor_x",
    }
    missing = required - parameters.keys()
    if missing:
        raise RuntimeError(f"parameter probe did not emit: {sorted(missing)}\n{result.stdout}")
    if parameters["beam_count"] != 10 or parameters["beam_last_height"] != 100:
        raise RuntimeError(f"unexpected optical grid parameters: {parameters}")
    if not (parameters["post_center_x"] > parameters["table_width"] / 2):
        raise RuntimeError(f"post is not outside table edge: {parameters}")
    if parameters["net_span"] <= parameters["table_width"]:
        raise RuntimeError(f"net span does not bridge the table: {parameters}")
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

        mirrored = output_dir / "optical-strip-mirror.stl"
        require_stl(
            run_openscad(
                openscad,
                mirrored,
                'PART="optical_strip"',
                "SIDE=-1",
            ),
            mirrored,
            "PART=optical_strip SIDE=-1",
        )

        left_center = stl_x_center(output_dir / "left_stand.stl")
        right_center = stl_x_center(output_dir / "right_stand.stl")
        optical_center = stl_x_center(output_dir / "optical_strip.stl")
        optical_mirror_center = stl_x_center(mirrored)
        if not (left_center < 0 < right_center):
            raise RuntimeError(
                f"integrated stand sides are not separated: left={left_center}, right={right_center}"
            )
        if not (optical_center > 0 and optical_mirror_center < 0):
            raise RuntimeError(
                "optical strip SIDE=-1 did not produce the opposite side geometry"
            )

        net_bounds = stl_bounds(output_dir / "net.stl")
        rail_bounds = stl_bounds(output_dir / "net_rail.stl")
        assembly_bounds = stl_bounds(output_dir / "assembly.stl")
        if net_bounds[0] >= 0 or net_bounds[1] <= 0:
            raise RuntimeError(f"net is not centered across the table: {net_bounds}")
        if rail_bounds[0] >= 0 or rail_bounds[1] <= 0:
            raise RuntimeError(f"net rail is not centered across the table: {rail_bounds}")
        if assembly_bounds[2] >= 0 or assembly_bounds[3] <= 0:
            raise RuntimeError(f"assembly does not include the table-depth axis: {assembly_bounds}")
        if assembly_bounds[5] <= parameters["net_height"] + parameters["beam_last_height"]:
            raise RuntimeError(f"uprights do not clear the optical window: {assembly_bounds}")

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

    print(
        "NET_STAND_OK "
        f"(table {parameters['table_width']:g} mm, net {parameters['net_height']:g} mm, "
        f"optical +{parameters['beam_first_height']:g}..+{parameters['beam_last_height']:g} mm, "
        f"{int(parameters['beam_count'])} channels)"
    )


if __name__ == "__main__":
    main()
