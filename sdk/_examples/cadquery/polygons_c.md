---
title: '多边形孔'
description: '可在堆栈各点生成多边形轮廓；适用于固件不做小孔补偿的 3D 打印机等场景。'
tags:
  - cadquery
  - examples
  - polygons
---
# 多边形孔

可在堆栈各点生成多边形轮廓；适用于固件不做小孔圆度补偿的 3D 打印机等场景。

```python
result = (
    cq.Workplane("front")
    .box(3.0, 4.0, 0.25)
    .pushPoints([(0, 0.75), (0, -0.75)])
    .polygon(6, 1.0)
    .cutThruAll()
)
```
