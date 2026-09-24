# OpenSCAD 机械主线

当前机械源文件是 [`net_stand.scad`](net_stand.scad)。它把球网、两侧立柱、桌下夹体、PVDF 传感器安装位、M6 光学壳体以及电子腔体放在同一套参数坐标中，用于装配干涉和打印件导出。

当前版本的边界很明确：网顶不设轨道；侧边空心布套先套到 `Ø10 mm × 152.5 mm` 圆柱插杆，再沿原门洞轴线从 x 侧推入两侧斜立柱下段的侧开接收腔，门洞横向宽度沿用历史 `15.2 mm`，从顶部下 `30 mm` 分型面装上上段封住插入口。斜立柱在顶部下 `30 mm` 分为下段和上段，公母定位键及四枚 `M3×40` 自攻钉只连接这两个立柱打印件；不再使用外侧矩形 U 夹。网端附近左右各一个 PVDF 振动传感器，传感器与网架保留 `18 mm` 横向净距。

本轮依据的 SketchUp 草图只作为形状关系参考，不作为实际尺寸源：左侧是固定灰色 C 形夹主体，右侧是斜立柱和绿色整体底座。当前正式接口采用 `779f046` 中的 C 方案：灰色 C 夹外侧切出让位腔，绿色底座沿 x 方向推入，黄色立柱在 `z=16 mm` 与绿色底座相接；底座保留两枚 `Ø4 mm` 通孔、中央 `Ø6×2 mm` 底坑和两侧 `15 mm` 外伸。立柱在 `z=230.5 mm` 分型，顶部 `30 mm` 上段继续到 `z=260.5 mm`，网布/圆柱插杆功能区仍只到 `z=168.5 mm`。正式尺寸仍以本文件的首样参数和验证约束为准。

夹体现在采用沿 `y=0` 分型的两半打印，斜立柱和绿色底座按上下分段：`clamp_body_half_user` 是操作者侧 y- 半体，`clamp_body_half_opponent` 是对手侧 y+ 半体，黄绿连接件的下段为 `post_clamp_carrier_lower`，顶部 30 mm 为 `post_clamp_carrier_upper`。两半用 9 套横向 M5 螺钉连接；两侧 y=0 分型内侧浅凹槽底对应阳刻相同的 `1…9` 编号，字顶低于分型基准，不落到外表面也不干涉合拢；左下角连接孔向外侧移动，电子仓左下角和右下斜加强边沿各有一个连接点，其中 6、7 号连接点及其 boss/孔位整体沿 Z− 下移 `9 mm`，前半圆头沉孔朝外，后半六角螺母窝朝外。只有贴着电子仓空腔面的连接点增加 boss 柱和十字肋，实心夹臂里的连接点只保留通孔/沉孔，避免外壳凸起。电子腔从分型面打开后可装板、走线。y+ 侧壁开出 `64×34 mm` 窗口。UI 结构现在是一个一体式打印件：外轮廓 `62.8×32.8 mm` 的齐平填平板、腔内阶梯式固定法兰、窗口捕获环和 8 个通孔在同一 STL 中融合；它从腔内 y- 侧推入，外表面与 C 夹壁齐平且不打螺钉孔，也没有隐藏 boss 收纳槽。腔内固定法兰位于 y=`17.5..20.0 mm`，窗口内捕获环延伸到 y=`25.5 mm` 并向面板周边压入 `0.4 mm`，整体外轮廓为 `72×42 mm`；8 个 `Ø2.3 mm` 通孔从腔内装入 `2 mm` 蘑菇头自攻钉，直接锁入 C 夹实心内壁 `Ø1.6 mm` 盲导孔；孔中心相对旧 M3 方案整体向外移 1.0 mm，孔边仍保留至少 `1.2 mm` 实体边，外壁底厚保留 `0.7 mm`，不生成正向 UI boss 柱。按键用封口板内侧导向柱，LED 的直孔可装透明导光柱，Type-C 直接走通槽，屏幕和扬声器留在腔内。安装时仍把绿色底座从 C 夹 x+ 开放端推入让位腔，两个 M4 螺钉穿过灰色 `Ø4.4 mm` 孔和绿色 `Ø4 mm` 孔，底部钢珠进入 `Ø6×2 mm` 浅坑定位。黄色立柱下段在 `z=16 mm` 与绿色底座相接并延伸到分型面 `z=230.5 mm`，顶部 30 mm 上段延伸到 `z=260.5 mm`，四枚 `M3×40` 连接上下段；网布/圆柱插杆功能区仍只到 `z=168.5 mm`。这里没有 T 槽、公轨、第二个滑靴或旧的直接共面座；分型总间隙 `0.20 mm` 是打印装配余量，不是强度或防水承诺。
电子腔本体采用“右侧桥体大面积内缩、内部形成整段电子仓”的真实负空间：全腔约 `117×40 mm`，两侧保留 `9 mm` 承力壁，上方保留约 `15.5 mm` 上部承力层，底部保留一体化 `4 mm` 斜底；两半分开后从 `y=0` 分型面装入 PCB/电池，主控板的 Edge.Cuts 轮廓先相减出板形让位，再由 x− 端 `[` 与 x+ 端 `]` 两件端部 C 形夹件承托和防上浮，端部整条竖根留在实心端墙内，不使用底部 standoff、PCB boss 或伸入腔体的主板螺钉。电池放在主控板器件层上方的第二层托位，避免夹件压穿电池，`x+` 外侧墙和 M5 boss 保持完整。正式 STL 不包含外购螺钉；正式打印包包含左右各一件从腔内装入的一体式 y+ UI 填平固定板（面板、腔内法兰、捕获环和 8 个孔融合为一件），当前源文件不再定义旧的电子腔底盖或连续垫。`net-stand-clamp-split-electronics-cutaway.png` 是诊断剖视图，会把 y- 外壁打开来显示真实大腔和分型面装配路径；窗口不代表正式打印件少了 x+ 外墙或承力结构。

