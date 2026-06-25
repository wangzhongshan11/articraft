# 仓库指南

本文面向在本仓库中工作的**编码智能体**（如 Cursor Agent、Claude Code 等），汇总项目结构、常用命令、风格约定与提交安全规则。人类贡献者亦可作速查；细节见 [CONTRIBUTING_c.md](CONTRIBUTING_c.md) 与 [CLAUDE_c.md](CLAUDE_c.md)。

---

## 项目结构与模块组织

| 目录 | 职责 |
| --- | --- |
| `agent/` | 生成运行时、提供商适配、prompt 编译/加载、工具、费用跟踪、TUI、批编排 |
| `storage/` | 规范 `data/` 布局、记录/类别/数据集、批规格、运行缓存、材质化元数据、搜索索引 |
| `sdk/`、`sdk/_core/` | 关节对象 SDK 层 |
| `sdk/_docs/`、`sdk/_examples/` | 面向智能体的创作资产（**创作契约**的一部分） |
| `viewer/api/` | FastAPI |
| `viewer/web/` | React/TypeScript/Three.js 查看器 |
| `cli/` | `articraft` 入口 |
| `tests/` | pytest，镜像主包 |

---

## 构建、测试与开发命令

产品工作流使用 `uv run articraft ...`；本地 setup/检查/查看器快捷方式使用 `just`。运行 `just` 列出全部快捷命令。

| 命令 | 说明 |
| --- | --- |
| `uv sync --group dev` | 安装 Python 与开发依赖 |
| `just setup` | 引导 `.env`、同步依赖、安装 pre-commit/pre-push 与托管 post-commit、有 npm 时装查看器依赖、初始化存储 |
| `uv build` | 在 `dist/` 构建 wheel 与 sdist |
| `uv run articraft init` | 创建规范 `data/` 树与工作台状态 |
| `uv run articraft status` | 数据集与工作台状态 |
| `uv run --group dev pytest -q` | 完整 Python 回归 |
| `just smoke-tests` | 快速 pre-push 套件 |
| `just test-all` | 完整 Python 套件 |
| `just format` | `ruff format .` |
| `just lint` | `ruff check .` |
| `uv run articraft data check` | 校验已检入的 `data/` 格式 |
| `uv run articraft hooks check` | 检查托管 git 钩子 |
| `uv run articraft env bootstrap` | 从 `.env.example` 创建 `.env`（不覆盖已有密钥） |

---

## 生成、数据集与查看器命令

- **外部智能体生成数据**必须遵循 [`EXTERNAL_AGENT_DATA_c.md`](EXTERNAL_AGENT_DATA_c.md)。若用户要求 Codex、Claude Code 等生成 Articraft 数据，使用 `uv run articraft external ...`；**不要**手动创建记录或使用替代流程。

| 命令 | 说明 |
| --- | --- |
| `uv run articraft generate "prompt text"` | 工作台模式生成 |
| `uv run articraft generate --model gemini-3-flash-preview --image reference.png "prompt text"` | 覆盖模型并添加参考图 |
| `uv run articraft draft "prompt text"` | 创建工作台草稿记录（不运行生成） |
| `uv run articraft draft --image reference.png "prompt text"` | 草稿附带参考图 |
| `uv run articraft rerun data/records/<id>` | 用已存配置重新生成 |
| `uv run articraft compile data/records/<id>` | 重新编译到 `data/cache/record_materialization/<id>/` |
| `uv run articraft compile-all` | 批量 visual 材质化（浏览查看器前推荐） |
| `uv run articraft compile-all --target full` | 非严格完整 bulk compile；加 `--strict` 为重度几何校验 |
| `uv run articraft dataset run "prompt text" --category-slug <slug>` | 单条直接进入数据集类别 |
| `uv run articraft dataset batch-new <batch-id>` | 创建 `data/batch_specs/<batch-id>.csv`（v1 表头） |
| `uv run articraft dataset batch data/batch_specs/<batch-id>.csv --row-concurrency 8 --subprocess-concurrency auto` | 运行跟踪批处理 |
| `uv run articraft dataset batch ... --resume` | 恢复该 spec 最近一次运行 |
| `uv run articraft workbench search-index` | 重建查看器搜索索引 |
| `just viewer` | 构建并启动完整查看器流程 |
| `just viewer-dev` | uvicorn + Vite 并行开发 |
| `uv run uvicorn viewer.api.app:app --reload --host 127.0.0.1 --port 8876` | 仅 API |
| `npm --prefix viewer/web run dev\|build\|lint\|typecheck` | 仅前端工作流 |

