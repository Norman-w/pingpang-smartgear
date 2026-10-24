// Real SCAD rendering of the verified, source-derived unified body.
// Rebuild with build_export.py after editing tapered_guard.scad.
use <tapered_guard.scad>;
use <../perpendicular-u-joint-guard-v1.13-edge-safe-label/component_colors.scad>;
VIEW="isolated"; // isolated | assembly | section | bottom_slice
EXTRA_X=2;
NATIVE=false; // Diagnostic only: native CGAL opening currently asserts.
module reviewed_body() {
    if(NATIVE)guard_v1_15(EXTRA_X,"body");
    else import("../exports/perpendicular-u-joint-v1.15-tapered-unified/guard-v1.15-body.stl",convexity=20);
}

module ramp_color_envelope() {
    minkowski(){wide_ramps(EXTRA_X);cube([0.002,0.002,0.002],center=true);}
}
module ramp_zone(outer) {
    for(s=[-1,1])scale([1,s,1])box_region(-outer,outer,21.501,60,0.201,22.999);
}
module mask(id) {
    outer=arm_outer_half_x(EXTRA_X)+0.001;
    if(id=="A")box_region(-60,60,-60,60,22.999,60);
    if(id=="B")box_region(-outer,outer,-21.501,21.501,0.201,22.999);
    if(id=="C")union(){
        for(s=[-1,1])scale([s,1,1])box_region(outer,60,-60,60,-60,22.999);
        difference(){ramp_zone(outer);ramp_color_envelope();}
    }
    if(id=="D")intersection(){ramp_zone(outer);ramp_color_envelope();}
    if(id=="E")box_region(-outer,outer,-60,60,-21.999,0.201);
    if(id=="F")box_region(-outer,outer,-60,60,-60,-21.999);
}
module clip_view(){
    if(VIEW=="section")box_region(-60,60,-17,-15,-60,60);
    else if(VIEW=="bottom_slice")box_region(-60,60,-60,60,-23.5,-23.4);
    else box_region(-60,60,-60,60,-60,60);
}
module part(id,c) {
    color(c)render(convexity=20)intersection(){reviewed_body();mask(id);clip_view();}
}
part("A",[1,.40,.07]);part("B",[.98,.76,.10]);
part("C",[.66,.24,.86]);part("D",[.23,.70,.25]);
part("E",[.02,.66,.73]);part("F",[.92,.12,.19]);
if(VIEW=="isolated" || VIEW=="assembly") {
    // Existing unchanged label export is derived from the same v1.13 module.
    color([.18,.18,.18])import("../exports/perpendicular-u-joint-v1.13-edge-safe-label/guard-v1.13-lettering.stl",convexity=16);
}
if(VIEW=="assembly")tubes();
axes();
