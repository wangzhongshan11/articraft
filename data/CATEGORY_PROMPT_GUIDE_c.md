# 类别 Prompt 指南

本文定义如何为 `data/batch_specs/` 下的批处理规格编写**类别 prompt**（每行 CSV 的 `prompt` 列）。

当前批处理使用**统一的默认建模栈**。prompt 中**不要**提及工具变体或流水线变体；正常批 CSV 也**不需要**额外的栈选择字段。

---

## 核心原则

**像机械工程师在餐巾纸上草图那样写 prompt——够用来开工，够不到填满规格书。**

系统 prompt 已覆盖：真实感、材质选择、校验、工具选择、构建流程。用户 prompt 应说明：

- **造什么**（对象身份）
- **有哪些主要部件**
- **如何运动**（关节化规格）

**更多 prompt 细节 → 更多几何 → 更多轮次 → 更高成本 → 更大出错面。** 你写的每一句都应告诉智能体一些**无法仅从对象名称推断**的信息。

---

## 系统 Prompt 已覆盖的内容

智能体系统 prompt 已强制下列要求——**不要在用户 prompt 中重复**：

- 逼真几何与合适的建模/CadQuery 工具选择
- 无悬空部件、无意外重叠
- 带编译反馈的增量构建
- 对放置、连通性、关节化的测试与校验
- 材质与颜色真实感
- 机械合理性

下列短语是**浪费 token**，**永远不要**写进 prompt：

- "realistic, highly detailed"
- "standalone mechanical study assembly"
- "for a specific tooling or pipeline variant"
- "emphasize rigid brackets, exposed bearing hardware"
- "disciplined machined-or-fabricated hard-surface geometry"
- "avoid product styling, decorative housings"
- "keep it as a pure mechanical assembly with explicit joints"
- "a short realism and buildability clause"

---

## Prompt 模板

每个 prompt 大致按下列顺序覆盖三件事（第 4 项可选）：

### 1. 对象身份（必需 — 约 1 句）

说明对象是什么，达到常人能认出的粒度。若该类别有多种常见形态，**点名具体变体**。

### 2. 部件结构（必需 — 约 1–2 句）

列出主要部件及**物理连接方式**，给智能体部件树脚手架。聚焦定义**轮廓**的部件与**会动**的部件，不必罗列每个子细节。

### 3. 关节化规格（必需 — 约 1–2 句）— **最重要**

- 关节类型：`revolute`（有限转动）、`prismatic`（滑动）、`continuous`（无界旋转）
- 连接哪些部件
- **轴方向**（相对父连杆/世界的大致方向）
- **明确写出每一个关节**
- 每个运动必须 tied 到**物理支撑**（见下文「关节化策略」）
- **不要**写数值运动范围（range of motion）——智能体会选机械上合理的限位

若对象身份包含键盘、按钮组、控制簇等**可见前面板控件**，在此**明确说明**；当按键/按钮 individually 可见时，写明它们**独立关节化**，而非熔成一块静态面板。

### 4. 尺度或比例提示（可选 — 约 1 句）

仅当默认尺度会歧义时需要。例如："desktop-scale"（桌面尺度）vs "industrial floor-mounted"（工业落地式），或 "arm span roughly 0.5m"（臂展约 0.5 米）。

---

## 复杂度预算

| 对象复杂度 | 目标部件数 | Prompt 长度 | 建议 max_turns |
| --- | --- | --- | --- |
| 简单（1–2 个关节） | 3–6 | 2–3 句 | 100 |
| 中等（3–5 个关节） | 6–12 | 3–4 句 | 140 |
| 复杂（6+ 关节） | 12–20 | 4–6 句 | 180 |

若超过 **6 句**，多半在**过度指定**。应拆成两个对象或简化。

> 以上为**当前工作预算**，非硬上限。本仓库新类别探索常见在 `100–200` turn 范围。对象确有几何/关节复杂度时可提高 turn 预算；**不要**为迁就过时 turn 目标而降低 prompt 质量。

---

## 示例

### 良好示例

**单旋转铰链：**

> A heavy-duty door hinge. Two rectangular leaf plates connected by a barrel-and-pin hinge with alternating knuckles. One revolute joint along the barrel axis.

**偏航-俯仰模块：**

> A two-axis gimbal mount. A yaw turntable base carries a U-shaped fork, which supports a pitch cradle between its arms. Yaw is continuous rotation about vertical; pitch is revolute about the horizontal fork axis.

