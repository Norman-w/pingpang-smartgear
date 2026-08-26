# STM32G031K8U6 载板候选引脚表 v0.1

状态：`工程候选已选；寄存器绑定与参考 ELF/bin 已完成构建自检；PCB、DMA、波形和实机边沿证据仍 pending`。

这是从“候选列表”进入“可以画最小原型”的输入，不是量产放行。当前候选为 `STM32G031K8U6`，封装 `UFQFPN32`；机器可读版本见同目录的 `m6-capture-carrier-stm32g031k8-pinmap.example.json`，无 HAL 的端口生命周期外壳和可选 CMSIS 寄存器绑定见 [`firmware/carrier/stm32g031-reference/`](../../firmware/carrier/stm32g031-reference/)，校验命令为：

```text
python3 tools/validate_m6_carrier_stm32_pinmap.py
python3 tools/test_validate_m6_carrier_stm32_pinmap.py
```

官方依据：

- [STM32G031K8 产品页](https://www.st.com/en/microcontrollers-microprocessors/stm32g031k8.html)
- [STM32G031K8 数据手册](https://www.st.com/resource/en/datasheet/stm32g031k8.pdf)

数据手册给出该系列最高 `64 MHz`、`64 KB Flash`、`8 KB SRAM`、DMA、SPI 和 SWD；UFQFPN32 的 pinout 和 AF0 映射是本表的唯一引脚依据。`RESET_N` 直接接 `PF2-NRST`，不是把复位线冒充普通 GPIO。

## 1. 选择理由

- 10 路输入选用 `PA1/2/3/4/5/6/7/9/10/15`，对应 EXTI `1/2/3/4/5/6/7/9/10/15`，把 EXTI0 留给 CS；
- SPI1 使用 `PB0/PB3/PB4/PB5` 的 AF0，分别作为 `NSS/SCK/MISO/MOSI`，并把 `PB0/NSS` 映射到专用 EXTI0，保留固定 152-byte mode-0 从机事务；
- `PB8` 作为低有效 `IRQ_N`；`PA13/PA14` 保留 SWD；`PF2-NRST` 接主控低有效复位；
- 不为首样强行挤入 UART/状态灯，先保留 `PB1/PB2/PC6/PA12` 作为测试/后续扩展；SWD 是首样烧录和调试主入口；
- 采集实现仍采用“GPIO EXTI + 自由运行微秒定时器 + FIFO”，而不是轮询。十路同时边沿的 ISR 延迟、DMA 和 SPI TX 预装必须在最小板上实测后才能关闭选型闸门。

## 2. 载板引脚分配

| 信号 | MCU 引脚 | UFQFPN32 pin | EXTI/复用 | 方向 | 状态 |
| --- | --- | ---: | --- | --- | --- |
| `CARRIER_IN[0]` | `PA1` | 8 | EXTI1 | 输入 | pending |
| `CARRIER_IN[1]` | `PA2` | 9 | EXTI2 | 输入 | pending |
| `CARRIER_IN[2]` | `PA3` | 10 | EXTI3 | 输入 | pending |
| `CARRIER_IN[3]` | `PA4` | 11 | EXTI4 | 输入 | pending |
| `CARRIER_IN[4]` | `PA5` | 12 | EXTI5 | 输入 | pending |
| `CARRIER_IN[5]` | `PA6` | 13 | EXTI6 | 输入 | pending |
| `CARRIER_IN[6]` | `PA7` | 14 | EXTI7 | 输入 | pending |
| `CARRIER_IN[7]` | `PA9` | 19 | EXTI9 | 输入 | pending |
| `CARRIER_IN[8]` | `PA10` | 21 | EXTI10 | 输入 | pending |
| `CARRIER_IN[9]` | `PA15` | 26 | EXTI15 | 输入 | pending |
| `CARRIER_CS_N` | `PB0` | 15 | SPI1_NSS / AF0 + EXTI0 | 输入 | pending |
| `CARRIER_SCK` | `PB3` | 27 | SPI1_SCK / AF0 | 输入 | pending |
| `CARRIER_MISO` | `PB4` | 28 | SPI1_MISO / AF0 | 输出 | pending |
| `CARRIER_MOSI` | `PB5` | 29 | SPI1_MOSI / AF0 | 输入 | pending |
| `CARRIER_IRQ_N` | `PB8` | 32 | 普通 GPIO | 输出 | pending |
| `CARRIER_RESET_N` | `PF2-NRST` | 6 | 硬件 NRST | 输入/复位 | pending |
| `SWDIO` | `PA13` | 24 | SWD | 双向 | pending |
| `SWCLK` | `PA14` | 25 | SWD | 输入 | pending |

SmartPaddle 主控侧连接沿用 [载板接口文档](m6-capture-carrier-v0.1.zh-CN.md) 的 GPIO10/11/12/13/14/5 候选：`SCK/MOSI/MISO/CS_N/IRQ_N/RESET_N`。`RESET_N` 在主控侧必须以开漏或经过明确电平/复位器件驱动，不能让两个推挽输出相互顶住。

## 3. 还未放行的项目

1. 将已通过目标架构 compile-only 和参考 ELF/bin 链接自检的寄存器绑定、启动链和 PB0/EXTI0 CS 边沿接入最终 PCB，并证明 SPI1 从机 DMA 配置在 CS 期间不会替换 TX 缓冲；
2. 用 TIM2 或等效自由运行定时器完成 1 µs 量级时间戳，并测量十路同时边沿的 ISR 延迟、顺序和 FIFO 深度；
3. 测量 `IRQ_N → CS_N → 首字节 → CS_N release`，并完成复位原因/首帧/看门狗证据；
4. 画 UFQFPN32 首样 PCB，保留 SWD、每路 `TP_CARRIER_IN`、SPI/IRQ/RESET 测试点和隔离电源分区；
5. 未完成上述证据前，`kUseM6Carrier`、`kCarrierClockOffsetConfirmed` 和验收包 `carrier_integration` 继续保持关闭/pending。
