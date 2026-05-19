---
title: '经典 OCC 瓶子'
description: 'CadQuery 基于 OpenCascade.org (OCC) 内核；熟悉 OCC 的开发者都了解著名的“瓶子”示例。'
tags:
  - cadquery
  - examples
  - the
  - classic
  - occ
  - bottle
---
# 经典 OCC 瓶子

CadQuery 基于 OpenCascade.org (OCC) 建模内核；熟悉 OCC 的开发者都了解著名的“瓶子”示例。

与 OCC 官方版本相比，本示例仍算较长（约 13 行），但比 pythonOCC 版本短一个数量级。

```python
(L, w, t) = (20.0, 6.0, 3.0)
s = cq.Workplane("XY")

# Draw half the profile of the bottle and extrude it
p = (
    s.center(-L / 2.0, 0)
    .vLine(w / 2.0)
    .threePointArc((L / 2.0, w / 2.0 + t), (L, w / 2.0))
    .vLine(-w / 2.0)
    .mirrorX()
    .extrude(30.0, True)
)

# Make the neck
p = p.faces(">Z").workplane(centerOption="CenterOfMass").circle(3.0).extrude(2.0, True)

# Make a shell
result = p.faces(">Z").shell(0.3)
```
