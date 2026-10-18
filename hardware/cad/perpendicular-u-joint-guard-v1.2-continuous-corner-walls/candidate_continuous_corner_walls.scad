// Candidate v1.2: two continuous X-end corner walls.
//
// Base: accepted v0.7 eaves12 geometry. v0.9/v1.0/v1.1 are not imported.
// The prior four separated front/back plates are replaced by two continuous
// solids that run through the available front/back envelope y=-21..+21.
// Their X ranges stay outside the blue lower tube's x=-10..+10 envelope.

use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
PART = "candidate_iso";

// Explicit v0.7 interface values; `use` imports modules, not top-level vars.
roof_x_outer = 27.4;       // accepted eaves12 roof: -27.4..+27.4
side_wall_x_outer = 15.4;  // existing side-wall outer edge
side_wall_x_inner = 10.4;  // existing side-wall inner edge
blue_tube_x_outer = 10.0;  // actual 20 mm blue tube half-width
wall_y_min = -21.0;
wall_y_max = 21.0;
wall_depth_y = wall_y_max - wall_y_min; // 42 mm continuous depth
roof_z_bottom = 21.0;
roof_z_top = 29.0;
landing_z = 0.0;           // blue lower tube top / side-wall lower target
roof_overlap_x = 1.0;
side_overlap_x = 1.0;

// v0.7 bottom retaining-hook contract.  These values are copied explicitly
// for the review/assertions; the actual printable hook remains inside the
// imported double_u_clip() and is not moved by v1.2.
hook_height_z = 1.5;
u_bottom_z = -21.0;
hook_top_z = u_bottom_z + hook_height_z; // -19.5
front_plate_y0 = 10.0;
front_plate_y1 = 21.0;
hook_depth_x = 3.5;
left_hook_center_x = -13.65;
right_hook_center_x = 13.65;
hook_center_z = u_bottom_z + hook_height_z / 2; // -20.25

assert(wall_depth_y == 42, "连续墙必须贯通 y=-21..+21");
assert(landing_z == 0,
       "蓝色下方方管上表面及侧墙目标高度必须是 z=0");
assert(roof_overlap_x > 0 && side_overlap_x > 0,
       "连续墙必须与屋檐和侧墙都有正重叠");
assert(side_wall_x_outer - side_overlap_x > blue_tube_x_outer,
       "连续墙下端不能进入蓝色方管 x=-10..+10 包络");
assert(hook_height_z == 1.5 && u_bottom_z == -21 && hook_top_z == -19.5,
       "底部内扣必须保持 z=-21..-19.5 的 1.5 mm");
assert(hook_top_z < 0 && landing_z == 0,
       "底部卡脚不得进入 z=0 以上的连续墙区域");

// One XZ trapezoid extruded over the whole front/back envelope.  This is a
// broad continuous wall/angle block, not a narrow decorative rib.  The
// 1 mm intervals at the roof and side-wall ends create positive overlap.
module continuous_wall_xz(points) {
    translate([0, (wall_y_min + wall_y_max) / 2, 0])
        rotate([90, 0, 0])
            linear_extrude(height = wall_depth_y,
                           center = true,
                           convexity = 10)
                polygon(points = points);
}

module continuous_neg_x_wall() {
    continuous_wall_xz([
        [-roof_x_outer, roof_z_bottom],
        [-roof_x_outer, roof_z_top],
        [-roof_x_outer + roof_overlap_x, roof_z_top],
        [-side_wall_x_outer + side_overlap_x, landing_z],
        [-side_wall_x_outer, landing_z]
    ]);
}

module continuous_pos_x_wall() {
    continuous_wall_xz([
        [roof_x_outer, roof_z_bottom],
        [roof_x_outer, roof_z_top],
        [roof_x_outer - roof_overlap_x, roof_z_top],
        [side_wall_x_outer - side_overlap_x, landing_z],
        [side_wall_x_outer, landing_z]
    ]);
}

module continuous_corner_walls() {
    union() {
        continuous_neg_x_wall();
        continuous_pos_x_wall();
    }
}

module candidate_print_solid() {
    // Reapply the true Z through-hole after the complete continuous-wall
    // union. The round v0.7 nut pocket remains part of this same relief.
    difference() {
        union() {
            double_u_clip();
            continuous_corner_walls();
        }
        vertical_screw_relief();
    }
}

module candidate_clip() {
    candidate_print_solid();
}

module candidate_assembly_iso() {
    upper_long_tube();
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.84, 0.12, 0.08]) continuous_neg_x_wall();
    color([0.12, 0.55, 0.78]) continuous_pos_x_wall();
    vertical_joint_screw();
}

