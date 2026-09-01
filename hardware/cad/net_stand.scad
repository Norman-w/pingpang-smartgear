// 乒乓智配：内置式球网支架与过网高度检测结构
// 当前主线 CAD。它替换传统球网和原有球网立柱，不再外挂到旧立柱上。
// 单位：mm；x=球台宽度方向，y=球台长度方向，z=球台台面以上。
//
// 预览/导出：
//   PART="assembly"          含球台截面、网、双侧支架和传感器的装配预览
//   PART="left_stand"         左侧立柱/桌下夹持/STG 托架结构检查件
//   PART="right_stand"        右侧立柱/桌下夹持/STG 托架结构检查件
//   PART="post"               单侧立柱主体
//   PART="post_segment"       当前单段立柱诊断/打印件（由 post_segment_index 选择）
//   PART="post_clamp_carrier" 整根立柱与桌外侧滑入载体一体打印件
//   PART="clamp_body_segment"  桌下 C 形夹内段/电子腔与母滑槽打印件
//   PART="post_segment"       兼容入口；输出同一整根立柱主体
//   PART="lower_stand_segment" 兼容入口；输出同一整根立柱+载体
//   PART="upper_stand_segment" 兼容入口；输出同一整根立柱主体
//   PART="post_joint_sleeve"  旧版立柱接缝兼容诊断（当前不装配）
//   PART="post_joint_key"     旧版立柱接缝兼容诊断（当前不装配）
//   PART="post_joint_exploded" 兼容入口；显示整根立柱向夹体滑入
//   PART="post_clamp_seated"   整根立柱推进到底后坐在夹具基台上的装配预览
//   PART="post_clamp_seated_fit_section" 立柱底面/基台/滑靴真实坐定剖面
//   PART="post_clamp_entry_open_section" x+入口真实材料剖面（诊断件）
//   PART="post_clamp_slide_interface_exploded" 立柱底部/基台/滑道沿 x 爆炸细节
//   PART="post_down_extension_stage1" 立柱向下延伸并按绿色 x-z 截面削料的候选件
//   PART="post_down_extension_stage1_raw" 立柱向下延伸的未削料原始包络（诊断件）
//   PART="post_down_extension_stage1_exploded" 立柱与阶段1向下延伸候选件爆炸预览（不含C形夹）
//   PART="post_skp_leg_foot_stage1" 按用户 SKP 原尺寸实现的单一腿脚候选件（含终端倒角）
//   PART="post_skp_leg_foot_stage1_raw" 用户 SKP 腿脚原尺寸、未倒角诊断件
//   PART="post_skp_leg_foot_stage1_exploded" 当前立柱与 SKP 腿脚候选件爆炸预览（不含C形夹）
//   PART="post_skp_leg_foot_fit_tool" 黄色下端+绿色腿脚的 C 型夹让位工具（诊断）
//   PART="clamp_body_skp_leg_foot_fit" 用黄色+绿色候选外形对灰色 C 夹做让位的诊断件
//   PART="post_skp_leg_foot_clamp_fit" 黄色立柱+绿色腿脚+让位后的灰色 C 夹可装配候选
//   PART="clamp_slide_exploded" 夹体母壳/载体公轨/防滑脱 M4 爆炸预览
//   PART="clamp_slide_fit_probe" 夹体公母滑槽局部装配剖切
//   PART="clamp_slide_fit_section" 夹体单侧宽面互锁滑道截面（真实装配基准）
//   PART="table_clamp"        单侧传统桌下夹持机构装配预览
//   PART="table_clamp_section" 桌板剖面/免打孔夹紧受力路径预览
//   PART="table_clamp_body"   单侧固定 C 形夹体
//   PART="clamp_electronics_gasket" 梯形电子腔连续柔性压紧垫（单独打印）
//   PART="clamp_electronics_ui_panel" 盖面交互子板/屏幕/按钮/声学占位
//   PART="clamp_electronics_ui_bezel" 可拆屏幕/按钮/指示灯/扬声器/USB-C 面框
//   PART="clamp_electronics_emitter_preview" 左侧发射电源子板/内置电池占位
//   PART="clamp_electronics_system_preview" 左右主控/发射电源/交互装配总览
//   PART="clamp_electronics_full_cutaway" 右侧电子腔完整剖切安装
//   PART="clamp_electronics_exploded" 单侧主控电子腔爆炸装配
//   PART="clamp_electronics_emitter_exploded" 单侧发射电子腔爆炸装配
//   PART="clamp_top_pad"     台面上表面胶皮装配占位（现场粘贴，不进正式打印包）
//   PART="clamp_pressure_pad" 台底可动圆盘压块（底面 M8 圆头收纳窝）
//   PART="clamp_screw"        M8×1.25 金属螺杆装配占位（非打印件，顶端圆头）
//   PART="clamp_body_nut"     固定在下臂螺母座中的 M8 螺母装配占位（标准件）
//   PART="clamp_knob"         手拧旋钮（含两枚 M8 对锁螺母捕获窝）
//   PART="clamp_knob_nut"     旋钮内捕获的两枚 M8 对锁螺母（标准件）
//   PART="net"                球网/网布装配占位（非打印件）
//   PART="net_rail"           旧版网顶承载条兼容预览（当前装配不使用）
//   PART="net_rail_segment"   旧版网顶承载条单段诊断件（当前不打印）
//   PART="net_rail_splice"    旧版网顶承载条拼接片诊断件（当前不打印）
//   PART="net_rail_saddle"    旧版网顶承托座诊断件（当前不打印）
//   PART="optical_rail"       旧版 10 路离散红外模块导轨（兼容诊断件）
//   PART="optical_strip"      旧版 10 路离散红外模块装配预览（兼容诊断件）
//   PART="optical_module_carrier" 旧版单个光学模块载台（兼容诊断件）
//   PART="m6_sensor_rail"     旧版 M6×0.75 直角十路单竖条/7 字座（兼容诊断件）
//   PART="m6_sensor_test_coupon" 旧版单 M6 7 字座试装样件（兼容诊断件）
//   PART="m6_sensor_array"    当前十路 M6 发射/接收器与长条主体装配占位
//   PART="m6_detector_fit_probe" 仅验证长条主体与真实 L 型激光头的 2 mm 卡入关系
//   PART="m6_detector_body"   当前 PETG 长条主体（45°斜向六角沉孔/短过孔）
//   PART="m6_detector_shell_front" PETG x- 光学端前盖候选
//   PART="m6_detector_shell_rear" PETG x+ 线缆端后盖候选
//   PART="m6_detector_bottom_cover" PETG 底盖候选
//   PART="m6_detector_wiring_reference" 两侧十路线缆汇线/压紧出线参考
//   PART="m6_detector_bottom_gasket" M6 底盖连续柔性压紧垫（单独打印）
//   PART="net_clamp_clip"      单侧全高 U 形滑入卡网夹（PETG 打印件）
//   PART="net_clamp_rod"       旧调用名，输出同一未旋转 U 形卡夹诊断件
//   PART="net_clamp_fit_probe" 网布穿过 3 mm 过道后插入 U 夹的局部诊断
//   PART="net_clamp_fit_section" 网布/立柱/卡夹截面（真实装配基准）
//   PART="m6_detector_exploded" 右/左侧检测器非剖切爆炸图
//   PART="m6_detector_net_connector" 历史采购金属 90°连接器占位（不属于当前装配）
//   PART="m6_detector_mount" 当前主体/器件/完整前后底盖/竖直采购球头装配（固定网柱独立）
//   PART="m6_detector_backplate" 兼容旧调用名；输出当前后盖
//   PART="m6_ballhead"        13 mm 采购球头云台竖直姿态占位（非打印件）
//   PART="m6_ballhead_mount" 兼容旧调用名；输出当前主体与采购球头装配
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
// M6×0.75 发射/接收器件装入一根可打印 PETG 长条主体（后续可复用包络改做
// CNC）。光学轴沿 x；
// L 型器件的蓝色尾线支路局部朝 z-，整件绕光束 x 轴旋转 -45°，从主体
// x+（右）/x-（左）的后方装入。主体按首样复核采用 x=10 mm 厚、y=56 mm
// 宽、z=216 mm 高的竖直承载条，不再用只能当薄背条的 6×18 mm 截面；原始十个通道中心
// 以 20 mm 节距从过网高度 +10 mm 排到 +190 mm；安装总成的 z 抬高量由
// “网顶净空 + 壳体底部”自动计算，并与球头底座/立柱顶面共用同一安装基准；
// 右侧器件的外侧装入方向为 x+，左侧由 SIDE 镜像后外侧装入方向为 x-。光学
// 头部穿过主体的头部让位孔，线缆留在主体外侧，不在铝材里挖线束槽；x 向
// 浅六角座只卡住真实金属头的六角外形，M6 外丝直接穿过主体，在外表面只
// 安装一枚原配 5 mm 螺帽，14 mm 外丝仍保留足够的外露长度。
// 当前装配已包含 PETG 前盖、后盖和底盖候选件；主体保持简单的 10×56×216 mm
// 长方条，不再带 T 形尾座。后盖的 x+ 背面中央在 y=0、z 中心做独立加厚
// boss，并开 x 向 Ø7.0 1/4-20 外牙通孔，供 13 mm 球头上端的 1/4-20 外牙从后方穿入；左侧
// 发射端通过 SIDE 镜像后，boss 落在 x- 背面，孔轴反向指向 x+；首样可以用
// 通螺栓/标准 1/4-20 捕获螺母，未来 CNC 时可改金属嵌件。采购球头保持竖直姿态，球头 z- 接口的 M8
// 直接进入浅黄色立柱顶面的中心 M8 攻丝底孔，球头安装轴心与后盖 boss 的 z 中心一致。网布功能区从黄灰交界 z=16 mm 共面起，向上一个网高至 z=168.5 mm；
// 固定网柱实体继续向上到 post_top。
// 整根单独打印并坐在固定 C 夹主体上；不再使用旧版独立 90°连接器或旧版独立上段外件。薄壳只作定位/保护，M6 独立支撑
// 的承力界面须在真实接口冻结后用固定件验证。M6 器件、球头、PVDF 薄膜、网布、金属螺杆和夹持软垫均为外购/装配边界；
// 主体、壳体和底盖可作为 PETG 首样打印件。
// M8 螺杆和螺母只在装配/剖面和 PART 单件预览中显示；STG-120ML 光纤头
// 保留为历史诊断件，不再作为当前装配主线。
// 前后盖沿 x 分成两件，均从 z+ 套入主体；底盖向下独立安装。沉头螺钉只是
// 盖件到主体的固定件；当前已冻结的承力路径是“传感器六角/螺杆 -> PETG/CNC 主体 ->
// 后盖 x 背面中央加厚 boss -> 采购 13 mm 球头上端 1/4-20 外牙 -> 球头 z- M8 -> 浅黄色立柱顶面”。电子腔、M6 盖件和出线处均有连续
// 压合面、定位唇、可替换胶条/压紧出线件参考；这里的“水密”只要求盒盖装好后严丝合缝、无明显贯通缝，
// 不代表 IP 等级或认证。该文件验证机械意图与参数关系，不等同于最终
// PETG 打印强度、球台兼容性、实物螺纹/光学精度或 NPN 电气验收。
// 整根立柱外侧共同保留贯穿网高的接收腔；网布先穿过立柱主体的 y 向
// 3 mm 过道，再把全高 U 形卡夹沿 x 从外侧滑入。卡夹两片 jaw 夹住网布
// 两面，网布张力/绳拉力把卡夹压向立柱的内端承托面。立柱侧面只做一处
// 内嵌被动防拔止挡，卡夹一侧 jaw 留有入口让位和一体弹性扣舌；止挡不在网布
// 主拉力路径中，不使用横向穿钉、螺钉或螺母。装入时扣舌让止挡越过，回拉时
// 扣舌的闭合肩挡住止挡；拆卸时按开让位侧 jaw，再把卡夹反向滑出。

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
// The upright keeps the top cross-section all the way down to the explicit
// 30 mm transition boundary above the C-clamp contact plane.  Only the lower
// section tapers to the broad C-clamp contact footprint.  The upright starts
// on the gray/yellow seat and never enters the lower C-clamp body.
post_interface_transition_height_z = 30;
post_interface_transition_extra_x = 3.5;
// Compatibility alias for older reports.  The active lower depth is derived
// from the complete C-clamp contact depth below, not from this legacy value.
post_interface_transition_extra_y = 10;
// ITTF 现行规则要求网柱外侧边界在球台侧线外 152.5 mm；这里把
// 152.5 mm 作为网架外边界，而不是把网柱中心误当成外伸量。28 mm
// 立柱的中心偏移因此为 152.5 - 14 = 138.5 mm。这样网布的名义总宽为
// 1830 mm，左右各比 1525 mm 球台多 152.5 mm；网顶不设置独立轨道。
net_post_outboard_extension = 152.5;
// 立柱外置 138.5 mm，使光学导轨仍可从立柱内侧悬到台边；模块镜头
// 轴线覆盖台面边缘，而不会嵌入实心立柱。
post_offset = 138.5;
post_center_x = table_edge_x + post_offset;
// C 形夹保留桌面的夹持开口、上/下接触界面和压块/螺杆区域；桌边外侧
// （x+、不接触桌面）的区域改为沿 y 全深的实心桥体。下部承力段靠球台
// （x-）侧厚 40 mm，并沿斜底过渡到加厚后的下夹臂；真实 PETG 材料、层向
// 和夹紧力仍需首样验证。
clamp_reinforcement_inboard_offset_x = 3;
clamp_reinforcement_near_table_thickness_z = 40;
clamp_reinforcement_depth_y = 58;
clamp_solid_bridge_clearance_x = 0.2;
clamp_lower_arm_clearance = 10;
// 梯形下方预留首样电子腔：保留 4 mm 顶板、两侧各 9 mm 承力壁，底部
// 以可拆盖板封闭。ESP32 主控板和受保护 1S 电池包只占用这个腔体，不把
// 电池或 USB 充电电路塞进桌面夹持/压块的受力区。
clamp_electronics_cavity_inboard_margin_x = 18;
clamp_electronics_cavity_outboard_margin_x = 38;
clamp_electronics_cavity_wall_y = 9;
clamp_electronics_cavity_roof_t = 4;
clamp_electronics_cavity_cover_t = 3;
clamp_electronics_board_length_x = 90;
clamp_electronics_board_width_y = 34;
clamp_electronics_battery_length_x = 65;
clamp_electronics_battery_width_y = 30;
clamp_electronics_battery_thickness_z = 7;
clamp_electronics_battery_clearance_z = 2;
clamp_electronics_mount_boss_d = 8;
clamp_electronics_mount_pilot_d = 3.4;
clamp_electronics_board_t = 1.6;
// Reserve the ESP32/module/boost top envelope, not only the bare PCB plane.
// These are the measured maxima of the KiCad STL export, not a generic IC
// height guess.  The ESP32 board export reaches z=7.595 mm above its local
// datum because the USB-C/headers and module are included in the solid.
clamp_electronics_component_height_z = 7.6;
clamp_electronics_component_clearance_z = 1;
clamp_electronics_board_top_clearance_z =
    clamp_electronics_component_height_z +
    clamp_electronics_component_clearance_z;
clamp_electronics_board_mount_hole_inset_x = 4.5;
clamp_electronics_board_mount_hole_inset_y = 4.5;
clamp_electronics_board_standoff_d = 6;
clamp_electronics_board_standoff_floor_clearance_z = 0.8;
clamp_electronics_battery_rail_t = 2;
clamp_electronics_battery_rail_h = 8;
clamp_electronics_battery_rail_clearance_y = 1.5;
// 连续压合界面：密封条/胶条是可替换件，盖板本体仍保持可打印。
clamp_electronics_gasket_width = 3;
clamp_electronics_gasket_height = 1.2;
clamp_electronics_gasket_clearance = 0.25;
clamp_electronics_cover_lip_t = 1.6;
clamp_electronics_cover_lip_h = 1.6;
clamp_electronics_cover_lip_clearance = 0.35;
// 盖面交互子板与面板器件的首样占位；它位于底盖外侧，不占用母板安装层。
clamp_electronics_ui_board_length_x = 60;
clamp_electronics_ui_board_width_y = 28;
clamp_electronics_ui_board_t = 1.6;
clamp_electronics_ui_screen_length_x = 28;
clamp_electronics_ui_screen_width_y = 14;
clamp_electronics_ui_button_d = 10;
clamp_electronics_ui_led_d = 4;
clamp_electronics_ui_speaker_d = 20;
clamp_electronics_ui_gland_d = 12;
// 发射端放在零件较少的左侧，内置受保护 1S 电池；子板同时保留外接输入。
clamp_electronics_emitter_board_length_x = 70;
clamp_electronics_emitter_board_width_y = 34;
clamp_electronics_emitter_board_t = 1.6;
clamp_electronics_emitter_battery_length_x = 65;
clamp_electronics_emitter_battery_width_y = 30;
clamp_electronics_emitter_battery_thickness_z = 7;
clamp_electronics_emitter_external_gland_d = 12;
// KiCad-generated board/component exports.  These are deliberately referenced
// by the mechanical source instead of being redrawn as anonymous boxes.  The
// generator writes the four files under hardware/electronics/3d/v0.2.
electronics_kicad_models_enabled = true;
// KiCad STL exports use y=-board_y and include the component overhang.  The
// main board is shifted 18.5 mm so its actual -38.04..1.105 mm model envelope
// sits inside the +/-20 mm cavity with measurable wall clearance.  The other
// boards have no y overhang and are centered on their physical board widths.
clamp_electronics_main_board_y_shift = 18.5;
clamp_electronics_emitter_board_y_shift =
    clamp_electronics_emitter_board_width_y / 2;
clamp_electronics_ui_board_y_shift = clamp_electronics_ui_board_width_y / 2;
clamp_electronics_faceplate_t = 4;
clamp_electronics_faceplate_border = 3;
clamp_electronics_faceplate_window_clearance = 1.2;
post_top_margin = 18;

// 网、光栅和网顶传感器
// The post/cloth/clip datum is the top of the fixed C-clamp seat.  It is kept
// explicit here because the seat aliases are declared later in this source;
// the assertion block below requires it to stay equal to post_bottom.
net_fixture_bottom_z = 16;
net_height = 152.5;
net_panel_bottom_z = net_fixture_bottom_z;
net_panel_top_z = net_panel_bottom_z + net_height;
// 立柱要高到足以让完整检测器壳体越过网顶。检测器、采购球头和
// 光学方向预览作为一个刚性总成整体上抬；具体抬高量在 M6 壳体包络
// 定义完成后自动计算，不能再用网页里的固定 20 mm 假位置。
// 网端卡持不再使用一根与网布同平面的圆柱。右侧立柱的 outboard x+ 面
// 留出窄的全高接收腔，网布先从球台中心侧沿 x 穿过 3 mm 过道；随后把
// 一个带上下夹槽的竖向 U 形卡夹从 x+ 向 x- 滑入，使网布位于两条夹 jaw
// 之间。左侧由 sided(-1) 镜像，拆卸时反向滑出。这里的宽腔参数保留旧名，
// 但现在表示 U 形卡夹的滑入接收腔，而不是圆柱孔。
// Compatibility parameter names retained for the old probe schema.  These
// now describe the depth/height of the active U-clip receiver pocket, not a
// cylindrical printed retainer.
net_clamp_channel_depth_x = 25;
net_clamp_cylinder_insertion_depth_x = 25;
net_clamp_channel_back_wall_t_x = 3;
net_clamp_cylinder_interference_d = 14;
net_clamp_cylinder_actual_d =
    net_clamp_cylinder_interference_d - 2;
net_clamp_channel_side_clearance = 0.6;
net_clamp_channel_back_clearance = 0.6;
net_clamp_channel_width_y = 8;
// The removable clip crossbar sits just beyond the nominal post face.  The
// channel is intentionally open at x+ so the complete vertical U-clip can be
// inserted and removed from outside; the fabric terminates at the post face
// and never has to pass through the crossbar.
net_clamp_channel_outboard_extension_x = 4.5;
net_clamp_channel_bottom_z = net_fixture_bottom_z;
net_clamp_channel_top_z = net_fixture_bottom_z + net_height;
net_clamp_channel_void_min_x =
    post_center_x + post_body_width / 2 -
    net_clamp_channel_depth_x +
    net_clamp_channel_back_wall_t_x;
net_clamp_channel_void_max_x =
    post_center_x + post_body_width / 2 +
    net_clamp_channel_outboard_extension_x;
net_clamp_cylinder_center_x =
    net_clamp_channel_void_min_x +
    net_clamp_cylinder_interference_d / 2 +
    net_clamp_channel_back_clearance;
net_clamp_cylinder_height =
    net_clamp_channel_top_z - net_clamp_channel_bottom_z;
// 当前主线不在网顶设置轨道或承载横梁；下面的旧 net_rail_* 参数和模块只
// 为历史布局/回归诊断保留，不能被 assembly 或正式打印清单调用。
net_top_rail_required = 0;
net_rail_height = 10;
net_rail_depth = 18;
net_sheet_t = 1.2;
// The printed U clip is a vertical part that slides along x. Its two jaws
// straddle the 1.2 mm net edge; the outer crossbar joins them. The fit is
// replaceable and the net/rope tension is carried into the post's inboard
// support. One embedded side keeper only prevents accidental reverse pull-out;
// it is not a screw hole and it is not the working tension path.
net_clamp_clip_clearance_x = 0.2;
net_clamp_clip_length_x =
    net_clamp_channel_void_max_x - net_clamp_channel_void_min_x -
    2 * net_clamp_clip_clearance_x;
net_clamp_clip_inner_x =
    net_clamp_channel_void_min_x + net_clamp_clip_clearance_x;
net_clamp_clip_outer_x =
    net_clamp_clip_inner_x + net_clamp_clip_length_x;
net_clamp_clip_jaw_t_y = 2.4;
net_clamp_clip_jaw_clearance_y = 0.6;
net_clamp_clip_jaw_gap_y = net_sheet_t + net_clamp_clip_jaw_clearance_y;
net_clamp_clip_jaw_center_y =
    net_clamp_clip_jaw_gap_y / 2 + net_clamp_clip_jaw_t_y / 2;
net_clamp_clip_outer_half_y =
    net_clamp_clip_jaw_center_y + net_clamp_clip_jaw_t_y / 2;
net_clamp_clip_crossbar_t_x = 3;
// One fixed keeper is integrated into the post's positive-y channel wall. The
// clip's positive-y jaw has a short relief open at its inner sliding tip. When
// the clip is fully seated, the keeper sits inside that relief; reversing the
// slide brings the jaw against the keeper after only a small service stroke.
// The keeper itself remains a solid post anchored 0.4 mm into the channel wall.
// The lead-in is now supplied by the clip's own one-way spring tongue, so the
// fixed post has no extra nose that could collide with that tongue at full seat.
net_clamp_keeper_enabled = true;
net_clamp_keeper_z_offset = 72;
net_clamp_keeper_height_z = 8;
net_clamp_keeper_x_min = net_clamp_clip_inner_x + 1.5;
net_clamp_keeper_x_max = net_clamp_clip_inner_x + 2.5;
net_clamp_keeper_lead_in_x = 0;
net_clamp_keeper_y_min =
    net_clamp_clip_jaw_center_y + net_clamp_clip_jaw_t_y / 2 - 0.9;
net_clamp_keeper_y_max =
    net_clamp_channel_width_y / 2 + 0.4;
net_clamp_keeper_z =
    net_clamp_channel_bottom_z + net_clamp_keeper_z_offset;
net_clamp_keeper_relief_min_x = net_clamp_clip_inner_x - 0.2;
net_clamp_keeper_relief_max_x = net_clamp_clip_inner_x + 4.2;
net_clamp_keeper_relief_min_y = net_clamp_keeper_y_min - 0.15;
net_clamp_keeper_relief_max_y = net_clamp_clip_outer_half_y + 0.15;
net_clamp_keeper_relief_clearance_z = 0.2;
// The clip-side anti-withdrawal feature is a short spring tongue fused to the
// positive-y jaw.  Its sloped x- nose lets the fixed keeper pass while the clip
// slides inward (x+ -> x-); its x+ shoulder is closed, so a reverse pull makes
// the keeper stop against it.  The 0.3 mm installed gap is intentional and is
// the visual/print clearance between the tongue and the fixed keeper.
net_clamp_keeper_latch_x_min = net_clamp_keeper_relief_min_x + 0.4;
net_clamp_keeper_latch_x_max = net_clamp_keeper_relief_min_x + 1.4;
net_clamp_keeper_latch_y_min = net_clamp_keeper_relief_min_y - 0.2;
net_clamp_keeper_latch_y_max = net_clamp_keeper_latch_y_min + 1.0;
net_clamp_keeper_latch_z = net_clamp_keeper_z + 0.4;
net_clamp_keeper_latch_height_z = net_clamp_keeper_height_z - 0.8;
// 网布位于 x-z 平面，厚度沿 y；在立柱实体和局部顶部加厚块中都切出
// 3 mm 的贯穿过道，使网布能从球台中心方向穿到外侧卡夹腔。这里的 x
// 范围含局部顶部加厚块；卡夹腔的内端止挡不切穿这条过道。
net_passage_width_y = 3;
net_passage_bottom_z = net_fixture_bottom_z;
net_passage_top_z = net_fixture_bottom_z + net_height;
net_passage_side_clearance_y =
    (net_passage_width_y - net_sheet_t) / 2;
net_passage_body_extension_x = 5;
net_passage_min_x =
    post_center_x - post_body_width / 2 -
    net_passage_body_extension_x - 0.2;
net_passage_max_x =
    post_center_x + post_body_width / 2 +
    net_passage_body_extension_x + 0.2;
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
// 单件试装样件只验证真实传感器、螺母防转和线缆让位，不进入 35 件正式
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
// Purchased 13 mm mini ballhead from the referenced product page.  The
// movable upper plate carries a fixed 1/4-20 UNC male stud; when the ball is
// opened 90 degrees that stud points along x into the detector rear boss.  The
// lower mounting end is the selected 13mm球【M8外牙】 variant and points z-.
// These are visual/fit envelopes for bought metal hardware, never printable
// thread claims.
m6_ballhead_ball_d = 13;
m6_ballhead_housing_d = 28;
m6_ballhead_housing_length_x = 26;
m6_ballhead_body_depth_y = 24;
m6_ballhead_body_corner_radius = 4;
m6_ballhead_ball_socket_d = 17;
m6_ballhead_side_plate_d = 24;
m6_ballhead_side_plate_t_x = 4;
m6_ballhead_lock_knob_d = 18;
m6_ballhead_lock_knob_t_y = 8;
m6_ballhead_lock_knob_ridge_count = 24;
m6_ballhead_base_d = 32;
m6_ballhead_base_t = 8;
// Compatibility name retained because existing preview/validation consumers
// call this the sensor-side stud.  Its actual selected thread is fixed 1/4-20,
// not M8.
m6_ballhead_sensor_stud_d = 6.35;
m6_ballhead_sensor_stud_length = 16;
m6_ballhead_sensor_thread_core_d = 5.35;
m6_ballhead_sensor_thread_pitch = 1.27;
m6_ballhead_net_stud_d = 8;
m6_ballhead_net_stud_length = 28;
m6_ballhead_net_thread_core_d = 6.6;
m6_ballhead_net_thread_pitch = 1.25;
m6_ballhead_top_nut_af = 11.1;
m6_ballhead_top_nut_h = 5.5;
m6_ballhead_bottom_nut_af = 13;
m6_ballhead_bottom_nut_h = 6.5;
m6_ballhead_nut_clearance = 0.35;
m6_ballhead_top_nut_pocket_af =
    m6_ballhead_top_nut_af + 2 * m6_ballhead_nut_clearance;
m6_ballhead_top_nut_pocket_depth =
    m6_ballhead_top_nut_h + 2 * m6_ballhead_nut_clearance;
m6_ballhead_bottom_nut_pocket_af =
    m6_ballhead_bottom_nut_af + 2 * m6_ballhead_nut_clearance;
m6_ballhead_bottom_nut_pocket_depth =
    m6_ballhead_bottom_nut_h + 2 * m6_ballhead_nut_clearance;
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
// z-slots pass through the current 28 x 38 mm net-frame upright and accept
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
// 机械契约：主体、前盖、后盖、底盖当前均为 PETG 首样候选；后续可按同一
// 包络改做 CNC/金属版本；盖件新增压合面与胶条参考，目标是盒盖装配严丝合缝，不做 IP 等级承诺。主体位于沿光束 x 轴拆分的前后壳之间，
// 前盖在光学端 x-、后盖在线缆端 x+；两盖从 z+ 套入，底盖从 z-贴合。
// M3/M4 沉头螺钉只锁盖件，传感器和主要支撑载荷不通过 PETG 舌片闭环。
m6_detector_body_depth_y = 56.0;
m6_detector_body_center_y = 0.0;
m6_detector_body_length_x = 10.0;
m6_detector_body_margin_z = 18;
m6_detector_body_front_margin_x = 1;
// First article scope: model only the long rectangular PETG-printable bar and the
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
// The purchased ballhead is mounted directly on the flat top of the same
// upright.  Keep the shell just above the net and derive the installed z datum
// from the actual raw shell bottom; this gives the current 29 mm lift while
// remaining parametric if the sensor pitch or cover margins change.
m6_detector_mount_net_clearance_z = 2;
m6_detector_raw_shell_bottom_z =
    net_height + m6_sensor_first_height -
    m6_detector_body_margin_z - m6_detector_shell_bottom_lip_z;
m6_detector_mount_raise_z = max(
    20,
    net_panel_top_z + m6_detector_mount_net_clearance_z -
        m6_detector_raw_shell_bottom_z
);
m6_detector_raw_ballhead_base_bottom_z =
    m6_array_center_z - m6_ballhead_housing_length_x / 2 -
    m6_ballhead_base_t;
// The active cover split is along the optical x axis: front/optical x- and
// rear/cable x+. Keep the historical overlap parameter for manifest
// compatibility at zero: the removable covers never occupy the same solid
// volume. A small explicit parting clearance separates their outer profiles;
// the 0.25 mm assembly clearance belongs to their separate groove tongues.
m6_detector_shell_split_overlap_x = 0;
m6_detector_shell_split_clearance_x = 0.2;
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
m6_detector_shell_gasket_width = 3;
m6_detector_shell_gasket_height = 1.0;
m6_detector_shell_gasket_clearance = 0.25;
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
m6_detector_cable_exit_y = -22;
m6_detector_cable_gland_outer_d = 18;
m6_detector_cable_gland_length_z = 6;
m6_detector_cable_gland_wall_t = 3;
m6_detector_cable_trunk_y = -34;
m6_detector_cable_trunk_x = 772.25;
m6_detector_cable_trunk_width_x = 6;
m6_detector_cable_trunk_depth_y = 5;
m6_detector_cable_trunk_clearance_y = 1.2;
m6_detector_cable_branch_d = 4;
m6_detector_cable_clip_d = 7;
m6_detector_cable_clip_t = 3;
m6_detector_cable_clearance_enabled = true;
m6_detector_show_shell = true;
// Inspection-only overlay; it is opt-in and never belongs to printable STL.
m6_show_optical_direction = false;
m6_detector_shell_alpha = 0.48;
// The active body is deliberately only a rectangular PETG-printable bar.  The
// gimbal interface belongs to the rear PETG cover instead of becoming an
// integral T-tail.  The nominal envelope is kept material-neutral so the same
// geometry can later be machined from CNC stock or fitted with a metal insert.
m6_detector_body_material = "PETG";
// The boss is centered on the rear x face, not on the y side of the body.  A
// 3 mm x overlap fuses the boss to the rear cover while leaving 11 mm of
// material projecting toward the purchased ballhead.
m6_detector_shell_support_boss_length_x = 14;
m6_detector_shell_support_boss_overlap_x = 3;
m6_detector_shell_support_boss_depth_y = 18;
m6_detector_shell_support_boss_height_z = 36;
m6_detector_shell_support_boss_radius = 2;
// The rear-shell cavity removes the boss's central x-overlap.  These two
// y-side ribs are therefore added after that cavity subtraction: each rib
// bridges from the boss root to the rear shell wall without entering the
// central 1/4-20 bore.  They are PETG load-path material, not decoration.
m6_detector_shell_support_gusset_x_overlap = 0.2;
m6_detector_shell_support_gusset_root_width_y = 5;
m6_detector_shell_support_gusset_wall_width_y = 2.4;
m6_detector_shell_support_gusset_height_z = 12;
// 1/4-20 upper stud clearance; the captured 1/4 nut provides the actual
// thread.  This is intentionally smaller than the old M8 hole.
m6_detector_shell_support_hole_d = 7.0;
m6_detector_shell_support_hole_depth_x = 14;
m6_detector_shell_support_stud_engagement_x = 12;
m6_detector_detector_ballhead_gap_x = 2;
m6_detector_sensor_head_y_offset = 0;

// 旧版采购金属 90°连接器参数只为兼容历史诊断件保留。它不再进入当前
// 装配；当前固定网柱顶端是带中心 M8 攻丝底孔的平顶，M6 球头下端直接进入该孔。
m6_detector_net_connector_material = "purchased metal 90-degree connector";
m6_detector_net_connector_arm_width_y = 24;
m6_detector_net_connector_arm_t_z = 10;
m6_detector_net_connector_leg_width_y = 32;
m6_detector_net_connector_leg_t_x = 8;
m6_detector_net_connector_post_overlap_x = 2;
m6_detector_net_connector_socket_outer_d = 14;
m6_detector_net_connector_socket_clearance_d = 8.6;
m6_detector_net_connector_socket_overlap_z = 0.2;
m6_detector_net_connector_post_bolt_d = 6.5;
m6_detector_net_connector_post_bolt_y = m6_post_mount_hole_y;

// 当前固定网柱顶面是平顶直连面：球头 z- M8 进入顶面中心的 M8 攻丝底孔。
// 不做圆柱 boss、六角螺母窝、侧向承力耳或独立 90°连接器；球头金属件
// 的弯矩通过这一个平顶孔直接传入同一根 PETG/CNC 立柱。
m6_detector_direct_mount_arm_width_y = 0;
m6_detector_direct_mount_arm_t_z = 0;
// Compatibility echoes retained for older parameter consumers. The active
// fixed-net post has no horizontal seat/arm or side-return web; it is a
// one-piece upright from z=16 to the direct ballhead seating plane. The old
// slide/shoe experiment is disabled and contributes no current assembly geometry.
m6_detector_direct_mount_web_width_y = 0;
m6_detector_direct_mount_web_t_x = 0;
m6_detector_direct_mount_post_overlap_x = 2;
m6_detector_direct_mount_socket_outer_d = 24; // retained envelope for reports
// The printed/CNC pilot bore is the M8 tap drill. The larger value is retained
// as an assembly-mouth reference, not as a separate boss or counterbore.
m6_detector_direct_mount_socket_clearance_d = 8.6;
m6_detector_direct_mount_socket_tap_d = 6.8;
// These names remain as compatibility echoes for older reports. No boss or
// captured nut is part of the active geometry.
m6_detector_direct_mount_socket_base_overlap_z = 0;
m6_detector_direct_mount_nut_loading_clearance_z = 0;
m6_detector_direct_mount_socket_bottom_clearance_z = 0;
m6_detector_direct_mount_socket_top_clearance_z = 0;
m6_detector_direct_mount_thread_depth_extra_z = 2;

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
// 传感器夹座以网布上沿为唯一安装基准，右侧件靠近右立柱、左侧件镜像；
// 夹座外端到立柱内侧面保留 18 mm，避免与网架/立柱发生干涉。
sensor_post_clearance_x = 18;
sensor_x_fraction = 0.32; // 历史布局读取兼容值；当前坐标由 sensor_post_clearance_x 决定。
sensor_front_offset = 4;
sensor_film_clearance_y = 0.4;
sensor_clip_rear_wall_t_y = 3;
sensor_clip_bridge_t_z = 3;
sensor_clip_bottom_z = net_panel_top_z - sensor_height;
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
// 两条夹持舌头向球台内侧同步延长；压紧螺杆位于新增后的下舌头
// 有效台下区段的中点，而不是贴近舌头根部。
clamp_tongue_extra_length_x = 20;
// ITTF Technical Leaflet T2 给出的网柱水平部分台外上限为 160 mm。
// 固定灰色夹体的 x+ 外侧端面与立柱下段的宽端面齐平；因此这里直接
// 复用下段的 x 扩大量，避免灰色夹体再向外多出一截。实际外伸为 156 mm，
// 仍比台边外伸至少 130 mm，但不把过度外伸误写成常规商品网夹尺寸。
clamp_horizontal_part_outboard_limit = 160;
clamp_outboard_extension_min = 130;
// The fixed gray clamp's outboard face is flush with the broad lower post
// footprint.  Keep this as a literal first-article datum so the lightweight
// preview can mirror it; the source assertion below locks it to the lower
// post expansion. The upper post remains 28 mm wide and is not moved.
clamp_outer_extension = 3.5;
clamp_pad_depth = 58;
// 上、下两条结构夹臂统一加厚到 14 mm；上夹板内收纳互咬宽面滑道，
// 台面上侧胶皮由现场粘贴，
// 台底压块是独立的刚性圆盘，不把接触层厚度混入夹体承力厚度。
clamp_pad_t = 14;
// The net post is seated on the gray/yellow boundary.  Zero is intentional:
// the lower C-clamp body is a separate printable part and the post does not
// insert into it.
post_c_clamp_overlap_depth_z = 0;
post_interface_transition_bottom_width_x =
    post_body_width + 2 * post_interface_transition_extra_x;
post_interface_transition_bottom_depth_y = clamp_pad_depth;
clamp_clearance = 1.5;
clamp_screw_d = 8;
// 首样采用真实 M8×1.25 金属螺杆；螺纹牙型不在 PETG 几何中建模，
// 但螺距作为标准件接口的一部分固化并由参数探针/验证脚本读取。
clamp_screw_pitch = 1.25;
clamp_screw_bore_d = clamp_screw_d + 0.8;
// 82 mm 台下有效舌长的中点：螺杆中心距台边 41 mm。
clamp_screw_inset = 41;
// 外包络仍保持 Ø36 mm；用圆形齿凸做 18 齿圆角锯齿握持圈，谷底为 Ø30 mm。
// 这样手指有明确的抗滑着力点，但不改变旋钮与螺杆的安装包络。
clamp_knob_d = 36;
clamp_knob_grip_root_d = 30;
clamp_knob_grip_tooth_count = 18;
clamp_knob_grip_tooth_d = 5;
clamp_knob_grip_tooth_pitch_r =
    clamp_knob_d / 2 - clamp_knob_grip_tooth_d / 2;
// 两枚预先对锁的标准 M8 螺母把旋钮和螺杆刚性耦合；单枚旋钮螺母与
// 固定下臂螺母同时啮合会形成不明确的双螺纹约束，首样不采用那种路径。
clamp_knob_h = 20;
// 加厚下部承力段后，为标准 M8 丝杆和旋钮保留更长的操作/装配空间；上端
// 仍只顶在台底压块下方，实际标准件长度以首样台面厚度和旋钮净空复核。
clamp_screw_to_knob_top_base = 32;
clamp_screw_extra_length_z = 12;
clamp_screw_to_knob_top =
    clamp_screw_to_knob_top_base + clamp_screw_extra_length_z;
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
// Keep all post/C-clamp datums after the pad declarations: OpenSCAD evaluates
// assignments in source order and must not silently turn the seat into undef.
clamp_slide_seat_z = clamp_top_pad_t + clamp_pad_t;
post_bottom = clamp_slide_seat_z;
// The 30 mm transition starts exactly at the C-clamp's upper contact plane.
// The net fabric and U-clip still stop at net_panel_top_z = 168.5 mm. The
// upright then continues as one solid piece to the flat ballhead seating plane;
// the top is derived from the installed M8 base, not from a separate bridge.
post_interface_transition_start_z = clamp_slide_seat_z;
post_interface_transition_top_z =
    post_interface_transition_start_z + post_interface_transition_height_z;
post_interface_transition_outer_min_x =
    post_center_x - post_interface_transition_bottom_width_x / 2;
post_interface_transition_outer_max_x =
    post_center_x + post_interface_transition_bottom_width_x / 2;
post_interface_transition_outer_min_y =
    -post_interface_transition_bottom_depth_y / 2;
post_interface_transition_outer_max_y =
    post_interface_transition_bottom_depth_y / 2;
// Retained as a compatibility datum; no below-seat overlap is present in the
// active geometry.
post_lower_overlap_solid_height_z = 0;
// The former shoe/track experiment remains in the source only as a retired
// compatibility diagnostic. It is deliberately disabled for the current
// printable assembly; no shoe, rail, or hidden hardware is below this seat.
clamp_slide_interface_enabled = false;
clamp_slide_split_x = 885.5;
// Retired slide dimensions kept only for compatibility probes. They are not
// emitted by the active assembly while clamp_slide_interface_enabled=false.
clamp_slide_shoe_deepening_x = 8;
clamp_slide_receiver_length_x = 81;
clamp_slide_tongue_attach_x = 35.7;
// Retired shoe dimensions; no male shoe is emitted by the current assembly.
clamp_slide_length_x = 79.0;
clamp_slide_tongue_min_x = 849.5 - clamp_slide_shoe_deepening_x;
// Retired runner dimensions; the active post lands directly on the unchanged
// z=16 mm flat seat and has no lower continuation below that plane. The old
// shoe/crotch experiment is intentionally not part of the current print set.
// Keep the historical values only so old diagnostics can still parse them.
// Historical shoe-drop value; it is not used by the active assembly.
clamp_slide_shoe_drop_z = 14;
clamp_slide_rail_y_positions = [-18, 18];
// Retired runner section parameters. The active assembly has no shoe or
// female tunnel; these values remain only for old diagnostic callers.
clamp_slide_rail_y_depth = 16;
// Retired shoe dimensions; not part of the current one-piece post.
clamp_slide_rail_head_width_y = 20;
clamp_slide_rail_neck_width_y = 17.5;
clamp_slide_rail_head_height_z = 6.5;
clamp_slide_rail_neck_height_z = 5.5;
clamp_slide_rail_height_z =
    clamp_slide_rail_head_height_z + clamp_slide_rail_neck_height_z;
clamp_slide_rail_center_z = 9 - clamp_slide_shoe_drop_z;
clamp_slide_rail_floor_z =
    clamp_slide_rail_center_z - clamp_slide_rail_height_z / 2;
clamp_slide_clearance = 0.35;
// The side ankle cheeks descend through the complete 12 mm shoe section and
// bury a further 0.2 mm below its floor. This makes the lowered shoe and leg
// share one outside envelope without a visible lower ledge: the front (y-z)
// outline starts its continuous lower-wide-to-upper-narrow taper at the shoe
// underside, while the insertion-direction (x-z) root stays broad through the
// rail top for a positive load path.
clamp_slide_post_foot_shoe_buried_overlap_z = 0.2;
clamp_slide_post_foot_shoe_overlap_z =
    clamp_slide_rail_height_z +
    clamp_slide_post_foot_shoe_buried_overlap_z;
clamp_slide_receiver_floor_z =
    clamp_slide_rail_floor_z - clamp_slide_clearance;
clamp_slide_receiver_top_z =
    clamp_slide_rail_floor_z + clamp_slide_rail_height_z + clamp_slide_clearance;
// Keep the female tunnel roof clearance explicit: the receiver uses the same
// broad head as the male runner, then leaves one full clearance above the
// runner's narrow neck instead of relying on a coincident top face.
clamp_slide_receiver_neck_height_z =
    clamp_slide_receiver_top_z - clamp_slide_receiver_floor_z -
    (clamp_slide_rail_head_height_z + clamp_slide_clearance);
// The central crotch is a terminal tie inside the existing shoe
// envelope, not a rear extension beyond the two feet. It runs across the last
// 10 mm of the two shoes and sits below the net bottom datum, so it can overlap
// the post's x footprint without closing the 3 mm net route or colliding with
// the removable U clip above z=0.
clamp_slide_post_foot_root_max_x =
    post_center_x + post_body_width / 2 + 6.2;
clamp_slide_post_foot_cross_tie_length_x = 10;
// End the crotch web 0.8 mm before the shoe/root terminal face.  This keeps
// the web wholly embedded in the tapered ankle at its outboard end while
// avoiding an exact coplanar end edge where the ankle reaches the runner
// endpoint. It is still inside the shoes; it is not a rear extension.
clamp_slide_post_foot_bridge_max_x =
    clamp_slide_post_foot_root_max_x - 0.8;
clamp_slide_post_foot_bridge_min_x =
    clamp_slide_post_foot_bridge_max_x -
    clamp_slide_post_foot_cross_tie_length_x;
// The pants crotch sits at the upper end of the lower U-opening, just below
// the net bottom. It is a 3.2 mm thick transverse brace; the lower portions of
// both legs remain open down to the two shoes. This is the sketch's
// "裤裆连两只鞋", not a bar laid across the shoe floor.
clamp_slide_post_foot_cross_tie_height_z = 3.2;
// Legacy names remain as read-only probe aliases for old report consumers;
// active geometry uses the explicit y head/neck widths above.
clamp_slide_rail_base_width_z = clamp_slide_rail_height_z;
clamp_slide_rail_neck_width_z = clamp_slide_rail_neck_height_z;
clamp_slide_lock_x = clamp_slide_split_x - 8;
clamp_slide_lock_bore_d = 4.4;
clamp_slide_lock_bolt_d = 4;
clamp_slide_lock_bolt_length = 30;
clamp_slide_lock_nut_af = 7.2;
clamp_slide_lock_nut_h = 4.6;
// One central spring-ball detent is installed in the gray fixed body at the
// green reference location. The orange carrier's thick terminal tie has the
// matching underside pocket.
// There is deliberately no detent in either of the two structural runners:
// the wide captured shoulders carry load and the M4 retainers only stop slide-out.
// Keep the ball inside the thick central tie and within the fixed-body
// envelope. The dimple is centered in the tie, so the carrier is stopped by
// the pocket at the final x datum while the detent remains outside both
// load-bearing runners.
clamp_slide_detent_x =
    clamp_slide_post_foot_bridge_min_x +
    clamp_slide_post_foot_cross_tie_length_x / 2;
clamp_slide_detent_y_positions = [0];
clamp_slide_detent_y_count = len(clamp_slide_detent_y_positions);
clamp_slide_detent_y_center = clamp_slide_detent_y_positions[0];
clamp_slide_detent_ball_d = 4;
clamp_slide_detent_bore_d = 4.4;
clamp_slide_detent_bore_bottom_z =
    clamp_slide_rail_floor_z - 0.2;
clamp_slide_detent_bore_top_z =
    clamp_slide_seat_z + 0.8;
clamp_slide_detent_ball_offset_z = 0.95;
// Keep the single ball below the crotch roof, with its crown still captured
// by the shallow underside pocket. This assignment is kept before the later
// tie-top aliases to preserve OpenSCAD's source-order evaluation.
clamp_slide_detent_ball_center_z =
    net_passage_bottom_z - clamp_slide_clearance - 0.1 -
    clamp_slide_post_foot_cross_tie_height_z +
    clamp_slide_detent_ball_offset_z;
clamp_slide_detent_spring_d = 3;
// With the deeper shoe/ankle, the ball is intentionally lower in the tie
// pocket. Keep the short spring rooted close to the bore floor so it still
// has positive working height instead of floating above the ball.
clamp_slide_detent_spring_bottom_z =
    clamp_slide_detent_bore_bottom_z + 0.2;
clamp_slide_detent_spring_top_z =
    clamp_slide_detent_ball_center_z - clamp_slide_detent_ball_d / 2;
clamp_slide_detent_spring_h =
    clamp_slide_detent_spring_top_z - clamp_slide_detent_spring_bottom_z;
clamp_slide_detent_retainer_d = 5.5;
clamp_slide_detent_retainer_h = 1.5;
clamp_slide_detent_retainer_center_z =
    clamp_slide_detent_bore_bottom_z + clamp_slide_detent_retainer_h / 2;
clamp_slide_detent_dimple_d = 5.2;
// The pocket is cut from the raised crotch-web underside. It reaches above
// the 4 mm ball crown while leaving a small solid roof below the net datum.
clamp_slide_detent_dimple_depth_z = 3.2;
// Compatibility name: the active fixed-body detent opening ends at the flat
// seat, while the matching shallow pocket is cut into the carrier bridge.
clamp_slide_detent_female_roof_z = clamp_slide_seat_z;
// The post foot is a U-shaped shoe around the net passage. The root cheeks are
// deliberately 20 mm wide and start at the split shoulder, so the foot is
// already captured when the post first touches the fixed body. The cheeks are
// tapered x/z gussets, not rectangular collars: they stay broad through the
// shoe's whole captured section and then narrow into the nominal 28 mm
// upright. The low tie is inside the shoe end envelope and joins both legs
// without closing the net route through the upright.
clamp_slide_post_foot_side_clearance_y = 2;
// A 20 mm lower shoe is intentionally heavier than the 17.5 mm upper leg. The
// captured rail neck uses that same 17.5 mm thickness, so the front view sees
// one lower-wide-to-upper-narrow outline rather than a rail shoulder poking
// out as a left/right step.
clamp_slide_post_foot_root_width_y = 20;
clamp_slide_post_foot_side_inner_y =
    clamp_slide_rail_y_positions[1] -
    clamp_slide_post_foot_root_width_y / 2;
clamp_slide_post_foot_side_outer_y =
    clamp_slide_rail_y_positions[1] +
    clamp_slide_post_foot_root_width_y / 2;
// The lower shoe/ankle is wider in the front view; its upper end becomes
// exactly the two side walls of the existing post net passage.  The upper
// face is y=+/-1.5..+/-19.  The active rail neck is 17.5 mm wide, matching
// each upper side wall, while the lower shoe head is 20 mm wide.  Therefore
// the lower-to-upper change is one shallow captured shoulder followed by a
// single eased 3-D taper; there is no second rectangular collar or reverse
// step on either side.
clamp_slide_post_foot_transition_section_count = 96;
clamp_slide_post_foot_transition_slice_z = 0.4;
// The final loft envelope reaches the nominal post envelope to within a
// 0.02 mm printable fusion tolerance.  This is below normal first-layer/mesh
// resolution and is not a visible collar; it only keeps the two source solids
// from sharing a coplanar Boolean face at the fusion seam.  The overlap is
// supplied only in z, and the transition is already finished at post_bottom;
// the extra 0.25 mm above that plane is a buried fusion zone.  The net passage
// remains the exact 3 mm opening.
clamp_slide_post_foot_post_fusion_inset = 0.02;
clamp_slide_post_foot_side_top_inner_y =
    net_passage_width_y / 2 - clamp_slide_post_foot_post_fusion_inset;
clamp_slide_post_foot_side_top_outer_y =
    post_body_depth / 2 - clamp_slide_post_foot_post_fusion_inset;
// The two side cheeks are the extended ankles. They continue 8 mm from the
// historical split datum toward the tabletop interior; the old shoe/rail
// diagnostic remains outside the active formal carrier path.
clamp_slide_post_foot_ankle_inboard_extension_x = 8;
clamp_slide_post_foot_root_min_x =
    clamp_slide_split_x - clamp_slide_post_foot_ankle_inboard_extension_x;
// Fixed docking shelf under the upright.  The shelf extends just beyond the
// post's outboard face; the carrier's raw upper-jaw material starts after it
// so the final view shows the post sitting on the fixed clamp base, not on a
// duplicate platform travelling with the post.
clamp_slide_post_seat_clearance_x = 1;
clamp_slide_post_seat_end_x =
    post_center_x + post_body_width / 2 + clamp_outer_extension;
// This full-y member is the central "crotch" between the two long ankle
// cheeks. It stays inside the existing shoe end envelope and below the net
// bottom datum, joining both feet without adding a rear block or a wall across
// the net route. Its underside is the one place where the central spring-ball
// pocket is cut.
clamp_slide_post_foot_bottom_z =
    clamp_slide_rail_floor_z + clamp_slide_rail_height_z -
    clamp_slide_post_foot_shoe_overlap_z;
// 阶段1只把绿色示意理解成面向桌心的 x-z 截面：从现有立柱底面向下
// 拉出一块足够到脚底的原始料，再用同一截面的两条轮廓边削去多余材料。
// 这不是两条 y 向腿，也没有蓝色独立鞋、中央横梁或 C 形夹；最终实体是
// 一个沿 y 方向保持整深的 x-z 截面拉伸体。底高和下端 x 包络暂复用工作区
// 已有的脚底基准，只作为本阶段观察用尺寸，不改变正式立柱/C 形夹路径。
post_down_extension_stage1_bottom_z = clamp_slide_post_foot_bottom_z;
post_down_extension_stage1_top_z = post_bottom;
post_down_extension_stage1_height_z =
    post_down_extension_stage1_top_z - post_down_extension_stage1_bottom_z;
post_down_extension_stage1_depth_y = post_interface_transition_bottom_depth_y;
post_down_extension_stage1_profile_section_count = 32;
post_down_extension_stage1_green_transition_start_z =
    clamp_slide_rail_floor_z + clamp_slide_rail_height_z;
post_down_extension_stage1_top_min_x = post_interface_transition_outer_min_x;
post_down_extension_stage1_top_max_x = post_interface_transition_outer_max_x;
post_down_extension_stage1_bottom_min_x = clamp_slide_post_foot_root_min_x;
post_down_extension_stage1_bottom_max_x = clamp_slide_post_foot_root_max_x;
post_down_extension_stage1_raw_min_x =
    min(post_down_extension_stage1_top_min_x,
        post_down_extension_stage1_bottom_min_x);
post_down_extension_stage1_raw_max_x =
    max(post_down_extension_stage1_top_max_x,
        post_down_extension_stage1_bottom_max_x);

// 用户提供的 SKP 是同一个器件的四个组：Group#1 是上方立柱/接口参照，
// Group#2 是中间的连续 y-z 截面，Group#3/Group#4 是同一器件中 y 向对称的
// 两个 15 mm 腿脚延伸。这里只搬入 Group#2/3/4 作为当前“脚”候选件；
// Group#1 不重复生成，因为当前正式立柱仍由 post_body_positive() 管理。
// 所有数字均由 SKP 的 mm 坐标直接记录，不做缩放。Group#1 的参照立柱
// 在 SKP 中为 43.7 mm；它不是当前正式下端 35 mm 宽面的尺寸。
post_skp_leg_foot_reference_upright_width_x = 43.7;
post_skp_leg_foot_reference_lower_depth_y = 57;
post_skp_leg_foot_reference_interface_z = 20;
post_skp_leg_foot_main_length_x = 43.7;
post_skp_leg_foot_side_extension_x = 15;
post_skp_leg_foot_side_height_z = 7;
post_skp_leg_foot_lower_min_y_local = 10.5;
post_skp_leg_foot_lower_max_y_local = 46.5;
post_skp_leg_foot_profile_top_z = 20;
// The user's correction is an edge datum, not a center datum: the SKP lower
// main body must finish flush with the yellow lower transition and gray clamp
// outboard edge.  This puts the 43.7 mm Group#2 main length at x=874.8..918.5
// instead of leaving its right side 9.35 mm beyond the surrounding assembly.
post_skp_leg_foot_aligned_max_x = post_interface_transition_outer_max_x;
post_skp_leg_foot_origin_x =
    post_skp_leg_foot_aligned_max_x - post_skp_leg_foot_main_length_x;
post_skp_leg_foot_origin_y =
    -post_skp_leg_foot_reference_lower_depth_y / 2;
// SKP z=20 is the red bottom plane of the reference upright.  Keep that
// interface on the current post bottom datum and let the SKP lower geometry
// extend downward from it; this candidate is intentionally not fused to the
// formal post or tested against the C-clamp yet.
post_skp_leg_foot_origin_z =
    post_bottom - post_skp_leg_foot_reference_interface_z;
post_skp_leg_foot_min_x =
    post_skp_leg_foot_origin_x - post_skp_leg_foot_side_extension_x;
post_skp_leg_foot_max_x =
    post_skp_leg_foot_origin_x + post_skp_leg_foot_main_length_x;
// The lower Groups #2/#3/#4 occupy y=10.5..46.5; the wider y=0..57 envelope
// belongs to Group#1's lower transition and is intentionally not duplicated.
post_skp_leg_foot_min_y =
    post_skp_leg_foot_origin_y + post_skp_leg_foot_lower_min_y_local;
post_skp_leg_foot_max_y =
    post_skp_leg_foot_origin_y + post_skp_leg_foot_lower_max_y_local;
post_skp_leg_foot_bottom_z = post_skp_leg_foot_origin_z;
post_skp_leg_foot_top_z =
    post_skp_leg_foot_origin_z + post_skp_leg_foot_profile_top_z;
// The SKP terminal is a straight x=-15 mm end at this checkpoint.  Apply a
// simple 45-degree upper leading chamfer while leaving the z=0 support line
// intact.  Both distances are independent parameters so the next review can
// change the edge treatment without redrawing the SKP profile.
post_skp_leg_foot_terminal_chamfer_x = 3;
post_skp_leg_foot_terminal_chamfer_z = 3;
post_skp_leg_foot_exploded_offset_x = 75;
// Use the existing first-article slide clearance for the gray C-clamp
// candidate.  The extra z overlap belongs only to the subtractive tool: it
// makes the common yellow/green interface cut unambiguous without moving the
// visible yellow or green geometry.
post_skp_leg_foot_fit_clearance = clamp_slide_clearance;
post_skp_leg_foot_fit_cutter_overlap_z = 0.5;
// Keep the crotch below the net's z=0 lower edge with the same 0.35 mm
// display/print clearance. The main nominal post still seats flat at z=16 mm;
// the raised tie is only the shoe-to-shoe connector and detent carrier.
clamp_slide_post_foot_cross_tie_top_z =
    // Keep the top face below the net datum and off the loft's internal slice
    // planes.  The small extra 0.10 mm is not a fit datum; it only prevents a
    // coplanar boolean seam where the full-depth crotch intersects the two
    // continuous ankle solids.
    net_passage_bottom_z - clamp_slide_clearance - 0.1;
clamp_slide_post_foot_cross_tie_bottom_z =
    clamp_slide_post_foot_cross_tie_top_z -
    clamp_slide_post_foot_cross_tie_height_z;
// The crotch is a thick central bridge between the two legs, not a plate that
// crosses through the two load-bearing slide shoes. Its lower edge is wider
// so it bites into both leg roots; the upper edge narrows continuously into
// the open gap. Every section remains inside the rail head's inner faces,
// so the bridge cannot create a false rail seam or a coplanar step.
// Compatibility values for the retired narrow-tie diagnostic only.  The
// active crotch below uses the separate 16 mm half-width and is the sole
// cross-connection in the printable carrier.
clamp_slide_post_foot_cross_tie_bottom_half_y = 7.5;
clamp_slide_post_foot_cross_tie_top_half_y = 6.5;
// The actual one-piece crotch web overlaps each leg's inner edge.  Its
// half-width is intentionally larger than the local gap; otherwise the bar
// would merely touch the two shoes and remain a separate, unsafe island.
clamp_slide_post_foot_cross_tie_bridge_half_y = 16;
// The crotch web tapers to a narrow central-gap nose at both x ends before
// opening out into the two legs.  Its end caps therefore never terminate
// inside a leg volume; the two legs meet the web on its sloped side surfaces,
// which is both a cleaner solid and the intended pants-like load path.
clamp_slide_post_foot_cross_tie_end_bottom_half_y = 6.4;
clamp_slide_post_foot_cross_tie_end_top_half_y = 1.2;
clamp_slide_post_foot_cross_tie_blend_z = 0.35;
// The visible legs are derived from the shoe-floor lower edge to the flat
// post seat.  They terminate at the post's existing bottom profile instead of
// rising above it as an outer collar.  A small 0.2 mm overlap below/above the
// seat keeps the hull and post a single printable solid.
clamp_slide_post_foot_ankle_height_z =
    post_bottom - clamp_slide_post_foot_bottom_z;
// Keep the same external envelope as the upright, but carry the loft 0.25 mm
// into the post in z.  This is an internal fusion zone (not an outside collar)
// and gives the boolean a real volume overlap instead of a coincident seam.
clamp_slide_post_foot_root_overlap_z = 0.25;
clamp_slide_post_foot_top_z =
    post_bottom + clamp_slide_post_foot_root_overlap_z;
clamp_slide_post_foot_slope_top_min_x =
    post_center_x - post_body_width / 2 +
    clamp_slide_post_foot_post_fusion_inset;
clamp_slide_post_foot_slope_top_max_x =
    post_center_x + post_body_width / 2 -
    clamp_slide_post_foot_post_fusion_inset;
// Both visible side contours begin at the underside of the shoe and use the
// same eased loft.  There is no intermediate horizontal plateau or collar on
// either side of the pants-shaped foot.  The broad runners remain the separate
// full-length load-bearing shoes below this loft.
clamp_slide_post_foot_transition_start_z =
    clamp_slide_post_foot_bottom_z;
// In the insertion direction the pants envelope stays exactly over the two
// shoe footprints through the captured shoe height, then eases into the
// upright at the shoe roof.  The ease has zero slope at both ends, so this is
// a tangent transition, not a left/right step; the runner end is co-planar
// with the pants root rather than protruding by 0.2 mm.  The transition ends
// at the post's actual bottom plane; the small z overlap above it is constant
// post-sized material, not another stepped section.
clamp_slide_post_foot_transition_side_start_z =
    clamp_slide_rail_floor_z + clamp_slide_rail_height_z;
clamp_slide_post_foot_transition_end_z = post_bottom;
// 台底压块是独立的刚性小圆盘：上表面为平面，底面中央收纳 M8 圆头。
// 上方台面接触面不再作为打印件，现场在固定上夹板下表面粘贴胶皮即可。
clamp_pressure_pad_d = 50;
// 保留宽/深别名给旧版预览和参数读取器；实际外形以圆盘直径为准。
clamp_pressure_pad_width = 50;
clamp_pressure_pad_depth = 50;
clamp_pressure_pad_t = 4;
clamp_pressure_pad_screw_socket_d = clamp_screw_d + 1.2;
clamp_pressure_pad_screw_socket_depth = 2;
clamp_pressure_pad_screw_socket_mouth_d = 11;
clamp_pressure_pad_screw_socket_chamfer_h = 0.8;
post_top =
    m6_detector_raw_ballhead_base_bottom_z + m6_detector_mount_raise_z;
// The active upright is one continuous print from the gray/yellow seat to the
// installed ballhead base seating plane. The net passage and U-clip receiving
// channel end at the net top; the material above them remains a solid 28 x 38 mm
// support section with one central M8 tap pilot in its flat top.
net_post_top_z = post_top;
post_above_net_height_z = net_post_top_z - net_panel_top_z;
post_segment_count = 1;
// Compatibility echo for old readers.  A one-piece upright has no post seam.
post_joint_gap = 0;
// Diagnostic views separate otherwise coincident faces by this amount so the
// load path and the clearance are legible. It is never applied to printable
// assembly geometry.
preview_fit_display_gap = 0.1;
// Diagnostic slide-out distance: move the complete carrier just beyond the
// fixed body's outboard face, with 1 mm of readable air after the 81 mm
// receiver. This is only a view transform; the installed datum remains zero.
preview_slide_out_offset_x = clamp_slide_receiver_length_x + 1;
// Override only for the collision probe; the printable assembly always uses
// the zero installed datum.  This lets validation test the actual x-only
// insertion path at several positions without introducing a second part.
fit_probe_offset_x = 0;
// Retained as a compatibility datum for old diagnostics.  It is deliberately
// not used to split the active print; the complete upright remains one piece.
post_joint_above_net_clearance_z = 18;
// Legacy post-joint dimensions remain available only for old diagnostic PARTs.
// The active load path uses the clamp carrier's x-direction broad slideways instead.
post_joint_rail_height_z = 30;
post_joint_rail_root_overlap_z = 14;
post_joint_rail_x_base_width = 14;
post_joint_rail_x_neck_width = 9;
post_joint_rail_y_depth = 6;
post_joint_rail_y_positions = [-12, 12];
post_joint_rail_clearance = 0.35;
// Legacy sleeve/key dimensions remain available to old diagnostic PART calls;
// they are no longer part of the active assembly or print matrix.
post_joint_sleeve_h = 24;
post_joint_clearance = 0.6;
post_segment_index = 0;
post_total_height = post_top - post_bottom;
// post_segment_length/post_joint_z are assigned with the active one-piece
// height below, after the direct-mount datum has been resolved.
// 网布延伸到两侧立柱外边界；立柱实体保留连续过道，网布端部由 U 形卡夹
// 从桌外侧压在立柱外表面。这对应网布从网柱上端一直固定到下端的装配关系。
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
    m6_detector_shell_split_x - m6_detector_shell_split_clearance_x;
m6_detector_shell_rear_min_x =
    m6_detector_shell_split_x + m6_detector_shell_split_clearance_x;
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
// The rear cover carries the only current gimbal interface.  For the positive
// side (right receiver) the boss is centered on the x+ rear face at y=0 and
// extends outward in +x.  SIDE=-1 mirrors this complete interface to the left
// emitter's x- rear face, so its M8 axis still points toward the optical x+.
m6_detector_shell_support_boss_min_x =
    m6_detector_shell_max_x -
    m6_detector_shell_support_boss_overlap_x;
m6_detector_shell_support_boss_max_x =
    m6_detector_shell_support_boss_min_x +
    m6_detector_shell_support_boss_length_x;
m6_detector_shell_support_boss_min_y =
    m6_detector_body_center_y -
    m6_detector_shell_support_boss_depth_y / 2;
m6_detector_shell_support_boss_max_y =
    m6_detector_body_center_y +
    m6_detector_shell_support_boss_depth_y / 2;
m6_detector_shell_support_boss_center_x =
    (m6_detector_shell_support_boss_min_x +
     m6_detector_shell_support_boss_max_x) / 2;
m6_detector_shell_support_boss_center_y = m6_detector_body_center_y;
m6_detector_shell_support_boss_bottom_z =
    m6_detector_body_center_z -
    m6_detector_shell_support_boss_height_z / 2;
m6_detector_shell_support_boss_top_z =
    m6_detector_body_center_z +
    m6_detector_shell_support_boss_height_z / 2;
m6_detector_shell_support_boss_center_z = m6_detector_body_center_z;
m6_detector_shell_support_hole_entry_x =
    m6_detector_shell_support_boss_max_x;
m6_detector_shell_support_hole_center_x =
    m6_detector_shell_support_hole_entry_x -
    m6_detector_shell_support_hole_depth_x / 2;
m6_detector_shell_support_nut_pocket_center_x =
    m6_detector_shell_support_boss_min_x +
    m6_ballhead_top_nut_pocket_depth / 2;
m6_detector_shell_support_gusset_min_x =
    m6_detector_shell_support_boss_min_x -
    m6_detector_shell_support_gusset_x_overlap;
m6_detector_shell_support_gusset_max_x =
    m6_detector_shell_max_x +
    m6_detector_shell_support_gusset_x_overlap;
m6_detector_shell_support_gusset_root_y_start_positive =
    m6_detector_shell_support_boss_max_y -
    m6_detector_shell_support_gusset_root_width_y;
m6_detector_shell_support_gusset_wall_y_start_positive =
    m6_detector_shell_max_y -
    m6_detector_shell_support_gusset_wall_width_y;
m6_detector_shell_support_gusset_bottom_z =
    m6_detector_shell_support_boss_center_z -
    m6_detector_shell_support_gusset_height_z / 2;
m6_detector_shell_support_gusset_top_z =
    m6_detector_shell_support_boss_center_z +
    m6_detector_shell_support_gusset_height_z / 2;

m6_detector_ballhead_sensor_stud_center_x =
    m6_detector_shell_support_hole_entry_x +
    m6_ballhead_sensor_stud_length / 2 -
    m6_detector_shell_support_stud_engagement_x;
m6_detector_ballhead_center_x =
    m6_detector_shell_support_hole_entry_x +
    (m6_ballhead_sensor_stud_length -
     m6_detector_shell_support_stud_engagement_x) +
    m6_detector_detector_ballhead_gap_x +
    m6_ballhead_housing_d / 2;
// The raw detector package is kept internally coherent, then the complete
// detector/ballhead assembly is translated along x so the purchased
// ballhead's downward interface is directly above the net-post centre.  This
// removes the previous horizontal support arm while preserving the post's
// required outboard position and the 1830 mm net span.
m6_detector_mount_x_offset =
    post_center_x - m6_detector_ballhead_center_x;
m6_detector_assembly_ballhead_center_x =
    m6_detector_ballhead_center_x + m6_detector_mount_x_offset;
m6_detector_assembly_optical_axis_x =
    m6_detector_fit_thread_tip_x + m6_detector_mount_x_offset;
m6_detector_ballhead_center_y = m6_detector_shell_support_boss_center_y;
m6_detector_ballhead_center_z = m6_detector_body_center_z;
m6_detector_ballhead_base_center_z =
    m6_detector_ballhead_center_z - m6_ballhead_housing_length_x / 2 -
    m6_ballhead_base_t / 2;
m6_detector_ballhead_net_stud_center_z =
    m6_detector_ballhead_base_center_z - m6_ballhead_base_t / 2 -
    m6_ballhead_net_stud_length / 2;
m6_detector_ballhead_net_interface_bottom_z =
    m6_detector_ballhead_net_stud_center_z -
    m6_ballhead_net_stud_length / 2;
// Raw detector coordinates above remain reusable for standalone fit/coupon
// exports.  The installed detector + purchased ballhead is raised as one rigid
// group so the shell clears the net; all active direct-support z datums below
// therefore use these assembly aliases rather than silently mixing raw and
// installed coordinates.
m6_detector_assembly_ballhead_center_z =
    m6_detector_ballhead_center_z + m6_detector_mount_raise_z;
m6_detector_assembly_ballhead_base_center_z =
    m6_detector_ballhead_base_center_z + m6_detector_mount_raise_z;
m6_detector_assembly_ballhead_net_stud_center_z =
    m6_detector_ballhead_net_stud_center_z + m6_detector_mount_raise_z;
m6_detector_assembly_ballhead_net_interface_bottom_z =
    m6_detector_ballhead_net_interface_bottom_z +
    m6_detector_mount_raise_z;
m6_detector_net_connector_interface_height_z =
    m6_ballhead_net_stud_length;
m6_detector_net_connector_socket_bottom_z =
    m6_detector_ballhead_net_interface_bottom_z -
    m6_detector_net_connector_socket_overlap_z;
m6_detector_net_connector_socket_top_z =
    m6_detector_ballhead_net_interface_bottom_z +
    m6_detector_net_connector_interface_height_z +
    m6_detector_net_connector_socket_overlap_z;
m6_detector_net_connector_socket_height_z =
    m6_detector_net_connector_socket_top_z -
    m6_detector_net_connector_socket_bottom_z;
m6_detector_net_connector_socket_center_z =
    (m6_detector_net_connector_socket_bottom_z +
     m6_detector_net_connector_socket_top_z) / 2;
m6_detector_net_connector_arm_min_x =
    m6_detector_ballhead_center_x -
    m6_detector_net_connector_socket_outer_d / 2;
m6_detector_net_connector_post_inner_face_x =
    post_center_x - post_body_width / 2;
m6_detector_net_connector_arm_max_x =
    m6_detector_net_connector_post_inner_face_x +
    m6_detector_net_connector_post_overlap_x;
m6_detector_net_connector_arm_bottom_z =
    m6_detector_ballhead_net_interface_bottom_z;
m6_detector_net_connector_arm_top_z =
    m6_detector_ballhead_net_interface_bottom_z +
    m6_detector_net_connector_arm_t_z;
m6_detector_net_connector_leg_min_x =
    m6_detector_net_connector_post_inner_face_x -
    m6_detector_net_connector_leg_t_x +
    m6_detector_net_connector_post_overlap_x;
m6_detector_net_connector_leg_max_x =
    m6_detector_net_connector_arm_max_x;
m6_detector_net_connector_leg_bottom_z =
    m6_detector_ballhead_net_interface_bottom_z;
m6_detector_net_connector_leg_top_z =
    m6_post_mount_hole_z + m6_mount_slot_length / 2 + 4;
m6_detector_net_connector_leg_height_z =
    m6_detector_net_connector_leg_top_z -
    m6_detector_net_connector_leg_bottom_z;
m6_detector_net_connector_mount_height_z =
    m6_post_mount_hole_z -
    m6_detector_ballhead_net_interface_bottom_z;

// The 208 x 24 mm receiver carrier is installed vertically in the +y side of
// the M6 rear/cable cavity. Its component side points toward -x. The board
// datum is intentionally outside the 10 mm optical bar and behind the rear
// cover boss; the harness still exits through the y- gland/trunk.
m6_receiver_carrier_length_z = 208;
m6_receiver_carrier_width_y = 24;
m6_receiver_carrier_board_t_x = 1.6;
m6_receiver_carrier_board_x = m6_detector_shell_inner_max_x - 3.6;
m6_receiver_carrier_board_y = m6_detector_shell_inner_max_y - 1.5;
m6_receiver_carrier_board_z_min = m6_detector_body_bottom_z + 7;
m6_receiver_carrier_board_z_max =
    m6_receiver_carrier_board_z_min + m6_receiver_carrier_length_z;
m6_receiver_carrier_component_depth_x = 6.4;
m6_receiver_carrier_clearance_to_body_x =
    m6_receiver_carrier_board_x - m6_receiver_carrier_component_depth_x -
    m6_detector_body_max_x;

// The active direct M6-to-net-post interface is the flat top of the one-piece
// upright. The purchased downward M8 stud enters this central tap pilot; no
// separate gray/yellow bridge, round boss, hex nut pocket, or side ear is used.
m6_detector_direct_mount_enabled = true;
// Compatibility optical-interface datums are also the active post-top support
// datums. They are computed from the installed ballhead and the same post axis.
m6_detector_direct_mount_thread_tap_d =
    m6_detector_direct_mount_socket_tap_d;
m6_detector_direct_mount_thread_top_z =
    m6_detector_assembly_ballhead_base_center_z -
    m6_ballhead_base_t / 2;
m6_detector_direct_mount_thread_depth_z =
    m6_ballhead_net_stud_length +
    m6_detector_direct_mount_thread_depth_extra_z;
m6_detector_direct_mount_thread_bottom_z =
    m6_detector_direct_mount_thread_top_z -
    m6_detector_direct_mount_thread_depth_z;
m6_detector_direct_mount_socket_bottom_z =
    m6_detector_direct_mount_thread_bottom_z;
m6_detector_direct_mount_socket_top_z =
    m6_detector_direct_mount_thread_top_z;
m6_detector_direct_mount_socket_height_z =
    m6_detector_direct_mount_thread_depth_z;
m6_detector_direct_mount_socket_center_z =
    (m6_detector_direct_mount_socket_bottom_z +
     m6_detector_direct_mount_socket_top_z) / 2;
m6_detector_direct_mount_socket_center_x =
    m6_detector_assembly_ballhead_center_x;
// Legacy nut-loading aliases now describe the blind-hole datum only.  They are
// deliberately zero-depth so no hexagonal nut pocket is generated or implied.
m6_detector_direct_mount_nut_pocket_bottom_z =
    m6_detector_direct_mount_thread_bottom_z;
m6_detector_direct_mount_nut_pocket_center_z =
    m6_detector_direct_mount_thread_bottom_z;
m6_detector_direct_mount_nut_loading_depth_z = 0;
m6_detector_direct_mount_arm_min_x =
    m6_detector_direct_mount_socket_center_x;
m6_detector_direct_mount_post_inner_face_x =
    post_center_x - post_body_width / 2;
m6_detector_direct_mount_arm_max_x =
    m6_detector_direct_mount_socket_center_x;
m6_detector_direct_mount_arm_bottom_z =
    m6_detector_direct_mount_thread_top_z;
m6_detector_direct_mount_arm_top_z =
    m6_detector_direct_mount_arm_bottom_z;
// The compatibility alias names the actual fixed-net post top, which is the
// ballhead base seating plane.
m6_detector_direct_mount_lower_post_top_z =
    net_post_top_z;
// Legacy diagnostic echoes: zero-width/zero-height means no active side web.
m6_detector_direct_mount_web_min_x =
    m6_detector_direct_mount_post_inner_face_x;
m6_detector_direct_mount_web_max_x =
    m6_detector_direct_mount_post_inner_face_x;
m6_detector_direct_mount_web_min_z =
    m6_detector_direct_mount_lower_post_top_z;
m6_detector_direct_mount_web_max_z =
    m6_detector_direct_mount_lower_post_top_z;
// Active printable upright: one continuous body from the gray/yellow seat to
// the ballhead seating post_top datum. The same print also owns the outboard clamp
// carrier; the complete piece is seated against the separate gray C-clamp.
active_post_top_z = net_post_top_z;
active_post_total_height = active_post_top_z - post_bottom;
// Legacy readers now receive the actual continuous printable height, rather
// than a nominal envelope that includes the unused optical-clearance margin.
post_segment_length = active_post_total_height;
post_joint_z = active_post_top_z;
// Legacy split aliases are terminal sentinels, never active parting surfaces.
post_split_z = active_post_top_z;
post_lower_segment_z = post_bottom;
post_lower_segment_height = active_post_total_height;
post_upper_segment_z = active_post_top_z;
post_upper_segment_height = 0;
post_segment_zs = [post_bottom];
post_segment_heights = [active_post_total_height];
active_post_segment_length = active_post_total_height;
active_post_joint_z = active_post_top_z;
post_joint_rail_z0 = active_post_top_z;
post_joint_lock_z = active_post_top_z;
m4_joint_bolt_clearance_d = 4.4;
m4_joint_bolt_length = 40;
m4_joint_bolt_z_offset = 7;
sensor_x =
    post_center_x - post_body_width / 2 - sensor_post_clearance_x -
    sensor_length / 2;
clamp_tongue_reach_inboard =
    clamp_reach_inboard + clamp_tongue_extra_length_x;
clamp_pad_x = table_edge_x - clamp_tongue_reach_inboard;
clamp_pad_outer_x = post_center_x + post_body_width / 2 + clamp_outer_extension;
clamp_outboard_extension_actual = clamp_pad_outer_x - table_edge_x;
clamp_outer_wall_x = clamp_pad_outer_x - clamp_outer_wall_width;
// The fixed gray clamp owns the complete C-frame envelope through its
// outboard face. This is the mechanical reason the body can embrace the
// post/foot from the first contact instead of handing the wall to the orange
// carrier as a second, weakly connected block.
clamp_fixed_body_max_x = clamp_pad_outer_x;
// The female tunnels and the ankle/crotch reliefs are open through this face.
// There is intentionally no gray end wall at x+: the carrier must be able to
// enter from outside and travel along x before the central detent locates it.
clamp_slide_entry_open_x = clamp_fixed_body_max_x + clamp_slide_clearance;
// Upper and lower structural jaws share the same extended inboard datum.
clamp_lower_arm_x = clamp_pad_x;
clamp_screw_x = table_edge_x - clamp_screw_inset;
clamp_top_pad_x = clamp_pad_x + 8;
clamp_lower_arm_top_z = -table_thickness - clamp_lower_arm_clearance;
clamp_lower_arm_bottom_z = clamp_lower_arm_top_z - clamp_lower_arm_t;
clamp_pressure_pad_top_z = -table_thickness - clamp_clearance;
clamp_pressure_pad_bottom_z = clamp_pressure_pad_top_z - clamp_pressure_pad_t;
clamp_pressure_pad_x = clamp_screw_x - clamp_pressure_pad_width / 2;
clamp_reinforcement_start_x =
    table_edge_x - clamp_reinforcement_inboard_offset_x;
clamp_reinforcement_end_x = clamp_pad_outer_x - 0.2;
clamp_reinforcement_top_z = clamp_lower_arm_top_z;
clamp_reinforcement_near_table_bottom_z =
    clamp_reinforcement_top_z - clamp_reinforcement_near_table_thickness_z;
clamp_reinforcement_outer_thickness_z = clamp_lower_arm_t;
clamp_reinforcement_outer_bottom_z =
    clamp_reinforcement_top_z - clamp_reinforcement_outer_thickness_z;
// The electronics cavity ends before the clamp slide shoulder. The complete
// gray C-frame remains one fixed printable body; the orange carrier contributes
// only the one-piece upright, its full-length male runners and the heavy U-foot.
clamp_slide_lock_y_positions = clamp_slide_rail_y_positions;
function clamp_reinforcement_bottom_z_at(x) =
    clamp_reinforcement_near_table_bottom_z +
    (x - clamp_reinforcement_start_x) /
        (clamp_reinforcement_end_x - clamp_reinforcement_start_x) *
        (clamp_reinforcement_outer_bottom_z -
         clamp_reinforcement_near_table_bottom_z);
clamp_electronics_cavity_x_min =
    clamp_reinforcement_start_x + clamp_electronics_cavity_inboard_margin_x;
clamp_electronics_cavity_x_max =
    clamp_reinforcement_end_x - clamp_electronics_cavity_outboard_margin_x;
clamp_electronics_cavity_y_half =
    clamp_reinforcement_depth_y / 2 - clamp_electronics_cavity_wall_y;
clamp_electronics_cavity_top_z =
    clamp_reinforcement_top_z - clamp_electronics_cavity_roof_t;
clamp_electronics_cavity_length_x =
    clamp_electronics_cavity_x_max - clamp_electronics_cavity_x_min;
clamp_electronics_board_x_min =
    clamp_electronics_cavity_x_min +
    (clamp_electronics_cavity_length_x - clamp_electronics_board_length_x) / 2;
clamp_electronics_board_x_max =
    clamp_electronics_board_x_min + clamp_electronics_board_length_x;
clamp_electronics_battery_x_min =
    clamp_electronics_cavity_x_min +
    (clamp_electronics_cavity_length_x - clamp_electronics_battery_length_x) / 2;
clamp_electronics_battery_x_max =
    clamp_electronics_battery_x_min + clamp_electronics_battery_length_x;
clamp_electronics_board_bottom_z =
    clamp_electronics_cavity_top_z -
    clamp_electronics_board_top_clearance_z;
// Exact NPTH positions from esp32-control-v0.1.kicad_pcb, transformed from
// KiCad board coordinates (y=0..34) into the OpenSCAD assembly datum.  Using
// four individual pairs keeps every printed boss coaxial with a real hole;
// the old symmetric approximation was not sufficient for an interference
// claim.
clamp_electronics_board_hole_xy = [
    [clamp_electronics_board_x_min + 13.5,
     clamp_electronics_main_board_y_shift - 30.0],
    [clamp_electronics_board_x_min + 49.0,
     clamp_electronics_main_board_y_shift - 29.0],
    [clamp_electronics_board_x_min + 78.0,
     clamp_electronics_main_board_y_shift - 3.5],
    [clamp_electronics_board_x_min + 80.0,
     clamp_electronics_main_board_y_shift - 30.0]
];
clamp_electronics_ui_board_x_min =
    clamp_electronics_cavity_x_min +
    (clamp_electronics_cavity_length_x -
     clamp_electronics_ui_board_length_x) / 2;
clamp_electronics_ui_board_x_max =
    clamp_electronics_ui_board_x_min +
    clamp_electronics_ui_board_length_x;
clamp_electronics_ui_board_z =
    clamp_reinforcement_bottom_z_at(clamp_electronics_cavity_x_min) -
    clamp_electronics_cavity_cover_t -
    clamp_electronics_ui_board_t - 3;
clamp_electronics_ui_screen_x_min =
    clamp_electronics_ui_board_x_min +
    (clamp_electronics_ui_board_length_x -
     clamp_electronics_ui_screen_length_x) / 2;
clamp_electronics_ui_screen_x_max =
    clamp_electronics_ui_screen_x_min +
    clamp_electronics_ui_screen_length_x;
clamp_electronics_emitter_board_x_min =
    clamp_electronics_cavity_x_min +
    (clamp_electronics_cavity_length_x -
     clamp_electronics_emitter_board_length_x) / 2;
clamp_electronics_emitter_board_x_max =
    clamp_electronics_emitter_board_x_min +
    clamp_electronics_emitter_board_length_x;
clamp_electronics_emitter_battery_x_min =
    clamp_electronics_cavity_x_min +
    (clamp_electronics_cavity_length_x -
     clamp_electronics_emitter_battery_length_x) / 2;
clamp_electronics_emitter_battery_x_max =
    clamp_electronics_emitter_battery_x_min +
    clamp_electronics_emitter_battery_length_x;
clamp_electronics_emitter_board_bottom_z =
    clamp_electronics_cavity_top_z -
    clamp_electronics_board_top_clearance_z -
    clamp_electronics_emitter_board_t;
// 桌边外侧不再保留 C 形开口；从桌边外侧留出一个明确的小间隙后，
// 用沿 y 全深的实心桥体连接上下夹臂。桥体底部继续沿用 40→12 mm 斜底。
clamp_solid_bridge_start_x = table_edge_x + clamp_solid_bridge_clearance_x;
clamp_solid_bridge_top_z = clamp_top_pad_t + clamp_pad_t;
// The screw pushes into the shallow underside socket of the independent pad.
// Its rounded tip stops at the socket ceiling; it never passes through the pad
// or the tabletop. The socket surrounds the tip during clamping while leaving
// the printed pad removable from the metal screw when unloaded.
clamp_screw_top_z =
    clamp_pressure_pad_bottom_z + clamp_pressure_pad_screw_socket_depth;
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
       "legacy optical-post envelope must clear the highest optical module");
assert(post_segment_count == 1 && post_joint_gap == 0 &&
           post_bottom == clamp_slide_seat_z &&
           active_post_top_z == net_post_top_z &&
           active_post_total_height == net_post_top_z - post_bottom &&
           net_post_top_z == post_top &&
           net_post_top_z > net_panel_top_z &&
           active_post_segment_length == active_post_total_height &&
           post_segment_length == active_post_total_height &&
           post_lower_segment_z == post_bottom &&
           post_lower_segment_height == active_post_total_height &&
           post_upper_segment_z == active_post_top_z &&
           post_upper_segment_height == 0 &&
           post_split_z == active_post_top_z &&
           len(post_segment_zs) == 1 && len(post_segment_heights) == 1 &&
           post_segment_zs[0] == post_bottom &&
           post_segment_heights[0] == active_post_total_height,
       "the active upright must be one continuous printable piece with no post seam");
assert(!clamp_slide_interface_enabled ||
           (clamp_slide_receiver_length_x > clamp_slide_length_x &&
           clamp_slide_shoe_deepening_x >= 8 &&
           clamp_slide_shoe_drop_z >= 9 &&
           clamp_slide_rail_center_z == 9 - clamp_slide_shoe_drop_z &&
           clamp_slide_receiver_length_x ==
               73 + clamp_slide_shoe_deepening_x &&
           clamp_slide_length_x >=
               71 + clamp_slide_shoe_deepening_x &&
           clamp_slide_length_x > 60 &&
           clamp_slide_tongue_attach_x > 0 &&
           clamp_slide_tongue_min_x + clamp_slide_receiver_length_x ==
               clamp_fixed_body_max_x &&
           clamp_slide_tongue_min_x + clamp_slide_length_x <=
               clamp_slide_post_foot_root_max_x &&
           clamp_slide_post_foot_root_max_x -
               (clamp_slide_tongue_min_x + clamp_slide_length_x) <= 0.75 &&
           abs(clamp_slide_tongue_attach_x -
               (clamp_slide_post_foot_root_max_x - clamp_slide_split_x)) <
               0.001 &&
           clamp_slide_tongue_min_x < clamp_slide_split_x &&
           clamp_slide_split_x <
               clamp_slide_tongue_min_x + clamp_slide_length_x &&
           clamp_slide_rail_y_positions[0] < 0 &&
           clamp_slide_rail_y_positions[1] > 0 &&
           clamp_slide_rail_y_depth > 0 &&
           clamp_slide_rail_base_width_z > clamp_slide_rail_neck_width_z &&
           clamp_slide_rail_neck_width_z > 0 &&
           clamp_slide_rail_height_z > 0 &&
           clamp_slide_clearance > 0 &&
           clamp_slide_lock_x > clamp_slide_tongue_min_x &&
           clamp_slide_lock_x < clamp_slide_split_x &&
           clamp_slide_lock_bore_d > clamp_slide_lock_bolt_d &&
           clamp_slide_lock_bolt_length > 0 &&
           clamp_slide_lock_nut_af > clamp_slide_lock_bolt_d &&
           clamp_slide_detent_y_count == 1 &&
           clamp_slide_detent_y_center == 0 &&
           clamp_slide_detent_x > clamp_slide_lock_x &&
           clamp_slide_detent_x >= clamp_slide_post_foot_bridge_min_x &&
           clamp_slide_detent_x <= clamp_slide_post_foot_bridge_max_x &&
           clamp_slide_detent_x - clamp_slide_post_foot_bridge_min_x >=
               clamp_slide_detent_dimple_d / 2 &&
           clamp_slide_post_foot_bridge_max_x - clamp_slide_detent_x >=
               clamp_slide_detent_dimple_d / 2 &&
           clamp_slide_detent_x > post_interface_transition_outer_max_x &&
           clamp_slide_detent_x < clamp_fixed_body_max_x &&
           clamp_slide_detent_x >=
               clamp_slide_post_foot_bridge_min_x +
                   clamp_slide_detent_bore_d / 2 &&
           clamp_slide_detent_x <=
               clamp_slide_post_foot_bridge_max_x -
                   clamp_slide_detent_bore_d / 2 &&
           clamp_slide_post_foot_bridge_max_x -
               clamp_slide_post_foot_bridge_min_x >=
               clamp_slide_detent_bore_d &&
           clamp_slide_post_foot_cross_tie_length_x >= 10 &&
           clamp_slide_post_foot_cross_tie_height_z > 3 &&
           clamp_slide_post_foot_cross_tie_top_z ==
               net_passage_bottom_z - clamp_slide_clearance - 0.1 &&
           clamp_slide_post_foot_root_min_x >= clamp_slide_tongue_min_x &&
           clamp_slide_split_x - clamp_slide_post_foot_root_min_x ==
               clamp_slide_post_foot_ankle_inboard_extension_x &&
           clamp_slide_detent_bore_d > clamp_slide_detent_ball_d &&
           clamp_slide_detent_dimple_d >= clamp_slide_detent_ball_d &&
           clamp_slide_detent_dimple_depth_z > 0 &&
           clamp_slide_detent_spring_d < clamp_slide_detent_ball_d &&
           clamp_slide_detent_spring_h > 0 &&
           clamp_slide_detent_female_roof_z >
               clamp_slide_rail_center_z &&
           clamp_slide_detent_bore_top_z > clamp_slide_seat_z &&
           abs(clamp_slide_detent_ball_center_z -
               clamp_slide_post_foot_cross_tie_bottom_z -
               clamp_slide_detent_ball_offset_z) < 0.001 &&
           clamp_slide_post_foot_cross_tie_bottom_z <
               clamp_slide_rail_floor_z + clamp_slide_rail_height_z &&
           clamp_slide_post_foot_cross_tie_bottom_z +
               clamp_slide_detent_dimple_depth_z >=
               clamp_slide_detent_ball_center_z +
                   clamp_slide_detent_ball_d / 2 &&
           clamp_slide_detent_bore_top_z -
               clamp_slide_detent_ball_center_z >=
               clamp_slide_detent_ball_d / 2 &&
           clamp_slide_seat_z == clamp_solid_bridge_top_z &&
           post_bottom == clamp_slide_seat_z &&
           clamp_slide_seat_z >
               clamp_slide_rail_floor_z + clamp_slide_rail_height_z &&
           clamp_slide_post_foot_root_overlap_z > 0 &&
           clamp_slide_post_foot_top_z > post_bottom),
       "the clamp must have two full-length rooted broad slideways, one central detent and non-structural anti-slide M4 retainers");
assert(!clamp_slide_interface_enabled ||
           (clamp_fixed_body_max_x == clamp_pad_outer_x &&
           clamp_slide_entry_open_x >=
               clamp_fixed_body_max_x + clamp_slide_clearance &&
           clamp_slide_post_foot_root_max_x < clamp_fixed_body_max_x &&
           clamp_fixed_body_max_x - clamp_slide_post_foot_root_max_x >= 1.2 &&
           clamp_slide_post_seat_end_x == clamp_fixed_body_max_x &&
           clamp_slide_post_foot_root_width_y >= 18 &&
           clamp_slide_post_foot_side_inner_y > net_passage_width_y / 2 &&
           clamp_slide_post_foot_side_outer_y + clamp_slide_clearance <
               clamp_pad_depth / 2 &&
           clamp_slide_post_foot_side_top_inner_y ==
               net_passage_width_y / 2 -
               clamp_slide_post_foot_post_fusion_inset &&
           clamp_slide_post_foot_side_top_outer_y ==
               post_body_depth / 2 -
               clamp_slide_post_foot_post_fusion_inset &&
           clamp_slide_post_foot_side_top_inner_y <
               clamp_slide_post_foot_side_top_outer_y &&
           clamp_slide_post_foot_side_top_outer_y <
               clamp_slide_post_foot_side_outer_y &&
           clamp_slide_post_foot_transition_section_count >= 6 &&
           clamp_slide_post_foot_transition_slice_z > 0 &&
           clamp_slide_post_foot_transition_start_z ==
               clamp_slide_post_foot_bottom_z &&
           clamp_slide_post_foot_transition_start_z <
               clamp_slide_post_foot_top_z &&
           clamp_slide_post_foot_transition_side_start_z ==
               clamp_slide_rail_floor_z + clamp_slide_rail_height_z &&
           clamp_slide_post_foot_transition_side_start_z <
               clamp_slide_post_foot_top_z &&
           clamp_slide_post_foot_transition_end_z == post_bottom &&
           clamp_slide_post_foot_transition_side_start_z <
               clamp_slide_post_foot_transition_end_z &&
           clamp_slide_post_foot_bottom_z <
               clamp_slide_rail_floor_z + clamp_slide_rail_height_z &&
           clamp_slide_post_foot_shoe_overlap_z >= 10 &&
           clamp_slide_rail_floor_z + clamp_slide_rail_height_z -
               clamp_slide_post_foot_bottom_z ==
               clamp_slide_post_foot_shoe_overlap_z &&
           clamp_slide_post_foot_bridge_min_x >=
               clamp_slide_post_foot_root_min_x &&
           clamp_slide_post_foot_bridge_max_x <=
               clamp_slide_post_foot_root_max_x &&
           clamp_slide_post_foot_bridge_min_x <
               clamp_slide_post_foot_bridge_max_x &&
           clamp_slide_post_foot_cross_tie_top_z <
               net_passage_bottom_z &&
           clamp_slide_post_foot_cross_tie_bottom_z <
               clamp_slide_post_foot_cross_tie_top_z &&
           clamp_slide_post_foot_cross_tie_bottom_half_y >
               clamp_slide_post_foot_cross_tie_top_half_y &&
           clamp_slide_post_foot_cross_tie_top_half_y > 0 &&
           clamp_slide_post_foot_cross_tie_bottom_half_y <
               clamp_slide_rail_y_positions[1] -
               clamp_slide_rail_head_width_y / 2 &&
           clamp_slide_post_foot_slope_top_min_x ==
               post_center_x - post_body_width / 2 +
               clamp_slide_post_foot_post_fusion_inset &&
           clamp_slide_post_foot_slope_top_max_x ==
               post_center_x + post_body_width / 2 -
               clamp_slide_post_foot_post_fusion_inset &&
           clamp_slide_post_foot_slope_top_min_x <
               clamp_slide_post_foot_slope_top_max_x &&
           post_interface_transition_height_z == 0 &&
           post_interface_transition_outer_max_x ==
               post_center_x + post_body_width / 2 &&
           post_interface_transition_outer_max_x <
               net_clamp_channel_void_max_x &&
           net_clamp_clip_outer_x >
               post_interface_transition_outer_max_x),
       "the fixed gray body must own the full outboard envelope and the carrier shoe must embrace the post from first contact");
assert(!clamp_slide_interface_enabled &&
           post_bottom == clamp_slide_seat_z &&
           post_c_clamp_overlap_depth_z == 0 &&
           net_panel_top_z == clamp_slide_seat_z + net_height &&
           net_post_top_z == post_top &&
           net_post_top_z > net_panel_top_z &&
           post_interface_transition_start_z == clamp_slide_seat_z &&
           post_interface_transition_height_z == 30 &&
           post_interface_transition_top_z ==
               post_interface_transition_start_z + 30 &&
           post_interface_transition_top_z < post_top &&
           post_interface_transition_bottom_width_x ==
               post_body_width + 2 * post_interface_transition_extra_x &&
           post_interface_transition_bottom_depth_y == clamp_pad_depth &&
           post_interface_transition_outer_min_x <
               post_interface_transition_outer_max_x &&
           post_interface_transition_outer_min_y <
               post_interface_transition_outer_max_y &&
           post_interface_transition_outer_max_x == clamp_fixed_body_max_x &&
           post_interface_transition_outer_max_y <= clamp_pad_depth / 2 &&
           post_interface_transition_outer_min_y >= -clamp_pad_depth / 2,
       "the active net post must start on the gray/yellow C-clamp seat, keep the net channel at one net height, and continue as one solid tapered upright");
assert(!clamp_slide_interface_enabled ||
       (clamp_slide_tongue_attach_x >= 35.5 &&
           clamp_slide_rail_y_depth >= 16 &&
           clamp_slide_rail_head_width_y >= 16 &&
           clamp_slide_rail_neck_width_y >= 10 &&
           clamp_slide_rail_head_height_z >= 6.5 &&
           clamp_slide_rail_neck_height_z >= 5.5 &&
           clamp_slide_rail_height_z >= 12 &&
           clamp_slide_post_foot_ankle_height_z >= 20 &&
           clamp_slide_post_foot_ankle_height_z ==
               post_bottom - clamp_slide_post_foot_bottom_z &&
           clamp_slide_post_foot_root_overlap_z >= 0.2),
       "the retired clamp-slide shoe diagnostics must not constrain the active seated net post");
assert(post_segment_index >= 0 && post_segment_index < post_segment_count,
       "post_segment_index must select an existing printable upright segment");
assert(!m6_detector_direct_mount_enabled ||
       (m6_post_mount_clearance_d >= m6_stage_bolt_d &&
           m6_post_mount_hole_y + m6_post_mount_clearance_d / 2 <
               post_body_depth / 2 &&
           m6_post_mount_hole_y > m6_post_mount_clearance_d / 2 &&
           m6_post_mount_hole_z > post_bottom &&
           m6_post_mount_hole_z < post_top &&
           m6_post_mount_bolt_length >=
               m6_mount_plate_t + post_body_width + 8),
       "legacy M6 adapter-to-upright holes are only valid when an optical direct support is enabled");
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
           m6_ballhead_body_depth_y > 0 &&
           m6_ballhead_body_corner_radius > 0 &&
           m6_ballhead_body_corner_radius <
               min(m6_ballhead_housing_d,
                   m6_ballhead_body_depth_y) / 2 &&
           m6_ballhead_ball_socket_d > m6_ballhead_ball_d &&
           m6_ballhead_side_plate_d > m6_ballhead_ball_d &&
           m6_ballhead_side_plate_t_x > 0 &&
           m6_ballhead_lock_knob_d > 0 &&
           m6_ballhead_lock_knob_t_y > 0 &&
           m6_ballhead_lock_knob_ridge_count >= 12 &&
           m6_ballhead_base_d > m6_ballhead_ball_d &&
           m6_ballhead_sensor_stud_d > m6_ballhead_sensor_thread_core_d &&
           m6_ballhead_sensor_thread_core_d > 0 &&
           m6_ballhead_sensor_thread_pitch > 0 &&
           m6_ballhead_net_stud_d == 8 &&
           m6_ballhead_net_stud_d > m6_ballhead_net_thread_core_d &&
           m6_ballhead_net_thread_core_d > 0 &&
           m6_ballhead_net_thread_pitch > 0 &&
           m6_ballhead_sensor_stud_length > 0 &&
           m6_ballhead_net_stud_length > 0 &&
           m6_ballhead_top_nut_pocket_af > m6_ballhead_top_nut_af &&
           m6_ballhead_top_nut_pocket_depth >= m6_ballhead_top_nut_h &&
           m6_ballhead_top_nut_pocket_af / cos(30) <
               m6_detector_shell_support_boss_depth_y &&
           m6_ballhead_bottom_nut_pocket_af >
               m6_ballhead_bottom_nut_af &&
           m6_ballhead_bottom_nut_pocket_depth >=
               m6_ballhead_bottom_nut_h &&
           m6_ballhead_bottom_nut_pocket_af / cos(30) <
               m6_detector_direct_mount_socket_outer_d &&
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
           m6_detector_shell_front_max_x < m6_detector_shell_rear_min_x &&
           m6_detector_shell_width_y > m6_detector_body_depth_y &&
           m6_detector_shell_height_z > m6_detector_body_height_z &&
           m6_detector_shell_front_max_x ==
               m6_detector_shell_split_x -
                   m6_detector_shell_split_clearance_x &&
           m6_detector_shell_rear_min_x ==
               m6_detector_shell_split_x +
                   m6_detector_shell_split_clearance_x &&
           m6_detector_shell_split_clearance_x > 0 &&
           m6_detector_front_cap_length_x >
               m6_detector_shell_split_clearance_x &&
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
       "cover countersinks and cable-gland exit must fit the printable covers");
assert(m6_detector_body_length_x == 10 &&
           m6_detector_body_depth_y == 56 &&
           m6_detector_body_height_z == 216 &&
           m6_detector_shell_support_boss_length_x > 0 &&
           m6_detector_shell_support_boss_depth_y >
               2 * m6_detector_shell_clearance &&
           m6_detector_shell_support_boss_overlap_x > 0 &&
           m6_detector_shell_support_boss_height_z > 0 &&
           m6_detector_shell_support_boss_min_x <
               m6_detector_shell_max_x &&
           m6_detector_shell_support_boss_max_x >
               m6_detector_shell_max_x &&
           m6_detector_shell_support_boss_overlap_x ==
               m6_detector_shell_max_x -
                   m6_detector_shell_support_boss_min_x &&
           m6_detector_shell_support_boss_min_y >=
               m6_detector_shell_min_y &&
           m6_detector_shell_support_boss_max_y <=
               m6_detector_shell_max_y &&
           m6_detector_shell_support_boss_center_y ==
               m6_detector_body_center_y &&
           m6_detector_shell_support_boss_min_x >=
               m6_detector_shell_rear_min_x &&
           m6_detector_shell_support_boss_bottom_z <
               m6_detector_shell_support_boss_center_z &&
           m6_detector_shell_support_boss_top_z >
               m6_detector_shell_support_boss_center_z &&
           m6_detector_shell_support_boss_radius > 0 &&
           m6_detector_shell_support_boss_radius <
               min(m6_detector_shell_support_boss_depth_y,
                   m6_detector_shell_support_boss_height_z) / 2 &&
           m6_detector_shell_support_hole_d >
               m6_ballhead_sensor_stud_d &&
           m6_detector_shell_support_hole_depth_x <=
               m6_detector_shell_support_boss_length_x &&
           m6_detector_shell_support_hole_entry_x ==
               m6_detector_shell_support_boss_max_x &&
           m6_detector_shell_support_hole_depth_x > 0 &&
           m6_detector_shell_support_hole_depth_x <=
               m6_detector_shell_support_boss_length_x &&
           m6_detector_shell_support_hole_entry_x ==
               m6_detector_shell_support_boss_max_x &&
           m6_detector_shell_support_nut_pocket_center_x -
               m6_ballhead_top_nut_pocket_depth / 2 >=
               m6_detector_shell_support_boss_min_x &&
           m6_detector_shell_support_nut_pocket_center_x +
               m6_ballhead_top_nut_pocket_depth / 2 <=
               m6_detector_shell_support_boss_max_x &&
           m6_ballhead_top_nut_pocket_af / cos(30) <
               m6_detector_shell_support_boss_depth_y &&
           m6_detector_shell_support_gusset_x_overlap >= 0 &&
           m6_detector_shell_support_gusset_root_width_y > 0 &&
           m6_detector_shell_support_gusset_wall_width_y > 0 &&
           m6_detector_shell_support_gusset_height_z > 0 &&
           m6_detector_shell_support_gusset_min_x <
               m6_detector_shell_support_boss_min_x &&
           m6_detector_shell_support_gusset_max_x >
               m6_detector_shell_max_x &&
           m6_detector_shell_support_gusset_root_y_start_positive >
               m6_detector_shell_support_boss_center_y +
                   m6_detector_shell_support_hole_d / 2 + 0.05 &&
           m6_detector_shell_support_gusset_wall_y_start_positive <
               m6_detector_shell_max_y &&
           m6_detector_shell_support_gusset_bottom_z <
               m6_detector_shell_support_gusset_top_z &&
           m6_detector_shell_support_gusset_bottom_z >=
               m6_detector_shell_bottom_z &&
           m6_detector_shell_support_gusset_top_z <=
               m6_detector_shell_top_z,
       "rectangular PETG body and rear-cover 1/4-20 boss must form the current ballhead interface envelope");
assert(m6_detector_ballhead_center_y == m6_detector_body_center_y &&
           m6_detector_ballhead_center_z == m6_detector_body_center_z &&
           m6_detector_ballhead_base_center_z <
               m6_detector_ballhead_center_z &&
           m6_detector_ballhead_net_stud_center_z <
               m6_detector_ballhead_base_center_z &&
           m6_detector_ballhead_sensor_stud_center_x <
               m6_detector_shell_support_hole_entry_x &&
           m6_detector_ballhead_sensor_stud_center_x -
               m6_ballhead_sensor_stud_length / 2 <
               m6_detector_shell_support_hole_entry_x &&
           m6_detector_ballhead_sensor_stud_center_x +
               m6_ballhead_sensor_stud_length / 2 >
               m6_detector_shell_support_hole_entry_x -
                   m6_detector_shell_support_stud_engagement_x &&
           m6_detector_ballhead_center_x >
               m6_detector_ballhead_sensor_stud_center_x,
       "commercial 13 mm ballhead must remain vertical with a rear-cover x-axis 1/4-20 interface");
assert(!m6_detector_direct_mount_enabled ||
       (m6_detector_direct_mount_socket_center_x == post_center_x &&
           m6_detector_assembly_ballhead_center_x == post_center_x &&
           m6_detector_mount_x_offset > 0 &&
           m6_detector_mount_raise_z > 0 &&
           m6_detector_shell_bottom_z + m6_detector_mount_raise_z >
               net_height &&
           m6_detector_assembly_optical_axis_x > table_edge_x &&
           m6_detector_assembly_optical_axis_x < net_span / 2 &&
           m6_detector_direct_mount_arm_min_x == post_center_x &&
           m6_detector_direct_mount_arm_max_x == post_center_x &&
           m6_detector_direct_mount_arm_width_y == 0 &&
           m6_detector_direct_mount_arm_t_z == 0 &&
           m6_detector_direct_mount_socket_outer_d <= post_body_width &&
           m6_detector_direct_mount_thread_tap_d >
               m6_ballhead_net_thread_core_d &&
           m6_detector_direct_mount_thread_tap_d <
               m6_ballhead_net_stud_d &&
           m6_detector_direct_mount_thread_top_z ==
               m6_detector_assembly_ballhead_base_center_z -
                   m6_ballhead_base_t / 2 &&
           m6_detector_direct_mount_socket_top_z ==
               m6_detector_direct_mount_thread_top_z &&
           m6_detector_direct_mount_socket_bottom_z ==
               m6_detector_direct_mount_thread_bottom_z &&
           m6_detector_direct_mount_thread_depth_z ==
               m6_ballhead_net_stud_length +
                   m6_detector_direct_mount_thread_depth_extra_z &&
           m6_detector_direct_mount_thread_depth_z >=
               m6_ballhead_net_stud_length + 1 &&
           m6_detector_direct_mount_socket_height_z ==
               m6_detector_direct_mount_thread_depth_z &&
           m6_detector_direct_mount_socket_bottom_z <
               m6_detector_direct_mount_socket_top_z &&
           m6_detector_direct_mount_arm_bottom_z ==
               m6_detector_direct_mount_thread_top_z &&
           m6_detector_direct_mount_arm_top_z ==
               m6_detector_direct_mount_arm_bottom_z &&
           m6_detector_direct_mount_lower_post_top_z ==
               m6_detector_direct_mount_thread_top_z &&
           m6_detector_direct_mount_lower_post_top_z > post_bottom &&
           m6_detector_direct_mount_lower_post_top_z - post_bottom < 270 &&
           m6_detector_direct_mount_nut_loading_depth_z == 0 &&
           m6_detector_direct_mount_nut_pocket_bottom_z ==
               m6_detector_direct_mount_thread_bottom_z &&
           m6_detector_direct_mount_nut_pocket_center_z ==
               m6_detector_direct_mount_thread_bottom_z &&
           m6_detector_direct_mount_socket_base_overlap_z == 0 &&
           m6_detector_direct_mount_nut_loading_clearance_z == 0 &&
           m6_detector_direct_mount_web_width_y == 0 &&
           m6_detector_direct_mount_web_t_x == 0),
       "the optional M6 direct-mount datum is internally consistent when explicitly enabled");
assert(m6_detector_direct_mount_enabled &&
           m6_detector_direct_mount_lower_post_top_z == net_post_top_z &&
           active_post_top_z == net_post_top_z &&
           active_post_total_height == net_post_top_z - post_bottom &&
           net_post_top_z > net_panel_top_z &&
           m6_detector_direct_mount_socket_top_z == net_post_top_z &&
           m6_detector_direct_mount_socket_top_z == post_top &&
           m6_detector_shell_bottom_z + m6_detector_mount_raise_z >=
               net_panel_top_z + m6_detector_mount_net_clearance_z &&
           m6_detector_direct_mount_socket_bottom_z <
               m6_detector_direct_mount_socket_top_z,
       "the one-piece fixed-net post must end at the flat ballhead seating plane and carry the central M8 tap pilot");
assert(net_clamp_channel_depth_x > net_clamp_channel_back_wall_t_x &&
           net_clamp_cylinder_insertion_depth_x == net_clamp_channel_depth_x &&
           net_clamp_channel_back_wall_t_x > 0 &&
           net_clamp_channel_back_wall_t_x < net_clamp_channel_depth_x &&
           net_clamp_cylinder_interference_d >
               net_clamp_cylinder_actual_d &&
           net_clamp_cylinder_actual_d ==
               net_clamp_cylinder_interference_d - 2 &&
           net_clamp_channel_width_y > 2 * net_clamp_clip_outer_half_y &&
           net_clamp_channel_void_min_x ==
               post_center_x + post_body_width / 2 -
                   net_clamp_channel_depth_x +
                   net_clamp_channel_back_wall_t_x &&
           net_clamp_channel_void_max_x >
               post_interface_transition_outer_max_x &&
           net_fixture_bottom_z == post_bottom &&
           net_clamp_channel_bottom_z == net_fixture_bottom_z &&
           net_clamp_channel_top_z == net_panel_top_z &&
           net_clamp_cylinder_height ==
               net_clamp_channel_top_z - net_clamp_channel_bottom_z &&
           net_clamp_clip_length_x > 15 &&
           net_clamp_clip_inner_x > net_clamp_channel_void_min_x &&
           net_clamp_clip_outer_x >
               post_interface_transition_outer_max_x &&
           net_clamp_clip_outer_x < net_clamp_channel_void_max_x &&
           net_clamp_clip_jaw_gap_y > net_sheet_t &&
           net_clamp_clip_jaw_t_y > 1 &&
           net_clamp_clip_crossbar_t_x > 2 &&
           net_clamp_keeper_enabled &&
           net_clamp_keeper_height_z >= 6 &&
           net_clamp_keeper_x_min > net_clamp_clip_inner_x &&
           net_clamp_keeper_x_max > net_clamp_keeper_x_min &&
           net_clamp_keeper_x_max < net_clamp_keeper_relief_max_x &&
           net_clamp_keeper_y_min > net_clamp_clip_jaw_center_y &&
           net_clamp_keeper_y_min <
               net_clamp_clip_jaw_center_y + net_clamp_clip_jaw_t_y / 2 &&
           net_clamp_keeper_y_max > net_clamp_channel_width_y / 2 &&
           net_clamp_keeper_z > net_clamp_channel_bottom_z &&
           net_clamp_keeper_z + net_clamp_keeper_height_z <
               net_clamp_channel_top_z &&
           net_clamp_keeper_relief_min_x < net_clamp_clip_inner_x &&
           net_clamp_keeper_relief_max_x > net_clamp_keeper_x_max &&
           net_clamp_keeper_relief_min_y < net_clamp_clip_outer_half_y &&
           net_clamp_keeper_relief_max_y > net_clamp_clip_outer_half_y &&
           net_clamp_keeper_latch_x_min >= net_clamp_keeper_relief_min_x &&
           net_clamp_keeper_latch_x_max < net_clamp_keeper_x_min &&
           net_clamp_keeper_x_min - net_clamp_keeper_latch_x_max >= 0.2 &&
           net_clamp_keeper_latch_y_min < net_clamp_keeper_y_min &&
           net_clamp_keeper_latch_y_max > net_clamp_keeper_y_min &&
           net_clamp_keeper_latch_y_max <= net_clamp_keeper_relief_max_y &&
           net_clamp_keeper_latch_z >= net_clamp_keeper_z &&
           net_clamp_keeper_latch_z + net_clamp_keeper_latch_height_z <=
               net_clamp_keeper_z + net_clamp_keeper_height_z &&
           net_clamp_channel_outboard_extension_x >=
               net_clamp_clip_crossbar_t_x + net_clamp_clip_clearance_x &&
           m6_detector_direct_mount_lower_post_top_z >=
               net_clamp_channel_top_z,
       "outboard net pocket must accept a full-height sliding U clip with a net-sized jaw gap and one passive embedded anti-withdrawal keeper");
assert(net_passage_width_y == 3 &&
           net_passage_width_y > net_sheet_t &&
           net_passage_side_clearance_y > 0 &&
           net_passage_min_x <
               post_center_x - post_body_width / 2 &&
           net_passage_max_x >
               post_center_x + post_body_width / 2 &&
           net_passage_min_x < net_passage_max_x &&
           net_passage_bottom_z == net_fixture_bottom_z &&
           net_passage_top_z == net_panel_top_z &&
           net_passage_top_z > net_passage_bottom_z &&
           net_passage_top_z <=
               m6_detector_direct_mount_lower_post_top_z,
       "net must have a 3 mm y-direction passage through the complete post envelope");
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
assert(post_top ==
           m6_detector_raw_ballhead_base_bottom_z +
               m6_detector_mount_raise_z &&
           m6_detector_shell_bottom_z + m6_detector_mount_raise_z >=
               net_panel_top_z + m6_detector_mount_net_clearance_z,
       "upright top must follow the ballhead base axis while the raised M6 shell clears the net");
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
       "the net span must reach the two standard outboard post limits");
assert(net_top_rail_required == 0 &&
           net_panel_bottom_z == net_fixture_bottom_z &&
           net_panel_top_z == net_fixture_bottom_z + net_height,
       "the active net must use the cloth top edge directly from the fixed seat; no top rail is allowed");
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
assert(clamp_outer_extension == post_interface_transition_extra_x,
       "the fixed gray clamp outboard face must align with the broad lower post footprint");
assert(clamp_tongue_extra_length_x > 0 &&
           clamp_tongue_reach_inboard ==
               clamp_reach_inboard + clamp_tongue_extra_length_x &&
           clamp_tongue_reach_inboard > clamp_reach_inboard &&
           clamp_lower_arm_x == clamp_pad_x &&
           abs(clamp_screw_x - (clamp_pad_x + table_edge_x) / 2) < 0.01 &&
           abs(clamp_screw_inset - clamp_tongue_reach_inboard / 2) < 0.01,
       "upper/lower clamp tongues must share the extended datum and center the pressure hardware on the lower tongue");
assert(clamp_reinforcement_inboard_offset_x > 0 &&
           clamp_reinforcement_near_table_thickness_z == 40 &&
           clamp_reinforcement_depth_y == clamp_pad_depth &&
           clamp_solid_bridge_clearance_x > 0 &&
           clamp_solid_bridge_start_x ==
               table_edge_x + clamp_solid_bridge_clearance_x &&
           clamp_solid_bridge_start_x > table_edge_x &&
           clamp_solid_bridge_start_x < clamp_reinforcement_end_x &&
           clamp_solid_bridge_top_z == clamp_top_pad_t + clamp_pad_t &&
           clamp_solid_bridge_top_z > clamp_reinforcement_top_z &&
           clamp_reinforcement_start_x < table_edge_x &&
           clamp_reinforcement_start_x > clamp_pressure_pad_x +
               clamp_pressure_pad_width / 2 &&
           clamp_reinforcement_end_x > clamp_reinforcement_start_x &&
           clamp_reinforcement_end_x > clamp_outer_wall_x &&
           clamp_reinforcement_top_z == clamp_lower_arm_top_z &&
           clamp_reinforcement_near_table_bottom_z ==
               clamp_reinforcement_top_z -
               clamp_reinforcement_near_table_thickness_z &&
           clamp_reinforcement_outer_thickness_z == clamp_lower_arm_t &&
           clamp_reinforcement_outer_bottom_z ==
               clamp_reinforcement_top_z -
               clamp_reinforcement_outer_thickness_z &&
           clamp_reinforcement_near_table_bottom_z <
               clamp_reinforcement_outer_bottom_z &&
           clamp_reinforcement_outer_bottom_z <
               clamp_reinforcement_top_z,
       "solid tapered under-clamp reinforcement/bridge must be full-depth, clear of the pad, and 40-to-12 mm");
assert(clamp_electronics_cavity_x_min > clamp_screw_x &&
           clamp_electronics_cavity_x_min >
               clamp_pressure_pad_x + clamp_pressure_pad_width / 2 &&
           clamp_electronics_cavity_x_max < clamp_reinforcement_end_x &&
           clamp_electronics_cavity_x_max > clamp_electronics_cavity_x_min &&
           clamp_electronics_cavity_length_x > clamp_electronics_board_length_x &&
           clamp_electronics_cavity_y_half > clamp_electronics_board_width_y / 2 &&
           clamp_electronics_cavity_y_half > clamp_electronics_battery_width_y / 2 &&
           clamp_electronics_cavity_top_z < clamp_reinforcement_top_z &&
           clamp_electronics_cavity_roof_t >= 4 &&
           clamp_electronics_cavity_y_half + 3 +
               clamp_electronics_mount_boss_d / 2 <
                   clamp_reinforcement_depth_y / 2 &&
           clamp_electronics_cavity_top_z -
               clamp_reinforcement_bottom_z_at(clamp_electronics_cavity_x_max) > 10,
       "electronics cavity must clear the M8 load path, fit the board/battery, and retain roof/side structure");
assert(clamp_electronics_battery_x_min > clamp_electronics_cavity_x_min &&
           clamp_electronics_battery_x_max < clamp_electronics_cavity_x_max &&
           clamp_electronics_board_x_min > clamp_electronics_cavity_x_min &&
           clamp_electronics_board_x_max < clamp_electronics_cavity_x_max,
       "electronics envelopes must remain inside the tapered cavity");
assert(clamp_electronics_board_bottom_z >
           clamp_reinforcement_bottom_z_at(clamp_electronics_board_x_min) &&
           clamp_electronics_board_bottom_z >
               clamp_reinforcement_bottom_z_at(clamp_electronics_board_x_max) &&
           abs(clamp_electronics_cavity_top_z -
               clamp_electronics_board_bottom_z -
               clamp_electronics_board_top_clearance_z) < 0.001 &&
           clamp_electronics_board_top_clearance_z >=
               clamp_electronics_component_height_z +
               clamp_electronics_component_clearance_z &&
           clamp_electronics_ui_board_length_x <
               clamp_electronics_cavity_length_x &&
           clamp_electronics_ui_board_width_y <
               2 * clamp_electronics_cavity_y_half &&
           clamp_electronics_emitter_board_length_x <
               clamp_electronics_cavity_length_x &&
           clamp_electronics_emitter_board_width_y <
               2 * clamp_electronics_cavity_y_half &&
           clamp_electronics_emitter_board_width_y -
               clamp_electronics_emitter_battery_width_y >= 2 &&
           clamp_electronics_battery_rail_clearance_y > 0 &&
           clamp_electronics_battery_width_y / 2 +
               clamp_electronics_battery_rail_clearance_y +
               clamp_electronics_battery_rail_t / 2 <
               clamp_electronics_cavity_y_half &&
           clamp_electronics_gasket_width > 0 &&
           clamp_electronics_gasket_height > 0 &&
           clamp_electronics_cover_lip_h > 0,
       "board planes, emitter daughter, UI panel, rails and continuous seal must fit the cavity");
assert(m6_receiver_carrier_board_x -
           m6_receiver_carrier_component_depth_x > m6_detector_body_max_x &&
           m6_receiver_carrier_board_x < m6_detector_shell_max_x &&
           m6_receiver_carrier_board_y - m6_receiver_carrier_width_y >=
               m6_detector_shell_inner_min_y + 1.5 &&
           m6_receiver_carrier_board_y <=
               m6_detector_shell_inner_max_y - 1.5 &&
           m6_receiver_carrier_board_z_min > m6_detector_shell_bottom_z &&
           m6_receiver_carrier_board_z_max < m6_detector_shell_top_z,
       "vertical receiver carrier must clear the optical bar and remain inside the M6 shell");
assert(abs(m6_detector_cable_exit_y) +
           m6_detector_cable_exit_d / 2 +
           m6_detector_cable_exit_sleeve_clearance <
               m6_detector_shell_width_y / 2 + m6_detector_shell_wall &&
           m6_detector_cable_trunk_y <
               m6_detector_shell_min_y -
               m6_detector_cable_trunk_clearance_y &&
           m6_detector_cable_gland_outer_d >=
               m6_detector_cable_exit_d +
               2 * m6_detector_cable_gland_wall_t &&
           m6_detector_shell_gasket_width > 0 &&
           m6_detector_shell_gasket_height > 0,
       "M6 cable gland/trunk must clear the shell and retain a continuous cover gasket reference");
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
assert(clamp_pressure_pad_d == clamp_pressure_pad_width &&
           clamp_pressure_pad_d == clamp_pressure_pad_depth &&
           clamp_pressure_pad_d > clamp_screw_d + 2 * clamp_clearance &&
           clamp_pressure_pad_t > clamp_pressure_pad_screw_socket_depth &&
           clamp_pressure_pad_screw_socket_d > clamp_screw_d &&
           clamp_pressure_pad_screw_socket_d < clamp_pressure_pad_d &&
           clamp_pressure_pad_screw_socket_mouth_d >=
               clamp_pressure_pad_screw_socket_d &&
           clamp_pressure_pad_screw_socket_chamfer_h > 0 &&
           clamp_pressure_pad_screw_socket_chamfer_h <
               clamp_pressure_pad_screw_socket_depth,
       "round pressure pad must have a flat top and a printable underside screw socket");
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
assert(clamp_pad_t == 14 && clamp_lower_arm_t == clamp_pad_t,
       "upper and lower structural clamp jaws must both be 14 mm thick");
assert(clamp_screw_top_z > clamp_pressure_pad_bottom_z &&
           clamp_screw_top_z <=
               clamp_pressure_pad_bottom_z +
               clamp_pressure_pad_screw_socket_depth + 0.01 &&
           clamp_screw_top_z < -table_thickness &&
           clamp_screw_tip_radius > 0,
       "rounded M8 screw tip must seat in the pad underside socket below the tabletop");
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
assert(clamp_knob_grip_root_d > clamp_screw_bore_d &&
           clamp_knob_grip_root_d < clamp_knob_d &&
           clamp_knob_grip_tooth_count >= 12 &&
           clamp_knob_grip_tooth_d > 0 &&
           clamp_knob_grip_tooth_pitch_r > clamp_knob_grip_root_d / 2 &&
           clamp_knob_grip_tooth_pitch_r - clamp_knob_grip_tooth_d / 2 <
               clamp_knob_grip_root_d / 2 &&
           clamp_knob_grip_tooth_pitch_r + clamp_knob_grip_tooth_d / 2 ==
               clamp_knob_d / 2,
       "hand knob must have an overlapping, rounded anti-slip tooth ring");
assert(sensor_count == 2 && sensor_x > sensor_length / 2 &&
           sensor_x + sensor_length / 2 < net_span / 2 &&
           abs((post_center_x - post_body_width / 2) -
               (sensor_x + sensor_length / 2) - sensor_post_clearance_x) < 0.01,
       "two PVDF mounts must sit near the net ends while clearing both posts");
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
assert(post_down_extension_stage1_bottom_z <
           post_down_extension_stage1_green_transition_start_z &&
           post_down_extension_stage1_green_transition_start_z <
           post_down_extension_stage1_top_z,
       "stage-1 green x-z transition must stay between the foot bottom and post bottom");
assert(post_down_extension_stage1_profile_section_count >= 4 &&
           post_down_extension_stage1_depth_y > 0 &&
           post_down_extension_stage1_height_z > 0 &&
           post_down_extension_stage1_bottom_min_x <
               post_down_extension_stage1_bottom_max_x &&
           post_down_extension_stage1_top_min_x <
               post_down_extension_stage1_top_max_x,
       "stage-1 downward extension profile must have positive printable dimensions");
assert(post_skp_leg_foot_reference_upright_width_x > 0 &&
           post_skp_leg_foot_reference_lower_depth_y > 0 &&
           post_skp_leg_foot_reference_interface_z > 0 &&
           post_skp_leg_foot_main_length_x > 0 &&
           post_skp_leg_foot_side_extension_x > 0 &&
           post_skp_leg_foot_side_height_z > 0 &&
           post_skp_leg_foot_lower_min_y_local <
               post_skp_leg_foot_lower_max_y_local &&
           post_skp_leg_foot_terminal_chamfer_x > 0 &&
           post_skp_leg_foot_terminal_chamfer_x <
               post_skp_leg_foot_side_extension_x &&
           post_skp_leg_foot_terminal_chamfer_z > 0 &&
           post_skp_leg_foot_terminal_chamfer_z <
               post_skp_leg_foot_side_height_z &&
           post_skp_leg_foot_max_x == post_skp_leg_foot_aligned_max_x &&
           post_skp_leg_foot_fit_clearance > 0 &&
           post_skp_leg_foot_fit_cutter_overlap_z > 0 &&
           post_skp_leg_foot_min_x < post_skp_leg_foot_max_x &&
           post_skp_leg_foot_min_y < post_skp_leg_foot_max_y &&
           post_skp_leg_foot_bottom_z < post_skp_leg_foot_top_z,
       "SKP leg/foot dimensions and terminal chamfer must be positive");

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

module clamp_solid_tapered_reinforcement_positive() {
    // Full-depth solid lower support below the tabletop clamp opening. The
    // inboard/table-near x- end is 40 mm thick; the outboard x+ end follows
    // the thickened 12 mm lower structural jaw with a sloped underside.
    color("slategray")
        rotate([90, 0, 0])
            linear_extrude(height = clamp_reinforcement_depth_y,
                           center = true)
                polygon(points = [
                    [clamp_reinforcement_start_x,
                     clamp_reinforcement_near_table_bottom_z],
                    [clamp_reinforcement_end_x,
                     clamp_reinforcement_outer_bottom_z],
                    [clamp_reinforcement_end_x,
                     clamp_reinforcement_top_z],
                    [clamp_reinforcement_start_x,
                     clamp_reinforcement_top_z]
                ]);
}

module clamp_solid_outboard_bridge_positive() {
    // The x+ zone is outside the tabletop and must be solid rather than a
    // second open C-shaped gap.  Starting just beyond the table edge avoids
    // intersecting the tabletop while the lower edge remains the 40-to-12 mm
    // tapered support profile.
    color("slategray")
        rotate([90, 0, 0])
            linear_extrude(height = clamp_reinforcement_depth_y,
                           center = true)
                polygon(points = [
                    [clamp_solid_bridge_start_x,
                     clamp_reinforcement_near_table_bottom_z],
                    [clamp_reinforcement_end_x,
                     clamp_reinforcement_outer_bottom_z],
                    [clamp_reinforcement_end_x,
                     clamp_solid_bridge_top_z],
                    [clamp_solid_bridge_start_x,
                     clamp_solid_bridge_top_z]
                ]);
}

module clamp_electronics_cavity_negative() {
    // Open from the sloped underside. The cut stops 4 mm below the lower-arm
    // top, so the cavity has a real roof; the y limits leave 9 mm side walls.
    rotate([90, 0, 0])
        linear_extrude(
            height = 2 * clamp_electronics_cavity_y_half,
            center = true)
            polygon(points = [
                [clamp_electronics_cavity_x_min,
                 clamp_reinforcement_bottom_z_at(
                     clamp_electronics_cavity_x_min) - 2],
                [clamp_electronics_cavity_x_max,
                 clamp_reinforcement_bottom_z_at(
                     clamp_electronics_cavity_x_max) - 2],
                [clamp_electronics_cavity_x_max,
                 clamp_electronics_cavity_top_z],
                [clamp_electronics_cavity_x_min,
                 clamp_electronics_cavity_top_z]
            ]);
}

module clamp_electronics_slope_rail_x(x_min, x_max, y_center,
                                      width_y, base_offset_z,
                                      height_z) {
    // A short hull at each x end follows the trapezoid's sloped underside.
    // It is used for the cover locating lip and the replaceable seal strip so
    // the sealing interface stays continuous instead of becoming four
    // floating blocks.
    hull() {
        translate([x_min,
                   y_center - width_y / 2,
                   clamp_reinforcement_bottom_z_at(x_min) + base_offset_z])
            cube([0.2, width_y, height_z]);
        translate([x_max - 0.2,
                   y_center - width_y / 2,
                   clamp_reinforcement_bottom_z_at(x_max) + base_offset_z])
            cube([0.2, width_y, height_z]);
    }
}

module clamp_electronics_cover_lip_positive() {
    // The lip enters the cavity by 1.6 mm and is offset from the body edge by
    // a controlled print clearance.  The four bars overlap at their corners.
    lip_x_min = clamp_electronics_cavity_x_min +
        clamp_electronics_cover_lip_clearance;
    lip_x_max = clamp_electronics_cavity_x_max -
        clamp_electronics_cover_lip_clearance;
    lip_y = clamp_electronics_cavity_y_half -
        clamp_electronics_cover_lip_t / 2 -
        clamp_electronics_cover_lip_clearance;
    union() {
        for (y_side = [-1, 1])
            clamp_electronics_slope_rail_x(
                lip_x_min, lip_x_max, y_side * lip_y,
                clamp_electronics_cover_lip_t, -0.02,
                clamp_electronics_cover_lip_h + 0.04);
        for (x_side = [lip_x_min, lip_x_max])
            translate([
                x_side - clamp_electronics_cover_lip_t / 2,
                -lip_y,
                clamp_reinforcement_bottom_z_at(x_side) - 0.02])
                cube([
                    clamp_electronics_cover_lip_t,
                    2 * lip_y,
                    clamp_electronics_cover_lip_h + 0.04
                ]);
    }
}

module clamp_electronics_gasket_positive() {
    // Replaceable silicone/EPDM strip reference. It is deliberately a
    // separate preview part rather than being fused into the PETG cover.
    seal_x_min = clamp_electronics_cavity_x_min +
        clamp_electronics_gasket_clearance;
    seal_x_max = clamp_electronics_cavity_x_max -
        clamp_electronics_gasket_clearance;
    seal_y = clamp_electronics_cavity_y_half -
        clamp_electronics_gasket_width / 2 -
        clamp_electronics_gasket_clearance;
    color("orange", 0.78)
        union() {
            for (y_side = [-1, 1])
                clamp_electronics_slope_rail_x(
                    seal_x_min, seal_x_max, y_side * seal_y,
                    clamp_electronics_gasket_width, 0.08,
                    clamp_electronics_gasket_height);
            for (x_side = [seal_x_min, seal_x_max])
                translate([
                    x_side - clamp_electronics_gasket_width / 2,
                    -seal_y,
                    clamp_reinforcement_bottom_z_at(x_side) + 0.08])
                    cube([
                        clamp_electronics_gasket_width,
                        2 * seal_y,
                        clamp_electronics_gasket_height
                    ]);
        }
}

module clamp_electronics_board_standoffs_positive() {
    // Four board standoffs are added after the cavity subtraction: they live
    // inside the hollow volume, while the surrounding tapered wall remains a
    // single solid. The two x planes also stay clear of the battery envelope.
    for (hole = clamp_electronics_board_hole_xy) {
        x = hole[0];
        y = hole[1];
        floor_z = clamp_reinforcement_bottom_z_at(x) +
            clamp_electronics_board_standoff_floor_clearance_z;
        translate([x, y, floor_z])
            cylinder(
                d = clamp_electronics_board_standoff_d,
                h = clamp_electronics_board_bottom_z - floor_z + 0.03);
    }
}

module clamp_electronics_emitter_edge_clips_positive() {
    // The emitter board's nominal corner holes would sit under the broad face
    // of the pouch cell. Four edge supports/retention lips therefore carry the
    // board from the battery-free y strips instead of puncturing its envelope.
    support_width_y = 1.4;
    support_y = clamp_electronics_emitter_board_width_y / 2 -
        support_width_y / 2;
    support_length_x = 8;
    for (x = [clamp_electronics_emitter_board_x_min,
              clamp_electronics_emitter_board_x_max - support_length_x]) {
        for (y_side = [-1, 1]) {
            floor_z = clamp_reinforcement_bottom_z_at(x +
                support_length_x / 2) +
                clamp_electronics_board_standoff_floor_clearance_z;
            y_min = y_side > 0 ? support_y - support_width_y / 2 :
                -support_y - support_width_y / 2;
            translate([x, y_min, floor_z])
                cube([
                    support_length_x,
                    support_width_y,
                    clamp_electronics_emitter_board_bottom_z - floor_z +
                        0.03
                ]);
            // A shallow outboard cap retains the board edge under the cover;
            // its inner edge remains outside the 30 mm battery envelope.
            clip_y_min = y_side > 0 ? support_y - 0.1 :
                -support_y - 1.9;
            translate([
                x,
                clip_y_min,
                clamp_electronics_emitter_board_bottom_z +
                    clamp_electronics_emitter_board_t - 0.08
            ])
                cube([support_length_x, 2.0, 1.1]);
        }
    }
}

module clamp_electronics_battery_rails_positive() {
    // Two low rails retain the pouch battery without puncturing or squeezing
    // its broad faces. The rail centers leave 1.5 mm to the pouch edge.
    battery_y = clamp_electronics_battery_width_y / 2 +
        clamp_electronics_battery_rail_clearance_y;
    for (y_side = [-1, 1])
        clamp_electronics_slope_rail_x(
            clamp_electronics_battery_x_min - 2,
            clamp_electronics_battery_x_max + 2,
            y_side * battery_y,
            clamp_electronics_battery_rail_t,
            0.4,
            clamp_electronics_battery_rail_h);
}

// -----------------------------------------------------------------------------
// KiCad board/component solids used by the mechanical package.  The STL files
// are exported by hardware/electronics/export_board_models.py.  KiCad's STL
// convention is x=board x, y=-board y, z=board/component height, hence the
// explicit y translations below are part of the shared mechanical datum.

module clamp_electronics_main_board_positive() {
    if (electronics_kicad_models_enabled)
        color("royalblue", 0.96)
            translate([
                clamp_electronics_board_x_min,
                clamp_electronics_main_board_y_shift,
                clamp_electronics_board_bottom_z
            ])
                import("../electronics/3d/v0.2/esp32-control-v0.1.stl",
                       convexity = 10);
    else
        color("royalblue", 0.96)
            translate([
                clamp_electronics_board_x_min,
                clamp_electronics_main_board_y_shift -
                    clamp_electronics_board_width_y,
                clamp_electronics_board_bottom_z
            ])
                cube([
                    clamp_electronics_board_length_x,
                    clamp_electronics_board_width_y,
                    clamp_electronics_board_t
                ]);
}

module clamp_electronics_emitter_board_positive() {
    if (electronics_kicad_models_enabled)
        color("crimson", 0.96)
            translate([
                clamp_electronics_emitter_board_x_min,
                clamp_electronics_emitter_board_y_shift,
                clamp_electronics_emitter_board_bottom_z
            ])
                import("../electronics/3d/v0.2/emitter-power-v0.2.stl",
                       convexity = 10);
    else
        color("crimson", 0.96)
            translate([
                clamp_electronics_emitter_board_x_min,
                clamp_electronics_emitter_board_y_shift -
                    clamp_electronics_emitter_board_width_y,
                clamp_electronics_emitter_board_bottom_z
            ])
                cube([
                    clamp_electronics_emitter_board_length_x,
                    clamp_electronics_emitter_board_width_y,
                    clamp_electronics_emitter_board_t
                ]);
}

module clamp_electronics_ui_board_positive() {
    if (electronics_kicad_models_enabled)
        color("royalblue", 0.96)
            translate([
                clamp_electronics_ui_board_x_min,
                clamp_electronics_ui_board_y_shift,
                clamp_electronics_ui_board_z
            ])
                import("../electronics/3d/v0.2/ui-panel-v0.2.stl",
                       convexity = 10);
    else
        color("royalblue", 0.96)
            translate([
                clamp_electronics_ui_board_x_min,
                clamp_electronics_ui_board_y_shift -
                    clamp_electronics_ui_board_width_y,
                clamp_electronics_ui_board_z
            ])
                cube([
                    clamp_electronics_ui_board_length_x,
                    clamp_electronics_ui_board_width_y,
                    clamp_electronics_ui_board_t
                ]);
}

module clamp_electronics_battery_positive() {
    // The pouch is a bought protected cell.  The printed rails touch only its
    // edge band; no boss or screw pierces the broad face.
    color("orange", 0.82)
        translate([
            clamp_electronics_battery_x_min,
            -clamp_electronics_battery_width_y / 2,
            clamp_reinforcement_bottom_z_at(
                (clamp_electronics_battery_x_min +
                 clamp_electronics_battery_x_max) / 2) +
                clamp_electronics_battery_clearance_z
        ])
            cube([
                clamp_electronics_battery_length_x,
                clamp_electronics_battery_width_y,
                clamp_electronics_battery_thickness_z
            ]);
}

module m6_receiver_carrier_board_raw_positive() {
    // Local board x becomes assembly z by a -90 degree Y rotation.  Local
    // board y is already the assembly y direction; the +y placement keeps the
    // carrier away from the rear boss, while cable branches remain on y-.
    if (electronics_kicad_models_enabled)
        color("seagreen", 0.96)
            translate([
                m6_receiver_carrier_board_x,
                m6_receiver_carrier_board_y,
                m6_receiver_carrier_board_z_min
            ])
                rotate([0, -90, 0])
                    import("../electronics/3d/v0.2/m6-receiver-carrier-v0.2.stl",
                           convexity = 10);
    else
        color("seagreen", 0.96)
            translate([
                m6_receiver_carrier_board_x -
                    m6_receiver_carrier_board_t_x,
                m6_receiver_carrier_board_y -
                    m6_receiver_carrier_width_y,
                m6_receiver_carrier_board_z_min
            ])
                cube([
                    m6_receiver_carrier_board_t_x,
                    m6_receiver_carrier_width_y,
                    m6_receiver_carrier_length_z
                ]);
}

module m6_receiver_carrier_board_positive() {
    // Installed wrapper.  The raw variant is used inside the detector's own
    // translated assembly so the mount offset is applied exactly once.
    translate([m6_detector_mount_x_offset, 0, m6_detector_mount_raise_z])
        m6_receiver_carrier_board_raw_positive();
}

module clamp_electronics_wiring_reference_positive() {
    // This is a serviceable route reference, not a rigid-cable claim.  The
    // bundle leaves the mother board through J4, runs beside the clamp/post,
    // then enters the M6 carrier from its +y cable side.  Each side is
    // mirrored by sided(-1), so RX and TX never share an unlabeled harness.
    board_wire_z = clamp_electronics_board_bottom_z + 2.8;
    carrier_wire_z =
        m6_detector_mount_raise_z +
        m6_receiver_carrier_board_z_min + 24;
    route_x = clamp_electronics_cavity_x_max + 5;
    carrier_x =
        m6_detector_mount_x_offset +
        m6_receiver_carrier_board_x - 5;
    color("royalblue", 0.82) {
        m6_cylinder_x(
            2.6,
            abs(route_x - (clamp_electronics_board_x_max - 5)),
            (route_x + clamp_electronics_board_x_max - 5) / 2,
            10,
            board_wire_z);
        m6_cylinder_z(
            2.6,
            carrier_wire_z - board_wire_z,
            route_x,
            10,
            (carrier_wire_z + board_wire_z) / 2);
        m6_cylinder_x(
            2.6,
            abs(route_x - carrier_x),
            (route_x + carrier_x) / 2,
            10,
            carrier_wire_z);
        m6_cylinder_y(
            2.6,
            abs(m6_receiver_carrier_board_y - 10),
            carrier_x,
            (m6_receiver_carrier_board_y + 10) / 2,
            carrier_wire_z);
    }
    color("gold", 0.92)
        translate([route_x - 4, 7, board_wire_z - 2])
            cube([8, 6, 4]);
}

module clamp_electronics_local_wiring_positive() {
    // Close-up harness stub used by the cavity views.  The complete board-to-
    // M6 route stays in clamp_electronics_wiring_reference_positive(); keeping
    // the long vertical run out of this close-up makes the shell/PCB fit
    // readable instead of shrinking it to a dot.
    board_wire_z = clamp_electronics_board_bottom_z + 2.8;
    route_x = clamp_electronics_cavity_x_max + 5;
    color("royalblue", 0.84)
        m6_cylinder_x(
            2.6,
            abs(route_x - (clamp_electronics_board_x_max - 5)),
            (route_x + clamp_electronics_board_x_max - 5) / 2,
            10,
            board_wire_z);
    color("gold", 0.94)
        translate([route_x - 4, 7, board_wire_z - 2])
            cube([8, 6, 4]);
}

module clamp_electronics_ui_bosses_positive() {
    // UI daughter mounting points hang from the outside of the cover. They
    // are separate from the four cover screws and leave the board removable.
    for (x = [clamp_electronics_ui_board_x_min +
                  clamp_electronics_board_mount_hole_inset_x,
              clamp_electronics_ui_board_x_max -
                  clamp_electronics_board_mount_hole_inset_x]) {
        for (y = [-clamp_electronics_ui_board_width_y / 2 +
                      clamp_electronics_board_mount_hole_inset_y,
                  clamp_electronics_ui_board_width_y / 2 -
                      clamp_electronics_board_mount_hole_inset_y]) {
            boss_top_z = clamp_reinforcement_bottom_z_at(x) -
                clamp_electronics_cavity_cover_t;
            boss_bottom_z = clamp_electronics_ui_board_z +
                clamp_electronics_ui_board_t - 0.1;
            translate([x, y, boss_bottom_z])
                cylinder(
                    d = clamp_electronics_board_standoff_d,
                    h = boss_top_z - boss_bottom_z + 0.1);
        }
    }
}

module clamp_electronics_ui_panel_positive() {
    // Removable UI daughter board on the underside of the sealed cover. The
    // board/component solid now comes from the KiCad export; the panel parts
    // below are the actual service envelopes that the faceplate must capture.
    clamp_electronics_ui_board_positive();
    color("black", 0.72)
        translate([
            clamp_electronics_ui_screen_x_min,
            -clamp_electronics_ui_screen_width_y / 2,
            clamp_electronics_ui_board_z +
                clamp_electronics_ui_board_t + 0.2])
            cube([
                clamp_electronics_ui_screen_length_x,
                clamp_electronics_ui_screen_width_y,
                1.2]);
    for (x = [clamp_electronics_ui_board_x_min + 8,
              clamp_electronics_ui_board_x_max - 8])
        color("darkgray")
            translate([x, 0,
                       clamp_electronics_ui_board_z +
                           clamp_electronics_ui_board_t + 0.2])
                cylinder(d = clamp_electronics_ui_button_d, h = 3);
    for (y = [-8, 8])
        color("limegreen")
            translate([
                (clamp_electronics_ui_board_x_min +
                 clamp_electronics_ui_board_x_max) / 2,
                y,
                clamp_electronics_ui_board_z +
                    clamp_electronics_ui_board_t + 0.2])
                cylinder(d = clamp_electronics_ui_led_d, h = 2.5);
    color("darkslategray", 0.88)
        translate([
            clamp_electronics_ui_board_x_min +
                clamp_electronics_ui_board_length_x * 0.78,
            0,
            clamp_electronics_ui_board_z +
                clamp_electronics_ui_board_t + 0.2])
            cylinder(d = clamp_electronics_ui_speaker_d, h = 2.2);
    color("gold", 0.9)
        translate([
            clamp_electronics_ui_board_x_max - 5,
            -clamp_electronics_ui_board_width_y / 2 + 5,
            clamp_electronics_ui_board_z +
                clamp_electronics_ui_board_t + 0.2])
            cylinder(d = 6, h = 2.2);
    // A capped panel USB-C reference is kept next to the UI board; it is not
    // a raw open hole through the PETG cover.
    color("black", 0.9)
        translate([
            clamp_electronics_ui_board_x_min + 5,
            0,
            clamp_electronics_ui_board_z +
                clamp_electronics_ui_board_t + 0.2])
            cube([8, 5, 2.2]);
}

module clamp_electronics_ui_bezel_positive() {
    // Separate printable faceplate: screen window, two button bores, two
    // light-pipe bores, speaker acoustic opening, and capped USB-C slot. The
    // cover below remains a continuous compression surface; this bezel is the
    // user-facing replaceable panel and is not a raw hole through the seal.
    faceplate_x_min = clamp_electronics_ui_board_x_min -
        clamp_electronics_faceplate_border;
    faceplate_x_max = clamp_electronics_ui_board_x_max +
        clamp_electronics_faceplate_border;
    faceplate_y_half = clamp_electronics_ui_board_width_y / 2 +
        clamp_electronics_faceplate_border;
    faceplate_z = clamp_electronics_ui_board_z +
        clamp_electronics_ui_board_t + 3.2;
    color("black")
        difference() {
            translate([
                faceplate_x_min,
                -faceplate_y_half,
                faceplate_z
            ])
                cube([
                    faceplate_x_max - faceplate_x_min,
                    2 * faceplate_y_half,
                    clamp_electronics_faceplate_t
                ]);
            // Display window.
            translate([
                clamp_electronics_ui_screen_x_min -
                    clamp_electronics_faceplate_window_clearance,
                -clamp_electronics_ui_screen_width_y / 2 -
                    clamp_electronics_faceplate_window_clearance,
                faceplate_z - 0.1
            ])
                cube([
                    clamp_electronics_ui_screen_length_x +
                        2 * clamp_electronics_faceplate_window_clearance,
                    clamp_electronics_ui_screen_width_y +
                        2 * clamp_electronics_faceplate_window_clearance,
                    clamp_electronics_faceplate_t + 0.2
                ]);
            // START and MODE buttons.
            for (x = [clamp_electronics_ui_board_x_min + 8,
                      clamp_electronics_ui_board_x_max - 8])
                translate([x, 0, faceplate_z - 0.1])
                    cylinder(
                        d = clamp_electronics_ui_button_d + 0.6,
                        h = clamp_electronics_faceplate_t + 0.2,
                        $fn = 64);
            // Status and battery light pipes.
            for (y = [-8, 8])
                translate([
                    (clamp_electronics_ui_board_x_min +
                     clamp_electronics_ui_board_x_max) / 2,
                    y,
                    faceplate_z - 0.1
                ])
                    cylinder(
                        d = clamp_electronics_ui_led_d + 0.8,
                        h = clamp_electronics_faceplate_t + 0.2,
                        $fn = 48);
            // Speaker acoustic window with a thin membrane installed later.
            translate([
                clamp_electronics_ui_board_x_min +
                    clamp_electronics_ui_board_length_x * 0.78,
                0,
                faceplate_z - 0.1
            ])
                cylinder(
                    d = clamp_electronics_ui_speaker_d - 4,
                    h = clamp_electronics_faceplate_t + 0.2,
                    $fn = 72);
            // USB-C bulkhead slot and silicone cap seat.
            translate([
                clamp_electronics_ui_board_x_min + 5,
                -3,
                faceplate_z - 0.1
            ])
                cube([8, 6, clamp_electronics_faceplate_t + 0.2]);
        }
}

module clamp_electronics_mount_bosses_positive() {
    // Four M3 pilot bosses sit in the retained side walls and are outside the
    // board envelope. They are pilots, not final insert geometry, until PETG
    // pull-out testing is recorded.
    for (x = [clamp_electronics_cavity_x_min + 4,
              clamp_electronics_cavity_x_max - 4]) {
        for (y = [-clamp_electronics_cavity_y_half - 3,
                  clamp_electronics_cavity_y_half + 3]) {
            translate([x, y,
                       clamp_reinforcement_bottom_z_at(x) - 1])
                cylinder(d = clamp_electronics_mount_boss_d, h = 10);
        }
    }
}

module clamp_electronics_cover_positive() {
    cover_x_min = clamp_electronics_cavity_x_min - 4;
    cover_x_max = clamp_electronics_cavity_x_max + 4;
    cover_y_half = clamp_electronics_cavity_y_half + 3;
    union() {
        color("black")
            difference() {
                rotate([90, 0, 0])
                    linear_extrude(
                        height = 2 * cover_y_half,
                        center = true)
                        polygon(points = [
                            [cover_x_min,
                             clamp_reinforcement_bottom_z_at(cover_x_min) -
                                 clamp_electronics_cavity_cover_t],
                            [cover_x_max,
                             clamp_reinforcement_bottom_z_at(cover_x_max) -
                                 clamp_electronics_cavity_cover_t],
                            [cover_x_max,
                             clamp_reinforcement_bottom_z_at(cover_x_max)],
                            [cover_x_min,
                             clamp_reinforcement_bottom_z_at(cover_x_min)]
                        ]);
                for (x = [clamp_electronics_cavity_x_min + 4,
                          clamp_electronics_cavity_x_max - 4]) {
                    for (y = [-clamp_electronics_cavity_y_half - 3,
                              clamp_electronics_cavity_y_half + 3]) {
                        translate([x, y,
                                   clamp_reinforcement_bottom_z_at(x) - 2])
                            cylinder(d = clamp_electronics_mount_pilot_d, h = 8);
                    }
                }
            }
        color("black")
            clamp_electronics_cover_lip_positive();
        color("black")
            clamp_electronics_ui_bosses_positive();
    }
}

module clamp_electronics_shell_display_frame_positive() {
    // Open inspection frame for the close-up render.  It is deliberately a
    // thin perimeter made from the same cavity datums, so the PCB/pack are not
    // hidden by a cut face.  The exact production shell remains available as
    // PART=clamp_electronics_shell_cutaway and PART=table_clamp_body.
    color("slategray", 0.42)
        union() {
            // Cavity roof and sloped floor rails.
            translate([
                clamp_electronics_cavity_x_min - 2,
                -clamp_electronics_cavity_y_half,
                clamp_electronics_cavity_top_z - 1.5
            ])
                cube([
                    clamp_electronics_cavity_length_x + 4,
                    2 * clamp_electronics_cavity_y_half,
                    3
                ]);
            for (y_side = [-1, 1])
                clamp_electronics_slope_rail_x(
                    clamp_electronics_cavity_x_min - 2,
                    clamp_electronics_cavity_x_max + 2,
                    y_side * (clamp_electronics_cavity_y_half - 1.5),
                    3,
                    -0.2,
                    2.4);
            // Inboard/outboard end returns close the section without blocking
            // the board face; the returns retain the real trapezoid floor slope.
            for (x_side = [clamp_electronics_cavity_x_min,
                           clamp_electronics_cavity_x_max])
                hull() {
                    translate([
                        x_side - 1.5,
                        -clamp_electronics_cavity_y_half,
                        clamp_reinforcement_bottom_z_at(x_side) - 1
                    ])
                        cube([3, 3, clamp_electronics_cavity_top_z -
                              clamp_reinforcement_bottom_z_at(x_side) + 2]);
                    translate([
                        x_side - 1.5,
                        clamp_electronics_cavity_y_half - 3,
                        clamp_reinforcement_bottom_z_at(x_side) - 1
                    ])
                        cube([3, 3, clamp_electronics_cavity_top_z -
                              clamp_reinforcement_bottom_z_at(x_side) + 2]);
                }
        }
}

module clamp_electronics_shell_cutaway_positive() {
    // True inspection section: start with the real C-clamp, remove the actual
    // cavity volume once more as a rectangular display cut (the production
    // body uses the sloped cavity negative), and open both y side walls. The
    // result keeps the roof/floor/load path while making the installed parts
    // physically inspectable. This is display-only; the printable body stays
    // unchanged.
    difference() {
        table_clamp_body_positive();
        translate([
            clamp_electronics_cavity_x_min - 1,
            -clamp_electronics_cavity_y_half - 1,
            clamp_reinforcement_near_table_bottom_z - 1
        ])
            cube([
                clamp_electronics_cavity_length_x + 2,
                2 * clamp_electronics_cavity_y_half + 2,
                clamp_electronics_cavity_top_z -
                    clamp_reinforcement_near_table_bottom_z + 3
            ]);
        translate([
            clamp_electronics_cavity_x_min - 20,
            -clamp_reinforcement_depth_y / 2 - 1,
            clamp_lower_arm_bottom_z - 10
        ])
            cube([
                clamp_electronics_cavity_length_x + 40,
                clamp_reinforcement_depth_y / 2 -
                    clamp_electronics_cavity_y_half + 1,
                100
            ]);
        translate([
            clamp_electronics_cavity_x_min - 20,
            clamp_electronics_cavity_y_half,
            clamp_lower_arm_bottom_z - 10
        ])
            cube([
                clamp_electronics_cavity_length_x + 40,
                clamp_reinforcement_depth_y / 2 -
                    clamp_electronics_cavity_y_half + 1,
                100
            ]);
    }
}

module clamp_electronics_full_cutaway_positive() {
    // Complete right-side receiver/main-controller installation.  Every solid
    // in this view has a physical role: shell, cover gasket, PCB model, pouch
    // cell, UI PCB, faceplate, bosses, and the serviceable harness route.
    clamp_electronics_shell_display_frame_positive();
    clamp_electronics_board_standoffs_positive();
    clamp_electronics_mount_bosses_positive();
    clamp_electronics_gasket_positive();
    clamp_electronics_battery_rails_positive();
    clamp_electronics_main_board_positive();
    clamp_electronics_battery_positive();
    clamp_electronics_ui_panel_positive();
    clamp_electronics_ui_bezel_positive();
    clamp_electronics_local_wiring_positive();
}

module clamp_electronics_structural_shell_for_clearance_positive() {
    // Remove the intentionally touching internal bosses/rails from the
    // structural shell before a clearance intersection.  The diagnostic then
    // measures only accidental board/battery penetration into the tapered
    // walls, roof or load-bearing bridge.
    difference() {
        table_clamp_body_positive();
        clamp_electronics_board_standoffs_positive();
        clamp_electronics_emitter_edge_clips_positive();
        clamp_electronics_battery_rails_positive();
        clamp_electronics_mount_bosses_positive();
    }
}

module clamp_electronics_interference_check_positive() {
    // Empty output is the pass condition: any triangles mean an actual KiCad
    // board/component solid or pouch cell intersects the structural shell.
    intersection() {
        clamp_electronics_structural_shell_for_clearance_positive();
        union() {
            clamp_electronics_main_board_positive();
            clamp_electronics_emitter_board_positive();
            clamp_electronics_battery_positive();
        }
    }
}

module m6_receiver_carrier_interference_check_positive() {
    // The receiver PCB is installed in the raw detector datum.  The empty
    // intersection is checked against both whole removable shell halves and
    // the rear support gussets; the board is allowed to live in the interior,
    // but may not cross a shell wall or boss.
    intersection() {
        union() {
            m6_detector_shell_front_positive(1);
            m6_detector_shell_rear_positive(1);
        }
        m6_receiver_carrier_board_raw_positive();
    }
}

module clamp_electronics_fit_preview_positive() {
    // Main board fit preview is now the complete sectioned installation, not a
    // free-floating envelope.
    clamp_electronics_full_cutaway_positive();
}

module clamp_electronics_emitter_preview_positive() {
    // Standalone emitter board and internal protected cell, with the same
    // actual KiCad-exported component model used by the installed section.
    clamp_electronics_gasket_positive();
    clamp_electronics_cover_lip_positive();
    clamp_electronics_emitter_edge_clips_positive();
    clamp_electronics_emitter_board_positive();
    clamp_electronics_battery_positive();
    clamp_electronics_local_wiring_positive();
}

module clamp_electronics_emitter_fit_preview_positive() {
    // The mirrored left clamp owns the emitter/power PCB and its own internal
    // battery.  The section keeps the shell wall and boss geometry visible.
    clamp_electronics_shell_display_frame_positive();
    clamp_electronics_gasket_positive();
    clamp_electronics_battery_rails_positive();
    clamp_electronics_emitter_board_positive();
    clamp_electronics_battery_positive();
    clamp_electronics_emitter_edge_clips_positive();
    clamp_electronics_local_wiring_positive();
}

module clamp_electronics_system_preview() {
    // Right = receiver/main control; left = emitter/internal power. Both
    // clamp cavities are shown with real boards in their installed shells.
    sided(1) clamp_electronics_m6_integration_preview_positive(false);
    sided(-1) clamp_electronics_m6_integration_preview_positive(true);
}

module clamp_electronics_m6_integration_preview_positive(is_emitter = false) {
    // Close system relationship: the local clamp installation, the real
    // board-to-M6 service route, and the installed M6 shell/receiver PCB all
    // share the same world datum.  This is the evidence model for routing and
    // interference; the clamp close-up intentionally omits the long run.
    if (is_emitter)
        clamp_electronics_emitter_fit_preview_positive();
    else
        clamp_electronics_fit_preview_positive();
    clamp_electronics_wiring_reference_positive();
    m6_detector_assembly_positive();
}

module clamp_electronics_exploded_positive() {
    // Exploded right-side service view.  The shell remains at its datum and
    // each removable item is pulled along a readable axis with no hidden
    // boolean clipping: PCB upward, pouch downward, cover/gasket toward y-,
    // UI board/faceplate farther toward y-.
    clamp_electronics_shell_display_frame_positive();
    clamp_electronics_local_wiring_positive();
    translate([0, 0, 12]) clamp_electronics_main_board_positive();
    translate([0, 0, -10]) clamp_electronics_battery_positive();
    translate([0, -38, 7]) clamp_electronics_gasket_positive();
    translate([0, -52, 14]) clamp_electronics_cover_positive();
    translate([0, -58, -7]) clamp_electronics_ui_panel_positive();
    translate([0, -58, -4]) clamp_electronics_ui_bezel_positive();
}

module clamp_electronics_emitter_exploded_positive() {
    // Exploded left-side service view, including the internal emitter power
    // board, protected battery and the optional external power connector path.
    clamp_electronics_shell_display_frame_positive();
    clamp_electronics_local_wiring_positive();
    translate([0, 0, 12]) clamp_electronics_emitter_board_positive();
    translate([0, 0, -10]) clamp_electronics_battery_positive();
    translate([0, -38, 7]) clamp_electronics_gasket_positive();
    translate([0, -52, 14]) clamp_electronics_cover_positive();
}

module clamp_electronics_system_exploded() {
    sided(1) clamp_electronics_exploded_positive();
    sided(-1) clamp_electronics_emitter_exploded_positive();
    // Keep the M6 housing/carrier in the same exploded evidence set; the
    // receiver PCB is the endpoint of the service harness shown by the
    // integration preview.
    sided(1) m6_detector_exploded_assembly_positive();
    sided(-1) m6_detector_exploded_assembly_positive();
}

module clamp_electronics_cutaway_preview_positive() {
    // Backward-compatible PART name for the complete section view.
    clamp_electronics_full_cutaway_positive();
}

module table_clamp_raw_positive() {
    // Uncut C-clamp stock belongs to the fixed gray body. The top of this
    // fixed body is the horizontal seating plane at z=16 mm; the current
    // upright begins on that plane and owns its own solid lower taper.
    color("slategray")
        union() {
            translate([clamp_pad_x, -clamp_pad_depth / 2, clamp_top_pad_t])
                cube([clamp_pad_outer_x - clamp_pad_x,
                      clamp_pad_depth, clamp_pad_t]);
            translate([clamp_outer_wall_x, -clamp_pad_depth / 2,
                       clamp_lower_arm_bottom_z])
                cube([clamp_outer_wall_width, clamp_pad_depth,
                      clamp_pad_t + clamp_top_pad_t + table_thickness +
                      clamp_lower_arm_clearance]);
            translate([clamp_lower_arm_x, -clamp_pad_depth / 2,
                       clamp_lower_arm_bottom_z])
                cube([clamp_pad_outer_x - clamp_lower_arm_x,
                      clamp_pad_depth, clamp_lower_arm_t]);
            translate([clamp_screw_x, 0, clamp_lower_arm_bottom_z])
                cylinder(d = clamp_threaded_boss_d, h = clamp_threaded_boss_h);
            clamp_solid_tapered_reinforcement_positive();
            clamp_solid_outboard_bridge_positive();
            clamp_electronics_mount_bosses_positive();
        }
}

module table_clamp_body_positive() {
    // 固定件是一个真正有开口的 C 形夹体：上夹板在台面上方，
    // 下臂在台底下方，中间留出台面厚度和压块行程；不把任何零件嵌入台面。
    difference() {
            table_clamp_raw_positive();
            // M8 螺杆只穿过下臂/螺母座，不能穿过球台。
            translate([clamp_screw_x, 0, clamp_lower_arm_bottom_z - 1])
                cylinder(d = clamp_screw_bore_d,
                         h = clamp_threaded_boss_h + 2);
            // 下臂下侧捕获固定 M8 螺母；螺杆转动而沿轴向进退，
            // 旋钮/螺杆受力路径不依赖 PETG 螺纹。
            translate([clamp_screw_x, 0, clamp_lower_arm_bottom_z - 0.01])
                hex_prism(clamp_nut_pocket_af, clamp_nut_pocket_depth + 0.01);
            clamp_electronics_cavity_negative();
            for (x = [clamp_electronics_cavity_x_min + 4,
                      clamp_electronics_cavity_x_max - 4]) {
                for (y = [-clamp_electronics_cavity_y_half - 3,
                          clamp_electronics_cavity_y_half + 3]) {
                    translate([x, y,
                               clamp_reinforcement_bottom_z_at(x) - 2])
                        cylinder(d = clamp_electronics_mount_pilot_d, h = 12);
                }
            }
            // The C-clamp's upper contact shelf stays solid.  The 3 mm net
            // passage is cut only in the orange upright; cutting it here would
            // create the unwanted horizontal slot visible on the gray clamp.
            // Keep only the retired slide cuts behind the explicit feature
            // flag so a legacy diagnostic cannot hollow the new solid seat.
            union() {
                if (clamp_slide_interface_enabled) {
                    clamp_slide_grooves_negative_positive();
                    clamp_slide_post_foot_relief_negative_positive();
                    clamp_slide_lock_bores_negative_positive();
                    clamp_slide_detent_bores_negative_positive();
                }
            }
        }
    // These features are inside the hollow volume, so they must be added
    // after the main cavity subtraction instead of being cut away with it.
    clamp_electronics_board_standoffs_positive();
    clamp_electronics_emitter_edge_clips_positive();
    clamp_electronics_battery_rails_positive();
}

module clamp_body_segment_positive() {
    // Printable fixed gray clamp shell. It contains the complete C-frame
    // envelope, trapezoid electronics cavity, two full-length female
    // slideways and the fixed seat beneath the upright. The body reaches its
    // outboard face so it embraces the post foot from first contact onward.
    // table_clamp_body_positive() already owns the exact fixed-body envelope
    // from clamp_pad_x through clamp_fixed_body_max_x.  Avoiding a second
    // coincident clipping cube at the outboard face keeps the open receiver
    // edge clean in exported STL while preserving that same envelope.
    table_clamp_body_positive();
}

module table_clamp_carrier_positive(tongue_color = "darkorange") {
    // Compatibility entry point for old callers. The former shoe/rail carrier
    // is retired. The active lower transition is part of post_body_positive()
    // and therefore starts flush on the fixed C-clamp seat; this module must
    // stay empty so a second carrier, foot, or under-seat part cannot reappear.
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
    // 独立可动圆盘压块：顶面是平盘，只接触台面底面；底面中央的
    // 浅收纳窝包住 M8 圆头，避免螺杆在夹紧时从压块表面滑脱。
    color("black")
        translate([clamp_screw_x, 0, clamp_pressure_pad_bottom_z])
            difference() {
                cylinder(d = clamp_pressure_pad_d,
                         h = clamp_pressure_pad_t,
                         $fn = 96);
                translate([0, 0, -0.01])
                    cylinder(d = clamp_pressure_pad_screw_socket_d,
                             h = clamp_pressure_pad_screw_socket_depth + 0.01,
                             $fn = 64);
                // 下缘倒角/喇叭口，方便圆头自动落入收纳窝。
                translate([0, 0, -0.01])
                    cylinder(d1 = clamp_pressure_pad_screw_socket_mouth_d,
                             d2 = clamp_pressure_pad_screw_socket_d,
                             h = clamp_pressure_pad_screw_socket_chamfer_h,
                             $fn = 64);
            }
}

module clamp_top_pad_positive() {
    // 台面上侧胶皮的装配占位：首样直接把胶皮粘在固定上夹板下表面；
    // 这里保留 2 mm 包络用于检查间隙，不把它列入正式打印件。
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

module clamp_knob_grip_positive() {
    // A round root plus overlapping round lobes gives a printable, rounded
    // saw-tooth grip.  The valleys stay inside the original Ø36 mm envelope,
    // while every lobe has a continuous radial connection to the root.
    translate([clamp_screw_x, 0, clamp_knob_bottom_z]) {
        cylinder(d = clamp_knob_grip_root_d, h = clamp_knob_h, $fn = 96);
        for (index = [0 : clamp_knob_grip_tooth_count - 1])
            rotate([0, 0, 360 * index / clamp_knob_grip_tooth_count])
                translate([clamp_knob_grip_tooth_pitch_r, 0, 0])
                    cylinder(d = clamp_knob_grip_tooth_d,
                             h = clamp_knob_h,
                             $fn = 24);
    }
}

module clamp_knob_positive() {
    color("dimgray")
        difference() {
            clamp_knob_grip_positive();
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

module clamp_slide_grooves_negative_positive() {
    // Female receivers are enclosed T-slot tunnels cut into the solid top jaw
    // of the inboard clamp body. Their only openings are at the outboard x
    // end, so the carrier can be inserted from outside and stopped at the
    // terminal shoulder. The wide head is captured above and below instead
    // of relying on two exposed cylindrical-looking tongues.
    for (y_position = clamp_slide_rail_y_positions)
        interlocking_slide_prism_x(
            clamp_slide_tongue_min_x - 0.3,
            // Run well past the fixed-body outboard face.  The extra opening
            // allowance keeps the female tunnel genuinely open at x+ and
            // avoids a coplanar end cap when the lowered receiver meets that
            // face; it does not change the 81 mm usable track datum.
            clamp_slide_receiver_length_x + 2,
            y_position,
            clamp_slide_receiver_floor_z,
            clamp_slide_rail_head_width_y + 2 * clamp_slide_clearance,
            clamp_slide_rail_neck_width_y + 2 * clamp_slide_clearance,
            clamp_slide_rail_head_height_z + clamp_slide_clearance,
            clamp_slide_receiver_neck_height_z
        );
}

module clamp_slide_receiver_lower_support_positive() {
    // Lowering the shoes must lower the gray receiver's load floor with them.
    // This is a shallow continuation of the fixed top jaw, not an extra part:
    // it occupies only the outboard x zone (already clear of the tabletop) and
    // is cut by the same net passage and female T-slots below.
    support_bottom_z = clamp_slide_receiver_floor_z - 0.6;
    // Overlap the original upper jaw by 0.2 mm so the support and jaw become
    // one solid instead of meeting on a coincident face.
    support_top_z = clamp_top_pad_t + 0.2;
    if (support_top_z > support_bottom_z)
        translate([
            clamp_slide_tongue_min_x - 1,
            -clamp_pad_depth / 2,
            support_bottom_z
        ])
            cube([
                clamp_pad_outer_x - 0.2 -
                    (clamp_slide_tongue_min_x - 1),
                clamp_pad_depth,
                support_top_z - support_bottom_z
            ]);
}

module clamp_slide_post_foot_positive() {
    // Retired compatibility name. The previous two-shoe/pants carrier was
    // structurally wrong for the requested seated interface. Diagnostics that
    // still select this name now show the same single solid transition as the
    // active post, never the old under-seat geometry.
    post_interface_transition_positive();
}

function clamp_slide_post_foot_ease(t) =
    t * t * (3 - 2 * t);

function clamp_slide_post_foot_lerp(a, b, t) =
    a + (b - a) * t;

function clamp_slide_post_foot_gap_inner_y(z) =
    clamp_slide_post_foot_inner_y(z);

function clamp_slide_post_foot_rail_blend_t(z) =
    max(
        0,
        min(
            1,
            (z -
             (clamp_slide_rail_floor_z +
              clamp_slide_rail_head_height_z)) /
                clamp_slide_rail_neck_height_z
        )
    );

function clamp_slide_post_foot_post_blend_t(z) =
    max(
        0,
        min(
            1,
            (z - clamp_slide_post_foot_transition_side_start_z) /
                (clamp_slide_post_foot_transition_end_z -
                 clamp_slide_post_foot_transition_side_start_z)
        )
    );

function clamp_slide_post_foot_rail_width_y(z) =
    z <= clamp_slide_rail_floor_z + clamp_slide_rail_head_height_z
        ? clamp_slide_rail_head_width_y
        : clamp_slide_post_foot_lerp(
              clamp_slide_rail_head_width_y,
              clamp_slide_rail_neck_width_y,
              clamp_slide_post_foot_ease(
                  clamp_slide_post_foot_rail_blend_t(z)
              )
          );

function clamp_slide_post_foot_outer_y(z) =
    z <= clamp_slide_rail_floor_z + clamp_slide_rail_head_height_z
        ? clamp_slide_rail_y_positions[1] +
              clamp_slide_rail_head_width_y / 2
        : z <= clamp_slide_rail_floor_z + clamp_slide_rail_height_z
            ? clamp_slide_rail_y_positions[1] +
                  clamp_slide_post_foot_rail_width_y(z) / 2
            : clamp_slide_post_foot_lerp(
                  clamp_slide_rail_y_positions[1] +
                      clamp_slide_rail_neck_width_y / 2,
                  clamp_slide_post_foot_side_top_outer_y,
                  clamp_slide_post_foot_ease(
                      clamp_slide_post_foot_post_blend_t(z)
                  )
              );

function clamp_slide_post_foot_inner_y(z) =
    z <= clamp_slide_rail_floor_z + clamp_slide_rail_head_height_z
        ? clamp_slide_rail_y_positions[1] -
              clamp_slide_rail_head_width_y / 2
        : z <= clamp_slide_rail_floor_z + clamp_slide_rail_height_z
            ? clamp_slide_rail_y_positions[1] -
                  clamp_slide_post_foot_rail_width_y(z) / 2
            : clamp_slide_post_foot_lerp(
                  clamp_slide_rail_y_positions[1] -
                      clamp_slide_rail_neck_width_y / 2,
                  clamp_slide_post_foot_side_top_inner_y,
                  clamp_slide_post_foot_ease(
                      clamp_slide_post_foot_post_blend_t(z)
                  )
              );

function clamp_slide_post_foot_outer_x(z) =
    clamp_slide_post_foot_lerp(
        clamp_slide_post_foot_root_max_x,
        clamp_slide_post_foot_slope_top_max_x,
        clamp_slide_post_foot_ease(
            clamp_slide_post_foot_post_blend_t(z)
        )
    );

function clamp_slide_post_foot_inner_x(z) =
    clamp_slide_post_foot_lerp(
        clamp_slide_tongue_min_x,
        clamp_slide_post_foot_slope_top_min_x,
        clamp_slide_post_foot_ease(
            clamp_slide_post_foot_post_blend_t(z)
        )
    );

function post_down_extension_stage1_green_t(z) =
    max(
        0,
        min(
            1,
            (z - post_down_extension_stage1_green_transition_start_z) /
                (post_down_extension_stage1_top_z -
                 post_down_extension_stage1_green_transition_start_z)
        )
    );

function post_down_extension_stage1_green_min_x(z) =
    clamp_slide_post_foot_lerp(
        post_down_extension_stage1_bottom_min_x,
        post_down_extension_stage1_top_min_x,
        clamp_slide_post_foot_ease(
            post_down_extension_stage1_green_t(z)
        )
    );

function post_down_extension_stage1_green_max_x(z) =
    clamp_slide_post_foot_lerp(
        post_down_extension_stage1_bottom_max_x,
        post_down_extension_stage1_top_max_x,
        clamp_slide_post_foot_ease(
            post_down_extension_stage1_green_t(z)
        )
    );

module clamp_slide_post_foot_pants_positive() {
    // Retired diagnostic alias. Keep old PART names safe and visually honest:
    // the current design is one solid, full-width tapered transition seated on
    // the C-clamp plane, not two legs plus a central crotch.
    post_interface_transition_positive();
}

module clamp_slide_post_foot_leg_positive(y_side) {
    // The lower rail-head footprint is the broad shoe.  From the rail neck
    // upward, x and y both ease continuously into the narrow two-sided post;
    // neither side is made by stacking a second rectangular collar.
    points = [
        for (i = [0:clamp_slide_post_foot_transition_section_count])
            let(
                t = i / clamp_slide_post_foot_transition_section_count,
                z = clamp_slide_post_foot_bottom_z +
                    (clamp_slide_post_foot_top_z -
                     clamp_slide_post_foot_bottom_z) * t,
                y_min = y_side > 0
                    ? clamp_slide_post_foot_inner_y(z)
                    : -clamp_slide_post_foot_outer_y(z),
                y_max = y_side > 0
                    ? clamp_slide_post_foot_outer_y(z)
                    : -clamp_slide_post_foot_inner_y(z)
            )
            each [
                [clamp_slide_post_foot_inner_x(z), y_min, z],
                [clamp_slide_post_foot_outer_x(z), y_min, z],
                [clamp_slide_post_foot_outer_x(z), y_max, z],
                [clamp_slide_post_foot_inner_x(z), y_max, z]
            ]
    ];
    // OpenSCAD's polyhedron face convention needs the opposite winding from
    // the old diagnostic loft.  Keep every outside normal pointing away from
    // the leg; otherwise a later union can classify an overlapping crotch as
    // a subtraction and leave non-manifold seam edges.
    faces = concat(
        [[0, 1, 2, 3]],
        [
            for (i = [0:clamp_slide_post_foot_transition_section_count - 1])
                let(a = i * 4, b = (i + 1) * 4)
                each [
                    [a, b + 1, a + 1],
                    [a, b, b + 1],
                    [a + 1, b + 2, a + 2],
                    [a + 1, b + 1, b + 2],
                    [a + 2, b + 3, a + 3],
                    [a + 2, b + 2, b + 3],
                    [a + 3, b, a],
                    [a + 3, b + 3, b]
                ]
        ],
        [[
            clamp_slide_post_foot_transition_section_count * 4 + 3,
            clamp_slide_post_foot_transition_section_count * 4 + 2,
            clamp_slide_post_foot_transition_section_count * 4 + 1,
            clamp_slide_post_foot_transition_section_count * 4
        ]]
    );
    polyhedron(points = points, faces = faces, convexity = 10);
}

module clamp_slide_post_foot_crotch_positive() {
    // One thick, level cross-tie joins the two legs at the shoe end.  It is
    // intentionally wider than the local central gap so it bites into both
    // ankles; this is the solid "裤裆" in the sketch, not a floating bar.
    difference() {
        translate([
            clamp_slide_post_foot_bridge_min_x,
            -clamp_slide_post_foot_cross_tie_bridge_half_y,
            clamp_slide_post_foot_cross_tie_bottom_z
        ])
            cube([
                clamp_slide_post_foot_bridge_max_x -
                    clamp_slide_post_foot_bridge_min_x,
                2 * clamp_slide_post_foot_cross_tie_bridge_half_y,
                clamp_slide_post_foot_cross_tie_top_z -
                    clamp_slide_post_foot_cross_tie_bottom_z
            ]);
        clamp_slide_detent_dimple_negative_positive();
    }
}

module clamp_slide_post_foot_leg_test_positive(y_side = 1) {
    // Geometry-only diagnostic for one of the two continuous leg/shoe lofts.
    // This is not a formal print item.
    clamp_slide_post_foot_leg_positive(y_side);
}

module clamp_slide_post_foot_legs_test_positive() {
    union() {
        clamp_slide_post_foot_leg_positive(-1);
        clamp_slide_post_foot_leg_positive(1);
    }
}

module clamp_slide_post_foot_gap_prism_x(x0, length, z0, z1) {
    // Follow the same x taper as the outer pants envelope, with a small
    // overcut margin.  A fixed x prism crossing the sloped outer wall created
    // duplicate edge fragments at the transition; a parallel loft leaves the
    // central opening genuinely open while keeping the exported mesh closed.
    section_count = clamp_slide_post_foot_transition_section_count;
    x_margin = 0.4;
    points = [
        for (i = [0:section_count])
            let(
                t = i / section_count,
                z = z0 + (z1 - z0) * t,
                x_min = clamp_slide_post_foot_inner_x(z) - x_margin,
                x_max = clamp_slide_post_foot_outer_x(z) + x_margin,
                y_inner = clamp_slide_post_foot_gap_inner_y(z)
            )
            each [
                [x_min, -y_inner, z],
                [x_max, -y_inner, z],
                [x_max, y_inner, z],
                [x_min, y_inner, z]
            ]
    ];
    faces = concat(
        [[0, 3, 2, 1]],
        [
            for (i = [0:section_count - 1])
                let(a = i * 4, b = (i + 1) * 4)
                each [
                    [a, a + 1, b + 1],
                    [a, b + 1, b],
                    [a + 1, a + 2, b + 2],
                    [a + 1, b + 2, b + 1],
                    [a + 2, a + 3, b + 3],
                    [a + 2, b + 3, b + 2],
                    [a + 3, a, b],
                    [a + 3, b, b + 3]
                ]
        ],
        [[
            section_count * 4,
            section_count * 4 + 1,
            section_count * 4 + 2,
            section_count * 4 + 3
        ]]
    );
    polyhedron(points = points, faces = faces, convexity = 10);
}

module clamp_slide_post_foot_side_cheeks_positive(only_side = 0) {
    // Each side is one continuous 3-D tapered leg.  The lower section is the
    // broad shoe root; the upper section is exactly the corresponding side of
    // the post.  A single closed multi-section polyhedron is used instead of
    // unioning many hull solids: there are no internal slice faces for
    // OpenSCAD to display as horizontal steps.  The eased boundary is nearly
    // tangent to the flat shoe and to the vertical post side at both ends.
    for (y_side = [-1, 1])
        if (only_side == 0 || y_side == only_side) {
        bottom_y_min = y_side > 0
            ? clamp_slide_post_foot_side_inner_y
            : -clamp_slide_post_foot_side_outer_y;
        bottom_y_max = y_side > 0
            ? clamp_slide_post_foot_side_outer_y
            : -clamp_slide_post_foot_side_inner_y;
        top_y_min = y_side > 0
            ? clamp_slide_post_foot_side_top_inner_y
            : -clamp_slide_post_foot_side_top_outer_y;
        top_y_max = y_side > 0
            ? clamp_slide_post_foot_side_top_outer_y
            : -clamp_slide_post_foot_side_top_inner_y;
        points = [
            for (i = [0:clamp_slide_post_foot_transition_section_count])
                let(
                    t = i / clamp_slide_post_foot_transition_section_count,
                    z = clamp_slide_post_foot_bottom_z +
                        (clamp_slide_post_foot_top_z -
                         clamp_slide_post_foot_bottom_z) * t,
                        profile_x_t = max(
                            0,
                            min(
                                1,
                                (z - clamp_slide_post_foot_transition_side_start_z) /
                                (clamp_slide_post_foot_top_z -
                                 clamp_slide_post_foot_transition_side_start_z)
                            )
                        ),
                    profile_y_t = max(
                        0,
                        min(
                            1,
                            (z - clamp_slide_post_foot_transition_start_z) /
                                (clamp_slide_post_foot_top_z -
                                 clamp_slide_post_foot_transition_start_z)
                        )
                    ),
                    e_x = clamp_slide_post_foot_ease(profile_x_t),
                    e_y = clamp_slide_post_foot_ease(profile_y_t),
                    x_min = clamp_slide_post_foot_lerp(
                        clamp_slide_post_foot_root_min_x,
                        clamp_slide_post_foot_slope_top_min_x,
                        e_x),
                    x_max = clamp_slide_post_foot_lerp(
                        clamp_slide_post_foot_root_max_x,
                        clamp_slide_post_foot_slope_top_max_x,
                        e_x),
                    y_min = clamp_slide_post_foot_lerp(
                        bottom_y_min, top_y_min, e_y),
                    y_max = clamp_slide_post_foot_lerp(
                        bottom_y_max, top_y_max, e_y)
                )
                each [
                    [x_min, y_min, z],
                    [x_max, y_min, z],
                    [x_max, y_max, z],
                    [x_min, y_max, z]
                ]
        ];
        faces = concat(
            [[0, 3, 2, 1]],
            [
                for (i = [0:clamp_slide_post_foot_transition_section_count - 1])
                    let(a = i * 4, b = (i + 1) * 4)
                    each [
                        [a, a + 1, b + 1],
                        [a, b + 1, b],
                        [a + 1, a + 2, b + 2],
                        [a + 1, b + 2, b + 1],
                        [a + 2, a + 3, b + 3],
                        [a + 2, b + 3, b + 2],
                        [a + 3, a, b],
                        [a + 3, b, b + 3]
                    ]
            ],
            [[
                clamp_slide_post_foot_transition_section_count * 4,
                clamp_slide_post_foot_transition_section_count * 4 + 1,
                clamp_slide_post_foot_transition_section_count * 4 + 2,
                clamp_slide_post_foot_transition_section_count * 4 + 3
            ]]
        );
        polyhedron(points = points, faces = faces, convexity = 10);
    }
}

module clamp_slide_post_foot_cross_tie_positive() {
    // Compatibility name for old diagnostics.  The active design has only
    // one central crotch web; do not resurrect the old narrow floating tie
    // here, because it made the preview look like a third printed part.
    clamp_slide_post_foot_crotch_positive();
}

module clamp_slide_post_foot_detent_detail_positive() {
    // Compatibility preview name. The former foot/detent close-up is now a
    // clean inspection of the actual one-piece solid transition only.
    color("goldenrod", 0.94)
        post_interface_transition_positive();
}

module clamp_slide_post_foot_union_test_positive(include_post = true, include_rails = true) {
    // Temporary geometry diagnostic retained for self-checking the continuous
    // leg fusion; it is not a printable/exported part.
    difference() {
        union() {
            if (include_post)
                post_body_positive();
            if (include_rails)
                clamp_slide_tongues_positive("goldenrod", false);
            clamp_slide_post_foot_positive();
        }
        if (include_rails)
            clamp_slide_lock_bores_negative_positive();
        if (include_rails)
            clamp_slide_lock_nut_pockets_negative_positive();
    }
}

module clamp_slide_post_foot_raw_post_union_test_positive() {
    // Topology diagnostic for the geometric join alone.  No post slots,
    // detent, or anti-slide holes are included here.
    union() {
        translate([
            post_center_x - post_body_width / 2,
            -post_body_depth / 2,
            post_bottom
        ])
            cube([post_body_width, post_body_depth, active_post_total_height]);
        clamp_slide_post_foot_positive();
    }
}

module clamp_slide_post_foot_raw_post_cut_test_positive() {
    // Topology diagnostic for the final post/foot Boolean with only the cuts
    // that belong to the upright.  The M4 retainer cuts are intentionally
    // omitted so they cannot mask the source of a join problem.
    difference() {
        union() {
            translate([
                post_center_x - post_body_width / 2,
                -post_body_depth / 2,
                post_bottom
            ])
                cube([post_body_width, post_body_depth, active_post_total_height]);
            clamp_slide_post_foot_positive();
        }
        net_passage_negative_positive();
        net_clamp_channel_negative_positive();
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

module clamp_slide_post_foot_raw_post_single_cut_test_positive(cut_kind = 0) {
    // Isolate one post cut while hardening the one-piece carrier topology.
    difference() {
        union() {
            translate([
                post_center_x - post_body_width / 2,
                -post_body_depth / 2,
                post_bottom
            ])
                cube([post_body_width, post_body_depth, active_post_total_height]);
            clamp_slide_post_foot_positive();
        }
        if (cut_kind == 0)
            net_passage_negative_positive();
        if (cut_kind == 1)
            net_clamp_channel_negative_positive();
        if (cut_kind == 2)
            for (y_position = [-m6_post_mount_hole_y,
                               m6_post_mount_hole_y])
                m6_slot_x_z_span(
                    post_center_x,
                    y_position,
                    m6_post_mount_hole_z,
                    m6_mount_slot_length,
                    post_body_width + 8,
                    m6_post_mount_clearance_d);
    }
}

module clamp_slide_post_foot_tie_test_positive() {
    // Isolate the one-piece crowned crotch while debugging strict STL edge
    // topology; this diagnostic is never part of the print matrix.
    difference() {
        clamp_slide_post_foot_cross_tie_positive();
        clamp_slide_detent_dimple_negative_positive();
    }
}

module clamp_slide_post_foot_tie_cheek_test_positive(y_side = 1) {
    difference() {
        union() {
            clamp_slide_post_foot_side_cheeks_positive(y_side);
            clamp_slide_post_foot_cross_tie_positive();
        }
        clamp_slide_detent_dimple_negative_positive();
    }
}

module clamp_slide_post_foot_relief_negative_positive() {
    // These pockets are the actual open entry mouths for the two upper legs.
    // They run across the complete male-shoe x span, not only the last root
    // millimetres: once the shoe rises above the female tunnel roof, the
    // tapered leg must have a continuous open pocket through the fixed top jaw
    // or it would collide with gray material.  The pocket starts just below
    // the rail roof, leaving the broad lower head captured by the female
    // T-slot.  Its inboard edge follows the same eased carrier curve with
    // 0.35 mm clearance; the outboard edge stays open through the x+ entry.
    for (y_side = [-1, 1]) {
        relief_bottom_z =
            clamp_slide_post_foot_transition_side_start_z -
            clamp_slide_clearance;
        relief_points = concat(
            [
                [clamp_slide_tongue_min_x - clamp_slide_clearance,
                 relief_bottom_z],
                [clamp_slide_entry_open_x,
                 relief_bottom_z],
                [clamp_slide_entry_open_x,
                 clamp_slide_post_foot_top_z + clamp_slide_clearance],
                [
                    clamp_slide_post_foot_lerp(
                        clamp_slide_tongue_min_x,
                        clamp_slide_post_foot_slope_top_min_x,
                        clamp_slide_post_foot_ease(1)) -
                        clamp_slide_clearance,
                    clamp_slide_post_foot_top_z + clamp_slide_clearance
                ]
            ],
            [
                for (i = [clamp_slide_post_foot_transition_section_count:-1:0])
                    let(
                        t = i / clamp_slide_post_foot_transition_section_count,
                        z = clamp_slide_post_foot_transition_side_start_z +
                            (clamp_slide_post_foot_top_z -
                             clamp_slide_post_foot_transition_side_start_z) * t
                    )
                    [
                        clamp_slide_post_foot_inner_x(z) -
                            clamp_slide_clearance,
                        z
                    ]
            ]
        );
        translate([
            0,
            y_side > 0
                ? clamp_slide_post_foot_side_outer_y + clamp_slide_clearance
                : -clamp_slide_post_foot_side_top_inner_y + clamp_slide_clearance,
            0
        ])
            rotate([90, 0, 0])
                linear_extrude(
                    height = clamp_slide_post_foot_side_outer_y -
                        clamp_slide_post_foot_side_top_inner_y +
                        2 * clamp_slide_clearance
                )
                    polygon(points = relief_points);
    }
    // The low full-depth crotch also needs an unobstructed x+ entry. It is
    // below the net lower edge, so this opening does not cut the 3 mm net
    // passage or the removable U-clip path above z=0.
    translate([
        clamp_slide_post_foot_bridge_min_x - clamp_slide_clearance,
        -clamp_pad_depth / 2 - clamp_slide_clearance,
        clamp_slide_receiver_floor_z - 0.2
    ])
        cube([
            clamp_slide_entry_open_x -
                (clamp_slide_post_foot_bridge_min_x -
                 clamp_slide_clearance),
            clamp_pad_depth + 2 * clamp_slide_clearance,
            clamp_slide_post_foot_cross_tie_top_z +
                clamp_slide_clearance + 0.4 -
                clamp_slide_receiver_floor_z
        ]);
}

module clamp_slide_lock_bores_negative_positive() {
    // These are the two visible foot/shoe through-holes from the reference
    // sketch. They accept M4 retainers only to prevent the carrier sliding
    // back out; they do not replace the captured slide shoulders in the load
    // path and do not turn the crotch into a separate part.
    for (y_position = clamp_slide_lock_y_positions)
        m4_cylinder_z(
            clamp_slide_lock_bore_d,
            clamp_slide_rail_height_z + 12,
            clamp_slide_lock_x,
            y_position,
            clamp_slide_rail_center_z
        );
}

module clamp_slide_detent_bores_negative_positive() {
    // One vertical service bore belongs to the fixed gray body at the central
    // green location. The steel ball, spring and retainer are installed from
    // below; the bore is outside both structural rail shoulders.
    for (y_position = clamp_slide_detent_y_positions)
        translate([clamp_slide_detent_x,
                   y_position,
                   clamp_slide_detent_bore_bottom_z])
            cylinder(
                d = clamp_slide_detent_bore_d,
                h = clamp_slide_detent_bore_top_z -
                    clamp_slide_detent_bore_bottom_z,
                $fn = 32);
}

module clamp_slide_detent_dimple_negative_positive() {
    // Matching underside pocket in the orange central shoe-end tie. The ball rises
    // from the gray fixed body into this pocket only at the seated x position;
    // it is a locating feature, not a structural undercut in either rail.
    for (y_position = clamp_slide_detent_y_positions)
        translate([clamp_slide_detent_x,
                   y_position,
                   // Start below the actual crotch underside so the pocket is
                   // open on the underside of the tie.
                   clamp_slide_post_foot_cross_tie_bottom_z - 0.2])
            cylinder(
                d1 = clamp_slide_detent_dimple_d,
                d2 = 2.4,
                h = clamp_slide_detent_dimple_depth_z,
                $fn = 32);
}

module clamp_slide_detent_hardware_positive() {
    // One purchased 4 mm steel ball, one short compression spring and one
    // retainer live in the fixed gray body at the central green location. None
    // of these pieces carries clamp load.
    for (y_position = clamp_slide_detent_y_positions) {
        color("silver")
            translate([clamp_slide_detent_x,
                       y_position,
                       clamp_slide_detent_ball_center_z])
                sphere(d = clamp_slide_detent_ball_d, $fn = 32);
        color("silver", 0.5)
            translate([clamp_slide_detent_x,
                       y_position,
                       clamp_slide_detent_spring_bottom_z])
                cylinder(d = clamp_slide_detent_spring_d,
                         h = clamp_slide_detent_spring_h,
                         $fn = 16);
        color("dimgray")
            translate([clamp_slide_detent_x,
                       y_position,
                       clamp_slide_detent_retainer_center_z])
                cylinder(d = clamp_slide_detent_retainer_d,
                         h = clamp_slide_detent_retainer_h,
                         $fn = 32);
    }
}

module clamp_slide_lock_nut_pockets_negative_positive() {
    // These hex recesses belong to the final one-piece carrier boolean.  They
    // must be cut after the ankle/rail union so an ankle cannot accidentally
    // refill half of an M4 anti-slide hole at the first-contact root.
    for (y_position = clamp_slide_lock_y_positions)
        translate([
            clamp_slide_lock_x,
            y_position,
            clamp_slide_rail_floor_z - 0.01
        ])
            hex_prism(
                clamp_slide_lock_nut_af,
                clamp_slide_lock_nut_h + 0.02);
}

module clamp_slide_tongues_raw_positive(tongue_color = "darkorange") {
    color(tongue_color)
        union()
            for (y_position = clamp_slide_rail_y_positions)
                interlocking_slide_prism_x(
                    clamp_slide_tongue_min_x,
                    clamp_slide_length_x,
                    y_position,
                    clamp_slide_rail_floor_z,
                    clamp_slide_rail_head_width_y,
                    clamp_slide_rail_neck_width_y,
                    clamp_slide_rail_head_height_z,
                    clamp_slide_rail_neck_height_z
                );
}

module clamp_slide_tongues_positive(
    tongue_color = "darkorange",
    include_retainers = true
) {
    // Male runners live on the outboard carrier. Each runner has a broad
    // lower head and a narrower upper neck, matching the enclosed female
    // tunnel in the clamp body. The carrier moves x- into the body; the head
    // shoulders and broad shoe seat carry vertical/lateral loads after the
    // terminal shoulder bottoms out.
    if (include_retainers)
        difference() {
            clamp_slide_tongues_raw_positive(tongue_color);
            clamp_slide_lock_bores_negative_positive();
            // Capture the M4 anti-slide nut in the lower shoulder of each
            // male rail. The nut pocket is not part of the structural
            // slide interface; it only makes the retainer serviceable.
            clamp_slide_lock_nut_pockets_negative_positive();
        }
    else
        clamp_slide_tongues_raw_positive(tongue_color);
}

module clamp_slide_lock_hardware_positive() {
    // Standard M4 hardware is shown only to document the anti-slide lock.
    // Remove the bolts before pulling the carrier out; the broad slideway itself is
    // the structural interface.
    color("silver")
        for (y_position = clamp_slide_lock_y_positions)
            m4_cylinder_z(
                clamp_slide_lock_bolt_d,
                clamp_slide_lock_bolt_length,
                clamp_slide_lock_x,
                y_position,
                clamp_slide_rail_center_z
            );
    color("gold")
        for (y_position = clamp_slide_lock_y_positions)
            translate([
                clamp_slide_lock_x,
                y_position,
                clamp_slide_rail_floor_z
            ])
                hex_prism(
                    clamp_slide_lock_nut_af,
                    clamp_slide_lock_nut_h);
}

module table_clamp_positive() {
    // Show the current seated assembly: the inboard shell and the complete
    // upright are separate printable parts. The former slide/detent hardware
    // is intentionally absent because the current load path is the direct
    // horizontal seat plus the solid tapered post base.
    clamp_body_segment_positive();
    post_clamp_carrier_positive();
    if (clamp_slide_interface_enabled) {
        clamp_slide_detent_hardware_positive();
        clamp_slide_lock_hardware_positive();
    }
    clamp_top_pad_positive();
    clamp_body_nut_positive();
    clamp_pressure_pad_positive();
    clamp_screw_positive();
    clamp_knob_positive();
    clamp_knob_nut_positive();
}

module clamp_slide_fit_probe_positive() {
    // Direct seated-interface proof. The gray C body stops at its highest
    // horizontal support plane and the orange one-piece post starts on the
    // same z datum. Only the two real solids are shown here.
    section_x = post_interface_transition_outer_min_x - 4;
    section_y = post_interface_transition_outer_min_y - 4;
    section_z = post_bottom - 2;
    section_size = [
        post_interface_transition_outer_max_x -
            post_interface_transition_outer_min_x + 8,
        post_interface_transition_outer_max_y -
            post_interface_transition_outer_min_y + 8,
        post_interface_transition_height_z + 10
    ];
    color("slategray", 0.72)
        intersection() {
            clamp_body_segment_positive();
            translate([section_x, section_y, section_z])
                cube(section_size);
        }
    // +0.1 mm is display-only separation. The exported geometry and fit
    // checks keep the exact shared z=16 datum.
    color("darkorange", 0.92)
        intersection() {
            translate([0, preview_fit_display_gap, 0])
                post_clamp_carrier_positive();
            translate([section_x, section_y, section_z])
                cube(section_size);
        }
}

module clamp_slide_fit_section_positive() {
    // A real y-section through the positive rail.  The two colors are the
    // actual inboard shell and outboard carrier, clipped at one broad
    // interlocking slideway so the captured shoulders, lower seat and deep
    // U-foot root remain inspectable.
    // Focus on the actual root/entry zone.  The full 79.0 mm runner is shown
    // in clamp_slide_fit_section; this close-up keeps the x+ opening and the
    // sloped ankle from disappearing inside an oversized gray C-frame.
    section_x = post_center_x - 2;
    section_y = post_interface_transition_outer_min_y - 4;
    section_z = post_bottom - 2;
    section_width = 4;
    section_height = post_interface_transition_height_z + 10;
    section_depth = post_interface_transition_outer_max_y -
        post_interface_transition_outer_min_y + 8;
    color("slategray", 0.32)
        intersection() {
            clamp_body_segment_positive();
            translate([section_x, section_y, section_z])
                cube([section_width, section_depth, section_height]);
        }
    // No colored void or duplicate receiver is added. The section contains
    // only material from the fixed body and the real one-piece post.
    color("darkorange", 0.92)
        intersection() {
            // The overlay is the actual one-piece pants foot; no raw runner is
            // drawn on top of it as a second object.
            translate([0, preview_fit_display_gap, 0])
                post_clamp_carrier_positive();
            translate([section_x, section_y, section_z])
                cube([section_width, section_depth, section_height]);
        }
}

module clamp_slide_exploded_positive() {
    // Visual-only service separation for the current two-part design. The
    // fixed gray C body stays on the table and the complete orange post is
    // pulled only in +x; there are no extra feet, rails or loose click parts.
    clamp_body_segment_positive();
    translate([preview_slide_out_offset_x, 0, 0])
        post_clamp_carrier_positive();
}

module clamp_slide_exploded(side = 1) {
    sided(side) clamp_slide_exploded_positive();
}

module table_clamp_section_clip() {
    // 这是组合诊断剖面：一条窄中线穿过 M8 压紧螺杆/旋钮，另一条宽切片
    // 覆盖 y 全深的实心渐变支撑。两条切片一起显示完整的免打孔受力路径。
    section_y = clamp_pad_depth / 2 - clamp_reinforcement_depth_y / 2;
    union() {
        translate([clamp_pad_x - 8, -1,
                   clamp_knob_bottom_z - 5])
            cube([clamp_pad_outer_x - clamp_pad_x + 16,
                  2,
                  -clamp_knob_bottom_z + 10]);
        translate([clamp_pad_x - 8,
                   section_y - (clamp_reinforcement_depth_y + 2) / 2,
                   clamp_knob_bottom_z - 5])
            cube([clamp_pad_outer_x - clamp_pad_x + 16,
                  clamp_reinforcement_depth_y + 2,
                  -clamp_knob_bottom_z + 10]);
    }
}

module table_clamp_section_positive() {
    section_x = clamp_pad_x - 8;
    section_width = clamp_pad_outer_x - clamp_pad_x + 16;
    section_y = clamp_pad_depth / 2 - clamp_reinforcement_depth_y / 2;
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

// The thin net passage crosses the complete post envelope in x.  The 3 mm
// y-width is intentionally separate from the wider outboard U-slot: the net
// passes through the post first, then the printed U clip closes the pocket
// around its exposed edge.
module net_passage_negative_positive() {
    translate([net_passage_min_x,
               -net_passage_width_y / 2,
               net_passage_bottom_z - 0.2])
        cube([net_passage_max_x - net_passage_min_x,
              net_passage_width_y,
              net_passage_top_z - net_passage_bottom_z + 0.4]);
}

// The receiving pocket is a narrow full-height slot open at the outboard x
// face. The net first passes through the central 3 mm tunnel; the removable
// U clip then slides into this pocket from outside and its two jaws straddle
// the net edge. The pocket has an inboard stop, so the clip cannot be pushed
// through the post.
module net_clamp_channel_negative_positive() {
    // The U-clip is a full-height part starting at the table-top/net datum.
    // Keep this functional receiving pocket open through the solid taper as
    // well; otherwise the clip would genuinely collide with the post between
    // z=16 and z=40 instead of entering from the outboard face. This is one of
    // the two intentional openings in the otherwise solid transition, along
    // with the 3 mm net passage.
    translate([net_clamp_channel_void_min_x,
               -net_clamp_channel_width_y / 2,
               net_clamp_channel_bottom_z - 0.2])
        cube([net_clamp_channel_void_max_x - net_clamp_channel_void_min_x,
              net_clamp_channel_width_y,
              net_clamp_channel_top_z - net_clamp_channel_bottom_z + 0.4]);
}

// One solid keeper is part of the post, not a loose pin. It is fused into the
// positive-y channel wall and projects only into the outer edge of the
// positive-y jaw. The net/rope load still seats the U clip against the
// inboard stop; this small feature only blocks an accidental reverse pull.
module net_clamp_keeper_positive() {
    if (net_clamp_keeper_enabled)
        color("darkorange")
            translate([net_clamp_keeper_x_min,
                       net_clamp_keeper_y_min,
                       net_clamp_keeper_z])
                cube([net_clamp_keeper_x_max - net_clamp_keeper_x_min,
                      net_clamp_keeper_y_max - net_clamp_keeper_y_min,
                      net_clamp_keeper_height_z]);
}

module net_clamp_keeper_relief_negative_positive() {
    // The relief is open at the clip's inner sliding tip. The fixed keeper
    // enters this window during insertion; the separate clip-side latch tongue
    // closes the window behind the keeper for the reverse-pull stop.
    if (net_clamp_keeper_enabled)
        translate([net_clamp_keeper_relief_min_x,
                   net_clamp_keeper_relief_min_y,
                   net_clamp_keeper_z - net_clamp_keeper_relief_clearance_z])
            cube([net_clamp_keeper_relief_max_x -
                      net_clamp_keeper_relief_min_x,
                  net_clamp_keeper_relief_max_y -
                      net_clamp_keeper_relief_min_y,
                  net_clamp_keeper_height_z +
                      2 * net_clamp_keeper_relief_clearance_z]);
}

// The fixed keeper is blocked on reverse pull by this clip-side spring tongue.
// The tongue is part of the positive-y jaw, not a separate pin: its x- edge is
// chamfered as the insertion lead-in and its x+ edge is the closed shoulder.
// Pressing the same jaw outward flexes the tongue clear of the keeper so the
// entire full-height clip can be slid back out.
module net_clamp_keeper_latch_positive() {
    if (net_clamp_keeper_enabled)
        translate([0, 0, net_clamp_keeper_latch_z])
            linear_extrude(height = net_clamp_keeper_latch_height_z)
                polygon(points = [
                    [net_clamp_keeper_latch_x_min,
                     net_clamp_keeper_latch_y_min],
                    [net_clamp_keeper_latch_x_max,
                     net_clamp_keeper_latch_y_min],
                    [net_clamp_keeper_latch_x_max,
                     net_clamp_keeper_latch_y_max],
                    [net_clamp_keeper_latch_x_min + 0.35,
                     net_clamp_keeper_latch_y_max],
                    [net_clamp_keeper_latch_x_min,
                     net_clamp_keeper_latch_y_min + 0.3]
                ]);
}

module net_clamp_clip_positive() {
    // This is a real PETG print part, not a purchased hardware placeholder.
    // It is a vertical U-shaped slide clip: the two parallel jaws grip the
    // fabric faces and the outer crossbar gives a positive insertion stop.
    // It enters from the outboard x face, so the full net never needs to be
    // threaded through a closed post after the clip is installed. The
    // crossbar is outside the post face; the net fabric ends at that face and
    // therefore cannot collide with the crossbar. The positive-y jaw carries
    // one open-ended keeper relief and one fused one-way spring tongue; there
    // are no transverse fastener holes.
    color("goldenrod")
        union() {
            difference() {
                union() {
                    translate([net_clamp_clip_inner_x,
                               -net_clamp_clip_jaw_center_y -
                               net_clamp_clip_jaw_t_y / 2,
                               net_clamp_channel_bottom_z])
                        cube([net_clamp_clip_length_x,
                              net_clamp_clip_jaw_t_y,
                              net_clamp_cylinder_height]);
                    translate([net_clamp_clip_inner_x,
                               net_clamp_clip_jaw_center_y -
                               net_clamp_clip_jaw_t_y / 2,
                               net_clamp_channel_bottom_z])
                        cube([net_clamp_clip_length_x,
                              net_clamp_clip_jaw_t_y,
                              net_clamp_cylinder_height]);
                    translate([net_clamp_clip_outer_x - net_clamp_clip_crossbar_t_x,
                               -net_clamp_clip_outer_half_y,
                               net_clamp_channel_bottom_z])
                        cube([net_clamp_clip_crossbar_t_x,
                              2 * net_clamp_clip_outer_half_y,
                              net_clamp_cylinder_height]);
                }
                net_clamp_keeper_relief_negative_positive();
            }
            net_clamp_keeper_latch_positive();
        }
}

// Compatibility name for old preview callers. The active print name is
// net_clamp_clip, while this alias deliberately keeps the real assembly datum.
module net_clamp_rod_positive() {
    net_clamp_clip_positive();
}

module net_clamp_clip_printable_positive() {
    // Print the tall clip flat on its broad side. In the installed datum z is
    // the net height; for FDM export it becomes the y footprint, while the
    // jaw/crossbar thickness becomes the printable z thickness (~6.6 mm).
    translate([
        -net_clamp_clip_inner_x,
        net_clamp_channel_top_z,
        net_clamp_clip_outer_half_y
    ])
        rotate([90, 0, 0])
            net_clamp_clip_positive();
}

module net_clamp_fit_probe_positive() {
    // Preview-only gauge: display the post-side receiving pocket and the
    // separate U clip together, with a thin net strip between its jaws.
    color("red", 0.22)
        translate([net_clamp_channel_void_min_x,
                   -net_clamp_channel_width_y / 2,
                   net_clamp_channel_bottom_z])
            cube([net_clamp_channel_void_max_x - net_clamp_channel_void_min_x,
                  net_clamp_channel_width_y,
                  net_clamp_channel_top_z - net_clamp_channel_bottom_z]);
    // The keeper is an integral feature of the fixed post, shown separately
    // here so the otherwise translucent pocket makes the anti-withdrawal path
    // readable in the close-up preview.
    net_clamp_keeper_positive();
    // Display-only +0.1 mm lateral separation normal to the jaw/slot faces
    // avoids a co-planar red/gold overlay. The exported clip and the real
    // assembly remain unshifted.
    translate([0, preview_fit_display_gap, 0])
        net_clamp_clip_positive();
    color("lightgray", 0.65)
        translate([net_clamp_clip_inner_x - 6,
                   -net_sheet_t / 2,
                   net_clamp_channel_bottom_z])
            cube([post_center_x + post_body_width / 2 -
                      (net_clamp_clip_inner_x - 6),
                  net_sheet_t,
                  net_clamp_cylinder_height]);
}

module net_clamp_fit_section_positive() {
    // A real z-section through the installed net edge.  This is intentionally
    // taken from the active post and active U clip, not from a schematic proxy:
    // the gray net ends at the post outer face, while both gold jaws remain
    // inside the red receiving pocket and the crossbar stays outboard.
    section_x = post_center_x - post_body_width / 2 - 12;
    section_width = net_clamp_channel_void_max_x - section_x + 10;
    section_y = -6;
    section_z = 72;
    section_height = 10;
    color("slategray", 0.34)
        intersection() {
            post_segment_positive(0);
            translate([section_x, section_y, section_z])
                cube([section_width, 12, section_height]);
        }
    color("tomato", 0.16)
        intersection() {
            net_clamp_channel_negative_positive();
            translate([section_x, section_y, section_z])
                cube([section_width, 12, section_height]);
        }
    color("goldenrod", 0.94)
        intersection() {
            // Display-only +0.1 mm lateral separation avoids co-planar faces.
            translate([0, preview_fit_display_gap, 0])
                net_clamp_clip_positive();
            translate([section_x, section_y, section_z])
                cube([section_width, 12, section_height]);
        }
    color("lightgray", 0.9)
        intersection() {
            translate([net_clamp_clip_inner_x - 6,
                       -net_sheet_t / 2,
                       net_clamp_channel_bottom_z])
                cube([post_center_x + post_body_width / 2 -
                          (net_clamp_clip_inner_x - 6),
                      net_sheet_t,
                      net_clamp_cylinder_height]);
            translate([section_x, section_y, section_z])
                cube([section_width, 12, section_height]);
        }
}

module post_joint_rails_positive() {
    // Male rails are fused into the lower post half. Their y offsets preserve
    // the central net passage, while the tapered shoulders make the upper half
    // self-locating when it is slid down from above.
    for (y_position = post_joint_rail_y_positions)
        dovetail_prism_z(
            post_joint_rail_z0,
            post_joint_rail_height_z,
            post_center_x,
            y_position,
            post_joint_rail_y_depth,
            post_joint_rail_x_base_width,
            post_joint_rail_x_neck_width
        );
}

module post_joint_rail_pockets_negative_positive() {
    // Matching female pockets are open at the bottom of the upper print. The
    // extra clearance is on every side of the PETG slide, not on the net path.
    for (y_position = post_joint_rail_y_positions)
        dovetail_prism_z(
            post_joint_rail_z0 - 0.2,
            post_joint_rail_height_z + 0.4,
            post_center_x,
            y_position,
            post_joint_rail_y_depth + 2 * post_joint_rail_clearance,
            post_joint_rail_x_base_width + 2 * post_joint_rail_clearance,
            post_joint_rail_x_neck_width + 2 * post_joint_rail_clearance
        );
}

module post_joint_lock_bores_negative_positive() {
    // These two M4 bores accept cross bolts after the upper segment has been
    // slid home. The dovetail shoulders carry the post load; bolts only stop
    // the upper segment from sliding back out.
    for (y_position = post_joint_rail_y_positions)
        m4_cylinder_x(
            m4_joint_bolt_clearance_d,
            post_body_width + 12,
            post_center_x,
            y_position,
            post_joint_lock_z
        );
}

module post_interface_transition_positive() {
    // One closed solid truncated-pyramid transition. The bottom face is the
    // C-clamp contact plane (z=16 mm); there is no lower insertion section.
    // The four taper faces finish exactly at the nominal 28 x 38 mm upper-post
    // section 30 mm above the contact plane.
    polyhedron(
        points = [
            [post_interface_transition_outer_min_x,
             post_interface_transition_outer_min_y,
             post_interface_transition_start_z],
            [post_interface_transition_outer_max_x,
             post_interface_transition_outer_min_y,
             post_interface_transition_start_z],
            [post_interface_transition_outer_max_x,
             post_interface_transition_outer_max_y,
             post_interface_transition_start_z],
            [post_interface_transition_outer_min_x,
             post_interface_transition_outer_max_y,
             post_interface_transition_start_z],
            [post_center_x - post_body_width / 2,
             -post_body_depth / 2,
             post_interface_transition_top_z],
            [post_center_x + post_body_width / 2,
             -post_body_depth / 2,
             post_interface_transition_top_z],
            [post_center_x + post_body_width / 2,
             post_body_depth / 2,
             post_interface_transition_top_z],
            [post_center_x - post_body_width / 2,
             post_body_depth / 2,
             post_interface_transition_top_z]
        ],
        faces = [
            [0, 3, 2, 1],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7]
        ],
        convexity = 10
    );
}

module post_continuous_envelope_positive() {
    // One watertight polyhedron carries the complete fixed-net upright without
    // coincident Boolean seams: a broad 35 x 58 mm footprint starts on the
    // gray/yellow C-clamp seat, tapers continuously for 30 mm, and then keeps
    // the nominal 28 x 38 mm section to the full active post_top datum.
    // There is no lower insertion ring, shoe, collar, or hidden post segment.
    polyhedron(
        points = [
            // broad C-clamp contact footprint, z = post_bottom = seat z
            [post_interface_transition_outer_min_x,
             post_interface_transition_outer_min_y, post_bottom],
            [post_interface_transition_outer_max_x,
             post_interface_transition_outer_min_y, post_bottom],
            [post_interface_transition_outer_max_x,
             post_interface_transition_outer_max_y, post_bottom],
            [post_interface_transition_outer_min_x,
             post_interface_transition_outer_max_y, post_bottom],
            // nominal upper footprint, z = start + 30 mm
            [post_center_x - post_body_width / 2,
             -post_body_depth / 2, post_interface_transition_top_z],
            [post_center_x + post_body_width / 2,
             -post_body_depth / 2, post_interface_transition_top_z],
            [post_center_x + post_body_width / 2,
             post_body_depth / 2, post_interface_transition_top_z],
            [post_center_x - post_body_width / 2,
             post_body_depth / 2, post_interface_transition_top_z],
            // flat top, same upper footprint
            [post_center_x - post_body_width / 2,
             -post_body_depth / 2, active_post_top_z],
            [post_center_x + post_body_width / 2,
             -post_body_depth / 2, active_post_top_z],
            [post_center_x + post_body_width / 2,
             post_body_depth / 2, active_post_top_z],
            [post_center_x - post_body_width / 2,
             post_body_depth / 2, active_post_top_z]
        ],
        faces = [
            // OpenSCAD's polyhedron winding is ordered for outward normals.
            // Keep the broad seat, taper and constant upper rings in one shell
            // so WebGL FrontSide rendering cannot make the post look incomplete.
            [0, 1, 2, 3],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [4, 5, 9, 8],
            [5, 6, 10, 9],
            [6, 7, 11, 10],
            [7, 4, 8, 11],
            [8, 11, 10, 9]
        ],
        convexity = 10
    );
}

module post_body_positive() {
    // The active upright is one continuous PETG body. It starts on the fixed
    // C-clamp seat, tapers for 30 mm from that plane, and ends at post_top. The
    // net passage and wider U-clip receiving pocket are cut only through the
    // net-height zone from this solid; the upper section remains solid.
    // this solid; there is no shoe, pants/crotch part, external ring, or lower
    // insertion into the C-clamp.
    color("goldenrod")
        union() {
            difference() {
                post_continuous_envelope_positive();
                // These two voids are continuous through the full post body.
                // The net is inserted before the separate U-shaped clip is
                // slid on. The keeper is added below, after the channel cut,
                // because it must occupy the channel as fused post material.
                net_passage_negative_positive();
                net_clamp_channel_negative_positive();
                // The central M8 tap pilot is cut from the flat post top. It is
                // the only optical-support interface: the purchased downward
                // M8 stud enters this hole, while the whole load path remains
                // in the same printed/CNC post. No external boss or bridge is
                // emitted here.
                if (m6_detector_direct_mount_enabled)
                    m6_cylinder_z(
                        m6_detector_direct_mount_thread_tap_d,
                        m6_detector_direct_mount_thread_depth_z,
                        m6_detector_direct_mount_socket_center_x,
                        m6_detector_body_center_y,
                        m6_detector_direct_mount_socket_center_z);
            }
            // A single integrated passive keeper is the only anti-withdrawal
            // feature. It is not a separate printed part and does not carry
            // the net/rope tension load.
            net_clamp_keeper_positive();
        }
}

module post_down_extension_stage1_raw_positive() {
    // Over-sized stock for the first modeling operation: pull the current
    // lower post face straight down to the existing foot-bottom datum. This
    // block is a diagnostic stock volume, not a released print part.
    translate([
        post_down_extension_stage1_raw_min_x,
        -post_down_extension_stage1_depth_y / 2,
        post_down_extension_stage1_bottom_z
    ])
        cube([
            post_down_extension_stage1_raw_max_x -
                post_down_extension_stage1_raw_min_x,
            post_down_extension_stage1_depth_y,
            post_down_extension_stage1_height_z
        ]);
}

module post_down_extension_stage1_green_profile_positive() {
    // The user's green outline is the x-z section viewed toward the table
    // center. Keep that section intact and extrude it only along y. The eased
    // upper boundary removes the rectangular stock gradually; there are no
    // y-separated legs, blue shoe solids, center ties, or 15 mm directional
    // offsets in this checkpoint candidate.
    points = concat(
        [
            [post_down_extension_stage1_top_min_x,
             post_down_extension_stage1_top_z],
            [post_down_extension_stage1_top_max_x,
             post_down_extension_stage1_top_z]
        ],
        [
            for (i = [1:post_down_extension_stage1_profile_section_count])
                let(
                    z = post_down_extension_stage1_top_z -
                        post_down_extension_stage1_height_z *
                            i / post_down_extension_stage1_profile_section_count
                )
                [post_down_extension_stage1_green_max_x(z), z]
        ],
        [
            [post_down_extension_stage1_bottom_min_x,
             post_down_extension_stage1_bottom_z]
        ],
        [
            for (i = [1:post_down_extension_stage1_profile_section_count - 1])
                let(
                    z = post_down_extension_stage1_bottom_z +
                        post_down_extension_stage1_height_z *
                            i / post_down_extension_stage1_profile_section_count
                )
                [post_down_extension_stage1_green_min_x(z), z]
        ]
    );
    rotate([90, 0, 0])
        linear_extrude(
            height = post_down_extension_stage1_depth_y,
            center = true,
            convexity = 10
        )
            polygon(points = points);
}

module post_down_extension_stage1_positive() {
    // The only geometry exported for this checkpoint is the green-profile
    // extension. It remains independent from the formal post and C-clamp.
    color("limegreen")
        post_down_extension_stage1_green_profile_positive();
}

module post_skp_yz_prism_positive(profile, x_start, length_x) {
    // linear_extrude is local-z by definition.  This rotation maps the local
    // profile axes [y,z] to world [y,z] and the extrusion direction to world
    // +x, matching the native SketchUp coordinate frame exactly.
    translate([
        post_skp_leg_foot_origin_x + x_start,
        post_skp_leg_foot_origin_y,
        post_skp_leg_foot_origin_z
    ])
        rotate([90, 0, 90])
            linear_extrude(height = length_x,
                           center = false,
                           convexity = 10)
                polygon(points = profile);
}

module post_skp_terminal_xz_limit_positive(y_min, y_max) {
    // Keep the lower support line flat at SKP z=0 and remove only the upper
    // corner at the x=-15 mm terminal.  The remaining end face is therefore
    // chamfered instead of ending as the original straight vertical cut.
    translate([
        post_skp_leg_foot_origin_x - post_skp_leg_foot_side_extension_x,
        post_skp_leg_foot_origin_y + y_max,
        post_skp_leg_foot_origin_z
    ])
        rotate([90, 0, 0])
            linear_extrude(height = y_max - y_min,
                           center = false,
                           convexity = 10)
                polygon(points = [
                    [0, 0],
                    [post_skp_leg_foot_side_extension_x, 0],
                    [post_skp_leg_foot_side_extension_x,
                     post_skp_leg_foot_side_height_z],
                    [post_skp_leg_foot_terminal_chamfer_x,
                     post_skp_leg_foot_side_height_z],
                    [0,
                     post_skp_leg_foot_side_height_z -
                         post_skp_leg_foot_terminal_chamfer_z]
                ]);
}

module post_skp_group2_positive() {
    // Group#2 end-face loop, copied from the supplied SKP in mm.  The
    // concave profile intentionally retains the central y=23.5..33.5,
    // z=0..12 opening; it is not two separate devices.
    post_skp_yz_prism_positive([
        [33.5, 0],
        [46.5, 0],
        [40.5, 7],
        [40.5, 20],
        [16.5, 20],
        [16.5, 7],
        [10.5, 0],
        [23.5, 0],
        [23.5, 12],
        [33.5, 12]
    ], 0, post_skp_leg_foot_main_length_x);
}

module post_skp_group3_raw_positive() {
    // Group#3 is the upper-y symmetric side shoe in the supplied SKP.
    post_skp_yz_prism_positive([
        [33.5, 0],
        [33.5, post_skp_leg_foot_side_height_z],
        [40.5, post_skp_leg_foot_side_height_z],
        [46.5, 0]
    ], -post_skp_leg_foot_side_extension_x,
       post_skp_leg_foot_side_extension_x);
}

module post_skp_group4_raw_positive() {
    // Group#4 is the lower-y symmetric side shoe in the supplied SKP.
    post_skp_yz_prism_positive([
        [10.5, 0],
        [16.5, post_skp_leg_foot_side_height_z],
        [23.5, post_skp_leg_foot_side_height_z],
        [23.5, 0]
    ], -post_skp_leg_foot_side_extension_x,
       post_skp_leg_foot_side_extension_x);
}

module post_skp_group3_chamfered_positive() {
    intersection() {
        post_skp_group3_raw_positive();
        post_skp_terminal_xz_limit_positive(33.5, 46.5);
    }
}

module post_skp_group4_chamfered_positive() {
    intersection() {
        post_skp_group4_raw_positive();
        post_skp_terminal_xz_limit_positive(10.5, 23.5);
    }
}

module post_skp_leg_foot_stage1_raw_positive() {
    // Exact lower-device geometry from SKP Groups #2/#3/#4, before the
    // explicitly requested terminal chamfer.  This is still one device; the
    // symmetric groups are joined at their shared x=0 interface.
    color("limegreen")
        union() {
            post_skp_group2_positive();
            post_skp_group3_raw_positive();
            post_skp_group4_raw_positive();
        }
}

module post_skp_leg_foot_stage1_positive() {
    // Printable checkpoint: the SKP lower device with a 3 x 3 mm 45-degree
    // upper leading chamfer on both 15 mm terminal shoes.  The C-clamp is
    // deliberately absent until the user accepts this shape.
    color("limegreen")
        union() {
            post_skp_group2_positive();
            post_skp_group3_chamfered_positive();
            post_skp_group4_chamfered_positive();
        }
}

module post_skp_leg_foot_fit_tool_positive() {
    // Build one subtractive tool from the visible yellow lower transition and
    // the green SKP lower device.  Keep the boolean operands as the original
    // closed solids: applying Minkowski to this concave, overlapping compound
    // makes CGAL 6.1 return an empty Nef object on the current macOS build.
    // Apply the clearance to each closed primitive separately.  A single
    // Minkowski around the concave, overlapping compound makes CGAL 6.1
    // return an empty Nef object on the current macOS build; split operands
    // retain the same silhouette while keeping the boolean robust.
    union() {
        minkowski() {
            post_skp_group2_positive();
            cube([
                2 * post_skp_leg_foot_fit_clearance,
                2 * post_skp_leg_foot_fit_clearance,
                2 * post_skp_leg_foot_fit_clearance
            ], center = true);
        }
        minkowski() {
            post_skp_group3_chamfered_positive();
            cube([
                2 * post_skp_leg_foot_fit_clearance,
                2 * post_skp_leg_foot_fit_clearance,
                2 * post_skp_leg_foot_fit_clearance
            ], center = true);
        }
        minkowski() {
            post_skp_group4_chamfered_positive();
            cube([
                2 * post_skp_leg_foot_fit_clearance,
                2 * post_skp_leg_foot_fit_clearance,
                2 * post_skp_leg_foot_fit_clearance
            ], center = true);
        }
        minkowski() {
            translate([0, 0, -post_skp_leg_foot_fit_cutter_overlap_z])
                post_interface_transition_positive();
            cube([
                2 * post_skp_leg_foot_fit_clearance,
                2 * post_skp_leg_foot_fit_clearance,
                2 * post_skp_leg_foot_fit_clearance
            ], center = true);
        }
    }
}

module clamp_body_skp_leg_foot_fit_positive() {
    // The gray C-clamp remains the base part.  Only the volume occupied by
    // the combined yellow/green seating region is removed; all other clamp
    // walls, the electronics cavity and the tabletop jaws remain unchanged.
    color("slategray")
        difference() {
            clamp_body_segment_positive();
            post_skp_leg_foot_fit_tool_positive();
        }
}

module post_skp_leg_foot_clamp_fit_positive() {
    // Assembly-only candidate: show the actual yellow upright and green SKP
    // lower device seated in the gray C-clamp whose matching pocket was cut
    // from the same combined geometry.  This is not yet the formal print
    // manifest entry until the user accepts the fit.
    clamp_body_skp_leg_foot_fit_positive();
    post_body_positive();
    post_skp_leg_foot_stage1_positive();
}

module post_skp_leg_foot_stage1_exploded_positive() {
    // Show the current upright and the one SKP-derived lower device as two
    // exploded positions.  The red plane marks the shared z datum in both
    // positions; no C-clamp or interference subtraction is included.
    color("red", 0.92)
        translate([
            post_interface_transition_outer_min_x - 8,
            -0.8,
            post_bottom - 0.2
        ])
            cube([
                post_interface_transition_bottom_width_x + 16,
                1.6,
                0.4
            ]);
    post_body_positive();

    translate([
        post_skp_leg_foot_exploded_offset_x,
        preview_fit_display_gap,
        0
    ]) {
        color("red", 0.92)
            translate([
                post_interface_transition_outer_min_x - 8,
                -0.8,
                post_bottom - 0.2
            ])
                cube([
                    post_interface_transition_bottom_width_x + 16,
                    1.6,
                    0.4
                ]);
        post_skp_leg_foot_stage1_positive();
    }
}

module post_segment_positive(index = 0) {
    // Compatibility entry point: index 0 is now the complete upright.  Any
    // second index is intentionally rejected so old split exports cannot be
    // mistaken for active printable geometry.
    assert(index == 0, "the active upright has one printable segment only");
    post_body_positive();
}

module post_clamp_carrier_positive() {
    // Formal printable assembly part: the complete upright, including the
    // solid lower transition, is one print. Its broad lower face sits on the
    // fixed C-clamp at clamp_slide_seat_z; it does not enter the C-clamp body.
    // The old carrier hook is retained as an empty compatibility module and
    // adds no extra geometry.
    color("goldenrod")
        union() {
            post_body_positive();
            table_clamp_carrier_positive("goldenrod");
        }
}

module lower_stand_segment_positive() {
    // Legacy name retained for old callers; the active replacement is the
    // complete one-piece upright.
    post_clamp_carrier_positive();
}

module upper_stand_segment_positive() {
    // Legacy name retained for old callers; no upper printable segment exists.
    post_body_positive();
}

module post_joint_sleeve_positive() {
    color("darkorange")
        difference() {
            translate([post_center_x - post_body_width / 2 - 5,
                       -post_body_depth / 2 - 4,
                       active_post_joint_z - post_joint_sleeve_h / 2])
                cube([post_body_width + 10, post_body_depth + 8,
                      post_joint_sleeve_h]);
            translate([post_center_x - post_body_width / 2 - post_joint_clearance,
                       -post_body_depth / 2 - post_joint_clearance,
                       active_post_joint_z - post_joint_sleeve_h / 2 - 1])
                cube([post_body_width + 2 * post_joint_clearance,
                      post_body_depth + 2 * post_joint_clearance,
                      post_joint_sleeve_h + 2]);
            for (z_offset = [-m4_joint_bolt_z_offset,
                             m4_joint_bolt_z_offset]) {
                m4_cylinder_y(
                    m4_joint_bolt_clearance_d,
                    post_body_depth + 20,
                    post_center_x,
                    active_post_joint_z + z_offset);
            }
        }
}

module post_joint_key_positive() {
    color("darkorange")
        difference() {
            translate([post_center_x - (post_body_width - 2) / 2,
                       -(post_body_depth - 2) / 2,
                       active_post_joint_z - (post_joint_sleeve_h - 4) / 2])
                cube([post_body_width - 2, post_body_depth - 2,
                      post_joint_sleeve_h - 4]);
            for (z_offset = [-m4_joint_bolt_z_offset,
                             m4_joint_bolt_z_offset]) {
                m4_cylinder_y(
                    m4_joint_bolt_clearance_d,
                    post_body_depth + 8,
                    post_center_x,
                    active_post_joint_z + z_offset);
            }
        }
}

module post_positive() {
    // Standalone view of the complete one-piece upright.  The outboard carrier
    // is intentionally omitted here so PART="post" remains a clean post-body
    // diagnostic; PART="post_clamp_carrier" is the formal print part.
    post_body_positive();
}

module post_clamp_slide_exploded_positive() {
    // Visual-only installation proof for the real one-piece part. The gray
    // inboard clamp body and its fixed seat stay at their datum. A translucent
    // home-position carrier shows the post bottom returning onto that seat;
    // the opaque carrier is then pulled only in +x to show the real slide-out
    // separation. No z lift or second platform is introduced. The 0.1 mm y
    // offset is display-only.
    color("slategray", 0.86)
        clamp_body_segment_positive();
    color("goldenrod", 0.34)
        post_clamp_carrier_positive();
    color("goldenrod", 0.86)
        translate([preview_slide_out_offset_x, preview_fit_display_gap, 0])
        post_clamp_carrier_positive();
}

module post_down_extension_stage1_exploded_positive() {
    // Checkpoint view for the corrected interpretation: the real post stays
    // at the red bottom-plane datum, the gray translucent block is the raw
    // downward pull stock, and the opaque green copy is the x-z profile after
    // excess material is removed. The two candidates are separated in x so
    // the preview itself does not union overlapping diagnostic shells. No
    // C-clamp is included in this view.
    color("red", 0.92)
        translate([
            post_down_extension_stage1_top_min_x - 42,
            -0.8,
            post_down_extension_stage1_top_z - 0.4
        ])
            cube([84, 1.6, 0.8]);
    post_body_positive();
    color("lightgray", 0.18)
        post_down_extension_stage1_raw_positive();
    translate([preview_slide_out_offset_x, preview_fit_display_gap, 0])
        post_down_extension_stage1_positive();
}

module post_clamp_slide_interface_exploded_positive() {
    // Focused lower-interface proof for the current direct seat. The fixed
    // C body and the complete orange post are clipped around the shared plane;
    // the post is then pulled only in +x for a readable service separation.
    section_x = post_interface_transition_outer_min_x - 5;
    section_y = post_interface_transition_outer_min_y - 5;
    section_z = post_bottom - 2;
    section_box = [section_x, section_y, section_z];
    section_size = [
        post_interface_transition_outer_max_x -
            post_interface_transition_outer_min_x + 10,
        post_interface_transition_outer_max_y -
            post_interface_transition_outer_min_y + 10,
        post_interface_transition_height_z + 12
    ];

    // Show only the actual fixed-body material in this slice. The support
    // plane remains gray so the orange lower taper can be seen sitting on it.
    color("slategray", 0.88)
        intersection() {
            clamp_body_segment_positive();
            translate(section_box)
                cube(section_size);
        }
    // Installed carrier, shown at its real datum. It is a single solid lower
    // taper seated on the gray horizontal support; there is no second shoe or
    // hidden rear wrapper.
    color("darkorange", 0.96)
        intersection() {
            post_clamp_carrier_positive();
            translate(section_box)
                cube(section_size);
        }
    // The same one-piece carrier is pulled only in +x for the exploded state.
    color("goldenrod", 0.96)
        intersection() {
            translate([preview_slide_out_offset_x, preview_fit_display_gap, 0])
                post_clamp_carrier_positive();
            translate([preview_slide_out_offset_x, preview_fit_display_gap, 0])
                cube(section_size);
        }
    // Hardware is intentionally omitted from this focused picture so the
    // shared plane and the continuous taper remain unambiguous.
}

module post_clamp_seated_positive() {
    // Final installed reference: the complete upright's flat lowest face is
    // seated directly on the fixed C-clamp's highest horizontal support plane
    // at the shared z=16 mm datum.
    clamp_body_segment_positive();
    post_clamp_carrier_positive();
}

module post_clamp_seated_fit_section_positive() {
    // Focused y-section through the actual seated transition. The section
    // contains one fixed gray support plane and one orange solid taper; there
    // is no foot, rail, collar, or under-seat piece to confuse the datum.
    section_x = post_center_x - 2;
    section_y = post_interface_transition_outer_min_y - 4;
    section_z = post_bottom - 2;
    section_width = 4;
    section_height = post_interface_transition_height_z + 10;
    section_depth = post_interface_transition_outer_max_y -
        post_interface_transition_outer_min_y + 8;
    section_box = [section_x, section_y, section_z];
    section_size = [section_width, section_depth, section_height];

    // Keep fixed-body material separate from the orange carrier.  The prior
    // union painted the installed carrier gray as well, which made a valid
    // open tunnel look like a closed block and obscured the actual entry.
    color("slategray", 0.62)
        intersection() {
            clamp_body_segment_positive();
            translate(section_box)
                cube(section_size);
        }
    color("goldenrod", 0.94)
        intersection() {
            post_clamp_carrier_positive();
            translate(section_box)
                cube(section_size);
        }
}

module post_clamp_entry_open_section_positive() {
    // Diagnostic-only x-normal section at the outboard interface. It is made
    // from the two real solids: gray is the fixed C body and orange is the
    // complete upright. The thin section checks that the upright's lowest
    // face meets the fixed support plane without a hidden rear wrapper or a
    // sealed block behind it.
    section_x = clamp_fixed_body_max_x - 3;
    section_width = 2.5;
    section_z = clamp_slide_rail_floor_z - 2;
    section_box = [
        section_x,
        -clamp_pad_depth / 2 - 1,
        section_z
    ];
    section_size = [
        section_width,
        clamp_pad_depth + 2,
        clamp_slide_seat_z - section_z + 5
    ];

    // Only material intersecting this thin slab is shown; no colored proxy or
    // extra locating block is added.
    color("slategray", 0.78)
        intersection() {
            clamp_body_segment_positive();
            translate(section_box)
                cube(section_size);
        }
    color("darkorange", 0.98)
        intersection() {
            post_clamp_carrier_positive();
            translate(section_box)
                cube(section_size);
        }
}

// Diagnostic-only solid intersection.  A correctly seated carrier may touch
// the fixed body at the seat and in the captured slideways, but it must not
// occupy any of the fixed body's material volume.  Exporting this PART gives
// the mechanical self-check a direct, measurable collision volume instead of
// relying on a translucent preview.
module post_clamp_fit_collision_probe_positive() {
    intersection() {
        clamp_body_segment_positive();
        post_clamp_carrier_positive();
    }
}

module post_clamp_fit_collision_probe_at_offset_positive() {
    intersection() {
        clamp_body_segment_positive();
        translate([fit_probe_offset_x, 0, 0])
            post_clamp_carrier_positive();
    }
}

// Compatibility preview name.  It no longer depicts a post joint.
module post_joint_exploded_positive() {
    post_clamp_slide_exploded_positive();
}

module post_joint_exploded(side = 1) {
    sided(side) post_clamp_slide_exploded_positive();
}

// -----------------------------------------------------------------------------
// 当前 M6 十路 PETG 主体、后盖 boss 与采购球头微调接口
//
// 机械契约：当前首样用可打印 PETG 长方条主体和 PETG 前后底盖；后续可将
// 同一主体包络改为 CNC。当前承力路径是：M6×0.75 器件六角/主体 ->
// 10×56×216 mm 长方条 -> 后盖 x 背面中央加厚 boss -> 采购 13 mm 球头上端 1/4-20 外牙；
// 球头 z- 下端 M8 与固定网柱断开，独立光学支撑尚待定义。采购球头提供偏航/俯仰/滚转微调；
// 前后壳和底盖只负责保护、导向和线缆出口，后盖 boss 的首样强度须用实物固定件验证。

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

module m4_cylinder_y(d, h, x_center, z_center) {
    // Transverse clearance bore for the two standard M4 joint lock screws.
    translate([x_center, 0, z_center])
        rotate([90, 0, 0])
            cylinder(d = d, h = h, center = true);
}

module m4_cylinder_x(d, h, x_center, y_center, z_center) {
    translate([x_center, y_center, z_center])
        rotate([0, 90, 0])
            cylinder(d = d, h = h, center = true);
}

module m4_cylinder_z(d, h, x_center, y_center, z_center) {
    translate([x_center, y_center, z_center])
        cylinder(d = d, h = h, center = true);
}

// A constant cross-section dovetail prism whose sliding axis is x. Retained
// for the older post-joint diagnostics; the active clamp interface below uses
// the wider, broad-head/narrow-neck interlocking slide prism instead.
module dovetail_prism_x(
    x0,
    length,
    y_center,
    z_center,
    y_depth,
    z_base_width,
    z_neck_width
) {
    translate([x0, y_center, z_center])
        rotate([0, 90, 0])
            linear_extrude(height = length)
                polygon(points = [
                    [-z_base_width / 2, -y_depth / 2],
                    [z_base_width / 2, -y_depth / 2],
                    [z_neck_width / 2, y_depth / 2],
                    [-z_neck_width / 2, y_depth / 2]
                ]);
}

// A constant cross-section captured slideway whose sliding axis is x. The
// broad head is at the lower z seat and the narrower neck rises above it. The
// matching female cut therefore leaves material both below and above the
// runner, with side capture along the two sloped shoulders. This is the
// clamp's actual active interface: it behaves like two broad interlocking
// tracks, not two exposed rods inserted into holes.
module interlocking_slide_prism_x(
    x0,
    length,
    y_center,
    z_floor,
    y_head_width,
    y_neck_width,
    head_height,
    neck_height
) {
    translate([x0, y_center, z_floor])
        rotate([0, 90, 0])
            linear_extrude(height = length)
                polygon(points = [
                    [0, -y_head_width / 2],
                    [0, y_head_width / 2],
                    [-head_height, y_head_width / 2],
                    [-(head_height + neck_height), y_neck_width / 2],
                    [-(head_height + neck_height), -y_neck_width / 2],
                    [-head_height, -y_head_width / 2]
                ]);
}

// A vertical dovetail prism used at the post seam. Its two side rails are
// deliberately offset from y=0 so the net's through-passage stays open.
module dovetail_prism_z(
    z0,
    height,
    x_center,
    y_center,
    y_depth,
    x_base_width,
    x_neck_width
) {
    translate([x_center, y_center, z0])
        linear_extrude(height = height)
            polygon(points = [
                [-x_base_width / 2, -y_depth / 2],
                [x_base_width / 2, -y_depth / 2],
                [x_neck_width / 2, y_depth / 2],
                [-x_neck_width / 2, y_depth / 2]
            ]);
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

module m6_rounded_rect_prism_z(width_x, depth_y, height_z, radius,
                               x_center, y_center, z_center) {
    // A rounded-rectangle cross section swept along z.  This is the compact
    // black housing envelope used for the purchased 13 mm ballhead; it is not
    // included in any printable-part export.
    hull() {
        for (x_offset = [-width_x / 2 + radius,
                         width_x / 2 - radius]) {
            for (y_offset = [-depth_y / 2 + radius,
                             depth_y / 2 - radius]) {
                m6_cylinder_z(
                    2 * radius,
                    height_z,
                    x_center + x_offset,
                    y_center + y_offset,
                    z_center);
            }
        }
    }
}

module m6_ridged_disc_z(d, h, x_center, y_center, z_center,
                        ridge_count = 24) {
    // Knurled-disc approximation for bought hardware only.  The circular
    // lobes make the preview read like the hand-lock wheel in the reference
    // images without implying that this difficult detail should be printed.
    ridge_d = 1.4;
    ridge_r = d / 2 - ridge_d / 2;
    union() {
        m6_cylinder_z(d - ridge_d, h, x_center, y_center, z_center);
        for (index = [0:ridge_count - 1]) {
            m6_cylinder_z(
                ridge_d,
                h,
                x_center + ridge_r * cos(360 * index / ridge_count),
                y_center + ridge_r * sin(360 * index / ridge_count),
                z_center);
        }
    }
}

module m6_ridged_disc_x(d, h, x_center, y_center, z_center,
                        ridge_count = 24) {
    ridge_d = 1.4;
    ridge_r = d / 2 - ridge_d / 2;
    union() {
        m6_cylinder_x(d - ridge_d, h, x_center, y_center, z_center);
        for (index = [0:ridge_count - 1]) {
            m6_cylinder_x(
                ridge_d,
                h,
                x_center,
                y_center + ridge_r * cos(360 * index / ridge_count),
                z_center + ridge_r * sin(360 * index / ridge_count));
        }
    }
}

module m6_ridged_disc_y(d, h, x_center, y_center, z_center,
                        ridge_count = 24) {
    ridge_d = 1.4;
    ridge_r = d / 2 - ridge_d / 2;
    union() {
        m6_cylinder_y(d - ridge_d, h, x_center, y_center, z_center);
        for (index = [0:ridge_count - 1]) {
            m6_cylinder_y(
                ridge_d,
                h,
                x_center + ridge_r * cos(360 * index / ridge_count),
                y_center,
                z_center + ridge_r * sin(360 * index / ridge_count));
        }
    }
}

module m6_threaded_stud_x(major_d, core_d, length, pitch,
                          x_center, y_center, z_center) {
    // Lightweight visual thread: a core plus overlapping crest rings.  This
    // represents the purchased 1/4-20 stud in the preview only; it is never a
    // replacement for the vendor's rolled thread or a printed thread.
    union() {
        m6_cylinder_x(core_d, length, x_center, y_center, z_center);
        for (offset = [-length / 2 + pitch / 2:pitch:length / 2 - pitch / 2]) {
            m6_cylinder_x(major_d, pitch * 0.36,
                          x_center + offset, y_center, z_center);
        }
    }
}

module m6_threaded_stud_z(major_d, core_d, length, pitch,
                          x_center, y_center, z_center) {
    // Same purchased-thread visual for the downward M8 mounting end.
    union() {
        m6_cylinder_z(core_d, length, x_center, y_center, z_center);
        for (offset = [-length / 2 + pitch / 2:pitch:length / 2 - pitch / 2]) {
            m6_cylinder_z(major_d, pitch * 0.36,
                          x_center, y_center, z_center + offset);
        }
    }
}

// -----------------------------------------------------------------------------
// M6 cover top-view footprints (z+)
//
// The user's sketch is a plan view with the optical/front x- end represented by
// a positive semicircular/elliptic arc and the cable/rear x+ end represented by
// a rear-only rounded profile.  The x- connection edge of the rear cover stays
// straight so it can meet the front cover cleanly.  These are 2-D footprints
// extruded in z; the split is only a cover parting boundary and no center
// cable/bridge line is modeled.

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
    rear_min_x = m6_detector_shell_rear_min_x;
    rear_max_x = m6_detector_shell_max_x;
    min_y = m6_detector_shell_min_y;
    max_y = m6_detector_shell_max_y;
    radius = min(
        m6_detector_shell_corner_radius,
        (rear_max_x - rear_min_x) / 2,
        (max_y - min_y) / 2
    );

    // Keep the x- split edge square.  Only the two x+ rear corners are
    // rounded, matching the requested top-view silhouette.
    polygon(points = concat(
        [
            [rear_min_x, min_y],
            [rear_max_x - radius, min_y]
        ],
        [
            for (angle = [-90:5:0])
                [
                    rear_max_x - radius + radius * cos(angle),
                    min_y + radius + radius * sin(angle)
                ]
        ],
        [
            [rear_max_x, max_y - radius]
        ],
        [
            for (angle = [0:5:90])
                [
                    rear_max_x - radius + radius * cos(angle),
                    max_y - radius + radius * sin(angle)
                ]
        ],
        [
            [rear_min_x, max_y]
        ]
    ));
}

module m6_detector_shell_footprint_positive() {
    union() {
        m6_detector_front_arc_footprint_positive();
        m6_detector_rear_rounded_footprint_positive();
        // The one-piece bottom cover bridges the 0.4 mm cover parting gap;
        // the front and rear side covers remain independently removable.
        translate([m6_detector_shell_front_max_x,
                   m6_detector_shell_min_y])
            square([
                m6_detector_shell_rear_min_x -
                    m6_detector_shell_front_max_x,
                m6_detector_shell_width_y]);
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
    // Compatibility entry point.  Keep the standalone historical name tied
    // to the same realistic purchased-hardware envelope as the active mount.
    m6_detector_ballhead_positive();
}

module m6_ballhead_mount_positive() {
    // Compatibility entry point now follows the current assembly.  The old
    // adapter plate/backplate and their gold through-bolts are deliberately
    // not part of any current M6 mount preview.
    m6_detector_mount_positive();
}

// -----------------------------------------------------------------------------
// 当前主体主线：L 型 M6 传感器 + x 轴 45° 让线旋转
//
// The optical channel and M6 threaded barrel remain on the x axis. In the
// local sensor frame the blue cable guard exits z-, then the complete
// purchased-device proxy is rolled -45° about x; that cable branch therefore
// points toward y-/z-. The active aperture is the hollow threaded-barrel tip;
// there is no separate black optical face on the gray hex.
// The active body is a solid, wide y-direction PETG-printable carrier centered
// at y=0. It has ten optical/head openings and shallow rear hex seats. The M6
// thread is a simple clearance pass-through; one purchased nut sits on the
// outside face. The cable stays outside the body and is not pocketed. The same
// rectangular envelope can later be machined from CNC stock.

module m6_sensor_roll_frame(index) {
    z0 = m6_sensor_z(index);
    translate([m6_sensor_axis_x, 0, z0])
        rotate([m6_sensor_roll_deg, 0, 0])
            translate([-m6_sensor_axis_x, 0, -z0])
                children();
}

module m6_detector_body_envelope_positive() {
    // The active body deliberately remains a simple 10 x 56 x 216 mm bar.
    // The rear-cover boss is a separate PETG part and is not fused into this
    // body envelope.
    translate([m6_detector_body_min_x,
               m6_detector_body_min_y,
               m6_detector_body_bottom_z])
        cube([m6_detector_body_length_x,
              m6_detector_body_depth_y,
              m6_detector_body_height_z]);
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
    color("lightsteelblue")
        difference() {
            m6_detector_body_envelope_positive();

            m6_detector_sensor_fit_voids_positive();

            // Do not cut a diagonal cable trench into the PETG/CNC body. The
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
// long rectangular PETG-printable bar and the real purchased L-shaped sensor model:
// gray hex head, hollow M6 optical barrel, blue right-angle guard, and short
// cable proxy.  The head enters from the outward face, overlaps the body by
// 2 mm, and stops there; one supplied lock nut is placed on the smooth inner
// body face. Covers, screws, brackets, and gimbals remain outside this probe.
module m6_detector_fit_body_positive() {
    color("lightsteelblue")
        difference() {
            m6_detector_body_envelope_positive();

            m6_detector_sensor_fit_voids_positive();
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
    // The M6 thread simply passes through the rectangular carrier. Only one
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
    // Each y edge has one continuous vertical groove in the rectangular body.
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
    // Its rear x+ face also owns an integral thickened PETG boss for the M8
    // ballhead stud.  The boss is centered in y and z, part of the rear cover,
    // not a hidden body tail or a separate gray adapter plate.
    union() {
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
        m6_detector_shell_support_boss_positive();
    }
}

module m6_detector_shell_support_boss_positive() {
    // Thickened rear-cover seat for the purchased 13 mm ballhead.  The
    // rounded outside avoids a sharp PETG stress riser; the hole is cut in
    // the rear-cover difference below and therefore remains a true through
    // clearance hole for the 1/4-20 external stud.
    m6_rounded_rect_prism_x(
        m6_detector_shell_support_boss_length_x,
        m6_detector_shell_support_boss_depth_y,
        m6_detector_shell_support_boss_height_z,
        m6_detector_shell_support_boss_radius,
        m6_detector_shell_support_boss_center_x,
        m6_detector_shell_support_boss_center_y,
        m6_detector_shell_support_boss_center_z);
}

module m6_detector_shell_support_hole_positive() {
    // The fixed upper stud on the purchased ballhead is 1/4-20 UNC, not M8.
    // Leave a printable clearance bore and capture one standard 1/4-20 metal
    // nut from the boss's inner side.  The nut pocket is deliberately hidden
    // inside the thick boss, so the PETG shell never carries a hand-tapped
    // thread or the main bending moment by itself.
    m6_cylinder_x(
        m6_detector_shell_support_hole_d,
        m6_detector_shell_support_hole_depth_x + 2,
        m6_detector_shell_support_hole_entry_x -
            m6_detector_shell_support_hole_depth_x / 2,
        m6_detector_shell_support_boss_center_y,
        m6_detector_shell_support_boss_center_z);
    m6_hex_prism_x(
        m6_ballhead_top_nut_pocket_af,
        m6_ballhead_top_nut_pocket_depth,
        m6_detector_shell_support_nut_pocket_center_x,
        m6_detector_shell_support_boss_center_y,
        m6_detector_shell_support_boss_center_z);
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

module m6_detector_shell_front_positive(alpha = m6_detector_shell_alpha) {
    // Front is the optical x- end. It keeps the positive spherical arc, spans
    // full y, owns the x- half of both side grooves, and is installed/removed
    // by sliding from z+ before the rear cover. It is fixed from x- by two
    // countersunk screws on the y+ screw track; the screws only clamp the
    // removable cover to the body's pilot holes.
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
    // half of both side grooves, and has a centered rear-face boss with an
    // x-axis 1/4-20 clearance hole for the purchased ballhead. It is fixed from
    // x+ by two countersunk screws on the y- track. During assembly it is
    // installed/removed by sliding from z+ after the front cover; its boss is
    // only the cover-side seat for the ballhead's horizontal M8 stud. The
    // ballhead's downward interface is carried by the straight post-centred
// support below; this rear cover has no horizontal support arm.
    union() {
        color("slategray", alpha)
            difference() {
                m6_detector_shell_rear_outer_positive();
                m6_detector_shell_inner_segment_positive(
                    m6_detector_shell_rear_min_x - 1,
                    m6_detector_shell_inner_max_x + 1);
                m6_detector_shell_support_hole_positive();
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
        // The cavity subtraction above would otherwise leave only the thin
        // rear wall between the boss and the shell.  Add two y-side triangular
        // ribs afterward so the boss has a continuous PETG load path; their
        // roots begin outside the central Ø7 support bore.
        m6_detector_shell_support_gussets_positive();
        for (y_side = [-1, 1])
            m6_detector_shell_tongue_positive(1, y_side);
    }
}

module m6_detector_shell_support_gussets_positive(alpha = m6_detector_shell_alpha) {
    color("slategray", alpha)
        for (y_side = [-1, 1]) {
            hull() {
                translate([
                    m6_detector_shell_support_gusset_min_x,
                    y_side > 0
                        ? m6_detector_shell_support_gusset_root_y_start_positive
                        : m6_detector_shell_support_boss_min_y,
                    m6_detector_shell_support_gusset_bottom_z
                ])
                    cube([
                        m6_detector_shell_support_gusset_max_x -
                            m6_detector_shell_support_gusset_min_x,
                        m6_detector_shell_support_gusset_root_width_y,
                        m6_detector_shell_support_gusset_height_z
                    ]);
                translate([
                    m6_detector_shell_support_gusset_min_x,
                    y_side > 0
                        ? m6_detector_shell_support_gusset_wall_y_start_positive
                        : m6_detector_shell_min_y,
                    m6_detector_shell_support_gusset_bottom_z
                ])
                    cube([
                        m6_detector_shell_support_gusset_max_x -
                            m6_detector_shell_support_gusset_min_x,
                        m6_detector_shell_support_gusset_wall_width_y,
                        m6_detector_shell_support_gusset_height_z
                    ]);
            }
    }
}

module m6_detector_cable_gland_positive(alpha = 0.90) {
    // A replaceable multi-hole cable gland/strain-relief collar sits below
    // the bottom cover. The opening is intentionally larger than one wire so
    // the final part can use a sealed 10/20-wire insert or be potted after the
    // harness is tested; it is not left as a naked open hole in the enclosure.
    color("black", alpha)
        difference() {
            translate([
                m6_detector_cable_exit_x,
                m6_detector_cable_exit_y,
                m6_detector_shell_bottom_z -
                    m6_detector_bottom_cover_t -
                    m6_detector_cable_gland_length_z])
                cylinder(
                    d = m6_detector_cable_gland_outer_d,
                    h = m6_detector_cable_gland_length_z + 0.3);
            m6_cylinder_z(
                m6_detector_cable_exit_d +
                    2 * m6_detector_cable_exit_sleeve_clearance,
                m6_detector_cable_gland_length_z + 3,
                m6_detector_cable_exit_x,
                m6_detector_cable_exit_y,
                m6_detector_shell_bottom_z -
                    m6_detector_bottom_cover_t -
                    m6_detector_cable_gland_length_z / 2);
        }
}

module m6_detector_cable_trunk_positive() {
    // The trunk is held just outside the y- shell wall. A 1.2 mm gap keeps the
    // wire guide from rubbing on the removable cover while the individual
    // branches remain visible for service and channel labeling.
    color("navy", 0.68)
        translate([
            m6_detector_cable_trunk_x -
                m6_detector_cable_trunk_width_x / 2,
            m6_detector_cable_trunk_y -
                m6_detector_cable_trunk_depth_y / 2,
            m6_detector_body_bottom_z + 4])
            cube([
                m6_detector_cable_trunk_width_x,
                m6_detector_cable_trunk_depth_y,
                m6_detector_body_height_z - 8]);
}

module m6_detector_cable_branch_positive(index) {
    z0 = m6_sensor_z(index);
    // After the -45 degree sensor roll the blue strain-relief exits toward
    // y-/z-. This straight branch is a service-routing reference, not a claim
    // that the purchased cable is rigid or exactly this bend radius.
    branch_z = z0 - 8;
    color("black", 0.82)
        m6_cylinder_y(
            m6_detector_cable_branch_d,
            abs(m6_detector_cable_trunk_y -
                m6_detector_sensor_body_center_y),
            m6_detector_cable_trunk_x,
            (m6_detector_cable_trunk_y +
             m6_detector_sensor_body_center_y) / 2,
            branch_z);
    color("royalblue", 0.84)
        translate([
            m6_detector_cable_trunk_x - 1.5,
            m6_detector_cable_trunk_y -
                m6_detector_cable_trunk_depth_y / 2 - 0.8,
            z0 - m6_detector_cable_clip_t / 2])
            cube([
                3,
                m6_detector_cable_trunk_depth_y + 1.6,
                m6_detector_cable_clip_t]);
}

module m6_detector_cable_routing_reference_positive() {
    // Ten labeled channels converge on one side-specific trunk. The positive
    // assembly is the right receiver; SIDE=-1 mirrors this entire reference
    // to the left emitter without changing the optical axis.
    m6_detector_cable_trunk_positive();
    for (index = [0:m6_sensor_count - 1])
        m6_detector_cable_branch_positive(index);
    color("black", 0.78)
        m6_cylinder_y(
            m6_detector_cable_branch_d,
            abs(m6_detector_cable_exit_y -
                m6_detector_cable_trunk_y),
            m6_detector_cable_trunk_x,
            (m6_detector_cable_exit_y +
             m6_detector_cable_trunk_y) / 2,
            m6_detector_shell_bottom_z -
                m6_detector_bottom_cover_t -
                m6_detector_cable_gland_length_z / 2);
    m6_detector_cable_gland_positive();
}

module m6_detector_bottom_gasket_positive() {
    // Separate orange gasket reference for the one-piece bottom cover. It
    // follows the shell footprint rather than leaving four independent strips.
    color("orange", 0.72)
        translate([0, 0, m6_detector_shell_bottom_z + 0.08])
            linear_extrude(height = m6_detector_shell_gasket_height)
                difference() {
                    offset(delta = m6_detector_shell_gasket_clearance +
                           m6_detector_shell_gasket_width / 2)
                        m6_detector_shell_footprint_positive();
                    offset(delta = -m6_detector_shell_gasket_width / 2)
                        m6_detector_shell_footprint_positive();
                }
}

module m6_detector_bottom_cover_positive() {
    union() {
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
        m6_detector_cable_gland_positive();
    }
}

module m6_detector_ballhead_positive() {
    // Purchased 13 mm mini ballhead in the required vertical posture.  The
    // black clamp body and silver ball are only an assembly/fit envelope.  The
    // ball is opened so its fixed upper 1/4-20 male stud points x- into the
    // detector rear boss; the selected lower M8 male stud points z- into the
    // straight same-material PETG post.  The top plate, lock wheel and knurled base
    // make the product read like the referenced hardware instead of a stack of
    // anonymous cylinders.
    body_x = m6_detector_ballhead_center_x;
    body_y = m6_detector_ballhead_center_y;
    body_z = m6_detector_ballhead_center_z;
    body_left_x = body_x - m6_ballhead_housing_d / 2;
    body_top_z = body_z + m6_ballhead_housing_length_x / 2;
    lock_knob_y = body_y - m6_ballhead_body_depth_y / 2 -
        m6_ballhead_lock_knob_t_y / 2 + 1;

    color("black")
        difference() {
            m6_rounded_rect_prism_z(
                m6_ballhead_housing_d,
                m6_ballhead_body_depth_y,
                m6_ballhead_housing_length_x,
                m6_ballhead_body_corner_radius,
                body_x,
                body_y,
                body_z);
            // Socket clearance and a top window expose the purchased metal
            // ball while leaving a substantial lower clamp body.
            translate([body_x, body_y, body_z])
                sphere(d = m6_ballhead_ball_socket_d, $fn = 48);
            translate([body_x, body_y,
                       body_top_z - m6_ballhead_housing_length_x / 4])
                cube([m6_ballhead_housing_d + 4,
                      m6_ballhead_body_depth_y + 4,
                      m6_ballhead_housing_length_x / 2],
                     center = true);
        }

    color("silver")
        translate([body_x, body_y, body_z])
            sphere(d = m6_ballhead_ball_d, $fn = 48);

    // Removable round plate / neck at the x- side, as seen in the vendor
    // images.  Its centerline is the upper movable 1/4-20 interface.
    color("black")
        m6_ridged_disc_x(
            m6_ballhead_side_plate_d,
            m6_ballhead_side_plate_t_x,
            body_left_x,
            body_y,
            body_z,
            24);
    color("silver")
        m6_cylinder_x(
            10,
            2.2,
            body_left_x - m6_ballhead_side_plate_t_x / 2 - 0.5,
            body_y,
            body_z);
    color("silver")
        m6_threaded_stud_x(
            m6_ballhead_sensor_stud_d,
            m6_ballhead_sensor_thread_core_d,
            m6_ballhead_sensor_stud_length,
            m6_ballhead_sensor_thread_pitch,
            m6_detector_ballhead_sensor_stud_center_x,
            body_y,
            body_z);

    // The side lock wheel is normal to y- and is intentionally offset one mm
    // into the body so the bought part reads as one connected mechanism.
    color("black")
        m6_ridged_disc_y(
            m6_ballhead_lock_knob_d,
            m6_ballhead_lock_knob_t_y,
            body_x,
            lock_knob_y,
            body_z,
            m6_ballhead_lock_knob_ridge_count);

    color("black")
        m6_ridged_disc_z(
            m6_ballhead_base_d,
            m6_ballhead_base_t,
            body_x,
            body_y,
            m6_detector_ballhead_base_center_z,
            32);
    color("silver")
        m6_cylinder_z(
            13,
            2,
            body_x,
            body_y,
            m6_detector_ballhead_base_center_z + m6_ballhead_base_t / 2 - 1);
    color("silver")
        m6_threaded_stud_z(
            m6_ballhead_net_stud_d,
            m6_ballhead_net_thread_core_d,
            m6_ballhead_net_stud_length,
            m6_ballhead_net_thread_pitch,
            body_x,
            body_y,
            m6_detector_ballhead_net_stud_center_z);
}

module m6_detector_net_connector_positive() {
    // Legacy-only purchased metal 90-degree bridge.  It is retained as a
    // compatibility diagnostic PART, but is deliberately not called by any
    // current assembly or print export.
    // The socket surrounds the downward M8 stud from its lowest end, the
    // horizontal arm starts at that same lowest interface datum and reaches
    // the net-frame upright's inner x face, and the vertical leg directly
    // attaches to the existing pair of x-through slots. There is no adapter
    // plate between the purchased connector and the upright. This is a
    // visual envelope for the bought connector: it is intentionally not a
    // PETG printable part and carries the support load through its metal body
    // and the two M6 through-bolts directly into the net-frame upright.
    color("dimgray")
        difference() {
            union() {
                translate([
                    m6_detector_net_connector_arm_min_x,
                    -m6_detector_net_connector_arm_width_y / 2,
                    m6_detector_net_connector_arm_bottom_z])
                    cube([
                        m6_detector_net_connector_arm_max_x -
                            m6_detector_net_connector_arm_min_x,
                        m6_detector_net_connector_arm_width_y,
                        m6_detector_net_connector_arm_t_z]);
                translate([
                    m6_detector_net_connector_leg_min_x,
                    -m6_detector_net_connector_leg_width_y / 2,
                    m6_detector_net_connector_leg_bottom_z])
                    cube([
                        m6_detector_net_connector_leg_max_x -
                            m6_detector_net_connector_leg_min_x,
                        m6_detector_net_connector_leg_width_y,
                        m6_detector_net_connector_leg_height_z]);
                // Hollow socket/collar for the downward ballhead stud. The
                // 0.2 mm z overlaps avoid a coincident-face seam at the arm
                // and capture the top of the stud against the ballhead base.
                difference() {
                    m6_cylinder_z(
                        m6_detector_net_connector_socket_outer_d,
                        m6_detector_net_connector_socket_height_z,
                        m6_detector_ballhead_center_x,
                        m6_detector_ballhead_center_y,
                        m6_detector_net_connector_socket_center_z);
                    m6_cylinder_z(
                        m6_detector_net_connector_socket_clearance_d,
                        m6_detector_net_connector_socket_height_z + 2,
                        m6_detector_ballhead_center_x,
                        m6_detector_ballhead_center_y,
                        m6_detector_net_connector_socket_center_z);
                }
            }
            // The post already has matching x-through slots. These bores keep
            // the bought bridge's two-hole pattern explicit and coaxial with
            // the post when the complete right/left stand is assembled.
            for (y_position = [
                -m6_detector_net_connector_post_bolt_y,
                m6_detector_net_connector_post_bolt_y
            ]) {
                m6_cylinder_x(
                    m6_detector_net_connector_post_bolt_d,
                    m6_detector_net_connector_leg_t_x + 8,
                    (m6_detector_net_connector_leg_min_x +
                     m6_detector_net_connector_leg_max_x) / 2,
                    y_position,
                    m6_post_mount_hole_z);
            }
        }
}

module m6_detector_direct_mount_positive() {
    // Compatibility hook retained for callers from the previous direct-mount
    // design. The active M8 socket is cut directly in post_body_positive();
    // this hook deliberately emits no separate gray/yellow connector geometry.
}

module m6_detector_mount_positive() {
    m6_detector_body_positive();
    m6_detector_sensor_array_positive();
    // Assembly order is deliberate: body and rotated L-devices establish the
    // optical datum; front cover slides on from z+ first, rear cover follows;
    // bottom cover closes from z- last. All covers remain whole in previews.
    if (m6_detector_show_shell) {
        m6_detector_shell_front_positive();
        m6_detector_shell_rear_positive();
        m6_detector_bottom_cover_positive();
        m6_detector_bottom_gasket_positive();
    }
    if (m6_detector_cable_clearance_enabled)
        m6_detector_cable_routing_reference_positive();
    // The receiver daughter board is part of the installed M6 shell, not a
    // floating documentation envelope.  This raw-frame call is translated by
    // m6_detector_assembly_positive() together with the optical hardware.
    m6_receiver_carrier_board_raw_positive();
    m6_detector_ballhead_positive();
}

// Standalone detector previews keep the raw sensor/body coordinate chain
// above readable.  The installed assembly is shifted as one rigid group so
// its ballhead centre and the straight net post share the same x datum.
module m6_detector_assembly_positive() {
    translate([m6_detector_mount_x_offset, 0, m6_detector_mount_raise_z])
        m6_detector_mount_positive();
}

module m6_detector_exploded_positive() {
    // Non-sectioned inspection view.  Each physical part stays whole and is
    // pulled away along its real assembly direction: sensors out through x+,
    // x- optical front cover, x+ cable rear cover, and bottom cover downward.
    // The purchased vertical ballhead remains whole; the upper stand segment's
    // integrated same-material support is shown by the stand assembly, not as a
    // separate detector or metal-bridge part.
    m6_detector_ballhead_positive();

    // PETG carrier stays at its installed datum.
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

    // Pull the actual vertical receiver carrier out toward +y so its PCB and
    // connector row remain inspectable beside the exploded shell.
    translate([0, 42, 0])
        m6_receiver_carrier_board_raw_positive();
}

module m6_detector_exploded_assembly_positive() {
    translate([m6_detector_mount_x_offset, 0, m6_detector_mount_raise_z])
        m6_detector_exploded_positive();
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

module m6_machining_rail_positive() {
    translate([-m6_sensor_rail_x, 0, -m6_array_bottom_z])
        m6_sensor_rail_positive();
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
    // purchased ball head. The ballhead is the adjustment part; its downward
    // interface screws directly into the integrated same-material PETG upper segment.
    // No dark-gray bridge, legacy separate upper post, or duplicate fastener stack is
    // included in the current detector assembly.
    m6_detector_assembly_positive();
}

module m6_gimbal(side = 1) {
    sided(side) m6_gimbal_positive();
}

module m6_beam_preview() {
    // 名义零角度时，十条相对发射/接收器光轴都穿过球台边缘；
    // 当前主线为单竖直排，故所有光轴使用主体 y=0 中心线。检测器
    // 总成已经沿 x 移到立柱中心，光束预览也跟随安装后的光轴。
    beam_axis_x = m6_detector_assembly_optical_axis_x;
    color("red", 0.25)
        for (index = [0:m6_sensor_count - 1]) {
            y0 = m6_detector_sensor_head_center_y;
            translate([-beam_axis_x,
                       y0 - 0.35,
                       m6_sensor_z(index) + m6_detector_mount_raise_z - 0.35])
                cube([2 * beam_axis_x, 0.7, 0.7]);
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

module m6_optical_direction_assembly_preview(side = 1) {
    // The positive/right receiver is translated +offset and its mirrored
    // left/emitter mate is translated -offset.  A single translation of the
    // two-sided preview would put the left beam at the wrong x datum.
    translate([side >= 0 ? m6_detector_mount_x_offset :
               -m6_detector_mount_x_offset,
               0,
               m6_detector_mount_raise_z])
        m6_optical_direction_preview(side);
}

module m6_optical_full_direction_preview() {
    // One arrow per channel makes the left-to-right beam direction explicit
    // when both post-centred detector assemblies are shown together.
    m6_optical_direction_assembly_preview(-1);
    m6_optical_direction_assembly_preview(1);
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

module m6_optical_exploded_direction_assembly_preview(side = 1) {
    translate([side >= 0 ? m6_detector_mount_x_offset :
               -m6_detector_mount_x_offset,
               0,
               m6_detector_mount_raise_z])
        m6_optical_exploded_direction_preview(side);
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
    // 历史 STG-120ML 诊断模块的下方桥脚曾跨住网顶承载条；它不属于当前
    // 装配/打印主线，当前网顶没有轨道，仍需保留旧参数仅供回归检查。
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
    -net_sheet_t / 2 - sensor_film_depth - sensor_film_clearance_y;

function sensor_clip_front_inner_y() = sensor_film_y();
function sensor_clip_front_outer_y() =
    sensor_clip_front_inner_y() - sensor_depth;
function sensor_clip_rear_inner_y() =
    net_sheet_t / 2 + sensor_film_clearance_y;
function sensor_clip_rear_outer_y() =
    sensor_clip_rear_inner_y() + sensor_clip_rear_wall_t_y;

module pvdf_film_positive(x_position) {
    color("black")
        translate([x_position - sensor_film_length / 2,
                   sensor_film_y(), net_panel_top_z - sensor_film_height])
            cube([sensor_film_length, sensor_film_depth, sensor_film_height]);
}

module sensor_clamp_lip_positive(x_position) {
    film_y = sensor_film_y();
    color("mediumpurple")
        for (side = [-1, 1]) {
            translate([x_position + side * (sensor_film_length / 2 - sensor_clamp_tab_width),
                       film_y - 0.5, net_panel_top_z - sensor_film_height - 1])
                cube([sensor_clamp_tab_width, sensor_clamp_tab_depth,
                      sensor_clamp_tab_height]);
        }
}

module sensor_mount_body_positive(x_position) {
    // This is a non-load-bearing PETG saddle over the net cloth's top edge.
    // Its front jaw carries the PVDF film; the bridge and rear jaw retain the
    // cloth.  It is independent of the posts and deliberately does not form a
    // rail across the net.
    color("mediumpurple") {
        translate([x_position - sensor_length / 2,
                   sensor_clip_front_outer_y(), sensor_clip_bottom_z])
            cube([sensor_length, sensor_depth, sensor_height]);
        translate([x_position - sensor_length / 2,
                   sensor_clip_front_inner_y(),
                   net_panel_top_z - sensor_clip_bridge_t_z])
            cube([sensor_length,
                  sensor_clip_rear_outer_y() - sensor_clip_front_inner_y(),
                  sensor_clip_bridge_t_z]);
        translate([x_position - sensor_length / 2,
                   sensor_clip_rear_inner_y(), sensor_clip_bottom_z])
            cube([sensor_length, sensor_clip_rear_wall_t_y, sensor_height]);
    }
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
        // 历史诊断承托座向内伸入网顶承载条；当前 U 形网夹不使用此模块。
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
        translate([-net_span / 2, -net_sheet_t / 2, net_panel_bottom_z])
            cube([net_span, net_sheet_t,
                  net_panel_top_z - net_panel_bottom_z]);
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
        table_clamp_positive();
        net_clamp_clip_positive();
        m6_gimbal_positive();
    }
}

module parameter_probe() {
    echo(str("NETSTAND_PARAM table_width=", table_width));
    echo(str("NETSTAND_PARAM net_post_outboard_extension=", net_post_outboard_extension));
    echo(str("NETSTAND_PARAM table_thickness=", table_thickness));
    echo(str("NETSTAND_PARAM net_fixture_bottom_z=", net_fixture_bottom_z));
    echo(str("NETSTAND_PARAM net_height=", net_height));
    echo(str("NETSTAND_PARAM m6_detector_mount_raise_z=", m6_detector_mount_raise_z));
    echo(str("NETSTAND_PARAM net_clamp_channel_depth_x=", net_clamp_channel_depth_x));
    echo(str("NETSTAND_PARAM net_clamp_cylinder_insertion_depth_x=", net_clamp_cylinder_insertion_depth_x));
    echo(str("NETSTAND_PARAM net_clamp_channel_back_wall_t_x=", net_clamp_channel_back_wall_t_x));
    echo(str("NETSTAND_PARAM net_clamp_cylinder_interference_d=", net_clamp_cylinder_interference_d));
    echo(str("NETSTAND_PARAM net_clamp_cylinder_actual_d=", net_clamp_cylinder_actual_d));
    echo(str("NETSTAND_PARAM net_clamp_channel_side_clearance=", net_clamp_channel_side_clearance));
    echo(str("NETSTAND_PARAM net_clamp_channel_back_clearance=", net_clamp_channel_back_clearance));
    echo(str("NETSTAND_PARAM net_clamp_channel_width_y=", net_clamp_channel_width_y));
    echo(str("NETSTAND_PARAM net_clamp_channel_outboard_extension_x=", net_clamp_channel_outboard_extension_x));
    echo(str("NETSTAND_PARAM net_clamp_channel_bottom_z=", net_clamp_channel_bottom_z));
    echo(str("NETSTAND_PARAM net_clamp_channel_top_z=", net_clamp_channel_top_z));
    echo(str("NETSTAND_PARAM net_clamp_channel_void_min_x=", net_clamp_channel_void_min_x));
    echo(str("NETSTAND_PARAM net_clamp_channel_void_max_x=", net_clamp_channel_void_max_x));
    echo(str("NETSTAND_PARAM net_clamp_cylinder_center_x=", net_clamp_cylinder_center_x));
    echo(str("NETSTAND_PARAM net_clamp_cylinder_height=", net_clamp_cylinder_height));
    echo(str("NETSTAND_PARAM net_clamp_clip_clearance_x=", net_clamp_clip_clearance_x));
    echo(str("NETSTAND_PARAM net_clamp_clip_length_x=", net_clamp_clip_length_x));
    echo(str("NETSTAND_PARAM net_clamp_clip_inner_x=", net_clamp_clip_inner_x));
    echo(str("NETSTAND_PARAM net_clamp_clip_outer_x=", net_clamp_clip_outer_x));
    echo(str("NETSTAND_PARAM net_clamp_clip_jaw_t_y=", net_clamp_clip_jaw_t_y));
    echo(str("NETSTAND_PARAM net_clamp_clip_jaw_center_y=", net_clamp_clip_jaw_center_y));
    echo(str("NETSTAND_PARAM net_clamp_clip_jaw_clearance_y=", net_clamp_clip_jaw_clearance_y));
    echo(str("NETSTAND_PARAM net_clamp_clip_jaw_gap_y=", net_clamp_clip_jaw_gap_y));
    echo(str("NETSTAND_PARAM net_clamp_clip_outer_half_y=", net_clamp_clip_outer_half_y));
    echo(str("NETSTAND_PARAM net_clamp_clip_crossbar_t_x=", net_clamp_clip_crossbar_t_x));
    echo(str("NETSTAND_PARAM net_clamp_keeper_enabled=", net_clamp_keeper_enabled ? 1 : 0));
    echo(str("NETSTAND_PARAM net_clamp_keeper_x_min=", net_clamp_keeper_x_min));
    echo(str("NETSTAND_PARAM net_clamp_keeper_x_max=", net_clamp_keeper_x_max));
    echo(str("NETSTAND_PARAM net_clamp_keeper_y_min=", net_clamp_keeper_y_min));
    echo(str("NETSTAND_PARAM net_clamp_keeper_y_max=", net_clamp_keeper_y_max));
    echo(str("NETSTAND_PARAM net_clamp_keeper_z=", net_clamp_keeper_z));
    echo(str("NETSTAND_PARAM net_clamp_keeper_height_z=", net_clamp_keeper_height_z));
    echo(str("NETSTAND_PARAM net_clamp_keeper_relief_min_x=", net_clamp_keeper_relief_min_x));
    echo(str("NETSTAND_PARAM net_clamp_keeper_relief_max_x=", net_clamp_keeper_relief_max_x));
    echo(str("NETSTAND_PARAM net_clamp_keeper_relief_min_y=", net_clamp_keeper_relief_min_y));
    echo(str("NETSTAND_PARAM net_clamp_keeper_relief_max_y=", net_clamp_keeper_relief_max_y));
    echo(str("NETSTAND_PARAM net_clamp_keeper_latch_x_min=", net_clamp_keeper_latch_x_min));
    echo(str("NETSTAND_PARAM net_clamp_keeper_latch_x_max=", net_clamp_keeper_latch_x_max));
    echo(str("NETSTAND_PARAM net_clamp_keeper_latch_y_min=", net_clamp_keeper_latch_y_min));
    echo(str("NETSTAND_PARAM net_clamp_keeper_latch_y_max=", net_clamp_keeper_latch_y_max));
    echo(str("NETSTAND_PARAM net_clamp_keeper_latch_z=", net_clamp_keeper_latch_z));
    echo(str("NETSTAND_PARAM net_clamp_keeper_latch_height_z=", net_clamp_keeper_latch_height_z));
    echo(str("NETSTAND_PARAM net_top_rail_required=", net_top_rail_required));
    echo(str("NETSTAND_PARAM net_panel_bottom_z=", net_panel_bottom_z));
    echo(str("NETSTAND_PARAM net_panel_top_z=", net_panel_top_z));
    echo(str("NETSTAND_PARAM net_rail_height=", net_rail_height));
    echo(str("NETSTAND_PARAM net_rail_depth=", net_rail_depth));
    echo(str("NETSTAND_PARAM net_sheet_t=", net_sheet_t));
    echo(str("NETSTAND_PARAM net_passage_width_y=", net_passage_width_y));
    echo(str("NETSTAND_PARAM net_passage_side_clearance_y=", net_passage_side_clearance_y));
    echo(str("NETSTAND_PARAM net_passage_body_extension_x=", net_passage_body_extension_x));
    echo(str("NETSTAND_PARAM net_passage_min_x=", net_passage_min_x));
    echo(str("NETSTAND_PARAM net_passage_max_x=", net_passage_max_x));
    echo(str("NETSTAND_PARAM net_passage_bottom_z=", net_passage_bottom_z));
    echo(str("NETSTAND_PARAM net_passage_top_z=", net_passage_top_z));
    echo(str("NETSTAND_PARAM beam_count=", beam_count));
    echo(str("NETSTAND_PARAM beam_first_height=", beam_first_height));
    echo(str("NETSTAND_PARAM beam_last_height=", beam_last_height));
    echo(str("NETSTAND_PARAM beam_pitch=", beam_pitch));
    echo(str("NETSTAND_PARAM post_center_x=", post_center_x));
    echo(str("NETSTAND_PARAM post_body_width=", post_body_width));
    echo(str("NETSTAND_PARAM post_body_depth=", post_body_depth));
    echo(str("NETSTAND_PARAM clamp_slide_interface_enabled=", clamp_slide_interface_enabled ? 1 : 0));
    echo(str("NETSTAND_PARAM post_interface_transition_height_z=", post_interface_transition_height_z));
    echo(str("NETSTAND_PARAM post_interface_transition_extra_x=", post_interface_transition_extra_x));
    echo(str("NETSTAND_PARAM post_interface_transition_extra_y=", post_interface_transition_extra_y));
    echo(str("NETSTAND_PARAM post_c_clamp_overlap_depth_z=", post_c_clamp_overlap_depth_z));
    echo(str("NETSTAND_PARAM post_interface_transition_bottom_width_x=", post_interface_transition_bottom_width_x));
    echo(str("NETSTAND_PARAM post_interface_transition_bottom_depth_y=", post_interface_transition_bottom_depth_y));
    echo(str("NETSTAND_PARAM post_lower_overlap_solid_height_z=", post_lower_overlap_solid_height_z));
    echo(str("NETSTAND_PARAM post_interface_transition_start_z=", post_interface_transition_start_z));
    echo(str("NETSTAND_PARAM post_interface_transition_top_z=", post_interface_transition_top_z));
    echo(str("NETSTAND_PARAM post_interface_transition_outer_max_x=", post_interface_transition_outer_max_x));
    echo(str("NETSTAND_PARAM post_bottom=", post_bottom));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_reference_upright_width_x=", post_skp_leg_foot_reference_upright_width_x));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_reference_lower_depth_y=", post_skp_leg_foot_reference_lower_depth_y));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_reference_interface_z=", post_skp_leg_foot_reference_interface_z));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_main_length_x=", post_skp_leg_foot_main_length_x));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_side_extension_x=", post_skp_leg_foot_side_extension_x));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_side_height_z=", post_skp_leg_foot_side_height_z));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_lower_min_y_local=", post_skp_leg_foot_lower_min_y_local));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_lower_max_y_local=", post_skp_leg_foot_lower_max_y_local));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_aligned_max_x=", post_skp_leg_foot_aligned_max_x));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_origin_x=", post_skp_leg_foot_origin_x));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_origin_y=", post_skp_leg_foot_origin_y));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_origin_z=", post_skp_leg_foot_origin_z));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_min_x=", post_skp_leg_foot_min_x));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_max_x=", post_skp_leg_foot_max_x));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_min_y=", post_skp_leg_foot_min_y));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_max_y=", post_skp_leg_foot_max_y));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_bottom_z=", post_skp_leg_foot_bottom_z));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_top_z=", post_skp_leg_foot_top_z));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_terminal_chamfer_x=", post_skp_leg_foot_terminal_chamfer_x));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_terminal_chamfer_z=", post_skp_leg_foot_terminal_chamfer_z));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_fit_clearance=", post_skp_leg_foot_fit_clearance));
    echo(str("NETSTAND_PARAM post_skp_leg_foot_fit_cutter_overlap_z=", post_skp_leg_foot_fit_cutter_overlap_z));
    echo(str("NETSTAND_PARAM net_post_top_z=", net_post_top_z));
    echo(str("NETSTAND_PARAM net_span=", net_span));
    echo(str("NETSTAND_PARAM post_segment_count=", post_segment_count));
    echo(str("NETSTAND_PARAM post_segment_length=", post_segment_length));
    echo(str("NETSTAND_PARAM post_joint_gap=", post_joint_gap));
    echo(str("NETSTAND_PARAM preview_fit_display_gap=", preview_fit_display_gap));
    echo(str("NETSTAND_PARAM post_joint_above_net_clearance_z=", post_joint_above_net_clearance_z));
    echo(str("NETSTAND_PARAM active_post_top_z=", active_post_top_z));
    echo(str("NETSTAND_PARAM active_post_total_height=", active_post_total_height));
    echo(str("NETSTAND_PARAM active_post_segment_length=", active_post_segment_length));
    echo(str("NETSTAND_PARAM active_post_joint_z=", active_post_joint_z));
    echo(str("NETSTAND_PARAM post_split_z=", post_split_z));
    echo(str("NETSTAND_PARAM post_lower_segment_z=", post_lower_segment_z));
    echo(str("NETSTAND_PARAM post_lower_segment_height=", post_lower_segment_height));
    echo(str("NETSTAND_PARAM post_upper_segment_z=", post_upper_segment_z));
    echo(str("NETSTAND_PARAM post_upper_segment_height=", post_upper_segment_height));
    echo(str("NETSTAND_PARAM m4_joint_bolt_clearance_d=", m4_joint_bolt_clearance_d));
    echo(str("NETSTAND_PARAM m4_joint_bolt_length=", m4_joint_bolt_length));
    echo(str("NETSTAND_PARAM m4_joint_bolt_z_offset=", m4_joint_bolt_z_offset));
    echo(str("NETSTAND_PARAM post_joint_rail_height_z=", post_joint_rail_height_z));
    echo(str("NETSTAND_PARAM post_joint_rail_root_overlap_z=", post_joint_rail_root_overlap_z));
    echo(str("NETSTAND_PARAM post_joint_rail_z0=", post_joint_rail_z0));
    echo(str("NETSTAND_PARAM post_joint_rail_x_base_width=", post_joint_rail_x_base_width));
    echo(str("NETSTAND_PARAM post_joint_rail_x_neck_width=", post_joint_rail_x_neck_width));
    echo(str("NETSTAND_PARAM post_joint_rail_y_depth=", post_joint_rail_y_depth));
    echo(str("NETSTAND_PARAM post_joint_rail_clearance=", post_joint_rail_clearance));
    echo(str("NETSTAND_PARAM post_joint_lock_z=", post_joint_lock_z));
    echo(str("NETSTAND_PARAM clamp_slide_split_x=", clamp_slide_split_x));
    echo(str("NETSTAND_PARAM clamp_slide_shoe_deepening_x=", clamp_slide_shoe_deepening_x));
    echo(str("NETSTAND_PARAM clamp_slide_shoe_drop_z=", clamp_slide_shoe_drop_z));
    echo(str("NETSTAND_PARAM clamp_slide_length_x=", clamp_slide_length_x));
    echo(str("NETSTAND_PARAM clamp_slide_tongue_attach_x=", clamp_slide_tongue_attach_x));
    echo(str("NETSTAND_PARAM clamp_slide_tongue_min_x=", clamp_slide_tongue_min_x));
    echo(str("NETSTAND_PARAM clamp_slide_receiver_length_x=", clamp_slide_receiver_length_x));
    echo(str("NETSTAND_PARAM clamp_slide_rail_y_outer=", max(clamp_slide_rail_y_positions)));
    echo(str("NETSTAND_PARAM clamp_slide_rail_y_depth=", clamp_slide_rail_y_depth));
    echo(str("NETSTAND_PARAM clamp_slide_rail_head_width_y=", clamp_slide_rail_head_width_y));
    echo(str("NETSTAND_PARAM clamp_slide_rail_neck_width_y=", clamp_slide_rail_neck_width_y));
    echo(str("NETSTAND_PARAM clamp_slide_rail_head_height_z=", clamp_slide_rail_head_height_z));
    echo(str("NETSTAND_PARAM clamp_slide_rail_neck_height_z=", clamp_slide_rail_neck_height_z));
    echo(str("NETSTAND_PARAM clamp_slide_rail_floor_z=", clamp_slide_rail_floor_z));
    echo(str("NETSTAND_PARAM clamp_slide_rail_base_width_z=", clamp_slide_rail_base_width_z));
    echo(str("NETSTAND_PARAM clamp_slide_rail_neck_width_z=", clamp_slide_rail_neck_width_z));
    echo(str("NETSTAND_PARAM clamp_slide_rail_height_z=", clamp_slide_rail_height_z));
    echo(str("NETSTAND_PARAM clamp_slide_rail_center_z=", clamp_slide_rail_center_z));
    echo(str("NETSTAND_PARAM clamp_slide_clearance=", clamp_slide_clearance));
    echo(str("NETSTAND_PARAM clamp_slide_receiver_floor_z=", clamp_slide_receiver_floor_z));
    echo(str("NETSTAND_PARAM clamp_slide_receiver_top_z=", clamp_slide_receiver_top_z));
    echo(str("NETSTAND_PARAM clamp_slide_receiver_neck_height_z=", clamp_slide_receiver_neck_height_z));
    echo(str("NETSTAND_PARAM clamp_slide_seat_z=", clamp_slide_seat_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_seat_clearance_x=", clamp_slide_post_seat_clearance_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_seat_end_x=", clamp_slide_post_seat_end_x));
    echo(str("NETSTAND_PARAM clamp_fixed_body_max_x=", clamp_fixed_body_max_x));
    echo(str("NETSTAND_PARAM clamp_slide_entry_open_x=", clamp_slide_entry_open_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_root_width_y=", clamp_slide_post_foot_root_width_y));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_ankle_inboard_extension_x=", clamp_slide_post_foot_ankle_inboard_extension_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_root_min_x=", clamp_slide_post_foot_root_min_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_root_max_x=", clamp_slide_post_foot_root_max_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_bridge_min_x=", clamp_slide_post_foot_bridge_min_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_bridge_max_x=", clamp_slide_post_foot_bridge_max_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_cross_tie_length_x=", clamp_slide_post_foot_cross_tie_length_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_cross_tie_top_z=", clamp_slide_post_foot_cross_tie_top_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_cross_tie_height_z=", clamp_slide_post_foot_cross_tie_height_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_cross_tie_bottom_z=", clamp_slide_post_foot_cross_tie_bottom_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_cross_tie_bottom_half_y=", clamp_slide_post_foot_cross_tie_bottom_half_y));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_cross_tie_top_half_y=", clamp_slide_post_foot_cross_tie_top_half_y));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_cross_tie_bridge_half_y=", clamp_slide_post_foot_cross_tie_bridge_half_y));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_bottom_z=", clamp_slide_post_foot_bottom_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_top_z=", clamp_slide_post_foot_top_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_transition_section_count=", clamp_slide_post_foot_transition_section_count));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_transition_slice_z=", clamp_slide_post_foot_transition_slice_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_transition_start_z=", clamp_slide_post_foot_transition_start_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_transition_side_start_z=", clamp_slide_post_foot_transition_side_start_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_transition_end_z=", clamp_slide_post_foot_transition_end_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_post_fusion_inset=", clamp_slide_post_foot_post_fusion_inset));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_side_outer_y=", clamp_slide_post_foot_side_outer_y));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_side_top_inner_y=", clamp_slide_post_foot_side_top_inner_y));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_side_top_outer_y=", clamp_slide_post_foot_side_top_outer_y));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_ankle_height_z=", clamp_slide_post_foot_ankle_height_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_slope_top_min_x=", clamp_slide_post_foot_slope_top_min_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_slope_top_max_x=", clamp_slide_post_foot_slope_top_max_x));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_shoe_buried_overlap_z=", clamp_slide_post_foot_shoe_buried_overlap_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_shoe_overlap_z=", clamp_slide_post_foot_shoe_overlap_z));
    echo(str("NETSTAND_PARAM clamp_slide_post_foot_root_overlap_z=", clamp_slide_post_foot_root_overlap_z));
    echo(str("NETSTAND_PARAM clamp_slide_lock_x=", clamp_slide_lock_x));
    echo(str("NETSTAND_PARAM clamp_slide_lock_bore_d=", clamp_slide_lock_bore_d));
    echo(str("NETSTAND_PARAM clamp_slide_lock_bolt_d=", clamp_slide_lock_bolt_d));
    echo(str("NETSTAND_PARAM clamp_slide_lock_bolt_length=", clamp_slide_lock_bolt_length));
    echo(str("NETSTAND_PARAM clamp_slide_lock_nut_af=", clamp_slide_lock_nut_af));
    echo(str("NETSTAND_PARAM clamp_slide_lock_nut_h=", clamp_slide_lock_nut_h));
    echo(str("NETSTAND_PARAM clamp_slide_detent_x=", clamp_slide_detent_x));
    echo(str("NETSTAND_PARAM clamp_slide_detent_y_count=", clamp_slide_detent_y_count));
    echo(str("NETSTAND_PARAM clamp_slide_detent_y_center=", clamp_slide_detent_y_center));
    echo(str("NETSTAND_PARAM clamp_slide_detent_ball_d=", clamp_slide_detent_ball_d));
    echo(str("NETSTAND_PARAM clamp_slide_detent_ball_offset_z=", clamp_slide_detent_ball_offset_z));
    echo(str("NETSTAND_PARAM clamp_slide_detent_ball_center_z=", clamp_slide_detent_ball_center_z));
    echo(str("NETSTAND_PARAM clamp_slide_detent_bore_d=", clamp_slide_detent_bore_d));
    echo(str("NETSTAND_PARAM clamp_slide_detent_bore_top_z=", clamp_slide_detent_bore_top_z));
    echo(str("NETSTAND_PARAM clamp_slide_detent_dimple_d=", clamp_slide_detent_dimple_d));
    echo(str("NETSTAND_PARAM clamp_slide_detent_dimple_depth_z=", clamp_slide_detent_dimple_depth_z));
    echo(str("NETSTAND_PARAM clamp_slide_detent_female_roof_z=", clamp_slide_detent_female_roof_z));
    echo(str("NETSTAND_PARAM clamp_slide_detent_spring_d=", clamp_slide_detent_spring_d));
    echo(str("NETSTAND_PARAM clamp_slide_detent_spring_h=", clamp_slide_detent_spring_h));
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
    echo(str("NETSTAND_PARAM sensor_length=", sensor_length));
    echo(str("NETSTAND_PARAM sensor_depth=", sensor_depth));
    echo(str("NETSTAND_PARAM sensor_height=", sensor_height));
    echo(str("NETSTAND_PARAM sensor_post_clearance_x=", sensor_post_clearance_x));
    echo(str("NETSTAND_PARAM sensor_film_y=", sensor_film_y()));
    echo(str("NETSTAND_PARAM sensor_film_height=", sensor_film_height));
    echo(str("NETSTAND_PARAM sensor_film_length=", sensor_film_length));
    echo(str("NETSTAND_PARAM sensor_film_depth=", sensor_film_depth));
    echo(str("NETSTAND_PARAM sensor_clamp_tab_width=", sensor_clamp_tab_width));
    echo(str("NETSTAND_PARAM clamp_reach_inboard=", clamp_reach_inboard));
    echo(str("NETSTAND_PARAM clamp_tongue_extra_length_x=",
             clamp_tongue_extra_length_x));
    echo(str("NETSTAND_PARAM clamp_tongue_reach_inboard=",
             clamp_tongue_reach_inboard));
    echo(str("NETSTAND_PARAM clamp_pad_x=", clamp_pad_x));
    echo(str("NETSTAND_PARAM clamp_pad_depth=", clamp_pad_depth));
    echo(str("NETSTAND_PARAM clamp_pad_t=", clamp_pad_t));
    echo(str("NETSTAND_PARAM clamp_horizontal_part_outboard_limit=",
             clamp_horizontal_part_outboard_limit));
    echo(str("NETSTAND_PARAM clamp_outboard_extension_min=", clamp_outboard_extension_min));
    echo(str("NETSTAND_PARAM clamp_outboard_extension_actual=", clamp_outboard_extension_actual));
    echo(str("NETSTAND_PARAM clamp_screw_inset=", clamp_screw_inset));
    echo(str("NETSTAND_PARAM clamp_reinforcement_inboard_offset_x=",
             clamp_reinforcement_inboard_offset_x));
    echo(str("NETSTAND_PARAM clamp_reinforcement_near_table_thickness_z=",
             clamp_reinforcement_near_table_thickness_z));
    echo(str("NETSTAND_PARAM clamp_reinforcement_depth_y=",
             clamp_reinforcement_depth_y));
    echo(str("NETSTAND_PARAM clamp_solid_bridge_clearance_x=",
             clamp_solid_bridge_clearance_x));
    echo(str("NETSTAND_PARAM clamp_solid_bridge_start_x=",
             clamp_solid_bridge_start_x));
    echo(str("NETSTAND_PARAM clamp_solid_bridge_top_z=",
             clamp_solid_bridge_top_z));
    echo(str("NETSTAND_PARAM clamp_reinforcement_start_x=",
             clamp_reinforcement_start_x));
    echo(str("NETSTAND_PARAM clamp_reinforcement_end_x=",
             clamp_reinforcement_end_x));
    echo(str("NETSTAND_PARAM clamp_reinforcement_top_z=",
             clamp_reinforcement_top_z));
    echo(str("NETSTAND_PARAM clamp_reinforcement_near_table_bottom_z=",
             clamp_reinforcement_near_table_bottom_z));
    echo(str("NETSTAND_PARAM clamp_reinforcement_outer_thickness_z=",
             clamp_reinforcement_outer_thickness_z));
    echo(str("NETSTAND_PARAM clamp_reinforcement_outer_bottom_z=",
             clamp_reinforcement_outer_bottom_z));
    echo(str("NETSTAND_PARAM clamp_electronics_cavity_x_min=",
             clamp_electronics_cavity_x_min));
    echo(str("NETSTAND_PARAM clamp_electronics_cavity_x_max=",
             clamp_electronics_cavity_x_max));
    echo(str("NETSTAND_PARAM clamp_electronics_cavity_y_half=",
             clamp_electronics_cavity_y_half));
    echo(str("NETSTAND_PARAM clamp_electronics_cavity_top_z=",
             clamp_electronics_cavity_top_z));
    echo(str("NETSTAND_PARAM clamp_electronics_cavity_roof_t=",
             clamp_electronics_cavity_roof_t));
    echo(str("NETSTAND_PARAM clamp_electronics_cavity_cover_t=",
             clamp_electronics_cavity_cover_t));
    echo(str("NETSTAND_PARAM clamp_electronics_cavity_length_x=",
             clamp_electronics_cavity_length_x));
    echo(str("NETSTAND_PARAM clamp_electronics_board_length_x=",
             clamp_electronics_board_length_x));
    echo(str("NETSTAND_PARAM clamp_electronics_board_width_y=",
             clamp_electronics_board_width_y));
    echo(str("NETSTAND_PARAM clamp_electronics_battery_length_x=",
             clamp_electronics_battery_length_x));
    echo(str("NETSTAND_PARAM clamp_electronics_battery_width_y=",
             clamp_electronics_battery_width_y));
    echo(str("NETSTAND_PARAM clamp_electronics_battery_thickness_z=",
             clamp_electronics_battery_thickness_z));
    echo(str("NETSTAND_PARAM clamp_electronics_battery_clearance_z=",
             clamp_electronics_battery_clearance_z));
    echo(str("NETSTAND_PARAM clamp_electronics_battery_rail_t=",
             clamp_electronics_battery_rail_t));
    echo(str("NETSTAND_PARAM clamp_electronics_battery_rail_clearance_y=",
             clamp_electronics_battery_rail_clearance_y));
    echo(str("NETSTAND_PARAM clamp_electronics_board_t=",
             clamp_electronics_board_t));
    echo(str("NETSTAND_PARAM clamp_electronics_board_standoff_d=",
             clamp_electronics_board_standoff_d));
    echo(str("NETSTAND_PARAM clamp_electronics_component_height_z=",
             clamp_electronics_component_height_z));
    echo(str("NETSTAND_PARAM clamp_electronics_component_clearance_z=",
             clamp_electronics_component_clearance_z));
    echo(str("NETSTAND_PARAM clamp_electronics_board_top_clearance_z=",
             clamp_electronics_board_top_clearance_z));
    echo(str("NETSTAND_PARAM clamp_electronics_board_bottom_z=",
             clamp_electronics_board_bottom_z));
    echo(str("NETSTAND_PARAM clamp_electronics_main_board_y_shift=",
             clamp_electronics_main_board_y_shift));
    echo(str("NETSTAND_PARAM clamp_electronics_ui_board_length_x=",
             clamp_electronics_ui_board_length_x));
    echo(str("NETSTAND_PARAM clamp_electronics_ui_board_width_y=",
             clamp_electronics_ui_board_width_y));
    echo(str("NETSTAND_PARAM clamp_electronics_ui_board_z=",
             clamp_electronics_ui_board_z));
    echo(str("NETSTAND_PARAM clamp_electronics_ui_board_y_shift=",
             clamp_electronics_ui_board_y_shift));
    echo(str("NETSTAND_PARAM clamp_electronics_emitter_board_length_x=",
             clamp_electronics_emitter_board_length_x));
    echo(str("NETSTAND_PARAM clamp_electronics_emitter_board_width_y=",
             clamp_electronics_emitter_board_width_y));
    echo(str("NETSTAND_PARAM clamp_electronics_emitter_board_bottom_z=",
             clamp_electronics_emitter_board_bottom_z));
    echo(str("NETSTAND_PARAM clamp_electronics_emitter_board_y_shift=",
             clamp_electronics_emitter_board_y_shift));
    echo(str("NETSTAND_PARAM clamp_electronics_emitter_battery_length_x=",
             clamp_electronics_emitter_battery_length_x));
    echo(str("NETSTAND_PARAM clamp_electronics_emitter_battery_width_y=",
             clamp_electronics_emitter_battery_width_y));
    echo(str("NETSTAND_PARAM clamp_electronics_emitter_battery_thickness_z=",
             clamp_electronics_emitter_battery_thickness_z));
    echo(str("NETSTAND_PARAM clamp_electronics_gasket_width=",
             clamp_electronics_gasket_width));
    echo(str("NETSTAND_PARAM clamp_electronics_cover_lip_h=",
             clamp_electronics_cover_lip_h));
    echo(str("NETSTAND_PARAM m6_receiver_carrier_length_z=",
             m6_receiver_carrier_length_z));
    echo(str("NETSTAND_PARAM m6_receiver_carrier_width_y=",
             m6_receiver_carrier_width_y));
    echo(str("NETSTAND_PARAM m6_receiver_carrier_board_x=",
             m6_receiver_carrier_board_x));
    echo(str("NETSTAND_PARAM m6_receiver_carrier_board_y=",
             m6_receiver_carrier_board_y));
    echo(str("NETSTAND_PARAM m6_receiver_carrier_board_z_min=",
             m6_receiver_carrier_board_z_min));
    echo(str("NETSTAND_PARAM m6_receiver_carrier_board_z_max=",
             m6_receiver_carrier_board_z_max));
    echo(str("NETSTAND_PARAM m6_receiver_carrier_clearance_to_body_x=",
             m6_receiver_carrier_clearance_to_body_x));
    echo(str("NETSTAND_PARAM clamp_electronics_faceplate_t=",
             clamp_electronics_faceplate_t));
    echo(str("NETSTAND_PARAM clamp_electronics_faceplate_border=",
             clamp_electronics_faceplate_border));
    echo(str("NETSTAND_PARAM clamp_pad_outer_x=", clamp_pad_outer_x));
    echo(str("NETSTAND_PARAM clamp_outer_wall_x=", clamp_outer_wall_x));
    echo(str("NETSTAND_PARAM clamp_lower_arm_x=", clamp_lower_arm_x));
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
    echo(str("NETSTAND_PARAM clamp_screw_to_knob_top_base=",
             clamp_screw_to_knob_top_base));
    echo(str("NETSTAND_PARAM clamp_screw_extra_length_z=",
             clamp_screw_extra_length_z));
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
    echo(str("NETSTAND_PARAM clamp_knob_d=", clamp_knob_d));
    echo(str("NETSTAND_PARAM clamp_knob_grip_root_d=", clamp_knob_grip_root_d));
    echo(str("NETSTAND_PARAM clamp_knob_grip_tooth_count=",
             clamp_knob_grip_tooth_count));
    echo(str("NETSTAND_PARAM clamp_knob_grip_tooth_d=", clamp_knob_grip_tooth_d));
    echo(str("NETSTAND_PARAM clamp_knob_grip_tooth_pitch_r=",
             clamp_knob_grip_tooth_pitch_r));
    echo(str("NETSTAND_PARAM clamp_knob_h=", clamp_knob_h));
    echo(str("NETSTAND_PARAM clamp_knob_top_z=", clamp_knob_top_z));
    echo(str("NETSTAND_PARAM clamp_knob_bottom_z=", clamp_knob_bottom_z));
    echo(str("NETSTAND_PARAM clamp_knob_nut_z=", clamp_knob_nut_z));
    echo(str("NETSTAND_PARAM clamp_knob_drive_nut_z=", clamp_knob_drive_nut_z));
    echo(str("NETSTAND_PARAM clamp_knob_lock_nut_z=", clamp_knob_lock_nut_z));
    echo(str("NETSTAND_PARAM clamp_knob_nut_bottom_z=", clamp_knob_nut_bottom_z));
    echo(str("NETSTAND_PARAM clamp_knob_nut_top_z=", clamp_knob_nut_top_z));
    echo(str("NETSTAND_PARAM clamp_lower_arm_t=", clamp_lower_arm_t));
    echo(str("NETSTAND_PARAM clamp_lower_arm_bottom_z=", clamp_lower_arm_bottom_z));
    echo(str("NETSTAND_PARAM clamp_lower_arm_top_z=", clamp_lower_arm_top_z));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_top_z=", clamp_pressure_pad_top_z));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_bottom_z=", clamp_pressure_pad_bottom_z));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_x=", clamp_pressure_pad_x));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_d=", clamp_pressure_pad_d));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_width=", clamp_pressure_pad_width));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_depth=", clamp_pressure_pad_depth));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_t=", clamp_pressure_pad_t));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_screw_socket_d=",
             clamp_pressure_pad_screw_socket_d));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_screw_socket_depth=",
             clamp_pressure_pad_screw_socket_depth));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_screw_socket_mouth_d=",
             clamp_pressure_pad_screw_socket_mouth_d));
    echo(str("NETSTAND_PARAM clamp_pressure_pad_screw_socket_chamfer_h=",
             clamp_pressure_pad_screw_socket_chamfer_h));
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
    echo(str("NETSTAND_PARAM m6_ballhead_body_depth_y=", m6_ballhead_body_depth_y));
    echo(str("NETSTAND_PARAM m6_ballhead_body_corner_radius=", m6_ballhead_body_corner_radius));
    echo(str("NETSTAND_PARAM m6_ballhead_ball_socket_d=", m6_ballhead_ball_socket_d));
    echo(str("NETSTAND_PARAM m6_ballhead_side_plate_d=", m6_ballhead_side_plate_d));
    echo(str("NETSTAND_PARAM m6_ballhead_side_plate_t_x=", m6_ballhead_side_plate_t_x));
    echo(str("NETSTAND_PARAM m6_ballhead_lock_knob_d=", m6_ballhead_lock_knob_d));
    echo(str("NETSTAND_PARAM m6_ballhead_lock_knob_t_y=", m6_ballhead_lock_knob_t_y));
    echo(str("NETSTAND_PARAM m6_ballhead_lock_knob_ridge_count=", m6_ballhead_lock_knob_ridge_count));
    echo(str("NETSTAND_PARAM m6_ballhead_base_d=", m6_ballhead_base_d));
    echo(str("NETSTAND_PARAM m6_ballhead_base_t=", m6_ballhead_base_t));
    echo(str("NETSTAND_PARAM m6_ballhead_sensor_stud_d=", m6_ballhead_sensor_stud_d));
    echo(str("NETSTAND_PARAM m6_ballhead_sensor_stud_length=", m6_ballhead_sensor_stud_length));
    echo(str("NETSTAND_PARAM m6_ballhead_sensor_thread_core_d=", m6_ballhead_sensor_thread_core_d));
    echo(str("NETSTAND_PARAM m6_ballhead_sensor_thread_pitch=", m6_ballhead_sensor_thread_pitch));
    echo(str("NETSTAND_PARAM m6_ballhead_net_stud_d=", m6_ballhead_net_stud_d));
    echo(str("NETSTAND_PARAM m6_ballhead_net_stud_length=", m6_ballhead_net_stud_length));
    echo(str("NETSTAND_PARAM m6_ballhead_net_thread_core_d=", m6_ballhead_net_thread_core_d));
    echo(str("NETSTAND_PARAM m6_ballhead_net_thread_pitch=", m6_ballhead_net_thread_pitch));
    echo(str("NETSTAND_PARAM m6_ballhead_top_nut_af=", m6_ballhead_top_nut_af));
    echo(str("NETSTAND_PARAM m6_ballhead_top_nut_h=", m6_ballhead_top_nut_h));
    echo(str("NETSTAND_PARAM m6_ballhead_bottom_nut_af=", m6_ballhead_bottom_nut_af));
    echo(str("NETSTAND_PARAM m6_ballhead_bottom_nut_h=", m6_ballhead_bottom_nut_h));
    echo(str("NETSTAND_PARAM m6_ballhead_nut_clearance=", m6_ballhead_nut_clearance));
    echo(str("NETSTAND_PARAM m6_ballhead_top_nut_pocket_af=", m6_ballhead_top_nut_pocket_af));
    echo(str("NETSTAND_PARAM m6_ballhead_top_nut_pocket_depth=", m6_ballhead_top_nut_pocket_depth));
    echo(str("NETSTAND_PARAM m6_ballhead_bottom_nut_pocket_af=", m6_ballhead_bottom_nut_pocket_af));
    echo(str("NETSTAND_PARAM m6_ballhead_bottom_nut_pocket_depth=", m6_ballhead_bottom_nut_pocket_depth));
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
    echo(str("NETSTAND_PARAM m6_detector_shell_split_clearance_x=", m6_detector_shell_split_clearance_x));
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
    echo(str("NETSTAND_PARAM m6_detector_cable_exit_y=", m6_detector_cable_exit_y));
    echo(str("NETSTAND_PARAM m6_detector_cable_gland_outer_d=",
             m6_detector_cable_gland_outer_d));
    echo(str("NETSTAND_PARAM m6_detector_cable_trunk_y=",
             m6_detector_cable_trunk_y));
    echo(str("NETSTAND_PARAM m6_detector_cable_trunk_x=",
             m6_detector_cable_trunk_x));
    echo(str("NETSTAND_PARAM m6_detector_cable_trunk_clearance_y=",
             m6_detector_cable_trunk_clearance_y));
    echo(str("NETSTAND_PARAM m6_detector_cable_clearance_enabled=",
             m6_detector_cable_clearance_enabled));
    echo(str("NETSTAND_PARAM m6_detector_detector_thread_axis_x=",
             m6_detector_detector_thread_axis_x));
    echo(str("NETSTAND_PARAM m6_detector_sensor_thread_center_y=", m6_detector_sensor_thread_center_y));
    echo(str("NETSTAND_PARAM m6_detector_sensor_head_center_y=", m6_detector_sensor_head_center_y));
    echo(str("NETSTAND_PARAM m6_detector_body_material=", m6_detector_body_material));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_length_x=", m6_detector_shell_support_boss_length_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_overlap_x=", m6_detector_shell_support_boss_overlap_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_depth_y=", m6_detector_shell_support_boss_depth_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_height_z=", m6_detector_shell_support_boss_height_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_radius=", m6_detector_shell_support_boss_radius));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_x_overlap=", m6_detector_shell_support_gusset_x_overlap));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_root_width_y=", m6_detector_shell_support_gusset_root_width_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_wall_width_y=", m6_detector_shell_support_gusset_wall_width_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_height_z=", m6_detector_shell_support_gusset_height_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_hole_d=", m6_detector_shell_support_hole_d));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_hole_depth_x=", m6_detector_shell_support_hole_depth_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_stud_engagement_x=", m6_detector_shell_support_stud_engagement_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_nut_pocket_center_x=", m6_detector_shell_support_nut_pocket_center_x));
    echo(str("NETSTAND_PARAM m6_detector_detector_ballhead_gap_x=", m6_detector_detector_ballhead_gap_x));
    echo(str("NETSTAND_PARAM m6_detector_sensor_head_y_offset=", m6_detector_sensor_head_y_offset));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_arm_width_y=", m6_detector_net_connector_arm_width_y));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_arm_t_z=", m6_detector_net_connector_arm_t_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_leg_width_y=", m6_detector_net_connector_leg_width_y));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_leg_t_x=", m6_detector_net_connector_leg_t_x));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_post_overlap_x=", m6_detector_net_connector_post_overlap_x));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_socket_outer_d=", m6_detector_net_connector_socket_outer_d));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_socket_clearance_d=", m6_detector_net_connector_socket_clearance_d));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_socket_overlap_z=", m6_detector_net_connector_socket_overlap_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_post_bolt_d=", m6_detector_net_connector_post_bolt_d));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_post_bolt_y=", m6_detector_net_connector_post_bolt_y));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_arm_width_y=", m6_detector_direct_mount_arm_width_y));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_arm_t_z=", m6_detector_direct_mount_arm_t_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_web_width_y=", m6_detector_direct_mount_web_width_y));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_web_t_x=", m6_detector_direct_mount_web_t_x));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_post_overlap_x=", m6_detector_direct_mount_post_overlap_x));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_outer_d=", m6_detector_direct_mount_socket_outer_d));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_clearance_d=", m6_detector_direct_mount_socket_clearance_d));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_tap_d=", m6_detector_direct_mount_socket_tap_d));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_enabled=", m6_detector_direct_mount_enabled ? 1 : 0));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_base_overlap_z=", m6_detector_direct_mount_socket_base_overlap_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_nut_loading_clearance_z=", m6_detector_direct_mount_nut_loading_clearance_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_bottom_clearance_z=", m6_detector_direct_mount_socket_bottom_clearance_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_top_clearance_z=", m6_detector_direct_mount_socket_top_clearance_z));
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
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_min_x=", m6_detector_shell_support_boss_min_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_max_x=", m6_detector_shell_support_boss_max_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_min_y=", m6_detector_shell_support_boss_min_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_max_y=", m6_detector_shell_support_boss_max_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_center_x=", m6_detector_shell_support_boss_center_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_center_y=", m6_detector_shell_support_boss_center_y));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_bottom_z=", m6_detector_shell_support_boss_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_top_z=", m6_detector_shell_support_boss_top_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_boss_center_z=", m6_detector_shell_support_boss_center_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_min_x=", m6_detector_shell_support_gusset_min_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_max_x=", m6_detector_shell_support_gusset_max_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_root_y_start_positive=", m6_detector_shell_support_gusset_root_y_start_positive));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_wall_y_start_positive=", m6_detector_shell_support_gusset_wall_y_start_positive));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_bottom_z=", m6_detector_shell_support_gusset_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_gusset_top_z=", m6_detector_shell_support_gusset_top_z));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_hole_entry_x=", m6_detector_shell_support_hole_entry_x));
    echo(str("NETSTAND_PARAM m6_detector_shell_support_hole_center_x=", m6_detector_shell_support_hole_center_x));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_center_x=", m6_detector_ballhead_center_x));
    echo(str("NETSTAND_PARAM m6_detector_mount_x_offset=", m6_detector_mount_x_offset));
    echo(str("NETSTAND_PARAM m6_detector_assembly_ballhead_center_x=", m6_detector_assembly_ballhead_center_x));
    echo(str("NETSTAND_PARAM m6_detector_assembly_optical_axis_x=", m6_detector_assembly_optical_axis_x));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_center_y=", m6_detector_ballhead_center_y));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_center_z=", m6_detector_ballhead_center_z));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_base_center_z=", m6_detector_ballhead_base_center_z));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_net_stud_center_z=", m6_detector_ballhead_net_stud_center_z));
    echo(str("NETSTAND_PARAM m6_detector_assembly_ballhead_center_z=", m6_detector_assembly_ballhead_center_z));
    echo(str("NETSTAND_PARAM m6_detector_assembly_ballhead_base_center_z=", m6_detector_assembly_ballhead_base_center_z));
    echo(str("NETSTAND_PARAM m6_detector_assembly_ballhead_net_stud_center_z=", m6_detector_assembly_ballhead_net_stud_center_z));
    echo(str("NETSTAND_PARAM m6_detector_assembly_ballhead_net_interface_bottom_z=", m6_detector_assembly_ballhead_net_interface_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_sensor_stud_center_x=", m6_detector_ballhead_sensor_stud_center_x));
    echo(str("NETSTAND_PARAM m6_detector_ballhead_net_interface_bottom_z=", m6_detector_ballhead_net_interface_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_interface_height_z=", m6_detector_net_connector_interface_height_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_socket_bottom_z=", m6_detector_net_connector_socket_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_socket_top_z=", m6_detector_net_connector_socket_top_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_socket_height_z=", m6_detector_net_connector_socket_height_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_socket_center_z=", m6_detector_net_connector_socket_center_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_arm_min_x=", m6_detector_net_connector_arm_min_x));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_post_inner_face_x=", m6_detector_net_connector_post_inner_face_x));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_arm_max_x=", m6_detector_net_connector_arm_max_x));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_arm_bottom_z=", m6_detector_net_connector_arm_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_arm_top_z=", m6_detector_net_connector_arm_top_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_leg_min_x=", m6_detector_net_connector_leg_min_x));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_leg_max_x=", m6_detector_net_connector_leg_max_x));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_leg_bottom_z=", m6_detector_net_connector_leg_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_leg_top_z=", m6_detector_net_connector_leg_top_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_leg_height_z=", m6_detector_net_connector_leg_height_z));
    echo(str("NETSTAND_PARAM m6_detector_net_connector_mount_height_z=", m6_detector_net_connector_mount_height_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_bottom_z=", m6_detector_direct_mount_socket_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_top_z=", m6_detector_direct_mount_socket_top_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_height_z=", m6_detector_direct_mount_socket_height_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_center_z=", m6_detector_direct_mount_socket_center_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_thread_tap_d=", m6_detector_direct_mount_thread_tap_d));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_thread_depth_z=", m6_detector_direct_mount_thread_depth_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_thread_bottom_z=", m6_detector_direct_mount_thread_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_thread_top_z=", m6_detector_direct_mount_thread_top_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_thread_depth_extra_z=", m6_detector_direct_mount_thread_depth_extra_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_socket_center_x=", m6_detector_direct_mount_socket_center_x));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_nut_pocket_bottom_z=", m6_detector_direct_mount_nut_pocket_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_nut_pocket_center_z=", m6_detector_direct_mount_nut_pocket_center_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_nut_loading_depth_z=", m6_detector_direct_mount_nut_loading_depth_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_arm_min_x=", m6_detector_direct_mount_arm_min_x));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_post_inner_face_x=", m6_detector_direct_mount_post_inner_face_x));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_arm_max_x=", m6_detector_direct_mount_arm_max_x));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_arm_bottom_z=", m6_detector_direct_mount_arm_bottom_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_arm_top_z=", m6_detector_direct_mount_arm_top_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_lower_post_top_z=", m6_detector_direct_mount_lower_post_top_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_web_min_x=", m6_detector_direct_mount_web_min_x));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_web_max_x=", m6_detector_direct_mount_web_max_x));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_web_min_z=", m6_detector_direct_mount_web_min_z));
    echo(str("NETSTAND_PARAM m6_detector_direct_mount_web_max_z=", m6_detector_direct_mount_web_max_z));
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
    stand(1);
    stand(-1);
    m6_beam_preview();
    // The complete assembly includes the real electronics in their two
    // trapezoid clamp cavities.  Dedicated section/explosion PARTs below are
    // used for close inspection because the whole stand is a very large view.
    clamp_electronics_system_preview();
    if (m6_show_optical_direction) {
        m6_optical_full_direction_preview();
    }
    // PVDF 座位于左右网端、靠近立柱但与立柱留开；网布上沿是它唯一的
    // 安装基准，网顶不设置贯通轨道。
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
} else if (PART == "post_clamp_carrier") {
    sided(default_side) post_clamp_carrier_positive();
} else if (PART == "lower_stand_segment") {
    sided(default_side) lower_stand_segment_positive();
} else if (PART == "clamp_body_segment") {
    sided(default_side) clamp_body_segment_positive();
} else if (PART == "upper_stand_segment") {
    sided(default_side) upper_stand_segment_positive();
} else if (PART == "post_joint_sleeve") {
    sided(default_side) post_joint_sleeve_positive();
} else if (PART == "post_joint_key") {
    sided(default_side) post_joint_key_positive();
} else if (PART == "post_clamp_slide_exploded") {
    sided(default_side) post_clamp_slide_exploded_positive();
} else if (PART == "post_clamp_slide_interface_exploded") {
    sided(default_side) post_clamp_slide_interface_exploded_positive();
} else if (PART == "post_down_extension_stage1") {
    sided(default_side) post_down_extension_stage1_positive();
} else if (PART == "post_down_extension_stage1_raw") {
    sided(default_side) post_down_extension_stage1_raw_positive();
} else if (PART == "post_down_extension_stage1_exploded") {
    sided(default_side) post_down_extension_stage1_exploded_positive();
} else if (PART == "post_skp_leg_foot_stage1") {
    sided(default_side) post_skp_leg_foot_stage1_positive();
} else if (PART == "post_skp_leg_foot_stage1_raw") {
    sided(default_side) post_skp_leg_foot_stage1_raw_positive();
} else if (PART == "post_skp_leg_foot_stage1_exploded") {
    sided(default_side) post_skp_leg_foot_stage1_exploded_positive();
} else if (PART == "post_skp_leg_foot_fit_tool") {
    sided(default_side) post_skp_leg_foot_fit_tool_positive();
} else if (PART == "clamp_body_skp_leg_foot_fit") {
    sided(default_side) clamp_body_skp_leg_foot_fit_positive();
} else if (PART == "post_skp_leg_foot_clamp_fit") {
    sided(default_side) post_skp_leg_foot_clamp_fit_positive();
} else if (PART == "post_clamp_seated") {
    sided(default_side) post_clamp_seated_positive();
} else if (PART == "post_clamp_seated_fit_section") {
    sided(default_side) post_clamp_seated_fit_section_positive();
} else if (PART == "post_clamp_entry_open_section") {
    sided(default_side) post_clamp_entry_open_section_positive();
} else if (PART == "post_clamp_fit_collision_probe") {
    sided(default_side) post_clamp_fit_collision_probe_positive();
} else if (PART == "post_clamp_fit_collision_probe_at_offset") {
    sided(default_side) post_clamp_fit_collision_probe_at_offset_positive();
} else if (PART == "clamp_slide_post_foot_detent_detail") {
    sided(default_side) clamp_slide_post_foot_detent_detail_positive();
} else if (PART == "clamp_slide_post_foot_transition_test") {
    // Geometry-only diagnostic for the actual continuous pants-shaped foot;
    // keep this entry point on the same solid as the formal carrier so a
    // focused transition preview cannot resurrect the retired stepped cheeks.
    sided(default_side) clamp_slide_post_foot_positive();
	} else if (PART == "clamp_slide_post_foot_pants_test") {
	    // Geometry-only diagnostic for the complete pants-shaped foot: two
	    // continuous legs plus the single central crotch web.  It is not a
	    // formal print item and is intentionally absent from the export matrix.
	    sided(default_side) clamp_slide_post_foot_positive();
		} else if (PART == "clamp_slide_post_foot_pants_raw_test") {
		    // Topology diagnostic: inspect the pants loft before the single detent
		    // pocket is cut.  This is never a printable/exported part.
		    sided(default_side) clamp_slide_post_foot_pants_positive();
		} else if (PART == "clamp_slide_post_foot_leg_test") {
		    sided(default_side)
		        clamp_slide_post_foot_leg_test_positive(default_side);
		} else if (PART == "clamp_slide_post_foot_legs_test") {
		    sided(default_side) clamp_slide_post_foot_legs_test_positive();
		} else if (PART == "clamp_slide_post_foot_union_test") {
    sided(default_side) clamp_slide_post_foot_union_test_positive();
	} else if (PART == "clamp_slide_post_foot_post_union_test") {
	    sided(default_side)
	        clamp_slide_post_foot_union_test_positive(true, false);
	} else if (PART == "clamp_slide_post_foot_raw_post_union_test") {
	    sided(default_side) clamp_slide_post_foot_raw_post_union_test_positive();
	} else if (PART == "clamp_slide_post_foot_raw_post_cut_test") {
	    sided(default_side) clamp_slide_post_foot_raw_post_cut_test_positive();
	} else if (PART == "clamp_slide_post_foot_raw_post_net_passage_test") {
	    sided(default_side)
	        clamp_slide_post_foot_raw_post_single_cut_test_positive(0);
	} else if (PART == "clamp_slide_post_foot_raw_post_channel_test") {
	    sided(default_side)
        clamp_slide_post_foot_raw_post_single_cut_test_positive(1);
	} else if (PART == "clamp_slide_post_foot_raw_post_slots_test") {
	    sided(default_side)
        clamp_slide_post_foot_raw_post_single_cut_test_positive(2);
	} else if (PART == "clamp_slide_post_foot_rail_union_test") {
    sided(default_side)
        clamp_slide_post_foot_union_test_positive(false, true);
} else if (PART == "clamp_slide_post_foot_tie_test") {
    sided(default_side) clamp_slide_post_foot_tie_test_positive();
} else if (PART == "clamp_slide_post_foot_tie_cheek_test") {
    sided(default_side) clamp_slide_post_foot_tie_cheek_test_positive(default_side);
} else if (PART == "post_joint_exploded") {
    post_joint_exploded(default_side);
} else if (PART == "clamp_slide_exploded") {
    clamp_slide_exploded(default_side);
} else if (PART == "clamp_slide_fit_probe") {
    sided(default_side) clamp_slide_fit_probe_positive();
} else if (PART == "clamp_slide_fit_section") {
    sided(default_side) clamp_slide_fit_section_positive();
} else if (PART == "table_clamp") {
    sided(default_side) table_clamp_positive();
} else if (PART == "table_clamp_section") {
    sided(default_side) table_clamp_section_positive();
} else if (PART == "table_clamp_body") {
    sided(default_side) table_clamp_body_positive();
} else if (PART == "clamp_electronics_cover") {
    sided(default_side) clamp_electronics_cover_positive();
} else if (PART == "clamp_electronics_gasket") {
    sided(default_side) clamp_electronics_gasket_positive();
} else if (PART == "clamp_electronics_ui_panel") {
    sided(default_side) clamp_electronics_ui_panel_positive();
} else if (PART == "clamp_electronics_ui_bezel") {
    sided(default_side) clamp_electronics_ui_bezel_positive();
} else if (PART == "clamp_electronics_emitter_preview") {
    sided(default_side) clamp_electronics_emitter_preview_positive();
} else if (PART == "clamp_electronics_emitter_fit_preview") {
    sided(default_side) clamp_electronics_emitter_fit_preview_positive();
} else if (PART == "clamp_electronics_system_preview") {
    clamp_electronics_system_preview();
} else if (PART == "clamp_electronics_system_exploded") {
    clamp_electronics_system_exploded();
} else if (PART == "clamp_electronics_exploded") {
    sided(default_side) clamp_electronics_exploded_positive();
} else if (PART == "clamp_electronics_emitter_exploded") {
    sided(default_side) clamp_electronics_emitter_exploded_positive();
} else if (PART == "clamp_electronics_full_cutaway") {
    sided(default_side) clamp_electronics_full_cutaway_positive();
} else if (PART == "clamp_electronics_interference_check") {
    sided(default_side) clamp_electronics_interference_check_positive();
} else if (PART == "m6_receiver_carrier_interference_check") {
    sided(default_side) m6_receiver_carrier_interference_check_positive();
} else if (PART == "clamp_electronics_shell_cutaway") {
    sided(default_side) clamp_electronics_shell_cutaway_positive();
} else if (PART == "clamp_electronics_m6_integration_preview") {
    sided(default_side) clamp_electronics_m6_integration_preview_positive(false);
} else if (PART == "table_clamp_electronics_preview") {
    sided(default_side) clamp_electronics_fit_preview_positive();
} else if (PART == "table_clamp_electronics_cutaway_preview") {
    sided(default_side) clamp_electronics_cutaway_preview_positive();
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
} else if (PART == "m6_detector_wiring_reference") {
    sided(default_side) m6_detector_cable_routing_reference_positive();
} else if (PART == "m6_detector_cable_gland") {
    sided(default_side) m6_detector_cable_gland_positive();
} else if (PART == "m6_detector_bottom_gasket") {
    sided(default_side) m6_detector_bottom_gasket_positive();
} else if (PART == "net_clamp_clip") {
    sided(default_side) net_clamp_clip_printable_positive();
} else if (PART == "net_clamp_rod") {
    sided(default_side) net_clamp_rod_positive();
} else if (PART == "net_clamp_fit_probe") {
    sided(default_side) {
        net_clamp_fit_probe_positive();
    }
} else if (PART == "net_clamp_fit_section") {
    sided(default_side) net_clamp_fit_section_positive();
} else if (PART == "m6_detector_net_connector") {
    sided(default_side) m6_detector_net_connector_positive();
} else if (PART == "m6_detector_mount") {
    sided(default_side) m6_detector_assembly_positive();
    if (m6_show_optical_direction) {
        m6_optical_direction_assembly_preview(default_side);
    }
} else if (PART == "m6_detector_exploded") {
    sided(default_side) m6_detector_exploded_assembly_positive();
    if (m6_show_optical_direction) {
        m6_optical_exploded_direction_assembly_preview(default_side);
    }
} else if (PART == "m6_detector_backplate") {
    sided(default_side) m6_detector_shell_rear_positive();
} else if (PART == "m6_ballhead") {
    sided(default_side) m6_detector_ballhead_positive();
} else if (PART == "m6_ballhead_mount") {
    sided(default_side) m6_detector_assembly_positive();
} else if (PART == "m6_gimbal") {
    m6_gimbal(default_side);
} else if (PART == "m6_machining_detector_body") {
    sided(default_side) m6_machining_detector_body_positive();
} else if (PART == "m6_machining_rail") {
    sided(default_side) m6_machining_rail_positive();
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
