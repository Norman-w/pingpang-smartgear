// Candidate v1.3: four triangular concave-corner fill blocks.
//
// Base: accepted v0.7 eaves12 geometry. v0.9/v1.0/v1.1/v1.2 are not
// imported. Each corner block is a real triangular prism: broad at the roof,
// tapering continuously toward z=0, and overlapping the U side wall.

use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
PART = "candidate_iso";

// Explicit v0.7 interface values.
roof_x_outer = 27.4;       // accepted eaves12 roof: -27.4..+27.4
side_wall_x_outer = 15.4;  // existing side-wall outer edge
blue_tube_x_outer = 10.0;  // blue lower 20x20 tube half-width
plate_y_inner = 10.0;
plate_y_outer = 21.0;
plate_depth_y = plate_y_outer - plate_y_inner; // 11 mm per front/back U plate

// The top edge is 0.5 mm inside the roof volume (roof underside z=21), and
// the lower point enters the side wall by 1 mm in X.  The XZ area therefore
// has positive overlap at both ends, not edge-only contact.
triangle_top_z = 21.5;
triangle_bottom_z = 0.0;
triangle_roof_overlap_z = triangle_top_z - 21.0;
triangle_side_overlap_x = 1.0;
triangle_inner_x = side_wall_x_outer - triangle_side_overlap_x; // 14.4

// Bottom retaining-hook contract copied from v0.7 for explicit verification.
hook_height_z = 1.5;
u_bottom_z = -21.0;
hook_top_z = u_bottom_z + hook_height_z; // -19.5

assert(plate_depth_y == 11, "每个三角块的前后板深必须是 11 mm");
assert(triangle_top_z > 21 && triangle_bottom_z == 0,
       "三角块上端必须搭入屋檐、下端落到 z=0");
assert(triangle_inner_x > blue_tube_x_outer,
       "三角块下端不得进入蓝色方管 x=-10..+10 包络");
assert(triangle_side_overlap_x > 0 && triangle_roof_overlap_z > 0,
       "三角块必须与屋檐和侧墙都有正重叠");
assert(hook_height_z == 1.5 && u_bottom_z == -21 && hook_top_z == -19.5,
       "底部卡脚必须保持 z=-21..-19.5");

// A polygon in XZ is extruded only through the corresponding front/back U
// plate. The center y=-10..+10 passage remains open.
module triangular_fill_xz(points, yc) {
    translate([0, yc, 0])
        rotate([90, 0, 0])
            linear_extrude(height = plate_depth_y,
                           center = true,
                           convexity = 10)
                polygon(points = points);
}

module front_neg_x_triangle() {
    // -X roof end -> +X inward. Top wide, lower point at the side wall.
    triangular_fill_xz([
        [-roof_x_outer, 21.0],
        [-triangle_inner_x, triangle_top_z],
        [-triangle_inner_x, triangle_bottom_z]
    ], (plate_y_inner + plate_y_outer) / 2);
}

module front_pos_x_triangle() {
    // +X roof end -> -X inward. Mirrored triangle.
    triangular_fill_xz([
        [roof_x_outer, 21.0],
        [triangle_inner_x, triangle_top_z],
        [triangle_inner_x, triangle_bottom_z]
    ], (plate_y_inner + plate_y_outer) / 2);
}

module back_neg_x_triangle() {
    triangular_fill_xz([
        [-roof_x_outer, 21.0],
        [-triangle_inner_x, triangle_top_z],
        [-triangle_inner_x, triangle_bottom_z]
    ], -(plate_y_inner + plate_y_outer) / 2);
}

module back_pos_x_triangle() {
    triangular_fill_xz([
        [roof_x_outer, 21.0],
        [triangle_inner_x, triangle_top_z],
        [triangle_inner_x, triangle_bottom_z]
    ], -(plate_y_inner + plate_y_outer) / 2);
}

module front_two_triangular_fills() {
    union() {
        front_neg_x_triangle();
        front_pos_x_triangle();
    }
}

module back_two_triangular_fills() {
    union() {
        back_neg_x_triangle();
        back_pos_x_triangle();
    }
}

module all_four_triangular_fills() {
    union() {
        front_two_triangular_fills();
        back_two_triangular_fills();
    }
}

module candidate_print_solid() {
    // Final hole operation is deliberately after the complete four-block
    // union; this preserves a true Z through-hole and the round nut pocket.
    difference() {
        union() {
            double_u_clip();
            all_four_triangular_fills();
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
    color([0.86, 0.13, 0.08]) front_two_triangular_fills();
    color([0.62, 0.12, 0.52]) back_two_triangular_fills();
    vertical_joint_screw();
}

module candidate_front_xz() {
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.86, 0.13, 0.08]) front_two_triangular_fills();
    vertical_joint_screw();
}

module candidate_back_xz() {
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.62, 0.12, 0.52]) back_two_triangular_fills();
    vertical_joint_screw();
}

module candidate_top_slice() {
    // At z=-0.5..2.5 the four blocks show their two front/back 11 mm bands;
    // the blue tube and the central y gap remain visible.
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
            front_two_triangular_fills();
            translate([-slice_box / 2, -slice_box / 2, -0.5])
                cube([slice_box, slice_box, 3.0]);
        }
    color([0.62, 0.12, 0.52])
        intersection() {
            back_two_triangular_fills();
            translate([-slice_box / 2, -slice_box / 2, -0.5])
                cube([slice_box, slice_box, 3.0]);
        }
}

module candidate_hole_section() {
    // Center y=0 section: the bore and round nut pocket are shown without
    // confusing them with the bottom hook, which is outside this section.
    intersection() {
        candidate_print_solid();
        translate([-100, -0.4, -100]) cube([200, 0.8, 200]);
    }
}

module candidate_hook_check() {
    // Isolated lower detail: exact imported v0.7 U plate and blue tube, with
    // hook volumes highlighted only for review. This is not the print union.
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
            u_plate(plate_y_inner, plate_y_outer);
            translate([-detail_box / 2, detail_y0, detail_z0])
                cube([detail_box, detail_ydepth, detail_h]);
        }
    color([0.20, 0.78, 0.20])
        intersection() {
            union() {
                translate([-13.65, 15.5, -20.25])
                    cube([3.5, 11, 1.5], center = true);
                translate([13.65, 15.5, -20.25])
                    cube([3.5, 11, 1.5], center = true);
            }
            translate([-detail_box / 2, detail_y0, detail_z0])
                cube([detail_box, detail_ydepth, detail_h]);
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
} else if (PART == "candidate_hook_check") {
    candidate_hook_check();
} else {
    candidate_assembly_iso();
}
