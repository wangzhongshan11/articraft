---
title: '齿条与齿轮'
description: '齿条与直齿轮啮合，并保留 `Workplane.gear()` 插件式工作流。'
tags:
  - cadquery
  - examples
  - gear
  - rack
  - pinion
---
# 齿条与齿轮

齿条可直接构建；从动小齿轮仍可使用内嵌的 `Workplane.gear()` 辅助，工作流与上游 `cq_gears` 一致。

```python
import cadquery as cq

from sdk import RackGear, SpurGear

pinion = SpurGear(module=1.0, teeth_number=18, width=6.0, bore_d=5.0)
rack = RackGear(module=1.0, length=35.0, width=6.0, height=4.0)

pinion_body = cq.Workplane("XY").gear(pinion).val()
rack_body = rack.build()

result = cq.Assembly(name="rack-and-pinion")
result.add(
    pinion_body,
    name="pinion",
    loc=cq.Location(cq.Vector(0.0, pinion.r0 + 1.2, 0.0)),
)
result.add(
    rack_body,
    name="rack",
    loc=cq.Location(cq.Vector(-17.5, 0.0, -3.0)),
)
```
