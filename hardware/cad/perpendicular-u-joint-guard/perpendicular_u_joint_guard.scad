// Pingpang-SmartGear — perpendicular 20x20 tube joint guard, v0.2
//
// Coordinate contract for this prototype:
//   x = barrier long direction
//   y = front/back direction
//   z = vertical direction
//
// The two context tubes are 20x20 and touch at z=0:
//   upper long tube: axis x, centre z=+10
//   lower cross tube: axis y, centre z=-10
//
// The printable parts are two separate U clips.  Their main U bodies sit on
// opposite y faces.  A male annular lap on the front clip enters a female
// annular socket on the back clip; the common screw clearance is on the y
// axis.  This is intentionally parameterized because the actual tube hole
// centre and the real M4/M5 hardware have not yet been measured.

$fn = 48;

PART = "joint_assembly";

// ---------- interface parameters ----------
tube = 20;
tube_clearance = 0.8;
u_inner_width = tube + tube_clearance;
wall = 4.0;
u_outer_width = u_inner_width + 2 * wall;

// The U is open toward the bottom and has small inward lips to retain the
// lower tube after the clip is placed over the joint.
u_bottom = -25;
u_top = 25;
hook_depth = 3.5;

// Front/back face plates.  Positive y is the front face.
plate_depth = 4.0;
front_y0 = 2.0;
front_y1 = front_y0 + plate_depth;
back_y0 = -front_y1;
back_y1 = -front_y0;

// Central lap: front male ring enters the back female socket.
male_lap_depth = 5.0;
male_od = 14.4;
female_od = 20.0;
female_id = 15.2;

// Central screw relief.  This is a clearance hole, not a printed thread.
screw_clearance_d = 6.2;
screw_counterbore_d = 10.8;
screw_counterbore_depth = 2.2;

// The central web joins the collar to both U arms and leaves a clear hole
// in the middle of the two-clips connection.
web_height = 8.0;
web_depth = plate_depth;

// ---------- small geometry helpers ----------
module box_at(xc, yc, zc, sx, sy, sz) {
    translate([xc, yc, zc]) cube([sx, sy, sz], center = true);
}

module annular_y(yc, length, outer_d, inner_d) {
    translate([0, yc, 0])
        difference() {
            rotate([90, 0, 0]) cylinder(d = outer_d, h = length, center = true);
            rotate([90, 0, 0]) cylinder(d = inner_d, h = length + 0.4, center = true);
        }
}

module u_body(y0, y1) {
    depth = y1 - y0;
    yc = (y0 + y1) / 2;
    left_x = -u_outer_width / 2 + wall / 2;
    right_x = u_outer_width / 2 - wall / 2;
    lip_z = u_bottom + wall / 2;
    left_lip_x = -u_outer_width / 2 + wall + hook_depth / 2;
    right_lip_x = u_outer_width / 2 - wall - hook_depth / 2;

    union() {
        // Top bridge and two long arms form the U profile.
        box_at(0, yc, u_top - wall / 2, u_outer_width, depth, wall);
        box_at(left_x, yc, (u_top + u_bottom) / 2, wall, depth, u_top - u_bottom);
        box_at(right_x, yc, (u_top + u_bottom) / 2, wall, depth, u_top - u_bottom);

        // Inward lower lips catch the lower 20x20 tube.
        box_at(left_lip_x, yc, lip_z, hook_depth, depth, wall);
        box_at(right_lip_x, yc, lip_z, hook_depth, depth, wall);

        // A short face web carries the screw collar without filling the U.
        box_at(0, yc, 0, u_outer_width, web_depth, web_height);
    }
}

module central_hole(y0, y1, outer_y, outward_sign) {
    // Main through-clearance hole along y.
    translate([0, (y0 + y1) / 2, 0])
        rotate([90, 0, 0])
            cylinder(d = screw_clearance_d, h = (y1 - y0) + 12, center = true);

