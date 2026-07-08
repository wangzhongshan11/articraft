# F10 · 开放式方格书架 / Open cube bookshelf

> **Visual reference**: `reference_F10_open_cube_bookshelf.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create an open cube bookshelf with an outer rectangular frame, three horizontal shelves, two vertical divider panels, and a shallow back-panel groove. The overall size is 1000 mm wide, 300 mm deep, and 1200 mm high. Arrange the shelves and dividers to form a regular 3 × 3 grid of open compartments. Use board-like panels around 18–25 mm thick, lightly round exposed front edges, and keep the back open except for the shallow groove detail.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个开放式方格书架，包括外框、三块水平层板、两块竖向分隔板以及背板安装浅槽。整体约宽 1000 mm、深 300 mm、高 1200 mm；层板与竖向分隔板形成规则的 3 × 3 开放格网。板件厚度约 18–25 mm，前侧外露边缘轻微倒圆；背面保持开放，仅保留浅槽构造细节。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: 1000 W × 300 D × 1200 H mm
- **Target capability tags**: outer frame, shelves, vertical dividers, repeated compartments, back groove

## Must be present

- outer frame
- three horizontal shelves
- two vertical dividers
- 3x3 open grid
- back groove

## Evaluation checks

- regular 3x3 compartment layout
- boards align
- open fronts
- shelf and divider count correct

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
