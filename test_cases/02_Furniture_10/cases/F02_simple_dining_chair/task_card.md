# F02 · 简约餐椅 / Simple dining chair

> **Visual reference**: `reference_F02_simple_dining_chair.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a simple wooden dining chair with a rectangular seat, four legs, a slightly reclined backrest, and side stretchers. The overall size is about 420 mm wide, 480 mm deep, and 880 mm high, with a seat height of about 450 mm. Use a 25–30 mm thick seat panel with softened edges. The two rear legs should continue upward to support the backrest. Keep the geometry clean and structurally credible, with modest fillets at exposed edges.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一把简约木质餐椅，包括矩形座板、四根椅腿、略后倾的靠背和侧向横撑。整体约宽 420 mm、深 480 mm、高 880 mm，坐面高约 450 mm。座板厚约 25–30 mm，边缘软化。两根后腿应向上延续以支撑靠背；整体几何清晰、结构合理，外露边缘采用适度圆角。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 420 W × 480 D × 880 H mm; seat height about 450 mm
- **Target capability tags**: seat, backrest, four legs, stretchers, back tilt

## Must be present

- seat panel
- four legs
- rear legs continue to backrest
- backrest
- side stretchers

## Evaluation checks

- semantic furniture parts
- chair sits flat
- backrest reads as connected structure
- left-right symmetry

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
