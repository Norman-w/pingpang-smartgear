# 内置式球网支架首样打印与装配清单 v0.7-split-c-scheme

本清单以 [`net_stand.scad`](net_stand.scad) 为唯一机械参数源。当前主线是不打孔的桌下 C 形夹：PETG 粗牙螺杆完全位于台面下方，采用 `12 mm` 大径、`9.6 mm` 芯径和 `4 mm` 螺距，牙根宽约 `2 mm`、凹槽宽约 `2 mm`、外侧锥尖约 `0.4 mm`，顶部扁球头向上进入独立台底压块；压块用贯穿球头窝和下方粗牙防脱压环把球头完整包住，压环无胶旋入。配套 PETG 粗牙固定螺母从下臂上侧六角沉孔装入，旋钮内再捕获两枚 `AF16 × 6 mm` 粗牙对锁螺母。夹体底面不再开一个相反方向的螺母窝，也不把旧的 M8×1.25 细牙钢件混入当前打印主线。当前 CAD 按 `12…40 mm` 台面厚度冻结，默认 `25 mm`，超过 `40 mm` 必须重新设计夹体和承力壁。夹体分成“y=0 分型的操作者侧/对手侧两个 C 形半体”和“带绿色整体底座的斜立柱下段/顶部 30 mm 上段”；两个半体沿 ±y 合拢，用 9 套横向 M5 连接，两侧 y=0 分型内侧浅凹槽底对应阳刻 `1…9` 编号，便于分开后按号装配；字顶低于分型基准，不出现在外壁且不影响分型贴合；左下角连接孔向外侧移动，电子仓左下角和右下斜加强边沿各增加连接点，其中 6、7 号连接点及其 boss/孔位整体沿 Z− 下移 `9 mm`；前半圆头沉孔朝外、后半六角螺母窝朝外。只有贴着电子仓空腔面的连接点增加 boss/十字肋，实心夹臂里的连接点只保留通孔/沉孔。电子仓位于 C 夹右侧桥体的整段内缩区域，约 `117×40 mm`，上方保留约 `15.5 mm` 承力层、两侧各 `9 mm` 承力壁和一体化 `4 mm` 斜底；两半分开后从 `y=0` 分型面装入 PCB/电池，主控板按 KiCad Edge.Cuts 板形相减出插入让位。x− 端是一件截面为 `[` 的打印端部夹件，x+ 端是一件镜像的 `]` 端部夹件；每件夹件由留在实心端墙内的整条竖根、下承托唇和上限位唇组成，合拢后形成 `[——主板——]`，不设置主板 boss/定位柱，也不要求螺丝刀进入闭合腔体；电池放在主控板器件层上方的第二层托位，避开端部夹件，不再压穿电池；`x+` 外侧墙和 M5 boss 保持完整，不再使用下方底盖和连续垫。绿色底座从 x+ 开放端推入灰色让位腔，黄色立柱在 `z=16 mm` 与底座相接，分型面为 `z=230.5 mm`，上段继续到 `z=260.5 mm`。绿色底座保留两枚 `Ø4 mm` 通孔、中央 `Ø6×2 mm` 底坑和两侧 `15 mm` 外伸；灰色夹体对应两枚 `Ø4.4 mm` 连接孔与下方钢珠定位孔。网布/圆柱插杆功能区仍为 `z=16…168.5 mm`，不使用 T 槽、公轨或第二个独立滑靴。

这里的“水密”只表示盒盖装好后应严丝合缝、没有明显贯通缝、错台或翘边；不代表 IP 等级、防水认证或实物密封测试已经完成。

## 结构主线

