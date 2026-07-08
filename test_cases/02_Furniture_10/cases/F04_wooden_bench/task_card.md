# F04 · 长凳 / Wooden bench

> **Visual reference**: `reference_F04_wooden_bench.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a simple wooden bench with a long rectangular seat, two end leg frames, and one lower longitudinal stretcher. The bench is 1000 mm wide, 300 mm deep, and 440 mm high. Use a 30 mm thick seat with rounded long edges. Place the two leg frames symmetrically near the ends and connect them with a stretcher close to the floor. Keep the joinery readable and the whole bench structurally stable.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一张简洁木质长凳，包括长条矩形坐面、两组端部支腿框架和一根靠近地面的纵向横撑。整体约宽 1000 mm、深 300 mm、高 440 mm；坐面厚约 30 mm，长边倒圆。两组腿架在两端附近对称布置，并以一根下部横撑连接。构件关系应清晰，整体结构稳定。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 1000 W × 300 D × 440 H mm
- **Target capability tags**: long seat, two leg frames, lower stretcher, symmetry, fillets

## Must be present

- long seat
- two symmetric leg frames
- one lower longitudinal stretcher
- rounded seat edges

## Evaluation checks

- multiple semantic parts
- end frames aligned
- stretcher connects frames
- bench rests flat

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
