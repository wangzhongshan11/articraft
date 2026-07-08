# S06 · 倾斜式手机支架 / Inclined phone stand

> **Visual reference**: `reference_S06_inclined_phone_stand.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a one-piece inclined smartphone stand with an 80 × 75 mm footprint and a 190 mm overall height. Use an inclined back panel that supports a phone in portrait orientation, a shallow front retaining lip, and a centered opening below the lip for a charging cable. Add one large triangular or rounded-rectangle cutout through the back support to reduce material while preserving a stable side profile. Round exposed edges.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个一体式倾斜手机支架，底面约 80 × 75 mm、整体高 190 mm。设置倾斜背板以支撑竖放手机，前端设置浅挡唇，并在挡唇下方居中开设充电线通孔。在背部支撑板贯穿开设一个较大的三角形或圆角矩形减重孔，同时保持稳定侧向轮廓；外露边缘倒圆。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: 80 × 75 × 190 mm
- **Target capability tags**: single part, inclined support, front lip, cable opening, weight-reduction cutout

## Must be present

- single part
- inclined back support
- front retaining lip
- charging-cable opening
- large back cutout

## Evaluation checks

- one watertight solid
- phone support angle readable
- cable opening reaches front edge
- stable base

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
