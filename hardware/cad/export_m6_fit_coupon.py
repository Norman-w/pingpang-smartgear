#!/usr/bin/env python3
"""Export the standalone M6 sensor fit coupon.

The coupon is a real first-article print used to check one purchased M6
right-angle sensor, its lock nut and cable exit before the two aluminum comb
rails are machined.  It intentionally has its own output directory and never
enters the 26-piece PETG/TPU print manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from validate_net_stand import _stl_topology, _stl_volume
from validate_scad import find_openscad, stl_bounds


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_stand.scad"
DEFAULT_OUTPUT = HERE / "exports" / "net-stand-v0.1" / "m6-fit-coupon"
SCHEMA_VERSION = "m6-fit-coupon-0.1"
STL_NAME = "m6-sensor-test-coupon.stl"
MANIFEST_NAME = "manifest.json"


def _round(value: float) -> float:
    rounded = round(float(value), 4)
    return 0.0 if abs(rounded) < 0.00005 else rounded


def _remove_stale_files(output_dir: Path, expected: set[str]) -> None:
    stale = sorted(
        path
        for path in output_dir.iterdir()
        if path.is_file() and path.name not in expected
    )
    if stale:
        names = ", ".join(path.name for path in stale)
        raise RuntimeError(
            "fit-coupon output contains stale files; rerun with --clean: " + names
        )


def _run_openscad(openscad: str, output: Path) -> None:
    result = subprocess.run(
        [
            openscad,
            "-o",
            str(output),
            "-D",
            'PART="m6_sensor_test_coupon"',
            str(SOURCE),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"OpenSCAD 导出试装样件失败:\n{result.stdout}")
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("OpenSCAD 没有生成 M6 试装样件 STL")


def export_fit_coupon(
    openscad: str,
    output_dir: Path,
    *,
    clean: bool = False,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = {STL_NAME, MANIFEST_NAME}
    if clean:
        for path in output_dir.iterdir():
            if path.is_file() and path.name not in expected:
                path.unlink()
    _remove_stale_files(output_dir, expected)

    stl_path = output_dir / STL_NAME
    _run_openscad(openscad, stl_path)
    closed, topology_summary = _stl_topology(stl_path)
    if not closed:
        raise RuntimeError(
            f"M6 试装样件不是封闭 STL: {topology_summary}"
        )
    volume_mm3 = _stl_volume(stl_path)
    if volume_mm3 <= 1e-6:
        raise RuntimeError(f"M6 试装样件体积无效: {volume_mm3}")
    min_x, max_x, min_y, max_y, min_z, max_z = stl_bounds(stl_path)
    manifest: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "source": "hardware/cad/net_stand.scad",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "part": 'PART="m6_sensor_test_coupon"',
        "units": "mm",
        "material": "PETG",
        "purpose": "加工两根铝合金梳齿条前，验证一枚真实 M6 直角器件、锁紧螺母、防转窝、头部方向和线缆让位。",
        "formal_print_manifest": False,
        "stl": STL_NAME,
        "local_origin": "试装样件背骨 x-min、y=0 中心线、z=0 底面",
        "bounds": {
            "min": [_round(min_x), _round(min_y), _round(min_z)],
            "max": [_round(max_x), _round(max_y), _round(max_z)],
            "size": [
                _round(max_x - min_x),
                _round(max_y - min_y),
                _round(max_z - min_z),
            ],
        },
        "volume_mm3": _round(volume_mm3),
        "topology": {
            "watertight_by_edge_topology": closed,
            "summary": topology_summary,
        },
        "fit_contract": {
            "sensor_thread_clearance_d_mm": 6.5,
            "sensor_thread_spec_candidate": "M6x0.75",
            "lock_nut_af_mm": 10,
            "guard_outer_d_mm": 15,
            "body_clearance_d_mm": 10,
            "cable_exit_must_be_checked_on_real_part": True,
        },
    }
    (output_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    try:
        manifest = export_fit_coupon(
            find_openscad(), args.output_dir, clean=args.clean
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(f"M6_FIT_COUPON_INVALID: {error}")
        return 1
    print(
        "M6_FIT_COUPON_OK "
        f"(bounds={manifest['bounds']['size']} mm, "
        f"watertight={manifest['topology']['watertight_by_edge_topology']}, "
        f"formal_print_manifest={manifest['formal_print_manifest']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
