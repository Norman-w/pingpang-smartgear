// v1.15: tapered-to-Y-edge outer ribs and unified (not per-feature) bevels.
// mm; X=upper tube, Y=lower foot, Z=up. One-piece X1C PETG FDM clip.
// Slide along -Z; keep original bore, fits, hooks and roof. No seal/new screw.
// Lower walls remain 7 mm (confirmed +2 mm outward per X side).
// Raw structural solids overlap; union FIRST, bevel only the unified body.
use <../perpendicular-u-joint-guard-v1.12-flush-roof/flush_roof_guard.scad>;
use <../perpendicular-u-joint-guard-v1.13-edge-safe-label/edge_safe_guard.scad>;

FEATURE="all";
EXTRA_X=2;
function arm_outer_half_x(extra=2)=15.9+extra;
function bottom_z()=-23.5;

module thick_arms(extra=2) {
    for(sx=[-1,1]) for(sy=[-1,1]) scale([sx,sy,1])
        translate([10.9,10.5,bottom_z()]) cube([5+extra,23,23.7]);
}
module wide_ramps(extra=2) {
    scale([arm_outer_half_x(extra)/15.9,1,1]) guard_v1_12(feature="ramps");
}
module root_bridges(extra=2) {
    // Fill the small triangular pocket between the old 5 mm upper wall
    // and the tapered rib above the new 7 mm lower arm. All bridge volume
    // lies outside mating envelopes, and overlaps both old and new solids.
    for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])
        translate([15.7,10.5,0])cube([arm_outer_half_x(extra)-15.7,11,23.2]);
}
module tapered_ribs(extra=2) {
    // Top rectangle is unchanged at the roof interface. At Z=-23.5,
    // the TWO bottom vertices form ONLY a Y-directed edge, no bottom face.
    // The inner slope embeds inside the 7 mm arm above that edge, providing
    // a volumetric union rather than a detached zero-thickness fin.
    x=arm_outer_half_x(extra);
    for(sx=[-1,1]) for(sy=[-1,1]) scale([sx,sy,1])
        polyhedron(points=[
            [14.9,10.5,23], [27.9,10.5,23],
            [27.9,21.5,23], [14.9,21.5,23],
            [x,10.5,-23.5], [x,33.5,-23.5]
        ], faces=[[3,2,1,0],[1,4,0],[2,5,4,1],[4,5,3,0],[5,2,3]],convexity=8);
}
module unified_blank(extra=2) {
    assert(extra>0 && extra<=6);
    union() {
        guard_v1_12();
        thick_arms(extra);
        wide_ramps(extra);
        root_bridges(extra);
        tapered_ribs(extra);
    }
}
module unified_body(extra=2) {
    union() {
        convex_edge_bevel(0.6) unified_blank(extra);
        // Original 1.5 mm lowest band stays exempt, including hook tips.
        // Rib geometry here is still tapered: no artificial flat bottom pad.
        intersection() { unified_blank(extra); bottom_protection(); }
    }
}
module guard_v1_15(extra=2,feature="all") {
    if(feature=="raw") unified_blank(extra);
    else if(feature=="body") unified_body(extra);
    else if(feature=="label") guard_v1_13(feature="label");
    else union() { unified_body(extra); guard_v1_13(feature="label"); }
}
guard_v1_15(EXTRA_X,FEATURE);
