// 乒乓智配：内置式球网支架与过网高度检测结构
// 当前主线 CAD。它替换传统球网和原有球网立柱，不再外挂到旧立柱上。
// 单位：mm；x=球台宽度方向，y=球台长度方向，z=球台台面以上。
//
// 预览/导出：
//   PART="assembly"          含球台截面、网、双侧支架和传感器的装配预览
//   PART="left_stand"         左侧立柱/桌下夹持/光学导轨结构检查件
//   PART="right_stand"        右侧立柱/桌下夹持/光学导轨结构检查件
//   PART="post"               单侧立柱主体
//   PART="post_segment"       单段可打印立柱（由 post_segment_index 选择）
//   PART="lower_stand_segment" 下段立柱与固定 C 形夹一体打印件
//   PART="post_joint_sleeve"  立柱中部外套筒
//   PART="post_joint_key"     立柱中部内芯
//   PART="table_clamp"        单侧传统桌下夹持机构装配预览
//   PART="table_clamp_section" 桌板剖面/免打孔夹紧受力路径预览
//   PART="table_clamp_body"   单侧固定 C 形夹体
//   PART="clamp_top_pad"     台面上表面可替换保护垫（TPU/硅胶占位）
//   PART="clamp_pressure_pad" 台底可动压块/软垫占位
//   PART="clamp_screw"        M8 螺杆占位（非打印件，顶端圆头）
//   PART="clamp_body_nut"     固定在下臂螺母座中的 M8 螺母（标准件）
//   PART="clamp_knob"         手拧旋钮（含 M8 螺母捕获窝）
//   PART="clamp_knob_nut"     旋钮内捕获的 M8 螺母（标准件）
//   PART="net"                球网/网布装配占位（非打印件）
//   PART="net_rail"           网顶承载条
//   PART="net_rail_segment"   单段网顶承载条（由 rail_segment_index 选择）
//   PART="net_rail_splice"    网顶承载条拼接片（由 rail_splice_index 选择）
//   PART="net_rail_saddle"    立柱内侧网顶承托/端部限位座
//   PART="optical_rail"       单侧可打印 10 路红外模块导轨、定位孔与刻度
//   PART="optical_strip"      单侧 10 路红外模块导轨与模块装配预览
//   PART="optical_module_carrier" 单个光学模块中性载台/调节槽（由 optical_module_index 选择）
//   PART="sensor_mount"       单侧网顶 PVDF 夹片安装座
//   PART="sensor_mount_body"   单侧可打印 PVDF 安装座本体（不含薄膜/压片）
//   PART="pvdf_film"          PVDF 薄膜包络（非打印件）
//   PART="sensor_clamp_lip"   PVDF 薄膜两侧可拆压片
//   PART="reference_carriage" 参考线端座与定位销
//   PART="reference_carriage_body" 可打印参考线端座本体（不含定位销）
//   PART="reference_pin"      参考线弹簧销占位（非打印件）
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
// 立柱外置 37 mm，使光学导轨留在立柱内侧与台边之间的开放空间；
// 模块镜头轴线因此可以覆盖台面边缘，而不会嵌入实心立柱。
post_offset = 37;
post_center_x = table_edge_x + post_offset;
post_body_width = 28;
post_body_depth = 38;
clamp_lower_arm_clearance = 10;
post_bottom = -table_thickness - clamp_lower_arm_clearance;
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
optical_locating_hole_d = 4;
optical_carrier_clearance = 0.6;
optical_carrier_wall = 3;
optical_carrier_z_wall = 1.5;
optical_carrier_back_depth = 5;
optical_carrier_slot_d = 3.4;
optical_carrier_slot_length = 4;
optical_module_index = 0;
scale_tick_width = 8;
scale_tick_height = 1.5;
sensor_count = 2;
sensor_length = 46;
sensor_depth = 10;
sensor_height = 8;
sensor_x_fraction = 0.32;
sensor_front_offset = 10;
sensor_film_length = sensor_length - 10;
sensor_film_depth = 2;
sensor_film_height = 3;
sensor_clamp_tab_width = 6;
sensor_clamp_tab_depth = 3;
sensor_clamp_tab_height = 4;
reference_height = 50;
reference_line_d = 1.5;
reference_pin_d = 3;
reference_pin_bore_d = reference_pin_d + 0.4;
reference_carriage_width = 20;
reference_carriage_depth = 8;
reference_carriage_height = 10;
reference_pin_length = optical_rail_width + reference_carriage_depth + 4;
rail_segment_index = 0;

// 传统桌下夹持结构
clamp_reach_inboard = 62;
clamp_outer_extension = 22;
clamp_pad_depth = 58;
clamp_pad_t = 8;
clamp_clearance = 1.5;
clamp_screw_d = 8;
// 首样采用真实 M8×1.25 金属螺杆；螺纹牙型不在 PETG 几何中建模，
// 但螺距作为标准件接口的一部分固化并由参数探针/验证脚本读取。
clamp_screw_pitch = 1.25;
clamp_screw_bore_d = clamp_screw_d + 0.8;
clamp_screw_inset = 30;
clamp_knob_d = 36;
clamp_knob_h = 12;
clamp_screw_to_knob_top = 32;
clamp_screw_capture_extension = 2;
clamp_nut_af = 13;
clamp_nut_h = 6.5;
clamp_nut_clearance = 0.35;
clamp_nut_pocket_af = clamp_nut_af + 2 * clamp_nut_clearance;
clamp_nut_pocket_depth = clamp_nut_h + clamp_nut_clearance;
clamp_outer_wall_width = 22;
clamp_lower_arm_t = clamp_pad_t;
clamp_threaded_boss_d = 22;
clamp_threaded_boss_h = 12;
clamp_top_pad_width = 96;
clamp_top_pad_depth = 48;
clamp_top_pad_t = 2;
clamp_pressure_pad_width = 42;
clamp_pressure_pad_depth = 44;
clamp_pressure_pad_t = 2;
post_top = net_height + beam_last_height + optical_module_height / 2 + post_top_margin;
post_segment_count = 2;
post_joint_gap = 2;
post_joint_sleeve_h = 24;
post_joint_clearance = 0.6;
post_segment_index = 0;
post_total_height = post_top - post_bottom;
post_segment_length =
    (post_total_height - post_joint_gap) / post_segment_count;