    // Head relief is only opened from the outward face.  It remains a simple
    // circular pocket so it can be changed to a real head/nut capture later.
    translate([0, outer_y - outward_sign * screw_counterbore_depth / 2, 0])
        rotate([90, 0, 0])
            cylinder(d = screw_counterbore_d,
                     h = screw_counterbore_depth + 0.2,
                     center = true);
}

module u_clip(front = true) {
    if (front) {
        // Front U body: y=+2..+6.  The male annular tongue projects inward.
        difference() {
            union() {
                u_body(front_y0, front_y1);
                annular_y(front_y0 - male_lap_depth / 2,
                          male_lap_depth,
                          male_od,
                          screw_clearance_d);
            }
            central_hole(front_y0, front_y1, front_y1, 1);
        }
    } else {
        // Back U body: y=-6..-2.  The female socket receives the male ring.
        socket_y0 = back_y1 - 0.4;
        socket_y1 = socket_y0 + male_lap_depth + 0.4;
        difference() {
            union() {
                u_body(back_y0, back_y1);
                annular_y((socket_y0 + socket_y1) / 2,
                          socket_y1 - socket_y0,
                          female_od,
                          female_id);
            }
            central_hole(back_y0, back_y1, back_y0, -1);
        }
    }
}

// ---------- context geometry ----------
module upper_long_tube() {
    color([0.58, 0.61, 0.66])
        translate([0, 0, tube / 2])
            cube([120, tube, tube], center = true);
}

module lower_cross_tube() {
    color([0.28, 0.45, 0.78])
        translate([0, 0, -tube / 2])
            cube([tube, 90, tube], center = true);
}

module joint_bolt() {
    color([0.82, 0.82, 0.84])
        translate([0, 0, 0])
            rotate([90, 0, 0])
                cylinder(d = 5.0, h = 34, center = true);

    color([0.92, 0.70, 0.12])
        translate([0, 15, 0])
            rotate([90, 0, 0])
                cylinder(d = 10.0, h = 4.0, center = true);

    color([0.92, 0.70, 0.12])
        translate([0, -15, 0])
            rotate([90, 0, 0])
                cylinder(d = 10.0, h = 4.0, center = true, $fn = 6);
}

module joint_assembly(show_bolt = true) {
    upper_long_tube();
    lower_cross_tube();

    color([0.97, 0.45, 0.10]) u_clip(true);
    color([0.08, 0.62, 0.63]) u_clip(false);

    if (show_bolt) joint_bolt();
}

module joint_exploded() {
    // Exploded only in y so the two U profiles and their central male/female
    // lap can be inspected without hiding the real assembled relation.
    upper_long_tube();
    lower_cross_tube();
    translate([0, 7, 0]) color([0.97, 0.45, 0.10]) u_clip(true);
    translate([0, -7, 0]) color([0.08, 0.62, 0.63]) u_clip(false);
    joint_bolt();
}

module joint_section() {
    // Right half section exposes the central web, screw relief, and lap ring.
    intersection() {
        joint_assembly(false);
        translate([0, -100, -100]) cube([100, 200, 200]);
    }
    joint_bolt();
}

module print_front() {
    // Put the U face on the bed: x/y footprint, y-depth becomes print height.
    translate([0, 0, 3]) rotate([90, 0, 0]) u_clip(true);
}

module print_back() {
    translate([0, 0, 6]) rotate([90, 0, 0]) u_clip(false);
}

module print_layout() {
    translate([-23, 0, 0]) print_front();
    translate([23, 0, 0]) print_back();
}

// ---------- part selector ----------
if (PART == "front_u") {
    u_clip(true);
} else if (PART == "back_u") {
    u_clip(false);
} else if (PART == "front_u_print") {
    print_front();
} else if (PART == "back_u_print") {
    print_back();
} else if (PART == "joint_exploded") {
    joint_exploded();
} else if (PART == "joint_section") {
    joint_section();
} else if (PART == "print_layout") {
    print_layout();
} else {
    joint_assembly();
}

