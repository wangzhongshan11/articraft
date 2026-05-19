# Articraft 中文文档索引（`_c` 译本）

> 本索引列出仓库内所有 **Markdown 文档** 的简体中文译本。命名规则：在扩展名前插入 `_c`，例如 `README.md` → `README_c.md`。  
> **英文原文未被修改**；译本与原文并列存放，便于对照阅读。

---

## 使用说明

| 项目 | 说明 |
|------|------|
| 如何阅读 | 打开与英文文件同目录下的 `*_c.md` 即可 |
| 代码与命令 | 译本中 **保留英文** 的命令行、路径、API 名、环境变量，并在正文中用中文解释 |
| 内部链接 | 译本内交叉引用已尽量指向 `*_c.md` 版本 |
| 未纳入范围 | `data/categories/**/prompt_batches/`（数据集提示词）、`data/system_prompts/`（哈希缓存）、`agent/prompts/generated/`（编译后的 LLM 系统提示，需保持英文） |
| 重新扫描 | `uv run python scripts/translate_docs_to_chinese_c.py` 列出全部文档；加 `--missing-only` 仅显示缺译本 |

---

## 一、项目入口与协作（15 个）

| 英文原文 | 中文译本 | 内容简介 |
|----------|----------|----------|
| [README.md](README.md) | [README_c.md](README_c.md) | 项目介绍、快速开始、生成与查看器、数据贡献、引用 |
| [AGENTS.md](AGENTS.md) | [AGENTS_c.md](AGENTS_c.md) | 面向 AI 编码助手的仓库规范与命令 |
| [CLAUDE.md](CLAUDE.md) | [CLAUDE_c.md](CLAUDE_c.md) | Claude Code 专用指南（与 AGENTS 对齐） |
| [CONTRIBUTING.md](CONTRIBUTING.md) | [CONTRIBUTING_c.md](CONTRIBUTING_c.md) | 贡献流程、PR、数据工作流、提交规范 |
| [EXTERNAL_AGENT_DATA.md](EXTERNAL_AGENT_DATA.md) | [EXTERNAL_AGENT_DATA_c.md](EXTERNAL_AGENT_DATA_c.md) | 外部 Agent（Cursor/Codex 等）写入数据集的标准流程 |
| [SECURITY.md](SECURITY.md) | [SECURITY_c.md](SECURITY_c.md) | 安全策略：执行不可信 `model.py` 的风险 |
| [docs/architecture.md](docs/architecture.md) | [docs/architecture_c.md](docs/architecture_c.md) | 架构与模块划分、Workbench vs 数据集批处理 |
| [docs/record_editing.md](docs/record_editing.md) | [docs/record_editing_c.md](docs/record_editing_c.md) | Fork 编辑已有记录、目录结构、查看器历史 |
| [docs/dataset_generation.md](docs/dataset_generation.md) | [docs/dataset_generation_c.md](docs/dataset_generation_c.md) | 批量 CSV、并发、Resume 策略 |
| [data/CATEGORY_PROMPT_GUIDE.md](data/CATEGORY_PROMPT_GUIDE.md) | [data/CATEGORY_PROMPT_GUIDE_c.md](data/CATEGORY_PROMPT_GUIDE_c.md) | 类别与提示词编写指南 |
| [data/CATEGORY_SELECTION_REQUIREMENTS.md](data/CATEGORY_SELECTION_REQUIREMENTS.md) | [data/CATEGORY_SELECTION_REQUIREMENTS_c.md](data/CATEGORY_SELECTION_REQUIREMENTS_c.md) | 类别筛选要求 |
| [data/REJECTED_CATEGORIES.md](data/REJECTED_CATEGORIES.md) | [data/REJECTED_CATEGORIES_c.md](data/REJECTED_CATEGORIES_c.md) | 已拒绝类别说明 |
| [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md) | [bug_report_c.md](.github/ISSUE_TEMPLATE/bug_report_c.md) | Bug 报告模板（中文说明） |
| [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md) | [feature_request_c.md](.github/ISSUE_TEMPLATE/feature_request_c.md) | 功能请求模板 |
| [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) | [PULL_REQUEST_TEMPLATE_c.md](.github/PULL_REQUEST_TEMPLATE_c.md) | PR 模板 |

---

## 二、Agent 提示词片段（7 个）

位于 `agent/prompts/sections/`，由 `agent/prompts/compile.py` 编译进 `generated/`。**运行时仍使用英文 generated 文件**；`_c` 供中文读者理解各段含义。