post_joint_z = post_bottom + post_segment_length + post_joint_gap / 2;
net_span = 2 * (post_center_x - post_body_width / 2);
net_rail_segment_count = 3;
net_rail_splice_overlap = 20;
net_rail_segment_length =
    (net_span + (net_rail_segment_count - 1) * net_rail_splice_overlap) /
    net_rail_segment_count;
net_rail_splice_plate_length = 60;
net_rail_splice_plate_depth = net_rail_depth + 4;
net_rail_splice_plate_t = 4;
net_rail_splice_hole_d = 3.2;
rail_splice_index = 0;
net_rail_saddle_overlap = 6;
net_rail_saddle_width = 12;
net_rail_saddle_depth = net_rail_depth + 6;
net_rail_saddle_height = 4;
net_rail_saddle_stop_t = 3;
// 右侧光学件的光轴必须覆盖球台边缘；左侧由 SIDE 镜像。导轨位于
// 立柱内侧与台边之间的开放空间，模块本体贴在导轨内侧，镜头朝向球台中心，
// 不把模块或导轨嵌入立柱实体。
optical_beam_edge_overlap = 0.5;
optical_beam_axis_x = table_edge_x + optical_beam_edge_overlap;
optical_center_x = optical_beam_axis_x +
                   optical_module_depth / 2 + optical_lens_depth / 2;
optical_rail_x = optical_center_x + optical_module_depth / 2;
optical_carrier_front_depth = optical_module_depth + 2 * optical_carrier_clearance;
optical_carrier_front_x = optical_rail_x - optical_carrier_front_depth;
optical_carrier_width = optical_module_width + 2 * optical_carrier_wall;
optical_carrier_height = optical_module_height + 2 * optical_carrier_z_wall;
optical_carrier_slot_offset = optical_module_width / 4 + optical_carrier_wall / 2;
sensor_x = sensor_x_fraction * net_span / 2;
clamp_pad_x = table_edge_x - clamp_reach_inboard;
clamp_pad_outer_x = post_center_x + post_body_width / 2 + clamp_outer_extension;
clamp_outer_wall_x = post_center_x + post_body_width / 2;
clamp_screw_x = table_edge_x - clamp_screw_inset;
clamp_top_pad_x = clamp_pad_x + 8;
clamp_lower_arm_top_z = -table_thickness - clamp_lower_arm_clearance;
clamp_lower_arm_bottom_z = clamp_lower_arm_top_z - clamp_lower_arm_t;
clamp_pressure_pad_top_z = -table_thickness - clamp_clearance;
clamp_pressure_pad_bottom_z = clamp_pressure_pad_top_z - clamp_pressure_pad_t;
clamp_pressure_pad_x = clamp_screw_x - clamp_pressure_pad_width / 2;
// The screw pushes the underside of the independent pad. It must not model
// itself as passing through the pad or through the tabletop.
clamp_screw_top_z = clamp_pressure_pad_bottom_z;
clamp_knob_top_z = clamp_screw_top_z - clamp_screw_to_knob_top;
clamp_knob_bottom_z = clamp_knob_top_z - clamp_knob_h;
clamp_screw_bottom_z =
    clamp_knob_top_z - clamp_nut_pocket_depth - clamp_screw_capture_extension;
clamp_screw_length = clamp_screw_top_z - clamp_screw_bottom_z;
clamp_screw_tip_radius = clamp_screw_d / 2;
clamp_body_nut_z = clamp_lower_arm_bottom_z + clamp_nut_clearance;
clamp_knob_nut_z = clamp_knob_top_z - clamp_nut_h;
default_side = SIDE == 0 ? 1 : SIDE;

assert(table_width > 0 && table_thickness > 0, "table dimensions must be positive");
assert(post_offset > 0, "integrated stand must sit outside the table edge");
assert(post_center_x > table_edge_x, "post center must be outside the table edge");
assert(optical_beam_edge_overlap >= 0 &&
           optical_beam_axis_x >= table_edge_x &&
           optical_rail_x >= table_edge_x &&
           optical_rail_x + optical_rail_depth <=
           post_center_x - post_body_width / 2,
       "optical axis must cover the tabletop edge while the rail stays outside the post body");
assert(net_height >= 152 && net_height <= 153,
       "first integrated stand keeps the traditional 152.5 mm net height");
assert(beam_count == 10, "first integrated stand uses ten optical channels");
assert(beam_first_height == 10 && beam_pitch == 10,
       "optical grid starts at +10 mm with a 10 mm pitch");
assert(beam_last_height == 100,
       "first optical window ends at +100 mm above the net top");
assert(post_top > net_height + beam_last_height + optical_module_height / 2,
       "upright must clear the highest optical module");
assert(post_segment_count == 2 && post_joint_gap > 0 &&
           post_segment_length > 100 && post_segment_length < 180 &&
           post_joint_sleeve_h > post_joint_gap && post_joint_clearance > 0,
       "the upright must split into two printable segments with a keyed joint");
assert(post_segment_index >= 0 && post_segment_index < post_segment_count,
       "post_segment_index must select an existing printable upright segment");
assert(optical_locating_hole_d > 0 && optical_locating_hole_d < optical_rail_width,
       "10 mm optical locating holes must fit through the rail");
assert(scale_tick_width > 0 && scale_tick_height > 0 && scale_tick_width < optical_rail_width,
       "height scale ticks must fit on the optical rail");
assert(optical_carrier_clearance > 0 && optical_carrier_wall >= 2 &&
           optical_carrier_z_wall > 0 &&
           optical_carrier_back_depth > 0 &&
           optical_carrier_front_depth > optical_module_depth &&
           optical_carrier_width > optical_module_width &&
           optical_carrier_height > optical_module_height &&
           optical_carrier_height < beam_pitch,
       "optical module carrier must leave a printable clearance pocket and rear wall");
assert(optical_carrier_slot_d > 0 &&
           optical_carrier_slot_length > optical_carrier_slot_d &&
           optical_carrier_slot_length < optical_carrier_width,
       "optical carrier adjustment slots must be printable");
assert(optical_module_index >= 0 && optical_module_index < beam_count,
       "optical_module_index must select an existing 10 mm channel");