电池、屏幕和扬声器等不贴 PCB、通过线束连接的实体包络统一定义在 [`electronics_components.scad`](electronics_components.scad) 中，每种物件只有一个模块定义；`net_stand.scad` 只在世界坐标中挂载这些实例。按键、0603 LED 和 USB-C 属于 PCB 直装件，必须使用 KiCad 封装中的 3D 模型，并随 UI 板 STL 一起导出，SCAD 不再复制它们。`clamp_electronics_ui_component_alignment_check`、UI 面板布局断言和电子腔空交集探针会把 KiCad 板模型与 SCAD 线束件一起检查对位/干涉。网页电子腔视图若要查看 SCAD 线束实体，可导出 `PART="clamp_electronics_ui_physical_items"` 到本地 `hardware/electronics/3d/v0.2/ui-physical-items-v0.2.stl`。

这里的“水密”只表示盒盖、压合边和接口在 CAD 中严丝合缝、没有明显贯穿缝；不宣称 IP 等级，也不替代实物淋水/装配检查。

## 当前源模型入口

常用 `PART`：

- `assembly`：完整球台截面、网布、两侧立柱/夹体、无网顶轨道的网端圆柱插杆、PVDF、左右十路 M6 发射/接收器件、M6 分体壳、球头和电子腔体装配预览；
- `left_stand` / `right_stand`：单侧装配预览；
- `post_clamp_carrier`：两段斜立柱与绿色整体底座的装配预览，不直接作为一件打印；正式打印件为 `post_clamp_carrier_lower` 和 `post_clamp_carrier_upper`。下段沿 x 方向进入灰色 C 夹让位腔，含两枚 `Ø4 mm` 孔、`Ø6×2 mm` 底坑、网布门洞和原位置侧开圆柱接收腔；上段为顶部下 `30 mm` 的可替换件，带公母键、四枚 `Ø3.4 mm` M3 通孔和顶部 M8 支撑孔；
- `post_clamp_seated`：绿色底座推进到底、黄色立柱坐在其 `z=16 mm` 接口上的装配证据；
- `post_clamp_seated_fit_section`：沿 C 方案底座和中央定位坑截取的坐定剖面，直接查看灰色让位腔、绿色底座、黄色渐变和钢珠定位的关系；
- `post_clamp_carrier_lower` / `post_clamp_carrier_upper`：正式打印的下段/上段；`post_segment` / `lower_stand_segment` / `upper_stand_segment` 是兼容诊断入口，不替代这两个正式 STL；
- `clamp_body_half_user` / `clamp_body_half_opponent`：沿 `y=0` 分型的操作者侧/对手侧 C 形夹半体；每半含整段大面积电子仓、完整 x+ 外侧 C 壁、绿色底座让位腔的一半、9 个横向 M5 连接点（只有碰到电子仓空腔面的点加 printed boss/rib，其余只保留通孔和沉孔）、前侧圆头沉孔或后侧防转六角螺母窝；两侧 y=0 分型内侧浅凹槽底对应阳刻相同的 `1…9` 装配编号，字顶低于分型基准；左下角连接孔向外侧移动，电子仓左下角和右下斜加强边沿各增加一个连接点；两半合拢后仍保留两枚 `Ø4.4 mm` C 方案连接孔和中央钢珠定位孔；
- `clamp_body_split_fit` / `clamp_body_split_exploded`：分型合拢和拆开的预览入口，不是打印件；
- 旧的电子腔底盖、连续垫和 UI boss 兼容入口已从当前源文件移除；左右各一件一体式 y+ 外侧齐平 UI 填平固定板是正式打印件。该一体件带屏幕窗、按键浅凹面/1.6 mm 内侧导向柱、0603 LED 直孔、扬声器窗和由当前 KiCad USB-C 外壳/屏蔽件尺寸生成的 0.25 mm 装配通道（排除侧面焊接脚）；外表面再做一个到达 KiCad 金属外壳前沿的圆角碗槽，外围保留 `0.60 mm` 连续环形打印底，中心 KiCad-fit 通孔贯穿并由 Type-C 金属壳体负责显示/插入，不再使用固定 1.25 mm 浅碗；没有隐藏 boss 收纳槽，外侧不打螺钉孔；腔内固定法兰位于 y=`17.5..20.0 mm`，窗口内捕获环到 y=`25.5 mm` 并与面板周边融合 `0.4 mm`，固定板外延加宽到 `72×42 mm`，带 8 个 `Ø2.3 mm` 通孔，从腔内装入 2 mm 蘑菇头自攻钉并直接进入 C 夹内壁 `Ø1.6 mm` 盲导孔；孔中心相对旧 M3 方案向外移 1.0 mm，孔边至少保留 `1.2 mm` 实体边，不使用正向 boss 柱。一体件从电子腔 y- 侧穿入并与外壁齐平；分开两半后从 y=0 分型面装入电子件，底部使用一体化斜底；
- `m6_detector_body` / `m6_detector_shell_front` / `m6_detector_shell_rear` / `m6_detector_bottom_cover`：M6 光学壳体四件；
- `net_clamp_rod`：正式打印的一根 `Ø10 mm × 152.5 mm` 圆柱插杆；导出 STL 时圆柱轴线沿 X 平放，装配时轴线保持竖直 Z，连同球网空心边套沿原门洞方向从 x 侧推入立柱下段侧开接收腔；不再有矩形卡条、U 夹或 keeper；
- `sensor_mount_body` / `sensor_clamp_lip` / `pvdf_film`：网端 PVDF 安装件；
- `clamp_pressure_pad` / `clamp_screw` / `clamp_knob` / `calibration_gauge`：桌下夹持和标定件；
- `clamp_slide_fit_probe` / `clamp_slide_exploded` / `clamp_slide_fit_section`：历史命名下的 C 方案让位腔、推进和定位诊断入口，不是独立滑轨打印件；
- `clamp_electronics_ui_physical_items` / `clamp_electronics_ui_component_alignment_check`：SCAD 线束实体件（屏幕/扬声器）装配和世界坐标/包络检查；PCB 按键、LED、USB-C 由 KiCad 板 STL 提供，不是独立打印件；
- `net_clamp_fit_probe` / `net_clamp_fit_section`：网布 3 mm 过道、半透明空心边套、Ø10 mm 圆柱插杆和原位置侧开接收腔的真实截面证据；
- `table_clamp_section` / `parameter_probe`：剖面和验证脚本参数探针，不是打印件。

