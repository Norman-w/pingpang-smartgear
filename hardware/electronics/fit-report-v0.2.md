# Pingpang SmartGear electronics system fit report v0.2

- Overall mechanical/package status: **PASS**
- Generated: `2026-09-03T09:49:01.936579+00:00`
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
| `ui-panel-v0.2.kicad_pcb` | 58.0 x 28.1 mm | 2 | 13 | 7 | 18 | 0 | 21 |

The PCB files and board STL/STEP exports are real KiCad artifacts. The main board still has an open copper gate (`65` unconnected items); it is not a fabrication/Gerber release.

- Physical cable connectors pass the generated `MX1.25`/1.25 mm pad-pitch contract, and every such PCB connector has a matching MX1.25 schematic instance; USB-C and button footprints are separate interfaces.
- Ordered connector pin-to-net contracts pass for the mother board, receiver 3-wire inputs, emitter 2-wire outputs and UI harnesses.
- Native PCB DRC aggregate: `PASS`; errors, expected isolated-copper warnings and unconnected airwires are reported separately below.

## Same-datum enclosure fit

| assembly | result | critical minimum margin |
|---|---|---:|
| right ESP32 mother board | **PASS** | 1.500 mm |
| left emitter power board | **PASS** | 4.000 mm |
| cover UI board | **PASS** | 6.000 mm |
| internal battery envelope | **PASS** | 2.000 mm |
| vertical M6 receiver carrier | **PASS** | 1.500 mm |

Mother-board boss centers are taken from the four NPTH positions in `esp32-control-v0.1.kicad_pcb`; the report does not use a symmetric placeholder hole pattern.

## Interference and exploded-view evidence

- AABB fit: conservative x/y/z envelope checks for every imported KiCad board and both internal battery packs.
- Boolean interference: `PASS` across both clamp sides and both M6 sides.
- OpenSCAD view compilation: `PASS` for full cutaway, physical shell cutaway, per-side exploded views, M6 integration, and M6 exploded assembly.
- Printable package: `37/37` STL files closed and positive volume.

## PCB DRC evidence

| board | DRC status | errors | warnings | unconnected |
|---|---|---:|---:|---:|
| `esp32-control-v0.1.kicad_pcb` | **PASS** | 0 | 0 | 65 |
| `m6-receiver-carrier-v0.2.kicad_pcb` | **PASS_WITH_EXPECTED_WARNINGS** | 0 | 1 | 38 |
| `emitter-power-v0.2.kicad_pcb` | **PASS_WITH_EXPECTED_WARNINGS** | 0 | 2 | 6 |
| `ui-panel-v0.2.kicad_pcb` | **PASS** | 0 | 0 | 15 |

The isolated-copper warnings are expected at this review stage because zones surround intentionally unrouted nets; they do not close the electrical fabrication gate.

## Release boundary

- Mechanical/package gate: **PASS**.
- Electrical fabrication gate: **OPEN** until copper routing, DRC, power-current bench validation, and the placeholder optocoupler/MCU selections are frozen.
- Lid fit is treated as a flush, no-visible-gap mechanical interface; this is not an IP waterproof certification.
