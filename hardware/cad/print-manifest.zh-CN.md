# 内置式球网支架首样打印与装配清单 v0.7-split-c-scheme

本清单以 [`net_stand.scad`](net_stand.scad) 为唯一机械参数源。当前主线是不打孔的桌下 C 形夹：M8 螺杆完全位于台面下方，扁球头向上顶独立台底压块；固定 M8 六角螺母从下臂上侧六角沉孔装入，夹体底面不再开一个相反方向的螺母窝。当前 CAD 按 `12…40 mm` 台面厚度冻结，默认 `25 mm`，超过 `40 mm` 必须重新设计夹体和承力壁。夹体分成“y=0 分型的操作者侧/对手侧两个 C 形半体”和“带绿色整体底座的整根立柱”；两个半体沿 ±y 合拢，用 8 套横向 M5 连接，左下角连接孔向外侧移动，电子腔边界前增加连接点，前半圆头沉孔朝外、后半六角螺母窝朝外。只有贴着电子仓空腔面的连接点增加 boss/十字肋，实心夹臂里的连接点只保留通孔/沉孔。电子仓位于 C 夹右侧桥体的整段内缩区域，约 `117×40 mm`，上方保留约 `15.5 mm` 承力层、两侧各 `9 mm` 承力壁和一体化 `4 mm` 斜底；两半分开后从 `y=0` 分型面装入 PCB/电池，主控板由底部柱支撑，电池放在主控板器件层上方的第二层托位，避开底部柱体，不再压穿电池；`x+` 外侧墙和 M5 boss 保持完整，不再使用下方底盖和连续垫。绿色底座从 x+ 开放端推入灰色让位腔，黄色立柱在 `z=16 mm` 与底座相接，主体连续到 `z=260.5 mm`。绿色底座保留两枚 `Ø4 mm` 通孔、中央 `Ø6×2 mm` 底坑和两侧 `15 mm` 外伸；灰色夹体对应两枚 `Ø4.4 mm` 连接孔与下方钢珠定位孔。网布/卡夹功能区仍为 `z=16…168.5 mm`，不使用 T 槽、公轨或第二个独立滑靴。

这里的“水密”只表示盒盖装好后应严丝合缝、没有明显贯通缝、错台或翘边；不代表 IP 等级、防水认证或实物密封测试已经完成。

## 结构主线

- 网顶不设置轨道、承载条、拼接片或承托座。网布总宽基准为 `1830 mm`，网顶高度为 `152.5 mm`。
- 真实网布从球台中心侧先穿过每根立柱的 `3 mm` y 向过道；网布端部止在立柱外侧面，不进入外侧横梁。
- 全高 U 形卡网夹从桌外侧沿 x 向球台中心滑入立柱外侧接收腔。两片 jaw 夹住名义 `1.2 mm` 网布，名义 jaw 间隙 `1.8 mm`；外侧横梁止挡，网布张力和绳的拉力负责压住卡夹，立柱内嵌单一被动止挡只防向外拔出；正侧 jaw 一体弹性扣舌让止挡越过、回拉时由闭合肩拦住。无穿钉、横向销钉或网夹螺钉。
- 立柱整根打印，绿色整体底座并入同一件；固定 C 形主体沿 `y=0` 分成操作者侧 y- 半体和对手侧 y+ 半体。先把后半的 8 枚 M5 六角螺母装入防转窝，再让两个半体沿 y 合拢，从操作者侧拧入 8 枚 M5 圆头螺钉；左下角连接孔已向外侧移动，电子腔边界前增加连接点；分型总间隙 `0.20 mm`。只有碰到电子仓空腔面的连接点才有 printed boss/十字肋，完全位于实心夹臂里的连接点只保留通孔/沉孔，避免外壳凸起。合拢后从 x+ 开放端把绿色底座沿 x 推入灰色让位腔，确认两枚 M4 穿过灰色 `Ø4.4 mm` 孔和绿色 `Ø4 mm` 孔，再让下方 `4 mm` 钢珠进入绿色 `Ø6×2 mm` 底坑。黄色立柱在 `z=16 mm` 与底座相接，主体连续到 `z=260.5 mm`；网布/卡夹功能区仍止于 `z=168.5 mm`。不存在 T 槽、公轨、第二个滑靴或旧版直接共面座；图示间隙只用于打印装配，不是实体强度或防水承诺。
- 网布接近左右网架末端的位置各放一个 PVDF 振动传感器座，传感器座与立柱保留 `18 mm` 横向净距。

