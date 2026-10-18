// v1.11, mm. X=upper gray tube axis; Y=blue foot axis; Z=up.
// Resize mating envelopes, NOT a global scale: walls, eaves, bore and ramp
// heights keep their accepted sizes. Actual context tubes remain 20x20.
$fn=48;

module guard_v1_11(nx=21,ny=21,nz=22,feature="all") {
    wall=5;
    inner_x=nx+0.8; // Preserve the pre-existing PETG printing relief.
    outer_x=inner_x+2*wall;
    wall_x=inner_x/2+wall/2;
    inner_y=ny/2;
    root_y=inner_y+11;
    tip_y=root_y+12;
    roof_bottom=nz+1;
    roof_top=roof_bottom+8;
    roof_half_x=outer_x/2+12;
    bottom_z=-nz-1.5;
    // Keep the real 20 mm foot's 0.6 mm engagement rather than moving the
    // lip tip outward with nx (which would leave only 0.1 mm engagement).
    lip_tip_x=20/2-0.6;
    lip_depth=wall_x-lip_tip_x;

    assert(nx>=20 && ny>=20 && nz>=20);
    assert(lip_depth>0 && lip_depth<wall+inner_x/2);

    module upper_body() {
        for(s=[-1,1]) {
            // Solid XZ upper U web, down from the roof to blue top Z=0.
            translate([0,s*(inner_y+root_y)/2,roof_top/2])
                cube([outer_x,11,roof_top],center=true);
            translate([s*wall_x,0,roof_top/2])
                cube([wall,2*root_y,roof_top],center=true);
        }
        translate([0,0,roof_bottom+4])
            cube([2*roof_half_x,2*root_y,8],center=true);
        for(sx=[-1,1]) for(sy=[-1,1])
            translate([0,sy*(inner_y+root_y)/2,0])
                rotate([90,0,0]) linear_extrude(height=11,center=true)
                    polygon([
                        [sx*roof_half_x,roof_bottom],
                        [sx*(outer_x/2-1),roof_bottom+0.5],
                        [sx*(outer_x/2-1),0]
                    ]);
    }
    module hooks() {
        for(sx=[-1,1]) for(sy=[-1,1])
            translate([sx*(lip_tip_x+lip_depth/2),
                       sy*(inner_y+tip_y)/2,-nz-0.75])
                cube([lip_depth,tip_y-inner_y,1.5],center=true);
    }
    module lower_body() {
        for(sx=[-1,1]) for(sy=[-1,1])
            translate([sx*wall_x,sy*(inner_y+tip_y)/2,bottom_z/2])
                cube([wall,tip_y-inner_y,-bottom_z],center=true);
        hooks();
    }
    module positive_ramp() {
        rotate([90,0,90]) linear_extrude(height=outer_x,center=true)
            polygon([[root_y-0.2,0],[tip_y,0],[tip_y,3],
                     [root_y,10],[root_y-0.2,10]]);
    }
    module end_ramps() {
        positive_ramp(); mirror([0,1,0]) positive_ramp();
        for(sx=[-1,1]) for(sy=[-1,1])
            translate([sx*wall_x,sy*(root_y+tip_y)/2,0])
                cube([wall,12,0.4],center=true);
    }

    difference() {
        union() {
            if(feature=="all" || feature=="upper") upper_body();
            if(feature=="all" || feature=="lower") lower_body();
            if(feature=="all" || feature=="ramps") end_ramps();
            if(feature=="hooks") hooks();
        }
        // True, unstepped round nut passage through the ENTIRE final part.
        cylinder(d=16,h=160,center=true,$fn=64);
        // Bottom-open gray-tube entry, ny wide and nz high. This removes
        // upper rigid interference without deleting either XZ solid web.
        translate([-60,-ny/2,-60]) cube([120,ny,60+nz]);
    }
}

guard_v1_11();
