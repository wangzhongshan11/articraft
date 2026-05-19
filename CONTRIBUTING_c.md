# 为 Articraft 做贡献

感谢你愿意改进 Articraft！我们欢迎各类贡献：缺陷报告、新功能、修复或更好的文档——一切都有帮助。

---

## 入门

1. **架构与项目布局：** 请先阅读 [架构指南](docs/architecture_c.md)，了解 `agent/`、`storage/`、`sdk/`、`viewer/` 等目录职责与数据流。
2. **环境搭建：** 若尚未配置，在仓库根目录执行：

    ```bash
    uv sync --group dev
    npm --prefix viewer/web ci
    uv run pre-commit install --hook-type pre-commit --hook-type pre-push
    uv run articraft hooks install
    ```

   或使用一键：`just setup`（会同步依赖、安装钩子、初始化 `data/` 等）。

---

## 开发工作流

### 常用命令

我们使用 `just` 作为主要任务运行器。无参数运行 `just` 可列出所有快捷方式。

| 命令 | 作用 |
| --- | --- |
| `just format` | 使用 Ruff 格式化 Python 代码 |
| `just lint` | Ruff 静态检查 |
| `just viewer-dev` | 同时启动 uvicorn API 与 Vite 前端，便于 UI 快速迭代 |
| `just smoke-tests` | 推送前快速冒烟测试套件 |
| `just test-all` | 完整 Python pytest 套件 |

### Python 开发

- 目标版本：**Python 3.11+**（本地 `uv` 倾向 3.12；**排除 3.13**）。
- 包管理：`uv`；格式与检查：`ruff`（`pyproject.toml`：行宽 100，规则 `E`/`F`/`I`，忽略 `E501`）。
- 提交 PR 前请运行 `just format` 与 `just lint`。
- 测试框架：`pytest`。我们优先**快速导入**、**稳健的行为断言**，避免脆弱的「逐行 prompt 快照」类测试；更新 prompt 契约时，应在同一变更中放宽或删除过时的 prompt 断言。

### 前端开发

查看器技术栈：React、TypeScript、Tailwind CSS v4、shadcn/ui、Three.js。Web 端启用严格 TypeScript 与 ESLint。

```bash
npm --prefix viewer/web run dev        # 启动 Vite 前端开发服务器
npm --prefix viewer/web run typecheck  # 运行 TSC
npm --prefix viewer/web run lint       # 运行 ESLint
```

---

## 创建 Pull Request

提交 PR 时，请将变更**限定在单一逻辑主题**（一个功能或一个修复），便于审查与回滚。

### 验证你的变更

1. 推送前尽量运行最快检查：

   ```bash
   just smoke-tests
   npm --prefix viewer/web run typecheck
   npm --prefix viewer/web run lint
   ```

2. 若改动面较广的 Python 逻辑，运行 `just test-all`。

### 提交（Commit）规范

我们重视提交信息质量：

- 使用**简短、祈使句**主题（例如 `Move prompt compiler under agent`，**不要**用 `Moved...` 或 `Moving...`）。
- 标题尽量 **50 字符以内**，且对应**一个逻辑变更**。
- 若修复某 issue，在正文中引用 issue 编号。

### PR 要求

1. 填写 Pull Request 模板，标明受影响区域（`agent`、`storage`、`sdk`、`viewer`、`cli`、`data` 等）。
2. 列出你为验证而运行的**确切** `uv`、`just`、`npm` 命令。
3. **仅当** API 或查看器行为变化时附截图或 GIF。
4. **数据相关注意：** 不要提交 `.env`、`data/cache/`、`data/local/`、生成的 URDF 或记录资产缓存目录。pre-commit 通常会拦截敏感路径。`data/` 下文件**豁免**「文件末尾必须有换行符」规则（生成物可能无末尾换行）。

---

## 数据贡献工作流

Articraft 的核心使命之一是通过众包构建**大规模、多样化**的关节化 3D 数据集。若你贡献的是**对象记录**而非纯代码，请遵循下列一致流程。

### 1. 选择生成路径

| 路径 | 适用场景 | 入口 |
| --- | --- | --- |
| **定向创作** | 单条 prompt 直接进入某类别 | `uv run articraft dataset run "<prompt>" --category-slug <slug>` |
| **编辑已有资产** | 在保留父记录前提下修改 | `uv run articraft fork data/records/<record_id> "<edit prompt>"`（见 [编辑已有记录](docs/record_editing_c.md)） |
| **AI 辅助（外部智能体）** | Claude Code、Cursor、Codex 等 | 提示智能体遵循 `EXTERNAL_AGENT_DATA_c.md`；**不要**自己手动跑完整 `external` 替代流程——由智能体在仓库内执行 `uv run articraft external ...` |
| **批量生成** | 多行、可 resume 的类别批处理 | CSV + `articraft dataset batch`（见 [数据集生成指南](docs/dataset_generation_c.md)） |

### 2. 本地验证

- 所有资产必须在本地**无错误编译**通过。
- 物理警告、部件重叠、连杆断开等问题应在提交 PR 前修复（可用 `articraft compile`、`external check`、查看器检查）。

### 3. 视觉策展与评级

- 打开查看器：`just viewer`，人工检查几何、关节范围、语义部件。
- **关键步骤：** 使用查看器**星级评级（1–5 星）**并保存。我们接受所有评级（1 星负样本同样宝贵），但你**必须**主动记录评级，否则策展不完整。

### 4. 定稿与归类

- 仅应推送已分配到**数据集类别**的记录；**工作台（workbench）**记录视为本地草稿，一般不进入数据集 PR。

### 5. 提交与 PR

- **仅 stage** `data/records/<id>/` 相关目录；钩子会阻止 cache、URDF 等。
- PR 标题示例：`Add 50 washing machines to dataset`。
- **大规模 PR 欢迎**：可从单个对象到数千条记录。
- **强烈建议附截图/GIF**：显著加快审查者对形态与关节的确认。

### 论文数据集计数说明

编辑论文时请区分「原始生成记录数」与「最终策展数据集」。最终论文数据集通常仅包含保留的 **4–5 星**对象；`data/records/` 中的 1–3 星可能是负样本或审计材料，**不应**计入最终对象数，除非重新统计并有意更新论文表述（默认可用「超过 10K」指最终策展规模）。

---

## 相关文档

- [安全策略](SECURITY_c.md)
- [外部智能体数据指南](EXTERNAL_AGENT_DATA_c.md)
- [类别提示指南](data/CATEGORY_PROMPT_GUIDE_c.md)
- [仓库指南 AGENTS](AGENTS_c.md)
