// 乒乓智配：球网立柱 X 型夹具与过网高度导轨
// 单一参数源。单位：mm。
//
// 预览/导出：
//   PART="assembly"    双侧装配预览
//   PART="left_clamp"  左侧夹具
//   PART="right_clamp" 右侧夹具
//   PART="arm"         活动臂
//   PART="roller"      竖直滚柱与压盖
//   PART="knob"        M8 旋钮/螺杆占位
//   PART="rod"          方杆
//   PART="bridge"       固定桥件
//   PART="guide"        连续光栅导轨
//   PART="calibration_gauge"  打印式光栅/参考线标定规
//   PART="parameter_probe"    输出几何验证所需的单一参数源
//   SIDE=0               按 PART 的默认左右方向
//   SIDE=1/-1            显式覆盖单夹具镜像选择
//
// 重要：螺纹、金属光轴、滚柱、软垫为装配占位几何；打印前要按实际
// 标准件、打印方向和 PETG 收缩率修订孔径与间隙。

$fn = 48;

PART = "assembly";
SIDE = 0;

// 立柱与夹持参数
post_nominal_d = 25;
post_radius = post_nominal_d / 2;
v_angle = 90;
jaw_clearance = 1.2;
soft_pad_t = 2.0;
jaw_length = 26;
jaw_width = 9;
jaw_height = 7;
jaw_mount_overlap = 2;

// X 臂/转轴参数
arm_length_outer = 90;
arm_length_inner = 60;
arm_outer_y = 24;
arm_inner_y = 16;
// 夹具运动参数：两根 X 臂绕中心轴同步转动。
// 外侧旋钮顶开滚柱时提高该角度，内侧 V 槽随同一角度移动。
clamp_angle_deg = 15;
clamp_angle_min_deg = 10;
clamp_angle_max_deg = 20;
arm_width = 14;
// The top view is a true X, but the two printable arms occupy separate
// vertical layers around the same Ø8 pivot.  arm_height is the complete
// stack envelope, not the thickness of one arm.
arm_height = 16;
arm_layer_thickness = 7;
arm_layer_gap = 2;
arm_lower_z = 0;
arm_upper_z = arm_layer_thickness + arm_layer_gap;
pivot_d = 8;
pivot_clearance = 0.35;
pivot_head_d = 16;
pivot_lock_t = 4;
arm_limit_d = 5;

// 外侧滚柱、螺杆与旋钮
roller_d = 16;
roller_h = 18;
roller_axis_d = 6;
screw_d = 8;
screw_pitch = 1.25;
screw_span = 82;
knob_d = 40;
knob_t = 14;
knob_grip_count = 12;

// 延长杆、导轨、参考线
rod_w = 12;
rod_h = 12;
rod_len = 130;
bridge_len = 58;
bridge_width = 34;
bridge_h = 10;
bridge_z = arm_height + 18;
guide_t = 5;
guide_width = 24;
beam_count = 10;
beam_first_height = 10;
beam_pitch = 10;
beam_last_height = beam_first_height + (beam_count - 1) * beam_pitch;
reference_height = 50;
reference_line_d = 1.5;
locating_hole_d = 4;

// 双侧预览间距（不是球桌最终规格）
assembly_span = 700;

assert(post_nominal_d > 0, "post_nominal_d must be positive");
assert(post_radius == post_nominal_d / 2,
       "post radius must stay derived from the nominal post diameter");
assert(v_angle == 90, "first prototype uses a 90 degree V jaw");
assert(pivot_d == 8, "first prototype uses an 8 mm metal pivot shaft");
assert(screw_d == 8, "first prototype uses an M8 screw");
assert(screw_pitch == 1.25, "first prototype uses an M8 x 1.25 screw");
assert(beam_count == 10, "first prototype uses 10 optical channels");
assert(beam_first_height == 10, "first effective beam starts at +10 mm");
assert(beam_last_height == 100, "first prototype ends at +100 mm");
assert(rod_w == 12 && rod_h == 12 && rod_len == 130, "first rod is 12 x 12 x 130 mm");
assert(SIDE == -1 || SIDE == 0 || SIDE == 1, "SIDE must be -1, 0, or 1");
assert(2 * arm_layer_thickness + arm_layer_gap == arm_height,
       "scissor arms must fit in the declared vertical stack");
assert(jaw_height <= arm_layer_thickness,
       "V jaw thickness must fit the arm layer");
assert(clamp_angle_deg >= clamp_angle_min_deg && clamp_angle_deg <= clamp_angle_max_deg,
       "clamp angle must stay inside the printable motion range");
