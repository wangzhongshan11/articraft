# F08 · 双开门矮柜 / Double-door low cabinet

> **Visual reference**: `reference_F08_double_door_low_cabinet.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a low storage cabinet with a rectangular enclosure, two equal front doors, one internal shelf, and short feet. The cabinet is 800 mm wide, 400 mm deep, and 600 mm high. Use two symmetric doors with a narrow central gap and small vertical pulls near the meeting edges. Keep the doors closed for the reference pose but model them as separate semantic parts. Use clean board-like construction with modest rounded exposed edges.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个双开门矮柜，包括矩形柜体、两扇等宽前门、一块内部层板和短脚。整体约宽 800 mm、深 400 mm、高 600 mm。两扇门左右对称，中间保留窄门缝，在相邻边附近设置小型竖向拉手。参考状态为闭合，但两扇门应作为独立语义部件建模。采用清晰板式构造，外露边缘适度倒圆。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 800 W × 400 D × 600 H mm
- **Target capability tags**: cabinet shell, two doors, interior shelf, symmetry, door gap

## Must be present

- cabinet shell
- two equal separate doors
- internal shelf
- center gap
- short feet

## Evaluation checks

- doors separate semantic parts
- door symmetry
- central gap present
- shelf positioned inside cabinet

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
