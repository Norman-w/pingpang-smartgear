#!/usr/bin/env python3
"""Render the rotating-foot guard concept directly from OpenSCAD."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "rotating_foot_guard.scad"
DEFAULT_OPENSCAD = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"


def find_openscad() -> str:
    candidates = [os.environ.get("OPENSCAD_BIN", ""), shutil.which("openscad") or "", DEFAULT_OPENSCAD]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise RuntimeError("未找到 OpenSCAD；请设置 OPENSCAD_BIN")


def run_openscad(openscad: str, part: str, output: Path, side: int, render: bool) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        openscad,
        "-o",
        str(output),
        "-D",
        f'PART="{part}"',
        "-D",
        f"SIDE={side}",
    ]
    if render:
        command.extend(
            [
                "--render",
                "--viewall",
                "--projection=ortho",
                "--imgsize",
                "1400,1000",
                "--colorscheme=Tomorrow",
            ]
        )
    command.append(str(SOURCE))
    print("$", " ".join(command))
    subprocess.run(command, check=True)
    if not output.is_file() or output.stat().st_size < 1024:
        raise RuntimeError(f"OpenSCAD 未生成有效输出: {output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--side", type=int, choices=(-1, 1), default=1)
    parser.add_argument("--export-stl", action="store_true", help="同时导出左右镜像的单件 STL")
    args = parser.parse_args()

    openscad = find_openscad()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    renders = [
        ("assembly_deployed", "guard-clip-assembly-deployed.png"),
        ("assembly_folded", "guard-clip-assembly-folded.png"),
        ("clip", "guard-clip-printable.png"),
        ("clip_cutaway", "guard-clip-cutaway.png"),
        ("fit_section", "guard-clip-fit-section.png"),
        ("hook_test_coupon", "guard-clip-hook-test-coupon.png"),
        ("print_orientation", "guard-clip-print-orientation.png"),
    ]
    for part, filename in renders:
        run_openscad(openscad, part, args.output_dir / filename, args.side, render=True)

    if args.export_stl:
        stl_dir = args.output_dir.parent.parent / "exports" / "rotating-foot-guard-v0.1"
        stl_dir.mkdir(parents=True, exist_ok=True)
        for side in (1, -1):
            side_label = "plus" if side > 0 else "minus"
            run_openscad(
                openscad,
                "clip",
                stl_dir / f"rotating-foot-guard-side-{side_label}.stl",
                side,
                render=False,
            )
            run_openscad(
                openscad,
                "print_orientation",
                stl_dir / f"rotating-foot-guard-side-{side_label}-print-orientation.stl",
                side,
                render=False,
            )
        run_openscad(
            openscad,
            "hook_test_coupon",
            stl_dir / "rotating-foot-guard-hook-test-coupon.stl",
            args.side,
            render=False,
        )
        print(f"STL_OUTPUT_DIR={stl_dir}")

    print(f"GUARD_CLIP_PREVIEWS_OK={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
