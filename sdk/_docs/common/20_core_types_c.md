# 核心类型（Core Types）

## 用途

本文档说明基础 `sdk` 中使用的核心数据类型：变换、几何描述符、材质、惯性、零件与关节。

## 导入

```python
from sdk import (
    Origin,
    Box,
    Cylinder,
    Sphere,
    Mesh,
    Material,
    Visual,
    Inertia,
    Inertial,
    MotionLimits,
    MotionProperties,
    Mimic,
    Part,
    Articulation,
    ArticulationType,
    scale_geometry_to_size,
)
```

## 单位

- 距离：米。
- 旋转：`Origin.rpy = (roll, pitch, yaw)`，单位为弧度。
- `Origin.rpy` 使用与 URDF 兼容的合成：`R = Rz(yaw) * Ry(pitch) * Rx(roll)`。
- 旋转与连续关节位置为弧度；移动关节位置为沿配置关节轴的米。
- URDF 圆柱体与局部 `+Z` 对齐。

## 推荐 API 面

- `Origin`
- `Box`、`Cylinder`、`Sphere`、`Mesh`
- `Material`、`Visual`
- `Inertia`、`Inertial.from_geometry(...)`
- `MotionLimits`、`MotionProperties`、`Mimic`
- `Part.visual(...)`、`Part.get_visual(...)`
- `Articulation`、`ArticulationType`
- `scale_geometry_to_size(...)`

## 变换

### `Origin`

```python
Origin(
    xyz: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
)
```

- `xyz`：平移，米。
- `rpy`：旋转，弧度，合成为 `R = Rz(yaw) * Ry(pitch) * Rx(roll)`。
- 两字段均须恰好 3 个数。

## 几何描述符

几何描述符仅描述形状。在包含的 `Visual` 或 `Collision` 上通过 `origin=Origin(...)` 放置变换。

### `Box`

```python
Box(size: tuple[float, float, float])
```

- `size`：全长宽 `(sx, sy, sz)`，米。

### `Cylinder`

```python
Cylinder(radius: float, length: float)
```

- `radius`：圆柱半径，米。
- `length`：沿局部 `+Z` 的全长。
- `height`：可作为 `length` 的兼容别名，新代码优先 `length`。

### `Sphere`

```python
Sphere(radius: float)
```

- `radius`：球半径，米。

### `Mesh`

```python
Mesh(
    filename: str | os.PathLike[str],
    scale: tuple[float, float, float] | None = None,
    source_geometry: Box | Cylinder | Sphere | None = None,
    source_transform: tuple[tuple[float, float, float, float], ...] | None = None,
)
```

- `filename`：绝对或相对资源的网格路径。
- `scale`：可选各轴缩放。
- `source_geometry`：由基元生成网格时的可选基元溯源。
- `source_transform`：可选溯源变换；须同时提供 `source_geometry`。

`filename` 必填且非空。

## 材质与视觉

### `Material`

```python
Material(
    name: str,
    rgba: tuple[float, float, float, float] | None = None,
    texture: str | None = None,
    *,
    color: tuple[float, float, float] | tuple[float, float, float, float] | None = None,
)
```

- `name`：材质名，必填。
- `rgba`：3 或 4 个浮点；3 元组扩展为 `(r, g, b, 1.0)`。
- `color`：`rgba` 的兼容别名；`rgba` 与 `color` 二选一。
- `texture`：可选纹理路径。

### `Visual`

```python
Visual(
    geometry: Box | Cylinder | Sphere | Mesh,
    origin: Origin = Origin(),
    material: Material | str | None = None,
    name: str | None = None,
)
```

- `geometry`：可见几何描述符。
- `origin`：该视觉在零件上的局部变换。
- `material`：`Material` 对象或已注册材质名。
- 材质按**每个视觉**分配；除非拆成多个视觉，网格子区域不会单独获得 SDK 材质。
- 经 `Part.visual(...)` 添加时，`color` 可作为 `material` 的兼容别名；新代码优先 `material`。
- `name`：可选视觉名；测试或探针片段需定位局部特征时使用。

## 惯性

### `Inertia`

```python
Inertia(
    ixx: float,
    ixy: float,
    ixz: float,
    iyy: float,
    iyz: float,
    izz: float,
)
```

存储单零件的惯性张量分量。

### `Inertial`

```python
Inertial(
    mass: float,
    inertia: Inertia,
    origin: Origin = Origin(),
)
```

### `Inertial.from_geometry(...)`

```python
Inertial.from_geometry(
    geometry: Box | Cylinder | Sphere | Mesh,
    mass: float,
    *,
    origin: Origin | None = None,
) -> Inertial
```

- `mass`：正质量，必填。
- `origin`：可选惯性原点。
- 支持 `Box`、`Cylinder`、`Sphere`。
- 网格几何会抛出 `ValidationError`。

## 运动

### `MotionLimits`

```python
MotionLimits(
    effort: float = 1.0,
    velocity: float = 1.0,
    lower: float | None = None,
    upper: float | None = None,
)
```

- `effort`：正力矩/力限制。
- `velocity`：正速度限制。
- `lower`、`upper`：可选关节位置界。

### `MotionProperties`

```python
MotionProperties(
    damping: float | None = None,
    friction: float | None = None,
)
```

两字段均可选。

### `Mimic`

```python
Mimic(
    joint: str,
    multiplier: float = 1.0,
    offset: float = 0.0,
)
```

- `joint`：源关节名。
- `multiplier`：对源姿态的线性缩放。
- `offset`：缩放后的加性偏移。

### `ArticulationType`

