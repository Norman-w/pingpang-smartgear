# 内置式球网支架首样打印与装配清单

这份清单只说明当前 `net_stand.scad` 的导出关系，不代表 PETG 实物已经打印、桌下夹持力已经合格，或光学/电气已经接通。当前结构是免打孔夹持：固定 C 形夹体跨过台边，M8 螺杆完全位于台面下方并顶起可动压块；不得把球台打孔作为安装前提。打印前仍需按实际喷嘴、层高、PETG 收缩、球台厚度和标准件尺寸复核。

## 当前主线：替换传统球网

| `PART` | 首样数量 | 处理方式 |
| --- | ---: | --- |
| `right_stand` | 1 | PETG 结构装配检查件；包含右侧立柱、桌下夹持、网顶承托座和 M6 PETG 光学基座；PVDF 座单独导出 |
| `left_stand` | 1 | PETG 结构装配检查件；为 `right_stand` 的镜像侧；M6 PETG 光学基座和 PVDF 座单独检查 |
| `post` | 2 | 立柱装配预览；当前每侧只保留直立上移到球头承托面的浅黄色下段、固定 C 形夹和最高水平面一体 M8 球头承座，不再装配深黄色上段 |
| `post_segment` | 0 | 旧版两段立柱兼容诊断入口；深黄色上段不进入当前打印清单 |
| `lower_stand_segment` | 2 | PETG；左右各 1 件，直立的浅黄色下段、固定 C 形夹和与立柱中心同轴的顶面一体 M8 球头承座合并打印，蓝色检测器/球头总成沿 x 对正后直接落在此承座上，不使用横向黄色承托臂；桌面夹持开口、压块和螺杆区域保留，桌边外侧非接触区沿 y 全深做成实心桥体，上下结构夹臂均为 12 mm，灰色下部支撑靠台侧厚 40 mm、外侧收口为 12 mm 并形成斜底；M8 夹紧丝杆相对原包络加长 12 mm |
| `net_clamp_rod` | 2 | PETG；左右各 1 根独立卡网圆柱；网布先沿 x 穿过立柱主体 y 向 `3 mm` 过道、再从外侧放入 U 形槽，圆柱沿 x 推入锁住；Ø14 mm 仅作干涉校核，实际打印圆柱为 Ø12 mm（直径小 2 mm） |
| `post_joint_sleeve` | 0 | 旧版两段立柱接缝兼容诊断入口；当前不再使用 |
| `post_joint_key` | 0 | 旧版两段立柱接缝兼容诊断入口；当前不再使用 |
| `table_clamp` | 2 | 装配预览，不建议直接作为单件打印；包含固定夹体、台底压块、M8×1.25 螺杆和旋钮边界 |
| `clamp_top_pad` | 2 | TPU/硅胶优先，归入 `TPU/柔性` 打印盘；左右各一件，位于固定上夹板与台面之间的可替换保护垫，不承担 C 形夹结构力路 |
| `clamp_pressure_pad` | 2 | TPU/硅胶/耐磨软垫优先，归入 `TPU/柔性` 打印盘；即使先打 PETG 几何样件，也不与 PETG 结构件共盘，左右各一件，独立位于台底 |
| `clamp_screw` | 2 | 非打印件；加长的 M8×1.25 竖直金属螺杆/圆头顶端，完全在台面下方，圆头只接触台底可动压块，不穿球台或压块 |
| `clamp_body_nut` | 2 | 非打印件；左右各 1 枚 M8 六角螺母，捕获在固定下臂的螺母座内，避免依赖 PETG 螺纹 |
| `clamp_knob` | 2 | PETG 打印旋钮；左右各一件，含 M8 通孔和两枚对锁螺母捕获窝，旋钮随螺杆转动 |
| `clamp_knob_nut` | 4 | 非打印件；左右各 2 枚 M8 六角螺母，先在螺杆下端对锁，再装入旋钮捕获窝，避免固定下臂与旋钮形成未定义的双螺纹约束 |
| `net_rail` | 1 | 三段网顶承载条装配预览；不建议整件打印 |
| `net_rail_segment` | 3 | PETG；名义总跨度 `1830 mm`，每段约 `623.33 mm`、相邻搭接 `20 mm`；也可按同一接口改用铝型材 |
| `net_rail_splice` | 2 | PETG；每个接缝一片，带 Ø3.2 mm M3 通孔；M3 螺钉/螺母为标准件 |
| `net_rail_saddle` | 2 | PETG；左右各一件，跨入立柱内侧并承托网顶承载条，带立柱侧端部限位 |
| `m6_detector_body` | 2 | PETG 首样打印件，后续可按同一包络改 CNC；简单矩形 `10×56×216 mm`，含 10 个 `20 mm` 节距的 x 向光学让位、绕 x 轴 -45° 的尾线让位和浅六角定位沉孔；主体不带 T 尾座或主体 M8 孔 |
| `m6_detector_shell_front` / `m6_detector_shell_rear` / `m6_detector_bottom_cover` | 各 2 | PETG 壳体候选件；前盖为 x− 端正圆弧、后盖与前盖接驳边为直角且仅自身 x+ 后部两角圆滑，并在背面中央（y=0、z 中心）带加厚 M8 boss，底盖同步采用组合俯视轮廓；当前仍需真实主体/线缆/球头首样复核后放行打印 |
| `m6_sensor_array` | 2 | 外购器件包络预览，不直接打印；左右各 10 枚 M6 直角对射器件，光学面沿 x 朝球台中心，尾线局部 z- 后绕 x 轴 -45°，单列中心距 20 mm，从各自外侧 x 方向进入 |
| `m6_detector_mount` | 2 | 左右完整装配预览，不直接打印；包括 45° L 型 PETG 主体、x− 正圆弧前盖、接驳边直角且仅后端圆角的 x+ 后盖、组合轮廓底盖、后盖 M8 boss 和竖直采购 13 mm 球头 |
| `m6_ballhead` | 2 | 外购件包络预览，不直接打印；采购球头保持竖直姿态，按 `13mm球【1/4内牙】`、`13mm球【1/4外牙】`、`13mm球【3/8外牙】`、`13mm球【M6外牙】`、`13mm球【M8外牙】`、`13mm球【M10外牙】` 选型；球头 z− 接口直接拧入浅黄色直立下段顶面的同轴 M8 承座，检测器/球头总成沿 x 移到立柱中心，不使用横向黄色承托臂或深灰色独立连接器 |
| `sensor_mount` | 2 | 装配预览，不直接打印；包含座体、PVDF 薄膜和可拆压片的关系 |
| `sensor_mount_body` | 2 | PETG；左右各一枚，只打印安装座本体，薄膜和压片另装 |
| `sensor_clamp_lip` | 2 | PETG/TPU 试样，首样归入 `TPU/柔性` 打印盘；左右各一套可拆压片，夹住 `pvdf_film` 两侧，不把薄膜永久粘死 |
| `pvdf_film` | 2 | 非打印件；PVDF 薄膜包络，首样按实物裁切并保留可替换性 |
| `calibration_gauge` | 1 | PETG；历史兼容的 STG-120ML 3.87 mm 高度标定规，暂保留用于旧方案回归，不作为 M6 光学精度依据 |
| `net` | 1 | 非打印件；使用真实球网/网布装配，OpenSCAD 只显示占位几何 |

