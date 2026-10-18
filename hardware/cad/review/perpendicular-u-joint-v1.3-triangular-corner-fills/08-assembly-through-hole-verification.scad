// Review only: unchanged v1.3 final solid + the source tube/screw envelopes.
// A thin y=0 section exposes the coaxial bore through every component.
// No dimensions or assembly transforms of the model are overridden here.
use <../../perpendicular-u-joint-guard-v1.3-triangular-corner-fills/candidate_triangular_corner_fills.scad>;
use <../../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
CHECK = "view";

module assembly_material_without_fastener() {
    candidate_print_solid();
    upper_long_tube();
    lower_cross_tube();
}

module centre_section() {
    // Slice/crop only affects the verification view, never printable source.
    intersection() {
        children();
        translate([-35, -0.025, -34]) cube([70, 0.05, 68]);
    }
}

module label_xz(value, x, z, size = 3.2, c = [0.1, 0.12, 0.15]) {
    color(c) translate([x, -1, z]) rotate([90, 0, 0])
        linear_extrude(height = 0.12)
            text(value, font = "Arial Unicode MS", size = size,
                 halign = "left", valign = "center");
}

module line_xz(a, b, c = [0.2, 0.23, 0.27], d = 0.24) {
    color(c) hull() {
        translate([a[0], -0.8, a[1]]) sphere(d = d, $fn = 12);
        translate([b[0], -0.8, b[1]]) sphere(d = d, $fn = 12);
    }
}

module verification_view() {
    // Source colors: orange printing, gray upper tube, blue lower tube,
    // silver screw and gold head/nut. All shown at their source coordinates.
    color([0.96, 0.39, 0.08]) centre_section() candidate_print_solid();
    // Outer display colors are needed because an intersection discards the
    // nested source colors in OpenSCAD F6. They match the source definitions.
    color([0.58, 0.61, 0.66]) centre_section() upper_long_tube();
    color([0.28, 0.45, 0.78]) centre_section() lower_cross_tube();
    color([0.82, 0.82, 0.84]) centre_section() difference() {
        vertical_joint_screw();
        translate([-12, -12, -27]) cube([24, 24, 4]);
        translate([-12, -12, 23.8]) cube([24, 24, 4]);
    }
    color([0.92, 0.70, 0.12]) centre_section() intersection() {
        vertical_joint_screw();
        union() {
            translate([-12, -12, -27]) cube([24, 24, 4]);
            translate([-12, -12, 23.8]) cube([24, 24, 4]);
        }
    }

    label_xz("v1.3 装配中心剖面  y=0  /  单位 mm", -38, 44, 4.1);
    label_xz("真实 SCAD 几何；上下管及打印件共用 Z 轴孔", -38, 38, 3.0);

    line_xz([8, 26], [36, 33]);
    label_xz("顶部螺母窝 Ø16", 40, 33, 3.4);
    line_xz([20, 22], [36, 25]);
    label_xz("v1.3 打印件", 40, 25, 3.4, [0.7, 0.24, 0.04]);
    line_xz([30, 10], [36, 10]);
    label_xz("上方管子（灰色）", 40, 10, 3.4);
    label_xz("Z = 0..20", 40, 5, 2.8);
    line_xz([9, -12], [36, -12]);
    label_xz("下方管子（蓝色）", 40, -12, 3.4, [0.18, 0.3, 0.6]);
    label_xz("Z = -20..0", 40, -17, 2.8);

    // Dimension across the actual nominal bore at the joint plane.
    line_xz([-3.1, 0], [-28, -4]);
    line_xz([3.1, 0], [28, -4]);
    label_xz("Ø6.2 Z 向同轴贯通", -34, -39, 3.6);
    label_xz("银色螺杆 Ø5；两侧各留 0.6 mm 名义间隙", -34, -45, 2.9);
    label_xz("顶部 Ø16 螺母窝为局部扩孔，不属于等径段", -34, -51, 2.9);

    // Z datum placed clear of the assembly section.
    color([0.10, 0.62, 0.23]) {
        translate([-39, 0, -30]) cylinder(d = 0.55, h = 59);
        translate([-39, 0, 29]) cylinder(r1 = 1.8, r2 = 0, h = 4);
    }
    label_xz("+Z", -45, 34, 3.3, [0.10, 0.62, 0.23]);
    label_xz("-Z", -45, -33, 3.3, [0.10, 0.62, 0.23]);
}

if (CHECK == "bore_obstruction") {
    // Must be empty: nominal Ø6.2 / 48-sided bore, z=-24..32.
    // Test 0.001 mm smaller in diameter to exclude coincident zero-volume
    // facets of the source cutter from the Boolean intersection result.
    // Excludes fastener itself, because the screw intentionally occupies it.
    intersection() {
        assembly_material_without_fastener();
        translate([0, 0, 4]) cylinder(d = 6.199, h = 56, center = true, $fn = 48);
    }
} else {
    verification_view();
}
