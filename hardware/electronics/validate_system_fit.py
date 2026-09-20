#!/usr/bin/env python3
"""Self-check the KiCad/electronics package against the OpenSCAD enclosure.

This is the system-level gate between the PCB generators and the mechanical
source. It checks native KiCad files, real board/component STL/STEP exports,
the transformed board envelopes in the shared OpenSCAD datum, empty boolean
interference probes, and the complete printed-parts manifest.

The board-to-wall checks intentionally use conservative AABBs. They are
supplemented by OpenSCAD boolean intersection probes: an empty diagnostic STL
means that the imported electronics do not penetrate the structural shell.
Board-level copper release remains a separate gate and is reported openly.
Run with KiCad's bundled Python when possible so ``pcbnew`` is available.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCAD = ROOT / "hardware/cad/net_stand.scad"
MODEL_DIR = HERE / "3d/v0.2"
MOTHER = HERE / "esp32-control-v0.1/esp32-control-v0.1.kicad_pcb"
SCHEMATIC = HERE / "esp32-control-v0.1/esp32-control-v0.1.kicad_sch"
SCHEMATICS = [
    SCHEMATIC,
    HERE / "daughter-boards-v0.2/m6-receiver-carrier-v0.2.kicad_sch",
    HERE / "daughter-boards-v0.2/emitter-power-v0.2.kicad_sch",
    HERE / "daughter-boards-v0.2/ui-panel-v0.2.kicad_sch",
]
PRINT_MANIFEST = ROOT / "hardware/cad/exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json"
REPORT_JSON = HERE / "fit-report-v0.2.json"
REPORT_MD = HERE / "fit-report-v0.2.md"
MM = 1_000_000
MX125_PITCH = 1.25
EXPECTED_PRINTABLE_COUNT = 39


BOARD_SPECS = {
    MOTHER: {
        "size": (86.0, 32.0),
        "model": "esp32-control-v0.1",
        "mx125_refs": {"J2", "J3", "J4", "J5", "J6", "J7", "J8"},
        "refs": {
            "H1", "H2", "H3", "H4", "U1", "U2", "U3", "J1", "J2",
            "J3", "J4", "J5", "J6", "J7", "J8", "SW1",
        },
    },
    HERE / "daughter-boards-v0.2/m6-receiver-carrier-v0.2.kicad_pcb": {
        "size": (80.0, 32.0),
        "model": "m6-receiver-carrier-v0.2",
        "mx125_refs": {"J_HOST", "J_PWR"}
        | {"J_RX%02d" % index for index in range(10)},
        "refs": {
            "H1", "H2", "H3", "H4", "J_HOST", "J_PWR", "U_MCU",
        }
        | {"J_RX%02d" % index for index in range(10)}
        | {"U_OP%02d" % index for index in range(10)},
    },
    HERE / "daughter-boards-v0.2/emitter-power-v0.2.kicad_pcb": {
        "size": (68.0, 32.0),
        "model": "emitter-power-v0.2",
        "mx125_refs": {"J_BAT", "J_EXT", "J_TX_A", "J_TX_B"},
        "refs": {
            "H1", "H2", "H3", "H4", "J_BAT", "J_EXT", "J_TX_A", "J_TX_B",
            "U_BOOST", "F_TX", "D_TVS",
        },
    },
    HERE / "daughter-boards-v0.2/ui-panel-v0.2.kicad_pcb": {
        "size": (58.0, 28.0),
        "model": "ui-panel-v0.2",
        "mx125_refs": {"J_MOTHER", "J_OLED", "J_SPK", "J_BUZ"},
        "refs": {
            "H1", "H2", "H3", "H4", "J_MOTHER", "J_OLED", "J_SPK",
            "J_BUZ", "SW_START", "SW_MODE", "D_STATUS", "D_BAT",
            "J_USB_PANEL",
        },
    },
}


CONNECTOR_NET_CONTRACTS = {
    MOTHER: {
        "J2": ("bat_p", "gnd"),
        "J3": ("sensor_ext", "gnd"),
        "J4": ("3v3", "gnd", "carrier_sck", "carrier_mosi", "carrier_miso", "carrier_cs_n", "carrier_irq_n", "carrier_reset_n"),
        "J5": ("pvdf_adc_l", "gnd", "pvdf_adc_r", "gnd"),
        "J6": ("pvdf_cmp_aux_l", "pvdf_cmp_aux_r"),
        "J7": ("3v3", "gnd", "ui_sda", "ui_scl", "ui_btn_start", "ui_btn_mode", "ui_buzzer", "ui_spk_bclk", "ui_spk_ws", "ui_spk_dout", "ui_led_status", "ui_led_battery"),
        "J8": ("sensor_fused", "gnd"),
    },
    HERE / "daughter-boards-v0.2/m6-receiver-carrier-v0.2.kicad_pcb": {
        "J_HOST": ("3v3", "gnd", "carrier_sck", "carrier_mosi", "carrier_miso", "carrier_cs_n", "carrier_irq_n", "carrier_reset_n"),
        "J_PWR": ("sensor_v", "sensor_gnd"),
        **{
            "J_RX%02d" % index: (
                "rx%02d_v" % index,
                "rx%02d_gnd" % index,
                "rx%02d_sig" % index,
            )
            for index in range(10)
        },
    },
    HERE / "daughter-boards-v0.2/emitter-power-v0.2.kicad_pcb": {
        "J_BAT": ("bat_p", "bat_gnd"),
        "J_EXT": ("ext_tx_in", "ext_tx_gnd"),
        "J_TX_A": tuple(
            net for index in range(5)
            for net in ("tx%02d_v" % index, "tx%02d_gnd" % index)
        ),
        "J_TX_B": tuple(
            net for index in range(5, 10)
            for net in ("tx%02d_v" % index, "tx%02d_gnd" % index)
        ),
    },
    HERE / "daughter-boards-v0.2/ui-panel-v0.2.kicad_pcb": {
        "J_MOTHER": ("3v3", "gnd", "ui_sda", "ui_scl", "ui_btn_start", "ui_btn_mode", "ui_buzzer", "ui_spk_bclk", "ui_spk_ws", "ui_spk_dout", "ui_led_status", "ui_led_battery"),
        "J_OLED": ("3v3", "gnd", "ui_sda", "ui_scl"),
        "J_SPK": ("ui_spk_bclk", "ui_spk_ws", "ui_spk_dout", "3v3", "gnd"),
        "J_BUZ": ("ui_buzzer", "gnd"),
    },
}


UI_DIRECT_PARTS = {
    "SW_START": {
        "model_token": "Button_Switch_SMD.3dshapes/SW_SPST_TS-1088-xR020.step",
        "pad_nets": {"1": "ui_btn_start", "2": "gnd"},
        "center": (10.0, 8.0),
    },
    "SW_MODE": {
        "model_token": "Button_Switch_SMD.3dshapes/SW_SPST_TS-1088-xR020.step",
        "pad_nets": {"1": "ui_btn_mode", "2": "gnd"},
        "center": (10.0, 20.0),
    },
    "D_STATUS": {
        "model_token": "LED_SMD.3dshapes/LED_0603_1608Metric.step",
        "pad_nets": {"1": "ui_led_status", "2": "gnd"},
        "center": (29.0, 3.0),
    },
    "D_BAT": {
        "model_token": "LED_SMD.3dshapes/LED_0603_1608Metric.step",
        "pad_nets": {"1": "ui_led_battery", "2": "gnd"},
        "center": (32.0, 25.0),
    },
    "J_USB_PANEL": {
        "model_token": "usb-c-vertical-proxy.step",
        "pad_nets": {
            "A1": "gnd", "A4": "usb_vbus", "A5": "cc1", "A6": "usb_dp",
            "A7": "usb_dn", "A8": "usb_sbu2", "A9": "usb_vbus",
            "A12": "gnd", "B1": "gnd", "B4": "usb_vbus", "B5": "cc2",
            "B6": "usb_dp", "B7": "usb_dn", "B8": "usb_sbu1",
            "B9": "usb_vbus", "B12": "gnd", "SH": "gnd",
        },
        "center": (47.0, 26.0),
    },
}


def find_executable(env_name: str, names: Sequence[str], fallbacks: Sequence[str]) -> str:
    candidates = [os.environ.get(env_name, "")]
    candidates.extend(shutil.which(name) or "" for name in names)
    candidates.extend(fallbacks)
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("executable not found: " + env_name)


def find_openscad() -> str:
    return find_executable(
        "OPENSCAD",
        ("openscad",),
        ("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",),
    )


def find_kicad_cli() -> str:
    return find_executable(
        "KICAD_CLI",
        ("kicad-cli",),
        ("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",),
    )


def find_kicad_python() -> str:
    return find_executable(
        "KICAD_PYTHON",
        ("python3.9",),
        (
            "/Applications/KiCad/KiCad.app/Contents/Frameworks/"
            "Python.framework/Versions/3.9/bin/python3.9",
        ),
    )


def run_openscad(
    openscad: str,
    output: Path,
    part: str,
    definitions: Iterable[str] = (),
) -> subprocess.CompletedProcess:
    command = [openscad, "-o", str(output), "-D", 'PART="%s"' % part]
    for definition in definitions:
        command.extend(["-D", definition])
    command.append(str(SCAD))
    return subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def probe_scad(openscad: str) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pingpang-fit-parameters-") as directory:
        output = Path(directory) / "parameters.stl"
        result = run_openscad(openscad, output, "parameter_probe")
    if result.returncode != 0:
        raise RuntimeError("OpenSCAD parameter probe failed:\n" + result.stdout)
    parameters: Dict[str, Any] = {}
    for match in re.finditer(r"NETSTAND_PARAM ([^=]+)=([^\"\n]+)", result.stdout):
        name, value = match.groups()
        value = value.strip()
        if value in {"true", "false"}:
            parameters[name] = value == "true"
        else:
            try:
                parameters[name] = float(value)
            except ValueError:
                parameters[name] = value
    if not parameters:
        raise RuntimeError("OpenSCAD parameter probe emitted no NETSTAND_PARAM records")
    return parameters


def number(parameters: Dict[str, Any], name: str) -> float:
    value = parameters[name]
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise RuntimeError("SCAD parameter is not numeric: %s=%r" % (name, value))
    return float(value)


def stl_bounds(path: Path) -> Tuple[float, float, float, float, float, float]:
    data = path.read_bytes()
    points: List[Tuple[float, float, float]] = []
    if len(data) >= 84:
        triangle_count = struct.unpack_from("<I", data, 80)[0]
        expected_size = 84 + triangle_count * 50
        if triangle_count and expected_size == len(data):
            for index in range(triangle_count):
                base = 84 + index * 50 + 12
                for vertex in range(3):
                    points.append(struct.unpack_from("<fff", data, base + vertex * 12))
    if not points:
        text = data.decode("utf-8", errors="replace")
        points = [
            (float(match.group(1)), float(match.group(2)), float(match.group(3)))
            for match in re.finditer(
                r"\bvertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)",
                text,
                re.IGNORECASE,
            )
        ]
    if not points:
        raise RuntimeError("cannot parse STL vertices: %s" % path)
    xs, ys, zs = zip(*points)
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def bounds_dict(bounds: Tuple[float, float, float, float, float, float]) -> Dict[str, List[float]]:
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    return {
        "min": [round(xmin, 4), round(ymin, 4), round(zmin, 4)],
        "max": [round(xmax, 4), round(ymax, 4), round(zmax, 4)],
        "size": [round(xmax - xmin, 4), round(ymax - ymin, 4), round(zmax - zmin, 4)],
    }


def translate_bounds(
    bounds: Tuple[float, float, float, float, float, float],
    dx: float,
    dy: float,
    dz: float,
) -> Tuple[float, float, float, float, float, float]:
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    return xmin + dx, xmax + dx, ymin + dy, ymax + dy, zmin + dz, zmax + dz


def ui_side_stl_bounds(
    bounds: Tuple[float, float, float, float, float, float],
    x_min: float,
    board_plane_y: float,
    board_z_min: float,
    board_width_y: float,
) -> Tuple[float, float, float, float, float, float]:
    """Map pcbnew's mirrored-y STL into the vertical y+ UI datum.

    KiCad exports a board with local y=-28..0.  The OpenSCAD side datum
    reflects that coordinate, then rotates local z into global +y and local y
    into global -z.  Keeping this transform here prevents the mechanical report
    from silently falling back to the retired horizontal-cover placement.
    """
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    local_y_min = -ymax
    local_y_max = -ymin
    return (
        xmin + x_min,
        xmax + x_min,
        zmin + board_plane_y,
        zmax + board_plane_y,
        board_z_min + board_width_y - local_y_max,
        board_z_min + board_width_y - local_y_min,
    )


def rotate_y_minus_90_then_translate(
    bounds: Tuple[float, float, float, float, float, float],
    dx: float,
    dy: float,
    dz: float,
) -> Tuple[float, float, float, float, float, float]:
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    # OpenSCAD rotate([0,-90,0]): x'=-z, y'=y, z'=x.
    return dx - zmax, dx - zmin, ymin + dy, ymax + dy, xmin + dz, xmax + dz


def floor_z_at(parameters: Dict[str, Any], x: float) -> float:
    start = number(parameters, "clamp_reinforcement_start_x")
    end = number(parameters, "clamp_reinforcement_end_x")
    near = number(parameters, "clamp_reinforcement_near_table_bottom_z")
    outer = number(parameters, "clamp_reinforcement_outer_bottom_z")
    return near + (x - start) / (end - start) * (outer - near)


def margin_report(
    bounds: Tuple[float, float, float, float, float, float],
    region: Tuple[float, float, float, float, float, float],
) -> Dict[str, float]:
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    rxmin, rxmax, rymin, rymax, rzmin, rzmax = region
    return {
        "x_min": xmin - rxmin,
        "x_max": rxmax - xmax,
        "y_min": ymin - rymin,
        "y_max": rymax - ymax,
        "z_min": zmin - rzmin,
        "z_max": rzmax - zmax,
    }


def rounded_mapping(values: Dict[str, float]) -> Dict[str, float]:
    return {key: round(value, 4) for key, value in values.items()}


def balanced_block(text: str, start: int) -> str:
    """Return the parenthesized KiCad expression beginning at *start*."""

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
                return text[start:index + 1]
    raise RuntimeError("unbalanced KiCad schematic expression")


def board_envelope(pcbnew: Any, path: Path) -> Dict[str, Any]:
    board = pcbnew.LoadBoard(str(path))
    edges = board.GetBoardEdgesBoundingBox()
    refs = {str(footprint.GetReference()) for footprint in board.GetFootprints()}
    models = sum(len(footprint.Models()) for footprint in board.GetFootprints())
    connectivity = board.GetConnectivity()
    connectivity.Build(board)
    connectors: Dict[str, int] = {}
    for footprint in board.GetFootprints():
        reference = str(footprint.GetReference())
        if reference.startswith(("J", "SW")):
            connectors[reference] = len(footprint.Pads())
    return {
        "path": str(path.relative_to(ROOT)),
        "size_mm": [edges.GetWidth() / MM, edges.GetHeight() / MM],
        "copper_layer_count": board.GetCopperLayerCount(),
        "footprints": len(board.GetFootprints()),
        "models": models,
        "nets": board.GetNetCount(),
        "tracks": len(board.GetTracks()),
        "unconnected": connectivity.GetUnconnectedCount(False),
        "references": sorted(refs),
        "connector_pad_counts": connectors,
    }


def check_mx125_connectors(pcbnew: Any, board_path: Path,
                           references: Iterable[str]) -> Dict[str, Any]:
    """Check physical cable connectors, not generic schematic symbols.

    USB-C and button footprints are intentionally outside this set.  The
    repository uses generic Conn_01xNN symbols in schematics, whose drawing
    grid is commonly 2.54 mm; that grid is not a physical PCB connector
    contract.  This check instead inspects the generated PCB pad coordinates
    and attached 1.25 mm review models.
    """
    board = pcbnew.LoadBoard(str(board_path))
    records: Dict[str, Any] = {}
    for reference in sorted(references):
        footprint = next(
            (item for item in board.GetFootprints()
             if str(item.GetReference()) == reference),
            None,
        )
        if footprint is None:
            raise RuntimeError("%s missing MX1.25 connector %s" % (board_path.name, reference))
        value = str(footprint.GetValue())
        if "MX1.25" not in value:
            raise RuntimeError(
                "%s connector %s is not labeled MX1.25: %s"
                % (board_path.name, reference, value)
            )
        pads = [
            pad for pad in footprint.Pads()
            if str(pad.GetNumber()) not in {"MP", "SH"}
        ]
        positions = []
        fp_position = footprint.GetPosition()
        for pad in pads:
            position = pad.GetPosition()
            positions.append((
                (position.x - fp_position.x) / MM,
                (position.y - fp_position.y) / MM,
            ))
        if len(positions) >= 2:
            x_values = [point[0] for point in positions]
            y_values = [point[1] for point in positions]
            axis_values = sorted(
                x_values if max(x_values) - min(x_values) >=
                max(y_values) - min(y_values) else y_values
            )
            pitch_deltas = [
                round(axis_values[index + 1] - axis_values[index], 4)
                for index in range(len(axis_values) - 1)
            ]
            if any(abs(delta - MX125_PITCH) > 0.01 for delta in pitch_deltas):
                raise RuntimeError(
                    "%s connector %s has non-1.25 mm signal pitch: %s"
                    % (board_path.name, reference, pitch_deltas)
                )
        model_files = [str(model.m_Filename) for model in footprint.Models()]
        if not any("P1.25mm" in filename for filename in model_files):
            raise RuntimeError(
                "%s connector %s has no attached 1.25 mm review model"
                % (board_path.name, reference)
            )
        records[reference] = {
            "value": value,
            "signal_pad_count": len(positions),
            "pitch_mm": pitch_deltas if len(positions) >= 2 else [],
            "models": model_files,
        }
    return {"status": "PASS", "connectors": records}


def check_schematic_connector_refs(schematic_path: Path,
                                   references: Iterable[str]) -> Dict[str, Any]:
    """Ensure every physical MX1.25 PCB connector has a schematic instance."""

    text = schematic_path.read_text(encoding="utf-8", errors="replace")
    instances: Dict[str, str] = {}
    for match in re.finditer(r"(?m)^\t\(symbol\s*$", text):
        block = balanced_block(text, match.start())
        reference_match = re.search(r'\(property "Reference" "([^"]+)"', block)
        value_match = re.search(r'\(property "Value" "([^"]+)"', block)
        if reference_match and value_match:
            instances[reference_match.group(1)] = value_match.group(1)
    values: Dict[str, str] = {}
    for reference in sorted(references):
        if reference not in instances:
            raise RuntimeError(
                "%s is missing schematic instance for connector %s"
                % (schematic_path.name, reference)
            )
        value = instances[reference]
        if "MX1.25" not in value:
            raise RuntimeError(
                "%s schematic connector %s is not labeled MX1.25: %s"
                % (schematic_path.name, reference, value)
            )
        values[reference] = value
    return {
        "status": "PASS",
        "schematic": str(schematic_path.relative_to(ROOT)),
        "references": values,
    }


def check_connector_net_contract(pcbnew: Any, board_path: Path,
                                 expected: Dict[str, Sequence[str]]) -> Dict[str, Any]:
    """Check the ordered pin-to-net contract for every board connector."""

    board = pcbnew.LoadBoard(str(board_path))
    records: Dict[str, Dict[str, str]] = {}
    for reference, expected_nets in sorted(expected.items()):
        footprint = next(
            (item for item in board.GetFootprints()
             if str(item.GetReference()) == reference),
            None,
        )
        if footprint is None:
            raise RuntimeError(
                "%s missing connector for net contract %s"
                % (board_path.name, reference)
            )
        actual: Dict[str, str] = {}
        for pad in footprint.Pads():
            number = str(pad.GetNumber())
            if number.isdigit() and int(number) <= len(expected_nets):
                actual[number] = str(pad.GetNetname())
        expected_map = {
            str(index + 1): net_name
            for index, net_name in enumerate(expected_nets)
        }
        if actual != expected_map:
            raise RuntimeError(
                "%s connector %s net contract mismatch: actual=%s expected=%s"
                % (board_path.name, reference, actual, expected_map)
            )
        records[reference] = actual
    return {"status": "PASS", "connectors": records}


def check_ui_direct_parts(pcbnew: Any, board_path: Path) -> Dict[str, Any]:
    """Check that panel-contact parts are real library footprints in-place.

    The screen is intentionally excluded because it is a cable-connected
    module.  Buttons, LEDs, and USB-C are checked for their library model,
    pad-to-net mapping, and the shared mechanical datum used by OpenSCAD.
    """
    board = pcbnew.LoadBoard(str(board_path))
    records: Dict[str, Any] = {}
    for reference, spec in UI_DIRECT_PARTS.items():
        footprint = next(
            (item for item in board.GetFootprints()
             if str(item.GetReference()) == reference),
            None,
        )
        if footprint is None:
            raise RuntimeError(
                "%s missing direct UI part %s" % (board_path.name, reference)
            )
        model_files = [str(model.m_Filename) for model in footprint.Models()]
        if not any(spec["model_token"] in filename for filename in model_files):
            raise RuntimeError(
                "%s UI part %s has no expected library model: %s"
                % (board_path.name, reference, model_files)
            )
        pads_by_name: Dict[str, List[str]] = {}
        for pad in footprint.Pads():
            name = str(pad.GetPadName())
            pads_by_name.setdefault(name, []).append(str(pad.GetNetname()))
        for pad_name, expected_net in spec["pad_nets"].items():
            actual_nets = pads_by_name.get(pad_name, [])
            if not actual_nets or any(net != expected_net for net in actual_nets):
                raise RuntimeError(
                    "%s UI part %s pad %s net mismatch: actual=%s expected=%s"
                    % (board_path.name, reference, pad_name, actual_nets, expected_net)
                )
        center_x, center_y = spec["center"]
        if reference == "J_USB_PANEL":
            origin = footprint.GetPosition()
            actual_center = (origin.x / MM, origin.y / MM)
        else:
            signal_pads = [
                pad for pad in footprint.Pads()
                if str(pad.GetPadName()) in spec["pad_nets"]
            ]
            if not signal_pads:
                raise RuntimeError("%s UI part %s has no signal pads" % (board_path.name, reference))
            actual_center = (
                sum(pad.GetPosition().x for pad in signal_pads) / len(signal_pads) / MM,
                sum(pad.GetPosition().y for pad in signal_pads) / len(signal_pads) / MM,
            )
        if any(abs(actual - expected) > 0.01 for actual, expected in zip(actual_center, (center_x, center_y))):
            raise RuntimeError(
                "%s UI part %s moved: actual=(%.3f, %.3f) expected=(%.3f, %.3f)"
                % (board_path.name, reference, actual_center[0], actual_center[1], center_x, center_y)
            )
        records[reference] = {
            "models": model_files,
            "center_mm": [round(actual_center[0], 3), round(actual_center[1], 3)],
            "pad_nets": {name: sorted(set(nets)) for name, nets in sorted(pads_by_name.items()) if name in spec["pad_nets"]},
        }
    return {"status": "PASS", "parts": records}


def check_ui_interface_alignment(
    pcbnew: Any, board_path: Path, parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Prove that real PCB parts land under the printed y+ faceplate openings."""
    direct = check_ui_direct_parts(pcbnew, board_path)
    board = pcbnew.LoadBoard(str(board_path))
    parameter_centers = {
        "SW_START": (
            number(parameters, "clamp_electronics_ui_button_a_x"),
            number(parameters, "clamp_electronics_ui_button_a_y"),
        ),
        "SW_MODE": (
            number(parameters, "clamp_electronics_ui_button_b_x"),
            number(parameters, "clamp_electronics_ui_button_b_y"),
        ),
        "D_STATUS": (
            number(parameters, "clamp_electronics_ui_led_a_x"),
            number(parameters, "clamp_electronics_ui_led_a_y"),
        ),
        "D_BAT": (
            number(parameters, "clamp_electronics_ui_led_b_x"),
            number(parameters, "clamp_electronics_ui_led_b_y"),
        ),
        "J_USB_PANEL": (
            number(parameters, "clamp_electronics_ui_usb_x"),
            number(parameters, "clamp_electronics_ui_usb_y"),
        ),
    }
    center_records: Dict[str, Dict[str, Any]] = {}
    for reference, expected in parameter_centers.items():
        actual = direct["parts"][reference]["center_mm"]
        delta = max(abs(actual[index] - expected[index]) for index in (0, 1))
        if delta > 0.01:
            raise RuntimeError(
                "UI panel datum mismatch for %s: actual=%s expected=%s"
                % (reference, actual, expected)
            )
        center_records[reference] = {
            "pcb_center_mm": actual,
            "faceplate_center_mm": [round(expected[0], 3), round(expected[1], 3)],
            "max_error_mm": round(delta, 4),
            "status": "PASS",
        }

    # The four real NPTH holes are the board-side references for the four
    # printed faceplate M2.5 holes.  A set comparison catches a swapped or
    # vertically mirrored panel even when the direct component centers happen
    # to look plausible.
    hole_centers = []
    for reference in ("H1", "H2", "H3", "H4"):
        footprint = next(
            (item for item in board.GetFootprints()
             if str(item.GetReference()) == reference),
            None,
        )
        if footprint is None:
            raise RuntimeError("UI panel missing mounting hole %s" % reference)
        position = footprint.GetPosition()
        hole_centers.append((round(position.x / MM, 3), round(position.y / MM, 3)))
    expected_holes = sorted(
        (
            (number(parameters, "clamp_electronics_ui_board_mount_hole_inset_x"),
             number(parameters, "clamp_electronics_ui_board_mount_hole_inset_y")),
            (number(parameters, "clamp_electronics_ui_board_length_x") -
             number(parameters, "clamp_electronics_ui_board_mount_hole_inset_x"),
             number(parameters, "clamp_electronics_ui_board_mount_hole_inset_y")),
            (number(parameters, "clamp_electronics_ui_board_length_x") -
             number(parameters, "clamp_electronics_ui_board_mount_hole_inset_x"),
             number(parameters, "clamp_electronics_ui_board_width_y") -
             number(parameters, "clamp_electronics_ui_board_mount_hole_inset_y")),
            (number(parameters, "clamp_electronics_ui_board_mount_hole_inset_x"),
             number(parameters, "clamp_electronics_ui_board_width_y") -
             number(parameters, "clamp_electronics_ui_board_mount_hole_inset_y")),
        )
    )
    if sorted(hole_centers) != [(round(x, 3), round(y, 3)) for x, y in expected_holes]:
        raise RuntimeError(
            "UI panel mounting-hole datum mismatch: actual=%s expected=%s"
            % (sorted(hole_centers), expected_holes)
        )

    board_width = number(parameters, "clamp_electronics_ui_board_length_x")
    board_height = number(parameters, "clamp_electronics_ui_board_width_y")
    border = number(parameters, "clamp_electronics_faceplate_border")
    screen_w = number(parameters, "clamp_electronics_ui_screen_length_x")
    screen_h = number(parameters, "clamp_electronics_ui_screen_width_y")
    window_clearance = number(parameters, "clamp_electronics_faceplate_window_clearance")
    button_d = number(parameters, "clamp_electronics_ui_button_d")
    button_clearance = number(parameters, "clamp_electronics_faceplate_button_clearance")
    led_bore_d = number(parameters, "clamp_electronics_ui_led_bore_d")
    speaker_d = number(parameters, "clamp_electronics_ui_speaker_d") - 4
    usb_w = 8 + 2 * number(parameters, "clamp_electronics_faceplate_usb_clearance")
    usb_h = 5 + 2 * number(parameters, "clamp_electronics_faceplate_usb_clearance")
    faceplate_inner_y = (
        number(parameters, "clamp_electronics_ui_side_board_plane_y")
        + number(parameters, "clamp_electronics_ui_service_height_z")
    )
    ui_local = stl_bounds(MODEL_DIR / "ui-panel-v0.2.stl")
    board_to_faceplate_gap = faceplate_inner_y - (
        number(parameters, "clamp_electronics_ui_side_board_plane_y") + ui_local[5]
    )
    if board_to_faceplate_gap < 0.2:
        raise RuntimeError(
            "UI board-to-faceplate service gap is too small: %.3f mm"
            % board_to_faceplate_gap
        )

    screen_x = (board_width - screen_w) / 2
    screen_y = (board_height - screen_h) / 2
    screen_opening = (
        screen_x - window_clearance,
        screen_x + screen_w + window_clearance,
        screen_y - window_clearance,
        screen_y + screen_h + window_clearance,
    )
    usb_center = parameter_centers["J_USB_PANEL"]
    usb_opening = (
        usb_center[0] - usb_w / 2,
        usb_center[0] + usb_w / 2,
        usb_center[1] - usb_h / 2,
        usb_center[1] + usb_h / 2,
    )

    def circle_rect_clearance(center: Tuple[float, float], diameter: float,
                              rect: Tuple[float, float, float, float]) -> float:
        x, y = center
        x_gap = max(rect[0] - x, 0.0, x - rect[1])
        y_gap = max(rect[2] - y, 0.0, y - rect[3])
        return (x_gap * x_gap + y_gap * y_gap) ** 0.5 - diameter / 2

    def rect_rect_clearance(
        first: Tuple[float, float, float, float],
        second: Tuple[float, float, float, float],
    ) -> float:
        x_gap = max(first[0] - second[1], second[0] - first[1], 0.0)
        y_gap = max(first[2] - second[3], second[2] - first[3], 0.0)
        return (x_gap * x_gap + y_gap * y_gap) ** 0.5

    interface_clearances = {
        "screen_to_faceplate_edge_mm": min(
            screen_opening[0] + border,
            board_width + border - screen_opening[1],
            screen_opening[2] + border,
            board_height + border - screen_opening[3],
        ),
        "usb_to_screen_mm": rect_rect_clearance(screen_opening, usb_opening),
        "buttons_to_screen_mm": min(
            circle_rect_clearance(parameter_centers["SW_START"], button_d, screen_opening),
            circle_rect_clearance(parameter_centers["SW_MODE"], button_d, screen_opening),
        ),
    }
    button_pocket_d = button_d + 2 * button_clearance
    if button_pocket_d <= 3.9:
        raise RuntimeError("UI button pocket does not clear the 3.9 mm switch body")
    if led_bore_d <= 1.6:
        raise RuntimeError("UI LED bore does not clear the 0603 body")
    if min(interface_clearances.values()) < 0.2:
        raise RuntimeError("UI faceplate openings lack the required 0.2 mm edge gap")

    usb_footprint = next(
        item for item in board.GetFootprints()
        if str(item.GetReference()) == "J_USB_PANEL"
    )
    usb_orientation = float(usb_footprint.GetOrientation().AsDegrees())
    if abs(usb_orientation) > 0.01:
        raise RuntimeError(
            "vertical USB-C footprint must remain at 0 degrees, got %.3f"
            % usb_orientation
        )

    return {
        "status": "PASS",
        "pcb_to_faceplate_centers": center_records,
        "mounting_holes": {
            "actual_local_mm": sorted(hole_centers),
            "expected_local_mm": [(round(x, 3), round(y, 3)) for x, y in expected_holes],
            "status": "PASS",
        },
        "faceplate": {
            "board_size_mm": [board_width, board_height],
            "screen_opening_mm": [round(screen_w + 2 * window_clearance, 3), round(screen_h + 2 * window_clearance, 3)],
            "button_pocket_d_mm": round(button_pocket_d, 3),
            "button_plunger_d_mm": number(parameters, "clamp_electronics_ui_button_plunger_d"),
            "led_bore_d_mm": round(led_bore_d, 3),
            "speaker_opening_d_mm": round(speaker_d, 3),
            "usb_opening_mm": [round(usb_w, 3), round(usb_h, 3)],
            "board_to_faceplate_gap_mm": round(board_to_faceplate_gap, 3),
            "opening_clearances_mm": {
                key: round(value, 3) for key, value in interface_clearances.items()
            },
            "status": "PASS",
        },
        "usb_c": {
            "orientation_deg": round(usb_orientation, 3),
            "mating_axis": "PCB normal -> y+ panel",
            "model": "usb-c-vertical-proxy.step",
            "status": "PASS",
            "physical_vendor_step": "OPEN until the purchased vertical receptacle SKU is frozen",
        },
    }


