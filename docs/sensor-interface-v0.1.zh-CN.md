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
- 比较器触发后才从 DMA 派发、但时间戳仍早于触发点的样本会回填当前帧预触发尾部；时间戳不早于触发点的样本才消耗后触发槽位。
- 迟到的 DMA 样本只有在 `trigger_us - sample_timestamp_us` 不超过配置的预触发时间窗时才允许回填；更早的旧 backlog 会被丢弃，不能冒充当前事件的预触发证据。
- `start_capture()` 快照滚动历史时也按每路样本时间戳筛选：只保留严格早于触发点且仍在预触发窗口内的样本；触发后的样本不能因主循环延迟而倒灌进预触发波形。
- 光栅和 PVDF 在聚合器中分别维护输入时间边界；不使用单一全局顺序拒绝跨传感器的合法异步关联，但同一传感器流中跨事件的旧观测会 fail-closed。
- 当前 ESP-IDF ADC 适配器的 DMA 读取帧上限为 256 bytes，帧缓存不得为 0，底层存储缓冲不得小于读取帧，且帧大小必须是 ADC 原始结果字节数的整数倍；重复 ADC 通道配置会拒绝初始化。这是软件边界，不替代最终 PCB 的 ADC 资源复核。
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

板级实现可直接复用 `firmware/main/sensor_self_test.h` 中的
`evaluate_beam_self_test()`、`piezo_baseline_is_quiet()` 和
`make_sensor_health_snapshot()`：逐路光学检查先生成 `pass_mask/fail_mask`，
PVDF 安静基线单独判定，机械参考线/安装标定由 `mechanical_calibration_valid`
提供。组合器允许光栅部分失败但只放行健康 bit；报告形状、校准 ID、非有限阈值
或机械标定失败都会 fail-closed，不会把不完整快照写成有效校准。

运行时通过 `sensor_health_gate.h` 的
`apply_sensor_health_snapshot()` 统一执行这一步：健康快照 hook、主机回放和
ESP32 任务不会各自复制一套校验逻辑。hook 不可用时调用
`apply_sensor_health_unavailable()`，聚合器会固定进入不可放行状态并保留
`health-snapshot-unavailable` 诊断 ID。

健康快照在事件归并期间发生变化也不会追溯覆盖旧候选：只要待决的光栅或
PVDF 候选跨过一次实际健康状态变化，最终事件会带
`sensor_health_changed_during_event` 并保持 `unknown`；重复提交完全相同的快照
不会触发该标记。

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

SmartPaddle 当前工程的实际 WebSocket 接口、压电资源冲突和强 hook 接入示例见 [`smartpaddle-integration-v0.1.zh-CN.md`](smartpaddle-integration-v0.1.zh-CN.md)。

修改信号命名、通道顺序、时间窗口或 `NetEvent` 字段时，应同步更新该 CSV、回放测试和本契约，并保留实测原始波形/逻辑分析仪证据。
