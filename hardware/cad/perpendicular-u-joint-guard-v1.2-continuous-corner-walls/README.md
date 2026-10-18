# v1.2 continuous corner walls

This candidate is independent of v0.7, v0.9, v1.0, and v1.1. It uses two
continuous X-end solid walls rather than four separated front/back ribs.

## Continuous wall geometry

- Negative-X wall: XZ trapezoid from the `-X` roof end toward `+X`, with
  roof-side range `x=-27.4..-26.4` and lower side-wall overlap
  `x=-15.4..-14.4`.
- Positive-X wall: mirrored inward from `+X`, with roof-side range
  `x=+26.4..+27.4` and lower side-wall overlap `x=+14.4..+15.4`.
- Both walls run continuously through `y=-21..+21` (42 mm), so their front and
  back ends form the four visible corner faces instead of four isolated plates.
- The walls land at `z=0` and occupy only the side regions outside the blue
  lower tube envelope `x=-10..+10`; the central tube path remains open.
- Roof dimensions remain the accepted eaves12 range `x=-27.4..+27.4`.

## Bottom hook and screw hole

- The imported v0.7 bottom hooks remain at `z=-21..-19.5`, exactly 1.5 mm
  high; they are not moved into the upper wall or roof.
- The final body is `difference(union(base, continuous_walls),
  vertical_screw_relief())`; the Ø6.2 Z-axis hole and round nut pocket are
  therefore applied after the whole union.

## Actual SCAD renders and STL

- [连续墙等轴图](../../review/perpendicular-u-joint-v1.2-continuous-corner-walls/01-continuous-walls-isometric.png)
- [前侧 XZ](../../review/perpendicular-u-joint-v1.2-continuous-corner-walls/02-front-xz.png)
- [后侧 XZ](../../review/perpendicular-u-joint-v1.2-continuous-corner-walls/03-back-xz.png)
- [顶部连续性/中央通道切片](../../review/perpendicular-u-joint-v1.2-continuous-corner-walls/04-top-continuity-channel.png)
- [底部通道视图](../../review/perpendicular-u-joint-v1.2-continuous-corner-walls/05-bottom-channel.png)
- [中心通孔剖面](../../review/perpendicular-u-joint-v1.2-continuous-corner-walls/06-through-hole-section.png)
- [独立底部卡脚核对](../../review/perpendicular-u-joint-v1.2-continuous-corner-walls/07-bottom-hook-check.png)
- [候选 STL](../../exports/perpendicular-u-joint-v1.2-continuous-corner-walls/perpendicular-double-u-guard-v1.2-continuous-corner-walls.stl)

All previews are generated from real OpenSCAD geometry with the OpenSCAD CLI;
no image-generation model was used. OpenSCAD syntax, renders, and STL export
completed with `NoError` and manifold top-level objects. Physical PETG fit and
impact/load acceptance still require a first article.
