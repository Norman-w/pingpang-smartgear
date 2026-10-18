// v1.8 real SCAD assembly, corrected 20+1.5 profile and diagnostics.
use <lower_20plus1p5_guard.scad>;
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.3-triangular-corner-fills/candidate_triangular_corner_fills.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;
$fn=48;
VIEW="assembly";

module label_xz(value,x,z,size=3,c=[0.1,0.12,0.15]) {
    color(c) translate([x,-2,z]) rotate([90,0,0]) linear_extrude(height=0.1)
        text(value,font="Arial Unicode MS",size=size,valign="center");
}
module label_yz(value,y,z,size=3,c=[0.1,0.12,0.15]) {
    color(c) translate([14,y,z]) rotate([90,0,90]) linear_extrude(height=0.1)
        text(value,font="Arial Unicode MS",size=size,valign="center");
}
module line_xz(a,b,c=[0.16,0.2,0.23]) {
    color(c) hull() {
        translate([a[0],-1,a[1]]) sphere(d=0.22,$fn=12);
        translate([b[0],-1,b[1]]) sphere(d=0.22,$fn=12);
    }
}
module line_yz(a,b,c=[0.16,0.2,0.23]) {
    color(c) hull() {
        translate([14,a[0],a[1]]) sphere(d=0.22,$fn=12);
        translate([14,b[0],b[1]]) sphere(d=0.22,$fn=12);
    }
}
module section_xz(y=27) {
    intersection() { children(); translate([-65,y-0.025,-32]) cube([130,0.05,70]); }
}
module section_yz(x=13) {
    intersection() { children(); translate([x-0.025,-65,-32]) cube([0.05,130,70]); }
}
module origin_length_zone() { translate([-60,-21,-40]) cube([120,42,100]); }
module coordinates() {
    for(a=[0,1,2]) {
        c=a==0?[0.48,0.51,0.55]:a==1?[0.16,0.43,0.82]:[0.12,0.65,0.24];
        r=a==0?[0,90,0]:a==1?[-90,0,0]:[0,0,0];
        p=[-64,-61,-27];
        color(c) translate(p) rotate(r) {
            cylinder(d=1.1,h=27);
            translate([0,0,27]) cylinder(r1=2.7,r2=0,h=6);
        }
    }
    for(entry=[
        ["+X 灰管",[-28,-61,-26],[0.38,0.4,0.44]],
        ["+Y 蓝管",[-64,-24,-26],[0.16,0.43,0.82]],
        ["+Z",[-64,-61,10],[0.12,0.65,0.24]]
    ]) color(entry[2]) translate(entry[1]) linear_extrude(height=0.2)
        text(entry[0],font="Arial Unicode MS",size=3.6);
}
module assembly() {
    upper_long_tube(); lower_cross_tube(); vertical_joint_screw();
    color([0.96,0.39,0.08]) guard_v1_8();
    coordinates();
}
module y_continuity() {
    // Colors indicate length zones of the SAME rebuilt solid, not separate
    // pieces: original length |y|<=21 and continuous new length 21..33.
    color([0.96,0.39,0.08]) section_yz() intersection() {
        guard_v1_8(); origin_length_zone();
    }
    color([0.12,0.57,0.65]) section_yz() difference() {
        guard_v1_8(); origin_length_zone();
    }
    color([0.58,0.61,0.66]) section_yz() upper_long_tube();
    label_yz("v1.8 沿蓝管 Y 连续延长 / X=13 剖面",-46,44,3.5);
    label_yz("同一截面：前后各由11 mm连续延长至23 mm",-46,37,2.9);
    for(pair=[[-33,-21],[21,33]]) {
        line_yz([pair[0],-29],[pair[1],-29]);
        line_yz([pair[0],-30],[pair[0],-28]);
        line_yz([pair[1],-30],[pair[1],-28]);
        label_yz("12 mm",(pair[0]+pair[1])/2-4.5,-32,2.7);
    }
    label_yz("Z=0",-47,0,2.9);
    label_yz("Z=-21.5",-53,-21.5,2.9);
    label_yz("21.5 mm",-54,-10,2.9);
    line_yz([-38,-21.5],[-38,0]);
    line_yz([-39,-21.5],[-37,-21.5]); line_yz([-39,0],[-37,0]);
    label_yz("-Y 蓝管方向",-35,-41,2.8);
    label_yz("+Y 蓝管方向",14,-41,2.8);
}
module corrected_end_profile() {
    // Actual y=27 section in the new extension. Green is ONLY the actual
    // inward hook at -21.5..-20; there is no old lip above the blue bottom.
    color([0.96,0.39,0.08]) section_xz() difference() {
        guard_v1_8(); lower_u_hooks();
    }
    color([0.16,0.65,0.22]) section_xz() lower_u_hooks();
    color([0.28,0.45,0.78]) section_xz() lower_cross_tube();
    label_xz("v1.8 新延长端 Y=27 / XZ截面",-45,15,3.7);
    label_xz("蓝管不动：侧壁20 mm + 管底内扣1.5 mm",-45,8,3.0);
    line_xz([22,-20],[22,0]);
    line_xz([21,-20],[23,-20]); line_xz([21,0],[23,0]);
    label_xz("侧壁 20 mm",26,-8,3.1);
    label_xz("蓝管上沿 Z=0",26,0,2.8,[0.18,0.3,0.6]);
    label_xz("蓝管下沿 Z=-20",26,-20,2.8,[0.18,0.3,0.6]);
    line_xz([-22,-21.5],[-22,0]);
    line_xz([-23,-21.5],[-21,-21.5]); line_xz([-23,0],[-21,0]);
    label_xz("总高 21.5 mm",-49,-10,3);
    line_xz([10,-20.75],[24,-28]);
    label_xz("绿色内扣 1.5 mm",26,-28,3,[0.10,0.48,0.16]);
    label_xz("Z=-21.5..-20",26,-33,2.8,[0.10,0.48,0.16]);
    label_xz("新段顶部齐Z=0；无+0.5上盖；无旧-19.5高位内扣",-45,-42,2.7);
}
module xy_continuity() {
    module plane() {
        intersection() { children(); translate([-65,-65,-10.1]) cube([130,130,0.2]); }
    }
    color([0.96,0.39,0.08]) plane() intersection() { guard_v1_8(); origin_length_zone(); }
    color([0.12,0.57,0.65]) plane() difference() { guard_v1_8(); origin_length_zone(); }
    color([0.28,0.45,0.78]) plane() lower_cross_tube();
    for(entry=[
        ["v1.8 下部XY剖面：Y内面±10，外端±33",-48,47,3.3],
        ["+33",22,33,2.7],["+21 原长度分界",22,21,2.7],
        ["-21 原长度分界",22,-21,2.7],["-33",22,-33,2.7],
        ["中央20 mm保持空；蓝管沿Y，灰管沿X",-48,-46,2.9]
    ]) color([0.1,0.12,0.15]) translate([entry[1],entry[2],-8])
        linear_extrude(height=0.1)
            text(entry[0],font="Arial Unicode MS",size=entry[3],valign="center");
}
module centre_hole_section() {
    color([0.96,0.39,0.08]) section_xz(0) guard_v1_8();
    color([0.58,0.61,0.66]) section_xz(0) upper_long_tube();
    color([0.28,0.45,0.78]) section_xz(0) lower_cross_tube();
    color([0.82,0.82,0.84]) section_xz(0) vertical_joint_screw();
    label_xz("v1.8 中心Y=0 / Ø16全深螺帽通行孔",-40,42,3.6);
    label_xz("打印件孔无台阶；铁管原Ø6.2孔保持不变",-40,35,2.9);
}
module lower_profile_at(y) {
    intersection() {
        translate([0,-y,0]) guard_v1_8();
        translate([-40,-0.025,-21.5]) cube([80,0.05,21.5]);
    }
}
module symmetric_difference() {
    difference() { children(0); children(1); }
    difference() { children(1); children(0); }
}
module upper_only() {
    intersection() { children(); translate([-60,-60,0.001]) cube([120,120,70]); }
}

