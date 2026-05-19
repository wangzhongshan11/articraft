---
title: '复制工作平面'
description: '已有 CadQuery 对象可从另一对象复制工作平面，便于在无合适面时建立正交特征。'
tags:
  - cadquery
  - examples
  - 复制
  - 工作平面
---
# 复制工作平面

当需要在已有实体上添加**与现有面不正交**的特征时，可能找不到可直接 `workplane()` 的参考面。此时可用 `copyWorkplane()` 从临时 `Workplane` 复制所需方位，继续链式建模。

**本例流程：**

1. 在 `front` 平面画圆并挤出，得到沿 Z 的圆柱。
2. 用 `copyWorkplane(cq.Workplane("right", origin=(-5, 0, 0)))` 注入右侧、偏移原点的工作平面。
3. 在新平面上再画圆并挤出，得到与第一柱垂直的第二柱。

```python
result = (
    cq.Workplane("front")
    .circle(1)
    .extrude(10)  # make a cylinder
    # We want to make a second cylinder perpendicular to the first,
    # but we have no face to base the workplane off
    .copyWorkplane(
        # create a temporary object with the required workplane
        cq.Workplane("right", origin=(-5, 0, 0))
    )
    .circle(1)
    .extrude(10)
)
```
