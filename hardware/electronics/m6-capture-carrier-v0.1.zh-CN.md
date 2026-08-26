# M6 十路边沿采集载板接口 v0.1

状态：`协议与 ESP32-S3 SPI master/IRQ 读取路径已实现并通过 ESP-IDF 5.5.1 编译；STM32G031K8U6/UFQFPN32 已有寄存器绑定和可链接参考 ELF/bin；运行时时钟校准门和板级 hook 已接入但默认关闭；光耦最终型号、PCB、线长和实物时序仍待确认`。

这份输入解决 SmartPaddle 参考主板的实际 GPIO 冲突。它不把 10 路输入接到当前 `net_sensor_config.h` 的占位 GPIO，也不使用普通 I²C 轮询去替代短脉冲采集。

## 1. 推荐分层

```text
M6 接收器 BK × 10
        │ 10–30 V NPN 开集电极
        ▼
每路独立 R_IN + 光耦隔离 + 3.3 V 逻辑
        │
        ▼
独立边沿采集 MCU（10 路 GPIO/定时器 + FIFO）
        │ 3.3 V SPI，带 IRQ
        ▼
SmartPaddle ESP32-S3
        │
        ▼
现有 NetEvent / SmartPaddle 设备端 /ws / App
```

一个逻辑高度通道对应一只发射器和一只接收器；当前机械主线因此是 10 个光束、20 枚 M6 实物（10 发射 + 10 接收）。载板只采集 10 路接收端 BK，发射端 BN/BU 由受保护的传感器电源独立供电。

载板 MCU 的唯一职责是：对 10 路隔离后的数字输入捕获上升/下降边沿、保存本地微秒时间戳、检测 FIFO 溢出，并通过 SPI 提供带 CRC 的事件帧。它不解释 `clean_over`、不计算高度，也不把传感器连接状态伪装成健康快照。

## 2. SmartPaddle 侧连接分配

SmartPaddle 参考 checkout 的 `pcb/lib/esp32s3wroom1/pinmap.py` 显示以下 GPIO 未被其当前项目绑定占用；机器可读候选保存在 [`firmware/main/m6_carrier_config.h`](../../firmware/main/m6_carrier_config.h)，仍需在最终 PCB 原理图和启动日志上复核：

| SmartPaddle GPIO | 载板信号 | 方向 | 说明 |
| --- | --- | --- | --- |
| GPIO10 | `CARRIER_SCK` | ESP32-S3 → 载板 | SPI mode 0；首样从 1 MHz 开始 |
| GPIO11 | `CARRIER_MOSI` | ESP32-S3 → 载板 | 事件读取事务填 `0x00`；时钟同步事务发送 `CLOCK_SYNC_REQUEST`，仍保持固定 152-byte 事务 |
| GPIO12 | `CARRIER_MISO` | 载板 → ESP32-S3 | 事件帧 |
| GPIO13 | `CARRIER_CS_N` | ESP32-S3 → 载板 | 每个事务重新对齐帧 |
| GPIO14 | `CARRIER_IRQ_N` | 载板 → ESP32-S3 | FIFO 非空/边界错误，开漏或 3.3 V 推挽按 PCB 定义 |
| GPIO5 | `CARRIER_RESET_N` | ESP32-S3 → 载板 | 低有效复位；上电默认保持复位 |
| GND | `CARRIER_GND` | — | 只允许 3.3 V 逻辑侧共地 |

GPIO19/20 的 USB、GPIO43/44 的 UART0、GPIO0/45/46 的启动脚和 GPIO35–37 的 N16R8 OPI PSRAM 不得改作载板信号。可重复审计命令：

```text
python3 tools/validate_smartpaddle_reference.py
```

当前审计会报告现有 Pingpang 直连占位与 SmartPaddle 的冲突；这正是选择独立载板的依据，不是让当前占位数组直接上板。

## 3. 事件帧协议

