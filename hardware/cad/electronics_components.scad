// Canonical physical electronics envelopes for the net-stand assembly.
//
// Units: mm.  Every module is a reusable local-frame model.  The origin is
// the component's mechanical datum (usually the PCB land centre), and the
// positive local z direction is the service-facing direction.  Assemblies
// must place these modules with translate()/rotate(); do not copy their
// geometry into a second module.
//
// These are only the mechanical envelopes for purchased parts that are not
// soldered to a PCB.  The button, LED and USB-C bodies are deliberately not
// duplicated here: their KiCad footprint models are exported with the board
// and are the authoritative solids used by the assembly collision checks.
// Exact vendor dimensions, electrical ratings, and first-article fit still
// require the selected part datasheets and a physical sample.

module electronics_rounded_prism_positive(length_x, width_y, height_z,
                                          corner_r = 1.0, fn = 32) {
    // A hull of four vertical cylinders gives a printable rounded XY outline
    // without changing the nominal X/Y envelope.  The vertical faces remain
    // planar, which is appropriate for a pouch cell and small enclosures.
    assert(length_x > 2 * corner_r && width_y > 2 * corner_r &&
           height_z > 0 && corner_r > 0,
           "electronics rounded prism dimensions are invalid");
    hull()
        for (x = [corner_r, length_x - corner_r])
            for (y = [corner_r, width_y - corner_r])
                translate([x, y, 0])
                    cylinder(r = corner_r, h = height_z, $fn = fn);
}

module electronics_battery_model_positive(length_x = 65, width_y = 30,
                                           thickness_z = 7,
                                           corner_r = 1.5) {
    // Protected 1S pouch-cell envelope.  The small terminal tab is kept
    // inside the model's X/Y envelope so rails can be checked against the
    // whole bought part without inventing a second battery solid.
    color("orange", 0.82)
        electronics_rounded_prism_positive(
            length_x, width_y, thickness_z, corner_r);
}

module electronics_screen_model_positive(length_x = 25, width_y = 14,
                                          thickness_z = 1.2,
                                          corner_r = 1.0) {
    // Cable-fed OLED/LCD module.  The glass is a thin inset layer on the
    // service-facing face; the body remains one canonical screen instance.
    assert(thickness_z > 0.3 && length_x > 2 && width_y > 2,
           "screen envelope dimensions are invalid");
    color("black", 0.86)
        electronics_rounded_prism_positive(
            length_x, width_y, thickness_z, corner_r);
    color("slategray", 0.70)
        translate([1.0, 1.0, thickness_z - 0.08])
            cube([length_x - 2.0, width_y - 2.0, 0.16]);
}

module electronics_speaker_model_positive(diameter = 16, height_z = 2.2,
                                           diaphragm_d = 12) {
    // Small round speaker body behind the acoustic opening.  The connector
    // remains on the KiCad UI board; this module is the separate loudspeaker
    // body that is mounted once at each world-space speaker location.
    assert(diameter > 0 && height_z > 0 && diaphragm_d > 0 &&
           diaphragm_d < diameter, "speaker envelope dimensions are invalid");
    color("darkslategray", 0.90)
        cylinder(d = diameter, h = height_z, $fn = 64);
    color("black", 0.76)
        translate([0, 0, height_z - 0.12])
            cylinder(d = diaphragm_d, h = 0.14, $fn = 64);
}
