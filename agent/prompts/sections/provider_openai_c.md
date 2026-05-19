<tools>
<!-- OpenAI 提供方：可用工具及使用约定 -->

- **可用工具（Available tools）**：`read_file`、`apply_patch`、`compile_model`、`probe_model`、`find_examples`。
- `read_file`：用于读取虚拟工作区文件**精确文本**的 **JSON tool**。
- `apply_patch`：**FREEFORM** 工具；发送**原始 patch 文本**，**不要**用 JSON 包装。
- `compile_model`：运行 compile + QC，并返回结构化的 `<compile_signals>`。
- `probe_model`：**只读** Python 检查；不写文件、不修改 object、不启动子进程。
- `find_examples`：在精选 SDK 示例中搜索模式。须结合当前 SDK 文档改编，勿机械复制；`[weakly relevant]` 仅作灵感。
- 在 patch 之前，先用 `read_file(path="model.py")` 读取**当前精确文件文本**。
- 优先多次**小型** `apply_patch` 编辑，而非一次巨型 patch 或整文件重写。
- 修改**现有**可编辑代码，**不要**假设从空白开始。
</tools>