assert(net_span > table_width, "the net must bridge both integrated uprights");
assert(net_rail_segment_count >= 2 && net_rail_segment_count <= 5 &&
           net_rail_segment_length > 100 && net_rail_splice_overlap > 0 &&
           net_rail_splice_overlap < net_rail_segment_length,
       "the long net rail must be split into printable overlapping segments");
assert(net_rail_splice_plate_length > net_rail_splice_overlap * 2 &&
           net_rail_splice_plate_depth > net_rail_depth &&
           net_rail_splice_plate_t > 0 && net_rail_splice_hole_d > 0 &&
           rail_splice_index >= 0 && rail_splice_index < net_rail_segment_count - 1,
       "each rail seam needs a printable splice plate and valid index");
assert(net_rail_saddle_overlap > 0 &&
           net_rail_saddle_width > net_rail_saddle_overlap &&
           net_rail_saddle_depth > net_rail_depth &&
           net_rail_saddle_height > 0 &&
           net_rail_saddle_stop_t > 0 &&
           net_rail_saddle_stop_t < net_rail_saddle_width,
       "each upright needs a printable rail saddle and end stop");
assert(clamp_reach_inboard > 40 && clamp_pad_t > 0 && clamp_outer_extension > 0,
       "traditional under-table clamp needs a real inboard contact pad");
assert(clamp_pad_x < table_edge_x && clamp_pad_outer_x > table_edge_x &&
           clamp_outer_wall_x < clamp_pad_outer_x &&
           clamp_screw_x > clamp_pad_x && clamp_screw_x < table_edge_x,
       "the C clamp must bridge the edge and keep the M8 screw below the tabletop");
assert(clamp_lower_arm_bottom_z < clamp_lower_arm_top_z &&
           clamp_lower_arm_top_z < clamp_pressure_pad_bottom_z &&
           clamp_pressure_pad_top_z < -table_thickness,
       "the lower arm and pressure pad must stay below the tabletop without drilling");
assert(clamp_pressure_pad_x > clamp_pad_x &&
           clamp_pressure_pad_x + clamp_pressure_pad_width < table_edge_x,
       "the movable pressure pad must contact the underside inside the table edge");
assert(clamp_top_pad_t > 0 && clamp_top_pad_width > 0 &&
           clamp_top_pad_depth > 0 &&
           clamp_top_pad_x >= clamp_pad_x &&
           clamp_top_pad_x + clamp_top_pad_width <= clamp_pad_outer_x &&
           clamp_top_pad_depth <= clamp_pad_depth,
       "replaceable upper protective pad must fit under the fixed jaw");
assert(clamp_outer_wall_width == clamp_pad_outer_x - clamp_outer_wall_x,
       "outer wall width must connect the post to the outer clamp edge");
assert(clamp_screw_d == 8 && clamp_screw_pitch == 1.25 &&
           clamp_screw_length > table_thickness,
       "first clamp uses an M8 x 1.25 vertical tightening screw");
assert(clamp_screw_top_z <= clamp_pressure_pad_bottom_z &&
           clamp_screw_top_z < -table_thickness &&
           clamp_screw_tip_radius > 0,
       "rounded M8 screw tip must contact the pad underside without penetrating it");
assert(clamp_nut_af > clamp_screw_d && clamp_nut_h > 0 &&
           clamp_nut_clearance > 0 &&
           clamp_nut_pocket_af > clamp_nut_af &&
           clamp_nut_pocket_af / cos(30) + 2 < clamp_threaded_boss_d &&
           clamp_nut_pocket_depth >= clamp_nut_h &&
           clamp_nut_pocket_depth < clamp_threaded_boss_h,
       "M8 nut pockets must fit inside the lower boss with printable clearance");
assert(clamp_screw_to_knob_top > clamp_nut_pocket_depth &&
           clamp_screw_capture_extension > 0 &&
           clamp_screw_bottom_z < clamp_knob_nut_z &&
           clamp_knob_bottom_z < clamp_knob_top_z,
       "M8 rod must reach the captured knob nut and leave a usable handwheel");
assert(clamp_knob_d > clamp_screw_bore_d && clamp_knob_h > clamp_nut_h,
       "printed clamp knob must leave an M8 bore and captured-nut wall");
assert(sensor_count == 2 && sensor_x > sensor_length / 2,
       "two PVDF mounts must fit on the net top without crossing the center");
assert(sensor_front_offset > 0, "PVDF mount front offset must leave a printable connection bridge");
assert(sensor_film_length > 0 && sensor_film_depth > 0 && sensor_film_height > 0 &&
           sensor_clamp_tab_width > 0 && sensor_clamp_tab_depth > 0 &&
           sensor_clamp_tab_height > 0 && sensor_clamp_tab_width < sensor_film_length,
       "PVDF film and its removable clamp lips must have printable dimensions");
assert(reference_height >= beam_first_height && reference_height <= beam_last_height &&
           (reference_height - beam_first_height) % beam_pitch == 0,
       "reference line must land on a 10 mm optical detent");
assert(reference_line_d > 0, "reference line diameter must be positive");
assert(reference_pin_d > 0 && reference_pin_d < optical_locating_hole_d,
       "reference pin must fit the 10 mm locating holes");
assert(reference_pin_bore_d > reference_pin_d &&
           reference_pin_bore_d < optical_locating_hole_d &&
           reference_pin_length > optical_rail_width + reference_carriage_depth,
       "reference carriage pin bore must leave print clearance and span the rail");
assert(reference_carriage_width > 0 && reference_carriage_depth > 0 &&
           reference_carriage_height > 0,
       "reference carriage dimensions must be positive");
assert(rail_segment_index >= 0 && rail_segment_index < net_rail_segment_count,
       "rail_segment_index must select an existing printable rail segment");
assert(SIDE == -1 || SIDE == 0 || SIDE == 1, "SIDE must be -1, 0, or 1");

function beam_z(height) = net_height + height;
// 参考光束线按实际镜头光轴，而不是按模块外壳内缘绘制；这样装配预览
// 能直接暴露光束是否覆盖球台边缘。
function beam_inner_span() = 2 * optical_beam_axis_x;
function sensor_z() = net_height + sensor_height / 2 - 1;
function net_rail_segment_start(index) =
    -net_span / 2 + index * (net_rail_segment_length - net_rail_splice_overlap);