| 原文 | 译本 |
|------|------|
| designer_common.md | designer_common_c.md |
| gemini_compaction.md | gemini_compaction_c.md |
| link_naming.md | link_naming_c.md |
| provider_gemini.md | provider_gemini_c.md |
| provider_openai.md | provider_openai_c.md |
| provider_openrouter_process.md | provider_openrouter_process_c.md |
| sdk_base.md | sdk_base_c.md |

---

## 三、SDK 参考文档 `sdk/_docs/`（26 个）

### common（8）

| 原文 | 译本 |
|------|------|
| common/00_quickstart.md | 00_quickstart_c.md |
| common/10_errors.md | 10_errors_c.md |
| common/20_core_types.md | 20_core_types_c.md |
| common/30_articulated_object.md | 30_articulated_object_c.md |
| common/40_assets.md | 40_assets_c.md |
| common/50_placement.md | 50_placement_c.md |
| common/70_probe_tooling.md | 70_probe_tooling_c.md |
| common/80_testing.md | 80_testing_c.md |

### base 几何专题（10）

| 原文 | 译本 |
|------|------|
| base/40_mesh_geometry.md | 40_mesh_geometry_c.md |
| base/41_panels_and_grilles.md | 41_panels_and_grilles_c.md |
| base/42_brackets_and_mounts.md | 42_brackets_and_mounts_c.md |
| base/43_fans_and_rotors.md | 43_fans_and_rotors_c.md |
| base/44_knobs_and_controls.md | 44_knobs_and_controls_c.md |
| base/45_wires.md | 45_wires_c.md |
| base/46_section_lofts.md | 46_section_lofts_c.md |
| base/47_bezels_and_frames.md | 47_bezels_and_frames_c.md |
| base/48_wheels_and_tires.md | 48_wheels_and_tires_c.md |
| base/49_hinges.md | 49_hinges_c.md |

### cadquery（8）

| 原文 | 译本 |
|------|------|
| cadquery/35_cadquery.md | 35_cadquery_c.md |
| cadquery/36_cadquery_primer.md | 36_cadquery_primer_c.md |
| cadquery/37_cadquery_workplane.md | 37_cadquery_workplane_c.md |
| cadquery/38_cadquery_sketch.md | 38_cadquery_sketch_c.md |
| cadquery/39_cadquery_assembly.md | 39_cadquery_assembly_c.md |
| cadquery/39b_cadquery_free_function.md | 39b_cadquery_free_function_c.md |
| cadquery/39c_cadquery_api_ref.md | 39c_cadquery_api_ref_c.md |
| cadquery/39d_cadquery_gears.md | 39d_cadquery_gears_c.md |

---

## 四、SDK 示例 `sdk/_examples/`（94 个）

每个示例均为 **YAML frontmatter + 说明 + Python 代码**；译本保留代码不变，并补充中文场景说明与参数解读。

- **`sdk/_examples/base/`**：13 个完整物体示例（搅拌机、ATV、风扇、望远镜等）
- **`sdk/_examples/cadquery/`**：81 个 CadQuery 片段与机构示例（齿轮、滑台、铰链、外壳等）

在资源管理器中于 `sdk/_examples` 下筛选 `*_c.md`，或与同名 `.md` 对照打开。

---

## 五、推荐阅读顺序（中文读者）

1. [README_c.md](README_c.md) — 总览  
2. [docs/architecture_c.md](docs/architecture_c.md) — 代码放在哪  
3. [sdk/_docs/common/00_quickstart_c.md](sdk/_docs/common/00_quickstart_c.md) — 写 `model.py` 的契约  
4. [docs/dataset_generation_c.md](docs/dataset_generation_c.md) 或 [CONTRIBUTING_c.md](CONTRIBUTING_c.md) — 批量造数据 / 贡献  
5. [docs/record_editing_c.md](docs/record_editing_c.md) — 修改已有资产  

---

## 六、统计

| 类别 | 数量 |
|------|------|
| 文档译本总计 | **142** |
| 根目录 + docs + data + GitHub | 15 |
| agent/prompts/sections | 7 |
| sdk/_docs | 26 |
| sdk/_examples | 94 |

---

## 七、维护说明

- 更新英文文档后，请同步更新对应 `*_c.md`，或重新发起翻译任务。  
- `scripts/translate_docs_to_chinese_c.py` 仅用于枚举路径，**不自动翻译**。  
- 若需将中文文档设为默认阅读路径，可在本地书签或 IDE 多根工作区中优先打开 `*_c.md`，**不要**在未协调的情况下替换 harness 加载的英文 SDK 文档路径（会影响 LLM 生成行为）。

---

*索引生成：Articraft 文档中文化批次；与英文仓库版本并列维护。*
