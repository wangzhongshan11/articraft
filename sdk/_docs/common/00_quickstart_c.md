# SDK 快速入门

## 用途

用本页启动新的 Articraft SDK 脚本。它定义必需的脚本契约、创作工作区规则，以及一个最小端到端示例。
详细 API 见下方挂载的 `docs/sdk/references/...` 文件列表。

## 虚拟工作区

你正在编辑一个**虚拟创作工作区**。

- `model.py` 是唯一可写文件。
- `docs/sdk/references/quickstart.md` 是本始终加载的入口。
- `docs/` 下一切内容为只读 SDK 指引。
- 在 `model.py` 中从 `sdk` 导入。
- 仅在需要时用 `read_file(path=...)` 加载精确参考文本。

## 导入契约

创作辅助函数以顶层公开导入形式从 `sdk` 暴露。
挂载文档按主题分组便于阅读；**文件名不暗示**存在对应的 Python 子模块。

```python
# 正确
from sdk import ArticulatedObject, MotionLimits, place_on_face

# 错误
from sdk.placement import place_on_face
from sdk.core_types import MotionLimits
```

## 挂载参考布局

`docs/sdk/references/` 中始终可用：

- `quickstart.md`：脚本契约、工作区规则、最小示例、工作流及完整参考索引。
- `errors.md`：常见编译与创作失败及解读方式。
- `core-types.md`：几何、材质、关节与测试相关核心类型，以及可选惯性辅助。
- `articulated-object.md`：对象、零件与关节创作辅助及查找模式。
- `assets.md`：独立脚本与测试的显式资源根辅助。
- `placement.md`：安装、偏移、包裹与对齐的放置辅助。
- `probe-tooling.md`：`probe_model` 辅助目录与检查工作流。
- `testing.md`：`TestContext`、`expect_*` 断言与测试创作模式。
- `cadquery/overview.md`：何时及为何在 Articraft 中使用 CadQuery 风格几何。
- `cadquery/primer.md`：CadQuery 心智模型与核心造型工作流。
- `cadquery/workplane.md`：基于工作平面的建模模式与常见操作。
- `cadquery/sketch.md`：草图驱动 2D 轮廓与轮廓构造工具。
- `cadquery/assembly.md`：CadQuery 装配辅助与组合模式。
- `cadquery/gears.md`：内嵌齿轮生成器及保留的 `Workplane.gear()` 插件工作流。
- `cadquery/free-functions.md`：自由函数几何辅助与实用构造器。
- `cadquery/api-ref.md`：精简 CadQuery API 参考与签名。

附加几何参考：

- `geometry/mesh-geometry.md`：网格生成流程、托管网格及基于网格的低层几何辅助。
- `geometry/panels-and-grilles.md`：穿孔板、开槽板及完整通风格栅。
- `geometry/brackets-and-mounts.md`：叉耳、叉架及轭式支撑件。
- `geometry/fans-and-rotors.md`：轴流风扇转子与蜗壳叶轮。
- `geometry/knobs-and-controls.md`：旋钮、表盘帽、握纹细节与轴孔。
- `geometry/wires.md`：线与路径构造辅助。
- `geometry/section-lofts.md`：截面放样、修复与截面驱动几何。
- `geometry/bezels-and-frames.md`：面框、框开口、凹腔与装饰边条。
- `geometry/wheels-and-tires.md`：轮辋结构、轮胎胎体、胎面与胎侧。
- `geometry/hinges.md`：外露桶形与钢琴铰链辅助。

若提示明确命名语义零件族（旋钮、面框、车轮、轮胎、通风格栅、支架、铰链等），在回退到低层网格页之前，先阅读对应的几何专题页。

按需阅读精确文档；**不要**凭记忆猜测辅助函数名或签名。

## 脚本契约

每个生成脚本应定义：

- `build_object_model() -> ArticulatedObject`
- `run_tests() -> TestReport`
- `object_model = build_object_model()`

`compile_model` 编译 `object_model`，从视觉几何推导精确碰撞，运行测试并导出结果。**不要**直接输出 URDF XML。

`compile_model` 还负责基线健全性/QC：自动检查模型有效性、恰好一个根零件、网格资源、浮空断开零件组、零件内断开几何岛，以及当前姿态下的真实 3D 重叠。

## 推荐导入

```python
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)
```

## 托管网格模式

