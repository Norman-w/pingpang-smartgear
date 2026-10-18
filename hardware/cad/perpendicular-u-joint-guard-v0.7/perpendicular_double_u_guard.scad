// Pingpang-SmartGear — one-piece double-U joint guard, v0.7
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

foot_bottom_z = -tube;
below_foot_extension_z = 1.0;
u_bottom = foot_bottom_z - below_foot_extension_z;
top_yoke_bottom_z = 21.0;       // 1 mm above the upper 20x20 tube top
top_yoke_thickness = 8.0;       // reinforced top connection beam
u_top = top_yoke_bottom_z + top_yoke_thickness;
roof_eave_extension_x = 12.0;   // roof overhang on each +X/-X side
roof_width_x = u_outer_width_x + 2 * roof_eave_extension_x;
hook_depth_x = 3.5; // thinner inward wrap; keep the 8 mm vertical hold
hook_height_z = 1.5; // retain only a thin 1-2 mm vertical inward lip
solid_upper_wall_bottom_z = 0.0; // upper wall/web ends at the foot's upper edge

// Preview-only context: show the complete lower foot rather than a clipped
// 20 mm joint slice.  This does not change the printable part.
preview_foot_length_y = 120.0;

// Vertical screw relief.  This is a clearance hole, never a printed thread;
// the actual M4/M5 screw and nut/tapped tube remain external hardware.
screw_clearance_d = 6.2;

// Full top nut envelope.  Use a round pocket so a hex nut can enter in any
// rotational orientation; the clearance is intentionally generous.
nut_pocket_d = 16.0;
nut_pocket_depth = 5.2;
nut_height = 4.0;
preview_nut_af = 8.0;

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

        // Solid upper web in the XZ U: fill the former open area below the
        // beam down to the top of the blue lower tube (z=0).  The web exists
        // only in the front/back U plates, so the lower foot still passes
        // through the 20 mm gap between them.
        box_at(0, yc,
               solid_upper_wall_bottom_z
                   + (u_top - solid_upper_wall_bottom_z) / 2,
               u_inner_width_x, depth,
               u_top - solid_upper_wall_bottom_z);

        // Inward lower hooks: the actual anti-rotation retaining feature.
        box_at(left_lip_x, yc, lip_z,
               hook_depth_x, depth, hook_height_z);
        box_at(right_lip_x, yc, lip_z,
               hook_depth_x, depth, hook_height_z);

    }
}

module printed_yokes() {
    // The top yoke joins the top bridges of both U plates into one roof.
    // It overhangs the U side walls by 12 mm on both sides along X.
    // The lower mouths remain open below z=0 so the front/back silhouettes
    // still retain the lower U feet and inward hooks.
    box_at(0, 0, u_top - top_yoke_thickness / 2,
           roof_width_x, 2 * front_y_outer, top_yoke_thickness);
}

module solid_upper_side_walls() {
    // Above the foot, the left and right sides are continuous solid walls
    // through the full front/back depth.  The front/back U plates also have
    // an upper web (inside u_plate) down to z=0.  The lower foot region remains
    // open except for the U arms and inward retaining hooks.
    left_x = -u_outer_width_x / 2 + wall / 2;
    right_x = u_outer_width_x / 2 - wall / 2;
    wall_height = u_top - solid_upper_wall_bottom_z;

    box_at(left_x, 0, solid_upper_wall_bottom_z + wall_height / 2,
           wall, 2 * front_y_outer, wall_height);
    box_at(right_x, 0, solid_upper_wall_bottom_z + wall_height / 2,
           wall, 2 * front_y_outer, wall_height);
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

    // Round pocket opens from the top face.  The remaining floor keeps the nut
    // captured while the round wall removes any rotational insertion constraint.
    translate([0, 0, u_top - nut_pocket_depth / 2])
        cylinder(d = nut_pocket_d,
                 h = nut_pocket_depth + 0.2,
                 center = true,
                 $fn = 64);
}

module double_u_clip() {
    difference() {
        union() {
            // Front U: inner face y=+10, outer face y=+21.
            u_plate(front_y_inner, front_y_outer);

            // Back U: inner face y=-10, outer face y=-21.
            u_plate(back_y_outer, back_y_inner);

            printed_yokes();
            solid_upper_side_walls();
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
    // Preview the complete lower foot along y.  The printable interface still
    // uses the exact 20 mm gap between the two U inner faces.
    color([0.28, 0.45, 0.78])
        difference() {
            translate([0, 0, -tube / 2])
                cube([tube, preview_foot_length_y, tube], center = true);
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
                cylinder(r = preview_nut_af / (2 * cos(30)) - 0.25,
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

