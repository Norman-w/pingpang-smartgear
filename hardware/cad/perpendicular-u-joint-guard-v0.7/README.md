# 一体式双 U 20×20 方管限位卡 v0.7

这是对 v0.6 顶部紧固件让位和顶梁强度的修正版。v0.6 的底部高度、完整脚示意、上半部实心侧墙和前后加深全部保留。

## 本版机械契约

- 打印件是一个整体，不依靠另一个打印件、螺丝或公母件把两个 U 卡子连接起来。
- 从正面看是一个带上部实心墙的 U，从背面看也是一个；两个 U 由上方的 PETG 一体连接梁直接连接，蓝色方管上表面以下仍保持开口并保留内扣。
- 两个 U 的内侧面之间的距离严格为 20 mm。
- 两根 20×20 方管在局部接头处上下贴合：上方长管沿 x，下方垂直于它的局部方管沿 y，接触面在 z=0。
- 螺丝轴线为竖直 z 方向，从方管下侧进入，穿过两根方管后从两个 U 的上方连接梁中央让出；打印件只提供竖直通孔，不打印螺纹。
- U 两侧下方保留向内的扣边，用来限制下方方管/脚的旋转逃逸。
- 下方内扣的位置和 x/z 关系还原；完整 U 片沿正面到背面方向加深，扩大对下方脚的包持长度；内侧 20 mm 基准不变。
- 从梁向下到脚的上沿（z=0），XZ 平面 U 的中间上半段和左右侧墙均形成实心墙；前后两片墙只占各自 U 的深度，蓝色方管仍通过两个 U 的 20 mm 内距；z<0 仍保留开口和内扣。
- 装配示意显示完整的 20×20 下方脚，示意长度为 120 mm；该长度只用于预览，不改变打印件尺寸。
- 脚底 z=-20 mm；打印件最低点 z=-21 mm，只向下伸出 1 mm；内扣仍保留 8 mm 的抱脚高度，避免削弱限位。
- 顶部连接梁加厚到 8 mm；其底面保持 z=21 mm，与上方 20×20 方管顶面 z=20 mm 留 1 mm 间隙。

## 当前参数

- U 内间距：20 mm
- 方管名义尺寸：20 mm
- U 侧壁：5 mm
- U 片前后深度：11 mm（基础 7 mm + 正面到背面方向增加 4 mm）；不再增加下方局部外凸抱块
- XZ 上部实心墙：从 z=29 mm（梁顶）连续到 z=0 mm（蓝色方管顶面）；前后 U 片各自填充，内距 20 mm 不变
- 下方内扣：X 向向内深度 3.5 mm，Z 向保留高度 1.5 mm（在用户要求的 1～2 mm 范围中取中值）
- 顶部房盖：沿 X 方向左右各加长 12 mm，形成两侧房檐；房盖总宽为 54.8 mm
- 脚底下伸量：1 mm
- x 方向内宽：20.8 mm，暂作为 PETG 装配余量
- 竖直通孔：Ø6.2 mm
- 顶部螺母圆形让位窝：Ø16 mm × 5.2 mm，螺母可任意旋转姿态放入并低于顶面

## 生成预览和 STL

```sh
python3 hardware/cad/perpendicular-u-joint-guard-v0.7/render_preview.py
```

输出目录：

- 预览：`hardware/cad/review/perpendicular-u-joint-v0.7/`
- STL：`hardware/cad/exports/perpendicular-u-joint-v0.7/`

只有一个打印件 STL：

- `perpendicular-double-u-guard-v0.7.stl`
- `perpendicular-double-u-guard-print-v0.7.stl`
- `perpendicular-double-u-guard-v0.7-upper-web.stl`（本次补齐 XZ 上部实心墙）
- `perpendicular-double-u-guard-v0.7-upper-web-thinner-hooks.stl`（内扣 X 向深度收薄到 3.5 mm）
- `perpendicular-double-u-guard-v0.7-upper-web-hooks-z1p5.stl`（内扣 Z 向高度收至 1.5 mm）
- `perpendicular-double-u-guard-v0.7-eaves12.stl`（顶部房盖沿 X 两侧各延长 12 mm）

## 仍需实测

当前已锁定的是结构关系和 U 内距 20 mm；螺丝实际头型、螺母/攻牙位置、方管外尺寸误差以及下扣边的实际抱持高度仍需量测。当前没有生成 3MF，也没有把 CAD/拓扑检查当成实体装配验收。

## 坐标参考

- `x`：围挡长方向，灰色上方方管沿此方向延伸；`+x` 指向长管右端。
- `y`：正面/背面方向，下方脚的轴线；v0.7 中正面为 `+y`，背面为 `-y`，两个 U 内侧面间距沿 y 为 20 mm。
- `z`：竖直方向；`+z` 向上，中心螺丝沿 z 贯穿。
- XZ 坐标渲染源：`hardware/cad/perpendicular-u-joint-guard-v0.7/coordinate_reference_xz.scad`；渲染图：`hardware/cad/review/perpendicular-u-joint-v0.7/09-xz-coordinate-scad.png`。该 XZ 视图按要求不显示灰色上方方管；灰色方管沿 X 方向只在三维装配语境中说明。
- 等轴坐标渲染源：`hardware/cad/perpendicular-u-joint-guard-v0.7/coordinate_reference_iso.scad`；渲染图：`hardware/cad/review/perpendicular-u-joint-v0.7/10-isometric-coordinate-scad.png`。该图显示真实灰色上方方管沿 X 方向、蓝色下方脚沿 Y 方向、螺丝沿 Z 方向。
- 本次上部实心墙等轴渲染：`hardware/cad/review/perpendicular-u-joint-v0.7/11-upper-web-isometric.png`；XZ 核对渲染：`hardware/cad/review/perpendicular-u-joint-v0.7/12-upper-web-xz.png`。
- 本次内扣收薄后的等轴渲染：`hardware/cad/review/perpendicular-u-joint-v0.7/13-thinner-hooks-isometric.png`；XZ 核对渲染：`hardware/cad/review/perpendicular-u-joint-v0.7/14-thinner-hooks-xz.png`。
- 本次 Z 向 1.5 mm 的等轴渲染：`hardware/cad/review/perpendicular-u-joint-v0.7/15-hooks-z1p5-isometric.png`；XZ 核对渲染：`hardware/cad/review/perpendicular-u-joint-v0.7/16-hooks-z1p5-xz.png`。
- 本次 X 向两侧各 12 mm 房檐的等轴渲染：`hardware/cad/review/perpendicular-u-joint-v0.7/17-eaves12-isometric.png`；XZ 核对渲染：`hardware/cad/review/perpendicular-u-joint-v0.7/18-eaves12-xz.png`。

