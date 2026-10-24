// v1.13 structural color review ONLY: original dimensions/geometry unchanged.
// X = upper long tube; Y = lower foot; Z = up. Units: mm.
// Colors identify contiguous regions of ONE printed part, not separate parts.
// A orange: roof/eaves; B yellow: upper solid walls; C purple: eave gussets;
// D green: fore/aft ramps; E cyan: lower clip arms; F red: bottom 1.5 mm band.
// Region boundaries are visual references, not manufacturing joints.
use <edge_safe_guard.scad>;

VIEW = "isolated"; // isolated | assembly
// Offset COLOR boundaries 0.001 mm from existing faces to avoid zero-volume
// coincident surfaces in preview. The partition still covers the same body:
// no gap, no overlap in volume, no change to the physical geometry.
roof_split=22.999;
wall_x_split=15.901;
wall_y_split=21.501;
lip_split=-21.999;

module box_region(x0,x1,y0,y1,z0,z1) {
    translate([x0,y0,z0]) cube([x1-x0,y1-y0,z1-z0]);
}
module region(id) {
    if (id=="A") box_region(-60,60,-60,60,roof_split,60);
    if (id=="B") box_region(-wall_x_split,wall_x_split,-wall_y_split,wall_y_split,0,roof_split);
    if (id=="C") for(s=[-1,1]) scale([s,1,1])
        box_region(wall_x_split,60,-wall_y_split,wall_y_split,0,roof_split);
    if (id=="D") for(s=[-1,1]) scale([1,s,1])
        box_region(-60,60,wall_y_split,60,0,roof_split);
    if (id=="E") box_region(-60,60,-60,60,lip_split,0);
    if (id=="F") box_region(-60,60,-60,60,-60,lip_split);
}
module colored_region(id,c) {
    color(c) render(convexity=20) intersection() {
        guard_v1_13(feature="body");
        region(id);
    }
}
module colored_guard() {
    colored_region("A",[1.00,0.40,0.07]);
    colored_region("B",[0.98,0.76,0.10]);
    colored_region("C",[0.66,0.24,0.86]);
    colored_region("D",[0.23,0.70,0.25]);
    colored_region("E",[0.02,0.66,0.73]);
    colored_region("F",[0.92,0.12,0.19]);
    color([0.18,0.18,0.18]) render(convexity=16)
        guard_v1_13(feature="label");
}
module tubes() {
    color([0.55,0.59,0.64]) translate([-48,-10,0]) cube([96,20,20]);
    color([0.13,0.32,0.70]) translate([-10,-44,-20]) cube([20,88,20]);
}
// Explicit positive XYZ triad beside the part; no model geometry is changed.
module arrow_axis(c,rot,label) {
    color(c) rotate(rot) {
        cylinder(h=15,r=0.40,$fn=16);
        translate([0,0,15]) cylinder(h=3,r1=1.3,r2=0,$fn=20);
    }
}
module axes() {
    translate([-43,-42,-23.5]) {
        arrow_axis([0.85,0.12,0.12],[0,90,0],"X");
        arrow_axis([0.12,0.60,0.12],[-90,0,0],"Y");
        arrow_axis([0.10,0.30,0.90],[0,0,0],"Z");
        color([0.85,0.12,0.12]) translate([20,0,0]) linear_extrude(.2) text("+X",size=3);
        color([0.12,0.60,0.12]) translate([0,20,0]) linear_extrude(.2) text("+Y",size=3);
        color([0.10,0.30,0.90]) translate([0,0,20]) rotate([90,0,0]) linear_extrude(.2) text("+Z",size=3);
    }
}
colored_guard();
if (VIEW=="assembly") tubes();
axes();
