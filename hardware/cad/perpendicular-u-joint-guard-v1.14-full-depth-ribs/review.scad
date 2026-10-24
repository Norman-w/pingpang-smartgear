// Actual source rendering. Colors are feature labels, not separate pieces.
use <reinforced_guard.scad>;
use <../perpendicular-u-joint-guard-v1.13-edge-safe-label/component_colors.scad>;
VIEW="isolated";
RIB_STYLE="vertical";
EXTRA_X=2;
module ramp_color_envelope() {
    // A 0.001 mm COLOR-only expansion avoids coincident classification faces.
    minkowski() { wide_ramps(EXTRA_X); cube([0.002,0.002,0.002],center=true); }
}
module ramp_side_region(outer) {
    for(s=[-1,1]) scale([1,s,1])
        box_region(-outer,outer,21.501,60,0.201,22.999);
}

module mask(id) {
    outer=arm_outer_half_x(EXTRA_X)+0.001;
    if(id=="A") box_region(-60,60,-60,60,22.999,60);
    if(id=="C") union() {
        for(s=[-1,1]) scale([s,1,1])
            box_region(outer,60,-60,60,-60,22.999);
        difference() { ramp_side_region(outer); ramp_color_envelope(); }
    }
    if(id=="B") box_region(-outer,outer,-21.501,21.501,0.201,22.999);
    if(id=="D") intersection() { ramp_side_region(outer); ramp_color_envelope(); }
    if(id=="E") box_region(-outer,outer,-60,60,-21.999,0.201);
    if(id=="F") box_region(-outer,outer,-60,60,-60,-21.999);
}
module part(id,c) {
    color(c) render(convexity=20) intersection() {
        guard_v1_14(EXTRA_X,RIB_STYLE,"body"); mask(id);
    }
}
part("A",[1,0.40,0.07]);
part("B",[0.98,0.76,0.10]);
part("C",[0.66,0.24,0.86]);
part("D",[0.23,0.70,0.25]);
part("E",[0.02,0.66,0.73]);
part("F",[0.92,0.12,0.19]);
// Use the unchanged, staged lettering mesh so body can be reviewed with
// CGAL without sending the curved font through CGAL's morphology bug.
color([0.18,0.18,0.18]) import("../exports/perpendicular-u-joint-v1.14-full-depth-ribs/guard-v1.14-lettering.stl",convexity=16);
if(VIEW=="assembly") tubes();
axes();
