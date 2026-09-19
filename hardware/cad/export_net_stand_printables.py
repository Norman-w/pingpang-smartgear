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
# The split C-clamp is the current printable source line.  Older output
# directories remain historical evidence and are never silently reused.
DEFAULT_OUTPUT = HERE / "exports" / "desktop-clamp-one-side-x1c-v0.7-split-c-scheme"


PART_NAMES_ZH = {
    "post_segment": "整根立柱（兼容诊断名）",
    "post_clamp_carrier": "整根立柱 + SKP C 方案整体底座",
    "lower_stand_segment": "整根立柱（兼容诊断名）",
    "clamp_body_half_user": "C 形夹操作者侧半体（y-）",
    "clamp_body_half_opponent": "C 形夹对手侧半体（y+）",
    "upper_stand_segment": "整根立柱（兼容诊断名）",
    "post_joint_sleeve": "旧版立柱接缝诊断件",
    "post_joint_key": "旧版立柱接缝诊断件",
    "clamp_top_pad": "台面保护软垫",
    "clamp_pressure_pad": "台底可动压块",
    "clamp_pressure_pad_guard": "台底压块扁球头防丢背护罩",
    "clamp_printed_screw": "PETG 粗牙扁球头夹紧螺杆",
    "clamp_body_nut": "PETG 粗牙固定螺母",
    "clamp_knob": "夹紧手拧旋钮",
    "clamp_knob_nut": "PETG 粗牙旋钮对锁螺母",
    "net_rail_segment": "旧版网顶承载条（诊断件）",
    "net_rail_splice": "旧版网顶承载条拼接片（诊断件）",
    "net_rail_saddle": "旧版网顶承托座（诊断件）",
    "optical_rail": "红外光栅导轨",
    "optical_module_carrier": "光栅光学模块载台",
    "stg120_outer_carrier": "STG-120ML 外侧光纤头托架",
    "stg120_center_bridge": "STG-120ML 中央背靠背支撑桥",
    "sensor_mount_body": "PVDF 网顶传感器座",
    "sensor_clamp_lip": "PVDF 薄膜压片",
    "reference_carriage_body": "参考线端座",
    "calibration_gauge": "过网高度标定规",
    "net_clamp_clip": "全高 U 形滑入卡网夹",
    "net_clamp_rod": "旧版卡网圆柱（兼容诊断件）",
    "clamp_electronics_cover": "电子腔底盖",
    "clamp_electronics_gasket": "电子腔连续压紧垫",
    "clamp_electronics_ui_bezel": "交互面板压框",
    "m6_detector_body": "M6 十路主体",
    "m6_detector_shell_front": "M6 光学端前盖",
    "m6_detector_shell_rear": "M6 线缆端后盖",
    "m6_detector_bottom_cover": "M6 底盖",
    "m6_detector_bottom_gasket": "M6 底盖连续垫",
    "m6_detector_cable_gland": "M6 多孔压紧出线环",
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
        "id": "printed-coarse-thread-rods",
        "name_zh": "PETG 粗牙夹紧螺杆",
        "name_en": "PETG coarse-pitch clamp screws",
        "kind": "打印结构件",
        "status": "PETG 打印件 / 配套打印螺母",
        "printable": True,
        "quantity": "2 根（左右各 1）",
        "scad_part": "clamp_printed_screw",
        "notes": "12 mm 大径、9.6 mm 芯径、4 mm 螺距；牙根宽约 2 mm、凹槽宽约 2 mm，外侧 0.4 mm 锥尖收窄，采用连续锥形粗牙带而非平顶环带。顶部 15.5 mm 扁球头进入台底压块。不要与标准 M8×1.25 螺母混用。",
    },
    {
        "id": "printed-coarse-body-nuts",
        "name_zh": "PETG 粗牙固定螺母",
        "name_en": "PETG coarse fixed nuts",
        "kind": "打印结构件",
        "status": "PETG 打印件 / 下臂捕获",
        "printable": True,
        "quantity": "2 枚（左右各 1）",
        "scad_part": "clamp_body_nut",
        "notes": "AF16、11.5 mm 高、与 4 mm 螺距/2 mm 牙根/0.4 mm 锥尖粗牙螺杆配套；从下臂上侧装入 12 mm 深捕获窝，底部保留承力壁。",
    },
    {
        "id": "printed-coarse-drive-nuts",
        "name_zh": "PETG 粗牙旋钮对锁螺母",
        "name_en": "PETG coarse drive-nut pairs",
        "kind": "打印结构件",
        "status": "PETG 打印件 / 旋钮内捕获",
        "printable": True,
        "quantity": "4 枚（每侧两枚）",
        "scad_part": "clamp_knob_nut",
        "notes": "每侧两枚、每枚 6 mm 高，先对锁后装入旋钮 AF16 捕获窝；内螺纹与 2 mm 牙根/2 mm 凹槽/0.4 mm 锥尖粗牙配套，只与配套粗牙螺杆使用。",
    },
    {
        "id": "c-scheme-retaining-fasteners",
        "name_zh": "C 方案底座连接螺钉与螺母",
        "name_en": "C-scheme base retaining fasteners",
        "kind": "连接标准件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "4 套（每侧 2 套）",
        "scad_part": "post_skp_c_fasteners",
        "notes": "绿色整体底座沿 x 方向推入灰色 C 夹让位腔后，用两枚 M4 穿过灰色上夹板的 Ø4.4 mm 孔与绿色底座的 Ø4 mm 孔锁紧；螺钉承担防退出和接口夹紧，不把钢珠当作承力件。",
    },
    {
        "id": "c-clamp-split-fasteners",
        "name_zh": "C 形夹分型面 M5 螺钉与六角螺母",
        "name_en": "C-clamp split-plane M5 fasteners",
        "kind": "结构连接标准件",
        "status": "外购 / 非打印件",
        "printable": False,
        "quantity": "每只 C 夹 9 个连接位；左右共 18 个连接位（M5 螺钉/螺母各 18 枚）",
        "scad_part": "clamp_body_split_fasteners",
        "notes": "y=0 竖直分型面采用 9 处横向 M5：操作者侧半体做圆头沉孔，对手侧半体做防转六角螺母窝；只有贴到电子腔空腔边界的连接位增加 boss 柱和十字肋，完全位于实体夹臂里的连接位只保留孔位，避免外壳凸起。左下角连接孔已向外侧移动，电子仓左下角与右下斜加强边沿各补 1 处连接点；先装后侧六角螺母，再从 y- 侧拧入螺钉。",
    },
    {
        "id": "c-scheme-detent-hardware",
        "name_zh": "C 方案 4 mm 钢珠、弹簧与压盖",
        "name_en": "C-scheme 4 mm spring-ball detent",
        "kind": "连接定位标准件",
        "status": "外购 / 非打印",
        "printable": False,
        "quantity": "2 套（每侧 1 套）",
        "scad_part": "post_skp_c_detent_hardware",
        "notes": "灰色 C 夹从下方装入短弹簧和 4 mm 钢珠，绿色整体底座的 Ø6×2 mm 底坑在推到底时定位并给出终点手感；钢珠只负责定位，不承担主承力。",
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
        "notes": "无网顶轨道。装配时先从球台中心侧把网布端部穿过两侧立柱的 3 mm y 向过道，网布端止在立柱外侧面，再从桌外侧沿 x 滑入全高 U 形卡夹；拆卸反向操作。",
    },
    {
        "id": "net-clamp-clips",
        "name_zh": "全高 U 形滑入卡网夹（PETG 打印）",
        "name_en": "printed PETG full-height sliding U clips",
        "kind": "卡网结构件",
        "status": "PETG 打印件 / 非采购件",
        "printable": True,
        "quantity": "2 件（左右各 1）",
        "scad_part": "net_clamp_clip",
        "notes": "先穿网，再从桌外侧沿 x 向球台中心滑入；两片 jaw 的名义间隙 1.8 mm，夹住 1.2 mm 网布，外侧横梁在立柱外面止挡。网布张力和绳的拉力负责把卡夹压在承托面上；立柱内嵌的一处被动止挡只防止卡夹向外拔出，不承担主拉力。卡夹正侧 jaw 自带一体弹性扣舌，斜面允许装入、闭合肩阻止反向脱出；按开对应 jaw 后即可解锁反向滑出。无穿钉、横向销钉或网夹螺钉。平放打印后沿 z 立起安装。",
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
        "notes": "默认采购 13mm球头【M8外牙】；球头保持竖直，商品固定上端 1/4-20 外牙从各自 x 后端进入背面中央加厚 boss。固定网柱从黄灰交界 z=16 mm 一体向上延伸到 z=372.5 mm；网布及卡夹仍只工作到 z=168.5 mm，不切 M6 球头直连孔；M6 光学总成的独立承力支撑待单独定义。偏航、俯仰、旋转微调依靠采购球头锁紧机构。",
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
        "notes": "顶面为平盘，接触台面底面；底面中央为内宽外窄的扁球头收纳窝，另配背护罩从底部向上扣入并胶合，防止拆下收纳时丢失。它不是软垫，首样按刚性 PETG 小底盘打印；若需要可在顶面另贴薄胶皮。",
    },
    {
        "id": "table-bottom-pressure-pad-guards",
        "name_zh": "台底压块背护罩",
        "name_en": "underside pressure-pad back guards",
        "kind": "防丢结构件",
        "status": "PETG 打印件 / 装入后胶合",
        "printable": True,
        "quantity": "2 件（左右各 1）",
        "scad_part": "clamp_pressure_pad_guard",
        "notes": "从压块底部向上扣入；中心孔让 12 mm 粗牙杆身通过但挡住 Ø15.5 扁球头，四根定位柱插入压块盲孔后再点胶。它只负责收纳防丢，不承担夹紧主载荷。",
    },
    {
        "id": "clamp-electronics-installation",
        "name_zh": "桌下夹体电子腔完整安装",
        "name_en": "clamp electronics installation",
        "kind": "电子装配",
        "status": "KiCad PCB + 外购器件 + 打印壳体",
        "printable": False,
        "quantity": "左右各 1 套",
        "scad_part": "clamp_electronics_full_cutaway",
        "notes": "右侧放 ESP32 母板、1S 电池和 y+ 侧壁 UI 子板/面框；左侧放发射电源子板与内置电池；所有线束沿 M6 侧出线并保留端子/压接接口。电子腔取消 UI 底盖，侧壁窗口由可拆面框维护。",
    },
    {
        "id": "m6-receiver-carrier-pcb",
        "name_zh": "M6 十路接收子板",
        "name_en": "M6 receiver carrier PCB",
        "kind": "电子装配",
        "status": "KiCad PCB / 真实 3D 模型 / 首样布线审查",
        "printable": False,
        "quantity": "2 块（左右各 1）",
        "scad_part": "m6_detector_mount",
        "notes": "竖直贴 M6 壳体 +y 内壁安装，采用 80 × 32 mm 集中式接收载板；光学头仍按 M6 壳体的 20 mm 阵列排列，线束在进入载板前汇聚，板级包络来自 KiCad STL/STEP。",
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


def _post_clamp_carrier_specs() -> list[ExportSpec]:
    return _side_specs(
        "post_clamp_carrier",
        "post-clamp-carrier",
        "PETG",
        "X1C 首样斜放 rx=0°、ry=51°、rz=45°；不切断、不缩放，按清单配置支撑。",
        "首样左右各一件；整根固定网柱与绿色 SKP 整体底座一体打印。底座沿 x 方向从灰色 C 夹外侧推入让位腔，整体包络约 58.7×58×20 mm；保留两枚 Ø4 mm 通孔、中央 Ø6×2 mm 底坑和两侧 15 mm 外伸。黄色立柱在 z=16 mm 与绿色底座相接，网布/卡夹的 3 mm 过道和接收腔仍只到网顶 z=168.5 mm，主体继续到 z=260.5 mm；不切断、不分段、没有 T 槽、公轨或第二个独立滑靴。灰色夹体必须使用配套让位腔、两枚 Ø4.4 mm 孔和下方钢珠定位孔；当前不切 M6 球头直连孔，M6 光学总成独立支撑待定义。X1C 首样采用 rx=0°、ry=51°、rz=45° 三轴斜放；不缩放，切片器仍需按清单配置支撑。旧的直接共面座打印件与本件不兼容，必须连同配套 C 方案夹体一起换版。",
    )


def _indexed_rail_specs() -> list[ExportSpec]:
    # The active design has no top net rail.  Keep the function name as a
    # compatibility boundary for callers that imported the old helper, but do
    # not let legacy rail geometry re-enter the printable package.
    return []


def build_export_specs() -> list[ExportSpec]:
    specs: list[ExportSpec] = []
    specs.extend(_post_clamp_carrier_specs())
    split_notes = (
        "左右各需一套；C 形夹沿 y=0 竖直分型为操作者侧 y- 半体和对手侧 y+ 半体。"
        "两半各有 9 个横向 M5 连接位；只有连接位的 Ø16 mm 足迹真正贴到电子腔空腔边界时，"
        "才打印 boss 柱和十字加强肋。完全位于 14 mm 实体上夹板/下臂里的连接位只保留通孔、"
        "沉孔或六角螺母窝，避免加强结构在外壳上形成凸起。左下角连接孔向外侧移动，"
        "电子仓左下角与右下斜加强边沿各补 1 处连接点，横向 M5 连接件把螺钉头/六角螺母的力传回承力壁。操作者侧"
        "为 M5 圆头沉孔，对手侧为防转六角螺母窝，分型总间隙 0.20 mm。电子腔在中间"
        "打开后可从分型面布线/装板；绿色 C 方案底座的 x+ 推入让位腔、两枚 Ø4.4 mm"
        "连接孔和中央钢珠定位孔保持不变。两个半体必须与新版 post_clamp_carrier 配套，"
        "旧整件夹体不再进入正式打印清单；图示间隙不是强度/防水承诺。"
    )
    specs.extend(
        _side_specs(
            "clamp_body_half_user",
            "clamp-body-half-user",
            "PETG",
            "大平面朝下；y- 分型面朝内；M5 圆头沉孔从外侧可达；底面朝下打印后去除分型毛刺。",
            split_notes,
        )
    )
    specs.extend(
        _side_specs(
            "clamp_body_half_opponent",
            "clamp-body-half-opponent",
            "PETG",
            "大平面朝下；y+ 分型面朝内；M5 六角螺母窝从外侧装入；底面朝下打印后去除分型毛刺。",
            split_notes,
        )
    )
    # The active electronics bay has an integrated floor and a y+ UI window.
    # The side faceplate is still a preview/fit item until its screw, gasket,
    # and service-opening dimensions are frozen; it is intentionally absent
    # from this 37-STL first package. The retired UI bottom cover remains only
    # as a legacy source diagnostic and is not part of the active assembly.
    specs.extend(
        _side_specs(
            "m6_detector_body",
            "m6-detector-body",
            "PETG",
            "长条主体平面朝下；M6 光学孔轴向按右侧基准；左右件分别打印。",
            "M6 十路直角光电器件的 PETG 长条主体，含 10 路头部定位/通孔和前后盖导向槽；内部接收子板不与主体熔成一体。",
        )
    )
    specs.extend(
        _side_specs(
            "m6_detector_shell_front",
            "m6-detector-front-cover",
            "PETG",
            "光学孔端面朝上；装配方向为 x- 滑入；盖板配合面打印后去毛刺。",
            "M6 光学端整片前盖，十路光学孔、两侧导向舌和沉头螺钉孔均保留；盖板为完整件，不用剖切件替代实物。",
        )
    )
    specs.extend(
        _side_specs(
            "m6_detector_shell_rear",
            "m6-detector-rear-cover",
            "PETG",
            "线缆端面朝上；装配方向为 x+ 滑入；后侧支撑 boss 朝外。",
            "M6 线缆端整片后盖，含球头支撑 boss、两侧导向舌和沉头螺钉孔；支撑受力路径与线缆出口分开。",
        )
    )
    specs.extend(
        _side_specs(
            "m6_detector_bottom_cover",
            "m6-detector-bottom-cover",
            "PETG",
            "底盖大平面朝下；出线孔朝外；螺钉沉头面朝上。",
            "M6 壳体底盖，四周连续压紧边、螺钉孔和多芯线缆出口均在同一可拆件上；不以透明剖切预览代替打印件。",
        )
    )
    specs.extend(
        _side_specs(
            "m6_detector_bottom_gasket",
            "m6-detector-bottom-gasket",
            "TPU/柔性",
            "薄片平面朝下；按柔性材料单独排盘；不得与 PETG 壳体同盘。",
            "M6 底盖连续压紧垫；仅作为盖板贴合/防尘的柔性件，不能把当前设计解释为防水等级认证。",
        )
    )
    specs.extend(
        _side_specs(
            "m6_detector_cable_gland",
            "m6-detector-cable-gland",
            "PETG",
            "环形端面朝下；通孔轴沿 Z；压紧件与线束测试后再冻结。",
            "M6 多孔压紧出线环/应力释放环；用于把十路线束从底盖引出，实际装配可配密封胶圈或灌封套，但壳盖本身仍按严丝合缝配合验收。",
        )
    )
    specs.extend(
        _side_specs(
            "net_clamp_clip",
            "net-clamp-clip",
            "PETG",
            "平放打印；宽面贴床；安装时把全高方向沿 z 立起，从立柱外侧沿 x 推入。",
            "真实全高 U 形滑入卡网夹；两片 jaw 名义间隙 1.8 mm，夹住 1.2 mm 网布；先从球台中心侧穿过立柱 3 mm 过道，再从桌外侧滑入卡夹，网布端止在立柱外边。网布张力和绳的拉力负责压紧卡夹，立柱内嵌单一被动止挡只防反向拔出；正侧 jaw 的一体弹性扣舌让止挡越过并在回拉时闭合肩拦住，无穿钉、横向销钉或网夹螺钉；按开 jaw 才能解锁反向滑出。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_pressure_pad",
            "clamp-pressure-pad",
            "PETG",
            "平盘顶面朝上；底面粗牙螺杆扁球头收纳窝朝下；圆盘平面贴打印床。",
            "独立台底 Ø50 mm 刚性圆盘压块；位于下舌头台下有效区段中点，顶面接触台底，底面内宽外窄窝容纳 Ø15.5 扁球头；底部四个盲孔接收背护罩定位柱；可选在顶面另贴薄胶皮。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_pressure_pad_guard",
            "clamp-pressure-pad-guard",
            "PETG",
            "环形护罩平面朝下；四根定位柱朝上插入压块底部盲孔。",
            "独立台底压块的扁球头防丢背护罩；中心孔允许 12 mm 粗牙杆身通过但挡住 Ø15.5 扁球头，装入压块后点胶固定，不承担夹紧主载荷。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_printed_screw",
            "clamp-printed-screw",
            "PETG",
            "轴线竖直；扁球头朝上；平盘压块装配后让球头落入内宽外窄窝；建议竖直打印并加 brim。",
            "正式 PETG 锥形粗牙夹紧螺杆；12 mm 大径、9.6 mm 芯径、4 mm 螺距、约 1.2 mm 牙高，牙根/凹槽各约 2 mm，外侧锥尖约 0.4 mm，顶部 15.5 mm 扁球头带浅六角驱动窝。必须和配套 PETG 锥形粗牙螺母成组使用，不与 M8×1.25 标准螺母混用。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_body_nut",
            "clamp-printed-body-nut",
            "PETG",
            "六角大平面贴床；螺纹轴线沿 Z；打印后清理内螺纹起始边。",
            "下臂捕获用 PETG 锥形粗牙固定螺母；AF16、11.5 mm 高，与 12/9.6 mm、4 mm 螺距、2 mm 牙根、0.4 mm 锥尖打印螺杆配套。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_knob",
            "clamp-knob",
            "PETG",
            "旋钮平面朝下；六角螺母捕获窝朝上。",
            "打印旋钮；必须装入预先对锁的两枚 PETG 粗牙螺母，不使用标准 M8 细牙螺母。",
        )
    )
    specs.extend(
        _side_specs(
            "clamp_knob_nut",
            "clamp-printed-knob-nut",
            "PETG",
            "六角大平面贴床；每个 STL 含两枚粗牙螺母，内螺纹轴线沿 Z。",
            "旋钮内捕获的两枚 PETG 锥形粗牙对锁螺母；每枚 6 mm 高，先对锁后装入旋钮捕获窝，牙根/凹槽各约 2 mm，锥尖约 0.4 mm。",
        )
    )
    specs.extend(
        _side_specs(
            "sensor_mount_body",
            "sensor-mount-body",
            "PETG",
            "网顶夹座平面朝下；U 形开口沿网布上沿扣入；薄膜和压片不可与本体合并打印。",
            "网端 PVDF 安装座本体；从网布上沿扣入，右件外端到右立柱内侧面保留 18 mm，左件镜像；本体不接触立柱，也不形成网顶轨道。",
        )
    )
    specs.extend(
        _side_specs(
            "sensor_clamp_lip",
            "sensor-clamp-lip",
            "PETG/TPU 试样",
            "压片平面朝下；同一 STL 含左右两枚可拆压片。",
            "夹持 PVDF 薄膜两侧的可拆压片；只压薄膜，不承担网架或立柱载荷。",
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
        "design": "desktop-clamp-one-side-x1c-v0.7-split-c-scheme",
        "source": str(SOURCE.relative_to(HERE.parent.parent)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "units": "mm",
        "install_model": "整体替换式球网支架；两侧传统桌下 C 形夹，免打孔；每只 C 夹由 y=0 分型的前后半体组成。",
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
