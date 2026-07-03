# Articraft × CAD Runtime：装配建模机制对照

> 本文仅比较**流程、机制与设计取向**，不涉及生成结果质量。  
> Articraft 根目录：`articraft-main`；CAD Runtime：`assembly-agent-v2/.agents/skills/cad/scripts/_runtime`。

---

## 一、定位

| | **Articraft** | **CAD Runtime** |
|---|---|---|
| **目标产物** | 可仿真/可视化的**关节化装配体**（URDF + mesh） | 可制造的**参数化 BRep 实体**（STEP 为主） |
| **几何内核** | 声明式 mesh（+ 可选 CadQuery） | build123d / OpenCascade 实体建模 |
| **装配语义载体** | `ArticulatedObject`（Part + Articulation） | `Compound` + `*Joint` 基准 + `assembly_joints()` |
| **运行形态** | 独立产品（CLI + 数据集 + Viewer） | Skill 内嵌运行时（外层 orchestrator 调度） |
| **下游** | Viewer 直接消费 URDF | `assembly` skill 再导出 URDF / `joints.json` |

二者共享部分装配运动学语义（CAD Runtime 的 `compute_part_world_transforms` 明确对齐 Articraft BFS 约定），但**源模型、编译链、交付物**根本不同。

---

## 二、Articraft 装配建模全链路

### 2.1 端到端流程

```
Prompt (+ 可选参考图)
  → CLI (generate / dataset run / batch)
  → staging: model.py + prompt.txt + traces/
  → ArticraftAgent 多轮 LLM 循环
  → 工具编辑 model.py → compile_model → 结构化 compile_signals
  → 终止：文本结束 + 最新代码已通过 fresh compile
  → data/records/<id>/revisions/<rev>/ 持久化
  → data/cache/record_materialization/<id>/ URDF + meshes
  → Viewer (FastAPI + Three.js)
```

**关键模块：** `agent/harness.py`（主循环）、`agent/compiler.py`（执行与导出）、`sdk/_core/v0/`（模型类型与 URDF）、`storage/`（记录/版本）、`viewer/api/store_materialization.py`（物化缓存）。

### 2.2 源模型契约

`model.py` 必须导出：

```python
def build_object_model() -> ArticulatedObject: ...
def run_tests() -> TestReport: ...
object_model = build_object_model()
```

- **Part** ↔ URDF `<link>`：刚体，承载 visual（mesh/原语）
- **Articulation** ↔ URDF `<joint>`：父子变换 + 运动自由度（revolute / prismatic / fixed …）
- **单根树**：每 part 最多一个 parent；`root_parts()` 必须唯一
- Agent **不手写 URDF**；碰撞体默认由 visual 自动推导（`exact_collisions`）

虚拟工作区：`model.py` 可写；`docs/sdk/references/*.md` 只读（映射 `sdk/_docs/`）。

### 2.3 Agent 工具与循环

| 工具 | 作用 |
|------|------|
| `read_file` | 读 model.py（可编辑区）与 SDK 文档 |
| `replace` / `write_file` / `apply_patch` | 改 model.py（按 provider 选集） |
| `compile_model` | 触发完整编译/QC，返回 `<compile_signals>` |
| `probe_model` | 子进程隔离执行探测代码（AABB、位姿、几何采样） |
| `find_examples` | 检索 `sdk/_examples/` |

**终止条件**（`TerminateReason.CODE_VALID`）：模型输出纯文本且无 tool call，且 `_latest_code_is_fresh()`——即自上次成功 `compile_model` 后代码未再变更。另有 `MAX_TURNS`、`COST_LIMIT`、`ERROR`。

**编译缓存：** `CompileFeedbackLoop` 按 edit revision 去重；未改代码的重复 `compile_model` 直接返回缓存。

**引导注入：** `GuidanceInjector` 在工具调用后按 AST/契约注入提醒（需 compile、基线 QC、精确几何等）。

### 2.4 编译与 QC 分层

```
runpy 执行 model.py
  → object_model.validate()
  → run_tests()          # Agent 编写的 prompt 级断言
  → 编译器基线 QC        # 单根、孤岛、当前姿态重叠、资产就绪 …
  → exact_collisions     # full target：由 visual 生成碰撞 mesh
  → compile_object_to_urdf_xml()
  → CompileReport → compile_signals 回灌 Agent
```

