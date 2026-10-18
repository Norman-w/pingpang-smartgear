# v1.11 两个首件 / X1C PETG

> 状态更新：用户随后手动旋转180°、改用树状支撑并启动打印。实际预计4h39m13s、108.87g、272层。实际工程与原生切片包现已另存至[正式首件目录](../print-packages/barrier-clip-v1.11-first-article/README.zh-CN.md)，以其中`upright-tree-actual`文件为准。下文“未发送”及3h59m配方仅记录此前顶盖朝下准备阶段，不是当前状态，也不推荐原样复打。尤其此前“支撑未进入配合区”的检查不能证明1.5 mm水平内扣的无支撑成型可靠。

## 已核实到的层级

v1.11源文件和几何审图已提交推送至main：`d5b5c3e1c18c8ea3ceefe94bea82cca1367d8f1e`，与远端一致。

两件已拼成一板，CLI切片及原生Bambu Studio重新切片均完成；原生发送窗口显示3h59m、106.88g，并自动匹配X1C的A4灰色Generic PETG。自动热床调平和动态流量校准开启，延时摄影关闭。

**尚未点击发送，尚未启动打印。等待用户确认上一单已取走、打印板已清理以及本次使用A4。** 上一单完成仅证明机器空闲，不证明板上已清理。摄像机画面中未见明显旧件，但不以此替代清理确认。打印机保留过“材料反光太弱，自动测光失败，首层检查可能不准确”的提示，不把自动首层检查当作已通过。

## 单板配方

| 项目 | 配置 |
|---|---|
| 机器/喷嘴/打印板 | X1 Carbon / 0.4 mm / 纹理PEI |
| 数量/排布 | 两件独立对象，一板；X间距20.2 mm |
| 朝向 | 原CAD绕X旋转180°，顶盖朝下，贴床；比例1:1 |
| 内宽/基准 | X实际21.8；Y21；Z每层22 mm，不再加切片XY补偿 |
| 层高/壁数 | 0.20 mm / 6道墙 |
| 顶/底层 | 各5层 |
| 填充 | 30% gyroid |
| 首层附着 | 外侧5 mm brim，间隙0.15 mm |
| 支撑 | 普通自动，仅从打印板生成，阈值45°，顶面间距0.24 mm |
| 材料 | Generic PETG，255°C喷嘴，70°C纹理板，最大体积流量12 mm³/s |
| 时间/耗材 | 原生切片约3h59m / 106.88 g，包含支撑约11.18 g |

两个实体各55.8×67×54.5 mm，位于床内；无非等比缩放、无丢件。最终G-code中普通支撑最高Z=26.8，支撑过渡最高26.2，接触层最高27.6；抱脚功能内腔从打印Z=31开始，底扣从Z=53开始，因此没有支撑进入这些配合区。短底扣内伸的打印质量仍需首件查看，不能由“无支撑”推出质量合格。

CAD仍保留已经说明的地面间隙问题：对实际20 mm脚，底扣最低点低于管底3.5 mm，首件装配前需核实垫脚/地面空间和回弹，不能将打印完成等同实物验收。

## 文件与复现

输出目录（被现有.gitignore忽略）：`../exports/perpendicular-u-joint-v1.11-fit-21xy-22z/two-piece-x1c/`。

- `barrier-clip-v1.11-2x-X1C-PETG-native.3mf`：原生重新切片后另存的可编辑工程；项目保存不含G-code，打开后需切片。
- `barrier-clip-v1.11-2x-X1C-PETG.gcode.3mf`：CLI已切片单板包，配置修复后可原生载入。
- `barrier-clip-v1.11-2x-X1C-PETG.3mf`：CLI可编辑工程。
- `package-audit.json`：包/源文件哈希、两件包围盒、G-code校验和、支撑区域和预计用量审计。
- `manifest.json`：物料/源文件追溯和未发送状态。

```sh
python3 hardware/cad/perpendicular-u-joint-guard-v1.11-fit-21xy-22z/build_two_piece_plate.py --settings-template /absolute/path/to/an-existing-native-X1C-project.3mf
python3 hardware/cad/perpendicular-u-joint-guard-v1.11-fit-21xy-22z/audit_two_piece_plate.py
```

先按README导出源STL。构建脚本只处理离线工程，不含联网发送或启动打印指令。它读取原生X1C工程的完整配置壳，再应用本机安装的官方机器/工艺/Generic PETG配置与本次参数；模板不提供零件几何。当前使用本机已存在的handles-x1c-current.3mf作配置壳，但没有修改该工程或其所属仓库。

原生载入曾因Generic PETG单一Standard变体与旧模板的两个filament_self_index不匹配而报Invalid configuration file；已把索引与变体数对齐，添加审计断言，并再次原生载入/切片确认材料没有回退。对应上游检查见[官方PresetBundle.cpp](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PresetBundle.cpp)。
