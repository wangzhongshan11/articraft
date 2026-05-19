# 面框与框条（Bezels and Frames）

## 用途

对框开口、装饰条与凹周边，用 `BezelGeometry` 代替叠圆角盒与手工开孔。

## 导入

```python
from sdk import (
    BezelGeometry,
    BezelFace,
    BezelRecess,
    BezelVisor,
    BezelFlange,
    BezelMounts,
    BezelCutout,
    BezelEdgeFeature,
    mesh_from_geometry,
)
```

## 推荐 API

| 形状意图 | 辅助 |
| --- | --- |
| 默认框开口、装饰环、面板围框 | `BezelGeometry` |
| 前唇与装饰面造型 | `BezelFace` |
| 凹腔或显示/仪表嵌入 | `BezelRecess` |
| 帽檐式顶伸 | `BezelVisor` |
| 后法兰与安装延伸 | `BezelFlange` |
| 凸台、耳片、后安装型 | `BezelMounts` |
| 边缘缺口与局部中断 | `BezelCutout`、`BezelEdgeFeature` |

## API 参考

### `BezelGeometry`

```python
BezelGeometry(
    opening_size,
    outer_size,
    depth,
    *,
    opening_shape: Literal["rect", "rounded_rect", "circle", "ellipse", "superellipse"] = "rounded_rect",
    outer_shape: Literal["rect", "rounded_rect", "circle", "ellipse", "superellipse"] = "rounded_rect",
    opening_corner_radius: float = 0.0,
    outer_corner_radius: float = 0.0,
    wall: float | tuple[float, float, float, float] | None = None,
    face: BezelFace | None = None,
    recess: BezelRecess | None = None,
    visor: BezelVisor | None = None,
    flange: BezelFlange | None = None,
    mounts: BezelMounts | None = None,
    cutouts: Sequence[BezelCutout] = (),
    edge_features: Sequence[BezelEdgeFeature] = (),
    center: bool = True,
)
```

- 框开口，可选凹腔、帽檐、法兰、后安装、边缘切口与装饰特征。
- 开口在局部 `XY`；深度沿 `Z`。
- `center=False`：后安装面在 `z=0`。
- 用于显示框、仪表装饰、灯/透镜框、凹面板围框。

## 建议

- 应读作开口周围装饰/框时用它，非实心盒打孔。
- 前面与后安装逻辑可见时显式建模。
- 真实装饰非对称时用非对称 `wall`。

## 示例

### 圆角矩形显示框

```python
display_bezel = BezelGeometry(
    (0.080, 0.050),
    (0.110, 0.080),
    0.012,
    opening_shape="rounded_rect",
    outer_shape="rounded_rect",
    opening_corner_radius=0.006,
    outer_corner_radius=0.010,
)
mesh = mesh_from_geometry(display_bezel, "display_bezel")
```

### 凹仪表框

```python
instrument_bezel = BezelGeometry(
    (0.072, 0.048),
    (0.108, 0.084),
    0.016,
    face=BezelFace(style="radiused_step", front_lip=0.003, fillet=0.002),
    recess=BezelRecess(depth=0.005, inset=0.004, floor_radius=0.0015),
    mounts=BezelMounts(style="bosses", hole_count=4, hole_diameter=0.003, boss_diameter=0.007, setback=0.008),
)
mesh = mesh_from_geometry(instrument_bezel, "instrument_bezel")
```

## 另见

- `40_mesh_geometry_c.md`：低层壳与开口辅助
- 完整脚本见基础 SDK 非对称面板框示例
