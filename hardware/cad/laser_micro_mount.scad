// Individual bare-laser kinematic cassette. Included by net_stand.scad.
// Units: mm. Prototype contract: PETG rigid parts, split TPU spherical liner,
// purchased steel spring and M2 hardware. No printed threads or sealing claim.
// Front is -x. Pitch is +rotation about y; yaw is +rotation about z.
// The two 45-degree adjusters are A/B, NOT independent pitch/yaw screws.
// Their common/differential travel sets the two angular degrees of freedom.
laser_module_d = 6;                 // provisional, measure the purchased head
laser_module_length = 12;           // provisional, body only, excluding wires
laser_module_clearance = 0.25;       // diametral FDM fit allowance
laser_micro_range_deg = 3;
laser_micro_pitch_deg = 0;
laser_micro_yaw_deg = 0;
laser_micro_explode = 0;
laser_micro_ball_d = 10;
laser_micro_tail_d = 8.4;
laser_micro_lever = 12;
laser_micro_screw_pitch = 0.4;       // M2 standard pitch, travel per turn
laser_micro_screw_length = 8;
laser_micro_screw_d = 2;
laser_micro_cap_screw_length = 14;
laser_micro_mount_screw_length = 10;
laser_micro_spring_wire = .4;
laser_micro_spring_radius = 1.4;     // centreline radius; OD 3.2
// Front anti-retraction ring that wraps the tip sphere and resists +x retraction.
// Small profile keeps ±3° sweep clearance while still creating a stop shoulder.
laser_micro_front_guard_outer_d = 9.0;
laser_micro_front_guard_inner_d = laser_module_d + laser_module_clearance + 0.6; // default clearance around 6.8 mm
laser_micro_front_guard_x = -3.2;
laser_micro_front_guard_len = 1.5;
laser_micro_front_guard_release = 0.75;
// Short rear radial pusher on the opposite side from the existing retention
// screw.  It presses the copper body inward near its rear end while the
// carrier's rear insertion bore remains open.
laser_micro_rear_pusher_d = 3.4;          // M3-class flat-point set screw
laser_micro_rear_pusher_clearance = 0.3;  // boss inner edge beyond the Ø6 body
laser_micro_rear_pusher_tap_d = 2.5;      // M3 printed-tap pilot (use insert for service)
laser_micro_rear_pusher_length = 3.0;     // nominal M3×3; tip stops at y=-3.05
laser_micro_rear_pusher_x = 8.0;          // rear section of the Ø6 mm body
laser_micro_rear_pusher_axis_y = -5.9;    // outside face; screw advances +y
laser_micro_rear_pusher_tip_setback = 0.15; // nominal 0.05 mm radial gap before hand-tightening
laser_micro_rear_pusher_axis_z = 0;
laser_micro_rear_pusher_boss_x = 6.0;
laser_micro_rear_pusher_boss_len = 4.0;
laser_micro_rear_pusher_boss_width = 2.6;
laser_micro_rear_pusher_boss_height = 4.2;
laser_micro_rear_pusher_drive_af = 2.0;
laser_micro_rear_pusher_withdraw = 3.0;
laser_micro_spring_turns = 4;
laser_micro_spring_free_height = 4.6; // candidate; force/rate still needs measurement
laser_micro_spring_floor = -7.6;
laser_micro_spring_pad = -4.1;
laser_micro_mount_y = 20;
laser_micro_origin_x = m6_detector_body_min_x;
// End-band cover screws avoid the cassette openings at the old first/last
// optical centres. The two new covers and rail must be used together.
laser_micro_cover_screw_z = [m6_detector_body_bottom_z+5,m6_detector_body_top_z-5];
laser_micro_frame_height = 18;
// The bare-head ears need a wider, deeper optical cap. Its cavity follows
// the curved outline; a rectangular cut previously erased the curved walls.
laser_micro_front_extra_depth = 6;
laser_micro_front_half_y = 31.8;
laser_micro_front_wall = 2.4;
laser_micro_front_min_x = m6_detector_shell_min_x-laser_micro_front_extra_depth;
laser_micro_front_screw_entry_x = laser_micro_front_min_x;
// The top screw must stay between the A/B tool axes, not cross either one.
laser_micro_front_screw_y = 0;
// Tool contract: AF4 through-tube for the locknut, OD <=6 mm, 60 mm
// working length; an AF1 key passes through it to hold the grub screw.
// The cylindrical envelope also covers a full turn of the tube/handle.
laser_micro_tool_d = 6;
laser_micro_tool_clearance = 0.5;     // radial allowance, not printer accuracy
laser_micro_access_d = laser_micro_tool_d+2*laser_micro_tool_clearance;
laser_micro_tool_length = 60;
laser_micro_tool_handle_d = 22;
laser_micro_tool_handle_length = 40;
laser_micro_service_channel = 8;    // zero based: channel 9
laser_micro_service_sign = 1;
laser_micro_service_withdraw = 0;
bare_laser_enabled = true;          // left TX cassette; RX interface unchanged
laser_micro_collision_mode = 0;     // 0 all; 1 moving/frame; 2 shell/rail; 3 adjacent

assert(laser_module_d > 0 && laser_module_d <= 6.2,
       "Current 20 mm cassette accepts <=6.2 mm heads; resize the shell for larger heads");
assert(laser_module_length > 0 && laser_module_length <= 15,
       "Measure the head: current tube supports bodies <=15 mm long");
assert(abs(laser_micro_pitch_deg) <= laser_micro_range_deg &&
       abs(laser_micro_yaw_deg) <= laser_micro_range_deg,
       "Individual adjustment must stay within the checked +/-3 degree range");
assert(laser_micro_rear_pusher_axis_y-laser_micro_rear_pusher_tip_setback+
       laser_micro_rear_pusher_length <= -laser_module_d/2+1e-6,
       "Rear pusher nominal tip must not penetrate the laser body");
