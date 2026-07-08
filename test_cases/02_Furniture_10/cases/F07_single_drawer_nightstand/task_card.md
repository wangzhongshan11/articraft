# F07 · 单抽屉床头柜 / Single-drawer nightstand

> **Visual reference**: `reference_F07_single_drawer_nightstand.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a compact single-drawer nightstand with a rectangular cabinet shell, one upper drawer, and one open lower shelf. The overall size is 450 mm wide, 400 mm deep, and 560 mm high. Use a 18–25 mm thick cabinet construction with four short feet. The drawer should include a separate drawer box and front panel, with a small clearance gap around the front and a simple centered pull. Keep the lower shelf open and structurally supported.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个紧凑的单抽屉床头柜，包括矩形柜体、上部单抽屉和下部开放置物格。整体约宽 450 mm、深 400 mm、高 560 mm；柜体板厚约 18–25 mm，底部设置四个短脚。抽屉由独立抽屉盒与抽屉面板组成，面板周边保留小装配缝，并设置居中简洁拉手。下部置物格保持开放并具备明确支撑关系。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 450 W × 400 D × 560 H mm
- **Target capability tags**: cabinet shell, drawer box, drawer front, clearance, feet

## Must be present

- cabinet shell
- separate drawer box
- drawer front
- open lower shelf
- four feet
- centered pull

## Evaluation checks

- drawer semantic parts separate
- drawer fits opening with clearance
- cabinet has open lower shelf
- feet touch floor

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
