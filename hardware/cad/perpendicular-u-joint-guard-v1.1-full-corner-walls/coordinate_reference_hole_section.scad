// v1.1 positive-X section of the printable body, exposing the Z through-hole.
use <candidate_full_corner_walls.scad>;
$fn=48; axis_z=[.10,.75,.25]; label_color=[.08,.10,.12];
module arrow_z(z0,z1,x,y,c){color(c){translate([x,y,z0])cylinder(d=1.2,h=z1-z0);translate([x,y,z1])cylinder(r1=3,r2=0,h=7);}}
module text_xz(value,x,y,z,size=5,c=label_color){color(c)translate([x,y,z])rotate([90,0,0])linear_extrude(height=.7)text(value,size=size,font="Arial:style=Bold",halign="left",valign="center");}
candidate_hole_section();
arrow_z(-28,40,38,38,axis_z);
text_xz("FINAL Z THROUGH-HOLE d=6.2",20,38,48,4.8,label_color);
text_xz("BOTTOM -> TOP / NUT POCKET REMAINS OPEN",-35,38,-29,4.0,label_color);
