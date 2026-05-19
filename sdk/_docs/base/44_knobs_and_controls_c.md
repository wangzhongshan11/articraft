# 旋钮与控件（Knobs and Controls）

## 用途

对旋转帽与家电旋钮，在手工旋转体加细节之前使用 `KnobGeometry`。

## 导入

```python
from sdk import (
    KnobGeometry,
    KnobSkirt,
    KnobGrip,
    KnobIndicator,
    KnobTopFeature,
    KnobBore,
    KnobRelief,
    mesh_from_geometry,
)
```

## 推荐 API

| 形状意图 | 辅助 |
| --- | --- |
| 普通家电/灶具/编码器/夹紧/指针旋钮 | `KnobGeometry` |
| 裙边、喇叭口、下缘倒角 | `KnobSkirt` |
| 直纹、肋、扇贝、滚花侧纹 | `KnobGrip` |
| 指针线、缺口、楔、点 | `KnobIndicator` |
| 顶帽、凹腔、顶嵌件 | `KnobTopFeature` |
| 轴接口 | `KnobBore` |
| 侧窗、顶凹、硬币槽 | `KnobRelief` |

## API 参考

### `KnobGeometry`

```python
KnobGeometry(
    diameter,
    height,
    *,
    body_style: Literal[
        "cylindrical",
        "tapered",
        "domed",
        "mushroom",
        "skirted",
        "hourglass",
        "faceted",
        "lobed",
    ] = "cylindrical",
    top_diameter=None,
    base_diameter=None,
    crown_radius: float = 0.0,
    edge_radius: float = 0.0,
    side_draft_deg: float = 0.0,
    skirt: KnobSkirt | None = None,
    grip: KnobGrip | None = None,
    indicator: KnobIndicator | None = None,
    top_feature: KnobTopFeature | None = None,
    bore: KnobBore | None = None,
    body_reliefs: Sequence[KnobRelief] = (),
    center: bool = True,
)
```

- 沿局部 `Z` 的旋转旋钮。
- `center=False`：安装面在 `z=0`。
- 用细节数据类添加握纹、指针、孔、顶帽，无需切换手工网格。
- 覆盖普通家电旋钮、直纹/滚花、蘑菇夹紧、多面合成、凸瓣手拧、指针表盘帽等。

## 建议

- 外观明显为旋钮时，即使多细节也先 `KnobGeometry`。
- 先定轮廓再细节：`skirted` 像灶具/烤箱；`faceted` 像机加工/合成；`lobed` 像手紧夹紧；`domed` 像消费电子；`hourglass` 像捏取表盘。
- 轴接口可见或提示要求 D 形/花键/键槽时建模轴接口。
- 用语义指示与顶特征代替临时布尔刻线。
- 勿对每个泛化「旋钮」提示默认同一裙边+直纹+刻线栈；按产品族匹配 body、grip、顶特征与指示。

## 示例

### 灶具旋钮

```python
range_knob = KnobGeometry(
    0.042,
    0.024,
    body_style="skirted",
    top_diameter=0.034,
    skirt=KnobSkirt(0.052, 0.006, flare=0.08, chamfer=0.0012),
    grip=KnobGrip(style="fluted", count=18, depth=0.0014),
    indicator=KnobIndicator(style="line", mode="engraved", depth=0.0008),
    bore=KnobBore(style="d_shaft", diameter=0.006, flat_depth=0.001),
)
mesh = mesh_from_geometry(range_knob, "range_knob")
```

### 滚花编码器旋钮

```python
encoder_knob = KnobGeometry(
    0.020,
    0.015,
    body_style="cylindrical",
    grip=KnobGrip(style="knurled", count=36, depth=0.0008, helix_angle_deg=20.0),
    indicator=KnobIndicator(style="dot", mode="raised", angle_deg=0.0),
)
mesh = mesh_from_geometry(encoder_knob, "encoder_knob")
```

### 多面合成旋钮

```python
synth_knob = KnobGeometry(
    0.026,
    0.018,
    body_style="faceted",
    base_diameter=0.028,
    top_diameter=0.020,
    edge_radius=0.0007,
    grip=KnobGrip(style="ribbed", count=12, depth=0.0007, width=0.0016),
    indicator=KnobIndicator(style="wedge", mode="raised", angle_deg=0.0),
    top_feature=KnobTopFeature(style="top_insert", diameter=0.010, height=0.0012),
)
mesh = mesh_from_geometry(synth_knob, "synth_knob")
```

### 凸瓣夹紧旋钮

```python
clamp_knob = KnobGeometry(
    0.040,
    0.022,
    body_style="lobed",
    base_diameter=0.028,
    top_diameter=0.036,
    crown_radius=0.0014,
    bore=KnobBore(style="round", diameter=0.008),
    body_reliefs=(KnobRelief(style="top_recess", width=0.014, depth=0.0016),),
)
mesh = mesh_from_geometry(clamp_knob, "clamp_knob")
```

## 另见

- `40_mesh_geometry_c.md`：低层旋转体、轮廓与导出
- 完整脚本见基础 SDK 直纹灶钮示例
