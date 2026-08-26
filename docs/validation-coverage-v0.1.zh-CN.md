# 乒乓智配验证证据映射 v0.1

> 当前硬件主线已经切换为用户指定的 M6 十路光电器件阵列 + 铝合金三轴微调基座；本文中保留的 STG-120ML 和旧版 10 路/10 mm 描述只作为历史接口兼容，不能当作当前 M6 器件已经具备逐点输出的证据。机械、采购和接口判断以 `docs/m6-optical-array-design-v0.1.zh-CN.md` 为准。

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
| M-01 | 无；`tools/validate_field_record.py` 可校验现场记录格式 | 记录项完整性和证据路径安全 | 内置支架重复从桌下夹紧、安装位置、滑移和软垫损伤记录 |
| M-02 | `hardware/cad/validate_net_stand.py`；OpenSCAD CI 当前 `net_stand.scad` 各部件、夹体/上表面保护垫/台底压块/圆头螺杆/固定下臂螺母/旋钮两枚对锁螺母拆分、18/25/30 mm 台厚免打孔矩阵、镜像、独立打印零件 STL 封闭边拓扑与非法参数路径 | 免打孔 C 形夹体跨过台边，上表面可替换保护垫位于固定上夹板与桌面之间，圆头 M8 螺杆只到台底压块下表面；固定下臂单枚螺母与旋钮两枚对锁螺母的包络、叠层深度和螺杆穿越关系可编译；独立打印零件的 STL 没有开放边/非流形边，组合装配 PART 只作为可视检查，左右导出可编译 | 实物样块/球台的夹紧力、台面损伤、保护垫材料/压缩、立柱倾斜、螺杆行程、对锁防松和标准件实际装配 |
| M-03 | `validate_net_stand.py`；`render_net_stand_preview.py`；装配页 | `152.5 mm` 网顶、`1830 mm` 名义网架总宽、左右各 `152.5 mm` 网柱外伸、当前夹体外轮廓名义外伸 `160 mm` 且结构下限为 `130 mm`、台边外三角侧肋、双侧替换式支架、3 段承载条与拼接片、左右各一根 M6 梳齿安装条、20 个 M6 直角器件包络、三轴微调基座、10 对名义光轴和 PVDF 安装位的参数与可视关系 | 真实网布张力、两侧外伸后的脚部/球路净空、三角肋耐久性、左右立柱/梳齿条平行度、网顶高度、M6 螺纹/螺母/光学中心、NPN 供电/电平和线缆净空；若宣称标准网夹兼容，还需量测 ITTF T2 的开口/台下投影边界 |
| B-01 | `test_clean_over_and_height_interval()`、`test_every_beam_mask_interval()` | `clean_over`、位图、离散高度和球底间隔契约 | 真实光束与球体遮挡 |
| B-02 | `test_sensor_pipeline_end_to_end()`、`test_trigger_before_dma_dispatch_pipeline()`、`test_runtime_chain_with_delivery()`、`net_event_trace` | 擦网候选与光栅关联、波形引用/特征、`touch_over` 以及事件进入传输缓存 | PVDF 前端与真实过网动作 |
| B-03 | `test_touch_no_cross_and_unknown()`、`net_event_trace` | 擦网无光栅时的 `touch_no_cross` 和质量标记 | 真实擦网未过网动作 |
| B-04/B-05 | `test_touch_over_before_and_after_beam()` | 左/右单通道 `sensor_mask` 与前后时序关联 | 左右 PVDF 实物分别接板触发 |
| B-06 | `test_each_beam_channel_independently()`、`test_beam_channel_remapping()`；全部 `1…1023` 位图 Schema 遍历（当前 10 路业务契约）；短遮挡实测按 [`m6-response-time-validation-v0.1.zh-CN.md`](m6-response-time-validation-v0.1.zh-CN.md) 执行 | 10 个 M6 接收端 NPN 通道的逻辑编号、原始输入 bit 到高度的排列映射、位图契约；商家 5 ms 响应语义已记录 | 实际 M6 发射/接收器、NPN 常开/常闭后缀、10–30 V 供电、负载/光耦或电平转换、最终逐通道接线顺序、最小输入脉宽、输出脉宽和逐通道遮挡响应 |
| M6 载板协议 | `m6_carrier_protocol_tests`、`m6_carrier_protocol.*`、`m6_carrier_adapter.*`、`m6_carrier_spi.*`、`sensor_board_hooks.*`、`carrier/m6_carrier_capture_core.*`、`carrier/m6_carrier_spi_slave_transport.*`、`carrier/stm32g031-reference/m6_carrier_stm32g031_port.*`、`carrier/stm32g031-reference/m6_carrier_stm32g031_register_port.*`、`carrier/stm32g031-reference/m6_carrier_stm32g031_startup.cpp`、`carrier/stm32g031-reference/stm32g031k8u6.ld`、可选 `CMakeLists.txt`、`m6_carrier_stm32g031_port_tests`、`m6-capture-carrier-stm32g031k8-pinmap.example.json`；ESP-IDF 5.5.1 build；`arm-none-eabi-g++ 16.2.0` + ST/ARM 官方头文件 object compile-only 与参考 ELF/bin | CRC/长度/分片/序号/FIFO 边界、`CLOCK_SYNC_REQUEST/RESPONSE` 两事务 t2/t3、载板侧固定 TX 缓冲编码、SPI 从机 IRQ/CS 生命周期、短事务 fail-closed、主机侧对称事务时钟偏移估计、至少三次样本的 offset spread/相邻漂移/最低 RTT 运行时校准门、板级同步 hook、换 offset 时清空旧边界、原始电平到 `BeamCapture` 的时间戳适配、ESP32-S3 IRQ 驱动固定最大 SPI 事务、STM32G031K8U6 的 10 路唯一 EXTI pin map、PB0/NSS 专用 EXTI0 CS 边沿、18/22 根 GPIO 资源预算、host 侧十路同时双边沿 20-edge 分帧、无 HAL 端口外壳、基于 ST CMSIS 的 EXTI/TIM2/SPI1/DMA1/DMAMUX1 寄存器绑定、最小启动/向量表/链接脚本、DMA/SPI 错误 fail-closed 和 DMA 计数一致性检查 | 最终板级固件与可烧录验证、PCB 与 SPI/IRQ 电气波形、真实同步事务波形/时钟漂移、真实十路同时边沿和 1–10 ms 实测 |
| B-07 | `test_channel_self_test_and_baseline()`、`test_sensor_health_quality_flags()`、`test_sensor_health_gate_pipeline()` | 发射/接收/基线/健康位图失败时 fail-closed | 断发射、偏接收、网体遮挡和环境光实测 |
| B-08 | `BeamSelfTestReport` 形状测试和健康门测试 | 每通道 pass/fail 位图可组合且坏快照不放行 | 上电自检在目标板逐通道执行并留档 |
| B-09 | `test_sensor_health_quality_flags()` | GPIO 队列溢出后的旧输入清理和 `unknown` | ESP32-S3 真实 ISR 高频边沿压力 |
| S-01 | `test_waveform_window()`、`test_trigger_before_dma_dispatch_pipeline()` | 双通道窗口、触发前/后边界、迟到 DMA 回填和波形特征 | ADC1 实际 16 kHz、AFE 电压/噪声/削顶测量 |
| S-02 | 无 | — | 旋钮、碰夹具、球网振动的原始波形与误报率 |
| S-03 | `test_waveform_timeout_flush()`、`test_touch_no_cross_and_unknown()` | 不完整帧释放、`waveform_incomplete` 和 fail-closed 状态 | 接板后真实 ADC 中断/超时行为 |
| T-01/T-02 | `test_delivery_recovery_and_feedback()`、`test_runtime_chain_with_delivery()`、可选 `smartpaddle_ws_transport_adapter.cpp` | 断链缓存、容量覆盖、发送失败、补发顺序和不重复，并验证完整传感器事件序列化后进入缓存再补发；联合 target 可强绑定 SmartPaddle `/ws` API | SmartPaddle/App 联合 target 编译、设备端 WebSocket 回环、健康快照和真实球事件 |
| T-03 | `tools/correlate_net_events.py`、`tools/test_correlate_net_events.py` | 对 `NetEvent.timestamp_us` 与外部 CSV 时间标记执行明确偏移、包含边界和时间窗匹配；不读取视频，也不解释图像 | 同钟来源/偏移的现场测量、外部设备导出文件和真实事件日志 |
| E-01 | `test_sequential_and_overlapping_events()`、`net_event_trace` | 可分离事件、重叠事件 fail-closed 和事件 ID | 真实连续单球与球路分离能力 |

## 2. 现场证据门

`docs/field-validation-record.example.json` 当前 19 项全部为 `pending`，`tools/validate_field_record.py` 只验证编号完整性和证据路径安全，不会把主机测试自动改成 `pass`。因此当前结论是：

- 软件/协议/参数验证链已具备并持续由 CI 执行；
- M-01、S-02 没有可替代的主机证据；T-03 现在有纯时间戳关联工具覆盖，但仍没有真实同钟/偏移的现场证据；
- B-06～B-09、S-01～S-03、T-01～T-02、E-01 以及 M6 载板协议的主机证据不能关闭对应实物验收项；
- 只有在证据目录存在照片、量具/示波器/逻辑分析仪记录、原始波形或真实事件日志后，才允许把记录从 `pending` 改成 `pass`/`fail`。
