#!/usr/bin/env python3
"""Export the generated KiCad boards as mechanical board/component models.

The PCB generators remain the source of truth for the board outline, pads,
nets and every PCB-mounted library 3D model, including the UI buttons, LEDs
and USB-C receptacle. Off-board wire-connected parts such as the screen and
speaker are supplied by the OpenSCAD mechanical assembly and are intentionally
not part of a PCB export. This adapter creates stable STL/STEP artifacts for
the OpenSCAD mechanical assembly and refuses to silently accept a board with
no attached library models.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "3d" / "v0.2"
OUTLINE_SCRIPT = HERE / "esp32-control-v0.1" / "generate_board_outline_scad.py"
OUTLINE_OUTPUT = HERE / "esp32-control-v0.1" / "board-outline.scad"
USB_SHELL_SCRIPT = HERE / "export_usb_shell_model.py"
BOARDS = (
    HERE / "esp32-control-v0.1" / "esp32-control-v0.1.kicad_pcb",
    HERE / "daughter-boards-v0.2" / "m6-receiver-carrier-v0.2.kicad_pcb",
    HERE / "daughter-boards-v0.2" / "emitter-power-v0.2.kicad_pcb",
    HERE / "daughter-boards-v0.2" / "ui-panel-v0.2.kicad_pcb",
)


def find_cli() -> str:
    candidates = (
        os.environ.get("KICAD_CLI", ""),
        shutil.which("kicad-cli") or "",
        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("kicad-cli not found; set KICAD_CLI")


def find_freecadcmd() -> str:
    candidates = (
        os.environ.get("FREECADCMD", ""),
        shutil.which("freecadcmd") or "",
        "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd",
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError(
        "FreeCADCmd not found; set FREECADCMD to regenerate the KiCad-derived "
        "USB-C housing STL"
    )


def model_count(board: Path) -> tuple[int, int]:
    """Return footprint count and attached 3D model count without GUI."""
    python = os.environ.get(
        "KICAD_PYTHON",
        "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9",
    )
    if not Path(python).is_file():
        return 0, board.read_text(errors="ignore").count("\n\t\t(model ")
    script = (
        "import pcbnew,sys; "
        "b=pcbnew.LoadBoard(sys.argv[1]); "
        "print(len(b.GetFootprints()), sum(len(fp.Models()) for fp in b.GetFootprints()))"
    )
    result = subprocess.run(
        [python, "-c", script, str(board)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    values = result.stdout.strip().splitlines()[-1].split()
    return int(values[0]), int(values[1])


def export(cli: str, board: Path, output_dir: Path) -> None:
    stem = board.stem
    footprints, models = model_count(board)
    if models <= 0:
        raise RuntimeError(f"{board.name} has no attached 3D models")
    output_dir.mkdir(parents=True, exist_ok=True)
    for extension, subcommand in (("stl", "stl"), ("step", "step")):
        output = output_dir / f"{stem}.{extension}"
        command = [
            cli,
            "pcb",
            "export",
            subcommand,
            "--force",
            "--subst-models",
            "--fuse-shapes",
            "-o",
            str(output),
            str(board),
        ]
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError(f"{subcommand} export failed for {board.name}:\n{result.stdout}")
    print(f"EXPORTED {stem}: footprints={footprints} models={models}")


def export_mechanical_outline(board: Path) -> None:
    """Keep the tracked OpenSCAD pocket contour tied to KiCad Edge.Cuts."""
    result = subprocess.run(
        [
            sys.executable,
            str(OUTLINE_SCRIPT),
            "--board",
            str(board),
            "--output",
            str(OUTLINE_OUTPUT),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"board outline export failed:\n{result.stdout}")
    print(result.stdout.strip())


def export_usb_housing(output_dir: Path) -> None:
    """Derive the panel-facing KiCad USB shell and omit solder contacts."""
    if not USB_SHELL_SCRIPT.is_file():
        raise RuntimeError(f"missing USB housing exporter: {USB_SHELL_SCRIPT}")
    output = output_dir / "usb-c-shell-v0.2.stl"
    result = subprocess.run(
        [find_freecadcmd(), str(USB_SHELL_SCRIPT), str(output)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0 or not output.is_file():
        raise RuntimeError(f"USB-C housing export failed:\n{result.stdout}")
    print(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cli = find_cli()
    for board in BOARDS:
        if not board.is_file():
            raise RuntimeError(f"missing board: {board}")
        export(cli, board, args.output_dir)
    export_mechanical_outline(BOARDS[0])
    export_usb_housing(args.output_dir)
    print(f"BOARD_MODELS_OK {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
