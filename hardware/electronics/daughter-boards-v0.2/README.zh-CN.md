# M6 / 发射电源 / UI 子板首样 v0.2

这些是母板之外的原生 KiCad `.kicad_pcb/.kicad_pro` 首样项目，另有 KiCad 导出的 STL/STEP。它们用于验证装配包络、端子数量和线束方向；板框和板侧连接器模型是真实文件，但尚未完成铜箔布线，因此还不是生产板。UI 的按键、0603 LED 和 USB-C 直接器件保留 KiCad 封装及其 3D 模型，并随 UI 板 STL 导出；屏幕、扬声器和电池等线束件才由 SCAD 装配层挂载。

## 板级分工

| 文件 | 外形 | 用途 | 现场接口 |
| --- | ---: | --- | --- |
| `m6-receiver-carrier-v0.2.kicad_pcb` | `80 × 32 mm` | 右侧接收端十路光耦/采集载板占位 | `J_RX00…J_RX09` 每路三芯，`J_HOST` 8 芯，`J_PWR` 2 芯，均为 MX1.25 候选 |
| `emitter-power-v0.2.kicad_pcb` | `68 × 32 mm` | 左侧发射端内置电源与升压占位 | `J_BAT/J_EXT` 2 芯，`J_TX_A/J_TX_B` 各 10 芯，均为 MX1.25 候选 |
| `ui-panel-v0.2.kicad_pcb` | `58 × 28 mm` | 盖面交互器件和面板线束 | `J_MOTHER` 12 芯、OLED 排线 4 芯、扬声器 5 芯、蜂鸣器 2 芯；START/MODE 贴片按键、2 个 0603 单色 LED、16 针 USB-C 为板上真实器件 |

三块子板均有对应原生 KiCad 原理图：[`m6-receiver-carrier-v0.2.kicad_sch`](m6-receiver-carrier-v0.2.kicad_sch)、[`emitter-power-v0.2.kicad_sch`](emitter-power-v0.2.kicad_sch)、[`ui-panel-v0.2.kicad_sch`](ui-panel-v0.2.kicad_sch)，审查 PDF 在 [`../output/pdf/`](../output/pdf/)；它们把 10 路 M6、内置电池/外接后备电源、UI/按钮/屏/音频/USB-C 的接口关系画成可打开的 KiCad 文件。

接收载板安装时长边对应 M6 壳体的竖直 z 方向，当前 `80 mm` 只作为壳体内的集中式采集板尺寸，不再把十个光学头的 `20 mm` 节距展开到 PCB 上；发射板和 UI 板对应梯形腔/盖板的独立安装面。发射板使用电池外侧的四个边缘支撑/压片，不把 boss 穿过电池宽面；主控母板的腔体余量和所有接口分工见 [`../system-packaging-v0.2.zh-CN.md`](../system-packaging-v0.2.zh-CN.md)。

对应的板级机械模型在 [`../3d/v0.2/`](../3d/v0.2/)：`m6-receiver-carrier-v0.2.{stl,step}`、`emitter-power-v0.2.{stl,step}`、`ui-panel-v0.2.{stl,step}`。统一装入壳体后的边界、boss、过线和干涉结果见 [`../fit-report-v0.2.md`](../fit-report-v0.2.md)。

## 接线约束

- M6 接收端：每路 `V / GND / SIG` 独立三芯锁扣线，编号与 `RX00…RX09` 一一对应。
- M6 发射端：每路 `TX_V / TX_GND` 两芯锁扣线，在线束侧汇线后分成 `J_TX_A`（TX00…TX04）和 `J_TX_B`（TX05…TX09）两个 10 芯 MX1.25 候选接口；发射器默认使用子板上的内置受保护 1S 电池和独立升压/限流模块。
- M6 接收端：每路 `BN / BU / BK` 三芯线仍按 `J_RX00…J_RX09` 独立编号；线束汇聚后在紧凑接收板上插接，接收板排列不代表光学头的物理间距。
- 本目录的接口候选统一锁定为 `MX1.25` 节距；JST-GH 模型只是当前仓库可用的 1.25 mm 锁扣外观代理，准确 MX1.25 厂家/料号、线径和额定电流仍需首样冻结，不使用 2.54 mm 物理连接器。
- `J_EXT` 是可插拔螺钉/压接端子形式的外部后备输入，不能与电池裸并联；最终反接、保险/TVS 和升压电流按实物模块冻结。
- UI 子板的母板、OLED、扬声器和蜂鸣器仍使用锁扣线束；START/MODE 使用库存 3.9×3.0×2.0 mm 两脚 SMD 按键，状态/电量使用 0603 单色 LED，USB-C 使用 KiCad 16 针库模型直接焊在 UI PCB 上，并与 y+ 封口板开口共用坐标。封口板在按键位置做浅凹面和腔内一体 1.6 mm 导向柱，直接顶到 KiCad 按键模型；LED 对准 2.2 mm 直孔；屏幕保留为排线连接的独立件，不把屏幕玻璃强行固定到 PCB，USB-C 端口配硅胶帽。按键、LED、USB-C 的机械实体只来自 KiCad 板模型；屏幕、扬声器和电池等非贴板件由 `hardware/cad/electronics_components.scad` 定义并在装配世界坐标中挂载；最终 USB-C 厂家/料号仍需首样冻结。

## 重生成与检查

在带有 KiCad `pcbnew` 的 Python 环境运行：

```text
KICAD_PYTHON=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
$KICAD_PYTHON generate_daughter_boards.py
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
  --output /tmp/pingpang-receiver-drc.txt m6-receiver-carrier-v0.2.kicad_pcb
```

原理图由上一级脚本生成并可直接在 KiCad 打开：

```text
python3 ../generate_daughter_schematics.py
```

三个板的首样目标是几何 DRC 为 0；未连接项是尚未布线的有意气连线，不等于 ERC/量产放行。每次修改板框或 `net_stand.scad` 后，回到仓库根目录运行：

```text
$KICAD_PYTHON hardware/electronics/validate_system_fit.py
```

## 盖合边界

盒盖这里不追求 IP 防水等级。“水密”只表示盖板装上后定位唇、连续压合面和胶条/替换密封条能够贴合，不出现明显贯通缝、错台或松动；线缆则用压紧出线件和应力释放完成装配。实际胶条压缩量、PETG boss 强度、电池弯折半径和连接器插拔空间仍需首样实物确认。
