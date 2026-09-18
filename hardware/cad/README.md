# OpenSCAD 机械主线

当前机械源文件是 [`net_stand.scad`](net_stand.scad)。它把球网、两侧立柱、桌下夹体、PVDF 传感器安装位、M6 光学壳体以及电子腔体放在同一套参数坐标中，用于装配干涉和打印件导出。

当前版本的边界很明确：网顶不设轨道；网布从球台中心侧穿过两侧立柱的连续 `3 mm` 过道，网布端部止到立柱外表面，再从桌外侧沿 `x+ → x−` 推入整高 U 形卡网夹。卡网夹的两片夹爪夹住网布，网布张力和绳的拉力负责把卡夹压在承托面上，立柱内嵌单一被动止挡只防止向外拔出，不使用穿钉；按开夹爪即可反向滑出。网端附近左右各一个 PVDF 振动传感器，传感器与网架保留 `18 mm` 横向净距。

本轮依据的 SketchUp 草图只作为形状关系参考，不作为实际尺寸源：左侧是固定灰色 C 形夹主体，右侧是整根立柱和绿色整体底座。当前正式接口采用 `779f046` 中的 C 方案：灰色 C 夹外侧切出让位腔，绿色底座沿 x 方向推入，黄色立柱在 `z=16 mm` 与绿色底座相接；底座保留两枚 `Ø4 mm` 通孔、中央 `Ø6×2 mm` 底坑和两侧 `15 mm` 外伸。主体继续到 `z=260.5 mm`，网布/卡夹功能区仍只到 `z=168.5 mm`。正式尺寸仍以本文件的首样参数和验证约束为准。

夹体采用两件式打印，立柱和绿色底座合为一件：固定的完整灰色 C 形主体为 `clamp_body_segment`，整根黄绿连接件为 `post_clamp_carrier`。安装时把绿色底座从灰色夹体的 x+ 开放端推入让位腔，两个 M4 螺钉穿过灰色 `Ø4.4 mm` 孔和绿色 `Ø4 mm` 孔，底部钢珠进入 `Ø6×2 mm` 浅坑定位。黄色立柱在 `z=16 mm` 与绿色底座相接，主体连续到 `z=260.5 mm`；网布/卡夹功能区仍只到 `z=168.5 mm`。这里没有 T 槽、公轨、第二个滑靴或旧的直接共面座；图示 `0.1 mm` 只用于分色显示，不是实体间隙。

这里的“水密”只表示盒盖、压合边和接口在 CAD 中严丝合缝、没有明显贯穿缝；不宣称 IP 等级，也不替代实物淋水/装配检查。

## 当前源模型入口

常用 `PART`：

- `assembly`：完整球台截面、网布、两侧立柱/夹体、无网顶轨道的网端 U 夹、PVDF、左右十路 M6 发射/接收器件、M6 分体壳、球头和电子腔体装配预览；
- `left_stand` / `right_stand`：单侧装配预览；
- `post_clamp_carrier`：整根黄色立柱与绿色 SKP 整体底座的一体打印件；底座沿 x 方向进入灰色 C 夹让位腔，含两枚 `Ø4 mm` 孔和 `Ø6×2 mm` 底坑；主体到 `z=260.5 mm`，不带灰色 C 壁，也不切固定网柱顶端 M8 直连孔；
- `post_clamp_seated`：绿色底座推进到底、黄色立柱坐在其 `z=16 mm` 接口上的装配证据；
- `post_clamp_seated_fit_section`：沿 C 方案底座和中央定位坑截取的坐定剖面，直接查看灰色让位腔、绿色底座、黄色渐变和钢珠定位的关系；
- `post_segment` / `lower_stand_segment` / `upper_stand_segment`：仅为旧调用兼容入口，不属于正式打印矩阵；
- `clamp_body_segment`：完整灰色 C 形固定主体打印件，含梯形电子腔、完整外侧 C 壁、盖板安装 boss、绿色底座让位腔、两枚 `Ø4.4 mm` 连接孔和中央钢珠定位孔；
- `clamp_electronics_cover` / `clamp_electronics_gasket` / `clamp_electronics_ui_bezel`：梯形腔盖、柔性压合件和交互面板压框；
- `m6_detector_body` / `m6_detector_shell_front` / `m6_detector_shell_rear` / `m6_detector_bottom_cover`：M6 光学壳体四件；
- `net_clamp_clip`：实际安装姿态的整高 U 形卡网夹；`net_clamp_clip_printable`：平放打印姿态；
- `sensor_mount_body` / `sensor_clamp_lip` / `pvdf_film`：网端 PVDF 安装件；
- `clamp_pressure_pad` / `clamp_screw` / `clamp_knob` / `calibration_gauge`：桌下夹持和标定件；
- `clamp_slide_fit_probe` / `clamp_slide_exploded` / `clamp_slide_fit_section`：历史命名下的 C 方案让位腔、推进和定位诊断入口，不是独立滑轨打印件；
- `net_clamp_fit_probe` / `net_clamp_fit_section`：网布过道、U 夹夹爪和单一内嵌被动止挡防拔路径的真实截面证据；
- `table_clamp_section` / `parameter_probe`：剖面和验证脚本参数探针，不是打印件。

`net_rail*`、`post_joint_sleeve`、`post_joint_key`、旧 `net_clamp_rod` 等名称只保留为历史/兼容诊断入口，不属于当前装配或打印清单。

## 导出和验证

正式打印导出只使用同一份 SCAD 参数源：

