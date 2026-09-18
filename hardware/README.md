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

网顶不设置轨道。网布从球台中心侧进入两侧立柱的连续 `3 mm` 过道，端部止到立柱外表面；整高 U 形卡网夹从桌外侧沿 `x+ → x−` 推入，夹爪夹住网布。网端附近左右各一个 PVDF 振动传感器，与网架保留 `18 mm` 横向净距。

固定 `clamp_body_segment` 与整根 `post_clamp_carrier` 分体打印；固定夹主体除网/卡夹功能开口外保持实心。立柱底面在 C 夹黄灰交界 `z=16 mm` 共面，一体实心延伸到 `z=372.5 mm`（总高 `356.5 mm`），不向下插入 C 形座；网布/卡夹功能区仍只到 `z=168.5 mm`，从承托面向上 `30 mm`（至 `z=46 mm`）做 `35×58 mm → 28×38 mm` 连续实心渐变，之后统一为顶端 `28×38 mm` 截面。网布仍从球台中心侧穿过连续 `3 mm` 过道，U 形卡夹从桌外侧沿 `x+ → x−` 推入；网布张力和绳的拉力负责把卡夹压住，立柱内嵌单一被动止挡只防向外拔出，按开夹爪即可解锁。立柱本体和网布过道没有上下接缝，固定网柱顶端不再设置直连 M8 孔。

盒盖、压合边和接口以“装配后严丝合缝、无明显贯穿缝”为目标；这里不宣称防水等级。真实网布、螺纹、张力、线缆弯曲和夹体耐久必须用首样实测。

## 打印状态

当前正式机械包以 [`cad/print-manifest.zh-CN.md`](cad/print-manifest.zh-CN.md) 和 [`cad/exports/desktop-clamp-one-side-x1c-v0.4-top-load/manifest.json`](cad/exports/desktop-clamp-one-side-x1c-v0.4-top-load/manifest.json) 为准：`37` 个 STL。256 mm 打印床拼盘见 [`cad/exports/desktop-clamp-one-side-x1c-v0.4-top-load/print-platter-256/manifest.json`](cad/exports/desktop-clamp-one-side-x1c-v0.4-top-load/print-platter-256/manifest.json)：`6` 张板、`37` 个已排版、`0` 个超尺寸件；两件整根立柱/载体使用实际三轴斜放。旧分体立柱、套筒、内芯和圆柱卡网件不再属于当前清单。

这是 CAD 包络/封闭 STL/排版证据，不是已切片、已生成 G-code 或已完成实物打印的证明。
