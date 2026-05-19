# 工作平面 — CadQuery 文档

## 概述

多数 CAD 程序使用工作平面概念。若有其他 CAD 经验，CadQuery 工作平面应较熟悉；若无，工作平面是需掌握的基本概念。

工作平面表示空间中的一个平面，其他特征相对其定位。有中心点与局部坐标系。多数创建对象的方法相对**当前**工作平面操作。

通常第一个工作平面是 `"XY"` 平面，也称「前」平面。定义实体后，常见做法是在要修改的面上选面并创建相对该面的新工作平面。也可在世界坐标系任意位置创建，或相对其他平面偏移/旋转。

工作平面最有力的特性是：可在工作平面坐标系中用 2D 坐标创作，CadQuery 再变换到世界坐标系，使 3D 特征落在预期位置，脚本更易编写与维护。

## 2D 构造

创建工作平面后可在 2D 中操作，再将特征用于 3D。提供预期的 2D 构造——圆、线、弧、镜像、点等。

## 3D 构造

可直接构造盒、楔、圆柱、球等 3D 基元，也可拉伸、扫掠、放样 2D 几何。基本基元操作同样可用。

## 常见陷阱：重复面工作平面

从选定面创建新工作平面时，CadQuery 默认**不一定**将原点保持在全局模型原点，而是将上一工作平面原点投影到该面。因此重复模式如：

```python
for angle in angles:
    body = (
        body.faces(">Z")
        .workplane()
        .transformed(rotate=(0, 0, angle))
        .center(radius, 0)
        .circle(hole_radius)
        .cutThruAll()
    )
```

在第一次特征后可能**漂移**——后续切除可能相对上一次切除的局部系而非模型中心。

对重复径向或对称特征，优先：

- 从固定全局工作平面如 `cq.Workplane("XY")` 建刀具，再用 `body.cut(cutter)` 减去。
- 用 `tag` 标记并复用稳定基工作平面，勿在循环内反复从面新建。
- 需要特定面局部原点时，创建面工作平面时有意使用 `centerOption=`。

## 选择器

选择器用于选一个或多个特征以定义新特征。例如拉伸盒体后选顶面放置特征，或选所有竖直边倒圆角。

可选择的类型：顶点、边、面、实体、线框。

选择器相当于传统 CAD 中用鼠标点选。

## 构造几何

构造几何不属于零件本身，仅辅助定位。常见用法：定义矩形，再用角点定位一组孔。

多数 CadQuery 构造方法提供 `forConstruction` 关键字，创建仅用于定位其他特征的几何。

## 栈（The Stack）

CadQuery 中每次操作返回带该操作结果的新 `Workplane`，含对象列表与父引用。

可随时回退：例如

```python
Workplane(someObject).faces(">Z").first().vertices()
```

返回最高面上所有顶点的 CadQuery 对象；也可 `.end()` 回到面：

```python
Workplane(someObject).faces(">Z").first().vertices().end()
```

## 链式调用

所有 `Workplane` 方法返回另一个 `Workplane` 以便流畅链式调用；用核心方法访问创建的对象。

链式调用中每次产生新 `Workplane` 时，其 `parent` 指向创建它的对象。若干方法会沿父链搜索（如查找上下文实体）。也可 `tag` 标记对象，后续用标签引用。

## 上下文实体（Context Solid）

多数时候只建一个对象并持续加特征。CadQuery 监视操作，将**第一个**创建的实体定为「上下文实体」；之后创建的特征默认与之合并（除非另指定）。即使实体在栈深处创建，例如：

```python
Workplane("XY").box(1, 2, 3).faces(">Z").circle(0.25).extrude(1)
```

得到 1×2×3 盒体，顶面圆柱凸台；无需手动合并，`extrude` 默认与上下文实体合并。`hole()` 类似——默认从上下文实体减去。

若要避免，设 `combine=False`，CadQuery 将单独创建实体。

## 迭代

CAD 模型常有重复几何；CadQuery 许多方法自动对栈上**每个**元素操作，无需手写 for 循环：

```python
Workplane("XY").box(1, 2, 3).faces(">Z").vertices().circle(0.5)
```

