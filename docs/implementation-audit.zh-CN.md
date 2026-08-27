# 乒乓智配首轮实现审计

> 说明：本文保留的是旧版 10 路离散光栅/10 mm 导轨与 STG-120ML 方案的历史审计记录。当前硬件主线已改为用户指定的 M6 十路光电器件、10×56×216 mm PETG 主体、后盖 x 背面中央加厚 1/4-20 boss 和竖直采购球头直连商品网夹；商品球头上端固定螺纹为 1/4-20 外牙，下端默认选择 M8 外牙，后盖/立柱分别使用隐藏的 1/4-20/M8 捕获螺母；下表中的旧版光栅/光纤“已证明”内容不代表当前采购件已经提供逐点位图。当前判断以 `docs/m6-optical-array-design-v0.1.zh-CN.md`、`docs/m6-aluminum-machining-spec-v0.1.zh-CN.md`、`docs/net-height-device-design.zh-CN.md` 和 `hardware/cad/net_stand.scad` 为准。

本文只记录当前仓库能被复核的证据，不把主机测试或 OpenSCAD 编译结果当作实体硬件验收，也不提交比赛级精度承诺。当前 M6 调整接口已收口为后盖 x 背面中央加厚 boss + 竖直采购 13 mm 球头直连商品网夹；主体和球头/网夹尺寸仍要结合收货实物冻结。

本文件的历史审计表保留了旧 `optical_rail`/STG-120ML 文字，便于追溯；当前机械证据以 20 个 M6 直角器件、10×56×216 mm PETG 主体、后盖 x 背面中央加厚 boss、前后分体壳/底盖、采购球头直连商品网夹、十条单列光轴和两根独立 PETG 卡网圆柱为准，旧光学托架/3.87 mm 标定规不属于当前采购或电气验收链。当前现场执行项见 [`docs/m6-optical-array-design-v0.1.zh-CN.md`](m6-optical-array-design-v0.1.zh-CN.md)、[`docs/m6-aluminum-machining-spec-v0.1.zh-CN.md`](m6-aluminum-machining-spec-v0.1.zh-CN.md)、[`docs/field-validation-record-template.zh-CN.md`](field-validation-record-template.zh-CN.md) 和 [`hardware/electronics/bring-up-v0.1.zh-CN.md`](../hardware/electronics/bring-up-v0.1.zh-CN.md)。

## 当前 M6/三轴主线可复核证据

