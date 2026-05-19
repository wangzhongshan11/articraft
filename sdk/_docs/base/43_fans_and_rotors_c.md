# 风扇与转子（Fans and Rotors）

## 用途

用于外露轴流转子与蜗壳式叶轮零件；留在基础 `sdk` 表面，经常规 `mesh_from_geometry(...)` 导出。

## 导入

```python
from sdk import (
    FanRotorGeometry,
    FanRotorBlade,
    FanRotorHub,
    FanRotorShroud,
    BlowerWheelGeometry,
    mesh_from_geometry,
)
```

## 推荐 API

- `FanRotorGeometry`：绕局部 `Z` 旋转的轴流风扇转子
- `FanRotorBlade`、`FanRotorHub`、`FanRotorShroud`：叶片、轮毂与 tip 环定制
- `BlowerWheelGeometry`：鼠笼式叶轮

### `FanRotorGeometry`

```python
FanRotorGeometry(
    outer_radius,
    hub_radius,
    blade_count,
    *,
    thickness,
    blade_pitch_deg: float = 28.0,
    blade_sweep_deg: float = 20.0,
    blade_root_chord=None,
    blade_tip_chord=None,
    blade: FanRotorBlade | None = None,
    hub: FanRotorHub | None = None,
    shroud: FanRotorShroud | None = None,
    center: bool = True,
)
```

- 绕局部 `Z` 的轴流风扇转子。
- `outer_radius`：转子包络半径。
- `thickness`：轮毂深度与叶片截面厚度尺度。
- `blade_pitch_deg`、`blade_sweep_deg`、`FanRotorBlade.tip_pitch_deg` 使用**度**。
- `center=False`：最后端面在 `z=0`。
- `FanRotorBlade`：叶片平面与叶尖桨距；`FanRotorHub`：轮毂样式与孔；`FanRotorShroud`：附 tip 环。

### `FanRotorBlade`

```python
FanRotorBlade(
    shape: Literal["straight", "scimitar", "broad", "narrow"] = "straight",
    tip_pitch_deg: float | None = None,
    camber: float = 0.0,
    tip_clearance: float = 0.0,
)
```

- `shape`：叶片平面形状。
- `tip_pitch_deg`：叶尖可不同于叶根桨距。
- `camber`：截面可见曲率。
- `tip_clearance`：无护罩叶尖相对 `outer_radius` 回退。

### `FanRotorHub`

```python
FanRotorHub(
    style: Literal["flat", "domed", "capped", "spinner"] = "domed",
    rear_collar_height: float | None = None,
    rear_collar_radius: float | None = None,
    bore_diameter: float | None = None,
)
```

- `style`：前轮毂轮廓。
- `rear_collar_height`、`rear_collar_radius`：后侧套环。
- `bore_diameter`：中心通孔（有轴转子）。

### `FanRotorShroud`

```python
FanRotorShroud(
    thickness,
    depth: float | None = None,
    clearance: float = 0.0,
    lip_depth: float = 0.0,
)
```

- 转子周围附 tip 环。
- `thickness`：环径向壁厚。
- `depth`：环轴向深度。
- `clearance`：环外壁与 `outer_radius` 径向余量。
- `lip_depth`：前侧轴向延伸。

### `BlowerWheelGeometry`

```python
BlowerWheelGeometry(
    outer_radius,
    inner_radius,
    width,
    blade_count,
    *,
    blade_thickness,
    blade_sweep_deg: float = 35.0,
    backplate: bool = True,
    shroud: bool = True,
    center: bool = True,
)
```

- 绕局部 `Z` 的鼠笼叶轮。
- `width`：沿局部 `Z` 的轴向宽度。
- `blade_thickness`：平面叶片厚度。
- 叶片通道向内腔开口，非止于平内墙。
- `center=False`：最后端面在 `z=0`。

## 示例

```python
fan_rotor = FanRotorGeometry(
    0.070,
    0.020,
    7,
    thickness=0.010,
    blade_pitch_deg=31.0,
    blade_sweep_deg=24.0,
    blade=FanRotorBlade(
        shape="scimitar",
        tip_pitch_deg=12.0,
        camber=0.16,
    ),
    hub=FanRotorHub(
        style="spinner",
        bore_diameter=0.005,
    ),
    shroud=FanRotorShroud(
        thickness=0.004,
        depth=0.012,
        clearance=0.0015,
        lip_depth=0.002,
    ),
)
mesh = mesh_from_geometry(fan_rotor, "fan_rotor")
```

```python
blower_wheel = BlowerWheelGeometry(
    0.080,
    0.040,
    0.050,
    18,
    blade_thickness=0.004,
    blade_sweep_deg=25.0,
)
mesh = mesh_from_geometry(blower_wheel, "blower_wheel")
```

## 相关示例

- 在基础 SDK 示例中搜索轴流转子与鼠笼叶轮完整脚本。

## 面向 agent 的澄清

- `FanRotorGeometry` 用于旋转叶轮本身，非周围框、格栅或壳体。
- `FanRotorShroud` 为附 tip 环，非独立静止风道/壳体。
- 需要轴孔时优先 `FanRotorHub`，勿手工布尔开孔。
