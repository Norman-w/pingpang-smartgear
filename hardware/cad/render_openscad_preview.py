#!/usr/bin/env python3
"""Render visual evidence directly from the OpenSCAD parameter source."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_post_x_clamp.scad"


def find_openscad() -> str:
    candidates = [
        os.environ.get("OPENSCAD", ""),
        shutil.which("openscad") or "",
        "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError(
        "OpenSCAD executable not found; set OPENSCAD to render CAD previews"
    )


def render(
    openscad: str,
    part: str,
    output: Path,
    width: int,
    height: int,
    definitions: tuple[str, ...] = (),
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    openscad_command = [
        openscad,
        "-o",
        str(output),
        "-D",
        f'PART="{part}"',
        "--render",
        "--viewall",
        "--projection=ortho",
        "--imgsize",
        f"{width},{height}",
        "--colorscheme=Tomorrow",
    ]
    for definition in definitions:
        openscad_command.extend(["-D", definition])
    openscad_command.append(str(SOURCE))
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
        raise RuntimeError(f"OpenSCAD produced no usable PNG for PART={part}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE / "rendered",
        help="directory receiving generated PNG evidence",
    )
    args = parser.parse_args()

    openscad = find_openscad()
    render(
        openscad,
        "assembly",
        args.output_dir / "openscad-assembly.png",
        1600,
        1000,
    )
    render(
        openscad,
        "left_clamp",
        args.output_dir / "openscad-left-clamp.png",
        1200,
        1000,
    )
    render(
        openscad,
        "jaw",
        args.output_dir / "openscad-jaw.png",
        1200,
        800,
    )
    render(
        openscad,
        "jaw_pad",
        args.output_dir / "openscad-jaw-pad.png",
        1200,
        800,
    )
    render(
        openscad,
        "roller_mount",
        args.output_dir / "openscad-roller-mount.png",
        1200,
        900,
    )
    render(
        openscad,
        "roller_cap",
        args.output_dir / "openscad-roller-cap.png",
        1000,
        800,
    )
    render(
        openscad,
        "optical_bank",
        args.output_dir / "openscad-optical-bank.png",
        1200,
        1000,
    )
    render(
        openscad,
        "optical_bank",
        args.output_dir / "openscad-optical-bank-mirror.png",
        1200,
        1000,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "reference_carriage",
        args.output_dir / "openscad-reference-carriage.png",
        1000,
        800,
    )
    render(
        openscad,
        "reference_carriage_body",
        args.output_dir / "openscad-reference-carriage-body.png",
        1000,
        800,
    )
    render(
        openscad,
        "calibration_gauge",
        args.output_dir / "openscad-calibration-gauge.png",
        1000,
        800,
    )
    print(f"OPENSCAD_PREVIEWS_OK ({args.output_dir})")


if __name__ == "__main__":
    main()
