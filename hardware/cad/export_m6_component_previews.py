#!/usr/bin/env python3
"""Export the current M6 detector components as a reproducible side package.

This auxiliary package keeps the PETG first-article body/covers visible as
independent, whole components.  The rectangular body is intentionally also
CNC-compatible later; the purchased 13 mm ballhead and fasteners remain
assembly interfaces rather than exported print parts.
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
DEFAULT_OUTPUT = HERE / "exports" / "net-stand-v0.1" / "m6-component-previews"
SCHEMA_VERSION = "m6-component-previews-0.3-20-mm-pitch-petg-body-rear-face-boss"


@dataclass(frozen=True)
class ComponentSpec:
    part: str
    stem: str
    name_zh: str
    component_kind: str
    material: str
    preview_is_printable: bool
    orientation: str
    coordinate_frame: str
    notes: str


COMPONENTS = (
    ComponentSpec(
        "m6_detector_body",
        "m6-detector-body",
        "M6 十路传感器主体（PETG 长方条；后续可换 CNC）",
        "PETG 可打印首样 / 后续 CNC 兼容",
        "PETG first article; future CNC-compatible 6061-T6 option",
        True,
        "保持 OpenSCAD 全局姿态；x 为光束方向，y 为球台前后，z 为竖直",
        "OpenSCAD 全局坐标；不做局部平移",
        "主体就是 10×56×216 mm 的连续矩形长条；含十路 20 mm 节距光学孔、浅 AF8 防转窝、盖件固定孔和 y± 边槽。主体不再带 T 尾座、M8 孔或独立线缆槽；云台接口位于后盖 x 背面中央 boss，首样确认后可按同一包络改 CNC。",
    ),
    ComponentSpec(
        "m6_detector_shell_front",
        "m6-detector-front-cover",
        "M6 光学端前盖",
        "PETG 打印候选",
        "PETG; print orientation and wall count TBD",
        True,
        "z+ 套入；x- 光学端正球弧朝外",
        "OpenSCAD 全局坐标；与主体装配基准一致",
        "加大后的 x- 前盖 bulkhead 只保留十个光学通孔；真实 AF8 六角、蓝色护套、线缆和一枚原配螺帽均收在壳内，不把前盖作为传感器或球头承力件。",
    ),
    ComponentSpec(
        "m6_detector_shell_rear",
        "m6-detector-rear-cover",
        "M6 线缆端后盖",
        "PETG 打印候选",
        "PETG; print orientation and wall count TBD",
        True,
        "z+ 套入；x+ 线缆端圆角矩形朝外",
        "OpenSCAD 全局坐标；与主体装配基准一致",
        "后盖与前盖共用 y± 连续侧槽的 x+ 半段；x+ 背面中央在 y=0、z 中心适当增厚形成 PETG 支撑 boss，开 x 向 Ø7.0 1/4-20 通孔并内藏标准捕获螺母，供采购球头固定上端连接；左侧件按 x 镜像。采购球头保持竖直，选定的下端 M8 外牙 z− 直接落在浅黄色直立下段顶面的同轴 M8 捕获螺母；检测器/球头总成沿 x 移到立柱中心，取消横向黄色承托臂，当前装配移除深黄色上段和深灰色独立连接器，首样需用实物复核 boss、承座和球头的承力与耐久。",
    ),
    ComponentSpec(
        "m6_detector_bottom_cover",
        "m6-detector-bottom-cover",
        "M6 底盖",
        "PETG 打印候选",
        "PETG; print orientation and wall count TBD",
        True,
        "z- 独立盖合；与壳体俯视轮廓一致",
        "OpenSCAD 全局坐标；与主体装配基准一致",
        "独立平板按前后壳组合轮廓封闭底部，含两枚沉头固定孔和约 Ø12 mm 统一线缆套管开放孔；不做密封承诺。",
    ),
)


def _round(value: float) -> float | int:
    rounded = round(float(value), 4)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def _run_export(
    openscad: str,
    output: Path,
    spec: ComponentSpec,
    side: str,
    side_value: int,
) -> None:
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


def _manifest_entry(
    output: Path,
    spec: ComponentSpec,
    side: str,
    side_value: int,
) -> dict[str, object]:
    closed, topology_summary = _stl_topology(output)
    if not closed:
        raise RuntimeError(f"M6 组件不是封闭 STL: {output.name}: {topology_summary}")
    volume_mm3 = _stl_volume(output)
    if volume_mm3 <= 1e-6:
        raise RuntimeError(f"M6 组件体积无效: {output.name}: {volume_mm3}")
    min_x, max_x, min_y, max_y, min_z, max_z = stl_bounds(output)
    return {
        "file": output.name,
        "part": spec.part,
        "name_zh": f"{spec.name_zh}（{'右' if side == 'right' else '左'}）",
        "component_kind": spec.component_kind,
        "printable": spec.preview_is_printable,
        "preview_is_printable": spec.preview_is_printable,
        "in_formal_print_manifest": False,
        "definitions": [f'PART="{spec.part}"', f"SIDE={side_value}"],
        "side": side,
        "side_value": side_value,
        "units": "mm",
        "material": spec.material,
        "orientation": spec.orientation,
        "coordinate_frame": spec.coordinate_frame,
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


def export_component_previews(
    openscad: str,
    output_dir: Path,
    *,
    clean: bool = False,
) -> dict[str, object]:
    """Export both mirror sides of each current M6 component."""

    output_dir.mkdir(parents=True, exist_ok=True)
    expected = {
        f"{side}-{spec.stem}.stl"
        for side, _ in (("right", 1), ("left", -1))
        for spec in COMPONENTS
    }
    stale = _stale_stl_files(output_dir, expected)
    if stale and not clean:
        names = ", ".join(path.name for path in stale)
        raise RuntimeError(
            f"M6 组件预览目录存在旧 STL：{names}；需要显式传 --clean 才会清理"
        )
    if clean:
        for path in stale:
            path.unlink()

    entries: list[dict[str, object]] = []
    for side, side_value in (("right", 1), ("left", -1)):
        for spec in COMPONENTS:
            output = output_dir / f"{side}-{spec.stem}.stl"
            _run_export(openscad, output, spec, side, side_value)
            entries.append(_manifest_entry(output, spec, side, side_value))

    manifest: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "status": "M6 当前独立组件预览；PETG 盖件待首样复核，金属件不得混入正式打印清单",
        "source": "hardware/cad/net_stand.scad",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "units": "mm",
        "coordinate_system": {
            "x": "beam direction; left emitter exits +x, right receiver aperture faces -x",
        "y": "table front/rear direction; rear-cover support boss is centered at y=0",
            "z": "vertical direction",
            "side_files": "right=SIDE 1, left=SIDE -1; left is the x mirror of right",
            "frame": "entries remain in global OpenSCAD coordinates so they align with assembly and machining spec",
        },
        "quantity": {
            "sides": 2,
            "component_types": len(COMPONENTS),
            "stl_files": len(entries),
            "purchased_ballheads_per_side": 1,
            "petg_print_candidates_per_side": 4,
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
        help="输出 Git 忽略的 M6 独立组件预览目录",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="只清理本目录中不属于当前组件清单的旧 STL",
    )
    args = parser.parse_args()
    manifest = export_component_previews(
        find_openscad(), args.output_dir.resolve(), clean=args.clean
    )
    print(
        "M6_COMPONENT_PREVIEWS_OK "
        f"(parts={len(manifest['parts'])}, output={args.output_dir.resolve()})"
    )


if __name__ == "__main__":
    main()
