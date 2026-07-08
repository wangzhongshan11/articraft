# S02 · 滑盖式线缆收纳盒 / Sliding-lid cable organizer

> **Visual reference**: `reference_S02_sliding_lid_cable_box.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a desktop cable organizer consisting of a hollow rectangular box and a top sliding lid. The box is 300 mm long, 120 mm deep, and 130 mm high, with about 3 mm walls. Add a shallow pair of longitudinal guide rails so the lid slides along the long direction and remains captured. Place one circular cable port on each short side and two circular cable ports on the front face. Use softly rounded external edges and leave the interior unobstructed for cables and a power strip.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个桌面线缆收纳盒，包括空心长方体盒体和顶部滑盖。盒体尺寸为长 300 mm、深 120 mm、高 130 mm，壁厚约 3 mm。沿长度方向设置一对浅导轨，使盖板能够沿长边滑动且不脱落。两个短侧面各设置一个圆形走线孔，前侧面设置两个圆形走线孔。外边缘采用柔和圆角，内部保持通畅，以容纳插排和线缆。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: 300 × 120 × 130 mm; nominal wall thickness 3 mm
- **Target capability tags**: hollow shell, sliding lid, cable ports, guide rails

## Must be present

- hollow box
- separate sliding lid
- longitudinal guide rails
- four cable ports
- rounded external edges

## Evaluation checks

- two semantic parts
- lid motion direction is longitudinal
- ports cut through walls
- no interference along lid travel

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