```python
ArticulationType.REVOLUTE
ArticulationType.CONTINUOUS
ArticulationType.PRISMATIC
ArticulationType.FIXED
ArticulationType.FLOATING
```

创建关节时使用这些枚举值。

## 零件与关节

### `Part`

```python
Part(
    name: str,
    visuals: list[Visual] = [],
    collisions: list[Collision] = [],
    inertial: Inertial | None = None,
    meta: dict[str, object] = {},
)
```

推荐零件创作入口：

```python
part.visual(
    geometry,
    *,
    origin: Origin | None = None,
    material: Material | str | None = None,
    name: str | None = None,
) -> Visual

part.get_visual(name: str) -> Visual
```

- 用 `part.visual(...)` 追加一个具名或未命名视觉。
- 测试或探针需特定局部特征时用 `part.get_visual(...)`。

### `Articulation`

```python
Articulation(
    name: str,
    articulation_type: ArticulationType | str,
    parent: str,
    child: str,
    origin: Origin = Origin(),
    axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    motion_limits: MotionLimits | None = None,
    motion_properties: MotionProperties | None = None,
    mimic: Mimic | None = None,
    meta: dict[str, object] = {},
)
```

- `parent`、`child`：零件名。
- `origin`：从父零件坐标系到关节坐标系的变换。
- `axis`：旋转、连续与移动关节的运动轴，在关节坐标系中表达。
- `origin.rpy` 相对父系旋转关节系，因而也旋转 `axis` 的语义。
- `mimic`：与另一标量关节的派生运动关系。
- 方向约定与关节限位规则见 `30_articulated_object_c.md`。

已创作模型优先 `model.articulation(...)`，勿手动构造 `Articulation`。

## 解析对象上支持的公开字段

`model.get_part(...)`、`model.get_articulation(...)`、`part.get_visual(...)` 返回公开 SDK 对象。在测试、探针及其他已创作代码中，可读取下列字段与别名。

### `Part`

- `part.name`
- `part.visuals`
- `part.collisions`
- `part.inertial`
- `part.meta`
- `part.assets`

### `Visual`

- `visual.name`
- `visual.geometry`
- `visual.origin`
- `visual.material`

### `Articulation`

- `joint.name`
- `joint.articulation_type`
- `joint.joint_type`
- `joint.parent`
- `joint.child`
- `joint.origin`
- `joint.axis`
- `joint.motion_limits`
- `joint.limit`
- `joint.motion_properties`
- `joint.dynamics`
- `joint.mimic`
- `joint.meta`

### `MotionLimits`

- `limits.effort`
- `limits.velocity`
- `limits.lower`
- `limits.upper`

示例：

```python
hinge = object_model.get_articulation("lid_hinge")
limits = hinge.motion_limits
if limits is not None and limits.lower is not None and limits.upper is not None:
    lower = limits.lower
    upper = limits.upper
```

## 缩放辅助

### `scale_geometry_to_size(...)`

```python
scale_geometry_to_size(
    geometry,
    target_size,
    *,
    mode="stretch",
    asset_root=None,
    filename=None,
)
```

- `geometry`：基元几何或 `Mesh`。
- `target_size`：目标尺寸 `(x, y, z)`；每轴可为正浮点或 `None`。
- `mode`：`"stretch"` 或 `"uniform"`。
- `asset_root`：缩放网格时使用的网格根。
- `filename`：缩放后基元无法仍表示为基元、须输出为网格时必填。

### 建议

- 精确目标尺寸比保持比例更重要时用 `mode="stretch"`。
- 形状应保持比例时用 `mode="uniform"`。
- 基元缩放仅当结果仍可表示为该基元时保持基元；例如非均匀拉伸球体须 `filename=...` 以输出网格。

## 示例

```python
badge = Material(name="badge", rgba=(0.8, 0.2, 0.1, 1.0))

panel = Part(name="panel")
panel.visual(
    Box((0.10, 0.16, 0.003)),
    origin=Origin(xyz=(0.0, 0.0, 0.0015)),
    material=badge,
    name="panel_shell",
)
```

```python
scaled = scale_geometry_to_size(
    Sphere(radius=0.02),
    (0.04, 0.06, 0.01),
    filename="assets/meshes/badge.obj",
)
```

## 另见

- `30_articulated_object_c.md`：模型创作辅助
- `50_placement_c.md`：安装与表面包裹辅助
- `80_testing_c.md`：测试中零件与命名视觉的用法

## 面向 agent 的澄清

- `Origin` 始终是局部刚体变换：`xyz` 为米制平移，`rpy` 为弧度 roll/pitch/yaw，右手系，URDF 兼容合成 `R = Rz(yaw) * Ry(pitch) * Rx(roll)`。
- 零件视觉或碰撞在零件局部系中用 `origin=Origin(...)` 放置；关节 `origin` 定义相对父零件系的子关节系。
- `Mesh(...)` 需要 `filename` 或 `name`：`filename` 为具体网格路径，`name` 为稍后解析的托管/物化网格。
- agent 创作路径不使用 `Part.collisions`；只创作视觉，派生碰撞由验证/物化处理。
- `ArticulationType.FLOATING` 支持但属高级；其创作/测试姿态值为 `Origin(...)`，`xyz` 为关节系相对平移，`rpy` 为同系相对旋转。
- `REVOLUTE`、`CONTINUOUS`、`PRISMATIC` 的 `axis` 为关节系单位向量；正旋转运动遵循右手定则绕 `+axis`；正移动沿 `+axis` 平移。
- `Mimic(...)` 用于标量关节；从源关节派生 `q_follower = multiplier * q_source + offset`；测试与探针中勿直接对 mimic 从动件设姿态。
