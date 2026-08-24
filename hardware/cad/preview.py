"""Generate a lightweight visual preview of the current integrated net stand.

This mirrors the intent of ``net_stand.scad`` without parsing STL files.  It is
useful in CI and on machines where the OpenSCAD GUI/CLI is not installed; it is
not a replacement for OpenSCAD geometry validation or a strength calculation.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "preview.png"

TABLE_WIDTH = 1525.0
TABLE_THICKNESS = 25.0
TABLE_EDGE = TABLE_WIDTH / 2
POST_OFFSET = 18.0
POST_WIDTH = 28.0
CLAMP_OUTER_EXTENSION = 22.0
POST_CENTER = TABLE_EDGE + POST_OFFSET
CLAMP_SCREW_INSET = 30.0
CLAMP_LOWER_ARM_CLEARANCE = 10.0
CLAMP_LOWER_ARM_TOP = -TABLE_THICKNESS - CLAMP_LOWER_ARM_CLEARANCE
CLAMP_LOWER_ARM_BOTTOM = CLAMP_LOWER_ARM_TOP - 8.0
CLAMP_PRESSURE_PAD_WIDTH = 42.0
CLAMP_PRESSURE_PAD_TOP = -TABLE_THICKNESS - 1.5
CLAMP_PRESSURE_PAD_BOTTOM = CLAMP_PRESSURE_PAD_TOP - 2.0
CLAMP_SCREW_X = -CLAMP_SCREW_INSET
CLAMP_SCREW_BOTTOM = CLAMP_PRESSURE_PAD_TOP - 36.0
CLAMP_KNOB_BOTTOM = CLAMP_SCREW_BOTTOM - 12.0
POST_BOTTOM = CLAMP_LOWER_ARM_TOP
NET_HEIGHT = 152.5
NET_RAIL_HEIGHT = 10.0
BEAM_FIRST = 10.0
BEAM_COUNT = 10
BEAM_PITCH = 10.0
BEAM_LAST = BEAM_FIRST + (BEAM_COUNT - 1) * BEAM_PITCH
POST_TOP = NET_HEIGHT + BEAM_LAST + 3.0 + 18.0
NET_SPAN = 2 * (POST_CENTER - POST_WIDTH / 2)
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
            [-NET_SPAN / 2 + POST_WIDTH / 2 + 8, NET_SPAN / 2 - POST_WIDTH / 2 - 8],
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
    ax.set_ylabel("height above net top / mm")
    ax.grid(True, alpha=0.22)
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper center", fontsize=7, ncol=2)


def draw_side(ax) -> None:
    # 以右侧台边为 x=0，正方向是桌外；画出免打孔 C 形夹体。
    post_x0 = POST_OFFSET - POST_WIDTH / 2
    clamp_pad_end = POST_OFFSET + POST_WIDTH / 2 + CLAMP_OUTER_EXTENSION
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
    ax.add_patch(
        Rectangle(
            (-62, 0),
            clamp_pad_end + 62,
            8,
            facecolor="#69727b",
            label="fixed upper jaw (no drilling)",
        )
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_SCREW_X - 9, CLAMP_LOWER_ARM_BOTTOM),
            clamp_pad_end - CLAMP_SCREW_X + 9,
            8,
            facecolor="#69727b",
            label="fixed lower arm / nut seat",
        )
    )
    ax.add_patch(
        Rectangle(
            (post_x0 + POST_WIDTH, CLAMP_LOWER_ARM_BOTTOM),
            CLAMP_OUTER_EXTENSION,
            51,
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
            2,
            facecolor="#111111",
            label="movable underside pressure pad",
        )
    )
    ax.plot(
        [CLAMP_SCREW_X, CLAMP_SCREW_X],
        [CLAMP_SCREW_BOTTOM, CLAMP_PRESSURE_PAD_TOP],
        color="#444",
        linewidth=3,
        label="M8 screw below tabletop",
    )
    ax.add_patch(
        Rectangle(
            (CLAMP_SCREW_X - 18, CLAMP_KNOB_BOTTOM),
            36,
            12,
            facecolor="#30343b",
            label="hand knob",
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
    ax.set_xlim(-82, clamp_pad_end + 18)
    ax.set_ylim(CLAMP_KNOB_BOTTOM - 8, POST_TOP + 20)
    ax.set_title("No-drill under-table C-clamp: side intent")
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
