---
title: '偏移工作平面'
description: '工作平面不必紧贴在某个面上；可在选定面的法向方向上按距离偏移后再草图与拉伸，本例在偏移平面上挤出圆盘并与基体合并。'
tags:
  - cadquery
  - examples
  - offset
  - workplanes
---
# 偏移工作平面

工作平面不必恰好落在实体表面上。创建 `workplane()` 时可通过 `offset` 参数沿法向离开该面一段距离，再在其上绘制草图——对“在壳体外侧再叠一层凸台”一类建模完全合法。

本例先挤出基座长方体，在 `-X` 侧面建立偏移 0.75 的工作平面，画圆并挤出，得到与主体结合的圆盘状凸台。

```python
result = cq.Workplane("front").box(3, 2, 0.5)  # make a basic prism
result = result.faces("<X").workplane(
    offset=0.75
)  # workplane is offset from the object surface
result = result.circle(1.0).extrude(0.5)  # disc
```
