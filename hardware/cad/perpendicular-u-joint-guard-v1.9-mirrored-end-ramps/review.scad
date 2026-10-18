// Real v1.9 SCAD geometry, diagnostic cuts and exact mirror checks.
use <mirrored_end_ramps_guard.scad>;
use <../perpendicular-u-joint-guard-v1.8-lower-20plus1p5/lower_20plus1p5_guard.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;
$fn=48;
VIEW="assembly";

module original_length_zone() { translate([-60,-21,-40]) cube([120,42,100]); }
module added_ramp_material() { difference() { guard_v1_9(); guard_v1_8(); } }
module region_original_length() { intersection() { guard_v1_8(); original_length_zone(); } }
module region_v1_8_extension() { difference() { guard_v1_8(); original_length_zone(); } }
module colored_part() {
    color([0.96,0.39,0.08]) region_original_length();
    color([0.12,0.57,0.65]) region_v1_8_extension();
    color([0.76,0.16,0.49]) added_ramp_material();
}
module section_yz(x=0) {
    intersection() { children(); translate([x-0.025,-65,-28]) cube([0.05,130,65]); }
}
module section_xz(y=27) {
    intersection() { children(); translate([-65,y-0.025,-28]) cube([130,0.05,65]); }
}
module label_yz(value,y,z,size=3,c=[0.1,0.12,0.15]) {
    color(c) translate([14,y,z]) rotate([90,0,90]) linear_extrude(height=0.1)
        text(value,font="Arial Unicode MS",size=size,valign="center");
}
module label_xz(value,x,z,size=3,c=[0.1,0.12,0.15]) {
    color(c) translate([x,-2,z]) rotate([90,0,0]) linear_extrude(height=0.1)
        text(value,font="Arial Unicode MS",size=size,valign="center");
}
module line_yz(a,b,c=[0.16,0.2,0.23]) {
    color(c) hull() {
        translate([14,a[0],a[1]]) sphere(d=0.2,$fn=12);
        translate([14,b[0],b[1]]) sphere(d=0.2,$fn=12);
    }
}
module line_xz(a,b,c=[0.16,0.2,0.23]) {
    color(c) hull() {
        translate([a[0],-1,a[1]]) sphere(d=0.2,$fn=12);
        translate([b[0],-1,b[1]]) sphere(d=0.2,$fn=12);
    }
}
module coordinates() {
    for(a=[0,1,2]) {
        c=a==0?[0.48,0.51,0.55]:a==1?[0.16,0.43,0.82]:[0.12,0.65,0.24];
        r=a==0?[0,90,0]:a==1?[-90,0,0]:[0,0,0];
        color(c) translate([-64,-61,-27]) rotate(r) {
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
    colored_part(); coordinates();
}
module yz_end(sign=1) {
    // Crop to this end only. Negative Y is not transformed in the scene;
    // its visible right-to-left 10 -> 3 mm profile is the true Y=0 mirror.
    y0=sign>0?16:-37;
    module detail() {
        intersection() { children(); translate([-30,y0,-23]) cube([60,21,55]); }
    }
    color([0.96,0.39,0.08]) section_yz() detail() region_original_length();
    color([0.12,0.57,0.65]) section_yz() detail() region_v1_8_extension();
    color([0.76,0.16,0.49]) section_yz() detail() added_ramp_material();
    color([0.28,0.45,0.78]) section_yz() detail() lower_cross_tube();
    left=sign>0?10:-41;
    label_yz(sign>0?"+Y 端实心斜坡 / X=0 YZ剖面":"-Y 端实心斜坡 / X=0 YZ剖面",left,39,3.4);
    label_yz(sign>0?"内端10 → 外端3 mm（沿+Y向外）":"外端3 → 内端10 mm（沿+Y靠近主体）",left,33,2.8);
    root=sign*21; tip=sign*33;
    a=sign>0?19:-19; b=sign>0?35:-35;
    line_yz([a,0],[a,10]);
    line_yz([a-0.5,0],[a+0.5,0]); line_yz([a-0.5,10],[a+0.5,10]);
    label_yz("10",a-2.8,14,2.9);
    line_yz([b,0],[b,3]);
    line_yz([b-0.5,0],[b+0.5,0]); line_yz([b-0.5,3],[b+0.5,3]);
    label_yz("3",b-0.8,7,2.9);
    line_yz([min(root,tip),-26],[max(root,tip),-26]);
    line_yz([root,-27],[root,-25]); line_yz([tip,-27],[tip,-25]);
    label_yz("12 mm",(root+tip)/2-4,-30,2.9);
    label_yz(sign>0?"Y=+21 主体端":"Y=-21 主体端",root-4,-35,2.7);
    label_yz(sign>0?"Y=+33 外端":"Y=-33 外端",tip-4,-40,2.7);
    label_yz("蓝管上沿 Z=0，蓝管 Z=-20..0",left,-46,2.8,[0.18,0.3,0.6]);
}
module ramp_xz() {
    color([0.96,0.39,0.08]) section_xz() region_original_length();
    color([0.12,0.57,0.65]) section_xz() region_v1_8_extension();
    color([0.76,0.16,0.49]) section_xz() added_ramp_material();
    color([0.28,0.45,0.78]) section_xz() lower_cross_tube();
    label_xz("v1.9 外伸端 Y=27 的 XZ截面",-43,21,3.6);
    label_xz("紫色斜坡：X=-11.4..+11.4，宽22.8 mm",-43,15,2.9);
    label_xz("此处高度6.5 mm（根部10、外端3）",-43,10,2.8);
    line_xz([-11.4,9],[11.4,9]);
    line_xz([-11.4,8.2],[-11.4,9.8]); line_xz([11.4,8.2],[11.4,9.8]);
    label_xz("蓝管Z=-20..0",23,-8,2.8,[0.18,0.3,0.6]);
    label_xz("两侧各搭入原墙1 mm",23,-14,2.8);
    label_xz("下部外宽30.8 mm未改变",-43,-30,2.9);
    label_xz("内扣仍为Z=-21.5..-20，厚1.5 mm",-43,-36,2.8);
    label_xz("青色：v1.8延长墙；紫色：v1.9新增实心斜坡",-43,-43,2.7);
}
module central_comparison() {
    module show(candidate=true) {
        color([0.96,0.39,0.08]) section_xz(0) {
            if(candidate) guard_v1_9(); else guard_v1_8();
        }
        color([0.58,0.61,0.66]) section_xz(0) upper_long_tube();
        color([0.28,0.45,0.78]) section_xz(0) lower_cross_tube();
        color([0.82,0.82,0.84]) section_xz(0) vertical_joint_screw();
    }
    translate([-83,0,0]) { show(false); label_xz("基线 v1.8 中心Y=0",-38,43,3.7); }
    translate([83,0,0]) { show(true); label_xz("v1.9 中心Y=0",-38,43,3.7); }
    label_xz("中央孔/灰管通道同形：Ø16全深孔与Y±10通道不被新增斜坡占用",-110,-40,3.2);
}
module symmetric_difference() {
    difference() { children(0); children(1); }
    difference() { children(1); children(0); }
}
module centre_zone() { translate([-60,-9.999,-30]) cube([120,19.998,65]); }

if(VIEW=="assembly") assembly();
else if(VIEW=="yz_plus") yz_end(1);
else if(VIEW=="yz_minus") yz_end(-1);
else if(VIEW=="xz") ramp_xz();
else if(VIEW=="central_comparison") central_comparison();
else if(VIEW=="clip") guard_v1_9();
else if(VIEW=="passage_obstruction") {
    intersection() { guard_v1_9(); translate([0,0,4]) cylinder(d=15.999,h=70,center=true,$fn=64); }
} else if(VIEW=="upper_motion_obstruction") {
    intersection() { guard_v1_9(); hull() { upper_long_tube(); translate([0,0,-53]) upper_long_tube(); } }
} else if(VIEW=="nut_motion_obstruction") {
    intersection() { guard_v1_9(); hull() { vertical_joint_screw(); translate([0,0,-53]) vertical_joint_screw(); } }
} else if(VIEW=="rigid_lower_motion_obstruction") {
    intersection() {
        difference() { guard_v1_9(); lower_u_hooks(); }
        hull() { lower_cross_tube(); translate([0,0,-53]) lower_cross_tube(); }
    }
} else if(VIEW=="original_removed") {
    difference() { guard_v1_8(); guard_v1_9(); }
} else if(VIEW=="lower_changed") {
    intersection() {
        symmetric_difference() { guard_v1_8(); guard_v1_9(); }
        translate([-60,-60,-30]) cube([120,120,29.999]);
    }
} else if(VIEW=="central_channel_changed") {
    intersection() {
        symmetric_difference() { guard_v1_8(); guard_v1_9(); }
        centre_zone();
    }
} else if(VIEW=="mirror_difference") {
    symmetric_difference() { guard_v1_9(); mirror([0,1,0]) guard_v1_9(); }
} else if(VIEW=="ramp_root_sample" || VIEW=="ramp_middle_sample" || VIEW=="ramp_tip_sample") {
    y0=VIEW=="ramp_root_sample"?21:VIEW=="ramp_middle_sample"?27:32.999;
    intersection() { ramp_prisms_pair(); translate([-20,y0,0]) cube([40,0.001,20]); }
}
