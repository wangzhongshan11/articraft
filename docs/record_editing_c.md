# 编辑已有记录

Articraft 通过 **fork（派生）** 将已有资产编辑为新记录，而不是在原记录上就地覆盖。Fork 保持**父记录不变**，并为本次编辑提供独立的提示、模型输出、溯源（provenance）、费用与轨迹。

> **设计原因：** 不提供面向用户的「就地编辑」命令，以避免所有权、溯源与 UI 状态混乱。要改形状/结构请用 `fork`；仅当有意用**原存储的提示与配置**从头再生成整条记录时，才使用 `rerun`。

---

## Fork 一个资产

使用 `articraft fork`，传入记录 ID 或规范记录目录路径：

```bash
uv run articraft fork data/records/<record_id> "make the handle longer"
```

### 与生成相同的模型控制

```bash
uv run articraft fork data/records/<record_id> \
  --model gemini-3-flash-preview \
  --thinking-level low \
  --max-cost-usd 1.5 \
  "make the hinge wider and reinforce the mounting plate"
```

| 参数 | 说明 |
| --- | --- |
| `--model` | 覆盖默认 LLM 模型 ID |
| `--thinking-level` | `low` / `med` / `high` |
| `--max-cost-usd` | 本次编辑运行的美元费用上限 |

### 参考图

编辑运行可附带参考图（与 `generate` 类似）：

```bash
uv run articraft fork data/records/<record_id> \
  --image reference.png \
  "match the latch shape in the reference image"
```

### 指定稳定的子记录 ID

若需要可预测的子记录目录名：

```bash
uv run articraft fork data/records/<record_id> \
  --record-id rec_longer_handle_edit \
  "make the handle longer"
```

**注意：** 子 ID 需在存储层唯一；与已有记录冲突会导致失败。

---

## Fork 会写入什么

Fork 创建**新的子记录**，并带有自己的**第一个修订版本**（revision）：

```text
data/records/<child_record_id>/
  record.json
  collections/
  revisions/
    rev_000001/
      prompt.txt
      model.py
      provenance.json
      cost.json   # 可选
      inputs/     # 仅本次编辑新提供的输入
      traces/
```

### 不会从父记录复制的内容

子记录**仅保存本次编辑运行**的制品，**不会**复制：

- 父记录的 `traces/`
- 父记录的费用文件、完整 provenance 历史
- 父记录的旧 `model.py` 快照
- 父记录的 `inputs/`（除非本次 fork 新提供）

### 谱系（lineage）如何工作

子记录在元数据中通过 **lineage 引用** 指向父记录与父修订版本。查看器历史面板可沿谱系遍历，从而在**不复制父轨迹文件**的情况下 inspect 父级对话与上下文。

---

## 数据集与工作台行为

Fork **默认继承**父记录的集合（collection）类型：

| 父记录类型 | Fork 结果 |
| --- | --- |
| 工作台记录 | 工作台子记录 |
| 数据集记录 | 同 `category_slug` 下的数据集子记录 |
| 数据集 ID | 子记录获得由「父 dataset ID + 子 record ID」派生的**新** dataset ID |

**父记录不会被修改。**

### `fork` vs `rerun`

| 操作 | 何时使用 | 父/原记录 |
| --- | --- | --- |
| `fork` | 用**新提示**做编辑或变体 | 父记录保留；新建子记录 |
| `rerun` | 用**原记录已存**的 prompt/provenance 设置重新生成 | 覆盖/更新同一记录的运行结果（有意为之时） |

外部智能体编辑现有资产时，应使用 `articraft external fork`（见 [EXTERNAL_AGENT_DATA_c.md](../EXTERNAL_AGENT_DATA_c.md)），不要手动复制 `data/records/` 文件夹。

---

## 查看编辑历史

Fork 完成后，按 usual 流程编译并打开查看器：

```bash
uv run articraft compile data/records/<child_record_id> --target visual
just viewer
```

查看器**历史面板**可沿 lineage 在子编辑与父对话之间切换，无需将父轨迹复制进子记录目录。

---

## 故障排查

| 现象 | 可能原因 | 建议 |
| --- | --- | --- |
| fork 后查看器无模型 | 未编译或编译失败 | 运行 `external check` 或 `articraft compile ... --target visual`，查看编译报告 |
| 子记录不在预期类别 | 父为工作台记录 | 需 `external finalize --category-slug ...` 或数据集工作流归入类别 |
| 费用超限 | `--max-cost-usd` 过低 | 提高上限或换更小/更便宜的模型 |
| 找不到父历史 | lineage 元数据损坏 | 检查子记录 `record.json` 与 provenance |

---

## 相关文档

- [README 快速入门](../README_c.md)
- [外部智能体 fork 流程](../EXTERNAL_AGENT_DATA_c.md)
- [贡献指南中的数据工作流](../CONTRIBUTING_c.md)