**伸缩臂：**

> A three-stage telescoping boom. Three nested rectangular tube sections that extend from a fixed root mount. Each stage slides prismatically along the boom axis.

**正交 XY 平台：**

> A two-axis positioning stage. A base carries an X-axis rail with sliding carriage; on top of that carriage sits a Y-axis rail with its own carriage, oriented 90 degrees to the first. Both axes are prismatic.

**电视壁挂架：**

> An articulated TV wall mount (no screen attached). A wall plate connects to a folding two-link arm via revolute joints, ending in a tilt-and-swivel head plate. Arm folds flat against the wall. Joints: two arm-fold revolute joints, one head tilt revolute, one head swivel revolute.

**肩-肘-腕臂：**

> A three-joint robotic arm. A base pedestal supports a shoulder revolute joint (vertical axis), an upper arm link to an elbow revolute, and a forearm link to a wrist revolute (roll axis).

**带可见按键的收银机：**

> A supermarket cash register with a front cash drawer, a sloped keypad console, and a customer display on a rear neck. The drawer slides prismatically from the base, the display tilts on a revolute hinge, and the visible keypad buttons articulate independently as small push controls in the console face.

### 不良 — 过于冗长

> Design a realistic, highly detailed single revolute hinge as a standalone mechanical study assembly for a special pipeline variant, with one clear rotary axis joining two rigid leaves or clevis members in a heavy-duty hinge. The hinge pin, barrel segments, and support cheeks should be prominent and mechanically plausible. Emphasize rigid brackets, exposed hinge hardware, removable access covers, and disciplined machined-or-fabricated hard-surface geometry, plus grease-cap details, stop lugs, and bolted leaf plates. Keep it as a pure mechanical assembly with explicit joints, guides, bearings, brackets, and support structure. Avoid product styling, decorative housings, or recognizable household or device forms.

**为何差：** 约 50% token 重复系统 prompt；**没有**显式关节规格，智能体须猜关节类型与范围；细节愿望清单（油嘴、止挡、检修盖）膨胀几何与错误面，却不改善可识别外形。

### 不良 — 过于简短

> A hinge.

**为何差：** 无部件结构、无关节规格、无尺度。会有输出，但很可能不符合预期。

### 不良 — 控件含糊

> A cash register with a drawer, screen, and controls.

**为何差：** "controls" 太模糊。若按键对身份重要，应写明可见控制簇存在且**独立关节化**；否则模型可能熔成单一静态表面。

---

## 关节化策略（Articulation Policy）

包含**常人在这类物体上会期望**的关节化——往往不止一种运动。

| 要做 | 不要做 |
| --- | --- |
| 保留类别典型的多种规范运动 | 为省事人为压成「只有一个运动」 |
| 包含小部件运动（旋钮、按钮、脚轮等） | 忽略仅因「小」而重要的运动 |
| 对可见控制面**点名**（独立按钮/键/拨盘） | 指望智能体仅从类别名推断控制面 |
| 当多个部件实为**同一刚性支撑总成**时写清楚（单托盘+左右对称支架） | 把对称支架写成可各自漂移的独立体 |
| 每个命名运动 tied 物理支撑 | 只写 "wheel spins" / "lid opens" |

**支撑表述示例：**

- ✅ "wheel mounted in a fork"（轮装在叉架中）
- ❌ "wheel spins"
- ✅ "lid hinged from the rear edge of the housing"
- ❌ "lid opens"
- ✅ "carriage slides on twin rails"
- ❌ "carriage moves"

---

## 批内多样性（Batch Diversity）

同一类别的 prompt 批次应包含**有意义的变化**，变化应来自类别**内部可信差异**，而非漂移到另一对象类。

可在批次间变化：

- 真实世界变体/子类型
- 比例与轮廓
- 子部件数量与布局
- 轴方向或关节布局

**保持类别边界稳定。** 避免「同一 prompt 只换形容词」的行。

---

## SDK 适配

类别 prompt 必须落在 SDK 栈能**可靠**建模的范围内。两条硬约束塑造下文一切：

1. **严格树结构** — 每个部件恰好一个父关节，无环。需要某部件被两条独立路径驱动的机构（闭链）**无法**建模。
2. **URDF 关节模型** — 每个关节单轴（一个 revolute、一个 prismatic 或一个 continuous）。无「一关节驱动另一关节」；耦合/齿轮联动不可表达。

