# ESP32-S3 主控与 1S 电源首样板 v0.2

状态：`目录沿用 v0.1 入口；当前板为真实 KiCad v0.2 首样板，已附原生主控原理图和板级 3D 模型；几何 DRC 0；尚未完成铜箔布线、ERC、器件实测和量产释放`。

这是放入桌下夹体梯形腔的 ESP32-S3 主控/电源板，不把 M6 的 10 路 NPN 输入直接接到 ESP32。M6 接收器仍由独立的 STM32G031 + 光耦载板采集，主控板通过 J4 接收 3.3 V SPI/IRQ；载板输入与光耦/连接器冻结仍是下一块板的工作。

## 机械配合

| 项目 | v0.2 值 |
| --- | ---: |
| PCB 外形 | `86 × 32 mm`，2 层首样放置板 |
| 梯形腔 x 范围 | `777.5…880.3 mm`，有效长 `102.8 mm` |
| 梯形腔 y 半宽 | `20 mm`，总有效宽 `40 mm` |
| 腔体顶板 | `4 mm` |
| PCB 顶面器件预留 | `4 mm` 器件包络 + `1 mm` 装配余量 |
| 两侧承力壁 | 各 `9 mm` |
| 底盖 | `3 mm`，4 个 M3 试样孔 |
| 电池包预留 | 受保护 1S，约 `65 × 30 × 7 mm` |
| 主板安装 | 4 个 `Ø2.8 mm NPTH`，与腔内 boss 对齐 |
| 主板边缘余量 | x 向总 `16.8 mm`，y 向按实际器件包络检查；板框本体为 `86 × 32 mm` |

PCB 的 86 mm 长度和 32 mm 宽度由当前 `hardware/cad/net_stand.scad` 的参数探针约束；SCAD 现在直接导入本目录 KiCad 导出的真实板/器件 STL，不再使用无来源的蓝色板占位。橙色电池是按 `65 × 30 × 7 mm` 的受保护软包包络，实际料号仍需首样冻结。

母板不把十路现场线和所有交互器件挤在同一块板上：右侧接收端使用独立的窄长十路载板，左侧发射端使用独立电源子板（默认内置受保护 1S 电池，同时保留外接 10–30 V 端子）。UI 子板承接盖面器件，其中 START/MODE 按键、状态/电量 LED 和 USB-C 直接焊在 UI PCB 上；屏幕保留排线接口，扬声器和蜂鸣器仍通过锁扣线束连接。

## 电源拓扑

```text
USB-C VBUS
    │
    └─ F1 PTC 1.1 A ─ vbus_limited ─┐
                                    │ VIN
受保护 1S 电池 J2 ─ bat_p ──────────┤ IP5305T
                                    │ 1S charger + 5 V boost
                                    └─ sys_5v ─ TPS62162 ─ 3v3 ─ ESP32-S3

J3 外部 10…30 V ─ F2 PTC ─ TVS 33 V ─ sensor_fused ─ M6 载板/传感器电源
                     （与 bat_p、sys_5v 不相连）
```

- J2 只接受带保护板的 1S 锂电池包；v0.1 不允许裸电芯直接接入。
- 电池电压经 `1 MΩ / 1 MΩ + 100 nF` 分压接 ESP32 GPIO9（`bat_sense`），这是电量估算，不是电池保护。
- IP5305T 的 LED1 经 1 kΩ 指示灯到地；KEY 由 SW1 拉低。LED2/LED3 保留为明确的 `*_nc` 测试网。
- TPS62162 按固定 3.3 V 连接，`FB` 接地，`VOS` 接 3v3；L2 为候选 `2.2 µH` 降压电感。
- M6 传感器电源从 J3 外接，不从电池升压输出偷电；NPN 黑线必须留在光耦载板侧。

## J4 载板接口

| J4 | 信号 | ESP32-S3 GPIO | 方向 |
| ---: | --- | ---: | --- |
| 1 | `3v3` | 3V3 | 主控供电 |
| 2 | `gnd` | GND | 逻辑地 |
| 3 | `carrier_sck` | GPIO10 | 主控 → 载板 |
| 4 | `carrier_mosi` | GPIO11 | 主控 → 载板 |
| 5 | `carrier_miso` | GPIO12 | 载板 → 主控 |
| 6 | `carrier_cs_n` | GPIO13 | 主控 → 载板 |
| 7 | `carrier_irq_n` | GPIO14 | 载板 → 主控 |
| 8 | `carrier_reset_n` | GPIO5 | 主控 → 载板 |

这组接口与 [`firmware/main/m6_carrier_config.h`](../../../firmware/main/m6_carrier_config.h) 的候选映射一致；`kUseM6Carrier` 仍保持关闭，直到载板、SPI/IRQ 波形和时钟同步完成实测。

## J8 传感器电源接口

| J8 | 信号 | 说明 |
| ---: | --- | --- |
| 1 | `sensor_fused` | J3 外部 10–30 V 经 PTC/TVS 后的传感器电源 |
| 2 | `gnd` | 传感器电源回路 |

J8 只接接收载板的电源端，J4 只接 3.3 V 逻辑；现场线束采用锁扣式端子或可插拔螺钉/压接端子，不允许在装配状态下直接焊飞线。

## J7 UI 子板接口

