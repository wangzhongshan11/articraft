# F06 · 双层边几 / Two-tier side table

> **Visual reference**: `reference_F06_two_tier_side_table.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a square two-tier side table with an upper tabletop, a lower storage shelf, and four shared corner legs. The overall size is 450 × 450 × 550 mm. The upper and lower panels should have softly rounded outer corners, with the lower shelf positioned roughly 120 mm above the floor. Use identical vertical legs to connect both levels, maintaining clean alignment and a stable furniture proportion.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一张方形双层边几，包括上层台面、下层置物板和四根贯通两层的角部腿件。整体尺寸为 450 × 450 × 550 mm。上下两层板件外角均采用柔和圆角，下层置物板距地面约 120 mm。四根竖向腿件应尺寸一致，并连接上下两层，保持清晰对齐和稳定的家具比例。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 450 W × 450 D × 550 H mm
- **Target capability tags**: two shelves, four legs, repeated supports, rounded corners

## Must be present

- upper tabletop
- lower shelf
- four shared legs
- rounded panel corners
- aligned levels

## Evaluation checks

- six semantic parts
- shelf at lower elevation
- all legs connect both panels
- plan alignment square

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
