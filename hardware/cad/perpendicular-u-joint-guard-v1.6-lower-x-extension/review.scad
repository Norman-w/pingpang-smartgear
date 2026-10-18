// v1.6 X-extension: real model sections and dimensions. No raster invention.
use <lower_x_extension_guard.scad>;
use <../perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad>;
use <../perpendicular-u-joint-guard-v1.3-triangular-corner-fills/candidate_triangular_corner_fills.scad>;
use <../perpendicular-u-joint-guard-v0.7/perpendicular_double_u_guard.scad>;
$fn=48;
VIEW="assembly";

module added() { difference() { guard_v1_6_x(); guard_v1_5(); } }
module colored_part() {
    color([0.96,0.39,0.08]) guard_v1_5();
    color([0.16,0.65,0.33]) added();
}
module assembly() {
    upper_long_tube(); lower_cross_tube(); colored_part(); vertical_joint_screw();
}
module xz_slice(y=15.5) {
    intersection() {
        children();
        translate([-65,y-0.025,-28]) cube([130,0.05,65]);
    }
}
module label_xz(value,x,z,size=3,c=[0.1,0.12,0.15]) {
    color(c) translate([x,-2,z]) rotate([90,0,0])
        linear_extrude(height=0.1)
            text(value,font="Arial Unicode MS",size=size,valign="center");
}
module line_xz(a,b,c=[0.16,0.2,0.23]) {
    color(c) hull() {
        translate([a[0],-1,a[1]]) sphere(d=0.22,$fn=12);
        translate([b[0],-1,b[1]]) sphere(d=0.22,$fn=12);
    }
}
module dim_x(a,b,z,caption) {
    line_xz([a,z],[b,z]);
    line_xz([a,z-1],[a,z+1]); line_xz([b,z-1],[b,z+1]);
    label_xz(caption,(a+b)/2-4.5,z-3,2.6);
}
module xz_dimensions(candidate=true,title=true) {
    color([0.96,0.39,0.08]) xz_slice() guard_v1_5();
    if(candidate) color([0.16,0.65,0.33]) xz_slice() added();
    color([0.28,0.45,0.78]) xz_slice() lower_cross_tube();
    if(title) {
        label_xz("v1.6 X 向下部延伸 / Y=15.5 剖面",-44,44,3.6);
        label_xz("绿色为新增打印材料；管子、原卡扣不移动",-44,37,2.9);
    }
    if(candidate) {
        dim_x(-27.4,-15.4,-28,"12 mm");
        dim_x(15.4,27.4,-28,"12 mm");
        line_xz([33,-21],[33,0.5]);
        line_xz([32,-21],[34,-21]); line_xz([32,0.5],[34,0.5]);
        label_xz("21.5 mm",37,-10,3);
        label_xz("Z=+0.5",37,0.5,2.8);
        label_xz("Z=-21",37,-21,2.8);
    }
    label_xz("-X",-27,-38,2.8); label_xz("+X",20,-38,2.8);
}
module comparison() {
    translate([-68,0,0]) {
        xz_dimensions(false,false);
        label_xz("基线 v1.5",-24,39,4);
        dim_x(-15.4,15.4,-28,"下部外宽 30.8");
    }
    translate([68,0,0]) {
        xz_dimensions(true,false);
        label_xz("候选 v1.6：X±12",-28,39,4);
    }
}
module yz_end_slice() {
    // New end material at x=20: both bands visible, center 20 mm is open.
    color([0.16,0.65,0.33]) intersection() {
        added(); translate([19.975,-40,-25]) cube([0.05,80,60]);
    }
    color([0.96,0.39,0.08]) intersection() {
        guard_v1_5(); translate([19.975,-40,-25]) cube([0.05,80,60]);
    }
    module label(value,y,z,size=3) {
        color([0.1,0.12,0.15]) translate([22,y,z]) rotate([90,0,90])
            linear_extrude(height=0.1)
                text(value,font="Arial Unicode MS",size=size,valign="center");
    }
    label("X=20 端部剖面：Y 尺寸保持原值",-32,39,3.4);
    label("Y=-21..-10",-33,-30,2.6);
    label("Y=+10..+21",5,-30,2.6);
    label("中央 -10..+10 保持 20 mm；灰管通路敞开",-32,-37,2.6);
    label("延伸块 Z=-21..+0.5，共 21.5 mm",-32,33,2.9);
}
module top_lower_slice() {
    color([0.96,0.39,0.08]) intersection() {
        guard_v1_5(); translate([-40,-40,-10.1]) cube([80,80,0.2]);
    }
    color([0.16,0.65,0.33]) intersection() {
        added(); translate([-40,-40,-10.1]) cube([80,80,0.2]);
    }
    color([0.28,0.45,0.78]) intersection() {
        lower_cross_tube(); translate([-40,-55,-10.1]) cube([80,110,0.2]);
    }
    for(entry=[
        ["v1.6 下部俯视：X 左右各 +12 mm；Y 不变",-48,40,3.2],
        ["X=-27.4",-44,26,2.8],["X=+27.4",15,26,2.8],
        ["Y 外宽 42 mm / 中央通道 20 mm",-38,-37,3.0]
    ]) color([0.1,0.12,0.15]) translate([entry[1],entry[2],-8])
        linear_extrude(height=0.1)
            text(entry[0],font="Arial Unicode MS",size=entry[3],valign="center");
}
module allowed_hooks() {
    for(yc=[-15.5,15.5]) for(xc=[-11.15,11.15])
        translate([xc,yc,-20.25]) cube([3.5,11,1.5],center=true);
}

if(VIEW=="assembly") assembly();
else if(VIEW=="xz") xz_dimensions();
else if(VIEW=="comparison") comparison();
else if(VIEW=="end") yz_end_slice();
else if(VIEW=="top") top_lower_slice();
else if(VIEW=="clip") guard_v1_6_x();
else if(VIEW=="passage_obstruction") {
    intersection() {
        guard_v1_6_x();
        translate([0,0,4]) cylinder(d=15.999,h=70,center=true,$fn=64);
    }
} else if(VIEW=="upper_motion_obstruction") {
    intersection() {
        guard_v1_6_x();
        hull() { upper_long_tube(); translate([0,0,-52]) upper_long_tube(); }
    }
} else if(VIEW=="nut_motion_obstruction") {
    intersection() {
        guard_v1_6_x();
        hull() { vertical_joint_screw(); translate([0,0,-52]) vertical_joint_screw(); }
    }
} else if(VIEW=="rigid_lower_motion_obstruction") {
    intersection() {
        difference() { guard_v1_6_x(); allowed_hooks(); }
        hull() { lower_cross_tube(); translate([0,0,-52]) lower_cross_tube(); }
    }
} else if(VIEW=="original_material_removed") {
    difference() { guard_v1_5(); guard_v1_6_x(); }
} else if(VIEW=="triangles_changed") {
    difference() { all_four_triangular_fills(); guard_v1_6_x(); }
} else if(VIEW=="hooks_changed") {
    intersection() {
        union() {
            difference() { guard_v1_5(); guard_v1_6_x(); }
            difference() { guard_v1_6_x(); guard_v1_5(); }
        }
        allowed_hooks();
    }
} else if(VIEW=="x_mirror_difference") {
    union() {
        difference() { guard_v1_6_x(); mirror([1,0,0]) guard_v1_6_x(); }
        difference() { mirror([1,0,0]) guard_v1_6_x(); guard_v1_6_x(); }
    }
}
