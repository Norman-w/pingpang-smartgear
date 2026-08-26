#!/usr/bin/env python3
"""Export the independent aluminum M6 machining previews.

These STL files are inspection/quotation aids, not printable parts.  Every
piece is emitted from the same ``net_stand.scad`` geometry as the assembly,
but in a local coordinate system documented in the manifest.  The output
directory is Git-ignored and is intentionally separate from the PETG print
manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from validate_net_stand import _stl_topology
from validate_scad import find_openscad, stl_bounds


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "net_stand.scad"
DEFAULT_OUTPUT = HERE / "exports" / "net-stand-v0.1" / "m6-machining-previews"
SCHEMA_VERSION = "m6-machining-previews-0.4-20-mm-pitch-l-sensor"


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
        "M6 十路 45° L 型长条主体（铝合金）",
        "主体 x-min、y-min、z-min；局部尺寸 10×56×216 mm",
        "6061-T6 主体，十个中心按 20 mm 节距排列；每路有沿 x 的光学/外丝通孔、绕 x 轴 -45° 的尾线让位和浅六角防转沉孔；线缆不在铝材中挖槽，壳体、底盖、传感器和球头均不包含。",
    ),
    MachiningPreviewSpec(
        "m6_machining_support",
        "m6-90-degree-support",
        "M6 90°金属支撑件",
        "支撑件 x-min、y-min、z-min；局部坐标只描述金属 L 形承力件",
        "水平承托臂、竖直连接腿和两侧三角加固肋一体加工/折弯边界；球头、网夹适配板和螺栓不包含。",
    ),
    MachiningPreviewSpec(
        "m6_machining_adapter",
        "m6-net-clamp-adapter",
        "M6 网夹/立柱固定适配板",
        "板材 x-min、y=0 中心线、板材 z-min",
        "含当前竖直网夹/立柱的安装孔位；采购 13 mm 球头通过后盖 boss 和 90° 支撑连接，不把球头本体当作加工件。商品网夹接口仍待实测。",
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
        "material": "6061-T6 aluminum; finish TBD",
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
        "status": "机加工/报价预览；不是最终放行图",
        "source": "hardware/cad/net_stand.scad",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "units": "mm",
        "material": "6061-T6 aluminum; finish TBD",
        "quantity": {
            "detector_bodies": 2,
            "support_brackets": 2,
            "net_clamp_adapters": 2,
            "purchased_ballheads": 2,
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