`assembly` 是整体关系预览，不建议直接导出成一件打印；`left_stand`/`right_stand` 也主要用于装配、干涉和桌下夹持检查。当前首样下段明确使用 `lower_stand_segment` 一体件，深黄色上段与两件接缝零件不再装配。下段立柱主体在网布通过处沿 x 贯穿切出 y 向 `3 mm` 过道，网布先穿过该过道并从外侧放入 U 形卡网槽，再把独立 PETG Ø12 mm 圆柱沿 x 推入；Ø14 mm 只作为干涉校核圆柱，不采购。M6 主线是用户选定的商品 SKU `6122579349941`（M6 直角对射、NPN、0–20 m）；当前按 M6×0.75 建模，光学面沿 x 朝球台中心，安装腿局部 z- 后绕 x 轴 -45°，传感器有效螺纹、外露六角、螺帽厚度、线缆出口和电气接口仍需向卖家/实物确认。M6 主体、前后盖、底盖和浅黄色下段一体承座是 PETG 首样候选，后续可改 CNC；采购 13 mm 球头与商品网夹属于外购边界，检测器/球头总成沿 x 移到立柱中心，球头 z− 接口直接拧入浅黄色直立下段顶面的同轴承座，不使用横向黄色承托臂或深灰色独立连接器。灰色桌下夹体保留桌面夹持开口、台底压块和螺杆区域；桌边外侧非接触区沿 y 全深为实心桥体，上下结构夹臂均为 12 mm，下部支撑靠台侧厚 40 mm、外侧收口为 12 mm 并形成斜底；M8 夹紧丝杆相对原包络加长 12 mm。PVDF、AFE、线束、ESP32-S3、M8 螺杆、固定下臂螺母、每侧两枚旋钮对锁螺母和网布也属于非 CAD 打印件或标准件；压块软垫必须按实物材料单独确认。旋钮和螺杆的接口现在由 CAD 明确为“固定下臂 M8 螺母 + 旋钮内两枚预先对锁的 M8 螺母 + M8 圆头螺杆”，不使用 PETG 内螺纹或不明确的双固定螺纹。

