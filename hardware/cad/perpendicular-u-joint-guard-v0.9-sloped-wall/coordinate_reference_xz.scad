// Candidate v0.9 actual OpenSCAD XZ coordinate review.
// The gray upper tube is intentionally omitted from this view.

use <candidate_sloped_wall.scad>;

$fn = 48;

axis_x = [0.95, 0.60, 0.05];
axis_y = [0.05, 0.60, 0.95];
axis_z = [0.10, 0.75, 0.25];
label_color = [0.08, 0.10, 0.12];

module arrow_x(x0, x1, y, z, c, shaft_d = 1.2, head_d = 5.0, head_h = 8.0) {
    color(c) {
        translate([x0, y, z])
            rotate([0, 90, 0])
                cylinder(d = shaft_d, h = x1 - x0);
        translate([x1, y, z])
            rotate([0, 90, 0])
                cylinder(r1 = head_d / 2, r2 = 0, h = head_h);
    }
}

module arrow_z(z0, z1, x, y, c, shaft_d = 1.2, head_d = 5.0, head_h = 8.0) {
    color(c) {
        translate([x, y, z0])
            cylinder(d = shaft_d, h = z1 - z0);
        translate([x, y, z1])
            cylinder(r1 = head_d / 2, r2 = 0, h = head_h);
    }
}

module y_dot(x, y, z, c) {
    color(c) {
        translate([x, y, z])
            rotate([90, 0, 0])
                cylinder(d = 9, h = 1.2, center = true);
        translate([x, y - 0.8, z])
            rotate([90, 0, 0])
                cylinder(d = 2.8, h = 1.8, center = true);
    }
}

module y_cross(x, y, z, c) {
    color(c)
        translate([x, y, z])
            rotate([90, 0, 0])
                cylinder(d = 10, h = 1.2, center = true, $fn = 4);
}

module text_xz(value, x, y, z, size = 5, c = label_color, halign = "left") {
    color(c)
        translate([x, y, z])
            rotate([90, 0, 0])
                linear_extrude(height = 0.7)
                    text(value, size = size, font = "Arial:style=Bold",
                         halign = halign, valign = "center");
}

module xz_coordinate_reference() {
    candidate_assembly_xz();

    // Put annotations in front (+Y) of the actual XZ geometry.
    arrow_x(-56, 56, 38, -34, axis_x);
    text_xz("+X  LONG / GREY TUBE AXIS", -56, 38, -41, 4.2, axis_x);

    arrow_z(-34, 50, 44, 38, axis_z);
    text_xz("+Z  UP / SCREW AXIS", 50, 38, 54, 4.2, axis_z);

    y_dot(-52, 38, 15, axis_y);
    text_xz("+Y FRONT", -46, 38, 15, 4.0, axis_y);
    y_cross(-52, 38, 3, axis_y);
    text_xz("-Y BACK", -46, 38, 3, 4.0, axis_y);

    text_xz("v0.9 SLOPED WALL / XZ", -58, 38, 62, 5.0, label_color);
    text_xz("BLUE TUBE TOP = z=0", -56, 38, -48, 4.0, label_color);
    text_xz("GREY TUBE HIDDEN IN THIS XZ VIEW", -56, 38, -54, 4.0, [0.55, 0.16, 0.06]);
}

xz_coordinate_reference();
