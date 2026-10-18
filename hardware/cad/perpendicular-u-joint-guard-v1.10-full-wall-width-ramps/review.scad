// Actual SCAD renders; magenta = complete ramps, teal = lower extension.
use <full_wall_width_ramps_guard.scad>;
use <../perpendicular-u-joint-guard-v1.9-mirrored-end-ramps/mirrored_end_ramps_guard.scad>;
use <../perpendicular-u-joint-guard-v1.9-mirrored-end-ramps/review.scad>;
use <../perpendicular-u-joint-guard-v1.8-lower-20plus1p5/lower_20plus1p5_guard.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;
$fn=48;
VIEW="assembly";

module ramps_added() { difference() { guard_v1_10(); guard_v1_8(); } }
module colored_current() {
    color([0.96,0.39,0.08]) region_original_length();
    color([0.12,0.57,0.65]) region_v1_8_extension();
    color([0.76,0.16,0.49]) ramps_added();
}
module assembly_current() {
    upper_long_tube(); lower_cross_tube(); vertical_joint_screw();
    colored_current(); coordinates();
}
module xz_current() {
    color([0.96,0.39,0.08]) section_xz() region_original_length();
    color([0.12,0.57,0.65]) section_xz() region_v1_8_extension();
    color([0.76,0.16,0.49]) section_xz() ramps_added();
    color([0.28,0.45,0.78]) section_xz() lower_cross_tube();
    label_xz("v1.10 / Y=27 的 XZ截面",-35,23,3.4);
    label_xz("梅红斜坡盖满两侧立墙，X=-15.4..+15.4",-43,17,2.8);
    line_xz([-15.4,10],[15.4,10]);
    line_xz([-15.4,9],[-15.4,11]); line_xz([15.4,9],[15.4,11]);
    label_xz("30.8 mm",-7,13,2.8);
    label_xz("墙厚5 mm",19,-7,2.8);
    label_xz("蓝管Z=-20..0",19,-13,2.8);
    label_xz("底扣Z=-21.5..-20，厚1.5 mm不变",-36,-29,2.8);
    label_xz("+X →   +Z ↑",-17,-36,2.8);
}
module xy_current() {
    module slab() { intersection() { children(); translate([-60,-60,0.5]) cube([120,120,0.05]); } }
    color([0.96,0.39,0.08]) slab() region_original_length();
    color([0.12,0.57,0.65]) slab() region_v1_8_extension();
    color([0.76,0.16,0.49]) slab() ramps_added();
    color([0.28,0.45,0.78]) intersection() {
        lower_cross_tube(); translate([-60,-60,-0.1]) cube([120,120,0.05]);
    }
    for(s=[-1,1]) color([0.1,0.12,0.15]) translate([-65,s*66,2])
        linear_extrude(height=0.1)
            text(s>0?"+Y端：斜坡外缘与墙齐平":"-Y端：同样盖满立墙",font="Arial Unicode MS",size=3);
    color([0.1,0.12,0.15]) translate([-65,-76,2]) linear_extrude(height=0.1)
        text("XY截面 Z=0.5 / X向右 Y向上",font="Arial Unicode MS",size=3);
}

if(VIEW=="assembly") assembly_current();
else if(VIEW=="xz") xz_current();
else if(VIEW=="xy") xy_current();
else if(VIEW=="clip") guard_v1_10();
else if(VIEW=="original_removed") difference() { guard_v1_9(); guard_v1_10(); }
else if(VIEW=="lower_changed") intersection() {
    symmetric_difference() { guard_v1_9(); guard_v1_10(); }
    translate([-60,-60,-30]) cube([120,120,29.999]);
}
else if(VIEW=="central_channel_changed") intersection() {
    symmetric_difference() { guard_v1_9(); guard_v1_10(); } centre_zone();
}
else if(VIEW=="mirror_difference") symmetric_difference() {
    guard_v1_10(); mirror([0,1,0]) guard_v1_10();
}
else if(VIEW=="passage_obstruction") intersection() {
    guard_v1_10(); translate([0,0,4]) cylinder(d=15.999,h=70,center=true,$fn=64);
}
else if(VIEW=="upper_motion_obstruction") intersection() {
    guard_v1_10(); hull() { upper_long_tube(); translate([0,0,-53]) upper_long_tube(); }
}
