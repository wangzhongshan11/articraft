# 草图教程（Sketch Tutorial）

本节演示用不同方式构造草图。

## 基于面的 API

构造草图的主要方式是基于面，并用布尔运算组合。

```python
import cadquery as cq

result = (
    cq.Sketch()
    .trapezoid(4, 3, 90)
    .vertices()
    .circle(0.5, mode="s")
    .reset()
    .vertices()
    .fillet(0.25)
    .reset()
    .rarray(0.6, 1, 5, 1)
    .slot(1.5, 0.4, mode="s", angle=90)
)
```

注意实现了选择器，但选择须显式 `reset`。`Sketch` 无历史，修改就地发生。

### 模式（Modes）

面 API 的每个操作接受 `mode` 参数定义与已有对象如何组合：融合（`mode='a'`）、切除（`mode='s'`）、相交（`mode='i'`）、替换（`mode='r'`）或仅作构造存储（`mode='c'`）。后者必须指定 `tag` 以便后续引用。默认融合。上例演示了减与加模式；下面演示另两种。

```python
result = (
    cq.Sketch()
    .rect(1, 2, mode="c", tag="base")
    .vertices(tag="base")
    .circle(0.7)
    .reset()
    .edges("|Y", tag="base")
    .ellipse(1.2, 1, mode="i")
    .reset()
    .rect(2, 2, mode="i")
    .clean()
)
```

## 基于边的 API

需要时可逐条边构造草图。

```python
import cadquery as cq

result = (
    cq.Sketch()
    .segment((0.0, 0), (0.0, 2.0))
    .segment((2.0, 0))
    .close()
    .arc((0.6, 0.6), 0.4, 0.0, 360.0)
    .assemble(tag="face")
    .edges("%LINE", tag="face")
    .vertices()
    .chamfer(0.2)
)
```

完成后须用 `assemble()` 转为基于面的表示，再应用面 API 操作。

## 凸包（Convex Hull）

**警告：** 凸包功能目前为实验性。

特殊场景可用直线段与圆弧构造凸包。

```python
result = (
    cq.Sketch()
    .arc((0, 0), 1.0, 0.0, 360.0)
    .arc((1, 1.5), 0.5, 0.0, 360.0)
    .segment((0.0, 2), (-1, 3.0))
    .hull()
)
```

## 基于约束的草图

**警告：** 2D 草图约束与求解器目前为实验性。

可用几何约束构造草图；目前仅线段与圆弧。

```python
import cadquery as cq

result = (
    cq.Sketch()
    .segment((0, 0), (0, 3.0), "s1")
    .arc((0.0, 3.0), (1.5, 1.5), (0.0, 0.0), "a1")
    .constrain("s1", "Fixed", None)
    .constrain("s1", "a1", "Coincident", None)
    .constrain("a1", "s1", "Coincident", None)
    .constrain("s1", "a1", "Angle", 45)
    .solve()
    .assemble()
)
```

`constrain()` 的参数以一个元组传入。表中 0..1 表示 0（元素起点）到 1（终点）之间的浮点位置。

| 名称 | 元数 | 实体 | 参数 | 说明 |
|------|-------|----------|-----------|-------------|
| FixedPoint | 1 | 全部 | 圆弧圆心为 None，段/弧上点为 0..1 | 指定点固定 |
| Coincident | 2 | 全部 | None | 指定点重合 |
| Angle | 2 | 全部 | angle | 两实体切线夹角固定 |
| Length | 1 | 全部 | length | 实体长度固定 |
| Distance | 2 | 全部 | None 或 0..1 对、distance | 两点距离固定 |
| Radius | 1 | Arc | radius | 圆弧半径固定 |
| Orientation | 1 | Segment | x,y | 与 (x,y) 平行 |
| ArcAngle | 1 | Arc | angle | 圆弧角跨度固定 |

## 与工作平面集成

