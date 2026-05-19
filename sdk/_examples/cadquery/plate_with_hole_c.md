---
title: '带孔板'
description: '矩形盒体并在顶面中心加工通孔的基础示例。'
tags:
  - cadquery
  - examples
  - plate
  - with
  - hole
---
# 带孔板

最简盒体加中心孔。

`">Z"` 选择结果盒体的最顶面；孔默认落在工作平面原点投影处——上一工作平面原点在 (0,0,0) 时，投影即面中心。默认孔深为贯穿整件。

```python
# The dimensions of the box. These can be modified rather than changing the
# object's cad directly.
length = 80.0
height = 60.0
thickness = 10.0
center_hole_dia = 22.0

# Create a box based on the dimensions above and add a 22mm center hole
result = (
    cq.Workplane("XY")
    .box(length, height, thickness)
    .faces(">Z")
    .workplane()
    .hole(center_hole_dia)
)
```
