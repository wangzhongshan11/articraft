# S05 · 排水皂盒 / Draining soap dish

> **Visual reference**: `reference_S05_draining_soap_dish.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a compact draining soap dish as one printable part. The overall size is 130 × 90 × 80 mm. Form a shallow rounded rectangular tray with a gently raised rim. Cut five parallel rounded drainage slots through the tray floor and add four short feet below to raise the dish. Use rounded outside corners and a shallow internal basin that keeps a bar of soap centered above the drainage slots.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个可 3D 打印的一体式排水皂盒，整体尺寸为 130 × 90 × 80 mm。形成浅圆角矩形托盘，并设置轻微抬高的边缘；在托盘底面贯穿开设五条平行圆角排水槽，底部设置四个短脚以抬高皂盒。外角倒圆，内部形成浅凹腔，使肥皂位于排水槽上方。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: 130 × 90 × 80 mm
- **Target capability tags**: shallow shell, slot array, raised feet, fillets

## Must be present

- single part
- shallow tray
- five through drainage slots
- four feet
- rounded corners

## Evaluation checks

- one watertight solid
- all slots cut through
- feet contact same ground plane
- tray retains soap

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
