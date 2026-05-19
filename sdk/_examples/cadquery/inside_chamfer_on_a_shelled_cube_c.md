---
title: '抽壳立方体内棱倒角'
description: '用逻辑选择器仅对抽壳后立方体顶面的内棱做倒角。'
tags:
  - cadquery
  - examples
  - 内棱
  - 倒角
  - 抽壳
  - 立方体
---
# 抽壳立方体内棱倒角

先建实心立方体，从顶面抽壳得到薄壁盒，再选中顶面，用边选择器 `not(<X or >X or <Y or >Y)` **排除外圈四边**，仅对内圈竖棱 `chamfer`，实现「开口朝上的盒体内角倒角」效果。

```python
result = (
    cq.Workplane("XY")
    .box(2, 2, 2)
    .faces(">Z")
    .shell(-0.2)
    .faces(">Z")
    .edges("not(<X or >X or <Y or >Y)")
    .chamfer(0.125)
)
```
