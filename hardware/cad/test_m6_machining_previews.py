#!/usr/bin/env python3
"""Validate the independent M6 machining preview export package."""

from __future__ import annotations

import tempfile
from pathlib import Path

from export_m6_machining_previews import PREVIEW_PARTS, export_machining_previews
from validate_scad import find_openscad


def _entries_by_part(manifest: dict[str, object]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for entry in manifest["parts"]:  # type: ignore[index]
        grouped.setdefault(entry["part"], []).append(entry)  # type: ignore[index]
    return grouped


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="m6-machining-previews-") as directory:
        output_dir = Path(directory)
        manifest = export_machining_previews(
            find_openscad(), output_dir, clean=True
        )
        if len(manifest["parts"]) != len(PREVIEW_PARTS) * 2:  # type: ignore[arg-type]
            raise AssertionError("expected one right and one left preview per part")
        grouped = _entries_by_part(manifest)
        if set(grouped) != {spec.part for spec in PREVIEW_PARTS}:
            raise AssertionError("machining preview part set changed")
        for entries in grouped.values():
            if len(entries) != 2:
                raise AssertionError("each machining part must have two side previews")
            for entry in entries:
                if entry["printable"] is not False:
                    raise AssertionError("machining previews must stay outside print manifest")
                if not entry["topology"]["watertight_by_edge_topology"]:  # type: ignore[index]
                    raise AssertionError("machining preview is not watertight")
                if not isinstance(entry.get("volume_mm3"), (int, float)) or entry["volume_mm3"] <= 0:
                    raise AssertionError("machining preview volume must be positive")
                output = output_dir / entry["file"]  # type: ignore[index]
                if not output.is_file() or output.stat().st_size == 0:
                    raise AssertionError(f"missing machining preview: {output.name}")

        def size(part: str) -> list[float]:
            return grouped[part][0]["bounds"]["size"]  # type: ignore[index,return-value]

        if size("m6_machining_detector_body") != [20, 69.2, 216]:
            raise AssertionError("detector T-tail local envelope changed")
        if size("m6_machining_support") != [106.75, 18, 60]:
            raise AssertionError("90-degree support local envelope changed")
        if size("m6_machining_adapter") != [6, 56, 228]:
            raise AssertionError("adapter plate envelope changed")

    print("M6_MACHINING_PREVIEWS_TEST_OK (6 watertight T-tail/support/adapter previews)")


if __name__ == "__main__":
    main()