assert(laser_micro_rear_pusher_tap_d < laser_micro_rear_pusher_d,
       "Rear pusher boss must have a threaded pilot smaller than the screw OD");
assert((-laser_module_d/2)-(laser_micro_rear_pusher_axis_y+
       laser_micro_rear_pusher_boss_width) >= laser_micro_rear_pusher_clearance-1e-6,
       "Rear pusher boss must leave the specified rear insertion clearance");

module lm_xcyl(d, h, x=0, y=0, z=0, facets=48) {
    translate([x,y,z]) rotate([0,90,0]) cylinder(d=d,h=h,$fn=facets);
}
module lm_half(top=true) {
    intersection() {
        children();
        translate([-40,-40,top ? 0 : -40]) cube([100,80,40]);
    }
}
module lm_adjust_axis(sign=1) {
    translate([laser_micro_lever,0,0]) rotate([-sign*45,0,0]) children();
}
module lm_moving(pitch=laser_micro_pitch_deg,yaw=laser_micro_yaw_deg) {
    rotate([0,0,yaw]) rotate([0,pitch,0]) children();
}
// A flat M2 end is a disk, not a point on the screw axis. Find the furthest
// tail surface under that disk. The old centre-ray solution penetrated the
// tilted tail. A coarse bracket plus bounded refinement locates rim contact;
// at zero tilt the maximum also lies on the rim along the cylinder axis.
function lm_tip_ray(sign,p,y,angle) =
    let(a=[cos(p)*cos(y),cos(p)*sin(y),-sin(p)],
        n=[0,sign/sqrt(2),1/sqrt(2)],
        r=laser_micro_screw_d/2,
        q=[laser_micro_lever+r*cos(angle),r*sin(angle)/sqrt(2),-sign*r*sin(angle)/sqrt(2)],
        b=q*a, c=n*a,
        aa=1-c*c, bb=-2*b*c,
        cc=q*q-b*b-pow(laser_micro_tail_d/2,2))
    (-bb+sqrt(bb*bb-4*aa*cc))/(2*aa);
function lm_tip_refine(s,p,y,lo,hi,n=28) = n==0 ? (lo+hi)/2 :
    let(a=lo+(hi-lo)/3,b=hi-(hi-lo)/3)
    lm_tip_ray(s,p,y,a)>lm_tip_ray(s,p,y,b)
      ? lm_tip_refine(s,p,y,lo,b,n-1) : lm_tip_refine(s,p,y,a,hi,n-1);
function lm_tip(sign,p=laser_micro_pitch_deg,y=laser_micro_yaw_deg) =
    let(values=[for(a=[0:15:345]) lm_tip_ray(sign,p,y,a)],
        centre=15*search(max(values),values)[0])
    lm_tip_ray(sign,p,y,lm_tip_refine(sign,p,y,centre-15,centre+15));
function lm_rotate(v,p,y) = [cos(y)*(cos(p)*v[0]+sin(p)*v[2])-sin(y)*v[1],
    sin(y)*(cos(p)*v[0]+sin(p)*v[2])+cos(y)*v[1],-sin(p)*v[0]+cos(p)*v[2]];
function lm_phase(e,a,b) = min(1,max(0,(e-a)/(b-a)));

// Bench disassembly, after removing a complete cassette from the rail.
// Captive nuts remain in their seats. A hand supports the spring-loaded tube
// while its cap is released. Separate axial exits before lateral parking.
function lm_cap_move(e) = [35*lm_phase(e,.44,.52),0,16*lm_phase(e,.36,.44)];
function lm_bolt_move(e) = [0,32*lm_phase(e,.30,.36),18*lm_phase(e,.18,.30)];
function lm_upper_liner_move(e) = [0,-24*lm_phase(e,.60,.66),11*lm_phase(e,.52,.60)];
function lm_carrier_move(e) = [-24*lm_phase(e,.76,.84),0,18*lm_phase(e,.66,.76)];
function lm_laser_move(e) = lm_carrier_move(e)+[20*lm_phase(e,.92,1),0,0];
function lm_lock_withdraw(e) = .6*lm_phase(e,0,.08);
function lm_screw_withdraw(e) = 1.2*lm_phase(e,.08,.18);
function lm_retention_withdraw(e) = 1.2*lm_phase(e,.84,.92);
function lm_rear_pusher_withdraw(e) = laser_micro_rear_pusher_withdraw*lm_phase(e,.84,.92);
function lm_bench_motion(e) = [lm_cap_move(e),lm_bolt_move(e),lm_upper_liner_move(e),
    lm_carrier_move(e),lm_laser_move(e),lm_lock_withdraw(e),lm_screw_withdraw(e),
    lm_retention_withdraw(e),lm_spring_release(e),lm_rear_pusher_withdraw(e)];
// Both head covers are serviced with the rail, rear housing and ballhead fixed.
// Pull each screw clear of the cap before parking it outside its full width.
function lm_cover_motion(e) = [[-50*lm_phase(e,.6,1),0,0],
    [-34*lm_phase(e,0,.4),45*lm_phase(e,.4,.6),0]];

