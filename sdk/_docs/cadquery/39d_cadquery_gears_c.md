# CadQuery 齿轮

## 用途

需要生成齿轮而非手画齿形时使用。`sdk` 内嵌来自 `cq_gears` 的 CadQuery 兼容齿轮表面，并从顶层 `sdk` 再导出。

输出为常规 CadQuery 几何，可：

- 调用 `.build()` 并用 `mesh_from_cadquery(...)` 附着
- 在可用时对 pair/gearset 辅助调用 `.assemble()`
- 使用保留的 `cadquery.Workplane.gear(...)` 与 `.addGear(...)` 插件工作流

## 导入

```python
import cadquery as cq

from sdk import (
    BevelGear,
    BevelGearPair,
    CrossedGearPair,
    CrossedHelicalGear,
    GearBase,
    HerringboneGear,
    HerringbonePlanetaryGearset,
    HerringboneRackGear,
    HerringboneRingGear,
    HyperbolicGear,
    HyperbolicGearPair,
    PlanetaryGearset,
    RackGear,
    RingGear,
    SpurGear,
    Worm,
    addGear,
    gear,
)
```

## 依赖

当前环境须安装 `cadquery`。本仓库预期：

```bash
uv sync --group dev
```

## 推荐 API

- 单齿轮：`SpurGear`、`HerringboneGear`、`RingGear`、`HerringboneRingGear`、`BevelGear`、`RackGear`、`HerringboneRackGear`、`Worm`、`CrossedHelicalGear`、`HyperbolicGear`
- 装配与配对：`PlanetaryGearset`、`HerringbonePlanetaryGearset`、`BevelGearPair`、`CrossedGearPair`、`HyperbolicGearPair`
- 工作平面插件：`gear(...)`、`addGear(...)`

## 共享契约

### `GearBase.build(...)`

```python
gear.build(**kv_params) -> cadquery.Shape
```

- 单齿轮类返回 CadQuery 实体或复合体。
- 配对与齿轮系辅助的 `.build(...)` 返回 CadQuery 复合体。
- 构造器 `**build_params` 成为后续 `.build(...)` / `.assemble(...)` 的默认关键字参数。

## 单齿轮族

### `SpurGear(...)`

```python
SpurGear(
    module,
    teeth_number,
    width,
    pressure_angle=20.0,
    helix_angle=0.0,
    clearance=0.0,
    backlash=0.0,
    addendum_coeff=None,
    dedendum_coeff=None,
    **build_params,
)
```

- `module`：当前 CadQuery 单位下的模数。
- `teeth_number`：齿数。
- `width`：沿齿轮轴的体宽。
- `pressure_angle`：压力角，**度**。
- `helix_angle`：螺旋角，**度**；`0.0` 为直齿。
- `clearance`：额外齿根间隙。
- `backlash`：齿侧间隙。
- `addendum_coeff`、`dedendum_coeff`：可选齿顶/齿根系数覆盖。
- `**build_params`：默认构建时覆盖。

`build(...)` 接受：

```python
bore_d=None,
missing_teeth=None,
hub_d=None,
hub_length=None,
recess_d=None,
recess=None,
bottom_recess=None,
bottom_recess_d=None,
bottom_hub_d=None,
n_spokes=None,
spoke_width=None,
spoke_fillet=None,
spokes_id=None,
spokes_od=None,
chamfer=None,
chamfer_top=None,
chamfer_bottom=None,
```

- `bore_d`：中心孔径。
- `missing_teeth`：缺失齿范围 `(start, end)` 或列表。
- `hub_d`、`hub_length`：轮毂直径与轴向长度。
- `recess_d`、`recess`：顶面凹腔直径与深度。
- `bottom_recess`、`bottom_recess_d`、`bottom_hub_d`：底面凹腔与轮毂覆盖。
- `n_spokes`、`spoke_width`、`spoke_fillet`、`spokes_id`、`spokes_od`：辐条切除控制。
- `chamfer`、`chamfer_top`、`chamfer_bottom`：齿棱倒角。

### `HerringboneGear(...)`

构造器同 `SpurGear(...)`。

- 双螺旋人字齿体；`build(...)` 参数同 `SpurGear(...)`。

### `RingGear(...)`

