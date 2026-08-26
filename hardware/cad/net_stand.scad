// 乒乓智配：内置式球网支架与过网高度检测结构
// 当前主线 CAD。它替换传统球网和原有球网立柱，不再外挂到旧立柱上。
// 单位：mm；x=球台宽度方向，y=球台长度方向，z=球台台面以上。
//
// 预览/导出：
//   PART="assembly"          含球台截面、网、双侧支架和传感器的装配预览
//   PART="left_stand"         左侧立柱/桌下夹持/STG 托架结构检查件
//   PART="right_stand"        右侧立柱/桌下夹持/STG 托架结构检查件
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
//   PART="clamp_screw"        M8×1.25 金属螺杆装配占位（非打印件，顶端圆头）
//   PART="clamp_body_nut"     固定在下臂螺母座中的 M8 螺母装配占位（标准件）
//   PART="clamp_knob"         手拧旋钮（含两枚 M8 对锁螺母捕获窝）
//   PART="clamp_knob_nut"     旋钮内捕获的两枚 M8 对锁螺母（标准件）
//   PART="net"                球网/网布装配占位（非打印件）
//   PART="net_rail"           网顶承载条
//   PART="net_rail_segment"   单段网顶承载条（由 rail_segment_index 选择）
//   PART="net_rail_splice"    网顶承载条拼接片（由 rail_splice_index 选择）
//   PART="net_rail_saddle"    立柱内侧网顶承托/端部限位座
//   PART="optical_rail"       旧版 10 路离散红外模块导轨（兼容诊断件）
//   PART="optical_strip"      旧版 10 路离散红外模块装配预览（兼容诊断件）
//   PART="optical_module_carrier" 旧版单个光学模块载台（兼容诊断件）
//   PART="m6_sensor_rail"     旧版 M6×0.75 直角十路单竖条/7 字座（兼容诊断件）
//   PART="m6_sensor_test_coupon" 旧版单 M6 7 字座试装样件（兼容诊断件）
//   PART="m6_sensor_array"    当前十路 M6 发射/接收器与长条主体装配占位
//   PART="m6_detector_fit_probe" 仅验证长条主体与真实 L 型激光头的 2 mm 卡入关系
//   PART="m6_detector_body"   当前 6061-T6 长条主体（45°斜向六角沉孔/短过孔）
//   PART="m6_detector_shell_front" PETG x- 光学端前盖候选
//   PART="m6_detector_shell_rear" PETG x+ 线缆端后盖候选
//   PART="m6_detector_bottom_cover" PETG 底盖候选
//   PART="m6_detector_exploded" 右/左侧检测器非剖切爆炸图
//   PART="m6_detector_support" 当前金属 90° 支撑件
//   PART="m6_detector_mount" 当前主体/器件/完整前后底盖/竖直采购球头/支撑装配
//   PART="m6_mount_adapter"   当前铝合金基座到网夹/立柱的竖直安装板
//   PART="m6_detector_backplate" 兼容旧调用名；输出当前后盖
//   PART="m6_ballhead"        13 mm 采购球头云台竖直姿态占位（非打印件）
//   PART="m6_ballhead_mount" 兼容旧调用名；输出当前主体支撑装配
//   PART="m6_gimbal"          兼容旧调用名；实际输出当前竖直球头装配
//   PART="stg120_outer_carrier" STG-120ML 外侧光纤头包络/安装托架
//   PART="stg120_center_bridge" STG-120ML 中央背靠背分段支撑桥
//   PART="stg120_preview"      STG-120ML 双分段光束装配预览（非打印件）
//   PART="sensor_mount"       单侧网顶 PVDF 夹片安装座
//   PART="sensor_mount_body"   单侧可打印 PVDF 安装座本体（不含薄膜/压片）
//   PART="pvdf_film"          PVDF 薄膜包络（非打印件）
//   PART="sensor_clamp_lip"   PVDF 薄膜两侧可拆压片
//   PART="reference_carriage" 旧版参考线端座与定位销（兼容诊断件）
//   PART="reference_carriage_body" 旧版可打印参考线端座（兼容诊断件）
//   PART="reference_pin"      旧版参考线弹簧销占位（兼容诊断件）
//   PART="calibration_gauge"  STG-120ML 3.87 mm 光点高度标定规
//   PART="parameter_probe"    输出验证脚本读取的参数清单
//   SIDE=0                    使用默认右侧；SIDE=1/-1 显式选择左右镜像
//
// 说明：当前光学主线是用户提供资料中的 M6 直角对射器件：每侧十个
// M6×0.75 发射/接收器件装入一根长条形 6061-T6 铝合金主体。光学轴沿 x；
// L 型器件的蓝色尾线支路局部朝 z-，整件绕光束 x 轴旋转 -45°，从主体
// x+（右）/x-（左）的后方装入。主体按首样复核采用 x=10 mm 厚、y=56 mm
// 宽、z=216 mm 高的竖直承载条，不再用只能当薄背条的 6×18 mm 截面；十个通道中心
// 以 20 mm 节距从过网高度 +10 mm 排到 +190 mm；
// 右侧器件的外侧装入方向为 x+，左侧由 SIDE 镜像后外侧装入方向为 x-。光学
// 头部穿过主体的头部让位孔，线缆留在主体外侧，不在铝材里挖线束槽；x 向
// 浅六角座只卡住真实金属头的六角外形，M6 外丝直接穿过主体，在外表面只
// 安装一枚原配 5 mm 螺帽，14 mm 外丝仍保留足够的外露长度。
// 当前装配已包含 PETG 前盖、后盖和底盖候选件；铝主体在 y- 边一体做成
// T 形尾座，尾座向本侧外向 x 延长至少 10 mm，并在 x+ 端攻 M8×1.25
// 盲牙；左侧镜像后即为 x- 端。采购 13 mm 球头的 M8 外牙直接拧入铝尾座，
// 再经金属 90° 支撑件和竖直网夹适配板连接到网架。铝合金件、M6 器件、球头、
// PVDF 薄膜、网布、金属螺杆和夹持软垫均为外购/机加工/装配边界，不能混入
// PETG 打印清单。
// M8 螺杆和螺母只在装配/剖面和 PART 单件预览中显示；STG-120ML 光纤头
// 保留为历史诊断件，不再作为当前装配主线。
// 前后盖沿 x 分成两件，均从 z+ 套入主体；底盖向下独立安装。沉头螺钉只是
// 盖件到主体的固定件，真正承力路径是“传感器六角/螺杆 -> 铝合金主体 ->
// 铝合金 T 尾座/M8 内丝 -> 金属 90° 支撑 -> 竖直球头/网夹适配板 -> 网架”。线缆孔为开放孔，
// 没有密封设计，不能宣称防水。该文件验证机械意图与参数关系，不等同于最终
// PETG 打印强度、球台兼容性、实物螺纹/光学精度或 NPN 电气验收。

$fn = 48;

PART = "assembly";
SIDE = 0;

// 球台与传统网架接口
table_width = 1525;
table_depth_preview = 500;
table_thickness = 25;
table_edge_x = table_width / 2;
post_body_width = 28;
post_body_depth = 38;
// ITTF 现行规则要求网柱外侧边界在球台侧线外 152.5 mm；这里把
// 152.5 mm 作为网架外边界，而不是把网柱中心误当成外伸量。28 mm
// 立柱的中心偏移因此为 152.5 - 14 = 138.5 mm。这样网顶承载条和
// 网布的名义总宽为 1830 mm，左右各比 1525 mm 球台多 152.5 mm。
net_post_outboard_extension = 152.5;
// 立柱外置 138.5 mm，使光学导轨仍可从立柱内侧悬到台边；模块镜头
// 轴线覆盖台面边缘，而不会嵌入实心立柱。
post_offset = 138.5;
post_center_x = table_edge_x + post_offset;
// C 形夹下方采用前后两片三角侧肋。起点位于可动压块外侧，底边与下臂
// 重叠，外侧竖边与 C 形外墙重叠，斜边朝台底收口；它不是放在上夹板外侧
// 的装饰三角形。真实 PETG 材料、层向和夹紧力仍需首样验证。
clamp_gusset_t_y = 10;
// Gusset start is measured outboard of the movable pressure-pad edge so the
// side cheek reinforces the lower arm without entering the pad's travel space.
clamp_gusset_start_inset = 6;
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

// 当前 M6 光电器件阵列。用户提供的资料明确给出“直角 M6”、安装螺纹
// M6×0.75、头部高度约 8 mm、水平外丝段 14 mm、总水平包络约 20 mm、
// 检测距离 20 m、NPN 选项。注意：水平 x 轴是光学轴和 M6 外丝轴；蓝色
// 护套/尾线从 L 头的另一条支路沿局部 z- 出线，绝不能把它画成 x 轴圆柱。
// 未旋转时这条尾线支路朝 z-，再绕光轴 x 旋转 -45°，落向 y-/z-，给相邻
// 20 mm 通道让线。当前主体采用一根能包络头部、线缆护套和装配余量的连续
// 竖直铝条，在十个高度加工水平光学让位孔、浅 x 向六角座和斜向尾线让位；前后 PETG 壳体按
// x- 光学端 / x+ 线缆端分段，并共享 y± 两条边槽。
m6_sensor_count = 10;
m6_sensor_center_pitch = 20;
m6_sensor_first_height = beam_first_height;
m6_sensor_thread_d = 6;
m6_sensor_thread_pitch = 0.75;
m6_sensor_tap_visual_d = 5.25;
m6_sensor_head_length_x = 6;
m6_sensor_head_width_y = 10;
m6_sensor_head_height_z = 8;
m6_sensor_head_hex_af = 8;
m6_sensor_face_d = 3;
m6_sensor_body_d = 6;
// The M6 threaded optical barrel is hollow.  This is a visual/first-article
// aperture placeholder; confirm the real clear bore from the purchased SKU.
m6_sensor_optical_bore_d = 3;
// Kept under the old name for manifest compatibility. It is a legacy envelope
// value, not the x-axis direction of the blue cable.
m6_sensor_body_length = 22;
m6_sensor_mount_x_offset = 3.25;
// Compatibility name retained because old manifests call this the mounting
// stem. In the purchased L-shaped M6 part it is the horizontal threaded section.
m6_sensor_mount_stem_length = 14;
m6_sensor_cable_guard_length = 10;
m6_sensor_cable_preview_length = 18;
m6_sensor_cable_d = 3;
m6_sensor_mount_plane_offset_z = 8;
m6_sensor_thread_engagement = 5;
m6_sensor_lock_nut_af = 10;
m6_sensor_lock_nut_h = 5;
m6_sensor_nut_pocket_clearance = 0.35;
m6_sensor_roll_deg = -45;
m6_sensor_guard_outer_d = 15;
m6_sensor_guard_h = 5;
// 单件试装样件只验证真实传感器、螺母防转和线缆让位，不进入 26 件正式
// PETG 拼盘；因此用比 M6 外螺纹略大的通孔，避免把未确认的攻牙规格冻结在
// 打印件里。正式铝条仍按卖家实物决定 M6×0.75 攻牙或通孔+螺母。
m6_sensor_test_coupon_backbone_h = 24;
m6_sensor_test_coupon_clearance_d = m6_sensor_thread_d + 0.5;
m6_sensor_test_coupon_guard_overlap = 0.2;
// Keep the coupon intentionally short and local: it is a fit check for one
// real sensor and one short 7-shaped seat, not a print of the full aluminum bar.
m6_sensor_test_coupon_tab_min_local_x = -12.5;
m6_sensor_test_coupon_mount_hole_local_x = -8.5;
m6_rail_t = 8;
m6_sensor_rail_post_clearance = 1;
m6_sensor_body_clearance_d = m6_sensor_body_d + 0.8;
m6_rail_width_y = 42;
m6_rail_tab_t = 6;
m6_rail_tab_width_y = 12;
m6_sensor_lane_offset_y = 9;
// Adjacent guards are axis-aligned 15 mm squares on the alternating y lanes.
// Keep both the actual y/z square gaps and a diagonal center-distance guard
// explicit so a future pitch or lane change cannot silently make the ten
// lock-nut pockets collide.
m6_adjacent_channel_center_distance_yz =
    sqrt(pow(2 * m6_sensor_lane_offset_y, 2) +
         pow(m6_sensor_center_pitch, 2));
m6_adjacent_guard_gap_y =
    2 * m6_sensor_lane_offset_y - m6_sensor_guard_outer_d;
m6_adjacent_guard_gap_z =
    m6_sensor_center_pitch - m6_sensor_guard_h;
m6_rail_end_margin = 12;
// 竖直传感器条与后背板的实体连接：背骨保留 4 个 M4×0.7 候选盲牙，
// 后背板用中心 M6 安装孔和两枚防转孔承接采购的 13 mm 球头。孔位避开
// 十路传感器/线缆让位孔，并保留铝材底壁；M4/M6 连接件因此成为阵列到
// 球头云台的明确承力件。
m6_rail_mount_clearance_d = 4.5;
m6_rail_mount_tap_d = 3.3;
m6_rail_mount_tap_depth = 6;
m6_rail_mount_hole_y = 16;
m6_rail_mount_z_offset = 40;
m6_rail_mount_bolt_length = 12;
m6_detector_backplate_t = 8;
m6_detector_backplate_width_y = 52;
m6_detector_backplate_height_z =
    (m6_sensor_count - 1) * m6_sensor_center_pitch +
    2 * m6_rail_end_margin + 16;
m6_detector_backplate_lock_hole_y = 18;
m6_detector_backplate_mount_clearance_d = 10.0;
m6_detector_backplate_anti_rotation_d = 4.5;
m6_ballhead_ball_d = 13;
m6_ballhead_housing_d = 28;
m6_ballhead_housing_length_x = 26;
m6_ballhead_base_d = 32;
m6_ballhead_base_t = 8;
m6_ballhead_sensor_stud_d = 8;
m6_ballhead_sensor_stud_length = 16;
m6_ballhead_net_stud_d = 8;
m6_ballhead_net_stud_length = 28;
m6_ballhead_tilt_range_deg = 90;
m6_ballhead_rotation_range_deg = 360;
m6_ballhead_mount_clearance_d = 6.5;
m6_rail_length_z =
    (m6_sensor_count - 1) * m6_sensor_center_pitch + 2 * m6_rail_end_margin;
m6_array_bottom_z =
    net_height + m6_sensor_first_height - m6_rail_end_margin;
m6_array_top_z = m6_array_bottom_z + m6_rail_length_z;
m6_array_center_z = (m6_array_bottom_z + m6_array_top_z) / 2;
m6_post_mount_hole_z = m6_array_center_z;

// 四层铝合金微调机构：固定适配板、水平 z 轴偏航双层转台、固定外叉架
// +绕 y 轴转动的内框，以及绕光轴 x 轴转动的滚转盘。锁紧槽负责粗调，
// M4 顶丝负责切向微调，最后由枢轴/锁紧螺钉承受工作载荷；默认角度为 0，
// 仅显示名义对准状态。
m6_mount_plate_t = 6;
m6_mount_plate_width_y = 56;
m6_mount_plate_height_z = m6_rail_length_z + 24;
m6_mount_slot_length = 12;
// The fixed adapter is not allowed to float against the upright.  These two
// z-slots pass through the current 28 x 38 mm net-clamp upright and accept
// M6 through-bolts; the real commercial clamp still has to be measured before
// this pattern is treated as a production interface.
m6_post_mount_clearance_d = 6.5;
m6_post_mount_hole_y = 10;
m6_post_mount_bolt_length = 45;
// 偏航必须绕竖直 z 轴，故在阵列下方增加水平转台；固定适配板承接
// 下层转台，转台上层带着竖直承载板和后续俯仰/滚转机构一起转动。
m6_yaw_stage_t = 6;
m6_yaw_stage_radius = 82;
m6_yaw_slot_radius = 64;
m6_yaw_stage_z = m6_array_bottom_z - 4;
m6_yaw_plate_t = 6;
m6_yaw_slot_length = 12;
m6_yaw_range_deg = 4;
// 外叉架必须包住 Ø110 滚转盘；原来的 56 mm 叉宽会与滚转盘相交，
// 不是可装配的叉架。内框留出 4 mm 径向间隙，并在后侧用中心脊承接
// x 轴滚转枢轴。
m6_pitch_yoke_t = 8;
m6_pitch_yoke_width_y = 158;
m6_pitch_yoke_length_x = 18;
m6_pitch_yoke_foot_t = 8;
m6_pitch_frame_t = 6;
m6_pitch_frame_outer_width_y = 140;
m6_pitch_frame_window_width_y = 118;
// The pitch frame follows the 20 mm M6 array: 216 mm body height plus 2 mm
// clearance each side in the window and an 8 mm outer rim.
m6_pitch_frame_outer_height_z = 236;
m6_pitch_frame_window_height_z = 220;
m6_pitch_frame_spine_width_y = 12;
m6_pitch_frame_hub_d = 16;
m6_pitch_pivot_offset_z = 26;
m6_pitch_lock_offset_z = 44;
m6_pitch_lock_tap_d = 5;
m6_pitch_lock_tap_depth = 8;
m6_pitch_slot_length = 12;
m6_pitch_range_deg = 4;
m6_roll_plate_t = 6;
// The four rail-to-roll M4 holes sit at y=±16, z=±40 relative to the
// roll center.  Ø110 leaves a positive edge margin around their Ø4.5
// clearance holes and also keeps the ±44 mm pitch lock-slot stations on
// the same machined plate; Ø46 would put the M4 holes outside the disk.
m6_roll_plate_d = 110;
m6_roll_slot_length = 10;
m6_roll_range_deg = 4;
// 偏航/俯仰使用 M8 枢轴；滚转中心穿过梳齿背骨，改用较小的 Ø6.5
// 通孔，避开相邻 M6 器件的 Ø10 线缆/本体让位孔。滚转锁紧槽在后侧
// 中心脊中攻 M5 盲牙，不能把传感器背骨当作无支撑的装饰板。
m6_pivot_d = 8.5;
m6_roll_pivot_d = 6.5;
m6_roll_lock_tap_d = 5;
m6_roll_lock_tap_depth = 8;
m6_roll_pivot_bolt_length = 32;
m6_stage_bolt_d = 6.5;
// 固定适配板与偏航下转台的明确承力连接：适配板开 M6 通孔，
// 下转台从 +x/网夹侧加工 M6×1.0 盲牙；不能只依靠两个零件相交。
m6_yaw_base_mount_clearance_d = 6.5;
m6_yaw_base_mount_tap_d = 5;
m6_yaw_base_mount_tap_depth = 10;
m6_yaw_base_mount_hole_y = 24;
m6_yaw_base_mount_bolt_length = 16;
// 偏航上转台与竖直承载板采用两枚 M5×0.8 竖向螺钉固定；偏航弧槽
// 只夹上下转台，不把承载板的连接力留给接触面。
m5_yaw_carrier_mount_clearance_d = 5.5;
m5_yaw_carrier_mount_tap_d = 4.2;
m5_yaw_carrier_mount_tap_depth = 5;
m5_yaw_carrier_mount_hole_y = 20;
m5_yaw_carrier_mount_bolt_length = 12;
m6_fine_adjuster_d = 4;
m6_fine_adjuster_length = 22;
// The yaw screw is supported by a fixed reaction ear attached to the lower
// yaw plate.  It is raised above the lower plate so its tip actually contacts
// the moving upper plate edge rather than disappearing into the lower plate.
m6_yaw_adjuster_block_width_x = 12;
m6_yaw_adjuster_block_depth_y = 8;
m6_yaw_adjuster_block_height_z = 18;
m6_yaw_adjuster_foot_inset_y = 6;
m6_yaw_adjuster_tap_d = 3.3;
m6_yaw_adjuster_tap_depth = 8;
m6_yaw_adjuster_tip_overtravel_y = 0.5;
// The pitch screw reacts against a fixed crossbar on the outer yoke; the
// roll screw reacts against a small fixed arm on the inner frame and kisses
// the roll-disc rim instead of crossing the disc face.
m6_pitch_adjuster_offset_z = 20;
m6_pitch_adjuster_bridge_t = 6;
m6_roll_adjuster_offset_z = 20;
m6_roll_adjuster_arm_depth_y = 8;
m6_roll_adjuster_arm_t = 6;
m6_roll_adjuster_clearance_y = 2;
m6_roll_adjuster_length = 16;
m6_yaw_angle = 0;
m6_pitch_angle = 0;
m6_roll_angle = 0;

// 当前长条主体/前后盖方案（v0.3）。这是独立于旧版梳齿/三轴参数的主线；
// 旧参数保留给历史 PART 和既有验证脚本，不再代表现行装配。
// 机械契约：主体为 6061-T6 铝合金机加工件；前盖、后盖、底盖为 PETG
// 尺寸样件/候选打印件；无密封。主体位于沿光束 x 轴拆分的前后壳之间，
// 前盖在光学端 x-、后盖在线缆端 x+；两盖从 z+ 套入，底盖从 z-贴合。
// M3/M4 沉头螺钉只锁盖件，传感器和主要支撑载荷不通过 PETG 舌片闭环。
m6_detector_body_depth_y = 56.0;
m6_detector_body_center_y = 0.0;
m6_detector_body_length_x = 10.0;
m6_detector_body_margin_z = 18;
m6_detector_body_front_margin_x = 1;
// First article scope: model only the long rectangular aluminum bar and the
// purchased sensor envelope.  The sensor is inserted from the outward x face
// until its AF8 head reaches the stop, then another 2 mm of that head remains
// captured inside the bar.  One supplied nut is shown on the smooth opposite
// face; covers, cable channels, brackets, and gimbals remain outside this probe.
m6_detector_fit_head_length_x = m6_sensor_head_length_x;
m6_detector_fit_head_width_y = m6_sensor_head_width_y;
m6_detector_fit_head_height_z = m6_sensor_head_height_z;
m6_detector_fit_capture_depth_x = 2.0;
// Nominally use the laser-head envelope itself.  No manufacturing clearance
// is invented at this stage; add it only after the purchased part is measured.
m6_detector_fit_head_clearance_y = 0.0;
m6_detector_fit_head_clearance_z = 0.0;
m6_detector_fit_thread_length_x = m6_sensor_mount_stem_length;
m6_detector_fit_thread_clearance_d = m6_sensor_thread_d + 0.6;
m6_detector_fit_thread_tip_allowance_x = 1.0;
m6_detector_shell_wall = 2.4;
m6_detector_shell_clearance = 0.6;
m6_detector_shell_bottom_lip_z = 3;
m6_detector_shell_top_lip_z = 3;
// The active cover split is along the optical x axis: front/optical x- and
// rear/cable x+. The old y split names below remain only as compatibility
// aliases for manifests that still read them.
m6_detector_shell_split_overlap_x = 0.3;
// Top-view z+ footprint: the optical/front x- half is a positive arc and the
// cable/rear x+ half is a rounded rectangle.  The front length deliberately
// extends ahead of the optical datum so the cover reads like the user's
// upper-arch sketch while the hollow optical tip remains open.
m6_detector_shell_corner_radius = 4.0;
// The enlarged front cap has a solid optical bulkhead; only ten small optical
// bores pass through it, so the AF8 head, blue guard, and one supplied nut stay
// inside the enclosure instead of being exposed at the front face.
m6_detector_front_cap_length_x = 18;
m6_detector_front_cap_reduction = 1.2;
m6_detector_body_groove_width_x = 4;
m6_detector_body_groove_depth_y = 1.2;
m6_detector_body_groove_margin_z = 5;
m6_detector_shell_tongue_depth_y = 1.0;
m6_detector_shell_tongue_clearance = 0.25;
m6_detector_optical_bore_d = 6.6;
m6_detector_thread_clearance_d = 6.6;
m6_detector_hex_pocket_af = m6_sensor_head_hex_af;
m6_detector_hex_pocket_depth_x = 2.1;
// Compatibility aliases for old manifests; the active pocket is normal to x
// and follows the purchased AF8 head itself, not the larger lock-nut envelope.
m6_detector_hex_pocket_depth_y = m6_detector_hex_pocket_depth_x;
m6_detector_hex_pocket_floor = 0.8;
m6_detector_shell_screw_pilot_d = 3.4;
m6_detector_shell_screw_head_d = 6.8;
m6_detector_shell_screw_head_depth = 2.0;
m6_detector_shell_screw_margin_z = 18;
m6_detector_bottom_cover_t = 3;
m6_bottom_cover_screw_depth = 5;
m6_detector_bottom_cover_screw_d = 3.4;
m6_detector_bottom_cover_screw_head_d = 6.8;
m6_detector_bottom_cover_screw_head_depth = 1.6;
m6_detector_bottom_cover_screw_inset_x = 9;
m6_detector_cable_exit_d = 12;
m6_detector_cable_exit_sleeve_clearance = 1;
m6_detector_cable_exit_y = 0;
m6_detector_cable_clearance_enabled = false;
m6_detector_show_shell = true;
// Inspection-only overlay; it is opt-in and never belongs to printable STL.
m6_show_optical_direction = false;
m6_detector_shell_alpha = 0.48;
// The support is an integral T-shaped extension of the 6061-T6 body.  The
// central bar remains 10 x 56 x 216 mm; at the y- edge a wider x-direction
// head projects outward by 10 mm and receives a direct M8x1.25 blind tap.
// On SIDE=-1 this whole T head mirrors to x-, i.e. the left emitter side.
m6_detector_support_tail_extension_x = 10;
m6_detector_support_tail_head_depth_y = 14;
m6_detector_support_tail_overlap_y = 0.8;
m6_detector_support_tail_height_z = 28;
m6_detector_support_tail_thread_pitch = 1.25;
m6_detector_support_tail_thread_depth_x = 12;
m6_detector_support_tail_tap_drill_d = 6.8;
m6_detector_support_tail_thread_mouth_d = 9.5;
m6_detector_support_tail_thread_mouth_depth_x = 1.0;
// Compatibility names now describe the integral T-head, not a printed rear
// shell boss.  They remain echoed for older manifests/readers.
m6_detector_support_boss_width_x =
    m6_detector_body_length_x + m6_detector_support_tail_extension_x;
