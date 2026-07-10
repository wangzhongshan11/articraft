生成一个桌面比例折叠式工具推车/婴儿车骨架模型，仅作机构和 3D 打印测试，不承载儿童或重物。包含四个轮子、前后轮轴、折叠推杆、矩形车斗框、两组 X 形连杆与展开锁止件。展开时尺寸约 220 × 140 × 200 mm；闭合后推杆和车斗框靠近。车轮可转动，折叠连杆有明确转轴与行程。输出多状态 URDF、所有结构件的可打印拆分、关节限位与 trace。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。