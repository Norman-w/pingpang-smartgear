// Matching RX enclosure for the bare-laser assembly. Units: mm.
// The receiver electronics are still the existing M6 geometry reference;
// this does not establish compatibility with the bare visible-light laser.
// PETG covers/carrier, TPU bottom pad; front cap enters along raw x+.
module receiver_rail_positive() {
    difference() {
        m6_detector_body_positive(laser_micro_cover_screw_z);
        lm_front_mount_clearances();
    }
}
module receiver_rear_cover() {
    m6_detector_shell_rear_positive(1,laser_micro_cover_screw_z);
}
module receiver_cover_set() {
    laser_micro_front_cover();
    receiver_rear_cover();
    laser_micro_bottom_cover();
    laser_micro_bottom_gasket();
    laser_micro_front_hardware();
}
module receiver_internal_positive() {
    receiver_rail_positive();
    m6_detector_sensor_array_positive();
    m6_receiver_carrier_board_raw_positive();
}
module receiver_mount_positive() {
    receiver_internal_positive();
    if(m6_detector_show_shell) {
        receiver_cover_set();
        m6_detector_cable_gland_positive();
    }
    // The old blue cable-clearance probe is a diagnostic envelope, not a
    // physical component. Keep it out of the closed enclosure assembly.
    m6_detector_ballhead_positive();
}
module receiver_detector_positive() {
    translate([m6_detector_mount_x_offset,0,m6_detector_mount_raise_z])
        receiver_mount_positive();
}
module receiver_cover_containment() {
    difference() {
        intersection() {
            receiver_internal_positive();
            translate([laser_micro_front_min_x-2,-50,m6_detector_shell_bottom_z-1])
                cube([m6_detector_shell_front_max_x-3-(laser_micro_front_min_x-2),100,m6_detector_shell_height_z+2]);
        }
        translate([0,0,m6_detector_shell_bottom_z+.5])
            linear_extrude(m6_detector_shell_height_z-laser_micro_front_wall-1)
                offset(delta=-.5) lm_front_inner_footprint();
    }
}
module receiver_cover_collision() {
    intersection() {
        receiver_internal_positive();
        union() {laser_micro_front_cover();receiver_rear_cover();laser_micro_bottom_cover();}
    }
    intersection() {
        laser_micro_front_hardware();
        union(){m6_detector_sensor_array_positive();m6_receiver_carrier_board_raw_positive();}
    }
}
