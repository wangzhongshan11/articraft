Generate a tabletop-scale, non-safety-critical printable articulated model. Use the Chinese prompt as the normative specification. Deliver semantic parts, joint hierarchy, URDF, source, STEP if supported, STL/3MF printable parts, motion evidence, print plan, and full provenance trace.
Simultaneous delivery:  telemetry/events.jsonl: Real events of current session, LLM, tools, asynchronous tasks, errors/retries, and product writes with UTC timestamps;  telemetry/run_summary.json: Actual duration, LLM/tool invocation counts, waiting time, Prompt/Completion/Total Tokens;  artifact_manifest.json, pipeline_plan.json, environment.json;  Final response lists model outputs and the above file paths;  Unobtainable data must be marked as unavailable and not estimated.

生成一个低载荷、桌面级复合杠杆钳/夹爪演示模型，不用于真实切割或高载荷夹持。包含两个手柄、两片钳口、主枢轴和一组复合连杆，使手柄闭合时钳口同步闭合。最大张口 35 mm，手柄长度约 120 mm。钳口内侧设计 1 mm 深的防滑齿纹，但所有尖角倒钝。要求记录钳口开闭行程、左右对称性和零件干涉；各件独立打印，销轴间隙 0.35 mm。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。