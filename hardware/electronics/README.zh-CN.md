# 电气首样入口

- [`system-packaging-v0.2.zh-CN.md`](system-packaging-v0.2.zh-CN.md)：母板、接收载板、发射端内置电源、UI 子板、端子化线束和梯形腔/盖板装配合同。
- [`esp32-control-v0.1/`](esp32-control-v0.1/)：ESP32-S3 主控、USB-C、受保护 1S 电池、电源树、PVDF ADC 辅助口和 M6 载板接口；目录内有原生 KiCad PCB、项目、主控原理图和板级 3D 导出。
- [`daughter-boards-v0.2/`](daughter-boards-v0.2/)：80×32 mm 十路接收载板、68×32 mm 发射端内置电源子板、58×28 mm UI 子板及其生成器/BOM、KiCad 项目和 3D 导出。
- [`atopile/`](atopile/)：可由 `ato validate`/`ato build` 检查的系统级 Atopile 接口合同；它记录板间连接和通道数，不冒充已完成铜箔布线的 PCB。
- [`validate_system_fit.py`](validate_system_fit.py)：用 KiCad `pcbnew` 和 OpenSCAD 参数探针检查板框、安装基准、腔体余量和 M6 竖放包络。
- [`m6-capture-carrier-v0.1.zh-CN.md`](m6-capture-carrier-v0.1.zh-CN.md)：独立 STM32G031 + 光耦十路 M6 载板接口契约与放行门；当前已有 KiCad 首样载板，最终铜箔、原理图和实物波形仍 OPEN。
- [`m6-capture-carrier-first-article-bom-v0.1.zh-CN.md`](m6-capture-carrier-first-article-bom-v0.1.zh-CN.md)：载板首样器件拓扑与外部电源边界。
- [`bring-up-v0.1.zh-CN.md`](bring-up-v0.1.zh-CN.md)：上电、光栅、PVDF 和健康快照的现场接板顺序。

主控板与 M6 载板必须分板：10–30 V NPN 黑线不能直接进入 ESP32 GPIO，电池也不能替代传感器外部电源。所有现场线束以锁扣对插、可插拔螺钉端子或压接端子交接，不留裸焊盘飞线。

这里的“水密”只代表盒盖压合后严丝合缝、无明显开缝/错台/松动；不代表 IP 等级，也不把首样文档当作防水认证。真实连接器、线径、电池和升压电流仍须在首样中冻结。

## 当前线路板尺寸原则

发射头与接收头之间的 `20 mm` 光学间距只属于 M6 光学头/机械壳体；十路线束在进入子板前先汇线，因此不把光学间距乘到 PCB 长度上。当前候选尺寸为：母板 `86×32 mm`、接收载板 `80×32 mm`、发射电源板 `68×32 mm`、UI 板 `58×28 mm`。四块板均为 2 层，按所在空腔和器件/走线可制造性取紧凑尺寸，不追求无余量的小板。

板上对插线束的候选接口统一为 `MX1.25` 节距；当前生成器使用仓库内可见的 JST-GH `1.25 mm` 锁扣模型作为外观/包络代理，准确采购厂家和料号仍需拿到实物或数据手册后冻结。原理图中的 `Conn_01xNN` 只是逻辑符号的引脚表示，不代表使用 2.54 mm 物理排针；物理 PCB 焊盘以 1.25 mm 候选为准。

## 当前可交付文件

当前已生成 4 个原生 KiCad `.kicad_pcb/.kicad_pro` 项目、ESP32 主控原生 `.kicad_sch`、板级 STL/STEP 和 Atopile `.ato` 接口合同。统一自证报告见 [`fit-report-v0.2.md`](fit-report-v0.2.md)；其中机械/装配与干涉为 `PASS`，电气生产释放仍因未布线/未实测保持 `OPEN`。`.ato` 与 KiCad 的职责刻意分开，避免把接口合同误当作 Gerber 生产数据。
