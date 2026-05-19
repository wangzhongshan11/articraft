# 装配教程（Assembly Tutorial）

本节演示装配与约束功能，构建逼真的机箱门装配（20×20 v-slot 型材）。

## 定义参数

先定义模型参数，便于后续改尺寸：

```python
import cadquery as cq

# Parameters
H = 400
W = 200
D = 350

PROFILE = cq.importers.importDXF("vslot-2020_1.dxf").wires()

SLOT_D = 5
PANEL_T = 3

HANDLE_D = 20
HANDLE_L = 50
HANDLE_W = 4
```

v-slot 截面从 DXF 导入，便于换成 Item、Bosch 等型材；厂商常提供 DXF。

## 定义可复用组件

定义按参数生成装配组件的函数：

```python
def make_vslot(l):
    return PROFILE.toPending().extrude(l)

def make_connector():
    rv = (
        cq.Workplane()
        .box(20, 20, 20)
        .faces("<X")
        .workplane()
        .cboreHole(6, 15, 18)
        .faces("<Z")
        .workplane(centerOption="CenterOfMass")
        .cboreHole(6, 15, 18)
    )

    # tag mating faces
    rv.faces(">X").tag("X").end()
    rv.faces(">Z").tag("Z").end()

    return rv

def make_panel(w, h, t, cutout):
    rv = (
        cq.Workplane("XZ")
        .rect(w, h)
        .extrude(t)
        .faces(">Y")
        .vertices()
        .rect(2 * cutout, 2 * cutout)
        .cutThruAll()
        .faces("<Y")
        .workplane()
        .pushPoints([(-w / 3, HANDLE_L / 2), (-w / 3, -HANDLE_L / 2)])
        .hole(3)
    )

    # tag mating edges
    rv.faces(">Y").edges("%CIRCLE").edges(">Z").tag("hole1")
    rv.faces(">Y").edges("%CIRCLE").edges("<Z").tag("hole2")

    return rv

def make_handle(w, h, r):
    pts = ((0, 0), (w, 0), (w, h), (0, h))

    path = cq.Workplane().polyline(pts)

    rv = (
        cq.Workplane("YZ")
        .rect(r, r)
        .sweep(path, transition="round")
        .tag("solid")
        .faces("<X")
        .workplane()
        .faces("<X", tag="solid")
        .hole(r / 1.5)
    )

    # tag mating faces
    rv.faces("<X").faces(">Y").tag("mate1")
    rv.faces("<X").faces("<Y").tag("mate2")

    return rv
```

## 初始装配

实例化组件并加入装配：

```python
# define the elements
door = (
    cq.Assembly()
    .add(make_vslot(H), name="left")
    .add(make_vslot(H), name="right")
    .add(make_vslot(W), name="top")
    .add(make_vslot(W), name="bottom")
    .add(make_connector(), name="con_tl", color=cq.Color("black"))
    .add(make_connector(), name="con_tr", color=cq.Color("black"))
    .add(make_connector(), name="con_bl", color=cq.Color("black"))
    .add(make_connector(), name="con_br", color=cq.Color("black"))
    .add(
        make_panel(W + SLOT_D, H + SLOT_D, PANEL_T, SLOT_D),
        name="panel",
        color=cq.Color(0, 0, 1, 0.2),
    )
    .add(
        make_handle(HANDLE_D, HANDLE_L, HANDLE_W),
        name="handle",
        color=cq.Color("yellow"),
    )
)
```

## 约束定义

定义全部约束：

