# F03 · 条板靠背椅 / Slat-back chair

> **Visual reference**: `reference_F03_slat_back_chair.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a dining chair with a solid seat, two rear uprights, and five evenly spaced vertical back slats. The chair is approximately 430 mm wide, 460 mm deep, and 860 mm high, with a 440 mm seat height. Use a slightly curved or gently rounded top rail connecting the two rear uprights. Keep the slats equally spaced and aligned above the seat, with simple square or rounded-section legs and light edge fillets.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一把带条板靠背的餐椅，包括实心坐面、两根后立柱和五根均匀排布的竖向靠背条。整体约宽 430 mm、深 460 mm、高 860 mm，坐面高约 440 mm。两根后立柱顶部以略带弧度或轻微圆角的横枨连接；靠背条应位于坐面上方并保持等距。椅腿可采用方形或圆角方形截面，外露边缘使用轻度圆角。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 430 W × 460 D × 860 H mm; seat height about 440 mm
- **Target capability tags**: seat, vertical back slats, repetition, side frame, fillets

## Must be present

- solid seat
- two rear uprights
- five vertical slats
- top rail
- four legs

## Evaluation checks

- slat count=5
- slat spacing consistent
- back assembly connected
- stable chair stance

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
