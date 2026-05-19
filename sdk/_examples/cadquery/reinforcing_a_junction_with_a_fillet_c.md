---
title: '用圆角加强连接'
description: '在选定边上施加圆角，以加强两特征之间的连接。'
tags:
  - cadquery
  - examples
  - reinforcing
  - junction
  - fillet
---
# 用圆角加强连接

```python
# This example demonstrates the use of a fillet to reinforce a junction
# between two parts by selecting the most relevant edge explicitly.

# Build a simple pipe connector with a relatively weak junction.
model = (
    cq.Workplane("XY")
    .box(15.0, 15.0, 2.0)
    .faces(">Z")
    .rect(10.0, 10.0, forConstruction=True)
    .vertices()
    .cskHole(2.0, 4.0, 82)
    .faces(">Z")
    .circle(4.0)
    .extrude(10.0)
    .faces(">Z")
    .hole(6)
)

# Reinforce the junction by filleting the circular edge closest to the center.
result = (
    model.faces("<Z[1]")
    .edges(cq.selectors.NearestToPointSelector((0.0, 0.0)))
    .fillet(1)
)
```
