# CadQuery API 参考

## 概述

CadQuery API 由 4 个主要对象组成：

- **Sketch** — 构造 2D 草图
- **Workplane** — 包装拓扑实体并提供 2D 建模上下文
- **Selector** — 筛选与选择
- **Assembly** — 将对象组合为装配

---

## 草图初始化

| 方法 | 说明 |
|--------|--------------|
| `Sketch(parent, locs, obj)` | 2D 草图。 |
| `Sketch.importDXF(filename[, tol, exclude, ...])` | 导入 DXF 并构造面。 |
| `Workplane.sketch()` | 初始化并返回草图。 |
| `Sketch.finalize()` | 结束草图构造并返回父对象。 |
| `Sketch.copy()` | 创建草图的部分副本。 |
| `Sketch.located(loc)` | 带新位置的部分副本。 |
| `Sketch.moved()` | 面已移动的部分副本。 |

---

## 草图选择

| 方法 | 说明 |
|--------|--------------|
| `Sketch.tag(tag)` | 标记当前选择。 |
| `Sketch.select(*tags)` | 按标签选择。 |
| `Sketch.reset()` | 重置当前选择。 |
| `Sketch.delete()` | 删除选中对象。 |
| `Sketch.faces([s, tag])` | 选择面。 |
| `Sketch.edges([s, tag])` | 选择边。 |
| `Sketch.vertices([s, tag])` | 选择顶点。 |

---

## 基于面的草图

| 方法 | 说明 |
|--------|--------------|
| `Sketch.face(b[, angle, mode, tag, ...])` | 由线框或边构造面。 |
| `Sketch.rect(w, h[, angle, mode, tag])` | 矩形面。 |
| `Sketch.circle(r[, mode, tag])` | 圆面。 |
| `Sketch.ellipse(a1, a2[, angle, mode, tag])` | 椭圆面。 |
| `Sketch.trapezoid(w, h, a1[, a2, angle, ...])` | 梯形面。 |
| `Sketch.slot(w, h[, angle, mode, tag])` | 槽形面。 |
| `Sketch.regularPolygon(r, n[, angle, mode, tag])` | 正多边形面。 |
| `Sketch.polygon(pts[, angle, mode, tag])` | 多边形面。 |
| `Sketch.rarray(xs, ys, nx, ny)` | 矩形位置阵列。 |
| `Sketch.parray(r, a1, da, n[, rotate])` | 极坐标位置阵列。 |
| `Sketch.distribute(n[, start, stop, rotate])` | 沿选中边/线框分布位置。 |
| `Sketch.each(callback[, mode, tag, ...])` | 对所有适用实体执行回调。 |
| `Sketch.push(locs[, tag])` | 将当前选择设为给定位置/点。 |
| `Sketch.hull([mode, tag])` | 由当前选择或全部对象生成凸包。 |
| `Sketch.offset(d[, mode, tag])` | 偏移选中线框或边。 |
| `Sketch.fillet(d)` | 按当前选择倒圆角。 |
| `Sketch.chamfer(d)` | 按当前选择倒斜角。 |
| `Sketch.clean()` | 移除内部线框。 |

---

## 基于边与约束的草图

| 方法 | 说明 |
|--------|--------------|
| `Sketch.edge(val[, tag, forConstruction])` | 向草图添加边。 |
| `Sketch.segment(...)` | 构造线段。 |
| `Sketch.arc(...)` | 构造圆弧。 |
| `Sketch.spline(...)` | 构造样条边。 |
| `Sketch.close([tag])` | 将末边连到首边。 |
| `Sketch.assemble([mode, tag])` | 将边装配为面。 |
| `Sketch.constrain(...)` | 添加约束。 |
| `Sketch.solve()` | 求解当前约束并更新边位置。 |

---

## 初始化

| 方法 | 说明 |
|--------|--------------|
| `Workplane(obj=None)` | 定义空间坐标系，可在其中使用 2D 坐标。 |

---

## 2D 操作

