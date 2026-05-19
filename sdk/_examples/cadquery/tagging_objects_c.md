---
title: '对象标记'
description: '`Workplane.tag()` 可为链中某一对象打上字符串标记，以便后续步骤引用。'
tags:
  - cadquery
  - examples
  - tagging
  - objects
---
# 对象标记

`Workplane.tag()` 可为链中某一对象打上字符串标记，以便后续步骤引用。

`Workplane.workplaneFromTagged()` 对标记对象应用 `Workplane.copyWorkplane()`。例如从同一面挤出两个不同实体后，再用普通选择器找回原面会变得困难。

```python
result = (
    cq.Workplane("XY")
    # create and tag the base workplane
    .box(10, 10, 10)
    .faces(">Z")
    .workplane()
    .tag("baseplane")
    # extrude a cylinder
    .center(-3, 0)
    .circle(1)
    .extrude(3)
    # to reselect the base workplane, simply
    .workplaneFromTagged("baseplane")
    # extrude a second cylinder
    .center(3, 0)
    .circle(1)
    .extrude(2)
)
```

标记还可与多数选择器联用，包括 `Workplane.vertices()`、`Workplane.faces()`、`Workplane.edges()`、`Workplane.wires()`、`Workplane.shells()`、`Workplane.solids()` 与 `Workplane.compounds()`。

```python
result = (
    cq.Workplane("XY")
    # create a triangular prism and tag it
    .polygon(3, 5)
    .extrude(4)
    .tag("prism")
    # create a sphere that obscures the prism
    .sphere(10)
    # create features based on the prism's faces
    .faces("<X", tag="prism")
    .workplane()
    .circle(1)
    .cutThruAll()
    .faces(">X", tag="prism")
    .faces(">Y")
    .workplane()
    .circle(1)
    .cutThruAll()
)
```
