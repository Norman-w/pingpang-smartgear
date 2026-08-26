#!/usr/bin/env python3
"""Render the M6 detector mount in six orthographic views plus an isometric view.

These images are visual audit evidence only.  They intentionally render the
whole assembly without a section cut, while the SCAD parameter assertions and
STL checks remain the source of truth for fit and topology.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_stand.scad"


def find_openscad() -> str:
    candidates = (
        os.environ.get("OPENSCAD", ""),
        shutil.which("openscad") or "",
        "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError(
        "OpenSCAD executable not found; set OPENSCAD to render M6 audit views"
    )


# The detector assembly is centered near x=770, y=0, z=252.5.  Eye points
# are deliberately outside the part so each image has a predictable datum:
# x- is the optical/front side, x+ is the cable/rear side, y- is the table
# front, y+ is the table rear, z+ is the user's top/sky view, and z- is the
# bottom/ground view.
M6_CENTER = (770.0, 0.0, 252.5)
VIEWS = {
    "front-optical-xminus": (300.0, 0.0, 252.5),
    "rear-cable-xplus": (1240.0, 0.0, 252.5),
    "front-table-yminus": (770.0, -520.0, 252.5),
    "rear-table-yplus": (770.0, 520.0, 252.5),
    "top-zplus": (770.0, 0.0, 820.0),
    "bottom-zminus": (770.0, 0.0, -320.0),
    "isometric": (1120.0, -980.0, 900.0),
}


def camera_arg(eye: tuple[float, float, float]) -> str:
    return "{} ,{} ,{} ,{} ,{} ,{}".format(
        eye[0],
        eye[1],
        eye[2],
        M6_CENTER[0],
        M6_CENTER[1],
        M6_CENTER[2],
    ).replace(" ", "")


def render(
    openscad: str,
    part: str,
    side: int,
    name: str,
    output_dir: Path,
    width: int,
    height: int,
) -> Path:
    output = output_dir / f"m6-{part}-{name}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    openscad_command = [
        openscad,
        "-o",
        str(output),
        "-D",
        f'PART="{part}"',
        "-D",
        f"SIDE={side}",
        "-D",
        "m6_show_optical_direction=true",
        "--render",
        "--viewall",
        "--projection=ortho",
        "--camera=" + camera_arg(VIEWS[name]),
        "--imgsize",
        f"{width},{height}",
        "--colorscheme=Tomorrow",
        str(SOURCE),
    ]
    command = openscad_command
    if not os.environ.get("DISPLAY") and shutil.which("xvfb-run"):
        command = [
            "xvfb-run",
            "-a",
            "--server-args=-screen 0 1920x1200x24",
            *openscad_command,
        ]
    print("$", " ".join(command))
    subprocess.run(command, check=True)
    if not output.is_file() or output.stat().st_size < 1_024:
        raise RuntimeError(f"OpenSCAD produced no usable PNG for {part}/{name}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE / "rendered" / "m6-audit",
        help="directory receiving generated PNG evidence",
    )
    parser.add_argument(
        "--part",
        choices=("m6_detector_mount", "m6_detector_exploded"),
        default="m6_detector_mount",
        help="whole assembly or whole, uncut exploded assembly",
    )
    parser.add_argument("--side", type=int, choices=(-1, 1), default=1)
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=1000)
    args = parser.parse_args()

    openscad = find_openscad()
    outputs = [
        render(
            openscad,
            args.part,
            args.side,
            name,
            args.output_dir,
            args.width,
            args.height,
        )
        for name in VIEWS
    ]
    print(f"M6_VIEWS_OK ({len(outputs)} views, {args.part}, {args.output_dir})")


if __name__ == "__main__":
    main()
