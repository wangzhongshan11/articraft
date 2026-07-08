# S09 · USB / SD 卡收纳座 / USB / SD card organizer

> **Visual reference**: `reference_S09_usb_sd_card_organizer.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a compact USB and SD card organizer as one solid base. The overall size is 120 × 70 × 36 mm. On the top face, arrange six narrow USB-sized vertical slots in one row and four wider SD-card-sized slots in a second row. Use evenly spaced rectangular pockets with softly rounded internal corners, and keep a solid perimeter wall around the slot field. Add small rounded external edges and a flat base.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个一体式 USB 与 SD 卡收纳座，整体尺寸为 120 × 70 × 36 mm。顶面设置两排插槽：一排为六个窄的 USB 尺寸竖向槽，另一排为四个较宽的 SD 卡尺寸槽。插槽采用均匀排布的圆角矩形凹槽，外侧保持完整边缘围合；外边缘轻微倒圆，底部平整。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: 120 × 70 × 36 mm
- **Target capability tags**: single part, slot array, multiple slot sizes, fillets

## Must be present

- single part
- six narrow USB slots
- four wider SD slots
- regular array
- flat base

## Evaluation checks

- one watertight solid
- slot counts and rows correct
- slots have distinguishable sizes
- spacing is regular

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
