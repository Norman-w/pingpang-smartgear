// Native CAD invariant probes. CHECK="all" must render EMPTY.
// Does not imply exported binary STL topology passed validation.
use <reinforced_guard.scad>;
use <../perpendicular-u-joint-guard-v1.13-edge-safe-label/edge_safe_guard.scad>;
CHECK="all";
module old_body() { guard_v1_13(feature="body"); }
module new_body() { guard_v1_14(feature="body"); }
module delta() { union(){ difference(){new_body();old_body();} difference(){old_body();new_body();} } }
module probe(test) {
if(test=="roof") intersection() {
    delta(); translate([-60,-60,23.001]) cube([120,120,40]);
}
if(test=="removed") difference(){old_body();new_body();}
if(test=="bore") intersection(){new_body();cylinder(d=15.99,h=150,center=true,$fn=64);}
if(test=="entry") intersection(){
    new_body();translate([-60,-10.499,-60])cube([120,20.998,82.999]);
}
if(test=="foot") intersection(){
    new_body();translate([-10.899,-60,-21.999])cube([21.798,120,21.998]);
}
if(test=="hooks") intersection(){
    delta();translate([-10.9,-60,-23.6])cube([21.8,120,1.601]);
}
if(test=="bottom_coverage") difference(){
    for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])
        translate([17.901,10.501,-23.499])cube([9.998,22.998,0.098]);
    new_body();
}
}
if(CHECK=="all") for(test=["roof","removed","bore","entry","foot","hooks","bottom_coverage"]) probe(test);
else probe(CHECK);
