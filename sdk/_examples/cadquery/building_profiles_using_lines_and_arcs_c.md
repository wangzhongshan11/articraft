---
title: '用直线与圆弧构建轮廓'
description: '用二维直线与三点圆弧拼接封闭轮廓，再拉伸为棱柱体。'
tags:
  - cadquery
  - examples
  - 轮廓
  - 直线
  - 圆弧
---
# 用直线与圆弧构建轮廓

有时需要**直线与圆弧**组合成复杂二维轮廓。本例在 `front` 工作平面上依次 `lineTo`、用 `threePointArc` 过渡圆弧，再 `close` 封闭轮廓并 `extrude` 得到棱柱实体。

**二维绘图约定：**

- 二维操作维护**当前点**，初始为原点。
- `close()` 将当前点连回轮廓起点，形成封闭线框。
- 封闭后即可拉伸为实体。

```python
result = (
    cq.Workplane("front")
    .lineTo(2.0, 0)
    .lineTo(2.0, 1.0)
    .threePointArc((1.0, 1.5), (0.0, 1.0))
    .close()
    .extrude(0.25)
)
```
