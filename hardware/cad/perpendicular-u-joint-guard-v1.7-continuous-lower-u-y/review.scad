// v1.7 real SCAD reviews, cross-section identity and installation checks.
use <continuous_lower_u_y_guard.scad>;
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.3-triangular-corner-fills/candidate_triangular_corner_fills.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;

$fn=48;
VIEW="assembly";
OFFSET_Z=0;

module added_material() { difference() { guard_v1_7(); guard_v1_5(); } }
module section_yz(x=13) {
    intersection() { children(); translate([x-0.025,-65,-30]) cube([0.05,130,65]); }
}
module section_xz(y=27) {
    intersection() { children(); translate([-65,y-0.025,-30]) cube([130,0.05,65]); }
}
module lower_xy_slice() {
    intersection() { children(); translate([-65,-65,-10.1]) cube([130,130,0.2]); }
}
module label_yz(value,y,z,size=3,c=[0.1,0.12,0.15]) {
    color(c) translate([14,y,z]) rotate([90,0,90])
        linear_extrude(height=0.1)
            text(value,font="Arial Unicode MS",size=size,valign="center");
}
module label_xz(value,x,z,size=3,c=[0.1,0.12,0.15]) {
    color(c) translate([x,-2,z]) rotate([90,0,0])
        linear_extrude(height=0.1)
            text(value,font="Arial Unicode MS",size=size,valign="center");
}
module label_xy(value,x,y,size=3,c=[0.1,0.12,0.15]) {
    color(c) translate([x,y,-8]) linear_extrude(height=0.1)
        text(value,font="Arial Unicode MS",size=size,valign="center");
}
module line_yz(a,b,c=[0.16,0.2,0.23]) {
    color(c) hull() {
        translate([14,a[0],a[1]]) sphere(d=0.22,$fn=12);
        translate([14,b[0],b[1]]) sphere(d=0.22,$fn=12);
    }
}
module y_dimension(a,b,z,caption) {
    line_yz([a,z],[b,z]);
    line_yz([a,z-1],[a,z+1]); line_yz([b,z-1],[b,z+1]);
    label_yz(caption,(a+b)/2-4.5,z-3,2.7);
}
module assembly() {
    upper_long_tube(); lower_cross_tube(); vertical_joint_screw();
    // Single orange union is the actual printable part, showing continuous
    // lower arms rather than visually detached colored substitute blocks.
    color([0.96,0.39,0.08]) translate([0,0,OFFSET_Z]) guard_v1_7();
    // Source-coordinate reference triad offset outside the model.
    color([0.48,0.51,0.55]) {
        translate([-64,-61,-27]) rotate([0,90,0]) cylinder(d=1.1,h=27);
        translate([-37,-61,-27]) rotate([0,90,0]) cylinder(r1=2.7,r2=0,h=6);
    }
    color([0.16,0.43,0.82]) {
        translate([-64,-61,-27]) rotate([-90,0,0]) cylinder(d=1.1,h=27);
        translate([-64,-34,-27]) rotate([-90,0,0]) cylinder(r1=2.7,r2=0,h=6);
    }
    color([0.12,0.65,0.24]) {
        translate([-64,-61,-27]) cylinder(d=1.1,h=27);
        translate([-64,-61,0]) cylinder(r1=2.7,r2=0,h=6);
    }
    for(entry=[
        ["+X 灰管",[-28,-61,-26],[0.38,0.4,0.44]],
        ["+Y 蓝管",[-64,-24,-26],[0.16,0.43,0.82]],
        ["+Z",[-64,-61,10],[0.12,0.65,0.24]]
    ]) color(entry[2]) translate(entry[1]) linear_extrude(height=0.2)
        text(entry[0],font="Arial Unicode MS",size=3.6);
}
module side_yz(candidate=true,title=true) {
    color([0.96,0.39,0.08]) section_yz() guard_v1_5();
    if(candidate) color([0.12,0.57,0.65]) section_yz() added_material();
    color([0.58,0.61,0.66]) section_yz() upper_long_tube();
    if(title) {
        label_yz("v1.7 沿蓝管 Y 连续拉长 / X=13 剖面",-47,45,3.5);
        label_yz("橙色原结构，青色同截面延长；接合处无空隙",-47,38,2.8);
    }
    if(candidate) {
        y_dimension(-33,-21,-29,"12 mm");
        y_dimension(21,33,-29,"12 mm");
        line_yz([-38,-21],[-38,0.5]);
        line_yz([-39,-21],[-37,-21]); line_yz([-39,0.5],[-37,0.5]);
        label_yz("Z=+0.5",-54,0.5,2.7);
        label_yz("Z=-21",-54,-21,2.7);
        label_yz("21.5 mm",-57,-10,2.8);
    }
    label_yz("-Y（蓝管方向）",-38,-39,2.8);
    label_yz("+Y（蓝管方向）",13,-39,2.8);
}
module comparison() {
    translate([0,-66,0]) {
        side_yz(false,false);
        label_yz("基线 v1.5",-28,39,4);
        y_dimension(-21,21,-29,"外宽 42 mm");
    }
    translate([0,66,0]) {
        side_yz(true,false);
        label_yz("v1.7 连续拉长同一 U 截面",-33,39,3.7);
    }
}
module end_xz() {
    // Section at the new segment y=27: this is the full ORIGINAL U profile,
    // including both arms, the bottom hooks and the z=0..0.5 upper transition.
    color([0.96,0.39,0.08]) section_xz() guard_v1_7();
    color([0.28,0.45,0.78]) section_xz() lower_cross_tube();
    label_xz("v1.7 延长段端部 / Y=27 的 XZ 剖面",-43,14,3.5);
    label_xz("与原段 Y=15.5 复用完全相同的 U/底扣截面",-43,8,2.8);
    label_xz("Z=+0.5：延长段顶部",25,0.5,2.7);
    label_xz("蓝管顶面 Z=0",25,-5,2.7,[0.18,0.3,0.6]);
    label_xz("蓝管底面 Z=-20",25,-20,2.7,[0.18,0.3,0.6]);
    label_xz("卡扣 Z=-21..-19.5",25,-26,2.7);
    label_xz("延长总高 21.5 mm：Z=-21..+0.5",-43,-34,3.0);
    label_xz("原管子与 1.5 mm 卡扣的 Z 位置均未移动",-43,-40,2.8);
}
module xy_check() {
    color([0.96,0.39,0.08]) lower_xy_slice() guard_v1_5();
    color([0.12,0.57,0.65]) lower_xy_slice() added_material();
    color([0.28,0.45,0.78]) lower_xy_slice() lower_cross_tube();
    label_xy("v1.7 下部 XY 剖面：沿蓝管 Y 连续延长",-48,48,3.3);
    label_xy("+Y",24,36,3,[0.18,0.3,0.6]);
    label_xy("+33",22,33,2.6); label_xy("+21 原端面",22,21,2.6);
    label_xy("-21 原端面",22,-21,2.6); label_xy("-33",22,-33,2.6);
    label_xy("中央 Y=-10..+10 =20 mm",-47,-45,3.0);
    label_xy("X 下部外宽仍为30.8 mm；灰管沿 X",-47,-51,2.8);
}
module allowed_hooks() {
    // Same source hook XZ profile; longer Y spans, with no change of height,
    // inner reach or the allowed 0.6 mm elastic engagement with the blue tube.
    for(yc=[-21.5,21.5]) for(xc=[-11.15,11.15])
        translate([xc,yc,-20.25]) cube([3.5,23,1.5],center=true);
}
module lower_profile_at(y) {
    intersection() {
        translate([0,-y,0]) guard_v1_7();
        translate([-40,-0.025,-21]) cube([80,0.05,21.5]);
    }
}
module symmetric_difference() {
    difference() { children(0); children(1); }
    difference() { children(1); children(0); }
}

