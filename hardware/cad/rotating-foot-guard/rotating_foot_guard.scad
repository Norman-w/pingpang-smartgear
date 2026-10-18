// 乒乓球围挡旋转脚防转卡子 v0.1
//
// 设计意图：每只可旋转支撑脚使用一枚 PETG 卡子。卡子从上方落下，
// 上端的反向 U 槽套住 20 mm 长向方管；两条连续侧肋把防转力矩传到
// 下端，单侧的向内扣舌从脚管边缘下方托住/抱住脚，限制脚从工作角度
// 自行旋转。SIDE=+1/-1 可生成相反方向的内扣，左右脚可镜像使用。
//
// 单位：mm。这个文件是独立原型，不修改当前 net_stand.scad 主线。
// 20x20 方管、螺丝规格、旋转轴距和脚端外形仍需实物量测后冻结。

$fn = 48;

PART = "assembly_deployed";
SIDE = 1;

// ---------------------------
// 机械契约 / 可调参数
// ---------------------------

tube_size = 20;
// 这是两侧总和的名义配合余量：inner = 20 + 0.8 = 20.8 mm。
// PETG 首样建议先用该值，实际插入/摇摆后再按测量值改。
tube_clearance_total = 0.8;
tube_inner = tube_size + tube_clearance_total;
guard_wall = 4.0;
guard_outer_depth = tube_inner + 2 * guard_wall;
guard_width_x = 38;

// 预览中的结构基准。长方向为 x，厚度/脚方向为 y，竖直为 z。
rail_center_z = 100;
rail_bottom_z = rail_center_z - tube_size / 2;
rail_top_z = rail_center_z + tube_size / 2;

// 上套槽是反向 U：顶板保留，底部开放，允许从 z+ 套到上方长向管。
saddle_bottom_z = rail_bottom_z - 6;
saddle_top_z = rail_top_z + guard_wall;

// 下端导向/抱脚区。下部横向内扣是故意的局部结构，不把整个窗口堵死。
spine_bottom_z = 7;
hook_z = 8;
hook_height_z = 5.0;
hook_depth_y = 4.0;
hook_bead_d = 3.2;
hook_bead_width_x = guard_width_x - 8;

// 预览用的假定装配包络；不是打印件尺寸真值。
pivot_z = 24;
foot_length_y = 120;
preview_rail_length_x = 150;
preview_post_top_clearance = 0;

assert(SIDE == 1 || SIDE == -1, "SIDE 必须是 +1 或 -1");
assert(tube_size > 0 && tube_clearance_total >= 0);
assert(guard_wall >= 3.2, "PETG 首样的侧壁不应小于 3.2 mm");
assert(guard_outer_depth > tube_inner);
assert(saddle_bottom_z < rail_bottom_z && saddle_top_z > rail_top_z);
assert(hook_z + hook_height_z <= pivot_z - tube_size / 2 + 1.0,
       "下扣高度与脚管底边的预览关系不一致");

function side_value(positive, negative) = SIDE > 0 ? positive : negative;

module block(size, center = [0, 0, 0]) {
    translate(center) cube(size, center = true);
}

module side_wall(y_sign, z0, z1) {
    y_center = y_sign * (guard_outer_depth / 2 - guard_wall / 2);
    block(
        [guard_width_x, guard_wall, z1 - z0],
        [0, y_center, (z0 + z1) / 2]
    );
}

// 上方套入的反向 U 槽。下侧不封，安装时可沿 z- 落下，长向管进入内腔。
module top_saddle() {
    block(
        [guard_width_x, guard_outer_depth, guard_wall],
        [0, 0, saddle_top_z - guard_wall / 2]
    );
    side_wall(-1, saddle_bottom_z, saddle_top_z);
    side_wall(1, saddle_bottom_z, saddle_top_z);
}

// 两侧连续侧肋：从上套槽一直落到脚的抱持区，不把防转力矩交给薄薄的
// 单点卡舌。中间保持 20.8 mm 的开放窗口。
module continuous_spines() {
    side_wall(-1, spine_bottom_z, saddle_bottom_z);
    side_wall(1, spine_bottom_z, saddle_bottom_z);
}

// 单侧向内扣。舌根与侧肋重叠，内端加圆条状小鼻尖，作为“抱住脚边”的
// 第一版入口/防脱特征；SIDE 镜像后可选择更适合实际脚的受力方向。
module inward_hook() {
    hook_outer_y = side_value(guard_outer_depth / 2, -guard_outer_depth / 2);
    hook_center_y = side_value(
        guard_outer_depth / 2 - hook_depth_y / 2,
        -guard_outer_depth / 2 + hook_depth_y / 2
    );
    block(
        [guard_width_x, hook_depth_y, hook_height_z],
        [0, hook_center_y, hook_z + hook_height_z / 2]
    );

    // 鼻尖中心落在内扣舌的内边，避免用尖薄平板直接刮擦 PETG/方管。
    bead_center_y = side_value(
        guard_outer_depth / 2 - hook_depth_y,
        -guard_outer_depth / 2 + hook_depth_y
    );
    translate([0, bead_center_y, hook_z + hook_height_z - hook_bead_d / 2])
        rotate([0, 90, 0])
        cylinder(d = hook_bead_d, h = hook_bead_width_x, center = true);
}