function net_rail_splice_center(index) =
    net_rail_segment_start(index) + net_rail_segment_length - net_rail_splice_overlap / 2;

module sided(side = 1) {
    if (side >= 0) {
        children();
    } else {
        mirror([1, 0, 0]) children();
    }
}

module table_clamp_body_positive() {
    // 固定件是一个真正有开口的 C 形夹体：上夹板在台面上方，
    // 下臂在台底下方，中间留出台面厚度和压块行程；不把任何零件嵌入台面。
    lower_arm_x = clamp_screw_x - clamp_threaded_boss_d / 2;
    color("slategray")
        difference() {
            union() {
                translate([clamp_pad_x, -clamp_pad_depth / 2, clamp_top_pad_t])
                    cube([clamp_pad_outer_x - clamp_pad_x,
                          clamp_pad_depth, clamp_pad_t]);
                translate([clamp_outer_wall_x, -clamp_pad_depth / 2,
                           clamp_lower_arm_bottom_z])
                    cube([clamp_outer_wall_width, clamp_pad_depth,
                          clamp_pad_t + clamp_top_pad_t + table_thickness +
                          clamp_lower_arm_clearance]);
                translate([lower_arm_x, -clamp_pad_depth / 2,
                           clamp_lower_arm_bottom_z])
                    cube([clamp_pad_outer_x - lower_arm_x,
                          clamp_pad_depth, clamp_lower_arm_t]);
                translate([clamp_screw_x, 0, clamp_lower_arm_bottom_z])
                    cylinder(d = clamp_threaded_boss_d, h = clamp_threaded_boss_h);
            }
            // M8 螺杆只穿过下臂/螺母座，不能穿过球台。
            translate([clamp_screw_x, 0, clamp_lower_arm_bottom_z - 1])
                cylinder(d = clamp_screw_bore_d,
                         h = clamp_threaded_boss_h + 2);
            // 下臂下侧捕获固定 M8 螺母；螺杆转动而沿轴向进退，
            // 旋钮/螺杆受力路径不依赖 PETG 螺纹。
            translate([clamp_screw_x, 0, clamp_lower_arm_bottom_z - 0.01])
                hex_prism(clamp_nut_pocket_af, clamp_nut_pocket_depth + 0.01);
        }
}

module hex_prism(across_flats, height) {
    rotate([0, 0, 30])
        cylinder(r = across_flats / (2 * cos(30)), h = height, $fn = 6);
}

module m8_nut_positive() {
    difference() {
        hex_prism(clamp_nut_af, clamp_nut_h);
        translate([0, 0, -1])
            cylinder(d = clamp_screw_bore_d, h = clamp_nut_h + 2);
    }
}

module clamp_body_nut_positive() {
    color("gold")
        translate([clamp_screw_x, 0, clamp_body_nut_z])
            m8_nut_positive();
}

module clamp_pressure_pad_positive() {
    // 独立可动压块：旋钮从下方顶它，压块顶面只接触台面底面。
    color("black")
        translate([clamp_pressure_pad_x, -clamp_pressure_pad_depth / 2,
                   clamp_pressure_pad_bottom_z])
            cube([clamp_pressure_pad_width, clamp_pressure_pad_depth,
                  clamp_pressure_pad_t]);
}

module clamp_top_pad_positive() {
    // 可替换上保护垫位于桌面 z=0 与固定上夹板之间；首样可用 TPU 打印，
    // 也可直接裁切同厚度硅胶片。它只承担接触保护，不承担 C 形夹结构力路。
    color("black")
        translate([clamp_top_pad_x, -clamp_top_pad_depth / 2, 0])
            cube([clamp_top_pad_width, clamp_top_pad_depth, clamp_top_pad_t]);
}

module clamp_screw_positive() {
    color("dimgray") {
        translate([clamp_screw_x, 0, clamp_screw_bottom_z])
            cylinder(d = clamp_screw_d,
                     h = clamp_screw_length - clamp_screw_tip_radius);
        translate([clamp_screw_x, 0,
                   clamp_screw_top_z - clamp_screw_tip_radius])
            sphere(r = clamp_screw_tip_radius);
    }
}

module clamp_knob_positive() {
    color("dimgray")
        difference() {
            translate([clamp_screw_x, 0, clamp_knob_bottom_z])
                cylinder(d = clamp_knob_d, h = clamp_knob_h);
            // The center bore lets the rod pass through the printed handwheel.
            translate([clamp_screw_x, 0, clamp_knob_bottom_z - 1])
                cylinder(d = clamp_screw_bore_d, h = clamp_knob_h + 2);
            // An M8 hex nut is captured from the handwheel top. The rod is
            // threaded through this nut, so turning the handwheel turns the
            // rod while the lower-arm nut converts rotation into clamp force.
            translate([clamp_screw_x, 0,
                       clamp_knob_top_z - clamp_nut_pocket_depth])
                hex_prism(clamp_nut_pocket_af, clamp_nut_pocket_depth + 0.01);
        }
}

module clamp_knob_nut_positive() {
    color("gold")
        translate([clamp_screw_x, 0, clamp_knob_nut_z])
            m8_nut_positive();
}

module table_clamp_positive() {
    table_clamp_body_positive();
    clamp_top_pad_positive();
    clamp_body_nut_positive();
    clamp_pressure_pad_positive();
    clamp_screw_positive();
    clamp_knob_positive();
    clamp_knob_nut_positive();
}

module table_clamp_section_clip() {
    // 只保留 y=0 附近的薄剖面，便于直接看清桌板、压块、圆头螺杆和两枚
    // M8 螺母的相对高度；它是可视校验件，不是额外的打印零件。
    translate([clamp_pad_x - 8, -4, clamp_knob_bottom_z - 5])
        cube([clamp_pad_outer_x - clamp_pad_x + 16,
              8,
              -clamp_knob_bottom_z + 10]);
}

