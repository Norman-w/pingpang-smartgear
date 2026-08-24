# OpenSCAD CAD

`net_post_x_clamp.scad` 是首轮唯一参数源，支持：

- `PART="assembly"`：双侧装配预览；
- `PART="left_clamp"` / `PART="right_clamp"`：左右镜像夹具装配导出（不包含装配预览用的立柱实体）；
- `PART="arm"`、`"roller"`、`"roller_mount"`、`"roller_cap"`、`"knob"`、`"screw_rod"`、`"rod"`、`"bridge"`、`"guide"`、`"reference_carriage"`：单件检查/导出；
- `PART="optical_bank"`：10 路发射/接收模块包络占位，`SIDE=-1` 为镜像接收侧；
- `PART="calibration_gauge"`：打印式 10 mm 光栅/参考线标定规；
- `PART="parameter_probe"`：由验证脚本读取的参数清单，不是打印件；
- `SIDE=0`：按 `PART` 的默认左右方向；`SIDE=1/-1`：显式覆盖单件镜像选择。

使用 OpenSCAD GUI 或命令行覆盖参数，例如：

```text
openscad -D 'PART="assembly"' -o assembly.stl net_post_x_clamp.scad
openscad -D 'PART="left_clamp"' -D 'SIDE=1' -o left-clamp.stl net_post_x_clamp.scad
```

模型中的螺纹杆、光轴、滚柱、压盖、光学模块和软垫是装配/器件占位几何。打印前需要按实际标准件、打印方向和 PETG 收缩率补偿孔径；不要把 `left_clamp`/`right_clamp` 的组合导出直接当作单个打印件，滚柱、压盖、螺杆和光学模块应按独立 PART 或实物件装配。

`clamp_angle_deg` 是 X 夹具的运动参数，首轮允许 `10°…20°`，默认 `15°`；两根活动臂分别为 `7 mm` 厚，中间保留 `2 mm` 间隙，共用 Ø8 光轴并在垂直方向错层，避免两个打印臂互相穿透。每层从中心向内外臂段实际生成三角肋，中心另有局部加厚；外侧滚柱、内侧 V 槽和螺杆位置随同一角度生成，活动臂中心包含 Ø8 轴孔和打印间隙。V 槽根部额外保留 `jaw_mount_overlap=2 mm` 的实体搭接，避免导出件只在端面相切。光学导轨的 10 mm 定位孔和参考线端座孔均为实际减料通孔；参考线端座的孔轴与导轨孔同轴，弹簧销长度覆盖端座和导轨；光学模块包络放在导轨另一侧并保留独立侧向净距，避免在参考高度与端座相撞。装配预览才额外显示名义立柱。当前仍需实物确认旋钮行程、夹紧力和 V 槽软垫的真实接触。

`preview.py` 在没有 OpenSCAD 渲染器时生成俯视/正视结构预览，用于检查 X 交叉、左右镜像、方杆、光栅高度和参考线档位关系。它不是 STL 几何验证器。

若本机安装了 OpenSCAD，可运行 `python3 validate_scad.py` 编译全部 `PART`、左右镜像覆盖和临时 STL，并读取 OpenSCAD 参数源验证 X 臂共轴、内侧 V 槽包络、M8 螺杆行程、轴孔间隙和 10 mm 光栅档位；它还会用 STL 包围盒检查左右方向相反，确认 10°/20° 两个运动端点可编译、25° 越界角度会被断言拒绝。该命令不把导出物写入仓库。单独运行 `python3 validate_geometry.py` 可只做参数/运动断言。

若需要直接检查实体几何外观，可运行 `python3 render_openscad_preview.py`；它从同一份 SCAD 生成双侧装配、左侧夹具、10 路光学模块包络、参考线端座和标定规五张 PNG，输出到 `rendered/`，与 `preview.py` 的意图图分开。CI 会把这些 OpenSCAD 渲染图作为 `smartgear-openscad-previews` artifact 保存。
