#!/usr/bin/env python3
"""Render and export the one-piece double-U guard v0.5."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCAD = Path(__file__).with_name("perpendicular_double_u_guard.scad")
REVIEW = ROOT / "hardware/cad/review/perpendicular-u-joint-v0.5"
EXPORTS = ROOT / "hardware/cad/exports/perpendicular-u-joint-v0.5"
OPENSCAD = Path("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD")


def run_openscad(*args: str) -> None:
    cmd = [str(OPENSCAD), *args]
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)


def render(part: str, name: str, camera: str) -> None:
    output = REVIEW / f"{name}.png"
    run_openscad(
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
    run_openscad(
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
        ("assembly_iso", "01-assembly-iso", "0,0,0,55,0,35,0"),
        ("assembly_section", "02-assembly-section", "0,0,0,55,0,35,0"),
        ("clip", "03-one-piece-iso", "0,0,0,55,0,35,0"),
        ("clip_front", "04-front-u", "0,0,0,90,0,0,0"),
        ("clip_top", "05-top-nut-pocket", "0,0,0,0,0,0,0"),
        ("clip_bottom", "06-bottom-opening", "0,0,0,180,0,0,0"),
        ("clip_print_orientation", "07-print-orientation", "0,0,0,55,0,35,0"),
    ]
    for part, name, camera in renders:
        render(part, name, camera)

    export_stl("clip", "perpendicular-double-u-guard-v0.5")
    export_stl("clip_print_orientation", "perpendicular-double-u-guard-print-v0.5")

    print(f"review:  {REVIEW}")
    print(f"exports: {EXPORTS}")


if __name__ == "__main__":
    main()

