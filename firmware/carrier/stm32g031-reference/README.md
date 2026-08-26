# STM32G031 载板端口外壳

这里是 `STM32G031K8U6 / UFQFPN32` 的平台适配边界，不依赖 STM32Cube 或厂商 HAL。目录同时提供两条路径：默认的寄存器级 object compile-only 检查，以及可选的最小无 HAL 参考镜像构建。后者包含启动文件、向量表、链接脚本和 freestanding 运行时补丁，可以导出 ELF/bin；它仍是“接口与启动链参考镜像”，不是已经通过首样 PCB、烧录上电和现场波形验收的量产固件。

现在另有一个可选的 [CMSIS 寄存器绑定](m6_carrier_stm32g031_register_port.cpp) 和 [CMake 入口](CMakeLists.txt)。它使用 ST 官方 `stm32g031xx.h` 的 EXTI、TIM2、SPI1、DMA1/DMAMUX1 寄存器定义，把端口外壳接到实际外设；本机已用 Homebrew `arm-none-eabi-g++ 16.2.0`、ST 官方 device header 和 ARM CMSIS-Core 做过目标架构 object compile-only 验证，并用同一套输入构建过参考 ELF/bin。参考镜像仍不会改变验收包的 `pending` 状态。

## 当前已收口的接口

`m6_carrier_stm32g031_port.*` 固化了 [候选 pin map](../../../hardware/electronics/m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md)：

- `PA1/2/3/4/5/6/7/9/10/15` → 10 路独立 EXTI 输入；
- `PB0/PB3/PB4/PB5` → SPI1 `NSS/SCK/MISO/MOSI`，mode 0；PB0 同时映射为专用 EXTI0 CS 边沿；
- `PB8` → 低有效 `IRQ_N`；`PA13/PA14` 保留 SWD；`PF2-NRST` 保留硬件复位；
- SPI 从机 TX 指针只在未进行 CS 事务时由 `service()` 更新，固定传输长度为 `152 bytes`；DMA transfer-error 与 SPI error IRQ 会把下一帧置为 `timestamp_invalid`；
- 无事件帧时 CS 事务接收 `CLOCK_SYNC_REQUEST`；载板在请求释放时记录 t2，在下一次响应 CS assertion 时记录 t3 并返回 CRC 保护的同步响应；
- CS 提前释放会把 `timestamp_invalid` 置到下一帧；复位会清空 FIFO、TX staging 和 IRQ 状态。

`PlatformHooks` 由真正的 STM32Cube LL/HAL 或寄存器代码实现。实际绑定时至少要完成：

1. GPIO 输入配置为双边沿 EXTI，并在 ISR 内读取自由运行的 `TIM2`（目标 1 µs）后调用 `on_input_edge()`；
2. SPI1 从机 mode 0 + DMA 使用 `tx_buffer()`，NSS/CS 边沿分别调用 `on_cs_asserted(timestamp_us)`/`on_cs_released()`；没有独立 CS EXTI 时可在主循环调用 `service_cs_level()`，它会用两个 DMA `CNDTR` 一致性检查计算事务字节数；无事件帧时同一入口接收时钟同步请求；
3. `configure_spi1_slave_dma()` 确认 DMA 不会在 CS 期间改写 TX buffer；
4. `drive_irq_n(true)` 代表释放高电平，`drive_irq_n(false)` 代表拉低通知主控；
5. 外部 `RESET_N` 让 MCU 重新启动，启动代码重新调用 `initialize()`，并保留复位原因/首帧日志。

