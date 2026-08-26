"""Generate a lightweight visual preview of the current integrated net stand.

This mirrors the intent of ``net_stand.scad`` without parsing STL files.  It is
useful in CI and on machines where the OpenSCAD GUI/CLI is not installed; it is
not a replacement for OpenSCAD geometry validation or a strength calculation.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "preview.png"

TABLE_WIDTH = 1525.0
TABLE_THICKNESS = 25.0
TABLE_EDGE = TABLE_WIDTH / 2
POST_WIDTH = 28.0
NET_POST_OUTBOARD_EXTENSION = 152.5
POST_OFFSET = 138.5
CLAMP_OUTER_EXTENSION = 7.5
CLAMP_REACH_INBOARD = 62.0
CLAMP_PAD_T = 8.0
CLAMP_CLEARANCE = 1.5
POST_CENTER = TABLE_EDGE + POST_OFFSET
CLAMP_SCREW_INSET = 30.0
CLAMP_SCREW_D = 8.0
CLAMP_SCREW_CAPTURE_EXTENSION = 2.0
CLAMP_KNOB_D = 36.0
CLAMP_KNOB_H = 20.0
CLAMP_SCREW_TO_KNOB_TOP = 32.0
CLAMP_NUT_AF = 13.0
CLAMP_NUT_H = 6.5
CLAMP_NUT_CLEARANCE = 0.35
CLAMP_KNOB_NUT_GAP = 0.4
CLAMP_KNOB_NUT_STACK = 2 * CLAMP_NUT_H + CLAMP_KNOB_NUT_GAP
CLAMP_TOP_PAD_X = -CLAMP_REACH_INBOARD + 8.0
CLAMP_TOP_PAD_WIDTH = 96.0
CLAMP_TOP_PAD_DEPTH = 48.0
CLAMP_TOP_PAD_T = 2.0
CLAMP_LOWER_ARM_CLEARANCE = 10.0
CLAMP_LOWER_ARM_TOP = -TABLE_THICKNESS - CLAMP_LOWER_ARM_CLEARANCE
CLAMP_LOWER_ARM_BOTTOM = CLAMP_LOWER_ARM_TOP - CLAMP_PAD_T
CLAMP_PRESSURE_PAD_WIDTH = 42.0
CLAMP_PRESSURE_PAD_DEPTH = 44.0
CLAMP_PRESSURE_PAD_T = 2.0
CLAMP_PRESSURE_PAD_TOP = -TABLE_THICKNESS - CLAMP_CLEARANCE
CLAMP_PRESSURE_PAD_BOTTOM = CLAMP_PRESSURE_PAD_TOP - CLAMP_PRESSURE_PAD_T
CLAMP_SCREW_X = -CLAMP_SCREW_INSET
CLAMP_PAD_X = -CLAMP_REACH_INBOARD
CLAMP_PAD_OUTER_X = POST_OFFSET + POST_WIDTH / 2 + CLAMP_OUTER_EXTENSION
CLAMP_OUTER_WALL_WIDTH = 22.0
CLAMP_OUTER_WALL_X = CLAMP_PAD_OUTER_X - CLAMP_OUTER_WALL_WIDTH
CLAMP_GUSSET_T_Y = 10.0
CLAMP_GUSSET_START_INSET = 6.0
CLAMP_GUSSET_START_X = CLAMP_SCREW_X + CLAMP_PRESSURE_PAD_WIDTH / 2 + CLAMP_GUSSET_START_INSET
CLAMP_GUSSET_END_X = CLAMP_PAD_OUTER_X - 0.2
CLAMP_LOWER_ARM_X = CLAMP_SCREW_X - 22.0 / 2
CLAMP_SCREW_TOP = CLAMP_PRESSURE_PAD_BOTTOM
CLAMP_KNOB_TOP = CLAMP_SCREW_TOP - CLAMP_SCREW_TO_KNOB_TOP
CLAMP_KNOB_BOTTOM = CLAMP_KNOB_TOP - CLAMP_KNOB_H
CLAMP_KNOB_NUT_TOP = CLAMP_KNOB_TOP - CLAMP_NUT_CLEARANCE / 2
CLAMP_KNOB_DRIVE_NUT_Z = CLAMP_KNOB_NUT_TOP - CLAMP_NUT_H
CLAMP_KNOB_LOCK_NUT_Z = (
    CLAMP_KNOB_DRIVE_NUT_Z - CLAMP_KNOB_NUT_GAP - CLAMP_NUT_H
)
CLAMP_SCREW_BOTTOM = CLAMP_KNOB_LOCK_NUT_Z - CLAMP_SCREW_CAPTURE_EXTENSION
CLAMP_BODY_NUT_Z = CLAMP_LOWER_ARM_BOTTOM + CLAMP_NUT_CLEARANCE
CLAMP_GUSSET_TOP_Z = CLAMP_PRESSURE_PAD_TOP - 0.5
CLAMP_GUSSET_BOTTOM_Z = CLAMP_LOWER_ARM_BOTTOM - 0.2
OPTICAL_BEAM_EDGE_OVERLAP = 0.5
OPTICAL_BEAM_AXIS_X = TABLE_EDGE + OPTICAL_BEAM_EDGE_OVERLAP
POST_BOTTOM = CLAMP_LOWER_ARM_TOP
NET_HEIGHT = 152.5
NET_RAIL_HEIGHT = 10.0
BEAM_FIRST = 10.0
BEAM_COUNT = 10
BEAM_PITCH = 10.0
BEAM_LAST = BEAM_FIRST + (BEAM_COUNT - 1) * BEAM_PITCH
M6_SENSOR_CENTER_PITCH = 20.0
M6_SENSOR_FIRST_HEIGHT = BEAM_FIRST
M6_SENSOR_LAST_HEIGHT = M6_SENSOR_FIRST_HEIGHT + (BEAM_COUNT - 1) * M6_SENSOR_CENTER_PITCH
M6_SENSOR_HEAD_LENGTH_X = 6.0
M6_SENSOR_HEAD_WIDTH_Y = 10.0
M6_SENSOR_HEAD_HEIGHT_Z = 8.0
M6_SENSOR_HEAD_HEX_AF = 8.0
M6_SENSOR_BODY_D = 6.0
M6_SENSOR_BODY_LENGTH = 22.0
M6_SENSOR_MOUNT_STEM_LENGTH = 14.0
M6_RAIL_T = 8.0
M6_RAIL_WIDTH_Y = 42.0
M6_RAIL_TAB_T = 6.0
M6_RAIL_TAB_WIDTH_Y = 12.0
M6_SENSOR_LANE_OFFSET_Y = 9.0
M6_RAIL_END_MARGIN = 12.0
M6_RAIL_LENGTH = (BEAM_COUNT - 1) * M6_SENSOR_CENTER_PITCH + 2 * M6_RAIL_END_MARGIN
M6_ARRAY_BOTTOM = NET_HEIGHT + M6_SENSOR_FIRST_HEIGHT - M6_RAIL_END_MARGIN
M6_ARRAY_TOP = M6_ARRAY_BOTTOM + M6_RAIL_LENGTH
M6_SENSOR_AXIS_X = OPTICAL_BEAM_AXIS_X
M6_SENSOR_RAIL_X = 788.0
M6_SENSOR_MOUNT_HOLE_X = M6_SENSOR_AXIS_X + 3.25
M6_RAIL_TAB_MIN_X = M6_SENSOR_AXIS_X + 1.0
M6_RAIL_TAB_MAX_X = M6_SENSOR_RAIL_X + M6_RAIL_T
M6_DETECTOR_BACKPLATE_X = M6_SENSOR_RAIL_X + M6_RAIL_T - 0.5
M6_DETECTOR_BACKPLATE_T = 8.0
M6_DETECTOR_BACKPLATE_HEIGHT = M6_RAIL_LENGTH + 16.0
M6_BALLHEAD_CENTER_X = M6_DETECTOR_BACKPLATE_X + M6_DETECTOR_BACKPLATE_T + 16.0 + 26.0 / 2
M6_BALLHEAD_BASE_CENTER_X = M6_BALLHEAD_CENTER_X + 26.0 / 2 + 8.0 / 2
M6_BALLHEAD_NET_STUD_CENTER_X = M6_BALLHEAD_BASE_CENTER_X + 8.0 / 2 + 28.0 / 2
M6_BALLHEAD_BALL_D = 13.0
M6_BALLHEAD_HOUSING_D = 28.0
M6_BALLHEAD_HOUSING_LENGTH_X = 26.0
M6_BALLHEAD_BASE_D = 32.0
M6_BALLHEAD_BASE_T = 8.0
M6_BALLHEAD_TILT_RANGE_DEG = 90.0
M6_BALLHEAD_ROTATION_RANGE_DEG = 360.0
M6_MOUNT_PLATE_X = POST_CENTER - POST_WIDTH / 2 - 6.0
M6_MOUNT_PLATE_WIDTH = 56.0
M6_MOUNT_PLATE_HEIGHT = M6_RAIL_LENGTH + 24.0
M6_YAW_STAGE_T = 6.0
M6_YAW_STAGE_RADIUS = 82.0
M6_YAW_SLOT_RADIUS = 64.0
M6_YAW_STAGE_Z = M6_ARRAY_BOTTOM - 4.0
M6_YAW_PIVOT_X = M6_MOUNT_PLATE_X - 3.0
M6_PITCH_YOKE_T = 8.0
M6_PITCH_YOKE_WIDTH_Y = 158.0
M6_PITCH_FRAME_T = 6.0
M6_PITCH_FRAME_OUTER_WIDTH_Y = 140.0
M6_PITCH_FRAME_WINDOW_WIDTH_Y = 118.0
M6_PITCH_FRAME_OUTER_HEIGHT_Z = 236.0
M6_PITCH_FRAME_WINDOW_HEIGHT_Z = 220.0
M6_PITCH_PIVOT_OFFSET_Z = 26.0
M6_ROLL_PIVOT_D = 6.5
M6_ROLL_PLATE_D = 110.0
# Current body-first 45-degree L-sensor contract.  These direct values mirror the
# SCAD inputs; the global body/shell/support coordinates below are derived from
# the table edge and the +10...+190 mm channel schedule.
M6_SENSOR_ROLL_DEG = -45.0
M6_DETECTOR_BODY_CENTER_Y = 0.0
M6_DETECTOR_BODY_DEPTH_Y = 56.0
M6_DETECTOR_BODY_LENGTH_X = 10.0
M6_DETECTOR_BODY_MARGIN_Z = 18.0
M6_DETECTOR_BODY_FRONT_MARGIN_X = 1.0
M6_DETECTOR_SHELL_WALL = 2.4
M6_DETECTOR_SHELL_CLEARANCE = 0.6
M6_DETECTOR_SHELL_BOTTOM_LIP_Z = 3.0
M6_DETECTOR_SHELL_TOP_LIP_Z = 3.0
M6_DETECTOR_SHELL_SPLIT_OVERLAP_X = 0.3
M6_DETECTOR_SHELL_CORNER_RADIUS = 2.2
M6_DETECTOR_FRONT_CAP_LENGTH_X = 8.0
M6_DETECTOR_FRONT_CAP_REDUCTION = 1.2
M6_DETECTOR_BODY_GROOVE_WIDTH_X = 4.0
M6_DETECTOR_BODY_GROOVE_DEPTH_Y = 1.2
M6_DETECTOR_BODY_GROOVE_MARGIN_Z = 5.0
M6_DETECTOR_SHELL_TONGUE_DEPTH_Y = 1.0
M6_DETECTOR_SHELL_TONGUE_CLEARANCE = 0.25
M6_DETECTOR_OPTICAL_BORE_D = 6.6
M6_DETECTOR_THREAD_CLEARANCE_D = 6.6
M6_DETECTOR_HEX_POCKET_AF = 10.7
M6_DETECTOR_HEX_POCKET_DEPTH_X = 2.5
M6_DETECTOR_HEX_POCKET_DEPTH_Y = 2.5
M6_DETECTOR_HEX_POCKET_FLOOR = 0.8
M6_DETECTOR_SHELL_SCREW_PILOT_D = 3.4
M6_DETECTOR_SHELL_SCREW_HEAD_D = 6.8
M6_DETECTOR_SHELL_SCREW_HEAD_DEPTH = 2.0
M6_DETECTOR_SHELL_SCREW_MARGIN_Z = 18.0
M6_DETECTOR_BOTTOM_COVER_T = 3.0
M6_BOTTOM_COVER_SCREW_DEPTH = 5.0
M6_DETECTOR_BOTTOM_COVER_SCREW_D = 3.4
M6_DETECTOR_BOTTOM_COVER_SCREW_HEAD_D = 6.8
M6_DETECTOR_BOTTOM_COVER_SCREW_HEAD_DEPTH = 1.6
M6_DETECTOR_BOTTOM_COVER_SCREW_INSET_X = 9.0
M6_DETECTOR_CABLE_EXIT_D = 12.0
M6_DETECTOR_CABLE_EXIT_SLEEVE_CLEARANCE = 1.0
M6_DETECTOR_SUPPORT_BOSS_WIDTH_X = 18.0
M6_DETECTOR_SUPPORT_BOSS_DEPTH_Y = 8.0
M6_DETECTOR_SUPPORT_BOSS_HEIGHT_Z = 24.0
M6_DETECTOR_SUPPORT_BOSS_X_FRACTION = 0.72
M6_DETECTOR_SUPPORT_TAP_D = 5.0
M6_DETECTOR_SUPPORT_TAP_DEPTH_X = 12.0
M6_DETECTOR_SUPPORT_ARM_T_Z = 8.0
M6_DETECTOR_SUPPORT_ARM_WIDTH_Y = 18.0
M6_DETECTOR_SUPPORT_LEG_T_X = 8.0
M6_DETECTOR_SUPPORT_LEG_BOTTOM_DROP_Z = 56.0
M6_DETECTOR_SUPPORT_GUSSET_T_Y = 6.0
M6_DETECTOR_SUPPORT_GUSSET_INSET_X = 8.0
M6_DETECTOR_SUPPORT_FASTENER_D = 5.5
M6_DETECTOR_DETECTOR_BALLHEAD_GAP_X = 2.0
M6_DETECTOR_SENSOR_HEAD_Y_OFFSET = 0.0
POST_TOP = max(NET_HEIGHT + BEAM_LAST + 3.0 + 18.0, M6_ARRAY_TOP + 18.0)
NET_SPAN = 2 * (POST_CENTER + POST_WIDTH / 2)
REFERENCE_HEIGHT = 50.0
SENSOR_X = 0.32 * NET_SPAN / 2


def draw_front(ax) -> None:
    ax.add_patch(
        Rectangle(
            (-TABLE_EDGE, -TABLE_THICKNESS),
            TABLE_WIDTH,
            TABLE_THICKNESS,
            facecolor="#a8adb3",
            edgecolor="#4d535a",
            alpha=0.55,
            label="tabletop section",
        )
    )
    ax.add_patch(
        Rectangle(
            (-NET_SPAN / 2, 0),
            NET_SPAN,
            NET_HEIGHT - NET_RAIL_HEIGHT,
            facecolor="#dfe3e8",
            edgecolor="#777d85",
            alpha=0.35,
            label="installed net",
        )
    )
    ax.add_patch(
        Rectangle(
            (-NET_SPAN / 2, NET_HEIGHT - NET_RAIL_HEIGHT),
            NET_SPAN,
            NET_RAIL_HEIGHT,
            facecolor="#f3f4f5",
            edgecolor="#53585f",
            label="net top rail",
        )
    )

    for x, label in (
        (-POST_CENTER, "left integrated post"),
        (POST_CENTER, "right integrated post"),
    ):
        ax.add_patch(
            Rectangle(
                (x - POST_WIDTH / 2, POST_BOTTOM),
                POST_WIDTH,
                POST_TOP - POST_BOTTOM,
                facecolor="#e67e22",
                edgecolor="#8d4c13",
                alpha=0.88,
                label=label,
            )
        )

    for index in range(BEAM_COUNT):
        height = BEAM_FIRST + index * BEAM_PITCH
        ax.plot(
            [-OPTICAL_BEAM_AXIS_X, OPTICAL_BEAM_AXIS_X],
            [NET_HEIGHT + height, NET_HEIGHT + height],
            color="#4c78a8",
            linewidth=1.2,
            alpha=0.8,
            label="10 optical beam levels" if index == 0 else "_nolegend_",
        )
        ax.text(
            NET_SPAN / 2 + 22,
            NET_HEIGHT + height,
            f"+{height:g}",
            va="center",
            fontsize=7,
        )

    body_min_x = M6_SENSOR_AXIS_X - M6_DETECTOR_BODY_FRONT_MARGIN_X
    body_max_x = body_min_x + M6_DETECTOR_BODY_LENGTH_X
    body_bottom = NET_HEIGHT + M6_SENSOR_FIRST_HEIGHT - M6_DETECTOR_BODY_MARGIN_Z
    body_top = body_bottom + (
        (BEAM_COUNT - 1) * M6_SENSOR_CENTER_PITCH
        + 2 * M6_DETECTOR_BODY_MARGIN_Z
    )
    shell_min_x = M6_SENSOR_AXIS_X - M6_DETECTOR_SHELL_WALL
    shell_max_x = (
        M6_SENSOR_AXIS_X
        + M6_SENSOR_HEAD_LENGTH_X
        + M6_SENSOR_MOUNT_STEM_LENGTH
        + M6_DETECTOR_SHELL_WALL
    )
    shell_bottom = body_bottom - M6_DETECTOR_SHELL_BOTTOM_LIP_Z
    shell_top = body_top + M6_DETECTOR_SHELL_TOP_LIP_Z
    for side, label in ((-1, "M6 45° L型长条主体（壳体待重画）"), (1, "_nolegend_")):
        body_x = body_min_x if side > 0 else -body_max_x
        shell_x = shell_min_x if side > 0 else -shell_max_x
        ax.add_patch(
            Rectangle(
                (body_x, body_bottom),
                M6_DETECTOR_BODY_LENGTH_X,
                body_top - body_bottom,
                facecolor="#b8c0c8",
                edgecolor="#505963",
                alpha=0.94,
            )
        )
        for index in range(BEAM_COUNT):
            z = NET_HEIGHT + M6_SENSOR_FIRST_HEIGHT + index * M6_SENSOR_CENTER_PITCH
            head_x = M6_SENSOR_AXIS_X if side > 0 else -M6_SENSOR_AXIS_X - M6_SENSOR_HEAD_LENGTH_X
            thread_x = (
                M6_SENSOR_AXIS_X + M6_SENSOR_HEAD_LENGTH_X
                if side > 0
                else -M6_SENSOR_AXIS_X - M6_SENSOR_HEAD_LENGTH_X - M6_SENSOR_MOUNT_STEM_LENGTH
            )
            cable_x = (
                M6_SENSOR_AXIS_X + M6_SENSOR_HEAD_LENGTH_X / 2 - M6_SENSOR_BODY_D / 2
                if side > 0
                else -M6_SENSOR_AXIS_X - M6_SENSOR_HEAD_LENGTH_X / 2 - M6_SENSOR_BODY_D / 2
            )
            ax.add_patch(
                Rectangle(
                    (head_x, z - M6_SENSOR_HEAD_HEIGHT_Z / 2),
                    M6_SENSOR_HEAD_LENGTH_X,
                    M6_SENSOR_BODY_D,
                    facecolor="#6c737b",
                    edgecolor="#2d3338",
                    alpha=0.9,
                )
            )
            ax.add_patch(
                Rectangle(
                    (thread_x, z - M6_SENSOR_HEAD_HEIGHT_Z / 2 + 1),
                    M6_SENSOR_MOUNT_STEM_LENGTH,
                    M6_SENSOR_HEAD_HEIGHT_Z - 2,
                    facecolor="#c1c7cc",
                    edgecolor="#68737b",
                    alpha=0.9,
                )
            )
            guard_drop = 10.0 * 2**-0.5
            ax.add_patch(
                Rectangle(
                    (cable_x, z - M6_SENSOR_HEAD_HEIGHT_Z / 2 - guard_drop),
                    M6_SENSOR_HEAD_HEIGHT_Z,
                    guard_drop,
                    facecolor="#3c65d7",
                    edgecolor="#263d91",
                    alpha=0.82,
                )
            )
            ax.plot(
                [cable_x + M6_SENSOR_HEAD_HEIGHT_Z / 2,
                 cable_x + M6_SENSOR_HEAD_HEIGHT_Z / 2],
                [z - M6_SENSOR_HEAD_HEIGHT_Z / 2 - guard_drop,
                 z - M6_SENSOR_HEAD_HEIGHT_Z / 2 - guard_drop - 12],
                color="#20252b",
                linewidth=1.4,
                alpha=0.95,
            )
            ax.plot(
                M6_SENSOR_MOUNT_HOLE_X if side > 0 else -M6_SENSOR_MOUNT_HOLE_X,
                z,
                marker="o",
                markersize=2.8,
                color="#20252b",
            )
            # One purchased nut sits directly on the outward body face.  It
            # is not a countersunk/embedded fixing screw and there is no
            # second lock nut in the current installation contract.
            nut_x = body_max_x if side > 0 else -body_max_x - 5
            ax.add_patch(
                Rectangle(
                    (nut_x, z - 5),
                    5,
                    10,
                    facecolor="#d0a72b",
                    edgecolor="#6a737b",
                    alpha=0.95,
                )
            )
            if index == 0 and side < 0:
                ax.plot([], [], color="#3c65d7", linewidth=3.0, label="蓝色护套：局部 z− 绕光束 x 轴 -45°")
                ax.plot([], [], color="#c1c7cc", linewidth=2.0, label="水平 M6 外丝 / 光学轴")
        # The side-specific vertical adapter and 90-degree support are shown
        # as an outline so the front view exposes the load path without
        # hiding the ten optical heads.
        adapter_x = M6_MOUNT_PLATE_X if side > 0 else -M6_MOUNT_PLATE_X - 6
        ax.add_patch(
            Rectangle(
                (adapter_x, M6_ARRAY_BOTTOM - 12),
                6,
                M6_MOUNT_PLATE_HEIGHT,
                facecolor="#d9dde1",
                edgecolor="#505963",
                alpha=0.48,
            )
        )

    for x in (-SENSOR_X, SENSOR_X):
        ax.add_patch(
            Rectangle(
                (x - 23, NET_HEIGHT - 1),
                46,
                8,
                facecolor="#9467bd",
                edgecolor="#4c2b68",
                label="PVDF net-top mounts" if x < 0 else "_nolegend_",
            )
        )

    reference_z = NET_HEIGHT + REFERENCE_HEIGHT
    ax.plot(
        [-NET_SPAN / 2, NET_SPAN / 2],
        [reference_z, reference_z],
        color="#31a354",
        linewidth=2.4,
        label="reference line (+50 mm detent)",
    )
    ax.annotate(
        "net-top datum +0",
        xy=(0, NET_HEIGHT),
        xytext=(0, NET_HEIGHT - 30),
        ha="center",
        arrowprops={"arrowstyle": "->", "color": "#444"},
        fontsize=8,
    )
    ax.set_xlim(-POST_CENTER - 90, POST_CENTER + 110)
    ax.set_ylim(POST_BOTTOM - 12, POST_TOP + 20)
    ax.set_title("Integrated net stand: front intent")
    ax.set_xlabel("table width / mm")
    ax.set_ylabel("z relative to table top / mm")
    ax.grid(True, alpha=0.22)
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper center", fontsize=7, ncol=2)


def draw_side(ax) -> None:
    # 以右侧台边为 x=0，正方向是桌外；画出免打孔 C 形夹体。
    post_x0 = POST_OFFSET - POST_WIDTH / 2
    ax.add_patch(
        Rectangle(
            (-62, -TABLE_THICKNESS),
            62,
            TABLE_THICKNESS,
            facecolor="#a8adb3",
            edgecolor="#4d535a",
            alpha=0.55,
            label="tabletop edge",
        )
    )
    body_min_x = M6_SENSOR_AXIS_X - M6_DETECTOR_BODY_FRONT_MARGIN_X
    body_max_x = body_min_x + M6_DETECTOR_BODY_LENGTH_X
    body_bottom = NET_HEIGHT + M6_SENSOR_FIRST_HEIGHT - M6_DETECTOR_BODY_MARGIN_Z
    body_height = (
        (BEAM_COUNT - 1) * M6_SENSOR_CENTER_PITCH
        + 2 * M6_DETECTOR_BODY_MARGIN_Z
    )
    ax.add_patch(
        Rectangle(
            (body_min_x - TABLE_EDGE, body_bottom),
            M6_DETECTOR_BODY_LENGTH_X,
            body_height,
            facecolor="#b8c0c8",
            edgecolor="#505963",
            alpha=0.94,
            label="M6 加宽加厚铝合金主体（56×10 mm 截面）",
        )
    )
    for index in range(BEAM_COUNT):
        z = NET_HEIGHT + M6_SENSOR_FIRST_HEIGHT + index * M6_SENSOR_CENTER_PITCH
        ax.plot(
            M6_SENSOR_AXIS_X - TABLE_EDGE,
            z,
            marker="o",
            markersize=2.8,
            color="#20252b",
        )
    # This global side view cannot expose rotation about the optical x axis,
    # so the y-z inset below is the authoritative visual check for the L leg.
    ax.plot(
        [M6_SENSOR_AXIS_X - TABLE_EDGE + 5,
         M6_SENSOR_AXIS_X - TABLE_EDGE + 5],
        [body_bottom - 1, body_bottom + body_height + 1],
        color="#66727c",
        linewidth=1.2,
        alpha=0.45,
        label="10 个 20 mm 节距通道的 x 轴投影",
    )
    support_arm_min_x = 807.24 - TABLE_EDGE
    support_arm_max_x = 889.0 - TABLE_EDGE
    support_arm_z = 182.5
    support_leg_x = 884.0 - TABLE_EDGE
    support_leg_bottom = 126.5
    support_leg_top = 186.5
    ax.add_patch(
        Rectangle(
            (support_arm_min_x, support_arm_z - 4),
            support_arm_max_x - support_arm_min_x,
            8,
            facecolor="#5f6972",
            edgecolor="#30383f",
            label="90° metal support arm",
        )
    )
    ax.add_patch(
        Rectangle(
            (support_leg_x - 4, support_leg_bottom),
            8,
            support_leg_top - support_leg_bottom,
            facecolor="#5f6972",
            edgecolor="#30383f",
            label="vertical support leg",
        )
    )
    ax.add_patch(
        Polygon(
            [
                (support_leg_x - 4, support_leg_bottom),
                (support_leg_x + 4, support_leg_bottom),
                (support_leg_x + 12, support_arm_z - 4),
                (support_leg_x - 4, support_arm_z - 4),
            ],
            closed=True,
            facecolor="#434c54",
            edgecolor="#30383f",
            alpha=0.9,
            label="triangular under-support gusset",
        )
    )
    adapter_x = M6_MOUNT_PLATE_X - TABLE_EDGE
    ax.add_patch(
        Rectangle(
            (adapter_x, M6_ARRAY_BOTTOM - 12),
            6.0,
            M6_MOUNT_PLATE_HEIGHT,
            facecolor="#d9dde1",
            edgecolor="#505963",
            alpha=0.8,
            label="vertical net-clamp adapter",
        )
    )
    ballhead_x = 823.24 - TABLE_EDGE
    ballhead_z = NET_HEIGHT + 55.0
    ax.add_patch(
        Rectangle(
            (ballhead_x - 14, ballhead_z - 13),
            28,
            26,
            facecolor="#c7cdd2",
            edgecolor="#505963",
            alpha=0.95,
            label="13 mm purchased ball head, vertical",
        )
    )
    ax.add_patch(
        Circle(
            (ballhead_x, ballhead_z),
            6.5,
            facecolor="#e2e5e8",
            edgecolor="#505963",
            alpha=0.9,
        )
    )
    ax.plot(
        [ballhead_x, ballhead_x],
        [ballhead_z - 26, support_arm_z],
        color="#b6bdc3",
        linewidth=4.0,
        label="vertical ball-head stud",
    )
    ax.plot(
        [body_max_x - TABLE_EDGE, ballhead_x - 14],
        [body_bottom + body_height / 2, ballhead_z],
        color="#b6bdc3",
        linewidth=4.0,
        label="horizontal rear boss connection",
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_PAD_X, CLAMP_TOP_PAD_T),
            CLAMP_PAD_OUTER_X - CLAMP_PAD_X,
            CLAMP_PAD_T,
            facecolor="#69727b",
            label="fixed upper jaw (no drilling)",
        )
    )
    ax.add_patch(
        Polygon(
            [
                (CLAMP_GUSSET_START_X, CLAMP_GUSSET_BOTTOM_Z),
                (CLAMP_GUSSET_END_X, CLAMP_GUSSET_BOTTOM_Z),
                (CLAMP_GUSSET_END_X, CLAMP_GUSSET_TOP_Z),
            ],
            closed=True,
            facecolor="#4f5963",
            edgecolor="#2e353c",
            alpha=0.92,
            label="under-clamp load gusset pair",
        )
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_TOP_PAD_X, 0),
            CLAMP_TOP_PAD_WIDTH,
            CLAMP_TOP_PAD_T,
            facecolor="#111111",
            label="replaceable upper protective pad",
        )
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_LOWER_ARM_X, CLAMP_LOWER_ARM_BOTTOM),
            CLAMP_PAD_OUTER_X - CLAMP_LOWER_ARM_X,
            CLAMP_PAD_T,
            facecolor="#69727b",
            label="fixed lower arm / nut seat",
        )
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_OUTER_WALL_X, CLAMP_LOWER_ARM_BOTTOM),
            CLAMP_OUTER_WALL_WIDTH,
            CLAMP_PAD_T + CLAMP_TOP_PAD_T + TABLE_THICKNESS + CLAMP_LOWER_ARM_CLEARANCE,
            facecolor="#69727b",
            label="outer C-frame",
        )
    )
    ax.add_patch(
        Rectangle(
            (post_x0, POST_BOTTOM),
            POST_WIDTH,
            POST_TOP - POST_BOTTOM,
            facecolor="#e67e22",
            edgecolor="#8d4c13",
            alpha=0.88,
            label="integrated upright",
        )
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_SCREW_X - CLAMP_PRESSURE_PAD_WIDTH / 2, CLAMP_PRESSURE_PAD_BOTTOM),
            CLAMP_PRESSURE_PAD_WIDTH,
            CLAMP_PRESSURE_PAD_T,
            facecolor="#111111",
            label="movable underside pressure pad",
        )
    )
    ax.plot(
        [CLAMP_SCREW_X, CLAMP_SCREW_X],
        [CLAMP_SCREW_BOTTOM, CLAMP_PRESSURE_PAD_TOP],
        color="#444",
        linewidth=CLAMP_SCREW_D / 2,
        label="M8 screw below tabletop",
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_SCREW_X - CLAMP_KNOB_D / 2, CLAMP_KNOB_BOTTOM),
            CLAMP_KNOB_D,
            CLAMP_KNOB_H,
            facecolor="#30343b",
            label="hand knob",
        )
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_SCREW_X - CLAMP_NUT_AF / 2, CLAMP_KNOB_LOCK_NUT_Z),
            CLAMP_NUT_AF,
            CLAMP_KNOB_NUT_STACK,
            facecolor="#d4a72c",
            edgecolor="#6e5515",
            label="two jam nuts captured in knob",
        )
    )
    ax.plot(
        [CLAMP_SCREW_X - CLAMP_NUT_AF / 2,
         CLAMP_SCREW_X + CLAMP_NUT_AF / 2],
        [CLAMP_KNOB_DRIVE_NUT_Z, CLAMP_KNOB_DRIVE_NUT_Z],
        color="#6e5515",
        linewidth=1,
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_SCREW_X - CLAMP_NUT_AF / 2, CLAMP_BODY_NUT_Z),
            CLAMP_NUT_AF,
            CLAMP_NUT_H,
            facecolor="#d4a72c",
            edgecolor="#6e5515",
            label="fixed M8 nut",
        )
    )
    ax.axhline(NET_HEIGHT, color="#ffffff", linewidth=2, label="traditional net top 152.5 mm")
    ax.axhline(NET_HEIGHT + REFERENCE_HEIGHT, color="#31a354", linewidth=2, label="reference line +50 mm")
    for index in range(BEAM_COUNT):
        height = BEAM_FIRST + index * BEAM_PITCH
        ax.plot(
            [POST_OFFSET - 8, POST_OFFSET + POST_WIDTH + 4],
            [NET_HEIGHT + height, NET_HEIGHT + height],
            color="#4c78a8",
            linewidth=1.0,
        )
    ax.add_patch(
        Rectangle(
            (post_x0 - 20, NET_HEIGHT - 1),
            12,
            8,
            facecolor="#9467bd",
            label="PVDF mount on net top",
        )
    )
    ax.set_xlim(-82, CLAMP_PAD_OUTER_X + 18)
    ax.set_ylim(CLAMP_KNOB_BOTTOM - 8, POST_TOP + 20)
    inset = ax.inset_axes([0.52, 0.58, 0.44, 0.34])
    inset.set_facecolor("#f7f9fb")
    inset.add_patch(
        Rectangle(
            (-9, -18),
            6,
            26,
            facecolor="#b8c0c8",
            edgecolor="#505963",
            alpha=0.92,
            label="主体 y- 背骨",
        )
    )
    inset.add_patch(
            Polygon(
                [(-4.62, 0), (-2.31, 4), (2.31, 4),
                 (4.62, 0), (2.31, -4), (-2.31, -4)],
                closed=True,
                facecolor="#6c737b",
                edgecolor="#2d3338",
                alpha=0.95,
                label="L 型六角头",
            )
    )
    cable_start = (-2.83, -2.83)
    cable_end = (
        cable_start[0] - 10.0 * 2**-0.5,
        cable_start[1] - 10.0 * 2**-0.5,
    )
    inset.plot(
        [cable_start[0], cable_end[0]],
        [cable_start[1], cable_end[1]],
        color="#3c65d7",
        linewidth=5.0,
        solid_capstyle="round",
        label="蓝色护套：局部 z− 绕 x 轴 -45°",
    )
    cable_tail_end = (
        cable_end[0] - 14 * 2**-0.5,
        cable_end[1] - 14 * 2**-0.5,
    )
    inset.plot(
        [cable_end[0], cable_tail_end[0]],
        [cable_end[1], cable_tail_end[1]],
        color="#20252b",
        linewidth=2.0,
        solid_capstyle="round",
        label="黑色线缆代理",
    )
    inset.add_patch(
        Circle(
            cable_end,
            2.8,
            facecolor="#3c65d7",
            edgecolor="#263d91",
            label="尾线支路",
        )
    )
    inset.axhline(0, color="#9aa4ad", linewidth=0.8)
    inset.axvline(0, color="#9aa4ad", linewidth=0.8)
    inset.set_xlim(-16, 8)
    inset.set_ylim(-18, 8)
    inset.set_aspect("equal", adjustable="box")
    inset.set_title("y-z 局部：斜向 7 字安装", fontsize=8)
    inset.set_xlabel("y（后方为 −）", fontsize=7)
    inset.set_ylabel("z", fontsize=7)
    inset.tick_params(labelsize=6)
    inset.grid(True, alpha=0.2)
    ax.set_title("No-drill under-table C-clamp + M6 45° L-body: side intent")
    ax.set_xlabel("relative to table edge: inboard <- / outboard -> / mm")
    ax.set_ylabel("z / mm")
    ax.grid(True, alpha=0.22)
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper left", fontsize=7)


def make_preview() -> None:
    fig, (front, side) = plt.subplots(1, 2, figsize=(16, 8), constrained_layout=True)
    draw_front(front)
    draw_side(side)
    fig.suptitle(
        "Pingpang SmartGear: integrated net stand and height grid (intent, not STL validation)",
        fontsize=14,
    )
    fig.savefig(OUT, dpi=160)
    print(OUT)


if __name__ == "__main__":
    make_preview()
