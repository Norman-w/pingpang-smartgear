# M6 十路边沿采集载板 MCU 选型与引脚预算闸门 v0.1

状态：`工程候选已选；STM32G031 无 HAL 参考固件已完成构建自检；MCU 量产放行、PCB 和实机载板证据仍 pending`。

本文件解决的是“可以开始画载板，但还不能把某个 MCU 伪装成已决定”的边界。机器可读的待确认清单见 [`m6-capture-carrier-mcu-selection.example.json`](m6-capture-carrier-mcu-selection.example.json)，可用下面的命令校验：

```text
python3 tools/validate_m6_carrier_mcu_selection.py
python3 tools/test_validate_m6_carrier_mcu_selection.py
```

## 1. 不可改变的载板契约

载板 MCU 不直接接收 M6 的 10–30 V NPN 输出；每一路必须先经过独立负载/光耦或等效隔离与 3.3 V 逻辑整形。MCU 只看到 10 路隔离后的数字输入，并负责：

- 对 10 路输入捕获上升沿和下降沿，不设置未经实测的去抖或最小脉宽过滤；
- 给每个边沿提供单调时间戳，目标时间分辨率为 `1 µs` 量级；
- 通过 3.3 V SPI 从机、mode 0、首样 `1 MHz`，发送预装的最大 `152 bytes` 事件帧；
- 在帧可读时拉低低有效 `IRQ_N`，接受主控低有效 `RESET_N`，并具备看门狗/安全复位；
- 保留可重复烧录、调试和首样测量入口，不能为了多挤出两根输入线而永久牺牲 SWD/JTAG/USB/UART；
- 把 FIFO 溢出、时间戳异常和复位原因显式报告给 ESP32-S3，不在载板上猜测球高或 `clean_over`。

当前主控侧 SPI/IRQ 候选分配、帧格式和 fail-closed 边界见 [`m6-capture-carrier-v0.1.zh-CN.md`](m6-capture-carrier-v0.1.zh-CN.md)。这里的 `152 bytes` 是已经实现并经主机测试的最大协议帧边界，不是说 MCU 必须用某一种 DMA API；具体实现要通过载板波形和最坏边沿突发验证。

## 2. 引脚和资源预算

| 资源 | 数量 | 属性 | 选型门 |
| --- | ---: | --- | --- |
| `CARRIER_IN[0..9]` | 10 | 隔离后的数字输入，双边沿时间戳 | 必须能处理十路同时变化；不能用单次轮询代替 |
| `SPI_SCK/MOSI/MISO/CS_N` | 4 | 3.3 V SPI 从机，mode 0 | 必须能在 CS 释放前保持预装 TX 缓冲 |
| `IRQ_N` | 1 | 载板 → ESP32-S3，低有效 | 中断产生和 SPI 帧准备顺序要能测量 |
| `RESET_N` | 1 | ESP32-S3 → 载板，低有效 | 上电默认安全、复位后首帧可识别 |
| `SWD/JTAG/USB 调试` | 至少 2 | 首样烧录、故障定位和固件更新 | 必须保留；不能只依赖一次性量产烧录 |
| `UART_TX/RX` | 0–2 | 可选日志/产测 | 推荐保留测试焊盘，必要时与调试接口复用 |
| `STATUS_LED` | 0–1 | 可选状态指示 | 仅用于 bring-up，不得占用关键输入 |

因此，必须 GPIO 预算是 `18` 根，带 UART、状态灯和产测余量建议按 `22` 根以上规划。这个数字只是接口数量预算，不等于某个封装可直接使用的 GPIO 数；最终还要排除电源、地、启动脚、晶振、调试复用、模拟专用脚和封装未引出的引脚。

时间资源同样要单独审计：至少需要一个自由运行的微秒计数基准、十路边沿捕获路径、SPI 从机接收/发送路径、FIFO 和看门狗。若采用“GPIO 中断读自由运行定时器”，必须用最坏十路同时边沿测量 ISR 延迟和乱序风险；若采用 PIO、定时器输入捕获或 DMA，必须把 FIFO 深度、溢出行为和调试日志一并验证。

