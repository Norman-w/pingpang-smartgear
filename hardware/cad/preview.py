"""Generate a lightweight visual preview of the first CAD parameter set.

This deliberately mirrors only the design intent of the OpenSCAD source: it is
not an STL parser or a replacement for OpenSCAD. It is useful in CI and on
machines where the OpenSCAD GUI/CLI is not installed.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "preview.png"

POST_D = 25
OUTER_X = -90
OUTER_Y = 24
INNER_X = 60
INNER_Y = 16
POST_X = INNER_X + 5
ROD_LEN = 130
BEAM_FIRST = 10
BEAM_COUNT = 10
BEAM_PITCH = 10
REFERENCE_HEIGHT = 50
ASSEMBLY_SPAN = 700


def draw_clamp(ax, x_offset: float, mirror: int, label: str) -> None:
    def p(x: float, y: float) -> tuple[float, float]:
        return (x_offset + mirror * x, y)

    arm_a = [p(OUTER_X, OUTER_Y), p(INNER_X, -INNER_Y)]
    arm_b = [p(OUTER_X, -OUTER_Y), p(INNER_X, INNER_Y)]
    for arm in (arm_a, arm_b):
        ax.plot([arm[0][0], arm[1][0]], [arm[0][1], arm[1][1]], color="#e67e22", linewidth=8, solid_capstyle="round")

    post = p(POST_X, 0)
    ax.add_patch(Circle(post, POST_D / 2, facecolor="#777b80", edgecolor="#30343b", alpha=0.8))

    for y, color in ((OUTER_Y, "#bbc0c7"), (-OUTER_Y, "#bbc0c7")):
        roller = p(OUTER_X, y)
        ax.add_patch(Circle(roller, 8, facecolor=color, edgecolor="#444", linewidth=1.5))

    for x, direction in ((POST_X - 25, 1), (POST_X + 25, -1)):
        cx, cy = p(x, 0)
        points = [(cx, cy), (cx + mirror * direction * 22, cy + 18), (cx + mirror * direction * 22, cy - 18)]
        ax.add_patch(Polygon(points, closed=True, facecolor="#f39c12", alpha=0.8))

    rod = p(POST_X + 4, 0)
    ax.plot([rod[0], rod[0]], [0, 0], marker="o", color="#d4af37", markersize=4)
    ax.text(x_offset, -45, label, ha="center", va="top", fontsize=9)


def make_preview() -> None:
    fig, (top, front) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)

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
