# 乒乓智配首轮实现审计

本文只记录当前仓库能被复核的证据，不把主机测试或 OpenSCAD 编译结果当作实体硬件验收，也不提交比赛级精度承诺。

## 已由当前仓库证明

| 范围 | 当前证据 |
| --- | --- |
| 当前内置球网支架 CAD | `hardware/cad/net_stand.scad` 支持 `assembly`、左右单侧结构检查件、两段约 `153 mm` 的立柱分件、接缝外套筒/内芯、固定 C 形夹体、台底可动压块、M8 螺杆/旋钮、3 段搭接网顶承载条、2 片带孔拼接片和两侧承托/端挡座、带每 10 mm 实际贯穿定位孔/刻度的光学导轨、10 个带正交调节长孔的光学模块载台、参考线端座/定位销、PVDF 薄膜/两侧可拆压片、独立 PVDF 安装座和标定规；首轮参数为球台宽度 `1525 mm`、网顶 `152.5 mm`、光栅 `+10…+100 mm`、M8 竖直夹紧螺杆；`validate_net_stand.py` 编译当前 PART、检查左右镜像、台边跨接、螺杆/压块均低于台面底面、3 段网顶承载条覆盖全跨度、承托座跨过立柱内侧并到达网顶高度、接缝拼接片索引、参考端座落在选定档位、全部 10 个载台档位、薄膜被压片包住、装配包络，并拒绝 9 路光栅、+55 mm 非法参考高度和不存在的载台索引。 |
| 历史外挂 X 夹具 CAD | `hardware/cad/net_post_x_clamp.scad` 和旧验证脚本保留在历史边界，用于设计回溯与旧几何回归；它不再是当前机械主线。 |
| CAD 几何关系 | `validate_net_stand.py` 从当前 OpenSCAD 参数探针读取网顶高度、光栅档位、立柱外置位置、网跨度和支架顶部余量；`preview.py`、`render_net_stand_preview.py` 提供当前内置支架的正视/侧面和 OpenSCAD 实体可视证据。 |
| 光栅业务 | 10 位 `beam_mask`、最低/最高命中光束、安静结束、超时边界、逐通道位图和高度区间均有主机测试；采集器保留跨事件时间边界，事件结束后迟到的旧边沿会形成 invalid/unknown，不会伪造新的有效高度。 |
| PVDF 业务 | 双通道合并、20 ms 预触发、80 ms 后触发、峰值/能量/持续时间、完整/不完整波形归档和超时释放均有主机测试；冷启动时预触发历史不足即使后窗口采满也保持 incomplete；ESP32 主循环先处理比较器边沿再派发下一批 ADC，且 DMA 时间戳仍早于触发点的 backlog 样本会回填当前帧预触发尾部；启动快照会按每路历史样本时间戳筛掉触发点之后及窗口之外的旧样本，避免主循环延迟污染预触发证据；迟到的旧样本、乱序样本和落在 80 ms 窗口外的样本不会被当作完整证据，乱序帧入队后还会清空滚动历史；空引用不会创建可回放帧；`piezo_waveform_hook.h` 为既有回放存储提供同步复制边界。 |
| 状态与质量 | `clean_over`、`touch_over`、`touch_no_cross`、`unknown`，以及标定、光栅健康、PVDF 基线、波形不完整、空/非有限波形特征、光栅/PVDF 跨事件乱序时间戳、健康快照在待决事件期间变化和 GPIO 队列溢出门均有测试；`sensor_self_test` 提供逐光栅报告、PVDF 安静基线和机械标定的 fail-closed 健康快照组合器，`sensor_health_gate` 还把板级快照实际应用到聚合器并覆盖可用、部分失败、不可用和坏 ID 路径；聚合器边界自身还会拒绝空校准 ID/越界健康位图，并在坏的光栅边界到达时收口旧 pending 事件。 |
| 输入边界保护 | 聚合器会拒绝非法 beam 位图/边界索引/反向时间边界、非法 PVDF sensor mask/时间顺序/非有限特征，并对极限时间戳使用饱和加法；ESP32 队列溢出时任务侧会丢弃溢出前残留边沿，聚合器同时清空旧 pending 候选并让下一条新事件保持 `unknown`，避免与新输入拼接；ADC DMA 只允许落在当前预触发时间窗内的迟到样本回填，窗口外旧样本和已闭合事件之后的旧样本不会进入下一帧滚动历史；直接 JSON 序列化也不会输出 `NaN`/负浮点字面量。反例已加入主机测试。 |
| 传输边界 | `NetEventDelivery` 支持断链缓存、有界覆盖、顺序补发、发送失败后保留事件；ESP32-S3 通过 `net_event_transport.h` 的两个弱 C hook 接 SmartPaddle 现有连接层；具体 `/ws` 适配示例与当前引脚冲突见 [`smartpaddle-integration-v0.1.zh-CN.md`](smartpaddle-integration-v0.1.zh-CN.md)。 |
| 固件构建 | ESP-IDF 5.5.1 / ESP32-S3 实际 `reconfigure + build` 通过，应用分区仍有余量。 |
| 契约与回归 | JSON Schema 正例/反例、CMake/CTest、ASan/UBSan 主机测试和可视预览均通过。 Schema 还限制 UUID-like `event_id`、10 mm 离散高度档位、每个 1…1023 光栅位图与最低/最高命中档位及球底间隔的对应关系、`touch_no_cross` 无光栅命中及擦网状态与传感器位图一致；主机测试遍历全部 1…1023 光栅位图。 |
| 实体几何可视证据 | `render_net_stand_preview.py` 从 `net_stand.scad` 渲染当前装配、左右支架、桌下夹持、光学导轨默认/镜像、单个光学载台、PVDF 安装座和标定规；旧 `render_openscad_preview.py` 单独保留历史方案渲染。两套渲染均由 CI 作为 artifact 保存。 |
| 现场证据门 | `docs/field-validation-record-v0.1.schema.json` 与 `tools/validate_field_record.py` 要求全部 M/B/S/T/E 编号存在；只有 `pending` 可以没有证据，`pass/fail` 必须引用 `evidence_root` 下真实文件；模板当前 19 项全部保持 `pending`，不冒充实机通过；逐项主机覆盖与实物缺口见 [`validation-coverage-v0.1.zh-CN.md`](validation-coverage-v0.1.zh-CN.md)。 |
| 可运行轨迹回放 | `firmware/host-tests/trace_replay.cpp` 读取固定 CSV，实际跑过光栅/PVDF/短波形采集/事件归并并输出 3 个 Schema 合法事件，`touch_over` 保留波形引用和持续时间；主机单元测试另覆盖“比较器先到、DMA 迟到预触发/后触发、完整帧回填后归并为 `touch_over`”的整条顺序路径；板级 hook 和实物记录边界见 `sensor-interface-v0.1.zh-CN.md` 与现场记录模板。 |
| 外部回放关联工具 | `tools/correlate_net_events.py` 支持 NetEvent JSONL/`JSON_EVENT` 行、外部时间标记 CSV、明确的微秒偏移和包含边界的匹配窗口；`tools/test_correlate_net_events.py` 覆盖偏移、窗口边界、默认元数据和畸形输入。它只做时间戳关联，不把外部视频结果当作本体判定。 |
| 接板操作边界 | `hardware/electronics/bring-up-v0.1.zh-CN.md` 固化上电、逐光栅、ADC、PVDF 基线和健康快照放行顺序；光栅发射、接收、清空基线、遮挡响应四个字段均会参与通道放行；该文档是现场执行清单，不被主机测试替代。 |
| 自动化入口 | `.github/workflows/validation.yml` 已配置主机/CTest/ASan/UBSan/Schema/预览、OpenSCAD 和 ESP32-S3/ESP-IDF 5.5.1 三个 job；最近一次推送的 GitHub Actions 结果以当前 commit 为准。 |

## 仍必须用实物证明

- PETG 内置支架的重复桌下安装、夹紧力、滑移、台面损伤、立柱倾斜、网布张力和 M8 螺杆行程；旧外挂 X 夹具的实物结论不迁移到当前主线；
- PVDF 夹片贴合、AFE 保护/偏置/增益/带宽、比较器阈值和旋钮/球网振动误报；
- 10 路调制红外发射器、光电二极管/TIA、环境光抑制、邻道串扰、球体遮挡宽度和逐通道对准；
- 最终 PCB 引脚复用、启动自检实际测量、机械参考线标定版本；
- SmartPaddle 工程中对传输/健康 hook 的强实现、真实 WebSocket/App 联调、断链补发；
- 单球连续分离、外部视频时间戳回放和目标球网型号兼容性。

以上项目对应 [`validation-matrix.zh-CN.md`](validation-matrix.zh-CN.md)，完成前不把设备描述为比赛裁判设备。
