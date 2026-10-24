# v1.13 结构分区审图

本次仅增加着色审图，不改模型、配合尺寸、倒角、文字或打印文件。
`component_colors.scad` 直接调用原生 `edge_safe_guard.scad`，用互不重叠的空间分区着色，分区边界不是零件拼接缝。原件仍为一体打印件。

| 编号 | 颜色 | 部位 |
| --- | --- | --- |
| A | 橙色 | 顶盖与 X 两侧房檐，Z≥23 |
| B | 黄色 | 上半部实心墙，连接顶盖与卡臂的区域 |
| C | 紫色 | X 两侧房檐下的三角加强部分 |
| D | 绿色 | 沿 ±Y 方向延伸的斜坡加强部分 |
| E | 青色 | 下半部包住支撑脚的卡臂，Z=-22..0 |
| F | 红色 | 最底端完整 1.5 mm 层，包括向内的扣边，Z=-23.5..-22 |

深灰色字样为顶面 `Norman@PingCloud`。装配图中灰色为沿 X 的上方长管，蓝色为沿 Y 的下方脚；两根真实方管仍是 20×20，Z 向上。

表内尺寸为名义分界。为避免渲染器把贴在实体表面的零体积面显示成错色，实际着色分界偏移 0.001 mm；相邻区域共用同一分界，实体完整覆盖，模型没有削减或添加材料。

用户反馈实物有被踢坏的情况。此图用于定位断裂部位；尚未据此判断断裂原因，也没有实施加固或验证抗冲击性能。

## 真实 SCAD 等轴图

- [卡子分区图（移去方管便于观察）](../review/perpendicular-u-joint-v1.13-edge-safe-label/03-component-colors-iso.png)
- [带方管的装配分区图](../review/perpendicular-u-joint-v1.13-edge-safe-label/04-component-colors-assembly-iso.png)

渲染：OpenSCAD `--backend=Manifold --preview --autocenter --viewall --projection=o --camera=0,0,0,54.7356,0,45,210 --imgsize=1500,1250 --colorscheme=Tomorrow`；装配图另加 `-D 'VIEW="assembly"'`。每个着色分区先经 `render()` 进行实体布尔计算。