草图创建后可在工作平面上 `extrude()`、`twistExtrude()`、`revolve()`、`sweep()`、`cutBlind()`、`cutThruAll()`、`loft()` 等。

草图可单独创建复用，也可在一条流畅链中就地创建，见下。

### 就地草图

```python
import cadquery as cq

result = (
    cq.Workplane()
    .box(5, 5, 1)
    .faces(">Z")
    .sketch()
    .regularPolygon(2, 3, tag="outer")
    .regularPolygon(1.5, 3, mode="s")
    .vertices(tag="outer")
    .fillet(0.2)
    .finalize()
    .extrude(0.5)
)
```

`sketch()` 之后可用草图 API，并保留原工作平面。

### 将已有草图放到工作平面

用 `placeSketch()` 原样放置已有草图。

```python
import cadquery as cq

s = cq.Sketch().trapezoid(3, 1, 110).vertices().fillet(0.2)

result = (
    cq.Workplane()
    .box(5, 5, 5)
    .faces(">X")
    .workplane()
    .transformed((0, 0, -90))
    .placeSketch(s)
    .cutThruAll()
)
```

### 跨多个元素的草图

构造草图前若选中多个元素，会创建多个草图。

草图会放在栈顶所有位置上。

```python
import cadquery as cq

result = (
    cq.Workplane()
    .box(5, 5, 1)
    .faces(">Z")
    .workplane()
    .rarray(2, 2, 2, 2)
    .rect(1.5, 1.5)
    .extrude(0.5)
    .faces(">Z")
    .sketch()
    .circle(0.4)
    .wires()
    .distribute(6)
    .circle(0.1, mode="a")
    .clean()
    .finalize()
    .cutBlind(-0.5, taper=10)
)
```

### 两草图间放样

`loft()` 需要不同工作平面上的两个草图。

```python
from cadquery import Workplane, Sketch, Vector, Location

s1 = Sketch().trapezoid(3, 1, 110).vertices().fillet(0.2)

s2 = Sketch().rect(2, 1).vertices().fillet(0.2)

result = Workplane().placeSketch(s1, s2.moved(z=3)).loft()
```

放样仅考虑外周线框，内线框静默忽略。仅栈顶草图参与当前操作（无 pending 草图），故 loft/sweep 时须在一次 `placeSketch` 中加入全部相关草图。

### 组合草图

用 `face()` 组合草图：

```python
import cadquery as cq

s1 = cq.Sketch().rect(2, 2)
s2 = cq.Sketch().circle(0.5)

result = s1.face(s2, mode='s')
```

也可用布尔运算：

```python
import cadquery as cq

s1 = cq.Sketch().rect(2, 2).vertices().fillet(0.25).reset()
s2 = cq.Sketch().rect(1, 1, angle=45).vertices().chamfer(0.1).reset()

result = s1 - s2
```

布尔运算对选择敏感，此例需 `reset()`。

### 偏移

可复用草图做 `offset()`：

```python
import cadquery as cq

sketch = (cq.Sketch()
    .rect(1.0, 4.0)
    .circle(1.0)
    .clean()
)

sketch_offset = sketch.copy().wires().offset(0.25)

result = cq.Workplane("front").placeSketch(sketch_offset).extrude(1.0)
result = result.faces(">Z").workplane().placeSketch(sketch).cutBlind(-0.50)
```

负偏移需谨慎 `mode`；常需 `mode='r'` 替换原面。

```python
import cadquery as cq

sketch = (cq.Sketch()
    .rect(1.0, 4.0)
    .circle(1.0)
    .clean()
)

sketch_offset = sketch.copy().wires().offset(-0.25, mode='r')

result = cq.Workplane("front").placeSketch(sketch).extrude(1.0)
result = result.faces(">Z").workplane().placeSketch(sketch_offset).cutBlind(-0.50)
```

### 导出与导入

草图可用 `export()` 导出；亦支持 `importDXF()` 导入 DXF。
