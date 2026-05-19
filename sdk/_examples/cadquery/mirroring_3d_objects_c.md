---
title: '三维对象镜像'
description: '演示在三维实体上对多个镜像平面进行镜像，并将镜像结果与原几何合并，形成对称组合体。'
tags:
  - cadquery
  - examples
  - mirroring
  - 3d
  - objects
---
# 三维对象镜像

下列代码先在 XY 工作平面上绘制封闭轮廓并拉伸，再绕 X 轴旋转、平移至包围盒中心，最后分别关于 XY 与 ZY 平面做正负偏移镜像，并将所有副本布尔合并为单一结果。适合学习 `mirror()` 的 `mirrorPlane` 与 `basePointVector` 参数如何控制镜像位置与方向。

```python
result0 = (
    cadquery.Workplane("XY")
    .moveTo(10, 0)
    .lineTo(5, 0)
    .threePointArc((3.9393, 0.4393), (3.5, 1.5))
    .threePointArc((3.0607, 2.5607), (2, 3))
    .lineTo(1.5, 3)
    .threePointArc((0.4393, 3.4393), (0, 4.5))
    .lineTo(0, 13.5)
    .threePointArc((0.4393, 14.5607), (1.5, 15))
    .lineTo(28, 15)
    .lineTo(28, 13.5)
    .lineTo(24, 13.5)
    .lineTo(24, 11.5)
    .lineTo(27, 11.5)
    .lineTo(27, 10)
    .lineTo(22, 10)
    .lineTo(22, 13.2)
    .lineTo(14.5, 13.2)
    .lineTo(14.5, 10)
    .lineTo(12.5, 10)
    .lineTo(12.5, 13.2)
    .lineTo(5.5, 13.2)
    .lineTo(5.5, 2)
    .threePointArc((5.793, 1.293), (6.5, 1))
    .lineTo(10, 1)
    .close()
)
result = result0.extrude(100)

result = result.rotate((0, 0, 0), (1, 0, 0), 90)

result = result.translate(result.val().BoundingBox().center.multiply(-1))

mirXY_neg = result.mirror(mirrorPlane="XY", basePointVector=(0, 0, -30))
mirXY_pos = result.mirror(mirrorPlane="XY", basePointVector=(0, 0, 30))
mirZY_neg = result.mirror(mirrorPlane="ZY", basePointVector=(-30, 0, 0))
mirZY_pos = result.mirror(mirrorPlane="ZY", basePointVector=(30, 0, 0))

result = result.union(mirXY_neg).union(mirXY_pos).union(mirZY_neg).union(mirZY_pos)
```
