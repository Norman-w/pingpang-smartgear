# v1.9：两端镜像实心斜坡

基于 v1.8 增加两块覆盖蓝管上沿的实心斜坡。蓝管沿 Y，灰管沿 X，Z 向上。斜坡高端都朝主体，低端都朝各自外缘。

## 两端实际轮廓

| 端部 | 外端 | 内端/主体端 | 高度变化 |
|---|---|---|---|
| 负 Y | `Y=-33, Z=3` | `Y=-21, Z=10` | 沿 +Y 靠主体：3 → 10 mm |
| 正 Y | `Y=+33, Z=3` | `Y=+21, Z=10` | 沿 +Y 向外：10 → 3 mm |

两端可见斜坡各长 12 mm，底面均为 Z=0，顶部沿 Y 线性变化。先在 YZ 平面构造长梯形截面，再沿 X 实心挤出，负端直接由正端关于 Y=0 镜像。

## X 范围与实体连接

候选斜坡宽 22.8 mm，范围 X=-11.4..+11.4。蓝管宽 20 mm；原 U 内宽 20.8 mm、侧墙内面 X=±10.4，因此斜坡覆盖蓝管并向两侧原墙各搭入 1 mm。原下部外宽 30.8 mm 和整件外宽 54.8 mm 都不增加。

根部向主体内搭入 0.2 mm（|Y|=20.8..21），保持根部高度 10 mm；侧墙连接体向下搭入 0.2 mm，仅占原有墙体范围。最终整体下部几何与 v1.8 相同，没有改变 20+1.5 内扣。主 STL 独立检查只有 1 个连通分量。

## 保持的 v1.8 基准

- 蓝管 Z=-20..0；侧壁贴管高 20 mm；内扣 Z=-21.5..-20，厚 1.5 mm。
- 下部 U 沿 Y 连续到 ±33，内侧面仍为 ±10，中央通道仍为 20 mm。
- 四个三角阴角、顶部屋檐、Ø16 全深无台阶螺帽通行孔、灰管直套让位均保留。
- 新增斜坡全部位于两端 |Y|≥20.8，中央孔和中央通道没有被占用。

## 实体及网格检查

| 检查 | 结果 |
|---|---|
| 关于 Y=0 的完整主实体镜像差 | 空（CGAL） |
| v1.8 被移除的材料 | 空 |
| Z<0 下部截面改变 | 空 |
| 中央 Y=-10..+10 通道内材料改变 | 空 |
| Ø16 孔内阻塞 | 空；数值检查采用 Ø15.999 mm |
| 预装螺帽/螺杆 0..53 mm 相对 Z 行程阻挡 | 空 |
| 灰管 0..53 mm 相对 Z 行程刚性阻挡 | 空（CGAL） |
| 蓝管与非卡扣材料的运动干涉 | 空（Manifold规则化） |
| 根部实体取样 | Y=21，顶面 Z=10，X 宽22.8 mm |
| 中段实体取样 | Y=27，顶面 Z=6.5，X 宽22.8 mm |
| 最外端实体顶点 | Y=33，顶面 Z=3 |

部分 Manifold 诊断曾输出共面零体积残面；CGAL 复核上管阻挡和镜像差均为空，没有将诊断残面当作主 STL。主 STL 使用 CGAL 导出并通过独立拓扑检查：464 个三角面、232 个顶点，1 个连通分量；watertight=True；退化面、边界边、非流形边、方向不一致边均为 0。单位 mm，包围盒 54.8 × 66 × 50.5 mm，体积约 49938.825 mm³。

剩余需要 PETG 首件确认的是斜坡与侧墙的实际连接强度、管子配合、卡扣压入力与回弹；当前没有进行材料弹性/承载试验。

## 真实 SCAD 图片与文件

颜色：橙色为原长度范围内主体，青色为 v1.8 连续延长墙，紫色为 v1.9 新增斜坡。颜色只用于审图，主 STL 是一个整体。

- [装配等轴图](../review/perpendicular-u-joint-v1.9-mirrored-end-ramps/01-mirrored-ramps-assembly.png)
- [+Y：内端10、外端3的YZ图](../review/perpendicular-u-joint-v1.9-mirrored-end-ramps/02-plus-y-10-to-3-profile.png)
- [-Y：外端3、内端10的YZ图](../review/perpendicular-u-joint-v1.9-mirrored-end-ramps/03-minus-y-3-to-10-profile.png)
- [端部XZ截面及22.8 mm宽度](../review/perpendicular-u-joint-v1.9-mirrored-end-ramps/04-end-xz-ramp-width.png)
- [中央孔/通道与v1.8对照](../review/perpendicular-u-joint-v1.9-mirrored-end-ramps/05-central-hole-channel-comparison.png)
- [反向等轴图](../review/perpendicular-u-joint-v1.9-mirrored-end-ramps/06-reverse-assembly.png)
- [主STL](../exports/perpendicular-u-joint-v1.9-mirrored-end-ramps/perpendicular-double-u-guard-v1.9-mirrored-end-ramps.stl)
- [主STL检查](../review/perpendicular-u-joint-v1.9-mirrored-end-ramps/stl-inspection.json)

全部图片由本目录真实 SCAD 和 OpenSCAD CLI 渲染，未使用图片生成。旧版本保留，未制作 3MF，未提交或推送。