m6_detector_support_boss_depth_y = m6_detector_support_tail_head_depth_y;
m6_detector_support_boss_height_z = m6_detector_support_tail_height_z;
m6_detector_support_boss_x_fraction = 0.72;
m6_detector_support_thread_nominal_d = 8.0;
// Compatibility names for the direct aluminum tap.  No PETG insert/boss is
// used in the active load path; the thread helix is represented by its tap
// drill and mouth envelope in this OpenSCAD handoff.
m6_detector_support_tap_d = m6_detector_support_tail_tap_drill_d;
m6_detector_support_tap_depth_x = m6_detector_support_tail_thread_depth_x;
m6_detector_support_metal_insert_d = 0;
m6_detector_support_metal_insert_length_x = 0;
m6_detector_support_arm_t_z = 8;
m6_detector_support_arm_width_y = 18;
m6_detector_support_leg_t_x = 8;
m6_detector_support_leg_bottom_drop_z = 56;
m6_detector_support_gusset_t_y = 6;
m6_detector_support_gusset_inset_x = 8;
m6_detector_support_fastener_d = 5.5;
m6_detector_support_fastener_head_d = 9;
m6_detector_support_fastener_head_depth = 2.5;
m6_detector_detector_ballhead_gap_x = 2;
m6_detector_sensor_head_y_offset = 0;

// 采购 STG-120ML 的真实机械包络（来自商品详情图，首样仍需量实物）。
// 该器件不是 10 个独立电子模块，而是两条相对的 130×19×6 mm 金属光纤头，
// 有效检测面 120 mm、32×Ø0.25 mm 纤芯、3.87 mm 光点间距；头部本身需要外接放大器。
stg120_head_length = 130;
stg120_active_length = 120;
stg120_head_width = 19;
stg120_head_thickness = 6;
stg120_head_end_margin = 5;
stg120_beam_count = 32;
stg120_beam_pitch = 3.87;
stg120_fiber_connector_d = 2.2;
stg120_detect_distance_max = 1000;
stg120_head_clearance = 0.8;
stg120_carrier_wall = 3;
stg120_carrier_extra = 3;
stg120_outer_face_x = table_edge_x + 0.5;
stg120_head_bottom_z = net_height - stg120_head_end_margin;
stg120_head_center_z = stg120_head_bottom_z + stg120_head_length / 2;
stg120_head_top_z = stg120_head_bottom_z + stg120_head_length;
stg120_outer_frame_min_x = stg120_outer_face_x - stg120_carrier_wall;
stg120_outer_frame_max_x = post_center_x - post_body_width / 2 + stg120_carrier_extra;
stg120_outer_frame_width = stg120_outer_frame_max_x - stg120_outer_frame_min_x;
stg120_outer_frame_y = stg120_head_width + 2 * stg120_carrier_wall;
stg120_outer_frame_z = stg120_head_length + 2 * stg120_carrier_wall;
stg120_center_frame_width = 20;
stg120_center_frame_y = stg120_head_width + 2 * stg120_carrier_wall;
stg120_center_frame_z = stg120_outer_frame_z;
stg120_reference_height = stg120_beam_pitch * 13;
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
// ITTF Technical Leaflet T2 给出的网柱水平部分台外上限为 160 mm。
// 当前自定义传感器夹体把最外点收敛到这个上限；它仍比台边外伸至少
// 130 mm，但不把过度外伸误写成常规商品网夹尺寸。
clamp_horizontal_part_outboard_limit = 160;
clamp_outboard_extension_min = 130;
// With the current 28 mm post and 138.5 mm center offset, 7.5 mm places the
// clamp's outermost face exactly at table edge + 160 mm. Keep this explicit so
// the dependency-free preview can audit the same first-article value.
clamp_outer_extension = 7.5;
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
// 两枚预先对锁的标准 M8 螺母把旋钮和螺杆刚性耦合；单枚旋钮螺母与
// 固定下臂螺母同时啮合会形成不明确的双螺纹约束，首样不采用那种路径。
clamp_knob_h = 20;
clamp_screw_to_knob_top = 32;
clamp_screw_capture_extension = 2;
clamp_nut_af = 13;
clamp_nut_h = 6.5;
clamp_nut_clearance = 0.35;
clamp_nut_pocket_af = clamp_nut_af + 2 * clamp_nut_clearance;
clamp_nut_pocket_depth = clamp_nut_h + clamp_nut_clearance;
clamp_knob_nut_gap = 0.4;
clamp_knob_nut_top_z_clearance = clamp_nut_clearance / 2;
clamp_knob_nut_stack_depth =
    2 * clamp_nut_h + clamp_knob_nut_gap;
clamp_knob_nut_pocket_depth =
    clamp_knob_nut_stack_depth + 2 * clamp_nut_clearance;
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
post_top = max(
    net_height + beam_last_height + optical_module_height / 2 + post_top_margin,
    m6_array_top_z + post_top_margin
);
post_segment_count = 2;
post_joint_gap = 2;
post_joint_sleeve_h = 24;
post_joint_clearance = 0.6;
post_segment_index = 0;
post_total_height = post_top - post_bottom;
post_segment_length =
    (post_total_height - post_joint_gap) / post_segment_count;
post_joint_z = post_bottom + post_segment_length + post_joint_gap / 2;
// 网布和网顶承载条延伸到两侧立柱外边界；立柱实体会与其端部重叠，
// 这对应常规网布从网柱上端一直固定到下端的装配关系。
net_span = 2 * (post_center_x + post_body_width / 2);
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
m6_sensor_axis_x = optical_beam_axis_x;
m6_sensor_mount_hole_x =
    m6_sensor_axis_x + m6_sensor_mount_x_offset;
// Vendor drawing: 20 mm from the optical face to the threaded end, of which
// the last 14 mm is M6×0.75 thread. The cable branch starts on the short head,
// not on the thread axis.
m6_sensor_thread_start_x =
    m6_sensor_axis_x + m6_sensor_head_length_x;
m6_sensor_thread_end_x =
    m6_sensor_thread_start_x + m6_sensor_mount_stem_length;
m6_sensor_overall_end_x = m6_sensor_thread_end_x;
m6_sensor_head_center_x =
    m6_sensor_axis_x + m6_sensor_head_length_x / 2;
// The vendor-style L sensor's active optical aperture is at the distal end of
// the horizontal threaded barrel.  The gray hex is the cable-side body and
// mounting shoulder, not a separate black optical window.
m6_sensor_optical_aperture_x = m6_sensor_thread_end_x;
m6_sensor_cable_exit_x =
    m6_sensor_head_center_x;
// The historical rail coordinate is retained for the rear support/gimbal
// envelope. The active detector body itself is the thin 6 mm x-direction bar;
// the purchased sensor's horizontal 20 mm package does not make the blue cable
// a second x-axis body.
m6_sensor_rail_x = m6_sensor_axis_x + m6_sensor_head_length_x +
                   m6_sensor_body_length - 3;
m6_rail_tab_min_x = m6_sensor_axis_x + 1;
m6_rail_tab_max_x = m6_sensor_rail_x + m6_rail_t;
m6_mount_plate_x = post_center_x - post_body_width / 2 - m6_mount_plate_t;
m6_yaw_plate_x = m6_mount_plate_x - m6_yaw_plate_t;
m6_pitch_frame_x = m6_sensor_rail_x + m6_rail_t + 2;
m6_yaw_carrier_x = m6_pitch_frame_x;
m6_roll_plate_x = m6_sensor_rail_x - m6_roll_plate_t;
m6_gimbal_pivot_x = m6_yaw_plate_x + m6_yaw_plate_t / 2;
m6_pitch_pivot_x = m6_pitch_frame_x + m6_pitch_frame_t / 2;
m6_roll_pivot_x = m6_sensor_rail_x - m6_roll_plate_t / 2;
m6_pitch_pivot_z = m6_array_center_z + m6_pitch_pivot_offset_z;
m6_roll_pivot_z = m6_array_center_z;
m6_roll_adjuster_contact_y =
    -sqrt((m6_roll_plate_d / 2) * (m6_roll_plate_d / 2) -
          m6_roll_adjuster_offset_z * m6_roll_adjuster_offset_z);
m6_detector_backplate_x = m6_sensor_rail_x + m6_rail_t - 0.5;
m6_ballhead_sensor_stud_center_x =
    m6_detector_backplate_x + m6_detector_backplate_t +
    m6_ballhead_sensor_stud_length / 2;
m6_ballhead_center_x =
    m6_detector_backplate_x + m6_detector_backplate_t +
    m6_ballhead_sensor_stud_length + m6_ballhead_housing_length_x / 2;
m6_ballhead_base_center_x =
    m6_ballhead_center_x + m6_ballhead_housing_length_x / 2 +
    m6_ballhead_base_t / 2;
m6_ballhead_net_stud_center_x =
    m6_ballhead_base_center_x + m6_ballhead_base_t / 2 +
    m6_ballhead_net_stud_length / 2;
m6_ballhead_axis_z = m6_array_center_z;
m6_pitch_yoke_bottom_z = m6_yaw_stage_z + 2 * m6_yaw_stage_t;
m6_pitch_yoke_top_z = m6_array_center_z + m6_pitch_frame_outer_height_z / 2;
m6_yaw_carrier_bottom_z = m6_pitch_yoke_bottom_z;
m6_yaw_carrier_height = m6_pitch_yoke_top_z - m6_pitch_yoke_bottom_z;

// Current detector-body derived coordinates.  The positive-side detector is
// the right-hand receiver: its optical face is toward -x and its cable/body
// extends toward +x.  The vertical aluminum carrier is centered on the
// sensor head/through-hole axis, not stretched along the beam.  SIDE=-1
// mirrors the complete assembly, so the left emitter faces +x and enters from
// x-.
m6_detector_body_center_x =
    m6_sensor_axis_x + m6_sensor_mount_x_offset;
m6_detector_body_min_x =
    m6_detector_body_center_x - m6_detector_body_length_x / 2;
m6_detector_body_max_x = m6_detector_body_min_x + m6_detector_body_length_x;
m6_detector_body_min_y =
    m6_detector_body_center_y - m6_detector_body_depth_y / 2;
m6_detector_body_max_y =
    m6_detector_body_center_y + m6_detector_body_depth_y / 2;
m6_detector_body_bottom_z =
    net_height + m6_sensor_first_height - m6_detector_body_margin_z;
m6_detector_body_top_z =
    net_height + m6_sensor_first_height +
    (m6_sensor_count - 1) * m6_sensor_center_pitch +
    m6_detector_body_margin_z;
m6_detector_body_height_z =
    m6_detector_body_top_z - m6_detector_body_bottom_z;
m6_detector_body_center_z =
    (m6_detector_body_bottom_z + m6_detector_body_top_z) / 2;
m6_detector_shell_min_x =
    m6_sensor_axis_x + m6_sensor_head_length_x / 2 -
    m6_detector_front_cap_length_x;
m6_detector_shell_max_x =
    m6_sensor_overall_end_x + m6_detector_shell_wall;
m6_detector_shell_min_y =
    m6_detector_body_min_y - m6_detector_shell_wall;
m6_detector_shell_max_y =
    m6_detector_body_max_y + m6_detector_shell_wall;
m6_detector_shell_width_y =
    m6_detector_shell_max_y - m6_detector_shell_min_y;
m6_detector_shell_bottom_z =
    m6_detector_body_bottom_z - m6_detector_shell_bottom_lip_z;
m6_detector_shell_top_z =
    m6_detector_body_top_z + m6_detector_shell_top_lip_z;
m6_detector_shell_height_z =
    m6_detector_shell_top_z - m6_detector_shell_bottom_z;
m6_detector_shell_split_x =
    m6_sensor_axis_x + m6_sensor_head_length_x / 2;
m6_detector_shell_front_max_x =
    m6_detector_shell_split_x + m6_detector_shell_split_overlap_x;
m6_detector_shell_rear_min_x =
    m6_detector_shell_split_x - m6_detector_shell_split_overlap_x;
// Active cover split is x-directed: the optical/front cover occupies x- and
// the cable/rear cover occupies x+. Keep the y names as whole-width aliases so
// old manifests do not accidentally reintroduce a y-split shell.
m6_detector_shell_split_y = m6_detector_body_center_y;
m6_detector_shell_front_min_y =
    m6_detector_shell_min_y;
m6_detector_shell_rear_max_y =
    m6_detector_shell_max_y;
m6_detector_shell_inner_min_x =
    m6_detector_shell_min_x - m6_detector_shell_clearance;
m6_detector_shell_inner_max_x =
    m6_sensor_overall_end_x + m6_detector_shell_clearance;
m6_detector_shell_inner_min_y =
    m6_detector_body_min_y - m6_detector_shell_clearance;
m6_detector_shell_inner_max_y =
    m6_detector_body_max_y + m6_detector_shell_clearance;
m6_detector_shell_inner_bottom_z = m6_detector_shell_bottom_z - 0.1;
m6_detector_shell_inner_top_z =
    m6_detector_body_top_z + m6_detector_shell_clearance;
m6_detector_detector_thread_axis_x = m6_sensor_mount_hole_x;
m6_detector_sensor_thread_start_y = m6_detector_body_min_y;
m6_detector_sensor_thread_center_y = m6_detector_body_center_y;
m6_detector_sensor_head_center_y = m6_detector_sensor_head_y_offset;
m6_detector_sensor_body_center_y = m6_detector_sensor_head_center_y;
// Minimal fit-probe coordinates.  Positive side is the right receiver: the
// real gray AF8 sensor head enters from x+, its inner shoulder is captured
// 2 mm inside the body, and the hollow M6 barrel continues through the body
// toward x-. One supplied M6 nut sits on the smooth opposite body face;
// SIDE=-1 mirrors all of these coordinates for the left emitter.
m6_detector_fit_head_inner_x =
    m6_detector_body_max_x - m6_detector_fit_capture_depth_x;
m6_detector_fit_head_center_x =
    m6_detector_fit_head_inner_x + m6_detector_fit_head_length_x / 2;
m6_detector_fit_thread_center_x =
    m6_detector_fit_head_inner_x - m6_detector_fit_thread_length_x / 2;
m6_detector_fit_thread_tip_x =
    m6_detector_fit_head_inner_x - m6_detector_fit_thread_length_x;
m6_detector_fit_thread_visible_length_x =
    m6_detector_body_min_x - m6_detector_fit_thread_tip_x;
m6_detector_fit_body_depth_limit_x =
    m6_detector_fit_thread_length_x +
    m6_detector_fit_capture_depth_x -
    m6_sensor_lock_nut_h -
    m6_detector_fit_thread_tip_allowance_x;
m6_detector_fit_nut_min_x =
    m6_detector_body_min_x - m6_sensor_lock_nut_h;
m6_detector_fit_nut_center_x =
    m6_detector_fit_nut_min_x + m6_sensor_lock_nut_h / 2;
m6_detector_sensor_install_offset_x =
    m6_detector_fit_head_center_x - m6_sensor_head_center_x;
// The bottom-cover sleeve hole follows the installed cable branch, not the
// raw purchased-model coordinate.  The raw sensor module remains reusable for
// the standalone inspection preview; only the installed detector array gets
// this x offset.
m6_detector_cable_exit_x =
    m6_sensor_cable_exit_x + m6_detector_sensor_install_offset_x;
// These aliases describe the installed positive receiver.  The standalone
// sensor preview derives its optional nut from the equivalent raw coordinate.
m6_detector_sensor_thread_end_x = m6_detector_fit_thread_tip_x;
m6_detector_thread_visible_length = m6_detector_fit_thread_visible_length_x;
m6_detector_sensor_nut_center_x = m6_detector_fit_nut_center_x;
m6_detector_sensor_nut_outer_x =
    m6_detector_sensor_nut_center_x - m6_sensor_lock_nut_h / 2;
m6_detector_sensor_nut_base_center_x =
    2 * m6_sensor_head_center_x -
    (m6_detector_fit_nut_center_x - m6_detector_sensor_install_offset_x);
m6_detector_body_screw_z = [
    m6_detector_body_bottom_z + m6_detector_shell_screw_margin_z,
    m6_detector_body_top_z - m6_detector_shell_screw_margin_z
];
m6_detector_shell_screw_y = [
    m6_detector_body_center_y - m6_detector_body_depth_y / 4,
    m6_detector_body_center_y + m6_detector_body_depth_y / 4
];
m6_detector_bottom_screw_x = [
    m6_detector_body_min_x + m6_detector_body_length_x / 4,
    m6_detector_body_max_x - m6_detector_body_length_x / 4
];
// Integral T-tail for the metal load path.  The wider head sits at the body
// y- edge, overlaps the bar by a small amount, and projects 10 mm toward the
// outward x direction on the positive receiver.  Mirroring the complete
// positive-side model puts the same head toward x- on the left emitter.
m6_detector_support_tail_min_x = m6_detector_body_min_x;
m6_detector_support_tail_max_x =
    m6_detector_body_max_x + m6_detector_support_tail_extension_x;
m6_detector_support_tail_width_x =
    m6_detector_support_tail_max_x - m6_detector_support_tail_min_x;
m6_detector_support_tail_max_y =
    m6_detector_body_min_y + m6_detector_support_tail_overlap_y;
m6_detector_support_tail_min_y =
    m6_detector_support_tail_max_y -
    m6_detector_support_tail_head_depth_y;
m6_detector_support_tail_center_y =
    (m6_detector_support_tail_min_y +
     m6_detector_support_tail_max_y) / 2;
m6_detector_support_tail_bottom_z =
    m6_detector_body_center_z - m6_detector_support_tail_height_z / 2;
m6_detector_support_tail_top_z =
    m6_detector_body_center_z + m6_detector_support_tail_height_z / 2;
m6_detector_support_tail_center_z = m6_detector_body_center_z;
m6_detector_support_tail_center_x =
    (m6_detector_support_tail_min_x +
     m6_detector_support_tail_max_x) / 2;
m6_detector_support_tail_thread_engagement_x =
    min(m6_detector_support_tail_thread_depth_x,
        m6_ballhead_sensor_stud_length - 4);
m6_detector_support_tail_thread_entry_x =
    m6_detector_support_tail_max_x;
m6_detector_support_tail_thread_center_x =
    m6_detector_support_tail_thread_entry_x -
    m6_detector_support_tail_thread_depth_x / 2;
// Compatibility aliases now point at the integral aluminum T-head.  They are
// intentionally not derived from the PETG rear-cover envelope.
m6_detector_support_boss_center_x =
    m6_detector_support_tail_center_x;
m6_detector_support_boss_min_x =
    m6_detector_support_tail_min_x;
m6_detector_support_boss_max_x =
    m6_detector_support_tail_max_x;
m6_detector_support_y = m6_detector_support_tail_center_y;
m6_detector_support_boss_min_y =
    m6_detector_support_tail_min_y;
m6_detector_support_boss_max_y =
    m6_detector_support_tail_max_y;
m6_detector_support_boss_center_z = m6_detector_body_center_z;
m6_detector_support_arm_z =
    m6_detector_body_center_z - m6_ballhead_housing_length_x / 2 -
    m6_ballhead_base_t - m6_detector_support_arm_t_z / 2;
m6_detector_ballhead_sensor_stud_center_x =
    m6_detector_support_tail_thread_entry_x +
    m6_ballhead_sensor_stud_length / 2 -
    m6_detector_support_tail_thread_engagement_x;
m6_detector_ballhead_center_x =
    m6_detector_support_tail_thread_entry_x +
    (m6_ballhead_sensor_stud_length -
     m6_detector_support_tail_thread_engagement_x) +
    m6_detector_detector_ballhead_gap_x +
    m6_ballhead_housing_d / 2;
m6_detector_ballhead_center_y = m6_detector_support_y;
m6_detector_ballhead_center_z = m6_detector_body_center_z;
m6_detector_ballhead_base_center_z =
    m6_detector_ballhead_center_z - m6_ballhead_housing_length_x / 2 -
    m6_ballhead_base_t / 2;
m6_detector_ballhead_net_stud_center_z =
    m6_detector_ballhead_base_center_z - m6_ballhead_base_t / 2 -
    m6_ballhead_net_stud_length / 2;
m6_detector_support_arm_min_x =
    m6_detector_ballhead_center_x - m6_ballhead_base_d / 2;
m6_detector_support_arm_max_x =
    m6_mount_plate_x + m6_mount_plate_t + 2;
m6_detector_support_arm_min_y =
    m6_detector_support_y - m6_detector_support_arm_width_y / 2;
m6_detector_support_arm_max_y =
    m6_detector_support_y + m6_detector_support_arm_width_y / 2;
m6_detector_support_leg_x =
    m6_mount_plate_x + m6_mount_plate_t / 2;
m6_detector_support_leg_bottom_z =
    m6_detector_support_arm_z - m6_detector_support_leg_bottom_drop_z;
m6_detector_support_leg_top_z =
    m6_detector_support_arm_z + m6_detector_support_arm_t_z / 2;
m6_detector_support_leg_height_z =
    m6_detector_support_leg_top_z - m6_detector_support_leg_bottom_z;
sensor_x = sensor_x_fraction * net_span / 2;
clamp_pad_x = table_edge_x - clamp_reach_inboard;
clamp_pad_outer_x = post_center_x + post_body_width / 2 + clamp_outer_extension;
clamp_outboard_extension_actual = clamp_pad_outer_x - table_edge_x;
clamp_outer_wall_x = clamp_pad_outer_x - clamp_outer_wall_width;
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
clamp_body_nut_z = clamp_lower_arm_bottom_z + clamp_nut_clearance;
clamp_knob_nut_top_z = clamp_knob_top_z - clamp_knob_nut_top_z_clearance;
clamp_knob_drive_nut_z = clamp_knob_nut_top_z - clamp_nut_h;
clamp_knob_lock_nut_z =
    clamp_knob_drive_nut_z - clamp_knob_nut_gap - clamp_nut_h;
clamp_knob_nut_bottom_z = clamp_knob_lock_nut_z;
// Backward-compatible alias for older parameter readers: the old single-nut
// value now names the upper/drive nut in the jam-nut stack.
clamp_knob_nut_z = clamp_knob_drive_nut_z;
clamp_screw_bottom_z =
    clamp_knob_lock_nut_z - clamp_screw_capture_extension;
clamp_screw_length = clamp_screw_top_z - clamp_screw_bottom_z;
clamp_screw_tip_radius = clamp_screw_d / 2;
clamp_gusset_start_x = clamp_screw_x +
                       clamp_pressure_pad_width / 2 +
                       clamp_gusset_start_inset;
clamp_gusset_end_x = clamp_pad_outer_x - 0.2;
// The triangle lives below the tabletop.  Its long lower edge overlaps the
// lower arm and its outer vertical edge overlaps the C-wall; the 0.2 mm
// offsets make the CSG unions real overlaps instead of coincident faces.
clamp_gusset_top_z = clamp_pressure_pad_top_z - 0.5;
clamp_gusset_bottom_z = clamp_lower_arm_bottom_z - 0.2;
default_side = SIDE == 0 ? 1 : SIDE;

assert(table_width > 0 && table_thickness > 0, "table dimensions must be positive");
assert(post_offset > 0, "integrated stand must sit outside the table edge");
assert(post_center_x > table_edge_x, "post center must be outside the table edge");
assert(net_post_outboard_extension >= 130 &&
           abs(post_center_x + post_body_width / 2 - table_edge_x -
               net_post_outboard_extension) < 0.01,
       "net post outer edge must meet the 130 mm minimum and the named extension");
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
           post_segment_length > 100 && post_segment_length < 240 &&
           post_joint_sleeve_h > post_joint_gap && post_joint_clearance > 0,
       "the upright must split into two printable segments with a keyed joint");
assert(post_segment_index >= 0 && post_segment_index < post_segment_count,
       "post_segment_index must select an existing printable upright segment");
assert(m6_post_mount_clearance_d >= m6_stage_bolt_d &&
           m6_post_mount_hole_y + m6_post_mount_clearance_d / 2 <
               post_body_depth / 2 &&
           m6_post_mount_hole_y > m6_post_mount_clearance_d / 2 &&
           m6_post_mount_hole_z > post_joint_z + post_joint_gap / 2 &&
           m6_post_mount_hole_z < post_top &&
           m6_post_mount_bolt_length >=
               m6_mount_plate_t + post_body_width + 8,
       "M6 adapter-to-upright through-bolts must clear the current net clamp");
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
assert(m6_sensor_count == beam_count &&
           m6_sensor_center_pitch == 2 * beam_pitch &&
           m6_sensor_first_height == beam_first_height &&
           m6_sensor_first_height +
               (m6_sensor_count - 1) * m6_sensor_center_pitch >
               m6_sensor_first_height,
       "M6 sensor array must keep ten channels at the collision-safe 20 mm pitch");
