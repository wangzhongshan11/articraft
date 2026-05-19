---
title: '在面上创建工作平面'
description: '在已有特征的面选片上定位新工作平面并打孔，是 CadQuery 面向过程建模的核心用法。'
tags:
  - cadquery
  - examples
  - 工作平面
  - 面
---
# 在面上创建工作平面

本示例演示如何在**已生成实体的某个面**上建立新工作平面并加工特征（此处为通孔）。这是 CadQuery 区别于普通「脚本堆坐标」的关键能力：用面选择器与工作平面链，减少手工维护大量绝对坐标。

**说明：**

- `Workplane.faces()` 接受选择器字符串，可筛选单个面并在其上 `workplane()`。
- 默认新工作平面原点：由所选面拟合平面，并将**上一工作平面原点**投影到该面。可用 `workplane(centerOption=...)` 改变行为。
- 不必为每个特征单独保存尺寸变量，模型在修改基体时更易保持一致。

```python
result = cq.Workplane("front").box(2, 3, 0.5)  # make a basic prism
result = (
    result.faces(">Z").workplane().hole(0.5)
)  # find the top-most face and make a hole
```
