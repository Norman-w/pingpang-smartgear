# 固件工程

这是 ESP32-S3 的业务固件骨架，专注于网顶擦网与过网高度事件，不在本仓库复制外部 SmartPaddle/目标 App 的配网、连接管理和多设备基础设施。

## 业务链路

```text
10 路 M6 NPN 光电 GPIO/中断 ─┐
                    ├─ NetEventAggregator ── NetEvent v0.1 ── WebSocket 适配点
2 路 PVDF comparator ─┘          │
                                 ├─ RGB/蜂鸣器适配点
                                 └─ RAM RingBuffer 断链缓存
```

`piezo_waveform.*` 保存每路 16 kHz、20 ms 预触发和 80 ms 后触发的双通道短波形，并在波形完成后计算峰值、能量和持续时间；ADC 流超时或冷启动时预触发历史不足会释放/保留相应帧，但让事件带 `waveform_incomplete`，不把零填充历史当作有效基线；主循环先消费比较器边沿再派发 ADC DMA，时间戳早于触发点的 backlog 样本会回填当前帧的预触发尾部；空引用不会启动可回放帧，乱序帧入队后会清空滚动历史，防止坏样本污染下一事件；GPIO 队列溢出等输入边界失败调用 `abort()` 时，当前帧和尚未交给业务层的 ready 帧都会丢弃，避免跨边界波形被归档。`piezo_waveform_archive.*` 保留最近若干帧，`waveform_ref` 不再是无目标的占位字符串。`piezo_adc_continuous.*` 已提供 ADC1 continuous/DMA 适配，并保留与目标 SmartPaddle/ESP-IDF 5.5.x 原始结果格式的适配边界，同时兼容 ESP-IDF 6.x 的解析接口；配置会拒绝重复 ADC 通道、无效帧大小和超过读取缓冲区的帧；目标 PCB 的最终引脚表和 AFE 输出范围仍需实机确认。

## 构建与测试

- ESP32-S3：在 ESP-IDF 环境中从 `firmware/` 运行 `idf.py build`；
- 主机业务测试：运行 `python3 host-tests/run_tests.py`；
- 主机测试依赖：在 `firmware/` 下运行 `python3 -m pip install -r host-tests/requirements.txt`；GitHub Actions 会自动执行主机、CTest、Python/Schema、预览、OpenSCAD 和 ESP32-S3/ESP-IDF 5.5.1 验证；
- `m6_carrier_protocol_tests` 额外验证载板帧的 CRC/长度/分片/序号/时钟偏移/FIFO 边界、`CLOCK_SYNC_REQUEST/RESPONSE` 两事务 t2/t3、至少三次低延迟稳定样本的运行时校准门、换 offset 时清空旧边界、载板 SPI 从机 TX 预装/IRQ-CS 生命周期、短事务 fail-closed、10 路同时双边沿的 20-edge 分帧以及原始电平进入 `BeamCapture` 的适配；它不替代载板 SPI 电气波形和实物短脉冲测试；
- 主机测试覆盖光栅位图/安静结束/超时/乱序/反向时间边界保护、PVDF 双通道归并、完整与不完整波形特征/归档/非有限值保护、窗口外 DMA backlog 丢弃、比较器先到后由 DMA 完成波形并归并为 `touch_over` 的顺序路径、输入边界失败时清空 ready 波形、传感器健康快照质量门、健康快照在待决事件期间变化时的 fail-closed 处理、聚合器对空校准 ID/越界健康位图和坏边界的 fail-closed 处理、GPIO 队列溢出、四种事件状态、端到端传感器归并、完整事件进入断链 RAM 缓存并恢复补发、传输恢复、JSON Schema 和 CSV 轨迹回放；ESP32 任务侧在队列溢出后会清空旧边沿，再等待新输入建立边界。

参考平级 checkout `../SmartPaddle` 的 `firmware/main/ws_data_server.h` 提供 `ws_data_has_client()` / `ws_data_send_text()`；`smartpaddle_ws_transport_adapter.cpp` 在定义 `SMARTGEAR_SMARTPADDLE_WS`、加入 SmartPaddle 的 include path 并链接其完整网络 component 后提供两个强 hook，默认构建仍保留弱 hook，因此不会把未链接的网络服务误报成已连接。这个适配器只完成代码边界，不代表两个工程已经合并或实机联调。

针对 SmartPaddle GPIO 冲突，`m6_carrier_protocol.*`、`m6_carrier_adapter.*` 和 `m6_carrier_spi.*` 已在 host 测试及现有 ESP-IDF v5.5.1 配置的 CMake build 中通过载板帧解码、ESP32-S3 SPI master/IRQ 读取、运行时四时间戳校准门和 `BeamCapture` 边界适配验证；`sensor_board_hooks.*` 的 `smartgear_board_read_m6_carrier_clock_sync()` 是板级同步事务注入口；`carrier/m6_carrier_capture_core.*` 与 `carrier/m6_carrier_spi_slave_transport.*` 提供 MCU 无关的载板 FIFO、TX 预装和 IRQ/CS 事务边界。`carrier_config::kUseM6Carrier` 默认关闭；载板 MCU 固件、PCB/光耦实物、实机时钟同步和 SPI/IRQ 波形仍需接板放行，未确认时主循环会清空边界并保持 `unknown`，不会伪造有效高度事件。

`carrier/esp32s3-reference/` 是一个独立的 ESP32-S3 载板平台参考工程，可在 ESP-IDF 5.5.1 下编译验证 10 路 GPIO ISR、SPI slave DMA、IRQ/RESET 和协议核心；它不等于最终生产 MCU 或 PCB。

`sensor_board_hooks.h` 的健康快照 hook 用于注入校准 ID、10 路光栅健康位图和 PVDF 安静基线，`sensor_health_gate.*` 负责把同一份快照以可测试的 fail-closed 规则写入聚合器；在 M6 SKU、NPN 常开/常闭极性、隔离前端和逐路自检未确认前，`net_sensor_config.h` 的 `kBeamPolarityConfirmed=false` 还会在主循环入口拒绝健康快照；`piezo_waveform_hook.h` 可把完整/不完整原始帧同步复制到目标回放存储。健康 hook 未实现、返回失败或快照形状非法时固件保持 `unknown`，不生成未经验证的有效事件；波形 hook 未实现时仍保留本地 RAM 归档。

载板工程候选的无 HAL 端口外壳见 [`carrier/stm32g031-reference/`](carrier/stm32g031-reference/)。它验证 `STM32G031K8U6/UFQFPN32` pin map、EXTI → 1 µs 定时器、SPI1 mode 0/152-byte TX staging、IRQ/CS 和复位生命周期；目录提供依赖 ST 官方 CMSIS device/core 与 ARM 工具链的寄存器级 object compile-only 绑定，以及可选的最小 STM32G031 参考 ELF/bin 构建。参考镜像已在本机链接并导出，但真实 PCB、DMA/ISR 波形、CS glue、烧录上电和接板验收仍保持 pending。

硬件 GPIO 映射在 `main/net_sensor_config.h` 中明确标为首轮占位，不能在最终 PCB 未复核前视为量产引脚表。`kBeamLogicalIndexByInput` 把原始 GPIO bit 映射到逻辑高度；默认是 identity，实物通道表确认非直序后必须同步更新并重新构建。健康快照使用映射后的逻辑位图。
