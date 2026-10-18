// v1.1 top slice at z=-0.5..2.5, exposing front/back depths and the open gap.
use <candidate_full_corner_walls.scad>;
$fn=48; axis_x=[.95,.60,.05]; axis_y=[.05,.60,.95]; label_color=[.08,.10,.12];
module arrow_x(x0,x1,y,z,c){color(c){translate([x0,y,z])rotate([0,90,0])cylinder(d=1.2,h=x1-x0);translate([x1,y,z])rotate([0,90,0])cylinder(r1=3,r2=0,h=7);}}
module arrow_y(y0,y1,x,z,c){color(c){translate([x,y0,z])rotate([-90,0,0])cylinder(d=1.2,h=y1-y0);translate([x,y1,z])rotate([-90,0,0])cylinder(r1=3,r2=0,h=7);}}
module text_xy(value,x,y,z,size=5,c=label_color){color(c)translate([x,y,z])linear_extrude(height=.7)text(value,size=size,font="Arial:style=Bold",halign="center",valign="center");}
candidate_top_slice();
arrow_x(-50,50,-38,4,axis_x); text_xy("+X LONG",50,-38,4,4,axis_x);
arrow_y(-35,35,42,4,axis_y); text_xy("+Y FRONT",42,35,4,4,axis_y);
text_xy("TOP SLICE z=-0.5..2.5",-28,45,4,4,label_color);
text_xy("FRONT y=+10..+21 (11 mm)",0,15,4,3.5,label_color);
text_xy("OPEN CENTRAL GAP y=-10..+10 (20 mm)",0,0,4,3.5,label_color);
text_xy("BACK y=-21..-10 (11 mm)",0,-15,4,3.5,label_color);
