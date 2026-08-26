#!/usr/bin/env python3
"""Export the current M6 45-degree L-sensor machining handoff.

The OpenSCAD ``parameter_probe`` is the numerical source of truth. This
handoff describes the aluminum body, the separate 90-degree metal support and
the vertical net-clamp adapter. PETG covers and the purchased 13 mm ballhead
are documented as assembly interfaces, not silently promoted to machined
parts.
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
SCHEMA_VERSION = "m6-machining-spec-v0.6-20-mm-pitch-l-sensor"


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
    shell_size = [
        _r(
            parameters["m6_detector_shell_max_x"]
            - parameters["m6_detector_shell_min_x"]
        ),
        _r(parameters["m6_detector_shell_width_y"]),
        _r(parameters["m6_detector_shell_height_z"]),
    ]
    support_min_x = parameters["m6_detector_support_arm_min_x"]
    support_max_x = max(
        parameters["m6_detector_support_arm_max_x"],
        parameters["m6_detector_support_leg_x"]
        + parameters["m6_detector_support_gusset_inset_x"],
    )
    support_size = [
        _r(support_max_x - support_min_x),
        _r(parameters["m6_detector_support_arm_width_y"]),
        _r(
            parameters["m6_detector_support_leg_top_z"]
            - parameters["m6_detector_support_leg_bottom_z"]
        ),
    ]
    adapter_size = [
        _r(parameters["m6_mount_plate_t"]),
        _r(parameters["m6_mount_plate_width_y"]),
        _r(parameters["m6_mount_plate_height_z"]),
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
        "status": "当前首样加工输入；真实传感器、球头和网夹实测前不得视为最终放行图",
        "material": "6061-T6 aluminum; finish and anodizing TBD",
        "quantity": {
            "detector_bodies": 2,
            "support_brackets": 2,
            "net_clamp_adapters": 2,
            "printed_front_covers": 2,
            "printed_rear_covers": 2,
            "printed_bottom_covers": 2,
            "purchased_ballheads": 2,
        },
        "part_schedule": [
            {
                "part": "m6_machining_detector_body",
                "name_zh": "十路 45° L 型长条传感器主体",
                "material": "6061-T6 aluminum",
                "blank_mm": body_size,
                "per_side": 1,
                "total": 2,
                "preview_is_printable": False,
                "process": "铣削/钻孔；主体为 x 向 10 mm 厚、y 向 56 mm 宽、z 向 216 mm 竖直长条，十个通道中心按 20 mm 节距布置；每路有沿 x 的中空 M6 光学/外丝筒让位孔、绕 x 轴 -45° 的尾线让位和 x 向浅六角座；壳体盲孔暂不作为主体放行条件",
                "fit_before_release": "先用一只真实 M6 直角对射头验证灰色六角外形、M6 中空外丝中心光学孔、蓝色尾线局部 z- 后绕 x 轴 -45°、六角窝、有效外丝、至少一枚原配螺帽和光轴高度",
            },
            {
                "part": "m6_machining_support",
                "name_zh": "90°金属承力支撑件",
                "material": "6061-T6 aluminum or equivalent metal; process TBD",
                "blank_mm": support_size,
                "per_side": 1,
                "total": 2,
                "preview_is_printable": False,
                "process": "折弯/铣削一体件或金属板件加工；水平臂、竖直腿、两侧三角加固肋共同承力",
                "fit_before_release": "实测球头下方螺纹、支撑臂高度和网夹适配板的孔位后冻结",
            },
            {
                "part": "m6_machining_adapter",
                "name_zh": "竖直网夹/立柱固定适配板",
                "material": "6061-T6 aluminum",
                "blank_mm": adapter_size,
                "per_side": 1,
                "total": 2,
                "preview_is_printable": False,
                "process": "板材钻铣；当前模型显示与 90° 支撑腿的两枚横向连接孔",
                "fit_before_release": "真实商品网夹固定面、夹具外伸、孔距、垫片和通栓叠层实测后再下最终订单",
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
                "name_zh": "后方桥接壳（PETG）",
                "per_side": 1,
                "total": 2,
                "notes": "覆盖 x+ 线缆端并带 y- 后置 boss；boss 中央沿 x- 指向光学端，使用金属 M8 外牙/衬套连接采购球头/转接件。",
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
            "top_entry": "前盖位于 x- 光学端并做正球弧、后盖位于 x+ 线缆端并做圆角矩形；后盖 y- 外侧带 M8 金属桥接 boss；主体位于两盖中间，前后盖均从主体 z+ 套入；底盖从 z- 贴合，最终尺寸待真实器件首样复核",
        },
        "support_contract": {
            "boss_width_x_mm": _r(parameters["m6_detector_support_boss_width_x"]),
            "boss_depth_y_mm": _r(parameters["m6_detector_support_boss_depth_y"]),
            "boss_height_z_mm": _r(parameters["m6_detector_support_boss_height_z"]),
            "boss_center_x_global_mm": _r(
                parameters["m6_detector_support_boss_center_x"]
            ),
            "support_y_global_mm": _r(parameters["m6_detector_support_y"]),
            "arm_z_global_mm": _r(parameters["m6_detector_support_arm_z"]),
            "arm_width_y_mm": _r(parameters["m6_detector_support_arm_width_y"]),
            "leg_x_global_mm": _r(parameters["m6_detector_support_leg_x"]),
            "leg_bottom_z_global_mm": _r(
                parameters["m6_detector_support_leg_bottom_z"]
            ),
            "leg_top_z_global_mm": _r(parameters["m6_detector_support_leg_top_z"]),
            "gusset_t_y_mm": _r(parameters["m6_detector_support_gusset_t_y"]),
            "thread_nominal_d_mm": _r(parameters["m6_detector_support_thread_nominal_d"]),
            "metal_insert_d_mm": _r(parameters["m6_detector_support_metal_insert_d"]),
            "metal_insert_length_x_mm": _r(parameters["m6_detector_support_metal_insert_length_x"]),
            "printed_boss_clearance_d_mm": _r(parameters["m6_detector_support_tap_d"]),
            "load_path": "后盖 boss -> 90°金属支撑水平臂 -> 竖直腿 -> 网夹适配板/网架",
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
            "posture": "球头主体竖直；下方螺柱接 90° 支撑，上方/侧向锁紧后盖总成",
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
                "name_zh": "前后盖到铝主体沉头螺丝",
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
                "name_zh": "后盖 boss 到采购球头",
                "per_side": 1,
                "total": 2,
                "spec": "selected 13 mm ballhead thread/adapter; current visual proxy is M8 external with metal bushing",
                "status": "verify delivered thread side, effective engagement and anti-rotation",
            },
            {
                "id": "support_to_adapter",
                "name_zh": "90°支撑到竖直网夹适配板",
                "per_side": 2,
                "total": 4,
                "spec": "nominal M5/M6 through-bolts; current CAD uses Ø5.5 clearance",
                "status": "freeze after real clamp interface measurement",
            },
        ],
        "release_checks": [
            "收到真实 M6 对射器件后复核 M6x0.75 有效外丝长度、头部六角 AF、六角轴向厚度、光学中心和原配螺帽厚度",
            "用一只真实器件先验证 10 mm 主体厚度、x 轴 -45° 斜向浅六角窝、一枚外螺帽和线缆弯曲半径",
            "确认左右件只做 x 镜像：左侧发射光轴朝 x+，右侧接收光轴朝 x-，两侧主体后方均为各自外侧 y-",
            "确认前盖 x-、后盖 x+ 从 z+ 套入；两盖舌片分别落入 y± 连续边槽的 x 前/后半，沉头螺钉不会进入光学孔或线缆孔",
            "球头按竖直姿态安装；到货后核对 13 mm 球、旋钮净空、90°开口、360°旋转和螺纹选项",
            "真实网夹安装面、球网外伸和孔距实测后，冻结竖直适配板及 90°支撑连接孔",
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
