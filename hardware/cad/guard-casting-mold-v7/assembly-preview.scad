// Authoritative assembled preview. All hardware below is printable PETG.
use <mold.scad>;
use <../guard-casting-mold-v1/mold.scad>;
use <../guard-casting-mold-v2/mold.scad>;
use <../guard-casting-mold-v3/mold.scad>;
color("#48a8dd",.4)difference(){shell_v7(-1);part_marks("left");}
color("#6383ed",.4)difference(){shell_v7(1);part_marks("right");}
color("#a877df")difference(){lid_v7();part_marks("lid");}
color("#4dbda6")difference(){end_v7(1);part_marks("lower");}
color("#f08eae")difference(){end_v7(-1);part_marks("back");}
color("#eeb750")difference(){upper_v3();part_marks("upper");}
color("#c9e65b")difference(){pull_pin();part_marks("pin");}
color("#ec7956")product();
for(k=["Z","X","Y"])clamp_pose(k){
 color("#dfcf9f")clamp_bolt(k=="Z"?138:k=="X"?168:188,k);
}
// Only TWO J screws, shown at C's alternative use location.
color("#ffad39")lid_sites()j_screw();