module lm_hex(af=4,h=1.6,bore=2) {
    difference() {
        cylinder(d=af/cos(30),h=h,$fn=6);
        translate([0,0,-.1]) cylinder(d=bore,h=h+.2,$fn=24);
    }
}
module lm_frame_envelope() {
    union() {
        // Front ring; split along z=0 to install and preload the TPU liner.
        translate([-4,-14,-9]) cube([8,28,18]);
        // Two side rails connect front ring to the rear reaction block.
        // Widen inward before cutting the lower neighbour's tool scallops.
        // The remaining side webs connect the spring floor to the front ring.
        for (s=[-1,1]) translate([3,s>0 ? 9.5 : -14,-9]) cube([14,4.5,18]);
        translate([10,0,0]) rotate([0,90,0]) linear_extrude(7)
            polygon([[-9,-8],[-9,8],[-3,14],[3,14],
                     [9,8],[9,-8],[3,-14],[-3,-14]]);
        // Front-access M2.5 mounting ears land on the unchanged carrier face.
        for(s=[-1,1]) hull() {
            lm_xcyl(8,4,-4,s*laser_micro_mount_y,0);
            translate([-4,s>0 ? 10 : -14,-4]) cube([4,4,8]);
        }
    }
}
module lm_frame_voids() {
    lm_xcyl(12.2,6,-3);       // liner outer seat, 1 mm retaining lips
    lm_xcyl(9.6,12,-6);      // front aperture and swinging neck clearance
    translate([4,-9,-5.4]) cube([6.1,18,11.5]);
    translate([9.9,-6,-5.4]) cube([8,12,11.5]);
    // Wire outlet through the rear, below/above the spring reaction floor.
    lm_xcyl(10.8,5,15);
    for(s=[-1,1]) {
        // Counterbores enter from z+, nuts insert from z- into the lower half.
        translate([0,s*10,-10]) cylinder(d=2.3,h=20,$fn=28);
        translate([0,s*10,6]) cylinder(d=4,h=4,$fn=32);
        translate([0,s*10,-9.1]) cylinder(d=4.4/cos(30),h=3.5,$fn=6);
        lm_xcyl(2.8,6,-5,s*laser_micro_mount_y);
        // Captive nut loads from x+. The larger coaxial counterbore admits
        // the locknut tube, with room for an AF1 holding key through its bore.
        lm_adjust_axis(s) {
            translate([0,0,3]) cylinder(d=2.3,h=20,$fn=28);
            translate([0,0,6.4]) cylinder(d=4.4/cos(30),h=1.9,$fn=6);
            translate([0,-2.3,6.4]) cube([8,4.6,1.9]);
            translate([0,0,9]) cylinder(d=laser_micro_access_d,h=80,$fn=48);
        }
        // A tool aimed at the channel below used to hit this cassette's
        // lower side rail. Remove its whole clearance envelope, not just
        // the screwdriver centreline. Identical scallops on every cassette.
        translate([0,0,-m6_sensor_center_pitch]) lm_adjust_axis(s)
            translate([0,0,9]) cylinder(d=laser_micro_access_d,h=80,$fn=48);
    }
    // Spring pocket has a floor at z=-7.6; it does not pierce the base.
    // Flare the mouth for the bent spring at combined pitch/yaw; keep the
    // lower seat centred and the load-bearing floor continuous.
    translate([laser_micro_lever,0,laser_micro_spring_floor]) cylinder(d1=3.6,d2=5.4,h=3,$fn=48);
}
module lm_frame(top=false) {
    lm_half(top) difference() { lm_frame_envelope(); lm_frame_voids(); }
}
module lm_liner(top=false) {
    lm_half(top) difference() {
        lm_xcyl(12.3,6,-3);  // 0.1 mm diametral outer preload, tune on a coupon
        sphere(d=10.1,$fn=64);
        lm_xcyl(9.2,9,-4.5);
    }
}
module lm_front_retract_collar() {
    // Front anti-retraction sleeve: covers the round tip and adds a rear shoulder.
    difference() {
        intersection() {
            translate([laser_micro_front_guard_x,0,0]) sphere(d=laser_micro_front_guard_outer_d,$fn=64);
            translate([laser_micro_front_guard_x,0,0])
                cube([laser_micro_front_guard_len,28,28],center=true);
        }
        intersection() {
            translate([laser_micro_front_guard_x,0,0]) sphere(d=laser_micro_front_guard_inner_d,$fn=64);
            translate([laser_micro_front_guard_x,0,0])
                cube([laser_micro_front_guard_len + 0.2,28,28],center=true);
        }
        // Rearward opening so assembly from +x is not permanently jammed.
        translate([laser_micro_front_guard_x + laser_micro_front_guard_len/2,0,0])
            cube([laser_micro_front_guard_len - laser_micro_front_guard_release,28,28],center=true);
        // Keep collar clear from the rear tail and side lands.
        translate([laser_micro_front_guard_x,0,0]) cube([0.8,28,28],center=true);
        // Front aperture is already used by the optical bore; preserve it.
        lm_xcyl(6,20,laser_micro_front_guard_x-10,0,-6);
    }
}
module lm_rear_pusher_boss() {
    // The boss is outside the lower-side bore wall.  Its inner edge stays
    // 0.3 mm beyond the Ø6 mm head envelope so rear insertion remains clear.
    translate([laser_micro_rear_pusher_boss_x,
               laser_micro_rear_pusher_axis_y,
               laser_micro_rear_pusher_axis_z-laser_micro_rear_pusher_boss_height/2])
        cube([laser_micro_rear_pusher_boss_len,
              laser_micro_rear_pusher_boss_width,
              laser_micro_rear_pusher_boss_height]);
}
module lm_rear_pusher_bore() {
    translate([laser_micro_rear_pusher_x,
               laser_micro_rear_pusher_axis_y-.1,
               laser_micro_rear_pusher_axis_z])
        rotate([-90,0,0])
            // Ø2.5 pilot is intentionally undersize for an M3 printed tap;
            // it is not a loose clearance hole.
            cylinder(d=laser_micro_rear_pusher_tap_d,
                     h=laser_micro_rear_pusher_boss_width+.2,$fn=32);
}
module lm_carrier() {
    difference() {
        union() {
            sphere(d=laser_micro_ball_d,$fn=64);
            lm_front_retract_collar();
            lm_xcyl(laser_micro_tail_d,15,0);
            lm_rear_pusher_boss();
            // A 4.4 mm wide bearing land supports the entire OD3.2 spring.
            // Cutting a flat from the cylinder alone left only a 1.82 mm land.
            translate([10,-2.2,laser_micro_spring_pad]) cube([5,4.4,.85]);
            // Retention grub screw uses a captured metal nut, not PETG thread.
            translate([5,3,-3]) cube([4,4.8,6]);
        }
        lm_rear_pusher_bore();
        lm_xcyl(laser_module_d+laser_module_clearance,23,-3);
        lm_xcyl(4.5,4,-6); // front stop lip, does not obstruct the optical bore
        translate([7,2,0]) rotate([-90,0,0]) cylinder(d=2.3,h=8,$fn=28);
        translate([7,5.4,0]) rotate([-90,0,0]) cylinder(d=4.4/cos(30),h=1.9,$fn=6);
        translate([5,-.01+5.4,0]) cube([4,1.91,4]);
        // Flat tangent contact for the spring at the tail.
        translate([10,-6,-8]) cube([5,12,3.9]);
    }
}
module lm_laser() {
    difference() {
        lm_xcyl(laser_module_d,laser_module_length,-3);
        lm_xcyl(3,1,-3.1);
    }
}
module lm_grub(length=8) {
    difference() {
        cylinder(d=2,h=length,$fn=24);
        translate([0,0,length-1.4]) cylinder(d=1.05/cos(30),h=1.5,$fn=6);
    }
}
module lm_adjust_screw(sign=1,withdraw=0) { lm_adjust_axis(sign) translate([0,0,lm_tip(sign)+withdraw])
    rotate([0,0,360*withdraw/laser_micro_screw_pitch]) lm_grub(laser_micro_screw_length); }
