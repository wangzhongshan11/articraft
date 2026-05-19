# 探针工具（Probe Tooling）

## 用途

`probe_model` 是仅用于检查的短 Python 片段工具，针对当前 `object_model` 运行。用于测量当前模型、观察姿态或关系，再将持久不变量写入 `run_tests()`。

## 调用契约

工具参数：

- `code: str`
- `timeout_ms: int = 600000`
- `include_stdout: bool = False`

执行规则：

- 写普通 Python，**恰好一次**调用 `emit(value)`。
- `value` 须 JSON 可序列化。
- 勿改文件、起子进程或使用网络。

## 预加载名称

- `object_model`
- `ctx`
- `emit(value)`
- `catalog()`

## 查找与姿态辅助

### `pose(mapping: dict[str, float | Origin] | None = None, **kwargs: float | Origin) -> ContextManager`

临时应用关节位置。

- 输入：关节名 → 标量位置或 `FLOATING` 的 `Origin(...)`。
- 旋转/连续：弧度；移动：米。浮动：`Origin.xyz` 米、`Origin.rpy` 弧度。
- 正标量遵循 `axis` 编码的关节约定；浮动不用 `axis`。
- 返回：`with pose(...):` 的上下文管理器。

### `part(name: str) -> object`

返回命名零件。

### `joint(name: str) -> object`

返回命名关节。

### `visual(part_name: str, visual_name: str) -> object`

返回零件上命名视觉。

### `parts() -> list[object]`

返回所有零件。

### `joints() -> list[object]`

返回所有关节。

### `visuals(part_or_name: object) -> list[object]`

返回零件的所有视觉。

- 接受：零件对象、零件名，或应解析所属零件的视觉。

### `name(obj: object) -> str`

返回零件、关节或视觉的可读名。

## 测量辅助

目标类型一般为零件、视觉或兼容查找结果，除非另有说明。

### `aabb(obj: object) -> dict[str, list[float]] | None`

世界系 AABB：

```python
{"min": [x, y, z], "max": [x, y, z]}
```

### `dims(obj: object) -> list[float] | None`

精确投影尺寸 `[dx, dy, dz]`。

### `center(obj: object) -> list[float] | None`

精确投影中心 `[x, y, z]`。

### `position(obj: object) -> list[float] | None`

代表性世界位置。

- 零件：零件世界位置
- 视觉：视觉中心
- 关节：可用时的关节原点

### `projection(obj: object, axis_or_axes: str | Sequence[str]) -> dict[str, object]`

沿一轴或多轴的精确几何投影区间。

### `summary(obj: object) -> dict[str, object]`

紧凑结构化摘要。

- 零件摘要：名、位置、中心、尺寸、AABB、视觉名列表。
- 关节摘要：名、类型、轴、运动限位字段。

## 对与关系报告

供直接 `emit(...)` 使用。

### `pair_report(a, b, elem_a=None, elem_b=None) -> dict[str, object]`

精确成对距离、重叠与投影细节。

### `gap_report(positive, negative, axis, positive_elem=None, negative_elem=None) -> dict[str, object]`

单轴有符号间隙。

- 正：分离；负：穿透。

### `overlap_report(a, b, axes="xy", elem_a=None, elem_b=None) -> dict[str, object]`

单轴或多轴重叠及 `min_overlap`。

### `within_report(inner, outer, axes="xy", inner_elem=None, outer_elem=None) -> dict[str, object]`

每轴包含裕度及总 `within`。

### `contact_report(a, b, elem_a=None, elem_b=None, contact_tol=1e-6) -> dict[str, object]`

接触判定、`min_distance`、碰撞状态。

### `mount_report(child, parent, elem_a=None, elem_b=None) -> dict[str, object]`

安装导向审查：成对、XY 包含、Z 间隙。

### `containment_report(inner, outer, axes="xy") -> dict[str, object]`

`within_report(...)` 的包含导向别名。