使用逻辑网格名；Articraft 管理物化后的 OBJ 资源路径。

- 用 `mesh_from_geometry(..., "part_name")` 生成程序化网格。
- 用 `mesh_from_input("mesh_name")` 导入已有 OBJ。
- 使用 `TestContext(object_model)`；不要手动接线资源根。
- 若编写独立本地脚本且需要稳定资源根，阅读 `docs/sdk/references/assets.md`。

## 最小示例

```python
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="example_box_lid")

    base = model.part("base")
    base.visual(
        Box((0.20, 0.20, 0.05)),
        origin=Origin(xyz=(0.0, 0.0, 0.025)),
        name="base_shell",
    )

    lid = model.part("lid")
    lid.visual(
        Box((0.18, 0.18, 0.02)),
        # 盖板零件坐标系位于铰链线上；面板沿 +X 伸出。
        origin=Origin(xyz=(0.09, 0.0, 0.01)),
        name="lid_shell",
    )

    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        # 正 q 应向上打开盖板，而非压入底座。
        # 闭合时盖板沿局部 +X 从铰链伸出，
        # 故选 -Y，使正旋转将自由边抬向 +Z。
        origin=Origin(xyz=(-0.09, 0.0, 0.05)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=1.2),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    lid = object_model.get_part("lid")
    hinge = object_model.get_articulation("base_to_lid")

    with ctx.pose({hinge: 0.0}):
        ctx.expect_gap(lid, base, axis="z", max_gap=0.001, max_penetration=0.0)
        ctx.expect_overlap(lid, base, axes="xy", min_overlap=0.05)

    return ctx.report()


object_model = build_object_model()
```

本例对盖板使用**铰链线零件坐标系**。在 `q=0` 时，子坐标系与盖板左缘处的关节坐标系重合。因闭合盖板沿局部 `+X` 伸出，`axis=(0, -1, 0)` 使正角度向上打开。

## 推荐工作流

1. 用 `model.part(...)` 创建零件。
2. 用 `part.visual(...)` 添加视觉几何。
3. 用 `model.articulation(...)` 添加运动。
4. 在 `run_tests()` 中加入提示相关的 `expect_*` 断言。
5. 仅当机制确实需要时，使用 `allow_overlap(...)` 与 `allow_isolated_part(...)`。

`part.inertial` 为可选；仅当下游仿真或导出消费者需要显式质量属性时再添加。

## 创作习惯

- 显式建模可见开口、空腔与空心体；不要用实心占位封住可见开口。
- 若物体分层或嵌套，用清晰视觉分隔建模各层，勿压成单一实心块。
- 保留主要面与盖板可见构造逻辑；若表面应读作连续一片，保持连通并在其上开洞，而非换成浮岛碎片。
- 隐藏支撑与内部结构可保持简单，只要外观正确。
- 单零件内避免断开视觉岛；若特征应读作安装件，给出真实筋、支架、销、套或壁连接，或拆成独立零件。
- 对已安装子零件，优先使用放置辅助，而非手调 `Origin(...)` 偏移。
- 对壳体、面板、踏板、脚、旋钮、按钮、垫、支架等刚性表面安装，默认用 `place_on_surface(...)`。
- 仅当父体确为盒状且语义参考为特定面时，用 `place_on_face(...)` 或 `place_on_face_uv(...)`。
- 居中子件应齐平而非半嵌入时，用 `proud_for_flush_mount(...)`。
- 使用克制、符合实物的材质与颜色，避免占位默认色。

## 参考路由

- 需要类型或辅助签名：读 `docs/sdk/references/core-types.md`。
- 需要零件/对象构造模式：读 `docs/sdk/references/articulated-object.md`。
- 需要显式资源根控制：读 `docs/sdk/references/assets.md`。
- 需要放置逻辑：读 `docs/sdk/references/placement.md`。
- 需要编译/调试解读：读 `docs/sdk/references/errors.md`。
- 需要探针辅助细节：读 `docs/sdk/references/probe-tooling.md`。
- 需要测试细节：读 `docs/sdk/references/testing.md`。
- 需要低层 CadQuery 几何：读相关 `docs/sdk/references/cadquery/*.md`。
- 需要语义几何族：先读相关 `docs/sdk/references/geometry/*.md` 专题页。
- 需要低层网格、线或放样辅助：读相关 `docs/sdk/references/geometry/*.md`。
