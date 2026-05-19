# 放置辅助（Placement Helpers）

## 用途

当一件物体需相对另一件对齐、安装或包裹时使用。

## 导入

```python
from sdk import (
    align_centers,
    place_on_surface,
    place_on_face,
    place_on_face_uv,
    proud_for_flush_mount,
    surface_frame,
    wrap_mesh_onto_surface,
    wrap_profile_onto_surface,
)
```

## 推荐 API

| 意图 | 辅助 |
| --- | --- |
| 沿选定轴对齐中心 | `align_centers(...)` |
| 刚性子件安装到目标表面 | `place_on_surface(...)` |
| 盒状面上安装 | `place_on_face(...)`、`place_on_face_uv(...)` |
| 计算齐平安装偏移 | `proud_for_flush_mount(...)` |
| 查询表面点与切向标架 | `surface_frame(...)` |
| 将已有网格包裹到曲面 | `wrap_mesh_onto_surface(...)` |
| 将带厚度 2D 轮廓包裹到曲面 | `wrap_profile_onto_surface(...)` |

## 主体约定

共享输入约定：

- `Part`：默认使用其视觉的并集
- `Visual`：仅该视觉
- `Box`、`Cylinder`、`Sphere`、`Mesh`：直接使用几何
- `MeshGeometry`：包裹辅助接受

`place_on_face(...)` 与 `proud_for_flush_mount(...)` 需要 `Part`。

## 对齐

### `align_centers(...)`

```python
align_centers(
    child_aabb,
    parent_aabb,
    *,
    axes=("x", "y", "z"),
) -> Origin
```

- `child_aabb`、`parent_aabb`：`(min_xyz, max_xyz)` AABB 对。
- `axes`：单轴、紧凑字符串如 `"xy"` 或轴名可迭代。
- 返回对齐所选中心坐标的 `Origin` 平移。

## 基于面的安装

### `place_on_face(...)`

```python
place_on_face(
    parent_link: Part,
    face: str,
    *,
    face_pos: tuple[float, float] = (0.0, 0.0),
    proud: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = True,
) -> Origin
```

- `parent_link`：盒状父零件。
- `face`：`"+x"`、`"-x"`、`"+y"`、`"-y"`、`"+z"`、`"-z"` 之一。
- `face_pos`：面上局部平面偏移，米。
- `proud`：沿面法向外的偏移。
- 返回刚性 `Origin`。

`face_pos` 在父面切向坐标中表达；返回子系为每面确定的右手基：

| 面 | `face_pos` 轴 | 子 `+X` | 子 `+Y` | 子 `+Z` |
| --- | --- | --- | --- | --- |
| `+x` | `(parent +Y, parent +Z)` | `parent -Z` | `parent +Y` | `parent +X` |
| `-x` | `(parent +Y, parent +Z)` | `parent +Z` | `parent +Y` | `parent -X` |
| `+y` | `(parent +X, parent +Z)` | `parent +X` | `parent -Z` | `parent +Y` |
| `-y` | `(parent +X, parent +Z)` | `parent +X` | `parent +Z` | `parent -Y` |
| `+z` | `(parent +X, parent +Y)` | `parent +X` | `parent +Y` | `parent +Z` |
| `-z` | `(parent +X, parent +Y)` | `parent +X` | `parent -Y` | `parent -Z` |

### `place_on_face_uv(...)`

```python
place_on_face_uv(
    parent_link: Part,
    face: str,
    *,
    uv: tuple[float, float] = (0.5, 0.5),
    uv_margin: float | tuple[float, float] = 0.0,
    proud: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = True,
) -> Origin
```

- `uv`：`[0, 1]` 归一化面坐标。
- `uv_margin`：内缩边距，单浮点或每轴一对。
- `uv` 与 `face_pos` 使用相同面切向轴。
- 返回刚性 `Origin`。

### `proud_for_flush_mount(...)`

```python
proud_for_flush_mount(
    child_link: Part,
    *,
    axis: str = "z",
    clearance: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = True,
) -> float
```

- 返回使居中子件齐平而非半嵌入的外偏移，与 `place_on_face(...)` 联用。
- `axis`：子局部厚度轴，`"x"`、`"y"` 或 `"z"`。
- `clearance`：额外正向外间隙，米。

## 表面查询

### `surface_frame(...)`

```python
surface_frame(
    target,
    *,
    point_hint=None,
    direction=None,
    asset_root=None,
    prefer_collisions: bool = False,
    up_hint=(0.0, 0.0, 1.0),
) -> SurfaceFrame
```