module guard_clip() {
    union() {
        top_saddle();
        continuous_spines();
        inward_hook();
    }
}

// 一个短的下扣试装片，先验证 20x20 方管进入窗口和内扣方向；后续可单独
// 导出它作为首件，而不必先打印整只长卡子。
module hook_test_coupon() {
    coupon_width_x = 34;
    coupon_depth_y = guard_outer_depth;
    coupon_height_z = 24;
    side_y = side_value(
        coupon_depth_y / 2 - guard_wall / 2,
        -coupon_depth_y / 2 + guard_wall / 2
    );
    // 两侧导向墙
    block([coupon_width_x, guard_wall, coupon_height_z], [0, -coupon_depth_y / 2 + guard_wall / 2, coupon_height_z / 2]);
    block([coupon_width_x, guard_wall, coupon_height_z], [0, coupon_depth_y / 2 - guard_wall / 2, coupon_height_z / 2]);
    // 底部局部托台和同样的内扣舌
    block([coupon_width_x, coupon_depth_y, guard_wall], [0, 0, guard_wall / 2]);
    translate([0, side_y, 13])
        block([coupon_width_x, hook_depth_y, hook_height_z]);
    translate([0, side_value(coupon_depth_y / 2 - hook_depth_y, -coupon_depth_y / 2 + hook_depth_y), 16])
        rotate([0, 90, 0])
        cylinder(d = hook_bead_d, h = coupon_width_x - 8, center = true);
}

// ---------------------------
// 装配预览包络（不进入 STL）
// ---------------------------

module square_tube_x(length, z_center, tube_color = [0.68, 0.70, 0.73]) {
    color(tube_color)
        translate([0, 0, z_center])
            cube([length, tube_size, tube_size], center = true);
}

module square_tube_z(z0, z1, tube_color = [0.58, 0.60, 0.64]) {
    color(tube_color)
        translate([0, 0, (z0 + z1) / 2])
            cube([tube_size, tube_size, z1 - z0], center = true);
}

module rotating_foot(angle_deg, tube_color = [0.50, 0.52, 0.56]) {
    color(tube_color)
        rotate([0, 0, angle_deg])
            translate([0, 0, pivot_z])
                cube([tube_size, foot_length_y, tube_size], center = true);
}

module pivot_hardware() {
    // 仅作 M4~M5 轴线位置示意；实际孔径、螺丝长度和螺母 AF 待实测。
    color([0.78, 0.80, 0.84])
        translate([0, 0, pivot_z - 11])
            cylinder(d = 5.2, h = 34, center = false);
    color([0.82, 0.68, 0.18])
        translate([0, 0, pivot_z + 10])
            cylinder(d = 9.0, h = 5, $fn = 6, center = false);
}

module preview_clip(alpha = 0.78) {
    color([0.95, 0.36, 0.08], alpha) guard_clip();
}

module assembly_deployed() {
    square_tube_x(preview_rail_length_x, rail_center_z);
    square_tube_z(pivot_z + tube_size / 2, rail_bottom_z + preview_post_top_clearance);
    // 工作状态：脚与围挡长方向约 90°，形成厚度方向支撑。
    rotating_foot(90);
    pivot_hardware();
    preview_clip(0.72);
}

module assembly_folded() {
    square_tube_x(preview_rail_length_x, rail_center_z);
    square_tube_z(pivot_z + tube_size / 2, rail_bottom_z + preview_post_top_clearance);
    // 收纳状态：脚旋到与长向上管平行，仅用于说明需要被限位的自由度。
    rotating_foot(0, [0.40, 0.42, 0.46]);
    pivot_hardware();
    preview_clip(0.42);
}

module clip_cutaway() {
    // 预览专用：取 x 中心的薄截面，直接显示 y-z 方向的装入路径。
    // 这不是打印实体，也不会改变 clip STL。
    intersection() {
        guard_clip();
        translate([0, 0, 60])
            cube([10, guard_outer_depth + 12, 130], center = true);
    }
}

module fit_section() {
    // 透明上下文只用于显示方管如何进入上槽、脚边如何被下扣托住。
    color([0.70, 0.72, 0.75, 0.68])
        translate([0, 0, rail_center_z])
            cube([guard_width_x - 4, tube_size, tube_size], center = true);
    color([0.48, 0.50, 0.54, 0.68])
        translate([0, 0, pivot_z])
            cube([tube_size, tube_size, tube_size], center = true);
    color([0.95, 0.36, 0.08])
        clip_cutaway();
}

module print_orientation() {
    // 侧面平放：原模型 y 方向成为打印高度，目标是不需要大面积支撑。
    rotate([90, 0, 0]) guard_clip();
}

if (PART == "clip") {
    guard_clip();
} else if (PART == "clip_cutaway") {
    clip_cutaway();
} else if (PART == "hook_test_coupon") {
    hook_test_coupon();
} else if (PART == "fit_section") {
    fit_section();
} else if (PART == "assembly_deployed") {
    assembly_deployed();
} else if (PART == "assembly_folded") {
    assembly_folded();
} else if (PART == "print_orientation") {
    print_orientation();
} else {
    echo("未知 PART，使用 clip");
    guard_clip();
}
