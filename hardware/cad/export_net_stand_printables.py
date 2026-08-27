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

from validate_net_stand import _stl_topology, _stl_volume
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
    "stg120_outer_carrier": "STG-120ML 外侧光纤头托架",
    "stg120_center_bridge": "STG-120ML 中央背靠背支撑桥",
    "sensor_mount_body": "PVDF 网顶传感器座",
    "sensor_clamp_lip": "PVDF 薄膜压片",
    "reference_carriage_body": "参考线端座",
    "calibration_gauge": "过网高度标定规",
    "net_clamp_rod": "U 槽卡网圆柱",
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
        "id": "net-clamp-rods",
        "name_zh": "U 槽卡网圆柱（PETG 打印）",
        "name_en": "printed PETG net-retention rods",
        "kind": "卡网结构件",
        "status": "PETG 打印件 / 非采购件",
        "printable": True,
        "quantity": "2 根（左右各 1）",
        "scad_part": "net_clamp_rod",
        "notes": "网布从立柱外侧塞入 U 形槽后，圆柱沿 x 推入锁住；Ø14 mm 只作干涉校核，实际打印圆柱为 Ø12 mm，直径小 2 mm。",
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
        "id": "m6-optical-devices",
        "name_zh": "M6 光电发射/接收器",
        "name_en": "M6 optical emitter/receiver devices",
        "kind": "光学器件",
        "status": "外购 / 用户选定 SKU 6122579349941 / 型号映射与尺寸待实测",
        "printable": False,
        "quantity": "20 枚（左右各 10）",
        "scad_part": "m6_sensor_array",
        "notes": "用户选定商品 SKU 6122579349941（M6 直角对射、NPN、0–20 m）；图片中的 VJTL06-20NZ/N3 只作型号映射候选。对射尺寸图记录 M6×0.75、头部约 8 mm、安装杆包络约 14 mm；同图反射条目 M6×0.5 不适用于当前主线。左右各 10 枚构成 10 对，卖家仍需确认实际后缀和接收输出数量。",
    },
    {
        "id": "m6-petg-detector-bodies",
        "name_zh": "M6 直角十路 PETG 长条主体",
        "name_en": "M6 right-angle ten-channel PETG detector bodies",
        "kind": "首样打印光学基座",
        "status": "PETG 首样 / 后续可 CNC / 待实物量测",
        "printable": True,
        "quantity": "2 根（左右各 1）",
        "scad_part": "m6_detector_body",
        "notes": "主体保持 10×56×216 mm 简单矩形，十路按 20 mm 单列排列，M6 中空外丝沿 x 贯穿；不带 T 尾座、不挖主体线缆槽。后盖 x 背面中央另设 y=0、z 中心加厚 1/4-20 boss，前后盖和底盖由 M6 组件预览包独立导出。",
    },
    {
        "id": "m6-purchased-ballhead",
        "name_zh": "13 mm 采购球头万向支撑件",
        "name_en": "purchased 13 mm ballhead/gimbal support",
        "kind": "外购光学承力接口",
        "status": "外购 / 当前默认 M8 外牙 / 待网夹接口量测",
        "printable": False,
        "quantity": "2 套（左右各 1）",
        "scad_part": "m6_ballhead",
        "notes": "默认采购 13mm球【M8外牙】；球头保持竖直，商品固定上端 1/4-20 外牙从各自 x 后端进入背面中央加厚 boss，选定下端 M8 外牙 z− 接口直接拧入浅黄色下段的一体 M8 捕获螺母。偏航、俯仰、旋转微调依靠采购球头锁紧机构；当前装配不再使用深灰色 90°连接器或深黄色上段立柱。",
    },
    {
        "id": "m6-ballhead-variants",
        "name_zh": "13 mm 球头螺纹选项",
        "name_en": "13 mm ballhead thread variants",
        "kind": "外购标准件",
        "status": "按采购 SKU 选择 / M8 外牙为当前模型默认",
        "printable": False,
        "quantity": "按两套基座",
        "scad_part": "m6_ballhead",
        "notes": "保留 1/4 内牙、1/4 外牙、3/8 外牙、M6 外牙、M8 外牙、M10 外牙选项；实际螺纹有效长度、旋钮净空、网夹孔位和防松方式按到货件确认。",
    },
    {
        "id": "m3-hardware",
        "name_zh": "M3 紧固件",
        "name_en": "M3 fasteners",
        "kind": "外购标准件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "按装配",
        "scad_part": "net_rail_splice",
        "notes": "用于网顶拼接片；M6 光学基座是铝合金机加工件，不把 M3 孔位写入当前打印包。",
    },
    {
        "id": "table-top-rubber",
        "name_zh": "台面上侧胶皮（现场粘贴）",
        "name_en": "glued tabletop rubber pads",
        "kind": "软质接触件",
        "status": "外购胶皮 / 现场粘贴 / 非打印",
        "printable": False,
        "quantity": "2 片",
        "scad_part": "clamp_top_pad",
        "notes": "粘贴在固定上夹板与台面接触的下表面，用于防滑和保护台面；OpenSCAD 保留 clamp_top_pad 作为装配占位，但不进入正式打印清单。",
    },
    {
        "id": "table-bottom-pressure-pads",
        "name_zh": "台底圆盘压块",
        "name_en": "round underside pressure pads",
        "kind": "夹紧结构件",
        "status": "PETG 打印件（可选粘薄胶皮）",
        "printable": True,
        "quantity": "2 件",
        "scad_part": "clamp_pressure_pad",
        "notes": "顶面为平盘，接触台面底面；底面中央有浅 M8 圆头收纳窝，螺杆从下方顶入。它不是软垫，首样按刚性 PETG 小底盘打印；若需要可在顶面另贴薄胶皮。",
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
    # The former dark-yellow upper post was removed from the active design.
    # Keep this helper as an explicit empty compatibility boundary so old
    # callers do not accidentally reintroduce a standalone upper segment into
    # the current print package.
    return []


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
    specs: list[ExportSpec] = []
    specs.extend(
        _side_specs(
            "lower_stand_segment",
            "lower-stand-segment",
            "PETG",
            "底面朝下；下段立柱与 C 形夹已经一体化，接缝方向沿 Z 轴。",
            "首样左右各一件；包含浅黄色下段、固定 C 形夹和一体 M8 球头承座，蓝色检测器总成直接拧入此承座；桌面夹持开口、压块和螺杆区域保留，灰色夹体外侧下部沿 y 全深为实心渐变支撑，靠台侧厚 40 mm、外侧 12 mm；上下夹持舌头各向台内延长 20 mm，台下有效伸入为 82 mm，压紧件位于下舌头中点，台底压紧盘为 Ø50 mm；M8 夹紧丝杆相对原包络加长 12 mm；不再拆分深黄色上段或深灰色连接器。",
        )
    )
    specs.extend(
        _side_specs(
            "net_clamp_rod",
            "net-clamp-rod",
            "PETG",
            "圆柱轴沿 Z；底端朝下；装配时从立柱外侧沿 x 推入 U 槽。",
            "独立 PETG 卡网圆柱；实际打印 Ø12 mm。Ø14 mm 只作为 U 槽干涉校核基准；网布先塞入外侧开口，再沿 x 推入圆柱锁住。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_pressure_pad",
            "clamp-pressure-pad",
            "PETG",
            "平盘顶面朝上；底面 M8 圆头收纳窝朝下；圆盘平面贴打印床。",
            "独立台底 Ø50 mm 刚性圆盘压块；位于下舌头台下有效区段中点，顶面接触台底，底面浅窝容纳并约束 M8 圆头螺杆；可选在顶面另贴薄胶皮。",
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
            notes="共享的 STG-120ML 32 点 / 3.87 mm 间距标定规；用于核对光纤头有效检测面和两段窗口，不代表放大器已经提供逐点输出。",
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
    volume_mm3 = _stl_volume(output)
    if volume_mm3 <= 1e-6:
        raise RuntimeError(f"打印件体积无效: {spec.filename}: {volume_mm3}")
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
        "volume_mm3": volume_mm3,
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
        help="仅清理输出目录中不属于当前打印清单的旧 STL；不会删除其它文件",
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
            "stg120_preview",
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
