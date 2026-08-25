# 内置式球网支架首样打印与装配清单

这份清单只说明当前 `net_stand.scad` 的导出关系，不代表 PETG 实物已经打印、桌下夹持力已经合格，或光学/电气已经接通。当前结构是免打孔夹持：固定 C 形夹体跨过台边，M8 螺杆完全位于台面下方并顶起可动压块；不得把球台打孔作为安装前提。打印前仍需按实际喷嘴、层高、PETG 收缩、球台厚度和标准件尺寸复核。

## 当前主线：替换传统球网

| `PART` | 首样数量 | 处理方式 |
| --- | ---: | --- |
| `right_stand` | 1 | PETG 结构装配检查件；包含右侧立柱、桌下夹持、网顶承托座和 STG-120ML 外侧托架；PVDF 座单独导出 |
| `left_stand` | 1 | PETG 结构装配检查件；为 `right_stand` 的镜像侧；STG-120ML 托架和 PVDF 座单独导出 |
| `post` | 2 | 立柱装配预览，不建议直接作为单件打印；当前按两段立柱、外套筒和内芯分件 |
| `post_segment` | 2 | PETG；左右各 1 件，导出 `post_segment_index=1` 的上段，约 153 mm |
| `lower_stand_segment` | 2 | PETG；左右各 1 件，包含 `post_segment_index=0` 下段与固定 C 形夹，首样一体打印避免分件相互干涉 |
| `post_joint_sleeve` | 2 | PETG；左右各一件，跨接两段立柱接缝 |
| `post_joint_key` | 2 | PETG；左右各一件，插入外套筒内部并定位接缝 |
| `table_clamp` | 2 | 装配预览，不建议直接作为单件打印；包含固定夹体、台底压块、M8×1.25 螺杆和旋钮边界 |
| `clamp_top_pad` | 2 | TPU/硅胶优先，归入 `TPU/柔性` 打印盘；左右各一件，位于固定上夹板与台面之间的可替换保护垫，不承担 C 形夹结构力路 |
| `clamp_pressure_pad` | 2 | TPU/硅胶/耐磨软垫优先，归入 `TPU/柔性` 打印盘；即使先打 PETG 几何样件，也不与 PETG 结构件共盘，左右各一件，独立位于台底 |
| `clamp_screw` | 2 | 非打印件；M8×1.25 竖直金属螺杆/圆头顶端，完全在台面下方，圆头只接触台底可动压块，不穿球台或压块 |
| `clamp_body_nut` | 2 | 非打印件；左右各 1 枚 M8 六角螺母，捕获在固定下臂的螺母座内，避免依赖 PETG 螺纹 |
| `clamp_knob` | 2 | PETG 打印旋钮；左右各一件，含 M8 通孔和两枚对锁螺母捕获窝，旋钮随螺杆转动 |
| `clamp_knob_nut` | 4 | 非打印件；左右各 2 枚 M8 六角螺母，先在螺杆下端对锁，再装入旋钮捕获窝，避免固定下臂与旋钮形成未定义的双螺纹约束 |
| `net_rail` | 1 | 三段网顶承载条装配预览；不建议整件打印 |
| `net_rail_segment` | 3 | PETG；每段约 536 mm、相邻搭接 20 mm；也可按同一接口改用铝型材 |
| `net_rail_splice` | 2 | PETG；每个接缝一片，带 Ø3.2 mm M3 通孔；M3 螺钉/螺母为标准件 |
| `net_rail_saddle` | 2 | PETG；左右各一件，跨入立柱内侧并承托网顶承载条，带立柱侧端部限位 |
| `stg120_outer_carrier` | 2 | PETG；左右各一件，包住 STG-120ML 约 130×19×6 mm 外形，窗口朝向球台中心 |
| `stg120_center_bridge` | 1 | PETG；中央背靠背支撑桥，同时承载左右两段的中央光纤头 |
| `stg120_preview` | 1 | 装配预览，不直接打印；显示两段光路和 32 个 3.87 mm 光点位置 |
| `sensor_mount` | 2 | 装配预览，不直接打印；包含座体、PVDF 薄膜和可拆压片的关系 |
| `sensor_mount_body` | 2 | PETG；左右各一枚，只打印安装座本体，薄膜和压片另装 |
| `sensor_clamp_lip` | 2 | PETG/TPU 试样，首样归入 `TPU/柔性` 打印盘；左右各一套可拆压片，夹住 `pvdf_film` 两侧，不把薄膜永久粘死 |
| `pvdf_film` | 2 | 非打印件；PVDF 薄膜包络，首样按实物裁切并保留可替换性 |
| `calibration_gauge` | 1 | PETG；共享的 STG-120ML 3.87 mm 光点间距高度标定规 |
| `net` | 1 | 非打印件；使用真实球网/网布装配，OpenSCAD 只显示占位几何 |

