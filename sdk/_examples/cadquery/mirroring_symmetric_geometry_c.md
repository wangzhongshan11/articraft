---
title: '对称几何的镜像'
description: '在二维草图中对轮廓做镜像以得到对称形状；示例同时引入水平线、垂直线等写法，使对称零件的编码更简洁。'
tags:
  - cadquery
  - examples
  - mirroring
  - symmetric
  - geometry
---
# 对称几何的镜像

当轮廓本身只需绘制一半、另一半通过对称得到时，可在二维工作平面上用 `mirrorY()`（或 `mirrorX()`）镜像线框，再统一拉伸。本例用 `hLine`/`vLine` 与 `hLineTo` 描述半边轮廓：`hLineTo` 允许按目标 X 坐标（而非增量距离）收线，最后 `mirrorY().extrude(0.25)` 生成完整截面并挤出。

```python
r = cq.Workplane("front").hLine(1.0)  # 1.0 is the distance, not coordinate
r = (
    r.vLine(0.5).hLine(-0.25).vLine(-0.25).hLineTo(0.0)
)  # hLineTo allows using xCoordinate not distance
result = r.mirrorY().extrude(0.25)  # mirror the geometry and extrude
```
