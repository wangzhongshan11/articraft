---
title: '直齿、斜齿与人字齿轮'
description: '使用内嵌齿轮类，并保留 `cadquery.Workplane.gear()` 插件工作流。'
tags:
  - cadquery
  - examples
  - gear
  - spur
  - helical
  - herringbone
---
# 直齿、斜齿与人字齿轮

示例使用内嵌 `sdk` 齿轮类，同时在 `cadquery.Workplane` 上保持熟悉的 `cq_gears` 插件模式。下列参数以米编写，导出网格已符合基础 SDK 坐标/单位约定。

```python
import cadquery as cq

from sdk import HerringboneGear, SpurGear, mesh_from_cadquery

spur = SpurGear(module=0.001, teeth_number=19, width=0.005, bore_d=0.005)
helical = SpurGear(
    module=0.001,
    teeth_number=17,
    width=0.006,
    helix_angle=25.0,
    bore_d=0.004,
)
herringbone = HerringboneGear(
    module=0.001,
    teeth_number=24,
    width=0.010,
    helix_angle=20.0,
    bore_d=0.005,
)

spur_body = cq.Workplane("XY").gear(spur).val()
helical_body = (
    cq.Workplane("XY")
    .moveTo(spur.r0 + helical.r0 + 0.004, 0.0)
    .gear(helical)
    .val()
)
herringbone_body = (
    cq.Workplane("XY")
    .moveTo(spur.r0 + helical.r0 + herringbone.r0 + 0.010, 0.0)
    .gear(herringbone)
    .val()
)

result = cq.Assembly(name="spur-family")
result.add(spur_body, name="spur")
result.add(helical_body, name="helical")
result.add(herringbone_body, name="herringbone")

mesh = mesh_from_cadquery(result, "spur_family")
```
