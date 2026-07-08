Generate a tabletop-scale, non-safety-critical printable articulated model. Use the Chinese prompt as the normative specification. Deliver semantic parts, joint hierarchy, URDF, source, STEP if supported, STL/3MF printable parts, motion evidence, print plan, and full provenance trace.
Simultaneous delivery:  telemetry/events.jsonl: Real events of current session, LLM, tools, asynchronous tasks, errors/retries, and product writes with UTC timestamps;  telemetry/run_summary.json: Actual duration, LLM/tool invocation counts, waiting time, Prompt/Completion/Total Tokens;  artifact_manifest.json, pipeline_plan.json, environment.json;  Final response lists model outputs and the above file paths;  Unobtainable data must be marked as unavailable and not estimated.

生成一个桌面级折叠三脚架手机/小相机支架。包含中心立柱、3 条等角分布的折叠腿、可上下滑动的开腿滑环、可俯仰云台和可调宽度 65–85 mm 的手机夹。腿长约 150 mm；三腿绕中心圆周均匀布置。云台俯仰范围 -20° 到 75°。要求收纳与展开两种状态都可表示，部件之间留 0.35 mm 活动间隙，夹具采用可拆分件或螺栓孔而不是不可打印的薄弹簧。输出完整模型与溯源证据。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。