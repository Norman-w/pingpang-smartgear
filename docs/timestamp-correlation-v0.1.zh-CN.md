# 外部回放时间戳关联 v0.1

这是一项面向 T-03 的保守数据工具：把 `NetEvent.timestamp_us` 与外部设备导出的时间标记按一个明确的时钟偏移和时间窗做匹配。它不读取视频帧，不识别球，不计算连续高度，也不把外部设备的结果改写成擦网裁判结论。

## 输入

事件文件是 JSONL，每行可以是原始 `NetEvent` JSON，也可以是主机回放输出的 `JSON_EVENT {...}` 行。至少需要 `type=net_event`、非空 `event_id` 和非负 `timestamp_us`。

外部标记是 CSV，必须有 `external_timestamp_us` 列，可选 `record_id` 与 `source`：

```csv
record_id,external_timestamp_us,source
camera-001,123456789,haikang
camera-002,123457120,haikang
```

没有 `record_id` 时工具使用行号生成 ID；没有 `source` 时使用 `external`。工具只保存这些标记信息，不假定外部设备使用了哪一种视频时间基准。

## 运行

```text
python3 tools/correlate_net_events.py \
  --events evidence/run-01-events.jsonl \
  --external evidence/run-01-external.csv \
  --offset-us -1234 \
  --window-us 50000 \
  > evidence/run-01-timestamp-correlation.jsonl
```

工具先计算：

```text
aligned_external_timestamp_us = external_timestamp_us + offset_us
delta_us = aligned_external_timestamp_us - event_timestamp_us
```

当 `abs(delta_us) <= window_us` 时输出为匹配项；边界是包含的。`offset_us` 的正负号必须在现场记录中说明，不能为了得到匹配而事后任意调整。每个事件都会输出一行，匹配项按绝对偏差、对齐时间和记录 ID 稳定排序；没有匹配项也会保留空数组。

## 证据边界

该工具只能证明输入记录之间的确定性时间窗关联。T-03 仍需要现场提供同钟来源或可复核的偏移测量、外部设备导出文件和事件 JSONL；工具成功运行不等于视频内容已验证，也不关闭 M/B/S 项的实物验收。
