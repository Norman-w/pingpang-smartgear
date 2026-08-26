#!/usr/bin/env python3
"""Regression-test the standalone M6 sensor fit coupon export."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from export_m6_fit_coupon import (
    MANIFEST_NAME,
    SOURCE,
    STL_NAME,
    export_fit_coupon,
)
from export_net_stand_printables import EXPORT_SPECS
from validate_scad import find_openscad


def main() -> None:
    if any(spec.part == "m6_sensor_test_coupon" for spec in EXPORT_SPECS):
        raise AssertionError("fit coupon must remain outside the formal print matrix")

    with tempfile.TemporaryDirectory(prefix="m6-fit-coupon-") as directory:
        output_dir = Path(directory)
        manifest = export_fit_coupon(find_openscad(), output_dir, clean=True)
        manifest_path = output_dir / MANIFEST_NAME
        stl_path = output_dir / STL_NAME
        if not manifest_path.is_file() or not stl_path.is_file():
            raise AssertionError("fit coupon export did not produce both artifacts")
        if manifest["schema_version"] != "m6-fit-coupon-0.1":
            raise AssertionError("unexpected fit coupon schema")
        if manifest["formal_print_manifest"] is not False:
            raise AssertionError("fit coupon must be marked outside formal print manifest")
        if manifest["source_sha256"] != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
            raise AssertionError("fit coupon source hash mismatch")
        if manifest["bounds"]["min"] != [-16, -21, 0]:
            raise AssertionError("fit coupon local minimum changed")
        if manifest["bounds"]["max"] != [8, 21, 24]:
            raise AssertionError("fit coupon local maximum changed")
        if manifest["bounds"]["size"] != [24, 42, 24]:
            raise AssertionError("fit coupon envelope changed")
        if not isinstance(manifest.get("volume_mm3"), (int, float)) or manifest["volume_mm3"] <= 0:
            raise AssertionError("fit coupon volume must be positive")
        if not manifest["topology"]["watertight_by_edge_topology"]:
            raise AssertionError("fit coupon must be watertight")
        disk_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if disk_manifest != manifest:
            raise AssertionError("fit coupon manifest is not reproducible")

    print("M6_FIT_COUPON_TEST_OK (watertight 24×42×24 mm short standalone fit print)")


if __name__ == "__main__":
    main()