assert(clamp_angle_min_deg > 0 && clamp_angle_max_deg < 30,
       "motion range must leave a stable X crossing");
assert(jaw_mount_overlap > 0 && jaw_mount_overlap < jaw_length / 2,
       "V jaw must overlap the arm endpoint without crossing its full length");

function point_x(p) = p[0];
function point_y(p) = p[1];
function segment_length(p1, p2) = sqrt(pow(point_x(p2) - point_x(p1), 2) + pow(point_y(p2) - point_y(p1), 2));
function segment_angle(p1, p2) = atan2(point_y(p2) - point_y(p1), point_x(p2) - point_x(p1));
function cross_2d(p1, p2) = point_x(p1) * point_y(p2) - point_y(p1) * point_x(p2);
function distance_2d(p1, p2) = sqrt(pow(point_x(p2) - point_x(p1), 2) + pow(point_y(p2) - point_y(p1), 2));
function post_x() = arm_length_inner + 5;
function outer_radius() = sqrt(pow(arm_length_outer, 2) + pow(arm_outer_y, 2));
function inner_radius() = sqrt(pow(arm_length_inner, 2) + pow(arm_inner_y, 2));
function outer_point(sign = 1) = [-outer_radius() * cos(clamp_angle_deg), sign * outer_radius() * sin(clamp_angle_deg)];
function inner_point(sign = 1) = [inner_radius() * cos(clamp_angle_deg), -sign * inner_radius() * sin(clamp_angle_deg)];
function jaw_to_post_gap() = distance_2d(inner_point(1), [post_x(), 0]);
function bridge_rod_x() = post_x() + 4;
function guide_x() = bridge_rod_x() + rod_w / 2 + guide_t / 2 + 2;
function beam_z(h) = bridge_z + h;
function screw_tip_y() = outer_point(1)[1] + roller_d / 2;

// 这些断言验证 X 线、内端夹持距离和外侧螺杆包络，而不是只验证语法。
assert(abs(cross_2d(outer_point(1), inner_point(1))) < 0.01,
       "upper scissor arm must pass through the pivot");
assert(abs(cross_2d(outer_point(-1), inner_point(-1))) < 0.01,
       "lower scissor arm must pass through the pivot");
assert(jaw_to_post_gap() + jaw_clearance < jaw_length,
       "inner V jaw must reach the nominal post with clearance margin");
assert(screw_span / 2 >= outer_radius() * sin(clamp_angle_deg) + roller_d / 2,
       "M8 screw span must cover both outer rollers");
assert(reference_height >= beam_first_height && reference_height <= beam_last_height &&
           (reference_height - beam_first_height) % beam_pitch == 0,
       "reference line must land on a 10 mm optical detent");
assert(locating_hole_d > 0 && locating_hole_d < guide_width,
       "locating holes must pass through the optical guide");

module beam_between_2d(p1, p2, width, height, z0 = 0) {
    translate([(point_x(p1) + point_x(p2)) / 2,
               (point_y(p1) + point_y(p2)) / 2,
               z0 + height / 2])
        rotate([0, 0, segment_angle(p1, p2)])
            cube([segment_length(p1, p2), width, height], center = true);
}

module vertical_cylinder_at(p, d, h, z0 = 0) {
    translate([point_x(p), point_y(p), z0])
        cylinder(d = d, h = h);
}

module metal_pivot_shaft() {
    color("silver")
        translate([0, 0, -pivot_lock_t])
            cylinder(d = pivot_d, h = arm_height + bridge_z + rod_len / 5 + pivot_lock_t * 2);
    color("dimgray") {
        translate([0, 0, -pivot_lock_t]) cylinder(d = pivot_head_d, h = pivot_lock_t);
        translate([0, 0, arm_height]) cylinder(d = pivot_head_d, h = pivot_lock_t);
    }
}

module scissor_arm(p1, p2, z0 = 0, label = "arm") {
    color("darkorange") {
        difference() {
            union() {
                beam_between_2d(p1, p2, arm_width, arm_layer_thickness, z0);
                // 中心局部加厚，表示箱型截面/三角肋区域。
                translate([0, 0, z0 + arm_layer_thickness / 2])
                    cylinder(d = arm_width + 8,
                             h = arm_layer_thickness,
                             center = true);
            }
            // Ø8 金属光轴的打印间隙孔；光轴由装配件穿过两根活动臂。
            translate([0, 0, z0 - 1])
                cylinder(d = pivot_d + pivot_clearance * 2,
                         h = arm_layer_thickness + 2);
        }
    }
    // 小型限位柱，首样用于限制过开和过夹。
    color("dimgray")
        translate([point_x(p2), point_y(p2), z0 + arm_layer_thickness])
            cylinder(d = arm_limit_d, h = 5);
}

