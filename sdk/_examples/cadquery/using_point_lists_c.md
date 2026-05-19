---
title: '点列表'
description: '需在多处创建特征而反复 `Workplane.center()` 过于繁琐时，可用点列表。'
tags:
  - cadquery
  - examples
  - using
  - point
  - lists
---
# 点列表

需在多处创建特征而反复 `Workplane.center()` 过于繁琐时，可用点列表。

将点列表压入堆栈后，多数构造方法（如 `Workplane.circle()`、`Workplane.rect()`）会对堆栈上所有点同时操作。

```python
r = cq.Workplane("front").circle(2.0)  # make base
r = r.pushPoints(
    [(1.5, 0), (0, 1.5), (-1.5, 0), (0, -1.5)]
)  # now four points are on the stack
r = r.circle(0.25)  # circle will operate on all four points
result = r.extrude(0.125)  # make prism
```
