# M6 十路边沿采集载板首样 BOM 与画板输入 v0.1

状态：`首样接口/BOM 输入已整理；STM32G031K8U6/UFQFPN32 有无 HAL 参考 ELF/bin，光耦型号、连接器脚距和 PCB 尚未冻结`。

本文件是给画板和首样采购使用的边界，不是已经存在的 KiCad 原理图，也不是可直接下单的最终 BOM。当前仓库没有载板 `.kicad_sch/.kicad_pcb`；在真实 M6 型号、光耦时序和 MCU 封装确认前，不能用一份手写网表冒充制造数据。

关联输入：

- [`m6-npn-interface-v0.1.zh-CN.md`](m6-npn-interface-v0.1.zh-CN.md)：每路 NPN 隔离拓扑和电流/功耗边界；
- [`m6-capture-carrier-v0.1.zh-CN.md`](m6-capture-carrier-v0.1.zh-CN.md)：ESP32-S3 侧 SPI/IRQ、帧协议和载板职责；
- [`m6-capture-carrier-mcu-selection-v0.1.zh-CN.md`](m6-capture-carrier-mcu-selection-v0.1.zh-CN.md)：MCU 候选、封装和 GPIO/时序放行门；
- [`m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md`](m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md)：当前工程候选的具体 pin map 和 EXTI 约束；
- [`../../firmware/carrier/esp32s3-reference/`](../../firmware/carrier/esp32s3-reference/)：可编译的 ESP32-S3 载板平台参考，不是生产板冻结；
- [`../../docs/m6-first-article-release-v0.1.zh-CN.md`](../../docs/m6-first-article-release-v0.1.zh-CN.md)：机械首样、网夹和 M6 实物放行顺序。

## 1. 电气分区和承诺边界

```text
J_SENSOR_POWER  V_SENSOR 10–30 V ── fuse/PTC ── TVS ── sensor distribution
                                      │
J_RX[0..9]  BK ── R_IN ── optocoupler LED   optocoupler transistor ── CARRIER_IN[0..9]
J_TX[0..9]  BN/BU ── sensor power only       3V3 + R_PULL + R_GPIO ── MCU

MCU 3V3 domain ── SPI_SCK/MOSI/MISO/CS_N + IRQ_N + RESET_N ── J_HOST ── ESP32-S3
                                  │
                               J_DEBUG / test points
```

- `V_SENSOR` 与 `V_LOGIC=3.3 V` 分区布线；10–30 V 只允许出现在传感器/光耦 LED 侧。
- 每一个接收器 BK 单独进入一只光耦；禁止十路并联、禁止把 BK 直接接 ESP32-S3 或载板 MCU。
- 发射器只需要 BN/BU 受保护供电，不进入边沿采集 MCU；接收器使用 BN/BU 供电并把 BK 送入独立输入通道。
- 光耦输出默认按开集电极 `3V3 → R_PULL → CARRIER_IN`；“遮挡为低”仍只是候选，最终极性必须以实物波形和卖家后缀确认。
- 载板 MCU 不负责高度、球状态或 WebSocket，只负责双边沿时间戳、FIFO、CRC 帧和边界错误。

## 2. 连接器和测试点命名

通道编号固定从低到高：`CH00=+10 mm` 到 `CH09=+100 mm`。左右两侧各自保持同样顺序；左右侧在线束标签中增加 `L/R`，不能靠线缆颜色猜通道。

| 位号/命名 | 数量 | 引脚/信号 | 首样要求 |
| --- | ---: | --- | --- |
| `J_SENSOR_POWER` | 1 | `V_SENSOR`, `0V_SENSOR`, 屏蔽/PE 预留 | 带防呆、保险/PTC 后接入；首样测启动峰值与压降 |
| `J_RX00…J_RX09` | 10 | `BN`, `BU`, `BK` | 每个接收器独立 3-pin；通道号永久印在丝印/线标 |
| `J_TX00…J_TX09` | 10 | `BN`, `BU` | 每个发射器独立 2-pin；不把发射/接收插座混用 |
| `J_HOST` | 1 | `3V3`, `GND`, `SCK`, `MOSI`, `MISO`, `CS_N`, `IRQ_N`, `RESET_N` | 推荐锁定或带防呆 2×5/1×8；SPI mode 0、首样 1 MHz |
| `J_DEBUG` | 1 | 具体按 MCU：SWD/JTAG/USB/UART | 即使量产不留，也必须为首样保留可探测焊盘 |
| `TP_SENSOR_BK00…09` | 10 | 每路传感器侧 BK/负载节点 | 与 `TP_OPTO_LED` 同时探测，不接 MCU 地以外的错误参考 |
| `TP_OPTO_LED00…09` | 10 | 光耦 LED 电流/回路节点 | 用于 10/24/30 V 电流和温升验证 |
| `TP_CARRIER_IN00…09` | 10 | 3.3 V MCU 输入 | 与逻辑分析仪地和 MCU 侧参考一致 |
| `TP_SPI_* / TP_IRQ / TP_RESET` | 至少 6 | SPI 四线、IRQ、RESET | 必须能在不拆板时测量 IRQ 到 CS、帧保持和复位 |

