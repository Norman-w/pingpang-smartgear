// v1.9, mm: two Y-mirrored solid end ramps on the accepted v1.8 lower U.
// Blue tube top is z=0; ramp root |y|=21 rises 10 mm, tip |y|=33 rises 3 mm.
use <../perpendicular-u-joint-guard-v1.8-lower-20plus1p5/lower_20plus1p5_guard.scad>;
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.4-full-nut-passage/full_nut_passage_guard.scad>;

$fn=48;
ramp_root_y=21;
ramp_tip_y=33;
ramp_root_z=10;
ramp_tip_z=3;
u_inner_half_x=10.4; // v1.8 X inner width 20.8
ramp_sidewall_overlap_x=1;
ramp_half_x=u_inner_half_x+ramp_sidewall_overlap_x; // 11.4 / width 22.8
ramp_root_overlap_y=0.2;
ramp_joint_overlap_z=0.2;

module positive_end_ramp_prism() {
    // Local XY polygon is the physical YZ contour; extrusion maps to X.
    // The visible 21..33 interval is exactly a trapezoid: 10 -> 3 mm.
    // A hidden 0.2 mm root lap holds the 10 mm height inside the old body.
    rotate([90,0,90])
        linear_extrude(height=2*ramp_half_x,center=true,convexity=10)
            polygon(points=[
                [ramp_root_y-ramp_root_overlap_y,0],
                [ramp_tip_y,0],
                [ramp_tip_y,ramp_tip_z],
                [ramp_root_y,ramp_root_z],
                [ramp_root_y-ramp_root_overlap_y,ramp_root_z]
            ]);
}

module ramp_prisms_pair() {
    positive_end_ramp_prism();
    mirror([0,1,0]) positive_end_ramp_prism();
}

module sidewall_join_keys() {
    // Volumetric joins at both supporting side walls. The z<0 halves lie
    // entirely inside the existing v1.8 arms, so the lower geometry does not
    // change. Contact width is 1 mm in X on each side, over all 12 mm of Y.
    for(s=[-1,1]) for(y0=[-ramp_tip_y,ramp_root_y])
        translate([s*(u_inner_half_x+ramp_sidewall_overlap_x/2),
                   y0+(ramp_tip_y-ramp_root_y)/2,0])
            cube([ramp_sidewall_overlap_x,ramp_tip_y-ramp_root_y,
                  2*ramp_joint_overlap_z],center=true);
}

module mirrored_end_reinforcement() {
    ramp_prisms_pair();
    sidewall_join_keys();
}

module guard_v1_9() {
    difference() {
        union() { guard_v1_8(); mirrored_end_reinforcement(); }
        full_depth_nut_passage();
        upper_pipe_vertical_entry_slot();
    }
}

guard_v1_9();
