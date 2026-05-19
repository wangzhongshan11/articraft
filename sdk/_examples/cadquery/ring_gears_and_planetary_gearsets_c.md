---
title: '内齿圈与行星轮系'
description: '使用内嵌 `sdk` 齿轮 API 构建内齿圈与行星轮系。'
tags:
  - cadquery
  - examples
  - gear
  - ring
  - planetary
---
# 内齿圈与行星轮系

内齿圈类与行星轮辅助函数已直接移植到 `sdk`，可组合固定内齿圈与完整轮系，无需依赖上游包。

```python
import cadquery as cq

from sdk import PlanetaryGearset, RingGear

ring = RingGear(module=1.0, teeth_number=42, width=6.0, rim_width=3.0)
planetary = PlanetaryGearset(
    module=1.0,
    sun_teeth_number=12,
    planet_teeth_number=9,
    width=5.0,
    rim_width=3.0,
    n_planets=3,
)

result = cq.Assembly(name="ring-and-planetary")
result.add(
    ring.build(),
    name="ring",
    loc=cq.Location(cq.Vector(-35.0, 0.0, 0.0)),
)
result.add(
    planetary.build(),
    name="planetary",
    loc=cq.Location(cq.Vector(20.0, 0.0, 0.0)),
)
```
