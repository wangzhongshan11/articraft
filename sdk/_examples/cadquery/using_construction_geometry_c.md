---
title: '构造几何'
description: '可绘制仅用于定位的特征：用其顶点确定其他特征位置；不直接参与成形的几何称为 `Construction Geometry`。'
tags:
  - cadquery
  - examples
  - using
  - construction
  - geometry
---
# 构造几何

可绘制仅用于定位的特征：用其顶点确定其他特征位置；不直接参与成形的几何称为 `Construction Geometry`。

下例先画矩形，再用其顶点定位一组孔。

```python
result = (
    cq.Workplane("front")
    .box(2, 2, 0.5)
    .faces(">Z")
    .workplane()
    .rect(1.5, 1.5, forConstruction=True)
    .vertices()
    .hole(0.125)
)
```
