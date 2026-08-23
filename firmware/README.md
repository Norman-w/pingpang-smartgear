# 固件工程

这是 ESP32-S3 的业务固件骨架，专注于网顶擦网与过网高度事件，不复制 SmartPaddle 已经完成的配网、连接管理和 App 多设备基础设施。

## 业务链路

```text
10 路光栅 GPIO/中断 ─┐
                    ├─ NetEventAggregator ── NetEvent v0.1 ── WebSocket 适配点
2 路 PVDF comparator ─┘          │
                                 ├─ RGB/蜂鸣器适配点
                                 └─ RAM RingBuffer 断链缓存
```

`piezo_waveform.*` 保存每路 16 kHz、20 ms 预触发和 80 ms 后触发的双通道短波形，并在波形完成后计算峰值、能量和持续时间；`piezo_waveform_archive.*` 保留最近若干完整帧，`waveform_ref` 不再是无目标的占位字符串。`piezo_adc_continuous.*` 已提供 ADC1 continuous/DMA 适配，并兼容 SmartPaddle 当前使用的 ESP-IDF 5.5.x 原始结果格式与 ESP-IDF 6.x 的解析接口；目标 PCB 的最终引脚表和 AFE 输出范围仍需实机确认。

## 构建与测试

- ESP32-S3：在 ESP-IDF 环境中从 `firmware/` 运行 `idf.py build`；
- 主机业务测试：运行 `python3 host-tests/run_tests.py`；
- 主机测试覆盖光栅位图/安静结束、PVDF 双通道归并、波形特征/归档与超时质量标记、传感器自检质量门、四种事件状态、波形窗口、环形缓存和 JSON Schema。

硬件 GPIO 映射在 `main/net_sensor_config.h` 中明确标为首轮占位，不能在最终 PCB 未复核前视为量产引脚表。
