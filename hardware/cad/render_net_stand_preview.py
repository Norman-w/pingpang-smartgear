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
OBSOLETE_OUTPUT_NAMES = (
    "net-stand-lower-stand-segment.png",
    "net-stand-upper-stand-segment.png",
    "net-stand-post-joint-exploded-right.png",
    "net-stand-post-joint-exploded-left.png",
)


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
    camera: str | None = None,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    openscad_command = [
        openscad,
        "-o",
        str(output),
        "-D",
        f'PART="{part}"',
        "--render",
        f"--camera={camera}" if camera else "--viewall",
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


def remove_obsolete_outputs(output_dir: Path) -> None:
    """Remove only retired evidence files emitted by this render script."""
    for name in OBSOLETE_OUTPUT_NAMES:
        output = output_dir / name
        if output.is_file():
            output.unlink()
            print("REMOVED_STALE_RENDER", output)


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
    remove_obsolete_outputs(args.output_dir)
    render(openscad, "assembly", args.output_dir / "net-stand-assembly.png", 1800, 1000)
    render(openscad, "left_stand", args.output_dir / "net-stand-left.png", 1200, 1000)
    render(openscad, "right_stand", args.output_dir / "net-stand-right.png", 1200, 1000)
    render(
        openscad,
        "post_clamp_carrier",
        args.output_dir / "net-stand-post-clamp-carrier.png",
        1200,
        1400,
    )
    render(
        openscad,
        "clamp_body_segment",
        args.output_dir / "net-stand-clamp-body-segment.png",
        1200,
        900,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "post_clamp_slide_exploded",
        args.output_dir / "net-stand-post-clamp-slide-exploded-right.png",
        1500,
        1100,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "post_clamp_slide_exploded",
        args.output_dir / "net-stand-post-clamp-slide-exploded-left.png",
        1500,
        1100,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "post_clamp_slide_interface_exploded",
        args.output_dir / "net-stand-post-clamp-slide-interface-exploded-right.png",
        1500,
        900,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "post_skp_leg_foot_stage1",
        args.output_dir / "net-stand-post-skp-leg-foot-stage1-right.png",
        1200,
        900,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "post_skp_leg_foot_stage1",
        args.output_dir / "net-stand-post-skp-leg-foot-stage1-section-right.png",
        1200,
        700,
        definitions=("SIDE=1",),
        # Side cut view: x is horizontal and z is vertical, so the 15 mm
        # inboard terminal chamfer is directly visible.
        camera="900,0,6,90,0,0,100",
    )
    render(
        openscad,
        "post_skp_leg_foot_stage1",
        args.output_dir / "net-stand-post-skp-leg-foot-stage1-front-right.png",
        900,
        700,
        definitions=("SIDE=1",),
        # Front view along x: the two symmetric y-side groups and the central
        # opening remain visible as one lower-device silhouette.
        camera="898,0,6,90,0,90,100",
    )
    render(
        openscad,
        "post_skp_leg_foot_stage1_exploded",
        args.output_dir / "net-stand-post-skp-leg-foot-stage1-exploded-right.png",
        1500,
        1100,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "clamp_body_skp_leg_foot_fit",
        args.output_dir / "net-stand-clamp-body-skp-leg-foot-fit-right.png",
        1400,
        1000,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "post_skp_leg_foot_clamp_fit",
        args.output_dir / "net-stand-post-skp-leg-foot-clamp-fit-right.png",
        1600,
        1200,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "post_clamp_seated",
        args.output_dir / "net-stand-post-clamp-seated-right.png",
        1500,
        1100,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "post_clamp_seated_fit_section",
        args.output_dir / "net-stand-post-clamp-seated-fit-section-right.png",
        1500,
        900,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "post_clamp_entry_open_section",
        args.output_dir / "net-stand-post-clamp-entry-open-section-right.png",
        1200,
        900,
        definitions=("SIDE=1",),
        # Keep a small x-normal/isometric angle so the open mouth, the two
        # side pockets and the seated carrier's actual material thickness are
        # all visible.  The section itself is generated from the real fixed
        # and carrier solids.
        camera="920,0,2,90,0,45,150",
    )
    render(
        openscad,
        "clamp_slide_exploded",
        args.output_dir / "net-stand-clamp-slide-exploded-right.png",
        1500,
        1100,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "clamp_slide_fit_probe",
        args.output_dir / "net-stand-clamp-slide-fit-probe-right.png",
        1400,
        1000,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "clamp_slide_fit_section",
        args.output_dir / "net-stand-clamp-slide-fit-section-right.png",
        1400,
        1000,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "clamp_slide_post_foot_detent_detail",
        args.output_dir / "net-stand-clamp-slide-foot-detent-detail-right.png",
        1200,
        900,
        definitions=("SIDE=1",),
        # Look from the underside of the carrier so the central ball groove
        # cut into the transverse tie is visible instead of hidden by its top
        # face.
        camera="920,0,12,170,20,0,160",
    )
    render(
        openscad,
        "net_clamp_clip",
        args.output_dir / "net-stand-net-clamp-clip-right.png",
        700,
        1000,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "net_clamp_clip",
        args.output_dir / "net-stand-net-clamp-clip-left.png",
        700,
        1000,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "net_clamp_fit_probe",
        args.output_dir / "net-stand-net-clamp-fit-probe-right.png",
        700,
        1000,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "net_clamp_fit_section",
        args.output_dir / "net-stand-net-clamp-fit-section-right.png",
        1200,
        900,
        definitions=("SIDE=1",),
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
        "table_clamp_electronics_preview",
        args.output_dir / "net-stand-table-clamp-electronics-preview.png",
        1200,
        900,
    )
    render(
        openscad,
        "table_clamp_electronics_cutaway_preview",
        args.output_dir / "net-stand-table-clamp-electronics-cutaway.png",
        1400,
        1000,
    )
    render(
        openscad,
        "clamp_electronics_full_cutaway",
        args.output_dir / "net-stand-electronics-full-cutaway.png",
        1400,
        1100,
    )
    render(
        openscad,
        "clamp_electronics_shell_cutaway",
        args.output_dir / "net-stand-electronics-shell-cutaway.png",
        1400,
        1100,
    )
    render(
        openscad,
        "clamp_electronics_emitter_fit_preview",
        args.output_dir / "net-stand-electronics-emitter-fit.png",
        1400,
        1100,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "clamp_electronics_exploded",
        args.output_dir / "net-stand-electronics-exploded-right.png",
        1400,
        1100,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "clamp_electronics_emitter_exploded",
        args.output_dir / "net-stand-electronics-exploded-left.png",
        1400,
        1100,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "clamp_electronics_m6_integration_preview",
        args.output_dir / "net-stand-electronics-m6-integration-right.png",
        1400,
        1500,
        definitions=("SIDE=1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "clamp_electronics_m6_integration_preview",
        args.output_dir / "net-stand-electronics-m6-integration-left.png",
        1400,
        1500,
        definitions=("SIDE=-1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "clamp_electronics_system_exploded",
        args.output_dir / "net-stand-electronics-system-exploded.png",
        1800,
        1300,
    )
    render(
        openscad,
        "clamp_electronics_cover",
        args.output_dir / "net-stand-clamp-electronics-cover.png",
        1200,
        700,
    )
    render(
        openscad,
        "clamp_electronics_system_preview",
        args.output_dir / "net-stand-electronics-system-preview.png",
        1800,
        900,
    )
    render(
        openscad,
        "clamp_electronics_emitter_preview",
        args.output_dir / "net-stand-electronics-emitter-preview.png",
        1200,
        900,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "clamp_electronics_ui_panel",
        args.output_dir / "net-stand-electronics-ui-panel.png",
        1200,
        700,
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
    render(
        openscad,
        "stg120_outer_carrier",
        args.output_dir / "net-stand-stg120-outer-carrier-right.png",
        900,
        1200,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "stg120_outer_carrier",
        args.output_dir / "net-stand-stg120-outer-carrier-left.png",
        900,
        1200,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "stg120_center_bridge",
        args.output_dir / "net-stand-stg120-center-bridge.png",
        700,
        1200,
    )
    render(
        openscad,
        "stg120_preview",
        args.output_dir / "net-stand-stg120-preview.png",
        1800,
        900,
    )
    render(
        openscad,
        "m6_detector_mount",
        args.output_dir / "net-stand-m6-detector-mount-right.png",
        1100,
        1300,
        definitions=("SIDE=1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "m6_detector_mount",
        args.output_dir / "net-stand-m6-detector-mount-left.png",
        1100,
        1300,
        definitions=("SIDE=-1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "m6_detector_exploded",
        args.output_dir / "net-stand-m6-detector-exploded-right.png",
        1500,
        1400,
        definitions=("SIDE=1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "m6_detector_exploded",
        args.output_dir / "net-stand-m6-detector-exploded-left.png",
        1500,
        1400,
        definitions=("SIDE=-1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "m6_detector_fit_probe",
        args.output_dir / "net-stand-m6-detector-fit-probe-right.png",
        1000,
        1300,
        definitions=("SIDE=1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "m6_detector_fit_probe",
        args.output_dir / "net-stand-m6-detector-fit-probe-left.png",
        1000,
        1300,
        definitions=("SIDE=-1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "m6_sensor_single",
        args.output_dir / "net-stand-m6-sensor-single-right.png",
        900,
        900,
        definitions=("SIDE=1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "m6_sensor_single",
        args.output_dir / "net-stand-m6-sensor-single-left.png",
        900,
        900,
        definitions=("SIDE=-1", "m6_show_optical_direction=true"),
    )
    render(
        openscad,
        "m6_detector_body",
        args.output_dir / "net-stand-m6-detector-body-right.png",
        700,
        1300,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "m6_detector_shell_front",
        args.output_dir / "net-stand-m6-detector-shell-front-right.png",
        900,
        1300,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "m6_detector_shell_rear",
        args.output_dir / "net-stand-m6-detector-shell-rear-right.png",
        900,
        1300,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "m6_detector_bottom_cover",
        args.output_dir / "net-stand-m6-detector-bottom-cover-right.png",
        900,
        700,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "m6_detector_wiring_reference",
        args.output_dir / "net-stand-m6-wiring-reference-right.png",
        1000,
        1300,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "m6_detector_wiring_reference",
        args.output_dir / "net-stand-m6-wiring-reference-left.png",
        1000,
        1300,
        definitions=("SIDE=-1",),
    )
    render(
        openscad,
        "m6_ballhead",
        args.output_dir / "net-stand-m6-vertical-ballhead-right.png",
        900,
        900,
        definitions=("SIDE=1",),
    )
    render(
        openscad,
        "m6_sensor_array",
        args.output_dir / "net-stand-m6-sensor-array-right.png",
        700,
        1300,
        definitions=("SIDE=1",),
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
        "sensor_mount_body",
        args.output_dir / "net-stand-sensor-mount-body.png",
        1000,
        800,
    )
    render(openscad, "net", args.output_dir / "net-stand-net-no-top-rail.png", 1800, 700)
    render(openscad, "calibration_gauge", args.output_dir / "net-stand-calibration-gauge.png", 900, 1000)
    print(f"NET_STAND_PREVIEWS_OK ({args.output_dir})")


if __name__ == "__main__":
    main()
