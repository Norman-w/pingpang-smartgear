# M6 载板采集核心

`m6_carrier_capture_core.*` 是与具体 MCU 无关的采集核心：

- GPIO/定时器中断调用 `on_edge(channel, level, timestamp_us)`；
- SPI 从机任务可调用 `pop_frame()` 后用 [`../main/m6_carrier_protocol.h`](../main/m6_carrier_protocol.h) 编码发送，也可调用 `pop_encoded_frame()` 直接填充至少 `152 bytes` 的 TX staging buffer；缓冲区过小会返回 0 且不消费 FIFO；
- 64 条边沿 FIFO、每帧最多 16 条；
- FIFO 溢出、非法电平/通道和时间戳倒退都通过协议 flag/丢弃计数暴露；
- 不做去抖、不要求 5 ms 最小遮挡、不延长或伪造传感器脉冲。

`m6_carrier_spi_slave_transport.*` 把 MCU 无关的 SPI 从机事务边界再收口一层：`service()` 预装完整帧，平台层随后拉低 `IRQ_N`；`begin_transaction()` 到 `end_transaction(152)` 期间 TX 缓冲不可替换；CS 提前释放会把 `timestamp_invalid` 置到下一帧。它还提供独立的 `CLOCK_SYNC_REQUEST` 接收事务和 `CLOCK_SYNC_RESPONSE` 两阶段 t2/t3 返回，不把同步字段混进事件帧。它不会假装已经实现某一颗 MCU 的 SPI/DMA 外设，平台适配只需要把 `tx_buffer()` 接到 DMA、把 `irq_asserted()` 映射到 IRQ 电平，并在 CS 边沿调用对应事务函数。

当前仓库另有一个独立的 [ESP32-S3 参考工程](esp32s3-reference/)，把上述事务接到 ESP-IDF `spi_slave` 和 10 路 GPIO ISR；它只是可编译的平台基线，不替代最终 MCU/封装/PCB 选型。

当前工程候选 `STM32G031K8U6 / UFQFPN32` 另有一个 [STM32G031 端口外壳](stm32g031-reference/)。它把候选 pin map、EXTI 输入、TIM 1 MHz、SPI1 DMA TX staging、IRQ/CS 和复位边界收成无 HAL 的接口，并由 host test 验证；同目录还提供依赖 ST CMSIS device/core 的寄存器级 compile-only 绑定，以及包含启动文件/链接脚本的可选参考 ELF/bin 构建。参考镜像可用于启动链检查，但十路 ISR 延迟、SPI/IRQ 波形、CS glue、最终 PCB 和烧录上电证据仍是现场放行项。

最小平台侧顺序：

```text
transport.service()
if transport.irq_asserted(): drive IRQ_N low
on CS low: transport.begin_transaction(); start SPI/DMA from tx_buffer()
on CS high: transport.end_transaction(transferred_bytes); drive IRQ_N high
```

当前提供可在 host/sanitizer 下验证的事件帧、同步请求/响应和 SPI 从机事务契约；ESP32-S3 主控侧的 `exchange_clock_sync()`/IRQ 读取在 `firmware/main/m6_carrier_spi.*` 已接入，ESP32-S3 参考载板和 STM32G031 参考端口也已接到同一传输状态机。具体载板 MCU 的 GPIO ISR、硬件定时器、SPI/DMA 外设、看门狗外壳和同步波形仍需在选定 MCU/PCB 后做实物放行。
