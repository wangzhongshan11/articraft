生成一个桌面级微型健身车传动演示模型，不用于承载人体。包含主车架、曲柄、两片踏板、飞轮、传动轮、座椅和可调座杆。曲柄与飞轮分别可绕平行轴转动，采用简单齿轮或皮带轮几何表达二者传动关系；座杆可在 25 mm 行程内上下移动并用定位孔锁止。总长约 220 mm。输出运动清单、传动轴对齐检查、可打印拆件、打印方案和完整 trace。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。