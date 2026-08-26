#!/usr/bin/env python3
"""Export the future-CNC M6 body preview.

This STL is an inspection/quotation aid, not the formal PETG print manifest.
The body is the same plain rectangular first article used for PETG; a future
6061-T6 CNC version can reuse its envelope. The vertical 13 mm ballhead and
its net-clamp interface are purchased and therefore have no self-made STL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from validate_net_stand import _stl_topology, _stl_volume
from validate_scad import find_openscad, stl_bounds


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_stand.scad"
DEFAULT_OUTPUT = HERE / "exports" / "net-stand-v0.1" / "m6-machining-previews"
SCHEMA_VERSION = "m6-machining-previews-0.6-20-mm-pitch-petg-body-rear-boss"


@dataclass(frozen=True)
class MachiningPreviewSpec:
    part: str
    stem: str
    name_zh: str
    local_origin: str
    notes: str


PREVIEW_PARTS = (
    MachiningPreviewSpec(
        "m6_machining_detector_body",
        "m6-detector-body",
        "M6 十路 45° L 型矩形主体（PETG 首样；后续可换 CNC）",
        "主体 x-min、y-min、z-min；当前是 10×56×216 mm 矩形长条，未来 CNC 沿用同一包络",
        "当前首样用 PETG 打印；后续可换 6061-T6 CNC。主体只有十个 20 mm 节距光学孔、浅 AF8 防转窝、盖件孔和 y± 边槽，不带 T 尾座、M8 接口或主体内线缆槽；后盖另有 PETG 加厚 boss，13 mm 采购球头保持竖直姿态并直接接商品网夹。",
    ),
)


def _round(value: float) -> float:
    rounded = round(float(value), 4)
    return 0.0 if abs(rounded) < 0.00005 else rounded


def _run_export(openscad: str, output: Path, spec: MachiningPreviewSpec, side: str, side_value: int) -> None:
    command = [
        openscad,
        "-o",
        str(output),
        "-D",
        f'PART="{spec.part}"',
        "-D",
        f"SIDE={side_value}",
        str(SOURCE),
    ]
    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"OpenSCAD 导出失败: {output.name} ({spec.part}, {side})\n{result.stdout}"
        )
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"OpenSCAD 没有生成 STL: {output.name}")


def _manifest_entry(output: Path, spec: MachiningPreviewSpec, side: str, side_value: int) -> dict[str, object]:
    closed, topology_summary = _stl_topology(output)
    if not closed:
        raise RuntimeError(
            f"机加工预览不是封闭 STL: {output.name}: {topology_summary}"
        )
    volume_mm3 = _stl_volume(output)
    if volume_mm3 <= 1e-6:
        raise RuntimeError(f"机加工预览体积无效: {output.name}: {volume_mm3}")
    min_x, max_x, min_y, max_y, min_z, max_z = stl_bounds(output)
    return {
        "file": output.name,
        "part": spec.part,
        "name_zh": f"{spec.name_zh}（{'右' if side == 'right' else '左'}）",
        "component_kind": "机加工件预览",
        "printable": False,
        "definitions": [f'PART="{spec.part}"', f"SIDE={side_value}"],
        "side": side,
        "side_value": side_value,
        "units": "mm",
        "material": "PETG first article; future 6061-T6 CNC option",
        "local_origin": spec.local_origin,
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
        "notes": spec.notes,
    }


def _stale_stl_files(output_dir: Path, expected: set[str]) -> list[Path]:
    return sorted(
        (path for path in output_dir.glob("*.stl") if path.name not in expected),
        key=lambda path: path.name,
    )


def export_machining_previews(
    openscad: str,
    output_dir: Path,
    *,
    clean: bool = False,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = {
        f"{side}-{spec.stem}.stl"
        for side, _ in (("right", 1), ("left", -1))
        for spec in PREVIEW_PARTS
    }
    stale = _stale_stl_files(output_dir, expected)
    if stale and not clean:
        names = ", ".join(path.name for path in stale)
        raise RuntimeError(
            f"机加工预览目录存在旧 STL：{names}；需要显式传 --clean 才会清理"
        )
    if clean:
        for path in stale:
            path.unlink()

    entries: list[dict[str, object]] = []
    for side, side_value in (("right", 1), ("left", -1)):
        for spec in PREVIEW_PARTS:
            output = output_dir / f"{side}-{spec.stem}.stl"
            _run_export(openscad, output, spec, side, side_value)
            entries.append(_manifest_entry(output, spec, side, side_value))

    manifest: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "status": "未来 CNC 主体/采购云台接口预览；不是最终放行图",
        "source": "hardware/cad/net_stand.scad",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "units": "mm",
        "material": "PETG first article body; future 6061-T6 CNC option",
        "quantity": {
            "detector_bodies": 2,
            "purchased_vertical_ballheads": 2,
            "preview_files": len(entries),
        },
        "coordinate_system": {
            "side_files": "right/left are mirrored local previews; use the same handedness as the net clamp",
            "positive_axes": "each entry documents its local origin; x/y/z remain OpenSCAD millimeters",
        },
        "parts": entries,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="输出 Git 忽略的机加工预览目录",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="只清理本目录中不属于当前预览清单的旧 STL",
    )
    args = parser.parse_args()
    manifest = export_machining_previews(
        find_openscad(), args.output_dir.resolve(), clean=args.clean
    )
    print(
        "M6_MACHINING_PREVIEWS_OK "
        f"(parts={len(manifest['parts'])}, output={args.output_dir.resolve()})"
    )


if __name__ == "__main__":
    main()
