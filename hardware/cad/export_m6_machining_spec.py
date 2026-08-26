#!/usr/bin/env python3
"""Export the current M6 first-article/CNC handoff.

The OpenSCAD ``parameter_probe`` is the numerical source of truth. The active
detector body is a printable PETG rectangle that can later be reproduced in
CNC; the rear cover carries the M8 clearance interface for the purchased
vertical 13 mm ballhead. No custom 90-degree support is part of this handoff.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from pathlib import Path

from validate_net_stand import SOURCE, probe_parameters
from validate_scad import find_openscad


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "exports" / "net-stand-v0.1" / "m6-machining-spec.json"
SCHEMA_VERSION = "m6-machining-spec-v0.8-20-mm-pitch-petg-body-rear-boss"


def _r(value: float) -> float | int:
    rounded = round(float(value), 4)
    if math.isclose(rounded, round(rounded), abs_tol=1e-9):
        return int(round(rounded))
    return rounded


def _channel_schedule(parameters: dict[str, float]) -> list[dict[str, object]]:
    count = int(parameters["m6_sensor_count"])
    net_height = parameters["net_height"]
    first_height = parameters["m6_sensor_first_height"]
    pitch = parameters["m6_sensor_center_pitch"]
    body_bottom = parameters["m6_detector_body_bottom_z"]
    return [
        {
            "channel_index": index,
            "height_from_table_mm": _r(first_height + index * pitch),
            "sensor_center_z_global_mm": _r(
                net_height + first_height + index * pitch
            ),
            "sensor_center_z_local_to_body_mm": _r(
                net_height + first_height + index * pitch - body_bottom
            ),
            "optical_axis_y_mm": _r(
                parameters["m6_detector_sensor_head_center_y"]
            ),
            "thread_axis_x_global_mm": _r(
                parameters["m6_detector_detector_thread_axis_x"]
            ),
            "insertion": "右侧从外侧 x+、左侧从外侧 x- 装入；灰色六角卡入各自外侧浅窝，M6 中空外丝/光学筒穿过主体并指向球台中心；蓝色尾线局部 z- 绕光束 x 轴 -45° 后从主体 y- 后方斜向让位；螺纹末端中心孔分别朝 x-/x+",
        }
        for index in range(count)
    ]


def build_spec(openscad: str, probe_directory: Path) -> dict[str, object]:
    parameters = probe_parameters(openscad, probe_directory)
    count = int(parameters["m6_sensor_count"])

    body_size = [
        _r(parameters["m6_detector_body_length_x"]),
        _r(parameters["m6_detector_body_depth_y"]),
        _r(parameters["m6_detector_body_height_z"]),
    ]
    body_min = [
        _r(parameters["m6_detector_body_min_x"]),
        _r(parameters["m6_detector_body_min_y"]),
        _r(parameters["m6_detector_body_bottom_z"]),
    ]
    body_envelope_size = body_size[:]
    body_envelope_min = body_min[:]
    shell_size = [
        _r(
            parameters["m6_detector_shell_max_x"]
            - parameters["m6_detector_shell_min_x"]
        ),
        _r(
            max(
                parameters["m6_detector_shell_max_y"],
                parameters["m6_detector_shell_support_boss_max_y"],
            )
            - min(
                parameters["m6_detector_shell_min_y"],
                parameters["m6_detector_shell_support_boss_min_y"],
            )
        ),
        _r(parameters["m6_detector_shell_height_z"]),
    ]
    body_depth_limit = (
        parameters["m6_detector_fit_thread_length_x"]
        + parameters["m6_detector_fit_capture_depth_x"]
        - parameters["m6_sensor_lock_nut_h"]
        - parameters["m6_detector_fit_thread_tip_allowance_x"]
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "source": "hardware/cad/net_stand.scad",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "units": "mm",
        "status": "当前 PETG 首样/CNC 复用输入；真实传感器、球头和网夹实测前不得视为最终放行图",
        "material": "PETG first article body and covers; future 6061-T6 CNC body option; purchased metal ballhead",
        "quantity": {
            "detector_bodies": 2,
            "printed_front_covers": 2,
            "printed_rear_covers": 2,
            "printed_bottom_covers": 2,
            "purchased_ballheads": 2,
        },
        "part_schedule": [
            {
                "part": "m6_machining_detector_body",
                "name_zh": "十路 45° L 型 PETG 长方条主体（后续可换 CNC）",
                "material": "PETG first article; future 6061-T6 CNC-compatible option",
                "blank_mm": body_size,
                "per_side": 1,
                "total": 2,
                "preview_is_printable": True,
                "process": "FDM PETG 首样打印；后续可按同一 10×56×216 mm 包络改为 6061-T6 CNC。十个通道中心按 20 mm 节距布置；每路有沿 x 的中空 M6 光学/外丝筒让位孔、绕 x 轴 -45° 的尾线让位和 x 向浅六角座；主体不带 T 尾座、M8 孔或主体内线缆槽",
                "fit_before_release": "先用一只真实 M6 直角对射头验证灰色六角外形、M6 中空外丝中心光学孔、蓝色尾线局部 z- 后绕光束 x 轴 -45°、六角窝、有效外丝、至少一枚原配螺帽和光轴高度",
            },
        ],
        "printed_cover_schedule": [
            {
                "part": "m6_detector_shell_front",
                "name_zh": "激光方向前盖（PETG）",
                "per_side": 1,
                "total": 2,
                "notes": "从主体上方套入；前端用浅球弧表达光学侧外形；沉头螺钉固定。",
            },
            {
                "part": "m6_detector_shell_rear",
                "name_zh": "后盖（PETG，后方加厚 M8 接口 boss）",
                "per_side": 1,
                "total": 2,
                "notes": "覆盖 x+ 线缆端；y− 后方加厚形成支撑 boss，开 x 向 Ø8.6 M8 通孔，供金属球头/转接件连接；首样不把薄壳当作唯一弯矩承力件。",
            },
            {
                "part": "m6_detector_bottom_cover",
                "name_zh": "底盖（PETG）",
                "per_side": 1,
                "total": 2,
                "notes": "与下方截面同宽；两枚沉头螺钉固定；中央开放 Ø12 mm 线缆/套管过孔，不宣称密封。",
            },
        ],
        "sensor_contract": {
            "sku_id": "6122579349941",
            "item_id": "1071628886139",
            "thread": "M6x0.75",
            "count_per_detector": count,
            "channel_pitch_mm": _r(parameters["m6_sensor_center_pitch"]),
            "height_schedule_mm": [
                _r(
                    parameters["m6_sensor_first_height"]
                    + index * parameters["m6_sensor_center_pitch"]
                )
                for index in range(count)
            ],
            "body_blank_mm": body_size,
            "body_global_min_mm": body_min,
            "body_envelope_mm": body_envelope_size,
            "body_envelope_global_min_mm": body_envelope_min,
            "body_center_y_global_mm": _r(parameters["m6_detector_body_center_y"]),
            "sensor_roll_deg": _r(parameters["m6_sensor_roll_deg"]),
            "body_depth_limit_from_stem_and_one_nut_mm": _r(body_depth_limit),
            "body_depth_margin_mm": _r(
                body_depth_limit - parameters["m6_detector_body_length_x"]
            ),
            "horizontal_thread_section_length_mm": _r(
                parameters["m6_sensor_mount_stem_length"]
            ),
            "horizontal_overall_package_length_mm": _r(
                parameters["m6_sensor_overall_end_x"]
                - parameters["m6_sensor_axis_x"]
            ),
            "cable_branch_local_axis": "z-",
            "cable_branch_roll_deg_about_x": _r(parameters["m6_sensor_roll_deg"]),
            "cable_guard_length_mm": _r(parameters["m6_sensor_cable_guard_length"]),
            "cable_d_mm": _r(parameters["m6_sensor_cable_d"]),
            "cable_pocketed_in_body": False,
            "sensor_optical_bore_d_mm": _r(parameters["m6_sensor_optical_bore_d"]),
            "optical_aperture_location": "M6 中空外丝筒的末端中心孔；灰色六角处不再画独立黑色光学面",
            "optical_bore_d_mm": _r(parameters["m6_detector_optical_bore_d"]),
            "thread_clearance_d_mm": _r(
                parameters["m6_detector_thread_clearance_d"]
            ),
            "hex_pocket_af_mm": _r(parameters["m6_detector_hex_pocket_af"]),
            "hex_pocket_depth_local_axis_mm": _r(
                parameters["m6_detector_hex_pocket_depth_x"]
            ),
            "hex_pocket_floor_mm": _r(
                parameters["m6_detector_hex_pocket_floor"]
            ),
            "insertion_axis": "right x+ / left x- outward entry; outer gray hex captured by shallow pocket; hollow threaded optical barrel and one nut pass toward the smooth opposite body face",
            "optical_axis": "x",
            "orientation": "L 型灰色六角/尾线在外侧，M6 中空外丝末端中心孔为出光/受光端并水平朝球台中心；蓝色尾线先沿局部 z-，再绕 x 轴 -45°，向 y-/z- 让位",
            "lane_layout": "单列竖直安装，所有光学中心 y=0；主体为 x=10 mm 厚、y=56 mm 宽并居中 y=0；十路中心高度为 +10、+30…+190 mm，不采用旧的左右交错双列",
            "sensor_nut_count_per_channel": 1,
            "sensor_nut_position": "主体平滑的另一侧表面；不嵌入主体；不使用打印固定螺丝",
            "thread_visible_after_body_mm": _r(
                parameters["m6_detector_thread_visible_length"]
            ),
            "channel_schedule": _channel_schedule(parameters),
        },
        "shell_contract": {
            "outer_envelope_mm": shell_size,
            "outer_min_global_mm": [
                _r(parameters["m6_detector_shell_min_x"]),
                _r(parameters["m6_detector_shell_min_y"]),
                _r(parameters["m6_detector_shell_bottom_z"]),
            ],
            "wall_mm": _r(parameters["m6_detector_shell_wall"]),
            "body_clearance_mm": _r(parameters["m6_detector_shell_clearance"]),
            "split_axis": "x",
            "split_x_global_mm": _r(parameters["m6_detector_shell_split_x"]),
            "top_view_profile": "z+ 俯视：x- 光学端为正圆弧，x+ 线缆端为圆角矩形；中间仅为前后盖分型边界，不建连线",
            "front_cap_length_x_mm": _r(
                parameters["m6_detector_front_cap_length_x"]
            ),
            "rear_corner_radius_mm": _r(
                parameters["m6_detector_shell_corner_radius"]
            ),
            "front_max_x_global_mm": _r(
                parameters["m6_detector_shell_front_max_x"]
            ),
            "rear_min_x_global_mm": _r(
                parameters["m6_detector_shell_rear_min_x"]
            ),
            "shared_edge_grooves": {
                "width_x_mm": _r(parameters["m6_detector_body_groove_width_x"]),
                "depth_y_mm": _r(parameters["m6_detector_body_groove_depth_y"]),
                "margin_z_mm": _r(parameters["m6_detector_body_groove_margin_z"]),
                "tongue_clearance_mm": _r(parameters["m6_detector_shell_tongue_clearance"]),
                "ownership": "前盖占 x- 半、后盖占 x+ 半；两盖共享 y± 两条连续竖槽",
            },
            "top_entry": "前盖位于 x- 光学端并做正球弧、后盖位于 x+ 线缆端并做圆角矩形；后盖 y- 外侧适当增厚形成 M8 支撑 boss，主体位于两盖中间，前后盖均从主体 z+ 套入；底盖从 z- 贴合，最终尺寸待真实器件首样复核",
            "support_boss": {
                "material": "PETG 首样；未来可换金属嵌件或 CNC 后盖",
                "min_global_mm": [
                    _r(parameters["m6_detector_shell_support_boss_min_x"]),
                    _r(parameters["m6_detector_shell_support_boss_min_y"]),
                    _r(parameters["m6_detector_shell_support_boss_bottom_z"]),
                ],
                "max_global_mm": [
                    _r(parameters["m6_detector_shell_support_boss_max_x"]),
                    _r(parameters["m6_detector_shell_support_boss_max_y"]),
                    _r(parameters["m6_detector_shell_support_boss_top_z"]),
                ],
                "length_x_mm": _r(parameters["m6_detector_shell_support_boss_length_x"]),
                "depth_y_mm": _r(parameters["m6_detector_shell_support_boss_depth_y"]),
                "height_z_mm": _r(parameters["m6_detector_shell_support_boss_height_z"]),
                "hole_axis": "x- from the rear x+ face toward the optical side",
                "hole_d_mm": _r(parameters["m6_detector_shell_support_hole_d"]),
                "hole_depth_x_mm": _r(parameters["m6_detector_shell_support_hole_depth_x"]),
                "hole_entry_x_global_mm": _r(parameters["m6_detector_shell_support_hole_entry_x"]),
            },
        },
        "support_contract": {
            "type": "purchased 13 mm ballhead/gimbal",
            "posture": "vertical; the purchased part itself supplies adjustment and net-clamp support",
            "boss_hole_axis": "x- from the rear cover boss toward the optical side",
            "boss_hole_d_mm": _r(parameters["m6_detector_shell_support_hole_d"]),
            "boss_hole_depth_x_mm": _r(parameters["m6_detector_shell_support_hole_depth_x"]),
            "boss_hole_entry_x_global_mm": _r(parameters["m6_detector_shell_support_hole_entry_x"]),
            "ballhead_stud_engagement_x_mm": _r(parameters["m6_detector_shell_support_stud_engagement_x"]),
            "ballhead_center_x_global_mm": _r(parameters["m6_detector_ballhead_center_x"]),
            "ballhead_center_y_global_mm": _r(parameters["m6_detector_ballhead_center_y"]),
            "ballhead_center_z_global_mm": _r(parameters["m6_detector_ballhead_center_z"]),
            "net_interface": "采购球头自带竖直螺柱/底座直接接商品网夹；不制作自有 90° 支撑 STL",
            "load_path": "PETG 后盖加厚 boss / 后续 CNC 或金属嵌件 -> M8 外牙采购球头 -> 球头自带竖直网夹接口",
        },
        "ballhead_contract": {
            "ball_d_mm": _r(parameters["m6_ballhead_ball_d"]),
            "housing_d_mm": _r(parameters["m6_ballhead_housing_d"]),
            "housing_length_mm": _r(parameters["m6_ballhead_housing_length_x"]),
            "base_d_mm": _r(parameters["m6_ballhead_base_d"]),
            "base_t_mm": _r(parameters["m6_ballhead_base_t"]),
            "sensor_stud_d_mm": _r(parameters["m6_ballhead_sensor_stud_d"]),
            "sensor_stud_length_mm": _r(
                parameters["m6_ballhead_sensor_stud_length"]
            ),
            "net_stud_d_mm": _r(parameters["m6_ballhead_net_stud_d"]),
            "net_stud_length_mm": _r(parameters["m6_ballhead_net_stud_length"]),
            "posture": "球头主体竖直；侧向 M8 外牙进入后盖 y− 加厚 boss 的 x 向通孔，下方竖直接口直接接商品网夹；最终承力以采购金属件和首样实测为准",
            "rotation_range_deg": _r(parameters["m6_ballhead_rotation_range_deg"]),
            "opening_range_deg": _r(parameters["m6_ballhead_tilt_range_deg"]),
            "selected_variant": "13mm球【M8外牙】（当前模型默认）",
            "alternative_variants": [
                "13mm球【1/4内牙】",
                "13mm球【1/4外牙】",
                "13mm球【3/8外牙】",
                "13mm球【M6外牙】",
                "13mm球【M8外牙】",
                "13mm球【M10外牙】",
            ],
            "status": "商品外形和螺纹版本仍需到货实测；不进入打印或铝件 STL",
        },
        "fastener_schedule": [
            {
                "id": "sensor_lock_nut",
                "name_zh": "M6 传感器原配锁紧螺帽",
                "per_side": count,
                "total": 2 * count,
                "spec": "M6x0.75 supplier nut; exactly one nut is shown directly outside the 10 mm body",
                "status": "verify real nut thickness and hex across flats",
            },
            {
                "id": "cover_to_body",
                "name_zh": "前后盖到 PETG/CNC 主体沉头螺丝",
                "per_side": 4,
                "total": 8,
                "spec": "M3/M4 class screw; hole/head dimensions remain first-article hardware choice",
                "status": "choose after cover material and tap drill review",
            },
            {
                "id": "bottom_cover_to_body",
                "name_zh": "底盖沉头螺丝",
                "per_side": 2,
                "total": 4,
                "spec": "M3/M4 class screw; two x positions",
                "status": "verify cable sleeve and screw-head clearance",
            },
            {
                "id": "detector_to_ballhead",
                "name_zh": "后盖加厚 boss 到采购球头",
                "per_side": 1,
                "total": 2,
                "spec": "selected 13 mm ballhead; current visual proxy is M8 external through the rear-cover boss, with first-article washer/insert decision pending",
                "status": "verify delivered thread side, effective engagement and anti-rotation",
            },
            {
                "id": "purchased_ballhead_to_net_clamp",
                "name_zh": "采购球头竖直接口到商品网夹",
                "per_side": 1,
                "total": 2,
                "spec": "use the selected 13 mm ballhead's supplied vertical stud/base and the purchased net-clamp interface; no custom support bracket",
                "status": "freeze after real ballhead and clamp measurement",
            },
        ],
        "release_checks": [
            "收到真实 M6 对射器件后复核 M6x0.75 有效外丝长度、头部六角 AF、六角轴向厚度、光学中心和原配螺帽厚度",
            "用一只真实器件先验证 10 mm 主体厚度、x 轴 -45° 斜向浅六角窝、一枚外螺帽和线缆弯曲半径",
            "确认左右件只做 x 镜像：左侧发射光轴朝 x+，右侧接收光轴朝 x-，两侧后盖 boss 均位于各自外侧 y-",
            "确认前盖 x-、后盖 x+ 从 z+ 套入；两盖舌片分别落入 y± 连续边槽的 x 前/后半，沉头螺钉不会进入光学孔或线缆孔",
            "球头按竖直姿态安装；到货后核对 13 mm 球、旋钮净空、90°开口、360°旋转和螺纹选项",
            "真实网夹安装面、球网外伸和孔距实测后，核对采购球头竖直螺柱/底座的直接安装界面，不再制作独立灰色适配板或 90°支撑件",
            "从最低/中间/最高通道复核发射端与接收端的偏航、俯仰、滚转微调范围和锁紧后保持性",
            "机加工件不进入 PETG 打印清单；底盖线缆孔是开放孔，不作防水承诺",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--openscad", default=None)
    args = parser.parse_args()
    openscad = args.openscad or find_openscad()
    with tempfile.TemporaryDirectory(prefix="m6-machining-probe-") as directory:
        spec = build_spec(openscad, Path(directory))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "M6_MACHINING_SPEC_OK "
        f"(output={args.output}, source_sha256={spec['source_sha256']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
