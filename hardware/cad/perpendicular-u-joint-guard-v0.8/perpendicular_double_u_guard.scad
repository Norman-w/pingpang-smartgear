// Pingpang-SmartGear — one-piece double-U joint guard, v0.8
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
//
// v0.8 annotation interpretation:
//   red  = the upper left/right side regions are solid walls;
//   green = add material at the upper front-to-back shoulder/overlap region,
//           without making downward-facing wings or reducing the 20 mm tube
//           passage.

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
front_back_extension_y = 4.0;  // complete U plate front-to-back extension
plate_depth_y = base_plate_depth_y + front_back_extension_y;
front_y_outer = front_y_inner + plate_depth_y;
back_y_outer = -front_y_outer;
back_y_inner = -front_y_inner;

foot_bottom_z = -tube;
below_foot_extension_z = 1.0;
u_bottom = foot_bottom_z - below_foot_extension_z;
top_yoke_bottom_z = 21.0;       // 1 mm above the upper 20x20 tube top
top_yoke_thickness = 8.0;       // keep the v0.7 top height/clearance
u_top = top_yoke_bottom_z + top_yoke_thickness;
hook_depth_x = 6.5;
hook_height_z = 8.0;            // vertical抱脚 contact above the foot bottom
solid_upper_wall_bottom_z = 0.0;

// ---------- red solid wall and green reinforcement ----------
// These walls keep their inner faces at +/-10.4 mm, so the 20 mm tube gap is
// not reduced.  The extra 2 mm is added only toward the outside.
solid_side_wall_thickness = 7.0;
top_yoke_width_x = u_inner_width_x + 2 * solid_side_wall_thickness;

// The green shoulder extends only toward the outside in x and front/back in y.
// It occupies the upper side-wall region z=0..21; it does not extend downward
// into the foot or the lower retaining-hook opening.
reinforcement_outset_x = 4.0;
reinforcement_front_back_extension_y = 6.0;
reinforcement_bottom_z = 0.0;
reinforcement_top_z = top_yoke_bottom_z;

// Preview-only context: show the complete lower foot rather than a clipped
// 20 mm joint slice.  This does not change the printable part.
preview_foot_length_y = 120.0;

// The axial screw passage is a true through-hole in the printed piece.  This
// is clearance only; no printed thread is modeled.
screw_clearance_d = 6.2;

// Full top nut envelope.  Use a round pocket so a hex nut can enter in any
// rotational orientation; the central screw passage remains through.
nut_pocket_d = 16.0;
nut_pocket_depth = 5.2;
nut_height = 4.0;
preview_nut_af = 8.0;

assert(u_inner_distance_y == 20, "双 U 内距离必须保持 20 mm");
assert(reinforcement_bottom_z >= foot_bottom_z, "加强体不能低于脚底限位");

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
    // The top yoke joins both U plates into one roof.  It is wider than the
    // nominal U top only toward the outside, reinforcing the top shoulders.
    box_at(0, 0, u_top - top_yoke_thickness / 2,
           top_yoke_width_x, 2 * front_y_outer, top_yoke_thickness);
}

module red_solid_upper_side_walls() {
    // Red-marked region: from the upper tube level down to z=0, both side
    // walls are solid across the complete front/back U depth.  The lower foot
    // remains open except for the U arms and inward retaining hooks.
    left_x = -u_inner_width_x / 2 - solid_side_wall_thickness / 2;
    right_x = u_inner_width_x / 2 + solid_side_wall_thickness / 2;
    wall_height = u_top - solid_upper_wall_bottom_z;

    box_at(left_x, 0, solid_upper_wall_bottom_z + wall_height / 2,
           solid_side_wall_thickness, 2 * front_y_outer, wall_height);
    box_at(right_x, 0, solid_upper_wall_bottom_z + wall_height / 2,
           solid_side_wall_thickness, 2 * front_y_outer, wall_height);
}

module green_reinforcement_shoulders() {
    // Green-marked region: two continuous upper side-wall reinforcement bands
    // running from the front U to the back U.  They are rectangular solid
    // additions, not four end blocks and not downward-sloping ribs.  They
    // reinforce the full front-to-back overlap while leaving lower hooks open.
    x_inner = u_inner_width_x / 2;
    x_outer = u_outer_width_x / 2 + reinforcement_outset_x;
    y_front_outer_plus = front_y_outer + reinforcement_front_back_extension_y;
    y_back_outer_minus = back_y_outer - reinforcement_front_back_extension_y;
    shoulder_depth = y_front_outer_plus - y_back_outer_minus;
    shoulder_height = reinforcement_top_z - reinforcement_bottom_z;

    right_x = (x_inner + x_outer) / 2;
    left_x = (-x_inner - x_outer) / 2;
    zc = (reinforcement_bottom_z + reinforcement_top_z) / 2;

    for (xc = [left_x, right_x]) {
        box_at(xc, 0, zc,
               x_outer - x_inner, shoulder_depth, shoulder_height);
    }
}

module vertical_screw_relief() {
    // TRUE THROUGH-HOLE: the small central cylinder runs from below u_bottom
    // to above u_top.  The lower-entering screw therefore cannot be blocked
    // by either the red solid walls or the green gussets.
    translate([0, 0, (u_bottom + u_top) / 2])
        cylinder(d = screw_clearance_d,
                 h = (u_top - u_bottom) + 8,
                 center = true);

    // Round pocket opens from the top face.  Its floor remains around the
    // through-hole so the nut is captured below the top surface.
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
            red_solid_upper_side_walls();
            green_reinforcement_shoulders();
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

module base_clip_for_marked_preview() {
    // Diagnostic-only base: the red and green additions are rendered
    // separately below so the annotation mapping can be inspected.
    difference() {
        union() {
            u_plate(front_y_inner, front_y_outer);
            u_plate(back_y_outer, back_y_inner);
            printed_yokes();
        }
        vertical_screw_relief();
    }
}

module assembly_marked() {
    upper_long_tube();
    lower_cross_tube();
    color([0.96, 0.39, 0.08]) base_clip_for_marked_preview();
    color([0.95, 0.12, 0.08]) red_solid_upper_side_walls();
    color([0.22, 0.78, 0.24]) green_reinforcement_shoulders();
    vertical_joint_screw();
}

module assembly_section() {
    // Cut the positive-x half to expose the vertical through-hole and the
    // 20 mm gap without hiding the foot.
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
} else if (PART == "assembly_marked") {
    assembly_marked();
} else if (PART == "clip_front") {
    clip_front();
} else if (PART == "clip_bottom") {
    clip_bottom();
} else if (PART == "clip_top") {
    clip_top();
} else {
    assembly_iso();
}
