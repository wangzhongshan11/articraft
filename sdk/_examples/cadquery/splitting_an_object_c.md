---
title: '分割实体'
description: '可用工作平面分割对象，并保留一侧或两侧结果。'
tags:
  - cadquery
  - examples
  - splitting
  - an
  - object
---
# 分割实体

可用工作平面分割对象，并保留一侧或两侧半体。

```python
c = cq.Workplane("XY").box(1, 1, 1).faces(">Z").workplane().circle(0.25).cutThruAll()

# now cut it in half sideways
result = c.faces(">Y").workplane(-0.5).split(keepTop=True)
```
