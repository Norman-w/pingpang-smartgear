# 硬件工程

这里放置夹具、延长杆、连续光栅导轨、参考线、PVDF 夹片、红外收发器和装配资料。

## 当前硬件拆分

- `cad/`：参数化 OpenSCAD、左右镜像件和装配预览；
- `electronics/`：PVDF AFE、调制红外光栅和板级接口边界；

当前打印件仍由 `cad/net_post_x_clamp.scad` 这一份参数源统一导出；夹具、方杆、参考线端座和光学模块的拆分清单见 [`cad/print-manifest.zh-CN.md`](cad/print-manifest.zh-CN.md)。`clamp/`、`extension-rod/`、`reference-line/` 和 `bom/` 是后续实物资料目录，尚未作为当前工程目录使用。

首版按 Ø25 mm 圆柱立柱起模，最终兼容范围必须以实物测量、夹紧力和滑移记录为依据。当前不包含相机作为本体测量链路；外部视频设备只用于后续时间戳回放复核。
