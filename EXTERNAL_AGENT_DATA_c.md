# 数据创作指南（外部智能体）

你是**在本仓库内**为 Articraft 创作数据的外部智能体 harness（例如 Codex、Claude Code）。下文是**唯一支持**的工作流。

**禁止：**

- 手动创建 `data/records/<id>` 目录
- 伪造记录元数据或 Articraft 内部 harness 轨迹
- 绕过下列 CLI 命令

---

## 请先阅读

在创建或编辑记录之前，请阅读核心创作要求（英文原文路径，内容属质量契约）：

```text
agent/prompts/sections/designer_common.md
agent/prompts/sections/link_naming.md
```

这些文件定义**不可妥协**的质量基线，包括但不限于：

- 逼真几何与面向用户的主要关节化机构
- 无悬空部件、无意外重叠
- 与 prompt 声明一致的 `run_tests()` 检查
- 简洁、语义化的 link 命名

**质量与真实感非常重要。** 应使用 SDK 与仓库文档中一切合适的建模工具，使几何读起来像真实物体而非占位方块。例如：中空结构应建为中空；弯曲、锥度、倒角、穿孔、软质、透明或复合形态应使用合适的 primitive、CadQuery 几何、loft、sweep、布尔、网格辅助、颜色与材质——当真实物体需要这些细节时，不要用粗糙盒体凑合。

随后在创作过程中使用 SDK 文档与示例：

```text
sdk/_docs/
sdk/_examples/
```

也可搜索仓库内已有示例。**优先参考高质量 5 星记录**；低分记录仅作反面教材：

```bash
uv run articraft external examples --query "washing machine"
uv run articraft external examples --category-slug washing_machine --rating-min 5
```

### 推荐高质量循环

1. 阅读用户 prompt，明确真实物体、尺度、可见材质、主要机构与操控件。
2. 写几何前阅读相关 SDK 文档/示例。
3. 用逼真、相连的结构与明确的主要关节机构搭建对象。
4. 在 `run_tests()` 中加入与 prompt 视觉/机械声明一致的检查。
5. 运行 `external check`，根据失败/警告修复模型，重复直至通过。

---

## 1. 初始化仓库

创作前执行：

```bash
uv sync --group dev
uv run articraft init
```

---

## 2. 创建记录

通过 external CLI 创建，并**显式标识**你的智能体类型：

```bash
uv run articraft external init --agent codex "washing machine"
uv run articraft external init --agent claude-code "washing machine"
```

| `--agent` | 默认提供商元数据 |
| --- | --- |
| `codex` | `openai` |
| `claude-code` | `anthropic` |

**强烈建议**在 `external init` 时注册你实际使用的模型与思考/推理级别（若已知）：

```bash
uv run articraft external init --agent claude-code --model-id claude-sonnet-4-6 --thinking-level high "washing machine"
uv run articraft external init --agent codex --model-id gpt-5.4 --thinking-level high "washing machine"
```

命令会打印 `record_id` 与 `record_dir`。**仅编辑**该次生成的记录，除非用户明确要求 broader 仓库变更。

**允许的外部智能体 ID：**

- `codex`
- `claude-code`

---

## 3. 编辑已有记录

用户要求修改已有 Articraft 资产时，请 **fork**，不要手动复制记录文件夹：

```bash
uv run articraft external fork --agent codex data/records/<record_id> "make the handle longer"
uv run articraft external fork --agent claude-code data/records/<record_id> "make the handle longer"
```

`fork` 会创建子记录并打印当前活动的 `model=` 与 `prompt=` 路径。**只编辑 CLI 打印的 `model=` 路径**。对外部智能体，**不支持**就地修改已有记录。

Fork 默认继承父集合；数据集 fork 获得由父 dataset ID 派生的新 ID；父 traces、费用、provenance 历史、旧模型快照与 inputs **不会**复制。UI 可通过 lineage 查看父级历史。

---

## 4. 创作对象

编辑：

```text
CLI 打印的 active model= 路径
```

v3 记录通常为：

```text
data/records/<record_id>/revisions/<revision_id>/model.py
```

用户 prompt 位于：

```text
CLI 打印的 active prompt= 路径
```

参考：

```text
sdk/_docs/
sdk/_examples/
```

对象须为高质量关节化资产：有意义部件、正确关节、可见机械结构、稳定几何、逼真材质/颜色、语义 link 名，以及 `run_tests()` 中的 prompt 专项测试。

---

## 5. 迭代

开发过程中运行 external check（带 finalize 前使用的严格校验门）：

```bash
uv run articraft external check data/records/<record_id>
```

重复「编辑 → check」直至通过。

---

## 6. 定稿（Finalize）

### 仅工作台对象

```bash
uv run articraft external finalize data/records/<record_id>
```

### 贡献到数据集

先查看现有类别：

```bash
uv run articraft external categories
```

再归入最合适类别：

```bash
uv run articraft external finalize data/records/<record_id> --category-slug washing_machine
```

**仅当用户明确要求加入数据集时**使用 `--category-slug`。

---

## 规则摘要

### 你必须

| 要求 | 说明 |
| --- | --- |
| 新记录 | 使用 `articraft external init` |
| 改已有记录 | 使用 `articraft external fork` |
| 元数据 | 保持 `creator.mode=external_agent` |
| 智能体 ID | 保持 `creator.agent=codex` 或 `claude-code` |
| 轨迹 | 保持 `creator.trace_available=false` |
| 校验 | 使用 `articraft external check` 与 `finalize` |
| 提交 | 工作台专用记录**不要** commit |
| 编辑范围 | 仅编辑 CLI 打印的活动 revision `model.py` |

### 你不得

- 手动创建记录目录
- 手动复制父记录文件夹做「编辑」
- 声称拥有内部 Articraft harness traces
- 写入 `traces/` 下文件
- 创作一个对象时编辑无关记录
- 除非用户要求，否则 promote 到数据集

---

## 故障排查

| 问题 | 处理 |
| --- | --- |
| `external check` 几何/重叠失败 | 读 SDK 文档，缩小 scope，修正支撑关系与关节轴 |
| 类别 slug 不存在 | `external categories` 或请用户确认新类别是否符合 [CATEGORY_SELECTION_REQUIREMENTS_c.md](data/CATEGORY_SELECTION_REQUIREMENTS_c.md) |
| 误编辑父记录路径 | 仅改 CLI 打印的子记录 `model=` |

---

## 相关文档

- [编辑已有记录](docs/record_editing_c.md)
- [贡献指南](CONTRIBUTING_c.md)
- [类别提示指南](data/CATEGORY_PROMPT_GUIDE_c.md)
