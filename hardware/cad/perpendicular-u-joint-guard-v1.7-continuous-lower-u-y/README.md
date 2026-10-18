# v1.7：沿蓝色下管 Y 轴连续延长原下部 U 结构

本候选直接基于 v1.5，不引用任何 v1.6 模型。灰色上管沿 X，蓝色下管沿 Y，Z 向上。

## 连续拉长的实际实现

`prolonged_lower_u()` 直接复用原始 `u_plate(y0,y1)`，把同一个 U 形抱脚/底扣截面一次连续生成到新的全长：

- 前侧从 `Y=+10..+21` 改为 `+10..+33`；原 11 mm 深度增加 12 mm，成为 23 mm。
- 后侧从 `Y=-21..-10` 改为 `-33..-10`；同样连续加长 12 mm。
- 内侧面仍为 `Y=±10`，中央 20 mm 通道不变；下部 X 外宽仍为 30.8 mm，没有沿灰管 X 方向加块。
- 新生成的长 U 与原结构在整个原 11 mm 区间实体重叠，Y=±21 不是断缝或另一个独立零件。

下部截取范围为 `Z=-21..+0.5`，总高 21.5 mm。原蓝管仍为 `Z=-20..0`，原 1.5 mm 内扣仍为 `Z=-21..-19.5`。上方多出的 0.5 mm 复用原 U 板在 Z=0 处的实心上部过渡，因此延长段顶面高于蓝管顶面 0.5 mm；没有平移蓝管或卡扣。

主实体保留 v1.5，合并连续加长的长 U 后，再做 Ø16 全深度螺帽通行孔与原灰管直套让位的最终切除。四个上宽下窄三角阴角填充块保持原定义。

## 检查结果

| 检查 | 实际结果 |
|---|---|
| 原段 Y=15.5 与延长段 Y=27 的下部截面差 | 空 |
| 后段 Y=-15.5 与延长段 Y=-27 的下部截面差 | 空 |
| 原 v1.5 实体被移除的材料 | 空 |
| 原底扣区域改变 | 空（CGAL） |
| 四个三角块材料缺失 | 空 |
| Ø16 通行孔内阻塞 | 空；检测用 Ø15.999 排除重合面 |
| 预装螺帽/螺杆连续 Z 行程 0..52 mm 阻挡 | 空 |
| 灰管连续 Z 行程 0..52 mm 刚性阻挡 | 空（CGAL） |
| 蓝管运动与非卡扣材料的体积干涉 | 0；仅 Z=0 顶部接触面，诊断残面的 Z 厚度为 0 |

诊断中的零厚度接触面不是可打印零件，也不作为主 STL 的失败判据。主 STL 使用 CGAL 导出并独立检查：432 个三角面、216 个顶点，watertight=True；退化面、边界边、非流形边、方向不一致边均为 0。单位为 mm，整件包围盒 54.8 × 66 × 50 mm，体积约 46521.625 mm³。

原内扣向蓝管内伸约 0.6 mm 的弹性干涉保留，并沿 Y 连续加长。PETG 卡臂的实际撑开、压入力和回弹仍需首件验证；本次没有做材料弹性仿真。

## 真实 SCAD 渲染和主文件

- [等轴装配图，打印件统一为橙色，带 XYZ 坐标](../review/perpendicular-u-joint-v1.7-continuous-lower-u-y/01-continuous-u-assembly.png)
- [YZ 长度/高度剖面，原结构与连续延长段](../review/perpendicular-u-joint-v1.7-continuous-lower-u-y/02-yz-length-height-dimensions.png)
- [v1.5 与 v1.7 对照](../review/perpendicular-u-joint-v1.7-continuous-lower-u-y/03-v1.5-v1.7-y-comparison.png)
- [延长段 Y=27 的 XZ 端部截面，含蓝管与底扣](../review/perpendicular-u-joint-v1.7-continuous-lower-u-y/04-new-segment-xz-profile.png)
- [下部 XY 剖面，标出原端面 ±21 与新端面 ±33](../review/perpendicular-u-joint-v1.7-continuous-lower-u-y/05-lower-xy-continuity.png)
- [主 STL](../exports/perpendicular-u-joint-v1.7-continuous-lower-u-y/perpendicular-double-u-guard-v1.7-continuous-lower-u-y.stl)
- [主 STL 检查文件](../review/perpendicular-u-joint-v1.7-continuous-lower-u-y/stl-inspection.json)

所有图片均由本目录真实 SCAD 和 OpenSCAD CLI 渲染。旧版保留；未制作 3MF，未提交或推送。