## 现行独立打印件：33 件

运行 `python3 export_net_stand_printables.py --clean` 实际导出并由 `test_export_net_stand_printables.py` 锁定为 `33/33`：

| 组别 | 数量 | 正式 `PART` |
| --- | ---: | --- |
| 整根立柱/分型夹体 | 6 | `post_clamp_carrier` ×2、`clamp_body_half_user` ×2、`clamp_body_half_opponent` ×2 |
| 桌下电子腔 | 0 | 电子仓由 C 夹本体一体内缩形成；底盖、连续垫和旧 UI 压框保留为诊断入口，不进入正式打印矩阵 |
| M6 壳体 | 12 | `m6_detector_body`、前盖、后盖、底盖、底盖垫、出线环各左右 1 件 |
| 卡网/夹紧件 | 10 | `net_clamp_clip` ×2、`clamp_pressure_pad` ×2、`clamp_pressure_pad_guard` ×2、`clamp_printed_screw` ×2、`clamp_knob` ×2 |
| PVDF/历史工具 | 5 | `sensor_mount_body` ×2、`sensor_clamp_lip` ×2、`calibration_gauge` ×1 |

逐文件的 `PART`、左右侧、材料、包围盒、体积和封闭拓扑摘要见 [`exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json`](exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json)。

正式清单不包含球台、网布、PVDF 薄膜、ESP32/子板 PCB、电池、M6 光电器件、采购球头、M8/M4/M3 金属件和线束。`post_joint_exploded`、`clamp_slide_exploded`、各类 `fit_section`/`fit_probe` 是检查用组合预览，不是打印件。

## 打印姿态与 256 mm 盘

`net_clamp_clip` 是一件全高、薄厚度的 U 形卡夹：导出 STL 时已把宽面平放，包围盒约 `26.1 × 152.5 × 6.6 mm`；装配时沿 z 立起，从连续立柱本体的外侧开口沿 `x+ → x−` 滑入，外侧横梁负责止挡，不能把它理解成需要轴向插入的圆柱件。其它零件不由脚本缩放或裁切。

默认 `256 × 256 × 256 mm` 拼盘已经生成：[`print-platter-256/manifest.json`](exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/print-platter-256/manifest.json)。当前目标为 `6` 盘、`33` 件已排版、`0` 件超尺寸：两件黄绿连接件采用 `rx=0°、ry=51°、rz=45°` 三轴斜放姿态，各占一张 PETG 盘；两个 C 夹半体与 U 形网夹按实际包络分到多张 PETG 盘，TPU/柔性单独一盘。这个结果证明保守包络排版和 STL 几何，不等于已生成 G-code、已验证切片支撑/首层或已完成实物打印。

## 关键导出命令

```text
python3 export_net_stand_printables.py --clean
python3 build_print_platter.py --preset x1c-256 --clean
python3 test_export_net_stand_printables.py
python3 test_build_print_platter.py --default
python3 validate_net_stand.py
```

单件检查示例：

```text
openscad -D 'PART="clamp_body_half_user"' -D 'SIDE=1' -o right-clamp-body-half-user.stl net_stand.scad
openscad -D 'PART="clamp_body_half_opponent"' -D 'SIDE=1' -o right-clamp-body-half-opponent.stl net_stand.scad
openscad -D 'PART="post_clamp_carrier"' -D 'SIDE=1' -o right-post-clamp-carrier.stl net_stand.scad
openscad -D 'PART="net_clamp_clip"' -D 'SIDE=1' -o right-net-clamp-clip.stl net_stand.scad
openscad -D 'PART="clamp_slide_fit_section"' -D 'SIDE=1' -o clamp-slide-section.png --render net_stand.scad
openscad -D 'PART="net_clamp_fit_section"' -D 'SIDE=1' -o net-clamp-section.png --render net_stand.scad
```

## X1C 3MF 的对象边界

旧的整件 C 夹/直接共面座 3MF 已作废，不能与当前分型 C 方案接口混用。当前可直接打开的 X1C/PETG 文件位于 `exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme-3mf/`。

补打这两个独立件请在 `hardware/cad` 下运行：

```text
python3 build_net_clamp_bambu_package.py --side both
```