`net_rail*`、`post_joint_sleeve`、`post_joint_key` 等名称只保留为历史/兼容诊断入口，不属于当前装配或打印清单；当前网端件是 `net_clamp_rod`。

## 导出和验证

正式打印导出只使用同一份 SCAD 参数源：

```text
python3 export_net_stand_printables.py --clean
python3 test_export_net_stand_printables.py
python3 build_print_platter.py --preset x1c-256 --clean
python3 test_build_print_platter.py --default
python3 validate_net_stand.py
```

正式包的当前结果是 `41` 个 STL，包含左右 y+ 外侧齐平 UI 填平固定板、一根圆柱插杆、斜立柱下段/顶部 30 mm 上段，以及 12 mm 大径/4 mm 螺距、2 mm 牙根与 2 mm 凹槽、0.4 mm 锥尖的 PETG 锥形粗牙螺杆、固定螺母和旋钮对锁螺母；牙根采用连续实体带，适合 FDM 扭矩，不再是细线牙或平顶环带。圆柱插杆包络约 `10×10×152.5 mm`，立柱下段和上段分别按各自姿态导出。`--clean` 会清除旧版网夹上下段、旧整件 C 夹、外挂套筒和内芯，避免历史文件静默混入。默认输出目录是 [`exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/`](exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/)，每个 STL 的来源、左右侧、材料、包围盒和封闭拓扑摘要记录在其中的 `manifest.json`。

