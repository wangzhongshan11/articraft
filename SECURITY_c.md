# 安全策略

## 如何报告安全问题

**请勿**就疑似密钥泄露、凭证暴露或其他敏感安全问题开设**公开** GitHub Issue。

请通过以下**私密**渠道联系维护者：

1. **首选：** 在仓库 **Security** 标签页点击 **「Report a vulnerability」**（GitHub Security Advisories）。
2. **备选：** 若 Advisory 不可用，请向维护者发送邮件。邮箱由下列片段拼接（防爬虫）：`mattzh1314` + `@` + `gmail` + `.com`。

报告请包含足以**复现或验证**问题的细节（受影响版本、步骤、影响范围等）。

### 报告中请勿包含

- 有效的 API 密钥或令牌
- 私有 prompt 或未发布数据集全文
- 原始凭证材料

---

## 关于生成代码的重要说明

Articraft 记录在 `revisions/<revision_id>/model.py` 中包含 **Python 脚本**。以下操作会在本机**执行这些脚本**：

- **编译（compile）**
- **探测（probe）/QC**
- **查看器材质化（materialization）**

### 风险与建议

| 风险场景 | 建议 |
| --- | --- |
| 批量运行不可信来源的 `data/records/` | 使用沙箱容器、 disposable VM 或专用隔离主机 |
| 对抗性 prompt 生成模型 | 勿在含敏感数据或凭证的生产机上直接 `generate` |
| 从第三方下载的 `model.py` | 视为不可信代码；先静态审阅再在隔离环境执行 |

**不要**在敏感机器上直接对不可信第三方 `model.py` 做 bulk-run、对抗性生成或未经审查的执行。

---

## 开发与贡献中的安全习惯

- 勿将 `.env`、密钥提交到 git（pre-commit 会扫描 staged 内容中的提供商密钥模式）。
- 勿在 Issue/PR 中粘贴完整 API key。
- 审查外部贡献的记录时，同样假设 `model.py` 可能恶意，在隔离环境打开查看器或编译。

---

## 许可证与责任

本仓库软件按 [Apache-2.0](LICENSE) 许可；用户对在本机执行生成代码的环境安全负责。