`J_HOST` 的信号方向与 SmartPaddle 侧一致：ESP32-S3 输出 `SCK/MOSI/CS_N/RESET_N`，载板输出 `MISO/IRQ_N`；两侧只共 3.3 V 逻辑地，不把 `0V_SENSOR` 是否与 MCU 地相连写成默认结论，按实际隔离/电源方案审查。

## 3. 首样参考 BOM

数量是“一块十路载板”的参考数量；`待选型` 不是可采购料号。画板时每个 `DNP` 位置必须保留焊盘和丝印，不得为了省位置删除短脉冲实验能力。

| 类别 | 参考位号 | 数量 | 规格/边界 | 状态 |
| --- | --- | ---: | --- | --- |
| 输入限流 | `R_IN00…09` | 10 | `1.8 kΩ ±1% / 1 W`；按卖家允许负载重算 | 参考值，待 M6 确认 |
| 输入隔离 | `U_OPTO00…09` | 10 | 约 5 mA LED 电流下有明确 CTR、传播延迟和温度保证的逻辑/高速光耦 | 型号待选 |
| MCU 上拉 | `R_PULL00…09` | 10 | `4.7 kΩ ±1%` 到 3.3 V | 参考值 |
| MCU 串阻 | `R_GPIO00…09` | 10 | `100 Ω ±1%`，靠近 MCU/连接器 | 参考值 |
| 输入滤波 | `C_EDGE00…09` | 10 | `1 nF`，默认 `DNP`；仅作为实测后可装选项 | DNP |
| 传感器入口保护 | `F1/PTC1`, `D1` | 1 套 | 保险/PTC、反接保护、约 33 V TVS；按最终电源峰值选额定值 | 型号待选 |
| 传感器去耦 | `C_SENSOR` | 1 套 | `100 nF + 47 µF`，耐压按 `V_SENSOR` 选择 | 参考值 |
| 载板 MCU | `U_MCU1` | 1 | `STM32G031K8U6`，UFQFPN32；必须覆盖 10 输入、SPI slave、IRQ/RESET、SWD 和看门狗 | 工程候选；待原型 |
| MCU 去耦 | `C_MCU` | 按数据手册 | 每个电源脚就近 100 nF，另留 1–10 µF | 待 MCU 确认 |
| 主控接口 | `J_HOST` | 1 | 8 信号/电源，锁定或防呆 | 脚距待选 |
| 传感器接口 | `J_RX00…09`, `J_TX00…09` | 20 | RX 3-pin、TX 2-pin；线缆防呆和锁紧优先 | 脚距待选 |
| 调试接口 | `J_DEBUG` | 1 | SWD/JTAG/USB/UART 之一或复合焊盘 | 随 MCU 冻结 |
| 状态/产测 | `LED_STATUS`, `R_TEST` | 1 套 | 可选，不能占用 10 路输入或启动脚 | 待选 |

## 4. 画板规则

1. 先画 `V_SENSOR` 与光耦 LED 区，再画 `3V3` 和 MCU 区，最后画 `J_HOST`；不要让传感器线束先穿过 MCU 区再回到光耦。
2. 每路 `R_IN → U_OPTO LED → BK` 的回路单独编号，光耦输出、上拉、串阻和测试点按同一通道成组放置；`CH00…CH09` 不允许通过“布局顺序”隐式决定。
3. 10 路 MCU 输入尽量放在同一 GPIO/定时器资源组；如果候选 MCU 需要 EXTI 共享或 PIO 分组，必须在选型记录中留下实际 pin mux 和中断延迟证据。
4. SPI、IRQ 和 RESET 走短线并留测试点；`IRQ_N` 的上拉/开漏方式必须在原理图上明确，不能只写在固件注释中。
5. 传感器电源入口、MCU 逻辑电源和主控接口分别标注电压域、地参考和允许探测点；所有连接器丝印必须包括 `L/R`、`TX/RX` 和 `CHxx`。
6. MCU 启动脚、调试脚、晶振/USB/Flash 专用脚不能被十路输入“临时借用”；选型 JSON 的 18/22 根 GPIO 门和具体封装 pinout 是画板放行条件。

## 5. 首样验收顺序

1. 不插 M6：检查 `V_SENSOR` 与 `3V3/GND` 无短路，确认保险、TVS、反接保护和连接器防呆；
2. 只装一条 `R_IN + U_OPTO + R_PULL + R_GPIO`：用受控 10/24/30 V 测 LED 电流、温升、光耦输出边沿和 1/2/3/4/5/6/8/10 ms 脉冲；
3. 复制十路后，用逻辑源对 `CARRIER_IN[0..9]` 同时制造 20 个边沿，验证载板本地 FIFO、最大 16-edge 分帧、SPI TX 预装和 IRQ/CS 生命周期；
4. 接 SmartPaddle ESP32-S3，确认 mode 0、1 MHz、152-byte 事务、CRC/序号和错误帧 fail-closed；
5. 最后才插入真实 M6，逐路记录 `TP_SENSOR_BK`、`TP_OPTO_LED`、`TP_CARRIER_IN`、传感器极性和通道映射。

没有完成第 1–4 步的原始记录前，不能把 `carrier_integration` 或任何通道标成 `pass`；没有真实 M6 与网夹机械记录前，不能把整机验收包标成 `pass`。
