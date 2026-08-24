#!/usr/bin/env python3
"""Keep the dependency-free intent preview aligned with the SCAD source."""

from __future__ import annotations

import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCAD = HERE / "net_stand.scad"
PREVIEW = HERE / "preview.py"

# These are the direct, first-article geometry values that the lightweight
# preview must mirror. Derived coordinates are intentionally checked by the
# OpenSCAD validator; this test prevents the two visual entry points from
# silently diverging on the design boundary itself.
PARAMETER_MAP = {
    "TABLE_WIDTH": "table_width",
    "TABLE_THICKNESS": "table_thickness",
    "POST_OFFSET": "post_offset",
    "POST_WIDTH": "post_body_width",
    "CLAMP_OUTER_EXTENSION": "clamp_outer_extension",
    "CLAMP_REACH_INBOARD": "clamp_reach_inboard",
    "CLAMP_PAD_T": "clamp_pad_t",
    "CLAMP_CLEARANCE": "clamp_clearance",
    "CLAMP_SCREW_INSET": "clamp_screw_inset",
    "CLAMP_KNOB_D": "clamp_knob_d",
    "CLAMP_KNOB_H": "clamp_knob_h",
    "CLAMP_SCREW_TO_KNOB_TOP": "clamp_screw_to_knob_top",
    "CLAMP_NUT_AF": "clamp_nut_af",
    "CLAMP_NUT_H": "clamp_nut_h",
    "CLAMP_NUT_CLEARANCE": "clamp_nut_clearance",
    "CLAMP_KNOB_NUT_GAP": "clamp_knob_nut_gap",
    "CLAMP_LOWER_ARM_CLEARANCE": "clamp_lower_arm_clearance",
    "CLAMP_PRESSURE_PAD_WIDTH": "clamp_pressure_pad_width",
    "CLAMP_PRESSURE_PAD_T": "clamp_pressure_pad_t",
}


def direct_assignments(path: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    pattern = re.compile(
        r"^\s*([A-Za-z_]\w*)\s*=\s*([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            values[match.group(1)] = float(match.group(2))
    return values


def main() -> None:
    scad_values = direct_assignments(SCAD)
    preview_values = direct_assignments(PREVIEW)
    missing_scad = sorted(set(PARAMETER_MAP.values()) - set(scad_values))
    missing_preview = sorted(set(PARAMETER_MAP) - set(preview_values))
    if missing_scad or missing_preview:
        raise AssertionError(
            f"preview parameter coverage missing: scad={missing_scad}, "
            f"preview={missing_preview}"
        )

    mismatches = []
    for preview_name, scad_name in PARAMETER_MAP.items():
        if preview_values[preview_name] != scad_values[scad_name]:
            mismatches.append(
                f"{preview_name}={preview_values[preview_name]} "
                f"!= {scad_name}={scad_values[scad_name]}"
            )
    if mismatches:
        raise AssertionError("preview/SCAD parameter mismatch: " + "; ".join(mismatches))

    print(f"PREVIEW_CONSISTENCY_OK ({len(PARAMETER_MAP)} direct parameters)")


if __name__ == "__main__":
    main()
