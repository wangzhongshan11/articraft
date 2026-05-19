---
title: '锥齿轮'
description: '使用仓库内 vendored 的 sdk 齿轮类生成单件锥齿轮与啮合锥齿轮副，并组装为 CadQuery Assembly。'
tags:
  - cadquery
  - examples
  - gear
  - bevel
  - 锥齿轮
---
# 锥齿轮

本示例展示如何用 `sdk` 中的 `BevelGear` 与 `BevelGearPair` 生成**锥齿轮**及**啮合副**。二者输出均为常规 CadQuery 实体或复合体，可直接并入与 SDK 其余零件相同的建模流程。文中尺寸均以**米**为单位书写，与 Articraft 默认单位一致。

**结构：**

- `single`：单件锥齿轮（模数、齿数、锥角、齿宽等参数化）。
- `pair`：一对啮合锥齿轮（大轮/小轮齿数、轴交角等）。
- 使用 `cq.Assembly` 将两件沿 X 方向错开摆放，便于在查看器中对比。
- `mesh_from_cadquery` 可将装配体导出为网格资产。

```python
import cadquery as cq

from sdk import BevelGear, BevelGearPair, mesh_from_cadquery

single = BevelGear(module=0.001, teeth_number=18, cone_angle=45.0, face_width=0.004)
pair = BevelGearPair(
    module=0.001,
    gear_teeth=24,
    pinion_teeth=16,
    face_width=0.004,
    axis_angle=90.0,
)

result = cq.Assembly(name="bevel-gears")
result.add(
    single.build(),
    name="single",
    loc=cq.Location(cq.Vector(-0.018, 0.0, 0.0)),
)
result.add(
    pair.build(),
    name="pair",
    loc=cq.Location(cq.Vector(0.018, 0.0, 0.0)),
)

mesh = mesh_from_cadquery(result, "bevel_gears")
```
