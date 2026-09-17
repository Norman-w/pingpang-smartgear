#!/usr/bin/env python3
"""Generate native KiCad review schematics for the three daughter boards.

The PCB generators remain the mechanical/footprint source of truth.  These
schematics deliberately expose the real connector and channel topology while
keeping unresolved first-article parts visible as review placeholders.
"""

from __future__ import annotations

from pathlib import Path

from generate_kicad_schematic import (
    extract_library_symbol,
    kicad_symbol_root,
    label,
    note,
    placed_symbol,
    uid,
    wire,
)


HERE = Path(__file__).resolve().parent


def load_definitions(specs: list[tuple[str, str, str]]) -> dict[str, str]:
    root = kicad_symbol_root()
    definitions: dict[str, str] = {}
    for library, filename, name in specs:
        lib_id = f"{library}:{name}"
        definitions[lib_id] = extract_library_symbol(
            root / filename, name, lib_id
        )
    return definitions


def schematic(
    output: Path,
    title: str,
    revision: str,
    definitions: dict[str, str],
    placed: list[str],
    wires: list[str],
    labels: list[str],
    notes: list[str],
) -> None:
    project_name = output.stem
    project_uuid = uid()
    root = [
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{project_uuid}")',
        '\t(paper "A4")',
        "\t(title_block",
        f'\t\t(title "{title}")',
        '\t\t(date "2026-08-28")',
        f'\t\t(rev "{revision}")',
        '\t\t(company "Pingpang SmartGear")',
        '\t\t(comment 1 "Native KiCad daughter-board review schematic")',
        '\t\t(comment 2 "Connectorized field wiring; first-article release gate remains open")',
        '\t\t(comment 3 "Mechanical package is checked separately against net_stand.scad")',
        "\t)",
        "\t(lib_symbols",
    ]
    root.extend(definitions.values())
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
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(root) + "\n", encoding="utf-8")
    print(f"SCHEMATIC_OK {output} ({len(placed)} instances)")


