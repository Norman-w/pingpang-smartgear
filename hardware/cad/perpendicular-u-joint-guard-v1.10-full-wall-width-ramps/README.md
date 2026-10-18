# v1.10：斜坡在 X 方向盖满立墙

仅纠正 v1.9 梅红斜坡的 X 宽度：22.8 → 30.8 mm，两侧各增加 4 mm，范围 X=-15.4..+15.4，与青绿色立墙外面齐平。沿 X 覆盖每侧完整 5 mm 墙厚，不额外伸出原外轮廓。

X 为灰管轴、Y 为蓝管轴、Z 向上；单位 mm。实际复用 v1.9 双斜坡，仅缩放 X，保留 YZ 轮廓：两端 |Y|=21 根部高10、|Y|=33 外端高3，各12 mm。底面 Z=0，连接体向下0.2 mm完全落在原立墙内。PETG 一体件仍从 +Z 向下安装，保留约0.6 mm弹性内扣及 Z=-21.5..-20 的1.5 mm底扣。

按 openscad-stl-print 流程进行真实 SCAD 渲染和独立 STL 检查：

- CGAL 主实体 Simple=yes；网格448面、224顶点，watertight=True。
- 退化面、边界边、非流形边、方向不一致边均0。
- 整体包围盒54.8×66×50.5 mm；体积51186.825280 mm³。
- CGAL 检查以下布尔结果均为空：v1.9材料被移除、Z<0下部改变、中央Y±10通道改变、Y=0镜像差、Ø15.999数值探针阻塞、灰管向下53 mm装入路径阻塞。实际通孔仍Ø16。
- v1.8/v1.9旧源文件保留未改。未生成3MF，未提交或推送。

数字检查不等于PETG实物装配、卡臂回弹或承载验收，需首件验证。

## 文件

- [主SCAD](full_wall_width_ramps_guard.scad)
- [等轴装配图](../review/perpendicular-u-joint-v1.10-full-wall-width-ramps/01-assembly.png)
- [XZ截面尺寸图](../review/perpendicular-u-joint-v1.10-full-wall-width-ramps/02-xz-full-wall-coverage.png)
- [XY截面图](../review/perpendicular-u-joint-v1.10-full-wall-width-ramps/03-xy-full-wall-coverage.png)
- [反向等轴图](../review/perpendicular-u-joint-v1.10-full-wall-width-ramps/04-reverse-assembly.png)
- [主STL](../exports/perpendicular-u-joint-v1.10-full-wall-width-ramps/perpendicular-double-u-guard-v1.10.stl)
- [STL检查报告](../review/perpendicular-u-joint-v1.10-full-wall-width-ramps/stl-inspection.json)

图中梅红表示完整斜坡，青绿表示原延长立墙。颜色仅用于审图，打印件是单件。所有图均由实际SCAD经OpenSCAD CLI渲染，未使用图片生成。
