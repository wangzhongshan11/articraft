---
title: '渐开线齿轮'
description: '生成渐开线齿廓单齿线框，极阵列复制为整圈，再扭转挤出成螺旋齿轮。'
tags:
  - cadquery
  - examples
  - 渐开线
  - 齿轮
---
# 渐开线齿轮

本示例用纯几何公式构造**渐开线齿廓**：计算分度圆、齿顶圆、基圆与齿根圆，用 `parametricCurve` 生成左右渐开线段，再与齿顶圆弧、齿根圆弧及径向线段 `assembleEdges` 成封闭线框，2D 倒角后通过 `polarArray` 按齿数复制并 `consolidateWires`，最后 `twistExtrude` 得到扭转齿宽。

下方代码完整保留原文（含 `involute_gear` 函数），便于学习与调试齿形参数（模数 `m`、齿数 `z`、压力角、变位等）。

```python
from math import radians, degrees, tan, acos, cos, sin


def involute_gear(m, z, alpha=20, shift=0, n=20):
    alpha = radians(alpha)

    # Radii
    r_ref = m * z / 2
    r_top = r_ref + m * (1 + shift)
    r_base = r_ref * cos(alpha)
    r_d = r_ref - 1.25 * m

    def inv(a):
        return tan(a) - a

    alpha_inv = inv(alpha)
    alpha_tip = acos(r_base / r_top)
    alpha_tip_inv = inv(alpha_tip)

    a = 90 / z + degrees(alpha_inv)
    a2 = 90 / z + degrees(alpha_inv) - degrees(alpha_tip_inv)
    a3 = 360 / z - a

    def involute_curve(r_b, sign=1):
        def f(r):
            local_alpha = sign * acos(r_b / r)
            x = r * cos(tan(local_alpha) - local_alpha)
            y = r * sin(tan(local_alpha) - local_alpha)
            return x, y

        return f

    right = (
        cq.Workplane()
        .transformed(rotate=(0, 0, a))
        .parametricCurve(
            involute_curve(r_base, -1),
            start=r_base,
            stop=r_top,
            makeWire=False,
            N=n,
        )
        .val()
    )

    left = (
        cq.Workplane()
        .transformed(rotate=(0, 0, -a))
        .parametricCurve(
            involute_curve(r_base),
            start=r_base,
            stop=r_top,
            makeWire=False,
            N=n,
        )
        .val()
    )

    top = cq.Edge.makeCircle(r_top, angle1=-a2, angle2=a2)
    bottom = cq.Edge.makeCircle(r_d, angle1=-a3, angle2=-a)

    side = cq.Edge.makeLine(cq.Vector(r_d, 0), cq.Vector(r_base, 0))
    side1 = side.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -a)
    side2 = side.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -a3)

    profile = cq.Wire.assembleEdges([left, top, right, side1, bottom, side2])
    profile = profile.chamfer2D(m / 4, profile.Vertices()[-3:-1])

    res = (
        cq.Workplane()
        .polarArray(0, 0, 360, z)
        .each(lambda loc: profile.located(loc))
        .consolidateWires()
    )

    return res.val()


result = (
    cq.Workplane(obj=involute_gear(1, 20))
    .toPending()
    .twistExtrude(20, 30)
)
```
