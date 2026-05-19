# 铰链（Hinges）

## 用途

用于应显示真实叶片、链节与销几何的外露实用铰链。

## 导入

```python
from sdk import (
    BarrelHingeGeometry,
    PianoHingeGeometry,
    HingeHolePattern,
    HingePinStyle,
    mesh_from_geometry,
)
```

## 推荐 API

| 形状意图 | 辅助 |
| --- | --- |
| 外露双叶实用铰链 | `BarrelHingeGeometry` |
| 连续铰链条 | `PianoHingeGeometry` |
| 叶片孔型 | `HingeHolePattern` |
| 可见销端细节 | `HingePinStyle` |

## API 参考

### `BarrelHingeGeometry`

```python
BarrelHingeGeometry(
    length,
    *,
    leaf_width_a,
    leaf_width_b=None,
    leaf_thickness,
    pin_diameter,
    knuckle_outer_diameter=None,
    knuckle_count: int = 5,
    clearance: float = 0.0005,
    open_angle_deg: float = 180.0,
    holes_a: HingeHolePattern | None = None,
    holes_b: HingeHolePattern | None = None,
    pin: HingePinStyle | None = None,
    center: bool = True,
)
```

- 绕局部 `Z` 销轴的双叶桶形铰链。
- `center=False`：下端在 `z=0`。
- `HingeHolePattern`：圆孔或长槽；`HingePinStyle`：销头变体。

### `PianoHingeGeometry`

```python
PianoHingeGeometry(
    length,
    *,
    leaf_width_a,
    leaf_width_b=None,
    leaf_thickness,
    pin_diameter,
    knuckle_pitch,
    clearance: float = 0.0005,
    open_angle_deg: float = 180.0,
    holes_a: HingeHolePattern | None = None,
    holes_b: HingeHolePattern | None = None,
    pin: HingePinStyle | None = None,
    center: bool = True,
)
```

- 绕局部 `Z` 的连续铰链条。
- `knuckle_pitch`：沿条重复节距。
- `center=False`：下端在 `z=0`。

## 建议

- 仅用于外露实用铰链；暗藏柜铰或定制连杆应直接建模。
- 保留真实链节/销逻辑；勿用两平板加装饰圆柱替代。

## 示例

```python
barrel_hinge = BarrelHingeGeometry(
    0.090,
    leaf_width_a=0.024,
    leaf_width_b=0.020,
    leaf_thickness=0.0024,
    pin_diameter=0.003,
    holes_a=HingeHolePattern(style="round", count=3, diameter=0.0032, edge_margin=0.010),
    holes_b=HingeHolePattern(style="slotted", count=2, slot_size=(0.007, 0.003), edge_margin=0.012),
)
barrel_hinge_mesh = mesh_from_geometry(barrel_hinge, "barrel_hinge")
```

```python
piano_hinge = PianoHingeGeometry(
    0.180,
    leaf_width_a=0.016,
    leaf_width_b=0.014,
    leaf_thickness=0.0018,
    pin_diameter=0.0025,
    knuckle_pitch=0.012,
)
piano_hinge_mesh = mesh_from_geometry(piano_hinge, "piano_hinge")
```

## 另见

- `40_mesh_geometry_c.md`：低层网格构造辅助