```python
# define the constraints
(
    door
    # left profile
    .constrain("left@faces@<Z", "con_bl?Z", "Plane")
    .constrain("left@faces@<X", "con_bl?X", "Axis")
    .constrain("left@faces@>Z", "con_tl?Z", "Plane")
    .constrain("left@faces@<X", "con_tl?X", "Axis")
    # top
    .constrain("top@faces@<Z", "con_tl?X", "Plane")
    .constrain("top@faces@<Y", "con_tl@faces@>Y", "Axis")
    # bottom
    .constrain("bottom@faces@<Y", "con_bl@faces@>Y", "Axis")
    .constrain("bottom@faces@>Z", "con_bl?X", "Plane")
    # right connectors
    .constrain("top@faces@>Z", "con_tr@faces@>X", "Plane")
    .constrain("bottom@faces@<Z", "con_br@faces@>X", "Plane")
    .constrain("left@faces@>Z", "con_tr?Z", "Axis")
    .constrain("left@faces@<Z", "con_br?Z", "Axis")
    # right profile
    .constrain("right@faces@>Z", "con_tr@faces@>Z", "Plane")
    .constrain("right@faces@<X", "left@faces@<X", "Axis")
    # panel
    .constrain("left@faces@>X[-4]", "panel@faces@<X", "Plane")
    .constrain("left@faces@>Z", "panel@faces@>Z", "Axis")
    # handle
    .constrain("panel?hole1", "handle?mate1", "Plane")
    .constrain("panel?hole2", "handle?mate2", "Point")
)
```

若字符串选择器不够用（如 `BoxSelector`、自定义选择器类），可向 `cadquery.Assembly.constrain()` 直接传 `cadquery.Shape`：

```python
.constrain("part1@faces@>Z", "part3@faces@<Z", "Axis")
```

等价于：

```python
.constrain("part1", part1.faces(">z").val(), "part3", part3.faces("<Z").val(), "Axis")
```

须传单个 `cadquery.Shape`，用 `cadquery.Workplane.val()`，勿传整个 `Workplane`。

## 最终结果

完整代码含 `solve()`：

```python
import cadquery as cq

# Parameters
H = 400
W = 200
D = 350

PROFILE = cq.importers.importDXF("vslot-2020_1.dxf").wires()

SLOT_D = 6
PANEL_T = 3

HANDLE_D = 20
HANDLE_L = 50
HANDLE_W = 4

def make_vslot(l):
    return PROFILE.toPending().extrude(l)

def make_connector():
    rv = (
        cq.Workplane()
        .box(20, 20, 20)
        .faces("<X")
        .workplane()
        .cboreHole(6, 15, 18)
        .faces("<Z")
        .workplane(centerOption="CenterOfMass")
        .cboreHole(6, 15, 18)
    )

    # tag mating faces
    rv.faces(">X").tag("X").end()
    rv.faces(">Z").tag("Z").end()

    return rv

def make_panel(w, h, t, cutout):
    rv = (
        cq.Workplane("XZ")
        .rect(w, h)
        .extrude(t)
        .faces(">Y")
        .vertices()
        .rect(2 * cutout, 2 * cutout)
        .cutThruAll()
        .faces("<Y")
        .workplane()
        .pushPoints([(-w / 3, HANDLE_L / 2), (-w / 3, -HANDLE_L / 2)])
        .hole(3)
    )

    # tag mating edges
    rv.faces(">Y").edges("%CIRCLE").edges(">Z").tag("hole1")
    rv.faces(">Y").edges("%CIRCLE").edges("<Z").tag("hole2")

    return rv

def make_handle(w, h, r):
    pts = ((0, 0), (w, 0), (w, h), (0, h))

    path = cq.Workplane().polyline(pts)

    rv = (
        cq.Workplane("YZ")
        .rect(r, r)
        .sweep(path, transition="round")
        .tag("solid")
        .faces("<X")
        .workplane()
        .faces("<X", tag="solid")
        .hole(r / 1.5)
    )

    # tag mating faces
    rv.faces("<X").faces(">Y").tag("mate1")
    rv.faces("<X").faces("<Y").tag("mate2")

    return rv

# define the elements
door = (
    cq.Assembly()
    .add(make_vslot(H), name="left")
    .add(make_vslot(H), name="right")
    .add(make_vslot(W), name="top")
    .add(make_vslot(W), name="bottom")
    .add(make_connector(), name="con_tl", color=cq.Color("black"))
    .add(make_connector(), name="con_tr", color=cq.Color("black"))
    .add(make_connector(), name="con_bl", color=cq.Color("black"))
    .add(make_connector(), name="con_br", color=cq.Color("black"))
    .add(
        make_panel(W + 2 * SLOT_D, H + 2 * SLOT_D, PANEL_T, SLOT_D),
        name="panel",
        color=cq.Color(0, 0, 1, 0.2),
    )
    .add(
        make_handle(HANDLE_D, HANDLE_L, HANDLE_W),
        name="handle",
        color=cq.Color("yellow"),
    )
)

# define the constraints
(
    door
    # left profile
    .constrain("left@faces@<Z", "con_bl?Z", "Plane")
    .constrain("left@faces@<X", "con_bl?X", "Axis")
    .constrain("left@faces@>Z", "con_tl?Z", "Plane")
    .constrain("left@faces@<X", "con_tl?X", "Axis")
    # top
    .constrain("top@faces@<Z", "con_tl?X", "Plane")
    .constrain("top@faces@<Y", "con_tl@faces@>Y", "Axis")
    # bottom
    .constrain("bottom@faces@<Y", "con_bl@faces@>Y", "Axis")
    .constrain("bottom@faces@>Z", "con_bl?X", "Plane")
    # right connectors
    .constrain("top@faces@>Z", "con_tr@faces@>X", "Plane")
    .constrain("bottom@faces@<Z", "con_br@faces@>X", "Plane")
    .constrain("left@faces@>Z", "con_tr?Z", "Axis")
    .constrain("left@faces@<Z", "con_br?Z", "Axis")
    # right profile
    .constrain("right@faces@>Z", "con_tr@faces@>Z", "Plane")
    .constrain("right@faces@<X", "left@faces@<X", "Axis")
    # panel
    .constrain("left@faces@>X[-4]", "panel@faces@<X", "Plane")
    .constrain("left@faces@>Z", "panel@faces@>Z", "Axis")
    # handle
    .constrain("panel?hole1", "handle?mate1", "Plane")
    .constrain("panel?hole2", "handle?mate2", "Point")
)

# solve
door.solve()

show_object(door, name="door")
```

