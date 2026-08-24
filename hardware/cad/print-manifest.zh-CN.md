# 内置式球网支架首样打印与装配清单

这份清单只说明当前 `net_stand.scad` 的导出关系，不代表 PETG 实物已经打印、桌下夹持力已经合格，或光学/电气已经接通。打印前仍需按实际喷嘴、层高、PETG 收缩、球台厚度和标准件尺寸复核。

## 当前主线：替换传统球网

| `PART` | 首样数量 | 处理方式 |
| --- | ---: | --- |
| `right_stand` | 1 | PETG 装配检查件；包含右侧立柱、桌下夹持、光学模块包络和 PVDF 安装座 |
| `left_stand` | 1 | PETG 装配检查件；为 `right_stand` 的镜像侧 |
| `post` | 2 | PETG；若拆分打印，左右各一件，实际加强肋/分体面待打印方向确认 |
| `table_clamp` | 2 | PETG；左右各一件；M8 竖直螺杆、旋钮和上下接触软垫使用实物件/替换件 |
| `net_rail` | 1 | PETG 或后续改为铝型材；承载网顶白边和两枚 PVDF 安装座 |
| `optical_strip` | 2 | PETG；左右各一条；电子光学模块不打印，用包络验证安装空间 |
| `sensor_mount` | 2 | PETG/TPU 组合首样；左右各一枚，PVDF 薄膜和线束按实物固定 |
| `calibration_gauge` | 1 | PETG；共享的 +10…+100 mm 十档高度标定规 |
| `net` | 1 | 非打印件；使用真实球网/网布装配，OpenSCAD 只显示占位几何 |

`assembly` 是整体关系预览，不建议直接导出成一件打印；`left_stand`/`right_stand` 也主要用于装配、干涉和桌下夹持检查，必要时再按切片结果拆分 `post` 与 `table_clamp`。光栅发射器/接收器、PVDF、AFE、线束、ESP32-S3、M8 螺杆、旋钮轴件、夹持软垫和网布属于非 CAD 打印件或标准件。

## 导出示例

```text
openscad -D 'PART="post"' -D 'SIDE=1' -o right-post.stl net_stand.scad
openscad -D 'PART="post"' -D 'SIDE=-1' -o left-post.stl net_stand.scad
openscad -D 'PART="table_clamp"' -D 'SIDE=1' -o right-clamp.stl net_stand.scad
openscad -D 'PART="table_clamp"' -D 'SIDE=-1' -o left-clamp.stl net_stand.scad
openscad -D 'PART="net_rail"' -o net-rail.stl net_stand.scad
openscad -D 'PART="optical_strip"' -D 'SIDE=-1' -o left-optical-strip.stl net_stand.scad
openscad -D 'PART="sensor_mount"' -D 'SIDE=1' -o right-pvdf-mount.stl net_stand.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_stand.scad
```

打印后先做无网桌下夹持检查，再装网布、网顶 PVDF 和光学模块。没有 M-01/M-02/M-03 的照片、量具读数和记录文件时，现场记录状态必须保持 `pending`。

## 机械首样顺序

1. 用 `table_clamp` 和一段与实物相同厚度的台面样块检查上下夹持面、螺杆行程和软垫压痕；
2. 安装左右 `post`，确认夹持后立柱不明显倾斜或滑移；
3. 安装 `net_rail` 和真实网布，记录网顶高度、网布张力和两侧平行度；
4. 安装 `optical_strip` 的光学包络、`sensor_mount` 和参考线，再做逐光束/逐 PVDF 接板记录；
5. 只有完成机械记录后，才把 `assembly` 的参数继续收敛为下一版打印尺寸。

## 历史方案边界

`net_post_x_clamp.scad` 及其旧打印清单属于前一轮外挂式 X 夹具，保留用于回溯和旧几何回归；不要把旧的 `arm`、`jaw`、`roller_mount`、`reference_carriage` 等零件混入当前内置支架首样。详见 [`legacy/README.md`](legacy/README.md)。
