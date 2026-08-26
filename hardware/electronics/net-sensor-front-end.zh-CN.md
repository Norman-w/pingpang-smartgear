# 网顶传感器前端首轮实现说明

这是一份板级实现边界说明，不是已经冻结的 PCB 原理图或最终 BOM。具体放大器、保护器件、光电二极管和阈值必须以真实波形、环境光和通道串扰测试为依据。

## PVDF 双通道

每个 PVDF 夹片保持可拆卸，尽量只把网顶白边的动态振动耦合进传感器：

```text
PVDF
  ├─ 串联限流/钳位与输入保护
  ├─ 中点偏置
  ├─ 可调增益 + 带通滤波 ──→ ADC1 连续采样
  └─ 可调阈值比较器 ───────→ ESP32-S3 GPIO/中断
```

设计约束：

- PVDF 不用于测静态网张力；
- 比较器路径只负责低延迟候选触发，不能替代 ADC 波形证据；
- ADC1 初始为 16 kHz，20 ms 预触发、80 ms 后触发，每路最多 1600 点；
- 保护和偏置必须保证最大冲击不会把 ESP32-S3 ADC 输入推到危险电压；
- 左、右通道分别记录峰值、能量、持续时间和波形引用；
- 安静基线在启动自检和每次安装后采集，阈值从基线加裕量开始。

## 10 路 M6 NPN 光电输入

```text
M6 发射器 × 10 ── 对射光路 ── M6 接收器 × 10
                                      │ BN/BU/BK
                                 10 路 NPN 开集电极
                                      │
                           每路 R_IN + 光耦隔离
                                      │
                              3.3 V 上拉 + GPIO
```

- 每路独立输出，禁止用低速逐路轮询或把十路 BK 并联代替并行采集；
- 发射端只按卖家确认的 BN/BU 供电，接收端 BK 经过额定的 `R_IN + 光耦`，不得把 10–30 V 节点直接接 ESP32-S3 GPIO；
- 首样参考拓扑、`1.8 kΩ/1 W` 输入电阻、3.3 V 侧上拉、测试点和功耗边界见 [`m6-npn-interface-v0.1.zh-CN.md`](m6-npn-interface-v0.1.zh-CN.md)；
- 5 ms 只表示状态变化到输出完成变化的响应语义；1–10 ms 已知脉冲的输入/输出波形必须按 [`docs/m6-response-time-validation-v0.1.zh-CN.md`](../../docs/m6-response-time-validation-v0.1.zh-CN.md) 留档；
- 接收前端必须考虑环境光、球网白边反射、邻道串扰和光耦/线缆传播延迟；
- 每路都需要启动自检：发射端断开、接收端偏移、持续遮挡和正常对准至少要能区分；
- 光学座提供 z 轴偏航、y 轴俯仰和 x 轴滚转微调，参考线提供机械高度复核；
- 只有 `+10…+100 mm` 的 10 根有效光束参与业务事件。

## ESP32-S3 接口边界

本工程采用单个 ESP32-S3 主控，左右两侧通过线缆接入。`firmware/main/net_sensor_config.h` 中的 GPIO/ADC、RGB 和蜂鸣器引脚只是首轮占位映射，必须在最终 PCB 和 SmartPaddle 既有引脚约束确认后替换。

业务层不依赖 BLE、Wi-Fi、MQTT、SSE 或 WebSocket；通信层只消费序列化后的 `NetEvent`。SmartPaddle 的 WebSocket、配网、连接管理和 App 集成沿用既有基础设施，不在本仓库复制一套。

## 需要实测后冻结的项目

1. PVDF 夹片的机械预紧量与最佳贴合位置；
2. AFE 的输入保护、偏置电压、增益、带通频段和比较器迟滞；
3. 光电二极管有效距离、调制频率、接收增益和阳光/室内灯抗扰；
4. 10 根光束之间的串扰、实际球体遮挡宽度和 M6 5 ms 响应对应的最小输入/输出脉宽（按 [`docs/m6-response-time-validation-v0.1.zh-CN.md`](../../docs/m6-response-time-validation-v0.1.zh-CN.md) 留存波形）；
5. 采样缓存、GPIO 中断负载和最终板级引脚复用。

板级 hook、逻辑通道顺序、fail-closed 规则和可运行 CSV 回放见 [`docs/sensor-interface-v0.1.zh-CN.md`](../../docs/sensor-interface-v0.1.zh-CN.md)；实物装配、逐光束自检、PVDF 原始波形和断链补发按 [`docs/field-validation-record-template.zh-CN.md`](../../docs/field-validation-record-template.zh-CN.md) 留档；第一次接板按 [`bring-up-v0.1.zh-CN.md`](bring-up-v0.1.zh-CN.md) 顺序执行。
