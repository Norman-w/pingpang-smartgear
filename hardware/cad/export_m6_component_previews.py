#!/usr/bin/env python3
"""Export the current M6 detector components as a reproducible side package.

This auxiliary package keeps the aluminum machining parts and PETG cover
candidates visible as independent, whole components.  It is intentionally
separate from the 26-piece PETG print manifest: the body, support and adapter
are metal parts, while the three covers are printable candidates that still
need first-article fit confirmation.
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
SCHEMA_VERSION = "m6-component-previews-0.1-20-mm-pitch-t-tail"


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
        "M6 十路传感器主体（一体 T 形尾座）",
        "铝合金机加工件预览",
        "6061-T6 aluminum; finish TBD",
        False,
        "保持 OpenSCAD 全局姿态；x 为光束方向，y 为球台前后，z 为竖直",
        "OpenSCAD 全局坐标；不做局部平移",
        "中央长条 10×56×216 mm，y- 一体 T 尾座向本侧 x 外伸 10 mm；含十路 20 mm 节距光学孔、浅 AF8 防转窝、盖件固定孔、边槽和直接 M8×1.25 内丝的 Ø6.8 攻牙底孔/入口沉台。真实螺旋牙由加工方攻制。",
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
        "后盖与前盖共用 y± 连续侧槽的 x+ 半段，并对 y- 一体铝合金 T 尾座做净空让位；沉头螺丝只固定壳体，PETG 不承受 M8 球头弯矩。",
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
    ComponentSpec(
        "m6_detector_support",
        "m6-90-degree-support",
        "M6 90°金属支撑件",
        "金属机加工/折弯件预览",
        "6061-T6 aluminum or equivalent metal; process TBD",
        False,
        "保持竖直姿态；水平臂接球头，竖直腿接网夹适配板",
        "OpenSCAD 全局坐标；不做局部平移",
        "水平承托臂、竖直连接腿和夹具下方两侧三角加固肋组成完整金属承力件；球头、紧固件和网夹适配板不并入本 STL。",
    ),
    ComponentSpec(
        "m6_mount_adapter",
        "m6-net-clamp-adapter",
        "M6 竖直网夹/立柱适配板",
        "铝合金机加工件预览",
        "6061-T6 aluminum; finish TBD",
        False,
        "竖直安装；板面承接金属支撑腿和网夹接口",
        "OpenSCAD 全局坐标；不做局部平移",
        "保持当前竖直网夹适配板孔位，作为金属 90°支撑到网架的接口；商品网夹外伸、孔距和垫片叠层仍需实测。",
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
            "y": "table front/rear direction; integral T-tail is on y-",
            "z": "vertical direction",
            "side_files": "right=SIDE 1, left=SIDE -1; left is the x mirror of right",
            "frame": "entries remain in global OpenSCAD coordinates so they align with assembly and machining spec",
        },
        "quantity": {
            "sides": 2,
            "component_types": len(COMPONENTS),
            "stl_files": len(entries),
            "metal_parts_per_side": 3,
            "petg_cover_candidates_per_side": 3,
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