`table_clamp_section` 只用于桌板剖面核对：灰色区域是桌板实体，上表面可替换保护垫位于固定上夹板与桌面之间，台底黑色/软色压块位于桌底下方，加长圆头螺杆只顶台底压块，固定下臂螺母和旋钮内两枚对锁螺母都在桌板下方；桌边外侧非接触区为 y 全深实心桥体，上下结构夹臂均为 12 mm，下部支撑靠台侧 40 mm、外侧 12 mm 并形成斜底。它不是新增打印件，也不改变 `table_clamp` 的免打孔装配关系。

## 导出示例

```text
openscad -D 'PART="post"' -D 'SIDE=1' -o right-post.stl net_stand.scad
openscad -D 'PART="post"' -D 'SIDE=-1' -o left-post.stl net_stand.scad
openscad -D 'PART="lower_stand_segment"' -D 'SIDE=1' -o right-lower-stand-segment.stl net_stand.scad
openscad -D 'PART="net_clamp_rod"' -D 'SIDE=1' -o right-net-clamp-rod.stl net_stand.scad
openscad -D 'PART="net_clamp_rod"' -D 'SIDE=-1' -o left-net-clamp-rod.stl net_stand.scad
# post_segment/post_joint_* 仅为历史兼容诊断，不进入当前打印包。
openscad -D 'PART="clamp_top_pad"' -D 'SIDE=1' -o right-clamp-top-pad.stl net_stand.scad
openscad -D 'PART="clamp_top_pad"' -D 'SIDE=-1' -o left-clamp-top-pad.stl net_stand.scad
openscad -D 'PART="clamp_pressure_pad"' -D 'SIDE=1' -o right-pressure-pad.stl net_stand.scad
openscad -D 'PART="clamp_pressure_pad"' -D 'SIDE=-1' -o left-pressure-pad.stl net_stand.scad
openscad -D 'PART="clamp_body_nut"' -D 'SIDE=1' -o right-clamp-body-nut.stl net_stand.scad
openscad -D 'PART="clamp_knob_nut"' -D 'SIDE=1' -o right-clamp-knob-nut.stl net_stand.scad
openscad -D 'PART="clamp_knob"' -D 'SIDE=1' -o right-clamp-knob.stl net_stand.scad
openscad -D 'PART="net_rail"' -o net-rail.stl net_stand.scad
openscad -D 'PART="net_rail_segment"' -D 'rail_segment_index=0' -o net-rail-segment-0.stl net_stand.scad
openscad -D 'PART="net_rail_segment"' -D 'rail_segment_index=1' -o net-rail-segment-1.stl net_stand.scad
openscad -D 'PART="net_rail_segment"' -D 'rail_segment_index=2' -o net-rail-segment-2.stl net_stand.scad
openscad -D 'PART="net_rail_saddle"' -D 'SIDE=1' -o right-net-rail-saddle.stl net_stand.scad
openscad -D 'PART="net_rail_saddle"' -D 'SIDE=-1' -o left-net-rail-saddle.stl net_stand.scad
openscad -D 'PART="m6_sensor_array"' -D 'SIDE=1' -o right-m6-sensor-array-preview.stl net_stand.scad
openscad -D 'PART="m6_sensor_array"' -D 'SIDE=-1' -o left-m6-sensor-array-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_mount"' -D 'SIDE=1' -o right-m6-detector-mount-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_mount"' -D 'SIDE=-1' -o left-m6-detector-mount-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_body"' -D 'SIDE=1' -o right-m6-detector-body-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_shell_front"' -D 'SIDE=1' -o right-m6-detector-front-cover-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_shell_rear"' -D 'SIDE=1' -o right-m6-detector-rear-cover-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_bottom_cover"' -D 'SIDE=1' -o right-m6-detector-bottom-cover-preview.stl net_stand.scad
openscad -D 'PART="sensor_mount"' -D 'SIDE=1' -o right-pvdf-mount.stl net_stand.scad
openscad -D 'PART="sensor_mount_body"' -D 'SIDE=1' -o right-pvdf-mount-body.stl net_stand.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_stand.scad
```

