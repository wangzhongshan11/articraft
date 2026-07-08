# F01 · 圆角四腿方凳 / Rounded four-leg stool

> **Visual reference**: `reference_F01_rounded_four_leg_stool.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a compact rounded four-leg stool. The square seat is 320 × 320 mm and 30 mm thick, with generously rounded outer corners. The assembled stool height is 440 mm. Add four slightly tapered legs placed symmetrically near the seat corners, with each leg seated into a shallow underside pocket or socket. Keep the stool visually simple, with soft edge fillets and a stable stance.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个紧凑的圆角四腿方凳。方形坐面尺寸为 320 × 320 mm、厚 30 mm，外角采用较大圆角；整体高 440 mm。在坐面四角附近对称布置四根略收分的腿件，每根腿插入坐面底部的浅定位孔或插座。整体保持简洁，外露边缘采用柔和圆角，姿态稳定。

## Case metadata

- **Group**: furniture
- **Reference dimensions**: seat: 320 × 320 × 30 mm; overall height: 440 mm
- **Target capability tags**: seat, four legs, symmetry, fillets, mortise-like pockets

## Must be present

- separate seat
- four symmetric legs
- underside locating pockets
- rounded seat corners
- stable stance

## Evaluation checks

- five semantic parts
- leg symmetry
- legs meet seat without floating
- seat and legs form plausible stool

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