module v_jaw(center, opening_angle = 0, z0 = 0) {
    // 两根 45 度肋形成 90 度 V 槽；V 的尖端朝向 center。
    color("orange")
        translate([point_x(center), point_y(center), z0 + arm_layer_thickness / 2])
            rotate([0, 0, opening_angle]) {
                for (a = [-45, 45])
                    rotate([0, 0, a])
                        // Start slightly behind the arm endpoint so the V jaw
                        // is an attached solid in the exported clamp, not a
                        // merely touching/free-floating body.
                        translate([jaw_length / 2 - jaw_mount_overlap, 0, 0])
                            cube([jaw_length, jaw_width, jaw_height], center = true);
            }

    // 可替换 TPU/硅胶软垫占位，颜色只用于装配预览。
    color("deepskyblue")
        translate([point_x(center), point_y(center), z0 + arm_layer_thickness / 2])
            rotate([0, 0, opening_angle])
                for (a = [-45, 45])
                    rotate([0, 0, a])
                        translate([jaw_length / 2 - soft_pad_t, 0, 0])
                            cube([soft_pad_t, jaw_width + 1, jaw_height - 4], center = true);
}

module dimpled_vertical_roller(p, has_dimple = false, z0 = 0) {
    color("silver")
        if (has_dimple)
            difference() {
                vertical_cylinder_at(p, roller_d, roller_h,
                                     z0 + arm_layer_thickness / 2 - roller_h / 2);
                // 圆坑在滚柱的外侧圆周面，承接沿 Y 方向来的螺杆圆头；
                // 不把顶面凹坑误当成水平推力承接面。
                translate([point_x(p), point_y(p) + roller_d / 2,
                           z0 + arm_layer_thickness / 2])
                    sphere(d = 6);
            }
        else
            vertical_cylinder_at(p, roller_d, roller_h,
                                 z0 + arm_layer_thickness / 2 - roller_h / 2);

    color("dimgray")
        vertical_cylinder_at(p, roller_axis_d, roller_h + 4,
                             z0 + arm_layer_thickness / 2 - roller_h / 2 - 2);
}

module removable_roller_cap(p, z0 = 0) {
    color("lightgray")
        translate([point_x(p), point_y(p),
                   z0 + arm_layer_thickness / 2 + roller_h / 2 + 1])
            cube([roller_d + 8, roller_d + 8, 3], center = true);
}

module u_roller_mount(p, has_dimple = false, z0 = 0) {
    // 两侧 cheek 代表可打印 U 槽，压盖单独显示以便检查防脱空间。
    color("darkorange") {
        translate([point_x(p), point_y(p) - (roller_d + 6) / 2,
                   z0 + arm_layer_thickness / 2])
            cube([roller_d + 12, 4, roller_h + 8], center = true);
        translate([point_x(p), point_y(p) + (roller_d + 6) / 2,
                   z0 + arm_layer_thickness / 2])
            cube([roller_d + 12, 4, roller_h + 8], center = true);
    }
    dimpled_vertical_roller(p, has_dimple, z0);
    removable_roller_cap(p, z0);
    if (!has_dimple)
        m8_nut_capture(p, z0);
}

module m8_nut_capture(p, z0 = 0) {
    // 下侧 U 槽捕获金属 M8 螺母；六边形仅表示标准件包络，实际螺纹由
    // 金属螺母/螺杆提供，不把打印件当成受力螺纹。
    color("dimgray")
        translate([point_x(p), point_y(p) - roller_d / 2 - 3,
                   z0 + arm_layer_thickness / 2])
            rotate([90, 0, 0])
                cylinder(d = 15, h = 6, center = true, $fn = 6);
}

module rounded_screw_rod() {
    // 横向 M8×1.25 金属螺杆占位；真实螺纹由标准件提供。
    color("silver")
        translate([outer_point(1)[0], 0, arm_height / 2])
            rotate([90, 0, 0])
                cylinder(d = screw_d, h = screw_span, center = true);
    color("silver")
        translate([outer_point(1)[0], screw_tip_y(), arm_height / 2])
            sphere(d = screw_d + 2);
}

