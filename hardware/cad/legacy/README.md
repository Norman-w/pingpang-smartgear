# 历史 CAD：外挂式 X 型夹具

`../net_post_x_clamp.scad` 是前一轮“夹在原球网立柱两侧”的外挂式方案。
它保留在原路径，供设计回溯和旧几何回归使用；当前机械主线不是它。

当前方案是直接替换传统球网的内置式支架，参数源为：

```text
../net_stand.scad
```

当前 CAD、打印清单、预览和验收描述都应优先引用 `net_stand.scad`。旧的
`validate_scad.py`、`validate_geometry.py` 和 `render_openscad_preview.py`
仍然只验证历史方案，避免历史几何在切换时无声损坏。