寄存器绑定采用 [ST 的 STM32G0 CMSIS device header](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-g0/master/Include/stm32g031xx.h) 和 [STM32G0x1 reference manual RM0444](https://www.st.com/resource/en/reference_manual/rm0444-stm32g0x1-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) 作为依据；具体时钟树、输入保护、DMA 重装和 CS 边沿仍必须按最终板卡重新审查。

## 本地验证边界

```text
cmake -S firmware/host-tests -B firmware/host-tests/build
cmake --build firmware/host-tests/build --parallel
ctest --test-dir firmware/host-tests/build --output-on-failure
```

`m6_carrier_stm32g031_port_tests` 验证 pin map、初始化顺序、TX staging、事件/时钟同步 IRQ-CS 生命周期、短事务 fail-closed 和复位行为；它不能证明 STM32 中断延迟、DMA 波形、3.3 V 电平或 PCB 已通过。真实硬件证据仍按载板 [首样接口与验收门](../../../hardware/electronics/m6-capture-carrier-v0.1.zh-CN.md) 记录，验收包继续保持 `pending`。

## 可选的寄存器 object 构建

准备与目标芯片匹配的 ST CMSIS device `Include/`、CMSIS-Core `core_cm0plus.h` 和 `arm-none-eabi` 工具链后，只编译不链接：

```text
cmake -S firmware/carrier/stm32g031-reference \
  -B firmware/carrier/stm32g031-reference/build \
  -DCMAKE_SYSTEM_NAME=Generic \
  -DCMAKE_CXX_COMPILER=arm-none-eabi-g++ \
  -DSTM32_CMSIS_DEVICE_G0_INCLUDE_DIR=/path/to/cmsis-device-g0/Include \
  -DSTM32_CMSIS_CORE_INCLUDE_DIR=/path/to/CMSIS/Core/Include
cmake --build firmware/carrier/stm32g031-reference/build --parallel
```

交叉编译时必须使用带 C++ 标准头的 ARM 工具链；`CMAKE_SYSTEM_NAME=Generic` 用来避免 macOS 主机把 `-arch arm64` 传给 `arm-none-eabi-g++`。本机这次 object 验证还使用了 `-DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY`。如果工具链没有随附 C++ 标准头，可以通过 `STM32_CXX_EXTRA_INCLUDE_DIRS` 传入与目标 ABI 兼容的标准头目录。

`PB0` 的 NSS 仍由 SPI 外设使用，并由寄存器绑定映射到专用 EXTI0，因此参考镜像不依赖主循环轮询才能捕获 CS；`service_cs_level()` 仍保留给替代平台 glue。无论采用 EXTI 还是外部 glue，都必须实测 `IRQ_N → CS_N → 首字节 → CS_N release` 窗口；无参释放路径只在 RX/TX 两个 DMA 计数一致时接受长度，否则按短事务 fail-closed。DMA transfer-error 与 SPI error IRQ 已在寄存器绑定中启用，仍需板级波形证明。

## 可选的 STM32G031 参考 ELF/bin

在准备好 ST CMSIS device/core 头文件、`arm-none-eabi-g++` 和 C++ 标准头后，可以打开 `BUILD_FLASHABLE_REFERENCE`：

```text
cmake -S firmware/carrier/stm32g031-reference \
  -B /tmp/m6-stm32-reference \
  -DCMAKE_SYSTEM_NAME=Generic \
  -DCMAKE_CXX_COMPILER=arm-none-eabi-g++ \
  -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY \
  -DBUILD_FLASHABLE_REFERENCE=ON \
  -DSTM32_CMSIS_DEVICE_G0_INCLUDE_DIR=/path/to/cmsis-device-g0/Include \
  -DSTM32_CMSIS_CORE_INCLUDE_DIR=/path/to/CMSIS/Core/Include
cmake --build /tmp/m6-stm32-reference --parallel
```

构建产物为 `m6_carrier_stm32g031_reference`、`.bin` 和 `.map`。镜像包含最小向量表、`.data/.bss` 初始化、寄存器绑定主循环以及 M0+ 所需的无 libc 运行时/原子操作补丁；本地自检应继续确认 `arm-none-eabi-nm -u` 无未解析符号，并查看 `arm-none-eabi-size` 的 Flash/RAM 占用。它只证明“参考启动链可链接”，不能证明最终 PCB 的时钟、输入保护、DMA、CS/IRQ 波形或传感器边沿时序。
