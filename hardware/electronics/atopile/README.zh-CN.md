# Atopile 系统接口合同

这里的 [`pingpang_smartgear.ato`](pingpang_smartgear.ato) 是系统级 Atopile 接口合同，明确母板、十路 M6 接收载板、发射端内置电源、UI 子板之间的可插拔信号和通道数量。

当前机械/接口候选为：母板 `86×32 mm`、接收载板 `80×32 mm`、发射电源板 `68×32 mm`、UI 板 `58×28 mm`，均为两层板；板级线束连接器物理节距统一为 MX1.25（1.25 mm）。M6 光学头的 20 mm 阵列间距只属于光学头和线束，不进入这个板间接口合同。

它与同目录上一级的原生 KiCad 文件分工如下：

- Atopile `.ato`：板间接口、端子化线束和 10 路通道数量的可验证合同；
- `../esp32-control-v0.1/` 与 `../daughter-boards-v0.2/`：实际 KiCad `.kicad_pcb/.kicad_pro` 首样板和 3D 模型；
- `../generate_kicad_schematic.py` / `../esp32-control-v0.1/esp32-control-v0.1.kicad_sch`：原生 KiCad 主控原理图；
- `../../cad/net_stand.scad`：壳体、boss、盖板、过线和板件的统一机械基准。

验证入口：

```text
ato validate hardware/electronics/atopile/pingpang_smartgear.ato
ato build hardware/electronics/atopile
```

Atopile 合同通过不等于 PCB 已完成布线、ERC/DRC 已关闭或电源/M6 波形已实测；这些状态以 [`../fit-report-v0.2.md`](../fit-report-v0.2.md) 的电气放行边界为准。
