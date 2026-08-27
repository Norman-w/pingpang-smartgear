# OpenSCAD CAD

当前机械主线是 `net_stand.scad`：直接做出一套替换传统球网的内置式球网支架，网布和网顶 PVDF 振动监测预装在支架上，左右端通过传统的桌下 C 形夹体固定到球台。M8×1.25 螺杆完全位于台面下方，向上顶台底可动压块；螺杆不穿过球台，不要求也不允许给球桌打孔。光学主线是左右各一套十路 M6 直角对射 NPN 器件：每侧使用一根竖直 `10×56×216 mm` 可打印 PETG 长条主体，光学/M6 外丝轴沿 x 朝球台中心，右侧从 x+、左侧从 x- 外侧装入；蓝色护套/尾线局部沿 z-，整件绕光束 x 轴旋转 -45°，在外侧沿 x 穿入并向 y-/z- 让线；十个中心按 `20 mm` 节距排列，避开原来过密的器件干涉。主体用 x 向浅六角沉孔定位，M6 外丝直穿，朝台内的平滑面带一枚原配螺帽，固定螺丝不嵌入主体，线缆也不在主体里挖槽。当前完整装配候选还包含 x- 光学端正球弧前盖、x+ 线缆端圆角矩形后盖（x 背面中央、y=0、z 中心加厚 M8 boss）和底盖；采购 13 mm 球头保持竖直，横向 M8 外牙从各自 x 后端进入后盖 boss，球头 z- 竖直接口由采购金属 90°连接器从最低端承接，再沿 x 接到网夹立柱的两枚 M6 槽孔；壳体只保护、导向和提供接口，后续可改 CNC 或加金属嵌件。左右总成只保留实际需要的偏航、俯仰、旋转微调链，不再使用旧的梳齿条和水平三层云台方案。

本轮首样暂时冻结在 `m6_detector_fit_probe`：只检查长条主体与真实三维 L 型激光头本体的几何卡入。器件按真实关系表示为灰色 `AF8` 六角主体、空心 `M6×0.75` 外丝光学筒、蓝色直角护套和黑色尾线；整件绕光束 x 轴 `-45°` 让线，从外侧插入主体约 `2 mm`。中空 M6 外丝贯穿主体，光学中心孔朝球台中心；本验证件不含原配螺帽、壳体、支撑或云台，孔径仍以到货 SKU 实测为准。

微调结构和 M6 器件待确认项见 [`../../docs/m6-optical-array-design-v0.1.zh-CN.md`](../../docs/m6-optical-array-design-v0.1.zh-CN.md)。

当前渲染对象和人工核验边界记录在 [`docs/visual-audit-v0.1.zh-CN.md`](../../docs/visual-audit-v0.1.zh-CN.md)；该记录把 CAD 可视结论与仍需实物验证的项目分开。

## 当前参数源：`net_stand.scad`

支持以下 `PART`：

