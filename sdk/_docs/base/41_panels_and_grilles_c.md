# 面板与格栅（`sdk`）

## 用途

用于带重复开孔、槽或百叶的面板。留在基础 `sdk` 表面，经 `mesh_from_geometry(...)` 导出。

## 导入

```python
from sdk import (
    PerforatedPanelGeometry,
    SlotPatternPanelGeometry,
    VentGrilleGeometry,
    VentGrilleSlats,
    VentGrilleFrame,
    VentGrilleMounts,
    VentGrilleSleeve,
    mesh_from_geometry,
)
```

## 推荐 API

- `PerforatedPanelGeometry`：圆孔板
- `SlotPatternPanelGeometry`：重复开槽面
- `VentGrilleGeometry`：带百叶与可选后套筒的框式通风/寄存器面
- `VentGrilleSlats`、`VentGrilleFrame`、`VentGrilleMounts`、`VentGrilleSleeve`：通风专用定制

### `PerforatedPanelGeometry`

```python
PerforatedPanelGeometry(
    panel_size,
    thickness,
    *,
    hole_diameter,
    pitch,
    frame=0.008,
    corner_radius=0.0,
    stagger=False,
    center=True,
)
```

- 在局部 `XY` 构建带圆通孔的平板。
- `pitch` 可为标量或 `(x_pitch, y_pitch)`。
- `stagger=True` 错开行。
- `center=False` 将后面置于 `z=0`。

### `SlotPatternPanelGeometry`

```python
SlotPatternPanelGeometry(
    panel_size,
    thickness,
    *,
    slot_size,
    pitch,
    frame=0.008,
    corner_radius=0.0,
    slot_angle_deg=0.0,
    stagger=False,
    center=True,
)
```

- 在局部 `XY` 构建开槽面。
- `slot_angle_deg`：平面内槽旋转，**度**。
- `pitch` 可为标量或 `(x_pitch, y_pitch)`。
- `center=False` 将后面置于 `z=0`。

### `VentGrilleGeometry`

```python
VentGrilleGeometry(
    panel_size,
    *,
    frame: float = 0.012,
    face_thickness: float = 0.004,
    duct_depth: float = 0.026,
    duct_wall: float = 0.003,
    slat_pitch: float = 0.018,
    slat_width: float = 0.009,
    slat_angle_deg: float = 35.0,
    slat_thickness: float | None = None,
    corner_radius: float = 0.0,
    slats: VentGrilleSlats | None = None,
    frame_profile: VentGrilleFrame | None = None,
    mounts: VentGrilleMounts | None = None,
    sleeve: VentGrilleSleeve | None = None,
    center: bool = True,
)
```

- 构建带真实百叶与可选后套筒的框式通风面。
- 格栅在局部 `XY`，沿 `Z` 延伸。
- `slat_angle_deg` 使用**度**。
- `center=False` 将最后端面置于 `z=0`。
- `VentGrilleSlats`：百叶轮廓、方向、退台与分隔条。
- `VentGrilleFrame`：齐平、斜面或圆角框处理。
- `VentGrilleMounts`：角安装孔。
- `VentGrilleSleeve`：移除套筒或短/全深套筒。

### `VentGrilleSlats`

```python
VentGrilleSlats(
    profile: Literal["flat", "airfoil", "boxed"] = "flat",
    direction: Literal["down", "up"] = "down",
    inset: float = 0.0,
    divider_count: int = 0,
    divider_width: float = 0.004,
)
```

- `profile`：百叶截面。
- `direction`：百叶角向上/下。
- `inset`：百叶向套筒内退。
- `divider_count`、`divider_width`：开口内竖向分隔条。

### `VentGrilleFrame`

```python
VentGrilleFrame(
    style: Literal["flush", "beveled", "radiused"] = "flush",
    depth: float = 0.0,
)
```

- `style="beveled"`：前倒角面。
- `style="radiused"`：前面周圆角。
- `depth`：可见倒角/圆角量。

### `VentGrilleMounts`

```python
VentGrilleMounts(
    style: Literal["none", "holes"] = "none",
    inset: float = 0.008,
    hole_diameter: float | None = None,
)
```

- `style="holes"`：四角通孔。
- `inset`：孔相对外轮廓退台。

### `VentGrilleSleeve`

```python
VentGrilleSleeve(
    style: Literal["none", "short", "full"] = "full",
    depth: float | None = None,
    wall: float | None = None,
)
```

- `style="none"`：无后套筒。
- `style="short"`：浅套筒。
- `style="full"`：全深套筒。
- `depth`、`wall` 可覆盖默认套筒尺寸。

## 示例

```python
speaker_face = PerforatedPanelGeometry(
    (0.16, 0.10),
    0.004,
    hole_diameter=0.006,
    pitch=(0.012, 0.012),
    frame=0.010,
    corner_radius=0.004,
    stagger=True,
)
mesh = mesh_from_geometry(speaker_face, "speaker_face")
```

```python
filter_face = SlotPatternPanelGeometry(
    (0.18, 0.09),
    0.004,
    slot_size=(0.024, 0.006),
    pitch=(0.032, 0.016),
    frame=0.010,
    corner_radius=0.004,
    slot_angle_deg=18.0,
    stagger=True,
)
mesh = mesh_from_geometry(filter_face, "filter_face")
```

```python
vent_grille = VentGrilleGeometry(
    (0.18, 0.10),
    frame=0.012,
    face_thickness=0.004,
    duct_depth=0.026,
    duct_wall=0.003,
    slat_pitch=0.018,
    slat_width=0.009,
    slat_angle_deg=30.0,
    corner_radius=0.006,
    slats=VentGrilleSlats(
        profile="airfoil",
        direction="down",
        divider_count=2,
        divider_width=0.004,
    ),
    frame_profile=VentGrilleFrame(style="beveled", depth=0.0012),
    mounts=VentGrilleMounts(style="holes", inset=0.010, hole_diameter=0.0032),
    sleeve=VentGrilleSleeve(style="full"),
)
mesh = mesh_from_geometry(vent_grille, "vent_grille")
```

## 面向 agent 的澄清

- 成品格栅/寄存器面用 `VentGrilleGeometry`；形状匹配时不要退回手工逐片百叶。
- `VentGrilleSleeve(style="none")` 适合浅家电通风与仅前面格栅。
- 分隔条在 `VentGrilleSlats` 中，非独立框辅助。
