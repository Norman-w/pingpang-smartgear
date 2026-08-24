# 乒乓智配验证证据映射 v0.1

本文把 [`validation-matrix.zh-CN.md`](validation-matrix.zh-CN.md) 的每一项映射到当前可复核的代码或现场证据。这里的“主机覆盖”只证明业务逻辑、时间边界或数据契约；它不替代传感器、球网、打印件、最终 PCB 和真实 App 的现场记录。

## 1. 软件/主机证据

主机入口：

```text
python3 firmware/host-tests/run_tests.py
ctest --test-dir firmware/host-tests/build --output-on-failure
ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 \
  ctest --test-dir firmware/host-tests/build-sanitize --output-on-failure
```

| 编号 | 当前软件证据 | 能证明什么 | 仍缺什么 |
| --- | --- | --- | --- |
| M-01 | 无 | 现场记录格式可校验 | 立柱重复拆装、滑移和软垫损伤记录 |
| M-02 | `hardware/cad/validate_scad.py`；OpenSCAD CI 19 个导出和 10°/20° 运动端点 | 参数、导出和镜像几何可编译 | 打印件全行程、滚柱防脱、螺杆圆头实际受力 |
| M-03 | `validate_geometry.py`；`render_openscad_preview.py` | 方杆/导轨/参考线的参数关系和可视布局 | 双侧实物平行度、参考线张力和夹具滑移 |
| B-01 | `test_clean_over_and_height_interval()`、`test_every_beam_mask_interval()` | `clean_over`、位图、离散高度和球底间隔契约 | 真实光束与球体遮挡 |
| B-02 | `test_sensor_pipeline_end_to_end()`、`test_trigger_before_dma_dispatch_pipeline()`、`net_event_trace` | 擦网候选与光栅关联、波形引用/特征和 `touch_over` | PVDF 前端与真实过网动作 |
| B-03 | `test_touch_no_cross_and_unknown()`、`net_event_trace` | 擦网无光栅时的 `touch_no_cross` 和质量标记 | 真实擦网未过网动作 |
| B-04/B-05 | `test_touch_over_before_and_after_beam()` | 左/右单通道 `sensor_mask` 与前后时序关联 | 左右 PVDF 实物分别接板触发 |
| B-06 | `test_each_beam_channel_independently()`；全部 `1…1023` 位图 Schema 遍历 | 通道编号、位图和高度映射 | 10 根真实光束逐根遮挡 |
| B-07 | `test_channel_self_test_and_baseline()`、`test_sensor_health_quality_flags()`、`test_sensor_health_gate_pipeline()` | 发射/接收/基线/健康位图失败时 fail-closed | 断发射、偏接收、网体遮挡和环境光实测 |
| B-08 | `BeamSelfTestReport` 形状测试和健康门测试 | 每通道 pass/fail 位图可组合且坏快照不放行 | 上电自检在目标板逐通道执行并留档 |
| B-09 | `test_sensor_health_quality_flags()` | GPIO 队列溢出后的旧输入清理和 `unknown` | ESP32-S3 真实 ISR 高频边沿压力 |
| S-01 | `test_waveform_window()`、`test_trigger_before_dma_dispatch_pipeline()` | 双通道窗口、触发前/后边界、迟到 DMA 回填和波形特征 | ADC1 实际 16 kHz、AFE 电压/噪声/削顶测量 |
| S-02 | 无 | — | 旋钮、碰夹具、球网振动的原始波形与误报率 |
| S-03 | `test_waveform_timeout_flush()`、`test_touch_no_cross_and_unknown()` | 不完整帧释放、`waveform_incomplete` 和 fail-closed 状态 | 接板后真实 ADC 中断/超时行为 |
| T-01/T-02 | `test_delivery_recovery_and_feedback()` | 断链缓存、容量覆盖、发送失败、补发顺序和不重复 | SmartPaddle/App 真实 WebSocket/BLE/MQTT/SSE 回调 |
| T-03 | 无 | — | 与外部视频/设备时间轴的同钟或偏移记录 |
| E-01 | `test_sequential_and_overlapping_events()`、`net_event_trace` | 可分离事件、重叠事件 fail-closed 和事件 ID | 真实连续单球与球路分离能力 |

## 2. 现场证据门

`docs/field-validation-record.example.json` 当前 19 项全部为 `pending`，`tools/validate_field_record.py` 只验证编号完整性和证据路径安全，不会把主机测试自动改成 `pass`。因此当前结论是：

- 软件/协议/参数验证链已具备并持续由 CI 执行；
- M-01、S-02、T-03 目前没有可替代的主机证据；
- B-06～B-09、S-01～S-03、T-01～T-02、E-01 的主机证据不能关闭对应实物验收项；
- 只有在证据目录存在照片、量具/示波器/逻辑分析仪记录、原始波形或真实事件日志后，才允许把记录从 `pending` 改成 `pass`/`fail`。

