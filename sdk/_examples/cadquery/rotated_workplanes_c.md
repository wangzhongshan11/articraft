---
title: '旋转工作平面'
description: '相对另一工作平面指定旋转角，可创建旋转后的草图平面。'
tags:
  - cadquery
  - examples
  - rotated
  - workplanes
---
# 旋转工作平面

相对另一工作平面指定旋转角即可创建旋转工作平面。本变体以米为单位直接编写尺寸。

```python
import cadquery as cq

from sdk import mesh_from_cadquery

result = (
    cq.Workplane("front")
    .box(0.100, 0.100, 0.006)
    .faces(">Z")
    .workplane()
    .transformed(offset=cq.Vector(0.0, -0.038, 0.025), rotate=cq.Vector(60, 0, 0))
    .rect(0.038, 0.038, forConstruction=True)
    .vertices()
    .hole(0.006)
)

mesh = mesh_from_cadquery(result, "rotated_workplane_plate")
```
