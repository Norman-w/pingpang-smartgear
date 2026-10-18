# 乒乓球围挡旋转脚防转卡子 v0.1

这是独立于现有 `hardware/cad/net_stand.scad` 的 PETG 原型。它针对用户描述的“20×20 方管骨架 + 可旋转支撑脚”做了一个每脚一枚、左右可镜像的上套下扣式限位卡：

- 上端是底部开放的反向 U 槽，从上方套住长方向的 20×20 方管；
- 两侧连续肋把下端内扣受到的防转力矩传回上套槽；
- 下端只有一侧做向内扣的舌和圆鼻尖，先用较小的局部接触阻止脚自行旋转，并保留从上方装入/手工拆下的可能；
- `SIDE=1` 和 `SIDE=-1` 生成相反方向的内扣，左右脚可按实际空间镜像；
- `hook_test_coupon` 可先打印短试装片，避免直接打印完整长卡子。

## 当前已知 / 暂定 / 待确认

| 项目 | 状态 | 当前值或要求 |
| --- | --- | --- |
| 打印工艺 | 已知 | Bambu Lab X1C，PETG，FDM |
| 方管名义外包络 | 已知 | 20×20 mm |
| 卡子数量 | 暂定 | 每只旋转脚 1 枚，左右镜像 |
| 初始总装配余量 | 暂定 | `tube_clearance_total = 0.8 mm`，即内宽 20.8 mm；不是最终实测值 |
| 卡子壁厚 | 暂定 | 4.0 mm，首样后按插入力/防转刚度调整 |
| 螺丝 | 待确认 | M4 或 M5；本版本只在装配预览中放置 Ø5.2 mm 轴线占位，不把螺纹冻结进卡子 |
| 旋转轴位置 | 待确认 | 需要脚管外侧包络、轴线到上管的距离、脚在工作角度的实际边界 |
| 内扣方向 | 待确认 | 先用 `SIDE=1`；若现场空间相反，导出 `SIDE=-1` |
| 受力目标 | 暂定 | 防止脚从工作角度自行旋转；不把卡子当作倒地冲击的主要承力件 |

## 预览 PART

```sh
OPENSCAD_BIN=/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD \
  python3 hardware/cad/rotating-foot-guard/render_preview.py \
  --output-dir hardware/cad/review/rotating-foot-guard-v0.1
```

预览包括：

- `guard-clip-assembly-deployed.png`：工作状态，上方方管、下方脚、螺丝轴线和透明卡子；
- `guard-clip-assembly-folded.png`：脚旋到收纳方向的对照；
- `guard-clip-printable.png`：实际打印实体的等轴视图；
- `guard-clip-cutaway.png`：卡子局部剖开，检查上槽、连续肋、下扣；
- `guard-clip-fit-section.png`：20×20 方管在上下捕获区域中的截面关系；
- `guard-clip-hook-test-coupon.png`：短下扣试装片；
- `guard-clip-print-orientation.png`：建议的侧面平放方向。

## 首样前必须量测

1. 方管在卡子接触位置的实际外宽/外深，而不是只看名义 20 mm；
2. 旋转脚在工作角度时，脚管上缘、下缘和螺丝轴线到上长管的三维距离；
3. 螺丝实际是 M4 还是 M5、上方螺母外包络、下方攻丝孔外包络，以及卡子是否需要让位；
4. 倒地变形后仍允许的最大偏摆和希望的人工拆装力；
5. 首件先打印 `hook_test_coupon`，确认卡子能落下、内扣能抱住、手拆不脆裂，再做全长卡子。

本目录目前不生成拼板 3MF。尺寸和脚的真实姿态确认后，再根据左右件数量、打印朝向、边距和是否需要测试片，一次性生成带 manifest、包围盒和哈希的 X1C 拼板。

带 `--export-stl` 时还会输出已经按建议侧面平放方向旋转过的 `*-print-orientation.stl`；它可以作为后续拼板的几何输入，但仍需在 Bambu Studio 中确认层高、支撑、壁数和 PETG 配置。
