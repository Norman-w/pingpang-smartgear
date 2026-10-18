# v1.8：下部截面严格按 20 + 1.5 mm 重建

本候选保留 v1.5 的上部已确认实体，重新生成整个下部抱脚截面。旧版本不覆盖，也不再使用旧的 `u_bottom=-21`、底扣 `-21..-19.5` 或延长段高出蓝管 `+0.5` 的定义。

## 正确的 Z 截面

| 实体/功能 | Z 范围 | 高度 |
|---|---|---|
| 固定蓝色 20×20 方管 | `-20..0` | 20 mm |
| U 侧壁贴管高度 | `-20..0` | 20 mm |
| 管底向内卡扣 | `-21.5..-20` | 1.5 mm |
| 下部总包络 | `-21.5..0` | 21.5 mm |

原蓝管和灰管不移动。原旧高位内扣被移除，新内扣整段位于蓝管底面以下；在最终装配位置只与蓝管底面接触，不再有旧版 0.5 mm 的竖直体积重叠。

下部侧壁向下延续到 -21.5，为内扣提供连续的实体连接。横向仍保持原逻辑：壁厚 5 mm、X 内宽 20.8 mm、`hook_depth_x=3.5 mm`，内扣 X 中心 ±11.15 mm、向内端到 ±9.4 mm。安装过程中蓝管仍需要撑开卡臂，使约 0.6 mm 的向内咬合通过，压到底后回弹到管底。

## Y 连续长度

- 前侧同一新截面连续生成 `Y=10..33`，后侧为 `Y=-33..-10`。
- 相比原来的外端 ±21，沿蓝管 Y 方向各增加 12 mm。
- 内侧面仍为 ±10，中央通道仍为 20 mm；下部 X 外宽仍为 30.8 mm。
- 新延长段顶部齐 Z=0，原段和延长段均采用同一个 20+1.5 截面。

上部通过原侧臂内部 0.1 mm 的体积重叠与重建下部连接。重叠没有在新延长端增加高于 Z=0 的实体。Ø16 全深无台阶孔、灰管刚性让位、顶部屋檐和四个三角阴角块继续保留。

## 检查结果

| 检查 | 结果 |
|---|---|
| 旧内扣尖端在 Z>-20 的残留 | 空 |
| 新延长段在 Z>0 的材料 | 空 |
| 前侧原长度区与延长区下部截面差 | 空（Manifold 规则化） |
| 后侧原长度区与延长区下部截面差 | 空（Manifold 规则化） |
| 上部与 v1.5 的实体差 | 空（CGAL） |
| 四个三角块材料缺失 | 空（Manifold 规则化） |
| Ø16 孔内阻塞 | 空；数值检验 Ø15.999 mm |
| 预装螺丝/螺帽 0..53 mm 相对 Z 行程阻挡 | 空 |
| 灰管 0..53 mm 相对 Z 行程刚性阻挡 | 空 |
| 蓝管扫掠与非卡扣实体的刚性体积干涉 | 无；CGAL仅输出零厚度接触面，Manifold规则化结果为空 |

诊断中的共面零厚度几何没有作为打印 STL 导出。主 STL 由 CGAL 导出并独立检查：440 个三角面、220 个顶点；watertight=True；退化面、边界边、非流形边、方向不一致边均为 0。单位 mm，包围盒 54.8 × 66 × 50.5 mm，体积约 46382.025 mm³。

PETG 首件仍需确认实际尺寸配合、压入力、卡臂撑开与回弹，以及底扣实际抱持效果。本次未进行材料弹性仿真。

## 实际 SCAD 渲染和文件

- [真实装配等轴图，带 XYZ 坐标](../review/perpendicular-u-joint-v1.8-lower-20plus1p5/01-assembly-corrected-lower-profile.png)
- [Y 连续长度与总高剖面](../review/perpendicular-u-joint-v1.8-lower-20plus1p5/02-y-continuity-21p5-height.png)
- [新延长端 Y=27 的 XZ 截面，明确 20+1.5](../review/perpendicular-u-joint-v1.8-lower-20plus1p5/03-end-xz-20-plus-1p5.png)
- [下部 XY 连续性](../review/perpendicular-u-joint-v1.8-lower-20plus1p5/04-lower-xy-continuity.png)
- [Ø16 通行孔中心剖面](../review/perpendicular-u-joint-v1.8-lower-20plus1p5/05-centre-full-nut-passage.png)
- [主 STL](../exports/perpendicular-u-joint-v1.8-lower-20plus1p5/perpendicular-double-u-guard-v1.8-lower-20plus1p5.stl)
- [主 STL 检查文件](../review/perpendicular-u-joint-v1.8-lower-20plus1p5/stl-inspection.json)

全部图像由本目录真实 SCAD 和 OpenSCAD CLI 渲染，没有使用图片生成。未制作 3MF，未提交或推送。