if(VIEW=="assembly") assembly();
else if(VIEW=="y") y_continuity();
else if(VIEW=="end") corrected_end_profile();
else if(VIEW=="xy") xy_continuity();
else if(VIEW=="hole") centre_hole_section();
else if(VIEW=="clip") guard_v1_8();
else if(VIEW=="upper_motion_obstruction") {
    intersection() { guard_v1_8(); hull() { upper_long_tube(); translate([0,0,-53]) upper_long_tube(); } }
} else if(VIEW=="nut_motion_obstruction") {
    intersection() { guard_v1_8(); hull() { vertical_joint_screw(); translate([0,0,-53]) vertical_joint_screw(); } }
} else if(VIEW=="rigid_lower_motion_obstruction") {
    intersection() {
        difference() { guard_v1_8(); lower_u_hooks(); }
        hull() { lower_cross_tube(); translate([0,0,-53]) lower_cross_tube(); }
    }
} else if(VIEW=="passage_obstruction") {
    intersection() { guard_v1_8(); translate([0,0,4]) cylinder(d=15.999,h=70,center=true,$fn=64); }
} else if(VIEW=="upper_shape_changed") {
    symmetric_difference() { upper_only() guard_v1_5(); upper_only() guard_v1_8(); }
} else if(VIEW=="triangles_changed") {
    difference() { all_four_triangular_fills(); guard_v1_8(); }
} else if(VIEW=="front_profile_difference") {
    symmetric_difference() { lower_profile_at(15.5); lower_profile_at(27); }
} else if(VIEW=="back_profile_difference") {
    symmetric_difference() { lower_profile_at(-15.5); lower_profile_at(-27); }
} else if(VIEW=="legacy_hook_residual") {
    // Old inward tips above blue bottom must be completely absent now.
    intersection() {
        guard_v1_8();
        union() {
            translate([9.4,-34,-19.999]) cube([0.999,68,0.499]);
            translate([-10.399,-34,-19.999]) cube([0.999,68,0.499]);
        }
    }
} else if(VIEW=="new_segment_above_zero") {
    intersection() {
        guard_v1_8();
        union() {
            translate([-40,21.001,0.001]) cube([80,13,30]);
            translate([-40,-34.001,0.001]) cube([80,13,30]);
        }
    }
} else if(VIEW=="seated_tube_contact") {
    intersection() { guard_v1_8(); lower_cross_tube(); }
}
