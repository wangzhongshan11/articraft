Generate a tabletop-scale, non-safety-critical printable articulated model. Use the Chinese prompt as the normative specification. Deliver semantic parts, joint hierarchy, URDF, source, STEP if supported, STL/3MF printable parts, motion evidence, print plan, and full provenance trace.
Simultaneous delivery:  telemetry/events.jsonl: Real events of current session, LLM, tools, asynchronous tasks, errors/retries, and product writes with UTC timestamps;  telemetry/run_summary.json: Actual duration, LLM/tool invocation counts, waiting time, Prompt/Completion/Total Tokens;  artifact_manifest.json, pipeline_plan.json, environment.json;  Final response lists model outputs and the above file paths;  Unobtainable data must be marked as unavailable and not estimated.

生成一个桌面级多层缝纫/小工具收纳盒。包含底盒、左右两组上翻托盘、主盖和联动连杆；打开主盖时，上层托盘能够通过铰链与连杆向两侧展开。整体闭合尺寸约 180 × 100 × 90 mm。盒体壁厚至少 2 mm，所有旋转连接留 0.35 mm 间隙，联动轨迹不得碰撞。要求分别导出底盒、托盘、盖、连杆与销轴；输出 URDF、model.py、STEP、STL/3MF、开闭关节状态图和完整 trace。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。