if(VIEW=="assembly") assembly();
else if(VIEW=="side") side_yz();
else if(VIEW=="comparison") comparison();
else if(VIEW=="end") end_xz();
else if(VIEW=="xy") xy_check();
else if(VIEW=="clip") guard_v1_7();
else if(VIEW=="upper_motion_obstruction") {
    intersection() {
        guard_v1_7();
        hull() { upper_long_tube(); translate([0,0,-52]) upper_long_tube(); }
    }
} else if(VIEW=="nut_motion_obstruction") {
    intersection() {
        guard_v1_7();
        hull() { vertical_joint_screw(); translate([0,0,-52]) vertical_joint_screw(); }
    }
} else if(VIEW=="rigid_lower_motion_obstruction") {
    intersection() {
        difference() { guard_v1_7(); allowed_hooks(); }
        hull() { lower_cross_tube(); translate([0,0,-52]) lower_cross_tube(); }
    }
} else if(VIEW=="passage_obstruction") {
    intersection() {
        guard_v1_7();
        translate([0,0,4]) cylinder(d=15.999,h=70,center=true,$fn=64);
    }
} else if(VIEW=="original_material_removed") {
    difference() { guard_v1_5(); guard_v1_7(); }
} else if(VIEW=="triangles_changed") {
    difference() { all_four_triangular_fills(); guard_v1_7(); }
} else if(VIEW=="front_profile_difference") {
    symmetric_difference() { lower_profile_at(15.5); lower_profile_at(27); }
} else if(VIEW=="back_profile_difference") {
    symmetric_difference() { lower_profile_at(-15.5); lower_profile_at(-27); }
} else if(VIEW=="old_hook_region_changed") {
    intersection() {
        union() {
            difference() { guard_v1_5(); guard_v1_7(); }
            difference() { guard_v1_7(); guard_v1_5(); }
        }
        union() {
            for(yc=[-15.5,15.5]) for(xc=[-11.15,11.15])
                translate([xc,yc,-20.25]) cube([3.5,11,1.5],center=true);
        }
    }
} else if(VIEW=="seated_elastic_hook_interference") {
    intersection() { guard_v1_7(); lower_cross_tube(); }
}