```python
SurfaceFrame(
    point: tuple[float, float, float],
    normal: tuple[float, float, float],
    tangent_u: tuple[float, float, float],
    tangent_v: tuple[float, float, float],
)
```

- `point_hint` 与 `direction` 恰提供一个。
- `point_hint`：目标感兴趣区域附近的世界点。
- `direction`：从目标粗中心向外的方向。
- `up_hint`：构造切向时偏好的世界上方向。
- 返回命中点、法向与切向基。

## 刚性表面安装

### `place_on_surface(...)`

```python
place_on_surface(
    child,
    target,
    *,
    point_hint=None,
    direction=None,
    child_axis: str = "+z",
    clearance: float = 0.0,
    spin: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = False,
    child_prefer_collisions: bool = False,
    up_hint=(0.0, 0.0, 1.0),
) -> Origin
```

- `child_axis`：应指向目标表面外的子局部轴，如 `"+z"`、`"-y"`。
- `clearance`：沿法向额外间隙，米。
- `spin`：绕法向额外旋转，弧度。
- 返回刚性 `Origin`。

## 共形表面包裹

### `wrap_mesh_onto_surface(...)`

```python
wrap_mesh_onto_surface(
    mesh,
    target,
    *,
    point_hint=None,
    direction=None,
    child_axis: str = "+z",
    visible_relief: float = 0.0,
    mapping: str = "auto",
    surface_max_edge: float | None = None,
    max_edge: float | None = None,
    spin: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = False,
    up_hint=(0.0, 0.0, 1.0),
) -> MeshGeometry
```

- `mesh`：`MeshGeometry` 或 `Mesh`。
- `target`：包裹目标。
- `visible_relief`：可见面相对目标外偏，米。
- `mapping`：
  - `"auto"`：优先内禀球/柱包裹，否则最近表面
  - `"intrinsic"`：要求内禀球/柱包裹
  - `"nearest"`：始终最近表面投影
- `surface_max_edge` / `max_edge`：可选包裹前细分目标；二选一。

返回烘焙的 `MeshGeometry`。

### `wrap_profile_onto_surface(...)`

```python
wrap_profile_onto_surface(
    profile,
    target,
    *,
    thickness: float,
    hole_profiles=(),
    point_hint=None,
    direction=None,
    visible_relief: float = 0.0,
    mapping: str = "auto",
    surface_max_edge: float | None = None,
    max_edge: float | None = None,
    spin: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = False,
    up_hint=(0.0, 0.0, 1.0),
) -> MeshGeometry
```

- `profile`：局部 XY 外环。
- `thickness`：正厚度，米。
- `hole_profiles`：可选 2D 通孔环。
- 可见面为局部 `z=0`；厚度沿局部 `-z` 向内。

返回烘焙的 `MeshGeometry`。

## 建议

### 理解包裹控制

- `child_axis` 指定哪条局部轴为可见外法向。
- 关心球/柱侧壁形状保持时用 `mapping="intrinsic"`。
- 包裹结果在曲面上明显弦切时降低 `surface_max_edge`。
- `visible_relief` 用于小间隙，非大刚性间距。

## 示例

### 面安装

```python
origin = place_on_face_uv(
    panel,
    "+z",
    uv=(0.75, 0.5),
    proud=proud_for_flush_mount(button, axis="z", clearance=0.0005),
    asset_root=HERE,
)
```

### 刚性表面安装

```python
origin = place_on_surface(
    child=button,
    target=panel,
    point_hint=(0.12, 0.0, 0.04),
    child_axis="+z",
    clearance=0.0005,
    spin=0.2,
    asset_root=HERE,
)
```

### 共形包裹

```python
wrapped = wrap_profile_onto_surface(
    profile,
    Sphere(radius=0.09),
    thickness=0.0015,
    direction=(1.0, 0.2, 0.1),
    mapping="intrinsic",
    visible_relief=0.00005,
    surface_max_edge=0.006,
)
```

## 另见

- `20_core_types_c.md`：几何描述符与 `Origin`
- `40_mesh_geometry_c.md`：`MeshGeometry`

## 面向 agent 的澄清

- `up_hint` 不仅破 tie：它将提示投影到切平面以定义零 `spin` 切向基；改 `up_hint` 会改 `spin=0` 含义。
- 角度输入为弧度，右手定则。
- 内禀包裹故意收窄：用于球与圆柱侧壁，非任意柱端盖或一般网格。
