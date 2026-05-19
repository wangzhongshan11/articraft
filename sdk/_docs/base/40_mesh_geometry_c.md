# 程序化网格（Procedural Meshes）

## 用途

用于低层程序化网格创作：基元实体、旋转体、拉伸、扫掠、轮廓、壳辅助与网格导出。
若形状属于旋钮、面框、车轮、风扇、面板等语义族，优先阅读下方列出的几何专题参考。

## 导入

```python
from sdk import (
    MeshGeometry,
    BoxGeometry,
    CapsuleGeometry,
    CylinderGeometry,
    ConeGeometry,
    DomeGeometry,
    SphereGeometry,
    TorusGeometry,
    LatheGeometry,
    LoftGeometry,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    SweepGeometry,
    rounded_rect_profile,
    superellipse_profile,
    sample_catmull_rom_spline_2d,
    sample_cubic_bezier_spline_2d,
    superellipse_side_loft,
    split_superellipse_side_loft,
    resample_side_sections,
    cut_opening_on_face,
    mesh_from_geometry,
)
```

## 推荐 API

- `MeshGeometry`
- 基元：`BoxGeometry`、`CylinderGeometry`、`ConeGeometry`、`SphereGeometry`、`DomeGeometry`、`CapsuleGeometry`、`TorusGeometry`
- 放样/拉伸/扫掠：`LatheGeometry`、`LoftGeometry`、`ExtrudeGeometry`、`ExtrudeWithHolesGeometry`、`SweepGeometry`
- 轮廓：`rounded_rect_profile`、`superellipse_profile`
- 样条/轮廓：`sample_catmull_rom_spline_2d(...)`、`sample_cubic_bezier_spline_2d(...)`
- 壳：`superellipse_side_loft(...)`、`split_superellipse_side_loft(...)`、`resample_side_sections(...)`
- 面板开口：`cut_opening_on_face(...)`
- 导出：`mesh_from_geometry(...)`

语义几何专题：

- `41_panels_and_grilles_c.md`：穿孔板、开槽板、通风格栅
- `42_brackets_and_mounts_c.md`：叉耳、叉架、轭
- `43_fans_and_rotors_c.md`：轴流转子与蜗壳叶轮
- `44_knobs_and_controls_c.md`：旋钮与控件帽
- `47_bezels_and_frames_c.md`：面框、装饰条、框开口
- `48_wheels_and_tires_c.md`：车轮与轮胎视觉
- `49_hinges_c.md`：外露实用铰链几何

## 核心网格类型

### `MeshGeometry`

```python
MeshGeometry(
    vertices: list[tuple[float, float, float]] = [],
    faces: list[tuple[int, int, int]] = [],
)
```

方法：

```python
geom.add_vertex(x, y, z) -> int
geom.add_face(a, b, c) -> None
geom.copy() -> MeshGeometry
geom.clone() -> MeshGeometry
geom.merge(other) -> MeshGeometry
geom.translate(dx, dy, dz) -> MeshGeometry
geom.scale(sx, sy=None, sz=None) -> MeshGeometry
geom.rotate(axis, angle, origin=(0.0, 0.0, 0.0)) -> MeshGeometry
geom.rotate_x(angle) -> MeshGeometry
geom.rotate_y(angle) -> MeshGeometry
geom.rotate_z(angle) -> MeshGeometry
geom.to_obj() -> str
geom.save_obj(path) -> None
```

- 顶点为米制 3D 点。
- 面为 0 基三角形索引。
- 所有变换原地进行并返回 `self`。

## 基元构造器

```python
BoxGeometry(size)
CylinderGeometry(radius, height, *, radial_segments=24, closed=True)
ConeGeometry(radius, height, *, radial_segments=24, closed=True)
SphereGeometry(radius, *, width_segments=24, height_segments=16)
DomeGeometry(radius, *, radial_segments=24, height_segments=12, closed=True)
CapsuleGeometry(radius, length, *, radial_segments=24, height_segments=8)
TorusGeometry(radius, tube, *, radial_segments=16, tubular_segments=32)
```

说明：

- `BoxGeometry` 中心在原点。
- `CylinderGeometry`、`ConeGeometry` 居中并沿局部 `Z`。
- `CapsuleGeometry.length` 为帽间圆柱中段长度。
- `DomeGeometry` 建上半球，底在 `z=0`。

## 放样 / 拉伸 / 扫掠

### `LatheGeometry`

```python
LatheGeometry(profile, *, segments=32, closed=True)
LatheGeometry.from_shell_profiles(
    outer_profile,
    inner_profile,
    *,
    segments=32,
    start_cap="flat",
    end_cap="flat",
    lip_samples=6,
)
```

- `profile`：`(radius, z)` 点可迭代。
- 半径非负。
- 薄壁旋转壳推荐 `from_shell_profiles(...)`。

### `LoftGeometry`

```python
LoftGeometry(profiles, *, cap=True, closed=True)
```

- `profiles`：3D 点环可迭代；各环点数相同。
- 低层网格放样；新壳/exterior 工作优先 `section_loft(...)`。

### `ExtrudeGeometry`

```python
ExtrudeGeometry(profile, height, *, cap=True, center=True, closed=True)
ExtrudeGeometry.centered(profile, height, *, cap=True, closed=True)
ExtrudeGeometry.from_z0(profile, height, *, cap=True, closed=True)
```

- `profile`：局部 XY 闭合轮廓。
- `height`：沿 Z 正拉伸长度。

### `ExtrudeWithHolesGeometry`

```python
ExtrudeWithHolesGeometry(
    outer_profile,
    hole_profiles,
    height,
    *,
    cap=True,
    center=True,
    closed=True,
)
```

