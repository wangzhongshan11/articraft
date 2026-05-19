# 截面放样（Section Lofts）

## 用途

当壳体或外形可由少量有序截面（可选路径与对称）描述时用 `section_loft(...)`。

## 导入

```python
from sdk import LoftTessellation, LoftSection, SectionLoftSpec, section_loft, repair_loft
```

## 推荐 API

- `section_loft(...)`
- `SectionLoftSpec`
- `repair_loft(...)`

## 核心入口

### `section_loft(...)`

```python
section_loft(
    spec: SectionLoftSpec | Sequence[LoftSection | Sequence[Sequence[float]]],
    **overrides,
) -> MeshGeometry
```

接受形式：

- 原始截面环序列
- `SectionLoftSpec(...)`

每截面环为有序闭合 3D 点环；至少两截面。

## 规格类型

### `LoftTessellation`

```python
LoftTessellation(
    tolerance: float = 0.001,
    angular_tolerance: float = 0.1,
)
```

- `tolerance`：线性细分容差。
- `angular_tolerance`：角度细分容差。

### `LoftSection`

```python
LoftSection(points: tuple[tuple[float, float, float], ...])
```

- `points`：一个有序截面环。

### `SectionLoftSpec`

```python
SectionLoftSpec(
    sections: tuple[LoftSection, ...],
    path: tuple[tuple[float, float, float], ...] | None = None,
    guide_curves: Mapping[str, tuple[tuple[float, float, float], ...]] | None = None,
    cap: bool = True,
    solid: bool = True,
    symmetry: str | None = None,
    ruled: bool = False,
    continuity: str = "C2",
    parametrization: str = "uniform",
    degree: int = 3,
    compat: bool = True,
    smoothing: bool = False,
    weights: tuple[float, float, float] = (1.0, 1.0, 1.0),
    repair: str = "auto",
    tessellation: LoftTessellation = LoftTessellation(),
)
```

常用字段：

- `sections`：有序截面（必填）
- `path`：路径驱动多截面扫掠的可选路径
- `cap`：请求端盖
- `solid`：支持时请求实体
- `symmetry`：可选；支持值 `mirror_yz`
- `repair`：`auto`、`mesh`、`kernel` 或 `off`
- `tessellation`：网格结果细分设置

高级后端调参字段：

- `guide_curves`
- `ruled`
- `continuity`
- `parametrization`
- `degree`
- `compat`
- `smoothing`
- `weights`

常规创作保持默认；困难放样再调。

## 修复

### `repair_loft(...)`

```python
repair_loft(
    geometry_or_spec: MeshGeometry | SectionLoftSpec | Sequence[LoftSection | Sequence[Sequence[float]]],
    *,
    repair: str = "auto",
) -> MeshGeometry
```

- 输入已是 `MeshGeometry`：网格侧修复。
- 输入为放样规格或原始截面：按 `repair` 模式重建放样。

## 建议

### 截面对应

- 从头到尾保持截面顺序一致。
- 每截面一个干净环。
- 周长点尽量对应。

### 何时加 `path`

- 常规截面放样可省略 `path`。
- 整体需弯曲或沿中心线时再加 `path`。

### 何时用 `repair_loft(...)`

- 稀疏/粗糙截面产生明显破损网格时。
- 优先于立即动用高级后端控制。

## 示例

原始截面：

```python
geom = section_loft(
    [
        [(-0.05, -0.03, 0.00), (0.05, -0.03, 0.00), (0.05, 0.03, 0.00), (-0.05, 0.03, 0.00)],
        [(-0.03, -0.02, 0.08), (0.03, -0.02, 0.08), (0.03, 0.02, 0.08), (-0.03, 0.02, 0.08)],
    ]
)
```

结构化规格：

```python
geom = section_loft(
    SectionLoftSpec(
        sections=(section0, section1, section2),
        path=((0.0, 0.0, 0.0), (0.02, 0.01, 0.04), (0.04, 0.0, 0.08)),
        symmetry="mirror_yz",
    )
)
```

修复：

```python
clean = repair_loft(spec, repair="mesh")
```

## 另见

- `40_mesh_geometry_c.md`：低层网格放样辅助

## 面向 agent 的澄清

- `guide_curves` 故意收窄：支持键 `spine`、`aux_spine`、`binormal`。
- 省略 `path` 且存在 `guide_curves.spine` 时，spine 成为扫掠路径。
- 走路径驱动扫掠分支时，若干高级字段（`continuity`、`parametrization`、`degree`、`compat`、`smoothing`、`weights`）非活跃旋钮；视为高级/条件控制，非保证全局行为。
