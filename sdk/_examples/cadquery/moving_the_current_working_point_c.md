---
title: '移动当前工作点'
description: '在需要封闭轮廓且带内部特征时，通过 center() 多次重设工作平面原点；说明新原点可相对上一工作中心指定，而非必须使用全局坐标。'
tags:
  - cadquery
  - examples
  - moving
  - the
  - current
  - working
  - point
---
# 移动当前工作点

本例需要带内孔的封闭轮廓：先画外圆，再在偏移位置加矩形与内圆，最后整体拉伸。代码拆成多行（亦可写成一条长链）以突出 `center()` 的用法——每次调用都会把**当前工作平面的原点**移到新位置；第二个 `center(-1.5, 1.5)` 中的偏移是**相对于上一中心**的，而不是世界坐标系下的绝对坐标。可在任意时刻建立新的工作中心，便于在复杂板上布置多个特征。

```python
result = cq.Workplane("front").circle(
    3.0
)  # current point is the center of the circle, at (0, 0)
result = result.center(1.5, 0.0).rect(0.5, 0.5)  # new work center is (1.5, 0.0)

result = result.center(-1.5, 1.5).circle(0.25)  # new work center is (0.0, 1.5).
# The new center is specified relative to the previous center, not global coordinates!

result = result.extrude(0.25)
```
