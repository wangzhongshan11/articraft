# OpenCode 与 Codex 配置指南

本仓库**原先没有** OpenCode / Codex 的专用配置文件，但已有面向外部智能体的数据创作规范：

| 文档 | 用途 |
|------|------|
| [EXTERNAL_AGENT_DATA.md](../EXTERNAL_AGENT_DATA.md) | Codex、Claude Code、Cursor 等写入数据集时的**唯一支持流程** |
| [EXTERNAL_AGENT_DATA_c.md](../EXTERNAL_AGENT_DATA_c.md) | 上表中文译本 |
| [AGENTS.md](../AGENTS.md) | 通用 AI 编码助手（含 Cursor Agent）仓库规范 |
| [CLAUDE.md](../CLAUDE.md) | Claude Code 专用说明 |

下文说明**新增的即刻可用配置**及启动方式。

---

## 新增文件一览

| 路径 | 工具 | 作用 |
|------|------|------|
| [opencode.json](../opencode.json) | OpenCode | 项目级默认智能体、指令文件、文件监视忽略项 |
| [.opencode/agents/articraft.md](../.opencode/agents/articraft.md) | OpenCode | 默认主智能体：Articraft 外部数据创作 |
| [.opencode/commands/*.md](../.opencode/commands/) | OpenCode | 斜杠命令：`/setup`、`/external-init` 等 |
| [.codex/config.toml](../.codex/config.toml) | Codex | 项目级说明发现（含 `EXTERNAL_AGENT_DATA.md` 回退） |

---

## OpenCode

### 前置条件

- 已安装 [OpenCode](https://opencode.ai/) CLI
- 本仓库已执行 `just setup`（或至少 `uv sync --group dev` + `uv run articraft init`）
- 在 OpenCode 中配置好所用模型的 API（全局 `~/.config/opencode/opencode.json`）

### 使用

在仓库根目录启动 OpenCode TUI 或 `opencode run`：

```bash
cd /path/to/articraft
opencode
```

默认主智能体为 **`articraft`**（见 `opencode.json` 的 `default_agent`）。会自动加载 `AGENTS.md`、`EXTERNAL_AGENT_DATA.md`、`CLAUDE.md`。

### 内置斜杠命令

| 命令 | 说明 |
|------|------|
| `/setup` | 引导执行 `just setup`、处理 npm registry 问题 |
| `/external-init <prompt>` | 按规范 `external init` 新建记录 |
| `/external-fork <record> <edit>` | Fork 已有记录再编辑 |
| `/external-check <record>` | 运行 `external check` 严格校验 |
| `/viewer` | 启动 `just viewer-dev` |

### `creator.agent` 与 OpenCode

存储层仅接受 `codex` 或 `claude-code`（见 `cli/external.py`）。用 OpenCode 创作数据时：

- 使用 **OpenAI** 模型 → `uv run articraft external init --agent codex ...`
- 使用 **Anthropic** 模型 → `--agent claude-code ...`

智能体配置里已写明该映射，无需改仓库代码。

---

## Codex（OpenAI）

### 前置条件

- 已安装 [Codex CLI](https://developers.openai.com/codex/)
- 在 `~/.codex/config.toml` 中配置认证与默认模型
- **将本仓库标记为 trusted**，否则项目内 `.codex/config.toml` 不会加载

### 使用

```bash
cd /path/to/articraft
codex
```

Codex 会沿目录链读取 `AGENTS.md`。若某层没有 `AGENTS.md`，会尝试 `EXTERNAL_AGENT_DATA.md`（由 `.codex/config.toml` 的 `project_doc_fallback_filenames` 指定）。

生成 Articraft 数据时，在对话中说明：

> 遵循 EXTERNAL_AGENT_DATA.md，使用 `uv run articraft external init --agent codex ...`

或先阅读 [EXTERNAL_AGENT_DATA_c.md](../EXTERNAL_AGENT_DATA_c.md)。

### 与 Cursor 的区别

| 工具 | 项目配置 | 数据创作规范 |
|------|----------|----------------|
| **Cursor** | [AGENTS.md](../AGENTS.md)（已存在） | [EXTERNAL_AGENT_DATA.md](../EXTERNAL_AGENT_DATA.md) |
| **Codex** | `.codex/config.toml` + `AGENTS.md` | 同上 + fallback 文件名 |
| **OpenCode** | `opencode.json` + `.opencode/` | `instructions` + `articraft` 智能体 |

---

## 快速验证

```bash
export PATH="/opt/homebrew/bin:$PATH"
uv run articraft status
uv run articraft external --help
```

Viewer：

```bash
just viewer-dev
# 浏览器打开 http://127.0.0.1:5173/
```

---

## 常见问题

**npm 安装失败（公司 registry）**

```bash
export NPM_CONFIG_REGISTRY=https://registry.npmjs.org/
npm --prefix viewer/web ci --registry https://registry.npmjs.org/
```

**Codex 未加载 `.codex/config.toml`**

在 Codex 中将项目设为 trusted，或把 `project_doc_fallback_filenames` 复制到 `~/.codex/config.toml`。

**OpenCode 扫描仓库很慢**

已在 `opencode.json` 中忽略 `data/cache/**` 等大目录；单条记录的 `model.py` 仍可正常编辑。

---

## 相关链接

- [OpenCode 配置文档](https://opencode.ai/docs/config/)
- [OpenCode 自定义命令](https://opencode.ai/docs/commands/)
- [Codex AGENTS.md 指南](https://developers.openai.com/codex/guides/agents-md)
- [Codex 项目 config.toml](https://developers.openai.com/codex/config-advanced#project-config-files-codexconfigtoml)
