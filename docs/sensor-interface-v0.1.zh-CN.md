# 乒乓智配传感器板级接口契约 v0.1

本文定义业务固件与传感器板、SmartPaddle 既有连接层之间的边界。它不是最终 PCB 原理图、引脚表或器件 BOM；在真实 AFE、PCB 和球网样机确认前，所有 GPIO/ADC 引脚都只能按“首轮占位”理解。

## 1. 逻辑信号

| 信号 | 数量 | 方向/边沿 | 当前约定 | 当前占位 |
| --- | ---: | --- | --- | --- |
| `BEAM_BLOCKED[i]` | 10 | GPIO，双边沿 | 低电平表示光束被遮挡；`i=0…9` 对应 +10…+100 mm 档位 | GPIO 4…13 |
| `PVDF_TRIGGER[i]` | 2 | GPIO，上升沿 | 高电平表示比较器候选触发；`i=0` 左，`i=1` 右 | GPIO 14、15 |
| `PVDF_ADC[i]` | 2 | ADC1 continuous/DMA | AFE 波形输入；每路业务采样率初始 16 kHz | ADC GPIO 1、2 |
| 反馈 LED | 3 | GPIO 输出 | 由业务状态映射 RGB 提示 | GPIO 16…18 |
| 蜂鸣器 | 1 | GPIO 输出 | 由业务状态映射短提示音 | GPIO 19 |

实际接线必须同时满足最终 PCB、电源启动脚、SmartPaddle 既有资源和 EMC 约束；不允许直接把表中的占位值当作量产引脚表。

## 2. 时序与采集边界

- ESP32-S3 GPIO 事件由 ISR 只采集通道、电平和 `esp_timer_get_time()` 单调微秒时间戳，再交给业务任务归并；ISR 不做 JSON、阈值学习或波形分析。
- 光栅输入采用并行 GPIO 采集，不以逐路低速轮询替代。业务层输出 `beam_mask`、最低/最高命中档位和区间结果。
- PVDF 比较器只产生低延迟候选；ADC1 连续采样保存触发前 20 ms、触发后 80 ms 的双通道短波形。
- AFE 的偏置、保护、增益、带通、比较器迟滞和光学调制参数必须通过真实波形与环境光测试冻结；接口契约不为这些参数预设精度。
- GPIO 队列溢出、健康快照不可用/形状非法、标定无效或波形不完整时，业务状态保持 `unknown`，不得输出伪造的有效高度或擦网结论。

## 3. SmartPaddle 适配 hook

### 3.1 传输

已有连接层实现 `net_event_transport.h` 中的两个 C hook 即可接入 WebSocket、BLE、MQTT 或 SSE 中的任一适配器：

```cpp
bool smartgear_board_transport_connected();
bool smartgear_board_transport_send_json(const char* json);
```

业务层只发送 `NetEvent v0.1` 的 JSON。连接断开或发送失败时，`NetEventDelivery` 按事件 ID 顺序保留在 RAM 环形缓存中；恢复连接后按原顺序补发，失败事件不被丢弃。具体容量当前为 16 条，仍需结合 SmartPaddle 设备内存和产品策略复核。

### 3.2 健康与标定

板级自检/标定层实现以下 hook，返回 `true` 才表示快照可用：

```cpp
bool smartgear_board_read_sensor_health(
    char* calibration_id,
    std::size_t calibration_id_capacity,
    std::uint16_t* healthy_beam_mask,
    bool* beam_health_valid,
    bool* piezo_baseline_valid,
    bool* calibration_valid);
```

`healthy_beam_mask` 的 bit 顺序必须与 `BEAM_BLOCKED[i]` 一致。健康快照不可用、校准 ID 为空/未终止，或健康位图包含第 10 路以外的 bit 时，固件会主动设置无效标记并让后续事件进入 `unknown`。

### 3.3 原始 PVDF 波形

如 SmartPaddle 已有诊断/回放存储，可实现以下同步 hook：

```cpp
bool smartgear_board_on_piezo_waveform(
    const char* reference,
    std::uint64_t trigger_us,
    std::size_t pre_trigger_samples,
    const std::int16_t* left_samples,
    std::size_t left_count,
    const std::int16_t* right_samples,
    std::size_t right_count,
    bool complete);
```

样本指针只在函数调用期间有效，适配层必须在返回前复制；返回 `false` 不影响固件将该帧保留在本地 RAM 归档中。完整帧和超时释放的不完整帧都可以通过此边界记录。

## 4. 可运行回放边界

`firmware/host-tests/trace_replay.cpp` 使用真实的光栅、PVDF、短波形采集和事件归并类读取 `fixtures/net_trace_v0.1.csv`。它会生成紧凑的预触发/后触发样本并检查 `waveform_ref`、持续时间和状态派生，再验证 JSON Schema；它不模拟 ADC 电气噪声、光学串扰、夹具滑移或真实无线链路。

修改信号命名、通道顺序、时间窗口或 `NetEvent` 字段时，应同步更新该 CSV、回放测试和本契约，并保留实测原始波形/逻辑分析仪证据。