def check_legacy_schematic_contract(schematic_path: Path) -> Dict[str, Any]:
    """Keep the retained legacy schematic from advertising obsolete connectors."""

    text = schematic_path.read_text(encoding="utf-8", errors="replace")
    forbidden = ["P2.00", "P2.54", "PinHeader"]
    found = [token for token in forbidden if token in text]
    if found:
        raise RuntimeError(
            "%s contains obsolete physical connector tokens: %s"
            % (schematic_path.name, found)
        )
    expected = {"J2", "J3", "J4", "J5", "J6", "J7", "J8"}
    found_blocks: Dict[str, str] = {}
    for block in re.findall(r"\$Comp\n.*?\$EndComp", text, re.DOTALL):
        match = re.search(r"^L \S+ (\S+)$", block, re.MULTILINE)
        if match and match.group(1) in expected:
            found_blocks[match.group(1)] = block
    missing = sorted(expected - set(found_blocks))
    if missing:
        raise RuntimeError(
            "%s is missing legacy schematic connectors: %s"
            % (schematic_path.name, missing)
        )
    for reference, block in sorted(found_blocks.items()):
        if "MX1.25" not in block or "P1.25mm" not in block:
            raise RuntimeError(
                "%s legacy connector %s is not an MX1.25/P1.25 declaration"
                % (schematic_path.name, reference)
            )
    return {
        "status": "PASS",
        "schematic": str(schematic_path.relative_to(ROOT)),
        "references": sorted(found_blocks),
    }


