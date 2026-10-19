// 乒乓球围挡支撑脚止转卡 v1.13：限制中心螺丝松动时支撑脚意外旋转。
// 适用接头：两根名义20x20方管上下贴合，工作时相互垂直，中心螺丝沿Z贯穿。
// 从上方沿-Z套入；前后两个一体U卡臂包住下方脚，底部内扣保持扣合。
// 收纳前先取下卡子，再将支撑脚转至与长管平行；不可带卡强行折转。
// 本件是可拆卸止转附件，不替代原螺丝紧固；实物扣合与地面间隙需验证。
// Units mm. X=gray upper tube, Y=blue foot, Z=up. One-piece PETG guard.
// Native solid construction: no imported mesh replaces the SCAD source.
use <../perpendicular-u-joint-guard-v1.12-flush-roof/flush_roof_guard.scad>;

module bevel_kernel(r) {
    // Octahedral structuring element: planar 45-degree relief on box edges.
    polyhedron(points=[[r,0,0],[-r,0,0],[0,r,0],[0,-r,0],[0,0,r],[0,0,-r]],
        faces=[[0,2,4],[2,1,4],[1,3,4],[3,0,4],
               [2,0,5],[1,2,5],[3,1,5],[0,3,5]],convexity=4);
}
module work_envelope() { translate([0,0,5]) cube([120,120,120],center=true); }
module convex_edge_bevel(r=0.6) {
    // Morphological opening: erode then dilate with the SAME symmetric
    // kernel. All positive edges/corners are treated, not concave corners.
    // Final intersection guarantees subtraction only, never reduced fits.
    intersection() {
        children();
        minkowski() {
            difference() {
                work_envelope();
                minkowski() {
                    difference() { work_envelope(); children(); }
                    bevel_kernel(r);
                }
            }
            bevel_kernel(r);
        }
    }
}
module bottom_protection(nz=22) {
    // Exact 1.5 mm bottom band, Z=-23.5..-22 with the accepted defaults.
    translate([0,0,-nz-0.75]) cube([120,120,1.5],center=true);
}
module labeled_text_blank(nz=22) {
    // Small bold lettering beside the bore, along X. 0.1 mm embeds into
    // the roof; nominal exposed height is 0.6 mm, with 0.1 mm edge bevel.
    translate([0,-15.5,nz+8.9]) linear_extrude(height=0.7,convexity=10)
        text("Norman@PingCloud",size=3,font="Arial:style=Bold",
             halign="center",valign="center",spacing=1,$fn=24);
}
module beveled_body(nx=21,ny=21,nz=22,chamfer=0.6) {
    union() {
        convex_edge_bevel(chamfer) guard_v1_12(nx,ny,nz);
        intersection() { guard_v1_12(nx,ny,nz); bottom_protection(nz); }
    }
}
module guard_v1_13(nx=21,ny=21,nz=22,chamfer=0.6,label=true,feature="all") {
    assert(chamfer>0 && chamfer<=0.8);
    if(feature=="body") beveled_body(nx,ny,nz,chamfer);
    else if(feature=="label") convex_edge_bevel(0.1) labeled_text_blank(nz);
    else union() {
        beveled_body(nx,ny,nz,chamfer);
        if(label) convex_edge_bevel(0.1) labeled_text_blank(nz);
    }
}

FEATURE="all";
guard_v1_13(feature=FEATURE);