- **visual target**：跳过物理碰撞，批量 Viewer 用（`compile-all`）
- **full target**：含碰撞与完整校验（`compile` / `--strict`）

QC 哲学：**compile 是传感器，不是优化目标**——不因通过测试而牺牲视觉/机构可信度。

### 2.5 存储与规模化

| 层级 | 路径 | 内容 |
|------|------|------|
| 规范源 | `data/records/<id>/revisions/<rev>/` | model.py、prompt、provenance、trajectory |
| 派生物 | `data/cache/record_materialization/<id>/` | URDF、OBJ/GLB、compile_report.json |
| 批量 | `data/batch_specs/*.csv` + `agent/batch_runner.py` | 行级并发、resume、成本上限 |

集合：`workbench`（实验）与 `dataset`（策展入库）共用同一 harness。

---

## 三、CAD Runtime 装配建模全链路

### 3.1 端到端流程

```
intent-confirmation → (可选) materialize_upstream
  → job.invoke.json
  → cad/invoke → CadAgentHarness
  → brief → implement → refine（三阶段）
  → edit_model：patch model.py + 即时几何编译
  → geometry_report 回灌 → STEP 导出
  → publish_artifacts (COS) → cad_scene_cache.json
  → assembly/export_urdf_from_generator、export_cad_joints（下游）
```

**关键模块：** `scripts/agent/harness.py`、`scripts/agent/agent_compile.py`、`scripts/common/compile_step.py`、`scripts/common/geocomp/`、`scripts/common/assembly_graph.py`、`scripts/common/assembly_kinematics.py`。

**运行环境：** Conda `cad`；`CAD_RUNTIME_ROOT` / `ASSEMBLY_REPO_ROOT`；case 隔离于 `cases/<case-id>/output/`。

### 3.2 双层规格：Brief + Generator

**`cad_brief.md`（Blueprint）**

- `### Parts`：BOM，每 part 一行 `{feature, material, representation}`
- `### Mounts`：parent→child 安装关系、关节名、轴向、角度范围

**`model.py`**

```python
def gen_step(overrides=None) -> Solid | Compound: ...
# 多零件：Compound(label="product", children=[...])
# 关节：RigidJoint / RevoluteJoint / ... + assembly_joints("mount", parent=..., child=..., ...)
```

- 几何在**零件局部坐标系**建造；世界位姿由关节图物化（`apply_assembly_joint_graph_materialize`）
- 参数契约：`PARAMS` + `resolve(PARAMS, overrides)`（`parametric/params.py`）
- API 分层：**S**（semantic_cad）> **G**（Tier-G 几何卡）> **H**（原生 build123d）

虚拟工作区：`model.py` + `cad_brief.md`（brief 阶段可写）+ `docs/cad/*` 映射 `authoring/`。

### 3.3 三阶段 Harness

| 阶段 | 可写 | 工具 |
|------|------|------|
| **brief** | `cad_brief.md` | `apply_patch`, `lookup_api`, `find_examples`, `read_file` |
| **implement** | `model.py` | `edit_model`（brief 只读） |
| **refine** | `model.py` | `edit_model` |

`edit_model` = patch + `gen_step()` + geometry compiler + 可选 STEP 写出；**每改必编**。

**终止（finish_gate）：** 通过 QC 的 fresh revision、STEP 已导出、brief 完整、连通性门（单根树）、可选质量分阈值。Agent 路径已退役 `validate_step()`，QC 完全由 geometry compiler 承担。

### 3.4 几何编译器（geocomp）

Pass DAG（短路于 `compile_error`）：

```
CompilePass → HealthPass → MatesPass → IntentPass → OrientationPass → SizePass
```

输出 `geometry_report.json/.md`，嵌入工具结果为 `<geometry_report>`。含 `spatial_digest`（世界 AABB/轴）、`mount_contact`（配合间隙/重叠）等遥测。

**与 brief 对齐：** `brief_digest_inventory_mismatch`、`mount_gap`、`axis_mismatch` 等将场景与 Blueprint 意图对照——**规格在 brief，几何在 model.py，QC 桥接二者**。

### 3.5 导出与下游解耦

