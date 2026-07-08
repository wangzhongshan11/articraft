Generate a tabletop-scale, non-safety-critical printable articulated model. Use the Chinese prompt as the normative specification. Deliver semantic parts, joint hierarchy, URDF, source, STEP if supported, STL/3MF printable parts, motion evidence, print plan, and full provenance trace.
Simultaneous delivery:  telemetry/events.jsonl: Real events of current session, LLM, tools, asynchronous tasks, errors/retries, and product writes with UTC timestamps;  telemetry/run_summary.json: Actual duration, LLM/tool invocation counts, waiting time, Prompt/Completion/Total Tokens;  artifact_manifest.json, pipeline_plan.json, environment.json;  Final response lists model outputs and the above file paths;  Unobtainable data must be marked as unavailable and not estimated.

生成一个桌面级铰接压板/华夫饼机外观机构模型，不包含加热、电气或食品接触要求。包含底座、上盖、上下可替换压板、后部双铰链、前部锁扣和 6 × 6 浅方格阵列。上盖开合范围 0° 到 105°；闭合时上、下压板保持至少 1.0 mm 间隙，避免几何穿插。外壳壁厚至少 2 mm；压板可拆分打印。输出完整的部件树、关节/锁扣检查、开闭图、STEP/STL/3MF 和 agent trace。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。