module lm_adjust_nut(sign=1,lock=false,withdraw=0) { lm_adjust_axis(sign) translate([0,0,(lock ? 9 : 6.55)+withdraw])
    rotate([0,0,360*withdraw/laser_micro_screw_pitch]) lm_hex(); }
module lm_retention_screw(withdraw=0) {
    translate([7,laser_module_d/2+withdraw,0]) rotate([-90,0,0])
        rotate([0,0,360*withdraw/laser_micro_screw_pitch]) lm_grub(5);
}
module lm_retention_nut() {
    translate([7,5.55,0]) rotate([-90,0,0]) lm_hex();
}
module lm_retention_hardware() { lm_retention_nut(); lm_retention_screw(); }
module lm_rear_pusher_screw(withdraw=0) {
    // Flat-point M3-class screw enters from the rear-side outside face and
    // bears on the Ø6 mm body.  The hex socket is on the accessible outside
    // face; positive withdraw moves it farther out along -y.
    translate([laser_micro_rear_pusher_x,
               laser_micro_rear_pusher_axis_y-laser_micro_rear_pusher_tip_setback-withdraw,
               laser_micro_rear_pusher_axis_z])
        rotate([-90,0,0]) difference() {
            cylinder(d=laser_micro_rear_pusher_d,
                     h=laser_micro_rear_pusher_length,$fn=32);
            translate([0,0,-.01])
                cylinder(d=laser_micro_rear_pusher_drive_af/cos(30),h=1.1,$fn=6);
        }
}
module lm_rear_pusher_hardware(withdraw=0) { lm_rear_pusher_screw(withdraw); }
module lm_cap_bolt(s=1,withdraw=0) {
        translate([0,s*10,withdraw]) rotate([0,0,360*min(withdraw,3)/laser_micro_screw_pitch]) {
            translate([0,0,6-laser_micro_cap_screw_length]) cylinder(d=2,h=laser_micro_cap_screw_length,$fn=24);
            translate([0,0,6]) difference() {
                cylinder(d=3.8,h=2,$fn=32);
                translate([0,0,.7]) cylinder(d=1.55/cos(30),h=1.4,$fn=6);
            }
        }
}
module lm_cap_bolts(withdraw=0) { for(s=[-1,1]) lm_cap_bolt(s,withdraw); }
module lm_cap_nuts() { for(s=[-1,1]) translate([0,s*10,-7.25]) lm_hex(); }
module lm_cap_hardware() { lm_cap_bolts(); lm_cap_nuts(); }
// Constant wire diameter. The centreline bends between the fixed floor and
// the rotating spring land. End turns have wire-diameter pitch; no mesh scale.
function lm_spring_point(u,p=laser_micro_pitch_deg,y=laser_micro_yaw_deg,lift=0) =
    let(w=laser_micro_spring_wire,
        bottom=[laser_micro_lever,0,laser_micro_spring_floor+w/2],
        top=lm_rotate([laser_micro_lever,0,laser_micro_spring_pad-w/2],p,y)+[0,0,lift],
        h=top[2]-bottom[2], turns=laser_micro_spring_turns, t=u*turns,
        z=t<1 ? w*t : t>turns-1 ? h-w*(turns-t) : w+(h-2*w)*(t-1)/(turns-2),
        f=z/h,
        ring=lm_rotate([laser_micro_spring_radius*cos(360*t),laser_micro_spring_radius*sin(360*t),0],p*f,y*f))
    bottom+(top-bottom)*f+ring;
function lm_spring_release(e) = min(lm_carrier_move(e)[2],
    laser_micro_spring_free_height-(laser_micro_spring_pad-laser_micro_spring_floor));
