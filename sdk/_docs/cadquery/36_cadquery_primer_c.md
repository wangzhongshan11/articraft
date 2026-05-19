# 概述

在讨论 CadQuery 之前，先简要说明 3D CAD 拓扑。CadQuery 基于 OpenCascade 内核，用边界表示（BREP）定义对象，即由包围表面定义物体。

在 BREP 系统中，自下而上定义形状的基本构造为：

- **vertex（顶点）** — 空间中一点
- **edge（边）** — 沿某路径（曲线）连接两个或多个顶点
- **wire（线框）** — 首尾相连的边集合
- **face（面）** — 由边或线框围成的表面
- **shell（壳）** — 沿部分边相连的面集合
- **solid（实体）** — 内部闭合的壳
- **compound（复合体）** — 实体集合

使用 CadQuery 时，希望以最少工作量创建上述对象。实际 CAD 内核中还有几何构造（如圆弧边引用完整圆曲线、直线边引用直线方程）。CadQuery 将这些与使用者隔离。

## CadQuery API 层次

深入 CadQuery 后，可能对 API 返回的不同对象类型感到困惑。本章说明各层及底层实现，便于更好利用 CadQuery。

CadQuery 由 4 层 API 叠建而成。

1. 流畅 API（Fluent API）
   - `Workplane`
   - `Sketch`
   - `Assembly`

2. 直接 API（Direct API）
   - `Shape`

3. 几何 API（Geometry API）
   - `Vector`
   - `Plane`
   - `Location`

4. OCCT API

### 流畅 API

所谓流畅 API 即初学时主要接触的 `Workplane` 及其方法。这是最常见、较易用的 API，简化许多操作。典型示例：

```python
part = Workplane("XY").box(1, 2, 3).faces(">Z").vertices().circle(0.5).cutThruAll()
```

此处创建 [`Workplane`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Workplane "cadquery.Workplane")，再链式调用方法构造零件。可把 [`Workplane`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Workplane "cadquery.Workplane") 视为零件对象，其方法为作用于零件的操作。常从空 [`Workplane`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Workplane "cadquery.Workplane") 开始，再调用方法添加特征。

流畅 API 的层次结构常体现为：

```python
part = Workplane("XY").box(1, 2, 3).faces(">Z").vertices().circle(0.5).cutThruAll()
```

或分步：

```python
part = Workplane("XY")
part = part.box(1, 2, 3)
part = part.faces(">Z")
part = part.vertices()
part = part.circle(0.5)
part = part.cutThruAll()
```

> 注意：第一种写法虽常见，但与单行等价，逐步调试较难；CQ-Editor 等可提供分步可视化。

### 直接 API

流畅 API 功能虽多，某些场景需要更灵活或更低层对象。

直接 API 是流畅 API 底层调用的 API，由九种拓扑类及其方法构成，包装等价 OCCT 类：

1. `Shape`
2. `Compound`
3. `CompSolid`
4. `Solid`
5. `Shell`
6. `Face`
7. `Wire`
8. `Edge`
9. `Vertex`

各类有创建/编辑对应形状的方法；也可用 freefuncapi。拓扑类有层次：Wire 由多条 Edge 组成，Edge 由顶点组成，自下而上可精细控制。

例如创建圆面：

```python
circle_wire = Wire.makeCircle(10, Vector(0, 0, 0), Vector(0, 0, 1))
circular_face = Face.makeFromWires(circle_wire, [])
```

注意

在 CadQuery（及 OCCT）中，各拓扑类都是 shape；[`Shape`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Shape "cadquery.Shape") 为最抽象拓扑类。子类继承 `Mixin3D` 或 `Mixin1D` 以共享方法。

直接 API 无父子数据结构，每次调用直接返回指定拓扑类型对象；比流畅 API 冗长，但更灵活（例如可直接操作 Face，流畅 API 中不便）。

### OCCT API

OCCT API 是 CadQuery 最底层。直接 API 建立在 OCCT API 之上；CadQuery 中通过 OCP 暴露 OCCT C++ 库的 Python 绑定，可访问（几乎）全部 OCCT 库。使用 OCCT API 灵活性最大，但非常冗长难用，需熟悉各 C++ 库；一般应避免。