- 网顶不设置轨道、承载条、拼接片或承托座。网布总宽基准为 `1830 mm`，网顶高度为 `152.5 mm`。
- 真实网布侧边空心布套先套在 `Ø10 mm` 圆柱插杆上，再沿原门洞轴线从 x 侧一起推入每根立柱下段的侧开接收腔；门洞横向宽度仍为历史 `15.2 mm`，装上段后由上段封住插入口。
- 球网侧边采用一根独立 `Ø10 mm × 152.5 mm` 圆柱插杆。先把圆柱穿过网布空心边套，再从下段立柱的原门洞方向沿 x 推入接收腔，最后装上上段将插杆捕获；不使用外侧矩形 U 夹、长方形卡条或 keeper。
- 斜立柱由下段和顶部下 `30 mm` 的上段组成，绿色整体底座并入下段；固定 C 形主体沿 `y=0` 分成操作者侧 y- 半体和对手侧 y+ 半体。先把后半的 9 枚 M5 六角螺母装入防转窝，再让两个半体沿 y 合拢，从操作者侧拧入 9 枚 M5 圆头螺钉；两侧 y=0 分型内侧浅凹槽底对应阳刻 `1…9`，按编号定位每个连接位，字顶低于分型基准；左下角连接孔已向外侧移动，电子仓左下角和右下斜加强边沿各增加连接点；分型总间隙 `0.20 mm`。只有碰到电子仓空腔面的连接点才有 printed boss/十字肋，完全位于实心夹臂里的连接点只保留通孔/沉孔，避免外壳凸起。合拢后从 x+ 开放端把绿色底座沿 x 推入灰色让位腔，确认两枚 M4 穿过灰色 `Ø4.4 mm` 孔和绿色 `Ø4 mm` 孔，再让下方 `4 mm` 钢珠进入绿色 `Ø6×2 mm` 底坑。黄色立柱在 `z=16 mm` 与底座相接，分型面为 `z=230.5 mm`，上段延伸到 `z=260.5 mm`；四枚普通盘头或低矮圆头 M3×40 自攻钉只从上段 `Ø3.4 mm` 通孔锁入下段 `Ø2.4 mm×10 mm` 盲孔，不用 90° 沉头或台阶肩螺钉。不存在 T 槽、公轨、第二个滑靴或旧版直接共面座；图示间隙只用于打印装配，不是实体强度或防水承诺。
- 网布接近左右网架末端的位置各放一个 PVDF 振动传感器座，传感器座与立柱保留 `18 mm` 横向净距。

## 现行独立打印件：41 件

运行 `python3 export_net_stand_printables.py --clean` 实际导出并由 `test_export_net_stand_printables.py` 锁定为 `41/41`：

| 组别 | 数量 | 正式 `PART` |
| --- | ---: | --- |
| 立柱分件/分型夹体 | 8 | `post_clamp_carrier_lower` ×2、`post_clamp_carrier_upper` ×2、`clamp_body_half_user` ×2、`clamp_body_half_opponent` ×2 |
| 桌下电子腔 | 2 | 电子仓由 C 夹本体一体内缩形成；左右各一件 y+ 外侧齐平 UI 填平固定板（面板、72×42 mm 腔内固定法兰、捕获环和 8 个孔融合为一件）进入正式打印矩阵，旧的底盖、连续垫和 UI boss 入口已移除 |
| M6 壳体 | 12 | `m6_detector_body`、前盖、后盖、底盖、底盖垫、出线环各左右 1 件 |
| 卡网/夹紧件 | 14 | `net_clamp_rod` ×2、`clamp_pressure_pad` ×2、`clamp_pressure_pad_guard` ×2、`clamp_printed_screw` ×2、`clamp_body_nut` ×2、`clamp_knob` ×2、`clamp_knob_nut` ×2（每个 STL 含一侧两枚螺母） |
| PVDF/历史工具 | 5 | `sensor_mount_body` ×2、`sensor_clamp_lip` ×2、`calibration_gauge` ×1 |

逐文件的 `PART`、左右侧、材料、包围盒、体积和封闭拓扑摘要见 [`exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json`](exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json)。

正式清单不包含球台、网布、PVDF 薄膜、ESP32/子板 PCB、电池、M6 光电器件、采购球头、M4/M5/M3 金属连接件和线束；当前夹紧螺杆及其两类螺母由 PETG 打印。`post_joint_exploded`、`clamp_slide_exploded`、各类 `fit_section`/`fit_probe` 是检查用组合预览，不是打印件。

## 打印姿态与 256 mm 盘

`net_clamp_rod` 是一根连续圆柱插杆，导出 STL 时圆柱轴线沿 X 平放，包围盒约 `10 × 10 × 152.5 mm`；装配时圆柱轴线沿 Z，穿过球网侧边空心布套后沿原门洞方向从 x 侧推入下段侧开接收腔，装上上段后被捕获。斜立柱下段包围盒约 `58.7 × 58.0 × 244.5 mm`（含绿色底座和公键），上段约 `28 × 38 × 30 mm`；上段四个 `Ø3.4 mm` 通孔与下段四个 `Ø2.4 mm × 10 mm` 盲孔对应，四枚 M3×40 只连接立柱上下两段；其它零件不由脚本缩放或裁切。

