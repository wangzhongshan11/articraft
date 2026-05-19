# 线、管与框（Wires, Tubes, and Frames）

## 用途

用于把手、环、打蛋笼、风扇护罩、篮筐、管框等细弯件。几乎所有连续弯曲零件从样条辅助起步。

## 导入

```python
from sdk import (
    WirePath,
    tube_from_spline_points,
    sweep_profile_along_spline,
    rounded_rect_profile,
)
```

## 推荐 API

| 形状意图 | 辅助 |
| --- | --- |
| 平滑圆轨、把手、环、框（默认） | `tube_from_spline_points(...)` |
| 平滑非圆截面轨与装饰条 | `sweep_profile_along_spline(...)` |
| 可读的手工路径（弧/贝塞尔段） | `WirePath` + 样条/扫掠 |

## API 参考

### `tube_from_spline_points(...)`

```python
tube_from_spline_points(
    points,
    *,
    radius: float,
    samples_per_segment: int = 12,
    closed_spline: bool = False,
    spline: str = "catmull_rom",
    alpha: float = 0.5,
    radial_segments: int = 16,
    cap_ends: bool = True,
    up_hint=(0.0, 0.0, 1.0),
    min_segment_length: float = 1e-6,
) -> MeshGeometry
```

- 拟合样条后建圆管。
- `spline`：`"catmull_rom"` 或 `"bezier"`。
- `alpha`：Catmull-Rom 参数，仅 `"catmull_rom"`。
- `closed_spline`：闭合路径。
- `cap_ends`：开放路径端盖。

### `sweep_profile_along_spline(...)`

```python
sweep_profile_along_spline(
    points,
    *,
    profile,
    samples_per_segment: int = 12,
    closed_spline: bool = False,
    spline: str = "catmull_rom",
    alpha: float = 0.5,
    cap_profile: bool = True,
    up_hint=(0.0, 0.0, 1.0),
    min_segment_length: float = 1e-6,
) -> MeshGeometry
```

- 拟合样条后扫掠闭合 2D 截面。
- 截面非圆时用。

### `WirePath`

```python
WirePath(start)
WirePath.from_points(points) -> WirePath
```

方法：

```python
wp.line_to(point) -> WirePath
wp.line_by(dx, dy, dz) -> WirePath
wp.bezier_to(control1, control2, end, *, samples=12) -> WirePath
wp.arc(*, center, normal, angle, segments=16) -> WirePath
wp.extend(points) -> WirePath
wp.to_points() -> list[tuple[float, float, float]]
```

可读性优先于从点集拟合时，用 `WirePath`，再以 `wp.to_points()` 喂给 `tube_from_spline_points(...)` 或 `sweep_profile_along_spline(...)`，使最终零件仍为平滑扫掠管。

## 建议

### 默认决策顺序

- 应读作一根连续弯管/线：先 `tube_from_spline_points(...)`。
- 连续弯轨但截面非圆：`sweep_profile_along_spline(...)`。
- 路径程序化比点列更易：`WirePath` → `to_points()` → 样条/扫掠。

### 调平滑度

- 样条结果粗糙时先增 `samples_per_segment`。
- 管仍显棱面时增 `radial_segments`。

## 示例

### 平滑把手

```python
handle = tube_from_spline_points(
    [
        (-0.03, 0.00, 0.00),
        (-0.01, 0.02, 0.01),
        (0.01, 0.02, 0.01),
        (0.03, 0.00, 0.00),
    ],
    radius=0.002,
    samples_per_segment=18,
    radial_segments=20,
    cap_ends=True,
)
```

### 自定义截面轨

```python
trim = sweep_profile_along_spline(
    [
        (-0.04, 0.00, 0.00),
        (-0.01, 0.02, 0.01),
        (0.02, 0.01, 0.01),
        (0.05, 0.00, 0.00),
    ],
    profile=rounded_rect_profile(0.004, 0.002, radius=0.0007),
    samples_per_segment=18,
    cap_profile=True,
)
```

### 用 `WirePath` 写平滑路径

```python
wp = (
    WirePath((-0.03, 0.00, 0.00))
    .bezier_to(
        (-0.02, 0.02, 0.01),
        (0.02, 0.02, 0.01),
        (0.03, 0.00, 0.00),
        samples=18,
    )
)

handle = tube_from_spline_points(
    wp.to_points(),
    radius=0.002,
    samples_per_segment=6,
    radial_segments=20,
    cap_ends=True,
)
```

弧或类贝塞尔段程序化更易、但最终仍应读作连续弯折时用此模式。

## 另见

- `40_mesh_geometry_c.md`：通用程序化网格创作

## 面向 agent 的澄清

- 样条/路径角度为弧度，右手定则。
- `spline="bezier"` 期望链式三次贝塞尔控制点，非通用过点插值。开放链 `(n-1)%3==0`；闭合链点列须已闭合。
- `up_hint` 定义扫掠截面运输标架；改 `up_hint` 会改截面滚转，即使路径点不变。
