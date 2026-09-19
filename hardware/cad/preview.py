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
POST_DEPTH = 38.0
NET_POST_OUTBOARD_EXTENSION = 152.5
POST_OFFSET = 138.5
# The fixed gray clamp ends flush with the broad lower post footprint; keep
# this literal synchronized with the SCAD first-article datum.
CLAMP_OUTER_EXTENSION = 3.5
CLAMP_REACH_INBOARD = 62.0
CLAMP_PAD_DEPTH = 58.0
# Both structural clamp tongues extend the same additional 20 mm into the
# tabletop; the lower pressure hardware is centered in that effective tongue.
CLAMP_TONGUE_EXTRA_LENGTH_X = 20.0
# The upper and lower structural clamp jaws are both 14 mm thick.  The upper
# tabletop rubber is external/glued; the lower contact part is a rigid round
# printed pad with a shallow socket for the coarse printed screw's flat ball tip.
CLAMP_PAD_T = 14.0
CLAMP_CLEARANCE = 1.5
POST_CENTER = TABLE_EDGE + POST_OFFSET
CLAMP_SCREW_INSET = 41.0
CLAMP_SCREW_D = 8.0  # legacy M8 envelope retained for the parameter mirror
CLAMP_PRINTED_SCREW_D = 12.0
CLAMP_SCREW_CAPTURE_EXTENSION = 2.0
# The knob keeps the same Ø36 mm envelope while using a rounded 18-lobe
# hand-grip ring: Ø30 mm root valleys and Ø5 mm circular lobes.
CLAMP_KNOB_D = 36.0
CLAMP_KNOB_GRIP_ROOT_D = 30.0
CLAMP_KNOB_GRIP_TOOTH_COUNT = 18.0
CLAMP_KNOB_GRIP_TOOTH_D = 5.0
CLAMP_KNOB_GRIP_TOOTH_PITCH_R = (
    CLAMP_KNOB_D / 2 - CLAMP_KNOB_GRIP_TOOTH_D / 2
)
CLAMP_KNOB_H = 20.0
CLAMP_SCREW_TO_KNOB_TOP_BASE = 32.0
CLAMP_SCREW_EXTRA_LENGTH_Z = 12.0
CLAMP_SCREW_TO_KNOB_TOP = CLAMP_SCREW_TO_KNOB_TOP_BASE + CLAMP_SCREW_EXTRA_LENGTH_Z
CLAMP_NUT_AF = 16.0
CLAMP_BODY_NUT_H = 11.5
CLAMP_DRIVE_NUT_H = 6.0
# Compatibility name used by the static preview parameter mirror; the active
# body nut uses the same 11.5 mm height.
CLAMP_NUT_H = 11.5
CLAMP_NUT_CLEARANCE = 0.35
CLAMP_KNOB_NUT_GAP = 0.6
CLAMP_KNOB_NUT_STACK = 2 * CLAMP_DRIVE_NUT_H + CLAMP_KNOB_NUT_GAP
CLAMP_TOP_PAD_X = -CLAMP_REACH_INBOARD + 8.0
CLAMP_TOP_PAD_WIDTH = 96.0
CLAMP_TOP_PAD_DEPTH = 48.0
CLAMP_TOP_PAD_T = 2.0
# The fixed-net upright starts on the gray/yellow C-clamp seat. The net datum
# remains one net height; the active post ends at the purchased ballhead's
# flat seating plane and carries its central M8 tap pilot.
CLAMP_SLIDE_SEAT_Z = CLAMP_TOP_PAD_T + CLAMP_PAD_T
POST_C_CLAMP_OVERLAP_DEPTH_Z = 0.0
POST_BOTTOM = CLAMP_SLIDE_SEAT_Z
# Formal 779f046 C-scheme interface, mirrored in the same relative x frame as
# the side elevation (absolute SCAD x minus TABLE_EDGE). The green SKP ROOT
# base enters the gray pocket from x+; the yellow upright starts at z=16.
SKP_BASE_MIN_X = 97.3
SKP_BASE_MAX_X = 156.0
SKP_BASE_MIN_Y = -23.0
SKP_BASE_MAX_Y = 23.0
SKP_BASE_BOTTOM_Z = -4.0
SKP_BASE_TOP_Z = 16.0
SKP_BASE_MAIN_MIN_X = 112.3
SKP_BASE_DETENT_X = 146.0
SKP_BASE_FASTENER_X = 105.3
SKP_BASE_FASTENER_Y = (-11.0, 11.0)
# Historical shoe/rail parameters are retained only so old reports can still
# parse the source; the active preview draws the direct solid taper below.
CLAMP_SLIDE_SHOE_DROP_Z = 14.0
CLAMP_SLIDE_POST_FOOT_ROOT_OVERLAP_Z = 0.25
CLAMP_SLIDE_POST_FOOT_TRANSITION_SECTION_COUNT = 96
CLAMP_SLIDE_POST_FOOT_TRANSITION_SLICE_Z = 0.4
CLAMP_SLIDE_POST_FOOT_POST_FUSION_INSET = 0.02
CLAMP_SLIDE_POST_FOOT_ANKLE_INBOARD_EXTENSION_X = 8.0
CLAMP_SLIDE_POST_FOOT_ROOT_WIDTH_Y = 20.0
# Historical clamp/post slide parameters are mirrored only for compatibility;
# none of these legacy shoe/rail values is drawn as an active component.
CLAMP_SLIDE_SPLIT_X_ABS = 885.5
# Historical compatibility values only; no hexagonal shoes or mother track is
# drawn or exported by the active design.
CLAMP_SLIDE_SHOE_DEEPENING_X = 8.0
CLAMP_SLIDE_RECEIVER_LENGTH_X = 81.0
CLAMP_SLIDE_TONGUE_ATTACH_X = 35.7
CLAMP_SLIDE_RAIL_Y_OUTER = 18.0
CLAMP_SLIDE_RAIL_HEAD_WIDTH_Y = 20.0
CLAMP_SLIDE_RAIL_NECK_WIDTH_Y = 17.5
CLAMP_SLIDE_RAIL_HEAD_HEIGHT_Z = 6.5
CLAMP_SLIDE_RAIL_NECK_HEIGHT_Z = 5.5
CLAMP_SLIDE_RAIL_HEIGHT_Z = (
    CLAMP_SLIDE_RAIL_HEAD_HEIGHT_Z + CLAMP_SLIDE_RAIL_NECK_HEIGHT_Z
)
CLAMP_SLIDE_RAIL_CENTER_Z = 9.0 - CLAMP_SLIDE_SHOE_DROP_Z
CLAMP_SLIDE_RAIL_FLOOR_Z = (
    CLAMP_SLIDE_RAIL_CENTER_Z - CLAMP_SLIDE_RAIL_HEIGHT_Z / 2
)
CLAMP_SLIDE_POST_FOOT_SHOE_BURIED_OVERLAP_Z = 0.2
CLAMP_SLIDE_POST_FOOT_SHOE_OVERLAP_Z = (
    CLAMP_SLIDE_RAIL_HEIGHT_Z
    + CLAMP_SLIDE_POST_FOOT_SHOE_BURIED_OVERLAP_Z
)
CLAMP_SLIDE_POST_FOOT_BOTTOM_Z = (
    CLAMP_SLIDE_RAIL_FLOOR_Z
    + CLAMP_SLIDE_RAIL_HEIGHT_Z
    - CLAMP_SLIDE_POST_FOOT_SHOE_OVERLAP_Z
)
CLAMP_SLIDE_POST_FOOT_ANKLE_HEIGHT_Z = (
    CLAMP_SLIDE_SEAT_Z - CLAMP_SLIDE_POST_FOOT_BOTTOM_Z
)
CLAMP_SLIDE_POST_FOOT_TRANSITION_START_Z = CLAMP_SLIDE_POST_FOOT_BOTTOM_Z
CLAMP_SLIDE_POST_FOOT_TRANSITION_SIDE_START_Z = (
    CLAMP_SLIDE_RAIL_FLOOR_Z + CLAMP_SLIDE_RAIL_HEIGHT_Z
)
CLAMP_SLIDE_POST_FOOT_TRANSITION_END_Z = CLAMP_SLIDE_SEAT_Z
CLAMP_SLIDE_CLEARANCE = 0.35
CLAMP_SLIDE_POST_FOOT_CROSS_TIE_TOP_Z = (
    -CLAMP_SLIDE_CLEARANCE - 0.1
)
CLAMP_SLIDE_POST_FOOT_CROSS_TIE_HEIGHT_Z = 3.2
CLAMP_SLIDE_POST_FOOT_CROSS_TIE_BOTTOM_Z = (
    CLAMP_SLIDE_POST_FOOT_CROSS_TIE_TOP_Z
    - CLAMP_SLIDE_POST_FOOT_CROSS_TIE_HEIGHT_Z
)
CLAMP_SLIDE_POST_FOOT_TOP_Z = (
    CLAMP_SLIDE_SEAT_Z + CLAMP_SLIDE_POST_FOOT_ROOT_OVERLAP_Z
)
CLAMP_SLIDE_RECEIVER_FLOOR_Z = CLAMP_SLIDE_RAIL_FLOOR_Z - CLAMP_SLIDE_CLEARANCE
CLAMP_SLIDE_RECEIVER_TOP_Z = (
    CLAMP_SLIDE_RAIL_FLOOR_Z
    + CLAMP_SLIDE_RAIL_HEIGHT_Z
    + CLAMP_SLIDE_CLEARANCE
)
CLAMP_SLIDE_RECEIVER_NECK_HEIGHT_Z = (
    CLAMP_SLIDE_RECEIVER_TOP_Z
    - CLAMP_SLIDE_RECEIVER_FLOOR_Z
    - CLAMP_SLIDE_RAIL_HEAD_HEIGHT_Z
    - CLAMP_SLIDE_CLEARANCE
)
CLAMP_SLIDE_SPLIT_X = CLAMP_SLIDE_SPLIT_X_ABS - TABLE_EDGE
CLAMP_SLIDE_TONGUE_MIN_X_ABS = 849.5 - CLAMP_SLIDE_SHOE_DEEPENING_X
CLAMP_SLIDE_TONGUE_MIN_X = CLAMP_SLIDE_TONGUE_MIN_X_ABS - TABLE_EDGE
CLAMP_SLIDE_TONGUE_LENGTH_X = 79.0
CLAMP_SLIDE_POST_SEAT_CLEARANCE_X = 1.0
CLAMP_SLIDE_POST_SEAT_END_X = (
    POST_OFFSET + POST_WIDTH / 2 + CLAMP_OUTER_EXTENSION
)
# These legacy coordinates are retained for report compatibility only. The
# active side view uses the direct post transition and never draws a foot-root
# band across the absolute x coordinate range.
CLAMP_SLIDE_POST_FOOT_ROOT_MAX_X = POST_OFFSET + POST_WIDTH / 2 + 6.2
CLAMP_SLIDE_POST_FOOT_ROOT_MIN_X = (
    CLAMP_SLIDE_SPLIT_X - CLAMP_SLIDE_POST_FOOT_ANKLE_INBOARD_EXTENSION_X
)
CLAMP_SLIDE_POST_FOOT_CROSS_TIE_LENGTH_X = 10.0
CLAMP_SLIDE_POST_FOOT_CROSS_TIE_BOTTOM_HALF_Y = 7.5
CLAMP_SLIDE_POST_FOOT_CROSS_TIE_TOP_HALF_Y = 6.5
CLAMP_SLIDE_POST_FOOT_CROSS_TIE_BRIDGE_HALF_Y = 16.0
CLAMP_SLIDE_POST_FOOT_BRIDGE_MAX_X = (
    CLAMP_SLIDE_POST_FOOT_ROOT_MAX_X - 0.8
)
CLAMP_SLIDE_POST_FOOT_BRIDGE_MIN_X = (
    CLAMP_SLIDE_POST_FOOT_BRIDGE_MAX_X
    - CLAMP_SLIDE_POST_FOOT_CROSS_TIE_LENGTH_X
)
# Historical detent coordinates are retained for compatibility; the green line
# in the active preview is only a mechanical reference, not a detent.
CLAMP_SLIDE_DETENT_X = (
    CLAMP_SLIDE_POST_FOOT_BRIDGE_MIN_X
    + CLAMP_SLIDE_POST_FOOT_CROSS_TIE_LENGTH_X / 2
)
CLAMP_LOWER_ARM_CLEARANCE = 10.0
CLAMP_LOWER_ARM_TOP = -TABLE_THICKNESS - CLAMP_LOWER_ARM_CLEARANCE
CLAMP_LOWER_ARM_BOTTOM = CLAMP_LOWER_ARM_TOP - CLAMP_PAD_T
CLAMP_PRESSURE_PAD_WIDTH = 50.0
CLAMP_PRESSURE_PAD_DEPTH = 50.0
CLAMP_PRESSURE_PAD_T = 4.0
CLAMP_PRESSURE_PAD_SOCKET_DEPTH = 2.0
CLAMP_PRESSURE_PAD_TOP = -TABLE_THICKNESS - CLAMP_CLEARANCE
CLAMP_PRESSURE_PAD_BOTTOM = CLAMP_PRESSURE_PAD_TOP - CLAMP_PRESSURE_PAD_T
CLAMP_SCREW_X = -CLAMP_SCREW_INSET
CLAMP_TONGUE_REACH_INBOARD = CLAMP_REACH_INBOARD + CLAMP_TONGUE_EXTRA_LENGTH_X
CLAMP_PAD_X = -CLAMP_TONGUE_REACH_INBOARD
CLAMP_PAD_OUTER_X = POST_OFFSET + POST_WIDTH / 2 + CLAMP_OUTER_EXTENSION
CLAMP_SLIDE_DETENT_BALL_OFFSET_Z = 0.95
CLAMP_SLIDE_DETENT_BALL_CENTER_Z = (
    CLAMP_SLIDE_POST_FOOT_CROSS_TIE_BOTTOM_Z
    + CLAMP_SLIDE_DETENT_BALL_OFFSET_Z
)
CLAMP_OUTER_WALL_WIDTH = 22.0
CLAMP_OUTER_WALL_X = CLAMP_PAD_OUTER_X - CLAMP_OUTER_WALL_WIDTH
CLAMP_REINFORCEMENT_INBOARD_OFFSET_X = 3.0
CLAMP_REINFORCEMENT_NEAR_TABLE_THICKNESS_Z = 40.0
CLAMP_REINFORCEMENT_DEPTH_Y = 58.0
CLAMP_SOLID_BRIDGE_CLEARANCE_X = 0.2
CLAMP_SOLID_BRIDGE_START_X = CLAMP_SOLID_BRIDGE_CLEARANCE_X
CLAMP_REINFORCEMENT_START_X = -CLAMP_REINFORCEMENT_INBOARD_OFFSET_X
CLAMP_REINFORCEMENT_END_X = CLAMP_PAD_OUTER_X - 0.2
CLAMP_LOWER_ARM_X = CLAMP_PAD_X
CLAMP_SCREW_TOP = CLAMP_PRESSURE_PAD_BOTTOM + CLAMP_PRESSURE_PAD_SOCKET_DEPTH
CLAMP_KNOB_TOP = CLAMP_SCREW_TOP - CLAMP_SCREW_TO_KNOB_TOP
CLAMP_KNOB_BOTTOM = CLAMP_KNOB_TOP - CLAMP_KNOB_H
CLAMP_KNOB_NUT_TOP = CLAMP_KNOB_TOP - CLAMP_NUT_CLEARANCE / 2
CLAMP_KNOB_DRIVE_NUT_Z = CLAMP_KNOB_NUT_TOP - CLAMP_DRIVE_NUT_H
CLAMP_KNOB_LOCK_NUT_Z = (
    CLAMP_KNOB_DRIVE_NUT_Z - CLAMP_KNOB_NUT_GAP - CLAMP_DRIVE_NUT_H
)
CLAMP_SCREW_BOTTOM = CLAMP_KNOB_LOCK_NUT_Z - CLAMP_SCREW_CAPTURE_EXTENSION
CLAMP_BODY_NUT_Z = CLAMP_LOWER_ARM_BOTTOM + CLAMP_NUT_CLEARANCE
CLAMP_REINFORCEMENT_TOP_Z = CLAMP_LOWER_ARM_TOP
CLAMP_REINFORCEMENT_NEAR_TABLE_BOTTOM_Z = (
    CLAMP_REINFORCEMENT_TOP_Z - CLAMP_REINFORCEMENT_NEAR_TABLE_THICKNESS_Z
)
CLAMP_REINFORCEMENT_OUTER_THICKNESS_Z = CLAMP_PAD_T
CLAMP_REINFORCEMENT_OUTER_BOTTOM_Z = (
    CLAMP_REINFORCEMENT_TOP_Z - CLAMP_REINFORCEMENT_OUTER_THICKNESS_Z
)
CLAMP_SOLID_BRIDGE_TOP_Z = CLAMP_TOP_PAD_T + CLAMP_PAD_T
OPTICAL_BEAM_EDGE_OVERLAP = 0.5
OPTICAL_BEAM_AXIS_X = TABLE_EDGE + OPTICAL_BEAM_EDGE_OVERLAP
NET_HEIGHT = 152.5
# The net and the full-height U clip share the fixed C-clamp seat as their
# lower datum.  Keep the lower/top values explicit so the preview cannot
# silently draw the clip into the dark lower clamp body again.
NET_FIXTURE_BOTTOM_Z = CLAMP_SLIDE_SEAT_Z
NET_POST_TOP_Z = NET_FIXTURE_BOTTOM_Z + NET_HEIGHT
# Kept as a source-mirroring legacy value for the parameter coverage test; the
# active drawing deliberately has no top rail.
NET_RAIL_HEIGHT = 10.0
NET_SHEET_T = 1.2
NET_PASSAGE_WIDTH_Y = 3.0
# Current first-article derived result: raw shell bottom 141.5 mm, net top
# 168.5 mm, and 2 mm clearance. The OpenSCAD source derives this value from
# those inputs; this lightweight mirror keeps the resulting scalar explicit.
M6_DETECTOR_MOUNT_RAISE_Z = 29.0
# Active net retention geometry: a full-height U clip slides into the outboard
# pocket after the fabric has passed through the 3 mm post passage.  The old
# cylinder-named values above remain only as compatibility aliases for old
# preview consumers and are not drawn.
NET_CLAMP_CLIP_CLEARANCE_X = 0.2
NET_CLAMP_CLIP_LENGTH_X = 26.1
NET_CLAMP_CLIP_INNER_X = POST_CENTER + POST_WIDTH / 2 - 21.8
NET_CLAMP_CLIP_OUTER_X = NET_CLAMP_CLIP_INNER_X + NET_CLAMP_CLIP_LENGTH_X
NET_CLAMP_CLIP_CROSSBAR_T_X = 3.0
NET_CLAMP_CHANNEL_DEPTH_X = POST_WIDTH
NET_CLAMP_CYLINDER_INSERTION_DEPTH_X = POST_WIDTH
NET_CLAMP_CHANNEL_BACK_WALL_T_X = 3.0
NET_CLAMP_CYLINDER_INTERFERENCE_D = 14.0
NET_CLAMP_CYLINDER_ACTUAL_D = NET_CLAMP_CYLINDER_INTERFERENCE_D - 2.0
NET_CLAMP_CHANNEL_SIDE_CLEARANCE = 0.6
NET_CLAMP_CHANNEL_BACK_CLEARANCE = 0.6
NET_CLAMP_CHANNEL_WIDTH_Y = (
    NET_CLAMP_CYLINDER_INTERFERENCE_D
    + 2 * NET_CLAMP_CHANNEL_SIDE_CLEARANCE
)
NET_CLAMP_CHANNEL_BOTTOM_Z = NET_FIXTURE_BOTTOM_Z
NET_CLAMP_CHANNEL_TOP_Z = NET_FIXTURE_BOTTOM_Z + NET_HEIGHT
NET_CLAMP_CHANNEL_VOID_MIN_X = (
    POST_CENTER
    + POST_WIDTH / 2
    - NET_CLAMP_CHANNEL_DEPTH_X
    + NET_CLAMP_CHANNEL_BACK_WALL_T_X
)
NET_CLAMP_CHANNEL_VOID_MAX_X = POST_CENTER + POST_WIDTH / 2 + 4.5
NET_CLAMP_CYLINDER_CENTER_X = (
    NET_CLAMP_CHANNEL_VOID_MIN_X
    + NET_CLAMP_CYLINDER_INTERFERENCE_D / 2
    + NET_CLAMP_CHANNEL_BACK_CLEARANCE
)
NET_CLAMP_CYLINDER_HEIGHT = NET_CLAMP_CHANNEL_TOP_Z - NET_CLAMP_CHANNEL_BOTTOM_Z
NET_CLAMP_KEEPER_Z = NET_CLAMP_CHANNEL_BOTTOM_Z + 72.0
NET_CLAMP_KEEPER_HEIGHT_Z = 8.0
NET_CLAMP_KEEPER_X_MIN = NET_CLAMP_CLIP_INNER_X + 1.5
NET_CLAMP_KEEPER_X_MAX = NET_CLAMP_CLIP_INNER_X + 2.5
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
POST_TOP_MARGIN = 18.0
# The active post top is the installed ballhead base seating plane.  With the
# current raw ballhead base bottom (231.5 mm) and derived 29 mm lift this is
# 260.5 mm; it is intentionally not the old full-array envelope.
POST_TOP = 260.5
M6_SENSOR_AXIS_X = OPTICAL_BEAM_AXIS_X
M6_SENSOR_RAIL_X = 788.0
M6_SENSOR_MOUNT_HOLE_X = 766.25
M6_RAIL_TAB_MIN_X = M6_SENSOR_AXIS_X + 1.0
M6_RAIL_TAB_MAX_X = M6_SENSOR_RAIL_X + M6_RAIL_T
M6_BALLHEAD_BALL_D = 13.0
M6_BALLHEAD_HOUSING_D = 28.0
M6_BALLHEAD_HOUSING_LENGTH_X = 26.0
M6_BALLHEAD_BODY_DEPTH_Y = 24.0
M6_BALLHEAD_BODY_CORNER_RADIUS = 4.0
M6_BALLHEAD_BALL_SOCKET_D = 17.0
M6_BALLHEAD_SIDE_PLATE_D = 24.0
M6_BALLHEAD_SIDE_PLATE_T_X = 4.0
M6_BALLHEAD_LOCK_KNOB_D = 18.0
M6_BALLHEAD_LOCK_KNOB_T_Y = 8.0
M6_BALLHEAD_LOCK_KNOB_RIDGE_COUNT = 24.0
M6_BALLHEAD_BASE_D = 32.0
M6_BALLHEAD_BASE_T = 8.0
M6_BALLHEAD_SENSOR_STUD_D = 6.35
M6_BALLHEAD_SENSOR_THREAD_CORE_D = 5.35
M6_BALLHEAD_SENSOR_THREAD_PITCH = 1.27
M6_BALLHEAD_NET_STUD_D = 8.0
M6_BALLHEAD_NET_STUD_LENGTH = 28.0
M6_BALLHEAD_NET_THREAD_CORE_D = 6.6
M6_BALLHEAD_NET_THREAD_PITCH = 1.25
M6_BALLHEAD_TOP_NUT_AF = 11.1
M6_BALLHEAD_TOP_NUT_H = 5.5
M6_BALLHEAD_BOTTOM_NUT_AF = 13.0
M6_BALLHEAD_BOTTOM_NUT_H = 6.5
M6_BALLHEAD_NUT_CLEARANCE = 0.35
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
M6_DETECTOR_SHELL_SUPPORT_GUSSET_X_OVERLAP = 0.2
M6_DETECTOR_SHELL_SUPPORT_GUSSET_ROOT_WIDTH_Y = 5.0
M6_DETECTOR_SHELL_SUPPORT_GUSSET_WALL_WIDTH_Y = 2.4
M6_DETECTOR_SHELL_SUPPORT_GUSSET_HEIGHT_Z = 12.0
M6_DETECTOR_SHELL_SUPPORT_HOLE_D = 7.0
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
M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_X = (
    M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X
    + M6_DETECTOR_SHELL_SUPPORT_BOSS_LENGTH_X / 2
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
M6_DETECTOR_SHELL_SUPPORT_GUSSET_MIN_X = (
    M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X
    - M6_DETECTOR_SHELL_SUPPORT_GUSSET_X_OVERLAP
)
M6_DETECTOR_SHELL_SUPPORT_GUSSET_MAX_X = (
    M6_DETECTOR_SHELL_MAX_X
    + M6_DETECTOR_SHELL_SUPPORT_GUSSET_X_OVERLAP
)
M6_DETECTOR_SHELL_SUPPORT_GUSSET_ROOT_Y_START_POSITIVE = (
    M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_Y
    - M6_DETECTOR_SHELL_SUPPORT_GUSSET_ROOT_WIDTH_Y
)
M6_DETECTOR_SHELL_SUPPORT_GUSSET_WALL_Y_START_POSITIVE = (
    M6_DETECTOR_SHELL_MAX_Y
    - M6_DETECTOR_SHELL_SUPPORT_GUSSET_WALL_WIDTH_Y
)
M6_DETECTOR_SHELL_SUPPORT_GUSSET_BOTTOM_Z = (
    M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_Z
    - M6_DETECTOR_SHELL_SUPPORT_GUSSET_HEIGHT_Z / 2
)
M6_DETECTOR_SHELL_SUPPORT_GUSSET_TOP_Z = (
    M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_Z
    + M6_DETECTOR_SHELL_SUPPORT_GUSSET_HEIGHT_Z / 2
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
# The raw detector dimensions remain in the same coordinate chain as the
# SCAD. In the installed stand the complete detector and purchased ballhead
# move together until the ballhead's z- interface is coaxial with the straight
# net-post centre. This removes the old horizontal support arm while
# preserving the net-post and net-span datums.
DETECTOR_ASSEMBLY_OFFSET_X = POST_CENTER - M6_DETECTOR_BALLHEAD_CENTER_X
# The M6 optical group is directly supported by the one-piece fixed-net post.
# The central M8 pilot is cut in the post top; no separate bridge is drawn.
M6_DETECTOR_DIRECT_MOUNT_ARM_WIDTH_Y = 0.0
M6_DETECTOR_DIRECT_MOUNT_ARM_T_Z = 0.0
M6_DETECTOR_DIRECT_MOUNT_ENABLED = True
M6_DETECTOR_DIRECT_MOUNT_WEB_WIDTH_Y = 0.0
M6_DETECTOR_DIRECT_MOUNT_WEB_T_X = 0.0
M6_DETECTOR_DIRECT_MOUNT_POST_OVERLAP_X = 2.0
# Retained as a compatibility envelope for older reports; no round boss is drawn.
M6_DETECTOR_DIRECT_MOUNT_SOCKET_OUTER_D = 24.0
M6_DETECTOR_DIRECT_MOUNT_SOCKET_CLEARANCE_D = 8.6
M6_DETECTOR_DIRECT_MOUNT_SOCKET_TAP_D = 6.8
# The tap-pilot dimensions are mirrored for the active flat-top interface.
M6_DETECTOR_DIRECT_MOUNT_THREAD_DEPTH_EXTRA_Z = 2.0
M6_DETECTOR_DIRECT_MOUNT_SOCKET_BASE_OVERLAP_Z = 0.0
M6_DETECTOR_DIRECT_MOUNT_NUT_LOADING_CLEARANCE_Z = 0.0
M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_CLEARANCE_Z = 0.0
M6_DETECTOR_DIRECT_MOUNT_SOCKET_TOP_CLEARANCE_Z = 0.0
M6_DETECTOR_DIRECT_MOUNT_ARM_MIN_X = POST_CENTER
M6_DETECTOR_DIRECT_MOUNT_ARM_MAX_X = POST_CENTER
M6_DETECTOR_DIRECT_MOUNT_ARM_BOTTOM_Z = (
    M6_DETECTOR_BALLHEAD_CENTER_Z
    - M6_BALLHEAD_HOUSING_LENGTH_X / 2
    - M6_BALLHEAD_BASE_T
)
M6_DETECTOR_DIRECT_MOUNT_ARM_TOP_Z = M6_DETECTOR_DIRECT_MOUNT_ARM_BOTTOM_Z
M6_DETECTOR_DIRECT_MOUNT_LOWER_POST_TOP_Z = M6_DETECTOR_DIRECT_MOUNT_ARM_BOTTOM_Z
M6_DETECTOR_DIRECT_MOUNT_WEB_MIN_X = POST_CENTER - POST_WIDTH / 2
M6_DETECTOR_DIRECT_MOUNT_WEB_MAX_X = M6_DETECTOR_DIRECT_MOUNT_WEB_MIN_X
M6_DETECTOR_DIRECT_MOUNT_WEB_MIN_Z = M6_DETECTOR_DIRECT_MOUNT_LOWER_POST_TOP_Z
M6_DETECTOR_DIRECT_MOUNT_WEB_MAX_Z = M6_DETECTOR_DIRECT_MOUNT_LOWER_POST_TOP_Z
M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_Z = (
    M6_DETECTOR_DIRECT_MOUNT_ARM_BOTTOM_Z
    - M6_BALLHEAD_NET_STUD_LENGTH
    - M6_DETECTOR_DIRECT_MOUNT_THREAD_DEPTH_EXTRA_Z
)
M6_DETECTOR_DIRECT_MOUNT_SOCKET_TOP_Z = (
    M6_DETECTOR_DIRECT_MOUNT_ARM_BOTTOM_Z
)
M6_DETECTOR_DIRECT_MOUNT_SOCKET_HEIGHT_Z = (
    M6_DETECTOR_DIRECT_MOUNT_SOCKET_TOP_Z
    - M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_Z
)
M6_DETECTOR_DIRECT_MOUNT_SOCKET_CENTER_X = POST_CENTER
# Compatibility aliases now point at the blind-hole bottom and explicitly carry
# no nut-loading volume.
M6_DETECTOR_DIRECT_MOUNT_NUT_POCKET_BOTTOM_Z = M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_Z
M6_DETECTOR_DIRECT_MOUNT_NUT_POCKET_CENTER_Z = M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_Z
M6_DETECTOR_DIRECT_MOUNT_NUT_LOADING_DEPTH_Z = 0.0

# Installed detector/ballhead coordinates are the raw detector coordinates plus
# one rigid z translation. The standalone part dimensions and the 20 mm pitch
# remain unchanged; only the assembled placement clears the net top.
for _installed_z_name in (
    "M6_DETECTOR_BODY_BOTTOM_Z",
    "M6_DETECTOR_SHELL_BOTTOM_Z",
    "M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_Z",
    "M6_DETECTOR_SHELL_SUPPORT_BOSS_BOTTOM_Z",
    "M6_DETECTOR_SHELL_SUPPORT_BOSS_TOP_Z",
    "M6_DETECTOR_SHELL_SUPPORT_GUSSET_BOTTOM_Z",
    "M6_DETECTOR_SHELL_SUPPORT_GUSSET_TOP_Z",
    "M6_DETECTOR_BALLHEAD_CENTER_Z",
    "M6_DETECTOR_BALLHEAD_NET_INTERFACE_BOTTOM_Z",
    "M6_DETECTOR_DIRECT_MOUNT_ARM_BOTTOM_Z",
    "M6_DETECTOR_DIRECT_MOUNT_ARM_TOP_Z",
    "M6_DETECTOR_DIRECT_MOUNT_LOWER_POST_TOP_Z",
    "M6_DETECTOR_DIRECT_MOUNT_WEB_MIN_Z",
    "M6_DETECTOR_DIRECT_MOUNT_WEB_MAX_Z",
    "M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_Z",
    "M6_DETECTOR_DIRECT_MOUNT_SOCKET_TOP_Z",
    "M6_DETECTOR_DIRECT_MOUNT_NUT_POCKET_BOTTOM_Z",
    "M6_DETECTOR_DIRECT_MOUNT_NUT_POCKET_CENTER_Z",
):
    globals()[_installed_z_name] += M6_DETECTOR_MOUNT_RAISE_Z
del _installed_z_name
# The fixed-net post top is the full active upright datum, while the net
# passage/clip datum remains NET_POST_TOP_Z.
M6_DETECTOR_DIRECT_MOUNT_LOWER_POST_TOP_Z = POST_TOP
M6_DETECTOR_DIRECT_MOUNT_WEB_MIN_Z = POST_TOP
M6_DETECTOR_DIRECT_MOUNT_WEB_MAX_Z = POST_TOP
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
# SCAD inputs; the raw body/shell/support coordinates below are derived from
# the table edge and the +10...+190 mm channel schedule, then the installed
# rigid group is raised by M6_DETECTOR_MOUNT_RAISE_Z.
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

# Apply the installed rigid-group translation to the absolute detector
# coordinates. Dimension fields stay unchanged; only the x datum moves.
M6_SENSOR_AXIS_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_SENSOR_MOUNT_HOLE_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_BODY_MIN_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_MIN_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_MAX_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_SPLIT_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_FRONT_MAX_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_REAR_MIN_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_SUPPORT_BOSS_MIN_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_SUPPORT_BOSS_MAX_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_SUPPORT_BOSS_CENTER_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_SUPPORT_HOLE_ENTRY_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_SUPPORT_GUSSET_MIN_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_SHELL_SUPPORT_GUSSET_MAX_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_BALLHEAD_CENTER_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_SENSOR_INSTALLED_HEAD_MIN_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_SENSOR_INSTALLED_THREAD_TIP_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_SENSOR_INSTALLED_CABLE_EXIT_X += DETECTOR_ASSEMBLY_OFFSET_X
M6_DETECTOR_NUT_MIN_X += DETECTOR_ASSEMBLY_OFFSET_X
# The active same-material PETG stand is one continuous printable upright.  The
# net cut creates the real y-side cheeks below the net top; it is not a second
# post parting line and it must not be rendered as one.
# The active lower taper is measured from the C-clamp contact plane.  The
# broad lower footprint matches the clamp's 58 mm y-depth; the upper section
# keeps the exact 28 x 38 mm top cross-section.
POST_INTERFACE_TRANSITION_HEIGHT_Z = 30.0
POST_INTERFACE_TRANSITION_EXTRA_X = 3.5
# Compatibility alias retained for older reports; the active lower y-depth is
# the complete C-clamp contact depth below, not this legacy inset value.
POST_INTERFACE_TRANSITION_EXTRA_Y = 10.0
POST_INTERFACE_TRANSITION_BOTTOM_WIDTH_X = (
    POST_WIDTH + 2 * POST_INTERFACE_TRANSITION_EXTRA_X
)
POST_INTERFACE_TRANSITION_BOTTOM_DEPTH_Y = CLAMP_PAD_DEPTH
POST_INTERFACE_TRANSITION_START_Z = CLAMP_SLIDE_SEAT_Z
POST_INTERFACE_TRANSITION_TOP_Z = (
    POST_INTERFACE_TRANSITION_START_Z + POST_INTERFACE_TRANSITION_HEIGHT_Z
)
POST_INTERFACE_TRANSITION_OUTER_MIN_X = (
    POST_OFFSET - POST_INTERFACE_TRANSITION_BOTTOM_WIDTH_X / 2
)
POST_INTERFACE_TRANSITION_OUTER_MAX_X = (
    POST_OFFSET + POST_INTERFACE_TRANSITION_BOTTOM_WIDTH_X / 2
)
POST_INTERFACE_TRANSITION_OUTER_MIN_Y = (
    -POST_INTERFACE_TRANSITION_BOTTOM_DEPTH_Y / 2
)
POST_INTERFACE_TRANSITION_OUTER_MAX_Y = (
    POST_INTERFACE_TRANSITION_BOTTOM_DEPTH_Y / 2
)
# Kept as a direct source-mirroring datum for older reports. It is no longer a
# parting height; the active print has no post seam.
POST_JOINT_ABOVE_NET_CLEARANCE_Z = 18.0
POST_SPLIT_Z = POST_TOP
POST_JOINT_GAP = 0.0
PREVIEW_FIT_DISPLAY_GAP = 0.1
POST_LOWER_SEGMENT_HEIGHT = POST_TOP - POST_BOTTOM
POST_UPPER_SEGMENT_Z = POST_TOP
POST_UPPER_SEGMENT_HEIGHT = 0.0
PREVIEW_TOP = max(
    POST_TOP,
    M6_DETECTOR_SHELL_BOTTOM_Z + M6_DETECTOR_SHELL_HEIGHT_Z,
    M6_DETECTOR_DIRECT_MOUNT_SOCKET_TOP_Z,
)
NET_SPAN = 2 * (POST_CENTER + POST_WIDTH / 2)
REFERENCE_HEIGHT = 50.0
SENSOR_X = 0.32 * NET_SPAN / 2


def eased_taper_profile(
    lower_min: float,
    lower_max: float,
    upper_min: float,
    upper_max: float,
    bottom_z: float,
    top_z: float,
    section_count: int = CLAMP_SLIDE_POST_FOOT_TRANSITION_SECTION_COUNT,
    transition_start_z: float | None = None,
) -> list[tuple[float, float]]:
    """Return a faceted large-radius taper with no shoulder/step.

    The smoothstep easing makes the boundary nearly tangent to the flat
    lower shoe and the vertical upper post.  It is intentionally sampled at
    the same section count as the OpenSCAD loft so the diagnostic drawing shows
    the real transition rather than a single straight wedge.
    """

    def ease(t: float) -> float:
        return t * t * (3.0 - 2.0 * t)

    def lerp(start: float, end: float, t: float) -> float:
        return start + (end - start) * t

    if transition_start_z is None:
        transition_start_z = bottom_z

    def profile_ease(z: float) -> float:
        span = top_z - transition_start_z
        if span <= 0:
            return 1.0
        profile_t = max(0.0, min(1.0, (z - transition_start_z) / span))
        return ease(profile_t)

    points = [(lower_min, bottom_z), (lower_max, bottom_z)]
    points.extend(
        (
            lerp(
                lower_max,
                upper_max,
                profile_ease(
                    lerp(bottom_z, top_z, index / section_count)
                ),
            ),
            lerp(bottom_z, top_z, index / section_count),
        )
        for index in range(1, section_count + 1)
    )
    points.append((upper_min, top_z))
    points.extend(
        (
            lerp(
                lower_min,
                upper_min,
                profile_ease(
                    lerp(bottom_z, top_z, index / section_count)
                ),
            ),
            lerp(bottom_z, top_z, index / section_count),
        )
        for index in range(section_count - 1, 0, -1)
    )
    return points


def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _foot_rail_width_y(z: float) -> float:
    """Mirror the source rail's broad shoe-to-neck section."""

    blend_start = CLAMP_SLIDE_RAIL_FLOOR_Z + CLAMP_SLIDE_RAIL_HEAD_HEIGHT_Z
    blend = (z - blend_start) / CLAMP_SLIDE_RAIL_NECK_HEIGHT_Z
    return CLAMP_SLIDE_RAIL_HEAD_WIDTH_Y + (
        CLAMP_SLIDE_RAIL_NECK_WIDTH_Y - CLAMP_SLIDE_RAIL_HEAD_WIDTH_Y
    ) * _smoothstep(blend)


def _foot_outer_y(z: float) -> float:
    rail_roof = CLAMP_SLIDE_RAIL_FLOOR_Z + CLAMP_SLIDE_RAIL_HEIGHT_Z
    if z <= CLAMP_SLIDE_RAIL_FLOOR_Z + CLAMP_SLIDE_RAIL_HEAD_HEIGHT_Z:
        return CLAMP_SLIDE_RAIL_Y_OUTER + CLAMP_SLIDE_RAIL_HEAD_WIDTH_Y / 2
    if z <= rail_roof:
        return CLAMP_SLIDE_RAIL_Y_OUTER + _foot_rail_width_y(z) / 2
    post_blend = (z - CLAMP_SLIDE_POST_FOOT_TRANSITION_SIDE_START_Z) / (
        CLAMP_SLIDE_POST_FOOT_TRANSITION_END_Z
        - CLAMP_SLIDE_POST_FOOT_TRANSITION_SIDE_START_Z
    )
    return (
        CLAMP_SLIDE_RAIL_Y_OUTER + CLAMP_SLIDE_RAIL_NECK_WIDTH_Y / 2
    ) + (
        POST_DEPTH / 2 - CLAMP_SLIDE_POST_FOOT_POST_FUSION_INSET
        - (CLAMP_SLIDE_RAIL_Y_OUTER + CLAMP_SLIDE_RAIL_NECK_WIDTH_Y / 2)
    ) * _smoothstep(post_blend)


def _foot_inner_y(z: float) -> float:
    rail_roof = CLAMP_SLIDE_RAIL_FLOOR_Z + CLAMP_SLIDE_RAIL_HEIGHT_Z
    if z <= CLAMP_SLIDE_RAIL_FLOOR_Z + CLAMP_SLIDE_RAIL_HEAD_HEIGHT_Z:
        return CLAMP_SLIDE_RAIL_Y_OUTER - CLAMP_SLIDE_RAIL_HEAD_WIDTH_Y / 2
    if z <= rail_roof:
        return CLAMP_SLIDE_RAIL_Y_OUTER - _foot_rail_width_y(z) / 2
    post_blend = (z - CLAMP_SLIDE_POST_FOOT_TRANSITION_SIDE_START_Z) / (
        CLAMP_SLIDE_POST_FOOT_TRANSITION_END_Z
        - CLAMP_SLIDE_POST_FOOT_TRANSITION_SIDE_START_Z
    )
    return (
        CLAMP_SLIDE_RAIL_Y_OUTER - CLAMP_SLIDE_RAIL_NECK_WIDTH_Y / 2
    ) + (
        NET_PASSAGE_WIDTH_Y / 2 - CLAMP_SLIDE_POST_FOOT_POST_FUSION_INSET
        - (CLAMP_SLIDE_RAIL_Y_OUTER - CLAMP_SLIDE_RAIL_NECK_WIDTH_Y / 2)
    ) * _smoothstep(post_blend)


def pants_leg_profile(side: int) -> list[tuple[float, float]]:
    """Return one real y-z leg, including the broad shoe and smooth ankle."""

    z_values = [
        CLAMP_SLIDE_POST_FOOT_BOTTOM_Z
        + (CLAMP_SLIDE_POST_FOOT_TOP_Z - CLAMP_SLIDE_POST_FOOT_BOTTOM_Z)
        * index
        / CLAMP_SLIDE_POST_FOOT_TRANSITION_SECTION_COUNT
        for index in range(CLAMP_SLIDE_POST_FOOT_TRANSITION_SECTION_COUNT + 1)
    ]
    if side > 0:
        outer = [(_foot_outer_y(z), z) for z in z_values]
        inner = [(_foot_inner_y(z), z) for z in reversed(z_values)]
    else:
        outer = [(-_foot_outer_y(z), z) for z in z_values]
        inner = [(-_foot_inner_y(z), z) for z in reversed(z_values)]
    return outer + inner


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
            (-NET_SPAN / 2, NET_FIXTURE_BOTTOM_Z),
            NET_SPAN,
            NET_HEIGHT,
            facecolor="#dfe3e8",
            edgecolor="#777d85",
            alpha=0.35,
            label="installed net z=16…168.5 mm",
        )
    )

    for x, side_label in (
        (-POST_CENTER, "left"),
        (POST_CENTER, "right"),
    ):
        ax.add_patch(
            Polygon(
                [
                    (x - POST_INTERFACE_TRANSITION_BOTTOM_WIDTH_X / 2,
                     POST_BOTTOM),
                    (x + POST_INTERFACE_TRANSITION_BOTTOM_WIDTH_X / 2,
                     POST_BOTTOM),
                    (x + POST_INTERFACE_TRANSITION_BOTTOM_WIDTH_X / 2,
                     POST_INTERFACE_TRANSITION_START_Z),
                    (x + POST_WIDTH / 2, POST_INTERFACE_TRANSITION_TOP_Z),
                    (x + POST_WIDTH / 2, POST_TOP),
                    (x - POST_WIDTH / 2, POST_TOP),
                    (x - POST_WIDTH / 2, POST_INTERFACE_TRANSITION_TOP_Z),
                    (x - POST_INTERFACE_TRANSITION_BOTTOM_WIDTH_X / 2,
                     POST_INTERFACE_TRANSITION_START_Z),
                ],
                closed=True,
                facecolor="#d4a24c",
                edgecolor="#8d6513",
                alpha=0.88,
                label=(
                    f"{side_label} 固定网柱：z=16→{POST_TOP:g} mm 一体实心"
                ),
            )
        )
        base_min_x = SKP_BASE_MIN_X if x > 0 else -SKP_BASE_MAX_X
        base_max_x = SKP_BASE_MAX_X if x > 0 else -SKP_BASE_MIN_X
        ax.add_patch(
            Polygon(
                [
                    (base_min_x + 3, SKP_BASE_BOTTOM_Z),
                    (base_max_x, SKP_BASE_BOTTOM_Z),
                    (base_max_x, SKP_BASE_BASE_TOP_Z if False else SKP_BASE_TOP_Z),
                    (base_min_x + 3, SKP_BASE_TOP_Z),
                    (base_min_x, SKP_BASE_TOP_Z - 3),
                    (base_min_x, SKP_BASE_BOTTOM_Z),
                ],
                closed=True,
                facecolor="#43d34d",
                edgecolor="#267d2f",
                linewidth=1.0,
                alpha=0.9,
                label=f"{side_label} 绿色 SKP 整体底座（x 向推进）",
            )
        )

    ax.plot(
        [POST_CENTER - 32, POST_CENTER + 32],
        [POST_BOTTOM, POST_BOTTOM],
        color="#2e596d",
        linewidth=2.2,
        label="灰色 C 夹让位腔 / 绿色底座顶面 z=16 mm",
    )
    ax.annotate(
        "绿色整体底座从 x+ 推入灰色 C 夹让位腔\n两枚 Ø4 穿孔配 Ø4.4 夹体孔；中央 Ø6×2 mm 底坑由 4 mm 钢球定位\n黄色立柱坐在绿色底座上，从 z=16 mm 一体延伸到 z=260.5 mm",
        xy=(POST_CENTER, POST_BOTTOM),
        xytext=(POST_CENTER - 210, POST_BOTTOM + 30),
        fontsize=7,
        color="#2e596d",
        arrowprops={"arrowstyle": "->", "color": "#2e596d", "lw": 0.9},
    )

    for side in (-1, 1):
        clip_x = (
            NET_CLAMP_CLIP_INNER_X
            if side > 0
            else -NET_CLAMP_CLIP_OUTER_X
        )
        crossbar_x = (
            NET_CLAMP_CLIP_OUTER_X - NET_CLAMP_CLIP_CROSSBAR_T_X
            if side > 0
            else -NET_CLAMP_CLIP_OUTER_X
        )
        ax.add_patch(
            Rectangle(
                (clip_x, NET_CLAMP_CHANNEL_BOTTOM_Z),
                NET_CLAMP_CLIP_LENGTH_X,
                NET_CLAMP_CYLINDER_HEIGHT,
                facecolor="#e2a52f",
                edgecolor="#815b0f",
                alpha=0.88,
                label="PETG 整高 U 形卡网夹（张力承力；一体扣舌配内嵌止挡防拔）" if side < 0 else "_nolegend_",
            )
        )
        ax.add_patch(
            Rectangle(
                (crossbar_x, NET_CLAMP_CHANNEL_BOTTOM_Z),
                NET_CLAMP_CLIP_CROSSBAR_T_X,
                NET_CLAMP_CYLINDER_HEIGHT,
                facecolor="#b87916",
                edgecolor="#815b0f",
                alpha=0.92,
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
                label="x+ 后盖接驳边直角、后端圆角；背面中央为采购球头加厚 boss" if side < 0 else "_nolegend_",
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
                label="后盖背面中央加厚 1/4-20 boss（采购球头）" if side < 0 else "_nolegend_",
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
            z = (
                NET_HEIGHT
                + M6_SENSOR_FIRST_HEIGHT
                + index * M6_SENSOR_CENTER_PITCH
                + M6_DETECTOR_MOUNT_RAISE_Z
            )
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
                (x - 23, NET_POST_TOP_Z - 1),
                46,
                8,
                facecolor="#9467bd",
                edgecolor="#4c2b68",
                label="PVDF 网端传感器座（网顶 z=168.5）" if x < 0 else "_nolegend_",
            )
        )

    reference_z = NET_POST_TOP_Z + REFERENCE_HEIGHT
    ax.plot(
        [-NET_SPAN / 2, NET_SPAN / 2],
        [reference_z, reference_z],
        color="#31a354",
        linewidth=2.4,
        label="reference line (+50 mm mechanical reference)",
    )
    ax.annotate(
        "net-top datum +0",
        xy=(0, NET_POST_TOP_Z),
        xytext=(0, NET_POST_TOP_Z - 30),
        ha="center",
        arrowprops={"arrowstyle": "->", "color": "#444"},
        fontsize=8,
    )
    ax.set_xlim(-POST_CENTER - 90, POST_CENTER + 110)
    ax.set_ylim(
        min(POST_BOTTOM, CLAMP_REINFORCEMENT_NEAR_TABLE_BOTTOM_Z) - 12,
        PREVIEW_TOP + 20,
    )
    ax.set_title("Integrated net stand: front intent (M6 assembly +20 mm; sliding U net clips)")
    ax.set_xlabel("table width / mm")
    ax.set_ylabel("z relative to table top / mm")
    ax.grid(True, alpha=0.22)
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper center", fontsize=7, ncol=2)