默认 `256 × 256 × 256 mm` 拼盘已经生成：[`print-platter-256/manifest.json`](exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/print-platter-256/manifest.json)。当前目标为 `7` 盘、`41` 件已排版、`0` 件超尺寸：两件下段黄绿连接件采用 `rx=0°、ry=51°、rz=45°` 三轴斜放姿态，各占一张 PETG 盘；两件上段按分型面平放；C 夹半体把各自 y 外侧大平面贴床，端部 `[ / ]` 夹件沿 y 方向逐层生成，圆柱插杆平放，其余零件按实际包络分到多张 PETG 盘，TPU/柔性单独一盘。这个结果证明保守包络排版和 STL 几何，不等于已生成 G-code、已验证切片支撑/首层或已完成实物打印。

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
openscad -D 'PART="post_clamp_carrier_lower"' -D 'SIDE=1' -o right-post-clamp-carrier-lower.stl net_stand.scad
openscad -D 'PART="post_clamp_carrier_upper"' -D 'SIDE=1' -o right-post-clamp-carrier-upper.stl net_stand.scad
openscad -D 'PART="net_clamp_rod"' -D 'SIDE=1' -o right-net-clamp-rod.stl net_stand.scad
openscad -D 'PART="clamp_slide_fit_section"' -D 'SIDE=1' -o clamp-slide-section.png --render net_stand.scad
openscad -D 'PART="net_clamp_fit_section"' -D 'SIDE=1' -o net-clamp-section.png --render net_stand.scad
```

## X1C 3MF 的对象边界

旧的整件 C 夹/直接共面座 3MF 已作废，不能与当前分型 C 方案接口混用。当前可直接打开的 X1C/PETG 文件位于 `exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme-3mf/`。

补打这两个独立件请在 `hardware/cad` 下运行：

```text
python3 build_net_clamp_bambu_package.py --side both
```

输出目录为 `exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme-3mf/`。左右两个 `*-split-c-scheme-X1C-PETG.3mf` 各自都包含 `clamp-body-half-user`、`clamp-body-half-opponent`、`post-clamp-carrier-lower`、`post-clamp-carrier-upper`、`clamp-electronics-ui-panel-mount` 和 `net-clamp-rod` 六个完整对象；这是不含 G-code 的可编辑工程，需在 Bambu Studio 中分盘排版后再切片。当前正式清单只有这个独立圆柱插杆，旧矩形卡条、外侧 U 夹和 keeper 均不再属于结构。

## 装配顺序

主控板已经删除底部 boss、standoff 和主板螺钉；正式固定件是 x−/x+ 两端各一件、随 C 夹半体一体打印的 `[` / `]` 端部夹件。打印 C 夹半体时把 y 外侧大平面（x-z 面）贴床，让端部夹件的下承托唇、上限位唇沿 y 方向逐层生成，不把 15 mm 唇做成 z 方向悬空桥；首样仍需在切片器中复核首层和壁数。

1. 先用目标球台厚度样块（本版适用 `12…40 mm`，默认 `25 mm`），把 `clamp_pressure_pad_guard`（球头螺纹防脱压环）从螺杆尾部套到 12 mm 杆身上；再把 `clamp_printed_screw` 的扁球头从压块底部送入 Ø16.7 内腔，确认球头四周约 0.6 mm 径向余量、顶部约 0.6 mm 轴向余量；最后将压环对准压块底部 Ø30 粗牙 boss 旋入到底。压环下缘 Ø13.2 孔让杆身通过但挡住球头，上口 Ø14.7 向内腔扩口，球头在里面可以运动；整个防脱结构不点胶、不装热熔螺母、不用松散销钉。然后安装左右 `post_clamp_carrier_lower` 和 `post_clamp_carrier_upper`、固定上夹板胶皮、`clamp_body_nut`、下臂上侧捕获螺母和旋钮内两枚 `clamp_knob_nut` 粗牙对锁螺母；确认不打孔、不碰台面、不干涉压块/螺杆工作区。粗牙件必须成套使用，不与 M8×1.25 金属螺母混配；2 mm 牙根/2 mm 凹槽加 0.4 mm 锥尖保证打印后牙根有连续实体，外形不是平顶环带。
2. 将左右新版 `clamp_body_half_user` 与 `clamp_body_half_opponent` 的大平面定位到夹体安装位置；先在对手侧半体外侧六角窝装入 9 枚 M5 螺母，再沿 y 合拢两半，从操作者侧拧入 9 枚 M5 螺钉，确认左下角连接孔向外侧移动后的净空、电子仓左下角与右下斜加强边沿新增连接点（其中 6、7 号已整体沿 Z− 下移 `9 mm`）以及空腔边界处的 boss 柱/十字肋完全贴合；实心夹臂里的连接点不应出现外凸 boss。电子件安装时保持主控板元件面朝 +z，不翻板：两半分开后先把主控板平放到任一半体的下承托唇上，让 x−/x+ 两端同时落入 `[` / `]` 夹件；确认两件夹件的上下唇与板厚间有设计余量，且整条竖根都在端墙内；再将另一半对准分型面并合拢，形成 `[——主板——]`，共同完成承托和防上浮，整个过程不需要把螺丝刀伸进电子腔。电池放在主控板器件层上方的第二层托位，确认电池与端部夹件和板上器件保持净空，再检查一体化斜底、9 mm 侧壁和约 15.5 mm 上部承力层没有干涉；`x+` 外侧墙和 boss 不切除，不安装下方底盖或连续垫。将一体式 `clamp_electronics_ui_panel_mount` 从电子腔 y- 侧穿入侧窗，确认外表面与 C 夹壁齐平，腔内侧 72×42 mm 固定法兰和捕获环落在墙内；使用 8 枚 2 mm 蘑菇头自攻钉从腔内穿过一体件上的 Ø2.3 mm 通孔，直接进入 C 夹实心内壁 Ø1.6 mm 盲导孔，捕获环已与面板周边融合 `0.4 mm`，孔边至少保留 `1.2 mm` 实体边，外壁底厚 `0.7 mm`；不生成正向 UI boss 柱，外侧不出现螺钉头或沉孔。确认屏幕窗口、START/MODE 腔内导向柱、两个 0603 LED 直孔（可加透明导光柱）、扬声器声学窗和由当前 KiCad USB-C 仅外壳/屏蔽罩轮廓生成的 0.25 mm 装配通道（侧面焊接脚、接触脚和安装脚不参与外侧开口轮廓）分别与 UI 子板器件对齐；外侧再挖一个以 KiCad 金属壳体前沿为止点的圆角矩形碗槽，外围保留 `0.60 mm` 连续环形打印底，中心 KiCad-fit 通孔贯穿并由 Type-C 金属壳体负责显示/插入；再从 x+ 开放端把对应 `post_clamp_carrier_lower` 的绿色整体底座沿 x 推入让位腔，确认两枚 M4 穿过灰色 `Ø4.4 mm` 孔和绿色 `Ø4 mm` 孔，再安装钢珠/弹簧/压盖。黄色立柱在 `z=16 mm` 与绿色底座相接，分型面为 `z=230.5 mm`，上段继续到 `z=260.5 mm`；网布/圆柱插杆功能区止于 `z=168.5 mm`。不要把旧的整件夹体或直接共面座立柱混进来。
3. 将下段 `post_clamp_carrier_lower` 从 x+ 开放端推入 C 夹让位腔，再把上段 `post_clamp_carrier_upper` 沿 z 对准 `z=230.5 mm` 分型面滑下；确认两条公母键贴合，四枚 M3×40 自攻钉从上段 Ø3.4 mm 通孔进入下段 Ø2.4 mm×10 mm 盲孔。顶部 M8 支撑孔随上段闭合，不使用接缝套筒。
4. 先把球网侧边的空心布套完整套到 `Ø10 mm × 152.5 mm` 圆柱插杆上；再把插杆与网布一起沿原门洞轴线从 x 侧推入下段侧开接收腔，确认杆底坐在 `z=16 mm`、网布覆盖 `z=16…168.5 mm`，最后装上 `post_clamp_carrier_upper` 封住插入口。拆卸时先拆上段，再沿相反方向抽出圆杆和网布。
5. 在网端靠近立柱的位置装 PVDF 座/薄膜/压片；每侧传感器与立柱保留 `18 mm` 横向净距。不得把 PVDF 座当作网架承力件。
6. 依次安装 M6 十路主体、前后盖、底盖、连续压合垫、出线环、线束和采购球头；闭合盖板后检查连续配合面、定位唇和胶条是否严丝合缝，无明显贯通缝或翘边。之后才进行 M6 光轴、球头微调、供电和输出联调。

## 电子与外购件边界

梯形夹体内部是电子腔，不把器件塞进桌面受力区：主控端预留 ESP32 母板、UI 子板、屏幕窗口、START/MODE 按钮、指示灯、扬声器/蜂鸣器、USB-C 和电池；另一端预留发射电源子板及内置 1S 电池，并保留外接电源接口。PCB、端子/压接线束和电池以 `hardware/electronics/` 的 KiCad/Atopile/装配包为准，先按 fit report 和实物器件复核，再封盖。

M6 器件采用左右各十路的实际安装包络，光学轴向球台中心；采购球头、M6 SKU、线束和端子必须按到货尺寸/后缀复核。现有 CAD/网格验证不能代替铜箔生产释放、电气波形、实物装配或承力试验。

## 历史入口

`net_rail*`、`post_joint_sleeve`、`post_joint_key` 等名称只保留为历史/兼容诊断入口，不能复制到正式打印包；当前网顶没有轨道，当前网端件是 `net_clamp_rod`，四枚 M3×40 属于立柱上下分型连接。
