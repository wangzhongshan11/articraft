# 测试（Testing）

从顶层 `sdk` 导入：

```python
from sdk import AllowedOverlap, TestContext, TestFailure, TestReport
```

`TestContext` 是已创作模型的 SDK 测试 harness。记录阻塞失败、非阻塞警告与显式豁免，由 `run_tests()` 返回 `TestReport`。

## 公开类型

### `TestFailure`

```python
TestFailure(name: str, details: str)
```

- `name`：记录的检查名。
- `details`：存入报告的失败详情。

### `AllowedOverlap`

```python
AllowedOverlap(
    link_a: str,
    link_b: str,
    reason: str,
    elem_a: str | None = None,
    elem_b: str | None = None,
)
```

- `allow_overlap(...)` 记录的结构化重叠豁免。

### `TestReport`

```python
TestReport(
    passed: bool,
    checks_run: int,
    checks: tuple[str, ...],
    failures: tuple[TestFailure, ...],
    warnings: tuple[str, ...] = (),
    allowances: tuple[str, ...] = (),
    allowed_isolated_parts: tuple[str, ...] = (),
    allowed_overlaps: tuple[AllowedOverlap, ...] = (),
)
```

- `passed`：无阻塞失败时为 `True`。
- `checks_run`：记录检查数。
- `checks`：有序检查名。
- `failures`：阻塞失败。
- `warnings`：警告及失败级警告检查。
- `allowances`：`allow_*` 的人类可读条目。
- `allowed_isolated_parts`：`allow_isolated_part(...)` 允许的零件名。
- `allowed_overlaps`：`allow_overlap(...)` 的结构化重叠豁免。

## 构造

```python
ctx = TestContext(model, seed=0)
```

- `model`：被测 `ArticulatedObject`。
- `seed`：姿态采样检查的确定性种子。

生成脚本应以：

```python
return ctx.report()
```

结束 `run_tests()`。

`compile_model` 自动运行基线健全性/QC：

- 模型有效性
- 恰好一个根零件
- 网格资源就绪
- 浮空断开零件组
- 零件内断开几何岛
- 当前姿态真实 3D 重叠

`run_tests()` 用于提示相关的精确断言：`expect_gap(...)`、`expect_overlap(...)`、`expect_contact(...)`、`expect_within(...)` 等。

姿态相关检查保持精简；仅在静息姿态精确检查仍无法消除机制歧义时，再加关节姿态断言。

## 高信号测试习惯

- 安装路径、保留插入或间隙重要时，优先精确零件/元素关系检查，而非宽泛启发式。
- 零件多视觉区域时，对关键安装用精确接触/支撑检查，而非整件近似。
- 几何表示稳定前，推迟脆弱数值阈值与精确 `elem_*` 检查。
- `run_tests()` 以精确 `elem_*` 引用视觉后，该名即契约；保留或同次编辑更新所有依赖检查。
- 默认勿加宽泛 lower/upper 姿态扫描；提示关键机制需证明时用一两个决定性姿态。
- 支撑、浮空或重叠语义不明时，先探针，再将不变量写入 `run_tests()`。

## 参数约定

以下规则适用于大部分 API；若某辅助不同，以其签名为准。

- `link_*`、`part`、`positive_link`、`negative_link`、`inner_link`、`outer_link` 接受 `Part` 或零件名字符串。API 混用 `link` 与 `part`，均指已创作零件。
- `elem_*`、`positive_elem`、`negative_elem`、`inner_elem`、`outer_elem` 接受命名 `Visual` 或所属零件的视觉名字符串。
- `axis` 须为 `"x"`、`"y"` 或 `"z"`，指正世界轴方向。
- `axes` 接受 `"x"`、`"y"`、`"z"`、`"xy"` 等或序列如 `("x", "y")`。
- 距离与容差为米。
- `name` 覆盖最终报告中的检查名。
- `max_pose_samples` 控制采样关节姿态数量。
- `contact_tol=None`、`overlap_tol=None`、`overlap_volume_tol=None` 表示「使用 SDK 默认」。

## 报告辅助

### `report() -> TestReport`

返回迄今记录检查的最终报告。

### `check(name: str, ok: bool, details: str = "") -> bool`

记录自定义阻塞检查。

### `fail(name: str, details: str) -> bool`

`check(name, False, details)` 的便捷包装。

### `warn(text: str) -> None`

向报告追加非阻塞警告。

## 豁免

### `allow_overlap(link_a, link_b, *, reason, elem_a=None, elem_b=None) -> None`

记录有意真实 3D 互穿，使重叠检查在该情况下不失败。勿仅因一件在另一件足迹/空腔内而使用。

- `reason`：必填理由。
- `elem_a`、`elem_b`：可选元素级范围；省略则适用于整对零件。

