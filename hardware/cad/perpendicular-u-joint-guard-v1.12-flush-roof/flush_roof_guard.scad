// v1.12, mm. X=upper gray tube; Y=blue foot; Z=up.
// Only remove the two 5 x ny x 1 mm ribs below the roof over the gray tube.
// Keep v1.11 as an immutable dependency; no rescaling or other geometry edits.
use <../perpendicular-u-joint-guard-v1.11-fit-21xy-22z/fit_clearance_guard.scad>;

module guard_v1_12(nx=21,ny=21,nz=22,feature="all") {
    roof_bottom=nz+1; // Same accepted 8 mm roof: Z=23..31 at defaults.
    difference() {
        guard_v1_11(nx,ny,nz,feature);
        // The old entry stopped at nz, leaving the arms' last 1 mm intact.
        // Cut to the actual roof underside, not into the roof or XZ webs.
        translate([-60,-ny/2,-60]) cube([120,ny,60+roof_bottom]);
    }
}

guard_v1_12();
