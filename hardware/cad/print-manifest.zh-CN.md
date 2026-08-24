# 首样打印与装配清单

这份清单只说明 CAD 导出关系，不代表 PETG 实物已经打印、夹紧力已经合格，或光学/电气已经接通。打印前仍需按实际喷嘴、层高、PETG 收缩和标准件尺寸复核孔径。

## 每侧夹具的首样导出

| `PART` | 首样数量 | 处理方式 |
| --- | ---: | --- |
| `arm` | 2 | PETG；同一活动臂导出打印两件，装配时分别作为上下错层臂 |
| `jaw` | 1 | PETG；包含上下两层的 90° V 槽硬体 |
| `jaw_pad` | 1 | TPU/硅胶替换件占位；包含两根臂上的软垫，不用 PETG 打印 |
| `roller_mount` | 1 | PETG；U 槽侧壁、带六边形螺母沉孔和 M8 通孔的捕获块，打印方向/是否拆分需按切片结果确认 |
| `roller_cap` | 1 | PETG；两只带侧向扣脚和光轴避让孔的可拆压盖 |
| `knob` | 1 | PETG；约 Ø40 mm 旋钮 |
| `bridge` | 1 | PETG；固定桥件 |
| `rod` | 1 | PETG；12×12×130 mm 方杆 |
| `guide` | 1 | PETG；连续导轨、刻度标记和 10 mm 定位通孔 |
| `reference_carriage_body` | 1 | PETG；只打印端座本体，包含参考线贯穿孔 |

`left_clamp`/`right_clamp` 是装配检查导出，不是单个可直接打印的组合件。`reference_carriage` 包含定位销装配占位，打印时使用 `reference_carriage_body`；`reference_pin`、`screw_rod`、Ø8 光轴、滚柱、滚柱轴和螺母使用实物标准件。`optical_bank` 是电子模块包络，不打印成最终光学件。

## 双侧设备的标准件与共享件

- 两侧各一根 Ø8 mm 金属中心光轴，并配锁紧件；
- 两侧各一根 M8×1.25 金属螺杆、圆头/球头和配套螺母；
- 每侧两只竖直滚柱、滚柱轴和可拆压盖；
- 每侧一只弹簧定位销，实际长度按端座/导轨实测确认；
- 每侧两组可替换 TPU/硅胶 V 槽软垫；
- 两侧各一套 PVDF 可拆夹片、AFE/线束和 10 路光学模块；
- `calibration_gauge` 打印一件作为共享的 +10…+100 mm 高度标定规。

## 导出示例

```text
openscad -D 'PART="arm"' -o arm.stl net_post_x_clamp.scad
openscad -D 'PART="jaw"' -o jaw.stl net_post_x_clamp.scad
openscad -D 'PART="jaw_pad"' -o jaw-pad.stl net_post_x_clamp.scad
openscad -D 'PART="reference_carriage_body"' -o reference-carriage.stl net_post_x_clamp.scad
openscad -D 'PART="calibration_gauge"' -o calibration-gauge.stl net_post_x_clamp.scad
```

打印后先完成 M-02 的无网运动检查，再安装立柱软垫和方杆；没有 M-01/M-02/M-03 的照片、量具读数和记录文件时，现场记录状态必须保持 `pending`。
