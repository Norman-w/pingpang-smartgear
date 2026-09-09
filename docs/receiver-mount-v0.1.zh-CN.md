# 接收端配套外壳 v0.1

接收端已同步改用完整弧形前腔、加大底盖和底部柔性垫，并配套更换承载条及后盖固定孔。左右仍为十路、20 mm节距，第一路安装后光轴高度191.5 mm，整排球头与立柱基准不变。

**本次完成的是外壳和安装接口。内部暂保留原M6接收头及接收子板作几何参考；接收元件选择尚未确认，不表示其电路已经兼容裸激光。** 若改用之前截图的接收小板，需要按实物板宽、板高、感光面位置、引脚及安装孔重新设计内部固定座，不能把发射端激光夹筒直接当作接收板支架。

## 结构与装配

- PETG前盖向光学侧加深6 mm，宽度63.6 mm，外包络24 × 63.6 × 222 mm；弧形内腔按外轮廓向内偏置2.4 mm。前腔自由包络按0.5 mm名义余量检查，导轨配合处另算。
- 前盖、底盖、TPU底垫和前盖金属件与发射端共用同一组模型；接收端承载条保留原M6头孔，但改用前向开口导槽、上下端部固定孔和两处M3捕获螺母槽。
- 前盖两颗M3×30沉头螺钉位于y=0中线，螺母从承载条后面装入。螺钉载荷由前盖支撑传到端部承力带，整排载荷仍通过后盖及其筋、球头传到立柱。
- 前盖从光学侧沿光轴推入，不从顶部一路滑过光头。后盖保留原球头座并使用端部固定孔，底盖从下方安装。新前盖、承载条、后盖、底盖和底垫必须成套使用。
- 右侧原始坐标出光孔朝x−；整排沿x正方向平移84.6 mm、向上平移29 mm。源STL保留原始装配坐标，单位为毫米，切片时逐件移到打印床。
- 无密封承诺。前盖与底盖的打印方向、支撑、螺母槽和导槽尺寸需要切片与首样试装确认。

## 预览与文件

[接收端预览](../hardware/cad/preview/?view=receiver)。夹座特写页新增“查看接收端”，主视图可通过“隐藏右侧头套”检查内部。缩放和平移沿用同一套修正后的导航。

五种打印件：

| 零件 | 文件 | 材料 |
|---|---|---|
| 接收端承载条 | [rail.stl](../hardware/cad/exports/receiver-mount-v0.1/rail.stl) | PETG |
| 加大前盖 | [front_cover.stl](../hardware/cad/exports/receiver-mount-v0.1/front_cover.stl) | PETG |
| 配套后盖 | [rear_cover.stl](../hardware/cad/exports/receiver-mount-v0.1/rear_cover.stl) | PETG |
| 加大底盖 | [bottom_cover.stl](../hardware/cad/exports/receiver-mount-v0.1/bottom_cover.stl) | PETG |
| 底部柔性垫 | [bottom_gasket.stl](../hardware/cad/exports/receiver-mount-v0.1/bottom_gasket.stl) | TPU |

包内另有前盖紧固件和原接收子板两个参考模型。原M6头在网页继续使用原有器件参考。两个SCAD库均由`net_stand.scad`包含；启用裸激光方案时，主装配的两端都进入新版外壳。

```sh
python3 hardware/cad/export_laser_micro_mount.py
python3 hardware/cad/export_receiver_mount.py
python3 hardware/cad/validate_receiver_mount.py
```

## 检查边界

验证器检查打印件封闭性与单一连接实体、前盖9条剖面射线的完整壁体、内部刚体与盖子干涉、0.5 mm前腔包覆，以及前盖抽出0、2、5、10、20、30、50 mm的七个离散位置。还逐字节核对两端四个共用STL，防止预览一端更新而另一端仍引用旧版。

这不包含实物打印公差、软线、实际工具、接收电路、光路或新接收板适配验证。当前结果见输出目录的`validation.json`及`review/verification.md`。