- `assembly`：含球台截面、网布、网顶承载条、双侧立柱、桌下夹持、左右各十路 45° L 型 M6 直角器件、PETG 长条主体、完整 x 向分体前后盖、底盖、后盖 M8 boss、竖直采购球头、球头下采购金属 90°连接器、PVDF 网顶安装座和十条名义光轴的装配预览；壳体默认显示；
- `left_stand` / `right_stand`：左右单侧结构检查件，包含立柱、传统桌下夹持、网顶承托座和 M6 PETG 光学基座；PVDF 座位于全宽网顶承载条中段，在 `assembly` 或 `sensor_mount` 中检查；
- `table_clamp_section`：桌板剖面可视校验件，明确显示桌板上下表面、独立台底压块、圆头 M8×1.25 螺杆、固定下臂螺母和旋钮内两枚对锁螺母；它只是证据预览，不是打印件；
- `post`：单侧立柱主体装配预览；`post_segment`：两段约 153 mm 的可打印立柱，`post_segment_index=1` 是首样上段；`lower_stand_segment`：把 `post_segment_index=0` 下段与固定 C 形夹一体打印，避免首样装配时两个实体相互干涉；`post_joint_sleeve` / `post_joint_key`：接缝外套筒与内芯；`table_clamp`：单侧桌下夹持装配预览；`table_clamp_body`：固定 C 形夹体和下臂 M8 螺母捕获窝的几何检查件；`clamp_top_pad`：固定上夹板与桌面之间的可替换 TPU/硅胶保护垫；`clamp_pressure_pad`：台底可动压块/软垫占位；`clamp_screw`：带圆头的 M8×1.25 标准螺杆占位；`clamp_body_nut`：固定下臂中的标准 M8 螺母；`clamp_knob`：带 M8 通孔和两枚对锁螺母捕获窝的手拧旋钮；`clamp_knob_nut`：旋钮内捕获的两枚标准 M8 对锁螺母；
- `net`：网布装配占位，不是 PETG 打印件；`net_rail`：名义总跨度 `1830 mm`、三段带搭接和拼接片的网顶承载条装配预览；`net_rail_segment`：约 `623.33 mm` 的可打印单段；`net_rail_splice`：带 M3 孔的拼接片；`net_rail_saddle`：两侧立柱内侧的承托/端部限位座；
- `m6_detector_body`：PETG 长条主体，中央基准 `10×56×216 mm`，后续可按同一包络改 CNC；10 个 `20 mm` 节距的 x 向水平光学/M6 外丝让位和绕 x 轴 -45° 的尾线让位孔，右侧从 x+、左侧从 x- 外侧装入，后方为浅 `AF8×2.1 mm` x 向六角定位沉孔，M6 外丝直穿，朝台内平滑面只保留一枚原配螺帽；主体不带 T 尾座、不挖主体线缆槽，后盖 x 背面中央另设 y=0、z 中心加厚 boss 和 Ø8.6 mm M8 通孔；
- `m6_detector_fit_probe` / `m6_detector_fit_body`：当前首样的最小验证件，包含中央 PETG 长条、按真实 `AF8` 六角头外形切出的浅 x 向卡槽和中空 M6 外丝通孔；配套显示真实三维灰色六角、空心光学筒、蓝色 L 型护套和 `-45°` 斜下尾线。右侧从 x+ 插入，左侧由镜像得到，轴向卡入量为 `2 mm`，不包含螺帽、壳体、支撑或云台；
- `m6_detector_shell_front` / `m6_detector_shell_rear` / `m6_detector_bottom_cover`：PETG x- 光学端正圆弧前盖、x+ 线缆端圆角矩形后盖（x 背面中央 y=0、z 中心加厚 M8 boss）和按组合轮廓制作的底盖；从 z+ 俯视时外形对应“上部正弧 + 下部圆角矩形”，中间只表示前后盖分型边界、不建连线；安装/拆卸顺序为前盖从 z+、后盖从 z+、底盖从 z-，两盖共享主体 y± 连续边槽并分别占 x- / x+ 半段，沉头孔和底盖 Ø12 mm 线缆套管孔仍需真实器件首样复核；
- `m6_detector_net_connector`：采购金属球头下接网夹 90°连接器的预览包络；球头 z- 接口从最低端进入中空套筒，水平臂沿 x 到网夹立柱内侧，竖直端两孔与立柱上段 x 向槽孔同轴；这是非打印承力件，不进入 PETG 打印清单；
- `m6_detector_mount`：当前默认显示主体、完整 x 分体壳体、底盖、后盖 M8 boss、竖直采购球头和球头下金属连接器的左右装配关系，球头及连接器不直接打印；`m6_ballhead` 是采购的 13 mm 球头外购件包络；
- `m6_sensor_array`：左右各十枚 M6 直角发射/接收器件的外购包络预览；`m6_gimbal`、`m6_sensor_rail` 及旧 `m6_machining_*` 名称仅保留为兼容/历史诊断入口，不代表当前加工方案；
- `stg120_outer_carrier` / `stg120_center_bridge` / `stg120_preview`：旧 STG-120ML 方案的历史兼容诊断件；旧版 `optical_rail` / `optical_module_carrier` 也只保留作回溯，不进入当前打印清单；
- `sensor_mount`：单侧网顶 PVDF 夹片装配预览；`sensor_mount_body`：不含薄膜和压片包络的可打印 PETG 座体；`pvdf_film` / `sensor_clamp_lip`：可拆薄膜和两侧压片包络；旧版 `reference_carriage` / `reference_pin` 只保留作历史标定几何诊断，不进入当前 STG-120ML 打印包；
- `calibration_gauge`：按 STG-120ML 的 3.87 mm 光点间距制作的高度标定规；
- `parameter_probe`：验证脚本读取的参数清单，不是打印件。