module printed_knob() {
    color("firebrick")
        translate([outer_point(1)[0], -screw_span / 2 - knob_t / 2 + 2, arm_height / 2])
            rotate([90, 0, 0])
                difference() {
                    cylinder(d = knob_d, h = knob_t, center = true);
                    cylinder(d = screw_d + 1, h = knob_t + 2, center = true);
                    for (i = [0 : knob_grip_count - 1])
                        rotate([0, 0, i * 360 / knob_grip_count])
                            translate([knob_d / 2 - 2, 0, 0])
                                cube([4, 5, knob_t + 2], center = true);
                }
}

module fixed_bridge() {
    color("darkorange")
        translate([bridge_rod_x(), 0, bridge_z])
            cube([bridge_len, bridge_width, bridge_h], center = true);
    color("dimgray")
        translate([bridge_rod_x(), 0, bridge_z + bridge_h / 2])
            cylinder(d = pivot_d + 2, h = bridge_h + 4, center = true);
}

module square_extension_rod() {
    color("gold")
        translate([bridge_rod_x(), -rod_w / 2, bridge_z + bridge_h / 2])
            cube([rod_w, rod_h, rod_len]);
}

module optical_guide() {
    color("slateblue")
        difference() {
            translate([guide_x(), -guide_width / 2, bridge_z + bridge_h / 2])
                cube([guide_t, guide_width, rod_len]);

            // These are real through-holes for the spring detent, not
            // positive cylinders that would accidentally print as posts.
            for (i = [0 : beam_count - 1]) {
                h = beam_first_height + i * beam_pitch;
                translate([guide_x() + guide_t / 2, 0, beam_z(h)])
                    rotate([90, 0, 0])
                        cylinder(d = locating_hole_d,
                                 h = guide_width + 4,
                                 center = true);
            }
        }

    // 每个光束高度的横向参考标记与定位孔。
    for (i = [0 : beam_count - 1]) {
        h = beam_first_height + i * beam_pitch;
        color("white")
            translate([guide_x() - 1, -guide_width / 2 - 4, beam_z(h)])
                cube([guide_t + 2, guide_width + 8, 1.5], center = true);
    }
}

module reference_line_carriage() {
    h = reference_height;
    color("limegreen")
        difference() {
            translate([guide_x() + guide_t / 2 + 4, 0, beam_z(h)])
                cube([12, guide_width + 6, 8], center = true);
            translate([guide_x() + guide_t / 2 + 4, 0, beam_z(h)])
                rotate([90, 0, 0])
                    cylinder(d = locating_hole_d,
                             h = guide_width + 8,
                             center = true);
        }

    // 弹簧定位销占位：只允许插入 10 mm 光栅档位的孔。
    color("silver")
        translate([guide_x() + guide_t / 2 + 4,
                   -(guide_width + 6) / 2 - 4,
                   beam_z(h)])
            rotate([90, 0, 0])
                cylinder(d = 3.2, h = 10, center = true);
}

module reference_line_between(span) {
    color("limegreen")
        translate([0, 0, beam_z(reference_height)])
            rotate([0, 90, 0])
                cylinder(d = reference_line_d, h = span, center = true);
}

module calibration_gauge() {
    // 可打印的机械标定规：每个横向挡片对应一根 +10…+100 mm 光束。
    // 实物放入发射/接收端之间后，可逐通道确认高度零点和档位。
    color("lightgray")
        translate([-6, -15, 0])
            cube([12, 30, beam_last_height + 12]);
    for (i = [0 : beam_count - 1]) {
        h = beam_first_height + i * beam_pitch;
        color("black")
            translate([0, 0, h])
                cube([34, 12, 3], center = true);
    }
    color("limegreen")
        translate([0, 0, reference_height])
            cube([42, 4, 2], center = true);
}

module parameter_probe() {
    // 供 validate_geometry.py 读取；几何计算不复制一套 CAD 参数。
    echo(str("SMARTGEAR_SIDE side=", SIDE));
    echo(str("SMARTGEAR_PARAM ",
             "post_nominal_d=", post_nominal_d,
             ";jaw_clearance=", jaw_clearance,
             ";jaw_length=", jaw_length,
             ";jaw_mount_overlap=", jaw_mount_overlap,
             ";v_angle=", v_angle,
             ";arm_length_outer=", arm_length_outer,
             ";arm_length_inner=", arm_length_inner,
             ";arm_outer_y=", arm_outer_y,
             ";arm_inner_y=", arm_inner_y,
             ";clamp_angle_deg=", clamp_angle_deg,
             ";clamp_angle_min_deg=", clamp_angle_min_deg,
             ";clamp_angle_max_deg=", clamp_angle_max_deg,
             ";arm_width=", arm_width,
             ";arm_height=", arm_height,
             ";arm_layer_thickness=", arm_layer_thickness,
             ";arm_layer_gap=", arm_layer_gap,
             ";pivot_d=", pivot_d,
             ";pivot_clearance=", pivot_clearance,
             ";roller_d=", roller_d,
             ";screw_d=", screw_d,
             ";screw_pitch=", screw_pitch,
             ";screw_span=", screw_span,
             ";rod_len=", rod_len,
             ";beam_count=", beam_count,
             ";beam_first_height=", beam_first_height,
             ";beam_pitch=", beam_pitch,
             ";beam_last_height=", beam_last_height,
             ";reference_height=", reference_height));
    cube([0.1, 0.1, 0.1]);
}

