# v1.11：21 mm XY / 22 mm Z 装配余量

基于已提交推送的 v1.10（`c6597345edb3dd24e056d5416291ad9cbcf73f9c`），独立修改配合基准，不整体缩放模型。X=灰色长管轴，Y=蓝色脚轴，Z向上，单位mm。实际管子预览仍为20×20，不能把配合放宽伪装成实物变粗。

| 项目 | v1.10 | v1.11 |
|---|---:|---:|
| X方管基准 | 20 | 21 |
| X原打印附加间隙 | 0.8 | 0.8 |
| X实际内宽 | 20.8 | 21.8 |
| 双U内距 / 灰管Y槽宽 | 20 | 21 |
| 每层Z方管容纳高度 | 20 | 22 |
| 下层容纳区 | -20..0 | -22..0 |
| 底扣Z范围 | -21.5..-20 | -23.5..-22 |
| 顶盖Z范围 | 21..29 | 23..31 |
| 每侧立墙厚度 | 5 | 5 |
| 底扣厚度 | 1.5 | 1.5 |
| 斜坡X全宽，与立墙外侧齐平 | 30.8 | 31.8 |
| 单侧屋檐 | 12 | 12 |
| 全深螺帽通孔 | Ø16 | Ø16 |

两侧主板仍各11 mm深，新增斜坡仍各12 mm长，关于Y=0镜像，靠主体高10、外端高3；两端移到 |Y|=21.5..33.5。屋檐、墙厚、坡高、通孔都没有被比例缩放。

内扣尖端仍X=±9.4，对实际20 mm蓝管保持0.6 mm咬合；随着墙外移，内扣X深从3.5调整到4.0 mm，Z厚仍1.5 mm。安装仍从+Z向-Z压入，底扣需要PETG卡臂弹性张开。放宽的最大21×22包络与内扣的弹性干涉也保留，不能把刚性无碰撞检查当作卡扣弹性试验。

## 地面空间与首件门槛

**Z放宽后底扣最低点为-23.5：比实际20 mm脚底(-20)低3.5 mm，比旧版再低2 mm。** 这实现了22 mm下层容纳空间，但若方管直接贴地，可能顶地。需确认实际垫脚/地面空间，不能由数字模型宣称已经可装。真实管上方至盖底间隙也由1增加至3 mm。

需首件确认：弯曲/倾斜实物的装配、螺帽实际尺寸、地面空间、PETG扣入力和回弹、放宽后的止转游隙及强度。当前没有进行打印、材料弹性或承载试验；没有生成3MF。

## 检查与文件

主STL通过CGAL导出和独立网格检查：432三角面、216顶点、1个连通分量；watertight=True；退化面/边界边/非流形边/方向不一致边均0。包围盒55.8×67×54.5 mm，体积约55472.809548 mm³。

`review.scad`提供可复查的布尔检查：镜像、Ø15.999数值探针通孔、21×22灰管包络60 mm竖直装入、预装螺丝/螺帽60 mm相对行程均为空。21×22蓝管最大包络排除底扣后的刚性运动检查经Manifold规则化为空；CGAL的Z=0接触面残留为零厚度、零体积，不是实体穿模。

源文件将几何重新集中参数化，可用 `guard_v1_11(20,20,20)` 回到旧基准，与v1.10进行对照。精确布尔差含旧版X缩放造成的零体积浮点外侧面；另提供±0.001 mm包络容差双向检查，避免把数值残面当成设计修改。

- [主SCAD](fit_clearance_guard.scad)
- [审图及布尔检查SCAD](review.scad)
- [真实等轴装配图](../review/perpendicular-u-joint-v1.11-fit-21xy-22z/01-assembly.png)
- [XZ内宽21.8、高22尺寸图](../review/perpendicular-u-joint-v1.11-fit-21xy-22z/02-xz-21p8-by-22.png)
- [YZ槽宽21、高22尺寸图](../review/perpendicular-u-joint-v1.11-fit-21xy-22z/03-yz-21-by-22.png)
- [俯视图](../review/perpendicular-u-joint-v1.11-fit-21xy-22z/04-top.png)
- [反向等轴图](../review/perpendicular-u-joint-v1.11-fit-21xy-22z/05-reverse-assembly.png)
- [主STL](../exports/perpendicular-u-joint-v1.11-fit-21xy-22z/perpendicular-double-u-guard-v1.11.stl)
- [独立STL检查](../review/perpendicular-u-joint-v1.11-fit-21xy-22z/stl-inspection.json)

导出命令（从仓库根运行，先建输出目录）：

```sh
/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD --backend=CGAL --export-format=binstl -o hardware/cad/exports/perpendicular-u-joint-v1.11-fit-21xy-22z/perpendicular-double-u-guard-v1.11.stl hardware/cad/perpendicular-u-joint-guard-v1.11-fit-21xy-22z/fit_clearance_guard.scad
```

全部图片来自实际SCAD渲染。v1.10已先行推送；本轮按用户确认将v1.11源文件及审图记录单独提交推送，再准备两个首件的X1C PETG拼板。旧模型未改。
