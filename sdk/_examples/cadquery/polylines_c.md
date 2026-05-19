---
title: '折线'
description: '`Workplane.polyline()` 可用大量首尾相连的直线段定义轮廓。'
tags:
  - cadquery
  - examples
  - polylines
---
# 折线

`Workplane.polyline()` 可用大量首尾相连的直线段定义轮廓。

本例用折线画出工字梁截面的一半，再 `mirrorY()` 得到完整截面并拉伸。

```python
(L, H, W, t) = (100.0, 20.0, 20.0, 1.0)
pts = [
    (0, H / 2.0),
    (W / 2.0, H / 2.0),
    (W / 2.0, (H / 2.0 - t)),
    (t / 2.0, (H / 2.0 - t)),
    (t / 2.0, (t - H / 2.0)),
    (W / 2.0, (t - H / 2.0)),
    (W / 2.0, H / -2.0),
    (0, H / -2.0),
]
result = cq.Workplane("front").polyline(pts).mirrorY().extrude(L)
```
