# v1.14 全深加强：形状确认版，暂不可打印

**历史撤回候选**：用户随后明确紫色底部应收成沿 Y 的棱而非宽底面；本版已由 v1.15 替代。以下是当时的审图记录，不是当前打印依据。

本版按实物易被踢坏的反馈调整几何，但不宣称已通过抗冲击或装配试验。保留 v1.13 原文件与正式打印包，不覆盖、不切片、不发送打印。

## 已确认的改动

- X 沿灰色上方长管，Y 沿蓝色下方支撑脚，Z 向上；单位 mm，一体 PETG FDM 件。
- 青色卡臂每侧沿 ±X 向外增加 2 mm：壁厚由 5 变为 7，内侧仍在 X=±10.9，外侧改为 ±17.9。
- 绿色斜坡同步加宽至 X=±17.9，总宽 35.8；原 Y/Z 斜坡轮廓不变。
- 紫色外缘沿 X=±27.9 竖直延伸至最低 Z=-23.5，与房檐外缘齐平。底部每个加强部分沿 Y 覆盖 10.5..33.5（另一端镜像），即覆盖青色卡臂完整 23 mm 长度。
- 紫色顶部保持原 Y 跨度 10.5..21.5，向下逐渐扩展 Y 范围。上方顶盖、房檐外包和字样保留原版。
- 保留原内腔、Ø16 竖直通孔及向内扣边；最低 1.5 mm 层仍不倒角。新增部件先做 0.6 阳边退让倒角，再与原倒角主体合并，避免对原顶盖重复倒角。

## 预览和验证边界

- `reinforced_guard.scad` 是原生实体入口，依赖原版 v1.12 / v1.13。
- `review.scad` 按原颜色分区进行真实 OpenSCAD 等轴审图；倒角主体由原生 SCAD 计算，字样复用从同一原文字模块导出的派生网格，以避开 CGAL 曲线字体布尔问题。
- [带 XYZ 的等轴图](../review/perpendicular-u-joint-v1.14-full-depth-ribs/01-vertical-iso.png)。颜色是同一实体的功能区域，不表示分件；紫色扩展部分与青色实体合并，因此部分青色外侧被紫色遮挡。
- `checks.scad` 是原生实体不变量探针，检查屋顶区域、原主体保留、通孔、装入槽、脚内腔、内扣和紫色底部覆盖；`CHECK="all"` 应输出空实体。
- 本次合并探针结果为 0 个面、无三维实体残留，但保留了 8 个顶点 / 4 条退化边，未作为完全空集验收通过。该结果不能替代下面的网格检查。
- **二进制 STL 试导尚未通过网格检查**：CGAL 倒角实体试导产生 8 个退化面和少量非流形边；简单近点合并不能安全消除，未采用自动补洞或未经验证的修补。失败报告保留在审图目录，试导仅作诊断，不是打印文件。仍需处理导出拓扑后才能制作正式 STL / 3MF。
- 加厚与全深加强会降低卡臂弹性；实际扣入、拆卸、地面间隙与抗踢效果仍须重新实测。

渲染先导出未改动的文字：

```sh
/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD --backend=Manifold --export-format=binstl -D 'FEATURE="label"' -o hardware/cad/exports/perpendicular-u-joint-v1.14-full-depth-ribs/guard-v1.14-lettering.stl hardware/cad/perpendicular-u-joint-guard-v1.14-full-depth-ribs/reinforced_guard.scad
/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD --backend=CGAL --preview --autocenter --viewall --projection=o --camera=0,0,0,54.7356,0,45,210 --imgsize=1500,1250 --colorscheme=Tomorrow -o hardware/cad/review/perpendicular-u-joint-v1.14-full-depth-ribs/01-vertical-iso.png hardware/cad/perpendicular-u-joint-guard-v1.14-full-depth-ribs/review.scad
```