M6 首样输入和可复现孔位表见 [`docs/m6-aluminum-machining-spec-v0.1.zh-CN.md`](../../docs/m6-aluminum-machining-spec-v0.1.zh-CN.md)，首样零件/紧固件清单和装配放行顺序见 [`../../docs/m6-first-article-release-v0.1.zh-CN.md`](../../docs/m6-first-article-release-v0.1.zh-CN.md)。运行 `python3 export_m6_machining_spec.py` 可从当前 SCAD 参数探针生成主体、后盖 boss、三件 PETG 盖件、传感器和采购球头选项的 JSON；运行 `python3 export_m6_machining_previews.py --clean` 只生成主体局部坐标 STL 及 `manifest.json`；运行 `python3 export_m6_component_previews.py --clean` 可按左右两侧独立生成主体、前盖、后盖和底盖共 8 个完整 STL 及组件清单。加工/打印前仍需用真实 M6 SKU、传感器六角/有效螺纹、采购球头螺纹选项和网夹安装面实测结果更新/复核。

首轮几何参数是球台宽度 `1525 mm`、网柱外边界距台边 `152.5 mm`、名义网架总宽 `1830 mm`、网顶高度 `152.5 mm`、10 个高度通道 `+10…+190 mm`、M6×0.75 直角对射器件和两侧 `M8×1.25` 竖直夹紧螺杆。M6 中央主体按 `10×56×216 mm` 建模：水平光学/M6 外丝轴沿 x，蓝色尾线局部沿 z- 后绕 x 轴 -45°，主体中心在 y=0，右侧从 x+、左侧从 x- 外侧装入，单列中心距 `20 mm`；10 mm x 厚度通过 2 mm 头部卡入、5 mm 螺帽和约 1 mm 端部余量闭合，首件需复核公差和螺帽真实厚度。后盖 x 背面中央另设约 `14×18×36 mm` 加厚 boss，并开 Ø8.6 mm x 向通孔接采购 13 mm 球头的 M8 外牙；壳体当前已按 x 光学端/线缆端分段：x- 前盖保留正球弧，x+ 后盖为圆角矩形，底盖有统一线缆套管过孔；两盖共享 y± 连续边槽，槽舌、沉头孔和真实器件净空仍需首样复核，不视为最终打印放行。采购球头保持竖直，球头 z- 接口由金属 90°连接器从接口最低端向上承接到网夹立柱 `z=252.5 mm` 连接高度（当前基准高差 `49 mm`），负责把偏航、俯仰、旋转微调传入网夹；连接器为外购金属件，不进入 PETG 打印包。依据 ITTF Technical Leaflet T2，当前自定义夹体最外点收敛为台边外 `160 mm`，仍满足项目下限 `130 mm`；它不是 ITTF 认证网夹，若复用商品夹，必须另测开口和台下投影。台边外伸段的前后两侧各有 `8 mm` 厚三角侧肋，实际 PETG 层向、夹紧力、网布张力、球路净空和球头刚度仍需首样验证。球网、M6 光电器件、采购球头、金属连接器、PVDF 薄膜、线束、夹持软垫和金属标准件仍属于装配边界；OpenSCAD 结果不等同于最终强度、球台兼容性、电气输出语义或光学精度验收。

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
openscad -D 'PART="m6_detector_mount"' -D 'SIDE=1' -o right-m6-detector-mount-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_mount"' -D 'SIDE=-1' -o left-m6-detector-mount-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_body"' -D 'SIDE=1' -o right-m6-detector-body-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_fit_probe"' -D 'SIDE=1' -o right-m6-detector-fit-probe-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_fit_probe"' -D 'SIDE=-1' -o left-m6-detector-fit-probe-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_shell_front"' -D 'SIDE=1' -o right-m6-detector-front-cover-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_shell_rear"' -D 'SIDE=1' -o right-m6-detector-rear-cover-preview.stl net_stand.scad
openscad -D 'PART="m6_detector_bottom_cover"' -D 'SIDE=1' -o right-m6-detector-bottom-cover-preview.stl net_stand.scad
# 独立输出并验证 M6 主体的局部首样/CNC 复用预览
python3 export_m6_machining_previews.py --clean
python3 test_m6_machining_previews.py
# STG-120ML 的旧 PART 仍可单独渲染回溯，但不属于当前首样。
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

