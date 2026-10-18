# v1.6：下部 X 正负两端各延伸 12 mm

本候选基于 v1.5，采用用户最新确认的 X 方向。此前 Y 向试画已停用，未导出主 STL；本模型不引用它。

## 实际边界

- 新增块只属于打印件，不加长或移动灰色上管、蓝色下管、螺丝或螺帽。
- 下部负 X 外端：`-15.4 → -27.4`，外延 12 mm。
- 下部正 X 外端：`+15.4 → +27.4`，外延 12 mm。
- 新增块 Y 范围沿用前后 U 板：`-21..-10`、`+10..+21`；Y 外宽仍为 42 mm，中央通道仍为 20 mm。
- 延伸块 Z 范围按最新确认取 `-21..+0.5`，总高 21.5 mm。
- 每个块向原 U 臂搭入 X=0.1 mm，形成正体积连接。下部 X 外宽由 30.8 增至 54.8 mm，恰好与已有屋檐外宽一致，因此整件总包围盒 X 没有继续增加。

原蓝管仍为 Z=-20..0，原弹性底扣仍为 Z=-21..-19.5，厚 1.5 mm。它们重叠 0.5 mm，合并范围原本为 21 mm；为了实现确认的新增块高度 21.5 mm，只将新增块上沿设到 Z=+0.5，没有移动原管子或卡扣。

## 保留内容和验证

- v1.4 的全深度 Ø16 无台阶通行孔保留。
- v1.3 四个三角填充块的 XZ 轮廓保留，布尔检查没有缺失材料。
- v1.5 原实体没有被削减；底扣区域对比为空，允许的弹性卡扣干涉保留。
- 相对 Z 行程 0..52 mm 的上管刚性扫掠检查通过（CGAL 交集为空）。
- 预装螺丝/螺帽扫掠和 Ø16 孔内阻塞检查均为空。
- 排除允许的底扣区域后，蓝管扫掠与打印件没有刚性体积干涉。
- 左右镜像实体差检查通过（CGAL 差为空）。Manifold 对部分共面边界会输出零体积残面，采用 CGAL 复核后确认为空，不将诊断面的拓扑当成主模型拓扑。

主 STL 使用 CGAL 导出，再用独立脚本检查：448 个三角面、224 个顶点；watertight=True，退化面/边界边/非流形边/方向不一致边均为 0。单位按 SCAD 为 mm，整件包围盒为 54.8 × 42 × 50 mm，体积约 52392.025 mm³。

下部 U 臂增加材料后，弹性扣入所需的压入力、撑开与回弹仍需 PETG 首件验证；当前检查证明名义装配路径和网格，不是材料弹性仿真。

## 真实 SCAD 图与输出

- [等轴装配图，绿色新增材料](../review/perpendicular-u-joint-v1.6-lower-x-extension/01-x-extensions-isometric.png)
- [XZ 尺寸核对，12/12/21.5 mm](../review/perpendicular-u-joint-v1.6-lower-x-extension/02-xz-extension-dimensions.png)
- [v1.5 与 v1.6 对照](../review/perpendicular-u-joint-v1.6-lower-x-extension/03-v1.5-v1.6-x-comparison.png)
- [沿 X 端部剖面，核对 Y 通道](../review/perpendicular-u-joint-v1.6-lower-x-extension/04-x-end-yz-section.png)
- [下部俯视尺寸图](../review/perpendicular-u-joint-v1.6-lower-x-extension/05-lower-top-dimensions.png)
- [主 STL](../exports/perpendicular-u-joint-v1.6-lower-x-extension/perpendicular-double-u-guard-v1.6-lower-x-extension.stl)
- [主 STL 检查](../review/perpendicular-u-joint-v1.6-lower-x-extension/stl-inspection.json)

所有图片均由本目录 `review.scad` 引用真实源模型后，通过 OpenSCAD CLI 渲染；未使用图片生成。未制作 3MF，未提交或推送。
