Generate a tabletop-scale, non-safety-critical printable articulated model. Use the Chinese prompt as the normative specification. Deliver semantic parts, joint hierarchy, URDF, source, STEP if supported, STL/3MF printable parts, motion evidence, print plan, and full provenance trace.
Simultaneous delivery:  telemetry/events.jsonl: Real events of current session, LLM, tools, asynchronous tasks, errors/retries, and product writes with UTC timestamps;  telemetry/run_summary.json: Actual duration, LLM/tool invocation counts, waiting time, Prompt/Completion/Total Tokens;  artifact_manifest.json, pipeline_plan.json, environment.json;  Final response lists model outputs and the above file paths;  Unobtainable data must be marked as unavailable and not estimated.

生成一个桌面比例折叠椅结构模型，仅用于机构演示，不用于承载人体。包含前后 X 形支架、座面、靠背和连接销轴；座面离地约 90 mm，闭合后厚度不超过 35 mm。至少包含 4 个可转动铰链，并在展开状态形成稳定三角受力轮廓。所有杆件厚度至少 4 mm，转轴间隙 0.35 mm。要求输出展开、半折、闭合三种状态的关节 probe 证据，以及可打印拆件和完整 trace。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。