module table_clamp_section_positive() {
    section_x = clamp_pad_x - 8;
    section_width = clamp_pad_outer_x - clamp_pad_x + 16;
    // 半透明台板截面明确标出 z=-table_thickness 到 z=0 的实体范围。
    color("gray", 0.45)
        translate([section_x, -4, -table_thickness])
            cube([section_width, 8, table_thickness]);
    intersection() {
        table_clamp_body_positive();
        table_clamp_section_clip();
    }
    intersection() {
        clamp_top_pad_positive();
        table_clamp_section_clip();
    }
    intersection() {
        clamp_pressure_pad_positive();
        table_clamp_section_clip();
    }
    intersection() {
        clamp_screw_positive();
        table_clamp_section_clip();
    }
    intersection() {
        clamp_body_nut_positive();
        table_clamp_section_clip();
    }
    intersection() {
        clamp_knob_positive();
        table_clamp_section_clip();
    }
    intersection() {
        clamp_knob_nut_positive();
        table_clamp_section_clip();
    }
}

module post_segment_positive(index = 0) {
    segment_z = post_bottom + index * (post_segment_length + post_joint_gap);
    color("darkorange")
        translate([post_center_x - post_body_width / 2,
                   -post_body_depth / 2, segment_z])
            cube([post_body_width, post_body_depth, post_segment_length]);
    // 下段单独导出时也必须带上台面上方的箱型加厚，否则单件打印会
    // 丢失承载网顶和光学导轨的局部结构。
    if (index == 0) {
        color("darkorange")
            translate([post_center_x - post_body_width / 2 - 5,
                       -post_body_depth / 2 - 4,
                       -2])
                cube([post_body_width + 10, post_body_depth + 8, 34]);
    }
}

module lower_stand_segment_positive() {
    // 首样的下段与桌下夹体一体打印，避免把两个相互穿入的独立实体
    // 交给装配者硬压在一起；上段仍通过套筒和内芯接到这个下段。
    union() {
        post_segment_positive(0);
        table_clamp_body_positive();
    }
}

module post_joint_sleeve_positive() {
    color("darkorange")
        difference() {
            translate([post_center_x - post_body_width / 2 - 5,
                       -post_body_depth / 2 - 4,
                       post_joint_z - post_joint_sleeve_h / 2])
                cube([post_body_width + 10, post_body_depth + 8,
                      post_joint_sleeve_h]);
            translate([post_center_x - post_body_width / 2 - post_joint_clearance,
                       -post_body_depth / 2 - post_joint_clearance,
                       post_joint_z - post_joint_sleeve_h / 2 - 1])
                cube([post_body_width + 2 * post_joint_clearance,
                      post_body_depth + 2 * post_joint_clearance,
                      post_joint_sleeve_h + 2]);
        }
}

module post_joint_key_positive() {
    color("darkorange")
        translate([post_center_x - (post_body_width - 2) / 2,
                   -(post_body_depth - 2) / 2,
                   post_joint_z - (post_joint_sleeve_h - 4) / 2])
            cube([post_body_width - 2, post_body_depth - 2,
                  post_joint_sleeve_h - 4]);
}

module post_positive() {
    for (index = [0:post_segment_count - 1]) {
        post_segment_positive(index);
    }
    post_joint_sleeve_positive();
    post_joint_key_positive();
}

module slot_through_x_y(y_center, z_center) {
    hull() {
        for (y_position = [y_center - optical_carrier_slot_length / 2,
                           y_center + optical_carrier_slot_length / 2]) {
            translate([optical_rail_x - 1, y_position, z_center])
                rotate([0, 90, 0])
                    cylinder(d = optical_carrier_slot_d,
                             h = optical_carrier_back_depth + 2);
        }
    }
}

module slot_through_x_z(y_center, z_center) {
    hull() {
        for (z_position = [z_center - optical_carrier_slot_length / 2,
                           z_center + optical_carrier_slot_length / 2]) {
            translate([optical_rail_x - 1, y_center, z_position])
                rotate([0, 90, 0])
                    cylinder(d = optical_carrier_slot_d,
                             h = optical_carrier_back_depth + 2);
        }
    }
}