| 格式 | 角色 |
|------|------|
| **STEP** | 主交付物 |
| **GLB** | 预览/发布侧车 |
| **URDF** | `common/urdf/emit` 可选；常由 assembly skill 二次导出 |
| **handoff.json** | 路径、校验摘要、主 artifact 类型 |

CAD 拥有 BRep 与源级关节；**assembly skill** 提升为 `joints.json` 与审阅版 URDF，不破坏生成器变换。

---

## 四、机制维度对照

### 4.1 装配抽象

| 维度 | Articraft | CAD Runtime |
|------|-----------|-------------|
| 零件 | `Part`（visual/collision 列表） | `Compound` 子节点 / 单 `Solid` |
| 关节 | `Articulation`（类型、origin、axis、limits、mimic） | `*Joint` 基准 + `assembly_joints()` 挂载表 |
| 层级 | 显式 parent/child 树 | brief Mounts + 运行时 `_assembly_graph` |
| 坐标 | 关节 origin = parent→joint；子系 q=0 重合 | 零件局部建模；BFS 物化世界 `Location` |
| 单位/轴向 | SDK 约定（与 URDF 一致） | mm；+Z 上、+Y 前、+X 右 |

### 4.2 Agent 交互

| 维度 | Articraft | CAD Runtime |
|------|-----------|-------------|
| 可写文件 | 仅 `model.py` | `cad_brief.md`（brief 期）+ `model.py` |
| 编译工具 | `compile_model`（与编辑解耦） | `edit_model`（编辑即编译） |
| 探测 | `probe_model`（独立子进程） | geometry_report 遥测为主；`probe_gate` 连通性 |
| 示例检索 | `find_examples` → `sdk/_examples/` | `find_examples` → showcases（BM25，源自 Articraft 适配） |
| 终止 | 纯文本 + fresh compile | finish_gate 多条件（QC/STEP/brief/连通） |
| Provider | OpenAI / Gemini / Anthropic / OpenRouter | 主要为 OpenAI 配置栈 |

### 4.3 编译与 QC

| 维度 | Articraft | CAD Runtime |
|------|-----------|-------------|
| 执行方式 | `runpy` 加载 Python 对象模型 | 注入 authoring surface 后调 `gen_step()` |
| 主校验 | SDK validate + 双层 test（基线 + `run_tests`） | geocomp Pass DAG + brief 意图对照 |
| 碰撞 | 由 visual 自动 exact collision | BRep 实体健康（`invalid_solid` 等） |
| 缓存 | 按 edit revision 缓存 compile | 按 revision fresh QC |
| 维护者路径 | 同一 `compiler.py` | 独立 `compile.py` / `validate_step`（维护者 CLI） |

### 4.4 持久化与编排

| 维度 | Articraft | CAD Runtime |
|------|-----------|-------------|
| 身份 | `record_id` + `rev_NNNNNN` | `case_id` 单次作业 |
| 规范存储 | `data/records/` 长期策展 | `cases/<id>/output/` 任务沙箱 |
| 批量 | 一等公民 CSV batch + resume | 外层 orchestrator 多 case |
| 发布 | 本地 Viewer + dataset manifest | COS + `cad_scene_cache.json` |
| 溯源 | provenance.json、cost、trajectory | trace.jsonl、run.json、handoff |

---

## 五、优劣对照（机制层面）

### Articraft 优势

1. **装配–仿真一体**：`ArticulatedObject` 即 URDF 源，关节/限位/ mimic 一次建模、直接导出，无二次 skill 提升。
2. **编辑–编译解耦**：可先小步改代码再 `compile_model`；`probe_model` 支持不改代码的轻量几何探针。
3. **QC 分层清晰**：编译器基线（结构健全）与 `run_tests()`（prompt 语义）职责分离，Agent 文档契约完整（`sdk/_docs/`）。
4. **产品化闭环**：记录版本、数据集批量、搜索索引、Viewer 同属一套 `storage` 布局。
5. **多 Provider 原生**：harness codec 适配四家 API，工具形态随 provider 切换（patch vs function edit）。
6. **碰撞自动化**：Agent 不手写 collision，降低视觉–物理不一致风险。

### Articraft 劣势

