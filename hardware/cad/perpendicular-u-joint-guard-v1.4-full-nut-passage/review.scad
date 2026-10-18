// Review and Boolean checks of the actual v1.4 solid. No AI images.
use <full_nut_passage_guard.scad>;
use <../perpendicular-u-joint-guard-v1.3-triangular-corner-fills/candidate_triangular_corner_fills.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
VIEW = "assembly";
OFFSET_Z = 0;

module tubes() { upper_long_tube(); lower_cross_tube(); }
module section() {
    intersection() {
        children();
        translate([-36, -0.025, -34]) cube([72, 0.05, 68]);
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
module section_fastener() {
    color([0.82, 0.82, 0.84]) section() difference() {
        vertical_joint_screw();
        translate([-12, -12, -27]) cube([24, 24, 4]);
        translate([-12, -12, 23.8]) cube([24, 24, 4]);
    }
    color([0.92, 0.70, 0.12]) section() intersection() {
        vertical_joint_screw();
        union() {
            translate([-12, -12, -27]) cube([24, 24, 4]);
            translate([-12, -12, 23.8]) cube([24, 24, 4]);
        }
    }
}
module assembled() {
    upper_long_tube();
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) translate([0, 0, OFFSET_Z]) guard_v1_4();
    vertical_joint_screw();
}
module central_section() {
    color([0.96, 0.39, 0.08]) section() guard_v1_4();
    color([0.58, 0.61, 0.66]) section() upper_long_tube();
    color([0.28, 0.45, 0.78]) section() lower_cross_tube();
    section_fastener();

    label_xz("v1.4 装配中心剖面  y=0", -40, 43, 4.2);
    label_xz("打印件全深度 Ø16：上下开口连续、无窝底", -40, 37, 3.2);
    line_xz([8, 24], [35, 30]);
    label_xz("Ø16 螺帽通行孔", 39, 30, 3.5);
    label_xz("螺帽/螺杆保持预装位置", 39, 25, 3.0);
    line_xz([30, 11], [35, 11]);
    label_xz("上方管子（灰色）", 39, 11, 3.2);
    line_xz([9, -12], [35, -12]);
    label_xz("下方管子（蓝色）", 39, -12, 3.2, [0.18, 0.3, 0.6]);
    label_xz("铁管原 Ø6.2 螺丝孔保留", 39, -18, 2.9);
    label_xz("仅打印件扩至 Ø16；管子、螺丝、四角块、底扣均沿用原几何", -40, -41, 2.8);
    color([0.10, 0.62, 0.23]) {
        translate([-40, 0, -29]) cylinder(d = 0.55, h = 58);
        translate([-40, 0, 29]) cylinder(r1 = 1.8, r2 = 0, h = 4);
    }
    label_xz("+Z", -46, 34, 3.1, [0.10, 0.62, 0.23]);
    label_xz("-Z", -46, -33, 3.1, [0.10, 0.62, 0.23]);
}
module insertion_view() {
    // Show the actual model above fixed tubes. OFFSET_Z=52 puts its bottom
    // at z=31, above the fixed nut/head envelope; arrow is -Z motion.
    assembled();
    color([0.10, 0.62, 0.23]) {
        translate([40, -30, 38]) cylinder(d = 1.7, h = 31);
        translate([40, -30, 38]) rotate([180, 0, 0])
            cylinder(r1 = 4.5, r2 = 0, h = 9);
    }
    // Coordinate labels are actual SCAD text outside the assembly.
    color([0.1, 0.12, 0.15]) translate([-40, -5, 112])
        linear_extrude(height = 0.3)
            text("v1.4  沿 -Z 套入", font = "Arial Unicode MS", size = 5);
}

module interference_section() {
    // Red is the exact material intersection, not a hand-drawn indication.
    color([0.96, 0.39, 0.08]) section() difference() {
        guard_v1_4(); tubes();
    }
    color([0.58, 0.61, 0.66]) section() difference() {
        upper_long_tube(); guard_v1_4();
    }
    color([0.28, 0.45, 0.78]) section() lower_cross_tube();
    color([0.9, 0.03, 0.03]) section() intersection() {
        guard_v1_4(); upper_long_tube();
    }
    label_xz("原墙体装配干涉核对  y=0", -39, 42, 4.1);
    label_xz("红色是实体布尔交集：原侧墙与灰色上管相交", -39, 36, 3.1);
    line_xz([13, 11], [37, 15]);
    label_xz("原侧墙占用灰管通路", 41, 15, 3.4, [0.8, 0.04, 0.04]);
    label_xz("两侧 |X|=10.4..15.4", 41, 9, 2.9);
    label_xz("Y=-10..+10, Z=0..20", 41, 4, 2.9);
    label_xz("按本次约束保持原墙体；Ø16 通行孔已单独验证通过", -39, -33, 3.0);
}

if (VIEW == "section") central_section();
else if (VIEW == "insertion") insertion_view();
else if (VIEW == "interference_section") interference_section();
else if (VIEW == "clip") guard_v1_4();
else if (VIEW == "passage_obstruction") {
    // 0.001 mm diameter allowance excludes zero-volume coincident faces.
    intersection() {
        guard_v1_4();
        translate([0, 0, 4]) cylinder(d = 15.999, h = 70, center = true, $fn = 64);
    }
} else if (VIEW == "changed_outside_passage") {
    // Must be empty: no v1.3 material changes outside the Ø16 cutter.
    difference() {
        difference() { candidate_print_solid(); guard_v1_4(); }
        full_depth_nut_passage();
    }
} else if (VIEW == "tube_interference") {
    intersection() {
        translate([0, 0, OFFSET_Z]) guard_v1_4();
        tubes();
    }
} else if (VIEW == "upper_tube_interference") {
    intersection() { guard_v1_4(); upper_long_tube(); }
} else if (VIEW == "lower_tube_interference") {
    intersection() { guard_v1_4(); lower_cross_tube(); }
} else if (VIEW == "nut_motion_obstruction") {
    // Fixed installed hardware swept relative to the part during -Z travel.
    intersection() {
        guard_v1_4();
        hull() {
            vertical_joint_screw();
            translate([0, 0, -52]) vertical_joint_screw();
        }
    }
} else assembled();
