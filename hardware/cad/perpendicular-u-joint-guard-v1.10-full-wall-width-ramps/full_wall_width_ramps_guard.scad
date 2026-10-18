// v1.10, mm. X=gray tube; Y=blue foot; Z=up.
// Only widen the v1.9 ramps in X to cover the entire 5 mm side walls.
// Preserve both YZ ramp profiles, downward installation and elastic lips.
use <../perpendicular-u-joint-guard-v1.9-mirrored-end-ramps/mirrored_end_ramps_guard.scad>;
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.4-full-nut-passage/full_nut_passage_guard.scad>;

$fn=48;
inner_half_x=10.4;
wall_x=5;
outer_half_x=inner_half_x+wall_x; // 15.4; final ramp width 30.8
v1_9_ramp_width_x=22.8;

module full_wall_width_ramps() {
    // Reuse the actual accepted paired profiles, transform X only.
    scale([2*outer_half_x/v1_9_ramp_width_x,1,1]) ramp_prisms_pair();
    // Positive-volume joins across the full wall top. Below Z=0 these
    // keys are wholly inside the existing walls, not new lip geometry.
    for(s=[-1,1]) for(yc=[-27,27])
        translate([s*(inner_half_x+wall_x/2),yc,0])
            cube([wall_x,12,0.4],center=true);
}

module guard_v1_10() {
    difference() {
        union() { guard_v1_9(); full_wall_width_ramps(); }
        full_depth_nut_passage();
        upper_pipe_vertical_entry_slot();
    }
}

guard_v1_10();
