---
title: '摆线齿轮'
description: '用 parametricCurve 定义内外摆线齿廓，再扭转挤出并中心开孔。'
tags:
  - cadquery
  - examples
  - 摆线
  - 齿轮
---
# 摆线齿轮

复杂齿廓可用 **`parametricCurve`** 参数曲线描述。本例定义内摆线（hypocycloid）与外摆线（epicycloid），按齿数比在外内摆线之间切换得到单齿周期，再扫掠成**螺旋摆线齿轮**实体，最后在顶面工作平面切通中心孔。

**数学与建模步骤：**

1. `hypocycloid` / `epicycloid`：标准参数方程。
2. `gear(t, r1, r2)`：按 `floor(t / 2π * (r1/r2))` 奇偶选择曲线分支，拼出完整齿廓周期。
3. `parametricCurve(lambda t: gear(t * 2π, 6, 1))` 生成 2D 线框。
4. `twistExtrude(15, 90)` 添加扭转与高度。
5. 顶面 `circle(2).cutThruAll()` 清空轴孔。

```python
import cadquery as cq
from math import sin, cos, pi, floor

# define the generating function
def hypocycloid(t, r1, r2):
    return (
        (r1 - r2) * cos(t) + r2 * cos(r1 / r2 * t - t),
        (r1 - r2) * sin(t) + r2 * sin(-(r1 / r2 * t - t)),
    )

def epicycloid(t, r1, r2):
    return (
        (r1 + r2) * cos(t) - r2 * cos(r1 / r2 * t + t),
        (r1 + r2) * sin(t) - r2 * sin(r1 / r2 * t + t),
    )

def gear(t, r1=4, r2=1):
    if (-1) ** (1 + floor(t / 2 / pi * (r1 / r2))) < 0:
        return epicycloid(t, r1, r2)
    else:
        return hypocycloid(t, r1, r2)

# create the gear profile and extrude it
result = (
    cq.Workplane("XY")
    .parametricCurve(lambda t: gear(t * 2 * pi, 6, 1))
    .twistExtrude(15, 90)
    .faces(">Z")
    .workplane()
    .circle(2)
    .cutThruAll()
)
```
