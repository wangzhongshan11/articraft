# CLAUDE_c.md

本文件为 [Claude Code](https://claude.ai/code) 在处理本仓库代码时提供指引。人类开发者也可与 [AGENTS_c.md](AGENTS_c.md) 对照使用。

---

## 本项目是什么

Articraft 是一个**智能体系统**：从文本提示与参考图像生成关节化 3D 对象。包含：

- 自定义关节对象 **SDK**
- 带工具调用的**多轮生成 harness**
- OpenAI、Gemini、Anthropic、OpenRouter **提供商适配器**
- 规范本地 **storage** / 数据集工具
- 基于 Three.js 的 **Web 查看器**

`sdk/_docs/` 下的 SDK 文档属于**智能体创作契约**的一部分。须与预期智能体行为及基线 compile/工具策略一致；**不要**在其中记录应由 harness 自动拥有（自动执行）的工作流。

若用户要求 Claude Code **生成 Articraft 数据**，遵循 [`EXTERNAL_AGENT_DATA_c.md`](EXTERNAL_AGENT_DATA_c.md)，使用 `uv run articraft external ...`；**不要**手动创建记录或使用替代流程。

---

## 常用命令

产品工作流：`uv run articraft ...`。`just` **有意**限于 setup、检查与查看器启动。

### 环境与质量门

```bash
uv sync --group dev
uv build
uv run articraft init
uv run articraft status
uv run --group dev pytest -q
uv run --group dev pytest tests/storage/test_repo.py -q
uv run --group dev pytest tests/sdk/test_imports.py::test_name -q

just setup
just format
just lint
just smoke-tests
just test-all

uv run articraft data check
uv run articraft env bootstrap
uv run articraft hooks check
uv run articraft hooks install
```

### 生成与记录工作流

```bash
uv run articraft generate "prompt text"
uv run articraft generate --model gemini-3-flash-preview --image reference.png "prompt text"
uv run articraft draft "prompt text"
uv run articraft draft --image reference.png "prompt text"
uv run articraft rerun data/records/<id>
uv run articraft compile data/records/<id>
uv run articraft compile data/records/<id> --target visual
uv run articraft compile-all
uv run articraft compile-all --target full
uv run articraft compile-all --target full --strict
uv run articraft view data/records/<id>
```

### 数据集工作流

```bash
uv run articraft dataset run "prompt text" --category-slug <slug>
uv run articraft dataset batch-new <batch-id>
uv run articraft dataset batch data/batch_specs/<batch-id>.csv --row-concurrency 8 --subprocess-concurrency auto
uv run articraft dataset batch data/batch_specs/<batch-id>.csv --row-concurrency 8 --subprocess-concurrency auto --resume
uv run articraft dataset batch data/batch_specs/<batch-id>.csv --resume --resume-policy failed_only
uv run articraft dataset validate
uv run articraft dataset manifest
uv run articraft dataset category upsert <slug> --title "Display Title"
uv run articraft dataset record delete <record-id>
uv run articraft workbench status
uv run articraft workbench search-index
```

### 查看器 / 前端

```bash
uv run articraft compile-all
just viewer
just viewer-dev
uv run uvicorn viewer.api.app:app --reload --host 127.0.0.1 --port 8876
npm --prefix viewer/web run dev
npm --prefix viewer/web run build
npm --prefix viewer/web run lint
npm --prefix viewer/web run typecheck
```

---

## 架构

### 包布局

| 路径 | 说明 |
| --- | --- |
| `agent/` | `runner.py` 兼容入口；`single_run.py` / `harness.py` 多轮 LLM；`compiler.py` 执行 `model.py` 并导出 URDF/网格；`providers/`；`tools/`；`prompts/`；`tui/` |
| `agent/batch_runner.py` | CSV 批编排：校验、预分配 ID、并发、resume、`data/cache/runs/` |
| `sdk/` | `sdk/v0/` 公开面；`_core` 几何/导出；`_docs` / `_examples` 进入智能体上下文 |
| `storage/` | 磁盘规范层：记录/类别/数据集/批规格/校验/清单/搜索索引 |
| `viewer/` | `viewer/api` FastAPI；`viewer/web` React + TS + Tailwind + Three.js + shadcn/ui |
| `cli/` | 顶层 `articraft` 命令 |
| `tests/` | pytest 镜像包结构 |

### 数据流

1. 提示/参考图 → `generate`、`dataset run` 或批 CSV 行。
2. Harness 构建提供商请求，多轮工具循环，写出 `model.py`。
3. `compiler.py` 执行 `model.py`，导出 URDF/网格。
4. 持久化到 `data/records/<record_id>/`（`record.json`、`revisions/`、`collections/`）。
5. 可再生物料 → `data/cache/record_materialization/<record_id>/`。
6. `viewer/api` 提供数据；`viewer/web` 渲染与管理。

### 存储布局

- `data/records/<record_id>/` — 规范记录
- `data/categories/` — 类别元数据
- `data/supercategories.json` — 超类
- `data/batch_specs/` — 批 CSV
- `data/cache/manifests/` — 派生清单
- `data/cache/record_materialization/<record_id>/` — URDF、编译报告、查看器资产
- `data/cache/runs/<run_id>/` — 批运行、分配、失败、resume
- `data/cache/search/` — 搜索索引

---

## 数据集批 CSV 模式

批规格位于 `data/batch_specs/`；文件名 stem = `batch_spec_id`。

**必需列：** `category_slug`、`prompt`、`provider`、`model_id`、`thinking_level`、`max_turns`

**推荐/可选：** `row_id`、`category_title`（新类别）、`max_cost_usd`、`label`、`sdk_package`（默认 `sdk`）

**校验：**

- `provider` ∈ `openai` | `gemini` | `anthropic` | `openrouter`
- `model_id` 与提供商推断一致（若可推断）
- `thinking_level` ∈ `low` | `med` | `high`
- `max_turns` 为正整数
- v1 **不支持** `image_path`
- 新 spec 建议 per-row 费用留空、`max_turns=100`

**Resume：** 同一 `batch_spec_id`、稳定 `row_id`、复用 `data/cache/runs/<run_id>/allocations.json`；策略 `failed_or_pending` | `failed_only` | `all`；默认拒绝行 spec 变更，除非 `--allow-resume-spec-mismatch`。

---

## 编译与查看器指引

| 场景 | 命令 |
| --- | --- |
| 浏览前快速可视化 | `uv run articraft compile-all` |
| 批量需要含碰撞 URDF | `compile-all --target full` |
| 重度几何失败即停 | 加 `--strict` |
| 单记录完整重编译 | `compile data/records/<id>`；仅查看器加 `--target visual` |
| 生产式本地查看 | `just viewer` → `127.0.0.1:8876` |
| 热重载开发 | `just viewer-dev`（Vite `:5173` 代理 API `:8876`） |

---

## 代码风格

- **Python：** 3.11+；本地 pin 3.12；排除 3.13；4 空格、`from __future__ import annotations`、显式类型、最小导入。
- **Ruff：** `pyproject.toml`，行宽 100，`py311`，`E`/`F`/`I`，忽略 `E501`；`just format` / `just lint`。
- **TypeScript/React：** 严格 TS、ESLint、Tailwind v4、shadcn/ui、`@/` 别名。
- 先遵循本地模式再抽象；变更范围保持在与任务相关的表面。

---

## 钩子与提交安全

`just setup` 安装 pre-commit/pre-push 与托管 post-commit。

**Pre-commit：** 敏感路径、密钥扫描、`data/` 格式、Ruff、前端 lint/typecheck。

**Pre-push：** 冒烟测试。

**拦截路径示例：** `.env`、`data/cache/`、`data/local/`、仅工作台记录、生成 URDF、生成资产目录。`data/` 豁免末尾换行规则。

---

## 环境

`.env` 中配置提供商密钥（见 `AGENTS_c.md`）。可选 `ARTICRAFT_MAX_COST_USD` 及提供商特定传输/缓存/重试设置。

`articraft generate` 默认 `gpt-5.4`、`--thinking-level high`。歧义模型名请显式 `--provider`。

---

## 论文数据集计数

编辑论文时区分原始生成记录与最终策展集。最终集通常仅 4–5 星；1–3 星为负样本/审计。除非重新统计并更新论文，可用「超过 10K」表述最终策展规模。