```text
python3 export_net_stand_printables.py --clean
python3 test_export_net_stand_printables.py
python3 build_print_platter.py --preset x1c-256 --clean
python3 test_build_print_platter.py --default
python3 validate_net_stand.py
```

正式包的当前结果是 `37` 个 STL。`--clean` 会清除旧版分体立柱、外挂套筒、内芯和圆柱卡网件，避免历史文件静默混入。默认输出目录是 [`exports/desktop-clamp-one-side-x1c-v0.4-top-load/`](exports/desktop-clamp-one-side-x1c-v0.4-top-load/)，每个 STL 的来源、左右侧、材料、包围盒和封闭拓扑摘要记录在其中的 `manifest.json`。

固定 C 形主体、整根黄绿连接件和全高 U 形网夹是不同打印件：`clamp_body_segment`、`post_clamp_carrier`、`net_clamp_clip`。旧的直接共面座目录已作废，不能把旧夹体和 C 方案立柱混用。需要直接换打接口时运行 `python3 build_net_clamp_bambu_package.py --side both`，使用 `exports/desktop-clamp-one-side-x1c-v0.6-c-scheme/` 下左右两个可编辑 X1C/PETG 3MF；每个文件都包含配套灰色夹体、黄绿连接件和 U 形网夹三个对象。

256 mm 打印床的几何拼盘结果记录在 [`exports/desktop-clamp-one-side-x1c-v0.4-top-load/print-platter-256/manifest.json`](exports/desktop-clamp-one-side-x1c-v0.4-top-load/print-platter-256/manifest.json)：当前脚本排为 `6` 张板、`37` 个已排零件、`0` 个超床件。两件黄绿连接件采用 `rx=0°、ry=51°、rz=45°` 三轴刚体斜放；这个结果只证明保守包络排版和 STL 几何，不等于已经切片、配置支撑、生成 G-code 或完成实物打印。

建议在导出后对全部 STL 做封闭拓扑复核：

```text
for stl in exports/desktop-clamp-one-side-x1c-v0.4-top-load/*.stl; do
  python3 /Users/norman/.codex/skills/openscad-stl-print/scripts/inspect_stl.py --require-watertight "$stl" >/dev/null || exit 1
done
```

## 预览和人工检查

```text
python3 render_net_stand_preview.py
python3 test_preview_consistency.py
python3 -m http.server 8000
```

浏览器装配页位于 [`preview/index.html`](preview/index.html)，可以切换装配、爆炸、打印拼盘和零件清单；真实打印件按 manifest 加载，外购器件和网布只作为装配占位。重点查看：

网页装配页现在直接加载正式 C 方案夹体和黄绿连接件；SKP 腿脚不再作为“候选件”叠加到另一套共面模型上。三维工具栏仍保留 C 方案近景，便于检查底座的两个通孔、中央浅坑和灰色让位腔。

- 网页爆炸视图中 `clamp_body_segment` 作为固定基台保持在原坐标，只有整根 `post_clamp_carrier` 沿 `x+ → x−` 滑入/拉出；爆炸状态不会把承座误显示成随载体移动的平台；

- [`clamp slide exploded`](rendered/net-stand-clamp-slide-exploded-right.png)：固定灰色 C 形主体与黄绿连接件的分体关系；重点检查绿色底座沿 x 方向退出/推进、两枚连接孔和中央定位坑；
- [`post/clamp seated`](rendered/net-stand-post-clamp-seated-right.png)：推进到底后的最终坐定状态，黄色立柱坐在绿色底座上，绿色底座落入灰色让位腔；
- [`post/clamp seated section`](rendered/net-stand-post-clamp-seated-fit-section-right.png)：真实 C 方案坐定界面的局部剖面，检查灰色让位腔、绿色底座、黄色 `30 mm` 渐变和中央钢珠；
- [`post/clamp entry open section`](rendered/net-stand-post-clamp-entry-open-section-right.png)：从开放装配方向查看让位腔入口和绿色底座的真实薄剖面；
- [`post/clamp slide exploded`](rendered/net-stand-post-clamp-slide-exploded-right.png)：固定夹体保持不动，黄绿连接件沿真实 x 方向拉出，用于检查两件装配关系；
- [`post/clamp slide interface exploded`](rendered/net-stand-post-clamp-slide-interface-exploded-right.png)：只截取底部连接接口，专门核对绿色整体底座、两个 `Ø4 mm` 孔、灰色 `Ø4.4 mm` 孔和中央定位坑；
- [`clamp slide section`](rendered/net-stand-clamp-slide-fit-section-right.png)：历史命名下的 C 方案 y 剖面诊断，不表示当前存在独立公母滑轨；
- [`clamp slide foot detent detail`](rendered/net-stand-clamp-slide-foot-detent-detail-right.png)：兼容诊断名，放大绿色底座和钢珠定位结构。
- [`net clip section`](rendered/net-stand-net-clamp-fit-section-right.png)：网布穿过 `3 mm` 过道、止到连续立柱本体外边，整高 U 夹从外侧 `x+` 进入并由外侧横梁止挡；夹爪咬合网布，立柱内嵌单一被动止挡只防拔出，无穿钉，不使用传统圆柱卡网件；
- [`assembly`](rendered/net-stand-assembly.png)：完整壳体、网布和两侧端部传感器的总干涉关系。

当前机械验证仍需实物完成：实际网布厚度与张力、内嵌止挡的脱出行程与释放手感、立柱与 C 夹的打印配合和落座稳定性、PETG 夹体耐久、盒盖装配缝、线缆弯曲半径、电子板与 boss 的真实装配、以及首层/切片后的打印结果。当前文件没有把这些未测项目写成已通过。
