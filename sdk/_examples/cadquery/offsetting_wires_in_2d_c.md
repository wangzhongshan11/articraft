---
title: '二维线框偏移'
description: '二维线框可通过 `Workplane.offset2D()` 进行内外偏移，并在拐角处选用不同的延伸/连接策略。'
tags:
  - cadquery
  - examples
  - offsetting
  - wires
  - in
  - 2d
---
# 二维线框偏移

二维线框可通过 `Workplane.offset2D()` 向内或向外偏移；拐角处理可选圆弧（`arc`）或延伸相交（`intersection`）等模式，见第一段示例对比。

```python
original = cq.Workplane().polygon(5, 10).extrude(0.1).translate((0, 0, 2))
arc = cq.Workplane().polygon(5, 10).offset2D(1, "arc").extrude(0.1).translate((0, 0, 1))
intersection = cq.Workplane().polygon(5, 10).offset2D(1, "intersection").extrude(0.1)
result = original.add(arc).add(intersection)
```

借助 `forConstruction=True`，可把螺栓孔阵列相对零件外轮廓整体内缩——下面在沉头孔示例基础上，将孔位从边缘偏移得到。

```python
result = (
    cq.Workplane()
    .box(4, 2, 0.5)
    .faces(">Z")
    .edges()
    .toPending()
    .offset2D(-0.25, forConstruction=True)
    .vertices()
    .cboreHole(0.125, 0.25, 0.125, depth=None)
)
```

注意：`Workplane.edges()` 仅用于**选择**对象，不会把选中的边加入建模上下文的 pending 边列表；否则下一次拉伸可能把“仅用于选择”的边一并挤出。若希望这些边参与 `Workplane.offset2D()`，需显式调用 `Workplane.toPending()` 将其加入 pending。
