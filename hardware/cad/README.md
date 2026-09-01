# OpenSCAD 机械主线

当前机械源文件是 [`net_stand.scad`](net_stand.scad)。它把球网、两侧立柱、桌下夹体、PVDF 传感器安装位、M6 光学壳体以及电子腔体放在同一套参数坐标中，用于装配干涉和打印件导出。

当前版本的边界很明确：网顶不设轨道；网布从球台中心侧穿过两侧立柱的连续 `3 mm` 过道，网布端部止到立柱外表面，再从桌外侧沿 `x+ → x−` 推入整高 U 形卡网夹。卡网夹的两片夹爪夹住网布，网布张力和绳的拉力负责把卡夹压在承托面上，立柱内嵌单一被动止挡只防止向外拔出，不使用穿钉；按开夹爪即可反向滑出。网端附近左右各一个 PVDF 振动传感器，传感器与网架保留 `18 mm` 横向净距。

本轮依据的 SketchUp 草图只作为形状关系参考，不作为实际尺寸源：左侧是固定灰色 C 形夹主体，右侧是整根立柱；草图中的颜色和“脚/裤裆”说法不进入当前结构。当前正式方案的立柱底面与 C 夹黄灰交界 `z=16 mm` 共面，一体实心延伸至 `z=372.5 mm`（总高 `356.5 mm`），不向下插入固定夹；网布/卡夹功能区仍只到 `z=168.5 mm`。从承托面 `z=16 mm` 向上 `30 mm` 做连续实心渐变，到 `z=46 mm` 后统一保持顶端 `28×38 mm` 截面。正式尺寸仍以本文件的首样参数和验证约束为准。

夹体采用两件式打印，立柱保持整根：固定的完整灰色 C 形主体为 `clamp_body_segment`，整根立柱为 `post_clamp_carrier`。立柱底面在 `z=16 mm` 共面坐在固定基台上，实体连续到 `z=372.5 mm`，不向下插入固定夹；网布/卡夹功能区仍只到 `z=168.5 mm`。从该承托面向上 `30 mm`（到 `z=46 mm`）做封闭实心连续渐变，之后统一保持顶端 `28×38 mm` 截面。两侧是连续斜坡，不做台阶、两种粗细矩形柱套接、外套圈、后置延长块、两只脚、裤裆或独立滑靴；立柱本体从底到顶没有第二道接缝。必要的网布 `3 mm` 过道和 U 形卡网夹接收腔仍作为功能开口，其余过渡保持实心；本轮不在固定网柱顶端切 M8 直连孔。两件从夹具体开放方向装配；图示 `0.1 mm` 只用于分色显示，不是实体间隙。

这里的“水密”只表示盒盖、压合边和接口在 CAD 中严丝合缝、没有明显贯穿缝；不宣称 IP 等级，也不替代实物淋水/装配检查。

## 当前源模型入口

常用 `PART`：

- `assembly`：完整球台截面、网布、两侧立柱/夹体、无网顶轨道的网端 U 夹、PVDF、左右十路 M6 发射/接收器件、M6 分体壳、球头和电子腔体装配预览；
- `left_stand` / `right_stand`：单侧装配预览；
- `post_clamp_carrier`：从黄灰交界 `z=16 mm` 起一体实心延伸至 `z=372.5 mm` 的整根立柱、连续网布过道和外侧卡夹接收腔；网布/卡夹功能区到 `z=168.5 mm`，下端底面与固定基台共面，不带 C 形固定壁，也不切固定网柱顶端 M8 直连孔；
- `post_clamp_seated`：整根立柱坐在固定 C 夹最高水平承托面上的装配证据；立柱底面与 `z=16 mm` 共面，不向下插入 C 形座；
- `post_clamp_seated_fit_section`：沿立柱下端截取的坐定剖面，直接查看 `35×58 mm` 下端、`z=16..46 mm` 锥形过渡和上段恒定 `28×38 mm` 的关系；
- `post_segment` / `lower_stand_segment` / `upper_stand_segment`：仅为旧调用兼容入口，不属于正式打印矩阵；
- `clamp_body_segment`：完整灰色 C 形固定主体打印件，含梯形电子腔、完整外侧 C 壁、盖板安装 boss，以及与立柱最低面共面的固定基台坐面；
- `clamp_electronics_cover` / `clamp_electronics_gasket` / `clamp_electronics_ui_bezel`：梯形腔盖、柔性压合件和交互面板压框；
- `m6_detector_body` / `m6_detector_shell_front` / `m6_detector_shell_rear` / `m6_detector_bottom_cover`：M6 光学壳体四件；
- `net_clamp_clip`：实际安装姿态的整高 U 形卡网夹；`net_clamp_clip_printable`：平放打印姿态；
- `sensor_mount_body` / `sensor_clamp_lip` / `pvdf_film`：网端 PVDF 安装件；
- `clamp_pressure_pad` / `clamp_screw` / `clamp_knob` / `calibration_gauge`：桌下夹持和标定件；
- `clamp_slide_fit_probe` / `clamp_slide_exploded` / `clamp_slide_fit_section`：历史命名下的共面落座/渐变剖面诊断入口，不是独立滑轨打印件；
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