| J7 | 信号 | ESP32-S3 GPIO |
| ---: | --- | ---: |
| 1 / 2 | `3v3 / gnd` | 电源 |
| 3 / 4 | `ui_sda / ui_scl` | GPIO16 / GPIO15 |
| 5 / 6 | `ui_btn_start / ui_btn_mode` | GPIO3 / GPIO4 |
| 7 | `ui_buzzer` | GPIO8 |
| 8 / 9 / 10 | `ui_spk_bclk / ui_spk_ws / ui_spk_dout` | GPIO6 / GPIO7 / GPIO17 |
| 11 / 12 | `ui_led_status / ui_led_battery` | GPIO18 / GPIO21 |

UI 子板使用 0.96 英寸 I2C OLED 排线接口、两颗 PCB 直装 3.9×3.0×2.0 mm 两脚 SMD 按键、两颗 0603 单色 LED、带声学膜的扬声器/蜂鸣器，以及一颗 16 针 USB-C 直装插座。按键、LED 和 USB-C 的坐标直接对应 y+ 面框开口。

## 文件与重生成

- [`esp32-control-v0.1.kicad_pcb`](esp32-control-v0.1.kicad_pcb)：KiCad 10 板文件，含 43 个首样封装、4 个 M2.5 NPTH 安装孔、1 个 ESP32 天线原生禁布区、2 个覆铜区、2 个电源芯片裸焊盘地过孔、0 条信号/电源铜线和 65 个待布气连线项；所有线束连接器候选均为 MX1.25。
- [`esp32-control-v0.1.kicad_sch`](esp32-control-v0.1.kicad_sch)：原生 KiCad 主控/电源/USB-C/M6/UI/PVDF 接口原理图；当前 ERC 仍为 `185` 条消息（`114` errors / `71` warnings），因此是可审查首样而非生产放行。
- [`../../output/pdf/esp32-control-v0.1-schematic.pdf`](../../output/pdf/esp32-control-v0.1-schematic.pdf)：由 `kicad-cli sch export pdf` 生成的原理图审查 PDF。
- [`../../3d/v0.2/`](../../3d/v0.2/)：由 KiCad `pcbnew` 导出的母板及子板 STL/STEP；壳体使用这些模型做统一坐标干涉检查。
- [`generate_board.py`](generate_board.py)：唯一板文件生成器；使用 KiCad 随附的 `pcbnew` Python API。
- [`../generate_kicad_schematic.py`](../generate_kicad_schematic.py)：原生 `.kicad_sch` 生成器。
- [`bom.csv`](bom.csv)：候选首样 BOM，器件封装/厂商料号仍需采购与实测冻结。
- [`circuit.md`](circuit.md)：人可审查的电路连接表和放行门。

```text
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
  generate_board.py
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
  --output /tmp/pingpang-control-drc.txt esp32-control-v0.1.kicad_pcb
```

本次 DRC 结果是“0 个几何/短路/边界违规，65 个未连接项”。65 个未连接项来自有意保留的首样气连线，不能写成 DRC 已通过，也不能直接导出 Gerber 生产。

### 子板首样

[`../daughter-boards-v0.2/`](../daughter-boards-v0.2/) 内包含：

- `m6-receiver-carrier-v0.2.kicad_pcb`：`80 × 32 mm` 集中式接收载板，十个 `MX1.25` 三芯口、一个 8 芯主控口和一个 2 芯传感器电源口；安装时长边沿 M6 壳体线缆侧竖直放置。光学头之间的 20 mm 间距不再展开到板框；
- `emitter-power-v0.2.kicad_pcb`：`68 × 32 mm` 发射端电源板，内置电池口、MX1.25 外接电源口、独立升压模块占位和 `J_TX_A/J_TX_B` 两个 10 芯十路发射线束口；
- `ui-panel-v0.2.kicad_pcb`：`58 × 28 mm` 盖面交互板，含 MX1.25 J7 对插、OLED 排线座、PCB 直装按钮/LED、I2S 扬声器、蜂鸣器和 16 针 USB-C 插座。

三块子板同样已经有原生 KiCad PCB/项目和实际板级 3D 导出；它们仍是首样放置/网表板，不能把未完成的升压模块、光耦或连接器选型直接当成最终可采购料号。

## 还未关闭的硬件门

1. IP5305T、TPS62162、USB-C 和 ESP32-S3 的最终厂商封装/焊盘/散热铜皮需要在 Eeschema 和目标封装库中复核；当前附带的是可打开、可检查、已参与机械包络的首样库模型。
2. 完成电源区布线后，测 USB 限流、低电量/Wi-Fi/LED 峰值电流、IP5305T/TPS62162 温升和 3.3 V 纹波。
3. 只用带保护的 1S 电池包；电池极性、连接器防呆、保险丝和外壳防磨损要在首样装配中记录。
4. 载板的光耦最终型号、`R_IN` 电流、10 路 NPN 波形、连接器和 STM32G031 PCB 仍需单独完成。
5. 底盖/安装柱的 PETG 拉脱和夹体受力测试完成后，才能冻结 PCB 固定方式和导出打印/加工包；盒盖要用连续胶条/定位唇压合，目标是装好后无明显贯通缝、错台或松动，不代表 IP 等级。
6. 用 KiCad 随附 Python 运行 `hardware/electronics/validate_system_fit.py`，需在每次改板/改壳后确认母板、发射子板、UI 子板和 M6 窄长接收板仍在各自包络内。
