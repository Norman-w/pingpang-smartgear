// 乒乓智配：内置式球网支架与过网高度检测结构
// 当前主线 CAD。它替换传统球网和原有球网立柱，不再外挂到旧立柱上。
// 单位：mm；x=球台宽度方向，y=球台长度方向，z=球台台面以上。
//
// 预览/导出：
//   PART="assembly"          含球台截面、网、双侧支架和传感器的装配预览
//   PART="left_stand"         左侧完整桌下夹持支架
//   PART="right_stand"        右侧完整桌下夹持支架
//   PART="post"               单侧立柱主体
//   PART="table_clamp"        单侧传统桌下夹持机构
//   PART="net"                球网/网布装配占位（非打印件）
//   PART="net_rail"           网顶承载条
//   PART="optical_strip"      单侧 10 路红外模块导轨与模块包络
//   PART="sensor_mount"       单侧网顶 PVDF 夹片安装座
//   PART="calibration_gauge"  10 mm 高度档位标定规
//   PART="parameter_probe"    输出验证脚本读取的参数清单
//   SIDE=0                    使用默认右侧；SIDE=1/-1 显式选择左右镜像
//
// 说明：光学器件、PVDF 薄膜、网布、金属螺杆和夹持软垫均为装配占位或
// 标准件边界。该文件验证的是当前机械意图与参数关系，不等同于最终
// PETG 打印强度、球台兼容性或光学精度验收。

$fn = 48;

PART = "assembly";
SIDE = 0;

// 球台与传统网架接口
table_width = 1525;
table_depth_preview = 500;
table_thickness = 25;
table_edge_x = table_width / 2;
post_offset = 18;
post_center_x = table_edge_x + post_offset;
post_body_width = 28;
post_body_depth = 38;
post_bottom = -table_thickness - 18;
post_top_margin = 18;

// 网、光栅和网顶传感器
net_height = 152.5;
net_rail_height = 10;
net_rail_depth = 18;
net_sheet_t = 1.2;
beam_count = 10;
beam_first_height = 10;
beam_pitch = 10;
beam_last_height = beam_first_height + (beam_count - 1) * beam_pitch;
optical_module_depth = 12;
optical_module_width = 18;
optical_module_height = 6;
optical_lens_d = 4;
optical_lens_depth = 3;
optical_rail_depth = 8;
optical_rail_width = 24;
optical_rail_margin = 8;
sensor_count = 2;
sensor_length = 46;
sensor_depth = 10;
sensor_height = 8;
sensor_x_fraction = 0.32;
sensor_front_offset = 10;
reference_height = 50;
reference_line_d = 1.5;

// 传统桌下夹持结构
clamp_reach_inboard = 62;
clamp_pad_depth = 58;
clamp_pad_t = 8;
clamp_clearance = 1.5;
clamp_screw_d = 8;
clamp_screw_x_from_edge = 34;
clamp_screw_length = table_thickness + clamp_pad_t * 2 + 14;
clamp_knob_d = 36;
clamp_knob_h = 12;
post_top = net_height + beam_last_height + optical_module_height / 2 + post_top_margin;
net_span = 2 * (post_center_x - post_body_width / 2);
optical_center_x = post_center_x - post_body_width / 2 - optical_module_depth / 2;
sensor_x = sensor_x_fraction * net_span / 2;
default_side = SIDE == 0 ? 1 : SIDE;

assert(table_width > 0 && table_thickness > 0, "table dimensions must be positive");
assert(post_offset > 0, "integrated stand must sit outside the table edge");
assert(post_center_x > table_edge_x, "post center must be outside the table edge");
assert(net_height >= 152 && net_height <= 153,
       "first integrated stand keeps the traditional 152.5 mm net height");
assert(beam_count == 10, "first integrated stand uses ten optical channels");
assert(beam_first_height == 10 && beam_pitch == 10,
       "optical grid starts at +10 mm with a 10 mm pitch");
assert(beam_last_height == 100,
       "first optical window ends at +100 mm above the net top");
assert(post_top > net_height + beam_last_height + optical_module_height / 2,
       "upright must clear the highest optical module");
assert(net_span > table_width, "the net must bridge both integrated uprights");
assert(clamp_reach_inboard > 40 && clamp_pad_t > 0,
       "traditional under-table clamp needs a real inboard contact pad");