协议实现位于 [`firmware/main/m6_carrier_protocol.h`](../../firmware/main/m6_carrier_protocol.h) 和 `.cpp`；ESP32-S3 的固定最大帧 SPI master 位于 [`firmware/main/m6_carrier_spi.h`](../../firmware/main/m6_carrier_spi.h)/`.cpp`，载板侧的固定 FIFO/打包核心位于 [`firmware/carrier/m6_carrier_capture_core.h`](../../firmware/carrier/m6_carrier_capture_core.h)，MCU 无关的 SPI 从机事务边界位于 [`firmware/carrier/m6_carrier_spi_slave_transport.h`](../../firmware/carrier/m6_carrier_spi_slave_transport.h)。帧采用小端序：

| 偏移 | 长度 | 字段 |
| ---: | ---: | --- |
| 0 | 2 | magic `A5 5A` |
| 2 | 1 | protocol version `1` |
| 3 | 1 | type `EDGE_BATCH=1` |
| 4 | 2 | payload 长度 |
| 6 | 4 | 单调递增 `sequence` |
| 10 | 1 | `edge_count`，最多 16 |
| 11 | 1 | flags：bit0=`fifo_overflow`，bit1=`timestamp_invalid` |
| 12 | 2 | 保留，必须为 0 |
| 14 | 8 | `base_timestamp_us`，载板本地单调时钟 |
| 22 | N×8 | 每条记录：`channel:u8, level:u8, reserved:u16, delta_us:u32` |
| 22+N×8 | 2 | CRC-16/CCITT，覆盖 magic 到最后一条记录 |

解码边界和从机 TX 生命周期已经有主机测试：完整帧、逐字节分片、噪声重同步、CRC 损坏、通道越界、时间差越界、序号跳变、FIFO 溢出标志、同步请求/响应 CRC 与 t2/t3、对称事务时钟偏移估计、运行时多样本校准门、152-byte 预装缓冲和 CS 提前释放。主控适配层必须遵守：

1. 先做 CRC、长度、通道范围和序号连续性检查；
2. 用主控发出/收到时间戳与载板收到/发出时间戳做对称事务估计，再把载板时钟转换到 ESP32 `esp_timer` 单调时间域；协议实现提供 `m6_carrier_estimate_clock_offset()` 和 `M6CarrierClockCalibration`。运行时校准默认要求至少 3 个已完成且显式标记 `exchange_verified=true` 的交换、往返时间不超过 50 ms、offset spread 不超过 250 us、相邻样本时钟漂移不超过 500 us，并优先采用最低往返样本；真实载板仍需周期性复测漂移，不能直接把两个时钟当成同一个时钟；
3. 每条记录按原始 `level` 送入现有 `BeamCapture`，由最终 NPN/光耦实测极性决定 `blocked`；
4. `fifo_overflow`、`timestamp_invalid`、序号跳变、时钟同步失效或 SPI 帧损坏时，清空当前边界并让下一业务事件保持 `unknown`；
5. ESP32 master 的事件读取路径当前用 IRQ 触发一次最大 `152 bytes` SPI mode 0 事务（MOSI 填 `0x00`）；独立时钟同步路径则发送 `CLOCK_SYNC_REQUEST`，随后再读取 `CLOCK_SYNC_RESPONSE`。载板 SPI 从机应在拉低 IRQ 前预装对应 TX 缓冲，并保持到 CS 释放；主控再按类型、长度和 CRC 解码。不在 SPI 任务里生成 JSON 或决定高度，`beam_channel_map` 和 `NetEventAggregator` 仍是唯一业务解释层。

时钟同步不是事件帧里的隐含字段，而是独立的两个固定长度事务：

| 类型 | wire payload | 含义 |
| --- | ---: | --- |
| `CLOCK_SYNC_REQUEST=2` | 4 bytes | 载板收到完整请求后记录 `t2=carrier_received_us`，并准备下一事务响应 |
| `CLOCK_SYNC_RESPONSE=3` | 20 bytes | 载板在响应 CS assertion 时记录 `t3=carrier_sent_us`，返回 `t2/t3` 和有效标志 |

