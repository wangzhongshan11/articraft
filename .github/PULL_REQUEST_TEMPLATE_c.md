## 描述

请清晰描述本次 PR 的新功能或缺陷修复。请包含审查者理解问题或功能所需的上下文（关联 Issue、动机、权衡）。

- **受影响区域：** [例如 agent、storage、sdk、viewer、data、cli、docs]

## 已运行的命令

列出你在本地为验证本变更而运行的**确切**命令（例如 `just test-all`、`uv run articraft generate ...` 等）：

- `...`

## 检查清单

- [ ] 我已阅读 [贡献指南](../CONTRIBUTING_c.md)。
- [ ] 我已运行本地格式化与 linter（`just format`、`just lint`；前端变更另运行 `npm --prefix viewer/web run lint` / `typecheck`）。
- [ ] 测试通过（`just smoke-tests` 或更广的 `just test-all`）。
- [ ] 若存在查看器或 API 行为变更，我已添加截图或 GIF。
- [ ] 相关文档已更新（含 `_c.md` 中文版若适用）。
- [ ] 数据 PR：仅包含 `data/records/<id>/`，未提交 `.env`、`data/cache/`、生成 URDF 等（pre-commit 应已拦截）。

## 数据贡献补充（若适用）

- 记录数量与类别 slug：
- 查看器星级分布（可选）：
- 代表性截图/GIF：
