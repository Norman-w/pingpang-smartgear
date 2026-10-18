# v1.0 four inward sloped walls

This candidate is independent of v0.7, v0.8, and v0.9. The v0.9 single
outward wall is not included.

## Four wall instances

The four walls are solid 5 mm-thick XZ prisms, placed in the existing front
and back 5 mm material bands:

| side | X end | X direction | Y band | landing |
|---|---|---|---|---|
| `+Y FRONT` | `-X` | from `x=-27.4` inward toward `+X` | `y=16..21` | `z=0` |
| `+Y FRONT` | `+X` | from `x=+27.4` inward toward `-X` | `y=16..21` | `z=0` |
| `-Y BACK` | `-X` | from `x=-27.4` inward toward `+X` | `y=-21..-16` | `z=0` |
| `-Y BACK` | `+X` | from `x=+27.4` inward toward `-X` | `y=-21..-16` | `z=0` |

The roof-end interval overlaps the roof by 1 mm in X; the lower interval
overlaps the corresponding existing side wall by 1 mm in X. Therefore each
wall is positively connected to both the roof and the side wall, rather than
touching only at an edge or point. The roof remains the accepted v0.7 eaves12
geometry (`x=-27.4..+27.4`, width 54.8 mm).

The blue lower tube top is `z=0`. The centre screw through-hole, round nut
pocket, 20 mm U inner gap, lower hooks, and 1.5 mm hook height come from v0.7
unchanged.

## Actual OpenSCAD checks

- [four-wall isometric](../../review/perpendicular-u-joint-v1.0-four-sloped-walls/01-four-walls-isometric.png)
- [+Y FRONT XZ](../../review/perpendicular-u-joint-v1.0-four-sloped-walls/02-front-plus-y-xz.png)
- [-Y BACK XZ](../../review/perpendicular-u-joint-v1.0-four-sloped-walls/03-back-minus-y-xz.png)
- [candidate STL](../../exports/perpendicular-u-joint-v1.0-four-sloped-walls/perpendicular-double-u-guard-v1.0-four-sloped-walls.stl)

OpenSCAD rendered all three review scenes and the STL export as manifold
objects with no reported errors. This is still digital geometry evidence;
PETG fit, ground clearance, screw-head clearance, and impact/load acceptance
require a physical first article.
