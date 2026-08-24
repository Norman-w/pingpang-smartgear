#!/usr/bin/env python3
"""Export the independent first-print parts from the current net-stand source.

The generated STL files and manifest are local artifacts under
``hardware/cad/exports/``.  A dedicated export directory must not silently
contain parts from an older design: stale STL files cause the exporter to
fail unless the caller explicitly supplies ``--clean``.
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


PART_NAMES_ZH = {
    "post_segment": "立柱上段",
    "lower_stand_segment": "立柱下段 + 桌下夹体",
    "post_joint_sleeve": "立柱接缝外套筒",
    "post_joint_key": "立柱接缝防转内芯",
    "clamp_top_pad": "台面保护软垫",
    "clamp_pressure_pad": "台底可动压块",
    "clamp_knob": "夹紧手拧旋钮",
    "net_rail_segment": "网顶承载条",
    "net_rail_splice": "网顶承载条拼接片",
    "net_rail_saddle": "网顶承托座",
    "optical_rail": "红外光栅导轨",
    "optical_module_carrier": "光栅光学模块载台",
    "sensor_mount_body": "PVDF 网顶传感器座",
    "sensor_clamp_lip": "PVDF 薄膜压片",
    "reference_carriage_body": "参考线端座",
    "calibration_gauge": "过网高度标定规",
}


def material_group_for(material: str) -> str:
    """Return the print-bed material group for a printable part.

    A part that may be printed in TPU (or replaced by silicone) is deliberately
    kept out of the PETG platter.  This also treats ``PETG/TPU 试样`` as a
    flexible-material sample so a mixed-material decision cannot accidentally
    become a mixed platter.
    """
    normalized = str(material).upper()
    if "TPU" in normalized or "硅胶" in str(material):
        return "TPU/柔性"
    return "PETG"


def part_name_zh(part: str, side: str | None = None, index: int | None = None) -> str:
    base = PART_NAMES_ZH.get(part, part)
    if part == "net_rail_segment" and index is not None:
        base = f"{base}第 {index + 1} 段"
    elif part == "net_rail_splice" and index is not None:
        base = f"{base}第 {index + 1} 片"
    elif part == "optical_module_carrier" and index is not None:
        base = f"{base} +{10 + index * 10} mm"
    if side:
        base = f"{base}（{'右' if side == 'right' else '左'}）"
    return base


ASSEMBLY_COMPONENTS = [
    {
        "id": "m8-threaded-rod",
        "name_zh": "M8×1.25 金属螺杆",
        "name_en": "M8 × 1.25 threaded rod",
        "kind": "外购标准件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "2 根",
        "scad_part": "clamp_screw",
        "notes": "装配预览中显示圆头占位；实际使用金属螺杆，不打印螺纹。",
    },
    {
        "id": "m8-fixed-nut",
        "name_zh": "M8 六角螺母（下臂固定）",
        "name_en": "M8 fixed nut",
        "kind": "外购标准件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "2 枚",
        "scad_part": "clamp_body_nut",
        "notes": "安装在 C 形夹下臂的捕获窝中，形成固定螺纹。",
    },
    {
        "id": "m8-jam-nuts",
        "name_zh": "M8 六角螺母（旋钮对锁）",
        "name_en": "M8 jam-nut pair",
        "kind": "外购标准件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "4 枚",
        "scad_part": "clamp_knob_nut",
        "notes": "每侧两枚预先对锁，装入打印旋钮的六角捕获窝。",
    },
    {
        "id": "net-fabric",
        "name_zh": "乒乓球网布",
        "name_en": "table-tennis net fabric",
        "kind": "装配件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "1 套",
        "scad_part": "net",
        "notes": "固定在三段网顶承载条与两侧立柱之间。",
    },
    {
        "id": "pvdf-film",
        "name_zh": "PVDF 压电薄膜",
        "name_en": "PVDF piezo film",
        "kind": "传感器件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "2 片",
        "scad_part": "pvdf_film",
        "notes": "夹在网顶白边的左右两个可拆传感器座中。",
    },
    {
        "id": "optical-modules",
        "name_zh": "调制红外发射 / 接收模块",
        "name_en": "modulated IR emitter / receiver modules",
        "kind": "光学器件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "10 对",
        "scad_part": "optical_strip",
        "notes": "装入两侧导轨的对应高度载台，真实型号和光轴仍需实测。",
    },
    {
        "id": "reference-pins",
        "name_zh": "Ø3 弹簧定位销",
        "name_en": "spring locating pins",
        "kind": "外购标准件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "2 枚",
        "scad_part": "reference_pin",
        "notes": "锁定参考线端座和 10 mm 光栅孔位。",
    },
    {
        "id": "m3-hardware",
        "name_zh": "M3 紧固件",
        "name_en": "M3 fasteners",
        "kind": "外购标准件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "按装配",
        "scad_part": "net_rail_splice / optical_module_carrier",
        "notes": "用于网顶拼接片、光学载台和传感器压片的锁紧。",
    },
    {
        "id": "contact-pads",
        "name_zh": "桌面 / 台底保护软垫",
        "name_en": "table contact pads",
        "kind": "软质接触件",
        "status": "TPU 打印样件或硅胶片",
        "printable": True,
        "quantity": "4 片",
        "scad_part": "clamp_top_pad / clamp_pressure_pad",
        "notes": "首样优先用 TPU 或现成硅胶片；PETG 只用于尺寸样件。",
    },
]


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
        # index=0 is exported as lower_stand_segment below so the first-print
        # lower upright and its C clamp are one physically assembleable part.
        for index in (1,):
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
            "lower_stand_segment",
            "lower-stand-segment",
            "PETG",
            "底面朝下；下段立柱与 C 形夹已经一体化，接缝方向沿 Z 轴。",
            "首样左右各一件；包含 post_segment_index=0 与固定 C 形夹，避免分件相互干涉。",
        )
    )
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
            "clamp_top_pad",
            "clamp-top-pad",
            "TPU/硅胶优先",
            "接触桌面的一面朝下；也可用同厚度硅胶片替代。",
            "固定上夹板与桌面之间的可替换保护垫；不承担 C 形夹结构力路。",
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
            "打印旋钮；必须装入预先对锁的两枚标准 M8 螺母，不使用 PETG 内螺纹。",
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
        "name_zh": part_name_zh(spec.part, spec.side, spec.index),
        "name_en": spec.part,
        "component_kind": "打印件",
        "printable": True,
        "definitions": list(spec.definitions),
        "side": spec.side,
        "side_value": spec.side_value,
        "index": spec.index,
        "units": "mm",
        "material": spec.material,
        "material_group": material_group_for(spec.material),
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


def _stale_stl_files(output_dir: Path) -> list[Path]:
    expected = {spec.filename for spec in EXPORT_SPECS}
    return sorted(
        (path for path in output_dir.glob("*.stl") if path.name not in expected),
        key=lambda path: path.name,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="生成 STL 和 manifest.json 的目录（默认位于 Git 忽略的 exports/ 下）",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="仅清理输出目录中不属于当前 50 件清单的旧 STL；不会删除其它文件",
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    stale_files = _stale_stl_files(output_dir)
    if stale_files and not args.clean:
        names = ", ".join(path.name for path in stale_files)
        raise RuntimeError(
            "输出目录包含不属于当前打印清单的旧 STL："
            f" {names}；如确认这些是旧生成物，请重新运行并加 --clean"
        )
    for stale_file in stale_files:
        stale_file.unlink()
        print(f"CLEANED_STALE_STL {stale_file.name}")

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
        "material_groups": ["PETG", "TPU/柔性"],
        "material_policy": "不同 material_group 不进入同一张打印拼盘；TPU/硅胶优先件单独排入柔性材料盘。",
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
        "assembly_components": ASSEMBLY_COMPONENTS,
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