分型后的两个 C 夹半体、斜立柱下段/上段、一体式 y+ 外侧齐平填平固定板和圆柱插杆是不同打印对象：`clamp_body_half_user`、`clamp_body_half_opponent`、`post_clamp_carrier_lower`、`post_clamp_carrier_upper`、`clamp_electronics_ui_panel_mount`、`net_clamp_rod`。旧的网夹上下段目录已作废，不能把旧文件混入当前包。需要直接换打接口时运行 `python3 build_net_clamp_bambu_package.py --side both`，使用 `exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme-3mf/` 下左右两个可编辑 X1C/PETG 3MF；每个文件包含前后两个夹体半件、立柱下段、立柱上段、一体式 y+ 外侧填平固定板和圆柱插杆六个对象。

256 mm 打印床的几何拼盘结果记录在 [`exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/print-platter-256/manifest.json`](exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/print-platter-256/manifest.json)：当前脚本目标为 `7` 张板、`41` 个已排零件、`0` 个超床件。左右两件下段黄绿连接件采用 `rx=0°、ry=51°、rz=45°` 三轴刚体斜放，顶部上段按分型面平放；两个 C 夹半体把各自 y 外侧大平面贴床，端部 `[ / ]` 夹件沿 y 方向逐层生成，一体式 圆柱网杆平放。这个结果只证明保守包络排版和 STL 几何，不等于已经切片、配置支撑、生成 G-code 或完成实物打印。

建议在导出后对全部 STL 做封闭拓扑复核：

```text
for stl in exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/*.stl; do
  python3 /Users/norman/.codex/skills/openscad-stl-print/scripts/inspect_stl.py --require-watertight "$stl" >/dev/null || exit 1
done
```