module lm_spring(lift=0) {
    for(i=[0:laser_micro_spring_turns*32-1]) hull() {
        for(j=[i,i+1]) translate(lm_spring_point(j/(laser_micro_spring_turns*32),
            laser_micro_pitch_deg,laser_micro_yaw_deg,lift)) sphere(d=laser_micro_spring_wire,$fn=8);
    }
}
module lm_mount_hardware() {
    for(s=[-1,1]) {
        lm_xcyl(2.5,laser_micro_mount_screw_length,-4,s*laser_micro_mount_y);
        lm_xcyl(4.5,2.5,-6.5,s*laser_micro_mount_y);
        translate([3,s*laser_micro_mount_y,0]) rotate([0,90,0]) lm_hex(5,2,2.5);
    }
}
module laser_micro_assembly(e=laser_micro_explode) {
    color("#647d96") lm_frame(false);
    assert(e==0 || (laser_micro_pitch_deg==0 && laser_micro_yaw_deg==0),"Return to zero before bench disassembly");
    color("#86a9c4") translate(lm_cap_move(e)) lm_frame(true);
    color("#46cfb2") lm_liner(false);
    color("#46cfb2") translate(lm_upper_liner_move(e)) lm_liner(true);
    lm_moving() {
        color("#ec934b") translate(lm_carrier_move(e)) lm_carrier();
        // Body withdraws toward +x from the carrier's rear; the small front
        // aperture is a physical stop, not a valid assembly path.
        color("#d4b567") translate(lm_laser_move(e)) lm_laser();
        color("silver") translate(lm_carrier_move(e)) { lm_retention_nut(); lm_retention_screw(lm_retention_withdraw(e)); }
        color("silver") translate(lm_carrier_move(e))
            lm_rear_pusher_hardware(lm_rear_pusher_withdraw(e));
    }
    color("silver") {
        translate(lm_cap_move(e)) for(s=[-1,1]) {
            lm_adjust_screw(s,lm_screw_withdraw(e)); lm_adjust_nut(s); lm_adjust_nut(s,true,lm_lock_withdraw(e));
        }
        translate([0,lm_bolt_move(e)[1],0]) lm_cap_bolts(lm_bolt_move(e)[2]);
        lm_cap_nuts();
        lm_spring(lm_spring_release(e));
        lm_mount_hardware();
    }
}
module laser_micro_rail_positive() {
    difference() {
        m6_detector_body_positive(laser_micro_cover_screw_z);
        // The sleeve also crosses the final 1.5 mm of the rail's back edge.
        // Keep the other 8.5 mm of its continuous spine intact.
        laser_micro_service_passages();
        lm_front_mount_clearances();
        for(i=[0:m6_sensor_count-1]) translate([laser_micro_origin_x,0,m6_sensor_z(i)]) {
            // Continuous outer spines carry the loads; tiny inter-row webs
            // only separate channels.  Covers retain their existing grooves.
            translate([-.1,-14.4,-9.4]) cube([10.2,28.8,18.8]);
            for(s=[-1,1]) {
                lm_xcyl(2.8,12,-1,s*laser_micro_mount_y);
                translate([3,s*laser_micro_mount_y,0]) rotate([0,90,0]) cylinder(d=5.35/cos(30),h=8,$fn=6);
            }
        }
    }
}
// Shared front-cover interface for the TX cassette rail and RX carrier.
module lm_front_mount_clearances() {
    for(s=[-1,1])
        translate([m6_detector_body_min_x-.1,
                   s>0 ? m6_detector_body_max_y-m6_detector_body_groove_depth_y : m6_detector_body_min_y,
                   m6_detector_body_bottom_z+m6_detector_body_groove_margin_z])
            cube([m6_detector_shell_front_max_x-m6_detector_body_min_x+.2,
                  m6_detector_body_groove_depth_y,
                  m6_detector_body_height_z-2*m6_detector_body_groove_margin_z]);
    for(z=laser_micro_cover_screw_z) {
        lm_xcyl(3.3,m6_detector_body_length_x+2,m6_detector_body_min_x-1,
                laser_micro_front_screw_y,z);
        translate([m6_detector_body_max_x-3,laser_micro_front_screw_y,z])
            rotate([0,90,0]) cylinder(d=5.9/cos(30),h=3.2,$fn=6);
    }
}
module laser_micro_array_positive() {
    color("#526f89") laser_micro_rail_positive();
    for(i=[0:m6_sensor_count-1])
        translate([laser_micro_origin_x,0,m6_sensor_z(i)]) laser_micro_assembly();
}
module laser_micro_detector_positive() {
    translate([m6_detector_mount_x_offset,0,m6_detector_mount_raise_z]) {
        laser_micro_array_positive();
        if(m6_detector_show_shell) {
            laser_micro_front_cover();
            laser_micro_rear_cover();
            laser_micro_bottom_cover();
            laser_micro_bottom_gasket();
            laser_micro_front_hardware();
            m6_detector_cable_gland_positive();
        }
        m6_detector_ballhead_positive();
    }
}

