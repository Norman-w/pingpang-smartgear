# v1.4 全深度螺帽通行孔

由实际 v1.3 实体新增一次 Ø16 mm 全深度切除，取消原 Ø6.2 主孔与顶部螺母窝之间的窝底台阶。只修改打印件，不修改铁管上的 Ø6.2 螺丝孔。

`full_nut_passage_guard.scad` 调用 v1.3 的 `candidate_print_solid()`，最后用 Z=-31..39 的 Ø16 / 64 边切削体切除中心。四个三角块、屋檐、底扣均继承原模型。

## 验证结果

- 全深度孔内阻塞交集为空（检测直径 15.999 mm，避开共面数值残片）。
- 预装螺帽/螺杆在相对 Z 行程 0..52 mm 的连续扫掠交集为空。
- 孔以外改动检查使用 CGAL：交集差为空。
- 最终 STL 使用 CGAL 导出并通过独立边拓扑检查：watertight=True，退化面/边界边/非流形边/反向边均为 0。
- 外包络 54.8 × 42 × 50 mm，体积约 45040.025 mm³。

本版仍保留旧侧墙对上方灰管的刚性干涉：两侧 |X|=10.4..15.4、Y=-10..10、Z=0..20，共约 4000 mm³；此问题已在独立 v1.5 处理。原底扣与下方蓝管的少量重叠属于用户允许的弹性安装干涉。

## 文件

- [装配等轴图](../review/perpendicular-u-joint-v1.4-full-nut-passage/01-assembly-isometric.png)
- [Ø16 中心剖面](../review/perpendicular-u-joint-v1.4-full-nut-passage/02-assembly-centre-section.png)
- [沿 -Z 套入方向](../review/perpendicular-u-joint-v1.4-full-nut-passage/03-insertion-minus-z.png)
- [原侧墙刚性干涉](../review/perpendicular-u-joint-v1.4-full-nut-passage/04-original-wall-interference.png)
- [STL](../exports/perpendicular-u-joint-v1.4-full-nut-passage/perpendicular-double-u-guard-v1.4-full-nut-passage.stl)

全部预览来自实际 SCAD 和 OpenSCAD CLI。未生成 3MF，未提交或推送。
