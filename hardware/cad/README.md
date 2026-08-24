# OpenSCAD CAD

当前机械主线是 `net_stand.scad`：直接做出一套替换传统球网的内置式球网支架，网布和网顶 PVDF 振动监测预装在支架上，左右端通过传统的桌下 C 形夹体固定到球台。M8 螺杆完全位于台面下方，向上顶台底可动压块；螺杆不穿过球台，不要求也不允许给球桌打孔。它不再依赖原球网立柱，也不再使用外挂式 X 夹具。

## 当前参数源：`net_stand.scad`

支持以下 `PART`：

- `assembly`：含球台截面、网布、网顶承载条、双侧立柱、桌下夹持、10 路光栅模块、PVDF 网顶安装座和参考线的装配预览；
- `left_stand` / `right_stand`：左右单侧结构检查件，包含立柱、传统桌下夹持、网顶承托座和单侧光学模块；PVDF 座位于全宽网顶承载条中段，在 `assembly` 或 `sensor_mount` 中检查；
- `post`：单侧立柱主体装配预览；`post_segment`：两段约 153 mm 的可打印立柱，`post_segment_index=0` 的下段包含台面上方承载加厚；`post_joint_sleeve` / `post_joint_key`：接缝外套筒与内芯；`table_clamp`：单侧桌下夹持装配预览；`table_clamp_body`：固定 C 形夹体；`clamp_pressure_pad`：台底可动压块/软垫占位；`clamp_knob`：手拧旋钮；
- `net`：网布装配占位，不是 PETG 打印件；`net_rail`：三段带搭接和拼接片的网顶承载条装配预览；`net_rail_segment`：约 524 mm 的可打印单段；`net_rail_splice`：带 M3 孔的拼接片；`net_rail_saddle`：两侧立柱内侧的承托/端部限位座；
- `optical_rail`：单侧可打印连续光学导轨、10 个贯穿定位孔和刻度；`optical_strip`：导轨、10 个模块包络和 10 个中性载台的装配预览，不作为单件打印；`optical_module_carrier`：单个模块的可打印 U 形载台，带正交调节长孔，`optical_module_index=0…9` 选择 10 mm 档位；
- `sensor_mount`：单侧网顶 PVDF 夹片安装座；`pvdf_film` / `sensor_clamp_lip`：可拆薄膜和两侧压片包络；`reference_carriage` / `reference_pin`：锁定到 10 mm 孔位的参考线端座与定位销；
- `calibration_gauge`：+10…+100 mm 高度档位标定规；
- `parameter_probe`：验证脚本读取的参数清单，不是打印件。

首轮几何参数是球台宽度 `1525 mm`、网顶高度 `152.5 mm`、光栅窗口 `+10…+100 mm`、10 mm 档位、两侧 `M8` 竖直夹紧螺杆。当前光学导轨已经包含每 `10 mm` 一个实际贯穿定位孔和可视刻度标记，参考线端座用 `reference_pin` 锁到这些孔位；每个光学模块由中性 U 形载台包住，后壁提供有限俯仰/偏航调节长孔，最终锁紧角度仍需真实收发器和光路实测；网顶承载条拆成 3 段、每段约 `524 mm`、搭接 `20 mm`，便于常见打印幅面或改用铝型材。球网、光学器件、PVDF 薄膜、线束、夹持软垫和金属标准件仍属于装配边界；OpenSCAD 结果不等同于最终强度、球台兼容性或光学精度验收。

导出示例：

```text
openscad -D 'PART="assembly"' -o net-stand-assembly.stl net_stand.scad
openscad -D 'PART="right_stand"' -o right-stand.stl net_stand.scad
openscad -D 'PART="left_stand"' -o left-stand.stl net_stand.scad
openscad -D 'PART="table_clamp_body"' -D 'SIDE=1' -o right-clamp-body.stl net_stand.scad
openscad -D 'PART="clamp_pressure_pad"' -D 'SIDE=1' -o right-pressure-pad.stl net_stand.scad
openscad -D 'PART="clamp_knob"' -D 'SIDE=1' -o right-clamp-knob.stl net_stand.scad
openscad -D 'PART="optical_rail"' -D 'SIDE=1' -o optical-rail-right.stl net_stand.scad
openscad -D 'PART="optical_strip"' -D 'SIDE=-1' -o optical-strip-left.stl net_stand.scad
openscad -D 'PART="optical_module_carrier"' -D 'optical_module_index=4' -o optical-carrier-50mm.stl net_stand.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_stand.scad
openscad -D 'PART="net_rail_segment"' -D 'rail_segment_index=1' -o net-rail-segment-1.stl net_stand.scad
openscad -D 'PART="net_rail_splice"' -D 'rail_splice_index=0' -o net-rail-splice-0.stl net_stand.scad
```

`preview.py` 在没有 OpenSCAD 的环境中生成当前内置支架的正视/侧面意图图，用于检查网顶、传统桌下夹持、双侧光学模块、参考线和 PVDF 安装座关系；它不是 STL 几何验证器。

本机安装 OpenSCAD 后运行：

```text
python3 validate_net_stand.py
python3 render_net_stand_preview.py
```

前者编译当前 `PART`、左右支架、可打印光学导轨、光学镜像/单个载台、参数探针和非法参数路径；后者从同一份参数源渲染当前装配、左右支架、桌下夹持、可打印光学导轨、光学装配预览、单个载台、PVDF 座和标定规，输出到 `rendered/net-stand-*.png`。CI 会把当前和历史两套渲染证据分别保存。

## 历史方案

`net_post_x_clamp.scad` 是前一轮外挂式 X 型立柱夹具。它被明确保留在 [`legacy/README.md`](legacy/README.md) 所述的历史边界内，用于设计回溯和旧几何回归；旧验证脚本 `validate_scad.py`、`validate_geometry.py`、`render_openscad_preview.py` 不应再被当作当前机械参数源。

当前与历史方案都暂不承诺比赛级裁判准确率。先打印内置支架的机械样件，确认球台厚度、夹持范围、网布张力、传感器安装和光学对准，再收敛尺寸与材料。