assert(m6_sensor_thread_d == 6 && m6_sensor_thread_pitch == 0.75 &&
           m6_sensor_tap_visual_d > 0 &&
           m6_sensor_tap_visual_d < m6_sensor_thread_d &&
           m6_sensor_head_length_x + m6_sensor_mount_stem_length == 20 &&
           m6_sensor_head_width_y >= m6_sensor_thread_d &&
           m6_sensor_head_height_z > 0 &&
           m6_sensor_head_hex_af > 0 &&
           m6_sensor_head_hex_af <= m6_sensor_head_width_y &&
           m6_sensor_body_d >= m6_sensor_thread_d &&
           m6_sensor_mount_stem_length > m6_sensor_thread_engagement &&
           m6_sensor_body_length > m6_sensor_thread_engagement &&
           m6_sensor_cable_guard_length > 0 &&
           m6_sensor_cable_preview_length > 0 &&
           m6_sensor_cable_d > 0 &&
           m6_sensor_thread_start_x == m6_sensor_axis_x +
               m6_sensor_head_length_x &&
           m6_sensor_thread_end_x == m6_sensor_overall_end_x,
       "M6×0.75 horizontal optical/thread axis and perpendicular cable branch must be usable");
assert(m6_rail_t > 0 && m6_rail_width_y > m6_sensor_head_width_y + 2 &&
           m6_rail_tab_t >= 5 &&
           m6_rail_tab_width_y > m6_sensor_thread_d + 2 &&
           2 * m6_sensor_lane_offset_y > m6_sensor_head_width_y &&
           2 * m6_sensor_lane_offset_y > m6_rail_tab_width_y &&
           m6_sensor_body_clearance_d > m6_sensor_body_d &&
           m6_sensor_body_clearance_d / 2 <
               m6_rail_width_y / 2 - m6_sensor_lane_offset_y &&
           m6_sensor_rail_post_clearance > 0 &&
           m6_rail_end_margin >= 8 && m6_rail_length_z > 0 &&
           m6_array_bottom_z < m6_array_top_z &&
           m6_sensor_axis_x >= table_edge_x &&
           m6_sensor_rail_x > m6_sensor_axis_x &&
           m6_sensor_rail_x + m6_rail_t <=
               post_center_x - post_body_width / 2 &&
           m6_rail_tab_min_x >= table_edge_x &&
           m6_rail_tab_min_x < m6_sensor_mount_hole_x &&
           m6_sensor_mount_hole_x < m6_rail_tab_max_x,
       "M6 single vertical sensor bar must cover the table edge and stay within the clamp-side envelope");
assert(m6_detector_backplate_t >= 6 &&
           m6_detector_backplate_width_y > m6_rail_width_y &&
           m6_detector_backplate_height_z > m6_rail_length_z &&
           m6_detector_backplate_x >= m6_sensor_rail_x &&
           m6_detector_backplate_x < m6_sensor_rail_x + m6_rail_t &&
           m6_detector_backplate_mount_clearance_d > m6_ballhead_sensor_stud_d &&
           m6_detector_backplate_anti_rotation_d > 0 &&
           m6_detector_backplate_lock_hole_y +
               m6_detector_backplate_anti_rotation_d / 2 <
               m6_detector_backplate_width_y / 2,
       "M6 detector backplate must overlap the vertical bar and leave a ball-head mounting pattern");
assert(m6_ballhead_ball_d == 13 &&
           m6_ballhead_housing_d > m6_ballhead_ball_d &&
           m6_ballhead_housing_length_x > m6_ballhead_sensor_stud_length &&
           m6_ballhead_base_d > m6_ballhead_ball_d &&
           m6_ballhead_sensor_stud_d == 8 &&
           m6_ballhead_net_stud_d == 8 &&
           m6_ballhead_sensor_stud_length > 0 &&
           m6_ballhead_net_stud_length > 0 &&
           m6_ballhead_tilt_range_deg == 90 &&
           m6_ballhead_rotation_range_deg == 360 &&
           m6_ballhead_net_stud_center_x - m6_ballhead_net_stud_length / 2 <
               m6_mount_plate_x + m6_mount_plate_t + 2 &&
           m6_ballhead_net_stud_center_x + m6_ballhead_net_stud_length / 2 >
               m6_mount_plate_x,
       "13 mm commercial ball head must bridge the detector backplate to the net-side adapter");
assert(m6_sensor_mount_plane_offset_z > m6_sensor_head_height_z / 2 &&
           m6_sensor_mount_plane_offset_z + m6_rail_tab_t -
               m6_sensor_head_height_z / 2 < m6_sensor_mount_stem_length,
       "legacy M6 fit coupon envelope must remain numerically valid");
assert(m6_sensor_lock_nut_af > m6_sensor_thread_d &&
           m6_sensor_lock_nut_h > 0 &&
           m6_sensor_nut_pocket_clearance > 0 &&
           m6_sensor_guard_outer_d > m6_sensor_lock_nut_af +
               2 * m6_sensor_nut_pocket_clearance &&
           m6_sensor_guard_h >= m6_sensor_lock_nut_h,
       "M6 lock-nut anti-rotation pocket must leave a machinable wall");
assert(m6_adjacent_channel_center_distance_yz >
           m6_sensor_guard_outer_d + 2 * m6_sensor_nut_pocket_clearance &&
           m6_adjacent_guard_gap_y > 2 * m6_sensor_nut_pocket_clearance &&
           m6_adjacent_guard_gap_z > 2 * m6_sensor_nut_pocket_clearance,
       "adjacent M6 lock-nut guards must clear in y/z at the 10 mm pitch");
assert(m6_sensor_test_coupon_backbone_h > m6_sensor_guard_h +
           m6_rail_tab_t &&
           m6_sensor_test_coupon_clearance_d > m6_sensor_thread_d &&
           m6_sensor_test_coupon_clearance_d < m6_sensor_guard_outer_d &&
           m6_sensor_test_coupon_guard_overlap > 0 &&
           m6_sensor_test_coupon_guard_overlap < m6_rail_tab_t / 2 &&
           m6_sensor_test_coupon_tab_min_local_x <
               m6_sensor_test_coupon_mount_hole_local_x &&
           m6_sensor_test_coupon_mount_hole_local_x < m6_rail_t,
       "M6 single-sensor fit coupon must leave a printable body and anti-rotation guard");
assert(m6_rail_mount_clearance_d > m6_rail_mount_tap_d &&
           m6_rail_mount_tap_depth > 0 &&
           m6_rail_mount_tap_depth <= m6_rail_t - 2 &&
           m6_rail_mount_hole_y + m6_rail_mount_clearance_d / 2 <
               m6_rail_width_y / 2 &&
           m6_rail_mount_z_offset + m6_rail_mount_clearance_d / 2 <
               m6_rail_length_z / 2 &&
           sqrt(pow(m6_rail_mount_hole_y - m6_sensor_lane_offset_y, 2) +
                pow((m6_sensor_count - 1) * m6_sensor_center_pitch / 2 -
                    m6_rail_mount_z_offset, 2)) >
               (m6_rail_mount_clearance_d + m6_sensor_body_clearance_d) / 2,
       "M4 rail-to-roll mounting holes must clear the M6 body envelopes");
assert(sqrt(pow(m6_rail_mount_hole_y, 2) +
            pow(m6_rail_mount_z_offset, 2)) +
           m6_rail_mount_clearance_d / 2 < m6_roll_plate_d / 2,
       "roll plate must contain all four rail-to-roll M4 clearance holes");
assert(m6_rail_tab_max_x - m6_rail_tab_min_x <= 130,
       "the standard outboard post limit must not create an excessively long M6 shelf");
assert(m6_roll_pivot_d > m6_sensor_thread_d &&
           m6_roll_pivot_d < m6_sensor_body_clearance_d +
               2 * m6_sensor_lane_offset_y &&
           sqrt(pow(m6_sensor_lane_offset_y, 2) +
                pow(m6_sensor_center_pitch / 2, 2)) >
               (m6_sensor_body_clearance_d + m6_roll_pivot_d) / 2,
       "central x-axis roll pivot must clear the nearest M6 body relief holes");
assert(m6_mount_plate_t >= 4 && m6_mount_plate_width_y > m6_rail_width_y &&
           m6_mount_plate_height_z > m6_rail_length_z &&
           m6_mount_slot_length > m6_stage_bolt_d &&
           m6_yaw_slot_length > m6_stage_bolt_d &&
           m6_pitch_slot_length > m6_stage_bolt_d &&
           m6_roll_slot_length > m6_stage_bolt_d,
       "M6 gimbal plates must leave machinable lock slots around the pivots");
assert(m6_yaw_range_deg > 0 && m6_yaw_range_deg <= 10 &&
           m6_pitch_range_deg > 0 && m6_pitch_range_deg <= 10 &&
           m6_roll_range_deg > 0 && m6_roll_range_deg <= 10 &&
           abs(m6_yaw_angle) <= m6_yaw_range_deg &&
           abs(m6_pitch_angle) <= m6_pitch_range_deg &&
           abs(m6_roll_angle) <= m6_roll_range_deg &&
           m6_pivot_d > m6_sensor_thread_d &&
           m6_stage_bolt_d > m6_fine_adjuster_d,
       "M6 gimbal angles, adjustment ranges and fastener hierarchy must be valid");
assert(m6_pitch_adjuster_offset_z > 0 &&
           m6_pitch_adjuster_offset_z < m6_pitch_frame_outer_height_z / 2 &&
           m6_pitch_adjuster_bridge_t >= m6_fine_adjuster_d &&
           m6_roll_adjuster_offset_z > 0 &&
           m6_roll_adjuster_offset_z < m6_roll_plate_d / 2 &&
           m6_roll_adjuster_arm_depth_y > m6_fine_adjuster_d &&
           m6_roll_adjuster_clearance_y > 0 &&
           m6_roll_adjuster_length > m6_fine_adjuster_d,
       "M6 fine-adjuster reaction pads must remain inside the pitch/roll envelopes");
assert(m6_yaw_adjuster_block_width_x > m6_fine_adjuster_d &&
           m6_yaw_adjuster_block_depth_y > 0 &&
           m6_yaw_adjuster_block_height_z > 2 * m6_yaw_stage_t &&
           m6_yaw_adjuster_foot_inset_y > 0 &&
           m6_yaw_adjuster_tap_d < m6_fine_adjuster_d &&
           m6_yaw_adjuster_tap_depth >= m6_yaw_adjuster_block_depth_y &&
           m6_yaw_adjuster_tip_overtravel_y > 0 &&
           m6_yaw_adjuster_tip_overtravel_y < m6_yaw_stage_t / 2,
       "yaw fine adjuster must have a raised fixed reaction ear and upper-plate contact");
assert(m6_pitch_frame_outer_width_y > m6_pitch_frame_window_width_y &&
           m6_pitch_frame_outer_height_z > m6_pitch_frame_window_height_z &&
           m6_pitch_frame_window_width_y > m6_roll_plate_d + 2 * 3 &&
           m6_pitch_frame_window_height_z > m6_roll_plate_d + 2 * 3 &&
           m6_pitch_frame_spine_width_y > m6_roll_pivot_d &&
           m6_pitch_frame_hub_d > m6_roll_pivot_d &&
           m6_pitch_yoke_width_y > m6_pitch_frame_outer_width_y + 2 &&
           m6_pitch_pivot_z > m6_array_center_z -
               m6_pitch_frame_outer_height_z / 2 &&
           m6_pitch_pivot_z < m6_array_center_z +
               m6_pitch_frame_outer_height_z / 2,
       "pitch inner frame must surround the roll plate and have a real y-axis axle");

// Current 45-degree L-sensor detector contract.  These checks deliberately sit
// beside (rather than replace) the legacy three-axis assertions so old
// diagnostic PARTs remain compilable while the active assembly follows the
// thin vertical carrier / outward x-entry design.
assert(abs(m6_sensor_roll_deg) == 45 &&
           m6_detector_body_depth_y > 0 &&
           m6_detector_body_length_x <=
               m6_detector_fit_body_depth_limit_x &&
           m6_detector_body_depth_y > m6_sensor_head_width_y + 2 &&
           m6_detector_body_min_y < m6_detector_sensor_head_center_y &&
           m6_detector_body_max_y > m6_detector_sensor_head_center_y &&
           m6_detector_body_center_x == m6_sensor_mount_hole_x &&
           m6_detector_body_height_z >
               (m6_sensor_count - 1) * m6_sensor_center_pitch &&
           m6_detector_body_bottom_z < m6_sensor_z(0) &&
           m6_detector_body_top_z > m6_sensor_z(m6_sensor_count - 1),
       "current M6 body must fit ten 10 mm channels and leave one-nut horizontal-thread clearance");
assert(m6_detector_hex_pocket_af >= m6_sensor_head_hex_af &&
           m6_detector_hex_pocket_af < m6_sensor_lock_nut_af &&
           m6_detector_hex_pocket_depth_x > 0 &&
           m6_detector_hex_pocket_depth_x >=
               m6_detector_fit_capture_depth_x + 0.1 - 0.001 &&
           m6_detector_hex_pocket_depth_x +
               m6_detector_hex_pocket_floor < m6_detector_body_length_x &&
           m6_detector_hex_pocket_depth_x < m6_detector_body_length_x &&
           m6_detector_thread_clearance_d > m6_sensor_thread_d &&
           m6_detector_optical_bore_d > m6_sensor_thread_d &&
           m6_detector_optical_bore_d < m6_detector_body_height_z &&
           m6_detector_thread_visible_length >
               m6_sensor_lock_nut_h + m6_sensor_nut_pocket_clearance,
       "shallow AF8 M6 hex pocket, through-bore and one external nut must be machinable");
assert(m6_detector_fit_head_length_x > m6_detector_fit_capture_depth_x &&
           m6_detector_fit_head_width_y > 0 &&
           m6_detector_fit_head_height_z > 0 &&
           m6_detector_fit_head_clearance_y >= 0 &&
           m6_detector_fit_head_clearance_z >= 0 &&
           m6_detector_fit_thread_length_x > 0 &&
           m6_detector_fit_thread_clearance_d > m6_sensor_thread_d &&
           m6_detector_fit_thread_visible_length_x >=
               m6_sensor_lock_nut_h +
               m6_detector_fit_thread_tip_allowance_x - 0.01,
       "minimal M6 fit probe must capture 2 mm of the real AF8 head and leave one nut thickness plus tip allowance exposed");
assert(m6_detector_shell_wall >= 2 &&
           m6_detector_shell_clearance > 0 &&
           m6_detector_shell_front_max_x > m6_detector_shell_min_x &&
           m6_detector_shell_rear_min_x < m6_detector_shell_max_x &&
           m6_detector_shell_front_max_x > m6_detector_shell_rear_min_x &&
           m6_detector_shell_width_y > m6_detector_body_depth_y &&
           m6_detector_shell_height_z > m6_detector_body_height_z &&
           m6_detector_front_cap_length_x >
               m6_detector_shell_split_overlap_x &&
           m6_detector_shell_min_x < m6_detector_fit_thread_tip_x &&
           m6_detector_shell_inner_min_x < m6_detector_fit_thread_tip_x &&
           m6_detector_shell_min_x + m6_detector_shell_wall <
               m6_detector_fit_thread_tip_x &&
           m6_detector_shell_wall <
               m6_detector_shell_front_max_x -
                   m6_detector_shell_min_x &&
           m6_detector_shell_corner_radius > 0 &&
           m6_detector_shell_corner_radius <
               min(m6_detector_shell_width_y, m6_detector_shell_height_z) / 2 &&
           m6_detector_shell_corner_radius <
               min(m6_detector_shell_max_x - m6_detector_shell_rear_min_x,
                   m6_detector_shell_width_y) / 2,
       "front/rear PETG covers must leave a body cavity and printable rounded envelope");
assert(m6_detector_body_groove_width_x > 0 &&
           m6_detector_body_groove_depth_y > 0 &&
           m6_detector_body_groove_depth_y < m6_detector_body_depth_y / 2 &&
           m6_detector_body_groove_margin_z > 0 &&
           2 * m6_detector_body_groove_margin_z < m6_detector_body_height_z &&
           m6_detector_body_groove_width_x / 2 >
               2 * m6_detector_shell_tongue_clearance &&
           m6_detector_body_groove_depth_y >
               2 * m6_detector_shell_tongue_clearance &&
           m6_detector_shell_tongue_depth_y >
               m6_detector_shell_tongue_clearance,
       "two x-half cover tongues must share real y-edge guide grooves with print clearance");
assert(m6_detector_shell_screw_pilot_d > 0 &&
           m6_detector_shell_screw_head_d > m6_detector_shell_screw_pilot_d &&
           m6_detector_shell_screw_head_depth > 0 &&
           m6_detector_bottom_cover_t >
               m6_detector_bottom_cover_screw_head_depth &&
           m6_detector_cable_exit_d > m6_sensor_body_d &&
           m6_detector_cable_exit_d +
               2 * m6_detector_cable_exit_sleeve_clearance <
               m6_detector_shell_width_y + 2 * m6_detector_shell_wall,
       "cover countersinks and open cable sleeve exit must fit the printable covers");
assert(m6_detector_support_tail_extension_x >= 10 &&
           m6_detector_support_tail_width_x >=
               m6_detector_body_length_x + 10 &&
           m6_detector_support_tail_head_depth_y >
               2 * m6_detector_shell_clearance &&
           m6_detector_support_tail_max_y > m6_detector_body_min_y &&
           m6_detector_support_tail_min_y < m6_detector_body_min_y &&
           m6_detector_support_tail_bottom_z <
               m6_detector_support_tail_center_z &&
           m6_detector_support_tail_top_z >
               m6_detector_support_tail_center_z &&
           m6_detector_support_tail_max_x <=
               m6_detector_shell_max_x &&
           m6_detector_support_tail_thread_pitch == 1.25 &&
           m6_detector_support_tail_thread_depth_x >
               m6_detector_support_tail_thread_mouth_depth_x &&
           m6_detector_support_tail_thread_depth_x <
               m6_detector_support_tail_width_x &&
           m6_detector_support_tail_tap_drill_d <
               m6_detector_support_thread_nominal_d &&
           m6_detector_support_tail_thread_mouth_d >
               m6_detector_support_thread_nominal_d &&
           m6_detector_support_tail_thread_engagement_x > 0 &&
           m6_detector_support_tail_thread_engagement_x <=
               m6_ballhead_sensor_stud_length &&
           m6_detector_support_boss_width_x ==
               m6_detector_support_tail_width_x &&
           m6_detector_support_boss_depth_y ==
               m6_detector_support_tail_head_depth_y &&
           m6_detector_support_boss_height_z ==
               m6_detector_support_tail_height_z &&
           m6_detector_support_arm_max_x > m6_detector_support_arm_min_x &&
           m6_detector_support_arm_min_x >
               m6_detector_support_tail_max_x &&
           m6_detector_support_leg_height_z > m6_detector_support_arm_t_z &&
           m6_detector_support_leg_x >= m6_mount_plate_x &&
           m6_detector_support_leg_x <= m6_mount_plate_x + m6_mount_plate_t &&
           m6_detector_support_metal_insert_d == 0 &&
           m6_detector_support_metal_insert_length_x == 0,
       "integral aluminum T-tail, direct M8 female tap, vertical ballhead and 90-degree bracket must form one load path");
assert(m6_detector_ballhead_center_z == m6_detector_body_center_z &&
           m6_detector_ballhead_base_center_z <
               m6_detector_ballhead_center_z &&
           m6_detector_ballhead_net_stud_center_z <
               m6_detector_ballhead_base_center_z &&
           m6_detector_ballhead_sensor_stud_center_x >
               m6_detector_support_boss_center_x &&
           m6_detector_ballhead_sensor_stud_center_x -
               m6_ballhead_sensor_stud_length / 2 <
               m6_detector_support_tail_thread_entry_x &&
           m6_detector_ballhead_sensor_stud_center_x +
               m6_ballhead_sensor_stud_length / 2 >
               m6_detector_support_tail_thread_entry_x -
                   m6_detector_support_tail_thread_engagement_x &&
           m6_detector_ballhead_center_x >
               m6_detector_ballhead_sensor_stud_center_x,
       "commercial 13 mm ballhead must remain vertical with a rear x-axis sensor interface");
assert(m6_yaw_stage_radius > m6_yaw_slot_radius +
           m6_stage_bolt_d &&
           m6_yaw_slot_radius > m6_stage_bolt_d &&
           m6_yaw_stage_t >= m6_yaw_plate_t &&
           m6_yaw_stage_z < m6_array_bottom_z &&
           m6_yaw_stage_z >=
               m6_array_center_z - m6_mount_plate_height_z / 2 &&
           m6_yaw_carrier_bottom_z < m6_array_center_z &&
           m6_yaw_carrier_bottom_z + m6_yaw_carrier_height >
               m6_array_top_z,
       "Z-axis yaw turntable must leave a usable pivot, arc slots and carrier");
assert(m6_yaw_base_mount_clearance_d > m6_yaw_base_mount_tap_d &&
           m6_yaw_base_mount_tap_depth >= m6_yaw_stage_t &&
           m6_yaw_base_mount_tap_depth <
               2 * m6_yaw_stage_radius - m6_mount_plate_t &&
           m6_yaw_base_mount_hole_y + m6_yaw_base_mount_clearance_d / 2 <
               m6_yaw_stage_radius &&
           m6_yaw_base_mount_hole_y > m6_pivot_d / 2 +
               m6_yaw_base_mount_clearance_d / 2,
       "fixed adapter must have two clear M6 connections into the yaw base");
assert(m5_yaw_carrier_mount_clearance_d > m5_yaw_carrier_mount_tap_d &&
           m5_yaw_carrier_mount_tap_depth > 0 &&
           m5_yaw_carrier_mount_hole_y +
               m5_yaw_carrier_mount_clearance_d / 2 <
               m6_mount_plate_width_y / 2 &&
           m5_yaw_carrier_mount_hole_y > m6_pivot_d / 2 +
               m5_yaw_carrier_mount_clearance_d / 2,
       "yaw carrier must have two explicit M5 vertical connections");
assert(post_top > m6_array_top_z + m6_rail_end_margin,
       "upright must clear the M6 aluminum rail and its adjustment hardware");
assert(stg120_head_length > stg120_active_length &&
           stg120_head_width > 0 && stg120_head_thickness > 0 &&
           stg120_head_end_margin > 0 &&
           stg120_active_length == stg120_head_length -
               2 * stg120_head_end_margin,
       "STG-120ML head envelope must leave equal end margins around the active face");
assert(stg120_beam_count == 32 && stg120_beam_pitch > 0 &&
           abs((stg120_beam_count - 1) * stg120_beam_pitch -
               stg120_active_length) < 0.1,
       "STG-120ML must use 32 optical points at 3.87 mm pitch");
assert(stg120_detect_distance_max >= stg120_outer_face_x &&
           stg120_outer_frame_width > stg120_head_thickness +
               2 * stg120_head_clearance &&
           stg120_outer_frame_max_x > stg120_outer_face_x +
               stg120_head_thickness,
       "STG-120ML outer carrier must leave a printable support arm inside the post");
assert(stg120_center_frame_width > stg120_head_thickness +
           2 * stg120_head_clearance &&
           stg120_center_frame_y > stg120_head_width &&
           stg120_center_frame_z == stg120_outer_frame_z,
       "STG-120ML central bridge must capture two back-to-back heads");
assert(net_span > table_width, "the net must bridge both integrated uprights");
assert(abs(net_span - (table_width + 2 * net_post_outboard_extension)) < 0.01,
       "net rail span must reach the two standard outboard post limits");
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
assert(clamp_gusset_t_y > 0 && clamp_gusset_t_y < clamp_pad_depth / 2 &&
           clamp_gusset_start_x > clamp_pressure_pad_x +
               clamp_pressure_pad_width / 2 &&
           clamp_gusset_start_x < clamp_gusset_end_x &&
           clamp_gusset_end_x > clamp_gusset_start_x &&
           clamp_gusset_end_x > clamp_outer_wall_x &&
           clamp_gusset_top_z < -table_thickness &&
           clamp_gusset_top_z > clamp_lower_arm_top_z &&
           clamp_gusset_bottom_z < clamp_lower_arm_bottom_z,
       "under-clamp triangular ribs must sit below the tabletop and overlap the lower arm and outer wall");
