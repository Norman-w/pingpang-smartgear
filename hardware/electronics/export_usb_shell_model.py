#!/usr/bin/env python3
"""Export the USB-C housing from KiCad's actual placed component model.

The UI board is exported first with ``kicad-cli``.  This script then reads that
placed STEP and keeps the four large USB housing/shield solids, excluding all
small solder/contact solids.  Reading the component-filtered KiCad export is
intentional: it preserves pcbnew's model rotation, origin, and offsets instead
of recreating a hand-written transform that can drift from the board STL.

The panel opening itself is driven by the target footprint's F.Fab rounded
profile in ``USB_C_Receptacle_G-Switch_GT-USB-7051x.kicad_mod``.  This STL is a
separate visual/interference reference and is never used as a SCAD proxy.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


UI_STEP_NAME = "ui-panel-v0.2.step"
USB_X_MIN = 40.0
USB_X_MAX = 54.0
USB_RAW_Y_MIN = -29.0
USB_RAW_Y_MAX = -21.0
MIN_HOUSING_VOLUME = 10.0
EXPECTED_HOUSING_SOLIDS = 4
FRONT_Z_TOLERANCE = 0.01


def parse_output(argv: list[str]) -> Path:
    # FreeCADCmd leaves the script path at sys.argv[1].  Accept its invocation
    # shape and a normal Python-style invocation for local checks.
    args = argv[2:] if len(argv) > 1 and argv[1].endswith(".py") else argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    return parser.parse_args(args).output


def is_usb_housing_candidate(solid) -> bool:
    bound = solid.BoundBox
    return (
        solid.Volume > MIN_HOUSING_VOLUME
        and bound.XMin >= USB_X_MIN
        and bound.XMax <= USB_X_MAX
        and bound.YMin >= USB_RAW_Y_MIN
        and bound.YMax <= USB_RAW_Y_MAX
        and bound.ZMax > 4.0
    )


def front_profile_bbox(solids):
    """Return the placed front-face x/y envelope for the report line."""
    front_z = max(solid.BoundBox.ZMax for solid in solids)
    points = []
    for solid in solids:
        for vertex in solid.Vertexes:
            point = vertex.Point
            if abs(point.z - front_z) <= FRONT_Z_TOLERANCE:
                points.append(point)
    if not points:
        raise RuntimeError("placed USB housing has no identifiable front profile")
    return (
        front_z,
        min(point.x for point in points),
        max(point.x for point in points),
        min(point.y for point in points),
        max(point.y for point in points),
    )


def main() -> int:
    output = parse_output(sys.argv)

    # FreeCAD modules are deliberately local; the normal repository Python
    # interpreter must still be able to lint this file without FreeCAD.
    import FreeCAD as App  # type: ignore
    import Mesh  # type: ignore
    import MeshPart  # type: ignore
    import Part  # type: ignore

    placed_step = output.parent / UI_STEP_NAME
    if not placed_step.is_file():
        raise FileNotFoundError(
            "KiCad placed UI STEP is required before USB shell export: "
            f"{placed_step}"
        )

    source = Part.read(str(placed_step))
    candidates = [solid for solid in source.Solids if is_usb_housing_candidate(solid)]
    if len(candidates) != EXPECTED_HOUSING_SOLIDS:
        details = [
            (
                round(solid.Volume, 3),
                tuple(round(value, 3) for value in (
                    solid.BoundBox.XMin,
                    solid.BoundBox.XMax,
                    solid.BoundBox.YMin,
                    solid.BoundBox.YMax,
                    solid.BoundBox.ZMin,
                    solid.BoundBox.ZMax,
                )),
            )
            for solid in source.Solids
            if solid.Volume > MIN_HOUSING_VOLUME
        ]
        raise RuntimeError(
            "expected four placed USB housing solids, "
            f"found {len(candidates)}; large solids={details}"
        )

    housing = Part.makeCompound(candidates)
    output.parent.mkdir(parents=True, exist_ok=True)
    mesh = MeshPart.meshFromShape(
        Shape=housing,
        LinearDeflection=0.05,
        AngularDeflection=0.12,
        Relative=False,
    )
    document = App.newDocument("usb_c_housing")
    feature = document.addObject("Mesh::Feature", "usb_c_housing")
    feature.Mesh = mesh
    document.recompute()
    Mesh.export([feature], str(output))

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"FreeCAD did not write USB-C housing STL: {output}")
    bound = housing.BoundBox
    front_z, front_x_min, front_x_max, front_y_min, front_y_max = front_profile_bbox(
        candidates
    )
    print(
        "USB_C_HOUSING_OK "
        f"source={placed_step} solids={len(candidates)} facets={mesh.CountFacets} "
        f"bbox=({bound.XMin:.3f},{bound.XMax:.3f})x"
        f"({bound.YMin:.3f},{bound.YMax:.3f})x"
        f"({bound.ZMin:.3f},{bound.ZMax:.3f}) "
        f"front_z={front_z:.3f} "
        f"front_profile=({front_x_min:.3f},{front_x_max:.3f})x"
        f"({front_y_min:.3f},{front_y_max:.3f}) "
        f"output={output}"
    )
    return 0


if __name__ == "__main__" or (
    len(sys.argv) > 1 and Path(sys.argv[1]).name == Path(__file__).name
):
    raise SystemExit(main())