```python
RingGear(
    module,
    teeth_number,
    width,
    rim_width,
    pressure_angle=20.0,
    helix_angle=0.0,
    clearance=0.0,
    backlash=0.0,
    **build_params,
)
```

- `rim_width`：内齿外侧额外轮缘径向厚度。
- 其余含义同 `SpurGear(...)`。

`build(...)` 接受：`chamfer`、`chamfer_top`、`chamfer_bottom`。

### `HerringboneRingGear(...)`

构造器同 `RingGear(...)`；双螺旋内齿圈；`build(...)` 同 `RingGear(...)`。

### `BevelGear(...)`

```python
BevelGear(
    module,
    teeth_number,
    cone_angle,
    face_width,
    pressure_angle=20.0,
    helix_angle=0.0,
    clearance=0.0,
    backlash=0.0,
    **build_params,
)
```

- `cone_angle`：节锥角，**度**。
- `face_width`：沿锥面的齿宽。
- `build(...)`：`bore_d`、`trim_bottom`、`trim_top`。

### `RackGear(...)`

```python
RackGear(
    module,
    length,
    width,
    height,
    pressure_angle=20.0,
    helix_angle=0.0,
    clearance=0.0,
    backlash=0.0,
    **build_params,
)
```

- `length`：沿 X 总长；`width`：局部系 Z 向齿宽；`height`：齿根下背高。
- `build()` 无额外公开参数。

### `HerringboneRackGear(...)`

同 `RackGear(...)` 构造器；双人字齿条；`build()` 同 `RackGear(...)`。

### `Worm(...)`

```python
Worm(
    module,
    lead_angle,
    n_threads,
    length,
    pressure_angle=20.0,
    clearance=0.0,
    backlash=0.0,
    **build_params,
)
```

- `lead_angle`：导程角，**度**；`n_threads`：头数；`length`：轴向长度。
- `build(...)`：`bore_d`。

### `CrossedHelicalGear(...)`

构造器字段同 `SpurGear(...)` 语义；需单件斜交螺旋成员时用；`build(...)` 同 `SpurGear(...)`。

### `HyperbolicGear(...)`

- `twist_angle`：双曲总扭角，**度**。
- `build(...)` 同 `SpurGear(...)`。

## 配对与齿轮系辅助

### `PlanetaryGearset(...)`

太阳轮、等间距行星轮、齿圈；`build()` 返回复合体。

`assemble(...)`：`build_sun`、`build_planets`、`build_ring`、`sun_build_args`、`planet_build_args`、`ring_build_args`。

### `HerringbonePlanetaryGearset(...)`

同 `PlanetaryGearset(...)`，为人字齿太阳/行星/齿圈。

### `BevelGearPair(...)`

`assemble(...)`：`build_gear`、`build_pinion`、`transform_pinion`、`gear_build_args`、`pinion_build_args`。

### `CrossedGearPair(...)`

`assemble(...)`：`build_gear1`、`build_gear2`、`transform_gear2`、`gear1_build_args`、`gear2_build_args`。

### `HyperbolicGearPair(...)`

`assemble(...)`：字段同 `CrossedGearPair` 风格。

## 工作平面插件

### `gear(...)`

```python
gear(
    workplane,
    gear_,
    *build_args,
    **build_kv_args,
) -> cadquery.Workplane
```

在工作平面各点放置齿轮；亦安装为 `cq.Workplane.gear(...)`。

### `addGear(...)`

构建并并入当前工作平面实体；亦安装为 `cq.Workplane.addGear(...)`。

## 推荐模式

```python
import cadquery as cq

from sdk import SpurGear, mesh_from_cadquery

spur = SpurGear(module=0.001, teeth_number=20, width=0.006, bore_d=0.004)
body = cq.Workplane("XY").gear(spur).val()

mesh = mesh_from_cadquery(body, "spur_gear")
```

## 说明

- 齿轮生成器使用当前 CadQuery 单位故事；导出到 `sdk` 时保持米或在导出时 `unit_scale`。
- 配对/齿轮系需要 CadQuery 装配结构用 `.assemble(...)`，要单一复合形状用 `.build(...)`。
- 从顶层 `sdk` 导入任一辅助即可使 `cq.Workplane.gear` 与 `cq.Workplane.addGear` 可用。
