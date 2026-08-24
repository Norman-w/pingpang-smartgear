#!/usr/bin/env python3
"""Compile every OpenSCAD PART and both mirror directions to temporary STL files."""

from __future__ import annotations

import os
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

from validate_geometry import read_parameters, validate

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_post_x_clamp.scad"
PARTS = (
    "assembly",
    "left_clamp",
    "right_clamp",
    "arm",
    "jaw",
    "jaw_pad",
    "roller",
    "roller_mount",
    "roller_cap",
    "knob",
    "screw_rod",
    "rod",
    "bridge",
    "guide",
    "reference_carriage",
    "reference_carriage_body",
    "reference_pin",
    "optical_bank",
    "calibration_gauge",
)


def stl_x_center(path: Path) -> float:
    """Return the X center of an ASCII or binary STL bounding box."""

    data = path.read_bytes()
    vertices: list[float] = []
    if len(data) >= 84:
        triangle_count = struct.unpack_from("<I", data, 80)[0]
        expected_size = 84 + triangle_count * 50
        if expected_size == len(data):
            for triangle in range(triangle_count):
                base = 84 + triangle * 50 + 12
                for vertex in range(3):
                    vertices.append(struct.unpack_from("<f", data, base + vertex * 12)[0])
    if not vertices:
        text = data.decode("ascii", errors="ignore")
        vertices = [
            float(match.group(1))
            for match in re.finditer(
                r"\bvertex\s+([-+0-9.eE]+)\s+[-+0-9.eE]+\s+[-+0-9.eE]+",
                text,
            )
        ]
    if not vertices:
        raise RuntimeError(f"cannot read STL vertices from {path}")
    return (min(vertices) + max(vertices)) / 2.0


def stl_bounds(path: Path) -> tuple[float, float, float, float, float, float]:
    """Return min/max X, Y and Z for an STL export."""

    data = path.read_bytes()
    vertices: list[tuple[float, float, float]] = []
    if len(data) >= 84:
        triangle_count = struct.unpack_from("<I", data, 80)[0]
        expected_size = 84 + triangle_count * 50
        if expected_size == len(data):
            for triangle in range(triangle_count):
                base = 84 + triangle * 50 + 12
                for vertex in range(3):
                    vertices.append(
                        struct.unpack_from("<fff", data, base + vertex * 12)
                    )
    if not vertices:
        text = data.decode("ascii", errors="ignore")
        vertices = [
            (float(match.group(1)), float(match.group(2)), float(match.group(3)))
            for match in re.finditer(
                r"\bvertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)",
                text,
            )
        ]
    if not vertices:
        raise RuntimeError(f"cannot read STL vertices from {path}")
    xs, ys, zs = zip(*vertices)
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


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


def main() -> None:
    openscad = find_openscad()
    with tempfile.TemporaryDirectory(prefix="pingpang-smartgear-scad-") as directory:
        output_dir = Path(directory)
        for part in PARTS:
            output = output_dir / f"{part}.stl"
            subprocess.run(
                [openscad, "-o", str(output), "-D", f'PART="{part}"', str(SOURCE)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError(f"OpenSCAD produced no STL for PART={part}")

        output = output_dir / "right-side.stl"
        subprocess.run(
            [
                openscad,
                "-o",
                str(output),
                "-D",
                'PART="right_clamp"',
                "-D",
                "SIDE=-1",
                str(SOURCE),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("OpenSCAD produced no STL for SIDE=-1")

        output = output_dir / "optical-bank-mirror.stl"
        subprocess.run(
            [
                openscad,
                "-o",
                str(output),
                "-D",
                'PART="optical_bank"',
                "-D",
                "SIDE=-1",
                str(SOURCE),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("OpenSCAD produced no STL for mirrored optical bank")

        output = output_dir / "left-side-explicit.stl"
        subprocess.run(
            [
                openscad,
                "-o",
                str(output),
                "-D",
                'PART="right_clamp"',
                "-D",
                "SIDE=1",
                str(SOURCE),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("OpenSCAD produced no STL for SIDE=1 override")

        left_default_center = stl_x_center(output_dir / "left_clamp.stl")
        right_default_center = stl_x_center(output_dir / "right_clamp.stl")
        left_override_center = stl_x_center(output_dir / "left-side-explicit.stl")
        optical_default_center = stl_x_center(output_dir / "optical_bank.stl")
        optical_mirror_center = stl_x_center(output_dir / "optical-bank-mirror.stl")
        if (
            left_default_center * right_default_center >= 0
            or left_override_center * right_default_center >= 0
            or optical_default_center * optical_mirror_center >= 0
        ):
            raise RuntimeError(
                "SIDE override did not produce opposite left/right or optical STL geometry"
            )

        carriage_bounds = stl_bounds(output_dir / "reference_carriage.stl")
        optical_bounds = stl_bounds(output_dir / "optical_bank.stl")
        if carriage_bounds[3] >= optical_bounds[2]:
            raise RuntimeError(
                "reference carriage and optical bank envelopes overlap in Y"
            )

        for angle in (10, 20):
            output = output_dir / f"left-angle-{angle}.stl"
            subprocess.run(
                [
                    openscad,
                    "-o",
                    str(output),
                    "-D",
                    'PART="left_clamp"',
                    "-D",
                    f"clamp_angle_deg={angle}",
                    str(SOURCE),
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError(f"OpenSCAD produced no STL for clamp angle {angle}")

        invalid = subprocess.run(
            [
                openscad,
                "-o",
                str(output_dir / "invalid-angle.stl"),
                "-D",
                'PART="left_clamp"',
                "-D",
                "clamp_angle_deg=25",
                str(SOURCE),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if invalid.returncode == 0:
            raise RuntimeError("OpenSCAD accepted an out-of-range clamp angle")

        invalid_layer = subprocess.run(
            [
                openscad,
                "-o",
                str(output_dir / "invalid-layer.stl"),
                "-D",
                'PART="left_clamp"',
                "-D",
                "arm_layer_gap=0",
                str(SOURCE),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if invalid_layer.returncode == 0:
            raise RuntimeError("OpenSCAD accepted intersecting scissor arm layers")
    geometry_result = validate(read_parameters(openscad))
    print(
        f"SCAD_OK ({len(PARTS)} exports + SIDE=±1 mirror geometry + motion 10/20 deg; "
        f"{geometry_result})"
    )


if __name__ == "__main__":
    main()
