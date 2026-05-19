---
title: '拉伸至指定面'
description: '当目标面非平面或挤出距离难算时，可用 extrude/cutBlind 的 until 参数（next、last 或 Face 对象）定终止面。'
tags:
  - cadquery
  - examples
  - 拉伸
  - 至面
  - 截止面
---
# 拉伸至指定面

有时需要将线框**拉伸到某一终止面**，而该面可能**非平面**，或难以预先算出精确挤出深度。此时可在 `extrude()` 的 `until` 参数中使用 `"next"`、`"last"`，或直接传入 `Face` 对象。`cutBlind()` 同样支持该语义，且可对多条 `Wire` 同时操作。

---

## 示例一：`extrude("next")`

先旋转半圆生成曲面体，再在其上建矩形轮廓，挤出至遇到的**下一面**为止。

```python
result = (
    cq.Workplane(origin=(20, 0, 0))
    .circle(2)
    .revolve(180, (-20, 0, 0), (-20, -1, 0))
    .center(-20, 0)
    .workplane()
    .rect(20, 4)
    .extrude("next")
)
```

---

## 示例二：`cutBlind("last")` 与多线框

`extrude()` 与 `cutBlind()` 行为一致；可对多个线框同时处理。先用 `eachpoint` + `loft` 生成多栋「摩天楼」轮廓，再整体变换并在一组顶点圆处 `cutBlind("last")` 切至最后相交面。

```python
skyscrapers_locations = [(-16, 1), (-8, 0), (7, 0.2), (17, -1.2)]
angles = iter([15, 0, -8, 10])
skyscrapers = (
    cq.Workplane()
    .pushPoints(skyscrapers_locations)
    .eachpoint(
        lambda loc: (
            cq.Workplane()
            .rect(5, 16)
            .workplane(offset=10)
            .ellipse(3, 8)
            .workplane(offset=10)
            .slot2D(20, 5, 90)
            .loft()
            .rotateAboutCenter((0, 0, 1), next(angles))
            .val()
            .located(loc)
        )
    )
)

result = (
    skyscrapers.transformed((0, -90, 0))
    .moveTo(15, 0)
    .rect(3, 3, forConstruction=True)
    .vertices()
    .circle(1)
    .cutBlind("last")
)
```

---

## 示例三：曲面上切除与再挤出

典型场景：在**曲面**上截止拉伸或切除，避免与曲面重叠导致的布尔瑕疵。球体与盒体组合后，选取特定球面作为 `cutBlind` 的目标面，再在另一工作平面 `extrude("next")` 继续特征。

```python
import cadquery as cq

sphere = cq.Workplane().sphere(5)
base = cq.Workplane(origin=(0, 0, -2)).box(12, 12, 10).cut(sphere).edges("|Z").fillet(2)
sphere_face = base.faces(">>X[2] and (not |Z) and (not |Y)").val()
base = base.faces("<Z").workplane().circle(2).extrude(10)

shaft = cq.Workplane().sphere(4.5).circle(1.5).extrude(20)

spherical_joint = (
    base.union(shaft)
    .faces(">X")
    .workplane(centerOption="CenterOfMass")
    .move(0, 4)
    .slot2D(10, 2, 90)
    .cutBlind(sphere_face)
    .workplane(offset=10)
    .move(0, 2)
    .circle(0.9)
    .extrude("next")
)

result = spherical_joint
```

---

**警告：** 若待拉伸线框**无法完整投影**到目标面，结果可能不可预测。算法会沿挤出方向从线框中心发射直线，统计与哪些面相交以确定候选面。请确保线框可投影到目标面，以免出现异常几何。
