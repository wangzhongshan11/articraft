# S08 · 可堆叠零件收纳盒 / Stackable parts bin

> **Visual reference**: `reference_S08_stackable_parts_bin.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create one stackable open-top parts bin for small hardware. The bin is 160 × 120 × 90 mm with approximately 3 mm walls and slightly drafted side walls. Add a recessed rectangular label field on the front face, a shallow stacking lip around the top rim, and matching underside recesses so identical bins can locate when stacked. Keep the inside open and add modest rounded corners.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个用于小五金件的可堆叠开口收纳盒。尺寸为 160 × 120 × 90 mm，壁厚约 3 mm，侧壁略有拔模。前侧面设置凹入式矩形标签区，顶部边缘设置浅堆叠定位唇，底部设置与之匹配的凹槽，使相同收纳盒能够稳定堆叠。内部保持开放，边角采用适度圆角。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: 160 × 120 × 90 mm; nominal wall thickness 3 mm
- **Target capability tags**: hollow bin, stacking lip, bottom recess, label recess, drafted walls

## Must be present

- open-top hollow bin
- front label recess
- top stacking lip
- matching bottom recess
- drafted walls

## Evaluation checks

- one watertight solid
- top and bottom stacking features align
- interior unobstructed
- label field recessed

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
