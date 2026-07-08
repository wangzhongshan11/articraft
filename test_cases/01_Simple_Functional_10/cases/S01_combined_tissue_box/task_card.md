# S01 · 组合式纸巾盒 / Combined tissue box

> **Visual reference**: `reference_S01_combined_tissue_box.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a combined tissue box with a hollow rectangular base and a separate removable lid. The overall footprint is 260 × 140 mm and the assembled height is 100 mm, with approximately 3 mm walls. Round the outer vertical edges and the lid perimeter. Center a rounded-rectangle dispensing opening in the lid, about 130 × 35 mm. The lid should seat on an internal lip of the base, leaving a visible but tight assembly seam. Keep the interior open for a standard tissue pack.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个组合式纸巾盒，包括空心长方体盒体和独立可拆卸盖板。整体尺寸为 260 × 140 × 100 mm，壁厚约 3 mm。外侧竖向边缘与盖板周边均倒圆角。盖板中央设置约 130 × 35 mm 的圆角矩形出纸孔。盖板应通过盒体内侧台阶定位，装配后保留清晰但紧凑的拼缝；盒体内部保持开放，可容纳常规抽纸包。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: 260 × 140 × 100 mm; nominal wall thickness 3 mm
- **Target capability tags**: hollow shell, rounded-rectangle cutout, lid-base fit, fillets

## Must be present

- hollow base
- separate lid
- centered rounded-rectangle opening
- internal locating lip
- rounded outer edges

## Evaluation checks

- two semantic parts
- lid covers opening without collision
- base is hollow and watertight
- opening cuts through lid

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