| 方法 | 说明 |
|--------|--------------|
| `Workplane.center(x, y)` | 将局部坐标平移到指定位置。 |
| `Workplane.lineTo(x, y[, forConstruction])` | 从当前点到给定点画线。 |
| `Workplane.line(xDist, yDist[, forConstruction])` | 相对当前点画线。 |
| `Workplane.vLine(distance[, forConstruction])` | 从当前点画竖直线。 |
| `Workplane.vLineTo(yCoord[, forConstruction])` | 画到给定 y 的竖直线。 |
| `Workplane.hLine(distance[, forConstruction])` | 画水平线。 |
| `Workplane.hLineTo(xCoord[, forConstruction])` | 画到给定 x 的水平线。 |
| `Workplane.polarLine(distance, angle, ...)` | 按给定长度与角度画线。 |
| `Workplane.polarLineTo(distance, angle, ...)` | 画到给定极坐标。 |
| `Workplane.moveTo(x, y)` | 移动到点而不画线。 |
| `Workplane.move(xDist, yDist)` | 按距离移动。 |
| `Workplane.spline(listOfXYTuple[, tangents, ...])` | 过点插值样条。 |
| `Workplane.parametricCurve(func[, N, start, ...])` | 逼近函数的样条曲线。 |
| `Workplane.parametricSurface(func[, N, ...])` | 逼近函数的样条曲面。 |
| `Workplane.threePointArc(point1, point2, ...)` | 过给定点的圆弧。 |
| `Workplane.sagittaArc(endPoint, sag, ...)` | 由矢高定义的弧。 |
| `Workplane.radiusArc(endPoint, radius, ...)` | 由半径定义的弧。 |
| `Workplane.tangentArcPoint(endpoint, ...)` | 与当前边相切的弧。 |
| `Workplane.mirrorY()` | 关于 y 轴镜像。 |
| `Workplane.mirrorX()` | 关于 x 轴镜像。 |
| `Workplane.wire([forConstruction])` | 将边连成线框。 |
| `Workplane.rect(xLen, yLen[, centered, ...])` | 为栈上每项画矩形。 |
| `Workplane.circle(radius[, forConstruction])` | 画圆。 |
| `Workplane.ellipse(x_radius, y_radius, ...)` | 画椭圆。 |
| `Workplane.ellipseArc(x_radius, y_radius, ...)` | 画椭圆弧。 |
| `Workplane.polyline(listOfXYTuple, ...)` | 折线。 |
| `Workplane.close()` | 结束构造并建闭合线框。 |
| `Workplane.rarray(xSpacing, ySpacing, xCount, ...)` | 点矩形阵列。 |
| `Workplane.polarArray(radius, startAngle, ...)` | 极坐标阵列。 |
| `Workplane.slot2D(length, diameter[, angle])` | 圆角槽。 |
| `Workplane.offset2D(d[, kind, forConstruction])` | 2D 偏移线框。 |
| `Workplane.placeSketch(*sketches)` | 放置给定草图。 |

---

## 3D 操作

| 方法 | 说明 |
|--------|--------------|
| `Workplane.cboreHole(diameter, cboreDiameter, ...)` | 沉孔。 |
| `Workplane.cskHole(diameter, cskDiameter, ...)` | 沉头孔。 |
| `Workplane.hole(diameter[, depth, clean])` | 孔。 |
| `Workplane.extrude(until[, combine, clean, ...])` | 拉伸棱柱体。 |
| `Workplane.cut(toCut[, clean, tol])` | 从当前实体切除。 |
| `Workplane.cutBlind(until[, clean, both, taper])` | 盲切。 |
| `Workplane.cutThruAll([clean, taper])` | 贯通切除。 |
| `Workplane.box(length, width, height, ...)` | 盒体。 |
| `Workplane.sphere(radius[, direct, angle1, ...])` | 球。 |
| `Workplane.wedge(dx, dy, dz, xmin, zmin, ...)` | 楔体。 |
| `Workplane.cylinder(height, radius[, direct, ...])` | 圆柱。 |
| `Workplane.union([toUnion, clean, glue, tol])` | 并集。 |
| `Workplane.combine([clean, glue, tol])` | 合并为一体。 |
| `Workplane.intersect(toIntersect[, clean, tol])` | 交集。 |
| `Workplane.loft([ruled, combine, clean])` | 放样实体。 |
| `Workplane.sweep(path[, multisection, ...])` | 扫掠实体。 |
| `Workplane.twistExtrude(distance, angleDegrees)` | 扭转拉伸。 |
| `Workplane.revolve([angleDegrees, axisStart, ...])` | 旋转体。 |
| `Workplane.text(txt, fontsize, distance, ...)` | 3D 文字。 |

### 3D 操作（无需工作平面）

