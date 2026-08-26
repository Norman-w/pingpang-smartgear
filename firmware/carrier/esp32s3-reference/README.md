# ESP32-S3 载板参考工程

这是一个可编译的载板平台参考，不是最终 MCU/PCB 决策。它用第二块 ESP32-S3 演示：

- 10 路光耦后的 GPIO 双边沿 ISR + `esp_timer` 时间戳；
- ESP-IDF `spi_slave` DMA、mode 0、最大 152-byte 事务；
- IRQ/RESET 控制、事件帧 TX 生命周期和 [`../m6_carrier_spi_slave_transport.*`](../m6_carrier_spi_slave_transport.h) 的两事务时钟同步响应；
- 与 SmartPaddle 主控侧 [`../../../main/m6_carrier_spi.*`](../../../main/m6_carrier_spi.h) 的协议连接。

GPIO ISR 入口和采集核心边沿写入路径显式标记为 IRAM；最终板仍需检查 map/链接器段、实机缓存关闭场景和逻辑分析仪波形，不能仅凭本工程编译结果放行。

## 参考引脚

| 信号 | GPIO |
| --- | ---: |
| `CARRIER_IN[0..9]` | 4–13 |
| `SPI_SCK/MOSI/MISO/CS_N` | 15/16/17/18 |
| `IRQ_N` | 14 |
| `RESET_N` | 21 |

这是独立载板的候选引脚，不是 SmartPaddle ESP32-S3 主控引脚。正式板仍必须按 [`../../../hardware/electronics/m6-capture-carrier-mcu-selection-v0.1.zh-CN.md`](../../../hardware/electronics/m6-capture-carrier-mcu-selection-v0.1.zh-CN.md) 做封装、启动脚、调试口和 EMI 复核。

## 构建

在 ESP-IDF `v5.5.1` 环境中：

```text
idf.py -C firmware/carrier/esp32s3-reference build
```

本机已使用 ESP-IDF `v5.5.1` 完成正式参考构建，生成 `m6_capture_carrier_esp32s3_reference.bin`（220256 bytes）；CI 仍以 `esp-idf-ci-action@v1` 的 `v5.5.1/esp32s3` 为准。该结果只证明参考工程可编译和链接，不等于最终 MCU、PCB、SPI/IRQ 波形或传感器实物已经放行。

该工程只证明平台适配可以编译和连接；未接真实光耦、M6、SPI 线和示波器前，不能把 `carrier_integration` 改成 `pass`，也不能把此参考工程当成量产 PCB。
