# SmartPaddle 复用与接入边界 v0.1

> 当前硬件已切换为用户指定的 M6 直角十路光电器件阵列 + 10×56×216 mm PETG 长条主体/后盖 x 背面中央加厚 1/4-20 boss + 竖直采购球头直连商品网夹。本文提到的 10 路光栅位图和 GPIO 只是业务契约背景；在 M6 NPN 输出数量、电流、接口保护和最终引脚确认前，ESP32-S3/App 不得把机械十个通道位置当作已冻结的物理接口或有效高度数据。

本文记录网高工程与 SmartPaddle 的目标接入边界。参考 checkout 位于当前项目平级目录 `../SmartPaddle`，本次核对的 commit 为 `df3fb6b`。关键证据来自 `firmware/main/ws_data_server.h/.cpp`、`web/src/lib/deviceImuProtocol.ts`、`web/vite.config.ts`、`server/main.go`、`pcb/lib/esp32s3wroom1/pinmap.py` 和 `firmware/main/config.h`。本项目工作树仍不复制 SmartPaddle 固件/App；外部工程的压电板、引脚表或四路击球采集器也不能直接当成网高设备的硬件实现。

## 1. 已核对的 WebSocket 边界

参考 checkout 已实际提供以下 C 接口（声明见 `../SmartPaddle/firmware/main/ws_data_server.h`）：

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

本仓库的 [`firmware/main/smartpaddle_ws_transport_adapter.cpp`](../firmware/main/smartpaddle_ws_transport_adapter.cpp) 已把这段代码做成可选强实现：只有在联合 ESP-IDF target 定义 `SMARTGEAR_SMARTPADDLE_WS`、加入 SmartPaddle 的 `firmware/main` include path 并链接 `ws_data_server.cpp` 后才启用；默认 Pingpang 构建不复制 SmartPaddle 网络服务，仍使用弱 hook。`NetEventDelivery` 会在发送失败时解除发送状态并把原事件放进 16 条 RAM 环形缓存；连接恢复后按原事件 ID 顺序补发。

联合 target 的接入动作应在其 component CMake 中完成，最小形状如下；`ws_data_server.cpp` 依赖 SmartPaddle 自己的 HTTPD/Wi-Fi/存储组件，不能只把一个 `.cpp` 文件拷贝进 Pingpang：

```cmake
target_compile_definitions(${COMPONENT_LIB} PRIVATE SMARTGEAR_SMARTPADDLE_WS)
target_include_directories(${COMPONENT_LIB} PRIVATE
    "${SMARTPADDLE_ROOT}/firmware/main")
target_sources(${COMPONENT_LIB} PRIVATE
    "${PINGPANG_ROOT}/firmware/main/smartpaddle_ws_transport_adapter.cpp")
```

同时把 SmartPaddle 原有的 `ws_data_server.cpp`、其 include path 和依赖 component 保留在同一个最终 ESP-IDF target；构建通过后再做设备端 `/ws` 文本帧回环，不能以 host 编译或弱 hook 返回值代替联调。

参考固件在 `ws_data_server.cpp` 中注册设备端 `/ws`，并以单客户端状态保存连接；`ws_data_send_text()` 使用 ESP-IDF HTTPD 异步文本帧发送。SmartPaddle Web 前端直连设备时也默认使用 `ws://<device>/ws`，开发服务器的 `/device/ws` 代理会去掉 `/device` 后转发到同一路径。另一个 `server/main.go` 中的 `/ws/paddle` 是 Go 服务端接收端点，不能把它误写成 ESP32 设备端路径。上面的适配器不改变既有配网、Wi-Fi 或 App 的连接流程；MQTT、SSE 和 BLE 适配器也只需实现同一组传输语义，不应进入 `NetEventAggregator`。

## 2. 当前硬件不能直接共用的部分

以下是从参考 checkout 的 S3 pinmap/config 与 Pingpang 当前占位映射得到的冲突清单：