---

## 编码风格与命名

- **Python：** 3.11+；`.python-version` 本地 pin 3.12；**排除 3.13**。4 空格缩进、`from __future__ import annotations`、显式类型注解、CLI 用小模块级 helper。
- **Ruff：** `line-length = 100`，`py311`，规则 `E`/`F`/`I`，忽略 `E501`。
- **命名：** 函数/模块/变量 `snake_case`；类 `PascalCase`。
- **viewer/web：** 严格 TypeScript、ESLint、Tailwind v4、shadcn/ui、`@/` 别名。

---

## 测试指南

- `pytest`，默认 importlib 模式与 xdist auto/worksteal。
- 测试文件：`tests/<包镜像路径>/test_<feature>.py`；优先原生 pytest 函数与 fixture、`assert`。
- 覆盖重点：快速导入、storage、CLI、viewer API、workbench、SDK、集成冒烟。
- **Prompt 回归：** 优先耐久**行为检查**，避免脆弱格式/行数预算断言；更新 prompt 契约时在同一变更中放宽或删除过时断言。

---

## 数据集批规格（Batch CSV）

- 位置：`data/batch_specs/`；文件名 stem = `batch_spec_id`（resume 用）。
- **必需列：** `category_slug`、`prompt`、`provider`、`model_id`、`thinking_level`、`max_turns`。
- **新类别：** 需要 `category_title`。
- **推荐/可选：** `row_id`、`max_cost_usd`、`label`、`sdk_package`（省略默认 `sdk`）。
- **提供商：** `openai`、`gemini`、`anthropic`、`openrouter`。
- **`thinking_level`：** `low` / `med` / `high`。
- **`max_turns`：** 正整数；新 spec 建议默认 `100`。
- **`row_id`：** 省略则 `row_0001`、`row_0002`…；resume 场景建议显式稳定 ID。
- **v1 不支持 `image_path`。**
- 新批 spec 一般**不要**填 per-row 费用上限，除非明确要求。

---

## 提交与 Pull Request

- 提交主题：简短祈使句，单逻辑变更（例：`Move prompt compiler under agent`）。
- PR：说明受影响面（`agent`、`storage`、`sdk`、`viewer`、`cli`）、列出验证命令；仅 API/查看器行为变化时附截图。

**Pre-commit：** 拦截敏感/本地路径、扫描 staged 密钥、校验 `data/` 格式、Ruff、前端变更时 viewer lint/typecheck。

**Pre-push：** 冒烟测试。

**勿提交：** `.env`、`data/cache/`、`data/local/`、仅工作台记录、生成 URDF、生成资产目录。`data/` 豁免末尾换行规则。

---

## 配置提示

提供商从 `.env` 加载：

- `OPENAI_API_KEYS` 或 `OPENAI_API_KEY`
- `GEMINI_API_KEYS`
- `ANTHROPIC_API_KEYS` 或 `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEYS` 或 `OPENROUTER_API_KEY`

可选：`ARTICRAFT_MAX_COST_USD` 默认单次预算。

`generate` 默认 `gpt-5.4`、`--thinking-level high`。已知模型 ID 可推断提供商；歧义时显式 `--provider`。

---

## 论文数据集计数

区分原始生成记录与最终策展集。论文最终集通常仅含保留的 **4–5 星**对象；1–3 星可能是负样本，不计入最终对象数。除非重新统计并有意更新论文，最终规模表述可用「超过 10K」。

---

## 智能体文档契约

`sdk/_docs/` 属于智能体创作契约。须与预期智能体行为及基线 compile/工具策略一致；**不要**在其中记录应由 harness 自动完成的工作流。
