# Pingpang SmartGear electronics system fit report v0.2

- Overall mechanical/package status: **PASS**
- Generated: `2026-09-21T23:21:18.596142+00:00`
- Mechanical source: `hardware/cad/net_stand.scad`
- Native KiCad status: `PASS`
- Native KiCad projects: `4` `.kicad_pcb` / `4` `.kicad_pro`; schematic PDF export: `PASS`
- Atopile `.ato`: validate `PASS`, build `PASS` (interface contract only; native KiCad remains the PCB source of truth)
- Native schematics exported: `4/4`; ERC is intentionally OPEN for the first-article review files.
- Retained legacy schematic connector contract: `PASS` (obsolete P2.00/P2.54/PinHeader tokens are rejected).

## Board files and signal budget

| board | outline | copper layers | footprints | 3D models | nets | tracks | unconnected |
|---|---:|---:|---:|---:|---:|---:|---:|
| `esp32-control-v0.1.kicad_pcb` | 86.0 x 32.0 mm | 2 | 43 | 31 | 51 | 2 | 65 |
| `m6-receiver-carrier-v0.2.kicad_pcb` | 80.0 x 32.0 mm | 2 | 27 | 23 | 41 | 0 | 48 |
| `emitter-power-v0.2.kicad_pcb` | 68.0 x 32.0 mm | 2 | 11 | 7 | 30 | 0 | 6 |
| `ui-panel-v0.2.kicad_pcb` | 58.0 x 28.1 mm | 2 | 13 | 9 | 20 | 0 | 32 |

The PCB files and board STL/STEP exports are real KiCad artifacts. The main board still has an open copper gate (`65` unconnected items); it is not a fabrication/Gerber release.

- Physical cable connectors pass the generated `MX1.25`/1.25 mm pad-pitch contract, and every such PCB connector has a matching MX1.25 schematic instance; USB-C and button footprints are separate interfaces.
- Ordered connector pin-to-net contracts pass for the mother board, receiver 3-wire inputs, emitter 2-wire outputs and UI harnesses.
- Native PCB DRC aggregate: `FAIL`; errors, expected isolated-copper warnings and unconnected airwires are reported separately below.

## Same-datum enclosure fit

| assembly | result | critical minimum margin |
|---|---|---:|
| right ESP32 mother board | **PASS** | 4.000 mm |
| left emitter power board | **PASS** | 4.000 mm |
| cover UI board | **PASS** | 0.560 mm |
| internal battery envelope | **PASS** | 2.000 mm |
| vertical M6 receiver carrier | **PASS** | 1.500 mm |

Mother-board retention is the native `esp32-control-v0.1.kicad_pcb` Edge.Cuts contour plus two opposing x-end printed `[`/`]` C-brackets; the full-height webs stay outside the board pocket and the lower/upper lips capture the board without shell bosses or locating pins.

## Interference and exploded-view evidence

- AABB fit: conservative x/y/z envelope checks for every imported KiCad board and both internal battery packs.
- Boolean interference: `PASS` across both clamp sides and both M6 sides.
- OpenSCAD view compilation: `PASS` for full cutaway, physical shell cutaway, per-side exploded views, M6 integration, and M6 exploded assembly.
- Printable package: `41/41` STL files closed and positive volume.

## UI panel direct interface

- Direct datum status: **PASS**. START/MODE, both 0603 LEDs and the USB-C footprint all match the printed insert-panel centers with zero measured coordinate error.
- Insert-panel contract: screen opening `27.4 × 16.4 mm`, button pocket `Ø4.9 mm` with `Ø1.6 mm` plungers, LED bores `Ø2.2 mm`, speaker opening `Ø12.0 mm`, USB-C slot `9.6 × 6.6 mm`, board-to-panel gap `0.6 mm`; panel inserts from the cavity with `0.6 mm` side clearance and finishes `0.0 mm` from the wall datum.
- Retaining-frame contract: `8` cavity-side holes, a `2.5 mm` mounting flange at y=`17.5..20.0 mm` plus a window capture bridge at y=`20.0..25.5 mm`, outer/inner borders `7.0/1.6 mm`, window clearance `0.2 mm`, Ø`2.3 mm` clearance holes for 2 mm mushroom-head self-tapping screws into Ø`1.6 mm` blind pilots cut directly in the solid C-clamp wall; pilot depth `8.3 mm` leaves `0.7 mm` outer-wall floor, with no positive boss and `1.2 mm` minimum edge land. Panel hidden relief cutouts: `none`; outer face screw openings: `none`.
- USB-C mating axis: `PCB normal -> y+ panel`; its KiCad footprint model is `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step (KiCad library model, rotated for y+)`. The final purchased receptacle dimensions/part number remains an explicit first-article item.

## PCB DRC evidence

| board | DRC status | errors | warnings | unconnected |
|---|---|---:|---:|---:|
| `esp32-control-v0.1.kicad_pcb` | **PASS** | 0 | 0 | 65 |
| `m6-receiver-carrier-v0.2.kicad_pcb` | **PASS_WITH_EXPECTED_WARNINGS** | 0 | 1 | 38 |
| `emitter-power-v0.2.kicad_pcb` | **PASS_WITH_EXPECTED_WARNINGS** | 0 | 2 | 6 |
| `ui-panel-v0.2.kicad_pcb` | **FAIL** | 18 | 0 | 21 |

The isolated-copper warnings are expected at this review stage because zones surround intentionally unrouted nets; they do not close the electrical fabrication gate.

## Release boundary

- Mechanical/package gate: **PASS**.
- Electrical fabrication gate: **OPEN** until copper routing, DRC, power-current bench validation, and the placeholder optocoupler/MCU selections are frozen.
- UI panel interface gate: **PASS**; the real button/LED/USB-C footprints and KiCad 3D models are checked against the printed y+ insert-panel datum. Screen/speaker/battery remain the off-board SCAD envelopes; the purchased USB-C dimensions/part number remains open until first article.
- Lid fit is treated as a flush, no-visible-gap mechanical interface; this is not an IP waterproof certification.