1. **BRep 能力弱**：mesh/原语/CadQuery 为主，无 STEP 级制造语义与实体布尔拓扑保障。
2. **无独立 Brief 层**：装配意图全在 `model.py`，缺少与几何并行的结构化 BOM/Mount 规格书及 brief–scene 自动对账。
3. **单文件写作**：复杂产品无 cad_brief 式的分阶段规格冻结，长任务更易漂移。
4. **阶段门控较松**：终止仅依赖 fresh compile + 无 tool call，无 STEP 级「主 artifact 必出」硬门。

### CAD Runtime 优势

1. **实体几何权威**：BRep 闭合体、配合面、STEP 交付，适合制造/工程下游。
2. **Brief-driven**：Blueprint（Parts + Mounts）与 `geometry_report` 意图 Pass 形成**规格–实现–验证**三角。
3. **三阶段 Harness**：先冻结 brief 再写几何，降低 implement 期规格漂移。
4. **edit_model 原子性**：改码即全量 `gen_step` + geocomp，反馈即时、状态一致。
5. **参数化一等**：`PARAMS` 契约 + CLI，利于下游调参与非 Agent 复跑。
6. **Skill 分层**：外层编排与内层 runtime 分离，case 隔离利于并行云作业。

### CAD Runtime 劣势

1. **URDF 非主路径**：关节在生成器注册，仿真包需 assembly skill 二次导出，链路更长。
2. **编辑成本固定高**：每次 `edit_model` 全量实体重建 + 多 Pass QC，难做 Articraft 式轻量 probe。
3. **环境重**：Conda + OCC 栈；非 Articraft `uv run` 单命令体验。
4. **无内置数据集/Viewer 产品**：依赖外层 assembly-agent 生态，本地检视需 STEP/GLB 侧车。
5. **Agent QC 单轨**：退役 `validate_step` 后全押 geocomp，维护者与客户化校验路径分裂。

---

## 六、设计取向总结

```
Articraft          「代码即关节化产品模型」→ 编译得 URDF → 仿真/展示/数据集
CAD Runtime        「Brief 定规格 + 代码产 BRep」→ STEP 交付 → 下游再关节化
```

| 选型倾向 | 更合适 |
|----------|--------|
| 机器人仿真、关节数据集、快速可视化迭代 | **Articraft** |
| 可制造实体、工程配合面、参数化调参、云 case 流水线 | **CAD Runtime** |
| 统一关节语义、跨系统复用运动学 | 二者已在 `assembly_kinematics` 对齐 BFS；**几何层仍不可互换** |

**互补关系：** CAD Runtime 的 Tier-G 示例与搜索模式明显借鉴 Articraft `sdk/_examples`；Articraft 的 CadQuery 扩展吸收参数化实体思路，但主路径仍是 mesh-first 关节对象。二者是**同一装配问题域上的两种运行时哲学**——Articraft 优化「关节化数字孪生快速落地」，CAD Runtime 优化「参数实体正确性与规格可追溯」。

---

## 七、关键文件索引

### Articraft

|  Concern | Path |
|----------|------|
| Agent 循环 | `agent/harness.py` |
| 编译导出 | `agent/compiler.py` |
| 工具注册 | `agent/tools/__init__.py` |
| 对象模型 | `sdk/_core/v0/articulated_object.py` |
| URDF | `sdk/_core/v0/_urdf_export.py` |
| 碰撞 | `sdk/_core/v0/exact_collisions.py` |
| 测试契约 | `sdk/_docs/common/80_testing.md` |
| 记录 | `storage/records.py`, `agent/record_persistence.py` |
| 批量 | `agent/batch_runner.py` |

### CAD Runtime

| Concern | Path |
|----------|------|
| Harness | `scripts/agent/harness.py` |
| 阶段/终止 | `scripts/agent/phase_state.py`, `finish_gate.py` |
| 装配图 | `scripts/common/assembly_graph.py` |
| 运动学 | `scripts/common/assembly_kinematics.py` |
| 编译 | `scripts/common/compile_step.py`, `scripts/agent/agent_compile.py` |
| 几何 QC | `scripts/common/geocomp/compiler.py` |
| 作者契约 | `authoring/modeling.md`, `positioning.md`, `compile.md` |
| 外层 Skill | `../SKILL.md`（`assembly-agent-v2/.agents/skills/cad/`） |

---

*文档版本：2026-07-03 · 基于 articraft-main 与 assembly-agent-v2 CAD `_runtime` 源码梳理*
