# v1.3 triangular concave-corner fills

This candidate is independent of v0.7, v0.9, v1.0, v1.1, and v1.2. It uses
four mirrored triangular prisms, one at each front/back and left/right X
corner, instead of a continuous equal-thickness wall.

## XZ corner section

- `-X` blocks run from the roof end `x=-27.4` inward toward `+X`.
- `+X` blocks run from `x=+27.4` inward toward `-X`.
- Each top edge is wide and overlaps the roof volume by `0.5 mm` at
  `z=21..21.5`.
- Each triangle tapers downward to the inner point `x=±14.4,z=0`; this point
  enters the existing side wall (`x=±15.4..±10.4`) by 1 mm while staying
  outside the blue tube envelope `x=-10..+10`.
- Each prism is only `y=+10..+21` or `y=-21..-10` (11 mm), matching the actual
  front/back U plate depth; the central `y=-10..+10` passage stays open.

The four modules are `front_neg_x_triangle`, `front_pos_x_triangle`,
`back_neg_x_triangle`, and `back_pos_x_triangle`.

## Existing hook and screw constraints

- v0.7 bottom retaining hooks remain at `z=-21..-19.5` (1.5 mm) and are not
  moved by the corner fills.
- The final printable body applies `vertical_screw_relief()` after the entire
  four-block union. The screw clearance is Ø6.2 mm along Z and the round top
  nut pocket remains.

## Actual OpenSCAD renders and STL

- [等轴图](../../review/perpendicular-u-joint-v1.3-triangular-corner-fills/01-triangular-fills-isometric.png)
- [前侧 XZ 三角剖面](../../review/perpendicular-u-joint-v1.3-triangular-corner-fills/02-front-xz-triangle-profile.png)
- [后侧 XZ 三角剖面](../../review/perpendicular-u-joint-v1.3-triangular-corner-fills/03-back-xz-triangle-profile.png)
- [顶部通道切片](../../review/perpendicular-u-joint-v1.3-triangular-corner-fills/04-top-channel-slice.png)
- [中心通孔剖面](../../review/perpendicular-u-joint-v1.3-triangular-corner-fills/05-through-hole-section.png)
- [底部卡脚核对](../../review/perpendicular-u-joint-v1.3-triangular-corner-fills/06-bottom-hook-check.png)
- [候选 STL](../../exports/perpendicular-u-joint-v1.3-triangular-corner-fills/perpendicular-double-u-guard-v1.3-triangular-corner-fills.stl)

All previews are generated from real OpenSCAD geometry with the OpenSCAD CLI;
no image-generation model was used. OpenSCAD syntax, renders, and STL export
completed with `NoError` and manifold top-level objects. PETG fit and load
acceptance still require a physical first article.
