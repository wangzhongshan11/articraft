---
title: '交错轴与双曲面齿轮副'
description: '使用 sdk 中的 CrossedGearPair 与 HyperbolicGearPair 构建交错螺旋与双曲面啮合副并同场景对比。'
tags:
  - cadquery
  - examples
  - gear
  - 交错轴
  - 双曲面
---
# 交错轴与双曲面齿轮副

`sdk` 直接提供 **交错轴螺旋齿轮副**（`CrossedGearPair`）与 **双曲面齿轮副**（`HyperbolicGearPair`），便于在同一 `Assembly` 中并排对比两类**偏置轴**传动几何。

**示例布局：**

- `crossed`：两齿轮齿数、齿宽、轴交角与螺旋角等参数化。
- `hyperbolic`：双曲面副的模数、齿数、齿宽与轴交角。
- 两件沿 X 正负方向平移，避免网格干涉。

```python
import cadquery as cq

from sdk import CrossedGearPair, HyperbolicGearPair

crossed = CrossedGearPair(
    module=1.0,
    gear1_teeth_number=20,
    gear2_teeth_number=20,
    gear1_width=4.0,
    gear2_width=4.0,
    shaft_angle=90.0,
    gear1_helix_angle=30.0,
)
hyperbolic = HyperbolicGearPair(
    module=1.0,
    gear1_teeth_number=20,
    width=4.0,
    shaft_angle=60.0,
)

result = cq.Assembly(name="skew-axis-gears")
result.add(
    crossed.build(),
    name="crossed",
    loc=cq.Location(cq.Vector(-18.0, 0.0, 0.0)),
)
result.add(
    hyperbolic.build(),
    name="hyperbolic",
    loc=cq.Location(cq.Vector(18.0, 0.0, 0.0)),
)
```