| GPIO | SmartPaddle 参考板实际用途 | Pingpang 当前占位 | 当前结论 |
| --- | --- | --- | --- |
| GPIO 4、6、7、8、9 | PZT ADC 窥探、PZT 比较器和电池采样 | 10 路光束占位包含 GPIO 4、6、7、8、9 | 直接冲突，且采样/前端不同 |
| GPIO 1、2 | PZT ADC 窥探（硬件跳线可选） | PVDF ADC 占位 GPIO 1、2 | 直接冲突，且采样/前端不同 |
| GPIO 15 | PZT 比较器 | PVDF 比较器占位 GPIO 15 | 直接冲突 |
| GPIO 16 | PZT 比较器 | 反馈红灯占位 GPIO 16 | 直接冲突 |
| GPIO 17、18 | PZT MCP4728 I²C | 反馈绿灯/蓝灯占位 GPIO 17、18 | 直接冲突 |
| GPIO 19、20 | USB D−/D+ | 反馈蜂鸣器占位包含 GPIO 19 | 直接冲突，且 USB 不能占用 |
| GPIO 21、40、41、47、48、0、43、44 | LED、IMU、保持供电、用户键、启动/调试 UART | Pingpang 占位或未来接口可能复用 | 必须保留并做最终 PCB 审计 |
| GPIO 35、36、37 | N16R8 OPI PSRAM | 未使用 | 不可用于传感器 |

因此，不能只修改 `net_sensor_config.h` 就把当前 Pingpang 固件直接烧进参考 SmartPaddle 主板。10 路光束 + 2 路 PVDF 需要独立传感器载板/线束和重新审计的 GPIO 资源；当前推荐的载板接口、SPI 引脚候选、带时间戳事件帧和边界规则见 [`hardware/electronics/m6-capture-carrier-v0.1.zh-CN.md`](../hardware/electronics/m6-capture-carrier-v0.1.zh-CN.md)。若保留 SmartPaddle 的 PZT/IMU/USB/电源功能，应评估额外 GPIO、硬件输入锁存/串行采集器或第二 MCU。对于 1–4 ms 短脉冲验收，普通 I²C 轮询扩展器不能未经时序实测就作为等价替代。

可重复执行的只读核对命令是 `python3 tools/validate_smartpaddle_reference.py`；当前 `--strict` 有意报告失败，因为它用于阻止把现有占位引脚直接接到 SmartPaddle 参考板。

## 3. 健康与波形强实现

WebSocket 适配不负责伪造传感器状态。目标 SmartPaddle 或网高设备的板级状态层需要强实现：

- `smartgear_board_read_sensor_health()`：返回校准 ID、10 路健康位图、PVDF 安静基线和校准有效标记；
- `smartgear_board_read_m6_carrier_clock_sync()`：在独立载板同步事务完成后提供主控/载板四个微秒时间戳，并只有在板级证据已核对时才把 `exchange_verified` 置为 true；弱 hook 默认不可用，不能用静态 offset 代替实测同步；
- `smartgear_board_on_piezo_waveform()`：在同步调用返回前复制波形指针；完整帧和超时帧都要记录；
- 未实现、返回失败或快照形状非法时，业务层保持 `unknown`，不能把网络已连接误当成传感器已标定。

参考 SmartPaddle 当前 `PiezoCapture::sample_adc_peaks()` 是诊断用 one-shot 采样，它不满足网高设备的 16 kHz、20 ms 预触发 + 80 ms 后触发要求。网高设备必须保留本工程的 ADC1 continuous/DMA 适配，或由新的板级采集器提供等价的双通道样本流。

## 4. 接入验收顺序

1. 在不接真实传感器的情况下，用本仓库 host test 的 fake send sink 验证 `NetEventDelivery` 的断链、发送失败、顺序补发和不重复。
2. 在参考 SmartPaddle 的 `/ws` 适配层或目标 App 的强 hook 中发送一条 Schema 合法的 `NetEvent`，确认文本帧可被 `deviceWsSingleton.ts` 接收；不要发到 Go 服务端的 `/ws/paddle`，除非另外实现该服务端的消息兼容。
3. 接入目标传感器板后，再按 [`hardware/electronics/bring-up-v0.1.zh-CN.md`](../hardware/electronics/bring-up-v0.1.zh-CN.md) 完成 GPIO、光栅、PVDF 和健康快照放行。
4. 最后才把 `calibration_valid` 与 `beam_health_valid` 置为 true，并执行现场记录模板中的 T-01/T-02。

当前代码已经具备“可选 `/ws` 强适配 + 业务事件边界”，但在联合 target 编译、设备端 `/ws` 文本帧回环、传感器健康快照和真实球验收完成前，不能声明已经完成 SmartPaddle 实机联调。
