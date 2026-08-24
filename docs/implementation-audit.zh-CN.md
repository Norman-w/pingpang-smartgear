# 乒乓智配首轮实现审计

本文只记录当前仓库能被复核的证据，不把主机测试或 OpenSCAD 编译结果当作实体硬件验收，也不提交比赛级精度承诺。

## 已由当前仓库证明

| 范围 | 当前证据 |
| --- | --- |
| X 型夹具 CAD | `hardware/cad/net_post_x_clamp.scad` 支持左右镜像、`SIDE=±1` 覆盖、10°…20° 运动参数、两臂 `7+2+7 mm` 上下错层、Ø8 轴孔、M8×1.25 螺杆/滚柱/压盖/螺母捕获、两侧真实三角肋、方杆、独立固定桥件、10 路导轨、带参考线贯穿孔的端座和 10 路光学模块包络；光栅定位孔与参考线端座孔为实际减料通孔，左右打印夹具不带装配预览立柱；V 槽硬体/可替换软垫、参考线端座本体/定位销均可分开导出；`validate_scad.py` 编译 19 个导出、检查左右/光学模块/jaw/guide STL 包围盒镜像、验证参考线端座全部 10 个档位并拒绝 +55 mm 越界高度、10°/20° 端点，并拒绝 25° 越界参数。 |
| CAD 几何关系 | `validate_geometry.py` 从 OpenSCAD 参数探针读取唯一参数源，检查 X 臂共线、内侧 V 槽到 Ø25 mm 立柱的包络、轴孔间隙、M8 行程和 10 mm 档位。 |
| 光栅业务 | 10 位 `beam_mask`、最低/最高命中光束、安静结束、超时边界、逐通道位图和高度区间均有主机测试。 |
| PVDF 业务 | 双通道合并、20 ms 预触发、80 ms 后触发、峰值/能量/持续时间、完整/不完整波形归档和超时释放均有主机测试；冷启动时预触发历史不足即使后窗口采满也保持 incomplete；ESP32 主循环先处理比较器边沿再派发下一批 ADC，且 DMA 时间戳仍早于触发点的 backlog 样本会回填当前帧预触发尾部；迟到的旧样本、乱序样本和落在 80 ms 窗口外的样本不会被当作完整证据，乱序帧入队后还会清空滚动历史；空引用不会创建可回放帧；`piezo_waveform_hook.h` 为既有回放存储提供同步复制边界。 |
| 状态与质量 | `clean_over`、`touch_over`、`touch_no_cross`、`unknown`，以及标定、光栅健康、PVDF 基线、波形不完整、空/非有限波形特征、乱序时间戳、健康快照在待决事件期间变化和 GPIO 队列溢出门均有测试；`sensor_self_test` 提供逐光栅报告、PVDF 安静基线和机械标定的 fail-closed 健康快照组合器，`sensor_health_gate` 还把板级快照实际应用到聚合器并覆盖可用、部分失败、不可用和坏 ID 路径；聚合器边界自身还会拒绝空校准 ID/越界健康位图，并在坏的光栅边界到达时收口旧 pending 事件。 |
| 输入边界保护 | 聚合器会拒绝非法 beam 位图/边界索引/反向时间边界、非法 PVDF sensor mask/时间顺序/非有限特征，并对极限时间戳使用饱和加法；ESP32 队列溢出时任务侧会丢弃溢出前残留边沿，聚合器同时清空旧 pending 候选并让下一条新事件保持 `unknown`，避免与新输入拼接；ADC DMA 只允许落在当前预触发时间窗内的迟到样本回填，窗口外旧样本会被丢弃；直接 JSON 序列化也不会输出 `NaN`/负浮点字面量。反例已加入主机测试。 |
| 传输边界 | `NetEventDelivery` 支持断链缓存、有界覆盖、顺序补发、发送失败后保留事件；ESP32-S3 通过 `net_event_transport.h` 的两个弱 C hook 接 SmartPaddle 现有连接层；具体 `/ws` 适配示例与当前引脚冲突见 [`smartpaddle-integration-v0.1.zh-CN.md`](smartpaddle-integration-v0.1.zh-CN.md)。 |
| 固件构建 | ESP-IDF 5.5.1 / ESP32-S3 实际 `reconfigure + build` 通过，应用分区仍有余量。 |
| 契约与回归 | JSON Schema 正例/反例、CMake/CTest、ASan/UBSan 主机测试和可视预览均通过。 Schema 还限制 UUID-like `event_id`、10 mm 离散高度档位、每个 1…1023 光栅位图与最低/最高命中档位及球底间隔的对应关系、`touch_no_cross` 无光栅命中及擦网状态与传感器位图一致；主机测试遍历全部 1…1023 光栅位图。 |
| 实体几何可视证据 | `hardware/cad/render_openscad_preview.py` 从同一份 SCAD 直接渲染双侧装配、左侧夹具、V 槽硬体、V 槽软垫、光学模块包络、参考线端座、端座可打印本体和标定规；左侧夹具单件为 manifold/no-error，八个视图均渲染成功，CI 将八张 PNG 作为独立 artifact 保存。 |
| 现场证据门 | `docs/field-validation-record-v0.1.schema.json` 与 `tools/validate_field_record.py` 要求全部 M/B/S/T/E 编号存在；只有 `pending` 可以没有证据，`pass/fail` 必须引用 `evidence_root` 下真实文件；模板当前 19 项全部保持 `pending`，不冒充实机通过。 |
| 可运行轨迹回放 | `firmware/host-tests/trace_replay.cpp` 读取固定 CSV，实际跑过光栅/PVDF/短波形采集/事件归并并输出 3 个 Schema 合法事件，`touch_over` 保留波形引用和持续时间；主机单元测试另覆盖“比较器先到、DMA 迟到预触发/后触发、完整帧回填后归并为 `touch_over`”的整条顺序路径；板级 hook 和实物记录边界见 `sensor-interface-v0.1.zh-CN.md` 与现场记录模板。 |
| 接板操作边界 | `hardware/electronics/bring-up-v0.1.zh-CN.md` 固化上电、逐光栅、ADC、PVDF 基线和健康快照放行顺序；光栅发射、接收、清空基线、遮挡响应四个字段均会参与通道放行；该文档是现场执行清单，不被主机测试替代。 |
| 自动化入口 | `.github/workflows/validation.yml` 已配置主机/CTest/ASan/UBSan/Schema/预览、OpenSCAD 和 ESP32-S3/ESP-IDF 5.5.1 三个 job；最近一次推送的 GitHub Actions 结果以当前 commit 为准。 |

## 仍必须用实物证明

- PETG 夹具的重复安装、夹紧力、滑移、滚柱防脱、螺杆行程和 Ø25 mm 立柱兼容范围；
- PVDF 夹片贴合、AFE 保护/偏置/增益/带宽、比较器阈值和旋钮/球网振动误报；
- 10 路调制红外发射器、光电二极管/TIA、环境光抑制、邻道串扰、球体遮挡宽度和逐通道对准；
- 最终 PCB 引脚复用、启动自检实际测量、机械参考线标定版本；
- SmartPaddle 工程中对传输/健康 hook 的强实现、真实 WebSocket/App 联调、断链补发；
- 单球连续分离、外部视频时间戳回放和目标球网型号兼容性。

以上项目对应 [`validation-matrix.zh-CN.md`](validation-matrix.zh-CN.md)，完成前不把设备描述为比赛裁判设备。