assert(clamp_pad_x < table_edge_x && clamp_pad_outer_x > table_edge_x &&
           clamp_outer_wall_x < clamp_pad_outer_x &&
           clamp_outboard_extension_actual >= clamp_outboard_extension_min &&
           clamp_outboard_extension_actual <=
               clamp_horizontal_part_outboard_limit + 0.01 &&
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
assert(clamp_knob_nut_gap >= 0 &&
           clamp_knob_nut_stack_depth ==
               2 * clamp_nut_h + clamp_knob_nut_gap &&
           clamp_knob_nut_pocket_depth > clamp_knob_nut_stack_depth &&
           clamp_knob_nut_pocket_depth < clamp_knob_h &&
           clamp_knob_nut_top_z <= clamp_knob_top_z &&
           clamp_knob_nut_bottom_z >= clamp_knob_bottom_z &&
           clamp_knob_drive_nut_z > clamp_knob_lock_nut_z,
       "two M8 jam nuts must fit as a captured, printable knob stack");
assert(clamp_screw_to_knob_top > clamp_knob_nut_pocket_depth &&
           clamp_screw_capture_extension > 0 &&
           clamp_screw_top_z > clamp_knob_nut_top_z &&
           clamp_screw_bottom_z < clamp_knob_nut_bottom_z &&
           clamp_screw_bottom_z > clamp_knob_bottom_z &&
           clamp_knob_bottom_z < clamp_knob_top_z,
       "M8 rod must pass through the jam-nut stack and leave a usable handwheel");
assert(clamp_knob_d > clamp_screw_bore_d &&
           clamp_knob_h > clamp_knob_nut_pocket_depth,
       "printed clamp knob must leave an M8 bore and captured jam-nut wall");
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
function m6_sensor_z(index) =
    net_height + m6_sensor_first_height + index * m6_sensor_center_pitch;
function m6_sensor_last_height() =
    m6_sensor_first_height +
    (m6_sensor_count - 1) * m6_sensor_center_pitch;
function m6_sensor_lane_y(index) =
    index % 2 == 0 ? -m6_sensor_lane_offset_y : m6_sensor_lane_offset_y;
function m6_sensor_tab_z(index) =
    m6_sensor_z(index) - m6_sensor_mount_plane_offset_z -
    m6_rail_tab_t / 2;
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

module clamp_outboard_gusset_positive() {
    // The gussets are triangular plates below the tabletop, duplicated at
    // the front/back y edges of the clamp.  The long lower edge overlaps the
    // lower arm, the outer vertical edge overlaps the C-wall, and the sloped
    // edge closes toward the underside of the table.  This is the conventional
    // under-clamp load path; it no longer pretends that an upper-jaw triangle
    // is a structural brace.
    color("slategray")
        for (y_side = [-1, 1]) {
            translate([0,
                       y_side * (clamp_pad_depth / 2 - clamp_gusset_t_y / 2),
                       0])
                rotate([90, 0, 0])
                    linear_extrude(height = clamp_gusset_t_y, center = true) {
                        polygon(points = [
                            [clamp_gusset_start_x, clamp_gusset_bottom_z],
                            [clamp_gusset_end_x, clamp_gusset_bottom_z],
                            [clamp_gusset_end_x, clamp_gusset_top_z]
                        ]);
                    }
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
                clamp_outboard_gusset_positive();
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
    // 这是金属外购螺杆的几何占位。首样不打印螺纹，使用真实 M8×1.25
    // 螺杆承受夹紧载荷；圆头只用于检查与台底压块的接触位置。
    color("silver") {
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
            // Two M8 nuts are pre-tightened against each other on the rod and
            // captured as one hex stack. This gives the handwheel a positive
            // drive interface; the lower-arm nut is the only stationary thread.
            translate([clamp_screw_x, 0,
                       clamp_knob_top_z - clamp_knob_nut_pocket_depth])
                hex_prism(clamp_nut_pocket_af,
                          clamp_knob_nut_pocket_depth + 0.01);
        }
}

module clamp_knob_nut_positive() {
    // Install these two standard nuts on the M8 rod and tighten them against
    // each other before inserting the stack into the printed knob. The
    // resulting jam pair rotates with the rod and does not create a second
    // independently constrained thread.
    color("gold") {
        translate([clamp_screw_x, 0, clamp_knob_drive_nut_z])
            m8_nut_positive();
        translate([clamp_screw_x, 0, clamp_knob_lock_nut_z])
            m8_nut_positive();
    }
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
    // 这是组合诊断剖面：一条窄中线穿过 M8 压紧螺杆/旋钮，另一条窄后侧
    // 切片穿过下方三角肋。两条切片一起显示完整的免打孔受力路径，不把
    // 夹具下方真正的加固肋误删成只剩一张中间薄片。
    section_y = clamp_pad_depth / 2 - clamp_gusset_t_y / 2;
    union() {
        translate([clamp_pad_x - 8, -1,
                   clamp_knob_bottom_z - 5])
            cube([clamp_pad_outer_x - clamp_pad_x + 16,
                  2,
                  -clamp_knob_bottom_z + 10]);
        translate([clamp_pad_x - 8,
                   section_y - (clamp_gusset_t_y + 2) / 2,
                   clamp_knob_bottom_z - 5])
            cube([clamp_pad_outer_x - clamp_pad_x + 16,
                  clamp_gusset_t_y + 2,
                  -clamp_knob_bottom_z + 10]);
    }
}

module table_clamp_section_positive() {
    section_x = clamp_pad_x - 8;
    section_width = clamp_pad_outer_x - clamp_pad_x + 16;
    section_y = clamp_pad_depth / 2 - clamp_gusset_t_y / 2;
    // 半透明台板截面明确标出 z=-table_thickness 到 z=0 的实体范围；
    // 两个切片都保留，旋钮内的两枚对锁螺母与固定下臂螺母均位于桌板底面以下。
    color("gray", 0.45)
        intersection() {
            translate([section_x,
                       -clamp_pad_depth / 2,
                       -table_thickness])
                cube([section_width, clamp_pad_depth, table_thickness]);
            table_clamp_section_clip();
        }
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
        difference() {
            union() {
                translate([post_center_x - post_body_width / 2,
                           -post_body_depth / 2, segment_z])
                    cube([post_body_width, post_body_depth,
                          post_segment_length]);
                // 下段单独导出时也必须带上台面上方的箱型加厚，否则单件打印会
                // 丢失承载网顶和光学导轨的局部结构。
                if (index == 0) {
                    translate([post_center_x - post_body_width / 2 - 5,
                               -post_body_depth / 2 - 4,
                               -2])
                        cube([post_body_width + 10, post_body_depth + 8,
                              34]);
                }
            }
            // The upper upright carries the aluminum adapter.  The elongated
            // x-through slots leave ±6 mm vertical installation adjustment;
            // the bolts are the actual load path, not the plate intersection.
            if (index == post_segment_count - 1) {
                for (y_position = [-m6_post_mount_hole_y,
                                   m6_post_mount_hole_y]) {
                    m6_slot_x_z_span(
                        post_center_x,
                        y_position,
                        m6_post_mount_hole_z,
                        m6_mount_slot_length,
                        post_body_width + 8,
                        m6_post_mount_clearance_d);
                }
            }
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

// -----------------------------------------------------------------------------
// 当前 M6 十路铝合金主体、T 尾座与采购球头微调接口
//
// 机械契约：6061-T6 铝合金主体、T 尾座、90° 支撑和适配板由机加工/金属
// 工艺完成；FDM 只用于 PETG 壳体和尺寸样件。当前承力路径是：
// M6×0.75 器件六角/主体 -> 10×56×216 mm 铝合金长条与 y- 一体 T 尾座
// -> 直接加工的 M8×1.25 内丝 -> 金属 M8 球头 -> 竖直 90° 支撑 -> 网夹适配板。
// 采购球头提供偏航/俯仰/滚转的微调接口；前后壳和底盖只负责保护、导向和
// 线缆出口，不承担球头弯矩。

module m6_cylinder_x(d, h, x_center, y_center, z_center) {
    translate([x_center, y_center, z_center])
        rotate([0, 90, 0])
            cylinder(d = d, h = h, center = true);
}

module m6_cylinder_y(d, h, x_center, y_center, z_center) {
    translate([x_center, y_center, z_center])
        rotate([90, 0, 0])
            cylinder(d = d, h = h, center = true);
}

module m6_cylinder_z(d, h, x_center, y_center, z_center) {
    translate([x_center, y_center, z_center])
        cylinder(d = d, h = h, center = true);
}

module m6_hex_prism(af, h, x_center, y_center, z_center) {
    // Across-flats hexagonal pocket for the supplied M6 lock nut.
    translate([x_center, y_center, z_center])
        cylinder(r = af / (2 * cos(30)), h = h, $fn = 6, center = true);
}

module m6_slot_x_y(x_center, y_center, z_center, length, d = m6_stage_bolt_d) {
    hull() {
        for (y_position = [y_center - length / 2,
                           y_center + length / 2]) {
            m6_cylinder_x(d, 24, x_center, y_position, z_center);
        }
    }
}

module m6_slot_x_z(x_center, y_center, z_center, length, d = m6_stage_bolt_d) {
    hull() {
        for (z_position = [z_center - length / 2,
                           z_center + length / 2]) {
            m6_cylinder_x(d, 24, x_center, y_center, z_position);
        }
    }
}

module m6_slot_x_z_span(x_center, y_center, z_center, length, x_span,
                        d = m6_stage_bolt_d) {
    hull() {
        for (z_position = [z_center - length / 2,
                           z_center + length / 2]) {
            m6_cylinder_x(d, x_span, x_center, y_center, z_position);
        }
    }
}

module m6_hex_prism_x(af, h, x_center, y_center, z_center) {
    translate([x_center, y_center, z_center])
        rotate([0, 90, 0])
            rotate([0, 0, 30])
                cylinder(r = af / (2 * cos(30)), h = h,
                         $fn = 6, center = true);
}

module m6_hex_prism_y(af, h, x_center, y_center, z_center) {
    // Hexagonal pocket normal to the rear y- face.  The 30° phase keeps two
    // flats horizontal in the x/z section, matching a typical M6 nut.
    translate([x_center, y_center, z_center])
        rotate([90, 0, 0])
            rotate([0, 0, 30])
                cylinder(r = af / (2 * cos(30)), h = h,
                         $fn = 6, center = true);
}

module m6_rounded_rect_prism_x(length_x, width_y, height_z, radius,
                               x_center, y_center, z_center) {
    // A rounded-rectangle cross section swept along x.  The hull of four
    // x-axis cylinders remains a single watertight solid and avoids a
    // printer-hostile minkowski stack on the long covers.
    hull() {
        for (y_offset = [-width_y / 2 + radius,
                         width_y / 2 - radius]) {
            for (z_offset = [-height_z / 2 + radius,
                             height_z / 2 - radius]) {
                m6_cylinder_x(
                    2 * radius,
                    length_x,
                    x_center,
                    y_center + y_offset,
                    z_center + z_offset);
            }
        }
    }
}

// -----------------------------------------------------------------------------
// M6 cover top-view footprints (z+)
//
// The user's sketch is a plan view with the optical/front x- end represented by
// a positive semicircular/elliptic arc and the cable/rear x+ end represented by
// a rounded rectangle.  These are 2-D footprints extruded in z; the split is
// only a cover parting boundary and no center cable/bridge line is modeled.

module m6_detector_front_arc_footprint_positive() {
    front_length_x =
        m6_detector_shell_front_max_x - m6_detector_shell_min_x;
    y_center =
        (m6_detector_shell_min_y + m6_detector_shell_max_y) / 2;
    polygon(points = concat(
        [[m6_detector_shell_front_max_x, m6_detector_shell_min_y]],
        [for (angle = [-90:5:90])
            [m6_detector_shell_front_max_x -
                 front_length_x * cos(angle),
             y_center + m6_detector_shell_width_y / 2 * sin(angle)]],
        [[m6_detector_shell_front_max_x, m6_detector_shell_max_y]]));
}

module m6_detector_rear_rounded_footprint_positive() {
    rear_length_x =
        m6_detector_shell_max_x - m6_detector_shell_rear_min_x;
    y_center =
        (m6_detector_shell_min_y + m6_detector_shell_max_y) / 2;
    translate([
        (m6_detector_shell_rear_min_x + m6_detector_shell_max_x) / 2,
        y_center])
        offset(r = m6_detector_shell_corner_radius)
            square([
                rear_length_x - 2 * m6_detector_shell_corner_radius,
                m6_detector_shell_width_y -
                    2 * m6_detector_shell_corner_radius],
                center = true);
}

module m6_detector_shell_footprint_positive() {
    union() {
        m6_detector_front_arc_footprint_positive();
        m6_detector_rear_rounded_footprint_positive();
    }
}

module m6_countersink_x(x_entry, direction, length_x, y_center, z_center,
                        pilot_d, head_d, head_depth) {
    // Explicit countersink: the broad cone mouth is at x_entry and the
    // smaller pilot continues in the selected direction.  This is distinct
    // from a counterbore and is used for the cover's flush M3/M4 screws.
    m6_cylinder_x(
        pilot_d,
        length_x,
        x_entry + direction * length_x / 2,
        y_center,
        z_center);
    translate([x_entry, y_center, z_center])
        rotate([0, direction * 90, 0])
            cylinder(d1 = head_d, d2 = pilot_d,
                     h = head_depth, center = false);
}

module m6_countersink_z(z_entry, direction, length_z, x_center, y_center,
                        pilot_d, head_d, head_depth) {
    // Vertical equivalent for the removable bottom cover.
    m6_cylinder_z(
        pilot_d,
        length_z,
        x_center,
        y_center,
        z_entry + direction * length_z / 2);
    translate([x_center, y_center, z_entry])
        rotate([direction < 0 ? 180 : 0, 0, 0])
            cylinder(d1 = head_d, d2 = pilot_d,
                     h = head_depth, center = false);
}

module m6_slot_y_z(x_center, y_center, z_center, length, d = m6_stage_bolt_d) {
    hull() {
        for (z_position = [z_center - length / 2,
                           z_center + length / 2]) {
            m6_cylinder_y(d, 24, x_center, y_center, z_position);
        }
    }
}

module m6_arc_slot_z(x_center, y_center, z_center, radius,
                     center_angle, half_angle, d = m6_stage_bolt_d) {
    // Small-angle arc slot for the real z-axis yaw turntable.  A faceted
    // swept slot is intentional here: it is easy to machine or waterjet and
    // leaves the two M6 clamp bolts as the load path after adjustment.
    hull() {
        for (angle = [center_angle - half_angle:1:center_angle + half_angle]) {
            m6_cylinder_z(
                d,
                m6_yaw_stage_t + 4,
                x_center + radius * cos(angle),
                y_center + radius * sin(angle),
                z_center);
        }
    }
}

module m6_sensor_rail_positive() {
    // 旧版兼容诊断件：这是铝合金梳齿方案的 1:1 外形和攻牙位置，不是
    // 当前 T 形主体主线，也不是 PETG 打印件。保留它只为历史回溯。
    // 竖直背骨承接十个水平托舌；每个托舌有一个 M6×0.75 竖直攻牙孔。
    // 偶数/奇数通道的托舌沿 y 交错，避免 14 mm 安装杆在 10 mm 节距上相撞。
    color("silver")
        difference() {
            union() {
                translate([m6_sensor_rail_x,
                           -m6_rail_width_y / 2,
                           m6_array_bottom_z])
                    cube([m6_rail_t, m6_rail_width_y, m6_rail_length_z]);
                for (index = [0:m6_sensor_count - 1]) {
                    translate([m6_rail_tab_min_x,
                               m6_sensor_lane_y(index) - m6_rail_tab_width_y / 2,
                               m6_sensor_tab_z(index) - m6_rail_tab_t / 2])
                        cube([m6_rail_tab_max_x - m6_rail_tab_min_x,
                              m6_rail_tab_width_y,
                              m6_rail_tab_t]);
                    // The vendor drawing shows a pair of M6 nuts under the
                    // right-angle head.  A captured hex pocket lets the nut
                    // clamp the head without allowing the L-body to rotate
                    // while the channel height is being tuned.
                    translate([m6_sensor_mount_hole_x - m6_sensor_guard_outer_d / 2,
                               m6_sensor_lane_y(index) - m6_sensor_guard_outer_d / 2,
                               m6_sensor_tab_z(index) + m6_rail_tab_t / 2])
                        cube([m6_sensor_guard_outer_d,
                              m6_sensor_guard_outer_d,
                              m6_sensor_guard_h]);
                }
            }
            // The right-angle body/cable sleeve crosses the backbone after
            // the head.  Leave a 1 mm radial envelope so the bought part can
            // pass through the aluminum rail without being clamped by it.
            for (index = [0:m6_sensor_count - 1]) {
                m6_cylinder_x(
                    m6_sensor_body_clearance_d,
                    m6_rail_t + 2,
                    m6_sensor_rail_x + m6_rail_t / 2,
                    m6_sensor_lane_y(index),
                    m6_sensor_z(index));
            }
            for (index = [0:m6_sensor_count - 1]) {
                // OpenSCAD 显示锁紧螺母六角窝和 M6×0.75 通孔；实际加工图
                // 可选“攻牙孔”或“通孔 + 防转螺母”，以卖家螺纹/螺母为准。
                m6_hex_prism(
                    m6_sensor_lock_nut_af +
                        2 * m6_sensor_nut_pocket_clearance,
                    m6_sensor_lock_nut_h +
                        m6_sensor_nut_pocket_clearance,
                    m6_sensor_mount_hole_x,
                    m6_sensor_lane_y(index),
                    m6_sensor_tab_z(index) + m6_rail_tab_t / 2 +
                        m6_sensor_guard_h -
                        (m6_sensor_lock_nut_h +
                         m6_sensor_nut_pocket_clearance) / 2);
                m6_cylinder_z(
                    m6_sensor_tap_visual_d,
                    m6_rail_tab_t + m6_sensor_guard_h + 4,
                    m6_sensor_mount_hole_x,
                    m6_sensor_lane_y(index),
                    m6_sensor_tab_z(index) + m6_sensor_guard_h / 2);
            }
            // The current production bar has no custom yaw/pitch/roll bearing
            // pattern.  Its rear plate and the purchased ball head provide the
            // adjustment interface; do not reintroduce the legacy roll-disc
            // holes into this single vertical sensor bar.
        }
}

module m6_sensor_test_coupon_positive() {
    // 旧版兼容诊断件：coupon 是低成本的梳齿托舌配合检查，不属于当前
    // T 形长条主体；保留它只用于历史资料/旧几何回归。
    //
    // The coupon hole is clearance, not a claim about the final M6×0.75 tap.
    // The real sensor is installed from the top; its hex nut sits in the open
    // pocket while the threaded stem passes through the tab.
    tab_min_x = m6_sensor_test_coupon_tab_min_local_x;
    tab_max_x = m6_rail_t;
    mount_hole_x = m6_sensor_test_coupon_mount_hole_local_x;
    lane_y = -m6_sensor_lane_offset_y;
    tab_center_z = m6_rail_tab_t / 2;
    tab_top_z = tab_center_z + m6_rail_tab_t / 2;
    guard_bottom_z = tab_top_z - m6_sensor_test_coupon_guard_overlap;
    guard_top_z = guard_bottom_z + m6_sensor_guard_h +
                  m6_sensor_test_coupon_guard_overlap;
    pocket_depth = m6_sensor_lock_nut_h + m6_sensor_nut_pocket_clearance;
    sensor_z = tab_center_z + m6_sensor_mount_plane_offset_z +
               m6_rail_tab_t / 2;
    color("lightgray")
        difference() {
            union() {
                translate([0,
                           -m6_rail_width_y / 2,
                           0])
                    cube([m6_rail_t,
                          m6_rail_width_y,
                          m6_sensor_test_coupon_backbone_h]);
                translate([tab_min_x,
                           lane_y - m6_rail_tab_width_y / 2,
                           tab_center_z - m6_rail_tab_t / 2])
                    cube([tab_max_x - tab_min_x,
                          m6_rail_tab_width_y,
                          m6_rail_tab_t]);
                // Overlap the guard into the tab by 0.2 mm so the coupon is
                // one printable solid rather than two merely touching boxes.
                translate([mount_hole_x - m6_sensor_guard_outer_d / 2,
                           lane_y - m6_sensor_guard_outer_d / 2,
                           guard_bottom_z])
                    cube([m6_sensor_guard_outer_d,
                          m6_sensor_guard_outer_d,
                          m6_sensor_guard_h +
                              m6_sensor_test_coupon_guard_overlap]);
            }
            // The real right-angle body/cable sleeve must be able to cross
            // the short backbone without being pinched by the sample.
            m6_cylinder_x(
                m6_sensor_body_clearance_d,
                m6_rail_t + 2,
                m6_rail_t / 2,
                lane_y,
                sensor_z);
            // Nut pocket opens at the guard top.  The smaller vertical hole
            // continues through both guard and tab for the M6 stem.
            m6_hex_prism(
                m6_sensor_lock_nut_af +
                    2 * m6_sensor_nut_pocket_clearance,
                pocket_depth,
                mount_hole_x,
                lane_y,
                guard_top_z - pocket_depth / 2);
            m6_cylinder_z(
                m6_sensor_test_coupon_clearance_d,
                guard_top_z + 4,
                mount_hole_x,
                lane_y,
                guard_top_z / 2);
        }
}

module m6_sensor_body_positive(index) {
    z0 = m6_sensor_z(index);
    y0 = m6_sensor_lane_y(index);
    thread_center_x =
        m6_sensor_thread_start_x + m6_sensor_mount_stem_length / 2;
    // Legacy standalone sensor proxy. The purchased right-angle device still
    // has a horizontal optical/M6 axis; the blue guard and cable are the
    // perpendicular local-z branch.
    color("dimgray")
        translate([m6_sensor_axis_x,
                   y0 - m6_sensor_head_width_y / 2,
                   z0 - m6_sensor_head_height_z / 2])
            cube([m6_sensor_head_length_x,
                  m6_sensor_head_width_y,
                  m6_sensor_head_height_z]);
    color("silver")
        m6_cylinder_x(
            m6_sensor_thread_d,
            m6_sensor_mount_stem_length,
            thread_center_x,
            y0,
            z0);
    color("royalblue")
        m6_cylinder_z(
            m6_sensor_body_d,
            m6_sensor_cable_guard_length,
            m6_sensor_cable_exit_x,
            y0,
            z0 - m6_sensor_head_height_z / 2 -
                m6_sensor_cable_guard_length / 2);
    color("black")
        m6_cylinder_z(
            m6_sensor_cable_d,
            m6_sensor_cable_preview_length,
            m6_sensor_cable_exit_x,
            y0,
            z0 - m6_sensor_head_height_z / 2 -
                m6_sensor_cable_guard_length -
                m6_sensor_cable_preview_length / 2);
    color("black")
        m6_cylinder_x(
            m6_sensor_face_d,
            1,
            m6_sensor_axis_x - 0.5,
            y0,
            z0);
}

module m6_sensor_array_positive() {
    // Public/current PART name now follows the rear-inserted long body.  The
    // old comb remains available as PART=m6_sensor_rail for diagnostics.
    m6_detector_body_positive();
    m6_detector_sensor_array_positive();
}

module m6_mount_adapter_positive() {
    // 两条竖向长孔（左右各一）与当前网夹/立柱的同轴长孔组成穿栓接口；
    // 孔位保留 ±6 mm 高度余量。真实商品网夹若不是当前 28×38 mm 立柱，
    // 仍需按实物改过渡板或孔距，不能把本接口当成商品夹具的量测结果。
    color("lightgray")
        difference() {
            translate([m6_mount_plate_x,
                       -m6_mount_plate_width_y / 2,
                       m6_array_center_z - m6_mount_plate_height_z / 2])
                cube([m6_mount_plate_t,
                      m6_mount_plate_width_y,
                      m6_mount_plate_height_z]);
            for (y_position = [-m6_post_mount_hole_y,
                               m6_post_mount_hole_y]) {
                m6_slot_x_z_span(
                    post_center_x,
                    y_position,
                    m6_post_mount_hole_z,
                    m6_mount_slot_length,
                    post_body_width + m6_mount_plate_t + 8,
                    m6_post_mount_clearance_d);
            }
            // Current active pattern: two visible holes at the 90° bracket
            // shelf level.  The legacy yaw/ballhead hole pattern is no longer
            // cut here; it made the vertical adapter look like the discarded
            // horizontal three-axis mechanism.
            for (z_position = [m6_post_mount_hole_z - 6,
                               m6_post_mount_hole_z + 6]) {
                m6_cylinder_x(
                    m6_detector_support_fastener_d,
                    m6_mount_plate_t + 4,
                    m6_mount_plate_x + m6_mount_plate_t / 2,
                    m6_detector_support_y,
                    z_position);
            }
        }
}

module m6_post_mount_hardware_positive() {
    // Two gold through-bolt stacks make the adapter-to-upright load path
    // visible in the assembly preview.  The final washer/nut stack and length
    // remain a first-article measurement item.
    for (y_position = [-m6_post_mount_hole_y,
                       m6_post_mount_hole_y]) {
        color("gold")
            m6_cylinder_x(
                m6_post_mount_clearance_d - 1,
                m6_post_mount_bolt_length,
                post_center_x,
                y_position,
                m6_post_mount_hole_z);
        color("gold")
            m6_hex_prism_x(
                m6_sensor_lock_nut_af,
                m6_sensor_lock_nut_h,
                m6_mount_plate_x - m6_sensor_lock_nut_h / 2,
                y_position,
                m6_post_mount_hole_z);
        color("gold")
            m6_hex_prism_x(
                m6_sensor_lock_nut_af,
                m6_sensor_lock_nut_h,
                post_center_x + post_body_width / 2 +
                    m6_sensor_lock_nut_h / 2,
                y_position,
                m6_post_mount_hole_z);
    }
}

module m6_detector_backplate_positive() {
    // This is the metal rear plate of the detector assembly.  It overlaps
    // the single vertical sensor bar by 0.5 mm and presents one central M6
    // hole plus two anti-rotation holes to the purchased ball head.  The
    // plate is therefore the only custom interface between the sensor metal
    // work and the commercial 13 mm ball.
    color("silver")
        difference() {
            translate([m6_detector_backplate_x,
                       -m6_detector_backplate_width_y / 2,
                       m6_array_center_z - m6_detector_backplate_height_z / 2])
                cube([m6_detector_backplate_t,
                      m6_detector_backplate_width_y,
                      m6_detector_backplate_height_z]);
            m6_cylinder_x(
                m6_detector_backplate_mount_clearance_d,
                m6_detector_backplate_t + 4,
                m6_detector_backplate_x + m6_detector_backplate_t / 2,
                0,
                m6_ballhead_axis_z);
            for (y_position = [-m6_detector_backplate_lock_hole_y,
                               m6_detector_backplate_lock_hole_y]) {
                m6_cylinder_x(
                    m6_detector_backplate_anti_rotation_d,
                    m6_detector_backplate_t + 4,
                    m6_detector_backplate_x + m6_detector_backplate_t / 2,
                    y_position,
                    m6_ballhead_axis_z);
            }
        }
}

module m6_ballhead_positive() {
    // Purchased 13 mm mini ball head proxy.  The actual metal head supplies
    // 360° rotation and 90° opening; these simple envelopes only show the
    // clear load path and the two M6 external-thread interfaces.
    color("silver") {
        translate([m6_ballhead_center_x, 0, m6_ballhead_axis_z])
            sphere(d = m6_ballhead_ball_d, $fn = 32);
        m6_cylinder_x(
            m6_ballhead_housing_d,
            m6_ballhead_housing_length_x,
            m6_ballhead_center_x,
            0,
            m6_ballhead_axis_z);
        m6_cylinder_x(
            m6_ballhead_base_d,
            m6_ballhead_base_t,
            m6_ballhead_base_center_x,
            0,
            m6_ballhead_axis_z);
        m6_cylinder_x(
            m6_ballhead_sensor_stud_d,
            m6_ballhead_sensor_stud_length + 2,
            m6_ballhead_sensor_stud_center_x,
            0,
            m6_ballhead_axis_z);
        m6_cylinder_x(
            m6_ballhead_net_stud_d,
            m6_ballhead_net_stud_length,
            m6_ballhead_net_stud_center_x,
            0,
            m6_ballhead_axis_z);
        // The two small pins are only an assembly proxy for the anti-rotation
        // pattern in the detector backplate; verify the vendor head geometry.
        for (y_position = [-m6_detector_backplate_lock_hole_y,
                           m6_detector_backplate_lock_hole_y]) {
            m6_cylinder_x(
                m6_detector_backplate_anti_rotation_d - 0.5,
                m6_ballhead_sensor_stud_length,
                m6_ballhead_sensor_stud_center_x,
                y_position,
                m6_ballhead_axis_z);
        }
    }
    color("dimgray")
        m6_cylinder_y(
            18,
            8,
            m6_ballhead_center_x,
            -m6_ballhead_housing_d / 2 - 2,
            m6_ballhead_axis_z);
}

module m6_ballhead_net_hardware_positive() {
    // The net-side adapter carries the selected M6-external thread with a
    // washer/nut stack.  If the purchased variant uses 1/4, 3/8, M8 or M10,
    // only this adapter hole/fastener pair changes; the sensor backplate and
    // the single vertical bar remain unchanged.
    color("gold") {
        m6_hex_prism_x(
            m6_sensor_lock_nut_af,
            m6_sensor_lock_nut_h,
            m6_mount_plate_x - m6_sensor_lock_nut_h / 2,
            0,
            m6_ballhead_axis_z);
        m6_hex_prism_x(
            m6_sensor_lock_nut_af,
            m6_sensor_lock_nut_h,
            post_center_x + post_body_width / 2 +
                m6_sensor_lock_nut_h / 2,
            0,
            m6_ballhead_axis_z);
    }
}

module m6_ballhead_mount_positive() {
    m6_mount_adapter_positive();
    m6_post_mount_hardware_positive();
    m6_detector_backplate_positive();
    m6_ballhead_positive();
    m6_ballhead_net_hardware_positive();
    m6_sensor_array_positive();
}

// -----------------------------------------------------------------------------
// 当前主体主线：L 型 M6 传感器 + x 轴 45° 让线旋转
//
// The optical channel and M6 threaded barrel remain on the x axis. In the
// local sensor frame the blue cable guard exits z-, then the complete
// purchased-device proxy is rolled -45° about x; that cable branch therefore
// points toward y-/z-. The active aperture is the hollow threaded-barrel tip;
// there is no separate black optical face on the gray hex.
// The aluminum body is a solid, wide x-direction carrier centered at y=0. It
// has ten optical/head openings and shallow rear hex seats. The M6 thread is
// a simple clearance pass-through; one purchased nut sits on the outside
// face. The cable stays outside the aluminum and is not pocketed.
// The PETG covers are separate protection/relief parts; they do not replace
// the aluminum bar or its integral T-tail as the sensor datum or primary
// structural member.

module m6_sensor_roll_frame(index) {
    z0 = m6_sensor_z(index);
    translate([m6_sensor_axis_x, 0, z0])
        rotate([m6_sensor_roll_deg, 0, 0])
            translate([-m6_sensor_axis_x, 0, -z0])
                children();
}

module m6_detector_body_t_tail_positive() {
    // The body is one machined aluminum part: the 10 x 56 x 216 mm vertical
    // bar is the stem of the top-view T, while this wider x-direction head
    // grows from its y- edge.  The head overlaps the bar by 0.8 mm in y so
    // the CSG result is a real connected solid, not a coincident attachment.
    translate([m6_detector_support_tail_min_x,
               m6_detector_support_tail_min_y,
               m6_detector_support_tail_bottom_z])
        cube([m6_detector_support_tail_width_x,
              m6_detector_support_tail_head_depth_y,
              m6_detector_support_tail_height_z]);
}

module m6_detector_body_envelope_positive() {
    // Keep the central bar dimensions explicit while adding the integral
    // T-tail that carries the M8 female interface directly into aluminum.
    union() {
        translate([m6_detector_body_min_x,
                   m6_detector_body_min_y,
                   m6_detector_body_bottom_z])
            cube([m6_detector_body_length_x,
                  m6_detector_body_depth_y,
                  m6_detector_body_height_z]);
        m6_detector_body_t_tail_positive();
    }
}

module m6_detector_body_tail_thread_void_positive() {
    // The supplier's M8 external ballhead stud enters from the positive x
    // face of the T-head.  A real M8x1.25 blind tap is represented by its
    // 6.8 mm tap-drill core plus a 9.5 mm entry chamfer; the helix itself is
    // left to the machinist rather than approximated by a fragile STL thread.
    m6_countersink_x(
        m6_detector_support_tail_thread_entry_x + 0.1,
        -1,
        m6_detector_support_tail_thread_depth_x + 0.2,
        m6_detector_support_y,
        m6_detector_support_boss_center_z,
        m6_detector_support_tail_tap_drill_d,
        m6_detector_support_tail_thread_mouth_d,
        m6_detector_support_tail_thread_mouth_depth_x);
}

module m6_detector_sensor_fit_voids_positive() {
    // One shared subtraction defines the actual first-article interface for
    // both the printable preview and the machined aluminum body.  The round
    // clearance is the hollow M6 optical barrel; the shallow AF8 pocket is
    // only 2.1 mm deep, so the gray head shoulder stops with 2 mm captured
    // instead of passing through the 10 mm bar.
    for (index = [0:m6_sensor_count - 1]) {
        z0 = m6_sensor_z(index);
        m6_cylinder_x(
            m6_detector_thread_clearance_d,
            m6_detector_body_length_x + 2,
            m6_detector_body_center_x,
            m6_detector_sensor_head_center_y,
            z0);
        m6_sensor_roll_frame(index)
            m6_hex_prism_x(
                m6_detector_hex_pocket_af,
                m6_detector_hex_pocket_depth_x,
                m6_detector_body_max_x -
                    m6_detector_hex_pocket_depth_x / 2,
                m6_detector_sensor_head_center_y,
                z0);
    }
}

module m6_detector_body_positive() {
    color("silver")
        difference() {
            m6_detector_body_envelope_positive();

            m6_detector_sensor_fit_voids_positive();
            m6_detector_body_tail_thread_void_positive();

            // Do not cut a diagonal cable trench into the aluminum. The
            // rotated blue guard and stripped cable leave on the outside face
            // and remain visible in the assembly preview.

            // Two pairs of M3/M4 cover pilot holes enter from the optical and
            // cable sides.  The countersink lives in the removable covers.
            for (y_position = m6_detector_shell_screw_y) {
                for (z_position = m6_detector_body_screw_z) {
                    m6_cylinder_x(
                        m6_detector_shell_screw_pilot_d,
                        m6_detector_body_length_x + 2,
                        m6_detector_body_center_x,
                        y_position,
                        z_position);
                }
            }

            // Bottom-cover pilot holes are blind in the metal body; the PETG
            // cover supplies the visible countersink.
            for (x_position = m6_detector_bottom_screw_x) {
                m6_cylinder_z(
                    m6_detector_bottom_cover_screw_d,
                    m6_bottom_cover_screw_depth,
                    x_position,
                    m6_detector_body_center_y,
                    m6_detector_body_bottom_z +
                        m6_bottom_cover_screw_depth / 2);
            }

            // A vertical pair of edge grooves gives each x-half of the cover
            // a captured tongue.  They are guides, not the primary load path.
            for (y_side = [-1, 1]) {
                translate([
                    m6_detector_body_center_x -
                        m6_detector_body_groove_width_x / 2,
                    y_side > 0
                        ? m6_detector_body_max_y -
                            m6_detector_body_groove_depth_y
                        : m6_detector_body_min_y,
                    m6_detector_body_bottom_z +
                        m6_detector_body_groove_margin_z])
                    cube([m6_detector_body_groove_width_x,
                          m6_detector_body_groove_depth_y,
                          m6_detector_body_height_z -
                              2 * m6_detector_body_groove_margin_z]);
            }
        }
}

// Minimal first-article fit probe.  This deliberately contains only the
// long rectangular aluminum bar and the real purchased L-shaped sensor model:
// gray hex head, hollow M6 optical barrel, blue right-angle guard, and short
// cable proxy.  The head enters from the outward face, overlaps the body by
// 2 mm, and stops there; one supplied lock nut is placed on the smooth inner
// body face. Covers, screws, brackets, and gimbals remain outside this probe.
module m6_detector_fit_body_positive() {
    color("silver")
        difference() {
            m6_detector_body_envelope_positive();

            m6_detector_sensor_fit_voids_positive();
            m6_detector_body_tail_thread_void_positive();
        }
}

module m6_detector_fit_sensor_positive(index) {
    m6_detector_sensor_installed_positive(index);
}

module m6_detector_fit_probe_positive() {
    m6_detector_fit_body_positive();
    for (index = [0:m6_sensor_count - 1]) {
        m6_detector_fit_sensor_positive(index);
    }
}

module m6_detector_sensor_local_positive(index, show_nut = true) {
    z0 = m6_sensor_z(index);
    thread_center_x =
        m6_sensor_thread_start_x + m6_sensor_mount_stem_length / 2;
    // Local frame before the -45° roll: the hollow M6 optical barrel runs
    // horizontally along x; only the blue strain relief and black cable point
    // down along local z-. The blue right-angle branch terminates at the
    // purchased gray hex body. It is not an x-axis cable body.
    color("dimgray")
        m6_hex_prism_x(
            m6_sensor_head_hex_af,
            m6_sensor_head_length_x,
            m6_sensor_head_center_x,
            m6_detector_sensor_head_center_y,
            z0);
    // The silver M6 section is a hollow optical barrel, not a solid mounting
    // screw. Keep the shell visible and remove its center all the way to the
    // tip; the dark end disk only marks the actual emit/receive aperture.
    color("silver")
        difference() {
            m6_cylinder_x(
                m6_sensor_thread_d,
                m6_sensor_mount_stem_length,
                thread_center_x,
                m6_detector_sensor_head_center_y,
                z0);
            m6_cylinder_x(
                m6_sensor_optical_bore_d,
                m6_sensor_mount_stem_length + 0.4,
                thread_center_x,
                m6_detector_sensor_head_center_y,
                z0);
        }
    color("royalblue")
        m6_cylinder_z(
            m6_sensor_body_d,
            m6_sensor_cable_guard_length,
            m6_sensor_cable_exit_x,
            m6_detector_sensor_body_center_y,
            z0 - m6_sensor_head_height_z / 2 -
                m6_sensor_cable_guard_length / 2);
    color("black")
        m6_cylinder_z(
            m6_sensor_cable_d,
            m6_sensor_cable_preview_length,
            m6_sensor_cable_exit_x,
            m6_detector_sensor_body_center_y,
            z0 - m6_sensor_head_height_z / 2 -
                m6_sensor_cable_guard_length -
                m6_sensor_cable_preview_length / 2);
    color("black")
        m6_cylinder_x(
            m6_sensor_optical_bore_d,
            0.4,
            m6_sensor_optical_aperture_x + 0.2,
            m6_detector_sensor_head_center_y,
            z0);
    // The M6 thread simply passes through the aluminum carrier. Only one
    // purchased nut is shown, seated directly on the outward body face; there
    // is no second nut and no printed fixing screw embedded in the body.
    if (show_nut) {
        color("gold")
            m6_hex_prism_x(
                m6_sensor_lock_nut_af,
                m6_sensor_lock_nut_h,
                m6_detector_sensor_nut_base_center_x,
                m6_detector_sensor_head_center_y,
                z0);
    }
}

module m6_detector_sensor_positive(index, show_nut = true) {
    m6_sensor_roll_frame(index)
        // Positive geometry is installed on the right receiver. The gray
        // hex/cable side stays at x+ against the shallow pocket; the hollow
        // threaded optical barrel points inward toward x- through the body.
        translate([2 * m6_sensor_head_center_x, 0, 0])
            mirror([1, 0, 0])
                m6_detector_sensor_local_positive(index, show_nut);
}

module m6_detector_sensor_installed_positive(index, show_nut = true) {
    // The raw purchased-device proxy is kept at its vendor-reference x
    // coordinates for the single-sensor preview.  The installed detector
    // translates the complete real L-shaped part so its AF8 head inner
    // shoulder is exactly 2 mm inside the aluminum body.  The only hardware
    // added here is one supplied nut on the smooth opposite body face.
    translate([m6_detector_sensor_install_offset_x, 0, 0])
        m6_detector_sensor_positive(index, false);
    if (show_nut) {
        z0 = m6_sensor_z(index);
        m6_sensor_roll_frame(index)
            color("gold")
                m6_hex_prism_x(
                    m6_sensor_lock_nut_af,
                    m6_sensor_lock_nut_h,
                    m6_detector_fit_nut_center_x,
                    m6_detector_sensor_head_center_y,
                    z0);
    }
}

module m6_detector_sensor_array_positive() {
    for (index = [0:m6_sensor_count - 1]) {
        m6_detector_sensor_installed_positive(index);
    }
}

// Inspection-only single purchased sensor.  The local origin is the optical
// axis at the first channel, so the standalone output is easy to read without
// the table, aluminum body, shell, gimbal, or clamp. SIDE=1 is the right
// receiver (hollow threaded tip toward -x); SIDE=-1 is its mirrored left
// emitter (hollow threaded tip toward +x).
module m6_sensor_single_preview(side = 1) {
    z0 = m6_sensor_z(0);
    if (side >= 0) {
        translate([-m6_sensor_head_center_x,
                   -m6_detector_sensor_head_center_y,
                   -z0])
            m6_detector_sensor_positive(0);
    } else {
        translate([m6_sensor_head_center_x,
                   -m6_detector_sensor_head_center_y,
                   -z0])
            mirror([1, 0, 0])
                m6_detector_sensor_positive(0);
    }
}

module m6_sensor_single_direction_preview(side = 1) {
    single_optical_tip_x =
        m6_sensor_head_center_x - m6_sensor_optical_aperture_x;
    if (side >= 0) {
        // Right receiver: incoming +x beam terminates at the hollow tip.
        m6_optical_arrow_x(single_optical_tip_x - 35,
                           single_optical_tip_x,
                           0,
                           0);
    } else {
        // Left emitter: outgoing +x beam leaves the mirrored hollow tip.
        m6_optical_arrow_x(
            -single_optical_tip_x,
            -single_optical_tip_x + 30,
            0,
            0);
    }
}

module m6_detector_front_outer_positive() {
    // Positive front arc in the z+ footprint; the inner x- opening below
    // leaves the hollow M6 optical tip unobstructed.
    translate([0, 0, m6_detector_shell_bottom_z])
        linear_extrude(height = m6_detector_shell_height_z, convexity = 10)
            m6_detector_front_arc_footprint_positive();
}

module m6_detector_shell_tongue_positive(x_side, y_side) {
    // Each y edge has one continuous vertical groove in the aluminum body.
    // The x- optical cover and x+ cable cover share that same groove, each
    // occupying one x half. The root runs back to the shell side wall so the
    // tongue is a connected guide feature rather than a floating insert.
    tongue_width_x = max(
        0.5,
        m6_detector_body_groove_width_x / 2 -
            2 * m6_detector_shell_tongue_clearance);
    tongue_min_x = x_side < 0
        ? m6_detector_body_center_x -
            m6_detector_body_groove_width_x / 2 +
            m6_detector_shell_tongue_clearance
        : m6_detector_body_center_x +
            m6_detector_shell_tongue_clearance;
    groove_min_y = y_side > 0
        ? m6_detector_body_max_y - m6_detector_body_groove_depth_y
        : m6_detector_body_min_y;
    tongue_min_y = y_side > 0
        ? groove_min_y + m6_detector_shell_tongue_clearance
        : m6_detector_shell_inner_min_y - 0.2;
    tongue_depth_y = y_side > 0
        ? m6_detector_shell_inner_max_y + 0.2 - tongue_min_y
        : m6_detector_body_min_y +
            m6_detector_body_groove_depth_y -
            m6_detector_shell_tongue_clearance - tongue_min_y;
    translate([tongue_min_x,
               tongue_min_y,
               m6_detector_body_bottom_z +
                   m6_detector_body_groove_margin_z])
        cube([tongue_width_x,
              tongue_depth_y,
              m6_detector_body_height_z -
                  2 * m6_detector_body_groove_margin_z]);
}

module m6_detector_shell_front_outer_positive() {
    // Front/optical cover is the x- segment of the positive spherical-arc
    // envelope. It spans the full y width and is not a y+ half.
    intersection() {
        m6_detector_front_outer_positive();
        translate([m6_detector_shell_min_x - 1,
                   m6_detector_shell_min_y - 1,
                   m6_detector_shell_bottom_z - 1])
            cube([m6_detector_shell_front_max_x -
                      m6_detector_shell_min_x + 2,
                  m6_detector_shell_width_y + 2,
                  m6_detector_shell_height_z + 2]);
    }
}

module m6_detector_shell_rear_outer_positive() {
    // Rear/cable cover is the x+ segment of the rounded-rectangle envelope.
    // The y- region is later relieved around the integral aluminum T-tail;
    // the rear cover itself is not a structural boss.
    intersection() {
        translate([0, 0, m6_detector_shell_bottom_z])
            linear_extrude(height = m6_detector_shell_height_z,
                           convexity = 10)
                m6_detector_rear_rounded_footprint_positive();
        translate([m6_detector_shell_rear_min_x - 1,
                   m6_detector_shell_min_y - 1,
                   m6_detector_shell_bottom_z - 1])
            cube([m6_detector_shell_max_x -
                      m6_detector_shell_rear_min_x + 2,
                  m6_detector_shell_width_y + 2,
                  m6_detector_shell_height_z + 2]);
    }
}

module m6_detector_shell_inner_segment_positive(x_min, x_max) {
    translate([x_min,
               m6_detector_shell_inner_min_y,
               m6_detector_shell_inner_bottom_z])
        cube([x_max - x_min,
              m6_detector_shell_inner_max_y -
                  m6_detector_shell_inner_min_y,
              m6_detector_shell_inner_top_z -
                  m6_detector_shell_inner_bottom_z]);
}

module m6_detector_front_optical_holes_positive() {
    // The enlarged x- front cap is a bulkhead.  Only the ten optical-axis
    // bores cross it; the real AF8 heads, blue guards, and supplied nuts are
    // all recessed behind this wall.
    for (index = [0:m6_sensor_count - 1]) {
        m6_cylinder_x(
            m6_detector_optical_bore_d,
            m6_detector_shell_wall + 2,
            m6_detector_shell_min_x + m6_detector_shell_wall / 2,
            m6_detector_sensor_head_center_y,
            m6_sensor_z(index));
    }
}

module m6_detector_body_tail_clearance_positive() {
    // Rear PETG is cut away around the T-tail with clearance.  The cutout is
    // deliberately larger than the tail envelope so the shell cannot become
    // a hidden load-bearing substitute for the aluminum body.
    translate([m6_detector_support_tail_min_x - m6_detector_shell_clearance,
               m6_detector_support_tail_min_y - m6_detector_shell_clearance,
               m6_detector_support_tail_bottom_z -
                   m6_detector_shell_clearance])
        cube([m6_detector_support_tail_width_x +
                  2 * m6_detector_shell_clearance,
              m6_detector_support_tail_head_depth_y +
                  2 * m6_detector_shell_clearance,
              m6_detector_support_tail_height_z +
                  2 * m6_detector_shell_clearance]);
}

module m6_detector_shell_front_positive(alpha = m6_detector_shell_alpha) {
    // Front is the optical x- end. It keeps the positive spherical arc, spans
    // full y, owns the x- half of both side grooves, and is fixed from x- by
    // two countersunk screws on the y+ screw track.
    union() {
        color("slategray", alpha)
            difference() {
                m6_detector_shell_front_outer_positive();
                m6_detector_shell_inner_segment_positive(
                    m6_detector_shell_min_x + m6_detector_shell_wall,
                    m6_detector_shell_front_max_x + 1);
                m6_detector_front_optical_holes_positive();
                for (z_position = m6_detector_body_screw_z) {
                    m6_countersink_x(
                        m6_detector_shell_min_x,
                        1,
                        m6_detector_shell_front_max_x -
                            m6_detector_shell_min_x + 2,
                        m6_detector_shell_screw_y[1],
                        z_position,
                        m6_detector_shell_screw_pilot_d,
                        m6_detector_shell_screw_head_d,
                        m6_detector_shell_screw_head_depth);
                }
            }
        for (y_side = [-1, 1])
            m6_detector_shell_tongue_positive(-1, y_side);
    }
}

module m6_detector_shell_rear_positive(alpha = m6_detector_shell_alpha) {
    // Rear is the cable x+ end. It is rounded-rectangle shaped, owns the x+
    // half of both side grooves, and is relieved around the integral body
    // T-tail. It is fixed from x+ by two countersunk screws on the y- track;
    // it does not carry the ballhead bending moment.
    union() {
        color("slategray", alpha)
            difference() {
                m6_detector_shell_rear_outer_positive();
                m6_detector_shell_inner_segment_positive(
                    m6_detector_shell_rear_min_x - 1,
                    m6_detector_shell_inner_max_x + 1);
                m6_detector_body_tail_clearance_positive();
                for (z_position = m6_detector_body_screw_z) {
                    m6_countersink_x(
                        m6_detector_shell_max_x,
                        -1,
                        m6_detector_shell_max_x -
                            m6_detector_shell_rear_min_x + 2,
                        m6_detector_shell_screw_y[0],
                        z_position,
                        m6_detector_shell_screw_pilot_d,
                        m6_detector_shell_screw_head_d,
                        m6_detector_shell_screw_head_depth);
                }
            }
        for (y_side = [-1, 1])
            m6_detector_shell_tongue_positive(1, y_side);
    }
}

module m6_detector_bottom_cover_positive() {
    color("darkslategray")
        difference() {
            translate([0,
                       0,
                       m6_detector_shell_bottom_z -
                           m6_detector_bottom_cover_t])
                linear_extrude(height = m6_detector_bottom_cover_t,
                               convexity = 10)
                    m6_detector_shell_footprint_positive();
            m6_cylinder_z(
                m6_detector_cable_exit_d,
                m6_detector_bottom_cover_t + 2,
                m6_detector_cable_exit_x,
                m6_detector_cable_exit_y,
                m6_detector_shell_bottom_z -
                    m6_detector_bottom_cover_t / 2);
            for (x_position = m6_detector_bottom_screw_x) {
                m6_countersink_z(
                    m6_detector_shell_bottom_z -
                        m6_detector_bottom_cover_t,
                    1,
                    m6_detector_bottom_cover_t + 2,
                    x_position,
                    0,
                    m6_detector_bottom_cover_screw_d,
                    m6_detector_bottom_cover_screw_head_d,
                    m6_detector_bottom_cover_screw_head_depth);
            }
        }
}

module m6_detector_support_positive() {
    // A purchased ball head is not the vertical support by itself.  This
    // metal L bracket runs from the head's lower stud to a vertical leg that
    // overlaps the net-clamp adapter plate; triangular side cheeks close the
    // 90° corner and carry the bending moment.
    color("dimgray")
        union() {
            translate([m6_detector_support_arm_min_x,
                       m6_detector_support_arm_min_y,
                       m6_detector_support_arm_z -
                           m6_detector_support_arm_t_z / 2])
                cube([m6_detector_support_arm_max_x -
                          m6_detector_support_arm_min_x,
                      m6_detector_support_arm_width_y,
                      m6_detector_support_arm_t_z]);
            translate([m6_detector_support_leg_x -
                           m6_detector_support_leg_t_x / 2,
                       m6_detector_support_arm_min_y,
                       m6_detector_support_leg_bottom_z])
                cube([m6_detector_support_leg_t_x,
                      m6_detector_support_arm_width_y,
                      m6_detector_support_leg_height_z]);
            for (y_side = [-1, 1]) {
                translate([0,
                           m6_detector_support_y +
                               y_side *
                                   (m6_detector_support_arm_width_y / 2 -
                                    m6_detector_support_gusset_t_y / 2),
                           0])
                    rotate([90, 0, 0])
                        linear_extrude(
                            height = m6_detector_support_gusset_t_y,
                            center = true)
                            polygon(points = [
                                [m6_detector_support_leg_x -
                                     m6_detector_support_leg_t_x / 2,
                                 m6_detector_support_arm_z -
                                     m6_detector_support_arm_t_z / 2],
                                [m6_detector_support_leg_x +
                                     m6_detector_support_gusset_inset_x,
                                 m6_detector_support_arm_z -
                                     m6_detector_support_arm_t_z / 2],
                                [m6_detector_support_leg_x -
                                     m6_detector_support_leg_t_x / 2,
                                 m6_detector_support_leg_bottom_z]
                            ]);
            }
        }
}

module m6_detector_ballhead_positive() {
    // Purchased 13 mm ball head in the user's required vertical posture:
    // housing/base/stud stack is z-oriented, while the M8 sensor-side stud
    // enters the integral aluminum T-tail along x. The selected default is
    // M8 external thread; the exact vendor transition remains a metal
    // hardware envelope, not a printed thread.
    color("silver") {
        translate([m6_detector_ballhead_center_x,
                   m6_detector_ballhead_center_y,
                   m6_detector_ballhead_center_z])
            sphere(d = m6_ballhead_ball_d, $fn = 32);
        m6_cylinder_z(
            m6_ballhead_housing_d,
            m6_ballhead_housing_length_x,
            m6_detector_ballhead_center_x,
            m6_detector_ballhead_center_y,
            m6_detector_ballhead_center_z);
        m6_cylinder_z(
            m6_ballhead_base_d,
            m6_ballhead_base_t,
            m6_detector_ballhead_center_x,
            m6_detector_ballhead_center_y,
            m6_detector_ballhead_base_center_z);
        m6_cylinder_x(
            m6_ballhead_sensor_stud_d,
            m6_ballhead_sensor_stud_length + 2,
            m6_detector_ballhead_sensor_stud_center_x,
            m6_detector_ballhead_center_y,
            m6_detector_ballhead_center_z);
        m6_cylinder_z(
            m6_ballhead_net_stud_d,
            m6_ballhead_net_stud_length,
            m6_detector_ballhead_center_x,
            m6_detector_ballhead_center_y,
            m6_detector_ballhead_net_stud_center_z);
    }
    color("dimgray")
        m6_cylinder_y(
            18,
            8,
            m6_detector_ballhead_center_x,
            m6_detector_ballhead_center_y -
                m6_ballhead_housing_d / 2 - 2,
            m6_detector_ballhead_center_z);
}

module m6_detector_support_hardware_positive() {
    color("gold") {
        // Sensor-side M8 external stud engages the female M8x1.25 blind tap
        // directly in the aluminum T-tail.  There is no PETG insert or rear
        // cover boss in this load path; the gold cylinder is only the
        // purchased metal stud envelope.
        m6_cylinder_x(
            m6_ballhead_sensor_stud_d - 0.4,
            m6_ballhead_sensor_stud_length,
            m6_detector_ballhead_sensor_stud_center_x,
            m6_detector_ballhead_center_y,
            m6_detector_ballhead_center_z);
        // Vertical M8 external stud into the 90° metal support shelf.
        m6_cylinder_z(
            m6_ballhead_net_stud_d - 0.4,
            m6_ballhead_net_stud_length,
            m6_detector_ballhead_center_x,
            m6_detector_ballhead_center_y,
            m6_detector_ballhead_net_stud_center_z);
        // Two visible M6 through bolts tie the vertical bracket to the
        // commercial/metal adapter plate; the exact clamp-side slot remains
        // a first-article measurement item.
        for (z_position = [m6_post_mount_hole_z - 6,
                           m6_post_mount_hole_z + 6]) {
            m6_cylinder_x(
                m6_detector_support_fastener_d - 0.6,
                m6_mount_plate_t + 14,
                m6_detector_support_leg_x,
                m6_detector_support_y,
                z_position);
        }
    }
}

module m6_detector_mount_positive() {
    m6_mount_adapter_positive();
    m6_post_mount_hardware_positive();
    m6_detector_support_positive();
    m6_detector_body_positive();
    m6_detector_sensor_array_positive();
    // The body and rotated L-device remain the optical datum; the completed
    // x-split protective covers are now visible in the assembly by default.
    if (m6_detector_show_shell) {
        m6_detector_shell_front_positive();
        m6_detector_shell_rear_positive();
        m6_detector_bottom_cover_positive();
    }
    m6_detector_ballhead_positive();
    m6_detector_support_hardware_positive();
}

module m6_detector_exploded_positive() {
    // Non-sectioned inspection view.  Each physical part stays whole and is
    // pulled away along its real assembly direction: sensors out through x+,
    // x- optical front cover, x+ cable rear cover, and bottom cover downward.
    // The metal support/ballhead/load path remains in place so
    // the exploded relationship to the net clamp is still readable.
    m6_mount_adapter_positive();
    m6_post_mount_hardware_positive();
    m6_detector_support_positive();
    m6_detector_ballhead_positive();
    m6_detector_support_hardware_positive();

    // Aluminum carrier stays at its installed datum.
    m6_detector_body_positive();

    // The ten purchased L sensors are withdrawn from the right-side receiver
    // entry.  On SIDE=-1 the outer mirror makes this the left-side withdrawal.
    translate([28, 0, 0])
        m6_detector_sensor_array_positive();

    // Covers are whole, opaque parts in this view; their separation is the
    // section substitute and no face is cut away.
    translate([-24, 0, 0])
        m6_detector_shell_front_positive(1);
    translate([24, 0, 0])
        m6_detector_shell_rear_positive(1);
    translate([0, 0, -18])
        m6_detector_bottom_cover_positive();
}

module m6_yaw_base_positive() {
    // 固定的下层水平转台，直接与网夹侧的固定适配板相交并承接 M8
    // 竖直枢轴。它不随偏航角转动。
    color("gainsboro")
        difference() {
            translate([m6_gimbal_pivot_x - m6_yaw_stage_radius,
                       -m6_yaw_stage_radius,
                       m6_yaw_stage_z])
                cube([2 * m6_yaw_stage_radius,
                      2 * m6_yaw_stage_radius,
                      m6_yaw_stage_t]);
            m6_cylinder_z(
                m6_pivot_d,
                m6_yaw_stage_t + 4,
                m6_gimbal_pivot_x,
                0,
                m6_yaw_stage_z + m6_yaw_stage_t / 2);
            // Blind M6×1.0 taps start at the fixed-adapter interface on the
            // +x side.  They turn the adapter/base intersection into a real
            // bolted load path.
            for (y_position = [-m6_yaw_base_mount_hole_y,
                               m6_yaw_base_mount_hole_y]) {
                m6_cylinder_x(
                    m6_yaw_base_mount_tap_d,
                    m6_yaw_base_mount_tap_depth,
                    m6_mount_plate_x - m6_yaw_base_mount_tap_depth / 2,
                    y_position,
                    m6_yaw_stage_z + m6_yaw_stage_t / 2);
            }
        }
}

module m6_yaw_reaction_block_positive() {
    // Fixed reaction ear for the yaw tangent screw.  The vertical portion is
    // outside the lower plate's y-min edge; the foot overlaps the lower plate
    // for a real load path.  The M4 pilot/tap is at the upper-plate mid-plane,
    // and the screw tip deliberately advances 0.5 mm past the edge to make
    // contact instead of merely ending flush with the reaction ear.
    block_x = m6_gimbal_pivot_x + m6_yaw_stage_radius -
              m6_yaw_adjuster_block_width_x / 2;
    block_y = -m6_yaw_stage_radius - m6_yaw_adjuster_block_depth_y;
    contact_z = m6_yaw_stage_z + m6_yaw_stage_t + m6_yaw_stage_t / 2;
    color("darkgray")
        difference() {
            union() {
                translate([block_x,
                           block_y,
                           m6_yaw_stage_z])
                    cube([m6_yaw_adjuster_block_width_x,
                          m6_yaw_adjuster_block_depth_y,
                          m6_yaw_adjuster_block_height_z]);
                translate([block_x,
                           block_y,
                           m6_yaw_stage_z])
                    cube([m6_yaw_adjuster_block_width_x,
                          m6_yaw_adjuster_block_depth_y +
                              m6_yaw_adjuster_foot_inset_y,
                          m6_yaw_stage_t]);
            }
            m6_cylinder_y(
                m6_yaw_adjuster_tap_d,
                m6_yaw_adjuster_block_depth_y + 4,
                m6_gimbal_pivot_x + m6_yaw_stage_radius,
                block_y + m6_yaw_adjuster_block_depth_y / 2,
                contact_z);
        }
}

module m6_yaw_base_with_reaction_positive() {
    union() {
        m6_yaw_base_positive();
        m6_yaw_reaction_block_positive();
    }
}

module m6_yaw_top_plate_positive() {
    // 随阵列转动的上层水平转台。两条 z 向弧槽提供 ±4° 粗调，中心
    // 枢轴只定位不承受全部抗扭；锁紧螺钉在弧槽两端夹住上下层。
    color("silver")
        difference() {
            translate([m6_gimbal_pivot_x - m6_yaw_stage_radius,
                       -m6_yaw_stage_radius,
                       m6_yaw_stage_z + m6_yaw_stage_t])
                cube([2 * m6_yaw_stage_radius,
                      2 * m6_yaw_stage_radius,
                      m6_yaw_stage_t]);
            m6_cylinder_z(
                m6_pivot_d,
                m6_yaw_stage_t + 4,
                m6_gimbal_pivot_x,
                0,
                m6_yaw_stage_z + 1.5 * m6_yaw_stage_t);
            for (center_angle = [-90, 90]) {
                m6_arc_slot_z(
                    m6_gimbal_pivot_x,
                    0,
                    m6_yaw_stage_z + 1.5 * m6_yaw_stage_t,
                    m6_yaw_slot_radius,
                    center_angle,
                    m6_yaw_range_deg);
            }
            // Vertical tapped holes for the carrier.  They sit away from
            // the central pivot and the radius-64 mm yaw arc slots.
            for (y_position = [-m5_yaw_carrier_mount_hole_y,
                               m5_yaw_carrier_mount_hole_y]) {
                m6_cylinder_z(
                    m5_yaw_carrier_mount_tap_d,
                    m5_yaw_carrier_mount_tap_depth,
                    m6_gimbal_pivot_x,
                    y_position,
                    m6_yaw_stage_z + 2 * m6_yaw_stage_t -
                        m5_yaw_carrier_mount_tap_depth / 2);
            }
        }
}

module m6_yaw_carrier_positive() {
    // Compatibility entry point for old preview callers.  The actual fixed
    // yaw carrier is now the explicit outer pitch yoke below; this foot
    // replaces the old vertical slab that intersected the roll plate.
    color("darkgray")
        difference() {
            translate([min(m6_yaw_plate_x, m6_pitch_frame_x - 2),
                       -m5_yaw_carrier_mount_hole_y - 8,
                       m6_yaw_carrier_bottom_z])
                cube([max(m6_yaw_plate_x + m6_yaw_plate_t,
                          m6_pitch_frame_x - 2 + m6_pitch_yoke_length_x) -
                          min(m6_yaw_plate_x, m6_pitch_frame_x - 2),
                      2 * (m5_yaw_carrier_mount_hole_y + 8),
                      m6_pitch_yoke_foot_t]);
            for (y_position = [-m5_yaw_carrier_mount_hole_y,
                               m5_yaw_carrier_mount_hole_y]) {
                m6_cylinder_z(
                    m5_yaw_carrier_mount_clearance_d,
                    m6_pitch_yoke_foot_t + 4,
                    m6_gimbal_pivot_x,
                    y_position,
                    m6_yaw_carrier_bottom_z + m6_pitch_yoke_foot_t / 2);
            }
        }
}

module m6_pitch_yoke_positive() {
    // Fixed outer fork: its cheeks carry the inner frame's y-axis pivot and
    // pitch lock slots.  The Ø110 roll plate is deliberately inside the
    // inner frame, not wedged between these two cheeks.
    yoke_cheek_center = m6_pitch_yoke_width_y / 2 -
                        m6_pitch_yoke_t / 2;
    color("darkgray")
        difference() {
            union() {
                for (cheek = [-1, 1]) {
                    translate([m6_pitch_frame_x - 2,
                               cheek * yoke_cheek_center -
                                   m6_pitch_yoke_t / 2,
                               m6_pitch_yoke_bottom_z])
                        cube([m6_pitch_yoke_length_x,
                              m6_pitch_yoke_t,
                              m6_pitch_yoke_top_z -
                                  m6_pitch_yoke_bottom_z]);
                }
                // The lower bridge is the legacy M5-to-yaw-top load path.
                // Keep it positive when the compact sensor bar moves the
                // pitch frame inboard of the yaw plate.
                translate([min(m6_yaw_plate_x, m6_pitch_frame_x - 2),
                           -m6_pitch_yoke_width_y / 2,
                           m6_pitch_yoke_bottom_z])
                    cube([max(m6_yaw_plate_x + m6_yaw_plate_t,
                              m6_pitch_frame_x - 2 + m6_pitch_yoke_length_x) -
                              min(m6_yaw_plate_x, m6_pitch_frame_x - 2),
                          m6_pitch_yoke_width_y,
                          m6_pitch_yoke_foot_t]);
            }
            for (cheek = [-1, 1]) {
                cheek_y = cheek * yoke_cheek_center;
                m6_cylinder_y(
                    m6_pivot_d,
                    m6_pitch_yoke_t + 4,
                    m6_pitch_pivot_x,
                    cheek_y,
                    m6_pitch_pivot_z);
                for (z_position = [m6_pitch_pivot_z - m6_pitch_lock_offset_z,
                                   m6_pitch_pivot_z + m6_pitch_lock_offset_z]) {
                    m6_slot_y_z(
                        m6_pitch_pivot_x,
                        cheek_y,
                        z_position,
                        m6_pitch_slot_length);
                }
            }
            for (y_position = [-m5_yaw_carrier_mount_hole_y,
                               m5_yaw_carrier_mount_hole_y]) {
                m6_cylinder_z(
                    m5_yaw_carrier_mount_clearance_d,
                    m6_pitch_yoke_foot_t + 4,
                    m6_gimbal_pivot_x,
                    y_position,
                    m6_pitch_yoke_bottom_z + m6_pitch_yoke_foot_t / 2);
            }
        }
}

module m6_pitch_frame_positive() {
    // Rotating inner pitch frame.  A rectangular ring surrounds the roll
    // disk, while the rear central spine carries the x-axis roll pivot and
    // the two M5 roll-lock taps.  Its side bosses are the only y-axis
    // connection to the fixed outer yoke.
    frame_x = m6_pitch_frame_x;
    frame_center_x = frame_x + m6_pitch_frame_t / 2;
    frame_outer_z = m6_array_center_z - m6_pitch_frame_outer_height_z / 2;
    frame_window_z = m6_array_center_z - m6_pitch_frame_window_height_z / 2;
    boss_y = m6_pitch_frame_outer_width_y / 2 + 5;
    color("slategray")
        difference() {
            union() {
                difference() {
                    translate([frame_x,
                               -m6_pitch_frame_outer_width_y / 2,
                               frame_outer_z])
                        cube([m6_pitch_frame_t,
                              m6_pitch_frame_outer_width_y,
                              m6_pitch_frame_outer_height_z]);
                    translate([frame_x - 1,
                               -m6_pitch_frame_window_width_y / 2,
                               frame_window_z])
                        cube([m6_pitch_frame_t + 2,
                              m6_pitch_frame_window_width_y,
                              m6_pitch_frame_window_height_z]);
                }
                // This spine is behind the sensor rail (x-positive), so it
                // does not enter the optical beam or cable exits.
                translate([frame_x,
                           -m6_pitch_frame_spine_width_y / 2,
                           frame_outer_z])
                    cube([m6_pitch_frame_t,
                          m6_pitch_frame_spine_width_y,
                          m6_pitch_frame_outer_height_z]);
                for (cheek = [-1, 1]) {
                    m6_cylinder_y(
                        m6_pitch_frame_hub_d,
                        20,
                        frame_center_x,
                        cheek * boss_y,
                        m6_pitch_pivot_z);
                }
                m6_cylinder_x(
                    m6_pitch_frame_hub_d,
                    14,
                    frame_center_x,
                    0,
                    m6_roll_pivot_z);
            }
            for (cheek = [-1, 1]) {
                m6_cylinder_y(
                    m6_pivot_d,
                    24,
                    frame_center_x,
                    cheek * boss_y,
                    m6_pitch_pivot_z);
                for (z_position = [m6_pitch_pivot_z - m6_pitch_lock_offset_z,
                                   m6_pitch_pivot_z + m6_pitch_lock_offset_z]) {
                    m6_cylinder_y(
                        m6_pitch_lock_tap_d,
                        20,
                        frame_center_x,
                        cheek * (m6_pitch_frame_outer_width_y / 2 - 5),
                        z_position);
                }
            }
            m6_cylinder_x(
                m6_roll_pivot_d,
                20,
                frame_center_x,
                0,
                m6_roll_pivot_z);
            for (z_position = [m6_roll_pivot_z - 16,
                               m6_roll_pivot_z + 16]) {
                m6_cylinder_x(
                    m6_roll_lock_tap_d,
                    m6_roll_lock_tap_depth + 4,
                    frame_center_x,
                    0,
                    z_position);
            }
        }
}

module m6_roll_pivot_hardware_positive() {
    // A long shoulder/washer stack bridges the roll plate, rail and the
    // 2 mm gap to the inner-frame spine.
    color("gold")
        m6_cylinder_x(
            m6_roll_pivot_d - 0.5,
            m6_roll_pivot_bolt_length,
            (m6_roll_pivot_x + m6_pitch_frame_x) / 2,
            0,
            m6_roll_pivot_z);
}

module m6_pitch_pivot_hardware_positive() {
    color("gold")
        for (cheek = [-1, 1]) {
            m6_cylinder_y(
                m6_pivot_d - 0.5,
                m6_pitch_yoke_t + 18,
                m6_pitch_pivot_x,
                cheek * (m6_pitch_yoke_width_y / 2 -
                          m6_pitch_yoke_t / 2),
                m6_pitch_pivot_z);
        }
}

module m6_roll_lock_hardware_positive() {
    color("gold")
        for (z_position = [m6_roll_pivot_z - 16,
                           m6_roll_pivot_z + 16]) {
            m6_cylinder_x(
                m6_stage_bolt_d - 0.5,
                m6_roll_pivot_bolt_length,
                (m6_roll_pivot_x + m6_pitch_frame_x) / 2,
                0,
                z_position);
        }
}

module m6_roll_plate_positive() {
    // 滚转：绕 x 轴的圆盘枢轴 + 上下两条切向锁紧槽。滚转盘与梳齿
    // 背骨用四枚 M4 连接；中心小枢轴穿过背骨并进入内框后侧中心脊。
    color("silver")
        difference() {
            translate([m6_roll_pivot_x, 0, m6_roll_pivot_z])
                rotate([0, 90, 0])
                    cylinder(d = m6_roll_plate_d,
                             h = m6_roll_plate_t,
                             center = true);
            m6_cylinder_x(
                m6_roll_pivot_d,
                m6_roll_plate_t + 4,
                m6_roll_pivot_x,
                0,
                m6_roll_pivot_z);
            for (z_position = [m6_roll_pivot_z - 16,
                               m6_roll_pivot_z + 16]) {
                m6_slot_x_y(
                    m6_roll_pivot_x,
                    0,
                    z_position,
                    m6_roll_slot_length);
            }
            // M4 clearance holes align with the four blind M4 taps in the
            // back of the comb rail.  They are the positive rail-to-gimbal
            // load path; the M6/roll slots below remain the adjustment clamp.
            for (hole_y = [-m6_rail_mount_hole_y, m6_rail_mount_hole_y]) {
                for (hole_z = [m6_roll_pivot_z - m6_rail_mount_z_offset,
                               m6_roll_pivot_z + m6_rail_mount_z_offset]) {
                    m6_cylinder_x(
                        m6_rail_mount_clearance_d,
                        m6_roll_plate_t + 4,
                        m6_roll_pivot_x,
                        hole_y,
                        hole_z);
                }
            }
        }
}

// The following entry points are deliberately local-coordinate machining
// previews. They reuse the same positive geometry as the assembly, but move
// each aluminum part to a small, machinist-friendly coordinate system:
// x-min/center-y/z-min for plates and frames, and the backbone x-min/center-y/
// bottom for the comb rail. They are not part of the PETG print manifest.
module m6_machining_detector_body_positive() {
    // Local quotation preview for the continuous 6061-T6 body. The ten
    // optical bores, rear M6 clearance bores and shallow anti-rotation
    // pockets remain in the preview; purchased sensors/nuts are excluded.
    translate([-m6_detector_body_min_x,
               -m6_detector_body_min_y,
               -m6_detector_body_bottom_z])
        m6_detector_body_positive();
}

module m6_machining_support_positive() {
    // Local quotation preview for the separate 90-degree metal support. Its
    // origin is the minimum x/y/z of the L bracket.
    translate([-m6_detector_support_arm_min_x,
               -m6_detector_support_arm_min_y,
               -m6_detector_support_leg_bottom_z])
        m6_detector_support_positive();
}

module m6_machining_rail_positive() {
    translate([-m6_sensor_rail_x, 0, -m6_array_bottom_z])
        m6_sensor_rail_positive();
}

module m6_machining_adapter_positive() {
    translate([-m6_mount_plate_x,
               0,
               -(m6_array_center_z - m6_mount_plate_height_z / 2)])
        m6_mount_adapter_positive();
}

module m6_machining_backplate_positive() {
    // Local quotation preview for the separate metal rear plate.  The
    // purchased ball head is intentionally absent: it is an off-the-shelf
    // component, not a printed or machined part in this project.
    translate([-m6_detector_backplate_x,
               0,
               -(m6_array_center_z - m6_detector_backplate_height_z / 2)])
        m6_detector_backplate_positive();
}

module m6_machining_yaw_base_positive() {
    translate([-(m6_gimbal_pivot_x - m6_yaw_stage_radius),
               0,
               -m6_yaw_stage_z])
        m6_yaw_base_with_reaction_positive();
}

module m6_machining_yaw_top_positive() {
    translate([-(m6_gimbal_pivot_x - m6_yaw_stage_radius),
               0,
               -(m6_yaw_stage_z + m6_yaw_stage_t)])
        m6_yaw_top_plate_positive();
}

module m6_machining_pitch_yoke_positive() {
    translate([-m6_yaw_plate_x,
               0,
               -m6_pitch_yoke_bottom_z])
        m6_pitch_yoke_positive();
}

module m6_machining_pitch_frame_positive() {
    frame_outer_z = m6_array_center_z - m6_pitch_frame_outer_height_z / 2;
    translate([-m6_pitch_frame_x, 0, -frame_outer_z])
        m6_pitch_frame_positive();
}

module m6_machining_roll_disc_positive() {
    translate([-(m6_roll_pivot_x - m6_roll_plate_t / 2),
               0,
               -(m6_roll_pivot_z - m6_roll_plate_d / 2)])
        m6_roll_plate_positive();
}

module m6_yaw_fine_adjuster_positive() {
    // Yaw tangent screw: along y at the +x outer tangent.  It is held by the
    // raised fixed reaction ear and its tip reaches 0.5 mm into the moving
    // upper-plate edge at the upper-plate mid-plane; the pivot/arc clamps
    // carry the working load after alignment.
    tip_y = -m6_yaw_stage_radius + m6_yaw_adjuster_tip_overtravel_y;
    contact_z = m6_yaw_stage_z + m6_yaw_stage_t + m6_yaw_stage_t / 2;
    color("gold")
        m6_cylinder_y(
            m6_fine_adjuster_d,
            m6_fine_adjuster_length,
            m6_gimbal_pivot_x + m6_yaw_stage_radius,
            tip_y - m6_fine_adjuster_length / 2,
            contact_z);
}

module m6_pitch_fine_adjuster_positive() {
    // A crossbar between the fixed yoke cheeks creates a real reaction point.
    // The x-directed M4 screw presses the inner-frame spine at a z offset
    // from the y pivot, producing pitch torque without being a load path.
    bridge_x = m6_pitch_frame_x + m6_pitch_yoke_length_x - 8;
    pitch_contact_z = m6_pitch_pivot_z + m6_pitch_adjuster_offset_z;
    color("darkgray")
        translate([bridge_x,
                   -m6_pitch_yoke_width_y / 2,
                   pitch_contact_z - m6_pitch_adjuster_bridge_t / 2])
            cube([8,
                  m6_pitch_yoke_width_y,
                  m6_pitch_adjuster_bridge_t]);
    color("gold")
        m6_cylinder_x(
            m6_fine_adjuster_d,
            m6_fine_adjuster_length,
            m6_pitch_frame_x + m6_pitch_frame_t +
                m6_fine_adjuster_length / 2,
            0,
            pitch_contact_z);
}

module m6_roll_fine_adjuster_positive() {
    // The inner-frame arm stays with the pitch frame.  Its y-directed M4
    // screw stops at the calculated rim tangent of the Ø110 roll disk, so it
    // can trim roll without crossing the optical disc face.
    arm_x = m6_roll_pivot_x - m6_roll_plate_t / 2;
    arm_width_x = m6_pitch_frame_x - arm_x;
    roll_contact_z = m6_roll_pivot_z + m6_roll_adjuster_offset_z;
    arm_max_y = m6_roll_adjuster_contact_y - m6_roll_adjuster_clearance_y;
    color("darkgray")
        translate([arm_x,
                   arm_max_y - m6_roll_adjuster_arm_depth_y,
                   roll_contact_z - m6_roll_adjuster_arm_t / 2])
            cube([arm_width_x,
                  m6_roll_adjuster_arm_depth_y,
                  m6_roll_adjuster_arm_t]);
    color("gold")
        m6_cylinder_y(
            m6_fine_adjuster_d,
            m6_roll_adjuster_length,
            m6_roll_pivot_x,
            m6_roll_adjuster_contact_y - m6_roll_adjuster_length / 2,
            roll_contact_z);
}

module m6_sensor_gimbal_adjusted_positive() {
    // The pitch frame and its roll support rotate about the y-axis first;
    // only the sensor/roll payload then rotates about x.  This nested
    // transform mirrors the actual two independent hinge axes.
    translate([m6_pitch_pivot_x, 0, m6_pitch_pivot_z])
        rotate([0, m6_pitch_angle, 0])
            translate([-m6_pitch_pivot_x, 0, -m6_pitch_pivot_z]) {
                m6_pitch_frame_positive();
                m6_roll_pivot_hardware_positive();
                m6_roll_lock_hardware_positive();
                m6_roll_fine_adjuster_positive();
                translate([m6_roll_pivot_x, 0, m6_roll_pivot_z])
                    rotate([m6_roll_angle, 0, 0])
                        translate([-m6_roll_pivot_x,
                                   0,
                                   -m6_roll_pivot_z]) {
                            m6_roll_plate_positive();
                            m6_sensor_array_positive();
                        }
            }
}

module m6_gimbal_positive() {
    // Compatibility entry point.  The current production assembly is the
    // long rear-inserted detector body with two protective covers, a vertical
    // purchased ball head and a metal 90° support.  The historical custom
    // three-axis gimbal remains available only through its legacy modules.
    m6_detector_mount_positive();
}

module m6_gimbal(side = 1) {
    sided(side) m6_gimbal_positive();
}

module m6_beam_preview() {
    // 名义零角度时，十条相对发射/接收器光轴都穿过球台边缘；
    // 当前主线为单竖直排，故所有光轴使用主体 y=0 中心线。
    color("red", 0.25)
        for (index = [0:m6_sensor_count - 1]) {
            y0 = m6_detector_sensor_head_center_y;
            translate([-m6_sensor_axis_x,
                       y0 - 0.35,
                       m6_sensor_z(index) - 0.35])
                cube([2 * m6_sensor_axis_x, 0.7, 0.7]);
        }
}

module m6_optical_arrow_x(x_start, x_end, y_center, z_center) {
    // The large cone base is at x_start and the tip is at x_end.  Every
    // rendered arrow therefore points in the physical +x beam direction.
    head_length = 8;
    shaft_d = 1.2;
    head_d = 5;
    shaft_end = x_end - head_length;
    color("red", 0.95) {
        m6_cylinder_x(
            shaft_d,
            max(0.2, shaft_end - x_start),
            (x_start + shaft_end) / 2,
            y_center,
            z_center);
        translate([x_end - head_length / 2, y_center, z_center])
            rotate([0, 90, 0])
                cylinder(
                    d1 = head_d,
                    d2 = 0.2,
                    h = head_length,
                    center = true,
                    $fn = 24);
    }
}

module m6_optical_direction_preview(side = 1) {
    // Global optical direction is always left -> right (+x).  On the right
    // receiver the arrow ends at the x- optical face; on the mirrored left
    // emitter it starts at the x+ optical face and leaves toward +x.
    for (index = [0:m6_sensor_count - 1]) {
        if (side >= 0) {
            m6_optical_arrow_x(
                m6_detector_fit_thread_tip_x - 35,
                m6_detector_fit_thread_tip_x,
                m6_detector_sensor_head_center_y,
                m6_sensor_z(index));
        } else {
            m6_optical_arrow_x(
                -m6_detector_fit_thread_tip_x,
                -m6_detector_fit_thread_tip_x + 35,
                m6_detector_sensor_head_center_y,
                m6_sensor_z(index));
        }
    }
}

module m6_optical_full_direction_preview() {
    // One arrow per channel makes the left-to-right beam direction explicit
    // when both detector assemblies are shown together.
    for (index = [0:m6_sensor_count - 1]) {
        m6_optical_arrow_x(
            -m6_detector_fit_thread_tip_x,
            m6_detector_fit_thread_tip_x,
            m6_detector_sensor_head_center_y,
            m6_sensor_z(index));
    }
}

module m6_optical_exploded_direction_preview(side = 1) {
    // The sensors in the exploded view are pulled 28 mm away from the body.
    // Extend the same +x beam arrow to the extracted optical face so the
    // assembly direction and the optical direction remain visible together.
    for (index = [0:m6_sensor_count - 1]) {
        if (side >= 0) {
            m6_optical_arrow_x(
                m6_detector_fit_thread_tip_x + 28 - 35,
                m6_detector_fit_thread_tip_x + 28,
                m6_detector_sensor_head_center_y,
                m6_sensor_z(index));
        } else {
            m6_optical_arrow_x(
                -(m6_detector_fit_thread_tip_x + 28),
                -(m6_detector_fit_thread_tip_x + 28) + 35,
                m6_detector_sensor_head_center_y,
                m6_sensor_z(index));
        }
    }
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

// STG-120ML 不是旧版的十个独立红外模块。它的 120 mm 竖直光纤头需要
// 一条连续的包络托架；商品标称最大检测距离 1000 mm，因此完整 1525 mm
// 球台宽度采用左右两段，各段从外侧立柱跨到中央背靠背支撑桥。
module stg120_outer_carrier_positive() {
    frame_z = stg120_head_bottom_z - stg120_carrier_wall;
    cavity_x = stg120_head_thickness + 2 * stg120_head_clearance +
               stg120_carrier_wall + 1;
    color("teal")
        difference() {
            translate([stg120_outer_frame_min_x,
                       -stg120_outer_frame_y / 2,
                       frame_z])
                cube([stg120_outer_frame_width,
                      stg120_outer_frame_y,
                      stg120_outer_frame_z]);
            // 光纤头从内侧滑入，前方光学窗口保持完全敞开；后方实体臂
            // 连接到原有立柱内侧，不依赖商品头部的 M3 螺纹孔位。
            translate([stg120_outer_frame_min_x - 1,
                       -stg120_head_width / 2 - stg120_head_clearance,
                       stg120_head_bottom_z - stg120_head_clearance])
                cube([cavity_x,
                      stg120_head_width + 2 * stg120_head_clearance,
                      stg120_head_length + 2 * stg120_head_clearance]);
        }
    // 3.87 mm 光束档位刻线先做成可见机械参考，不把它宣称为传感器输出。
    color("white")
        for (i = [0:stg120_beam_count - 1]) {
            translate([stg120_outer_frame_min_x,
                       -stg120_outer_frame_y / 2 - 0.3,
                       beam_z(i * stg120_beam_pitch) - 0.35])
                cube([stg120_outer_frame_width, 1, 0.7]);
        }
}

module stg120_outer_carrier(side = 1) {
    sided(side) stg120_outer_carrier_positive();
}

module stg120_center_bridge_positive() {
    frame_z = stg120_head_bottom_z - stg120_carrier_wall;
    cavity_width = stg120_head_thickness + 2 * stg120_head_clearance;
    color("teal")
        difference() {
            translate([-stg120_center_frame_width / 2,
                       -stg120_center_frame_y / 2,
                       frame_z])
                cube([stg120_center_frame_width,
                      stg120_center_frame_y,
                      stg120_center_frame_z]);
            // 中央桥两侧各收纳一只头部，两个窗口相背打开，形成左右
            // 两个不超过 1000 mm 的光学分段；中心不留遮光隔墙。
            translate([-stg120_head_thickness - stg120_head_clearance,
                       -stg120_head_width / 2 - stg120_head_clearance,
                       stg120_head_bottom_z - stg120_head_clearance])
                cube([cavity_width,
                      stg120_head_width + 2 * stg120_head_clearance,
                      stg120_head_length + 2 * stg120_head_clearance]);
            translate([-stg120_head_clearance,
                       -stg120_head_width / 2 - stg120_head_clearance,
                       stg120_head_bottom_z - stg120_head_clearance])
                cube([cavity_width,
                      stg120_head_width + 2 * stg120_head_clearance,
                      stg120_head_length + 2 * stg120_head_clearance]);
        }
    // 下方桥脚跨住网顶承载条；它是三点支撑的机械首样，仍需实物检查
    // 是否遮挡球路或网布张力路径。
    color("teal")
        translate([-stg120_center_frame_width / 2,
                   -(net_rail_depth + 6) / 2,
                   net_height - net_rail_height - 2])
            cube([stg120_center_frame_width, net_rail_depth + 6, 6]);
}

module stg120_center_bridge() {
    stg120_center_bridge_positive();
}

module stg120_head_body_positive(x_center, face_direction = 1) {
    face_x = x_center + face_direction * stg120_head_thickness / 2;
    color("silver")
        translate([x_center - stg120_head_thickness / 2,
                   -stg120_head_width / 2,
                   stg120_head_bottom_z])
            cube([stg120_head_thickness,
                  stg120_head_width,
                  stg120_head_length]);
    color("black")
        translate([face_x - 0.15,
                   -stg120_head_width / 2 + 1,
                   net_height])
            cube([0.3, stg120_head_width - 2, stg120_active_length]);
}

module stg120_pair_preview_positive() {
    // 右半段：外侧头的出光面朝中心，中央头的出光面朝右。
    stg120_head_body_positive(
        stg120_outer_face_x + stg120_head_thickness / 2, -1);
    stg120_head_body_positive(-stg120_head_thickness / 2, 1);
    color("red", 0.22)
        for (i = [0:stg120_beam_count - 1]) {
            translate([0, -0.35, beam_z(i * stg120_beam_pitch) - 0.3])
                cube([stg120_outer_face_x, 0.7, 0.6]);
        }
}

module stg120_preview() {
    stg120_pair_preview_positive();
    mirror([1, 0, 0]) stg120_pair_preview_positive();
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
    // 三段带 20 mm 搭接，打印长度约 623.33 mm；实际装配时用下方拼接片/螺钉
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
    gauge_width = 32;
    gauge_depth = 18;
    gauge_height = stg120_active_length + 20;
    color("darkorange") {
        cube([gauge_width, gauge_depth, gauge_height]);
        for (i = [0:stg120_beam_count - 1]) {
            h = i * stg120_beam_pitch;
            translate([gauge_width - 8, -2, h - 1])
                cube([12, gauge_depth + 4, 2]);
        }
    }
    color("black")
        for (i = [0:stg120_beam_count - 1]) {
            h = i * stg120_beam_pitch;
            translate([gauge_width + 6, gauge_depth / 2, h + 1])
                linear_extrude(height = 0.6)
                    text(str("+", h), size = 4, halign = "left", valign = "center");
        }
}

module stg120_reference_line() {
    color("limegreen")
        translate([-net_span / 2, -1.1,
                   beam_z(stg120_reference_height) - reference_line_d / 2])
            cube([net_span, reference_line_d, reference_line_d]);
}

module stand(side = 1) {
    sided(side) {
        post_positive();
        table_clamp_positive();
        net_rail_saddle_positive();
        m6_gimbal_positive();
    }
}

module parameter_probe() {
    echo(str("NETSTAND_PARAM table_width=", table_width));
    echo(str("NETSTAND_PARAM net_post_outboard_extension=", net_post_outboard_extension));
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
    echo(str("NETSTAND_PARAM clamp_horizontal_part_outboard_limit=",
             clamp_horizontal_part_outboard_limit));
    echo(str("NETSTAND_PARAM clamp_outboard_extension_min=", clamp_outboard_extension_min));
    echo(str("NETSTAND_PARAM clamp_outboard_extension_actual=", clamp_outboard_extension_actual));
    echo(str("NETSTAND_PARAM clamp_gusset_t_y=", clamp_gusset_t_y));
    echo(str("NETSTAND_PARAM clamp_gusset_start_inset=", clamp_gusset_start_inset));
    echo(str("NETSTAND_PARAM clamp_gusset_start_x=", clamp_gusset_start_x));
    echo(str("NETSTAND_PARAM clamp_gusset_end_x=", clamp_gusset_end_x));
    echo(str("NETSTAND_PARAM clamp_gusset_top_z=", clamp_gusset_top_z));
    echo(str("NETSTAND_PARAM clamp_gusset_bottom_z=", clamp_gusset_bottom_z));
    echo(str("NETSTAND_PARAM clamp_pad_outer_x=", clamp_pad_outer_x));
    echo(str("NETSTAND_PARAM clamp_outer_wall_x=", clamp_outer_wall_x));
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
    echo(str("NETSTAND_PARAM clamp_knob_nut_gap=", clamp_knob_nut_gap));
    echo(str("NETSTAND_PARAM clamp_knob_nut_stack_depth=", clamp_knob_nut_stack_depth));
    echo(str("NETSTAND_PARAM clamp_knob_nut_pocket_depth=", clamp_knob_nut_pocket_depth));
    echo(str("NETSTAND_PARAM clamp_body_nut_z=", clamp_body_nut_z));
    echo(str("NETSTAND_PARAM clamp_knob_h=", clamp_knob_h));
    echo(str("NETSTAND_PARAM clamp_knob_top_z=", clamp_knob_top_z));
    echo(str("NETSTAND_PARAM clamp_knob_bottom_z=", clamp_knob_bottom_z));
    echo(str("NETSTAND_PARAM clamp_knob_nut_z=", clamp_knob_nut_z));
    echo(str("NETSTAND_PARAM clamp_knob_drive_nut_z=", clamp_knob_drive_nut_z));
    echo(str("NETSTAND_PARAM clamp_knob_lock_nut_z=", clamp_knob_lock_nut_z));
    echo(str("NETSTAND_PARAM clamp_knob_nut_bottom_z=", clamp_knob_nut_bottom_z));
    echo(str("NETSTAND_PARAM clamp_knob_nut_top_z=", clamp_knob_nut_top_z));
    echo(str("NETSTAND_PARAM clamp_lower_arm_bottom_z=", clamp_lower_arm_bottom_z));
    echo(str("NETSTAND_PARAM clamp_lower_arm_top_z=", clamp_lower_arm_top_z));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_top_z=", clamp_pressure_pad_top_z));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_bottom_z=", clamp_pressure_pad_bottom_z));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_x=", clamp_pressure_pad_x));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_width=", clamp_pressure_pad_width));
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
    echo(str("NETSTAND_PARAM m6_sensor_count=", m6_sensor_count));
    echo(str("NETSTAND_PARAM m6_sensor_center_pitch=", m6_sensor_center_pitch));
    echo(str("NETSTAND_PARAM m6_sensor_first_height=", m6_sensor_first_height));
    echo(str("NETSTAND_PARAM m6_sensor_last_height=", m6_sensor_last_height()));
    echo(str("NETSTAND_PARAM m6_sensor_thread_d=", m6_sensor_thread_d));
    echo(str("NETSTAND_PARAM m6_sensor_thread_pitch=", m6_sensor_thread_pitch));
    echo(str("NETSTAND_PARAM m6_sensor_tap_visual_d=", m6_sensor_tap_visual_d));
    echo(str("NETSTAND_PARAM m6_sensor_head_length_x=", m6_sensor_head_length_x));
    echo(str("NETSTAND_PARAM m6_sensor_head_width_y=", m6_sensor_head_width_y));
    echo(str("NETSTAND_PARAM m6_sensor_head_height_z=", m6_sensor_head_height_z));
    echo(str("NETSTAND_PARAM m6_sensor_head_hex_af=", m6_sensor_head_hex_af));
    echo(str("NETSTAND_PARAM m6_sensor_optical_bore_d=", m6_sensor_optical_bore_d));
    echo(str("NETSTAND_PARAM m6_sensor_body_d=", m6_sensor_body_d));
    echo(str("NETSTAND_PARAM m6_sensor_body_length=", m6_sensor_body_length));
    echo(str("NETSTAND_PARAM m6_sensor_mount_x_offset=", m6_sensor_mount_x_offset));
    echo(str("NETSTAND_PARAM m6_sensor_mount_stem_length=", m6_sensor_mount_stem_length));
    echo(str("NETSTAND_PARAM m6_sensor_cable_guard_length=", m6_sensor_cable_guard_length));
    echo(str("NETSTAND_PARAM m6_sensor_cable_preview_length=", m6_sensor_cable_preview_length));
    echo(str("NETSTAND_PARAM m6_sensor_cable_d=", m6_sensor_cable_d));
    echo(str("NETSTAND_PARAM m6_sensor_thread_start_x=", m6_sensor_thread_start_x));
    echo(str("NETSTAND_PARAM m6_sensor_thread_end_x=", m6_sensor_thread_end_x));
    echo(str("NETSTAND_PARAM m6_sensor_optical_aperture_x=", m6_sensor_optical_aperture_x));
    echo(str("NETSTAND_PARAM m6_sensor_overall_end_x=", m6_sensor_overall_end_x));
    echo(str("NETSTAND_PARAM m6_sensor_head_center_x=", m6_sensor_head_center_x));
    echo(str("NETSTAND_PARAM m6_sensor_cable_exit_x=", m6_sensor_cable_exit_x));
    echo(str("NETSTAND_PARAM m6_sensor_lock_nut_h=", m6_sensor_lock_nut_h));
    echo(str("NETSTAND_PARAM m6_sensor_mount_plane_offset_z=", m6_sensor_mount_plane_offset_z));
    echo(str("NETSTAND_PARAM m6_sensor_lock_nut_af=", m6_sensor_lock_nut_af));
    echo(str("NETSTAND_PARAM m6_sensor_guard_outer_d=", m6_sensor_guard_outer_d));
    echo(str("NETSTAND_PARAM m6_sensor_guard_h=", m6_sensor_guard_h));
    echo(str("NETSTAND_PARAM m6_sensor_test_coupon_backbone_h=", m6_sensor_test_coupon_backbone_h));
    echo(str("NETSTAND_PARAM m6_sensor_test_coupon_clearance_d=", m6_sensor_test_coupon_clearance_d));
    echo(str("NETSTAND_PARAM m6_sensor_test_coupon_guard_overlap=", m6_sensor_test_coupon_guard_overlap));
    echo(str("NETSTAND_PARAM m6_sensor_nut_pocket_clearance=", m6_sensor_nut_pocket_clearance));
    echo(str("NETSTAND_PARAM m6_sensor_lane_offset_y=", m6_sensor_lane_offset_y));
    echo(str("NETSTAND_PARAM m6_adjacent_channel_center_distance_yz=", m6_adjacent_channel_center_distance_yz));
    echo(str("NETSTAND_PARAM m6_adjacent_guard_gap_y=", m6_adjacent_guard_gap_y));
    echo(str("NETSTAND_PARAM m6_adjacent_guard_gap_z=", m6_adjacent_guard_gap_z));
    echo(str("NETSTAND_PARAM m6_rail_t=", m6_rail_t));
    echo(str("NETSTAND_PARAM m6_sensor_body_clearance_d=", m6_sensor_body_clearance_d));
    echo(str("NETSTAND_PARAM m6_rail_width_y=", m6_rail_width_y));
    echo(str("NETSTAND_PARAM m6_rail_tab_t=", m6_rail_tab_t));
    echo(str("NETSTAND_PARAM m6_rail_tab_width_y=", m6_rail_tab_width_y));
    echo(str("NETSTAND_PARAM m6_rail_mount_clearance_d=", m6_rail_mount_clearance_d));
    echo(str("NETSTAND_PARAM m6_rail_mount_tap_d=", m6_rail_mount_tap_d));
    echo(str("NETSTAND_PARAM m6_rail_mount_tap_depth=", m6_rail_mount_tap_depth));
    echo(str("NETSTAND_PARAM m6_rail_mount_hole_y=", m6_rail_mount_hole_y));
    echo(str("NETSTAND_PARAM m6_rail_mount_z_offset=", m6_rail_mount_z_offset));
    echo(str("NETSTAND_PARAM m6_rail_mount_bolt_length=", m6_rail_mount_bolt_length));
    echo(str("NETSTAND_PARAM m6_detector_backplate_t=", m6_detector_backplate_t));
    echo(str("NETSTAND_PARAM m6_detector_backplate_width_y=", m6_detector_backplate_width_y));
    echo(str("NETSTAND_PARAM m6_detector_backplate_height_z=", m6_detector_backplate_height_z));
    echo(str("NETSTAND_PARAM m6_detector_backplate_lock_hole_y=", m6_detector_backplate_lock_hole_y));
    echo(str("NETSTAND_PARAM m6_detector_backplate_mount_clearance_d=", m6_detector_backplate_mount_clearance_d));
    echo(str("NETSTAND_PARAM m6_detector_backplate_anti_rotation_d=", m6_detector_backplate_anti_rotation_d));
    echo(str("NETSTAND_PARAM m6_ballhead_ball_d=", m6_ballhead_ball_d));
    echo(str("NETSTAND_PARAM m6_ballhead_housing_d=", m6_ballhead_housing_d));
    echo(str("NETSTAND_PARAM m6_ballhead_housing_length_x=", m6_ballhead_housing_length_x));
    echo(str("NETSTAND_PARAM m6_ballhead_base_d=", m6_ballhead_base_d));
    echo(str("NETSTAND_PARAM m6_ballhead_base_t=", m6_ballhead_base_t));
    echo(str("NETSTAND_PARAM m6_ballhead_sensor_stud_d=", m6_ballhead_sensor_stud_d));
    echo(str("NETSTAND_PARAM m6_ballhead_sensor_stud_length=", m6_ballhead_sensor_stud_length));
    echo(str("NETSTAND_PARAM m6_ballhead_net_stud_d=", m6_ballhead_net_stud_d));
    echo(str("NETSTAND_PARAM m6_ballhead_net_stud_length=", m6_ballhead_net_stud_length));
    echo(str("NETSTAND_PARAM m6_ballhead_tilt_range_deg=", m6_ballhead_tilt_range_deg));
    echo(str("NETSTAND_PARAM m6_ballhead_rotation_range_deg=", m6_ballhead_rotation_range_deg));
    echo(str("NETSTAND_PARAM m6_ballhead_mount_clearance_d=", m6_ballhead_mount_clearance_d));
    echo(str("NETSTAND_PARAM m6_sensor_roll_deg=", m6_sensor_roll_deg));
    echo(str("NETSTAND_PARAM m6_detector_body_depth_y=", m6_detector_body_depth_y));
    echo(str("NETSTAND_PARAM m6_detector_body_center_y=", m6_detector_body_center_y));
    echo(str("NETSTAND_PARAM m6_detector_body_length_x=", m6_detector_body_length_x));
    echo(str("NETSTAND_PARAM m6_detector_body_margin_z=", m6_detector_body_margin_z));
    echo(str("NETSTAND_PARAM m6_detector_body_front_margin_x=", m6_detector_body_front_margin_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_head_length_x=", m6_detector_fit_head_length_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_head_width_y=", m6_detector_fit_head_width_y));
    echo(str("NETSTAND_PARAM m6_detector_fit_head_height_z=", m6_detector_fit_head_height_z));
    echo(str("NETSTAND_PARAM m6_detector_fit_capture_depth_x=", m6_detector_fit_capture_depth_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_head_clearance_y=", m6_detector_fit_head_clearance_y));
    echo(str("NETSTAND_PARAM m6_detector_fit_head_clearance_z=", m6_detector_fit_head_clearance_z));
    echo(str("NETSTAND_PARAM m6_detector_fit_thread_length_x=", m6_detector_fit_thread_length_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_thread_clearance_d=", m6_detector_fit_thread_clearance_d));
    echo(str("NETSTAND_PARAM m6_detector_fit_thread_tip_allowance_x=", m6_detector_fit_thread_tip_allowance_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_head_inner_x=", m6_detector_fit_head_inner_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_head_center_x=", m6_detector_fit_head_center_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_thread_tip_x=", m6_detector_fit_thread_tip_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_thread_visible_length_x=", m6_detector_fit_thread_visible_length_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_body_depth_limit_x=", m6_detector_fit_body_depth_limit_x));
    echo(str("NETSTAND_PARAM m6_detector_fit_nut_center_x=", m6_detector_fit_nut_center_x));
    echo(str("NETSTAND_PARAM m6_detector_sensor_install_offset_x=", m6_detector_sensor_install_offset_x));
    echo(str("NETSTAND_PARAM m6_detector_sensor_nut_center_x=", m6_detector_sensor_nut_center_x));
    echo(str("NETSTAND_PARAM m6_detector_thread_visible_length=", m6_detector_thread_visible_length));
    echo(str("NETSTAND_PARAM m6_detector_shell_wall=", m6_detector_shell_wall));
    echo(str("NETSTAND_PARAM m6_detector_shell_clearance=", m6_detector_shell_clearance));
    echo(str("NETSTAND_PARAM m6_detector_shell_bottom_lip_z=", m6_detector_shell_bottom_lip_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_top_lip_z=", m6_detector_shell_top_lip_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_split_overlap_x=", m6_detector_shell_split_overlap_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_corner_radius=", m6_detector_shell_corner_radius));
    echo(str("NETSTAND_PARAM m6_detector_front_cap_length_x=", m6_detector_front_cap_length_x));
    echo(str("NETSTAND_PARAM m6_detector_front_cap_reduction=", m6_detector_front_cap_reduction));
    echo(str("NETSTAND_PARAM m6_detector_body_groove_width_x=", m6_detector_body_groove_width_x));
    echo(str("NETSTAND_PARAM m6_detector_body_groove_depth_y=", m6_detector_body_groove_depth_y));
    echo(str("NETSTAND_PARAM m6_detector_body_groove_margin_z=", m6_detector_body_groove_margin_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_tongue_depth_y=", m6_detector_shell_tongue_depth_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_tongue_clearance=", m6_detector_shell_tongue_clearance));
    echo(str("NETSTAND_PARAM m6_detector_optical_bore_d=", m6_detector_optical_bore_d));
    echo(str("NETSTAND_PARAM m6_detector_thread_clearance_d=", m6_detector_thread_clearance_d));
    echo(str("NETSTAND_PARAM m6_detector_hex_pocket_af=", m6_detector_hex_pocket_af));
    echo(str("NETSTAND_PARAM m6_detector_hex_pocket_depth_x=", m6_detector_hex_pocket_depth_x));
    echo(str("NETSTAND_PARAM m6_detector_hex_pocket_depth_y=", m6_detector_hex_pocket_depth_y));
    echo(str("NETSTAND_PARAM m6_detector_hex_pocket_floor=", m6_detector_hex_pocket_floor));
    echo(str("NETSTAND_PARAM m6_detector_shell_screw_pilot_d=", m6_detector_shell_screw_pilot_d));
    echo(str("NETSTAND_PARAM m6_detector_shell_screw_head_d=", m6_detector_shell_screw_head_d));
    echo(str("NETSTAND_PARAM m6_detector_shell_screw_head_depth=", m6_detector_shell_screw_head_depth));
    echo(str("NETSTAND_PARAM m6_detector_shell_screw_margin_z=", m6_detector_shell_screw_margin_z));
    echo(str("NETSTAND_PARAM m6_detector_bottom_cover_t=", m6_detector_bottom_cover_t));
    echo(str("NETSTAND_PARAM m6_bottom_cover_screw_depth=", m6_bottom_cover_screw_depth));
    echo(str("NETSTAND_PARAM m6_detector_bottom_cover_screw_d=", m6_detector_bottom_cover_screw_d));
    echo(str("NETSTAND_PARAM m6_detector_bottom_cover_screw_head_d=", m6_detector_bottom_cover_screw_head_d));
    echo(str("NETSTAND_PARAM m6_detector_bottom_cover_screw_head_depth=", m6_detector_bottom_cover_screw_head_depth));
    echo(str("NETSTAND_PARAM m6_detector_bottom_cover_screw_inset_x=", m6_detector_bottom_cover_screw_inset_x));
    echo(str("NETSTAND_PARAM m6_detector_cable_exit_d=", m6_detector_cable_exit_d));
    echo(str("NETSTAND_PARAM m6_detector_cable_exit_sleeve_clearance=", m6_detector_cable_exit_sleeve_clearance));
    echo(str("NETSTAND_PARAM m6_detector_cable_exit_x=", m6_detector_cable_exit_x));
    echo(str("NETSTAND_PARAM m6_detector_detector_thread_axis_x=",
             m6_detector_detector_thread_axis_x));
    echo(str("NETSTAND_PARAM m6_detector_sensor_thread_center_y=", m6_detector_sensor_thread_center_y));
    echo(str("NETSTAND_PARAM m6_detector_sensor_head_center_y=", m6_detector_sensor_head_center_y));
    echo(str("NETSTAND_PARAM m6_detector_support_boss_width_x=", m6_detector_support_boss_width_x));
    echo(str("NETSTAND_PARAM m6_detector_support_boss_depth_y=", m6_detector_support_boss_depth_y));
    echo(str("NETSTAND_PARAM m6_detector_support_boss_height_z=", m6_detector_support_boss_height_z));
    echo(str("NETSTAND_PARAM m6_detector_support_boss_x_fraction=", m6_detector_support_boss_x_fraction));
    echo(str("NETSTAND_PARAM m6_detector_support_thread_nominal_d=", m6_detector_support_thread_nominal_d));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_extension_x=", m6_detector_support_tail_extension_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_head_depth_y=", m6_detector_support_tail_head_depth_y));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_overlap_y=", m6_detector_support_tail_overlap_y));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_height_z=", m6_detector_support_tail_height_z));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_thread_pitch=", m6_detector_support_tail_thread_pitch));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_thread_depth_x=", m6_detector_support_tail_thread_depth_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_tap_drill_d=", m6_detector_support_tail_tap_drill_d));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_thread_mouth_d=", m6_detector_support_tail_thread_mouth_d));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_thread_mouth_depth_x=", m6_detector_support_tail_thread_mouth_depth_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tap_d=", m6_detector_support_tap_d));
    echo(str("NETSTAND_PARAM m6_detector_support_tap_depth_x=", m6_detector_support_tap_depth_x));
    echo(str("NETSTAND_PARAM m6_detector_support_metal_insert_d=", m6_detector_support_metal_insert_d));
    echo(str("NETSTAND_PARAM m6_detector_support_metal_insert_length_x=", m6_detector_support_metal_insert_length_x));
    echo(str("NETSTAND_PARAM m6_detector_support_arm_t_z=", m6_detector_support_arm_t_z));
    echo(str("NETSTAND_PARAM m6_detector_support_arm_width_y=", m6_detector_support_arm_width_y));
    echo(str("NETSTAND_PARAM m6_detector_support_leg_t_x=", m6_detector_support_leg_t_x));
    echo(str("NETSTAND_PARAM m6_detector_support_leg_bottom_drop_z=", m6_detector_support_leg_bottom_drop_z));
    echo(str("NETSTAND_PARAM m6_detector_support_gusset_t_y=", m6_detector_support_gusset_t_y));
    echo(str("NETSTAND_PARAM m6_detector_support_gusset_inset_x=", m6_detector_support_gusset_inset_x));
    echo(str("NETSTAND_PARAM m6_detector_support_fastener_d=", m6_detector_support_fastener_d));
    echo(str("NETSTAND_PARAM m6_detector_detector_ballhead_gap_x=", m6_detector_detector_ballhead_gap_x));
    echo(str("NETSTAND_PARAM m6_detector_sensor_head_y_offset=", m6_detector_sensor_head_y_offset));
    echo(str("NETSTAND_PARAM m6_detector_body_min_x=", m6_detector_body_min_x));
    echo(str("NETSTAND_PARAM m6_detector_body_max_x=", m6_detector_body_max_x));
    echo(str("NETSTAND_PARAM m6_detector_body_min_y=", m6_detector_body_min_y));
    echo(str("NETSTAND_PARAM m6_detector_body_max_y=", m6_detector_body_max_y));
    echo(str("NETSTAND_PARAM m6_detector_body_bottom_z=", m6_detector_body_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_body_top_z=", m6_detector_body_top_z));
    echo(str("NETSTAND_PARAM m6_detector_body_height_z=", m6_detector_body_height_z));
    echo(str("NETSTAND_PARAM m6_detector_body_center_z=", m6_detector_body_center_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_min_x=", m6_detector_shell_min_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_max_x=", m6_detector_shell_max_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_min_y=", m6_detector_shell_min_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_max_y=", m6_detector_shell_max_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_width_y=", m6_detector_shell_width_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_bottom_z=", m6_detector_shell_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_top_z=", m6_detector_shell_top_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_height_z=", m6_detector_shell_height_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_split_x=", m6_detector_shell_split_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_front_max_x=", m6_detector_shell_front_max_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_rear_min_x=", m6_detector_shell_rear_min_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_split_y=", m6_detector_shell_split_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_front_min_y=", m6_detector_shell_front_min_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_rear_max_y=", m6_detector_shell_rear_max_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_inner_min_x=", m6_detector_shell_inner_min_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_inner_max_x=", m6_detector_shell_inner_max_x));
    echo(str("NETSTAND_PARAM m6_detector_support_boss_center_x=", m6_detector_support_boss_center_x));
    echo(str("NETSTAND_PARAM m6_detector_support_y=", m6_detector_support_y));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_min_x=", m6_detector_support_tail_min_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_max_x=", m6_detector_support_tail_max_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_width_x=", m6_detector_support_tail_width_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_min_y=", m6_detector_support_tail_min_y));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_max_y=", m6_detector_support_tail_max_y));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_center_y=", m6_detector_support_tail_center_y));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_bottom_z=", m6_detector_support_tail_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_top_z=", m6_detector_support_tail_top_z));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_center_z=", m6_detector_support_tail_center_z));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_center_x=", m6_detector_support_tail_center_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_thread_engagement_x=", m6_detector_support_tail_thread_engagement_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_thread_entry_x=", m6_detector_support_tail_thread_entry_x));
    echo(str("NETSTAND_PARAM m6_detector_support_tail_thread_center_x=", m6_detector_support_tail_thread_center_x));
    echo(str("NETSTAND_PARAM m6_detector_support_arm_z=", m6_detector_support_arm_z));
    echo(str("NETSTAND_PARAM m6_detector_support_arm_min_x=", m6_detector_support_arm_min_x));
    echo(str("NETSTAND_PARAM m6_detector_support_arm_max_x=", m6_detector_support_arm_max_x));
    echo(str("NETSTAND_PARAM m6_detector_support_leg_x=", m6_detector_support_leg_x));
    echo(str("NETSTAND_PARAM m6_detector_support_leg_bottom_z=", m6_detector_support_leg_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_support_leg_top_z=", m6_detector_support_leg_top_z));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_center_x=", m6_detector_ballhead_center_x));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_center_y=", m6_detector_ballhead_center_y));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_center_z=", m6_detector_ballhead_center_z));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_base_center_z=", m6_detector_ballhead_base_center_z));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_net_stud_center_z=", m6_detector_ballhead_net_stud_center_z));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_sensor_stud_center_x=", m6_detector_ballhead_sensor_stud_center_x));
    echo(str("NETSTAND_PARAM m6_rail_length_z=", m6_rail_length_z));
    echo(str("NETSTAND_PARAM m6_array_bottom_z=", m6_array_bottom_z));
    echo(str("NETSTAND_PARAM m6_array_top_z=", m6_array_top_z));
    echo(str("NETSTAND_PARAM m6_array_center_z=", m6_array_center_z));
    echo(str("NETSTAND_PARAM m6_sensor_axis_x=", m6_sensor_axis_x));
    echo(str("NETSTAND_PARAM m6_sensor_rail_x=", m6_sensor_rail_x));
    echo(str("NETSTAND_PARAM m6_detector_backplate_x=", m6_detector_backplate_x));
    echo(str("NETSTAND_PARAM m6_ballhead_center_x=", m6_ballhead_center_x));
    echo(str("NETSTAND_PARAM m6_ballhead_axis_z=", m6_ballhead_axis_z));
    echo(str("NETSTAND_PARAM m6_ballhead_net_stud_center_x=", m6_ballhead_net_stud_center_x));
    echo(str("NETSTAND_PARAM m6_mount_plate_x=", m6_mount_plate_x));
    echo(str("NETSTAND_PARAM m6_mount_plate_t=", m6_mount_plate_t));
    echo(str("NETSTAND_PARAM m6_mount_slot_length=", m6_mount_slot_length));
    echo(str("NETSTAND_PARAM m6_post_mount_clearance_d=", m6_post_mount_clearance_d));
    echo(str("NETSTAND_PARAM m6_post_mount_hole_y=", m6_post_mount_hole_y));
    echo(str("NETSTAND_PARAM m6_post_mount_bolt_length=", m6_post_mount_bolt_length));
    echo(str("NETSTAND_PARAM m6_post_mount_hole_z=", m6_post_mount_hole_z));
    echo(str("NETSTAND_PARAM m6_mount_plate_width_y=", m6_mount_plate_width_y));
    echo(str("NETSTAND_PARAM m6_mount_plate_height_z=", m6_mount_plate_height_z));
    echo(str("NETSTAND_PARAM m6_yaw_stage_t=", m6_yaw_stage_t));
    echo(str("NETSTAND_PARAM m6_yaw_stage_radius=", m6_yaw_stage_radius));
    echo(str("NETSTAND_PARAM m6_yaw_slot_radius=", m6_yaw_slot_radius));
    echo(str("NETSTAND_PARAM m6_yaw_stage_z=", m6_yaw_stage_z));
    echo(str("NETSTAND_PARAM m6_yaw_carrier_bottom_z=", m6_yaw_carrier_bottom_z));
    echo(str("NETSTAND_PARAM m6_yaw_carrier_height=", m6_yaw_carrier_height));
    echo(str("NETSTAND_PARAM m6_yaw_plate_t=", m6_yaw_plate_t));
    echo(str("NETSTAND_PARAM m6_pitch_yoke_t=", m6_pitch_yoke_t));
    echo(str("NETSTAND_PARAM m6_pitch_yoke_width_y=", m6_pitch_yoke_width_y));
    echo(str("NETSTAND_PARAM m6_pitch_yoke_length_x=", m6_pitch_yoke_length_x));
    echo(str("NETSTAND_PARAM m6_pitch_yoke_foot_t=", m6_pitch_yoke_foot_t));
    echo(str("NETSTAND_PARAM m6_pitch_frame_t=", m6_pitch_frame_t));
    echo(str("NETSTAND_PARAM m6_pitch_frame_outer_width_y=", m6_pitch_frame_outer_width_y));
    echo(str("NETSTAND_PARAM m6_pitch_frame_window_width_y=", m6_pitch_frame_window_width_y));
    echo(str("NETSTAND_PARAM m6_pitch_frame_outer_height_z=", m6_pitch_frame_outer_height_z));
    echo(str("NETSTAND_PARAM m6_pitch_frame_window_height_z=", m6_pitch_frame_window_height_z));
    echo(str("NETSTAND_PARAM m6_pitch_frame_spine_width_y=", m6_pitch_frame_spine_width_y));
    echo(str("NETSTAND_PARAM m6_pitch_frame_hub_d=", m6_pitch_frame_hub_d));
    echo(str("NETSTAND_PARAM m6_pitch_pivot_offset_z=", m6_pitch_pivot_offset_z));
    echo(str("NETSTAND_PARAM m6_pitch_pivot_x=", m6_pitch_pivot_x));
    echo(str("NETSTAND_PARAM m6_pitch_pivot_z=", m6_pitch_pivot_z));
    echo(str("NETSTAND_PARAM m6_roll_pivot_z=", m6_roll_pivot_z));
    echo(str("NETSTAND_PARAM m6_pitch_slot_length=", m6_pitch_slot_length));
    echo(str("NETSTAND_PARAM m6_roll_plate_t=", m6_roll_plate_t));
    echo(str("NETSTAND_PARAM m6_roll_plate_d=", m6_roll_plate_d));
    echo(str("NETSTAND_PARAM m6_roll_slot_length=", m6_roll_slot_length));
    echo(str("NETSTAND_PARAM m6_pivot_d=", m6_pivot_d));
    echo(str("NETSTAND_PARAM m6_roll_pivot_d=", m6_roll_pivot_d));
    echo(str("NETSTAND_PARAM m6_pitch_lock_tap_d=", m6_pitch_lock_tap_d));
    echo(str("NETSTAND_PARAM m6_pitch_lock_tap_depth=", m6_pitch_lock_tap_depth));
    echo(str("NETSTAND_PARAM m6_roll_lock_tap_d=", m6_roll_lock_tap_d));
    echo(str("NETSTAND_PARAM m6_roll_lock_tap_depth=", m6_roll_lock_tap_depth));
    echo(str("NETSTAND_PARAM m6_roll_pivot_bolt_length=", m6_roll_pivot_bolt_length));
    echo(str("NETSTAND_PARAM m6_stage_bolt_d=", m6_stage_bolt_d));
    echo(str("NETSTAND_PARAM m6_fine_adjuster_d=", m6_fine_adjuster_d));
    echo(str("NETSTAND_PARAM m6_fine_adjuster_length=", m6_fine_adjuster_length));
    echo(str("NETSTAND_PARAM m6_yaw_adjuster_block_width_x=", m6_yaw_adjuster_block_width_x));
    echo(str("NETSTAND_PARAM m6_yaw_adjuster_block_depth_y=", m6_yaw_adjuster_block_depth_y));
    echo(str("NETSTAND_PARAM m6_yaw_adjuster_block_height_z=", m6_yaw_adjuster_block_height_z));
    echo(str("NETSTAND_PARAM m6_yaw_adjuster_foot_inset_y=", m6_yaw_adjuster_foot_inset_y));
    echo(str("NETSTAND_PARAM m6_yaw_adjuster_tap_d=", m6_yaw_adjuster_tap_d));
    echo(str("NETSTAND_PARAM m6_yaw_adjuster_tap_depth=", m6_yaw_adjuster_tap_depth));
    echo(str("NETSTAND_PARAM m6_yaw_adjuster_tip_overtravel_y=", m6_yaw_adjuster_tip_overtravel_y));
    echo(str("NETSTAND_PARAM m6_pitch_adjuster_offset_z=", m6_pitch_adjuster_offset_z));
    echo(str("NETSTAND_PARAM m6_pitch_adjuster_bridge_t=", m6_pitch_adjuster_bridge_t));
    echo(str("NETSTAND_PARAM m6_roll_adjuster_offset_z=", m6_roll_adjuster_offset_z));
    echo(str("NETSTAND_PARAM m6_roll_adjuster_contact_y=", m6_roll_adjuster_contact_y));
    echo(str("NETSTAND_PARAM m6_roll_adjuster_arm_depth_y=", m6_roll_adjuster_arm_depth_y));
    echo(str("NETSTAND_PARAM m6_roll_adjuster_arm_t=", m6_roll_adjuster_arm_t));
    echo(str("NETSTAND_PARAM m6_roll_adjuster_clearance_y=", m6_roll_adjuster_clearance_y));
    echo(str("NETSTAND_PARAM m6_roll_adjuster_length=", m6_roll_adjuster_length));
    echo(str("NETSTAND_PARAM m6_yaw_range_deg=", m6_yaw_range_deg));
    echo(str("NETSTAND_PARAM m6_pitch_range_deg=", m6_pitch_range_deg));
    echo(str("NETSTAND_PARAM m6_roll_range_deg=", m6_roll_range_deg));
    echo(str("NETSTAND_PARAM m6_yaw_base_mount_clearance_d=", m6_yaw_base_mount_clearance_d));
    echo(str("NETSTAND_PARAM m6_yaw_base_mount_tap_d=", m6_yaw_base_mount_tap_d));
    echo(str("NETSTAND_PARAM m6_yaw_base_mount_tap_depth=", m6_yaw_base_mount_tap_depth));
    echo(str("NETSTAND_PARAM m6_yaw_base_mount_hole_y=", m6_yaw_base_mount_hole_y));
    echo(str("NETSTAND_PARAM m6_yaw_base_mount_bolt_length=", m6_yaw_base_mount_bolt_length));
    echo(str("NETSTAND_PARAM m5_yaw_carrier_mount_clearance_d=", m5_yaw_carrier_mount_clearance_d));
    echo(str("NETSTAND_PARAM m5_yaw_carrier_mount_tap_d=", m5_yaw_carrier_mount_tap_d));
    echo(str("NETSTAND_PARAM m5_yaw_carrier_mount_tap_depth=", m5_yaw_carrier_mount_tap_depth));
    echo(str("NETSTAND_PARAM m5_yaw_carrier_mount_hole_y=", m5_yaw_carrier_mount_hole_y));
    echo(str("NETSTAND_PARAM m5_yaw_carrier_mount_bolt_length=", m5_yaw_carrier_mount_bolt_length));
    echo(str("NETSTAND_PARAM stg120_head_length=", stg120_head_length));
    echo(str("NETSTAND_PARAM stg120_active_length=", stg120_active_length));
    echo(str("NETSTAND_PARAM stg120_head_width=", stg120_head_width));
    echo(str("NETSTAND_PARAM stg120_head_thickness=", stg120_head_thickness));
    echo(str("NETSTAND_PARAM stg120_beam_count=", stg120_beam_count));
    echo(str("NETSTAND_PARAM stg120_beam_pitch=", stg120_beam_pitch));
    echo(str("NETSTAND_PARAM stg120_detect_distance_max=", stg120_detect_distance_max));
    echo(str("NETSTAND_PARAM stg120_outer_face_x=", stg120_outer_face_x));
    echo(str("NETSTAND_PARAM stg120_outer_frame_min_x=", stg120_outer_frame_min_x));
    echo(str("NETSTAND_PARAM stg120_outer_frame_max_x=", stg120_outer_frame_max_x));
    echo(str("NETSTAND_PARAM stg120_reference_height=", stg120_reference_height));
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
    m6_beam_preview();
    if (m6_show_optical_direction) {
        m6_optical_full_direction_preview();
    }
    // PVDF 座位于全宽网顶承载条的中段，只有在完整装配中才有真实承载关系。
    sensor_mount(1);
    sensor_mount(-1);
    reference_line();
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
} else if (PART == "m6_sensor_rail") {
    sided(default_side) m6_sensor_rail_positive();
} else if (PART == "m6_sensor_test_coupon") {
    m6_sensor_test_coupon_positive();
} else if (PART == "m6_sensor_array") {
    sided(default_side) m6_sensor_array_positive();
} else if (PART == "m6_sensor_single") {
    m6_sensor_single_preview(default_side);
    if (m6_show_optical_direction) {
        m6_sensor_single_direction_preview(default_side);
    }
} else if (PART == "m6_detector_fit_probe") {
    sided(default_side) m6_detector_fit_probe_positive();
    if (m6_show_optical_direction) {
        m6_optical_direction_preview(default_side);
    }
} else if (PART == "m6_detector_fit_body") {
    sided(default_side) m6_detector_fit_body_positive();
} else if (PART == "m6_detector_body") {
    sided(default_side) m6_detector_body_positive();
} else if (PART == "m6_detector_shell_front") {
    sided(default_side) m6_detector_shell_front_positive();
} else if (PART == "m6_detector_shell_rear") {
    sided(default_side) m6_detector_shell_rear_positive();
} else if (PART == "m6_detector_bottom_cover") {
    sided(default_side) m6_detector_bottom_cover_positive();
} else if (PART == "m6_detector_support") {
    sided(default_side) m6_detector_support_positive();
} else if (PART == "m6_detector_mount") {
    sided(default_side) m6_detector_mount_positive();
    if (m6_show_optical_direction) {
        m6_optical_direction_preview(default_side);
    }
} else if (PART == "m6_detector_exploded") {
    sided(default_side) m6_detector_exploded_positive();
    if (m6_show_optical_direction) {
        m6_optical_exploded_direction_preview(default_side);
    }
} else if (PART == "m6_mount_adapter") {
    sided(default_side) m6_mount_adapter_positive();
} else if (PART == "m6_detector_backplate") {
    sided(default_side) m6_detector_shell_rear_positive();
} else if (PART == "m6_ballhead") {
    sided(default_side) m6_detector_ballhead_positive();
} else if (PART == "m6_ballhead_mount") {
    sided(default_side) m6_detector_mount_positive();
} else if (PART == "m6_gimbal") {
    m6_gimbal(default_side);
} else if (PART == "m6_machining_detector_body") {
    sided(default_side) m6_machining_detector_body_positive();
} else if (PART == "m6_machining_support") {
    sided(default_side) m6_machining_support_positive();
} else if (PART == "m6_machining_rail") {
    sided(default_side) m6_machining_rail_positive();
} else if (PART == "m6_machining_adapter") {
    sided(default_side) m6_machining_adapter_positive();
} else if (PART == "m6_machining_backplate") {
    sided(default_side) m6_machining_backplate_positive();
} else if (PART == "m6_machining_yaw_base") {
    sided(default_side) m6_machining_yaw_base_positive();
} else if (PART == "m6_machining_yaw_top") {
    sided(default_side) m6_machining_yaw_top_positive();
} else if (PART == "m6_machining_pitch_yoke") {
    sided(default_side) m6_machining_pitch_yoke_positive();
} else if (PART == "m6_machining_pitch_frame") {
    sided(default_side) m6_machining_pitch_frame_positive();
} else if (PART == "m6_machining_roll_disc") {
    sided(default_side) m6_machining_roll_disc_positive();
} else if (PART == "stg120_outer_carrier") {
    stg120_outer_carrier(default_side);
} else if (PART == "stg120_center_bridge") {
    stg120_center_bridge();
} else if (PART == "stg120_preview") {
    stg120_preview();
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
