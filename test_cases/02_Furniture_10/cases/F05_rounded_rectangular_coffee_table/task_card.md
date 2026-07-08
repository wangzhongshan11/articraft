# F05 · 圆角矩形茶几 / Rounded rectangular coffee table

> **Visual reference**: `reference_F05_rounded_rectangular_coffee_table.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a rounded rectangular coffee table with a 900 × 500 mm tabletop and an overall height of 400 mm. Use a 30 mm thick tabletop with broad rounded corners and softened edges. Add four legs inset from the corners and a shallow apron or lower frame beneath the tabletop. Keep the design minimal and use clean symmetric construction; do not add drawers, handles, or ornamental carving.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一张圆角矩形茶几，桌面尺寸为 900 × 500 mm，整体高 400 mm。桌面厚约 30 mm，四角采用较大圆角，边缘软化。四根桌腿从桌角内缩布置，并在桌面下设置浅桌裙或下部框架。整体保持极简、对称、构造清晰，不添加抽屉、把手或雕饰。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 900 W × 500 D × 400 H mm
- **Target capability tags**: rounded tabletop, four legs, apron, underside shelf opening

## Must be present

- rounded rectangle tabletop
- four inset legs
- apron/lower frame
- minimal symmetric construction

## Evaluation checks

- five or more semantic parts
- tabletop corner radius present
- leg placement symmetric
- legs connect to frame

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
