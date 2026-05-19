<modeling>
<!-- SDK 建模与测试基线：几何创作与 TestContext 使用约定 -->

## GEOMETRY（几何）

- 保持 `build_object_model()` 与 `run_tests()` 为**顶层入口点（top-level entry points）**。
- 从 `sdk` **直接导入**公开创作 API。
- **不要**根据 docs 主题名猜测 Python 子模块。例如：使用 `from sdk import place_on_face`，**而非** `from sdk.placement import place_on_face`。
- 仅当 primitives **能可信地表示可见形态**时才使用；**不要**用封顶的 primitive 实心体替代：可见中空体、切开孔洞、内嵌腔体、曲面壳体、环、格栅或分层制造面板。
- 对需要更低层形状控制的**可见几何**，优先使用 **CadQuery**：中空壳体、开口圆柱/管、贯穿开孔、布尔切割面板、连续曲面、loft、sweep、凹槽、翻边/唇缘、rim，以及逼真的家电或机器外壳等。
- **自由混用** primitives 与 CadQuery。良好模型常对隐藏/简单结构用 primitives，对 primitives 会显得像占位符的**可见部分**用 CadQuery。
- 匹配物体的**可见构造逻辑**。若某面应读起来像**一块连续制造的面**，应保留为带开孔/切口的连通面，而非用分离漂浮的成员重建。仅当可见形态**确实应读起来像离散成员**时，才采用分件构造。
- 编写 mesh 支撑的视觉效果时，使用托管逻辑名，例如 `mesh_from_geometry(..., "door_panel")` 或 `mesh_from_cadquery(..., "door_panel")`；**不要**在推理中涉及文件系统路径。
- **仅创作视觉几何**；**不要**在 `sdk` 中创作碰撞几何（collision geometry）。
- 保持正确的关节原点、轴、限位与关节行为。

## TESTING（测试）

- 使用 `sdk.TestContext`，返回 `ctx.report()`，并让 `compile_model` 负责基线 sanity/QC 流程。
- 优先 `TestContext(object_model)`；**新代码中不要**传入 asset roots。
- 用 `run_tests()` 做 prompt 相关的**精确检查**、针对性姿态检查、以及**显式 allowance**。
- 将 overlap 发现**先视为分类任务**：判断报告中的相交是应通过带作用域的 `ctx.allow_overlap(...)` 覆盖的**有意设计嵌入**，还是需改几何/安装/姿态的**非故意碰撞**。可接受的有意情形包括：代理嵌套（proxy nesting）、捕获销/轴、seated trim、合规压缩等。
- 每个 `ctx.allow_overlap(...)` 至少配对**一项精确证明检查**，例如 `expect_within(...)`、`expect_overlap(...)`、`expect_gap(..., max_penetration=...)`、`expect_contact(...)`，或决定性的姿态检查。
</modeling>
