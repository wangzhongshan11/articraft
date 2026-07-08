# F09 · 带线孔书桌 / Desk with cable grommet

> **Visual reference**: `reference_F09_desk_with_cable_grommet.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a compact writing desk with a 1200 × 600 mm rectangular tabletop, four legs, and an overall height of 750 mm. Round the tabletop corners and edge transitions. Add one circular cable grommet hole near the rear-right corner of the tabletop. Include a shallow front modesty panel or a simple under-desk support rail, while leaving the leg space open. Use symmetric leg placement and a clean furniture-like construction.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一张紧凑书桌，桌面为 1200 × 600 mm 矩形，四腿支撑，整体高 750 mm。桌面四角与边缘过渡倒圆；在桌面后侧靠右位置设置一个圆形穿线孔。前侧设置浅挡板或简单桌下横撑，同时保持腿部活动空间开放。桌腿对称布置，整体采用清晰的家具构造。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 1200 W × 600 D × 750 H mm
- **Target capability tags**: large tabletop, cable hole, four legs, modesty panel, rounded edges

## Must be present

- large rounded tabletop
- one circular cable hole
- four legs
- front modesty/support panel
- open leg space

## Evaluation checks

- tabletop is one continuous panel with hole
- leg symmetry
- support panel does not block leg space
- stable stance

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
