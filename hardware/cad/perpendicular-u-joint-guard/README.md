# Perpendicular 20×20 tube U-joint guard v0.2

这是对上一版“从上方套入、向下长臂”的概念的独立重做。上一版目录
`hardware/cad/rotating-foot-guard/` 保留为历史概念，本目录不覆盖它。

## 当前结构假设

- 面向围挡长方向时，正面有一件 U 卡子，背面有一件独立 U 卡子。
- 两件 U 卡子的主体分别位于 `+y` 和 `-y`，中间用同轴的“前公环 + 后母座”搭接。
- 搭接中心沿 y 轴留出螺丝通孔和外侧圆形头部避让孔；不在 PETG 内打印螺纹。
- 上方长管沿 x 方向，中心 z=+10；下方垂直管沿 y 方向，中心 z=-10；两根 20×20 方管在 z=0 处上下贴合。
- U 的下方两侧有向内的小扣边，按 20.8 mm 的内宽预留 0.8 mm 总装配间隙。

这些轴线和孔中心是 v0.2 的接口假设，尤其是实际螺丝中心相对两根方管的位置仍需实测。`screw_clearance_d=6.2`
只是兼容 M4/M5 的初始通孔，不代表实际最终孔径。

## 预览与导出

```sh
python3 hardware/cad/perpendicular-u-joint-guard/render_preview.py
```

预览会生成在 `hardware/cad/review/perpendicular-u-joint-v0.2/`，独立 STL 会生成在
`hardware/cad/exports/perpendicular-u-joint-v0.2/`：

- `perpendicular-u-front-v0.2.stl`
- `perpendicular-u-back-v0.2.stl`
- `perpendicular-u-front-print-v0.2.stl`
- `perpendicular-u-back-print-v0.2.stl`

## 还不能视为完成的部分

1. 用卡尺确认两个方管的真实相对位置、螺丝轴线和螺丝头/螺母外形。
2. 确认“搭接”是否采用当前的同轴公母环，还是需要改成上下/左右错齿的片状搭接。
3. 先打印单件配合试块，验证 PETG 的 20×20 内宽、下扣边和公母环间隙。
4. 实测确认后再做 X1C 打印方向、数量和 3MF 拼板；当前没有把这版预览当成物理验收。