## 数据导出

可导出 STEP 或 OCCT 内部 XML。STEP 可被 FreeCAD 等加载；XML 供其他 OCCT 应用使用。

```python
door.export("door.step")
door.export("door.xml")
```

---

# 对象位置

可用初始 `Location` 添加对象，例如：

```python
import cadquery as cq

cone = cq.Solid.makeCone(1, 0, 2)

assy = cq.Assembly()
assy.add(
    cone,
    loc=cq.Location((0, 0, 0), (1, 0, 0), 180),
    name="cone0",
    color=cq.Color("green"),
)
assy.add(cone, name="cone1", color=cq.Color("blue"))

show_object(assy)
```

也可用约束与 `solve()` 定位。若同时使用初始位置与 `solve()`，求解器会用解覆盖初始位置，但初始位置仍可影响最终解：欠约束时求解器可能不移动对代价函数无贡献的对象；多解时初始位置可决定收敛到哪一解；复杂装配中近似正确的初始位置可减少计算时间。

---

# 约束

约束常比直接给位置更能表达真实关系。上例中两锥底面应相贴，用 `Plane` 约束建模；若只给显式位置，`cone1` 移动时用户还须更新位置。

至少一个约束且运行 `solve()` 时，会建立优化问题：每个约束提供代价函数，依赖两对象的 `Location`；求解器变动装配子件位置以最小化代价之和。阅读下方各约束的代价形式即可理解其行为。

## Point（点）

常用约束，最小化两点距离。用途：面居中、顶点对齐；也可用虚拟顶点做偏移。

创建 `Point` 约束时，`param` 可指定期望间距（无方向性）；要定向偏移请用虚拟 `Vertex`。

`Point` 用 `Center()` 取中心，适用于 `Shape` 子类。

