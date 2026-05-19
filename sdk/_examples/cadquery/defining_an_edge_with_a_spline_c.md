---
title: '用样条定义边'
description: '通过点列样条（spline）定义复杂侧边轮廓，再拉伸成实体。'
tags:
  - cadquery
  - examples
  - 样条
  - 边
  - 轮廓
---
# 用样条定义边

当某条边需要**光滑复杂曲线**而非直线或圆弧时，可用 `spline()` 过给定点列定义侧边，再与直线段 `lineTo` 组合、`close` 封闭并 `extrude`。本例在矩形基边上用样条过渡，形成不规则轮廓板。

`includeCurrent=True` 表示样条从当前点开始，与已有线段顺滑衔接。

```python
s = cq.Workplane("XY")
sPnts = [
    (2.75, 1.5),
    (2.5, 1.75),
    (2.0, 1.5),
    (1.5, 1.0),
    (1.0, 1.25),
    (0.5, 1.0),
    (0, 1.0),
]
r = s.lineTo(3.0, 0).lineTo(3.0, 1.0).spline(sPnts, includeCurrent=True).close()
result = r.extrude(0.5)
```
