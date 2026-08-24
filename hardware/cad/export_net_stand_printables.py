#!/usr/bin/env python3
"""Export the independent first-print parts from the current net-stand source.

The generated STL files and manifest are local artifacts under
``hardware/cad/exports/``.  This script intentionally does not delete old
files: rerunning it overwrites only the explicitly generated filenames.
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
DEFAULT_OUTPUT = HERE / "exports" / "net-stand-v0.1"


@dataclass(frozen=True)
class ExportSpec:
    filename: str
    part: str
    definitions: tuple[str, ...]
    side: str | None
    side_value: int | None
    index: int | None
    material: str
    orientation: str
    notes: str


def _side_specs(
    part: str,
    stem: str,
    material: str,
    orientation: str,
    notes: str,
) -> list[ExportSpec]:
    specs: list[ExportSpec] = []
    for label, value in (("right", 1), ("left", -1)):
        specs.append(
            ExportSpec(
                filename=f"{label}-{stem}.stl",
                part=part,
                definitions=(f'PART="{part}"', f"SIDE={value}"),
                side=label,
                side_value=value,
                index=None,
                material=material,
                orientation=orientation,
                notes=notes,
            )
        )
    return specs


def _indexed_side_specs(
    part: str,
    stem: str,
    indices: range,
    material: str,
    orientation: str,
    notes: str,
) -> list[ExportSpec]:
    specs: list[ExportSpec] = []
    for label, value in (("right", 1), ("left", -1)):
        for index in indices:
            specs.append(
                ExportSpec(
                    filename=f"{label}-{stem}-{index}.stl",
                    part=part,
                    definitions=(
                        f'PART="{part}"',
                        f"SIDE={value}",
                        f"optical_module_index={index}",
                    ),
                    side=label,
                    side_value=value,
                    index=index,
                    material=material,
                    orientation=orientation,
                    notes=notes,
                )
            )
    return specs


def _indexed_post_specs() -> list[ExportSpec]:
    specs: list[ExportSpec] = []
    for label, value in (("right", 1), ("left", -1)):
        for index in range(2):
            specs.append(
                ExportSpec(
                    filename=f"{label}-post-segment-{index}.stl",
                    part="post_segment",
                    definitions=(
                        'PART="post_segment"',
                        f"SIDE={value}",
                        f"post_segment_index={index}",
                    ),
                    side=label,
                    side_value=value,
                    index=index,
                    material="PETG",
                    orientation="底面朝下；接缝方向沿 Z 轴，切片时保留外壁和局部加厚。",
                    notes="两段立柱之一；必须与同侧套筒和内芯配合，不把 post 装配预览直接切片。",
                )
            )
    return specs


def _indexed_rail_specs() -> list[ExportSpec]:
    specs: list[ExportSpec] = []
    for part, stem, count, notes in (
        (
            "net_rail_segment",
            "net-rail-segment",
            3,
            "网顶承载条单段；相邻段搭接 20 mm，并用拼接片锁紧。",
        ),
        (
            "net_rail_splice",
            "net-rail-splice",
            2,
            "网顶承载条接缝拼接片；M3 螺钉和螺母为标准件。",
        ),
    ):
        for index in range(count):
            definition_name = (
                "rail_segment_index"
                if part == "net_rail_segment"
                else "rail_splice_index"
            )
            specs.append(
                ExportSpec(
                    filename=f"{stem}-{index}.stl",
                    part=part,
                    definitions=(f'PART="{part}"', f"{definition_name}={index}"),
                    side=None,
                    side_value=None,
                    index=index,
                    material="PETG",
                    orientation="大平面朝下；长件按打印机尺寸和翘曲风险在切片器中复核。",
                    notes=notes,
                )
            )
    return specs


def build_export_specs() -> list[ExportSpec]:
    specs = _indexed_post_specs()
    specs.extend(
        _side_specs(
            "post_joint_sleeve",
            "post-joint-sleeve",
            "PETG",
            "套筒开口朝上；按实际插接间隙复核，不强压进立柱。",
            "立柱两段接缝外套筒。",
        )
    )
    specs.extend(
        _side_specs(
            "post_joint_key",
            "post-joint-key",
            "PETG",
            "最大平面朝下；装配前检查与套筒的滑动间隙。",
            "立柱两段接缝内芯/防转键。",
        )
    )
    specs.extend(
        _side_specs(
            "table_clamp_body",
            "table-clamp-body",
            "PETG",
            "C 形开口朝外；上夹板和下臂按层间强度方向切片。",
            "传统桌下 C 形夹固定体；不打孔、不穿透台面。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_pressure_pad",
            "clamp-pressure-pad",
            "TPU/硅胶优先，PETG 仅作几何样件",
            "接触台底的一面朝上；实际软垫材料需要单独确认。",
            "独立台底压块/软垫占位；M8 圆头螺杆只顶它的下侧。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_knob",
            "clamp-knob",
            "PETG",
            "旋钮平面朝下；六角螺母捕获窝朝上。",
            "打印旋钮；必须装入标准 M8 捕获螺母，不使用 PETG 内螺纹。",
        )
    )
    specs.extend(_indexed_rail_specs())
    specs.extend(
        _side_specs(
            "net_rail_saddle",
            "net-rail-saddle",
            "PETG",
            "承托平面朝上；端挡朝外。",
            "立柱内侧网顶承托/端部限位座。",
        )
    )
    specs.extend(
        _side_specs(
            "optical_rail",
            "optical-rail",
            "PETG",
            "导轨基面朝下；定位孔和刻度朝外可见。",
            "单侧 10 路光学模块导轨；真实光学件不在 STL 内。",
        )
    )
    specs.extend(
        _indexed_side_specs(
            "optical_module_carrier",
            "optical-module-carrier",
            range(10),
            "PETG",
            "U 形开口朝上；长孔方向按实物模块调节方向复核。",
            "单个 +10…+100 mm 光学模块载台；M3 紧固件和收发器为标准/外购件。",
        )
    )
    specs.extend(
        _side_specs(
            "sensor_mount_body",
            "sensor-mount-body",
            "PETG",
            "安装座底面朝下；薄膜和压片不可与本体合并打印。",
            "网顶 PVDF 安装座本体；sensor_mount 只保留为组合预览。",
        )
    )
    specs.extend(
        _side_specs(
            "sensor_clamp_lip",
            "sensor-clamp-lip",
            "PETG/TPU 试样",
            "压片平面朝下；同一 STL 含左右两枚可拆压片。",
            "夹持 PVDF 薄膜两侧的可拆压片。",
        )
    )
    specs.extend(
        _side_specs(
            "reference_carriage_body",
            "reference-carriage-body",
            "PETG",
            "端座底面朝下；定位销另用标准件安装。",
            "参考线端座本体；reference_carriage 只保留为端座+定位销装配预览。",
        )
    )
    specs.append(
        ExportSpec(
            filename="calibration-gauge.stl",
            part="calibration_gauge",
            definitions=('PART="calibration_gauge"',),
            side=None,
            side_value=None,
            index=None,
            material="PETG",
            orientation="底面朝下；刻度面朝上。",
            notes="共享的 +10…+100 mm 高度档位标定规。",
        )
    )
    return specs


EXPORT_SPECS = build_export_specs()


def _run_export(openscad: str, output: Path, spec: ExportSpec) -> None:
    command = [openscad, "-o", str(output)]
    for definition in spec.definitions:
        command.extend(["-D", definition])
    command.append(str(SOURCE))
    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"OpenSCAD 导出失败: {spec.filename} ({spec.definitions})\n{result.stdout}"
        )
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"OpenSCAD 没有生成 STL: {spec.filename}")


def _manifest_entry(output: Path, spec: ExportSpec) -> dict[str, object]:
    closed, topology_summary = _stl_topology(output)
    if not closed:
        raise RuntimeError(
            f"打印件不是封闭 STL: {spec.filename}: {topology_summary}"
        )
    min_x, max_x, min_y, max_y, min_z, max_z = stl_bounds(output)
    return {
        "file": output.name,
        "part": spec.part,
        "definitions": list(spec.definitions),
        "side": spec.side,
        "side_value": spec.side_value,
        "index": spec.index,
        "units": "mm",
        "material": spec.material,
        "orientation": spec.orientation,
        "notes": spec.notes,
        "bounds": {
            "min": [min_x, min_y, min_z],
            "max": [max_x, max_y, max_z],
            "size": [max_x - min_x, max_y - min_y, max_z - min_z],
        },
        "topology": {
            "watertight_by_edge_topology": closed,
            "summary": topology_summary,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="生成 STL 和 manifest.json 的目录（默认位于 Git 忽略的 exports/ 下）",
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    openscad = find_openscad()
    entries: list[dict[str, object]] = []
    for number, spec in enumerate(EXPORT_SPECS, start=1):
        output = output_dir / spec.filename
        _run_export(openscad, output, spec)
        entries.append(_manifest_entry(output, spec))
        print(f"[{number:02d}/{len(EXPORT_SPECS):02d}] {spec.filename}")

    manifest = {
        "schema_version": "0.1",
        "design": "net-stand-v0.1",
        "source": str(SOURCE.relative_to(HERE.parent.parent)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "units": "mm",
        "install_model": "整体替换式球网支架；两侧传统桌下 C 形夹，免打孔。",
        "print_process": "FDM 首样；材料、喷嘴、层高、支撑和壁厚仍需按实物/切片器复核。",
        "preview_parts_excluded": [
            "assembly",
            "left_stand",
            "right_stand",
            "post",
            "table_clamp",
            "net_rail",
            "optical_strip",
            "sensor_mount",
            "reference_carriage",
        ],
        "parts": entries,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"PRINT_PACKAGE_OK ({len(entries)} STL, manifest={manifest_path})")


if __name__ == "__main__":
    main()
