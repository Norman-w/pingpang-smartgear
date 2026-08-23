#!/usr/bin/env python3
"""Compile every OpenSCAD PART and both mirror directions to temporary STL files."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_post_x_clamp.scad"
PARTS = (
    "assembly",
    "left_clamp",
    "right_clamp",
    "arm",
    "roller",
    "knob",
    "rod",
    "guide",
    "calibration_gauge",
)


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
    print(f"SCAD_OK ({len(PARTS)} parts + SIDE=-1)")


if __name__ == "__main__":
    main()
