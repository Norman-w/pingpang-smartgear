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

`piezo_waveform.*` 保存每路 16 kHz、20 ms 预触发和 80 ms 后触发的双通道短波形，并在波形完成后计算峰值、能量和持续时间；ADC 流超时会释放采集状态、保留不完整帧并让事件带 `waveform_incomplete`。`piezo_waveform_archive.*` 保留最近若干帧，`waveform_ref` 不再是无目标的占位字符串。`piezo_adc_continuous.*` 已提供 ADC1 continuous/DMA 适配，并兼容 SmartPaddle 当前使用的 ESP-IDF 5.5.x 原始结果格式与 ESP-IDF 6.x 的解析接口；目标 PCB 的最终引脚表和 AFE 输出范围仍需实机确认。

## 构建与测试

- ESP32-S3：在 ESP-IDF 环境中从 `firmware/` 运行 `idf.py build`；
- 主机业务测试：运行 `python3 host-tests/run_tests.py`；
- 主机测试依赖：在 `firmware/` 下运行 `python3 -m pip install -r host-tests/requirements.txt`；GitHub Actions 会自动执行主机、CTest、Python/Schema、预览和 OpenSCAD 验证；
- 主机测试覆盖光栅位图/安静结束/超时/乱序保护、PVDF 双通道归并、完整与不完整波形特征/归档/非有限值保护、传感器健康快照质量门、GPIO 队列溢出 fail-closed、四种事件状态、端到端传感器归并、传输恢复、JSON Schema 和 CSV 轨迹回放。

SmartPaddle 连接层实现 `net_event_transport.h` 中的两个 hook 即可接入已有 WebSocket/连接管理；`sensor_board_hooks.h` 的健康快照 hook 用于注入校准 ID、10 路光栅健康位图和 PVDF 安静基线；`piezo_waveform_hook.h` 可把完整/不完整原始帧同步复制到既有回放存储。健康 hook 未实现、返回失败或快照形状非法时固件保持 `unknown`，不生成未经验证的有效事件；波形 hook 未实现时仍保留本地 RAM 归档。

硬件 GPIO 映射在 `main/net_sensor_config.h` 中明确标为首轮占位，不能在最终 PCB 未复核前视为量产引脚表。