def receiver_schematic() -> None:
    specs = [
        ("MCU_ST_STM32G0", "MCU_ST_STM32G0.kicad_sym", "STM32G031C8Ux"),
        ("Isolator", "Isolator.kicad_sym", "LTV-817"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x02"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x03"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x08"),
        ("Device", "Device.kicad_sym", "R"),
        ("Device", "Device.kicad_sym", "C"),
        ("power", "power.kicad_sym", "+3V3"),
        ("power", "power.kicad_sym", "GND"),
    ]
    definitions = load_definitions(specs)
    project_uuid = uid()
    placed: list[str] = [
        placed_symbol(
            "MCU_ST_STM32G0:STM32G031C8Ux",
            definitions["MCU_ST_STM32G0:STM32G031C8Ux"],
            "U_MCU",
            "STM32G031K8U6 / 10-channel edge capture",
            "Package_DFN_QFN:UFQFPN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm",
            190,
            125,
            project_uuid,
            "m6-receiver-carrier-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x08",
            definitions["Connector_Generic:Conn_01x08"],
            "J_HOST",
            "MOTHER HOST MX1.25 LOCK 8P",
            "Connector_JST:JST_GH_SM08B-GHS-TB_1x08-1MP_P1.25mm_Horizontal",
            250,
            80,
            project_uuid,
            "m6-receiver-carrier-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x02",
            definitions["Connector_Generic:Conn_01x02"],
            "J_PWR",
            "SENSOR RAIL MX1.25 2P",
            "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            250,
            165,
            project_uuid,
            "m6-receiver-carrier-v0.2",
        ),
    ]
    for index in range(10):
        y = 28 + index * 18
        placed.append(
            placed_symbol(
                "Connector_Generic:Conn_01x03",
                definitions["Connector_Generic:Conn_01x03"],
                f"J_RX{index:02d}",
                f"RX{index:02d} M6 V/G/S MX1.25",
                "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal",
                30,
                y,
                project_uuid,
                "m6-receiver-carrier-v0.2",
            )
        )
        placed.append(
            placed_symbol(
                "Isolator:LTV-817",
                definitions["Isolator:LTV-817"],
                f"U_OP{index:02d}",
                f"RX{index:02d} isolation",
                "Package_SO:SOIC-4_4.55x2.6mm_P1.27mm",
                98,
                y,
                project_uuid,
                "m6-receiver-carrier-v0.2",
            )
        )
    wires = [
        wire(45, 28, 86, 28),
        wire(45, 46, 86, 46),
        wire(45, 64, 86, 64),
        wire(45, 82, 86, 82),
        wire(45, 100, 86, 100),
        wire(45, 118, 86, 118),
        wire(45, 136, 86, 136),
        wire(45, 154, 86, 154),
        wire(45, 172, 86, 172),
        wire(45, 190, 86, 190),
        wire(105, 125, 175, 125),
        wire(205, 125, 235, 80),
    ]
    labels = [
        label("RX00..RX09: V / GND / NPN_SIG", 48, 22),
        label("ISOLATED EDGE INPUTS", 106, 22),
        label("SPI + IRQ + RESET", 208, 72),
        label("10-30V SENSOR RAIL", 208, 157),
        label("3V3_LOGIC", 151, 125),
    ]
    notes = [
        note("PINGPANG / M6 RECEIVER CARRIER / 10 CHANNELS", 14, 12, 1.8),
        note("Each RX connector is a separate keyed 3-wire harness; board sockets are grouped after the 20 mm optical harness converges", 14, 18),
        note("LTV-817 and R_IN values remain first-article placeholders until the purchased NPN sensor output is measured", 14, 230),
        note("J_HOST is the 8-wire SPI/IRQ/reset handoff to the ESP32 mother board; J_PWR is sensor-side power only", 14, 237),
        note("ERC/open connectivity is intentional at this review stage; do not release Gerbers from this file", 14, 244),
    ]
    schematic(
        HERE / "daughter-boards-v0.2/m6-receiver-carrier-v0.2.kicad_sch",
        "M6 receiver carrier / ten isolated channels",
        "v0.2",
        definitions,
        placed,
        wires,
        labels,
        notes,
    )


def emitter_schematic() -> None:
    specs = [
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x02"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x06"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x10"),
        ("Device", "Device.kicad_sym", "Battery"),
        ("Device", "Device.kicad_sym", "R"),
        ("Device", "Device.kicad_sym", "C"),
        ("Device", "Device.kicad_sym", "D"),
        ("power", "power.kicad_sym", "GND"),
    ]
    definitions = load_definitions(specs)
    project_uuid = uid()
    placed = [
        placed_symbol(
            "Device:Battery", definitions["Device:Battery"], "BT1",
            "PROTECTED 1S POUCH 65x30x7", "Battery:BatteryHolder_Keystone_1042_1x18650",
            38, 70, project_uuid, "emitter-power-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x02", definitions["Connector_Generic:Conn_01x02"], "J_BAT",
            "BATTERY MX1.25 LOCK 2P", "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            38, 105, project_uuid, "emitter-power-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x02", definitions["Connector_Generic:Conn_01x02"], "J_EXT",
            "EXT TX 10-30V MX1.25 2P / CURRENT GATE", "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            38, 145, project_uuid, "emitter-power-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x06", definitions["Connector_Generic:Conn_01x06"], "U_BOOST",
            "TX BOOST / CURRENT-LIMIT MODULE PLACEHOLDER", "Converter_DCDC:Converter_DCDC_SMD",
            112, 116, project_uuid, "emitter-power-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x10", definitions["Connector_Generic:Conn_01x10"], "J_TX_A",
            "TX00..TX04 2-WIRE MX1.25 10P", "Connector_JST:JST_GH_SM10B-GHS-TB_1x10-1MP_P1.25mm_Horizontal",
            195, 98, project_uuid, "emitter-power-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x10", definitions["Connector_Generic:Conn_01x10"], "J_TX_B",
            "TX05..TX09 2-WIRE MX1.25 10P", "Connector_JST:JST_GH_SM10B-GHS-TB_1x10-1MP_P1.25mm_Horizontal",
            195, 136, project_uuid, "emitter-power-v0.2",
        ),
        placed_symbol(
            "Device:R", definitions["Device:R"], "F_TX", "PTC / fuse review", "Fuse:Fuse_1206_3216Metric",
            78, 150, project_uuid, "emitter-power-v0.2",
        ),
        placed_symbol(
            "Device:D", definitions["Device:D"], "D_TVS", "TX rail TVS review", "Diode_SMD:D_SMA",
            100, 150, project_uuid, "emitter-power-v0.2",
        ),
    ]
    wires = [
        wire(45, 70, 100, 116),
        wire(45, 105, 100, 116),
        wire(45, 145, 78, 150),
        wire(85, 150, 100, 150),
        wire(100, 150, 112, 125),
        wire(125, 116, 180, 116),
    ]
    labels = [
        label("BAT_P / BAT_GND", 48, 70),
        label("EXT_TX_IN / EXT_TX_GND", 48, 145),
        label("TX_RAIL / TX_GND", 128, 116),
        label("TX00..TX04 / TX05..TX09", 182, 88),
    ]
    notes = [
        note("PINGPANG / EMITTER INTERNAL POWER / TEN 2-WIRE OUTPUTS", 14, 12, 1.8),
        note("Default source is the protected 1S pouch battery in the low-component end of the left clamp cavity", 14, 20),
        note("J_EXT is a serviceable screw/crimp fallback input; never parallel an unprotected cell or bypass the protection path", 14, 27),
        note("U_BOOST, fuse/TVS values and peak TX current remain first-article selection gates", 14, 220),
        note("J_TX_A and J_TX_B are two keyed 1.25 mm 10-pin sections: TX00..TX04 and TX05..TX09", 14, 227),
    ]
    schematic(
        HERE / "daughter-boards-v0.2/emitter-power-v0.2.kicad_sch",
        "Emitter internal battery and boost power daughter",
        "v0.2",
        definitions,
        placed,
        wires,
        labels,
        notes,
    )


def ui_schematic() -> None:
    specs = [
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x02"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x04"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x05"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x07"),
        ("Connector_Generic", "Connector_Generic.kicad_sym", "Conn_01x12"),
        ("Device", "Device.kicad_sym", "LED"),
        ("Device", "Device.kicad_sym", "Buzzer"),
        ("Device", "Device.kicad_sym", "Speaker"),
        ("Switch", "Switch.kicad_sym", "SW_Push"),
        ("power", "power.kicad_sym", "GND"),
        ("power", "power.kicad_sym", "+3V3"),
    ]
    definitions = load_definitions(specs)
    project_uuid = uid()
    placed = [
        placed_symbol(
            "Connector_Generic:Conn_01x12", definitions["Connector_Generic:Conn_01x12"], "J_MOTHER",
            "MOTHER UI MX1.25 LOCK 12P", "Connector_JST:JST_GH_SM12B-GHS-TB_1x12-1MP_P1.25mm_Horizontal",
            34, 75, project_uuid, "ui-panel-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x04", definitions["Connector_Generic:Conn_01x04"], "J_OLED",
            "OLED I2C RESERVE MX1.25 4P", "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal",
            110, 55, project_uuid, "ui-panel-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x05", definitions["Connector_Generic:Conn_01x05"], "J_SPK",
            "I2S SPEAKER MX1.25 LOCK 5P", "Connector_JST:JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal",
            110, 100, project_uuid, "ui-panel-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x02", definitions["Connector_Generic:Conn_01x02"], "J_BUZ",
            "BUZZER MX1.25 LOCK 2P", "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal",
            110, 145, project_uuid, "ui-panel-v0.2",
        ),
        placed_symbol(
            "Switch:SW_Push", definitions["Switch:SW_Push"], "SW_START",
            "SEALED START BUTTON", "Button_Switch_SMD:SW_SPST_TL3301N160QG",
            176, 65, project_uuid, "ui-panel-v0.2",
        ),
        placed_symbol(
            "Switch:SW_Push", definitions["Switch:SW_Push"], "SW_MODE",
            "SEALED MODE BUTTON", "Button_Switch_SMD:SW_SPST_TL3301N160QG",
            176, 105, project_uuid, "ui-panel-v0.2",
        ),
        placed_symbol(
            "Device:LED", definitions["Device:LED"], "D_STATUS",
            "STATUS LIGHT PIPE", "LED_SMD:LED_0603_1608Metric",
            176, 145, project_uuid, "ui-panel-v0.2",
        ),
        placed_symbol(
            "Device:LED", definitions["Device:LED"], "D_BAT",
            "BATTERY LIGHT PIPE", "LED_SMD:LED_0603_1608Metric",
            176, 165, project_uuid, "ui-panel-v0.2",
        ),
        placed_symbol(
            "Connector_Generic:Conn_01x07", definitions["Connector_Generic:Conn_01x07"], "J_USB_PANEL",
            "USB-C BULKHEAD MX1.25 7P / SILICONE CAP", "Connector_JST:JST_GH_SM07B-GHS-TB_1x07-1MP_P1.25mm_Horizontal",
            245, 110, project_uuid, "ui-panel-v0.2",
        ),
    ]
    wires = [
        wire(49, 75, 92, 55),
        wire(49, 75, 92, 100),
        wire(49, 75, 92, 145),
        wire(128, 55, 165, 65),
        wire(128, 100, 165, 105),
        wire(128, 145, 165, 145),
        wire(187, 145, 230, 110),
    ]
    labels = [
        label("I2C OLED / SDA / SCL", 80, 47),
        label("I2S BCLK / WS / DOUT", 80, 92),
        label("BUZZER", 80, 137),
        label("START / MODE", 164, 47),
        label("STATUS / BATTERY LED", 164, 137),
        label("USB VBUS / D+ / D- / CC1 / CC2", 214, 101),
    ]
    notes = [
        note("PINGPANG / SEALED UI PANEL / OLED + BUTTONS + AUDIO + USB-C", 14, 12, 1.8),
        note("The 12-pin mother-board cable carries power, I2C, two buttons, buzzer, I2S speaker and two status LEDs", 14, 20),
        note("Faceplate has a display window, two button bores, two light pipes, acoustic membrane opening and capped USB-C slot", 14, 27),
        note("Use a panel bulkhead/short harness so the sealed cover has no raw board-edge connector exposed", 14, 215),
    ]
    schematic(
        HERE / "daughter-boards-v0.2/ui-panel-v0.2.kicad_sch",
        "Sealed UI daughter / OLED, buttons, audio and USB-C",
        "v0.2",
        definitions,
        placed,
        wires,
        labels,
        notes,
    )


def main() -> int:
    receiver_schematic()
    emitter_schematic()
    ui_schematic()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
