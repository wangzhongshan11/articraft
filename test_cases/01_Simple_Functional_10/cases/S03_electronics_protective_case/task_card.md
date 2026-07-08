# S03 · 电子设备保护壳 / Electronics protective case

> **Visual reference**: `reference_S03_electronics_protective_case.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a compact two-piece protective enclosure for a small electronic device. The assembled case is 160 × 120 × 30 mm with approximately 2.5–3 mm shell walls and rounded corners. Use a lower tray and a detachable upper cover. Add a rectangular ventilation array on the upper cover, a side cutout for a connector, and four internal screw-boss locations near the corners. Use small clearance between upper and lower shells so the enclosure reads as a realistic assembled product.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个用于小型电子设备的两片式保护壳。装配整体尺寸为 160 × 120 × 30 mm，壳体壁厚约 2.5–3 mm，四角倒圆。由下部托盘和可拆卸上盖组成；上盖设置矩形阵列散热孔，侧面设置一个接口开孔，内部四角附近设置四个螺丝柱位置。上下壳之间保留合理装配间隙，使其呈现为真实的产品外壳。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: 160 × 120 × 30 mm; nominal shell thickness 2.5–3 mm
- **Target capability tags**: two-piece enclosure, ventilation array, ports, screw bosses

## Must be present

- lower tray
- upper cover
- ventilation array
- connector cutout
- four screw-boss locations
- rounded corners

## Evaluation checks

- two shells fit
- ventilation holes fully cut through
- side port accessible
- case interior exists

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
