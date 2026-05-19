---
title: '在顶点上定位工作平面'
description: '先选面再选顶点，用 CenterOfMass 将工作平面原点落在顶点；并演示 cutThruAll 贯穿切除。'
tags:
  - cadquery
  - examples
  - 工作平面
  - 顶点
---
# 在顶点上定位工作平面

通常 `Workplane.workplane()` 需要先选中一个**面**。若在选面之后**立即**再选**顶点**，并将 `centerOption` 设为 `CenterOfMass`，则工作平面仍贴合该面，但**原点落在顶点**而非面心。本例在盒体顶面选 `<XY` 顶点（左下），以此原点打圆并 `cutThruAll()` **贯穿整个零件**切除一角。

**API 要点：**

- `vertices("<XY")`：在已选面上筛选方向性顶点。
- `cutThruAll()`：沿法向切透，深度无需手填。

```python
result = cq.Workplane("front").box(3, 2, 0.5)  # make a basic prism
result = (
    result.faces(">Z").vertices("<XY").workplane(centerOption="CenterOfMass")
)  # select the lower left vertex and make a workplane
result = result.circle(1.0).cutThruAll()  # cut the corner out
```
