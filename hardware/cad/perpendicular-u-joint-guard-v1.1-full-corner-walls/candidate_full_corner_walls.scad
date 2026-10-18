// Candidate v1.1: four full-depth solid corner walls.
//
// Base: accepted v0.7 eaves12 geometry.  v0.9 and v1.0 are not imported.
// The four XZ corner solids occupy the full front/back U-plate depths:
//   +Y FRONT: y=+10..+21
//   -Y BACK:  y=-21..-10
// The central y=-10..+10 passage remains open.

use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
PART = "candidate_iso";

// Explicit v0.7 interface values.  `use` imports modules, not top-level vars.
roof_x_outer = 27.4;       // accepted eaves12 roof: -27.4..+27.4
side_wall_x_outer = 15.4;  // existing side-wall outer edge
side_wall_x_inner = 10.4;  // existing side-wall inner edge
plate_y_inner = 10.0;
plate_y_outer = 21.0;
plate_depth_y = plate_y_outer - plate_y_inner; // 11 mm full U-plate depth
material_thickness = 5.0;  // existing X side-wall thickness
roof_z_bottom = 21.0;
roof_z_top = 29.0;
landing_z = 0.0;           // blue lower tube top / side-wall lower target
roof_overlap_x = 1.0;
side_overlap_x = 1.0;

front_wall_y0 = plate_y_inner;
front_wall_y1 = plate_y_outer;
back_wall_y0 = -plate_y_outer;
back_wall_y1 = -plate_y_inner;

assert(plate_depth_y == 11, "前后 U 板完整深度必须是 11 mm");
assert(landing_z == 0,
       "蓝色下方方管上表面及侧墙目标高度必须是 z=0");
assert(roof_overlap_x > 0 && side_overlap_x > 0,
       "四面墙必须与屋檐和侧墙都有正重叠");
assert(front_wall_y0 == 10 && front_wall_y1 == 21,
       "前侧整段包角墙必须覆盖 y=+10..+21");
assert(back_wall_y0 == -21 && back_wall_y1 == -10,
       "后侧整段包角墙必须覆盖 y=-21..-10");

// The XZ trapezoid covers the complete corner volume between the roof end
// and the side-wall interface.  It has a finite roof overlap (1 mm) and a
// finite side-wall overlap (1 mm), so it is not an edge-tangent rib.
module sloped_wall_xz(points, yc) {
    translate([0, yc, 0])
        rotate([90, 0, 0])
            linear_extrude(height = plate_depth_y,
                           center = true,
                           convexity = 10)
                polygon(points = points);
}

module wall_front_neg_x() {
    sloped_wall_xz([
        [-roof_x_outer, roof_z_bottom],
        [-roof_x_outer, roof_z_top],
        [-roof_x_outer + roof_overlap_x, roof_z_top],
        [-side_wall_x_outer + side_overlap_x, landing_z],
        [-side_wall_x_outer, landing_z]
    ], (front_wall_y0 + front_wall_y1) / 2);
}

module wall_front_pos_x() {
    sloped_wall_xz([
        [roof_x_outer, roof_z_bottom],
        [roof_x_outer, roof_z_top],
        [roof_x_outer - roof_overlap_x, roof_z_top],
        [side_wall_x_outer - side_overlap_x, landing_z],
        [side_wall_x_outer, landing_z]
    ], (front_wall_y0 + front_wall_y1) / 2);
}

module wall_back_neg_x() {
    sloped_wall_xz([
        [-roof_x_outer, roof_z_bottom],
        [-roof_x_outer, roof_z_top],
        [-roof_x_outer + roof_overlap_x, roof_z_top],
        [-side_wall_x_outer + side_overlap_x, landing_z],
        [-side_wall_x_outer, landing_z]
    ], (back_wall_y0 + back_wall_y1) / 2);
}

module wall_back_pos_x() {
    sloped_wall_xz([
        [roof_x_outer, roof_z_bottom],
        [roof_x_outer, roof_z_top],
        [roof_x_outer - roof_overlap_x, roof_z_top],
        [side_wall_x_outer - side_overlap_x, landing_z],
        [side_wall_x_outer, landing_z]
    ], (back_wall_y0 + back_wall_y1) / 2);
}

module front_two_full_corner_walls() {
    union() {
        wall_front_neg_x();
        wall_front_pos_x();
    }
}

module back_two_full_corner_walls() {
    union() {
        wall_back_neg_x();
        wall_back_pos_x();
    }
}

module all_four_full_corner_walls() {
    union() {
        front_two_full_corner_walls();
        back_two_full_corner_walls();
    }
}

module candidate_print_solid() {
    // The through-hole is intentionally applied after the complete union.
    // This keeps the screw clearance unambiguously open from the bottom to
    // the top, while preserving the round nut pocket from the v0.7 base.
    difference() {
        union() {
            double_u_clip();
            all_four_full_corner_walls();
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
    color([0.86, 0.13, 0.08]) front_two_full_corner_walls();
    color([0.62, 0.12, 0.52]) back_two_full_corner_walls();
    vertical_joint_screw();
}

module candidate_front_xz() {
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.86, 0.13, 0.08]) front_two_full_corner_walls();
    vertical_joint_screw();
}

module candidate_back_xz() {
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.62, 0.12, 0.52]) back_two_full_corner_walls();
    vertical_joint_screw();
}

module candidate_top_slice() {
    // Review slice z=-0.5..2.5: it includes the blue tube's top and the
    // printable corner walls, exposing the full y bands and the open 20 mm
    // central passage.
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
    color([0.86, 0.13, 0.08])
        intersection() {
            front_two_full_corner_walls();
            translate([-slice_box / 2, -slice_box / 2, -0.5])
                cube([slice_box, slice_box, 3.0]);
        }
    color([0.62, 0.12, 0.52])
        intersection() {
            back_two_full_corner_walls();
            translate([-slice_box / 2, -slice_box / 2, -0.5])
                cube([slice_box, slice_box, 3.0]);
        }
}

module candidate_hole_section() {
    // Thin y=0 centre section of the printable body.  The final difference
    // leaves the complete z-axis hole and round top pocket visible; the
    // opening below the roof is intentionally visible because the central
    // y=-10..+10 passage is not filled by the front/back corner walls.
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
} else if (PART == "candidate_hole_section") {
    candidate_hole_section();
} else {
    candidate_assembly_iso();
}
