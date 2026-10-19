// Real source geometry; diagnostic views/Boolean checks, not a print plate.
use <flush_roof_guard.scad>;
use <../perpendicular-u-joint-guard-v1.11-fit-21xy-22z/fit_clearance_guard.scad>;
VIEW="section";

module half_space() { translate([-65,0,-35]) cube([130,65,85]); }
module nominal_tubes(section=false) {
    // Physical tubes remain 20 x 20 in the established, unshifted frame.
    color([0.55,0.59,0.64]) render(convexity=12) intersection() {
        translate([-48,-10,0]) cube([96,20,20]);
        if(section) half_space();
    }
    // Keep the blue foot complete so both ends remain visible.
    color([0.13,0.32,0.7]) translate([-10,-44,-20]) cube([20,88,20]);
}
module colored_clip(section=false) {
    color([0.95,0.47,0.1]) render(convexity=12) intersection() {
        guard_v1_12();
        if(section) half_space();
    }
}
module expected_ribs(inset=0) {
    for(s=[-1,1])
        translate([s*13.4,0,22.5])
            cube([5-2*inset,21-2*inset,1-2*inset],center=true);
}
module removed() { difference() { guard_v1_11(); guard_v1_12(); } }

if(VIEW=="clip") guard_v1_12();
else if(VIEW=="added") difference() { guard_v1_12(); guard_v1_11(); }
else if(VIEW=="removed") removed();
else if(VIEW=="removed_outside_expected") difference() { removed(); expected_ribs(); }
else if(VIEW=="expected_missing") difference() { expected_ribs(0.001); removed(); }
else if(VIEW=="rib_residue") intersection() { guard_v1_12(); expected_ribs(0.001); }
else if(VIEW=="mirror_difference") {
    difference() { guard_v1_12(); mirror([0,1,0]) guard_v1_12(); }
    difference() { mirror([0,1,0]) guard_v1_12(); guard_v1_12(); }
}
else if(VIEW=="roof_obstruction") intersection() {
    guard_v1_12(); translate([-55,-10.499,22.001]) cube([110,20.998,0.998]);
}
else if(VIEW=="section") { colored_clip(true); nominal_tubes(true); }
else { colored_clip(); nominal_tubes(); }