| 方法 | 说明 |
|--------|--------------|
| `Workplane.shell(thickness[, kind])` | 抽壳。 |
| `Workplane.fillet(radius)` | 选中边倒圆。 |
| `Workplane.chamfer(length[, length2])` | 选中边倒角。 |
| `Workplane.split()` | 一分为二。 |
| `Workplane.rotate(axisStartPoint, ...)` | 旋转栈上项。 |
| `Workplane.rotateAboutCenter(axisEndPoint, ...)` | 绕中心轴旋转。 |
| `Workplane.translate(vec)` | 平移。 |
| `Workplane.mirror([mirrorPlane, ...])` | 镜像。 |

---

## 文件管理与导出

| 方法 | 说明 |
|--------|--------------|
| `importers.importStep(fileName)` | 导入 STEP 到 Workplane。 |
| `importers.importDXF(filename[, tol, ...])` | 导入 DXF。 |
| `exporters.export(w, fname[, exportType, ...])` | 导出 Workplane 或 Shape。 |
| `occ_impl.exporters.dxf.DxfDocument([...])` | 从对象创建 DXF 文档。 |

---

## 迭代方法

| 方法 | 说明 |
|--------|--------------|
| `Workplane.each(callback, ...)` | 对栈上每项执行函数。 |
| `Workplane.eachpoint(arg, ...)` | 类似 `each()`，按点应用。 |

---

## 栈与选择器方法

| 方法 | 说明 |
|--------|--------------|
| `Workplane.all()` | 返回栈上全部对象。 |
| `Workplane.size()` | 栈上对象数量。 |
| `Workplane.vals()` | 当前值列表。 |
| `Workplane.add()` | 添加到栈。 |
| `Workplane.val()` | 栈顶第一项。 |
| `Workplane.first()` | 第一项。 |
| `Workplane.item(i)` | 第 i 项。 |
| `Workplane.last()` | 最后一项。 |
| `Workplane.end([n])` | 第 n 层父元素。 |
| `Workplane.vertices([selector, tag])` | 选顶点。 |
| `Workplane.faces([selector, tag])` | 选面。 |
| `Workplane.edges([selector, tag])` | 选边。 |
| `Workplane.wires([selector, tag])` | 选线框。 |
| `Workplane.solids([selector, tag])` | 选实体。 |
| `Workplane.shells([selector, tag])` | 选壳。 |
| `Workplane.compounds([selector, tag])` | 选复合体。 |

---

## 选择器

| 方法 | 说明 |
|--------|--------------|
| `NearestToPointSelector(pnt)` | 选离点最近对象。 |
| `BoxSelector(point0, point1[, boundingbox])` | 盒内选择。 |
| `BaseDirSelector(vector[, tolerance])` | 按方向向量。 |
| `ParallelDirSelector(vector[, tolerance])` | 平行于方向。 |
| `DirectionSelector(vector[, tolerance])` | 对齐方向。 |
| `DirectionNthSelector(vector, n, ...)` | 第 n 个平行/法向对象。 |
| `LengthNthSelector(n[, directionMax, tolerance])` | 按第 n 长度。 |
| `AreaNthSelector(n[, directionMax, tolerance])` | 按第 n 面积。 |
| `RadiusNthSelector(n[, directionMax, tolerance])` | 按第 n 半径。 |
| `PerpendicularDirSelector(vector[, tolerance])` | 垂直于方向。 |
| `TypeSelector(typeString)` | 按几何类型。 |
| `DirectionMinMaxSelector(vector, ...)` | 沿方向最近/最远。 |
| `CenterNthSelector(vector, n[, directionMax, ...])` | 按投影中心距离排序。 |
| `BinarySelector(left, right)` | 二元选择器基类。 |
| `AndSelector(left, right)` | 交。 |
| `SumSelector(left, right)` | 并。 |
| `SubtractSelector(left, right)` | 差。 |
| `InverseSelector(selector)` | 反选。 |
| `StringSyntaxSelector(selectorString)` | 字符串语法筛选。 |

---

## 装配

| 方法 | 说明 |
|--------|--------------|
| `Assembly(obj, loc, name, color, metadata)` | Workplane 与 Shape 的嵌套装配。 |
| `Assembly.add()` | 添加子装配。 |
| `Assembly.save(path[, exportType, mode, ...])` | 保存装配。 |
| `Assembly.constrain()` | 定义约束。 |
| `Assembly.solve([verbosity])` | 求解约束。 |
| `Constraint` | `ConstraintSpec` 别名。 |
| `Color()` | `Quantity_ColorRGBA` 包装。 |
