# OpenSCAD CAD

当前机械主线是 `net_stand.scad`：直接做出一套替换传统球网的内置式球网支架，网布和网顶 PVDF 振动监测预装在支架上，左右端通过传统的桌下 C 形夹体固定到球台。M8×1.25 螺杆完全位于台面下方，向上顶台底可动压块；螺杆不穿过球台，不要求也不允许给球桌打孔。它不再依赖原球网立柱，也不再使用外挂式 X 夹具。

当前渲染对象和人工核验边界记录在 [`docs/visual-audit-v0.1.zh-CN.md`](../../docs/visual-audit-v0.1.zh-CN.md)；该记录把 CAD 可视结论与仍需实物验证的项目分开。

## 当前参数源：`net_stand.scad`

支持以下 `PART`：

- `assembly`：含球台截面、网布、网顶承载条、双侧立柱、桌下夹持、两段 STG-120ML 光纤头、外侧托架、中央背靠背支撑桥、PVDF 网顶安装座和检测窗口的装配预览；
- `left_stand` / `right_stand`：左右单侧结构检查件，包含立柱、传统桌下夹持、网顶承托座和 STG-120ML 外侧托架；PVDF 座位于全宽网顶承载条中段，在 `assembly` 或 `sensor_mount` 中检查；
- `table_clamp_section`：桌板剖面可视校验件，明确显示桌板上下表面、独立台底压块、圆头 M8×1.25 螺杆、固定下臂螺母和旋钮内两枚对锁螺母；它只是证据预览，不是打印件；
- `post`：单侧立柱主体装配预览；`post_segment`：两段约 153 mm 的可打印立柱，`post_segment_index=1` 是首样上段；`lower_stand_segment`：把 `post_segment_index=0` 下段与固定 C 形夹一体打印，避免首样装配时两个实体相互干涉；`post_joint_sleeve` / `post_joint_key`：接缝外套筒与内芯；`table_clamp`：单侧桌下夹持装配预览；`table_clamp_body`：固定 C 形夹体和下臂 M8 螺母捕获窝的几何检查件；`clamp_top_pad`：固定上夹板与桌面之间的可替换 TPU/硅胶保护垫；`clamp_pressure_pad`：台底可动压块/软垫占位；`clamp_screw`：带圆头的 M8×1.25 标准螺杆占位；`clamp_body_nut`：固定下臂中的标准 M8 螺母；`clamp_knob`：带 M8 通孔和两枚对锁螺母捕获窝的手拧旋钮；`clamp_knob_nut`：旋钮内捕获的两枚标准 M8 对锁螺母；
- `net`：网布装配占位，不是 PETG 打印件；`net_rail`：三段带搭接和拼接片的网顶承载条装配预览；`net_rail_segment`：约 536 mm 的可打印单段；`net_rail_splice`：带 M3 孔的拼接片；`net_rail_saddle`：两侧立柱内侧的承托/端部限位座；
- `stg120_outer_carrier`：单侧 STG-120ML 130×19×6 mm 光纤头包络托架；`stg120_center_bridge`：中央背靠背支撑桥，同时承载左右两段的中央光纤头；`stg120_preview`：两段光路和 32 个 3.87 mm 光点位置的装配预览，不作为单件打印；旧版 `optical_rail` / `optical_module_carrier` 仅保留在 SCAD 中作历史兼容诊断，不进入当前打印清单；
- `sensor_mount`：单侧网顶 PVDF 夹片装配预览；`sensor_mount_body`：不含薄膜和压片包络的可打印 PETG 座体；`pvdf_film` / `sensor_clamp_lip`：可拆薄膜和两侧压片包络；旧版 `reference_carriage` / `reference_pin` 只保留作历史标定几何诊断，不进入当前 STG-120ML 打印包；
- `calibration_gauge`：按 STG-120ML 的 3.87 mm 光点间距制作的高度标定规；
- `parameter_probe`：验证脚本读取的参数清单，不是打印件。

