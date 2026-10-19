use <edge_safe_guard.scad>;
use <../perpendicular-u-joint-guard-v1.12-flush-roof/flush_roof_guard.scad>;
VIEW="assembly";

module tube_context() {
    color([0.55,0.59,0.64]) translate([-48,-10,0]) cube([96,20,20]);
    color([0.13,0.32,0.7]) translate([-10,-44,-20]) cube([20,88,20]);
}
module preview_guard() {
    color([0.95,0.47,0.1]) render(convexity=16) guard_v1_13(feature="body");
    // Contrast is for legibility in the render only; same-material mesh.
    color([0.94,0.77,0.4]) render(convexity=16) guard_v1_13(feature="label");
}
module bottom_band() { translate([0,0,-22.75]) cube([120,120,1.5],center=true); }
module positive_body_change() {
    difference() { guard_v1_13(feature="body"); guard_v1_12(); }
}
module bottom_difference() {
    intersection() {
        bottom_band();
        union() {
            difference() { guard_v1_13(feature="body"); guard_v1_12(); }
            difference() { guard_v1_12(); guard_v1_13(feature="body"); }
        }
    }
}
if(VIEW=="body") guard_v1_13(feature="body");
else if(VIEW=="clip") guard_v1_13();
else if(VIEW=="body_added") positive_body_change();
else if(VIEW=="bottom_difference") bottom_difference();
else if(VIEW=="bore_obstruction") intersection() {
    guard_v1_13(feature="body"); cylinder(d=15.99,h=150,center=true,$fn=64);
}
else if(VIEW=="old_rib_residue") intersection() {
    guard_v1_13(feature="body"); translate([-50,-10.499,22.001]) cube([100,20.998,0.998]);
}
else if(VIEW=="roof_detail") {
    intersection() { preview_guard(); translate([-35,-30,21]) cube([70,60,15]); }
}
else if(VIEW=="isolated") preview_guard();
else { tube_context(); preview_guard(); }