module optical_module_carrier_positive(height) {
    z0 = beam_z(height);
    // 载台是一个包住电子模块的中性 U 形框。后壁与连续导轨重合，
    // 两个正交长孔给 M3 紧固件留下有限俯仰/偏航调节余量；最终角度
    // 和锁紧力仍需在真实发射/接收器上实测，不把包络当成光学精度承诺。
    color("teal")
        difference() {
            translate([optical_carrier_front_x,
                       -optical_carrier_width / 2,
                       z0 - optical_carrier_height / 2])
                cube([optical_carrier_front_depth + optical_carrier_back_depth,
                      optical_carrier_width, optical_carrier_height]);
            translate([optical_carrier_front_x - 1,
                       -optical_module_width / 2 - optical_carrier_clearance,
                       z0 - optical_module_height / 2 - optical_carrier_clearance])
                cube([optical_carrier_front_depth + 1,
                      optical_module_width + 2 * optical_carrier_clearance,
                      optical_module_height + 2 * optical_carrier_clearance]);
            // y 向槽用于偏航微调，z 向槽用于俯仰微调；槽位落在后壁/侧耳，
            // 不切穿模块包络的中心区域。
            slot_through_x_y(0, z0 - optical_carrier_height / 4);
            slot_through_x_z(optical_carrier_slot_offset, z0);
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

module optical_rail_positive() {
    color("goldenrod")
        difference() {
            translate([optical_rail_x, -optical_rail_width / 2,
                       net_height - optical_rail_margin])
                cube([optical_rail_depth, optical_rail_width,
                      post_top - net_height + optical_rail_margin]);
            // 每个 10 mm 档位都有实际贯穿孔；参考线/标定销可以使用这些孔。
            for (i = [0:beam_count - 1]) {
                translate([optical_rail_x + optical_rail_depth / 2, 0,
                           beam_z(beam_first_height + i * beam_pitch)])
                    rotate([90, 0, 0])
                        cylinder(d = optical_locating_hole_d,
                                 h = optical_rail_width + 2,
                                 center = true);
            }
        }

    color("white")
        for (i = [0:beam_count - 1]) {
            translate([optical_rail_x - 0.5, -scale_tick_width / 2,
                       beam_z(beam_first_height + i * beam_pitch) - scale_tick_height / 2])
                cube([1, scale_tick_width, scale_tick_height]);
        }
}

module optical_strip_positive() {
    optical_rail_positive();
    for (i = [0:beam_count - 1]) {
        optical_module_carrier_positive(beam_first_height + i * beam_pitch);
        optical_module_positive(beam_first_height + i * beam_pitch);
    }
}

function sensor_film_y() =
    -net_rail_depth / 2 - sensor_front_offset - sensor_depth - sensor_film_depth;

module pvdf_film_positive(x_position) {
    color("black")
        translate([x_position - sensor_film_length / 2,
                   sensor_film_y(), net_height - 1])
            cube([sensor_film_length, sensor_film_depth, sensor_film_height]);
}

module sensor_clamp_lip_positive(x_position) {
    film_y = sensor_film_y();
    color("mediumpurple")
        for (side = [-1, 1]) {
            translate([x_position + side * (sensor_film_length / 2 - sensor_clamp_tab_width),
                       film_y - 0.5, net_height - 1])
                cube([sensor_clamp_tab_width, sensor_clamp_tab_depth,
                      sensor_clamp_tab_height]);
        }
}

module sensor_mount_body_positive(x_position) {
    color("mediumpurple")
        translate([x_position - sensor_length / 2,
                   -net_rail_depth / 2 - sensor_front_offset - sensor_depth,
                   net_height - 1])
            cube([sensor_length, sensor_depth, sensor_height]);
    // 连接夹臂跨过前向间隙，把传感器座真正接到网顶承载条前侧。
    color("mediumpurple")
        translate([x_position - 8,
                   -net_rail_depth / 2 - sensor_front_offset,
                   net_height - 1])
            cube([16, sensor_front_offset, sensor_height]);
}

module sensor_mount_positive(x_position) {
    sensor_mount_body_positive(x_position);
    pvdf_film_positive(x_position);
    sensor_clamp_lip_positive(x_position);
}

module sensor_mount(side = 1) {
    sided(side) sensor_mount_positive(sensor_x);
}

module sensor_mount_body(side = 1) {
    sided(side) sensor_mount_body_positive(sensor_x);
}

module net_rail_segment_positive(index = 0) {
    color("white")
        difference() {
            translate([net_rail_segment_start(index),
                       -net_rail_depth / 2,
                       net_height - net_rail_height])
                cube([net_rail_segment_length, net_rail_depth, net_rail_height]);
            // 拼接片的两个 M3 孔分别落在相邻的两段承载条中。
            if (index > 0) {
                translate([net_rail_splice_center(index - 1) + 20, 0,
                           net_height - net_rail_height - 1])
                    cylinder(d = net_rail_splice_hole_d,
                             h = net_rail_height + 2);
            }
            if (index < net_rail_segment_count - 1) {
                translate([net_rail_splice_center(index) - 20, 0,
                           net_height - net_rail_height - 1])
                    cylinder(d = net_rail_splice_hole_d,
                             h = net_rail_height + 2);
            }
        }
}

module net_rail_splice_positive(index = 0) {
    seam_x = net_rail_splice_center(index);
    color("lightgray")
        difference() {
            translate([seam_x - net_rail_splice_plate_length / 2,
                       -net_rail_splice_plate_depth / 2,
                       net_height - net_rail_height - net_rail_splice_plate_t])
                cube([net_rail_splice_plate_length,
                      net_rail_splice_plate_depth,
                      net_rail_splice_plate_t]);
            for (hole_x = [-20, 20]) {
                translate([seam_x + hole_x, 0,
                           net_height - net_rail_height - 1])
                    cylinder(d = net_rail_splice_hole_d,
                             h = net_rail_splice_plate_t + 2);
            }
        }
}

module net_rail_saddle_positive() {
    inner_face_x = post_center_x - post_body_width / 2;
    base_x = inner_face_x - net_rail_saddle_overlap;
    base_z = net_height - net_rail_height - net_rail_saddle_height;
    color("lightgray") {
        // 承托座向内伸入网顶承载条，并向外与立柱相交，形成明确的受力路径。
        translate([base_x, -net_rail_saddle_depth / 2, base_z])
            cube([net_rail_saddle_width, net_rail_saddle_depth,
                  net_rail_saddle_height]);
        // 立柱侧端挡住承载条，限制沿 x 方向滑出；不改变网顶高度基准。
        translate([inner_face_x, -net_rail_saddle_depth / 2,
                   net_height - net_rail_height])
            cube([net_rail_saddle_stop_t, net_rail_saddle_depth,
                  net_rail_height]);
    }
}

module net_rail_saddle(side = 1) {
    sided(side) net_rail_saddle_positive();
}

module net_rail() {
    // 三段带 20 mm 搭接，打印长度约 536 mm；实际装配时用下方拼接片/螺钉
    // 或铝型材替代件把搭接处锁紧。整体 PART 仍用于连续网顶关系预览。
    for (index = [0:net_rail_segment_count - 1]) {
        net_rail_segment_positive(index);
    }
    for (index = [0:net_rail_segment_count - 2]) {
        net_rail_splice_positive(index);
    }
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

module reference_pin_positive() {
    color("black")
        translate([optical_rail_x + optical_rail_depth / 2,
                   -reference_carriage_depth / 2,
                   beam_z(reference_height)])
            rotate([90, 0, 0])
                cylinder(d = reference_pin_d, h = reference_pin_length,
                         center = true);
}

module reference_carriage_body_positive() {
    carriage_center_x = optical_rail_x + optical_rail_depth / 2;
    carriage_z = beam_z(reference_height) - reference_carriage_height / 2;
    color("seagreen") {
        difference() {
            union() {
                // 端座位于导轨前侧；可拆销从端座前表面穿过端座和导轨，
                // 只能落在光学导轨的 10 mm 贯穿孔档位。
                translate([carriage_center_x - reference_carriage_width / 2,
                           -optical_rail_width / 2 - reference_carriage_depth,
                           carriage_z])
                    cube([reference_carriage_width, reference_carriage_depth,
                          reference_carriage_height]);
                // 小桥把线端带到网面前侧的参考线位置，并与销孔保持一体。
                translate([carriage_center_x - 4,
                           -optical_rail_width / 2 - reference_carriage_depth,
                           beam_z(reference_height) - 1.5])
                    cube([8, optical_rail_width / 2 + reference_carriage_depth - 1.1, 3]);
            }
            // 打印间隙孔沿 y 方向贯穿端座/桥件；光学导轨本体的孔由
            // optical_rail_positive() 提供，装配后两孔共轴。
            translate([carriage_center_x, -reference_carriage_depth / 2,
                       beam_z(reference_height)])
                rotate([90, 0, 0])
                    cylinder(d = reference_pin_bore_d,
                             h = reference_pin_length + 2,
                             center = true);
        }
    }
}

module reference_carriage_positive() {
    reference_carriage_body_positive();
    reference_pin_positive();
}

module reference_carriage(side = 1) {
    sided(side) reference_carriage_positive();
}

module reference_carriage_body(side = 1) {
    sided(side) reference_carriage_body_positive();
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
        net_rail_saddle_positive();
        optical_strip_positive();
    }
}

module parameter_probe() {
    echo(str("NETSTAND_PARAM table_width=", table_width));
    echo(str("NETSTAND_PARAM table_thickness=", table_thickness));
    echo(str("NETSTAND_PARAM net_height=", net_height));
    echo(str("NETSTAND_PARAM net_rail_height=", net_rail_height));
    echo(str("NETSTAND_PARAM net_rail_depth=", net_rail_depth));
    echo(str("NETSTAND_PARAM beam_count=", beam_count));
    echo(str("NETSTAND_PARAM beam_first_height=", beam_first_height));
    echo(str("NETSTAND_PARAM beam_last_height=", beam_last_height));
    echo(str("NETSTAND_PARAM beam_pitch=", beam_pitch));
    echo(str("NETSTAND_PARAM post_center_x=", post_center_x));
    echo(str("NETSTAND_PARAM post_body_width=", post_body_width));
    echo(str("NETSTAND_PARAM post_body_depth=", post_body_depth));
    echo(str("NETSTAND_PARAM post_bottom=", post_bottom));
    echo(str("NETSTAND_PARAM net_span=", net_span));
    echo(str("NETSTAND_PARAM post_segment_count=", post_segment_count));
    echo(str("NETSTAND_PARAM post_segment_length=", post_segment_length));
    echo(str("NETSTAND_PARAM post_joint_gap=", post_joint_gap));
    echo(str("NETSTAND_PARAM net_rail_segment_count=", net_rail_segment_count));
    echo(str("NETSTAND_PARAM net_rail_segment_length=", net_rail_segment_length));
    echo(str("NETSTAND_PARAM net_rail_splice_overlap=", net_rail_splice_overlap));
    echo(str("NETSTAND_PARAM net_rail_splice_plate_length=", net_rail_splice_plate_length));
    echo(str("NETSTAND_PARAM net_rail_splice_hole_d=", net_rail_splice_hole_d));
    echo(str("NETSTAND_PARAM net_rail_saddle_overlap=", net_rail_saddle_overlap));
    echo(str("NETSTAND_PARAM net_rail_saddle_width=", net_rail_saddle_width));
    echo(str("NETSTAND_PARAM net_rail_saddle_depth=", net_rail_saddle_depth));
    echo(str("NETSTAND_PARAM net_rail_saddle_height=", net_rail_saddle_height));
    echo(str("NETSTAND_PARAM post_top=", post_top));
    echo(str("NETSTAND_PARAM post_offset=", post_offset));
    echo(str("NETSTAND_PARAM sensor_x=", sensor_x));
    echo(str("NETSTAND_PARAM sensor_film_length=", sensor_film_length));
    echo(str("NETSTAND_PARAM sensor_film_depth=", sensor_film_depth));
    echo(str("NETSTAND_PARAM sensor_clamp_tab_width=", sensor_clamp_tab_width));
    echo(str("NETSTAND_PARAM clamp_pad_x=", clamp_pad_x));
    echo(str("NETSTAND_PARAM clamp_pad_depth=", clamp_pad_depth));
    echo(str("NETSTAND_PARAM clamp_pad_outer_x=", clamp_pad_outer_x));
    echo(str("NETSTAND_PARAM clamp_screw_x=", clamp_screw_x));
    echo(str("NETSTAND_PARAM clamp_screw_d=", clamp_screw_d));
    echo(str("NETSTAND_PARAM clamp_screw_pitch=", clamp_screw_pitch));
    echo(str("NETSTAND_PARAM clamp_threaded_boss_d=", clamp_threaded_boss_d));
    echo(str("NETSTAND_PARAM clamp_threaded_boss_h=", clamp_threaded_boss_h));
    echo(str("NETSTAND_PARAM clamp_top_pad_x=", clamp_top_pad_x));
    echo(str("NETSTAND_PARAM clamp_top_pad_width=", clamp_top_pad_width));
    echo(str("NETSTAND_PARAM clamp_top_pad_depth=", clamp_top_pad_depth));
    echo(str("NETSTAND_PARAM clamp_top_pad_t=", clamp_top_pad_t));
    echo(str("NETSTAND_PARAM clamp_screw_top_z=", clamp_screw_top_z));
    echo(str("NETSTAND_PARAM clamp_screw_bottom_z=", clamp_screw_bottom_z));
    echo(str("NETSTAND_PARAM clamp_screw_length=", clamp_screw_length));
    echo(str("NETSTAND_PARAM clamp_screw_tip_radius=", clamp_screw_tip_radius));
    echo(str("NETSTAND_PARAM clamp_screw_to_knob_top=", clamp_screw_to_knob_top));
    echo(str("NETSTAND_PARAM clamp_nut_af=", clamp_nut_af));
    echo(str("NETSTAND_PARAM clamp_nut_h=", clamp_nut_h));
    echo(str("NETSTAND_PARAM clamp_nut_clearance=", clamp_nut_clearance));
    echo(str("NETSTAND_PARAM clamp_nut_pocket_af=", clamp_nut_pocket_af));
    echo(str("NETSTAND_PARAM clamp_nut_pocket_depth=", clamp_nut_pocket_depth));
    echo(str("NETSTAND_PARAM clamp_body_nut_z=", clamp_body_nut_z));
    echo(str("NETSTAND_PARAM clamp_knob_top_z=", clamp_knob_top_z));
    echo(str("NETSTAND_PARAM clamp_knob_bottom_z=", clamp_knob_bottom_z));
    echo(str("NETSTAND_PARAM clamp_knob_nut_z=", clamp_knob_nut_z));
    echo(str("NETSTAND_PARAM clamp_lower_arm_bottom_z=", clamp_lower_arm_bottom_z));
    echo(str("NETSTAND_PARAM clamp_lower_arm_top_z=", clamp_lower_arm_top_z));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_top_z=", clamp_pressure_pad_top_z));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_bottom_z=", clamp_pressure_pad_bottom_z));
    echo(str("NETSTAND_PARAM optical_locating_hole_d=", optical_locating_hole_d));
    echo(str("NETSTAND_PARAM optical_rail_width=", optical_rail_width));
    echo(str("NETSTAND_PARAM optical_module_depth=", optical_module_depth));
    echo(str("NETSTAND_PARAM optical_module_width=", optical_module_width));
    echo(str("NETSTAND_PARAM optical_module_height=", optical_module_height));
    echo(str("NETSTAND_PARAM optical_rail_depth=", optical_rail_depth));
    echo(str("NETSTAND_PARAM optical_beam_edge_overlap=", optical_beam_edge_overlap));
    echo(str("NETSTAND_PARAM optical_beam_axis_x=", optical_beam_axis_x));
    echo(str("NETSTAND_PARAM optical_rail_x=", optical_rail_x));
    echo(str("NETSTAND_PARAM optical_carrier_clearance=", optical_carrier_clearance));
    echo(str("NETSTAND_PARAM optical_carrier_wall=", optical_carrier_wall));
    echo(str("NETSTAND_PARAM optical_carrier_z_wall=", optical_carrier_z_wall));
    echo(str("NETSTAND_PARAM optical_carrier_back_depth=", optical_carrier_back_depth));
    echo(str("NETSTAND_PARAM optical_carrier_front_depth=", optical_carrier_front_depth));
    echo(str("NETSTAND_PARAM optical_carrier_width=", optical_carrier_width));
    echo(str("NETSTAND_PARAM optical_carrier_height=", optical_carrier_height));
    echo(str("NETSTAND_PARAM optical_carrier_slot_d=", optical_carrier_slot_d));
    echo(str("NETSTAND_PARAM optical_carrier_slot_length=", optical_carrier_slot_length));
    echo(str("NETSTAND_PARAM optical_module_index=", optical_module_index));
    echo(str("NETSTAND_PARAM reference_pin_d=", reference_pin_d));
    echo(str("NETSTAND_PARAM reference_pin_bore_d=", reference_pin_bore_d));
    echo(str("NETSTAND_PARAM reference_pin_length=", reference_pin_length));
    echo(str("NETSTAND_PARAM reference_carriage_depth=", reference_carriage_depth));
    cube([0.2, 0.2, 0.2]);
}