| 范围 | 当前证据与边界 |
| --- | --- |
| M6 机械阵列 | `hardware/cad/net_stand.scad` 的当前 `m6_detector_body`、`m6_sensor_array` 和 `m6_detector_mount` 定义左右各 10 个 M6×0.75 直角器件、`+10…+190 mm` 高度通道、20 mm 节距、10×56×216 mm PETG 长条主体、浅 x 向六角座、单枚主体外表面螺帽、尾线 -45° 让位、后盖 boss/y± 桥接肋和两侧镜像装配；`validate_net_stand.py` 已通过左右结构、20 mm 节距、分体壳/底盖、boss 孔和采购球头接口验证。它证明的是参数化 CAD，不是 20 枚实物已经到货或光学中心已一致。 |
| M6 主体与球头承力连接 | 当前输入记录 10×56×216 mm PETG 长条、后盖 x 背面中央加厚 boss、Ø7.0 x 向 1/4-20 外牙通孔与隐藏捕获螺母、boss 根部 y± 实体桥接肋、以及竖直采购 13 mm 球头直连商品网夹；球头下端默认 M8 外牙进入浅黄色下段 Ø24/Ø8.6 顶装承座并压住标准 M8 螺母，前后盖/底盖只做保护和让位；`export_m6_machining_spec.py` 生成带源 SHA-256 的 JSON，`test_m6_machining_spec.py` 校验 x/y/z 方向、boss 孔和采购件承力边界；`export_m6_machining_previews.py` 只生成左右主体 STL，`export_m6_component_previews.py` 另生成主体、前盖、后盖、底盖左右共 8 个完整封闭 STL，`test_m6_component_previews.py` 校验镜像、包围盒和拓扑。该输入仍不是最终打印/加工放行图，商品网夹接口、球头螺纹和实物配合必须现场复核。 |
| 5 ms 语义 | `docs/vendor/m6-laser-opposed/SELLER-CONFIRMATION.zh-CN.md`、`docs/m6-response-time-validation-v0.1.zh-CN.md` 和验收 JSON 已记录商家回复：5 ms 是状态变化到输出变化完成的响应语义，不是连续遮挡 5 ms 的最低门槛；最小输入脉宽、输出脉宽和短球遮挡漏检仍待波形实测。 |
| M6 电气边界 | `hardware/electronics/m6-npn-interface-v0.1.zh-CN.md`、`hardware/electronics/m6-capture-carrier-v0.1.zh-CN.md`、`hardware/electronics/m6-capture-carrier-mcu-selection-v0.1.zh-CN.md`、`hardware/electronics/m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md`、`firmware/carrier/stm32g031-reference/m6_carrier_stm32g031_port.*`、`firmware/carrier/stm32g031-reference/m6_carrier_stm32g031_register_port.*`、`firmware/carrier/stm32g031-reference/m6_carrier_stm32g031_startup.cpp`、`firmware/carrier/stm32g031-reference/stm32g031k8u6.ld`、`firmware/host-tests/test_m6_carrier_stm32g031_port.cpp`、`tools/validate_m6_interface.py`、`tools/validate_m6_carrier_mcu_selection.py`、`tools/validate_m6_carrier_stm32_pinmap.py`、`net_sensor_config.h` 和 `beam_channel_map.cpp` 已把 NPN 三线、隔离前端候选、独立边沿采集载板、带 CRC/序号/本地时间戳的 10 路输入协议、`CLOCK_SYNC_REQUEST/RESPONSE` 两事务 t2/t3、`M6CarrierClockCalibration` 多样本运行时校准门、`smartgear_board_read_m6_carrier_clock_sync()` 板级注入口、10–30 V 边界、STM32G031K8U6/UFQFPN32 工程 pin map、18/22 根 GPIO 预算、原始输入 bit→逻辑高度排列、fail-closed 极性门、无 HAL 端口契约、CMSIS 寄存器绑定和最小参考启动链固定；当前参考 pin map 让 `PB0/NSS` 取得专用 EXTI0，十路输入使用 `PA1/2/3/4/5/6/7/9/10/15`，不再依赖 CS 轮询；端口测试覆盖精确 pin map、初始化顺序、10 路 EXTI、1 MHz/SPI1-DMA TX staging、事件/同步 IRQ/CS、复位、短事务和输入歧义失败闭锁；寄存器绑定已用 Homebrew `arm-none-eabi-g++ 16.2.0`、ST 官方 device header 和 ARM CMSIS-Core 做目标架构 object compile-only 验证，参考 ELF/bin 也已无未解析符号并导出；无参 CS 释放路径会校验 RX/TX DMA 计数一致性，DMA/SPI 错误中断 fail-closed。参考镜像不等于最终实板放行；常开/常闭、负载能力、光耦型号、载板 PCB、逐通道接线顺序、同步事务电气波形、时钟漂移和主控侧波形尚未确认。 |
| 当前验证 | 本地已通过 OpenSCAD `NET_STAND_OK`、M6 规格/组件导出与独立预览测试、M6 验收/通道模板校验、MCU 选型闸门校验、载板 FIFO/TX 预装/IRQ-CS/十路同时边沿 host 测试、主机测试、CTest、ASan/UBSan、20 件 PETG 打印包、2 张 256 mm 拼盘（长轨和一体下段超尺寸单独标注）和当前预览渲染；这些结果不能替代 M/B/S/T/E 实物证据、最终 MCU/PCB 或联合 target。 |

## 历史方案证据（不计入当前 M6 完成判定）

