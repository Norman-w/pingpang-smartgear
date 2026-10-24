# 围挡脚限位卡：版本与交付索引

这是围挡限位卡的独立工作，不替代本目录的球网/立柱主线。当前零件几何为 **v1.15**：下卡臂加厚至 7 mm，斜筋下收成 Y 向棱，连接处补实并统一倒角。实物抗踢强度仍待验证。

## 当前可用入口

- [v1.15 源码与数字验证](perpendicular-u-joint-guard-v1.15-tapered-unified/README.zh-CN.md)。
- [v1.15 六件黑色 PETG 正式打印包](print-packages/barrier-clip-v1.15-6x-black-PETG/README.zh-CN.md)：一板六件，房盖向上、内扣朝下；沿用实际首件 0.20 mm / 6 墙 / 30% gyroid / 自动树状支撑。预计 16h13m10s / 388.62g。
- [v1.15 等轴审图](review/perpendicular-u-joint-v1.15-tapered-unified/01-tapered-iso.png)。

## 历史首件记录（v1.11，不是当前几何）

- [v1.11主SCAD](perpendicular-u-joint-guard-v1.11-fit-21xy-22z/fit_clearance_guard.scad)：X基准21并保留0.8打印间隙，实际内宽21.8；Y内距21；Z两层各22 mm；底扣厚1.5；立墙5；顶盖8；螺帽全深孔Ø16。
- [真实等轴审图](review/perpendicular-u-joint-v1.11-fit-21xy-22z/01-assembly.png)与[几何说明](perpendicular-u-joint-guard-v1.11-fit-21xy-22z/README.md)。
- [实际首件工程与已切片包](print-packages/barrier-clip-v1.11-first-article/README.zh-CN.md)：**采用用户翻转后的正放方向和树状支撑，不是之前顶盖朝下的准备版。** 两个一板，X1C、Generic PETG、6墙、30%gyroid，预计4h39m13s/108.87g。
- [离线时间对照](review/perpendicular-u-joint-v1.11-fit-21xy-22z/time-comparison/README.zh-CN.md)：仅研究，未采用其中的15%填充方案，未改正在打印的任务。

首件已由用户启动，尚无完成、取件、扣入、止转或强度验收结论。v1.11底扣比实际20 mm方管底低3.5 mm，必须实物确认地面空间。

## 历史版本如何使用

目录按原位置保留，避免破坏`use/include`依赖或已有图片引用。以下版本是设计过程档案，**不是推荐打印清单**；不要把某个旧README中的“当前”解读为本次交付。

| 阶段 | 源码目录 | 状态 |
|---|---|---|
| v0.1 | `rotating-foot-guard/` | 早期方案，已被后续替代 |
| v0.2 | `perpendicular-u-joint-guard/` | 早期双件方案，已被一体件替代 |
| v0.3–v0.6、v0.8 | 对应版本目录 | 方向、螺帽空间和壁厚修订档案 |
| v0.7 | `perpendicular-u-joint-guard-v0.7/` | 已采用基线，保留完整依赖 |
| v0.9–v1.2 | 对应sloped/full/continuous目录 | 斜墙候选档案，非最终结构 |
| v1.3–v1.5 | 三角填角、全深孔、直套让位目录 | 已采用依赖历史 |
| v1.6 X/Y | `perpendicular-u-joint-guard-v1.6-lower-*-extension/` | 未采用/撤回，勿打印 |
| v1.7 | `perpendicular-u-joint-guard-v1.7-continuous-lower-u-y/` | Z解释错误，已由v1.8替代 |
| v1.8 | `perpendicular-u-joint-guard-v1.8-lower-20plus1p5/` | 20+1.5基线 |
| v1.9–v1.10 | 镜像斜坡、全墙宽斜坡目录 | 已采用中间版本 |
| v1.11 | `perpendicular-u-joint-guard-v1.11-fit-21xy-22z/` | 历史实际首件与打印配方来源 |
| v1.12–v1.13 | flush-roof / edge-safe-label | 顶部让位、倒角、字样的依赖基线 |
| v1.14 | `perpendicular-u-joint-guard-v1.14-full-depth-ribs/` | 已撤回的宽底直立筋候选，勿打印 |
| v1.15 | `perpendicular-u-joint-guard-v1.15-tapered-unified/` | 当前六件试印几何，实物待验证 |

各阶段图片在`review/perpendicular-u-joint-*`或`review/rotating-foot-guard-v0.1`。v0.7遗留的`*-coordinate-thumbnail.svg*`只是早期非CAD示意档案，不是精确模型或当前渲染证据；当前入口采用真实SCAD渲染图。

## 归档与忽略边界

- 源代码、历史说明、审图、当前实际可编辑3MF、当前原生已切片3MF、当前STL、时间对照及哈希清单纳入Git。
- `exports/`、`__pycache__/`和`.DS_Store`继续按现有.gitignore作为生成物/本地缓存；不通过扩大ignore隐藏本次源文件。
- 为避免仅保存在被忽略的exports里，相关历史导出完整封装为正式包内的`historical-generated-exports-REFERENCE-ONLY.zip`。它含被替代的STL/准备版3MF，只供追溯，不能代替实际首件入口。
- 临时五组切片比较的输入、输出、日志保存在正式包内的`offline-time-comparison-REFERENCE-ONLY.zip`，记录结果另外保存为文本；这些都是离线方案，没有发送打印。
- 正式包中的`archive-inventory.json`列出本任务归档文件的SHA256，验证SCAD相对依赖、ZIP条目及实际包的两件单板/参数/网格一致性。没有清除或覆盖旧设计。
