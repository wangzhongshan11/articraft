# CadQuery 辅助

## 用途

`sdk` 保留基础 SDK 的关节物体、测试与导出栈，但用 CadQuery 创作可见网格几何。

适用于：

- 关节结构应在 Python/URDF 空间保持显式
- 可见几何用 CadQuery 更易创作
- 最终视觉应为网格支撑

## 导入

```python
import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    cadquery_local_aabb,
    export_cadquery_components,
    export_cadquery_mesh,
    mesh_components_from_cadquery,
    mesh_from_cadquery,
    mesh_from_input,
    save_cadquery_obj,
    tessellate_cadquery,
)
```

## 推荐 API

- `cadquery_local_aabb(...)`
- `tessellate_cadquery(...)`
- `export_cadquery_mesh(...)`
- `export_cadquery_components(...)`
- `mesh_from_cadquery(...)`
- `mesh_components_from_cadquery(...)`

兼容辅助：

- `save_cadquery_obj(...)`

## 单位

CadQuery 本身无单位。在 `sdk` 中，已创作几何必须以**米**落地。

- CadQuery 模型已用米创作时，保持 `unit_scale=1.0`。
- 以毫米创作时，将字面值改为米，或在导出时**恰好一次**传 `unit_scale=0.001`。
- `unit_scale` 作用于整个细分结果，含已求解装配/组件位置。

## 辅助参考

### `tessellate_cadquery(...)`

```python
tessellate_cadquery(
    model: object,
    *,
    tolerance: float = 0.001,
    angular_tolerance: float = 0.1,
    unit_scale: float = 1.0,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]
```

- 返回原始顶点与三角面。
- 需要细分几何而非导出 OBJ 时使用。

### `cadquery_local_aabb(...)`

```python
cadquery_local_aabb(
    model: object,
    *,
    tolerance: float = 0.001,
    angular_tolerance: float = 0.1,
    unit_scale: float = 1.0,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]
```

- 细分 CadQuery 结果的局部轴对齐包围盒。
- 附着网格到 `ArticulatedObject` 前探测尺寸/放置时有用。

### `export_cadquery_mesh(...)`

```python
export_cadquery_mesh(
    model: object,
    name: str,
    *,
    assets=None,
    tolerance: float = 0.001,
    angular_tolerance: float = 0.1,
    unit_scale: float = 1.0,
) -> CadQueryMeshExport
```

```python
CadQueryMeshExport(
    mesh: Mesh,
    local_aabb,
    center_xyz,
    size_xyz,
)
```

- 内部物化 OBJ，返回托管 `sdk.Mesh` 与局部边界。
- `name`：逻辑网格名如 `"door_panel"`，或遗留路径式 `"door_panel.obj"`。
- `assets`：可选显式资源所有者/根；托管 harness 外需稳定磁盘路径时读 `../common/40_assets_c.md`。
- `tolerance`：线性细分容差。
- `angular_tolerance`：角度细分容差，**弧度**。
- `unit_scale`：缩放细分几何与 CadQuery 装配位置。

### `export_cadquery_components(...)`

```python
export_cadquery_components(
    model: object,
    name: str,
    *,
    assets=None,
    tolerance: float = 0.001,
    angular_tolerance: float = 0.1,
    unit_scale: float = 1.0,
) -> list[CadQueryMeshExport]
```

- 将 CadQuery 多形体工作平面或装配拆为每组件一个导出网格。
- 在选定逻辑名下使用编号托管名如 `"pair__component_001.obj"`。
- 按 CadQuery 顺序返回每个 `CadQueryMeshExport`。

### `mesh_from_cadquery(...)`

```python
mesh_from_cadquery(
    model: object,
    name: str,
    *,
    assets=None,
    tolerance: float = 0.001,
    angular_tolerance: float = 0.1,
    unit_scale: float = 1.0,
) -> Mesh
```

- 将 CadQuery 视觉附着到零件的**常规**辅助；参数同 `export_cadquery_mesh(...)`，仅返回 `Mesh`。

