// v1.5: v1.4 Ø16 full nut passage + minimum downward-entry upper-tube slot.
// Units mm. X: upper long tube; Y: blue foot/front-back; Z: up.
use <../perpendicular-u-joint-guard-v1.4-full-nut-passage/full_nut_passage_guard.scad>;

$fn = 48;

module upper_pipe_vertical_entry_slot() {
    // Fixed gray upper tube: x=-60..60, y=-10..10, z=0..20.
    // While the clip moves down, that tube sweeps upward in clip coordinates.
    // A bottom-open slot ending at z=20 covers its whole relevant sweep in
    // the printed z=-21..29 envelope. Roof underside remains at z=21.
    // Preserve exact 20 mm Y width rather than silently adding fit clearance.
    translate([-60, -10, -31]) cube([120, 20, 51]);
}

module guard_v1_5() {
    difference() {
        guard_v1_4();
        upper_pipe_vertical_entry_slot();
    }
}

guard_v1_5();
