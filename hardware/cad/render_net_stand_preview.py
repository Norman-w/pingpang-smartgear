#!/usr/bin/env python3
"""Render visual evidence for the current integrated net stand."""

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
        "OpenSCAD executable not found; set OPENSCAD to render integrated net-stand previews"
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
    render(openscad, "assembly", args.output_dir / "net-stand-assembly.png", 1800, 1000)
    render(openscad, "left_stand", args.output_dir / "net-stand-left.png", 1200, 1000)
    render(openscad, "right_stand", args.output_dir / "net-stand-right.png", 1200, 1000)
    render(
        openscad,
        "post_segment",
        args.output_dir / "net-stand-post-segment-lower.png",
        700,
        1200,
        definitions=("post_segment_index=0",),
    )
    render(
        openscad,
        "post_segment",
        args.output_dir / "net-stand-post-segment-upper.png",
        700,
        1200,
        definitions=("post_segment_index=1",),
    )
    render(
        openscad,
        "lower_stand_segment",
        args.output_dir / "net-stand-lower-stand-segment.png",
        1200,
        1000,
    )
    render(
        openscad,
        "post_joint_sleeve",
        args.output_dir / "net-stand-post-joint-sleeve.png",
        700,
        700,
    )
    render(
        openscad,
        "post_joint_key",
        args.output_dir / "net-stand-post-joint-key.png",
        700,
        700,
    )
    render(openscad, "table_clamp", args.output_dir / "net-stand-table-clamp.png", 1200, 900)
    render(
        openscad,
        "table_clamp_section",
        args.output_dir / "net-stand-table-clamp-section.png",
        1200,
        1200,
    )
    render(
        openscad,
        "table_clamp_body",
        args.output_dir / "net-stand-table-clamp-body.png",
        1200,
        900,
    )
    render(
        openscad,
        "clamp_top_pad",
        args.output_dir / "net-stand-clamp-top-pad.png",
        900,
        700,
    )
    render(
        openscad,
        "clamp_pressure_pad",
        args.output_dir / "net-stand-clamp-pressure-pad.png",
        900,
        700,
    )
    render(
        openscad,
        "clamp_screw",
        args.output_dir / "net-stand-clamp-screw.png",
        700,
        1000,
    )
    render(
        openscad,
        "clamp_body_nut",
        args.output_dir / "net-stand-clamp-body-nut.png",
        600,
        600,
    )
    render(openscad, "clamp_knob", args.output_dir / "net-stand-clamp-knob.png", 900, 700)
    render(
        openscad,
        "clamp_knob_nut",
        args.output_dir / "net-stand-clamp-knob-nut.png",
        600,
        600,
    )
    render(openscad, "optical_rail", args.output_dir / "net-stand-optical-rail.png", 900, 1200)
    render(openscad, "optical_strip", args.output_dir / "net-stand-optical-strip.png", 1000, 1200)
    render(
        openscad,
        "optical_strip",
        args.output_dir / "net-stand-optical-strip-mirror.png",
        1000,
        1200,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "optical_module_carrier",
        args.output_dir / "net-stand-optical-module-carrier.png",
        900,
        700,
        definitions=("optical_module_index=4",),
    )
    render(openscad, "sensor_mount", args.output_dir / "net-stand-sensor-mount.png", 1000, 800)
    render(openscad, "pvdf_film", args.output_dir / "net-stand-pvdf-film.png", 800, 600)
    render(
        openscad,
        "sensor_clamp_lip",
        args.output_dir / "net-stand-pvdf-clamp-lip.png",
        800,
        600,
    )
    render(
        openscad,
        "reference_carriage",
        args.output_dir / "net-stand-reference-carriage.png",
        1000,
        800,
    )
    render(
        openscad,
        "net_rail_segment",
        args.output_dir / "net-stand-net-rail-segment.png",
        1200,
        500,
        definitions=("rail_segment_index=1",),
    )
    render(
        openscad,
        "net_rail_splice",
        args.output_dir / "net-stand-net-rail-splice.png",
        900,
        600,
        definitions=("rail_splice_index=0",),
    )
    render(
        openscad,
        "net_rail_saddle",
        args.output_dir / "net-stand-net-rail-saddle.png",
        900,
        700,
    )
    render(openscad, "calibration_gauge", args.output_dir / "net-stand-calibration-gauge.png", 900, 1000)
    print(f"NET_STAND_PREVIEWS_OK ({args.output_dir})")


if __name__ == "__main__":
    main()
