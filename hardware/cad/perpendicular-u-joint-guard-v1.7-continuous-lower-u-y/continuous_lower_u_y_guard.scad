// v1.7 candidate, mm: prolong the original U/retaining-hook cross-section
// along the BLUE LOWER TUBE axis Y. No v1.6 geometry is imported.
// Front U: y=10..33; rear U: y=-33..-10. Original inner faces stay +/-10.
// Lower extension range: z=-21..+0.5, height 21.5. Physical tubes and original
// hook z=-21..-19.5 are unchanged. The top 0.5 mm reuses the original upper
// web transition in u_plate(), i.e. the same profile throughout the new span.
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.4-full-nut-passage/full_nut_passage_guard.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn = 48;
outer_y_extension = 12;
lower_u_inner_y = 10;
original_lower_u_outer_y = 21;
lower_u_outer_y = original_lower_u_outer_y + outer_y_extension; // 33
lower_segment_bottom_z = -21;
lower_segment_top_z = 0.5;

assert(2*lower_u_inner_y == 20, "中央通道应保持 20 mm");
assert(lower_segment_top_z-lower_segment_bottom_z == 21.5,
       "连续延长段必须覆盖 Z=-21..+0.5，共21.5 mm");

module prolonged_lower_u(y0, y1) {
    // One uninterrupted extrusion over the WHOLE new U-plate depth, not a
    // pair of external substitute blocks. u_plate() is the original model's
    // authoritative cross-section, including its actual inward lower hooks.
    intersection() {
        u_plate(y0, y1);
        translate([-40,-40,lower_segment_bottom_z])
            cube([80,80,lower_segment_top_z-lower_segment_bottom_z]);
    }
}

module continuous_lower_u_pair() {
    prolonged_lower_u(lower_u_inner_y, lower_u_outer_y);
    prolonged_lower_u(-lower_u_outer_y, -lower_u_inner_y);
}

module guard_v1_7() {
    difference() {
        union() {
            guard_v1_5();
            // Original 11 mm and new 12 mm spans are evaluated as a single
            // 23 mm-deep U profile; overlap with the original is volumetric.
            continuous_lower_u_pair();
        }
        full_depth_nut_passage();
        upper_pipe_vertical_entry_slot();
    }
}

guard_v1_7();
