#!/usr/bin/env python3
"""Regression-test the independent M6 body/cover/support preview package."""

from __future__ import annotations

import hashlib
import math
import tempfile
from pathlib import Path

from export_m6_component_previews import COMPONENTS, SCHEMA_VERSION, SOURCE, export_component_previews
from validate_net_stand import _stl_mirror_signature
from validate_scad import find_openscad


def _entries(manifest: dict[str, object]) -> list[dict[str, object]]:
    value = manifest.get("parts")
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise AssertionError("M6 component manifest parts must be a list of objects")
    return value  # type: ignore[return-value]


def _size(entry: dict[str, object]) -> list[float | int]:
    bounds = entry.get("bounds")
    if not isinstance(bounds, dict) or not isinstance(bounds.get("size"), list):
        raise AssertionError(f"missing bounds size: {entry.get('file')}")
    return bounds["size"]  # type: ignore[return-value]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="m6-component-previews-") as directory:
        output_dir = Path(directory)
        manifest = export_component_previews(
            find_openscad(), output_dir, clean=True
        )
        entries = _entries(manifest)
        expected_parts = {spec.part for spec in COMPONENTS}
        if manifest.get("schema_version") != SCHEMA_VERSION:
            raise AssertionError("unexpected M6 component preview schema")
        if manifest.get("source") != "hardware/cad/net_stand.scad":
            raise AssertionError("component preview source changed")
        if manifest.get("source_sha256") != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
            raise AssertionError("component preview source hash does not match")
        if len(entries) != len(COMPONENTS) * 2:
            raise AssertionError("expected right and left exports for every component")

        by_part: dict[str, list[dict[str, object]]] = {}
        for entry in entries:
            part = entry.get("part")
            if part not in expected_parts:
                raise AssertionError(f"unexpected M6 component: {part}")
            by_part.setdefault(part, []).append(entry)
            if entry.get("side") not in {"right", "left"}:
                raise AssertionError("component preview side metadata is invalid")
            if entry.get("in_formal_print_manifest") is not False:
                raise AssertionError("component previews must stay outside print manifest")
            if entry.get("topology", {}).get("watertight_by_edge_topology") is not True:  # type: ignore[union-attr]
                raise AssertionError(f"component is not watertight: {entry.get('file')}")
            if not isinstance(entry.get("volume_mm3"), (int, float)) or entry["volume_mm3"] <= 0:
                raise AssertionError(f"component volume is invalid: {entry.get('file')}")
            output = output_dir / str(entry["file"])
            if not output.is_file() or output.stat().st_size == 0:
                raise AssertionError(f"missing component STL: {output.name}")

        if set(by_part) != expected_parts or any(len(items) != 2 for items in by_part.values()):
            raise AssertionError("component preview side matrix changed")

        spec_by_part = {spec.part: spec for spec in COMPONENTS}
        for part, items in by_part.items():
            right = next(item for item in items if item["side"] == "right")
            left = next(item for item in items if item["side"] == "left")
            right_path = output_dir / str(right["file"])
            left_path = output_dir / str(left["file"])
            if _stl_mirror_signature(right_path, reflect_x=False) != _stl_mirror_signature(
                left_path, reflect_x=True
            ):
                raise AssertionError(f"left/right mirror changed for {part}")
            expected_printable = spec_by_part[part].preview_is_printable
            if right.get("printable") is not expected_printable or left.get("printable") is not expected_printable:
                raise AssertionError(f"printability metadata changed for {part}")

        body_size = _size(by_part["m6_detector_body"][0])
        if body_size != [20, 69.2, 216]:
            raise AssertionError(f"integral T-tail body envelope changed: {body_size}")
        for part in (
            "m6_detector_shell_front",
            "m6_detector_shell_rear",
            "m6_detector_bottom_cover",
        ):
            size = _size(by_part[part][0])
            if not all(isinstance(value, (int, float)) and value > 0 for value in size):
                raise AssertionError(f"cover preview has an empty axis: {part} {size}")
            if not spec_by_part[part].preview_is_printable:
                raise AssertionError(f"cover must be a printable candidate: {part}")

        body_z = _size(by_part["m6_detector_body"][0])[2]
        if not math.isclose(float(body_z), 216.0, abs_tol=0.01):
            raise AssertionError("body vertical height changed")

    print("M6_COMPONENT_PREVIEWS_TEST_OK (12 watertight body/cover/support/adapter previews)")


if __name__ == "__main__":
    main()
