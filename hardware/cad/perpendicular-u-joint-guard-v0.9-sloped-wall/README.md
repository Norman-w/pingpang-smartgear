# v0.9 sloped-wall candidate

This is an isolated candidate based on the accepted v0.7 eaves12 geometry. It
does not overwrite v0.7 or v0.8.

## Coordinate interpretation

- `x`: barrier long direction; the accepted roof is `x=-27.4..+27.4`.
- `y`: front/back direction; the two U inner faces remain 20 mm apart.
- `z`: vertical direction; the blue lower 20×20 tube occupies `z=-20..0`, so
  its top surface is `z=0`.
- The vertical screw remains a through-hole on the z axis and the round top
  nut pocket remains unchanged.

## Candidate addition

The new solid wall is a triangular prism in the XZ plane, extruded 5 mm along
Y:

- roof-end edge: `x=-27.4`, `z=21..29`;
- diagonal direction: toward `-X` and `-Z`;
- landing point: `x=-39.4`, `z=0`;
- solid depth: `5 mm` along Y.

The roof-end edge overlaps the existing roof, so the STL is still one connected
printed body. The wall is outside the 20 mm central lower-foot passage and does
not change the screw hole.

## Actual OpenSCAD previews

- [等轴坐标预览](../../review/perpendicular-u-joint-v0.9-sloped-wall/01-candidate-isometric.png)
- [XZ 核对预览](../../review/perpendicular-u-joint-v0.9-sloped-wall/02-candidate-xz.png)
- [候选一体 STL](../../exports/perpendicular-u-joint-v0.9-sloped-wall/perpendicular-double-u-guard-v0.9-sloped-wall.stl)

The previews are digital geometry checks only. PETG fit, screw-head envelope,
ground clearance, and load/impact resistance still need first-article tests.
