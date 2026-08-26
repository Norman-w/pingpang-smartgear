# 乒乓智配 · PingPang SmartGear

乒乓球训练与比赛相关的智能辅助装备、配件及识别系统。

本仓库采用软硬件一体化方式管理，目标是把乒乓球训练中的测量、校准、识别和比赛辅助能力做成可重复搭建、可验证、可扩展的设备。

## 当前项目

### 球网立柱夹持式过网高度检测设备

在球网两侧立柱边缘夹装可调高度的延长杆，在两根延长杆的同一刻度之间拉设参考线，并结合视觉识别检测乒乓球经过球网平面时的高度。

首个原型的工作结果预计包括：

- 球网两侧的夹持与快速拆装；
- 延长杆高度刻度和左右同步校准；
- 可更换、可识别的参考线；
- 球网平面和参考高度的标定；
- 乒乓球过网事件、过网高度、目标高度差和识别置信度；
- 为后续训练记录、智能球桌和比赛辅助系统提供统一数据接口。

当前阶段：**首样机械 CAD 与软件验证已完成；M6 实物、电气波形、装配对准和目标板联调待完成**。

当前光学机械主线改为用户选定商品 SKU `6122579349941` 对应的左右各一套 10 路 M6 直角对射 NPN 发射/接收器阵列。每侧器件安装在
铝合金梳齿安装条上，再通过水平 z 轴偏航转台、y 轴俯仰叉架和 x 轴滚转盘安装到网夹/立柱；
资料中的当前“对射”条目给出 M6×0.75、20 m 和约 8/14 mm 的直角包络（同一张图的“反射”条目另为 M6×0.5）；SKU 实际型号后缀、有效螺纹长度和输出数量仍需按卖家/实物确认，设计说明见
[`docs/m6-optical-array-design-v0.1.zh-CN.md`](docs/m6-optical-array-design-v0.1.zh-CN.md)。

## 仓库结构

```text
docs/       需求、技术方案、测量定义与测试记录
hardware/   夹具、延长杆、参考线、传感器安装和 CAD/BOM
firmware/   设备控制器、传感器采集和通信固件
vision/     球体检测、轨迹估计、过网高度计算
software/   标定工具、调试界面和训练/比赛数据接口
```

## 设计原则

1. **先建立可测量的基准**：每个高度结果都要能追溯到球网平面、刻度和标定过程。
2. **机械与识别解耦**：夹具和参考线即使脱离视觉系统，也能作为训练辅助工具使用。
3. **先做最小闭环**：先验证“安装 → 标定 → 识别 → 输出结果”，再扩展到复杂比赛场景。
4. **结果带置信度**：识别失败、遮挡或标定失效时，不输出看似精确的伪结果。

## 文档入口

- [首个原型说明](docs/net-height-device-design.zh-CN.md)
- [技术架构与数据接口](docs/sensor-interface-v0.1.zh-CN.md)
- [硬件工程说明](hardware/README.md)
- [M6 5 ms 响应/最小遮挡实测方案](docs/m6-response-time-validation-v0.1.zh-CN.md)
- [M6 十路 NPN 隔离前端参考设计](hardware/electronics/m6-npn-interface-v0.1.zh-CN.md)
- [M6 十路边沿采集载板接口与 SmartPaddle SPI 协议](hardware/electronics/m6-capture-carrier-v0.1.zh-CN.md)
- [M6 载板 MCU 选型与引脚预算闸门](hardware/electronics/m6-capture-carrier-mcu-selection-v0.1.zh-CN.md)
- [STM32G031K8U6 载板候选引脚表](hardware/electronics/m6-capture-carrier-stm32g031k8-pinmap-v0.1.zh-CN.md)
- [M6 载板首样 BOM 与画板输入](hardware/electronics/m6-capture-carrier-first-article-bom-v0.1.zh-CN.md)
- [M6 卖家下单确认单](docs/vendor/m6-laser-opposed/SELLER-CONFIRMATION.zh-CN.md)
- [M6 通道映射模板](docs/vendor/m6-laser-opposed/channel-map.example.json)
- [M6 总验收包模板](docs/vendor/m6-laser-opposed/acceptance-bundle.example.json)
- [M6 铝合金梳齿条/三轴基座加工输入](docs/m6-aluminum-machining-spec-v0.1.zh-CN.md)
- [M6 首样加工与装配放行包](docs/m6-first-article-release-v0.1.zh-CN.md)
- [视觉识别工程说明](vision/README.md)

## 适用范围

本项目当前面向训练、实验和产品研发。未经重复性、环境适应性和规则符合性验证的版本，不作为正式比赛裁判依据。