- `outer_profile`：外环；`hole_profiles`：通孔环。

### `SweepGeometry`

```python
SweepGeometry(profile, path, *, cap=False, closed=True)
```

- 仅简单平移扫掠；管/轨类见 `45_wires_c.md`。

## 轮廓与壳辅助

### `rounded_rect_profile(...)`

```python
rounded_rect_profile(
    width: float,
    height: float,
    radius: float,
    *,
    corner_segments: int = 6,
) -> list[tuple[float, float]]
```

### `superellipse_profile(...)`

```python
superellipse_profile(
    width: float,
    height: float,
    exponent: float = 2.6,
    *,
    segments: int = 48,
) -> list[tuple[float, float]]
```

### `sample_catmull_rom_spline_2d(...)`

```python
sample_catmull_rom_spline_2d(
    points,
    *,
    samples_per_segment: int = 12,
    closed: bool = False,
    alpha: float = 0.5,
) -> list[tuple[float, float]]
```

### `sample_cubic_bezier_spline_2d(...)`

```python
sample_cubic_bezier_spline_2d(
    control_points,
    *,
    samples_per_segment: int = 12,
) -> list[tuple[float, float]]
```

### `superellipse_side_loft(...)`

```python
superellipse_side_loft(
    sections,
    *,
    exponents=2.8,
    segments: int = 56,
    cap: bool = True,
    closed: bool = True,
    min_height: float = 0.0001,
    min_width: float = 0.0001,
) -> MeshGeometry
```

### `split_superellipse_side_loft(...)`

```python
split_superellipse_side_loft(
    sections,
    *,
    split_y: float,
    exponents=2.8,
    segments: int = 56,
    cap: bool = True,
    closed: bool = True,
    min_height: float = 0.0001,
    min_width: float = 0.0001,
) -> tuple[MeshGeometry, MeshGeometry, tuple[float, float, float, float]]
```

### `resample_side_sections(...)`

```python
resample_side_sections(
    sections,
    *,
    samples_per_span: int = 2,
    smooth_passes: int = 0,
    min_height: float = 0.0001,
    min_width: float = 0.0001,
) -> list[tuple[float, float, float, float]]
```

## 面板开口

### `cut_opening_on_face(...)`

```python
cut_opening_on_face(
    shell_geometry: MeshGeometry,
    *,
    face: str,
    opening_profile,
    depth: float,
    offset=(0.0, 0.0),
    taper: float = 0.0,
) -> MeshGeometry
```

- 在已有网格壳选定盒状面上建内部开口喉部。
- **不**执行布尔减。
- 目标面已开口（壳状）时最佳。
- `face`：`"+x"`…`"-z"`。

## 导出为 `sdk.Mesh`

### `mesh_from_geometry(...)`

```python
mesh_from_geometry(
    geometry: MeshGeometry,
    name: str,
) -> Mesh
```

- 物化到运行时管理的内部 OBJ。
- 返回指向托管资源的 `sdk.Mesh`。
- 最终视觉为网格支撑时使用。

## 建议

### 可变行为

- `MeshGeometry` 变换原地修改。
- 多变体复用基网格前 `copy()` 或 `clone()`。

### 选择辅助层级

- 已知语义形状（旋钮、面框、车轮、格栅、支架）优先专题页。
- 新壳/exterior 放样优先 `section_loft(...)` 而非原始 `LoftGeometry(...)`。
- 轨/环/框优先 `45_wires_c.md` 样条优先指引；除非故意硬角，从 `tube_from_spline_points(...)` 或 `sweep_profile_along_spline(...)` 起步。

### 导出网格视觉

- 程序化网格创作可见形状。
- `mesh_from_geometry(...)` 转为 `sdk.Mesh`。
- 使用稳定逻辑名如 `"shell"`、`"rear_bracket"`，非路径。

## 示例

```python
shell = ExtrudeGeometry(
    rounded_rect_profile(0.12, 0.08, 0.01),
    0.03,
    cap=True,
    center=True,
)
mesh = mesh_from_geometry(shell, "shell")
```

```python
lip = LatheGeometry.from_shell_profiles(
    [(0.42, -0.30), (0.55, -0.12), (0.62, 0.00)],
    [(0.30, -0.24), (0.40, -0.10), (0.48, 0.00)],
    segments=72,
    end_cap="round",
    lip_samples=10,
)
```

## 另见

- `41_panels_and_grilles_c.md`
- `42_brackets_and_mounts_c.md`
- `43_fans_and_rotors_c.md`
- `44_knobs_and_controls_c.md`
- `45_wires_c.md`
- `46_section_lofts_c.md`
- `47_bezels_and_frames_c.md`
- `48_wheels_and_tires_c.md`
- `49_hinges_c.md`
- `50_placement_c.md`

## 面向 agent 的澄清

- 角度参数为弧度、右手定则，除非参数名以 `_deg` 结尾。
- `LoftGeometry` 通过 XY 投影验证轮廓；端盖仅当首尾轮廓为常 `z` 平面时如预期。
- `ExtrudeGeometry(..., center=True)` 实体以轮廓平面为中心，跨 `z∈[-height/2,+height/2]`；要 `z∈[0,height]` 用 `from_z0(...)`。
- `rounded_rect_profile`、`superellipse_profile` 返回居中逆时针 XY 环。
- `cut_opening_on_face` 自身不减封闭实体材料；添加喉部内壁，目标面已开或外切另做。
- 侧放样辅助截面元组在最终零件系：`(y, z_min, z_max, width)`，放样轴 `+Y`，截面在 `XZ`。
