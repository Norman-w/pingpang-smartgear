#!/usr/bin/env python3
"""Emit the OpenSCAD board-outline include from the native KiCad board.

The mechanical shell must use the same Edge.Cuts contour as the PCB.  Keep
the generated include beside the native board (rather than under ignored
3D-export output) so a source review can see which Edge.Cuts outline the x-end C-brackets use.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_BOARD = HERE / "esp32-control-v0.1.kicad_pcb"
DEFAULT_OUTPUT = HERE / "board-outline.scad"

_LINE_RE = re.compile(
    r"\(gr_line\s+"
    r"\(start\s+(?P<x0>[-+0-9.eE]+)\s+(?P<y0>[-+0-9.eE]+)\)\s+"
    r"\(end\s+(?P<x1>[-+0-9.eE]+)\s+(?P<y1>[-+0-9.eE]+)\)\s+"
    r"\(stroke.*?\)\s+\(layer\s+\"Edge\.Cuts\"\)",
    re.S,
)
_ARC_RE = re.compile(r"\(gr_arc.*?\(layer\s+\"Edge\.Cuts\"\)", re.S)


def _point_key(point: tuple[float, float]) -> tuple[int, int]:
    return round(point[0] * 1_000_000), round(point[1] * 1_000_000)


def _edge_points(board: Path) -> list[tuple[float, float]]:
    text = board.read_text(encoding="utf-8")
    if _ARC_RE.search(text):
        raise RuntimeError("Edge.Cuts arcs are not supported by this exporter yet")
    segments = [
        (
            (float(match.group("x0")), float(match.group("y0"))),
            (float(match.group("x1")), float(match.group("y1"))),
        )
        for match in _LINE_RE.finditer(text)
    ]
    if len(segments) < 3:
        raise RuntimeError("native KiCad board has fewer than three Edge.Cuts lines")

    first = segments.pop(0)
    points = [first[0], first[1]]
    while segments:
        tail = _point_key(points[-1])
        for index, (start, end) in enumerate(segments):
            if _point_key(start) == tail:
                points.append(end)
                segments.pop(index)
                break
            if _point_key(end) == tail:
                points.append(start)
                segments.pop(index)
                break
        else:
            raise RuntimeError("Edge.Cuts lines do not form one connected loop")

    if _point_key(points[-1]) != _point_key(points[0]):
        raise RuntimeError("Edge.Cuts loop is not closed")
    points.pop()

    # OpenSCAD's polygon needs a stable winding.  Keep the native outline,
    # but reverse clockwise contours so the generated diagnostic is positive.
    area = sum(
        points[index][0] * points[(index + 1) % len(points)][1]
        - points[(index + 1) % len(points)][0] * points[index][1]
        for index in range(len(points))
    ) / 2
    if area < 0:
        points.reverse()
    return points


def write_outline(board: Path, output: Path) -> None:
    points = _edge_points(board)
    output.write_text(
        "// AUTO-GENERATED from esp32-control-v0.1.kicad_pcb Edge.Cuts; do not edit.\n"
        "// Used by net_stand.scad to form the main-PCB insertion pocket/x-end C-brackets.\n"
        "esp32_control_board_edge_points = [\n"
        + "".join(f"    [{x:.6f}, {y:.6f}],\n" for x, y in points)
        + "];\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    write_outline(args.board, args.output)
    print(f"BOARD_OUTLINE_OK points={len(_edge_points(args.board))} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
