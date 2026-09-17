#!/usr/bin/env python3
"""Generate the connectorized ESP32 control schematic in native KiCad format.

The PCB generators in this repository are intentionally code-driven, but the
deliverable still needs a schematic that opens in KiCad.  This small generator
embeds the exact symbols from the installed KiCad libraries and emits a
normal ``.kicad_sch`` file, so the schematic is inspectable without relying on
an external Atopile conversion step.
"""

from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "esp32-control-v0.1/esp32-control-v0.1.kicad_sch"


def kicad_symbol_root() -> Path:
    candidates = [
        Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"),
        Path("/usr/share/kicad/symbols"),
    ]
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "Connector_Generic.kicad_sym").is_file():
            return candidate
    raise RuntimeError("KiCad symbol libraries were not found")


def balanced_block(text: str, start: int) -> str:
    """Return the parenthesized expression beginning at *start*."""

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError(f"unbalanced KiCad expression at offset {start}")


def extract_library_symbol(path: Path, name: str, qualified: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf'^\s*\(symbol "{re.escape(name)}"', text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"symbol {name!r} not found in {path}")
    block = balanced_block(text, text.find("(", match.start()))
    return block.replace(f'(symbol "{name}"', f'(symbol "{qualified}"', 1)


def symbol_pin_numbers(block: str) -> list[str]:
    numbers = re.findall(r'\(number "([^"]+)"', block)
    return list(dict.fromkeys(numbers))


def uid() -> str:
    return str(uuid.uuid4())


def field(name: str, value: str, x: float, y: float, hidden: bool = False) -> str:
    hide = "\n\t\t\t\t(hide yes)" if hidden else ""
    return (
        f'\t\t(property "{name}" "{value}"\n'
        f'\t\t\t(at {x:g} {y:g} 0)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t){hide}\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
    )


def placed_symbol(
    lib_id: str,
    definition: str,
    reference: str,
    value: str,
    footprint: str,
    x: float,
    y: float,
    project_uuid: str,
    project_name: str,
) -> str:
    pins = symbol_pin_numbers(definition)
    lines = [
        "\t(symbol",
        f'\t\t(lib_id "{lib_id}")',
        f"\t\t(at {x:g} {y:g} 0)",
        "\t\t(unit 1)",
        "\t\t(exclude_from_sim no)",
        "\t\t(in_bom yes)",
        "\t\t(on_board yes)",
        "\t\t(dnp no)",
        f'\t\t(uuid "{uid()}")',
        field("Reference", reference, 0, -3.81),
        field("Value", value, 0, 3.81),
        field("Footprint", footprint, 0, 0, hidden=True),
        field("Datasheet", "~", 0, 0, hidden=True),
        field("Description", "Pingpang SmartGear connectorized control path", 0, 0, hidden=True),
    ]
    for number in pins:
        lines.extend(
            [
                f'\t\t(pin "{number}"',
                f'\t\t\t(uuid "{uid()}")',
                "\t\t)",
            ]
        )
    lines.extend(
        [
            "\t\t(instances",
            f'\t\t\t(project "{project_name}"',
            f'\t\t\t\t(path "/{project_uuid}"',
            f'\t\t\t\t\t(reference "{reference}")',
            "\t\t\t\t\t(unit 1)",
            "\t\t\t\t)",
            "\t\t\t)",
            "\t\t)",
            "\t)",
        ]
    )
    return "\n".join(lines)


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        "\t(wire\n"
        f"\t\t(pts (xy {x1:g} {y1:g}) (xy {x2:g} {y2:g}))\n"
        "\t\t(stroke (width 0) (type solid))\n"
        f'\t\t(uuid "{uid()}")\n'
        "\t)"
    )


def label(name: str, x: float, y: float, angle: int = 0) -> str:
    justify = "left bottom" if angle == 0 else "right bottom"
    return (
        f'\t(label "{name}"\n'
        f"\t\t(at {x:g} {y:g} {angle})\n"
        "\t\t(effects\n"
        "\t\t\t(font (size 1.27 1.27))\n"
        f"\t\t\t(justify {justify})\n"
        "\t\t)\n"
        f'\t\t(uuid "{uid()}")\n'
        "\t)"
    )


def note(text: str, x: float, y: float, size: float = 1.27) -> str:
    return (
        f'\t(text "{text}"\n'
        "\t\t(exclude_from_sim no)\n"
        f"\t\t(at {x:g} {y:g} 0)\n"
        f"\t\t(effects (font (size {size:g} {size:g})) (justify left bottom))\n"
        f'\t\t(uuid "{uid()}")\n'
        "\t)"
    )


