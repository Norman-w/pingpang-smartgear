# v1.5 竖直套入让位

在 v1.4 的全深度 Ø16 通行孔基础上，仅去掉上方灰管相对打印件向上运动时需要经过的刚性侧墙材料。底扣的弹性干涉按用户确认保留。

## 实际改动

旧刚性干涉位置为两侧 |X|=10.4..15.4、Y=-10..+10、Z=0..20，共 4000 mm³。新增底部开放的让位切削体 X=-60..60、Y=-10..10、Z=-31..20，只在与原打印件相交处去料。屋檐底面仍为 Z=21，因此灰管顶面 Z=20 与屋檐有原本的 1 mm 间隙。

- 中央 Y 通道沿用名义 20 mm，没有额外放大。
- 四个前后/左右三角阴角填充块仍由 v1.3 定义，保持上宽下窄和原搭接。
- Ø16 全深度孔保留，打印件孔口没有窝底或缩径。
- 四个原始底扣保持 Z=-21..-19.5、高 1.5 mm；原始 X 中心为 ±11.15 mm，向内端到 ±9.4 mm。相对蓝管 ±10 mm 边界的 0.6 mm 咬合保持原样。

## 检查结论

使用模型连续扫掠体进行相对 Z 行程 0..52 mm 的检查，覆盖从打印件底部高于预装螺丝直到压到底的过程：

| 检查 | 结果 |
|---|---|
| 灰管扫掠与打印件的刚性干涉 | 空 |
| 预装螺帽/螺杆扫掠阻挡 | 空 |
| 全深度 Ø16 通行孔内阻塞 | 空；数值检验采用 Ø15.999 mm |
| 蓝管扫掠与非卡扣实体的刚性干涉 | 空（Manifold 规则化后） |
| 允许的底扣与蓝管重叠 | 保留，装配终点约 13.2 mm³ |
| v1.4→v1.5 底扣变化 | 空；原卡扣保持 |
| 竖直让位切削体外的材料变化 | 空（CGAL） |

CGAL 对共面接触可能输出零体积面；诊断再经 Manifold 规则化后确认为空。这个诊断现象不影响最终实体：主 STL 使用 CGAL 导出，并通过独立拓扑检查，watertight=True；退化面、边界边、非流形边和方向不一致边均为 0。单位按源模型为 mm，外包络 54.8 × 42 × 50 mm，体积约 41040.025 mm³。

剩余待实物核对的是 PETG 卡臂能否撑开约 0.6 mm 后可靠回弹，以及名义 20 mm 通道的打印配合；本次是几何/网格验证，没有模拟材料弹性或实际安装力。

## 真实 SCAD 渲染和输出

- [装配等轴图](../review/perpendicular-u-joint-v1.5-vertical-tube-clearance/01-assembly-isometric.png)
- [中心剖面](../review/perpendicular-u-joint-v1.5-vertical-tube-clearance/02-centre-section.png)
- [预装硬件与 -Z 套入方向](../review/perpendicular-u-joint-v1.5-vertical-tube-clearance/03-insertion-minus-z.png)
- [X=13 的侧向 YZ 剖面](../review/perpendicular-u-joint-v1.5-vertical-tube-clearance/04-side-yz-entry-section.png)
- [原始弹性底扣实物几何局部](../review/perpendicular-u-joint-v1.5-vertical-tube-clearance/05-original-elastic-hooks.png)
- [STL 检查报告](../review/perpendicular-u-joint-v1.5-vertical-tube-clearance/stl-inspection.json)
- [最终 STL](../exports/perpendicular-u-joint-v1.5-vertical-tube-clearance/perpendicular-double-u-guard-v1.5-vertical-tube-clearance.stl)

主模型直接导出：

```sh
/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD --backend=CGAL --export-format binstl -o hardware/cad/exports/perpendicular-u-joint-v1.5-vertical-tube-clearance/perpendicular-double-u-guard-v1.5-vertical-tube-clearance.stl hardware/cad/perpendicular-u-joint-guard-v1.5-vertical-tube-clearance/vertical_tube_clearance_guard.scad
```

全部图像来自实际 SCAD 和 OpenSCAD CLI。旧 v1.3/v1.4 保留，未制作 3MF，未提交或推送。