脚本把正式独立打印件写入被 Git 忽略的 `exports/net-stand-v0.1/`，同时生成 `manifest.json`（单位、来源 `PART`、左右侧、包围盒和封闭拓扑摘要）。输出目录若有旧版 STL，必须显式加 `--clean` 才会清理，避免历史外挂夹或旧光学载台混入当前首样；`test_export_net_stand_printables.py` 会固定当前 26 件 PETG/TPU 导出矩阵，并拒绝清单之外的 STL。M6 主体、前后盖和底盖是当前 PETG 首样候选，采购球头、金属 90°连接器与商品网夹不进入打印包；`assembly`、左右支架、`table_clamp`、`sensor_mount`、`m6_detector_mount` 等仍是组合装配预览，不进入这个通用打印包；输出 STL 仍需在切片软件中按实际材料、喷嘴和方向复核。

机加工独立预览包单独输出，不与打印清单混用：

```text
python3 export_m6_machining_previews.py --clean
python3 test_m6_machining_previews.py
```

生成物位于 `exports/net-stand-v0.1/m6-machining-previews/`：当前只导出主体左右两件局部坐标封闭 STL（左右完整装配另由 `m6_detector_mount` 预览），`manifest.json` 记录源文件哈希、局部坐标原点、包围盒和拓扑摘要。它们既可用于 PETG 首样，也可作为未来 CNC 包络/孔位核对输入，不是最终放行图。

当前 M6 总成的完整组件预览单独输出，不与正式 26 件 PETG/TPU 打印清单混用：

```text
python3 export_m6_component_previews.py --clean
python3 test_m6_component_previews.py
```

生成物位于 `exports/net-stand-v0.1/m6-component-previews/`：左右各一套主体、x- 前盖、x+ 后盖和底盖，共 8 个完整 STL。`manifest.json` 记录 `PART`/`SIDE`、全局 OpenSCAD 坐标、材料、是否为 PETG 候选、包围盒、体积和封闭边拓扑；后盖 boss 的 M8 接口以 Ø8.6 通孔表示，采购球头、商品网夹和实际螺纹不进入 STL。四件都是可切片候选，但仍需真实传感器、尾线和球头接口首样确认。

`preview.py` 在没有 OpenSCAD 的环境中生成当前内置支架的正视/侧面意图图，用于检查网顶、传统桌下夹持、双侧 M6 直角阵列、参考线和 PVDF 安装座关系；它不是 STL 几何验证器。

## 打印拼盘与预览页

拼盘脚本只对已经导出的独立 STL 做 0/90° 旋转和平移，不缩放、不裁切、不把零件布尔合并。默认按 `256 × 256 × 256 mm` 打印床、边缘余量 `5 mm`、零件间距 `5 mm` 生成合并拼盘 STL；不同 `material_group` 严格分盘，当前源清单是 26 件，3 段约 `623.33 × 18 × 10 mm` 的网顶承载条明确列为超尺寸件，铝合金光学基座不进入拼盘，板数和已排版数量以最新 manifest 为准。

```text
python3 hardware/cad/export_net_stand_printables.py --clean
python3 hardware/cad/build_print_platter.py --clean
python3 hardware/cad/test_build_print_platter.py --default
```

生成物位于被 Git 忽略的 `hardware/cad/exports/net-stand-v0.1/`。其中 `print-platter-256/manifest.json` 记录打印床、板次、材料组、源 STL、实际包围盒和超尺寸原因；`plate-*.stl` 是可以导入切片器的拼盘文件。使用更大打印床时可以选择内置预设，或传入 `--bed-width`、`--bed-depth`、`--bed-height`。材料不同不能共用一张板，即使某个零件标注为 `PETG/TPU 试样`，首样也按 TPU/柔性盘隔离。

独立预览页是 `hardware/cad/preview/index.html`，它参考 SmartPaddle 的拼盘操作方式，并扩展为四个查看模式：

- `装配预览`：加载 26 个打印 STL 的真实装配坐标，同时显示球台、网布、左右各十路 45° L 型 M6 直角光电器件、PETG 长条主体、x 向分体前后壳、后盖 boss、底盖、竖直采购球头、球头下采购金属 90°连接器、PVDF、M8 螺杆/螺母等非打印占位；壳体以半透明完整候选件显示；
- `爆炸预览`：通过爆炸程度滑杆和装配步骤查看各组零件的分离方向、中文名称、材料与装配说明；
- `打印拼盘`：提供打印床切换、间距/余量调节、自动重新排版、板次切换、俯视图点击选件、Three.js STL 预览、源 STL/拼盘 STL 下载和布局 JSON 下载；
- `零件清单`：集中查看所有打印件的中文名、材料组、尺寸和 STL 下载入口。