### 可接受重叠模式

用于局部、大多隐藏且机制可解释的小重叠。整件宽泛豁免是错误默认。

- **嵌套代理配合**：滑块、桅杆、抽屉在简化实心套筒内表示为移动。配合 `expect_within(...)` 与保留插入轴上的 `expect_overlap(...)`。
- **捕获销/轴**：铰链销、旋钮柄、轴有意嵌在桶/衬套/轮毂代理内。配合 `expect_contact(...)`、`expect_gap(..., max_penetration=...)` 或决定性姿态检查。
- **就座装饰/顺应压缩**：面框、帽、塞、密封或缓冲需微小局部嵌入以读作就座/压缩。配合 `expect_contact(...)` 或就座界面的 `expect_gap(..., max_penetration=...)`。

### `allow_isolated_part(part, *, reason) -> None`

记录命名零件在编译器浮空/断开零件组检查中允许保持孤立。

多零件有意浮空组合时，对该组每个已创作零件分别允许。

### `allow_coplanar_surfaces(link_a, link_b, *, reason, elem_a=None, elem_b=None) -> None`

为 `warn_if_coplanar_surfaces(...)` 记录有意共面关系。

### 嵌套滑块与伸缩配合

编译器重叠检查将真实 3D 互穿视为失败，除非显式允许。

嵌套移动配合决策规则：

- 外件为真实空心或留隙套筒：用 `expect_within(...)`、`expect_gap(...)` 与保留插入检查证明；**不要** `allow_overlap(...)`
- 外件为简化实心代理且仍表示一件在另一件内滑动：可对代表套筒/配合的**具名元素**使用范围化 `allow_overlap(...)`

伸缩杆/导轨/套筒常用精确模式：

- 非运动轴 `expect_within(...)` 证明对中
- 静息与最大伸出时 `expect_overlap(..., axes="<滑动轴>")` 证明保留插入
- `with ctx.pose(...)` 证明子件沿预期方向运动

`expect_overlap(...)` 是投影重叠检查，**非**碰撞豁免；证明轴上保留长度，不抑制编译器重叠检查。

```python
ctx.allow_overlap(
    outer_stage,
    inner_stage,
    elem_a="outer_sleeve",
    elem_b="inner_member",
    reason="The inner member is intentionally represented as sliding inside the sleeve proxy.",
)

ctx.expect_within(
    inner_stage,
    outer_stage,
    axes="xy",
    inner_elem="inner_member",
    outer_elem="outer_sleeve",
    margin=0.002,
    name="inner member stays centered in the sleeve",
)
ctx.expect_overlap(
    inner_stage,
    outer_stage,
    axes="z",
    elem_a="inner_member",
    elem_b="outer_sleeve",
    min_overlap=0.080,
    name="collapsed stage remains inserted in the sleeve",
)

rest_pos = ctx.part_world_position(inner_stage)
with ctx.pose({slide_joint: slide_upper}):
    ctx.expect_within(
        inner_stage,
        outer_stage,
        axes="xy",
        inner_elem="inner_member",
        outer_elem="outer_sleeve",
        margin=0.002,
        name="extended stage stays centered in the sleeve",
    )
    ctx.expect_overlap(
        inner_stage,
        outer_stage,
        axes="z",
        elem_a="inner_member",
        elem_b="outer_sleeve",
        min_overlap=0.030,
        name="extended stage retains insertion in the sleeve",
    )
    extended_pos = ctx.part_world_position(inner_stage)

ctx.check(
    "stage extends upward",
    rest_pos is not None and extended_pos is not None and extended_pos[2] > rest_pos[2] + 0.02,
    details=f"rest={rest_pos}, extended={extended_pos}",
)
```

错误默认是宽泛整件豁免（如 `ctx.allow_overlap("cabinet", "drawer", ...)`），而仅一个命名套筒/配合界面有意重叠；有稳定名称时务必限定到具体元素。

## 姿态与世界空间查询

### `pose(joint_positions: dict[object, float | Origin] | None = None, **kwargs: float | Origin) -> Iterator[None]`

临时姿态覆盖上下文。

```python
with ctx.pose({hinge: 0.5}):
    ...

with ctx.pose(hinge=0.5):
    ...
```

- `joint_positions`：关节对象或名 → 位置；标量 `float`，浮动 `Origin(...)`。
- `**kwargs`：关节名简写。
- 旋转/连续：弧度；移动：米；浮动：`Origin.xyz` 米、`Origin.rpy` 弧度。
- 正标量遵循关节约定：旋转右手定则，移动沿 `+axis`；浮动不用 `axis`。
- mimic 从动件由源关节自动派生；对源关节设姿态，非从动件。
- 退出时恢复先前姿态。