module candidate_front_xz() {
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.84, 0.12, 0.08]) continuous_neg_x_wall();
    color([0.12, 0.55, 0.78]) continuous_pos_x_wall();
    vertical_joint_screw();
}

module candidate_back_xz() {
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.84, 0.12, 0.08]) continuous_neg_x_wall();
    color([0.12, 0.55, 0.78]) continuous_pos_x_wall();
    vertical_joint_screw();
}

module candidate_top_slice() {
    // z=-0.5..2.5 slice exposes the two walls' continuous y=-21..+21 span,
    // the blue tube, the open x=-10..+10 tube envelope, and the bore.
    slice_box = 200;
    color([0.28, 0.45, 0.78])
        intersection() {
            lower_cross_tube();
            translate([-slice_box / 2, -slice_box / 2, -0.5])
                cube([slice_box, slice_box, 3.0]);
        }
    color([0.96, 0.39, 0.08])
        intersection() {
            double_u_clip();
            translate([-slice_box / 2, -slice_box / 2, -0.5])
                cube([slice_box, slice_box, 3.0]);
        }
    color([0.84, 0.12, 0.08])
        intersection() {
            continuous_neg_x_wall();
            translate([-slice_box / 2, -slice_box / 2, -0.5])
                cube([slice_box, slice_box, 3.0]);
        }
    color([0.12, 0.55, 0.78])
        intersection() {
            continuous_pos_x_wall();
            translate([-slice_box / 2, -slice_box / 2, -0.5])
                cube([slice_box, slice_box, 3.0]);
        }
}

module candidate_bottom_view() {
    // Lower slice: shows the two lower U sides/hooks and the unfilled blue
    // tube path. The screw bore is still a true Z-axis opening in the final.
    slice_box = 200;
    color([0.96, 0.39, 0.08])
        intersection() {
            candidate_print_solid();
            translate([-slice_box / 2, -slice_box / 2, -21.5])
                cube([slice_box, slice_box, 3.0]);
        }
}

module candidate_hook_check() {
    // Detail only: crop the actual +Y front U plate and blue lower tube to
    // z=-22..-17 so the 1.5 mm lower hook is visible at useful scale.
    detail_box = 200;
    detail_z0 = -22;
    detail_h = 5;
    detail_y0 = 8;
    detail_ydepth = 15;
    intersection() {
        lower_cross_tube();
        translate([-detail_box / 2, detail_y0, detail_z0])
            cube([detail_box, detail_ydepth, detail_h]);
    }
    color([0.96, 0.39, 0.08])
        intersection() {
            u_plate(front_plate_y0, front_plate_y1);
            translate([-detail_box / 2, detail_y0, detail_z0])
                cube([detail_box, detail_ydepth, detail_h]);
        }
    // Highlight the exact imported hook volumes in green; these boxes occupy
    // the same coordinates as the v0.7 hook geometry inside u_plate().
    color([0.20, 0.78, 0.20])
        intersection() {
            union() {
                translate([left_hook_center_x, (front_plate_y0 + front_plate_y1) / 2, hook_center_z])
                    cube([hook_depth_x, front_plate_y1 - front_plate_y0, hook_height_z], center = true);
                translate([right_hook_center_x, (front_plate_y0 + front_plate_y1) / 2, hook_center_z])
                    cube([hook_depth_x, front_plate_y1 - front_plate_y0, hook_height_z], center = true);
            }
            translate([-detail_box / 2, detail_y0, detail_z0])
                cube([detail_box, detail_ydepth, detail_h]);
        }
}

module candidate_hole_section() {
    // y=0 centre section: the centre passage is intentionally open below the
    // roof, while the final Z bore and round nut pocket are visible in the
    // remaining top beam.
    intersection() {
        candidate_print_solid();
        translate([-100, -0.4, -100]) cube([200, 0.8, 200]);
    }
}

if (PART == "candidate_clip") {
    candidate_clip();
} else if (PART == "candidate_front_xz") {
    candidate_front_xz();
} else if (PART == "candidate_back_xz") {
    candidate_back_xz();
} else if (PART == "candidate_top_slice") {
    candidate_top_slice();
} else if (PART == "candidate_bottom_view") {
    candidate_bottom_view();
} else if (PART == "candidate_hook_check") {
    candidate_hook_check();
} else if (PART == "candidate_hole_section") {
    candidate_hole_section();
} else {
    candidate_assembly_iso();
}
