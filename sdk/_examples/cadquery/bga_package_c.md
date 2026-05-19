---
title: 'BGA 封装'
description: '通用球栅阵列（BGA）封装模型，可在顶面切削球形定位标记（index mark）。'
tags:
  - cadquery
  - examples
  - bga
  - package
  - smd
  - 封装
---
# BGA 封装

本示例复现 `cq-electronics` 中的**通用 BGA 封装**：先以给定长宽厚生成矩形基体，再在非简化模式下于顶角附近切出球形**定位凹坑**（index mark），便于贴片识别方向。

**参数说明：**

- `length` / `width` / `height`：封装外形尺寸。
- `simple`：为 `True` 时仅保留盒体，不加工定位球切除。
- 定位球位置由封装半长宽向内偏移 1 mm，高度略高于顶面，再用 `cut` 与主体布尔差。

代码与 API 名称保持英文，便于与 CadQuery / 电子封装库对照。

```python
import cadquery as cq

length = 20
width = 20
height = 1
simple = False

result = cq.Workplane("XY").box(length, width, height)

if not simple:
    index_mark_radius = 2
    index_mark_loc_x = -((length / 2) - 1)
    index_mark_loc_y = -((width / 2) - 1)
    index_mark_elevation = (height / 2) + (index_mark_radius * 0.93)

    index_mark = cq.Workplane(
        origin=(
            index_mark_loc_x,
            index_mark_loc_y,
            index_mark_elevation,
        )
    ).sphere(index_mark_radius)

    result = result.cut(index_mark)
```