ESP32 master 的 `exchange_clock_sync()` 用请求开始的 `t1=host_sent_us`、响应事务结束的 `t4=host_received_us` 解码成一份 `M6CarrierClockSyncSample`；载板传输层、ESP32-S3 参考载板和 STM32G031 参考端口都已实现这个两事务生命周期。它解决的是代码/协议边界，不等于实板已经测得 SPI/IRQ 延迟、时钟漂移或最小有效脉宽。

当前 v0.1 的事件帧和独立同步事务代码均已实现，但 `firmware/main/m6_carrier_config.h` 中 `kCarrierClockOffsetConfirmed` 仍必须保持 `false`；主循环只有在 `exchange_clock_sync()` 或板级 `smartgear_board_read_m6_carrier_clock_sync()` 提供真实四时间戳，且 `M6CarrierClockCalibration::confirm()` 通过后才更新适配器 offset。弱 hook 默认返回不可用。校准失效或尚未确认时，ESP32 主循环会清空载板边界，不会生成有效高度事件；改变 offset 时也会丢弃旧时间域中的半截边界。实际选定 MCU、PCB、示波器/逻辑分析仪波形和漂移记录仍是现场放行门。

## 4. 板级首样输入

- 每一路 M6 BK 先按 [`m6-npn-interface-v0.1.zh-CN.md`](m6-npn-interface-v0.1.zh-CN.md) 经过独立输入电阻和光耦；不得让 10–30 V 到达载板 MCU；
- 每路保留 `TP_SENSOR_BK[n]`、`TP_OPTO_LED[n]`、`TP_CARRIER_IN[n]`；首样同时测传感器侧和载板侧边沿；
- 载板每路必须能在本地定时器中捕获双边沿，不能用“主控读一次 GPIO”推断没有漏脉冲；
- FIFO 深度、SPI 服务周期和线缆传播延迟必须以最坏 10 路同时变化、1–10 ms 参考脉冲实测；
- 最大 16 边沿帧为 `152 bytes`，SPI 纯传输时间在 `1 MHz` 下约 `1.216 ms`、`4 MHz` 下约 `0.304 ms`；这只是总线占用预算，不能替代载板本地捕获和 FIFO 深度实测；
- 输入电源、发射器电源和逻辑 3.3 V 分开去耦，传感器侧按 10–30 V 保护方案执行；
- 当前工程候选为 `STM32G031K8U6 / UFQFPN32`，具体 pin map 见 [`m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md`](m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md)；候选必须至少提供 10 路边沿输入、硬件定时器、SPI 从机、非易失校准版本和掉电安全复位。DMA/定时器寄存器绑定、最小启动/链接脚本和参考 ELF/bin 已完成源码/链接级检查，但选型闸门、实物波形和最终 PCB 仍未关闭，不能生成最终 PCB。

## 5. 放行门

1. 空载 SPI 读写：CRC 正确、序号连续、复位后第一帧可识别；
2. 单路 1/2/3/4/5/6/8/10 ms 参考脉冲：传感器侧、光耦侧和载板事件时间戳一一对应；
3. 十路同时变化：无 FIFO 溢出、无丢帧、无错误通道；
4. 断开/短接/过压保护故障：载板上报边界错误，业务层输出 `unknown`；
5. 完成 SmartPaddle `/ws` 适配后，再按 [`bring-up-v0.1.zh-CN.md`](bring-up-v0.1.zh-CN.md) 执行逐路映射、健康快照和真实球体验收。

在上述证据完成前，本载板是“可制造接口和可测试协议”，不是已验证的 M6 最小脉宽或真实球速性能结论。首样连接器、测试点、隔离器件位置和画板顺序见 [`m6-capture-carrier-first-article-bom-v0.1.zh-CN.md`](m6-capture-carrier-first-article-bom-v0.1.zh-CN.md)；该输入仍不等于已有 PCB。
