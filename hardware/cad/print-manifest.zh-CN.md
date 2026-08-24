# 内置式球网支架首样打印与装配清单

这份清单只说明当前 `net_stand.scad` 的导出关系，不代表 PETG 实物已经打印、桌下夹持力已经合格，或光学/电气已经接通。当前结构是免打孔夹持：固定 C 形夹体跨过台边，M8 螺杆完全位于台面下方并顶起可动压块；不得把球台打孔作为安装前提。打印前仍需按实际喷嘴、层高、PETG 收缩、球台厚度和标准件尺寸复核。

## 当前主线：替换传统球网

| `PART` | 首样数量 | 处理方式 |
| --- | ---: | --- |
| `right_stand` | 1 | PETG 结构装配检查件；包含右侧立柱、桌下夹持、网顶承托座和光学模块包络；PVDF 座单独导出 |
| `left_stand` | 1 | PETG 结构装配检查件；为 `right_stand` 的镜像侧；PVDF 座单独导出 |
| `post` | 2 | 立柱装配预览，不建议直接作为单件打印；当前按两段立柱、外套筒和内芯分件 |
| `post_segment` | 4 | PETG；左右各 2 段，每段约 153 mm；`post_segment_index=0` 下段自带台面上方承载加厚 |
| `post_joint_sleeve` | 2 | PETG；左右各一件，跨接两段立柱接缝 |
| `post_joint_key` | 2 | PETG；左右各一件，插入外套筒内部并定位接缝 |
| `table_clamp` | 2 | 装配预览，不建议直接作为单件打印；包含固定夹体、台底压块、M8 螺杆和旋钮边界 |
| `table_clamp_body` | 2 | PETG；左右各一件的固定 C 形夹体，上夹板跨过台边、下臂承载螺母座 |
| `clamp_pressure_pad` | 2 | TPU/硅胶/耐磨软垫优先，也可先用 PETG 几何样件；左右各一件，独立位于台底 |
| `clamp_screw` | 2 | 非打印件；M8 竖直螺杆/圆头顶端，完全在台面下方，圆头只接触台底可动压块，不穿球台或压块 |
| `clamp_body_nut` | 2 | 非打印件；左右各 1 枚 M8 六角螺母，捕获在固定下臂的螺母座内，避免依赖 PETG 螺纹 |
| `clamp_knob` | 2 | PETG 打印旋钮；左右各一件，含 M8 通孔和顶部六角螺母捕获窝，旋钮随螺杆转动 |
| `clamp_knob_nut` | 2 | 非打印件；左右各 1 枚 M8 六角螺母，装入旋钮捕获窝并锁住螺杆下端 |
| `net_rail` | 1 | 三段网顶承载条装配预览；不建议整件打印 |
| `net_rail_segment` | 3 | PETG；每段约 524 mm、相邻搭接 20 mm；也可按同一接口改用铝型材 |
| `net_rail_splice` | 2 | PETG；每个接缝一片，带 Ø3.2 mm M3 通孔；M3 螺钉/螺母为标准件 |
| `net_rail_saddle` | 2 | PETG；左右各一件，跨入立柱内侧并承托网顶承载条，带立柱侧端部限位 |
| `optical_rail` | 2 | PETG；左右各一条，可打印导轨本体，包含 10 个贯穿定位孔和刻度 |
| `optical_strip` | 2 | 装配预览，不直接打印；包含导轨、模块包络和载台关系，电子光学模块不打印 |
| `optical_module_carrier` | 20 | PETG；每侧 10 枚，按 `optical_module_index=0…9` 导出；U 形载台后壁带正交调节长孔，M3 紧固件为标准件 |
| `sensor_mount` | 2 | PETG/TPU 组合首样；左右各一枚，PVDF 薄膜和线束按实物固定 |
| `sensor_clamp_lip` | 2 | PETG/TPU；左右各一套可拆压片，夹住 `pvdf_film` 两侧，不把薄膜永久粘死 |
| `pvdf_film` | 2 | 非打印件；PVDF 薄膜包络，首样按实物裁切并保留可替换性 |
| `reference_carriage` | 2 | PETG；左右各一枚，作为校准时的参考线端座，不永久挡住光栅 |
| `reference_pin` | 2 | 非打印件；约 Ø3 mm 弹簧定位销，插入导轨 Ø4 mm 孔 |
| `calibration_gauge` | 1 | PETG；共享的 +10…+100 mm 十档高度标定规 |
| `net` | 1 | 非打印件；使用真实球网/网布装配，OpenSCAD 只显示占位几何 |

