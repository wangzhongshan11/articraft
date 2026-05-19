# 支架与安装件（Brackets and Mounts）

## 用途

用于安装逻辑清晰的支架类零件：叉耳、开叉与轭，带真实厚度、开口与销/耳轴支撑。

## 导入

```python
from sdk import (
    ClevisBracketGeometry,
    PivotForkGeometry,
    TrunnionYokeGeometry,
    mesh_from_geometry,
)
```

## 推荐 API

| 形状意图 | 辅助 |
| --- | --- |
| 双耳底座与横孔销接支架 | `ClevisBracketGeometry` |
| 需前向插入间隙的开前叉 | `PivotForkGeometry` |
| 托住旋转耳轴/桶的轭 | `TrunnionYokeGeometry` |

## API 参考

### `ClevisBracketGeometry`

```python
ClevisBracketGeometry(
    overall_size,
    *,
    gap_width,
    bore_diameter,
    bore_center_z,
    base_thickness,
    corner_radius: float = 0.0,
    center: bool = True,
)
```

- U 形叉耳，底座与横孔。
- `overall_size`：`(width_x, depth_y, height_z)`。
- `gap_width`：颊板间净距。
- `bore_center_z`：自底面向上量。
- `center=False`：底安装面在 `z=0`。

### `PivotForkGeometry`

```python
PivotForkGeometry(
    overall_size,
    *,
    gap_width,
    bore_diameter,
    bore_center_z,
    bridge_thickness,
    corner_radius: float = 0.0,
    center: bool = True,
)
```

- 开前叉，两齿与后桥。
- `gap_width`：齿间净距。
- `bridge_thickness`：后连接桥沿局部 `Y` 的厚度。
- `bore_center_z`：自底面向上量。

### `TrunnionYokeGeometry`

```python
TrunnionYokeGeometry(
    overall_size,
    *,
    span_width,
    trunnion_diameter,
    trunnion_center_z,
    base_thickness,
    corner_radius: float = 0.0,
    center: bool = True,
)
```

- 颊板耳轴孔的轭式支撑。
- `span_width`：颊板间净开口。
- `trunnion_center_z`：自底面向上量。
- `center=False`：底座在 `z=0`。

## 建议

- 支架应读作带可用安装几何的单一真实件，非装饰占位。
- 保留真实插入与摆动间隙；勿为省事封死叉口或轭口。
- 若无颊板开口、仅为弯平板，用低层网格工具。

## 示例

```python
clevis = ClevisBracketGeometry(
    (0.08, 0.04, 0.06),
    gap_width=0.032,
    bore_diameter=0.012,
    bore_center_z=0.038,
    base_thickness=0.012,
)
clevis_mesh = mesh_from_geometry(clevis, "clevis")
```

```python
pivot_fork = PivotForkGeometry(
    (0.08, 0.05, 0.05),
    gap_width=0.034,
    bore_diameter=0.010,
    bore_center_z=0.028,
    bridge_thickness=0.012,
)
pivot_fork_mesh = mesh_from_geometry(pivot_fork, "pivot_fork")
```

```python
trunnion_yoke = TrunnionYokeGeometry(
    (0.12, 0.05, 0.08),
    span_width=0.060,
    trunnion_diameter=0.016,
    trunnion_center_z=0.050,
    base_thickness=0.014,
)
trunnion_yoke_mesh = mesh_from_geometry(trunnion_yoke, "trunnion_yoke")
```

## 另见

- `40_mesh_geometry_c.md`：低层拉伸与轮廓辅助
- `50_placement_c.md`：将支架零件安装到父体
