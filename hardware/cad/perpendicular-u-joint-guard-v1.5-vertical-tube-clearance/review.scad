// v1.5 real SCAD assembly and motion checks; all old sources unchanged.
use <vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.4-full-nut-passage/full_nut_passage_guard.scad>;
use <../perpendicular-u-joint-guard-v1.3-triangular-corner-fills/candidate_triangular_corner_fills.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
VIEW = "assembly";
OFFSET_Z = 0;

module slice() {
    intersection() {
        children();
        translate([-36, -0.025, -34]) cube([72, 0.05, 68]);
    }
}
module label_xz(value, x, z, size = 3.2, c = [0.10, 0.12, 0.15]) {
    color(c) translate([x, -1, z]) rotate([90, 0, 0])
        linear_extrude(height = 0.12)
            text(value, font = "Arial Unicode MS", size = size,
                 halign = "left", valign = "center");
}
module label_yz(value, y, z, size = 3.2, c = [0.10, 0.12, 0.15]) {
    color(c) translate([14, y, z]) rotate([90, 0, 90])
        linear_extrude(height = 0.12)
            text(value, font = "Arial Unicode MS", size = size,
                 halign = "left", valign = "center");
}
module assembled() {
    upper_long_tube();
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) translate([0, 0, OFFSET_Z]) guard_v1_5();
    vertical_joint_screw();
}
module centre_section() {
    color([0.96, 0.39, 0.08]) slice() guard_v1_5();
    color([0.58, 0.61, 0.66]) slice() upper_long_tube();
    color([0.28, 0.45, 0.78]) slice() lower_cross_tube();
    color([0.82, 0.82, 0.84]) slice() difference() {
        vertical_joint_screw();
        translate([-12, -12, -27]) cube([24, 24, 4]);
        translate([-12, -12, 23.8]) cube([24, 24, 4]);
    }
    color([0.92, 0.70, 0.12]) slice() intersection() {
        vertical_joint_screw();
        union() {
            translate([-12, -12, -27]) cube([24, 24, 4]);
            translate([-12, -12, 23.8]) cube([24, 24, 4]);
        }
    }
    label_xz("v1.5 中心剖面  Y=0", -39, 43, 4.1);
    label_xz("屋檐下方留出灰管竖直装入通道", -39, 36, 3.2);
    label_xz("Ø16 全深通行孔，无台阶", 39, 29, 3.2);
    label_xz("上方灰管", 39, 12, 3.4);
    label_xz("下方蓝管", 39, -12, 3.4, [0.18, 0.3, 0.6]);
    label_xz("原侧墙 X=±10.4..15.4 在中央 Y=-10..+10 段已让位", -39, -38, 2.9);
}
module entry_motion_view() {
    assembled();
    color([0.1, 0.62, 0.23]) {
        translate([40, -30, 38]) cylinder(d = 1.7, h = 31);
        translate([40, -30, 38]) rotate([180, 0, 0])
            cylinder(r1 = 4.5, r2 = 0, h = 9);
    }
    color([0.1, 0.12, 0.15]) translate([-40, -5, 112])
        linear_extrude(height = 0.3)
            text("v1.5  沿 -Z 套入", font = "Arial Unicode MS", size = 5);
}
module y_entry_section() {
    // A real YZ section through x=13 crosses the former interfering side wall.
    color([0.96, 0.39, 0.08]) intersection() {
        guard_v1_5();
        translate([12.975, -32, -25]) cube([0.05, 64, 60]);
    }
    color([0.58, 0.61, 0.66]) intersection() {
        upper_long_tube();
        translate([12.975, -32, -25]) cube([0.05, 64, 60]);
    }
    label_yz("v1.5 侧剖面 X=13", -27, 40, 3.8);
    label_yz("中央 20 mm 向下开口，灰管可直入", -27, 34, 2.7);
    label_yz("Y=-10..+10", -8, -29, 2.8);
    label_yz("前后 U 板及三角块保留", -27, -36, 2.7);
}

module allowed_bottom_hook_regions() {
    // Exact v0.7 hook boxes, used ONLY to classify the allowed snap-fit
    // interference. They are never added to or removed from the exported part.
    // Original centers: ±11.15 (not ±13.65), Z=-20.25, height=1.5.
    for (yc = [-15.5, 15.5])
        for (xc = [-11.15, 11.15])
            translate([xc, yc, -20.25]) cube([3.5, 11, 1.5], center = true);
}

module retained_hook_detail() {
    // Real lower crop of the completed model; exact hook volumes highlighted.
    color([0.28, 0.45, 0.78]) intersection() {
        lower_cross_tube();
        translate([-20, 8, -22]) cube([40, 16, 6]);
    }
    color([0.96, 0.39, 0.08]) intersection() {
        difference() { guard_v1_5(); allowed_bottom_hook_regions(); }
        translate([-20, 8, -22]) cube([40, 16, 6]);
    }
    color([0.18, 0.72, 0.18]) intersection() {
        guard_v1_5(); allowed_bottom_hook_regions();
        translate([-20, 8, -22]) cube([40, 16, 6]);
    }
}

if (VIEW == "section") centre_section();
else if (VIEW == "entry_section") y_entry_section();
else if (VIEW == "insertion") entry_motion_view();
else if (VIEW == "hook_detail") retained_hook_detail();
else if (VIEW == "clip") guard_v1_5();
else if (VIEW == "upper_tube_motion_obstruction") {
    intersection() {
        guard_v1_5();
        hull() { upper_long_tube(); translate([0, 0, -52]) upper_long_tube(); }
    }
} else if (VIEW == "nut_motion_obstruction") {
    intersection() {
        guard_v1_5();
        hull() { vertical_joint_screw(); translate([0, 0, -52]) vertical_joint_screw(); }
    }
} else if (VIEW == "passage_obstruction") {
    intersection() {
        guard_v1_5();
        translate([0, 0, 4]) cylinder(d = 15.999, h = 70, center = true, $fn = 64);
    }
} else if (VIEW == "lower_tube_motion_obstruction") {
    intersection() {
        guard_v1_5();
        hull() { lower_cross_tube(); translate([0, 0, -52]) lower_cross_tube(); }
    }
} else if (VIEW == "lower_tube_seated_obstruction") {
    intersection() { guard_v1_5(); lower_cross_tube(); }
} else if (VIEW == "rigid_lower_tube_motion_obstruction") {
    intersection() {
        difference() { guard_v1_5(); allowed_bottom_hook_regions(); }
        hull() { lower_cross_tube(); translate([0, 0, -52]) lower_cross_tube(); }
    }
} else if (VIEW == "hooks_changed") {
    union() {
        difference() {
            intersection() { guard_v1_4(); allowed_bottom_hook_regions(); }
            guard_v1_5();
        }
        difference() {
            intersection() { guard_v1_5(); allowed_bottom_hook_regions(); }
            guard_v1_4();
        }
    }
} else if (VIEW == "triangles_changed") {
    // The underlying v1.3 triangle definitions are unchanged. Their material
    // must still be present in the completed v1.5 solid.
    difference() { all_four_triangular_fills(); guard_v1_5(); }
} else if (VIEW == "changed_outside_entry_slot") {
    difference() {
        difference() { guard_v1_4(); guard_v1_5(); }
        upper_pipe_vertical_entry_slot();
    }
} else assembled();