## 3. 候选 MCU 对比

以下是进入首样评审的候选，不是采购指令：

| 候选 | 适合点 | 首样必须补的证据 | 当前倾向 |
| --- | --- | --- | --- |
| **RP2040** | 官方规格列出 30 个用户 GPIO、2 个 SPI 和 PIO；PIO 适合把十路并行输入做成确定性采集路径 | PIO 输入捕获程序、FIFO/DMA、SPI 从机预装 152-byte TX、复位/调试/量产烧录流程 | 倾向作为“时序优先”候选，未冻结 |
| **STM32G031K8** | ST 官方资料列出 Cortex-M0+、最高 64 MHz、64 KB Flash、8 KB RAM、DMA 和 SPI；`K8U6` 的 UFQFPN32 有足够的独立 EXTI 线和 SWD 余量 | 具体 `UFQFPN32` pinout、DMA/定时器分配、SPI 从机 TX 预装和 SWD 产测 | 当前工程候选，仍未量产放行 |
| **ESP32-C3** | 可复用 ESP-IDF、日志和 SPI 从机软件生态；官方 ESP-IDF 文档支持 SPI slave 和握手 GPIO | 152-byte 帧必须走 DMA；10 路输入的 ISR/FIFO 延迟、功耗/启动时间、无线功能是否值得引入 | 倾向作为“软件复用”候选，不是默认首选 |

RP2040 的 PIO 只是提供了值得验证的硬件路径，不代表本项目已经有可烧录的载板固件。STM32G031K8U6 的系列页面能力也不能替代选定封装的 pinout 审计。ESP32-C3 若不使用 DMA，官方文档的无 DMA 事务边界不足以直接承诺 `152 bytes`；不能因为主控侧已经是 ESP-IDF 就跳过这项验证。

官方资料入口：

- [Raspberry Pi RP2040 specifications](https://www.raspberrypi.com/products/rp2040/specifications/)
- [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
- [ST STM32G031K8 product page](https://www.st.com/en/microcontrollers-microprocessors/stm32g031k8.html)
- [STM32G031K8 datasheet](https://www.st.com/resource/en/datasheet/stm32g031k8.pdf)
- [Espressif ESP32-C3 SPI slave API](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-reference/peripherals/spi_slave.html)

## 4. 选型放行顺序

1. **工程候选**：当前先以 `STM32G031K8U6 / UFQFPN32` 作为成本/简单度方向的工程候选；这不是已下单的量产决定。
2. **封装 pinout 复核**：具体分配见 [`m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md`](m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md) 和机器可读 JSON；仍需按实物封装、启动脚、电源、SWD 和 DMA 工程复核。
3. **采集路径原型**：用选定 MCU 的最小板或开发板验证十路同时边沿、双边沿时间戳、FIFO 溢出和复位后的首帧。
4. **SPI 从机原型**：验证 ESP32-S3 主控的 mode 0 / 1 MHz / 152-byte 事务；载板在 IRQ 前预装 TX，测量 IRQ 到 CS、CS 到首字节和帧保持时间。
5. **联合时钟验证**：实现独立同步交换，记录载板时钟到 ESP32 `esp_timer` 的 offset 和漂移；在证据写入验收包前保持 `kCarrierClockOffsetConfirmed=false`。
6. **冻结 PCB rev**：只有上述证据和成本/供货决定都完成，才把 `mcu_model`、`package`、`pcb_revision` 从 `pending` 改为具体值，并开始十路 PCB 首样。

## 5. 当前结论

现在可以按 `STM32G031K8U6 / UFQFPN32` 画最小原型、使用 [`firmware/carrier/stm32g031-reference/`](../../firmware/carrier/stm32g031-reference/) 的寄存器绑定/启动链参考镜像，并继续做协议、隔离前端和机械线束并行工作；仍不能声称“载板已能制造”或“参考镜像已在实板运行”。下一件硬件证据是用最小原型证明十路边沿采集和 152-byte SPI 从机事务。验收包的 `carrier_integration` 保持 `pending` 是有意的放行门，不是遗漏。
