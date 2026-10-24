// v1.14 preview candidate, mm. X=upper long tube, Y=lower foot, Z=up.
// One-piece PETG FDM clip, installed along -Z, removed before folding foot.
// No split joint/seal/new fastener. Preserve Ø16 Z passage and fit spaces.
// User confirmed +2 mm OUTWARD per X side: lower arm wall 5 -> 7 mm.
// Load-path intent: roof -> extended outer ribs -> full-length lower arms.
// This is a geometry candidate, NOT proof of impact resistance or snap force.
use <../perpendicular-u-joint-guard-v1.12-flush-roof/flush_roof_guard.scad>;
use <../perpendicular-u-joint-guard-v1.13-edge-safe-label/edge_safe_guard.scad>;

EXTRA_X=2;
RIB_STYLE="vertical"; // User confirmed: outside X edge drops vertically.
FEATURE="all";

function inner_x()=21.8;
function old_outer_half_x()=15.9;
function arm_outer_half_x(extra=2)=old_outer_half_x()+extra;
function roof_half_x()=27.9;
function inner_y()=10.5;
function root_y()=21.5;
function tip_y()=33.5;
function bottom_z()=-23.5;

module thick_arms(extra=2) {
    for(sx=[-1,1]) for(sy=[-1,1]) scale([sx,sy,1])
        translate([inner_x()/2,inner_y(),bottom_z()])
            cube([5+extra,tip_y()-inner_y(),-bottom_z()+0.2]);
}
module wide_ramps(extra=2) {
    // Scale ONLY the X span of the original independent ramp feature.
    scale([arm_outer_half_x(extra)/old_outer_half_x(),1,1])
        guard_v1_12(feature="ramps");
}
module extended_ribs(extra=2,style="vertical") {
    assert(style=="vertical");
    for(sx=[-1,1]) for(sy=[-1,1]) scale([sx,sy,1]) hull() {
        // Match the original triangle BELOW the roof; the original body
        // supplies its embedded upper 0.5 mm. Stop this hull at Z=23 so
        // widening Y at the bottom cannot add material above the roof base.
        translate([0,root_y(),0]) rotate([90,0,0])
            linear_extrude(height=root_y()-inner_y())
                polygon([[27.9,23],[14.9,23],[14.9,0]]);
        // Full 23 mm Y footprint at Z minimum. Explicit volumetric overlap
        // with arm; it is not merely a touching cosmetic outer surface.
        translate([old_outer_half_x()-1,inner_y(),bottom_z()])
            cube([roof_half_x()-(old_outer_half_x()-1),
                  tip_y()-inner_y(),0.1]);
    }
}
module reinforced_blank(extra=2,style="vertical") {
    assert(extra>0 && extra<=6);
    union() {
        guard_v1_12();
        thick_arms(extra);
        wide_ramps(extra);
        extended_ribs(extra,style);
    }
}
module reinforced_body(extra=2,style="vertical") {
    union() {
        // Keep the approved body/roof intact. Bevel additions separately
        // before joining: no second morphological pass over old chamfers.
        guard_v1_13(feature="body");
        convex_edge_bevel(0.6) thick_arms(extra);
        convex_edge_bevel(0.6) wide_ramps(extra);
        convex_edge_bevel(0.6) extended_ribs(extra,style);
        // Preserve the accepted bottom 1.5 mm band / hook geometry.
        intersection() { reinforced_blank(extra,style); bottom_protection(); }
    }
}
module guard_v1_14(extra=2,style="vertical",feature="all") {
    if(feature=="body") reinforced_body(extra,style);
    else if(feature=="label") guard_v1_13(feature="label");
    else union() { reinforced_body(extra,style); guard_v1_13(feature="label"); }
}
guard_v1_14(EXTRA_X,RIB_STYLE,FEATURE);
