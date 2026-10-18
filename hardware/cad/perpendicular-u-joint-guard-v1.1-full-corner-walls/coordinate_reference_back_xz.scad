// v1.1 -Y BACK XZ check; reflected only for an upright review camera.
use <candidate_full_corner_walls.scad>;
$fn=48; axis_x=[.95,.60,.05]; axis_y=[.05,.60,.95]; axis_z=[.10,.75,.25]; label_color=[.08,.10,.12];
module arrow_x(x0,x1,y,z,c){color(c){translate([x0,y,z])rotate([0,90,0])cylinder(d=1.2,h=x1-x0);translate([x1,y,z])rotate([0,90,0])cylinder(r1=2.5,r2=0,h=8);}}
module arrow_z(z0,z1,x,y,c){color(c){translate([x,y,z0])cylinder(d=1.2,h=z1-z0);translate([x,y,z1])cylinder(r1=2.5,r2=0,h=8);}}
module text_xz(value,x,y,z,size=5,c=label_color,halign="left"){color(c)translate([x,y,z])rotate([90,0,0])linear_extrude(height=.7)text(value,size=size,font="Arial:style=Bold",halign=halign,valign="center");}
module y_dot(x,y,z){color(axis_y)translate([x,y,z])rotate([90,0,0])cylinder(d=9,h=1.2,center=true);}
module y_cross(x,y,z){color(axis_y)translate([x,y,z])rotate([90,0,0])cylinder(d=10,h=1.2,center=true,$fn=4);}
mirror([0,1,0]) candidate_back_xz();
arrow_x(-56,56,38,-34,axis_x); text_xz("+X LONG / BOTH ENDS SLOPE INWARD",-56,38,-41,4.1,axis_x);
arrow_z(-34,50,44,38,axis_z); text_xz("+Z UP / SCREW AXIS",50,38,54,4.2,axis_z);
y_dot(-52,38,15); text_xz("+Y FRONT (AWAY)",-46,38,15,3.8,axis_y);
y_cross(-52,38,3); text_xz("-Y BACK y=-21..-10",-46,38,3,3.8,axis_y);
text_xz("v1.1 FULL BACK CORNER WALLS",-58,38,62,4.8,label_color);
text_xz("LANDING z=0 / GREY TUBE HIDDEN",-56,38,-48,4.0,label_color);