module laser_micro_service_passages() {
    for(i=[0:m6_sensor_count-1])
        translate([laser_micro_origin_x,0,m6_sensor_z(i)])
            for(s=[-1,1]) lm_adjust_axis(s) translate([0,0,9])
                cylinder(d=laser_micro_access_d,h=80,$fn=48);
}
module lm_front_footprint() {
    x=m6_detector_shell_front_max_x;
    polygon(concat([[x,-laser_micro_front_half_y]],
        [for(a=[-90:2:90]) [x-(x-laser_micro_front_min_x)*cos(a),laser_micro_front_half_y*sin(a)]],
        [[x,laser_micro_front_half_y]]));
}
module lm_front_inner_footprint() {
    union() {
        offset(delta=-laser_micro_front_wall) lm_front_footprint();
        // Open the rear mating face while preserving both curved side walls.
        translate([m6_detector_shell_front_max_x-laser_micro_front_wall-.1,
                   -laser_micro_front_half_y+laser_micro_front_wall])
            square([laser_micro_front_wall+1.2,
                    2*(laser_micro_front_half_y-laser_micro_front_wall)]);
    }
}
module lm_front_outer() {
    translate([0,0,m6_detector_shell_bottom_z])
        linear_extrude(m6_detector_shell_height_z) lm_front_footprint();
}
module lm_front_cavity() {
    translate([0,0,m6_detector_shell_bottom_z-.1])
        linear_extrude(m6_detector_shell_height_z-laser_micro_front_wall+.1)
            lm_front_inner_footprint();
}
module lm_front_tongue(s) {
    w=max(.5,m6_detector_body_groove_width_x/2-2*m6_detector_shell_tongue_clearance);
    x=m6_detector_body_center_x-m6_detector_body_groove_width_x/2+m6_detector_shell_tongue_clearance;
    inside=m6_detector_body_max_y-m6_detector_body_groove_depth_y+m6_detector_shell_tongue_clearance;
    outside=laser_micro_front_half_y-.4;
    translate([x,s>0 ? inside : -outside,
               m6_detector_body_bottom_z+m6_detector_body_groove_margin_z])
        cube([w,outside-inside,m6_detector_body_height_z-2*m6_detector_body_groove_margin_z]);
}
module laser_micro_front_cover() {
    color("#728394") difference() {
        union() {
            difference() { lm_front_outer(); lm_front_cavity(); }
            for(s=[-1,1]) lm_front_tongue(s);
            // Flat countersunk entry pads connect through tapered supports
            // toward the rail. The support narrows before reaching channel 1
            // or 10, retaining a 0.5 mm gap to their front rings.
            for(z=laser_micro_cover_screw_z) union() {
                lm_xcyl(10,9,laser_micro_front_screw_entry_x,laser_micro_front_screw_y,z);
                hull() {
                    lm_xcyl(10,.5,laser_micro_front_screw_entry_x+8.5,laser_micro_front_screw_y,z);
                    translate([laser_micro_origin_x-5.8,laser_micro_front_screw_y-5,z-3.5])
                        cube([.5,10,7]);
                }
                translate([laser_micro_origin_x-5.8,laser_micro_front_screw_y-5,z-3.5])
                    cube([5.8,10,7]); // hard stop seats on rail at x=origin
            }
        }
        for(i=[0:m6_sensor_count-1])
            lm_xcyl(m6_detector_optical_bore_d,laser_micro_front_wall+3,
                    laser_micro_front_min_x-1,0,m6_sensor_z(i));
        for(z=laser_micro_cover_screw_z)
            m6_countersink_x(laser_micro_front_screw_entry_x,1,
                laser_micro_origin_x-laser_micro_front_screw_entry_x+1,
                laser_micro_front_screw_y,z,m6_detector_shell_screw_pilot_d,
                m6_detector_shell_screw_head_d,m6_detector_shell_screw_head_depth);
    }
}
module lm_complete_footprint() {
    union() { m6_detector_shell_footprint_positive(); lm_front_footprint(); }
}
module laser_micro_bottom_cover() {
    // The floor must grow with the front cap; the old floor left an open lip.
    color("#526f89") difference() {
        translate([0,0,m6_detector_shell_bottom_z-m6_detector_bottom_cover_t])
            linear_extrude(m6_detector_bottom_cover_t) lm_complete_footprint();
        translate([m6_detector_cable_exit_x,m6_detector_cable_exit_y,m6_detector_shell_bottom_z-4])
            cylinder(d=m6_detector_cable_exit_d,h=5,$fn=48);
        for(x=m6_detector_bottom_screw_x)
            m6_countersink_z(m6_detector_shell_bottom_z-m6_detector_bottom_cover_t,1,
                m6_detector_bottom_cover_t+2,x,0,m6_detector_bottom_cover_screw_d,
                m6_detector_bottom_cover_screw_head_d,m6_detector_bottom_cover_screw_head_depth);
    }
}
module laser_micro_bottom_gasket() {
    color("#dc9850") translate([0,0,m6_detector_shell_bottom_z+.08])
        linear_extrude(m6_detector_shell_gasket_height) difference() {
            offset(delta=m6_detector_shell_gasket_clearance+m6_detector_shell_gasket_width/2)
                lm_complete_footprint();
            offset(delta=-m6_detector_shell_gasket_width/2) lm_complete_footprint();
        }
}
module laser_micro_front_bolts() {
    color("silver") for(z=laser_micro_cover_screw_z) {
        lm_xcyl(3,30,laser_micro_front_screw_entry_x,laser_micro_front_screw_y,z);
        translate([laser_micro_front_screw_entry_x,laser_micro_front_screw_y,z])
            rotate([0,90,0]) cylinder(d1=6,d2=3,h=1.7,$fn=36);
    }
}
module laser_micro_front_nuts() {
    color("silver") for(z=laser_micro_cover_screw_z)
        translate([m6_detector_body_max_x-2.7,laser_micro_front_screw_y,z])
            rotate([0,90,0]) lm_hex(5.5,2.4,3);
}
module laser_micro_front_hardware() { laser_micro_front_bolts(); laser_micro_front_nuts(); }
module laser_micro_cover_containment() {
    // Parts must actually be inside the curved front cavity with 0.5 mm
    // clearance. A missing wall cannot make this test pass by itself.
    difference() {
        intersection() {
            union() {
                laser_micro_rail_positive();
                for(i=[0,4,m6_sensor_count-1])
                    translate([laser_micro_origin_x,0,m6_sensor_z(i)]) laser_micro_assembly(0);
            }
            translate([laser_micro_front_min_x-2,-50,m6_detector_shell_bottom_z-1])
                cube([m6_detector_shell_front_max_x-3-(laser_micro_front_min_x-2),100,m6_detector_shell_height_z+2]);
        }
        translate([0,0,m6_detector_shell_bottom_z+.5])
            linear_extrude(m6_detector_shell_height_z-laser_micro_front_wall-1)
                offset(delta=-.5) lm_front_inner_footprint();
    }
}
module laser_micro_service_labels() {
    for(i=[0:m6_sensor_count-1]) for(s=[-1,1]) {
        label=str(s>0 ? "A" : "B",i+1);
        roof=m6_detector_shell_top_z-m6_sensor_z(i)<m6_detector_shell_max_y;
        if(roof)
            translate([laser_micro_origin_x+laser_micro_lever+7,
                       s*(m6_detector_shell_top_z-m6_sensor_z(i)),
                       m6_detector_shell_top_z-.45])
                linear_extrude(.6) text(label,size=3,halign="center",valign="center",font="Liberation Sans:style=Bold");
        else
            translate([laser_micro_origin_x+laser_micro_lever+7,
                       s*(m6_detector_shell_max_y-.45),
                       m6_sensor_z(i)+m6_detector_shell_max_y])
                rotate([90,0,s>0 ? 180 : 0]) linear_extrude(.6)
                    text(label,size=3,halign="center",valign="center",font="Liberation Sans:style=Bold");
    }
}
module laser_micro_rear_cover() {
    // Side ports, plus two ports in the roof for channel 10. The structural
    // rear cover, its 1/4-20 boss and the ballhead stay bolted in place.
    difference() {
        m6_detector_shell_rear_positive(m6_detector_shell_alpha,laser_micro_cover_screw_z);
        laser_micro_service_passages();
        laser_micro_service_labels();
    }
}

