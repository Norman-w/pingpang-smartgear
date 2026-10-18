// v1.6 candidate, mm. Extend only the lower U arms and retaining hooks.
// Interpretation of 'from the bottom upwards': z=-21..0 (blue foot top).
// Front outer face +21 -> +33; rear outer face -21 -> -33, 12 mm each.
// The v1.5 body, triangle XZ profiles and existing snap hooks are inherited.
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.4-full-nut-passage/full_nut_passage_guard.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
y_outward_extension = 12;
lower_extension_bottom_z = -21;
lower_extension_top_z = 0;
extension_joint_overlap = 0.1;

module lower_extension_band(y0, y1) {
    // Reuse the real v0.7 U cross-section, including its 1.5 mm hook.
    // Clipping to z<=0 excludes the upper web, roof and corner triangles.
    intersection() {
        u_plate(y0, y1);
        translate([-40, -50, lower_extension_bottom_z])
            cube([80, 100, lower_extension_top_z - lower_extension_bottom_z]);
    }
}

module lower_y_extensions() {
    lower_extension_band(21 - extension_joint_overlap, 21 + y_outward_extension);
    lower_extension_band(-21 - y_outward_extension, -21 + extension_joint_overlap);
}

module guard_v1_6() {
    difference() {
        union() {
            guard_v1_5();
            lower_y_extensions();
        }
        // Final operations keep the accepted full-depth nut passage and the
        // v1.5 rigid upper-tube entry clearance authoritative.
        full_depth_nut_passage();
        upper_pipe_vertical_entry_slot();
    }
}

guard_v1_6();
