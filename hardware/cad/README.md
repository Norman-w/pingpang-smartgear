# OpenSCAD CAD

当前机械主线是 `net_stand.scad`：直接做出一套替换传统球网的内置式球网支架，网布和网顶 PVDF 振动监测预装在支架上，左右端通过传统的桌下 C 形夹体固定到球台。M8×1.25 螺杆完全位于台面下方，向上顶台底可动压块；螺杆不穿过球台，不要求也不允许给球桌打孔。它不再依赖原球网立柱，也不再使用外挂式 X 夹具。

当前渲染对象和人工核验边界记录在 [`docs/visual-audit-v0.1.zh-CN.md`](../../docs/visual-audit-v0.1.zh-CN.md)；该记录把 CAD 可视结论与仍需实物验证的项目分开。

## 当前参数源：`net_stand.scad`

支持以下 `PART`：

- `assembly`：含球台截面、网布、网顶承载条、双侧立柱、桌下夹持、10 路光栅模块、PVDF 网顶安装座和参考线的装配预览；
- `left_stand` / `right_stand`：左右单侧结构检查件，包含立柱、传统桌下夹持、网顶承托座和单侧光学模块；PVDF 座位于全宽网顶承载条中段，在 `assembly` 或 `sensor_mount` 中检查；
- `table_clamp_section`：桌板剖面可视校验件，明确显示桌板上下表面、独立台底压块、圆头 M8×1.25 螺杆、固定下臂螺母和旋钮捕获螺母；它只是证据预览，不是打印件；
- `post`：单侧立柱主体装配预览；`post_segment`：两段约 153 mm 的可打印立柱，`post_segment_index=1` 是首样上段；`lower_stand_segment`：把 `post_segment_index=0` 下段与固定 C 形夹一体打印，避免首样装配时两个实体相互干涉；`post_joint_sleeve` / `post_joint_key`：接缝外套筒与内芯；`table_clamp`：单侧桌下夹持装配预览；`table_clamp_body`：固定 C 形夹体和下臂 M8 螺母捕获窝的几何检查件；`clamp_top_pad`：固定上夹板与桌面之间的可替换 TPU/硅胶保护垫；`clamp_pressure_pad`：台底可动压块/软垫占位；`clamp_screw`：带圆头的 M8×1.25 标准螺杆占位；`clamp_body_nut`：固定下臂中的标准 M8 螺母；`clamp_knob`：带 M8 通孔和顶部六角螺母捕获窝的手拧旋钮；`clamp_knob_nut`：旋钮内捕获的标准 M8 螺母；
- `net`：网布装配占位，不是 PETG 打印件；`net_rail`：三段带搭接和拼接片的网顶承载条装配预览；`net_rail_segment`：约 536 mm 的可打印单段；`net_rail_splice`：带 M3 孔的拼接片；`net_rail_saddle`：两侧立柱内侧的承托/端部限位座；
- `optical_rail`：单侧可打印连续光学导轨、10 个贯穿定位孔和刻度；`optical_strip`：导轨、10 个模块包络和 10 个中性载台的装配预览，不作为单件打印；`optical_module_carrier`：单个模块的可打印 U 形载台，带正交调节长孔，`optical_module_index=0…9` 选择 10 mm 档位；
- `sensor_mount`：单侧网顶 PVDF 夹片装配预览；`sensor_mount_body`：不含薄膜和压片包络的可打印 PETG 座体；`pvdf_film` / `sensor_clamp_lip`：可拆薄膜和两侧压片包络；`reference_carriage`：参考线端座与定位销装配预览；`reference_carriage_body`：不含定位销的可打印 PETG 端座；`reference_pin`：锁定到 10 mm 孔位的标准弹簧定位销；
- `calibration_gauge`：+10…+100 mm 高度档位标定规；
- `parameter_probe`：验证脚本读取的参数清单，不是打印件。

首轮几何参数是球台宽度 `1525 mm`、网顶高度 `152.5 mm`、光栅窗口 `+10…+100 mm`、10 mm 档位、两侧 `M8×1.25` 竖直夹紧螺杆。立柱外置 `37 mm`，让光学导轨位于台边与立柱内缘之间的开放空间，镜头光轴覆盖球台边缘；当前光学导轨已经包含每 `10 mm` 一个实际贯穿定位孔和可视刻度标记，参考线端座用 `reference_pin` 锁到这些孔位；每个光学模块由中性 U 形载台包住，后壁提供有限俯仰/偏航调节长孔，最终锁紧角度仍需真实收发器和光路实测；网顶承载条拆成 3 段、每段约 `536 mm`、搭接 `20 mm`，便于常见打印幅面或改用铝型材。夹紧受力路径明确为固定下臂 M8 螺母、圆头 M8×1.25 螺杆、顶部捕获 M8 螺母的打印旋钮和独立台底压块；不使用 PETG 内螺纹。球网、光学器件、PVDF 薄膜、线束、夹持软垫和金属标准件仍属于装配边界；OpenSCAD 结果不等同于最终强度、球台兼容性或光学精度验收。

