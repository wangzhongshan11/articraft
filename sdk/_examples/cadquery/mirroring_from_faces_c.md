---
title: '基于面的镜像'
description: '演示如何选定某个面作为镜像平面，对实体进行镜像，并可立即将镜像体与原几何做并集，得到对称或加倍结构。'
tags:
  - cadquery
  - examples
  - mirroring
  - from
  - faces
---
# 基于面的镜像

本示例先挤出一段 L 形截面，再调用 `mirror()` 并传入 `result.faces(">X")` 作为镜像参考面；`union=True` 会在镜像完成后立刻与原实体合并。适合需要“以现有面为对称面、一次完成镜像+合并”的场景，避免手动复制与对齐。

```python
result = cq.Workplane("XY").line(0, 1).line(1, 0).line(0, -0.5).close().extrude(1)

result = result.mirror(result.faces(">X"), union=True)
```