`assembly` 是整体关系预览，不建议直接导出成一件打印；`left_stand`/`right_stand` 也主要用于装配、干涉和桌下夹持检查。当前立柱明确按 `post_segment`、`post_joint_sleeve`、`post_joint_key` 分件导出，不能把装配预览当作单件打印件。光栅发射器/接收器、PVDF、AFE、线束、ESP32-S3、M8 螺杆、两枚 M8 螺母、旋钮轴件和网布属于非 CAD 打印件或标准件；压块软垫必须按实物材料单独确认。旋钮和螺杆的接口现在由 CAD 明确为“固定下臂 M8 螺母 + 旋钮捕获 M8 螺母 + M8 圆头螺杆”，不使用 PETG 内螺纹。

`table_clamp_section` 只用于桌板剖面核对：灰色区域是桌板实体，黑色/软色压块位于桌底下方，圆头螺杆只顶压块，固定下臂螺母和旋钮捕获螺母都在桌板下方。它不是新增打印件，也不改变 `table_clamp` 的装配关系。

## 导出示例

```text
openscad -D 'PART="post"' -D 'SIDE=1' -o right-post.stl net_stand.scad
openscad -D 'PART="post"' -D 'SIDE=-1' -o left-post.stl net_stand.scad
openscad -D 'PART="post_segment"' -D 'SIDE=1' -D 'post_segment_index=0' -o right-post-lower.stl net_stand.scad
openscad -D 'PART="post_segment"' -D 'SIDE=1' -D 'post_segment_index=1' -o right-post-upper.stl net_stand.scad
openscad -D 'PART="post_joint_sleeve"' -D 'SIDE=1' -o right-post-sleeve.stl net_stand.scad
openscad -D 'PART="post_joint_key"' -D 'SIDE=1' -o right-post-key.stl net_stand.scad
openscad -D 'PART="table_clamp_body"' -D 'SIDE=1' -o right-clamp-body.stl net_stand.scad
openscad -D 'PART="table_clamp_body"' -D 'SIDE=-1' -o left-clamp-body.stl net_stand.scad
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
openscad -D 'PART="optical_rail"' -D 'SIDE=1' -o right-optical-rail.stl net_stand.scad
openscad -D 'PART="optical_rail"' -D 'SIDE=-1' -o left-optical-rail.stl net_stand.scad
openscad -D 'PART="optical_strip"' -D 'SIDE=-1' -o left-optical-strip.stl net_stand.scad
openscad -D 'PART="optical_module_carrier"' -D 'SIDE=1' -D 'optical_module_index=4' -o right-optical-carrier-50mm.stl net_stand.scad
openscad -D 'PART="optical_module_carrier"' -D 'SIDE=-1' -D 'optical_module_index=4' -o left-optical-carrier-50mm.stl net_stand.scad
openscad -D 'PART="sensor_mount"' -D 'SIDE=1' -o right-pvdf-mount.stl net_stand.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_stand.scad
```

打印后先做无网桌下夹持检查，再装网布、网顶 PVDF 和光学模块。没有 M-01/M-02/M-03 的照片、量具读数和记录文件时，现场记录状态必须保持 `pending`。

## 机械首样顺序

1. 用 `table_clamp_body`、`clamp_pressure_pad`、两枚标准 M8 螺母和一段与实物相同厚度的台面样块检查上夹板、台底压块、圆头螺杆行程、旋钮捕获和软垫压痕；
2. 先将左右各自的两段 `post_segment` 用 `post_joint_key` 和 `post_joint_sleeve` 定位装配，再确认夹持后立柱不明显倾斜或滑移；
3. 把左右 `net_rail_saddle` 装到立柱内侧，拼接 3 段 `net_rail_segment` 成 `net_rail`，确认承载条落在承托座且被端挡限位，再安装真实网布，记录网顶高度、网布张力和两侧平行度；
4. 安装可打印的 `optical_rail`，再安装 10 个 `optical_module_carrier` 和真实收发器；`optical_strip` 只用于装配关系预览；用载台长孔做有限俯仰/偏航预调，再用 `reference_carriage`/`reference_pin` 逐档复核参考线，最后做逐光束/逐 PVDF 接板记录；
5. 只有完成机械记录后，才把 `assembly` 的参数继续收敛为下一版打印尺寸。

## 历史方案边界

`net_post_x_clamp.scad` 及其旧打印清单属于前一轮外挂式 X 夹具，保留用于回溯和旧几何回归；不要把旧的 `arm`、`jaw`、`roller_mount`、`reference_carriage` 等零件混入当前内置支架首样。详见 [`legacy/README.md`](legacy/README.md)。
