#!/usr/bin/env python3
"""Generate the connectorized first-article daughter boards.

The boards intentionally keep copper routing at the first-article review
gate, but they are real KiCad boards.  Board-specific connector/IC models and
the PCB-mounted panel parts (buttons, LEDs and USB-C) stay attached to the
board export, so the KiCad board STL is the single source for those solids.
Off-board, wire-connected parts such as the screen and speaker are mounted by
the SCAD assembly.  Board size, connector count and mounting-hole datums
remain machine checked before the reviewed copper-routing pass.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MM = 1_000_000
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE


MX125_PITCH = 1.25
# The exact purchased "MX1.25" manufacturer/SKU is not present in the
# repository yet.  These installed KiCad JST-GH models are used only as the
# reviewable 1.25 mm keyed-locking envelope; the footprint contract and pad
# pitch stay at 1.25 mm so a later exact MX1.25 model can be swapped in.
MODEL_MX125_1X12 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM12B-GHS-TB_1x12-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X10 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM10B-GHS-TB_1x10-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X8 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM08B-GHS-TB_1x08-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X7 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM07B-GHS-TB_1x07-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X5 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X4 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X3 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal.step"
MODEL_MX125_1X2 = "${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal.step"
MODEL_SOIC8 = "${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/SOIC-8_3.9x4.9mm_P1.27mm.step"
MODEL_SOIC4 = "${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/SOIC-4_4.55x2.6mm_P1.27mm.step"
MODEL_0603 = "${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0603_1608Metric.step"
MODEL_PANEL_BUTTON = "${KICAD10_3DMODEL_DIR}/Button_Switch_SMD.3dshapes/SW_SPST_TS-1088-xR020.step"
MODEL_PANEL_LED = "${KICAD10_3DMODEL_DIR}/LED_SMD.3dshapes/LED_0603_1608Metric.step"
# The UI PCB is installed vertically behind the y+ service panel.  The
# available 16-pin GCT top-mount library model is a horizontal receptacle, so
# its source +Y mating axis is rotated +90 degrees about footprint X into the
# vertical footprint's +Z board normal.  The complete UI board is then
# installed with -90 degrees about X, carrying that opening through the y+
# panel.  The model remains attached to the KiCad footprint and is therefore
# included in the board export, not SCAD.
MODEL_USB_C_PANEL = "${KICAD10_3DMODEL_DIR}/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step"
KICAD_FOOTPRINT_ROOT = Path(
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
)
LIB_PANEL_BUTTON = KICAD_FOOTPRINT_ROOT / "Button_Switch_SMD.pretty"
LIB_PANEL_LED = KICAD_FOOTPRINT_ROOT / "LED_SMD.pretty"
LIB_USB_C_PANEL = KICAD_FOOTPRINT_ROOT / "Connector_USB.pretty"


def add_3d_model(pcbnew, fp, filename: str, rotation=(0.0, 0.0, 0.0)):
    model = pcbnew.FP_3DMODEL()
    model.m_Filename = filename
    model.m_Offset = pcbnew.VECTOR3D(0.0, 0.0, 0.0)
    model.m_Rotation = pcbnew.VECTOR3D(*rotation)
    model.m_Scale = pcbnew.VECTOR3D(1.0, 1.0, 1.0)
    model.m_Opacity = 1.0
    model.m_Show = True
    fp.Add3DModel(model)
    return model


def connector_model(count: int, pitch: float, horizontal: bool):
    models = {
        12: MODEL_MX125_1X12,
        10: MODEL_MX125_1X10,
        8: MODEL_MX125_1X8,
        7: MODEL_MX125_1X7,
        5: MODEL_MX125_1X5,
        4: MODEL_MX125_1X4,
        3: MODEL_MX125_1X3,
        2: MODEL_MX125_1X2,
    }
    if abs(pitch - MX125_PITCH) >= 0.02:
        return None
    filename = models.get(count)
    if filename is None:
        return None
    return filename, (0.0, 0.0, 90.0 if not horizontal else 0.0)


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


def add_text(board, pcbnew, text: str, x: float, y: float,
             size: float = 0.8, layer=None, thickness: float = 0.14):
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
                b: tuple[float, float], width: float = 0.12):
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(layer)
    shape.SetStart(xy(pcbnew, *a))
    shape.SetEnd(xy(pcbnew, *b))
    shape.SetWidth(int(round(width * MM)))
    board.Add(shape)
    return shape


def add_rect(board, pcbnew, layer, cx: float, cy: float, w: float, h: float,
             width: float = 0.10):
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = cy - h / 2, cy + h / 2
    for a, b in (
        ((x0, y0), (x1, y0)),
        ((x1, y0), (x1, y1)),
        ((x1, y1), (x0, y1)),
        ((x0, y1), (x0, y0)),
    ):
        add_segment(board, pcbnew, layer, a, b, width)


def add_board_outline(board, pcbnew, width: float, height: float):
    add_rect(board, pcbnew, pcbnew.Edge_Cuts, width / 2, height / 2,
             width, height, 0.05)


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


def load_library_fp(board, pcbnew, library: Path, name: str, ref: str,
                    value: str, x: float, y: float, rotation: float = 0.0):
    """Add an installed KiCad footprint without replacing its 3D model.

    The library footprint is deliberately loaded instead of drawing a generic
    rectangle.  That keeps the copper land pattern, courtyard, mounting
    holes, and the purchased-part model tied together for the mechanical
    review.  ``x``/``y`` is the footprint origin used by the library; callers
    compensate for off-centre origins when they need a panel datum.
    """
    if not library.is_dir():
        raise RuntimeError(f"KiCad footprint library is missing: {library}")
    plugin_type = pcbnew.PCB_IO_MGR.GuessPluginTypeFromLibPath(str(library))
    plugin = pcbnew.PCB_IO_MGR.FindPlugin(plugin_type)
    fp = plugin.FootprintLoad(str(library), name)
    if fp is None:
        raise RuntimeError(f"cannot load KiCad footprint {library.name}:{name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(xy(pcbnew, x, y))
    fp.SetOrientation(pcbnew.EDA_ANGLE(rotation, pcbnew.DEGREES_T))
    # Keep references readable in the board preview while leaving the
    # installed library's fabrication/courtyard graphics intact.
    fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Value().SetLayer(pcbnew.F_Fab)
    # The direct panel parts are identified by their value/reference in the
    # fabrication view; their library silkscreen outlines are too close to
    # the neighbouring cable lands for this compact review board.
    for item in fp.GraphicalItems():
        if item.GetLayer() == pcbnew.F_SilkS:
            item.SetLayer(pcbnew.F_Fab)
    board.Add(fp)
    return fp


def assign_pad_nets(fp, nets: dict[str, object], mapping: dict[str, str]):
    """Assign named library pads, including duplicated USB-C pad names."""
    for pad in fp.Pads():
        number = str(pad.GetPadName())
        net_name = mapping.get(number)
        if net_name is not None:
            pad.SetNet(nets[net_name])


def add_panel_button(board, pcbnew, nets: dict[str, object], ref: str,
                     value: str, center_x: float, center_y: float,
                     signal_net: str):
    # TS-1088-xR020 is a 3.9 x 3.0 x 2.0 mm, two-pad SMD tactile switch.  Its
    # footprint origin is the centre of the actuator body, so the board datum
    # and the printed button plunger use the same x/y coordinate directly.
    fp = load_library_fp(
        board, pcbnew, LIB_PANEL_BUTTON, "SW_SPST_TS-1088-xR020", ref, value,
        center_x, center_y,
    )
    assign_pad_nets(fp, nets, {"1": signal_net, "2": "gnd"})
    return fp


def add_panel_led(board, pcbnew, nets: dict[str, object], ref: str,
                  value: str, center_x: float, center_y: float,
                  signal_net: str, model: str):
    # The 0603 footprint origin is the optical/body centre.  Keep the two
    # existing single-colour LED nets and expose them through short, straight
    # faceplate bores; a WS2812B/RGB replacement would require new data/RGB
    # wiring, which is deliberately outside this placement-only revision.
    fp = load_library_fp(
        board, pcbnew, LIB_PANEL_LED, "LED_0603_1608Metric", ref, value,
        center_x, center_y,
    )
    assign_pad_nets(fp, nets, {"1": signal_net, "2": "gnd"})
    fp.Models().clear()
    add_3d_model(pcbnew, fp, model)
    return fp


def add_panel_usb_c(board, pcbnew, nets: dict[str, object], ref: str,
                    value: str, center_x: float, center_y: float):
    # The electrical footprint is vertical and stays at 0 degrees.  The
    # substituted GCT model is rotated +90 degrees about footprint X so its
    # actual +Y opening points along the footprint's +Z normal.  When the
    # entire UI board is installed on the y+ wall, that normal becomes +Y.
    fp = load_library_fp(
        board, pcbnew, LIB_USB_C_PANEL,
        "USB_C_Receptacle_G-Switch_GT-USB-7051x",
        ref, value, center_x, center_y, rotation=0.0,
    )
    # The footprint's installed G-Switch model is not present in this KiCad
    # library package. Use the available 16-pin KiCad library model explicitly
    # so board export and enclosure fit share the same panel-normal mating
    # axis instead of silently dropping the connector model.
    fp.Models().clear()
    add_3d_model(pcbnew, fp, MODEL_USB_C_PANEL, rotation=(90.0, 0.0, 0.0))
    assign_pad_nets(fp, nets, {
        "A1": "gnd", "A4": "usb_vbus", "A5": "cc1", "A6": "usb_dp",
        "A7": "usb_dn", "A8": "usb_sbu2", "A9": "usb_vbus",
        "A12": "gnd", "B1": "gnd", "B4": "usb_vbus", "B5": "cc2",
        "B6": "usb_dp", "B7": "usb_dn", "B8": "usb_sbu1",
        "B9": "usb_vbus", "B12": "gnd", "SH": "gnd",
    })
    # Keep the 0.79 mm vertical-receptacle pitch while using a 0.65 mm review pad.  It
    # leaves the board's normal 0.20 mm copper-clearance rule intact and still
    # gives a 0.125 mm annulus around the 0.40 mm plated drill.  The final
    # fabrication land is a first-article datasheet check, not a hidden
    # relaxation of the whole board's DRC.
    for pad in fp.Pads():
        name = str(pad.GetPadName())
        if name not in {"", "SH"}:
            pad.SetSize(xy(pcbnew, 0.65, 0.65))
        if pad.GetNetname() == "gnd":
            pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
    return fp


def add_smd_pad(pcbnew, fp, number: str, x: float, y: float,
                w: float, h: float, net=None):
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


def add_pth_pad(pcbnew, fp, number: str, x: float, y: float,
                diameter: float, drill: float, net=None):
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


def add_mount_hole(board, pcbnew, ref: str, x: float, y: float):
    fp = new_fp(board, pcbnew, ref, "M2.5 NPTH", x, y,
                pcbnew.FP_THROUGH_HOLE)
    add_npth_pad(pcbnew, fp, 0, 0, 4.8, 2.8)
    board.Add(fp)
    add_rect(board, pcbnew, pcbnew.F_Fab, x, y, 5.5, 5.5, 0.10)


def add_connector(board, pcbnew, pads: dict[str, object], ref: str,
                  value: str, x: float, y: float, count: int,
                  pitch: float = MX125_PITCH, horizontal: bool = False):
    if abs(pitch - MX125_PITCH) < 0.02:
        # Use the installed 1.25 mm keyed-locking footprint geometry for the
        # review board.  The actual purchased MX1.25 SKU can replace the
        # model/land pattern later without changing the channel topology.
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
        # Keep the review lands inside the compact board edge.  The exact
        # purchased MX1.25 land pattern is still a later SKU-freeze item.
        mount_size = (1.0, 2.2) if horizontal else (2.2, 1.0)
        for px, py in mount_xy:
            add_smd_pad(pcbnew, fp, "MP", px, py,
                        mount_size[0], mount_size[1])
        board.Add(fp)
        w, h = (span + 3.7, 5.3) if horizontal else (5.3, span + 3.7)
        add_rect(board, pcbnew, pcbnew.F_Fab, x, y, w, h, 0.10)
        add_text(board, pcbnew, ref, x, y - h / 2 - 0.7, 0.65)
        model_info = connector_model(count, pitch, horizontal)
        if model_info:
            add_3d_model(pcbnew, fp, *model_info)
        return fp

    fp = new_fp(board, pcbnew, ref, value, x, y, pcbnew.FP_THROUGH_HOLE)
    pad_diameter = min(1.7, max(0.8, pitch - 0.30))
    drill_diameter = min(0.9, pad_diameter - 0.30)
    for index in range(count):
        offset = (index - (count - 1) / 2) * pitch
        px, py = (offset, 0) if horizontal else (0, offset)
        number = str(index + 1)
        add_pth_pad(pcbnew, fp, number, px, py, pad_diameter, drill_diameter,
                    pads.get(number))
    board.Add(fp)
    w, h = ((count - 1) * pitch + 3.0, 3.4) if horizontal else (
        3.4, (count - 1) * pitch + 3.0)
    add_rect(board, pcbnew, pcbnew.F_Fab, x, y, w, h, 0.10)
    add_text(board, pcbnew, ref, x, y - h / 2 - 0.7, 0.65)
    model_info = connector_model(count, pitch, horizontal)
    if model_info:
        add_3d_model(pcbnew, fp, *model_info)
    return fp


def add_chip(board, pcbnew, nets: dict[str, object], ref: str, value: str,
             x: float, y: float, pad_xy: list[tuple[str, float, float]],
             body: tuple[float, float] = (5.0, 3.0),
             pad_size: tuple[float, float] = (1.0, 1.0),
             model: str | None = None):
    fp = new_fp(board, pcbnew, ref, value, x, y)
    for number, px, py in pad_xy:
        add_smd_pad(pcbnew, fp, number, px, py, pad_size[0], pad_size[1],
                    nets.get(number))
    board.Add(fp)
    add_rect(board, pcbnew, pcbnew.F_Fab, x, y, body[0], body[1], 0.10)
    add_text(board, pcbnew, ref, x, y - body[1] / 2 - 0.65, 0.60)
    if model is None:
        model = MODEL_SOIC8 if len(pad_xy) >= 4 else MODEL_0603
    add_3d_model(pcbnew, fp, model)
    return fp


def add_two_pad(board, pcbnew, nets: dict[str, object], ref: str,
                value: str, x: float, y: float, horizontal: bool = True):
    if horizontal:
        pad_xy = [("1", -1.25, 0), ("2", 1.25, 0)]
    else:
        pad_xy = [("1", 0, -1.25), ("2", 0, 1.25)]
    return add_chip(board, pcbnew, nets, ref, value, x, y, pad_xy,
                    body=(3.2, 2.0))


def add_ground_zone(board, pcbnew, net, width: float, height: float):
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
    for point in ((0.6, 0.6), (width - 0.6, 0.6),
                  (width - 0.6, height - 0.6), (0.6, height - 0.6)):
        zone.AppendCorner(xy(pcbnew, *point), -1)
    board.Add(zone)
    return zone


def make_board(pcbnew, title: str, generator: str, width: float,
               height: float, net_names: tuple[str, ...]):
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    board.SetGenerator(generator)
    board.GetTitleBlock().SetTitle(title)
    board.GetTitleBlock().SetComment(1, "Placement/net assignment first article; not fabrication release")
    board.GetTitleBlock().SetComment(2, "All field wiring is connectorized; no flying-wire solder joints")
    board.GetTitleBlock().SetComment(3, "Board envelope is a mechanical fit reference")
    nets = {name: ensure_net(board, pcbnew, name) for name in net_names}
    add_board_outline(board, pcbnew, width, height)
    return board, nets


def add_four_mounts(board, pcbnew, width: float, height: float,
                    inset: float = 4.5):
    for ref, x, y in (
        ("H1", inset, inset),
        ("H2", width - inset, inset),
        ("H3", inset, height - inset),
        ("H4", width - inset, height - inset),
    ):
        add_mount_hole(board, pcbnew, ref, x, y)


def build_receiver(pcbnew):
    width, height = 80.0, 32.0
    net_names = ["gnd", "3v3", "sensor_v", "sensor_gnd",
                 "carrier_sck", "carrier_mosi", "carrier_miso",
                 "carrier_cs_n", "carrier_irq_n", "carrier_reset_n"]
    for index in range(10):
        net_names.extend((f"rx{index:02d}_v", f"rx{index:02d}_gnd",
                          f"rx{index:02d}_sig"))
    board, nets = make_board(
        pcbnew,
        "Pingpang M6 receiver carrier / 10 channel v0.2",
        "Pingpang SmartGear M6 receiver carrier v0.2",
        width, height, tuple(net_names),
    )
    add_four_mounts(board, pcbnew, width, height, inset=4.5)

    # The optical heads keep their 20 mm pitch in the mechanical M6 body.  At
    # this board boundary their ten 3-wire harnesses have already converged,
    # so the MX1.25 sockets are grouped as two rows of five.  PCB dimensions
    # therefore no longer encode the optical head spacing.
    channel_x = (12.0, 24.0, 36.0, 48.0, 60.0)
    for index in range(10):
        row, column = divmod(index, 5)
        x = channel_x[column]
        connector_y = 5.0 if row == 0 else 27.0
        opto_y = 12.0 if row == 0 else 20.0
        add_connector(
            board, pcbnew,
            {"1": nets[f"rx{index:02d}_v"],
             "2": nets[f"rx{index:02d}_gnd"],
             "3": nets[f"rx{index:02d}_sig"]},
            f"J_RX{index:02d}", "MX1.25_LOCK_3P_RX", x, connector_y,
            3, MX125_PITCH,
            horizontal=True,
        )
        # Four-pad optocoupler placeholder: signal, isolated ground, logic
        # supply, and a spare output/test pad.  The exact optocoupler and
        # resistor current are intentionally frozen during schematic review.
        add_chip(
            board, pcbnew, {
                "1": nets[f"rx{index:02d}_sig"],
                "2": nets[f"rx{index:02d}_gnd"],
                "3": nets["3v3"],
                "4": nets["gnd"],
            }, f"U_OP{index:02d}", "OPTO_PLACEHOLDER", x, opto_y,
            [("1", -3.25, -0.635), ("2", -3.25, 0.635),
             ("3", 3.25, 0.635), ("4", 3.25, -0.635)],
            body=(4.55, 2.6), pad_size=(1.6, 0.55),
            model=MODEL_SOIC4,
        )

    # Keep the host, sensor rail and local MCU in the open right-hand service
    # pocket, away from the ten channel sockets.
    add_connector(
        board, pcbnew,
        {"1": nets["3v3"], "2": nets["gnd"],
         "3": nets["carrier_sck"], "4": nets["carrier_mosi"],
         "5": nets["carrier_miso"], "6": nets["carrier_cs_n"],
         "7": nets["carrier_irq_n"], "8": nets["carrier_reset_n"]},
        "J_HOST", "MX1.25_MOTHER_HOST_LOCK_8P", 67.0, 18.0, 8,
        MX125_PITCH,
        horizontal=True,
    )
    add_connector(
        board, pcbnew,
        {"1": nets["sensor_v"], "2": nets["sensor_gnd"]},
        "J_PWR", "MX1.25_SENSOR_RAIL_LOCK_2P", 76.0, 13.0, 2,
        MX125_PITCH,
        horizontal=False,
    )
    add_chip(
        board, pcbnew, {
            "1": nets["carrier_sck"], "2": nets["carrier_mosi"],
            "3": nets["carrier_miso"], "4": nets["carrier_cs_n"],
            "5": nets["carrier_irq_n"], "6": nets["carrier_reset_n"],
            "7": nets["3v3"], "8": nets["gnd"],
        }, "U_MCU", "STM32G031_PLACEHOLDER", 68.0, 25.0,
        [("1", -2.475, -1.905), ("2", -2.475, -0.635),
         ("3", -2.475, 0.635), ("4", -2.475, 1.905),
         ("5", 2.475, 1.905), ("6", 2.475, 0.635),
         ("7", 2.475, -0.635), ("8", 2.475, -1.905)],
        body=(3.9, 4.9), pad_size=(1.95, 0.6),
    )
    add_text(board, pcbnew, "10x RX / 3-WIRE MX1.25", 39, 31.0, 0.62)
    add_text(board, pcbnew, "BOARD PITCH != OPTICAL 20 mm", 39, 31.7, 0.50)
    add_ground_zone(board, pcbnew, nets["gnd"], width, height)
    return board, width, height


def build_emitter_power(pcbnew):
    width, height = 68.0, 32.0
    net_names = ["gnd", "bat_p", "bat_gnd", "ext_tx_in", "ext_tx_gnd",
                 "tx_rail", "tx_gnd", "tx_enable", "charge_status"]
    for index in range(10):
        net_names.extend((f"tx{index:02d}_v", f"tx{index:02d}_gnd"))
    board, nets = make_board(
        pcbnew,
        "Pingpang emitter internal power daughter v0.2",
        "Pingpang SmartGear emitter power daughter v0.2",
        width, height, tuple(net_names),
    )
    add_four_mounts(board, pcbnew, width, height, inset=3.5)
    add_connector(
        board, pcbnew,
        {"1": nets["bat_p"], "2": nets["bat_gnd"]},
        "J_BAT", "MX1.25_PROTECTED_1S_LOCK_2P", 9.0, 8.0, 2,
        MX125_PITCH,
        horizontal=False,
    )
    add_connector(
        board, pcbnew,
        {"1": nets["ext_tx_in"], "2": nets["ext_tx_gnd"]},
        "J_EXT", "MX1.25_EXT_TX_10-30V_2P_CURRENT_GATE", 21.0, 5.0, 2,
        MX125_PITCH,
        horizontal=True,
    )
    for connector_ref, first_index, x, y in (
        ("J_TX_A", 0, 52.0, 5.0),
        ("J_TX_B", 5, 52.0, 27.0),
    ):
        add_connector(
            board, pcbnew,
            {str(2 * local_index + 1): nets[f"tx{first_index + local_index:02d}_v"]
             for local_index in range(5)}
            | {str(2 * local_index + 2): nets[f"tx{first_index + local_index:02d}_gnd"]
               for local_index in range(5)},
            connector_ref, f"MX1.25_TX_{'A' if first_index == 0 else 'B'}_10P",
            x, y, 10, MX125_PITCH, horizontal=True,
        )
    add_two_pad(board, pcbnew, {
        "1": nets["ext_tx_in"], "2": nets["tx_rail"]},
        "F_TX", "PTC_OR_FUSE", 29.0, 9.0)
    add_two_pad(board, pcbnew, {
        "1": nets["tx_rail"], "2": nets["ext_tx_gnd"]},
        "D_TVS", "TVS_BY_MODULE", 35.0, 9.0)
    add_chip(
        board, pcbnew, {
            "1": nets["bat_p"], "2": nets["bat_gnd"],
            "3": nets["tx_rail"], "4": nets["tx_gnd"],
            "5": nets["tx_enable"], "6": nets["charge_status"],
        }, "U_BOOST", "TX_BOOST_CURRENT_RATED_PLACEHOLDER", 34.0, 19.0,
        [("1", -4.0, -2.0), ("2", -4.0, 2.0), ("3", -1.3, -2.0),
         ("4", -1.3, 2.0), ("5", 1.3, -2.0), ("6", 1.3, 2.0)],
        body=(10.0, 8.0), pad_size=(1.2, 1.0),
    )
    add_text(board, pcbnew, "BATTERY DEFAULT / EXT FALLBACK", 34, 2.0, 0.62)
    add_text(board, pcbnew, "TX00..TX04 / TX05..TX09 2-WIRE", 51, 31.0, 0.58)
    add_ground_zone(board, pcbnew, nets["gnd"], width, height)
    return board, width, height


def build_ui(pcbnew):
    width, height = 58.0, 28.0
    net_names = ["gnd", "3v3", "ui_sda", "ui_scl", "ui_btn_start",
                 "ui_btn_mode", "ui_buzzer", "ui_spk_bclk", "ui_spk_ws",
                 "ui_spk_dout", "ui_led_status", "ui_led_battery",
                 "usb_vbus", "usb_dp", "usb_dn", "cc1", "cc2",
                 "usb_sbu1", "usb_sbu2"]
    board, nets = make_board(
        pcbnew,
        "Pingpang sealed UI daughter / direct controls USB-C v0.2",
        "Pingpang SmartGear UI daughter v0.2",
        width, height, tuple(net_names),
    )
    add_four_mounts(board, pcbnew, width, height, inset=3.5)
    add_connector(
        board, pcbnew,
        {"1": nets["3v3"], "2": nets["gnd"], "3": nets["ui_sda"],
         "4": nets["ui_scl"], "5": nets["ui_btn_start"],
         "6": nets["ui_btn_mode"], "7": nets["ui_buzzer"],
         "8": nets["ui_spk_bclk"], "9": nets["ui_spk_ws"],
         "10": nets["ui_spk_dout"], "11": nets["ui_led_status"],
         "12": nets["ui_led_battery"]},
        # Keep the 12-pin mother-board cable on the lower interior band.  The
        # left column is reserved for the two real tactile switches so their
        # actuator bodies and panel bores cannot be hidden under a connector.
        # Shift the keyed harness body 2 mm left.  The old centre put its
        # left mechanical pad under the right pad of the MODE tactile switch
        # once the real 3.9 x 3.0 mm SMD footprint was loaded.  This is a
        # placement-only correction: no PCB copper is routed or changed.
        "J_MOTHER", "MX1.25_MOTHER_UI_LOCK_12P", 18.0, 17.0, 12,
        MX125_PITCH,
        horizontal=True,
    )
    add_connector(
        board, pcbnew,
        {"1": nets["3v3"], "2": nets["gnd"], "3": nets["ui_sda"],
         "4": nets["ui_scl"]},
        "J_OLED", "MX1.25_I2C_OLED_FPC_4P", 26.0, 8.0, 4,
        MX125_PITCH,
        horizontal=False,
    )
    add_connector(
        board, pcbnew,
        {"1": nets["ui_spk_bclk"], "2": nets["ui_spk_ws"],
         "3": nets["ui_spk_dout"], "4": nets["3v3"], "5": nets["gnd"]},
        "J_SPK", "MX1.25_I2S_SPEAKER_LOCK_5P", 47.0, 8.0, 5,
        MX125_PITCH,
        horizontal=True,
    )
    add_connector(
        board, pcbnew,
        {"1": nets["ui_buzzer"], "2": nets["gnd"]},
        "J_BUZ", "MX1.25_BUZZER_LOCK_2P", 38.0, 16.0, 2,
        MX125_PITCH,
        horizontal=True,
    )
    # These are the actual panel-contact parts.  Their centre datums are
    # shared with net_stand.scad and the electronics browser; no separate
    # generic connector or light-pipe placeholder is allowed here.
    add_panel_button(
        board, pcbnew, nets, "SW_START", "SEALED_SMD_TACTILE_START", 10.0, 8.0,
        "ui_btn_start",
    )
    add_panel_button(
        board, pcbnew, nets, "SW_MODE", "SEALED_SMD_TACTILE_MODE", 10.0, 20.0,
        "ui_btn_mode",
    )
    add_panel_led(
        board, pcbnew, nets, "D_STATUS", "LED_STATUS_0603_GREEN", 29.0, 3.0,
        "ui_led_status", MODEL_PANEL_LED,
    )
    add_panel_led(
        board, pcbnew, nets, "D_BAT", "LED_BATTERY_0603_YELLOW", 32.0, 25.0,
        "ui_led_battery", MODEL_PANEL_LED,
    )
    add_panel_usb_c(
        board, pcbnew, nets, "J_USB_PANEL", "USB-C_VERTICAL_16P_DIRECT",
        47.0, 26.0,
    )
    add_text(board, pcbnew, "SEALED PANEL: OLED CABLE / DIRECT BTN / LED / USB-C", 29, 2.0, 0.60)
    add_text(board, pcbnew, "USB-C 16P / PORT TO y+ BEZEL", 47, 27.0, 0.54)
    add_ground_zone(board, pcbnew, nets["gnd"], width, height)
    return board, width, height


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    import pcbnew

    builders = (
        ("m6-receiver-carrier-v0.2.kicad_pcb", build_receiver),
        ("emitter-power-v0.2.kicad_pcb", build_emitter_power),
        ("ui-panel-v0.2.kicad_pcb", build_ui),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, builder in builders:
        board, width, height = builder(pcbnew)
        output = args.output_dir / filename
        board.Save(str(output))
        print(f"WROTE {output}")
        print(f"  SIZE {width:.1f} x {height:.1f} mm")
        print(f"  FOOTPRINTS {len(board.GetFootprints())}")
        print(f"  ZONES {board.GetAreaCount()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