// The real tool's tube is hollow so the AF1 key can prevent lock-tightening
// from turning the adjustment screw. This is a tool illustration, not an STL
// offered as a printed substitute for a metal socket.
module lm_service_tool(sign=laser_micro_service_sign,withdraw=laser_micro_service_withdraw) {
    lm_adjust_axis(sign) translate([0,0,withdraw]) {
        color("#62e4d1") difference() {
            translate([0,0,9.05]) cylinder(d=laser_micro_tool_d,h=laser_micro_tool_length,$fn=48);
            translate([0,0,9]) cylinder(d=4.15/cos(30),h=4.2,$fn=6);
            translate([0,0,9]) cylinder(d=2.6,h=laser_micro_tool_length+1,$fn=32);
        }
        color("#376d80") difference() {
            translate([0,0,9.05+laser_micro_tool_length])
                cylinder(d=laser_micro_tool_handle_d,h=laser_micro_tool_handle_length,$fn=48);
            translate([0,0,9+laser_micro_tool_length])
                cylinder(d=2.6,h=laser_micro_tool_handle_length+1,$fn=32);
        }
        color("#edbd66") translate([0,0,lm_tip(sign)+laser_micro_screw_length-1.25])
            cylinder(d=1/cos(30),h=laser_micro_tool_length+laser_micro_tool_handle_length+4,$fn=6);
    }
}
// Conservative swept solid: insertion/withdrawal and unrestricted rotation.
// Its intentional engagement with the addressed screw/locknut is excluded
// from this probe and checked with the hollow tool separately.
module lm_service_sweep(sign=laser_micro_service_sign) {
    lm_adjust_axis(sign) {
        translate([0,0,9.05]) cylinder(d=laser_micro_tool_d,h=laser_micro_tool_length+60,$fn=48);
        translate([0,0,9.05+laser_micro_tool_length])
            cylinder(d=laser_micro_tool_handle_d,h=laser_micro_tool_handle_length+60,$fn=48);
    }
}
module lm_service_obstacles(channel=laser_micro_service_channel,sign=laser_micro_service_sign) {
    translate([-laser_micro_origin_x,0,-m6_sensor_z(channel)]) {
        laser_micro_rail_positive();
        laser_micro_front_cover();
        laser_micro_rear_cover();
        laser_micro_bottom_cover();
        laser_micro_front_hardware();
        m6_detector_ballhead_positive();
    }
    // All neighbours remain installed, including their hardware.
    for(i=[0:m6_sensor_count-1]) translate([0,0,(i-channel)*m6_sensor_center_pitch]) {
        lm_frame(false); lm_frame(true);
        lm_moving() {
            lm_carrier(); lm_laser(); lm_retention_hardware();
            lm_rear_pusher_hardware();
        }
        lm_cap_hardware(); lm_mount_hardware();
        for(s=[-1,1]) {
            lm_adjust_nut(s);
            if(i!=channel || s!=sign) { lm_adjust_screw(s); lm_adjust_nut(s,true); }
        }
    }
}
module laser_micro_service_collision() {
    intersection() { lm_service_sweep(); lm_service_obstacles(); }
    // Thread and hex-drive engagement are explicit, so check the real tube
    // against the addressed screw/locknut as well as the other solids.
    intersection() {
        lm_service_tool();
        union() { lm_adjust_screw(laser_micro_service_sign); lm_adjust_nut(laser_micro_service_sign,true); }
    }
}

