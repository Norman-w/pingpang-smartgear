// Candidate v1.0: four inward sloped solid walls.
//
// Base: accepted v0.7 eaves12 geometry.  v0.9's single outward wall is not
// imported and is not part of this candidate.
//
// Coordinate contract:
//   x = barrier long direction
//   y = front/back direction (+Y FRONT, -Y BACK)
//   z = vertical direction

use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;

PART = "candidate_iso";

// Explicit v0.7 interface values.  `use` imports the base modules, not its
// top-level variables, so the candidate keeps its interface dimensions here.
roof_x_outer = 27.4;       // roof x range is -27.4..+27.4; eaves12
side_wall_x_outer = 15.4;  // existing side-wall outer edge
material_thickness = 5.0;  // same as the existing U side-wall thickness
roof_z_bottom = 21.0;
roof_z_top = 29.0;
landing_z = 0.0;           // blue lower tube top / side-wall lower target
roof_overlap_x = 1.0;      // positive overlap into roof, toward the centre
side_overlap_x = 1.0;      // positive overlap into side wall, toward the centre
front_y_outer = 21.0;
back_y_outer = -21.0;
front_wall_yc = front_y_outer - material_thickness / 2;
back_wall_yc = back_y_outer + material_thickness / 2;

assert(landing_z == 0,
       "蓝色下方方管上表面及侧墙目标高度必须是 z=0");
assert(roof_overlap_x > 0 && side_overlap_x > 0,
       "四面斜墙必须与屋檐和侧墙都有正重叠");
assert(material_thickness == 5,
       "斜墙厚度沿用现有 5 mm 结构厚度");

// The polygon is an XZ trapezoid with finite overlap at both ends.  At the
// roof end it occupies x=-27.4..-26.4 (or the mirrored +X interval) through
// the roof's z=21..29 volume.  At the lower end it occupies a 1 mm-wide
// interval inside the corresponding existing side wall, so it is not merely
// tangent at an edge or a single point.
module sloped_wall_xz(points, yc) {
    translate([0, yc, 0])
        rotate([90, 0, 0])
            linear_extrude(height = material_thickness,
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
    ], front_wall_yc);
}

module wall_front_pos_x() {
    sloped_wall_xz([
        [roof_x_outer, roof_z_bottom],
        [roof_x_outer, roof_z_top],
        [roof_x_outer - roof_overlap_x, roof_z_top],
        [side_wall_x_outer - side_overlap_x, landing_z],
        [side_wall_x_outer, landing_z]
    ], front_wall_yc);
}

module wall_back_neg_x() {
    sloped_wall_xz([
        [-roof_x_outer, roof_z_bottom],
        [-roof_x_outer, roof_z_top],
        [-roof_x_outer + roof_overlap_x, roof_z_top],
        [-side_wall_x_outer + side_overlap_x, landing_z],
        [-side_wall_x_outer, landing_z]
    ], back_wall_yc);
}

module wall_back_pos_x() {
    sloped_wall_xz([
        [roof_x_outer, roof_z_bottom],
        [roof_x_outer, roof_z_top],
        [roof_x_outer - roof_overlap_x, roof_z_top],
        [side_wall_x_outer - side_overlap_x, landing_z],
        [side_wall_x_outer, landing_z]
    ], back_wall_yc);
}

module front_two_sloped_walls() {
    union() {
        wall_front_neg_x();
        wall_front_pos_x();
    }
}

module back_two_sloped_walls() {
    union() {
        wall_back_neg_x();
        wall_back_pos_x();
    }
}

module all_four_sloped_walls() {
    union() {
        front_two_sloped_walls();
        back_two_sloped_walls();
    }
}

module candidate_clip() {
    // One union: base v0.7 body plus four overlapping wall prisms.
    union() {
        double_u_clip();
        all_four_sloped_walls();
    }
}

module candidate_assembly_iso() {
    upper_long_tube();
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.86, 0.13, 0.08]) front_two_sloped_walls();
    color([0.62, 0.12, 0.52]) back_two_sloped_walls();
    vertical_joint_screw();
}

module candidate_front_xz() {
    // +Y FRONT only: both -X and +X walls are shown, with the gray tube
    // intentionally omitted from this XZ check view.
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.86, 0.13, 0.08]) front_two_sloped_walls();
    vertical_joint_screw();
}

module candidate_back_xz() {
    // -Y BACK only: mirror check of the same two inward walls.
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.62, 0.12, 0.52]) back_two_sloped_walls();
    vertical_joint_screw();
}

if (PART == "candidate_clip") {
    candidate_clip();
} else if (PART == "candidate_front_xz") {
    candidate_front_xz();
} else if (PART == "candidate_back_xz") {
    candidate_back_xz();
} else {
    candidate_assembly_iso();
}