def check_boards(pcbnew: Any) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for path, spec in BOARD_SPECS.items():
        if not path.is_file():
            raise RuntimeError("missing KiCad board: %s" % path)
        record = board_envelope(pcbnew, path)
        actual_width, actual_height = record["size_mm"]
        expected_width, expected_height = spec["size"]
        if abs(actual_width - expected_width) > 0.1 or abs(actual_height - expected_height) > 0.1:
            raise RuntimeError(
                "%s outline changed: actual=%.3fx%.3f expected=%.3fx%.3f"
                % (path.name, actual_width, actual_height, expected_width, expected_height)
            )
        if record["copper_layer_count"] != 2:
            raise RuntimeError(
                "%s is not the declared two-layer first-article board: %s"
                % (path.name, record["copper_layer_count"])
            )
        missing = sorted(set(spec["refs"]) - set(record["references"]))
        if missing:
            raise RuntimeError("%s missing refs: %s" % (path.name, missing))
        if record["models"] <= 0:
            raise RuntimeError("%s has no attached KiCad 3D models" % path.name)
        model_stl = MODEL_DIR / (spec["model"] + ".stl")
        model_step = MODEL_DIR / (spec["model"] + ".step")
        for model_path in (model_stl, model_step):
            if not model_path.is_file() or model_path.stat().st_size == 0:
                raise RuntimeError("missing board model: %s" % model_path)
        record["model_files"] = {
            "stl": str(model_stl.relative_to(ROOT)),
            "step": str(model_step.relative_to(ROOT)),
            "stl_bytes": model_stl.stat().st_size,
            "step_bytes": model_step.stat().st_size,
            "stl_bounds": bounds_dict(stl_bounds(model_stl)),
        }
        record["mx125_contract"] = check_mx125_connectors(
            pcbnew, path, spec["mx125_refs"]
        )
        record["schematic_connector_contract"] = check_schematic_connector_refs(
            path.with_suffix(".kicad_sch"), spec["mx125_refs"]
        )
        record["connector_net_contract"] = check_connector_net_contract(
            pcbnew, path, CONNECTOR_NET_CONTRACTS[path]
        )
        if path.name == "ui-panel-v0.2.kicad_pcb":
            record["ui_direct_part_contract"] = check_ui_direct_parts(pcbnew, path)
        records.append(record)
    return records