### 各 API 层之间切换

三层 API 复杂度与功能不同，可混合使用。以下为各层互操作方式。

#### 流畅 API <=> 直接 API

从流畅 API 链末端取直接 API（拓扑）对象：

用 [`Workplane.val()`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Workplane.val "cadquery.Workplane.val") 取栈顶对象，[`Workplane.vals()`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Workplane.vals "cadquery.Workplane.vals") 取全部。

```python
>>> box = Workplane().box(10, 5, 5)
>>> print(type(box))
<class cadquery.cq.Workplane>
```

```python
>>> box = Workplane().box(10, 5, 5).val()
>>> print(type(box))
<class cadquery.occ_impl.shapes.Solid>
```

若只关心工作平面的上下文实体，可用 [`Workplane.findSolid()`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Workplane.findSolid "cadquery.Workplane.findSolid")：

```python
>>> part = Workplane().box(10,5,5).circle(3).val()
>>> print(type(part))
<class cadquery.cq.Wire>
```

```python
>>> part = Workplane().box(10,5,5).circle(3).findSolid()
>>> print(type(part))
<class cadquery.occ_impl.shapes.Compound>
# findSolid 返回 Solid 或 Compound
```

反向：将拓扑对象作为 [`Workplane`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Workplane "cadquery.Workplane") 的基对象：

```python
solid_box = Solid.makeBox(10, 10, 10)
part = Workplane(obj=solid_box)
# 可继续在流畅 API 中建模
part = part.faces(">Z").circle(1).extrude(10)
```

用 [`Workplane.newObject()`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Workplane.newObject "cadquery.Workplane.newObject") 将拓扑对象作为流畅链中新步骤：

```python
circle_wire = Wire.makeCircle(1, Vector(0, 0, 0), Vector(0, 0, 1))
box = Workplane().box(10, 10, 10).newObject([circle_wire])
# 继续建模
box = (
    box.toPending().cutThruAll()
)  # 后续操作用到 pending 时需 toPending
```

#### 直接 API <=> OCCT API

直接 API 各对象在 `wrapped` 属性中保存 OCCT 等价对象：

```python
>>> box = Solid.makeBox(10,5,5)
>>> print(type(box))
<class cadquery.occ_impl.shapes.Solid>
```

```python
>>> box = Solid.makeBox(10,5,5).wrapped
>>> print(type(box))
<class OCP.TopoDS.TopoDS_Solid>
```

将 OCCT 对象转为直接 API 对象时，作为参数传给目标类：

```python
>>> occt_box = BRepPrimAPI_MakeBox(5,5,5).Solid()
>>> print(type(occt_box))
<class OCP.TopoDS.TopoDS_Solid>
```

```python
>>> direct_api_box = Solid(occt_box)
>>> print(type(direct_api_box))
<class cadquery.occ_impl.shapes.Solid>
```

注意

多方法（Multimethods）

