---
title: '参数化轴承座'
description: '只需组合少数几个基础建模函数，用寥寥数行代码即可构建质量很高的参数化轴承座（pillow block）。'
tags:
  - cadquery
  - examples
  - 参数化
  - 轴承
  - 轴承座
---
# 参数化轴承座

本示例演示如何用 CadQuery 以极少代码搭建**参数化轴承座**（bearing pillow block）：先拉出基座实体，再在顶面定工作平面并打轴承孔，最后用构造矩形定位四个安装孔并一次性加工沉孔（cbore）。整体思路是「盒体 → 顶面工作平面 → 孔阵列」，适合作为机架类零件的入门模板。

将 `(length, height, bearing_diam, thickness, padding)` 视为可调参数，即可在不改流程的前提下缩放外形、孔径与边距。

```python
(length, height, bearing_diam, thickness, padding) = (30.0, 40.0, 22.0, 10.0, 8.0)

result = (
    cq.Workplane("XY")
    .box(length, height, thickness)
    .faces(">Z")
    .workplane()
    .hole(bearing_diam)
    .faces(">Z")
    .workplane()
    .rect(length - padding, height - padding, forConstruction=True)
    .vertices()
    .cboreHole(2.4, 4.4, 2.1)
)
```
