# S10 · 模块化抽屉分隔件 / Modular drawer divider

> **Visual reference**: `reference_S10_modular_drawer_divider.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a modular drawer-divider system made from repeated thin panels. Each main divider panel is approximately 150 mm long, 90 mm high, and 5 mm thick. Use centered half-depth cross slots so identical panels can intersect at right angles and form adjustable rectangular compartments. Round the exposed top corners slightly and add a small end stop or shallow notch at the panel ends to improve readability. Show at least four panels assembled into a simple grid.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个由重复薄板组成的模块化抽屉分隔系统。主分隔板尺寸约为长 150 mm、高 90 mm、厚 5 mm。在板件中部设置半深交叉插槽，使相同板件能够以直角互插，形成可调整的矩形分隔空间。顶部外露角轻微倒圆，板件端部设置小止挡或浅缺口以增强识别性；至少展示四个板件组装成一个简洁网格。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: nominal divider panels: 150 × 90 × 5 mm
- **Target capability tags**: interlocking panels, cross slots, orthogonal assembly, repeated components

## Must be present

- repeated divider panels
- half-depth cross slots
- right-angle interlocking
- four-panel grid

## Evaluation checks

- multiple semantic parts
- cross slots align at mid-height
- panels intersect without gross collision
- assembly forms compartments

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
