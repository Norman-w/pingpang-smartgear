// v7 custom FDM coarse jack. mm; X upper beam, Y foot, Z upward.
// Reinforced roots and enlarged pouring/vent ports; product shape unchanged.
use <../guard-casting-mold-v2/mold.scad>;
use <../guard-casting-mold-v1/mold.scad>;
use <../guard-casting-mold-v3/mold.scad>;
use <thread-profile.scad>;
FEATURE="assembly";
BX=84;BY=102;Z0=-33.5;Z1=43;CORE_DROP=1;
PITCH=8;CORE_R=9.5;TOOTH_H=1.5;ROOT_W=5.6;CREST_W=1.6;
RADIAL_CLEAR=.3;AXIAL_CLEAR=.25;ENGAGE=32;SHAFT=72;
// Installation clamps use a lighter separate thread.  The two J demolding
// screws intentionally keep the larger hand-screw profile above.
CLAMP_PITCH=8;CLAMP_CORE_R=7;CLAMP_TOOTH_H=1.25;CLAMP_ROOT_W=5.0;CLAMP_CREST_W=1.2;
CLAMP_RADIAL_CLEAR=.3;CLAMP_AXIAL_CLEAR=.25;
module box(a,b){translate(a)cube(b-a);}
module pose(p,r=[0,0,0]){translate(p)rotate(r)children();}
module female_cut(length=32){
 translate([0,0,-.1])cylinder(r=CORE_R+RADIAL_CLEAR,h=length+.2,$fn=96);
 tp_anchored_helix(-.1,length+.1,0,CORE_R,TOOTH_H,PITCH,ROOT_W,CREST_W,radial=RADIAL_CLEAR,axial=AXIAL_CLEAR,steps_turn=96);
 // Continuous mouth taper for alignment; maximum diameter admits the male crest.
 translate([0,0,length-2])cylinder(d1=19.6,d2=24,h=2.1,$fn=96);
}
module clamp_female_cut(length=24){
 translate([0,0,-.1])cylinder(r=CLAMP_CORE_R+CLAMP_RADIAL_CLEAR,h=length+.2,$fn=96);
 tp_anchored_helix(-.1,length+.1,0,CLAMP_CORE_R,CLAMP_TOOTH_H,CLAMP_PITCH,CLAMP_ROOT_W,CLAMP_CREST_W,radial=CLAMP_RADIAL_CLEAR,axial=CLAMP_AXIAL_CLEAR,steps_turn=96);
 translate([0,0,length-2])cylinder(d1=15.6,d2=19,h=2.1,$fn=96);
}
module male_shaft(){union(){
 cylinder(d1=16,d2=19,h=2,$fn=96);
 translate([0,0,1.9])cylinder(r=CORE_R,h=SHAFT-1.9,$fn=96);
 tp_anchored_helix(2,SHAFT-2,0,CORE_R,TOOTH_H,PITCH,ROOT_W,CREST_W,steps_turn=96);
}}
module hand_screw(){union(){male_shaft();
 // Six smooth lobes; hand use only, no wrench flats / long lever holes.
 translate([0,0,SHAFT-.1])linear_extrude(height=10.1)union(){circle(d=36,$fn=96);for(a=[0:60:300])rotate(a)translate([16,0])circle(d=12,$fn=40);}
}}
module j_screw(){difference(){hand_screw();letter_cut([0,0,SHAFT+10],[0,0,0],"J",10);}}
module female_coupon(){difference(){cylinder(d=38,h=ENGAGE,$fn=96);female_cut();}}
module lid_sites(){for(s=[-1,1])pose([s*53,30,30.2])children();}
module end_sites(s){for(x=[-50,50])pose([x,s*51,-12],[s>0?-90:90,0,0])children();}
module side_sites(){for(y=[-48,48])pose([0,y,-57],[0,90,0])children();}
// Main bore keeps 1.9mm separation from central round-hole insert envelope.
POUR_D=10;FUNNEL_D=24;VENT_D=3;VENT_EXIT_D=6;
module enlarged_ports(){
 translate([0,15.5,29.9])cylinder(d=POUR_D,h=14.2,$fn=64);
 translate([0,15.5,37])cylinder(d1=POUR_D,d2=FUNNEL_D,h=6.1,$fn=64);
 for(x=[-23,23])for(y=[-18,18]){
  translate([x,y,29.9])cylinder(d=VENT_D,h=14.2,$fn=40);
  translate([x,y,41.5])cylinder(d1=VENT_D,d2=VENT_EXIT_D,h=1.6,$fn=40);
 }
}
// Printed installation bolts: Z x4, X x1, Y x2; seven same-profile nuts.
// Separate from the two transferable short J demolding screws.
CLAMP_D=17.2;CLAMP_NUT_H=24;
module grip40(h){linear_extrude(height=h)union(){circle(d=38,$fn=96);for(a=[0:60:300])rotate(a)translate([14,0])circle(d=12,$fn=40);}}
module letter_cut(p,r,txt,size=12,spin=0,depth=.7){pose(p,r)rotate([0,0,spin])translate([0,0,-depth])linear_extrude(height=depth+.2)text(txt,size=size,font="Arial:style=Bold",halign="center",valign="center");}
module clamp_bolt(L,mark){difference(){union(){
 cylinder(d1=12.5,d2=15.5,h=2,$fn=96);
 translate([0,0,1.9])cylinder(r=CLAMP_CORE_R,h=48.2,$fn=96);
 tp_anchored_helix(2,48,0,CLAMP_CORE_R,CLAMP_TOOTH_H,CLAMP_PITCH,CLAMP_ROOT_W,CLAMP_CREST_W,radial=CLAMP_RADIAL_CLEAR,axial=CLAMP_AXIAL_CLEAR,phase=180,steps_turn=96);
 translate([0,0,48])cylinder(d=15.5,h=L-52.0,$fn=96);
 translate([0,0,L-4])cylinder(d1=15.5,d2=20,h=4.1,$fn=96);
 translate([0,0,L])grip40(10);
 }letter_cut([0,0,L+10],[0,0,0],mark,12);}}