### `mesh_components_from_cadquery(...)`

```python
mesh_components_from_cadquery(
    model: object,
    name: str,
    *,
    assets=None,
    tolerance: float = 0.001,
    angular_tolerance: float = 0.1,
    unit_scale: float = 1.0,
) -> list[Mesh]
```

- `export_cadquery_components(...)` 的仅组件便捷包装；一 CadQuery 源变多个网格视觉时用。

### `save_cadquery_obj(...)`

```python
save_cadquery_obj(
    model: object,
    name: str,
    *,
    assets=None,
    tolerance: float = 0.001,
    angular_tolerance: float = 0.1,
    unit_scale: float = 1.0,
) -> Path
```

- 公开兼容辅助，直接返回物化 OBJ 路径。
- 新代码若要托管 `Mesh`，优先 `export_cadquery_mesh(...)` 或 `mesh_from_cadquery(...)`。

## 推荐模式

CadQuery 负责可见网格，再作为普通视觉挂到 `ArticulatedObject` 零件上。

SDK 材质赋给结果 `Visual`，**非** CadQuery 面或单导出网格内的子体。`mesh_from_cadquery(...)` **不保留** CadQuery 面色、逐面材质、UV 与纹理坐标。不同区域需不同材质时，拆成多个 CadQuery 网格/组件，各挂独立 `material=...` 视觉。

```python
door_shape = (
    cq.Workplane("XY")
    .box(0.58, 0.02, 0.78)
    .edges("|Z").fillet(0.01)
)

door = model.part("door")
door.visual(mesh_from_cadquery(door_shape, "door"))
```

## 建议

- 关节在 `ArticulatedObject` 保持显式；勿从 CadQuery 装配推断 URDF 关节。
- 惯性显式给出，勿从导出网格推导。
- 使用稳定逻辑网格名如 `"door"`、`"left_bracket"`，非文件系统路径。
- 谨慎使用重复 `faces(...).workplane()` 循环；重复特征时常用固定参考平面更稳。

## 示例

```python
def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject("cabinet_door")

    body = model.part("body")
    body.visual(Box((0.6, 0.3, 0.8)))

    door_shape = (
        cq.Workplane("XY")
        .box(0.58, 0.02, 0.78)
        .edges("|Z").fillet(0.01)
    )
    door = model.part("door")
    door.visual(mesh_from_cadquery(door_shape, "door"))

    model.articulation(
        "body_to_door",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(-0.29, 0.15, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.7, effort=5.0, velocity=1.0),
    )

    return model
```

## 面向 agent 的澄清

- `mesh_from_cadquery(...)`、`export_cadquery_mesh(...)` 接受 CadQuery `Shape`、`Workplane`、`Assembly`；工作平面从其解析实体导出；装配按各组件当前 CadQuery 位置导出。
- `cadquery_local_aabb(...)`、`export_cadquery_components(...)`、`mesh_components_from_cadquery(...)` 接受相同输入类型。
- 约束 CadQuery 装配须在导出前求解；SDK **不会**替你调用 `solve()`。
- 每个 CadQuery 模型择一单位故事：直接以米创作，或保持源单位并在导出到 `sdk` 时传匹配 `unit_scale`。
- 导出保留 CadQuery 局部系；SDK **不**自动重定心、推断铰链枢轴或把几何移到关节轴。
- 铰链枢轴应在铰链处时：在 CadQuery 局部系建模，或用 `visual(origin=Origin(...))` 显式对齐网格系与关节系。
- 材质按 SDK 视觉分配；多材质 CadQuery 几何先拆成多个导出网格/组件。
- 每 CadQuery 组件要单独网格时用 `export_cadquery_components(...)` 或 `mesh_components_from_cadquery(...)`。

## 另见

- `../common/80_testing_c.md`：共享测试 API
- `../common/00_quickstart_c.md`：整体脚本契约
- `39d_cadquery_gears_c.md`：内嵌齿轮生成器与 Workplane 齿轮插件
- `../common/40_assets_c.md`：显式资源根控制