### 几何：建模效果较好（大致由易到难）

| 类型 | 说明 |
| --- | --- |
| **box / cylinder / sphere primitive** | 直接导出 URDF primitive；最紧凑、精确、网格风险最低 |
| **挤出型材与面板** | 平板、L 支架、C 槽、带矩形开孔的面板 |
| **旋转体 / 车削形** | 旋钮、把手、盖、桶身、喷嘴、炮塔 dome |
| **布尔挖空的 primitive** | 圆柱减圆柱（铰链耳）、带矩形孔的 box |
| **多分支树装配** | 一父多独立子（多抽屉柜、风扇轮毂+叶片、躯干双臂） |
| **顺序连杆链** | 伸缩级、机械臂段、折叠臂链；深度任意，完全支持 |

### 几何：建模效果较差

| 类型 | 说明 |
| --- | --- |
| **有机自由曲面** | 复合曲面外壳（车身板、 ergonomic 握把）需 `section_loft` 多引导线，易碎；优先可识别平面/圆柱/旋转剖面的物体 |
| **无清晰内外轮廓的薄壁壳** | 须显式创作；无自动 offset。壁厚非设计重点时描述为实心 |
| **软物与柔性元件** | 布、橡胶密封、皮带、缆线、弹簧、链条在 URDF 中无表示；仅描述刚性结构件 |
| **表面肌理** | URDF 仅支持 RGBA 颜色；描述滚花、拉丝、浮雕 logo 浪费 token |

### 运动学：URDF 无法表达的模式

下列模式听起来合理但在模型层会失败——**避免**核心功能依赖它们的类别：

| 模式 | 失败原因 | 可用替代 |
| --- | --- | --- |
| **剪刀/交叉连杆**（剪刀千斤顶、lazy tongs、伸缩臂叉、剪刀升降台） | 交叉杆须共享中心枢轴与端部枢轴 — 闭链 | 伸缩 prismatic 柱，或简单两连杆折叠臂 |
| **四连杆与平行连杆**（平行四边形臂、双驱动平行夹爪） | 连杆有两个父级 | 一颚作 prismatic 子件；另一颚 fixed 于机体 |
| **耦合/同步关节**（齿条齿轮驱动第二件、缆驱夹爪、蜗杆+输出齿轮） | 无 joint-drives-joint；各关节独立 | 只描述输出件运动，省略传动 |
| **差速齿轮组** | 载体同时是侧齿轮父与子 | 不建模；改选独立关节对象 |
| **弹簧/阻尼回位**（凸轮+弹簧从动件） | URDF 无弹簧；凸轮几何不产生运动学 | 省略回位弹簧；只描述关节轴 |

当左右配对支撑共同承载同一刚性体时，prompt 优先写共享体为主语（"a single rigid tray supported by matched left and right side assemblies"），并保持对应件对齐；除非类别定义要求独立漂移，不要把对称支架写成可各自自由摆动的无关部件。

### 关节类型速查

| 类型 | 用途 |
| --- | --- |
| **revolute** | 有限转动：铰链、翻盖、盖、臂关节；总有运动限位 |
| **prismatic** | 有限平移：抽屉、滑轨、伸缩级、夹爪 |
| **continuous** | 无界旋转：轮子、风扇、转台；**不要**用 revolute 表示自由旋转的轮 |
| **fixed** | 零自由度刚性连接：法兰、盖、装饰环等相对父件不动 |

每个关节**单轴**。球窝腕需三条 revolute **链式**堆叠（yaw → pitch → roll），在关节规格中**分别**写明各轴。

---

## 提交前检查清单

- [ ] 是否清晰命名对象？
- [ ] 是否列出关键部件及连接方式？
- [ ] 是否指定每个关节类型与轴？
- [ ] 刚性分组部件与对称配对支架是否在需要对齐时写明确？
- [ ] 是否避免写数值运动范围？
- [ ] 是否 ≤ 6 句？
- [ ] 是否避免重复系统 prompt 已覆盖内容？
- [ ] 机械工程师能否仅凭此 prompt 开工？

---

## 相关文档

- [类别入选要求](CATEGORY_SELECTION_REQUIREMENTS_c.md)
- [已拒绝类别](REJECTED_CATEGORIES_c.md)
- [数据集生成指南](../docs/dataset_generation_c.md)