## 预览和人工检查

```text
python3 render_net_stand_preview.py
python3 test_preview_consistency.py
python3 -m http.server 8000
```

浏览器装配页位于 [`preview/index.html`](preview/index.html)，可以切换装配、爆炸、打印拼盘和零件清单；真实打印件按 manifest 加载，电子腔专页加载包含 PCB 直装按键/LED/USB-C 模型的 KiCad 板级 STL，并把屏幕/扬声器等 SCAD 线束实体作为装配件检查。重点查看：

网页装配页现在直接加载正式 C 方案夹体半件和黄绿连接件；SKP 腿脚不再作为“候选件”叠加到另一套共面模型上。三维工具栏仍保留 C 方案近景，并增加 y=0 分型合拢/爆炸检查，便于检查 M5 boss、螺母窝、电子腔和底座让位腔。

- 网页爆炸视图中 `clamp_body_half_user` / `clamp_body_half_opponent` 沿 y 方向分开，`post_clamp_carrier_lower` 沿 `x+ → x−` 滑入/拉出，`post_clamp_carrier_upper` 沿 z 方向从分型面抬起；爆炸状态会把分型面、M5 boss、电子腔和立柱公母键打开，不把承座误显示成随载体移动的平台；

- [`clamp slide exploded`](rendered/net-stand-clamp-slide-exploded-right.png)：固定灰色 C 形主体与黄绿连接件的分体关系；重点检查绿色底座沿 x 方向退出/推进、两枚连接孔和中央定位坑；
- [`post/clamp seated`](rendered/net-stand-post-clamp-seated-right.png)：推进到底后的最终坐定状态，黄色立柱坐在绿色底座上，绿色底座落入灰色让位腔；
- [`post/clamp seated section`](rendered/net-stand-post-clamp-seated-fit-section-right.png)：真实 C 方案坐定界面的局部剖面，检查灰色让位腔、绿色底座、黄色 `30 mm` 渐变和中央钢珠；
- [`post/clamp entry open section`](rendered/net-stand-post-clamp-entry-open-section-right.png)：从开放装配方向查看让位腔入口和绿色底座的真实薄剖面；
- [`post/clamp slide exploded`](rendered/net-stand-post-clamp-slide-exploded-right.png)：固定夹体保持不动，黄绿连接件沿真实 x 方向拉出，用于检查两件装配关系；
- [`post/clamp slide interface exploded`](rendered/net-stand-post-clamp-slide-interface-exploded-right.png)：只截取底部连接接口，专门核对绿色整体底座、两个 `Ø4 mm` 孔、灰色 `Ø4.4 mm` 孔和中央定位坑；
- [`clamp slide section`](rendered/net-stand-clamp-slide-fit-section-right.png)：历史命名下的 C 方案 y 剖面诊断，不表示当前存在独立公母滑轨；
- [`clamp slide foot detent detail`](rendered/net-stand-clamp-slide-foot-detent-detail-right.png)：兼容诊断名，放大绿色底座和钢珠定位结构。
- [`net rod section`](rendered/net-stand-net-clamp-fit-section-right.png)：网布空心边套套在 Ø10 mm 圆柱插杆上，一起沿原门洞轴线从 x 侧进入下段侧开接收腔；半透明圆筒只表示布套包络，正式打印件只有圆柱插杆。四枚 M3×40 不属于网端件，而是属于立柱上下分型连接；
- [`assembly`](rendered/net-stand-assembly.png)：完整壳体、网布和两侧端部传感器的总干涉关系。

当前机械验证仍需实物完成：实际网布厚度与张力、内嵌止挡的脱出行程与释放手感、立柱与 C 夹的打印配合和落座稳定性、PETG 夹体耐久、盒盖装配缝、线缆弯曲半径、电子板与 boss 的真实装配、以及首层/切片后的打印结果。当前文件没有把这些未测项目写成已通过。