`assembly` 是整体关系预览，不建议直接导出成一件打印；`left_stand`/`right_stand` 也主要用于装配、干涉和桌下夹持检查。当前首样下段明确使用 `lower_stand_segment` 一体件，上段再与 `post_joint_sleeve`、`post_joint_key` 连接；不要把独立 `post_segment_index=0` 和独立夹体混合装配。STG-120ML 光纤头、配套放大器、PVDF、AFE、线束、ESP32-S3、M8 螺杆、固定下臂螺母、每侧两枚旋钮对锁螺母和网布属于非 CAD 打印件或标准件；压块软垫必须按实物材料单独确认。旋钮和螺杆的接口现在由 CAD 明确为“固定下臂 M8 螺母 + 旋钮内两枚预先对锁的 M8 螺母 + M8 圆头螺杆”，不使用 PETG 内螺纹或不明确的双固定螺纹。

`table_clamp_section` 只用于桌板剖面核对：灰色区域是桌板实体，上表面可替换保护垫位于固定上夹板与桌面之间，台底黑色/软色压块位于桌底下方，圆头螺杆只顶台底压块，固定下臂螺母和旋钮内两枚对锁螺母都在桌板下方。它不是新增打印件，也不改变 `table_clamp` 的免打孔装配关系。

## 导出示例

```text
openscad -D 'PART="post"' -D 'SIDE=1' -o right-post.stl net_stand.scad
openscad -D 'PART="post"' -D 'SIDE=-1' -o left-post.stl net_stand.scad
openscad -D 'PART="lower_stand_segment"' -D 'SIDE=1' -o right-lower-stand-segment.stl net_stand.scad
openscad -D 'PART="post_segment"' -D 'SIDE=1' -D 'post_segment_index=1' -o right-post-upper.stl net_stand.scad
openscad -D 'PART="post_joint_sleeve"' -D 'SIDE=1' -o right-post-sleeve.stl net_stand.scad
openscad -D 'PART="post_joint_key"' -D 'SIDE=1' -o right-post-key.stl net_stand.scad
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
openscad -D 'PART="stg120_outer_carrier"' -D 'SIDE=1' -o right-stg120-outer-carrier.stl net_stand.scad
openscad -D 'PART="stg120_outer_carrier"' -D 'SIDE=-1' -o left-stg120-outer-carrier.stl net_stand.scad
openscad -D 'PART="stg120_center_bridge"' -o stg120-center-bridge.stl net_stand.scad
openscad -D 'PART="stg120_preview"' -o stg120-preview.stl net_stand.scad
openscad -D 'PART="sensor_mount"' -D 'SIDE=1' -o right-pvdf-mount.stl net_stand.scad
openscad -D 'PART="sensor_mount_body"' -D 'SIDE=1' -o right-pvdf-mount-body.stl net_stand.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_stand.scad
```

批量导出首样打印包：

```text
python3 export_net_stand_printables.py --clean
python3 test_export_net_stand_printables.py
```

默认输出到 Git 忽略目录 `exports/net-stand-v0.1/`。其中 `manifest.json` 固化每个 STL 的 `PART`、定义、左右侧、单位、材料组、包围盒和封闭拓扑摘要；`--clean` 只清理该目录中不属于当前 29 件清单的旧 STL，避免旧外挂/旧光学载台零件混入打印包；它只导出独立打印件，不把球台、网布、PVDF 薄膜、STG-120ML 光纤头、配套放大器或组合装配预览误当作 PETG 单件。

打印后先做无网桌下夹持检查，再装网布、网顶 PVDF 和光学模块。M8 螺杆按 `M8×1.25` 标准件采购或确认，不能用 PETG 内螺纹替代。没有 M-01/M-02/M-03 的照片、量具读数和记录文件时，现场记录状态必须保持 `pending`。

## 机械首样顺序

1. 用 `lower_stand_segment`、`clamp_top_pad`、`clamp_pressure_pad`、每侧三枚标准 M8 螺母（1 枚固定下臂 + 2 枚旋钮对锁）和一段与实物相同厚度的台面样块检查上夹板保护、台底压块、圆头螺杆行程、旋钮驱动和两侧软垫压痕；
2. 先将左右各自的 `lower_stand_segment` 与上段 `post_segment_index=1` 用 `post_joint_key` 和 `post_joint_sleeve` 定位装配，再确认夹持后立柱不明显倾斜或滑移；
3. 把左右 `net_rail_saddle` 装到立柱内侧，拼接 3 段 `net_rail_segment` 成 `net_rail`，确认承载条落在承托座且被端挡限位，再安装真实网布，记录网顶高度、网布张力和两侧平行度；
4. 安装两侧 `stg120_outer_carrier` 和中央 `stg120_center_bridge`，装入两段 STG-120ML 光纤头；每段先按约 763 mm 跨度对向，检查窗口、线缆弯曲和中央桥净空，再用 3.87 mm 标定规记录高度基准；放大器输出语义和电流尚未冻结，不得直接生成逐光束位图；
5. 只有完成机械记录后，才把 `assembly` 的参数继续收敛为下一版打印尺寸。

## 历史方案边界

`net_post_x_clamp.scad` 及其旧打印清单属于前一轮外挂式 X 夹具，保留用于回溯和旧几何回归；不要把旧的 `arm`、`jaw`、`roller_mount`、`reference_carriage` 等零件混入当前内置支架首样。详见 [`legacy/README.md`](legacy/README.md)。
