# v1.1 full-depth four-corner walls

This candidate is independent of v0.7, v0.9, and v1.0. It replaces the thin
5 mm Y ribs with full-depth solid walls for each front/back U plate.

## Geometry contract

- `+Y FRONT`: every corner wall spans `y=+10..+21` (11 mm).
- `-Y BACK`: every corner wall spans `y=-21..-10` (11 mm).
- The central passage `y=-10..+10` remains open for the blue lower tube.
- `-X` walls slope inward toward `+X`; `+X` walls slope inward toward `-X`.
- All four walls land at `z=0`, the blue lower tube's top surface.
- Roof range remains `x=-27.4..+27.4` (the accepted 12 mm eaves).
- Roof and side-wall interfaces each have 1 mm positive X overlap.
- The existing material thickness is retained at 5 mm; the 11 mm value is the
  complete front/back U-plate depth, not an arbitrary thickening.

## Through-hole

The final printable union is followed by `difference(..., vertical_screw_relief())`.
The clearance remains Ø6.2 mm along Z, and the round top nut pocket remains
from v0.7. The centre-slice preview makes the open bore and nut pocket visible.

## Actual OpenSCAD previews and STL

- [等轴图：四个整段包角墙](../../review/perpendicular-u-joint-v1.1-full-corner-walls/01-four-full-walls-isometric.png)
- [+Y FRONT XZ](../../review/perpendicular-u-joint-v1.1-full-corner-walls/02-front-plus-y-xz.png)
- [-Y BACK XZ](../../review/perpendicular-u-joint-v1.1-full-corner-walls/03-back-minus-y-xz.png)
- [顶部切片：11 mm / 20 mm / 11 mm](../../review/perpendicular-u-joint-v1.1-full-corner-walls/04-top-y-depth-gap.png)
- [中心 Z 向通孔剖面](../../review/perpendicular-u-joint-v1.1-full-corner-walls/05-through-hole-section.png)
- [候选 STL](../../exports/perpendicular-u-joint-v1.1-full-corner-walls/perpendicular-double-u-guard-v1.1-full-corner-walls.stl)

OpenSCAD syntax, all review renders, and STL export completed with `NoError`
and manifold top-level objects. Physical PETG fit, screw clearance, ground
clearance, and impact/load acceptance still require a first article.