if (PART == "assembly") {
    table_preview();
    net_panel();
    net_rail();
    stand(1);
    stand(-1);
    // PVDF 座位于全宽网顶承载条的中段，只有在完整装配中才有真实承载关系。
    sensor_mount(1);
    sensor_mount(-1);
    beam_markers();
    reference_line();
    reference_carriage(1);
    reference_carriage(-1);
} else if (PART == "left_stand") {
    stand(-1);
} else if (PART == "right_stand") {
    stand(1);
} else if (PART == "post") {
    sided(default_side) post_positive();
} else if (PART == "post_segment") {
    sided(default_side) post_segment_positive(post_segment_index);
} else if (PART == "lower_stand_segment") {
    sided(default_side) lower_stand_segment_positive();
} else if (PART == "post_joint_sleeve") {
    sided(default_side) post_joint_sleeve_positive();
} else if (PART == "post_joint_key") {
    sided(default_side) post_joint_key_positive();
} else if (PART == "table_clamp") {
    sided(default_side) table_clamp_positive();
} else if (PART == "table_clamp_section") {
    sided(default_side) table_clamp_section_positive();
} else if (PART == "table_clamp_body") {
    sided(default_side) table_clamp_body_positive();
} else if (PART == "clamp_top_pad") {
    sided(default_side) clamp_top_pad_positive();
} else if (PART == "clamp_pressure_pad") {
    sided(default_side) clamp_pressure_pad_positive();
} else if (PART == "clamp_screw") {
    sided(default_side) clamp_screw_positive();
} else if (PART == "clamp_body_nut") {
    sided(default_side) clamp_body_nut_positive();
} else if (PART == "clamp_knob") {
    sided(default_side) clamp_knob_positive();
} else if (PART == "clamp_knob_nut") {
    sided(default_side) clamp_knob_nut_positive();
} else if (PART == "net") {
    net_panel();
} else if (PART == "net_rail") {
    net_rail();
} else if (PART == "net_rail_segment") {
    net_rail_segment_positive(rail_segment_index);
} else if (PART == "net_rail_splice") {
    net_rail_splice_positive(rail_splice_index);
} else if (PART == "net_rail_saddle") {
    net_rail_saddle(default_side);
} else if (PART == "optical_rail") {
    sided(default_side) optical_rail_positive();
} else if (PART == "optical_strip") {
    sided(default_side) optical_strip_positive();
} else if (PART == "optical_module_carrier") {
    sided(default_side)
        optical_module_carrier_positive(
            beam_first_height + optical_module_index * beam_pitch);
} else if (PART == "sensor_mount") {
    sensor_mount(default_side);
} else if (PART == "sensor_mount_body") {
    sensor_mount_body(default_side);
} else if (PART == "pvdf_film") {
    sided(default_side) pvdf_film_positive(sensor_x);
} else if (PART == "sensor_clamp_lip") {
    sided(default_side) sensor_clamp_lip_positive(sensor_x);
} else if (PART == "reference_carriage") {
    reference_carriage(default_side);
} else if (PART == "reference_carriage_body") {
    reference_carriage_body(default_side);
} else if (PART == "reference_pin") {
    sided(default_side) reference_pin_positive();
} else if (PART == "calibration_gauge") {
    calibration_gauge();
} else if (PART == "parameter_probe") {
    parameter_probe();
} else {
    assert(false, str("unknown PART: ", PART));
}