装配模式中的球台、网布、光学器件、PVDF 和金属标准件明确是“装配占位”，不进入 PETG / TPU 打印拼盘；打印拼盘仍严格按材料分盘。页面内的拼盘调参只是浏览器预览，只有再次运行 Python 拼盘脚本才会生成对应的合并 STL。

```text
python3 -m http.server 8000
打开 http://127.0.0.1:8000/hardware/cad/preview/index.html
```

页面默认读取 `exports/net-stand-v0.1/print-platter-256/manifest.json`；如果页面显示清单读取失败，先执行上面的导出和拼盘命令。Three.js 从 CDN 加载，网络不可用时俯视图、自动排版和 JSON 下载仍可用，但 3D STL 检查器会降级为提示。

本机已验证 OpenSCAD `2026.04.26 (git b38f6888)`；安装后运行：

```text
python3 validate_net_stand.py
python3 test_preview_consistency.py
python3 render_net_stand_preview.py
# M6 总成六视图（x-/x+/y-/y+/z-/z+）和无剖切等轴审计图
python3 render_m6_views.py --part m6_detector_mount
python3 render_m6_views.py --part m6_detector_exploded
```

`test_preview_consistency.py` 不需要 OpenSCAD，用于防止无 OpenSCAD 的轻量意图图继续沿用旧外挂夹具的关键参数；`validate_net_stand.py` 编译当前 `PART`、左右支架、桌板剖面夹持证据、下段立柱+夹体一体件、M6 45° L 型主体/斜向 7 字孔/后盖 boss/采购球头/球头下金属 90°连接器完整装配、圆头螺杆/固定下臂 M8 螺母/旋钮内两枚对锁螺母、参数探针、18/25/30 mm 台厚免打孔夹持矩阵和非法参数路径；参数探针还会在 Python 级别复核 M6 的 `20 mm` 节距、`+10…+190 mm` 高度、x 轴 -45° 姿态、后方浅六角定位、主体厚度、竖直球头 z- 接口、连接器高度和网夹立柱孔位。`test_m6_machining_previews.py` 会实际导出主体左右两件局部首样/CNC 复用预览并检查封闭拓扑和关键包围盒；`test_m6_component_previews.py` 会实际导出当前主体、前后盖、底盖两侧共 8 个完整 STL，检查左右镜像、材料/打印候选元数据、封闭拓扑和主体 `10×56×216 mm` 包络。除组合装配预览外，成功导出的独立打印零件还会做 STL 封闭边拓扑检查。装配预览允许桌板、网布和电子/标准件包络重叠，只用于 PNG，不是打印件。后者从同一份参数源渲染当前装配、左右支架、桌下夹持、45° L 型 M6 光电器件阵列、竖直球头、球头下金属 90°连接器、PVDF 座和标定规，输出到 `rendered/net-stand-*.png`。CI 会把当前和历史两套渲染证据分别保存。

`render_m6_views.py` 输出到被 Git 忽略的 `rendered/m6-audit/`：六个正交视图和一个等轴视图。视图使用明确的 `x−` 光学端、`x+` 线缆端、`y−/y+` 球台前后、`z+` 俯视和 `z−` 仰视相机；`m6_detector_exploded` 仍是完整实体拉开显示，不做剖切。方向箭头仅为检查叠加，不进入独立 STL。默认 `--side 1` 查看右侧接收端；用 `--side -1` 查看左侧发射端，脚本会同步镜像相机并在文件名中保留 `side-1`。检查球头是否装在壳体后端面时，应优先看 `rear-cable-xplus-side1`（右侧）和 `rear-cable-xplus-side-1`（左侧）正交图，等轴图中的球头锁紧钮不代表壳体侧挂。

## 历史方案

`net_post_x_clamp.scad` 是前一轮外挂式 X 型立柱夹具。它被明确保留在 [`legacy/README.md`](legacy/README.md) 所述的历史边界内，用于设计回溯和旧几何回归；旧验证脚本 `validate_scad.py`、`validate_geometry.py`、`render_openscad_preview.py` 不应再被当作当前机械参数源。

当前与历史方案都暂不承诺比赛级裁判准确率。先打印内置支架的机械样件，确认球台厚度、夹持范围、网布张力、传感器安装和光学对准，再收敛尺寸与材料。