矩形面有 4 个顶点，`vertices()` 选 4 个顶点，`circle()` 对栈上每项迭代，故实际创建 4 个圆。

编写插件时值得记住；`cadquery.Workplane.each()` 很有用。

## 自省示例

**注意：** 刚学 CadQuery 可稍后阅读。若已有建模经验并想读源码理解行为，建议先读此例。

可为 `Workplane`、`Plane`、`CQContext` 定义更详细的 `__str__` 并补丁：

```python
import cadquery as cq

def tidy_repr(obj):
    """Shortens a default repr string"""
    return repr(obj).split(".")[-1].rstrip(">")

def _ctx_str(self):
    return (
        tidy_repr(self)
        + ":\n"
        + f" pendingWires: {self.pendingWires}\n"
        + f" pendingEdges: {self.pendingEdges}\n"
        + f" tags: {self.tags}"
    )

cq.cq.CQContext.__str__ = _ctx_str

def _plane_str(self):
    return (
        tidy_repr(self)
        + ":\n"
        + f" origin: {self.origin.toTuple()}\n"
        + f" z direction: {self.zDir.toTuple()}"
    )

cq.occ_impl.geom.Plane.__str__ = _plane_str

def _wp_str(self):
    out = tidy_repr(self) + ":\n"
    out += f" parent: {tidy_repr(self.parent)}\n" if self.parent else " no parent\n"
    out += f" plane: {self.plane}\n"
    out += f" objects: {self.objects}\n"
    out += f" modelling context: {self.ctx}"
    return out

cq.Workplane.__str__ = _wp_str
```

然后分步构造零件并检查每步的 `Workplane` 与 `CQContext`。最终零件构造链：

```python
part = (
    cq.Workplane()
    .box(1, 1, 1)
    .tag("base")
    .wires(">Z")
    .toPending()
    .translate((0.1, 0.1, 1.0))
    .toPending()
    .loft()
    .faces(">>X", tag="base")
    .workplane(centerOption="CenterOfMass")
    .circle(0.2)
    .extrude(1)
)
```

**注意：** 此例部分建模过程为演示而略显刻意，非最佳流畅写法。

### 分步分析

链的起点：

```python
part = cq.Workplane()
print(part)
```

输出示例：

```
Workplane object at 0x2760:
  no parent
  plane: Plane object at 0x2850:
    origin: (0.0, 0.0, 0.0)
    z direction: (0.0, 0.0, 1.0)
  objects: []
  modelling context: CQContext object at 0x2730:
    pendingWires: []
    pendingEdges: []
    tags: {}
```

这是空 `Workplane`；链中第一个，无 `parent`；`plane` 为 XY 平面。

`box(1,1,1)` 后得到新 `Workplane`，`parent` 指向前一步；`objects` 含一个 `Solid`；`ctx` 在链中共享（地址如 `0x2730`）。新 `Workplane()` 会有不同 `CQContext`。

`tag("base")` **返回同一** `Workplane` 实例（`tag` 是少数不返回新对象的方法之一）；`tags` 字典记录名称。

`faces(">>Z")` 从父 `Solid` 取 Z 最远面放入 `objects`，`Solid` 不再在栈顶；需要实体时沿父链 `findSolid()`。

`wires()` 将面边界放入 `objects` 为 `Wire`。

`toPending()` 将线框推入 `ctx.pendingWires`，同样常返回同一对象。

`translate` 改变 `objects` 中的 `Wire`；再次 `toPending()` 使 `pendingWires` 含两条线框供 `loft()`。

`loft()` 清空 `pendingWires`，`objects` 为 `Compound`。

`faces(">>X", tag="base")` 用标签 `base` 在父链找面；`workplane()` 建立法向沿 +X 的新平面，`objects` 清空。

`circle(0.2)` 将圆放入 `objects` 与 `pendingWires`。

`extrude(1, clean=False)` 生成凸台 `Compound`；`clean=True`（默认）时中间还会多一层 `Workplane` 在 `parent` 链中。

**说明：** `extrude` 的 `clean` 默认为 `True`：先拉伸再 `clean()` 精炼；示例 `clean=False` 便于观察上一步对象仍在 `parent` 中。
