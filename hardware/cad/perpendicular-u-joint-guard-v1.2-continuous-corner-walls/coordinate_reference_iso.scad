// v1.2 continuous X-end walls actual OpenSCAD isometric review.
use <candidate_continuous_corner_walls.scad>;
$fn=48; axis_x=[.95,.60,.05]; axis_y=[.05,.60,.95]; axis_z=[.10,.75,.25];
module arrow_x(x0,x1,y,z,c){color(c){translate([x0,y,z])rotate([0,90,0])cylinder(d=1.8,h=x1-x0);translate([x1,y,z])rotate([0,90,0])cylinder(r1=5.5,r2=0,h=10);}}
module arrow_y(y0,y1,x,z,c){color(c){translate([x,y0,z])rotate([-90,0,0])cylinder(d=1.8,h=y1-y0);translate([x,y1,z])rotate([-90,0,0])cylinder(r1=5.5,r2=0,h=10);}}
module arrow_z(z0,z1,x,y,c){color(c){translate([x,y,z0])cylinder(d=1.8,h=z1-z0);translate([x,y,z1])cylinder(r1=5.5,r2=0,h=10);}}
module top_label(x,y,z,value,c,size=6){color(c)translate([x,y,z])linear_extrude(height=.7)text(value,size=size,font="Arial:style=Bold",halign="center",valign="center");}
candidate_assembly_iso();
arrow_x(-78,78,-52,36,axis_x); top_label(78,-52,47,"+X LONG",axis_x,7);
arrow_y(-78,78,-52,36,axis_y); top_label(-52,78,47,"+Y FRONT",axis_y,7);
arrow_z(-30,64,55,55,axis_z); top_label(55,55,73,"+Z UP",axis_z,7);
color([.12,.12,.12])translate([0,0,30])sphere(d=4);