module clamp_nut(){difference(){grip40(CLAMP_NUT_H);clamp_female_cut(CLAMP_NUT_H);letter_cut([15,0,0],[180,0,0],"N",6);}}
module clamp_pose(k){
 if(k=="Z")for(x=[-22,22])for(y=[-92,92])pose([x,y,-83])children();
 if(k=="X")pose([98,0,-55],[0,-90,0])children();
 if(k=="Y")for(x=[-96,96])pose([x,108,-20],[90,0,0])children();
}
module clamp_holes(){
 for(k=["Z","X","Y"])clamp_pose(k){
  translate([0,0,-.1])cylinder(d=CLAMP_D,h=20.1,$fn=64);
  translate([0,0,20])rotate([0,0,180])clamp_female_cut(24);
  translate([0,0,44])cylinder(d=CLAMP_D,h=166,$fn=64);
  L=k=="Z"?138:k=="X"?168:188;
  translate([0,0,L-4])cylinder(d1=CLAMP_D,d2=29.2,h=4.1,$fn=64);
 }
}
module lower_clamp_tabs(s){for(q=[-1,1])scale([s,q,1])box([0,64,-63],[44,116,-39]);}
module upper_clamp_tabs(){for(x=[-22,22])for(q=[-1,1])scale([1,q,1])box([x-22,40,30.2],[x+22,116,55]);}
module x_clamp_boss(s){scale([s,1,1]){
 box([29,-24,-79],[s>0?78:70,24,-31]);box([29,-24,-33.7],[42,24,-15]);
}}
module y_clamp_boss(s){for(q=[-1,1])scale([q,s,1]){
 box([64,60,-42],[118,s>0?88:80,2]);
 hull(){box([50,60,6],[64.2,80,10.2]);box([63.8,60,-1.8],[64.2,80,2.2]);}
 hull(){box([50,60,-34],[64.2,80,-30]);box([63.8,60,-42],[64.2,80,-38]);}
}}
module part_marks(k){
 if(k=="left")letter_cut([-42,-30,6],[0,-90,0],"A",14,-90);
 if(k=="right")letter_cut([42,-30,6],[0,90,0],"B",14,90);
 if(k=="lid")letter_cut([-15,0,43],[0,0,0],"C",14);
 if(k=="upper")letter_cut([70,0,23],[0,0,0],"D",9);
 if(k=="lower"){letter_cut([118,70,-20],[0,90,0],"E",12,90);letter_cut([-118,70,-20],[0,-90,0],"E",12,-90);}
 if(k=="back"){letter_cut([118,-70,-20],[0,90,0],"F",12,90);letter_cut([-118,-70,-20],[0,-90,0],"F",12,-90);}
 if(k=="pin")letter_cut([34,0,46.5],[0,0,0],"G",4,0,.4);
}
module shell_v7(s){difference(){union(){located_shell(s);lower_clamp_tabs(s);x_clamp_boss(s);
 // Broad top reaction pads; Y>=12 clears the upper-core handle (|Y|<=10.5).
 if(s>0)box([32,12,16],[74,48,30.2]);else box([-74,12,16],[-32,48,30.2]);
 for(q=[-1,1])scale([s,q,1])box([32,37,-30],[68,51,6]);
 // X split jack pads below the original core envelope Z=-33.5.
 for(y=[-48,48]){
 if(s>0)difference(){union(){box([29,max(y-21,-50.8),-75],[50,min(y+21,50.8),-15]);box([0,y-21,-75],[50,y+21,-39]);}
  pose([0,y,-57],[0,90,0]){female_cut();translate([0,0,31.9])cylinder(d=24,h=19,$fn=96);}
 }else{box([-50,max(y-21,-50.8),-75],[-29,min(y+21,50.8),-15]);box([-50,y-21,-75],[0,y+21,-39]);}
 }
}lid_sockets();front_sockets();back_sockets();enlarged_ports();clamp_holes();}}
module lid_v7(){difference(){union(){located_lid();upper_clamp_tabs();
 for(s=[-1,1])scale([s,1,1]){
  box([29,12,30.2],[73,48,62.2]);
  // Sloped root web bonds to lid top; stays clear of the X=23 vent columns.
  hull(){box([25,12,42.8],[33.3,48,43.2]);box([32.8,12,57.8],[33.3,48,58.2]);}
 }
 }lid_sites()female_cut();enlarged_ports();clamp_holes();}}
