# 软件与数据工具

这里放置 `NetEvent v0.1` 查看器、光栅/压电记录导出、标定记录和与训练/比赛相关系统的适配层。

首版业务数据来自 ESP32-S3 的光栅位图、离散高度区间、PVDF 质量信息和时间戳。外部视频仅作为可选回放证据，不是本设备的实时识别链路。

T-03 的时间戳关联工具见 [`../docs/timestamp-correlation-v0.1.zh-CN.md`](../docs/timestamp-correlation-v0.1.zh-CN.md) 和 [`../tools/correlate_net_events.py`](../tools/correlate_net_events.py)。它只根据现场记录提供的外部时间戳、明确偏移和时间窗生成关联结果，不读取或解释视频画面。
