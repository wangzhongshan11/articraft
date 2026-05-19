---
title: '沉孔与锥形沉头孔'
description: 'CadQuery 提供 cboreHole 等宏，一步完成沉孔或沉头孔，支持多点阵列。'
tags:
  - cadquery
  - examples
  - 沉孔
  - 沉头孔
  - 孔
---
# 沉孔与锥形沉头孔

**沉孔（counterbore）**与**沉头（countersink）**在机械件中极为常见，CadQuery 提供 `cboreHole`、`cskHole` 等宏，可**一步**完成阶梯孔，用法与 `hole()` 类似，既支持单点也支持由 `vertices()` 得到的**点列表**。

本例在薄板上用构造矩形顶点布四个 **cboreHole**（通孔深度 `depth=None` 表示切透）。

```python
result = (
    cq.Workplane(cq.Plane.XY())
    .box(4, 2, 0.5)
    .faces(">Z")
    .workplane()
    .rect(3.5, 1.5, forConstruction=True)
    .vertices()
    .cboreHole(0.125, 0.25, 0.125, depth=None)
)
```