def main() -> int:
    symbols = kicad_symbol_root()
    library_specs = [
        ("RF_Module", "RF_Module.kicad_sym", "ESP32-S3-WROOM-1"),
        ("Connector", "Connector.kicad_sym", "USB_C_Receptacle_USB2.0_16P"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x02"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x04"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x06"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x08"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x12"),
        ("Device", "Device.kicad_sym", "Battery"),
        ("Device", "Device.kicad_sym", "C"),
        ("Device", "Device.kicad_sym", "LED"),
        ("Device", "Device.kicad_sym", "R"),
        ("Regulator_Switching", "Regulator_Switching.kicad_sym", "TPS62162DSG"),
        ("Switch", "Switch.kicad_sym", "SW_Push"),
        ("power", "power.kicad_sym", "+3V3"),
        ("power", "power.kicad_sym", "GND"),
        ("power", "power.kicad_sym", "VBUS"),
    ]
    definitions: dict[str, str] = {}
    for library, filename, name in library_specs:
        lib_id = f"{library}:{name}"
        definitions[lib_id] = extract_library_symbol(
            symbols / filename, name, lib_id
        )

    project_name = "esp32-control-v0.1"
    project_uuid = uid()
    placed = [
        placed_symbol(
            "RF_Module:ESP32-S3-WROOM-1",
            definitions["RF_Module:ESP32-S3-WROOM-1"],
            "U1",
            "ESP32-S3-WROOM-1-N16R8",
            "RF_Module:ESP32-S3-WROOM-1",
            104,
            118,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector:USB_C_Receptacle_USB2.0_16P",
            definitions["Connector:USB_C_Receptacle_USB2.0_16P"],
            "J1",
            "USB-C POWER + DATA",
            "Connector_USB:GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
            28,
            50,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x02",
            definitions["Connector_Generic:Conn_01x02"],
            "J2",
            "BATTERY MX1.25 LOCK 2P",
            "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            230,
            52,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x02",
            definitions["Connector_Generic:Conn_01x02"],
            "J3",
            "M6 SENSOR 10-30V MX1.25 2P",
            "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            230,
            88,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x02",
            definitions["Connector_Generic:Conn_01x02"],
            "J6",
            "PVDF COMPARATOR AUX MX1.25 2P DNP",
            "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            230,
            168,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x02",
            definitions["Connector_Generic:Conn_01x02"],
            "J8",
            "M6 SENSOR RAIL MX1.25 2P",
            "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            230,
            204,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Device:Battery",
            definitions["Device:Battery"],
            "BT1",
            "PROTECTED 1S Li-ion 65x30x7",
            "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            28,
            155,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x08",
            definitions["Connector_Generic:Conn_01x08"],
            "U2",
            "IP5305T-HSOP8-1EP / 1S POWER",
            "Package_SO:HTSOP-8-1EP_3x3mm_P0.65mm_EP1.6x2.4mm",
            60,
            155,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Regulator_Switching:TPS62162DSG",
            definitions["Regulator_Switching:TPS62162DSG"],
            "U3",
            "TPS62162DSG / 3V3 BUCK",
            "Package_DFN_QFN:WSON-8-1EP_2x2mm_P0.5mm_EP0.8x1.6mm",
            78,
            220,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x08",
            definitions["Connector_Generic:Conn_01x08"],
            "J4",
            "M6 CARRIER HOST MX1.25 LOCK 8P",
            "Connector_JST:JST_GH_SM08B-GHS-TB_1x08-1MP_P1.25mm_Horizontal",
            182,
            55,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x12",
            definitions["Connector_Generic:Conn_01x12"],
            "J7",
            "UI PANEL MX1.25 LOCK 12P",
            "Connector_JST:JST_GH_SM12B-GHS-TB_1x12-1MP_P1.25mm_Horizontal",
            182,
            125,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x04",
            definitions["Connector_Generic:Conn_01x04"],
            "J5",
            "PVDF ADC AUX MX1.25",
            "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal",
            182,
            205,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Switch:SW_Push",
            definitions["Switch:SW_Push"],
            "SW1",
            "POWER / START KEY",
            "Button_Switch_THT:SW_PUSH_6mm",
            55,
            215,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Device:LED",
            definitions["Device:LED"],
            "D1",
            "STATUS LED",
            "LED_SMD:LED_0603_1608Metric",
            135,
            215,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Device:C",
            definitions["Device:C"],
            "C1",
            "100uF USB input bulk",
            "Capacitor_SMD:C_0805_2012Metric",
            54,
            65,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "Device:C",
            definitions["Device:C"],
            "C2",
            "10uF 3V3 rail",
            "Capacitor_SMD:C_0805_2012Metric",
            78,
            185,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "power:+3V3",
            definitions["power:+3V3"],
            "#PWR01",
            "+3V3",
            "",
            88,
            88,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "power:VBUS",
            definitions["power:VBUS"],
            "#PWR02",
            "VBUS",
            "",
            42,
            42,
            project_uuid,
            project_name,
        ),
        placed_symbol(
            "power:GND",
            definitions["power:GND"],
            "#PWR03",
            "GND",
            "",
            104,
            245,
            project_uuid,
            project_name,
        ),
    ]

    wires = [
        wire(220, 52, 224.92, 52),
        wire(220, 49.46, 224.92, 49.46),
        wire(220, 88, 224.92, 88),
        wire(220, 85.46, 224.92, 85.46),
        wire(220, 168, 224.92, 168),
        wire(220, 165.46, 224.92, 165.46),
        wire(220, 204, 224.92, 204),
        wire(220, 201.46, 224.92, 201.46),
        wire(42, 42, 54, 42),
        wire(42, 42, 42, 65),
        wire(42, 65, 54, 65),
        wire(54, 65, 88, 65),
        wire(88, 65, 88, 90),
        wire(60, 145, 60, 125),
        wire(60, 125, 88, 125),
        wire(88, 125, 88, 90),
        wire(88, 90, 88, 100),
        wire(88, 100, 88, 118),
        wire(104, 90, 104, 100),
        wire(104, 100, 142, 100),
        wire(142, 100, 142, 55),
        wire(142, 55, 177, 55),
        wire(119, 112, 150, 112),
        wire(150, 112, 150, 125),
        wire(150, 125, 177, 125),
        wire(119, 124, 145, 124),
        wire(145, 124, 145, 205),
        wire(145, 205, 177, 205),
        wire(28, 165, 45, 165),
        wire(45, 165, 45, 155),
        wire(45, 155, 52, 155),
        wire(78, 220, 104, 220),
        wire(104, 220, 104, 145),
        wire(104, 145, 104, 146),
        wire(55, 215, 55, 205),
        wire(55, 205, 70, 205),
        wire(70, 205, 70, 185),
        wire(70, 185, 78, 185),
        wire(135, 215, 135, 200),
        wire(135, 200, 160, 200),
        wire(160, 200, 160, 125),
        wire(160, 125, 177, 125),
        wire(104, 145, 104, 245),
    ]
    labels = [
        label("BAT_P", 220, 52),
        label("GND", 220, 49.46),
        label("SENSOR_EXT_10-30V", 220, 88),
        label("GND", 220, 85.46),
        label("PVDF_CMP_AUX_L", 220, 168),
        label("PVDF_CMP_AUX_R", 220, 165.46),
        label("SENSOR_FUSED", 220, 204),
        label("GND", 220, 201.46),
        label("VBUS_USB_C", 43, 42),
        label("BAT_1S", 29, 165),
        label("SYS_5V", 61, 125),
        label("+3V3_MAIN", 89, 90),
        label("M6_SPI_SCK", 178, 55),
        label("M6_SPI_MOSI", 178, 58),
        label("M6_SPI_MISO", 178, 61),
        label("M6_IRQ0..9", 178, 64),
        label("UI_I2C_SDA/SCL", 178, 125),
        label("UI_I2S_SPK", 178, 128),
        label("UI_START_MODE", 178, 131),
        label("PVDF_ADC_AUX", 178, 205),
        label("GND", 105, 245),
    ]
    notes = [
        note("PINGPANG SMARTGEAR / ESP32-S3 CONTROL + 1S POWER", 12, 14, 2.0),
        note("J1 USB-C: VBUS + D+/D-; ESD/PTC and CC pulldowns are on the mother PCB", 12, 22),
        note("BT1 is a protected 1S pouch in the left emitter-side clamp; J_BAT is serviceable", 12, 28),
        note("U2 IP5305 power path -> SYS_5V; U3 TPS62162 -> regulated +3V3 for ESP32 and sensors", 12, 34),
        note("J4: MX1.25 keyed harness to M6 carrier; J7: MX1.25 keyed UI daughter board", 116, 28),
        note("J5: PVDF / auxiliary ADC; every field wire leaves through a lockable connector", 116, 34),
        note("J2/J3/J6/J8: the remaining 2-pin MX1.25 battery, sensor-rail and AUX interfaces", 116, 40),
        note("Electrical release gate: PCB placement/net assignment exists; copper routing and bench validation remain open", 12, 270),
        note("Mechanical source: hardware/cad/net_stand.scad | 3D board exports: hardware/electronics/3d/v0.2", 12, 277),
    ]

    root = [
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{project_uuid}")',
        "\t(paper \"A4\")",
        "\t(title_block",
        '\t\t(title "ESP32-S3 control, power and connector harness")',
        '\t\t(date "2026-08-28")',
        '\t\t(rev "v0.2")',
        '\t\t(company "Pingpang SmartGear")',
        '\t\t(comment 1 "Native KiCad schematic generated from the same board contract")',
        '\t\t(comment 2 "Mechanical source: hardware/cad/net_stand.scad")',
        '\t\t(comment 3 "Routing and bench validation remain release gates")',
        "\t)",
        "\t(lib_symbols",
    ]
    for definition in definitions.values():
        root.append(definition)
    root.append("\t)")
    root.extend(notes)
    root.extend(wires)
    root.extend(labels)
    root.extend(placed)
    root.extend(
        [
            "\t(sheet_instances",
            "\t\t(path \"/\"",
            '\t\t\t(page "1")',
            "\t\t)",
            "\t)",
            "\t(embedded_fonts no)",
            ")",
        ]
    )
    OUT.write_text("\n".join(root) + "\n", encoding="utf-8")
    print(f"SCHEMATIC_OK {OUT} ({len(definitions)} embedded symbols, {len(placed)} instances)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
