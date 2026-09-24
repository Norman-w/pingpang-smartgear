# 电路连接审查表 v0.2

本文、原生 [`esp32-control-v0.1.kicad_sch`](esp32-control-v0.1.kicad_sch) 和 `generate_board.py` 共同描述首样板；真正的网名和焊盘连接以生成的 `.kicad_pcb` 为机器可读基线。这里的 v0.2 是可打开、可审查的首样/放置网表，尚不是完成布线的量产原理图。

## 电源

| 区块 | 连接 | 备注 |
| --- | --- | --- |
| USB-C | `usb_vbus → F1 → vbus_limited → U2.1 VIN` | F1 候选 PTC 1.1 A |
| USB-C 数据 | `USB_DP → R1 22R → usb_dp_mcu → U1.GPIO20`；`USB_DN → R2 22R → usb_dn_mcu → U1.GPIO19` | CC1/CC2 各 5.1 kΩ 到 GND |
| 1S 电池 | `J2.1 bat_p → U2.6 BAT`；`J2.2 → gnd` | 仅带保护 1S 包 |
| 电池检测 | `bat_p → R5 1 MΩ → bat_sense → R6 1 MΩ → gnd`；`bat_sense → C1 100 nF → gnd` | GPIO9，估算用途 |
| 5 V | `U2.7 boost_sw ↔ L1 2.2 µH ↔ U2.8 sys_5v` | IP5305T 升压环路 |
| 3.3 V | `U3.2 sys_5v`，`U3.3 buck_en`，`U3.6 3v3`，`U3.7 buck_sw ↔ L2 2.2 µH`，`U3.5 FB → gnd` | TPS62162 固定 3.3 V 候选连接 |
| 按键/指示 | `U2.5 power_key ↔ SW1 ↔ gnd`；`U2.2 led_charge → R8 1 kΩ → D1 → gnd` | LED2/LED3 为 `ip_led2_nc/ip_led3_nc` |

## 外部接口

| 连接器 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| J3 传感器电源 | `sensor_ext` | `gnd` | — | — |
| J8 接收载板电源 | `sensor_fused` | `gnd` | — | — |
| J5 PVDF ADC | `pvdf_adc_l` | `gnd` | `pvdf_adc_r` | `gnd` |
| J6 PVDF 比较器辅助 | `pvdf_cmp_aux_l` | `pvdf_cmp_aux_r` | — | — |

J3 后面预留 F2 PTC 与 D2 33 V TVS。它只是 10–30 V 外部电源入口；当前板没有把外部传感器黑线引到 ESP32。J6 明确是辅助/DNP 接口，因为 GPIO14 已给 M6 载板 IRQ，不能在板上偷偷复用。

J8 是 J3 保护后的两芯 MX1.25 可插拔电源 hand-off，和 J4 的 3.3 V 逻辑线分开。接收载板上的十路 `J_RX00…J_RX09` 均为三芯 MX1.25 锁扣接口，发射端另有独立电源子板，并以 `J_TX_A/J_TX_B` 两个 10 芯 MX1.25 接口承接十路两线线束；现场线束不采用裸焊盘或飞线。这里的线束汇聚与插接位置不改变光学头的 20 mm 机械间距。

## J7 UI 子板

| J7 | 网名 | ESP32-S3 GPIO | UI 子板负载 |
| ---: | --- | ---: | --- |
| 1 / 2 | `3v3 / gnd` | — | OLED、按钮、LED、音频公共电源 |
| 3 / 4 | `ui_sda / ui_scl` | GPIO16 / GPIO15 | 0.96 英寸 I2C OLED 排线接口 |
| 5 / 6 | `ui_btn_start / ui_btn_mode` | GPIO3 / GPIO4 | 两个面板按钮 |
| 7 | `ui_buzzer` | GPIO8 | 蜂鸣器驱动 |
| 8 / 9 / 10 | `ui_spk_bclk / ui_spk_ws / ui_spk_dout` | GPIO6 / GPIO7 / GPIO17 | I2S 扬声器模块 |
| 11 / 12 | `ui_led_status / ui_led_battery` | GPIO18 / GPIO21 | UI PCB 上的 0603 单色直装指示灯 |

## ESP32-S3 关键焊盘

| 模块焊盘 | 网名 | 功能 |
| ---: | --- | --- |
| 1 / 40 | `gnd` | 地 |
| 2 | `3v3` | 主电源 |
| 3 | `esp_en` | CHIP_PU |
| 5 | `carrier_reset_n` | GPIO5 |
| 14 / 15 | `usb_dn_mcu / usb_dp_mcu` | GPIO19/20 |
| 4 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 16 / 23 | `ui_btn_mode / ui_spk_bclk / ui_spk_ws / ui_scl / ui_sda / ui_spk_dout / ui_led_status / ui_buzzer / ui_btn_start / ui_led_battery` | GPIO4 / GPIO6 / GPIO7 / GPIO15 / GPIO16 / GPIO17 / GPIO18 / GPIO8 / GPIO3 / GPIO21 |
| 17 | `bat_sense` | GPIO9 / ADC1_CH8 |
| 18…22 | `carrier_sck/mosi/miso/cs_n/irq_n` | GPIO10…14 |
| 27 | `boot` | GPIO0 启动脚 |
| 38 / 39 | `pvdf_adc_r / pvdf_adc_l` | GPIO2 / GPIO1 |
| 36 / 37 | `uart_rx / uart_tx` | 调试串口保留 |

GPIO35…37 的 OPI PSRAM/模块专用限制、GPIO0/45/46 启动约束和 USB/UART 引脚不能因下一轮布线方便而改变。

## 放行顺序

1. 在 KiCad 中把 `U1/U2/U3/J1/J2/J3/J4/J7/J8` 换成已经核对过的厂商库封装；逐焊盘对照本表和数据手册。
2. 先布 USB/电池/5 V/3.3 V 电源环路，再布 J4 SPI/IRQ；天线禁布区保持原生 rule area。
3. ERC/DRC 关闭真实违规后，限流电源、空载/低电量/Wi-Fi/LED 工况逐项测量。
4. 电源与主控稳定后，再接独立 M6 载板，测 CS/IRQ/RESET 方向、1 MHz 首样事务和四时间戳同步。
5. y+ 侧 UI 采用一体式填平固定板从腔内安装，8 枚腔内自攻钉均匀固定；这里只要求面板齐平、无明显错台或松动，不把它写成 IP 防水等级。USB-C、按钮、屏和声学件均通过面板开口/硅胶帽/声学膜处理。