assert(clamp_screw_d == 8 && clamp_screw_length > table_thickness,
       "first clamp uses an M8 vertical tightening screw");
assert(sensor_count == 2 && sensor_x > sensor_length / 2,
       "two PVDF mounts must fit on the net top without crossing the center");
assert(reference_height >= beam_first_height && reference_height <= beam_last_height &&
           (reference_height - beam_first_height) % beam_pitch == 0,
       "reference line must land on a 10 mm optical detent");
assert(reference_line_d > 0, "reference line diameter must be positive");
assert(SIDE == -1 || SIDE == 0 || SIDE == 1, "SIDE must be -1, 0, or 1");

function beam_z(height) = net_height + height;
function beam_inner_span() = net_span - post_body_width - optical_module_depth * 2;
function sensor_z() = net_height + sensor_height / 2 - 1;

module sided(side = 1) {
    if (side >= 0) {
        children();
    } else {
        mirror([1, 0, 0]) children();
    }
}

module table_clamp_positive() {
    pad_x = table_edge_x - clamp_reach_inboard;
    pad_width = post_center_x + post_body_width / 2 - pad_x;
    screw_x = table_edge_x - clamp_screw_x_from_edge;

    color("slategray") {
        // 上下夹持面直接贴合台面，保留少量软垫/装配余量。
        translate([pad_x, -clamp_pad_depth / 2, -clamp_pad_t])
            cube([pad_width, clamp_pad_depth, clamp_pad_t]);
        translate([pad_x, -clamp_pad_depth / 2, -table_thickness - clamp_pad_t])
            cube([pad_width, clamp_pad_depth, clamp_pad_t]);
        // 外侧夹臂把上下接触面连成传统网架的 C 形受力路径。
        translate([post_center_x - post_body_width / 2,
                   -clamp_pad_depth / 2,
                   -table_thickness - clamp_pad_t])
            cube([post_body_width, clamp_pad_depth,
                  table_thickness + clamp_pad_t * 2]);
    }

    color("dimgray") {
        translate([screw_x, 0, -table_thickness - clamp_pad_t - 3])
            cylinder(d = clamp_screw_d, h = clamp_screw_length);
        translate([screw_x, 0, -table_thickness - clamp_pad_t - clamp_knob_h])
            cylinder(d = clamp_knob_d, h = clamp_knob_h);
    }

    color("black") {
        translate([screw_x, 0, -clamp_pad_t - clamp_clearance])
            cylinder(d = clamp_screw_d + 8, h = 2);
        translate([screw_x, 0, -table_thickness - clamp_pad_t - 2])
            cylinder(d = clamp_screw_d + 8, h = 2);
    }
}

module post_positive() {
    color("darkorange") {
        translate([post_center_x - post_body_width / 2,
                   -post_body_depth / 2,
                   post_bottom])
            cube([post_body_width, post_body_depth, post_top - post_bottom]);
        // 台面上方的局部箱型加厚，承载网顶和光学导轨。
        translate([post_center_x - post_body_width / 2 - 5,
                   -post_body_depth / 2 - 4,
                   -2])
            cube([post_body_width + 10, post_body_depth + 8, 34]);
    }

}

module optical_module_positive(height) {
    z0 = beam_z(height);
    color("royalblue")
        translate([optical_center_x - optical_module_depth / 2,
                   -optical_module_width / 2,
                   z0 - optical_module_height / 2])
            cube([optical_module_depth, optical_module_width, optical_module_height]);
    color("red")
        translate([optical_center_x - optical_module_depth / 2 - optical_lens_depth / 2,
                   0, z0])
            rotate([0, 90, 0])
                cylinder(d = optical_lens_d, h = optical_lens_depth, center = true);
}

module optical_strip_positive() {
    color("goldenrod")
        translate([post_center_x - post_body_width / 2 - optical_rail_depth,
                   -optical_rail_width / 2,
                   net_height - optical_rail_margin])
            cube([optical_rail_depth, optical_rail_width,
                  post_top - net_height + optical_rail_margin]);

    for (i = [0:beam_count - 1]) {
        optical_module_positive(beam_first_height + i * beam_pitch);
    }
}

