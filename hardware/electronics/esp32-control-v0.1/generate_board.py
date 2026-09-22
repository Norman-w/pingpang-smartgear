#!/usr/bin/env python3
"""Generate the Pingpang ESP32-S3 control/power first-article PCB.

This deliberately uses KiCad's bundled ``pcbnew`` Python API instead of
hand-editing a board file.  The output is a real KiCad board with library
3D models attached to the first-article footprints.  Copper routing remains a
separate review gate; the M6 optical receiver carrier remains a separate board
connected through J4.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "esp32-control-v0.1.kicad_pcb"
MM = 1_000_000
BOARD_W = 86.0
BOARD_H = 32.0


MODEL_ESP32 = "${KICAD10_3DMODEL_DIR}/RF_Module.3dshapes/ESP32-S3-WROOM-1.step"
MODEL_IP5305 = "${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/HTSOP-8-1EP_3.9x4.9mm_P1.27mm.step"
MODEL_TPS62162 = "${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm.step"
MODEL_USB_C = "${KICAD10_3DMODEL_DIR}/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step"
MX125_PITCH = 1.25
# The exact purchased MX1.25 manufacturer/SKU is not present in the
# repository.  The installed JST-GH models provide a real keyed 1.25 mm
# visual envelope for this review candidate; replace only the model/land
# pattern after the user's exact connector is frozen.
MODEL_MX125_1X12 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM12B-GHS-TB_1x12-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X8 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM08B-GHS-TB_1x08-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X4 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X2 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal.step"
MODEL_0603 = "${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0603_1608Metric.step"


def add_3d_model(pcbnew, fp, filename: str, rotation=(0.0, 0.0, 0.0)):
    """Attach a KiCad library model to a generated footprint.

    The pad geometry remains generated from the electrical contract, while
    the visual/height envelope comes from the installed KiCad library model.
    This makes the board export usable by the mechanical assembly without
    pretending that an unmodelled rectangle is a finished component.
    """
    model = pcbnew.FP_3DMODEL()
    model.m_Filename = filename
    model.m_Offset = pcbnew.VECTOR3D(0.0, 0.0, 0.0)
    model.m_Rotation = pcbnew.VECTOR3D(*rotation)
    model.m_Scale = pcbnew.VECTOR3D(1.0, 1.0, 1.0)
    model.m_Opacity = 1.0
    model.m_Show = True
    fp.Add3DModel(model)
    return model


def connector_model(ref: str, count: int, pitch: float, horizontal: bool):
    """Return a library model and XY rotation for a connector envelope."""
    if abs(pitch - MX125_PITCH) < 0.02:
        models = {
            12: MODEL_MX125_1X12,
            8: MODEL_MX125_1X8,
            4: MODEL_MX125_1X4,
            2: MODEL_MX125_1X2,
        }
        filename = models.get(count)
        if filename is None:
            return None
        return filename, (0.0, 0.0, 90.0 if not horizontal else 0.0)
    return None


def xy(pcbnew, x: float, y: float):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


def ensure_net(board, pcbnew, name: str):
    if name != name.lower():
        raise ValueError(f"net names must be lowercase: {name}")
    net = board.FindNet(name)
    if net is None:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
    return net


def add_text(board, pcbnew, text: str, x: float, y: float, size: float = 1.0,
             layer=None, thickness: float = 0.15):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetLayer(pcbnew.Dwgs_User if layer is None else layer)
    item.SetPosition(xy(pcbnew, x, y))
    item.SetTextHeight(int(round(size * MM)))
    item.SetTextWidth(int(round(size * MM)))
    item.SetTextThickness(int(round(thickness * MM)))
    board.Add(item)
    return item


def add_segment(board, pcbnew, layer, a: tuple[float, float],
                b: tuple[float, float], width: float = 0.15):
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(layer)
    shape.SetStart(xy(pcbnew, *a))
    shape.SetEnd(xy(pcbnew, *b))
    shape.SetWidth(int(round(width * MM)))
    board.Add(shape)
    return shape


def add_rect(board, pcbnew, layer, cx: float, cy: float, w: float, h: float,
             width: float = 0.12):
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = cy - h / 2, cy + h / 2
    for a, b in (
        ((x0, y0), (x1, y0)),
        ((x1, y0), (x1, y1)),
        ((x1, y1), (x0, y1)),
        ((x0, y1), (x0, y0)),
    ):
        add_segment(board, pcbnew, layer, a, b, width)


def add_board_outline(board, pcbnew):
    add_rect(board, pcbnew, pcbnew.Edge_Cuts, BOARD_W / 2, BOARD_H / 2,
             BOARD_W, BOARD_H, 0.05)


def add_smd_pad(pcbnew, fp, number: str, x: float, y: float, w: float,
                h: float, net=None):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(xy(pcbnew, w, h))
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    layers.AddLayer(pcbnew.F_Mask)
    pad.SetLayerSet(layers)
    pad.SetFPRelativePosition(xy(pcbnew, x, y))
    if net is not None:
        pad.SetNet(net)
    fp.Add(pad)
    return pad


def add_pth_pad(pcbnew, fp, number: str, x: float, y: float, diameter: float,
                drill: float, net=None):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(xy(pcbnew, diameter, diameter))
    pad.SetDrillSize(xy(pcbnew, drill, drill))
    pad.SetLayerSet(pad.PTHMask())
    pad.SetFPRelativePosition(xy(pcbnew, x, y))
    if net is not None:
        pad.SetNet(net)
    fp.Add(pad)
    return pad


def add_npth_pad(pcbnew, fp, x: float, y: float, diameter: float,
                 drill: float):
    pad = pcbnew.PAD(fp)
    pad.SetNumber("")
    pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(xy(pcbnew, diameter, diameter))
    pad.SetDrillSize(xy(pcbnew, drill, drill))
    pad.SetLayerSet(pad.UnplatedHoleMask())
    pad.SetFPRelativePosition(xy(pcbnew, x, y))
    fp.Add(pad)
    return pad


def new_fp(board, pcbnew, ref: str, value: str, x: float, y: float,
           attr=None):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetAttributes(pcbnew.FP_SMD if attr is None else attr)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Value().SetLayer(pcbnew.F_Fab)
    fp.SetPosition(xy(pcbnew, x, y))
    fp.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
    return fp


def add_chip(board, pcbnew, pads: dict[str, str], ref: str, value: str,
             x: float, y: float, pad_xy: list[tuple[str, float, float]],
             body: tuple[float, float] = (3.2, 1.8), pad_size=(1.0, 1.0)):
    fp = new_fp(board, pcbnew, ref, value, x, y)
    netpads = {}
    for number, px, py in pad_xy:
        netpads[number] = add_smd_pad(
            pcbnew, fp, number, px, py, pad_size[0], pad_size[1],
            pads.get(number))
    board.Add(fp)
    add_rect(board, pcbnew, pcbnew.F_Fab, x, y, body[0], body[1], 0.10)
    add_text(board, pcbnew, ref, x, y - body[1] / 2 - 0.7, 0.75)
    add_3d_model(pcbnew, fp, MODEL_0603)
    return fp, netpads


def add_two_pad_chip(board, pcbnew, pads: dict[str, str], ref: str,
                     value: str, x: float, y: float, horizontal=True,
                     body=(2.4, 1.4), pad_size=(1.0, 1.0)):
    if horizontal:
        coords = [("1", -body[0] / 2 - 0.05, 0),
                  ("2", body[0] / 2 + 0.05, 0)]
    else:
        coords = [("1", 0, -body[1] / 2 - 0.05),
                  ("2", 0, body[1] / 2 + 0.05)]
    return add_chip(board, pcbnew, pads, ref, value, x, y, coords, body,
                    pad_size)


def add_connector(board, pcbnew, pads: dict[str, str], ref: str, value: str,
                  x: float, y: float, count: int, pitch: float = MX125_PITCH,
                  horizontal=False, body_w: float | None = None):
    if abs(pitch - MX125_PITCH) < 0.02:
        # Match the installed keyed-locking 1.25 mm model: signal pads are
        # 1.25 mm apart, while the two mounting pads are mechanical only.
        fp = new_fp(board, pcbnew, ref, value, x, y, pcbnew.FP_SMD)
        span = (count - 1) * MX125_PITCH
        signal_size = (0.6, 1.7) if horizontal else (1.7, 0.6)
        for index in range(count):
            offset = (index - (count - 1) / 2) * MX125_PITCH
            px, py = ((offset, -1.85) if horizontal
                      else (1.85, offset))
            number = str(index + 1)
            add_smd_pad(
                pcbnew, fp, number, px, py, signal_size[0], signal_size[1],
                pads.get(number),
            )
        mount_offset = span / 2 + 1.85
        mount_xy = ((-mount_offset, 1.35), (mount_offset, 1.35)) if horizontal else (
            (-1.35, -mount_offset), (-1.35, mount_offset)
        )
        # Keep the mechanical lands inside a compact board edge with the
        # current review placement.  The exact MX1.25 land pattern remains a
        # later SKU-freeze item, so this is not presented as a production pad.
        mount_size = (1.0, 2.2) if horizontal else (2.2, 1.0)
        for px, py in mount_xy:
            add_smd_pad(pcbnew, fp, "MP", px, py,
                        mount_size[0], mount_size[1])
        board.Add(fp)
        w, h = (span + 3.7, 5.3) if horizontal else (5.3, span + 3.7)
        add_rect(board, pcbnew, pcbnew.F_Fab, x, y, w, h, 0.10)
        add_text(board, pcbnew, ref, x, y - h / 2 - 0.8, 0.75)
        model_info = connector_model(ref, count, pitch, horizontal)
        if model_info:
            add_3d_model(pcbnew, fp, *model_info)
        return {str(index + 1): fp.Pads()[index] for index in range(count)}

    fp = new_fp(board, pcbnew, ref, value, x, y, pcbnew.FP_THROUGH_HOLE)
    # Keep the placeholder WTB pads manufacturable at the 1.25 mm UI pitch.
    # The final connector library footprint will replace this review shape,
    # but must preserve the same pitch and pin order.
    pad_diameter = min(1.7, max(0.8, pitch - 0.30))
    drill_diameter = min(0.9, pad_diameter - 0.30)
    coords = []
    netpads = {}
    for index in range(count):
        offset = (index - (count - 1) / 2) * pitch
        px, py = (offset, 0) if horizontal else (0, offset)
        number = str(index + 1)
        coords.append((px, py))
        netpads[number] = add_pth_pad(
            pcbnew, fp, number, px, py, pad_diameter, drill_diameter,
            pads.get(number))
    board.Add(fp)
    if horizontal:
        w, h = ((count - 1) * pitch + 3.0, 3.4)
    else:
        w, h = (3.4, (count - 1) * pitch + 3.0)
    if body_w is not None:
        w = body_w if horizontal else 3.4
    add_rect(board, pcbnew, pcbnew.F_Fab, x, y, w, h, 0.10)
    add_text(board, pcbnew, ref, x, y - h / 2 - 0.8, 0.75)
    model_info = connector_model(ref, count, pitch, horizontal)
    if model_info:
        add_3d_model(pcbnew, fp, *model_info)
    return netpads


def add_usb_c_receptacle(board, pcbnew, pads: dict[str, str], ref: str,
                         value: str, x: float, y: float):
    """Add the native 16-contact USB-C model instead of a fake pin row."""
    fp = new_fp(board, pcbnew, ref, value, x, y, pcbnew.FP_SMD)
    usb_pads = (
        ("A1", -3.20, -3.68, 0.6, 1.15, "gnd"),
        ("A4", -2.40, -3.68, 0.6, 1.15, "usb_vbus"),
        ("A5", -1.25, -3.68, 0.3, 1.15, "cc1"),
        ("A6", -0.25, -3.68, 0.3, 1.15, "usb_dp"),
        ("A7", 0.25, -3.68, 0.3, 1.15, "usb_dn"),
        ("A8", 1.25, -3.68, 0.3, 1.15, None),
        ("A9", 2.40, -3.68, 0.6, 1.15, "usb_vbus"),
        ("A12", 3.20, -3.68, 0.6, 1.15, "gnd"),
        ("B1", 3.20, -3.68, 0.6, 1.15, "gnd"),
        ("B4", 2.40, -3.68, 0.6, 1.15, "usb_vbus"),
        ("B5", 1.75, -3.68, 0.3, 1.15, "cc2"),
        ("B6", 0.75, -3.68, 0.3, 1.15, "usb_dp"),
        ("B7", -0.75, -3.68, 0.3, 1.15, "usb_dn"),
        ("B8", -1.75, -3.68, 0.3, 1.15, None),
        ("B9", -2.40, -3.68, 0.6, 1.15, "usb_vbus"),
        ("B12", -3.20, -3.68, 0.6, 1.15, "gnd"),
    )
    for number, px, py, w, h, net_name in usb_pads:
        add_smd_pad(pcbnew, fp, number, px, py, w, h,
                    pads.get(number) if net_name else None)
    for px, py in ((-4.32, -3.105), (-4.32, 1.075),
                   (4.32, -3.105), (4.32, 1.075)):
        add_pth_pad(pcbnew, fp, "SH", px, py, 1.0, 0.6)
    board.Add(fp)
    add_rect(board, pcbnew, pcbnew.F_Fab, x, y - 0.29, 10.64, 8.94, 0.10)
    add_text(board, pcbnew, ref, x, y - 5.6, 0.70)
    add_3d_model(pcbnew, fp, MODEL_USB_C)
    return {number: fp.FindPadByNumber(number) for number, *_ in usb_pads}


def add_test_point(board, pcbnew, net, ref: str, x: float, y: float):
    fp = new_fp(board, pcbnew, ref, "TEST_POINT", x, y,
                pcbnew.FP_THROUGH_HOLE)
    add_pth_pad(pcbnew, fp, "1", 0, 0, 1.8, 0.9, net)
    board.Add(fp)
    add_text(board, pcbnew, ref, x, y + 1.6, 0.60)
    return fp


def add_mount_hole(board, pcbnew, ref: str, x: float, y: float):
    fp = new_fp(board, pcbnew, ref, "M2.5 NPTH", x, y,
                pcbnew.FP_THROUGH_HOLE)
    add_npth_pad(pcbnew, fp, 0, 0, 4.8, 2.8)
    board.Add(fp)
    add_rect(board, pcbnew, pcbnew.F_Fab, x, y, 5.5, 5.5, 0.10)


def add_esp32(board, pcbnew, nets: dict[str, object]):
    # Rotated ESP32-S3-WROOM-1-N16R8 reference placement.  The local pad
    # coordinates are the same orientation documented by the SmartPaddle
    # reference: antenna toward board -X.
    pad_xy = {}
    for pad in range(1, 15):
        pad_xy[pad] = (-5.26 + (pad - 1) * 1.27, 9.20)
    for pad in range(15, 27):
        pad_xy[pad] = (13.00, 6.985 - (pad - 15) * 1.27)
    for pad in range(27, 41):
        pad_xy[pad] = (11.25 - (pad - 27) * 1.27, -9.20)

    pad_net_names = {
        1: "gnd", 2: "3v3", 3: "esp_en", 4: "ui_btn_mode",
        5: "carrier_reset_n", 7: "ui_spk_bclk", 8: "ui_spk_ws",
        9: "ui_scl", 10: "ui_sda", 11: "ui_spk_dout",
        12: "ui_led_status", 13: "ui_buzzer", 14: "usb_dn_mcu",
        16: "ui_btn_start", 17: "bat_sense", 18: "carrier_sck",
        19: "carrier_mosi", 20: "carrier_miso", 21: "carrier_cs_n",
        22: "carrier_irq_n", 23: "ui_led_battery", 24: "power_latch_future",
        15: "usb_dp_mcu", 25: "user_button_future", 27: "boot", 36: "uart_rx",
        37: "uart_tx", 38: "pvdf_adc_r", 39: "pvdf_adc_l", 40: "gnd",
    }
    fp = new_fp(board, pcbnew, "U1", "ESP32-S3-WROOM-1-N16R8", 25, 16)
    pad_refs = {}
    for number, (px, py) in pad_xy.items():
        net_name = pad_net_names.get(number)
        pad_refs[str(number)] = add_smd_pad(
            pcbnew, fp, str(number), px, py, 1.0, 1.0,
            nets.get(net_name) if net_name else None)
    board.Add(fp)
    add_rect(board, pcbnew, pcbnew.F_Fab, 25, 16, 25.5, 18.0, 0.12)
    add_text(board, pcbnew, "U1 ESP32-S3", 25, 27.2, 0.80)
    add_text(board, pcbnew, "ANT -X", 12.5, 16, 0.65)
    add_3d_model(pcbnew, fp, MODEL_ESP32, (0.0, 0.0, 90.0))
    return fp, pad_refs


def add_ip5305(board, pcbnew, nets):
    pad_xy = {
        "1": (-2.5, -2.25), "2": (-2.5, -0.75),
        "3": (-2.5, 0.75), "4": (-2.5, 2.25),
        "5": (2.5, 2.25), "6": (2.5, 0.75),
        "7": (2.5, -0.75), "8": (2.5, -2.25), "9": (0, 0),
    }
    pad_nets = {
        "1": "vbus_limited", "2": "led_charge", "3": "ip_led2_nc",
        "4": "ip_led3_nc", "5": "power_key", "6": "bat_p",
        "7": "boost_sw", "8": "sys_5v", "9": "gnd",
    }
    fp = new_fp(board, pcbnew, "U2", "IP5305T-HSOP8-1EP", 47, 7.5)
    refs = {}
    for number, (px, py) in pad_xy.items():
        refs[number] = add_smd_pad(
            pcbnew, fp, number, px, py, 1.35 if number != "9" else 2.8,
            1.0 if number != "9" else 2.8,
            nets[pad_nets[number]])
    board.Add(fp)
    add_rect(board, pcbnew, pcbnew.F_Fab, 47, 7.5, 7.5, 6.5, 0.10)
    add_text(board, pcbnew, "U2 IP5305T", 47, 11.8, 0.75)
    add_3d_model(pcbnew, fp, MODEL_IP5305)
    return fp, refs


def add_tps62162(board, pcbnew, nets):
    pad_xy = {
        "1": (-2.5, -2.25), "2": (-2.5, -0.75),
        "3": (-2.5, 0.75), "4": (-2.5, 2.25),
        "5": (2.5, 2.25), "6": (2.5, 0.75),
        "7": (2.5, -0.75), "8": (2.5, -2.25), "9": (0, 0),
    }
    pad_nets = {
        "1": "gnd", "2": "sys_5v", "3": "buck_en", "4": "gnd",
        "5": "gnd", "6": "3v3", "7": "buck_sw", "8": "pg_3v3",
        "9": "gnd",
    }
    fp = new_fp(board, pcbnew, "U3", "TPS62162-QFN8-EP", 67, 7.5)
    refs = {}
    for number, (px, py) in pad_xy.items():
        refs[number] = add_smd_pad(
            pcbnew, fp, number, px, py, 1.35 if number != "9" else 2.8,
            1.0 if number != "9" else 2.8,
            nets[pad_nets[number]])
    board.Add(fp)
    add_rect(board, pcbnew, pcbnew.F_Fab, 67, 7.5, 7.5, 6.5, 0.10)
    add_text(board, pcbnew, "U3 TPS62162", 67, 11.8, 0.75)
    add_3d_model(pcbnew, fp, MODEL_TPS62162)
    return fp, refs


def add_keepout(board, pcbnew, name: str, points):
    zone = pcbnew.ZONE(board)
    zone.SetIsRuleArea(True)
    zone.SetDoNotAllowZoneFills(True)
    zone.SetDoNotAllowTracks(True)
    zone.SetDoNotAllowVias(True)
    zone.SetDoNotAllowPads(False)
    zone.SetDoNotAllowFootprints(False)
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    layers.AddLayer(pcbnew.B_Cu)
    zone.SetLayerSet(layers)
    zone.SetZoneName(name)
    for x, y in points:
        zone.AppendCorner(xy(pcbnew, x, y), -1)
    board.Add(zone)
    return zone


def add_ground_zone(board, pcbnew, net):
    zone = pcbnew.ZONE(board)
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    layers.AddLayer(pcbnew.B_Cu)
    zone.SetLayerSet(layers)
    zone.SetNet(net)
    zone.SetZoneName("GND_PLANE_FIRST_ARTICLE")
    zone.SetAssignedPriority(0)
    zone.SetLocalClearance(int(round(0.25 * MM)))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    zone.SetFillMode(pcbnew.ZONE_FILL_MODE_POLYGONS)
    for point in ((0.6, 0.6), (BOARD_W - 0.6, 0.6),
                  (BOARD_W - 0.6, BOARD_H - 0.6), (0.6, BOARD_H - 0.6)):
        zone.AppendCorner(xy(pcbnew, *point), -1)
    board.Add(zone)
    zone.SetFillFlag(pcbnew.F_Cu, True)
    zone.SetFillFlag(pcbnew.B_Cu, True)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    return zone


def add_ground_via(board, pcbnew, net, x: float, y: float):
    """Connect a crowded exposed-pad ground island to the B.Cu plane."""
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(xy(pcbnew, x, y))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetWidth(int(round(0.80 * MM)))
    via.SetDrill(int(round(0.30 * MM)))
    via.SetNet(net)
    board.Add(via)
    return via


def add_track(board, pcbnew, net, a, b, layer=0, width=0.20):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(xy(pcbnew, *a))
    track.SetEnd(xy(pcbnew, *b))
    track.SetLayer(layer)
    track.SetWidth(int(round(width * MM)))
    track.SetNet(net)
    board.Add(track)
    return track


def add_direct_connection(board, pcbnew, net, pad_a, pad_b, layer=0,
                          width=0.20):
    a = pad_a.GetPosition()
    b = pad_b.GetPosition()
    return add_track(
        board, pcbnew, net,
        (a.x / MM, a.y / MM), (b.x / MM, b.y / MM), layer, width)


def build_board():
    import pcbnew

    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    board.SetGenerator("Pingpang SmartGear ESP32 control v0.2")
    board.GetTitleBlock().SetTitle("Pingpang SmartGear ESP32-S3 control + 1S power v0.2")
    board.GetTitleBlock().SetComment(1, "Placement/net assignment first article; not fabrication release")
    board.GetTitleBlock().SetComment(2, "J4/J8 connect the receiver carrier; J7 connects the UI daughter board")
    board.GetTitleBlock().SetComment(3, "Protected 1S battery only; sensor rail remains external")

    net_names = (
        "gnd", "usb_vbus", "vbus_limited", "bat_p", "bat_sense", "sys_5v",
        "boost_sw", "3v3", "buck_sw", "buck_en", "pg_3v3", "power_key",
        "led_charge", "ip_led2_nc", "ip_led3_nc", "usb_dp", "usb_dn",
        "usb_dp_mcu", "usb_dn_mcu", "cc1", "cc2", "sensor_ext",
        "sensor_fused", "carrier_sck", "carrier_mosi", "carrier_miso",
        "carrier_cs_n", "carrier_irq_n", "carrier_reset_n", "pvdf_adc_l",
        "pvdf_adc_r", "pvdf_cmp_aux_l", "pvdf_cmp_aux_r", "ui_sda",
        "ui_scl", "ui_btn_start", "ui_btn_mode", "ui_buzzer",
        "ui_spk_bclk", "ui_spk_ws", "ui_spk_dout", "ui_led_status",
        "ui_led_battery", "status_led", "sensor_carrier_v",
        "power_latch_future", "user_button_future", "boot", "esp_en",
        "uart_rx", "uart_tx",
    )
    nets = {name: ensure_net(board, pcbnew, name) for name in net_names}
    add_board_outline(board, pcbnew)

    # The antenna end is toward -X.  The native rule area is intentionally
    # larger than the module outline and blocks copper/tracks/vias while still
    # allowing the module footprint itself to overlap the edge of the area.
    add_keepout(board, pcbnew, "ESP32_ANTENNA_KEEP_OUT", [
        (1.0, 7.0), (12.0, 7.0), (12.0, 27.0), (1.0, 27.0)
    ])

    # Mechanical mounting is deliberately outside the RF keepout and follows
    # the compact 86 x 32 mm board envelope used by the SCAD clamp cavity.
    # These four NPTH holes remain useful PCB/fabrication features.  The current
    # PETG shell does not align bosses or locating pins to them: its mechanical
    # datum is the Edge.Cuts contour; the enclosure retains it with two
    # opposing x-end C-brackets.
    for ref, x, y in (
        # The RF module and edge connectors occupy the nominal corners, so
        # the four bosses use the nearest clear pockets on this compact board.
        ("H1", 13.5, 28.0),
        ("H2", 45.0, 28.0),
        ("H3", 75.0, 3.5),
        ("H4", 75.0, 28.0),
    ):
        add_mount_hole(board, pcbnew, ref, x, y)

    _u1, esp_pads = add_esp32(board, pcbnew, nets)
    _u2, ip_pads = add_ip5305(board, pcbnew, nets)
    _u3, buck_pads = add_tps62162(board, pcbnew, nets)

    component_pads = {}

    def two(ref, value, x, y, padmap, horizontal=True, body=(2.4, 1.4)):
        _fp, p = add_two_pad_chip(
            board, pcbnew, padmap, ref, value, x, y, horizontal, body)
        component_pads[ref] = p

    # USB-C input and CC resistors.  VBUS is current-limited before IP5305 VIN.
    component_pads["J1"] = add_usb_c_receptacle(
        board, pcbnew,
        {"A1": nets["gnd"], "A4": nets["usb_vbus"],
         "A5": nets["cc1"], "A6": nets["usb_dp"],
         "A7": nets["usb_dn"], "A9": nets["usb_vbus"],
         "A12": nets["gnd"], "B1": nets["gnd"],
         "B4": nets["usb_vbus"], "B5": nets["cc2"],
         "B6": nets["usb_dp"], "B7": nets["usb_dn"],
         "B9": nets["usb_vbus"], "B12": nets["gnd"]},
        "J1", "USB-C-POWER-DATA", 6.2, 4.8)
    two("F1", "PTC 1.1A", 15.0, 3.8,
        {"1": nets["usb_vbus"], "2": nets["vbus_limited"]})
    two("R1", "22R USB_DP", 20.5, 3.8,
        {"1": nets["usb_dp"], "2": nets["usb_dp_mcu"]})
    two("R2", "22R USB_DN", 26.0, 3.8,
        {"1": nets["usb_dn"], "2": nets["usb_dn_mcu"]})
    two("R3", "5k1 CC1", 44.0, 19.0,
        {"1": nets["cc1"], "2": nets["gnd"]})
    two("R4", "5k1 CC2", 48.0, 19.0,
        {"1": nets["cc2"], "2": nets["gnd"]})

    # Battery connector, sense divider, and bulk capacitors.
    component_pads["J2"] = add_connector(
        board, pcbnew,
        {"1": nets["bat_p"], "2": nets["gnd"]},
        "J2", "MX1.25_PROTECTED_1S_BAT", 82.0, 4.5, 2, MX125_PITCH,
        horizontal=False)
    two("R5", "1M BAT_TOP", 73.0, 16.0,
        {"1": nets["bat_p"], "2": nets["bat_sense"]})
    two("R6", "1M BAT_BOTTOM", 73.0, 20.0,
        {"1": nets["bat_sense"], "2": nets["gnd"]})
    two("C1", "100n BAT_SENSE", 76.5, 18.0,
        {"1": nets["bat_sense"], "2": nets["gnd"]}, horizontal=False)
    two("C2", "22u BAT", 52.0, 14.0,
        {"1": nets["bat_p"], "2": nets["gnd"]}, horizontal=False)
    two("C3", "10u VBUS", 40.0, 3.8,
        {"1": nets["vbus_limited"], "2": nets["gnd"]}, horizontal=False)
    two("C4", "22u SYS5V", 58.0, 3.8,
        {"1": nets["sys_5v"], "2": nets["gnd"]}, horizontal=False)
    two("C5", "10u 3V3", 76.0, 9.0,
        {"1": nets["3v3"], "2": nets["gnd"]}, horizontal=False)

    # IP5305 boost and TPS62162 buck power loops.
    two("L1", "2.2uH BOOST XFL4020", 54.0, 7.5,
        {"1": nets["boost_sw"], "2": nets["sys_5v"]}, body=(4.0, 4.0))
    two("L2", "2.2uH BUCK XFL3012", 75.0, 7.5,
        {"1": nets["buck_sw"], "2": nets["3v3"]}, body=(3.0, 3.0))
    two("R7", "100k BUCK_EN", 60.0, 15.0,
        {"1": nets["sys_5v"], "2": nets["buck_en"]})
    two("C6", "100n BUCK_EN", 66.0, 15.0,
        {"1": nets["buck_en"], "2": nets["gnd"]})

    # Charge/status key path; LED2/LED3 remain explicit no-connect test nets.
    two("R8", "1k CHARGE_LED", 43.0, 14.0,
        {"1": nets["led_charge"], "2": nets["status_led"]})
    two("D1", "GREEN STATUS", 49.0, 14.0,
        {"1": nets["status_led"], "2": nets["gnd"]})
    component_pads["SW1"] = add_connector(
        board, pcbnew,
        {"1": nets["power_key"], "2": nets["gnd"]},
        "SW1", "IP5305 KEY", 53.0, 27.0, 2, 5.0,
        horizontal=True, body_w=7.0)

    # External 10–30 V sensor rail.  It is a passthrough to the future M6
    # carrier; it is not derived from BAT_P or SYS_5V.
    component_pads["J3"] = add_connector(
        board, pcbnew,
        {"1": nets["sensor_ext"], "2": nets["gnd"]},
        "J3", "MX1.25_SENSOR_10-30V_IN", 82.0, 11.0, 2, MX125_PITCH,
        horizontal=False)
    two("F2", "PTC SENSOR", 76.0, 13.0,
        {"1": nets["sensor_ext"], "2": nets["sensor_fused"]})
    _d2_fp, component_pads["D2"] = add_two_pad_chip(
        board, pcbnew,
        {"1": nets["sensor_fused"], "2": nets["gnd"]},
        "D2", "TVS 33V SENSOR", 82.0, 16.0,
        horizontal=True, body=(3.0, 2.0))

    # Host-side carrier connector: GPIO10..14 + GPIO5 mapping from the
    # repository candidate header.  J4 pin order is the documented contract.
    component_pads["J4"] = add_connector(
        board, pcbnew,
        {"1": nets["3v3"], "2": nets["gnd"], "3": nets["carrier_sck"],
         "4": nets["carrier_mosi"], "5": nets["carrier_miso"],
         "6": nets["carrier_cs_n"], "7": nets["carrier_irq_n"],
         "8": nets["carrier_reset_n"]},
        "J4", "MX1.25_M6_CARRIER_HOST", 82.0, 23.5, 8, MX125_PITCH,
        horizontal=False)

    # The sensor rail is kept separate from the logic harness so an external
    # 10–30 V field supply never enters the ESP32/UI cable.  J8 is the
    # pluggable two-pin hand-off to the receiver carrier.
    component_pads["J8"] = add_connector(
        board, pcbnew,
        {"1": nets["sensor_fused"], "2": nets["gnd"]},
        "J8", "MX1.25_M6_SENSOR_RAIL_LINK", 54.0, 22.0, 2, MX125_PITCH,
        horizontal=False)

    # PVDF ADC pair is wired to the firmware's current ADC candidates. The
    # comparator pair is brought to an AUX connector only; GPIO14 is reserved
    # for carrier IRQ, so no hidden muxing is introduced here.
    component_pads["J5"] = add_connector(
        board, pcbnew,
        {"1": nets["pvdf_adc_l"], "2": nets["gnd"],
         "3": nets["pvdf_adc_r"], "4": nets["gnd"]},
        "J5", "MX1.25_PVDF_ADC_AUX", 62.0, 26.0, 4, MX125_PITCH,
        horizontal=False)
    component_pads["J6"] = add_connector(
        board, pcbnew,
        {"1": nets["pvdf_cmp_aux_l"], "2": nets["pvdf_cmp_aux_r"]},
        "J6", "MX1.25_PVDF_CMP_AUX_DNP", 69.0, 26.0, 2, MX125_PITCH,
        horizontal=False)

    # All user-facing controls stay on a removable daughter board.  A single
    # keyed 1.25 mm locking harness carries the complete GPIO budget; the
    # daughter board owns the buttons, OLED reserve, LEDs, buzzer and speaker
    # connector so the mother board can remain inside the compact cavity.
    component_pads["J7"] = add_connector(
        board, pcbnew,
        {"1": nets["3v3"], "2": nets["gnd"], "3": nets["ui_sda"],
         "4": nets["ui_scl"], "5": nets["ui_btn_start"],
         "6": nets["ui_btn_mode"], "7": nets["ui_buzzer"],
         "8": nets["ui_spk_bclk"], "9": nets["ui_spk_ws"],
         "10": nets["ui_spk_dout"], "11": nets["ui_led_status"],
         "12": nets["ui_led_battery"]},
        "J7", "MX1.25_UI_PANEL_LOCK_12P", 31.0, 29.0, 12, MX125_PITCH,
        horizontal=True)

    for ref, net_name, x, y in (
        ("TP1", "bat_p", 62.0, 20.0), ("TP2", "bat_sense", 68.0, 20.0),
        ("TP3", "sys_5v", 58.0, 18.0), ("TP4", "3v3", 78.0, 24.0),
        ("TP5", "gnd", 74.0, 22.0), ("TP6", "carrier_irq_n", 76.0, 21.0),
        ("TP7", "sensor_fused", 72.0, 12.0),
    ):
        add_test_point(board, pcbnew, nets[net_name], ref, x, y)

    # No copper tracks are generated in this pass.  KiCad airwires are the
    # intentional hand-off between placement/net assignment and the reviewed
    # power/signal routing pass; this keeps a false DRC-clean result out of the
    # first-article artifact.

    # Labels make the review board useful even before the remaining airwires
    # are routed.  Keep these on Dwgs.User to avoid implying copper.
    add_text(board, pcbnew, "PINGPANG ESP32-S3 / 1S POWER v0.2", 45, 1.2,
             1.0, pcbnew.Dwgs_User, 0.18)
    add_text(board, pcbnew, "J4: 3V3 GND SCK MOSI MISO CS IRQ RESET", 68, 33.0,
             0.62, pcbnew.Dwgs_User, 0.12)
    add_text(board, pcbnew, "J7: UI LOCK 12P", 39, 33.0,
             0.62, pcbnew.Dwgs_User, 0.12)
    add_text(board, pcbnew, "J8: SENSOR_RAIL", 52, 21.2,
             0.62, pcbnew.Dwgs_User, 0.12)
    add_text(board, pcbnew, "J3: EXT 10-30V ONLY", 83, 10.4, 0.62,
             pcbnew.Dwgs_User, 0.12)
    add_text(board, pcbnew, "BAT: PROTECTED 1S", 83, 1.2, 0.62,
             pcbnew.Dwgs_User, 0.12)

    # A first-article common-ground plane is safe to generate automatically;
    # all signal/power routing remains an explicit later review step.
    # Via-in-pad is used only for the two exposed ground pads so the plane is
    # not dependent on a narrow top-layer thermal spoke between power pads.
    add_ground_via(board, pcbnew, nets["gnd"], 47.0, 7.5)
    add_ground_via(board, pcbnew, nets["gnd"], 67.0, 7.5)
    add_ground_zone(board, pcbnew, nets["gnd"])

    return board


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    import pcbnew

    board = build_board()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    board.Save(str(args.output))
    print(f"WROTE {args.output}")
    print(f"FOOTPRINTS {len(board.GetFootprints())}")
    print(f"TRACKS {len(board.GetTracks())}")
    print(f"ZONES {board.GetAreaCount()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