调试反向铰链或滑块时，用 `part_world_position(...)`、`part_world_aabb(...)` 或 `expect_*` 比较闭合与打开/伸出姿态；默认应确认上限位沿预期向外/向上，而非仅无重叠。

### `part_world_position(part) -> tuple[float, float, float] | None`

当前姿态下零件原点世界坐标。

### `link_world_position(link) -> tuple[float, float, float] | None`

`part_world_position(...)` 的别名。

### `part_world_aabb(part) -> tuple[Vec3, Vec3] | None`

当前姿态下整件世界 AABB。

### `link_world_aabb(link) -> tuple[Vec3, Vec3] | None`

`part_world_aabb(...)` 的别名。

### `part_element_world_aabb(part, *, elem) -> tuple[Vec3, Vec3] | None`

零件上单个命名视觉元素的世界 AABB。

## 结构检查

本节方法记录命名检查，通过返回 `True`，失败返回 `False`。

### `fail_if_articulation_origin_far_from_geometry(*, tol=0.015, reason=None, name=None) -> bool`

关节原点距附近几何超过 `tol` 时失败。

- `tol`：非负绝对容差，米。
- `reason`：放宽容差时作为警告记录的可选说明。

可用，但非推荐默认栈（容差为绝对而非尺度相关）。

### `warn_if_articulation_origin_far_from_geometry(*, tol=0.015, reason=None, name=None) -> bool`

同上，警告级。

### `warn_if_coplanar_surfaces(*, max_pose_samples=32, plane_tol=0.001, min_overlap=0.02, min_overlap_ratio=0.35, ignore_adjacent=True, ignore_fixed=True, name=None) -> bool`

可疑共面或近共面表面的警告启发式。

- `plane_tol`：最大平面分离。
- `min_overlap`：两平面轴最小重叠距离。
- `min_overlap_ratio`：`[0,1]` 最小重叠面积比。
- `ignore_adjacent`、`ignore_fixed`：与采样重叠检查同义。

仅当该启发式回答真实不确定性时使用。

## 精确断言

本节方法记录命名检查，通过返回 `True`，失败返回 `False`。

### `expect_origin_distance(link_a, link_b, *, axes="xy", min_dist=0.0, max_dist=None, name=None) -> bool`

沿请求轴检查零件原点距离。

### `expect_origin_gap(positive_link, negative_link, *, axis, min_gap=0.0, max_gap=None, name=None) -> bool`

沿正世界轴检查原点间有符号间隙。

### `expect_contact(link_a, link_b, *, contact_tol=1e-6, elem_a=None, elem_b=None, name=None) -> bool`

两零件或两命名元素间精确最小距离。

### `expect_gap(positive_link, negative_link, *, axis, min_gap=None, max_gap=None, max_penetration=None, positive_elem=None, negative_elem=None, elem_a=None, elem_b=None, name=None) -> bool`

沿正世界轴的有符号精确几何间隙。

- 测量：`positive.min[axis] - negative.max[axis]`。
- `min_gap`：下界；省略时由 `max_penetration` 推导。
- `max_gap`：可选上界。
- `max_penetration`：允许穿透深度的便捷下界 `-max_penetration`。
- `positive_elem`、`negative_elem`：可选元素范围；`elem_a`/`elem_b` 为兼容别名。

主要精确间隙与就座辅助。

### `expect_overlap(link_a, link_b, *, axes="xy", min_overlap=0.0, elem_a=None, elem_b=None, name=None) -> bool`

精确投影重叠（足迹/投影，非碰撞/接触）。

### `expect_within(inner_link, outer_link, *, axes="xy", margin=0.0, inner_elem=None, outer_elem=None, elem_a=None, elem_b=None, name=None) -> bool`

内件或命名元素在外件请求轴上保持在内。

- `margin`：允许超出外界的松弛。

嵌套滑块：非运动轴 `expect_within(...)`，滑动轴配合 `expect_overlap(...)` 或 `expect_gap(...)`。勿单独 `expect_within(...)` 作为全行程仍插入的证明。

## 浮动姿态说明

- `ctx.pose(...)` 混用标量 `float` 与 `FLOATING` 的 `Origin(...)`；类型错误会 `ValidationError`。
- 浮动关节：`Origin.xyz` 为关节系相对平移，`Origin.rpy` 为同系相对旋转；零姿态为 `Origin()`。
- mimic 从动件不能在 `ctx.pose(...)` 中直接覆盖；驱动源关节。
- `sample_poses(...)` 与姿态采样 QC 默认仅对浮动关节用 `Origin()`；要测更多浮动姿态，设 `joint.meta["qc_samples"] = [Origin(...), ...]`。
