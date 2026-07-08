生成一个桌面级、可 3D 打印的双臂可调台灯模型。包含加重底座、下臂、上臂、可俯仰灯头；下臂与上臂通过两个水平转轴连接，灯头再通过一个俯仰转轴连接。每个转轴使用可打印销轴或 M4 螺栓孔，转动间隙 0.35 mm，设置机械限位以避免互相穿插。臂长约 120 mm 和 100 mm，底座直径约 110 mm。
要求零件可拆分打印；输出 URDF、model.py、STEP、STL/3MF、零件清单、关节清单、动作范围、打印朝向和完整 trace。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。
