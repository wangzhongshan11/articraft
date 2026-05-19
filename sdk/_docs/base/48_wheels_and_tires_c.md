# 车轮与轮胎（Wheels and Tires）

## 用途

用于应读作真实滚动硬件的轮辋-轮胎视觉，而非泛化圆柱。

## 导入

```python
from sdk import (
    WheelGeometry,
    WheelRim,
    WheelHub,
    WheelFace,
    WheelSpokes,
    WheelBore,
    WheelFlange,
    BoltPattern,
    TireGeometry,
    TireCarcass,
    TireTread,
    TireGroove,
    TireSidewall,
    TireShoulder,
    mesh_from_geometry,
)
```

## 推荐 API

| 形状意图 | 辅助 |
| --- | --- |
| 轮辋、轮毂、盘面、辐条、安装孔 | `WheelGeometry` |
| 胎体、胎面、沟槽、胎侧、胎肩 | `TireGeometry` |
| 轮结构细节组 | `WheelRim`、`WheelHub`、`WheelFace`、`WheelSpokes`、`WheelBore`、`WheelFlange`、`BoltPattern` |
| 轮胎细节组 | `TireCarcass`、`TireTread`、`TireGroove`、`TireSidewall`、`TireShoulder` |

## API 参考

### `WheelGeometry`

```python
WheelGeometry(
    radius,
    width,
    *,
    rim: WheelRim | None = None,
    hub: WheelHub | None = None,
    face: WheelFace | None = None,
    spokes: WheelSpokes | None = None,
    bore: WheelBore | None = None,
    flange: WheelFlange | None = None,
    center: bool = True,
)
```

- 绕局部 `X` 旋转的轮辋/轮毂视觉。
- 宽度沿 `X`；径向轮廓在 `YZ`。
- `center=False`：内侧安装面在 `x=0`。
- 细节数据类覆盖实心轮、开槽轮、辐条轮、深碟面、推圈式等。

### `TireGeometry`

```python
TireGeometry(
    outer_radius,
    width,
    *,
    inner_radius: float | None = None,
    carcass: TireCarcass | None = None,
    tread: TireTread | None = None,
    grooves: Sequence[TireGroove] = (),
    sidewall: TireSidewall | None = None,
    shoulder: TireShoulder | None = None,
    center: bool = True,
)
```

- 沿局部 `X` 与 `WheelGeometry` 直接组合。
- `inner_radius`：轮座腔；`outer_radius`：外滚动半径。
- `center=False`：内侧端面在 `x=0`。
- 覆盖光辊、公路胎、方肩实用胎、肋条、人字、块/lug 等。

## 建议

- 材质不同时轮与胎拆成独立视觉。
- 用轮辅助做真实盘面结构，勿在盘上刻浅辐条线。
- 用胎辅助做真实胎侧胎面，勿用圆环/圆柱代替。

## 示例

### 轮胎对

```python
wheel = WheelGeometry(
    0.120,
    0.040,
    rim=WheelRim(
        inner_radius=0.082,
        flange_height=0.010,
        flange_thickness=0.004,
        bead_seat_depth=0.004,
    ),
    hub=WheelHub(
        radius=0.028,
        width=0.030,
        cap_style="domed",
        bolt_pattern=BoltPattern(
            count=5,
            circle_diameter=0.034,
            hole_diameter=0.004,
        ),
    ),
    face=WheelFace(dish_depth=0.006, front_inset=0.003, rear_inset=0.002),
    spokes=WheelSpokes(style="split_y", count=5, thickness=0.003, window_radius=0.010),
    bore=WheelBore(style="round", diameter=0.012),
)
wheel_mesh = mesh_from_geometry(wheel, "wheel")

tire = TireGeometry(
    0.145,
    0.052,
    inner_radius=0.110,
    carcass=TireCarcass(belt_width_ratio=0.66, sidewall_bulge=0.08),
    tread=TireTread(style="chevron", depth=0.006, count=18, angle_deg=26.0, land_ratio=0.58),
    grooves=(TireGroove(center_offset=0.0, width=0.006, depth=0.003),),
    sidewall=TireSidewall(style="rounded", bulge=0.06),
    shoulder=TireShoulder(width=0.006, radius=0.004),
)
tire_mesh = mesh_from_geometry(tire, "tire")
```

### 实用胎

```python
utility_tire = TireGeometry(
    0.180,
    0.080,
    inner_radius=0.132,
    tread=TireTread(style="block", depth=0.010, count=20, land_ratio=0.55),
    sidewall=TireSidewall(style="square", bulge=0.02),
    shoulder=TireShoulder(width=0.010, radius=0.003),
)
mesh = mesh_from_geometry(utility_tire, "utility_tire")
```

## 另见

- `40_mesh_geometry_c.md`：低层旋转体与壳几何
- 完整脚本见基础 SDK 滑板车轮+公路胎示例
