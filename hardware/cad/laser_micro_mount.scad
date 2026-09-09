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
// The screw tip is the intersection of its radial axis with the rotated tail
// cylinder, computed exactly from distance to the cylinder's unit axis.
function lm_tip(sign,p=laser_micro_pitch_deg,y=laser_micro_yaw_deg) =
    let(a=[cos(p)*cos(y),cos(p)*sin(y),-sin(p)],
        n=[0,sign/sqrt(2),1/sqrt(2)],
        b=laser_micro_lever*a[0], c=n*a,
        aa=1-c*c, bb=-2*b*c,
        cc=laser_micro_lever*laser_micro_lever-b*b-
           pow(laser_micro_tail_d/2,2))
    (-bb+sqrt(bb*bb-4*aa*cc))/(2*aa);

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
    translate([laser_micro_lever,0,-7.6]) cylinder(d=3.6,h=3,$fn=32);
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
module lm_carrier() {
    difference() {
        union() {
            sphere(d=laser_micro_ball_d,$fn=64);
            lm_xcyl(laser_micro_tail_d,15,0);
            // Retention grub screw uses a captured metal nut, not PETG thread.
            translate([5,3,-3]) cube([4,4.8,6]);
        }
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
module lm_adjust_screw(sign=1) { lm_adjust_axis(sign) translate([0,0,lm_tip(sign)]) lm_grub(laser_micro_screw_length); }
module lm_adjust_nut(sign=1,lock=false) { lm_adjust_axis(sign) translate([0,0,lock ? 9 : 6.55]) lm_hex(); }
module lm_retention_hardware() {
    translate([7,5.55,0]) rotate([-90,0,0]) lm_hex();
    translate([7,laser_module_d/2,0]) rotate([-90,0,0]) lm_grub(5);
}
module lm_cap_hardware() {
    for(s=[-1,1]) {
        translate([0,s*10,-6]) cylinder(d=2,h=12,$fn=24);
        translate([0,s*10,6]) cylinder(d=3.8,h=2,$fn=32);
        translate([0,s*10,-7.25]) lm_hex();
    }
}
module lm_spring() {
    // Purchased OD3.2 wire0.4 spring; model length follows the moving flat pad.
    // The free length / rate must be selected after a real preload trial.
    h=3.1-laser_micro_lever*sin(laser_micro_pitch_deg);
    translate([laser_micro_lever,0,-7.4])
        for(i=[0:71]) hull() {
            for(j=[i,i+1]) translate([1.4*cos(j*15),1.4*sin(j*15),h*j/72]) sphere(d=.4,$fn=8);
        }
}
module lm_mount_hardware() {
    for(s=[-1,1]) {
        lm_xcyl(2.5,8,-4,s*laser_micro_mount_y);
        lm_xcyl(4.5,2.5,-6.5,s*laser_micro_mount_y);
        translate([3,s*laser_micro_mount_y,0]) rotate([0,90,0]) lm_hex(5,2,2.5);
    }
}
module laser_micro_assembly(e=laser_micro_explode) {
    color("#647d96") lm_frame(false);
    color("#86a9c4") translate([0,0,e*20]) lm_frame(true);
    color("#46cfb2") translate([0,0,-e*5]) lm_liner(false);
    color("#46cfb2") translate([0,0,e*14]) lm_liner(true);
    lm_moving() {
        color("#ec934b") translate([-e*14,-e*10,e*9]) lm_carrier();
        // Body withdraws toward +x from the carrier's rear; the small front
        // aperture is a physical stop, not a valid assembly path.
        color("#d4b567") translate([e*10,-e*10,e*9]) lm_laser();
        color("silver") translate([-e*14,-e*10,e*9]) lm_retention_hardware();
    }
    color("silver") {
        translate([0,0,e*20]) for(s=[-1,1]) { lm_adjust_screw(s); lm_adjust_nut(s); lm_adjust_nut(s,true); }
        translate([0,0,e*20]) lm_cap_hardware();
        lm_spring();
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
                    cube([5.2,10,7]);
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
module laser_micro_front_hardware() {
    color("silver") for(z=laser_micro_cover_screw_z) {
        lm_xcyl(3,30,laser_micro_front_screw_entry_x,laser_micro_front_screw_y,z);
        translate([laser_micro_front_screw_entry_x,laser_micro_front_screw_y,z])
            rotate([0,90,0]) cylinder(d1=6,d2=3,h=1.7,$fn=36);
        translate([m6_detector_body_max_x-2.7,laser_micro_front_screw_y,z])
            rotate([0,90,0]) lm_hex(5.5,2.4,3);
    }
}
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
        lm_moving() { lm_carrier(); lm_laser(); lm_retention_hardware(); }
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
    echo(str("LASER_PARAM module_d=",laser_module_d));
    echo(str("LASER_PARAM module_length=",laser_module_length));
    echo(str("LASER_PARAM range_deg=",laser_micro_range_deg));
    echo(str("LASER_PARAM lever=",laser_micro_lever));
    echo(str("LASER_PARAM tail_d=",laser_micro_tail_d));
    echo(str("LASER_PARAM screw_pitch=",laser_micro_screw_pitch));
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
