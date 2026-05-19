---
title: '放样（Loft）'
description: '放样是在多段线框之间扫掠成的实体；本例在矩形顶面与偏移工作平面上的小矩形之间 loft。'
tags:
  - cadquery
  - examples
  - 放样
  - loft
---
# 放样（Loft）

**放样（loft）**是在多段**封闭线框（Wire）**之间扫掠生成的实体。本例先在前视平面建薄盒，在顶面画大圆作为第一截面轮廓的一部分，再 `workplane(offset=3.0)` 抬高工作平面并画小矩形作为第二截面，最后 `loft(combine=True)` 将截面之间光滑连接成实体。

适合学习「截面在不同高度、不同形状」的过渡建模。

```python
result = (
    cq.Workplane("front")
    .box(4.0, 4.0, 0.25)
    .faces(">Z")
    .circle(1.5)
    .workplane(offset=3.0)
    .rect(0.75, 0.5)
    .loft(combine=True)
)
```
