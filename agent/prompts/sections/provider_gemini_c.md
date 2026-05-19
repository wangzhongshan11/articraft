<tools>
<!-- Gemini 提供方：可用工具及使用约定 -->

- **可用工具（Available tools）**：`read_file`、`replace`、`write_file`、`compile_model`、`probe_model`、`find_examples`。
- `read_file`：读取虚拟工作区中文件的**精确文本**。对当前可编辑代码段使用 `read_file(path="model.py")`；对只读 SDK 参考使用 `read_file(path="docs/...")`。
- `replace`：在可编辑代码段内执行**外科手术式**文本替换（surgical text replacement）。
- `write_file`：当需要**有意**进行较大范围替换时，重写整个可编辑代码段。
- `compile_model`：运行 compile + QC，并返回结构化的 `<compile_signals>`。
- `probe_model`：**只读** Python 检查；不写文件、不修改 object、不启动子进程（subprocesses）。
- `find_examples`：在精选 SDK 示例中搜索模式。须结合当前 SDK 文档**改编**结果，**不要**机械复制示例代码；标记为 `[weakly relevant]` 的条目仅作灵感参考。
- 优先使用**小而精确**的 `replace` 编辑，而非大范围重写。
- 若 `replace` 因 `old_string` 未匹配而失败，再次调用 `read_file(path="model.py")`，并用**更小的精确片段**重试。
- 修改**现有**可编辑代码；仅当你**有意**替换整个可编辑段时才使用 `write_file`。
- 当不再需要 tools 时，应**结束（conclude）**，而非继续在文本中反思。
- 在**最新 revision** 上 compile **干净通过**后，**立即结束**，除非你能点名**一个具体未解决缺陷**。
- 成功后**不要**做额外验证、回顾性闲聊或无命名缺陷的精修轮次。
</tools>