def captured_slide_profile(
    center_y: float,
    floor_z: float,
    head_width_y: float,
    neck_width_y: float,
    head_height_z: float,
    neck_height_z: float,
):
    """Return a legacy y-z polygon for compatibility-only diagnostics."""

    top_z = floor_z + head_height_z + neck_height_z
    return [
        (center_y - head_width_y / 2, floor_z),
        (center_y + head_width_y / 2, floor_z),
        (center_y + head_width_y / 2, floor_z + head_height_z),
        (center_y + neck_width_y / 2, top_z),
        (center_y - neck_width_y / 2, top_z),
        (center_y - head_width_y / 2, floor_z + head_height_z),
    ]


def draw_side(ax) -> None:
    # 以右侧台边为 x=0，正方向是桌外；画出免打孔 C 形夹体。
    post_x0 = POST_OFFSET - POST_WIDTH / 2
    ax.add_patch(
        Rectangle(
            (-CLAMP_TONGUE_REACH_INBOARD, -TABLE_THICKNESS),
            CLAMP_TONGUE_REACH_INBOARD,
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
            label="后盖 x+ 背面中央加厚 1/4-20 捕获螺母 boss",
        )
    )
    for index in range(BEAM_COUNT):
        z = (
            NET_HEIGHT
            + M6_SENSOR_FIRST_HEIGHT
            + index * M6_SENSOR_CENTER_PITCH
            + M6_DETECTOR_MOUNT_RAISE_Z
        )
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
    ballhead_body_left = ballhead_x - M6_BALLHEAD_HOUSING_D / 2
    ballhead_body_bottom = ballhead_z - M6_BALLHEAD_HOUSING_LENGTH_X / 2
    ballhead_base_bottom = (
        ballhead_body_bottom - M6_BALLHEAD_BASE_T
    )
    ballhead_interface_bottom = (
        ballhead_base_bottom - M6_BALLHEAD_NET_STUD_LENGTH
    )
    ax.add_patch(
        Rectangle(
            (ballhead_body_left, ballhead_body_bottom),
            M6_BALLHEAD_HOUSING_D,
            M6_BALLHEAD_HOUSING_LENGTH_X,
            facecolor="#1d2227",
            edgecolor="#080a0c",
            alpha=0.95,
            label="采购 13 mm 球头黑色夹持壳（不打印）",
        )
    )
    ax.add_patch(
        Circle(
            (ballhead_x, ballhead_z),
            M6_BALLHEAD_BALL_D / 2,
            facecolor="#b9c0c6",
            edgecolor="#4e5961",
            alpha=0.9,
            label="13 mm 不锈钢球（采购件）",
        )
    )
    ax.add_patch(
        Rectangle(
            (ballhead_body_left - M6_BALLHEAD_SIDE_PLATE_T_X / 2,
             ballhead_z - M6_BALLHEAD_SIDE_PLATE_D / 2),
            M6_BALLHEAD_SIDE_PLATE_T_X,
            M6_BALLHEAD_SIDE_PLATE_D,
            facecolor="#161a1e",
            edgecolor="#050607",
            alpha=0.98,
            label="可拆圆盘 / 1/4-20 上端接口",
        )
    )
    ax.add_patch(
        Circle(
            (ballhead_x, ballhead_z),
            M6_BALLHEAD_LOCK_KNOB_D / 2,
            facecolor="#0e1114",
            edgecolor="#050607",
            linewidth=1.0,
            alpha=0.32,
            label="侧向锁紧旋钮（采购件）",
        )
    )
    ax.add_patch(
        Rectangle(
            (ballhead_x - M6_BALLHEAD_BASE_D / 2,
             ballhead_base_bottom),
            M6_BALLHEAD_BASE_D,
            M6_BALLHEAD_BASE_T,
            facecolor="#171b1f",
            edgecolor="#050607",
            alpha=0.98,
            label="球头底座 Ø32 mm（采购件）",
        )
    )
    ax.plot(
        [ballhead_x, ballhead_x],
        [ballhead_interface_bottom, ballhead_base_bottom],
        color="#c7cdd2",
        linewidth=3.0,
        label="采购球头下端 M8 外牙（独立光学支撑接口）",
    )
    ax.plot(
        [boss_max_x - TABLE_EDGE,
         ballhead_body_left - M6_BALLHEAD_SIDE_PLATE_T_X / 2],
        [body_bottom + body_height / 2, ballhead_z],
        color="#c7cdd2",
        linewidth=3.0,
        label="1/4-20 外牙 x− → 后盖捕获 1/4 螺母",
    )
    for tick_x in range(
        int(ballhead_body_left - M6_BALLHEAD_SIDE_PLATE_T_X / 2),
        int(boss_max_x - TABLE_EDGE),
        2,
    ):
        ax.plot(
            [tick_x, tick_x + 0.7],
            [ballhead_z - 1.2, ballhead_z + 1.2],
            color="#f0f2f3",
            linewidth=0.7,
            alpha=0.7,
        )
    # The higher M6 optical support is intentionally not drawn as a solid
    # connection to the fixed full-height post.  A dashed marker keeps the
    # unresolved interface visible while making the physical gap unambiguous.
    post_top_x = POST_CENTER - TABLE_EDGE
    optical_support_x = M6_DETECTOR_DIRECT_MOUNT_SOCKET_CENTER_X - TABLE_EDGE
    ax.plot(
        [post_top_x, optical_support_x],
        [POST_TOP, M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_Z],
        color="#b04a3a",
        linewidth=1.2,
        linestyle=(0, (4, 3)),
        label="M6 独立支撑待定义（与固定网柱断开）",
    )
    ax.scatter(
        [post_top_x, optical_support_x],
        [POST_TOP, M6_DETECTOR_DIRECT_MOUNT_SOCKET_BOTTOM_Z],
        color="#b04a3a",
        s=12,
        zorder=6,
    )
    ax.add_patch(
        Polygon(
            [
                (
                    CLAMP_SOLID_BRIDGE_START_X,
                    CLAMP_REINFORCEMENT_NEAR_TABLE_BOTTOM_Z,
                ),
                (
                    CLAMP_REINFORCEMENT_END_X,
                    CLAMP_REINFORCEMENT_OUTER_BOTTOM_Z,
                ),
                (
                    CLAMP_REINFORCEMENT_END_X,
                    CLAMP_SOLID_BRIDGE_TOP_Z,
                ),
                (
                    CLAMP_SOLID_BRIDGE_START_X,
                    CLAMP_SOLID_BRIDGE_TOP_Z,
                ),
            ],
            closed=True,
            facecolor="#5d6872",
            edgecolor="#2e353c",
            alpha=0.72,
            label="桌边外侧非接触区：y 全深实心桥体",
        )
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_PAD_X, CLAMP_TOP_PAD_T),
            CLAMP_PAD_OUTER_X - CLAMP_PAD_X,
            CLAMP_PAD_T,
            facecolor="#69727b",
            label="加长上舌头 82 mm / 14 mm 厚（不打孔）",
        )
    )
    ax.add_patch(
        Polygon(
            [
                (
                    CLAMP_REINFORCEMENT_START_X,
                    CLAMP_REINFORCEMENT_NEAR_TABLE_BOTTOM_Z,
                ),
                (
                    CLAMP_REINFORCEMENT_END_X,
                    CLAMP_REINFORCEMENT_OUTER_BOTTOM_Z,
                ),
                (
                    CLAMP_REINFORCEMENT_END_X,
                    CLAMP_REINFORCEMENT_TOP_Z,
                ),
                (
                    CLAMP_REINFORCEMENT_START_X,
                    CLAMP_REINFORCEMENT_TOP_Z,
                ),
            ],
            closed=True,
            facecolor="#4f5963",
            edgecolor="#2e353c",
            alpha=0.92,
            label="全宽实心下部支撑：靠台侧厚 40 mm，外侧 12 mm 斜底",
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
    # Current 779f046 C-scheme interface in the side elevation: the gray
    # clamp has a shallow receiving pocket and the green SKP ROOT base enters
    # horizontally from x+. The yellow upright begins on the green top at z=16.
    ax.add_patch(
        Rectangle(
            (SKP_BASE_MIN_X - 3, SKP_BASE_BOTTOM_Z),
            (SKP_BASE_MAX_X - SKP_BASE_MIN_X) + 6,
            SKP_BASE_TOP_Z - SKP_BASE_BOTTOM_Z,
            facecolor="#687985",
            edgecolor="#3f4d57",
            linewidth=1.0,
            alpha=0.28,
            label="灰色 C 夹让位腔（配套 Ø4.4 孔 / 中央定位孔）",
        )
    )
    post_skp_side_polygon = [
        (SKP_BASE_MIN_X + 3, SKP_BASE_BOTTOM_Z),
        (SKP_BASE_MAX_X, SKP_BASE_BOTTOM_Z),
        (SKP_BASE_MAX_X, SKP_BASE_TOP_Z),
        (SKP_BASE_MIN_X + 3, SKP_BASE_TOP_Z),
        (SKP_BASE_MIN_X, SKP_BASE_TOP_Z - 3),
        (SKP_BASE_MIN_X, SKP_BASE_BOTTOM_Z),
    ]
    ax.add_patch(
        Polygon(
            post_skp_side_polygon,
            closed=True,
            facecolor="#43d34d",
            edgecolor="#267d2f",
            linewidth=1.0,
            alpha=0.92,
            label="绿色 SKP 整体底座：x+ 推入 / 两枚 Ø4 / Ø6×2 底坑",
        )
    )
    ax.scatter(
        [SKP_BASE_DETENT_X], [SKP_BASE_BOTTOM_Z],
        color="#d8dde2", edgecolor="#4d5964", s=18, zorder=7,
        label="4 mm 钢球定位（只定位，不承主载）",
    )
    # The yellow fixed-net post starts on the green base top, tapers
    # continuously for 30 mm, and then remains 28 x 38 mm for the rest.
    post_side_polygon = [
        (POST_INTERFACE_TRANSITION_OUTER_MIN_X, POST_BOTTOM),
        (POST_INTERFACE_TRANSITION_OUTER_MAX_X, POST_BOTTOM),
        (POST_INTERFACE_TRANSITION_OUTER_MAX_X,
         POST_INTERFACE_TRANSITION_START_Z),
        (POST_OFFSET + POST_WIDTH / 2, POST_INTERFACE_TRANSITION_TOP_Z),
        (POST_OFFSET + POST_WIDTH / 2, POST_TOP),
        (POST_OFFSET - POST_WIDTH / 2, POST_TOP),
        (POST_OFFSET - POST_WIDTH / 2, POST_INTERFACE_TRANSITION_TOP_Z),
        (POST_INTERFACE_TRANSITION_OUTER_MIN_X,
         POST_INTERFACE_TRANSITION_START_Z),
    ]
    ax.add_patch(
        Polygon(
            post_side_polygon,
            closed=True,
            facecolor="#d98d27",
            edgecolor="#7d530b",
            linewidth=1.0,
            alpha=0.82,
            label="整根固定网柱：z=16→260.5 一体实心渐变/恒定段",
        )
    )
    ax.plot(
        [POST_INTERFACE_TRANSITION_OUTER_MIN_X - 6,
         POST_INTERFACE_TRANSITION_OUTER_MAX_X + 6],
        [POST_BOTTOM, POST_BOTTOM],
        color="#2e596d",
        linewidth=2.2,
        label="绿色底座顶面 z=16 mm；黄色立柱落座",
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_LOWER_ARM_X, CLAMP_LOWER_ARM_BOTTOM),
            CLAMP_PAD_OUTER_X - CLAMP_LOWER_ARM_X,
            CLAMP_PAD_T,
            facecolor="#69727b",
            label="加长下舌头 82 mm / 14 mm 厚 / 压紧居中",
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
    ax.annotate(
        "绿色底座从 x+ 推入灰色让位腔；终点由 4 mm 钢球定位\n两枚 Ø4 绿件通孔与灰色 Ø4.4 孔对齐后锁紧\n黄色立柱从绿色顶面 z=16 mm 起，继续到 z=260.5 mm",
        xy=(POST_OFFSET, POST_INTERFACE_TRANSITION_TOP_Z),
        xytext=(72, 45),
        fontsize=7,
        color="#7d530b",
        arrowprops={"arrowstyle": "->", "color": "#7d530b", "lw": 0.9},
    )
    ax.plot(
        [post_x0, CLAMP_SLIDE_POST_SEAT_END_X],
        [CLAMP_SLIDE_SEAT_Z, CLAMP_SLIDE_SEAT_Z],
        color="#dfe7ec",
        linewidth=2.2,
        solid_capstyle="butt",
        label="灰色 C 夹让位腔上缘 / 绿色底座顶面 z=16 mm",
    )
    ax.annotate(
        "绿色整体底座沿 x+ 推入灰色 C 夹\n到位后两枚 M4 固定，中央钢球只负责咯噔定位",
        xy=(POST_OFFSET, CLAMP_SLIDE_SEAT_Z),
        xytext=(72, 30),
        fontsize=7,
        color="#2e596d",
        arrowprops={"arrowstyle": "->", "color": "#2e596d", "lw": 0.9},
    )
    ax.add_patch(
        Rectangle(
            (NET_CLAMP_CLIP_INNER_X - TABLE_EDGE, NET_CLAMP_CHANNEL_BOTTOM_Z),
            NET_CLAMP_CLIP_LENGTH_X,
            NET_CLAMP_CYLINDER_HEIGHT,
            facecolor="#e2a52f",
            edgecolor="#815b0f",
            alpha=0.9,
            label="PETG 整高 U 形卡网夹（外侧 x+ 滑入；张力承力）",
        )
    )
    ax.add_patch(
        Rectangle(
            (
                NET_CLAMP_CLIP_OUTER_X - TABLE_EDGE - NET_CLAMP_CLIP_CROSSBAR_T_X,
                NET_CLAMP_CHANNEL_BOTTOM_Z,
            ),
            NET_CLAMP_CLIP_CROSSBAR_T_X,
            NET_CLAMP_CYLINDER_HEIGHT,
            facecolor="#b87916",
            edgecolor="#815b0f",
            alpha=0.92,
        )
    )
    ax.add_patch(
        Rectangle(
            (NET_CLAMP_KEEPER_X_MIN - TABLE_EDGE, NET_CLAMP_KEEPER_Z),
            NET_CLAMP_KEEPER_X_MAX - NET_CLAMP_KEEPER_X_MIN,
            NET_CLAMP_KEEPER_HEIGHT_Z,
            facecolor="#8f4f18",
            edgecolor="#5e3210",
            linewidth=1.0,
            alpha=0.95,
            label="立柱内嵌单一被动止挡（配卡夹一体扣舌；只防拔出；无穿钉）",
        )
    )
    ax.annotate(
        "网布穿过立柱主体的 y 向过道：3 mm\n卡夹由网布/绳张力压住，一体扣舌配内嵌止挡只防拔出",
        xy=(post_x0 + POST_WIDTH / 2,
            NET_FIXTURE_BOTTOM_Z + NET_HEIGHT / 2),
        xytext=(post_x0 - 58, NET_FIXTURE_BOTTOM_Z + NET_HEIGHT / 2 + 18),
        fontsize=7,
        color="#7d5a0c",
        arrowprops={"arrowstyle": "->", "color": "#7d5a0c", "lw": 0.8},
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_SCREW_X - CLAMP_PRESSURE_PAD_WIDTH / 2, CLAMP_PRESSURE_PAD_BOTTOM),
            CLAMP_PRESSURE_PAD_WIDTH,
            CLAMP_PRESSURE_PAD_T,
            facecolor="#111111",
            label="台底 Ø50 压紧盘（下舌头中点）",
        )
    )
    ax.plot(
        [CLAMP_SCREW_X, CLAMP_SCREW_X],
        [CLAMP_SCREW_BOTTOM, CLAMP_PRESSURE_PAD_TOP],
        color="#444",
        linewidth=CLAMP_PRINTED_SCREW_D / 2,
        label="PETG 锥形粗牙螺杆（12 mm 大径 / 4 mm 螺距 / 2 mm 牙根 / 0.4 mm 锥尖）",
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_SCREW_X - CLAMP_KNOB_D / 2, CLAMP_KNOB_BOTTOM),
            CLAMP_KNOB_D,
            CLAMP_KNOB_H,
            facecolor="#30343b",
            label="圆角锯齿手拧旋钮（18 齿，外径 36 mm）",
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
            CLAMP_BODY_NUT_H,
            facecolor="#d4a72c",
            edgecolor="#6e5515",
            label="固定 PETG 粗牙螺母（AF16）",
        )
    )
    ax.axhline(NET_POST_TOP_Z, color="#ffffff", linewidth=2, label="网顶 z=168.5 mm（从 z=16 起 152.5 mm）")
    ax.axhline(NET_POST_TOP_Z + REFERENCE_HEIGHT, color="#31a354", linewidth=2, label="reference line +50 mm")
    for index in range(BEAM_COUNT):
        height = BEAM_FIRST + index * BEAM_PITCH
        ax.plot(
            [POST_OFFSET - 8, POST_OFFSET + POST_WIDTH + 4],
            [NET_POST_TOP_Z + height, NET_POST_TOP_Z + height],
            color="#4c78a8",
            linewidth=1.0,
        )
    ax.add_patch(
        Rectangle(
            (post_x0 - 20, NET_POST_TOP_Z - 1),
            12,
            8,
            facecolor="#9467bd",
            label="PVDF mount on net top",
        )
    )
    ax.set_xlim(-82, CLAMP_PAD_OUTER_X + 18)
    ax.set_ylim(CLAMP_KNOB_BOTTOM - 8, PREVIEW_TOP + 20)
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
    slide_inset = ax.inset_axes([0.52, 0.12, 0.44, 0.34])
    slide_inset.set_facecolor("#f7f9fb")
    # y-z section of the actual C-scheme interface. The gray pocket is
    # behind the green base; the 4 mm ball reaches the green underside pocket.
    slide_inset.add_patch(
        Rectangle(
            (-24, SKP_BASE_BOTTOM_Z),
            48,
            SKP_BASE_TOP_Z - SKP_BASE_BOTTOM_Z,
            facecolor="#aeb7bf",
            edgecolor="#4d5964",
            alpha=0.46,
            label="灰色 C 夹让位腔（截面）",
        )
    )
    slide_inset.add_patch(
        Polygon(
            [
                (-23, SKP_BASE_BOTTOM_Z), (23, SKP_BASE_BOTTOM_Z),
                (23, 3), (17, 7), (17, SKP_BASE_TOP_Z),
                (-17, SKP_BASE_TOP_Z), (-17, 7), (-23, 3),
            ],
            closed=True,
            facecolor="#43d34d",
            edgecolor="#267d2f",
            linewidth=1.1,
            alpha=0.92,
            label="绿色整体底座（57 mm 宽，底部 Ø6×2 mm）",
        )
    )
    slide_inset.add_patch(
        Circle((0, SKP_BASE_BOTTOM_Z), 2.0, facecolor="#d8dde2",
               edgecolor="#4d5964", zorder=7,
               label="4 mm 钢球 / 弹簧定位",
        )
    )
    slide_inset.add_patch(
        Polygon(
            [
                (POST_INTERFACE_TRANSITION_OUTER_MIN_Y, POST_BOTTOM),
                (POST_INTERFACE_TRANSITION_OUTER_MAX_Y, POST_BOTTOM),
                (POST_INTERFACE_TRANSITION_OUTER_MAX_Y,
                 POST_INTERFACE_TRANSITION_START_Z),
                (POST_DEPTH / 2, POST_INTERFACE_TRANSITION_TOP_Z),
                (-POST_DEPTH / 2, POST_INTERFACE_TRANSITION_TOP_Z),
                (POST_INTERFACE_TRANSITION_OUTER_MIN_Y,
                 POST_INTERFACE_TRANSITION_START_Z),
            ],
            closed=True,
            facecolor="#d98d27",
            edgecolor="#7d530b",
            linewidth=1.1,
            alpha=0.9,
            label="黄色立柱从绿色顶面 z=16 起渐变 30 mm",
        )
    )
    slide_inset.add_patch(
        Rectangle(
            (-POST_DEPTH / 2, POST_INTERFACE_TRANSITION_TOP_Z),
            POST_DEPTH,
            10,
            facecolor="#d4a24c",
            edgecolor="#8d6513",
            alpha=0.9,
            label="z=46 后立柱 28×38 mm 恒定至 z=260.5",
        )
    )
    slide_inset.plot(
        [POST_INTERFACE_TRANSITION_OUTER_MIN_Y - 3,
         POST_INTERFACE_TRANSITION_OUTER_MAX_Y + 3],
        [POST_BOTTOM, POST_BOTTOM],
        color="#2e596d",
        linewidth=2.0,
        label="绿色底座顶面 z=16 mm；黄色立柱落座",
    )
    slide_inset.annotate(
        "绿色底座进入灰色让位腔\nØ4 钢球落入 Ø6×2 mm 底坑",
        xy=(0, CLAMP_SLIDE_SEAT_Z),
        xytext=(12, CLAMP_SLIDE_SEAT_Z - 4),
        fontsize=7,
        color="#2e596d",
        arrowprops={"arrowstyle": "->", "color": "#2e596d", "lw": 0.8},
    )
    slide_inset.set_xlim(-34, 34)
    slide_inset.set_ylim(SKP_BASE_BOTTOM_Z - 3, POST_INTERFACE_TRANSITION_TOP_Z + 10)
    slide_inset.set_aspect("equal", adjustable="box")
    slide_inset.set_title("真实 y-z：C 方案绿色底座 + 灰色让位腔", fontsize=8)
    slide_inset.set_xlabel("y / mm（绿色底座 57 mm → 黄色上段 38 mm）", fontsize=7)
    slide_inset.set_ylabel("z", fontsize=7)
    slide_inset.tick_params(labelsize=6)
    slide_inset.grid(True, alpha=0.2)
    ax.set_title("No-drill C-clamp + SKP C-scheme push-in base + 30 mm solid taper: side intent")
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


def rear_back_rounded_points(
    x_min: float, x_max: float, y_min: float, y_max: float, radius: float
):
    """Return a plan footprint with a straight x- edge and rounded x+ rear."""

    radius = min(radius, (x_max - x_min) / 2, (y_max - y_min) / 2)
    points = [(x_min, y_min), (x_max - radius, y_min)]
    for angle in range(-90, 1, 10):
        radians = math.radians(angle)
        points.append(
            (
                x_max - radius + radius * math.cos(radians),
                y_min + radius + radius * math.sin(radians),
            )
        )
    points.append((x_max, y_max - radius))
    for angle in range(0, 91, 10):
        radians = math.radians(angle)
        points.append(
            (
                x_max - radius + radius * math.cos(radians),
                y_max - radius + radius * math.sin(radians),
            )
        )
    points.append((x_min, y_max))
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
        rear_back_rounded_points(
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
            label="x+ 后盖：接驳边直角、后端圆角俯视轮廓",
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
            label="后盖背面中央加厚 1/4-20 boss（采购球头）",
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
    ax.set_title("z+ 俯视：前盖正弧 + 后盖直角接驳/后端圆角")
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
