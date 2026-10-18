// Candidate v0.9: v0.7 eaves12 plus a solid sloped wall on the -X end.
//
// Coordinate contract (same as v0.7):
//   x = barrier long direction
//   y = front/back direction
//   z = vertical direction
//
// This file deliberately imports v0.7 with `use` and does not modify it.
// The imported v0.7 model already contains the accepted +/-12 mm X eaves,
// the round top nut pocket, the vertical through-hole, and the 20 mm Y gap.

use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;

PART = "candidate_iso";

// These values are explicit here so the candidate remains reviewable even
// though OpenSCAD `use` imports modules rather than the source's top-level
// variables.
candidate_roof_x_min = -27.4; // v0.7 roof width 54.8, eaves12
candidate_roof_bottom_z = 21.0;
candidate_roof_top_z = 29.0;
sloped_wall_run_x = 12.0;
sloped_wall_end_x = candidate_roof_x_min - sloped_wall_run_x;
sloped_wall_landing_z = 0.0; // blue lower tube's top surface
sloped_wall_depth_y = 5.0;  // solid plate depth, not a thin visual line

assert(sloped_wall_landing_z == 0,
       "蓝色下方方管上表面在当前坐标中必须是 z=0");
assert(sloped_wall_run_x > 0, "斜墙必须向 -X 延伸");
assert(sloped_wall_end_x < candidate_roof_x_min,
       "斜墙下端必须位于屋檐 -X 端之外");

module solid_sloped_wall_candidate() {
    // A triangular prism in the XZ plane, extruded 5 mm along Y.  Its full
    // vertical roof-end edge overlaps the existing roof from z=21..29, while
    // its diagonal edge travels toward -X and ends exactly at z=0.
    // This is a solid wall/gusset, not a line or decorative rib.
    rotate([90, 0, 0])
        linear_extrude(height = sloped_wall_depth_y,
                       center = true,
                       convexity = 10)
            polygon(points = [
                [candidate_roof_x_min, candidate_roof_bottom_z],
                [candidate_roof_x_min, candidate_roof_top_z],
                [sloped_wall_end_x, sloped_wall_landing_z]
            ]);
}

module candidate_clip() {
    // The imported v0.7 body remains one printable solid; the new prism is
    // overlapped into the -X roof edge so the union is connected.
    union() {
        double_u_clip();
        solid_sloped_wall_candidate();
    }
}

module candidate_assembly_iso() {
    // Context only: gray upper tube is along X, blue lower tube is along Y.
    upper_long_tube();
    lower_cross_tube();
    // Keep the candidate wall visually distinct in review renders.  The STL
    // export uses candidate_clip(), so these review colors do not split the
    // printable part into separate objects.
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.82, 0.16, 0.08]) solid_sloped_wall_candidate();
    vertical_joint_screw();
}

module candidate_assembly_xz() {
    // Deliberately omit the gray upper tube in this XZ check view.
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    color([0.82, 0.16, 0.08]) solid_sloped_wall_candidate();
    vertical_joint_screw();
}

if (PART == "candidate_clip") {
    candidate_clip();
} else if (PART == "candidate_xz") {
    candidate_assembly_xz();
} else {
    candidate_assembly_iso();
}
