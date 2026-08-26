# M6/M4 直角对射供应商资料归档

本目录保存用户上传的供应商图片原件，作为本项目的设计输入快照。图片中的 M3/M4/M5、反射型、PNP 和常闭型号是供应商可选项；当前项目指令只采用 **M6 直角对射、0–20 m、NPN**。

## 来源记录

- 商品页：[淘宝 item 1071628886139](https://item.taobao.com/item.htm?id=1071628886139&skuId=6122579349941)
- 用户选定的采购 SKU：`6122579349941`（已保存为采购目标；不等于卖家已确认的型号后缀）
- 归档日期：2026-08-25
- 原始图片：[`source-images/`](source-images/)
- 图片为用户提供的资料，不代表本仓库已经向卖家下单，也不替代实物量测或卖家书面确认。

## 当前采用的资料

| 文件 | 内容 |
| --- | --- |
| `01-size-options.png` | M3/M4/M5/M6/M8 直头和弯头规格总览 |
| `02-wiring-npn-pnp.png` | NPN/PNP 三线接线图 |
| `03-m3-reference-dimensions.png` | M3 直头/对射尺寸参考 |
| `04-m6-right-angle-dimensions.png` | M6 直角尺寸；当前“对射”条目为 M6×0.75，另一个“反射”条目为 M6×0.5；8 mm/14 mm 包络 |
| `05-m3-right-angle-dimensions.png` | M3 直角尺寸参考 |
| `06-m5-right-angle-dimensions.png` | M5 直角尺寸参考 |
| `07-m4-right-angle-dimensions.png` | M4 直角尺寸参考 |
| `08-reflection-parameter-table.png` | 反射型型号和通用参数表 |
| `09-opposed-parameter-table.png` | 对射型型号和通用参数表，含 `VJTL06-20NZ` 等 |

## 从图片读出的 M6 直角对射记录

- 用户采购目标：SKU `6122579349941`，M6 直角对射、NPN、0–20 m。图片型号表的 `VJTL06-20NZ`（常开）和 `VJTL06-20N3`（常闭）只作为型号映射候选，不能替代该 SKU 的卖家确认。
- M6 直角对射安装螺纹：`M6×0.75`；同图直角反射安装螺纹为 `M6×0.5`，不要混用。
- 图示头部高度约 `8 mm`，安装杆包络约 `14 mm`，截面横向约 `10 mm`。
- 总览图对 M6L 给出约 `22 mm` 的横向参考和约 `39 mm` 的竖向参考；这两项在加工前按实物复核。
- 通用参数表给出：`10–30 V DC`、响应 `5 ms`、IP65、304 不锈钢、标准线缆 `2 m`、最大负载电流 `150 mA`。
- NPN 图示：棕 `BN(1)` 接 `+V`，蓝 `BU(3)` 接 `-V`，黑 `BK(2)` 接负载/NO 开集电极输出。

## 商家对 5 ms 的回复（用户转述，2026-08-25）

用户向商家确认：“被测信号变化到传感器输出真正完成变化需要 5 ms；是否不要求物体必须持续遮挡 5 ms 才能检测？”商家回复“是的”，本仓库将其记录为：**5 ms 是状态变化到输出完成变化的响应时间语义，不是商家声明的最小连续遮挡时间。**

这条回复仍不能证明 1–4 ms 的短遮挡一定会产生可捕获的 NPN 脉冲。最小输入脉宽、上升/下降沿分别的最大响应时间、输出脉宽和内部滤波仍需用示波器/逻辑分析仪实测；不能仅凭“5 ms 响应”关闭高速乒乓球漏检风险。实测步骤见 [`../../m6-response-time-validation-v0.1.zh-CN.md`](../../m6-response-time-validation-v0.1.zh-CN.md)。

下单前逐项发给商家的确认话术和收货证据清单见 [`SELLER-CONFIRMATION.zh-CN.md`](SELLER-CONFIRMATION.zh-CN.md)。

收货后的总验收入口是 [`acceptance-bundle.example.json`](acceptance-bundle.example.json)：它把 SKU、20 只器件、载板 MCU/PCB、SPI/IRQ/时钟同步/SmartPaddle 回环、M6 实测螺纹/包络/线缆尺寸、三轴机械记录、八个遮挡脉宽批次、10 路通道映射和四类真实球路径集中起来；模板保持 `pending`，不会把设计或主机测试自动升级为实物通过。

验收包还固定记录了卖家已经确认的 5 ms 语义：这是输入状态变化到 NPN 输出完成变化的时间，不是“连续遮挡 5 ms 才能检测”；最小输入脉宽仍保持未知，必须用真实波形关闭。

验收校验器还会阻止把 `procurement.model_status` 改成 `pass` 却继续保留
`seller_model=pending/TBD/待确认`；SKU 后缀必须有实际卖家/发货证据后才能放行采购区。

收到器件后可先创建一份不覆盖旧目录的运行骨架：

```text
python3 tools/init_m6_acceptance_run.py --output-dir evidence/<run-id>
python3 tools/validate_m6_acceptance_bundle.py evidence/<run-id>/acceptance-bundle.json
```

初始化命令只复制 `pending` 模板和 1/2/3/4/5/6/8/10 ms 八张 CSV 表头，不生成任何通过证据。

## 采购与电气待确认

1. 淘宝 SKU `6122579349941` 的最后一个选项实际对应什么型号，以及是常开还是常闭；
2. 10 个发射器和 10 个接收器是否分开包装，独立 NPN 输出到底有几路；
3. M6×0.75 的有效螺纹长度、配套螺母对边尺寸、头部防转平面和光学中心到螺纹轴的偏置；
4. 黑线输出的负载接法、输出低电平电流、电源共地方式和线缆弯曲半径；
5. 10–30 V 传感器电源必须经过光耦/电平转换后进入 M6 边沿采集载板，载板再以 3.3 V SPI 接 SmartPaddle/ESP32-S3；不能把黑线直接接到 3.3 V GPIO。

机械设计记录见 [`../../m6-optical-array-design-v0.1.zh-CN.md`](../../m6-optical-array-design-v0.1.zh-CN.md)。