module net_post() {
    color([0.45, 0.45, 0.48, 0.65])
        translate([post_x(), 0, -4])
            cylinder(d = post_nominal_d, h = bridge_z + bridge_h + 4);
}

module clamp_assembly(include_post = true) {
    // 两条相反斜率的臂在俯视形成 X，并在同一 Ø8 光轴上上下错层；
    // 端点由同一夹具角度生成，避免把两个打印臂建模成互相穿透的实体。
    arm_a_outer = outer_point(1);
    arm_a_inner = inner_point(1);
    arm_b_outer = outer_point(-1);
    arm_b_inner = inner_point(-1);

    // The nominal post is assembly-preview geometry only; it must not be
    // included in a printable left/right clamp export.
    if (include_post)
        net_post();
    scissor_arm(arm_a_outer, arm_a_inner, arm_lower_z, "arm_a_lower");
    scissor_arm(arm_b_outer, arm_b_inner, arm_upper_z, "arm_b_upper");

    // 两个分别固定在活动臂内端的相向 90 度 V 槽，首样按 Ø25 圆柱立柱。
    v_jaw(arm_a_inner, atan2(-arm_a_inner[1], post_x() - arm_a_inner[0]), arm_lower_z);
    v_jaw(arm_b_inner, atan2(-arm_b_inner[1], post_x() - arm_b_inner[0]), arm_upper_z);

    // 外侧两个竖直滚柱：上侧承接螺杆圆头，下侧容纳螺母/螺纹件。
    u_roller_mount(outer_point(1), true, arm_lower_z);
    u_roller_mount(outer_point(-1), false, arm_upper_z);
    rounded_screw_rod();
    printed_knob();

    metal_pivot_shaft();
    fixed_bridge();
    square_extension_rod();
    optical_guide();
    reference_line_carriage();
}

module oriented_clamp(side = 1, include_post = true) {
    if (side >= 0)
        clamp_assembly(include_post);
    else
        mirror([1, 0, 0]) clamp_assembly(include_post);
}

function resolved_side(default_side) = SIDE == 0 ? default_side : SIDE;

module assembly_preview() {
    left_x = -assembly_span / 2;
    right_x = assembly_span / 2;

    translate([left_x, 0, 0]) oriented_clamp(1, true);
    translate([right_x, 0, 0]) oriented_clamp(-1, true);
    reference_line_between(assembly_span);

    // 仅用于查看双侧关系的透明球网面，不是打印件。
    color([0.2, 0.65, 0.85, 0.18])
        translate([0, -0.8, 0])
            cube([assembly_span, 1.6, bridge_z + bridge_h + rod_len / 2]);
}

if (PART == "assembly") {
    assembly_preview();
} else if (PART == "left_clamp") {
    oriented_clamp(resolved_side(1), false);
} else if (PART == "right_clamp") {
    oriented_clamp(resolved_side(-1), false);
} else if (PART == "arm") {
    scissor_arm(outer_point(1), inner_point(1), arm_lower_z);
} else if (PART == "roller") {
    u_roller_mount(outer_point(1), true, arm_lower_z);
    u_roller_mount(outer_point(-1), false, arm_upper_z);
} else if (PART == "knob") {
    rounded_screw_rod();
    printed_knob();
} else if (PART == "rod") {
    square_extension_rod();
} else if (PART == "bridge") {
    fixed_bridge();
} else if (PART == "guide") {
    optical_guide();
    reference_line_carriage();
} else if (PART == "calibration_gauge") {
    calibration_gauge();
} else if (PART == "parameter_probe") {
    parameter_probe();
} else {
    echo("Unknown PART; use assembly, left_clamp, right_clamp, arm, roller, knob, rod, bridge, guide, calibration_gauge, or parameter_probe.");
}
