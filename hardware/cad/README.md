# OpenSCAD CAD

`net_post_x_clamp.scad` 是首轮唯一参数源，支持：

- `PART="assembly"`：双侧装配预览；
- `PART="left_clamp"` / `PART="right_clamp"`：左右镜像夹具；
- `PART="arm"`、`"roller"`、`"knob"`、`"rod"`、`"guide"`：单件检查；
- `PART="calibration_gauge"`：打印式 10 mm 光栅/参考线标定规；
- `SIDE=1/-1`：左/右镜像选择。

使用 OpenSCAD GUI 或命令行覆盖参数，例如：

```text
openscad -D 'PART="assembly"' -o assembly.stl net_post_x_clamp.scad
openscad -D 'PART="left_clamp"' -D 'SIDE=1' -o left-clamp.stl net_post_x_clamp.scad
```

模型中的螺纹杆、光轴、滚柱和软垫是装配占位几何。打印前需要按实际标准件、打印方向和 PETG 收缩率补偿孔径；不要把首轮参数当作最终生产尺寸。

`preview.py` 在没有 OpenSCAD 渲染器时生成俯视/正视结构预览，用于检查 X 交叉、左右镜像、方杆、光栅高度和参考线档位关系。它不是 STL 几何验证器。

若本机安装了 OpenSCAD，可运行 `python3 validate_scad.py` 编译全部 `PART`、右侧镜像和临时 STL；该命令不把导出物写入仓库。
