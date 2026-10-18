use <fit_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.10-full-wall-width-ramps/full_wall_width_ramps_guard.scad>;
use <../perpendicular-u-joint-guard-v1.9-mirrored-end-ramps/review.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;
$fn=48;
VIEW="assembly";

module centre_band() { translate([-60,-21.5,-40]) cube([120,43,100]); }
module lower_half() { translate([-60,-60,-40]) cube([120,120,40]); }
module current_colored() {
    color([0.96,0.39,0.08]) intersection() { guard_v1_11(); centre_band(); }
    color([0.12,0.57,0.65]) intersection() {
        difference() { guard_v1_11(); centre_band(); } lower_half();
    }
    color([0.76,0.16,0.49]) difference() {
        guard_v1_11(); centre_band(); lower_half();
    }
}
module current_section_xz(y=27.5) {
    color([0.96,0.39,0.08]) section_xz(y) intersection() { guard_v1_11(); centre_band(); }
    color([0.12,0.57,0.65]) section_xz(y) intersection() {
        difference() { guard_v1_11(); centre_band(); } lower_half();
    }
    color([0.76,0.16,0.49]) section_xz(y) difference() {
        guard_v1_11(); centre_band(); lower_half();
    }
    color([0.28,0.45,0.78]) section_xz(y) lower_cross_tube();
}
module assembly_current() {
    upper_long_tube(); lower_cross_tube(); vertical_joint_screw();
    current_colored(); coordinates();
}
module xz_dimensions() {
    current_section_xz();
    label_xz("v1.11 / XZ截面 Y=27.5",-42,26,3.6);
    label_xz("X基准21 + 原打印间隙0.8 = 内宽21.8 mm",-42,20,2.8);
    line_xz([-10.9,-7],[10.9,-7]);
    label_xz("21.8",-5,-5,2.7);
    line_xz([-20,0],[-20,-22]);
    line_xz([-21,0],[-19,0]); line_xz([-21,-22],[-19,-22]);
    label_xz("22 mm",-35,-12,2.8);
    label_xz("蓝管仍20×20",20,-6,2.7,[0.18,0.3,0.6]);
    label_xz("底部新增2 mm容纳余量",20,-14,2.7);
    label_xz("内扣厚1.5 / 对20管咬合0.6 mm",-40,-32,2.8);
    label_xz("梅红斜坡全宽31.8，仍盖满5 mm立墙",-40,-38,2.8);
    label_xz("+X →    +Z ↑",-16,-44,2.8);
}
module yz_dimensions() {
    color([0.96,0.39,0.08]) section_yz() guard_v1_11();
    color([0.58,0.61,0.66]) section_yz() upper_long_tube();
    color([0.28,0.45,0.78]) section_yz() lower_cross_tube();
    label_yz("v1.11 / YZ中心截面 X=0",-43,49,3.5);
    label_yz("灰管槽Y宽21；Z容纳高22；盖下另留1",-43,42,2.9);
    line_yz([-10.5,35],[10.5,35]);
    line_yz([-10.5,34],[-10.5,36]); line_yz([10.5,34],[10.5,36]);
    label_yz("21 mm",-5,38,2.8);
    line_yz([0.5,0],[0.5,22]);
    label_yz("22",1.5,10,2.8);
    label_yz("实际灰管仍20×20；屋盖底面Z=23",-43,-30,2.9);
    label_yz("+Y →    +Z ↑",-15,-37,2.8);
}
module top_current() {
    color([0.96,0.39,0.08]) guard_v1_11();
    upper_long_tube(); lower_cross_tube();
}
module max_gray() { translate([0,0,11]) cube([120,21,22],center=true); }
module max_blue() { translate([0,0,-11]) cube([21,120,22],center=true); }
module tolerance_envelope() {
    minkowski() { children(); cube([0.002,0.002,0.002],center=true); }
}

if(VIEW=="assembly") assembly_current();
else if(VIEW=="xz") xz_dimensions();
else if(VIEW=="yz") yz_dimensions();
else if(VIEW=="top") top_current();
else if(VIEW=="baseline_difference") symmetric_difference() {
    guard_v1_11(20,20,20); guard_v1_10();
}
else if(VIEW=="baseline_tolerance_difference") {
    // v1.10 X-only ramp scaling has sub-micron floating-point outer-plane
    // residue. Verify shape equivalence with an explicit 0.001 mm bound.
    difference() { guard_v1_11(20,20,20); tolerance_envelope() guard_v1_10(); }
    difference() { guard_v1_10(); tolerance_envelope() guard_v1_11(20,20,20); }
}
else if(VIEW=="mirror_difference") symmetric_difference() {
    guard_v1_11(); mirror([0,1,0]) guard_v1_11();
}
else if(VIEW=="passage_obstruction") intersection() {
    guard_v1_11(); cylinder(d=15.999,h=160,center=true,$fn=64);
}
else if(VIEW=="max_gray_motion_obstruction") intersection() {
    guard_v1_11(); hull() { max_gray(); translate([0,0,-60]) max_gray(); }
}
else if(VIEW=="max_blue_rigid_motion_obstruction") intersection() {
    difference() { guard_v1_11(); guard_v1_11(feature="hooks"); }
    hull() { max_blue(); translate([0,0,-60]) max_blue(); }
}
else if(VIEW=="screw_motion_obstruction") intersection() {
    guard_v1_11(); hull() { vertical_joint_screw(); translate([0,0,-60]) vertical_joint_screw(); }
}
else if(VIEW=="clip") guard_v1_11();