module end_v7(s){difference(){union(){
 if(s>0)located_lower();else located_back();
 // Wide 14mm end plate ties both seats into the existing shoulder, not thin ears.
 for(x=[-22,22])scale([1,s,1])box([x-23,60,-34],[x+23,92,16]);
 for(x=[-22,22])intersection(){translate([x,s*92,-34])cylinder(d=46,h=50,$fn=64);scale([1,s,1])box([-50,51,-35],[50,116,17]);}
 y_clamp_boss(s);
 scale([1,s,1])box([-71,51,-34],[71,65,16]);
 for(q=[-1,1])scale([q,s,1]){
  box([29,51,-34],[71,83,10]);
  hull(){box([22,64.8,-25],[29.2,65.2,6]);box([28.8,79.8,-25],[29.2,80.2,6]);}
 }
 }end_sites(s){female_cut();translate([0,0,31.9])cylinder(d=24,h=41,$fn=64);}clamp_holes();}}
if(FEATURE=="clamp-Z")clamp_bolt(138,"Z");
else if(FEATURE=="clamp-X")clamp_bolt(168,"X");
else if(FEATURE=="clamp-Y")clamp_bolt(188,"Y");
else if(FEATURE=="clamp-nut")clamp_nut();
else if(FEATURE=="left")difference(){shell_v7(-1);part_marks("left");}
else if(FEATURE=="right")difference(){shell_v7(1);part_marks("right");}
else if(FEATURE=="lid")difference(){lid_v7();part_marks("lid");}
else if(FEATURE=="lower")difference(){end_v7(1);part_marks("lower");}
else if(FEATURE=="back")difference(){end_v7(-1);part_marks("back");}
else if(FEATURE=="upper")difference(){upper_v3();part_marks("upper");}
else if(FEATURE=="pin")difference(){pull_pin();part_marks("pin");}
else if(FEATURE=="product")product();
else if(FEATURE=="screw")j_screw();
else if(FEATURE=="male-test")male_shaft();
else if(FEATURE=="female-test")female_coupon();
else{color("#48a8dd",.4)shell_v7(-1);color("#6383ed",.4)shell_v7(1);color("#a877df")lid_v7();color("#4dbda6")end_v7(1);color("#f08eae")end_v7(-1);color("#eeb750")upper_v3();color("#ec7956")product();}
