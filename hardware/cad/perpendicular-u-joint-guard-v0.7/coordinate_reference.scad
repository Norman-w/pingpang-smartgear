// Coordinate reference only.  The mechanical baseline is v0.7; this file
// adds colored axes and labels without changing the v0.7 printable geometry.

use <perpendicular_double_u_guard.scad>;

$fn = 32;

module arrow_x(x0, x1, y, z, c) {
    color(c) {
        translate([x0, y, z])
            rotate([0, 90, 0]) cylinder(d = 1.8, h = x1 - x0);
        translate([x1, y, z])
            rotate([0, 90, 0]) cylinder(r1 = 4.0, r2 = 0, h = 8.0);
    }
}

module arrow_y(y0, y1, x, z, c) {
    color(c) {
        translate([x, y0, z])
            rotate([-90, 0, 0]) cylinder(d = 1.8, h = y1 - y0);
        translate([x, y1, z])
            rotate([-90, 0, 0]) cylinder(r1 = 4.0, r2 = 0, h = 8.0);
    }
}

module arrow_z(z0, z1, x, y, c) {
    color(c) {
        translate([x, y, z0])
            cylinder(d = 1.8, h = z1 - z0);
        translate([x, y, z1])
            cylinder(r1 = 4.0, r2 = 0, h = 8.0);
    }
}

module top_label(x, y, z, value, c) {
    color(c)
        translate([x, y, z])
            linear_extrude(height = 0.6)
                text(value, size = 5, halign = "center", valign = "center");
}

module coordinate_reference() {
    // The restored pre-annotation baseline.
    assembly_iso();

    // X: barrier long direction / upper gray tube axis.
    arrow_x(-72, 72, 0, 36, [1.0, 0.65, 0.05]);
    top_label(57, 0, 36, "X LONG", [1.0, 0.65, 0.05]);

    // Y: front-to-back direction / lower blue foot axis.
    arrow_y(-72, 72, 0, -28, [0.05, 0.75, 1.0]);
    top_label(0, 54, -28, "Y + FRONT", [0.05, 0.75, 1.0]);

    // Z: vertical direction / screw axis.
    arrow_z(-35, 58, 35, -35, [0.15, 0.95, 0.25]);
    top_label(35, -35, 61, "Z UP / SCREW", [0.15, 0.95, 0.25]);
}

coordinate_reference();
