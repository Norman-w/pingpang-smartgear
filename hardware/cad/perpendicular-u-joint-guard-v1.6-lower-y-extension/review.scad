// v1.6 review only: actual SCAD geometry, dimensions and Boolean diagnostics.
use <lower_y_extension_guard.scad>;
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.3-triangular-corner-fills/candidate_triangular_corner_fills.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
VIEW = "assembly";

module added_material() { difference() { guard_v1_6(); guard_v1_5(); } }
module colored_part() {
    color([0.96, 0.39, 0.08]) guard_v1_5();
    color([0.16, 0.65, 0.33]) added_material();
}
module assembly(candidate = true) {
    upper_long_tube();
    lower_cross_tube();
    if (candidate) colored_part();
    else color([0.96, 0.39, 0.08]) guard_v1_5();
    vertical_joint_screw();
}
module yz_slice(x = 13) {
    intersection() {
        children();
        translate([x - 0.025, -65, -32]) cube([0.05, 130, 70]);
    }
}
module label_yz(value, y, z, size = 3.0, c = [0.1, 0.12, 0.15]) {
    color(c) translate([14, y, z]) rotate([90, 0, 90])
        linear_extrude(height = 0.1)
            text(value, font = "Arial Unicode MS", size = size,
                 halign = "left", valign = "center");
}
module line_yz(a, b, c = [0.18, 0.2, 0.23], d = 0.22) {
    color(c) hull() {
        translate([14, a[0], a[1]]) sphere(d = d, $fn = 12);
        translate([14, b[0], b[1]]) sphere(d = d, $fn = 12);
    }
}
module y_dimension(a, b, z, caption) {
    line_yz([a,z],[b,z]);
    line_yz([a,z-1],[a,z+1]);
    line_yz([b,z-1],[b,z+1]);
    label_yz(caption, (a+b)/2-5, z-3, 2.8);
}
module side_dimensions(candidate = true, title = true) {
    color([0.96, 0.39, 0.08]) yz_slice() guard_v1_5();
    if (candidate) color([0.16, 0.65, 0.33]) yz_slice() added_material();
    color([0.58, 0.61, 0.66]) yz_slice() upper_long_tube();
    if (title) {
        label_yz("v1.6 底部 Y 向对称延伸  /  X=13 剖面", -43, 43, 3.7);
        label_yz("绿色：仅 Z=-21..0；上方三角块与屋檐沿用 v1.5", -43, 36, 2.7);
    }
    if (candidate) {
        y_dimension(-33,-21,-28,"12 mm");
        y_dimension(21,33,-28,"12 mm");
        line_yz([-38,-21],[-38,0]);
        line_yz([-39,-21],[-37,-21]);
        line_yz([-39,0],[-37,0]);
        label_yz("Z=0",-49,0,2.8);
        label_yz("Z=-21",-51,-21,2.8);
        label_yz("高度 21",-54,-10,2.8);
    }
    label_yz("-Y BACK",-32,-38,2.8);
    label_yz("+Y FRONT",21,-38,2.8);
}
module comparison() {
    translate([0,-63,0]) {
        side_dimensions(false, false);
        label_yz("基线 v1.5", -30, 39, 4);
        y_dimension(-21,21,-28,"原外宽 42 mm");
    }
    translate([0,63,0]) {
        side_dimensions(true, false);
        label_yz("候选 v1.6", -30, 39, 4);
        label_yz("下部外宽 66 mm", -24, 32, 3);
    }
}
module bottom_dimensions() {
    // Top-down slice through the true lower hooks at z=-20.25.
    color([0.96, 0.39, 0.08]) intersection() {
        guard_v1_5();
        translate([-40,-50,-20.5]) cube([80,100,0.5]);
    }
    color([0.16, 0.65, 0.33]) intersection() {
        added_material();
        translate([-40,-50,-20.5]) cube([80,100,0.5]);
    }
    color([0.28, 0.45, 0.78]) intersection() {
        lower_cross_tube();
        translate([-10,-60,-20]) cube([20,120,0.1]);
    }
    // All labels are actual SCAD text, rendered above the clipped geometry.
    for (entry = [
        ["v1.6 底扣层俯视：前后各加 12 mm",-45,48,3.4],
        ["-33",20,-33,2.9], ["-21",20,-21,2.9],
        ["+21",20,21,2.9], ["+33",20,33,2.9],
        ["中央 Y=-10..+10 保持 20 mm",-43,-48,3.0]
    ]) color([0.1,0.12,0.15]) translate([entry[1],entry[2],-18])
        linear_extrude(height=0.1)
            text(entry[0],font="Arial Unicode MS",size=entry[3],valign="center");
}
module all_hook_regions() {
    // Original hook cross-section, now continuous from y=10..33 on each side.
    for (yc=[-21.5,21.5]) for(xc=[-11.15,11.15])
        translate([xc,yc,-20.25]) cube([3.5,23,1.5],center=true);
}

if (VIEW == "assembly") assembly();
else if (VIEW == "side") side_dimensions();
else if (VIEW == "comparison") comparison();
else if (VIEW == "bottom") bottom_dimensions();
else if (VIEW == "clip") guard_v1_6();
else if (VIEW == "passage_obstruction") {
    intersection() {
        guard_v1_6();
        translate([0,0,4]) cylinder(d=15.999,h=70,center=true,$fn=64);
    }
} else if (VIEW == "upper_motion_obstruction") {
    intersection() {
        guard_v1_6();
        hull() { upper_long_tube(); translate([0,0,-52]) upper_long_tube(); }
    }
} else if (VIEW == "nut_motion_obstruction") {
    intersection() {
        guard_v1_6();
        hull() { vertical_joint_screw(); translate([0,0,-52]) vertical_joint_screw(); }
    }
} else if (VIEW == "rigid_lower_motion_obstruction") {
    intersection() {
        difference() { guard_v1_6(); all_hook_regions(); }
        hull() { lower_cross_tube(); translate([0,0,-52]) lower_cross_tube(); }
    }
} else if (VIEW == "baseline_material_removed") {
    difference() { guard_v1_5(); guard_v1_6(); }
} else if (VIEW == "upper_geometry_changed") {
    intersection() {
        difference() { guard_v1_6(); guard_v1_5(); }
        translate([-100,-100,0.001]) cube([200,200,100]);
    }
} else if (VIEW == "triangles_changed") {
    difference() { all_four_triangular_fills(); guard_v1_6(); }
} else if (VIEW == "mirror_difference") {
    union() {
        difference() { guard_v1_6(); mirror([0,1,0]) guard_v1_6(); }
        difference() { mirror([0,1,0]) guard_v1_6(); guard_v1_6(); }
    }
}
