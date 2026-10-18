// v1.6 X-extension candidate, mm. Keep v1.5 geometry; add lower outer blocks.
// X ends ±15.4 -> ±27.4, 12 mm per side. Y stays [-21,-10] / [10,21].
// Existing lower tube z=-20..0; original snap hook z=-21..-19.5.
// Their union spans 21 mm due to 0.5 mm intentional overlap. To honor the
// spoken 21.5 mm added-block height without moving existing features, anchor
// at the original printed bottom -21 and end the new blocks at z=+0.5.
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.4-full-nut-passage/full_nut_passage_guard.scad>;

$fn = 48;
x_outward_extension = 12;
original_outer_x = 15.4;
extension_bottom_z = -21;
extension_height_z = 21.5;
extension_top_z = extension_bottom_z + extension_height_z; // +0.5
extension_overlap_x = 0.1;

module lower_x_extensions() {
    // Four outer blocks join the existing four lower U arms with positive
    // 0.1 mm X overlap. No translations/scales of any original feature.
    for (y0 = [-21,10]) {
        translate([original_outer_x-extension_overlap_x, y0, extension_bottom_z])
            cube([x_outward_extension+extension_overlap_x, 11, extension_height_z]);
        translate([-original_outer_x-x_outward_extension, y0, extension_bottom_z])
            cube([x_outward_extension+extension_overlap_x, 11, extension_height_z]);
    }
}

module guard_v1_6_x() {
    difference() {
        union() { guard_v1_5(); lower_x_extensions(); }
        full_depth_nut_passage();
        upper_pipe_vertical_entry_slot();
    }
}

guard_v1_6_x();