导出示例：

```text
openscad -D 'PART="assembly"' -o net-stand-assembly.stl net_stand.scad
openscad -D 'PART="right_stand"' -o right-stand.stl net_stand.scad
openscad -D 'PART="left_stand"' -o left-stand.stl net_stand.scad
openscad -D 'PART="lower_stand_segment"' -D 'SIDE=1' -o right-lower-stand-segment.stl net_stand.scad
openscad -D 'PART="table_clamp_section"' -D 'SIDE=1' -o right-clamp-section.stl net_stand.scad
openscad -D 'PART="clamp_top_pad"' -D 'SIDE=1' -o right-clamp-top-pad.stl net_stand.scad
openscad -D 'PART="clamp_pressure_pad"' -D 'SIDE=1' -o right-pressure-pad.stl net_stand.scad
openscad -D 'PART="clamp_body_nut"' -D 'SIDE=1' -o right-clamp-body-nut.stl net_stand.scad
openscad -D 'PART="clamp_screw"' -D 'SIDE=1' -o right-clamp-screw.stl net_stand.scad
openscad -D 'PART="clamp_knob"' -D 'SIDE=1' -o right-clamp-knob.stl net_stand.scad
openscad -D 'PART="clamp_knob_nut"' -D 'SIDE=1' -o right-clamp-knob-nut.stl net_stand.scad
openscad -D 'PART="optical_rail"' -D 'SIDE=1' -o optical-rail-right.stl net_stand.scad
openscad -D 'PART="optical_strip"' -D 'SIDE=-1' -o optical-strip-left.stl net_stand.scad
openscad -D 'PART="optical_module_carrier"' -D 'optical_module_index=4' -o optical-carrier-50mm.stl net_stand.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_stand.scad
openscad -D 'PART="net_rail_segment"' -D 'rail_segment_index=1' -o net-rail-segment-1.stl net_stand.scad
openscad -D 'PART="net_rail_splice"' -D 'rail_splice_index=0' -o net-rail-splice-0.stl net_stand.scad
openscad -D 'PART="sensor_mount_body"' -D 'SIDE=1' -o right-pvdf-mount-body.stl net_stand.scad
openscad -D 'PART="reference_carriage_body"' -D 'SIDE=1' -o right-reference-carriage-body.stl net_stand.scad
```

首样批量导出使用同一参数源：

```text
python3 export_net_stand_printables.py
```

脚本把独立打印件写入被 Git 忽略的 `exports/net-stand-v0.1/`，同时生成 `manifest.json`（单位、来源 `PART`、左右侧、档位、包围盒和封闭拓扑摘要）。`test_export_net_stand_printables.py` 会固定 50 件导出矩阵，并在本地产物存在时核对 manifest 与每个 STL；`assembly`、左右支架、`table_clamp`、`sensor_mount`、`reference_carriage` 等仍是组合装配预览，不进入这个打印包；输出 STL 仍需在切片软件中按实际材料、喷嘴和方向复核。

`preview.py` 在没有 OpenSCAD 的环境中生成当前内置支架的正视/侧面意图图，用于检查网顶、传统桌下夹持、双侧光学模块、参考线和 PVDF 安装座关系；它不是 STL 几何验证器。

本机安装 OpenSCAD 后运行：

```text
python3 validate_net_stand.py
python3 render_net_stand_preview.py
```

前者编译当前 `PART`、左右支架、桌板剖面夹持证据、下段立柱+夹体一体件、可打印光学导轨、光学镜像/单个载台、圆头螺杆/两枚 M8 螺母/旋钮捕获、参数探针、18/25/30 mm 台厚免打孔夹持矩阵和非法参数路径；除 `assembly`、左右单侧结构、`post`、`table_clamp`、`net_rail`、`optical_strip` 等装配/渲染预览外，成功导出的独立打印零件还会做 STL 封闭边拓扑检查。装配预览允许桌板、网布和电子/标准件包络重叠，只用于 PNG，不是打印件。后者从同一份参数源渲染当前装配、左右支架、桌下夹持及其桌板剖面、圆头螺杆、两个螺母、带捕获窝旋钮、可打印光学导轨、光学装配预览、单个载台、PVDF 座和标定规，输出到 `rendered/net-stand-*.png`。CI 会把当前和历史两套渲染证据分别保存。

## 历史方案

`net_post_x_clamp.scad` 是前一轮外挂式 X 型立柱夹具。它被明确保留在 [`legacy/README.md`](legacy/README.md) 所述的历史边界内，用于设计回溯和旧几何回归；旧验证脚本 `validate_scad.py`、`validate_geometry.py`、`render_openscad_preview.py` 不应再被当作当前机械参数源。

当前与历史方案都暂不承诺比赛级裁判准确率。先打印内置支架的机械样件，确认球台厚度、夹持范围、网布张力、传感器安装和光学对准，再收敛尺寸与材料。