批量导出首样打印包：

```text
python3 export_net_stand_printables.py --clean
python3 test_export_net_stand_printables.py
```

默认输出到 Git 忽略目录 `exports/net-stand-v0.1/`。其中 `manifest.json` 固化每个 STL 的 `PART`、定义、左右侧、单位、材料组、包围盒和封闭拓扑摘要；`--clean` 只清理该目录中不属于当前 22 件清单的旧 STL，避免旧外挂/旧光学载台零件混入打印包；它只导出独立打印件，不把球台、网布、PVDF 薄膜、M6 光电器件、采购球头、配套放大器或组合装配预览误当作 PETG 单件。

打印后先做无网桌下夹持检查，再装网布、网顶 PVDF 和光学模块。M8 螺杆按 `M8×1.25` 标准件采购或确认，不能用 PETG 内螺纹替代。没有 M-01/M-02/M-03 的照片、量具读数和记录文件时，现场记录状态必须保持 `pending`。

## 机械首样顺序

1. 用 `lower_stand_segment`、`clamp_top_pad`、`clamp_pressure_pad`、每侧三枚标准 M8 螺母（1 枚固定下臂 + 2 枚旋钮对锁）和一段与实物相同厚度的台面样块检查上夹板保护、台底压块、加长圆头螺杆行程、旋钮驱动、实心渐变下部支撑和两侧软垫压痕；
2. 先将左右各自的 `lower_stand_segment` 直接装到球台边缘并确认一体 M8 球头承座方向、夹持后立柱不明显倾斜或滑移；不再装配深黄色上段或接缝零件；
3. 把左右 `net_rail_saddle` 装到立柱内侧，拼接 3 段 `net_rail_segment` 成名义总宽 `1830 mm` 的 `net_rail`，确认左右网柱外边界各比台边外伸 `152.5 mm`、承载条落在承托座且被端挡限位；检查灰色夹体外侧实心渐变下部没有侵入桌面夹持开口，再把真实网布塞入立柱外侧 U 槽，沿 x 推入左右独立 `net_clamp_rod` 圆柱锁住，记录网顶高度、网布张力和两侧平行度；
4. 先只用一根 M6 PETG 主体、一枚真实 M6 直角对射器件和原配螺帽做主体首样装配，确认光学面水平朝球台中心、L 型安装腿朝下后绕 x 轴 -45°、斜向 7 字孔、浅 AF8 六角沉孔、有效螺纹、至少一枚螺帽的锁紧空间和 20 mm 通道节距；再试装 x− 正圆弧前盖、接驳边直角且仅后端圆角的 x+ 后盖、共享边槽舌和组合轮廓底盖，最后安装左右两侧 20 枚器件和竖直采购球头，确认检测器/球头总成沿 x 对正立柱中心、球头 z− 接口直接拧入浅黄色直立下段顶面的同轴 M8 承座且没有横向黄色承托臂，再完成偏航、俯仰、旋转微调并记录 NPN 输出/供电边界；
5. 只有完成机械记录后，才把 `assembly` 的参数继续收敛为下一版打印尺寸。

## 历史方案边界

`net_post_x_clamp.scad` 及其旧打印清单属于前一轮外挂式 X 夹具，保留用于回溯和旧几何回归；不要把旧的 `arm`、`jaw`、`roller_mount`、`reference_carriage` 等零件混入当前内置支架首样。详见 [`legacy/README.md`](legacy/README.md)。

旧的 `stg120_outer_carrier`、`stg120_center_bridge`、`stg120_preview` 和 3.87 mm `calibration_gauge` 只属于 STG-120ML 历史验证链；它们不再代表当前 M6 光学阵列的安装方式。当前首样打印包固定为 22 件，其中两根 `net_clamp_rod` 是直接打印的 PETG 卡网圆柱；M6 光电器件和采购球头按外购件单独采购；主体/壳体/底盖/浅黄色下段承座先按 PETG 打印，后续可按同一包络改 CNC。
