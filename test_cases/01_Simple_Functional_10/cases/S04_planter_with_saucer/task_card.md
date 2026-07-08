# S04 · 带托盘的花盆 / Planter with saucer

> **Visual reference**: `reference_S04_planter_with_saucer.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a tapered round planter and a separate matching saucer. The planter is about 120 mm in top diameter and 130 mm high, with a hollow planting cavity, a 3 mm wall, and one circular drainage hole at the bottom center. The saucer is about 140 mm in diameter and 18 mm high, with a shallow recessed dish that nests under the planter. Use a simple rounded rim and a stable flat base.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个略微收分的圆形花盆和独立匹配托盘。花盆顶部直径约 120 mm、高 130 mm，具有空心种植腔、约 3 mm 壁厚，并在底部中心设置一个圆形排水孔。托盘直径约 140 mm、高 18 mm，设置浅凹盘以承接花盆。花盆口沿采用简单圆角，底部保持稳定平整。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: pot: Ø120 × 130 mm; saucer: Ø140 × 18 mm
- **Target capability tags**: revolved profile, hollow volume, drainage hole, nested assembly

## Must be present

- tapered hollow planter
- central drainage hole
- separate saucer
- nested geometry
- rounded rim

## Evaluation checks

- two semantic parts
- drainage hole reaches cavity
- planter seats within saucer
- both parts watertight

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
