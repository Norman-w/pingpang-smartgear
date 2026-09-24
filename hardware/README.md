# 硬件工程

这里放置内置式球网支架、两侧 M6 发射/接收阵列、网端 PVDF 传感器、ESP32 主控、子板、电池和装配资料。

新增的左侧裸激光可调小夹座见[结构与装配说明](../docs/laser-micro-mount-v0.1.zh-CN.md)。单颗特写、原位调节演示与整排共用 SCAD 导出的模型，工具从编号孔进入，邻居和后盖保持固定。输出位于 `cad/exports/laser-micro-mount-v0.1/`；加大前腔的新前盖、新承载条、后盖、底盖与底部柔性垫成套使用，原 M6 电气资料仅供接口参考。

右侧也已同步[接收端外壳](../docs/receiver-mount-v0.1.zh-CN.md)，输出为 `cad/exports/receiver-mount-v0.1/`；内部元件仍为原M6接口参考，待确认接收器后适配固定座。

## 当前硬件拆分

- [`cad/`](cad/)：参数化 OpenSCAD 机械源、完整装配/爆炸/剖切预览、正式 STL 导出和 256 mm 打印拼盘；
- [`electronics/`](electronics/)：ESP32-S3 主控板、M6 接收载板、发射端内置电源子板、UI 子板、Atopile 接口合同、3D 板模型和统一壳内干涉报告；
- [`first-article-bom.zh-CN.md`](first-article-bom.zh-CN.md)：首样采购和实物放行边界；
- [`../docs/m6-optical-array-design-v0.1.zh-CN.md`](../docs/m6-optical-array-design-v0.1.zh-CN.md)：M6 阵列和安装基准。

电子系统的机械—电气合同见 [`electronics/system-packaging-v0.2.zh-CN.md`](electronics/system-packaging-v0.2.zh-CN.md)。其中已给出母板、接收/发射/UI 子板、端子化线束、电池仓、USB-C、按钮、屏幕预留、扬声器/蜂鸣器、指示灯和梯形腔的统一坐标。主控与 1S 电源首样板见 [`electronics/esp32-control-v0.1/`](electronics/esp32-control-v0.1/)，M6 接收载板和发射端电源子板见 [`electronics/daughter-boards-v0.2/`](electronics/daughter-boards-v0.2/)。

## 当前机械结构

网顶不设置轨道。网布侧边空心布套先套到 `Ø10 mm × 152.5 mm` 圆柱插杆，再把这套组件从球台中心侧穿过立柱下段的连续 `3 mm` 网布过道，沿原门洞轴线从 x 侧推入下段的侧开接收腔；安装上段后封住插入口。斜立柱在顶部下 `30 mm` 分成下段和可替换上段，两段用公母定位键和四枚 M3×40 自攻钉连接。网端附近左右各一个 PVDF 振动传感器，与网架保留 `18 mm` 横向净距。

C 形夹按 y=0 分型为 `clamp_body_half_user` 与 `clamp_body_half_opponent` 两半，斜立柱和绿色载体则由 `post_clamp_carrier_lower`、`post_clamp_carrier_upper` 两件打印；固定夹半体除网布 `3 mm` 过道和侧开接收腔外保持实心。立柱底面在 C 夹黄灰交界 `z=16 mm` 共面，分型位于顶部下 `30 mm`，上段带公母键和四枚 M3×40 连接孔；网布/圆柱插杆功能区仍只到 `z=168.5 mm`。网端装配不使用矩形卡夹、keeper 或竖直盲孔：先把边套套在 Ø10 圆柱上，再沿 x 方向推入下段侧开接收腔，最后合上上段。上段保留顶部 M8 支撑孔，四枚立柱连接螺丝只属于立柱上下段。

盒盖、压合边和接口以“装配后严丝合缝、无明显贯穿缝”为目标；这里不宣称防水等级。真实网布、螺纹、张力、线缆弯曲和夹体耐久必须用首样实测。

## 打印状态

当前正式机械包以 [`cad/print-manifest.zh-CN.md`](cad/print-manifest.zh-CN.md) 和 [`cad/exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json`](cad/exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/manifest.json) 为准：`41` 个 STL。256 mm 打印床拼盘见 [`cad/exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/print-platter-256/manifest.json`](cad/exports/desktop-clamp-one-side-x1c-v0.7-split-c-scheme/print-platter-256/manifest.json)：`7` 张板、`41` 个已排版、`0` 个超尺寸件；斜立柱下段/绿色载体使用实际三轴斜放，上段按分型面平放姿态打印。旧整高 C 夹、电子腔底盖/连续垫、网夹分体、套筒和内芯不再属于当前清单；旧矩形卡条与 keeper 已移除，当前为独立 Ø10 mm 圆柱插杆和下段侧开接收腔。

立柱上下段连接螺丝当前按普通盘头或低矮圆头 `M3×40` 自攻钉采购；结构没有 90° 沉头窝，也不使用台阶肩螺丝。这是 CAD 包络/封闭 STL/排版证据，不是已切片、已生成 G-code 或已完成实物打印的证明。
