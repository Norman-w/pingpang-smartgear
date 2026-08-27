"""Generate a lightweight visual preview of the current integrated net stand.

This mirrors the intent of ``net_stand.scad`` without parsing STL files.  It is
useful in CI and on machines where the OpenSCAD GUI/CLI is not installed; it is
not a replacement for OpenSCAD geometry validation or a strength calculation.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Polygon, Rectangle


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "preview.png"

# The preview is consumed as a Chinese design-review image.  Prefer the
# built-in macOS CJK font when it is available, while retaining a portable
# Latin fallback for CI/Linux hosts where that system font does not exist.
_CJK_FONT = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
if _CJK_FONT.is_file():
    font_manager.fontManager.addfont(str(_CJK_FONT))
    plt.rcParams["font.family"] = "Hiragino Sans GB"
else:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

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
M6_SENSOR_LOCK_NUT_H = 5.0
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
M6_SENSOR_MOUNT_HOLE_X = 766.25
M6_RAIL_TAB_MIN_X = M6_SENSOR_AXIS_X + 1.0
M6_RAIL_TAB_MAX_X = M6_SENSOR_RAIL_X + M6_RAIL_T
M6_BALLHEAD_BALL_D = 13.0
M6_BALLHEAD_HOUSING_D = 28.0
M6_BALLHEAD_HOUSING_LENGTH_X = 26.0
M6_BALLHEAD_BASE_D = 32.0
M6_BALLHEAD_BASE_T = 8.0
M6_BALLHEAD_SENSOR_STUD_D = 8.0
M6_BALLHEAD_NET_STUD_D = 8.0
M6_BALLHEAD_NET_STUD_LENGTH = 28.0
M6_BALLHEAD_TILT_RANGE_DEG = 90.0
M6_BALLHEAD_ROTATION_RANGE_DEG = 360.0
M6_YAW_STAGE_T = 6.0
M6_YAW_STAGE_RADIUS = 82.0
M6_YAW_SLOT_RADIUS = 64.0
M6_DETECTOR_BODY_MIN_X = 761.25
M6_DETECTOR_BODY_BOTTOM_Z = 144.5
M6_DETECTOR_BODY_HEIGHT_Z = 216.0
M6_DETECTOR_SHELL_MIN_X = 748.0
M6_DETECTOR_SHELL_MAX_X = 785.4
M6_DETECTOR_SHELL_MIN_Y = -30.4
M6_DETECTOR_SHELL_MAX_Y = 30.4
M6_DETECTOR_SHELL_BOTTOM_Z = 141.5
M6_DETECTOR_SHELL_HEIGHT_Z = 222.0
M6_DETECTOR_SHELL_SPLIT_X = 766.0
M6_DETECTOR_SHELL_FRONT_MAX_X = 765.8
M6_DETECTOR_SHELL_REAR_MIN_X = 766.2
M6_DETECTOR_SHELL_SUPPORT_BOSS_LENGTH_X = 14.0
M6_DETECTOR_SHELL_SUPPORT_BOSS_OVERLAP_X = 3.0
M6_DETECTOR_SHELL_SUPPORT_BOSS_DEPTH_Y = 18.0
M6_DETECTOR_SHELL_SUPPORT_BOSS_HEIGHT_Z = 36.0
M6_DETECTOR_SHELL_SUPPORT_BOSS_RADIUS = 2.0
M6_DETECTOR_SHELL_SUPPORT_HOLE_D = 8.6
M6_DETECTOR_SHELL_SUPPORT_HOLE_DEPTH_X = 14.0
M6_DETECTOR_SHELL_SUPPORT_STUD_ENGAGEMENT_X = 12.0
M6_DETECTOR_DETECTOR_BALLHEAD_GAP_X = 2.0
M6_DETECTOR_BODY_CENTER_Y = 0.0
M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X = (
    M6_DETECTOR_SHELL_MAX_X
    - M6_DETECTOR_SHELL_SUPPORT_BOSS_OVERLAP_X
)
M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_X = (
    M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X
    + M6_DETECTOR_SHELL_SUPPORT_BOSS_LENGTH_X
)
M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_Y = (
    M6_DETECTOR_BODY_CENTER_Y + M6_DETECTOR_SHELL_SUPPORT_BOSS_DEPTH_Y / 2
)
M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_Y = (
    M6_DETECTOR_BODY_CENTER_Y - M6_DETECTOR_SHELL_SUPPORT_BOSS_DEPTH_Y / 2
)
M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_Z = (
    M6_DETECTOR_BODY_BOTTOM_Z + M6_DETECTOR_BODY_HEIGHT_Z / 2
)
M6_DETECTOR_SHELL_SUPPORT_BOSS_BOTTOM_Z = (
    M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_Z
    - M6_DETECTOR_SHELL_SUPPORT_BOSS_HEIGHT_Z / 2
)
M6_DETECTOR_SHELL_SUPPORT_BOSS_TOP_Z = (
    M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_Z
    + M6_DETECTOR_SHELL_SUPPORT_BOSS_HEIGHT_Z / 2
)
M6_DETECTOR_SHELL_SUPPORT_HOLE_ENTRY_X = M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_X
M6_DETECTOR_BALLHEAD_CENTER_X = (
    M6_DETECTOR_SHELL_SUPPORT_HOLE_ENTRY_X
    + (16.0 - M6_DETECTOR_SHELL_SUPPORT_STUD_ENGAGEMENT_X)
    + M6_DETECTOR_DETECTOR_BALLHEAD_GAP_X
    + M6_BALLHEAD_HOUSING_D / 2
)
M6_DETECTOR_BALLHEAD_CENTER_Y = M6_DETECTOR_BODY_CENTER_Y
M6_DETECTOR_BALLHEAD_CENTER_Z = M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_Z
M6_DETECTOR_BALLHEAD_NET_INTERFACE_BOTTOM_Z = (
    M6_DETECTOR_BALLHEAD_CENTER_Z
    - M6_BALLHEAD_HOUSING_LENGTH_X / 2
    - M6_BALLHEAD_BASE_T
    - M6_BALLHEAD_NET_STUD_LENGTH
)
M6_NET_CONNECTOR_ARM_MIN_X = M6_DETECTOR_BALLHEAD_CENTER_X - 14.0 / 2
M6_NET_CONNECTOR_ARM_MAX_X = POST_CENTER - POST_WIDTH / 2 + 2.0
M6_NET_CONNECTOR_ARM_BOTTOM_Z = M6_DETECTOR_BALLHEAD_NET_INTERFACE_BOTTOM_Z
M6_NET_CONNECTOR_ARM_TOP_Z = M6_NET_CONNECTOR_ARM_BOTTOM_Z + 10.0
M6_NET_CONNECTOR_LEG_MIN_X = POST_CENTER - POST_WIDTH / 2 - 6.0
M6_NET_CONNECTOR_LEG_MAX_X = M6_NET_CONNECTOR_ARM_MAX_X
M6_NET_CONNECTOR_LEG_BOTTOM_Z = M6_DETECTOR_BALLHEAD_NET_INTERFACE_BOTTOM_Z
M6_NET_CONNECTOR_LEG_TOP_Z = M6_DETECTOR_BALLHEAD_CENTER_Z + 6.0 + 4.0
M6_NET_CONNECTOR_SOCKET_BOTTOM_Z = M6_DETECTOR_BALLHEAD_NET_INTERFACE_BOTTOM_Z - 0.2
M6_NET_CONNECTOR_SOCKET_TOP_Z = (
    M6_DETECTOR_BALLHEAD_NET_INTERFACE_BOTTOM_Z
    + M6_BALLHEAD_NET_STUD_LENGTH
    + 0.2
)
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
M6_DETECTOR_BODY_DEPTH_Y = 56.0
M6_DETECTOR_BODY_LENGTH_X = 10.0
M6_DETECTOR_BODY_MARGIN_Z = 18.0
M6_DETECTOR_BODY_FRONT_MARGIN_X = 1.0
M6_DETECTOR_SHELL_WALL = 2.4
M6_DETECTOR_SHELL_CLEARANCE = 0.6
M6_DETECTOR_SHELL_BOTTOM_LIP_Z = 3.0
M6_DETECTOR_SHELL_TOP_LIP_Z = 3.0
M6_DETECTOR_SHELL_SPLIT_OVERLAP_X = 0.0
M6_DETECTOR_SHELL_SPLIT_CLEARANCE_X = 0.2
M6_DETECTOR_SHELL_CORNER_RADIUS = 4.0
M6_DETECTOR_FRONT_CAP_LENGTH_X = 18.0
M6_DETECTOR_FRONT_CAP_REDUCTION = 1.2
M6_DETECTOR_BODY_GROOVE_WIDTH_X = 4.0
M6_DETECTOR_BODY_GROOVE_DEPTH_Y = 1.2
M6_DETECTOR_BODY_GROOVE_MARGIN_Z = 5.0
M6_DETECTOR_SHELL_TONGUE_DEPTH_Y = 1.0
M6_DETECTOR_SHELL_TONGUE_CLEARANCE = 0.25
M6_DETECTOR_OPTICAL_BORE_D = 6.6
M6_DETECTOR_THREAD_CLEARANCE_D = 6.6
M6_DETECTOR_HEX_POCKET_AF = 8.0
M6_DETECTOR_HEX_POCKET_DEPTH_X = 2.1
M6_DETECTOR_HEX_POCKET_DEPTH_Y = 2.1
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
M6_SENSOR_INSTALL_OFFSET_X = 6.25
M6_SENSOR_INSTALLED_HEAD_MIN_X = 769.25
M6_SENSOR_INSTALLED_THREAD_TIP_X = 755.25
M6_SENSOR_INSTALLED_CABLE_EXIT_X = 772.25
M6_DETECTOR_NUT_MIN_X = 756.25
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

    body_min_x = M6_DETECTOR_BODY_MIN_X
    body_max_x = body_min_x + M6_DETECTOR_BODY_LENGTH_X
    body_bottom = M6_DETECTOR_BODY_BOTTOM_Z
    body_height = M6_DETECTOR_BODY_HEIGHT_Z
    body_top = body_bottom + body_height
    shell_min_x = M6_DETECTOR_SHELL_MIN_X
    shell_max_x = M6_DETECTOR_SHELL_MAX_X
    shell_bottom = M6_DETECTOR_SHELL_BOTTOM_Z
    shell_top = shell_bottom + M6_DETECTOR_SHELL_HEIGHT_Z
    front_max_x = M6_DETECTOR_SHELL_FRONT_MAX_X
    rear_min_x = M6_DETECTOR_SHELL_REAR_MIN_X
    front_width = front_max_x - shell_min_x
    rear_width = shell_max_x - rear_min_x
    for side, label in ((-1, "M6 x向分体壳/底盖与45° L型长条主体"), (1, "_nolegend_")):
        body_x = body_min_x if side > 0 else -body_max_x
        front_shell_x = shell_min_x if side > 0 else -front_max_x
        rear_shell_x = rear_min_x if side > 0 else -shell_max_x
        ax.add_patch(
            Rectangle(
                (front_shell_x, shell_bottom),
                front_width,
                shell_top - shell_bottom,
                facecolor="#6f7f90",
                edgecolor="#3e4b57",
                alpha=0.10,
                label="x- 前盖正球弧候选" if side < 0 else "_nolegend_",
            )
        )
        # The two x-segments are drawn as light outlines; keep the optical
        # parts above them so this overview remains readable.
        ax.add_patch(
            Rectangle(
                (rear_shell_x, shell_bottom),
                rear_width,
                shell_top - shell_bottom,
                facecolor="#8796a5",
                edgecolor="#3e4b57",
                alpha=0.08,
                label="x+ 后盖圆角矩形；背面中央为采购球头加厚 boss" if side < 0 else "_nolegend_",
            )
        )
        ax.add_patch(
            Rectangle(
                (
                    M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X
                    if side > 0
                    else -M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_X,
                    M6_DETECTOR_SHELL_SUPPORT_BOSS_BOTTOM_Z,
                ),
                M6_DETECTOR_SHELL_SUPPORT_BOSS_LENGTH_X,
                M6_DETECTOR_SHELL_SUPPORT_BOSS_HEIGHT_Z,
                facecolor="#8e989f",
                edgecolor="#38434c",
                linewidth=1.2,
                alpha=0.75,
                label="后盖背面中央加厚 M8 boss（采购球头）" if side < 0 else "_nolegend_",
            )
        )
        ax.add_patch(
            Rectangle(
                (body_x, body_bottom),
                M6_DETECTOR_BODY_LENGTH_X,
                body_top - body_bottom,
                facecolor="#e0a05b",
                edgecolor="#505963",
                alpha=0.94,
            )
        )
        for index in range(BEAM_COUNT):
            z = NET_HEIGHT + M6_SENSOR_FIRST_HEIGHT + index * M6_SENSOR_CENTER_PITCH
            head_x = (
                M6_SENSOR_INSTALLED_HEAD_MIN_X
                if side > 0
                else -M6_SENSOR_INSTALLED_HEAD_MIN_X - M6_SENSOR_HEAD_LENGTH_X
            )
            thread_x = (
                M6_SENSOR_INSTALLED_THREAD_TIP_X
                if side > 0
                else -M6_SENSOR_INSTALLED_THREAD_TIP_X - M6_SENSOR_MOUNT_STEM_LENGTH
            )
            cable_x = (
                M6_SENSOR_INSTALLED_CABLE_EXIT_X - M6_SENSOR_BODY_D / 2
                if side > 0
                else -M6_SENSOR_INSTALLED_CABLE_EXIT_X - M6_SENSOR_BODY_D / 2
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
                M6_SENSOR_INSTALLED_THREAD_TIP_X
                if side > 0
                else -M6_SENSOR_INSTALLED_THREAD_TIP_X,
                z,
                marker="o",
                markersize=2.8,
                color="#20252b",
            )
            # One purchased nut sits directly on the outward body face.  It
            # is not a countersunk/embedded fixing screw and there is no
            # second lock nut in the current installation contract.
            nut_x = (
                M6_DETECTOR_NUT_MIN_X
                if side > 0
                else -M6_DETECTOR_NUT_MIN_X - M6_SENSOR_LOCK_NUT_H
            )
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
                ax.plot([], [], color="#3c65d7", linewidth=3.0, label="蓝色护套：局部 z- 绕光束 x 轴 -45°")
                ax.plot([], [], color="#c1c7cc", linewidth=2.0, label="水平 M6 外丝 / 光学轴")

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
    body_min_x = M6_DETECTOR_BODY_MIN_X
    body_max_x = body_min_x + M6_DETECTOR_BODY_LENGTH_X
    body_bottom = M6_DETECTOR_BODY_BOTTOM_Z
    body_height = M6_DETECTOR_BODY_HEIGHT_Z
    shell_min_x = M6_DETECTOR_SHELL_MIN_X
    shell_max_x = M6_DETECTOR_SHELL_MAX_X
    shell_bottom = M6_DETECTOR_SHELL_BOTTOM_Z
    shell_height = M6_DETECTOR_SHELL_HEIGHT_Z
    ax.add_patch(
        Rectangle(
            (shell_min_x - TABLE_EDGE, shell_bottom),
            shell_max_x - shell_min_x,
            shell_height,
            facecolor="#8796a5",
            edgecolor="#3e4b57",
            alpha=0.12,
            label="x−/x+ PETG 分体壳包络",
        )
    )
    ax.add_patch(
        Rectangle(
            (body_min_x - TABLE_EDGE, body_bottom),
            M6_DETECTOR_BODY_LENGTH_X,
            body_height,
            facecolor="#e0a05b",
            edgecolor="#505963",
            alpha=0.94,
            label="M6 PETG 长条主体（56×10 mm 截面；未来可 CNC）",
        )
    )
    boss_min_x = M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X
    boss_max_x = M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_X
    boss_bottom_z = M6_DETECTOR_SHELL_SUPPORT_BOSS_BOTTOM_Z
    boss_height_z = M6_DETECTOR_SHELL_SUPPORT_BOSS_HEIGHT_Z
    ax.add_patch(
        Rectangle(
            (boss_min_x - TABLE_EDGE, boss_bottom_z),
            boss_max_x - boss_min_x,
            boss_height_z,
            facecolor="#8e989f",
            edgecolor="#38434c",
            linewidth=1.2,
            alpha=0.72,
            label="后盖 x+ 背面中央加厚 M8 boss",
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
    ballhead_x = M6_DETECTOR_BALLHEAD_CENTER_X - TABLE_EDGE
    ballhead_z = body_bottom + body_height / 2
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
        [
            ballhead_z
            - M6_BALLHEAD_HOUSING_LENGTH_X / 2
            - M6_BALLHEAD_BASE_T
            - 28.0,
            ballhead_z - M6_BALLHEAD_HOUSING_LENGTH_X / 2 - M6_BALLHEAD_BASE_T,
        ],
        color="#b6bdc3",
        linewidth=4.0,
        label="采购球头 z− 接口（由金属 90°连接器承接）",
    )
    ax.plot(
        [boss_max_x - TABLE_EDGE, ballhead_x - M6_BALLHEAD_HOUSING_D / 2],
        [body_bottom + body_height / 2, ballhead_z],
        color="#b6bdc3",
        linewidth=4.0,
        label="采购球头 M8 外牙 → 后盖 x+ 背面中央 boss",
    )
    # The ballhead's z- interface is not the net-clamp post itself.  A
    # purchased metal 90-degree connector starts at the interface's lowest
    # end, runs along x, then rises to the post's upper x-through slot.  Draw
    # this before the orange post so the 2 mm overlap is visibly carried by
    # the post rather than appearing as a floating gray plate.
    connector_arm_min_x = M6_NET_CONNECTOR_ARM_MIN_X - TABLE_EDGE
    connector_arm_max_x = M6_NET_CONNECTOR_ARM_MAX_X - TABLE_EDGE
    connector_leg_min_x = M6_NET_CONNECTOR_LEG_MIN_X - TABLE_EDGE
    connector_leg_max_x = M6_NET_CONNECTOR_LEG_MAX_X - TABLE_EDGE
    ax.add_patch(
        Rectangle(
            (connector_arm_min_x, M6_NET_CONNECTOR_ARM_BOTTOM_Z),
            connector_arm_max_x - connector_arm_min_x,
            M6_NET_CONNECTOR_ARM_TOP_Z - M6_NET_CONNECTOR_ARM_BOTTOM_Z,
            facecolor="#58626a",
            edgecolor="#26313b",
            alpha=0.92,
            label="采购金属 90°连接器：从球头 z−最低端起",
        )
    )
    ax.add_patch(
        Rectangle(
            (connector_leg_min_x, M6_NET_CONNECTOR_LEG_BOTTOM_Z),
            connector_leg_max_x - connector_leg_min_x,
            M6_NET_CONNECTOR_LEG_TOP_Z - M6_NET_CONNECTOR_LEG_BOTTOM_Z,
            facecolor="#58626a",
            edgecolor="#26313b",
            alpha=0.92,
            label="连接器竖直腿 → 网夹立柱两枚 M6 贯穿孔",
        )
    )
    ax.add_patch(
        Rectangle(
            (ballhead_x - 7.0, M6_NET_CONNECTOR_SOCKET_BOTTOM_Z),
            14.0,
            M6_NET_CONNECTOR_SOCKET_TOP_Z - M6_NET_CONNECTOR_SOCKET_BOTTOM_Z,
            facecolor="#58626a",
            edgecolor="#26313b",
            linewidth=1.0,
            alpha=0.34,
            label="球头 z− 接口套筒（Ø14 / Ø8.6）",
        )
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
        label="蓝色护套：局部 z- 绕 x 轴 -45°",
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
    inset.set_xlabel("y（后方为 -）", fontsize=7)
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


def front_arc_points(x_min: float, x_max: float, y_min: float, y_max: float):
    """Return the z+ plan-view positive arc used by the x- front cover."""

    length = x_max - x_min
    y_center = (y_min + y_max) / 2
    half_width = (y_max - y_min) / 2
    points = [(x_max, y_min)]
    for angle in range(-90, 91, 5):
        radians = math.radians(angle)
        points.append(
            (
                x_max - length * math.cos(radians),
                y_center + half_width * math.sin(radians),
            )
        )
    points.append((x_max, y_max))
    return points


def rounded_rect_points(
    x_min: float, x_max: float, y_min: float, y_max: float, radius: float
):
    """Return a sampled rounded rectangle in the x/y plan plane."""

    radius = min(radius, (x_max - x_min) / 2, (y_max - y_min) / 2)
    points = [(x_min + radius, y_min), (x_max - radius, y_min)]
    for start, end, cx, cy in (
        (-90, 0, x_max - radius, y_min + radius),
        (0, 90, x_max - radius, y_max - radius),
        (90, 180, x_min + radius, y_max - radius),
        (180, 270, x_min + radius, y_min + radius),
    ):
        for angle in range(start, end + 1, 10):
            radians = math.radians(angle)
            points.append((cx + radius * math.cos(radians), cy + radius * math.sin(radians)))
    return points


def draw_top(ax) -> None:
    """Draw the user's z+ shell silhouette with x- at the top of the panel."""

    body_min_x = M6_DETECTOR_BODY_MIN_X
    body_max_x = body_min_x + M6_DETECTOR_BODY_LENGTH_X
    shell_split_x = M6_DETECTOR_SHELL_SPLIT_X
    shell_min_x = M6_DETECTOR_SHELL_MIN_X
    shell_max_x = M6_DETECTOR_SHELL_MAX_X
    shell_min_y = -M6_DETECTOR_BODY_DEPTH_Y / 2 - M6_DETECTOR_SHELL_WALL
    shell_max_y = M6_DETECTOR_BODY_DEPTH_Y / 2 + M6_DETECTOR_SHELL_WALL
    front_max_x = M6_DETECTOR_SHELL_FRONT_MAX_X
    rear_min_x = M6_DETECTOR_SHELL_REAR_MIN_X

    # Plot y horizontally and -(x - split) vertically.  This puts x- (the
    # optical/front end) above x+ (the cable/rear end), matching the sketch.
    def plan(points):
        return [(y, -(x - shell_split_x)) for x, y in points]

    front = plan(front_arc_points(shell_min_x, front_max_x, shell_min_y, shell_max_y))
    rear = plan(
        rounded_rect_points(
            rear_min_x,
            shell_max_x,
            shell_min_y,
            shell_max_y,
            M6_DETECTOR_SHELL_CORNER_RADIUS,
        )
    )
    ax.add_patch(
        Polygon(
            front,
            closed=True,
            facecolor="#3567d6",
            edgecolor="#173d9b",
            linewidth=1.8,
            alpha=0.32,
            label="x- 前盖：正圆弧俯视轮廓",
        )
    )
    ax.add_patch(
        Polygon(
            rear,
            closed=True,
            facecolor="#36a852",
            edgecolor="#197331",
            linewidth=1.8,
            alpha=0.28,
            label="x+ 后盖：圆角矩形俯视轮廓",
        )
    )

    body_plan = plan(
        [
            (body_min_x, -M6_DETECTOR_BODY_DEPTH_Y / 2),
            (body_max_x, -M6_DETECTOR_BODY_DEPTH_Y / 2),
            (body_max_x, M6_DETECTOR_BODY_DEPTH_Y / 2),
            (body_min_x, M6_DETECTOR_BODY_DEPTH_Y / 2),
        ]
    )
    ax.add_patch(
        Polygon(
            body_plan,
            closed=True,
            facecolor="#9da7b0",
            edgecolor="#4d5964",
            linewidth=1.2,
            alpha=0.85,
            label="PETG 长条主体（10 × 56 mm；未来可 CNC）",
        )
    )
    boss_plan = plan(
        [
            (M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X,
             M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_Y),
            (M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_X,
             M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_Y),
            (M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_X,
             M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_Y),
            (M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X,
             M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_Y),
        ]
    )
    ax.add_patch(
        Polygon(
            boss_plan,
            closed=True,
            facecolor="#8e989f",
            edgecolor="#38434c",
            linewidth=1.5,
            alpha=0.86,
            label="后盖背面中央加厚 M8 boss（采购球头）",
        )
    )
    cable_hole_y = 0.0
    cable_hole_plot = (cable_hole_y, -(M6_SENSOR_INSTALLED_CABLE_EXIT_X - shell_split_x))
    ax.add_patch(
        Circle(
            cable_hole_plot,
            M6_DETECTOR_CABLE_EXIT_D / 2,
            facecolor="#f7f9fb",
            edgecolor="#26333e",
            linewidth=1.2,
            alpha=0.95,
            label="底盖 D12 mm 统一套管孔",
        )
    )
    ax.plot(
        [shell_min_y, shell_max_y],
        [0, 0],
        linestyle=(0, (5, 3)),
        color="#4d5964",
        linewidth=1.0,
        label="前/后盖分型边界（非连线）",
    )
    ax.annotate(
        "x- 光学端",
        xy=(0, -(shell_min_x - shell_split_x)),
        xytext=(0, -(shell_min_x - shell_split_x) + 3),
        ha="center",
        color="#173d9b",
        arrowprops={"arrowstyle": "-|>", "color": "#173d9b"},
        fontsize=9,
    )
    ax.annotate(
        "x+ 线缆端",
        xy=(0, -(shell_max_x - shell_split_x)),
        xytext=(0, -(shell_max_x - shell_split_x) - 3),
        ha="center",
        color="#197331",
        arrowprops={"arrowstyle": "-|>", "color": "#197331"},
        fontsize=9,
    )
    ax.set_xlim(-36, 36)
    ax.set_ylim(-24, 16)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("z+ 俯视：前盖正弧 + 后盖圆角矩形")
    ax.set_xlabel("y（球台前后）/ mm")
    ax.set_ylabel("-(x-分型面) / mm；上方为 x- 光学端")
    ax.grid(True, alpha=0.22)
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="lower center", fontsize=7, ncol=2)


def make_preview() -> None:
    fig, (front, side, top) = plt.subplots(1, 3, figsize=(21, 8), constrained_layout=True)
    draw_front(front)
    draw_side(side)
    draw_top(top)
    fig.suptitle(
        "Pingpang SmartGear: integrated net stand, M6 x-split shell, and z+ footprint (intent, not STL validation)",
        fontsize=14,
    )
    fig.savefig(OUT, dpi=160)
    print(OUT)


if __name__ == "__main__":
    make_preview()
