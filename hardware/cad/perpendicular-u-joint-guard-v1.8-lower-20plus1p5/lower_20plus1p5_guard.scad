// v1.8, mm. Rebuild the WHOLE lower U profile to the explicit 20+1.5 rule.
// Physical blue tube z=-20..0; contact wall height=20; inward lip below it
// z=-21.5..-20. No legacy u_bottom=-21 / lip top=-19.5 in the rebuilt lower.
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.4-full-nut-passage/full_nut_passage_guard.scad>;

$fn=48;
tube_size=20;
tube_top_z=0;
tube_bottom_z=tube_top_z-tube_size; // -20
lip_thickness_z=1.5;
lower_bottom_z=tube_bottom_z-lip_thickness_z; // -21.5
wall_thickness_x=5;
u_clearance_x=0.8;
inner_width_x=tube_size+u_clearance_x; // 20.8
outer_width_x=inner_width_x+2*wall_thickness_x; // 30.8
hook_depth_x=3.5;
u_inner_y=10;
u_outer_y=33; // original 21 + 12 mm along BLUE tube Y
upper_joint_overlap_z=0.1;

assert(tube_top_z-lower_bottom_z==21.5, "下部总高应为20+1.5=21.5 mm");
assert(2*u_inner_y==20, "中央Y通道应保持20 mm");

module upper_v1_5_preserved() {
    // Keep the accepted upper body. The 0.1 mm overlap is entirely within
    // the original arm footprint, ensuring a solid join without changing
    // the final upper shape or extending the new Y segments above z=0.
    intersection() {
        guard_v1_5();
        translate([-60,-60,-upper_joint_overlap_z])
            cube([120,120,70]);
    }
}

module lower_u_hooks() {
    // Same hook_depth_x, wall and X-clearance logic as the source v0.7 U.
    // Only Z is deliberately corrected to the new user's 20+1.5 definition.
    hook_xc=outer_width_x/2-wall_thickness_x/2-hook_depth_x/2; // 11.15
    for(yc=[-(u_inner_y+u_outer_y)/2,(u_inner_y+u_outer_y)/2])
        for(s=[-1,1])
            translate([s*hook_xc,yc,tube_bottom_z-lip_thickness_z/2])
                cube([hook_depth_x,u_outer_y-u_inner_y,lip_thickness_z],center=true);
}

module rebuilt_lower_u_pair() {
    wall_xc=inner_width_x/2+wall_thickness_x/2; // 12.9
    for(yc=[-(u_inner_y+u_outer_y)/2,(u_inner_y+u_outer_y)/2])
        for(s=[-1,1])
            translate([s*wall_xc,yc,(lower_bottom_z+tube_top_z)/2])
                cube([wall_thickness_x,u_outer_y-u_inner_y,
                      tube_top_z-lower_bottom_z],center=true);
    lower_u_hooks();
}

module guard_v1_8() {
    difference() {
        union() {
            upper_v1_5_preserved();
            rebuilt_lower_u_pair();
        }
        full_depth_nut_passage();
        upper_pipe_vertical_entry_slot();
    }
}

guard_v1_8();
