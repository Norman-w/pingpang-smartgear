# 乒乓智配首轮实现审计

本文只记录当前仓库能被复核的证据，不把主机测试或 OpenSCAD 编译结果当作实体硬件验收，也不提交比赛级精度承诺。

## 已由当前仓库证明

| 范围 | 当前证据 |
| --- | --- |
| X 型夹具 CAD | `hardware/cad/net_post_x_clamp.scad` 支持左右镜像、10°…20° 运动参数、Ø8 轴孔、M8 螺杆/滚柱/压盖、方杆、10 路导轨和参考线端座；`validate_scad.py` 编译 9 个 PART、镜像件、10°/20° 端点，并拒绝 25° 越界参数。 |
| CAD 几何关系 | `validate_geometry.py` 从 OpenSCAD 参数探针读取唯一参数源，检查 X 臂共线、内侧 V 槽到 Ø25 mm 立柱的包络、轴孔间隙、M8 行程和 10 mm 档位。 |
| 光栅业务 | 10 位 `beam_mask`、最低/最高命中光束、安静结束、超时边界、逐通道位图和高度区间均有主机测试。 |
| PVDF 业务 | 双通道合并、20 ms 预触发、80 ms 后触发、峰值/能量/持续时间、完整/不完整波形归档和超时释放均有主机测试。 |
| 状态与质量 | `clean_over`、`touch_over`、`touch_no_cross`、`unknown`，以及标定、光栅健康、PVDF 基线、波形不完整和 GPIO 队列溢出门均有测试。 |
| 传输边界 | `NetEventDelivery` 支持断链缓存、顺序补发、发送失败后保留事件；ESP32-S3 通过 `net_event_transport.h` 的两个弱 C hook 接 SmartPaddle 现有连接层。 |
| 固件构建 | ESP-IDF 5.5.1 / ESP32-S3 实际 `reconfigure + build` 通过，应用分区仍有余量。 |
| 契约与回归 | JSON Schema 正例/反例、CMake/CTest、ASan/UBSan 主机测试和可视预览均通过。 |

## 仍必须用实物证明

- PETG 夹具的重复安装、夹紧力、滑移、滚柱防脱、螺杆行程和 Ø25 mm 立柱兼容范围；
- PVDF 夹片贴合、AFE 保护/偏置/增益/带宽、比较器阈值和旋钮/球网振动误报；
- 10 路调制红外发射器、光电二极管/TIA、环境光抑制、邻道串扰、球体遮挡宽度和逐通道对准；
- 最终 PCB 引脚复用、启动自检实际测量、机械参考线标定版本；
- SmartPaddle 工程中对传输/健康 hook 的强实现、真实 WebSocket/App 联调、断链补发；
- 单球连续分离、外部视频时间戳回放和目标球网型号兼容性。

以上项目对应 [`validation-matrix.zh-CN.md`](validation-matrix.zh-CN.md)，完成前不把设备描述为比赛裁判设备。