输出目录为 `exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme-3mf/`。左右两个 `*-split-c-scheme-X1C-PETG.3mf` 各自都包含 `clamp-body-half-user`、`clamp-body-half-opponent`、`post-clamp-carrier` 和 `net-clamp-clip` 四个完整对象；这是不含 G-code 的可编辑工程，需在 Bambu Studio 中分盘排版后再切片。当前设计没有另一个独立圆柱 `net_clamp_rod`；旧名称只保留为兼容诊断入口。

## 装配顺序

1. 先用目标球台厚度样块（本版适用 `12…40 mm`，默认 `25 mm`），安装左右 `post_clamp_carrier`、固定上夹板胶皮、`clamp_pressure_pad`、`clamp_pressure_pad_guard`、M8 金属螺杆或低载临时 `clamp_printed_screw`、下臂上侧固定螺母和旋钮内两枚预对锁螺母；确认不打孔、不碰台面、不干涉压块/螺杆工作区。背护罩四根定位柱插入压块盲孔后点胶，中心孔让杆身通过但挡住扁球头。
2. 将左右新版 `clamp_body_half_user` 与 `clamp_body_half_opponent` 的大平面定位到夹体安装位置；先在对手侧半体外侧六角窝装入 8 枚 M5 螺母，再沿 y 合拢两半，从操作者侧拧入 8 枚 M5 螺钉，确认左下角连接孔向外侧移动后的净空、电子腔边界前新增连接点以及空腔边界处的 boss 柱/十字肋完全贴合；实心夹臂里的连接点不应出现外凸 boss。电子件在两半分开时从 `y=0` 分型面放入右侧大电子仓，主控板由底部 standoff 支撑，电池放在主控板器件层上方的第二层托位，确认电池不被支柱压穿，再检查一体化斜底、9 mm 侧壁和约 15.5 mm 上部承力层没有干涉；`x+` 外侧墙和 boss 不切除，不安装下方底盖、连续垫或旧 UI 压框。之后从 x+ 开放端把对应 `post_clamp_carrier` 的绿色整体底座沿 x 推入让位腔，确认两枚 M4 穿过灰色 `Ø4.4 mm` 孔和绿色 `Ø4 mm` 孔，再安装钢珠/弹簧/压盖。黄色立柱在 `z=16 mm` 与绿色底座相接，主体继续到 `z=260.5 mm`；网布/卡网夹功能区止于 `z=168.5 mm`。不要把旧的整件夹体或直接共面座立柱混进来。
3. 不再安装立柱上下分件、接缝套筒或独立上段；球头承座已经与整根立柱顶端一体打印。
4. 先把真实网布端部从球台中心侧穿过立柱的全高 `3 mm` 过道；网布端边止在立柱外侧面。再把 `net_clamp_clip` 从桌外侧沿 x 滑入，确认两片 jaw 夹住网布、外侧横梁位于立柱外面，一体扣舌让内嵌止挡越过并在终点咯噔落位。拆网时按开对应 jaw 使扣舌让开，反向滑出 U 夹，最后抽出网布；不装穿钉。
5. 在网端靠近立柱的位置装 PVDF 座/薄膜/压片；每侧传感器与立柱保留 `18 mm` 横向净距。不得把 PVDF 座当作网架承力件。
6. 依次安装 M6 十路主体、前后盖、底盖、连续压合垫、出线环、线束和采购球头；闭合盖板后检查连续配合面、定位唇和胶条是否严丝合缝，无明显贯通缝或翘边。之后才进行 M6 光轴、球头微调、供电和输出联调。

## 电子与外购件边界

梯形夹体内部是电子腔，不把器件塞进桌面受力区：主控端预留 ESP32 母板、UI 子板、屏幕窗口、START/MODE 按钮、指示灯、扬声器/蜂鸣器、USB-C 和电池；另一端预留发射电源子板及内置 1S 电池，并保留外接电源接口。PCB、端子/压接线束和电池以 `hardware/electronics/` 的 KiCad/Atopile/装配包为准，先按 fit report 和实物器件复核，再封盖。

M6 器件采用左右各十路的实际安装包络，光学轴向球台中心；采购球头、M6 SKU、线束和端子必须按到货尺寸/后缀复核。现有 CAD/网格验证不能代替铜箔生产释放、电气波形、实物装配或承力试验。

## 历史入口

`net_rail*`、`post_joint_sleeve`、`post_joint_key`、`net_clamp_rod` 只保留为旧版本兼容诊断入口，不能复制到正式打印包；当前网顶没有轨道，当前卡网件是 `net_clamp_clip`。
