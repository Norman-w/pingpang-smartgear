# OpenSCAD CAD

当前机械主线是 `net_stand.scad`：直接做出一套替换传统球网的内置式球网支架，网布和网顶 PVDF 振动监测预装在支架上，左右端通过传统的桌下上下夹持面固定到球台。夹紧螺杆和导向座全部位于台边外侧，只夹台面边缘，不要求也不允许给球桌打孔。它不再依赖原球网立柱，也不再使用外挂式 X 夹具。

## 当前参数源：`net_stand.scad`

支持以下 `PART`：

- `assembly`：含球台截面、网布、网顶承载条、双侧立柱、桌下夹持、10 路光栅模块、PVDF 网顶安装座和参考线的装配预览；
- `left_stand` / `right_stand`：左右完整的内置式支架，包含立柱、传统桌下夹持、单侧光学模块和 PVDF 安装座；
- `post`：单侧立柱主体；`table_clamp`：单侧桌下夹持机构；
- `net`：网布装配占位，不是 PETG 打印件；`net_rail`：网顶承载条；
- `optical_strip`：单侧连续光学导轨和 10 个模块包络，`SIDE=-1` 可生成镜像侧；
- `sensor_mount`：单侧网顶 PVDF 夹片安装座；
- `calibration_gauge`：+10…+100 mm 高度档位标定规；
- `parameter_probe`：验证脚本读取的参数清单，不是打印件。

首轮几何参数是球台宽度 `1525 mm`、网顶高度 `152.5 mm`、光栅窗口 `+10…+100 mm`、10 mm 档位、两侧 `M8` 竖直夹紧螺杆。当前光学导轨已经包含每 `10 mm` 一个实际贯穿定位孔和可视刻度标记，便于参考线/标定销复核。球网、光学器件、PVDF 薄膜、线束、夹持软垫和金属标准件仍属于装配边界；OpenSCAD 结果不等同于最终强度、球台兼容性或光学精度验收。

导出示例：

```text
openscad -D 'PART="assembly"' -o net-stand-assembly.stl net_stand.scad
openscad -D 'PART="right_stand"' -o right-stand.stl net_stand.scad
openscad -D 'PART="left_stand"' -o left-stand.stl net_stand.scad
openscad -D 'PART="optical_strip"' -D 'SIDE=-1' -o optical-strip-left.stl net_stand.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_stand.scad
```

`preview.py` 在没有 OpenSCAD 的环境中生成当前内置支架的正视/侧面意图图，用于检查网顶、传统桌下夹持、双侧光学模块、参考线和 PVDF 安装座关系；它不是 STL 几何验证器。

本机安装 OpenSCAD 后运行：

```text
python3 validate_net_stand.py
python3 render_net_stand_preview.py
```

前者编译当前 `PART`、左右支架、光学镜像、参数探针和非法参数路径；后者从同一份参数源渲染当前装配、左右支架、桌下夹持、光学导轨镜像、PVDF 座和标定规，输出到 `rendered/net-stand-*.png`。CI 会把当前和历史两套渲染证据分别保存。

## 历史方案

`net_post_x_clamp.scad` 是前一轮外挂式 X 型立柱夹具。它被明确保留在 [`legacy/README.md`](legacy/README.md) 所述的历史边界内，用于设计回溯和旧几何回归；旧验证脚本 `validate_scad.py`、`validate_geometry.py`、`render_openscad_preview.py` 不应再被当作当前机械参数源。

当前与历史方案都暂不承诺比赛级裁判准确率。先打印内置支架的机械样件，确认球台厚度、夹持范围、网布张力、传感器安装和光学对准，再收敛尺寸与材料。