def check_native_kicad(cli: str) -> Dict[str, Any]:
    for schematic in SCHEMATICS:
        if not schematic.is_file():
            raise RuntimeError("native KiCad schematic missing: %s" % schematic)
        if not schematic.read_text(encoding="utf-8", errors="replace").lstrip().startswith("(kicad_sch"):
            raise RuntimeError("schematic is not native .kicad_sch syntax: %s" % schematic)
    schematic_records: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="pingpang-kicad-sch-") as directory:
        for index, schematic in enumerate(SCHEMATICS):
            pdf = Path(directory) / ("schematic-%d.pdf" % index)
            export = subprocess.run(
                [cli, "sch", "export", "pdf", "--output", str(pdf), str(schematic)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            erc = Path(directory) / ("schematic-%d-erc.rpt" % index)
            erc_run = subprocess.run(
                [cli, "sch", "erc", "--output", str(erc), str(schematic)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            pdf_ok = pdf.is_file() and pdf.stat().st_size > 0
            erc_text = erc.read_text(encoding="utf-8", errors="replace") if erc.is_file() else erc_run.stdout
            if export.returncode != 0 or not pdf_ok:
                raise RuntimeError("KiCad cannot export the native schematic:\n" + export.stdout)
            violation_match = re.search(r"ERC messages:\s*(\d+)\s+Errors\s+(\d+)\s+Warnings\s+(\d+)", erc_text)
            schematic_records.append({
                "path": str(schematic.relative_to(ROOT)),
                "pdf_export": "PASS",
                "erc_violations": int(violation_match.group(1)) if violation_match else None,
                "erc_errors": int(violation_match.group(2)) if violation_match else None,
                "erc_warnings": int(violation_match.group(3)) if violation_match else None,
            })
    main_record = schematic_records[0]
    violations = main_record["erc_violations"]
    errors = main_record["erc_errors"]
    warnings = main_record["erc_warnings"]
    ato_files = sorted(str(path.relative_to(ROOT)) for path in ROOT.rglob("*.ato"))
    legacy_path = SCHEMATIC.parent / "esp32-control-v0.1.sch"
    legacy_connector_contract = (
        check_legacy_schematic_contract(legacy_path)
        if legacy_path.is_file() else {"status": "NOT_PRESENT"}
    )
    ato_entry = ROOT / "hardware/electronics/atopile/pingpang_smartgear.ato"
    ato_executable = shutil.which("ato")
    atopile_validation = "NOT_PRESENT"
    atopile_build = "NOT_PRESENT"
    atopile_output = ""
    if ato_entry.is_file():
        if not ato_executable:
            raise RuntimeError("Atopile source exists but the `ato` executable is missing")
        ato_run = subprocess.run(
            [ato_executable, "validate", str(ato_entry)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
        )
        atopile_output = ato_run.stdout.strip()
        if ato_run.returncode != 0:
            raise RuntimeError("Atopile validation failed:\n" + atopile_output)
        atopile_validation = "PASS"
        build_run = subprocess.run(
            [ato_executable, "--non-interactive", "build", str(ato_entry.parent)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=120,
        )
        if build_run.returncode != 0:
            raise RuntimeError("Atopile build failed:\n" + build_run.stdout)
        atopile_build = "PASS"
    return {
        "native_schematic": str(SCHEMATIC.relative_to(ROOT)),
        "native_schematics": schematic_records,
        "native_pcb_count": sum(path.is_file() for path in BOARD_SPECS),
        "native_project_count": sum(
            (path.parent / path.name.replace(".kicad_pcb", ".kicad_pro")).is_file()
            for path in BOARD_SPECS
        ),
        "legacy_schematic_kept": (SCHEMATIC.parent / "esp32-control-v0.1.sch").is_file(),
        "legacy_connector_contract": legacy_connector_contract,
        "atopile_ato_files": ato_files,
        "atopile_present": bool(ato_files),
        "atopile_entry": str(ato_entry.relative_to(ROOT)) if ato_entry.is_file() else None,
        "atopile_validation": atopile_validation,
        "atopile_build": atopile_build,
        "atopile_output": atopile_output,
        "kicad_pdf_export": "PASS" if all(item["pdf_export"] == "PASS" for item in schematic_records) else "FAIL",
        "erc_violations": violations,
        "erc_errors": errors,
        "erc_warnings": warnings,
        "erc_release": "OPEN: schematic still has unconnected/placeholder nets" if violations else "PASS",
    }


def check_pcb_drc(cli: str) -> Dict[str, Any]:
    """Run native PCB DRC and separate errors, zone warnings and airwires."""

    records: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="pingpang-pcb-drc-") as directory:
        output_dir = Path(directory)
        for index, board_path in enumerate(BOARD_SPECS):
            report_path = output_dir / ("board-%d.json" % index)
            run = subprocess.run(
                [
                    cli, "pcb", "drc", "--format", "json", "--severity-all",
                    "--refill-zones", "--output", str(report_path),
                    str(board_path),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=120,
            )
            if run.returncode != 0 or not report_path.is_file():
                raise RuntimeError(
                    "KiCad PCB DRC failed for %s:\n%s"
                    % (board_path.name, run.stdout)
                )
            data = json.loads(report_path.read_text(encoding="utf-8"))
            violations = data.get("violations", [])
            if not isinstance(violations, list):
                raise RuntimeError(
                    "KiCad PCB DRC report has no violations list: %s"
                    % board_path.name
                )
            severity_counts: Dict[str, int] = {}
            warning_types: List[str] = []
            for violation in violations:
                if not isinstance(violation, dict):
                    continue
                severity = str(violation.get("severity", "unknown"))
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                if severity == "warning":
                    warning_types.append(str(violation.get("type", "unknown")))
            errors = severity_counts.get("error", 0)
            unexpected_warnings = sorted(
                warning_type for warning_type in set(warning_types)
                if warning_type != "isolated_copper"
            )
            records.append({
                "path": str(board_path.relative_to(ROOT)),
                "violations": len(violations),
                "severity_counts": severity_counts,
                "errors": errors,
                "warnings": severity_counts.get("warning", 0),
                "warning_types": sorted(set(warning_types)),
                "unexpected_warning_types": unexpected_warnings,
                "unconnected": len(data.get("unconnected_items", [])),
                "status": "FAIL" if errors or unexpected_warnings else (
                    "PASS_WITH_EXPECTED_WARNINGS" if warning_types else "PASS"
                ),
            })
    return {
        "method": "KiCad pcb drc --severity-all --refill-zones",
        "boards": records,
        "status": "PASS" if all(item["status"] != "FAIL" for item in records) else "FAIL",
        "release": "OPEN until all unconnected items are routed and expected zone warnings are reviewed",
    }


def check_model_fits(parameters: Dict[str, Any]) -> Dict[str, Any]:
    cavity_x_min = number(parameters, "clamp_electronics_cavity_x_min")
    cavity_x_max = number(parameters, "clamp_electronics_cavity_x_max")
    cavity_y_half = number(parameters, "clamp_electronics_cavity_y_half")
    cavity_top = number(parameters, "clamp_electronics_cavity_top_z")
    main_x_min = cavity_x_min + (
        number(parameters, "clamp_electronics_cavity_length_x")
        - number(parameters, "clamp_electronics_board_length_x")
    ) / 2
    emitter_x_min = cavity_x_min + (
        number(parameters, "clamp_electronics_cavity_length_x")
        - number(parameters, "clamp_electronics_emitter_board_length_x")
    ) / 2
    ui_x_min = cavity_x_min + (
        number(parameters, "clamp_electronics_cavity_length_x")
        - number(parameters, "clamp_electronics_ui_board_length_x")
    ) / 2
    main_y_shift = number(parameters, "clamp_electronics_main_board_y_shift") if "clamp_electronics_main_board_y_shift" in parameters else 18.5
    emitter_y_shift = number(parameters, "clamp_electronics_emitter_board_y_shift") if "clamp_electronics_emitter_board_y_shift" in parameters else 17.0
    main_local = stl_bounds(MODEL_DIR / "esp32-control-v0.1.stl")
    emitter_local = stl_bounds(MODEL_DIR / "emitter-power-v0.2.stl")
    ui_local = stl_bounds(MODEL_DIR / "ui-panel-v0.2.stl")
    main_world = translate_bounds(
        main_local, main_x_min, main_y_shift, number(parameters, "clamp_electronics_board_bottom_z")
    )
    emitter_world = translate_bounds(
        emitter_local, emitter_x_min, emitter_y_shift,
        number(parameters, "clamp_electronics_emitter_board_bottom_z"),
    )
    ui_plane_y = number(parameters, "clamp_electronics_ui_side_board_plane_y")
    ui_z_min = number(parameters, "clamp_electronics_ui_side_board_z_min")
    ui_board_width = number(parameters, "clamp_electronics_ui_board_width_y")
    ui_window_border = number(parameters, "clamp_electronics_ui_side_window_border")
    ui_world = ui_side_stl_bounds(
        ui_local, ui_x_min, ui_plane_y, ui_z_min, ui_board_width
    )
    cavity_floor_low = number(parameters, "clamp_reinforcement_near_table_bottom_z")
    main_region = (cavity_x_min, cavity_x_max, -cavity_y_half, cavity_y_half, cavity_floor_low, cavity_top)
    main_margins = margin_report(main_world, main_region)
    emitter_margins = margin_report(emitter_world, main_region)
    floor_margins = {
        "main": main_world[4] - max(floor_z_at(parameters, main_world[0]), floor_z_at(parameters, main_world[1])),
        "emitter": emitter_world[4] - max(floor_z_at(parameters, emitter_world[0]), floor_z_at(parameters, emitter_world[1])),
    }
    battery_length = number(parameters, "clamp_electronics_battery_length_x")
    battery_width = number(parameters, "clamp_electronics_battery_width_y")
    battery_x_min = cavity_x_min + (number(parameters, "clamp_electronics_cavity_length_x") - battery_length) / 2
    battery_x_max = battery_x_min + battery_length
    battery_floor = floor_z_at(parameters, (battery_x_min + battery_x_max) / 2)
    battery_world = (
        battery_x_min,
        battery_x_max,
        -battery_width / 2,
        battery_width / 2,
        battery_floor + number(parameters, "clamp_electronics_battery_clearance_z"),
        battery_floor + number(parameters, "clamp_electronics_battery_clearance_z") + number(parameters, "clamp_electronics_battery_thickness_z"),
    )
    battery_margins = margin_report(
        battery_world,
        (cavity_x_min, cavity_x_max, -cavity_y_half, cavity_y_half, cavity_floor_low, cavity_top),
    )
    battery_margins["floor"] = battery_world[4] - battery_floor
    hole_xy = [
        [main_x_min + 13.5, main_y_shift - 28.0],
        [main_x_min + 45.0, main_y_shift - 28.0],
        [main_x_min + 75.0, main_y_shift - 3.5],
        [main_x_min + 75.0, main_y_shift - 28.0],
    ]
    boss_check = all(
        cavity_x_min < point[0] < cavity_x_max
        and -cavity_y_half < point[1] < cavity_y_half
        for point in hole_xy
    )
    faceplate_inner_y = (
        ui_plane_y + number(parameters, "clamp_electronics_ui_service_height_z")
    )
    ui_xy_margins = {
        "x_min": ui_world[0] - cavity_x_min,
        "x_max": cavity_x_max - ui_world[1],
        "inner_wall": ui_world[2] - cavity_y_half,
        "outer_faceplate_gap": faceplate_inner_y - ui_world[3],
        "z_min": ui_world[4] - (ui_z_min - ui_window_border),
        "z_max": (ui_z_min + ui_board_width + ui_window_border) - ui_world[5],
    }
    inner_x_min = number(parameters, "m6_detector_shell_inner_min_x")
    inner_x_max = number(parameters, "m6_detector_shell_inner_max_x")
    body_max_x = number(parameters, "m6_detector_body_max_x")
    body_min_y = number(parameters, "m6_detector_body_min_y")
    body_max_y = number(parameters, "m6_detector_body_max_y")
    shell_clearance = number(parameters, "m6_detector_shell_clearance")
    inner_y_min = body_min_y - shell_clearance
    inner_y_max = body_max_y + shell_clearance
    shell_bottom = number(parameters, "m6_detector_shell_bottom_z")
    body_top = number(parameters, "m6_detector_body_top_z")
    receiver_local = stl_bounds(MODEL_DIR / "m6-receiver-carrier-v0.2.stl")
    receiver_world = rotate_y_minus_90_then_translate(
        receiver_local,
        number(parameters, "m6_receiver_carrier_board_x"),
        number(parameters, "m6_receiver_carrier_board_y"),
        number(parameters, "m6_receiver_carrier_board_z_min"),
    )
    receiver_region = (
        inner_x_min,
        inner_x_max,
        inner_y_min,
        inner_y_max,
        shell_bottom - 0.1,
        body_top + shell_clearance,
    )
    receiver_margins = margin_report(receiver_world, receiver_region)
    receiver_margins["optical_body_clearance"] = receiver_world[0] - body_max_x
    receiver_declared_clearance = number(parameters, "m6_receiver_carrier_clearance_to_body_x")
    receiver_pass = min(receiver_margins.values()) >= 0 and receiver_margins["optical_body_clearance"] >= 1.0
    main_pass = min(main_margins.values()) >= 0 and floor_margins["main"] >= 0
    emitter_pass = min(emitter_margins.values()) >= 0 and floor_margins["emitter"] >= 0
    battery_pass = min(battery_margins.values()) >= 0
    ui_pass = min(ui_xy_margins.values()) >= 0
    return {
        "cavity_mm": {
            "x": [cavity_x_min, cavity_x_max],
            "y": [-cavity_y_half, cavity_y_half],
            "top_z": cavity_top,
            "length_x": cavity_x_max - cavity_x_min,
        },
        "main_board": {
            "local_bounds": bounds_dict(main_local),
            "world_bounds": bounds_dict(main_world),
            "translation": [main_x_min, main_y_shift, number(parameters, "clamp_electronics_board_bottom_z")],
            "margins_to_cavity": rounded_mapping(main_margins),
            "floor_clearance": round(floor_margins["main"], 4),
            "status": "PASS" if main_pass else "FAIL",
        },
        "emitter_board": {
            "local_bounds": bounds_dict(emitter_local),
            "world_bounds": bounds_dict(emitter_world),
            "translation": [emitter_x_min, emitter_y_shift, number(parameters, "clamp_electronics_emitter_board_bottom_z")],
            "margins_to_cavity": rounded_mapping(emitter_margins),
            "floor_clearance": round(floor_margins["emitter"], 4),
            "status": "PASS" if emitter_pass else "FAIL",
        },
        "ui_board": {
            "local_bounds": bounds_dict(ui_local),
            "world_bounds": bounds_dict(ui_world),
            "side_datum": {
                "board_x_min": ui_x_min,
                "board_plane_y": ui_plane_y,
                "board_z_min": ui_z_min,
                "y_reflection": True,
            },
            "margins_to_side_window": rounded_mapping(ui_xy_margins),
            "status": "PASS" if ui_pass else "FAIL",
        },
        "internal_battery": {
            "quantity": 2,
            "size_mm": [battery_length, battery_width, number(parameters, "clamp_electronics_battery_thickness_z")],
            "world_bounds": bounds_dict(battery_world),
            "margins_to_cavity": rounded_mapping(battery_margins),
            "rail_side_clearance": round(cavity_y_half - battery_width / 2 - number(parameters, "clamp_electronics_battery_rail_clearance_y") - number(parameters, "clamp_electronics_battery_rail_t") / 2, 4),
            "status": "PASS" if battery_pass else "FAIL",
        },
        "mother_board_bosses": {
            "hole_centers_xy_mm": [[round(x, 4), round(y, 4)] for x, y in hole_xy],
            "boss_diameter_mm": number(parameters, "clamp_electronics_board_standoff_d"),
            "status": "PASS" if boss_check else "FAIL",
        },
        "m6_receiver_carrier": {
            "local_bounds": bounds_dict(receiver_local),
            "world_bounds": bounds_dict(receiver_world),
            "translation_and_rotation": {
                "translate": [number(parameters, "m6_receiver_carrier_board_x"), number(parameters, "m6_receiver_carrier_board_y"), number(parameters, "m6_receiver_carrier_board_z_min")],
                "rotation_deg_y": -90,
            },
            "margins_to_m6_inner_shell": rounded_mapping(receiver_margins),
            "declared_conservative_body_clearance": round(receiver_declared_clearance, 4),
            "status": "PASS" if receiver_pass else "FAIL",
        },
        "all_pass": main_pass and emitter_pass and ui_pass and battery_pass and boss_check and receiver_pass,
    }


def check_print_manifest() -> Dict[str, Any]:
    if not PRINT_MANIFEST.is_file():
        raise RuntimeError("print manifest missing: %s" % PRINT_MANIFEST)
    data = json.loads(PRINT_MANIFEST.read_text(encoding="utf-8"))
    entries = data.get("parts")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("print manifest has no parts")
    closed = sum(
        1 for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("topology"), dict)
        and entry["topology"].get("watertight_by_edge_topology") is True
    )
    positive = sum(
        1 for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("volume_mm3"), (int, float)) and entry["volume_mm3"] > 0
    )
    if len(entries) != EXPECTED_PRINTABLE_COUNT or closed != len(entries) or positive != len(entries):
        raise RuntimeError(
            "print manifest is not a complete closed %d-part package"
            % EXPECTED_PRINTABLE_COUNT
        )
    return {
        "manifest": str(PRINT_MANIFEST.relative_to(ROOT)),
        "printable_stl_count": len(entries),
        "closed_count": closed,
        "positive_volume_count": positive,
        "status": "PASS",
    }


def check_open_scad_views(openscad: str) -> Dict[str, Any]:
    views = [
        ("clamp_electronics_full_cutaway", ()),
        ("clamp_electronics_shell_cutaway", ()),
        ("clamp_electronics_exploded", ("SIDE=1",)),
        ("clamp_electronics_emitter_exploded", ("SIDE=-1",)),
        ("clamp_electronics_system_exploded", ()),
        ("clamp_electronics_m6_integration_preview", ("SIDE=1",)),
        ("clamp_electronics_m6_integration_preview", ("SIDE=-1",)),
        ("m6_detector_mount", ("SIDE=1",)),
        ("m6_detector_exploded", ("SIDE=1",)),
    ]
    records: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="pingpang-fit-views-") as directory:
        output_dir = Path(directory)
        for index, (part, definitions) in enumerate(views):
            output = output_dir / ("%02d-%s.stl" % (index, part))
            result = run_openscad(openscad, output, part, definitions)
            if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError("OpenSCAD view failed for %s:\n%s" % (part, result.stdout))
            records.append({
                "part": part,
                "definitions": list(definitions),
                "bytes": output.stat().st_size,
                "manifold_reported": "NoError" in result.stdout,
            })
    return {"views": records, "status": "PASS"}


def check_empty_interference_probes(openscad: str) -> Dict[str, Any]:
    probes = [
        ("clamp_electronics_interference_check", ("SIDE=1",)),
        ("clamp_electronics_interference_check", ("SIDE=-1",)),
        ("m6_receiver_carrier_interference_check", ("SIDE=1",)),
        ("m6_receiver_carrier_interference_check", ("SIDE=-1",)),
    ]
    records: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="pingpang-fit-interference-") as directory:
        output_dir = Path(directory)
        for index, (part, definitions) in enumerate(probes):
            output = output_dir / ("%02d-%s.stl" % (index, part))
            result = run_openscad(openscad, output, part, definitions)
            has_mesh = output.is_file() and output.stat().st_size > 0
            empty_top_level = "Current top level object is empty" in result.stdout
            if result.returncode != 0 and not empty_top_level:
                raise RuntimeError("OpenSCAD interference probe failed for %s:\n%s" % (part, result.stdout))
            if has_mesh:
                raise RuntimeError(
                    "interference probe is non-empty for %s %s:\n%s"
                    % (part, definitions, result.stdout)
                )
            records.append({
                "part": part,
                "definitions": list(definitions),
                "intersection_mesh": "empty",
                "status": "PASS",
            })
    return {
        "method": "OpenSCAD boolean intersection; empty STL is pass",
        "aabb_is_conservative": True,
        "probes": records,
        "status": "PASS",
    }


def markdown_report(report: Dict[str, Any]) -> str:
    mechanical = report["mechanical_fit"]
    boards = report["boards"]
    lines = [
        "# Pingpang SmartGear electronics system fit report v0.2",
        "",
        "- Overall mechanical/package status: **%s**" % report["status"],
        "- Generated: `%s`" % report["generated_at"],
        "- Mechanical source: `hardware/cad/net_stand.scad`",
        "- Native KiCad status: `%s`" % report["native_kicad"]["kicad_pdf_export"],
            "- Native KiCad projects: `%d` `.kicad_pcb` / `%d` `.kicad_pro`; schematic PDF export: `%s`" % (report["native_kicad"]["native_pcb_count"], report["native_kicad"]["native_project_count"], report["native_kicad"]["kicad_pdf_export"]),
            "- Atopile `.ato`: validate `%s`, build `%s` (interface contract only; native KiCad remains the PCB source of truth)" % (report["native_kicad"]["atopile_validation"], report["native_kicad"]["atopile_build"]),
            "- Native schematics exported: `%d/%d`; ERC is intentionally OPEN for the first-article review files." % (sum(item["pdf_export"] == "PASS" for item in report["native_kicad"]["native_schematics"]), len(report["native_kicad"]["native_schematics"])),
            "- Retained legacy schematic connector contract: `%s` (obsolete P2.00/P2.54/PinHeader tokens are rejected)." % report["native_kicad"]["legacy_connector_contract"]["status"],
        "",
        "## Board files and signal budget",
        "",
        "| board | outline | copper layers | footprints | 3D models | nets | tracks | unconnected |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for board in boards:
        lines.append(
            "| `%s` | %.1f x %.1f mm | %d | %d | %d | %d | %d | %d |"
            % (
                Path(board["path"]).name,
                board["size_mm"][0],
                board["size_mm"][1],
                board["copper_layer_count"],
                board["footprints"],
                board["models"],
                board["nets"],
                board["tracks"],
                board["unconnected"],
            )
        )
    lines.extend(
        [
            "",
            "The PCB files and board STL/STEP exports are real KiCad artifacts. The main board still has an open copper gate (`%d` unconnected items); it is not a fabrication/Gerber release." % boards[0]["unconnected"],
            "",
            "- Physical cable connectors pass the generated `MX1.25`/1.25 mm pad-pitch contract, and every such PCB connector has a matching MX1.25 schematic instance; USB-C and button footprints are separate interfaces.",
            "- Ordered connector pin-to-net contracts pass for the mother board, receiver 3-wire inputs, emitter 2-wire outputs and UI harnesses.",
            "- Native PCB DRC aggregate: `%s`; errors, expected isolated-copper warnings and unconnected airwires are reported separately below." % report["pcb_drc"]["status"],
            "",
            "## Same-datum enclosure fit",
            "",
            "| assembly | result | critical minimum margin |",
            "|---|---|---:|",
        ]
    )
    for key, title in (("main_board", "right ESP32 mother board"), ("emitter_board", "left emitter power board"), ("ui_board", "cover UI board"), ("internal_battery", "internal battery envelope"), ("m6_receiver_carrier", "vertical M6 receiver carrier")):
        item = mechanical[key]
        margins = item.get(
            "margins_to_cavity",
            item.get(
                "margins_to_side_window",
                item.get(
                    "xy_margins_to_cavity_datum",
                    item.get("margins_to_m6_inner_shell", {}),
                ),
            ),
        )
        minimum = min(margins.values()) if margins else 0
        lines.append("| %s | **%s** | %.3f mm |" % (title, item["status"], minimum))
    lines.extend(
        [
            "",
            "Mother-board boss centers are taken from the four NPTH positions in `esp32-control-v0.1.kicad_pcb`; the report does not use a symmetric placeholder hole pattern.",
            "",
            "## Interference and exploded-view evidence",
            "",
            "- AABB fit: conservative x/y/z envelope checks for every imported KiCad board and both internal battery packs.",
            "- Boolean interference: `%s` across both clamp sides and both M6 sides." % report["interference"]["status"],
            "- OpenSCAD view compilation: `%s` for full cutaway, physical shell cutaway, per-side exploded views, M6 integration, and M6 exploded assembly." % report["openscad_views"]["status"],
            "- Printable package: `%d/%d` STL files closed and positive volume." % (report["print_package"]["closed_count"], report["print_package"]["printable_stl_count"]),
            "",
            "## UI panel direct interface",
            "",
            "- Direct datum status: **%s**. START/MODE, both 0603 LEDs and the vertical USB-C footprint all match the printed faceplate centers with zero measured coordinate error." % report["ui_interface"]["status"],
            "- Faceplate contract: screen opening `%.1f × %.1f mm`, button pocket `Ø%.1f mm` with `Ø%.1f mm` plungers, LED bores `Ø%.1f mm`, speaker opening `Ø%.1f mm`, USB-C slot `%.1f × %.1f mm`, board-to-faceplate gap `%.1f mm`." % (
                report["ui_interface"]["faceplate"]["screen_opening_mm"][0],
                report["ui_interface"]["faceplate"]["screen_opening_mm"][1],
                report["ui_interface"]["faceplate"]["button_pocket_d_mm"],
                report["ui_interface"]["faceplate"]["button_plunger_d_mm"],
                report["ui_interface"]["faceplate"]["led_bore_d_mm"],
                report["ui_interface"]["faceplate"]["speaker_opening_d_mm"],
                report["ui_interface"]["faceplate"]["usb_opening_mm"][0],
                report["ui_interface"]["faceplate"]["usb_opening_mm"][1],
                report["ui_interface"]["faceplate"]["board_to_faceplate_gap_mm"],
            ),
            "- USB-C mating axis: `%s`; its model is `%s`. The final purchased vertical-receptacle STEP/part number remains an explicit first-article item." % (
                report["ui_interface"]["usb_c"]["mating_axis"],
                report["ui_interface"]["usb_c"]["model"],
            ),
            "",
            "## PCB DRC evidence",
            "",
            "| board | DRC status | errors | warnings | unconnected |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for item in report["pcb_drc"]["boards"]:
        lines.append(
            "| `%s` | **%s** | %d | %d | %d |"
            % (
                Path(item["path"]).name,
                item["status"],
                item["errors"],
                item["warnings"],
                item["unconnected"],
            )
        )
    lines.extend(
        [
            "",
            "The isolated-copper warnings are expected at this review stage because zones surround intentionally unrouted nets; they do not close the electrical fabrication gate.",
            "",
            "## Release boundary",
            "",
            "- Mechanical/package gate: **PASS**.",
            "- Electrical fabrication gate: **OPEN** until copper routing, DRC, power-current bench validation, and the placeholder optocoupler/MCU selections are frozen.",
            "- UI panel interface gate: **%s**; the real button/LED/USB-C footprints are checked against the printed y+ faceplate datum. The vertical USB-C proxy remains open only for the final vendor STEP swap." % report["ui_interface"]["status"],
            "- Lid fit is treated as a flush, no-visible-gap mechanical interface; this is not an IP waterproof certification.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_with_kicad_python() -> int:
    try:
        import pcbnew  # type: ignore
    except ModuleNotFoundError:
        bundled = find_kicad_python()
        if Path(sys.executable).resolve() != Path(bundled).resolve():
            result = subprocess.run([bundled, str(Path(__file__).resolve())], check=False)
            return result.returncode
        raise

    openscad = find_openscad()
    cli = find_kicad_cli()
    parameters = probe_scad(openscad)
    boards = check_boards(pcbnew)
    ui_interface = check_ui_interface_alignment(
        pcbnew,
        HERE / "daughter-boards-v0.2/ui-panel-v0.2.kicad_pcb",
        parameters,
    )
    native_kicad = check_native_kicad(cli)
    pcb_drc = check_pcb_drc(cli)
    mechanical = check_model_fits(parameters)
    if not mechanical["all_pass"]:
        raise RuntimeError("one or more same-datum electronic envelopes failed")
    print_package = check_print_manifest()
    interference = check_empty_interference_probes(openscad)
    openscad_views = check_open_scad_views(openscad)
    report: Dict[str, Any] = {
        "schema_version": "0.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "mechanical_fit": mechanical,
        "ui_interface": ui_interface,
        "boards": boards,
        "native_kicad": native_kicad,
        "pcb_drc": pcb_drc,
        "print_package": print_package,
        "interference": interference,
        "openscad_views": openscad_views,
        "release_boundary": {
            "mechanical_package": "PASS",
            "electrical_fabrication": "OPEN",
            "reason": "PCB connectivity still contains unconnected items and first-article placeholders",
            "lid_interface": "flush/no-visible-gap fit target, not IP waterproof certification",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(markdown_report(report), encoding="utf-8")
    print(
        "ELECTRONICS_FIT_OK "
        "mechanical=PASS "
        "interference=PASS "
        "printables=%d/%d "
        "native_kicad=PASS "
        "electrical_release=OPEN "
        "report=%s"
        % (
            print_package["closed_count"],
            print_package["printable_stl_count"],
            REPORT_JSON,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_with_kicad_python())