module laser_micro_metadata() {
    for(e=[0:.01:1]) {
        echo(str("LASER_MOTION ",e," ",lm_bench_motion(e)));
        echo(str("COVER_MOTION ",e," ",lm_cover_motion(e)));
    }
    echo(str("LASER_PARAM module_d=",laser_module_d));
    echo(str("LASER_PARAM module_length=",laser_module_length));
    echo(str("LASER_PARAM range_deg=",laser_micro_range_deg));
    echo(str("LASER_PARAM lever=",laser_micro_lever));
    echo(str("LASER_PARAM tail_d=",laser_micro_tail_d));
    echo(str("LASER_PARAM screw_pitch=",laser_micro_screw_pitch));
    echo(str("LASER_PARAM screw_d=",laser_micro_screw_d));
    echo(str("LASER_PARAM screw_length=",laser_micro_screw_length));
    echo(str("LASER_PARAM cap_screw_length=",laser_micro_cap_screw_length));
    echo(str("LASER_PARAM mount_screw_length=",laser_micro_mount_screw_length));
    echo(str("LASER_PARAM spring_wire=",laser_micro_spring_wire));
    echo(str("LASER_PARAM spring_radius=",laser_micro_spring_radius));
    echo(str("LASER_PARAM spring_turns=",laser_micro_spring_turns));
    echo(str("LASER_PARAM spring_free_height=",laser_micro_spring_free_height));
    echo(str("LASER_PARAM spring_floor=",laser_micro_spring_floor));
    echo(str("LASER_PARAM spring_pad=",laser_micro_spring_pad));
    echo(str("LASER_PARAM count=",m6_sensor_count));
    echo(str("LASER_PARAM pitch=",m6_sensor_center_pitch));
    echo(str("LASER_PARAM origin_x=",laser_micro_origin_x));
    echo(str("LASER_PARAM optical_bore_d=",m6_detector_optical_bore_d));
    echo(str("LASER_PARAM first_z=",m6_sensor_z(0)));
    echo(str("LASER_PARAM installed_offset_x=",m6_detector_mount_x_offset));
    echo(str("LASER_PARAM installed_offset_z=",m6_detector_mount_raise_z));
    echo(str("LASER_PARAM access_d=",laser_micro_access_d));
    echo(str("LASER_PARAM tool_d=",laser_micro_tool_d));
    echo(str("LASER_PARAM tool_clearance=",laser_micro_tool_clearance));
    echo(str("LASER_PARAM tool_length=",laser_micro_tool_length));
    echo(str("LASER_PARAM tool_handle_d=",laser_micro_tool_handle_d));
    echo(str("LASER_PARAM tool_handle_length=",laser_micro_tool_handle_length));
    echo(str("LASER_PARAM shell_top_z=",m6_detector_shell_top_z));
    echo(str("LASER_PARAM shell_half_y=",m6_detector_shell_max_y));
    echo(str("LASER_PARAM front_extra_depth=",laser_micro_front_extra_depth));
    echo(str("LASER_PARAM front_half_y=",laser_micro_front_half_y));
    echo(str("LASER_PARAM front_wall=",laser_micro_front_wall));
    echo(str("LASER_PARAM front_min_x=",laser_micro_front_min_x));
    echo(str("LASER_PARAM front_split_x=",m6_detector_shell_front_max_x));
    echo(str("LASER_PARAM front_guard_outer_d=",laser_micro_front_guard_outer_d));
    echo(str("LASER_PARAM front_guard_inner_d=",laser_micro_front_guard_inner_d));
    echo(str("LASER_PARAM front_guard_x=",laser_micro_front_guard_x));
    echo(str("LASER_PARAM front_guard_len=",laser_micro_front_guard_len));
    echo(str("LASER_PARAM front_guard_release=",laser_micro_front_guard_release));
    echo(str("LASER_PARAM rear_pusher_d=",laser_micro_rear_pusher_d));
    echo(str("LASER_PARAM rear_pusher_clearance=",laser_micro_rear_pusher_clearance));
    echo(str("LASER_PARAM rear_pusher_tap_d=",laser_micro_rear_pusher_tap_d));
    echo(str("LASER_PARAM rear_pusher_length=",laser_micro_rear_pusher_length));
    echo(str("LASER_PARAM rear_pusher_x=",laser_micro_rear_pusher_x));
    echo(str("LASER_PARAM rear_pusher_axis_y=",laser_micro_rear_pusher_axis_y));
    echo(str("LASER_PARAM rear_pusher_tip_setback=",laser_micro_rear_pusher_tip_setback));
    echo(str("LASER_PARAM rear_pusher_axis_z=",laser_micro_rear_pusher_axis_z));
    echo(str("LASER_PARAM rear_pusher_boss_x=",laser_micro_rear_pusher_boss_x));
    echo(str("LASER_PARAM rear_pusher_boss_len=",laser_micro_rear_pusher_boss_len));
    echo(str("LASER_PARAM rear_pusher_boss_width=",laser_micro_rear_pusher_boss_width));
    echo(str("LASER_PARAM rear_pusher_boss_height=",laser_micro_rear_pusher_boss_height));
    echo(str("LASER_PARAM rear_pusher_drive_af=",laser_micro_rear_pusher_drive_af));
    echo(str("LASER_PARAM rear_pusher_withdraw=",laser_micro_rear_pusher_withdraw));
}

// Rigid solid interference probe. The TPU liner and metal threaded interfaces
// intentionally use nominal preload/thread envelopes and are checked separately.
module laser_micro_collision() {
    if(laser_micro_collision_mode==0 || laser_micro_collision_mode==1) intersection() {
        lm_moving() lm_carrier();
        union() { lm_frame(false); lm_frame(true); }
    }
    if(laser_micro_collision_mode==0 || laser_micro_collision_mode==2)
        for(i=[0,4,m6_sensor_count-1]) intersection() {
            // Include projecting ears, screw heads and nuts, also at the end
            // channels next to the front-cover screw supports.
            laser_micro_assembly(0);
            translate([-laser_micro_origin_x,0,-m6_sensor_z(i)]) {
                laser_micro_rail_positive();
                laser_micro_front_cover();
                laser_micro_rear_cover();
                laser_micro_bottom_cover();
                laser_micro_front_hardware();
            }
        }
    // Adjacent moving tails, frame caps, screw tips and hardware envelopes.
    if(laser_micro_collision_mode==0 || laser_micro_collision_mode==3) intersection() {
        laser_micro_assembly(0);
        translate([0,0,m6_sensor_center_pitch]) laser_micro_assembly(0);
    }
}
