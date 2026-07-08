生成一个桌面级折叠四旋翼无人机机架，仅作为无电子件的结构与机构原型。中央机身为 120 mm 见方的轻量化壳体，四个折叠臂以 90° 圆周阵列连接；每个臂长约 95 mm，具有展开定位角和折叠收纳角。每个臂根部使用可打印铰链或 M3 销轴孔，并配独立锁止卡扣。桨盘仅作为圆形安装盘，不生成可飞行部件。要求展开状态与收纳状态均无碰撞，所有臂可单独打印。
输出完整可溯源产物。
同时交付：
telemetry/events.jsonl：本轮会话、LLM、工具、异步任务、错误/重试、产物写入的真实事件与 UTC 时间；
telemetry/run_summary.json：真实耗时、LLM/工具调用次数、等待时间、Prompt/Completion/Total Token；
artifact_manifest.json、pipeline_plan.json、environment.json；
最终回复列出模型产物和上述文件路径；
无法获取的数据必须标记 unavailable，不得估算。