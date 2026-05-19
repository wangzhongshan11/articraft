# 已拒绝的类别

#
# 维护一份简单运行列表：记录曾被加入但后来移除的类别，
# 以便在后续头脑风暴或 tracker 编辑时避免意外重新引入。

下列类别**曾进入讨论或短期存在**，但因运动学/SDK 适配、范围重叠、或难以稳定批量生成等原因**未保留**在 `data/categories/` 正式分类中。新增类别前请先对照 [类别入选要求](CATEGORY_SELECTION_REQUIREMENTS_c.md) 与 [类别提示指南](CATEGORY_PROMPT_GUIDE_c.md)。

| 英文名称（仓库记录用） | 简要拒绝原因（说明） |
| --- | --- |
| Universal joint shaft | 万向节轴：耦合/闭链或 URDF 难以诚实表达的核心运动 |
| Stapler | 订书机：机构与夹持运动常超出简单树形单轴关节模型 |
| Hole punch | 打孔器：类似订书机，定义性运动难用显式关节树表达 |
| Vehicle side-mirror assembly | 车辆侧后视镜总成：范围过大/机构复杂，易与现有车辆部件类别重叠 |
| True wireless earbuds charging case | TWS 耳机充电盒：小尺度多机构，易碎且与消费电子细分类重复 |
| Car door with sliding window | 带升降窗车门：多自由度耦合（窗轨+门铰）难诚实建模 |
| Caulking gun | 胶枪：螺旋/活塞耦合运动不适合作为类别主定义 |
| Game controller with triggers and thumbsticks | 带扳机与摇杆的游戏手柄：大量小关节与控制面，批处理成本高且 SDK 易碎 |
| Robot head and torso | 机器人头与躯干：范围模糊，与机械臂/躯干类重叠 |
| Biped pelvis assembly | 双足骨盆总成：生物运动链与闭链问题 |
| Helmet | 头盔：多为刚性壳体，关节化价值低或 articulation 不清晰 |
| Scissors | 剪刀：交叉连杆/闭链为类别核心，与 URDF 树约束冲突 |

> **使用方式：** 若你提议的新类别与上表语义相近，请先考虑合并进现有类别、改写 prompt 批次，或换用 [指南中的可用替代机构](CATEGORY_PROMPT_GUIDE_c.md#运动学-urdf-无法表达的模式)（例如用伸缩 prismatic 代替剪刀式连杆）。
