# 关节物体（ArticulatedObject）

## 用途

`ArticulatedObject` 是已创作装配的根。用它创建零件、关节、材质及模型级元数据。

## 导入

```python
from sdk import ArticulatedObject
```

## 推荐 API

- `ArticulatedObject(...)`
- `model.part(...)`
- `model.articulation(...)`
- `model.material(...)`
- `model.get_part(...)`
- `model.get_articulation(...)`
- `model.root_parts()`
- `model.validate(strict=True)`

## 构造

```python
ArticulatedObject(
    name: str,
    parts: list[Part] = [],
    articulations: list[Articulation] = [],
    materials: list[Material] = [],
    meta: dict[str, object] = {},
    assets=None,
)
```

重要字段：

- `name`：模型名。
- `parts`：已创作零件。
- `articulations`：已创作关节。
- `materials`：已注册材质。
- `meta`：可选模型级元数据。
- `assets`：网格创作的可选资源所有者或根。
- 网格资源由运行时管理；经 `mesh_from_geometry(...)`、`mesh_from_input(...)`、`mesh_from_cadquery(...)` 等创作网格视觉。

## 创作辅助

### `model.part(...)`

```python
model.part(
    name: str,
    *,
    visuals: Iterable[Visual] | None = None,
    inertial: Inertial | None = None,
    meta: dict[str, object] | None = None,
) -> Part
```

- 创建 `Part`，追加到 `model.parts` 并返回。
- 返回的零件是调用 `part.visual(...)` 的常规位置。

### `model.articulation(...)`

```python
model.articulation(
    name: str,
    articulation_type: ArticulationType | str,
    parent: str | Part,
    child: str | Part,
    *,
    origin: Origin | None = None,
    axis: tuple[float, float, float] | None = None,
    motion_limits: MotionLimits | None = None,
    motion_properties: MotionProperties | None = None,
    mimic: Mimic | None = None,
    meta: dict[str, object] | None = None,
) -> Articulation
```

- `parent`、`child`：零件对象或零件名。
- `origin`：父零件系到关节系的变换；默认 `Origin()`。
- `axis`：关节系中的运动轴；默认 `(0.0, 0.0, 1.0)`。
- `motion_limits`：所需关节限位。
- `motion_properties`：可选阻尼与摩擦。
- `mimic`：与另一标量关节的派生运动关系。

`mimic` 用于简单线性耦合：对向夹爪指、配对门、皮带联动滑块等，`q_follower = multiplier * q_source + offset`。勿用于非线性耦合或真实闭链机构。

## 坐标系与方向约定

关节使用 URDF 风格关节系：

1. `origin` 将关节系相对父零件系放置。
2. `axis` 写在关节系中，非世界系。
3. 在 `q=0` 时，子零件系与关节系重合。
4. 正 `REVOLUTE`/`CONTINUOUS` 运动绕 `axis` 遵循右手定则。
5. 正 `PRISMATIC` 沿 `+axis` 平移子件。

实践中常见错误是铰链线正确但**轴符号**错误。若增大关节值使子件压入父件，应**取反 `axis`**，而非交换 `lower`/`upper`。

### 示例：应向上打开的盖板

```python
# 闭合盖板几何沿局部 +X 从铰链线伸出。
# 使用 -Y 使正 q 将自由边抬向 +Z。
model.articulation(
    "body_to_lid",
    ArticulationType.REVOLUTE,
    parent=body,
    child=lid,
    origin=Origin(xyz=(-0.09, 0.0, 0.05)),
    axis=(0.0, -1.0, 0.0),
    motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=1.2),
)
```

### 示例：镜像盖板仍保持「正为打开」

```python
# 若闭合面板沿局部 -X 从铰链伸出，
# 翻转轴符号使正 q 仍向上/向外打开。
model.articulation(
    "body_to_mirrored_lid",
    ArticulationType.REVOLUTE,
    parent=body,
    child=mirrored_lid,
    origin=Origin(xyz=(0.09, 0.0, 0.05)),
    axis=(0.0, 1.0, 0.0),
    motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=1.2),
)
```

### 示例：应向外伸出的抽屉

```python
# 正移动关节 q 沿 +X 将抽屉拉出。
model.articulation(
    "cabinet_to_drawer",
    ArticulationType.PRISMATIC,
    parent=cabinet,
    child=drawer,
    origin=Origin(xyz=(0.0, 0.0, 0.12)),
    axis=(1.0, 0.0, 0.0),
    motion_limits=MotionLimits(effort=40.0, velocity=0.25, lower=0.0, upper=0.28),
)
```

