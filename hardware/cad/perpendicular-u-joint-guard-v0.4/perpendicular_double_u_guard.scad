// Pingpang-SmartGear — one-piece double-U joint guard, v0.4
//
// Mechanical contract for this correction:
//   x = barrier long direction
//   y = front/back direction
//   z = vertical direction
//
// The printed part is ONE solid.  It contains a front U and a back U, joined
// by one printed top yoke.  The clear distance between the two U inner faces
// is exactly 20 mm.  There is no male/female printed connection and no second
// printed part to bolt together.
//
// The context tubes are the local joint envelope:
//   upper long 20x20 tube: axis x, z=0..20
//   lower perpendicular 20x20 tube: axis y, z=-20..0
// They touch at z=0 and share a vertical screw axis through their centre.

$fn = 48;

PART = "assembly_iso";

// ---------- fixed interface dimensions ----------
tube = 20;
u_inner_distance_y = 20;       // hard requirement: inner face to inner face
u_clearance_x = 0.8;           // only the x direction has initial PETG relief
u_inner_width_x = tube + u_clearance_x;
wall = 5.0;
u_outer_width_x = u_inner_width_x + 2 * wall;

front_y_inner = u_inner_distance_y / 2;
base_plate_depth_y = 7.0;
front_back_extension_y = 4.0;  // extend the complete U plate front-to-back
plate_depth_y = base_plate_depth_y + front_back_extension_y;
front_y_outer = front_y_inner + plate_depth_y;
back_y_outer = -front_y_outer;
back_y_inner = -front_y_inner;

u_bottom = -28;
u_top = 27;
top_yoke_thickness = 6.0;
hook_depth_x = 6.5;
hook_height_z = 8.0;

// Vertical screw relief.  This is a clearance hole, never a printed thread;
// the actual M4/M5 screw and nut/tapped tube remain external hardware.
screw_clearance_d = 6.2;

// Full top nut envelope.  The socket is intentionally larger than an M5 AF8
// nut and deeper than a typical 4 mm nut, so the nut cannot touch the top
// surface when the screw is tightened.
nut_pocket_af = 12.0;
nut_pocket_depth = 5.2;
nut_height = 4.0;

assert(u_inner_distance_y == 20, "双 U 内距离必须保持 20 mm");

// ---------- helpers ----------
module box_at(xc, yc, zc, sx, sy, sz) {
    translate([xc, yc, zc]) cube([sx, sy, sz], center = true);
}

module u_plate(y0, y1) {
    depth = y1 - y0;
    yc = (y0 + y1) / 2;
    left_x = -u_outer_width_x / 2 + wall / 2;
    right_x = u_outer_width_x / 2 - wall / 2;
    lip_z = u_bottom + hook_height_z / 2;
    left_lip_x = -u_outer_width_x / 2 + wall / 2 + hook_depth_x / 2;
    right_lip_x = u_outer_width_x / 2 - wall / 2 - hook_depth_x / 2;
    union() {
        // U top and two continuous arms.
        box_at(0, yc, u_top - top_yoke_thickness / 2,
               u_outer_width_x, depth, top_yoke_thickness);
        box_at(left_x, yc, (u_top + u_bottom) / 2,
               wall, depth, u_top - u_bottom);
        box_at(right_x, yc, (u_top + u_bottom) / 2,
               wall, depth, u_top - u_bottom);

        // Inward lower hooks: the actual anti-rotation retaining feature.
        box_at(left_lip_x, yc, lip_z,
               hook_depth_x, depth, hook_height_z);
        box_at(right_lip_x, yc, lip_z,
               hook_depth_x, depth, hook_height_z);

    }
}

module printed_yokes() {
    // The top yoke joins the top bridges of both U plates into one roof.
    // The lower mouths remain open so the front/back silhouettes stay U-shaped.
    box_at(0, 0, u_top - top_yoke_thickness / 2,
           u_outer_width_x, 2 * front_y_outer, top_yoke_thickness);
}

module vertical_screw_relief() {
    // Full z-axis clearance through the printed top yoke.  There is no printed
    // material in the middle gap, so this does not create a hidden horizontal
    // tunnel or a self-intersecting connector.  The screw approaches from
    // below, passes through the two tube sections, and exits this top yoke.
    translate([0, 0, (u_bottom + u_top) / 2])
        cylinder(d = screw_clearance_d,
                 h = (u_top - u_bottom) + 8,
                 center = true);

    // Hexagonal pocket opens from the top face.  Across-flats clearance is
    // deliberately generous; the remaining floor keeps the nut captured.
    translate([0, 0, u_top - nut_pocket_depth / 2])
        rotate([0, 0, 30])
            cylinder(r = nut_pocket_af / (2 * cos(30)),
                     h = nut_pocket_depth + 0.2,
                     center = true,
                     $fn = 6);
}

module double_u_clip() {
    difference() {
        union() {
            // Front U: inner face y=+10, outer face y=+21.
            u_plate(front_y_inner, front_y_outer);

            // Back U: inner face y=-10, outer face y=-21.
            u_plate(back_y_outer, back_y_inner);

            printed_yokes();
        }
        vertical_screw_relief();
    }
}

// ---------- context envelope for preview only ----------
module vertical_bore() {
    translate([0, 0, 0])
        cylinder(d = screw_clearance_d, h = 60, center = true);
}

module upper_long_tube() {
    color([0.58, 0.61, 0.66])
        difference() {
            translate([0, 0, tube / 2])
                cube([120, tube, tube], center = true);
            vertical_bore();
        }
}

module lower_cross_tube() {
    // This is the local 20 mm joint section between the two U inner faces.
    color([0.28, 0.45, 0.78])
        difference() {
            translate([0, 0, -tube / 2])
                cube([tube, u_inner_distance_y, tube], center = true);
            vertical_bore();
        }
}

module vertical_joint_screw() {
    color([0.82, 0.82, 0.84])
        translate([0, 0, 0])
            cylinder(d = 5.0, h = 62, center = true);

    // Screw head below the lower yoke.
    color([0.92, 0.70, 0.12])
        translate([0, 0, u_bottom - 4])
            cylinder(d = 10.0, h = 4.0, center = true);

    // The nut sits inside the recessed top pocket, below the top surface.
    color([0.92, 0.70, 0.12])
        translate([0, 0, u_top - nut_pocket_depth + nut_height / 2])
            rotate([0, 0, 30])
                cylinder(r = nut_pocket_af / (2 * cos(30)) - 0.25,
                         h = nut_height,
                         center = true,
                         $fn = 6);
}

module assembly_iso() {
    upper_long_tube();
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) double_u_clip();
    vertical_joint_screw();
}

module assembly_section() {
    // Cut the positive-x half to expose the vertical hole and the 20 mm gap.
    intersection() {
        assembly_iso();
        translate([0, -100, -100]) cube([100, 200, 200]);
    }
}

module clip_front() {
    double_u_clip();
}

module clip_bottom() {
    double_u_clip();
}

module clip_top() {
    double_u_clip();
}

module clip_print_orientation() {
    // One-piece print orientation.  The y envelope is placed on z=0.
    translate([0, 0, front_y_outer])
        rotate([90, 0, 0]) double_u_clip();
}

if (PART == "clip") {
    double_u_clip();
} else if (PART == "clip_print_orientation") {
    clip_print_orientation();
} else if (PART == "assembly_section") {
    assembly_section();
} else if (PART == "clip_front") {
    clip_front();
} else if (PART == "clip_bottom") {
    clip_bottom();
} else if (PART == "clip_top") {
    clip_top();
} else {
    assembly_iso();
}

