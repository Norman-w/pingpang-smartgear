# v1.11 两件首件：实际正放 + 树状支撑

## 以这里的actual文件为准

- [可编辑工程](barrier-clip-v1.11-2x-upright-tree-actual.3mf)：从用户手动翻转后的Bambu Studio未保存工程原生另存。顶盖朝上、底扣在下，树状自动支撑；没有重新修改尺寸、墙数或填充。
- [原生单盘已切片包](barrier-clip-v1.11-2x-upright-tree-actual.gcode.3mf)：从同一已切片工程原生导出。单板两件，预计16753秒，即4h39m13s，108.87g（模型95g、支撑约13.87g），272层。
- [原CAD坐标STL](guard-v1.11-cad-coordinates.stl)：与v1.11源文件导出相同；不代表直接贴床姿态。
- `reference-roof-down-prepared-NOT-ACTUAL.3mf`：较早的倒置准备版，仅供对照，不是这次实际发送的版本。它会让1.5 mm水平内扣在上方成为悬挑；此前只核查支撑未进入配合区，不足以证明内扣可稳定无支撑成型，**不建议原样复打**。

本次任务在打印机上的名字仍为`barrier-clip-v1.11-2x-X1C-PETG-native`；为了归档而另存为actual名字不会重命名或改变已发送任务，也没有发送第二次任务。

## 实际配方与接受边界

X1 Carbon、0.4喷嘴、纹理PEI、A4灰色Generic PETG；0.20层高、6墙、30%gyroid、顶底各5层、树状自动支撑、仅从床生成、阈值45°；喷嘴255°C、床70°C。保留原XY补偿0。启动时用户自行操作打印，随后原生设备页观察到命名匹配的任务处于热床准备阶段（0/272层）。这里不将预热/执行等同打印完成或实物验收。

打印仍需首件检查底扣成型、回弹、实物松紧和止转效果，特别是Z放宽后底扣低于实际20 mm脚底3.5 mm的地面空间。用户最终决定“先这样”，因此没有采用减填充/加墙优化，没有暂停、取消或重新发送打印。

## 文件保全

历史SCAD/审图按原目录纳入Git，[总索引](../../BARRIER-GUARD-INDEX.zh-CN.md)明确各版状态。

`historical-generated-exports-REFERENCE-ONLY.zip`保留此前本任务被忽略的导出文件（不含.DS_Store等缓存）；`offline-time-comparison-REFERENCE-ONLY.zip`保留五组临时比较输入/输出/日志。两者是历史档案，不是当前打印入口。完整内容和所有归档文件的哈希见`archive-inventory.json`，可用`../../perpendicular-u-joint-guard-v1.11-fit-21xy-22z/audit_archive.py --verify`复核。
