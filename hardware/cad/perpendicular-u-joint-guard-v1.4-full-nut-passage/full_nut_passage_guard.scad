// v1.4: keep the exact v1.3 body; remove the nut-pocket floor with one
// full-depth Ø16 cylindrical subtraction. Units: mm; Z positive upwards.
// Imported v1.3 geometry contains all four triangles and the lower hooks.
use <../perpendicular-u-joint-guard-v1.3-triangular-corner-fills/candidate_triangular_corner_fills.scad>;

$fn = 48;
PART = "clip";
nut_passage_d = 16.0;

module full_depth_nut_passage() {
    // Cutter extends z=-31..39, past the whole printed z=-21..29 envelope.
    // 64 facets match the existing Ø16 pocket, avoiding a stepped profile.
    translate([0, 0, 4])
        cylinder(d = nut_passage_d, h = 70, center = true, $fn = 64);
}

module guard_v1_4() {
    difference() {
        candidate_print_solid();
        full_depth_nut_passage();
    }
}

guard_v1_4();