### 保留插入：移动与嵌套级

套筒、伸缩杆、嵌套导轨等，按**完全伸出姿态**定尺寸，而非仅塌陷轮廓。若一件在另一件内滑动，滑动件须有足够隐藏长度，在上限位仍保持啮合。

启发式：

`滑动件长度 >= 最大伸出时可见长度 + 最小保留插入量`

实践中：

- 将移动关节 `origin` 放在套筒入口、座口等名义就位面，而非任意零件中心
- `motion_limits.upper` 为保留插入后的可用行程，非整件长度
- 若机构需要，让子几何在隐藏方向越过关节系延伸

```python
# 内桅在可见座下方延伸，以便最大行程仍保持啮合。
outer_sleeve = model.part("outer_sleeve")
inner_mast = model.part("inner_mast")

outer_sleeve.visual(
    Cylinder(radius=0.022, length=0.240),
    origin=Origin(xyz=(0.0, 0.0, 0.120)),
)
inner_mast.visual(
    Cylinder(radius=0.016, length=0.620),
    origin=Origin(xyz=(0.0, 0.0, 0.110)),
)

model.articulation(
    "sleeve_to_mast",
    ArticulationType.PRISMATIC,
    parent=outer_sleeve,
    child=inner_mast,
    # 关节放在套筒入口/就位面。
    origin=Origin(xyz=(0.0, 0.0, 0.240)),
    axis=(0.0, 0.0, 1.0),
    # 上限行程在内桅完全退出套筒前停止。
    motion_limits=MotionLimits(lower=0.0, upper=0.260, effort=80.0, velocity=0.20),
)
```

### `model.material(...)`

```python
model.material(
    name: str,
    *,
    rgba: Sequence[float] | None = None,
    color: Sequence[float] | None = None,
    texture: str | None = None,
) -> Material
```

- 在 `model.materials` 上注册材质。
- `rgba` 与 `color` 二选一。
- 3 元组颜色扩展为 `(r, g, b, 1.0)`。

## 查找辅助

### `model.get_part(name) -> Part`

```python
model.get_part(name: str | Part) -> Part
```

返回命名零件；不存在则 `ValidationError`。

### `model.get_articulation(name) -> Articulation`

```python
model.get_articulation(name: str | Articulation) -> Articulation
```

返回命名关节；不存在则 `ValidationError`。

### `model.root_parts() -> list[Part]`

返回不作为任何关节子件的零件。

## 验证

### `model.validate(...)`

```python
model.validate(
    *,
    strict: bool = True,
    strict_mesh_paths: bool = False,
) -> None
```

验证包括：

- 至少一个零件
- 零件名唯一
- 关节名唯一
- 材质名唯一
- 关节引用存在的父/子零件
- 每零件至多一个父关节
- 几何与材质有效
- 严格模式下，关节图从至少一根连通

## 关节规则

调用 `model.articulation(...)` 时：

- `REVOLUTE`、`PRISMATIC` 需要 `MotionLimits(effort=..., velocity=..., lower=..., upper=...)`。
- `CONTINUOUS` 需要 `MotionLimits(effort=..., velocity=...)`，不得设 `lower`/`upper`。
- `FIXED`、`FLOATING` 不得使用 `motion_limits`。
- `mimic=Mimic(...)` 仅用于标量关节；源关节须兼容运动域；mimic 环无效。
- 严格模式下，运动轴须为非零三维向量。

## 示例

```python
model = ArticulatedObject(name="desk_lamp")

base = model.part("base")
arm = model.part("arm")

model.articulation(
    "base_to_arm",
    ArticulationType.REVOLUTE,
    parent=base,
    child=arm,
    origin=Origin(xyz=(0.0, 0.0, 0.08)),
    # 臂几何从肩部沿局部 +X 伸出，故 -Y 使正 q 向上俯仰。
    axis=(0.0, -1.0, 0.0),
    motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=-0.8, upper=0.8),
)
```

## 另见

- `20_core_types_c.md`：`Part`、`Articulation`、`MotionLimits` 与材质
- `80_testing_c.md`：几何与关节 QC

## 面向 agent 的澄清

- `origin` 定义父系中的关节系；子零件相对该关节系运动。
- `axis` 在应用 `origin.rpy` 后的关节系中表达，非世界系；应写为单位向量。
- `FLOATING` 为高级，不用 `axis` 或标量限位；测试/探针用 `Origin(xyz=..., rpy=...)` 驱动，非标量。
- 若增大标量关节值使子件反向运动，取反 `axis`；勿靠翻转限位交换开合语义。