### `alignment_report(a, b) -> dict[str, object]`

世界系中心有符号与绝对差。

## 审查辅助

### `sample_poses(max_samples: int = 32, seed: int = 0) -> list[dict[str, float | Origin]]`

关节姿态样本。

### `nearest_neighbors(obj, candidates=None, limit: int = 5) -> list[dict[str, object]]`

相对目标最近的候选零件。

### `find_clearance_risks(limit: int = 10, parts=None) -> list[dict[str, object]]`

可能碰撞/间隙问题。

### `find_floating_parts(limit: int = 10, parts=None) -> list[dict[str, object]]`

最近邻关系暗示可能浮空的零件。

### `geometry_connectivity_report(part_or_name, contact_tol: float = 1e-6) -> dict[str, object]`

零件级连通诊断，比较：

- 网格视觉/碰撞内原始连通分量
- 编译精确碰撞条目数
- 当前 SDK 连通 QC 发现（若有）

当零件内可见浮岛但自动编译警告未触发时使用。

### `layout_report(items, axis: str = "x") -> dict[str, object]`

单轴重复间距审查。

### `grid_report(items, axes="xy") -> dict[str, object]`

近似 2D 网格结构。

### `symmetry_report(items, axis: str = "x") -> dict[str, object]`

近似双侧对称报告。

## 建议

- 探针用于了解当前模型行为。
- 找到不变量后，用对应 `expect_*` 写入 `run_tests()` 以跨修复轮次保持。
- 优先对象优先片段：零件/关节/视觉解析为局部变量再传给报告辅助。
- 编译反馈暗示浮几何、重叠风险或可疑支撑且原因不明时，先探针再改。
- 优先短探针回答一个空间问题，勿大诊断脚本混检。

## 常见探针场景

- 重叠/碰撞分类：`pair_report`、`overlap_report` 或 `mount_report`。
- 看似浮空或弱支撑：`find_floating_parts`、`nearest_neighbors` 或 `mount_report`。
- 配合、包含或定向间隙不明：`within_report` 或 `gap_report`。
- 单零件内可疑断开网格岛：`geometry_connectivity_report`。

## 示例

安装特征审查：

```python
panel = part("panel")
knob = visual("panel", "knob")
emit(mount_report(knob, panel))
```

姿态感知接触：

```python
with pose(lid_hinge=1.0):
    emit(contact_report(part("lid"), part("frame")))
```

报告对的重叠分类：

```python
emit(pair_report(part("spindle_head"), part("table"), elem_a="quill", elem_b="table_disk"))
```

可疑零件浮空/支撑路径：

```python
handle = part("handle")
emit({"floating": find_floating_parts(parts=[handle], limit=1), "neighbors": nearest_neighbors(handle, limit=3)})
```

重复布局：

```python
keys = [visual("keyboard", name) for name in ("key_1", "key_2", "key_3", "key_4")]
emit(layout_report(keys, axis="x"))
```

可疑网格零件断开岛：

```python
report = geometry_connectivity_report("left_frame")
emit(
    {
        "part": report["part"],
        "has_raw_disconnected_components": report["has_raw_disconnected_components"],
        "disconnected_items": report["disconnected_items"],
        "compiled_collision_count": report["compiled_collision_count"],
        "qc_detected_disconnected_islands": report["qc_detected_disconnected_islands"],
        "blind_spot_suspected": report["blind_spot_suspected"],
    }
)
```

## 另见

- `80_testing_c.md`：持久测试 API

## 浮动姿态说明

- `pose(...)` 可混用：标量关节 `float`，`FLOATING` 用 `Origin(...)`。
- `sample_poses(...)` 返回相同混用姿态映射；浮动关节默认仅采样 `Origin()`，除非关节元数据提供 `Origin(...)` 的 `qc_samples`。
- 探针 `summary(joint)` 将浮动关节报告为刚性 6-DOF，`Origin` 姿态值，而非轴驱动标量模型。