| 范围 | 当前证据 |
| --- | --- |
| 当前内置球网支架 CAD | `hardware/cad/net_stand.scad` 支持 `assembly`、左右单侧结构检查件、两段约 `153 mm` 的立柱分件、下段与固定 C 形夹一体的 `lower_stand_segment`、接缝外套筒/内芯、固定上夹板与桌面之间的可替换保护垫、台底可动压块、带圆头且不穿入压块的加长 M8 螺杆、固定下臂 M8 螺母窝、带两枚预先对锁 M8 螺母捕获窝和 18 齿圆角锯齿握持圈的旋钮、桌面夹持开口外侧沿 y 全深的实心桥体与 40→12 mm 实心渐变下部支撑、上下结构夹臂均 12 mm、名义总宽 `1830 mm` 的 3 段搭接网顶承载条、2 片带孔拼接片和两侧承托/端挡座、可单独导出的 `optical_rail`、带每 10 mm 实际贯穿定位孔/刻度的光学导轨、光轴覆盖球台边缘的 10 个带正交调节长孔光学模块载台、带打印间隙贯穿销孔的参考线端座/定位销、PVDF 薄膜/两侧可拆压片、独立 PVDF 安装座和标定规；`optical_strip` 仅用于装配预览；首轮参数为球台宽度 `1525 mm`、网柱外边界离台边 `152.5 mm`、网顶 `152.5 mm`、夹体外轮廓名义外伸 `160 mm`（项目下限 `130 mm`，对应 ITTF T2 水平部分上限）、光栅 `+10…+100 mm`、相对原包络加长 `12 mm` 的 M8 竖直夹紧螺杆；`validate_net_stand.py` 编译当前 PART、检查左右镜像、独立打印零件 STL 的封闭边拓扑、18/25/30 mm 台厚下的免打孔路径、台边跨接、光学导轨处于立柱实体外、上表面保护垫包络、实心桥体/渐变支撑与 C 形夹下部重叠、圆头螺杆/压块/固定下臂单枚螺母/旋钮两枚对锁螺母的装配包络与叠层均低于台面底面、3 段网顶承载条覆盖全跨度、承托座跨过立柱内侧并到达网顶高度、接缝拼接片索引、参考端座和定位销贯穿端座/导轨并落在选定档位、全部 10 个载台档位、薄膜被压片包住、下段一体打印件包络和装配包络，并拒绝 9 路光栅、+55 mm 非法参考高度、无打印间隙的销孔和不存在的载台索引；`assembly`、左右单侧结构和其它组合 PART 明确只做装配/重叠 PNG 预览，不作为打印 STL。 |
| 历史外挂 X 夹具 CAD | `hardware/cad/net_post_x_clamp.scad` 和旧验证脚本保留在历史边界，用于设计回溯与旧几何回归；它不再是当前机械主线。 |
| CAD 几何关系 | `validate_net_stand.py` 从当前 OpenSCAD 参数探针读取网顶高度、光栅档位、网柱外边界 `+152.5 mm`、名义网架跨度 `1830 mm`、夹体名义外伸 `160 mm`、实心渐变支撑和支架顶部余量；`preview.py`、`render_net_stand_preview.py` 提供当前内置支架的正视/侧面和 OpenSCAD 实体可视证据。 |
| 光栅业务 | 10 位 `beam_mask`、最低/最高命中光束、安静结束、超时边界、逐通道位图和高度区间均有主机测试；采集器保留跨事件时间边界，事件结束后迟到的旧边沿会形成 invalid/unknown，不会伪造新的有效高度。 |
| PVDF 业务 | 双通道合并、20 ms 预触发、80 ms 后触发、峰值/能量/持续时间、完整/不完整波形归档和超时释放均有主机测试；冷启动时预触发历史不足即使后窗口采满也保持 incomplete；ESP32 主循环先处理比较器边沿再派发下一批 ADC，且 DMA 时间戳仍早于触发点的 backlog 样本会回填当前帧预触发尾部；启动快照会按每路历史样本时间戳筛掉触发点之后及窗口之外的旧样本，避免主循环延迟污染预触发证据；迟到的旧样本、乱序样本和落在 80 ms 窗口外的样本不会被当作完整证据，乱序帧入队后还会清空滚动历史；空引用不会创建可回放帧；`piezo_waveform_hook.h` 为既有回放存储提供同步复制边界。 |
| 状态与质量 | `clean_over`、`touch_over`、`touch_no_cross`、`unknown`，以及标定、光栅健康、PVDF 基线、波形不完整、空/非有限波形特征、光栅/PVDF 跨事件乱序时间戳、健康快照在待决事件期间变化和 GPIO 队列溢出门均有测试；`sensor_self_test` 提供逐光栅报告、PVDF 安静基线和机械标定的 fail-closed 健康快照组合器，`sensor_health_gate` 还把板级快照实际应用到聚合器并覆盖可用、部分失败、不可用和坏 ID 路径；聚合器边界自身还会拒绝空校准 ID/越界健康位图，并在坏的光栅边界到达时收口旧 pending 事件。 |
| 输入边界保护 | 聚合器会拒绝非法 beam 位图/边界索引/反向时间边界、非法 PVDF sensor mask/时间顺序/非有限特征，并对极限时间戳使用饱和加法；ESP32 队列溢出时任务侧会丢弃溢出前残留边沿，波形采集器同时丢弃当前帧和尚未交给业务层的 ready 帧，聚合器清空旧 pending 候选并让下一条新事件保持 `unknown`，避免与新输入拼接或跨边界归档；ADC DMA 只允许落在当前预触发时间窗内的迟到样本回填，窗口外旧样本和已闭合事件之后的旧样本不会进入下一帧滚动历史；直接 JSON 序列化也不会输出 `NaN`/负浮点字面量。反例已加入主机测试。 |
| 传输边界 | `NetEventDelivery` 支持断链缓存、有界覆盖、顺序补发、发送失败后保留事件；ESP32-S3 通过 `net_event_transport.h` 的两个 C hook 接入连接层，`smartpaddle_ws_transport_adapter.cpp` 已提供定义宏并链接 SmartPaddle `ws_data_server` 后的 `/ws` 强实现；具体目标契约、引脚冲突和联合 target 验收见 [`smartpaddle-integration-v0.1.zh-CN.md`](smartpaddle-integration-v0.1.zh-CN.md)。 |
| 固件构建 | 本轮通过已有 ESP-IDF `v5.5.1`/`esp32s3` 配置目录执行 `cmake --build firmware/build --parallel`，包含 `m6_carrier_spi.cpp`、两事务时钟同步和可选 SmartPaddle adapter 的 `pingpang_smartgear.bin` 成功链接，应用分区余量约 54%；独立 ESP32-S3 载板参考工程同样成功构建，应用分区余量约 79%。直接用 v5.5.1 `idf.py` 重配置会受到本机仅安装 `esp-15.2.0` 而 v5.5.1 要求 `esp-14.2.0` 的工具链版本门阻止，因此不把新建 v5.5.1 build 目录冒充为重新配置证据。STM32G031 的无 HAL 端口外壳通过 host/CTest/ASan/UBSan 回归，CMSIS 寄存器绑定已用 `arm-none-eabi-g++ 16.2.0` + ST/ARM 官方头文件做目标架构 object compile-only 验证；可选参考目标已完成启动文件、链接脚本、无 libc 运行时补丁的 ELF/bin 链接自检（text 13,088 bytes、bss 1,436 bytes、无未解析符号）。该结果证明源码和参考启动链能被目标编译器解析，不替代最终 PCB 引脚、传感器极性和烧录/上电实测。 |
| 契约与回归 | JSON Schema 正例/反例、CMake/CTest、ASan/UBSan 主机测试和可视预览均通过。 Schema 还限制 UUID-like `event_id`、10 mm 离散高度档位、每个 1…1023 光栅位图与最低/最高命中档位及球底间隔的对应关系、`touch_no_cross` 无光栅命中及擦网状态与传感器位图一致；主机测试遍历全部 1…1023 光栅位图，并由 `test_runtime_chain_with_delivery()` 串起比较器→ADC 波形→光栅归并→NetEvent JSON→断链缓存/补发。 |
| 实体几何可视证据 | `preview.py` 生成无 OpenSCAD 的当前意图图，`test_preview_consistency.py` 对照 `net_stand.scad` 检查 130 个直接首样参数；`render_net_stand_preview.py` 从 `net_stand.scad` 渲染当前装配、左右支架、桌下夹持、桌板剖面免打孔受力路径、带孔旋钮、可打印光学导轨、光学装配预览、单个光学载台、PVDF 安装座和标定规；旧 `render_openscad_preview.py` 单独保留历史方案渲染。两套渲染均由 CI 作为 artifact 保存。 |
| 现场证据门 | `docs/field-validation-record-v0.1.schema.json` 与 `tools/validate_field_record.py` 要求全部 M/B/S/T/E 编号存在；只有 `pending` 可以没有证据，`pass/fail` 必须引用 `evidence_root` 下真实文件；模板当前 19 项全部保持 `pending`，不冒充实机通过；逐项主机覆盖与实物缺口见 [`validation-coverage-v0.1.zh-CN.md`](validation-coverage-v0.1.zh-CN.md)。 |
| 可运行轨迹回放 | `firmware/host-tests/trace_replay.cpp` 读取固定 CSV，实际跑过光栅/PVDF/短波形采集/事件归并并输出 3 个 Schema 合法事件，`touch_over` 保留波形引用和持续时间；主机单元测试另覆盖“比较器先到、DMA 迟到预触发/后触发、完整帧回填后归并为 `touch_over`”的整条顺序路径；板级 hook 和实物记录边界见 `sensor-interface-v0.1.zh-CN.md` 与现场记录模板。 |
| 外部回放关联工具 | `tools/correlate_net_events.py` 支持 NetEvent JSONL/`JSON_EVENT` 行、外部时间标记 CSV、明确的微秒偏移和包含边界的匹配窗口；`tools/test_correlate_net_events.py` 覆盖偏移、窗口边界、默认元数据和畸形输入。它只做时间戳关联，不把外部视频结果当作本体判定。 |
| 接板操作边界 | `hardware/electronics/bring-up-v0.1.zh-CN.md` 固化上电、逐光栅、ADC、PVDF 基线和健康快照放行顺序；光栅发射、接收、清空基线、遮挡响应四个字段均会参与通道放行；该文档是现场执行清单，不被主机测试替代。 |
| 自动化入口 | `.github/workflows/validation.yml` 已配置主机/CTest/ASan/UBSan/Schema/预览、OpenSCAD 和 ESP32-S3/ESP-IDF 5.5.1 三个 job；最近一次推送的 GitHub Actions 结果以当前 commit 为准。 |

## 当前仍必须用实物证明

- PETG 内置支架的重复桌下安装、夹紧力、滑移、台面损伤、立柱倾斜、网布张力、M8 螺杆/固定下臂螺母/每侧两枚旋钮对锁螺母的实际锁固和行程；旧外挂 X 夹具的实物结论不迁移到当前主线；
- PVDF 夹片贴合、AFE 保护/偏置/增益/带宽、比较器阈值和旋钮/球网振动误报；
- 20 个 M6 发射/接收器、实际螺纹/外径/光学中心、环境光抑制、邻道串扰、球体遮挡宽度和逐通道对准；
- 最终 PCB 引脚复用、启动自检实际测量、机械参考线标定版本；
- SmartPaddle 工程中对传输/健康 hook 的强实现、真实 WebSocket/App 联调、断链补发；
- 单球连续分离、外部视频时间戳回放和目标球网型号兼容性。

以上项目对应 [`validation-matrix.zh-CN.md`](validation-matrix.zh-CN.md)，完成前不把设备描述为比赛裁判设备。
