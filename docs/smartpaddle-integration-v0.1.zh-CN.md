# SmartPaddle 复用与接入边界 v0.1

> 当前硬件已切换为 STG-120ML 两段光纤头 + 配套放大器。本文提到的 10 路光栅位图和 GPIO 只是早期接口兼容背景；在放大器输出语义和电流确认前，ESP32-S3/App 不得把它当作已冻结的物理接口或有效高度数据。

本文把本机 SmartPaddle 工程中已经存在的能力与本工程的新增业务边界对齐。这里复用的是 ESP32-S3、时间戳、连接管理、配网和 App 多设备的模式；不把 SmartPaddle 当前的压电板、引脚表或四路击球采集器直接当成网高设备的硬件实现。

## 1. 当前可直接复用的 WebSocket 边界

当前 SmartPaddle 固件已经提供以下 C 接口：

```cpp
bool ws_data_has_client(void);
esp_err_t ws_data_send_text(const char* data, size_t len);
```

网高业务层的 `firmware/main/net_event_transport.h` 只需要一个强实现即可完成首个 WebSocket 适配：

```cpp
#include <cstring>
#include "esp_err.h"
#include "ws_data_server.h"

extern "C" bool smartgear_board_transport_connected() {
    return ws_data_has_client();
}

extern "C" bool smartgear_board_transport_send_json(const char* json) {
    return json != nullptr &&
           ws_data_send_text(json, std::strlen(json)) == ESP_OK;
}
```

这段代码是接入示例，不在本仓库复制 SmartPaddle 的网络服务。`NetEventDelivery` 会在发送失败时解除发送状态并把原事件放进 16 条 RAM 环形缓存；连接恢复后按原事件 ID 顺序补发。

SmartPaddle 当前 WebSocket 服务端 URI 是 `/ws`，上面的适配器使用已有服务端，不改变配网、Wi-Fi 或 App 的连接流程。MQTT、SSE 和 BLE 适配器也只需实现同一组传输语义，不应进入 `NetEventAggregator`。

## 2. 当前硬件不能直接共用的部分

本机 SmartPaddle 当前板级实现的压电比较器/诊断资源大致为：

| 资源 | SmartPaddle 当前用途 | 网高设备首轮占位 | 结论 |
| --- | --- | --- | --- |
| GPIO 15、16、6、7 | 4 路 PZT 比较器 | 2 路 PVDF 比较器 GPIO 14、15 | 有冲突，不能直接共用引脚表 |
| GPIO 1、2、4、8 | PZT ADC 峰值诊断 | 2 路 ADC1 连续波形 GPIO 1、2 | 采样模式不同，不能把 one-shot 峰值当短波形 |
| GPIO 17、18 | MCP4728 阈值 DAC I²C | 首轮未冻结 | 需要单独确认板级资源 |
| GPIO 40、41 | IM948 UART | 网高设备未使用 | 可作为复用工程的既有约束参考 |

因此，网高设备首轮应使用独立的传感器载板/线束和最终确认的 ESP32-S3 引脚表。SmartPaddle 的 PZT 前端、四路 `PiezoCapture` 和 GPIO 配置不能未经重新布线就接入 10 路光栅与双 PVDF。

## 3. 健康与波形强实现

WebSocket 适配不负责伪造传感器状态。SmartPaddle 或网高设备的板级状态层需要强实现：

- `smartgear_board_read_sensor_health()`：返回校准 ID、10 路健康位图、PVDF 安静基线和校准有效标记；
- `smartgear_board_on_piezo_waveform()`：在同步调用返回前复制波形指针；完整帧和超时帧都要记录；
- 未实现、返回失败或快照形状非法时，业务层保持 `unknown`，不能把网络已连接误当成传感器已标定。

SmartPaddle 当前的 `sample_adc_peaks()` 是诊断用 one-shot 采样，不满足网高设备的 16 kHz、20 ms 预触发 + 80 ms 后触发要求。网高设备必须保留本工程的 ADC1 continuous/DMA 适配，或由新的板级采集器提供等价的双通道样本流。

## 4. 接入验收顺序

1. 在不接真实传感器的情况下，用本仓库 host test 的 fake send sink 验证 `NetEventDelivery` 的断链、发送失败、顺序补发和不重复。
2. 在 SmartPaddle/目标 App 的强 hook 中发送一条 Schema 合法的 `NetEvent`，确认文本帧可被 App 多设备层识别。
3. 接入目标传感器板后，再按 [`hardware/electronics/bring-up-v0.1.zh-CN.md`](../hardware/electronics/bring-up-v0.1.zh-CN.md) 完成 GPIO、光栅、PVDF 和健康快照放行。
4. 最后才把 `calibration_valid` 与 `beam_health_valid` 置为 true，并执行现场记录模板中的 T-01/T-02。

在上述步骤完成前，本工程只能声明“传输边界与业务事件可接入”，不能声明已经完成 SmartPaddle 实机联调。
