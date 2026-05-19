# 数据集生成指南

Articraft 的数据集批处理由 `data/batch_specs/` 下的 **CSV 规格文件**驱动。CSV **文件名（不含扩展名）** 即为该批次的 `batch_spec_id`。

该命名与 **resume（恢复）** 强相关——请务必理解下列规则后再跑大批量任务。

---

## `batch_spec_id` 与 resume 要点

| 规则 | 说明 |
| --- | --- |
| `batch_spec_id` = CSV 文件名 stem | 例如 `chairs_v1.csv` → `batch_spec_id` 为 `chairs_v1` |
| `--resume` 查找对象 | 同一 `batch_spec_id` 的**最近一次**运行 |
| 重命名 CSV | `chairs_v1.csv` → `chairs_v2.csv` 会被视为**全新批次**，无法自动接续旧 run |
| `row_id` 稳定性 | resume 按 `row_id` 匹配行；计划重试或改 spec 时请使用**稳定、显式**的 `row_id` |
| 默认 resume 策略 | `failed_or_pending`：重跑失败、待处理及中断的 `running` 行 |
| 改 prompt/`max_turns` 后 resume | 默认会因 spec 不兼容被拒；可对失败行使用 `--allow-resume-spec-mismatch` |

---

## 1. 创建批规格文件

使用内置模板创建空 CSV（含当前 v1 表头）：

```bash
uv run articraft dataset batch-new <batch-id>
```

生成路径：`data/batch_specs/<batch-id>.csv`。

**建议：** 新建类别相关批处理前，阅读 [类别提示指南](../data/CATEGORY_PROMPT_GUIDE_c.md) 与 [类别入选要求](../data/CATEGORY_SELECTION_REQUIREMENTS_c.md)。

---

## 2. 填写 CSV

每一行 = 一次数据集生成任务。

| 列名 | 是否必需 | 说明 |
| --- | --- | --- |
| `row_id` | **强烈推荐** | 稳定行标识，resume 依赖此项。省略时默认 `row_0001`、`row_0002`…（顺序敏感，不利于后期改 spec） |
| `category_slug` | 是 | 数据集类别 slug（对应 `data/categories/`） |
| `category_title` | 有时必需 | 当 `category_slug` **尚不存在**时，该行必须提供显示标题 |
| `prompt` | 是 | 生成用自然语言提示（英文 prompt 原文通常保留在 CSV 中） |
| `provider` | 是 | `openai`、`gemini`、`anthropic` 或 `openrouter` |
| `model_id` | 是 | 模型 ID，须与 `provider` 一致（可推断时） |
| `thinking_level` | 是 | `low`、`med` 或 `high` |
| `max_turns` | 是 | 正整数，多轮工具循环上限；新 spec **建议默认 `100`** |
| `max_cost_usd` | 否 | 该行可选美元预算；空白则继承批 CLI 的 `--max-cost-usd` 或环境变量 `ARTICRAFT_MAX_COST_USD` |
| `label` | 否 | 自由形式跟踪标签 |
| `sdk_package` | 否 | SDK 包覆盖，默认 `sdk` |

**v1 限制与校验：**

- **`image_path` 在批 CSV v1 中不支持**（勿添加该列期望生效）
- **重复的 `row_id` 会被拒绝**
- `provider` / `thinking_level` / `max_turns` 非法值会在批启动前校验失败

**可选列备忘：** 若仓库版本支持 `sdk_package`，省略时默认为 `sdk`。

---

## 3. 首次运行

```bash
uv run articraft dataset batch data/batch_specs/<batch-id>.csv --row-concurrency 8 --subprocess-concurrency auto
```

### 常用执行参数

| 参数 | 含义 |
| --- | --- |
| `--row-concurrency` | 同时处于活动状态的最大行数；可为 `auto`、`max` 或整数 |
| `--subprocess-concurrency` | 并发编译 / QC / probe 子进程上限 |
| `--max-cost-usd` | 对 CSV 中 `max_cost_usd` 为空的行应用的默认美元预算 |

**调优提示：**

- API 限流或 OOM 时：降低 `--row-concurrency` 或 `--subprocess-concurrency`。
- 成本敏感：为每行设 `max_cost_usd` 或降低 `max_turns`（可能影响质量）。

---

## 4. 安全地 resume 批次

某行失败后，可用 `--resume` 恢复（**同一 CSV 文件名 / `batch_spec_id`**）：

```bash
uv run articraft dataset batch data/batch_specs/<batch-id>.csv --row-concurrency 8 --subprocess-concurrency auto --resume
```

### `--resume` 会做什么

- 复用同一 `batch_spec_id` 的**最近一次** prior run
- 复用先前的 `dataset_id`、`record_id` **分配**（见 `data/cache/runs/<run_id>/allocations.json`）
- **保留已成功行**的结果
- 默认重跑状态为 `failed`、`pending` 或中断的 `running` 行

### Resume 策略（`--resume-policy`）

```bash
uv run articraft dataset batch data/batch_specs/<batch-id>.csv --resume --resume-policy failed_only
```

| 策略 | 行为 |
| --- | --- |
| `failed_only` | 仅重跑最新状态为 `failed` 的行 |
| `failed_or_pending` | 重跑失败、待处理及中断行（**默认**） |
| `all` | 重跑**每一行**（慎用，会重复成功行的生成成本） |

### 修改失败行的 prompt 或 `max_turns`

默认 resume 会**拒绝**与上次运行不一致的行 spec。若你**有意**为失败行修改参数：

```bash
uv run articraft dataset batch data/batch_specs/<batch-id>.csv --resume --allow-resume-spec-mismatch
```

---

## 5. 输出与状态位置

| 时机 | 路径 |
| --- | --- |
| 某行成功后 | 规范记录更新于 `data/records/<record-id>/` |
| 可恢复的批运行状态 | `data/cache/runs/<run_id>/`（结果、分配、失败、resume 状态等） |
| 查看器材质化 | `data/cache/record_materialization/<record-id>/`（由 `compile` / `compile-all` 生成） |

**注意：** `data/cache/` 一般**不应**提交到 git；pre-commit 会阻止敏感缓存路径。

---

## 批处理后的本地验证清单

- [ ] `uv run articraft dataset validate`（若你维护数据集不变式）
- [ ] 对关键记录 `uv run articraft compile data/records/<id>`
- [ ] `just viewer` 中检查关节、重叠、评级
- [ ] 仅将 `data/records/<id>/` 纳入 PR（见 [CONTRIBUTING_c.md](../CONTRIBUTING_c.md)）

---

## 相关文档

- [架构说明](architecture_c.md)
- [类别提示指南](../data/CATEGORY_PROMPT_GUIDE_c.md)
- [类别入选要求](../data/CATEGORY_SELECTION_REQUIREMENTS_c.md)
- [已拒绝类别列表](../data/REJECTED_CATEGORIES_c.md)
