Generate a tabletop-scale, non-safety-critical printable articulated model. Use the Chinese prompt as the normative specification. Deliver semantic parts, joint hierarchy, URDF, source, STEP if supported, STL/3MF printable parts, motion evidence, print plan, and full provenance trace.
Simultaneous delivery:  telemetry/events.jsonl: Real events of current session, LLM, tools, asynchronous tasks, errors/retries, and product writes with UTC timestamps;  telemetry/run_summary.json: Actual duration, LLM/tool invocation counts, waiting time, Prompt/Completion/Total Tokens;  artifact_manifest.json, pipeline_plan.json, environment.json;  Final response lists model outputs and the above file paths;  Unobtainable data must be marked as unavailable and not estimated.

生成一个桌面级可打印风扇外观与运动原型，不包含真实电机或电气部件。包含圆形前后网罩、5 叶叶轮、叶轮轴、U 形俯仰支架和底座。叶轮可绕水平轴旋转；风扇主体可在支架上从 -15° 到 45° 俯仰。网罩格栅厚度至少 1.6 mm，叶轮与网罩间最小安全间隙 3 mm。所有零件可拆分打印；输出 URDF、model.py、STEP、STL/3MF、零件/关节清单、关节 probe 证据、打印方案和 trace。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。