"""Generate a lightweight visual preview of the first CAD parameter set.

This deliberately mirrors only the design intent of the OpenSCAD source: it is
not an STL parser or a replacement for OpenSCAD. It is useful in CI and on
machines where the OpenSCAD GUI/CLI is not installed.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "preview.png"

POST_D = 25
OUTER_RADIUS = math.hypot(90, 24)
INNER_RADIUS = math.hypot(60, 16)
INNER_NOMINAL_X = 60
CLAMP_ANGLE_DEG = 15
JAW_LENGTH = 26
POST_X = INNER_NOMINAL_X + 5
ROD_LEN = 130
BEAM_FIRST = 10
BEAM_COUNT = 10
BEAM_PITCH = 10
REFERENCE_HEIGHT = 50
ASSEMBLY_SPAN = 700


def outer_point(sign: int, angle_deg: float = CLAMP_ANGLE_DEG) -> tuple[float, float]:
    angle = math.radians(angle_deg)
    return (-OUTER_RADIUS * math.cos(angle), sign * OUTER_RADIUS * math.sin(angle))


def inner_point(sign: int, angle_deg: float = CLAMP_ANGLE_DEG) -> tuple[float, float]:
    angle = math.radians(angle_deg)
    return (INNER_RADIUS * math.cos(angle), -sign * INNER_RADIUS * math.sin(angle))


def draw_v_jaw(ax, center: tuple[float, float], post: tuple[float, float]) -> None:
    angle = math.atan2(post[1] - center[1], post[0] - center[0])
    endpoints = []
    for offset in (-math.pi / 4, math.pi / 4):
        endpoint_angle = angle + offset
        endpoints.append(
            (
                center[0] + JAW_LENGTH * math.cos(endpoint_angle),
                center[1] + JAW_LENGTH * math.sin(endpoint_angle),
            )
        )
    ax.add_patch(
        Polygon(
            [center, endpoints[0], endpoints[1]],
            closed=True,
            facecolor="#f39c12",
            alpha=0.8,
        )
    )


def draw_motion_envelope(ax, x_offset: float, mirror: int) -> None:
    def p(x: float, y: float) -> tuple[float, float]:
        return (x_offset + mirror * x, y)

    for angle in (10, 20):
        outer_a = outer_point(1, angle)
        outer_b = outer_point(-1, angle)
        inner_a = inner_point(1, angle)
        inner_b = inner_point(-1, angle)
        color = "#6baed6" if angle == 10 else "#fb6a4a"
        for arm_index, (first, second) in enumerate(
            ((outer_a, inner_a), (outer_b, inner_b))
        ):
            label = (
                f"motion envelope {angle}°"
                if arm_index == 0 and x_offset < 0
                else "_nolegend_"
            )
            first_plot = p(*first)
            second_plot = p(*second)
            ax.plot(
                [first_plot[0], second_plot[0]],
                [first_plot[1], second_plot[1]],
                color=color,
                linewidth=2,
                linestyle="--",
                alpha=0.65,
                label=label,
            )


def draw_clamp(ax, x_offset: float, mirror: int, label: str) -> None:
    def p(x: float, y: float) -> tuple[float, float]:
        return (x_offset + mirror * x, y)

    outer_a = outer_point(1)
    outer_b = outer_point(-1)
    inner_a = inner_point(1)
    inner_b = inner_point(-1)
    arm_a = [p(*outer_a), p(*inner_a)]
    arm_b = [p(*outer_b), p(*inner_b)]
    for arm in (arm_a, arm_b):
        ax.plot([arm[0][0], arm[1][0]], [arm[0][1], arm[1][1]], color="#e67e22", linewidth=8, solid_capstyle="round")

    post = p(POST_X, 0)
    ax.add_patch(Circle(post, POST_D / 2, facecolor="#777b80", edgecolor="#30343b", alpha=0.8))

    for point in (outer_a, outer_b):
        roller = p(*point)
        ax.add_patch(Circle(roller, 8, facecolor="#bbc0c7", edgecolor="#444", linewidth=1.5))

    draw_v_jaw(ax, p(*inner_a), post)
    draw_v_jaw(ax, p(*inner_b), post)
    ax.text(x_offset, -45, label, ha="center", va="top", fontsize=9)


def make_preview() -> None:
    fig, (top, front) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)

    draw_motion_envelope(top, -ASSEMBLY_SPAN / 2, 1)
    draw_motion_envelope(top, ASSEMBLY_SPAN / 2, -1)
    draw_clamp(top, -ASSEMBLY_SPAN / 2, 1, "LEFT X CLAMP (TOP)")
    draw_clamp(top, ASSEMBLY_SPAN / 2, -1, "RIGHT X CLAMP (MIRROR)")
    top.plot([-ASSEMBLY_SPAN / 2 + POST_X, ASSEMBLY_SPAN / 2 - POST_X], [0, 0], color="#31a354", linewidth=2, label="reference-line axis")
    top.set_aspect("equal")
    top.set_xlim(-420, 420)
    top.set_ylim(-75, 75)
    top.set_title("True scissor X and bilateral mirror")
    top.set_xlabel("table width / mm")
    top.set_ylabel("clamp top view / mm")
    top.grid(True, alpha=0.25)
    top.legend(loc="upper center", fontsize=8)

    # 正视图：两根方杆、10 个有效光束档位和参考线。
    left = -ASSEMBLY_SPAN / 2 + POST_X
    right = ASSEMBLY_SPAN / 2 - POST_X
    front.plot([left, left], [0, ROD_LEN], color="#d4af37", linewidth=10, solid_capstyle="butt")
    front.plot([right, right], [0, ROD_LEN], color="#d4af37", linewidth=10, solid_capstyle="butt")
    for i in range(BEAM_COUNT):
        h = BEAM_FIRST + i * BEAM_PITCH
        front.plot([left, right], [h, h], color="#4c78a8", linewidth=1.4, alpha=0.8)
        front.text(right + 18, h, f"+{h} mm", va="center", fontsize=8)
    front.plot([left, right], [REFERENCE_HEIGHT, REFERENCE_HEIGHT], color="#31a354", linewidth=2, label="reference line (10 mm detent)")
    front.set_xlim(left - 80, right + 85)
    front.set_ylim(-10, ROD_LEN + 10)
    front.set_title("Continuous beam guide and height detents (front)")
    front.set_xlabel("table width / mm")
    front.set_ylabel("above net top / mm")
    front.grid(True, alpha=0.25)
    front.legend(fontsize=8)

    fig.suptitle("Pingpang SmartGear CAD intent preview (not STL validation)", fontsize=14)
    fig.savefig(OUT, dpi=160)
    print(OUT)


if __name__ == "__main__":
    make_preview()
