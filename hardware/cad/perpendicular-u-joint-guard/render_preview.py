#!/usr/bin/env python3
"""Render and export the v0.2 perpendicular 20x20 U-joint guard."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCAD = Path(__file__).with_name("perpendicular_u_joint_guard.scad")
REVIEW = ROOT / "hardware/cad/review/perpendicular-u-joint-v0.2"
EXPORTS = ROOT / "hardware/cad/exports/perpendicular-u-joint-v0.2"
OPENSCAD = Path("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD")


def run_openSCAD(*args: str) -> None:
    cmd = [str(OPENSCAD), *args]
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)


def render(part: str, name: str, camera: str) -> None:
    output = REVIEW / f"{name}.png"
    run_openSCAD(
        "--render",
        "--viewall",
        "--projection=ortho",
        f"--camera={camera}",
        "--imgsize=1500,1100",
        "--colorscheme=Tomorrow",
        f"-D PART=\"{part}\"",
        "-o",
        str(output),
        str(SCAD),
    )


def export_stl(part: str, name: str) -> None:
    output = EXPORTS / f"{name}.stl"
    run_openSCAD(
        "--export-format",
        "binstl",
        f"-D PART=\"{part}\"",
        "-o",
        str(output),
        str(SCAD),
    )


def main() -> None:
    if not OPENSCAD.exists():
        raise SystemExit(f"OpenSCAD not found: {OPENSCAD}")

    REVIEW.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)

    renders = [
        ("joint_assembly", "01-joint-assembly-iso", "0,0,0,55,0,35,0"),
        ("joint_exploded", "02-joint-exploded-iso", "0,0,0,55,0,35,0"),
        ("joint_section", "03-joint-section-iso", "0,0,0,55,0,35,0"),
        ("print_layout", "04-print-layout", "0,0,0,0,0,0,0"),
        ("front_u", "05-front-u-detail", "0,0,0,90,0,0,0"),
        ("back_u", "06-back-u-detail", "0,0,0,-90,0,0,0"),
    ]
    for part, name, camera in renders:
        render(part, name, camera)

    exports = [
        ("front_u", "perpendicular-u-front-v0.2"),
        ("back_u", "perpendicular-u-back-v0.2"),
        ("front_u_print", "perpendicular-u-front-print-v0.2"),
        ("back_u_print", "perpendicular-u-back-print-v0.2"),
    ]
    for part, name in exports:
        export_stl(part, name)

    print(f"review:  {REVIEW}")
    print(f"exports: {EXPORTS}")
    print("stl inspector:", shutil.which("python3"))


if __name__ == "__main__":
    main()

