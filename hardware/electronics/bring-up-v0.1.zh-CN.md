# 传感器板 Bring-up 顺序 v0.1

本文是第一次接入 ESP32-S3、PVDF AFE 和 10 路 M6 直角对射 NPN 前端时的操作顺序。它不冻结 PCB 引脚、电压、阈值或器件型号；任何一步未通过，都不能把健康快照标记为有效，也不能生成有效高度/擦网结论。

## 0. 上电前

记录 PCB、固件 commit、`net_sensor_config.h` 版本、校准规版本、`net_stand.scad` 版本和球台台面厚度。断电测量 3.3 V 与 GND 是否短路，确认 ESP32-S3、AFE、发射端和接收端的地线共地；确认 GPIO 1/2 的 AFE 输出不超过最终 ADC 衰减允许范围。首轮占位 GPIO 不能直接视为最终 PCB 引脚。

证据：`<run>-P00-power.csv`、`<run>-P00-board.jpg`、万用表/示波器型号和读数。

## 1. GPIO 电平与时间戳

先不接球网和光学发射器，只接逻辑测试源：

1. 对 `PVDF_TRIGGER[0..1]` 分别施加低/高电平，确认只有上升沿进入对应通道，记录 `esp_timer_get_time()` 时间戳。
2. 对经过负载/光耦/电平转换后的 `M6_BEAM_BLOCKED[0..9]` 逐路施加未遮挡/遮挡电平；若使用 SmartPaddle 参考板，应先在独立载板的 `CARRIER_IN[0..9]` 验证双边沿时间戳、SPI CRC/序号和 FIFO 状态，再确认主控映射到 `M6_BEAM_BLOCKED`。确认逻辑极性按最终 NPN 常开/常闭后缀配置，且每一位与物理高度顺序一致；不得把传感器 10–30 V 输出直接接 ESP32-S3 GPIO。
3. 同时制造两路边沿，确认 GPIO ISR 只入队，不在 ISR 中执行 JSON 或波形分析。

首样隔离前端参考电阻、光耦选择条件、测试点和电源保护见 [`m6-npn-interface-v0.1.zh-CN.md`](m6-npn-interface-v0.1.zh-CN.md)；先用单路验证，再复制到十路。

证据：逻辑分析仪 CSV、串口日志、通道映射表。时间戳乱序或队列溢出时，下一事件必须是 `unknown`。

## 2. M6 NPN 光电逐路自检

保持内置式球网支架、M6 梳齿条和三轴基座固定：

1. 按供应商接线图给发射/接收器件提供 10–30 V，棕线接 +V、蓝线接 0 V；接收端黑线只进入已验证的负载/光耦/电平转换，正常对准时记录每路 NPN 基线和主控侧电平。
2. 关闭/断开发射端，确认 `emitter_ok=false` 或对应通道失败。
3. 横向偏移接收端，确认 `receiver_ok=false` 或对应通道失败。
4. 用不透光挡片逐根遮挡 `+10…+100 mm` 光束，确认每次只有目标 bit 置位；同时记录 NPN 输出电平、负载电流和主控侧逻辑。
5. 让网体持续遮挡，确认与球遮挡不同的健康/边界记录，不把持续遮挡伪造成球高。

把每路结果转换为 `BeamChannelCheck`，调用 `evaluate_beam_self_test()`；只有通过的 bit 才写入 `healthy_beam_mask`。记录 M6 电源、NPN 负载电流、环境光、通道串扰和参考线读数。

商家确认的 5 ms 只表示状态变化到 NPN 输出完成变化的响应时间，不是必须持续遮挡 5 ms 才能检测，也不是小于 5 ms 必定有输出。首样应按 [`docs/m6-response-time-validation-v0.1.zh-CN.md`](../../docs/m6-response-time-validation-v0.1.zh-CN.md) 用已知 1–10 ms 遮挡脉冲同时记录传感器侧和主控侧波形；在最小输入脉宽和输出脉宽未实测前，不得通过高速球体检测验收。

证据：`<run>-B08-channel-<n>.json`、逻辑分析仪 CSV、标定规照片、环境光记录。

## 3. PVDF AFE 与 ADC

在不碰球网的情况下记录每路安静基线，至少覆盖配置的预触发窗口；计算峰值和 RMS，并使用 `piezo_baseline_is_quiet()` 判定。随后依次施加轻触、真实擦网、旋钮操作和夹具碰撞，保存 ADC 原始波形，不先凭单次峰值冻结阈值。

确认：

- ADC1 两路有效采样率为每路 16 kHz；
- 触发前 20 ms、触发后 80 ms 的帧边界正确；
- AFE 最大输出未削顶到危险电压；
- 比较器触发时间与 ADC 波形引用能通过 `waveform_ref` 关联；
- 中途停止 ADC 时得到 `complete=false`，事件带 `waveform_incomplete`。

证据：`<run>-S01-left.csv`、`<run>-S01-right.csv`、`<run>-S01-events.jsonl`、阈值/滤波配置。

## 4. 健康快照与业务放行

SmartPaddle 适配层实现 `smartgear_board_read_sensor_health()` 后，先提交以下组合：

| 组合 | 预期 |
| --- | --- |
| 空校准 ID + `calibration_valid=true` | 快照非法，事件 `unknown` |
| `healthy_beam_mask` 含 bit 10 或更高 | 快照非法，事件 `unknown` |
| 光栅部分失败 | 仅失败 bit 命中时事件 `unknown` |
| PVDF 基线未通过 | 含擦网候选的事件 `unknown` |
| 全部健康且校准 ID 有效 | 才允许 `clean_over`/`touch_over` |

传输 hook 未接入或发送失败不改变业务事件内容；事件进入 RAM 缓存，恢复连接后按原事件 ID 顺序补发。

## 5. 现场放行条件

只有当本文件第 0～4 节证据齐全，并完成 [`docs/field-validation-record-template.zh-CN.md`](../../docs/field-validation-record-template.zh-CN.md) 中的 M/B/S/T/E 项，才允许把“待接板”改成“实机通过”。在此之前，ESP32-S3 成功编译只证明固件可链接，不证明传感器电气或机械性能。