```python
import cadquery as cq

# Use the Point constraint to position boxes relative to an arc
line = cq.Edge.makeCircle(radius=10, angle1=0, angle2=90)
box = cq.Workplane().box(1, 1, 1)

assy = cq.Assembly()
assy.add(line, name="line")

# position the red box on the center of the arc
assy.add(box, name="box0", color=cq.Color("red"))
assy.constrain("line", "box0", "Point")

# position the green box at a normalized distance of 0.8 along the arc
position0 = line.positionAt(0.8)
assy.add(box, name="box1", color=cq.Color("green"))
assy.constrain(
    "line",
    cq.Vertex.makeVertex(*position0.toTuple()),
    "box1",
    box.val(),
    "Point",
)

# position the orange box 2 units in any direction from the green box
assy.add(box, name="box2", color=cq.Color("orange"))
assy.constrain(
    "line",
    cq.Vertex.makeVertex(*position0.toTuple()),
    "box2",
    box.val(),
    "Point",
    param=2,
)

# position the blue box offset 2 units in the x direction from the green box
position1 = position0 + cq.Vector(2, 0, 0)
assy.add(box, name="box3", color=cq.Color("blue"))
assy.constrain(
    "line",
    cq.Vertex.makeVertex(*position1.toTuple()),
    "box3",
    box.val(),
    "Point",
)

assy.solve()
show_object(assy)
```

## Axis（轴）

最小化两向量夹角。用于面对齐、控制旋转。`param` 默认 180°（法向反平行，常见「贴合」mate）。`param=0` 时同向，用于销钉入孔等：

```python
import cadquery as cq

cone = cq.Solid.makeCone(1, 0, 2)

assy = cq.Assembly()
assy.add(cone, name="cone0", color=cq.Color("green"))
assy.add(cone, name="cone1", color=cq.Color("blue"))
assy.constrain("cone0@faces@<Z", "cone1@faces@<Z", "Axis")

assy.solve()
show_object(assy)
```

```python
import cadquery as cq

plate = cq.Workplane().box(10, 10, 1).faces(">Z").workplane().hole(2)
cone = cq.Solid.makeCone(0.8, 0, 4)

assy = cq.Assembly()
assy.add(plate, name="plate", color=cq.Color("green"))
assy.add(cone, name="cone", color=cq.Color("blue"))
assy.constrain("plate@faces@>Z", "cone@faces@<Z", "Point")
assy.constrain("plate@faces@>Z", "cone@faces@<Z", "Axis", param=0)

assy.solve()
show_object(assy)
```

提取方向向量的方式依对象类型：

- **Face**：`normalAt()`
- **geomType 为 CIRCLE 的 Edge**：`normal()`
- **其他 Edge**：`tangentAt()`

其他类型会 `ValueError`；最常见是对 `Face` 建 `Axis` 约束。

## Plane（平面）

`Point` 与 `Axis` 的组合，常用快捷方式。`param` 作用于 `Axis` 部分；贴合面保持默认，贯通孔/面用 `param=0`（见 Axis 节）。

## PointInPlane

将第一个对象中心约束在第二个对象定义的平面内（沿法向 `param` 偏移）。用于 L 形支架上盒体定位等：

```python
import cadquery as cq

# Create an L-shaped object:
bracket = (
    cq.Workplane("YZ")
    .hLine(1)
    .vLine(0.1)
    .hLineTo(0.2)
    .vLineTo(1)
    .hLineTo(0)
    .close()
    .extrude(1)
    .faces(">Y[1]")
    .tag("inner_vert")
    .end()
    .faces(">Z[1]")
    .tag("inner_horiz")
    .end()
)

box = cq.Workplane().box(0.5, 0.5, 0.5)

assy = cq.Assembly()
assy.add(bracket, name="bracket", color=cq.Color("gray"))
assy.add(box, name="box", color=cq.Color("green"))

assy.constrain("bracket@faces@>Z", "box@faces@>Z", "Axis", param=0)
assy.constrain("bracket@faces@>X", "box@faces@>X", "Axis", param=0)
assy.constrain("box@faces@<Z", "bracket?inner_horiz", "PointInPlane")
assy.constrain("box@faces@<Y", "bracket?inner_vert", "PointInPlane", param=0.2)
assy.constrain("box@faces@>X", "bracket@faces@>X", "PointInPlane", param=-0.1)

assy.solve()
show_object(assy)
```