module sensor_mount_positive(x_position) {
    color("mediumpurple")
        translate([x_position - sensor_length / 2,
                   -net_rail_depth / 2 - sensor_front_offset - sensor_depth,
                   net_height - 1])
            cube([sensor_length, sensor_depth, sensor_height]);
    color("black")
        translate([x_position - sensor_length / 2 + 5,
                   -net_rail_depth / 2 - sensor_front_offset - sensor_depth - 2,
                   net_height - 1])
            cube([sensor_length - 10, 2, 3]);
}

module sensor_mount(side = 1) {
    sided(side) sensor_mount_positive(sensor_x);
}

module net_rail() {
    color("white")
        translate([-net_span / 2, -net_rail_depth / 2, net_height - net_rail_height])
            cube([net_span, net_rail_depth, net_rail_height]);
}

module net_panel() {
    color("lightgray", 0.38)
        translate([-net_span / 2, -net_sheet_t / 2, 0])
            cube([net_span, net_sheet_t, net_height - net_rail_height]);
}

module beam_markers() {
    color("limegreen", 0.28)
        for (i = [0:beam_count - 1]) {
            translate([-beam_inner_span() / 2, -0.45,
                       beam_z(beam_first_height + i * beam_pitch) - 0.35])
                cube([beam_inner_span(), 0.9, 0.7]);
        }
}

module reference_line() {
    color("limegreen")
        translate([-net_span / 2, -1.1, beam_z(reference_height) - reference_line_d / 2])
            cube([net_span, reference_line_d, reference_line_d]);
}

module table_preview() {
    color("gray", 0.45)
        translate([-table_width / 2, -table_depth_preview / 2, -table_thickness])
            cube([table_width, table_depth_preview, table_thickness]);
}

module calibration_gauge() {
    gauge_width = 26;
    gauge_depth = 18;
    gauge_height = beam_last_height + 20;
    color("darkorange") {
        cube([gauge_width, gauge_depth, gauge_height]);
        for (i = [0:beam_count - 1]) {
            h = beam_first_height + i * beam_pitch;
            translate([gauge_width - 8, -2, h - 1])
                cube([12, gauge_depth + 4, 2]);
        }
    }
    color("black")
        for (i = [0:beam_count - 1]) {
            h = beam_first_height + i * beam_pitch;
            translate([gauge_width + 6, gauge_depth / 2, h + 1])
                linear_extrude(height = 0.6)
                    text(str("+", h), size = 4, halign = "left", valign = "center");
        }
}

module stand(side = 1) {
    sided(side) {
        post_positive();
        table_clamp_positive();
        optical_strip_positive();
        sensor_mount_positive(sensor_x);
    }
}

module parameter_probe() {
    echo(str("NETSTAND_PARAM table_width=", table_width));
    echo(str("NETSTAND_PARAM net_height=", net_height));
    echo(str("NETSTAND_PARAM beam_count=", beam_count));
    echo(str("NETSTAND_PARAM beam_first_height=", beam_first_height));
    echo(str("NETSTAND_PARAM beam_last_height=", beam_last_height));
    echo(str("NETSTAND_PARAM beam_pitch=", beam_pitch));
    echo(str("NETSTAND_PARAM post_center_x=", post_center_x));
    echo(str("NETSTAND_PARAM net_span=", net_span));
    echo(str("NETSTAND_PARAM post_top=", post_top));
    echo(str("NETSTAND_PARAM sensor_x=", sensor_x));
    cube([0.2, 0.2, 0.2]);
}

if (PART == "assembly") {
    table_preview();
    net_panel();
    net_rail();
    stand(1);
    stand(-1);
    beam_markers();
    reference_line();
} else if (PART == "left_stand") {
    stand(-1);
} else if (PART == "right_stand") {
    stand(1);
} else if (PART == "post") {
    sided(default_side) post_positive();
} else if (PART == "table_clamp") {
    sided(default_side) table_clamp_positive();
} else if (PART == "net") {
    net_panel();
} else if (PART == "net_rail") {
    net_rail();
} else if (PART == "optical_strip") {
    sided(default_side) optical_strip_positive();
} else if (PART == "sensor_mount") {
    sensor_mount(default_side);
} else if (PART == "calibration_gauge") {
    calibration_gauge();
} else if (PART == "parameter_probe") {
    parameter_probe();
} else {
    assert(false, str("unknown PART: ", PART));
}
