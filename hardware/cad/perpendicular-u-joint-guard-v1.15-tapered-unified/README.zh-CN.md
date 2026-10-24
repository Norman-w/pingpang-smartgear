# v1.15：紫色下收成棱、连接处补实

用于两根 20×20 方管上下垂直搭接处的可拆卸止转卡。一体 PETG / X1C FDM 件；X 沿上方长管，Y 沿下方支撑脚，Z 向上，单位 mm。使用时沿 -Z 套入，收纳前先取下卡子。

六件黑色 PETG 打印交付见[正式打印包](../print-packages/barrier-clip-v1.15-6x-black-PETG/README.zh-CN.md)。`build_six_plate.py` 离线生成六件工程和切片，`audit_six_plate.py` 核对数量、姿态、尺寸、热床边界、历史实际配方及支撑路径；两者均不发送打印。发送状态另见打印包 `manifest.json`。

## 本次修正

- 保留已确认的卡臂外扩量：青色每侧沿 X 向外增加 2 mm，壁厚 7 mm，内侧 X=±10.9，外侧 X=±17.9。绿色斜坡外侧面随之对齐。
- 紫色不再是宽底直立块。上端仍连接原房檐，下端收敛到 **X=±17.9、Z=-23.5 的 Y 向棱**，没有新增紫色水平底面。每条底棱的 Y 范围为 10.5..33.5，另一端镜像，覆盖卡臂完整 23 mm 长度。
- 紫色使用顶面四点、底棱两点构成的闭合六顶点楔体；下端不是用小平板冒充尖棱。它在底棱上方与卡臂有真实体积重叠，不是悬空片。
- 先合并未经倒角的原主体、加厚卡臂、加宽斜坡、紫色楔体，再对合并实体进行 0.6 阳边倒角，不再对接合面各自倒角。
- 剖面发现原 5 mm 上半墙与新 7 mm 卡臂、斜收筋之间还存在小三角空腔；用根部过渡实体补实。补料仅在原接合区和方管配合包络外，不改变内腔或中心通孔。
- 原最低 1.5 mm 层保留，不倒角；内扣、顶面字样、安装方向及原上方顶盖尺寸保持。

## 源文件、实际渲染与导出

- `tapered_guard.scad`：原生几何与统一倒角的定义；依赖 v1.12 / v1.13，不覆盖历史版。
- `build_export.py`：稳定导出路径。CGAL 直接计算复杂统一倒角会触发断言，因此先由原生 SCAD 导出封闭原始实体，再用 Manifold64 实现**相同的八面体侵蚀→膨胀→与原实体求交→恢复底层**运算。数值容差及二进制输出坐标网格为 0.00001 mm；不补洞、不体素化、不替换设计形状。输出记录源码及网格 SHA-256。
- `review.scad`：OpenSCAD 对上述已验证派生网格进行真实着色渲染。SCAD 源仍是几何依据；颜色只是同一实体的标识，不是分件或多色打印设置。
- `validate_geometry.py`：接合区实体探针、安装通道、螺丝通孔、底棱端点和上盖对比。

```sh
uv run --no-project --with manifold3d==3.5.4 --with numpy==2.5.4 python hardware/cad/perpendicular-u-joint-guard-v1.15-tapered-unified/build_export.py
uv run --no-project --with manifold3d==3.5.4 --with numpy==2.5.4 python hardware/cad/perpendicular-u-joint-guard-v1.15-tapered-unified/validate_geometry.py
```

文字网格复用 v1.13 的同源导出；若不存在，先运行 v1.13 的 `build_export.py`。输出目录在 `hardware/cad/exports/perpendicular-u-joint-v1.15-tapered-unified/`，`guard-v1.15.stl` 为整件，`guard-v1.15-body.stl` 为审图主体，`raw-solid.stl` / `body-manifold.stl` 为中间或诊断输出，不是打印入口。

## 已核对的数字几何

- 最终整件 7864 面、3932 顶点，单一连通实体；退化面、边界边、非流形边、方向错误均为 0，封闭流形检查通过。
- 外包约 55.8×67×55.1 mm（含字样），体积约 70640.635 mm³。
- 6 类接合区、每类 4 个对称位置的缺料体积均为 0，包含上墙到斜筋的小三角空腔位置。
- 上方管槽、下方脚内腔、Ø15.98 通孔探针侵入体积均为 0。
- 最低平面最外 X=±17.9，四条 Y 向底棱的所有端点均在实际网格上；没有延伸至房檐 X=±27.9 的紫色平底。
- Z≥24 的上盖与 v1.13 差集体积合计约 0.00083 mm³，为导出量化误差量级；屋盖设计尺寸未修改。

报告和审图：

- [带 XYZ 的等轴图](../review/perpendicular-u-joint-v1.15-tapered-unified/01-tapered-iso.png)
- [XZ 连接剖面，Y=-17..-15](../review/perpendicular-u-joint-v1.15-tapered-unified/02-xz-section.png)
- [最低 0.1 mm 薄层底视核对](../review/perpendicular-u-joint-v1.15-tapered-unified/03-bottom-slice.png)
- 审图目录内 `build-validation.json`、`geometry-validation.json`、`stl-inspection.json`、`body-inspection.json`。

这些结果只证明数字几何和网格连通性。实际扣入弹性、拆卸、地面间隙和抗踢强度仍须重新试装/测试，不能以网格封闭代替实物验收。旧 v1.13 正式打印包未变。