CadQuery 用 Multimethod 按参数类型分发方法。例如 [`arc()`](https://cadquery.readthedocs.io/en/latest/classreference.html#cadquery.Sketch.arc "cadquery.Sketch.arc") 中 `a_sketch.arc((1, 2), (2, 3))` 与 `a_sketch.arc((1, 2), (2, 3), (3, 4))` 会分到不同实现。多方法生效时**不要**用关键字参数指定本应按位置传递的参数。例如**不要**写 `a_sketch.arc(p1=(1, 2), p2=(2, 3), p3=(3, 4))`，应使用前述位置参数形式。分发失败时 CadQuery 会尝试回退到首个注册的多方法，但仍应避免对位置参数使用关键字。

选择器（Selectors）

选择器用于选一个或多个特征以定义新特征。例如拉伸盒体后选顶面放置新特征，或选所有竖直边倒圆角。

可用选择器选择顶点、边、面、实体与线框。

选择器相当于在传统 CAD 中用鼠标选择。

Workplane 类

`Workplane` 含当前选中对象（`objects` 属性中的 Shape、Vector 或 Location 列表）、建模上下文（`ctx`）及流畅 API 方法，是用户最常实例化的类。

详见 [API Reference](https://cadquery.readthedocs.io/en/latest/apireference.html#apireference)。

装配（Assemblies）

简单模型可组合为复杂、可嵌套的装配。

![Image 1: _images/assy.png](https://cadquery.readthedocs.io/en/latest/_images/assy.png)

简单示例：

```python
from cadquery import *

w = 10
d = 10
h = 10

part1 = Workplane().box(2 * w, 2 * d, h)
part2 = Workplane().box(w, d, 2 * h)
part3 = Workplane().box(w, d, 3 * h)

assy = (
    Assembly(part1, loc=Location(Vector(-w, 0, h / 2)))
    .add(
        part2, loc=Location(Vector(1.5 * w, -0.5 * d, h / 2)), color=Color(0, 0, 1, 0.5)
    )
    .add(part3, loc=Location(Vector(-0.5 * w, -0.5 * d, 2 * h)), color=Color("red"))
)
```

子零件位置相对父装配定义——上例中 `part3` 在全球坐标约为 (-5,-5,20)。可用颜色区分装配并导出 STEP 或 OCCT XML。

带约束的装配

有时不宜显式给定组件位置，而应用约束得到全参数化装配：

```python
from cadquery import *

w = 10
d = 10
h = 10

part1 = Workplane().box(2 * w, 2 * d, h)
part2 = Workplane().box(w, d, 2 * h)
part3 = Workplane().box(w, d, 3 * h)

assy = (
    Assembly(part1, name="part1", loc=Location(Vector(-w, 0, h / 2)))
    .add(part2, name="part2", color=Color(0, 0, 1, 0.5))
    .add(part3, name="part3", color=Color("red"))
    .constrain("part1@faces@>Z", "part3@faces@<Z", "Axis")
    .constrain("part1@faces@>Z", "part2@faces@<Z", "Axis")
    .constrain("part1@faces@>Y", "part3@faces@<Y", "Axis")
    .constrain("part1@faces@>Y", "part2@faces@<Y", "Axis")
    .constrain("part1@vertices@>(-1,-1,1)", "part3@vertices@>(-1,-1,-1)", "Point")
    .constrain("part1@vertices@>(1,-1,-1)", "part2@vertices@>(-1,-1,-1)", "Point")
    .solve()
)
```

与上一节显式定位结果相同，但改 `w`、`d`、`h` 时位置自动重算。可用标签简化约束：

```python
from cadquery import *

w = 10
d = 10
h = 10

part1 = Workplane().box(2 * w, 2 * d, h)
part2 = Workplane().box(w, d, 2 * h)
part3 = Workplane().box(w, d, 3 * h)

part1.faces(">Z").edges("<X").vertices("<Y").tag("pt1")
part1.faces(">X").edges("<Z").vertices("<Y").tag("pt2")
part3.faces("<Z").edges("<X").vertices("<Y").tag("pt1")
part2.faces("<X").edges("<Z").vertices("<Y").tag("pt2")

assy1 = (
    Assembly(part1, name="part1", loc=Location(Vector(-w, 0, h / 2)))
    .add(part2, name="part2", color=Color(0, 0, 1, 0.5))
    .add(part3, name="part3", color=Color("red"))
    .constrain("part1@faces@>Z", "part3@faces@<Z", "Axis")
    .constrain("part1@faces@>Z", "part2@faces@<Z", "Axis")
    .constrain("part1@faces@>Y", "part3@faces@<Y", "Axis")
    .constrain("part1@faces@>Y", "part2@faces@<Y", "Axis")
    .constrain("part1?pt1", "part3?pt1", "Point")
    .constrain("part1?pt2", "part2?pt2", "Point")
    .solve()
)
```

当前实现的约束类型：

- **Axis**：两法向反平行或夹角等于给定值（弧度）。适用于具一致法向的实体——平面、线框、边。
- **Point**：两点重合或相距给定距离。适用于所有实体；线/面/实体用质心，顶点用顶点位置。
- **Plane**：`Axis` 与 `Point` 的组合。
