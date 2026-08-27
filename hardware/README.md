# 硬件工程

这里放置内置式球网支架、替换球网、左右各十路 M6 直角对射光电器件的 PETG 长条主体、
带水平 z 轴偏航、y 轴俯仰、x 轴滚转微调的光学基座、参考线、PVDF 网顶夹片、线束和装配资料。

当前光学机械主线见 [`../docs/m6-optical-array-design-v0.1.zh-CN.md`](../docs/m6-optical-array-design-v0.1.zh-CN.md)。
旧版连续光栅、STG-120ML 光纤头和相关托架仍保留在 CAD/文档中，用于回溯和兼容诊断，
不再代表当前首样采购主线。

## 当前硬件拆分

- `cad/`：当前内置式球网支架、M6 十路 PETG 长条主体/前后盖/底盖的参数化 OpenSCAD、左右镜像件和装配预览；
- `electronics/`：PVDF AFE、M6 NPN 对射传感器隔离前端和板级接口边界；
- [`electronics/m6-npn-interface-v0.1.zh-CN.md`](electronics/m6-npn-interface-v0.1.zh-CN.md)：10 路 M6 NPN 隔离输入参考电路、计算边界、BOM 和上电检查；
- [`electronics/m6-capture-carrier-v0.1.zh-CN.md`](electronics/m6-capture-carrier-v0.1.zh-CN.md)：针对 SmartPaddle GPIO 冲突的独立边沿采集载板、SPI 引脚候选、CRC 帧协议和 1–10 ms 放行门；
- [`electronics/m6-capture-carrier-mcu-selection-v0.1.zh-CN.md`](electronics/m6-capture-carrier-mcu-selection-v0.1.zh-CN.md)：载板 MCU 候选、18/22 根 GPIO 资源预算、封装与时序放行门；
- [`electronics/m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md`](electronics/m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md)：当前 STM32G031K8U6/UFQFPN32 工程候选 pin map，仍需最小原型实测；
- [`electronics/m6-capture-carrier-first-article-bom-v0.1.zh-CN.md`](electronics/m6-capture-carrier-first-article-bom-v0.1.zh-CN.md)：载板首样连接器、10 路隔离、测试点、画板规则和逐级上电/波形放行顺序；
- [`first-article-bom.zh-CN.md`](first-article-bom.zh-CN.md)：首样采购数量、免打孔装配顺序和未冻结的实物边界；
- [`../docs/m6-first-article-release-v0.1.zh-CN.md`](../docs/m6-first-article-release-v0.1.zh-CN.md)：M6 铝件 14 件清单、名义连接件、三轴装配顺序和首样退回条件；

当前打印件由 `cad/net_stand.scad` 这一份参数源统一导出：它包含左右两段式立柱、下段与传统桌下 C 形夹一体的 `lower_stand_segment`、接缝外套筒/内芯、固定上夹板与桌面之间的可替换保护垫、台底可动压块、网顶承载条、光学模块安装位和 PVDF 夹片安装位。打印数量、标准件和非打印装配边界见 [`cad/print-manifest.zh-CN.md`](cad/print-manifest.zh-CN.md)。

首版按 `1525 mm` 球台宽度、`25 mm` 台面厚度、ITTF 网柱外边界距台边 `152.5 mm` 和 `152.5 mm` 网顶高度起模；因此网顶承载条/网布名义总宽为 `1830 mm`，而不是几乎等于球台宽度。当前支架免打孔，固定 C 形夹体跨过台边，上夹板与桌面之间放置可替换 TPU/硅胶保护垫，保留桌面夹持开口、台底压块和螺杆区域，开口外侧下部改为沿 y 全深的实心渐变承力段，靠台侧厚 `40 mm`、外侧厚 `8 mm` 并形成斜底；固定下臂捕获一枚 M8 螺母；每侧夹紧螺杆下端由两枚预先对锁的 M8 螺母和打印旋钮刚性带动，圆头 M8×1.25 螺杆在台面下方顶起独立可动压块夹紧台底，当前相对原包络加长 `12 mm`，不依赖 PETG 内螺纹或不明确的双固定螺纹；光学导轨位于台边与立柱内缘之间的开放空间，光轴覆盖球台边缘。实心渐变支撑的 PETG 层向、夹紧力、网布张力、加长螺杆行程和真实网夹兼容范围必须以首样实物记录为准。当前不包含相机作为本体测量链路；外部视频设备只用于后续时间戳回放复核。原 `cad/net_post_x_clamp.scad` 是保留的外挂 X 夹具历史方案，不是当前主线。