## PointOnLine

将第一个对象中心约束在第二个对象定义的直线上。

## FixedPoint

锁定对象平移自由度，将中心固定到 `param` 给定位置。

## FixedRotation

锁定旋转自由度，相对 `param` 给定旋转角。

## FixedAxis

将对象法向/切向固定到 `param` 给定方向向量，锁定两个旋转自由度。

---

# 装配颜色

除 RGBA 外，`Color` 可从文本名实例化。有效颜色名包括（与英文原文相同）：

aliceblue, antiquewhite, antiquewhite1, antiquewhite2, antiquewhite3, antiquewhite4, aquamarine1, aquamarine2, aquamarine4, azure, azure2, azure3, azure4, beet, beige, bisque, bisque2, bisque3, bisque4, black, blanchedalmond, blue, blue1, blue2, blue3, blue4, blueviolet, brown, brown1, brown2, brown3, brown4, burlywood, burlywood1, burlywood2, burlywood3, burlywood4, cadetblue, cadetblue1, cadetblue2, cadetblue3, cadetblue4, chartreuse, chartreuse1, chartreuse2, chartreuse3, chartreuse4, chocolate, chocolate1, chocolate2, chocolate3, chocolate4, coral, coral1, coral2, coral3, coral4, cornflowerblue, cornsilk1, cornsilk2, cornsilk3, cornsilk4, cyan, cyan1, cyan2, cyan3, cyan4, darkgoldenrod, darkgoldenrod1, darkgoldenrod2, darkgoldenrod3, darkgoldenrod4, darkgreen, darkkhaki, darkolivegreen, darkolivegreen1, darkolivegreen2, darkolivegreen3, darkolivegreen4, darkorange, darkorange1, darkorange2, darkorange3, darkorange4, darkorchid, darkorchid1, darkorchid2, darkorchid3, darkorchid4, darksalmon, darkseagreen, darkseagreen1, darkseagreen2, darkseagreen3, darkseagreen4, darkslateblue, darkslategray, darkslategray1, darkslategray2, darkslategray3, darkslategray4, darkturquoise, darkviolet, deeppink, deeppink2, deeppink3, deeppink4, deepskyblue1, deepskyblue2, deepskyblue3, deepskyblue4, dodgerblue1, dodgerblue2, dodgerblue3, dodgerblue4, firebrick, firebrick1, firebrick2, firebrick3, firebrick4, floralwhite, forestgreen, gainsboro, ghostwhite, gold, gold1, gold2, gold3, gold4, goldenrod, goldenrod1, goldenrod2, goldenrod3, goldenrod4, gray, gray0, gray1, gray2, gray3, gray4, gray5, gray6, gray7, gray8, gray9, gray10, gray11, gray12, gray13, gray14, gray15, gray16, gray17, gray18, gray19, gray20, gray21, gray22, gray23, gray24, gray25, gray26, gray27, gray28, gray29, gray30, gray31, gray32, gray33, gray34, gray35, gray36, gray37, gray38, gray39, gray40, gray41, gray42, gray43, gray44, gray45, gray46, gray47, gray48, gray49, gray50, gray51, gray52, gray53, gray54, gray55, gray56, gray57, gray58, gray59, gray60, gray61, gray62, gray63, gray64, gray65, gray66, gray67, gray68, gray69, gray70, gray71, gray72, gray73, gray74, gray75, gray76, gray77, gray78, gray79, gray80, gray81, gray82, gray83, gray85, gray86, gray87, gray88, gray89, gray90, gray91, gray92, gray93, gray94, gray95, gray97, gray98, gray99, green, green1, green2, green3, green4, greenyellow, honeydew, honeydew2, honeydew3, honeydew4, hotpink, hotpink1, hotpink2, hotpink3, hotpink4, indianred, indianred1, indianred2, indianred3, indianred4, ivory, ivory2, ivory3, ivory4, khaki, khaki1, khaki2, khaki3, khaki4, lavender, lavenderblush1, lavenderblush2, lavenderblush3, lavenderblush4, lawngreen, lemonchiffon1, lemonchiffon2, lemonchiffon3, lemonchiffon4, lightblue, lightblue1, lightblue2, lightblue3, lightblue4, lightcoral, lightcyan, lightcyan1, lightcyan2, lightcyan3, lightcyan4, lightgoldenrod, lightgoldenrod1, lightgoldenrod2, lightgoldenrod3, lightgoldenrod4, lightgoldenrodyellow, lightgray, lightpink, lightpink1, lightpink2, lightpink3, lightpink4, lightsalmon1, lightsalmon2, lightsalmon3, lightsalmon4, lightseagreen, lightskyblue, lightskyblue1, lightskyblue2, lightskyblue3, lightskyblue4, lightslateblue, lightslategray, lightsteelblue, lightsteelblue1, lightsteelblue2, lightsteelblue3, lightsteelblue4, lightyellow, lightyellow2, lightyellow3, lightyellow4, limegreen, linen, magenta, magenta1, magenta2, magenta3, magenta4, maroon, maroon1, maroon2, maroon3, maroon4, matrablue, matragray, mediumaquamarine, mediumorchid, mediumorchid1, mediumorchid2, mediumorchid3, mediumorchid4, mediumpurple, mediumpurple1, mediumpurple2, mediumpurple3, mediumpurple4, mediumseagreen, mediumslateblue, mediumspringgreen, mediumturquoise, mediumvioletred, midnightblue, mintcream, mistyrose, mistyrose2, mistyrose3, mistyrose4, moccasin, navajowhite1, navajowhite2, navajowhite3, navajowhite4, navyblue, oldlace, olivedrab, olivedrab1, olivedrab2, olivedrab3, olivedrab4, orange, orange1, orange2, orange3, orange4, orangered, orangered1, orangered2, orangered3, orangered4, orchid, orchid1, orchid2, orchid3, orchid4, palegoldenrod, palegreen, palegreen1, palegreen2, palegreen3, palegreen4, paleturquoise, paleturquoise1, paleturquoise2, paleturquoise3, paleturquoise4, palevioletred, palevioletred1, palevioletred2, palevioletred3, palevioletred4, papayawhip, peachpuff, peachpuff2, peachpuff3, peachpuff4, peru, pink, pink1, pink2, pink3, pink4, plum, plum1, plum2, plum3, plum4, powderblue, purple, purple1, purple2, purple3, purple4, red, red1, red2, red3, red4, rosybrown, rosybrown1, rosybrown2, rosybrown3, rosybrown4, royalblue, royalblue1, royalblue2, royalblue3, royalblue4, saddlebrown, salmon, salmon1, salmon2, salmon3, salmon4, sandybrown, seagreen, seagreen1, seagreen2, seagreen3, seagreen4, seashell, seashell2, seashell3, seashell4, sienna, sienna1, sienna2, sienna3, sienna4, skyblue, skyblue1, skyblue2, skyblue3, skyblue4, slateblue, slateblue1, slateblue2, slateblue3, slateblue4, slategray, slategray1, slategray2, slategray3, slategray4, snow, snow2, snow3, snow4, springgreen, springgreen2, springgreen3, springgreen4, steelblue, steelblue1, steelblue2, steelblue3, steelblue4, tan, tan1, tan2, tan3, tan4, teal, thistle, thistle1, thistle2, thistle3, thistle4, tomato, tomato1, tomato2, tomato3, tomato4, turquoise, turquoise1, turquoise2, turquoise3, turquoise4, violet, violetred, violetred1, violetred2, violetred3, violetred4, wheat, wheat1, wheat2, wheat3, wheat4, white, whitesmoke, yellow, yellow1, yellow2, yellow3, yellow4, yellowgreen