首轮几何参数是球台宽度 `1525 mm`、网顶高度 `152.5 mm`、STG-120ML 有效检测窗口约 `0…120 mm`、光点间距 `3.87 mm`、两侧 `M8×1.25` 竖直夹紧螺杆。单对光纤头的标称最大检测距离为 `1000 mm`，所以全宽采用左右两段、中央背靠背支撑桥；两侧托架只按商品头部外形包络夹持，线缆出口预留弯曲和应变释放空间，不未经量测写死商品孔位。网顶承载条拆成 3 段、每段约 `536 mm`、搭接 `20 mm`，便于常见打印幅面或改用铝型材。夹紧受力路径明确为固定下臂 M8 螺母、两枚预先对锁并由旋钮捕获的 M8 螺母、圆头 M8×1.25 螺杆和独立台底压块；不使用 PETG 内螺纹，也不让旋钮与固定下臂形成未定义的双螺纹约束。球网、光纤头、配套放大器、PVDF 薄膜、线束、夹持软垫和金属标准件仍属于装配边界；OpenSCAD 结果不等同于最终强度、球台兼容性、放大器输出语义或光学精度验收。

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
openscad -D 'PART="stg120_outer_carrier"' -D 'SIDE=1' -o right-stg120-outer-carrier.stl net_stand.scad
openscad -D 'PART="stg120_center_bridge"' -o stg120-center-bridge.stl net_stand.scad
openscad -D 'PART="stg120_preview"' -o stg120-preview.stl net_stand.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_stand.scad
openscad -D 'PART="net_rail_segment"' -D 'rail_segment_index=1' -o net-rail-segment-1.stl net_stand.scad
openscad -D 'PART="net_rail_splice"' -D 'rail_splice_index=0' -o net-rail-splice-0.stl net_stand.scad
openscad -D 'PART="sensor_mount_body"' -D 'SIDE=1' -o right-pvdf-mount-body.stl net_stand.scad
```

首样批量导出使用同一参数源：

```text
python3 export_net_stand_printables.py --clean
python3 test_export_net_stand_printables.py
```

脚本把独立打印件写入被 Git 忽略的 `exports/net-stand-v0.1/`，同时生成 `manifest.json`（单位、来源 `PART`、左右侧、包围盒和封闭拓扑摘要）。输出目录若有旧版 STL，必须显式加 `--clean` 才会清理，避免历史外挂夹或旧光学载台混入当前首样；`test_export_net_stand_printables.py` 会固定当前 29 件导出矩阵，并拒绝清单之外的 STL。`assembly`、左右支架、`table_clamp`、`sensor_mount`、`stg120_preview` 等仍是组合装配预览，不进入这个打印包；输出 STL 仍需在切片软件中按实际材料、喷嘴和方向复核。

`preview.py` 在没有 OpenSCAD 的环境中生成当前内置支架的正视/侧面意图图，用于检查网顶、传统桌下夹持、双侧光学模块、参考线和 PVDF 安装座关系；它不是 STL 几何验证器。

## 打印拼盘与预览页

拼盘脚本只对已经导出的独立 STL 做 0/90° 旋转和平移，不缩放、不裁切、不把零件布尔合并。默认按 `256 × 256 × 256 mm` 打印床、边缘余量 `5 mm`、零件间距 `5 mm` 生成合并拼盘 STL；不同 `material_group` 严格分盘，当前源清单是 29 件，3 段约 `537 × 18 × 10 mm` 的网顶承载条明确列为超尺寸件，板数和已排版数量以最新 manifest 为准。

```text
python3 hardware/cad/export_net_stand_printables.py --clean
python3 hardware/cad/build_print_platter.py --clean
python3 hardware/cad/test_build_print_platter.py --default
```

生成物位于被 Git 忽略的 `hardware/cad/exports/net-stand-v0.1/`。其中 `print-platter-256/manifest.json` 记录打印床、板次、材料组、源 STL、实际包围盒和超尺寸原因；`plate-*.stl` 是可以导入切片器的拼盘文件。使用更大打印床时可以选择内置预设，或传入 `--bed-width`、`--bed-depth`、`--bed-height`。材料不同不能共用一张板，即使某个零件标注为 `PETG/TPU 试样`，首样也按 TPU/柔性盘隔离。

独立预览页是 `hardware/cad/preview/index.html`，它参考 SmartPaddle 的拼盘操作方式，并扩展为四个查看模式：

- `装配预览`：加载 29 个打印 STL 的真实装配坐标，同时显示球台、网布、两段 STG-120ML 光纤头/检测窗口、配套放大器边界、PVDF、M8 螺杆/螺母等非打印占位；
- `爆炸预览`：通过爆炸程度滑杆和装配步骤查看各组零件的分离方向、中文名称、材料与装配说明；
- `打印拼盘`：提供打印床切换、间距/余量调节、自动重新排版、板次切换、俯视图点击选件、Three.js STL 预览、源 STL/拼盘 STL 下载和布局 JSON 下载；
- `零件清单`：集中查看所有打印件的中文名、材料组、尺寸和 STL 下载入口。

装配模式中的球台、网布、光学器件、PVDF 和金属标准件明确是“装配占位”，不进入 PETG / TPU 打印拼盘；打印拼盘仍严格按材料分盘。页面内的拼盘调参只是浏览器预览，只有再次运行 Python 拼盘脚本才会生成对应的合并 STL。

```text
python3 -m http.server 8000
打开 http://127.0.0.1:8000/hardware/cad/preview/index.html
```

页面默认读取 `exports/net-stand-v0.1/print-platter-256/manifest.json`；如果页面显示清单读取失败，先执行上面的导出和拼盘命令。Three.js 从 CDN 加载，网络不可用时俯视图、自动排版和 JSON 下载仍可用，但 3D STL 检查器会降级为提示。

本机安装 OpenSCAD 后运行：

```text
python3 validate_net_stand.py
python3 test_preview_consistency.py
python3 render_net_stand_preview.py
```

`test_preview_consistency.py` 不需要 OpenSCAD，用于防止无 OpenSCAD 的轻量意图图继续沿用旧外挂夹具的关键参数；`validate_net_stand.py` 编译当前 `PART`、左右支架、桌板剖面夹持证据、下段立柱+夹体一体件、STG-120ML 外侧托架/中央桥、圆头螺杆/固定下臂 M8 螺母/旋钮内两枚对锁螺母、参数探针、18/25/30 mm 台厚免打孔夹持矩阵和非法参数路径；除 `assembly`、左右单侧结构、`post`、`table_clamp`、`net_rail`、`stg120_preview` 等装配/渲染预览外，成功导出的独立打印零件还会做 STL 封闭边拓扑检查。装配预览允许桌板、网布和电子/标准件包络重叠，只用于 PNG，不是打印件。后者从同一份参数源渲染当前装配、左右支架、桌下夹持及其桌板剖面、圆头螺杆、固定螺母和对锁螺母叠层、带捕获窝旋钮、STG-120ML 光纤头/中央桥装配预览、PVDF 座和标定规，输出到 `rendered/net-stand-*.png`。CI 会把当前和历史两套渲染证据分别保存。

## 历史方案

`net_post_x_clamp.scad` 是前一轮外挂式 X 型立柱夹具。它被明确保留在 [`legacy/README.md`](legacy/README.md) 所述的历史边界内，用于设计回溯和旧几何回归；旧验证脚本 `validate_scad.py`、`validate_geometry.py`、`render_openscad_preview.py` 不应再被当作当前机械参数源。

当前与历史方案都暂不承诺比赛级裁判准确率。先打印内置支架的机械样件，确认球台厚度、夹持范围、网布张力、传感器安装和光学对准，再收敛尺寸与材料。