正式包的当前结果是 `33` 个 STL。`--clean` 会清除旧版分体立柱、外挂套筒、内芯和圆柱卡网件，避免历史文件静默混入。每个 STL 的来源、左右侧、材料、包围盒和封闭拓扑摘要记录在 [`exports/net-stand-v0.1/manifest.json`](exports/net-stand-v0.1/manifest.json)。

256 mm 打印床的几何拼盘结果记录在 [`exports/net-stand-v0.1/print-platter-256/manifest.json`](exports/net-stand-v0.1/print-platter-256/manifest.json)：`6` 张板、`33` 个已排零件、`0` 个超床件。两件整根立柱采用 `rx=0°、ry=51°、rz=45°` 三轴刚体斜放，实际变换包络约 `252.5×252.5×251.6 mm`，按该件专用 `1.5 mm` 名义边缘余量排版；这个结果只证明保守包络排版和 STL 几何，不等于已经切片、配置支撑、生成 G-code 或完成实物打印。

建议在导出后对全部 STL 做封闭拓扑复核：

```text
for stl in exports/net-stand-v0.1/*.stl; do
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

本阶段的 SKP 腿脚候选也已接入同一 WebGL 装配页，但明确标为候选件：它不进入正式打印 manifest / 打印拼盘。当前新增“显示灰色 C 型夹让位候选”开关，用黄色立柱下端与绿色 SKP 腿脚的组合外形对灰色 C 型夹做差集，让位后的灰色夹体与黄色、绿色件保持同一安装坐标；关闭开关可恢复未切的正式灰色夹体。三维工具栏的“SKP 腿脚近景”仍只保留右侧绿色候选件，便于分别确认腿脚形状和让位结果。正式打印件在用户确认前不替换。

- 网页爆炸视图中 `clamp_body_segment` 作为固定基台保持在原坐标，只有整根 `post_clamp_carrier` 沿 `x+ → x−` 滑入/拉出；爆炸状态不会把承座误显示成随载体移动的平台；

- [`clamp slide exploded`](rendered/net-stand-clamp-slide-exploded-right.png)：固定灰色 C 形主体与整根橙色立柱的分体关系；重点检查立柱底面与 `z=16 mm` 共面、实体连续到 `z=372.5 mm`、网布/卡夹功能区到 `z=168.5 mm` 以及从该面向上 `30 mm` 的连续渐变，不把历史命名理解为当前独立滑轨；
- [`post/clamp seated`](rendered/net-stand-post-clamp-seated-right.png)：推进到底后的最终坐定状态，立柱底面与固定夹具基台的落座关系可直接检查；
- [`post/clamp seated section`](rendered/net-stand-post-clamp-seated-fit-section-right.png)：真实坐定界面的局部剖面，固定夹承托面为 `z=16 mm`，立柱底面共面落座，其上 `30 mm`（至 `z=46 mm`）连续渐变收至 `28×38 mm`，全段为同一实心体；
- [`post/clamp entry open section`](rendered/net-stand-post-clamp-entry-open-section-right.png)：从开放装配方向查看固定灰色主体与橙色整根立柱的真实薄剖面；只显示必要的网布/卡网开口，不添加脚、裤裆、滑靴、咯噔件或虚构透明块；
- [`post/clamp slide exploded`](rendered/net-stand-post-clamp-slide-exploded-right.png)：固定夹体保持不动，整根立柱作为单一打印件显示在外侧，用于检查两件装配关系、`z=16 mm` 共面落座、其上 `30 mm` 连续渐变和上段恒定截面；
- [`post/clamp slide interface exploded`](rendered/net-stand-post-clamp-slide-interface-exploded-right.png)：只截取立柱底部与固定基台，专门核对“立柱底面与 `z=16 mm` 共面，整根实体延伸至 `z=372.5 mm`，网布/卡夹功能区止于 `z=168.5 mm`，不插入 C 形座”；
- [`clamp slide section`](rendered/net-stand-clamp-slide-fit-section-right.png)：历史命名下的立柱/C 夹剖面诊断，检查 `z=16 mm` 共面、`35×58 → 28×38 mm` 和 `30 mm` 连续渐变，不表示当前存在两条独立公母滑轨；
- [`clamp slide foot detent detail`](rendered/net-stand-clamp-slide-foot-detent-detail-right.png)：兼容诊断名，当前只放大同一段实心渐变，不生成脚、裤裆或咯噔硬件。
- [`net clip section`](rendered/net-stand-net-clamp-fit-section-right.png)：网布穿过 `3 mm` 过道、止到连续立柱本体外边，整高 U 夹从外侧 `x+` 进入并由外侧横梁止挡；夹爪咬合网布，立柱内嵌单一被动止挡只防拔出，无穿钉，不使用传统圆柱卡网件；
- [`assembly`](rendered/net-stand-assembly.png)：完整壳体、网布和两侧端部传感器的总干涉关系。

当前机械验证仍需实物完成：实际网布厚度与张力、内嵌止挡的脱出行程与释放手感、立柱与 C 夹的打印配合和落座稳定性、PETG 夹体耐久、盒盖装配缝、线缆弯曲半径、电子板与 boss 的真实装配、以及首层/切片后的打印结果。当前文件没有把这些未测项目写成已通过。
